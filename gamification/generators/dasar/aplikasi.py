"""
Sub-level: Aplikasi Turunan (Level Utama 2 — Kalkulus Dasar).
Rujukan: Stewart §3.9–3.10, §4.1–4.7; Whitman Bab 5–6; Strang (MIT) Bab 3.
"""

from fractions import Fraction as Fr
import math

from .. import register
from ..fmt import MINUS, interval, lin, n, paren, poly, sup
from ..graphs import fn, g2d, hline, param, pt, readout, vline
from ..precalc.common import distinct, nz
from .limit import ev, js_poly
from .turunan import dpoly, tg

SG, LJ, EK, CK, OP = "kd-apl-singgung", "kd-apl-laju", "kd-apl-ekstrem", "kd-apl-cekung", "kd-apl-optimasi"


def y_line(m, c):
    return f"y = {lin(m, c)}"


def pi_txt(fr, unit=""):
    """Bilangan kπ (fr = k)."""
    fr = Fr(fr)
    if fr == 0:
        return f"0{unit}"
    coef = "" if fr == 1 else (MINUS if fr == -1 else n(fr))
    return f"{coef}π{unit}"


def per_pi(fr, unit=""):
    """Bilangan k/π."""
    fr = Fr(fr)
    return f"{n(fr.numerator)}/({fr.denominator}π){unit}" if fr.denominator != 1 else f"{n(fr)}/π{unit}"


def cubic_from_crit(rng, p, q, a=None):
    """Kubik dengan f′ = 3a(x − p)(x − q); koefisien bulat (a dipilih genap bila p + q ganjil)."""
    if a is None:
        a = rng.choice([1, -1, 2, -2]) if (p + q) % 2 == 0 else rng.choice([2, -2])
    d = rng.randint(-5, 5)
    return [a, Fr(-3 * a * (p + q), 2), 3 * a * p * q, d], a


# ════════════════════════ Topik 1: Garis singgung & aproksimasi ═══════════
@register("apl.singgung", SG, (1, 2, 3))
def singgung(rng, tier):
    deg = 2 if tier == 1 else 3
    co = [nz(rng, -2, 2)] + [rng.randint(-4, 4) for _ in range(deg)]
    x0 = rng.randint(-2, 2)
    y0, m = ev(co, x0), ev(dpoly(co), x0)
    c = y0 - m * x0
    correct = y_line(m, c)
    return {"prompt": f"Tentukan persamaan garis singgung kurva y = {poly(co)} di titik dengan x = {n(x0)}.",
            "correct": correct, "distractors": [y_line(m, y0), y_line(-m, y0 + m * x0), y_line(m, c + 1), y_line(y0, m), y_line(m + 1, c), y_line(m, c - 2)],
            "steps": [f"Titik singgung: y({n(x0)}) = {n(y0)}.", f"y′ = {poly(dpoly(co))} ⇒ m = y′({n(x0)}) = {n(m)}.",
                      f"y − {paren(y0)} = {n(m)}(x − {paren(x0)}) ⇒ <b>{correct}</b>."],
            "graphs": [tg(js_poly(co), js_poly(dpoly(co)), x0, x=(-4, 4), y=(-25, 25))],
            "explanation": "Garis singgung di x₀: y − f(x₀) = f′(x₀)(x − x₀) (soal U-S1)."}


@register("apl.titik_gradien", SG, (1, 2))
def titik_gradien(rng, tier):
    a, b, c = nz(rng, -3, 3), rng.randint(-6, 6), rng.randint(-6, 6)
    x0 = rng.randint(-3, 3)
    m = 2 * a * x0 + b
    y0 = a * x0 * x0 + b * x0 + c
    correct = f"({n(x0)}, {n(y0)})"
    return {"prompt": f"Di titik mana garis singgung kurva y = {poly([a, b, c])} memiliki gradien {n(m)}?",
            "correct": correct, "distractors": [f"({n(y0)}, {n(x0)})", f"({n(-x0)}, {n(y0)})", f"({n(x0)}, {n(m)})", f"({n(x0 + 1)}, {n(y0 + m)})"],
            "steps": [f"y′ = {lin(2 * a, b)}.", f"{lin(2 * a, b)} = {n(m)} ⇒ x = {n(x0)}.", f"y = {n(y0)} ⇒ <b>{correct}</b>."],
            "graphs": [tg(f"{a}*x*x+({b})*x+({c})", f"{2 * a}*x+({b})", x0, x=(-6, 6), y=(-30, 30))],
            "explanation": "Gradien garis singgung = nilai turunan."}


@register("apl.normal", SG, (2, 3, 4))
def normal(rng, tier):
    co = [nz(rng, -2, 2), rng.randint(-4, 4), rng.randint(-4, 4)]
    x0 = rng.randint(-2, 2)
    m = ev(dpoly(co), x0)
    while m == 0:
        x0 += 1
        m = ev(dpoly(co), x0)
    y0 = ev(co, x0)
    mn = Fr(-1, m)
    c = y0 - mn * x0
    correct = y_line(mn, c)
    return {"prompt": f"Tentukan persamaan garis <b>normal</b> kurva y = {poly(co)} di x = {n(x0)}.",
            "correct": correct, "distractors": [y_line(m, y0 - m * x0), y_line(-mn, y0 + mn * x0), y_line(mn, -c), y_line(Fr(1, m), y0 - Fr(x0, m)),
                            y_line(mn, c + 1), y_line(mn, c - 2), y_line(-m, c)],
            "steps": [f"Gradien singgung m = y′({n(x0)}) = {n(m)}.", f"Garis normal tegak lurus singgung: m<sub>n</sub> = −1/m = {n(mn)}.",
                      f"y − {paren(y0)} = {n(mn)}(x − {paren(x0)}) ⇒ <b>{correct}</b>."],
            "explanation": "Normal ⟂ singgung: m_normal · m_singgung = −1."}


@register("apl.aproksimasi", SG, (3, 4, 5))
def aproksimasi(rng, tier):
    s = rng.randint(2, 10)
    d = nz(rng, -3, 3)
    if tier <= 4:
        approx = s + Fr(d, 2 * s)
        target = s * s + d
        prompt = f"Gunakan aproksimasi linear f(x) = √x di x = {s * s} untuk menaksir √{target}."
        steps = [f"L(x) = f(a) + f′(a)(x − a) dengan a = {s * s}: f(a) = {s}, f′(a) = 1/(2·{s}) = 1/{2 * s}.",
                 f"√{target} ≈ {s} + ({n(d)})/{2 * s} = <b>{n(float(approx))}</b>.", f"Nilai sebenarnya ≈ {math.sqrt(target):.4f}."]
        expr, dexpr, a0 = "sqrt(x)", "1/(2*sqrt(x))", s * s
    else:
        approx = s + Fr(d, 3 * s * s)
        target = s ** 3 + d
        prompt = f"Gunakan aproksimasi linear f(x) = ∛x di x = {s ** 3} untuk menaksir ∛{target}."
        steps = [f"f(a) = {s}, f′(a) = 1/(3a<sup>2/3</sup>) = 1/{3 * s * s}.", f"∛{target} ≈ {s} + ({n(d)})/{3 * s * s} = <b>{n(float(approx))}</b>.",
                 f"Nilai sebenarnya ≈ {target ** (1 / 3):.5f}."]
        expr, dexpr, a0 = "cbrt(x)", "1/(3*cbrt(x)**2)", s ** 3
    correct = n(float(approx))
    return {"prompt": prompt, "correct": correct,
            "distractors": [n(float(s + Fr(d, s))), n(float(s - (approx - s))), n(float(s + d)), n(float(approx) + 0.1)],
            "steps": steps, "graphs": [tg(expr, dexpr, a0, x=(max(0.01, a0 - 6), a0 + 6), y=(s - 2, s + 2),
                                          caption="Di dekat titik singgung, garis merah hampir berimpit dengan kurva: itulah aproksimasi linear.")],
            "explanation": "f(a + Δx) ≈ f(a) + f′(a)Δx (diferensial)."}


@register("apl.singgung_luar", SG, (4, 5))
def singgung_luar(rng, tier):
    p = rng.randint(-3, 3)
    s = rng.randint(1, 4)
    q = p * p - s * s
    t1, t2 = p - s, p + s
    correct = f"m = {n(2 * t1)} atau m = {n(2 * t2)}"
    return {"prompt": f"Tentukan gradien garis-garis singgung kurva y = x² yang melalui titik ({n(p)}, {n(q)}) (di luar kurva).",
            "correct": correct, "distractors": [f"m = {n(2 * p)}", f"m = {n(t1)} atau m = {n(t2)}", f"m = {n(-2 * t1)} atau m = {n(-2 * t2)}", f"m = {n(2 * p)} atau m = {n(q)}"],
            "steps": ["Garis singgung di (t, t²): y = 2t·x − t².", f"Melalui ({n(p)}, {n(q)}): {n(q)} = 2t·{paren(p)} − t² ⇒ t² − {n(2 * p)}t + {paren(q)} = 0.",
                      f"t = {n(t1)} atau t = {n(t2)} ⇒ gradien 2t: <b>{correct}</b>."],
            "graphs": [g2d("Dua garis singgung dari titik luar", [p - 6, p + 6], [-10, 30], [param("t", "Titik singgung t", p - 5, p + 5, 0.05, t2, "t")],
                           [fn("x*x", "blue", "y = x²"), fn("2*t*x-t*t", "red", "singgung di t", dash=True), pt(p, q, "orange", label="titik luar")],
                           [readout("Garis melewati titik luar? (selisih)", f"2*t*{p}-t*t-({q})", 3)], "Geser t: hanya dua posisi yang membuat garis merah melewati titik oranye.")],
            "explanation": "Parameterkan titik singgung, lalu syaratkan garis melewati titik yang diberikan."}


# ════════════════════════ Topik 2: Laju terkait ════════════════════════════
@register("apl.laju_lingkaran", LJ, (1, 2))
def laju_lingkaran(rng, tier):
    r, dr = rng.randint(2, 20), rng.randint(1, 5)
    if tier == 1:
        val = 2 * r * dr
        prompt = f"Jari-jari lingkaran bertambah {dr} cm/s. Seberapa cepat luasnya bertambah saat r = {r} cm?"
        steps = ["A = πr² ⇒ dA/dt = 2πr·dr/dt.", f"dA/dt = 2π·{r}·{dr} = <b>{pi_txt(val, ' cm²/s')}</b>."]
        correct, wrong = pi_txt(val, " cm²/s"), [pi_txt(r * r, " cm²/s"), pi_txt(r * dr, " cm²/s"), pi_txt(2 * r, " cm²/s"), pi_txt(val * 2, " cm²/s")]
    else:
        val = 2 * dr
        prompt = f"Jari-jari lingkaran bertambah {dr} cm/s. Seberapa cepat kelilingnya bertambah (saat r = {r} cm)?"
        steps = ["K = 2πr ⇒ dK/dt = 2π·dr/dt (tidak bergantung pada r).", f"dK/dt = <b>{pi_txt(val, ' cm/s')}</b>."]
        correct, wrong = pi_txt(val, " cm/s"), [pi_txt(2 * r * dr, " cm/s"), pi_txt(dr, " cm/s"), pi_txt(2 * r, " cm/s"), pi_txt(val + 2, " cm/s")]
    return {"prompt": prompt, "correct": correct, "distractors": wrong, "steps": steps,
            "graphs": [g2d("Laju luas bergantung pada r", [0, 25], [0, 300], [param("R", "Jari-jari r", 0, 25, 0.5, r, "r")],
                           [fn(f"2*pi*x*{dr}", "blue", "dA/dt"), pt("R", f"2*pi*R*{dr}")], [readout("dA/dt", f"2*pi*R*{dr}", 3)],
                           "Lingkaran makin besar ⇒ luas bertambah makin cepat walau dr/dt tetap.")],
            "explanation": "Laju terkait: tulis hubungan besaran, turunkan terhadap waktu t (aturan rantai)."}


@register("apl.laju_kubus", LJ, (1, 2))
def laju_kubus(rng, tier):
    s, ds = rng.randint(2, 12), rng.randint(1, 4)
    if tier == 1:
        val, what, form = 3 * s * s * ds, "volume", "V = s³ ⇒ dV/dt = 3s²·ds/dt"
        unit = " cm³/s"
    else:
        val, what, form = 12 * s * ds, "luas permukaan", "L = 6s² ⇒ dL/dt = 12s·ds/dt"
        unit = " cm²/s"
    return {"prompt": f"Rusuk kubus bertambah {ds} cm/s. Seberapa cepat {what}nya bertambah saat rusuk {s} cm?",
            "correct": f"{val}{unit}", "distractors": [f"{s ** 3}{unit}", f"{3 * s * ds}{unit}", f"{val * 2}{unit}", f"{s * s * ds}{unit}"],
            "steps": [form + ".", f"Substitusi s = {s}, ds/dt = {ds}: <b>{val}{unit}</b>."],
            "explanation": "Turunkan rumus geometri terhadap t."}


@register("apl.laju_tangga", LJ, (2, 3, 4))
def laju_tangga(rng, tier):
    x, y, L = rng.choice([(3, 4, 5), (4, 3, 5), (6, 8, 10), (8, 6, 10), (5, 12, 13), (12, 5, 13)])
    dx = Fr(rng.randint(1, 4), rng.choice([1, 2]))
    dy = -Fr(x) * dx / y
    correct = f"{n(abs(dy))} m/s (turun)"
    return {"prompt": f"Tangga {L} m bersandar pada dinding tegak. Dasar tangga ditarik menjauhi dinding {n(dx)} m/s. "
                      f"Seberapa cepat ujung atas tangga turun saat dasarnya {x} m dari dinding?",
            "correct": correct, "distractors": [f"{n(dx)} m/s (turun)", f"{n(Fr(y) * dx / x)} m/s (turun)", f"{n(abs(dy))} m/s (naik)", f"{n(abs(dy) * 2)} m/s (turun)"],
            "steps": [f"x² + y² = {L}² ⇒ 2x·dx/dt + 2y·dy/dt = 0.", f"Saat x = {x}: y = √({L * L} − {x * x}) = {y}.",
                      f"dy/dt = −x·(dx/dt)/y = −{x}·{n(dx)}/{y} = {n(dy)} ⇒ <b>{correct}</b>."],
            "graphs": [g2d("Tangga meluncur", [0, L + 1], [0, L + 1], [param("X", "Jarak dasar x", 0.2, L - 0.2, 0.05, x, "x")],
                           [{"type": "segment", "x1": "X", "y1": 0, "x2": 0, "y2": f"sqrt({L * L}-X*X)", "color": "orange", "width": 5},
                            pt(0, f"sqrt({L * L}-X*X)")],
                           [readout("y", f"sqrt({L * L}-X*X)", 3), readout("dy/dt", f"-X*{float(dx)}/sqrt({L * L}-X*X)", 4)],
                           "Makin dekat ke lantai, ujung atas turun makin cepat.")],
            "explanation": "Soal U-S7 (berkas soal dasar) adalah versi tetap soal ini."}


@register("apl.laju_bola", LJ, (3, 4, 5))
def laju_bola(rng, tier):
    r = rng.randint(2, 10)
    dV = rng.choice([10, 20, 50, 100, 36, 64])
    if tier <= 4:
        dr = Fr(dV, 4 * r * r)
        prompt = f"Balon bola dipompa {dV} cm³/s. Seberapa cepat jari-jarinya bertambah saat r = {r} cm?"
        correct = per_pi(dr, " cm/s")
        steps = ["V = (4/3)πr³ ⇒ dV/dt = 4πr²·dr/dt.", f"dr/dt = {dV}/(4π·{r * r}) = <b>{correct}</b>."]
        wrong = [per_pi(Fr(dV, 4 * r ** 3), " cm/s"), per_pi(Fr(dV, r * r), " cm/s"), pi_txt(dr, " cm/s"), per_pi(dr * 2, " cm/s")]
    else:
        dr = Fr(dV, 4 * r * r)
        dS = 8 * r * dr
        prompt = f"Balon bola dipompa {dV} cm³/s. Seberapa cepat luas permukaannya bertambah saat r = {r} cm?"
        correct = f"{n(dS)} cm²/s"
        steps = ["dr/dt = (dV/dt)/(4πr²).", "S = 4πr² ⇒ dS/dt = 8πr·dr/dt = 8πr·(dV/dt)/(4πr²) = 2(dV/dt)/r.",
                 f"dS/dt = 2·{dV}/{r} = <b>{correct}</b> (π saling coret!)."]
        wrong = [f"{n(dS * 2)} cm²/s", pi_txt(dS, " cm²/s"), f"{n(Fr(dV, r))} cm²/s", f"{n(dS + 1)} cm²/s"]
    return {"prompt": prompt, "correct": correct, "distractors": wrong, "steps": steps, "explanation": "Volume & luas bola: V = 4πr³/3, S = 4πr²."}


@register("apl.laju_bayangan", LJ, (4, 5))
def laju_bayangan(rng, tier):
    H = rng.choice([6, 8, 9, 10, 12])
    h = rng.choice([v for v in (1.5, 2, 3) if v < H])
    v = rng.randint(1, 3)
    h = Fr(h).limit_denominator(2)
    tip = Fr(v) * H / (H - h)
    shadow = Fr(v) * h / (H - h)
    ask = "ujung bayangan" if tier == 4 else "panjang bayangan"
    val = tip if tier == 4 else shadow
    return {"prompt": f"Lampu jalan setinggi {H} m. Orang setinggi {n(h)} m berjalan menjauhi tiang dengan kecepatan {v} m/s. "
                      f"Seberapa cepat {ask} bergerak/bertambah?",
            "correct": f"{n(val)} m/s", "distractors": [f"{n(tip if tier == 5 else shadow)} m/s", f"{v} m/s", f"{n(Fr(v) * H / h)} m/s", f"{n(val * 2)} m/s"],
            "steps": ["Segitiga sebangun: s/h = (x + s)/H, dengan x jarak orang ke tiang dan s panjang bayangan.",
                      f"s(H − h) = hx ⇒ s = {n(h)}x/{n(H - h)} ⇒ ds/dt = {n(h / (H - h))}·{v} = {n(shadow)} m/s.",
                      f"Ujung bayangan berada di x + s ⇒ kecepatannya {v} + {n(shadow)} = {n(tip)} m/s.", f"Jawaban: <b>{n(val)} m/s</b>."],
            "explanation": "Laju terkait dengan segitiga sebangun (Stewart §3.9)."}


@register("apl.laju_kerucut", LJ, (4, 5))
def laju_kerucut(rng, tier):
    R, Hc = rng.choice([(2, 4), (3, 6), (1, 2), (2, 6), (3, 9)])
    k = Fr(R, Hc)
    h = rng.randint(2, 6)
    dV = rng.choice([2, 4, 8, 9, 12])
    dh = Fr(dV) / (k * k * h * h)
    return {"prompt": f"Air dialirkan {dV} m³/menit ke tangki kerucut terbalik (jari-jari atas {R} m, tinggi {Hc} m). "
                      f"Seberapa cepat permukaan air naik saat kedalaman {h} m?",
            "correct": per_pi(dh, " m/menit"), "distractors": [per_pi(Fr(dV, h * h), " m/menit"), per_pi(dh * 3, " m/menit"), pi_txt(dh, " m/menit"), per_pi(dh / 2, " m/menit")],
            "steps": [f"Sebangun: r/h = {R}/{Hc} ⇒ r = {n(k)}h.", f"V = (1/3)πr²h = (π/3)·{n(k * k)}·h³ ⇒ dV/dt = π·{n(k * k)}·h²·dh/dt.",
                      f"dh/dt = {dV}/(π·{n(k * k)}·{h * h}) = <b>{per_pi(dh, ' m/menit')}</b>."],
            "explanation": "Hilangkan variabel tambahan (r) dengan kesebangunan sebelum menurunkan."}


# ════════════════════════ Topik 3: Nilai ekstrem ═══════════════════════════
@register("apl.ekstrem_kuadrat", EK, (1, 2))
def ekstrem_kuadrat(rng, tier):
    a, h, k = nz(rng, -3, 3), rng.randint(-4, 4), rng.randint(-8, 8)
    co = [a, -2 * a * h, a * h * h + k]
    kind = "minimum" if a > 0 else "maksimum"
    return {"prompt": f"Dengan turunan, tentukan nilai {kind} f(x) = {poly(co)}.", "correct": n(k),
            "distractors": [n(co[2]), n(-k), n(h), n(k + a)],
            "steps": [f"f′(x) = {lin(2 * a, -2 * a * h)} = 0 ⇒ x = {n(h)}.", f"f″ = {2 * a} {'&gt;' if a > 0 else '&lt;'} 0 ⇒ {kind}.",
                      f"f({n(h)}) = <b>{n(k)}</b>."],
            "graphs": [tg(js_poly(co), js_poly(dpoly(co)), h, x=(h - 5, h + 5), y=(k - 20, k + 20),
                          caption="Di titik ekstrem, garis singgung mendatar (f′ = 0).")],
            "explanation": "Titik kritis: f′(x) = 0."}


@register("apl.kritis", EK, (1, 2))
def kritis(rng, tier):
    p, q = sorted(distinct(rng, -4, 4, 2))
    co, a = cubic_from_crit(rng, p, q)
    correct = f"x = {n(p)} dan x = {n(q)}"
    return {"prompt": f"Tentukan titik-titik kritis f(x) = {poly(co)}.", "correct": correct,
            "distractors": [f"x = {n(-p)} dan x = {n(-q)}", f"x = {n(p + q)} dan x = {n(p * q)}", f"x = {n(p)} saja", f"x = {n(Fr(p + q, 2))}"],
            "steps": [f"f′(x) = {poly(dpoly(co))}.", f"Faktorkan: f′(x) = {n(3 * a)}(x − {paren(p)})(x − {paren(q)}).", f"f′ = 0 ⇒ <b>{correct}</b>."],
            "graphs": [tg(js_poly(co), js_poly(dpoly(co)), p, x=(p - 3, q + 3), y=(-40, 40))],
            "explanation": "Titik kritis: f′(x) = 0 atau f′ tidak ada."}


@register("apl.naik_turun", EK, (2, 3))
def naik_turun(rng, tier):
    p, q = sorted(distinct(rng, -4, 4, 2))
    co, a = cubic_from_crit(rng, p, q)
    want = rng.choice(["naik", "turun"])
    up_outside = a > 0
    outside = f"{interval(None, p, hi_closed=False)} ∪ {interval(q, None, lo_closed=False)}"
    inside = interval(p, q, False, False)
    correct = outside if (want == "naik") == up_outside else inside
    return {"prompt": f"Pada interval mana f(x) = {poly(co)} <b>{want}</b>?", "correct": correct,
            "distractors": [inside if correct == outside else outside, interval(-q, -p, False, False), interval(p, None, lo_closed=False), "ℝ"],
            "steps": [f"f′(x) = {n(3 * a)}(x − {paren(p)})(x − {paren(q)}).",
                      f"Karena 3a = {n(3 * a)} {'&gt;' if a > 0 else '&lt;'} 0: f′ {'positif' if a > 0 else 'negatif'} di luar akar dan {'negatif' if a > 0 else 'positif'} di antara akar.",
                      f"f {want} ⇔ f′ {'&gt;' if want == 'naik' else '&lt;'} 0 ⇒ <b>{correct}</b>."],
            "graphs": [g2d("f (biru) dan f′ (oranye)", [p - 3, q + 3], [-40, 40], [],
                           [fn(js_poly(co), "blue", "f"), fn(js_poly(dpoly(co)), "orange", "f′", dash=True), hline(0)], None,
                           "f naik tepat ketika grafik f′ di atas sumbu-x.")],
            "explanation": "Uji turunan pertama: f′ > 0 naik, f′ < 0 turun."}


@register("apl.maks_tertutup", EK, (3, 4, 5))
def maks_tertutup(rng, tier):
    p, q = sorted(distinct(rng, -3, 3, 2))
    co, a = cubic_from_crit(rng, p, q)
    lo, hi = p - rng.randint(1, 2), q + rng.randint(0 if tier < 5 else 1, 2)
    cands = {x: ev(co, x) for x in (lo, p, q, hi)}
    want = rng.choice(["maksimum", "minimum"])
    best = max(cands, key=cands.get) if want == "maksimum" else min(cands, key=cands.get)
    val = cands[best]
    return {"prompt": f"Tentukan nilai {want} mutlak f(x) = {poly(co)} pada interval [{n(lo)}, {n(hi)}].", "correct": n(val),
            "distractors": [n(v) for x, v in cands.items() if v != val] + [n(val + 1), n(-val)],
            "steps": [f"Titik kritis: f′ = 0 ⇒ x = {n(p)}, {n(q)} (keduanya di dalam interval).",
                      "Bandingkan nilai f di titik kritis dan ujung interval: " + ", ".join(f"f({n(x)}) = {n(v)}" for x, v in cands.items()) + ".",
                      f"Nilai {want} mutlak = <b>{n(val)}</b> di x = {n(best)}."],
            "graphs": [g2d("Ekstrem mutlak pada interval tertutup", [lo - 1, hi + 1], [float(min(cands.values())) - 10, float(max(cands.values())) + 10], [],
                           [fn(js_poly(co), "blue", "f", **{"from": lo, "to": hi}), vline(lo), vline(hi)] + [pt(x, float(v), "red" if x == best else "orange") for x, v in cands.items()],
                           None, "Kandidat: titik kritis (f′ = 0) dan kedua ujung interval.")],
            "explanation": "Metode interval tertutup: bandingkan f di titik kritis dan di ujung."}


@register("apl.uji_kedua", EK, (2, 3, 4, 5))
def uji_kedua(rng, tier):
    if tier <= 4:
        p, q = sorted(distinct(rng, -3, 3, 2))
        co, a = cubic_from_crit(rng, p, q)
        mx, mn = (p, q) if a > 0 else (q, p)
        correct = f"maks. lokal di x = {n(mx)}, min. lokal di x = {n(mn)}"
        return {"prompt": f"Gunakan uji turunan kedua untuk f(x) = {poly(co)}.", "correct": correct,
                "distractors": [f"maks. lokal di x = {n(mn)}, min. lokal di x = {n(mx)}", f"min. lokal di x = {n(p)} dan x = {n(q)}",
                                f"maks. lokal di x = {n(-mx)}, min. lokal di x = {n(-mn)}", "tidak ada ekstrem lokal"],
                "steps": [f"Titik kritis x = {n(p)}, {n(q)}.", f"f″(x) = {poly(dpoly(dpoly(co)))}.",
                          f"f″({n(mx)}) = {n(ev(dpoly(dpoly(co)), mx))} &lt; 0 ⇒ maksimum; f″({n(mn)}) = {n(ev(dpoly(dpoly(co)), mn))} &gt; 0 ⇒ minimum.",
                          f"<b>{correct}</b> (soal U-S2 serupa)."],
                "explanation": "f″(c) < 0 ⇒ maksimum lokal; f″(c) > 0 ⇒ minimum lokal."}
    b = rng.randint(1, 3)
    val = -b ** 4
    return {"prompt": f"Tentukan nilai minimum f(x) = x⁴ − {2 * b * b}x² dan banyaknya ekstrem lokal.", "correct": f"min {n(val)}, 3 ekstrem lokal",
            "distractors": [f"min {n(val)}, 2 ekstrem lokal", "min 0, 3 ekstrem lokal", f"min {n(-b * b)}, 3 ekstrem lokal", f"min {n(val)}, 1 ekstrem lokal"],
            "steps": [f"f′ = 4x³ − {4 * b * b}x = 4x(x − {b})(x + {b}) ⇒ x = 0, ±{b}.", f"f″ = 12x² − {4 * b * b}: f″(0) &lt; 0 (maks), f″(±{b}) &gt; 0 (min).",
                      f"f(±{b}) = {b ** 4} − {2 * b ** 4} = {n(val)} ⇒ <b>min {n(val)}, 3 ekstrem lokal</b>."],
            "graphs": [tg(f"x**4-{2 * b * b}*x*x", f"4*x**3-{4 * b * b}*x", b, x=(-b - 2, b + 2), y=(-b ** 4 - 5, 20))],
            "explanation": "Polinom berderajat 4 dapat memiliki hingga 3 ekstrem lokal."}


# ════════════════════════ Topik 4: Kecekungan & sketsa ═════════════════════
@register("apl.cekung_kuadrat", CK, (1,))
def cekung_kuadrat(rng, tier):
    a, b, c = nz(rng, -4, 4), rng.randint(-5, 5), rng.randint(-5, 5)
    correct = "cekung ke atas di seluruh ℝ" if a > 0 else "cekung ke bawah di seluruh ℝ"
    return {"prompt": f"Bagaimana kecekungan f(x) = {poly([a, b, c])}?", "correct": correct,
            "distractors": ["cekung ke bawah di seluruh ℝ" if a > 0 else "cekung ke atas di seluruh ℝ", f"berubah kecekungan di x = {n(Fr(-b, 2 * a))}",
                            "tidak cekung (lurus)", f"cekung ke atas hanya untuk x &gt; {n(Fr(-b, 2 * a))}"],
            "steps": [f"f″(x) = {2 * a} (konstan).", f"f″ {'&gt;' if a > 0 else '&lt;'} 0 di mana-mana ⇒ <b>{correct}</b>."],
            "explanation": "f″ > 0 cekung ke atas (∪), f″ < 0 cekung ke bawah (∩)."}


@register("apl.titik_belok", CK, (1, 2, 3))
def titik_belok(rng, tier):
    a = rng.choice([1, -1, 3, -3]) if tier == 1 else rng.choice([1, -1, 2, -2, 3])
    xi = rng.randint(-3, 3)
    b = -3 * a * xi
    c, d = rng.randint(-6, 6), rng.randint(-6, 6)
    co = [a, b, c, d]
    yi = ev(co, xi)
    correct = f"({n(xi)}, {n(yi)})"
    return {"prompt": f"Tentukan titik belok f(x) = {poly(co)}.", "correct": correct,
            "distractors": [f"({n(-xi)}, {n(ev(co, -xi))})", f"({n(xi)}, {n(d)})", f"({n(yi)}, {n(xi)})", f"({n(xi + 1)}, {n(ev(co, xi + 1))})"],
            "steps": [f"f″(x) = {lin(6 * a, 2 * b)}.", f"f″ = 0 ⇒ x = {n(xi)}; tanda f″ berganti di sana (fungsi linear).",
                      f"f({n(xi)}) = {n(yi)} ⇒ titik belok <b>{correct}</b>."],
            "graphs": [g2d("Titik belok: kecekungan berganti", [xi - 4, xi + 4], [yi - 30, yi + 30], [param("s", "x uji", xi - 3.5, xi + 3.5, 0.05, xi + 1, "x")],
                           [fn(js_poly(co), "blue", "f"), pt(xi, yi, "red", label="belok"), pt("s", js_poly(co).replace("x", "s"), "orange")],
                           [readout("f″(x uji)", f"{6 * a}*s+({2 * b})", 3)], "Tanda f″ (tabel) berubah saat titik uji melewati titik belok.")],
            "explanation": "Titik belok kubik ax³ + bx² + … ada di x = −b/(3a)."}


@register("apl.cekung_interval", CK, (2, 3))
def cekung_interval(rng, tier):
    a = nz(rng, -3, 3)
    xi = rng.randint(-3, 3)
    co = [a, -3 * a * xi, rng.randint(-4, 4), rng.randint(-4, 4)]
    want = rng.choice(["ke atas", "ke bawah"])
    right = (a > 0) == (want == "ke atas")
    correct = interval(xi, None, lo_closed=False) if right else interval(None, xi, hi_closed=False)
    return {"prompt": f"Pada interval mana f(x) = {poly(co)} cekung {want}?", "correct": correct,
            "distractors": [interval(None, xi, hi_closed=False) if right else interval(xi, None, lo_closed=False), interval(-xi, None, lo_closed=False) if xi else "ℝ",
                            "ℝ", interval(xi - 1, xi + 1, False, False)],
            "steps": [f"f″(x) = {lin(6 * a, -6 * a * xi)} = {n(6 * a)}(x − {paren(xi)}).",
                      f"Cekung {want} ⇔ f″ {'&gt;' if want == 'ke atas' else '&lt;'} 0 ⇒ <b>{correct}</b>."],
            "explanation": "Tanda f″ menentukan kecekungan."}


@register("apl.baca_turunan", CK, (2, 3, 4, 5))
def baca_turunan(rng, tier):
    p, q = distinct(rng, -4, 5, 2)
    if tier <= 3:
        correct = f"hanya di x = {n(p)} (minimum lokal)"
        prompt = f"Diketahui f′(x) = (x − {paren(p)})(x − {paren(q)})². Di mana f memiliki ekstrem lokal?"
        steps = [f"f′ berganti tanda di x = {n(p)} (akar ganjil): dari − ke + ⇒ minimum lokal.",
                 f"Di x = {n(q)} (akar ganda) f′ tidak berganti tanda ⇒ bukan ekstrem (titik stasioner datar).", f"Jawaban: <b>{correct}</b>."]
        wrong = [f"di x = {n(p)} dan x = {n(q)}", f"hanya di x = {n(q)}", f"hanya di x = {n(p)} (maksimum lokal)", "tidak ada"]
        expr = f"(x-({p}))*(x-({q}))**2"
    else:
        r = rng.choice([v for v in range(-4, 6) if v not in (p, q)])
        a, b, c = sorted([p, q, r])
        correct = f"maks. lokal di x = {n(b)}; min. lokal di x = {n(a)} dan x = {n(c)}"
        prompt = f"Diketahui f′(x) = (x − {paren(a)})(x − {paren(b)})(x − {paren(c)}). Klasifikasikan ekstrem lokal f."
        steps = ["Tanda f′: − di kiri a, + di (a, b), − di (b, c), + di kanan c.", f"− → + : minimum ({n(a)}, {n(c)}); + → − : maksimum ({n(b)}).", f"<b>{correct}</b>."]
        wrong = [f"min. lokal di x = {n(b)}; maks. lokal di x = {n(a)} dan x = {n(c)}", f"maks. lokal di x = {n(a)}, {n(b)}, {n(c)}",
                 f"maks. lokal di x = {n(c)}; min. lokal di x = {n(a)}", "tidak ada ekstrem lokal"]
        expr = f"(x-({a}))*(x-({b}))*(x-({c}))"
    return {"prompt": prompt, "correct": correct, "distractors": wrong, "steps": steps,
            "graphs": [g2d("Grafik f′: ekstrem f terjadi saat f′ memotong (bukan menyinggung) sumbu-x", [-6, 7], [-30, 30], [],
                           [fn(expr, "orange", "f′(x)"), hline(0)], None, "Di akar ganda grafik f′ hanya menyinggung sumbu-x.")],
            "explanation": "Uji turunan pertama: perhatikan pergantian tanda f′."}


@register("apl.banyak_akar", CK, (4, 5))
def banyak_akar(rng, tier):
    m = rng.randint(1, 3)
    M = 2 * m ** 3
    if tier == 4:
        k = rng.choice([0, M - 1, -(M - 1), M + rng.randint(1, 5), -(M + rng.randint(1, 5)), M, -M])
        cnt = 3 if abs(k) < M else (2 if abs(k) == M else 1)
        return {"prompt": f"Berapa banyak akar real persamaan x³ − {3 * m * m}x {'+' if k >= 0 else MINUS} {abs(k)} = 0?",
                "correct": str(cnt), "distractors": [str(v) for v in (1, 2, 3, 0) if v != cnt],
                "steps": [f"f′ = 3x² − {3 * m * m} = 0 ⇒ x = ±{m}.", f"f({MINUS}{m}) = {n(M + k)} (maks), f({m}) = {n(k - M)} (min).",
                          "3 akar bila maks &gt; 0 &gt; min; 2 akar bila salah satunya 0; selain itu 1 akar.", f"Jawaban: <b>{cnt}</b>."],
                "graphs": [g2d("Geser k: banyak titik potong dengan sumbu-x", [-4, 4], [-30, 30], [param("k", "k", -M - 10, M + 10, 0.5, k, "k")],
                               [fn(f"x**3-{3 * m * m}*x+k", "blue", "f"), hline(0)], [readout("maks", f"{M}+k", 3), readout("min", f"k-{M}", 3)],
                               "Akar real = titik potong grafik dengan sumbu-x.")],
                "explanation": "Banyak akar kubik dapat dibaca dari tanda nilai maksimum & minimum lokalnya."}
    return {"prompt": f"Tentukan semua k agar x³ − {3 * m * m}x + k = 0 memiliki tiga akar real berbeda.", "correct": f"{MINUS}{M} &lt; k &lt; {M}",
            "distractors": [f"{MINUS}{M} ≤ k ≤ {M}", f"k &gt; {M}", f"{MINUS}{m} &lt; k &lt; {m}", f"{MINUS}{3 * m * m} &lt; k &lt; {3 * m * m}"],
            "steps": [f"Ekstrem di x = ±{m}: maks {M} + k, min k − {M}.", f"Tiga akar ⇔ {M} + k &gt; 0 dan k − {M} &lt; 0.", f"<b>{MINUS}{M} &lt; k &lt; {M}</b>."],
            "explanation": "Gunakan nilai ekstrem untuk menganalisis banyak akar."}


# ════════════════════════ Topik 5: Optimasi, L'Hôpital, TNR ═════════════════
@register("apl.opt_bilangan", OP, (1, 2))
def opt_bilangan(rng, tier):
    S = 2 * rng.randint(3, 30)
    if tier == 1:
        val, what = S * S // 4, "hasil kali maksimum"
        steps = [f"y = {S} − x ⇒ P(x) = x({S} − x).", f"P′ = {S} − 2x = 0 ⇒ x = {S // 2}.", f"P = {S // 2}·{S // 2} = <b>{val}</b>."]
    else:
        val, what = S * S // 2, "jumlah kuadrat minimum"
        steps = [f"Q(x) = x² + ({S} − x)².", f"Q′ = 2x − 2({S} − x) = 0 ⇒ x = {S // 2}.", f"Q = 2·{S // 2}² = <b>{val}</b>."]
    return {"prompt": f"Dua bilangan positif berjumlah {S}. Tentukan {what}nya.", "correct": n(val),
            "distractors": [n(S * S), n(S // 2), n(val + S), n(val // 2)], "steps": steps,
            "graphs": [g2d("Fungsi yang dioptimalkan", [0, S], [0, S * S], [param("X", "x", 0, S, 0.5, S / 4, "x")],
                           [fn(f"x*({S}-x)" if tier == 1 else f"x*x+({S}-x)**2", "blue", "fungsi"),
                            pt("X", f"X*({S}-X)" if tier == 1 else f"X*X+({S}-X)**2")],
                           [readout("nilai", f"X*({S}-X)" if tier == 1 else f"X*X+({S}-X)**2", 2)], "Ekstrem terjadi saat kedua bilangan sama.")],
            "explanation": "Optimasi: buat fungsi satu variabel, turunkan, cari f′ = 0."}


@register("apl.opt_kotak", OP, (2, 3, 4))
def opt_kotak(rng, tier):
    k = rng.randint(1, 5)
    s = 6 * k
    V = 16 * k ** 3
    return {"prompt": f"Dari karton persegi bersisi {s} cm, keempat sudutnya dipotong persegi bersisi x lalu dilipat menjadi kotak tanpa tutup. "
                      "Tentukan volume maksimum kotak.",
            "correct": f"{V} cm³", "distractors": [f"{(s - 2 * (k + 1)) ** 2 * (k + 1)} cm³", f"{s ** 3 // 27} cm³", f"{4 * k ** 3} cm³", f"{V + s} cm³"],
            "steps": [f"V(x) = x({s} − 2x)², 0 &lt; x &lt; {s // 2}.", f"V′ = ({s} − 2x)({s} − 6x) = 0 ⇒ x = {k} (x = {s // 2} membuat V = 0).",
                      f"V({k}) = {k}·{s - 2 * k}² = <b>{V} cm³</b>."],
            "graphs": [g2d("Volume kotak V(x)", [0, s / 2], [0, V * 1.3], [param("X", "Potongan x", 0, s / 2, 0.05, k / 2, "x")],
                           [fn(f"x*({s}-2*x)**2", "blue", "V(x)"), pt("X", f"X*({s}-2*X)**2")], [readout("V", f"X*({s}-2*X)**2", 2)],
                           f"Maksimum di x = s/6 = {k}.")],
            "explanation": "Soal optimasi klasik Stewart §4.7."}


@register("apl.lhopital", OP, (1, 2, 3, 4, 5))
def lhopital(rng, tier):
    a = nz(rng, -4, 4)
    if tier == 1:
        val, prompt = Fr(a), f"Hitung lim<sub>x→0</sub> (e<sup>{n(a)}x</sup> − 1)/x dengan aturan L'Hôpital."
        steps = ["Bentuk 0/0 ⇒ turunkan pembilang dan penyebut.", f"lim {n(a)}e<sup>{n(a)}x</sup>/1 = <b>{n(a)}</b>."]
    elif tier == 2:
        val, prompt = Fr(a), f"Hitung lim<sub>x→0</sub> ln(1 + {n(a)}x)/x."
        steps = ["0/0 ⇒ L'Hôpital.", f"lim [{n(a)}/(1 + {n(a)}x)]/1 = <b>{n(a)}</b>."]
    elif tier == 3:
        m = rng.randint(2, 4)
        val, prompt = Fr(0), f"Hitung lim<sub>x→∞</sub> x{sup(m)}/e<sup>x</sup>."
        steps = [f"∞/∞ ⇒ L'Hôpital {m} kali: {m}!/eˣ.", "eˣ tumbuh lebih cepat dari polinom ⇒ <b>0</b>."]
    elif tier == 4:
        val, prompt = Fr(a * a, 2), f"Hitung lim<sub>x→0</sub> (e<sup>{n(a)}x</sup> − 1 − {n(a)}x)/x²."
        steps = ["0/0 ⇒ L'Hôpital: ({n}e^{{ax}} − {n})/(2x), masih 0/0.".format(n=n(a)), f"L'Hôpital lagi: {n(a * a)}e<sup>{n(a)}x</sup>/2 → <b>{n(val)}</b>."]
    else:
        val, prompt = Fr(-a ** 3, 6), f"Hitung lim<sub>x→0</sub> (sin({n(a)}x) − {n(a)}x)/x³."
        steps = ["0/0 ⇒ L'Hôpital tiga kali.", f"−{n(a ** 3)}cos({n(a)}x)/6 → <b>{n(val)}</b>."]
    return {"prompt": prompt, "correct": n(val), "distractors": [n(-val) if val else "1", n(val + 1), "∞", n(val * 2) if val else "−1"], "steps": steps,
            "explanation": "L'Hôpital: untuk 0/0 atau ∞/∞, lim f/g = lim f′/g′ (bila ada)."}


@register("apl.tnr", OP, (3, 4))
def tnr(rng, tier):
    if tier == 3:
        p, q = nz(rng, -3, 3), rng.randint(-5, 5)
        a, b = sorted(distinct(rng, -4, 6, 2))
        c = Fr(a + b, 2)
        prompt = f"Tentukan c yang memenuhi Teorema Nilai Rata-rata untuk f(x) = {poly([p, q, 0])} pada [{n(a)}, {n(b)}]."
        steps = [f"[f(b) − f(a)]/(b − a) = {n(p)}(a + b) + {paren(q)} = {n(p * (a + b) + q)}.", f"f′(c) = {n(2 * p)}c + {paren(q)} = {n(p * (a + b) + q)}.",
                 f"c = <b>{n(c)}</b> (titik tengah — sifat khusus parabola)."]
        correct, wrong = f"c = {n(c)}", [f"c = {n(Fr(b - a, 2))}", f"c = {n(a)}", f"c = {n(b)}", f"c = {n(c + 1)}"]
    else:
        k = rng.choice([1, 2])
        b = 3 * k
        correct = f"c = {'' if k == 1 else k}√3"
        prompt = f"Tentukan c ∈ (0, {b}) yang memenuhi Teorema Nilai Rata-rata untuk f(x) = x³ pada [0, {b}]."
        steps = [f"[f({b}) − f(0)]/{b} = {b ** 3}/{b} = {b * b}.", f"f′(c) = 3c² = {b * b} ⇒ c² = {3 * k * k}.", f"<b>{correct}</b>."]
        wrong = [f"c = {b // 2 if b % 2 == 0 else n(Fr(b, 2))}", f"c = {'' if k == 1 else k}√2", f"c = {3 * k * k}", f"c = {b}"]
    return {"prompt": prompt, "correct": correct, "distractors": wrong, "steps": steps,
            "explanation": "TNR: ada c di (a, b) dengan f′(c) = [f(b) − f(a)]/(b − a) (Whitman §6.5)."}


@register("apl.opt_jarak", OP, (4, 5))
def opt_jarak(rng, tier):
    s = rng.randint(1, 4)
    a = Fr(4 * s * s + 1, 4)   # a − 1/4 = s²
    return {"prompt": f"Tentukan jarak terpendek dari titik (0, {n(a)}) ke parabola y = x².", "correct": n(s),
            "distractors": [n(a), n(Fr(s * s)), n(s + 1), n(Fr(1, 2))],
            "steps": [f"D² = x² + (x² − {n(a)})². Misal u = x² ≥ 0: D² = u + (u − {n(a)})².",
                      f"d(D²)/du = 1 + 2(u − {n(a)}) = 0 ⇒ u = {n(a - Fr(1, 2))}.",
                      f"D² = {n(a - Fr(1, 2))} + 1/4 = {s * s} ⇒ D = <b>{s}</b>."],
            "graphs": [g2d("Jarak titik ke parabola", [-5, 5], [-1, float(a) + 3], [param("X", "x", -4, 4, 0.01, 1, "x")],
                           [fn("x*x", "blue", "y = x²"), pt(0, float(a), "orange"), {"type": "segment", "x1": 0, "y1": float(a), "x2": "X", "y2": "X*X", "color": "red", "dash": True}],
                           [readout("Jarak", f"sqrt(X*X+(X*X-{float(a)})**2)", 4)], "Geser x untuk mencari jarak terkecil.")],
            "explanation": "Minimalkan kuadrat jarak (lebih mudah dari jaraknya)."}
