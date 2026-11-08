"""
Bank soal dari buku referensi berlisensi terbuka (+ soal susunan tim untuk topik yang tidak ada di buku).

Sumber:
* Whitman Calculus (D. Guichard dkk.), CC BY-NC-SA 4.0 — kode ``WH-<bagian>-<nomor>``
  menunjuk latihan asli di buku.
* Strang, Calculus (MIT OpenCourseWare), CC BY-NC-SA — kode ``ST-<subbab>-<n>``;
  ``<subbab>`` = subbab buku, ``<n>`` = nomor urut adaptasi (bukan nomor latihan buku).
* Soal susunan tim (``CB-…``) untuk topik yang tidak dibahas kedua buku.

Soal diterjemahkan/diadaptasi menjadi pilihan ganda dengan pembahasan bertahap.

Mechanism
---------
Soal bank menunjuk langsung ke **topik** kurikulum 4 level. Saat seed:

* ``node``    = sub-level pemilik topik, ``faculty`` = fakultas sub-level itu,
* ``session`` = sesi latihan topik itu sesuai tingkat kesulitan
  (basic → Sesi I, medium → Sesi II, high → Sesi III),

sehingga soal ikut diundi di sesinya, dan lewat ``sessions._extra_pool`` juga
di sesi lain pada sub-level yang sama dengan tingkat kesulitan yang cocok.
Soal ber-``diag=True`` juga masuk kumpulan tes diagnostik (diundi acak).
Topik Kalkulus Lanjut yang sama di tiga jalur fakultas ditulis sekali (``kl(...)``)
lalu disalin per fakultas oleh ``expand``.
"""

from . import (
    mit_lanjut, mit_pd_parabola,
    whitman_aplikasi_turunan, whitman_integral, whitman_limit_turunan, whitman_menengah, whitman_precalc,
)
from ._q import expand

TIER_OF = {"basic": 1, "medium": 2, "high": 3}

# Dokumen sumber yang belum dibuat oleh levels.BOOKS.
DOCUMENTS = [
    {"slug": "bank-tim", "filename": "Bank soal tambahan", "title": "Soal Tambahan Calculus Bridge",
     "subtitle": "Disusun tim untuk topik yang tidak dibahas buku referensi (Laplace, Gamma, analisis, asimtotik)",
     "category": "soal", "order": 110},
]

QUESTIONS = expand([
    *whitman_precalc.QUESTIONS,
    *whitman_limit_turunan.QUESTIONS,
    *whitman_aplikasi_turunan.QUESTIONS,
    *whitman_integral.QUESTIONS,
    *whitman_menengah.QUESTIONS,
    *mit_pd_parabola.QUESTIONS,
    *mit_lanjut.QUESTIONS,
])
