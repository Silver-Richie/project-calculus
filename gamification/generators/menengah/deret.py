"""
Sub-level: Barisan dan Deret Tak Hingga (Level Utama 3 — Kalkulus Menengah).
Rujukan: Stewart Bab 11; Whitman Bab 11; Strang (MIT) Bab 10.
"""

from fractions import Fraction as Fr
import math

from .. import register
from ..fmt import MINUS, n, paren, sup
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


@register("bs.rekursif", BS, (2, 3, 4, 5))
def rekursif(rng, tier):
    if tier <= 3:
        m = rng.randint(2, 6)
        c = m * (m - 1)
        prompt = f"a₁ = 1, aₙ₊₁ = √({c} + aₙ). Barisan ini naik dan terbatas. Berapa limitnya?"
        correct = n(m)
        steps = ["Misal limit L: L = √(" + str(c) + " + L) ⇒ L² − L − " + str(c) + " = 0.", f"(L − {m})(L + {m - 1}) = 0 ⇒ L = {m} (L &gt; 0).", f"<b>{m}</b>."]
        wrong = [n(m - 1), n(c), "∞", n(m + 1)]
        js = None
    elif tier == 4:
        s = rng.randint(2, 9)
        c = s * s
        prompt = f"Barisan Newton aₙ₊₁ = (aₙ + {c}/aₙ)/2 dengan a₁ = 1 konvergen ke …"
        correct = n(s)
        steps = [f"Limit L memenuhi L = (L + {c}/L)/2 ⇒ L² = {c}.", f"a₁ &gt; 0 ⇒ semua suku positif ⇒ L = <b>{s}</b> (metode Newton untuk √{c}, Fasilkom)."]
        wrong = [n(c), n(Fr(c, 2)), "1", n(s + 1)]
    else:
        prompt = "aₙ₊₁ = 1 + 1/aₙ, a₁ = 1 (1, 2, 3/2, 5/3, …). Limitnya adalah …"
        correct = "(1 + √5)/2"
        steps = ["Rasio bilangan Fibonacci berturutan.", "L = 1 + 1/L ⇒ L² − L − 1 = 0.", "L &gt; 0 ⇒ <b>(1 + √5)/2</b> (rasio emas φ)."]
        wrong = ["(1 − √5)/2", "2", "√5", "3/2"]
    return {"prompt": prompt, "correct": correct, "distractors": wrong, "steps": steps,
            "explanation": "Teorema barisan monoton: monoton & terbatas ⇒ konvergen; limit didapat dari persamaan titik tetap."}


@register("bs.apit", BS, (4, 5))
def apit(rng, tier):
    cases = [("sin(n)/n", "0", "−1/n ≤ sin n / n ≤ 1/n dan kedua batas → 0."),
             ("(−1)ⁿ/n²", "0", "|aₙ| ≤ 1/n² → 0."),
             ("n!/nⁿ", "0", "n!/nⁿ = (1/n)(2/n)…(n/n) ≤ 1/n → 0."),
             ("ⁿ√n", "1", "ln ⁿ√n = (ln n)/n → 0 ⇒ ⁿ√n → e⁰ = 1."),
             ("(2ⁿ + 3ⁿ)<sup>1/n</sup>", "3", "3ⁿ ≤ 2ⁿ + 3ⁿ ≤ 2·3ⁿ ⇒ 3 ≤ aₙ ≤ 2<sup>1/n</sup>·3 → 3.")]
    term, ans, why = rng.choice(cases if tier == 5 else cases[:4])
    return {"prompt": f"Hitung lim<sub>n→∞</sub> {term}.", "correct": ans, "distractors": [v for v in ["0", "1", "∞", "tidak ada", "3", "e"] if v != ans],
            "steps": ["Teorema apit: bn ≤ aₙ ≤ cₙ, bn, cₙ → L ⇒ aₙ → L.", why, f"<b>{ans}</b>."],
            "explanation": "Teorema apit menangani suku berosilasi atau faktorial."}


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


@register("dg.teleskopik", GM, (2, 3, 4, 5))
def teleskopik(rng, tier):
    if tier <= 3:
        k = rng.randint(1, 3)
        val = Fr(1, k) * sum(Fr(1, j) for j in range(1, k + 1))
        prompt = f"Hitung Σ<sub>n=1</sub><sup>∞</sup> 1/(n(n + {k}))." if k > 1 else "Hitung Σ<sub>n=1</sub><sup>∞</sup> 1/(n(n + 1))."
        steps = [f"1/(n(n + {k})) = (1/{k})[1/n − 1/(n + {k})].", f"Teleskopik: tersisa (1/{k})(1 + 1/2 + … + 1/{k}).", f"= <b>{n(val)}</b>."]
    elif tier == 4:
        val = Fr(1, 2)
        prompt = "Hitung Σ<sub>n=1</sub><sup>∞</sup> 1/((2n − 1)(2n + 1))."
        steps = ["= (1/2)[1/(2n − 1) − 1/(2n + 1)].", "Teleskopik: (1/2)(1 − 0).", "<b>1/2</b>."]
    else:
        val = Fr(3, 2)
        prompt = "Hitung Σ<sub>n=2</sub><sup>∞</sup> 2/(n² − 1)."
        steps = ["2/(n² − 1) = 1/(n − 1) − 1/(n + 1).", "Jumlah parsial: (1 − 1/3) + (1/2 − 1/4) + (1/3 − 1/5) + … — yang tidak terhapus hanya 1 dan 1/2.",
                 "Σ = 1 + 1/2 = <b>3/2</b>."]
    return {"prompt": prompt, "correct": n(val), "distractors": [n(val * 2), "1", "divergen", n(val / 2)], "steps": steps,
            "explanation": "Deret teleskopik: tulis suku sebagai selisih, sebagian besar suku saling menghapus."}


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
    k = rng.randint(1, 5)
    term, ans = rng.choice([(f"n/(n + {k})", "divergen (suku → 1 ≠ 0)"), (f"({k}n² + 1)/(n² + {k})", f"divergen (suku → {k} ≠ 0)"),
                            ("cos(1/n)", "divergen (suku → 1 ≠ 0)"), (f"(1 + 1/n)ⁿ", "divergen (suku → e ≠ 0)")])
    return {"prompt": f"Apa kesimpulan uji suku ke-n untuk Σ {term}?", "correct": ans,
            "distractors": ["konvergen (suku menuju 0)", "uji tidak dapat menyimpulkan", "konvergen mutlak", "konvergen bersyarat"],
            "steps": ["Uji divergensi: jika lim aₙ ≠ 0 maka Σ aₙ divergen.", f"Suku {term} tidak menuju 0.", f"<b>{ans}</b>. (Catatan: aₙ → 0 saja tidak menjamin konvergen, contoh Σ 1/n.)"],
            "explanation": "Syarat perlu konvergen: aₙ → 0."}


@register("du.p_deret", UJ, (1, 2, 3))
def p_deret(rng, tier):
    p = rng.choice([Fr(2), Fr(3), Fr(1, 2), Fr(1), Fr(3, 2), Fr(4, 3), Fr(2, 3)])
    conv = p > 1
    ans = "konvergen" if conv else "divergen"
    if tier == 1:
        prompt = f"Apakah deret-p Σ 1/n<sup>{n(p)}</sup> konvergen?"
        why = f"p = {n(p)} {'&gt;' if conv else '≤'} 1."
    else:
        c = rng.randint(1, 9)
        prompt = f"Apakah Σ {c}/(n<sup>{n(p)}</sup> + {c}) konvergen?"
        why = f"Untuk n besar suku ≈ {c}/n<sup>{n(p)}</sup>; uji banding limit dengan deret-p, p = {n(p)} {'&gt;' if conv else '≤'} 1."
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
    p = rng.choice([Fr(1), Fr(1, 2), Fr(2), Fr(3, 2), Fr(1, 3)])
    if p > 1:
        ans = "konvergen mutlak"
    else:
        ans = "konvergen bersyarat"
    if tier == 5 and rng.random() < 0.4:
        return {"prompt": "Berapa jumlah deret harmonik bergantian 1 − 1/2 + 1/3 − 1/4 + …?", "correct": "ln 2",
                "distractors": ["1", "1/2", "divergen", "π/4"],
                "steps": ["Deret Maclaurin ln(1 + x) = x − x²/2 + x³/3 − … berlaku untuk −1 &lt; x ≤ 1.", "Substitusi x = 1 ⇒ jumlah <b>ln 2</b>.",
                          "Deret ini konvergen bersyarat: menyusun ulang suku dapat mengubah jumlahnya (teorema Riemann)."],
                "explanation": "Deret bergantian bisa konvergen walau deret nilai mutlaknya divergen."}
    return {"prompt": f"Klasifikasikan deret Σ (−1)ⁿ/n<sup>{n(p)}</sup>.", "correct": ans, "distractors": [v for v in ["konvergen mutlak", "konvergen bersyarat", "divergen", "konvergen ke 0"] if v != ans],
            "steps": ["Uji deret bergantian: bₙ = 1/nᵖ turun dan → 0 ⇒ deret konvergen.", f"Σ |aₙ| = Σ 1/nᵖ dengan p = {n(p)}: {'konvergen' if p > 1 else 'divergen'}.",
                      f"<b>{ans}</b>."],
            "explanation": "Mutlak: Σ|aₙ| konvergen. Bersyarat: Σ aₙ konvergen tetapi Σ|aₙ| divergen."}


# ════════════════════════ Topik 4: Deret pangkat & Taylor ══════════════════
@register("dp.dikenal", PW, (1, 2))
def dikenal(rng, tier):
    cases = [("Σ xⁿ/n!", "eˣ"), ("Σ (−1)ⁿx²ⁿ⁺¹/(2n + 1)!", "sin x"), ("Σ (−1)ⁿx²ⁿ/(2n)!", "cos x"), ("Σ xⁿ (|x| &lt; 1)", "1/(1 − x)"),
             ("Σ (−1)ⁿ⁺¹xⁿ/n (n ≥ 1)", "ln(1 + x)")]
    series, f = rng.choice(cases if tier == 2 else cases[:4])
    return {"prompt": f"Deret Maclaurin {series} adalah ekspansi dari fungsi …", "correct": f, "distractors": [c[1] for c in cases if c[1] != f],
            "steps": ["Hafalkan deret Maclaurin dasar: eˣ, sin x, cos x, 1/(1 − x), ln(1 + x).", f"<b>{f}</b>."],
            "graphs": [g2d("Polinom Taylor menghampiri eˣ", [-3, 3], [-2, 12], [param("N", "derajat N", 0, 10, 1, 3, "N")],
                           [fn("exp(x)", "blue", "eˣ"), fn("sum(0,N,k=>pow(x,k)/fact(k))", "red", "Tₙ(x)", dash=True)], None, "Naikkan N: polinom makin berimpit dengan eˣ.")],
            "explanation": "f(x) = Σ f⁽ⁿ⁾(0)xⁿ/n! (Maclaurin)."}


@register("dp.jari_jari", PW, (1, 2, 3))
def jari_jari(rng, tier):
    c = rng.randint(2, 6)
    if tier == 1:
        term, ans = rng.choice([(f"xⁿ/{c}ⁿ", f"R = {c}"), ("xⁿ/n!", "R = ∞"), ("n!·xⁿ", "R = 0")])
        steps = ["Uji rasio: |aₙ₊₁xⁿ⁺¹/(aₙxⁿ)| &lt; 1.", f"Hasil: <b>{ans}</b>."]
        prompt = f"Tentukan jari-jari kekonvergenan Σ {term}."
        wrong = [o for o in [f"R = {c}", "R = ∞", "R = 0", "R = 1", f"R = 1/{c}"] if o != ans]
    else:
        a = rng.randint(-3, 3)
        ans = f"[{n(a - c)}, {n(a + c)})"
        prompt = f"Tentukan interval kekonvergenan Σ<sub>n≥1</sub> (x − {paren(a)})ⁿ/(n·{c}ⁿ)."
        steps = [f"Uji rasio ⇒ |x − {paren(a)}| &lt; {c} ⇒ R = {c}.", f"Ujung x = {n(a + c)}: Σ 1/n (harmonik) divergen.",
                 f"Ujung x = {n(a - c)}: Σ (−1)ⁿ/n konvergen (bergantian).", f"Interval: <b>{ans}</b>."]
        wrong = [f"({n(a - c)}, {n(a + c)}]", f"[{n(a - c)}, {n(a + c)}]", f"({n(a - c)}, {n(a + c)})", f"[{n(-c)}, {n(c)})"]
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
    m = rng.randint(1, 3)
    k = m + rng.randint(1, 4)
    # f = x^m e^x = Σ x^{n+m}/n! ⇒ koef x^k = 1/(k − m)! ⇒ f^(k)(0) = k!/(k − m)!
    val = math.factorial(k) // math.factorial(k - m)
    return {"prompt": f"Untuk f(x) = x{sup(m) if m > 1 else ''}eˣ, hitung f<sup>({k})</sup>(0) memakai deret Maclaurin.", "correct": n(val),
            "distractors": [n(math.factorial(k)), n(Fr(1, math.factorial(k - m))), n(val * 2), n(k - m)],
            "steps": [f"x{sup(m)}eˣ = Σ xⁿ⁺{m}/n!; koefisien x{sup(k)} = 1/({k} − {m})!.", f"f<sup>({k})</sup>(0) = {k}!·(koefisien) = {k}!/{k - m}!.", f"= <b>{val}</b>."],
            "explanation": "Koefisien deret Taylor cₖ = f⁽ᵏ⁾(0)/k!."}


@register("dp.jumlah_deret", PW, (3, 4, 5))
def jumlah_deret(rng, tier):
    k = rng.randint(2, 5)
    if tier <= 4:
        val = Fr(k, (k - 1) ** 2)
        prompt = f"Hitung Σ<sub>n=1</sub><sup>∞</sup> n/{k}ⁿ."
        steps = ["Turunkan Σ xⁿ = 1/(1 − x): Σ n xⁿ⁻¹ = 1/(1 − x)², jadi Σ n xⁿ = x/(1 − x)².", f"x = 1/{k}: (1/{k})/(1 − 1/{k})² = <b>{n(val)}</b>."]
    else:
        val = None
        prompt = f"Hitung Σ<sub>n=0</sub><sup>∞</sup> {k}ⁿ/n!."
        steps = [f"Σ xⁿ/n! = eˣ dengan x = {k}.", f"= <b>e{sup(k)}</b>."]
    correct = n(val) if val is not None else f"e{sup(k)}"
    return {"prompt": prompt, "correct": correct, "distractors": [n(Fr(1, k - 1)), n(Fr(k, k - 1)), "divergen", f"e{sup(k - 1)}" if val is None else n(Fr(k * k, (k - 1) ** 2))],
            "steps": steps, "explanation": "Turunkan/integralkan deret pangkat suku demi suku di dalam jari-jari kekonvergenan."}
