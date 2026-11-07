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
- [ ] 6. Minta persetujuan user untuk Level 3  ← **SEDANG MENUNGGU USER** (belum commit)
## Level Utama 3 — Kalkulus Tingkat Menengah  (belum dimulai)
## Level Utama 4 — Kalkulus Tingkat Lanjut  (belum dimulai)

## Catatan sesi
- 2026-11-07: Level 1 selesai dikembangkan. Revisi: tiap topik = node sendiri di jalur zig-zag (Practice.pathHTML),
  5 titik sesi di bawah node, Archie di samping topik aktif, topik dibuka berurutan (server + client),
  aset static diberi ?v=mtime (templatetag `asset`) agar cache browser tidak memakai JS lama. Heredoc bash sering gagal di mesin ini → tulis skrip
  patch ke scratchpad lalu jalankan dengan `.\env\Scripts\python.exe`.
- Format grafik: angka negatif di ekspresi aman (`graphlab.js` mengubah `--` → `- -`).
