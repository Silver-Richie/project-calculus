"""
Calculus Bridge - Gamification URL routing.
"""

from django.urls import path

from . import auth_views
from .views import (
    landing_page, get_curriculum_api, get_diagnostic_api, submit_diagnostic_api, set_faculty_api,
    session_api, submit_session_api, complete_node_api,
    free_practice_catalog_api, free_practice_start_api, trial_quiz_api,
)

app_name = 'gamification'

urlpatterns = [
    path('', landing_page, name='home'),

    # Autentikasi & onboarding (templates/auth/)
    path('auth/', auth_views.splash, name='auth_splash'),
    path('auth/masuk/', auth_views.login_view, name='auth_login'),
    path('auth/daftar/', auth_views.register_view, name='auth_register'),
    path('auth/keluar/', auth_views.logout_view, name='auth_logout'),
    path('auth/fakultas/', auth_views.faculty_select, name='auth_faculty'),
    path('auth/tes-awal/', auth_views.diagnostic_offer, name='auth_diagnostic_offer'),
    path('auth/tes-awal/mulai/', auth_views.diagnostic_test, name='auth_diagnostic_test'),
    path('auth/tes-awal/hasil/', auth_views.diagnostic_result, name='auth_diagnostic_result'),

    # API
    path('api/coba-soal/', trial_quiz_api, name='trial_quiz_api'),
    path('api/curriculum/', get_curriculum_api, name='curriculum_api'),
    path('api/latihan-bebas/', free_practice_catalog_api, name='free_practice_catalog'),
    path('api/latihan-bebas/mulai/', free_practice_start_api, name='free_practice_start'),
    path('api/diagnostic/', get_diagnostic_api, name='diagnostic_api'),
    path('api/diagnostic/submit/', submit_diagnostic_api, name='submit_diagnostic_api'),
    path('api/profile/faculty/', set_faculty_api, name='set_faculty_api'),
    path('api/session/<int:session_id>/', session_api, name='session_api'),
    path('api/session/<int:session_id>/submit/', submit_session_api, name='submit_session_api'),
    path('api/progress/node/', complete_node_api, name='complete_node_api'),
]
