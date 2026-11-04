"""
Calculus Bridge — logika bisnis kurikulum & diagnostik.

Views hanya memanggil fungsi di sini lalu mengembalikan JSON, sehingga logika
pemilihan jalur belajar dan evaluasi diagnostik mudah diuji secara terpisah.
"""

from django.db.models import F, Prefetch, Q

from .models import Faculty, SourceDocument, SkillNode, LessonSection, Question, Option

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

    Mechanism: Tahap 1–5 (materi umum, faculty = NULL) dipakai semua fakultas,
    lalu Tahap 6–8 hanya milik fakultas yang dipilih. Node bertipe 'reference'
    (lampiran) tidak masuk skill tree.
    """
    return (
        SkillNode.objects.filter(kind="lesson")
        .filter(_visible_to(faculty))
        .select_related("source_document", "faculty")
        .prefetch_related(
            Prefetch("sections", queryset=LessonSection.objects.order_by("order")),
            Prefetch(
                "questions",
                queryset=Question.objects.select_related("source_document")
                .prefetch_related(Prefetch("options", queryset=Option.objects.order_by("order")))
                .order_by("order", "id"),
            ),
        )
        .order_by("order", "stage_number")
    )


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
            for o in q.options.all()
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
    return data


def build_curriculum(faculty):
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

    return {
        "faculty": faculty.slug if faculty else None,
        "tree": [serialize_node(n) for n in nodes],
        "documents": documents,
        "references": [serialize_node(r) | {"questions": []} for r in references],
    }


# ── Diagnostik ────────────────────────────────────────────────────────────
def diagnostic_questions(faculty):
    """
    Satu soal per tingkat (Dasar → Menengah → Tinggi).

    Mechanism: soal Dasar diambil dari soal umum (berlaku semua fakultas);
    soal Menengah & Tinggi diambil dari bank soal fakultas yang dipilih,
    sehingga diagnostik menguji konteks fakultas pengguna.
    """
    picked = []
    for level in ("basic", "medium", "high"):
        qs = (
            Question.objects.filter(is_diagnostic=True, difficulty=level)
            .filter(_visible_to(faculty))
            .select_related("source_document")
            .prefetch_related(Prefetch("options", queryset=Option.objects.order_by("order")))
            .order_by(F("faculty_id").desc(nulls_last=True), "order")  # utamakan soal milik fakultas
        )
        q = qs.first()
        if q:
            picked.append(q)
    return picked


def evaluate_diagnostic(faculty, answers):
    """
    Menilai jawaban diagnostik dan menentukan titik mulai skill tree.

    `answers` = [{"code": "U-D1", "option_id": 12}, ...]. Penilaian dilakukan
    di server (kunci jawaban tidak dikirim ke browser).
    Untuk kompatibilitas lama, item {"difficulty": ..., "is_correct": ...} juga diterima.

    Decision logic:
      - Dasar salah                → 'weak_foundation'   → mulai Tahap 1 (fundamental)
      - Dasar benar, ada yang salah → 'ready_for_calculus' → mulai Tahap 2 (jalur standar)
      - Semua benar                → 'mastery'           → langsung ke tahap khusus fakultas
    """
    results = []
    for ans in answers:
        code = ans.get("code")
        if code:
            q = Question.objects.filter(code=code).prefetch_related("options").first()
            if not q:
                continue
            correct_opt = next((o for o in q.options.all() if o.is_correct), None)
            is_correct = correct_opt is not None and str(correct_opt.id) == str(ans.get("option_id"))
            results.append({
                "code": q.code,
                "difficulty": q.difficulty,
                "difficulty_label": q.get_difficulty_display(),
                "is_correct": is_correct,
                "answer": q.answer,
            })
        else:
            results.append({
                "code": None,
                "difficulty": ans.get("difficulty"),
                "is_correct": bool(ans.get("is_correct")),
            })

    def level_ok(level):
        level_results = [r for r in results if r["difficulty"] == level]
        return bool(level_results) and all(r["is_correct"] for r in level_results)

    basic_ok, medium_ok, high_ok = level_ok("basic"), level_ok("medium"), level_ok("high")
    nodes = list(
        SkillNode.objects.filter(kind="lesson").filter(_visible_to(faculty)).order_by("order", "stage_number")
    )
    general = [n for n in nodes if n.faculty_id is None]
    specific = [n for n in nodes if n.faculty_id is not None]

    def slug_at(seq, i):
        return seq[min(i, len(seq) - 1)].slug if seq else None

    if not basic_ok:
        evaluation = "weak_foundation"
        recommended = slug_at(general, 0)
        message = "Fondasi limit dan aljabar perlu diperkuat. Mulai dari Tahap 1: Fungsi dan Limit."
    elif not (medium_ok and high_ok):
        evaluation = "ready_for_calculus"
        recommended = slug_at(general, 1)
        message = "Fondasi aman. Lanjutkan jalur standar mulai Tahap 2: Turunan dan Aplikasinya."
    else:
        evaluation = "mastery"
        recommended = slug_at(specific, 0) or slug_at(general, 0)
        fac_name = faculty.short_name if faculty else ""
        message = f"Penguasaan tinggi! Langsung ke materi khusus {fac_name}."

    return {
        "evaluation": evaluation,
        "recommended_node": recommended,
        "message": message,
        "results": results,
        "xp_awarded": 40,
    }
