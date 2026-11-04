"""
Sumber: 4_Soal_Pembahasan_FT.pdf
"Soal dan Pembahasan: Fakultas Teknik (FT)" — 3 mudah · 3 sedang · 3 sulit.
Fokus: kalkulus sebagai alat pemodelan fisika dan rekayasa.

Hanya tampil di jalur FT: Mudah → Tahap 6, Sedang → Tahap 7, Sulit → Tahap 8.
"""

from .helpers import param, readout, tangent_graph, antiderivative_family, limit_graph

DOCUMENT = {
    "slug": "soal-ft",
    "filename": "4_Soal_Pembahasan_FT.pdf",
    "title": "Soal dan Pembahasan: Fakultas Teknik (FT)",
    "subtitle": "Laju terkait, optimasi, usaha, volume, PD, panjang kurva",
    "category": "soal",
    "faculty": "ft",
    "order": 4,
}

QUESTIONS = [
    # ── Tingkat Mudah ───────────────────────────────────────────────────────
    {
        "code": "FT-M1",
        "node": "ft-konsep",
        "difficulty": "basic",
        "prompt": "Tentukan f′(x) dan nilai f′(1) untuk f(x) = 3x⁴ − 2x² + 5x − 7.",
        "options": [
            ("f′(x) = 12x³ − 4x + 5 dan f′(1) = 13", True),
            ("f′(x) = 12x³ − 4x dan f′(1) = 8", False),
            ("f′(x) = 12x³ − 4x + 5 − 7 dan f′(1) = 6", False),
            ("f′(x) = 3x³ − 2x + 5 dan f′(1) = 6", False),
        ],
        "steps": [
            "Turunkan suku demi suku dengan aturan pangkat: (3x⁴)′ = 12x³, (−2x²)′ = −4x, (5x)′ = 5, konstanta menjadi 0.",
            "Jadi f′(x) = 12x³ − 4x + 5.",
            "Substitusi x = 1: 12 − 4 + 5 = 13.",
        ],
        "answer": "f′(x) = 12x³ − 4x + 5 dan f′(1) = 13.",
        "graphs": [
            tangent_graph(
                "f(x) = 3x⁴ − 2x² + 5x − 7 dan garis singgungnya",
                "3*x**4-2*x**2+5*x-7", "12*x**3-4*x+5", "Titik singgung a (soal: 1)", -1.5, 1.5, 1,
                [-1.6, 1.6], [-16, 14],
            )
        ],
    },
    {
        "code": "FT-M2",
        "node": "ft-konsep",
        "difficulty": "basic",
        "prompt": "Hitung ∫(6x² − 4x + 3) dx.",
        "options": [
            ("12x − 4 + C", False),
            ("2x³ − 2x² + 3x + C", True),
            ("2x³ − 2x² + 3x", False),
            ("6x³ − 4x² + 3x + C", False),
        ],
        "steps": [
            "Integralkan per suku: ∫6x²dx = 2x³, ∫−4x dx = −2x², ∫3 dx = 3x.",
            "Tambahkan konstanta integrasi C.",
        ],
        "answer": "2x³ − 2x² + 3x + C.",
        "graphs": [
            antiderivative_family(
                "Integran 6x² − 4x + 3 dan antiturunan 2x³ − 2x² + 3x + C",
                "6*x*x-4*x+3", "2*x**3-2*x*x+3*x", [-1.5, 2], [-12, 14], x0=1,
            )
        ],
    },
    {
        "code": "FT-M3",
        "node": "ft-konsep",
        "difficulty": "basic",
        "prompt": "Hitung lim<sub>x→2</sub> (x² − 4)/(x − 2).",
        "options": [("0", False), ("2", False), ("4", True), ("Tidak ada, karena bentuknya 0/0", False)],
        "steps": [
            "Substitusi langsung memberi 0/0 (bentuk tak tentu).",
            "Faktorkan: x² − 4 = (x − 2)(x + 2), sehingga (x² − 4)/(x − 2) = x + 2 untuk x ≠ 2.",
            "Limit = 2 + 2 = 4.",
        ],
        "answer": "4.",
        "graphs": [
            limit_graph(
                "f(x) = (x² − c²)/(x − c) di sekitar x = c",
                "(x*x-c*c)/(x-c)", "c", "2*c", [-1, 6], [-1, 11],
                c_param=param("c", "Titik limit c (soal: 2)", 0.5, 4, 0.1, 2, "c"),
            )
        ],
    },
    # ── Tingkat Sedang ──────────────────────────────────────────────────────
    {
        "code": "FT-S1",
        "node": "ft-terapan",
        "difficulty": "medium",
        "is_diagnostic": True,
        "prompt": "Sebuah balon berbentuk bola dipompa sehingga jari-jarinya bertambah 2 cm/s. "
                  "Berapa laju pertambahan volumenya saat jari-jari 5 cm?",
        "options": [
            ("100π ≈ 314,2 cm³/s", False),
            ("500π/3 ≈ 523,6 cm³/s", False),
            ("200π ≈ 628,3 cm³/s", True),
            ("40π ≈ 125,7 cm³/s", False),
        ],
        "steps": [
            "Volume bola V = (4/3)πr³. Turunkan terhadap waktu t dengan aturan rantai: dV/dt = 4πr² · dr/dt.",
            "Substitusi r = 5 cm dan dr/dt = 2 cm/s: dV/dt = 4π(25)(2) = 200π.",
        ],
        "answer": "200π ≈ 628,3 cm³/s.",
        "graphs": [
            {
                "type": "2d",
                "title": "Volume bola V(r) dan laju perubahannya",
                "x": [0, 8.5],
                "y": [0, 2300],
                "xlabel": "r (cm)",
                "ylabel": "V (cm³)",
                "params": [
                    param("r", "Jari-jari r (soal: 5 cm)", 0.5, 8, 0.05, 5, "r"),
                    param("dr", "Laju dr/dt (soal: 2 cm/s)", 0.5, 4, 0.1, 2, "dr/dt"),
                ],
                "elements": [
                    {"type": "fn", "expr": "4/3*pi*x**3", "from": 0, "color": "blue", "label": "V(r) = (4/3)πr³"},
                    {"type": "fn", "expr": "4/3*pi*r**3 + 4*pi*r*r*(x-r)", "color": "red", "dash": True,
                     "label": "singgung (kemiringan dV/dr = 4πr²)"},
                    {"type": "point", "x": "r", "y": "4/3*pi*r**3", "color": "red"},
                ],
                "readouts": [
                    readout("V", "4/3*pi*r**3", 2),
                    readout("dV/dr = 4πr²", "4*pi*r*r", 2),
                    readout("dV/dt = 4πr²·dr/dt", "4*pi*r*r*dr", 2),
                ],
                "caption": "Laju volume sebanding dengan r²: balon besar membutuhkan lebih banyak udara per detik.",
            }
        ],
    },
    {
        "code": "FT-S2",
        "node": "ft-terapan",
        "difficulty": "medium",
        "prompt": "Dari selembar karton persegi 12 cm × 12 cm, dipotong persegi kecil bersisi x di keempat sudutnya, "
                  "lalu dilipat menjadi kotak tanpa tutup. Tentukan x agar volume kotak maksimum.",
        "options": [
            ("x = 3 cm, volume maksimum 108 cm³", False),
            ("x = 6 cm, volume maksimum 0 cm³", False),
            ("x = 4 cm, volume maksimum 64 cm³", False),
            ("x = 2 cm, volume maksimum 128 cm³", True),
        ],
        "steps": [
            "Alas kotak (12 − 2x) × (12 − 2x), tinggi x, sehingga V(x) = x(12 − 2x)² dengan 0 &lt; x &lt; 6.",
            "V′(x) = (12−2x)² + x·2(12−2x)(−2) = (12−2x)(12 − 6x).",
            "V′ = 0 → x = 6 (tidak berlaku, alas nol) atau x = 2.",
            "Uji: V′ berubah dari positif ke negatif di x = 2, sehingga maksimum. V(2) = 2·8² = 128.",
        ],
        "answer": "x = 2 cm, volume maksimum 128 cm³.",
        "graphs": [
            {
                "type": "2d",
                "title": "Gambar 1. Volume kotak V(x) = x(s − 2x)²",
                "x": [0, "s/2"],
                "y": [0, "2*s**3/27*1.2"],
                "xlabel": "x (cm)",
                "ylabel": "V (cm³)",
                "params": [
                    param("s", "Sisi karton s (soal: 12 cm)", 6, 20, 0.5, 12, "s"),
                    param("x0", "Potongan sudut x", 0, 10, 0.01, 2, "x"),
                ],
                "elements": [
                    {"type": "fn", "expr": "x*(s-2*x)**2", "from": 0, "to": "s/2", "color": "blue", "label": "V(x)"},
                    {"type": "point", "x": "s/6", "y": "2*s**3/27", "color": "red", "label": "maks: x = {{s/6}}"},
                    {"type": "point", "x": "min(x0, s/2)", "y": "min(x0,s/2)*(s-2*min(x0,s/2))**2", "color": "orange"},
                ],
                "readouts": [
                    readout("V(x) pada x pilihanmu", "min(x0,s/2)*(s-2*min(x0,s/2))**2", 2),
                    readout("x optimum = s/6", "s/6", 3),
                    readout("V maksimum = 2s³/27", "2*s**3/27", 2),
                ],
                "caption": "Geser x untuk mencari puncak, lalu ubah ukuran karton s: x optimum selalu s/6.",
            }
        ],
    },
    {
        "code": "FT-S3",
        "node": "ft-terapan",
        "difficulty": "medium",
        "prompt": "Pegas memiliki konstanta k = 200 N/m. Berapa usaha untuk meregangkannya dari x = 0,1 m sampai x = 0,3 m? "
                  "(Hukum Hooke: F = kx)",
        "options": [("W = 4 joule", False), ("W = 8 joule", True), ("W = 16 joule", False), ("W = 40 joule", False)],
        "steps": [
            "Usaha = ∫F dx = ∫<sub>0,1</sub><sup>0,3</sup> 200x dx.",
            "Antiturunan: 100x². Evaluasi: 100(0,3)² − 100(0,1)² = 9 − 1 = 8.",
        ],
        "answer": "W = 8 joule.",
        "graphs": [
            {
                "type": "2d",
                "title": "Gambar 2. Usaha sama dengan luas di bawah kurva gaya F = kx",
                "x": [0, 0.5],
                "y": [0, 210],
                "xlabel": "x (m)",
                "ylabel": "F (N)",
                "params": [
                    param("k", "Konstanta pegas k (soal: 200 N/m)", 50, 400, 5, 200, "k"),
                    param("a", "Regangan awal (soal: 0,1 m)", 0, 0.5, 0.01, 0.1, "x₁"),
                    param("b", "Regangan akhir (soal: 0,3 m)", 0, 0.5, 0.01, 0.3, "x₂"),
                ],
                "elements": [
                    {"type": "fill", "upper": "k*x", "from": "a", "to": "b", "color": "amber"},
                    {"type": "fn", "expr": "k*x", "color": "blue", "label": "F = kx"},
                    {"type": "text", "x": "(a+b)/2", "y": "k*(a+b)/4", "text": "W = {{k/2*(b*b-a*a)}} J",
                     "anchor": "middle", "color": "navy"},
                ],
                "readouts": [readout("W = (k/2)(x₂² − x₁²)", "k/2*(b*b-a*a)", 3)],
            }
        ],
    },
    # ── Tingkat Sulit ───────────────────────────────────────────────────────
    {
        "code": "FT-H1",
        "node": "ft-ujian",
        "difficulty": "high",
        "prompt": "Daerah D dibatasi kurva y = x² dan y = √x. Tentukan volume benda yang terbentuk jika D diputar "
                  "mengelilingi sumbu x.",
        "options": [("7π/10", False), ("9π/70", False), ("π/3", False), ("3π/10", True)],
        "steps": [
            "Titik potong: x² = √x → x⁴ = x → x = 0 atau x = 1.",
            "Pada 0 ≤ x ≤ 1, √x ≥ x², jadi jari-jari luar R = √x dan jari-jari dalam r = x².",
            "Metode cincin: V = π∫<sub>0</sub><sup>1</sup> (R² − r²)dx = π∫<sub>0</sub><sup>1</sup> (x − x⁴)dx.",
            "= π[x²/2 − x⁵/5]<sub>0</sub><sup>1</sup> = π(1/2 − 1/5) = 3π/10.",
        ],
        "answer": "V = 3π/10 satuan volume.",
        "explanation": "Pada metode cincin kuadratkan masing-masing jari-jari: R² − r², bukan (R − r)².",
        "graphs": [
            {
                "type": "2d",
                "title": "Gambar 3. Daerah D yang diputar (y = √x dan y = xⁿ)",
                "x": [-0.05, 1.1],
                "y": [-0.05, 1.1],
                "params": [param("n", "Pangkat kurva dalam n (soal: 2)", 1.2, 5, 0.1, 2, "n")],
                "elements": [
                    {"type": "fill", "upper": "sqrt(x)", "lower": "x**n", "from": 0, "to": 1, "color": "amber"},
                    {"type": "fn", "expr": "x**n", "from": 0, "to": 1, "color": "blue", "label": "y = xⁿ (r)"},
                    {"type": "fn", "expr": "sqrt(x)", "from": 0, "to": 1, "color": "red", "label": "y = √x (R)"},
                ],
                "readouts": [
                    readout("V = π(1/2 − 1/(2n+1))", "pi*(1/2-1/(2*n+1))", 5),
                    readout("V/π", "1/2-1/(2*n+1)", 5),
                ],
            },
            {
                "type": "3d",
                "title": "Gambar 4. Benda putar (permukaan luar merah, rongga dalam biru)",
                "extent": 1.2,
                "axes": [1.3, 1.2, 1.2],
                "yaw": 15,
                "tilt": 20,
                "params": [param("n", "Pangkat kurva dalam n (soal: 2)", 1.2, 5, 0.1, 2, "n")],
                "surfaces": [
                    {"u": [0, 1], "v": [0, "2*pi"], "x": "u", "y": "sqrt(u)*cos(v)", "z": "sqrt(u)*sin(v)",
                     "color": "red", "nu": 14, "nv": 24, "label": "permukaan luar y = √x"},
                    {"u": [0, 1], "v": [0, "2*pi"], "x": "u", "y": "u**n*cos(v)", "z": "u**n*sin(v)",
                     "color": "blue", "nu": 14, "nv": 24, "label": "rongga y = xⁿ"},
                ],
                "readouts": [readout("V", "pi*(1/2-1/(2*n+1))", 5)],
            },
        ],
    },
    {
        "code": "FT-H2",
        "node": "ft-ujian",
        "difficulty": "high",
        "prompt": "Secangkir kopi bersuhu 85 °C diletakkan di ruangan bersuhu 25 °C. Setelah 10 menit suhunya 55 °C. "
                  "Menurut hukum pendinginan Newton dT/dt = −k(T − 25), kapan suhu kopi mencapai 35 °C?",
        "options": [
            ("t ≈ 16,67 menit", False),
            ("t ≈ 20 menit", False),
            ("t ≈ 25,85 menit", True),
            ("t ≈ 30 menit", False),
        ],
        "steps": [
            "Pisahkan variabel: dT/(T−25) = −k dt → ln|T−25| = −kt + c, sehingga T − 25 = 60e<sup>−kt</sup> (dari T(0) = 85).",
            "Syarat T(10) = 55: 30 = 60e<sup>−10k</sup> → e<sup>−10k</sup> = 1/2 → k = (ln 2)/10.",
            "Untuk T = 35: 10 = 60e<sup>−kt</sup> → e<sup>−kt</sup> = 1/6 → t = (ln 6)/k = 10·ln 6/ln 2.",
            "Numerik: 10 × 2,585 ≈ 25,85.",
        ],
        "answer": "t ≈ 25,85 menit.",
        "explanation": "Pendinginan bersifat eksponensial, bukan linear — jangan membagi selisih suhu dengan laju rata-rata.",
        "graphs": [
            {
                "type": "2d",
                "title": "Gambar 5. Kurva pendinginan kopi",
                "x": [0, 60],
                "y": [10, 90],
                "xlabel": "t (menit)",
                "ylabel": "T (°C)",
                "params": [
                    param("Ta", "Suhu ruang (soal: 25 °C)", 10, 35, 0.5, 25, "T_ruang"),
                    param("T10", "Suhu setelah 10 menit (soal: 55 °C)", 40, 80, 0.5, 55, "T(10)"),
                    param("Tt", "Suhu target (soal: 35 °C)", 30, 70, 0.5, 35, "T_target"),
                ],
                "elements": [
                    {"type": "fn", "expr": "Ta + (85-Ta)*exp(-ln((85-Ta)/(T10-Ta))/10*x)", "from": 0, "color": "blue",
                     "label": "T(t)"},
                    {"type": "hline", "y": "Tt", "color": "red", "dash": True, "label": "suhu target"},
                    {"type": "hline", "y": "Ta", "color": "gray", "dash": True, "label": "suhu ruang"},
                    {"type": "point", "x": 10, "y": "T10", "color": "green"},
                    {"type": "point", "x": "ln((85-Ta)/(Tt-Ta))/(ln((85-Ta)/(T10-Ta))/10)", "y": "Tt", "color": "red",
                     "label": "t ≈ {{ln((85-Ta)/(Tt-Ta))/(ln((85-Ta)/(T10-Ta))/10)}} menit"},
                ],
                "readouts": [
                    readout("k = ln((85 − T_ruang)/(T(10) − T_ruang))/10", "ln((85-Ta)/(T10-Ta))/10", 5),
                    readout("t saat mencapai suhu target", "ln((85-Ta)/(Tt-Ta))/(ln((85-Ta)/(T10-Ta))/10)", 3),
                ],
            }
        ],
    },
    {
        "code": "FT-H3",
        "node": "ft-ujian",
        "difficulty": "high",
        "is_diagnostic": True,
        "prompt": "Tentukan panjang kurva y = (2/3)x<sup>3/2</sup> untuk 0 ≤ x ≤ 3.",
        "options": [("2√3 ≈ 3,46", False), ("14/3 ≈ 4,67", True), ("7/3 ≈ 2,33", False), ("16/3 ≈ 5,33", False)],
        "steps": [
            "y′ = (2/3)(3/2)x<sup>1/2</sup> = √x, maka 1 + (y′)² = 1 + x.",
            "L = ∫<sub>0</sub><sup>3</sup> √(1+x) dx = (2/3)(1+x)<sup>3/2</sup> dari 0 sampai 3.",
            "= (2/3)(8 − 1) = 14/3.",
        ],
        "answer": "L = 14/3 ≈ 4,67 satuan.",
        "graphs": [
            {
                "type": "2d",
                "title": "Gambar 6. Kurva y = (2/3)x^(3/2) yang dihitung panjangnya",
                "x": [-0.2, 6.2],
                "y": [-0.3, 10.5],
                "params": [param("b", "Batas kanan b (soal: 3)", 0.1, 6, 0.01, 3, "b")],
                "elements": [
                    {"type": "fn", "expr": "2/3*x**1.5", "from": 0, "to": 6, "color": "gray", "width": 1.5},
                    {"type": "fn", "expr": "2/3*x**1.5", "from": 0, "to": "b", "color": "blue", "width": 4,
                     "label": "busur yang diukur"},
                    {"type": "segment", "x1": 0, "y1": 0, "x2": "b", "y2": "2/3*b**1.5", "color": "red", "dash": True,
                     "label": "tali busur (garis lurus)"},
                ],
                "readouts": [
                    readout("Panjang busur L = (2/3)((1+b)^(3/2) − 1)", "2/3*((1+b)**1.5-1)"),
                    readout("Panjang tali busur", "sqrt(b*b + (2/3*b**1.5)**2)"),
                ],
                "caption": "Panjang busur selalu ≥ panjang garis lurus antara kedua ujungnya.",
            }
        ],
    },
]
