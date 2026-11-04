"""
Sumber: 1_Materi_Umum_Kalkulus.pdf
"Materi Umum Kalkulus — Konsep dan rumus dasar untuk semua fakultas."

Berkas ini menjadi Tahap 1–5 pada skill tree SEMUA fakultas (faculty = None).
Soal untuk node-node ini berasal dari 3_Soal_Pembahasan_Dasar_Medium.pdf.
"""

from .helpers import param, readout, table, bullets

DOCUMENT = {
    "slug": "materi-umum",
    "filename": "1_Materi_Umum_Kalkulus.pdf",
    "title": "Materi Umum Kalkulus",
    "subtitle": "Konsep dan rumus dasar untuk semua fakultas",
    "category": "materi",
    "faculty": None,
    "order": 1,
}

# ─────────────────────────────────────────────────────────────────────────────
# Tahap 1 — Fungsi dan Limit
# ─────────────────────────────────────────────────────────────────────────────
LIMIT_SECTIONS = [
    {
        "heading": "Definisi dan sifat limit",
        "body_html": """
<p><strong>Definisi.</strong> lim<sub>x→a</sub> f(x) = L berarti nilai f(x) dapat dibuat sedekat mungkin ke L
dengan mengambil x cukup dekat ke a (x ≠ a). Limit ada jika <em>limit kiri = limit kanan</em>.</p>
<p><strong>Sifat limit.</strong> Jika lim f = L dan lim g = M, maka lim (f ± g) = L ± M, lim (f·g) = L·M,
lim (f/g) = L/M (M ≠ 0), lim c·f = c·L.</p>""",
    },
    {
        "heading": "Limit penting",
        "body_html": table(
            ["Limit penting", "Nilai", "Catatan"],
            [
                ["lim<sub>x→0</sub> sin x / x", "1", "Dasar turunan fungsi trigonometri"],
                ["lim<sub>x→0</sub> (1 − cos x)/x", "0", ""],
                ["lim<sub>x→0</sub> (eˣ − 1)/x", "1", "Dasar turunan eˣ"],
                ["lim<sub>n→∞</sub> (1 + 1/n)ⁿ", "e ≈ 2,71828", "Definisi bilangan e"],
                ["lim<sub>x→∞</sub> 1/xᵖ (p > 0)", "0", "Dipakai pada limit tak hingga"],
            ],
        ),
        "graphs": [
            {
                "type": "2d",
                "title": "lim x→0 sin(x)/x = 1",
                "x": [-8, 8],
                "y": [-0.5, 1.4],
                "params": [param("h", "Posisi x", -6, 6, 0.01, 1.5, "x")],
                "elements": [
                    {"type": "fn", "expr": "sin(x)/x", "color": "blue", "label": "sin(x)/x"},
                    {"type": "hline", "y": 1, "color": "gray", "dash": True},
                    {"type": "point", "x": 0, "y": 1, "hollow": True, "color": "blue"},
                    {"type": "point", "x": "h", "y": "sin(h)/h", "color": "red"},
                ],
                "readouts": [readout("x", "h", 3), readout("sin(x)/x", "sin(h)/h", 6)],
                "caption": "Geser x menuju 0: nilai sin(x)/x mendekati 1, walaupun di x = 0 fungsinya tidak terdefinisi.",
            },
            {
                "type": "2d",
                "title": "lim n→∞ (1 + 1/n)ⁿ = e",
                "x": [0, 60],
                "y": [1.8, 2.9],
                "xlabel": "n",
                "params": [param("n", "n", 1, 60, 1, 5, "n")],
                "elements": [
                    {"type": "fn", "expr": "(1+1/x)**x", "from": 0.5, "color": "blue", "label": "(1 + 1/n)ⁿ"},
                    {"type": "hline", "y": "e", "color": "green", "dash": True, "label": "e ≈ 2,71828"},
                    {"type": "point", "x": "n", "y": "(1+1/n)**n", "color": "red"},
                ],
                "readouts": [readout("(1 + 1/n)ⁿ", "(1+1/n)**n", 6), readout("Selisih terhadap e", "e-(1+1/n)**n", 6)],
            },
        ],
    },
    {
        "heading": "Bentuk tak tentu",
        "body_html": """
<p><strong>Bentuk tak tentu</strong> (0/0, ∞/∞, ∞ − ∞, 0·∞): coba</p>
<ol class="lesson-list">
  <li>faktorisasi,</li>
  <li>perkalian sekawan untuk akar,</li>
  <li>bagi dengan pangkat tertinggi saat x→∞,</li>
  <li>aturan L'Hôpital: lim f/g = lim f′/g′ bila bentuk 0/0 atau ∞/∞.</li>
</ol>""",
    },
    {
        "heading": "Kontinuitas",
        "body_html": """
<p><strong>Kontinuitas di x = a</strong> memerlukan tiga syarat: f(a) terdefinisi, lim<sub>x→a</sub> f(x) ada,
dan nilai limit sama dengan f(a).</p>
<p><strong>Teorema Nilai Antara:</strong> fungsi kontinu pada [a,b] mengambil semua nilai antara f(a) dan f(b).</p>""",
    },
]

# ─────────────────────────────────────────────────────────────────────────────
# Tahap 2 — Turunan dan aplikasinya
# ─────────────────────────────────────────────────────────────────────────────
DERIVATIVE_SECTIONS = [
    {
        "heading": "Definisi turunan",
        "body_html": """
<p><strong>Definisi.</strong> f′(x) = lim<sub>h→0</sub> [f(x+h) − f(x)]/h. Secara geometri f′(a) adalah
kemiringan garis singgung di x = a; secara fisika, laju perubahan sesaat.</p>""",
        "graphs": [
            {
                "type": "2d",
                "title": "Gambar 1. Turunan sebagai kemiringan garis singgung",
                "x": [-0.5, 4.2],
                "y": [-0.5, 8],
                "params": [
                    param("a", "Titik singgung a", 0, 4, 0.01, 3, "a"),
                    param("h", "Lebar selisih h", -2, 2, 0.01, 1, "h"),
                ],
                "elements": [
                    {"type": "fn", "expr": "0.5*(x-1)**2+0.5", "color": "blue", "label": "f(x)"},
                    {"type": "fn", "expr": "(0.5*(a-1)**2+0.5) + (a-1)*(x-a)", "color": "red", "dash": True,
                     "label": "garis singgung di x = a"},
                    {"type": "fn",
                     "expr": "(0.5*(a-1)**2+0.5) + ((0.5*(a+h-1)**2+0.5)-(0.5*(a-1)**2+0.5))/h*(x-a)",
                     "color": "green", "label": "garis sekan (a, a+h)"},
                    {"type": "point", "x": "a", "y": "0.5*(a-1)**2+0.5", "color": "red"},
                    {"type": "point", "x": "a+h", "y": "0.5*(a+h-1)**2+0.5", "color": "green"},
                ],
                "readouts": [
                    readout("Kemiringan sekan [f(a+h) − f(a)]/h", "((0.5*(a+h-1)**2+0.5)-(0.5*(a-1)**2+0.5))/h"),
                    readout("f′(a) (kemiringan singgung)", "a-1"),
                ],
                "caption": "f(x) = ½(x − 1)² + ½. Geser h menuju 0: garis sekan (hijau) berimpit dengan garis singgung (merah). "
                           "Itulah definisi turunan sebagai limit.",
            }
        ],
    },
    {
        "heading": "Tabel turunan dasar",
        "body_html": table(
            ["f(x)", "f′(x)", "f(x)", "f′(x)"],
            [
                ["c (konstanta)", "0", "eˣ", "eˣ"],
                ["xⁿ", "n·xⁿ⁻¹", "aˣ", "aˣ ln a"],
                ["sin x", "cos x", "ln x", "1/x"],
                ["cos x", "−sin x", "tan x", "sec²x"],
                ["arcsin x", "1/√(1−x²)", "arctan x", "1/(1+x²)"],
            ],
        ),
    },
    {
        "heading": "Aturan turunan",
        "body_html": """
<div class="formula-box"><code>(u ± v)′ = u′ ± v′</code><span>Aturan jumlah</span></div>
<div class="formula-box"><code>(uv)′ = u′v + uv′</code><span>Aturan hasil kali</span></div>
<div class="formula-box"><code>(u/v)′ = (u′v − uv′)/v²</code><span>Aturan hasil bagi</span></div>
<div class="formula-box"><code>[f(g(x))]′ = f′(g(x))·g′(x)</code><span>Aturan rantai</span></div>
<p><strong>Turunan implisit:</strong> turunkan kedua ruas terhadap x, ingat y = y(x).</p>""",
    },
    {
        "heading": "Aplikasi turunan",
        "body_html": bullets([
            "<strong>Garis singgung</strong> di (a, f(a)): y − f(a) = f′(a)(x − a).",
            "<strong>Titik kritis</strong>: f′(c) = 0 atau f′ tidak ada. <strong>Uji turunan pertama</strong>: "
            "f′ berubah + ke − → maksimum lokal; − ke + → minimum lokal. <strong>Uji turunan kedua</strong>: "
            "f″(c) &lt; 0 maksimum, f″(c) &gt; 0 minimum. Titik belok terjadi di tempat f″ berganti tanda (kecekungan berubah).",
            "<strong>Optimasi</strong>: (1) gambar dan beri variabel, (2) tulis fungsi tujuan, (3) kurangi menjadi satu "
            "variabel memakai kendala, (4) cari titik kritis dan periksa batas domain.",
            "<strong>Laju terkait</strong>: tulis hubungan antar besaran, turunkan terhadap waktu t, baru substitusi nilai sesaat.",
        ]),
        "graphs": [
            {
                "type": "2d",
                "title": "Gambar 2. Titik ekstrem lokal fungsi kubik: di sana f′ = 0",
                "x": [-3.2, 5.2],
                "y": [-40, 40],
                "params": [param("t", "Posisi garis singgung x", -3, 5, 0.01, 0, "x")],
                "elements": [
                    {"type": "fn", "expr": "x**3-3*x**2-9*x+5", "color": "blue", "label": "f(x) = x³ − 3x² − 9x + 5"},
                    {"type": "fn", "expr": "(t**3-3*t**2-9*t+5) + (3*t*t-6*t-9)*(x-t)", "color": "red", "dash": True,
                     "label": "garis singgung"},
                    {"type": "point", "x": -1, "y": 10, "color": "green", "label": "maks lokal (−1, 10)"},
                    {"type": "point", "x": 3, "y": -22, "color": "red", "label": "min lokal (3, −22)"},
                    {"type": "point", "x": "t", "y": "t**3-3*t**2-9*t+5", "color": "orange"},
                ],
                "readouts": [
                    readout("f′(x)", "3*t*t-6*t-9"),
                    readout("f″(x)", "6*t-6"),
                ],
                "caption": "Geser titik singgung: garis menjadi mendatar (f′ = 0) tepat di titik ekstrem. "
                           "Tanda f″ menentukan jenisnya.",
            }
        ],
    },
]

# ─────────────────────────────────────────────────────────────────────────────
# Tahap 3 — Integral dan aplikasinya
# ─────────────────────────────────────────────────────────────────────────────
INTEGRAL_SECTIONS = [
    {
        "heading": "Antiturunan & Teorema Dasar Kalkulus",
        "body_html": """
<p><strong>Antiturunan</strong> F dari f memenuhi F′ = f; ditulis ∫ f(x)dx = F(x) + C.</p>
<div class="formula-box"><code>∫<sub>a</sub><sup>b</sup> f(x)dx = F(b) − F(a)</code><span>Teorema Dasar Kalkulus</span></div>
<div class="formula-box"><code>d/dx ∫<sub>a</sub><sup>x</sup> f(t)dt = f(x)</code><span>Teorema Dasar Kalkulus (bagian kedua)</span></div>""",
    },
    {
        "heading": "Tabel integral dasar",
        "body_html": table(
            ["f(x)", "∫ f(x) dx", "f(x)", "∫ f(x) dx"],
            [
                ["xⁿ (n ≠ −1)", "xⁿ⁺¹/(n+1) + C", "1/x", "ln|x| + C"],
                ["eˣ", "eˣ + C", "aˣ", "aˣ/ln a + C"],
                ["sin x", "−cos x + C", "cos x", "sin x + C"],
                ["sec²x", "tan x + C", "1/(1+x²)", "arctan x + C"],
            ],
        ),
    },
    {
        "heading": "Teknik integrasi",
        "body_html": bullets([
            "<em>Substitusi</em>: misal u = g(x), ∫ f(g(x))g′(x)dx = ∫ f(u)du.",
            "<em>Parsial</em>: ∫ u dv = uv − ∫ v du (pilih u dengan urutan LIATE: Logaritma, Invers trigonometri, "
            "Aljabar, Trigonometri, Eksponen).",
            "<em>Pecahan parsial</em> untuk fungsi rasional.",
        ]),
    },
    {
        "heading": "Aplikasi integral",
        "body_html": bullets([
            "Luas antar kurva: ∫(atas − bawah)dx.",
            "Volume cakram/cincin: V = π∫(R² − r²)dx.",
            "Panjang kurva: L = ∫√(1 + (y′)²)dx.",
            "Nilai rata-rata: f<sub>rata</sub> = (1/(b−a))∫<sub>a</sub><sup>b</sup> f dx.",
        ]),
        "graphs": [
            {
                "type": "2d",
                "title": "Gambar 3. Integral sebagai limit jumlah Riemann",
                "x": [-0.1, 2.1],
                "y": [-0.1, 2.2],
                "params": [param("n", "Banyak persegi panjang n", 1, 60, 1, 4, "n")],
                "elements": [
                    {"type": "riemann", "id": "R", "expr": "x", "from": 0, "to": 2, "n": "n", "mode": "right", "color": "amber"},
                    {"type": "fn", "expr": "x", "color": "blue", "label": "f(x) = x"},
                ],
                "readouts": [
                    readout("Jumlah Riemann kanan", "R", 5),
                    readout("Nilai eksak ∫₀² x dx", "2", 5),
                    readout("Galat", "R-2", 5),
                ],
                "caption": "Perbesar n: jumlah luas persegi panjang mendekati luas eksak 2.",
            }
        ],
    },
]

# ─────────────────────────────────────────────────────────────────────────────
# Tahap 4 — Barisan dan deret
# ─────────────────────────────────────────────────────────────────────────────
SERIES_SECTIONS = [
    {
        "heading": "Uji kekonvergenan deret",
        "body_html": table(
            ["Deret", "Kekonvergenan"],
            [
                ["Geometri Σ arⁿ", "Konvergen jika |r| &lt; 1, jumlah = a/(1 − r)"],
                ["Deret-p Σ 1/nᵖ", "Konvergen jika p &gt; 1 (p = 1: harmonik, divergen)"],
                ["Uji suku ke-n", "Jika lim aₙ ≠ 0, deret divergen"],
                ["Uji rasio", "ρ = lim |aₙ₊₁/aₙ|; ρ &lt; 1 konvergen, ρ &gt; 1 divergen"],
                ["Deret berganti tanda (Leibniz)", "Konvergen jika |aₙ| menurun menuju 0"],
            ],
        ),
        "graphs": [
            {
                "type": "2d",
                "title": "Jumlah parsial deret geometri Σ rᵏ (a = 1)",
                "x": [-0.5, 30.5],
                "y": [-3, 12],
                "xlabel": "N",
                "params": [
                    param("r", "Rasio r", -1.2, 1.2, 0.01, 0.5, "r"),
                    param("N", "Banyak suku N", 1, 30, 1, 10, "N"),
                ],
                "elements": [
                    {"type": "iter", "id": "G", "init": {"k": 0, "s": 1}, "update": {"k": "k+1", "s": "s + r**(k+1)"},
                     "steps": "N", "px": "k", "py": "s", "color": "blue", "label": "jumlah parsial S_N"},
                    {"type": "hline", "y": "abs(r) < 1 ? 1/(1-r) : NaN", "color": "green", "dash": True,
                     "label": "a/(1 − r) (jika |r| < 1)"},
                ],
                "readouts": [
                    readout("S_N", "G.s", 5),
                    readout("a/(1 − r)", "abs(r) < 1 ? 1/(1-r) : NaN", 5),
                ],
                "caption": "Untuk |r| < 1 jumlah parsial menuju a/(1 − r). Coba r ≥ 1 atau r ≤ −1: deretnya divergen.",
            }
        ],
    },
    {
        "heading": "Deret Maclaurin",
        "body_html": table(
            ["Deret Maclaurin", "Berlaku untuk"],
            [
                ["eˣ = 1 + x + x²/2! + x³/3! + …", "semua x"],
                ["sin x = x − x³/3! + x⁵/5! − …", "semua x"],
                ["cos x = 1 − x²/2! + x⁴/4! − …", "semua x"],
                ["1/(1−x) = 1 + x + x² + …", "|x| &lt; 1"],
                ["ln(1+x) = x − x²/2 + x³/3 − …", "−1 &lt; x ≤ 1"],
            ],
        ),
        "graphs": [
            {
                "type": "2d",
                "title": "Hampiran Maclaurin untuk sin x",
                "x": [-9, 9],
                "y": [-2.5, 2.5],
                "params": [param("N", "Banyak suku", 1, 10, 1, 3, "N")],
                "elements": [
                    {"type": "fn", "expr": "sin(x)", "color": "blue", "label": "sin x"},
                    {"type": "fn", "expr": "sum(0, N-1, k => (-1)**k * x**(2*k+1) / fact(2*k+1))", "color": "red",
                     "dash": True, "label": "polinom Maclaurin ({{N}} suku)"},
                ],
                "readouts": [readout("Galat di x = 3", "abs(sin(3) - sum(0, N-1, k => (-1)**k * 3**(2*k+1) / fact(2*k+1)))", 6)],
                "caption": "Semakin banyak suku, polinom Maclaurin semakin dekat dengan sin x pada selang yang semakin lebar.",
            }
        ],
    },
]

# ─────────────────────────────────────────────────────────────────────────────
# Tahap 5 — Fungsi dua variabel (+ kesalahan yang sering terjadi)
# ─────────────────────────────────────────────────────────────────────────────
MULTIVAR_SECTIONS = [
    {
        "heading": "Turunan parsial, gradien, dan integral lipat",
        "body_html": """
<p><strong>Turunan parsial</strong> ∂f/∂x: turunkan terhadap x dengan y dianggap konstan (dan sebaliknya).</p>
<p><strong>Gradien</strong> ∇f = (∂f/∂x, ∂f/∂y) menunjuk arah kenaikan tercepat. <strong>Titik kritis</strong>: ∇f = 0.</p>
<p><strong>Uji turunan kedua</strong>: D = f<sub>xx</sub>f<sub>yy</sub> − (f<sub>xy</sub>)²; D &gt; 0 dan f<sub>xx</sub> &gt; 0 → minimum,
D &gt; 0 dan f<sub>xx</sub> &lt; 0 → maksimum, D &lt; 0 → titik pelana.</p>
<p><strong>Integral lipat</strong>: ∬<sub>D</sub> f dA dihitung sebagai integral berulang; gambar daerah D lebih dulu untuk
menentukan batas.</p>""",
        "graphs": [
            {
                "type": "3d",
                "title": "Gambar 4. Permukaan z = x² + b·y²",
                "extent": 2.2,
                "axes": [2, 2, 3],
                "params": [param("b", "Koefisien b", -1, 2, 0.05, 1, "b")],
                "surfaces": [
                    {"u": [-1.5, 1.5], "v": [-1.5, 1.5], "x": "u", "y": "v", "z": "(u*u + b*v*v)/2",
                     "color": "teal", "nu": 16, "nv": 16, "label": "z = x² + b·y² (skala z ½)"},
                ],
                "readouts": [
                    readout("D = f_xx·f_yy − f_xy² = 2·2b", "4*b", 3),
                ],
                "caption": "Untuk b = 1 diperoleh z = x² + y² (titik minimum). Geser b ke nilai negatif: D < 0 dan "
                           "permukaan berubah menjadi pelana. Sumbu z digambar dengan skala ½.",
            }
        ],
    },
    {
        "heading": "Kesalahan yang sering terjadi",
        "body_html": bullets([
            "Lupa konstanta C pada integral tak tentu, atau lupa mengganti batas saat substitusi integral tentu.",
            "Menulis (f·g)′ = f′·g′ (yang benar: f′g + fg′).",
            "Memakai L'Hôpital pada bentuk yang bukan 0/0 atau ∞/∞.",
            "Lupa aturan rantai pada fungsi komposisi, misalnya turunan sin(3x) adalah 3cos(3x), bukan cos(3x).",
            "Tidak memeriksa titik batas domain saat mencari maksimum atau minimum.",
            "Mengira deret konvergen hanya karena suku-sukunya menuju 0 (deret harmonik adalah contoh penyangkal).",
        ]),
    },
]

NODES = [
    {
        "slug": "umum-limit",
        "faculty": None,
        "stage_number": 1,
        "order": 1,
        "icon": "∞",
        "title": "Tahap 1: Fungsi dan Limit",
        "badge_label": "Materi Umum",
        "subtitle": "Definisi limit, limit penting, bentuk tak tentu, dan kontinuitas.",
        "summary_html": "Limit kiri/kanan, sifat limit, limit penting, bentuk tak tentu, kontinuitas.",
        "sections": LIMIT_SECTIONS,
    },
    {
        "slug": "umum-turunan",
        "faculty": None,
        "stage_number": 2,
        "order": 2,
        "icon": "📈",
        "title": "Tahap 2: Turunan dan Aplikasinya",
        "badge_label": "Materi Umum",
        "subtitle": "Definisi, tabel turunan, aturan turunan, garis singgung, ekstrem, optimasi, laju terkait.",
        "summary_html": "Kemiringan garis singgung, aturan rantai, titik kritis, optimasi, laju terkait.",
        "sections": DERIVATIVE_SECTIONS,
    },
    {
        "slug": "umum-integral",
        "faculty": None,
        "stage_number": 3,
        "order": 3,
        "icon": "∫",
        "title": "Tahap 3: Integral dan Aplikasinya",
        "badge_label": "Materi Umum",
        "subtitle": "Antiturunan, Teorema Dasar Kalkulus, substitusi, parsial, luas, volume, panjang kurva.",
        "summary_html": "Teorema Dasar Kalkulus, teknik integrasi, luas antar kurva, jumlah Riemann.",
        "sections": INTEGRAL_SECTIONS,
    },
    {
        "slug": "umum-deret",
        "faculty": None,
        "stage_number": 4,
        "order": 4,
        "icon": "Σ",
        "title": "Tahap 4: Barisan dan Deret",
        "badge_label": "Materi Umum",
        "subtitle": "Uji kekonvergenan dan deret Maclaurin.",
        "summary_html": "Deret geometri, deret-p, uji rasio, deret berganti tanda, deret Maclaurin.",
        "sections": SERIES_SECTIONS,
    },
    {
        "slug": "umum-dua-variabel",
        "faculty": None,
        "stage_number": 5,
        "order": 5,
        "icon": "🗻",
        "title": "Tahap 5: Fungsi Dua Variabel",
        "badge_label": "Materi Umum",
        "subtitle": "Turunan parsial, gradien, uji turunan kedua, integral lipat, dan kesalahan umum.",
        "summary_html": "Turunan parsial, gradien, titik pelana, integral lipat.",
        "sections": MULTIVAR_SECTIONS,
    },
]
