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
    3. Hapus node & soal lama yang tidak lagi ada di konten (kecuali --keep-stale),
       sehingga database selalu sama dengan berkas konten.
Semua langkah berjalan dalam satu transaksi: jika validasi gagal, tidak ada yang berubah.
"""

from collections import defaultdict

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from gamification import content
from gamification.models import (
    Faculty, SourceDocument, SkillNode, LessonSection, Question, Option,
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
