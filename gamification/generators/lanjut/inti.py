"""
Topik INTI Level Utama 4 (Kalkulus Tingkat Lanjut) — dipakai bersama oleh jalur FT, FMIPA, dan Fasilkom.

Setiap generator didaftarkan ke tiga topik sekaligus (kl-ft-…, kl-fm-…, kl-fk-…).
Rujukan: Stewart Bab 12–16; Whitman Bab 14–16; Strang (MIT) Bab 11–15.
"""

from fractions import Fraction as Fr
import math

from .. import register
from ..fmt import MINUS, fac, n, paren, poly, sup, terms, times
from ..graphs import fn, g2d, param, pt, readout
from ..precalc.common import distinct, nz
from ..dasar.aplikasi import pi_txt

FAC = ("ft", "fm", "fk")


def core(key):
    """Tuple slug topik inti untuk ketiga fakultas."""
    return tuple(f"kl-{f}-{key}" for f in FAC)


PBF, PBL, TPP, TPG, ILG, ILK, KVM, KVG, FKG, FKA = (core(k) for k in (
    "pb-fungsi", "pb-limit", "tp-parsial", "tp-gradien", "il-ganda", "il-koordinat", "kv-medan", "kv-garis", "fk-gamma", "fk-analisis"))


# ════════════════════════ Fungsi dua variabel ═══════════════════════════════
@register("pf.nilai", PBF, (1, 2))
def pf_nilai(rng, tier):
    a, b, c = nz(rng, -3, 3), rng.randint(-4, 4), rng.randint(-3, 3)
    x, y = rng.randint(-3, 3), rng.randint(-3, 3)
    if tier == 1:
        val = a * x * x + b * x * y + c * y * y
        f = f"{n(a)}x² + {n(b)}xy + {n(c)}y²".replace("+ −", "− ")
    else:
        val = Fr(a * x + b, 1) * (y * y + 1)
        f = f"({n(a)}x + {n(b)})(y² + 1)".replace("+ −", "− ")
    return {"prompt": f"Diketahui f(x, y) = {f}. Hitung f({n(x)}, {n(y)}).", "correct": n(val),
            "distractors": [n(val + 1), n(-val), n(val * 2), n(a * y * y + b * x * y + c * x * x) if tier == 1 else n((a * y + b) * (x * x + 1))],
            "steps": ["Fungsi dua variabel memasangkan setiap titik (x, y) dengan satu bilangan f(x, y).", f"Substitusi x = {n(x)}, y = {n(y)}: <b>{n(val)}</b>."],
            "explanation": "f: ℝ² → ℝ; grafiknya permukaan z = f(x, y) di ruang tiga dimensi."}


@register("pf.domain", PBF, (1, 2, 3))
def pf_domain(rng, tier):
    r = rng.randint(1, 6)
    cases = [(f"√({r * r} − x² − y²)", f"cakram tertutup x² + y² ≤ {r * r}", "bilangan di bawah akar ≥ 0."),
             ("ln(x − y)", "setengah bidang x &gt; y", "argumen ln harus &gt; 0."),
             (f"1/(x² + y² − {r * r})", f"semua (x, y) kecuali lingkaran x² + y² = {r * r}", "penyebut tidak boleh 0."),
             ("√(y − x²)", "daerah di atas (dan pada) parabola y = x²", "y − x² ≥ 0.")]
    pool = cases[:2] if tier == 1 else cases
    f, dom, why = rng.choice(pool)
    return {"prompt": f"Tentukan domain alami f(x, y) = {f}.", "correct": dom, "distractors": [c[1] for c in cases if c[1] != dom] + ["seluruh ℝ²"],
            "steps": [f"Syarat: {why}", f"Domain: <b>{dom}</b>."], "explanation": "Domain fungsi dua variabel berupa daerah di bidang-xy."}


@register("pf.kurva_tingkat", PBF, (2, 3, 4, 5))
def kurva_tingkat(rng, tier):
    k = rng.randint(1, 9)
    a, b = rng.randint(1, 3), rng.randint(1, 3)
    cases = [("x² + y²", f"lingkaran berjari-jari √{k}" if int(k ** 0.5) ** 2 != k else f"lingkaran berjari-jari {int(k ** 0.5)}", f"x*x+y*y", "circle"),
             ("y − x²", f"parabola y = x² + {k}", "y-x*x", "parab"),
             (f"{a * a if a > 1 else ''}x² + {b * b if b > 1 else ''}y²", "elips", "", "ell"),
             ("x² − y²", "hiperbola", "", "hyp")]
    pool = cases[:2] if tier == 2 else cases
    f, shape, _, kind = rng.choice(pool)
    return {"prompt": f"Kurva tingkat f(x, y) = {f} pada ketinggian k = {k} berbentuk …", "correct": shape,
            "distractors": [c[1] for c in cases if c[1] != shape] + ["garis lurus"],
            "steps": ["Kurva tingkat = himpunan titik dengan f(x, y) = k (seperti garis kontur peta).", f"{f} = {k} ⇒ <b>{shape}</b>."],
            "graphs": [g2d("Peta kontur: beberapa kurva tingkat", [-4, 4], [-4, 4], [param("kk", "k", 0.5, 9, 0.5, k, "k")],
                           [{"type": "param", "t": [0, "2*pi"], "x": "sqrt(kk)*cos(t)", "y": "sqrt(kk)*sin(t)", "color": "blue"},
                            {"type": "param", "t": [0, "2*pi"], "x": "sqrt(kk/2)*cos(t)", "y": "sqrt(kk/2)*sin(t)", "color": "gray"}] if kind == "circle" else
                           [fn("x*x+kk", "blue", "y = x² + k"), fn("x*x+kk/2", "gray", dash=True)] if kind == "parab" else
                           [{"type": "param", "t": [0, "2*pi"], "x": f"sqrt(kk)/{a}*cos(t)", "y": f"sqrt(kk)/{b}*sin(t)", "color": "blue"}] if kind == "ell" else
                           [{"type": "param", "t": [-2, 2], "x": "sqrt(kk)*cosh(t)", "y": "sqrt(kk)*sinh(t)", "color": "blue"},
                            {"type": "param", "t": [-2, 2], "x": "-sqrt(kk)*cosh(t)", "y": "sqrt(kk)*sinh(t)", "color": "blue"}],
                           None, "Geser k: kurva tingkat untuk ketinggian lain dari permukaan yang sama.")],
            "explanation": "Kurva tingkat adalah ‘irisan mendatar’ permukaan z = f(x, y)."}


@register("pf.permukaan", PBF, (3, 4, 5))
def permukaan(rng, tier):
    cases = [("z = x² + y²", "paraboloid (mangkuk)"), ("z = x² − y²", "paraboloid hiperbolik (pelana)"), ("z = √(x² + y²)", "kerucut"),
             ("z = 6 − 2x − 3y", "bidang datar"), ("z = √(9 − x² − y²)", "setengah bola"), ("z = y²", "silinder parabolik")]
    f, shape = rng.choice(cases)
    return {"prompt": f"Grafik {f} adalah …", "correct": shape, "distractors": [c[1] for c in cases if c[1] != shape],
            "steps": ["Lihat irisan dengan bidang z = k (kurva tingkat) dan dengan bidang x = 0 / y = 0.", f"<b>{shape}</b>."],
            "explanation": "Mengenali permukaan dari irisan-irisannya (Stewart §12.6)."}


# ════════════════════════ Limit & kekontinuan dua variabel ══════════════════
@register("pl.substitusi", PBL, (1, 2))
def pl_substitusi(rng, tier):
    a, b = rng.randint(-3, 3), rng.randint(-3, 3)
    p, q = nz(rng, -3, 3), rng.randint(-4, 4)
    if tier == 1:
        val = Fr(p * a * a + q * a * b)
        prompt = f"Hitung lim<sub>(x,y)→({n(a)},{n(b)})</sub> ({n(p)}x² + {n(q)}xy).".replace("+ −", "− ")
    else:
        den = a * a + b * b + 1
        val = Fr(p * a + q * b, den)
        prompt = f"Hitung lim<sub>(x,y)→({n(a)},{n(b)})</sub> ({n(p)}x + {n(q)}y)/(x² + y² + 1).".replace("+ −", "− ")
    return {"prompt": prompt, "correct": n(val), "distractors": [n(val + 1), n(-val), "tidak ada", "0" if val else "1"],
            "steps": ["Polinom dan fungsi rasional (penyebut ≠ 0) kontinu ⇒ substitusi langsung.", f"<b>{n(val)}</b>."],
            "explanation": "Fungsi kontinu: limit = nilai fungsi."}


def mono(var, e):
    return "" if e == 0 else var if e == 1 else f"{var}{sup(e)}"


def cf(c):
    """Koefisien bulat di depan monomial: 1 → '', −1 → '−'."""
    return "" if c == 1 else MINUS if c == -1 else n(c)


def sqrt_pi(c):
    """c·√π: 3/4 → '3√π/4'."""
    return times(c, "√π")


def gamma_val(s):
    """Γ(s) untuk s bulat positif atau setengah bulat: (pecahan, pakai_√π)."""
    s = Fr(s)
    if s.denominator == 1:
        return Fr(math.factorial(s.numerator - 1)), False
    v, x = Fr(1), Fr(1, 2)     # Γ(1/2) = √π
    while x < s:
        v, x = v * x, x + 1
    while x > s:               # s negatif: Γ(x − 1) = Γ(x)/(x − 1)
        x -= 1
        v = v / x
    return v, True


def gtxt(s):
    v, sq = gamma_val(s)
    return sqrt_pi(v) if sq else n(v)


@register("pl.kontinu", PBL, (1, 2, 3))
def pl_kontinu(rng, tier):
    a = rng.randint(1, 9)
    g, why = rng.choice([("sin", "sin u/u → 1"), ("tan", "tan u/u → 1"), ("e", "(eᵘ − 1)/u → 1"), ("ln", "ln(1 + u)/u → 1")])
    r2 = "(x² + y²)"
    num = {"sin": f"sin({a if a > 1 else ''}{r2})", "tan": f"tan({a if a > 1 else ''}{r2})", "e": f"(e<sup>{a if a > 1 else ''}(x² + y²)</sup> − 1)",
           "ln": f"ln(1 + {a if a > 1 else ''}{r2})"}[g]
    return {"prompt": f"Agar f(x, y) = {num}/(x² + y²) untuk (x, y) ≠ (0, 0) kontinu di (0, 0), nilai f(0, 0) haruslah …",
            "correct": n(a), "distractors": ["0", "1" if a != 1 else "2", "tidak ada nilai yang cocok", n(a * a)],
            "steps": ["Misal r² = x² + y² → 0 (dari arah mana pun).", f"Dengan u = {a}r²: f = {a}·[{why.split(' → ')[0]}] dan {why}.", f"Jadi limitnya {a}, sehingga f(0, 0) = <b>{a}</b>."],
            "explanation": "Kontinu ⇔ nilai fungsi = limit."}


@register("pl.jalur", PBL, (2, 3, 4, 5))
def pl_jalur(rng, tier):
    x, y = ("x", "y") if rng.random() < 0.5 else ("y", "x")      # permutasi peran variabel
    if tier <= 3:
        a, b, c, d = nz(rng, -4, 4), nz(rng, -4, 4), rng.randint(1, 4), rng.randint(1, 4)
        m = nz(rng, -3, 4)
        if tier == 2:
            num, val = terms([(a, f"{x}²"), (b, f"{y}²")]), Fr(a + b * m * m, c + d * m * m)
            work = f"({n(a)} + {n(b)}·{m * m}){x}²/({c} + {d}·{m * m}){x}²".replace("+ −", "− ")
        else:
            num, val = terms([(a, f"{x}{y}")]), Fr(a * m, c + d * m * m)
            work = f"{n(a * m)}{x}²/({c} + {d * m * m}){x}²"
        den = terms([(c, f"{x}²"), (d, f"{y}²")])
        prompt = f"Untuk f(x, y) = ({num})/({den}), hitung limit f sepanjang garis {y} = {cf(m)}{x} saat (x, y) → (0, 0)."
        return {"prompt": prompt, "correct": n(val), "distractors": ["0", n(Fr(a, c)), n(-val), "tidak ada", n(val + 1)],
                "steps": [f"Substitusi {y} = {cf(m)}{x}: f = {work}.", f"{x}² saling menghapus ⇒ <b>{n(val)}</b>.",
                          f"Karena hasilnya bergantung pada gradien m (coba m lain!), limit dua variabel di (0, 0) TIDAK ADA."],
                "explanation": "Dua jalur dengan nilai limit berbeda ⇒ limit tidak ada."}
    if tier == 4:
        a, b, c = nz(rng, -5, 5), rng.randint(1, 4), rng.randint(1, 4)
        exists = rng.random() < 0.35
        if exists:
            p = rng.choice([(2, 1), (1, 2), (3, 0), (2, 2)])
            num = terms([(a, mono(x, p[0]) + mono(y, p[1]))])
            correct = "ada, nilainya 0"
            steps = [f"Kutub: pembilang berderajat {sum(p)} &gt; 2 = derajat penyebut.",
                     f"|f| ≤ {abs(a)}r{sup(sum(p) - 2) if sum(p) > 3 else ''}/min({b}, {c}) → 0 untuk SEMUA arah θ.", "<b>ada, nilainya 0</b>."]
            wrong = [f"tidak ada ({y} = {x} memberi {n(Fr(a, b + c))}, {y} = 0 memberi 0)", f"ada, nilainya {n(Fr(a, b + c))}", "ada, nilainya 1", "tidak ada karena penyebut 0"]
        else:
            num = terms([(a, f"{x}{y}")])
            v = Fr(a, b + c)
            correct = f"tidak ada ({y} = {x} memberi {n(v)}, {y} = 0 memberi 0)"
            steps = [f"Jalur {y} = 0: f = 0.", f"Jalur {y} = {x}: f = {n(a)}{x}²/({b + c}{x}²) = {n(v)}.", "Dua jalur memberi nilai berbeda ⇒ <b>limit tidak ada</b>."]
            wrong = ["ada, nilainya 0", f"ada, nilainya {n(v)}", "ada, nilainya 1", "tidak ada karena penyebut 0"]
        return {"prompt": f"Apakah lim<sub>(x,y)→(0,0)</sub> ({num})/({terms([(b, f'{x}²'), (c, f'{y}²')])}) ada?", "correct": correct, "distractors": wrong,
                "steps": steps, "explanation": "Uji dua jalur untuk membuktikan TIDAK ada; koordinat kutub/apit untuk membuktikan ADA."}
    # tier 5: semua garis memberi 0, tetapi kurva x = y^k memberi nilai lain
    a, b, c, k = nz(rng, -6, 6), rng.randint(1, 4), rng.randint(1, 4), rng.choice([2, 3])
    v = Fr(a, b + c)
    num, den = terms([(a, f"{x}{mono(y, k)}")]), terms([(b, f"{x}²"), (c, mono(y, 2 * k))])
    correct = f"tidak ada ({x} = {mono(y, k)} memberi {n(v)}, garis lurus memberi 0)"
    return {"prompt": f"Apakah lim<sub>(x,y)→(0,0)</sub> ({num})/({den}) ada?", "correct": correct,
            "distractors": ["ada, nilainya 0 (semua garis lurus memberi 0)", f"ada, nilainya {n(v)}", f"tidak ada ({x} = {y} memberi {n(v)}, {y} = 0 memberi 0)", "ada, nilainya 1"],
            "steps": [f"Sepanjang garis {y} = m{x}: pembilang ~ {x}{sup(k + 1)}, penyebut ~ {b}{x}² ⇒ f → 0 untuk setiap m.",
                      f"Sepanjang kurva {x} = {mono(y, k)}: f = {n(a)}{mono(y, 2 * k)}/(({b} + {c}){mono(y, 2 * k)}) = {n(v)}.",
                      "Semua garis memberi 0, tetapi kurva memberi nilai lain ⇒ <b>limit tidak ada</b>. Memeriksa garis saja tidak cukup!"],
            "explanation": "Limit dua variabel harus sama di SEMUA jalur, termasuk kurva."}


@register("pl.polar", PBL, (3, 4, 5))
def pl_polar(rng, tier):
    k, c = rng.randint(1, 6), rng.randint(1, 6)
    K = "" if k == 1 else str(k)
    p, q = rng.choice([(2, 1), (1, 2), (3, 0), (0, 3), (2, 2), (3, 1), (1, 3)])
    a = nz(rng, -5, 5)
    poly_num = terms([(a, mono("x", p) + mono("y", q))])
    cases = [(f"({poly_num})/(x² + y²)", "0", f"Kutub: |f| ≤ {abs(a)}r{sup(p + q - 2) if p + q > 3 else ''} → 0 tanpa bergantung θ."),
             (f"sin({K}(x² + y²))/(x² + y²)", n(k), f"u = r²: sin({K}u)/u → {k}."),
             (f"(e<sup>{K}(x² + y²)</sup> − 1)/(x² + y²)", n(k), f"(e<sup>{K}u</sup> − 1)/u → {k} dengan u = r²."),
             (f"ln(1 + {K}(x² + y²))/(x² + y²)", n(k), f"ln(1 + {K}u)/u → {k} dengan u = r².")]
    if tier >= 4:
        cases += [(f"(1 − cos({K}(x² + y²)))/(x² + y²)²", n(Fr(k * k, 2)), f"(1 − cos({K}u))/u² → {k}²/2 dengan u = r²."),
                  (f"(x² + y²)/(√(x² + y² + {c * c}) − {c})", n(2 * c), f"Kalikan sekawan: r²(√(r² + {c * c}) + {c})/r² → {c} + {c}."),
                  (f"{K}(x² + y²)·ln(x² + y²)", "0", "r² ln r² → 0 (L'Hôpital pada ln u/(1/u))."),
                  (f"sin({K}xy)/(x² + y²)", "tidak ada", f"Kutub: sin({K}r² cos θ sin θ)/r² → {K or '1'}·cos θ sin θ, bergantung θ ⇒ tidak ada.")]
    f, val, why = rng.choice(cases)
    pool = [v for v in ["0", "1", n(k), n(2 * c), n(Fr(k * k, 2)), "tidak ada", "∞"] if v != val]
    return {"prompt": f"Gunakan koordinat kutub untuk menghitung lim<sub>(x,y)→(0,0)</sub> {f}.", "correct": val, "distractors": pool,
            "steps": ["x = r cos θ, y = r sin θ; (x, y) → (0, 0) ⇔ r → 0 untuk SEMUA θ.", why, f"<b>{val}</b>."],
            "explanation": "Jika bentuk kutub ≤ g(r) → 0 tanpa bergantung θ, limitnya ada; jika masih bergantung θ, tidak ada."}


# ════════════════════════ Turunan parsial ═══════════════════════════════════
@register("tpp.notasi", TPP, (1, 2))
def tpp_notasi(rng, tier):
    a = rng.randint(2, 5)
    xa1 = "x" if a == 2 else f"x{sup(a - 1)}"
    cases = [(f"x{sup(a)} sin y", f"{a}{xa1} sin y", [f"x{sup(a)} cos y", f"{a}{xa1} cos y", f"{a}{xa1}"]),
             (f"e<sup>{a}x</sup>y²", f"{a}e<sup>{a}x</sup>y²", [f"2ye<sup>{a}x</sup>", f"e<sup>{a}x</sup>y²", f"{a}e<sup>{a}x</sup>·2y"]),
             (f"ln(x{sup(a)} + y)", f"{a}{xa1}/(x{sup(a)} + y)", [f"1/(x{sup(a)} + y)", f"{a}{xa1}", f"(x{sup(a)} + y)/{a}x"])]
    f, good, bad = rng.choice(cases)
    return {"prompt": f"Tentukan ∂f/∂x untuk f(x, y) = {f}.", "correct": good, "distractors": bad + ["0"],
            "steps": ["∂f/∂x: turunkan terhadap x dan perlakukan y sebagai konstanta.", f"<b>{good}</b>."],
            "explanation": "Turunan parsial = laju perubahan saat hanya satu variabel bergerak."}


@register("tpp.parsial", TPP, (1, 2, 3))
def tpp_parsial(rng, tier):
    a, b = nz(rng, -3, 3), nz(rng, -3, 4)
    m, k = rng.randint(1, 3), rng.randint(1, 3)
    x, y = rng.randint(-2, 2), rng.randint(-2, 2)
    fx = a * m * x ** (m - 1) * y ** k + b * y
    fy = a * k * x ** m * y ** (k - 1) + b * x
    ask = rng.choice(["x", "y"])
    val = fx if ask == "x" else fy
    xm = "x" if m == 1 else f"x{sup(m)}"
    yk = "y" if k == 1 else f"y{sup(k)}"
    return {"prompt": f"f(x, y) = {n(a)}{xm}{yk} + {n(b)}xy. Hitung ∂f/∂{ask} di ({n(x)}, {n(y)}).".replace("+ −", "− "), "correct": n(val),
            "distractors": [n(fy if ask == "x" else fx), n(val + b), n(-val), n(a * x ** m * y ** k + b * x * y)],
            "steps": [f"∂f/∂x = {n(a * m)}x{sup(m - 1) if m > 2 else ('' if m == 1 else '')}{'' if m > 1 else ''}{yk if m >= 1 else ''} + {n(b)}y (y konstan)." if ask == "x" else
                      f"∂f/∂y = {n(a * k)}{xm}y{sup(k - 1) if k > 2 else ''} + {n(b)}x (x konstan).", f"Di ({n(x)}, {n(y)}): <b>{n(val)}</b>."],
            "graphs": [g2d(f"Irisan permukaan pada {'y' if ask == 'x' else 'x'} tetap", [-3, 3], [-30, 30], [param("c", f"{'y' if ask == 'x' else 'x'} tetap", -3, 3, 0.1, y if ask == "x" else x, "c")],
                           [fn(f"{a}*x**{m}*c**{k}+({b})*x*c" if ask == "x" else f"{a}*c**{m}*x**{k}+({b})*c*x", "blue", "irisan")], None,
                           f"∂f/∂{ask} adalah kemiringan kurva irisan ini.")],
            "explanation": "Soal U-S6 (berkas soal dasar) adalah contoh tetapnya."}


@register("tpp.orde2", TPP, (2, 3, 4))
def tpp_orde2(rng, tier):
    a, m, k = nz(rng, -3, 3), rng.randint(1, 4), rng.randint(1, 4)
    x, y = rng.randint(1, 2), rng.randint(-2, 2)
    if tier <= 3:
        val = a * m * k * x ** (m - 1) * y ** (k - 1)
        prompt = f"f(x, y) = {n(a)}x{sup(m) if m > 1 else ''}y{sup(k) if k > 1 else ''}. Hitung f<sub>xy</sub>({x}, {n(y)})."
        steps = [f"f<sub>x</sub> = {n(a * m)}x{sup(m - 1)}y{sup(k)}, lalu turunkan terhadap y: f<sub>xy</sub> = {n(a * m * k)}x{sup(m - 1)}y{sup(k - 1)}.",
                 "Teorema Clairaut: f<sub>xy</sub> = f<sub>yx</sub> bila keduanya kontinu.", f"Nilai: <b>{n(val)}</b>."]
        correct = n(val)
        wrong = [n(a * m * (m - 1) * x ** max(m - 2, 0) * y ** k), n(val * 2), n(-val), n(val + 1)]
    else:
        x, y = rng.choice([(1, 1), (1, 2), (2, 1), (1, 3), (2, -1), (1, -2)])
        correct = f"{n(1 + x * y)}e{sup(x * y)}" if x * y != 1 else "2e"
        prompt = f"f(x, y) = e<sup>xy</sup>. Hitung f<sub>xy</sub>({x}, {n(y)})."
        steps = ["f<sub>x</sub> = y·e<sup>xy</sup>.", "f<sub>xy</sub> = e<sup>xy</sup> + xy·e<sup>xy</sup> = (1 + xy)e<sup>xy</sup>.", f"Di ({x}, {n(y)}): <b>{correct}</b>."]
        wrong = [f"e{sup(x * y)}", f"{n(x * y)}e{sup(x * y)}", f"{n(y * y)}e{sup(x * y)}", f"{n(1 - x * y)}e{sup(x * y)}"]
    return {"prompt": prompt, "correct": correct, "distractors": wrong, "steps": steps, "explanation": "Turunan parsial orde dua dan teorema Clairaut."}


@register("tpp.rantai", TPP, (3, 4, 5))
def tpp_rantai(rng, tier):
    t = rng.randint(1, 2)
    if tier <= 4:
        p, q = rng.randint(1, 3), rng.randint(1, 3)
        # z = x²y, x = t^p, y = t^q ⇒ z = t^{2p + q} ⇒ dz/dt = (2p + q) t^{2p+q−1}
        val = (2 * p + q) * t ** (2 * p + q - 1)
        return {"prompt": f"z = x²y dengan x = t{sup(p) if p > 1 else ''}, y = t{sup(q) if q > 1 else ''}. Hitung dz/dt saat t = {t}.", "correct": n(val),
                "distractors": [n(2 * p * t ** (2 * p + q - 1)), n(val + 1), n(t ** (2 * p + q)), n(val * 2)],
                "steps": ["Aturan rantai: dz/dt = (∂z/∂x)(dx/dt) + (∂z/∂y)(dy/dt) = 2xy·x′ + x²·y′.",
                          f"Di t = {t}: x = {t ** p}, y = {t ** q}, x′ = {p * t ** (p - 1)}, y′ = {q * t ** (q - 1)}.",
                          f"dz/dt = 2·{t ** p}·{t ** q}·{p * t ** (p - 1)} + {t ** (2 * p)}·{q * t ** (q - 1)} = <b>{val}</b>."],
                "explanation": "Aturan rantai multivariabel: jumlahkan kontribusi setiap jalur."}
    s = rng.randint(1, 3)
    val = 2 * s + 2 * s   # z = x² + y², x = s + t, y = s − t ⇒ ∂z/∂s = 2x + 2y = 4s
    return {"prompt": f"z = x² + y² dengan x = s + t, y = s − t. Hitung ∂z/∂s di (s, t) = ({s}, {t}).", "correct": n(4 * s),
            "distractors": [n(4 * t), n(2 * s), n(2 * (s + t)), "0"],
            "steps": ["∂z/∂s = z_x·x_s + z_y·y_s = 2x·1 + 2y·1.", f"x = {s + t}, y = {s - t} ⇒ 2({s + t}) + 2({s - t}) = <b>{4 * s}</b>."],
            "explanation": "Pohon aturan rantai untuk variabel antara."}


@register("tpp.implisit", TPP, (4, 5))
def tpp_implisit(rng, tier):
    x0, y0, z0 = rng.randint(1, 3), rng.randint(1, 3), rng.randint(1, 3)
    c = x0 * x0 + y0 * y0 + z0 * z0 + x0 * y0 * z0
    val = Fr(-(2 * x0 + y0 * z0), 2 * z0 + x0 * y0)
    return {"prompt": f"Permukaan x² + y² + z² + xyz = {c} memuat titik ({x0}, {y0}, {z0}). Hitung ∂z/∂x di titik itu.", "correct": n(val),
            "distractors": [n(-val), n(Fr(-(2 * x0), 2 * z0)), n(Fr(2 * z0 + x0 * y0, 2 * x0 + y0 * z0)), n(val - 1)],
            "steps": ["F(x, y, z) = 0 ⇒ ∂z/∂x = −F<sub>x</sub>/F<sub>z</sub>.", f"F<sub>x</sub> = 2x + yz = {2 * x0 + y0 * z0}, F<sub>z</sub> = 2z + xy = {2 * z0 + x0 * y0}.",
                      f"∂z/∂x = <b>{n(val)}</b>."], "explanation": "Turunan implisit multivariabel."}


# ════════════════════════ Gradien & turunan berarah ═════════════════════════
def _f_grad(rng):
    a, b, c = nz(rng, -3, 3), nz(rng, -3, 3), rng.randint(-3, 3)
    x, y = rng.randint(-2, 2), rng.randint(-2, 2)
    fx, fy = 2 * a * x + c * y, 2 * b * y + c * x
    f = terms([(a, "x²"), (b, "y²"), (c, "xy")])
    return f, x, y, fx, fy


@register("tg.gradien", TPG, (1, 2))
def tg_gradien(rng, tier):
    f, x, y, fx, fy = _f_grad(rng)
    correct = f"⟨{n(fx)}, {n(fy)}⟩"
    return {"prompt": f"Tentukan ∇f({n(x)}, {n(y)}) untuk f(x, y) = {f}.", "correct": correct,
            "distractors": [f"⟨{n(fy)}, {n(fx)}⟩", f"⟨{n(-fx)}, {n(-fy)}⟩", f"⟨{n(fx + 1)}, {n(fy)}⟩", f"⟨{n(fx)}, {n(fx)}⟩"],
            "steps": ["∇f = ⟨f<sub>x</sub>, f<sub>y</sub>⟩.", f"f<sub>x</sub>({n(x)}, {n(y)}) = {n(fx)}, f<sub>y</sub>({n(x)}, {n(y)}) = {n(fy)}.", f"<b>{correct}</b>."],
            "explanation": "Gradien menunjuk arah kenaikan tercepat dan tegak lurus kurva tingkat."}


@register("tg.ortho", TPG, (1, 2))
def tg_ortho(rng, tier):
    a, b = nz(rng, -3, 3), nz(rng, -3, 3)
    x0, y0 = nz(rng, -3, 3), nz(rng, -3, 3)
    k = a * x0 * x0 + b * y0 * y0
    gx, gy = 2 * a * x0, 2 * b * y0
    f = terms([(a, "x²"), (b, "y²")])
    if tier == 1:
        good = f"⟨{n(gx)}, {n(gy)}⟩, tegak lurus kurva tingkat"
        return {"prompt": f"Kurva tingkat f(x, y) = {f} melalui titik ({n(x0)}, {n(y0)}). Vektor gradien di titik itu dan hubungannya dengan kurva tingkat adalah …",
                "correct": good, "distractors": [f"⟨{n(gx)}, {n(gy)}⟩, menyinggung kurva tingkat", f"⟨{n(-gy)}, {n(gx)}⟩, tegak lurus kurva tingkat",
                                                 f"⟨{n(a * x0)}, {n(b * y0)}⟩, menyinggung kurva tingkat", f"⟨{n(gy)}, {n(gx)}⟩, tegak lurus kurva tingkat"],
                "steps": [f"∇f = ⟨{n(2 * a)}x, {n(2 * b)}y⟩ = ⟨{n(gx)}, {n(gy)}⟩ di ({n(x0)}, {n(y0)}).",
                          "Sepanjang kurva tingkat f konstan ⇒ D<sub>u</sub>f = ∇f·u = 0 untuk u menyinggung kurva ⇒ ∇f ⟂ kurva tingkat.", f"<b>{good}</b>."],
                "explanation": "Sifat geometris gradien (dasar gradient descent)."}
    # tier 2: garis singgung kurva tingkat memakai ∇f sebagai vektor normal
    c = gx * x0 + gy * y0
    good = f"{terms([(gx, 'x'), (gy, 'y')])} = {n(c)}"
    return {"prompt": f"Tentukan garis singgung kurva tingkat {f} = {n(k)} di titik ({n(x0)}, {n(y0)}).", "correct": good,
            "distractors": [f"{terms([(gy, 'x'), (-gx, 'y')])} = {n(gy * x0 - gx * y0)}", f"{terms([(gx, 'x'), (gy, 'y')])} = {n(k)}",
                            f"{terms([(gx, 'x'), (-gy, 'y')])} = {n(gx * x0 - gy * y0)}", f"{terms([(gx, 'x'), (gy, 'y')])} = {n(c + 1)}"],
            "steps": [f"∇f({n(x0)}, {n(y0)}) = ⟨{n(gx)}, {n(gy)}⟩ tegak lurus kurva tingkat ⇒ menjadi vektor NORMAL garis singgung.",
                      f"Garis: {n(gx)}{fac(x0)} + {n(gy)}{fac(y0, 'y')} = 0.", f"<b>{good}</b>."],
            "explanation": "∇f ⟂ kurva tingkat: gradien adalah normal garis singgung kurva f(x, y) = k."}


@register("tg.berarah", TPG, (2, 3, 4))
def tg_berarah(rng, tier):
    f, x, y, fx, fy = _f_grad(rng)
    p, q, h = rng.choice([(3, 4, 5), (4, 3, 5), (-3, 4, 5), (5, 12, 13), (12, -5, 13), (0, 1, 1), (1, 0, 1)])
    val = Fr(fx * p + fy * q, h)
    return {"prompt": f"f(x, y) = {f}. Hitung turunan berarah di ({n(x)}, {n(y)}) dalam arah vektor ⟨{n(p)}, {n(q)}⟩.", "correct": n(val),
            "distractors": [n(fx * p + fy * q), n(-val), n(Fr(fx + fy, 1)), n(val + 1)],
            "steps": [f"Satuan arah: u = ⟨{n(p)}, {n(q)}⟩/{h}.", f"∇f = ⟨{n(fx)}, {n(fy)}⟩.", f"D<sub>u</sub>f = ∇f·u = ({n(fx)}·{paren(p)} + {n(fy)}·{paren(q)})/{h} = <b>{n(val)}</b>."],
            "explanation": "Turunan berarah D_u f = ∇f · u (u vektor satuan!)."}


@register("tg.maks_arah", TPG, (3, 4, 5))
def tg_maks(rng, tier):
    p, q, h = rng.choice([(3, 4, 5), (6, 8, 10), (5, 12, 13), (8, 15, 17)])
    # f = (p/2)x² + q·y di (1, y0) ⇒ ∇f = (p, q)
    return {"prompt": f"f(x, y) = {n(Fr(p, 2))}x² + {q}y. Berapa laju kenaikan maksimum f di (1, 5) dan ke arah mana?",
            "correct": f"{h}, arah ⟨{p}, {q}⟩", "distractors": [f"{p + q}, arah ⟨{p}, {q}⟩", f"{h}, arah ⟨{q}, {p}⟩", f"{h * h}, arah ⟨{p}, {q}⟩", f"{h}, arah ⟨{-p}, {-q}⟩"],
            "steps": [f"∇f = ⟨{n(p)}x, {q}⟩ = ⟨{p}, {q}⟩ di (1, 5).", f"Laju maksimum = |∇f| = √({p * p} + {q * q}) = {h}, searah ∇f.", f"<b>{h}, arah ⟨{p}, {q}⟩</b>."],
            "explanation": "max D_u f = |∇f|, dicapai saat u searah ∇f; minimum −|∇f| (berlawanan)."}


@register("tg.bidang_singgung", TPG, (3, 4, 5))
def tg_bidang(rng, tier):
    a, b = nz(rng, -2, 3), nz(rng, -2, 3)
    x0, y0 = rng.randint(-2, 2), rng.randint(-2, 2)
    z0 = a * x0 * x0 + b * y0 * y0
    fx, fy = 2 * a * x0, 2 * b * y0
    c = z0 - fx * x0 - fy * y0
    pl = lambda p, q, r: "z = " + terms([(p, "x"), (q, "y")], r)
    correct = pl(fx, fy, c)
    return {"prompt": f"Tentukan bidang singgung permukaan z = {terms([(a, 'x²'), (b, 'y²')])} di titik ({n(x0)}, {n(y0)}, {n(z0)}).", "correct": correct,
            "distractors": [pl(fx, fy, z0), pl(fy, fx, c), pl(a, b, c), pl(-fx, -fy, c), pl(fx, fy, c + 1)],
            "steps": ["z − z₀ = f<sub>x</sub>(x − x₀) + f<sub>y</sub>(y − y₀).", f"f<sub>x</sub> = {n(fx)}, f<sub>y</sub> = {n(fy)}.", f"<b>{correct}</b> (linearisasi dua variabel)."],
            "explanation": "Bidang singgung = aproksimasi linear L(x, y)."}


# ════════════════════════ Integral ganda ════════════════════════════════════
@register("ig.volume", ILG, (1, 2))
def ig_volume(rng, tier):
    if tier == 1:
        c, p, q = rng.randint(1, 9), rng.randint(1, 5), rng.randint(1, 5)
        return {"prompt": f"Hitung ∬<sub>R</sub> {c} dA dengan R = [0, {p}] × [0, {q}].", "correct": n(c * p * q),
                "distractors": [n(c * (p + q)), n(p * q), n(c * p * q * 2), n(Fr(c * p * q, 2))],
                "steps": ["∬ c dA = c × luas R.", f"{c}·{p}·{q} = <b>{c * p * q}</b> (volume balok)."], "explanation": "Integral ganda = volume di bawah permukaan."}
    a, b, c = rng.randint(1, 4), rng.randint(1, 4), rng.randint(1, 6)
    val = Fr(a * b * c, 6)
    return {"prompt": f"Hitung volume benda di oktan pertama di bawah bidang x/{a} + y/{b} + z/{c} = 1.", "correct": n(val),
            "distractors": [n(Fr(a * b * c, 2)), n(Fr(a * b * c, 3)), n(a * b * c), n(val + 1)],
            "steps": [f"z = {c}(1 − x/{a} − y/{b}) di atas segitiga 0 ≤ x ≤ {a}, 0 ≤ y ≤ {b}(1 − x/{a}).", "∬ z dA = (1/3)·(luas alas)·tinggi = (1/3)(ab/2)c.", f"= <b>{n(val)}</b> (limas segitiga)."],
            "explanation": "Volume = ∬ f(x, y) dA."}


@register("ig.persegi", ILG, (1, 2, 3))
def ig_persegi(rng, tier):
    p, q = rng.randint(1, 4), rng.randint(1, 4)
    a, b = nz(rng, -3, 4), nz(rng, -3, 4)
    if tier <= 2:
        val = Fr(a * p * p * q, 2) + Fr(b * p * q * q, 2)
        f = f"{n(a)}x + {n(b)}y".replace("+ −", "− ")
    else:
        val = Fr(a * p * p * q ** 3, 6)
        f = f"{n(a)}xy²"
    return {"prompt": f"Hitung ∬<sub>R</sub> ({f}) dA dengan R = [0, {p}] × [0, {q}].", "correct": n(val),
            "distractors": [n(val * 2), n(-val), n(val + 1), n(Fr(a * p * q, 2))],
            "steps": ["Teorema Fubini: ∬ = ∫₀^p ∫₀^q f dy dx (urutan bebas untuk persegi panjang).",
                      f"Integral dalam lalu integral luar memberi <b>{n(val)}</b>."],
            "explanation": "Integral berulang pada persegi panjang."}


@register("ig.daerah", ILG, (2, 3, 4, 5))
def ig_daerah(rng, tier):
    # D antara y = x^p dan y = k^{p−1}x (berpotongan di x = 0 dan x = k); integran α·xⁱyʲ
    p = 2 if tier <= 3 else rng.choice([2, 3])
    k, al = rng.randint(1, 3), rng.randint(1, 4)
    i, j = rng.choice({2: [(0, 0), (1, 0)], 3: [(1, 0), (0, 1), (2, 0)], 4: [(1, 1), (0, 1), (2, 0)], 5: [(1, 1), (2, 1), (1, 2)]}[tier])
    N = i + p * (j + 1) + 1
    val = Fr(al * k ** N, j + 1) * (Fr(1, i + j + 2) - Fr(1, N))
    swap = rng.random() < 0.5
    X, Y = ("y", "x") if swap else ("x", "y")      # tipe II: peran x dan y ditukar
    s = k ** (p - 1)
    integ = f"{al if al > 1 else ''}{mono(X, i)}{mono(Y, j)}" or "1"
    prompt = f"Hitung ∬<sub>D</sub> {integ} dA dengan D dibatasi {Y} = {mono(X, p)} dan {Y} = {cf(s)}{X}."
    steps = [f"Titik potong: {mono(X, p)} = {cf(s)}{X} ⇒ {X} = 0 dan {X} = {k}; untuk 0 ≤ {X} ≤ {k}: {mono(X, p)} ≤ {Y} ≤ {cf(s)}{X}" + (" (daerah tipe II: batas dalam terhadap x)." if swap else "."),
             f"Integral dalam: ∫ {mono(Y, j) or '1'} d{Y} = [{Y}{sup(j + 1) if j else ''}/{j + 1}]".replace("/1]", "]") + f" dari {mono(X, p)} ke {cf(s)}{X}.",
             f"Integral luar: {al if al > 1 else ''}∫₀^{k} {mono(X, i)}[({cf(s)}{X}){sup(j + 1) if j else ''} − {mono(X, p * (j + 1))}]{f'/{j + 1}' if j else ''} d{X} = <b>{n(val)}</b>."]
    return {"prompt": prompt, "correct": n(val), "distractors": [n(val * 2), n(val / 2), n(Fr(al * k ** N, (j + 1) * (i + j + 2))), n(val + 1)], "steps": steps,
            "graphs": [g2d("Daerah D", [-0.5, k + 0.5], [-0.5, k ** p + 1], [], [{"type": "fill", "upper": f"{s}*x", "lower": f"x**{p}", "from": 0, "to": k, "color": "amber"},
                                                                              fn(f"{s}*x", "green"), fn(f"x**{p}")], None,
                           "Batas dalam dari kurva ke garis" + (" (sumbu ditukar: baca x sebagai y)." if swap else "."))],
            "explanation": "Daerah tipe I: a ≤ x ≤ b, g₁(x) ≤ y ≤ g₂(x); tipe II menukar peran x dan y."}


@register("ig.urutan", ILG, (3, 4, 5))
def ig_urutan(rng, tier):
    # ∫₀^{a^k} ∫_{x^{1/k}}^{a} c·g(y^{k+1}) dy dx = c∫₀^a y^k g(y^{k+1}) dy
    k = 1 if tier == 3 else rng.randint(1, 3)
    a, c = (rng.randint(1, 3) if k == 1 else rng.randint(1, 2)), rng.randint(1, 6)
    g = rng.choice(["e", "e", "sin", "cos"])
    N = a ** (k + 1)
    co = Fr(c, k + 1)
    lo = "x" if k == 1 else ("√x" if k == 2 else "∛x")
    integ = {"e": f"e<sup>{mono('y', k + 1)}</sup>", "sin": f"sin({mono('y', k + 1)})", "cos": f"cos({mono('y', k + 1)})"}[g]
    pre = "" if c == 1 else str(c)
    core = {"e": f"e{sup(N)} − 1" if N > 1 else "e − 1", "sin": f"1 − cos {N}", "cos": f"sin {N}"}[g]
    lead = lambda v: "" if v == 1 else f"({n(v)})" if Fr(v).denominator > 1 else n(v)
    body = core if g == "cos" else f"({core})"
    fmt_ = lambda v: (core if v == 1 else f"{lead(v)} {core}") if g == "cos" else (core if v == 1 else f"{lead(v)}{body}")
    correct = fmt_(co)
    bad = [fmt_(Fr(c)), fmt_(co / 2), "tidak dapat dihitung", fmt_(Fr(c, k + 2))]
    xa = f"{a ** k}" if k > 1 else f"{a}"
    return {"prompt": f"Hitung ∫<sub>0</sub><sup>{xa}</sup> ∫<sub>{lo}</sub><sup>{a}</sup> {pre}{integ} dy dx dengan menukar urutan integrasi.", "correct": correct,
            "distractors": bad,
            "steps": [f"{integ} tidak punya antiturunan elementer terhadap y ⇒ tukar urutan.",
                      f"Daerah: 0 ≤ x ≤ {xa}, {lo} ≤ y ≤ {a} ⇔ 0 ≤ y ≤ {a}, 0 ≤ x ≤ {mono('y', k)}.",
                      f"∫₀^{a} ∫₀^{{{mono('y', k)}}} {pre}{integ} dx dy = ∫₀^{a} {pre}{mono('y', k)}·{integ} dy (faktor {mono('y', k)} muncul dari integral dalam!).",
                      f"Substitusi u = {mono('y', k + 1)}: = <b>{correct}</b>."],
            "explanation": "Menukar urutan integrasi dapat membuat integral mustahil menjadi mudah."}


@register("ig.segitiga", ILG, (3, 4, 5))
def ig_segitiga(rng, tier):
    # ∬_T xⁱyʲ dA, T: x, y ≥ 0, x/a + y/b ≤ 1  =  aⁱ⁺¹bʲ⁺¹ i! j!/(i + j + 2)!  (integral Dirichlet)
    a, b, c = rng.randint(1, 4), rng.randint(1, 4), rng.randint(1, 3)
    i, j = rng.choice({3: [(1, 0), (0, 1), (1, 1)], 4: [(1, 1), (2, 0), (0, 2), (2, 1)], 5: [(2, 1), (1, 2), (2, 2), (3, 1)]}[tier])
    val = c * Fr(a ** (i + 1) * b ** (j + 1) * math.factorial(i) * math.factorial(j), math.factorial(i + j + 2))
    integ = f"{c if c > 1 else ''}{mono('x', i)}{mono('y', j)}"
    return {"prompt": f"Hitung ∬<sub>T</sub> {integ} dA dengan T segitiga berpuncak (0, 0), ({a}, 0), dan (0, {b}).", "correct": n(val),
            "distractors": [n(val * 2), n(c * Fr(a ** (i + 1) * b ** (j + 1), (i + 1) * (j + 1))), n(val / 2), n(val + 1)],
            "steps": [f"Sisi miring: x/{a} + y/{b} = 1 ⇒ untuk 0 ≤ x ≤ {a}: 0 ≤ y ≤ {n(Fr(b, a))}({a} − x).".replace("1(", "(") if b != a else f"Sisi miring: x + y = {a} ⇒ 0 ≤ y ≤ {a} − x.",
                      f"Integral dalam ∫ {mono('y', j) or '1'} dy, lalu integral luar dalam x (substitusi x = {a}t mempercepat: muncul integral Beta).",
                      f"Hasil umum: aⁱ⁺¹bʲ⁺¹·i!·j!/(i + j + 2)! ⇒ {c if c > 1 else ''}{'·' if c > 1 else ''}{a}{sup(i + 1)}·{b}{sup(j + 1)}·{math.factorial(i)}·{math.factorial(j)}/{math.factorial(i + j + 2)} = <b>{n(val)}</b>."],
            "graphs": [g2d("Segitiga T", [-0.5, a + 0.5], [-0.5, b + 0.5], [], [{"type": "fill", "upper": f"{b}-{b}/{a}*x", "lower": "0", "from": 0, "to": a, "color": "amber"},
                                                                             fn(f"{b}-{b}/{a}*x", "green", "sisi miring")], None, "Batas atas y mengikuti sisi miring segitiga.")],
            "explanation": "Integral ganda pada segitiga: batas dalam berupa garis miring."}


# ════════════════════════ Integral lipat koordinat kutub/silinder/bola ══════
@register("ik.jacobian_polar", ILK, (1, 2))
def ik_jac(rng, tier):
    if tier == 1:
        a, b = rng.randint(1, 5), rng.randint(1, 5)
        kind = rng.choice(["polar", "elips", "elips"])
        if kind == "polar" or a == b == 1:
            return {"prompt": "Dalam koordinat kutub (x = r cos θ, y = r sin θ), elemen luas dA sama dengan …", "correct": "r dr dθ",
                    "distractors": ["dr dθ", "r² dr dθ", "dr dθ / r", "r sin θ dr dθ"],
                    "steps": ["Sektor kecil berukuran Δr (radial) × rΔθ (busur).", "Luas ≈ r Δr Δθ ⇒ dA = <b>r dr dθ</b> (determinan Jacobian = r)."],
                    "explanation": "Jangan lupa faktor r saat mengubah ke koordinat kutub."}
        J = a * b
        good = f"{J}r dr dθ"
        return {"prompt": f"Koordinat kutub-elips: x = {cf(a)}r cos θ, y = {cf(b)}r sin θ. Elemen luas dA sama dengan …", "correct": good,
                "distractors": ["r dr dθ", f"{a + b}r dr dθ", f"{J} dr dθ", f"{J}r² dr dθ"],
                "steps": [f"J = |∂(x, y)/∂(r, θ)| = |({a} cos θ)({b}r cos θ) − (−{a}r sin θ)({b} sin θ)|.", f"= {J}r(cos²θ + sin²θ) = {J}r ⇒ <b>{good}</b>.",
                          f"Contoh pakai: luas elips x²/{a * a} + y²/{b * b} ≤ 1 = ∫₀^{{2π}}∫₀¹ {J}r dr dθ = {J}π."],
                "explanation": "Faktor Jacobian = faktor pembesaran luas oleh transformasi."}
    while True:
        p, q, s, t = (rng.randint(-3, 3) for _ in range(4))
        D = p * t - q * s
        if D != 0:
            break
    u0, v0 = rng.randint(1, 4), rng.randint(1, 4)
    area = abs(D) * u0 * v0
    X, Y = terms([(p, "u"), (q, "v")]), terms([(s, "u"), (t, "v")])
    return {"prompt": f"Transformasi x = {X}, y = {Y} memetakan persegi panjang [0, {u0}] × [0, {v0}] di bidang-uv ke jajaran genjang R. Berapa luas R?",
            "correct": n(area), "distractors": [n(u0 * v0), n(D * u0 * v0) if D < 0 else n(area * 2), n(abs(p * t + q * s) * u0 * v0), n(area + u0 * v0)],
            "steps": [f"Jacobian: ∂(x, y)/∂(u, v) = det [[{n(p)}, {n(q)}], [{n(s)}, {n(t)}]] = {n(p)}·{paren(t)} − {paren(q)}·{paren(s)} = {n(D)}.",
                      f"dA = |J| du dv = {abs(D)} du dv ⇒ luas R = {abs(D)} × luas persegi panjang ({u0 * v0}).", f"<b>{area}</b>."],
            "explanation": "Pakai NILAI MUTLAK determinan: luas tidak pernah negatif."}


@register("ik.polar", ILK, (1, 2, 3))
def ik_polar(rng, tier):
    R = rng.randint(1, 5)
    th = rng.choice([Fr(1, 2), Fr(1), Fr(3, 2), Fr(2), Fr(1, 3), Fr(2, 3)])   # sudut sektor dalam satuan π
    sec = "cakram" if th == 2 else f"sektor 0 ≤ θ ≤ {times(th, 'π')}"
    reg = f"x² + y² ≤ {R * R}" + ("" if th == 2 else f", {sec}")
    if tier == 1:
        val = th * R * R / 2
        correct, prompt = times(val, "π"), f"Gunakan koordinat kutub untuk menghitung luas daerah {reg}."
        steps = [f"∫₀^{{{times(th, 'π')}}} ∫₀^{R} r dr dθ = {times(th, 'π')}·{R * R}/2.", f"= <b>{correct}</b>."]
        wrong = [times(val * 2, "π"), times(th * R, "π"), n(val), times(val / 2, "π")]
    elif tier == 2:
        m = rng.randint(1, 2)
        val = th * Fr(R ** (2 * m + 2), 2 * m + 2)
        f = "x² + y²" if m == 1 else "(x² + y²)²"
        correct, prompt = times(val, "π"), f"Hitung ∬<sub>D</sub> {f} dA, D: {reg}."
        steps = [f"{f} = r{sup(2 * m)}, dA = r dr dθ.", f"∫₀^{{{times(th, 'π')}}} ∫₀^{R} r{sup(2 * m + 1)} dr dθ = {times(th, 'π')}·{R ** (2 * m + 2)}/{2 * m + 2}.", f"= <b>{correct}</b>."]
        wrong = [times(th * Fr(R ** (2 * m + 1), 2 * m + 1), "π"), times(val * 2, "π"), times(th * Fr(R ** (2 * m + 2), 2 * m), "π"), n(val)]
    else:
        cc = rng.randint(1, 3)
        e = cc * R * R
        co = Fr(th, 2 * cc)
        core = f"1 − e{sup(-e)}"
        correct = f"{times(co, 'π')}·({core})" if co != 1 else f"π({core})"
        prompt = f"Hitung ∬<sub>D</sub> e<sup>−{cc if cc > 1 else ''}(x² + y²)</sup> dA, D: {reg}."
        steps = [f"∫ e<sup>−{cc if cc > 1 else ''}r²</sup> r dr = −e<sup>−{cc if cc > 1 else ''}r²</sup>/{2 * cc}.",
                 f"∫₀^{{{times(th, 'π')}}} ∫₀^{R} … = {times(th, 'π')}·({core})/{2 * cc}.", f"= <b>{correct}</b>. Untuk R → ∞ pada cakram penuh: π/{cc}, asal-usul integral Gauss."]
        wrong = [f"{times(co * 2, 'π')}·({core})", f"{times(co, 'π')}·(1 − e{sup(-cc * R)})", f"{times(co, 'π')}·e{sup(-e)}", times(co, "π")]
    return {"prompt": prompt, "correct": correct, "distractors": wrong, "steps": steps,
            "graphs": [g2d("Daerah dalam koordinat kutub", [-6, 6], [-6, 6], [param("RR", "R", 0.5, 5.5, 0.1, R, "R")],
                           [{"type": "param", "t": [0, f"{float(th)}*pi"], "x": "RR*cos(t)", "y": "RR*sin(t)", "color": "blue"},
                            {"type": "segment", "x1": 0, "y1": 0, "x2": "RR", "y2": 0, "color": "blue"},
                            {"type": "segment", "x1": 0, "y1": 0, "x2": f"RR*cos({float(th)}*pi)", "y2": f"RR*sin({float(th)}*pi)", "color": "blue"}], None,
                           "Batas sederhana dalam (r, θ): 0 ≤ r ≤ R, θ dalam rentang sektor.")],
            "explanation": "Daerah lingkaran/sektor → koordinat kutub; dA = r dr dθ."}


@register("ik.cincin", ILK, (2, 3, 4, 5))
def ik_cincin(rng, tier):
    a, b = sorted(distinct(rng, 1, 5, 2))
    if tier <= 3:
        val = Fr(2 * (b ** 3 - a ** 3), 3)
        correct, prompt = pi_txt(val), f"Hitung ∬<sub>D</sub> √(x² + y²) dA, D: {a * a} ≤ x² + y² ≤ {b * b}."
        steps = [f"√(x² + y²) = r ⇒ ∫₀^{{2π}} ∫<sub>{a}</sub><sup>{b}</sup> r·r dr dθ.", f"= 2π({b}³ − {a}³)/3 = <b>{correct}</b>."]
        wrong = [pi_txt(val / 2), pi_txt(b * b - a * a), pi_txt(Fr(b ** 3 - a ** 3, 3)), n(val)]
    else:
        correct, prompt = f"2π ln {n(Fr(b, a))}" if Fr(b, a).denominator == 1 else f"2π ln({n(Fr(b, a))})", f"Hitung ∬<sub>D</sub> dA/(x² + y²), D: {a * a} ≤ x² + y² ≤ {b * b}."
        steps = ["1/r²·r dr = dr/r.", f"∫₀^{{2π}} ∫<sub>{a}</sub><sup>{b}</sup> dr/r dθ = 2π ln({b}/{a}).", f"<b>{correct}</b>."]
        wrong = [f"π ln({n(Fr(b, a))})", f"2π({b} − {a})", f"2π ln({b * b - a * a})", "divergen"]
    return {"prompt": prompt, "correct": correct, "distractors": wrong, "steps": steps, "explanation": "Cincin (annulus): a ≤ r ≤ b."}


@register("ik.silinder_bola", ILK, (3, 4, 5))
def ik_silinder_bola(rng, tier):
    if tier == 3:
        a, b, c = rng.randint(2, 9), rng.randint(1, 4), 0
        kind = rng.choice(["bidang", "bidang", "dua"])
        if kind == "bidang":
            c = rng.randint(0, a - 1)
            val = Fr((a - c) ** 2, 2 * b)
            prompt = f"Hitung volume benda di bawah paraboloid z = {a} − {cf(b)}(x² + y²) dan di atas bidang z = {c} (koordinat silinder)."
            steps = [f"Batas bayangan: {a} − {b}r² = {c} ⇒ r² = {n(Fr(a - c, b))}.", f"V = ∫₀^{{2π}} ∫₀^{{√({n(Fr(a - c, b))})}} ({a - c} − {cf(b)}r²) r dr dθ = 2π·[{a - c}r²/2 − {b}r⁴/4].",
                     f"= π({a - c})²/(2·{b}) = <b>{times(val, 'π')}</b>."]
            wrong = [times(val * 2, "π"), times(val / 2, "π"), times(Fr((a - c) ** 2, b), "π"), times(Fr(a * a - c * c, 2 * b), "π"), n(val)]
        else:
            b2 = rng.randint(1, 3)
            val = Fr(a * a, 2 * (b + b2))
            prompt = f"Hitung volume benda di antara paraboloid z = {a} − {cf(b)}(x² + y²) (atas) dan z = {cf(b2)}(x² + y²) (bawah)."
            steps = [f"Perpotongan: {a} − {b}r² = {b2}r² ⇒ r² = {n(Fr(a, b + b2))}.", f"Tinggi = {a} − {b + b2}r²; V = 2π∫₀^{{√({n(Fr(a, b + b2))})}} ({a} − {b + b2}r²) r dr.",
                     f"= π·{a}²/(2·{b + b2}) = <b>{times(val, 'π')}</b>."]
            wrong = [times(val * 2, "π"), times(val / 2, "π"), times(Fr(a * a, 2 * b), "π"), times(Fr(a, b + b2), "π"), n(val)]
        return {"prompt": prompt, "correct": times(val, "π"), "distractors": wrong, "steps": steps, "explanation": "Koordinat silinder: dV = r dz dr dθ."}
    if tier == 4:
        kind = rng.choice(["massa", "kerucut_es", "bola"])
        if kind == "massa":
            R, H, k, m, q = rng.randint(1, 3), rng.randint(1, 3), rng.randint(1, 3), rng.randint(0, 2), rng.randint(0, 2)
            val = Fr(2 * k * R ** (m + 2) * H ** (q + 1), (m + 2) * (q + 1))
            rho = f"{cf(k)}{mono('r', m)}{mono('z', q)}" or str(k)
            rho = rho if rho not in ("", MINUS) else "1"
            prompt = f"Silinder r ≤ {R}, 0 ≤ z ≤ {H} memiliki rapat massa ρ = {rho if rho else k} (r jarak ke sumbu-z). Hitung massanya."
            steps = [f"M = ∭ ρ dV = ∫₀^{{2π}} ∫₀^{R} ∫₀^{H} {rho}·r dz dr dθ (faktor r dari dV!).",
                     f"= 2π·{k}·[r{sup(m + 2)}/{m + 2}]₀^{R}·[z{sup(q + 1) if q else ''}/{q + 1}]₀^{H}.".replace("/1]", "]"), f"= <b>{times(val, 'π')}</b>."]
            wrong = [times(Fr(2 * k * R ** (m + 1) * H ** (q + 1), (m + 1) * (q + 1)), "π"), times(val * 2, "π"), times(val / 2, "π"), n(val)]
            return {"prompt": prompt, "correct": times(val, "π"), "distractors": wrong, "steps": steps, "explanation": "Koordinat silinder: dV = r dz dr dθ."}
        R = rng.randint(1, 3)
        if kind == "kerucut_es":
            phi, one_minus = rng.choice([("π/3", Fr(1, 2)), ("π/2", Fr(1)), ("2π/3", Fr(3, 2))])
            val = Fr(2 * R ** 3, 3) * one_minus
            prompt = f"Hitung volume ‘es krim’: daerah di dalam bola ρ ≤ {R} dan di dalam kerucut φ ≤ {phi} (koordinat bola)."
            steps = ["dV = ρ² sin φ dρ dφ dθ.", f"∫₀^{{2π}} dθ · ∫₀^{{{phi}}} sin φ dφ · ∫₀^{R} ρ² dρ = 2π·(1 − cos {phi})·{R ** 3}/3.", f"= <b>{times(val, 'π')}</b>."]
            wrong = [times(Fr(4 * R ** 3, 3), "π"), times(val * 2, "π"), times(Fr(2 * R ** 3, 3), "π") if one_minus != 1 else times(Fr(R ** 3, 3), "π"), times(val, "π²")]
            return {"prompt": prompt, "correct": times(val, "π"), "distractors": wrong, "steps": steps, "explanation": "Koordinat bola: dV = ρ² sin φ dρ dφ dθ."}
        return {"prompt": f"Turunkan volume bola berjari-jari {R} dengan koordinat bola.", "correct": times(Fr(4 * R ** 3, 3), "π"),
                "distractors": [times(4 * R * R, "π"), times(Fr(2 * R ** 3, 3), "π"), times(R ** 3, "π"), times(Fr(8 * R ** 3, 3), "π")],
                "steps": ["dV = ρ² sin φ dρ dφ dθ.", f"∫₀^{{2π}} ∫₀^π ∫₀^{R} ρ² sin φ dρ dφ dθ = 2π·2·{R ** 3}/3.", f"= <b>{times(Fr(4 * R ** 3, 3), 'π')}</b>."],
                "explanation": "Koordinat bola: dV = ρ² sin φ dρ dφ dθ."}
    R, m, k = rng.randint(1, 3), rng.randint(1, 3), rng.randint(1, 3)
    kind = rng.choice(["radial", "z2", "setengah"])
    if kind == "radial":
        val = Fr(4 * k * R ** (m + 3), m + 3)
        steps = [f"Dalam koordinat bola integran = {cf(k)}ρ{sup(m) if m > 1 else ''} dan dV = ρ² sin φ dρ dφ dθ.",
                 f"∫₀^{{2π}} ∫₀^π ∫₀^{R} {cf(k)}ρ{sup(m + 2)} sin φ dρ dφ dθ = 4π·{k}·{R}{sup(m + 3)}/{m + 3}.", f"= <b>{times(val, 'π')}</b>."]
        if m == 1:
            integ = f"{cf(k)}√(x² + y² + z²)"
        elif m == 2:
            integ = f"{cf(k)}(x² + y² + z²)"
        else:
            integ = f"{cf(k)}(x² + y² + z²)<sup>3/2</sup>"
        prompt = f"Hitung ∭<sub>B</sub> {integ} dV, B bola berjari-jari {R} berpusat di asal."
        wrong = [times(Fr(4 * k * R ** (m + 2), m + 2), "π"), times(val * 2, "π"), times(Fr(k * R ** (m + 3), m + 3), "π"), times(Fr(4 * R ** 3, 3) * k, "π")]
    elif kind == "z2":
        val = Fr(4 * k * R ** 5, 15)
        prompt = f"Hitung ∭<sub>B</sub> {cf(k)}z² dV, B bola berjari-jari {R} berpusat di asal."
        steps = ["Simetri: ∭ x² = ∭ y² = ∭ z² = (1/3)∭ ρ² dV.", f"∭ ρ² dV = 4π·{R}⁵/5 ⇒ ∭ z² dV = 4π{R}⁵/15.", f"Dikali {k}: <b>{times(val, 'π')}</b>." if k > 1 else f"<b>{times(val, 'π')}</b>."]
        wrong = [times(Fr(4 * k * R ** 5, 5), "π"), times(val * 2, "π"), times(Fr(4 * k * R ** 5, 3), "π"), "0"]
    else:
        val = Fr(k * R ** 4, 4)
        prompt = f"Hitung ∭<sub>H</sub> {cf(k)}z dV, H setengah bola atas x² + y² + z² ≤ {R * R}, z ≥ 0."
        steps = ["z = ρ cos φ, dV = ρ² sin φ dρ dφ dθ, 0 ≤ φ ≤ π/2.", f"∫₀^{{2π}} dθ·∫₀^{{π/2}} cos φ sin φ dφ·∫₀^{R} ρ³ dρ = 2π·(1/2)·{R}⁴/4.", f"= <b>{times(val, 'π')}</b>."]
        wrong = ["0", times(val * 2, "π"), times(Fr(k * R ** 4, 2), "π"), times(Fr(2 * k * R ** 3, 3), "π")]
    return {"prompt": prompt, "correct": times(val, "π"), "distractors": wrong, "steps": steps, "explanation": "Simetri bola → koordinat bola."}


# ════════════════════════ Medan vektor, divergensi, curl ═══════════════════
@register("kvm.gambar", KVM, (1, 2))
def kvm_gambar(rng, tier):
    cases = [("F = ⟨−y, x⟩", "berputar berlawanan arah jarum jam mengelilingi titik asal"), ("F = ⟨x, y⟩", "memancar keluar dari titik asal (radial)"),
             ("F = ⟨1, 0⟩", "seragam ke arah sumbu-x positif"), ("F = ⟨y, −x⟩", "berputar searah jarum jam")]
    f, d = rng.choice(cases)
    js = {"F = ⟨−y, x⟩": ("-y", "x"), "F = ⟨x, y⟩": ("x", "y"), "F = ⟨1, 0⟩": ("1", "0"), "F = ⟨y, −x⟩": ("y", "-x")}[f]
    els = []
    for i in range(-3, 4):
        for j in range(-3, 4):
            P, Q = js[0].replace("x", str(i)).replace("y", str(j)), js[1].replace("x", str(i)).replace("y", str(j))
            els.append({"type": "segment", "x1": i, "y1": j, "x2": f"{i}+0.25*({P})", "y2": f"{j}+0.25*({Q})", "color": "blue", "arrow": True, "width": 1.6})
    return {"prompt": f"Medan vektor {f} paling tepat digambarkan sebagai …", "correct": d, "distractors": [c[1] for c in cases if c[1] != d] + ["nol di semua titik"],
            "steps": ["Gambar beberapa vektor F(x, y) di titik-titik sampel.", f"<b>{d}</b>."],
            "graphs": [g2d(f"Medan {f}", [-4, 4], [-4, 4], [], els, None, "Setiap panah menunjukkan arah dan besar F di titik itu.")],
            "explanation": "Medan vektor memasangkan vektor ke setiap titik (aliran fluida, gaya, angin)."}


@register("kvm.divergensi", KVM, (1, 2, 3))
def kvm_div(rng, tier):
    a, b, c = nz(rng, -3, 3), nz(rng, -3, 3), nz(rng, -3, 3)
    x, y, z = rng.randint(-2, 2), rng.randint(-2, 2), rng.randint(-2, 2)
    if tier == 1:
        val = a + b
        prompt = f"Hitung div F untuk F = ⟨{n(a)}x, {n(b)}y⟩."
        steps = ["div F = ∂P/∂x + ∂Q/∂y.", f"= {n(a)} + {paren(b)} = <b>{n(val)}</b>."]
    else:
        val = 2 * a * x + b * z + c * x * y
        prompt = f"Hitung div F di ({n(x)}, {n(y)}, {n(z)}) untuk F = ⟨{n(a)}x², {n(b)}yz, {n(c)}xyz⟩."
        steps = ["div F = ∂P/∂x + ∂Q/∂y + ∂R/∂z.", f"= {n(2 * a)}x + {n(b)}z + {n(c)}xy.", f"Di titik itu: <b>{n(val)}</b>."]
    return {"prompt": prompt, "correct": n(val), "distractors": [n(val + 1), n(-val), "0" if val else "1", n(val * 2)], "steps": steps,
            "explanation": "Divergensi = laju ‘keluarnya’ fluida per volume (sumber > 0, sumur < 0)."}


@register("kvm.curl", KVM, (2, 3, 4, 5))
def kvm_curl(rng, tier):
    a, b = nz(rng, -3, 3), nz(rng, -3, 3)
    if tier <= 3:
        val = a - b
        prompt = f"Hitung curl skalar (∂Q/∂x − ∂P/∂y) untuk F = ⟨{n(b)}y, {n(a)}x⟩."
        steps = ["Untuk F = ⟨P, Q⟩: curl = ∂Q/∂x − ∂P/∂y.", f"= {n(a)} − {paren(b)} = <b>{n(val)}</b>."]
        correct = n(val)
        wrong = [n(a + b), n(b - a), "0" if val else "1", n(val * 2)]
    else:
        prompt = f"Hitung curl F untuk F = ⟨0, {terms([(a, 'z')])}, {terms([(b, 'x')])}⟩."
        correct = f"⟨{n(-a)}, {n(-b)}, 0⟩"
        steps = ["curl F = ⟨R<sub>y</sub> − Q<sub>z</sub>, P<sub>z</sub> − R<sub>x</sub>, Q<sub>x</sub> − P<sub>y</sub>⟩.",
                 f"P = 0, Q = {n(a)}z, R = {n(b)}x ⇒ ⟨0 − {paren(a)}, 0 − {paren(b)}, 0 − 0⟩.", f"<b>{correct}</b>."]
        wrong = [f"⟨{n(a)}, {n(b)}, 0⟩", f"⟨{n(-b)}, {n(-a)}, 0⟩", "⟨0, 0, 0⟩", f"⟨0, {n(-a)}, {n(-b)}⟩"]
    return {"prompt": prompt, "correct": correct, "distractors": wrong, "steps": steps, "explanation": "Curl mengukur kecenderungan berputar (rotasi lokal)."}


@register("kvm.konservatif", KVM, (3, 4, 5))
def kvm_kons(rng, tier):
    a, b, c = nz(rng, -3, 3), nz(rng, -3, 3), rng.randint(-3, 3)
    cons = rng.random() < 0.6
    P = terms([(2 * a, "x"), (c, "y")])
    Q = terms([(c if cons else c + 1, "x"), (2 * b, "y")])
    if cons:
        correct = f"konservatif, f = {n(a)}x² + {n(c)}xy + {n(b)}y²".replace("+ −", "− ")
        why = f"P<sub>y</sub> = {n(c)} = Q<sub>x</sub>; integralkan: f = {n(a)}x² + {n(c)}xy + {n(b)}y² (+ konstanta)."
    else:
        correct = "tidak konservatif"
        why = f"P<sub>y</sub> = {n(c)} ≠ Q<sub>x</sub> = {n(c + 1)}."
    return {"prompt": f"Apakah F = ⟨{P}, {Q}⟩ konservatif? Jika ya, tentukan fungsi potensialnya.", "correct": correct,
            "distractors": ["tidak konservatif" if cons else f"konservatif, f = {n(a)}x² + {n(c)}xy + {n(b)}y²".replace("+ −", "− "),
                            f"konservatif, f = {n(2 * a)}x² + {n(2 * b)}y²".replace("+ −", "− "), f"konservatif, f = {n(a)}x² + {n(b)}y²".replace("+ −", "− "), "konservatif, f = 0"],
            "steps": ["F = ⟨P, Q⟩ (di daerah terhubung sederhana) konservatif ⇔ ∂P/∂y = ∂Q/∂x.", why, f"<b>{correct}</b>."],
            "explanation": "Medan konservatif = gradien suatu fungsi potensial."}


# ════════════════════════ Integral garis & Green ═══════════════════════════
@register("kvg.param", KVG, (1, 2))
def kvg_param(rng, tier):
    A = (rng.randint(-3, 3), rng.randint(-3, 3))
    B = (rng.randint(-3, 5), rng.randint(-3, 5))
    while B == A:
        B = (B[0] + 1, B[1])
    d = (B[0] - A[0], B[1] - A[1])
    correct = f"r(t) = ⟨{n(A[0])} + {n(d[0])}t, {n(A[1])} + {n(d[1])}t⟩, 0 ≤ t ≤ 1".replace("+ −", "− ")
    return {"prompt": f"Parametrisasi ruas garis dari A({n(A[0])}, {n(A[1])}) ke B({n(B[0])}, {n(B[1])}) adalah …", "correct": correct,
            "distractors": [f"r(t) = ⟨{n(B[0])} + {n(d[0])}t, {n(B[1])} + {n(d[1])}t⟩, 0 ≤ t ≤ 1".replace("+ −", "− "),
                            f"r(t) = ⟨{n(A[0])} + {n(B[0])}t, {n(A[1])} + {n(B[1])}t⟩, 0 ≤ t ≤ 1".replace("+ −", "− "),
                            f"r(t) = ⟨{n(d[0])}t, {n(d[1])}t⟩, 0 ≤ t ≤ 1", f"r(t) = ⟨{n(A[0])} + {n(d[0])}t, {n(A[1])} + {n(d[1])}t⟩, 0 ≤ t ≤ 2".replace("+ −", "− ")],
            "steps": ["r(t) = A + t(B − A), 0 ≤ t ≤ 1.", f"B − A = ⟨{n(d[0])}, {n(d[1])}⟩ ⇒ <b>{correct}</b>."], "explanation": "Parametrisasi adalah langkah pertama integral garis."}


@register("kvg.skalar", KVG, (1, 2, 3))
def kvg_skalar(rng, tier):
    r = rng.randint(1, 4)
    if tier <= 2:
        c = rng.randint(1, 5)
        val = 2 * c * r
        return {"prompt": f"Hitung ∫<sub>C</sub> {c} ds dengan C lingkaran x² + y² = {r * r}.", "correct": pi_txt(val),
                "distractors": [pi_txt(c * r), pi_txt(c * r * r), n(val), pi_txt(val * 2)],
                "steps": ["∫ c ds = c × panjang kurva.", f"Keliling 2π·{r} ⇒ <b>{pi_txt(val)}</b>."], "explanation": "∫_C f ds dengan f konstan = f × panjang C."}
    return {"prompt": f"Hitung ∫<sub>C</sub> (x² + y²) ds dengan C lingkaran berjari-jari {r} berpusat di asal.", "correct": pi_txt(2 * r ** 3),
            "distractors": [pi_txt(2 * r * r), pi_txt(r ** 3), pi_txt(Fr(4 * r ** 3, 3)), n(2 * r ** 3)],
            "steps": [f"Pada C: x² + y² = {r * r} dan ds = {r} dt.", f"∫₀^{{2π}} {r * r}·{r} dt = <b>{pi_txt(2 * r ** 3)}</b>."], "explanation": "ds = |r′(t)| dt."}


@register("kvg.kerja", KVG, (2, 3, 4))
def kvg_kerja(rng, tier):
    a = nz(rng, -3, 3)
    x1, y1 = rng.randint(1, 3), rng.randint(1, 3)
    val = a * x1 * y1
    return {"prompt": f"Hitung kerja ∫<sub>C</sub> F·dr dengan F = ⟨{n(a)}y, {n(a)}x⟩ sepanjang kurva r(t) = ⟨{x1}t, {y1}t²⟩, 0 ≤ t ≤ 1.", "correct": n(val),
            "distractors": [n(2 * val), "0", n(-val), n(a * (x1 + y1))],
            "steps": [f"Cara langsung: F(r(t))·r′(t) = {n(a)}·{y1}t²·{x1} + {n(a)}·{x1}t·{2 * y1}t = {n(3 * a * x1 * y1)}t²; ∫₀¹ = {n(val)}.",
                      f"Atau: F = ∇({n(a)}xy) konservatif ⇒ kerja = f(akhir) − f(awal) = {n(a)}·{x1}·{y1} − 0.", f"<b>{n(val)}</b>."],
            "explanation": "Kerja = ∫ F·dr; untuk medan konservatif hanya bergantung ujung-ujungnya."}


@register("kvg.green", KVG, (3, 4, 5))
def kvg_green(rng, tier):
    k = rng.randint(1, 3)
    if tier <= 4:
        r = rng.randint(1, 4)
        val = 2 * k * r * r
        return {"prompt": f"Gunakan Teorema Green untuk ∮<sub>C</sub> (−{k if k > 1 else ''}y dx + {k if k > 1 else ''}x dy), C lingkaran berjari-jari {r} berlawanan arah jarum jam.",
                "correct": pi_txt(val), "distractors": [pi_txt(k * r * r), pi_txt(val * 2), "0", pi_txt(2 * k * r)],
                "steps": ["Green: ∮ P dx + Q dy = ∬ (Q<sub>x</sub> − P<sub>y</sub>) dA.", f"Q<sub>x</sub> − P<sub>y</sub> = {k} + {k} = {2 * k}.", f"{2 * k} × luas (π{r * r}) = <b>{pi_txt(val)}</b>."],
                "explanation": "Teorema Green menghubungkan integral garis tertutup dengan integral ganda (luas = ½∮ x dy − y dx)."}
    a, b = rng.randint(1, 4), rng.randint(1, 4)
    # P = −y², Q = x² pada [0, a] × [0, b]: Q_x − P_y = 2x + 2y ⇒ ∬ = a²b + ab²
    val = a * a * b + a * b * b
    return {"prompt": f"Hitung ∮<sub>C</sub> (−y² dx + x² dy) dengan C batas persegi panjang [0, {a}] × [0, {b}] (berlawanan jarum jam).", "correct": n(val),
            "distractors": [n(a * b), n(2 * a * b), "0", n(Fr(val, 2))],
            "steps": ["Q<sub>x</sub> − P<sub>y</sub> = 2x + 2y.", f"∬ (2x + 2y) dA = {a}²·{b} + {a}·{b}² = <b>{val}</b>."], "explanation": "Green mengubah 4 integral garis menjadi satu integral ganda."}


@register("kvg.fundamental", KVG, (4, 5))
def kvg_fundamental(rng, tier):
    A = (rng.randint(-2, 2), rng.randint(-2, 2))
    B = (rng.randint(-2, 3), rng.randint(-2, 3))
    f = lambda p: p[0] ** 2 * p[1] + p[1] ** 3
    val = f(B) - f(A)
    return {"prompt": f"Hitung ∫<sub>C</sub> ∇f·dr untuk f(x, y) = x²y + y³, C sembarang kurva dari ({n(A[0])}, {n(A[1])}) ke ({n(B[0])}, {n(B[1])}).", "correct": n(val),
            "distractors": [n(-val), n(f(B)), "0", "bergantung pada lintasan"],
            "steps": ["Teorema fundamental integral garis: ∫ ∇f·dr = f(B) − f(A) (tak bergantung lintasan).", f"f(B) = {n(f(B))}, f(A) = {n(f(A))}.", f"<b>{n(val)}</b>."],
            "explanation": "Kurva tertutup ⇒ ∮ ∇f·dr = 0."}


# ════════════════════════ Fungsi Gamma, Beta ═══════════════════════════════
@register("fg.gamma", FKG, (1, 2, 3, 4, 5))
def fg_gamma(rng, tier):
    if tier == 1:
        if rng.random() < 0.4:
            m = rng.randint(2, 8)
            return {"prompt": f"Hitung Γ({m}) dengan Γ(x) = ∫<sub>0</sub><sup>∞</sup> t<sup>x−1</sup>e<sup>−t</sup> dt.", "correct": n(math.factorial(m - 1)),
                    "distractors": [n(math.factorial(m)), n(m - 1), n(math.factorial(m - 2)), n(m * m)],
                    "steps": ["Integral parsial: Γ(x + 1) = xΓ(x), Γ(1) = 1.", f"Γ({m}) = ({m} − 1)! = <b>{math.factorial(m - 1)}</b>."],
                    "explanation": "Gamma memperluas faktorial: Γ(n) = (n − 1)!."}
        a = rng.randint(3, 10)
        b = rng.randint(max(1, a - 4), a - 1)
        val = Fr(math.factorial(a - 1), math.factorial(b - 1))
        return {"prompt": f"Hitung Γ({a})/Γ({b}).", "correct": n(val), "distractors": [n(Fr(math.factorial(a), math.factorial(b))), n(Fr(a, b)), n(val * a), n(math.factorial(a - b))],
                "steps": [f"Γ({a}) = {a - 1}! dan Γ({b}) = {b - 1}!.", f"{a - 1}!/{b - 1}! = {' · '.join(str(t) for t in range(b, a))} = <b>{n(val)}</b>."],
                "explanation": "Γ(n) = (n − 1)! sehingga rasio Gamma menjadi perkalian berurutan."}
    if tier == 2:
        if rng.random() < 0.5:
            m, c = rng.randint(2, 7), rng.randint(1, 4)
            val = c * math.factorial(m)
            return {"prompt": f"Hitung ∫<sub>0</sub><sup>∞</sup> {c if c > 1 else ''}t{sup(m)}e<sup>−t</sup> dt.", "correct": n(val),
                    "distractors": [n(c * math.factorial(m - 1)), n(c * math.factorial(m + 1)), n(val * 2), n(c * m)],
                    "steps": [f"Bentuk Γ(x) dengan x − 1 = {m} ⇒ x = {m + 1}.", f"{c if c > 1 else ''}Γ({m + 1}) = {c if c > 1 else ''}{'·' if c > 1 else ''}{m}! = <b>{val}</b>."],
                    "explanation": "∫₀^∞ tⁿe^{−t} dt = Γ(n + 1) = n!."}
        p, q = rng.randint(1, 5), rng.randint(1, 5)
        val = Fr(math.factorial(p - 1) * math.factorial(q - 1), math.factorial(p + q - 1))
        return {"prompt": f"Hitung Γ({p})Γ({q})/Γ({p + q}).", "correct": n(val),
                "distractors": [n(Fr(math.factorial(p) * math.factorial(q), math.factorial(p + q))), n(Fr(1, p + q)), n(val * 2), n(Fr(p * q, p + q))],
                "steps": [f"= {p - 1}!·{q - 1}!/{p + q - 1}!.", f"= <b>{n(val)}</b> (ini juga B({p}, {q}) = ∫₀¹ x{sup(p - 1) if p > 1 else '⁰'}(1 − x){sup(q - 1) if q > 1 else '⁰'} dx).".replace("x⁰", "1").replace("(1 − x)⁰", "")],
                "explanation": "Fungsi Beta: B(p, q) = Γ(p)Γ(q)/Γ(p + q)."}
    if tier == 3:
        # ∫₀^∞ c·x^m e^{−a x²} dx = c·Γ((m + 1)/2)/(2a^{(m+1)/2})
        m, c = rng.randint(0, 5), rng.randint(1, 3)
        s = Fr(m + 1, 2)
        a = rng.choice([1, 4, 9]) if s.denominator == 2 else rng.randint(1, 4)
        root = math.isqrt(a)
        apow = Fr(a) ** s.numerator if s.denominator == 1 else Fr(root) ** (m + 1)
        g, sq = gamma_val(s)
        val = c * g / (2 * apow)
        correct = sqrt_pi(val) if sq else n(val)
        alt = (lambda v: sqrt_pi(v) if sq else n(v))
        integ = f"{c if c > 1 else ''}{mono('x', m)}e<sup>−{a if a > 1 else ''}x²</sup>"
        return {"prompt": f"Hitung ∫<sub>0</sub><sup>∞</sup> {integ} dx dengan fungsi Gamma.", "correct": correct,
                "distractors": [alt(val * 2), alt(val / 2), alt(c * g / apow / 2 * a) if a > 1 else (n(val) if sq else sqrt_pi(val)), alt(c * g)],
                "steps": [f"Substitusi u = {a if a > 1 else ''}x² ⇒ x = √(u/{a}), dx = du/(2√({a}u)).".replace("/1)", ")").replace("√(1u)", "√u"),
                          f"Integral menjadi {c if c > 1 else ''}Γ({n(s)})/(2{'·' + str(a) + '<sup>' + n(s) + '</sup>' if a > 1 else ''}), dengan Γ({n(s)}) = {gtxt(s)}.",
                          f"= <b>{correct}</b>."],
                "explanation": "Substitusi pangkat mengubah e^{−ax²} menjadi bentuk Gamma: Γ((m + 1)/2)/(2a^{(m+1)/2})."}
    if tier == 4:
        k = rng.randint(0, 6)
        s = Fr(2 * k + 1, 2)
        g, _ = gamma_val(s)
        if rng.random() < 0.5:
            return {"prompt": f"Hitung Γ({n(s)}) jika Γ(1/2) = √π.", "correct": sqrt_pi(g),
                    "distractors": [sqrt_pi(g * 2), "√π" if k else "2√π", sqrt_pi(Fr(math.factorial(k))) if k > 1 else sqrt_pi(g * 3), times(g, "π")],
                    "steps": ["Γ(x + 1) = xΓ(x) berulang dari Γ(1/2) = √π.", (" · ".join(f"{n(Fr(2 * j + 1, 2))}" for j in range(k)) + " · √π.") if k else "Langsung: Γ(1/2) = √π.", f"= <b>{sqrt_pi(g)}</b>."],
                    "explanation": "Γ(1/2) = √π berasal dari integral Gauss."}
        if rng.random() < 0.35:
            nb = rng.randint(1, 6)
            val = Fr(math.factorial(nb - 1)) / gamma_val(Fr(2 * nb + 1, 2))[0]   # B(1/2, n) = Γ(1/2)Γ(n)/Γ(n + 1/2)
            return {"prompt": f"Hitung ∫<sub>0</sub><sup>1</sup> x<sup>−1/2</sup>(1 − x){sup(nb - 1) if nb > 1 else '⁰'} dx = B(1/2, {nb}).".replace("(1 − x)⁰", ""),
                    "correct": n(val), "distractors": [n(val * 2), n(val / 2), sqrt_pi(val), n(Fr(1, nb))],
                    "steps": ["B(a, b) = Γ(a)Γ(b)/Γ(a + b).", f"Γ(1/2)Γ({nb})/Γ({n(Fr(2 * nb + 1, 2))}) = √π·{math.factorial(nb - 1)}/({gtxt(Fr(2 * nb + 1, 2))}).",
                              f"√π saling menghapus: <b>{n(val)}</b>."],
                    "explanation": "Fungsi Beta lewat Gamma; √π dari Γ(1/2) saling menghapus."}
        j = rng.randint(1, 3)
        t = s - j if s - j > 0 else s + j
        hi, lo = max(s, t), min(s, t)
        val = gamma_val(hi)[0] / gamma_val(lo)[0]
        return {"prompt": f"Hitung Γ({n(hi)})/Γ({n(lo)}).", "correct": n(val), "distractors": [n(val * hi), n(hi - lo), n(val / lo) if lo != 1 else n(val + 1), sqrt_pi(val)],
                "steps": [f"Γ({n(hi)}) = " + " · ".join(n(lo + i) for i in range(int(hi - lo))) + f" · Γ({n(lo)}).", f"√π saling menghapus: <b>{n(val)}</b>."],
                "explanation": "Rasio Gamma berselisih bilangan bulat = perkalian berurutan."}
    j = rng.randint(1, 3)
    s = Fr(1, 2) - j
    g, _ = gamma_val(s)
    if rng.random() < 0.5:
        return {"prompt": f"Gunakan Γ(x) = Γ(x + 1)/x untuk menghitung Γ({n(s)}).", "correct": sqrt_pi(g),
                "distractors": [sqrt_pi(-g), sqrt_pi(g * 2), "tidak terdefinisi", sqrt_pi(1 / g)],
                "steps": ["Γ(x) = Γ(x + 1)/x memperluas Γ ke argumen negatif (kecuali 0, −1, −2, …).",
                          " ⇒ ".join(f"Γ({n(Fr(1, 2) - i)}) = Γ({n(Fr(1, 2) - i + 1)})/({n(Fr(1, 2) - i)})" for i in range(1, j + 1)) + ".", f"= <b>{sqrt_pi(g)}</b>."],
                "explanation": "Γ tidak terdefinisi hanya di 0, −1, −2, …; di setengah-bulat negatif nilainya kelipatan √π."}
    m, k = rng.choice([(2, 3), (5, 3), (8, 3), (1, 4), (3, 4), (5, 4), (7, 4), (0, 2), (2, 2), (4, 2), (1, 2), (3, 2), (5, 2)])   # (m + 1)/k bulat/setengah bulat
    s, c = Fr(m + 1, k), rng.randint(1, 3)
    gv, sq = gamma_val(s)
    val = c * gv / k
    correct = sqrt_pi(val) if sq else n(val)
    return {"prompt": f"Hitung ∫<sub>0</sub><sup>∞</sup> {c if c > 1 else ''}{mono('x', m)}e<sup>−x{sup(k)}</sup> dx.", "correct": correct,
            "distractors": [sqrt_pi(val * k) if sq else n(val * k), sqrt_pi(val * 2) if sq else n(val * 2), n(val) if sq else sqrt_pi(val), "divergen"],
            "steps": [f"Substitusi u = x{sup(k)}: x = u<sup>1/{k}</sup>, dx = (1/{k})u<sup>1/{k} − 1</sup> du.",
                      f"∫ = ({n(Fr(c, k))})∫₀^∞ u<sup>{n(s)} − 1</sup>e<sup>−u</sup> du = {c if c > 1 else ''}Γ({n(s)})/{k}, dengan Γ({n(s)}) = {gtxt(s)}.", f"= <b>{correct}</b>."],
            "explanation": "∫₀^∞ x^m e^{−x^k} dx = Γ((m + 1)/k)/k."}


@register("fg.erf", FKG, (1, 2))
def fg_erf(rng, tier):
    s, c, b = rng.randint(1, 5), rng.randint(1, 4), rng.randint(-3, 3)
    a = s * s
    xb = "x" if b == 0 else f"(x {MINUS if b > 0 else '+'} {abs(b)})"
    if tier == 1:
        val = Fr(c, s)
        return {"prompt": f"Hitung ∫<sub>−∞</sub><sup>∞</sup> {c if c > 1 else ''}e<sup>−{a if a > 1 else ''}{xb}²</sup> dx.", "correct": sqrt_pi(val),
                "distractors": [sqrt_pi(Fr(c, a)), sqrt_pi(val / 2), times(val, "π"), sqrt_pi(val * 2)],
                "steps": [f"Geser u = {xb.strip('()')}: pergeseran tidak mengubah integral pada (−∞, ∞)." if b else "Integran sudah berpusat di 0.",
                          f"Skala v = {s}u: ∫ e<sup>−v²</sup> dv/{s} = √π/{s}." if s > 1 else "∫ e<sup>−u²</sup> du = √π (integral Gauss).",
                          f"Dikali {c}: <b>{sqrt_pi(val)}</b>." if c > 1 else f"<b>{sqrt_pi(val)}</b>."],
                "explanation": "∫ e^{−a(x − b)²} dx = √(π/a): dasar normalisasi distribusi normal."}
    kind = rng.choice(["setengah", "sigma", "momen"])
    if kind == "setengah":
        val = Fr(c, 2 * s)
        prompt = f"Hitung ∫<sub>0</sub><sup>∞</sup> {c if c > 1 else ''}e<sup>−{a if a > 1 else ''}x²</sup> dx."
        steps = ["Integran genap ⇒ setengah dari integral pada (−∞, ∞).", f"(1/2)·{c if c > 1 else ''}√π/{s} = <b>{sqrt_pi(val)}</b>.".replace("/1 ", " ")]
        correct, wrong = sqrt_pi(val), [sqrt_pi(val * 2), sqrt_pi(val / 2), times(val, "π"), sqrt_pi(Fr(c, 2 * a)), "1"]
    elif kind == "sigma":
        correct = f"{c * s if c * s > 1 else ''}√(2π)"
        prompt = f"Hitung ∫<sub>−∞</sub><sup>∞</sup> {c if c > 1 else ''}e<sup>−{xb}²/{2 * a}</sup> dx (σ = {s})."
        steps = [f"Substitusi u = {xb.strip('()')}/({s}√2): dx = {s}√2 du.", f"{c if c > 1 else ''}·{s}√2·√π = <b>{correct}</b>.".lstrip("·")]
        wrong = [f"{c * s if c * s > 1 else ''}√π", f"{c * a if c * a > 1 else ''}√(2π)", f"{c if c > 1 else ''}√(2π)" if s > 1 else "2√(2π)", f"{c * s if c * s > 1 else ''}2π"]
    else:
        val = Fr(c, 2 * s ** 3)
        prompt = f"Hitung ∫<sub>−∞</sub><sup>∞</sup> {c if c > 1 else ''}x²e<sup>−{a if a > 1 else ''}x²</sup> dx."
        steps = ["Parsial: u = x, dv = x e<sup>−ax²</sup> dx ⇒ ∫ x²e<sup>−ax²</sup> = (1/(2a))∫ e<sup>−ax²</sup> dx.", f"= (1/(2·{a}))·√π/{s}{f' × {c}' if c > 1 else ''} = <b>{sqrt_pi(val)}</b>."]
        correct, wrong = sqrt_pi(val), [sqrt_pi(val * 2), sqrt_pi(val / 2), times(val, "π"), sqrt_pi(Fr(c, s)), sqrt_pi(val * 4)]
    return {"prompt": prompt, "correct": correct, "distractors": wrong, "steps": steps,
            "explanation": "Integral Gauss dalam berbagai skala (statistika, difusi panas)."}


@register("fg.integral_gamma", FKG, (2, 3, 4))
def fg_integral(rng, tier):
    m, a = rng.randint(1, 4), rng.randint(1, 3)
    val = Fr(math.factorial(m), a ** (m + 1))
    return {"prompt": f"Hitung ∫<sub>0</sub><sup>∞</sup> x{sup(m) if m > 1 else ''}e<sup>−{a if a > 1 else ''}x</sup> dx dengan fungsi Gamma.", "correct": n(val),
            "distractors": [n(math.factorial(m)), n(Fr(math.factorial(m), a ** m)), n(Fr(1, a)), n(val * 2)],
            "steps": [f"Substitusi u = {a}x: ∫ = (1/{a}{sup(m + 1)})∫₀^∞ u{sup(m)}e⁻ᵘ du = Γ({m + 1})/{a ** (m + 1)}.", f"= {m}!/{a ** (m + 1)} = <b>{n(val)}</b>."],
            "explanation": "∫₀^∞ xⁿe^{−ax} dx = n!/a^{n+1}."}


@register("fg.beta", FKG, (3, 4, 5))
def fg_beta(rng, tier):
    p, q = rng.randint(1, 4), rng.randint(1, 4)
    val = Fr(math.factorial(p) * math.factorial(q), math.factorial(p + q + 1))
    return {"prompt": f"Hitung ∫<sub>0</sub><sup>1</sup> x{sup(p) if p > 1 else ''}(1 − x){sup(q) if q > 1 else ''} dx dengan fungsi Beta.", "correct": n(val),
            "distractors": [n(Fr(1, p + q + 1)), n(Fr(math.factorial(p + q), math.factorial(p + q + 1))), n(val * 2), n(Fr(1, (p + 1) * (q + 1)))],
            "steps": ["B(a, b) = ∫₀¹ x<sup>a−1</sup>(1 − x)<sup>b−1</sup> dx = Γ(a)Γ(b)/Γ(a + b).", f"a = {p + 1}, b = {q + 1}: {p}!·{q}!/{p + q + 1}!.", f"= <b>{n(val)}</b>."],
            "explanation": "Fungsi Beta: dasar distribusi Beta (statistika Bayes)."}


# ════════════════════════ Dasar analisis real ══════════════════════════════
@register("fa.archimedes", FKA, (1, 2))
def fa_arch(rng, tier):
    k = rng.randint(3, 500)
    if tier == 1:
        p, form = 1, rng.choice(["1/n", "1/n"])
    else:
        p, form = rng.randint(2, 9), rng.choice(["1/n", "1/n²", "1/√n"])
    eps = Fr(p, k)
    if form == "1/n":
        bound = 1 / eps
        N = math.floor(bound) + 1
        why = f"1/n &lt; {n(eps)} ⇔ n &gt; {n(bound)}."
    elif form == "1/n²":
        bound = 1 / eps
        N = math.isqrt(bound.numerator // bound.denominator) + 1
        while Fr(1, N * N) >= eps:
            N += 1
        while N > 1 and Fr(1, (N - 1) ** 2) < eps:
            N -= 1
        why = f"1/n² &lt; {n(eps)} ⇔ n² &gt; {n(bound)}."
    else:
        bound = (1 / eps) ** 2
        N = math.floor(bound) + 1
        why = f"1/√n &lt; {n(eps)} ⇔ √n &gt; {n(1 / eps)} ⇔ n &gt; {n(bound)}."
    return {"prompt": f"Berapa bilangan asli n terkecil sehingga {form} &lt; {n(eps)}?", "correct": str(N), "distractors": [str(N - 1), str(N + 1), str(k), str(2 * N)],
            "steps": [why, f"n terkecil = <b>{N}</b> (sifat Archimedes: selalu ada n seperti ini)."],
            "explanation": "Sifat Archimedes menjadi dasar setiap bukti ε–N."}


@register("fa.sup", FKA, (1, 2, 3))
def fa_sup(rng, tier):
    k, c = rng.randint(1, 9), rng.randint(-5, 5)
    b = rng.randint(2, 9)
    cases = [(f"{{{n(c)} − {b}/n : n ∈ ℕ}}", f"sup = {n(c)}, inf = {n(c - b)}", f"{c} − {b}/n naik mendekati {n(c)} (tak tercapai), terkecil saat n = 1: {n(c - b)}."),
             (f"{{{n(c)} + {b}/n : n ∈ ℕ}}", f"sup = {n(c + b)}, inf = {n(c)}", f"Terbesar saat n = 1: {n(c + b)}; turun mendekati {n(c)} (tak tercapai)."),
             (f"({n(c - k)}, {n(c + k)}]", f"sup = {n(c + k)}, inf = {n(c - k)}", "sup tercapai (anggota), inf tidak tercapai."),
             (f"{{x : |x − {paren(c)}| &lt; {k}}}".replace("− (−", "+ (").replace("+ (", "+ ").replace(")|", "|") if c < 0 else f"{{x : |x − {c}| &lt; {k}}}",
              f"sup = {n(c + k)}, inf = {n(c - k)}", f"himpunan = ({n(c - k)}, {n(c + k)})."),
             (f"{{n/(n + {k}) : n ∈ ℕ}}", f"sup = 1, inf = {n(Fr(1, k + 1))}", f"naik dari 1/{k + 1} (n = 1) menuju 1 (tak tercapai).")]
    if tier >= 2:
        cases += [("{(−1)ⁿ + 1/n : n ∈ ℕ}", "sup = 3/2, inf = −1", "n = 2 memberi 3/2 (terbesar); n ganjil memberi −1 + 1/n yang turun ke −1 (tak tercapai)."),
                  (f"{{x : x² &lt; {k * k}}}", f"sup = {k}, inf = {n(-k)}", f"himpunan = ({n(-k)}, {k})."),
                  (f"{{{b}(−1)ⁿ + {n(c)} : n ∈ ℕ}}", f"sup = {n(c + b)}, inf = {n(c - b)}", f"Himpunan hanya berisi dua nilai: {n(c - b)} dan {n(c + b)} (keduanya tercapai).")]
    s, ans, why = rng.choice(cases)
    pool = [c_[1] for c_ in cases if c_[1] != ans] + ["sup dan inf tidak ada"]
    return {"prompt": f"Tentukan supremum dan infimum himpunan {s}.", "correct": ans, "distractors": pool,
            "steps": ["sup = batas atas terkecil, inf = batas bawah terbesar (tidak harus anggota himpunan).", why, f"<b>{ans}</b>."],
            "explanation": "Aksioma kelengkapan: setiap himpunan tak kosong yang terbatas di atas punya supremum di ℝ."}


@register("fa.eps_n", FKA, (2, 3, 4, 5))
def fa_eps(rng, tier):
    a, c = rng.randint(1, 4), rng.randint(1, 3)
    b = rng.randint(1, 5)
    # aₙ = (a n + b)/(c n) → a/c ; |aₙ − a/c| = b/(c n) < ε ⇔ n > b/(c ε)
    eps = Fr(1, rng.choice([10, 100, 20, 50]))
    bound = Fr(b) / (c * eps)
    N = math.floor(bound) + 1
    return {"prompt": f"aₙ = ({a}n + {b})/({c if c > 1 else ''}n) → {n(Fr(a, c))}. Untuk ε = {n(eps)}, tentukan N terkecil agar |aₙ − {n(Fr(a, c))}| &lt; ε untuk semua n ≥ N.",
            "correct": str(N), "distractors": [str(N - 1), str(N + 1), str(int(1 / eps)), str(N * 2)],
            "steps": [f"|aₙ − {n(Fr(a, c))}| = {b}/({c}n).", f"{b}/({c}n) &lt; {n(eps)} ⇔ n &gt; {n(bound)}.", f"N = <b>{N}</b>."],
            "explanation": "Definisi limit barisan: ∀ε > 0 ∃N ∀n ≥ N: |aₙ − L| < ε."}


@register("fa.pernyataan", FKA, (3, 4, 5))
def fa_pernyataan(rng, tier):
    cases = [("Setiap barisan konvergen pasti terbatas.", "benar"), ("Setiap barisan terbatas pasti konvergen.", "salah (contoh (−1)ⁿ)"),
             ("Setiap barisan terbatas punya sub-barisan konvergen.", "benar (Bolzano–Weierstrass)"), ("Barisan Cauchy di ℝ pasti konvergen.", "benar (kelengkapan ℝ)"),
             ("Barisan Cauchy di ℚ pasti konvergen di ℚ.", "salah (contoh pendekatan desimal √2)"), ("Barisan monoton naik pasti konvergen.", "salah (contoh aₙ = n)")]
    s, ans = rng.choice(cases)
    opts = ["benar", "salah (contoh (−1)ⁿ)", "benar (Bolzano–Weierstrass)", "benar (kelengkapan ℝ)", "salah (contoh pendekatan desimal √2)", "salah (contoh aₙ = n)"]
    return {"prompt": f"Benar atau salah: “{s}”", "correct": ans, "distractors": [o for o in opts if o != ans],
            "steps": ["Periksa definisi, lalu cari bukti singkat atau contoh penyangkal.", f"<b>{ans}</b>."],
            "explanation": "Analisis real menuntut bukti atau contoh penyangkal, bukan intuisi grafik."}
