"""
Riwayat Pengerjaan & Arsip Coret-coretan untuk Mode Level Up.

Mechanism
---------
* Setiap percobaan sesi yang selesai dinilai dicatat sebagai satu LevelAttemptRecord
  (mengulang sesi yang sama 3× = 3 riwayat terpisah), dengan rincian per soal di
  QuestionAttemptDetail: cuplikan soal, jawaban user, kunci, dan coretan papan tulis
  dalam bentuk vektor (`scratchpad_strokes`).
* Penyimpanan dipanggil browser SETELAH jawaban dinilai (POST .../riwayat/), jadi
  penilaian dan XP di sessions.submit_session tidak tersentuh. Benar/salah per soal
  tetap diambil dari `results` penilaian server, bukan dari klaim browser.
* Retensi 30 hari tanpa cron job: `prune` menghapus record user itu yang sudah lewat
  HISTORY_DAYS, dijalankan setiap kali user menyimpan riwayat baru atau membukanya.
* Batas ukuran: coretan satu soal dibuang bila JSON-nya lebih besar dari
  MAX_STROKE_BYTES, dan sisa soal dalam satu percobaan dibatasi MAX_ATTEMPT_BYTES,
  supaya request dan database tetap ringan. Soal yang coretannya dibuang ditandai
  {"trimmed": True} agar viewer bisa menjelaskannya.
"""

import json
from datetime import timedelta

from django.db import transaction
from django.utils import timezone

from .models import LevelAttemptRecord, QuestionAttemptDetail

HISTORY_DAYS = 30
MAX_STROKE_BYTES = 40_000        # coretan satu soal
MAX_ATTEMPT_BYTES = 200_000      # total coretan satu percobaan
MAX_TEXT = 2_000                 # potong cuplikan soal/jawaban yang kepanjangan


def prune(user):
    """Hapus riwayat user ini yang lebih tua dari HISTORY_DAYS. Mengembalikan jumlah record terhapus."""
    cutoff = timezone.now() - timedelta(days=HISTORY_DAYS)
    deleted, _ = LevelAttemptRecord.objects.filter(user=user, created_at__lt=cutoff).delete()
    return deleted


def fit_strokes(raw):
    """
    Bersihkan payload coretan satu soal: hanya {"v", "space", "strokes"} yang dipakai.

    `space` menyatakan ruang koordinat titik: "norm" (pecahan lebar papan, papan tulis
    biasa) atau "world" (piksel kanvas, papan tulis pan/zoom). Viewer membaca tanda ini,
    jadi coretan lama tetap tergambar benar walau papan tulisnya berganti versi.
    """
    if not isinstance(raw, dict):
        return {}
    strokes = raw.get("strokes")
    if not isinstance(strokes, list) or not strokes:
        return {}
    space = raw.get("space") if raw.get("space") in ("norm", "world") else "norm"
    data = {"v": 1, "space": space, "strokes": strokes}
    if len(json.dumps(data, separators=(",", ":"))) > MAX_STROKE_BYTES:
        return {"v": 1, "space": space, "strokes": [], "trimmed": True}
    return data


def _text(value):
    return str(value or "")[:MAX_TEXT]


@transaction.atomic
def save_attempt(user, session, attempt, results, items, duration_seconds=0):
    """
    Simpan satu percobaan ke riwayat.

    `results` = daftar {"id", "correct"} dari sessions.submit_session (sumber benar/salah).
    `items`   = daftar dari browser: {"id", "prompt", "user_answer", "correct_answer", "strokes"}.
    Soal yang tidak ada di `results` (mis. id karangan) diabaikan.
    """
    truth = {str(r.get("id")): bool(r.get("correct")) for r in results or []}
    record = LevelAttemptRecord.objects.create(
        user=user, session=session, attempt=attempt,
        score_correct=sum(truth.values()), score_wrong=len(truth) - sum(truth.values()),
        duration_seconds=max(0, min(int(duration_seconds or 0), 24 * 3600)),
    )
    budget = MAX_ATTEMPT_BYTES
    details, number = [], 0
    for item in items or []:
        qid = str(item.get("id"))
        if qid not in truth:
            continue
        number += 1
        strokes = fit_strokes(item.get("strokes"))
        size = len(json.dumps(strokes, separators=(",", ":"))) if strokes else 0
        if size > budget:
            strokes = {"v": 1, "space": strokes.get("space", "norm"), "strokes": [], "trimmed": True}
        else:
            budget -= size
        details.append(QuestionAttemptDetail(
            record=record, number=number, question_ref=qid[:120],
            prompt=_text(item.get("prompt")), user_answer=_text(item.get("user_answer")),
            correct_answer=_text(item.get("correct_answer")), is_correct=truth[qid],
            scratchpad_strokes=strokes,
        ))
    QuestionAttemptDetail.objects.bulk_create(details)
    prune(user)
    return record


def _card(record):
    return {
        "id": record.id,
        "session_number": record.session.number,
        "session_title": record.session.title,
        "created_at": timezone.localtime(record.created_at).isoformat(timespec="minutes"),
        "score_correct": record.score_correct,
        "score_wrong": record.score_wrong,
        "total": record.total,
        "stars_earned": record.stars_earned,
        "duration_seconds": record.duration_seconds,
        "passed": record.passed,
        "scratchpads": sum(1 for d in record.details.all() if (d.scratchpad_strokes or {}).get("strokes")),
    }


def topic_history(user, topic):
    """
    Riwayat semua percobaan user pada satu topik, terbaru dulu.

    Percobaan dinomori per sesi sesuai urutan waktu (Percobaan #1 = yang paling awal),
    jadi nomornya tetap sama walau riwayat lama sudah terhapus karena retensi.
    """
    prune(user)
    records = list(LevelAttemptRecord.objects.filter(user=user, session__topic=topic)
                   .select_related("session").prefetch_related("details").order_by("created_at", "id"))
    seen = {}
    cards = []
    for r in records:
        seen[r.session_id] = seen.get(r.session_id, 0) + 1
        cards.append({**_card(r), "attempt_no": seen[r.session_id]})
    cards.reverse()
    return {"topic": {"slug": topic.slug, "title": topic.title}, "attempts": cards}


def attempt_detail(user, record_id):
    """Rincian satu percobaan (termasuk coretan). Mengembalikan None bila bukan milik user ini."""
    record = (LevelAttemptRecord.objects.filter(user=user, pk=record_id)
              .select_related("session__topic").prefetch_related("details").first())
    if record is None:
        return None
    return {
        **_card(record),
        "topic": {"slug": record.session.topic.slug, "title": record.session.topic.title},
        "questions": [{
            "number": d.number,
            "prompt": d.prompt,
            "user_answer": d.user_answer,
            "correct_answer": d.correct_answer,
            "is_correct": d.is_correct,
            "scratchpad": d.scratchpad_strokes or {},
        } for d in record.details.all()],
    }


def topics_with_history(user):
    """Slug topik yang punya riwayat (dipakai frontend untuk menandai node yang bisa dibuka riwayatnya)."""
    prune(user)
    slugs = (LevelAttemptRecord.objects.filter(user=user)
             .values_list("session__topic__slug", flat=True).distinct())
    return sorted(set(slugs))
