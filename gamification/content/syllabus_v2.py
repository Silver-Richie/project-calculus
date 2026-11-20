"""
Silabus Calculus Bridge v2 — indeks target (Purcell, Stewart, OpenStax Calculus Vol 1–3).

Fase 0: berkas ini HANYA indeks. Isi materi & slide ditulis bertahap per batch ke berkas level
(content/levels/l1–l4) dengan kunci "slides" (LessonSlide). Jalankan
`python manage.py audit_kurikulum` untuk melihat cakupan: topik yang sudah ada, yang baru,
jumlah slide, dan bagian yang masih menulis rumus sebagai teks biasa (belum LaTeX).

Setiap topik:
  slug     : slug topik target. Bila sama dengan slug yang sudah ada, topik itu yang di-upgrade.
  title    : judul topik v2.
  covers   : slug topik lama yang isinya digabung/dipakai (boleh kosong untuk topik baru).
  slides   : target jumlah slide (min, max) — fondasi 4–6, topik berat 7–10+.
  track    : "inti" (semua fakultas) atau "fasilkom" / "fmipa" / "ft" (jalur spesialisasi).
  slides_on: (opsional) slug tempat dek slide dipasang bila slug target tidak ada sebagai topik
             (Level 4 berjalur fakultas: dek inti dipasang ke salinan kl-ft/fm/fk-*).

Jenis slide (LessonSlide.kind): intuition, derivation, theorem, example, pitfall, checkpoint.
Rumus: $inline$ dan $$blok$$ (KaTeX). Hindari "x^2", "r dr dθ", atau <sup> untuk rumus.
"""

LIGHT, MID, HEAVY = (4, 6), (6, 8), (7, 10)

SYLLABUS = [
    {"level": "precalculus", "title": "PreCalculus & Fondasi", "topics": [
        {"slug": "pre-bilangan-real", "title": "Sistem Bilangan Real & Interval", "covers": ["pre-bilangan-real"], "slides": LIGHT},
        {"slug": "pre-pertidaksamaan", "title": "Pertidaksamaan & Nilai Mutlak", "covers": ["pre-pertidaksamaan", "pre-nilai-mutlak"], "slides": MID},
        {"slug": "pre-konsep-fungsi", "title": "Fungsi & Komposisi", "covers": ["pre-konsep-fungsi", "pre-fungsi-linear", "pre-fungsi-kuadrat"], "slides": MID},
        {"slug": "pre-fungsi-invers", "title": "Fungsi Invers", "covers": [], "slides": LIGHT},
        {"slug": "pre-polinomial-rasional", "title": "Polinomial & Fungsi Rasional", "covers": [], "slides": MID},
        {"slug": "pre-fungsi-trigonometri", "title": "Trigonometri & Identitas", "covers": ["pre-fungsi-trigonometri"], "slides": MID},
        {"slug": "pre-fungsi-eksponensial", "title": "Eksponensial & Logaritma", "covers": ["pre-fungsi-eksponensial", "pre-fungsi-logaritma"], "slides": MID},
        {"slug": "pre-barisan-sigma", "title": "Barisan & Notasi Sigma", "covers": [], "slides": LIGHT},
        {"slug": "pre-vektor-matriks", "title": "Pengantar Vektor & Matriks Dasar", "covers": [], "slides": MID},
    ]},
    {"level": "kalkulus-dasar", "title": "Kalkulus Dasar (Kalkulus 1)", "topics": [
        {"slug": "kd-lim-konsep", "title": "Intuisi Limit & Limit Sepihak", "covers": ["kd-lim-konsep"], "slides": MID},
        {"slug": "kd-lim-aljabar", "title": "Hukum Limit & Bentuk Tak Tentu", "covers": ["kd-lim-aljabar", "kd-lim-takhingga", "kd-lim-trig"], "slides": HEAVY},
        {"slug": "kd-lim-kontinu", "title": "Kontinuitas & Teorema Nilai Antara", "covers": ["kd-lim-kontinu"], "slides": MID},
        {"slug": "kd-tur-definisi", "title": "Definisi Turunan & Garis Singgung", "covers": ["kd-tur-definisi", "kd-apl-singgung"], "slides": MID},
        {"slug": "kd-tur-rantai", "title": "Aturan Turunan & Aturan Rantai", "covers": ["kd-tur-dasar", "kd-tur-perkalian", "kd-tur-rantai", "kd-tur-transenden"], "slides": HEAVY},
        {"slug": "kd-apl-laju", "title": "Turunan Implisit & Laju Terkait", "covers": ["kd-apl-laju", "kd-tur-transenden"], "slides": MID},
        {"slug": "kd-apl-ekstrem", "title": "Ekstremum & Teorema Nilai Rata-Rata", "covers": ["kd-apl-ekstrem", "kd-apl-optimasi"], "slides": MID},
        {"slug": "kd-apl-optimasi", "title": "Sketsa Kurva & Optimasi", "covers": ["kd-apl-cekung", "kd-apl-optimasi"], "slides": HEAVY},
        {"slug": "kd-int-riemann", "title": "Integral Tak Tentu & Jumlah Riemann", "covers": ["kd-int-antiturunan", "kd-int-riemann", "kd-int-tentu"], "slides": HEAVY},
        {"slug": "kd-int-tdk", "title": "Teorema Dasar Kalkulus", "covers": ["kd-int-tdk"], "slides": MID},
        {"slug": "kd-int-substitusi", "title": "Teknik Substitusi", "covers": ["kd-int-substitusi"], "slides": MID},
    ]},
    {"level": "kalkulus-menengah", "title": "Kalkulus Tingkat Menengah (Kalkulus 2)", "topics": [
        {"slug": "km-apl-volume", "title": "Luas Daerah & Volume Benda Putar", "covers": ["km-apl-luas", "km-apl-volume", "km-apl-panjang"], "slides": HEAVY},
        {"slug": "km-apl-fisika", "title": "Kerja, Tekanan & Pusat Massa", "covers": ["km-apl-fisika"], "slides": HEAVY},
        {"slug": "km-tek-parsial", "title": "Integrasi Parsial", "covers": ["km-tek-parsial"], "slides": HEAVY},
        {"slug": "km-tek-trig", "title": "Integral Trigonometri & Substitusi Trigonometri", "covers": ["km-tek-trig"], "slides": HEAVY},
        {"slug": "km-tek-pecahan", "title": "Pecahan Parsial", "covers": ["km-tek-pecahan"], "slides": HEAVY},
        {"slug": "km-tek-takwajar", "title": "Integral Tak Wajar", "covers": ["km-tek-takwajar"], "slides": MID},
        {"slug": "km-lhopital", "title": "Aturan L'Hôpital", "covers": ["kd-apl-optimasi"], "slides": MID},
        {"slug": "km-pd-konsep", "title": "Persamaan Diferensial Orde Satu", "covers": ["km-pd-konsep", "km-pd-terpisah", "km-pd-linear", "km-pd-model"], "slides": HEAVY},
        {"slug": "km-kut-kalkulus", "title": "Kurva Parametrik & Koordinat Kutub", "covers": ["km-kut-koordinat", "km-kut-kalkulus"], "slides": HEAVY},
        {"slug": "km-ker-elips", "title": "Irisan Kerucut", "covers": ["km-ker-parabola", "km-ker-elips"], "slides": MID},
        {"slug": "km-der-uji", "title": "Barisan & Uji Konvergensi Deret", "covers": ["km-der-barisan", "km-der-geometri", "km-der-uji"], "slides": HEAVY},
        {"slug": "km-der-pangkat", "title": "Deret Pangkat, Taylor & Maclaurin", "covers": ["km-der-pangkat"], "slides": HEAVY},
    ]},
    {"level": "kalkulus-lanjut", "title": "Kalkulus Tingkat Lanjut (Kalkulus 3 / Multivariabel)", "topics": [
        {"slug": "kl-geometri-ruang", "title": "Geometri Ruang & Permukaan Kuadrik", "covers": ["kl-fm-kuadrik", "kl-ft-pb-fungsi"], "slides": MID},
        {"slug": "kl-fungsi-vektor", "title": "Fungsi Vektor & Kelengkungan", "covers": [], "slides": HEAVY, "slides_on": ["kl-ft-fungsi-vektor"]},
        {"slug": "kl-turunan-parsial", "title": "Turunan Parsial & Bidang Singgung", "covers": ["kl-ft-tp-parsial", "kl-ft-pb-limit"], "slides": HEAVY},
        {"slug": "kl-gradien", "title": "Aturan Rantai Multivariabel & Gradien", "covers": ["kl-ft-tp-gradien"], "slides": HEAVY},
        {"slug": "kl-optimasi-lagrange", "title": "Optimasi & Pengali Lagrange", "covers": ["kl-ft-lagrange", "kl-fm-hessian"], "slides": HEAVY},
        {"slug": "kl-integral-lipat", "title": "Integral Lipat Dua & Tiga", "covers": ["kl-ft-il-ganda", "kl-fm-jacobian"], "slides": HEAVY},
        {"slug": "kl-silinder-bola", "title": "Koordinat Silinder & Bola", "covers": ["kl-ft-il-koordinat"], "slides": MID},
        {"slug": "kl-medan-vektor", "title": "Medan Vektor, Divergensi & Curl", "covers": ["kl-ft-kv-medan"], "slides": MID},
        {"slug": "kl-integral-garis", "title": "Integral Garis & Teorema Green", "covers": ["kl-ft-kv-garis"], "slides": HEAVY},
        {"slug": "kl-permukaan-stokes", "title": "Integral Permukaan, Teorema Stokes & Divergensi Gauss", "covers": ["kl-ft-fluks"], "slides": (8, 12)},
    ]},
]

TRACKS = {
    "fasilkom": {"title": "Jalur Fasilkom", "topics": [
        {"slug": "kl-fk-asimtotik", "title": "Laju Pertumbuhan Asimtotik (Big-O lewat Limit)", "covers": ["kl-fk-asimtotik"], "slides": MID},
        {"slug": "kl-fk-numerik", "title": "Metode Numerik: Newton-Raphson & Simpson", "covers": ["kl-fk-asimtotik"], "slides": HEAVY},
        {"slug": "kl-fk-gd", "title": "Kalkulus Gradien untuk Optimasi (Gradient Descent)", "covers": ["kl-fk-gd"], "slides": HEAVY},
    ]},
    "fmipa": {"title": "Jalur FMIPA", "topics": [
        {"slug": "kl-fm-epsilon-delta", "title": "Pembuktian Formal Limit (ε–δ)", "covers": ["kd-lim-kontinu", "kl-fm-fk-analisis"], "slides": HEAVY},
        {"slug": "kl-fm-fk-gamma", "title": "Fungsi Khusus: Gamma, Beta & Error", "covers": ["kl-fm-fk-gamma"], "slides": MID},
        {"slug": "kl-fm-fk-analisis", "title": "Pengantar Analisis Real", "covers": ["kl-fm-fk-analisis", "kl-fm-seragam"], "slides": HEAVY},
    ]},
    "ft": {"title": "Jalur Fakultas Teknik", "topics": [
        {"slug": "kl-ft-pd-orde2", "title": "Persamaan Diferensial Orde Dua", "covers": [], "slides": HEAVY},
        {"slug": "kl-ft-fourier", "title": "Deret Fourier", "covers": [], "slides": HEAVY},
        {"slug": "kl-ft-laplace", "title": "Pengantar Transformasi Laplace", "covers": ["kl-ft-laplace"], "slides": HEAVY},
    ]},
}


def all_topics():
    """(level/jalur, topik) untuk semua topik target, urut sesuai silabus."""
    for lvl in SYLLABUS:
        for t in lvl["topics"]:
            yield lvl["level"], {**t, "track": "inti"}
    for key, tr in TRACKS.items():
        for t in tr["topics"]:
            yield key, {**t, "track": key}
