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


def _user_faculty_id(user_id):
    return UserProfile.objects.filter(user_id=user_id).values_list("faculty_id", flat=True).first()


def _draw(session, user_id, attempt):
    """
    Undi slot soal secara seimbang: kumpulan berbobot diacak lalu diambil bergiliran,
    sehingga 10 soal tersebar ke semua jenis generator sebelum ada yang berulang.
    """
    rng = random.Random(f"{user_id}:{session.id}:{attempt}")
    pool = _pool(session, _user_faculty_id(user_id))
    if not pool:
        return []
    bag = [(kind, key) for kind, key, w in pool for _ in range(max(1, w))]
    slots = []
    while len(slots) < session.question_count:
        rng.shuffle(bag)
        slots.extend(bag)
    slots = slots[: session.question_count]
    # soal tetap tidak boleh muncul dua kali
    seen, out = set(), []
    for kind, key in slots:
        if kind == "q":
            if key in seen:
                continue
            seen.add(key)
        out.append((kind, key, rng.randrange(10 ** 9)))
    return out


def _fixed_question_payload(q):
    from .services import serialize_question
    data = serialize_question(q)
    data["id"] = f"q:{q.code}"
    data["options"] = [{"id": i, "text": o["text"], "is_correct": o["is_correct"]} for i, o in enumerate(data["options"])]
    return data


def build_quiz(session, user_id, attempt):
    """Soal lengkap (dengan kunci & pembahasan) untuk satu percobaan."""
    fixed = {q.code: q for q in session.fixed_questions.prefetch_related("options")}
    questions = []
    for i, (kind, key, sub) in enumerate(_draw(session, user_id, attempt), start=1):
        if kind == "g":
            q = generators.generate(key, sub, session.number)
            q["id"] = f"g:{key}:{sub}"
        else:
            q = _fixed_question_payload(fixed[key])
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


# ── API utama ───────────────────────────────────────────────────────────────
def open_session(user, session):
    """Soal untuk percobaan berjalan. Raise PermissionError bila sesi masih terkunci."""
    if not is_unlocked(user, session):
        raise PermissionError("Selesaikan sesi/topik sebelumnya terlebih dahulu.")
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
    dengan mengulang sesi yang sama).
    """
    if not is_unlocked(user, session):
        raise PermissionError("Sesi masih terkunci.")
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

    xp = max(0, score - prev_best) * session.xp_per_question
    if xp:
        profile, _ = UserProfile.objects.get_or_create(user=user)
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

