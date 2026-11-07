"""
Level Utama 3 — Kalkulus Tingkat Menengah.

Sub-level (masing-masing 4 topik × 5 sesi; soal dari gamification/generators/menengah/*):
  1. Teknik Pengintegralan          2. Aplikasi Integral
  3. Persamaan Diferensial Orde Satu 4. Irisan Kerucut & Koordinat Kutub
  5. Barisan dan Deret Tak Hingga

Konten lama: node umum-deret (berkas 1) dan soal U-S4 (berkas 3) digabung lewat ABSORB_*.
"""

from ..helpers import bullets, param, readout, table
from .l1_precalculus import g, ref
from .l2_kalkulus_dasar import S, T

MAIN_LEVEL = {"slug": "kalkulus-menengah", "order": 3, "title": "Kalkulus Tingkat Menengah",
              "subtitle": "Teknik & aplikasi integral, PD orde satu, kerucut & kutub, deret", "icon": "🌀"}


def fn(expr, color="blue", label=None, **kw):
    el = {"type": "fn", "expr": expr, "color": color}
    if label:
        el["label"] = label
    el.update(kw)
    return el


# ═════════════════════════ Sub-level 1: Teknik Pengintegralan ═══════════════
TEKNIK = [
    T("km-tek-parsial", "Integral Parsial", "🧷", "∫ u dv = uv − ∫ v du, LIATE, metode tabel, integral siklik.",
      "Stewart §7.1; Whitman §8.4; Strang §7.1", [
          S("Rumus integral parsial",
            "<p>Dari aturan perkalian (uv)′ = u′v + uv′ diperoleh <b>∫ u dv = uv − ∫ v du</b>. Pilih u yang menjadi lebih sederhana bila "
            "diturunkan (urutan LIATE: Logaritma, Invers trig, Aljabar, Trigonometri, Eksponen).</p>"
            + table(["Integral", "u", "dv", "Hasil"], [["∫ x eˣ dx", "x", "eˣ dx", "eˣ(x − 1) + C"], ["∫ ln x dx", "ln x", "dx", "x ln x − x + C"],
                                                       ["∫ x cos x dx", "x", "cos x dx", "x sin x + cos x + C"]])
            + "<p>Pangkat polinom tinggi: ulangi (metode tabel). eˣ sin x: parsial dua kali memunculkan integral semula (siklik).</p>"
            + ref("Stewart §7.1 Integration by Parts", "Whitman §8.4")),
      ]),
    T("km-tek-trig", "Integral Trigonometri & Substitusi Trig", "📐", "Pangkat sin/cos, setengah sudut, Wallis, x = a sin θ.",
      "Stewart §7.2–7.3; Whitman §8.2–8.3", [
          S("Pangkat fungsi trigonometri",
            bullets(["Pangkat ganjil: sisihkan satu faktor, ubah sisanya dengan sin² + cos² = 1, substitusi.",
                     "Pangkat genap: sin²x = (1 − cos 2x)/2, cos²x = (1 + cos 2x)/2.",
                     "Ortogonalitas: ∫₀^{2π} sin(mx)sin(nx) dx = 0 (m ≠ n), = π (m = n) — dasar deret Fourier."]),
            [g("Rata-rata sin²x adalah 1/2", [0, 6.3], [-0.2, 1.2], [param("k", "frekuensi k", 1, 5, 1, 1, "k")],
               [fn("sin(k*x)**2", "blue", "sin²(kx)"), fn("0.5", "red", "1/2", dash=True)], None, "Luas di atas dan di bawah garis 1/2 saling mengimbangi.")]),
          S("Substitusi trigonometri",
            table(["Bentuk", "Substitusi", "Identitas"], [["√(a² − x²)", "x = a sin θ", "1 − sin² = cos²"], ["√(a² + x²)", "x = a tan θ", "1 + tan² = sec²"],
                                                         ["√(x² − a²)", "x = a sec θ", "sec² − 1 = tan²"]])
            + "<p>Contoh: ∫₀ᵃ √(a² − x²) dx = πa²/4 (seperempat lingkaran).</p>"),
      ]),
    T("km-tek-pecahan", "Pecahan Parsial", "🧩", "Dekomposisi fungsi rasional: linear, berulang, kuadrat tak tereduksi.",
      "Stewart §7.4; Whitman §8.5", [
          S("Dekomposisi pecahan parsial",
            table(["Faktor penyebut", "Suku pecahan"], [["(x − a)", "A/(x − a)"], ["(x − a)²", "A/(x − a) + B/(x − a)²"], ["x² + bx + c (D < 0)", "(Ax + B)/(x² + bx + c)"]])
            + "<p>Jika derajat pembilang ≥ penyebut, bagi dulu (pembagian polinom). Hasil integral berupa ln|…| dan arctan(…).</p>"
            + "<p>Contoh: 1/(x² − 1) = (1/2)[1/(x − 1) − 1/(x + 1)] ⇒ ∫ = (1/2) ln|(x − 1)/(x + 1)| + C.</p>"),
      ]),
    T("km-tek-takwajar", "Integral Tak Wajar", "♾️", "Batas tak hingga, integran tak terbatas, uji banding.",
      "Stewart §7.8; Whitman §9.7; Strang §7.5", [
          S("Integral tak wajar",
            "<p>∫ₐ^∞ f dx = lim<sub>t→∞</sub> ∫ₐᵗ f dx; bila integran tak terbatas di c, ambil limit menuju c. Konvergen bila limit berhingga.</p>"
            + bullets(["∫₁^∞ dx/xᵖ konvergen ⇔ p > 1.", "∫₀¹ dx/xᵖ konvergen ⇔ p < 1.", "∫₀^∞ e^{−ax} dx = 1/a; ∫₀^∞ xⁿe⁻ˣ dx = n!.",
                       "Integral Gauss ∫_{−∞}^{∞} e^{−x²} dx = √π (FMIPA: distribusi normal)."]),
            [g("∫₁ᵗ 1/xᵖ dx untuk t → ∞", [0.8, 40], [0, 1.5], [param("pp", "p", 0.5, 3, 0.05, 2, "p"), param("t", "t", 1, 40, 0.5, 20, "t")],
               [{"type": "fill", "upper": "pow(x,-pp)", "from": 1, "to": "t", "color": "amber"}, fn("pow(x,-pp)", "blue", "1/xᵖ")],
               [readout("∫₁ᵗ", "pp==1?log(t):(pow(t,1-pp)-1)/(1-pp)", 4), readout("limit (p > 1)", "pp>1?1/(pp-1):Infinity", 4)],
               "Bandingkan p = 1 (divergen) dan p = 2 (konvergen ke 1).")]),
      ]),
]

# ═════════════════════════ Sub-level 2: Aplikasi Integral ══════════════════
APLIKASI = [
    T("km-apl-luas", "Luas Daerah Lanjutan", "🗺️", "Luas antara kurva, integral terhadap y, daerah berpotongan.", "Stewart §6.1; Whitman §9.1", [
        S("Luas antara kurva",
          "<p>Luas = ∫ₐᵇ [f(x) − g(x)] dx (atas − bawah) atau ∫ [kanan − kiri] dy. Cari titik potong; jika kurva bersilang, pecah interval.</p>",
          [g("Luas antara y = x² dan y = k − x²", [-4, 4], [-1, 12], [param("k", "k", 1, 10, 0.5, 8, "k")],
             [{"type": "fill", "upper": "k-x*x", "lower": "x*x", "from": "-sqrt(k/2)", "to": "sqrt(k/2)", "color": "amber"}, fn("x*x"), fn("k-x*x", "green")],
             [readout("Luas = (4/3)(k/2)^(3/2)·2", "8/3*pow(k/2,1.5)", 4)], "Geser k: titik potong ±√(k/2) dan luas berubah.")]),
    ]),
    T("km-apl-volume", "Volume Benda Putar", "🏺", "Metode cakram, cincin, kulit tabung, penampang, Pappus.",
      "Stewart §6.2–6.3; Whitman §9.3; Strang §8.3", [
          S("Tiga metode volume",
            table(["Metode", "Rumus", "Kapan"], [["Cakram", "π∫ f(x)² dx", "daerah menempel sumbu putar"], ["Cincin", "π∫ (R² − r²) dx", "ada lubang di tengah"],
                                                ["Kulit tabung", "2π∫ x f(x) dx", "diputar terhadap sumbu-y"], ["Penampang", "∫ A(x) dx", "penampang diketahui"]])
            + "<p>Teorema Pappus: V = luas daerah × keliling lintasan sentroid (torus: 2π²Rr²).</p>",
            [g("Benda putar y = √x (cakram)", [-0.5, 5], [-3, 3], [param("X", "posisi x", 0, 4, 0.01, 2, "x")],
               [{"type": "fill", "upper": "sqrt(x)", "lower": "-sqrt(x)", "from": 0, "to": 4, "color": "amber"}, fn("sqrt(x)"), fn("-sqrt(x)", dash=True),
                {"type": "segment", "x1": "X", "y1": "sqrt(X)", "x2": "X", "y2": "-sqrt(X)", "color": "red", "width": 3}],
               [readout("luas cakram πx", "pi*X", 4), readout("V = π∫₀⁴ x dx", "8*pi", 4)], "Setiap ruas merah adalah diameter satu cakram.")]),
      ]),
    T("km-apl-panjang", "Panjang Busur & Luas Permukaan", "📏", "L = ∫√(1 + y′²) dx, kurva parametrik, luas selimut.",
      "Stewart §8.1–8.2, §10.2; Whitman §9.9", [
          S("Panjang busur dan luas permukaan",
            bullets(["L = ∫ₐᵇ √(1 + f′(x)²) dx.", "Parametrik: L = ∫ √(x′(t)² + y′(t)²) dt.", "Luas permukaan putar: S = 2π∫ f(x)√(1 + f′(x)²) dx.",
                     "Kabel listrik menggantung berbentuk y = cosh x (catenary) — panjangnya sinh x (FT)."]),
            [g("Hampiran panjang busur dengan n ruas garis", [-0.2, 3.3], [-0.2, 3.5], [param("N", "banyak ruas n", 1, 30, 1, 3, "n")],
               [fn("x*sqrt(x)", "blue", "y = x^(3/2)", **{"from": 0}),
                {"type": "iter", "id": "P", "init": {"x": 0}, "update": {"x": "x+3/N"}, "steps": "N", "px": "x", "py": "x*sqrt(x)", "color": "red"}],
               [readout("Panjang eksak ∫₀³ √(1 + 9x/4) dx", "(8/27)*(pow(1+27/4,1.5)-1)", 5)], "Semakin banyak ruas, poligon semakin dekat ke kurva.")]),
      ]),
    T("km-apl-fisika", "Terapan: Kerja, Pusat Massa & Peluang", "⚙️", "Kerja pegas & pompa, sentroid, fungsi kepadatan peluang.",
      "Stewart §6.4, §8.3, §8.5; Strang §8.5–8.6", [
          S("Integral dalam fisika dan peluang",
            bullets(["Kerja gaya variabel W = ∫ F(x) dx; pegas F = kx (Hooke).", "Memompa cairan: W = ∫ (ρg · luas irisan · jarak angkat) dy.",
                     "Pusat massa x̄ = ∫ xρ dx / ∫ ρ dx; sentroid daerah x̄ = (1/A)∫ x f(x) dx.",
                     "Fungsi kepadatan f ≥ 0, ∫ f = 1, P(a ≤ X ≤ b) = ∫ₐᵇ f dx (FMIPA statistika)."])
            + ref("Stewart §6.4 Work", "Stewart §8.5 Probability")),
      ]),
]

# ═════════════════════════ Sub-level 3: PD Orde Satu ═══════════════════════
PD = [
    T("km-pd-konsep", "Konsep PD & Medan Arah", "🧭", "Solusi PD, medan arah, metode Euler, ekuilibrium.", "Stewart §9.1–9.2; Strang §6.7", [
        S("Persamaan diferensial",
          "<p>PD orde satu y′ = f(x, y) menetapkan gradien solusi di setiap titik. <b>Medan arah</b> menggambarkan gradien itu; <b>metode Euler</b> "
          "yₙ₊₁ = yₙ + h·f(xₙ, yₙ) mengikutinya langkah demi langkah. PD otonom y′ = f(y): ekuilibrium di akar f.</p>",
          [g("Euler untuk y′ = y, y(0) = 1", [0, 2.2], [0, 9], [param("hh", "h", 0.05, 0.5, 0.05, 0.5, "h")],
             [fn("exp(x)", "blue", "eˣ (eksak)"),
              {"type": "iter", "id": "E", "init": {"x": 0, "y": 1}, "update": {"x": "x+hh", "y": "y+hh*y"}, "steps": "floor(2/hh)", "px": "x", "py": "y", "color": "red"}],
             None, "Galat Euler mengecil sebanding dengan h.")]),
    ]),
    T("km-pd-terpisah", "PD Terpisah", "✂️", "dy/h(y) = g(x) dx, syarat awal, solusi yang meledak.", "Stewart §9.3; Whitman §17.1; Strang §6.3", [
        S("Memisahkan variabel",
          "<p>Jika y′ = g(x)h(y), tulis dy/h(y) = g(x) dx lalu integralkan kedua ruas. Contoh: y′ = 2xy ⇒ ln|y| = x² + C ⇒ y = Ae^{x²}. "
          "y′ = y² dengan y(0) = 1/a ⇒ y = 1/(a − x), meledak di x = a.</p>"),
    ]),
    T("km-pd-linear", "PD Linear Orde Satu", "📏", "Faktor integrasi μ = e^{∫P dx}, keadaan tunak, rangkaian RC.", "Stewart §9.5; Strang §6.5", [
        S("Faktor integrasi",
          "<p>y′ + P(x)y = Q(x). Kalikan μ = e^{∫P dx}: (μy)′ = μQ ⇒ y = (1/μ)[∫ μQ dx + C]. Koefisien konstan y′ + ay = b: y = b/a + Ce^{−ax} "
          "(keadaan tunak b/a). Rangkaian RC (FT): q(t) = EC(1 − e^{−t/RC}).</p>",
          [g("Rangkaian RC: q(t) = EC(1 − e^(−t/RC))", [0, 10], [0, 12], [param("tau", "τ = RC", 0.5, 5, 0.1, 2, "τ"), param("Q", "EC", 2, 10, 0.5, 10, "EC")],
             [fn("Q*(1-exp(-x/tau))", "blue", "q(t)"), fn("Q", "red", dash=True)], [readout("q(τ) = 63% EC", "Q*(1-exp(-1))", 3)], "Setelah satu τ, muatan mencapai ≈ 63%.")]),
    ]),
    T("km-pd-model", "Model: Pertumbuhan, Pendinginan, Logistik", "🌱", "Bunga kontinu, peluruhan, hukum Newton, logistik, campuran.",
      "Stewart §9.4, §9.3; Strang §6.3, §6.6", [
          S("Model PD baku",
            table(["Model", "PD", "Solusi"], [["Pertumbuhan/peluruhan", "y′ = ky", "y₀e^{kt}"], ["Pendinginan Newton", "T′ = −k(T − Tₛ)", "Tₛ + (T₀ − Tₛ)e^{−kt}"],
                                              ["Logistik", "P′ = rP(1 − P/K)", "K/(1 + Ae^{−rt})"], ["Campuran", "s′ = masuk − keluar", "linear orde satu"]]),
            [g("Logistik vs eksponensial", [0, 10], [0, 120], [param("r", "r", 0.2, 2, 0.1, 0.8, "r")],
               [fn("100/(1+9*exp(-r*x))", "blue", "logistik K = 100"), fn("10*exp(r*x)", "orange", "eksponensial", dash=True), fn("100", "red", dash=True)], None,
               "Awalnya sama, lalu logistik melandai ke daya tampung K.")]),
      ]),
]

# ═════════════════════════ Sub-level 4: Irisan Kerucut & Koordinat Kutub ════
KERUCUT = [
    T("km-ker-parabola", "Parabola", "🥣", "Fokus, direktriks, bentuk baku, sifat pantul.", "Stewart §10.5; Whitman §10.1", [
        S("Parabola",
          "<p>Himpunan titik berjarak sama ke fokus dan direktriks. y² = 4px: fokus (p, 0), direktriks x = −p; x² = 4py: fokus (0, p). "
          "Sinar sejajar sumbu dipantulkan ke fokus — antena parabola, lampu sorot (FT).</p>",
          [g("Parabola x² = 4py", [-8, 8], [-3, 10], [param("p", "p", 0.25, 3, 0.25, 1, "p")],
             [fn("x*x/(4*p)", "blue", "parabola"), {"type": "point", "x": 0, "y": "p", "color": "red", "label": "fokus"}, fn("-p", "gray", "direktriks", dash=True)],
             None, "p besar ⇒ parabola melebar, fokus menjauh.")]),
    ]),
    T("km-ker-elips", "Elips & Hiperbola", "🪐", "Sumbu, fokus, eksentrisitas, asimtot, orbit.", "Stewart §10.5–10.6; Whitman §10.2–10.3", [
        S("Elips dan hiperbola",
          table(["Kurva", "Persamaan", "Fokus", "Catatan"], [["Elips", "x²/a² + y²/b² = 1", "c² = a² − b²", "e = c/a < 1"],
                                                          ["Hiperbola", "x²/a² − y²/b² = 1", "c² = a² + b²", "asimtot y = ±(b/a)x"]])
          + "<p>Jenis kerucut Ax² + Bxy + Cy² + … = 0: B² − 4AC &lt; 0 elips, = 0 parabola, &gt; 0 hiperbola. Orbit planet = elips (Kepler).</p>",
          [g("Elips dengan eksentrisitas e", [-6, 6], [-5, 5], [param("ee", "e", 0, 0.95, 0.01, 0.6, "e")],
             [{"type": "param", "t": [0, "2*pi"], "x": "5*cos(t)", "y": "5*sqrt(1-ee*ee)*sin(t)", "color": "blue"},
              {"type": "point", "x": "5*ee", "y": 0, "color": "red"}, {"type": "point", "x": "-5*ee", "y": 0, "color": "red"}],
             [readout("b = a√(1 − e²)", "5*sqrt(1-ee*ee)", 3)], "e = 0 lingkaran; e → 1 sangat pipih.")]),
    ]),
    T("km-kut-koordinat", "Koordinat Kutub", "🎯", "Konversi (r, θ) ↔ (x, y), persamaan & kurva kutub.", "Stewart §10.3; Whitman §10.4; Strang §9.2", [
        S("Koordinat kutub",
          "<p>x = r cos θ, y = r sin θ, r² = x² + y², tan θ = y/x. Kurva baku: lingkaran r = a, r = 2a cos θ; kardioid r = a(1 + cos θ); mawar r = a cos(nθ) "
          "(n ganjil: n kelopak, genap: 2n); spiral r = aθ.</p>",
          [g("Mawar r = cos(nθ)", [-1.3, 1.3], [-1.3, 1.3], [param("nn", "n", 1, 7, 1, 3, "n")],
             [{"type": "param", "t": [0, "2*pi"], "x": "cos(nn*t)*cos(t)", "y": "cos(nn*t)*sin(t)", "color": "blue", "samples": 500}], None,
             "Hitung kelopak untuk n ganjil dan genap.")]),
    ]),
    T("km-kut-kalkulus", "Kalkulus Kutub & Parametrik", "🌀", "dy/dx parametrik/kutub, luas kutub, sikloida.", "Stewart §10.2, §10.4; Whitman §10.5", [
        S("Turunan dan luas",
          bullets(["Parametrik: dy/dx = (dy/dt)/(dx/dt); luas ∫ y dx.", "Kutub: dy/dx = (r′ sin θ + r cos θ)/(r′ cos θ − r sin θ).",
                   "Luas kutub A = (1/2)∫ r² dθ (sektor tipis).", "Sikloida: panjang 8r, luas 3πr²."]),
          [g("Luas kutub sebagai jumlah sektor", [-1, 3], [-2, 2], [param("th", "θ batas", 0.1, 6.28, 0.01, 3, "θ")],
             [{"type": "param", "t": [0, "2*pi"], "x": "(1+cos(t))*cos(t)", "y": "(1+cos(t))*sin(t)", "color": "gray"},
              {"type": "param", "t": [0, "th"], "x": "(1+cos(t))*cos(t)", "y": "(1+cos(t))*sin(t)", "color": "blue", "width": 3}],
             [readout("(1/2)∫₀^θ (1 + cos t)² dt", "0.5*(1.5*th+2*sin(th)+sin(2*th)/4)", 4)], "Untuk θ = 2π luasnya 3π/2 (kardioid).")]),
    ]),
]

# ═════════════════════════ Sub-level 5: Barisan & Deret ════════════════════
DERET = [
    T("km-der-barisan", "Barisan & Limitnya", "🔢", "Limit barisan, teorema apit, barisan monoton & rekursif.", "Stewart §11.1; Whitman §11.1; Strang §10.1", [
        S("Barisan",
          "<p>aₙ → L bila suku-suku mendekati L. Alat: limit fungsi (aₙ = f(n)), teorema apit, dan teorema barisan monoton (monoton + terbatas ⇒ konvergen). "
          "Barisan rekursif aₙ₊₁ = (aₙ + c/aₙ)/2 adalah metode Newton untuk √c (Fasilkom).</p>",
          [g("Barisan Newton menuju √c", [0, 10], [0, 12], [param("c", "c", 2, 50, 1, 10, "c"), param("a1", "a₁", 0.5, 10, 0.5, 1, "a₁")],
             [{"type": "iter", "id": "N", "init": {"k": 1, "a": "a1"}, "update": {"k": "k+1", "a": "(a+c/a)/2"}, "steps": 8, "px": "k", "py": "a", "color": "blue"},
              fn("sqrt(c)", "red", dash=True)], [readout("√c", "sqrt(c)", 6)], "Konvergen sangat cepat (kuadratik).")]),
    ]),
    T("km-der-geometri", "Deret Geometri & Teleskopik", "🪜", "Σ arⁿ = a/(1 − r), deret teleskopik, desimal berulang.", "Stewart §11.2; Whitman §11.2", [
        S("Deret geometri",
          "<p>Σ arⁿ konvergen ⇔ |r| &lt; 1, jumlahnya a/(1 − r). Deret teleskopik: suku berbentuk selisih bₙ − bₙ₊₁ sehingga jumlah parsial = b₁ − bₙ₊₁. "
          "Deret harmonik Σ 1/n divergen walau sukunya → 0.</p>",
          [g("Jumlah parsial Σ rⁿ", [0, 25], [-1, 11], [param("rr", "r", -0.95, 0.95, 0.05, 0.8, "r")],
             [{"type": "iter", "id": "P", "init": {"k": 0, "s": 1}, "update": {"k": "k+1", "s": "s+pow(rr,k+1)"}, "steps": 24, "px": "k", "py": "s", "color": "blue"},
              fn("1/(1-rr)", "red", dash=True)], [readout("1/(1 − r)", "1/(1-rr)", 4)], "")]),
    ]),
    T("km-der-uji", "Uji Kekonvergenan", "🧪", "Uji divergensi, integral, p-deret, banding, rasio, deret bergantian.", "Stewart §11.3–11.7; Whitman §11.3–11.7", [
        S("Strategi uji deret",
          table(["Uji", "Kapan", "Kesimpulan"], [["Suku ke-n", "selalu dicek dulu", "aₙ ↛ 0 ⇒ divergen"], ["Deret-p / integral", "1/nᵖ, f(n) turun", "p > 1 konvergen"],
                                                ["Banding (limit)", "mirip deret diketahui", "ikut deret pembanding"], ["Rasio", "faktorial, cⁿ", "L < 1 konvergen"],
                                                ["Bergantian", "(−1)ⁿbₙ", "bₙ ↓ 0 ⇒ konvergen"]])),
      ]),
    T("km-der-pangkat", "Deret Pangkat & Taylor", "🎛️", "Jari-jari & interval konvergensi, deret Maclaurin baku.", "Stewart §11.8–11.11; Whitman §11.8–11.11; Strang §10.4", [
        S("Deret pangkat dan Taylor",
          "<p>Σ cₙ(x − a)ⁿ konvergen pada interval berjari-jari R (uji rasio), ujung diuji terpisah. Taylor: cₙ = f⁽ⁿ⁾(a)/n!.</p>"
          + table(["Fungsi", "Deret Maclaurin", "Berlaku"], [["eˣ", "Σ xⁿ/n!", "semua x"], ["sin x", "x − x³/3! + x⁵/5! − …", "semua x"],
                                                          ["cos x", "1 − x²/2! + x⁴/4! − …", "semua x"], ["1/(1 − x)", "Σ xⁿ", "|x| < 1"], ["ln(1 + x)", "x − x²/2 + x³/3 − …", "−1 < x ≤ 1"]]),
          [g("Polinom Taylor sin x", [-7, 7], [-3, 3], [param("N", "derajat N", 1, 15, 2, 3, "N")],
             [fn("sin(x)", "blue", "sin x"), fn("sum(0,(N-1)/2,k=>pow(-1,k)*pow(x,2*k+1)/fact(2*k+1))", "red", "Tₙ", dash=True)], None,
             "Polinom Taylor hanya akurat di dekat 0; naikkan N untuk jangkauan lebih luas.")]),
    ]),
]

SUBLEVELS = [
    {"slug": "km-teknik-integral", "title": "Teknik Pengintegralan", "subtitle": "Parsial, trigonometri, pecahan parsial, tak wajar", "icon": "🧰",
     "badge_label": "Kalkulus Menengah", "summary_html": "<p>Alat-alat untuk menghitung integral yang tidak dapat diselesaikan substitusi sederhana.</p>", "topics": TEKNIK},
    {"slug": "km-aplikasi-integral", "title": "Aplikasi Integral", "subtitle": "Luas, volume, panjang busur, kerja, peluang", "icon": "🏗️",
     "badge_label": "Kalkulus Menengah", "summary_html": "<p>Integral sebagai penjumlahan potongan kecil dalam geometri, fisika (FT), dan statistika (FMIPA).</p>", "topics": APLIKASI},
    {"slug": "km-pd-orde-satu", "title": "Persamaan Diferensial Orde Satu", "subtitle": "Terpisah, linear, dan model nyata", "icon": "🌱",
     "badge_label": "Kalkulus Menengah", "summary_html": "<p>Memodelkan perubahan: pertumbuhan, pendinginan, rangkaian listrik, populasi.</p>", "topics": PD},
    {"slug": "km-kerucut-kutub", "title": "Irisan Kerucut & Koordinat Kutub", "subtitle": "Parabola, elips, hiperbola, kurva kutub", "icon": "🪐",
     "badge_label": "Kalkulus Menengah", "summary_html": "<p>Kurva-kurva klasik dan cara baru mendeskripsikan bidang dengan (r, θ).</p>", "topics": KERUCUT},
    {"slug": "km-barisan-deret", "title": "Barisan dan Deret Tak Hingga", "subtitle": "Konvergensi, uji deret, deret Taylor", "icon": "🔁",
     "badge_label": "Kalkulus Menengah", "summary_html": "<p>Menjumlahkan tak hingga banyak suku dan menghampiri fungsi dengan polinom.</p>", "topics": DERET},
]

ABSORB_NODES = {"umum-deret": "km-barisan-deret"}
ABSORB_SECTIONS = {("umum-deret", "Uji kekonvergenan deret"): "km-der-uji", ("umum-deret", "Deret Maclaurin"): "km-der-pangkat"}
# U-S4 (integral parsial) saat ini berada di sub-level kd-integral (Level 2) tanpa sesi.
FIXED_QUESTIONS = {}
MOVE_QUESTIONS = {"U-S4": ("km-tek-parsial", 3)}
