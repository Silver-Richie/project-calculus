"""
Calculus Bridge - Ranked Duel asinkron (lawan hantu/bot, tanpa WebSocket).

Arsitektur
----------
1. find_match(user)            Kurva matchmaking per rank: Terra III & II 100% bot, Terra I 30% hantu,
                               Luna 50% hantu, Solar/Nova/Apex 100% hantu (fallback bot bila belum ada
                               rekaman yang cocok). Hantu = GhostRecord pemain lain di pool & MMR terdekat.
2. generate_duel_match(seed)   10 soal dari satu match_seed: kesulitan Mudah/Sedang/Sulit diacak total,
                               topik lintas fakultas, level materi dibatasi rank (POOL_LEVELS).
                               Seed yang sama ⇒ soal & urutan identik (hantu menyimpan resepnya juga).
3. open_question / submit_answer
                               Server membuka soal (q_started_at) dan menilai jawaban dengan waktu server:
                               benar = skor dasar + sisa detik; salah/habis waktu = 0.
4. resolve_duel(match)         Skor tertinggi menang (seri dipecah total waktu). Bintang/Apex Points lewat
                               PlayerRank (ranking.py), Streak Shield dipakai bila kalah akan mengurangi
                               bintang/poin, MMR tersembunyi diperbarui, dan SEMUA penampilan yang selesai
                               10 soal (menang, kalah, seri — bukan menyerah/putus) disimpan sebagai GhostRecord,
                               supaya pool hantu punya kurva kemampuan alami (tanpa survivorship bias).
Bot tampil seperti pemain biasa (nama acak ala pemain, avatar default); jenis lawan tidak dikirim ke browser.
Anti-curang: keluar tab pertama = soal berjalan dihitung salah; kedua = menyerah (kalah, tanpa shield).
"""

import random
import secrets
from datetime import timedelta

from django.db import transaction
from django.db.models import F
from django.utils import timezone

from . import avatar, bot_names, campus, generators, ranking, shop
from .leveling import level_for
from .models import GhostRecord, RankedMatch, Topic, UserProfile, rank_of
from .ranking import describe

QUESTION_COUNT = 10
GRACE_MS = 1500                     # toleransi latensi setelah batas waktu
MAX_TAB_LEAVES = 2
MIN_LEVEL = 3                       # sama dengan duel lama: rank terbuka di Level 3

# Kesulitan → (batas waktu detik, skor dasar, tingkat generator yang dipakai)
DIFFICULTY = {
    "easy": {"label": "Mudah", "time": 30, "base": 100, "tiers": (1,)},
    "medium": {"label": "Sedang", "time": 60, "base": 200, "tiers": (2,)},
    "hard": {"label": "Sulit", "time": 120, "base": 300, "tiers": (3, 4, 5)},
}
# Tier rank → level kurikulum (MainLevel.order) yang boleh muncul. Kesulitan tetap acak total.
POOL_LEVELS = {"terra": (1, 2), "luna": (1, 2, 3), "solar": (1, 2, 3, 4), "nova": (1, 2, 3, 4), "apex": (1, 2, 3, 4)}

GHOST_WINDOW = 150                  # selisih MMR awal pencarian hantu; melebar bila kosong
GHOST_REPEAT_COOLDOWN = timedelta(hours=6)

# Bot: peluang benar dasar per tier, disesuaikan kesulitan soal.
BOT_ACCURACY = {"terra": 0.55, "luna": 0.62, "solar": 0.68, "nova": 0.74, "apex": 0.8}
BOT_DIFF_ADJ = {"easy": 0.15, "medium": 0.0, "hard": -0.18}


class RankedError(Exception):
    """Galat yang pesannya boleh ditampilkan ke pemain."""


# ── 1. Matchmaking ───────────────────────────────────────────────────────────
def ghost_share(state):
    """Peluang mendapat lawan hantu (sisanya bot) menurut rank."""
    if state.tier == "terra":
        return 0.0 if state.division in (3, 2) else 0.3
    if state.tier == "luna":
        return 0.5
    return 1.0


def eligibility(user):
    profile = UserProfile.objects.filter(user=user).first()
    level = level_for(profile.xp if profile else 0)
    if level < MIN_LEVEL:
        return f"Ranked kebuka di Level {MIN_LEVEL} (Level kamu: {level}). Kumpulin XP dulu dari sesi latihan topik."
    return None


def pick_ghost(user, pool, mmr, now=None, rng=None):
    """Rekaman pemain lain di pool yang sama dengan MMR terdekat (jendela melebar), acak di antara 5 terdekat."""
    now, rng = now or timezone.now(), rng or random.Random()
    recent = set(RankedMatch.objects.filter(user=user, ghost__isnull=False, created_at__gte=now - GHOST_REPEAT_COOLDOWN)
                 .values_list("ghost_id", flat=True))
    base = GhostRecord.objects.filter(pool=pool).exclude(user=user).exclude(pk__in=recent)
    for window in (GHOST_WINDOW, GHOST_WINDOW * 2, GHOST_WINDOW * 4, None):
        qs = base if window is None else base.filter(mmr__gte=mmr - window, mmr__lte=mmr + window)
        cands = sorted(qs.order_by("-created_at")[:50], key=lambda g: abs(g.mmr - mmr))[:5]
        if cands:
            return rng.choice(cands)
    return None


def find_match(user, rng=None, now=None):
    """
    Buat RankedMatch baru untuk `user` (duel aktif lama yang ditinggal dianggap menyerah dulu).
    Mengembalikan RankedMatch.
    """
    rng, now = rng or random.Random(), now or timezone.now()
    msg = eligibility(user)
    if msg:
        raise RankedError(msg)
    for stale in RankedMatch.objects.filter(user=user, status=RankedMatch.ACTIVE):
        resolve_duel(stale, forfeit=True)
    rank = rank_of(user)
    state, pool = rank.state, rank.tier
    ghost = pick_ghost(user, pool, rank.mmr, now, rng) if rng.random() < ghost_share(state) else None
    if ghost:
        return RankedMatch.objects.create(
            user=user, opponent_kind=RankedMatch.GHOST, ghost=ghost, opponent=_ghost_opponent(ghost),
            opponent_mmr=ghost.mmr, match_seed=ghost.match_seed, pool=ghost.pool, questions=ghost.questions)
    seed = secrets.token_hex(8)
    questions = generate_duel_match(seed, pool)
    bot = simulate_bot(questions, state, rank.mmr, seed)
    return RankedMatch.objects.create(
        user=user, opponent_kind=RankedMatch.BOT, opponent=bot, opponent_mmr=bot["mmr"],
        match_seed=seed, pool=pool, questions=questions)


def _ghost_opponent(ghost):
    card = {**player_card(ghost.user), "id": None}              # id tidak dikirim: kartu hantu & bot berbentuk sama
    return {"kind": "ghost", "card": card, "answers": ghost.answers, "mmr": ghost.mmr}


# ── 2. Generator 10 soal dari seed ──────────────────────────────────────────
def _candidates(pool):
    """(topik, generator) per kesulitan, urutan deterministik (topik & key diurutkan)."""
    topics = list(Topic.objects.filter(node__main_level__order__in=POOL_LEVELS[pool]).order_by("slug").values_list("slug", "title"))
    gens = sorted(generators.REGISTRY.values(), key=lambda g: g.key)
    out = {}
    for diff, info in DIFFICULTY.items():
        out[diff] = [(slug, title, g) for slug, title in topics for g in gens
                     if slug in g.topics and set(g.tiers) & set(info["tiers"])]
    return out


def generate_duel_match(match_seed, pool):
    """
    Resep 10 soal yang identik untuk siapa pun yang memakai match_seed + pool yang sama.

    Setiap soal: kesulitan diacak seragam (bisa 10 Sulit atau 10 Mudah — sengaja), lalu topik & generator
    diacak dari semua jalur fakultas di level yang diizinkan rank; topik tidak berulang selama masih ada pilihan.
    """
    rng = random.Random(f"ranked|{match_seed}|{pool}")
    cands = _candidates(pool)
    picked, used = [], set()
    while len(picked) < QUESTION_COUNT:
        diff = rng.choice(list(DIFFICULTY))
        options = [c for c in cands[diff] if c[0] not in used] or cands[diff]
        slug, title, gen = rng.choice(options)
        tier = rng.choice([t for t in gen.tiers if t in DIFFICULTY[diff]["tiers"]])
        seed = rng.randrange(10 ** 9)
        generators.generate(gen.key, seed, tier)                  # pastikan resep valid
        used.add(slug)
        info = DIFFICULTY[diff]
        picked.append({"key": gen.key, "seed": seed, "tier": tier, "topic": title, "difficulty": diff,
                       "time_limit": info["time"], "base": info["base"]})
    return picked


# ── Penilaian ───────────────────────────────────────────────────────────────
def score_for(correct, ms, spec):
    """Skor dasar + sisa waktu (detik bulat ke bawah) bila benar; 0 bila salah/habis waktu."""
    limit_ms = spec["time_limit"] * 1000
    if not correct or ms > limit_ms:
        return 0
    return spec["base"] + (limit_ms - ms) // 1000


def simulate_bot(questions, state, mmr, seed):
    """Jawaban bot yang masuk akal: peluang benar per tier & kesulitan, waktu acak dalam batas soal."""
    rng = random.Random(f"bot|{seed}")
    answers = []
    for spec in questions:
        p = min(0.95, max(0.1, BOT_ACCURACY[state.tier] + BOT_DIFF_ADJ[spec["difficulty"]]))
        correct = rng.random() < p
        frac = rng.uniform(0.25, 0.8) if correct else rng.uniform(0.4, 1.0)
        ms = int(spec["time_limit"] * 1000 * frac)
        answers.append({"option": None, "correct": correct, "ms": ms, "points": score_for(correct, ms, spec)})
    campus_name = rng.choice(campus.SUGGESTIONS) if rng.random() < 0.6 else ""
    card = {"id": None, **bot_identity(rng), "level": rng.randint(3, 25), "campus": campus_name, "rank": describe(state),
            "avatar": {"kind": "initial"}}
    return {"kind": "bot", "card": card, "answers": answers, "mmr": mmr + rng.randint(-60, 60)}


def bot_identity(rng):
    """Nama & fakultas bot ala pemain sungguhan (bot_names.py); tidak pernah sama dengan username pengguna asli."""
    from django.contrib.auth import get_user_model
    users = get_user_model().objects
    return bot_names.generate(rng, taken=lambda name: users.filter(username__iexact=name).exists())


def _question(spec):
    return generators.generate(spec["key"], spec["seed"], spec["tier"])


def _payload(match, index):
    spec = match.questions[index]
    q = _question(spec)
    deadline = match.q_started_at + timedelta(seconds=spec["time_limit"])
    return {"index": index, "total": len(match.questions), "topic": spec["topic"],
            "difficulty": spec["difficulty"], "difficulty_label": DIFFICULTY[spec["difficulty"]]["label"],
            "time_limit": spec["time_limit"], "base": spec["base"],
            "prompt": q["prompt"], "options": [{"id": o["id"], "text": o["text"]} for o in q["options"]],
            "deadline": int(deadline.timestamp() * 1000)}


def _get_active(match_id, user):
    match = RankedMatch.objects.select_for_update().filter(pk=match_id, user=user).first()
    if not match:
        raise RankedError("Duel-nya gak ketemu.")
    return match


# ── 3. Buka & jawab soal ────────────────────────────────────────────────────
def open_question(match_id, user, now=None):
    """Buka soal berikutnya (atau kembalikan soal yang sedang berjalan bila halaman dimuat ulang)."""
    now = now or timezone.now()
    with transaction.atomic():
        match = _get_active(match_id, user)
        if match.status != RankedMatch.ACTIVE:
            raise RankedError("Duel ini udah selesai.")
        if match.q_started_at is None:
            match.q_started_at = now
            match.save(update_fields=["q_started_at"])
        return _payload(match, match.current)


def submit_answer(match_id, user, index, option_id, now=None):
    """
    Nilai jawaban soal `index` dengan waktu server. option_id None = waktu habis / tidak menjawab.
    Mengembalikan ringkasan soal; bila soal terakhir, ringkasan memuat "result" (hasil duel).
    """
    now = now or timezone.now()
    with transaction.atomic():
        match = _get_active(match_id, user)
        if match.status != RankedMatch.ACTIVE or match.current != index or match.q_started_at is None:
            raise RankedError("Soal ini udah ditutup.")
        spec = match.questions[index]
        ms = int((now - match.q_started_at).total_seconds() * 1000)
        limit_ms = spec["time_limit"] * 1000
        q = _question(spec)
        late = ms > limit_ms + GRACE_MS
        correct = not late and option_id is not None and any(o["id"] == option_id and o["is_correct"] for o in q["options"])
        ms = min(ms, limit_ms)
        mine = {"option": option_id, "correct": correct, "ms": ms, "points": score_for(correct, ms, spec)}
        return _close_question(match, index, mine, q)


def _close_question(match, index, mine, q):
    match.answers = [*match.answers, mine]
    match.current, match.q_started_at = index + 1, None
    match.save(update_fields=["answers", "current", "q_started_at"])
    theirs = match.opponent["answers"][index]
    out = {"index": index, "last": index + 1 >= len(match.questions),
           "correct_option": next(o["id"] for o in q["options"] if o["is_correct"]), "answer": q["answer"],
           "you": mine, "opponent": {k: theirs[k] for k in ("correct", "ms", "points")},
           "totals": _totals(match)}
    if out["last"]:
        out["result"] = resolve_duel(match)
    return out


def leave_tab(match_id, user):
    """Keluar tab: pertama = soal berjalan dihitung salah, ke-MAX_TAB_LEAVES = menyerah."""
    with transaction.atomic():
        match = _get_active(match_id, user)
        if match.status != RankedMatch.ACTIVE:
            return None
        match.tab_leaves += 1
        match.save(update_fields=["tab_leaves"])
        if match.tab_leaves >= MAX_TAB_LEAVES:
            return {"forfeit": True, "result": resolve_duel(match, forfeit=True)}
        voided = None
        if match.q_started_at is not None:
            spec = match.questions[match.current]
            voided = match.current
            reveal = _close_question(match, match.current, {"option": None, "correct": False, "ms": spec["time_limit"] * 1000, "points": 0},
                                     _question(spec))
            return {"forfeit": False, "tab_leaves": match.tab_leaves, "max_tab_leaves": MAX_TAB_LEAVES, "voided": voided, "reveal": reveal}
        return {"forfeit": False, "tab_leaves": match.tab_leaves, "max_tab_leaves": MAX_TAB_LEAVES, "voided": None}


def _totals(match):
    n = len(match.answers)
    mine = {"points": sum(a["points"] for a in match.answers), "correct": sum(a["correct"] for a in match.answers),
            "ms": sum(a["ms"] for a in match.answers)}
    opp = match.opponent["answers"][:n]
    theirs = {"points": sum(a["points"] for a in opp), "correct": sum(a["correct"] for a in opp), "ms": sum(a["ms"] for a in opp)}
    return {"you": mine, "opponent": theirs}


# ── 4. Hasil duel ────────────────────────────────────────────────────────────
def outcome(me, opp):
    """'win' | 'lose' | 'draw' dari skor, lalu total waktu (lebih cepat menang)."""
    if me["points"] != opp["points"]:
        return "win" if me["points"] > opp["points"] else "lose"
    if me["ms"] != opp["ms"]:
        return "win" if me["ms"] < opp["ms"] else "lose"
    return "draw"


def resolve_duel(match, forfeit=False):
    """
    Akhiri duel (sekali saja): bandingkan skor penuh 10 soal, perbarui rank, pakai shield bila perlu,
    beri diamond saat menang, dan simpan penampilan pemenang sebagai GhostRecord.
    Soal yang belum dijawab (menyerah) dihitung 0.
    """
    with transaction.atomic():
        if RankedMatch.objects.filter(pk=match.pk, status=RankedMatch.ACTIVE).update(
                status=RankedMatch.FINISHED, finished_at=timezone.now()) == 0:
            match.refresh_from_db()
            return match.result
        match.refresh_from_db()
        while len(match.answers) < len(match.questions):          # menyerah: sisa soal = 0
            spec = match.questions[len(match.answers)]
            match.answers.append({"option": None, "correct": False, "ms": spec["time_limit"] * 1000, "points": 0})
        totals = _totals(match)
        verdict = "lose" if forfeit else outcome(totals["you"], totals["opponent"])
        rank = rank_of(match.user)
        state_before = rank.state
        shield_used, gems, delta = False, 0, 0
        if verdict == "draw":
            rank.record_draw(match.opponent_mmr)
        else:
            won = verdict == "win"
            protected = False
            if not won and not forfeit and ranking.loses_on_defeat(state_before):
                shield_used = protected = UserProfile.objects.filter(user=match.user, star_shields__gt=0).update(
                    star_shields=F("star_shields") - 1) == 1
            delta = rank.record_duel(won, match.opponent_mmr, protected)
            if won:
                gems = shop.award(match.user_id, shop.DUEL_WIN_REWARD)
        if not forfeit:                                            # selesai 10 soal tanpa menyerah/putus
            _save_ghost(match, totals["you"], state_before, rank)
        rank.refresh_from_db()
        match.result = {
            "verdict": verdict, "forfeit": forfeit, "delta": delta, "apex": state_before.tier == "apex",
            "shield_used": shield_used, "gems_awarded": gems, "terra_safe": verdict == "lose" and delta == 0 and not shield_used,
            "you": totals["you"], "opponent": totals["opponent"],
            "rank": {**describe(rank.state), "wins": rank.wins, "losses": rank.losses},
        }
        match.save(update_fields=["answers", "result"])
        return match.result


def _save_ghost(match, mine, state_before, rank):
    """Penampilan yang selesai (menang/kalah/seri) menjadi lawan hantu baru di pool yang sama."""
    GhostRecord.objects.create(
        user=match.user, match_seed=match.match_seed, pool=match.pool, mmr=rank.mmr,
        rank_label=ranking.label(state_before), questions=match.questions, answers=match.answers,
        total_score=mine["points"], correct=mine["correct"], total_ms=mine["ms"])


# ── Tampilan ─────────────────────────────────────────────────────────────────
def player_card(user):
    profile = UserProfile.objects.filter(user=user).select_related("faculty").first()
    return {
        "id": user.id, "name": user.first_name or user.username, "username": user.username,
        "level": level_for(profile.xp if profile else 0),
        "campus": profile.campus if profile and profile.campus != "Umum" else "",
        "faculty": profile.faculty.short_name if profile and profile.faculty else "",
        "rank": describe(rank_of(user).state),
        "avatar": avatar.describe(profile) if profile else {"kind": "initial"},
    }


def match_intro(match):
    """Data layar VS: kartu kedua pemain + daftar kesulitan 10 soal (soalnya sendiri belum dibuka)."""
    return {
        "match_id": match.id, "total": len(match.questions), "you": player_card(match.user),
        "opponent": match.opponent["card"],                          # jenis lawan (hantu/bot) sengaja tidak dikirim
        "difficulties": [q["difficulty"] for q in match.questions],
        "rules": {d: {"label": i["label"], "time": i["time"], "base": i["base"]} for d, i in DIFFICULTY.items()},
        "max_tab_leaves": MAX_TAB_LEAVES,
    }


def recent_results(user_ids, n=5):
    """
    Hasil n duel terakhir tiap pemain (urut lama → baru): 'w' menang, 'l' kalah, 'd' imbang.
    Menggabungkan Ranked Duel asinkron (RankedMatch) dengan riwayat duel real-time lama (DuelMatch).
    """
    from django.db.models import Q
    from .models import DuelMatch
    rows = {uid: [] for uid in user_ids}
    ranked = (RankedMatch.objects.filter(status=RankedMatch.FINISHED, user_id__in=user_ids)
              .order_by("-finished_at").values_list("user_id", "finished_at", "result")[:n * len(user_ids) * 2])
    for uid, at, res in ranked:
        rows[uid].append((at, {"win": "w", "lose": "l"}.get((res or {}).get("verdict"), "d")))
    old = (DuelMatch.objects.filter(status=DuelMatch.FINISHED)
           .filter(Q(player_a_id__in=user_ids) | Q(player_b_id__in=user_ids))
           .order_by("-finished_at").values_list("player_a_id", "player_b_id", "winner_id", "finished_at")[:n * len(user_ids) * 2])
    for a, b, winner, at in old:
        for uid in (a, b):
            if uid in rows:
                rows[uid].append((at, "d" if winner is None else "w" if winner == uid else "l"))
    return {uid: [r for _, r in sorted(items, key=lambda x: x[0])[-n:]] for uid, items in rows.items()}
