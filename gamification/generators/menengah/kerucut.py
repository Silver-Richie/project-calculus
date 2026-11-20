"""
Sub-level: Irisan Kerucut & Koordinat Kutub (Level Utama 3 — Kalkulus Menengah).
Rujukan: Stewart §10.1–10.6; Whitman Bab 10; Strang (MIT) Bab 9.
"""

from fractions import Fraction as Fr
import math

from .. import register
from ..fmt import MINUS, fac, n, paren, sqrt_simplify, sup, surd, terms, times
from ..graphs import fn, g2d, param, pt, readout
from ..precalc.common import distinct, nz
from ..precalc.trigonometri import exact, rad_text
from ..dasar.aplikasi import pi_txt

PB, EH, KK, KC = "km-ker-parabola", "km-ker-elips", "km-kut-koordinat", "km-kut-kalkulus"


def conic_graph(title, x_js, y_js, caption, params=None, extra=None, rng_=(-10, 10)):
    return g2d(title, list(rng_), list(rng_), params or [],
               [{"type": "param", "t": [0, "2*pi"], "x": x_js, "y": y_js, "color": "blue", "samples": 300}] + (extra or []), None, caption)


def polar_graph(title, r_js, caption, params=None, lim=4, t_max="2*pi"):
    return g2d(title, [-lim, lim], [-lim, lim], params or [],
               [{"type": "param", "t": [0, t_max], "x": f"({r_js})*cos(t)", "y": f"({r_js})*sin(t)", "color": "blue", "samples": 400}], None, caption)


# ════════════════════════ Topik 1: Parabola ════════════════════════════════
@register("kp.fokus", PB, (1, 2, 3))
def fokus(rng, tier):
    p = nz(rng, -4, 4)
    h, k = (0, 0) if tier < 3 else (rng.randint(-3, 3), rng.randint(-3, 3))
    axis = rng.choice(["x", "y"]) if tier >= 2 else "x"
    if axis == "x":
        eq = f"{fac(k, 'y') if k else 'y'}² = {4 * p}{fac(h)}" if tier == 3 else f"y² = {4 * p}x"
        F, D = f"({n(h + p)}, {n(k)})", f"x = {n(h - p)}"
    else:
        eq = f"{fac(h) if h else 'x'}² = {4 * p}{fac(k, 'y')}" if tier == 3 else f"x² = {4 * p}y"
        F, D = f"({n(h)}, {n(k + p)})", f"y = {n(k - p)}"
    correct = f"fokus {F}, direktriks {D}"
    wrongF = f"({n(h - p)}, {n(k)})" if axis == "x" else f"({n(h)}, {n(k - p)})"
    wrongD = f"x = {n(h + p)}" if axis == "x" else f"y = {n(k + p)}"
    return {"prompt": f"Tentukan fokus dan direktriks parabola {eq}.".replace("(x − 0)", "x").replace("(y − 0)", "y"), "correct": correct,
            "distractors": [f"fokus {wrongF}, direktriks {wrongD}", f"fokus {F}, direktriks {wrongD}", f"fokus ({n(h + 4 * p)}, {n(k)}), direktriks {D}",
                            f"fokus {wrongF}, direktriks {D}"],
            "steps": ["Bentuk baku y² = 4px: puncak (0, 0), fokus (p, 0), direktriks x = −p (untuk x² = 4py: fokus (0, p), direktriks y = −p).",
                      f"4p = {4 * p} ⇒ p = {n(p)}" + (f"; puncak digeser ke ({n(h)}, {n(k)})." if tier == 3 else "."), f"<b>{correct}</b>."],
            "graphs": [g2d("Parabola: setiap titik berjarak sama ke fokus dan direktriks", [-10, 10], [-10, 10],
                           [param("pp", "p", -4, 4, 0.25, p, "p"), param("t", "titik pada parabola (t)", -3, 3, 0.05, 1, "t")],
                           [{"type": "param", "t": [-4, 4], "x": "pp*t*t", "y": "2*pp*t", "color": "blue"} if axis == "x" else
                            {"type": "param", "t": [-4, 4], "x": "2*pp*t", "y": "pp*t*t", "color": "blue"},
                            pt("pp", 0, "red", label="F") if axis == "x" else pt(0, "pp", "red", label="F")],
                           [readout("jarak ke fokus", "pp*(1+t*t)", 4), readout("jarak ke direktriks", "pp*t*t+pp", 4)], "Kedua jarak di tabel selalu sama (definisi parabola).")],
            "explanation": "Parabola = himpunan titik berjarak sama ke fokus dan direktriks."}


@register("kp.melalui", PB, (1, 2))
def melalui(rng, tier):
    a, b = rng.randint(1, 5), nz(rng, -6, 6)
    p = Fr(b * b, 4 * a)
    return {"prompt": f"Parabola y² = 4px melalui titik ({a}, {n(b)}). Tentukan p.", "correct": f"p = {n(p)}",
            "distractors": [f"p = {n(Fr(b * b, a))}", f"p = {n(Fr(4 * a, b * b))}", f"p = {n(Fr(b, 4 * a))}", f"p = {n(p * 2)}"],
            "steps": [f"{n(b)}² = 4p·{a}.", f"p = {b * b}/{4 * a} = <b>{n(p)}</b>."], "explanation": "Substitusi titik ke persamaan."}


@register("kp.lengkap_kuadrat", PB, (2, 3, 4))
def lengkap_kuadrat(rng, tier):
    h, k = rng.randint(-4, 4), rng.randint(-4, 4)
    p = nz(rng, -3, 3)
    # (y − k)² = 4p(x − h) ⇒ y² − 2ky − 4px + (k² + 4ph) = 0
    c = k * k + 4 * p * h
    eq = f"y² {'+' if -2 * k >= 0 else MINUS} {abs(2 * k)}y {'+' if -4 * p >= 0 else MINUS} {abs(4 * p)}x {'+' if c >= 0 else MINUS} {abs(c)} = 0"
    correct = f"({n(h)}, {n(k)})"
    return {"prompt": f"Tentukan puncak parabola {eq}.", "correct": correct,
            "distractors": [f"({n(-h)}, {n(-k)})", f"({n(k)}, {n(h)})", f"({n(h)}, {n(-k)})", f"({n(c)}, {n(k)})"],
            "steps": [f"Kelompokkan y: y² − {n(2 * k)}y = {n(4 * p)}x − {paren(c)}.", f"Lengkapkan kuadrat: (y − {paren(k)})² = {n(4 * p)}x − {paren(c)} + {k * k} = {n(4 * p)}(x − {paren(h)}).",
                      f"Puncak <b>{correct}</b>."], "explanation": "Melengkapkan kuadrat membawa ke bentuk baku."}


@register("kp.reflektor", PB, (3, 4, 5))
def reflektor(rng, tier):
    D = rng.choice([2, 4, 6, 8, 12])
    d = rng.choice([Fr(1, 2), Fr(1), Fr(3, 2), Fr(1, 4)])
    p = Fr(D * D, 16) / d
    return {"prompt": f"Antena parabola berdiameter {D} m dan kedalaman {n(d)} m. Seberapa jauh dari puncak penerima harus dipasang (di fokus)?",
            "correct": f"{n(p)} m", "distractors": [f"{n(p * 2)} m", f"{n(Fr(D, 4))} m", f"{n(d)} m", f"{n(Fr(D * D, 4) / d)} m"],
            "steps": ["Gunakan x² = 4py dengan puncak di dasar antena.", f"Tepi antena di (±{n(Fr(D, 2))}, {n(d)}): {n(Fr(D * D, 4))} = 4p·{n(d)}.", f"p = <b>{n(p)} m</b>."],
            "explanation": "Sifat pantul parabola: sinar sejajar sumbu terkumpul di fokus (FT telekomunikasi)."}


@register("kp.singgung", PB, (4, 5))
def kp_singgung(rng, tier):
    p = rng.randint(1, 3)
    t = nz(rng, -3, 3)
    x0, y0 = p * t * t, 2 * p * t
    m = Fr(1, t)
    c = y0 - m * x0
    correct = f"y = {n(m)}x + {n(c)}".replace("+ −", "− ")
    return {"prompt": f"Tentukan garis singgung parabola y² = {4 * p}x di titik ({x0}, {n(y0)}).", "correct": correct,
            "distractors": [f"y = {n(-m)}x + {n(y0 + m * x0)}".replace("+ −", "− "), f"y = {n(m * 2)}x + {n(y0 - 2 * m * x0)}".replace("+ −", "− "), f"y = {n(m)}x + {n(y0)}".replace("+ −", "− "),
                            f"y = {n(t)}x + {n(y0 - t * x0)}".replace("+ −", "− ")],
            "steps": [f"Turunan implisit: 2y·y′ = {4 * p} ⇒ y′ = {2 * p}/y.", f"Di y = {n(y0)}: m = {n(m)}.", f"<b>{correct}</b>."],
            "explanation": "Garis singgung irisan kerucut via turunan implisit."}


def rootxt(v):
    """√v disederhanakan sebagai teks (v bulat ≥ 0)."""
    c, r = sqrt_simplify(v)
    return surd(c, r)


def ctr(var, h):
    return f"{var}²" if h == 0 else f"({var} {MINUS} {h})²" if h > 0 else f"({var} + {-h})²"


# ════════════════════════ Topik 2: Elips & hiperbola ═══════════════════════
TRIPLES = [(5, 4, 3), (5, 3, 4), (13, 12, 5), (13, 5, 12), (10, 8, 6), (17, 15, 8)]


@register("ke.elips", EH, (1, 2, 3))
def elips(rng, tier):
    a = rng.randint(2, 7)
    b = rng.randint(1, a - 1)
    c2 = a * a - b * b
    h, k = (0, 0) if tier == 1 else (rng.randint(-3, 3), rng.randint(-3, 3))
    vert = tier >= 2 and rng.random() < 0.4
    ask = "fokus" if tier == 1 else rng.choice(["fokus", "eksentrisitas"])
    ct = rootxt(c2)
    X, Y = ctr("x", h), ctr("y", k)
    eq = (f"{X}/{b * b} + {Y}/{a * a} = 1" if vert else f"{X}/{a * a} + {Y}/{b * b} = 1").replace("²/1 ", "² ").replace("²/1 =", "² =")
    if ask == "fokus":
        F = (lambda s: f"({n(h)}, {n(k)} ± {s})") if vert else (lambda s: f"({n(h)} ± {s}, {n(k)})")
        G = (lambda s: f"({n(h)} ± {s}, {n(k)})") if vert else (lambda s: f"({n(h)}, {n(k)} ± {s})")
        if (h, k) == (0, 0):
            F = (lambda s: f"(0, ±{s})") if vert else (lambda s: f"(±{s}, 0)")
            G = (lambda s: f"(±{s}, 0)") if vert else (lambda s: f"(0, ±{s})")
        correct = F(ct)
        wrong = [F(str(a)), G(ct), F(rootxt(a * a + b * b)), F(str(b))]
        step = f"c² = a² − b² = {a * a} − {b * b} = {c2} ⇒ c = {ct}; fokus berjarak c dari pusat ({n(h)}, {n(k)}) sepanjang sumbu mayor: <b>{correct}</b>."
    else:
        cc, r = sqrt_simplify(c2)
        g = math.gcd(cc, a)
        correct = surd(cc // g, r) + (f"/{a // g}" if a // g > 1 else "")
        wrong = [n(Fr(b, a)), n(Fr(c2, a * a)), surd(cc, r) + f"/{b}" if b > 1 else surd(cc, r), rootxt(a * a + b * b) + f"/{a}"]
        step = f"c = √({a * a} − {b * b}) = {ct}; e = c/a = <b>{correct}</b> (0 &lt; e &lt; 1 untuk elips)."
    return {"prompt": f"Tentukan {ask} elips {eq}.", "correct": correct, "distractors": wrong,
            "steps": [f"Penyebut terbesar a² = {a * a} ada di bawah {'y' if vert else 'x'} ⇒ sumbu mayor {'tegak' if vert else 'mendatar'}; b² = {b * b}; pusat ({n(h)}, {n(k)}).", step],
            "graphs": [conic_graph("Elips: jumlah jarak ke kedua fokus = 2a", f"{h}+{b if vert else a}*cos(t)", f"{k}+{a if vert else b}*sin(t)", "Ubah b untuk melihat elips makin pipih/bulat.",
                                   extra=[pt(h, k + math.sqrt(c2), "red", label="F₁") if vert else pt(h + math.sqrt(c2), k, "red", label="F₁"),
                                          pt(h, k - math.sqrt(c2), "red", label="F₂") if vert else pt(h - math.sqrt(c2), k, "red", label="F₂")], rng_=(-a - 6, a + 6))],
            "explanation": "Elips: c² = a² − b² (a = setengah sumbu mayor), e = c/a."}


@register("ke.hiperbola", EH, (1, 2, 3))
def hiperbola(rng, tier):
    a, b = rng.randint(1, 6), rng.randint(1, 6)
    h, k = (0, 0) if tier == 1 else (rng.randint(-3, 3), rng.randint(-3, 3))
    ask = "asimtot" if tier == 1 else rng.choice(["asimtot", "fokus"])
    X, Y = ctr("x", h), ctr("y", k)
    m = Fr(b, a)
    if ask == "asimtot":
        L = "y" if k == 0 else f"y {MINUS} {k}" if k > 0 else f"y + {-k}"
        R = "x" if h == 0 else f"(x {MINUS} {h})" if h > 0 else f"(x + {-h})"
        mt = lambda v: "" if v == 1 else n(v) if Fr(v).denominator == 1 else f"({n(v)})"
        correct = f"{L} = ±{mt(m)}{R}"
        wrong = [f"{L} = ±{mt(Fr(a, b))}{R}", f"{L} = ±{mt(m * 2)}{R}", f"{L} = ±{mt(m * 3)}{R}", f"x = ±{a}"]
        step = f"Asimtot: {L} = ±(b/a){R} dengan b/a = {n(m)}: <b>{correct}</b>."
    else:
        ct = rootxt(a * a + b * b)
        correct = f"(±{ct}, 0)" if (h, k) == (0, 0) else f"({n(h)} ± {ct}, {n(k)})"
        G = (lambda s: f"(±{s}, 0)") if (h, k) == (0, 0) else (lambda s: f"({n(h)} ± {s}, {n(k)})")
        wrong = [G(str(a)), G(rootxt(abs(a * a - b * b))) if a != b else G("0"), f"(0, ±{ct})" if (h, k) == (0, 0) else f"({n(h)}, {n(k)} ± {ct})", G(str(a + b))]
        step = f"c² = a² + b² = {a * a} + {b * b} = {a * a + b * b} ⇒ c = {ct}; fokus <b>{correct}</b>."
    return {"prompt": f"Tentukan {ask} hiperbola {X}/{a * a} − {Y}/{b * b} = 1.".replace("²/1 ", "² "), "correct": correct, "distractors": wrong,
            "steps": [f"a = {a}, b = {b}, pusat ({n(h)}, {n(k)}).", step],
            "graphs": [g2d("Hiperbola dan asimtotnya", [h - a - 8, h + a + 8], [k - 8, k + 8], [],
                           [{"type": "param", "t": [-2.2, 2.2], "x": f"{h}+{a}*cosh(t)", "y": f"{k}+{b}*sinh(t)", "color": "blue"},
                            {"type": "param", "t": [-2.2, 2.2], "x": f"{h}-{a}*cosh(t)", "y": f"{k}+{b}*sinh(t)", "color": "blue"},
                            fn(f"{k}+{b / a}*(x-({h}))", "gray", dash=True), fn(f"{k}-{b / a}*(x-({h}))", "gray", dash=True)], None, "Cabang hiperbola mendekati asimtot di kejauhan.")],
            "explanation": "Hiperbola: c² = a² + b²; asimtot y − k = ±(b/a)(x − h)."}


@register("ke.jenis", EH, (3, 4, 5))
def jenis(rng, tier):
    if tier <= 4:
        A, C = nz(rng, -5, 5), nz(rng, -5, 5)
        D, E = rng.randint(-6, 6), rng.randint(-6, 6)
        if tier == 4 and rng.random() < 0.3:
            C = 0
        kind = "lingkaran" if A == C else "elips (atau lingkaran)" if A * C > 0 else "hiperbola" if A * C < 0 else "parabola"
        eq = terms([(A, "x²"), (C, "y²"), (D, "x"), (E, "y")], -7) + " = 0"
        why = "AC &gt; 0 ⇒ elips; A = C ⇒ lingkaran; AC &lt; 0 ⇒ hiperbola; AC = 0 ⇒ parabola."
    else:
        A, C = rng.randint(1, 4), rng.randint(1, 4)
        B = rng.randint(-6, 6)
        if rng.random() < 0.25 and math.isqrt(4 * A * C) ** 2 == 4 * A * C:
            B = math.isqrt(4 * A * C) * rng.choice([1, -1])
        disc = B * B - 4 * A * C
        kind = "elips (atau lingkaran)" if disc < 0 else "parabola" if disc == 0 else "hiperbola"
        eq = terms([(A, "x²"), (B, "xy"), (C, "y²")], -4) + " = 0"
        why = f"Diskriminan B² − 4AC = {B * B} − {4 * A * C} = {disc}: &lt; 0 elips, = 0 parabola, &gt; 0 hiperbola."
    options = ["elips (atau lingkaran)", "hiperbola", "parabola", "lingkaran"]
    return {"prompt": f"Persamaan {eq} menyatakan irisan kerucut jenis apa?", "correct": kind, "distractors": [o for o in options if o != kind] + ["garis lurus"],
            "steps": [why, f"Jawaban: <b>{kind}</b>."], "explanation": "Jenis irisan kerucut dari koefisien kuadratnya."}


@register("ke.orbit", EH, (4, 5))
def orbit(rng, tier):
    if tier == 4:
        e = rng.choice([Fr(1, 10), Fr(1, 5), Fr(1, 4), Fr(1, 3), Fr(2, 5), Fr(1, 2), Fr(3, 5), Fr(3, 4)])
        a = e.denominator * rng.randint(2, 9)
        c = a * e
        return {"prompt": f"Orbit satelit berbentuk elips dengan setengah sumbu mayor {a}·10³ km dan eksentrisitas {n(e)}; bumi di salah satu fokus. Berapa jarak terdekat (perigee) dan terjauh (apogee)?",
                "correct": f"{n(a - c)}·10³ km dan {n(a + c)}·10³ km", "distractors": [f"{n(c)}·10³ km dan {a}·10³ km", f"{n(a - 2 * c)}·10³ km dan {n(a + 2 * c)}·10³ km",
                                                                              f"{n(a * (1 - e * e))}·10³ km dan {a}·10³ km", f"{a}·10³ km dan {n(a + c)}·10³ km"],
                "steps": [f"c = ae = {a}·{n(e)} = {n(c)}·10³ km.", "Jarak fokus ke ujung sumbu mayor: a − c dan a + c.", f"<b>{n(a - c)}·10³ km dan {n(a + c)}·10³ km</b>."],
                "explanation": "Hukum Kepler I: orbit planet/satelit berupa elips dengan pusat massa di fokus."}
    a = rng.randint(2, 9)
    b = rng.randint(1, a)
    q = rng.choice([1, 1, 2, 4])
    part = {1: "", 2: "bagian atas (y ≥ 0) ", 4: "bagian di kuadran I "}[q]
    val = Fr(a * b, q)
    return {"prompt": f"Hitung luas {part}elips x²/{a * a} + y²/{b * b} ≤ 1 dengan integral.".replace("²/1 ", "² "), "correct": times(val, "π"),
            "distractors": [times(Fr(a * a, q), "π"), times(val / 2, "π"), times(val * 2, "π"), n(val)],
            "steps": [f"Luas penuh = 4∫₀^{a} {b}√(1 − x²/{a * a}) dx.", f"Substitusi x = {a} sin θ: 4·{a * b}·∫₀^{{π/2}} cos²θ dθ = {a * b}π.", f"Bagian yang diminta: <b>{times(val, 'π')}</b>."],
            "explanation": "Luas elips πab (lingkaran: a = b = r)."}


# ════════════════════════ Topik 3: Koordinat kutub ═════════════════════════
@register("kk.ke_kartesius", KK, (1, 2))
def ke_kartesius(rng, tier):
    r = rng.randint(2, 6)
    deg = rng.choice([0, 90, 180, 270]) if tier == 1 else rng.choice([30, 60, 120, 135, 210, 300, 45])
    def mul(v):
        if v == "0":
            return "0"
        neg = v.startswith(MINUS)
        core = v.lstrip(MINUS)
        if core == "1":
            out = str(r)
        elif core == "1/2":
            out = n(Fr(r, 2))
        elif core.endswith("/2"):
            coef = Fr(r, 2)
            out = f"{'' if coef == 1 else n(coef)}{core[:-2]}"
        else:
            out = f"{r}·{core}"
        return (MINUS if neg else "") + out
    x, y = mul(exact("cos", deg)), mul(exact("sin", deg))
    correct = f"({x}, {y})"
    alt = f"({y}, {x})"
    return {"prompt": f"Ubah koordinat kutub (r, θ) = ({r}, {rad_text(deg)}) ke koordinat Kartesius.", "correct": correct,
            "distractors": [alt if alt != correct else f"({x}, {r})", f"({r}, {rad_text(deg)})", f"({mul(exact('cos', (deg + 180) % 360))}, {y})", f"({x}, {mul(exact('sin', (deg + 180) % 360))})"],
            "steps": ["x = r cos θ, y = r sin θ.", f"x = {r}·cos({rad_text(deg)}) = {x}, y = {r}·sin({rad_text(deg)}) = {y}.", f"<b>{correct}</b>."],
            "graphs": [g2d("Titik kutub", [-7, 7], [-7, 7], [param("th", "θ (derajat)", 0, 360, 1, deg, "θ"), param("rr", "r", 0, 6, 0.5, r, "r")],
                           [{"type": "segment", "x1": 0, "y1": 0, "x2": "rr*cos(th*pi/180)", "y2": "rr*sin(th*pi/180)", "color": "blue"},
                            pt("rr*cos(th*pi/180)", "rr*sin(th*pi/180)", "red")], [readout("x", "rr*cos(th*pi/180)", 4), readout("y", "rr*sin(th*pi/180)", 4)],
                           "r = jarak ke titik asal, θ = sudut dari sumbu-x positif.")],
            "explanation": "Kutub → Kartesius: x = r cos θ, y = r sin θ."}


@register("kk.ke_kutub", KK, (1, 2, 3))
def ke_kutub(rng, tier):
    s = rng.randint(1, 6)
    if tier == 1 and rng.random() < 0.5:
        x, y, r = rng.choice([(3, 4, 5), (4, 3, 5), (5, 12, 13), (12, 5, 13), (8, 15, 17)])
        x, y, r = x * s, y * s, r * s
        correct = f"({r}, arctan({n(Fr(y, x))}))"
        wrong = [f"({r}, arctan({n(Fr(x, y))}))", f"({x + y}, arctan({n(Fr(y, x))}))", f"({r * r}, arctan({n(Fr(y, x))}))", f"({r}, {n(Fr(y, x))})"]
        steps = [f"r = √({x * x} + {y * y}) = {r}.", f"Titik di kuadran I: θ = arctan({y}/{x}).", f"<b>{correct}</b>."]
    else:
        k = rng.randint(0, 7)
        dx, dy = [(1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1), (0, -1), (1, -1)][k]
        x, y = dx * s, dy * s
        rt = str(s) if dx * dy == 0 else (f"{s}√2" if s > 1 else "√2")
        th = ["0", "π/4", "π/2", "3π/4", "π", "5π/4", "3π/2", "7π/4"][k]
        th_bad = ["0", "π/4", "π/2", "3π/4", "π", "5π/4", "3π/2", "7π/4"][(k + 4) % 8]
        correct = f"({rt}, {th})"
        wrong = [f"({rt}, {th_bad})", f"({2 * s * s if dx * dy else s * s}, {th})", f"({rt}, {['π/4', '0', 'π', 'π/4', '0', 'π/4', 'π/2', '−π/4'][k]})", f"({abs(x) + abs(y)}, {th})"]
        steps = ["r = √(x² + y²), tan θ = y/x (perhatikan kuadran!).", f"r = {rt}; titik ({n(x)}, {n(y)}) memberi θ = {th}.", f"<b>{correct}</b>."]
    return {"prompt": f"Ubah titik Kartesius ({n(x)}, {n(y)}) ke koordinat kutub (r ≥ 0, 0 ≤ θ &lt; 2π).", "correct": correct, "distractors": wrong, "steps": steps,
            "explanation": "Representasi kutub tidak tunggal: (r, θ) = (r, θ + 2π) = (−r, θ + π)."}


@register("kk.persamaan", KK, (2, 3, 4, 5))
def kk_persamaan(rng, tier):
    a = rng.randint(1, 5)
    cases = [(f"r = {a}", f"x² + y² = {a * a}", "lingkaran berpusat di titik asal"),
             (f"r sin θ = {a}", f"y = {a}", "garis mendatar"),
             (f"r = {2 * a} cos θ", f"(x − {a})² + y² = {a * a}", "lingkaran berpusat ({a}, 0)"),
             (f"r = {2 * a} sin θ", f"x² + (y − {a})² = {a * a}", "lingkaran berpusat (0, {a})")]
    pol, cart, what = rng.choice(cases[:2] if tier == 2 else cases[1:])
    wrong = [c[1] for c in cases if c[1] != cart] + [f"x² + y² = {a}"]
    return {"prompt": f"Ubah persamaan kutub {pol} ke bentuk Kartesius.", "correct": cart, "distractors": wrong,
            "steps": ["Gunakan r² = x² + y², x = r cos θ, y = r sin θ (kalikan dengan r bila perlu).", f"Hasil: <b>{cart}</b> — {what.format(a=a)}."],
            "graphs": [polar_graph(f"Kurva {pol}", {f"r = {a}": str(a), f"r sin θ = {a}": f"{a}/sin(t)", f"r = {2 * a} cos θ": f"{2 * a}*cos(t)",
                                                     f"r = {2 * a} sin θ": f"{2 * a}*sin(t)"}[pol], "Kurva kutub digambar dengan x = r cos θ, y = r sin θ.", lim=2 * a + 2)],
            "explanation": "Konversi persamaan kutub ↔ Kartesius."}


@register("kk.kurva", KK, (3, 4, 5))
def kk_kurva(rng, tier):
    a, b = rng.randint(1, 4), rng.randint(1, 4)
    f = rng.choice(["cos", "sin"])
    s = rng.choice(["+", MINUS])
    if tier == 3:
        kind = rng.choice(["kardioid", "limason", "lingkaran", "spiral"])
        if kind == "kardioid":
            pol, ans, js, why = f"r = {a}(1 {s} {f} θ)", "kardioid", f"{a}*(1{'+' if s == '+' else '-'}{f}(t))", "r = a(1 ± cos θ) atau a(1 ± sin θ) berbentuk hati (kardioid)."
        elif kind == "limason":
            c, d = (a + b + 1, b) if rng.random() < 0.5 else (b, a + b)
            loop = c < d
            ans = "limason dengan simpul dalam" if loop else "limason tanpa simpul (berlekuk)"
            pol, js, why = f"r = {c} {s} {d} {f} θ", f"{c}{'+' if s == '+' else '-'}{d}*{f}(t)", f"r = a ± b {f} θ: |a| &lt; |b| ⇒ ada simpul dalam; |a| &gt; |b| ⇒ tanpa simpul; a = b ⇒ kardioid."
        elif kind == "lingkaran":
            pol, ans, js, why = f"r = {2 * a} {f} θ", "lingkaran", f"{2 * a}*{f}(t)", f"Kalikan r: r² = {2 * a}r {f} θ ⇒ lingkaran berjari-jari {a}."
        else:
            pol, ans, js, why = f"r = {a}θ", "spiral Archimedes", f"{a}*t", "r tumbuh linear terhadap θ ⇒ spiral Archimedes."
        wrong = [w for w in ["kardioid", "mawar 4 kelopak", "spiral Archimedes", "lemniskat", "lingkaran", "limason dengan simpul dalam"] if w != ans]
    else:
        m = rng.randint(2, 7)
        petals = m if m % 2 else 2 * m
        pol, ans, js = f"r = {a + 1} {f}({m}θ)", f"mawar {petals} kelopak", f"{a + 1}*{f}({m}*t)"
        wrong = [f"mawar {m if m % 2 == 0 else 2 * m} kelopak", f"mawar {petals + 1} kelopak", "kardioid", "lingkaran"]
        why = f"r = a {f}(nθ): n ganjil ⇒ n kelopak, n genap ⇒ 2n kelopak. n = {m}."
    return {"prompt": f"Kurva kutub {pol} berbentuk …", "correct": ans, "distractors": wrong, "steps": [why, f"<b>{ans}</b>."],
            "graphs": [polar_graph(pol, js, "Kurva digambar dengan x = r cos θ, y = r sin θ untuk 0 ≤ θ ≤ 2π.", params=None, lim=max(4, 2 * a + 2 * b + 2))],
            "explanation": "Mengenali bentuk kurva kutub baku (Stewart §10.3)."}


# ════════════════════════ Topik 4: Kalkulus kutub & parametrik ═════════════
@register("kc.param_slope", KC, (1, 2, 3))
def param_slope(rng, tier):
    a, b = rng.randint(-3, 3), rng.randint(1, 6)
    t = nz(rng, -3, 3)
    val = Fr(3 * t * t - b, 2 * t)
    xt = "t²" if a == 0 else f"t² {'+' if a > 0 else MINUS} {abs(a)}"
    return {"prompt": f"Kurva parametrik x = {xt}, y = t³ − {b}t. Hitung dy/dx saat t = {n(t)}.", "correct": n(val),
            "distractors": [n(Fr(2 * t, 3 * t * t - b)) if 3 * t * t - b else "0", n(3 * t * t - b), n(-val), n(val + 1)],
            "steps": ["dy/dx = (dy/dt)/(dx/dt).", f"dy/dt = 3t² − {b}, dx/dt = 2t.", f"Di t = {n(t)}: ({3 * t * t - b})/({2 * t}) = <b>{n(val)}</b>."],
            "graphs": [g2d("Kurva parametrik dan titik t", [-5, 15], [-15, 15], [param("T", "t", -3, 3, 0.01, t, "t")],
                           [{"type": "param", "t": [-3, 3], "x": f"t*t+({a})", "y": f"t**3-{b}*t", "color": "blue"},
                            pt(f"T*T+({a})", f"T**3-{b}*T", "red")], [readout("dy/dx", f"(3*T*T-{b})/(2*T)", 4)], "Garis singgung tegak saat dx/dt = 0 (t = 0).")],
            "explanation": "Turunan kurva parametrik."}


@register("kc.luas_kutub", KC, (1, 2, 3, 4))
def luas_kutub(rng, tier):
    a = rng.randint(1, 4)
    kind = rng.choice(["lingkaran", "kardioid"]) if tier < 4 else rng.choice(["kardioid", "mawar"])
    if kind == "lingkaran":
        val, pol, js = Fr(a * a), f"r = {2 * a} cos θ", f"{2 * a}*cos(t)"
        steps = [f"Luas = (1/2)∫ r² dθ, kurva tertutup untuk −π/2 ≤ θ ≤ π/2.", f"(1/2)∫ {4 * a * a} cos²θ dθ = {2 * a * a}·π/2.", f"= <b>{pi_txt(val)}</b> (lingkaran jari-jari {a})."]
    elif kind == "kardioid":
        val, pol, js = Fr(3 * a * a, 2), f"r = {a}(1 + cos θ)", f"{a}*(1+cos(t))"
        steps = ["Luas = (1/2)∫₀^{2π} a²(1 + cos θ)² dθ.", "(1 + cos θ)² = 1 + 2cos θ + cos²θ; integral pada [0, 2π] = 2π + 0 + π = 3π.", f"Luas = (1/2)·{a * a}·3π = <b>{pi_txt(val)}</b>."]
    else:
        m = rng.choice([2, 3])
        val, pol, js = Fr(a * a, 4 * m), f"r = {a} cos({m}θ) (satu kelopak)", f"{a}*cos({m}*t)"
        steps = [f"Satu kelopak: −π/{2 * m} ≤ θ ≤ π/{2 * m}.", f"(1/2)∫ {a * a}cos²({m}θ) dθ = (1/2)·{a * a}·π/{2 * m}.", f"= <b>{pi_txt(val)}</b>."]
    return {"prompt": f"Hitung luas daerah yang dilingkupi kurva kutub {pol}.", "correct": pi_txt(val),
            "distractors": [pi_txt(val * 2), pi_txt(val / 2), pi_txt(a * a * 2), n(val)], "steps": steps,
            "graphs": [polar_graph(pol, js, "Luas kutub dijumlahkan dari sektor-sektor tipis (1/2)r²dθ.", lim=2 * a + 1)],
            "explanation": "Luas daerah kutub A = (1/2)∫ r² dθ."}


@register("kc.slope_kutub", KC, (4, 5))
def slope_kutub(rng, tier):
    a = rng.randint(1, 6)
    if tier == 4:
        if rng.random() < 0.7:
            th, val = rng.choice([("π/6", "−√3"), ("π/4", "−1"), ("π/3", "−√3/3"), ("2π/3", "√3/3"), ("3π/4", "1"), ("5π/6", "√3")])
            pol, form = f"r = {a}", "dy/dx = (r cos θ)/(−r sin θ) = −cot θ (r konstan, r′ = 0)."
        else:
            th, val = rng.choice([("π/6", "−√3/3"), ("π/3", "√3/3"), ("π/8", "−1"), ("3π/8", "1")])
            pol, form = f"r = {2 * a} cos θ", f"x = {a}(1 + cos 2θ), y = {a} sin 2θ ⇒ dy/dx = −cot 2θ."
        steps = ["x = r cos θ, y = r sin θ ⇒ dy/dx = (r′ sin θ + r cos θ)/(r′ cos θ − r sin θ).", form, f"Di θ = {th}: <b>{val}</b>."]
    else:
        th, val = rng.choice([("π/6", "−1"), ("π/4", "1 − √2"), ("π/3", "0"), ("π/2", "1"), ("2π/3", "tidak terdefinisi (garis singgung tegak)"),
                              ("5π/6", "−1"), ("3π/2", "−1")])
        pol = f"r = {a}(1 + cos θ)"
        steps = [f"r′ = −{a} sin θ; pembilang a(cos θ + cos 2θ), penyebut −a(sin θ + sin 2θ).", "dy/dx = −(cos θ + cos 2θ)/(sin θ + sin 2θ).", f"Di θ = {th}: <b>{val}</b>."]
    pool = ["−1", "1", "0", "√3", "−√3", "√3/3", "−√3/3", "1 − √2", "tidak terdefinisi (garis singgung tegak)"]
    return {"prompt": f"Tentukan dy/dx pada kurva {pol} di θ = {th}.", "correct": val, "distractors": [p for p in pool if p != val],
            "steps": steps, "explanation": "Turunan kurva kutub lewat parametrisasi x(θ), y(θ); skala a tidak memengaruhi kemiringan."}


@register("kc.parametrik_luas", KC, (3, 4, 5))
def parametrik_luas(rng, tier):
    if tier <= 4:
        a, b = rng.randint(1, 6), rng.randint(1, 6)
        return {"prompt": f"Hitung luas daerah di dalam kurva x = {a} cos t, y = {b} sin t (0 ≤ t ≤ 2π).", "correct": times(a * b, "π"),
                "distractors": [times(a * a, "π") if a != b else times(2 * a * b, "π"), times(Fr(a * b, 2), "π"), times(4 * a * b, "π"), n(a * b)],
                "steps": ["Luas = |∫ y dx| = |∫₀^{2π} y(t)x′(t) dt|.", f"∫ {b} sin t·(−{a} sin t) dt = −{a * b}π.", f"Luas = <b>{times(a * b, 'π')}</b> (elips)."],
                "explanation": "Luas daerah kurva parametrik tertutup: ∫ y dx."}
    r = rng.randint(1, 6)
    kind = rng.choice(["sikloida", "astroid", "polinom"])
    if kind == "sikloida":
        val, prompt = times(3 * r * r, "π"), f"Hitung luas di bawah satu lengkung sikloida x = {r}(t − sin t), y = {r}(1 − cos t)."
        steps = [f"Luas = ∫₀^{{2π}} y·x′ dt = {r * r}∫ (1 − cos t)² dt.", "∫₀^{2π} (1 − 2cos t + cos²t) dt = 2π + π = 3π.", f"= <b>{val}</b> (3 kali luas roda)."]
        wrong = [times(2 * r * r, "π"), times(4 * r * r, "π"), n(8 * r), times(r * r, "π")]
    elif kind == "astroid":
        val, prompt = times(Fr(3 * r * r, 8), "π"), f"Hitung luas daerah di dalam astroid x = {r} cos³t, y = {r} sin³t."
        steps = [f"Luas = 4∫ (kuadran I) = 4∫<sub>π/2</sub><sup>0</sup> {r} sin³t·(−{3 * r} cos²t sin t) dt = {12 * r * r}∫₀^{{π/2}} sin⁴t cos²t dt.",
                 "Wallis: ∫₀^{π/2} sin⁴t cos²t dt = π/32.", f"= <b>{val}</b>."]
        wrong = [times(Fr(3 * r * r, 4), "π"), times(r * r, "π"), times(Fr(3 * r * r, 16), "π"), times(Fr(r * r, 8), "π")]
    else:
        c, B = rng.randint(1, 4), rng.randint(1, 3)
        v = Fr(2 * c * B ** 5, 5)
        val, prompt = n(v), f"Hitung luas di bawah kurva parametrik x = t², y = {c if c > 1 else ''}t³ untuk 0 ≤ t ≤ {B}."
        steps = ["Luas = ∫ y dx = ∫ y(t)·x′(t) dt.", f"∫₀^{B} {c if c > 1 else ''}t³·2t dt = {2 * c}·{B}⁵/5.", f"= <b>{val}</b>."]
        wrong = [n(Fr(c * B ** 4, 4)), n(v * 2), n(Fr(c * B ** 5, 5)), n(Fr(2 * c * B ** 4, 4))]
    return {"prompt": prompt, "correct": val, "distractors": wrong, "steps": steps, "explanation": "Luas kurva parametrik: ∫ y dx = ∫ y(t)x′(t) dt."}
