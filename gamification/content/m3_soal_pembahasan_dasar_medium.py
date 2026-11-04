"""
Sumber: 3_Soal_Pembahasan_Dasar_Medium.pdf
"Soal dan Pembahasan — Tingkat Dasar hingga Medium (umum)": 6 soal dasar, 7 soal medium.

Soal umum berlaku untuk SEMUA fakultas (faculty = None) dan menjadi latihan
Tahap 1–5 (materi dari 1_Materi_Umum_Kalkulus.pdf).

Opsi pilihan ganda (pengecoh) disusun dari kesalahan yang sering terjadi; teks
soal, langkah pembahasan, dan jawaban mengikuti berkas sumber.
"""

from .helpers import (param, readout, tangent_graph, antiderivative_family, limit_graph, area_graph)

DOCUMENT = {
    "slug": "soal-dasar-medium",
    "filename": "3_Soal_Pembahasan_Dasar_Medium.pdf",
    "title": "Soal dan Pembahasan: Dasar hingga Medium",
    "subtitle": "Soal umum yang berlaku untuk semua fakultas: 6 soal dasar dan 7 soal medium",
    "category": "soal",
    "faculty": None,
    "order": 3,
}

QUESTIONS = [
    # ── Tingkat Dasar ───────────────────────────────────────────────────────
    {
        "code": "U-D1",
        "node": "umum-limit",
        "difficulty": "basic",
        "is_diagnostic": True,
        "prompt": "Hitung lim<sub>x→3</sub> (x² − 9)/(x − 3).",
        "options": [("0", False), ("6", True), ("3", False), ("Tidak ada, karena bentuknya 0/0", False)],
        "steps": [
            "Substitusi langsung menghasilkan 0/0.",
            "Faktorkan x² − 9 = (x − 3)(x + 3) sehingga ekspresi menjadi x + 3 untuk x ≠ 3.",
            "Limit = 3 + 3 = 6.",
        ],
        "answer": "6.",
        "explanation": "Bentuk 0/0 bukan berarti limit tidak ada — sederhanakan dulu dengan faktorisasi.",
        "graphs": [
            limit_graph(
                "f(x) = (x² − c²)/(x − c) di sekitar x = c",
                "(x*x-c*c)/(x-c)", "c", "2*c", [-1, 7], [-1, 13],
                c_param=param("c", "Titik limit c (soal: 3)", 0.5, 5, 0.1, 3, "c"),
                caption="Geser d menuju 0: f(x) mendekati 2c. Ubah c untuk membandingkan: limitnya selalu 2c.",
            )
        ],
    },
    {
        "code": "U-D2",
        "node": "umum-limit",
        "difficulty": "basic",
        "prompt": "Hitung lim<sub>x→∞</sub> (4x² − 3x)/(2x² + 1).",
        "options": [("4", False), ("∞", False), ("2", True), ("0", False)],
        "steps": [
            "Bagi pembilang dan penyebut dengan x² (pangkat tertinggi): (4 − 3/x)/(2 + 1/x²).",
            "Saat x → ∞, 3/x → 0 dan 1/x² → 0.",
            "Limit = 4/2 = 2.",
        ],
        "answer": "2.",
        "graphs": [
            {
                "type": "2d",
                "title": "f(x) = (a·x² − 3x)/(2x² + 1) untuk x besar",
                "x": [0, 60],
                "y": [-1.5, 4.5],
                "params": [
                    param("a", "Koefisien a (soal: 4)", 1, 8, 0.1, 4, "a"),
                    param("X", "Nilai x", 1, 60, 0.5, 10, "x"),
                ],
                "elements": [
                    {"type": "fn", "expr": "(a*x*x-3*x)/(2*x*x+1)", "from": 0, "color": "blue", "label": "f(x)"},
                    {"type": "hline", "y": "a/2", "color": "green", "dash": True, "label": "asimtot y = a/2"},
                    {"type": "point", "x": "X", "y": "(a*X*X-3*X)/(2*X*X+1)", "color": "red"},
                ],
                "readouts": [
                    readout("f(x)", "(a*X*X-3*X)/(2*X*X+1)", 5),
                    readout("Limit = a/2", "a/2"),
                ],
                "caption": "Perbesar x: kurva makin rapat ke asimtot a/2. Hanya koefisien pangkat tertinggi yang menentukan.",
            }
        ],
    },
    {
        "code": "U-D3",
        "node": "umum-turunan",
        "difficulty": "basic",
        "is_diagnostic": True,
        "prompt": "Tentukan f′(x) dan f′(0) untuk f(x) = (2x + 1)⁵.",
        "options": [
            ("f′(x) = 5(2x + 1)⁴; f′(0) = 5", False),
            ("f′(x) = 10(2x + 1)⁴; f′(0) = 10", True),
            ("f′(x) = 10(2x + 1)⁵; f′(0) = 10", False),
            ("f′(x) = 2(2x + 1)⁴; f′(0) = 2", False),
        ],
        "steps": [
            "Aturan rantai: luar u⁵, dalam u = 2x + 1.",
            "f′(x) = 5(2x + 1)⁴ · 2 = 10(2x + 1)⁴.",
            "f′(0) = 10 · 1⁴ = 10.",
        ],
        "answer": "f′(x) = 10(2x + 1)⁴; f′(0) = 10.",
        "explanation": "Jangan lupa mengalikan dengan turunan fungsi dalam (2x + 1)′ = 2.",
        "graphs": [
            tangent_graph(
                "f(x) = (2x + 1)ⁿ dan garis singgungnya",
                "(2*x+1)**n", "2*n*(2*x+1)**(n-1)", "Titik singgung a (soal: 0)", -1, 0.5, 0,
                [-1.2, 0.6], [-6, 40],
                extra_params=[param("n", "Pangkat n (soal: 5)", 1, 6, 1, 5, "n")],
                extra_readouts=[readout("f′(0) = 2n", "2*n")],
                caption="Ubah pangkat n untuk membandingkan: f′(0) = n·2 = 2n, faktor 2 berasal dari aturan rantai.",
            )
        ],
    },
    {
        "code": "U-D4",
        "node": "umum-turunan",
        "difficulty": "basic",
        "prompt": "Tentukan turunan f(x) = x ln x dan hitung f′(e).",
        "options": [
            ("f′(x) = 1/x; f′(e) = 1/e", False),
            ("f′(x) = ln x; f′(e) = 1", False),
            ("f′(x) = ln x + 1; f′(e) = 2", True),
            ("f′(x) = x + ln x; f′(e) = e + 1", False),
        ],
        "steps": [
            "Aturan hasil kali: u = x, v = ln x.",
            "f′(x) = 1·ln x + x·(1/x) = ln x + 1.",
            "f′(e) = ln e + 1 = 2.",
        ],
        "answer": "f′(x) = ln x + 1; f′(e) = 2.",
        "explanation": "Kesalahan umum: (f·g)′ ≠ f′·g′. Gunakan f′g + fg′.",
        "graphs": [
            tangent_graph(
                "f(x) = x ln x dan garis singgungnya",
                "x*ln(x)", "ln(x)+1", "Titik singgung a (soal: e ≈ 2,718)", 0.1, 4, 2.718,
                [0, 4.2], [-1, 6.5],
            )
        ],
    },
    {
        "code": "U-D5",
        "node": "umum-integral",
        "difficulty": "basic",
        "prompt": "Hitung ∫<sub>0</sub><sup>2</sup> (3x² + 1) dx.",
        "options": [("8", False), ("10", True), ("13", False), ("26", False)],
        "steps": [
            "Antiturunan: x³ + x.",
            "Evaluasi: (8 + 2) − (0 + 0) = 10.",
        ],
        "answer": "10.",
        "graphs": [
            area_graph(
                "Luas di bawah f(x) = 3x² + 1 dari 0 sampai b",
                "3*x*x+1", 0, param("b", "Batas atas b (soal: 2)", 0, 3, 0.01, 2, "b"),
                "b**3+b", [-0.3, 3.2], [-1, 30],
            )
        ],
    },
    {
        "code": "U-D6",
        "node": "umum-integral",
        "difficulty": "basic",
        "prompt": "Hitung ∫ 2x(x² + 1)³ dx.",
        "options": [
            ("(x² + 1)⁴ + C", False),
            ("x²(x² + 1)⁴/4 + C", False),
            ("(x² + 1)⁴/4 + C", True),
            ("(x² + 1)⁴/4", False),
        ],
        "steps": [
            "Substitusi u = x² + 1, du = 2x dx.",
            "∫ u³ du = u⁴/4 + C.",
            "Kembalikan: (x² + 1)⁴/4 + C.",
        ],
        "answer": "(x² + 1)⁴/4 + C.",
        "explanation": "Jangan lupa konstanta C pada integral tak tentu.",
        "graphs": [
            antiderivative_family(
                "Integran 2x(x² + 1)³ dan antiturunan (x² + 1)⁴/4 + C",
                "2*x*(x*x+1)**3", "(x*x+1)**4/4", [-1.5, 1.5], [-6, 10], x0=0.8,
            )
        ],
    },
    # ── Tingkat Medium ──────────────────────────────────────────────────────
    {
        "code": "U-S1",
        "node": "umum-turunan",
        "difficulty": "medium",
        "prompt": "Tentukan persamaan garis singgung kurva y = x³ − 2x + 1 di titik dengan x = 1.",
        "options": [("y = x + 1", False), ("y = 3x − 3", False), ("y = −x + 1", False), ("y = x − 1", True)],
        "steps": [
            "y(1) = 1 − 2 + 1 = 0, jadi titiknya (1, 0).",
            "y′ = 3x² − 2, sehingga kemiringan m = y′(1) = 1.",
            "Garis: y − 0 = 1·(x − 1), yaitu y = x − 1.",
        ],
        "answer": "y = x − 1.",
        "graphs": [
            tangent_graph(
                "Gambar 1. Kurva y = x³ − 2x + 1 dan garis singgung di x = a",
                "x**3-2*x+1", "3*x*x-2", "Titik singgung a (soal: 1)", -2, 2, 1,
                [-2.2, 2.2], [-3, 6],
                extra_readouts=[readout("Titik potong sumbu y garis singgung", "(a**3-2*a+1) - (3*a*a-2)*a")],
                fn_label="y = x³ − 2x + 1",
            )
        ],
    },
    {
        "code": "U-S2",
        "node": "umum-turunan",
        "difficulty": "medium",
        "prompt": "Tentukan titik ekstrem lokal f(x) = x³ − 3x² − 9x + 5 beserta jenisnya.",
        "options": [
            ("Maksimum lokal di (3, −22); minimum lokal di (−1, 10)", False),
            ("Maksimum lokal di (−1, 10); minimum lokal di (3, −22)", True),
            ("Maksimum lokal di (−1, 10); tidak ada minimum lokal", False),
            ("Maksimum lokal di (1, −6); minimum lokal di (−3, −22)", False),
        ],
        "steps": [
            "f′(x) = 3x² − 6x − 9 = 3(x − 3)(x + 1) = 0 → x = −1 atau x = 3.",
            "f″(x) = 6x − 6. f″(−1) = −12 &lt; 0 → maksimum lokal; f″(3) = 12 &gt; 0 → minimum lokal.",
            "Nilai: f(−1) = −1 − 3 + 9 + 5 = 10; f(3) = 27 − 27 − 27 + 5 = −22.",
        ],
        "answer": "Maksimum lokal di (−1, 10); minimum lokal di (3, −22).",
        "graphs": [
            {
                "type": "2d",
                "title": "Gambar 2. f(x) = x³ − 3x² − b·x + 5 dengan ekstrem lokalnya",
                "x": [-3.2, 5.2],
                "y": [-45, 45],
                "params": [param("b", "Koefisien b (soal: 9)", -6, 15, 0.1, 9, "b")],
                "elements": [
                    {"type": "fn", "expr": "x**3-3*x**2-b*x+5", "color": "blue", "label": "f(x)"},
                    {"type": "point", "x": "1-sqrt(1+b/3)", "y": "(1-sqrt(1+b/3))**3-3*(1-sqrt(1+b/3))**2-b*(1-sqrt(1+b/3))+5",
                     "color": "green", "label": "maks"},
                    {"type": "point", "x": "1+sqrt(1+b/3)", "y": "(1+sqrt(1+b/3))**3-3*(1+sqrt(1+b/3))**2-b*(1+sqrt(1+b/3))+5",
                     "color": "red", "label": "min"},
                ],
                "readouts": [
                    readout("x maks = 1 − √(1 + b/3)", "1-sqrt(1+b/3)"),
                    readout("f(x maks)", "(1-sqrt(1+b/3))**3-3*(1-sqrt(1+b/3))**2-b*(1-sqrt(1+b/3))+5"),
                    readout("x min = 1 + √(1 + b/3)", "1+sqrt(1+b/3)"),
                    readout("f(x min)", "(1+sqrt(1+b/3))**3-3*(1+sqrt(1+b/3))**2-b*(1+sqrt(1+b/3))+5"),
                ],
                "caption": "f′(x) = 3x² − 6x − b = 0. Geser b ke bawah −3: diskriminan negatif, titik ekstrem lenyap.",
            }
        ],
    },
    {
        "code": "U-S3",
        "node": "umum-integral",
        "difficulty": "medium",
        "prompt": "Hitung ∫<sub>0</sub><sup>1</sup> x e<sup>x²</sup> dx.",
        "options": [("e − 1", False), ("(e − 1)/2", True), ("e/2", False), ("(e + 1)/2", False)],
        "steps": [
            "Substitusi u = x², du = 2x dx → x dx = du/2. Batas: x = 0 → u = 0; x = 1 → u = 1.",
            "∫<sub>0</sub><sup>1</sup> (1/2)eᵘ du = (1/2)[eᵘ]<sub>0</sub><sup>1</sup> = (e − 1)/2.",
        ],
        "answer": "(e − 1)/2 ≈ 0,859.",
        "graphs": [
            area_graph(
                "Luas di bawah x·e^(x²) dari 0 sampai b",
                "x*exp(x*x)", 0, param("b", "Batas atas b (soal: 1)", 0, 1.5, 0.01, 1, "b"),
                "(exp(b*b)-1)/2", [-0.1, 1.6], [-0.5, 15],
            )
        ],
    },
    {
        "code": "U-S4",
        "node": "umum-integral",
        "difficulty": "medium",
        "prompt": "Hitung ∫<sub>0</sub><sup>π/2</sup> x cos x dx.",
        "options": [("π/2", False), ("π/2 + 1", False), ("1 − π/2", False), ("π/2 − 1", True)],
        "steps": [
            "Parsial: u = x, dv = cos x dx → du = dx, v = sin x.",
            "∫ x cos x dx = x sin x − ∫ sin x dx = x sin x + cos x.",
            "Evaluasi: (π/2 · 1 + 0) − (0 + 1) = π/2 − 1.",
        ],
        "answer": "π/2 − 1 ≈ 0,571.",
        "graphs": [
            area_graph(
                "Luas bertanda di bawah x·cos x dari 0 sampai b",
                "x*cos(x)", 0, param("b", "Batas atas b (soal: π/2 ≈ 1,571)", 0, 3.2, 0.001, 1.5708, "b"),
                "b*sin(b)+cos(b)-1", [-0.2, 3.3], [-3.5, 1.2],
                caption="Setelah x = π/2, cos x negatif sehingga luas bertanda mulai berkurang.",
            )
        ],
    },
    {
        "code": "U-S5",
        "node": "umum-integral",
        "difficulty": "medium",
        "prompt": "Hitung luas daerah yang dibatasi y = x + 2 dan y = x².",
        "options": [("10/3", False), ("7/6", False), ("9/2", True), ("27/2", False)],
        "steps": [
            "Titik potong: x² = x + 2 → x² − x − 2 = 0 → x = −1 dan x = 2. Pada selang itu garis berada di atas parabola.",
            "Luas = ∫<sub>−1</sub><sup>2</sup> (x + 2 − x²) dx = [x²/2 + 2x − x³/3]<sub>−1</sub><sup>2</sup>.",
            "Di x = 2: 2 + 4 − 8/3 = 10/3. Di x = −1: 1/2 − 2 + 1/3 = −7/6.",
            "Luas = 10/3 − (−7/6) = 20/6 + 7/6 = 27/6 = 9/2.",
        ],
        "answer": "9/2 satuan luas.",
        "graphs": [
            {
                "type": "2d",
                "title": "Gambar 3. Daerah di antara garis y = x + c dan parabola y = x²",
                "x": [-2.5, 3.5],
                "y": [-0.5, 10],
                "params": [param("c", "Konstanta garis c (soal: 2)", 0, 4, 0.05, 2, "c")],
                "elements": [
                    {"type": "fill", "upper": "x+c", "lower": "x*x", "from": "(1-sqrt(1+4*c))/2",
                     "to": "(1+sqrt(1+4*c))/2", "color": "amber"},
                    {"type": "fn", "expr": "x+c", "color": "blue", "label": "y = x + c"},
                    {"type": "fn", "expr": "x*x", "color": "red", "label": "y = x²"},
                ],
                "readouts": [
                    readout("x₁", "(1-sqrt(1+4*c))/2"),
                    readout("x₂", "(1+sqrt(1+4*c))/2"),
                    readout("Luas = (1 + 4c)^(3/2)/6", "(1+4*c)**1.5/6"),
                ],
                "caption": "Untuk c = 2 luasnya 9/2 = 4,5. Ubah c dan bandingkan daerahnya.",
            }
        ],
    },
    {
        "code": "U-S6",
        "node": "umum-dua-variabel",
        "difficulty": "medium",
        "prompt": "Untuk f(x, y) = x²y + 3xy², hitung ∂f/∂x dan ∂f/∂y di titik (1, 2).",
        "options": [
            ("∂f/∂x = 13 dan ∂f/∂y = 16", False),
            ("∂f/∂x = 4 dan ∂f/∂y = 13", False),
            ("∂f/∂x = 16 dan ∂f/∂y = 13", True),
            ("∂f/∂x = 16 dan ∂f/∂y = 1", False),
        ],
        "steps": [
            "∂f/∂x (y konstan) = 2xy + 3y². Di (1, 2): 2·1·2 + 3·4 = 4 + 12 = 16.",
            "∂f/∂y (x konstan) = x² + 6xy. Di (1, 2): 1 + 12 = 13.",
            "Gradien di (1, 2) adalah (16, 13).",
        ],
        "answer": "∂f/∂x = 16 dan ∂f/∂y = 13.",
        "graphs": [
            {
                "type": "2d",
                "title": "Irisan z = f(x, y₀) (y dibuat konstan)",
                "x": [-3, 3],
                "y": [-30, 45],
                "params": [
                    param("y0", "Nilai y₀ yang dibekukan (soal: 2)", -3, 3, 0.05, 2, "y₀"),
                    param("x0", "Titik x₀ (soal: 1)", -2.5, 2.5, 0.01, 1, "x₀"),
                ],
                "elements": [
                    {"type": "fn", "expr": "x*x*y0 + 3*x*y0*y0", "color": "blue", "label": "z = f(x, y₀)"},
                    {"type": "fn", "expr": "(x0*x0*y0 + 3*x0*y0*y0) + (2*x0*y0 + 3*y0*y0)*(x-x0)", "color": "red",
                     "dash": True, "label": "singgung (kemiringan ∂f/∂x)"},
                    {"type": "point", "x": "x0", "y": "x0*x0*y0 + 3*x0*y0*y0", "color": "red"},
                ],
                "readouts": [
                    readout("∂f/∂x = 2xy + 3y²", "2*x0*y0 + 3*y0*y0"),
                    readout("∂f/∂y = x² + 6xy", "x0*x0 + 6*x0*y0"),
                ],
                "caption": "Turunan parsial terhadap x = kemiringan irisan saat y dibekukan.",
            }
        ],
    },
    {
        "code": "U-S7",
        "node": "umum-turunan",
        "difficulty": "medium",
        "prompt": "Tangga 5 m bersandar pada dinding tegak. Dasar tangga ditarik menjauhi dinding dengan laju 0,5 m/s. "
                  "Seberapa cepat ujung atas tangga turun saat dasar berjarak 3 m dari dinding?",
        "options": [("0,5 m/s", False), ("0,375 m/s", True), ("0,667 m/s", False), ("0,3 m/s", False)],
        "steps": [
            "Misal x jarak dasar dan y tinggi ujung: x² + y² = 25. Saat x = 3, y = 4.",
            "Turunkan terhadap t: 2x·x′ + 2y·y′ = 0 → y′ = −x·x′/y.",
            "y′ = −(3)(0,5)/4 = −0,375.",
        ],
        "answer": "Ujung atas turun dengan laju 0,375 m/s.",
        "explanation": "Laju terkait: tulis hubungan, turunkan terhadap t, baru substitusi nilai sesaat.",
        "graphs": [
            {
                "type": "2d",
                "title": "Gambar 4. Sketsa tangga",
                "x": [-0.6, 12],
                "y": [-0.6, 8.6],
                "height": 360,
                "params": [
                    param("xb", "Jarak dasar x (soal: 3 m)", 0.2, 7.9, 0.01, 3, "x"),
                    param("L", "Panjang tangga L (soal: 5 m)", 3, 8, 0.1, 5, "L"),
                    param("v", "Laju dx/dt (soal: 0,5 m/s)", 0.1, 2, 0.05, 0.5, "dx/dt"),
                ],
                "elements": [
                    {"type": "segment", "x1": 0, "y1": 0, "x2": 0, "y2": 8.5, "color": "navy", "width": 3},
                    {"type": "segment", "x1": 0, "y1": 0, "x2": 12, "y2": 0, "color": "navy", "width": 3},
                    {"type": "segment", "x1": 0, "y1": "sqrt(L*L-xb*xb)", "x2": "xb", "y2": 0, "color": "blue", "width": 4,
                     "label": "tangga"},
                    {"type": "segment", "x1": "xb", "y1": 0.35, "x2": "xb+v*2", "y2": 0.35, "color": "red", "arrow": True},
                    {"type": "point", "x": 0, "y": "sqrt(L*L-xb*xb)", "color": "orange", "label": "y = {{sqrt(L*L-xb*xb)}}"},
                ],
                "readouts": [
                    readout("y = √(L² − x²)", "sqrt(L*L-xb*xb)"),
                    readout("dy/dt = −x·(dx/dt)/y", "-xb*v/sqrt(L*L-xb*xb)"),
                ],
                "caption": "Semakin jauh dasar tangga, semakin cepat ujung atas turun (y makin kecil).",
            }
        ],
    },
]
