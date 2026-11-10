"""
URL configuration for project_calculus project.
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),   # login Google (django-allauth)
    path('', include('gamification.urls')),
]
