"""
Sub-level: Teknik Pengintegralan (Level Utama 3 — Kalkulus Menengah).
Rujukan: Stewart §7.1–7.4, §7.8; Whitman §8.2–8.5; Strang (MIT) Bab 7.
"""

from fractions import Fraction as Fr
import math

from .. import register
from ..fmt import MINUS, fac, lin, n, paren, poly, sup
from ..graphs import fn, g2d, hline, param, readout
from ..precalc.common import distinct, nz
from ..dasar.aplikasi import pi_txt

PS, TG, PP, TW = "km-tek-parsial", "km-tek-trig", "km-tek-pecahan", "km-tek-takwajar"


def area(title, expr, a, b, caption, xr=None, yr=(-2, 4)):
    return g2d(title, xr or [a - 0.5, b + 0.5], list(yr), [param("bb", "Batas atas", a, b, 0.01, b, "b")],
               [{"type": "fill", "upper": expr, "from": a, "to": "bb", "color": "amber"}, fn(expr, "blue", "integran")], None, caption)


# ════════════════════════ Topik 1: Integral parsial ═══════════════════════
@register("tp.pilih_u", PS, (1, 2))
def pilih_u(rng, tier):
    cases = [("x·eˣ", "u = x, dv = eˣ dx"), ("x²·ln x", "u = ln x, dv = x² dx"), ("x·sin x", "u = x, dv = sin x dx"),
             ("arctan x", "u = arctan x, dv = dx"), ("x·cos(3x)", "u = x, dv = cos(3x) dx"), ("ln x", "u = ln x, dv = dx")]
    f, good = rng.choice(cases)
    u = good.split(",")[0][4:]
    dv = good.split("dv = ")[1]
    wrong = [f"u = {dv.replace(' dx', '')}, dv = {u} dx", "u = 1, dv = " + f + " dx", f"u = {f}, dv = dx" if f not in ("ln x", "arctan x") else "u = x, dv = ln x dx",
             "u = eˣ, dv = x dx" if "e" in f else "u = sin x, dv = x dx"]
    return {"prompt": f"Pada ∫ {f} dx dengan integral parsial, pilihan u dan dv yang paling tepat adalah …", "correct": good, "distractors": wrong,
            "steps": ["Rumus: ∫ u dv = uv − ∫ v du.", "Urutan LIATE (Logaritma, Invers trig, Aljabar, Trigonometri, Eksponen): pilih u dari yang paling depan.",
                      f"Untuk {f}: <b>{good}</b> — turunan u lebih sederhana dan dv mudah diintegralkan."],
            "explanation": "Integral parsial adalah kebalikan aturan perkalian: (uv)′ = u′v + uv′."}


@register("tp.xeax", PS, (1, 2, 3))
def xeax(rng, tier):
    a = nz(rng, -3, 3, (0,))
    if tier == 1:
        correct = f"e<sup>{n(a)}x</sup>(x/{paren(a)} − 1/{a * a}) + C".replace("e<sup>1x</sup>", "eˣ").replace("/1 ", " ")
        prompt = f"Tentukan ∫ x·e<sup>{n(a)}x</sup> dx."
        steps = [f"u = x, dv = e<sup>{n(a)}x</sup> dx ⇒ du = dx, v = e<sup>{n(a)}x</sup>/{paren(a)}.",
                 f"∫ = x·e<sup>{n(a)}x</sup>/{paren(a)} − ∫ e<sup>{n(a)}x</sup>/{paren(a)} dx = x·e<sup>{n(a)}x</sup>/{paren(a)} − e<sup>{n(a)}x</sup>/{a * a} + C.",
                 f"<b>{correct}</b>."]
        wrong = [f"x²e<sup>{n(a)}x</sup>/2 + C", f"e<sup>{n(a)}x</sup>(x/{paren(a)} + 1/{a * a}) + C", f"e<sup>{n(a)}x</sup>(x − 1) + C", f"{n(a)}x·e<sup>{n(a)}x</sup> + C"]
        graph = None
    elif tier == 2:
        a = abs(a)
        correct = f"x·sin({a}x)/{a} + cos({a}x)/{a * a} + C"
        prompt = f"Tentukan ∫ x·cos({a}x) dx."
        steps = [f"u = x, dv = cos({a}x) dx ⇒ v = sin({a}x)/{a}.", f"∫ = x sin({a}x)/{a} − ∫ sin({a}x)/{a} dx = x sin({a}x)/{a} + cos({a}x)/{a * a} + C.", f"<b>{correct}</b>."]
        wrong = [f"x·sin({a}x)/{a} − cos({a}x)/{a * a} + C", f"x²sin({a}x)/2 + C", f"−x·sin({a}x)/{a} + cos({a}x)/{a * a} + C", f"sin({a}x)/{a} + C"]
        graph = None
    else:
        which = rng.choice(["e", "cos"])
        if which == "e":
            correct, prompt = "1", "Hitung ∫<sub>0</sub><sup>1</sup> x·eˣ dx."
            steps = ["Antiturunan: eˣ(x − 1).", "[eˣ(x − 1)]₀¹ = e·0 − (1)(−1) = <b>1</b>."]
            wrong = ["e", "e − 1", "e − 2", "1/2"]
            graph = area("Luas di bawah x·eˣ", "x*exp(x)", 0, 1, "Luas pada [0, 1] tepat 1.", yr=(-0.5, 3))
        else:
            correct, prompt = "π/2 − 1", "Hitung ∫<sub>0</sub><sup>π/2</sup> x·cos x dx (soal U-S4)."
            steps = ["Antiturunan: x sin x + cos x.", "[x sin x + cos x]₀^{π/2} = (π/2 + 0) − (0 + 1) = <b>π/2 − 1</b>."]
            wrong = ["π/2", "π/2 + 1", "1", "1 − π/2"]
            graph = area("Luas di bawah x·cos x", "x*cos(x)", 0, 1.5708, "Nilai ≈ 0,5708.", yr=(-0.3, 1))
    return {"prompt": prompt, "correct": correct, "distractors": wrong, "steps": steps, "graphs": [graph] if graph else [],
            "explanation": "∫ u dv = uv − ∫ v du."}


@register("tp.lnx", PS, (1, 2, 3, 4, 5))
def lnx(rng, tier):
    m = rng.randint(1, 4)
    if tier <= 2:
        k = m + 1
        correct = f"x{sup(k)} ln x/{k} − x{sup(k)}/{k * k} + C"
        prompt = f"Tentukan ∫ x{sup(m) if m > 1 else ''} ln x dx."
        steps = [f"u = ln x, dv = x{sup(m) if m > 1 else ''} dx ⇒ du = dx/x, v = x{sup(k)}/{k}.",
                 f"∫ = x{sup(k)} ln x/{k} − ∫ x{sup(m) if m > 1 else ''}/{k} dx = <b>{correct}</b>."]
        wrong = [f"x{sup(k)} ln x/{k} + x{sup(k)}/{k * k} + C", f"x{sup(k)}/{k}·1/x + C", f"x{sup(m)} (ln x)²/2 + C", f"x{sup(k)} ln x/{k} + C"]
    elif tier <= 4:
        k = m + 1
        correct = f"({m}e{sup(k)} + 1)/{k * k}"
        prompt = f"Hitung ∫<sub>1</sub><sup>e</sup> x{sup(m) if m > 1 else ''} ln x dx."
        steps = [f"Antiturunan: x{sup(k)} ln x/{k} − x{sup(k)}/{k * k}.", f"Di x = e: e{sup(k)}/{k} − e{sup(k)}/{k * k} = {m}e{sup(k)}/{k * k}; di x = 1: −1/{k * k}.",
                 f"Selisih: <b>{correct}</b>."]
        wrong = [f"({m}e{sup(k)} − 1)/{k * k}", f"e{sup(k)}/{k}", f"(e{sup(k)} + 1)/{k * k}", f"({k}e{sup(k)} + 1)/{k * k}"]
    else:
        correct = "e − 2"
        prompt = "Hitung ∫<sub>1</sub><sup>e</sup> (ln x)² dx."
        steps = ["Parsial dua kali: u = (ln x)², dv = dx ⇒ x(ln x)² − ∫ 2 ln x dx.", "∫ 2 ln x dx = 2(x ln x − x).",
                 "Antiturunan x(ln x)² − 2x ln x + 2x: di e → e − 2e + 2e = e; di 1 → 2.", "<b>e − 2</b>."]
        wrong = ["e", "e − 1", "2 − e", "1"]
    return {"prompt": prompt, "correct": correct, "distractors": wrong, "steps": steps, "explanation": "ln x hampir selalu dipilih sebagai u."}


@register("tp.berulang", PS, (3, 4, 5))
def berulang(rng, tier):
    if tier == 3:
        correct, prompt = "e − 2", "Hitung ∫<sub>0</sub><sup>1</sup> x²·eˣ dx."
        steps = ["Parsial dua kali (metode tabel): x² ↔ eˣ, 2x ↔ eˣ, 2 ↔ eˣ.", "Antiturunan eˣ(x² − 2x + 2).", "[ ]₀¹ = e(1) − 2 = <b>e − 2</b>."]
        wrong = ["e − 1", "e", "2e − 2", "e + 2"]
    elif tier == 4:
        correct, prompt = "π² − 4", "Hitung ∫<sub>0</sub><sup>π</sup> x²·sin x dx."
        steps = ["Tabel: x² ↔ sin x, 2x ↔ −cos x, 2 ↔ −sin x, 0 ↔ cos x.", "Antiturunan −x² cos x + 2x sin x + 2 cos x.",
                 "Di π: π² − 2; di 0: 2. Selisih <b>π² − 4</b>."]
        wrong = ["π²", "π² + 4", "π² − 2", "2π"]
    else:
        a, b = rng.choice([(1, 1), (1, 2), (2, 1), (3, 4), (2, 3), (1, 3)])
        val = Fr(b, a * a + b * b)
        correct = n(val)
        prompt = f"Hitung ∫<sub>0</sub><sup>∞</sup> e<sup>−{a if a > 1 else ''}x</sup> sin({b if b > 1 else ''}x) dx."
        steps = ["Parsial dua kali menghasilkan integral semula (siklik): I = … − (b²/a²)·I.", "Selesaikan untuk I: I = b/(a² + b²).", f"= <b>{correct}</b>."]
        wrong = [n(Fr(a, a * a + b * b)), n(Fr(1, a * a + b * b)), n(Fr(b, a)), "1"]
    return {"prompt": prompt, "correct": correct, "distractors": wrong, "steps": steps,
            "explanation": "Integral parsial berulang: metode tabel, atau ‘siklik’ untuk eˣ·sin/cos."}


# ════════════════════════ Topik 2: Integral trig & substitusi trig ═════════
@register("tt.pangkat_trig", TG, (1, 2, 3, 4))
def pangkat_trig(rng, tier):
    if tier == 1:
        correct, prompt = "−cos x + cos³x/3 + C", "Tentukan ∫ sin³x dx."
        steps = ["sin³x = sin x(1 − cos²x).", "u = cos x, du = −sin x dx: ∫ −(1 − u²) du = −u + u³/3.", f"<b>{correct}</b>."]
        wrong = ["sin⁴x/4 + C", "cos x − cos³x/3 + C", "−cos³x/3 + C", "−cos x + C"]
    elif tier == 2:
        val, f = Fr(2, 3), rng.choice(["sin", "cos"])
        correct, prompt = "2/3", f"Hitung ∫<sub>0</sub><sup>π/2</sup> {f}³x dx."
        steps = [f"{f}³x = {f} x(1 − {'cos' if f == 'sin' else 'sin'}²x); substitusi u = {'cos' if f == 'sin' else 'sin'} x.", "Nilai integral = 1 − 1/3 = <b>2/3</b>."]
        wrong = ["1/3", "3/4", "1", "π/4"]
    else:
        nn = rng.choice([2, 4, 6] if tier == 4 else [3, 5, 7])
        num = math.prod(range(nn - 1, 0, -2))
        den = math.prod(range(nn, 0, -2))
        frac = Fr(num, den)
        correct = f"{n(frac)}·π/2" if nn % 2 == 0 else n(frac)
        prompt = f"Hitung ∫<sub>0</sub><sup>π/2</sup> cos{sup(nn)}x dx."
        steps = ["Rumus reduksi (Wallis): ∫₀^{π/2} cosⁿx dx = ((n − 1)/n)·∫₀^{π/2} cosⁿ⁻²x dx.",
                 f"Untuk n {'genap' if nn % 2 == 0 else 'ganjil'}: {' · '.join(f'{k - 1}/{k}' for k in range(nn, 1, -2))}" + (" · π/2." if nn % 2 == 0 else "."),
                 f"= <b>{correct}</b>."]
        wrong = [n(frac) if nn % 2 == 0 else f"{n(frac)}·π/2", f"{n(Fr(1, nn))}", f"{n(frac * 2)}", "π/4"]
    return {"prompt": prompt, "correct": correct, "distractors": wrong, "steps": steps, "explanation": "Pangkat ganjil: pisahkan satu faktor lalu substitusi. Pangkat genap: identitas setengah sudut / reduksi."}


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
    a = rng.randint(1, 6)
    kind = rng.choice(["lingkaran", "arcsin"]) if tier == 3 else rng.choice(["arctan", "lingkaran"]) if tier == 4 else "x2"
    if kind == "lingkaran":
        correct, prompt = pi_txt(Fr(a * a, 4)), f"Hitung ∫<sub>0</sub><sup>{a}</sup> √({a * a} − x²) dx."
        steps = [f"x = {a} sin θ, dx = {a} cos θ dθ, √({a * a} − x²) = {a} cos θ; batas 0 → 0, {a} → π/2.", f"∫₀^{{π/2}} {a * a} cos²θ dθ = {a * a}·π/4.", f"= <b>{correct}</b> (seperempat lingkaran)."]
        wrong = [pi_txt(Fr(a * a, 2)), pi_txt(a * a), pi_txt(Fr(a, 4)), n(a * a)]
    elif kind == "arcsin":
        correct, prompt = "π/2", f"Hitung ∫<sub>0</sub><sup>{a}</sup> dx/√({a * a} − x²)."
        steps = [f"x = {a} sin θ ⇒ integran menjadi dθ.", "Batas θ: 0 → π/2.", "<b>π/2</b>."]
        wrong = [pi_txt(Fr(1, 2 * a)), "π", "1", f"π/{2 * a}" if a > 1 else "π/4"]
    elif kind == "arctan":
        correct, prompt = f"π/{4 * a}", f"Hitung ∫<sub>0</sub><sup>{a}</sup> dx/(x² + {a * a})."
        steps = [f"x = {a} tan θ, dx = {a} sec²θ dθ, x² + {a * a} = {a * a} sec²θ.", f"∫ (1/{a}) dθ dari 0 sampai π/4.", f"= <b>π/{4 * a}</b>."]
        wrong = [f"π/{2 * a}", "π/4", f"π/{4 * a * a}", f"{a}π/4"]
    else:
        correct, prompt = pi_txt(Fr(a * a, 4)), f"Hitung ∫<sub>0</sub><sup>{a}</sup> x²/√({a * a} − x²) dx."
        steps = [f"x = {a} sin θ: integran {a * a} sin²θ dθ, θ dari 0 ke π/2.", f"{a * a}·π/4.", f"<b>{correct}</b>."]
        wrong = [pi_txt(Fr(a * a, 2)), pi_txt(Fr(a, 4)), n(Fr(a * a, 4)), pi_txt(a * a)]
    return {"prompt": prompt, "correct": correct, "distractors": wrong, "steps": steps,
            "graphs": [area("Daerah yang dihitung", f"sqrt({a * a}-x*x)" if kind == "lingkaran" else f"1/(x*x+{a * a})" if kind == "arctan" else f"sqrt({a * a}-x*x)",
                            0, a, "Substitusi trigonometri menghilangkan akar kuadrat.", yr=(-0.2, a + 0.5))] if kind in ("lingkaran", "arctan") else [],
            "explanation": "√(a² − x²): x = a sin θ; √(a² + x²): x = a tan θ; √(x² − a²): x = a sec θ."}


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
    p = Fr(rng.choice([2, 3, 4, 5])) if tier == 1 else rng.choice([Fr(3, 2), Fr(5, 2), Fr(4, 3), Fr(1, 2), Fr(1), Fr(2)])
    if tier == 3:
        p = rng.choice([Fr(1), Fr(1, 2), Fr(3, 2), Fr(5, 4)])
    conv = p > 1
    correct = n(1 / (p - 1)) if conv else "divergen"
    ptxt = n(p)
    return {"prompt": f"Hitung ∫<sub>1</sub><sup>∞</sup> dx/x<sup>{ptxt}</sup> (atau nyatakan divergen).", "correct": correct,
            "distractors": [n(1 / p), "divergen" if conv else n(abs(1 / (p - 1)) if p != 1 else 1), "0", n(1 / (p + 1))],
            "steps": ["∫₁ᵗ x⁻ᵖ dx = (t¹⁻ᵖ − 1)/(1 − p) untuk p ≠ 1, dan ln t untuk p = 1; lalu t → ∞.",
                      "Konvergen ⇔ p &gt; 1, nilainya 1/(p − 1)." if conv else f"p = {ptxt} ≤ 1 ⇒ t¹⁻ᵖ (atau ln t) → ∞.", f"Jawaban: <b>{correct}</b>."],
            "graphs": [g2d("Luas di bawah 1/xᵖ sampai t", [0.8, 30], [0, 1.5], [param("t", "Batas atas t", 1, 30, 0.1, 10, "t"), param("pp", "p", 0.5, 3, 0.05, float(p), "p")],
                           [{"type": "fill", "upper": "pow(x,-pp)", "from": 1, "to": "t", "color": "amber"}, fn("pow(x,-pp)", "blue", "1/xᵖ")],
                           [readout("∫₁ᵗ", "pp==1?log(t):(pow(t,1-pp)-1)/(1-pp)", 4)], "Untuk p > 1 luas mendekati batas; untuk p ≤ 1 terus membesar.")],
            "explanation": "Uji-p integral: ∫₁^∞ 1/xᵖ konvergen ⇔ p > 1 (dipakai lagi di uji integral deret)."}


@register("tw.eksponen", TW, (1, 2, 3, 5))
def tw_eksponen(rng, tier):
    a, b = rng.randint(1, 9), rng.randint(1, 5)
    if tier <= 2:
        val = Fr(a, b)
        prompt = f"Hitung ∫<sub>0</sub><sup>∞</sup> {a}e<sup>−{b if b > 1 else ''}x</sup> dx."
        steps = [f"∫₀ᵗ = ({a}/{b})(1 − e<sup>−{b}t</sup>).", f"t → ∞: <b>{n(val)}</b>."]
    elif tier == 3:
        val = Fr(1, b * b)
        prompt = f"Hitung ∫<sub>0</sub><sup>∞</sup> x·e<sup>−{b if b > 1 else ''}x</sup> dx."
        steps = ["Parsial: −(x/b)e⁻ᵇˣ − e⁻ᵇˣ/b²; suku x·e⁻ᵇˣ → 0 untuk x → ∞ (L'Hôpital).", f"= 1/{b * b} = <b>{n(val)}</b> (rata-rata distribusi eksponensial dikali 1/λ)."]
    else:
        m = rng.randint(2, 6)
        val = Fr(math.factorial(m))
        prompt = f"Hitung ∫<sub>0</sub><sup>∞</sup> x{sup(m)}e<sup>−x</sup> dx."
        steps = ["Iₙ = ∫₀^∞ xⁿe⁻ˣ dx; parsial memberi Iₙ = n·Iₙ₋₁ dengan I₀ = 1.", f"Iₙ = n! ⇒ <b>{m}! = {val}</b> (fungsi Gamma Γ(n + 1))."]
    return {"prompt": prompt, "correct": n(val), "distractors": [n(val * 2), "divergen", n(val + 1), "0"], "steps": steps,
            "explanation": "Integral tak wajar = limit integral biasa saat batas → ∞."}


@register("tw.tak_terbatas", TW, (2, 3, 4))
def tak_terbatas(rng, tier):
    if tier == 2:
        a = rng.randint(1, 9) ** 2
        val = 2 * int(a ** 0.5)
        prompt, correct = f"Hitung ∫<sub>0</sub><sup>{a}</sup> dx/√x.", n(val)
        steps = ["Integran tak terbatas di x = 0: ∫ₛ^{a} x<sup>−1/2</sup> dx = 2√a − 2√s.", f"s → 0⁺: 2√{a} = <b>{val}</b>."]
        wrong = [n(int(a ** 0.5)), "divergen", n(val * 2), n(a)]
    else:
        p = rng.choice([Fr(1, 2), Fr(1, 3), Fr(2, 3), Fr(1), Fr(2)]) if tier == 4 else rng.choice([Fr(1, 2), Fr(1, 3), Fr(3, 4)])
        conv = p < 1
        correct = n(1 / (1 - p)) if conv else "divergen"
        prompt = f"Hitung ∫<sub>0</sub><sup>1</sup> dx/x<sup>{n(p)}</sup> (atau nyatakan divergen)."
        steps = ["Masalah di x = 0. ∫ₛ¹ x⁻ᵖ dx = (1 − s¹⁻ᵖ)/(1 − p) untuk p ≠ 1.", "Konvergen ⇔ p &lt; 1 (kebalikan dari kasus ∞)." if conv else "p ≥ 1 ⇒ divergen.", f"<b>{correct}</b>."]
        wrong = [n(1 / p) if p else "1", "divergen" if conv else n(1), "0", n(1 / (p + 1))]
    return {"prompt": prompt, "correct": correct, "distractors": wrong, "steps": steps, "explanation": "Integran tak terbatas di ujung: ambil limit dari dalam interval."}


@register("tw.banding", TW, (4, 5))
def tw_banding(rng, tier):
    if tier == 4:
        k = rng.randint(1, 9)
        cases = [(f"∫<sub>1</sub><sup>∞</sup> dx/(x² + {k})", "konvergen", f"1/(x² + {k}) ≤ 1/x² dan ∫ 1/x² konvergen."),
                 (f"∫<sub>1</sub><sup>∞</sup> dx/√(x + {k})", "divergen", f"1/√(x + {k}) ≥ 1/√({k + 1}x) ~ 1/x<sup>1/2</sup>, p = 1/2 ≤ 1."),
                 (f"∫<sub>1</sub><sup>∞</sup> e<sup>−x²</sup> dx", "konvergen", "e<sup>−x²</sup> ≤ e<sup>−x</sup> untuk x ≥ 1, dan ∫ e⁻ˣ konvergen."),
                 (f"∫<sub>2</sub><sup>∞</sup> dx/ln x", "divergen", "1/ln x ≥ 1/x untuk x ≥ 2, dan ∫ 1/x divergen.")]
        expr, ans, why = rng.choice(cases)
        return {"prompt": f"Apakah {expr} konvergen atau divergen?", "correct": ans, "distractors": ["divergen" if ans == "konvergen" else "konvergen", "bernilai 0", "tidak dapat ditentukan"],
                "steps": ["Uji banding: 0 ≤ f ≤ g; ∫g konvergen ⇒ ∫f konvergen; ∫f divergen ⇒ ∫g divergen.", why, f"<b>{ans}</b>."],
                "explanation": "Uji banding cukup menentukan konvergensi tanpa menghitung nilainya."}
    a = rng.randint(1, 9)
    if rng.random() < 0.5:
        correct, prompt = "π", "Hitung ∫<sub>−∞</sub><sup>∞</sup> dx/(1 + x²)."
        steps = ["Pecah di 0: 2∫₀^∞ dx/(1 + x²) = 2·lim arctan t.", "= 2·π/2 = <b>π</b>."]
        wrong = ["π/2", "divergen", "2π", "1"]
    else:
        correct, prompt = f"(1/2)√(π/{a})" if a > 1 else "√π/2", f"Gunakan ∫<sub>−∞</sub><sup>∞</sup> e<sup>−x²</sup> dx = √π untuk menghitung ∫<sub>0</sub><sup>∞</sup> e<sup>−{a if a > 1 else ''}x²</sup> dx."
        steps = [f"Substitusi u = √{a}·x: ∫₀^∞ e<sup>−{a}x²</sup> dx = (1/√{a})∫₀^∞ e<sup>−u²</sup> du.", "Fungsi genap: ∫₀^∞ = √π/2.", f"<b>{correct}</b> (integral Gauss, FMIPA)."]
        wrong = [f"√(π/{a})", "√π", "divergen", f"π/{2 * a}"]
    return {"prompt": prompt, "correct": correct, "distractors": wrong, "steps": steps, "explanation": "Integral tak wajar dua arah dipecah di satu titik."}
