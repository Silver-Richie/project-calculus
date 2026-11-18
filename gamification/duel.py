"""
Calculus Bridge - Duel kalkulus real-time: aturan & penyimpanan (dipanggil consumers.DuelConsumer).

Alur
----
1. Antrean   : pemain Level ≥ MIN_LEVEL masuk antrean (DuelQueue). find_opponent() mencari lawan
               dengan nilai kemampuan (mmr) terdekat dalam jendela yang melebar selama menunggu
               (WINDOW_START + WINDOW_STEP tiap 10 detik, maks WINDOW_MAX). Lawan yang sama tidak
               dipertemukan lagi dalam REMATCH_COOLDOWN.
2. Soal      : QUESTION_COUNT soal identik dari generator (resep key/seed/tier disimpan di DuelMatch);
               tingkat kesulitan mengikuti tier pemain yang lebih rendah (POOLS). Ke browser hanya
               dikirim teks soal & opsi (tanpa kunci).
3. Menjawab  : record_answer() menilai di server; waktu diukur dari q_started_at di server.
               Benar = 100 + bonus cepat sampai 50; salah/tidak menjawab = 0.
4. Per soal  : resolve_question() menutup soal (dipanggil saat kedua pemain menjawab atau waktu
               habis; aman dipanggil berulang), lalu start_question() membuka soal berikutnya.
5. Hasil     : poin tertinggi menang; seri dipecah total waktu; masih seri = imbang.
               Kalah dengan selisih ≤ 1 soal benar dilindungi (bintang tidak berkurang).
               Keluar di tengah duel (forfeit) = kalah tanpa perlindungan.
               Bintang & nilai kemampuan diperbarui lewat PlayerRank (aturan di ranking.py). Duel tidak memberi XP.
               Menang (bukan karena lawan keluar) memberi +2 diamond; Perisai Bintang dari toko
               otomatis menahan bintang saat kalah (use_shield).
"""

import random
from datetime import timedelta

from django.db import transaction
from django.db.models import F, Q
from django.utils import timezone

from . import generators, ranking, shop
from .leveling import level_for
from .models import DuelAnswer, DuelMatch, DuelQueue, Topic, UserProfile, rank_of
from .ranking import TIERS, describe

MIN_LEVEL = 3
QUESTION_COUNT = 5
WINDOW_START, WINDOW_STEP, WINDOW_MAX = 100, 50, 500
REMATCH_COOLDOWN = timedelta(minutes=10)
QUEUE_TIMEOUT = 60            # detik menunggu lawan sebelum menyerah
GRACE_MS = 1500               # toleransi latensi jaringan setelah waktu soal habis
BASE_POINTS, SPEED_BONUS = 100, 50

# Tier → (level kurikulum sumber soal, tingkat generator) dan waktu per soal (detik).
POOLS = {
    "terra": (("precalculus", "kalkulus-dasar"), (1,)),
    "luna": (("kalkulus-dasar",), (1, 2)),
    "solar": (("kalkulus-dasar", "kalkulus-menengah"), (2,)),
    "nova": (("kalkulus-menengah",), (2, 3)),
    "apex": (("kalkulus-menengah", "kalkulus-lanjut"), (3, 4)),
}
TIME_LIMITS = {"terra": 45, "luna": 55, "solar": 65, "nova": 75, "apex": 90}


# ── Kelayakan & antrean ─────────────────────────────────────────────────────
def eligibility(user):
    """None bila boleh duel, selain itu pesan alasannya."""
    profile = UserProfile.objects.filter(user=user).first()
    level = level_for(profile.xp if profile else 0)
    if level < MIN_LEVEL:
        return f"Duel terbuka mulai Level {MIN_LEVEL}. Levelmu sekarang {level}: selesaikan sesi latihan topik untuk menambah XP."
    return None


def _window(joined_at, now):
    waited = (now - joined_at).total_seconds()
    return min(WINDOW_MAX, WINDOW_START + WINDOW_STEP * int(waited // 10))


def _recent_opponents(user, now):
    recent = DuelMatch.objects.filter(Q(player_a=user) | Q(player_b=user), created_at__gte=now - REMATCH_COOLDOWN)
    return {uid for m in recent for uid in m.players()} - {user.id}


def find_opponent(user, channel_name, now=None):
    """
    Masukkan/perbarui pemain di antrean lalu cari lawan. Mengembalikan (DuelMatch, kanal_lawan)
    bila lawan ditemukan (keduanya keluar dari antrean), atau (None, None) bila masih menunggu.
    """
    now = now or timezone.now()
    me = rank_of(user)
    with transaction.atomic():
        entry, created = DuelQueue.objects.get_or_create(
            user=user, defaults={"channel_name": channel_name, "mmr": me.mmr, "joined_at": now})
        if not created and entry.channel_name != channel_name:
            entry.channel_name, entry.mmr, entry.joined_at = channel_name, me.mmr, now
            entry.save()
        blocked = _recent_opponents(user, now) | {user.id}
        best = None
        for cand in DuelQueue.objects.exclude(user_id__in=blocked).select_related("user"):
            window = max(_window(entry.joined_at, now), _window(cand.joined_at, now))
            gap = abs(cand.mmr - entry.mmr)
            if gap <= window and (best is None or gap < abs(best.mmr - entry.mmr)):
                best = cand
        if not best:
            return None, None
        # Ambil lawan secara atomik: bila pemain lain lebih dulu mengambilnya, coba lagi nanti.
        if DuelQueue.objects.filter(pk=best.pk).delete()[0] == 0:
            return None, None
        entry.delete()
        match = create_match(user, best.user)
        return match, best.channel_name


def leave_queue(user):
    DuelQueue.objects.filter(user=user).delete()


def queue_expired(user, now=None):
    entry = DuelQueue.objects.filter(user=user).first()
    return bool(entry) and ((now or timezone.now()) - entry.joined_at).total_seconds() >= QUEUE_TIMEOUT


# ── Soal ───────────────────────────────────────────────────────────────────
def pick_questions(tier, rng=None):
    """QUESTION_COUNT resep soal dari topik umum yang berbeda-beda, sesuai POOLS[tier]."""
    rng = rng or random.Random()
    levels, tiers = POOLS[tier]
    topics = list(Topic.objects.filter(node__faculty__isnull=True, node__main_level__slug__in=levels))
    cands = [(t, g) for t in topics for g in generators.REGISTRY.values()
             if t.slug in g.topics and set(g.tiers) & set(tiers)]
    rng.shuffle(cands)
    picked, used = [], set()
    for topic, gen in cands:
        if topic.slug in used:
            continue
        gen_tier = rng.choice([t for t in gen.tiers if t in tiers])
        seed = rng.randrange(10 ** 9)
        generators.generate(gen.key, seed, gen_tier)          # pastikan soal valid sebelum dipakai
        used.add(topic.slug)
        picked.append({"key": gen.key, "seed": seed, "tier": gen_tier, "topic": topic.title})
        if len(picked) == QUESTION_COUNT:
            break
    return picked


def _question(match, index):
    spec = match.questions[index]
    return generators.generate(spec["key"], spec["seed"], spec["tier"])


def question_payload(match, index):
    """Soal untuk dikirim ke kedua pemain: teks & opsi saja (kunci tidak dikirim)."""
    q = _question(match, index)
    deadline = match.q_started_at + timedelta(seconds=match.time_limit)
    return {
        "index": index, "total": len(match.questions), "topic": match.questions[index]["topic"],
        "prompt": q["prompt"], "options": [{"id": o["id"], "text": o["text"]} for o in q["options"]],
        "time_limit": match.time_limit, "deadline": int(deadline.timestamp() * 1000),
    }


def create_match(user_a, user_b):
    ra, rb = rank_of(user_a), rank_of(user_b)
    tier = min(ra.tier, rb.tier, key=TIERS.index)
    return DuelMatch.objects.create(player_a=user_a, player_b=user_b, tier=tier,
                                    questions=pick_questions(tier), time_limit=TIME_LIMITS[tier])


def start_question(match_id, index):
    """Buka soal `index` (sekali saja). Mengembalikan payload soal, atau None bila sudah dibuka/selesai."""
    with transaction.atomic():
        updated = DuelMatch.objects.filter(pk=match_id, status=DuelMatch.ACTIVE, current=index,
                                           q_started_at__isnull=True).update(q_started_at=timezone.now())
        if not updated:
            return None
        return question_payload(DuelMatch.objects.get(pk=match_id), index)


# ── Menjawab & menutup soal ────────────────────────────────────────────────
def points_for(correct, ms, limit_ms):
    if not correct:
        return 0
    return BASE_POINTS + round(SPEED_BONUS * max(0, limit_ms - ms) / limit_ms)


def record_answer(match_id, user, index, option_id, now=None):
    """
    Nilai satu jawaban. Mengembalikan (ok, pesan_galat, kedua_pemain_sudah_menjawab).
    Ditolak bila bukan soal yang sedang berjalan, sudah menjawab, atau waktu habis.
    """
    now = now or timezone.now()
    with transaction.atomic():
        match = DuelMatch.objects.filter(pk=match_id, status=DuelMatch.ACTIVE).first()
        if not match or user.id not in match.players():
            return False, "Duel tidak ditemukan.", False
        if match.current != index or match.q_started_at is None:
            return False, "Soal ini sudah ditutup.", False
        ms = int((now - match.q_started_at).total_seconds() * 1000)
        limit_ms = match.time_limit * 1000
        if ms > limit_ms + GRACE_MS:
            return False, "Waktu habis.", False
        q = _question(match, index)
        correct = any(o["id"] == option_id and o["is_correct"] for o in q["options"])
        _, created = DuelAnswer.objects.get_or_create(
            match=match, user=user, index=index,
            defaults={"option_id": option_id, "correct": correct, "ms": min(ms, limit_ms),
                      "points": points_for(correct, min(ms, limit_ms), limit_ms)})
        if not created:
            return False, "Kamu sudah menjawab soal ini.", False
        both = DuelAnswer.objects.filter(match=match, index=index).count() == 2
        return True, "", both


def _totals(match):
    totals = {uid: {"points": 0, "correct": 0, "ms": 0} for uid in match.players()}
    for a in match.answers.all():
        t = totals[a.user_id]
        t["points"] += a.points
        t["correct"] += a.correct
        t["ms"] += a.ms
    return totals


def resolve_question(match_id, index, force=False):
    """
    Tutup soal `index` (sekali saja): pemain yang belum menjawab dicatat tidak menjawab.
    Hanya menutup bila kedua pemain sudah menjawab, waktu habis, atau force=True.
    Mengembalikan ringkasan untuk ditampilkan, atau None bila soal sudah ditutup / belum waktunya.
    """
    with transaction.atomic():
        match = DuelMatch.objects.filter(pk=match_id, status=DuelMatch.ACTIVE, current=index,
                                         q_started_at__isnull=False).first()
        if not match:
            return None
        limit_ms = match.time_limit * 1000
        answered = {a.user_id: a for a in match.answers.filter(index=index)}
        elapsed = (timezone.now() - match.q_started_at).total_seconds() * 1000
        if not force and len(answered) < 2 and elapsed < limit_ms:
            return None
        if DuelMatch.objects.filter(pk=match_id, current=index, q_started_at=match.q_started_at) \
                .update(current=index + 1, q_started_at=None) == 0:
            return None
        for uid in match.players():
            if uid not in answered:
                answered[uid] = DuelAnswer.objects.create(match=match, user_id=uid, index=index, ms=limit_ms)
        q = _question(match, index)
        match.refresh_from_db()
        return {
            "index": index, "last": index + 1 >= len(match.questions),
            "correct_option": next(o["id"] for o in q["options"] if o["is_correct"]),
            "answer": q["answer"],
            "players": {str(uid): {"option": a.option_id, "correct": a.correct, "points": a.points} for uid, a in answered.items()},
            "totals": {str(uid): t for uid, t in _totals(match).items()},
        }


# ── Hasil akhir ────────────────────────────────────────────────────────────
def outcome(totals_a, totals_b):
    """'a', 'b', atau 'draw' dari poin, lalu total waktu (lebih cepat menang)."""
    if totals_a["points"] != totals_b["points"]:
        return "a" if totals_a["points"] > totals_b["points"] else "b"
    if totals_a["ms"] != totals_b["ms"]:
        return "a" if totals_a["ms"] < totals_b["ms"] else "b"
    return "draw"


def is_protected(loser, winner):
    """Kalah tipis (selisih ≤ 1 soal benar) → bintang tidak berkurang."""
    return winner["correct"] - loser["correct"] <= 1


def use_shield(user_id, state):
    """
    Pakai satu Perisai Bintang (toko diamond) bila kekalahan ini akan mengurangi bintang.

    Mechanism: kekalahan tanpa perlindungan disimulasikan dengan ranking.apply_result; hanya
    bila bintang berkurang, stok perisai dikurangi lewat UPDATE bersyarat (star_shields > 0)
    sehingga perisai tidak pernah terpakai dua kali atau menjadi negatif.
    """
    if ranking.apply_result(state, won=False)[1] >= 0:
        return False
    return UserProfile.objects.filter(user_id=user_id, star_shields__gt=0).update(star_shields=F("star_shields") - 1) == 1


def finish_match(match_id, forfeit_by=None):
    """
    Akhiri duel (sekali saja) dan perbarui rank kedua pemain.
    forfeit_by = id pemain yang keluar di tengah duel (otomatis kalah, tanpa perlindungan).
    Mengembalikan ringkasan per pemain, atau None bila duel sudah selesai.
    """
    with transaction.atomic():
        if DuelMatch.objects.filter(pk=match_id, status=DuelMatch.ACTIVE).update(
                status=DuelMatch.FINISHED, finished_at=timezone.now()) == 0:
            return None
        match = DuelMatch.objects.select_related("player_a", "player_b").get(pk=match_id)
        totals = _totals(match)
        a, b = match.player_a_id, match.player_b_id
        if forfeit_by:
            result = "b" if forfeit_by == a else "a"
        else:
            result = outcome(totals[a], totals[b])
        ranks = {a: rank_of(match.player_a), b: rank_of(match.player_b)}
        mmr_before = {uid: r.mmr for uid, r in ranks.items()}
        players = {}
        for uid, side in ((a, "a"), (b, "b")):
            opp = b if uid == a else a
            shield_used, gems = False, 0
            if result == "draw":
                ranks[uid].record_draw(mmr_before[opp])
                delta, protected, verdict = 0, False, "draw"
            else:
                won = result == side
                protected = not won and not forfeit_by and is_protected(totals[uid], totals[opp])
                if not won and not forfeit_by and not protected:
                    shield_used = use_shield(uid, ranks[uid].state)
                    protected = shield_used
                delta = ranks[uid].record_duel(won, mmr_before[opp], protected)
                verdict = "win" if won else "lose"
                if won and not forfeit_by:
                    gems = shop.award(uid, shop.DUEL_WIN_REWARD)
            players[str(uid)] = {"verdict": verdict, "star_delta": delta, "protected": protected,
                                 "shield_used": shield_used, "gems_awarded": gems,
                                 "rank": {**describe(ranks[uid].state), "wins": ranks[uid].wins, "losses": ranks[uid].losses},
                                 **totals[uid]}
        match.winner_id = None if result == "draw" else (a if result == "a" else b)
        match.result = {"players": players, "forfeit_by": forfeit_by}
        match.save(update_fields=["winner", "result"])
        return match.result


def active_match_of(user):
    return DuelMatch.objects.filter(Q(player_a=user) | Q(player_b=user), status=DuelMatch.ACTIVE).first()


def player_card(user):
    """Info lawan untuk layar VS."""
    profile = UserProfile.objects.filter(user=user).select_related("faculty").first()
    return {
        "id": user.id, "name": user.first_name or user.username,
        "level": level_for(profile.xp if profile else 0),
        "campus": profile.campus if profile and profile.campus != "Umum" else "",
        "faculty": profile.faculty.short_name if profile and profile.faculty else "",
        "rank": describe(rank_of(user).state),
    }
