"""
Unit tests for Calculus Bridge Gamification models, content seed, and API endpoints.
"""

import io
import json

from django.contrib.auth.models import User
from django.core.management import call_command
from django.test import TestCase, Client

from . import content
from .models import (
    Faculty, SourceDocument, SkillNode, LessonSection, Question, UserProfile, UserProgress,
)


class GamificationModelTests(TestCase):
    def setUp(self):
        self.faculty = Faculty.objects.create(
            slug="fasilkom",
            name="Fakultas Ilmu Komputer",
            short_name="Fasilkom",
            icon="💻",
            description="Fokus Komputasi",
            focus_areas="Gradien Machine Learning"
        )
        self.node = SkillNode.objects.create(
            stage_number=1,
            title="Tahap 1: Fungsi dan Limit",
            slug="umum-limit",
            badge_label="Materi Umum",
            subtitle="Limit",
            order=1
        )
        self.user = User.objects.create_user(username="mahasiswa_baru", password="password123")
        self.profile = UserProfile.objects.create(user=self.user, faculty=self.faculty, xp=50, hearts=5)

    def test_faculty_str(self):
        self.assertEqual(str(self.faculty), "Fasilkom - Fakultas Ilmu Komputer")

    def test_skill_node_str(self):
        self.assertEqual(str(self.node), "Stage 1: Tahap 1: Fungsi dan Limit")

    def test_question_str_uses_code(self):
        q = Question.objects.create(code="U-D1", node=self.node, difficulty="basic", prompt="Soal")
        self.assertEqual(str(q), "U-D1 (Dasar (Basic))")

    def test_user_profile_deduct_heart(self):
        self.profile.deduct_heart()
        self.assertEqual(self.profile.hearts, 4)

    def test_user_profile_add_xp(self):
        self.profile.add_xp(30)
        self.assertEqual(self.profile.xp, 80)

    def test_user_progress_completion(self):
        progress = UserProgress.objects.create(user=self.user, node=self.node, status='active')
        progress.mark_completed(earned_score=100)
        self.assertEqual(progress.status, 'completed')
        self.assertIsNotNone(progress.completed_at)


class ContentSeedTests(TestCase):
    """Memastikan berkas konten termuat lengkap dan terpisah per berkas/fakultas."""

    @classmethod
    def setUpTestData(cls):
        call_command("seed_gamification", stdout=io.StringIO())

    def test_one_document_per_source_file(self):
        self.assertEqual(SourceDocument.objects.count(), 7)
        self.assertEqual(
            list(SourceDocument.objects.values_list("filename", flat=True)),
            [m.DOCUMENT["filename"] for m in content.SOURCES],
        )

    def test_question_counts_per_file(self):
        counts = {d.slug: d.questions.count() for d in SourceDocument.objects.all()}
        self.assertEqual(counts["soal-dasar-medium"], 13)
        self.assertEqual(counts["soal-ft"], 9)
        self.assertEqual(counts["soal-fmipa"], 9)
        self.assertEqual(counts["soal-fasilkom"], 9)

    def test_faculty_questions_live_in_faculty_nodes(self):
        for q in Question.objects.exclude(faculty=None).select_related("node", "faculty"):
            self.assertEqual(q.node.faculty_id, q.faculty_id, q.code)
        for q in Question.objects.filter(faculty=None).select_related("node"):
            self.assertIsNone(q.node.faculty_id, q.code)

    def test_every_question_has_one_correct_option_and_pembahasan(self):
        for q in Question.objects.prefetch_related("options"):
            self.assertEqual(sum(o.is_correct for o in q.options.all()), 1, q.code)
            self.assertTrue(q.steps, q.code)
            self.assertTrue(q.answer, q.code)
            self.assertTrue(q.graphs, f"{q.code} belum punya grafik slider")

    def test_graph_specs_have_valid_params(self):
        specs = [g for q in Question.objects.all() for g in q.graphs]
        specs += [g for s in LessonSection.objects.all() for g in s.graphs]
        for spec in specs:
            self.assertIn(spec.get("type"), ("2d", "3d"))
            for p in spec.get("params", []):
                self.assertLessEqual(p["min"], p["value"], spec.get("title"))
                self.assertLessEqual(p["value"], p["max"], spec.get("title"))

    def test_reseed_is_idempotent(self):
        before = (SkillNode.objects.count(), LessonSection.objects.count(), Question.objects.count())
        call_command("seed_gamification", stdout=io.StringIO())
        after = (SkillNode.objects.count(), LessonSection.objects.count(), Question.objects.count())
        self.assertEqual(before, after)


class GamificationApiTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("seed_gamification", stdout=io.StringIO())

    def setUp(self):
        self.client = Client()

    def _curriculum(self, faculty):
        response = self.client.get(f'/api/curriculum/?faculty={faculty}')
        self.assertEqual(response.status_code, 200)
        return json.loads(response.content)

    def test_curriculum_tree_is_general_plus_own_faculty(self):
        data = self._curriculum("ft")
        self.assertEqual(data["status"], "success")
        self.assertEqual(len(data["faculties"]), 3)
        slugs = [n["slug"] for n in data["tree"]]
        self.assertEqual(slugs[:5], ["umum-limit", "umum-turunan", "umum-integral", "umum-deret", "umum-dua-variabel"])
        self.assertEqual(slugs[5:], ["ft-konsep", "ft-terapan", "ft-ujian"])

    def test_curriculum_hides_other_faculty_files(self):
        files = [d["filename"] for d in self._curriculum("fmipa")["documents"]]
        self.assertIn("5_Soal_Pembahasan_FMIPA.pdf", files)
        self.assertNotIn("4_Soal_Pembahasan_FT.pdf", files)
        self.assertNotIn("6_Soal_Pembahasan_Fasilkom.pdf", files)

    def test_diagnostic_questions_hide_answers(self):
        data = json.loads(self.client.get('/api/diagnostic/?faculty=fasilkom').content)
        codes = [q["code"] for q in data["questions"]]
        self.assertEqual(len(codes), 10)
        levels = [q["difficulty"] for q in data["questions"]]
        self.assertEqual((levels.count("basic"), levels.count("medium"), levels.count("high")), (5, 3, 2))
        self.assertTrue(all(c.startswith(("FK-", "U-")) for c in codes))
        for q in data["questions"]:
            self.assertNotIn("steps", q)
            for o in q["options"]:
                self.assertNotIn("is_correct", o)

    def _submit(self, faculty, correct_map):
        answers = []
        for code, correct in correct_map.items():
            q = Question.objects.get(code=code)
            opt = q.options.get(is_correct=correct) if correct else q.options.filter(is_correct=False).first()
            answers.append({"code": code, "option_id": opt.id})
        response = self.client.post(
            '/api/diagnostic/submit/',
            data=json.dumps({"faculty": faculty, "answers": answers}),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 200)
        return json.loads(response.content)

    def test_diagnostic_weak_foundation(self):
        data = self._submit("ft", {"U-D1": False, "FT-S1": True, "FT-H3": False})
        self.assertEqual(data["evaluation"], "weak_foundation")
        self.assertEqual(data["recommended_node"], "umum-limit")

    def test_diagnostic_ready_for_calculus(self):
        data = self._submit("ft", {"U-D1": True, "FT-S1": True, "FT-H3": False})
        self.assertEqual(data["evaluation"], "ready_for_calculus")
        self.assertEqual(data["recommended_node"], "umum-turunan")

    def test_diagnostic_mastery_goes_to_faculty_track(self):
        data = self._submit("fmipa", {"U-D1": True, "FM-S1": True, "FM-H3": True})
        self.assertEqual(data["evaluation"], "mastery")
        self.assertEqual(data["recommended_node"], "fmipa-konsep")

    def test_diagnostic_rejects_bad_payload(self):
        response = self.client.post('/api/diagnostic/submit/', data="{}", content_type='application/json')
        self.assertEqual(response.status_code, 400)


class AuthOnboardingTests(TestCase):
    """Alur: splash → login/daftar → pilih fakultas → tawaran tes → tes 10 soal → hasil → beranda."""

    @classmethod
    def setUpTestData(cls):
        call_command("seed_gamification", stdout=io.StringIO())

    def _register(self, username="budi", email="budi@mail.com"):
        return self.client.post("/auth/daftar/", {
            "reg-first_name": "Budi Santoso",
            "reg-username": username,
            "reg-email": email,
            "reg-password1": "KalkulusAsik123",
            "reg-password2": "KalkulusAsik123",
        })

    def test_home_requires_login(self):
        self.assertRedirects(self.client.get("/"), "/auth/")

    def test_splash_links_to_login(self):
        response = self.client.get("/auth/")
        self.assertContains(response, "Archie")
        self.assertContains(response, 'href="/auth/masuk/"')

    def test_register_saves_user_and_goes_to_faculty(self):
        response = self._register()
        self.assertRedirects(response, "/auth/fakultas/")
        user = User.objects.get(username="budi")
        self.assertEqual(user.email, "budi@mail.com")
        self.assertTrue(UserProfile.objects.filter(user=user, faculty=None).exists())
        # Belum pilih fakultas → beranda mengarahkan ke pilih fakultas
        self.assertRedirects(self.client.get("/"), "/auth/fakultas/")

    def test_register_rejects_duplicate_email(self):
        self._register()
        self.client.post("/auth/keluar/")
        response = self._register(username="budi2")
        self.assertEqual(response.status_code, 400)
        self.assertContains(response, "Email ini sudah terdaftar", status_code=400)

    def test_login_existing_user_goes_home(self):
        self._register()
        self.client.post("/auth/fakultas/", {"faculty": "ft"})
        self.client.post("/auth/keluar/")
        response = self.client.post("/auth/masuk/", {"login-username": "budi@mail.com", "login-password": "KalkulusAsik123"})
        self.assertRedirects(response, "/")
        home = self.client.get("/")
        self.assertContains(home, 'id="server-profile"')
        self.assertContains(home, "Budi Santoso")

    def test_login_wrong_password(self):
        self._register()
        self.client.post("/auth/keluar/")
        response = self.client.post("/auth/masuk/", {"login-username": "budi", "login-password": "salah"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "kata sandi salah")

    def test_faculty_then_offer_then_skip(self):
        self._register()
        self.assertRedirects(self.client.post("/auth/fakultas/", {"faculty": "fmipa"}), "/auth/tes-awal/")
        offer = self.client.get("/auth/tes-awal/")
        self.assertContains(offer, 'href="/auth/tes-awal/mulai/"')
        self.assertContains(offer, 'href="/"')
        self.assertEqual(self.client.get("/").status_code, 200)

    def test_diagnostic_test_has_10_questions_for_faculty(self):
        self._register()
        self.client.post("/auth/fakultas/", {"faculty": "ft"})
        response = self.client.get("/auth/tes-awal/mulai/")
        questions = response.context["questions"]
        self.assertEqual(len(questions), 10)
        self.assertEqual([q.difficulty for q in questions].count("basic"), 5)
        self.assertEqual([q.difficulty for q in questions].count("medium"), 3)
        self.assertEqual([q.difficulty for q in questions].count("high"), 2)
        self.assertTrue(all(q.faculty is None or q.faculty.slug == "ft" for q in questions))

    def test_diagnostic_all_correct_saves_mastery(self):
        self._register()
        self.client.post("/auth/fakultas/", {"faculty": "fmipa"})
        questions = self.client.get("/auth/tes-awal/mulai/").context["questions"]
        data = {f"q_{q.code}": q.options.get(is_correct=True).id for q in questions}
        response = self.client.post("/auth/tes-awal/mulai/", data)
        self.assertRedirects(response, "/auth/tes-awal/hasil/")

        user = User.objects.get(username="budi")
        profile = user.gamification_profile
        self.assertTrue(profile.diagnostic_completed)
        self.assertEqual(profile.recommended_node.slug, "fmipa-konsep")
        self.assertEqual(UserProgress.objects.get(user=user, node__slug="fmipa-konsep").status, "active")
        self.assertEqual(UserProgress.objects.get(user=user, node__slug="umum-limit").status, "completed")

        result = self.client.get("/auth/tes-awal/hasil/")
        self.assertContains(result, "10<small>/10</small>")

    def test_diagnostic_weak_basics_starts_at_stage_one(self):
        self._register()
        self.client.post("/auth/fakultas/", {"faculty": "fasilkom"})
        questions = self.client.get("/auth/tes-awal/mulai/").context["questions"]
        data = {f"q_{q.code}": q.options.filter(is_correct=False).first().id for q in questions}
        self.client.post("/auth/tes-awal/mulai/", data)
        profile = User.objects.get(username="budi").gamification_profile
        self.assertEqual(profile.recommended_node.slug, "umum-limit")

    def test_diagnostic_incomplete_answers_rejected(self):
        self._register()
        self.client.post("/auth/fakultas/", {"faculty": "ft"})
        response = self.client.post("/auth/tes-awal/mulai/", {})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Jawab semua soal")

    def test_set_faculty_api_requires_login_and_saves(self):
        self.assertEqual(self.client.post("/api/profile/faculty/", "{}", content_type="application/json").status_code, 302)
        self._register()
        self.client.post("/auth/fakultas/", {"faculty": "ft"})
        r = self.client.post("/api/profile/faculty/", json.dumps({"faculty": "fasilkom"}), content_type="application/json")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(User.objects.get(username="budi").gamification_profile.faculty.slug, "fasilkom")
