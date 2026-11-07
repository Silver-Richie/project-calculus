"""
Level Utama 4 — Kalkulus Tingkat Lanjut, JALUR TERPISAH PER FAKULTAS.

Setiap fakultas (FT, FMIPA, Fasilkom) memiliki 5 sub-level sendiri (SkillNode.faculty diisi):
  1. Kalkulus Peubah Banyak   2. Turunan Parsial   3. Integral Lipat
  4. Kalkulus Vektor          5. Fungsi Khusus (& Analisis Real)
Tiap sub-level berisi 2 topik INTI (materi & generator sama untuk ketiga fakultas)
dan 1 topik TERAPAN khusus fakultas (generator di gamification/generators/lanjut/{ft,fm,fk}.py).

Konten lama (node ft/fmipa/fasilkom-konsep/terapan/ujian dan umum-dua-variabel) digabung lewat ABSORB_*.
"""

from ..helpers import bullets, param, readout, table
from .l1_precalculus import g, ref
from .l2_kalkulus_dasar import S, T

MAIN_LEVEL = {"slug": "kalkulus-lanjut", "order": 4, "title": "Kalkulus Tingkat Lanjut",
              "subtitle": "Jalur khusus fakultas: peubah banyak, turunan parsial, integral lipat, kalkulus vektor, fungsi khusus", "icon": "🛰️"}

FACULTIES = {"ft": ("ft", "FT"), "fm": ("fmipa", "FMIPA"), "fk": ("fasilkom", "Fasilkom")}


def fn(expr, color="blue", label=None, **kw):
    el = {"type": "fn", "expr": expr, "color": color}
    if label:
        el["label"] = label
    el.update(kw)
    return el


def surface(title, z_expr, caption, params=None, rng_=2):
    """Permukaan 3D z = f(x, y) (GraphLab 3D, kamera dapat diputar)."""
    return {"type": "3d", "title": title, "params": params or [],
            "surfaces": [{"u": [-rng_, rng_], "v": [-rng_, rng_], "x": "u", "y": "v", "z": z_expr.replace("x", "u").replace("y", "v")}],
            "caption": caption}


# ═══════════════════════════ Materi topik INTI (dipakai 3 fakultas) ════════
CORE = {
    "pb-fungsi": ("Fungsi Dua Variabel & Kurva Tingkat", "🗻", "Domain, grafik permukaan, kurva tingkat, kuadrik.", "Stewart §14.1, §12.6; Whitman §14.1; Strang §13.1", [
        S("Fungsi z = f(x, y)",
          "<p>Fungsi dua variabel memasangkan titik (x, y) di domain D ⊂ ℝ² dengan satu bilangan. Grafiknya permukaan di ℝ³; "
          "<b>kurva tingkat</b> f(x, y) = k adalah ‘garis kontur’ seperti pada peta topografi.</p>"
          + table(["f(x, y)", "Kurva tingkat", "Permukaan"], [["x² + y²", "lingkaran", "paraboloid"], ["x² − y²", "hiperbola", "pelana"],
                                                            ["√(x² + y²)", "lingkaran berjarak sama", "kerucut"], ["ax + by", "garis sejajar", "bidang"]]),
          [surface("Permukaan z = a·x² + b·y²", "a*x*x+b*y*y", "Ubah b menjadi negatif: mangkuk berubah menjadi pelana.",
                   [param("a", "a", -2, 2, 0.1, 1, "a"), param("b", "b", -2, 2, 0.1, 1, "b")])]),
    ]),
    "pb-limit": ("Limit & Kekontinuan Multivariabel", "🎯", "Uji jalur, koordinat kutub, kekontinuan.", "Stewart §14.2; Whitman §14.2", [
        S("Limit dua variabel",
          "<p>lim<sub>(x,y)→(a,b)</sub> f = L bila f mendekati L dari <b>semua</b> arah. Jika dua jalur memberi nilai berbeda, limit tidak ada. "
          "Koordinat kutub membantu: bila |f − L| ≤ g(r) → 0 tanpa bergantung θ, limit ada.</p>",
          [g("Nilai (x² − y²)/(x² + y²) sepanjang garis y = mx", [-0.5, 3], [-1.2, 1.2], [param("m", "gradien jalur m", -3, 3, 0.05, 1, "m")],
             [fn("(1-m*m)/(1+m*m)+0*x", "blue", "nilai di sepanjang jalur")], [readout("limit jalur", "(1-m*m)/(1+m*m)", 4)],
             "Nilai berubah dengan m ⇒ limit di (0, 0) tidak ada.")]),
    ]),
    "tp-parsial": ("Turunan Parsial & Aturan Rantai", "∂", "f_x, f_y, orde dua, Clairaut, aturan rantai, turunan implisit.", "Stewart §14.3, §14.5; Whitman §14.3–14.5; Strang §13.2", [
        S("Turunan parsial",
          "<p>∂f/∂x: turunkan terhadap x dengan y dianggap konstan (kemiringan irisan y = konstan). Orde dua: f<sub>xx</sub>, f<sub>xy</sub>, f<sub>yy</sub>; "
          "Clairaut: f<sub>xy</sub> = f<sub>yx</sub> bila kontinu. Aturan rantai: dz/dt = z<sub>x</sub>x′ + z<sub>y</sub>y′; implisit ∂z/∂x = −F<sub>x</sub>/F<sub>z</sub>.</p>",
          [surface("Irisan z = x²y pada y tetap", "x*x*y", "Turunan parsial = kemiringan kurva irisan.", rng_=2)]),
    ]),
    "tp-gradien": ("Gradien, Turunan Berarah & Bidang Singgung", "🧭", "∇f, D_u f = ∇f·u, laju maksimum, linearisasi.", "Stewart §14.4, §14.6; Whitman §14.5; Strang §13.4", [
        S("Gradien",
          bullets(["∇f = ⟨f<sub>x</sub>, f<sub>y</sub>⟩ tegak lurus kurva tingkat.", "Turunan berarah D<sub>u</sub>f = ∇f·u (u vektor satuan).",
                   "Laju kenaikan maksimum |∇f| ke arah ∇f; penurunan tercepat ke arah −∇f (dasar gradient descent).",
                   "Bidang singgung: z = f(a, b) + f<sub>x</sub>(x − a) + f<sub>y</sub>(y − b)."]),
          [g("Gradien tegak lurus kurva tingkat x² + 2y² = k", [-3, 3], [-3, 3], [param("t", "posisi pada kurva", 0, 6.28, 0.01, 0.8, "t")],
             [{"type": "param", "t": [0, "2*pi"], "x": "2*cos(t)", "y": "sqrt(2)*sin(t)", "color": "gray"},
              {"type": "segment", "x1": "2*cos(t)", "y1": "sqrt(2)*sin(t)", "x2": "2*cos(t)+0.3*4*cos(t)", "y2": "sqrt(2)*sin(t)+0.3*4*sqrt(2)*sin(t)", "color": "red", "arrow": True}],
             None, "Panah merah = ∇f, selalu tegak lurus kontur.")]),
    ]),
    "il-ganda": ("Integral Ganda", "▦", "Fubini, daerah umum, menukar urutan, volume.", "Stewart §15.1–15.3; Whitman §15.1–15.2; Strang §14.1–14.2", [
        S("Integral ganda",
          "<p>∬<sub>D</sub> f dA = volume di bawah z = f di atas D (bila f ≥ 0). Teorema Fubini: hitung sebagai integral berulang. Daerah tipe I: "
          "g₁(x) ≤ y ≤ g₂(x); tipe II: h₁(y) ≤ x ≤ h₂(y). Menukar urutan bisa membuat integral mustahil menjadi mudah (∫∫ e^{y²}).</p>",
          [g("Jumlah Riemann ganda menuju volume", [-0.2, 2.2], [-0.2, 2.2], [param("N", "grid n×n", 1, 20, 1, 4, "n")],
             [{"type": "param", "t": [0, 2], "x": "t", "y": "0", "color": "gray"}, {"type": "text", "x": 1, "y": 1.1, "text": "Σ f(xᵢ, yⱼ)ΔA → ∬ f dA"}],
             [readout("ΔA = (2/n)²", "4/(N*N)", 4)], "Semakin halus grid, jumlah Riemann semakin dekat ke integral.")]),
    ]),
    "il-koordinat": ("Integral Lipat: Kutub, Silinder & Bola", "🌐", "dA = r dr dθ, dV = r dz dr dθ, dV = ρ² sin φ dρ dφ dθ.",
                     "Stewart §15.3, §15.7–15.9; Whitman §15.3–15.5", [
        S("Penggantian koordinat",
          table(["Sistem", "Elemen", "Cocok untuk"], [["Kutub", "r dr dθ", "cakram, cincin"], ["Silinder", "r dz dr dθ", "tabung, paraboloid"],
                                                      ["Bola", "ρ² sin φ dρ dφ dθ", "bola, kerucut"]])
          + "<p>Contoh: ∬<sub>ℝ²</sub> e<sup>−(x²+y²)</sup> dA = π ⇒ ∫ e<sup>−x²</sup> dx = √π.</p>"),
    ]),
    "kv-medan": ("Medan Vektor, Divergensi & Curl", "🌪️", "Medan vektor, div F, curl F, medan konservatif.", "Stewart §16.1, §16.5; Whitman §16.1; Strang §15.1", [
        S("Divergensi dan curl",
          "<p>Medan vektor F = ⟨P, Q, R⟩. <b>div F</b> = P<sub>x</sub> + Q<sub>y</sub> + R<sub>z</sub> (sumber/sumur); <b>curl F</b> = ∇ × F (rotasi). "
          "F konservatif (F = ∇f) ⇔ curl F = 0 pada daerah terhubung sederhana.</p>",
          [g("Medan F = ⟨−ay, x⟩ + b⟨x, y⟩", [-3, 3], [-3, 3], [param("a", "komponen rotasi", -1, 1, 0.1, 1, "a"), param("b", "komponen sumber", -1, 1, 0.1, 0, "b")],
             [{"type": "segment", "x1": i, "y1": j, "x2": f"{i}+0.3*(-a*({j})+b*({i}))", "y2": f"{j}+0.3*(a*({i})+b*({j}))", "color": "blue", "arrow": True, "width": 1.4}
              for i in (-2, -1, 0, 1, 2) for j in (-2, -1, 0, 1, 2)],
             [readout("div F = 2b", "2*b", 2), readout("curl F = 2a", "2*a", 2)], "a mengatur pusaran (curl), b mengatur sumber (divergensi).")]),
    ]),
    "kv-garis": ("Integral Garis & Teorema Green", "🔄", "∫ f ds, ∫ F·dr, teorema fundamental, Green.", "Stewart §16.2–16.4; Whitman §16.2–16.4; Strang §15.2–15.3", [
        S("Integral garis dan Green",
          bullets(["∫<sub>C</sub> f ds = ∫ f(r(t))|r′(t)| dt (massa kawat).", "∫<sub>C</sub> F·dr = ∫ F(r(t))·r′(t) dt (kerja).",
                   "Medan konservatif: ∫ ∇f·dr = f(B) − f(A).", "Green: ∮<sub>C</sub> P dx + Q dy = ∬<sub>D</sub> (Q<sub>x</sub> − P<sub>y</sub>) dA."])),
    ]),
    "fk-gamma": ("Fungsi Gamma, Beta & Error", "Γ", "Γ(n) = (n − 1)!, Γ(1/2) = √π, fungsi Beta, erf.", "Stewart §7.8 (latihan), Whitman §9.7; Strang §7.5", [
        S("Fungsi khusus",
          table(["Fungsi", "Definisi", "Sifat"], [["Γ(x)", "∫₀^∞ t^{x−1}e^{−t} dt", "Γ(x + 1) = xΓ(x), Γ(n) = (n − 1)!"],
                                                  ["B(a, b)", "∫₀¹ t^{a−1}(1 − t)^{b−1} dt", "Γ(a)Γ(b)/Γ(a + b)"], ["erf(x)", "(2/√π)∫₀ˣ e^{−t²} dt", "erf(∞) = 1"]]),
          [g("Fungsi Gamma memperluas faktorial", [0.1, 5.5], [0, 25], [param("X", "x", 0.2, 5.4, 0.01, 4, "x")],
             [{"type": "point", "x": "X", "y": "fact(floor(X)-1)", "color": "blue", "label": "(n − 1)! untuk n = ⌊x⌋"}, {"type": "point", "x": 1, "y": 1, "color": "red"}, {"type": "point", "x": 2, "y": 1, "color": "red"},
              {"type": "point", "x": 3, "y": 2, "color": "red"}, {"type": "point", "x": 4, "y": 6, "color": "red"}, {"type": "point", "x": 5, "y": 24, "color": "red"}],
             None, "Titik merah: Γ(n) = (n − 1)! — Gamma adalah kurva mulus yang melalui semuanya.")]),
    ]),
    "fk-analisis": ("Dasar Analisis Real", "∀", "Supremum, sifat Archimedes, definisi ε–N, barisan Cauchy.", "Stewart Lamp. F & §11.1; Whitman §11.1", [
        S("Bahasa analisis real",
          "<p><b>Aksioma kelengkapan</b>: setiap himpunan tak kosong terbatas di atas punya supremum. <b>Sifat Archimedes</b>: untuk ε &gt; 0 ada n dengan 1/n &lt; ε. "
          "<b>Limit barisan</b>: ∀ε &gt; 0 ∃N ∀n ≥ N: |aₙ − L| &lt; ε. Barisan Cauchy di ℝ selalu konvergen; teorema Bolzano–Weierstrass.</p>",
          [g("Definisi ε–N: setelah N semua suku masuk pita ε", [0, 40], [0, 3], [param("eps", "ε", 0.02, 0.5, 0.01, 0.1, "ε")],
             [{"type": "hband", "from": "2-eps", "to": "2+eps", "color": "red"},
              {"type": "iter", "id": "A", "init": {"k": 1}, "update": {"k": "k+1"}, "steps": 39, "px": "k", "py": "(2*k+2)/k", "color": "blue"},
              {"type": "vline", "x": "2/eps", "color": "green", "dash": True}], [readout("N = 2/ε", "2/eps", 2)], "aₙ = (2n + 2)/n; garis hijau = N.")]),
    ]),
}

# ═══════════════════════════ Materi topik TERAPAN per fakultas ═════════════
APPLIED = {
    "ft": {
        "pb": ("kl-ft-galat", "Medan Suhu & Analisis Galat", "🌡️", "Medan skalar teknik, diferensial total, galat relatif pengukuran.", "Stewart §14.4; Strang §13.3", [
            S("Diferensial total dalam rekayasa",
              "<p>dz = f<sub>x</sub>dx + f<sub>y</sub>dy menaksir perubahan kecil. Galat relatif produk pangkat V = πr²h: dV/V = 2dr/r + dh/h — dipakai "
              "untuk toleransi manufaktur & kalibrasi alat ukur. Medan suhu T(x, y): panas mengalir ke arah −∇T.</p>")]),
        "tp": ("kl-ft-lagrange", "Optimasi Desain & Pengali Lagrange", "📦", "Ekstrem dua variabel dan optimasi berkendala.", "Stewart §14.7–14.8; Strang §13.5–13.6", [
            S("Pengali Lagrange",
              "<p>Optimumkan f dengan kendala g = c: selesaikan ∇f = λ∇g bersama g = c. Contoh: kotak tanpa tutup volume tetap ⇒ x = y = 2z; "
              "x + y + z = S memaksimumkan xyz saat x = y = z.</p>",
              [g("Kendala lingkaran dan kontur x + y = k", [-3, 3], [-3, 3], [param("k", "nilai f = x + y", -3, 3, 0.05, 2, "k")],
                 [{"type": "param", "t": [0, "2*pi"], "x": "2*cos(t)", "y": "2*sin(t)", "color": "blue"}, fn("k-x", "red", "x + y = k", dash=True)],
                 [readout("maksimum 2√2", "2*sqrt(2)", 4)], "Kontur terjauh yang masih menyentuh lingkaran menyinggungnya: ∇f ∥ ∇g.")])]),
        "il": ("kl-ft-massa", "Massa, Momen Inersia & Pusat Massa", "⚙️", "Lamina, momen inersia penampang, sentroid, RMS.", "Stewart §15.4; Strang §14.3", [
            S("Integral lipat dalam mekanika",
              bullets(["Massa m = ∬ ρ dA; pusat massa x̄ = ∬ xρ dA / m.", "Momen inersia luas I<sub>x</sub> = ∬ y² dA (kekakuan balok: bh³/12).",
                       "Momen inersia polar I₀ = ∬ (x² + y²) dA (poros: πR⁴/2).", "Nilai RMS arus AC: V₀/√2."]))]),
        "kv": ("kl-ft-fluks", "Fluks, Teorema Divergensi & Stokes", "⚡", "Fluks, hukum Gauss, teorema divergensi, Stokes & Ampère.", "Stewart §16.7–16.9; Strang §15.4–15.6", [
            S("Teorema integral vektor",
              table(["Teorema", "Rumus", "Fisika (FT)"], [["Divergensi", "∯ F·n dS = ∭ div F dV", "Hukum Gauss listrik"],
                                                         ["Stokes", "∮ F·dr = ∬ (curl F)·n dS", "Hukum Ampère / Faraday"],
                                                         ["Green", "∮ P dx + Q dy = ∬ (Q_x − P_y) dA", "sirkulasi 2D"]]))]),
        "fk": ("kl-ft-laplace", "Transformasi Laplace", "ℒ", "ℒ{f}, tabel, invers, menyelesaikan PD & rangkaian.", "Strang §6.4 (pendekatan), Stewart (Laplace di latihan PD)", [
            S("Transformasi Laplace",
              "<p>ℒ{f}(s) = ∫₀^∞ e<sup>−st</sup>f(t) dt mengubah turunan menjadi perkalian: ℒ{y′} = sY − y(0), ℒ{y″} = s²Y − sy(0) − y′(0). "
              "PD linear koefisien konstan menjadi persamaan aljabar Y(s), lalu invers lewat tabel & pecahan parsial (analisis rangkaian, sistem kendali).</p>"
              + table(["f(t)", "F(s)"], [["1", "1/s"], ["tⁿ", "n!/sⁿ⁺¹"], ["e^{at}", "1/(s − a)"], ["sin bt", "b/(s² + b²)"], ["cos bt", "s/(s² + b²)"]]))]),
    },
    "fm": {
        "pb": ("kl-fm-kuadrik", "Ruang ℝ³ & Permukaan Kuadrik", "🥚", "Jarak, bola, enam kuadrik baku, irisan.", "Stewart §12.1, §12.6; Whitman §12.1", [
            S("Kuadrik",
              table(["Persamaan", "Permukaan"], [["x²/a² + y²/b² + z²/c² = 1", "elipsoida"], ["x²/a² + y²/b² − z²/c² = 1", "hiperboloida satu lembar"],
                                                ["−x²/a² − y²/b² + z²/c² = 1", "hiperboloida dua lembar"], ["z = x²/a² + y²/b²", "paraboloida eliptik"],
                                                ["z = y²/b² − x²/a²", "paraboloida hiperbolik"], ["z² = x²/a² + y²/b²", "kerucut"]]),
              [surface("Hiperboloida satu lembar (bagian atas & bawah)", "sqrt(x*x+y*y+0.0001)", "Irisan z = k berupa lingkaran yang membesar.", rng_=2)])]),
        "tp": ("kl-fm-hessian", "Hessian & Klasifikasi Titik Kritis", "🧮", "Uji turunan kedua, determinan Hessian, Lagrange & bukti.", "Stewart §14.7; Whitman §14.7", [
            S("Uji turunan kedua",
              "<p>Di titik kritis, D = f<sub>xx</sub>f<sub>yy</sub> − f<sub>xy</sub>². D &gt; 0 & f<sub>xx</sub> &gt; 0: minimum; D &gt; 0 & f<sub>xx</sub> &lt; 0: maksimum; "
              "D &lt; 0: pelana; D = 0: uji gagal. D adalah determinan matriks Hessian — bentuk kuadrat definit/tak tentu.</p>",
              [surface("Titik pelana z = x² − y²", "x*x-y*y", "Naik pada satu arah, turun pada arah lain.")])]),
        "il": ("kl-fm-jacobian", "Integral Lipat Tiga & Jacobian", "🧊", "∭, batas dari bidang, penggantian variabel, determinan Jacobian.", "Stewart §15.6, §15.9; Whitman §15.6", [
            S("Penggantian variabel",
              "<p>∬<sub>R</sub> f(x, y) dA = ∬<sub>S</sub> f(x(u, v), y(u, v))|∂(x, y)/∂(u, v)| du dv. Jacobian kutub = r, bola = ρ² sin φ. "
              "Transformasi linear u = x + y, v = x − y mengubah jajaran genjang menjadi persegi panjang dengan |J| = 1/2.</p>")]),
        "kv": ("kl-fm-potensial", "Medan Konservatif & Fungsi Potensial", "🗺️", "Uji P_y = Q_x, mencari potensial, peran topologi.", "Stewart §16.3; Whitman §16.3", [
            S("Medan konservatif",
              "<p>Pada daerah terbuka terhubung sederhana, empat pernyataan setara: F = ∇f; ∫ F·dr bebas lintasan; ∮ F·dr = 0; P<sub>y</sub> = Q<sub>x</sub>. "
              "Tanpa syarat terhubung sederhana, F = ⟨−y, x⟩/(x² + y²) memenuhi P<sub>y</sub> = Q<sub>x</sub> tetapi ∮ = 2π.</p>")]),
        "fk": ("kl-fm-seragam", "Kontinuitas & Konvergensi Seragam", "📐", "Teorema nilai ekstrem/antara, kontinu seragam, barisan fungsi.", "Stewart Lamp. F; Whitman §11.11", [
            S("Analisis real lanjutan",
              bullets(["Teorema Nilai Ekstrem & Nilai Antara (butuh interval tertutup terbatas & kontinuitas).",
                       "Kontinu seragam: δ tidak bergantung titik; kontinu di [a, b] ⇒ kontinu seragam (Heine–Cantor).",
                       "fₙ → f seragam ⇔ sup|fₙ − f| → 0; limit seragam fungsi kontinu itu kontinu (xⁿ di [0, 1] tidak seragam)."]),
              [g("fₙ(x) = xⁿ: konvergen titik demi titik, tidak seragam", [0, 1.05], [0, 1.1], [param("N", "n", 1, 80, 1, 6, "n")],
                 [fn("pow(x,N)", "blue", "xⁿ", **{"from": 0, "to": 1})], [readout("sup|fₙ − f| pada [0,1)", "1", 2)], "Supremum selisih tetap 1 untuk semua n.")])]),
    },
    "fk": {
        "pb": ("kl-fk-norma", "Norma, Jarak & Fungsi Kerugian", "📊", "Norma L1/L2/L∞, jarak, kemiripan kosinus, MSE.", "Stewart §12.2–12.3; materi khusus Fasilkom", [
            S("Geometri data",
              "<p>Data = vektor di ℝⁿ. Norma L2 √Σxᵢ², L1 Σ|xᵢ|, L∞ max|xᵢ|; jarak = norma selisih (k-NN, clustering). Kemiripan kosinus u·v/(‖u‖‖v‖) "
              "(temu kembali informasi). Fungsi kerugian MSE = (1/m)Σ(ŷ − y)² adalah fungsi banyak variabel dari parameter model.</p>",
              [g("Bola satuan norma Lp", [-1.5, 1.5], [-1.5, 1.5], [param("p", "p", 1, 8, 0.1, 2, "p")],
                 [{"type": "param", "t": [0, "2*pi"], "x": "sign(cos(t))*pow(abs(cos(t)),2/p)", "y": "sign(sin(t))*pow(abs(sin(t)),2/p)", "color": "blue"}], None,
                 "p = 1: belah ketupat (L1), p = 2: lingkaran (L2), p besar: mendekati persegi (L∞).")])]),
        "tp": ("kl-fk-gd", "Gradient Descent & Backpropagation", "🤖", "GD 1D/2D, laju belajar, sigmoid, softmax, backprop.", "Strang §13.4; materi khusus Fasilkom", [
            S("Belajar = mengikuti −∇L",
              "<p>Gradient descent: w ← w − η∇L(w). Laju belajar η terlalu besar ⇒ divergen (untuk f = ax²/2 perlu η &lt; 2/a). Backpropagation menerapkan aturan rantai "
              "lapis demi lapis; σ′ = σ(1 − σ); softmax pᵢ = e^{zᵢ}/Σe^{zⱼ} dengan kerugian −ln p.</p>",
              [g("GD pada f(x, y) = x² + c·y² (lintasan zig-zag)", [-5, 5], [-3, 3], [param("c", "c", 1, 10, 0.5, 4, "c"), param("eta", "η", 0.01, 0.25, 0.01, 0.2, "η")],
                 [{"type": "param", "t": [0, "2*pi"], "x": "4*cos(t)", "y": "4/sqrt(c)*sin(t)", "color": "gray"},
                  {"type": "iter", "id": "G", "init": {"x": 4, "y": 1}, "update": {"x": "x-eta*2*x", "y": "y-eta*2*c*y"}, "steps": 15, "px": "x", "py": "y", "color": "red"}],
                 None, "c besar (kontur pipih) + η besar ⇒ zig-zag pada arah y.")])]),
        "il": ("kl-fk-peluang", "Peluang Gabungan & Monte Carlo", "🎲", "Kepadatan gabungan, ekspektasi, eksponensial, Monte Carlo.", "Stewart §15.4 (Probability); materi Fasilkom", [
            S("Peluang kontinu",
              "<p>P((X, Y) ∈ D) = ∬<sub>D</sub> f(x, y) dA; E[X] = ∫ x f(x) dx. Distribusi eksponensial λe<sup>−λx</sup> memodelkan waktu antar-kedatangan (antrian server). "
              "Monte Carlo menaksir integral dengan rata-rata sampel acak; galat ∝ 1/√N, tak bergantung dimensi.</p>")]),
        "kv": ("kl-fk-simulasi", "Medan Vektor dalam Simulasi & Grafika", "🎮", "Partikel & integrasi Euler, normal permukaan, kerja, pusaran.", "Stewart §16.1, §14.6; Strang §15.1", [
            S("Medan vektor di komputer",
              bullets(["Partikel: r′ = F(r), langkah Euler r ← r + hF(r) (game & simulasi fisika).", "Normal permukaan z = f(x, y): ⟨−f<sub>x</sub>, −f<sub>y</sub>, 1⟩ untuk pencahayaan.",
                       "Curl mendeteksi pusaran (simulasi fluida); kerja medan konservatif hanya bergantung titik ujung."]))]),
        "fk": ("kl-fk-asimtotik", "Analisis Asimtotik, Stirling & Newton", "⏱️", "Notasi Θ, hierarki pertumbuhan, Stirling, metode Newton.", "Materi khusus Fasilkom; Strang §3.8", [
            S("Kalkulus untuk analisis algoritma",
              "<p>f = Θ(g) ⇔ 0 &lt; lim f/g &lt; ∞. Hierarki: log n ≪ √n ≪ n ≪ n log n ≪ n² ≪ 2ⁿ ≪ n!. Stirling n! ≈ √(2πn)(n/e)ⁿ memberi batas bawah pengurutan Θ(n log n). "
              "Metode Newton xₙ₊₁ = xₙ − f/f′ konvergen kuadratik.</p>",
              [g("Pertumbuhan fungsi", [1, 12], [0, 200], [], [fn("log(x)/log(2)*10", "gray", "10 log n"), fn("x*x", "blue", "n²"), fn("pow(2,x)", "red", "2ⁿ")], None,
                 "Eksponensial akhirnya mengalahkan polinom berapa pun.")])]),
    },
}

SUB = [("pb", "peubah-banyak", "Kalkulus Peubah Banyak", "🗻", ("pb-fungsi", "pb-limit")),
       ("tp", "turunan-parsial", "Turunan Parsial", "∂", ("tp-parsial", "tp-gradien")),
       ("il", "integral-lipat", "Integral Lipat", "▦", ("il-ganda", "il-koordinat")),
       ("kv", "kalkulus-vektor", "Kalkulus Vektor", "🌪️", ("kv-medan", "kv-garis")),
       ("fk", "fungsi-khusus", "Fungsi Khusus", "Γ", ("fk-gamma", "fk-analisis"))]


def _core_topic(fac, key):
    title, icon, summary, refs, sections = CORE[key]
    return T(f"kl-{fac}-{key}", title, icon, summary, refs, sections)


SUBLEVELS = []
for fac, (fac_slug, fac_name) in FACULTIES.items():
    for i, (code, slug, title, icon, cores) in enumerate(SUB, start=1):
        a_slug, a_title, a_icon, a_sum, a_refs, a_secs = APPLIED[fac][code]
        sub_title = "Fungsi Khusus & Analisis Real" if (code == "fk" and fac == "fm") else title
        SUBLEVELS.append({
            "slug": f"kl-{fac}-{slug}", "faculty": fac_slug, "order": i, "title": sub_title,
            "subtitle": f"Jalur {fac_name}", "icon": icon, "badge_label": f"Kalkulus Lanjut · {fac_name}",
            "summary_html": f"<p>Sub-level khusus jalur {fac_name}: dua topik inti dan satu topik terapan {fac_name}.</p>",
            "topics": [_core_topic(fac, cores[0]), _core_topic(fac, cores[1]), T(a_slug, a_title, a_icon, a_sum, a_refs, a_secs)],
        })

# ── Penggabungan konten lama ────────────────────────────────────────────────
ABSORB_NODES = {
    "ft-konsep": "kl-ft-peubah-banyak", "ft-terapan": "kl-ft-peubah-banyak", "ft-ujian": "kl-ft-peubah-banyak",
    "fmipa-konsep": "kl-fm-peubah-banyak", "fmipa-terapan": "kl-fm-peubah-banyak", "fmipa-ujian": "kl-fm-peubah-banyak",
    "fasilkom-konsep": "kl-fk-peubah-banyak", "fasilkom-terapan": "kl-fk-peubah-banyak", "fasilkom-ujian": "kl-fk-peubah-banyak",
    "umum-dua-variabel": "kl-ft-turunan-parsial",
}
_ALL_TP = ["kl-ft-tp-parsial", "kl-fm-tp-parsial", "kl-fk-tp-parsial"]
ABSORB_SECTIONS = {
    ("ft-konsep", "Peta topik FT"): "kl-ft-galat", ("ft-konsep", "Rumus kunci FT"): "kl-ft-galat", ("ft-ujian", "Strategi FT"): "kl-ft-galat",
    ("ft-terapan", "Contoh 1 (RMS)"): "kl-ft-massa", ("ft-terapan", "Contoh 3 (nilai rata-rata)"): "kl-ft-massa",
    ("ft-ujian", "Volume benda putar dengan metode cincin"): "kl-ft-massa",
    ("ft-terapan", "Contoh 2 (PD terpisahkan)"): "kl-ft-laplace", ("ft-terapan", "Model pendinginan (PD terpisahkan)"): "kl-ft-laplace",
    ("fmipa-konsep", "Peta topik FMIPA"): "kl-fm-kuadrik", ("fmipa-konsep", "Pernyataan dan rumus kunci FMIPA"): "kl-fm-kuadrik",
    ("fmipa-ujian", "Strategi FMIPA"): "kl-fm-kuadrik", ("fmipa-terapan", "Contoh 3 (koordinat polar)"): "kl-fm-jacobian",
    ("fmipa-terapan", "Contoh 1 (Teorema Nilai Rata-rata)"): "kl-fm-seragam", ("fmipa-terapan", "Contoh 2 (integral tak wajar)"): "kl-fm-seragam",
    ("fmipa-ujian", "Ilustrasi definisi ε–δ"): "kl-fm-seragam", ("fmipa-ujian", "Hampiran Maclaurin"): "kl-fm-seragam",
    ("fasilkom-konsep", "Peta topik Fasilkom"): "kl-fk-norma", ("fasilkom-konsep", "Rumus kunci Fasilkom"): "kl-fk-norma",
    ("fasilkom-ujian", "Strategi Fasilkom"): "kl-fk-norma",
    ("fasilkom-terapan", "Contoh 2 (backpropagation satu neuron)"): "kl-fk-gd", ("fasilkom-terapan", "Sigmoid dan turunannya"): "kl-fk-gd",
    ("fasilkom-ujian", "Gradient descent pada garis kontur"): "kl-fk-gd", ("fasilkom-terapan", "Contoh 3 (distribusi eksponensial)"): "kl-fk-peluang",
    ("fasilkom-terapan", "Contoh 1 (Newton–Raphson)"): "kl-fk-asimtotik", ("fasilkom-ujian", "Perbandingan laju pertumbuhan fungsi"): "kl-fk-asimtotik",
    ("umum-dua-variabel", "Turunan parsial, gradien, dan integral lipat"): _ALL_TP,
    ("umum-dua-variabel", "Kesalahan yang sering terjadi"): _ALL_TP,
}
# Soal lama → (topik, sesi). Soal milik fakultas hanya diundi untuk user fakultas itu (sessions._pool).
FIXED_QUESTIONS = {
    "FT-M1": ("kd-tur-dasar", 1), "FT-M2": ("kd-int-antiturunan", 1), "FT-M3": ("kd-lim-aljabar", 1), "FT-S1": ("kd-apl-laju", 2),
    "FT-S2": ("kd-apl-optimasi", 3), "FT-S3": ("km-apl-fisika", 2), "FT-H1": ("km-apl-volume", 3), "FT-H2": ("km-pd-model", 3), "FT-H3": ("km-apl-panjang", 3),
    "FM-M1": ("kd-lim-trig", 1), "FM-M2": ("kd-tur-perkalian", 1), "FM-M3": ("kd-int-tdk", 1), "FM-S1": ("kd-apl-optimasi", 3),
    "FM-S2": ("km-tek-parsial", 2), "FM-S3": ("km-der-pangkat", 3), "FM-H1": ("kd-lim-kontinu", 4), "FM-H2": ("km-der-pangkat", 4), "FM-H3": ("kl-fm-il-ganda", 3),
    "FK-M1": ("kl-fk-gd", 1), "FK-M2": ("kd-lim-takhingga", 1), "FK-M3": ("kd-int-riemann", 2), "FK-S1": ("kd-tur-transenden", 3),
    "FK-S2": ("kl-fk-gd", 2), "FK-S3": ("kd-int-riemann", 3), "FK-H1": ("kl-fk-gd", 3), "FK-H2": ("kl-fk-gd", 4), "FK-H3": ("kd-int-riemann", 4),
    "U-S6": ("kl-ft-tp-parsial", 1),
}
