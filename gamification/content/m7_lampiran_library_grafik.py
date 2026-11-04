"""
Sumber: 7_Lampiran_Library_Grafik.pdf
"Daftar Library Grafik — Lampiran untuk pengembangan aplikasi."

Lampiran ini tidak masuk skill tree; ditampilkan sebagai bacaan referensi di
halaman Lesson (kind = 'reference').
"""

from .helpers import table, bullets

DOCUMENT = {
    "slug": "lampiran-library-grafik",
    "filename": "7_Lampiran_Library_Grafik.pdf",
    "title": "Daftar Library Grafik untuk Aplikasi",
    "subtitle": "Web (JavaScript) · Mobile · Backend Python · Rekomendasi kombinasi",
    "category": "lampiran",
    "faculty": None,
    "order": 7,
}

NOTE = ("<p class=\"lesson-note\">Daftar berikut dikelompokkan menurut platform. Lisensi dan status pemeliharaan ditulis "
        "berdasarkan pengetahuan saat penyusunan; <strong>periksa kembali versi dan lisensi terbaru</strong> di situs resmi "
        "masing-masing sebelum dipakai di produk.</p>")

SECTIONS = [
    {
        "heading": "E.1 Web (JavaScript)",
        "body_html": NOTE + table(
            ["Library", "Lisensi", "Kegunaan untuk kalkulus", "Catatan"],
            [
                ["Function Plot", "MIT", "Plot f(x) dari ekspresi teks, zoom/pan, garis singgung, anotasi.",
                 "Berbasis D3; ringan dan cocok untuk grafik fungsi 2D."],
                ["JSXGraph", "LGPL/MIT (periksa)", "Grafik interaktif: titik bisa digeser, slider, garis singgung, jumlah Riemann.",
                 "Sangat cocok untuk visualisasi konsep."],
                ["Plotly.js", "MIT", "Grafik 2D dan 3D: permukaan z=f(x,y), kontur, heatmap, scatter.",
                 "Bundle besar; ideal untuk turunan parsial dan gradient descent."],
                ["Chart.js", "MIT", "Garis, batang, radar: dashboard progres belajar dan statistik skor.",
                 "Mudah dipakai; kurang cocok untuk plot fungsi kontinu."],
                ["D3.js", "ISC", "Visualisasi kustom berbasis SVG (animasi konvergensi, jumlah Riemann).",
                 "Fleksibel, kurva belajar tinggi."],
                ["Mafs", "MIT", "Komponen React untuk grafik matematika interaktif.", "Khusus React."],
                ["Three.js", "MIT", "Rendering 3D WebGL: benda putar, permukaan, medan vektor.",
                 "Butuh kode lebih banyak daripada Plotly."],
                ["Desmos API", "Perlu API key", "Kalkulator grafik tertanam yang sudah dikenal mahasiswa.",
                 "Cek syarat penggunaan komersial."],
                ["GeoGebra Apps API", "Non-komersial gratis", "Applet grafik, geometri, dan CAS tertanam.",
                 "Penggunaan komersial perlu lisensi."],
                ["KaTeX / MathJax", "MIT / Apache-2.0", "Render rumus LaTeX pada soal dan pembahasan.",
                 "KaTeX lebih cepat; MathJax lebih lengkap."],
                ["math.js", "Apache-2.0", "Parsing dan evaluasi ekspresi yang diketik pengguna.", "Dipasangkan dengan Function Plot."],
            ],
        ),
    },
    {
        "heading": "E.2 Mobile",
        "body_html": table(
            ["Platform", "Library", "Lisensi", "Catatan"],
            [
                ["Flutter", "fl_chart", "MIT", "Garis, batang, scatter; mendukung animasi dan sentuhan."],
                ["Flutter", "Syncfusion Charts", "Komunitas/komersial", "Fitur banyak; periksa syarat lisensi komunitas."],
                ["Android (Compose)", "Vico", "Apache-2.0", "Grafik modern untuk Jetpack Compose."],
                ["Android (View)", "MPAndroidChart", "Apache-2.0", "Populer; pemeliharaan kurang aktif, pertimbangkan alternatif."],
                ["iOS", "Swift Charts", "Bawaan Apple", "Tersedia mulai iOS 16; integrasi SwiftUI."],
                ["iOS", "DGCharts", "Apache-2.0", "Penerus library Charts."],
                ["React Native", "Victory Native, react-native-gifted-charts", "MIT", "Grafik 2D umum."],
                ["React Native", "react-native-skia", "MIT", "Menggambar kurva fungsi dengan performa tinggi."],
                ["Lintas platform", "WebView + JSXGraph/Plotly/KaTeX", "Sesuai library", "Satu kode grafik dipakai di web dan mobile."],
            ],
        ),
    },
    {
        "heading": "E.3 Backend / pembuatan konten (Python)",
        "body_html": table(
            ["Library", "Lisensi", "Kegunaan", "Catatan"],
            [
                ["Matplotlib", "Lisensi permisif (PSF)", "Membuat gambar statis untuk bank soal dan pembahasan.",
                 "Gambar PNG/SVG disajikan lewat CDN."],
                ["SymPy", "BSD", "Membangkitkan soal acak, menurunkan dan mengintegralkan simbolik, membuat kunci jawaban otomatis.",
                 "Dipakai untuk memverifikasi jawaban modul ini."],
                ["Plotly (Python)", "MIT", "Grafik interaktif yang diekspor sebagai HTML/JSON.", "Cocok untuk konten 3D."],
                ["Manim", "MIT", "Animasi video penjelasan konsep (gaya 3Blue1Brown).", "Rendering lebih berat."],
            ],
        ),
    },
    {
        "heading": "E.4 Rekomendasi kombinasi",
        "body_html": bullets([
            "<strong>Aplikasi web:</strong> KaTeX (rumus) + Function Plot atau JSXGraph (grafik 2D interaktif) + Plotly.js "
            "(3D, kontur, gradient descent) + Chart.js (dashboard progres).",
            "<strong>Aplikasi Flutter:</strong> fl_chart untuk statistik, dan WebView berisi JSXGraph/Plotly untuk grafik fungsi "
            "interaktif; rumus dengan paket render LaTeX.",
            "<strong>Backend soal:</strong> SymPy untuk membangkitkan soal bervariasi dan kunci jawaban, Matplotlib untuk gambar "
            "pembahasan, simpan sebagai aset statis.",
            "<strong>Pemetaan fakultas:</strong> FT → grafik fisika &amp; benda putar (Plotly 3D/Three.js); FMIPA → ε–δ, deret, "
            "Taylor (JSXGraph); Fasilkom → kontur loss, kurva sigmoid, kompleksitas (Plotly + Chart.js).",
        ]) + "<p class=\"lesson-note\">Catatan: modul ini adalah materi belajar dan telah diperiksa ulang secara komputasi, "
             "namun tetap disarankan ditinjau oleh dosen pengampu sebelum dipublikasikan di aplikasi.</p>",
    },
]

NODES = [
    {
        "slug": "lampiran-library-grafik",
        "faculty": None,
        "kind": "reference",
        "stage_number": 0,
        "order": 99,
        "icon": "📚",
        "title": "Lampiran: Daftar Library Grafik",
        "badge_label": "Lampiran",
        "subtitle": "Library grafik untuk web, mobile, dan backend Python beserta rekomendasi kombinasi.",
        "summary_html": "Referensi library grafik untuk pengembangan aplikasi.",
        "sections": SECTIONS,
    }
]
