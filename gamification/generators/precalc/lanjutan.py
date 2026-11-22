"""
Topik Level 1 kurikulum v2 yang semula hanya materi: fungsi invers, polinomial & fungsi rasional,
barisan & notasi sigma, serta pengantar vektor & matriks.
Rujukan: Stewart Lampiran & Bab 1; Whitman Bab 1; Strang (MIT) Bab 0–1.
"""

from fractions import Fraction as Fr
import math

from .. import attach, register
from ..fmt import MINUS, n, paren, poly, sqrt_simplify, sup, surd, terms
from .common import distinct, nz

INV, PR, SG, VM = "pre-fungsi-invers", "pre-polinomial-rasional", "pre-barisan-sigma", "pre-vektor-matriks"

attach(INV, "fn.invers")


def frac_lin(p, q, r, s, var="x"):
    """(px + q)/(rx + s) sebagai teks."""
    return f"({terms([(p, var)], q)})/({terms([(r, var)], s)})"


# ════════════════════════ Fungsi invers ═══════════════════════════════════
@register("inv.linear", INV, (1, 2, 3))
def inv_linear(rng, tier):
    a, b = nz(rng, -6, 6), rng.randint(-9, 9)
    while (a, b) == (1, 0):          # f(x) = x terlalu trivial
        b = rng.randint(-9, 9)
    f = terms([(a, "x")], b)
    inv = f"(x {MINUS} {b})/{paren(a)}" if b > 0 else f"(x + {-b})/{paren(a)}" if b < 0 else f"x/{paren(a)}"
    if a == 1:
        inv = terms([(1, "x")], -b)
    if tier <= 2:
        return {"prompt": f"Tentukan invers dari f(x) = {f}.", "correct": f"f⁻¹(x) = {inv}",
                "distractors": [f"f⁻¹(x) = {terms([(a, 'x')], -b)}", f"f⁻¹(x) = 1/({f})", f"f⁻¹(x) = x/{paren(a)} {'+' if b >= 0 else MINUS} {abs(b)}", f"f⁻¹(x) = (x + {b})/{paren(a)}".replace("+ −", "− ")],
                "steps": [f"Tulis y = {f}, lalu tukar peran: x = {terms([(a, 'y')], b)}.", f"Selesaikan untuk y: y = {inv}.", f"<b>f⁻¹(x) = {inv}</b>. Cek: f(f⁻¹(x)) = x."],
                "explanation": "Invers membalik kerja fungsi: ‘kali a lalu tambah b’ dibalik menjadi ‘kurangi b lalu bagi a’."}
    k = rng.randint(-10, 10)
    val = Fr(k - b, a)
    return {"prompt": f"f(x) = {f}. Hitung f⁻¹({n(k)}).", "correct": n(val),
            "distractors": [n(a * k + b), n(Fr(k + b, a)), n(-val), n(Fr(1, a * k + b)) if a * k + b else "0"],
            "steps": [f"f⁻¹({n(k)}) = x yang memenuhi f(x) = {n(k)}.", f"{f} = {n(k)} ⇒ x = ({n(k)} − {paren(b)})/{paren(a)}.", f"= <b>{n(val)}</b>."],
            "explanation": "f⁻¹(k) adalah input yang menghasilkan output k."}


@register("inv.rasional", INV, (3, 4, 5))
def inv_rasional(rng, tier):
    while True:
        p, q, r, s = nz(rng, -5, 5), rng.randint(-6, 6), nz(rng, -4, 4), rng.randint(-6, 6)
        if p * s - q * r != 0:
            break
    f = frac_lin(p, q, r, s)

    def norm(t):
        """Penyebut berkoefisien x positif (mengalikan atas & bawah dengan −1 tidak mengubah fungsi)."""
        return tuple(-v for v in t) if t[2] < 0 else t

    def same(t, u):
        """Dua pecahan linear sama ⇔ (p, q, r, s) sebanding."""
        return all(t[i] * u[j] == t[j] * u[i] for i in range(4) for j in range(4))

    good = norm((s, -q, -r, p))
    inv = frac_lin(*good)
    if tier <= 4:
        cands = [(r, s, p, q), (s, q, r, p), (s, -q, r, p), (p, -q, -r, s), (-s, -q, -r, p)]
        wrong = [f"f⁻¹(x) = {frac_lin(*norm(t))}" for t in cands if not same(t, good)]
        return {"prompt": f"Tentukan invers dari f(x) = {f}.", "correct": f"f⁻¹(x) = {inv}",
                "distractors": wrong,
                "steps": [f"y = {f} ⇒ y({terms([(r, 'x')], s)}) = {terms([(p, 'x')], q)}.", f"Kumpulkan x: x({terms([(r, 'y')], -p)}) = {terms([(-s, 'y')], q)}.",
                          f"Tukar x ↔ y: <b>f⁻¹(x) = {inv}</b>."],
                "explanation": "Invers (ax + b)/(cx + d) adalah (dx − b)/(−cx + a): tukar a ↔ d dan ubah tanda b, c."}
    k = rng.randint(-6, 6)
    while p - r * k == 0:
        k += 1
    val = Fr(s * k - q, p - r * k)
    return {"prompt": f"f(x) = {f}. Hitung f⁻¹({n(k)}).", "correct": n(val),
            "distractors": [n(Fr(p * k + q, r * k + s)) if r * k + s else "tidak terdefinisi", n(-val), n(Fr(s * k + q, p - r * k)), n(val + 1)],
            "steps": [f"Selesaikan {f} = {n(k)}.", f"{terms([(p, 'x')], q)} = {n(k)}({terms([(r, 'x')], s)}) ⇒ x({n(p - r * k)}) = {n(s * k - q)}.", f"x = <b>{n(val)}</b>."],
            "explanation": "f⁻¹(k) dicari langsung dari persamaan f(x) = k — tanpa harus menulis rumus f⁻¹."}


@register("inv.eksp", INV, (2, 3, 4, 5))
def inv_eksp(rng, tier):
    b, h, k = rng.choice([2, 3, 5, 10]), rng.randint(-4, 4), rng.randint(-5, 5)
    xh = "x" if h == 0 else f"x {MINUS} {h}" if h > 0 else f"x + {-h}"
    xk = "x" if k == 0 else f"x {MINUS} {k}" if k > 0 else f"x + {-k}"
    if rng.random() < 0.5:
        f = f"{b}<sup>{xh}</sup>" + (f" {'+' if k > 0 else MINUS} {abs(k)}" if k else "")
        inv = f"log<sub>{b}</sub>({xk})" + (f" {'+' if h > 0 else MINUS} {abs(h)}" if h else "")
        bad = [f"log<sub>{b}</sub>({xh})" + (f" {'+' if k > 0 else MINUS} {abs(k)}" if k else ""), f"{b}<sup>{xk}</sup>" + (f" {'+' if h > 0 else MINUS} {abs(h)}" if h else ""),
               f"log<sub>{b}</sub> x {'+' if k >= 0 else MINUS} {abs(k)}", f"1/({f})"]
        dom = f"x &gt; {n(k)}"
    else:
        f = f"log<sub>{b}</sub>({xh})" + (f" {'+' if k > 0 else MINUS} {abs(k)}" if k else "")
        inv = f"{b}<sup>{xk}</sup>" + (f" {'+' if h > 0 else MINUS} {abs(h)}" if h else "")
        bad = [f"{b}<sup>{xh}</sup>" + (f" {'+' if k > 0 else MINUS} {abs(k)}" if k else ""), f"log<sub>{b}</sub>({xk})" + (f" {'+' if h > 0 else MINUS} {abs(h)}" if h else ""),
               f"{b}<sup>x</sup> {'+' if h + k >= 0 else MINUS} {abs(h + k)}", f"x<sup>{b}</sup>"]
        dom = "semua x real"
    return {"prompt": f"Tentukan invers dari f(x) = {f}.", "correct": f"f⁻¹(x) = {inv}", "distractors": [f"f⁻¹(x) = {w}" for w in bad],
            "steps": ["Eksponen dan logaritma (basis sama) saling invers.", f"Tukar x ↔ y lalu selesaikan untuk y: <b>f⁻¹(x) = {inv}</b>.", f"Domain f⁻¹ = range f: {dom}."],
            "explanation": "Pergeseran mendatar f menjadi pergeseran tegak f⁻¹ (dan sebaliknya) — grafik dicerminkan terhadap y = x."}


@register("inv.domain", INV, (1, 2, 4, 5))
def inv_domain(rng, tier):
    h, k = rng.randint(-5, 5), rng.randint(-5, 5)
    if tier <= 2:
        a, b, c = nz(rng, -4, 4), rng.randint(-5, 5), rng.randint(2, 4)
        cases = [(f"f(x) = {terms([(a, 'x')], b)}", "ya"), (f"f(x) = x² + {c}", "tidak"), (f"f(x) = x³ + {c}", "ya"), (f"f(x) = |x − {c}|", "tidak"),
                 (f"f(x) = {c}<sup>x</sup>", "ya"), (f"f(x) = (x − {c})² pada x ≥ {c}", "ya"), (f"f(x) = sin x pada ℝ", "tidak")]
        f, ans = rng.choice(cases)
        correct = f"{ans} — {'lolos' if ans == 'ya' else 'gagal'} uji garis mendatar"
        return {"prompt": f"Apakah {f} punya invers (satu-satu)?", "correct": correct,
                "distractors": [f"{'tidak' if ans == 'ya' else 'ya'} — {'gagal' if ans == 'ya' else 'lolos'} uji garis mendatar", "ya — semua fungsi punya invers", "tidak — hanya fungsi linear yang punya invers"],
                "steps": ["Fungsi punya invers ⇔ satu-satu ⇔ setiap garis mendatar memotong grafik paling banyak sekali.", f"<b>{correct}</b>."],
                "explanation": "Domain bisa dibatasi agar fungsi menjadi satu-satu (mis. x² pada x ≥ 0)."}
    x = f"x {MINUS} {h}" if h > 0 else f"x + {-h}" if h < 0 else "x"
    f = f"({x})²" + (f" {'+' if k > 0 else MINUS} {abs(k)}" if k else "")
    xk = f"x {MINUS} {k}" if k > 0 else f"x + {-k}" if k < 0 else "x"
    inv = (f"{n(h)} + √({xk})" if h else f"√({xk})")
    correct = f"f⁻¹(x) = {inv}, x ≥ {n(k)}"
    return {"prompt": f"f(x) = {f} dengan domain dibatasi x ≥ {n(h)}. Tentukan f⁻¹ beserta domainnya.", "correct": correct,
            "distractors": [f"f⁻¹(x) = {n(h)} − √({xk}), x ≥ {n(k)}" if h else f"f⁻¹(x) = −√({xk}), x ≥ {n(k)}", f"f⁻¹(x) = {inv}, x ≥ {n(h)}",
                            f"f⁻¹(x) = {n(k)} + √({x}), x ≥ {n(h)}" if k else f"f⁻¹(x) = √({x}), x ≥ {n(h)}", f"f⁻¹(x) = {inv}, semua x"],
            "steps": [f"Pada x ≥ {n(h)} fungsi naik ⇒ satu-satu.", f"y = {f} ⇒ x = {n(h)} ± √(y − {paren(k)}); pilih + karena x ≥ {n(h)}.".replace("0 ± ", "±"),
                      f"Domain f⁻¹ = range f = [{n(k)}, ∞): <b>{correct}</b>."],
            "explanation": "Membatasi domain parabola pada salah satu sisi puncak membuatnya punya invers."}


# ════════════════════════ Polinomial & fungsi rasional ════════════════════
def _ev(co, x):
    return sum(c * x ** (len(co) - 1 - i) for i, c in enumerate(co))


@register("pr.sisa", PR, (1, 2, 3))
def pr_sisa(rng, tier):
    co = [nz(rng, -3, 3)] + [rng.randint(-6, 6) for _ in range(3)]
    if tier <= 2:
        a = nz(rng, -3, 3)
        div, at = f"(x {MINUS} {a})" if a > 0 else f"(x + {-a})", Fr(a)
    else:
        p, q = rng.randint(2, 3), nz(rng, -5, 5)
        div, at = f"({terms([(p, 'x')], -q)})", Fr(q, p)
    val = _ev(co, at)
    return {"prompt": f"Tentukan sisa pembagian P(x) = {poly(co)} oleh {div}.", "correct": n(val),
            "distractors": [n(_ev(co, -at)), n(val + 1), "0" if val else "1", n(co[-1])],
            "steps": [f"Teorema sisa: sisa pembagian P(x) oleh (x − c) adalah P(c); untuk (px − q) sisanya P(q/p).", f"c = {n(at)}: P({n(at)}) = <b>{n(val)}</b>."],
            "explanation": "Teorema sisa menghindari pembagian bersusun."}


@register("pr.faktor", PR, (2, 3, 4))
def pr_faktor(rng, tier):
    a, p, k = nz(rng, -3, 3), rng.randint(-5, 5), rng.randint(-9, 9)
    q = -(a ** 3 + p * a * a + k * a)
    P = terms([(1, "x³"), (p, "x²")]) + " + kx" + (f" + {q}" if q > 0 else f" {MINUS} {-q}" if q < 0 else "")
    div = f"(x {MINUS} {a})" if a > 0 else f"(x + {-a})"
    return {"prompt": f"Tentukan k agar {div} merupakan faktor dari P(x) = {P}.", "correct": f"k = {n(k)}",
            "distractors": [f"k = {n(-k)}", f"k = {n(k + a)}", f"k = {n(q)}", f"k = {n(k + 1)}"],
            "steps": ["Teorema faktor: (x − c) faktor ⇔ P(c) = 0.", f"P({n(a)}) = {n(a ** 3)} + {n(p * a * a)} + {n(a)}k + {n(q)} = 0.".replace("+ −", "− "),
                      f"{n(a)}k = {n(-(a ** 3 + p * a * a + q))} ⇒ <b>k = {n(k)}</b>."],
            "explanation": "Faktor ⇔ akar: (x − c) membagi habis P ⇔ P(c) = 0."}


@register("pr.asimtot", PR, (1, 2, 3, 4, 5))
def pr_asimtot(rng, tier):
    if tier <= 3:
        while True:
            p, q, r, s = nz(rng, -6, 6), rng.randint(-9, 9), nz(rng, -4, 4), rng.randint(-9, 9)
            if p * s != q * r:
                break
        f = frac_lin(p, q, r, s)
        va, ha = Fr(-s, r), Fr(p, r)
        correct = f"x = {n(va)} dan y = {n(ha)}"
        return {"prompt": f"Tentukan asimtot tegak dan asimtot datar f(x) = {f}.", "correct": correct,
                "distractors": [f"x = {n(-va)} dan y = {n(ha)}", f"x = {n(va)} dan y = {n(Fr(q, s)) if s else '0'}", f"x = {n(ha)} dan y = {n(va)}", f"x = {n(va)} dan y = 0"],
                "steps": [f"Tegak: penyebut nol (pembilang tidak nol) ⇒ {terms([(r, 'x')], s)} = 0 ⇒ x = {n(va)}.",
                          f"Datar: derajat sama ⇒ y = rasio koefisien utama = {n(p)}/{n(r)} = {n(ha)}.", f"<b>{correct}</b>."],
                "explanation": "Asimtot datar ditentukan perbandingan derajat pembilang dan penyebut."}
    if tier == 4 or rng.random() < 0.5:
        a, b, c, d = nz(rng, -5, 5), rng.randint(-6, 6), nz(rng, -4, 4), rng.randint(-6, 6)
        kind = rng.choice(["sama", "lebih_kecil"])
        if kind == "sama":
            f = f"({terms([(a, 'x²'), (b, 'x')], 3)})/({terms([(c, 'x²')], d if d else 1)})"
            correct = f"y = {n(Fr(a, c))}"
            why = f"Derajat sama (2) ⇒ y = {n(a)}/{n(c)}."
        else:
            f = f"({terms([(b if b else 1, 'x')], 3)})/({terms([(c, 'x²')], d if d else 1)})"
            correct = "y = 0"
            why = "Derajat pembilang (1) &lt; derajat penyebut (2) ⇒ y = 0."
        return {"prompt": f"Tentukan asimtot datar f(x) = {f}.", "correct": correct,
                "distractors": [w for w in ["y = 0", f"y = {n(Fr(a, c))}", f"y = {n(Fr(c, a))}", "tidak ada", f"y = {n(a)}"] if w != correct],
                "steps": [why, f"<b>{correct}</b>."], "explanation": "Bandingkan derajat: kecil/besar → 0; sama → rasio koefisien; lebih besar satu → asimtot miring."}
    b, c, d = rng.randint(-6, 6), rng.randint(-9, 9), nz(rng, -5, 5)
    while d * d + b * d + c == 0:
        c += 1
    f = f"({terms([(1, 'x²'), (b, 'x')], c)})/(x {MINUS} {d})" if d > 0 else f"({terms([(1, 'x²'), (b, 'x')], c)})/(x + {-d})"
    m = b + d
    correct = f"y = {terms([(1, 'x')], m)}"
    return {"prompt": f"Tentukan asimtot miring f(x) = {f}.", "correct": correct,
            "distractors": [f"y = {terms([(1, 'x')], b)}", f"y = {terms([(1, 'x')], b - d)}" if b - d != m else f"y = {terms([(1, 'x')], m + 1)}", "y = x", f"y = {terms([(1, 'x')], -m)}" if m else "y = 0"],
            "steps": [f"Pembilang berderajat satu lebih tinggi ⇒ bagi bersusun: x² + … = (x − {paren(d)})(x + {n(m)}) + sisa.", f"Hasil bagi x + {paren(m)} adalah asimtot miring.", f"<b>{correct}</b>."],
            "explanation": "Asimtot miring = hasil bagi polinom (sisa/penyebut → 0)."}


@register("pr.akar", PR, (1, 4, 5))
def pr_akar(rng, tier):
    r = sorted(distinct(rng, -5, 5, 3)) if tier > 1 else sorted(distinct(rng, -6, 6, 2))
    if tier == 1:
        co = [1, -(r[0] + r[1]), r[0] * r[1]]
        correct = f"x = {n(r[0])} atau x = {n(r[1])}"
        return {"prompt": f"Tentukan semua nol polinom P(x) = {poly(co)}.", "correct": correct,
                "distractors": [f"x = {n(-r[0])} atau x = {n(-r[1])}", f"x = {n(r[0])} atau x = {n(-r[1])}", f"x = {n(r[0] + r[1])} atau x = {n(r[0] * r[1])}", f"x = {n(-r[0])} atau x = {n(r[1])}"],
                "steps": [f"Cari dua bilangan berjumlah {n(r[0] + r[1])} dan berhasil kali {n(r[0] * r[1])}.", f"P(x) = (x − {paren(r[0])})(x − {paren(r[1])}) ⇒ <b>{correct}</b>."],
                "explanation": "Nol polinom = akar persamaan P(x) = 0."}
    co = [1, -sum(r), r[0] * r[1] + r[0] * r[2] + r[1] * r[2], -r[0] * r[1] * r[2]]
    ask = rng.choice(["jumlah", "kali", "jumlah_kuadrat"]) if tier == 5 else "akar"
    if ask == "akar":
        correct = "x = " + ", ".join(n(v) for v in r)
        wrong = ["x = " + ", ".join(n(-v) for v in r), "x = " + ", ".join(n(v) for v in (r[0], r[1], -r[2])), "x = " + ", ".join(n(v) for v in (-r[0], r[1], r[2])), "x = " + ", ".join(n(v + 1) for v in r)]
        steps = [f"Teorema akar rasional: kandidat = pembagi {n(co[-1])}.", f"Uji: P({n(r[0])}) = 0, lalu bagi sintetik dan faktorkan sisanya.", f"<b>{correct}</b>."]
    else:
        val = {"jumlah": sum(r), "kali": r[0] * r[1] * r[2], "jumlah_kuadrat": sum(v * v for v in r)}[ask]
        word = {"jumlah": "jumlah ketiga akarnya", "kali": "hasil kali ketiga akarnya", "jumlah_kuadrat": "jumlah kuadrat ketiga akarnya"}[ask]
        correct = n(val)
        wrong = [n(-val), n(co[2]), n(val + 1), n(sum(r) ** 2)]
        steps = ["Vieta untuk x³ + bx² + cx + d: Σr = −b, Σrᵢrⱼ = c, r₁r₂r₃ = −d.",
                 "Jumlah kuadrat = (Σr)² − 2Σrᵢrⱼ." if ask == "jumlah_kuadrat" else "Langsung dari koefisien — tanpa mencari akarnya.", f"<b>{correct}</b>."]
        return {"prompt": f"Untuk P(x) = {poly(co)}, hitung {word} (dengan Vieta).", "correct": correct, "distractors": wrong, "steps": steps,
                "explanation": "Rumus Vieta menghubungkan akar dan koefisien."}
    return {"prompt": f"Tentukan semua nol polinom P(x) = {poly(co)}.", "correct": correct, "distractors": wrong, "steps": steps,
            "explanation": "Teorema akar rasional + pembagian sintetik."}


# ════════════════════════ Barisan & notasi sigma ═════════════════════════
@register("sg.aritmetika", SG, (1, 2, 3))
def sg_aritmetika(rng, tier):
    a, d, N = rng.randint(-9, 12), nz(rng, -5, 7), rng.randint(8, 40)
    terms_ = ", ".join(n(a + d * i) for i in range(4))
    if tier == 1:
        val = a + (N - 1) * d
        return {"prompt": f"Barisan {terms_}, … . Tentukan suku ke-{N}.", "correct": n(val), "distractors": [n(a + N * d), n(N * d), n(val + d), n(a * N)],
                "steps": [f"Aritmetika: a = {n(a)}, beda d = {n(d)}.", f"U<sub>n</sub> = a + (n − 1)d = {n(a)} + {N - 1}·{paren(d)} = <b>{n(val)}</b>."],
                "explanation": "Suku ke-n barisan aritmetika: a + (n − 1)d."}
    val = Fr(N, 2) * (2 * a + (N - 1) * d)
    return {"prompt": f"Hitung jumlah {N} suku pertama deret {terms_}, … .", "correct": n(val),
            "distractors": [n(N * (a + (N - 1) * d)), n(Fr(N, 2) * (a + (N - 1) * d)), n(val + d), n(Fr(N, 2) * (2 * a + N * d))],
            "steps": [f"S<sub>n</sub> = n/2·(2a + (n − 1)d).", f"= {N}/2·(2·{paren(a)} + {N - 1}·{paren(d)}) = <b>{n(val)}</b>."],
            "explanation": "Trik Gauss: pasangkan suku pertama dan terakhir."}


@register("sg.geometri", SG, (1, 2, 3, 4))
def sg_geometri(rng, tier):
    a = nz(rng, -5, 6)
    r = rng.choice([2, 3, -2, Fr(1, 2), -3, Fr(1, 3)]) if tier > 1 else rng.choice([2, 3, -2])
    N = rng.randint(4, 8)
    terms_ = ", ".join(n(a * Fr(r) ** i) for i in range(4))
    if tier == 1:
        val = a * Fr(r) ** (N - 1)
        return {"prompt": f"Barisan {terms_}, … . Tentukan suku ke-{N}.", "correct": n(val), "distractors": [n(a * Fr(r) ** N), n(a * Fr(r) * (N - 1)), n(-val), n(val * 2)],
                "steps": [f"Geometri: a = {n(a)}, rasio r = {n(r)}.", f"U<sub>n</sub> = a·rⁿ⁻¹ = {n(a)}·({n(r)}){sup(N - 1)} = <b>{n(val)}</b>."],
                "explanation": "Suku ke-n barisan geometri: a·rⁿ⁻¹."}
    r = Fr(r)
    val = a * (r ** N - 1) / (r - 1)
    return {"prompt": f"Hitung jumlah {N} suku pertama deret {terms_}, … .", "correct": n(val),
            "distractors": [n(a * (r ** (N + 1) - 1) / (r - 1)), n(a * r ** N), n(a / (1 - r)), n(val + a)],
            "steps": [f"S<sub>n</sub> = a(rⁿ − 1)/(r − 1) dengan a = {n(a)}, r = {n(r)}.", f"= {n(a)}(({n(r)}){sup(N)} − 1)/({n(r)} − 1) = <b>{n(val)}</b>."],
            "explanation": "Jumlah geometri berhingga; untuk |r| < 1 dan n → ∞ menjadi a/(1 − r)."}


@register("sg.sigma", SG, (2, 3, 4, 5))
def sg_sigma(rng, tier):
    N = rng.randint(5, 20)
    a, b, c = (0, nz(rng, -5, 5), rng.randint(-6, 6)) if tier == 2 else (nz(rng, -3, 3), rng.randint(-5, 5), rng.randint(-6, 6))
    if tier == 5 and rng.random() < 0.5:
        m = rng.randint(2, 6)
        val = sum(k ** 3 for k in range(m, N + 1))
        return {"prompt": f"Hitung Σ<sub>k={m}</sub><sup>{N}</sup> k³.", "correct": n(val),
                "distractors": [n((N * (N + 1) // 2) ** 2), n(val + (m - 1) ** 3), n(val - m ** 3), n(sum(k * k for k in range(m, N + 1)))],
                "steps": [f"Σ<sub>k=1</sub><sup>n</sup> k³ = (n(n + 1)/2)².", f"Σ<sub>k={m}</sub><sup>{N}</sup> = ({N * (N + 1) // 2})² − ({(m - 1) * m // 2})² (kurangi k = 1 … {m - 1}).", f"= <b>{n(val)}</b>."],
                "explanation": "Mulai indeks ≠ 1: kurangi jumlah suku yang tidak ikut."}
    S1, S2 = N * (N + 1) // 2, N * (N + 1) * (2 * N + 1) // 6
    val = a * S2 + b * S1 + c * N
    expr = terms([(a, "k²"), (b, "k")], c)
    return {"prompt": f"Hitung Σ<sub>k=1</sub><sup>{N}</sup> ({expr}).", "correct": n(val),
            "distractors": [n(a * S2 + b * S1 + c), n(a * S1 * S1 + b * S1 + c * N), n(val - c * N), n(val + b)],
            "steps": ["Sifat linear: Σ(ak² + bk + c) = aΣk² + bΣk + c·n.", f"Σk = {S1}, Σk² = {S2}, n = {N}.", f"= {n(a)}·{S2} + {n(b)}·{S1} + {n(c)}·{N} = <b>{n(val)}</b>.".replace("+ −", "− ")],
            "explanation": "Rumus: Σk = n(n + 1)/2, Σk² = n(n + 1)(2n + 1)/6."}


@register("sg.teleskop", SG, (4, 5))
def sg_teleskop(rng, tier):
    N, c, m = rng.randint(5, 50), rng.randint(1, 6), rng.randint(0, 4)
    if rng.random() < 0.6:
        val = c * (Fr(1, m + 1) - Fr(1, N + m + 1))
        den = f"(k + {m})(k + {m + 1})" if m else "k(k + 1)"
        return {"prompt": f"Hitung Σ<sub>k=1</sub><sup>{N}</sup> {c}/({den}).", "correct": n(val),
                "distractors": [n(Fr(c, m + 1)), n(c * Fr(N, N + 1)) if m else n(val * 2), n(val + Fr(c, N + m + 1)), n(c * (Fr(1, m + 1) - Fr(1, N + m)))],
                "steps": [f"{c}/({den}) = {c}[1/(k + {m}) − 1/(k + {m + 1})] (pecahan parsial).".replace("k + 0", "k"),
                          f"Teleskopik: tersisa {c}[1/{m + 1} − 1/{N + m + 1}].", f"= <b>{n(val)}</b>."],
                "explanation": "Deret teleskopik: suku tengah saling menghapus."}
    sq = rng.randint(2, 9)
    Nn = sq * sq - 1
    val = sq - 1
    return {"prompt": f"Hitung Σ<sub>k=1</sub><sup>{Nn}</sup> (√(k + 1) − √k).", "correct": n(val),
            "distractors": [n(sq), n(Nn), n(sq - 2), f"√{Nn}"],
            "steps": ["Suku berurutan saling menghapus: (√2 − √1) + (√3 − √2) + … .", f"Tersisa √{Nn + 1} − √1 = {sq} − 1 = <b>{val}</b>."],
            "explanation": "Deret teleskopik: Σ(f(k + 1) − f(k)) = f(n + 1) − f(1)."}


# ════════════════════════ Vektor & matriks dasar ═════════════════════════
def vec(v):
    return "⟨" + ", ".join(n(x) for x in v) + "⟩"


TRIPLES3 = [(1, 2, 2, 3), (2, 3, 6, 7), (1, 4, 8, 9), (4, 4, 7, 9), (2, 6, 9, 11), (3, 4, 12, 13), (2, 10, 11, 15)]


@register("vm.vektor", VM, (1, 2, 3))
def vm_vektor(rng, tier):
    u = [rng.randint(-5, 5) for _ in range(2 if tier == 1 else 3)]
    v = [rng.randint(-5, 5) for _ in range(len(u))]
    p, q = nz(rng, -3, 3), nz(rng, -3, 3)
    if tier <= 2 and rng.random() < 0.6:
        w = [p * a + q * b for a, b in zip(u, v)]
        return {"prompt": f"u = {vec(u)}, v = {vec(v)}. Hitung {n(p)}u + {n(q)}v.".replace("+ −", "− "), "correct": vec(w),
                "distractors": [vec([p * a - q * b for a, b in zip(u, v)]), vec([a + b for a, b in zip(u, v)]), vec([q * a + p * b for a, b in zip(u, v)]), vec([x + 1 for x in w])],
                "steps": ["Operasi vektor dikerjakan per komponen.", f"<b>{vec(w)}</b>."], "explanation": "Kombinasi linear vektor."}
    a, b, c, h = rng.choice(TRIPLES3)
    s = [rng.choice([1, -1]) for _ in range(3)]
    P = [rng.randint(-4, 4) for _ in range(3)]
    Q = [P[0] + s[0] * a, P[1] + s[1] * b, P[2] + s[2] * c]
    return {"prompt": f"Hitung panjang vektor AB untuk A({', '.join(n(x) for x in P)}) dan B({', '.join(n(x) for x in Q)}).", "correct": n(h),
            "distractors": [n(a + b + c), n(h * h), n(h + 1), f"√{a * a + b * b}"],
            "steps": [f"AB = B − A = {vec([Q[i] - P[i] for i in range(3)])}.", f"|AB| = √({a * a} + {b * b} + {c * c}) = √{h * h} = <b>{h}</b>."],
            "explanation": "Panjang vektor = √(jumlah kuadrat komponen)."}


@register("vm.dot", VM, (2, 3, 4, 5))
def vm_dot(rng, tier):
    u = [nz(rng, -5, 5) for _ in range(3)]
    v = [rng.randint(-5, 5) for _ in range(3)]
    if tier <= 3:
        val = sum(a * b for a, b in zip(u, v))
        return {"prompt": f"Hitung u·v untuk u = {vec(u)} dan v = {vec(v)}.", "correct": n(val),
                "distractors": [n(-val), n(sum(u) * sum(v)), vec([a * b for a, b in zip(u, v)]), n(val + 1)],
                "steps": ["u·v = u₁v₁ + u₂v₂ + u₃v₃.", f"= {' + '.join(f'{paren(a)}·{paren(b)}' for a, b in zip(u, v))} = <b>{n(val)}</b>."],
                "explanation": "Hasil kali titik bernilai skalar; u·v = 0 ⇔ u ⟂ v."}
    if tier == 4:
        # cari k agar u ⟂ ⟨v₁, v₂, k⟩ (k bulat)
        while True:
            v2 = [rng.randint(-5, 5), rng.randint(-5, 5), 0]
            rest = u[0] * v2[0] + u[1] * v2[1]
            if rest % u[2] == 0:
                k = -rest // u[2]
                v2[2] = k
                break
        return {"prompt": f"Tentukan k agar u = {vec(u)} tegak lurus v = ⟨{n(v2[0])}, {n(v2[1])}, k⟩.", "correct": f"k = {n(k)}",
                "distractors": [f"k = {n(-k)}", f"k = {n(k + 1)}", f"k = {n(rest)}", "k = 0" if k else "k = 1"],
                "steps": ["Tegak lurus ⇔ u·v = 0.", f"{n(rest)} + {paren(u[2])}k = 0.", f"<b>k = {n(k)}</b>."], "explanation": "u ⟂ v ⇔ u·v = 0."}
    a, b, h = rng.choice([(3, 4, 5), (5, 12, 13), (8, 15, 17)])
    m = rng.randint(1, 4)
    u2, v2 = [a, b], [m * rng.choice([a, -a]), m * rng.choice([b, -b])]
    cos = Fr(u2[0] * v2[0] + u2[1] * v2[1], h * h * m)
    return {"prompt": f"Hitung cos θ, θ sudut antara u = {vec(u2)} dan v = {vec(v2)}.", "correct": n(cos),
            "distractors": [n(-cos), n(cos * m) if m > 1 else n(cos / 2), n(Fr(u2[0] * v2[0] + u2[1] * v2[1], h)), "0" if cos else "1"],
            "steps": ["cos θ = u·v/(|u||v|).", f"u·v = {u2[0] * v2[0] + u2[1] * v2[1]}, |u| = {h}, |v| = {m * h}.", f"cos θ = <b>{n(cos)}</b>."],
            "explanation": "Hasil kali titik mengukur seberapa searah dua vektor."}


@register("vm.det", VM, (1, 2, 3, 4))
def vm_det(rng, tier):
    if tier <= 2:
        a, b, c, d = (rng.randint(-6, 6) for _ in range(4))
        val = a * d - b * c
        return {"prompt": f"Hitung det [[{n(a)}, {n(b)}], [{n(c)}, {n(d)}]].", "correct": n(val),
                "distractors": [n(a * d + b * c), n(b * c - a * d), n(a * b - c * d), n(val + 1)],
                "steps": ["det [[a, b], [c, d]] = ad − bc.", f"= {paren(a)}·{paren(d)} − {paren(b)}·{paren(c)} = <b>{n(val)}</b>."],
                "explanation": "det = 0 ⇔ matriks tidak punya invers."}
    M = [[rng.randint(-3, 3) for _ in range(3)] for _ in range(3)]
    (a, b, c), (d, e, f), (g, h, i) = M
    val = a * (e * i - f * h) - b * (d * i - f * g) + c * (d * h - e * g)
    rows = "; ".join("[" + ", ".join(n(x) for x in r) + "]" for r in M)
    return {"prompt": f"Hitung determinan matriks [{rows}].", "correct": n(val),
            "distractors": [n(-val), n(a * (e * i - f * h) + b * (d * i - f * g) + c * (d * h - e * g)), n(val + 1), n(a * e * i)],
            "steps": ["Ekspansi kofaktor baris pertama: a(ei − fh) − b(di − fg) + c(dh − eg).",
                      f"= {paren(a)}·{n(e * i - f * h)} − {paren(b)}·{n(d * i - f * g)} + {paren(c)}·{n(d * h - e * g)}.", f"= <b>{n(val)}</b>."],
            "explanation": "Determinan 3×3 = volume (bertanda) balok jajaran genjang dari baris-barisnya."}


@register("vm.matriks", VM, (3, 4, 5))
def vm_matriks(rng, tier):
    while True:
        a, b, c, d = (rng.randint(-4, 4) for _ in range(4))
        if a * d - b * c:
            break
    D = a * d - b * c
    A = f"[[{n(a)}, {n(b)}], [{n(c)}, {n(d)}]]"
    if tier == 3:
        p, q, r, s = (rng.randint(-4, 4) for _ in range(4))
        P = [[a * p + b * r, a * q + b * s], [c * p + d * r, c * q + d * s]]
        txt = f"[[{n(P[0][0])}, {n(P[0][1])}], [{n(P[1][0])}, {n(P[1][1])}]]"
        return {"prompt": f"Hitung AB untuk A = {A} dan B = [[{n(p)}, {n(q)}], [{n(r)}, {n(s)}]].", "correct": txt,
                "distractors": [f"[[{n(a * p)}, {n(b * q)}], [{n(c * r)}, {n(d * s)}]]", f"[[{n(p * a + q * c)}, {n(p * b + q * d)}], [{n(r * a + s * c)}, {n(r * b + s * d)}]]",
                                f"[[{n(P[0][0])}, {n(P[1][0])}], [{n(P[0][1])}, {n(P[1][1])}]]", f"[[{n(P[0][0] + 1)}, {n(P[0][1])}], [{n(P[1][0])}, {n(P[1][1])}]]"],
                "steps": ["(AB)ᵢⱼ = baris i dari A · kolom j dari B.", f"<b>{txt}</b>. (Umumnya AB ≠ BA.)"], "explanation": "Perkalian matriks = komposisi transformasi linear."}
    if tier == 4:
        inv = f"(1/{n(D)})[[{n(d)}, {n(-b)}], [{n(-c)}, {n(a)}]]" if D != 1 else f"[[{n(d)}, {n(-b)}], [{n(-c)}, {n(a)}]]"
        return {"prompt": f"Tentukan invers A = {A}.", "correct": inv,
                "distractors": [f"(1/{n(D)})[[{n(a)}, {n(-b)}], [{n(-c)}, {n(d)}]]", f"(1/{n(-D)})[[{n(d)}, {n(-b)}], [{n(-c)}, {n(a)}]]", f"(1/{n(D)})[[{n(d)}, {n(b)}], [{n(c)}, {n(a)}]]",
                                f"[[{n(Fr(1, a)) if a else '0'}, {n(Fr(1, b)) if b else '0'}], [{n(Fr(1, c)) if c else '0'}, {n(Fr(1, d)) if d else '0'}]]"],
                "steps": [f"det A = {n(D)} ≠ 0 ⇒ invers ada.", "A⁻¹ = (1/det)[[d, −b], [−c, a]] — tukar diagonal utama, ubah tanda diagonal lain.", f"<b>{inv}</b>."],
                "explanation": "Invers 2×2 lewat determinan."}
    x, y = rng.randint(-5, 5), rng.randint(-5, 5)
    e, f = a * x + b * y, c * x + d * y
    correct = f"x = {n(x)}, y = {n(y)}"
    return {"prompt": f"Selesaikan sistem {terms([(a, 'x'), (b, 'y')])} = {n(e)} dan {terms([(c, 'x'), (d, 'y')])} = {n(f)} dengan aturan Cramer.", "correct": correct,
            "distractors": [f"x = {n(y)}, y = {n(x)}", f"x = {n(-x)}, y = {n(y)}", f"x = {n(x)}, y = {n(-y)}" if y else f"x = {n(x)}, y = 1", f"x = {n(x + 1)}, y = {n(y)}"],
            "steps": [f"D = {n(D)}.", f"Dₓ = {n(e * d - b * f)}, D<sub>y</sub> = {n(a * f - e * c)}.", f"x = Dₓ/D, y = D<sub>y</sub>/D ⇒ <b>{correct}</b>."],
            "explanation": "Cramer: tiap variabel = determinan dengan kolomnya diganti ruas kanan, dibagi D."}
