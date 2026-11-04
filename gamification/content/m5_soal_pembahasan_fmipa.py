"""
Sumber: 5_Soal_Pembahasan_FMIPA.pdf
"Soal dan Pembahasan: Fakultas MIPA (FMIPA)" — 3 mudah · 3 sedang · 3 sulit.
Fokus: ketelitian konsep, pembuktian, deret, dan teknik integrasi.

Hanya tampil di jalur FMIPA: Mudah → Tahap 6, Sedang → Tahap 7, Sulit → Tahap 8.
"""

from .helpers import param, readout, tangent_graph, limit_graph, area_graph

DOCUMENT = {
    "slug": "soal-fmipa",
    "filename": "5_Soal_Pembahasan_FMIPA.pdf",
    "title": "Soal dan Pembahasan: Fakultas MIPA (FMIPA)",
    "subtitle": "Limit, ε–δ, L'Hôpital, deret, Taylor, integral lipat",
    "category": "soal",
    "faculty": "fmipa",
    "order": 5,
}

QUESTIONS = [
    # ── Tingkat Mudah ───────────────────────────────────────────────────────
    {
        "code": "FM-M1",
        "node": "fmipa-konsep",
        "difficulty": "basic",
        "prompt": "Hitung lim<sub>x→0</sub> sin(3x)/x.",
        "options": [("1", False), ("3", True), ("0", False), ("1/3", False)],
        "steps": [
            "Tulis sin(3x)/x = 3 · sin(3x)/(3x).",
            "Misal u = 3x; jika x→0 maka u→0 dan lim sin u / u = 1.",
            "Hasil = 3 · 1 = 3.",
        ],
        "answer": "3.",
        "graphs": [
            limit_graph(
                "Gambar 1. Grafik sin(kx)/x mendekati k di sekitar x = 0",
                "sin(k*x)/x", "0", "k", [-6, 6], [-2, 7],
                c_param=param("k", "Koefisien k (soal: 3)", 0.5, 6, 0.1, 3, "k"),
                caption="Geser d menuju 0: nilai mendekati k. Ubah k untuk membandingkan: lim sin(kx)/x = k.",
            )
        ],
    },
    {
        "code": "FM-M2",
        "node": "fmipa-konsep",
        "difficulty": "basic",
        "prompt": "Tentukan turunan f(x) = x²eˣ.",
        "options": [
            ("f′(x) = 2x·eˣ", False),
            ("f′(x) = x²eˣ", False),
            ("f′(x) = (x² + 2)eˣ", False),
            ("f′(x) = (x² + 2x)eˣ", True),
        ],
        "steps": [
            "Aturan hasil kali dengan u = x², v = eˣ: f′ = u′v + uv′.",
            "f′ = 2x·eˣ + x²·eˣ = (x² + 2x)eˣ.",
        ],
        "answer": "f′(x) = (x² + 2x)eˣ.",
        "graphs": [
            tangent_graph(
                "f(x) = x²eˣ dan garis singgungnya",
                "x*x*exp(x)", "(x*x+2*x)*exp(x)", "Titik singgung a", -4, 1, -0.5,
                [-5, 1.5], [-1.5, 8],
                caption="Garis singgung mendatar di x = 0 dan x = −2, tempat (x² + 2x)eˣ = 0.",
            )
        ],
    },
    {
        "code": "FM-M3",
        "node": "fmipa-konsep",
        "difficulty": "basic",
        "prompt": "Hitung ∫<sub>0</sub><sup>π</sup> sin x dx.",
        "options": [("0", False), ("1", False), ("2", True), ("−2", False)],
        "steps": [
            "Antiturunan sin x adalah −cos x.",
            "[−cos x] dari 0 ke π = −cos π − (−cos 0) = 1 + 1 = 2.",
        ],
        "answer": "2.",
        "graphs": [
            area_graph(
                "Luas bertanda di bawah sin x dari 0 sampai b",
                "sin(x)", 0, param("b", "Batas atas b (soal: π ≈ 3,1416)", 0, 6.2832, 0.001, 3.1416, "b"),
                "1-cos(b)", [-0.3, 6.6], [-1.3, 1.3],
                caption="Untuk b = 2π luas di atas dan di bawah sumbu saling menghapus sehingga integralnya 0.",
            )
        ],
    },
    # ── Tingkat Sedang ──────────────────────────────────────────────────────
    {
        "code": "FM-S1",
        "node": "fmipa-terapan",
        "difficulty": "medium",
        "is_diagnostic": True,
        "prompt": "Hitung lim<sub>x→0</sub> (eˣ − 1 − x)/x².",
        "options": [("1/2", True), ("1", False), ("0", False), ("∞", False)],
        "steps": [
            "Substitusi memberi 0/0, gunakan L'Hôpital.",
            "Turunan pertama: (eˣ − 1)/(2x) → masih 0/0.",
            "Turunan kedua: eˣ/2 → 1/2 saat x → 0.",
            "(Cek dengan deret: eˣ − 1 − x = x²/2 + x³/6 + …, dibagi x² → 1/2.)",
        ],
        "answer": "1/2.",
        "graphs": [
            {
                "type": "2d",
                "title": "Gambar 2. Nilai fungsi mendekati 1/2",
                "x": [-3, 3],
                "y": [0, 2],
                "params": [param("d", "Posisi x", -2.5, 2.5, 0.005, 0.8, "x")],
                "elements": [
                    {"type": "fn", "expr": "(exp(x)-1-x)/(x*x)", "color": "blue", "label": "(eˣ − 1 − x)/x²"},
                    {"type": "fn", "expr": "1/2 + x/6", "color": "green", "dash": True, "label": "hampiran deret 1/2 + x/6"},
                    {"type": "point", "x": 0, "y": 0.5, "hollow": True, "color": "blue"},
                    {"type": "point", "x": "d", "y": "(exp(d)-1-d)/(d*d)", "color": "red"},
                ],
                "readouts": [readout("f(x)", "(exp(d)-1-d)/(d*d)", 6), readout("Hampiran 1/2 + x/6", "1/2 + d/6", 6)],
                "caption": "Dekat x = 0, fungsi hampir sama dengan 1/2 + x/6 — sesuai pengecekan dengan deret.",
            }
        ],
    },
    {
        "code": "FM-S2",
        "node": "fmipa-terapan",
        "difficulty": "medium",
        "prompt": "Hitung ∫ x e<sup>2x</sup> dx.",
        "options": [
            ("x e<sup>2x</sup>/2 + C", False),
            ("e<sup>2x</sup>(2x − 1)/4 + C", True),
            ("e<sup>2x</sup>(2x + 1)/4 + C", False),
            ("e<sup>2x</sup>(x − 1)/2 + C", False),
        ],
        "steps": [
            "Integral parsial: u = x, dv = e<sup>2x</sup>dx → du = dx, v = e<sup>2x</sup>/2.",
            "∫ = x·e<sup>2x</sup>/2 − ∫ e<sup>2x</sup>/2 dx = x e<sup>2x</sup>/2 − e<sup>2x</sup>/4 + C.",
            "Sederhanakan: e<sup>2x</sup>(2x − 1)/4 + C.",
        ],
        "answer": "e<sup>2x</sup>(2x − 1)/4 + C.",
        "graphs": [
            {
                "type": "2d",
                "title": "Integran x·e^(kx) dan antiturunan e^(kx)(kx − 1)/k² + C",
                "x": [-2.5, 1.2],
                "y": [-1.5, 6],
                "params": [
                    param("k", "Koefisien k (soal: 2)", 0.5, 3, 0.05, 2, "k"),
                    param("C", "Konstanta integrasi C", -2, 2, 0.05, 0, "C"),
                ],
                "elements": [
                    {"type": "fn", "expr": "x*exp(k*x)", "color": "orange", "label": "integran x·e^(kx)"},
                    {"type": "fn", "expr": "exp(k*x)*(k*x-1)/(k*k) + C", "color": "blue", "label": "F(x) + C"},
                ],
                "readouts": [
                    readout("∫₀¹ x·e^(kx) dx = F(1) − F(0)", "exp(k)*(k-1)/(k*k) + 1/(k*k)", 5),
                ],
                "caption": "Titik minimum F berada tepat di x = 0, tempat integran berganti tanda (F′ = integran).",
            }
        ],
    },
    {
        "code": "FM-S3",
        "node": "fmipa-terapan",
        "difficulty": "medium",
        "prompt": "Tentukan interval konvergensi deret Σ<sub>n=1</sub><sup>∞</sup> xⁿ/(n·2ⁿ).",
        "options": [("(−2, 2)", False), ("(−2, 2]", False), ("[−2, 2]", False), ("[−2, 2)", True)],
        "steps": [
            "Uji rasio: |a<sub>n+1</sub>/a<sub>n</sub>| = |x|/2 · n/(n+1) → |x|/2. Konvergen jika |x|/2 &lt; 1, yaitu |x| &lt; 2 (jari-jari R = 2).",
            "Titik ujung x = 2: deret menjadi Σ 1/n (harmonik) yang divergen.",
            "Titik ujung x = −2: Σ (−1)ⁿ/n (harmonik berganti tanda) konvergen menurut uji deret berganti.",
        ],
        "answer": "Interval konvergensi [−2, 2).",
        "explanation": "Selalu periksa kedua titik ujung secara terpisah.",
        "graphs": [
            {
                "type": "2d",
                "title": "Jumlah parsial S_N(x) = Σ xⁿ/(n·Rⁿ)",
                "x": ["-1.5*R", "1.3*R"],
                "y": [-2, 5],
                "params": [
                    param("R", "Basis R (soal: 2)", 1, 4, 0.1, 2, "R"),
                    param("N", "Banyak suku N", 1, 80, 1, 10, "N"),
                ],
                "elements": [
                    {"type": "vband", "from": "-R", "to": "R", "color": "green", "opacity": 0.08},
                    {"type": "fn", "expr": "-ln(1-x/R)", "from": "-R", "to": "R*0.999", "color": "blue",
                     "label": "jumlah eksak −ln(1 − x/R)"},
                    {"type": "fn", "expr": "sum(1, N, n => x**n/(n*R**n))", "color": "red", "dash": True,
                     "label": "S_N(x), N = {{N}}"},
                    {"type": "vline", "x": "-R", "color": "green", "dash": True},
                    {"type": "vline", "x": "R", "color": "red", "dash": True},
                ],
                "readouts": [
                    readout("S_N(−R) → −ln 2 (konvergen)", "sum(1, N, n => (-1)**n/n)", 5),
                    readout("S_N(R) = 1 + 1/2 + … + 1/N (divergen)", "sum(1, N, n => 1/n)", 5),
                ],
                "caption": "Perbesar N: di x = −R jumlah parsial stabil, di x = R terus naik perlahan (harmonik).",
            }
        ],
    },
    # ── Tingkat Sulit ───────────────────────────────────────────────────────
    {
        "code": "FM-H1",
        "node": "fmipa-ujian",
        "difficulty": "high",
        "prompt": "Buktikan dengan definisi ε–δ bahwa lim<sub>x→2</sub> x² = 4. Pilihan δ mana yang membuat bukti berhasil "
                  "untuk setiap ε &gt; 0?",
        "options": [
            ("δ = ε", False),
            ("δ = ε/4, tanpa syarat tambahan", False),
            ("δ = min{1, ε/5}", True),
            ("δ = min{1, 5ε}", False),
        ],
        "steps": [
            "Diberikan ε &gt; 0. Kita ingin |x² − 4| &lt; ε bila 0 &lt; |x − 2| &lt; δ.",
            "Faktorkan: |x² − 4| = |x − 2|·|x + 2|.",
            "Batasi δ ≤ 1. Maka |x − 2| &lt; 1 → 1 &lt; x &lt; 3 → |x + 2| &lt; 5.",
            "Sehingga |x² − 4| &lt; 5|x − 2|. Agar ini &lt; ε cukup |x − 2| &lt; ε/5.",
            "Pilih δ = min{1, ε/5}. Maka 0 &lt; |x − 2| &lt; δ menjamin |x² − 4| &lt; ε. ∎",
        ],
        "answer": "Terbukti dengan δ = min{1, ε/5}.",
        "graphs": [
            {
                "type": "2d",
                "title": "Gambar 3. Pita ε di sumbu y dan pita δ di sumbu x",
                "x": [0.8, 3.2],
                "y": [0, 10],
                "params": [
                    param("eps", "ε (soal: contoh ε = 1)", 0.05, 4, 0.01, 1, "ε"),
                    param("dt", "δ coba-cobamu", 0.01, 1.2, 0.01, 0.2, "δ coba"),
                ],
                "elements": [
                    {"type": "hband", "from": "4-eps", "to": "4+eps", "color": "amber", "label": "pita ε"},
                    {"type": "vband", "from": "2-min(1,eps/5)", "to": "2+min(1,eps/5)", "color": "green",
                     "label": "δ = min{1, ε/5}"},
                    {"type": "vline", "x": "2-dt", "color": "purple", "dash": True, "label": "δ coba"},
                    {"type": "vline", "x": "2+dt", "color": "purple", "dash": True},
                    {"type": "fn", "expr": "x*x", "color": "blue", "label": "f(x) = x²"},
                    {"type": "point", "x": 2, "y": 4, "color": "red"},
                ],
                "readouts": [
                    readout("δ = min{1, ε/5}", "min(1,eps/5)"),
                    readout("max |x² − 4| di pita δ rumus", "4*min(1,eps/5) + min(1,eps/5)**2"),
                    readout("max |x² − 4| di pita δ coba", "4*dt + dt*dt"),
                    readout("δ coba berhasil? (1 = ya, 0 = tidak)", "(4*dt + dt*dt) < eps ? 1 : 0", 0),
                ],
                "caption": "Bukti berhasil jika seluruh kurva di dalam pita δ tetap berada di dalam pita ε. "
                           "Coba δ-mu sendiri dan bandingkan dengan δ = min{1, ε/5}.",
            }
        ],
    },
    {
        "code": "FM-H2",
        "node": "fmipa-ujian",
        "difficulty": "high",
        "prompt": "Hampiri ∫<sub>0</sub><sup>1</sup> e<sup>−x²</sup> dx memakai deret Maclaurin sampai suku ke-5 dan taksir galatnya.",
        "options": [
            ("≈ 0,7429 dengan galat ≤ 0,0046", False),
            ("≈ 0,7475 dengan galat ≤ 0,00076", True),
            ("≈ 0,6667 dengan galat ≤ 0,1", False),
            ("≈ 0,7468 dengan galat 0", False),
        ],
        "steps": [
            "Dari eᵘ = Σ uⁿ/n! dengan u = −x²: e<sup>−x²</sup> = 1 − x² + x⁴/2 − x⁶/6 + x⁸/24 − …",
            "Integrasikan suku demi suku pada [0,1]: 1 − 1/3 + 1/10 − 1/42 + 1/216 − …",
            "Lima suku pertama: 1 − 0,33333 + 0,1 − 0,02381 + 0,00463 ≈ 0,74749.",
            "Deret berganti tanda dengan suku menurun, sehingga galat ≤ suku berikutnya = 1/(120·11) = 1/1320 ≈ 0,00076.",
            "(Nilai eksak ≈ 0,746824; selisih 0,00066, memenuhi batas.)",
        ],
        "answer": "≈ 0,7475 dengan galat ≤ 0,00076.",
        "graphs": [
            {
                "type": "2d",
                "title": "Gambar 4. Hampiran Maclaurin vs fungsi asli",
                "x": [0, 2],
                "y": [-0.6, 1.2],
                "params": [param("N", "Banyak suku N (soal: 5)", 1, 10, 1, 5, "N")],
                "elements": [
                    {"type": "fill", "upper": "exp(-x*x)", "from": 0, "to": 1, "color": "amber", "opacity": 0.18},
                    {"type": "fn", "expr": "exp(-x*x)", "color": "blue", "label": "e^(−x²)"},
                    {"type": "fn", "expr": "sum(0, N-1, k => (-1)**k * x**(2*k) / fact(k))", "color": "red", "dash": True,
                     "label": "Taylor dengan {{N}} suku"},
                ],
                "readouts": [
                    readout("Hampiran ∫₀¹", "sum(0, N-1, k => (-1)**k / (fact(k)*(2*k+1)))", 6),
                    readout("Batas galat (suku berikutnya)", "1/(fact(N)*(2*N+1))", 6),
                    readout("Galat sebenarnya (eksak 0,746824)", "abs(sum(0, N-1, k => (-1)**k / (fact(k)*(2*k+1))) - 0.7468241328)", 6),
                ],
            }
        ],
    },
    {
        "code": "FM-H3",
        "node": "fmipa-ujian",
        "difficulty": "high",
        "is_diagnostic": True,
        "prompt": "Hitung ∬<sub>D</sub> xy dA, dengan D daerah antara y = x² dan y = x.",
        "options": [("1/12", False), ("1/6", False), ("1/48", False), ("1/24", True)],
        "steps": [
            "Titik potong x² = x → x = 0 dan x = 1; di antara itu x² ≤ x.",
            "Integral berulang: ∫<sub>0</sub><sup>1</sup> ∫<sub>x²</sub><sup>x</sup> xy dy dx.",
            "Bagian dalam: x·[y²/2]<sub>x²</sub><sup>x</sup> = x(x² − x⁴)/2 = (x³ − x⁵)/2.",
            "Bagian luar: (1/2)[x⁴/4 − x⁶/6]<sub>0</sub><sup>1</sup> = (1/2)(1/4 − 1/6) = (1/2)(1/12) = 1/24.",
        ],
        "answer": "1/24.",
        "graphs": [
            {
                "type": "2d",
                "title": "Gambar 5. Daerah integrasi D dan irisan integral dalam",
                "x": [-0.1, 1.15],
                "y": [-0.1, 1.15],
                "params": [param("x0", "Posisi irisan x", 0, 1, 0.01, 0.6, "x")],
                "elements": [
                    {"type": "fill", "upper": "x", "lower": "x*x", "from": 0, "to": 1, "color": "amber"},
                    {"type": "fill", "upper": "x", "lower": "x*x", "from": 0, "to": "x0", "color": "orange", "opacity": 0.35},
                    {"type": "fn", "expr": "x", "from": 0, "to": 1, "color": "blue", "label": "y = x"},
                    {"type": "fn", "expr": "x*x", "from": 0, "to": 1, "color": "red", "label": "y = x²"},
                    {"type": "segment", "x1": "x0", "y1": "x0*x0", "x2": "x0", "y2": "x0", "color": "navy", "width": 4,
                     "label": "irisan: y dari x² ke x"},
                ],
                "readouts": [
                    readout("Integral dalam (x³ − x⁵)/2", "(x0**3 - x0**5)/2", 5),
                    readout("Akumulasi ∫₀ˣ (dalam) dx", "(x0**4/4 - x0**6/6)/2", 6),
                    readout("Total (x = 1)", "1/24", 6),
                ],
                "caption": "Integral dalam menjumlah sepanjang irisan vertikal; integral luar menyapu irisan dari 0 ke 1.",
            }
        ],
    },
]
