"""
Calculus Bridge - Penyesuaian django-allauth untuk "Masuk dengan Google".

Mekanisme:
    - allauth hanya dipakai untuk login Google. Pendaftaran manual tetap lewat
      form kita sendiri (auth_views.register_view), jadi halaman daftar bawaan
      allauth (/accounts/signup/) ditutup, sedangkan daftar via Google dibuka.
    - Setelah login (Google maupun akun lama), pengguna diarahkan dengan aturan
      yang sama seperti login biasa: next_step_for() → pilih fakultas / beranda.
    - Jika Google gagal/dibatalkan, pengguna kembali ke halaman Masuk dengan pesan,
      bukan ke halaman error bawaan allauth.
"""

from allauth.account.adapter import DefaultAccountAdapter
from allauth.core.exceptions import ImmediateHttpResponse
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse


class AccountAdapter(DefaultAccountAdapter):
    def is_open_for_signup(self, request):
        return False   # daftar manual memakai form kita sendiri

    def get_login_redirect_url(self, request):
        from .auth_views import next_step_for
        return reverse(next_step_for(request.user))

    get_signup_redirect_url = get_login_redirect_url   # akun Google baru → pilih fakultas


class SocialAccountAdapter(DefaultSocialAccountAdapter):
    def is_open_for_signup(self, request, sociallogin):
        return True    # akun baru boleh dibuat lewat Google

    def on_authentication_error(self, request, provider, error=None, exception=None, extra_context=None):
        messages.error(request, "Masuk dengan Google gagal atau dibatalkan. Silakan coba lagi.")
        raise ImmediateHttpResponse(redirect("gamification:auth_login"))
