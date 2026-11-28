"""
Calculus Bridge - Views & API handlers.

Views dibuat tipis: pengambilan dan pengolahan data ada di services.py.
"""

import json
import uuid

from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q, Value
from django.db.models.functions import Coalesce
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.templatetags.static import static
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST

from . import avatar, campus, free_practice, generators, history, ranked_duel, ranking, reminders, services, sessions, shop
from .leveling import level_for, level_info
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
        "campus_suggestions": campus.SUGGESTIONS,
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



@login_required
@require_POST
def set_avatar_api(request):
    """
    POST /api/profile/avatar/ — ganti foto profil (gamification/avatar.py).
    JSON {"kind": "initial"} | {"kind": "preset", "preset": "integral"};
    unggahan: multipart dengan kind=upload dan berkas "file" (sudah dipotong 256×256 di browser).
    """
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    body = request.POST if request.FILES or request.content_type.startswith("multipart") else _json_body(request)
    kind = body.get("kind")
    try:
        if kind == "initial":
            avatar.set_initial(profile)
        elif kind == "preset":
            avatar.set_preset(profile, body.get("preset", ""))
        elif kind == "upload":
            avatar.set_upload(profile, request.FILES.get("file"))
        else:
            raise avatar.AvatarError("Jenis foto gak dikenal.")
    except avatar.AvatarError as err:
        return JsonResponse({"status": "error", "message": str(err)}, status=400)
    return JsonResponse({"status": "success", "avatar": avatar.describe(profile)})


@login_required
@require_POST
def set_campus_api(request):
    """POST /api/profile/campus/ {"campus": "Universitas Indonesia"} atau {"umum": true}."""
    body = _json_body(request)
    name = campus.UMUM if body.get("umum") else campus.normalize(body.get("campus"))
    if not name:
        return JsonResponse({"status": "error", "message": "Tulis nama kampusmu, atau centang Umum."}, status=400)
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    profile.campus = name
    profile.save(update_fields=["campus", "updated_at"])
    return JsonResponse({"status": "success", "campus": name})


TOP_LIMIT = 100          # leaderboard hanya menampilkan 100 besar


@login_required
@require_GET
def leaderboard_api(request):
    """
    GET /api/peringkat/?board=level|rank|wins&scope=global|kampus|fakultas|apex

    * board=level : urut total XP (Level dihitung dari XP).
    * board=rank  : urut posisi tangga rank duel (ranking.ladder_points), seri dipecah nilai
                    kemampuan; pemain yang belum pernah duel = Terra III 0★.
                    scope=apex → Top 100 pemain Apex se-Indonesia.
    * board=wins  : urut jumlah kemenangan duel (bukan posisi rank).

    Mengembalikan Top 100 (`rows`), pemain di sekitar posisi pengguna (`around`, dua di atas & dua di bawah —
    hanya bila pengguna masih di dalam Top 100, supaya daftar tidak pernah memuat pemain di luar 100 besar),
    dan baris pengguna (`me`, selalu dengan posisinya). Posisi sama untuk nilai sama; `index` = urutan pasti
    di daftar (untuk menggabungkan `rows` & `around` di layar).
    Sebaran tier (`tiers`) tetap menghitung SEMUA pemain di cakupan, bukan hanya Top 100.
    Papan rank/wins juga memuat 5 hasil duel terakhir tiap baris (`recent`) dan `played` (sudah ada
    duel di cakupan ini); papan rank memuat jumlah pemain per tier (`tiers`, kolom Ketinggian).
    "kampus" butuh kampus terisi dan bukan "Umum"; "fakultas" memakai fakultas akun.
    """
    board = request.GET.get("board", "level")
    scope = request.GET.get("scope", "global")
    if board not in ("level", "rank", "wins") or scope not in ("global", "kampus", "fakultas", "apex") \
            or (scope == "apex" and board != "rank"):
        return JsonResponse({"status": "error", "message": "Papan atau cakupan tidak dikenal."}, status=400)
    me, _ = UserProfile.objects.get_or_create(user=request.user)
    qs = (UserProfile.objects.select_related("user", "faculty", "user__duel_rank").filter(user__is_active=True)
          .annotate(rank_points=Coalesce("user__duel_rank__points", 0), rank_mmr=Coalesce("user__duel_rank__mmr", 1000),
                    rank_wins=Coalesce("user__duel_rank__wins", 0)))
    if scope == "kampus":
        if not me.campus or me.campus == campus.UMUM:
            return JsonResponse({"status": "need_campus", "scope": scope, "campus": me.campus})
        qs = qs.filter(campus=me.campus)
    elif scope == "fakultas":
        if not me.faculty_id:
            return JsonResponse({"status": "error", "message": "Pilih fakultas dulu, ya."}, status=400)
        qs = qs.filter(faculty_id=me.faculty_id)
    elif scope == "apex":
        qs = qs.filter(user__duel_rank__tier="apex")

    key, order = {
        "level": ("xp", ["-xp", "user_id"]),
        "rank": ("rank_points", ["-rank_points", "-rank_mmr", "user_id"]),
        "wins": ("rank_wins", ["-rank_wins", "user_id"]),
    }[board]
    duels = board != "level"

    def row(p, pos, index=None):
        look = shop.appearance(p)
        pr = getattr(p.user, "duel_rank", None)
        st = pr.state if pr else ranking.RankState()
        r = {"pos": pos, "index": index, "name": p.user.first_name or p.user.username, "username": p.user.username,
             "user_id": p.user_id, "faculty": p.faculty.short_name if p.faculty else "", "campus": p.campus,
             "me": p.pk == me.pk, "frame": look.get("frame", ""), "title": look["title_text"], "tier": st.tier,
             "avatar": avatar.describe(p)}
        if board == "level":
            r.update(xp=p.xp, level=level_for(p.xp))
        else:
            r.update(rank=ranking.describe(st), wins=pr.wins if pr else 0, losses=pr.losses if pr else 0,
                     points=ranking.ladder_points(st))
        return r

    def position(p):
        return qs.filter(**{f"{key}__gt": getattr(p, key)}).count() + 1

    def index_of(p):
        """Urutan pasti p di qs.order_by(*order): hitung yang mendahuluinya per kunci urutan."""
        ahead, tied = Q(), Q()
        for field in order:
            name = field.lstrip("-")
            ahead |= tied & Q(**{f"{name}__{'gt' if field.startswith('-') else 'lt'}": getattr(p, name)})
            tied &= Q(**{name: getattr(p, name)})
        return qs.filter(ahead).count()

    ordered = qs.order_by(*order)
    top = list(ordered[:TOP_LIMIT])
    rows, pos, prev = [], 0, None
    for i, p in enumerate(top):
        value = getattr(p, key)
        if value != prev:
            pos, prev = i + 1, value
        rows.append(row(p, pos, i))

    me_row = qs.filter(pk=me.pk).first()
    around = []
    if me_row:
        my_index = index_of(me_row)
        if my_index < TOP_LIMIT:
            start = max(0, my_index - 2)
            around = [row(p, position(p), start + j) for j, p in enumerate(ordered[start:min(my_index + 3, TOP_LIMIT)])]
        mine = row(me_row, position(me_row), my_index)
    else:
        mine = row(me, qs.filter(**{f"{key}__gt": getattr(me, key, 0) if board == "level" else 0}).count() + 1)
    if board == "level":
        mine["level_info"] = level_info(me.xp)

    data = {"status": "success", "board": board, "scope": scope, "total": qs.count(),
            "rows": rows, "around": around, "me": mine,
            "label": {"global": "Seluruh Indonesia", "kampus": me.campus, "apex": "Top 100 Apex se-Indonesia",
                      "fakultas": me.faculty.name if me.faculty else ""}[scope]}
    if duels:
        shown = {r["user_id"] for r in rows + around + [mine]}
        recent = ranked_duel.recent_results(list(shown))
        for r in rows + around + [mine]:
            r["recent"] = recent.get(r["user_id"], [])
        data["played"] = qs.filter(Q(user__duel_rank__wins__gt=0) | Q(user__duel_rank__losses__gt=0)).exists()
    if board == "rank":
        counts = dict(qs.annotate(t=Coalesce("user__duel_rank__tier", Value("terra")))
                      .values_list("t").annotate(n=Count("pk")).values_list("t", "n"))
        data["tiers"] = [{"tier": t, "name": ranking.TIER_NAMES[t], "count": counts.get(t, 0)} for t in ranking.TIERS]
    return JsonResponse(data)


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
def leave_session_api(request, session_id):
    """
    POST /api/session/<id>/keluar-tab/ {"attempt": 0, "quit": false}

    Dikirim browser saat pengguna keluar tab/jendela di tengah sesi (anti-curang, sessions.leave_tab).
    """
    session = get_object_or_404(PracticeSession.objects.select_related("topic__node"), pk=session_id)
    body = _json_body(request)
    try:
        result = sessions.leave_tab(request.user, session, int(body.get("attempt", -1)), bool(body.get("quit")))
    except sessions.NoHeartsError as err:
        return JsonResponse({"status": "no_hearts", "message": str(err), "hearts": err.state}, status=403)
    except PermissionError as err:
        return JsonResponse({"status": "locked", "message": str(err)}, status=403)
    return JsonResponse(result)


# ── Riwayat Pengerjaan & Arsip Coret-coretan (gamification/history.py) ──────
@login_required
@require_POST
def save_attempt_history_api(request, session_id):
    """
    POST /api/session/<id>/riwayat/ — simpan percobaan yang baru dinilai ke riwayat.

    Body: {"attempt": 0, "duration": 180, "results": [{"id", "correct"}],
           "items": [{"id", "prompt", "user_answer", "correct_answer", "strokes"}]}
    Benar/salah diambil dari `results` hasil penilaian server yang dikirim balik browser;
    id yang tidak ada di situ diabaikan, jadi riwayat tidak bisa diisi soal karangan.
    """
    session = get_object_or_404(PracticeSession.objects.select_related("topic"), pk=session_id)
    body = _json_body(request)
    record = history.save_attempt(
        request.user, session, int(body.get("attempt", 0)),
        body.get("results") or [], body.get("items") or [], body.get("duration", 0),
    )
    return JsonResponse({"status": "success", "record": record.id, "saved": record.details.count()})


@login_required
@require_GET
def topic_history_api(request, slug):
    """GET /api/riwayat/topik/<slug>/ — daftar percobaan user pada satu topik, terbaru dulu."""
    topic = get_object_or_404(Topic, slug=slug)
    return JsonResponse({"status": "success", **history.topic_history(request.user, topic)})


@login_required
@require_GET
def attempt_history_api(request, record_id):
    """GET /api/riwayat/<id>/ — rincian satu percobaan beserta coretan papan tulisnya."""
    data = history.attempt_detail(request.user, record_id)
    if data is None:
        return JsonResponse({"status": "error", "message": "Riwayat tidak ditemukan."}, status=404)
    return JsonResponse({"status": "success", **data})


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


# ── Toko Diamond (shop.py) ──────────────────────────────────────────────────
@login_required
@require_GET
def shop_api(request):
    """GET /api/toko/ — saldo diamond, stok perisai, nyawa, dan katalog bertanda dimiliki/terpasang."""
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    return JsonResponse({"status": "success", **shop.state(profile)})


@login_required
@require_POST
def shop_buy_api(request):
    """POST /api/toko/beli/ {"item": "hearts-full"} — beli satu barang (dinilai & dikunci di server)."""
    try:
        data = shop.buy(request.user, _json_body(request).get("item"))
    except shop.ShopError as err:
        return JsonResponse({"status": "error", "message": str(err)}, status=400)
    return JsonResponse({"status": "success", **data})


@login_required
@require_POST
def shop_equip_api(request):
    """POST /api/toko/pakai/ {"item": "acc-mahkota", "on": true} — pasang/lepas kosmetik milik sendiri."""
    body = _json_body(request)
    try:
        data = shop.equip(request.user, body.get("item"), bool(body.get("on", True)))
    except shop.ShopError as err:
        return JsonResponse({"status": "error", "message": str(err)}, status=400)
    return JsonResponse({"status": "success", **data})


# ── Ranked Duel asinkron (hantu/bot, tanpa WebSocket) — aturan di ranked_duel.py ─────────
def _ranked_call(fn):
    try:
        return JsonResponse({"status": "success", **(fn() or {})})
    except ranked_duel.RankedError as err:
        return JsonResponse({"status": "error", "message": str(err)}, status=400)


@login_required
@require_POST
def ranked_start_api(request):
    """POST /api/ranked/mulai/ — cari lawan (hantu/bot sesuai rank) dan siapkan 10 soal."""
    return _ranked_call(lambda: ranked_duel.match_intro(ranked_duel.find_match(request.user)))


@login_required
@require_POST
def ranked_question_api(request, match_id):
    """POST /api/ranked/<id>/soal/ — buka soal berikutnya (waktu mulai dicatat server)."""
    return _ranked_call(lambda: {"question": ranked_duel.open_question(match_id, request.user)})


@login_required
@require_POST
def ranked_answer_api(request, match_id):
    """POST /api/ranked/<id>/jawab/ {"index": 0, "option": 2|null} — null = waktu habis."""
    body = _json_body(request)
    option = body.get("option")
    return _ranked_call(lambda: ranked_duel.submit_answer(
        match_id, request.user, int(body.get("index", -1)), None if option is None else int(option)))


@login_required
@require_POST
def ranked_leave_api(request, match_id):
    """POST /api/ranked/<id>/keluar-tab/ — anti-curang: keluar tab ke-1 = soal salah, ke-2 = menyerah."""
    return _ranked_call(lambda: ranked_duel.leave_tab(match_id, request.user))


@login_required
@require_POST
def ranked_forfeit_api(request, match_id):
    """POST /api/ranked/<id>/menyerah/ — keluar di tengah duel = kalah (tanpa Streak Shield)."""
    def run():
        match = ranked_duel.RankedMatch.objects.filter(pk=match_id, user=request.user).first()
        if not match:
            raise ranked_duel.RankedError("Duel-nya gak ketemu.")
        return {"result": ranked_duel.resolve_duel(match, forfeit=True)}
    return _ranked_call(run)


# ── PWA & pengingat harian (Tahap 1 notifikasi) — logika kalender di reminders.py ─────────
SW_VERSION = "v1"        # naikkan bila daftar berkas cache service worker berubah


@require_GET
def manifest_view(request):
    """GET /manifest.webmanifest — membuat aplikasi bisa dipasang (Add to Home Screen)."""
    icon = lambda name, size, purpose="any": {"src": static(f"img/pwa/{name}"), "sizes": size, "type": "image/png", "purpose": purpose}  # noqa: E731
    data = {
        "name": "Calculus Bridge", "short_name": "Calculus Bridge", "lang": "id",
        "description": "Belajar kalkulus interaktif: skill tree, latihan berjenjang, dan Ranked Duel.",
        "start_url": "/?source=pwa", "scope": "/", "display": "standalone",
        "background_color": "#F7F5F2", "theme_color": "#2563EB",
        "icons": [icon("icon-192.png", "192x192"), icon("icon-512.png", "512x512"), icon("maskable-512.png", "512x512", "maskable")],
    }
    return JsonResponse(data, content_type="application/manifest+json", json_dumps_params={"ensure_ascii": False})


@require_GET
def service_worker_view(request):
    """
    GET /sw.js — service worker dilayani dari akar situs (bukan /static/) agar cakupannya seluruh situs.
    Tidak di-cache browser lama-lama supaya pembaruan cepat terpasang.
    """
    response = render(request, "pwa/sw.js", {"version": SW_VERSION, "offline_url": "/offline/",
                                             "icon": static("img/pwa/icon-192.png")},
                      content_type="application/javascript")
    response["Cache-Control"] = "no-cache"
    response["Service-Worker-Allowed"] = "/"
    return response


@require_GET
def offline_view(request):
    """GET /offline/ — halaman cadangan saat tidak ada koneksi (disimpan service worker)."""
    return render(request, "pwa/offline.html")


def _reminder_start(request):
    hour, minute, offset = reminders.parse(request.GET.get("jam"), request.GET.get("tz", "-420"))
    return reminders.first_start(hour, minute, offset), request.build_absolute_uri("/")


@require_GET
def reminder_google_view(request):
    """GET /pengingat/google/?jam=19:00&tz=-420 — alihkan ke Google Calendar (acara harian, tanpa OAuth)."""
    try:
        start, app_url = _reminder_start(request)
    except ValueError as err:
        return JsonResponse({"status": "error", "message": str(err)}, status=400)
    return redirect(reminders.google_url(start, app_url))


@require_GET
def reminder_ics_view(request):
    """GET /pengingat.ics?jam=19:00&tz=-420 — unduh pengingat harian untuk Apple Calendar / Outlook."""
    try:
        start, app_url = _reminder_start(request)
    except ValueError as err:
        return JsonResponse({"status": "error", "message": str(err)}, status=400)
    body = reminders.ics(start, app_url, f"{uuid.uuid4()}@{request.get_host()}")
    response = HttpResponse(body, content_type="text/calendar; charset=utf-8")
    response["Content-Disposition"] = 'attachment; filename="pengingat-calculus-bridge.ics"'
    return response
