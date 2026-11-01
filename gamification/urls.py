"""
Calculus Bridge - Gamification URL routing.
"""

from django.urls import path
from .views import landing_page, get_curriculum_api, submit_diagnostic_api

app_name = 'gamification'

urlpatterns = [
    path('', landing_page, name='home'),
    path('api/curriculum/', get_curriculum_api, name='curriculum_api'),
    path('api/diagnostic/submit/', submit_diagnostic_api, name='submit_diagnostic_api'),
]
