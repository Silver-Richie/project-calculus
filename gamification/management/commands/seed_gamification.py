"""
Memuat kurikulum Calculus Bridge dari paket gamification/content ke database.

Usage:
    .\\env\\Scripts\\python.exe manage.py seed_gamification
    .\\env\\Scripts\\python.exe manage.py seed_gamification --keep-stale

Mechanism:
    1. Upsert Faculty dari content/faculties.py.
    2. Untuk setiap berkas sumber (content/m1 … m7), dengan urutan nomor berkas:
       - upsert SourceDocument (kunci: slug),
       - upsert SkillNode (kunci: slug) lalu tulis ulang LessonSection-nya,
       - upsert Question (kunci: code) lalu tulis ulang Option-nya.
    3. Muat kurikulum 4 level utama (content/levels): MainLevel, sub-level (SkillNode),
       Topic + materi, 5 PracticeSession per topik + QuestionTemplate dari registry generator.
       Node lama ditempatkan ke level utama lewat LEGACY_PLACEMENT.
    4. Hapus node & soal lama yang tidak lagi ada di konten (kecuali --keep-stale),
       sehingga database selalu sama dengan berkas konten.
Semua langkah berjalan dalam satu transaksi: jika validasi gagal, tidak ada yang berubah.
"""

from collections import defaultdict

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.db.models import Max

from gamification import content, generators
from gamification.content import levels
from gamification.models import (
    Faculty, SourceDocument, SkillNode, LessonSection, Question, Option,
    MainLevel, Topic, PracticeSession, QuestionTemplate,
)


class Command(BaseCommand):
    help = "Muat ulang kurikulum (materi, soal, pembahasan, grafik interaktif) dari gamification/content."

    def add_arguments(self, parser):
        parser.add_argument(
            "--keep-stale",
            action="store_true",
            help="Jangan hapus node/soal lama yang tidak ada di berkas konten.",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("Memuat kurikulum Calculus Bridge..."))

        faculties = self._seed_faculties()
        node_slugs, question_codes = set(), set()
        self._question_order = defaultdict(int)  # urutan soal per node, sesuai urutan berkas

        for module in content.SOURCES:
            doc = self._seed_document(module.DOCUMENT, faculties)
            for node_data in getattr(module, "NODES", []):
                node_slugs.add(self._seed_node(node_data, doc, faculties).slug)
            for q_data in getattr(module, "QUESTIONS", []):
                question_codes.add(self._seed_question(q_data, doc).code)

        node_slugs |= self._seed_levels()

        if not options["keep_stale"]:
            stale_nodes = SkillNode.objects.exclude(slug__in=node_slugs)
            stale_questions = Question.objects.exclude(code__in=question_codes)
            n_nodes, n_questions = stale_nodes.count(), stale_questions.count()
            stale_questions.delete()
            stale_nodes.delete()
            if n_nodes or n_questions:
                self.stdout.write(f"  [Dihapus] {n_nodes} node lama, {n_questions} soal lama")

        self.stdout.write(self.style.SUCCESS(
            f"Selesai: {len(node_slugs)} node, {LessonSection.objects.count()} bagian materi, "
            f"{len(question_codes)} soal dari {len(content.SOURCES)} berkas."
        ))

    # ── helpers ────────────────────────────────────────────────────────────
    def _seed_faculties(self):
        result = {}
        for item in content.FACULTIES:
            fac, _ = Faculty.objects.update_or_create(slug=item["slug"], defaults=item)
            result[fac.slug] = fac
        self.stdout.write(f"  [OK] {len(result)} fakultas")
        return result

    def _seed_document(self, data, faculties):
        data = dict(data)
        fac_slug = data.pop("faculty", None)
        data["faculty"] = faculties[fac_slug] if fac_slug else None
        doc, _ = SourceDocument.objects.update_or_create(slug=data.pop("slug"), defaults=data)
        self.stdout.write(f"  [Berkas] {doc.filename}")
        return doc

    def _seed_node(self, data, doc, faculties):
        data = dict(data)
        sections = data.pop("sections", [])
        fac_slug = data.pop("faculty", None)
        data["faculty"] = faculties[fac_slug] if fac_slug else None
        data["source_document"] = doc
        node, _ = SkillNode.objects.update_or_create(slug=data.pop("slug"), defaults=data)

        node.sections.all().delete()
        LessonSection.objects.bulk_create([
            LessonSection(
                node=node,
                source_document=doc,
                order=i,
                heading=s["heading"],
                body_html=s.get("body_html", "").strip(),
                graphs=s.get("graphs", []),
            )
            for i, s in enumerate(sections, start=1)
        ])
        self.stdout.write(f"    [Node] {node.slug}: {len(sections)} bagian materi")
        return node

    def _seed_question(self, data, doc):
        data = dict(data)
        code = data.pop("code")
        options = data.pop("options", [])
        node_slug = data.pop("node")

        if sum(1 for _, ok in options if ok) != 1:
            raise CommandError(f"Soal {code} harus punya tepat satu opsi benar.")
        try:
            node = SkillNode.objects.get(slug=node_slug)
        except SkillNode.DoesNotExist:
            raise CommandError(f"Soal {code} menunjuk node '{node_slug}' yang tidak ada.")

        self._question_order[node.slug] += 1
        defaults = {
            "node": node,
            "source_document": doc,
            "faculty": doc.faculty,
            "difficulty": data.pop("difficulty"),
            "is_diagnostic": data.pop("is_diagnostic", False),
            "prompt": data.pop("prompt"),
            "steps": data.pop("steps", []),
            "answer": data.pop("answer", ""),
            "explanation": data.pop("explanation", ""),
            "graphs": data.pop("graphs", []),
            "xp_reward": data.pop("xp_reward", 20),
            "order": self._question_order[node.slug],
        }
        if data:
            raise CommandError(f"Soal {code}: field tidak dikenal {sorted(data)}")

        question, _ = Question.objects.update_or_create(code=code, defaults=defaults)
        question.options.all().delete()
        Option.objects.bulk_create([
            Option(question=question, text=text, is_correct=ok, order=i)
            for i, (text, ok) in enumerate(options)
        ])
        return question

    # ── kurikulum 4 level ──────────────────────────────────────────────────
    def _seed_levels(self):
        """
        Mechanism: level utama di-upsert (kunci slug); setiap sub-level menjadi SkillNode
        dengan order = level.order × 100 + urutan, sehingga skill tree terurut per level.
        Setiap topik mendapat 5 sesi; template sesi diambil otomatis dari registry
        generator (topik + tier), jadi menambah generator baru cukup dengan @register.
        """
        main = {}
        for data in levels.MAIN_LEVELS:
            lvl, _ = MainLevel.objects.update_or_create(slug=data["slug"], defaults={k: v for k, v in data.items() if k != "slug"})
            main[lvl.slug] = lvl
        MainLevel.objects.exclude(slug__in=main).delete()
        for book in levels.BOOKS:
            SourceDocument.objects.update_or_create(slug=book["slug"], defaults={k: v for k, v in book.items() if k != "slug"})

        slugs, topic_slugs = set(), set()
        n_sessions = n_templates = 0
        for module in levels.LEVEL_MODULES:
            lvl = main[module.MAIN_LEVEL["slug"]]
            for i, sub in enumerate(module.SUBLEVELS, start=1):
                node, _ = SkillNode.objects.update_or_create(slug=sub["slug"], defaults={
                    "main_level": lvl, "faculty": None, "source_document": None, "kind": "lesson",
                    "stage_number": lvl.order, "order": lvl.order * 100 + i, "title": sub["title"],
                    "subtitle": sub.get("subtitle", ""), "icon": sub.get("icon", "📘"),
                    "badge_label": sub.get("badge_label", lvl.title), "summary_html": sub.get("summary_html", ""),
                    "is_boss": False,
                })
                node.sections.all().delete()
                slugs.add(node.slug)
                for t_order, t in enumerate(sub["topics"], start=1):
                    topic, _ = Topic.objects.update_or_create(slug=t["slug"], defaults={
                        "node": node, "order": t_order, "title": t["title"], "icon": t.get("icon", "📗"),
                        "summary": t.get("summary", ""), "references": t.get("references", ""),
                    })
                    topic_slugs.add(topic.slug)
                    topic.sections.all().delete()
                    LessonSection.objects.bulk_create([
                        LessonSection(topic=topic, order=k, heading=sec["heading"],
                                      body_html=sec.get("body_html", "").strip(), graphs=sec.get("graphs", []))
                        for k, sec in enumerate(t.get("sections", []), start=1)
                    ])
                    for number, tier, title, ratio, xp in levels.SESSION_PLAN:
                        gens = generators.for_topic(topic.slug, number)
                        if not gens:
                            raise CommandError(f"Topik {topic.slug} sesi {number} tidak punya generator soal.")
                        session, _ = PracticeSession.objects.update_or_create(topic=topic, number=number, defaults={
                            "tier": tier, "title": title, "pass_ratio": ratio, "xp_per_question": xp,
                            "question_count": levels.QUESTIONS_PER_SESSION,
                        })
                        session.templates.exclude(key__in=[g.key for g in gens]).delete()
                        for gen in gens:
                            QuestionTemplate.objects.update_or_create(session=session, key=gen.key, defaults={"weight": gen.weight})
                        n_sessions += 1
                        n_templates += len(gens)
                    PracticeSession.objects.filter(topic=topic).exclude(number__in=[p[0] for p in levels.SESSION_PLAN]).delete()
                self.stdout.write(f"    [Sub-level] {node.slug}: {len(sub['topics'])} topik")
        Topic.objects.exclude(slug__in=topic_slugs).delete()
        self._absorb_legacy()

        # Node lama: pasang ke level utama, urutan relatif dipertahankan.
        for node in SkillNode.objects.filter(kind="lesson").exclude(slug__in=slugs).order_by("order", "stage_number", "id"):
            lvl = main[levels.LEGACY_PLACEMENT.get(node.slug, levels.LEGACY_DEFAULT_LEVEL)]
            node.main_level = lvl
            node.order = lvl.order * 100 + 50 + node.order
            node.save(update_fields=["main_level", "order"])
        self.stdout.write(f"  [OK] {len(main)} level utama, {len(topic_slugs)} topik, {n_sessions} sesi, {n_templates} template soal")
        return slugs

    def _absorb_legacy(self):
        """
        Gabungkan node lama (berkas 1–7) ke topik kurikulum baru.

        Mechanism: tiap modul level boleh mendefinisikan ABSORB_NODES (node lama → sub-level),
        ABSORB_SECTIONS ((node, judul bagian) → topik) dan FIXED_QUESTIONS (kode soal → (topik, sesi)).
        Bagian materi dipindah ke topik (sumber berkas tetap tercatat), soal lama menjadi soal tetap
        yang ikut diundi di sesi itu (atau hanya di Bank Soal bila None), lalu node lama dihapus.
        Karena berkas lama di-seed ulang setiap kali, langkah ini idempoten.
        """
        for module in levels.LEVEL_MODULES:
            for legacy_slug, target_slug in getattr(module, "ABSORB_NODES", {}).items():
                legacy = SkillNode.objects.filter(slug=legacy_slug).first()
                if not legacy:
                    continue
                target = SkillNode.objects.get(slug=target_slug)
                for sec in legacy.sections.order_by("order"):
                    topic_slug = module.ABSORB_SECTIONS.get((legacy_slug, sec.heading))
                    topic = Topic.objects.get(slug=topic_slug) if topic_slug else target.topics.order_by("order").first()
                    sec.order = (topic.sections.aggregate(m=Max("order"))["m"] or 0) + 1
                    sec.node, sec.topic = None, topic
                    sec.save()
                for q in legacy.questions.all():
                    spec = module.FIXED_QUESTIONS.get(q.code)
                    if spec:
                        q.session = PracticeSession.objects.get(topic__slug=spec[0], number=spec[1])
                        q.node = q.session.topic.node
                    else:
                        q.session, q.node = None, target
                    q.save(update_fields=["session", "node"])
                legacy.delete()
                self.stdout.write(f"    [Gabung] {legacy_slug} → {target_slug}")
