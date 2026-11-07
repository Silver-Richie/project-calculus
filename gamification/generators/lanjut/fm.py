"""
Topik TERAPAN khusus FMIPA (Level Utama 4): ruang ℝ³ & kuadrik, Hessian, Jacobian, medan konservatif, analisis real.
Rujukan: Stewart §12.1, §12.6, §14.7, §15.9, §16.3; Whitman Bab 12–16; analisis: Stewart Lampiran F & Whitman §11.
"""

from fractions import Fraction as Fr
import math

from .. import register
from ..fmt import MINUS, n, paren, sup, terms
from ..graphs import fn, g2d, param, readout
from ..precalc.common import distinct, nz

KD, HS, JC, PT, SR = "kl-fm-kuadrik", "kl-fm-hessian", "kl-fm-jacobian", "kl-fm-potensial", "kl-fm-seragam"


# ════════════════════════ Ruang ℝ³ & permukaan kuadrik ════════════════════
@register("fmk.jarak", KD, (1, 2))
def fmk_jarak(rng, tier):
    d = rng.choice([(2, 3, 6, 7), (1, 4, 8, 9), (2, 6, 9, 11), (4, 4, 7, 9), (1, 2, 2, 3)])
    A = [rng.randint(-3, 3) for _ in range(3)]
    sgn = [rng.choice([1, -1]) for _ in range(3)]
    B = [A[i] + sgn[i] * d[i] for i in range(3)]
    return {"prompt": f"Hitung jarak titik A({', '.join(n(v) for v in A)}) dan B({', '.join(n(v) for v in B)}) di ℝ³.", "correct": n(d[3]),
            "distractors": [n(d[0] + d[1] + d[2]), n(d[3] ** 2), n(d[3] + 1), f"√{d[0] ** 2 + d[1] ** 2}"],
            "steps": ["|AB| = √(Δx² + Δy² + Δz²).", f"√({d[0] ** 2} + {d[1] ** 2} + {d[2] ** 2}) = √{d[3] ** 2} = <b>{d[3]}</b>."], "explanation": "Rumus jarak di ℝ³ (Pythagoras dua kali)."}


@register("fmk.bola", KD, (1, 2, 3))
def fmk_bola(rng, tier):
    h, k, l = rng.randint(-4, 4), rng.randint(-4, 4), rng.randint(-4, 4)
    r = rng.randint(1, 6)
    D, E, F = -2 * h, -2 * k, -2 * l
    G = h * h + k * k + l * l - r * r
    eq = f"x² + y² + z² {'+' if D >= 0 else MINUS} {abs(D)}x {'+' if E >= 0 else MINUS} {abs(E)}y {'+' if F >= 0 else MINUS} {abs(F)}z {'+' if G >= 0 else MINUS} {abs(G)} = 0"
    correct = f"pusat ({n(h)}, {n(k)}, {n(l)}), jari-jari {r}"
    return {"prompt": f"Tentukan pusat dan jari-jari bola {eq}.", "correct": correct,
            "distractors": [f"pusat ({n(-h)}, {n(-k)}, {n(-l)}), jari-jari {r}", f"pusat ({n(h)}, {n(k)}, {n(l)}), jari-jari {r * r}", f"pusat ({n(D)}, {n(E)}, {n(F)}), jari-jari {r}",
                            f"pusat ({n(h)}, {n(k)}, {n(l)}), jari-jari {r + 1}"],
            "steps": ["Lengkapkan kuadrat setiap variabel: (x − h)² + (y − k)² + (z − l)² = r².", f"h = {n(h)}, k = {n(k)}, l = {n(l)}, r² = {r * r}.", f"<b>{correct}</b>."],
            "explanation": "Bola = himpunan titik berjarak r dari pusat."}


@register("fmk.kuadrik", KD, (2, 3, 4, 5))
def fmk_kuadrik(rng, tier):
    cases = [("x²/4 + y²/9 + z² = 1", "elipsoida"), ("x² + y² − z² = 1", "hiperboloida satu lembar"), ("−x² − y² + z² = 1", "hiperboloida dua lembar"),
             ("z = x² + 2y²", "paraboloida eliptik"), ("z = y² − x²", "paraboloida hiperbolik"), ("z² = x² + y²", "kerucut eliptik")]
    eq, kind = rng.choice(cases[:4] if tier == 2 else cases)
    return {"prompt": f"Permukaan kuadrik {eq} adalah …", "correct": kind, "distractors": [c[1] for c in cases if c[1] != kind],
            "steps": ["Lihat tanda koefisien kuadrat dan irisan dengan bidang koordinat.", f"<b>{kind}</b>."], "explanation": "Enam kuadrik baku (Stewart §12.6, Tabel 1)."}


@register("fmk.irisan", KD, (4, 5))
def fmk_irisan(rng, tier):
    a, b, c = rng.choice([(3, 4, 5), (6, 8, 10), (5, 12, 13), (4, 3, 5)])
    return {"prompt": f"Irisan hiperboloida x² + y² − z² = {a * a} dengan bidang z = {b} berbentuk …", "correct": f"lingkaran berjari-jari {c}",
            "distractors": [f"lingkaran berjari-jari {a}", f"lingkaran berjari-jari {a + b}", "hiperbola", "elips tidak bulat"],
            "steps": [f"Substitusi z = {b}: x² + y² = {a * a} + {b * b} = {c * c}.", f"<b>lingkaran berjari-jari {c}</b> — makin jauh dari z = 0 makin besar."],
            "explanation": "Irisan mendatar hiperboloida satu lembar selalu lingkaran/elips."}


# ════════════════════════ Hessian & klasifikasi titik kritis ═══════════════
@register("fmh.kritis", HS, (1, 2, 3))
def fmh_kritis(rng, tier):
    x0, y0 = rng.randint(-3, 3), rng.randint(-3, 3)
    a, c = rng.randint(1, 3), rng.randint(1, 3)
    D_, E_ = -2 * a * x0, -2 * c * y0
    correct = f"({n(x0)}, {n(y0)})"
    return {"prompt": f"Tentukan titik kritis f(x, y) = {a if a > 1 else ''}x² + {c if c > 1 else ''}y² {'+' if D_ >= 0 else MINUS} {abs(D_)}x {'+' if E_ >= 0 else MINUS} {abs(E_)}y.",
            "correct": correct, "distractors": [f"({n(-x0)}, {n(-y0)})", f"({n(y0)}, {n(x0)})", f"({n(D_)}, {n(E_)})", "(0, 0)" if (x0, y0) != (0, 0) else "(1, 1)"],
            "steps": [f"f<sub>x</sub> = {2 * a}x + {paren(D_)} = 0 ⇒ x = {n(x0)}.", f"f<sub>y</sub> = {2 * c}y + {paren(E_)} = 0 ⇒ y = {n(y0)}.", f"<b>{correct}</b>."],
            "explanation": "Titik kritis: ∇f = 0."}


@register("fmh.uji_d", HS, (2, 3, 4, 5))
def fmh_uji(rng, tier):
    k = rng.randint(1, 3)
    if tier <= 3:
        # f = x³ − 3k²x + y² ⇒ kritis (±k, 0); D = 6x·2
        correct = f"min lokal di ({k}, 0), pelana di ({MINUS}{k}, 0)"
        return {"prompt": f"Klasifikasikan titik kritis f(x, y) = x³ − {3 * k * k}x + y².", "correct": correct,
                "distractors": [f"min lokal di ({MINUS}{k}, 0), pelana di ({k}, 0)", f"maks lokal di ({k}, 0), min lokal di ({MINUS}{k}, 0)", "dua minimum lokal", "dua titik pelana"],
                "steps": [f"∇f = ⟨3x² − {3 * k * k}, 2y⟩ = 0 ⇒ (±{k}, 0).", "D = f<sub>xx</sub>f<sub>yy</sub> − f<sub>xy</sub>² = 6x·2.",
                          f"Di ({k}, 0): D &gt; 0, f<sub>xx</sub> &gt; 0 ⇒ min; di (−{k}, 0): D &lt; 0 ⇒ pelana.", f"<b>{correct}</b>."],
                "explanation": "Uji turunan kedua dengan determinan Hessian D."}
    correct = "pelana di (0, 0), min lokal di (1, 1)"
    return {"prompt": "Klasifikasikan titik kritis f(x, y) = x³ + y³ − 3xy.", "correct": correct,
            "distractors": ["min lokal di (0, 0), pelana di (1, 1)", "maks lokal di (1, 1)", "dua titik pelana", "min lokal di (0, 0) dan (1, 1)"],
            "steps": ["f<sub>x</sub> = 3x² − 3y = 0, f<sub>y</sub> = 3y² − 3x = 0 ⇒ (0, 0), (1, 1).", "D = 36xy − 9.", "D(0, 0) = −9 &lt; 0 pelana; D(1, 1) = 27 &gt; 0, f<sub>xx</sub> = 6 &gt; 0 min.",
                      f"<b>{correct}</b>."], "explanation": "Hessian H = [[f_xx, f_xy], [f_xy, f_yy]], D = det H."}


@register("fmh.hessian", HS, (1, 2, 3))
def fmh_hessian(rng, tier):
    a, b, c = nz(rng, -4, 4), rng.randint(-4, 4), nz(rng, -4, 4)
    D = 4 * a * c - b * b
    kind = "minimum" if D > 0 and a > 0 else "maksimum" if D > 0 else "pelana" if D < 0 else "uji gagal (D = 0)"
    return {"prompt": f"f(x, y) = {n(a)}x² + {n(b)}xy + {n(c)}y² punya titik kritis (0, 0). Jenisnya?".replace("+ −", "− "), "correct": kind,
            "distractors": [k for k in ["minimum", "maksimum", "pelana", "uji gagal (D = 0)"] if k != kind] + ["bukan titik kritis"],
            "steps": [f"H = [[{2 * a}, {b}], [{b}, {2 * c}]], D = {2 * a}·{2 * c} − {b * b} = {D}.",
                      "D &gt; 0 & f<sub>xx</sub> &gt; 0: min; D &gt; 0 & f<sub>xx</sub> &lt; 0: maks; D &lt; 0: pelana.", f"<b>{kind}</b>."],
            "explanation": "Bentuk kuadrat definit positif/negatif/tak tentu."}


@register("fmh.jarak_garis", HS, (4, 5))
def fmh_jarak(rng, tier):
    a, b, h = rng.choice([(3, 4, 5), (5, 12, 13), (8, 15, 17), (6, 8, 10)])
    c = h * rng.randint(1, 4)
    val = Fr(c * c, h * h)
    return {"prompt": f"Dengan pengali Lagrange, tentukan minimum x² + y² pada garis {a}x + {b}y = {c}.", "correct": n(val),
            "distractors": [n(Fr(c, h)), n(Fr(c * c, a + b)), n(val * 2), n(c)],
            "steps": [f"∇(x² + y²) = λ⟨{a}, {b}⟩ ⇒ (x, y) = (λ/2)⟨{a}, {b}⟩.", f"Substitusi ke garis: λ/2 = {c}/{h * h}.", f"Minimum = {c}²/{h * h} = <b>{n(val)}</b> (kuadrat jarak garis ke asal)."],
            "explanation": "Lagrange memberi bukti rumus jarak titik ke garis."}


# ════════════════════════ Integral lipat tiga & Jacobian ══════════════════
@register("fmj.lipat3", JC, (1, 2, 3))
def fmj_lipat3(rng, tier):
    a, b, c = rng.randint(1, 3), rng.randint(1, 3), rng.randint(1, 3)
    if tier == 1:
        k = rng.randint(1, 5)
        val = k * a * b * c
        f = str(k)
    else:
        val = Fr(a * a * b * b * c * c, 8)
        f = "xyz"
    return {"prompt": f"Hitung ∭<sub>B</sub> {f} dV dengan B = [0, {a}] × [0, {b}] × [0, {c}].", "correct": n(val),
            "distractors": [n(val * 2), n(a * b * c), n(Fr(a * b * c, 8)), n(val + 1)],
            "steps": ["Fubini: integral berulang tiga kali (urutan bebas pada balok).", f"<b>{n(val)}</b>."], "explanation": "Integral lipat tiga pada balok."}


@register("fmj.tetra", JC, (1, 2))
def fmj_tetra(rng, tier):
    a, b, c = rng.randint(1, 4), rng.randint(1, 4), rng.randint(1, 6)
    return {"prompt": f"Hitung volume tetrahedron dengan titik sudut (0,0,0), ({a},0,0), (0,{b},0), (0,0,{c}) menggunakan integral lipat tiga.", "correct": n(Fr(a * b * c, 6)),
            "distractors": [n(Fr(a * b * c, 3)), n(Fr(a * b * c, 2)), n(a * b * c), n(Fr(a + b + c, 6))],
            "steps": [f"V = ∫₀^{a}∫₀^{{{b}(1 − x/{a})}}∫₀^{{{c}(1 − x/{a} − y/{b})}} dz dy dx.", f"= {a}·{b}·{c}/6 = <b>{n(Fr(a * b * c, 6))}</b>."], "explanation": "Batas integral lipat tiga dari bidang miring."}


@register("fmj.jacobian", JC, (2, 3, 4, 5))
def fmj_jac(rng, tier):
    cases = [("x = r cos θ, y = r sin θ", "r"), ("x = ρ sin φ cos θ, y = ρ sin φ sin θ, z = ρ cos φ", "ρ² sin φ"),
             ("x = u + v, y = u − v", "2 (nilai mutlak)"), ("x = 2u, y = 3v", "6")]
    t, J = rng.choice(cases)
    return {"prompt": f"Nilai mutlak determinan Jacobian |∂(x, y{', z' if 'z' in t else ''})/∂(…)| untuk transformasi {t} adalah …", "correct": J,
            "distractors": [c[1] for c in cases if c[1] != J] + ["1"],
            "steps": ["J = determinan matriks turunan parsial (x, y, …) terhadap variabel baru.", f"<b>{J}</b>. Elemen luas/volume berubah menjadi |J| du dv (…)."],
            "explanation": "Jacobian = faktor skala luas/volume pada penggantian variabel."}


@register("fmj.substitusi", JC, (3, 4, 5))
def fmj_sub(rng, tier):
    a, b = rng.randint(1, 4), rng.randint(1, 4)
    val = Fr(a * a * b, 4)
    return {"prompt": f"Hitung ∬<sub>R</sub> (x + y) dA, R jajaran genjang 0 ≤ x + y ≤ {a}, 0 ≤ x − y ≤ {b}, dengan u = x + y, v = x − y.", "correct": n(val),
            "distractors": [n(Fr(a * a * b, 2)), n(val * 2), n(Fr(a * b, 2)), n(Fr(a * a * b, 8))],
            "steps": ["x = (u + v)/2, y = (u − v)/2 ⇒ |∂(x, y)/∂(u, v)| = 1/2.", f"∫₀^{b}∫₀^{a} u·(1/2) du dv = (1/2)·{a * a}/2·{b}.", f"= <b>{n(val)}</b>."],
            "explanation": "Penggantian variabel mengubah jajaran genjang menjadi persegi panjang."}


# ════════════════════════ Medan konservatif & potensial ═══════════════════
@register("fmp.uji", PT, (1, 2, 3))
def fmp_uji(rng, tier):
    cases = [("⟨2xy, x²⟩", "konservatif", "P_y = 2x = Q_x"), ("⟨y, −x⟩", "tidak konservatif", "P_y = 1 ≠ −1 = Q_x"),
             ("⟨eʸ, xeʸ⟩", "konservatif", "P_y = eʸ = Q_x"), ("⟨x², xy⟩", "tidak konservatif", "P_y = 0 ≠ y = Q_x"),
             ("⟨y cos x, sin x⟩", "konservatif", "P_y = cos x = Q_x")]
    F, ans, why = rng.choice(cases)
    return {"prompt": f"Apakah F = {F} konservatif pada ℝ²?", "correct": ans, "distractors": ["tidak konservatif" if ans == "konservatif" else "konservatif", "bergantung lintasan", "tidak dapat ditentukan"],
            "steps": ["Pada daerah terhubung sederhana: konservatif ⇔ ∂P/∂y = ∂Q/∂x.", why.replace("P_y", "P<sub>y</sub>").replace("Q_x", "Q<sub>x</sub>") + ".", f"<b>{ans}</b>."],
            "explanation": "Uji silang turunan parsial."}


@register("fmp.lintasan", PT, (1, 2))
def fmp_lintasan(rng, tier):
    A, B = (rng.randint(0, 3), rng.randint(0, 3)), (rng.randint(0, 3), rng.randint(0, 3))
    f = lambda p: p[0] ** 2 * p[1]
    val = f(B) - f(A)
    return {"prompt": f"F = ⟨2xy, x²⟩ = ∇(x²y). Hitung ∫<sub>C</sub> F·dr dari ({A[0]}, {A[1]}) ke ({B[0]}, {B[1]}) sepanjang lintasan apa pun.", "correct": n(val),
            "distractors": [n(-val), n(f(B)), "bergantung lintasan", n(val + 1)],
            "steps": ["Medan konservatif ⇒ ∫ F·dr = f(B) − f(A).", f"= {f(B)} − {f(A)} = <b>{n(val)}</b>."], "explanation": "Kebebasan lintasan."}


@register("fmp.potensial", PT, (2, 3, 4, 5))
def fmp_pot(rng, tier):
    a, b, c = nz(rng, -3, 3), nz(rng, -3, 3), nz(rng, -3, 3)
    pot = lambda p, q, r: "f = " + terms([(p, "x³"), (q, "xy"), (r, "y²")]) + " + K"
    correct = pot(a, c, b)
    return {"prompt": f"Tentukan fungsi potensial F = ⟨{terms([(3 * a, 'x²'), (c, 'y')])}, {terms([(c, 'x'), (2 * b, 'y')])}⟩.", "correct": correct,
            "distractors": [pot(3 * a, c, 2 * b), pot(a, 2 * c, b), pot(a, 0, b), "tidak ada (tidak konservatif)", pot(a, -c, b)],
            "steps": [f"f = ∫ P dx = {n(a)}x³ + {n(c)}xy + g(y).", f"f<sub>y</sub> = {n(c)}x + g′(y) = Q ⇒ g′(y) = {n(2 * b)}y ⇒ g = {n(b)}y².", f"<b>{correct}</b>."],
            "explanation": "Integralkan P terhadap x, lalu cocokkan dengan Q."}


@register("fmp.lubang", PT, (4, 5))
def fmp_lubang(rng, tier):
    R = rng.randint(1, 5)
    return {"prompt": f"F = ⟨−y, x⟩/(x² + y²) memenuhi P<sub>y</sub> = Q<sub>x</sub> di ℝ² ∖ {{(0, 0)}}. Hitung ∮ F·dr mengelilingi lingkaran berjari-jari {R}.",
            "correct": "2π", "distractors": ["0", f"{2 * R}π", f"π{R * R}", "tidak terdefinisi"],
            "steps": [f"Parametrisasi r = ⟨{R} cos t, {R} sin t⟩: F·r′ = ({R}²sin²t + {R}²cos²t)/{R}² = 1.", "∮ = ∫₀^{2π} 1 dt = <b>2π</b> ≠ 0.",
                      "Jadi F TIDAK konservatif: daerahnya berlubang (tidak terhubung sederhana), uji P_y = Q_x tidak cukup."],
            "explanation": "Syarat topologi (terhubung sederhana) penting dalam teorema."}


# ════════════════════════ Analisis real: kontinuitas & konvergensi seragam ═
@register("fms.teorema", SR, (1, 2, 3))
def fms_teorema(rng, tier):
    cases = [("f kontinu pada [a, b] pasti mencapai nilai maksimum dan minimum.", "benar (Teorema Nilai Ekstrem)"),
             ("f kontinu pada (a, b) pasti mencapai nilai maksimum.", "salah (contoh f(x) = x pada (0, 1))"),
             ("f kontinu pada [a, b] dengan f(a) &lt; 0 &lt; f(b) pasti punya akar di (a, b).", "benar (Teorema Nilai Antara)"),
             ("f terdiferensialkan pada (a, b) dan kontinu di [a, b] ⇒ ada c dengan f′(c) = (f(b) − f(a))/(b − a).", "benar (Teorema Nilai Rata-rata)")]
    s, ans = rng.choice(cases)
    return {"prompt": f"Benar atau salah: “{s}”", "correct": ans, "distractors": [c[1] for c in cases if c[1] != ans] + ["salah (hanya untuk polinom)"],
            "steps": ["Cek hipotesis teorema: interval tertutup & terbatas, kontinuitas, keterdiferensialan.", f"<b>{ans}</b>."],
            "explanation": "Teorema-teorema dasar memerlukan hipotesis yang tepat."}


@register("fms.seragam", SR, (1, 2, 3, 4))
def fms_seragam(rng, tier):
    cases = [("f(x) = x² pada [0, 1]", "kontinu seragam"), ("f(x) = x² pada ℝ", "tidak kontinu seragam"), ("f(x) = 1/x pada (0, 1]", "tidak kontinu seragam"),
             ("f(x) = √x pada [0, ∞)", "kontinu seragam"), ("f(x) = sin x pada ℝ", "kontinu seragam")]
    f, ans = rng.choice(cases)
    return {"prompt": f"Apakah {f} kontinu seragam?", "correct": ans, "distractors": ["tidak kontinu seragam" if ans == "kontinu seragam" else "kontinu seragam", "tidak kontinu", "tidak dapat ditentukan"],
            "steps": ["Kontinu seragam: δ yang sama berlaku untuk semua titik.", "Kontinu pada interval tertutup terbatas ⇒ kontinu seragam (Heine–Cantor); turunan terbatas juga cukup.",
                      "x² pada ℝ dan 1/x di dekat 0 memiliki kemiringan tak terbatas.", f"<b>{ans}</b>."],
            "explanation": "Kontinuitas seragam lebih kuat dari kontinuitas titik demi titik."}


@register("fms.barisan_fungsi", SR, (3, 4, 5))
def fms_bf(rng, tier):
    if tier == 3:
        return {"prompt": "Barisan fungsi fₙ(x) = xⁿ pada [0, 1] konvergen titik demi titik ke …", "correct": "f(x) = 0 untuk 0 ≤ x &lt; 1 dan f(1) = 1 (tidak seragam)",
                "distractors": ["f(x) = 0 untuk semua x (seragam)", "f(x) = 1 untuk semua x", "f(x) = x", "tidak konvergen"],
                "steps": ["Untuk 0 ≤ x &lt; 1: xⁿ → 0; untuk x = 1: 1ⁿ = 1.", "Limitnya tidak kontinu, padahal setiap fₙ kontinu ⇒ konvergensi tidak mungkin seragam.",
                          "<b>f(x) = 0 untuk x &lt; 1, f(1) = 1 (tidak seragam)</b>."],
                "graphs": [g2d("fₙ(x) = xⁿ", [0, 1.05], [0, 1.1], [param("N", "n", 1, 60, 1, 5, "n")], [fn("pow(x,N)", "blue", "xⁿ", **{"from": 0, "to": 1})], None,
                               "Untuk n besar grafik ‘patah’ di dekat x = 1.")],
                "explanation": "Limit seragam dari fungsi kontinu selalu kontinu."}
    k = rng.randint(1, 5)
    nn = k * k
    val = Fr(1, 2 * k)
    return {"prompt": f"fₙ(x) = x/(1 + nx²) pada ℝ. Hitung sup |fₙ(x)| untuk n = {nn}.", "correct": n(val),
            "distractors": [n(Fr(1, k)), n(Fr(1, nn)), "1", n(Fr(1, 2 * nn))],
            "steps": ["f′ = 0 ⇒ 1 − nx² = 0 ⇒ x = 1/√n.", "fₙ(1/√n) = (1/√n)/2 = 1/(2√n).", f"n = {nn}: <b>{n(val)}</b>. Karena sup → 0, fₙ → 0 secara seragam."],
            "explanation": "Konvergen seragam ⇔ sup|fₙ − f| → 0."}


@register("fms.cauchy", SR, (4, 5))
def fms_cauchy(rng, tier):
    cases = [("Σ 1/n² konvergen", "benar — jumlah parsialnya barisan Cauchy (|Sₘ − Sₙ| ≤ 1/n)"),
             ("Barisan Sₙ = 1 + 1/2 + … + 1/n adalah barisan Cauchy", "salah — S₂ₙ − Sₙ ≥ 1/2 untuk semua n"),
             ("Setiap barisan Cauchy di ℝ terbatas", "benar — ambil ε = 1"),
             ("ℚ lengkap (setiap barisan Cauchy di ℚ konvergen di ℚ)", "salah — pendekatan desimal √2")]
    s, ans = rng.choice(cases)
    return {"prompt": f"Benar atau salah: “{s}”?", "correct": ans, "distractors": [c[1] for c in cases if c[1] != ans],
            "steps": ["Barisan Cauchy: ∀ε ∃N: |aₘ − aₙ| &lt; ε untuk m, n ≥ N.", f"<b>{ans}</b>."], "explanation": "Kriteria Cauchy tidak memerlukan tahu limitnya."}
