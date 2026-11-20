"""
Topik TERAPAN khusus FMIPA (Level Utama 4): ruang ℝ³ & kuadrik, Hessian, Jacobian, medan konservatif, analisis real.
Rujukan: Stewart §12.1, §12.6, §14.7, §15.9, §16.3; Whitman Bab 12–16; analisis: Stewart Lampiran F & Whitman §11.
"""

from fractions import Fraction as Fr
import math

from .. import register
from ..fmt import MINUS, n, paren, sqrt_simplify, sup, surd, terms
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
    a, b, c = rng.randint(1, 9), rng.randint(1, 9), rng.randint(1, 9)
    v = ["x", "y", "z"]
    rng.shuffle(v)
    X, Y, Z = v                      # Z = sumbu istimewa
    sq = lambda var, k: f"{var}²" if k == 1 else f"{var}²/{k}"
    cases = [(f"{sq(X, a)} + {sq(Y, b)} + {sq(Z, c)} = 1", "elipsoida"),
             (f"{sq(X, a)} + {sq(Y, b)} − {sq(Z, c)} = 1", "hiperboloida satu lembar"),
             (f"−{sq(X, a)} − {sq(Y, b)} + {sq(Z, c)} = 1", "hiperboloida dua lembar"),
             (f"{Z} = {sq(X, a)} + {sq(Y, b)}", "paraboloida eliptik"),
             (f"{Z} = {sq(Y, b)} − {sq(X, a)}", "paraboloida hiperbolik"),
             (f"{Z}² = {sq(X, a)} + {sq(Y, b)}", "kerucut eliptik")]
    eq, kind = rng.choice(cases[:4] if tier == 2 else cases)
    why = {"elipsoida": "Ketiga kuadrat bertanda + dan = 1: semua irisan berupa elips.",
           "hiperboloida satu lembar": "Satu kuadrat bertanda −: irisan tegak lurus sumbu itu selalu elips (tidak pernah kosong).",
           "hiperboloida dua lembar": "Dua kuadrat bertanda −: irisan dekat pusat kosong ⇒ dua lembar terpisah.",
           "paraboloida eliptik": "Satu variabel berpangkat satu, dua kuadrat bertanda sama.",
           "paraboloida hiperbolik": "Satu variabel berpangkat satu, dua kuadrat berlawanan tanda (pelana).",
           "kerucut eliptik": "Persamaan homogen derajat dua (= 0 setelah dipindah ruas)."}[kind]
    return {"prompt": f"Permukaan kuadrik {eq} adalah …", "correct": kind, "distractors": [c_[1] for c_ in cases if c_[1] != kind],
            "steps": ["Lihat tanda koefisien kuadrat, variabel berpangkat satu, dan ruas kanan.", why, f"<b>{kind}</b> (sumbu istimewa: {Z})."],
            "explanation": "Enam kuadrik baku (Stewart §12.6, Tabel 1) — penyebut hanya mengubah ukuran, bukan jenis."}


@register("fmk.irisan", KD, (4, 5))
def fmk_irisan(rng, tier):
    a, k = rng.randint(1, 6), rng.randint(1, 6)
    kind = rng.choice(["hiperboloida", "paraboloida", "kerucut", "pelana"] if tier == 5 else ["hiperboloida", "paraboloida", "kerucut"])
    rt_ = lambda v: surd(*sqrt_simplify(v))
    if kind == "hiperboloida":
        eq, plane, correct = f"x² + y² − z² = {a * a}", f"z = {k}", f"lingkaran berjari-jari {rt_(a * a + k * k)}"
        wrong = [f"lingkaran berjari-jari {a}", f"lingkaran berjari-jari {a + k}", "hiperbola", "elips tidak bulat"]
        work = f"Substitusi z = {k}: x² + y² = {a * a} + {k * k} = {a * a + k * k}."
    elif kind == "paraboloida":
        eq, plane, correct = f"z = {cf(a)}(x² + y²)", f"z = {a * k * k}", f"lingkaran berjari-jari {k}"
        wrong = [f"lingkaran berjari-jari {k * k}", f"lingkaran berjari-jari {a * k}", "parabola", "titik"]
        work = f"{a}(x² + y²) = {a * k * k} ⇒ x² + y² = {k * k}."
    elif kind == "kerucut":
        eq, plane, correct = f"z² = {cf(a * a)}(x² + y²)", f"z = {a * k}", f"lingkaran berjari-jari {k}"
        wrong = [f"lingkaran berjari-jari {a * k}", f"lingkaran berjari-jari {k * k}", "hiperbola", "dua garis berpotongan"]
        work = f"{a * a * k * k} = {a * a}(x² + y²) ⇒ x² + y² = {k * k}."
    else:
        eq, plane, correct = f"z = y² − {cf(a)}x²", f"x = {k}", f"parabola z = y² − {a * k * k} (terbuka ke atas)"
        wrong = [f"parabola z = −y² + {a * k * k} (terbuka ke bawah)", "hiperbola", f"lingkaran berjari-jari {k}", "dua garis berpotongan"]
        work = f"Substitusi x = {k}: z = y² − {a * k * k}."
    return {"prompt": f"Irisan permukaan {eq} dengan bidang {plane} berbentuk …", "correct": correct, "distractors": wrong,
            "steps": [work, f"<b>{correct}</b>."], "explanation": "Irisan (jejak) dengan bidang sejajar bidang koordinat mengungkap bentuk kuadrik."}


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


def cf(c):
    return "" if c == 1 else MINUS if c == -1 else n(c)


def sh(var, h):
    """(x − h) atau x."""
    return var if h == 0 else f"({var} {MINUS} {h})" if h > 0 else f"({var} + {-h})"


def pt2(a, b):
    return f"({n(a)}, {n(b)})"


def npow(N, e):
    """N^e untuk N kuadrat sempurna dan e kelipatan 1/2 → pecahan."""
    e = Fr(e)
    r = math.isqrt(N)
    v = Fr(r) ** int(e * 2)
    return v


@register("fmh.uji_d", HS, (2, 3, 4, 5))
def fmh_uji(rng, tier):
    h, v = rng.randint(-2, 2), rng.randint(-2, 2)
    if tier <= 3:
        # f = a(x−h)³ − 3ak²(x−h) + s·b(y−v)²  ⇒ kritis (h ± k, v)
        a, k, b, s = rng.randint(1, 3), rng.randint(1, 3), rng.randint(1, 3), rng.choice([1, -1])
        swap = rng.random() < 0.4
        X, Y = ("y", "x") if swap else ("x", "y")
        f = f"{cf(a)}{sh(X, h)}³ {MINUS} {3 * a * k * k}{sh(X, h)} {'+' if s > 0 else MINUS} {cf(b)}{sh(Y, v)}²"
        P, Q = (h + k, v), (h - k, v)
        if swap:
            P, Q = (v, h + k), (v, h - k)
        if s > 0:
            correct = f"min lokal di {pt2(*P)}, pelana di {pt2(*Q)}"
            wrong = [f"min lokal di {pt2(*Q)}, pelana di {pt2(*P)}", f"maks lokal di {pt2(*P)}, min lokal di {pt2(*Q)}", "dua minimum lokal", f"pelana di {pt2(*P)}, maks lokal di {pt2(*Q)}"]
        else:
            correct = f"pelana di {pt2(*P)}, maks lokal di {pt2(*Q)}"
            wrong = [f"maks lokal di {pt2(*P)}, pelana di {pt2(*Q)}", f"min lokal di {pt2(*P)}, pelana di {pt2(*Q)}", "dua titik pelana", f"min lokal di {pt2(*P)}, maks lokal di {pt2(*Q)}"]
        at_P = f"D {'&gt;' if s > 0 else '&lt;'} 0" + (f" dan f<sub>{X}{X}</sub> &gt; 0 ⇒ min" if s > 0 else " ⇒ pelana")
        at_Q = f"D {'&lt;' if s > 0 else '&gt;'} 0" + (" ⇒ pelana" if s > 0 else f" dan f<sub>{X}{X}</sub> &lt; 0 ⇒ maks")
        steps = [f"∂f/∂{X} = {3 * a}{sh(X, h)}² − {3 * a * k * k} = 0 ⇒ {X} = {n(h)} ± {k}; ∂f/∂{Y} = {2 * s * b}{sh(Y, v)} = 0 ⇒ {Y} = {n(v)}.",
                 f"f<sub>{X}{X}</sub> = {6 * a}{sh(X, h)}, f<sub>{Y}{Y}</sub> = {n(2 * s * b)}, f<sub>xy</sub> = 0 ⇒ D = {n(12 * a * s * b)}{sh(X, h)}.",
                 f"Di {X} = {n(h + k)}: {at_P}; di {X} = {n(h - k)}: {at_Q}.",
                 f"<b>{correct}</b>."]
        return {"prompt": f"Klasifikasikan titik kritis f(x, y) = {f}.", "correct": correct, "distractors": wrong, "steps": steps,
                "explanation": "Uji turunan kedua dengan determinan Hessian D = f_xx f_yy − f_xy²."}
    # f = (x−h)³ + (y−v)³ − 3c(x−h)(y−v)  ⇒ kritis (h, v) dan (h + c, v + c)
    c = nz(rng, -3, 3)
    X, Y = sh("x", h), sh("y", v)
    f = f"{X}³ + {Y}³ {MINUS} {3 * abs(c)}{X}{Y}" if c > 0 else f"{X}³ + {Y}³ + {3 * abs(c)}{X}{Y}"
    P, Q = (h, v), (h + c, v + c)
    kind = "min lokal" if c > 0 else "maks lokal"
    correct = f"pelana di {pt2(*P)}, {kind} di {pt2(*Q)}"
    return {"prompt": f"Klasifikasikan titik kritis f(x, y) = {f}.", "correct": correct,
            "distractors": [f"{kind} di {pt2(*P)}, pelana di {pt2(*Q)}", f"pelana di {pt2(*P)}, {'maks lokal' if c > 0 else 'min lokal'} di {pt2(*Q)}", "dua titik pelana",
                            f"pelana di {pt2(*P)}, {kind} di {pt2(h - c, v - c)}"],
            "steps": [f"Misal u = {X}, w = {Y}: f<sub>u</sub> = 3u² − {3 * c}w = 0, f<sub>w</sub> = 3w² − {3 * c}u = 0 ⇒ (u, w) = (0, 0) atau ({c}, {c}).".replace("− −", "+ "),
                      f"D = 36uw − {9 * c * c}: di (0, 0) D = −{9 * c * c} &lt; 0 ⇒ pelana; di ({c}, {c}) D = {27 * c * c} &gt; 0 dan f<sub>uu</sub> = {6 * c} ⇒ {kind}.",
                      f"Kembali ke (x, y): <b>{correct}</b>."],
            "explanation": "Hessian H = [[f_xx, f_xy], [f_xy, f_yy]], D = det H; pergeseran pusat hanya menggeser titik kritis."}


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
    kind = rng.choice(["linear", "linear", "elips", "bola"] if tier >= 4 else ["linear", "elips"])
    if kind == "linear":
        while True:
            p, q, s, t = (rng.randint(-4, 4) for _ in range(4))
            D = p * t - q * s
            if D:
                break
        tr = f"x = {terms([(p, 'u'), (q, 'v')])}, y = {terms([(s, 'u'), (t, 'v')])}"
        correct = n(abs(D))
        wrong = [n(abs(p * t + q * s)) if abs(p * t + q * s) != abs(D) else n(abs(D) + 1), n(D) if D < 0 else n(-D), n(abs(p + t)) if abs(p + t) != abs(D) else n(abs(D) * 2), "1"]
        why = f"det [[{n(p)}, {n(q)}], [{n(s)}, {n(t)}]] = {n(p)}·{paren(t)} − {paren(q)}·{paren(s)} = {n(D)}."
    elif kind == "elips":
        a, b = rng.randint(1, 6), rng.randint(1, 6)
        tr = f"x = {cf(a)}r cos θ, y = {cf(b)}r sin θ"
        correct = f"{a * b if a * b > 1 else ''}r"
        wrong = ["r", f"{a + b}r", f"{a * b}", f"{a * b}r²"]
        why = f"det [[{a} cos θ, −{a}r sin θ], [{b} sin θ, {b}r cos θ]] = {a * b}r(cos²θ + sin²θ)."
    else:
        a = rng.randint(1, 4)
        tr = f"x = {cf(a)}ρ sin φ cos θ, y = {cf(a)}ρ sin φ sin θ, z = {cf(a)}ρ cos φ"
        correct = f"{a ** 3 if a > 1 else ''}ρ² sin φ"
        wrong = ["ρ² sin φ", f"{a * a}ρ² sin φ" if a > 1 else "ρ sin φ", f"{a ** 3}ρ sin φ", f"{a ** 3}ρ²"]
        why = f"Skala {a} pada ketiga koordinat mengalikan volume dengan {a}³; Jacobian bola standar ρ² sin φ."
    return {"prompt": f"Nilai mutlak determinan Jacobian untuk transformasi {tr} adalah …", "correct": correct, "distractors": wrong,
            "steps": ["J = determinan matriks turunan parsial (x, y, …) terhadap variabel baru.", why, f"<b>{correct}</b>: elemen luas/volume menjadi |J| du dv (…)."],
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
    if tier == 1 and rng.random() < 0.4:
        cases = [("f kontinu pada [a, b] pasti mencapai nilai maksimum dan minimum.", "benar (Teorema Nilai Ekstrem)"),
                 ("f kontinu pada (a, b) pasti mencapai nilai maksimum.", "salah (contoh f(x) = x pada (0, 1))"),
                 ("f kontinu pada [a, b] dengan f(a) &lt; 0 &lt; f(b) pasti punya akar di (a, b).", "benar (Teorema Nilai Antara)"),
                 ("f terdiferensialkan pada (a, b) dan kontinu di [a, b] ⇒ ada c dengan f′(c) = (f(b) − f(a))/(b − a).", "benar (Teorema Nilai Rata-rata)")]
        s, ans = rng.choice(cases)
        return {"prompt": f"Benar atau salah: “{s}”", "correct": ans, "distractors": [c[1] for c in cases if c[1] != ans] + ["salah (hanya untuk polinom)"],
                "steps": ["Cek hipotesis teorema: interval tertutup & terbatas, kontinuitas, keterdiferensialan.", f"<b>{ans}</b>."],
                "explanation": "Teorema-teorema dasar memerlukan hipotesis yang tepat."}
    if tier <= 2:
        # Teorema Nilai Antara pada polinom kubik
        p, q = rng.randint(-6, 6), rng.randint(-9, 9)
        a = rng.randint(-3, 1)
        b = a + rng.randint(1, 3)
        F = lambda x: x ** 3 + p * x + q
        fa, fb = F(a), F(b)
        poly_ = terms([(1, "x³"), (p, "x")], q)
        if fa * fb < 0:
            correct = f"ya — f({n(a)}) = {n(fa)} dan f({n(b)}) = {n(fb)} berlawanan tanda"
        elif fa == 0 or fb == 0:
            correct = f"ya — f({n(a) if fa == 0 else n(b)}) = 0 di ujung interval"
        else:
            correct = f"tidak dapat disimpulkan dari TNA — f({n(a)}) = {n(fa)} dan f({n(b)}) = {n(fb)} bertanda sama"
        return {"prompt": f"Dengan Teorema Nilai Antara, apakah f(x) = {poly_} pasti memiliki akar di [{n(a)}, {n(b)}]?", "correct": correct,
                "distractors": [f"ya — f({n(a)}) = {n(fa)} dan f({n(b)}) = {n(fb)} berlawanan tanda" if fa * fb >= 0 else f"tidak — f({n(a)}) = {n(fa)} dan f({n(b)}) = {n(fb)}",
                                "tidak — polinom kubik tidak kontinu", "ya — setiap polinom kubik punya akar di setiap interval", f"tidak dapat disimpulkan — f({n(a)}) = {n(fa + 1)}"],
                "steps": ["Polinom kontinu di mana-mana ⇒ TNA berlaku pada [a, b].", f"f({n(a)}) = {n(fa)}, f({n(b)}) = {n(fb)}.",
                          "Tanda berlawanan ⇒ ada c dengan f(c) = 0. Tanda sama ⇒ TNA tidak menjamin apa pun (bisa ada, bisa tidak).", f"<b>{correct}</b>."],
                "explanation": "TNA: f kontinu pada [a, b] dan k di antara f(a), f(b) ⇒ ada c dengan f(c) = k."}
    # tier 3: Teorema Nilai Rata-rata — cari c
    if rng.random() < 0.5:
        A, B, C = nz(rng, -3, 3), rng.randint(-4, 4), rng.randint(-5, 5)
        a = rng.randint(-3, 2)
        b = a + rng.randint(1, 4)
        c = Fr(a + b, 2)
        f = terms([(A, "x²"), (B, "x")], C)
        why = f"f′(x) = {n(2 * A)}x {'+' if B >= 0 else MINUS} {abs(B)}; (f(b) − f(a))/(b − a) = {n(A * (a + b) + B)} ⇒ x = ({n(a)} + {n(b)})/2."
    else:
        a = rng.randint(0, 2)
        b = a + rng.randint(1, 3)
        c2 = Fr(a * a + a * b + b * b, 3)
        num, den = c2.numerator, c2.denominator
        co, r = sqrt_simplify(num * den)
        c = f"{surd(co, r)}/{den}" if den > 1 else surd(co, r)
        if r == 1:
            c = Fr(co, den)
        f = "x³"
        why = f"f′(c) = 3c² = (b³ − a³)/(b − a) = a² + ab + b² = {a * a + a * b + b * b} ⇒ c² = {n(c2)}, ambil c di ({n(a)}, {n(b)})."
    correct = n(c) if isinstance(c, Fr) else c
    return {"prompt": f"Tentukan c pada Teorema Nilai Rata-rata untuk f(x) = {f} pada [{n(a)}, {n(b)}].", "correct": correct,
            "distractors": [n(Fr(a + b, 3)), n(Fr(b - a, 2)), n(b), n(Fr(a + 2 * b, 3))],
            "steps": ["TNR: ada c ∈ (a, b) dengan f′(c) = (f(b) − f(a))/(b − a).", why, f"<b>c = {correct}</b>."],
            "explanation": "Untuk parabola, c selalu titik tengah interval."}


@register("fms.seragam", SR, (1, 2, 3, 4))
def fms_seragam(rng, tier):
    k, M, d = rng.randint(2, 5), rng.randint(1, 9), rng.choice(["1/2", "1", "2", "1/10"])
    if tier >= 3 and rng.random() < 0.6:
        # δ terbesar untuk ε tertentu
        if rng.random() < 0.5:
            a, b = nz(rng, -9, 9), rng.randint(-5, 5)
            eps = Fr(rng.choice([1, 3, 6, 9]), 100)
            dl = eps / abs(a)
            f, why = terms([(a, "x")], b), f"|f(x) − f(y)| = {abs(a)}|x − y| &lt; ε ⇔ |x − y| &lt; ε/{abs(a)}."
        else:
            eps = Fr(rng.choice([1, 2, 5]), 100)
            dl = eps / (2 * M)
            f, why = f"x² pada [0, {M}]", f"|x² − y²| = |x + y||x − y| ≤ {2 * M}|x − y| ⇒ cukup |x − y| &lt; ε/{2 * M}."
        return {"prompt": f"f(x) = {f}. Untuk ε = {n(eps)}, berapa δ (terbesar dari estimasi Lipschitz) agar |x − y| &lt; δ ⇒ |f(x) − f(y)| &lt; ε untuk SEMUA x, y?",
                "correct": n(dl), "distractors": [n(eps), n(dl * 2), n(dl / 2), n(eps * 2)],
                "steps": ["Kontinu seragam: satu δ berlaku di semua titik.", why, f"δ = <b>{n(dl)}</b>."],
                "explanation": "Fungsi Lipschitz (|f(x) − f(y)| ≤ L|x − y|) kontinu seragam dengan δ = ε/L."}
    cases = [(f"f(x) = x{sup(k)} pada [0, {M}]", "kontinu seragam", f"Interval tertutup terbatas (Heine–Cantor); juga |f′| ≤ {k}·{M}{sup(k - 1)}."),
             (f"f(x) = x{sup(k)} pada ℝ", "tidak kontinu seragam", f"Kemiringan {k}x{sup(k - 1) if k > 2 else ''} tak terbatas: δ harus makin kecil untuk x besar."),
             (f"f(x) = 1/x{sup(k - 1) if k > 2 else ''} pada (0, 1]", "tidak kontinu seragam", "Di dekat 0 fungsi meledak; barisan xₙ = 1/n dan 1/(n + 1) makin dekat tetapi nilai fungsinya tidak."),
             (f"f(x) = 1/x{sup(k - 1) if k > 2 else ''} pada [{d}, ∞)", "kontinu seragam", f"Turunan terbatas pada [{d}, ∞) ⇒ Lipschitz."),
             ("f(x) = √x pada [0, ∞)", "kontinu seragam", "|√x − √y| ≤ √|x − y| ⇒ δ = ε² bekerja di semua titik."),
             (f"f(x) = sin({k}x) pada ℝ", "kontinu seragam", f"|f′| ≤ {k} ⇒ Lipschitz."),
             (f"f(x) = e<sup>{k}x</sup> pada (−∞, {M}]", "kontinu seragam", f"|f′| ≤ {k}e<sup>{k * M}</sup> ⇒ Lipschitz."),
             (f"f(x) = e<sup>{k}x</sup> pada ℝ", "tidak kontinu seragam", "Kemiringan tumbuh tanpa batas untuk x → ∞."),
             (f"f(x) = ln x pada [{d}, ∞)", "kontinu seragam", f"|f′| = 1/x ≤ 1/{d}."),
             ("f(x) = ln x pada (0, 1]", "tidak kontinu seragam", "f → −∞ di dekat 0."),
             (f"f(x) = sin(1/x) pada (0, 1]", "tidak kontinu seragam", "Berosilasi makin cepat di dekat 0: titik-titik dekat bisa bernilai 1 dan −1.")]
    f, ans, why = rng.choice(cases)
    return {"prompt": f"Apakah {f} kontinu seragam?", "correct": ans,
            "distractors": ["tidak kontinu seragam" if ans == "kontinu seragam" else "kontinu seragam", "tidak kontinu", "tidak dapat ditentukan"],
            "steps": ["Kontinu seragam: δ yang sama berlaku untuk semua titik.", why, f"<b>{ans}</b>."],
            "explanation": "Kontinuitas seragam lebih kuat dari kontinuitas titik demi titik."}


@register("fms.barisan_fungsi", SR, (3, 4, 5))
def fms_bf(rng, tier):
    if tier == 3:
        if rng.random() < 0.6:
            dl, N = rng.choice([Fr(1, 2), Fr(1, 3), Fr(2, 3), Fr(3, 4), Fr(1, 4)]), rng.randint(2, 6)
            val = dl ** N
            return {"prompt": f"fₙ(x) = xⁿ → 0 titik demi titik pada [0, {n(dl)}]. Hitung sup<sub>[0, {n(dl)}]</sub> |f<sub>{N}</sub>(x) − 0| dan simpulkan.",
                    "correct": f"{n(val)}; sup = ({n(dl)})ⁿ → 0, jadi seragam pada [0, {n(dl)}]",
                    "distractors": [f"{n(val)}; tetapi tidak seragam karena x¹ⁿ → 1 di x = 1", f"1; tidak seragam", f"{n(dl * N)}; seragam", f"{n(val * 2)}; seragam"],
                    "steps": [f"xⁿ naik pada [0, {n(dl)}] ⇒ sup tercapai di x = {n(dl)}: ({n(dl)}){sup(N)} = {n(val)}.", f"Karena {n(dl)} &lt; 1, ({n(dl)})ⁿ → 0 ⇒ konvergen seragam pada [0, {n(dl)}].",
                              "Pada [0, 1] tidak seragam: limitnya loncat di x = 1 (limit seragam fungsi kontinu harus kontinu)."],
                    "explanation": "Menjauh dari titik bermasalah (x = 1) memulihkan keseragaman."}
        N = rng.randint(1, 6)
        val = Fr(N ** N, (N + 1) ** (N + 1))
        return {"prompt": f"fₙ(x) = xⁿ(1 − x) pada [0, 1]. Hitung sup |f<sub>{N}</sub>(x)|.", "correct": n(val),
                "distractors": [n(Fr(1, N + 1)), n(Fr(N, N + 1)), n(Fr(1, 4)) if val != Fr(1, 4) else "1/2", n(val * 2)],
                "steps": [f"f′ = x<sup>n−1</sup>(n − (n + 1)x) = 0 ⇒ x = n/(n + 1) = {N}/{N + 1}.", f"f({N}/{N + 1}) = ({N}/{N + 1}){sup(N)}·1/{N + 1} = {n(val)}.",
                          f"<b>{n(val)}</b>; secara umum sup ≈ 1/(e(n + 1)) → 0 ⇒ seragam."],
                "explanation": "sup|fₙ − f| dicari lewat titik kritis turunan."}
    # fₙ(x) = n^a x^b/(1 + n^c x^{2b}): u = x^b ⇒ maks di u = n^{−c/2}, nilai n^{a − c/2}/2
    c = rng.randint(1, 4)
    a, b = rng.randint(0, c - 1) if tier == 5 else rng.randint(0, c), rng.randint(1, 3)
    na = "" if a == 0 else ("n" if a == 1 else f"n{sup(a)}")
    nc = "n" if c == 1 else f"n{sup(c)}"
    xb, x2b = ("x" if b == 1 else f"x{sup(b)}"), f"x{sup(2 * b)}"
    fn_txt = f"{na}{xb}/(1 + {nc}{x2b})"
    if tier == 4:
        N = rng.choice([4, 9, 16, 25])
        val = npow(N, Fr(a) - Fr(c, 2)) / 2
        return {"prompt": f"fₙ(x) = {fn_txt} pada [0, 1]. Hitung sup |fₙ(x)| untuk n = {N}.", "correct": n(val),
                "distractors": [n(val * 2), n(npow(N, Fr(a) - c) / 2) if a != c else n(val / 2), n(npow(N, a) / 2), n(Fr(1, 2)) if val != Fr(1, 2) else "1"],
                "steps": [f"Substitusi u = {xb}: g(u) = {na or '1'}·u/(1 + {nc}u²); g′ = 0 ⇒ u = n<sup>−{n(Fr(c, 2))}</sup> (berada di [0, 1]).".replace("1·u", "u"),
                          f"Nilai maksimum = n<sup>{n(a)}</sup>·n<sup>−{n(Fr(c, 2))}</sup>/2 = n<sup>{n(Fr(2 * a - c, 2))}</sup>/2.", f"n = {N}: <b>{n(val)}</b>."],
                "explanation": "sup|fₙ| lewat titik kritis; perilakunya untuk n → ∞ menentukan keseragaman."}
    dl = rng.choice(["1/2", "1/3", "δ"])
    if 2 * a < c:
        correct = f"seragam pada [0, 1] dan pada [{dl}, 1]"
    else:
        correct = f"tidak seragam pada [0, 1], tetapi seragam pada [{dl}, 1]"
    return {"prompt": f"fₙ(x) = {fn_txt} → 0 titik demi titik pada [0, 1]. Bagaimana keseragamannya pada [0, 1] dan pada [{dl}, 1] (0 &lt; {dl} &lt; 1)?",
            "correct": correct,
            "distractors": [c_ for c_ in [f"seragam pada [0, 1] dan pada [{dl}, 1]", f"tidak seragam pada [0, 1], tetapi seragam pada [{dl}, 1]",
                                           f"tidak seragam pada keduanya", f"seragam pada [0, 1], tetapi tidak pada [{dl}, 1]"] if c_ != correct],
            "steps": [f"Pada [0, 1]: sup |fₙ| = n<sup>{n(Fr(2 * a - c, 2))}</sup>/2 (di u = {xb} = n<sup>−{n(Fr(c, 2))}</sup>) ⇒ → 0 ⇔ a &lt; c/2; di sini a = {a}, c = {c}.",
                      f"Pada [{dl}, 1] (untuk n besar fungsi turun di sana): sup ≤ n<sup>{a - c}</sup>/{dl}{sup(b) if b > 1 else ''} → 0 karena a &lt; c.",
                      f"<b>{correct}</b>."],
            "explanation": "Titik kritis yang bergeser ke 0 (u = n^{−c/2}) penyebab hilangnya keseragaman di [0, 1]."}


@register("fms.cauchy", SR, (4, 5))
def fms_cauchy(rng, tier):
    if rng.random() < 0.4:
        cases = [("Σ 1/n² konvergen", "benar — jumlah parsialnya barisan Cauchy (|Sₘ − Sₙ| ≤ 1/n)"),
                 ("Barisan Sₙ = 1 + 1/2 + … + 1/n adalah barisan Cauchy", "salah — S₂ₙ − Sₙ ≥ 1/2 untuk semua n"),
                 ("Setiap barisan Cauchy di ℝ terbatas", "benar — ambil ε = 1"),
                 ("ℚ lengkap (setiap barisan Cauchy di ℚ konvergen di ℚ)", "salah — pendekatan desimal √2")]
        s, ans = rng.choice(cases)
        return {"prompt": f"Benar atau salah: “{s}”?", "correct": ans, "distractors": [c[1] for c in cases if c[1] != ans],
                "steps": ["Barisan Cauchy: ∀ε ∃N: |aₘ − aₙ| &lt; ε untuk m, n ≥ N.", f"<b>{ans}</b>."], "explanation": "Kriteria Cauchy tidak memerlukan tahu limitnya."}
    c, E = rng.randint(1, 9), rng.choice([10, 20, 50, 100, 1000])
    if tier == 4:
        N = c * E + 1
        return {"prompt": f"aₙ = {c if c > 1 else ''}{'/' if c > 1 else '1/'}n{'' if c > 1 else ''}. Untuk m &gt; n berlaku |aₘ − aₙ| &lt; {c}/n. N terkecil agar {c}/n &lt; 1/{E} untuk semua n ≥ N?",
                "correct": str(N), "distractors": [str(c * E), str(E), str(N + c), str(c + E)],
                "steps": ["Cukup buat batas atas {c}/n lebih kecil dari ε.".replace("{c}", str(c)), f"{c}/n &lt; 1/{E} ⇔ n &gt; {c * E}.", f"N = <b>{N}</b>."],
                "explanation": "Kriteria Cauchy: cari N dari batas atas |aₘ − aₙ|."}
    r = rng.choice([Fr(1, 2), Fr(1, 3), Fr(1, 10)])
    k = rng.randint(2, 8)
    # Sₙ = Σ_{j≤n} r^j: |Sₘ − Sₙ| < r^{n+1}/(1 − r)
    bound = r ** (k + 1) / (1 - r)
    return {"prompt": f"Sₙ = Σ<sub>j=1</sub><sup>n</sup> ({n(r)})ʲ. Untuk m &gt; n = {k}, batas atas terbaik dari |Sₘ − Sₙ| (dari deret ekornya) adalah …",
            "correct": n(bound), "distractors": [n(r ** k), n(r ** (k + 1)), n(bound * 2), n(r ** k / (1 - r))],
            "steps": [f"|Sₘ − Sₙ| = Σ<sub>j=n+1</sub><sup>m</sup> rʲ &lt; Σ<sub>j=n+1</sub><sup>∞</sup> rʲ = r<sup>n+1</sup>/(1 − r).", f"n = {k}, r = {n(r)}: <b>{n(bound)}</b> → 0, jadi (Sₙ) Cauchy."],
            "explanation": "Ekor deret geometri memberi batas Cauchy eksplisit."}
