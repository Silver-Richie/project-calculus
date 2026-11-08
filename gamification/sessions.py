"""
Sesi latihan berlapis: pengundian soal per user, penilaian, dan progres.

Mechanism
---------
* Soal sebuah sesi tidak disimpan. Server mengundi `question_count` butir dari
  kumpulan sesi (QuestionTemplate + soal tetap) dengan rng ber-seed
  ``"<user>:<sesi>:<percobaan>"``. Setiap butir generator mendapat sub-seed
  sendiri, sehingga soal = fungsi murni dari (user, sesi, percobaan).
* Percobaan (`attempt`) = UserSessionProgress.attempts saat sesi dibuka. Membuka
  ulang tanpa mengirim jawaban memberi soal yang sama (tidak bisa "mengocok ulang");
  setelah dikirim, attempts bertambah sehingga percobaan berikutnya memakai angka baru.
* Penilaian membangun ulang soal dari seed yang sama, jadi kunci jawaban tidak
  pernah perlu disimpan.
* Sesi n+1 terbuka setelah sesi n lulus. Topik tuntas bila sesi wajib
  (REQUIRED_SESSIONS) lulus; sub-level tuntas bila semua topiknya tuntas.
"""

import math
import random

from django.db import transaction
from django.db.models import Q
from django.utils import timezone

from . import generators
from .models import PracticeSession, Question, SkillNode, Topic, UserProfile, UserProgress, UserSessionProgress

REQUIRED_SESSIONS = 3          # Sesi I–III wajib; IV–V tantangan opsional (XP ekstra)


# ── pengundian ──────────────────────────────────────────────────────────────
def _pool(session, faculty_id=None):
    """
    Daftar butir yang bisa diundi: ('g', key, weight) dan ('q', code, 1).

    Soal tetap milik fakultas tertentu (mis. FT-S1) hanya ikut diundi untuk user
    fakultas itu; soal umum (faculty kosong) untuk semua.
    """
    items = [("g", t.key, t.weight) for t in session.templates.all() if t.key in generators.REGISTRY]
    items += [("q", q.code, 1) for q in session.fixed_questions.all()
              if q.code and (q.faculty_id is None or q.faculty_id == faculty_id)]
    return items


def _extra_pool(session, faculty_id=None):
    """
    Bank soal tambahan di luar jenis inti sesi, agar soal tidak itu-itu saja.

    Mechanism — sumber generator ditambahkan berlapis, dari yang paling dekat dengan
    materi sesi, dan berhenti begitu total jenis soal mencapai MIN_VARIETY:
      1. Generator lain dari topik yang sama pada tingkat tetangga (sesi ±1).
      2. Ulasan: topik-topik sebelumnya di sub-level yang sama (tingkat ±1).
      3. Topik yang sama pada tingkat ±2.
      4. Ulasan: topik di sub-level sebelumnya pada jalur fakultas user (tingkat ±1).
    Lalu soal PDF dari database ikut ditambahkan: sub-level sama, tingkat kesulitan
    sama, bukan soal diagnostik. Generator yang dipinjam dijalankan pada tingkat
    terdekat yang didukungnya (lihat _gen_tier).
    """
    topic, tier = session.topic, session.number
    core = {t.key for t in session.templates.all()}
    earlier = set(Topic.objects.filter(node_id=topic.node_id, order__lt=topic.order).values_list("slug", flat=True))
    prev_node = (SkillNode.objects.filter(kind="lesson", order__lt=topic.node.order)
                 .filter(Q(faculty__isnull=True) | Q(faculty_id=faculty_id)).order_by("-order").first())
    prev_topics = set(prev_node.topics.values_list("slug", flat=True)) if prev_node else set()
    layers = [({topic.slug}, 1), (earlier, 1), ({topic.slug}, 2), (prev_topics, 1)]

    picked = []
    for slugs, reach in layers:
        if len(core) + len(picked) >= MIN_VARIETY:
            break
        picked += [g.key for g in generators.REGISTRY.values()
                   if g.key not in core and g.key not in picked
                   and slugs.intersection(g.topics) and any(abs(t - tier) <= reach for t in g.tiers)]
    items = [("g", key) for key in picked]
    pdf = (Question.objects.filter(node_id=topic.node_id, difficulty=generators.TIER_DIFFICULTY[tier], is_diagnostic=False)
           .exclude(session=session).exclude(code="")
           .filter(Q(faculty__isnull=True) | Q(faculty_id=faculty_id)))
    items += [("q", code) for code in pdf.values_list("code", flat=True)]
    return items


def _gen_tier(key, tier):
    """Tingkat yang dipakai saat menjalankan generator: tingkat sesi bila didukung, selain itu yang terdekat."""
    return min(generators.REGISTRY[key].tiers, key=lambda t: (abs(t - tier), t))


def _user_faculty_id(user_id):
    return UserProfile.objects.filter(user_id=user_id).values_list("faculty_id", flat=True).first()


def _deal(rng, bag, k, used):
    """
    Ambil k butir dari `bag` secara bergiliran.

    Mechanism: setiap putaran, bag dikocok Fisher-Yates (`rng.shuffle`) lalu diambil
    berurutan, sehingga semua jenis soal muncul dulu sebelum ada yang berulang.
    Soal tetap ('q') paling banyak sekali per sesi (dicatat di `used`).
    """
    out = []
    while len(out) < k:
        items = [it for it in bag if not (it[0] == "q" and it[1] in used)]
        if not items:
            break
        rng.shuffle(items)
        for kind, key in items[: k - len(out)]:
            if kind == "q":
                used.add(key)
            out.append((kind, key))
    return out


CORE_SHARE = 0.6               # porsi minimal soal dari jenis inti sesi; sisanya dari bank tambahan
MIN_VARIETY = 8                # target jumlah jenis soal per sesi sebelum berhenti meminjam dari lapisan berikutnya


def _draw(session, user_id, attempt):
    """
    Undi 10 slot soal untuk satu percobaan.

    Mechanism: rng ber-seed ``"<user>:<sesi>:<percobaan>"`` (bisa dibangun ulang saat
    penilaian). Sebanyak CORE_SHARE slot diambil dari jenis inti sesi (berbobot),
    sisanya dari _extra_pool; bila bank tambahan kurang, slot diisi jenis inti.
    Hasil gabungan dikocok sekali lagi agar soal tambahan tidak menumpuk di akhir.
    """
    rng = random.Random(f"{user_id}:{session.id}:{attempt}")
    faculty_id = _user_faculty_id(user_id)
    n = session.question_count
    core = [(kind, key) for kind, key, w in _pool(session, faculty_id) for _ in range(max(1, w))]
    extra = _extra_pool(session, faculty_id)
    used = set()
    slots = _deal(rng, extra, n - math.ceil(CORE_SHARE * n) if core else n, used)
    slots += _deal(rng, core, n - len(slots), used)
    rng.shuffle(slots)
    return [(kind, key, rng.randrange(10 ** 9)) for kind, key in slots]


def _fixed_question_payload(q, seed):
    """
    Soal tetap (dari PDF) → payload sesi, dengan urutan opsi diacak.

    Mechanism: opsi dikocok Fisher-Yates (`random.shuffle`) memakai rng ber-seed
    ``"<code>|<seed>"``. Seed berasal dari pengundian sesi, jadi saat penilaian
    urutan yang sama dibangun ulang dan id opsi (= indeks) tetap cocok.
    """
    from .services import serialize_question
    data = serialize_question(q)
    data["id"] = f"q:{q.code}"
    opts = data["options"]
    random.Random(f"{q.code}|{seed}").shuffle(opts)
    data["options"] = [{"id": i, "text": o["text"], "is_correct": o["is_correct"]} for i, o in enumerate(opts)]
    return data


def build_quiz(session, user_id, attempt):
    """Soal lengkap (dengan kunci & pembahasan) untuk satu percobaan."""
    drawn = _draw(session, user_id, attempt)
    fixed = {q.code: q for q in Question.objects.filter(code__in=[k for kind, k, _ in drawn if kind == "q"])
             .prefetch_related("options")}
    questions = []
    for i, (kind, key, sub) in enumerate(drawn, start=1):
        if kind == "g":
            q = generators.generate(key, sub, _gen_tier(key, session.number))
            q["id"] = f"g:{key}:{sub}"
        else:
            q = _fixed_question_payload(fixed[key], sub)
        if kind == "g":
            q["code"] = f"{session.topic.slug.split('-', 1)[1].upper()[:12]}-S{session.number}-{i:02d}"
        q["xp_reward"] = session.xp_per_question
        q["difficulty_label"] = session.get_tier_display()
        questions.append(q)
    return questions


# ── status & progres ────────────────────────────────────────────────────────
def session_meta(session):
    return {
        "id": session.id, "number": session.number, "tier": session.tier, "tier_label": session.get_tier_display(),
        "title": session.title, "question_count": session.question_count,
        "pass_score": pass_score(session), "xp_per_question": session.xp_per_question,
    }


def pass_score(session):
    return math.ceil(session.pass_ratio * session.question_count)


def progress_map(user):
    """{session_id: {...}} untuk user login (dipakai frontend menentukan kunci sesi)."""
    if not user.is_authenticated:
        return {}
    return {
        p.session_id: {"attempts": p.attempts, "best": p.best_score, "last": p.last_score, "passed": p.passed}
        for p in UserSessionProgress.objects.filter(user=user)
    }


def topic_unlocked(user, topic):
    """Topik dibuka berurutan: topik pertama terbuka, topik k terbuka bila topik k−1 tuntas."""
    prev = Topic.objects.filter(node=topic.node, order__lt=topic.order).order_by("-order").first()
    return prev is None or topic_done(user, prev)


def is_unlocked(user, session):
    """Sesi 1 terbuka bila topiknya terbuka; sesi n terbuka bila sesi n−1 pada topik yang sama lulus."""
    if session.number == 1:
        return topic_unlocked(user, session.topic)
    return UserSessionProgress.objects.filter(
        user=user, session__topic=session.topic, session__number=session.number - 1, passed=True
    ).exists()


def topic_done(user, topic):
    return UserSessionProgress.objects.filter(
        user=user, session__topic=topic, session__number=REQUIRED_SESSIONS, passed=True
    ).exists()


def _complete_node_if_done(user, node):
    """Tandai sub-level selesai (UserProgress) bila semua topiknya tuntas; aktifkan node berikutnya."""
    topics = list(node.topics.all())
    if not topics or not all(topic_done(user, t) for t in topics):
        return None
    prog, _ = UserProgress.objects.get_or_create(user=user, node=node)
    if prog.status != "completed":
        prog.status, prog.completed_at = "completed", timezone.now()
        prog.save()
    return node.slug


# ── Nyawa ───────────────────────────────────────────────────────────────────
class NoHeartsError(PermissionError):
    """Nyawa habis: sesi latihan tidak bisa dibuka/dikirim sampai nyawa terisi ulang."""

    def __init__(self, state):
        self.state = state
        hours, rest = divmod(state["refill_in"], 3600)
        super().__init__(f"Nyawamu habis. Nyawa penuh kembali dalam {hours} jam {rest // 60} menit.")


def _profile_for_hearts(user, lock=False):
    qs = UserProfile.objects.select_for_update() if lock else UserProfile.objects
    profile, _ = qs.get_or_create(user=user)
    return profile


def require_hearts(user, lock=False):
    """Pastikan user masih punya nyawa (setelah isi ulang otomatis). Raise NoHeartsError bila 0."""
    profile = _profile_for_hearts(user, lock)
    state = profile.hearts_state()
    if state["hearts"] <= 0:
        raise NoHeartsError(state)
    return profile


# ── API utama ───────────────────────────────────────────────────────────────
def open_session(user, session):
    """
    Soal untuk percobaan berjalan.

    Raise PermissionError bila sesi masih terkunci, NoHeartsError bila nyawa habis.
    """
    if not is_unlocked(user, session):
        raise PermissionError("Selesaikan sesi/topik sebelumnya terlebih dahulu.")
    require_hearts(user)
    progress, _ = UserSessionProgress.objects.get_or_create(user=user, session=session)
    return {
        "session": session_meta(session),
        "topic": {"slug": session.topic.slug, "title": session.topic.title},
        "attempt": progress.attempts,
        "questions": build_quiz(session, user.id, progress.attempts),
    }


@transaction.atomic
def submit_session(user, session, attempt, answers):
    """
    Menilai jawaban sesi. `answers` = [{"id": "g:key:seed", "option": 2}, ...].

    XP hanya diberikan untuk peningkatan skor terbaik (tidak bisa 'farming' XP
    dengan mengulang sesi yang sama). Gagal lulus mengurangi satu nyawa; dengan
    nyawa 0 jawaban tidak dinilai (NoHeartsError), agar sesi yang dibuka di tab
    lain sebelum nyawa habis tidak bisa dipakai untuk terus mencoba.
    """
    if not is_unlocked(user, session):
        raise PermissionError("Sesi masih terkunci.")
    profile = require_hearts(user, lock=True)
    progress, _ = UserSessionProgress.objects.select_for_update().get_or_create(user=user, session=session)
    if attempt != progress.attempts:
        raise ValueError("Percobaan sudah kedaluwarsa. Muat ulang sesi.")

    quiz = build_quiz(session, user.id, attempt)
    key = {q["id"]: next(o["id"] for o in q["options"] if o["is_correct"]) for q in quiz}
    chosen = {str(a.get("id")): a.get("option") for a in answers}
    results = [{"id": qid, "correct": chosen.get(qid) == right} for qid, right in key.items()]
    score = sum(r["correct"] for r in results)

    prev_best = progress.best_score
    progress.attempts += 1
    progress.last_score = score
    progress.best_score = max(prev_best, score)
    newly_passed = score >= pass_score(session) and not progress.passed
    if score >= pass_score(session):
        progress.passed = True
        progress.passed_at = progress.passed_at or timezone.now()
    progress.save()

    heart_lost = score < pass_score(session)
    if heart_lost:
        profile.lose_heart()

    xp = max(0, score - prev_best) * session.xp_per_question
    if xp:
        profile.add_xp(xp)

    node = session.topic.node
    completed_node = _complete_node_if_done(user, node) if newly_passed else None
    next_node = None
    if completed_node:
        fac_id = _user_faculty_id(user.id)
        nxt = (SkillNode.objects.filter(kind="lesson", order__gt=node.order)
               .filter(Q(faculty__isnull=True) | Q(faculty_id=fac_id)).order_by("order").first())
        if nxt:
            np_, _ = UserProgress.objects.get_or_create(user=user, node=nxt)
            if np_.status == "locked":
                np_.status = "active"
                np_.save()
            next_node = nxt.slug

    return {
        "heart_lost": heart_lost, "hearts": profile.hearts_state(),
        "score": score, "total": len(quiz), "pass_score": pass_score(session), "passed": score >= pass_score(session),
        "best": progress.best_score, "attempts": progress.attempts, "xp_awarded": xp, "results": results,
        "unlocked_next_session": newly_passed and session.number < 5,
        "topic_done": topic_done(user, session.topic),
        "node_completed": completed_node, "next_node": next_node,
    }


def mark_node_completed(user, node):
    """Simpan penyelesaian node lama (kuis per node) ke database."""
    prog, _ = UserProgress.objects.get_or_create(user=user, node=node)
    if prog.status != "completed":
        prog.status, prog.completed_at = "completed", timezone.now()
        prog.save()
    return prog

