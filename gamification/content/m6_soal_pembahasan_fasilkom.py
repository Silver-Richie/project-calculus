"""
Sumber: 6_Soal_Pembahasan_Fasilkom.pdf
"Soal dan Pembahasan: Fakultas Ilmu Komputer (Fasilkom)" — 3 mudah · 3 sedang · 3 sulit.
Fokus: kalkulus untuk machine learning, analisis algoritma, dan metode numerik.

Hanya tampil di jalur Fasilkom: Mudah → Tahap 6, Sedang → Tahap 7, Sulit → Tahap 8.
"""

from .helpers import param, readout

DOCUMENT = {
    "slug": "soal-fasilkom",
    "filename": "6_Soal_Pembahasan_Fasilkom.pdf",
    "title": "Soal dan Pembahasan: Fakultas Ilmu Komputer (Fasilkom)",
    "subtitle": "Gradient descent, sigmoid, softmax, Big-O, integral numerik",
    "category": "soal",
    "faculty": "fasilkom",
    "order": 6,
}

SOFTMAX = "exp(z{k})/(exp(z1)+exp(z2)+exp(z3))"

QUESTIONS = [
    # ── Tingkat Mudah ───────────────────────────────────────────────────────
    {
        "code": "FK-M1",
        "node": "fasilkom-konsep",
        "difficulty": "basic",
        "prompt": "Fungsi kerugian f(x) = (x − 3)² diminimalkan dengan gradient descent: x<sub>baru</sub> = x − η f′(x). "
                  "Mulai x₀ = 0 dan η = 0,1. Berapa x₁?",
        "options": [("x₁ = −0,6", False), ("x₁ = 0,3", False), ("x₁ = 0,6", True), ("x₁ = 6", False)],
        "steps": [
            "f′(x) = 2(x − 3).",
            "Pada x₀ = 0: f′(0) = −6.",
            "x₁ = 0 − 0,1·(−6) = 0,6 (bergerak mendekati minimum di x = 3).",
        ],
        "answer": "x₁ = 0,6.",
        "graphs": [
            {
                "type": "2d",
                "title": "Gradient descent pada f(x) = (x − 3)²",
                "x": [-3, 7.5],
                "y": [-1, 30],
                "params": [
                    param("eta", "Laju belajar η (soal: 0,1)", 0.01, 1.1, 0.01, 0.1, "η"),
                    param("k", "Banyak iterasi (soal: 1)", 0, 30, 1, 1, "k"),
                    param("x0", "Titik awal x₀ (soal: 0)", -2.5, 7, 0.1, 0, "x₀"),
                ],
                "elements": [
                    {"type": "fn", "expr": "(x-3)**2", "color": "blue", "label": "f(x) = (x − 3)²"},
                    {"type": "iter", "id": "G", "init": {"x": "x0"}, "update": {"x": "x - eta*2*(x-3)"}, "steps": "k",
                     "px": "x", "py": "(x-3)**2", "color": "red", "label": "langkah gradient descent"},
                ],
                "readouts": [
                    readout("xₖ", "G.x", 5),
                    readout("Rumus tertutup 3 − (3 − x₀)(1 − 2η)ᵏ", "3 - (3-x0)*(1-2*eta)**k", 5),
                    readout("f(xₖ)", "(G.x-3)**2", 5),
                ],
                "caption": "Coba η > 1: langkah melompati minimum dan membesar (divergen). η = 0,5 langsung tiba di x = 3.",
            }
        ],
    },
    {
        "code": "FK-M2",
        "node": "fasilkom-konsep",
        "difficulty": "basic",
        "prompt": "Waktu eksekusi sebuah algoritma T(n) = 3n² + 2n. Hitung lim<sub>n→∞</sub> T(n)/(n² + 5) dan simpulkan "
                  "orde pertumbuhannya.",
        "options": [
            ("Limit = 3, sehingga T(n) = Θ(n)", False),
            ("Limit = 1, sehingga T(n) = Θ(n²)", False),
            ("Limit = ∞, sehingga T(n) = Θ(n³)", False),
            ("Limit = 3, sehingga T(n) = Θ(n²)", True),
        ],
        "steps": [
            "Bagi pembilang dan penyebut dengan n²: (3 + 2/n)/(1 + 5/n²).",
            "Saat n→∞: 2/n → 0 dan 5/n² → 0, sehingga limit = 3.",
            "Karena limit rasio terhadap n² berhingga dan positif, T(n) = Θ(n²).",
        ],
        "answer": "Limit = 3, sehingga T(n) = Θ(n²).",
        "graphs": [
            {
                "type": "2d",
                "title": "Rasio T(n)/(n² + 5) untuk n besar",
                "x": [0, 80],
                "y": [0, 8],
                "xlabel": "n",
                "params": [
                    param("a", "Koefisien n² pada T(n) (soal: 3)", 0.5, 6, 0.1, 3, "a"),
                    param("n", "Nilai n", 1, 80, 1, 10, "n"),
                ],
                "elements": [
                    {"type": "fn", "expr": "(a*x*x+2*x)/(x*x+5)", "from": 0, "color": "blue", "label": "T(n)/(n² + 5)"},
                    {"type": "hline", "y": "a", "color": "green", "dash": True, "label": "limit = a"},
                    {"type": "point", "x": "n", "y": "(a*n*n+2*n)/(n*n+5)", "color": "red"},
                ],
                "readouts": [readout("T(n)/(n² + 5)", "(a*n*n+2*n)/(n*n+5)", 5), readout("Limit", "a")],
            }
        ],
    },
    {
        "code": "FK-M3",
        "node": "fasilkom-konsep",
        "difficulty": "basic",
        "prompt": "Hampiri ∫<sub>0</sub><sup>2</sup> x dx dengan jumlah Riemann kanan, n = 4 persegi panjang. "
                  "Berapa galat terhadap nilai eksak?",
        "options": [
            ("Hampiran 1,5; galat 0,5", False),
            ("Hampiran 2,5; galat 0,5", True),
            ("Hampiran 2; galat 0", False),
            ("Hampiran 2,5; galat 0,25", False),
        ],
        "steps": [
            "Lebar Δx = 2/4 = 0,5; titik kanan: 0,5; 1; 1,5; 2.",
            "Jumlah = 0,5 × (0,5 + 1 + 1,5 + 2) = 0,5 × 5 = 2,5.",
            "Nilai eksak ∫x dx = x²/2 = 2. Galat = 2,5 − 2 = 0,5.",
        ],
        "answer": "Hampiran 2,5; galat 0,5 (lebih besar dari eksak).",
        "graphs": [
            {
                "type": "2d",
                "title": "Gambar 1. Jumlah Riemann untuk f(x) = x",
                "x": [-0.1, 2.1],
                "y": [-0.1, 2.2],
                "params": [
                    param("n", "Banyak persegi panjang n (soal: 4)", 1, 40, 1, 4, "n"),
                    param("m", "Titik sampel: 0 kiri · 1 kanan · 2 tengah · 3 trapesium (soal: 1)", 0, 3, 1, 1, "mode"),
                ],
                "elements": [
                    {"type": "riemann", "id": "R", "expr": "x", "from": 0, "to": 2, "n": "n", "mode": "m", "color": "amber"},
                    {"type": "fn", "expr": "x", "color": "blue", "label": "f(x) = x"},
                ],
                "readouts": [readout("Hampiran", "R", 5), readout("Nilai eksak", "2"), readout("Galat", "R-2", 5)],
                "caption": "Riemann kanan selalu di atas eksak untuk fungsi naik; titik tengah dan trapesium tepat untuk garis lurus.",
            }
        ],
    },
    # ── Tingkat Sedang ──────────────────────────────────────────────────────
    {
        "code": "FK-S1",
        "node": "fasilkom-terapan",
        "difficulty": "medium",
        "prompt": "Fungsi sigmoid σ(x) = 1/(1 + e<sup>−x</sup>) dipakai pada neural network. Tunjukkan σ′(x) = σ(x)(1 − σ(x)) "
                  "dan hitung σ′(0).",
        "options": [
            ("σ′(x) = σ(x)(1 − σ(x)) dan σ′(0) = 1/2", False),
            ("σ′(x) = σ(x)² dan σ′(0) = 1/4", False),
            ("σ′(x) = σ(x)(1 − σ(x)) dan σ′(0) = 1/4", True),
            ("σ′(x) = 1 − σ(x) dan σ′(0) = 1/2", False),
        ],
        "steps": [
            "Tulis σ = (1 + e<sup>−x</sup>)<sup>−1</sup>. Aturan rantai: σ′ = e<sup>−x</sup>/(1 + e<sup>−x</sup>)².",
            "Pisahkan: σ′ = [1/(1+e<sup>−x</sup>)]·[e<sup>−x</sup>/(1+e<sup>−x</sup>)] = σ · (1 − σ), karena 1 − σ = e<sup>−x</sup>/(1 + e<sup>−x</sup>).",
            "Di x = 0: σ(0) = 1/2, sehingga σ′(0) = (1/2)(1/2) = 1/4 (nilai maksimum turunan).",
        ],
        "answer": "σ′(x) = σ(x)(1 − σ(x)) dan σ′(0) = 1/4.",
        "graphs": [
            {
                "type": "2d",
                "title": "Gambar 2. Sigmoid σ(kx) dan turunannya",
                "x": [-8, 8],
                "y": [-0.1, 1.1],
                "params": [
                    param("a", "Titik x (soal: 0)", -8, 8, 0.05, 0, "x"),
                    param("k", "Kecuraman k (soal: 1)", 0.25, 3, 0.05, 1, "k"),
                ],
                "elements": [
                    {"type": "fn", "expr": "sigmoid(k*x)", "color": "blue", "label": "σ(kx)"},
                    {"type": "fn", "expr": "k*sigmoid(k*x)*(1-sigmoid(k*x))", "color": "red", "label": "turunan k·σ(1 − σ)"},
                    {"type": "fn", "expr": "sigmoid(k*a) + k*sigmoid(k*a)*(1-sigmoid(k*a))*(x-a)", "color": "orange",
                     "dash": True, "label": "garis singgung"},
                    {"type": "point", "x": "a", "y": "sigmoid(k*a)", "color": "orange"},
                ],
                "readouts": [
                    readout("σ(kx)", "sigmoid(k*a)"),
                    readout("Turunan di x", "k*sigmoid(k*a)*(1-sigmoid(k*a))"),
                ],
                "caption": "Untuk k = 1 turunan terbesar 1/4 di x = 0. Jauh dari 0 turunannya hampir nol (vanishing gradient).",
            }
        ],
    },
    {
        "code": "FK-S2",
        "node": "fasilkom-terapan",
        "difficulty": "medium",
        "is_diagnostic": True,
        "prompt": "Model linear ŷ = wx + b dengan kerugian L = (wx + b − y)². Untuk data x = 2, y = 5, parameter w = 1, b = 0: "
                  "hitung gradien (∂L/∂w, ∂L/∂b) dan parameter baru setelah satu langkah gradient descent dengan η = 0,1.",
        "options": [
            ("Gradien (−6, −3); w = 1,6 dan b = 0,3", False),
            ("Gradien (12, 6); w = −0,2 dan b = −0,6", False),
            ("Gradien (−12, −6); w = 13 dan b = 6", False),
            ("Gradien (−12, −6); w = 2,2 dan b = 0,6", True),
        ],
        "steps": [
            "Residu r = wx + b − y = 1·2 + 0 − 5 = −3.",
            "∂L/∂w = 2r·x = 2(−3)(2) = −12; ∂L/∂b = 2r = −6.",
            "Update: w = 1 − 0,1(−12) = 2,2; b = 0 − 0,1(−6) = 0,6.",
            "Cek prediksi baru: 2,2·2 + 0,6 = 5,0, tepat sama dengan y.",
        ],
        "answer": "Gradien (−12, −6); w = 2,2 dan b = 0,6.",
        "graphs": [
            {
                "type": "2d",
                "title": "Garis model sebelum dan sesudah satu langkah",
                "x": [-0.5, 4],
                "y": [-1, 10],
                "params": [
                    param("eta", "Laju belajar η (soal: 0,1)", 0, 0.3, 0.005, 0.1, "η"),
                    param("w0", "w awal (soal: 1)", -1, 3, 0.1, 1, "w"),
                    param("b0", "b awal (soal: 0)", -2, 3, 0.1, 0, "b"),
                ],
                "elements": [
                    {"type": "fn", "expr": "w0*x+b0", "color": "gray", "dash": True, "label": "sebelum: ŷ = wx + b"},
                    {"type": "fn", "expr": "(w0 - eta*2*(2*w0+b0-5)*2)*x + (b0 - eta*2*(2*w0+b0-5))", "color": "blue",
                     "label": "sesudah satu langkah"},
                    {"type": "point", "x": 2, "y": 5, "color": "red", "label": "data (2, 5)"},
                ],
                "readouts": [
                    readout("∂L/∂w = 2r·x", "2*(2*w0+b0-5)*2"),
                    readout("∂L/∂b = 2r", "2*(2*w0+b0-5)"),
                    readout("w baru", "w0 - eta*2*(2*w0+b0-5)*2"),
                    readout("b baru", "b0 - eta*2*(2*w0+b0-5)"),
                    readout("Prediksi baru di x = 2", "(w0 - eta*2*(2*w0+b0-5)*2)*2 + (b0 - eta*2*(2*w0+b0-5))"),
                ],
                "caption": "Dengan η = 0,1 garis tepat melewati data. η lebih besar membuat garis melewati target (overshoot).",
            }
        ],
    },
    {
        "code": "FK-S3",
        "node": "fasilkom-terapan",
        "difficulty": "medium",
        "prompt": "Potongan kode: <code>for i in 1..n: for j in 1..i: kerjakan()</code>. Hitung banyak pemanggilan T(n) "
                  "dan tentukan lim T(n)/n².",
        "options": [
            ("T(n) = n², lim T(n)/n² = 1, orde Θ(n²)", False),
            ("T(n) = n(n+1)/2, lim T(n)/n² = 1/2, orde Θ(n²)", True),
            ("T(n) = n(n−1)/2, lim T(n)/n² = 1/2, orde Θ(n)", False),
            ("T(n) = n log n, lim T(n)/n² = 0, orde Θ(n log n)", False),
        ],
        "steps": [
            "Untuk setiap i, loop dalam berjalan i kali, sehingga T(n) = Σ<sub>i=1</sub><sup>n</sup> i = n(n+1)/2.",
            "T(n)/n² = (n² + n)/(2n²) = 1/2 + 1/(2n) → 1/2.",
            "Limit berhingga positif, jadi T(n) = Θ(n²). (Secara kontinu, T(n) ≈ ∫<sub>0</sub><sup>n</sup> x dx = n²/2.)",
        ],
        "answer": "T(n) = n(n+1)/2, lim T(n)/n² = 1/2, orde Θ(n²).",
        "graphs": [
            {
                "type": "2d",
                "title": "Rasio T(n)/n² = 1/2 + 1/(2n)",
                "x": [0, 50],
                "y": [0, 1.1],
                "xlabel": "n",
                "params": [param("n", "Nilai n", 1, 50, 1, 5, "n")],
                "elements": [
                    {"type": "fn", "expr": "(x*(x+1)/2)/(x*x)", "from": 1, "color": "blue", "label": "T(n)/n²"},
                    {"type": "hline", "y": 0.5, "color": "green", "dash": True, "label": "limit 1/2"},
                    {"type": "point", "x": "n", "y": "(n*(n+1)/2)/(n*n)", "color": "red"},
                ],
                "readouts": [readout("T(n) = n(n+1)/2", "n*(n+1)/2", 0), readout("T(n)/n²", "(n*(n+1)/2)/(n*n)", 5)],
            },
            {
                "type": "2d",
                "title": "Gambar 3. Perbandingan laju pertumbuhan fungsi",
                "x": [1, "N"],
                "y": [0, "N*N/2*1.25"],
                "xlabel": "n",
                "params": [param("N", "Rentang n sampai", 5, 60, 1, 20, "N")],
                "elements": [
                    {"type": "fn", "expr": "x", "color": "blue", "label": "n"},
                    {"type": "fn", "expr": "x*log2(x)", "color": "orange", "label": "n log n"},
                    {"type": "fn", "expr": "x*(x+1)/2", "color": "red", "label": "T(n) = n(n+1)/2"},
                    {"type": "fn", "expr": "2**x/1000", "color": "purple", "label": "2ⁿ (skala /1000)"},
                ],
            },
        ],
    },
    # ── Tingkat Sulit ───────────────────────────────────────────────────────
    {
        "code": "FK-H1",
        "node": "fasilkom-ujian",
        "difficulty": "high",
        "is_diagnostic": True,
        "prompt": "Fungsi f(x, y) = x² + 4y² diminimalkan dengan gradient descent mulai (4, 1) dan laju belajar η = 0,1. "
                  "(a) Tentukan titik setelah 2 iterasi. (b) Tentukan rentang η agar iterasi konvergen ke (0, 0).",
        "options": [
            ("(a) (3,2; 0,2). (b) 0 &lt; η &lt; 1", False),
            ("(a) (2,56; 0,04). (b) 0 &lt; η &lt; 1", False),
            ("(a) (2,56; 0,04). (b) 0 &lt; η &lt; 1/4", True),
            ("(a) (1,6; 0,6). (b) 0 &lt; η &lt; 1/8", False),
        ],
        "steps": [
            "∇f = (2x, 8y). Update: x ← x − η·2x = (1 − 2η)x; y ← y − η·8y = (1 − 8η)y.",
            "Untuk η = 0,1: x ← 0,8x dan y ← 0,2y. Setelah k iterasi: (4·0,8ᵏ, 0,2ᵏ).",
            "(a) k = 1: (3,2; 0,2). k = 2: (2,56; 0,04).",
            "(b) Konvergen jika |1 − 2η| &lt; 1 dan |1 − 8η| &lt; 1. Syarat pertama: 0 &lt; η &lt; 1; syarat kedua: "
            "0 &lt; η &lt; 1/4. Keduanya terpenuhi bila 0 &lt; η &lt; 1/4.",
            "Catatan: arah y yang lebih curam membatasi η; inilah alasan mengapa fitur dengan skala berbeda memperlambat pelatihan.",
        ],
        "answer": "(a) (2,56; 0,04). (b) 0 &lt; η &lt; 1/4.",
        "graphs": [
            {
                "type": "2d",
                "title": "Gambar 4. Lintasan gradient descent pada garis kontur",
                "x": [-5, 5.5],
                "y": [-3, 3],
                "params": [
                    param("eta", "Laju belajar η (soal: 0,1)", 0.01, 0.3, 0.005, 0.1, "η"),
                    param("k", "Banyak iterasi (soal: 2)", 0, 25, 1, 2, "k"),
                ],
                "elements": [
                    *[{"type": "param", "t": [0, "2*pi"], "x": f"sqrt({c})*cos(t)", "y": f"sqrt({c})/2*sin(t)",
                       "color": "#BFDBFE", "width": 1.2} for c in (1, 4, 9, 16, 25)],
                    {"type": "iter", "id": "GD", "init": {"x": 4, "y": 1}, "update": {"x": "x - eta*2*x", "y": "y - eta*8*y"},
                     "steps": "k", "color": "red", "label": "lintasan (mulai (4, 1))"},
                ],
                "readouts": [
                    readout("xₖ = 4(1 − 2η)ᵏ", "GD.x", 5),
                    readout("yₖ = (1 − 8η)ᵏ", "GD.y", 5),
                    readout("|1 − 2η|", "abs(1-2*eta)", 4),
                    readout("|1 − 8η| (harus < 1)", "abs(1-8*eta)", 4),
                ],
                "caption": "Naikkan η melewati 0,25: komponen y mulai berosilasi dan membesar walaupun x masih mengecil.",
            }
        ],
    },
    {
        "code": "FK-H2",
        "node": "fasilkom-ujian",
        "difficulty": "high",
        "prompt": "Klasifikasi tiga kelas memakai softmax p<sub>i</sub> = e<sup>z<sub>i</sub></sup>/Σe<sup>z<sub>j</sub></sup> dan "
                  "kerugian L = −ln p₁ (kelas benar = 1). Untuk z = (2, 1, 0), hitung p dan gradien ∂L/∂z.",
        "options": [
            ("p ≈ (0,665; 0,245; 0,090) dan ∇<sub>z</sub>L ≈ (0,665; 0,245; 0,090)", False),
            ("p ≈ (0,667; 0,333; 0) dan ∇<sub>z</sub>L ≈ (−0,333; 0,333; 0)", False),
            ("p ≈ (0,665; 0,245; 0,090) dan ∇<sub>z</sub>L ≈ (0,335; −0,245; −0,090)", False),
            ("p ≈ (0,665; 0,245; 0,090) dan ∇<sub>z</sub>L ≈ (−0,335; 0,245; 0,090)", True),
        ],
        "steps": [
            "Penyebut: e² + e¹ + e⁰ ≈ 7,389 + 2,718 + 1 = 11,107.",
            "p₁ ≈ 0,6652; p₂ ≈ 0,2447; p₃ ≈ 0,0900 (jumlah = 1).",
            "Turunkan L = −z₁ + ln Σe<sup>z<sub>j</sub></sup>: ∂L/∂z<sub>k</sub> = −[k=1] + e<sup>z<sub>k</sub></sup>/Σe<sup>z<sub>j</sub></sup> = p<sub>k</sub> − [k=1].",
            "Jadi ∂L/∂z = (p₁ − 1, p₂, p₃) ≈ (−0,3348; 0,2447; 0,0900). Jumlah komponen = 0, sesuai sifat softmax.",
        ],
        "answer": "p ≈ (0,665; 0,245; 0,090) dan ∇<sub>z</sub>L ≈ (−0,335; 0,245; 0,090).",
        "graphs": [
            {
                "type": "2d",
                "title": "Gambar 5. Probabilitas softmax dan gradiennya",
                "x": [0.4, 3.6],
                "y": [-1.1, 1.15],
                "params": [
                    param("z1", "z₁ (soal: 2)", -3, 4, 0.05, 2, "z₁"),
                    param("z2", "z₂ (soal: 1)", -3, 4, 0.05, 1, "z₂"),
                    param("z3", "z₃ (soal: 0)", -3, 4, 0.05, 0, "z₃"),
                ],
                "elements": [
                    {"type": "bar", "x": 0.82, "w": 0.32, "h": SOFTMAX.format(k=1), "color": "blue", "label": "p (softmax)"},
                    {"type": "bar", "x": 1.82, "w": 0.32, "h": SOFTMAX.format(k=2), "color": "blue"},
                    {"type": "bar", "x": 2.82, "w": 0.32, "h": SOFTMAX.format(k=3), "color": "blue"},
                    {"type": "bar", "x": 1.18, "w": 0.32, "h": SOFTMAX.format(k=1) + " - 1", "color": "red",
                     "label": "gradien ∂L/∂z"},
                    {"type": "bar", "x": 2.18, "w": 0.32, "h": SOFTMAX.format(k=2), "color": "red"},
                    {"type": "bar", "x": 3.18, "w": 0.32, "h": SOFTMAX.format(k=3), "color": "red"},
                    {"type": "text", "x": 1, "y": -1.02, "text": "kelas 1 (benar)", "anchor": "middle", "color": "navy"},
                    {"type": "text", "x": 2, "y": -1.02, "text": "kelas 2", "anchor": "middle", "color": "navy"},
                    {"type": "text", "x": 3, "y": -1.02, "text": "kelas 3", "anchor": "middle", "color": "navy"},
                ],
                "readouts": [
                    readout("p₁", SOFTMAX.format(k=1)),
                    readout("p₂", SOFTMAX.format(k=2)),
                    readout("p₃", SOFTMAX.format(k=3)),
                    readout("L = −ln p₁", "-ln(" + SOFTMAX.format(k=1) + ")"),
                ],
                "caption": "Naikkan z₁: p₁ mendekati 1 dan seluruh gradien mendekati 0 (model sudah yakin benar).",
            }
        ],
    },
    {
        "code": "FK-H3",
        "node": "fasilkom-ujian",
        "difficulty": "high",
        "prompt": "Hampiri ∫<sub>0</sub><sup>1</sup> x² dx dengan aturan trapesium n = 4. (a) Hitung hampiran dan galatnya. "
                  "(b) Gunakan batas galat |E| ≤ (b−a)h²·max|f″|/12 untuk mencari n minimum agar galat &lt; 10<sup>−4</sup>.",
        "options": [
            ("(a) T = 0,34375; galat ≈ 0,0104. (b) n minimum = 40", False),
            ("(a) T = 0,3125; galat ≈ 0,0208. (b) n minimum = 41", False),
            ("(a) T = 0,34375; galat ≈ 0,0104. (b) n minimum = 1667", False),
            ("(a) T = 0,34375; galat ≈ 0,0104. (b) n minimum = 41", True),
        ],
        "steps": [
            "(a) h = 0,25; nilai f: 0; 0,0625; 0,25; 0,5625; 1.",
            "T = (h/2)[f₀ + 2(f₁+f₂+f₃) + f₄] = 0,125[0 + 2(0,875) + 1] = 0,125 × 2,75 = 0,34375.",
            "Eksak 1/3 ≈ 0,33333, galat ≈ 0,01042.",
            "(b) f″ = 2, jadi |E| ≤ 1·h²·2/12 = h²/6 dan h = 1/n. Perlu 1/(6n²) &lt; 10<sup>−4</sup> → n² &gt; 1666,7 → n &gt; 40,82.",
            "Karena n bilangan bulat, n minimum = 41.",
        ],
        "answer": "(a) T = 0,34375; galat ≈ 0,0104. (b) n minimum = 41.",
        "graphs": [
            {
                "type": "2d",
                "title": "Gambar 6. Trapesium menghampiri luas di bawah y = x²",
                "x": [-0.05, 1.05],
                "y": [-0.05, 1.1],
                "params": [param("n", "Banyak subselang n (soal: 4)", 1, 50, 1, 4, "n")],
                "elements": [
                    {"type": "riemann", "id": "T", "expr": "x*x", "from": 0, "to": 1, "n": "n", "mode": "trap", "color": "amber"},
                    {"type": "fn", "expr": "x*x", "color": "blue", "label": "y = x²"},
                ],
                "readouts": [
                    readout("Hampiran trapesium T", "T", 6),
                    readout("Galat T − 1/3", "T - 1/3", 6),
                    readout("Batas galat 1/(6n²)", "1/(6*n*n)", 6),
                    readout("Galat < 10⁻⁴ ? (1 = ya)", "1/(6*n*n) < 1e-4 ? 1 : 0", 0),
                ],
                "caption": "Galat trapesium untuk x² tepat 1/(6n²). Geser n ke 41 untuk melihat batas 10⁻⁴ terlampaui.",
            }
        ],
    },
]
