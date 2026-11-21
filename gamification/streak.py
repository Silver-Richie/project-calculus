"""
Calculus Bridge - Streak harian (hari berturut-turut bermain).

Mechanism: setiap aktivitas yang dihitung (mengirim sesi latihan, menyelesaikan Ranked Duel) memanggil
record_activity(). Hari dihitung dalam WIB (Asia/Jakarta).
    • main lagi di hari yang sama      → streak tetap
    • main di hari berikutnya          → streak + 1
    • bolong satu hari atau lebih      → streak mulai lagi dari 1
status() dipakai banner beranda: streak yang masih hidup (0 bila sudah putus) dan apakah hari ini sudah main.
"""

from datetime import timedelta
from zoneinfo import ZoneInfo

from django.utils import timezone

LOCAL_TZ = ZoneInfo("Asia/Jakarta")


def today(now=None):
    return timezone.localtime(now or timezone.now(), LOCAL_TZ).date()


def record_activity(profile, now=None):
    """Catat aktivitas hari ini pada UserProfile dan perbarui streak (aman dipanggil berulang)."""
    day = today(now)
    last = profile.last_active_on
    if last == day:
        return profile.streak_days
    profile.streak_days = profile.streak_days + 1 if last == day - timedelta(days=1) else 1
    profile.last_active_on = day
    profile.save(update_fields=["streak_days", "last_active_on"])
    return profile.streak_days


def status(profile, now=None):
    """
    {"days": streak yang masih hidup, "played_today": bool, "state": "aman" | "nunggu" | "baru"}

    aman   = sudah main hari ini; nunggu = streak masih hidup tapi belum main hari ini (putus besok);
    baru   = belum punya streak (atau sudah putus).
    """
    day = today(now)
    last = profile.last_active_on
    if last == day:
        return {"days": profile.streak_days, "played_today": True, "state": "aman"}
    if last == day - timedelta(days=1):
        return {"days": profile.streak_days, "played_today": False, "state": "nunggu"}
    return {"days": 0, "played_today": False, "state": "baru"}
