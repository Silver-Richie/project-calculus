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
        pdfs = SourceDocument.objects.exclude(category="buku")
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
        self.assertEqual(profile.recommended_node.slug, "km-teknik-integral")
        self.assertEqual(UserProgress.objects.get(user=user, node__slug="km-teknik-integral").status, "active")
        self.assertEqual(UserProgress.objects.get(user=user, node__slug="kd-limit-kekontinuan").status, "completed")

        result = self.client.get("/auth/tes-awal/hasil/")
        self.assertContains(result, "10<small>/10</small>")

    def test_diagnostic_weak_basics_starts_at_stage_one(self):
        self._register()
        self.client.post("/auth/fakultas/", {"faculty": "fasilkom"})
        questions = self.client.get("/auth/tes-awal/mulai/").context["questions"]
        data = {f"q_{q.code}": q.options.filter(is_correct=False).first().id for q in questions}
        self.client.post("/auth/tes-awal/mulai/", data)
        profile = User.objects.get(username="budi").gamification_profile
        self.assertEqual(profile.recommended_node.slug, "pre-sistem-bilangan-fungsi")

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
