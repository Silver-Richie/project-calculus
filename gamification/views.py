"""
Calculus Bridge - Views & API handlers.
Provides endpoints for curriculum retrieval, diagnostic evaluation,
and progress synchronization.
"""

import json
from django.http import JsonResponse
from django.views.decorators.http import require_GET, require_POST
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from .models import Faculty, SkillNode, Question, Option, UserProgress, UserProfile


def landing_page(request):
    """
    Renders the main gamified single-page application.
    Passes faculties and available skill nodes into the template context.
    """
    faculties = Faculty.objects.all()
    nodes = SkillNode.objects.all().order_by('order')
    return render(request, "index.html", {
        "faculties": faculties,
        "nodes": nodes
    })


@require_GET
def get_curriculum_api(request):
    """
    Returns public curriculum data (faculties, skill tree nodes, and preview questions).
    Mechanism: Serializes relational database models into JSON for frontend consumption.
    """
    faculties_data = [
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

    nodes_data = [
        {
            "slug": n.slug,
            "title": n.title,
            "stage_number": n.stage_number,
            "badge_label": n.badge_label,
            "subtitle": n.subtitle,
            "summary_html": n.summary_html,
            "video_title": n.video_title,
            "video_duration": n.video_duration,
            "order": n.order,
        }
        for n in SkillNode.objects.all().order_by('order')
    ]

    return JsonResponse({
        "status": "success",
        "faculties": faculties_data,
        "nodes": nodes_data
    })


@csrf_exempt
@require_POST
def submit_diagnostic_api(request):
    """
    Evaluates submitted diagnostic answers and determines adaptive learning path.
    Mechanism:
    - Parses submitted answers for basic, medium, high questions.
    - If basic fails -> flags weak fundamentals -> recommends 'node-precalc'.
    - If basic succeeds but high fails -> recommends 'node-limit' (Calculus 1).
    - If all succeed -> awards mastery recommendation.
    """
    try:
        data = json.loads(request.body)
        answers = data.get('answers', [])
        faculty_slug = data.get('faculty', 'fasilkom')

        basic_ok = False
        medium_ok = False
        high_ok = False

        for ans in answers:
            diff = ans.get('difficulty')
            is_correct = ans.get('is_correct', False)
            if diff == 'basic' and is_correct:
                basic_ok = True
            elif diff == 'medium' and is_correct:
                medium_ok = True
            elif diff == 'high' and is_correct:
                high_ok = True

        if not basic_ok:
            rec_status = "weak_foundation"
            recommended_node = "node-precalc"
            message = "Fondasi aljabar dasar perlu penguatan. Mulai dari Precalculus Bridge."
        elif basic_ok and not high_ok:
            rec_status = "ready_for_calculus"
            recommended_node = "node-limit"
            message = "Fondasi aljabar stabil. Mulai langsung dari Calculus 1 (Limit & Turunan)."
        else:
            rec_status = "mastery"
            recommended_node = "node-chain"
            message = "Penguasaan tinggi! Siap untuk tantangan Aturan Rantai & Optimasi Lanjutan."

        return JsonResponse({
            "status": "success",
            "evaluation": rec_status,
            "recommended_node": recommended_node,
            "message": message,
            "xp_awarded": 40
        })
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=400)
