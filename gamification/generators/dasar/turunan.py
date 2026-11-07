"""
Sub-level: Turunan / Diferensial (Level Utama 2 — Kalkulus Dasar).
Rujukan: Stewart §2.7–2.8, §3.1–3.6; Whitman Bab 2–4; Strang (MIT) Bab 2 & 4.
"""

from fractions import Fraction as Fr
import math

from .. import register
from ..fmt import MINUS, lin, n, paren, poly, sup
from ..graphs import fn, g2d, param, pt, readout
from ...content.helpers import tangent_graph
from ..precalc.common import distinct, nz
from .limit import ev, js_poly, xm

DF, DS, PK, RT, TS = "kd-tur-definisi", "kd-tur-dasar", "kd-tur-perkalian", "kd-tur-rantai", "kd-tur-transenden"


def dpoly(co):
    """Koefisien turunan polinom."""
    deg = len(co) - 1
    return [c * (deg - i) for i, c in enumerate(co[:-1])] or [0]


def tg(expr, dexpr, a, x=(-5, 5), y=(-20, 20), caption=None):
    return tangent_graph("Grafik f dan garis singgung di x = a", expr, dexpr, "Titik singgung a", x[0], x[1], float(a),
                         list(x), list(y), caption=caption or "Geser a: kemiringan garis merah = f′(a). Bandingkan dengan nilai di tabel.")


# ════════════════════════ Topik 1: Definisi turunan ════════════════════════
@register("tur.sekan", DF, (1, 2))
def sekan(rng, tier):
    a, b, c = nz(rng, -3, 3), rng.randint(-5, 5), rng.randint(-5, 5)
    x1, x2 = sorted(distinct(rng, -3, 4, 2))
    co = [a, b, c]
    m = Fr(ev(co, x2) - ev(co, x1), x2 - x1)
    if tier == 1:
        prompt = f"Hitung laju perubahan rata-rata f(x) = {poly(co)} pada interval [{n(x1)}, {n(x2)}]."
    else:
        prompt = f"Berapa gradien garis sekan grafik f(x) = {poly(co)} yang melalui titik berabsis x = {n(x1)} dan x = {n(x2)}?"
    return {"prompt": prompt, "correct": n(m), "distractors": [n(2 * a * x1 + b), n(-m), n(ev(co, x2) - ev(co, x1)), n(m + 1)],
            "steps": ["Laju perubahan rata-rata = gradien sekan = [f(b) − f(a)]/(b − a).",
                      f"f({n(x2)}) = {n(ev(co, x2))}, f({n(x1)}) = {n(ev(co, x1))}.",
                      f"[{n(ev(co, x2))} − {paren(ev(co, x1))}]/({n(x2)} − {paren(x1)}) = <b>{n(m)}</b>."],
            "graphs": [g2d("Garis sekan menuju garis singgung", [-5, 6], [-25, 25],
                           [param("h", "Lebar h = b − a", 0.01, 4, 0.01, x2 - x1, "h")],
                           [fn(f"{a}*x*x+({b})*x+({c})", "blue", "f(x)"),
                            fn(f"({a}*({x1}+h)**2+({b})*({x1}+h)-{a}*{x1 * x1}-({b})*{x1})/h*(x-({x1}))+{ev(co, x1)}", "red", "sekan", dash=True),
                            pt(x1, ev(co, x1)), pt(f"{x1}+h", f"{a}*({x1}+h)**2+({b})*({x1}+h)+({c})", "orange")],
                           [readout("Gradien sekan", f"({a}*({x1}+h)**2+({b})*({x1}+h)-{a}*{x1 * x1}-({b})*{x1})/h", 4),
                            readout(f"f′({x1}) (h → 0)", str(2 * a * x1 + b), 4)],
                           "Kecilkan h: garis sekan berputar menjadi garis singgung — itulah definisi turunan.")],
            "explanation": "Turunan = limit gradien sekan saat lebar interval → 0."}


@register("tur.definisi", DF, (1, 2, 3))
def definisi(rng, tier):
    k = rng.randint(-3, 3)
    if tier <= 2:
        a, b, c = nz(rng, -3, 3), rng.randint(-5, 5), rng.randint(-5, 5)
        val = 2 * a * k + b
        prompt = f"Dengan definisi f′(x) = lim<sub>h→0</sub> [f(x + h) − f(x)]/h, hitung f′({n(k)}) untuk f(x) = {poly([a, b, c])}."
        steps = [f"f(x + h) − f(x) = {n(a)}[(x + h)² − x²] + {paren(b)}h = {n(a)}(2xh + h²) + {paren(b)}h.",
                 f"Bagi h: {n(2 * a)}x + {n(a)}h + {paren(b)} → (h → 0) f′(x) = {lin(2 * a, b)}.", f"f′({n(k)}) = <b>{n(val)}</b>."]
        graph = tg(f"{a}*x*x+({b})*x+({c})", f"{2 * a}*x+({b})", k)
    else:
        a = nz(rng, -6, 6)
        k = nz(rng, -3, 3)
        val = Fr(-a, k * k)
        prompt = f"Dengan definisi turunan, hitung f′({n(k)}) untuk f(x) = {n(a)}/x."
        steps = [f"f(x + h) − f(x) = {n(a)}/(x + h) − {n(a)}/x = −{paren(a)}h / (x(x + h)).",
                 f"Bagi h dan h → 0: f′(x) = −{paren(a)}/x².", f"f′({n(k)}) = <b>{n(val)}</b>."]
        graph = tg(f"{a}/x", f"-({a})/(x*x)", k, y=(-12, 12))
    return {"prompt": prompt, "correct": n(val), "distractors": [n(-val), n(val + 1), n(val * 2), "0"], "steps": steps, "graphs": [graph],
            "explanation": "f′(a) = lim [f(a + h) − f(a)]/h = kemiringan garis singgung di a."}


@register("tur.kenali", DF, (2, 3, 4, 5))
def kenali(rng, tier):
    if tier <= 3:
        c, m = rng.randint(1, 4), rng.randint(2, 5)
        val = m * c ** (m - 1)
        prompt = f"Hitung lim<sub>h→0</sub> [({c} + h){sup(m)} − {c ** m}] / h."
        steps = [f"Bentuk ini adalah definisi f′({c}) untuk f(x) = x{sup(m)}.", f"f′(x) = {m}x{sup(m - 1)} ⇒ f′({c}) = {m}·{c}{sup(m - 1)} = <b>{val}</b>."]
        correct = n(val)
        wrong = [n(c ** m), n(m * c ** m), "0", n(val + m)]
    elif tier == 4:
        k = rng.randint(1, 6)
        val = Fr(1, 2 * k)
        prompt = f"Hitung lim<sub>h→0</sub> [√({k * k} + h) − {k}] / h."
        steps = [f"Ini f′({k * k}) untuk f(x) = √x.", f"f′(x) = 1/(2√x) ⇒ f′({k * k}) = 1/{2 * k} = <b>{n(val)}</b>."]
        correct, wrong = n(val), [n(Fr(1, k)), n(2 * k), "0", n(Fr(1, k * k))]
    else:
        from ..precalc.trigonometri import exact, rad_text
        deg = rng.choice([30, 45, 60, 120, 150])
        val = exact("cos", deg)
        prompt = f"Hitung lim<sub>h→0</sub> [sin({rad_text(deg)} + h) − sin({rad_text(deg)})] / h."
        steps = ["Ini definisi turunan sin x di x = a.", f"(sin x)′ = cos x ⇒ cos({rad_text(deg)}) = <b>{val}</b>."]
        correct, wrong = val, [exact("sin", deg), "0", "1", f"{MINUS}{val}" if not val.startswith(MINUS) else val[1:]]
    return {"prompt": prompt, "correct": correct, "distractors": wrong, "steps": steps,
            "explanation": "Kenali pola lim [f(a + h) − f(a)]/h sebagai f′(a) — tidak perlu menghitung limit dari nol."}


@register("tur.terdiferensial", DF, (4, 5))
def terdiferensial(rng, tier):
    c = nz(rng, -3, 3)
    if tier == 4:
        a, b = 2 * c, -c * c
        correct = f"a = {n(a)}, b = {n(b)}"
        return {"prompt": f"f(x) = x² untuk x ≤ {n(c)} dan f(x) = ax + b untuk x &gt; {n(c)}. Tentukan a, b agar f terdiferensialkan di x = {n(c)}.",
                "correct": correct, "distractors": [f"a = {n(c)}, b = {n(c * c - c * c)}", f"a = {n(a)}, b = {n(-b)}", f"a = {n(b)}, b = {n(a)}", f"a = {n(2 * c + 1)}, b = {n(b - c)}"],
                "steps": [f"Kontinu: a·{paren(c)} + b = {c * c}.", f"Turunan kiri = turunan kanan: 2·{paren(c)} = a ⇒ a = {n(a)}.",
                          f"b = {c * c} − {n(a)}·{paren(c)} = {n(b)}. Jawaban: <b>{correct}</b>. (Garis ax + b adalah garis singgung x² di c.)"],
                "graphs": [tg("x*x", "2*x", c, caption="Potongan kanan harus berimpit dengan garis singgung merah agar tidak ada ‘sudut’.")],
                "explanation": "Terdiferensialkan ⇒ kontinu dan turunan kiri = turunan kanan."}
    m = rng.randint(1, 4)
    return {"prompt": f"Di titik mana f(x) = |{m}x − {m * c}| + {m}x² <b>tidak</b> terdiferensialkan?".replace("− −", "+ "),
            "correct": f"x = {n(c)}", "distractors": ["x = 0", f"x = {n(-c)}", "terdiferensialkan di semua x", f"x = {n(m * c)}"],
            "steps": [f"{m}x² mulus di mana-mana; |{m}(x − {paren(c)})| membentuk sudut di x = {n(c)}.",
                      f"Turunan kiri dan kanan di x = {n(c)} berbeda {2 * m} satuan.", f"Jawaban: <b>x = {n(c)}</b>."],
            "graphs": [g2d("Sudut pada grafik", [c - 3, c + 3], [-2, 30], [], [fn(f"abs({m}*x-({m * c}))+{m}*x*x", "blue", "f")], None,
                           "Perbesar di sekitar titik sudut: grafik tidak pernah tampak seperti garis lurus.")],
            "explanation": "|x − c| tidak terdiferensialkan di c (sudut)."}


# ════════════════════════ Topik 2: Aturan pangkat, konstanta, jumlah ════════
@register("tur.rumus_poly", DS, (1, 2))
def rumus_poly(rng, tier):
    co = [nz(rng, -4, 4), rng.randint(-6, 6), rng.randint(-9, 9), rng.randint(-9, 9)]
    if tier == 2:
        co = [nz(rng, -3, 3), 0] + co[1:]
    d = dpoly(co)
    correct = f"f′(x) = {poly(d)}"
    deg = len(co) - 1
    wrong = [f"f′(x) = {poly([c * (deg - i + 1) for i, c in enumerate(co[:-1])])}", f"f′(x) = {poly(d[:-1] + [d[-1] + co[-1]])}",
             f"f′(x) = {poly([c for c in co[:-1]])}", f"f′(x) = {poly([-c for c in d])}"]
    return {"prompt": f"Tentukan turunan f(x) = {poly(co)}.", "correct": correct, "distractors": wrong,
            "steps": ["Aturan pangkat: (xⁿ)′ = n·xⁿ⁻¹; konstanta diturunkan menjadi 0; turunan jumlah = jumlah turunan.",
                      "Kalikan setiap koefisien dengan pangkatnya, lalu kurangi pangkat dengan 1.", f"<b>{correct}</b>."],
            "graphs": [tg(js_poly(co), js_poly(d), 1, x=(-4, 4), y=(-40, 40))],
            "explanation": "d/dx (axⁿ) = naxⁿ⁻¹."}


@register("tur.pangkat", DS, (1, 2, 3))
def pangkat(rng, tier):
    k = rng.randint(1, 3)
    if tier == 1:
        co = [nz(rng, -3, 3), rng.randint(-5, 5), rng.randint(-5, 5), rng.randint(-5, 5)]
        val = ev(dpoly(co), k)
        f = poly(co)
        steps = [f"f′(x) = {poly(dpoly(co))}.", f"f′({k}) = <b>{n(val)}</b>."]
        expr, dexpr = js_poly(co), js_poly(dpoly(co))
    elif tier == 2:
        a, b = nz(rng, -4, 4), nz(rng, -6, 6)
        m = rng.randint(1, 3)
        val = Fr(a * 3 * k * k) - Fr(b * m, k ** (m + 1))
        f = f"{n(a)}x³ + {n(b)}/x{sup(m) if m > 1 else ''}".replace("+ −", "− ")
        steps = [f"Tulis {n(b)}/x{sup(m) if m > 1 else ''} = {n(b)}x{sup(-m)}.", f"f′(x) = {n(3 * a)}x² − {n(b * m)}x{sup(-m - 1)}.",
                 f"f′({k}) = {n(3 * a * k * k)} − {n(Fr(b * m, k ** (m + 1)))} = <b>{n(val)}</b>."]
        expr, dexpr = f"{a}*x**3+({b})/x**{m}", f"{3 * a}*x*x-({b * m})/x**{m + 1}"
    else:
        a, b = nz(rng, -6, 6), nz(rng, -4, 4)
        s = rng.randint(1, 3)
        k = s * s
        val = Fr(a, 2 * s) + Fr(3 * b, 2) * s
        f = f"{n(a)}√x + {n(b)}x√x".replace("+ −", "− ")
        steps = [f"√x = x<sup>1/2</sup>, x√x = x<sup>3/2</sup>.", f"f′(x) = {n(a)}/(2√x) + {n(Fr(3 * b, 2))}√x.",
                 f"f′({k}) = {n(a)}/{2 * s} + {n(Fr(3 * b, 2))}·{s} = <b>{n(val)}</b>."]
        expr, dexpr = f"{a}*sqrt(x)+({b})*x*sqrt(x)", f"{a}/(2*sqrt(x))+{1.5 * b}*sqrt(x)"
    return {"prompt": f"Diketahui f(x) = {f}. Hitung f′({k}).", "correct": n(val), "distractors": [n(val + 1), n(-val), n(val * 2), n(val - 3)],
            "steps": steps, "graphs": [tg(expr, dexpr, k, x=(0.1 if tier == 3 else -4, 6), y=(-40, 40))],
            "explanation": "Ubah akar dan pecahan menjadi pangkat (xᵖ), lalu pakai aturan pangkat."}


@register("tur.tingkat_tinggi", DS, (2, 3, 4, 5))
def tingkat_tinggi(rng, tier):
    if tier == 5:
        nn = rng.randint(4, 9)
        target = nn * (nn - 1)
        return {"prompt": f"Untuk f(x) = xⁿ (n bilangan asli), diketahui f″(1) = {target}. Tentukan n.", "correct": f"n = {nn}",
                "distractors": [f"n = {nn - 1}", f"n = {nn + 1}", f"n = {target // 2}", f"n = {int(target ** 0.5)}"],
                "steps": ["f′(x) = nxⁿ⁻¹, f″(x) = n(n − 1)xⁿ⁻².", f"f″(1) = n(n − 1) = {target}.", f"n² − n − {target} = 0 ⇒ <b>n = {nn}</b> (akar positif)."],
                "explanation": "Turunan kedua = turunan dari turunan pertama."}
    co = [nz(rng, -3, 3), rng.randint(-5, 5), rng.randint(-6, 6), rng.randint(-6, 6), rng.randint(-6, 6)]
    k = rng.randint(-2, 2)
    order = 2 if tier <= 3 else 3
    d = co
    for _ in range(order):
        d = dpoly(d)
    val = ev(d, k)
    mark = "″" if order == 2 else "‴"
    return {"prompt": f"Diketahui f(x) = {poly(co)}. Hitung f{mark}({n(k)}).", "correct": n(val),
            "distractors": [n(ev(dpoly(co), k)), n(val + 2), n(-val), n(ev(dpoly(dpoly(dpoly(co))) if order == 2 else dpoly(dpoly(co)), k))],
            "steps": [f"f′(x) = {poly(dpoly(co))}.", f"f″(x) = {poly(dpoly(dpoly(co)))}."]
                     + ([f"f‴(x) = {poly(dpoly(dpoly(dpoly(co))))}."] if order == 3 else []) + [f"f{mark}({n(k)}) = <b>{n(val)}</b>."],
            "explanation": "f″ menyatakan kecekungan; dalam fisika, turunan kedua posisi = percepatan."}


@register("tur.turunan_ke_n", DS, (4, 5))
def turunan_ke_n(rng, tier):
    nn = rng.randint(4, 8)
    m = rng.randint(2, nn - 1) if tier == 4 else nn
    val = math.factorial(nn) // math.factorial(nn - m)
    return {"prompt": f"Untuk f(x) = x{sup(nn)}, hitung f<sup>({m})</sup>(1)" + (" (turunan ke-n dengan n = pangkatnya)." if m == nn else "."),
            "correct": n(val), "distractors": [n(nn * m), n(nn ** m), n(val // nn if val // nn else 1), n(math.factorial(m))],
            "steps": [f"Setiap penurunan menurunkan pangkat 1 dan mengalikan dengan pangkat lama.",
                      f"f<sup>({m})</sup>(x) = {nn}·{nn - 1}·…·{nn - m + 1}·x{sup(nn - m)}.", f"Di x = 1: {nn}!/{nn - m}! = <b>{val}</b>."],
            "explanation": "dᵐ/dxᵐ xⁿ = n!/(n − m)! · xⁿ⁻ᵐ; turunan ke-n dari xⁿ adalah n!."}


# ════════════════════════ Topik 3: Perkalian & pembagian ═══════════════════
@register("tur.kali_rumus", PK, (1, 2))
def kali_rumus(rng, tier):
    m = rng.randint(1, 3)
    a, b = nz(rng, -4, 4), nz(rng, -6, 6)
    # f = x^m (ax + b) = a x^{m+1} + b x^m
    full = [a, b] + [0] * m
    d = dpoly(full)
    correct = f"f′(x) = {poly(d)}"
    return {"prompt": f"Tentukan turunan f(x) = x{sup(m) if m > 1 else ''}({lin(a, b)}) dengan aturan perkalian.",
            "correct": correct, "distractors": [f"f′(x) = {m}x{sup(m - 1) if m > 2 else ''}·{n(a)}".replace("x⁰", ""), f"f′(x) = {poly([a * m, 0] + [0] * (m - 1))}",
                                                f"f′(x) = {poly([a * (m + 1), b] + [0] * (m - 1))}", f"f′(x) = {poly([-c for c in d])}"],
            "steps": ["(uv)′ = u′v + uv′ dengan u = xᵐ, v = ax + b.", f"u′v + uv′ = {m}x{sup(m - 1)}({lin(a, b)}) + x{sup(m)}·{n(a)}.",
                      f"Sederhanakan: <b>{correct}</b>. (Cek: ekspansi dulu lalu turunkan memberi hasil sama.)"],
            "explanation": "Turunan hasil kali BUKAN hasil kali turunan: (uv)′ = u′v + uv′."}


@register("tur.perkalian", PK, (1, 2, 3))
def perkalian(rng, tier):
    a, b, c, d = nz(rng, -3, 3), rng.randint(-4, 4), nz(rng, -3, 3), rng.randint(-5, 5)
    k = rng.randint(-2, 2)
    u, du = a * k + b, a
    v, dv = c * k * k + d, 2 * c * k
    val = du * v + u * dv
    return {"prompt": f"f(x) = ({lin(a, b)})({poly([c, 0, d])}). Hitung f′({n(k)}).", "correct": n(val),
            "distractors": [n(du * dv), n(du * v - u * dv), n(val + 1), n(u * v)],
            "steps": [f"u = {lin(a, b)}, u′ = {n(a)}; v = {poly([c, 0, d])}, v′ = {lin(2 * c, 0)}.",
                      f"Di x = {n(k)}: u = {n(u)}, u′ = {n(du)}, v = {n(v)}, v′ = {n(dv)}.",
                      f"f′ = u′v + uv′ = {n(du)}·{paren(v)} + {n(u)}·{paren(dv)} = <b>{n(val)}</b>."],
            "graphs": [tg(f"({a}*x+({b}))*({c}*x*x+({d}))", f"{a}*({c}*x*x+({d}))+({a}*x+({b}))*{2 * c}*x", k, x=(-4, 4), y=(-40, 40))],
            "explanation": "(uv)′ = u′v + uv′."}


@register("tur.pembagian", PK, (2, 3, 4, 5))
def pembagian(rng, tier):
    k = rng.randint(-2, 2)
    if tier <= 4:
        a, b, c, d = nz(rng, -4, 4), rng.randint(-5, 5), nz(rng, -3, 3), rng.randint(-5, 5)
        while a * d - b * c == 0 or c * k + d == 0:
            d += 1
        val = Fr(a * d - b * c, (c * k + d) ** 2)
        prompt = f"f(x) = ({lin(a, b)}) / ({lin(c, d)}). Hitung f′({n(k)})."
        steps = ["(u/v)′ = (u′v − uv′)/v².", f"u′v − uv′ = {n(a)}({lin(c, d)}) − ({lin(a, b)})·{n(c)} = {n(a * d - b * c)} (konstan!).",
                 f"f′({n(k)}) = {n(a * d - b * c)}/{paren(c * k + d)}² = <b>{n(val)}</b>."]
        expr, dexpr = f"({a}*x+({b}))/({c}*x+({d}))", f"({a * d - b * c})/({c}*x+({d}))**2"
    else:
        p, q = distinct(rng, 1, 9, 2)
        val = Fr(2 * k * (q - p), (k * k + q) ** 2)
        prompt = f"f(x) = (x² + {p}) / (x² + {q}). Hitung f′({n(k)})."
        steps = ["u′v − uv′ = 2x(x² + q) − (x² + p)·2x = 2x(q − p).", f"f′(x) = 2x({q} − {p})/(x² + {q})².", f"f′({n(k)}) = <b>{n(val)}</b>."]
        expr, dexpr = f"(x*x+{p})/(x*x+{q})", f"2*x*({q}-{p})/(x*x+{q})**2"
    return {"prompt": prompt, "correct": n(val), "distractors": [n(-val), n(val * 2), n(val + 1), "0" if val else "1"], "steps": steps,
            "graphs": [tg(expr, dexpr, k, x=(-5, 5), y=(-8, 8))], "explanation": "Aturan pembagian: (u/v)′ = (u′v − uv′)/v²."}


@register("tur.kali_tabel", PK, (3, 4, 5))
def kali_tabel(rng, tier):
    g, dg, h, dh = nz(rng, -5, 5), rng.randint(-4, 4), nz(rng, -5, 5), rng.randint(-4, 4)
    if tier == 3:
        what, val = "(g·h)′(2)", Fr(dg * h + g * dh)
        st = f"g′h + gh′ = {n(dg)}·{paren(h)} + {n(g)}·{paren(dh)}"
    elif tier == 4:
        what, val = "(g/h)′(2)", Fr(dg * h - g * dh, h * h)
        st = f"(g′h − gh′)/h² = ({n(dg)}·{paren(h)} − {n(g)}·{paren(dh)})/{h * h}"
    else:
        what, val = "(g²·h)′(2)", Fr(2 * g * dg * h + g * g * dh)
        st = f"2gg′h + g²h′ = 2·{paren(g)}·{paren(dg)}·{paren(h)} + {g * g}·{paren(dh)}"
    return {"prompt": f"Diketahui g(2) = {n(g)}, g′(2) = {n(dg)}, h(2) = {n(h)}, h′(2) = {n(dh)}. Hitung {what}.",
            "correct": n(val), "distractors": [n(dg * dh), n(-val), n(val + 1), n(g * h)],
            "steps": ["Gunakan aturan perkalian/pembagian dengan nilai-nilai di x = 2.", f"{st} = <b>{n(val)}</b>."],
            "explanation": "Aturan turunan bekerja dengan nilai numerik — tidak perlu rumus fungsi lengkap."}


# ════════════════════════ Topik 4: Aturan rantai ═══════════════════════════
@register("tur.rantai_rumus", RT, (1, 2))
def rantai_rumus(rng, tier):
    a, b = nz(rng, -5, 5, (0, 1)), nz(rng, -6, 6)
    m = rng.randint(2, 7)
    inner = lin(a, b)
    correct = f"{n(m * a)}({inner}){sup(m - 1) if m > 2 else ''}"
    return {"prompt": f"Tentukan turunan f(x) = ({inner}){sup(m)}.", "correct": correct,
            "distractors": [f"{m}({inner}){sup(m - 1) if m > 2 else ''}", f"{n(a)}({inner}){sup(m - 1) if m > 2 else ''}", f"{n(m * a)}({inner}){sup(m)}",
                            f"{n(m * a)}x{sup(m - 1) if m > 2 else ''}"],
            "steps": [f"Luar: u{sup(m)} → {m}u{sup(m - 1)}; dalam: u = {inner} → u′ = {n(a)}.",
                      f"Aturan rantai: f′ = {m}({inner}){sup(m - 1)}·{n(a)} = <b>{correct}</b>."],
            "explanation": "(f(g(x)))′ = f′(g(x))·g′(x): turunan luar × turunan dalam."}


@register("tur.rantai_pangkat", RT, (1, 2, 3))
def rantai_pangkat(rng, tier):
    m = rng.randint(2, 5)
    k = rng.randint(-1, 2)
    if tier <= 2:
        a, b = nz(rng, -3, 3), rng.randint(-3, 3)
        u, du = a * k + b, a
        inner, expr = lin(a, b), f"({a}*x+({b}))"
    else:
        a, b = nz(rng, -2, 2), rng.randint(-3, 3)
        u, du = a * k * k + b, 2 * a * k
        inner, expr = poly([a, 0, b]), f"({a}*x*x+({b}))"
    val = m * u ** (m - 1) * du
    return {"prompt": f"f(x) = ({inner}){sup(m)}. Hitung f′({n(k)}).", "correct": n(val),
            "distractors": [n(m * u ** (m - 1)), n(val * 2), n(u ** m), n(-val) if val else "1"],
            "steps": [f"f′(x) = {m}({inner}){sup(m - 1)}·({'(' + inner + ')′' })", f"Di x = {n(k)}: dalam = {n(u)}, turunan dalam = {n(du)}.",
                      f"f′({n(k)}) = {m}·{paren(u)}{sup(m - 1)}·{paren(du)} = <b>{n(val)}</b>."],
            "graphs": [tg(f"{expr}**{m}", f"{m}*{expr}**{m - 1}*({'%d' % a if tier <= 2 else '%d*x' % (2 * a)})", k, x=(-3, 3), y=(-30, 30))],
            "explanation": "U-D3 (berkas soal dasar) adalah contoh klasik: (2x + 1)⁵."}


@register("tur.rantai_akar", RT, (2, 3))
def rantai_akar(rng, tier):
    for _ in range(100):
        a, b, k = rng.randint(1, 4), rng.randint(-5, 9), rng.randint(1, 4)
        s2 = a * k * k + b
        s = int(round(s2 ** 0.5)) if s2 > 0 else 0
        if s > 0 and s * s == s2:
            break
    else:
        a, b, k, s = 1, 0, 3, 3
    val = Fr(a * k, s)
    return {"prompt": f"f(x) = √({poly([a, 0, b])}). Hitung f′({k}).", "correct": n(val),
            "distractors": [n(Fr(1, 2 * s)), n(Fr(2 * a * k, s)), n(Fr(a * k, s * s)), n(val + 1)],
            "steps": ["f = u<sup>1/2</sup> ⇒ f′ = u′/(2√u).", f"u = {poly([a, 0, b])}, u′ = {n(2 * a)}x.",
                      f"f′({k}) = {2 * a * k}/(2·√{s2}) = {2 * a * k}/{2 * s} = <b>{n(val)}</b>."],
            "graphs": [tg(f"sqrt({a}*x*x+({b}))", f"{a}*x/sqrt({a}*x*x+({b}))", k, x=(0, 6), y=(0, 15))],
            "explanation": "d/dx √u = u′/(2√u)."}


@register("tur.rantai_tabel", RT, (3, 4, 5))
def rantai_tabel(rng, tier):
    g2, dg2 = rng.randint(-3, 4), nz(rng, -4, 4)
    fg, dfg = rng.randint(-5, 5), nz(rng, -4, 4)
    if tier <= 4:
        val = dfg * dg2
        prompt = (f"Diketahui g(2) = {n(g2)}, g′(2) = {n(dg2)}, f({n(g2)}) = {n(fg)}, f′({n(g2)}) = {n(dfg)}. "
                  "Jika h(x) = f(g(x)), hitung h′(2).")
        steps = ["h′(x) = f′(g(x))·g′(x).", f"h′(2) = f′(g(2))·g′(2) = f′({n(g2)})·{paren(dg2)} = {n(dfg)}·{paren(dg2)} = <b>{n(val)}</b>."]
    else:
        dk = nz(rng, -3, 3)
        val = dfg * dg2 * dk
        prompt = (f"Diketahui k(1) = 2, k′(1) = {n(dk)}, g(2) = {n(g2)}, g′(2) = {n(dg2)}, f′({n(g2)}) = {n(dfg)}. "
                  "Jika H(x) = f(g(k(x))), hitung H′(1).")
        steps = ["Rantai tiga lapis: H′(x) = f′(g(k(x)))·g′(k(x))·k′(x).",
                 f"H′(1) = f′(g(2))·g′(2)·k′(1) = {n(dfg)}·{paren(dg2)}·{paren(dk)} = <b>{n(val)}</b>."]
    return {"prompt": prompt, "correct": n(val), "distractors": [n(fg * dg2), n(dfg + dg2), n(-val) if val else "1", n(val + dg2)],
            "steps": steps, "explanation": "Turunan komposisi = perkalian turunan setiap lapis, dievaluasi di titik yang tepat."}


@register("tur.rantai_trig", RT, (4, 5))
def rantai_trig(rng, tier):
    a = rng.randint(1, 4)
    pt_txt = f"π/{4 * a}" if a > 1 else "π/4"
    if tier == 4:
        val = a
        prompt = f"f(x) = sin²({a if a > 1 else ''}x). Hitung f′({pt_txt})."
        steps = [f"f′(x) = 2 sin({a}x)·cos({a}x)·{a} = {a}·sin({2 * a}x).", f"Di x = {pt_txt}: {a}·sin(π/2) = <b>{a}</b>."]
        expr, dexpr = f"sin({a}*x)**2", f"{a}*sin({2 * a}*x)"
    else:
        val = -a
        prompt = f"f(x) = ln(cos({a if a > 1 else ''}x)). Hitung f′({pt_txt})."
        steps = [f"f′(x) = [−sin({a}x)·{a}]/cos({a}x) = −{a}·tan({a}x).", f"Di x = {pt_txt}: −{a}·tan(π/4) = <b>{-a}</b>."]
        expr, dexpr = f"log(cos({a}*x))", f"-{a}*tan({a}*x)"
    return {"prompt": prompt, "correct": n(val), "distractors": [n(-val), n(2 * a), "1", "0"], "steps": steps,
            "graphs": [tg(expr, dexpr, math.pi / (4 * a), x=(0, 1.5), y=(-3, 3))],
            "explanation": "Fungsi bersarang: turunkan dari lapis terluar ke dalam."}


# ════════════════════════ Topik 5: Trigonometri, eksponen, log & implisit ═
@register("tur.trig", TS, (1, 2, 3))
def trig(rng, tier):
    a, b, c, d = nz(rng, -5, 5), nz(rng, 1, 5), nz(rng, -5, 5), nz(rng, 1, 5)
    if tier <= 2:
        val = a * b
        prompt = f"f(x) = {n(a)} sin({b}x) + {n(c)} cos({d}x). Hitung f′(0).".replace("+ −", "− ")
        steps = ["(sin u)′ = cos u·u′ dan (cos u)′ = −sin u·u′.", f"f′(x) = {n(a * b)} cos({b}x) − {n(c * d)} sin({d}x).",
                 f"f′(0) = {n(a * b)}·1 − {n(c * d)}·0 = <b>{n(val)}</b>."]
        expr, dexpr = f"{a}*sin({b}*x)+({c})*cos({d}*x)", f"{a * b}*cos({b}*x)-({c * d})*sin({d}*x)"
    else:
        prompt = f"f(x) = {n(a)} tan({b}x) + x·cos x. Hitung f′(0)."
        val = a * b + 1
        steps = ["(tan u)′ = sec²u·u′; (x cos x)′ = cos x − x sin x.", f"f′(0) = {n(a)}·{b}·sec²0 + (cos 0 − 0) = {n(a * b)} + 1 = <b>{n(val)}</b>."]
        expr, dexpr = f"{a}*tan({b}*x)+x*cos(x)", f"{a * b}/cos({b}*x)**2+cos(x)-x*sin(x)"
    return {"prompt": prompt, "correct": n(val), "distractors": [n(-val), n(c * d), "0", n(val + 1)], "steps": steps,
            "graphs": [tg(expr, dexpr, 0, x=(-1.5, 1.5), y=(-12, 12))], "explanation": "(sin x)′ = cos x, (cos x)′ = −sin x, (tan x)′ = sec²x."}


@register("tur.eksp_log", TS, (1, 2, 3))
def eksp_log(rng, tier):
    a = nz(rng, -4, 4)
    if tier == 1:
        val, prompt = Fr(a), f"f(x) = e<sup>{n(a)}x</sup>. Hitung f′(0)."
        steps = [f"(e<sup>u</sup>)′ = e<sup>u</sup>·u′ ⇒ f′(x) = {n(a)}e<sup>{n(a)}x</sup>.", f"f′(0) = {n(a)}·1 = <b>{n(a)}</b>."]
        expr, dexpr, k = f"exp({a}*x)", f"{a}*exp({a}*x)", 0
    elif tier == 2:
        k = rng.randint(0, 4)
        b = rng.randint(1, 9) + max(0, -a * k)   # pastikan ak + b > 0 (domain ln)
        val = Fr(a, a * k + b)
        prompt = f"f(x) = ln({lin(a, b)}). Hitung f′({k})."
        steps = ["(ln u)′ = u′/u.", f"f′(x) = {n(a)}/({lin(a, b)}).", f"f′({k}) = {n(a)}/{n(a * k + b)} = <b>{n(val)}</b>."]
        expr, dexpr = f"log({a}*x+({b}))", f"{a}/({a}*x+({b}))"
    else:
        m = rng.randint(1, 3)
        val = Fr(m + 1)
        prompt = f"f(x) = x ln x. Hitung f′(e)." if m == 1 else f"f(x) = x{sup(m)} ln x. Hitung f′(e)/e{sup(m - 1) if m > 2 else ''}."
        steps = [f"Aturan perkalian: f′ = {m}x{sup(m - 1) if m > 1 else '⁰'}·ln x + x{sup(m) if m > 1 else ''}·(1/x) = x{sup(m - 1) if m > 1 else '⁰'}({m} ln x + 1).",
                 f"Di x = e (ln e = 1): e{sup(m - 1) if m > 1 else '⁰'}·({m} + 1).", f"Jawaban: <b>{m + 1}</b>."]
        expr, dexpr, k = f"x**{m}*log(x)", f"x**{m - 1}*({m}*log(x)+1)", math.e
    return {"prompt": prompt, "correct": n(val), "distractors": [n(val + 1), n(-val), "1" if val != 1 else "e", n(val * 2)], "steps": steps,
            "graphs": [tg(expr, dexpr, k, x=(0.05 if tier >= 2 else -2, 6), y=(-6, 12))], "explanation": "(eˣ)′ = eˣ, (ln x)′ = 1/x (Strang §6.2–6.4)."}


@register("tur.implisit", TS, (3, 4, 5))
def implisit(rng, tier):
    if tier == 3:
        p, q, r = rng.choice([(3, 4, 5), (4, 3, 5), (5, 12, 13), (6, 8, 10), (8, 6, 10)])
        p *= rng.choice([1, -1])
        q *= rng.choice([1, -1])
        val = Fr(-p, q)
        prompt = f"Tentukan dy/dx pada lingkaran x² + y² = {r * r} di titik ({n(p)}, {n(q)})."
        steps = ["Turunkan kedua ruas terhadap x (y fungsi dari x): 2x + 2y·y′ = 0.", "y′ = −x/y.", f"Di ({n(p)}, {n(q)}): y′ = <b>{n(val)}</b>."]
        graph = g2d("Garis singgung lingkaran", [-r - 3, r + 3], [-r - 3, r + 3], [param("t0", "Sudut titik (rad)", 0, 6.28, 0.01, round(math.atan2(q, p) % (2 * math.pi), 2), "θ")],
                    [{"type": "param", "t": [0, "2*pi"], "x": f"{r}*cos(t)", "y": f"{r}*sin(t)", "color": "blue"},
                     pt(f"{r}*cos(t0)", f"{r}*sin(t0)"), fn(f"{r}*sin(t0)-cos(t0)/sin(t0)*(x-{r}*cos(t0))", "red", "singgung", dash=True)],
                    [readout("y′ = −x/y", "-cos(t0)/sin(t0)", 4)], "Garis singgung selalu tegak lurus jari-jari.")
    elif tier == 4:
        x0, y0 = nz(rng, -3, 3), nz(rng, -3, 3)
        while x0 + 2 * y0 == 0:
            y0 += 1
        c = x0 * x0 + x0 * y0 + y0 * y0
        val = Fr(-(2 * x0 + y0), x0 + 2 * y0)
        prompt = f"Kurva x² + xy + y² = {c}. Tentukan dy/dx di titik ({n(x0)}, {n(y0)})."
        steps = ["Turunkan: 2x + (y + x·y′) + 2y·y′ = 0.", "y′(x + 2y) = −(2x + y) ⇒ y′ = −(2x + y)/(x + 2y).",
                 f"Di ({n(x0)}, {n(y0)}): y′ = −({n(2 * x0 + y0)})/({n(x0 + 2 * y0)}) = <b>{n(val)}</b>."]
        graph = None
    else:
        x0, y0 = nz(rng, 1, 3), nz(rng, 1, 3)
        c = x0 * y0 * y0 + x0 * x0 * y0
        val = Fr(-(y0 * y0 + 2 * x0 * y0), 2 * x0 * y0 + x0 * x0)
        prompt = f"Kurva xy² + x²y = {c}. Tentukan dy/dx di titik ({x0}, {y0})."
        steps = ["Turunkan: (y² + 2xy·y′) + (2xy + x²y′) = 0.", "y′(2xy + x²) = −(y² + 2xy).",
                 f"Di ({x0}, {y0}): y′ = −{y0 * y0 + 2 * x0 * y0}/{2 * x0 * y0 + x0 * x0} = <b>{n(val)}</b>."]
        graph = None
    return {"prompt": prompt, "correct": n(val), "distractors": [n(-val), n(Fr(1) / val) if val else "1", n(val + 1), "0" if val else "−1"],
            "steps": steps, "graphs": [graph] if graph else [], "explanation": "Turunan implisit: turunkan kedua ruas, ingat (y²)′ = 2y·y′."}


@register("tur.invers", TS, (4, 5))
def tur_invers(rng, tier):
    p, q = rng.randint(1, 5), rng.randint(-5, 5)
    a = rng.randint(-2, 2) if tier == 4 else rng.randint(1, 3)
    b = a ** 3 + p * a + q
    val = Fr(1, 3 * a * a + p)
    return {"prompt": f"f(x) = x³ + {p}x {'+' if q >= 0 else MINUS} {abs(q)} memiliki invers g. Hitung g′({n(b)}).",
            "correct": n(val), "distractors": [n(3 * a * a + p), n(Fr(1, 3 * b * b + p)), n(-val), n(Fr(1, p))],
            "steps": [f"Cari a dengan f(a) = {n(b)}: a = {n(a)}.", f"f′(x) = 3x² + {p} ⇒ f′({n(a)}) = {3 * a * a + p}.",
                      f"g′({n(b)}) = 1/f′({n(a)}) = <b>{n(val)}</b> (Strang §4.3)."],
            "graphs": [g2d("Gradien invers = kebalikan gradien f", [-6, 10], [-6, 10], [],
                           [fn(f"x**3+{p}*x+({q})", "blue", "f"), fn("x", "gray", dash=True)], None,
                           "Grafik g adalah cerminan f terhadap y = x; kemiringan saling berkebalikan.")],
            "explanation": "(f⁻¹)′(b) = 1/f′(a) dengan f(a) = b."}
