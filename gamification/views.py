"""
Calculus Bridge - Views & API handlers.

Views dibuat tipis: pengambilan dan pengolahan data ada di services.py.
"""

import json

from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST

from . import services
from .models import Faculty


def landing_page(request):
    """
    Merender aplikasi satu halaman. Konten kurikulum dimuat oleh JavaScript
    lewat /api/curriculum/ sesuai fakultas yang dipilih pengguna.
    """
    return render(request, "index.html", {"faculties": Faculty.objects.all()})


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
    curriculum = services.build_curriculum(faculty)
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
