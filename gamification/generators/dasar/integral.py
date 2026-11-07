"""
Sub-level: Integral Tentu & Tak Tentu (Level Utama 2 — Kalkulus Dasar).
Rujukan: Stewart §4.9, §5.1–5.5; Whitman Bab 7, §8.1; Strang (MIT) Bab 5.
"""

from fractions import Fraction as Fr
import math

from .. import register
from ..fmt import MINUS, lin, n, paren, poly, sup
from ..graphs import fn, g2d, hline, param, pt, readout
from ..precalc.common import distinct, nz
from .limit import ev, js_poly

AT, RM, TT, TD, SB = "kd-int-antiturunan", "kd-int-riemann", "kd-int-tentu", "kd-int-tdk", "kd-int-substitusi"


def ipoly(co):
    """Koefisien antiturunan polinom (konstanta integrasi 0)."""
    deg = len(co) - 1
    return [Fr(c, deg - i + 1) for i, c in enumerate(co)] + [0]


def defint(co, a, b):
    F = ipoly(co)
    return ev(F, Fr(b)) - ev(F, Fr(a))


def area_spec(title, expr, a, b, caption, lower="0", xr=None, yr=None):
    xr = xr or [a - 2, b + 2]
    return g2d(title, xr, yr or [-10, 20], [param("bb", "Batas atas b", a, b + 2, 0.05, b, "b")],
               [{"type": "fill", "upper": expr, "lower": lower, "from": a, "to": "bb", "color": "amber"}, fn(expr, "blue", "f(x)")]
               + ([fn(lower, "green", "g(x)")] if lower != "0" else []),
               None, caption)


# ════════════════════════ Topik 1: Antiturunan ═════════════════════════════
@register("int.rumus", AT, (1,))
def rumus(rng, tier):
    m = rng.randint(2, 9)
    a = nz(rng, -5, 5)
    correct = f"{n(Fr(a, m + 1))}x{sup(m + 1)} + C"
    return {"prompt": f"Tentukan ∫ {n(a)}x{sup(m)} dx.", "correct": correct,
            "distractors": [f"{n(a * m)}x{sup(m - 1)} + C", f"{n(Fr(a, m))}x{sup(m + 1)} + C", f"{n(Fr(a, m + 1))}x{sup(m + 1)}", f"{n(a)}x{sup(m + 1)} + C"],
            "steps": ["∫ xⁿ dx = xⁿ⁺¹/(n + 1) + C (n ≠ −1).", f"∫ {n(a)}x{sup(m)} dx = {n(a)}·x{sup(m + 1)}/{m + 1} + C = <b>{correct}</b>.",
                      "Jangan lupa + C: setiap fungsi yang berbeda konstanta punya turunan yang sama."],
            "explanation": "Antiturunan membalik turunan; cek dengan menurunkan hasilnya."}


@register("int.pangkat", AT, (1, 2, 3, 4, 5))
def pangkat(rng, tier):
    if tier <= 2:
        deg = 2 if tier == 1 else 3
        res = [nz(rng, -3, 3)] + [rng.randint(-4, 4) for _ in range(deg)]
        co = [c * (deg - i + 1) for i, c in enumerate(res)]   # integran = turunan dari res·x
        F = res + [0]
        correct = f"{poly(F)} + C"
        prompt = f"Tentukan ∫ ({poly(co)}) dx."
        steps = ["Integralkan suku demi suku: ∫ axⁿ dx = a·xⁿ⁺¹/(n + 1).", f"Hasil: <b>{correct}</b>.", "Cek: turunkan hasil, harus kembali ke integran."]
        wrong = [f"{poly([c * (deg - i) for i, c in enumerate(co[:-1])])} + C", f"{poly(F)}", f"{poly([c for c in co] + [0])} + C", f"{poly([-c for c in F])} + C"]
        graph = g2d("Keluarga antiturunan F(x) + C", [-3, 3], [-20, 20], [param("C", "C", -10, 10, 0.5, 0, "C")],
                    [fn(js_poly(co), "orange", "integran f"), fn(js_poly(F) + "+C", "blue", "F(x) + C")], None,
                    "Mengubah C hanya menggeser F naik-turun; kemiringannya tetap sama dengan f.")
    elif tier == 3:
        a, b = nz(rng, -4, 4), nz(rng, -4, 4)
        correct = f"{n(Fr(2 * a, 3))}x√x {MINUS} {n(b)}/x + C".replace(f"{MINUS} {MINUS}", "+ ")
        prompt = f"Tentukan ∫ ({n(a)}√x + {n(b)}/x²) dx.".replace("+ −", "− ")
        steps = ["√x = x<sup>1/2</sup>, 1/x² = x<sup>−2</sup>.", f"∫ {n(a)}x<sup>1/2</sup> dx = {n(Fr(2 * a, 3))}x<sup>3/2</sup> = {n(Fr(2 * a, 3))}x√x.",
                 f"∫ {n(b)}x<sup>−2</sup> dx = −{paren(b)}x<sup>−1</sup>.", f"<b>{correct}</b>."]
        wrong = [f"{n(Fr(a, 2))}/√x + {n(b)}/x + C", f"{n(Fr(3 * a, 2))}x√x − {n(b)}/x + C", f"{n(Fr(2 * a, 3))}x√x + {n(b)}/x + C", f"{n(a)}x√x − {n(b)}/x³ + C"]
        graph = None
    else:
        a = nz(rng, -4, 4) if tier == 5 else nz(rng, 1, 5)
        correct = f"x³/3 + {n(2 * a)}x {MINUS} {n(a * a)}/x + C".replace("+ −", "− ")
        prompt = f"Tentukan ∫ (x² {'+' if a > 0 else MINUS} {abs(a)})² / x² dx."
        steps = [f"Uraikan dulu: (x² + {paren(a)})²/x² = x² + {n(2 * a)} + {a * a}/x².", f"∫ = x³/3 + {n(2 * a)}x − {a * a}/x + C.", f"<b>{correct}</b>."]
        wrong = [f"(x² + {paren(a)})³/(3x²) + C", f"x³/3 + {n(2 * a)}x + {n(a * a)}/x + C", f"x³/3 + {n(a * a)}/x + C", f"x³ + {n(2 * a)}x − {n(a * a)}/x + C"]
        graph = None
    return {"prompt": prompt, "correct": correct, "distractors": wrong, "steps": steps, "graphs": [graph] if graph else [],
            "explanation": "Tidak ada ‘aturan perkalian’ untuk integral: uraikan bentuknya dulu."}


@register("int.trig_eksp", AT, (2, 3))
def trig_eksp(rng, tier):
    a, b, c = nz(rng, -5, 5), nz(rng, -5, 5), nz(rng, 1, 4)
    if tier == 2:
        correct = f"{n(a)} sin x + {n(b)}eˣ + C".replace("+ −", "− ")
        prompt = f"Tentukan ∫ ({n(a)} cos x + {n(b)}eˣ) dx.".replace("+ −", "− ")
        wrong = [f"{n(-a)} sin x + {n(b)}eˣ + C", f"{n(a)} sin x + {n(b)}eˣ⁺¹ + C", f"{n(-a)} cos x + {n(b)}eˣ + C", f"{n(a)} sin x + {n(b)}xeˣ + C"]
        steps = ["∫ cos x dx = sin x, ∫ eˣ dx = eˣ.", f"<b>{correct}</b>."]
    else:
        correct = f"{n(Fr(-a, c))} cos({c}x) + C"
        prompt = f"Tentukan ∫ {n(a)} sin({c}x) dx."
        wrong = [f"{n(Fr(a, c))} cos({c}x) + C", f"{n(-a * c)} cos({c}x) + C", f"{n(Fr(a, c))} sin({c}x) + C", f"{n(-a)} cos({c}x) + C"]
        steps = ["∫ sin(kx) dx = −cos(kx)/k + C (cek: turunan −cos(kx)/k adalah sin(kx)).", f"<b>{correct}</b>."]
    return {"prompt": prompt, "correct": correct, "distractors": wrong, "steps": steps, "explanation": "Tabel integral dasar = tabel turunan dibaca terbalik."}


@register("int.syarat_awal", AT, (2, 3, 4))
def syarat_awal(rng, tier):
    res = [nz(rng, -2, 2), rng.randint(-4, 4), rng.randint(-5, 5), rng.randint(-6, 6)]
    if tier == 2:
        res = res[1:]
    d = res[-1]
    deriv = [c * (len(res) - 1 - i) for i, c in enumerate(res[:-1])]
    k = rng.randint(1, 3)
    val = ev(res, k)
    return {"prompt": f"Diketahui F′(x) = {poly(deriv)} dan F(0) = {n(d)}. Hitung F({k}).", "correct": n(val),
            "distractors": [n(val - d), n(ev(deriv, k)), n(val + d), n(val + 1)],
            "steps": [f"F(x) = ∫ ({poly(deriv)}) dx = {poly(res[:-1] + [0])} + C.", f"F(0) = C = {n(d)}.", f"F({k}) = <b>{n(val)}</b>."],
            "explanation": "Syarat awal menentukan konstanta integrasi C."}


@register("int.gerak", AT, (4, 5))
def gerak(rng, tier):
    v0, s0, T = rng.randint(-5, 10), rng.randint(0, 20), rng.randint(1, 5)
    if tier == 4:
        A = rng.choice([2, 4, 6, -2, -4, 10])
        val = s0 + v0 * T + Fr(A * T * T, 2)
        prompt = f"Benda bergerak dengan percepatan a(t) = {A} m/s², v(0) = {v0} m/s, s(0) = {s0} m. Tentukan posisi s({T})."
        steps = [f"v(t) = ∫ a dt = {A}t + {v0}.", f"s(t) = ∫ v dt = {n(Fr(A, 2))}t² + {v0}t + {s0}.", f"s({T}) = <b>{n(val)} m</b>."]
    else:
        k = rng.randint(1, 3)
        val = s0 + v0 * T + k * T ** 3
        prompt = f"Percepatan roket a(t) = {6 * k}t m/s², v(0) = {v0} m/s, s(0) = {s0} m. Tentukan s({T})."
        steps = [f"v(t) = {3 * k}t² + {v0}.", f"s(t) = {k}t³ + {v0}t + {s0}.", f"s({T}) = <b>{n(val)} m</b>."]
    return {"prompt": prompt, "correct": f"{n(val)} m", "distractors": [f"{n(val - s0)} m", f"{n(val + v0)} m", f"{n(s0 + v0 * T)} m", f"{n(val * 2)} m"],
            "steps": steps, "explanation": "Posisi = integral kecepatan, kecepatan = integral percepatan (Strang Bab 5)."}


# ════════════════════════ Topik 2: Sigma & jumlah Riemann ══════════════════
@register("int.notasi_sigma", RM, (1, 2))
def notasi_sigma(rng, tier):
    lo = rng.randint(1, 3)
    hi = lo + rng.randint(2, 4)
    if tier == 1:
        a, b = nz(rng, -4, 4), rng.randint(-5, 5)
        terms = [a * k + b for k in range(lo, hi + 1)]
        what = f"({lin(a, b, 'k')})"
    else:
        terms = [k * k for k in range(lo, hi + 1)]
        what = "k²"
    val = sum(terms)
    return {"prompt": f"Hitung Σ<sub>k={lo}</sub><sup>{hi}</sup> {what}.", "correct": n(val),
            "distractors": [n(val - terms[0]), n(val + terms[-1] + (terms[-1] - terms[-2])), n(len(terms) * terms[0]), n(val + 1)],
            "steps": [f"Tulis sukunya: {' + '.join(paren(t) for t in terms)}.", f"Jumlah = <b>{n(val)}</b>."],
            "explanation": "Σ dari k = m sampai n: jumlahkan suku untuk setiap k bulat."}


@register("int.sigma", RM, (1, 2, 3, 5))
def sigma(rng, tier):
    N = rng.randint(10, 100)
    if tier <= 2:
        a, b = nz(rng, -5, 5), rng.randint(-5, 5)
        val = a * N * (N + 1) // 2 + b * N
        prompt = f"Hitung Σ<sub>k=1</sub><sup>{N}</sup> ({lin(a, b, 'k')})."
        steps = ["Σk = n(n + 1)/2 dan Σ1 = n.", f"{n(a)}·{N}·{N + 1}/2 + {paren(b)}·{N} = <b>{n(val)}</b>."]
    elif tier == 3:
        N = rng.randint(5, 20)
        val = N * (N + 1) * (2 * N + 1) // 6 + N * (N + 1) // 2
        prompt = f"Hitung Σ<sub>k=1</sub><sup>{N}</sup> k(k + 1)."
        steps = ["k(k + 1) = k² + k.", "Σk² = n(n + 1)(2n + 1)/6, Σk = n(n + 1)/2.", f"= {N * (N + 1) * (2 * N + 1) // 6} + {N * (N + 1) // 2} = <b>{val}</b>."]
    else:
        val = Fr(N, N + 1)
        prompt = f"Hitung Σ<sub>k=1</sub><sup>{N}</sup> 1/(k(k + 1))."
        steps = ["1/(k(k + 1)) = 1/k − 1/(k + 1) (teleskopik).", f"Jumlah = 1 − 1/{N + 1} = <b>{n(val)}</b>."]
    return {"prompt": prompt, "correct": n(val), "distractors": [n(val + 1), n(val * 2), n(val - N), n(Fr(N - 1, N))], "steps": steps,
            "explanation": "Rumus jumlah baku diperlukan untuk menghitung limit jumlah Riemann."}


@register("int.riemann", RM, (2, 3, 4))
def riemann(rng, tier):
    L = rng.choice([2, 3, 4])
    N = rng.choice([2, 4]) if tier == 2 else rng.choice([4, 5, 6])
    mode = rng.choice(["right", "left"]) if tier < 4 else rng.choice(["right", "left", "mid"])
    dx = Fr(L, N)
    xs = {"right": [dx * k for k in range(1, N + 1)], "left": [dx * k for k in range(N)], "mid": [dx * k + dx / 2 for k in range(N)]}[mode]
    val = sum(x * x for x in xs) * dx
    exact = Fr(L ** 3, 3)
    name = {"right": "titik ujung kanan", "left": "titik ujung kiri", "mid": "titik tengah"}[mode]
    return {"prompt": f"Taksir ∫<sub>0</sub><sup>{L}</sup> x² dx dengan jumlah Riemann {N} persegi panjang ({name}).", "correct": n(val),
            "distractors": [n(exact), n(sum(x * x for x in xs)), n(val + dx), n(val * 2)],
            "steps": [f"Δx = {L}/{N} = {n(dx)}. Titik sampel: " + ", ".join(n(x) for x in xs) + ".",
                      f"Jumlah = Δx·Σf(xᵢ) = {n(dx)}·{n(sum(x * x for x in xs))} = <b>{n(val)}</b>.", f"Nilai eksak {n(exact)}; tambah n untuk taksiran lebih baik."],
            "graphs": [g2d("Jumlah Riemann untuk x²", [-0.2, L + 0.5], [-0.5, L * L + 1], [param("N", "Banyak persegi panjang n", 1, 40, 1, N, "n")],
                           [{"type": "riemann", "id": "R", "expr": "x*x", "from": 0, "to": L, "n": "N", "mode": mode, "color": "amber"}, fn("x*x", "blue", "x²")],
                           [readout("Jumlah Riemann", "R", 5), readout("Integral eksak", str(L ** 3 / 3), 5)],
                           "Perbanyak n: jumlah Riemann mendekati luas eksak (definisi integral tentu).")],
            "explanation": "∫ f dx = lim Σ f(xᵢ)Δx (Stewart §5.2)."}


@register("int.limit_riemann", RM, (3, 4, 5))
def limit_riemann(rng, tier):
    c, p = rng.randint(1, 3), rng.randint(1, 3) if tier < 5 else rng.randint(2, 4)
    val = Fr(c ** (p + 1), p + 1)
    cs = "" if c == 1 else str(c)
    return {"prompt": f"Hitung lim<sub>n→∞</sub> Σ<sub>k=1</sub><sup>n</sup> ({cs}{'/' if cs else '1/'}n)·({cs}k/n){sup(p)}.".replace("(/n)", "(1/n)"),
            "correct": n(val), "distractors": [n(Fr(c ** p, p)), n(Fr(1, p + 1)), n(c ** (p + 1)), "∞"],
            "steps": [f"Ini jumlah Riemann kanan dengan Δx = {c}/n dan xₖ = {c}k/n pada [0, {c}].", f"Limitnya = ∫<sub>0</sub><sup>{c}</sup> x{sup(p)} dx.",
                      f"= {c}{sup(p + 1)}/{p + 1} = <b>{n(val)}</b>."],
            "explanation": "Kenali Σ f(xₖ)Δx sebagai integral tentu."}


# ════════════════════════ Topik 3: Integral tentu & sifat ══════════════════
@register("int.geometri", TT, (1, 2))
def geometri(rng, tier):
    if tier == 1:
        m, c = rng.randint(0, 3), rng.randint(1, 5)
        a, b = 0, rng.randint(2, 6)
        val = Fr(m * b * b, 2) + c * b
        prompt = f"Hitung ∫<sub>0</sub><sup>{b}</sup> ({lin(m, c)}) dx dengan memandangnya sebagai luas."
        steps = [f"Daerah di bawah garis dari 0 sampai {b} berbentuk trapesium dengan sisi sejajar {c} dan {m * b + c}, tinggi {b}.",
                 f"Luas = ({c} + {m * b + c})/2 · {b} = <b>{n(val)}</b>."]
        corr = n(val)
        wrong = [n(val * 2), n((m * b + c) * b), n(c * b), n(val + 1)]
        graph = area_spec("Integral = luas trapesium", f"{m}*x+{c}", 0, b, "Geser b dan perhatikan luas berubah.")
    else:
        r = rng.randint(1, 6)
        val = Fr(r * r, 2)
        prompt = f"Hitung ∫<sub>{MINUS}{r}</sub><sup>{r}</sup> √({r * r} − x²) dx."
        steps = [f"y = √({r * r} − x²) adalah setengah lingkaran berjari-jari {r}.", f"Luas = πr²/2 = <b>{n(val)}π</b>."]
        corr = f"{n(val)}π"
        wrong = [f"{r * r}π", f"{n(Fr(r * r, 4))}π", f"{n(val)}", f"{2 * r}π"]
        graph = g2d("Setengah lingkaran", [-r - 1, r + 1], [-1, r + 1], [], [{"type": "fill", "upper": f"sqrt({r * r}-x*x)", "from": -r, "to": r, "color": "amber"},
                                                                           fn(f"sqrt({r * r}-x*x)", "blue")], None, "Integral = luas daerah berwarna.")
    return {"prompt": prompt, "correct": corr, "distractors": wrong, "steps": steps, "graphs": [graph],
            "explanation": "Integral tentu dari fungsi tak negatif = luas di bawah kurva."}


@register("int.tentu_poly", TT, (1, 2, 3))
def tentu_poly(rng, tier):
    deg = 1 if tier == 1 else 2
    co = [nz(rng, -3, 3)] + [rng.randint(-4, 4) for _ in range(deg)]
    if tier == 3:
        co = [nz(rng, -2, 2)] + [rng.randint(-3, 3) for _ in range(3)]
    a, b = sorted(distinct(rng, -2, 3, 2))
    val = defint(co, a, b)
    F = ipoly(co)
    return {"prompt": f"Hitung ∫<sub>{n(a)}</sub><sup>{n(b)}</sup> ({poly(co)}) dx.", "correct": n(val),
            "distractors": [n(ev(co, b) - ev(co, a)), n(-val), n(ev(F, Fr(b))), n(val + 1)],
            "steps": [f"Antiturunan: F(x) = {poly(F)}.", f"F({n(b)}) − F({n(a)}) = {n(ev(F, Fr(b)))} − {paren(ev(F, Fr(a)))} = <b>{n(val)}</b>."],
            "graphs": [area_spec("Luas bertanda (di bawah sumbu-x dihitung negatif)", js_poly(co), a, b,
                                 "Bagian di bawah sumbu-x mengurangi nilai integral.", xr=[a - 2, b + 2], yr=[-20, 20])],
            "explanation": "∫ₐᵇ f dx = F(b) − F(a) (soal U-D5 serupa)."}


@register("int.sifat", TT, (2, 3, 4))
def sifat(rng, tier):
    A_, B_ = rng.randint(-9, 12), rng.randint(-9, 12)
    if tier == 2:
        val = A_ - B_
        prompt = f"Diketahui ∫<sub>0</sub><sup>5</sup> f(x) dx = {A_} dan ∫<sub>0</sub><sup>2</sup> f(x) dx = {B_}. Hitung ∫<sub>2</sub><sup>5</sup> f(x) dx."
        steps = ["∫₀⁵ = ∫₀² + ∫₂⁵ (sifat penjumlahan interval).", f"∫₂⁵ = {A_} − {paren(B_)} = <b>{n(val)}</b>."]
    elif tier == 3:
        p, q = nz(rng, -3, 4), rng.randint(-3, 3)
        val = p * A_ + q * 4
        prompt = f"Diketahui ∫<sub>1</sub><sup>5</sup> f(x) dx = {A_}. Hitung ∫<sub>1</sub><sup>5</sup> ({n(p)}f(x) + {n(q)}) dx.".replace("+ −", "− ")
        steps = ["Linearitas: ∫(pf + q) = p∫f + q·(b − a).", f"{n(p)}·{paren(A_)} + {paren(q)}·4 = <b>{n(val)}</b>."]
    else:
        val = -(A_ + B_)
        prompt = (f"Diketahui ∫<sub>0</sub><sup>3</sup> f(x) dx = {A_} dan ∫<sub>3</sub><sup>7</sup> f(x) dx = {B_}. "
                  "Hitung ∫<sub>7</sub><sup>0</sup> f(x) dx.")
        steps = ["∫₀⁷ = ∫₀³ + ∫₃⁷.", f"Menukar batas mengubah tanda: ∫₇⁰ = −∫₀⁷ = −({A_} + {paren(B_)}) = <b>{n(val)}</b>."]
    return {"prompt": prompt, "correct": n(val), "distractors": [n(-val) if val else "1", n(A_ + B_), n(val + 1), n(A_ * B_)], "steps": steps,
            "explanation": "Sifat integral tentu: linear, aditif terhadap interval, ∫ₐᵇ = −∫ᵦᵃ."}


@register("int.mutlak", TT, (3, 4, 5))
def mutlak(rng, tier):
    if tier == 3:
        a, b = rng.randint(1, 6), rng.randint(1, 6)
        val = Fr(a * a + b * b, 2)
        prompt, expr, lo, hi = f"Hitung ∫<sub>{MINUS}{a}</sub><sup>{b}</sup> |x| dx.", "abs(x)", -a, b
        steps = ["|x| = −x untuk x &lt; 0, x untuk x ≥ 0: pecah di 0.", f"∫₋ₐ⁰ (−x) dx = {a * a}/2, ∫₀ᵇ x dx = {b * b}/2.", f"Total = <b>{n(val)}</b>."]
    elif tier == 4:
        b = rng.randint(3, 8)
        c = rng.randint(1, b - 1)
        val = Fr(c * c + (b - c) ** 2, 2)
        prompt, expr, lo, hi = f"Hitung ∫<sub>0</sub><sup>{b}</sup> |x − {c}| dx.", f"abs(x-{c})", 0, b
        steps = [f"Pecah di x = {c}: dua segitiga dengan alas {c} dan {b - c}.", f"Luas = {c}²/2 + {b - c}²/2 = <b>{n(val)}</b>."]
    else:
        c = rng.randint(1, 3)
        b = c + rng.randint(1, 3)
        val = Fr(2 * c ** 3, 3) + (Fr(b ** 3, 3) - c * c * b) - (Fr(c ** 3, 3) - c ** 3)
        prompt, expr, lo, hi = f"Hitung ∫<sub>0</sub><sup>{b}</sup> |x² − {c * c}| dx.", f"abs(x*x-{c * c})", 0, b
        steps = [f"x² − {c * c} &lt; 0 di [0, {c}) dan ≥ 0 di [{c}, {b}].", f"∫₀^{c} ({c * c} − x²) dx = {n(Fr(2 * c ** 3, 3))}.",
                 f"∫_{c}^{b} (x² − {c * c}) dx = {n(val - Fr(2 * c ** 3, 3))}.", f"Total = <b>{n(val)}</b>."]
    return {"prompt": prompt, "correct": n(val), "distractors": [n(val * 2), n(defint([1, 0], lo, hi) if tier == 3 else val - 1), n(val + 1), n(abs(val - 2))],
            "steps": steps, "graphs": [area_spec("Integral nilai mutlak = jumlah luas (semua positif)", expr, lo, hi, "Pecah interval di titik nol fungsi di dalam |…|.")],
            "explanation": "Integral |f|: pecah interval di titik saat f berganti tanda."}


@register("int.simetri", TT, (4, 5))
def simetri(rng, tier):
    a = rng.randint(1, 4)
    k = nz(rng, -5, 5)
    if tier == 4:
        o1, o2 = nz(rng, -4, 4), nz(rng, -4, 4)
        val = 2 * k * a + Fr(2 * a ** 3, 3)
        prompt = f"Hitung ∫<sub>{MINUS}{a}</sub><sup>{a}</sup> ({n(o1)}x⁵ + x² + {n(o2)}x³ + {n(k)}) dx.".replace("+ −", "− ")
        steps = ["Suku berpangkat ganjil adalah fungsi ganjil: integralnya pada [−a, a] = 0.", f"Sisa: 2∫₀^{a} (x² + {paren(k)}) dx = 2({a ** 3}/3 + {paren(k)}·{a}).",
                 f"= <b>{n(val)}</b>."]
    else:
        val = 2 * k * a
        prompt = f"Hitung ∫<sub>{MINUS}{a}</sub><sup>{a}</sup> (x³ cos x + {n(k)}) dx."
        steps = ["x³ cos x ganjil (ganjil × genap) ⇒ integralnya 0 pada interval simetris.", f"Sisa ∫ {n(k)} dx = {n(k)}·{2 * a} = <b>{n(val)}</b>."]
    return {"prompt": prompt, "correct": n(val), "distractors": [n(val * 2), "0", n(-val), n(k * a)], "steps": steps,
            "graphs": [g2d("Fungsi ganjil: luas kiri dan kanan saling menghapus", [-a - 1, a + 1], [-10, 10], [],
                           [{"type": "fill", "upper": "x**3*cos(x)", "from": -a, "to": a, "color": "amber"}, fn("x**3*cos(x)", "blue", "x³cos x")], None,
                           "Bagian di atas dan di bawah sumbu-x sama luas.")],
            "explanation": "f ganjil ⇒ ∫₋ₐᵃ f = 0; f genap ⇒ ∫₋ₐᵃ f = 2∫₀ᵃ f."}


# ════════════════════════ Topik 4: Teorema Dasar Kalkulus ══════════════════
@register("int.tdk_selisih", TD, (1, 2))
def tdk_selisih(rng, tier):
    Fa, Fb = rng.randint(-10, 20), rng.randint(-10, 20)
    a, b = sorted(distinct(rng, 0, 6, 2))
    val = Fb - Fa
    return {"prompt": f"F adalah antiturunan f dengan F({a}) = {n(Fa)} dan F({b}) = {n(Fb)}. Hitung ∫<sub>{a}</sub><sup>{b}</sup> f(x) dx.",
            "correct": n(val), "distractors": [n(Fa - Fb), n(Fa + Fb), n(Fr(val, b - a)), n(val + 1)],
            "steps": ["TDK bagian 2: ∫ₐᵇ f(x) dx = F(b) − F(a).", f"= {n(Fb)} − {paren(Fa)} = <b>{n(val)}</b>."],
            "explanation": "Cukup satu antiturunan; konstanta C saling menghapus."}


@register("int.tdk_eval", TD, (1, 2, 3))
def tdk_eval(rng, tier):
    k = rng.randint(2, 9)
    choice = rng.choice(["cos", "exp", "inv"]) if tier < 3 else "sin"
    if choice == "cos":
        a = nz(rng, -4, 4)
        val, prompt = Fr(a), f"Hitung ∫<sub>0</sub><sup>π/2</sup> {n(a)} cos x dx."
        steps = [f"Antiturunan {n(a)} sin x.", f"{n(a)}(sin(π/2) − sin 0) = <b>{n(a)}</b>."]
    elif choice == "exp":
        val, prompt = Fr(k - 1), f"Hitung ∫<sub>0</sub><sup>ln {k}</sup> eˣ dx."
        steps = ["Antiturunan eˣ.", f"e<sup>ln {k}</sup> − e⁰ = {k} − 1 = <b>{k - 1}</b>."]
    elif choice == "inv":
        m = rng.randint(1, 5)
        val, prompt = Fr(m), f"Hitung ∫<sub>1</sub><sup>e{sup(m)}</sup> (1/x) dx."
        steps = ["Antiturunan ln x.", f"ln e{sup(m)} − ln 1 = <b>{m}</b>."]
    else:
        a = nz(rng, 1, 5)
        val, prompt = Fr(2 * a), f"Hitung ∫<sub>0</sub><sup>π</sup> {a} sin x dx."
        steps = [f"Antiturunan −{a} cos x.", f"−{a}(cos π − cos 0) = −{a}(−1 − 1) = <b>{2 * a}</b>."]
    return {"prompt": prompt, "correct": n(val), "distractors": [n(-val), "0", n(val + 1), n(val * 2)], "steps": steps,
            "explanation": "TDK mengubah luas menjadi selisih nilai antiturunan."}


@register("int.tdk_turunan", TD, (2, 3, 4, 5))
def tdk_turunan(rng, tier):
    c = rng.randint(-5, 5)
    k = rng.randint(1, 3)
    if tier == 2:
        val = k * k + c
        prompt = f"Jika G(x) = ∫<sub>1</sub><sup>x</sup> (t² {'+' if c >= 0 else MINUS} {abs(c)}) dt, hitung G′({k})."
        steps = ["TDK bagian 1: d/dx ∫ₐˣ f(t) dt = f(x).", f"G′({k}) = {k}² + {paren(c)} = <b>{val}</b>."]
    elif tier == 3:
        val = (k ** 4 + c) * 2 * k
        prompt = f"Jika G(x) = ∫<sub>0</sub><sup>x²</sup> (t² {'+' if c >= 0 else MINUS} {abs(c)}) dt, hitung G′({k})."
        steps = ["Batas atas u = x²: G′(x) = f(x²)·2x (aturan rantai).", f"G′({k}) = ({k}⁴ + {paren(c)})·{2 * k} = <b>{val}</b>."]
    else:
        val = (k ** 3 + c) * 3 * k * k - (k + c)
        prompt = f"Jika G(x) = ∫<sub>x</sub><sup>x³</sup> (t {'+' if c >= 0 else MINUS} {abs(c)}) dt, hitung G′({k})."
        steps = ["G′(x) = f(x³)·3x² − f(x)·1.", f"G′({k}) = ({k ** 3} + {paren(c)})·{3 * k * k} − ({k} + {paren(c)}) = <b>{val}</b>."]
    return {"prompt": prompt, "correct": n(val), "distractors": [n(val + 1), n(-val), n(k * k + c) if tier > 2 else n(Fr(k ** 3, 3) + c * k), n(val * 2)],
            "steps": steps, "explanation": "d/dx ∫ₐ^{g(x)} f(t) dt = f(g(x))·g′(x)."}


@register("int.rata_rata", TD, (3, 4))
def rata_rata(rng, tier):
    a, c = nz(rng, -3, 3), rng.randint(-5, 5)
    b = rng.choice([3, 6]) if tier == 3 else rng.choice([2, 3, 4])
    val = Fr(a * b * b, 3) + c
    extra = " lalu tentukan c dengan f(c) = rata-rata (c &gt; 0)"
    return {"prompt": f"Tentukan nilai rata-rata f(x) = {poly([a, 0, c])} pada [0, {b}]" + (extra if tier == 4 else "") + ".",
            "correct": n(val) if tier == 3 else f"rata-rata {n(val)}, c² = {n(Fr(b * b, 3))}",
            "distractors": [n(val + c) if tier == 3 else f"rata-rata {n(val)}, c² = {n(Fr(b * b, 2))}", n(Fr(a * b * b + c, 2)) if tier == 3 else f"rata-rata {n(val * 2)}, c² = {n(Fr(b * b, 3))}",
                            n(a * b * b + c) if tier == 3 else f"rata-rata {n(val + 1)}, c² = {n(Fr(b * b, 3))}", n(val * 2) if tier == 3 else f"rata-rata {n(val)}, c² = {b}"],
            "steps": ["f̄ = (1/(b − a)) ∫ₐᵇ f(x) dx.", f"∫₀^{b} ({poly([a, 0, c])}) dx = {n(Fr(a * b ** 3, 3) + c * b)}.", f"f̄ = {n(Fr(a * b ** 3, 3) + c * b)}/{b} = <b>{n(val)}</b>."]
                     + ([f"f(c) = {n(a)}c² + {paren(c)} = {n(val)} ⇒ c² = {n(Fr(b * b, 3))} (Teorema Nilai Rata-rata untuk integral)."] if tier == 4 else []),
            "graphs": [g2d("Persegi panjang setinggi rata-rata punya luas sama", [-0.5, b + 0.5], [-10, 25], [],
                           [{"type": "fill", "upper": f"{a}*x*x+({c})", "from": 0, "to": b, "color": "amber"},
                            {"type": "hline", "y": float(val), "color": "red", "dash": True}, fn(f"{a}*x*x+({c})", "blue", "f")],
                           None, "Garis merah = nilai rata-rata f̄.")],
            "explanation": "Nilai rata-rata = integral dibagi panjang interval (Strang §5.6)."}


@register("int.tdk_fungsi", TD, (4, 5))
def tdk_fungsi(rng, tier):
    a = rng.randint(-4, 4)
    k = rng.randint(1, 3)
    if tier == 4:
        val = 3 * k * k + 2 * a * k
        prompt = f"Fungsi kontinu f memenuhi ∫<sub>0</sub><sup>x</sup> f(t) dt = x³ {'+' if a >= 0 else MINUS} {abs(a)}x² untuk semua x. Hitung f({k})."
        steps = ["Turunkan kedua ruas (TDK 1): f(x) = 3x² + 2·{}x.".format(paren(a)), f"f({k}) = <b>{val}</b>."]
    else:
        m = rng.randint(3, 5)
        val = m * k ** (m - 2)
        prompt = f"Fungsi kontinu f memenuhi ∫<sub>0</sub><sup>x</sup> t·f(t) dt = x{sup(m)} untuk semua x. Hitung f({k})."
        steps = [f"Turunkan: x·f(x) = {m}x{sup(m - 1)}.", f"f(x) = {m}x{sup(m - 2)} (x ≠ 0).", f"f({k}) = <b>{val}</b>."]
    return {"prompt": prompt, "correct": n(val), "distractors": [n(val + 1), n(k ** 3 + a * k * k), n(val * 2), n(val - k)], "steps": steps,
            "explanation": "Persamaan integral diselesaikan dengan menurunkan kedua ruas."}


# ════════════════════════ Topik 5: Substitusi & luas daerah ════════════════
@register("int.luas_linear", SB, (1, 2))
def luas_linear(rng, tier):
    m, c = rng.randint(1, 4), rng.randint(0, 6)
    a, b = sorted(distinct(rng, 0, 6, 2))
    val = defint([m, c], a, b)
    return {"prompt": f"Hitung luas daerah di bawah y = {lin(m, c)} di atas sumbu-x dari x = {a} sampai x = {b}.", "correct": n(val),
            "distractors": [n(val * 2), n((m * b + c) * (b - a)), n(val + c), n(Fr(m * (b - a), 2))],
            "steps": [f"Luas = ∫<sub>{a}</sub><sup>{b}</sup> ({lin(m, c)}) dx.", f"[{n(Fr(m, 2))}x² + {c}x] dari {a} ke {b} = <b>{n(val)}</b>."],
            "graphs": [area_spec("Luas di bawah garis", f"{m}*x+{c}", a, b, "Bandingkan dengan rumus luas trapesium.")],
            "explanation": "Luas di atas sumbu-x = integral tentu."}


@register("int.substitusi", SB, (1, 2, 3))
def substitusi(rng, tier):
    a, b = nz(rng, 1, 4), rng.randint(1, 5)
    m = rng.randint(2, 5)
    if tier <= 2:
        correct = f"({poly([a, 0, b])}){sup(m + 1)}/{m + 1} + C"
        prompt = f"Tentukan ∫ {2 * a}x({poly([a, 0, b])}){sup(m)} dx."
        steps = [f"Misal u = {poly([a, 0, b])} ⇒ du = {2 * a}x dx.", f"∫ u{sup(m)} du = u{sup(m + 1)}/{m + 1} + C.", f"<b>{correct}</b>."]
        wrong = [f"({poly([a, 0, b])}){sup(m + 1)} + C", f"{2 * a}x({poly([a, 0, b])}){sup(m + 1)}/{m + 1} + C",
                 f"({poly([a, 0, b])}){sup(m - 1)}/{m - 1} + C", f"({poly([a, 0, b])}){sup(m + 1)}/{(m + 1) * 2 * a} + C"]
    else:
        k = rng.randint(1, 2)
        u1 = a * k * k + b
        val = Fr(u1 ** (m + 1) - b ** (m + 1), m + 1)
        correct = n(val)
        prompt = f"Hitung ∫<sub>0</sub><sup>{k}</sup> {2 * a}x({poly([a, 0, b])}){sup(m)} dx."
        steps = [f"u = {poly([a, 0, b])}: x = 0 → u = {b}, x = {k} → u = {u1}.", f"∫<sub>{b}</sub><sup>{u1}</sup> u{sup(m)} du = [u{sup(m + 1)}/{m + 1}].",
                 f"({u1}{sup(m + 1)} − {b}{sup(m + 1)})/{m + 1} = <b>{correct}</b>."]
        wrong = [n(Fr(u1 ** (m + 1), m + 1)), n(val * 2), n(Fr(u1 ** m - b ** m, m)), n(val + 1)]
    return {"prompt": prompt, "correct": correct, "distractors": wrong, "steps": steps,
            "explanation": "Substitusi u = g(x), du = g′(x) dx — kebalikan aturan rantai (soal U-D6, U-S3 serupa)."}


@register("int.subst_trig", SB, (2, 3, 4, 5))
def subst_trig(rng, tier):
    m = rng.randint(1, 6)
    if tier <= 3:
        correct = f"sin{sup(m + 1)}x/{m + 1} + C"
        prompt = f"Tentukan ∫ sin{sup(m) if m > 1 else ''}x · cos x dx."
        steps = ["u = sin x, du = cos x dx.", f"∫ u{sup(m)} du = u{sup(m + 1)}/{m + 1} + C ⇒ <b>{correct}</b>."]
        wrong = [f"cos{sup(m + 1)}x/{m + 1} + C", f"−sin{sup(m + 1)}x/{m + 1} + C", f"sin{sup(m - 1) if m > 1 else '⁰'}x·{m} + C", f"sin{sup(m + 1)}x + C"]
    elif tier == 4:
        val = Fr(1, m + 1)
        correct = n(val)
        prompt = f"Hitung ∫<sub>0</sub><sup>π/2</sup> sin{sup(m) if m > 1 else ''}x · cos x dx."
        steps = ["u = sin x: batas 0 → 0, π/2 → 1.", f"∫₀¹ u{sup(m)} du = <b>{correct}</b>."]
        wrong = [n(Fr(1, m)), "1", "0", n(Fr(m, m + 1))]
    else:
        val = Fr(1, m + 1)
        correct = n(val)
        prompt = f"Hitung ∫<sub>0</sub><sup>π/4</sup> tan{sup(m) if m > 1 else ''}x · sec²x dx."
        steps = ["u = tan x, du = sec²x dx: batas 0 → 0, π/4 → 1.", f"∫₀¹ u{sup(m)} du = <b>{correct}</b>."]
        wrong = [n(Fr(1, m)), "1", "π/4", n(Fr(m, m + 1))]
    return {"prompt": prompt, "correct": correct, "distractors": wrong, "steps": steps, "explanation": "Cari fungsi yang turunannya juga muncul sebagai faktor."}


@register("int.luas_parabola", SB, (2, 3, 4))
def luas_parabola(rng, tier):
    p, q = sorted(distinct(rng, -4, 5, 2))
    k = 1 if tier < 4 else rng.choice([2, 3])
    val = Fr(k * (q - p) ** 3, 6)
    co = [-k, k * (p + q), -k * p * q]
    return {"prompt": f"Hitung luas daerah yang dibatasi parabola y = {poly(co)} dan sumbu-x.", "correct": n(val),
            "distractors": [n(val * 2), n(Fr((q - p) ** 3, 3)), n(val + 1), n(Fr(k * (q - p) ** 2, 2))],
            "steps": [f"Titik potong sumbu-x: {n(k) + '·' if k > 1 else ''}−(x − {paren(p)})(x − {paren(q)}) = 0 ⇒ x = {n(p)}, {n(q)}.",
                      f"Luas = ∫<sub>{n(p)}</sub><sup>{n(q)}</sup> ({poly(co)}) dx.", f"Rumus cepat k(q − p)³/6 = {k}·{q - p}³/6 = <b>{n(val)}</b>."],
            "graphs": [area_spec("Daerah di bawah parabola", js_poly(co), p, q, "Geser b untuk melihat luas terakumulasi.", yr=[-5, float(max(10, k * (q - p) ** 2 / 4 + 3))])],
            "explanation": "Luas parabola antara dua akarnya = |a|(q − p)³/6."}


@register("int.luas_dua_kurva", SB, (3, 4, 5))
def luas_dua_kurva(rng, tier):
    p, q = sorted(distinct(rng, -3, 4, 2))
    m, c = p + q, -p * q
    val = Fr((q - p) ** 3, 6)
    return {"prompt": f"Hitung luas daerah yang dibatasi y = x² dan y = {lin(m, c)}.", "correct": n(val),
            "distractors": [n(val * 2), n(Fr((q - p) ** 3, 3)), n(val + 1), n(defint([1, 0, 0], p, q))],
            "steps": [f"Titik potong: x² = {lin(m, c)} ⇒ (x − {paren(p)})(x − {paren(q)}) = 0 ⇒ x = {n(p)}, {n(q)}.",
                      f"Luas = ∫<sub>{n(p)}</sub><sup>{n(q)}</sup> [({lin(m, c)}) − x²] dx (garis di atas).", f"= ({q} − {paren(p)})³/6 = <b>{n(val)}</b>."],
            "graphs": [g2d("Luas di antara dua kurva", [p - 2, q + 2], [-2, max(q * q, p * p) + 4], [param("mm", "Gradien garis", m - 3, m + 3, 0.1, m, "m")],
                           [{"type": "fill", "upper": f"mm*x+({c})", "lower": "x*x", "from": f"(mm-sqrt(mm*mm+4*({c})))/2", "to": f"(mm+sqrt(mm*mm+4*({c})))/2", "color": "amber"},
                            fn("x*x", "blue", "x²"), fn(f"mm*x+({c})", "green", "garis")],
                           [readout("Luas (rumus d³/6)", f"pow(mm*mm+4*({c}),1.5)/6", 4)], "Ubah gradien garis: titik potong dan luas ikut berubah.")],
            "explanation": "Luas antara f dan g = ∫ (atas − bawah) dx (soal U-S5 serupa)."}
