"""
Topik: Fungsi Eksponensial — sifat, grafik & asimtot, persamaan, pertidaksamaan, pertumbuhan/peluruhan.
Rujukan: Stewart §1.4; Strang (MIT) §6.1–6.3; Whitman §4.6.
"""

from fractions import Fraction as Fr

from .. import register
from ..fmt import MINUS, interval, lin, n, paren, poly_in, sup
from ..graphs import fn, g2d, hline, param, pt, readout
from .common import distinct, nz

T = "pre-fungsi-eksponensial"


def exp_graph(title, a, b, k, caption, reads=None):
    return g2d(title, [-5, 5], [-6, 12],
               [param("a", "Pengali a", -4, 4, 0.25, float(a), "a"), param("bb", "Basis b", 0.2, 4, 0.05, float(b), "b"),
                param("k", "Geser vertikal k", -4, 4, 0.25, float(k), "k")],
               [fn("a*pow(bb,x)+k", "blue", "y = a·bˣ + k"), hline("k", "red"), pt(0, "a+k", label="(0, a + k)")],
               [readout("Asimtot y = k", "k", 2), readout("Titik potong sumbu-y", "a+k", 3)] + (reads or []), caption)


@register("exp.nilai", T, (1,))
def nilai(rng, tier):
    a, b = rng.choice([1, 2, 3, 5]), rng.choice([2, 3, 4, 5])
    x = rng.randint(-3, 3)
    val = a * Fr(b) ** x
    return {"prompt": f"Diketahui f(x) = {'' if a == 1 else a}·{b}ˣ".replace("·", "" if a == 1 else "·") + f". Hitung f({n(x)}).",
            "correct": n(val), "distractors": [n(a * b * x), n(-val) if x < 0 else n(a * Fr(b) ** (x + 1)), n((a * b) ** x if x >= 0 else Fr(1, (a * b) ** -x)),
                                               n(a * Fr(b) ** (-x))],
            "steps": [f"f({n(x)}) = {'' if a == 1 else str(a) + '·'}{b}{sup(x)}.",
                      "Pangkat negatif berarti kebalikan: b⁻ⁿ = 1/bⁿ." if x < 0 else "Pangkat 0 menghasilkan 1." if x == 0 else "Hitung pangkat dulu, baru kalikan dengan a.",
                      f"= <b>{n(val)}</b>."],
            "graphs": [exp_graph("Grafik eksponensial", a, b, 0, "Basis b > 1: naik; 0 < b < 1: turun. Grafik tidak pernah menyentuh asimtot y = k.",
                                 [readout(f"f({n(x)})", f"a*pow(bb,{x})+k", 4)])],
            "explanation": "aˣ⁺ʸ = aˣaʸ, a⁰ = 1, a⁻ⁿ = 1/aⁿ."}


@register("exp.persamaan", T, (1, 2, 3))
def persamaan(rng, tier):
    p = rng.choice([2, 3])
    m, nn = (1, 1) if tier == 1 else rng.choice([(2, 3), (3, 2), (2, 1), (1, 2), (3, 1)])
    if tier == 3:
        m = -m
    x0 = rng.randint(-4, 5)
    a, c = nz(rng, -3, 3), nz(rng, -3, 3)
    while m * a == nn * c:
        c = nz(rng, -3, 3)
    b = rng.randint(-5, 5)
    while (m * (a * x0 + b)) % nn:      # pilih b agar d bulat
        b += 1
    d = (m * (a * x0 + b)) // nn - c * x0
    B1 = p ** abs(m)
    B2 = p ** nn
    base1 = f"(1/{B1})" if m < 0 else str(B1)
    rhs = lin(c, d) if tier > 1 else str(d)
    lhs = lin(a, b)
    if tier == 1:
        x0 = Fr(d - b, a)
        prompt = f"Selesaikan {p}<sup>{lhs}</sup> = {p}<sup>{d}</sup>."
        steps = ["Basis sama ⇒ pangkat sama.", f"{lhs} = {d} ⇒ x = <b>{n(x0)}</b>."]
    else:
        prompt = f"Selesaikan {base1}<sup>{lhs}</sup> = {B2}<sup>{rhs}</sup>."
        steps = [f"Tulis dengan basis {p}: {base1} = {p}{sup(m)}, {B2} = {p}{sup(nn)}.",
                 f"{p}<sup>{m}({lhs})</sup> = {p}<sup>{nn}({rhs})</sup> ⇒ {m}({lhs}) = {nn}({rhs}).",
                 f"{lin(m * a, m * b)} = {lin(nn * c, nn * d)} ⇒ x = <b>{n(x0)}</b>."]
    return {"prompt": prompt, "correct": f"x = {n(x0)}",
            "distractors": [f"x = {n(-x0)}", f"x = {n(x0 + 1)}", f"x = {n(Fr(d - b, a) if a else x0 + 2)}", f"x = {n(x0 - 2)}"],
            "steps": steps,
            "graphs": [g2d("Kedua ruas sebagai fungsi x: titik potong = penyelesaian", [float(x0) - 4, float(x0) + 4], [-1, 40],
                           [param("s", "x uji", float(x0) - 3.5, float(x0) + 3.5, 0.05, float(x0) + 1, "x")],
                           [fn(f"pow({p},{m}*({a}*x+({b})))", "blue", "ruas kiri"),
                            fn(f"pow({p},{nn if tier > 1 else 1}*({c if tier > 1 else 0}*x+({d})))", "orange", "ruas kanan"),
                            pt("s", f"pow({p},{m}*({a}*s+({b})))")],
                           [readout("ruas kiri", f"pow({p},{m}*({a}*s+({b})))", 4),
                            readout("ruas kanan", f"pow({p},{nn if tier > 1 else 1}*({c if tier > 1 else 0}*s+({d})))", 4)],
                           "Geser x uji ke titik potong: kedua ruas bernilai sama.")],
            "explanation": "aᶠ⁽ˣ⁾ = aᵍ⁽ˣ⁾ (a > 0, a ≠ 1) ⇔ f(x) = g(x). Samakan basis dulu."}


@register("exp.sifat_grafik", T, (1, 2))
def sifat_grafik(rng, tier):
    a, b, k = nz(rng, -3, 3), rng.choice([2, 3, Fr(1, 2), Fr(1, 3), 4]), rng.randint(-4, 4)
    ask = rng.choice(["asimtot datar", "titik potong sumbu-y"]) if tier == 1 else rng.choice(["asimtot datar", "titik potong sumbu-y", "daerah hasil"])
    fx = f"{'' if a == 1 else (MINUS if a == -1 else n(a))}({n(b)})ˣ {'+' if k >= 0 else MINUS} {abs(k)}"
    if ask == "asimtot datar":
        correct, wrong = f"y = {n(k)}", [f"y = {n(a + k)}", f"y = 0", f"x = {n(k)}", f"y = {n(-k)}"]
        steps = ["bˣ → 0 untuk x → −∞ (b > 1) atau x → ∞ (0 < b < 1), tetapi tidak pernah 0.", f"Maka y → 0 + {paren(k)}: asimtot <b>{correct}</b>."]
    elif ask == "titik potong sumbu-y":
        correct, wrong = f"(0, {n(a + k)})", [f"(0, {n(k)})", f"(0, {n(a)})", f"({n(a + k)}, 0)", f"(0, {n(a * b + k)})"]
        steps = ["Titik potong sumbu-y: x = 0, dan b⁰ = 1.", f"y = {n(a)}·1 + {paren(k)} = {n(a + k)} ⇒ <b>{correct}</b>."]
    else:
        correct = interval(k, None, lo_closed=False) if a > 0 else interval(None, k, hi_closed=False)
        wrong = [interval(k, None) if a > 0 else interval(None, k), interval(None, k, hi_closed=False) if a > 0 else interval(k, None, lo_closed=False), "ℝ",
                 interval(a + k, None, lo_closed=False)]
        steps = ["bˣ &gt; 0 untuk semua x.", f"a = {n(a)} {'positif' if a > 0 else 'negatif'} ⇒ a·bˣ {'&gt;' if a > 0 else '&lt;'} 0.",
                 f"Ditambah {n(k)}: daerah hasil <b>{correct}</b> (k sendiri tidak pernah tercapai)."]
    return {"prompt": f"Tentukan {ask} dari grafik y = {fx}.", "correct": correct, "distractors": wrong, "steps": steps,
            "graphs": [exp_graph("y = a·bˣ + k", a, b, k, "Asimtot y = k (garis merah). Ubah a menjadi negatif: grafik tercermin terhadap asimtot.")],
            "explanation": "y = a·bˣ + k: asimtot datar y = k, titik potong y = a + k."}


@register("exp.pertumbuhan", T, (2, 3))
def pertumbuhan(rng, tier):
    if tier == 2:
        N0 = rng.choice([100, 200, 500, 1000])
        T2 = rng.choice([2, 3, 4, 5])
        k = rng.randint(2, 5)
        t = T2 * k
        val = N0 * 2 ** k
        prompt = f"Koloni bakteri (FMIPA) berjumlah {N0} dan berlipat dua setiap {T2} jam. Berapa jumlahnya setelah {t} jam?"
        correct = f"{val:,}".replace(",", ".")
        wrong = [f"{N0 * 2 * k:,}".replace(",", "."), f"{N0 * 2 ** t:,}".replace(",", ".") if t < 15 else f"{N0 * 3 ** k:,}".replace(",", "."),
                 f"{N0 * 2 ** (k - 1):,}".replace(",", "."), f"{N0 * k ** 2:,}".replace(",", ".")]
        steps = [f"Model: N(t) = N₀·2<sup>t/{T2}</sup>.", f"t/{T2} = {k} kali penggandaan.", f"N = {N0}·2{sup(k)} = <b>{correct}</b>."]
        expr, x1, y1 = f"{N0}*pow(2,x/{T2})", t * 1.3, val * 1.3
    else:
        m0 = rng.choice([80, 160, 320, 640])
        h = rng.choice([5, 8, 10, 12])
        k = rng.randint(2, 4)
        rem = Fr(m0, 2 ** k)
        prompt = f"Zat radioaktif bermassa {m0} gram memiliki waktu paruh {h} tahun. Setelah berapa tahun massanya tinggal {n(rem)} gram?"
        correct = f"{h * k} tahun"
        wrong = [f"{h * (k + 1)} tahun", f"{h * (k - 1)} tahun", f"{h * 2 ** k} tahun", f"{h + k} tahun"]
        steps = [f"m(t) = {m0}·(1/2)<sup>t/{h}</sup>.", f"{n(rem)}/{m0} = 1/{2 ** k} = (1/2){sup(k)} ⇒ t/{h} = {k}.", f"t = <b>{h * k} tahun</b>."]
        expr, x1, y1 = f"{m0}*pow(0.5,x/{h})", h * (k + 2), m0 * 1.1
    return {"prompt": prompt, "correct": correct, "distractors": wrong, "steps": steps,
            "graphs": [g2d("Pertumbuhan / peluruhan eksponensial", [0, x1], [0, y1],
                           [param("tt", "Waktu t", 0, x1, 0.1, x1 / 1.3 if tier == 2 else h * k, "t")],
                           [fn(expr, "blue", "model"), pt("tt", expr.replace("x", "tt"))],
                           [readout("Nilai saat t", expr.replace("x", "tt"), 4)],
                           "Setiap selang waktu yang sama, besaran dikali faktor yang sama (bukan ditambah).")],
            "explanation": "Eksponensial: laju perubahan sebanding dengan besaran itu sendiri (MIT §6.3)."}


@register("exp.substitusi", T, (3, 4))
def substitusi(rng, tier):
    p = rng.choice([2, 3])
    e1, e2 = distinct(rng, 0, 3, 2)
    r1, r2 = p ** e1, p ** e2
    if tier == 4:
        r2 = -rng.randint(1, 5)  # akar negatif ditolak
    S, P = r1 + r2, r1 * r2
    prompt = f"Selesaikan {poly_in([1, -S, P], f'{p}ˣ').replace(f'({p}ˣ)²', f'{p * p}ˣ')} = 0."
    sols = sorted([e for e, r in ((e1, r1), (e2, r2)) if r > 0])
    correct = "x = " + " atau x = ".join(n(s) for s in sols)
    wrong = [f"x = {n(r1)} atau x = {n(r2)}", f"x = {n(sols[0] + 1)}", "tidak ada penyelesaian", f"x = {n(e1)} atau x = {n(e2 if tier == 3 else -e2 - 1)}"]
    steps = [f"Misal u = {p}ˣ (&gt; 0): u² {MINUS if S > 0 else '+'} {abs(S)}u {'+' if P >= 0 else MINUS} {abs(P)} = 0.",
             f"(u − {paren(r1)})(u − {paren(r2)}) = 0 ⇒ u = {n(r1)} atau u = {n(r2)}."]
    if tier == 4:
        steps.append(f"u = {p}ˣ selalu positif, jadi u = {n(r2)} <b>ditolak</b>.")
    steps.append(f"{p}ˣ = {r1} ⇒ x = {e1}" + (f"; {p}ˣ = {r2} ⇒ x = {e2}" if tier == 3 else "") + f". Jawaban: <b>{correct}</b>.")
    return {"prompt": prompt, "correct": correct, "distractors": wrong, "steps": steps,
            "graphs": [g2d("Substitusi u = pˣ mengubah persamaan menjadi kuadrat", [-1, 6], [-10, 30],
                           [param("s", "x uji", -1, 4, 0.01, sols[0], "x")],
                           [fn(f"pow({p},2*x)-({S})*pow({p},x)+({P})", "blue", "ruas kiri"), hline(0), pt("s", f"pow({p},2*s)-({S})*pow({p},s)+({P})")],
                           [readout("u = pˣ", f"pow({p},s)", 4), readout("ruas kiri", f"pow({p},2*s)-({S})*pow({p},s)+({P})", 4)],
                           "Nilai nol ruas kiri = penyelesaian. Perhatikan u = pˣ tidak pernah negatif.")],
            "explanation": "Persamaan bentuk a·p²ˣ + b·pˣ + c = 0 diselesaikan dengan u = pˣ, ingat syarat u > 0."}


@register("exp.simetri", T, (4, 5))
def simetri(rng, tier):
    k = rng.randint(3, 7)
    if tier == 4:
        val, ask, form = k * k - 2, "4ˣ + 4⁻ˣ", "(2ˣ + 2⁻ˣ)² = 4ˣ + 2 + 4⁻ˣ"
        last = f"4ˣ + 4⁻ˣ = {k}² − 2 = <b>{k * k - 2}</b>."
    else:
        val, ask, form = k ** 3 - 3 * k, "8ˣ + 8⁻ˣ", "(2ˣ + 2⁻ˣ)³ = 8ˣ + 8⁻ˣ + 3(2ˣ + 2⁻ˣ)"
        last = f"8ˣ + 8⁻ˣ = {k}³ − 3·{k} = <b>{k ** 3 - 3 * k}</b>."
    return {"prompt": f"Jika 2ˣ + 2⁻ˣ = {k}, hitung {ask}.", "correct": n(val),
            "distractors": [n(k * k), n(k ** 3), n(val + 2), n(k * k + 2) if tier == 4 else n(k ** 3 - k)],
            "steps": ["Perhatikan 2ˣ · 2⁻ˣ = 1.", f"Gunakan {form}.", last],
            "explanation": "Kuadratkan/pangkatkan bentuk simetris u + 1/u untuk mendapatkan u² + 1/u² dan u³ + 1/u³."}


@register("exp.pertidaksamaan", T, (3, 4, 5))
def pertidaksamaan(rng, tier):
    small = tier >= 4 and rng.random() < 0.7
    base = rng.choice(["1/2", "1/3"]) if small else rng.choice(["2", "3"])
    bval = {"1/2": 0.5, "1/3": 1 / 3, "2": 2, "3": 3}[base]
    a, c = nz(rng, -4, 4), rng.randint(-5, 5)
    x0 = Fr(c, 1)
    op = rng.choice(["&gt;", "&lt;"])
    flip = small
    res = {"&gt;": "&lt;" if flip else "&gt;", "&lt;": "&gt;" if flip else "&lt;"}[op]
    x_op = res
    # (base)^(x − a) op (base)^c ⇒ x − a  res  c
    bound = c + a
    correct = interval(bound, None, lo_closed=False) if x_op == "&gt;" else interval(None, bound, hi_closed=False)
    wrong = [interval(None, bound, hi_closed=False) if x_op == "&gt;" else interval(bound, None, lo_closed=False),
             interval(c - a, None, lo_closed=False), interval(bound, None) if x_op == "&gt;" else interval(None, bound), interval(None, c, hi_closed=False)]
    return {"prompt": f"Selesaikan ({base})<sup>x {MINUS if a > 0 else '+'} {abs(a)}</sup> {op} ({base})<sup>{c}</sup>.",
            "correct": correct, "distractors": wrong,
            "steps": [f"Basis {base} {'di antara 0 dan 1 ⇒ fungsi turun, tanda dibalik' if flip else 'lebih dari 1 ⇒ fungsi naik, tanda tetap'}.",
                      f"x − {paren(a)} {res} {c} ⇒ x {res} {bound}.", f"Jawaban: <b>{correct}</b>."],
            "graphs": [g2d("y = bˣ: naik untuk b > 1, turun untuk 0 < b < 1", [-6, 6], [-1, 10],
                           [param("bb", "Basis b", 0.2, 3, 0.05, bval, "b")],
                           [fn("pow(bb,x)", "blue", "y = bˣ"), hline(1)],
                           [readout("b", "bb", 3)], "Geser b melewati 1: arah grafik berbalik, karena itu tanda pertidaksamaan juga berbalik.")],
            "explanation": "Untuk 0 < b < 1, bᵘ < bᵛ ⇔ u > v (tanda dibalik)."}
