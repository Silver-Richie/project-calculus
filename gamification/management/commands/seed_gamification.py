"""
Django management command to seed initial faculties, skill tree nodes,
and calculus questions for Calculus Bridge.
Usage:
    .\\env\\Scripts\\python.exe manage.py seed_gamification
"""

from django.core.management.base import BaseCommand
from gamification.models import Faculty, SkillNode, Question, Option


class Command(BaseCommand):
    help = "Populate initial Calculus Bridge curriculum, faculties, and questions."

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("Seeding Calculus Bridge data..."))

        # 1. Seed Faculties
        faculties_data = [
            {
                "slug": "ft",
                "name": "Fakultas Teknik",
                "short_name": "FT",
                "icon": "⚙️",
                "description": "Menekankan aplikasi fisik, laju perubahan terapan, perhitungan volume benda putar, dan optimasi material.",
                "focus_areas": "Laju Terkait • Optimasi Desain & Struktur • Kalkulus Vektor Dasar"
            },
            {
                "slug": "fasilkom",
                "name": "Fakultas Ilmu Komputer",
                "short_name": "Fasilkom",
                "icon": "💻",
                "description": "Fokus pada logika analitis, turunan numerik, gradien untuk Machine Learning, dan analisis limit kompleksitas algoritma.",
                "focus_areas": "Gradien Descent & AI • Limit Asimtotik (Big-O) • Aproksimasi Deret Taylor"
            },
            {
                "slug": "fmipa",
                "name": "Fakultas Matematika dan Ilmu Pengetahuan Alam",
                "short_name": "FMIPA",
                "icon": "🔬",
                "description": "Mempelajari keketatan matematis formal, definisi limit Epsilon-Delta, teorema nilai rata-rata, dan pembuktian kalkulus.",
                "focus_areas": "Pembuktian Formal (ε - δ) • Teorema Nilai Rata-rata (MVT) • Kekontinuan Seragam"
            }
        ]

        faculty_objs = {}
        for item in faculties_data:
            fac, created = Faculty.objects.update_or_create(
                slug=item["slug"],
                defaults=item
            )
            faculty_objs[item["slug"]] = fac
            status = "Created" if created else "Updated"
            self.stdout.write(f"  [{status}] Faculty: {fac.short_name}")

        # 2. Seed Skill Tree Nodes
        nodes_data = [
            {
                "stage_number": 1,
                "title": "Tahap 1: Precalculus Bridge",
                "slug": "node-precalc",
                "badge_label": "Fondasi Aljabar",
                "subtitle": "Menyegarkan pemfaktoran, pecahan aljabar, dan fungsi sebelum masuk kalkulus.",
                "summary_html": "Ringkasan konsep pemfaktoran aljabar, selisih kuadrat, dan manipulasi pecahan bentuk rasional.",
                "video_title": "Video Modul: Rahasia Aljabar Mahasiswa Baru",
                "video_duration": "08:45",
                "order": 1
            },
            {
                "stage_number": 2,
                "title": "Tahap 2: Limit & Kekontinuan",
                "slug": "node-limit",
                "badge_label": "Konsep Intuitif",
                "subtitle": "Memahami batas pendekatan nilai fungsi saat mendekati titik kritis.",
                "summary_html": "Intuisi limit sepihak, limit bentuk tak tentu 0/0, strategi pemfaktoran dan perkalian sekawan.",
                "video_title": "Video Modul: Intuisi Limit & Garis Singgung",
                "video_duration": "12:10",
                "order": 2
            },
            {
                "stage_number": 3,
                "title": "Tahap 3: Dasar Turunan & Garis Singgung",
                "slug": "node-deriv",
                "badge_label": "Kalkulus 1",
                "subtitle": "Memahami laju perubahan sesaat, kemiringan tangen, dan aturan pangkat.",
                "summary_html": "Definisi limit turunan f'(x) = lim_{h->0} [f(x+h) - f(x)]/h dan aturan turunan dasar.",
                "video_title": "Video Modul: Garis Singgung & Speedometer Kalkulus",
                "video_duration": "14:20",
                "order": 3
            },
            {
                "stage_number": 4,
                "title": "Tahap 4: Aturan Rantai & Implisit",
                "slug": "node-chain",
                "badge_label": "Advanced Chain Rule",
                "subtitle": "Menurunkan fungsi bersarang/komposisi yang sering keluar di ujian.",
                "summary_html": "Metode kupas kulit buah: d/dx[f(g(x))] = f'(g(x)) * g'(x) serta turunan implisit.",
                "video_title": "Video Modul: Trik Menguasai Aturan Rantai",
                "video_duration": "11:15",
                "order": 4
            },
            {
                "stage_number": 5,
                "title": "Tahap 5: Aplikasi Turunan & Optimasi",
                "slug": "node-app",
                "badge_label": "Real-world Engineering",
                "subtitle": "Mencari nilai maksimum, minimum, laju terkait, dan desain efisien.",
                "summary_html": "Titik stasioner, uji turunan pertama dan kedua untuk mencari solusi optimal dalam rekayasa.",
                "video_title": "Video Modul: Optimasi Biaya & Struktur",
                "video_duration": "16:40",
                "order": 5
            }
        ]

        node_objs = {}
        for item in nodes_data:
            node, created = SkillNode.objects.update_or_create(
                slug=item["slug"],
                defaults=item
            )
            node_objs[item["slug"]] = node
            status = "Created" if created else "Updated"
            self.stdout.write(f"  [{status}] SkillNode: {node.title}")

        # 3. Seed Diagnostic Questions
        diag_questions = [
            {
                "faculty": faculty_objs["fasilkom"],
                "is_diagnostic": True,
                "difficulty": "basic",
                "prompt": "Sederhanakan ekspresi aljabar berikut untuk x ≠ 3: (x² - 9) / (x - 3)",
                "explanation": "Pembilang merupakan selisih kuadrat: x² - 9 = (x - 3)(x + 3). Bagi dengan (x - 3) menghasilkan x + 3.",
                "options": [
                    {"text": "x - 3", "is_correct": False},
                    {"text": "x + 3", "is_correct": True},
                    {"text": "3x", "is_correct": False},
                    {"text": "x² + 3", "is_correct": False}
                ]
            },
            {
                "faculty": faculty_objs["fasilkom"],
                "is_diagnostic": True,
                "difficulty": "medium",
                "prompt": "Tentukan nilai dari limit fungsi rasional: lim_{x -> 2} (x² + x - 6) / (x - 2)",
                "explanation": "Substitusi langsung menghasilkan 0/0. Faktorkan pembilang menjadi (x + 3)(x - 2). Coret faktor (x - 2) dan masukkan x = 2: 2 + 3 = 5.",
                "options": [
                    {"text": "0", "is_correct": False},
                    {"text": "5", "is_correct": True},
                    {"text": "4", "is_correct": False},
                    {"text": "Tidak terdefinisi", "is_correct": False}
                ]
            },
            {
                "faculty": faculty_objs["fasilkom"],
                "is_diagnostic": True,
                "difficulty": "high",
                "prompt": "Dalam optimasi Machine Learning, kita butuh turunan fungsi error. Tentukan f'(x) untuk f(x) = (3x² + 1)³",
                "explanation": "Gunakan Aturan Rantai: Misal u = 3x² + 1, u' = 6x. Turunan u³ adalah 3u² · u' = 3(3x² + 1)² · 6x = 18x(3x² + 1)².",
                "options": [
                    {"text": "9(3x² + 1)²", "is_correct": False},
                    {"text": "18x(3x² + 1)²", "is_correct": True},
                    {"text": "6x(3x² + 1)²", "is_correct": False},
                    {"text": "3(6x)²", "is_correct": False}
                ]
            }
        ]

        for q_data in diag_questions:
            options_list = q_data.pop("options")
            q, _ = Question.objects.update_or_create(
                prompt=q_data["prompt"],
                defaults=q_data
            )
            # Create options
            q.options.all().delete()
            for idx, opt in enumerate(options_list):
                Option.objects.create(
                    question=q,
                    text=opt["text"],
                    is_correct=opt["is_correct"],
                    order=idx
                )
            self.stdout.write(f"  [Seeded] Diagnostic Question: {q.prompt[:40]}...")

        self.stdout.write(self.style.SUCCESS("Calculus Bridge seed completed successfully!"))

