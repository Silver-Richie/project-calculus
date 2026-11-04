"""
Konten kurikulum Calculus Bridge, dipisahkan per berkas sumber.

Setiap modul di paket ini mewakili SATU berkas PDF materi:

    m1_materi_umum_kalkulus.py           -> 1_Materi_Umum_Kalkulus.pdf
    m2_materi_khusus_ft_fmipa_fasilkom.py -> 2_Materi_Khusus_FT_FMIPA_Fasilkom.pdf
    m3_soal_pembahasan_dasar_medium.py    -> 3_Soal_Pembahasan_Dasar_Medium.pdf
    m4_soal_pembahasan_ft.py              -> 4_Soal_Pembahasan_FT.pdf
    m5_soal_pembahasan_fmipa.py           -> 5_Soal_Pembahasan_FMIPA.pdf
    m6_soal_pembahasan_fasilkom.py        -> 6_Soal_Pembahasan_Fasilkom.pdf
    m7_lampiran_library_grafik.py         -> 7_Lampiran_Library_Grafik.pdf

Setiap modul mendefinisikan:
    DOCUMENT  : dict metadata berkas (-> model SourceDocument)
    NODES     : list node + bagian materinya (-> SkillNode + LessonSection)   [opsional]
    QUESTIONS : list soal + opsi + langkah pembahasan + grafik (-> Question + Option) [opsional]

Data dimuat ke database oleh: manage.py seed_gamification
Format spec grafik interaktif dijelaskan di README.md pada folder ini.
"""

from . import (
    faculties,
    m1_materi_umum_kalkulus,
    m2_materi_khusus_ft_fmipa_fasilkom,
    m3_soal_pembahasan_dasar_medium,
    m4_soal_pembahasan_ft,
    m5_soal_pembahasan_fmipa,
    m6_soal_pembahasan_fasilkom,
    m7_lampiran_library_grafik,
)

FACULTIES = faculties.FACULTIES

# Urutan = urutan nomor berkas. Berkas materi dimuat sebelum berkas soal
# karena soal menunjuk ke node yang dibuat oleh berkas materi.
SOURCES = [
    m1_materi_umum_kalkulus,
    m2_materi_khusus_ft_fmipa_fasilkom,
    m3_soal_pembahasan_dasar_medium,
    m4_soal_pembahasan_ft,
    m5_soal_pembahasan_fmipa,
    m6_soal_pembahasan_fasilkom,
    m7_lampiran_library_grafik,
]
