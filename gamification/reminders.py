"""
Calculus Bridge - Pengingat harian lewat kalender pengguna (Tahap 1 notifikasi, tanpa OAuth).

Mechanism
---------
Server tidak pernah menghubungi Google (aman untuk allowlist akun gratis PythonAnywhere):
* google_url(): tautan "action=TEMPLATE" Google Calendar dengan RRULE:FREQ=DAILY — pengguna sendiri yang
  menekan Simpan, lalu Google Calendar yang mengirim pengingatnya ke HP mereka.
* ics(): berkas iCalendar (RFC 5545) acara berulang harian + VALARM, untuk Apple Calendar / Outlook.
Jam dipilih pengguna dalam waktu lokalnya; tz = Date.getTimezoneOffset() browser (menit, UTC − lokal,
mis. WIB = −420), sehingga acara disimpan dalam UTC dan tampil benar di zona mana pun.
"""

import re
from datetime import datetime, timedelta, timezone as dt_timezone
from urllib.parse import quote, urlencode

TITLE = "Latihan Calculus Bridge"
DETAILS = "Satu sesi latihan cukup buat jaga streak-mu. Buka: {url}"
DURATION = timedelta(minutes=15)
_JAM = re.compile(r"^([01]?\d|2[0-3]):([0-5]\d)$")


def parse(jam, tz):
    """'19:00' & '-420' → (19, 0, −420). ValueError bila tidak valid."""
    m = _JAM.match((jam or "").strip())
    if not m:
        raise ValueError("Jam harus berformat JJ:MM, mis. 19:00.")
    try:
        offset = int(tz)
    except (TypeError, ValueError):
        raise ValueError("Zona waktu tidak valid.") from None
    if not -840 <= offset <= 840:
        raise ValueError("Zona waktu tidak valid.")
    return int(m.group(1)), int(m.group(2)), offset


def first_start(hour, minute, offset, now=None):
    """Kemunculan pertama (UTC) jam lokal itu: hari ini bila belum lewat, selain itu besok."""
    now = now or datetime.now(dt_timezone.utc)
    local_now = now - timedelta(minutes=offset)
    start_local = local_now.replace(hour=hour, minute=minute, second=0, microsecond=0)
    if start_local <= local_now:
        start_local += timedelta(days=1)
    return start_local + timedelta(minutes=offset)


def _stamp(dt):
    return dt.astimezone(dt_timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def google_url(start, app_url):
    """Tautan Google Calendar untuk membuat acara berulang harian (pengguna masih bisa mengubahnya)."""
    params = {
        "action": "TEMPLATE", "text": TITLE, "details": DETAILS.format(url=app_url),
        "dates": f"{_stamp(start)}/{_stamp(start + DURATION)}", "recur": "RRULE:FREQ=DAILY", "location": app_url,
    }
    return "https://calendar.google.com/calendar/render?" + urlencode(params, quote_via=quote)


def _escape(text):
    return text.replace("\\", "\\\\").replace(";", "\\;").replace(",", "\\,").replace("\n", "\\n")


def _fold(line):
    """Lipat baris > 75 oktet sesuai RFC 5545 §3.1."""
    raw, out = line.encode("utf-8"), []
    while len(raw) > 75:
        cut = 75 if not out else 74
        while (raw[cut] & 0xC0) == 0x80:        # jangan memotong di tengah karakter UTF-8
            cut -= 1
        out.append(raw[:cut].decode("utf-8"))
        raw = raw[cut:]
    out.append(raw.decode("utf-8"))
    return "\r\n ".join(out)


def ics(start, app_url, uid, now=None):
    """Berkas .ics: acara harian berulang + alarm tepat waktu (untuk Apple Calendar / Outlook)."""
    now = now or datetime.now(dt_timezone.utc)
    lines = [
        "BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//Calculus Bridge//Pengingat Harian//ID", "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH", "BEGIN:VEVENT", f"UID:{uid}", f"DTSTAMP:{_stamp(now)}",
        f"DTSTART:{_stamp(start)}", f"DTEND:{_stamp(start + DURATION)}", "RRULE:FREQ=DAILY",
        f"SUMMARY:{_escape(TITLE)}", f"DESCRIPTION:{_escape(DETAILS.format(url=app_url))}", f"URL:{app_url}",
        "BEGIN:VALARM", "ACTION:DISPLAY", f"DESCRIPTION:{_escape(TITLE)}", "TRIGGER:-PT0M", "END:VALARM",
        "END:VEVENT", "END:VCALENDAR",
    ]
    return "\r\n".join(_fold(line) for line in lines) + "\r\n"
