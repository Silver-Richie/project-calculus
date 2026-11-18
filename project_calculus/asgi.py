"""
ASGI config for project_calculus project.

HTTP dilayani Django seperti biasa; WebSocket (duel kalkulus real-time) diarahkan ke
gamification/routing.py dengan sesi login Django (AuthMiddlewareStack) dan pemeriksaan
asal (hanya host di ALLOWED_HOSTS).
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project_calculus.settings')
django_asgi_app = get_asgi_application()   # harus sebelum impor yang memuat model

from channels.auth import AuthMiddlewareStack  # noqa: E402
from channels.routing import ProtocolTypeRouter, URLRouter  # noqa: E402
from channels.security.websocket import AllowedHostsOriginValidator  # noqa: E402

from gamification.routing import websocket_urlpatterns  # noqa: E402

application = ProtocolTypeRouter({
    'http': django_asgi_app,
    'websocket': AllowedHostsOriginValidator(AuthMiddlewareStack(URLRouter(websocket_urlpatterns))),
})
