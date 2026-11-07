# Progres Pengembangan Kurikulum 4 Level

File checkpoint. **Claude/developer wajib membaca file ini sebelum melanjutkan**, lalu
memperbarui checklist setiap kali satu langkah selesai. Jika sesi terputus (token habis),
lanjutkan dari langkah pertama yang belum dicentang.

Referensi buku (ada di `~/Downloads`):
- Whitman Calculus — kalkulus dasar & FMIPA
- MIT Calculus (Gilbert Strang) — kalkulus keteknikan (FT)
- Stewart, Calculus Early Transcendentals 9e — visual grafik, latihan & pembahasan, Fasilkom

Keputusan user:
- Konten 7 PDF lama **digabung** ke sub-level baru yang sesuai (dikerjakan per level utama).
- Soal **diacak per user** (generator berparameter + seed per user/sesi/percobaan).
- **5 sesi** per sub-topik: I Mudah, II Sedang, III Sulit, IV Tantangan, V Olimpiade; 10 soal/sesi.
- Pengembangan **bertahap per level utama**; lanjut ke level berikutnya hanya setelah user setuju.

## Level Utama 1 — PreCalculus  (branch: `feat/precalculus-level`)
- [x] 1. Model: MainLevel, Topic, PracticeSession, QuestionTemplate, UserSessionProgress + migration 0003
- [x] 2. Mesin generator soal (`gamification/generators/`): registry, seed, opsi acak, serialisasi
- [x] 3. Generator + materi Sub-level "Sistem Bilangan dan Fungsi" (9 topik, 75 generator, lulus fuzz 300 seed)
      - materi: gamification/content/levels/l1_precalculus.py
- [x] 4. Seed: main levels, sub-level, topik, sesi, template; node lama dipetakan ke level utama
      (`content/levels/__init__.py` → LEGACY_PLACEMENT; seed idempoten, sudah dijalankan 2×)
- [x] 5. API: sesi (ambil soal acak, kirim hasil) + kurikulum bersarang
- [x] 6. Frontend: skill tree per level utama, drawer topik → materi + 5 sesi
- [x] 7. Diagnostik: weak_foundation → PreCalculus
- [x] 8. Tes + verifikasi headless (48 tes OK; headless: 0 error JS, 107 grafik generator + 21 grafik materi
      tanpa NaN di ujung slider, alur sesi I lengkap sampai dinilai server)
- [ ] 9. Minta persetujuan user untuk lanjut ke Level Utama 2 (Kalkulus Dasar)  ← **SEDANG MENUNGGU USER**
      Belum di-commit (user belum meminta commit).

## Level Utama 2 — Kalkulus Dasar  (DISETUJUI user 2026-11-07; dikerjakan di branch yang sama, belum commit)
Format: sama dengan Level 1 terbaru (tiap topik = node di jalur zig-zag, 5 sesi, topik berurutan).
Sub-level & topik (slug topik):
- kd-limit-kekontinuan: kd-lim-konsep, kd-lim-aljabar, kd-lim-takhingga, kd-lim-trig, kd-lim-kontinu
- kd-turunan: kd-tur-definisi, kd-tur-dasar, kd-tur-perkalian, kd-tur-rantai, kd-tur-transenden
- kd-aplikasi-turunan: kd-apl-singgung, kd-apl-laju, kd-apl-ekstrem, kd-apl-cekung, kd-apl-optimasi
- kd-integral: kd-int-antiturunan, kd-int-riemann, kd-int-tentu, kd-int-tdk, kd-int-substitusi
Langkah:
- [x] 1. Generator `gamification/generators/dasar/` (95 generator, lulus fuzz 300 seed; `tidy()` merapikan teks "1x", "+ −")
- [x] 2. Materi `content/levels/l2_kalkulus_dasar.py`
- [x] 3. Gabung konten lama: node umum-limit/turunan/integral → topik baru (section + soal U-* sebagai soal tetap sesi); hapus dari LEGACY_PLACEMENT
- [x] 4. Seed + tes (51 tes OK) (perbarui ekspektasi diagnostik: ready → kd-limit-kekontinuan)
- [x] 5. Verifikasi headless + screenshot (0 error JS, 211 grafik generator tanpa NaN)
- [x] 6. User menyetujui lanjut ke Level 3 (2026-11-07)
## Level Utama 3 — Kalkulus Tingkat Menengah  (DISETUJUI; branch sama, belum commit)
Sub-level & topik (4 topik per sub-level):
- km-teknik-integral: km-tek-parsial, km-tek-trig, km-tek-pecahan, km-tek-takwajar
- km-aplikasi-integral: km-apl-luas, km-apl-volume, km-apl-panjang, km-apl-fisika
- km-pd-orde-satu: km-pd-konsep, km-pd-terpisah, km-pd-linear, km-pd-model
- km-kerucut-kutub: km-ker-parabola, km-ker-elips, km-kut-koordinat, km-kut-kalkulus
- km-barisan-deret: km-der-barisan, km-der-geometri, km-der-uji, km-der-pangkat
Gabung: node umum-deret (2 bagian) → km-der-uji / km-der-pangkat; soal U-S4 → km-tek-parsial sesi 3.
Langkah:
- [x] 1. Generator `gamification/generators/menengah/` (89 generator, lulus fuzz 300 seed; tidy() kini dijalankan sebelum buang duplikat)
- [x] 2. Materi `content/levels/l3_kalkulus_menengah.py` (+ ABSORB, MOVE_QUESTIONS U-S4)
- [x] 3. Seed + tes (52 tes OK)
- [x] 4. Verifikasi headless + screenshot (0 error JS, 276 grafik generator tanpa NaN)
- [x] 5. User menyetujui Level 4 — format: JALUR TERPISAH PER FAKULTAS
## Level Utama 4 — Kalkulus Tingkat Lanjut  (DISETUJUI: jalur terpisah per fakultas; branch sama, belum commit)
Struktur: tiap fakultas (ft, fm = FMIPA, fk = Fasilkom) punya 5 sub-level `kl-<fak>-<sub>`:
peubah-banyak, turunan-parsial, integral-lipat, kalkulus-vektor, fungsi-khusus (FMIPA: "& Analisis Real").
Tiap sub-level 3 topik: 2 topik INTI (generator & materi dipakai bersama 3 fakultas, register(topic=tuple))
+ 1 topik TERAPAN khusus fakultas. Slug topik: `kl-<fak>-<kunci>`.
Inti: pb-fungsi, pb-limit | tp-parsial, tp-gradien | il-ganda, il-koordinat | kv-medan, kv-garis | fk-gamma, fk-analisis
Terapan FT : ft-galat, ft-lagrange, ft-massa, ft-fluks, ft-laplace
Terapan FM : fm-kuadrik, fm-hessian, fm-jacobian, fm-potensial, fm-seragam
Terapan FK : fk-norma, fk-gd, fk-peluang, fk-simulasi, fk-asimtotik
Gabung: node fakultas lama (ft/fmipa/fasilkom-konsep/terapan/ujian) → bagian materi ke topik terapan fakultasnya;
soal FT-/FM-/FK- → soal tetap di topik Level 2/3 yang cocok, hanya diundi untuk fakultasnya (sessions._pool).
umum-dua-variabel → topik inti tp-parsial (bagian disalin ke 3 fakultas), U-S6 → kl-ft-tp-parsial.
Diagnostik "mastery" → awal Kalkulus Menengah (bukan lagi tahap fakultas).
Langkah:
- [x] 1. Mesin: register(topic=tuple), filter soal tetap per fakultas, sub-level berfakultas (skrip engine_l4.py)
- [x] 2. Generator `gamification/generators/lanjut/` (104 generator; total 363 lulus fuzz 300 seed)
- [x] 3. Materi `content/levels/l4_kalkulus_lanjut.py` + ABSORB (semua node lama terserap)
- [x] 4. Seed + tes (55 tes OK; 94 topik, 470 sesi)
- [x] 5. Verifikasi headless 3 fakultas (0 error JS, 296 grafik tanpa NaN)
- [x] 6. Laporan akhir ke user — SEMUA LEVEL SELESAI. Belum commit (menunggu instruksi user).

## Catatan sesi
- 2026-11-07: Level 1 selesai dikembangkan. Revisi: tiap topik = node sendiri di jalur zig-zag (Practice.pathHTML),
  5 titik sesi di bawah node, Archie di samping topik aktif, topik dibuka berurutan (server + client),
  aset static diberi ?v=mtime (templatetag `asset`) agar cache browser tidak memakai JS lama. Heredoc bash sering gagal di mesin ini → tulis skrip
  patch ke scratchpad lalu jalankan dengan `.\env\Scripts\python.exe`.
- Format grafik: angka negatif di ekspresi aman (`graphlab.js` mengubah `--` → `- -`).
