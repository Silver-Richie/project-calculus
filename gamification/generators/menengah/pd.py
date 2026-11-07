"""
Sub-level: Persamaan Diferensial Orde Satu (Level Utama 3 — Kalkulus Menengah).
Rujukan: Stewart Bab 9 (9.1–9.5); Strang (MIT) §6.3–6.7; Whitman Bab 17.
"""

from fractions import Fraction as Fr
import math

from .. import register
from ..fmt import MINUS, lin, n, paren, sup
from ..graphs import fn, g2d, hline, param, pt, readout
from ..precalc.common import distinct, nz

KO, TP, LN, MD = "km-pd-konsep", "km-pd-terpisah", "km-pd-linear", "km-pd-model"


def slope_field(title, f_js, xr, yr, sol_js=None, caption=None, params=None):
    """Medan arah: ruas-ruas pendek ber-gradien f(x, y) di grid, plus kurva solusi opsional."""
    els = []
    nx, ny = 11, 9
    for i in range(nx):
        for j in range(ny):
            x = xr[0] + (xr[1] - xr[0]) * (i + 0.5) / nx
            y = yr[0] + (yr[1] - yr[0]) * (j + 0.5) / ny
            s = f_js.replace("x", f"({x:.3f})").replace("y", f"({y:.3f})")
            h = (xr[1] - xr[0]) / nx * 0.35
            els.append({"type": "segment", "x1": f"{x:.3f}-{h:.3f}/sqrt(1+({s})**2)", "y1": f"{y:.3f}-{h:.3f}*({s})/sqrt(1+({s})**2)",
                        "x2": f"{x:.3f}+{h:.3f}/sqrt(1+({s})**2)", "y2": f"{y:.3f}+{h:.3f}*({s})/sqrt(1+({s})**2)", "color": "gray", "width": 1.4})
    if sol_js:
        els.append(fn(sol_js, "red", "solusi"))
    return g2d(title, xr, yr, params or [], els, None, caption)


# ════════════════════════ Topik 1: Konsep PD & medan arah ═════════════════
@register("pdk.cek_solusi", KO, (1, 2))
def cek_solusi(rng, tier):
    k = nz(rng, -4, 4, (0, 1))
    if tier == 1:
        prompt = f"Fungsi manakah yang merupakan solusi y′ = {k}y?"
        correct = f"y = 5e<sup>{k}x</sup>"
        wrong = [f"y = e<sup>x</sup> + {k}", f"y = {k}x²", f"y = e<sup>{-k}x</sup>", f"y = {k}e<sup>x</sup>"]
        steps = [f"Uji y = Ce<sup>{k}x</sup>: y′ = {k}Ce<sup>{k}x</sup> = {k}y ✓.", f"Konstanta C bebas (di sini 5): <b>{correct}</b>."]
    else:
        w = abs(k)
        prompt = f"Fungsi manakah yang memenuhi y″ + {w * w}y = 0?"
        correct = f"y = 3 sin({w}x) − 2 cos({w}x)"
        wrong = [f"y = e<sup>{w}x</sup>", f"y = sin({w * w}x)", f"y = 3 sin x", f"y = x² + {w * w}"]
        steps = [f"y″ dari sin({w}x) dan cos({w}x) sama dengan −{w * w} kali fungsinya.", f"Kombinasi linear keduanya memenuhi y″ + {w * w}y = 0 ⇒ <b>{correct}</b> (getaran pegas, FT)."]
    return {"prompt": prompt, "correct": correct, "distractors": wrong, "steps": steps,
            "explanation": "Memeriksa solusi: substitusikan ke persamaan, kedua ruas harus sama."}


@register("pdk.kemiringan", KO, (1, 2, 3))
def kemiringan(rng, tier):
    x0, y0 = rng.randint(-3, 3), rng.randint(-3, 3)
    if tier == 1:
        f_txt, f_js, val = "x + y", "x+y", x0 + y0
    elif tier == 2:
        f_txt, f_js, val = "x² − y", "x*x-y", x0 * x0 - y0
    else:
        f_txt, f_js, val = "xy − y²", "x*y-y*y", x0 * y0 - y0 * y0
    return {"prompt": f"Pada medan arah y′ = {f_txt}, berapa gradien ruas garis di titik ({n(x0)}, {n(y0)})?", "correct": n(val),
            "distractors": [n(-val), n(val + 1), n(x0 - y0), "0" if val else "1"],
            "steps": ["Medan arah: di setiap titik (x, y) digambar ruas kecil dengan gradien y′ = f(x, y).", f"f({n(x0)}, {n(y0)}) = <b>{n(val)}</b>."],
            "graphs": [slope_field(f"Medan arah y′ = {f_txt}", f_js, [-4, 4], [-4, 4], caption="Kurva solusi selalu menyinggung ruas-ruas kecil ini.")],
            "explanation": "PD orde satu menentukan gradien solusi di setiap titik."}


@register("pdk.euler", KO, (2, 3, 4, 5))
def euler(rng, tier):
    h = Fr(1, rng.choice([2, 4, 10])) if tier >= 3 else Fr(1, 2)
    steps_n = {2: 1, 3: 2, 4: 2, 5: 3}[tier]
    y0 = rng.randint(1, 3)
    a = rng.randint(1, 2)
    x, y = Fr(0), Fr(y0)
    lines = []
    for _ in range(steps_n):
        slope = a * x + y
        y = y + h * slope
        lines.append(f"x = {n(x)}: y′ = {n(a)}·{n(x)} + {n(y - h * slope)} = {n(slope)} ⇒ y ≈ {n(y)}")
        x += h
    return {"prompt": f"Gunakan metode Euler dengan h = {n(h)} pada y′ = {'' if a == 1 else a}x + y, y(0) = {y0} untuk menaksir y({n(x)}).",
            "correct": n(y), "distractors": [n(y + h), n(y0 + x), n(y * 2), n(Fr(y0) * (1 + h) ** steps_n)],
            "steps": ["Euler: yₙ₊₁ = yₙ + h·f(xₙ, yₙ).", *lines, f"Taksiran y({n(x)}) ≈ <b>{n(y)}</b>."],
            "graphs": [g2d("Euler vs solusi eksak", [-0.1, 1.6], [0, 10], [param("hh", "Langkah h", 0.05, 0.5, 0.05, float(h), "h")],
                           [fn(f"({y0}+{a})*exp(x)-{a}*x-{a}", "blue", "solusi eksak"),
                            {"type": "iter", "id": "E", "init": {"x": 0, "y": y0}, "update": {"x": "x+hh", "y": f"y+hh*({a}*x+y)"}, "steps": "floor(1.5/hh)",
                             "px": "x", "py": "y", "color": "red"}],
                           None, "Perkecil h: titik-titik Euler (merah) makin dekat ke kurva biru.")],
            "explanation": "Metode Euler mengikuti garis singgung selangkah demi selangkah (dasar simulasi numerik, Fasilkom)."}


@register("pdk.ekuilibrium", KO, (4, 5))
def ekuilibrium(rng, tier):
    p, q = sorted(distinct(rng, -4, 6, 2))
    if tier == 4:
        correct = f"y = {n(p)} stabil, y = {n(q)} tidak stabil"
        prompt = f"Tentukan solusi ekuilibrium y′ = (y − {paren(p)})(y − {paren(q)}) dan kestabilannya."
        steps = ["Ekuilibrium: y′ = 0 ⇒ y = p atau y = q.", f"Di antara {n(p)} dan {n(q)} y′ &lt; 0 (turun); di atas {n(q)} y′ &gt; 0; di bawah {n(p)} y′ &gt; 0.",
                 f"Solusi di dekat {n(p)} tertarik ke {n(p)} (stabil); di dekat {n(q)} menjauh (tidak stabil). <b>{correct}</b>."]
        wrong = [f"y = {n(p)} tidak stabil, y = {n(q)} stabil", f"keduanya stabil", f"y = {n(-p)} dan y = {n(-q)}", "tidak ada ekuilibrium"]
        js = f"(x-({p}))*(x-({q}))"
    else:
        K = rng.choice([10, 20, 50, 100])
        correct = f"y = 0 tidak stabil, y = {K} stabil"
        prompt = f"Model logistik y′ = 0,5y(1 − y/{K}). Tentukan ekuilibrium dan kestabilannya."
        steps = [f"y′ = 0 ⇒ y = 0 atau y = {K}.", f"Untuk 0 &lt; y &lt; {K}: y′ &gt; 0 (naik ke {K}); untuk y &gt; {K}: y′ &lt; 0 (turun ke {K}).", f"<b>{correct}</b> (daya tampung)."]
        wrong = [f"y = 0 stabil, y = {K} tidak stabil", "keduanya stabil", f"hanya y = {K // 2}", "tidak ada ekuilibrium"]
        js = None
    return {"prompt": prompt, "correct": correct, "distractors": wrong, "steps": steps,
            "graphs": [g2d("Garis fase: tanda y′ sebagai fungsi y", [p - 3, q + 3], [-8, 8], [], [fn(js, "blue", "f(y)"), hline(0), pt(p, 0, "green"), pt(q, 0, "red")], None,
                           "Hijau = stabil (panah menuju), merah = tidak stabil (panah menjauh).")] if js else [],
            "explanation": "PD otonom y′ = f(y): ekuilibrium di akar f; stabil bila f berubah dari + ke −."}


# ════════════════════════ Topik 2: PD terpisah ═════════════════════════════
@register("pdt.konsep", TP, (1,))
def pdt_konsep(rng, tier):
    good = rng.choice(["y′ = x²y", "y′ = eˣ⁺ʸ", "y′ = (x + 1)/y²", "y′ = y·cos x"])
    return {"prompt": "Persamaan diferensial manakah yang <b>terpisah</b> (separable)?", "correct": good,
            "distractors": ["y′ = x + y", "y′ = x² + y²", "y′ = sin(xy)", "y′ = x − y²"],
            "steps": ["PD terpisah dapat ditulis y′ = g(x)·h(y).", "eˣ⁺ʸ = eˣ·eʸ juga terpisah; x + y dan x² + y² tidak dapat dipisah menjadi perkalian.", f"<b>{good}</b>."],
            "explanation": "Pisahkan: dy/h(y) = g(x) dx, lalu integralkan kedua ruas."}


@register("pdt.eksponen", TP, (1, 2, 3))
def pdt_eksponen(rng, tier):
    k = nz(rng, -3, 3)
    a = rng.randint(1, 9)
    if tier == 1:
        correct = f"y = {a}e<sup>{n(k)}x</sup>"
        return {"prompt": f"Selesaikan y′ = {n(k)}y dengan y(0) = {a}.", "correct": correct,
                "distractors": [f"y = e<sup>{n(k)}x</sup> + {a}", f"y = {a}e<sup>x</sup>", f"y = {a}e<sup>{n(-k)}x</sup>", f"y = {n(k)}e<sup>{a}x</sup>",
                               f"y = {a + 1}e<sup>{n(k)}x</sup>", f"y = {a}e<sup>{n(k + 1)}x</sup>"],
                "steps": [f"dy/y = {n(k)} dx ⇒ ln|y| = {n(k)}x + C ⇒ y = Ae<sup>{n(k)}x</sup>.", f"y(0) = A = {a}. <b>{correct}</b>."],
                "graphs": [g2d("y = y₀e^(kx)", [-2, 2], [0, 30], [param("kk", "k", -3, 3, 0.1, k, "k"), param("y0", "y₀", 1, 9, 1, a, "y₀")], [fn("y0*exp(kk*x)", "blue", "y")],
                               None, "k > 0: tumbuh; k < 0: meluruh.")],
                "explanation": "y′ = ky ⇔ y = y₀e^(kx)."}
    k = abs(k)
    m = rng.randint(1, 3)
    val = a * 2 ** m
    return {"prompt": f"y′ = {k}y, y(0) = {a}. Hitung y({m} ln 2 / {k})." if k > 1 else f"y′ = y, y(0) = {a}. Hitung y({m} ln 2).",
            "correct": n(val), "distractors": [n(a * m * 2), n(a * 2 ** (m + 1)), n(a + 2 ** m), n(a * math.e ** m // 1)],
            "steps": [f"y = {a}e<sup>{k}x</sup>.", f"e<sup>{k}·{m} ln 2/{k}</sup> = e<sup>{m} ln 2</sup> = 2{sup(m)}.", f"y = {a}·{2 ** m} = <b>{val}</b>."],
            "explanation": "Waktu penggandaan = ln 2 / k."}


@register("pdt.xy", TP, (2, 3, 4))
def pdt_xy(rng, tier):
    c = rng.randint(1, 3)
    A = rng.randint(1, 9)
    correct = f"y = {A}e<sup>{n(Fr(c, 2)) if c != 2 else ''}x²</sup>".replace("<sup>1/2x²</sup>", "<sup>x²/2</sup>")
    return {"prompt": f"Selesaikan y′ = {'' if c == 1 else c}xy dengan y(0) = {A}.", "correct": correct,
            "distractors": [f"y = {A}e<sup>{c}x</sup>", f"y = {A} + {n(Fr(c, 2))}x²", f"y = {A}e<sup>{c}x²</sup>" if c != 2 else f"y = {A}e<sup>x²/2</sup>", f"y = e<sup>x²</sup> + {A - 1}"],
            "steps": [f"dy/y = {c}x dx ⇒ ln|y| = {n(Fr(c, 2))}x² + C.", f"y = Ae<sup>{n(Fr(c, 2))}x²</sup>, A = y(0) = {A}.", f"<b>{correct}</b> (solusi Ae^(x²) dari materi khusus FT)."],
            "graphs": [slope_field(f"Medan arah y′ = {c}xy", f"{c}*x*y", [-2, 2], [-1, 10], f"{A}*exp({c / 2}*x*x)", "Kurva merah mengikuti arah medan.")],
            "explanation": "Pisahkan variabel, integralkan, lalu gunakan syarat awal."}


@register("pdt.x_per_y", TP, (2, 3, 4, 5))
def x_per_y(rng, tier):
    if tier <= 4:
        a, b, c = rng.choice([(3, 4, 5), (4, 3, 5), (5, 12, 13), (6, 8, 10), (8, 15, 17)])
        return {"prompt": f"Selesaikan y′ = x/y, y(0) = {a} (y &gt; 0), lalu hitung y({b}).", "correct": n(c),
                "distractors": [n(a + b), n(b), n(c + 1), n(a * b)],
                "steps": ["y dy = x dx ⇒ y²/2 = x²/2 + C ⇒ y² = x² + C′.", f"y(0) = {a} ⇒ C′ = {a * a}: y = √(x² + {a * a}).", f"y({b}) = √({b * b} + {a * a}) = <b>{c}</b>."],
                "graphs": [slope_field("Medan arah y′ = x/y (hiperbola)", "x/y", [-6, 6], [0.5, 12], f"sqrt(x*x+{a * a})", "Solusi berupa cabang hiperbola y² − x² = konstan.")],
                "explanation": "PD terpisah dengan solusi implisit."}
    a, b = rng.randint(1, 3), rng.randint(1, 3)
    c3 = a ** 3 + b ** 3
    return {"prompt": f"Selesaikan y′ = x²/y², y(0) = {a}, lalu hitung y³ di x = {b}.", "correct": n(c3),
            "distractors": [n(a ** 3), n((a + b) ** 3), n(b ** 3), n(c3 + 1)],
            "steps": ["y² dy = x² dx ⇒ y³/3 = x³/3 + C ⇒ y³ = x³ + C′.", f"C′ = {a ** 3}.", f"y³({b}) = {b ** 3} + {a ** 3} = <b>{c3}</b>."],
            "explanation": "Integralkan kedua ruas setelah dipisah."}


@register("pdt.ledakan", TP, (3, 4, 5))
def ledakan(rng, tier):
    a = rng.randint(2, 6)
    if tier <= 4:
        b = rng.randint(1, a - 1)
        val = Fr(1, a - b)
        return {"prompt": f"Selesaikan y′ = y², y(0) = 1/{a}, lalu hitung y({b}).", "correct": n(val),
                "distractors": [n(Fr(1, a + b)), n(Fr(1, a) + b), n(Fr(b, a)), n(val * 2)],
                "steps": ["dy/y² = dx ⇒ −1/y = x + C.", f"y(0) = 1/{a} ⇒ C = −{a} ⇒ y = 1/({a} − x).", f"y({b}) = 1/{a - b} = <b>{n(val)}</b>."],
                "explanation": "PD nonlinear bisa memiliki solusi yang ‘meledak’ dalam waktu terbatas."}
    return {"prompt": f"Solusi y′ = y², y(0) = 1/{a} hanya terdefinisi pada interval …", "correct": f"x &lt; {a}",
            "distractors": [f"x &gt; {a}", "semua bilangan real", f"x &lt; 1/{a}", f"−{a} &lt; x &lt; {a}"],
            "steps": [f"y = 1/({a} − x).", f"y → ∞ saat x → {a}⁻ (solusi meledak).", f"Interval kontinu yang memuat x = 0: <b>x &lt; {a}</b>."],
            "graphs": [g2d("Solusi meledak: y = 1/(a − x)", [-2, a + 2], [0, 10], [param("aa", "a", 1, 6, 0.5, a, "a")],
                           [fn("1/(aa-x)", "red", "y"), {"type": "vline", "x": "aa", "color": "gray", "dash": True}], None,
                           "Semakin kecil y(0), semakin lama sebelum meledak.")],
            "explanation": "Interval keberadaan solusi bergantung pada syarat awal."}


# ════════════════════════ Topik 3: PD linear orde satu ═════════════════════
@register("pdl.faktor", LN, (1, 2))
def pdl_faktor(rng, tier):
    a = nz(rng, -4, 4)
    if tier == 1:
        correct = f"e<sup>{n(a)}x</sup>"
        prompt = f"Faktor integrasi PD y′ + {paren(a)}y = x adalah …"
        steps = ["Bentuk baku y′ + P(x)y = Q(x); faktor integrasi μ = e<sup>∫P dx</sup>.", f"P = {n(a)} ⇒ μ = <b>e<sup>{n(a)}x</sup></b>."]
        wrong = [f"e<sup>{n(-a)}x</sup>", f"{n(a)}x", "eˣ", f"e<sup>{n(a)}</sup>"]
    else:
        k = rng.randint(1, 4)
        correct = f"x{sup(k)}" if k > 1 else "x"
        prompt = f"Faktor integrasi PD y′ + ({k}/x)y = x² (x &gt; 0) adalah …"
        steps = [f"μ = e<sup>∫{k}/x dx</sup> = e<sup>{k} ln x</sup>.", f"= <b>{correct}</b>."]
        wrong = [f"x{sup(-k)}", f"e<sup>{k}x</sup>", f"ln x{sup(k)}", f"{k}x"]
    return {"prompt": prompt, "correct": correct, "distractors": wrong, "steps": steps,
            "explanation": "Kalikan PD dengan μ: ruas kiri menjadi (μy)′."}


@register("pdl.konstan", LN, (1, 2, 3, 4))
def pdl_konstan(rng, tier):
    a = rng.randint(1, 5)
    b = a * rng.randint(1, 6)
    y0 = rng.randint(0, 20)
    ss = Fr(b, a)
    if tier <= 2:
        return {"prompt": f"Solusi y′ + {a}y = {b} mendekati nilai berapa untuk x → ∞ (keadaan tunak)?", "correct": n(ss),
                "distractors": [n(b), n(a), "0", n(Fr(a, b))],
                "steps": [f"Solusi umum: y = {n(ss)} + Ce<sup>−{a}x</sup>.", f"e<sup>−{a}x</sup> → 0 ⇒ y → <b>{n(ss)}</b> (tidak bergantung syarat awal)."],
                "graphs": [g2d("Semua solusi menuju keadaan tunak", [0, 3], [-2, 25], [param("c", "Syarat awal y(0)", -2, 25, 0.5, y0, "y₀")],
                               [fn(f"{float(ss)}+(c-{float(ss)})*exp(-{a}*x)", "blue", "y"), hline(float(ss), "red")], None, "Geser y(0): kurva berbeda, tetapi tujuannya sama.")],
                "explanation": "y′ + ay = b: keadaan tunak b/a."}
    C = y0 - ss
    correct = f"y = {n(ss)} {'+' if C >= 0 else MINUS} {n(abs(C))}e<sup>−{a}x</sup>" if C else f"y = {n(ss)}"
    return {"prompt": f"Selesaikan y′ + {a}y = {b} dengan y(0) = {y0}.", "correct": correct,
            "distractors": [f"y = {n(ss)} + {n(y0)}e<sup>−{a}x</sup>", f"y = {n(y0)}e<sup>−{a}x</sup>", f"y = {n(ss)} {'+' if C >= 0 else MINUS} {n(abs(C))}e<sup>{a}x</sup>",
                            f"y = {b} + {n(C)}e<sup>−{a}x</sup>"],
            "steps": [f"μ = e<sup>{a}x</sup>: (e<sup>{a}x</sup>y)′ = {b}e<sup>{a}x</sup>.", f"e<sup>{a}x</sup>y = {n(ss)}e<sup>{a}x</sup> + C ⇒ y = {n(ss)} + Ce<sup>−{a}x</sup>.",
                      f"y(0) = {y0} ⇒ C = {n(C)}. <b>{correct}</b>."],
            "explanation": "Faktor integrasi untuk koefisien konstan."}


@register("pdl.koef_x", LN, (3, 4, 5))
def koef_x(rng, tier):
    c, m = nz(rng, -3, 4), rng.randint(0, 2)
    y1 = rng.randint(-3, 5)
    C = Fr(y1) - Fr(c, m + 2)
    val = Fr(c * 2 ** (m + 1), m + 2) + C / 2
    xm = f"x{sup(m)}" if m > 1 else ("x" if m == 1 else "")
    return {"prompt": f"Selesaikan y′ + y/x = {n(c)}{xm} (x &gt; 0), y(1) = {n(y1)}, lalu hitung y(2).", "correct": n(val),
            "distractors": [n(val + C / 2), n(Fr(c * 2 ** (m + 1), m + 2)), n(val * 2), n(y1 * 2)],
            "steps": ["μ = e<sup>∫dx/x</sup> = x ⇒ (xy)′ = " + f"{n(c)}x{sup(m + 1) if m + 1 > 1 else ''}.",
                      f"xy = {n(Fr(c, m + 2))}x{sup(m + 2)} + C ⇒ y = {n(Fr(c, m + 2))}x{sup(m + 1) if m + 1 > 1 else ''} + C/x.",
                      f"y(1) = {y1} ⇒ C = {n(C)}.", f"y(2) = {n(Fr(c * 2 ** (m + 1), m + 2))} + {n(C)}/2 = <b>{n(val)}</b>."],
            "explanation": "Koefisien P(x) = 1/x memberi faktor integrasi μ = x."}


@register("pdl.rc", LN, (4, 5))
def rc(rng, tier):
    E, R = rng.choice([5, 9, 12, 24]), rng.choice([2, 4, 5, 10])
    Cap = Fr(rng.choice([1, 2, 5]), 10)
    tau = R * Cap
    if tier == 4:
        return {"prompt": f"Rangkaian RC: R = {R} Ω, C = {n(Cap)} F, sumber E = {E} V, q(0) = 0, dengan Rq′ + q/C = E. Berapa konstanta waktu dan muatan akhirnya?",
                "correct": f"τ = {n(tau)} s, q∞ = {n(E * Cap)} C", "distractors": [f"τ = {n(Fr(R) / Cap)} s, q∞ = {n(E * Cap)} C", f"τ = {n(tau)} s, q∞ = {n(Fr(E, R))} C",
                                                                            f"τ = {n(tau)} s, q∞ = {E} C", f"τ = {n(Cap / R)} s, q∞ = {n(E * Cap)} C"],
                "steps": ["Bentuk linear: q′ + q/(RC) = E/R.", f"Solusi q(t) = EC(1 − e<sup>−t/RC</sup>), τ = RC = {n(tau)} s.", f"q → EC = <b>{n(E * Cap)} C</b>."],
                "graphs": [g2d("Pengisian kapasitor", [0, float(tau) * 6], [0, float(E * Cap) * 1.2], [param("RR", "R (Ω)", 1, 20, 1, R, "R")],
                               [fn(f"{float(E * Cap)}*(1-exp(-x/(RR*{float(Cap)})))", "blue", "q(t)"), hline(float(E * Cap), "red")], None,
                               "R lebih besar ⇒ τ lebih besar ⇒ pengisian lebih lambat.")],
                "explanation": "Rangkaian RC (FT elektro) = PD linear orde satu."}
    return {"prompt": f"Rangkaian RC dengan τ = RC = {n(tau)} s mulai kosong dan diisi menuju muatan akhir Q. Berapa lama sampai muatan mencapai Q/2?",
            "correct": f"{n(tau)}·ln 2 s", "distractors": [f"{n(tau / 2)} s", f"{n(tau)} s", f"{n(tau)}·ln 3 s", f"{n(tau * 2)} s"],
            "steps": ["q(t) = Q(1 − e<sup>−t/τ</sup>).", "Q/2 = Q(1 − e<sup>−t/τ</sup>) ⇒ e<sup>−t/τ</sup> = 1/2.", f"t = τ ln 2 = <b>{n(tau)}·ln 2 s</b>."],
            "explanation": "Waktu paruh pengisian = τ ln 2."}


# ════════════════════════ Topik 4: Model PD ════════════════════════════════
@register("pdm.bunga", MD, (1, 2))
def bunga(rng, tier):
    r = rng.choice([2, 4, 5, 8, 10])
    if tier == 1:
        correct = f"A = A₀e<sup>{n(Fr(r, 100))}t</sup>"
        return {"prompt": f"Tabungan bertambah dengan bunga kontinu {r}% per tahun: A′ = {n(Fr(r, 100))}A. Solusinya adalah …", "correct": correct,
                "distractors": [f"A = A₀(1 + {n(Fr(r, 100))}t)", f"A = A₀ + e<sup>{n(Fr(r, 100))}t</sup>", f"A = A₀e<sup>{r}t</sup>", f"A = {n(Fr(r, 100))}A₀t"],
                "steps": ["A′ = kA ⇒ A = A₀e<sup>kt</sup>.", f"k = {n(Fr(r, 100))}: <b>{correct}</b>."], "explanation": "Pertumbuhan eksponensial: laju ∝ besaran."}
    correct = f"t = ln 2 / {r / 100:g} ≈ {math.log(2) * 100 / r:.1f} tahun".replace(".", ",")
    return {"prompt": f"Dengan bunga kontinu {r}% per tahun, berapa lama tabungan menjadi dua kali lipat?", "correct": correct,
            "distractors": [f"t = {100 // r} tahun", f"t = 2/{r / 100:g} tahun".replace(".", ","), f"t = ln {r} tahun", f"t = {r / 100:g}·ln 2 tahun".replace(".", ",")],
            "steps": ["2A₀ = A₀e<sup>kt</sup> ⇒ t = ln 2/k.", f"<b>{correct}</b> (aturan 70: ≈ 70/{r})."], "explanation": "Waktu ganda = ln 2 / k."}


@register("pdm.peluruhan", MD, (1, 2, 3))
def peluruhan(rng, tier):
    h = rng.choice([5, 8, 10, 20, 30])
    if tier == 1:
        correct = f"k = ln 2 / {h}"
        return {"prompt": f"Zat meluruh menurut y′ = −ky dengan waktu paruh {h} tahun. Nilai k adalah …", "correct": correct,
                "distractors": [f"k = {h}/ln 2", f"k = 1/{h}", f"k = ln {h}/2", f"k = 2/{h}"],
                "steps": [f"y = y₀e<sup>−kt</sup>; saat t = {h}: 1/2 = e<sup>−{h}k</sup>.", f"<b>{correct}</b>."], "explanation": "k = ln 2 / waktu paruh."}
    m0 = rng.choice([100, 200, 400, 800])
    p = rng.randint(1, 3) if tier == 2 else rng.randint(2, 4)
    t = h * p
    val = Fr(m0, 2 ** p)
    return {"prompt": f"Massa awal {m0} g, waktu paruh {h} tahun, y′ = −ky. Berapa massa setelah {t} tahun?", "correct": f"{n(val)} g",
            "distractors": [f"{n(Fr(m0, 2 * p))} g", f"{n(val * 2)} g", f"{n(m0 - val)} g", f"{n(Fr(m0, p + 1))} g"],
            "steps": [f"y = {m0}·e<sup>−kt</sup> = {m0}·(1/2)<sup>t/{h}</sup>.", f"t/{h} = {p} ⇒ y = {m0}/{2 ** p} = <b>{n(val)} g</b>."],
            "explanation": "Peluruhan radioaktif: y′ = −ky (FMIPA)."}


@register("pdm.newton", MD, (2, 3, 4))
def newton(rng, tier):
    Ta = rng.choice([20, 25, 30])
    d0 = rng.choice([64, 80, 72, 54])
    r = rng.choice([Fr(1, 2), Fr(3, 4), Fr(2, 3)])
    T0, T1 = Ta + d0, Ta + d0 * r
    t1 = rng.choice([5, 10, 15])
    val = Ta + d0 * r * r
    return {"prompt": f"Kopi bersuhu {n(T0)}°C di ruang {Ta}°C menjadi {n(T1)}°C setelah {t1} menit (hukum pendinginan Newton T′ = −k(T − T<sub>ruang</sub>)). Berapa suhunya setelah {2 * t1} menit?",
            "correct": f"{n(val)}°C", "distractors": [f"{n(T1 - (T0 - T1))}°C", f"{n(Ta + d0 * r / 2)}°C", f"{n(T1)}°C", f"{n(val + 5)}°C"],
            "steps": [f"T − {Ta} = {d0}·e<sup>−kt</sup>.", f"Setelah {t1} menit selisih suhu dikali e<sup>−{t1}k</sup> = {n(r)}.",
                      f"Setelah {2 * t1} menit: dikali {n(r)}² ⇒ T = {Ta} + {d0}·{n(r * r)} = <b>{n(val)}°C</b>."],
            "graphs": [g2d("Pendinginan Newton", [0, t1 * 4], [Ta - 5, T0 + 5], [param("kk", "k", 0.01, 0.3, 0.005, round(-math.log(float(r)) / t1, 3), "k")],
                           [fn(f"{Ta}+{d0}*exp(-kk*x)", "blue", "T(t)"), hline(Ta, "gray")], None, "Suhu mendekati suhu ruang secara eksponensial (FT termodinamika).")],
            "explanation": "Selisih suhu meluruh eksponensial."}


@register("pdm.logistik", MD, (3, 4, 5))
def logistik(rng, tier):
    K = rng.choice([100, 200, 500, 1000])
    if tier == 3:
        r = rng.choice([Fr(1, 2), Fr(1, 10), Fr(1, 5)])
        return {"prompt": f"Populasi P′ = {n(r)}P(1 − P/{K}). Pada ukuran populasi berapa laju pertumbuhannya maksimum?", "correct": f"P = {K // 2}",
                "distractors": [f"P = {K}", "P = 0", f"P = {K // 4}", f"P = {n(Fr(K, 3))}"],
                "steps": [f"Laju g(P) = {n(r)}P − {n(r)}P²/{K} (parabola dalam P).", f"g′(P) = 0 ⇒ P = {K}/2.", f"<b>P = {K // 2}</b>, setengah daya tampung."],
                "graphs": [g2d("Laju pertumbuhan logistik terhadap P", [0, K], [0, float(r) * K / 4 * 1.3], [], [fn(f"{float(r)}*x*(1-x/{K})", "blue", "P′")], None,
                               "Puncak parabola di P = K/2 (titik belok kurva populasi).")],
                "explanation": "Model logistik: pertumbuhan tercepat di K/2."}
    P0 = rng.choice([K // 10, K // 5, K // 4])
    A = Fr(K - P0, P0)
    r = rng.choice([1, 2])
    return {"prompt": f"P′ = {r if r > 1 else ''}P(1 − P/{K}), P(0) = {P0}. Kapan P mencapai {K // 2}?", "correct": f"t = ln({n(A)})/{r}" if r > 1 else f"t = ln {n(A)}",
            "distractors": [f"t = ln({n(A + 1)})/{r}", f"t = {n(A)}/{r}", f"t = ln 2/{r}", f"t = ln({K})/{r}"],
            "steps": [f"Solusi P = K/(1 + Ae<sup>−rt</sup>), A = (K − P₀)/P₀ = {n(A)}.", "P = K/2 ⇔ Ae<sup>−rt</sup> = 1 ⇔ t = ln A / r.",
                      f"<b>t = ln({n(A)})/{r}</b>."],
            "graphs": [g2d("Kurva logistik", [0, 10], [0, K * 1.1], [param("rr", "r", 0.2, 2, 0.1, r, "r")],
                           [fn(f"{K}/(1+{float(A)}*exp(-rr*x))", "blue", "P(t)"), hline(K, "red"), hline(K / 2, "gray")], None, "Kurva-S: lambat, cepat, lalu melandai menuju K.")],
            "explanation": "P(t) = K/(1 + Ae^(−rt))."}


@register("pdm.campuran", MD, (4, 5))
def campuran(rng, tier):
    V = rng.choice([100, 200, 500])
    cin = Fr(rng.choice([1, 2, 5]), 10)
    rate = rng.choice([5, 10, 20])
    s0 = rng.choice([0, 10, 50])
    limit = cin * V
    if tier == 4:
        return {"prompt": f"Tangki berisi {V} L air dengan {s0} kg garam. Larutan {n(cin)} kg/L masuk {rate} L/menit, campuran keluar dengan laju sama. Berapa kg garam dalam jangka panjang?",
                "correct": f"{n(limit)} kg", "distractors": [f"{n(limit + s0)} kg", f"{s0} kg", f"{n(cin * rate)} kg", f"{n(limit / 2)} kg"],
                "steps": [f"s′ = (masuk) − (keluar) = {n(cin)}·{rate} − (s/{V})·{rate}.", f"Bentuk linear s′ + ({rate}/{V})s = {n(cin * rate)} ⇒ s → {n(cin * rate)}/({rate}/{V}).",
                          f"= <b>{n(limit)} kg</b> (konsentrasi tangki = konsentrasi masuk)."], "explanation": "Model campuran: laju = masuk − keluar."}
    tt = Fr(V, rate)
    val = (limit + s0) / 2
    return {"prompt": f"Tangki {V} L berisi {s0} kg garam; larutan {n(cin)} kg/L masuk {rate} L/menit dan keluar dengan laju sama. Berapa garam setelah t = {n(tt)}·ln 2 menit?",
            "correct": f"{n(val)} kg", "distractors": [f"{n(limit)} kg", f"{n(limit / 2)} kg", f"{n(val + s0)} kg", f"{s0} kg"],
            "steps": [f"s(t) = {n(limit)} + ({s0} − {n(limit)})e<sup>−{rate}t/{V}</sup>.", f"Pada t = ({V}/{rate}) ln 2: e<sup>…</sup> = 1/2.", f"s = {n(limit)} + ({s0} − {n(limit)})/2 = <b>{n(val)} kg</b>."],
            "explanation": "Setelah satu ‘waktu paruh’, selisih terhadap nilai akhir tinggal setengah."}
