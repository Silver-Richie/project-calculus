"""
Calculus Bridge - Views & API handlers.

Views dibuat tipis: pengambilan dan pengolahan data ada di services.py.
"""

import json

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST

from . import free_practice, generators, services, sessions
from .models import Faculty, MainLevel, PracticeSession, SkillNode, Topic, UserProfile


def landing_page(request):
    """
    Alamat utama situs.

    - Belum login          → homepage publik (pengenalan fitur, video animasi, kuis coba 5 soal).
    - Belum pilih fakultas → halaman pilih fakultas.
    - Selain itu           → beranda aplikasi (aplikasi satu halaman).
    Data profil & progres dikirim ke JS lewat json_script (`server-profile`),
    sedangkan konten kurikulum dimuat lewat /api/curriculum/.
    """
    if not request.user.is_authenticated:
        return render(request, "home/homepage.html", {
            "level_count": MainLevel.objects.count(),
            "topic_count": Topic.objects.count(),
            "generator_count": len(generators.REGISTRY),
        })
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    if not profile.faculty_id:
        return redirect("gamification:auth_faculty")
    return render(request, "index.html", {
        "faculties": Faculty.objects.all(),
        "server_profile": services.profile_bootstrap(request.user),
    })


@login_required
@require_POST
def set_faculty_api(request):
    """POST /api/profile/faculty/ {"faculty": "ft"} — menyimpan jalur fakultas ke akun."""
    try:
        slug = json.loads(request.body or b"{}").get("faculty")
    except json.JSONDecodeError:
        slug = None
    faculty = Faculty.objects.filter(slug=slug).first()
    if not faculty:
        return JsonResponse({"status": "error", "message": "Fakultas tidak dikenal."}, status=400)
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    profile.faculty = faculty
    profile.save(update_fields=["faculty", "updated_at"])
    return JsonResponse({"status": "success", "faculty": faculty.slug})


@require_GET
def get_curriculum_api(request):
    """
    GET /api/curriculum/?faculty=ft

    Mengembalikan daftar fakultas dan kurikulum fakultas terpilih: skill tree
    (materi, soal, pembahasan, grafik interaktif), berkas sumber, dan lampiran.
    """
    faculty = services.get_faculty(request.GET.get("faculty", services.DEFAULT_FACULTY))
    faculties = [
        {
            "slug": f.slug,
            "name": f.name,
            "short_name": f.short_name,
            "icon": f.icon,
            "description": f.description,
            "focus_areas": f.focus_areas,
        }
        for f in Faculty.objects.all()
    ]
    curriculum = services.build_curriculum(faculty, request.user)
    return JsonResponse({
        "status": "success",
        "faculties": faculties,
        **curriculum,
        "nodes": curriculum["tree"],  # alias lama
    })


@require_GET
def get_diagnostic_api(request):
    """GET /api/diagnostic/?faculty=ft — soal diagnostik tanpa kunci jawaban."""
    faculty = services.get_faculty(request.GET.get("faculty", services.DEFAULT_FACULTY))
    questions = services.diagnostic_questions(faculty)
    return JsonResponse({
        "status": "success",
        "faculty": faculty.slug if faculty else None,
        "questions": [services.serialize_question(q, include_answer=False) for q in questions],
    })


@csrf_exempt
@require_POST
def submit_diagnostic_api(request):
    """
    POST /api/diagnostic/submit/
    Body: {"faculty": "ft", "answers": [{"code": "U-D1", "option_id": 3}, ...]}

    Menilai jawaban di server dan mengembalikan rekomendasi node awal
    (lihat services.evaluate_diagnostic untuk decision logic).
    """
    try:
        data = json.loads(request.body or b"{}")
    except json.JSONDecodeError:
        return JsonResponse({"status": "error", "message": "Body JSON tidak valid."}, status=400)

    answers = data.get("answers")
    if not isinstance(answers, list):
        return JsonResponse({"status": "error", "message": "Field 'answers' wajib berupa list."}, status=400)

    faculty = services.get_faculty(data.get("faculty", services.DEFAULT_FACULTY))
    result = services.evaluate_diagnostic(faculty, answers)
    return JsonResponse({"status": "success", **result})


def _json_body(request):
    try:
        return json.loads(request.body or b"{}")
    except json.JSONDecodeError:
        return {}


@login_required
@require_GET
def session_api(request, session_id):
    """
    GET /api/session/<id>/ — 10 soal acak (khusus user ini) untuk percobaan berjalan.

    Soal memuat kunci & pembahasan agar umpan balik bisa langsung ditampilkan;
    skor resmi tetap dihitung ulang di server saat dikirim.
    """
    session = get_object_or_404(PracticeSession.objects.select_related("topic"), pk=session_id)
    try:
        data = sessions.open_session(request.user, session)
    except sessions.NoHeartsError as err:
        return JsonResponse({"status": "no_hearts", "message": str(err), "hearts": err.state}, status=403)
    except PermissionError as err:
        return JsonResponse({"status": "locked", "message": str(err)}, status=403)
    return JsonResponse({"status": "success", **data})


@login_required
@require_POST
def submit_session_api(request, session_id):
    """POST /api/session/<id>/submit/ {"attempt": 0, "answers": [{"id": "g:key:seed", "option": 2}]}"""
    session = get_object_or_404(PracticeSession.objects.select_related("topic__node"), pk=session_id)
    body = _json_body(request)
    try:
        result = sessions.submit_session(request.user, session, int(body.get("attempt", -1)), body.get("answers") or [])
    except sessions.NoHeartsError as err:
        return JsonResponse({"status": "no_hearts", "message": str(err), "hearts": err.state}, status=403)
    except PermissionError as err:
        return JsonResponse({"status": "locked", "message": str(err)}, status=403)
    except ValueError as err:
        return JsonResponse({"status": "error", "message": str(err)}, status=409)
    return JsonResponse({"status": "success", **result})


@login_required
@require_POST
def complete_node_api(request):
    """POST /api/progress/node/ {"slug": "umum-limit"} — simpan penyelesaian node (kuis lama) ke database."""
    node = SkillNode.objects.filter(slug=_json_body(request).get("slug"), kind="lesson").first()
    if not node:
        return JsonResponse({"status": "error", "message": "Node tidak dikenal."}, status=400)
    sessions.mark_node_completed(request.user, node)
    return JsonResponse({"status": "success", "slug": node.slug})


# ── Kuis coba di homepage (tanpa login) ─────────────────────────────────────
@require_GET
def trial_quiz_api(request):
    """GET /api/coba-soal/ — 5 soal coba acak untuk tamu (lihat free_practice.trial_quiz)."""
    return JsonResponse({"status": "success", "questions": free_practice.trial_quiz()})


# ── Latihan Bebas (tanpa nyawa & tanpa XP) ──────────────────────────────────
@login_required
@require_GET
def free_practice_catalog_api(request):
    """GET /api/latihan-bebas/?faculty=ft — pilihan level → topik untuk satu fakultas."""
    faculty = services.get_faculty(request.GET.get("faculty", services.DEFAULT_FACULTY))
    return JsonResponse({"status": "success", "faculty": faculty.slug, "levels": free_practice.catalog(faculty)})


@login_required
@require_POST
def free_practice_start_api(request):
    """
    POST /api/latihan-bebas/mulai/ {"faculty": "ft", "topics": ["pre-bilangan-real", ...], "count": 10}

    Mengembalikan soal acak lengkap dengan kunci & pembahasan (dinilai di browser).
    Tidak mengubah nyawa, XP, maupun progres.
    """
    body = _json_body(request)
    faculty = services.get_faculty(body.get("faculty", services.DEFAULT_FACULTY))
    try:
        count = int(body.get("count", 10))
        questions = free_practice.build_quiz(faculty, body.get("topics") or [], count)
    except (TypeError, ValueError) as err:
        return JsonResponse({"status": "error", "message": str(err) or "Permintaan tidak valid."}, status=400)
    return JsonResponse({"status": "success", "questions": questions})
