"""
Calculus Bridge - Alur autentikasi & onboarding (templates/auth/).

Alur:
    /                      Homepage publik untuk tamu (views.landing_page) → tombol Masuk / Daftar
    /auth/                 Alamat lama layar pembuka → diarahkan ke homepage (/)
    /auth/masuk/           Halaman login (tab Masuk / Daftar; ?tab=daftar membuka tab Daftar)
        ├─ Masuk berhasil  → beranda (/)            [atau pilih fakultas jika belum]
        ├─ Daftar berhasil → /auth/fakultas/       (username + kata sandi, tanpa email)
        └─ Tombol Google   → /accounts/google/login/ (django-allauth, lihat auth_adapters.py)
    /auth/fakultas/        Pilih FT / FMIPA / Fasilkom
    /auth/tes-awal/        Tawaran tes kemampuan awal (Ya / Lewati)
        ├─ Ya    → /auth/tes-awal/mulai/  (10 soal: 5 mudah, 3 sedang, 2 sulit)
        │           → /auth/tes-awal/hasil/ → beranda
        └─ Lewati → beranda
"""

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST

from . import services
from .forms import FacultyForm, LoginForm, RegisterForm
from .models import Faculty, SkillNode, UserProfile

RESULT_SESSION_KEY = "diagnostic_result"
DIAGNOSTIC_SESSION_KEY = "diagnostic_questions"   # soal & urutan opsi yang sedang ditampilkan


def _profile(user):
    profile, _ = UserProfile.objects.get_or_create(user=user)
    return profile


def next_step_for(user):
    """Ke mana pengguna yang sudah login harus diarahkan berikutnya."""
    if not _profile(user).faculty_id:
        return "gamification:auth_faculty"
    return "gamification:home"


def splash(request):
    """Alamat lama layar pembuka: tamu diarahkan ke homepage publik."""
    if request.user.is_authenticated:
        return redirect(next_step_for(request.user))
    return redirect("gamification:home")


def login_view(request):
    """Halaman login berisi dua tab: Masuk (akun lama) dan Daftar (akun baru)."""
    if request.user.is_authenticated:
        return redirect(next_step_for(request.user))

    login_form = LoginForm(request, data=request.POST or None, prefix="login")
    if request.method == "POST" and login_form.is_valid():
        login(request, login_form.get_user())
        return redirect(next_step_for(request.user))

    return render(request, "auth/login.html", {
        "login_form": login_form,
        "register_form": RegisterForm(prefix="reg"),
        # ?tab=daftar → langsung buka tab Daftar (tautan "Daftar" di homepage).
        "active_tab": "daftar" if request.GET.get("tab") == "daftar" else "masuk",
        "google_enabled": bool(settings.GOOGLE_CLIENT_ID),
    })


@require_POST
def register_view(request):
    """Mendaftarkan akun baru (disimpan ke database) lalu lanjut memilih fakultas."""
    form = RegisterForm(request.POST, prefix="reg")
    if form.is_valid():
        user = form.save()
        UserProfile.objects.get_or_create(user=user)
        login(request, user, backend="django.contrib.auth.backends.ModelBackend")
        messages.success(request, f"Akun berhasil dibuat. Selamat datang, {user.first_name or user.username}!")
        return redirect("gamification:auth_faculty")

    return render(request, "auth/login.html", {
        "login_form": LoginForm(request, prefix="login"),
        "register_form": form,
        "active_tab": "daftar",
        "google_enabled": bool(settings.GOOGLE_CLIENT_ID),
    }, status=400)


@require_POST
def logout_view(request):
    logout(request)
    return redirect("gamification:home")


@login_required
def faculty_select(request):
    """Memilih fakultas; menentukan jalur belajar dan soal diagnostik."""
    profile = _profile(request.user)
    form = FacultyForm(request.POST or None, initial={"faculty": profile.faculty})
    if request.method == "POST" and form.is_valid():
        profile.faculty = form.cleaned_data["faculty"]
        profile.save(update_fields=["faculty", "updated_at"])
        return redirect("gamification:auth_diagnostic_offer")

    return render(request, "auth/faculty_select.html", {
        "form": form,
        "faculties": Faculty.objects.all(),
        "selected": profile.faculty.slug if profile.faculty else None,
    })


def _require_faculty(view):
    """Dekorator: halaman diagnostik butuh fakultas yang sudah dipilih."""
    @login_required
    def wrapper(request, *args, **kwargs):
        if not _profile(request.user).faculty_id:
            return redirect("gamification:auth_faculty")
        return view(request, *args, **kwargs)
    wrapper.__name__ = view.__name__
    wrapper.__doc__ = view.__doc__
    return wrapper


@_require_faculty
def diagnostic_offer(request):
    """Menawarkan tes kemampuan awal. Ya → tes, Lewati → beranda."""
    profile = _profile(request.user)
    return render(request, "auth/diagnostic_offer.html", {
        "faculty": profile.faculty,
        "plan": [{"label": lbl, "count": c} for lbl, c in
                 zip(("Mudah", "Sedang", "Sulit"), (c for _, c in services.DIAGNOSTIC_PLAN))],
        "total": sum(c for _, c in services.DIAGNOSTIC_PLAN),
    })


@_require_faculty
def diagnostic_test(request):
    """
    Tes kemampuan awal 10 soal sesuai prodi.

    GET  : menampilkan soal (tanpa kunci jawaban).
    POST : menilai di server, menyimpan hasil ke UserProfile & UserProgress,
           lalu mengalihkan ke halaman hasil.

    Soal diundi acak setiap GET; urutan soal & opsi disimpan di session
    (DIAGNOSTIC_SESSION_KEY) agar POST menilai soal yang sama persis.
    """
    profile = _profile(request.user)
    questions = None

    if request.method == "POST":
        # Nilai soal yang benar-benar ditampilkan (soal diundi acak setiap GET).
        questions = services.diagnostic_from_snapshot(request.session.get(DIAGNOSTIC_SESSION_KEY))
        if questions is None:
            messages.error(request, "Sesi tes kedaluwarsa. Soal baru sudah disiapkan, silakan jawab ulang.")
        else:
            answers = [{"code": q.code, "option_id": request.POST.get(f"q_{q.code}")} for q in questions]
            if any(not a["option_id"] for a in answers):
                messages.error(request, "Jawab semua soal terlebih dahulu.")
            else:
                result = services.evaluate_diagnostic(profile.faculty, answers)
                services.apply_diagnostic_to_profile(request.user, profile.faculty, result)
                request.session[RESULT_SESSION_KEY] = result
                request.session.pop(DIAGNOSTIC_SESSION_KEY, None)
                return redirect("gamification:auth_diagnostic_result")

    if questions is None:
        questions = services.diagnostic_questions(profile.faculty)
        request.session[DIAGNOSTIC_SESSION_KEY] = services.diagnostic_snapshot(questions)

    return render(request, "auth/diagnostic_test.html", {
        "faculty": profile.faculty,
        "questions": questions,
        "answered": request.POST,
    })


@_require_faculty
def diagnostic_result(request):
    result = request.session.get(RESULT_SESSION_KEY)
    if not result:
        return redirect("gamification:auth_diagnostic_offer")
    level_rows = [
        {"label": label, **result["levels"][key]}
        for key, label in (("basic", "Mudah"), ("medium", "Sedang"), ("high", "Sulit"))
    ]
    node = SkillNode.objects.filter(slug=result.get("recommended_node")).first()
    return render(request, "auth/diagnostic_result.html", {
        "result": result,
        "recommended_title": node.title if node else "",
        "level_rows": level_rows,
        "faculty": _profile(request.user).faculty,
    })
