"""
Calculus Bridge — logika bisnis kurikulum & diagnostik.

Views hanya memanggil fungsi di sini lalu mengembalikan JSON, sehingga logika
pemilihan jalur belajar dan evaluasi diagnostik mudah diuji secara terpisah.
"""

import random

from django.db.models import Prefetch, Q

from .models import (
    Faculty, SourceDocument, SkillNode, LessonSection, Question, Option, MainLevel, Topic, PracticeSession,
)

DEFAULT_FACULTY = "fasilkom"


def get_faculty(slug):
    """Mengembalikan Faculty berdasarkan slug, atau fakultas default jika tidak ditemukan."""
    return Faculty.objects.filter(slug=slug).first() or Faculty.objects.filter(slug=DEFAULT_FACULTY).first()


def _visible_to(faculty):
    """Filter Q: konten umum (faculty kosong) + konten milik fakultas tersebut."""
    return Q(faculty__isnull=True) | Q(faculty=faculty)


def tree_nodes(faculty):
    """
    Node skill tree untuk satu fakultas, berurutan.

    Mechanism: node diurutkan per level utama (order = level × 100 + urutan).
    Node umum (faculty = NULL) dipakai semua fakultas; node khusus hanya milik
    fakultas yang dipilih. Node bertipe 'reference' (lampiran) tidak masuk skill tree.
    Sub-level kurikulum baru membawa Topic → materi + 5 PracticeSession.
    """
    return (
        SkillNode.objects.filter(kind="lesson")
        .filter(_visible_to(faculty))
        .select_related("source_document", "faculty", "main_level")
        .prefetch_related(
            Prefetch("sections", queryset=LessonSection.objects.order_by("order")),
            Prefetch("topics", queryset=Topic.objects.order_by("order").prefetch_related(
                Prefetch("sections", queryset=LessonSection.objects.select_related("source_document").order_by("order")),
                Prefetch("sessions", queryset=PracticeSession.objects.order_by("number")),
            )),
            Prefetch(
                "questions",
                queryset=Question.objects.select_related("source_document")
                .prefetch_related(Prefetch("options", queryset=Option.objects.order_by("order")))
                .order_by("order", "id"),
            ),
        )
        .order_by("order", "stage_number")
    )


def option_list(q):
    """Opsi soal: urutan acak bila sudah dikocok (lihat diagnostic_questions), selain itu urutan database."""
    return getattr(q, "shuffled_options", None) or list(q.options.all())


def serialize_question(q, include_answer=True):
    """Soal → dict JSON. `include_answer=False` dipakai untuk tes diagnostik."""
    data = {
        "code": q.code,
        "difficulty": q.difficulty,
        "difficulty_label": q.get_difficulty_display(),
        "prompt": q.prompt,
        "xp_reward": q.xp_reward,
        "source": q.source_document.filename if q.source_document else "",
        "options": [
            {"id": o.id, "text": o.text, **({"is_correct": o.is_correct} if include_answer else {})}
            for o in option_list(q)
        ],
    }
    if include_answer:
        data.update({
            "steps": q.steps,
            "answer": q.answer,
            "explanation": q.explanation,
            "graphs": q.graphs,
        })
    return data


def serialize_node(node, with_content=True):
    data = {
        "slug": node.slug,
        "kind": node.kind,
        "title": node.title,
        "stage_number": node.stage_number,
        "order": node.order,
        "icon": node.icon,
        "is_boss": node.is_boss,
        "badge_label": node.badge_label,
        "subtitle": node.subtitle,
        "summary": node.summary_html,
        "faculty": node.faculty.slug if node.faculty else None,
        "main_level": node.main_level.slug if node.main_level_id else None,
        "source": {
            "slug": node.source_document.slug,
            "filename": node.source_document.filename,
            "title": node.source_document.title,
        } if node.source_document else None,
    }
    if with_content:
        data["sections"] = [
            {"heading": s.heading, "body_html": s.body_html, "graphs": s.graphs}
            for s in node.sections.all()
        ]
        data["questions"] = [serialize_question(q) for q in node.questions.all()]
        data["topics"] = [serialize_topic(t) for t in node.topics.all()]
    return data


def serialize_topic(topic):
    """Topik + materi + metadata 5 sesi (soal sesi diambil terpisah lewat /api/session/<id>/)."""
    from .sessions import session_meta
    return {
        "slug": topic.slug,
        "title": topic.title,
        "icon": topic.icon,
        "summary": topic.summary,
        "references": topic.references,
        "sections": [{"heading": s.heading, "body_html": s.body_html, "graphs": s.graphs,
                      "source": s.source_document.filename if s.source_document_id else ""}
                     for s in topic.sections.all()],
        "sessions": [session_meta(s) for s in topic.sessions.all()],
    }


def build_curriculum(faculty, user=None):
    """
    Kurikulum lengkap satu fakultas untuk frontend.

    Returns dict berisi:
      - tree       : node skill tree (materi + soal + pembahasan + grafik)
      - documents  : berkas sumber yang relevan (umum + fakultas ini), untuk halaman Lesson
      - references : node lampiran (bacaan saja)
    """
    nodes = list(tree_nodes(faculty))
    references = (
        SkillNode.objects.filter(kind="reference")
        .select_related("source_document")
        .prefetch_related(Prefetch("sections", queryset=LessonSection.objects.order_by("order")))
    )

    documents = []
    for doc in SourceDocument.objects.filter(_visible_to(faculty)).order_by("order"):
        if doc.category == "soal":
            items = [q.code for n in nodes for q in n.questions.all() if q.source_document_id == doc.id]
        else:
            items = [n.slug for n in nodes if n.source_document_id == doc.id]
            items += [r.slug for r in references if r.source_document_id == doc.id]
        if items:
            documents.append({
                "slug": doc.slug,
                "filename": doc.filename,
                "title": doc.title,
                "subtitle": doc.subtitle,
                "category": doc.category,
                "items": items,
            })

    from .sessions import progress_map, REQUIRED_SESSIONS
    return {
        "faculty": faculty.slug if faculty else None,
        "main_levels": [
            {"slug": m.slug, "title": m.title, "subtitle": m.subtitle, "icon": m.icon, "order": m.order}
            for m in MainLevel.objects.order_by("order")
        ],
        "required_sessions": REQUIRED_SESSIONS,
        "session_progress": progress_map(user) if user is not None else {},
        "tree": [serialize_node(n) for n in nodes],
        "documents": documents,
        "references": [serialize_node(r) | {"questions": []} for r in references],
    }


# ── Diagnostik ────────────────────────────────────────────────────────────
# Komposisi tes kemampuan awal: 10 soal = 5 mudah, 3 sedang, 2 sulit.
DIAGNOSTIC_PLAN = (("basic", 5), ("medium", 3), ("high", 2))

# Batas lulus per tingkat (proporsi jawaban benar).
PASS_RATIO = {"basic": 0.6, "medium": 0.6, "high": 0.5}

EVALUATION_LABELS = {
    "weak_foundation": "Perlu Penguatan Fondasi",
    "ready_for_calculus": "Siap Kalkulus (Jalur Standar)",
    "mastery": "Penguasaan Tinggi",
}


def diagnostic_questions(faculty, rng=None):
    """
    Soal tes diagnostik sesuai DIAGNOSTIC_PLAN (5 mudah, 3 sedang, 2 sulit), diacak.

    Mechanism: untuk tiap tingkat, soal bertanda is_diagnostic dikumpulkan (soal
    fakultas pengguna diutamakan, lalu soal umum). Bila stok lebih banyak dari
    kuota, kandidat diambil acak dari kelompok yang sama prioritasnya. Lalu urutan
    10 soal dan urutan opsi tiap soal dikocok Fisher-Yates (`random.shuffle`).
    Penilaian memakai kode soal & id opsi database, jadi pengacakan tidak
    memengaruhi skor.
    """
    rng = rng or random.Random()
    picked = []
    for level, count in DIAGNOSTIC_PLAN:
        qs = list(
            Question.objects.filter(is_diagnostic=True, difficulty=level)
            .filter(_visible_to(faculty))
            .select_related("source_document", "node")
            .prefetch_related(Prefetch("options", queryset=Option.objects.order_by("order")))
        )
        own = [q for q in qs if q.faculty_id is not None]
        general = [q for q in qs if q.faculty_id is None]
        rng.shuffle(own)
        rng.shuffle(general)
        picked.extend((own + general)[:count])
    rng.shuffle(picked)
    for q in picked:
        q.shuffled_options = list(q.options.all())
        rng.shuffle(q.shuffled_options)
    return picked


def grade_answers(answers):
    """
    Menilai jawaban di server. `answers` = [{"code": "U-D1", "option_id": 12}, ...].
    Item lama {"difficulty": ..., "is_correct": ...} tetap diterima (kompatibilitas).
    """
    codes = [a.get("code") for a in answers if a.get("code")]
    questions = {
        q.code: q for q in Question.objects.filter(code__in=codes).prefetch_related("options")
    }
    results = []
    for ans in answers:
        code = ans.get("code")
        if not code:
            results.append({"code": None, "difficulty": ans.get("difficulty"),
                            "is_correct": bool(ans.get("is_correct"))})
            continue
        q = questions.get(code)
        if not q:
            continue
        correct_opt = next((o for o in q.options.all() if o.is_correct), None)
        chosen = next((o for o in q.options.all() if str(o.id) == str(ans.get("option_id"))), None)
        results.append({
            "code": q.code,
            "difficulty": q.difficulty,
            "difficulty_label": q.get_difficulty_display(),
            "prompt": q.prompt,
            "chosen": chosen.text if chosen else "",
            "correct": correct_opt.text if correct_opt else "",
            "is_correct": chosen is not None and chosen == correct_opt,
            "answer": q.answer,
        })
    return results


def evaluate_diagnostic(faculty, answers):
    """
    Menilai jawaban diagnostik dan menentukan titik mulai skill tree.

    Decision logic (lulus = proporsi benar >= PASS_RATIO tingkat itu):
      - Mudah tidak lulus                → 'weak_foundation'    → mulai PreCalculus (fundamental)
      - Mudah lulus, Sedang/Sulit tidak  → 'ready_for_calculus' → mulai Kalkulus Dasar (jalur standar)
      - Semua tingkat lulus              → 'mastery'            → lanjut ke Kalkulus Tingkat Menengah
    """
    results = grade_answers(answers)

    def summary(level):
        rows = [r for r in results if r["difficulty"] == level]
        correct = sum(r["is_correct"] for r in rows)
        return {"correct": correct, "total": len(rows),
                "passed": bool(rows) and correct / len(rows) >= PASS_RATIO[level]}

    levels = {lvl: summary(lvl) for lvl, _ in DIAGNOSTIC_PLAN}
    nodes = list(
        SkillNode.objects.filter(kind="lesson").filter(_visible_to(faculty))
        .select_related("main_level").order_by("order", "stage_number")
    )
    general = [n for n in nodes if n.faculty_id is None]
    specific = [n for n in nodes if n.faculty_id is not None]

    def slug_at(seq, i):
        return seq[min(i, len(seq) - 1)].slug if seq else None

    def first_of_level(level_slug, fallback):
        node = next((n for n in general if n.main_level and n.main_level.slug == level_slug), None)
        return node.slug if node else fallback

    if not levels["basic"]["passed"]:
        evaluation = "weak_foundation"
        recommended = first_of_level("precalculus", slug_at(general, 0))
        message = "Fondasi aljabar dan fungsi perlu diperkuat. Mulai dari PreCalculus: Sistem Bilangan dan Fungsi."
    elif not (levels["medium"]["passed"] and levels["high"]["passed"]):
        evaluation = "ready_for_calculus"
        recommended = first_of_level("kalkulus-dasar", slug_at(general, 1))
        message = "Fondasi aman. Lanjutkan jalur standar mulai Kalkulus Dasar: Limit dan Kekontinuan."
    else:
        evaluation = "mastery"
        recommended = first_of_level("kalkulus-menengah", slug_at(specific, 0) or slug_at(general, 0))
        fac_name = faculty.short_name if faculty else ""
        message = (f"Penguasaan tinggi! Lanjut ke Kalkulus Tingkat Menengah, lalu jalur Kalkulus Lanjut khusus {fac_name}.")

    return {
        "evaluation": evaluation,
        "evaluation_label": EVALUATION_LABELS[evaluation],
        "recommended_node": recommended,
        "message": message,
        "levels": levels,
        "score": sum(r["is_correct"] for r in results),
        "total": len(results),
        "results": results,
        "xp_awarded": 40,
    }


def apply_diagnostic_to_profile(user, faculty, evaluation):
    """
    Menyimpan hasil diagnostik ke database pengguna.

    Mechanism: UserProfile diperbarui (status, level, rekomendasi, XP), lalu
    UserProgress dibuat untuk setiap node skill tree fakultas: node sebelum
    rekomendasi = 'completed' (dilewati), node rekomendasi = 'active'.
    """
    from django.utils import timezone
    from .models import UserProfile, UserProgress

    profile, _ = UserProfile.objects.get_or_create(user=user)
    recommended = SkillNode.objects.filter(slug=evaluation["recommended_node"]).first()
    profile.faculty = faculty
    profile.diagnostic_completed = True
    profile.diagnostic_level = evaluation["evaluation_label"]
    profile.recommended_node = recommended
    profile.xp += evaluation.get("xp_awarded", 0)
    profile.save()

    nodes = list(
        SkillNode.objects.filter(kind="lesson").filter(_visible_to(faculty)).order_by("order", "stage_number")
    )
    rec_index = next((i for i, n in enumerate(nodes) if recommended and n.pk == recommended.pk), 0)
    for i, node in enumerate(nodes[: rec_index + 1]):
        progress, _ = UserProgress.objects.get_or_create(user=user, node=node)
        if i < rec_index and progress.status != "completed":
            progress.status = "completed"
            progress.completed_at = timezone.now()
            progress.save()
        elif i == rec_index and progress.status == "locked":
            progress.status = "active"
            progress.save()
    return profile


def profile_bootstrap(user):
    """Data profil + progres untuk diinisialisasi ke State JS di halaman beranda."""
    from .models import UserProfile

    profile, _ = UserProfile.objects.get_or_create(user=user)
    records = user.progress_records.select_related("node")
    return {
        "username": user.username,
        "display_name": user.first_name or user.username,
        "faculty": profile.faculty.slug if profile.faculty else None,
        "faculty_name": profile.faculty.name if profile.faculty else "",
        "xp": profile.xp,
        "diagnostic_level": profile.diagnostic_level,
        "completed": [r.node.slug for r in records if r.status == "completed"],
        "active": next((r.node.slug for r in records if r.status == "active"), None),
    }
