"""
URL configuration for project_calculus project.
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),   # login Google (django-allauth)
    path('', include('gamification.urls')),
]

# Foto profil saat pengembangan lokal (di server, /media/ dilayani web server).
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
