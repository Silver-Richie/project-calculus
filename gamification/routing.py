"""Rute WebSocket (lihat project_calculus/asgi.py)."""

from django.urls import path

from .consumers import DuelConsumer

websocket_urlpatterns = [
    path("ws/duel/", DuelConsumer.as_asgi()),
]
