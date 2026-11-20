"""
Sub-level: Teknik Pengintegralan (Level Utama 3 — Kalkulus Menengah).
Rujukan: Stewart §7.1–7.4, §7.8; Whitman §8.2–8.5; Strang (MIT) Bab 7.
"""

from fractions import Fraction as Fr
import math

from .. import register
from ..fmt import MINUS, fac, frac_terms, lin, n, over, paren, poly, sup, terms, times
from ..graphs import fn, g2d, hline, param, readout
from ..precalc.common import distinct, nz
from ..dasar.aplikasi import pi_txt

PS, TG, PP, TW = "km-tek-parsial", "km-tek-trig", "km-tek-pecahan", "km-tek-takwajar"


def area(title, expr, a, b, caption, xr=None, yr=(-2, 4)):
    return g2d(title, xr or [a - 0.5, b + 0.5], list(yr), [param("bb", "Batas atas", a, b, 0.01, b, "b")],
               [{"type": "fill", "upper": expr, "from": a, "to": "bb", "color": "amber"}, fn(expr, "blue", "integran")], None, caption)


def xpow(k, var="x"):
    return var if k == 1 else f"{var}{sup(k)}"


def expx(a):
    """e^(ax) sebagai teks: eˣ, e⁻ˣ, e<sup>2x</sup>."""
    return "eˣ" if a == 1 else "e⁻ˣ" if a == -1 else f"e<sup>{n(a)}x</sup>"


def epow(k):
    return "e" if k == 1 else f"e{sup(k)}"


def lnax(a):
    return "ln x" if a == 1 else f"ln({a}x)"


def kx(k):
    return "x" if k == 1 else f"{k}x"


def _d(p):
    """Turunan polinom (koefisien dari pangkat rendah ke tinggi)."""
    return [i * c for i, c in enumerate(p)][1:]


def _ev(p, x):
    return sum(c * x ** i for i, c in enumerate(p))


def _ptxt(p):
    """Polinom (rendah → tinggi) sebagai teks, dibungkus kurung bila lebih dari satu suku."""
    s = poly(list(reversed(p)))
    return s if sum(1 for c in p if c) == 1 else f"({s})"


def tabel_exp(p, a, b):
    """
    ∫₀ᵇ P(x)e^{ax} dx = e^{ab}·S(b) − S(0), S = Σ (−1)ⁱ P⁽ⁱ⁾/a^{i+1} (metode tabel).
    Mengembalikan (koefisien e^{ab}, konstanta).
    """
    a = Fr(a)
    S, q, i = [], list(map(Fr, p)), 0
    while q:
        S.append([(-1) ** i * c / a ** (i + 1) for c in q])
        q, i = _d(q), i + 1
    tot = [sum(col) for col in zip(*[r + [0] * (len(p) - len(r)) for r in S])]
    return _ev(tot, b), -_ev(tot, 0)


def tabel_trig(p, k, f):
    """
    ∫₀^π P(x)·f(kx) dx (f = sin/cos) dengan metode tabel; hasil = polinom dalam π (rendah → tinggi).
    sin: [−cos(kx)·C + sin(kx)·D]₀^π,  cos: [sin(kx)·C + cos(kx)·D]₀^π,
    C = Σ (−1)ⁱ P⁽²ⁱ⁾/k^{2i+1}, D = Σ (−1)ⁱ P⁽²ⁱ⁺¹⁾/k^{2i+2}.
    """
    deg = len(p)
    C, D = [Fr(0)] * deg, [Fr(0)] * deg
    q, j = list(map(Fr, p)), 0
    while q:
        tgt, sgn, pw = (C, (-1) ** (j // 2), j + 1) if j % 2 == 0 else (D, (-1) ** (j // 2), j + 1)
        for i, c in enumerate(q):
            tgt[i] += sgn * c / Fr(k) ** pw
        q, j = _d(q), j + 1
    s = (-1) ** k   # cos(kπ); sin(kπ) = 0
    if f == "sin":
        out = [-s * c for c in C]
        out[0] += C[0]
    else:
        out = [s * c for c in D]
        out[0] -= D[0]
    return out


def pi_poly(coefs):
    """Polinom dalam π (rendah → tinggi) → teks dengan penyebut bersama."""
    monos = ["", "π", "π²", "π³", "π⁴"]
    return over([(c, monos[i]) for i, c in enumerate(coefs) if i > 0][::-1], coefs[0])


def wrong_e(ce, E, c0):
    """Pengecoh untuk jawaban ce·E + c0: selalu ada ≥ 3 yang berbeda dari jawaban benar."""
    return [over([(ce, E)], -c0), over([(ce + 1, E)], c0), over([(ce, E)], c0 + 1), over([(-ce, E)], c0), over([(ce * 2, E)], c0)]


def wrong_pi(val):
    return [pi_poly([-c for c in val]), pi_poly([val[0] + 1] + val[1:]), pi_poly([val[0] - 1] + val[1:]), pi_poly([c * 2 for c in val])]


def _rand_poly(rng, deg, lead=1):
    """Polinom derajat `deg` (rendah → tinggi), koefisien kecil, koefisien utama `lead`."""
    return [rng.randint(-3, 3) for _ in range(deg)] + [lead]


# ════════════════════════ Topik 1: Integral parsial ═══════════════════════
@register("tp.pilih_u", PS, (1, 2))
def pilih_u(rng, tier):
    m, a = rng.randint(1, 4), rng.randint(2, 5)
    xm = xpow(m)
    kind = rng.choice(["exp", "ln", "sin", "cos", "atan"] if tier == 2 else ["exp", "ln", "sin", "cos"])
    other = {"exp": f"e<sup>{a}x</sup>", "ln": f"ln({a}x)", "sin": f"sin({a}x)", "cos": f"cos({a}x)", "atan": f"arctan({a}x)"}[kind]
    f = f"{xm}·{other}"
    if kind in ("ln", "atan"):
        u, dv, why = other, f"{xm} dx", f"{'Logaritma' if kind == 'ln' else 'Invers trig'} berada di depan Aljabar pada LIATE; turunannya ({'1/x' if kind == 'ln' else f'{a}/(1 + {a * a}x²)'}) jauh lebih sederhana."
    else:
        u, dv, why = xm, f"{other} dx", f"Aljabar berada di depan {'Eksponen' if kind == 'exp' else 'Trigonometri'}; menurunkan {xm} berulang kali membuatnya habis menjadi konstanta."
    good = f"u = {u}, dv = {dv}"
    wrong = [f"u = {dv[:-3]}, dv = {u} dx", f"u = 1, dv = {f} dx", f"u = {f}, dv = dx", f"u = {xm}·{u if u != xm else other}, dv = dx"]
    return {"prompt": f"Pada ∫ {f} dx dengan integral parsial, pilihan u dan dv yang paling tepat adalah …", "correct": good, "distractors": wrong,
            "steps": ["Rumus: ∫ u dv = uv − ∫ v du.", "Urutan LIATE (Logaritma, Invers trig, Aljabar, Trigonometri, Eksponen): pilih u dari yang paling depan.",
                      why, f"<b>{good}</b>."],
            "explanation": "Integral parsial adalah kebalikan aturan perkalian: (uv)′ = u′v + uv′."}


@register("tp.xeax", PS, (1, 2, 3))
def xeax(rng, tier):
    if tier == 1:
        a, c = nz(rng, -5, 5), rng.randint(1, 4)
        cx = f"{c}x" if c > 1 else "x"
        correct = f"{expx(a)}({frac_terms([(Fr(c, a), 'x')], Fr(-c, a * a))}) + C"
        prompt = f"Tentukan ∫ {cx}·{expx(a)} dx."
        steps = [f"u = {cx}, dv = {expx(a)} dx ⇒ du = {c if c > 1 else ''}dx, v = {expx(a)}/{paren(a)}.",
                 f"∫ = {cx}·{expx(a)}/{paren(a)} − ∫ {c if c > 1 else ''}{expx(a)}/{paren(a)} dx.", f"= <b>{correct}</b>."]
        wrong = [f"{expx(a)}({frac_terms([(Fr(c, a), 'x')], Fr(c, a * a))}) + C", f"{frac_terms([(Fr(c, 2), 'x²')])}·{expx(a)} + C",
                 f"{expx(a)}({frac_terms([(c, 'x')], -c)}) + C", f"{expx(a)}({frac_terms([(Fr(c * a), 'x')], Fr(-c, a * a))}) + C"]
        return {"prompt": prompt, "correct": correct, "distractors": wrong, "steps": steps, "explanation": "∫ u dv = uv − ∫ v du."}
    if tier == 2:
        a, c, f = rng.randint(1, 6), rng.randint(1, 4), rng.choice(["sin", "cos"])
        cx = f"{c}x" if c > 1 else "x"
        if f == "cos":
            correct = frac_terms([(Fr(c, a), f"x·sin({kx(a)})"), (Fr(c, a * a), f"cos({kx(a)})")]) + " + C"
            wrong = [frac_terms([(Fr(c, a), f"x·sin({kx(a)})"), (Fr(-c, a * a), f"cos({kx(a)})")]) + " + C",
                     frac_terms([(Fr(-c, a), f"x·sin({kx(a)})"), (Fr(c, a * a), f"cos({kx(a)})")]) + " + C",
                     frac_terms([(Fr(c, 2), f"x²·sin({kx(a)})")]) + " + C", frac_terms([(Fr(c * a), f"x·sin({kx(a)})"), (Fr(c), f"cos({kx(a)})")]) + " + C"]
            v = f"sin({kx(a)})/{a}" if a > 1 else f"sin x"
        else:
            correct = frac_terms([(Fr(-c, a), f"x·cos({kx(a)})"), (Fr(c, a * a), f"sin({kx(a)})")]) + " + C"
            wrong = [frac_terms([(Fr(c, a), f"x·cos({kx(a)})"), (Fr(c, a * a), f"sin({kx(a)})")]) + " + C",
                     frac_terms([(Fr(-c, a), f"x·cos({kx(a)})"), (Fr(-c, a * a), f"sin({kx(a)})")]) + " + C",
                     frac_terms([(Fr(-c, 2), f"x²·cos({kx(a)})")]) + " + C", frac_terms([(Fr(-c * a), f"x·cos({kx(a)})"), (Fr(c), f"sin({kx(a)})")]) + " + C"]
            v = f"−cos({kx(a)})/{a}" if a > 1 else "−cos x"
        prompt = f"Tentukan ∫ {cx}·{f}({kx(a)}) dx."
        steps = [f"u = {cx}, dv = {f}({kx(a)}) dx ⇒ v = {v}.", "∫ = uv − ∫ v du, lalu integralkan sekali lagi.", f"<b>{correct}</b>."]
        return {"prompt": prompt, "correct": correct, "distractors": wrong, "steps": steps, "explanation": "∫ u dv = uv − ∫ v du."}
    # tier 3: integral tentu dengan P(x) linear
    p = [rng.randint(-2, 3), rng.randint(1, 3)]
    if rng.random() < 0.5:
        a, b = rng.choice([1, -1, 2, -2]), rng.choice([1, 2])
        ce, c0 = tabel_exp(p, a, b)
        correct = over([(ce, epow(a * b))], c0)
        prompt = f"Hitung ∫<sub>0</sub><sup>{b}</sup> {_ptxt(p)}·{expx(a)} dx."
        steps = [f"u = {poly(p[::-1])}, dv = {expx(a)} dx ⇒ v = {expx(a)}/{paren(a)}.",
                 f"Antiturunan: {expx(a)}·[{frac_terms([(Fr(p[1], a), 'x')], Fr(p[0], a) - Fr(p[1], a * a))}].",
                 f"Evaluasi di {b} dan 0: <b>{correct}</b>."]
        wrong = wrong_e(ce, epow(a * b), c0)
    else:
        k, f = rng.randint(1, 3), rng.choice(["sin", "cos"])
        val = tabel_trig(p, k, f)
        correct = pi_poly(val)
        prompt = f"Hitung ∫<sub>0</sub><sup>π</sup> {_ptxt(p)}·{f}({kx(k)}) dx."
        steps = [f"u = {poly(p[::-1])}, dv = {f}({kx(k)}) dx; integral parsial sekali (u′ konstan).",
                 f"Gunakan cos({k}π) = {(-1) ** k} dan sin({k}π) = 0 saat evaluasi.", f"<b>{correct}</b>."]
        wrong = wrong_pi(val)
    return {"prompt": prompt, "correct": correct, "distractors": wrong, "steps": steps, "explanation": "∫ₐᵇ u dv = [uv]ₐᵇ − ∫ₐᵇ v du."}


@register("tp.lnx", PS, (1, 2, 3, 4, 5))
def lnx(rng, tier):
    m, c = rng.randint(0, 2 if tier == 1 else 5), rng.randint(1, 5)
    k = m + 1
    cxm = (f"{c}" if c > 1 else "") + ("" if m == 0 else xpow(m))
    if tier <= 2:
        a = rng.randint(1, 4)
        correct = frac_terms([(Fr(c, k), f"{xpow(k)} {lnax(a)}"), (Fr(-c, k * k), xpow(k))]) + " + C"
        prompt = f"Tentukan ∫ {cxm + '·' if cxm else ''}{lnax(a)} dx."
        steps = [f"u = {lnax(a)}, dv = {cxm or '1'} dx ⇒ du = dx/x (konstanta {a} hilang saat diturunkan: ln({a}x) = ln {a} + ln x), v = {frac_terms([(Fr(c, k), xpow(k))])}.",
                 f"∫ = {frac_terms([(Fr(c, k), f'{xpow(k)} {lnax(a)}')])} − ∫ {frac_terms([(Fr(c, k), xpow(m) if m else '')])} dx.", f"= <b>{correct}</b>."]
        wrong = [frac_terms([(Fr(c, k), f"{xpow(k)} {lnax(a)}"), (Fr(c, k * k), xpow(k))]) + " + C",
                 frac_terms([(Fr(c, k), f"{xpow(k)} {lnax(a)}")]) + " + C",
                 frac_terms([(Fr(c, k), f"{xpow(k)} {lnax(a)}"), (Fr(-c * a, k * k), xpow(k))]) + " + C",
                 frac_terms([(Fr(c, 2), f"{xpow(m) + ' ' if m else ''}({lnax(a)})²")]) + " + C"]
        return {"prompt": prompt, "correct": correct, "distractors": wrong, "steps": steps, "explanation": "ln x hampir selalu dipilih sebagai u."}
    j = rng.randint(1, 2)
    up = "e" if j == 1 else "e²"
    if tier <= 4:
        # ∫₁^{e^j} c·x^m ln x dx = c[(jk − 1)e^{jk} + 1]/k²
        ce, c0 = Fr(c * (j * k - 1), k * k), Fr(c, k * k)
        correct = over([(ce, epow(j * k))], c0)
        prompt = f"Hitung ∫<sub>1</sub><sup>{up}</sup> {cxm + '·' if cxm else ''}ln x dx."
        steps = [f"u = ln x, dv = {cxm or '1'} dx ⇒ antiturunan {frac_terms([(Fr(c, k), xpow(k) + ' ln x'), (Fr(-c, k * k), xpow(k))])}.",
                 f"Di x = {up}: ln x = {j}; di x = 1: ln x = 0.", f"Selisih: <b>{correct}</b>."]
        wrong = [over([(Fr(c, k), epow(j * k))])] + wrong_e(ce, epow(j * k), c0)
    else:
        # ∫₁^{e^j} c·x^m (ln x)² dx = c[(j²k² − 2jk + 2)e^{jk} − 2]/k³
        ce, c0 = Fr(c * (j * j * k * k - 2 * j * k + 2), k ** 3), Fr(-2 * c, k ** 3)
        correct = over([(ce, epow(j * k))], c0)
        prompt = f"Hitung ∫<sub>1</sub><sup>{up}</sup> {cxm + '·' if cxm else ''}(ln x)² dx."
        steps = ["Parsial dua kali: u = (ln x)² lalu u = ln x (dv = pangkat x).",
                 f"Antiturunan: {xpow(k)}·[(ln x)²/{k} − 2 ln x/{k * k} + 2/{k ** 3}]{f' × {c}' if c > 1 else ''}.".replace("/1 ", " ").replace("/1]", "]"),
                 f"Di x = {up} (ln x = {j}) dikurangi di x = 1 (ln x = 0): <b>{correct}</b>."]
        wrong = [over([(ce, epow(j * k))])] + wrong_e(ce, epow(j * k), c0)
    return {"prompt": prompt, "correct": correct, "distractors": wrong, "steps": steps, "explanation": "ln x hampir selalu dipilih sebagai u."}


@register("tp.berulang", PS, (3, 4, 5))
def berulang(rng, tier):
    if tier == 5 and rng.random() < 0.6:
        a, b, c = rng.randint(1, 5), rng.randint(1, 5), rng.randint(1, 3)
        f = rng.choice(["sin", "cos"])
        val = Fr(c * (b if f == "sin" else a), a * a + b * b)
        correct = n(val)
        prompt = f"Hitung ∫<sub>0</sub><sup>∞</sup> {c if c > 1 else ''}{expx(-a)}·{f}({kx(b)}) dx."
        steps = ["Parsial dua kali menghasilkan integral semula (siklik): I = (suku batas) − (b²/a²)·I.",
                 f"Selesaikan untuk I: ∫₀^∞ e<sup>−ax</sup>sin(bx) dx = b/(a² + b²), ∫₀^∞ e<sup>−ax</sup>cos(bx) dx = a/(a² + b²).",
                 f"a = {a}, b = {b}{f', dikali {c}' if c > 1 else ''}: <b>{correct}</b>."]
        wrong = [n(Fr(c * (a if f == "sin" else b), a * a + b * b)), n(Fr(c, a * a + b * b)), n(Fr(c * b, a) if f == "sin" else Fr(c * a, b)), n(val * 2)]
        return {"prompt": prompt, "correct": correct, "distractors": wrong, "steps": steps,
                "explanation": "Integral parsial berulang: metode tabel, atau ‘siklik’ untuk eᵃˣ·sin/cos."}
    deg = 2 if tier == 3 else rng.choice([2, 3])
    p = _rand_poly(rng, deg, lead=1 if tier == 3 else rng.choice([1, 1, 2, -1]))
    if tier == 3 or rng.random() < 0.4:
        a, b = rng.choice([1, -1, 2, -2] if tier == 3 else [1, -1, 2, -2, 3]), 1
        ce, c0 = tabel_exp(p, a, b)
        correct = over([(ce, epow(a))], c0)
        prompt = f"Hitung ∫<sub>0</sub><sup>1</sup> {_ptxt(p)}·{expx(a)} dx."
        steps = [f"Metode tabel: kolom D = {poly(p[::-1])} diturunkan sampai 0, kolom I = {expx(a)} diintegralkan berulang (setiap kali dibagi {paren(a)}).",
                 "Kalikan diagonal dengan tanda bergantian +, −, +, … .", f"Evaluasi pada [0, 1]: <b>{correct}</b>."]
        wrong = wrong_e(ce, epow(a), c0)
    else:
        k, f = rng.randint(1, 3), rng.choice(["sin", "cos"])
        val = tabel_trig(p, k, f)
        correct = pi_poly(val)
        prompt = f"Hitung ∫<sub>0</sub><sup>π</sup> {_ptxt(p)}·{f}({kx(k)}) dx."
        steps = [f"Metode tabel: kolom D = {poly(p[::-1])} diturunkan sampai 0, kolom I = {f}({kx(k)}) diintegralkan berulang.",
                 f"Kalikan diagonal dengan tanda +, −, +, …; lalu pakai sin({k}π) = 0 dan cos({k}π) = {(-1) ** k}.", f"<b>{correct}</b>."]
        wrong = wrong_pi(val)
    return {"prompt": prompt, "correct": correct, "distractors": wrong, "steps": steps,
            "explanation": "Integral parsial berulang: metode tabel, atau ‘siklik’ untuk eᵃˣ·sin/cos."}


# ════════════════════════ Topik 2: Integral trig & substitusi trig ═════════
def trigp(f, m, k):
    """sinᵐ(kx) sebagai teks."""
    if not m:
        return ""
    return f"{f}{sup(m) if m > 1 else ''}" + ((" x" if m == 1 else "x") if k == 1 else f"({k}x)")


def dfact(m):
    return math.prod(range(m, 0, -2)) if m > 0 else 1


def wallis(m, nn):
    """∫₀^{π/2} sinᵐx cosⁿx dx = (m−1)!!(n−1)!!/(m+n)!! × (π/2 bila m, n genap). Hasil (pecahan, pakai_π)."""
    v = Fr(dfact(m - 1) * dfact(nn - 1), dfact(m + nn))
    return (v / 2, True) if m % 2 == 0 and nn % 2 == 0 else (v, False)


def _prod(m, nn, k):
    parts = [trigp("sin", m, k), trigp("cos", nn, k)]
    return " ".join(p for p in parts if p)


@register("tt.pangkat_trig", TG, (1, 2, 3, 4))
def pangkat_trig(rng, tier):
    k = rng.randint(1, 4 if tier == 1 else 3)
    if tier == 1:
        odd, p, q = rng.choice(["sin", "cos"]), rng.randint(0, 2), rng.choice([0, 2, 4])   # pasangan genap: hanya satu cara substitusi
        if p == 0 and q == 0:
            p = 1
        other = "cos" if odd == "sin" else "sin"
        sgn = -1 if odd == "sin" else 1   # du = ∓k·(fungsi ganjil) dx
        pairs = [(Fr(sgn * math.comb(p, j) * (-1) ** j, k * (q + 2 * j + 1)), trigp(other, q + 2 * j + 1, k)) for j in range(p + 1)][::-1]
        correct = frac_terms(pairs) + " + C"
        body = "·".join([f"(1 − u²){sup(p) if p > 1 else ''}"] * (p > 0) + [xpow(q, "u")] * (q > 0)) or "1"
        f = trigp(odd, 2 * p + 1, k) + (" " + trigp(other, q, k) if q else "")
        prompt = f"Tentukan ∫ {f} dx."
        steps = [f"Pangkat {odd} ganjil: sisihkan satu faktor {odd}({kx(k)}) dan ubah sisanya dengan {odd}² = 1 − {other}².",
                 f"Substitusi u = {other}({kx(k)}), du = {'−' if sgn < 0 else ''}{k if k > 1 else ''}{odd}({kx(k)}) dx: ∫ {'−' if sgn < 0 else ''}{body} du{f'/{k}' if k > 1 else ''}.",
                 f"<b>{correct}</b>."]
        wrong = [frac_terms([(-c, mo) for c, mo in pairs]) + " + C", frac_terms([(c * k, mo) for c, mo in pairs]) + " + C" if k > 1 else frac_terms([(c * 2, mo) for c, mo in pairs]) + " + C",
                 frac_terms([(c, mo.replace(other, odd)) for c, mo in pairs]) + " + C", frac_terms(pairs[:1] if len(pairs) > 1 else [(pairs[0][0], trigp(other, q + 2, k))]) + " + C"]
        return {"prompt": prompt, "correct": correct, "distractors": wrong, "steps": steps,
                "explanation": "Pangkat ganjil: pisahkan satu faktor lalu substitusi. Pangkat genap: identitas setengah sudut / reduksi."}
    if tier == 2:
        m, nn = rng.choice([(m, q) for m in range(6) for q in range(6) if (m % 2 or q % 2) and m + q >= 2])
    elif tier == 3:
        m, nn = rng.choice([(m, 0) for m in (2, 4, 6, 8)] + [(0, q) for q in (2, 4, 6, 8)] + [(2, 2), (2, 4), (4, 2)])
    else:
        m, nn = rng.choice([(m, q) for m in range(0, 9) for q in range(0, 9) if m + q >= 5])
    c = rng.randint(1, 3)
    w, has_pi = wallis(m, nn)
    val = Fr(c, k) * w
    sym = "π" if has_pi else ""
    correct = times(val, sym) if has_pi else n(val)
    up = "π/2" if k == 1 else f"π/{2 * k}"
    prompt = f"Hitung ∫<sub>0</sub><sup>{up}</sup> {c if c > 1 else ''}{_prod(m, nn, k)} dx."
    steps = [f"Substitusi t = {k}x (bila k ≠ 1) mengubah batas menjadi [0, π/2] dan memberi faktor 1/{k}." if k > 1 else "Batas [0, π/2]: pakai rumus Wallis / reduksi.",
             f"Rumus Wallis: ∫₀^{{π/2}} sinᵐ cosⁿ = (m − 1)!!(n − 1)!!/(m + n)!!{' × π/2 (m, n keduanya genap)' if has_pi else ' (ada pangkat ganjil, tanpa π)'}; di sini m = {m}, n = {nn}.",
             f"Hasil: {c if c > 1 else ''}{'·' if c > 1 else ''}{times(w, sym) if has_pi else n(w)}{f'/{k}' if k > 1 else ''} = <b>{correct}</b>."]
    alt = (lambda v: times(v, sym) if has_pi else n(v))
    wrong = [alt(val * k) if k > 1 else alt(val * 2), n(val) if has_pi else times(val, "π"), alt(val / 2), alt(Fr(c, m + nn + 1))]
    return {"prompt": prompt, "correct": correct, "distractors": wrong, "steps": steps,
            "explanation": "Pangkat ganjil: pisahkan satu faktor lalu substitusi. Pangkat genap: identitas setengah sudut / reduksi (Wallis)."}


@register("tt.setengah_sudut", TG, (1, 2))
def setengah_sudut(rng, tier):
    k = rng.randint(1, 4)
    m = rng.randint(1, 3)
    f = rng.choice(["sin", "cos"])
    val = Fr(m, 2) if tier == 1 else Fr(m)
    upper = f"{'' if m == 1 else m}π" if tier == 1 else f"{2 * m}π" if m > 1 else "2π"
    return {"prompt": f"Hitung ∫<sub>0</sub><sup>{upper}</sup> {f}²({'' if k == 1 else k}x) dx.", "correct": pi_txt(val),
            "distractors": [pi_txt(val * 2), pi_txt(val / 2), n(val), pi_txt(val + 1)],
            "steps": [f"{f}²u = (1 {'−' if f == 'sin' else '+'} cos 2u)/2.", "Bagian cos(2kx) berintegral 0 pada kelipatan periode penuh.",
                      f"Sisa ∫ 1/2 dx = (panjang interval)/2 = <b>{pi_txt(val)}</b>."],
            "graphs": [g2d(f"{f}²(kx) berosilasi di sekitar 1/2", [0, 6.3], [-0.2, 1.2], [param("k", "k", 1, 4, 1, k, "k")],
                           [fn(f"{f}(k*x)**2", "blue", "f"), hline(0.5, "red")], None, "Rata-rata fungsi = 1/2, sehingga integral = setengah panjang interval.")],
            "explanation": "Identitas setengah sudut menurunkan pangkat genap."}


@register("tt.ortogonal", TG, (3, 4, 5))
def ortogonal(rng, tier):
    m, k = rng.randint(1, 5), rng.randint(1, 5)
    if tier == 5:
        correct, prompt = "0", f"Hitung ∫<sub>0</sub><sup>2π</sup> sin({m}x)·cos({k}x) dx."
        why = "sin(mx)cos(kx) = [sin((m + k)x) + sin((m − k)x)]/2; setiap suku sinus berintegral 0 pada [0, 2π]."
        wrong = ["π", "2π", "π/2", "1"]
    else:
        same = rng.random() < 0.5
        if same:
            k = m
        correct = "π" if m == k else "0"
        prompt = f"Hitung ∫<sub>0</sub><sup>2π</sup> sin({m}x)·sin({k}x) dx."
        why = "sin(mx)sin(kx) = [cos((m − k)x) − cos((m + k)x)]/2." + (" Untuk m = k, suku pertama = 1/2 ⇒ integral π." if m == k else " Kedua kosinus berintegral 0.")
        wrong = ["0" if correct == "π" else "π", "2π", "π/2", "1"]
    return {"prompt": prompt, "correct": correct, "distractors": wrong, "steps": [why, f"Jawaban: <b>{correct}</b>."],
            "explanation": "Ortogonalitas sinus–kosinus: dasar deret Fourier (analisis sinyal FT/Fasilkom)."}


@register("tt.substitusi_trig", TG, (3, 4, 5))
def substitusi_trig(rng, tier):
    a, c = rng.randint(1, 6), rng.randint(1, 4)
    C = "" if c == 1 else str(c)
    pool = {3: ["seperempat", "setengah", "arcsin", "arcsin6"], 4: ["arctan", "arctan_tak", "arctan_dua", "seperempat"], 5: ["x2", "x2akar", "kuadrat2", "pangkat32"]}[tier]
    kind = rng.choice(pool)
    sq = f"√({a * a} − x²)"
    if kind == "seperempat":
        val, sym, prompt = Fr(c * a * a, 4), "π", f"Hitung ∫<sub>0</sub><sup>{a}</sup> {C}{sq} dx."
        work = [f"x = {a} sin θ, dx = {a} cos θ dθ, {sq} = {a} cos θ; batas 0 → 0, {a} → π/2.", f"{C}∫₀^{{π/2}} {a * a} cos²θ dθ = {C}{'·' if c > 1 else ''}{a * a}·π/4 (seperempat lingkaran)."]
    elif kind == "setengah":
        val, sym, prompt = Fr(c * a * a, 2), "π", f"Hitung ∫<sub>−{a}</sub><sup>{a}</sup> {C}{sq} dx."
        work = [f"x = {a} sin θ: batas −π/2 → π/2.", f"{C}∫ {a * a} cos²θ dθ = {C}{'·' if c > 1 else ''}{a * a}·π/2 (setengah lingkaran)."]
    elif kind in ("arcsin", "arcsin6"):
        up, ang = (str(a), Fr(1, 2)) if kind == "arcsin" else ((f"{a}/2" if a % 2 else str(a // 2)), Fr(1, 6))
        val, sym, prompt = c * ang, "π", f"Hitung ∫<sub>0</sub><sup>{up}</sup> {C or '1'}/{sq} dx."
        work = [f"x = {a} sin θ ⇒ integran menjadi {C or '1'} dθ.", f"Batas θ: 0 → arcsin({'1' if kind == 'arcsin' else '1/2'}) = {times(ang, 'π')}."]
    elif kind == "arctan":
        val, sym, prompt = Fr(c, 4 * a), "π", f"Hitung ∫<sub>0</sub><sup>{a}</sup> {C or '1'}/(x² + {a * a}) dx."
        work = [f"x = {a} tan θ, dx = {a} sec²θ dθ, x² + {a * a} = {a * a} sec²θ.", f"∫ ({C or '1'}/{a}) dθ dari 0 sampai π/4."]
    elif kind == "arctan_tak":
        val, sym, prompt = Fr(c, 2 * a), "π", f"Hitung ∫<sub>0</sub><sup>∞</sup> {C or '1'}/(x² + {a * a}) dx."
        work = [f"x = {a} tan θ: integran ({C or '1'}/{a}) dθ.", "Batas θ: 0 → π/2 (x → ∞)."]
    elif kind == "arctan_dua":
        val, sym, prompt = Fr(c, 2 * a), "π", f"Hitung ∫<sub>−{a}</sub><sup>{a}</sup> {C or '1'}/(x² + {a * a}) dx."
        work = [f"x = {a} tan θ: integran ({C or '1'}/{a}) dθ.", "Batas θ: −π/4 → π/4."]
    elif kind == "x2":
        val, sym, prompt = Fr(c * a * a, 4), "π", f"Hitung ∫<sub>0</sub><sup>{a}</sup> {C}x²/{sq} dx."
        work = [f"x = {a} sin θ: integran {C}{'·' if c > 1 else ''}{a * a} sin²θ dθ, θ dari 0 ke π/2.", f"{C}{'·' if c > 1 else ''}{a * a}·π/4."]
    elif kind == "x2akar":
        val, sym, prompt = Fr(c * a ** 4, 16), "π", f"Hitung ∫<sub>0</sub><sup>{a}</sup> {C}x²{sq} dx."
        work = [f"x = {a} sin θ: integran {a ** 4} sin²θ cos²θ dθ = {a ** 4}·sin²(2θ)/4.", f"∫₀^{{π/2}} sin²(2θ) dθ = π/4 ⇒ {C}{'·' if c > 1 else ''}{a ** 4}·π/16."]
    elif kind == "kuadrat2":
        val, sym, prompt = Fr(c, 4 * a ** 3), "π", f"Hitung ∫<sub>0</sub><sup>∞</sup> {C or '1'}/(x² + {a * a})² dx."
        work = [f"x = {a} tan θ: integran ({C or '1'}/{a ** 3}) cos²θ dθ.", f"∫₀^{{π/2}} cos²θ dθ = π/4."]
    else:
        val, sym, prompt = Fr(c, a * a), "√2/2", f"Hitung ∫<sub>0</sub><sup>{a}</sup> {C or '1'}/(x² + {a * a})<sup>3/2</sup> dx."
        work = [f"x = {a} tan θ: integran ({C or '1'}/{a * a}) cos θ dθ, θ dari 0 ke π/4.", "∫₀^{π/4} cos θ dθ = sin(π/4) = √2/2."]
    correct = times(val, "π") if sym == "π" else times(val / 2, "√2")
    alt = (lambda v: times(v, "π")) if sym == "π" else (lambda v: times(v / 2, "√2"))
    return {"prompt": prompt, "correct": correct, "distractors": [alt(val * 2), alt(val / 2), n(val) if sym == "π" else times(val, "π"), alt(val * a) if a > 1 else alt(val * 3)],
            "steps": work + [f"= <b>{correct}</b>."],
            "explanation": "√(a² − x²): x = a sin θ; √(a² + x²) atau x² + a²: x = a tan θ; √(x² − a²): x = a sec θ."}


# ════════════════════════ Topik 3: Pecahan parsial ═════════════════════════
@register("pp.dekomposisi", PP, (1, 2))
def dekomposisi(rng, tier):
    a, b = distinct(rng, -5, 5, 2)
    p, q = (0, 1) if tier == 1 else (nz(rng, -3, 3), rng.randint(-4, 4))
    A, B = Fr(p * a + q, a - b), Fr(p * b + q, b - a)
    num = lin(p, q) if p else str(q)
    correct = f"A = {n(A)}, B = {n(B)}"
    return {"prompt": f"Tulis ({num})/({fac(a)}{fac(b)}) = A/{fac(a)} + B/{fac(b)}. Tentukan A dan B.",
            "correct": correct, "distractors": [f"A = {n(B)}, B = {n(A)}", f"A = {n(-A)}, B = {n(-B)}", f"A = {n(A + 1)}, B = {n(B)}", f"A = {n(q)}, B = {n(-q)}"],
            "steps": [f"Kalikan dengan penyebut: {num} = A(x − {paren(b)}) + B(x − {paren(a)}).",
                      f"x = {n(a)}: A = {n(p * a + q)}/{paren(a - b)} = {n(A)}.  x = {n(b)}: B = {n(p * b + q)}/{n(b - a)} = {n(B)}.", f"<b>{correct}</b>."],
            "explanation": "Metode ‘tutup’ (Heaviside): substitusi akar penyebut."}


@register("pp.dua_linear", PP, (1, 2, 3))
def dua_linear(rng, tier):
    a, b = distinct(rng, -4, 4, 2)
    p, q = nz(rng, -3, 3), rng.randint(-4, 4)
    A, B = Fr(p * a + q, a - b), Fr(p * b + q, b - a)
    if tier <= 2:
        correct = f"{n(A)} ln|x − {paren(a)}| + {n(B)} ln|x − {paren(b)}| + C".replace("+ −", "− ")
        prompt = f"Tentukan ∫ ({lin(p, q)})/({fac(a)}{fac(b)}) dx."
        wrong = [f"{n(B)} ln|x − {paren(a)}| + {n(A)} ln|x − {paren(b)}| + C".replace("+ −", "− "), f"ln|(x − {paren(a)})(x − {paren(b)})| + C",
                 f"{n(A)}/(x − {paren(a)}) + {n(B)}/(x − {paren(b)}) + C", f"{n(-A)} ln|x − {paren(a)}| + {n(-B)} ln|x − {paren(b)}| + C".replace("+ −", "− ")]
        steps = [f"Pecah: A = {n(A)}, B = {n(B)}.", "∫ dx/(x − c) = ln|x − c|.", f"<b>{correct}</b>."]
    else:
        k = rng.randint(1, 3)
        m = rng.randint(2, 4)
        ratio = Fr(m * (m + 1), (m + 2) * (m - 1))
        correct = f"(1/{2 * k}) ln({n(ratio)})"
        prompt = f"Hitung ∫<sub>{m * k}</sub><sup>{(m + 1) * k}</sup> dx/(x² − {k * k})."
        steps = [f"1/(x² − {k * k}) = (1/{2 * k})[1/(x − {k}) − 1/(x + {k})].", f"Antiturunan (1/{2 * k}) ln|(x − {k})/(x + {k})|.",
                 f"Selisih: (1/{2 * k})[ln({m}/{m + 2}) − ln({m - 1}/{m + 1})] = <b>{correct}</b>."]
        wrong = [f"(1/{k}) ln({n(ratio)})", f"(1/{2 * k}) ln({n(1 / ratio)})", f"ln({n(ratio)})", f"(1/{2 * k}) ln({m + 1})"]
    return {"prompt": prompt, "correct": correct, "distractors": wrong, "steps": steps,
            "explanation": "Pecahan parsial mengubah fungsi rasional menjadi jumlah suku ln dan arctan."}


@register("pp.berulang", PP, (2, 3, 4, 5))
def pp_berulang(rng, tier):
    a = nz(rng, -4, 4)
    c = rng.randint(-5, 5)
    s = a + c
    if tier <= 4:
        correct = f"ln|x − {paren(a)}| − {paren(s)}/(x − {paren(a)}) + C"
        prompt = f"Tentukan ∫ ({lin(1, c)})/{fac(a)}² dx."
        steps = [f"(x + {paren(c)})/(x − a)² = 1/(x − a) + {n(s)}/(x − a)² dengan a = {n(a)} (tulis x + c = (x − a) + (a + c)).",
                 "∫ 1/(x − a) dx = ln|x − a|; ∫ 1/(x − a)² dx = −1/(x − a).", f"<b>{correct}</b>."]
        wrong = [f"ln|x − {paren(a)}| + {paren(s)}/(x − {paren(a)}) + C", f"ln|x − {paren(a)}|² + C", f"{paren(s)} ln|x − {paren(a)}| + C",
                 f"−{paren(s)}/(x − {paren(a)}) + C"]
    else:
        val = Fr(s, 2)
        correct = f"ln 2 + {n(val)}".replace("+ −", "− ")
        prompt = f"Hitung ∫<sub>{n(a + 1)}</sub><sup>{n(a + 2)}</sup> ({lin(1, c)})/{fac(a)}² dx."
        steps = [f"Antiturunan ln|x − {paren(a)}| − {n(s)}/(x − {paren(a)}).", f"Di x = a + 2: ln 2 − {n(s)}/2; di x = a + 1: 0 − {n(s)}.",
                 f"Selisih: ln 2 + {n(s)}/2 = <b>{correct}</b>."]
        wrong = [f"ln 2 − {n(val)}", f"ln 2 + {n(s)}", f"{n(val)}", f"2 ln 2 + {n(val)}"]
    return {"prompt": prompt, "correct": correct, "distractors": wrong, "steps": steps, "explanation": "Faktor berulang (x − a)² butuh suku A/(x − a) + B/(x − a)²."}


@register("pp.kuadrat", PP, (3, 4, 5))
def pp_kuadrat(rng, tier):
    a = rng.randint(1, 6)
    if tier == 3:
        correct, prompt = f"(1/{a}) arctan(x/{a}) + C" if a > 1 else "arctan x + C", f"Tentukan ∫ dx/(x² + {a * a})."
        steps = [f"Bentuk baku ∫ dx/(x² + a²) = (1/a) arctan(x/a) + C, a = {a}.", f"<b>{correct}</b>."]
        wrong = [f"arctan(x/{a}) + C" if a > 1 else "arctan(x)/2 + C", f"ln(x² + {a * a}) + C", f"(1/{2 * a}) ln|(x − {a})/(x + {a})| + C", f"{a} arctan({a}x) + C"]
    elif tier == 4:
        b, c = rng.randint(-6, 6), rng.randint(1, 12)
        correct, prompt = f"ln|x² {'+' if b >= 0 else MINUS} {abs(b)}x + {c}| + C", f"Tentukan ∫ (2x {'+' if b >= 0 else MINUS} {abs(b)})/(x² {'+' if b >= 0 else MINUS} {abs(b)}x + {c}) dx."
        steps = ["Pembilang adalah turunan penyebut: ∫ u′/u dx = ln|u| + C.", f"<b>{correct}</b>."]
        wrong = ["arctan(x) + C", f"(x² + {paren(b)}x + {c})²/2 + C", f"1/(x² + {paren(b)}x + {c}) + C", f"2 ln|x| + C"]
    else:
        p, q = nz(rng, -4, 4), rng.randint(1, 4)
        correct, prompt = f"π/{4 * q}", f"Hitung ∫<sub>{n(-p)}</sub><sup>{n(-p + q)}</sup> dx/(x² {'+' if 2 * p >= 0 else MINUS} {abs(2 * p)}x + {p * p + q * q})."
        steps = [f"Lengkapkan kuadrat: x² + {2 * p}x + {p * p + q * q} = (x + {paren(p)})² + {q * q}.", f"u = x + {paren(p)}: ∫₀^{q} du/(u² + {q * q}) = (1/{q}) arctan(1).",
                 f"= <b>π/{4 * q}</b>."]
        wrong = [f"π/{2 * q}", "π/4", f"π/{4 * q * q}", f"{q}π/4"]
    return {"prompt": prompt, "correct": correct, "distractors": wrong, "steps": steps, "explanation": "Faktor kuadrat tak tereduksi → arctan (setelah melengkapkan kuadrat)."}


# ════════════════════════ Topik 4: Integral tak wajar ══════════════════════
@register("tw.p_integral", TW, (1, 2, 3))
def p_integral(rng, tier):
    c = rng.randint(1, 5)
    if tier == 1:
        p, b = Fr(rng.randint(2, 5)), rng.randint(1, 4)
    elif tier == 2:
        p, b = rng.choice([Fr(3, 2), Fr(5, 2), Fr(4, 3), Fr(1, 2), Fr(1), Fr(2), Fr(3)]), 1
        if p.denominator == 1 and p > 1:
            b = rng.randint(1, 3)
    else:
        p, b = rng.choice([Fr(1), Fr(1, 2), Fr(3, 2), Fr(5, 4), Fr(2, 3), Fr(4, 3)]), 1
    conv = p > 1
    val = c * Fr(b) ** (1 - p) / (p - 1) if conv else None
    correct = n(val) if conv else "divergen"
    ptxt = n(p)
    C = "" if c == 1 else str(c)
    return {"prompt": f"Hitung ∫<sub>{b}</sub><sup>∞</sup> {C or '1'}/x<sup>{ptxt}</sup> dx (atau nyatakan divergen).", "correct": correct,
            "distractors": [n(c / p), "divergen" if conv else n(c), "0", n(Fr(c, p + 1)), n(val * 2) if conv else n(Fr(c, 2))],
            "steps": ["∫ᵇᵗ x⁻ᵖ dx = (t¹⁻ᵖ − b¹⁻ᵖ)/(1 − p) untuk p ≠ 1, dan ln(t/b) untuk p = 1; lalu t → ∞.",
                      f"p = {ptxt} &gt; 1 ⇒ t¹⁻ᵖ → 0, nilai = {C}{'·' if c > 1 else ''}{b}<sup>{n(1 - p)}</sup>/({ptxt} − 1)." if conv else f"p = {ptxt} ≤ 1 ⇒ t¹⁻ᵖ (atau ln t) → ∞.",
                      f"Jawaban: <b>{correct}</b>."],
            "graphs": [g2d("Luas di bawah 1/xᵖ sampai t", [0.8, 30], [0, 1.5], [param("t", "Batas atas t", 1, 30, 0.1, 10, "t"), param("pp", "p", 0.5, 3, 0.05, float(p), "p")],
                           [{"type": "fill", "upper": "pow(x,-pp)", "from": 1, "to": "t", "color": "amber"}, fn("pow(x,-pp)", "blue", "1/xᵖ")],
                           [readout("∫₁ᵗ", "pp==1?log(t):(pow(t,1-pp)-1)/(1-pp)", 4)], "Untuk p > 1 luas mendekati batas; untuk p ≤ 1 terus membesar.")],
            "explanation": "Uji-p integral: ∫^∞ 1/xᵖ konvergen ⇔ p > 1 (dipakai lagi di uji integral deret)."}


@register("tw.eksponen", TW, (1, 2, 3, 5))
def tw_eksponen(rng, tier):
    a, b = rng.randint(1, 9), rng.randint(1, 5)
    if tier <= 2:
        s = 0 if tier == 1 else rng.randint(0, 2)
        val = Fr(a, b)
        pre = "" if s == 0 else f"e{sup(-b * s)}·"
        correct = n(val) if s == 0 else over([(val, f"e{sup(-b * s)}")])
        prompt = f"Hitung ∫<sub>{s}</sub><sup>∞</sup> {a}e<sup>−{b if b > 1 else ''}x</sup> dx."
        steps = [f"∫ₛᵗ = ({a}/{b})(e<sup>−{b}s</sup> − e<sup>−{b}t</sup>) dengan s = {s}.", f"t → ∞: <b>{correct}</b>."]
        wrong = [over([(val * 2, pre[:-1] or "")]) if s else n(val * 2), "divergen", n(Fr(a * b)), "0", n(val + 1)]
    else:
        m = rng.randint(1, 2) if tier == 3 else rng.randint(2, 6)
        b = rng.randint(1, 5) if tier == 3 else rng.randint(1, 2)
        c = rng.randint(1, 4)
        val = Fr(c * math.factorial(m), b ** (m + 1))
        correct = n(val)
        prompt = f"Hitung ∫<sub>0</sub><sup>∞</sup> {c if c > 1 else ''}x{sup(m) if m > 1 else ''}e<sup>−{b if b > 1 else ''}x</sup> dx."
        steps = [f"Iₘ = ∫₀^∞ xᵐe<sup>−bx</sup> dx; parsial memberi Iₘ = (m/b)·Iₘ₋₁ dengan I₀ = 1/b (suku batas → 0 karena eksponen mengalahkan polinom).",
                 f"Iₘ = m!/b<sup>m+1</sup> ⇒ {c if c > 1 else ''}{'·' if c > 1 else ''}{m}!/{b}{sup(m + 1)} = <b>{correct}</b>."]
        wrong = [n(Fr(c * math.factorial(m), b ** m)), "divergen", n(val * 2), n(c * math.factorial(m))]
    return {"prompt": prompt, "correct": correct, "distractors": wrong, "steps": steps,
            "explanation": "Integral tak wajar = limit integral biasa saat batas → ∞."}


@register("tw.tak_terbatas", TW, (2, 3, 4))
def tak_terbatas(rng, tier):
    c = rng.randint(1, 4)
    C = "" if c == 1 else str(c)
    if tier == 2:
        kind = rng.choice(["akar", "kubik", "geser"])
        s = rng.randint(1, 6)
        if kind == "akar":
            val, prompt = Fr(2 * c * s), f"Hitung ∫<sub>0</sub><sup>{s * s}</sup> {C or '1'}/√x dx."
            work = f"∫ₛ x<sup>−1/2</sup> dx = 2√x; s → 0⁺: 2·{s}{'·' + C if C else ''}."
        elif kind == "kubik":
            val, prompt = Fr(3 * c * s * s, 2), f"Hitung ∫<sub>0</sub><sup>{s ** 3}</sup> {C or '1'}/∛x dx."
            work = f"∫ x<sup>−1/3</sup> dx = (3/2)x<sup>2/3</sup>; di {s ** 3}: (3/2)·{s * s}{'·' + C if C else ''}."
        else:
            a = rng.randint(1, 5)
            val, prompt = Fr(2 * c * s), f"Hitung ∫<sub>{a}</sub><sup>{a + s * s}</sup> {C or '1'}/√(x − {a}) dx."
            work = f"Integran tak terbatas di x = {a}; ∫ (x − {a})<sup>−1/2</sup> dx = 2√(x − {a}) ⇒ 2·{s}{'·' + C if C else ''}."
        correct, wrong = n(val), [n(val / 2), "divergen", n(val * 2), n(val + c)]
        steps = [work, f"<b>{correct}</b>."]
    else:
        kind = rng.choice(["pangkat", "pangkat", "ln"]) if tier == 4 else "pangkat"
        if kind == "pangkat":
            p = rng.choice([Fr(1, 2), Fr(1, 3), Fr(2, 3), Fr(1), Fr(2), Fr(3, 2)]) if tier == 4 else rng.choice([Fr(1, 2), Fr(1, 3), Fr(3, 4), Fr(2, 3)])
            conv = p < 1
            q = 1 - p
            base = rng.randint(1, 3)
            b = Fr(base) ** p.denominator if conv else 1        # b^(1−p) bulat
            val = c * Fr(base) ** (q.numerator) / q if conv else None
            correct = n(val) if conv else "divergen"
            prompt = f"Hitung ∫<sub>0</sub><sup>{n(b)}</sup> {C or '1'}/x<sup>{n(p)}</sup> dx (atau nyatakan divergen)."
            steps = ["Masalah di x = 0. ∫ₛᵇ x⁻ᵖ dx = (b¹⁻ᵖ − s¹⁻ᵖ)/(1 − p) untuk p ≠ 1.",
                     f"p = {n(p)} &lt; 1 ⇒ s¹⁻ᵖ → 0: {C}{'·' if c > 1 else ''}{n(b)}<sup>{n(q)}</sup>/{n(q)}." if conv else "p ≥ 1 ⇒ divergen (kebalikan kasus ∞).", f"<b>{correct}</b>."]
            wrong = [n(c / p) if conv else n(c), "divergen" if conv else n(Fr(c, 2)), "0", n(val * 2) if conv else "1"]
        else:
            m = rng.randint(0, 4)
            val = Fr(-c, (m + 1) ** 2)
            correct = n(val)
            prompt = f"Hitung ∫<sub>0</sub><sup>1</sup> {C}{'x' if m == 1 else f'x{sup(m)}' if m else ''}{'·' if (m or C) else ''}ln x dx."
            steps = [f"Parsial: u = ln x, dv = x{sup(m) if m > 1 else '' if m else '⁰'} dx ⇒ antiturunan x{sup(m + 1) if m else ''} ln x/{m + 1} − x{sup(m + 1) if m else ''}/{(m + 1) ** 2}.".replace("x⁰", "1").replace("/1 ", " "),
                     f"Batas bawah: x<sup>{m + 1}</sup> ln x → 0 saat x → 0⁺ (L'Hôpital).", f"Hasil {C}{'·' if c > 1 else ''}(−1/{(m + 1) ** 2}) = <b>{correct}</b>."]
            wrong = [n(-val), "divergen", n(Fr(-c, m + 1)), n(val * 2)]
    return {"prompt": prompt, "correct": correct, "distractors": wrong, "steps": steps, "explanation": "Integran tak terbatas di ujung: ambil limit dari dalam interval."}


@register("tw.banding", TW, (4, 5))
def tw_banding(rng, tier):
    if tier == 4:
        k, m = rng.randint(1, 9), rng.randint(2, 4)
        cases = [(f"∫<sub>1</sub><sup>∞</sup> dx/(x{sup(m)} + {k})", "konvergen", f"1/(x{sup(m)} + {k}) ≤ 1/x{sup(m)} dan p = {m} &gt; 1."),
                 (f"∫<sub>1</sub><sup>∞</sup> dx/√(x + {k})", "divergen", f"1/√(x + {k}) ≥ 1/√({k + 1}x) ~ 1/x<sup>1/2</sup>, p = 1/2 ≤ 1."),
                 (f"∫<sub>1</sub><sup>∞</sup> e<sup>−{k if k > 1 else ''}x²</sup> dx", "konvergen", f"e<sup>−{k}x²</sup> ≤ e<sup>−{k}x</sup> untuk x ≥ 1, dan ∫ e<sup>−{k}x</sup> konvergen."),
                 (f"∫<sub>2</sub><sup>∞</sup> dx/ln x", "divergen", "1/ln x ≥ 1/x untuk x ≥ 2, dan ∫ 1/x divergen."),
                 (f"∫<sub>1</sub><sup>∞</sup> (2 + sin x)/x{sup(m)} dx", "konvergen", f"0 ≤ (2 + sin x)/x{sup(m)} ≤ 3/x{sup(m)}, p = {m} &gt; 1."),
                 (f"∫<sub>1</sub><sup>∞</sup> (x + {k})/(x² + 1) dx", "divergen", "Banding limit dengan 1/x: rasio → 1, dan ∫ 1/x divergen."),
                 (f"∫<sub>1</sub><sup>∞</sup> x/(x{sup(m + 1)} + {k}) dx", "konvergen" if m > 1 else "divergen", f"~ 1/x{sup(m)}: p = {m}.")]
        expr, ans, why = rng.choice(cases)
        return {"prompt": f"Apakah {expr} konvergen atau divergen?", "correct": ans, "distractors": ["divergen" if ans == "konvergen" else "konvergen", "bernilai 0", "tidak dapat ditentukan"],
                "steps": ["Uji banding: 0 ≤ f ≤ g; ∫g konvergen ⇒ ∫f konvergen; ∫f divergen ⇒ ∫g divergen.", why, f"<b>{ans}</b>."],
                "explanation": "Uji banding cukup menentukan konvergensi tanpa menghitung nilainya."}
    c, s = rng.randint(1, 5), rng.randint(1, 5)
    kind = rng.choice(["lorentz", "kuadrat", "gauss"])
    if kind == "lorentz":
        val = Fr(c, s)
        correct, prompt = times(val, "π"), f"Hitung ∫<sub>−∞</sub><sup>∞</sup> {c if c > 1 else ''}/(x² + {s * s}) dx.".replace("∞</sup> /", "∞</sup> 1/")
        steps = [f"Pecah di 0: 2∫₀^∞; antiturunan ({c}/{s}) arctan(x/{s}).", f"2·({c}/{s})·(π/2) = <b>{correct}</b>."]
        wrong = [times(val / 2, "π"), "divergen", times(val * 2, "π"), n(val)]
    elif kind == "kuadrat":
        p = rng.randint(-4, 4)
        q = p * p + s * s
        val = Fr(1, s)
        correct = times(val, "π")
        prompt = f"Hitung ∫<sub>−∞</sub><sup>∞</sup> dx/({terms([(1, 'x²'), (2 * p, 'x')], q)})."
        steps = [f"Lengkapkan kuadrat: {terms([(1, 'x²'), (2 * p, 'x')], q)} = {fac(-p)}² + {s * s}.".replace("(x)²", "x²"),
                 f"Geser u = x {'+' if p >= 0 else MINUS} {abs(p)}: ∫ du/(u² + {s * s}) = π/{s}.".replace(" + 0:", ":").replace(" − 0:", ":"), f"<b>{correct}</b>."]
        wrong = [times(val / 2, "π"), "divergen", times(val * 2, "π"), times(Fr(1, q), "π")]
    else:
        a = s * s
        correct = times(Fr(c, 2 * s), "√π")
        prompt = f"Gunakan ∫<sub>−∞</sub><sup>∞</sup> e<sup>−x²</sup> dx = √π untuk menghitung ∫<sub>0</sub><sup>∞</sup> {c if c > 1 else ''}e<sup>−{a if a > 1 else ''}x²</sup> dx."
        steps = [f"Substitusi u = {s}x: ∫₀^∞ e<sup>−{a}x²</sup> dx = (1/{s})∫₀^∞ e<sup>−u²</sup> du.", "Fungsi genap: ∫₀^∞ = √π/2.", f"<b>{correct}</b> (integral Gauss)."]
        wrong = [times(Fr(c, s), "√π"), times(Fr(c, 2), "√π") if s > 1 else times(Fr(c, 4), "√π"), "divergen", times(Fr(c, 2 * a), "π")]
    return {"prompt": prompt, "correct": correct, "distractors": wrong, "steps": steps, "explanation": "Integral tak wajar dua arah dipecah di satu titik."}
