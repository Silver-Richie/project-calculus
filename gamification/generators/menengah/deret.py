"""
Sub-level: Barisan dan Deret Tak Hingga (Level Utama 3 — Kalkulus Menengah).
Rujukan: Stewart Bab 11; Whitman Bab 11; Strang (MIT) Bab 10.
"""

from fractions import Fraction as Fr
import math

from .. import register
from ..fmt import MINUS, fac, lin, n, paren, sqrt_simplify, sup, surd, terms, times
from ..graphs import fn, g2d, hline, param, pt, readout
from ..precalc.common import distinct, nz

BS, GM, UJ, PW = "km-der-barisan", "km-der-geometri", "km-der-uji", "km-der-pangkat"


def seq_graph(title, term_js, L, caption, N=30):
    return g2d(title, [0, N + 1], None or [float(L) - 3 if L is not None else -3, float(L) + 3 if L is not None else 3],
               [param("M", "Banyak suku ditampilkan", 1, N, 1, N, "N")],
               [{"type": "iter", "id": "S", "init": {"k": 1}, "update": {"k": "k+1"}, "steps": "M-1", "px": "k", "py": term_js, "color": "blue"}]
               + ([hline(float(L), "red")] if L is not None else []), None, caption)


# ════════════════════════ Topik 1: Barisan ═════════════════════════════════
@register("bs.suku", BS, (1, 2))
def suku(rng, tier):
    a, d = rng.randint(-5, 9), nz(rng, -4, 6)
    if tier == 1:
        terms = [a + d * i for i in range(4)]
        correct = f"aₙ = {n(a - d)} + {n(d)}n".replace("+ −", "− ") if a - d else f"aₙ = {n(d)}n"
        wrong = [f"aₙ = {n(a)} + {n(d)}n".replace("+ −", "− "), f"aₙ = {n(d)}n²", f"aₙ = {n(a)}·{n(d)}ⁿ", f"aₙ = {n(a + d)} + {n(d)}n".replace("+ −", "− ")]
        steps = [f"Selisih tetap {n(d)} ⇒ barisan aritmetika aₙ = a₁ + (n − 1)d.", f"aₙ = {n(a)} + (n − 1)·{paren(d)} = <b>{correct[5:]}</b>."]
    else:
        a, r = rng.randint(1, 5), rng.choice([2, 3, -2, Fr(1, 2)])
        terms = [a * r ** i for i in range(4)]
        correct = f"aₙ = {a}·{paren(r) if not isinstance(r, Fr) else '(' + n(r) + ')'}ⁿ⁻¹"
        wrong = [f"aₙ = {a}·{paren(r) if not isinstance(r, Fr) else '(' + n(r) + ')'}ⁿ", f"aₙ = {a} + {n(r)}n", f"aₙ = {n(r)}·{a}ⁿ⁻¹", f"aₙ = {a}n{sup(2)}"]
        steps = [f"Rasio tetap {n(r)} ⇒ barisan geometri aₙ = a₁rⁿ⁻¹.", f"<b>{correct}</b>."]
    return {"prompt": f"Tentukan rumus suku ke-n barisan {', '.join(n(t) for t in terms)}, …", "correct": correct, "distractors": wrong, "steps": steps,
            "explanation": "Kenali pola: selisih tetap (aritmetika) atau rasio tetap (geometri)."}


@register("bs.limit", BS, (1, 2, 3))
def bs_limit(rng, tier):
    if tier == 1:
        a, c = nz(rng, -6, 6), nz(rng, 1, 6)
        val = Fr(a, c)
        prompt, js = f"Hitung lim<sub>n→∞</sub> ({n(a)}n² + 3)/({c}n² − n).", f"({a}*k*k+3)/({c}*k*k-k)"
        steps = ["Bagi dengan n²: (a + 3/n²)/(c − 1/n).", f"→ {n(a)}/{c} = <b>{n(val)}</b>."]
        correct = n(val)
    elif tier == 2:
        a = nz(rng, -3, 3)
        correct, prompt, js = (f"e{sup(a)}" if a != 1 else "e"), f"Hitung lim<sub>n→∞</sub> (1 + {n(a)}/n)ⁿ.", f"pow(1+({a})/k,k)"
        steps = ["Limit baku (1 + a/n)ⁿ → eᵃ.", f"<b>{correct}</b>."]
        val = Fr(0)
    else:
        k = nz(rng, -8, 8)
        val = Fr(k, 2)
        prompt, js = f"Hitung lim<sub>n→∞</sub> (√(n² + {k}n) − n).".replace("+ −", "− "), f"sqrt(k*k+({k})*k)-k"
        steps = ["Kalikan sekawan: kn/(√(n² + kn) + n).", f"Bagi n: {k}/(√(1 + {k}/n) + 1) → {k}/2.", f"<b>{n(val)}</b>."]
        correct = n(val)
    wrong = ["0", "∞", "1", n(val * 2) if val else "e", n(val + 1)]
    L = float(val) if tier != 2 else (math.e ** a)
    return {"prompt": prompt, "correct": correct, "distractors": wrong, "steps": steps,
            "graphs": [seq_graph("Suku-suku barisan mendekati limit", js, L, "Titik-titik makin rapat ke garis merah.")],
            "explanation": "Limit barisan = limit fungsi f(x) untuk x → ∞ bila aₙ = f(n)."}


def quad_root(k, D):
    """(k + √D)/2 disederhanakan (D bukan kuadrat sempurna)."""
    c, r = sqrt_simplify(D)
    if k % 2 == 0 and c % 2 == 0:
        return f"{n(k // 2)} + {surd(c // 2, r)}" if k else surd(c // 2, r)
    return f"({n(k)} + {surd(c, r)})/2"


def quad_root_minus(k, D):
    c, r = sqrt_simplify(D)
    if k % 2 == 0 and c % 2 == 0:
        return f"{n(k // 2)} − {surd(c // 2, r)}"
    return f"({n(k)} − {surd(c, r)})/2"


def _iterate(f, a1, steps=400):
    a = a1
    for _ in range(steps):
        a = f(a)
    return a


@register("bs.rekursif", BS, (2, 3, 4, 5))
def rekursif(rng, tier):
    if tier <= 3:
        # aₙ₊₁ = √(c + d·aₙ): titik tetap L² = c + dL, dipilih L bulat > d sehingga c > 0
        d = rng.randint(1, 2) if tier == 2 else rng.randint(1, 4)
        L = rng.randint(d + 1, d + 7)
        c, a1 = L * L - d * L, rng.randint(0, L - 1)
        dtxt = "" if d == 1 else str(d)
        prompt = f"a₁ = {a1}, aₙ₊₁ = √({c} + {dtxt}aₙ). Barisan ini naik dan terbatas. Berapa limitnya?"
        steps = [f"Misal limit L: L = √({c} + {dtxt}L) ⇒ L² − {dtxt}L − {c} = 0.".replace("− 1L", "− L"),
                 f"(L − {L})(L + {L - d}) = 0 ⇒ L = {L} (akar lain negatif, padahal semua suku ≥ 0).", f"<b>{L}</b>."]
        return {"prompt": prompt, "correct": n(L), "distractors": [n(d - L), n(L + 1), n(c), n(L - 1), "∞"], "steps": steps,
                "explanation": "Teorema barisan monoton: monoton & terbatas ⇒ konvergen; limit didapat dari persamaan titik tetap."}
    if tier == 4:
        kind = rng.choice(["mobius", "mobius", "newton"])
        if kind == "newton":
            s, a1 = rng.randint(2, 12), rng.randint(1, 4)
            c = s * s
            prompt = f"Barisan Newton aₙ₊₁ = (aₙ + {c}/aₙ)/2 dengan a₁ = {a1} konvergen ke …"
            steps = [f"Limit L memenuhi L = (L + {c}/L)/2 ⇒ L² = {c}.", f"a₁ &gt; 0 ⇒ semua suku positif ⇒ L = <b>{s}</b> (metode Newton untuk √{c})."]
            return {"prompt": prompt, "correct": n(s), "distractors": [n(c), n(Fr(c, 2)), n(-s), n(s + 1)], "steps": steps,
                    "explanation": "Limit barisan rekursif konvergen adalah titik tetap fungsi iterasinya."}
        # aₙ₊₁ = (p·aₙ + q)/(aₙ + s) dengan titik tetap L (menarik) dan M (menolak)
        while True:
            L, M, s = rng.randint(1, 6), rng.randint(-6, 5), rng.randint(1, 6)
            p, q = s + L + M, -L * M
            if M == L or abs(s + M) >= abs(s + L) or (s + L) * (s + M) == 0:
                continue
            a1 = rng.choice([v for v in range(0, 5) if v != M])
            try:
                lim = _iterate(lambda a: (p * a + q) / (a + s), float(a1))
            except ZeroDivisionError:
                continue
            if abs(lim - L) < 1e-9:
                break
        num = terms([(p, "aₙ")], q)
        fl = lambda r: "L" if r == 0 else f"(L {MINUS if r > 0 else '+'} {abs(r)})"
        prompt = f"Barisan aₙ₊₁ = ({num})/(aₙ + {s}) dengan a₁ = {a1} diketahui konvergen. Berapa limitnya?"
        steps = [f"Limit L memenuhi L = ({terms([(p, 'L')], q)})/(L + {s}) ⇒ L² + {s}L = {terms([(p, 'L')], q)}.",
                 f"{terms([(1, 'L²'), (s - p, 'L')], -q)} = 0 ⇒ {fl(M) + fl(L) if M == 0 else fl(L) + fl(M)} = 0 ⇒ L = {L} atau L = {n(M)}.",
                 f"Titik tetap yang menarik adalah yang memenuhi |f′(L)| &lt; 1: f′(x) = {(s + L) * (s + M)}/(x + {s})², |f′({L})| = {n(Fr(abs(s + M), s + L))} &lt; 1, sedangkan |f′({n(M)})| = {n(Fr(abs(s + L), abs(s + M))) if s + M else '∞'} &gt; 1.",
                 f"Jadi limitnya <b>{L}</b>."]
        return {"prompt": prompt, "correct": n(L), "distractors": [n(M), n(L + 1), n(p), "divergen"], "steps": steps,
                "explanation": "Barisan rekursif aₙ₊₁ = f(aₙ) konvergen ke titik tetap yang menarik (|f′(L)| < 1)."}
    # tier 5: limit irasional berbentuk (k + √D)/2
    if rng.random() < 0.5:
        while True:
            k, m = rng.randint(1, 5), rng.randint(1, 8)
            D = k * k + 4 * m
            if math.isqrt(D) ** 2 != D:
                break
        prompt = f"aₙ₊₁ = {k} + {m}/aₙ, a₁ = 1. Barisan ini konvergen. Limitnya adalah …"
        steps = [f"L = {k} + {m}/L ⇒ L² − {k}L − {m} = 0.".replace(" 1L", " L"), f"L = ({k} ± √{D})/2; semua suku ≥ {k} &gt; 0 sehingga dipilih akar positif.",
                 f"<b>{quad_root(k, D)}</b>{' (rasio emas φ)' if (k, m) == (1, 1) else ''}."]
    else:
        while True:
            c = rng.randint(1, 14)
            D = 1 + 4 * c
            if math.isqrt(D) ** 2 != D:
                break
        k = 1
        prompt = f"aₙ₊₁ = √({c} + aₙ), a₁ = 0. Barisan ini naik dan terbatas. Limitnya adalah …"
        steps = [f"L = √({c} + L) ⇒ L² − L − {c} = 0.", f"L = (1 ± √{D})/2; L ≥ 0 sehingga dipilih akar positif.", f"<b>{quad_root(1, D)}</b>."]
    correct = quad_root(k, D)
    c_, r_ = sqrt_simplify(D)
    return {"prompt": prompt, "correct": correct, "distractors": [quad_root_minus(k, D), surd(c_, r_), f"{n(k)} + {surd(c_, r_)}", n(k + 1)], "steps": steps,
            "explanation": "Teorema barisan monoton: monoton & terbatas ⇒ konvergen; limit didapat dari persamaan titik tetap."}


@register("bs.apit", BS, (4, 5))
def apit(rng, tier):
    a, b, c, p = rng.randint(2, 9), rng.randint(1, 9), rng.randint(2, 9), rng.randint(1, 3)
    ns = "n" if p == 1 else f"n{sup(p)}"
    x, y = sorted(distinct(rng, 2, 9, 2))
    z = rng.randint(y + 1, 12)
    cases = [(f"sin({a}n)/({ns} + {b})", "0", f"−1/({ns} + {b}) ≤ aₙ ≤ 1/({ns} + {b}) dan kedua batas → 0."),
             (f"{c}·cos(n²)/{ns}", "0", f"|aₙ| ≤ {c}/{ns} → 0."),
             (f"(−1)ⁿ·{c}/{ns}", "0", f"|aₙ| = {c}/{ns} → 0."),
             (f"({x}ⁿ + {y}ⁿ)<sup>1/n</sup>", str(y), f"{y}ⁿ ≤ {x}ⁿ + {y}ⁿ ≤ 2·{y}ⁿ ⇒ {y} ≤ aₙ ≤ 2<sup>1/n</sup>·{y} → {y}."),
             (f"ⁿ√({c}n)", "1", f"ln aₙ = (ln {c} + ln n)/n → 0 ⇒ aₙ → e⁰ = 1."),
             (f"{c}ⁿ/n!", "0", f"Untuk n &gt; {2 * c}: setiap faktor tambahan {c}/k ≤ 1/2, sehingga aₙ ≤ K·(1/2)ⁿ → 0.")]
    if tier == 5:
        cases += [(f"({x}ⁿ + {y}ⁿ + {z}ⁿ)<sup>1/n</sup>", str(z), f"{z}ⁿ ≤ aₙⁿ ≤ 3·{z}ⁿ ⇒ {z} ≤ aₙ ≤ 3<sup>1/n</sup>·{z} → {z}."),
                  (f"n!/nⁿ", "0", "n!/nⁿ = (1/n)(2/n)…(n/n) ≤ 1/n → 0."),
                  (f"(n{sup(p + 1)} + {c})<sup>1/n</sup>", "1", f"1 ≤ aₙ ≤ (2n{sup(p + 1)})<sup>1/n</sup> = 2<sup>1/n</sup>(ⁿ√n){sup(p + 1)} → 1."),
                  (f"({y}ⁿ + n{sup(p)})<sup>1/n</sup>", str(y), f"{y}ⁿ ≤ aₙⁿ ≤ 2·{y}ⁿ untuk n besar (eksponensial mengalahkan polinom) ⇒ aₙ → {y}.")]
    term, ans, why = rng.choice(cases)
    return {"prompt": f"Hitung lim<sub>n→∞</sub> {term}.", "correct": ans, "distractors": [v for v in ["0", "1", "∞", "tidak ada", str(x), str(x + y), "e"] if v != ans],
            "steps": ["Teorema apit: bₙ ≤ aₙ ≤ cₙ dan bₙ, cₙ → L ⇒ aₙ → L.", why, f"<b>{ans}</b>."],
            "explanation": "Teorema apit menangani suku berosilasi, faktorial, dan akar ke-n."}


# ════════════════════════ Topik 2: Deret geometri & teleskopik ═════════════
@register("dg.jumlah", GM, (1, 2, 3))
def dg_jumlah(rng, tier):
    a = nz(rng, -6, 9)
    r = rng.choice([Fr(1, 2), Fr(1, 3), Fr(-1, 2), Fr(2, 3), Fr(-1, 3), Fr(3, 4)])
    start = 0 if tier == 1 else rng.choice([1, 2])
    first = a * r ** start
    S = first / (1 - r)
    prompt = f"Hitung Σ<sub>n={start}</sub><sup>∞</sup> {n(a)}·({n(r)})ⁿ."
    return {"prompt": prompt, "correct": n(S), "distractors": [n(Fr(a) / (1 - r)) if start else n(a / (1 + r)), n(S * 2), n(first / (1 + r)), "divergen"],
            "steps": ["Deret geometri Σ arⁿ konvergen ⇔ |r| &lt; 1, jumlahnya (suku pertama)/(1 − r).", f"Suku pertama (n = {start}): {n(first)}; r = {n(r)}.",
                      f"S = {n(first)}/(1 − {paren(r) if r > 0 else '(' + n(r) + ')'}) = <b>{n(S)}</b>."],
            "graphs": [g2d("Jumlah parsial menuju S", [0, 20], [float(S) - abs(float(S)) - 2, float(S) + abs(float(S)) + 2], [param("rr", "r", -0.95, 0.95, 0.05, float(r), "r")],
                           [{"type": "iter", "id": "P", "init": {"k": 0, "s": float(first)}, "update": {"k": "k+1", "s": f"s+{float(first)}*pow(rr,k+1)"}, "steps": 19,
                             "px": "k", "py": "s", "color": "blue"}, {"type": "hline", "y": f"{float(first)}/(1-rr)", "color": "red", "dash": True}],
                           [readout("S = a/(1 − r)", f"{float(first)}/(1-rr)", 5)], "r negatif: jumlah parsial berzig-zag; |r| dekat 1: konvergen lambat.")],
            "explanation": "Σ arⁿ = a/(1 − r) untuk |r| < 1."}


@register("dg.konvergen", GM, (1, 2))
def dg_konvergen(rng, tier):
    k = rng.randint(2, 6)
    if tier == 1:
        good = rng.choice([f"Σ (1/{k})ⁿ", f"Σ ({MINUS}{k - 1}/{k})ⁿ", f"Σ 5·(0,9)ⁿ"])
        return {"prompt": "Deret geometri manakah yang konvergen?", "correct": good, "distractors": [f"Σ ({k}/{k - 1})ⁿ", f"Σ ({MINUS}{k})ⁿ", "Σ 1ⁿ", "Σ (−1)ⁿ"],
                "steps": ["Konvergen ⇔ |r| &lt; 1.", f"<b>{good}</b> memiliki |r| &lt; 1; r = −1 dan r = 1 divergen."], "explanation": "Syarat konvergen deret geometri."}
    return {"prompt": f"Untuk x berapa deret Σ<sub>n=0</sub><sup>∞</sup> (x/{k})ⁿ konvergen, dan berapa jumlahnya?", "correct": f"|x| &lt; {k}, jumlah {k}/({k} − x)",
            "distractors": [f"|x| ≤ {k}, jumlah {k}/({k} − x)", f"|x| &lt; 1, jumlah 1/(1 − x)", f"|x| &lt; {k}, jumlah x/({k} − x)", f"x &lt; {k}, jumlah {k}/({k} − x)"],
            "steps": [f"r = x/{k}; konvergen ⇔ |x/{k}| &lt; 1 ⇔ |x| &lt; {k}.", f"Jumlah 1/(1 − x/{k}) = {k}/({k} − x)."], "explanation": "Deret geometri dengan rasio bergantung x adalah deret pangkat pertama."}


def _fac(a, b, var="n"):
    s = lin(a, b, var)
    return s if s == var else f"({s})"


@register("dg.teleskopik", GM, (2, 3, 4, 5))
def teleskopik(rng, tier):
    c = rng.randint(1, 6)
    if tier == 5 and rng.random() < 0.6:
        if rng.random() < 0.5:
            k = rng.randint(1, 4)
            n0 = k + 1
            val = Fr(c, 2 * k) * sum(Fr(1, j) for j in range(1, 2 * k + 1))
            prompt = f"Hitung Σ<sub>n={n0}</sub><sup>∞</sup> {c}/(n² − {k * k})."
            steps = [f"n² − {k * k} = (n − {k})(n + {k}) ⇒ {c}/(n² − {k * k}) = ({n(Fr(c, 2 * k))})[1/(n − {k}) − 1/(n + {k})].",
                     f"Suku positif 1/(n − {k}) memuat 1, 1/2, 1/3, …; suku negatif 1/(n + {k}) memuat 1/{2 * k + 1}, 1/{2 * k + 2}, … — yang tersisa 1 + 1/2 + … + 1/{2 * k}.",
                     f"Σ = ({n(Fr(c, 2 * k))})(1 + 1/2 + … + 1/{2 * k}) = <b>{n(val)}</b>."]
            first = Fr(c, 2 * k)
        else:
            n0 = rng.randint(1, 4)
            val = Fr(c, 2 * n0 * (n0 + 1))
            prompt = f"Hitung Σ<sub>n={n0}</sub><sup>∞</sup> {c}/(n(n + 1)(n + 2))."
            steps = ["1/(n(n + 1)(n + 2)) = (1/2)[1/(n(n + 1)) − 1/((n + 1)(n + 2))] — selisih dua suku berurutan.",
                     f"Teleskopik: tersisa (1/2)·1/({n0}·{n0 + 1}).", f"Dikali {c}: <b>{n(val)}</b>."]
            first = Fr(c, n0 * (n0 + 1))
        return {"prompt": prompt, "correct": n(val), "distractors": [n(val * 2), n(first), "divergen", n(val / 2), n(val + 1)], "steps": steps,
                "explanation": "Deret teleskopik: tulis suku sebagai selisih, sebagian besar suku saling menghapus."}
    if tier <= 3:
        a, b, k, n0 = 1, rng.randint(0, 1 if tier == 2 else 3), rng.randint(1, 2 if tier == 2 else 3), rng.randint(1, 2)
    else:
        a, k, n0 = rng.choice([2, 3]), rng.randint(1, 2), 1
        b = rng.choice([v for v in (-1, 1, 2) if a + v >= 1 and math.gcd(a, abs(v)) == 1])
    # c/((an + b)(a(n + k) + b)) = (c/(ak))[1/(an + b) − 1/(a(n + k) + b)]
    lead = Fr(c, a * k)
    left = [a * (n0 + j) + b for j in range(k)]
    val = lead * sum(Fr(1, v) for v in left)
    prompt = f"Hitung Σ<sub>n={n0}</sub><sup>∞</sup> {c}/({_fac(a, b)}{_fac(a, b + a * k)})."
    steps = [f"Pecahan parsial: {c}/({_fac(a, b)}{_fac(a, b + a * k)}) = ({n(lead)})[1/{_fac(a, b)} − 1/{_fac(a, b + a * k)}] (selisih penyebut {a * k}).",
             f"Suku positif 1/{_fac(a, b)} mulai dari n = {n0} tidak terhapus untuk {k} suku pertama: {' + '.join(f'1/{v}' if v != 1 else '1' for v in left)}.",
             f"Σ = ({n(lead)})({' + '.join(f'1/{v}' if v != 1 else '1' for v in left)}) = <b>{n(val)}</b>."]
    return {"prompt": prompt, "correct": n(val), "distractors": [n(val * a * k) if a * k > 1 else n(val * 2), n(lead * Fr(1, left[0])) if k > 1 else n(val / 2), "divergen", n(val + 1), n(val * 2)],
            "steps": steps, "explanation": "Deret teleskopik: tulis suku sebagai selisih, sebagian besar suku saling menghapus."}


@register("dg.desimal", GM, (2, 3))
def dg_desimal(rng, tier):
    d = rng.randint(1, 98)
    val = Fr(d, 99)
    s = f"{d:02d}"
    return {"prompt": f"Nyatakan 0,{s}{s}{s}… sebagai deret geometri dan hitung jumlahnya.", "correct": n(val),
            "distractors": [n(Fr(d, 100)), n(Fr(d, 90)), n(Fr(d, 999)), n(val + Fr(1, 99))],
            "steps": [f"0,{s}{s}… = {d}/100 + {d}/100² + … (a = {d}/100, r = 1/100).", f"S = ({d}/100)/(1 − 1/100) = {d}/99 = <b>{n(val)}</b>."],
            "explanation": "Desimal berulang = deret geometri."}


@register("dg.pantulan", GM, (4, 5))
def pantulan(rng, tier):
    h = rng.choice([2, 3, 4, 5, 10])
    r = rng.choice([Fr(1, 2), Fr(2, 3), Fr(3, 4), Fr(3, 5)])
    total = h + 2 * h * r / (1 - r)
    return {"prompt": f"Bola dijatuhkan dari ketinggian {h} m dan setiap pantulan mencapai {n(r)} tinggi sebelumnya. Berapa total jarak tempuh hingga berhenti?",
            "correct": f"{n(total)} m", "distractors": [f"{n(h / (1 - r))} m", f"{n(2 * h / (1 - r))} m", f"{n(total - h)} m", "tak hingga"],
            "steps": ["Jarak = turun pertama + 2×(semua tinggi pantulan).", f"Tinggi pantulan: {n(h * r)}, {n(h * r * r)}, … jumlah {n(h * r)}/(1 − {n(r)}) = {n(h * r / (1 - r))}.",
                      f"Total = {h} + 2·{n(h * r / (1 - r))} = <b>{n(total)} m</b>."], "explanation": "Model fisika dengan deret geometri (FT)."}


# ════════════════════════ Topik 3: Uji kekonvergenan ═══════════════════════
@register("du.divergensi", UJ, (1, 2))
def divergensi(rng, tier):
    a, b, c, k = rng.randint(1, 9), rng.randint(0, 9), rng.randint(1, 5), rng.randint(1, 5)
    L = n(Fr(a, c))
    cases = [(f"({terms([(a, 'n')], b)})/({terms([(c, 'n')], k)})", L), (f"({a}n² + 1)/({c}n² + n)", L),
             (f"cos({k}/n)", "1"), (f"(1 + {k}/n)ⁿ".replace("(1 + 1/n)", "(1 + 1/n)"), "e" if k == 1 else f"e{sup(k)}"),
             (f"n·sin({k}/n)", str(k)), (f"ⁿ√{a + 1}", "1"), (f"arctan({k}n)", "π/2")]
    term, lim = rng.choice(cases)
    ans = f"divergen (suku → {lim} ≠ 0)"
    return {"prompt": f"Apa kesimpulan uji suku ke-n untuk Σ {term}?", "correct": ans,
            "distractors": ["konvergen (suku menuju 0)", "uji tidak dapat menyimpulkan", "konvergen mutlak", f"konvergen ke {lim}"],
            "steps": ["Uji divergensi: jika lim aₙ ≠ 0 maka Σ aₙ divergen.", f"lim {term} = {lim} ≠ 0.", f"<b>{ans}</b>. (Catatan: aₙ → 0 saja tidak menjamin konvergen, contoh Σ 1/n.)"],
            "explanation": "Syarat perlu konvergen: aₙ → 0."}


@register("du.p_deret", UJ, (1, 2, 3))
def p_deret(rng, tier):
    p = rng.choice([Fr(2), Fr(3), Fr(1, 2), Fr(1), Fr(3, 2), Fr(4, 3), Fr(2, 3), Fr(5, 2), Fr(1, 3), Fr(5, 4)])
    c, k = rng.randint(1, 9), rng.randint(1, 9)
    if tier == 1:
        conv = p > 1
        prompt = f"Apakah deret Σ {c}/n<sup>{n(p)}</sup> konvergen?"
        why = f"Konstanta {c} tidak memengaruhi konvergensi; p = {n(p)} {'&gt;' if conv else '≤'} 1."
    elif tier == 2:
        conv = p > 1
        prompt = f"Apakah Σ {c}/(n<sup>{n(p)}</sup> + {k}) konvergen?"
        why = f"Untuk n besar suku ≈ {c}/n<sup>{n(p)}</sup>; uji banding limit dengan deret-p, p = {n(p)} {'&gt;' if conv else '≤'} 1."
    else:
        if rng.random() < 0.5:
            r, s = rng.randint(0, 3), rng.randint(1, 5)
            q = s - r
            conv = q > 1
            prompt = f"Apakah Σ {'n' if r == 1 else f'n{sup(r)}' if r else '1'}/(n{sup(s) if s > 1 else ''} + {k}) konvergen?"
            why = f"Suku ≈ n{sup(r) if r > 1 else '' if r else '⁰'}/n{sup(s) if s > 1 else ''} = 1/n{sup(q) if q != 1 else ''}: deret-p dengan p = {q} {'&gt;' if conv else '≤'} 1.".replace("n⁰", "1")
        else:
            conv = p > 1
            prompt = f"Apakah Σ<sub>n≥2</sub> 1/(n (ln n)<sup>{n(p)}</sup>) konvergen?"
            why = f"Uji integral: u = ln x mengubah ∫ dx/(x (ln x)ᵖ) menjadi ∫ du/uᵖ — konvergen ⇔ p &gt; 1; p = {n(p)}."
    ans = "konvergen" if conv else "divergen"
    return {"prompt": prompt, "correct": ans, "distractors": ["divergen" if conv else "konvergen", "konvergen ke 1", "tidak dapat ditentukan"],
            "steps": ["Deret-p Σ 1/nᵖ konvergen ⇔ p &gt; 1 (uji integral: ∫₁^∞ x⁻ᵖ dx).", why, f"<b>{ans}</b>."],
            "graphs": [g2d("Jumlah parsial Σ 1/nᵖ", [0, 60], [0, 8], [param("pp", "p", 0.5, 3, 0.05, float(p), "p")],
                           [{"type": "iter", "id": "P", "init": {"k": 1, "s": 1}, "update": {"k": "k+1", "s": "s+pow(k+1,-pp)"}, "steps": 59, "px": "k", "py": "s", "color": "blue"}],
                           None, "p ≤ 1: jumlah parsial terus naik (lambat); p > 1: melandai ke suatu nilai.")],
            "explanation": "Deret harmonik Σ 1/n (p = 1) divergen."}


@register("du.rasio", UJ, (2, 3, 4))
def rasio(rng, tier):
    c = rng.randint(2, 5)
    k = rng.randint(1, 4)
    form = rng.choice(["poly_exp", "exp_fact", "fact_exp"]) if tier >= 3 else "poly_exp"
    if form == "poly_exp":
        term, L, ans = f"n{sup(k)}/{c}ⁿ", Fr(1, c), "konvergen"
        why = f"aₙ₊₁/aₙ = ((n + 1)/n){sup(k)}·1/{c} → 1/{c}."
    elif form == "exp_fact":
        term, L, ans = f"{c}ⁿ/n!", Fr(0), "konvergen"
        why = f"aₙ₊₁/aₙ = {c}/(n + 1) → 0."
    else:
        term, L, ans = f"n!/{c}ⁿ", None, "divergen"
        why = f"aₙ₊₁/aₙ = (n + 1)/{c} → ∞."
    correct = f"L = {n(L) if L is not None else '∞'}, {ans}"
    return {"prompt": f"Gunakan uji rasio untuk Σ {term}.", "correct": correct,
            "distractors": [f"L = {n(L) if L is not None else '∞'}, {'divergen' if ans == 'konvergen' else 'konvergen'}", f"L = 1, uji gagal", f"L = {c}, divergen", f"L = {n(Fr(1, c)) if L != Fr(1, c) else '0'}, konvergen"],
            "steps": ["Uji rasio: L = lim |aₙ₊₁/aₙ|; L &lt; 1 konvergen mutlak, L &gt; 1 divergen, L = 1 tidak dapat disimpulkan.", why, f"<b>{correct}</b>."],
            "explanation": "Uji rasio cocok untuk faktorial dan pangkat eksponensial."}


@register("du.banding", UJ, (3, 4, 5))
def du_banding(rng, tier):
    k = rng.randint(1, 9)
    cases = [(f"1/(n² + {k})", "konvergen", "≤ 1/n² (deret-p, p = 2)."), (f"1/(2ⁿ + {k})", "konvergen", "≤ (1/2)ⁿ (geometri)."),
             (f"1/(n + {k})", "divergen", "≈ 1/n (harmonik); uji banding limit memberi 1."), (f"ln n / n", "divergen", "≥ 1/n untuk n ≥ 3."),
             (f"1/(n·ln n) (n ≥ 2)", "divergen", "uji integral: ∫ dx/(x ln x) = ln(ln x) → ∞."), (f"1/(n (ln n)²) (n ≥ 2)", "konvergen", "uji integral: ∫ dx/(x ln²x) = −1/ln x terbatas.")]
    term, ans, why = rng.choice(cases[:4] if tier < 5 else cases)
    return {"prompt": f"Apakah Σ {term} konvergen?", "correct": ans, "distractors": ["divergen" if ans == "konvergen" else "konvergen", "konvergen bersyarat", "tidak dapat ditentukan"],
            "steps": ["Bandingkan dengan deret yang diketahui (deret-p, geometri) atau gunakan uji integral.", why, f"<b>{ans}</b>."],
            "explanation": "Uji banding & uji integral (Stewart §11.3–11.4)."}


@register("du.alternating", UJ, (4, 5))
def alternating(rng, tier):
    if tier == 5 and rng.random() < 0.4:
        k = rng.randint(1, 9)
        if k == 1:
            prompt, correct = "Berapa jumlah deret harmonik bergantian 1 − 1/2 + 1/3 − 1/4 + …?", "ln 2"
        else:
            prompt, correct = f"Berapa jumlah Σ<sub>n≥1</sub> (−1)ⁿ⁺¹/(n·{k}ⁿ)?", f"ln({k + 1}/{k})"
        return {"prompt": prompt, "correct": correct, "distractors": ["1", f"ln {k + 1}", "divergen", f"1/{k + 1}", "π/4"],
                "steps": ["Deret Maclaurin ln(1 + x) = x − x²/2 + x³/3 − … berlaku untuk −1 &lt; x ≤ 1.", f"Substitusi x = {'1' if k == 1 else f'1/{k}'} ⇒ jumlah <b>{correct}</b>.",
                          "Untuk x = 1 deret konvergen bersyarat: menyusun ulang suku dapat mengubah jumlahnya (teorema Riemann)."],
                "explanation": "Deret bergantian bisa konvergen walau deret nilai mutlaknya divergen."}
    r, s, k = rng.randint(0, 2), rng.randint(1, 4), rng.randint(1, 9)
    q = Fr(s - r) if rng.random() < 0.6 else rng.choice([Fr(1, 2), Fr(3, 2), Fr(1, 3), Fr(5, 2)])
    if q.denominator == 1 and rng.random() < 0.6:
        num = "n" if r == 1 else f"n{sup(r)}" if r else "1"
        term = f"(−1)ⁿ·{num}/(n{sup(s) if s > 1 else ''} + {k})"
        q = Fr(s - r)
    else:
        term = f"(−1)ⁿ·{k}/n<sup>{n(q)}</sup>"
    ans = "konvergen mutlak" if q > 1 else "konvergen bersyarat" if q > 0 else "divergen"
    return {"prompt": f"Klasifikasikan deret Σ {term}.", "correct": ans, "distractors": [v for v in ["konvergen mutlak", "konvergen bersyarat", "divergen", "konvergen ke 0"] if v != ans],
            "steps": [f"|aₙ| berperilaku seperti 1/n<sup>{n(q)}</sup>.",
                      "q ≤ 0: suku tidak menuju 0 ⇒ divergen." if q <= 0 else f"Uji deret bergantian: |aₙ| akhirnya turun dan → 0 ⇒ Σ aₙ konvergen; Σ |aₙ| deret-p dengan p = {n(q)}: {'konvergen' if q > 1 else 'divergen'}.",
                      f"<b>{ans}</b>."],
            "explanation": "Mutlak: Σ|aₙ| konvergen. Bersyarat: Σ aₙ konvergen tetapi Σ|aₙ| divergen."}


# ════════════════════════ Topik 4: Deret pangkat & Taylor ══════════════════
@register("dp.dikenal", PW, (1, 2))
def dikenal(rng, tier):
    a = rng.randint(1, 5)
    ax = "x" if a == 1 else f"{a}x"
    A = "x" if a == 1 else f"({a}x)"
    cases = [(f"Σ {A}ⁿ/n!", f"e<sup>{ax}</sup>" if a > 1 else "eˣ"), (f"Σ (−1)ⁿ{A}<sup>2n+1</sup>/(2n + 1)!", f"sin({ax})" if a > 1 else "sin x"),
             (f"Σ (−1)ⁿ{A}<sup>2n</sup>/(2n)!", f"cos({ax})" if a > 1 else "cos x"), (f"Σ {A}ⁿ (|x| &lt; {n(Fr(1, a))})", f"1/(1 − {ax})")]
    if tier == 2:
        cases += [(f"Σ (−1)ⁿ{A}<sup>2n</sup> (|x| &lt; {n(Fr(1, a))})", f"1/(1 + {a * a if a > 1 else ''}x²)"),
                  (f"Σ<sub>n≥1</sub> (−1)ⁿ⁺¹{A}ⁿ/n", f"ln(1 + {ax})"), (f"Σ xⁿ⁺{a}/n!", f"x{sup(a) if a > 1 else ''}eˣ")]
    series, f = rng.choice(cases)
    return {"prompt": f"Deret Maclaurin {series} adalah ekspansi dari fungsi …", "correct": f, "distractors": [c[1] for c in cases if c[1] != f] + [f"e<sup>−{ax}</sup>"],
            "steps": ["Hafalkan deret Maclaurin dasar: eᵘ, sin u, cos u, 1/(1 − u), ln(1 + u).", f"Di sini u = {ax} (substitusi ke deret baku): <b>{f}</b>."],
            "graphs": [g2d("Polinom Taylor menghampiri eˣ", [-3, 3], [-2, 12], [param("N", "derajat N", 0, 10, 1, 3, "N")],
                           [fn("exp(x)", "blue", "eˣ"), fn("sum(0,N,k=>pow(x,k)/fact(k))", "red", "Tₙ(x)", dash=True)], None, "Naikkan N: polinom makin berimpit dengan eˣ.")],
            "explanation": "f(x) = Σ f⁽ⁿ⁾(0)xⁿ/n! (Maclaurin); substitusi u = ax memberi deret baru tanpa menurunkan ulang."}


@register("dp.jari_jari", PW, (1, 2, 3))
def jari_jari(rng, tier):
    c, k = rng.randint(2, 9), rng.randint(1, 3)
    if tier == 1:
        term, ans = rng.choice([(f"xⁿ/{c}ⁿ", f"R = {c}"), ("xⁿ/n!", "R = ∞"), ("n!·xⁿ", "R = 0"), (f"{c}ⁿxⁿ", f"R = 1/{c}"),
                                (f"n{sup(k) if k > 1 else ''}xⁿ/{c}ⁿ", f"R = {c}"), (f"xⁿ/(n{sup(k) if k > 1 else ''}·{c}ⁿ)", f"R = {c}"), (f"{c}ⁿxⁿ/n!", "R = ∞")])
        steps = ["Uji rasio: |aₙ₊₁xⁿ⁺¹/(aₙxⁿ)| &lt; 1 (faktor polinom nᵏ tidak memengaruhi R).", f"Hasil: <b>{ans}</b>."]
        prompt = f"Tentukan jari-jari kekonvergenan Σ {term}."
        wrong = [o for o in [f"R = {c}", "R = ∞", "R = 0", "R = 1", f"R = 1/{c}"] if o != ans]
    else:
        a = rng.randint(-4, 4)
        p = rng.choice([1, 1, 2]) if tier == 3 else 1
        sign = rng.choice([1, -1]) if tier == 3 else 1
        lo, hi = a - c, a + c
        if p == 2:
            ans, endtxt = f"[{n(lo)}, {n(hi)}]", "Kedua ujung: Σ (±1)ⁿ/n² konvergen mutlak."
        elif sign == 1:
            ans, endtxt = f"[{n(lo)}, {n(hi)})", f"Ujung x = {n(hi)}: Σ 1/n divergen; x = {n(lo)}: Σ (−1)ⁿ/n konvergen."
        else:
            ans, endtxt = f"({n(lo)}, {n(hi)}]", f"Ujung x = {n(hi)}: Σ (−1)ⁿ/n konvergen; x = {n(lo)}: Σ 1/n divergen."
        sg = "(−1)ⁿ" if sign < 0 else ""
        prompt = f"Tentukan interval kekonvergenan Σ<sub>n≥1</sub> {sg}{fac(a)}ⁿ/(n{sup(2) if p == 2 else ''}·{c}ⁿ)."
        steps = [f"Uji rasio ⇒ |x − {paren(a)}| &lt; {c} ⇒ R = {c}, pusat {n(a)}.", endtxt, f"Interval: <b>{ans}</b>."]
        wrong = [w for w in [f"({n(lo)}, {n(hi)}]", f"[{n(lo)}, {n(hi)}]", f"({n(lo)}, {n(hi)})", f"[{n(lo)}, {n(hi)})", f"[{n(-c)}, {n(c)})"] if w != ans]
    return {"prompt": prompt, "correct": ans, "distractors": wrong, "steps": steps, "explanation": "Deret pangkat konvergen pada interval berpusat a; ujung diuji terpisah."}


@register("dp.koefisien", PW, (2, 3, 4))
def koefisien(rng, tier):
    a = nz(rng, -3, 3)
    k = rng.randint(2, 5)
    f = rng.choice(["exp", "geom"] if tier == 2 else ["exp", "geom", "sin"])
    if f == "exp":
        val = Fr(a ** k, math.factorial(k))
        prompt = f"Koefisien x{sup(k)} pada deret Maclaurin e<sup>{n(a)}x</sup> adalah …"
        steps = [f"e<sup>u</sup> = Σ uⁿ/n!, u = {n(a)}x.", f"Koefisien x{sup(k)}: {n(a)}{sup(k)}/{k}! = <b>{n(val)}</b>."]
    elif f == "geom":
        val = Fr(a) ** k
        prompt = f"Koefisien x{sup(k)} pada deret Maclaurin 1/(1 − {n(a)}x) adalah …"
        steps = [f"1/(1 − u) = Σ uⁿ, u = {n(a)}x.", f"Koefisien x{sup(k)}: {paren(a)}{sup(k)} = <b>{n(val)}</b>."]
    else:
        k = rng.choice([3, 5])
        sign = -1 if k % 4 == 3 else 1
        val = Fr(sign * a ** k, math.factorial(k))
        prompt = f"Koefisien x{sup(k)} pada deret Maclaurin sin({n(a)}x) adalah …"
        steps = [f"sin u = u − u³/3! + u⁵/5! − …, u = {n(a)}x.", f"Koefisien x{sup(k)}: {'−' if sign < 0 else ''}{n(a)}{sup(k)}/{k}! = <b>{n(val)}</b>."]
    return {"prompt": prompt, "correct": n(val), "distractors": [n(-val), n(Fr(a) ** k), n(Fr(a, math.factorial(k))), n(val * k)], "steps": steps,
            "explanation": "Substitusi ke deret baku lebih cepat daripada menurunkan berulang."}


@register("dp.turunan_ke_n", PW, (4, 5))
def turunan_ke_n(rng, tier):
    m, a = rng.randint(1, 3), rng.choice([1, 1, 2, -1, 3])
    k = m + rng.randint(1, 4)
    # f = x^m e^{ax} = Σ aⁿ x^{n+m}/n! ⇒ koef x^k = a^{k−m}/(k − m)! ⇒ f^(k)(0) = k!·a^{k−m}/(k − m)!
    val = math.factorial(k) * a ** (k - m) // math.factorial(k - m)
    e = "eˣ" if a == 1 else "e⁻ˣ" if a == -1 else f"e<sup>{a}x</sup>"
    return {"prompt": f"Untuk f(x) = x{sup(m) if m > 1 else ''}{e}, hitung f<sup>({k})</sup>(0) memakai deret Maclaurin.", "correct": n(val),
            "distractors": [n(math.factorial(k)), n(Fr(a ** (k - m), math.factorial(k - m))), n(val * 2), n(-val) if val else "1"],
            "steps": [f"x{sup(m) if m > 1 else ''}{e} = Σ {paren(a)}ⁿxⁿ⁺{m}/n!; koefisien x{sup(k)} = {paren(a)}{sup(k - m)}/({k} − {m})!.",
                      f"f<sup>({k})</sup>(0) = {k}!·(koefisien) = {k}!·{paren(a)}{sup(k - m)}/{k - m}!.", f"= <b>{n(val)}</b>."],
            "explanation": "Koefisien deret Taylor cₖ = f⁽ᵏ⁾(0)/k!."}


@register("dp.jumlah_deret", PW, (3, 4, 5))
def jumlah_deret(rng, tier):
    k, c = rng.randint(2, 9), rng.randint(1, 4)
    C = "" if c == 1 else str(c)
    if tier <= 4:
        if tier == 3 or rng.random() < 0.5:
            val = Fr(c * k, (k - 1) ** 2)
            prompt = f"Hitung Σ<sub>n=1</sub><sup>∞</sup> {C}n/{k}ⁿ."
            steps = ["Turunkan Σ xⁿ = 1/(1 − x): Σ n xⁿ = x/(1 − x)².", f"x = 1/{k}: (1/{k})/(1 − 1/{k})² = {n(Fr(k, (k - 1) ** 2))}{f', dikali {c}' if c > 1 else ''} = <b>{n(val)}</b>."]
        else:
            val = Fr(c * k * (k + 1), (k - 1) ** 3)
            prompt = f"Hitung Σ<sub>n=1</sub><sup>∞</sup> {C}n²/{k}ⁿ."
            steps = ["Turunkan dua kali: Σ n² xⁿ = x(1 + x)/(1 − x)³.", f"x = 1/{k}: = {n(Fr(k * (k + 1), (k - 1) ** 3))}{f', dikali {c}' if c > 1 else ''} = <b>{n(val)}</b>."]
        correct = n(val)
        wrong = [n(Fr(c, k - 1)), n(Fr(c * k, k - 1)), "divergen", n(val * 2), n(Fr(c * k * k, (k - 1) ** 2))]
    else:
        kind = rng.choice(["exp", "cos", "sin", "ln", "expm1"])
        if kind == "exp":
            prompt, correct = f"Hitung Σ<sub>n=0</sub><sup>∞</sup> {C}·{k}ⁿ/n!.".replace("> ·", "> "), f"{C}e{sup(k)}"
            steps = [f"Σ xⁿ/n! = eˣ dengan x = {k}.", f"= <b>{correct}</b>."]
        elif kind == "cos":
            prompt, correct = f"Hitung Σ<sub>n=0</sub><sup>∞</sup> (−1)ⁿ{k}<sup>2n</sup>/(2n)!.", f"cos {k}"
            steps = [f"Σ (−1)ⁿx<sup>2n</sup>/(2n)! = cos x dengan x = {k}.", f"<b>{correct}</b>."]
        elif kind == "sin":
            prompt, correct = f"Hitung Σ<sub>n=0</sub><sup>∞</sup> (−1)ⁿ{k}<sup>2n+1</sup>/(2n + 1)!.", f"sin {k}"
            steps = [f"Σ (−1)ⁿx<sup>2n+1</sup>/(2n + 1)! = sin x dengan x = {k}.", f"<b>{correct}</b>."]
        elif kind == "ln":
            prompt, correct = f"Hitung Σ<sub>n=1</sub><sup>∞</sup> 1/(n·{k}ⁿ).", f"ln({k}/{k - 1})" if k > 2 else "ln 2"
            steps = ["Σ xⁿ/n = −ln(1 − x) untuk |x| &lt; 1.", f"x = 1/{k}: −ln(1 − 1/{k}) = <b>{correct}</b>."]
        else:
            prompt, correct = f"Hitung Σ<sub>n=0</sub><sup>∞</sup> {k}ⁿ/(n + 1)!.", f"(e{sup(k)} − 1)/{k}"
            steps = [f"Σ xⁿ/(n + 1)! = (1/x)Σ xⁿ⁺¹/(n + 1)! = (eˣ − 1)/x.", f"x = {k}: <b>{correct}</b>."]
        wrong = [f"e{sup(k)}" if correct != f"e{sup(k)}" else f"e{sup(k + 1)}", f"e{sup(k - 1)}", "divergen", f"cos {k}" if kind != "cos" else f"sin {k}", f"ln {k}"]
    return {"prompt": prompt, "correct": correct, "distractors": wrong,
            "steps": steps, "explanation": "Turunkan/integralkan deret pangkat suku demi suku di dalam jari-jari kekonvergenan; kenali deret baku."}
