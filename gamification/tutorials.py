"""
Calculus Bridge - Tur panduan kontekstual (spotlight Archie per halaman, static/js/tour.js).

UserProfile.completed_tutorials = daftar slug tur yang sudah selesai atau dilewati. Tur suatu halaman
hanya muncul otomatis bila slug-nya belum ada di daftar. "Ulangi Panduan Aplikasi" di Profil mengosongkan daftar.
"""

# Urutan = urutan tampil di dokumentasi; slug harus sama dengan kunci TOURS di static/js/tour.js.
PAGES = ("home", "quiz", "ranked", "shop", "leaderboard", "lesson")


def mark_done(profile, page):
    """Tambahkan slug tur ke daftar selesai (sekali saja). ValueError bila slug tidak dikenal."""
    if page not in PAGES:
        raise ValueError("Tur tidak dikenal.")
    done = list(profile.completed_tutorials or [])
    if page not in done:
        done.append(page)
        profile.completed_tutorials = done
        profile.save(update_fields=["completed_tutorials"])
    return done


def reset(profile):
    """Kosongkan daftar: semua tur akan muncul lagi saat halamannya dibuka."""
    profile.completed_tutorials = []
    profile.save(update_fields=["completed_tutorials"])
    return []
