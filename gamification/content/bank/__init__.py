"""
Bank soal dari buku referensi berlisensi terbuka.

Sumber: Whitman Calculus (David Guichard dkk.), lisensi CC BY-NC-SA 4.0
(https://www.whitman.edu/mathematics/calculus/). Soal diterjemahkan dan diadaptasi
menjadi pilihan ganda; kode ``WH-<bagian>-<nomor>`` menunjuk ke latihan asli di buku.
Langkah pembahasan ditulis ulang (buku hanya memuat kunci jawaban).

Mechanism
---------
Berbeda dengan berkas soal 3–6 (yang menempel ke node lama lalu diserap), soal
bank menunjuk langsung ke **topik** kurikulum 4 level. Saat seed:

* ``node``    = sub-level pemilik topik,
* ``session`` = sesi latihan topik itu sesuai tingkat kesulitan
  (basic → Sesi I, medium → Sesi II, high → Sesi III),

sehingga soal ikut diundi di sesinya, dan lewat ``sessions._extra_pool`` juga
di sesi lain pada sub-level yang sama dengan tingkat kesulitan yang cocok.
Soal ber-``diag=True`` juga masuk kumpulan tes diagnostik (diundi acak).
"""

from . import whitman_precalc, whitman_limit_turunan, whitman_aplikasi_turunan, whitman_integral, whitman_menengah

BOOK_SLUG = "buku-whitman"          # SourceDocument dibuat dari levels.BOOKS
TIER_OF = {"basic": 1, "medium": 2, "high": 3}

QUESTIONS = [
    *whitman_precalc.QUESTIONS,
    *whitman_limit_turunan.QUESTIONS,
    *whitman_aplikasi_turunan.QUESTIONS,
    *whitman_integral.QUESTIONS,
    *whitman_menengah.QUESTIONS,
]
