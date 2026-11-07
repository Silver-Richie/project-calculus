# Konten Kurikulum Calculus Bridge

Satu modul Python = satu berkas PDF materi. Setelah mengubah konten, jalankan:

```bash
.\env\Scripts\python.exe manage.py seed_gamification
```

Seed bersifat idempoten: node dicocokkan lewat `slug`, soal lewat `code`, dan node/soal
yang sudah tidak ada di berkas konten akan dihapus (pakai `--keep-stale` untuk mencegahnya).

## Peta berkas → database

| Modul | Berkas sumber | Isi di database |
|---|---|---|
| `m1_materi_umum_kalkulus.py` | 1_Materi_Umum_Kalkulus.pdf | Tahap 1–5 (semua fakultas) |
| `m2_materi_khusus_ft_fmipa_fasilkom.py` | 2_Materi_Khusus_FT_FMIPA_Fasilkom.pdf | Tahap 6–8 per fakultas (A = FT, B = FMIPA, C = Fasilkom) |
| `m3_soal_pembahasan_dasar_medium.py` | 3_Soal_Pembahasan_Dasar_Medium.pdf | Soal U-D1…U-S7 di Tahap 1–5 |
| `m4_soal_pembahasan_ft.py` | 4_Soal_Pembahasan_FT.pdf | Soal FT-M/S/H → Tahap 6/7/8 jalur FT |
| `m5_soal_pembahasan_fmipa.py` | 5_Soal_Pembahasan_FMIPA.pdf | Soal FM-M/S/H → Tahap 6/7/8 jalur FMIPA |
| `m6_soal_pembahasan_fasilkom.py` | 6_Soal_Pembahasan_Fasilkom.pdf | Soal FK-M/S/H → Tahap 6/7/8 jalur Fasilkom |
| `m7_lampiran_library_grafik.py` | 7_Lampiran_Library_Grafik.pdf | Bacaan referensi (tidak masuk skill tree) |

## Skema database

```
Faculty ─┬─< SourceDocument (1 baris per PDF; faculty kosong = umum)
         ├─< SkillNode (faculty kosong = Tahap umum) ─┬─< LessonSection (heading, body_html, graphs)
         │        └── source_document → SourceDocument └─< Question (code, steps, answer, graphs) ─< Option
         └─< UserProfile / UserProgress (progress → SkillNode)
```

* Soal tingkat **Mudah/Dasar** → `difficulty="basic"`, **Sedang/Medium** → `"medium"`, **Sulit** → `"high"`.
* `is_diagnostic=True` menandai soal tes diagnostik (U-D1 + satu soal Sedang & Sulit per fakultas).

## Format grafik interaktif (`graphs`)

Dirender oleh `static/js/graphlab.js`. Setiap `params` menjadi slider; `value` adalah nilai
di soal. Saat slider digeser, grafik soal tetap tampil sebagai bayangan abu-abu dan tombol
**📌 Pin** menyimpan kondisi untuk dibandingkan.

```python
{
    "type": "2d",                       # atau "3d"
    "title": "Judul grafik",
    "x": [-3, 5], "y": [-10, "2*a"],    # rentang; boleh ekspresi parameter
    "params": [param("a", "Label slider", min, max, step, nilai_soal, "simbol")],
    "elements": [
        {"type": "fn", "expr": "a*x**2", "color": "blue", "label": "f(x)"},
        {"type": "fill", "upper": "x+2", "lower": "x*x", "from": -1, "to": 2},
        {"type": "point", "x": "a", "y": "a*a", "hollow": False},
        {"type": "segment", "x1": 0, "y1": 0, "x2": "a", "y2": 1, "arrow": True},
        {"type": "hline", "y": 2}, {"type": "vline", "x": "a"},
        {"type": "hband", "from": "4-eps", "to": "4+eps"}, {"type": "vband", ...},
        {"type": "riemann", "id": "R", "expr": "x", "from": 0, "to": 2, "n": "n", "mode": "right"},
        {"type": "iter", "id": "G", "init": {"x": 0}, "update": {"x": "x-eta*2*(x-3)"},
         "steps": "k", "px": "x", "py": "(x-3)**2"},
        {"type": "param", "t": [0, "2*pi"], "x": "cos(t)", "y": "sin(t)"},
        {"type": "bar", "x": 1, "w": 0.3, "h": "p1"},
        {"type": "text", "x": 1, "y": 2, "text": "nilai = {{a*2}}"},
    ],
    "readouts": [readout("Label", "ekspresi", digit)],   # tabel nilai soal vs sekarang
    "caption": "Penjelasan singkat",
}
```

3D: `{"type": "3d", "surfaces": [{"u": [a, b], "v": [c, d], "x": "...", "y": "...", "z": "..."}]}`
(slider putar & kemiringan kamera ditambahkan otomatis).

Ekspresi memakai sintaks JavaScript: `x**2`, `sin`, `cos`, `exp`, `ln`, `sqrt`, `pi`, `e`,
`fact(n)`, `sum(a, b, k => ...)`, `sigmoid(z)`, `min`, `max`. Hasil elemen ber-`id`
(`riemann`, `iter`) bisa dipakai di readout, mis. `"R"` atau `"G.x"`.
Hindari nama parameter `x`, `t`, `u`, `v` karena dipakai sebagai variabel kurva.

## Kurikulum 4 level (`content/levels/`) + generator soal (`gamification/generators/`)

```
MainLevel (judul saja: PreCalculus, Kalkulus Dasar, Menengah, Lanjut)
  └─ SkillNode = sub-level ─< Topic ─┬─< LessonSection (materi + grafik slider)
                                     └─< PracticeSession ×5 ─< QuestionTemplate (key generator)
UserSessionProgress (user × sesi: attempts, best_score, passed)
```

* Materi level ditulis di `levels/lN_*.py` (`MAIN_LEVEL`, `SUBLEVELS` → `topics` → `sections`).
* Soal sesi **tidak disimpan**: tiap sesi menunjuk generator (`@register(key, topic, tiers)`) di
  `generators/<level>/<topik>.py`. Server mengundi 10 soal dengan seed `user:sesi:percobaan`,
  sehingga tiap user mendapat angka berbeda dan penilaian bisa diulang di server (`gamification/sessions.py`).
* Menambah variasi soal cukup dengan menulis generator baru + `@register(...)`, lalu jalankan seed:
  template sesi diperbarui otomatis.
* Generator mengembalikan `prompt`, `correct`, `distractors`, `steps` (pembahasan), `graphs` (spec GraphLab di atas).
* Sesi I–III wajib (topik tuntas), Sesi IV–V bonus. Sesi n terbuka setelah sesi n−1 lulus.
* Tes `GeneratorTests` menjalankan setiap generator di setiap tingkat untuk 40 seed.
