"""
Kurikulum 4 level utama (PreCalculus → Kalkulus Dasar → Menengah → Lanjut).

Struktur:
    MainLevel (judul saja)
      └─ SkillNode  = sub-level (mis. "Sistem Bilangan dan Fungsi")
           └─ Topic = sub-topik (mis. "Pertidaksamaan") ─┬─ LessonSection (materi)
                                                        └─ PracticeSession ×5 ─< QuestionTemplate (generator)

Setiap modul lN_*.py mendefinisikan MAIN_LEVEL dan SUBLEVELS (berisi TOPICS).
Level yang belum dikembangkan cukup terdaftar di MAIN_LEVELS sebagai judul; node
konten lama (7 PDF) ditempatkan sementara lewat LEGACY_PLACEMENT dan akan
digabungkan ke sub-level baru saat level itu dikerjakan (lihat docs/kurikulum/PROGRESS.md).
"""

from . import l1_precalculus, l2_kalkulus_dasar

# Modul level yang sudah dikembangkan (berurutan).
LEVEL_MODULES = [l1_precalculus, l2_kalkulus_dasar]

MAIN_LEVELS = [
    l1_precalculus.MAIN_LEVEL,
    l2_kalkulus_dasar.MAIN_LEVEL,
    {"slug": "kalkulus-menengah", "order": 3, "title": "Kalkulus Tingkat Menengah",
     "subtitle": "Teknik & aplikasi integral, PD orde satu, koordinat kutub, deret", "icon": "🌀"},
    {"slug": "kalkulus-lanjut", "order": 4, "title": "Kalkulus Tingkat Lanjut",
     "subtitle": "Peubah banyak, turunan parsial, integral lipat, kalkulus vektor", "icon": "🛰️"},
]

# Node lama (berkas 1–7) → level utama sementara, urutan relatif dipertahankan.
# (umum-limit/turunan/integral sudah diserap ke Level 2 — lihat l2_kalkulus_dasar.ABSORB_NODES)
LEGACY_PLACEMENT = {
    "umum-deret": "kalkulus-menengah",
    "umum-dua-variabel": "kalkulus-lanjut",
}
LEGACY_DEFAULT_LEVEL = "kalkulus-lanjut"   # node khusus fakultas (Tahap 6–8)

# Lima sesi latihan berlapis per sub-topik.
SESSION_PLAN = [
    # (nomor, tier, judul, ambang lulus, XP per soal)
    (1, "mudah", "Sesi I · Mudah", 0.7, 10),
    (2, "sedang", "Sesi II · Sedang", 0.7, 15),
    (3, "sulit", "Sesi III · Sulit", 0.6, 20),
    (4, "tantangan", "Sesi IV · Tantangan", 0.6, 25),
    (5, "olimpiade", "Sesi V · Olimpiade", 0.5, 30),
]
QUESTIONS_PER_SESSION = 10

BOOKS = [
    {"slug": "buku-whitman", "filename": "Whitman_Calculus Material.pdf", "title": "Whitman Calculus",
     "subtitle": "Kalkulus dasar & fokus FMIPA", "category": "buku", "order": 101},
    {"slug": "buku-mit", "filename": "MIT_Calculus.pdf", "title": "Calculus — Gilbert Strang (MIT)",
     "subtitle": "Kalkulus keteknikan (FT)", "category": "buku", "order": 102},
    {"slug": "buku-stewart", "filename": "Calculus Early Transcendentals 9e (Stewart).pdf",
     "title": "Calculus: Early Transcendentals — Stewart", "subtitle": "Visual grafik, latihan & pembahasan, Fasilkom",
     "category": "buku", "order": 103},
]
