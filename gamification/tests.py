"""
Unit tests for Calculus Bridge Gamification models, content seed, and API endpoints.
"""

import io
import json
from dataclasses import replace
from datetime import timedelta

from channels.db import database_sync_to_async
from channels.routing import URLRouter
from channels.testing import WebsocketCommunicator
from django.contrib.auth.models import User
from django.core.management import call_command
from django.test import TestCase, TransactionTestCase, Client
from django.utils import timezone

from . import consumers, content, duel, generators, leveling, ranking
from .content import bank
from .routing import websocket_urlpatterns
from .models import (
    DuelAnswer, DuelMatch, DuelQueue, Faculty, SourceDocument, SkillNode, LessonSection, PlayerRank, Question, Topic,
    UserProfile, UserProgress, rank_of,
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
        pdfs = SourceDocument.objects.exclude(category="buku").exclude(slug__in=[d["slug"] for d in bank.DOCUMENTS])
        self.assertEqual(pdfs.count(), 7)
        self.assertEqual(
            list(pdfs.values_list("filename", flat=True)),
            [m.DOCUMENT["filename"] for m in content.SOURCES],
        )
        # tiga buku rujukan kurikulum 4 level
        self.assertEqual(SourceDocument.objects.filter(category="buku").count(), 3)

    def test_question_counts_per_file(self):
        counts = {d.slug: d.questions.count() for d in SourceDocument.objects.all()}
        self.assertEqual(counts["soal-dasar-medium"], 13)
        self.assertEqual(counts["soal-ft"], 9)
        self.assertEqual(counts["soal-fmipa"], 9)
        self.assertEqual(counts["soal-fasilkom"], 9)

    def test_faculty_questions_live_in_matching_sessions(self):
        """Soal fakultas menjadi soal tetap sesi di topik umum atau topik jalur fakultasnya sendiri."""
        for q in Question.objects.exclude(faculty=None).select_related("session__topic__node", "faculty"):
            self.assertIsNotNone(q.session, q.code)
            self.assertIn(q.session.topic.node.faculty_id, (None, q.faculty_id), q.code)

    def test_every_question_has_one_correct_option_and_pembahasan(self):
        for q in Question.objects.prefetch_related("options"):
            self.assertEqual(sum(o.is_correct for o in q.options.all()), 1, q.code)
            self.assertTrue(q.steps, q.code)
            self.assertTrue(q.answer, q.code)
            if not q.code.startswith(("WH-", "ST-", "CB-")):   # bank soal (content/bank) belum memakai grafik
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
        self.assertEqual(slugs[0], "pre-sistem-bilangan-fungsi")   # Level Utama 1: PreCalculus
        self.assertEqual(slugs[1:5], ["kd-limit-kekontinuan", "kd-turunan", "kd-aplikasi-turunan", "kd-integral"])  # Level 2
        self.assertEqual(slugs[5:10], ["km-teknik-integral", "km-aplikasi-integral", "km-pd-orde-satu", "km-kerucut-kutub", "km-barisan-deret"])  # Level 3
        self.assertEqual(slugs[10:], ["kl-ft-peubah-banyak", "kl-ft-turunan-parsial", "kl-ft-integral-lipat",
                                      "kl-ft-kalkulus-vektor", "kl-ft-fungsi-khusus"])                                   # Level 4 jalur FT
        self.assertEqual([m["slug"] for m in data["main_levels"]],
                         ["precalculus", "kalkulus-dasar", "kalkulus-menengah", "kalkulus-lanjut"])

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
        self.assertTrue(all(not c.startswith(("FT-", "FM-")) for c in codes))   # tidak ada soal prodi lain
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
        self.assertEqual(data["recommended_node"], "pre-sistem-bilangan-fungsi")

    def test_diagnostic_ready_for_calculus(self):
        data = self._submit("ft", {"U-D1": True, "FT-S1": True, "FT-H3": False})
        self.assertEqual(data["evaluation"], "ready_for_calculus")
        self.assertEqual(data["recommended_node"], "kd-limit-kekontinuan")     # awal Kalkulus Dasar

    def test_diagnostic_mastery_goes_to_faculty_track(self):
        data = self._submit("fmipa", {"U-D1": True, "FM-S1": True, "FM-H3": True})
        self.assertEqual(data["evaluation"], "mastery")
        self.assertEqual(data["recommended_node"], "km-teknik-integral")

    def test_diagnostic_rejects_bad_payload(self):
        response = self.client.post('/api/diagnostic/submit/', data="{}", content_type='application/json')
        self.assertEqual(response.status_code, 400)


class AuthOnboardingTests(TestCase):
    """Alur: homepage → login/daftar → pilih fakultas → tawaran tes → tes 10 soal → hasil → beranda."""

    @classmethod
    def setUpTestData(cls):
        call_command("seed_gamification", stdout=io.StringIO())

    def _register(self, username="budi"):
        return self.client.post("/auth/daftar/", {
            "reg-username": username,
            "reg-password1": "KalkulusAsik123",
            "reg-password2": "KalkulusAsik123",
        })

    def test_guest_sees_public_homepage(self):
        response = self.client.get("/")
        self.assertTemplateUsed(response, "home/homepage.html")
        self.assertContains(response, 'href="/auth/masuk/"')                 # Masuk (kanan atas)
        self.assertContains(response, 'href="/auth/masuk/?tab=daftar"')      # Daftar
        self.assertContains(response, 'id="trial-root"')                      # kuis coba
        self.assertContains(response, 'data-video="tour"')                    # video pengenalan
        self.assertContains(response, '<meta name="description"')
        self.assertContains(response, "js/mathfrac.js")                       # pecahan bertumpuk

    def test_onboarding_requires_campus_or_umum(self):
        self._register()
        missing = self.client.post("/auth/fakultas/", {"faculty": "ft"})
        self.assertEqual(missing.status_code, 200)
        self.assertContains(missing, "Tulis nama kampusmu")
        self.assertRedirects(self.client.post("/auth/fakultas/", {"faculty": "ft", "campus": "x", "campus_umum": "1"}),
                             "/auth/tes-awal/")
        self.assertEqual(User.objects.get(username="budi").gamification_profile.campus, "Umum")
        self.client.post("/auth/fakultas/", {"faculty": "ft", "campus": "  Institut   Teknologi Bandung "})
        self.assertEqual(User.objects.get(username="budi").gamification_profile.campus, "Institut Teknologi Bandung")

    def test_old_splash_redirects_to_homepage(self):
        self.assertRedirects(self.client.get("/auth/"), "/")

    def test_login_page_can_open_register_tab(self):
        self.assertEqual(self.client.get("/auth/masuk/?tab=daftar").context["active_tab"], "daftar")
        self.assertEqual(self.client.get("/auth/masuk/").context["active_tab"], "masuk")

    def test_logout_returns_to_homepage(self):
        self._register()
        self.assertRedirects(self.client.post("/auth/keluar/"), "/")

    def test_register_saves_user_and_goes_to_faculty(self):
        response = self._register()
        self.assertRedirects(response, "/auth/fakultas/")
        user = User.objects.get(username="budi")
        self.assertEqual(user.email, "")   # daftar manual tanpa email
        self.assertTrue(UserProfile.objects.filter(user=user, faculty=None).exists())
        # Belum pilih fakultas → beranda mengarahkan ke pilih fakultas
        self.assertRedirects(self.client.get("/"), "/auth/fakultas/")

    def test_register_rejects_mismatched_password(self):
        response = self.client.post("/auth/daftar/", {
            "reg-username": "budi", "reg-password1": "KalkulusAsik123", "reg-password2": "BedaSandi456"})
        self.assertEqual(response.status_code, 400)
        self.assertFalse(User.objects.filter(username="budi").exists())

    def test_register_rejects_duplicate_username(self):
        self._register()
        self.client.post("/auth/keluar/")
        response = self._register()
        self.assertEqual(response.status_code, 400)
        self.assertEqual(User.objects.filter(username="budi").count(), 1)

    def test_login_existing_user_goes_home(self):
        self._register()
        self.client.post("/auth/fakultas/", {"faculty": "ft", "campus": "Universitas Indonesia"})
        self.client.post("/auth/keluar/")
        response = self.client.post("/auth/masuk/", {"login-username": "budi", "login-password": "KalkulusAsik123"})
        self.assertRedirects(response, "/")
        home = self.client.get("/")
        self.assertContains(home, 'id="server-profile"')
        self.assertContains(home, "budi")

    def test_login_wrong_password(self):
        self._register()
        self.client.post("/auth/keluar/")
        response = self.client.post("/auth/masuk/", {"login-username": "budi", "login-password": "salah"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "kata sandi salah")

    def test_faculty_then_offer_then_skip(self):
        self._register()
        self.assertRedirects(self.client.post("/auth/fakultas/", {"faculty": "fmipa", "campus": "Universitas Indonesia"}), "/auth/tes-awal/")
        offer = self.client.get("/auth/tes-awal/")
        self.assertContains(offer, 'href="/auth/tes-awal/mulai/"')
        self.assertContains(offer, 'href="/"')
        self.assertEqual(self.client.get("/").status_code, 200)

    def test_diagnostic_test_has_10_questions_for_faculty(self):
        self._register()
        self.client.post("/auth/fakultas/", {"faculty": "ft", "campus": "Universitas Indonesia"})
        response = self.client.get("/auth/tes-awal/mulai/")
        questions = response.context["questions"]
        self.assertEqual(len(questions), 10)
        self.assertEqual([q.difficulty for q in questions].count("basic"), 5)
        self.assertEqual([q.difficulty for q in questions].count("medium"), 3)
        self.assertEqual([q.difficulty for q in questions].count("high"), 2)
        self.assertTrue(all(q.faculty is None or q.faculty.slug == "ft" for q in questions))

    def test_diagnostic_all_correct_saves_mastery(self):
        self._register()
        self.client.post("/auth/fakultas/", {"faculty": "fmipa", "campus": "Universitas Indonesia"})
        questions = self.client.get("/auth/tes-awal/mulai/").context["questions"]
        data = {f"q_{q.code}": q.options.get(is_correct=True).id for q in questions}
        response = self.client.post("/auth/tes-awal/mulai/", data)
        self.assertRedirects(response, "/auth/tes-awal/hasil/")

        user = User.objects.get(username="budi")
        profile = user.gamification_profile
        self.assertTrue(profile.diagnostic_completed)
        self.assertEqual(profile.xp, 0)                 # XP hanya dari sesi topik, bukan tes awal
        self.assertEqual(profile.campus, "Universitas Indonesia")
        self.assertEqual(profile.recommended_node.slug, "km-teknik-integral")
        self.assertEqual(UserProgress.objects.get(user=user, node__slug="km-teknik-integral").status, "active")
        self.assertEqual(UserProgress.objects.get(user=user, node__slug="kd-limit-kekontinuan").status, "completed")

        result = self.client.get("/auth/tes-awal/hasil/")
        self.assertContains(result, "10<small>/10</small>")

    def test_diagnostic_weak_basics_starts_at_stage_one(self):
        self._register()
        self.client.post("/auth/fakultas/", {"faculty": "fasilkom", "campus": "Universitas Indonesia"})
        questions = self.client.get("/auth/tes-awal/mulai/").context["questions"]
        data = {f"q_{q.code}": q.options.filter(is_correct=False).first().id for q in questions}
        self.client.post("/auth/tes-awal/mulai/", data)
        profile = User.objects.get(username="budi").gamification_profile
        self.assertEqual(profile.recommended_node.slug, "pre-sistem-bilangan-fungsi")

    def test_diagnostic_incomplete_answers_rejected(self):
        self._register()
        self.client.post("/auth/fakultas/", {"faculty": "ft", "campus": "Universitas Indonesia"})
        shown = [q.code for q in self.client.get("/auth/tes-awal/mulai/").context["questions"]]
        response = self.client.post("/auth/tes-awal/mulai/", {})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Jawab semua soal")
        # Soal yang sama ditampilkan ulang, bukan undian baru.
        self.assertEqual([q.code for q in response.context["questions"]], shown)

    def test_diagnostic_post_without_shown_questions_draws_new_set(self):
        self._register()
        self.client.post("/auth/fakultas/", {"faculty": "ft", "campus": "Universitas Indonesia"})
        response = self.client.post("/auth/tes-awal/mulai/", {})
        self.assertContains(response, "Sesi tes kedaluwarsa")
        self.assertEqual(len(response.context["questions"]), 10)

    def test_set_faculty_api_requires_login_and_saves(self):
        self.assertEqual(self.client.post("/api/profile/faculty/", "{}", content_type="application/json").status_code, 302)
        self._register()
        self.client.post("/auth/fakultas/", {"faculty": "ft", "campus": "Universitas Indonesia"})
        r = self.client.post("/api/profile/faculty/", json.dumps({"faculty": "fasilkom"}), content_type="application/json")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(User.objects.get(username="budi").gamification_profile.faculty.slug, "fasilkom")


# ─────────────────────────────────────────────────────────────────────────────
# Kurikulum 4 level: generator soal, struktur level, dan sesi latihan berlapis
# ─────────────────────────────────────────────────────────────────────────────
from . import generators  # noqa: E402
from .content import levels  # noqa: E402
from . import services  # noqa: E402
from .models import MainLevel, Topic, PracticeSession, UserSessionProgress  # noqa: E402


class GeneratorTests(TestCase):
    """Setiap generator, pada setiap tingkat sesinya, harus menghasilkan soal valid & deterministik."""

    SEEDS = range(25)

    def test_every_generator_produces_valid_questions(self):
        for key, gen in generators.REGISTRY.items():
            for tier in gen.tiers:
                for seed in self.SEEDS:
                    with self.subTest(key=key, tier=tier, seed=seed):
                        q = generators.generate(key, seed, tier)
                        self.assertEqual(len(q["options"]), 4)
                        self.assertEqual(sum(o["is_correct"] for o in q["options"]), 1)
                        self.assertEqual(len({o["text"] for o in q["options"]}), 4)
                        self.assertTrue(q["prompt"] and q["steps"])
                        json.dumps(q)

    def test_generation_is_deterministic(self):
        for key, gen in generators.REGISTRY.items():
            self.assertEqual(generators.generate(key, 123, gen.tiers[0]), generators.generate(key, 123, gen.tiers[0]))

    def test_each_topic_has_generators_for_all_five_sessions(self):
        topics = [t["slug"] for m in levels.LEVEL_MODULES for sub in m.SUBLEVELS for t in sub["topics"]]
        self.assertEqual(len(topics), 9 + 20 + 20 + 45)
        for slug in topics:
            for tier in range(1, 6):
                with self.subTest(topic=slug, tier=tier):
                    self.assertGreaterEqual(len(generators.for_topic(slug, tier)), 2)


class CurriculumLevelTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("seed_gamification", stdout=io.StringIO())

    def test_main_levels_and_precalc_structure(self):
        self.assertEqual(MainLevel.objects.count(), 4)
        node = SkillNode.objects.get(slug="pre-sistem-bilangan-fungsi")
        self.assertEqual(node.main_level.slug, "precalculus")
        self.assertEqual(node.topics.count(), 9)
        for topic in node.topics.all():
            self.assertTrue(topic.sections.exists(), topic.slug)
            self.assertEqual(list(topic.sessions.values_list("number", flat=True)), [1, 2, 3, 4, 5])
            for session in topic.sessions.all():
                self.assertTrue(session.templates.exists())

    def test_legacy_nodes_are_placed_in_main_levels(self):
        self.assertFalse(SkillNode.objects.filter(kind="lesson", main_level__isnull=True).exists())
        legacy = ["umum-deret", "umum-dua-variabel", "ft-konsep", "fmipa-terapan", "fasilkom-ujian"]
        self.assertFalse(SkillNode.objects.filter(slug__in=legacy).exists())      # semua diserap ke level 2–4

    def test_legacy_limit_turunan_integral_absorbed_into_level_two(self):
        self.assertFalse(SkillNode.objects.filter(slug__in=["umum-limit", "umum-turunan", "umum-integral"]).exists())
        q = Question.objects.get(code="U-D1")
        self.assertEqual((q.session.topic.slug, q.session.number), ("kd-lim-aljabar", 1))
        self.assertTrue(q.is_diagnostic)
        q4 = Question.objects.get(code="U-S4")   # integral parsial → Level 3
        self.assertEqual((q4.session.topic.slug, q4.session.number), ("km-tek-parsial", 3))
        moved = LessonSection.objects.filter(topic__slug="kd-lim-konsep", source_document__slug="materi-umum")
        self.assertEqual(moved.count(), 1)

    def test_level_four_separate_faculty_tracks(self):
        for fac in ("ft", "fmipa", "fasilkom"):
            nodes = SkillNode.objects.filter(main_level__slug="kalkulus-lanjut", faculty__slug=fac)
            self.assertEqual(nodes.count(), 5, fac)
            for node in nodes:
                self.assertEqual(node.topics.count(), 3)
        # materi lama fakultas pindah ke topik terapan fakultasnya; materi dua variabel disalin ke 3 jalur
        self.assertTrue(LessonSection.objects.filter(topic__slug="kl-fk-gd", heading="Sigmoid dan turunannya").exists())
        for fac in ("ft", "fm", "fk"):
            self.assertTrue(LessonSection.objects.filter(topic__slug=f"kl-{fac}-tp-parsial", heading="Kesalahan yang sering terjadi").exists())
        q = Question.objects.get(code="FT-S1")
        self.assertEqual((q.session.topic.slug, q.faculty.slug), ("kd-apl-laju", "ft"))

    def test_faculty_tracks_hidden_from_other_faculties(self):
        tree = services.build_curriculum(Faculty.objects.get(slug="fasilkom"))["tree"]
        slugs = [n["slug"] for n in tree]
        self.assertIn("kl-fk-turunan-parsial", slugs)
        self.assertNotIn("kl-ft-turunan-parsial", slugs)

    def test_level_three_structure(self):
        nodes = SkillNode.objects.filter(main_level__slug="kalkulus-menengah", kind="lesson")
        self.assertEqual(nodes.count(), 5)
        for node in nodes:
            self.assertEqual(node.topics.count(), 4)
        self.assertTrue(LessonSection.objects.filter(topic__slug="km-der-uji", source_document__slug="materi-umum").exists())

    def test_level_two_structure(self):
        for slug in ["kd-limit-kekontinuan", "kd-turunan", "kd-aplikasi-turunan", "kd-integral"]:
            node = SkillNode.objects.get(slug=slug)
            self.assertEqual(node.main_level.slug, "kalkulus-dasar")
            self.assertEqual(node.topics.count(), 5)

    def test_reseed_is_idempotent(self):
        before = (Topic.objects.count(), PracticeSession.objects.count(), LessonSection.objects.count())
        call_command("seed_gamification", stdout=io.StringIO())
        self.assertEqual(before, (Topic.objects.count(), PracticeSession.objects.count(), LessonSection.objects.count()))


class PracticeSessionApiTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("seed_gamification", stdout=io.StringIO())
        cls.s1 = PracticeSession.objects.get(topic__slug="pre-bilangan-real", number=1)
        cls.s2 = PracticeSession.objects.get(topic__slug="pre-bilangan-real", number=2)

    def setUp(self):
        self.user = User.objects.create_user("sinta", password="rahasia-123")
        self.client = Client()
        self.client.force_login(self.user)

    def _open(self, session, client=None):
        return (client or self.client).get(f"/api/session/{session.id}/")

    def _answers(self, data, correct=True):
        return [{"id": q["id"], "option": next(o["id"] for o in q["options"] if o["is_correct"] == correct)}
                for q in data["questions"]]

    def _submit(self, session, attempt, answers):
        return self.client.post(f"/api/session/{session.id}/submit/",
                                data=json.dumps({"attempt": attempt, "answers": answers}),
                                content_type="application/json")

    def test_session_returns_ten_questions_with_explanations(self):
        data = self._open(self.s1).json()
        self.assertEqual(len(data["questions"]), 10)
        q = data["questions"][0]
        self.assertTrue(q["steps"])
        self.assertEqual(sum(o["is_correct"] for o in q["options"]), 1)

    def test_questions_are_randomised_per_user(self):
        other = User.objects.create_user("tono", password="rahasia-123")
        c2 = Client()
        c2.force_login(other)
        mine = [q["prompt"] for q in self._open(self.s1).json()["questions"]]
        theirs = [q["prompt"] for q in self._open(self.s1, c2).json()["questions"]]
        self.assertNotEqual(mine, theirs)

    def test_reopening_without_submit_keeps_same_questions(self):
        a = self._open(self.s1).json()["questions"]
        b = self._open(self.s1).json()["questions"]
        self.assertEqual([q["id"] for q in a], [q["id"] for q in b])

    def test_session_two_locked_until_session_one_passed(self):
        self.assertEqual(self._open(self.s2).status_code, 403)
        data = self._open(self.s1).json()
        res = self._submit(self.s1, data["attempt"], self._answers(data)).json()
        self.assertTrue(res["passed"])
        self.assertEqual(res["score"], 10)
        self.assertEqual(self._open(self.s2).status_code, 200)

    def test_failed_attempt_and_new_numbers_on_retry(self):
        data = self._open(self.s1).json()
        res = self._submit(self.s1, data["attempt"], self._answers(data, correct=False)).json()
        self.assertFalse(res["passed"])
        self.assertEqual(res["score"], 0)
        retry = self._open(self.s1).json()
        self.assertEqual(retry["attempt"], 1)
        self.assertNotEqual([q["id"] for q in retry["questions"]], [q["id"] for q in data["questions"]])

    def test_xp_only_for_improvement(self):
        data = self._open(self.s1).json()
        first = self._submit(self.s1, data["attempt"], self._answers(data)).json()
        self.assertEqual(first["xp_awarded"], 10 * self.s1.xp_per_question)
        data = self._open(self.s1).json()
        again = self._submit(self.s1, data["attempt"], self._answers(data)).json()
        self.assertEqual(again["xp_awarded"], 0)
        self.assertEqual(UserProfile.objects.get(user=self.user).xp, 10 * self.s1.xp_per_question)

    def test_session_result_reports_level(self):
        data = self._open(self.s1).json()
        res = self._submit(self.s1, data["attempt"], self._answers(data)).json()
        xp = 10 * self.s1.xp_per_question
        self.assertEqual(res["level"]["xp"], xp)
        self.assertEqual(res["level"]["level"], leveling.level_for(xp))
        self.assertEqual(res["leveled_up"], leveling.level_for(xp) > 1)

    def test_stale_attempt_rejected(self):
        data = self._open(self.s1).json()
        self._submit(self.s1, data["attempt"], self._answers(data))
        self.assertEqual(self._submit(self.s1, data["attempt"], self._answers(data)).status_code, 409)

    def test_completing_all_topics_completes_sublevel(self):
        node = SkillNode.objects.get(slug="pre-sistem-bilangan-fungsi")
        for topic in node.topics.all():
            for number in (1, 2, 3):
                session = topic.sessions.get(number=number)
                data = self._open(session).json()
                res = self._submit(session, data["attempt"], self._answers(data)).json()
        self.assertEqual(res["node_completed"], "pre-sistem-bilangan-fungsi")
        self.assertEqual(res["next_node"], "kd-limit-kekontinuan")
        self.assertEqual(UserProgress.objects.get(user=self.user, node=node).status, "completed")
        self.assertEqual(UserProgress.objects.get(user=self.user, node__slug="kd-limit-kekontinuan").status, "active")

    def test_curriculum_includes_session_progress(self):
        data = self._open(self.s1).json()
        self._submit(self.s1, data["attempt"], self._answers(data))
        cur = self.client.get("/api/curriculum/?faculty=ft").json()
        self.assertTrue(cur["session_progress"][str(self.s1.id)]["passed"])
        node = cur["tree"][0]
        self.assertEqual(len(node["topics"]), 9)
        self.assertEqual(len(node["topics"][0]["sessions"]), 5)

    def test_topics_unlock_in_order(self):
        topic2 = PracticeSession.objects.get(topic__slug="pre-pertidaksamaan", number=1)
        self.assertEqual(self._open(topic2).status_code, 403)
        for number in (1, 2, 3):
            session = PracticeSession.objects.get(topic__slug="pre-bilangan-real", number=number)
            data = self._open(session).json()
            self._submit(session, data["attempt"], self._answers(data))
        self.assertEqual(self._open(topic2).status_code, 200)

    def test_session_api_requires_login(self):
        self.assertEqual(Client().get(f"/api/session/{self.s1.id}/").status_code, 302)

    def test_legacy_node_completion_saved(self):
        res = self.client.post("/api/progress/node/", data=json.dumps({"slug": "kd-turunan"}), content_type="application/json")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(UserProgress.objects.get(user=self.user, node__slug="kd-turunan").status, "completed")


class FacultyFixedQuestionTests(TestCase):
    """Soal tetap milik fakultas (mis. FT-S1) hanya diundi untuk user fakultas itu."""

    @classmethod
    def setUpTestData(cls):
        call_command("seed_gamification", stdout=io.StringIO())

    def _codes(self, faculty_slug):
        from .sessions import _pool
        session = PracticeSession.objects.get(topic__slug="kd-apl-laju", number=2)
        fac = Faculty.objects.get(slug=faculty_slug)
        return {key for kind, key, _ in _pool(session, fac.id) if kind == "q"}

    def test_ft_question_only_for_ft(self):
        self.assertIn("FT-S1", self._codes("ft"))
        self.assertNotIn("FT-S1", self._codes("fasilkom"))


import random  # noqa: E402

from . import sessions  # noqa: E402
from .models import Faculty, Question  # noqa: E402


class ShuffleTests(TestCase):
    """Pengacakan soal: diagnostik & opsi soal PDF bervariasi, tetapi penilaian tetap benar."""

    @classmethod
    def setUpTestData(cls):
        call_command("seed_gamification", stdout=io.StringIO())
        cls.faculty = Faculty.objects.get(slug="ft")
        cls.user = User.objects.create_user("acak", password="x")

    def test_diagnostic_keeps_plan_but_varies_questions(self):
        """Komposisi 5/3/2 tetap, tetapi isi dan urutan soal berganti antar-percobaan."""
        sets, orders = set(), set()
        for s in range(20):
            qs = services.diagnostic_questions(self.faculty, random.Random(s))
            counts = {lvl: sum(q.difficulty == lvl for q in qs) for lvl, _ in services.DIAGNOSTIC_PLAN}
            self.assertEqual(counts, dict(services.DIAGNOSTIC_PLAN))
            self.assertEqual(len({q.code for q in qs}), len(qs))      # tidak ada soal ganda
            self.assertTrue(any(q.faculty_id == self.faculty.id for q in qs))  # konteks prodi tetap ada
            sets.add(frozenset(q.code for q in qs))
            orders.add(tuple(q.code for q in qs))
        self.assertGreater(len(sets), 10)
        self.assertGreater(len(orders), 10)

    def test_diagnostic_grading_unaffected_by_shuffle(self):
        qs = services.diagnostic_questions(self.faculty, random.Random(7))
        answers = [{"code": q.code, "option_id": next(o.id for o in q.shuffled_options if o.is_correct)} for q in qs]
        result = services.evaluate_diagnostic(self.faculty, answers)
        self.assertEqual(result["score"], len(qs))

    def test_fixed_question_options_shuffled_and_regradable(self):
        q = Question.objects.filter(session__isnull=False).first()
        correct_positions = set()
        for seed in range(30):
            a = sessions._fixed_question_payload(q, seed)
            b = sessions._fixed_question_payload(q, seed)
            self.assertEqual(a["options"], b["options"])          # seed sama → urutan sama (penilaian aman)
            correct_positions.add(next(o["id"] for o in a["options"] if o["is_correct"]))
        self.assertGreater(len(correct_positions), 1)              # jawaban benar tidak selalu di posisi yang sama

    def test_session_attempts_give_different_questions(self):
        session = PracticeSession.objects.filter(number=1).order_by("id").first()
        first = [q["id"] for q in sessions.build_quiz(session, self.user.id, 0)]
        second = [q["id"] for q in sessions.build_quiz(session, self.user.id, 1)]
        self.assertEqual(first, [q["id"] for q in sessions.build_quiz(session, self.user.id, 0)])
        self.assertNotEqual(first, second)

    def test_session_pool_is_varied(self):
        """Setiap percobaan memuat ≥6 jenis soal, termasuk sesi topik pertama (tanpa topik sebelumnya)."""
        for slug in ("pre-bilangan-real", "kd-lim-konsep"):
            for session in PracticeSession.objects.filter(topic__slug=slug):
                for attempt in range(3):
                    quiz = sessions.build_quiz(session, self.user.id, attempt)
                    self.assertEqual(len(quiz), session.question_count)
                    self.assertGreaterEqual(len({q["id"].split(":")[1] for q in quiz}), 6)

    def test_borrowed_generators_are_graded_consistently(self):
        """Soal pinjaman (tingkat lain) dibangun ulang sama persis saat penilaian."""
        session = PracticeSession.objects.get(topic__slug="pre-bilangan-real", number=1)
        a = sessions.build_quiz(session, self.user.id, 5)
        b = sessions.build_quiz(session, self.user.id, 5)
        self.assertEqual([(q["id"], q["options"]) for q in a], [(q["id"], q["options"]) for q in b])



class BookBankTests(TestCase):
    """Bank soal buku referensi (content/bank) termuat dan terpasang ke sesi yang benar."""

    @classmethod
    def setUpTestData(cls):
        call_command("seed_gamification", stdout=io.StringIO())

    def test_all_bank_questions_seeded_to_matching_session(self):
        codes = [d["code"] for d in bank.QUESTIONS]
        self.assertEqual(len(codes), len(set(codes)))
        qs = {q.code: q for q in Question.objects.filter(code__in=codes).select_related("session__topic", "node")}
        self.assertEqual(len(qs), len(codes))
        for d in bank.QUESTIONS:
            q = qs[d["code"]]
            self.assertEqual(q.session.topic.slug, d["topic"])
            self.assertEqual(q.session.number, bank.TIER_OF[d["difficulty"]])
            self.assertEqual(q.node_id, q.session.topic.node_id)
            self.assertEqual(q.options.filter(is_correct=True).count(), 1)
            self.assertEqual(q.options.count(), 4)

    def test_every_bank_difficulty_has_diagnostic_questions(self):
        for level, count in services.DIAGNOSTIC_PLAN:
            n = sum(1 for d in bank.QUESTIONS if d["is_diagnostic"] and d["difficulty"] == level)
            self.assertGreaterEqual(n, count, level)

    def test_bank_questions_appear_in_sessions(self):
        """Soal buku muncul di sesi latihan (lewat soal tetap sesi maupun bank tambahan sub-level)."""
        user = User.objects.create_user("bank", password="x")
        seen = set()
        for session in PracticeSession.objects.filter(topic__slug="kd-tur-rantai"):
            for attempt in range(10):
                seen |= {q["id"] for q in sessions.build_quiz(session, user.id, attempt) if q["id"].startswith("q:WH-")}
        self.assertGreater(len(seen), 5)


class BankFacultyTests(TestCase):
    """Soal Kalkulus Lanjut bersama disalin ke tiga jalur dan hanya terlihat oleh fakultasnya."""

    @classmethod
    def setUpTestData(cls):
        call_command("seed_gamification", stdout=io.StringIO())

    def test_shared_topic_copied_per_faculty(self):
        codes = set(Question.objects.filter(code__startswith="ST-13.2-6").values_list("code", "faculty__slug"))
        self.assertEqual(codes, {("ST-13.2-6T", "ft"), ("ST-13.2-6M", "fmipa"), ("ST-13.2-6K", "fasilkom")})

    def test_curriculum_lists_only_own_faculty_bank_questions(self):
        data = services.build_curriculum(Faculty.objects.get(slug="ft"))
        codes = {c for d in data["documents"] for c in d["items"] if isinstance(c, str) and c.startswith("ST-")}
        self.assertTrue(codes)
        self.assertFalse(any(c.endswith(("M", "K")) for c in codes))


class DiagnosticBankTests(TestCase):
    """Tes diagnostik diundi dari bank soal per level dengan aturan sebaran topik & prodi."""

    @classmethod
    def setUpTestData(cls):
        call_command("seed_gamification", stdout=io.StringIO())
        cls.faculty = Faculty.objects.get(slug="fmipa")

    def test_pool_uses_level_bank(self):
        pool = services._diagnostic_pool(self.faculty)
        self.assertGreater(sum(len(v) for v in pool.values()), 250)
        levels = {q.node.main_level.slug for q in pool["basic"] if not q.is_diagnostic}
        self.assertEqual(levels, {"precalculus"})
        self.assertTrue(all(q.node.main_level.slug == "kalkulus-dasar" for q in pool["high"] if not q.is_diagnostic))

    def test_one_question_per_topic_and_own_faculty_share(self):
        for seed in range(30):
            qs = services.diagnostic_questions(self.faculty, random.Random(seed))
            keys = [services._topic_key(q) for q in qs]
            self.assertEqual(len(keys), len(set(keys)))
            self.assertGreaterEqual(sum(q.faculty_id == self.faculty.id for q in qs), 3)

    def test_grading_uses_test_section_not_question_difficulty(self):
        qs = services.diagnostic_questions(self.faculty, random.Random(3))
        answers = [{"code": q.code, "option_id": next(o.id for o in q.shuffled_options if o.is_correct)} for q in qs]
        result = services.evaluate_diagnostic(self.faculty, answers)
        self.assertEqual(result["evaluation"], "mastery")
        self.assertEqual({k: v["total"] for k, v in result["levels"].items()}, dict(services.DIAGNOSTIC_PLAN))


from datetime import timedelta  # noqa: E402

from django.utils import timezone  # noqa: E402


class HeartsTests(TestCase):
    """Sistem nyawa: 10 nyawa, −1 saat gagal sesi, sesi terkunci di 0, penuh lagi 24 jam setelah nyawa pertama hilang."""

    setUpTestData = PracticeSessionApiTests.__dict__["setUpTestData"]
    setUp = PracticeSessionApiTests.setUp
    _open = PracticeSessionApiTests._open
    _answers = PracticeSessionApiTests._answers
    _submit = PracticeSessionApiTests._submit

    def _fail(self, session):
        data = self._open(session).json()
        return self._submit(session, data["attempt"], self._answers(data, correct=False))

    def test_new_profile_has_ten_hearts(self):
        state = UserProfile.objects.get_or_create(user=self.user)[0].hearts_state()
        self.assertEqual((state["hearts"], state["max_hearts"], state["refill_at"]), (10, 10, None))

    def test_failing_session_costs_one_heart_and_starts_timer(self):
        r = self._fail(self.s1).json()
        self.assertTrue(r["heart_lost"])
        self.assertEqual(r["hearts"]["hearts"], 9)
        self.assertGreater(r["hearts"]["refill_in"], 23 * 3600)

    def test_passing_session_keeps_hearts(self):
        data = self._open(self.s1).json()
        r = self._submit(self.s1, data["attempt"], self._answers(data)).json()
        self.assertFalse(r["heart_lost"])
        self.assertEqual(r["hearts"]["hearts"], 10)

    def test_zero_hearts_blocks_open_and_submit(self):
        data = self._open(self.s1).json()          # sesi dibuka saat nyawa masih ada
        profile = UserProfile.objects.get(user=self.user)
        profile.hearts, profile.hearts_lost_at = 0, timezone.now()
        profile.save()
        r = self._open(self.s1)
        self.assertEqual(r.status_code, 403)
        self.assertEqual(r.json()["status"], "no_hearts")
        r = self._submit(self.s1, data["attempt"], self._answers(data, correct=False))
        self.assertEqual(r.status_code, 403)
        self.assertEqual(UserProfile.objects.get(user=self.user).hearts, 0)

    def test_refill_24_hours_after_first_loss(self):
        self._fail(self.s1)
        self._fail(self.s1)
        profile = UserProfile.objects.get(user=self.user)
        first_loss = profile.hearts_lost_at
        self.assertEqual(profile.hearts, 8)
        profile.refresh_hearts(first_loss + timedelta(hours=23, minutes=59))
        self.assertEqual(profile.hearts, 8)                       # belum 24 jam
        profile.refresh_hearts(first_loss + timedelta(hours=24))
        self.assertEqual((profile.hearts, profile.hearts_lost_at), (10, None))

    def test_later_losses_do_not_restart_timer(self):
        profile = UserProfile.objects.get_or_create(user=self.user)[0]
        t0 = timezone.now()
        profile.lose_heart(t0)
        profile.lose_heart(t0 + timedelta(hours=5))
        self.assertEqual(profile.hearts_lost_at, t0)


from . import free_practice  # noqa: E402


class FreePracticeTests(TestCase):
    """Latihan Bebas: pilih topik & jumlah soal, soal acak, tanpa nyawa dan tanpa XP."""

    @classmethod
    def setUpTestData(cls):
        call_command("seed_gamification", stdout=io.StringIO())

    def setUp(self):
        self.user = User.objects.create_user("bebas", password="rahasia-123")
        self.client = Client()
        self.client.force_login(self.user)
        self.fk = Faculty.objects.get(slug="fasilkom")

    def test_catalog_lists_levels_and_only_own_faculty_topics(self):
        data = self.client.get("/api/latihan-bebas/?faculty=fasilkom").json()
        slugs = [t["slug"] for lvl in data["levels"] for t in lvl["topics"]]
        self.assertEqual([lvl["slug"] for lvl in data["levels"]][0], "precalculus")
        self.assertIn("kl-fk-gd", slugs)
        self.assertFalse(any(s.startswith(("kl-ft-", "kl-fm-")) for s in slugs))

    def test_quiz_respects_count_and_mixes_chosen_topics(self):
        topics = ["pre-fungsi-eksponensial", "pre-bilangan-real"]
        r = self.client.post("/api/latihan-bebas/mulai/", json.dumps({"faculty": "fasilkom", "topics": topics, "count": 15}),
                             content_type="application/json").json()
        qs = r["questions"]
        self.assertEqual(len(qs), 15)
        self.assertEqual(len({q["topic"] for q in qs}), 2)
        self.assertTrue(all(sum(o["is_correct"] for o in q["options"]) == 1 for q in qs))

    def test_count_is_clamped_and_other_faculty_topics_rejected(self):
        self.assertEqual(len(free_practice.build_quiz(self.fk, ["pre-bilangan-real"], 99)), free_practice.MAX_QUESTIONS)
        r = self.client.post("/api/latihan-bebas/mulai/", json.dumps({"faculty": "fasilkom", "topics": ["kl-ft-laplace"], "count": 5}),
                             content_type="application/json")
        self.assertEqual(r.status_code, 400)

    def test_does_not_touch_hearts_or_xp(self):
        profile = UserProfile.objects.get_or_create(user=self.user)[0]
        profile.hearts, profile.hearts_lost_at = 0, timezone.now()
        profile.save()
        r = self.client.post("/api/latihan-bebas/mulai/", json.dumps({"faculty": "fasilkom", "topics": ["kd-tur-rantai"], "count": 5}),
                             content_type="application/json")
        self.assertEqual(r.status_code, 200)          # nyawa 0 tetap boleh latihan bebas
        profile.refresh_from_db()
        self.assertEqual((profile.hearts, profile.xp), (0, 0))

    def test_questions_differ_between_requests(self):
        a = free_practice.build_quiz(self.fk, ["kd-tur-rantai"], 10)
        b = free_practice.build_quiz(self.fk, ["kd-tur-rantai"], 10)
        self.assertNotEqual([q["prompt"] for q in a], [q["prompt"] for q in b])



class TrialQuizTests(TestCase):
    """Kuis coba di homepage: 5 soal tanpa login (3 Kalkulus Dasar + 2 Menengah, Mudah–Sedang)."""

    @classmethod
    def setUpTestData(cls):
        call_command("seed_gamification", stdout=io.StringIO())

    def test_guest_gets_five_questions_by_plan(self):
        response = self.client.get("/api/coba-soal/")          # tanpa login
        self.assertEqual(response.status_code, 200)
        qs = response.json()["questions"]
        self.assertEqual([q["level"] for q in qs],
                         ["Kalkulus Dasar"] * 3 + ["Kalkulus Tingkat Menengah"] * 2)
        self.assertTrue(all(q["difficulty_label"] in ("Mudah", "Sedang") for q in qs))
        self.assertEqual(len({q["topic"] for q in qs}), 5)       # topik berbeda-beda
        self.assertTrue(all(sum(o["is_correct"] for o in q["options"]) == 1 for q in qs))

    def test_only_general_topics(self):
        general = set(Topic.objects.filter(node__faculty__isnull=True).values_list("title", flat=True))
        for _ in range(5):
            self.assertTrue({q["topic"] for q in free_practice.trial_quiz()} <= general)

    def test_post_not_allowed(self):
        self.assertEqual(self.client.post("/api/coba-soal/").status_code, 405)



class LevelTests(TestCase):
    """Level dari total XP: naik dari Level n ke n+1 butuh 100 + 50·(n−1) XP."""

    def test_thresholds(self):
        self.assertEqual([leveling.total_xp_for(n) for n in range(1, 6)], [0, 100, 250, 450, 700])
        self.assertEqual(leveling.level_for(0), 1)
        self.assertEqual(leveling.level_for(99), 1)
        self.assertEqual(leveling.level_for(100), 2)
        self.assertEqual(leveling.level_for(449), 3)
        self.assertEqual(leveling.level_info(260), {"level": 3, "xp": 260, "into": 10, "need": 200, "percent": 5})


class LeaderboardTests(TestCase):
    """Papan peringkat Level (/api/peringkat/) dan isian kampus (/api/profile/campus/)."""

    @classmethod
    def setUpTestData(cls):
        call_command("seed_gamification", stdout=io.StringIO())
        ft, fm = Faculty.objects.get(slug="ft"), Faculty.objects.get(slug="fmipa")
        for name, xp, fac, kampus in [("ani", 500, ft, "Universitas Indonesia"), ("budi", 300, fm, "Universitas Indonesia"),
                                      ("cici", 300, ft, "Institut Teknologi Bandung"), ("dedi", 50, ft, "Umum")]:
            user = User.objects.create_user(name, password="rahasia-123")
            UserProfile.objects.create(user=user, xp=xp, faculty=fac, campus=kampus)

    def setUp(self):
        self.client.force_login(User.objects.get(username="dedi"))

    def board(self, scope):
        return self.client.get(f"/api/peringkat/?scope={scope}").json()

    def test_global_sorted_with_shared_positions(self):
        data = self.board("global")
        self.assertEqual([(r["name"], r["pos"], r["level"]) for r in data["rows"]],
                         [("ani", 1, 4), ("budi", 2, 3), ("cici", 2, 3), ("dedi", 4, 1)])
        self.assertEqual((data["me"]["pos"], data["me"]["me"]), (4, True))

    def test_faculty_scope(self):
        self.assertEqual([r["name"] for r in self.board("fakultas")["rows"]], ["ani", "cici", "dedi"])

    def test_campus_scope_needs_real_campus(self):
        self.assertEqual(self.board("kampus")["status"], "need_campus")      # dedi = Umum
        r = self.client.post("/api/profile/campus/", json.dumps({"campus": " universitas   Indonesia"}),
                             content_type="application/json")
        self.assertEqual(r.json()["campus"], "universitas Indonesia")
        self.client.post("/api/profile/campus/", json.dumps({"campus": "Universitas Indonesia"}), content_type="application/json")
        self.assertEqual([r["name"] for r in self.board("kampus")["rows"]], ["ani", "budi", "dedi"])

    def test_campus_api_validation(self):
        bad = self.client.post("/api/profile/campus/", json.dumps({"campus": "  "}), content_type="application/json")
        self.assertEqual(bad.status_code, 400)
        ok = self.client.post("/api/profile/campus/", json.dumps({"umum": True}), content_type="application/json")
        self.assertEqual(ok.json()["campus"], "Umum")

    def test_requires_login(self):
        self.client.logout()
        self.assertEqual(self.client.get("/api/peringkat/").status_code, 302)



class RankingRuleTests(TestCase):
    """Aturan bintang rank duel (ranking.py): mirip ML + perlindungan, Apex bintang tanpa batas."""

    def st(self, tier="terra", division=3, stars=0, streak=0):
        return ranking.RankState(tier, division, stars, streak)

    def test_start_is_terra_three(self):
        start = ranking.RankState()
        self.assertEqual((ranking.label(start), ranking.ladder_points(start)), ("Terra III", 0))

    def test_full_stars_then_win_promotes_with_one_star(self):
        new, delta = ranking.apply_result(self.st("luna", 2, 4), won=True)
        self.assertEqual((new.tier, new.division, new.stars, delta), ("luna", 1, 1, 1))
        new, _ = ranking.apply_result(self.st("luna", 1, 4), won=True)
        self.assertEqual((new.tier, new.division, new.stars), ("solar", 3, 1))

    def test_third_straight_win_gives_bonus_star_below_nova(self):
        state = ranking.RankState()
        deltas = []
        for _ in range(3):
            state, d = ranking.apply_result(state, won=True)
            deltas.append(d)
        self.assertEqual(deltas, [1, 1, 2])
        self.assertEqual((state.tier, state.division, state.stars), ("terra", 2, 1))   # 3★ penuh → Terra II 1★
        _, d = ranking.apply_result(self.st("nova", 2, 1, streak=2), won=True)
        self.assertEqual(d, 1)                                                          # Nova: tanpa bonus

    def test_terra_never_loses_stars(self):
        new, delta = ranking.apply_result(self.st("terra", 1, 2, streak=4), won=False)
        self.assertEqual((new.stars, new.win_streak, delta), (2, 0, 0))
        new, _ = ranking.apply_result(self.st("terra", 3, 0), won=False)
        self.assertEqual((new.tier, new.division, new.stars), ("terra", 3, 0))

    def test_close_loss_is_protected(self):
        new, delta = ranking.apply_result(self.st("solar", 2, 2), won=False, protected=True)
        self.assertEqual((new.stars, delta), (2, 0))
        new, delta = ranking.apply_result(self.st("solar", 2, 2), won=False)
        self.assertEqual((new.stars, delta), (1, -1))

    def test_loss_at_zero_stars_demotes(self):
        new, _ = ranking.apply_result(self.st("solar", 2, 0), won=False)
        self.assertEqual((new.tier, new.division, new.stars), ("solar", 3, 3))
        new, _ = ranking.apply_result(self.st("luna", 3, 0), won=False)
        self.assertEqual((new.tier, new.division, new.stars), ("terra", 1, 2))

    def test_apex_entry_exit_and_titles(self):
        new, _ = ranking.apply_result(self.st("nova", 1, 5), won=True)
        self.assertEqual((new.tier, new.division, new.stars, ranking.label(new)), ("apex", None, 1, "Apex"))
        new, _ = ranking.apply_result(self.st("apex", None, 0), won=False)
        self.assertEqual((new.tier, new.division, new.stars), ("nova", 1, 4))
        self.assertEqual([ranking.apex_title(n) for n in (24, 25, 50, 100, 250)], ["", "Orbit", "Galaksi", "Kosmos", "Kosmos"])
        self.assertEqual(ranking.label(self.st("apex", None, 37)), "Apex Orbit")

    def test_ladder_points_increase_one_per_star(self):
        state, points = ranking.RankState(), [0]
        for _ in range(60):
            state, _ = ranking.apply_result(replace(state, win_streak=0), won=True)
            points.append(ranking.ladder_points(state))
        self.assertEqual(points, list(range(61)))
        self.assertEqual(ranking.ladder_points(self.st("apex", None, 10)), 3 * (3 + 4 + 4 + 5) + 10)

    def test_elo(self):
        self.assertEqual(ranking.elo_update(1000, 1000, 1), 1016)
        self.assertEqual(ranking.elo_update(1000, 1000, 0), 984)
        self.assertLess(ranking.elo_update(1400, 1000, 1) - 1400, 16)   # menang lawan lemah: naik sedikit


class RankLeaderboardTests(TestCase):
    """Papan peringkat Rank (/api/peringkat/?board=rank) dan PlayerRank.record_duel."""

    @classmethod
    def setUpTestData(cls):
        call_command("seed_gamification", stdout=io.StringIO())
        ft = Faculty.objects.get(slug="ft")
        states = {"ani": ("apex", None, 30, 1300), "budi": ("nova", 1, 2, 1200), "cici": ("nova", 1, 2, 1250), "dedi": None}
        for name, state in states.items():
            user = User.objects.create_user(name, password="rahasia-123")
            UserProfile.objects.create(user=user, faculty=ft, campus="Universitas Indonesia")
            if state:
                pr = PlayerRank(user=user, mmr=state[3])
                pr.set_state(ranking.RankState(*state[:3]))
                pr.save()

    def setUp(self):
        self.client.force_login(User.objects.get(username="dedi"))

    def board(self, scope="global"):
        return self.client.get(f"/api/peringkat/?board=rank&scope={scope}").json()

    def test_sorted_by_ladder_then_hidden_rating(self):
        data = self.board()
        self.assertEqual([(r["name"], r["pos"], r["rank"]["label"]) for r in data["rows"]],
                         [("ani", 1, "Apex Orbit"), ("cici", 2, "Nova I"), ("budi", 2, "Nova I"), ("dedi", 4, "Terra III")])
        self.assertEqual(data["me"]["rank"]["stars"], 0)

    def test_top_apex_only_lists_apex(self):
        self.assertEqual([r["name"] for r in self.board("apex")["rows"]], ["ani"])
        self.assertEqual(self.client.get("/api/peringkat/?board=level&scope=apex").status_code, 400)
        self.assertEqual(self.client.get("/api/peringkat/?board=duel").status_code, 400)

    def test_record_duel_updates_stars_points_and_rating(self):
        pr = rank_of(User.objects.get(username="budi"))
        delta = pr.record_duel(won=False, opponent_mmr=1200)
        pr.refresh_from_db()
        self.assertEqual((delta, pr.stars, pr.losses, pr.mmr, pr.points), (-1, 1, 1, 1184, ranking.ladder_points(pr.state)))
        pr.record_duel(won=True, opponent_mmr=1200, protected=False)
        pr.refresh_from_db()
        self.assertEqual((pr.stars, pr.wins), (2, 1))

    def test_home_bootstrap_has_rank(self):
        response = self.client.get("/")
        self.assertEqual(response.context["server_profile"]["rank"]["label"], "Terra III")
        self.assertContains(response, 'id="profile-rank"')



class DuelLogicTests(TestCase):
    """Duel real-time: antrean, penilaian di server, penutupan soal, dan hasil (duel.py)."""

    @classmethod
    def setUpTestData(cls):
        call_command("seed_gamification", stdout=io.StringIO())

    def player(self, name, xp=300, mmr=1000, state=None):
        user = User.objects.create_user(name, password="rahasia-123")
        UserProfile.objects.create(user=user, xp=xp)
        pr = rank_of(user)
        pr.mmr = mmr
        if state:
            pr.set_state(ranking.RankState(*state))
        pr.save()
        return user

    def match(self):
        a, b = self.player("ana"), self.player("bayu")
        return duel.create_match(a, b), a, b

    def correct_option(self, match, index):
        spec = match.questions[index]
        q = generators.generate(spec["key"], spec["seed"], spec["tier"])
        return next(o["id"] for o in q["options"] if o["is_correct"]), next(o["id"] for o in q["options"] if not o["is_correct"])

    def test_requires_level_three(self):
        self.assertIn("Level 3", duel.eligibility(self.player("baru", xp=249)))
        self.assertIsNone(duel.eligibility(self.player("siap", xp=250)))

    def test_matchmaking_window_and_rematch_cooldown(self):
        a, b, c = self.player("a1", mmr=1000), self.player("b1", mmr=1080), self.player("c1", mmr=1350)
        self.assertEqual(duel.find_opponent(a, "ch-a"), (None, None))
        self.assertEqual(duel.find_opponent(c, "ch-c"), (None, None))                 # selisih 350: belum
        match, channel = duel.find_opponent(b, "ch-b")
        self.assertEqual((set(match.players()), channel), ({a.id, b.id}, "ch-a"))
        self.assertFalse(DuelQueue.objects.filter(user__in=[a, b]).exists())
        DuelQueue.objects.filter(user=c).update(joined_at=timezone.now() - timedelta(seconds=60))
        self.assertEqual(duel.find_opponent(a, "ch-a2")[0].players(), [a.id, c.id])   # jendela melebar
        duel.find_opponent(b, "ch-b2")
        self.assertEqual(duel.find_opponent(a, "ch-a3"), (None, None))               # baru saja melawan b

    def test_questions_identical_and_key_not_sent(self):
        match, a, b = self.match()
        self.assertEqual(len({q["topic"] for q in match.questions}), duel.QUESTION_COUNT)
        payload = duel.start_question(match.pk, 0)
        self.assertNotIn("is_correct", json.dumps(payload))
        self.assertIsNone(duel.start_question(match.pk, 0))                           # sekali saja

    def test_answers_scored_on_server(self):
        match, a, b = self.match()
        duel.start_question(match.pk, 0)
        right, wrong = self.correct_option(match, 0)
        self.assertEqual(duel.record_answer(match.pk, a, 0, right), (True, "", False))
        self.assertFalse(duel.record_answer(match.pk, a, 0, wrong)[0])               # sudah menjawab
        self.assertFalse(duel.record_answer(match.pk, b, 1, wrong)[0])               # bukan soal berjalan
        late = timezone.now() + timedelta(seconds=match.time_limit + 5)
        self.assertEqual(duel.record_answer(match.pk, b, 0, wrong, now=late)[1], "Waktu habis.")
        self.assertEqual(duel.record_answer(match.pk, b, 0, wrong), (True, "", True))
        pa = DuelAnswer.objects.get(match=match, user=a)
        self.assertTrue(pa.correct and 100 <= pa.points <= 150)
        self.assertEqual(DuelAnswer.objects.get(match=match, user=b).points, 0)

    def test_resolve_waits_then_fills_missing(self):
        match, a, b = self.match()
        duel.start_question(match.pk, 0)
        right, _ = self.correct_option(match, 0)
        duel.record_answer(match.pk, a, 0, right)
        self.assertIsNone(duel.resolve_question(match.pk, 0))                         # b belum, waktu belum habis
        summary = duel.resolve_question(match.pk, 0, force=True)
        self.assertEqual((summary["correct_option"], summary["players"][str(b.id)]["option"]), (right, None))
        self.assertIsNone(duel.resolve_question(match.pk, 0, force=True))             # sekali saja
        self.assertEqual(DuelMatch.objects.get(pk=match.pk).current, 1)

    def test_outcome_and_protection(self):
        t = lambda pts, ms, c: {"points": pts, "ms": ms, "correct": c}
        self.assertEqual(duel.outcome(t(500, 9000, 4), t(420, 1000, 4)), "a")
        self.assertEqual(duel.outcome(t(400, 9000, 4), t(400, 8000, 4)), "b")        # seri poin: lebih cepat
        self.assertEqual(duel.outcome(t(400, 8000, 4), t(400, 8000, 4)), "draw")
        self.assertTrue(duel.is_protected(t(0, 0, 3), t(0, 0, 4)))
        self.assertFalse(duel.is_protected(t(0, 0, 2), t(0, 0, 4)))

    def test_finish_updates_ranks_and_forfeit(self):
        a, b = self.player("lina", state=("luna", 2, 2, 0)), self.player("budi", state=("luna", 2, 2, 0))
        match = duel.create_match(a, b)
        for i in range(duel.QUESTION_COUNT):
            duel.start_question(match.pk, i)
            right, wrong = self.correct_option(match, i)
            duel.record_answer(match.pk, a, i, right)
            duel.record_answer(match.pk, b, i, right if i < 2 else wrong)               # b: 2 benar
            duel.resolve_question(match.pk, i)
        result = duel.finish_match(match.pk)
        self.assertEqual((result["players"][str(a.id)]["verdict"], result["players"][str(a.id)]["star_delta"]), ("win", 1))
        self.assertEqual((result["players"][str(b.id)]["star_delta"], result["players"][str(b.id)]["protected"]), (-1, False))
        self.assertIsNone(duel.finish_match(match.pk))
        self.assertEqual((rank_of(a).stars, rank_of(b).stars, rank_of(a).wins), (3, 1, 1))

        other = duel.create_match(self.player("cici", state=("solar", 3, 1, 0)), b)
        res = duel.finish_match(other.pk, forfeit_by=b.id)
        self.assertEqual(res["players"][str(b.id)]["verdict"], "lose")
        self.assertFalse(res["players"][str(b.id)]["protected"])
        self.assertEqual(DuelMatch.objects.get(pk=other.pk).winner.username, "cici")


class DuelWebSocketTests(TransactionTestCase):
    """Duel ujung-ke-ujung lewat WebSocket: dua pemain dipertemukan, 5 soal, hasil; dan keluar di tengah duel."""

    def setUp(self):
        call_command("seed_gamification", stdout=io.StringIO())
        self.a = User.objects.create_user("andi", password="rahasia-123")
        self.b = User.objects.create_user("bela", password="rahasia-123")
        for u in (self.a, self.b):
            UserProfile.objects.create(user=u, xp=300)
        self._saved = (consumers.VS_DELAY, consumers.REVEAL_DELAY, consumers.POLL_SECONDS)
        consumers.VS_DELAY = consumers.REVEAL_DELAY = 0
        consumers.POLL_SECONDS = 0.05

    def tearDown(self):
        consumers.VS_DELAY, consumers.REVEAL_DELAY, consumers.POLL_SECONDS = self._saved

    async def connect(self, user):
        comm = WebsocketCommunicator(URLRouter(websocket_urlpatterns), "/ws/duel/")
        comm.scope["user"] = user
        connected, _ = await comm.connect()
        self.assertTrue(connected)
        return comm

    async def until(self, comm, kind, timeout=10):
        while True:
            msg = await comm.receive_json_from(timeout=timeout)
            if msg["type"] == kind:
                return msg

    def answer_key(self, match_id, index):
        match = DuelMatch.objects.get(pk=match_id)
        spec = match.questions[index]
        q = generators.generate(spec["key"], spec["seed"], spec["tier"])
        return next(o["id"] for o in q["options"] if o["is_correct"])

    async def matched_pair(self):
        ca, cb = await self.connect(self.a), await self.connect(self.b)
        await ca.send_json_to({"type": "queue"})
        await self.until(ca, "queued")
        await cb.send_json_to({"type": "queue"})
        ma, mb = await self.until(ca, "matched"), await self.until(cb, "matched")
        self.assertEqual((ma["match"], ma["opponent"]["name"], mb["opponent"]["name"]), (mb["match"], "bela", "andi"))
        return ca, cb, ma["match"]

    async def test_full_duel(self):
        ca, cb, match_id = await self.matched_pair()
        for i in range(duel.QUESTION_COUNT):
            qa, qb = await self.until(ca, "question"), await self.until(cb, "question")
            self.assertEqual((qa["index"], qb["index"], qa["prompt"]), (i, i, qb["prompt"]))
            self.assertNotIn("is_correct", json.dumps(qa))
            right = await database_sync_to_async(self.answer_key)(match_id, i)
            await ca.send_json_to({"type": "answer", "index": i, "option": right})
            self.assertEqual((await self.until(cb, "progress"))["index"], i)
            wrong = next(o["id"] for o in qb["options"] if o["id"] != right)
            await cb.send_json_to({"type": "answer", "index": i, "option": wrong})
            reveal = await self.until(ca, "reveal")
            self.assertEqual(reveal["correct_option"], right)
        fa, fb = await self.until(ca, "finished"), await self.until(cb, "finished")
        self.assertEqual((fa["you"]["verdict"], fb["you"]["verdict"], fa["you"]["correct"]), ("win", "lose", 5))
        self.assertEqual(fb["you"]["star_delta"], 0)                                   # Terra: tidak kehilangan bintang
        await ca.disconnect()
        await cb.disconnect()

    async def test_leaving_mid_duel_is_a_loss(self):
        ca, cb, match_id = await self.matched_pair()
        await self.until(ca, "question")
        await ca.disconnect()
        fb = await self.until(cb, "finished")
        self.assertEqual((fb["you"]["verdict"], fb["forfeit"]), ("win", True))
        await cb.disconnect()

    async def test_low_level_is_refused(self):
        low = await database_sync_to_async(User.objects.create_user)("rendah", password="rahasia-123")
        comm = WebsocketCommunicator(URLRouter(websocket_urlpatterns), "/ws/duel/")
        comm.scope["user"] = low
        await comm.connect()
        msg = await comm.receive_json_from()
        self.assertEqual(msg["code"], "level")
        await comm.disconnect()


# ── Masuk dengan Google (django-allauth) ──────────────────────────────
from allauth.account.models import EmailAddress  # noqa: E402
from allauth.core import context as allauth_context  # noqa: E402
from allauth.socialaccount.adapter import get_adapter as get_social_adapter  # noqa: E402
from allauth.socialaccount.helpers import complete_social_login  # noqa: E402
from allauth.socialaccount.models import SocialAccount, SocialLogin  # noqa: E402
from django.contrib.auth.models import AnonymousUser  # noqa: E402
from django.contrib.messages.storage.fallback import FallbackStorage  # noqa: E402
from django.contrib.sessions.middleware import SessionMiddleware  # noqa: E402
from django.test import RequestFactory, override_settings  # noqa: E402

GOOGLE_TEST_SETTINGS = dict(
    GOOGLE_CLIENT_ID="tes-id",
    SOCIALACCOUNT_PROVIDERS={"google": {"APPS": [{"client_id": "tes-id", "secret": "tes", "key": ""}]}},
)


class GoogleLoginTests(TestCase):
    """Tombol Google, akun baru via Google, dan penyambungan ke akun lama dengan email sama."""

    def _google_login(self, email, uid="g-123", name="Budi"):
        """Mensimulasikan callback Google yang sukses (tanpa menghubungi server Google)."""
        request = RequestFactory().get("/accounts/google/login/callback/")
        SessionMiddleware(lambda r: None).process_request(request)
        request.session.save()
        request.user = AnonymousUser()
        request._messages = FallbackStorage(request)
        with allauth_context.request_context(request):
            sociallogin = SocialLogin(
                provider=get_social_adapter().get_provider(request, "google"),
                user=User(email=email, first_name=name),
                account=SocialAccount(provider="google", uid=uid, extra_data={"email": email}),
                email_addresses=[EmailAddress(email=email, verified=True, primary=True)],
            )
            return complete_social_login(request, sociallogin)

    def test_google_button_disabled_without_client_id(self):
        with override_settings(GOOGLE_CLIENT_ID=""):
            response = self.client.get("/auth/masuk/")
        self.assertContains(response, "Lanjutkan dengan Google", count=1)
        self.assertContains(response, "disabled")
        self.assertNotContains(response, 'action="/accounts/google/login/')

    @override_settings(**GOOGLE_TEST_SETTINGS)
    def test_google_button_shown_with_client_id(self):
        response = self.client.get("/auth/masuk/")
        self.assertContains(response, "Lanjutkan dengan Google", count=1)
        self.assertContains(response, 'action="/accounts/google/login/')

    def test_login_page_has_field_icons_and_new_title(self):
        response = self.client.get("/auth/masuk/")
        self.assertContains(response, "Siap melanjutkan quest kalkulusmu hari ini?")
        self.assertContains(response, 'class="auth-input-icon"', count=5)   # 2 di Masuk + 3 di Daftar
        self.assertContains(response, 'id="mascot-card"')

    @override_settings(**GOOGLE_TEST_SETTINGS)
    def test_new_google_user_created_and_goes_to_faculty(self):
        response = self._google_login("budi@gmail.com")
        self.assertEqual(response.url, "/auth/fakultas/")
        user = User.objects.get(email="budi@gmail.com")
        self.assertTrue(SocialAccount.objects.filter(user=user, provider="google").exists())

    @override_settings(**GOOGLE_TEST_SETTINGS)
    def test_google_connects_to_existing_account_with_same_email(self):
        lama = User.objects.create_user("budilama", "budi@gmail.com", "KalkulusAsik123")
        self._google_login("budi@gmail.com")
        self.assertEqual(User.objects.filter(email__iexact="budi@gmail.com").count(), 1)
        self.assertTrue(SocialAccount.objects.filter(user=lama, provider="google").exists())

    def test_allauth_signup_page_closed(self):
        response = self.client.get("/accounts/signup/")
        self.assertNotContains(response, 'name="password1"')


from . import shop  # noqa: E402


class ShopEconomyTests(TestCase):
    """Diamond: hadiah naik level (10·level), topik tuntas (+5) — lihat shop.py."""

    setUpTestData = PracticeSessionApiTests.__dict__["setUpTestData"]
    setUp = PracticeSessionApiTests.setUp
    _open = PracticeSessionApiTests._open
    _answers = PracticeSessionApiTests._answers
    _submit = PracticeSessionApiTests._submit

    def _pass(self, session):
        data = self._open(session).json()
        return self._submit(session, data["attempt"], self._answers(data)).json()

    def test_new_account_starts_with_zero_gems(self):
        self.assertEqual(UserProfile.objects.get_or_create(user=self.user)[0].gems, 0)

    def test_level_reward_formula(self):
        self.assertEqual([shop.level_reward(n) for n in (2, 3, 5)], [20, 30, 50])
        self.assertEqual(shop.level_rewards_between(1, 4), 20 + 30 + 40)
        self.assertEqual(shop.level_rewards_between(3, 3), 0)

    def test_level_up_awards_gems(self):
        UserProfile.objects.create(user=self.user, xp=99)
        r = self._pass(self.s1)                       # Sesi I: bukan sesi wajib terakhir → tanpa bonus topik
        self.assertTrue(r["leveled_up"])
        expected = shop.level_rewards_between(1, r["level"]["level"])
        self.assertEqual((r["gems_awarded"], r["gems"]), (expected, expected))
        self.assertEqual(UserProfile.objects.get(user=self.user).gems, expected)

    def test_topic_done_awards_bonus_once(self):
        topic = self.s1.topic
        for number in (1, 2):
            self._pass(topic.sessions.get(number=number))
        before = UserProfile.objects.get(user=self.user)
        s3 = topic.sessions.get(number=3)
        r = self._pass(s3)
        lv = shop.level_rewards_between(leveling.level_for(before.xp), r["level"]["level"])
        self.assertEqual(r["gems_awarded"], lv + shop.TOPIC_REWARD)
        r = self._pass(s3)                            # ulang: sudah lulus & skor sama → tanpa hadiah
        self.assertEqual(r["gems_awarded"], 0)


class ShopApiTests(TestCase):
    """Belanja & memasang kosmetik lewat /api/toko/."""

    def setUp(self):
        self.user = User.objects.create_user("dewi", password="rahasia-123")
        self.profile = UserProfile.objects.create(user=self.user, gems=100)
        self.client = Client()
        self.client.force_login(self.user)

    def post(self, url, body):
        return self.client.post(url, data=json.dumps(body), content_type="application/json")

    def test_catalog_lists_items(self):
        data = self.client.get("/api/toko/").json()
        self.assertEqual(data["gems"], 100)
        self.assertEqual(len(data["items"]), len(shop.CATALOG))
        self.assertFalse(any(it["owned"] for it in data["items"]))

    def test_insufficient_gems_rejected(self):
        r = self.post("/api/toko/beli/", {"item": "frame-pelangi"})
        self.assertEqual(r.status_code, 400)
        self.assertEqual(UserProfile.objects.get(pk=self.profile.pk).gems, 100)

    def test_hearts_refill(self):
        self.assertEqual(self.post("/api/toko/beli/", {"item": "hearts-full"}).status_code, 400)   # sudah penuh
        self.profile.hearts, self.profile.hearts_lost_at = 3, timezone.now()
        self.profile.save()
        self.assertEqual(self.post("/api/toko/beli/", {"item": "hearts-one"}).json()["hearts"]["hearts"], 4)
        data = self.post("/api/toko/beli/", {"item": "hearts-full"}).json()
        self.assertEqual((data["hearts"]["hearts"], data["hearts"]["refill_at"], data["gems"]), (10, None, 100 - 6 - 30))

    def test_hearts_three_capped_at_max(self):
        self.profile.hearts, self.profile.hearts_lost_at = 8, timezone.now()
        self.profile.save()
        data = self.post("/api/toko/beli/", {"item": "hearts-three"}).json()
        self.assertEqual((data["hearts"]["hearts"], data["hearts"]["refill_at"]), (10, None))

    def test_shield_stock_capped(self):
        UserProfile.objects.filter(pk=self.profile.pk).update(star_shields=shop.MAX_SHIELDS)
        self.assertEqual(self.post("/api/toko/beli/", {"item": "star-shield"}).status_code, 400)

    def test_shield_pack_respects_cap(self):
        UserProfile.objects.filter(pk=self.profile.pk).update(star_shields=shop.MAX_SHIELDS - 2)
        self.assertEqual(self.post("/api/toko/beli/", {"item": "star-shield-3"}).status_code, 400)   # 3 > sisa 2
        UserProfile.objects.filter(pk=self.profile.pk).update(star_shields=0)
        data = self.post("/api/toko/beli/", {"item": "star-shield-3"}).json()
        self.assertEqual((data["star_shields"], data["gems"]), (3, 60))

    def test_cosmetic_buy_equip_and_leaderboard(self):
        data = self.post("/api/toko/beli/", {"item": "title-limit"}).json()
        self.assertEqual((data["gems"], data["equipped"]["title"], data["equipped"]["title_text"]), (80, "title-limit", "Pejuang Limit"))
        self.assertEqual(self.post("/api/toko/beli/", {"item": "title-limit"}).status_code, 400)       # sudah dimiliki
        self.assertEqual(self.post("/api/toko/pakai/", {"item": "frame-emas"}).status_code, 400)       # belum dibeli
        row = self.client.get("/api/peringkat/?board=level").json()["me"]
        self.assertEqual(row["title"], "Pejuang Limit")
        data = self.post("/api/toko/pakai/", {"item": "title-limit", "on": False}).json()
        self.assertNotIn("title", data["equipped"])


class ShopDuelTests(TestCase):
    """Perisai Bintang dipakai otomatis saat kalah duel; menang duel memberi diamond."""

    @classmethod
    def setUpTestData(cls):
        call_command("seed_gamification", stdout=io.StringIO())

    player = DuelLogicTests.player
    correct_option = DuelLogicTests.correct_option

    def play(self, a, b, b_correct):
        match = duel.create_match(a, b)
        for i in range(duel.QUESTION_COUNT):
            duel.start_question(match.pk, i)
            right, wrong = self.correct_option(match, i)
            duel.record_answer(match.pk, a, i, right)
            duel.record_answer(match.pk, b, i, right if i < b_correct else wrong)
            duel.resolve_question(match.pk, i)
        return duel.finish_match(match.pk)["players"]

    def test_shield_saves_star_and_winner_gets_gems(self):
        a, b = self.player("lina", state=("luna", 2, 2, 0)), self.player("budi", state=("luna", 2, 2, 0))
        UserProfile.objects.filter(user=b).update(star_shields=1)
        res = self.play(a, b, 2)
        self.assertEqual((res[str(b.id)]["shield_used"], res[str(b.id)]["star_delta"]), (True, 0))
        self.assertEqual((rank_of(b).stars, UserProfile.objects.get(user=b).star_shields), (2, 0))
        self.assertEqual(res[str(a.id)]["gems_awarded"], shop.DUEL_WIN_REWARD)
        self.assertEqual(UserProfile.objects.get(user=a).gems, shop.DUEL_WIN_REWARD)

    def test_shield_not_spent_when_no_star_at_risk(self):
        a, b = self.player("tia", state=("terra", 3, 1, 0)), self.player("uli", state=("terra", 3, 1, 0))
        UserProfile.objects.filter(user=b).update(star_shields=1)
        res = self.play(a, b, 2)                       # Terra: kalah tidak mengurangi bintang
        self.assertFalse(res[str(b.id)]["shield_used"])
        self.assertEqual(UserProfile.objects.get(user=b).star_shields, 1)
