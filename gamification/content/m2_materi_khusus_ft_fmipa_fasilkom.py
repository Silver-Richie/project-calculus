"""
Sumber: 2_Materi_Khusus_FT_FMIPA_Fasilkom.pdf
"Materi Khusus per Fakultas — topik lanjutan yang paling sering dipakai oleh
masing-masing fakultas. Prasyarat: materi umum kalkulus."

Berkas ini dipecah per fakultas menjadi Tahap 6–8 (bagian A = FT, B = FMIPA,
C = Fasilkom). Soal untuk tiap tahap diambil dari berkas soal fakultasnya
(4_…FT, 5_…FMIPA, 6_…Fasilkom) sesuai tingkat Mudah / Sedang / Sulit.
"""

from .helpers import param, readout, table

DOCUMENT = {
    "slug": "materi-khusus",
    "filename": "2_Materi_Khusus_FT_FMIPA_Fasilkom.pdf",
    "title": "Materi Khusus Kalkulus",
    "subtitle": "Fakultas Teknik · FMIPA · Fasilkom",
    "category": "materi",
    "faculty": None,  # berisi tiga fakultas; setiap node diberi fakultasnya sendiri
    "order": 2,
}

# ═════════════════════════════════════════════════════════════════════════════
# A. Fakultas Teknik (FT): Kalkulus untuk Pemodelan Rekayasa
# ═════════════════════════════════════════════════════════════════════════════
FT_INTRO = [
    {
        "heading": "Peta topik FT",
        "body_html": """
<p><strong>Peta topik:</strong> laju terkait dan optimasi, usaha, volume dan luas permukaan benda putar,
nilai rata-rata dan RMS, pusat massa, persamaan diferensial orde 1.</p>""",
    },
    {
        "heading": "Rumus kunci FT",
        "body_html": table(
            ["Konsep", "Rumus", "Contoh penggunaan"],
            [
                ["Usaha", "W = ∫ F(x) dx", "Pegas, pompa, mengangkat kabel"],
                ["Luas permukaan putar", "S = 2π∫ y √(1+(y′)²) dx", "Tangki, kerucut, kubah"],
                ["Nilai rata-rata", "f<sub>rata</sub> = (1/(b−a))∫ f dx", "Suhu rata-rata, beban rata-rata"],
                ["Nilai RMS", "f<sub>rms</sub> = √[(1/T)∫ f² dt]", "Tegangan dan arus AC"],
                ["Pusat massa (1D)", "x̄ = ∫xρ(x)dx / ∫ρ(x)dx", "Balok tak homogen"],
                ["PD terpisahkan", "dy/dx = g(x)h(y) → ∫dy/h = ∫g dx", "Pendinginan, peluruhan, rangkaian RC"],
                ["PD linear orde 1", "y′ + p(x)y = q(x); faktor integrasi μ = e<sup>∫p dx</sup>", "Rangkaian RL, pencampuran"],
            ],
        ),
    },
]

FT_EXAMPLES = [
    {
        "heading": "Contoh 1 (RMS)",
        "body_html": """
<p>Arus i(t) = I<sub>m</sub> sin ωt dengan periode T. Karena rata-rata sin² adalah 1/2,
i<sub>rms</sub> = √(I<sub>m</sub>²/2) = I<sub>m</sub>/√2 ≈ 0,707 I<sub>m</sub>.</p>""",
        "graphs": [
            {
                "type": "2d",
                "title": "Arus AC dan nilai RMS-nya",
                "x": [0, 12.6],
                "y": [-5.5, 5.5],
                "xlabel": "t",
                "params": [
                    param("Im", "Amplitudo Iₘ", 0.5, 5, 0.1, 2, "Iₘ"),
                    param("w", "Frekuensi sudut ω", 0.5, 3, 0.05, 1, "ω"),
                ],
                "elements": [
                    {"type": "fn", "expr": "Im*sin(w*x)", "color": "blue", "label": "i(t) = Iₘ sin ωt"},
                    {"type": "fn", "expr": "(Im*sin(w*x))**2", "color": "orange", "label": "i²(t)"},
                    {"type": "hline", "y": "Im/sqrt(2)", "color": "red", "dash": True, "label": "i_rms = Iₘ/√2"},
                    {"type": "hline", "y": "Im*Im/2", "color": "amber", "dash": True, "label": "rata-rata i² = Iₘ²/2"},
                ],
                "readouts": [readout("i_rms", "Im/sqrt(2)"), readout("i_rms / Iₘ", "1/sqrt(2)")],
                "caption": "Ubah Iₘ dan ω: rasio i_rms/Iₘ selalu 0,707 — tidak bergantung pada frekuensi.",
            }
        ],
    },
    {
        "heading": "Contoh 2 (PD terpisahkan)",
        "body_html": """
<p>dy/dx = 2xy, y(0) = 1. Pisahkan: dy/y = 2x dx → ln|y| = x² + c → y = Ae<sup>x²</sup>.
Dengan y(0) = 1 diperoleh A = 1, jadi y = e<sup>x²</sup>.</p>""",
        "graphs": [
            {
                "type": "2d",
                "title": "Keluarga solusi y = A·e^(x²)",
                "x": [-1.6, 1.6],
                "y": [-6, 12],
                "params": [param("A", "Syarat awal y(0) = A", -3, 3, 0.1, 1, "A")],
                "elements": [
                    {"type": "fn", "expr": "A*exp(x*x)", "color": "blue", "label": "y = A·e^(x²)"},
                    {"type": "point", "x": 0, "y": "A", "color": "red", "label": "y(0) = {{A}}"},
                ],
                "readouts": [readout("y(1)", "A*exp(1)")],
                "caption": "Setiap nilai A memberi satu solusi; syarat awal y(0) memilih kurva yang tepat.",
            }
        ],
    },
    {
        "heading": "Contoh 3 (nilai rata-rata)",
        "body_html": """
<p>Rata-rata f(x) = x² pada [0, 3] adalah (1/3)∫<sub>0</sub><sup>3</sup>x²dx = (1/3)(9) = 3.</p>""",
        "graphs": [
            {
                "type": "2d",
                "title": "Nilai rata-rata x² pada [0, b]",
                "x": [-0.2, 5.2],
                "y": [-0.5, 26],
                "params": [param("b", "Ujung selang b", 0.5, 5, 0.05, 3, "b")],
                "elements": [
                    {"type": "fill", "upper": "x*x", "from": 0, "to": "b", "color": "amber"},
                    {"type": "fn", "expr": "x*x", "color": "blue", "label": "f(x) = x²"},
                    {"type": "segment", "x1": 0, "y1": "b*b/3", "x2": "b", "y2": "b*b/3", "color": "red", "width": 3,
                     "label": "f_rata = b²/3"},
                ],
                "readouts": [readout("f_rata", "b*b/3")],
                "caption": "Luas persegi panjang setinggi f_rata sama dengan luas di bawah kurva.",
            }
        ],
    },
    {
        "heading": "Model pendinginan (PD terpisahkan)",
        "body_html": "<p>Hukum pendinginan Newton dT/dt = −k(T − T<sub>ruang</sub>) menghasilkan "
                     "T(t) = T<sub>ruang</sub> + (T₀ − T<sub>ruang</sub>)e<sup>−kt</sup>.</p>",
        "graphs": [
            {
                "type": "2d",
                "title": "Gambar 1. Model pendinginan eksponensial",
                "x": [0, 40],
                "y": [15, 95],
                "xlabel": "t (menit)",
                "ylabel": "T (°C)",
                "params": [
                    param("k", "Konstanta k", 0.01, 0.3, 0.001, 0.0693, "k"),
                    param("T0", "Suhu awal T₀", 50, 95, 1, 85, "T₀"),
                    param("Ta", "Suhu ruang", 15, 35, 1, 25, "T_ruang"),
                ],
                "elements": [
                    {"type": "fn", "expr": "Ta + (T0-Ta)*exp(-k*x)", "from": 0, "color": "blue", "label": "T(t)"},
                    {"type": "hline", "y": "Ta", "color": "gray", "dash": True, "label": "suhu ruang"},
                ],
                "readouts": [readout("T(10)", "Ta + (T0-Ta)*exp(-k*10)", 3), readout("Waktu paruh selisih ln2/k", "ln(2)/k", 3)],
            }
        ],
    },
]

FT_ADVANCED = [
    {
        "heading": "Volume benda putar dengan metode cincin",
        "body_html": "<p>Daerah antara y = √x (luar) dan y = x² (dalam) pada 0 ≤ x ≤ 1 diputar mengelilingi sumbu x: "
                     "V = π∫(R² − r²)dx = 3π/10.</p>",
        "graphs": [
            {
                "type": "3d",
                "title": "Gambar 2. Benda putar: V = 3π/10",
                "extent": 1.2,
                "axes": [1.3, 1.2, 1.2],
                "yaw": 15,
                "tilt": 20,
                "params": [param("n", "Pangkat kurva dalam y = xⁿ", 1.2, 5, 0.1, 2, "n")],
                "surfaces": [
                    {"u": [0, 1], "v": [0, "2*pi"], "x": "u", "y": "sqrt(u)*cos(v)", "z": "sqrt(u)*sin(v)",
                     "color": "red", "nu": 14, "nv": 24, "label": "permukaan luar (y = √x)"},
                    {"u": [0, 1], "v": [0, "2*pi"], "x": "u", "y": "u**n*cos(v)", "z": "u**n*sin(v)",
                     "color": "blue", "nu": 14, "nv": 24, "label": "rongga dalam (y = xⁿ)"},
                ],
                "readouts": [readout("V = π(1/2 − 1/(2n+1))", "pi*(1/2 - 1/(2*n+1))", 5)],
            }
        ],
    },
    {
        "heading": "Strategi FT",
        "body_html": "<p><strong>Strategi:</strong> tulis model dan satuan terlebih dahulu; cek dimensi jawaban "
                     "(misalnya usaha dalam joule); gambar sketsa untuk soal volume dan optimasi.</p>",
    },
]

# ═════════════════════════════════════════════════════════════════════════════
# B. Fakultas MIPA: Analisis dan Ketelitian Konsep
# ═════════════════════════════════════════════════════════════════════════════
FMIPA_INTRO = [
    {
        "heading": "Peta topik FMIPA",
        "body_html": """
<p><strong>Peta topik:</strong> definisi limit ε–δ, teorema (Nilai Antara, Rolle, Nilai Rata-rata), deret dan uji
kekonvergenan, Taylor dengan sisa, integral tak wajar, integral lipat dan koordinat polar.</p>""",
    },
    {
        "heading": "Pernyataan dan rumus kunci FMIPA",
        "body_html": table(
            ["Konsep", "Pernyataan / rumus"],
            [
                ["Limit ε–δ", "lim<sub>x→a</sub> f(x) = L jika ∀ε &gt; 0 ∃δ &gt; 0: 0 &lt; |x−a| &lt; δ ⇒ |f(x)−L| &lt; ε"],
                ["Teorema Rolle", "f kontinu di [a,b], terdiferensial di (a,b), f(a) = f(b) ⇒ ∃c: f′(c) = 0"],
                ["Teorema Nilai Rata-rata", "∃c ∈ (a,b): f′(c) = [f(b) − f(a)]/(b − a)"],
                ["Sisa Taylor (Lagrange)", "R<sub>n</sub>(x) = f<sup>(n+1)</sup>(c)/(n+1)! · (x − a)<sup>n+1</sup>"],
                ["Integral tak wajar", "∫<sub>1</sub><sup>∞</sup> 1/xᵖ dx konvergen ⇔ p &gt; 1"],
                ["Koordinat polar", "x = r cos θ, y = r sin θ, dA = r dr dθ"],
                ["Uji banding", "0 ≤ aₙ ≤ bₙ: Σbₙ konvergen ⇒ Σaₙ konvergen"],
            ],
        ),
    },
]

FMIPA_EXAMPLES = [
    {
        "heading": "Contoh 1 (Teorema Nilai Rata-rata)",
        "body_html": "<p>f(x) = x² pada [1, 3]: [f(3) − f(1)]/2 = (9 − 1)/2 = 4. Karena f′(c) = 2c = 4, maka c = 2 ∈ (1, 3).</p>",
        "graphs": [
            {
                "type": "2d",
                "title": "Teorema Nilai Rata-rata untuk f(x) = x²",
                "x": [-0.5, 4.5],
                "y": [-1, 18],
                "params": [
                    param("a", "Ujung kiri a", 0, 2, 0.05, 1, "a"),
                    param("b", "Ujung kanan b", 2.2, 4, 0.05, 3, "b"),
                ],
                "elements": [
                    {"type": "fn", "expr": "x*x", "color": "blue", "label": "f(x) = x²"},
                    {"type": "segment", "x1": "a", "y1": "a*a", "x2": "b", "y2": "b*b", "color": "green", "label": "garis sekan"},
                    {"type": "fn", "expr": "((a+b)/2)**2 + (a+b)*(x-(a+b)/2)", "color": "red", "dash": True,
                     "label": "garis singgung di c (sejajar sekan)"},
                    {"type": "point", "x": "(a+b)/2", "y": "((a+b)/2)**2", "color": "red", "label": "c = {{(a+b)/2}}"},
                    {"type": "point", "x": "a", "y": "a*a", "color": "green"},
                    {"type": "point", "x": "b", "y": "b*b", "color": "green"},
                ],
                "readouts": [
                    readout("Kemiringan sekan [f(b) − f(a)]/(b − a)", "(b*b-a*a)/(b-a)"),
                    readout("c", "(a+b)/2"),
                    readout("f′(c) = 2c", "a+b"),
                ],
            }
        ],
    },
    {
        "heading": "Contoh 2 (integral tak wajar)",
        "body_html": "<p>∫<sub>1</sub><sup>∞</sup> x<sup>−2</sup>dx = lim<sub>b→∞</sub> [−1/x]<sub>1</sub><sup>b</sup> = lim (1 − 1/b) = 1 (konvergen).</p>",
        "graphs": [
            {
                "type": "2d",
                "title": "∫₁ᵇ 1/xᵖ dx saat b membesar",
                "x": [0.5, 30],
                "y": [-0.1, 1.2],
                "params": [
                    param("p", "Pangkat p", 0.5, 3, 0.05, 2, "p"),
                    param("b", "Batas atas b", 1, 30, 0.1, 10, "b"),
                ],
                "elements": [
                    {"type": "fill", "upper": "x**(-p)", "from": 1, "to": "b", "color": "amber"},
                    {"type": "fn", "expr": "x**(-p)", "from": 0.5, "color": "blue", "label": "1/xᵖ"},
                ],
                "readouts": [
                    readout("∫₁ᵇ 1/xᵖ dx", "abs(p-1) < 1e-9 ? ln(b) : (1 - b**(1-p))/(p-1)", 5),
                    readout("Limit b→∞ (jika p > 1)", "p > 1 ? 1/(p-1) : inf", 5),
                ],
                "caption": "Untuk p > 1 luasnya menuju 1/(p − 1); untuk p ≤ 1 luas terus membesar (divergen).",
            }
        ],
    },
    {
        "heading": "Contoh 3 (koordinat polar)",
        "body_html": "<p>∬<sub>ℝ²</sub> e<sup>−(x²+y²)</sup> dA = ∫<sub>0</sub><sup>2π</sup>∫<sub>0</sub><sup>∞</sup> e<sup>−r²</sup> r dr dθ = 2π · (1/2) = π. "
                     "Akibatnya ∫<sub>−∞</sub><sup>∞</sup> e<sup>−x²</sup>dx = √π.</p>",
        "graphs": [
            {
                "type": "2d",
                "title": "Luas di bawah e^(−a·x²) = √(π/a)",
                "x": [-3.5, 3.5],
                "y": [-0.05, 1.15],
                "params": [param("a", "Koefisien a", 0.3, 4, 0.05, 1, "a")],
                "elements": [
                    {"type": "fill", "upper": "exp(-a*x*x)", "from": -3.5, "to": 3.5, "color": "amber"},
                    {"type": "fn", "expr": "exp(-a*x*x)", "color": "blue", "label": "e^(−a x²)"},
                ],
                "readouts": [readout("√(π/a)", "sqrt(pi/a)", 5)],
                "caption": "Dengan a = 1 diperoleh √π ≈ 1,77245.",
            }
        ],
    },
]

FMIPA_ADVANCED = [
    {
        "heading": "Ilustrasi definisi ε–δ",
        "body_html": "<p>Untuk lim<sub>x→2</sub> x² = 4: setiap pita ε di sekitar 4 (sumbu y) harus dapat dijawab "
                     "dengan pita δ di sekitar 2 (sumbu x).</p>",
        "graphs": [
            {
                "type": "2d",
                "title": "Gambar 3. Bukti ε–δ untuk lim x² = 4 (x→2)",
                "x": [1, 3],
                "y": [0.5, 9.5],
                "params": [param("eps", "ε", 0.05, 3, 0.01, 1, "ε")],
                "elements": [
                    {"type": "hband", "from": "4-eps", "to": "4+eps", "color": "amber"},
                    {"type": "vband", "from": "2-min(1,eps/5)", "to": "2+min(1,eps/5)", "color": "green"},
                    {"type": "fn", "expr": "x*x", "color": "blue", "label": "f(x) = x²"},
                    {"type": "point", "x": 2, "y": 4, "color": "red"},
                ],
                "readouts": [readout("δ = min(1, ε/5)", "min(1,eps/5)", 4)],
            }
        ],
    },
    {
        "heading": "Hampiran Maclaurin",
        "body_html": "<p>Makin tinggi orde polinom Taylor, makin dekat hampirannya ke fungsi asli.</p>",
        "graphs": [
            {
                "type": "2d",
                "title": "Gambar 4. Hampiran Maclaurin untuk e^(−x²)",
                "x": [0, 2],
                "y": [-0.6, 1.2],
                "params": [param("N", "Banyak suku", 1, 10, 1, 5, "N")],
                "elements": [
                    {"type": "fn", "expr": "exp(-x*x)", "color": "blue", "label": "e^(−x²)"},
                    {"type": "fn", "expr": "sum(0, N-1, k => (-1)**k * x**(2*k) / fact(k))", "color": "red", "dash": True,
                     "label": "Taylor orde {{2*N-2}}"},
                ],
            }
        ],
    },
    {
        "heading": "Strategi FMIPA",
        "body_html": "<p><strong>Strategi:</strong> pada pembuktian, tulis dulu apa yang diketahui dan apa yang harus "
                     "ditunjukkan; pada deret, sebutkan nama uji yang dipakai dan periksa syaratnya; selalu periksa "
                     "titik ujung interval konvergensi.</p>",
    },
]

# ═════════════════════════════════════════════════════════════════════════════
# C. Fakultas Ilmu Komputer (Fasilkom): Kalkulus untuk Komputasi dan AI
# ═════════════════════════════════════════════════════════════════════════════
FASILKOM_INTRO = [
    {
        "heading": "Peta topik Fasilkom",
        "body_html": """
<p><strong>Peta topik:</strong> gradien dan gradient descent, aturan rantai pada backpropagation, fungsi aktivasi
dan softmax, notasi asimptotik lewat limit, integrasi numerik, metode Newton–Raphson, probabilitas kontinu.</p>""",
    },
    {
        "heading": "Rumus kunci Fasilkom",
        "body_html": table(
            ["Konsep", "Rumus", "Penggunaan"],
            [
                ["Gradient descent", "θ ← θ − η ∇L(θ)", "Melatih model; η = laju belajar"],
                ["Backpropagation", "∂L/∂w = ∂L/∂y · ∂y/∂z · ∂z/∂w", "Aturan rantai pada jaringan saraf"],
                ["Sigmoid", "σ(z) = 1/(1+e<sup>−z</sup>); σ′ = σ(1−σ)", "Klasifikasi biner"],
                ["Tanh", "tanh′(z) = 1 − tanh²(z)", "Aktivasi simetris"],
                ["ReLU", "max(0,z); turunan 0 (z&lt;0) atau 1 (z&gt;0)", "Aktivasi jaringan dalam"],
                ["Softmax + log-loss", "∂L/∂z<sub>k</sub> = p<sub>k</sub> − y<sub>k</sub>", "Klasifikasi multikelas"],
                ["Notasi asimptotik", "lim f/g = c ∈ (0,∞) ⇒ f = Θ(g)", "Analisis algoritma"],
                ["Trapesium", "T = (h/2)[f₀ + 2f₁ + … + 2f<sub>n−1</sub> + f<sub>n</sub>]; |E| ≤ (b−a)h²max|f″|/12", "Integral numerik"],
                ["Newton–Raphson", "x<sub>n+1</sub> = x<sub>n</sub> − f(x<sub>n</sub>)/f′(x<sub>n</sub>)", "Mencari akar secara iteratif"],
                ["Fungsi kepadatan", "f(x) ≥ 0 dan ∫f dx = 1; E[X] = ∫x f(x)dx", "Probabilitas kontinu"],
            ],
        ),
    },
]

FASILKOM_EXAMPLES = [
    {
        "heading": "Contoh 1 (Newton–Raphson)",
        "body_html": "<p>Hampiri √2 sebagai akar f(x) = x² − 2, x₀ = 1: x₁ = 1 − (−1)/2 = 1,5; x₂ = 1,5 − 0,25/3 ≈ 1,41667; "
                     "x₃ ≈ 1,41422 (nilai sebenarnya 1,41421…).</p>",
        "graphs": [
            {
                "type": "2d",
                "title": "Newton–Raphson untuk f(x) = x² − c",
                "x": [-0.5, 4.5],
                "y": [-3, 8],
                "params": [
                    param("c", "Bilangan c (mencari √c)", 0.5, 9, 0.1, 2, "c"),
                    param("x0", "Tebakan awal x₀", 0.3, 4, 0.01, 1, "x₀"),
                    param("k", "Banyak iterasi", 0, 6, 1, 3, "k"),
                ],
                "elements": [
                    {"type": "fn", "expr": "x*x-c", "color": "blue", "label": "f(x) = x² − c"},
                    {"type": "iter", "id": "NR", "init": {"x": "x0"}, "update": {"x": "x - (x*x-c)/(2*x)"}, "steps": "k",
                     "px": "x", "py": "0", "color": "red", "label": "iterasi xₙ"},
                    {"type": "vline", "x": "sqrt(c)", "color": "green", "dash": True, "label": "√c"},
                ],
                "readouts": [readout("xₖ", "NR.x", 6), readout("√c", "sqrt(c)", 6), readout("Galat", "abs(NR.x - sqrt(c))", 8)],
            }
        ],
    },
    {
        "heading": "Contoh 2 (backpropagation satu neuron)",
        "body_html": """
<p>z = wx + b, y = σ(z), L = (y − t)². Untuk w = 0,5, b = 0, x = 2, t = 1: z = 1, y ≈ 0,7311,
σ′(1) = y(1−y) ≈ 0,1966. ∂L/∂w = 2(y−t)·σ′(z)·x = 2(−0,2689)(0,1966)(2) ≈ −0,2115.
Gradien negatif berarti w perlu dinaikkan.</p>""",
        "graphs": [
            {
                "type": "2d",
                "title": "Kerugian L(w) = (σ(2w) − 1)² dan gradiennya",
                "x": [-3, 3],
                "y": [-0.1, 1.05],
                "xlabel": "w",
                "params": [param("w", "Bobot w", -3, 3, 0.01, 0.5, "w")],
                "elements": [
                    {"type": "fn", "expr": "(sigmoid(2*x)-1)**2", "color": "blue", "label": "L(w)"},
                    {"type": "fn", "expr": "(sigmoid(2*w)-1)**2 + 2*(sigmoid(2*w)-1)*sigmoid(2*w)*(1-sigmoid(2*w))*2*(x-w)",
                     "color": "red", "dash": True, "label": "garis singgung (kemiringan = ∂L/∂w)"},
                    {"type": "point", "x": "w", "y": "(sigmoid(2*w)-1)**2", "color": "red"},
                ],
                "readouts": [
                    readout("y = σ(2w)", "sigmoid(2*w)"),
                    readout("∂L/∂w", "2*(sigmoid(2*w)-1)*sigmoid(2*w)*(1-sigmoid(2*w))*2"),
                ],
            }
        ],
    },
    {
        "heading": "Contoh 3 (distribusi eksponensial)",
        "body_html": "<p>f(x) = λe<sup>−λx</sup>, x ≥ 0. ∫<sub>0</sub><sup>∞</sup> λe<sup>−λx</sup>dx = 1 (valid sebagai kepadatan) "
                     "dan E[X] = ∫<sub>0</sub><sup>∞</sup> xλe<sup>−λx</sup>dx = 1/λ (integral parsial).</p>",
        "graphs": [
            {
                "type": "2d",
                "title": "Kepadatan eksponensial f(x) = λe^(−λx)",
                "x": [0, 6],
                "y": [-0.05, 3.1],
                "params": [
                    param("lam", "Laju λ", 0.3, 3, 0.05, 1, "λ"),
                    param("b", "Batas atas b", 0, 6, 0.05, 2, "b"),
                ],
                "elements": [
                    {"type": "fill", "upper": "lam*exp(-lam*x)", "from": 0, "to": "b", "color": "amber"},
                    {"type": "fn", "expr": "lam*exp(-lam*x)", "from": 0, "color": "blue", "label": "f(x)"},
                    {"type": "vline", "x": "1/lam", "color": "red", "dash": True, "label": "E[X] = 1/λ"},
                ],
                "readouts": [readout("P(X ≤ b) = 1 − e^(−λb)", "1-exp(-lam*b)"), readout("E[X]", "1/lam")],
            }
        ],
    },
    {
        "heading": "Sigmoid dan turunannya",
        "body_html": "<p>σ′(z) = σ(z)(1 − σ(z)) mencapai maksimum 1/4 di z = 0.</p>",
        "graphs": [
            {
                "type": "2d",
                "title": "Gambar 5. Sigmoid dan turunannya",
                "x": [-8, 8],
                "y": [-0.05, 1.05],
                "params": [param("z", "Titik z", -8, 8, 0.05, 0, "z")],
                "elements": [
                    {"type": "fn", "expr": "sigmoid(x)", "color": "blue", "label": "σ(x)"},
                    {"type": "fn", "expr": "sigmoid(x)*(1-sigmoid(x))", "color": "red", "label": "σ′(x) = σ(x)(1 − σ(x))"},
                    {"type": "point", "x": "z", "y": "sigmoid(z)", "color": "blue"},
                    {"type": "point", "x": "z", "y": "sigmoid(z)*(1-sigmoid(z))", "color": "red"},
                ],
                "readouts": [readout("σ(z)", "sigmoid(z)"), readout("σ′(z)", "sigmoid(z)*(1-sigmoid(z))")],
            }
        ],
    },
]

FASILKOM_ADVANCED = [
    {
        "heading": "Gradient descent pada garis kontur",
        "body_html": "<p>f(x, y) = x² + 4y², mulai dari (4, 1). Arah y yang lebih curam membatasi laju belajar η.</p>",
        "graphs": [
            {
                "type": "2d",
                "title": "Gambar 6. Gradient descent, f = x² + 4y²",
                "x": [-5, 5],
                "y": [-2.5, 2.5],
                "params": [
                    param("eta", "Laju belajar η", 0.01, 0.3, 0.005, 0.1, "η"),
                    param("k", "Banyak iterasi", 0, 25, 1, 12, "k"),
                ],
                "elements": [
                    *[{"type": "param", "t": [0, "2*pi"], "x": f"sqrt({c})*cos(t)", "y": f"sqrt({c})/2*sin(t)",
                       "color": "#BFDBFE", "width": 1.2} for c in (1, 4, 9, 16, 25)],
                    {"type": "iter", "id": "GD", "init": {"x": 4, "y": 1}, "update": {"x": "x - eta*2*x", "y": "y - eta*8*y"},
                     "steps": "k", "color": "red", "label": "lintasan gradient descent"},
                ],
                "readouts": [readout("xₖ", "GD.x"), readout("yₖ", "GD.y"), readout("|1 − 8η| (harus < 1)", "abs(1-8*eta)")],
            }
        ],
    },
    {
        "heading": "Perbandingan laju pertumbuhan fungsi",
        "body_html": "<p>Untuk analisis kompleksitas, bandingkan laju pertumbuhan n, n log n, n²/2, dan 2ⁿ.</p>",
        "graphs": [
            {
                "type": "2d",
                "title": "Gambar 7. Laju pertumbuhan fungsi",
                "x": [1, "N"],
                "y": [0, "N*N/2*1.25"],
                "xlabel": "n",
                "params": [param("N", "Rentang n sampai", 5, 60, 1, 20, "N")],
                "elements": [
                    {"type": "fn", "expr": "x", "color": "blue", "label": "n"},
                    {"type": "fn", "expr": "x*log2(x)", "color": "orange", "label": "n log n"},
                    {"type": "fn", "expr": "x*x/2", "color": "red", "label": "n²/2 (loop bersarang)"},
                    {"type": "fn", "expr": "2**x/1000", "color": "purple", "label": "2ⁿ (skala diperkecil /1000)"},
                ],
            }
        ],
    },
    {
        "heading": "Strategi Fasilkom",
        "body_html": "<p><strong>Strategi:</strong> pikirkan gradien sebagai arah mendaki; periksa dimensi vektor; untuk "
                     "analisis kompleksitas, ubah penjumlahan menjadi rumus tertutup lalu hitung limitnya.</p>",
    },
]


def _faculty_nodes(fac, short, slugs, intro, examples, advanced, subtitles):
    """Tahap 6–8 untuk satu fakultas: Mudah, Sedang, dan Sulit (boss)."""
    s_easy, s_mid, s_hard = slugs
    return [
        {
            "slug": s_easy, "faculty": fac, "stage_number": 6, "order": 6, "icon": "🧭",
            "title": f"Tahap 6: {short} — Konsep Kunci",
            "badge_label": f"Khusus {short} · Mudah",
            "subtitle": subtitles[0],
            "summary_html": subtitles[0],
            "sections": intro,
        },
        {
            "slug": s_mid, "faculty": fac, "stage_number": 7, "order": 7, "icon": "🛠️",
            "title": f"Tahap 7: {short} — Contoh Terapan",
            "badge_label": f"Khusus {short} · Sedang",
            "subtitle": subtitles[1],
            "summary_html": subtitles[1],
            "sections": examples,
        },
        {
            "slug": s_hard, "faculty": fac, "stage_number": 8, "order": 8, "icon": "🏆", "is_boss": True,
            "title": f"Tahap 8: {short} — Ujian Sulit",
            "badge_label": f"Khusus {short} · Sulit",
            "subtitle": subtitles[2],
            "summary_html": subtitles[2],
            "sections": advanced,
        },
    ]


NODES = (
    _faculty_nodes(
        "ft", "FT", ("ft-konsep", "ft-terapan", "ft-ujian"), FT_INTRO, FT_EXAMPLES, FT_ADVANCED,
        ("Peta topik dan rumus kunci pemodelan rekayasa.",
         "RMS, PD terpisahkan, nilai rata-rata, dan model pendinginan.",
         "Volume benda putar dan strategi pemodelan."),
    )
    + _faculty_nodes(
        "fmipa", "FMIPA", ("fmipa-konsep", "fmipa-terapan", "fmipa-ujian"), FMIPA_INTRO, FMIPA_EXAMPLES, FMIPA_ADVANCED,
        ("Peta topik, ε–δ, teorema, Taylor, integral tak wajar, polar.",
         "Teorema Nilai Rata-rata, integral tak wajar, koordinat polar.",
         "Ilustrasi ε–δ, hampiran Maclaurin, dan strategi pembuktian."),
    )
    + _faculty_nodes(
        "fasilkom", "Fasilkom", ("fasilkom-konsep", "fasilkom-terapan", "fasilkom-ujian"),
        FASILKOM_INTRO, FASILKOM_EXAMPLES, FASILKOM_ADVANCED,
        ("Peta topik dan rumus kunci komputasi & AI.",
         "Newton–Raphson, backpropagation, distribusi eksponensial, sigmoid.",
         "Gradient descent pada kontur, laju pertumbuhan, dan strategi."),
    )
)
