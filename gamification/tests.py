"""
Unit tests for Calculus Bridge Gamification models and API endpoints.
"""

import json
from django.test import TestCase, Client
from django.contrib.auth.models import User
from .models import Faculty, SkillNode, Question, Option, UserProfile, UserProgress


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
            title="Tahap 1: Precalculus",
            slug="node-precalc",
            badge_label="Fondasi Aljabar",
            subtitle="Penguatan aljabar",
            summary_html="<p>Summary</p>",
            order=1
        )
        self.user = User.objects.create_user(username="mahasiswa_baru", password="password123")
        self.profile = UserProfile.objects.create(
            user=self.user,
            faculty=self.faculty,
            xp=50,
            hearts=5
        )

    def test_faculty_str(self):
        self.assertEqual(str(self.faculty), "Fasilkom - Fakultas Ilmu Komputer")

    def test_skill_node_str(self):
        self.assertEqual(str(self.node), "Stage 1: Tahap 1: Precalculus")

    def test_user_profile_deduct_heart(self):
        self.profile.deduct_heart()
        self.assertEqual(self.profile.hearts, 4)

    def test_user_profile_add_xp(self):
        self.profile.add_xp(30)
        self.assertEqual(self.profile.xp, 80)

    def test_user_progress_completion(self):
        progress = UserProgress.objects.create(
            user=self.user,
            node=self.node,
            status='active'
        )
        progress.mark_completed(earned_score=100)
        self.assertEqual(progress.status, 'completed')
        self.assertIsNotNone(progress.completed_at)


class GamificationApiTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.faculty = Faculty.objects.create(
            slug="ft",
            name="Fakultas Teknik",
            short_name="FT",
            icon="⚙️",
            description="Fokus Rekayasa Fisik",
            focus_areas="Laju Terkait"
        )
        self.node = SkillNode.objects.create(
            stage_number=1,
            title="Tahap 1: Precalculus",
            slug="node-precalc",
            order=1
        )

    def test_curriculum_api(self):
        response = self.client.get('/api/curriculum/')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data["status"], "success")
        self.assertEqual(len(data["faculties"]), 1)
        self.assertEqual(len(data["nodes"]), 1)

    def test_diagnostic_api_weak_foundation(self):
        payload = {
            "faculty": "ft",
            "answers": [
                {"difficulty": "basic", "is_correct": False},
                {"difficulty": "medium", "is_correct": True},
                {"difficulty": "high", "is_correct": False}
            ]
        }
        response = self.client.post(
            '/api/diagnostic/submit/',
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data["evaluation"], "weak_foundation")
        self.assertEqual(data["recommended_node"], "node-precalc")

    def test_diagnostic_api_ready_for_calculus(self):
        payload = {
            "faculty": "ft",
            "answers": [
                {"difficulty": "basic", "is_correct": True},
                {"difficulty": "medium", "is_correct": True},
                {"difficulty": "high", "is_correct": False}
            ]
        }
        response = self.client.post(
            '/api/diagnostic/submit/',
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data["evaluation"], "ready_for_calculus")
        self.assertEqual(data["recommended_node"], "node-limit")
