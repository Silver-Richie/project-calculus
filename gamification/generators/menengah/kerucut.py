"""
Sub-level: Irisan Kerucut & Koordinat Kutub (Level Utama 3 — Kalkulus Menengah).
Rujukan: Stewart §10.1–10.6; Whitman Bab 10; Strang (MIT) Bab 9.
"""

from fractions import Fraction as Fr
import math

from .. import register
from ..fmt import MINUS, fac, n, paren, sup
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


# ════════════════════════ Topik 2: Elips & hiperbola ═══════════════════════
TRIPLES = [(5, 4, 3), (5, 3, 4), (13, 12, 5), (13, 5, 12), (10, 8, 6), (17, 15, 8)]


@register("ke.elips", EH, (1, 2, 3))
def elips(rng, tier):
    a, b, c = rng.choice(TRIPLES)
    ask = "fokus" if tier == 1 else rng.choice(["fokus", "eksentrisitas"])
    if ask == "fokus":
        correct = f"(±{c}, 0)"
        wrong = [f"(±{a}, 0)", f"(0, ±{c})", f"(±{b}, 0)", f"(±{a + b}, 0)"]
        step = f"c² = a² − b² = {a * a} − {b * b} = {c * c} ⇒ c = {c}; fokus <b>{correct}</b>."
    else:
        correct = n(Fr(c, a))
        wrong = [n(Fr(b, a)), n(Fr(a, c)), n(Fr(c, b)), "1"]
        step = f"c = {c}, e = c/a = <b>{correct}</b> (0 &lt; e &lt; 1 untuk elips)."
    return {"prompt": f"Tentukan {ask} elips x²/{a * a} + y²/{b * b} = 1.", "correct": correct, "distractors": wrong,
            "steps": [f"a = {a} (sumbu mayor di sumbu-x), b = {b}.", step],
            "graphs": [conic_graph("Elips: jumlah jarak ke kedua fokus = 2a", f"{a}*cos(t)", f"{b}*sin(t)", "Ubah b untuk melihat elips makin pipih/bulat.",
                                   extra=[pt(c, 0, "red", label="F₁"), pt(-c, 0, "red", label="F₂")], rng_=(-a - 3, a + 3))],
            "explanation": "Elips: x²/a² + y²/b² = 1, c² = a² − b², e = c/a."}


@register("ke.hiperbola", EH, (1, 2, 3))
def hiperbola(rng, tier):
    c, a, b = rng.choice(TRIPLES)
    ask = "asimtot" if tier == 1 else rng.choice(["asimtot", "fokus"])
    if ask == "asimtot":
        correct = f"y = ±{n(Fr(b, a))}x"
        wrong = [f"y = ±{n(Fr(a, b))}x", f"y = ±{n(Fr(c, a))}x", f"x = ±{a}", f"y = ±{b}x"]
        step = f"Asimtot y = ±(b/a)x = <b>±{n(Fr(b, a))}x</b>."
    else:
        correct = f"(±{c}, 0)"
        wrong = [f"(±{a}, 0)", f"(0, ±{c})", f"(±{n(Fr(c * c - 2 * b * b))}, 0)" if c * c - 2 * b * b > 0 else f"(±{b}, 0)", f"(±{a + b}, 0)"]
        step = f"c² = a² + b² = {a * a} + {b * b} = {c * c} ⇒ fokus <b>{correct}</b>."
    return {"prompt": f"Tentukan {ask} hiperbola x²/{a * a} − y²/{b * b} = 1.", "correct": correct, "distractors": wrong,
            "steps": [f"a = {a}, b = {b}.", step],
            "graphs": [g2d("Hiperbola dan asimtotnya", [-c - 6, c + 6], [-c - 6, c + 6], [],
                           [{"type": "param", "t": [-2.2, 2.2], "x": f"{a}*cosh(t)", "y": f"{b}*sinh(t)", "color": "blue"},
                            {"type": "param", "t": [-2.2, 2.2], "x": f"-{a}*cosh(t)", "y": f"{b}*sinh(t)", "color": "blue"},
                            fn(f"{b / a}*x", "gray", dash=True), fn(f"-{b / a}*x", "gray", dash=True)], None, "Cabang hiperbola mendekati asimtot di kejauhan.")],
            "explanation": "Hiperbola: c² = a² + b²; asimtot y = ±(b/a)x."}


@register("ke.jenis", EH, (3, 4, 5))
def jenis(rng, tier):
    if tier <= 4:
        A, C = nz(rng, -5, 5), nz(rng, -5, 5)
        D, E = rng.randint(-6, 6), rng.randint(-6, 6)
        kind = "elips (atau lingkaran)" if A * C > 0 else "hiperbola"
        if A == C:
            kind = "lingkaran"
        eq = f"{A}x² + {C}y² + {D}x + {E}y − 7 = 0".replace("+ −", "− ")
        why = "AC &gt; 0 ⇒ elips; A = C ⇒ lingkaran; AC &lt; 0 ⇒ hiperbola; AC = 0 ⇒ parabola."
    else:
        A, B, C = rng.choice([(1, 1, 1), (1, 4, 1), (1, 2, 1), (2, 3, 1), (1, 3, 2), (3, 2, 1)])
        disc = B * B - 4 * A * C
        kind = "elips (atau lingkaran)" if disc < 0 else "parabola" if disc == 0 else "hiperbola"
        eq = f"{A}x² + {B}xy + {C}y² − 4 = 0".replace(" 1x", " x").replace(" 1y", " y")
        why = f"Diskriminan B² − 4AC = {B * B} − {4 * A * C} = {disc}: &lt; 0 elips, = 0 parabola, &gt; 0 hiperbola."
    options = ["elips (atau lingkaran)", "hiperbola", "parabola", "lingkaran"]
    return {"prompt": f"Persamaan {eq} menyatakan irisan kerucut jenis apa?", "correct": kind, "distractors": [o for o in options if o != kind] + ["garis lurus"],
            "steps": [why, f"Jawaban: <b>{kind}</b>."], "explanation": "Jenis irisan kerucut dari koefisien kuadratnya."}


@register("ke.orbit", EH, (4, 5))
def orbit(rng, tier):
    a, b, c = rng.choice(TRIPLES)
    if tier == 4:
        return {"prompt": f"Orbit satelit berbentuk elips dengan setengah sumbu mayor {a}·10³ km dan eksentrisitas {n(Fr(c, a))}; bumi di salah satu fokus. Berapa jarak terdekat (perigee) dan terjauh (apogee)?",
                "correct": f"{a - c}·10³ km dan {a + c}·10³ km", "distractors": [f"{b}·10³ km dan {a}·10³ km", f"{a - b}·10³ km dan {a + b}·10³ km", f"{c}·10³ km dan {a}·10³ km", f"{a}·10³ km dan {a + c}·10³ km"],
                "steps": [f"c = ae = {c}·10³ km.", f"Jarak fokus ke ujung sumbu mayor: a − c dan a + c.", f"<b>{a - c}·10³ km dan {a + c}·10³ km</b>."],
                "explanation": "Hukum Kepler I: orbit planet/satelit berupa elips dengan pusat massa di fokus."}
    return {"prompt": f"Hitung luas elips x²/{a * a} + y²/{b * b} = 1 dengan integral.", "correct": pi_txt(a * b),
            "distractors": [pi_txt(a * a), pi_txt(Fr(a * b, 2)), pi_txt(a + b), n(a * b)],
            "steps": [f"Luas = 4∫₀^{a} {b}√(1 − x²/{a * a}) dx.", f"Substitusi x = {a} sin θ: 4·{a * b}·∫₀^{{π/2}} cos²θ dθ = 4·{a * b}·π/4.", f"= <b>{pi_txt(a * b)}</b>."],
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
    choices = [(3, 4, 5), (4, 3, 5), (5, 12, 13)] if tier == 1 else [(1, 1, None), (1, 0, None), (0, 2, None), (-2, 0, None), (-1, -1, None), (3, 4, 5)]
    x, y, r = rng.choice(choices)
    if r is None:
        r2 = x * x + y * y
        rt = f"√{r2}" if int(r2 ** 0.5) ** 2 != r2 else str(int(r2 ** 0.5))
        th = {(1, 1): "π/4", (1, 0): "0", (0, 2): "π/2", (-2, 0): "π", (-1, -1): "5π/4"}[(x, y)]
        correct = f"({rt}, {th})"
        wrong = [f"({rt}, {'π/4' if th != 'π/4' else '3π/4'})", f"({r2}, {th})", f"({rt}, {'π' if th != 'π' else '0'})", f"({abs(x) + abs(y)}, {th})"]
        steps = ["r = √(x² + y²), tan θ = y/x (perhatikan kuadran).", f"r = {rt}, θ = {th}.", f"<b>{correct}</b>."]
    else:
        correct = f"({r}, arctan({n(Fr(y, x))}))"
        wrong = [f"({r}, arctan({n(Fr(x, y))}))", f"({x + y}, arctan({n(Fr(y, x))}))", f"({r * r}, arctan({n(Fr(y, x))}))", f"({r}, {n(Fr(y, x))})"]
        steps = [f"r = √({x * x} + {y * y}) = {r}.", f"Titik di kuadran I: θ = arctan({y}/{x}).", f"<b>{correct}</b>."]
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
    if tier == 3:
        a = rng.randint(1, 3)
        pol, kind, js = f"r = {a}(1 + cos θ)", "kardioid", f"{a}*(1+cos(t))"
        wrong = ["mawar 4 kelopak", "spiral Archimedes", "lemniskat", "lingkaran"]
        why = "r = a(1 ± cos θ) atau a(1 ± sin θ) berbentuk hati (kardioid)."
    else:
        m = rng.randint(2, 6)
        petals = m if m % 2 else 2 * m
        pol, kind, js = f"r = 3 cos({m}θ)", f"mawar {petals} kelopak", f"3*cos({m}*t)"
        wrong = [f"mawar {m if m % 2 == 0 else 2 * m} kelopak", f"mawar {m + 1} kelopak", "kardioid", "lingkaran"]
        why = f"r = a cos(nθ): n ganjil ⇒ n kelopak, n genap ⇒ 2n kelopak. n = {m}."
    return {"prompt": f"Kurva kutub {pol} berbentuk …", "correct": kind, "distractors": wrong, "steps": [why, f"<b>{kind}</b>."],
            "graphs": [polar_graph(pol, js, "Kurva digambar dengan x = r cos θ, y = r sin θ untuk 0 ≤ θ ≤ 2π.", params=None, lim=4)],
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
    a = rng.randint(1, 4)
    if tier == 4:
        return {"prompt": f"Tentukan dy/dx pada lingkaran r = {a} di θ = π/4.", "correct": "−1", "distractors": ["1", "0", "tidak terdefinisi", f"{MINUS}{a}"],
                "steps": ["x = r cos θ, y = r sin θ dengan r konstan.", "dy/dx = (r cos θ)/(−r sin θ) = −cot θ.", "Di π/4: <b>−1</b>."],
                "explanation": "dy/dx = (r′ sin θ + r cos θ)/(r′ cos θ − r sin θ)."}
    return {"prompt": f"Tentukan dy/dx pada kardioid r = {a}(1 + cos θ) di θ = π/2.", "correct": "1", "distractors": ["−1", "0", "tidak terdefinisi", f"{a}"],
            "steps": [f"r = {a}, r′ = −{a} sin θ = −{a} di θ = π/2.", "dy/dx = (r′ sin θ + r cos θ)/(r′ cos θ − r sin θ) = (−a + 0)/(0 − a).", "= <b>1</b>."],
            "explanation": "Turunan kurva kutub lewat parametrisasi x(θ), y(θ)."}


@register("kc.parametrik_luas", KC, (3, 4, 5))
def parametrik_luas(rng, tier):
    r = rng.randint(1, 4)
    if tier <= 4:
        a, b = rng.randint(1, 5), rng.randint(1, 5)
        return {"prompt": f"Hitung luas daerah di dalam kurva x = {a} cos t, y = {b} sin t (0 ≤ t ≤ 2π).", "correct": pi_txt(a * b),
                "distractors": [pi_txt(a * a), pi_txt(Fr(a * b, 2)), pi_txt(2 * a * b), n(a * b)],
                "steps": ["Luas = ∫ y dx = |∫₀^{2π} y(t)x′(t) dt|.", f"∫ {b} sin t·(−{a} sin t) dt = −{a * b}π.", f"Luas = <b>{pi_txt(a * b)}</b> (elips)."],
                "explanation": "Luas daerah kurva parametrik tertutup: ∫ y dx."}
    return {"prompt": f"Hitung luas di bawah satu lengkung sikloida x = {r}(t − sin t), y = {r}(1 − cos t).", "correct": pi_txt(3 * r * r),
            "distractors": [pi_txt(2 * r * r), pi_txt(4 * r * r), n(8 * r), pi_txt(r * r)],
            "steps": [f"Luas = ∫₀^{{2π}} y·x′ dt = {r * r}∫ (1 − cos t)² dt.", "∫₀^{2π} (1 − 2cos t + cos²t) dt = 2π + π = 3π.", f"= <b>{pi_txt(3 * r * r)}</b> (3 kali luas roda)."],
            "explanation": "Hasil Roberval: luas sikloida = 3πr²."}
