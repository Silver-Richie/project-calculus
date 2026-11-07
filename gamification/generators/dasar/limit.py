"""
Sub-level: Limit dan Kekontinuan (Level Utama 2 — Kalkulus Dasar).
Rujukan: Stewart §2.2–2.6; Whitman §2.3, §4.3; Strang (MIT) §2.6–2.7.
"""

from fractions import Fraction as Fr
import math

from .. import register
from ..fmt import MINUS, fac, lin, n, paren, poly, sup
from ..graphs import fn, g2d, hline, param, pt, readout, vline
from ..precalc.common import distinct, nz
from ..precalc.trigonometri import exact, rad_text

K, A, I, TR, C = "kd-lim-konsep", "kd-lim-aljabar", "kd-lim-takhingga", "kd-lim-trig", "kd-lim-kontinu"


def xm(c):
    """Teks 'x − c' tanpa kurung (c = 0 → 'x')."""
    return "x" if c == 0 else (f"x {MINUS} {n(c)}" if c > 0 else f"x + {n(-c)}")


def ev(coeffs, x):
    """Nilai polinom (koefisien derajat tertinggi dulu)."""
    v = 0
    for c in coeffs:
        v = v * x + c
    return v


def js_poly(coeffs, var="x"):
    deg = len(coeffs) - 1
    return "+".join(f"({c})*{var}**{deg - i}" for i, c in enumerate(coeffs)) or "0"


def approach_graph(title, expr, c, L, xr, yr, caption, hole=True):
    """Grafik limit dengan titik bergerak x = c + d (slider d → 0)."""
    sub = expr.replace("x", "(X)")
    return g2d(title, xr, yr, [param("d", "Jarak ke c (d)", -1.5, 1.5, 0.01, 0.6, "d")],
               [fn(expr, "blue", "f(x)"), hline(L, "gray"), pt(c, L, "blue", hollow=hole),
                pt(f"{c}+d", sub.replace("X", f"{c}+d"), "red", label="x = c + d")],
               [readout("x", f"{c}+d", 4), readout("f(x)", sub.replace("X", f"{c}+d"), 6), readout("Nilai limit", str(L), 6)],
               caption)


# ════════════════════════ Topik 1: Konsep limit & limit sepihak ═════════════
@register("lim.substitusi", K, (1, 2))
def substitusi(rng, tier):
    c = rng.randint(-3, 3)
    co = [nz(rng, -2, 2), rng.randint(-4, 4), rng.randint(-5, 5), rng.randint(-6, 6)]
    if tier == 1:
        val = ev(co, c)
        prompt = f"Hitung lim<sub>x→{n(c)}</sub> ({poly(co)})."
        expr = js_poly(co)
        steps = ["Polinom kontinu di semua bilangan real, jadi limitnya cukup dihitung dengan substitusi langsung.",
                 f"f({n(c)}) = {n(val)}."]
    else:
        d = rng.choice([v for v in range(-6, 7) if v != -c and v != 0])
        top = co[1:]
        val = Fr(ev(top, c), c + d)
        prompt = f"Hitung lim<sub>x→{n(c)}</sub> ({poly(top)}) / ({lin(1, d)})."
        expr = f"({js_poly(top)})/(x+({d}))"
        steps = [f"Penyebut di x = {n(c)}: {n(c + d)} ≠ 0, jadi fungsi rasional kontinu di sana (Hukum Limit untuk hasil bagi).",
                 f"Substitusi: {n(ev(top, c))} / {n(c + d)} = {n(val)}."]
    steps.append(f"Jawaban: <b>{n(val)}</b>.")
    return {"prompt": prompt, "correct": n(val), "distractors": [n(val + 1), n(-val), n(val * 2), n(val - 2)], "steps": steps,
            "graphs": [approach_graph("Nilai f(x) saat x mendekati c", expr, c, float(val), [c - 4, c + 4],
                                      [float(val) - 15, float(val) + 15], "Geser d menuju 0 dari kiri dan kanan.", hole=False)],
            "explanation": "Jika f kontinu di c (polinom, rasional dengan penyebut ≠ 0), maka lim f(x) = f(c)."}


@register("lim.sepihak", K, (1, 2, 3))
def sepihak(rng, tier):
    c = rng.randint(-2, 3)
    a, b = nz(rng, -3, 3), rng.randint(-4, 4)
    d, e = nz(rng, -3, 3), rng.randint(-4, 4)
    L1, L2 = a * c + b, d * c + e
    if tier == 3:
        e2 = rng.randint(-3, 3)
        k = c * c + e2 - a * c
        prompt = (f"f(x) = {lin(a, 0)} + k untuk x &lt; {n(c)} dan f(x) = x² {'+' if e2 >= 0 else MINUS} {abs(e2)} untuk x ≥ {n(c)}. "
                  f"Tentukan k agar lim<sub>x→{n(c)}</sub> f(x) ada.")
        return {"prompt": prompt, "correct": f"k = {n(k)}", "distractors": [f"k = {n(k + a * c * 2)}", f"k = {n(-k)}", f"k = {n(k + 1)}", f"k = {n(c * c + e2)}"],
                "steps": [f"Limit kiri: lim<sub>x→{n(c)}⁻</sub> ({lin(a, 0)} + k) = {n(a * c)} + k.",
                          f"Limit kanan: lim<sub>x→{n(c)}⁺</sub> (x² + {paren(e2)}) = {n(c * c + e2)}.",
                          f"Limit ada ⇔ kiri = kanan: {n(a * c)} + k = {n(c * c + e2)} ⇒ <b>k = {n(k)}</b>."],
                "graphs": [g2d("Fungsi sepotong-sepotong: geser k sampai kedua potongan bertemu", [c - 4, c + 4], [-15, 20],
                               [param("k", "k", k - 8, k + 8, 0.5, k + 3, "k")],
                               [fn(f"{a}*x+k", "orange", "kiri", **{"to": c}), fn(f"x*x+({e2})", "blue", "kanan", **{"from": c}),
                                pt(c, f"{a}*{c}+k", "orange", hollow=True), pt(c, c * c + e2, "blue")],
                               [readout("limit kiri", f"{a}*{c}+k", 3), readout("limit kanan", str(c * c + e2), 3)],
                               f"Pada k = {k} kedua potongan bersambung di x = {c}.")],
                "explanation": "lim f(x) ada ⇔ limit kiri dan limit kanan ada dan sama."}
    side = rng.choice(["⁻", "⁺"])
    prompt = (f"Diketahui f(x) = {lin(a, b)} untuk x &lt; {n(c)} dan f(x) = {lin(d, e)} untuk x ≥ {n(c)}. ")
    if tier == 1:
        val = L1 if side == "⁻" else L2
        prompt += f"Hitung lim<sub>x→{n(c)}{side}</sub> f(x)."
        correct, wrong = n(val), [n(L2 if side == "⁻" else L1), n(val + 1), n(-val), n(L1 + L2)]
        steps = [f"x→{n(c)}{side} berarti x mendekati {n(c)} dari {'kiri (x &lt; c)' if side == '⁻' else 'kanan (x &gt; c)'}, "
                 f"jadi pakai rumus {lin(a, b) if side == '⁻' else lin(d, e)}.", f"Substitusi x = {n(c)}: <b>{n(val)}</b>."]
    else:
        prompt += f"Bagaimana lim<sub>x→{n(c)}</sub> f(x)?"
        correct = f"ada, nilainya {n(L1)}" if L1 == L2 else f"tidak ada (kiri {n(L1)} ≠ kanan {n(L2)})"
        wrong = [f"ada, nilainya {n(L2 + 1)}", f"ada, nilainya {n(L1 + L2)}", f"tidak ada (kiri {n(L2)} ≠ kanan {n(L1)})" if L1 != L2 else "tidak ada",
                 f"ada, nilainya {n(L1)}" if L1 != L2 else f"ada, nilainya {n(L1 + 1)}"]
        steps = [f"Limit kiri = {n(a)}·{paren(c)} + {paren(b)} = {n(L1)}.", f"Limit kanan = {n(d)}·{paren(c)} + {paren(e)} = {n(L2)}.",
                 f"Limit (dua sisi) ada hanya jika keduanya sama. Jawaban: <b>{correct}</b>."]
    return {"prompt": prompt, "correct": correct, "distractors": wrong, "steps": steps,
            "graphs": [g2d("Limit kiri vs limit kanan", [c - 4, c + 4], [-15, 15],
                           [param("d", "Jarak ke c (d > 0)", 0.01, 2, 0.01, 0.8, "d")],
                           [fn(f"{a}*x+({b})", "orange", "x < c", **{"to": c}), fn(f"{d}*x+({e})", "blue", "x ≥ c", **{"from": c}),
                            pt(f"{c}-d", f"{a}*({c}-d)+({b})", "orange"), pt(f"{c}+d", f"{d}*({c}+d)+({e})", "blue")],
                           [readout("f(c − d)", f"{a}*({c}-d)+({b})", 4), readout("f(c + d)", f"{d}*({c}+d)+({e})", 4)],
                           "Kecilkan d: titik oranye menuju limit kiri, titik biru menuju limit kanan.")],
            "explanation": "lim f(x) ada ⇔ lim kiri = lim kanan."}


@register("lim.hukum", K, (3, 4, 5))
def hukum(rng, tier):
    A_, B_ = nz(rng, -6, 6), nz(rng, -6, 6)
    p, q = nz(rng, -4, 4), nz(rng, -4, 4)
    if tier == 3:
        val = p * A_ + q * B_
        what = f"[{n(p)}f(x) + {n(q)}g(x)]"
        step = f"{n(p)}·{paren(A_)} + {n(q)}·{paren(B_)} = {n(val)}"
    elif tier == 4:
        while A_ + B_ == 0:
            B_ += 1
        val = Fr(A_ * B_, A_ + B_)
        what = "f(x)·g(x) / [f(x) + g(x)]"
        step = f"({n(A_)}·{paren(B_)}) / ({n(A_)} + {paren(B_)}) = {n(val)}"
    else:
        A_ = rng.choice([1, 4, 9, 16, 25]) - B_ * 0
        k = rng.randint(2, 4)
        val = Fr(int(math.isqrt(A_)) + k * B_ ** 2, 1)
        what = f"[√f(x) + {k}·(g(x))²]"
        step = f"√{A_} + {k}·{paren(B_)}² = {int(math.isqrt(A_))} + {k * B_ * B_} = {n(val)}"
    return {"prompt": f"Diketahui lim<sub>x→c</sub> f(x) = {n(A_)} dan lim<sub>x→c</sub> g(x) = {n(B_)}. Hitung lim<sub>x→c</sub> {what}.",
            "correct": n(val), "distractors": [n(val + 1), n(-val), n(val * 2), n(A_ + B_)],
            "steps": ["Hukum limit: limit jumlah = jumlah limit, limit kali = kali limit, limit hasil bagi = hasil bagi limit "
                      "(penyebut ≠ 0), dan lim √f = √(lim f) (bila lim f ≥ 0).", f"Substitusi nilai limit: {step}.", f"Jawaban: <b>{n(val)}</b>."],
            "explanation": "Hukum limit (Stewart §2.3) memungkinkan limit dihitung bagian per bagian."}


@register("lim.eksistensi", K, (4, 5))
def eksistensi(rng, tier):
    c = rng.randint(-4, 5)
    if tier == 4:
        m = rng.randint(1, 4)
        correct = f"kiri = {MINUS}{m}, kanan = {m}, limit tidak ada"
        return {"prompt": f"Untuk f(x) = {m}|{xm(c)}| / ({xm(c)}), tentukan perilaku limit di x = {n(c)}.",
                "correct": correct,
                "distractors": [f"kiri = kanan = {m}, limit = {m}", f"kiri = {m}, kanan = {MINUS}{m}, limit tidak ada", "limit = 0", f"kiri = kanan = {MINUS}{m}, limit = {MINUS}{m}"],
                "steps": [f"Untuk x &gt; {n(c)}: |x − c| = x − c, jadi f(x) = {m}.", f"Untuk x &lt; {n(c)}: |x − c| = −(x − c), jadi f(x) = −{m}.",
                          f"Limit kiri −{m} ≠ limit kanan {m} ⇒ <b>limit tidak ada</b> (lompatan)."],
                "graphs": [g2d("Fungsi tangga m|x − c|/(x − c)", [c - 4, c + 4], [-5, 5], [param("m", "m", 1, 4, 1, m, "m")],
                               [fn(f"m*abs(x-({c}))/(x-({c}))", "blue", "f(x)"), pt(c, "-m", "blue", hollow=True), pt(c, "m", "blue", hollow=True)],
                               None, "Ada lompatan setinggi 2m di x = c.")],
                "explanation": "Limit dua sisi tidak ada bila limit kiri ≠ limit kanan."}
    nn = rng.randint(-3, 6)
    val = 2 * nn - 1
    return {"prompt": f"Hitung lim<sub>x→{n(nn)}⁻</sub> ⌊x⌋ + lim<sub>x→{n(nn)}⁺</sub> ⌊x⌋ (⌊x⌋ = bilangan bulat terbesar ≤ x).",
            "correct": n(val), "distractors": [n(2 * nn), n(2 * nn + 1), n(nn), "tidak ada"],
            "steps": [f"Sedikit di kiri {n(nn)} (mis. {n(nn)} − 0,001): ⌊x⌋ = {n(nn - 1)}.",
                      f"Sedikit di kanan {n(nn)}: ⌊x⌋ = {n(nn)}.", f"Jumlah: {n(nn - 1)} + {n(nn)} = <b>{n(val)}</b>. (Limit dua sisi ⌊x⌋ di bilangan bulat tidak ada.)"],
            "graphs": [g2d("y = ⌊x⌋ (fungsi tangga)", [nn - 3, nn + 3], [nn - 4, nn + 3], [param("d", "d", 0.01, 0.99, 0.01, 0.3, "d")],
                           [fn("floor(x)", "blue", "⌊x⌋"), pt(f"{nn}-d", f"floor({nn}-d)", "orange"), pt(f"{nn}+d", f"floor({nn}+d)", "red")],
                           None, "Titik oranye (kiri) dan merah (kanan) berada di anak tangga berbeda.")],
            "explanation": "Limit sepihak dapat ada walaupun limit dua sisi tidak ada."}


# ════════════════════════ Topik 2: Teknik aljabar bentuk 0/0 ═══════════════
@register("lim.faktor", A, (1, 2, 3))
def faktor(rng, tier):
    a, b = distinct(rng, -5, 6, 2)
    if tier == 3:
        a = nz(rng, -3, 3)
        val = 3 * a * a
        prompt = f"Hitung lim<sub>x→{n(a)}</sub> (x³ {MINUS if a ** 3 >= 0 else '+'} {abs(a ** 3)}) / {fac(a)}."
        steps = ["Substitusi langsung memberi 0/0 (bentuk tak tentu).", f"x³ − a³ = (x − a)(x² + ax + a²) dengan a = {n(a)}.",
                 f"Coret (x − a): lim (x² + ax + a²) = 3a² = <b>{n(val)}</b>."]
        expr = f"(x**3-({a ** 3}))/(x-({a}))"
    else:
        co = [1, -(a + b), a * b]
        val = a - b
        prompt = f"Hitung lim<sub>x→{n(a)}</sub> ({poly(co)}) / {fac(a)}."
        steps = ["Substitusi langsung: 0/0 (tak tentu) ⇒ faktorkan pembilang.",
                 f"{poly(co)} = {fac(a)}{fac(b)}.", f"Coret {fac(a)}: lim<sub>x→{n(a)}</sub> {fac(b)} = {n(a)} − {paren(b)} = <b>{n(val)}</b>."]
        expr = f"({js_poly(co)})/(x-({a}))"
    if tier == 2:
        k = rng.choice([2, 3, -2])
        co = [k, -k * (a + b), k * a * b]
        val = k * (a - b)
        prompt = f"Hitung lim<sub>x→{n(a)}</sub> ({poly(co)}) / {fac(a)}."
        steps = ["Substitusi langsung: 0/0 ⇒ faktorkan.", f"{poly(co)} = {k}{fac(a)}{fac(b)}.",
                 f"Coret {fac(a)}: {k}·({n(a)} − {paren(b)}) = <b>{n(val)}</b>."]
        expr = f"({js_poly(co)})/(x-({a}))"
    return {"prompt": prompt, "correct": n(val), "distractors": [n(a + b), n(-val), n(val + 1), "0", "tidak ada"], "steps": steps,
            "graphs": [approach_graph("Lubang pada grafik: f tidak terdefinisi di c, tetapi limitnya ada", expr, a, float(val),
                                      [a - 4, a + 4], [float(val) - 12, float(val) + 12], "Grafik berupa garis/parabola dengan satu titik berlubang.")],
            "explanation": "0/0 bukan jawaban: sederhanakan (faktorkan) lalu substitusi."}


@register("lim.selisih_kuadrat", A, (1, 2))
def selisih_kuadrat(rng, tier):
    a = nz(rng, -7, 7)
    if tier == 1:
        val = 2 * a
        prompt = f"Hitung lim<sub>x→{n(a)}</sub> (x² − {a * a}) / {fac(a)}."
        steps = [f"x² − {a * a} = {fac(a)}{fac(-a)}.", f"Coret: lim (x + {paren(a)}) = <b>{n(val)}</b>."]
    else:
        m = nz(rng, -4, 4, (0, 1))
        val = Fr(2 * a, m)
        prompt = f"Hitung lim<sub>x→{n(a)}</sub> (x² − {a * a}) / ({lin(m, -m * a)})."
        steps = [f"Penyebut = {m}{fac(a)}; pembilang = {fac(a)}{fac(-a)}.", f"Coret (x − a): lim (x + a)/{paren(m)} = {n(2 * a)}/{paren(m)} = <b>{n(val)}</b>."]
    return {"prompt": prompt, "correct": n(val), "distractors": [n(a * a), "0", n(-val), n(val + 1)], "steps": steps,
            "explanation": "a² − b² = (a − b)(a + b)."}


@register("lim.akar", A, (2, 3, 4))
def akar(rng, tier):
    q = rng.randint(1, 5)
    p = rng.randint(-5, 8)
    c = q * q - p
    val = Fr(1, 2 * q)
    if tier == 4:
        val = Fr(2 * q)
        prompt = f"Hitung lim<sub>x→{n(c)}</sub> ({xm(c)}) / (√(x {'+' if p >= 0 else MINUS} {abs(p)}) − {q})."
        steps = ["Substitusi memberi 0/0. Kalikan pembilang & penyebut dengan sekawan √(x + p) + q.",
                 f"Penyebut menjadi x + {paren(p)} − {q * q} = {xm(c)}, sehingga tersisa √(x + {paren(p)}) + {q}.",
                 f"Di x = {n(c)}: {q} + {q} = <b>{2 * q}</b>."]
    else:
        prompt = f"Hitung lim<sub>x→{n(c)}</sub> (√(x {'+' if p >= 0 else MINUS} {abs(p)}) − {q}) / {fac(c)}."
        steps = ["Substitusi memberi 0/0. Kalikan dengan sekawan √(x + p) + q.",
                 f"(√(x + {paren(p)}) − {q})(√(x + {paren(p)}) + {q}) = x + {paren(p)} − {q * q} = {xm(c)}.",
                 f"Coret: lim 1/(√(x + {paren(p)}) + {q}) = 1/({q} + {q}) = <b>{n(val)}</b>."]
    return {"prompt": prompt, "correct": n(val), "distractors": [n(Fr(1, q)), n(Fr(1, 2 * q)), n(2 * q), "0", n(val * 2 + 1)], "steps": steps,
            "graphs": [approach_graph("Limit bentuk akar", f"(sqrt(x+({p}))-{q})/(x-({c}))", c, float(Fr(1, 2 * q)),
                                      [max(-p, c - 4), c + 4], [-0.2, 1.2], "Fungsi tidak terdefinisi tepat di c tetapi nilainya mendekati 1/(2q).")],
            "explanation": "Bentuk 0/0 dengan akar: kalikan sekawan."}


@register("lim.pecahan", A, (3, 4))
def pecahan(rng, tier):
    a = nz(rng, -6, 6)
    if tier == 3:
        val = Fr(-1, a * a)
        prompt = f"Hitung lim<sub>x→{n(a)}</sub> (1/x − 1/{paren(a)}) / {fac(a)}."
        steps = ["Samakan penyebut: 1/x − 1/a = (a − x)/(ax).", "Bagi dengan (x − a): (a − x)/(ax(x − a)) = −1/(ax).",
                 f"Di x = {n(a)}: −1/{a * a} = <b>{n(val)}</b>."]
    else:
        val = Fr(-2, a ** 3)
        prompt = f"Hitung lim<sub>x→{n(a)}</sub> (1/x² − 1/{a * a}) / {fac(a)}."
        steps = ["1/x² − 1/a² = (a² − x²)/(a²x²) = −(x − a)(x + a)/(a²x²).", "Coret (x − a): −(x + a)/(a²x²).",
                 f"Di x = {n(a)}: −2a/a⁴ = −2/a³ = <b>{n(val)}</b>."]
    return {"prompt": prompt, "correct": n(val), "distractors": [n(-val), n(Fr(1, a)), "0", n(val * 2)], "steps": steps,
            "explanation": "Pecahan bersusun: samakan penyebut dulu. Limit ini adalah turunan 1/x (atau 1/x²) di a."}


@register("lim.pangkat_umum", A, (4, 5))
def pangkat_umum(rng, tier):
    if tier == 4:
        nn, a = rng.randint(3, 7), rng.choice([1, 2, -1])
        val = nn * a ** (nn - 1)
        prompt = f"Hitung lim<sub>x→{n(a)}</sub> (x{sup(nn)} − {paren(a ** nn)}) / {fac(a)}."
        steps = ["xⁿ − aⁿ = (x − a)(xⁿ⁻¹ + axⁿ⁻² + … + aⁿ⁻¹), jumlah n suku.", f"Di x = a setiap suku bernilai aⁿ⁻¹, jadi limit = n·aⁿ⁻¹ = {nn}·{paren(a)}{sup(nn - 1)}.",
                 f"= <b>{n(val)}</b>."]
    else:
        nn, m = distinct(rng, 2, 9, 2)
        val = Fr(nn, m)
        prompt = f"Hitung lim<sub>x→1</sub> (x{sup(nn)} − 1) / (x{sup(m)} − 1)."
        steps = ["Bagi pembilang dan penyebut dengan (x − 1).", f"(x{sup(nn)} − 1)/(x − 1) → {nn} dan (x{sup(m)} − 1)/(x − 1) → {m} (pola n·1ⁿ⁻¹).",
                 f"Limit = <b>{n(val)}</b>."]
    return {"prompt": prompt, "correct": n(val), "distractors": [n(val + 1), n(Fr(1) / val if val else 2), "1", "0"], "steps": steps,
            "explanation": "lim (xⁿ − aⁿ)/(x − a) = n·aⁿ⁻¹ — cikal bakal aturan pangkat turunan."}


@register("lim.akar_kubik", A, (5,))
def akar_kubik(rng, tier):
    a = rng.choice([1, 2, 3, -1, -2])
    val = Fr(1, 3 * a * a)
    return {"prompt": f"Hitung lim<sub>x→{n(a ** 3)}</sub> (∛x − {paren(a)}) / (x − {paren(a ** 3)}).",
            "correct": n(val), "distractors": [n(Fr(1, a * a)), n(3 * a * a), n(Fr(1, 3 * a)), "0"],
            "steps": ["Misal u = ∛x, maka x = u³ dan u → a.", f"(u − a)/(u³ − a³) = 1/(u² + au + a²).", f"Di u = a: 1/(3a²) = <b>{n(val)}</b>."],
            "explanation": "Substitusi variabel mengubah akar menjadi polinom."}


# ════════════════════════ Topik 3: Limit di tak hingga & asimtot ═══════════
@register("lim.inf_dasar", I, (1, 2))
def inf_dasar(rng, tier):
    a, k = nz(rng, -9, 9), nz(rng, -9, 9)
    p = rng.randint(1, 3)
    if tier == 1:
        prompt, val = f"Hitung lim<sub>x→∞</sub> ({n(a)} + {n(k)}/x{sup(p) if p > 1 else ''}).", a
        steps = ["Untuk x → ∞, k/xᵖ → 0 (p &gt; 0).", f"Limit = {n(a)} + 0 = <b>{n(a)}</b>."]
    else:
        prompt, val = f"Hitung lim<sub>x→−∞</sub> ({n(k)}/x{sup(p) if p > 1 else ''} − {paren(a)}).", -a
        steps = ["Untuk x → −∞, k/xᵖ → 0 juga.", f"Limit = 0 − {paren(a)} = <b>{n(-a)}</b>."]
    return {"prompt": prompt, "correct": n(val), "distractors": [n(val + k), "∞", "0" if val else "1", n(-val) if val else "−1"], "steps": steps,
            "explanation": "lim 1/xᵖ = 0 untuk x → ±∞ (p > 0)."}


@register("lim.rasional_inf", I, (1, 2, 3))
def rasional_inf(rng, tier):
    a, c = nz(rng, -6, 6), nz(rng, -6, 6)
    b, d = rng.randint(-9, 9), rng.randint(-9, 9)
    case = "sama" if tier == 1 else rng.choice(["sama", "kecil", "besar"])
    if case == "sama":
        num, den, val = poly([a, b, 1]), poly([c, d, 2]), Fr(a, c)
        why = f"Derajat pembilang = penyebut = 2 ⇒ limit = rasio koefisien utama {n(a)}/{n(c)}."
    elif case == "kecil":
        num, den, val = lin(a, b), poly([c, d, 1]), Fr(0)
        why = "Derajat pembilang (1) &lt; derajat penyebut (2) ⇒ limit = 0."
    else:
        num, den = poly([a, b, 0, 1]), poly([c, d])
        val = "∞" if a * c > 0 else f"{MINUS}∞"
        why = f"Derajat pembilang (3) &gt; penyebut (1) ⇒ tak hingga; tanda mengikuti {n(a)}/{n(c)}."
    correct = val if isinstance(val, str) else n(val)
    wrong = ["0", "∞", f"{MINUS}∞", n(Fr(b, d)) if d else "1", n(Fr(a, c)), "1"]
    return {"prompt": f"Hitung lim<sub>x→∞</sub> ({num}) / ({den}).", "correct": correct, "distractors": wrong,
            "steps": ["Bagi pembilang dan penyebut dengan pangkat tertinggi penyebut; suku k/xᵖ → 0.", why, f"Jawaban: <b>{correct}</b>."],
            "explanation": "Limit fungsi rasional di ∞ ditentukan oleh suku berderajat tertinggi."}


@register("lim.asimtot", I, (2, 3))
def asimtot(rng, tier):
    a, c = nz(rng, -5, 5), nz(rng, -3, 3)
    b, d = rng.randint(-6, 6), rng.randint(-6, 6)
    while a * d - b * c == 0:
        d += 1
    h, v = Fr(a, c), Fr(-d, c)
    correct = f"datar y = {n(h)}, tegak x = {n(v)}"
    return {"prompt": f"Tentukan asimtot datar dan asimtot tegak dari f(x) = ({lin(a, b)}) / ({lin(c, d)}).",
            "correct": correct,
            "distractors": [f"datar y = {n(v)}, tegak x = {n(h)}", f"datar y = {n(Fr(b, d)) if d else 0}, tegak x = {n(v)}",
                            f"datar y = {n(h)}, tegak x = {n(-v)}", f"datar y = 0, tegak x = {n(v)}"],
            "steps": [f"Asimtot datar: lim<sub>x→±∞</sub> f(x) = {n(a)}/{n(c)} = {n(h)}.",
                      f"Asimtot tegak: penyebut nol di x = {n(v)} (pembilang tidak nol di sana karena ad − bc ≠ 0).", f"Jawaban: <b>{correct}</b>."],
            "graphs": [g2d("Asimtot fungsi rasional", [float(v) - 8, float(v) + 8], [float(h) - 8, float(h) + 8],
                           [param("aa", "a", -5, 5, 0.5, a, "a")],
                           [fn(f"(aa*x+({b}))/({c}*x+({d}))", "blue", "f(x)"), {"type": "hline", "y": f"aa/{c}", "color": "red", "dash": True},
                            vline(float(v), "red")],
                           [readout("Asimtot datar a/c", f"aa/{c}", 3)], "Ubah a: asimtot datar bergeser, asimtot tegak tetap.")],
            "explanation": "f(x) = (ax + b)/(cx + d): asimtot datar y = a/c, tegak x = −d/c."}


@register("lim.akar_inf", I, (3, 4, 5))
def akar_inf(rng, tier):
    p, q = distinct(rng, -9, 9, 2)
    if tier == 5:
        val = Fr(p - q, 2)
        prompt = f"Hitung lim<sub>x→∞</sub> (√(x² {'+' if p >= 0 else MINUS} {abs(p)}x) − √(x² {'+' if q >= 0 else MINUS} {abs(q)}x))."
        steps = ["Kalikan sekawan: selisih akar = [(x² + px) − (x² + qx)] / (√(x² + px) + √(x² + qx)).",
                 "= (p − q)x / (√(x² + px) + √(x² + qx)); bagi dengan x: penyebut → 1 + 1 = 2.", f"Limit = (p − q)/2 = <b>{n(val)}</b>."]
        expr = f"sqrt(x*x+({p})*x)-sqrt(x*x+({q})*x)"
    else:
        a = rng.choice([1, 4, 9]) if tier == 4 else 1
        r = int(a ** 0.5)
        val = Fr(p, 2 * r)
        prompt = f"Hitung lim<sub>x→∞</sub> (√({'' if a == 1 else a}x² {'+' if p >= 0 else MINUS} {abs(p)}x) − {'' if r == 1 else r}x)."
        steps = ["Bentuk ∞ − ∞: kalikan sekawan.", f"= {n(p)}x / (√({a}x² + {paren(p)}x) + {r}x).",
                 f"Bagi dengan x: {n(p)}/(√{a} + {r}) = {n(p)}/{2 * r} = <b>{n(val)}</b>."]
        expr = f"sqrt({a}*x*x+({p})*x)-{r}*x"
    return {"prompt": prompt, "correct": n(val), "distractors": [n(Fr(p)), "0", "∞", n(val * 2 + 1)], "steps": steps,
            "graphs": [g2d("Selisih akar mendekati konstanta", [1, 200], [float(val) - 3, float(val) + 3],
                           [param("X", "x", 1, 200, 1, 20, "x")], [fn(expr, "blue", "f(x)", **{"from": 1}), hline(float(val), "red"),
                                                                    pt("X", expr.replace("x", "X"))],
                           [readout("f(x)", expr.replace("x", "X"), 6)], "Perbesar x: f(x) mendekati garis merah.")],
            "explanation": "∞ − ∞ dengan akar: kalikan sekawan agar menjadi bentuk ∞/∞."}


@register("lim.e", I, (4, 5))
def lim_e(rng, tier):
    a, b = nz(rng, -3, 3), rng.randint(1, 4)
    k = a * b
    correct = f"e{sup(k)}" if k != 1 else "e"
    return {"prompt": f"Hitung lim<sub>x→∞</sub> (1 + {n(a)}/x)<sup>{b}x</sup>.".replace("+ −", "− "),
            "correct": correct, "distractors": [f"e{sup(a)}" if a != k else "1", "1", "∞", f"e{sup(-k)}", f"e{sup(k + 1)}"],
            "steps": ["Limit standar: lim<sub>x→∞</sub> (1 + a/x)ˣ = eᵃ (Whitman §4.3, Stewart §3.6).",
                      f"(1 + {n(a)}/x)<sup>{b}x</sup> = [(1 + {n(a)}/x)ˣ]<sup>{b}</sup> → (e<sup>{a}</sup>)<sup>{b}</sup>.", f"= <b>{correct}</b>."],
            "graphs": [g2d("(1 + a/x)^(bx) menuju e^(ab)", [1, 100], [0, max(3.0, math.exp(k) * 1.4)],
                           [param("X", "x", 1, 100, 1, 10, "x")], [fn(f"pow(1+({a})/x,{b}*x)", "blue", "f(x)", **{"from": 1}),
                                                                     hline(math.exp(k), "red")],
                           [readout("f(x)", f"pow(1+({a})/X,{b}*X)", 6), readout("e^(ab)", f"exp({k})", 6)], "Bentuk 1^∞ adalah tak tentu: hasilnya e^(ab), bukan 1.")],
            "explanation": "1^∞ tak tentu; gunakan lim (1 + a/x)ˣ = eᵃ."}


# ════════════════════════ Topik 4: Limit trigonometri ══════════════════════
@register("lim.trig_substitusi", TR, (1, 2))
def trig_substitusi(rng, tier):
    deg = rng.choice([30, 45, 60, 90, 180]) if tier == 1 else rng.choice([120, 135, 150, 210, 270, 300])
    f1 = rng.choice(["sin", "cos"])
    val = exact(f1, deg)
    return {"prompt": f"Hitung lim<sub>x→{rad_text(deg)}</sub> {f1} x.", "correct": val,
            "distractors": [exact("cos" if f1 == "sin" else "sin", deg), "0" if val != "0" else "1", "tidak ada", f"{MINUS}{val}" if not val.startswith(MINUS) and val != "0" else "1/2"],
            "steps": ["sin dan cos kontinu di semua bilangan real ⇒ limit = nilai fungsi.", f"{f1}({rad_text(deg)}) = <b>{val}</b>."],
            "explanation": "Fungsi trigonometri kontinu di domainnya."}


@register("lim.sinx_x", TR, (1, 2, 3))
def sinx_x(rng, tier):
    a, b = nz(rng, -6, 6), nz(rng, 1, 6)
    if tier == 1:
        val, prompt = Fr(a, b), f"Hitung lim<sub>x→0</sub> sin({n(a)}x) / ({b}x)."
        steps = ["Limit dasar: lim<sub>u→0</sub> sin u / u = 1.", f"sin({n(a)}x)/({b}x) = ({n(a)}/{b})·sin({n(a)}x)/({n(a)}x) → {n(a)}/{b}.", f"= <b>{n(val)}</b>."]
        expr = f"sin({a}*x)/({b}*x)"
    elif tier == 2:
        val, prompt = Fr(a, b), f"Hitung lim<sub>x→0</sub> tan({n(a)}x) / sin({b}x)."
        steps = ["tan u / u → 1 dan sin u / u → 1 untuk u → 0.", f"tan({n(a)}x)/sin({b}x) = [tan({n(a)}x)/({n(a)}x)]·[({b}x)/sin({b}x)]·({n(a)}/{b}).", f"= <b>{n(val)}</b>."]
        expr = f"tan({a}*x)/sin({b}*x)"
    else:
        val, prompt = Fr(a * a, 2), f"Hitung lim<sub>x→0</sub> (1 − cos({n(a)}x)) / x²."
        steps = ["1 − cos u = 2 sin²(u/2).", f"(1 − cos({n(a)}x))/x² = 2[sin({n(a)}x/2)/x]² → 2·({n(a)}/2)².", f"= <b>{n(val)}</b>."]
        expr = f"(1-cos({a}*x))/(x*x)"
    return {"prompt": prompt, "correct": n(val), "distractors": [n(Fr(b, a)), "1", "0", n(val * 2)], "steps": steps,
            "graphs": [g2d("Mendekati 0 dari kedua sisi", [-2, 2], [float(val) - 3, float(val) + 3],
                           [param("d", "x", -1, 1, 0.005, 0.5, "x")], [fn(expr, "blue", "f(x)"), hline(float(val), "red"), pt("d", expr.replace("x", "d"))],
                           [readout("f(x)", expr.replace("x", "d"), 6)], "Nilai di x = 0 tidak terdefinisi, tetapi grafik menuju garis merah.")],
            "explanation": "lim sin x / x = 1 (x dalam radian) — Whitman §4.3 “A hard limit”."}


@register("lim.trig_campur", TR, (2, 3, 4, 5))
def trig_campur(rng, tier):
    a, b = nz(rng, 1, 7), nz(rng, 1, 7)
    if tier <= 3:
        val = Fr(a, b)
        prompt, expr = f"Hitung lim<sub>x→0</sub> sin({a}x) / sin({b}x).", f"sin({a}*x)/sin({b}*x)"
        steps = [f"Bagi pembilang dan penyebut dengan x: [sin({a}x)/x] / [sin({b}x)/x] → {a}/{b}.", f"= <b>{n(val)}</b>."]
    else:
        val = Fr(a, b * b)
        prompt, expr = f"Hitung lim<sub>x→0</sub> x·sin({a}x) / sin²({b}x).", f"x*sin({a}*x)/sin({b}*x)**2"
        steps = ["Tulis sebagai [sin(ax)/x]·[x/sin(bx)]².", f"→ {a}·(1/{b})².", f"= <b>{n(val)}</b>."]
    return {"prompt": prompt, "correct": n(val), "distractors": [n(Fr(b, a)), "1", "0", n(val + 1)], "steps": steps,
            "graphs": [g2d("Grafik dekat x = 0", [-1, 1], [float(val) - 2, float(val) + 2], [param("d", "x", -0.8, 0.8, 0.005, 0.4, "x")],
                           [fn(expr, "blue", "f(x)"), hline(float(val), "red"), pt("d", expr.replace("x", "d"))], [readout("f(x)", expr.replace("x", "d"), 6)],
                           "Titik merah mendekati garis limit.")],
            "explanation": "Pecah menjadi faktor-faktor bentuk sin u / u."}


@register("lim.trig_olim", TR, (4, 5))
def trig_olim(rng, tier):
    a = nz(rng, 1, 4)
    if tier == 4:
        b = nz(rng, 1, 4)
        val = Fr(a * a, 2 * b)
        prompt = f"Hitung lim<sub>x→0</sub> (1 − cos({a}x)) / (x·sin({b}x))."
        steps = ["1 − cos(ax) ≈ (ax)²/2 dan sin(bx) ≈ bx untuk x kecil (atau gunakan 2sin²).", f"→ ({a}²/2)x² / ({b}x²) = <b>{n(val)}</b>."]
    else:
        val = Fr(a ** 3, 2)
        prompt = f"Hitung lim<sub>x→0</sub> (tan({a}x) − sin({a}x)) / x³."
        steps = ["tan u − sin u = tan u (1 − cos u).", f"= [tan({a}x)/x]·[(1 − cos({a}x))/x²] → {a}·({a}²/2).", f"= <b>{n(val)}</b>."]
    return {"prompt": prompt, "correct": n(val), "distractors": [n(val * 2), "0", "1", n(Fr(a, 2))], "steps": steps,
            "explanation": "Gabungkan beberapa limit dasar: sin u/u → 1, (1 − cos u)/u² → 1/2."}


# ════════════════════════ Topik 5: Kekontinuan & pembuktian limit ══════════
@register("kont.titik", C, (1, 2))
def kont_titik(rng, tier):
    c = rng.randint(-4, 4)
    good = rng.choice([f"f(x) = {poly([1, -c, 2])}", f"f(x) = |{xm(c)}|", f"f(x) = ({lin(1, 1)}) / ({poly([1, 0, 1])})"])
    bad = [f"f(x) = 1 / {fac(c)}", f"f(x) = {fac(c)} / {fac(c)}", f"f(x) = ⌊x⌋ (bila {n(c)} bulat)", f"f(x) = √({lin(1, -c - 1)})" if tier == 2 else f"f(x) = ({poly([1, 0, -(c * c)])}) / {fac(c)}"]
    return {"prompt": f"Fungsi manakah yang <b>kontinu</b> di x = {n(c)}?", "correct": good, "distractors": bad,
            "steps": ["f kontinu di c ⇔ (1) f(c) terdefinisi, (2) lim<sub>x→c</sub> f(x) ada, (3) keduanya sama.",
                      f"1/(x − c) dan (x − c)/(x − c) tidak terdefinisi di c; ⌊x⌋ melompat di bilangan bulat; √(x − c − 1) tidak terdefinisi di c.",
                      f"Hanya <b>{good}</b> yang memenuhi ketiga syarat."],
            "explanation": "Tiga syarat kekontinuan: terdefinisi, limit ada, limit = nilai fungsi."}


@register("kont.piecewise", C, (1, 2, 3, 4, 5))
def kont_piecewise(rng, tier):
    c = rng.randint(-2, 3)
    if tier <= 3:
        a = nz(rng, -3, 3)
        e = rng.randint(-4, 4)
        k = Fr(c * c + e - (a * c if tier >= 2 else 0), 1)
        if tier == 1:
            prompt = f"Tentukan k agar f(x) = x² {'+' if e >= 0 else MINUS} {abs(e)} (x ≠ {n(c)}) dan f({n(c)}) = k kontinu di x = {n(c)}."
            k = Fr(c * c + e)
            steps = ["Kontinu di c ⇔ f(c) = lim<sub>x→c</sub> f(x).", f"lim = {n(c)}² + {paren(e)} = {n(k)} ⇒ <b>k = {n(k)}</b>."]
        else:
            prompt = (f"Tentukan k agar f(x) = {lin(a, 0)} + k (x &lt; {n(c)}) dan f(x) = x² {'+' if e >= 0 else MINUS} {abs(e)} (x ≥ {n(c)}) "
                      f"kontinu di x = {n(c)}.")
            steps = ["Kontinu di c ⇔ limit kiri = limit kanan = f(c).", f"{n(a * c)} + k = {n(c * c + e)} ⇒ <b>k = {n(k)}</b>."]
        return {"prompt": prompt, "correct": f"k = {n(k)}", "distractors": [f"k = {n(k + 1)}", f"k = {n(-k)}", f"k = {n(k + 2 * c)}", "tidak ada k"],
                "steps": steps, "explanation": "Kontinuitas fungsi sepotong-sepotong: samakan nilai di titik sambung."}
    # dua titik sambung: f = ax + b (x < 0), x² + 1 (0 ≤ x ≤ 1)? → gunakan c1 = 0, c2 = c2
    c2 = rng.randint(1, 3)
    m = rng.randint(-3, 3)
    # f = x² + m untuk x < 0 ; ax + b untuk 0 ≤ x < c2 ; x³ untuk x ≥ c2
    b = m
    a = Fr(c2 ** 3 - b, c2)
    correct = f"a = {n(a)}, b = {n(b)}"
    return {"prompt": f"f(x) = x² {'+' if m >= 0 else MINUS} {abs(m)} (x &lt; 0), f(x) = ax + b (0 ≤ x &lt; {c2}), f(x) = x³ (x ≥ {c2}). "
                      "Tentukan a dan b agar f kontinu di semua x.",
            "correct": correct, "distractors": [f"a = {n(b)}, b = {n(a)}", f"a = {n(a + 1)}, b = {n(b)}", f"a = {n(a)}, b = {n(-b)}", "tidak ada a, b"],
            "steps": [f"Di x = 0: lim kiri = 0 + {paren(m)} = {n(m)} = b.", f"Di x = {c2}: a·{c2} + b = {c2}³ = {c2 ** 3} ⇒ a = ({c2 ** 3} − {paren(b)})/{c2} = {n(a)}.",
                      f"Jawaban: <b>{correct}</b>."],
            "graphs": [g2d("Tiga potong yang harus bersambung", [-3, c2 + 2], [-6, 30], [param("aa", "a", float(a) - 5, float(a) + 5, 0.1, float(a) + 2, "a")],
                           [fn(f"x*x+({m})", "orange", **{"to": 0}), fn(f"aa*x+({b})", "blue", **{"from": 0, "to": c2}), fn("x**3", "green", **{"from": c2})],
                           [readout("a·c + b", f"aa*{c2}+({b})", 3), readout("c³", str(c2 ** 3), 3)], "Geser a sampai potongan biru menyambung dengan kurva hijau.")],
            "explanation": "Setiap titik sambung memberi satu persamaan."}


@register("kont.jenis", C, (2, 3))
def kont_jenis(rng, tier):
    c = nz(rng, -4, 4)
    d = rng.choice([v for v in range(-5, 6) if v != c])
    kind = rng.choice(["dapat dihapus", "loncat", "tak hingga"])
    if kind == "dapat dihapus":
        f = f"({xm(c)})({xm(d)}) / ({xm(c)})"
        why = f"Faktor (x − {n(c)}) dapat dicoret; limit ada ({n(c - d)}) tetapi f({n(c)}) tidak terdefinisi."
        expr = f"(x-({c}))*(x-({d}))/(x-({c}))"
    elif kind == "loncat":
        f = f"|{xm(c)}| / ({xm(c)})"
        why = "Limit kiri −1 dan limit kanan 1 berbeda (loncatan berhingga)."
        expr = f"abs(x-({c}))/(x-({c}))"
    else:
        f = f"1 / ({xm(c)})²"
        why = "f(x) → ∞ saat x → c (asimtot tegak)."
        expr = f"1/(x-({c}))**2"
    others = [k for k in ["dapat dihapus", "loncat", "tak hingga"] if k != kind] + ["f kontinu di x = c"]
    return {"prompt": f"Jenis diskontinuitas f(x) = {f} di x = {n(c)} adalah …", "correct": kind, "distractors": others,
            "steps": ["Dapat dihapus: limit ada tetapi ≠ f(c) atau f(c) tak terdefinisi. Loncat: limit kiri ≠ kanan (berhingga). "
                      "Tak hingga: limit sepihak ±∞.", why, f"Jawaban: <b>{kind}</b>."],
            "graphs": [g2d("Bentuk diskontinuitas", [c - 4, c + 4], [-6, 6], [], [fn(expr, "blue", "f(x)"), vline(c, "gray")], None,
                           "Perhatikan perilaku grafik di sekitar garis putus-putus x = c.")],
            "explanation": "Stewart §2.5: removable, jump, infinite discontinuity."}


@register("kont.tna", C, (3, 4))
def kont_tna(rng, tier):
    r = rng.choice([v + 0.5 for v in range(-4, 4)])
    # p(x) = a(x − r)(x² + 1) → akar tunggal r; pakai versi berkoefisien bulat dengan 2r
    co = [2, -2 * r * 1, 2, -2 * r]  # 2(x − r)(x² + 1)
    co = [int(c) for c in co]
    lo = int(r - 0.5)
    correct = f"[{n(lo)}, {n(lo + 1)}]"
    wrong = [f"[{n(lo + 1)}, {n(lo + 2)}]", f"[{n(lo - 1)}, {n(lo)}]", f"[{n(lo + 2)}, {n(lo + 3)}]", f"[{n(lo - 2)}, {n(lo - 1)}]"]
    return {"prompt": f"Menurut Teorema Nilai Antara, p(x) = {poly(co)} pasti memiliki akar di interval …",
            "correct": correct, "distractors": wrong,
            "steps": ["TNA: jika p kontinu di [a, b] dan p(a), p(b) berbeda tanda, maka ada c ∈ (a, b) dengan p(c) = 0.",
                      f"p({n(lo)}) = {n(ev(co, lo))} dan p({n(lo + 1)}) = {n(ev(co, lo + 1))} berbeda tanda.", f"Jadi akar ada di <b>{correct}</b>."],
            "graphs": [g2d("Tanda p(a) dan p(b) berbeda ⇒ grafik memotong sumbu-x", [lo - 3, lo + 4], [-30, 30],
                           [param("a", "a", lo - 3, lo + 3, 1, lo, "a")],
                           [fn(js_poly(co), "blue", "p(x)"), hline(0), pt("a", js_poly(co).replace("x", "a")), pt("a+1", js_poly(co).replace("x", "(a+1)"), "orange")],
                           [readout("p(a)", js_poly(co).replace("x", "a"), 3), readout("p(a + 1)", js_poly(co).replace("x", "(a+1)"), 3)],
                           "Geser a: cari interval dengan titik merah dan oranye di sisi berbeda sumbu-x.")],
            "explanation": "TNA menjamin keberadaan akar, tidak menghitung nilainya (gunakan bisection/Newton)."}


@register("kont.epsilon_delta", C, (4, 5))
def epsilon_delta(rng, tier):
    if tier == 4:
        m = nz(rng, -6, 6)
        b, c = rng.randint(-5, 5), rng.randint(-3, 3)
        eps = Fr(rng.choice([1, 1, 3, 1]), rng.choice([10, 100, 20]))
        delta = eps / abs(m)
        L = m * c + b
        return {"prompt": f"Pada bukti ε–δ untuk lim<sub>x→{n(c)}</sub> ({lin(m, b)}) = {n(L)}, berapa δ terbesar yang menjamin "
                          f"|f(x) − {n(L)}| &lt; ε untuk ε = {n(eps)}?",
                "correct": f"δ = {n(delta)}", "distractors": [f"δ = {n(eps * abs(m))}", f"δ = {n(eps)}", f"δ = {n(delta / 2)}", f"δ = {n(eps + abs(m))}"],
                "steps": [f"|f(x) − L| = |{lin(m, b)} − {paren(L)}| = |{n(m)}|·|x − {paren(c)}|.",
                          f"Agar &lt; ε perlu |x − c| &lt; ε/|m| = {n(eps)}/{abs(m)}.", f"δ terbesar = <b>{n(delta)}</b>."],
                "graphs": [g2d("Pita ε (merah) dan pita δ (hijau)", [c - 2, c + 2], [L - 3 * abs(m), L + 3 * abs(m)],
                               [param("eps", "ε", 0.05, 2, 0.05, max(0.1, float(eps) * 10), "ε")],
                               [fn(f"{m}*x+({b})", "blue", "f"), {"type": "hband", "from": f"{L}-eps", "to": f"{L}+eps", "color": "red"},
                                {"type": "vband", "from": f"{c}-eps/{abs(m)}", "to": f"{c}+eps/{abs(m)}", "color": "green"}],
                               [readout("δ = ε/|m|", f"eps/{abs(m)}", 4)], "Setiap x di pita hijau menghasilkan f(x) di pita merah.")],
                "explanation": "Definisi: ∀ε > 0 ∃δ > 0 sehingga 0 < |x − c| < δ ⇒ |f(x) − L| < ε."}
    c = rng.randint(1, 4)
    eps = Fr(1, rng.choice([10, 100]))
    delta = min(Fr(1), eps / (2 * c + 1))
    return {"prompt": f"Bukti lim<sub>x→{c}</sub> x² = {c * c} memakai δ = min(1, ε/(2·{c} + 1)). Berapa δ untuk ε = {n(eps)}?",
            "correct": f"δ = {n(delta)}", "distractors": [f"δ = {n(eps / (2 * c))}", f"δ = {n(eps)}", "δ = 1", f"δ = {n(eps / (c * c))}"],
            "steps": [f"|x² − {c * c}| = |x − {c}|·|x + {c}|.", f"Batasi |x − {c}| &lt; 1 ⇒ |x + {c}| &lt; 2·{c} + 1 = {2 * c + 1}.",
                      f"Maka |x² − {c * c}| &lt; {2 * c + 1}·|x − {c}| &lt; ε bila |x − {c}| &lt; ε/{2 * c + 1}.",
                      f"δ = min(1, {n(eps)}/{2 * c + 1}) = <b>{n(delta)}</b>."],
            "explanation": "Untuk fungsi nonlinear, batasi dulu δ ≤ 1 agar faktor |x + c| terbatas (Stewart §2.4)."}
