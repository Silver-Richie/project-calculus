"""
Topik Level 4 kurikulum v2 yang semula hanya materi: fungsi vektor & kelengkungan (ketiga fakultas),
PD orde dua & deret Fourier (FT), metode numerik (Fasilkom), pembuktian ε–δ (FMIPA),
serta Lagrange (Fasilkom) dan Stokes–Gauss (FMIPA, Fasilkom) yang memakai ulang generator FT.
Rujukan: Stewart §13.1–13.3, §17.1–17.4, §11.11 (galat), §7.7 (numerik), §2.4 (ε–δ); Strang (MIT) Bab 8, 10.
"""

from fractions import Fraction as Fr
import math

from .. import attach, register
from ..fmt import MINUS, n, paren, sqrt_simplify, sup, surd, terms, times
from ..precalc.common import distinct, nz
from .inti import core

FV = core("fungsi-vektor")
PD2, FR, NUM, ED = "kl-ft-pd-orde2", "kl-ft-fourier", "kl-fk-numerik", "kl-fm-epsilon-delta"

attach("kl-fk-lagrange", "ftl.ekstrem", "ftl.lagrange", "ftl.kotak", "ftl.tiga_var")
for _t in ("kl-fm-stokes-gauss", "kl-fk-stokes-gauss"):
    attach(_t, "ftf.kerja", "ftf.fluks_bidang", "ftf.divergensi", "ftf.stokes", "ftf.gauss")
attach(NUM, "fka.newton")
attach(ED, "kont.epsilon_delta", "fa.eps_n")


def rt(v):
    return surd(*sqrt_simplify(v))


def cf(c):
    return "" if c == 1 else MINUS if c == -1 else n(c)


# ════════════════════════ Fungsi vektor & kelengkungan ═══════════════════
@register("fv.turunan", FV, (1, 2))
def fv_turunan(rng, tier):
    a, b, c = nz(rng, -4, 4), nz(rng, -3, 3), nz(rng, -5, 5)
    p, q = rng.randint(2, 3), rng.randint(1, 2)
    t0 = rng.randint(-2, 2)
    comps = [(a, p), (b, q), (c, 1)]
    r = "⟨" + ", ".join(f"{cf(k)}t{sup(e) if e > 1 else ''}" for k, e in comps) + "⟩"
    d = [k * e * t0 ** (e - 1) for k, e in comps]
    pos = [k * t0 ** e for k, e in comps]
    correct = "⟨" + ", ".join(n(v) for v in d) + "⟩"
    return {"prompt": f"r(t) = {r}. Hitung vektor kecepatan r′({n(t0)}).", "correct": correct,
            "distractors": ["⟨" + ", ".join(n(v) for v in pos) + "⟩", "⟨" + ", ".join(n(k * t0 ** (e - 1)) for k, e in comps) + "⟩",
                            "⟨" + ", ".join(n(-v) for v in d) + "⟩", "⟨" + ", ".join(n(v + 1) for v in d) + "⟩"],
            "steps": ["Turunkan setiap komponen terhadap t.", f"r′(t) = ⟨" + ", ".join(f"{n(k * e)}t{sup(e - 1) if e > 2 else ''}" if e > 1 else n(k) for k, e in comps) + "⟩.",
                      f"Di t = {n(t0)}: <b>{correct}</b>."],
            "explanation": "Kecepatan = turunan posisi; arahnya menyinggung lintasan."}


@register("fv.laju", FV, (1, 2, 3))
def fv_laju(rng, tier):
    a, b, h = rng.choice([(3, 4, 5), (4, 3, 5), (5, 12, 13), (12, 5, 13), (8, 15, 17), (6, 8, 10)])
    k = rng.randint(1, 3)
    if tier == 1:
        return {"prompt": f"Hitung laju (besar kecepatan) heliks r(t) = ⟨{a} cos t, {a} sin t, {b}t⟩.", "correct": n(h),
                "distractors": [n(a + b), n(h * h), n(a), n(b)],
                "steps": [f"r′(t) = ⟨−{a} sin t, {a} cos t, {b}⟩.", f"|r′| = √({a * a}(sin²t + cos²t) + {b * b}) = √{h * h} = <b>{h}</b> (konstan)."],
                "explanation": "Heliks berlaju tetap: komponen putar dan naik saling tegak lurus."}
    L = 2 * k * h
    return {"prompt": f"Hitung panjang busur heliks r(t) = ⟨{a} cos t, {a} sin t, {b}t⟩ untuk 0 ≤ t ≤ {2 * k}π.", "correct": times(L, "π"),
            "distractors": [times(2 * k * a, "π"), times(k * h, "π"), times(2 * k * (a + b), "π"), n(L)],
            "steps": ["L = ∫ |r′(t)| dt.", f"|r′(t)| = √({a * a} + {b * b}) = {h} (konstan).", f"L = {h}·{2 * k}π = <b>{times(L, 'π')}</b>."],
            "explanation": "Panjang busur kurva ruang: L = ∫ |r′(t)| dt."}


@register("fv.kelengkungan", FV, (3, 4, 5))
def fv_kelengkungan(rng, tier):
    kind = rng.choice(["heliks", "parabola", "lingkaran", "elips"] if tier >= 4 else ["heliks", "lingkaran", "parabola"])
    if kind == "heliks":
        a, b = rng.randint(1, 6), rng.randint(1, 6)
        val = Fr(a, a * a + b * b)
        prompt = f"Hitung kelengkungan heliks r(t) = ⟨{a} cos t, {a} sin t, {b}t⟩."
        steps = ["κ = |r′ × r″|/|r′|³.", f"|r′| = √{a * a + b * b}, |r′ × r″| = {a}√{a * a + b * b}.", f"κ = {a}/{a * a + b * b} = <b>{n(val)}</b>."]
        wrong = [n(Fr(1, a)), n(Fr(b, a * a + b * b)), n(Fr(a, b)), n(val * 2)]
    elif kind == "lingkaran":
        R = rng.randint(2, 12)
        val = Fr(1, R)
        prompt = f"Hitung kelengkungan lingkaran r(t) = ⟨{R} cos t, {R} sin t⟩."
        steps = ["Lingkaran berjari-jari R memiliki κ = 1/R di setiap titik.", f"<b>{n(val)}</b>."]
        wrong = [str(R), n(Fr(1, R * R)), n(Fr(2, R)), "0"]
    elif kind == "parabola":
        c, x0 = nz(rng, -5, 5), rng.choice([0, 0, 1, -1])
        num, base = 2 * abs(c), 1 + 4 * c * c * x0 * x0
        prompt = f"Hitung kelengkungan y = {cf(c)}x² di x = {x0}."
        if x0 == 0:
            correct = str(num)
            steps = ["κ = |y″|/(1 + y′²)<sup>3/2</sup>.", f"Di puncak y′ = 0, y″ = {2 * c} ⇒ κ = <b>{num}</b>."]
            wrong = [str(abs(c)), n(Fr(1, num)), str(2 * num), "0"]
        else:
            co, r = sqrt_simplify(base)
            correct = f"{num}/{base}<sup>3/2</sup>" if r != 1 else n(Fr(num, co ** 3))
            steps = ["κ = |y″|/(1 + y′²)<sup>3/2</sup>.", f"y′({x0}) = {2 * c * x0}, y″ = {2 * c} ⇒ κ = {num}/(1 + {4 * c * c})<sup>3/2</sup>.", f"<b>{correct}</b>."]
            wrong = [str(num), f"{num}/{base}", f"{abs(c)}/{base}<sup>3/2</sup>", f"{num}/{base}<sup>1/2</sup>"]
        return {"prompt": prompt, "correct": correct, "distractors": wrong, "steps": steps,
                "explanation": "Kelengkungan mengukur seberapa cepat arah singgung berubah per satuan panjang busur."}
    else:
        a, b = distinct(rng, 1, 6, 2)
        val = Fr(a, b * b)
        prompt = f"Hitung kelengkungan elips r(t) = ⟨{a} cos t, {b} sin t⟩ di titik ({a}, 0)."
        steps = ["Untuk kurva bidang: κ = |x′y″ − y′x″|/(x′² + y′²)<sup>3/2</sup>.", f"Di t = 0: x′ = 0, y′ = {b}, x″ = −{a}, y″ = 0 ⇒ κ = {a * b}/{b ** 3}.", f"= <b>{n(val)}</b>."]
        wrong = [n(Fr(b, a * a)), n(Fr(1, a)), n(Fr(a, b)), n(val * 2)]
    return {"prompt": prompt, "correct": n(val), "distractors": wrong, "steps": steps,
            "explanation": "Kelengkungan mengukur seberapa cepat arah singgung berubah per satuan panjang busur."}


@register("fv.tnb", FV, (4, 5))
def fv_tnb(rng, tier):
    a, b = rng.randint(1, 6), rng.randint(1, 6)
    if rng.random() < 0.5:
        val = Fr(b, a * a + b * b)
        return {"prompt": f"Hitung torsi τ heliks r(t) = ⟨{a} cos t, {a} sin t, {b}t⟩.", "correct": n(val),
                "distractors": [n(Fr(a, a * a + b * b)), n(Fr(1, b)), "0", n(Fr(b, a))],
                "steps": ["τ = (r′ × r″)·r‴/|r′ × r″|².", f"(r′ × r″)·r‴ = {a * a * b}, |r′ × r″|² = {a * a}({a * a + b * b}).", f"τ = <b>{n(val)}</b> (kurva bidang punya τ = 0)."],
                "explanation": "Torsi mengukur seberapa cepat kurva ‘keluar’ dari bidang oskulasinya."}
    p, q, h = rng.choice([(3, 4, 5), (4, 3, 5), (5, 12, 13), (12, 5, 13)])
    t0 = rng.randint(1, 3)
    # r(t) = ⟨p t, q t, c⟩ + vektor singgung satuan konstan
    return {"prompt": f"Tentukan vektor singgung satuan T(t) untuk r(t) = ⟨{p}t, {q}t, {a}⟩ di t = {t0}.", "correct": f"⟨{p}/{h}, {q}/{h}, 0⟩",
            "distractors": [f"⟨{p}, {q}, 0⟩", f"⟨{q}/{h}, {p}/{h}, 0⟩", f"⟨{p * t0}/{h}, {q * t0}/{h}, 0⟩", f"⟨{p}/{h}, {q}/{h}, {a}⟩"],
            "steps": [f"r′(t) = ⟨{p}, {q}, 0⟩, |r′| = {h}.", f"T = r′/|r′| = <b>⟨{p}/{h}, {q}/{h}, 0⟩</b> (garis lurus: T konstan, κ = 0)."],
            "explanation": "T = r′/|r′|; N = T′/|T′|; B = T × N."}


# ════════════════════════ PD orde dua (FT) ═══════════════════════════════
def _ekspo(r, var="x"):
    return "" if r == 0 else f"e<sup>{cf(r)}{var}</sup>"


@register("pd2.karakteristik", PD2, (1, 2, 3))
def pd2_kar(rng, tier):
    kind = rng.choice(["beda", "kembar", "kompleks"] if tier >= 2 else ["beda", "kembar"])
    if kind == "beda":
        r1, r2 = sorted(distinct(rng, -5, 5, 2))
        p, q = -(r1 + r2), r1 * r2
        correct = f"y = C₁{_ekspo(r1)} + C₂{_ekspo(r2)}".replace("C₁ +", "C₁ +").replace("C₁ + C₂", "C₁ + C₂")
        wrong = [f"y = C₁{_ekspo(-r1)} + C₂{_ekspo(-r2)}", f"y = (C₁ + C₂x){_ekspo(r1)}", f"y = C₁ cos({abs(r1) or 1}x) + C₂ sin({abs(r2) or 1}x)", f"y = C₁{_ekspo(r1 + r2)}"]
        why = f"r² + {n(p)}r + {n(q)} = 0 ⇒ r = {n(r1)}, {n(r2)} (dua akar real berbeda)."
    elif kind == "kembar":
        r = nz(rng, -4, 4)
        p, q = -2 * r, r * r
        correct = f"y = (C₁ + C₂x){_ekspo(r)}"
        wrong = [f"y = C₁{_ekspo(r)} + C₂{_ekspo(r)}", f"y = (C₁ + C₂x){_ekspo(-r)}", f"y = C₁{_ekspo(r)} + C₂{_ekspo(-r)}", f"y = C₁ cos({abs(r)}x) + C₂ sin({abs(r)}x)"]
        why = f"r² + {n(p)}r + {n(q)} = (r − {paren(r)})² ⇒ akar kembar r = {n(r)} ⇒ solusi kedua dikali x."
    else:
        al, be = rng.randint(-3, 3), rng.randint(1, 4)
        p, q = -2 * al, al * al + be * be
        bx = "x" if be == 1 else f"{be}x"
        correct = f"y = {_ekspo(al)}(C₁ cos {bx} + C₂ sin {bx})" if al else f"y = C₁ cos {bx} + C₂ sin {bx}"
        wrong = [f"y = C₁{_ekspo(al + be)} + C₂{_ekspo(al - be)}", f"y = {_ekspo(-al)}(C₁ cos {bx} + C₂ sin {bx})" if al else f"y = C₁ cosh {bx} + C₂ sinh {bx}",
                 f"y = {_ekspo(be)}(C₁ cos {al or 1}x + C₂ sin {al or 1}x)", f"y = (C₁ + C₂x){_ekspo(al)}" if al else f"y = C₁ + C₂x"]
        why = f"r = {n(al)} ± {be if be > 1 else ''}i (akar kompleks) ⇒ e<sup>αx</sup>(C₁ cos βx + C₂ sin βx)."
    pde = f"y″ {'+' if p >= 0 else MINUS} {abs(p)}y′ {'+' if q >= 0 else MINUS} {abs(q)}y = 0".replace(" + 0y′", "").replace(" − 0y′", "").replace(" 1y′", " y′").replace(" 1y ", " y ")
    return {"prompt": f"Tentukan solusi umum {pde}.", "correct": correct.replace("e<sup></sup>", ""), "distractors": wrong,
            "steps": ["Coba y = e<sup>rx</sup> ⇒ persamaan karakteristik r² + pr + q = 0.", why, f"<b>{correct}</b>."],
            "explanation": "Tiga kasus akar karakteristik: real berbeda, kembar, kompleks."}


@register("pd2.redaman", PD2, (1, 2, 3, 4, 5))
def pd2_redaman(rng, tier):
    m, w = rng.randint(1, 5), rng.randint(1, 6)
    k = m * w * w
    if tier == 1:
        return {"prompt": f"Pegas tanpa redaman: {m if m > 1 else ''}y″ + {k}y = 0 (massa {m} kg, konstanta {k} N/m). Frekuensi sudut alaminya ω₀ = …", "correct": f"{w} rad/s",
                "distractors": [f"{k} rad/s", f"{w * w} rad/s", f"{n(Fr(k, m * 2))} rad/s", f"{w + 1} rad/s"],
                "steps": ["my″ + ky = 0 ⇒ y = C₁ cos ω₀t + C₂ sin ω₀t dengan ω₀ = √(k/m).", f"√({k}/{m}) = <b>{w} rad/s</b>."],
                "explanation": "Osilator harmonik: frekuensi bergantung massa dan kekakuan, bukan simpangan awal."}
    cc = 2 * m * w                     # redaman kritis
    c = rng.choice([cc, cc, rng.randint(1, cc - 1) if cc > 1 else cc, cc + rng.randint(1, 6)])
    kind = "redaman kurang (berosilasi meluruh)" if c < cc else "redaman kritis" if c == cc else "redaman lebih (tanpa osilasi)"
    if tier <= 3:
        return {"prompt": f"Sistem {m if m > 1 else ''}y″ + {c}y′ + {k}y = 0 (FT: suspensi/rangkaian RLC) termasuk jenis …", "correct": kind,
                "distractors": [o for o in ["redaman kurang (berosilasi meluruh)", "redaman kritis", "redaman lebih (tanpa osilasi)", "tanpa redaman (osilasi abadi)"] if o != kind],
                "steps": [f"Diskriminan c² − 4mk = {c * c} − {4 * m * k} = {c * c - 4 * m * k}.", "&lt; 0 kurang, = 0 kritis, &gt; 0 lebih.", f"<b>{kind}</b> (redaman kritis c = 2√(mk) = {cc})."],
                "explanation": "Redaman kritis kembali ke kesetimbangan paling cepat tanpa berosilasi — target desain suspensi."}
    return {"prompt": f"Untuk m = {m} kg dan k = {k} N/m, berapa koefisien redaman kritis c agar sistem my″ + cy′ + ky = 0 tidak berosilasi namun kembali secepat mungkin?",
            "correct": f"c = {cc} N·s/m", "distractors": [f"c = {m * w} N·s/m", f"c = {4 * m * k} N·s/m", f"c = {w} N·s/m", f"c = {2 * cc} N·s/m"],
            "steps": ["Kritis ⇔ c² − 4mk = 0 ⇔ c = 2√(mk).", f"2√({m}·{k}) = 2·{m * w} = <b>{cc} N·s/m</b>."],
            "explanation": "c < 2√(mk): berosilasi; c > 2√(mk): lambat merayap."}


@register("pd2.nilai_awal", PD2, (3, 4, 5))
def pd2_nilai_awal(rng, tier):
    r1, r2 = sorted(distinct(rng, -4, 4, 2))
    A, B = rng.randint(-5, 5), rng.randint(-6, 6)
    # y = C₁e^{r1 x} + C₂e^{r2 x}: C₁ + C₂ = A, r1C₁ + r2C₂ = B
    C2 = Fr(B - r1 * A, r2 - r1)
    C1 = A - C2
    p, q = -(r1 + r2), r1 * r2
    pde = f"y″ {'+' if p >= 0 else MINUS} {abs(p)}y′ {'+' if q >= 0 else MINUS} {abs(q)}y = 0".replace(" + 0y′", "").replace(" − 0y′", "").replace(" 1y′", " y′").replace(" + 0y", "").replace(" − 0y", "").replace(" 1y ", " y ")
    correct = f"C₁ = {n(C1)}, C₂ = {n(C2)}"
    return {"prompt": f"Solusi {pde} berbentuk y = C₁{_ekspo(r1) or '·1'} + C₂{_ekspo(r2) or '·1'}. Dengan y(0) = {n(A)} dan y′(0) = {n(B)}, tentukan C₁ dan C₂.",
            "correct": correct, "distractors": [f"C₁ = {n(C2)}, C₂ = {n(C1)}", f"C₁ = {n(A)}, C₂ = {n(B)}", f"C₁ = {n(-C1)}, C₂ = {n(-C2)}" if (C1, C2) != (0, 0) else "C₁ = 1, C₂ = 1",
                                                f"C₁ = {n(C1 + 1)}, C₂ = {n(C2 - 1)}"],
            "steps": [f"y(0) = C₁ + C₂ = {n(A)}.", f"y′(0) = {n(r1)}C₁ + {n(r2)}C₂ = {n(B)}.", f"Selesaikan: <b>{correct}</b>."],
            "explanation": "Dua syarat awal menentukan dua konstanta solusi umum."}


@register("pd2.partikular", PD2, (4, 5))
def pd2_partikular(rng, tier):
    p, q = rng.randint(-4, 4), nz(rng, -6, 9)
    if rng.random() < 0.5:
        K = q * rng.randint(-4, 4) or q
        val = Fr(K, q)
        rhs, yp = n(K), n(val)
        why = f"Coba y<sub>p</sub> = A (konstan): q·A = {n(K)} ⇒ A = {n(val)}."
    else:
        a = rng.randint(-3, 3)
        D = a * a + p * a + q
        while D == 0:
            q += 1
            D = a * a + p * a + q
        rhs = f"e<sup>{cf(a)}x</sup>" if a else "1"
        yp = f"{times(Fr(1, D), 'e<sup>' + cf(a) + 'x</sup>') if a else n(Fr(1, D))}"
        why = f"Coba y<sub>p</sub> = Ae<sup>{a}x</sup>: A({a}² + {paren(p)}·{paren(a)} + {paren(q)}) = 1 ⇒ A = 1/{n(D)}."
    pde = f"y″ {'+' if p >= 0 else MINUS} {abs(p)}y′ {'+' if q >= 0 else MINUS} {abs(q)}y".replace(" + 0y′", "").replace(" − 0y′", "").replace(" 1y′", " y′").replace(" 1y", " y")
    return {"prompt": f"Tentukan satu solusi partikular dari {pde} = {rhs}.", "correct": f"y<sub>p</sub> = {yp}",
            "distractors": [f"y<sub>p</sub> = {rhs}", f"y<sub>p</sub> = {MINUS}{yp}" if not yp.startswith(MINUS) else f"y<sub>p</sub> = {yp[1:]}", "y<sub>p</sub> = 0", f"y<sub>p</sub> = x·{rhs}"],
            "steps": ["Koefisien tak tentu: tebak bentuk yang sama dengan ruas kanan.", why, f"<b>y<sub>p</sub> = {yp}</b>; solusi umum = y<sub>h</sub> + y<sub>p</sub>."],
            "explanation": "Koefisien tak tentu untuk ruas kanan konstan/eksponensial."}


# ════════════════════════ Deret Fourier (FT) ═════════════════════════════
@register("fr.periode", FR, (1, 2))
def fr_periode(rng, tier):
    a, b = distinct(rng, 1, 12, 2)
    g = math.gcd(a, b)
    correct = times(Fr(2, g), "π")
    f1 = "sin x" if a == 1 else f"sin {a}x"
    f2 = "cos x" if b == 1 else f"cos {b}x"
    return {"prompt": f"Periode dasar f(x) = {f1} + {f2} adalah …", "correct": correct,
            "distractors": [times(Fr(2, a * b), "π"), times(Fr(2, max(a, b)), "π"), times(Fr(2 * a * b, g), "π") if a * b != g else "4π", times(Fr(1, g), "π")],
            "steps": [f"Periode suku-suku: 2π/{a} dan 2π/{b}.", f"Periode gabungan = 2π/FPB({a}, {b}) = 2π/{g}.", f"<b>{correct}</b>."],
            "explanation": "Jumlah sinusoid periodik bila rasio frekuensinya rasional."}


@register("fr.genap", FR, (1, 2, 3))
def fr_genap(rng, tier):
    a, k = rng.randint(1, 5), rng.randint(2, 5)
    cases = [(f"f(x) = {a}x² pada (−π, π)", "hanya suku cosinus (bₙ = 0)"), (f"f(x) = {a}x pada (−π, π)", "hanya suku sinus (a₀ = aₙ = 0)"),
             (f"f(x) = |{a}x| pada (−π, π)", "hanya suku cosinus (bₙ = 0)"), (f"f(x) = x{sup(2 * k - 1)} pada (−π, π)", "hanya suku sinus (a₀ = aₙ = 0)"),
             (f"f(x) = {a} + sin {k}x", "konstanta dan satu suku sinus saja"), (f"f(x) = x cos {k}x pada (−π, π)", "hanya suku sinus (a₀ = aₙ = 0)"),
             (f"f(x) = x sin {k}x pada (−π, π)", "hanya suku cosinus (bₙ = 0)")]
    f, ans = rng.choice(cases)
    return {"prompt": f"Deret Fourier {f} memuat …", "correct": ans,
            "distractors": [o for o in ["hanya suku cosinus (bₙ = 0)", "hanya suku sinus (a₀ = aₙ = 0)", "konstanta dan satu suku sinus saja", "suku sinus dan cosinus lengkap"] if o != ans],
            "steps": ["Fungsi genap ⇒ bₙ = 0 (deret cosinus); fungsi ganjil ⇒ a₀ = aₙ = 0 (deret sinus).", f"<b>{ans}</b>."],
            "explanation": "Simetri memotong separuh perhitungan koefisien Fourier."}


@register("fr.koefisien", FR, (2, 3, 4, 5))
def fr_koef(rng, tier):
    c, k = rng.randint(1, 6), rng.randint(1, 8)
    kind = rng.choice(["linear", "kotak"] if tier <= 3 else ["kuadrat", "mutlak", "linear", "kotak"])
    if kind == "linear":
        val = Fr(2 * c * (-1) ** (k + 1), k)
        sym, prompt, why = "", f"Untuk f(x) = {c if c > 1 else ''}x pada (−π, π), hitung b<sub>{k}</sub>.", f"bₙ = (1/π)∫ {c if c > 1 else ''}x sin nx dx = 2·{c}(−1)ⁿ⁺¹/n."
    elif kind == "kotak":
        val = Fr(4 * c, k) if k % 2 else Fr(0)
        sym, prompt, why = "/π" if k % 2 else "", f"Gelombang kotak f(x) = {c} untuk 0 &lt; x &lt; π dan −{c} untuk −π &lt; x &lt; 0. Hitung b<sub>{k}</sub>.", f"bₙ = (2/π)∫₀^π {c} sin nx dx = 2·{c}(1 − (−1)ⁿ)/(nπ): nol untuk n genap."
    elif kind == "kuadrat":
        val = Fr(4 * c * (-1) ** k, k * k)
        sym, prompt, why = "", f"Untuk f(x) = {c if c > 1 else ''}x² pada (−π, π), hitung a<sub>{k}</sub>.", f"aₙ = (1/π)∫ {c if c > 1 else ''}x² cos nx dx = 4·{c}(−1)ⁿ/n²."
    else:
        val = Fr(-4 * c, k * k) if k % 2 else Fr(0)
        sym, prompt, why = "/π" if k % 2 else "", f"Untuk f(x) = {c if c > 1 else ''}|x| pada (−π, π), hitung a<sub>{k}</sub>.", f"aₙ = (2/π)∫₀^π {c if c > 1 else ''}x cos nx dx = 2·{c}((−1)ⁿ − 1)/(πn²): nol untuk n genap."
    show = (lambda v: "0" if v == 0 else (f"{n(v)}/π" if v.denominator == 1 else f"{n(v.numerator)}/({v.denominator}π)") if sym else n(v))
    correct = show(val)
    return {"prompt": prompt, "correct": correct, "distractors": [show(-val) if val else "1", show(val * 2) if val else show(Fr(4 * c, k)), show(val / 2) if val else "π", "0" if val else show(Fr(2 * c, k))],
            "steps": ["Koefisien Fourier pada (−π, π): aₙ = (1/π)∫ f cos nx dx, bₙ = (1/π)∫ f sin nx dx.", why, f"n = {k}: <b>{correct}</b>."],
            "explanation": "Rumus koefisien baku untuk x, x², |x|, dan gelombang kotak."}


@register("fr.parseval", FR, (4, 5))
def fr_parseval(rng, tier):
    c = rng.randint(1, 6)
    cases = [(f"Σ<sub>n≥1</sub> {c}/n²", Fr(c, 6), "π²", "deret Fourier x² dievaluasi di x = π (atau Parseval untuk f = x)"),
             (f"Σ<sub>n≥1</sub> {c}(−1)ⁿ⁺¹/n²", Fr(c, 12), "π²", "deret Fourier x² dievaluasi di x = 0"),
             (f"Σ<sub>n ganjil</sub> {c}/n²", Fr(c, 8), "π²", "deret Fourier |x| dievaluasi di x = 0"),
             (f"Σ<sub>n≥1</sub> {c}/n⁴", Fr(c, 90), "π⁴", "Parseval untuk f = x²"),
             (f"Σ<sub>n≥0</sub> {c}(−1)ⁿ/(2n + 1)", Fr(c, 4), "π", "deret Fourier gelombang kotak di x = π/2 (deret Leibniz)")]
    expr, v, sym, why = rng.choice(cases if tier == 5 else cases[:3] + cases[4:])
    correct = times(v, sym)
    return {"prompt": f"Gunakan deret Fourier untuk menghitung {expr}.", "correct": correct,
            "distractors": [times(v * 2, sym), times(v / 2, sym), times(v, "π" if sym != "π" else "π²"), "divergen"],
            "steps": [f"Sumber: {why}.", f"Nilai dasar dikali {c}: <b>{correct}</b>."],
            "explanation": "Deret Fourier memberi jumlah deret numerik klasik (masalah Basel: Σ1/n² = π²/6)."}


# ════════════════════════ Metode numerik (Fasilkom) ══════════════════════
def _poly_txt(co):
    return terms([(c, f"x{sup(len(co) - 1 - i)}" if len(co) - 1 - i > 1 else "x" if len(co) - 1 - i == 1 else "") for i, c in enumerate(co[:-1])], co[-1])


def _pev(co, x):
    return sum(Fr(c) * Fr(x) ** (len(co) - 1 - i) for i, c in enumerate(co))


@register("num.trapesium", NUM, (1, 2, 3))
def num_trapesium(rng, tier):
    co = [rng.randint(1, 3), rng.randint(-3, 3), rng.randint(-3, 5)]
    a = rng.randint(0, 2)
    N = rng.choice([2, 4]) if tier > 1 else 2
    h = Fr(rng.choice([1, 2]), 1) if tier > 1 else Fr(1)
    b = a + N * h
    ys = [_pev(co, a + i * h) for i in range(N + 1)]
    T = h / 2 * (ys[0] + 2 * sum(ys[1:-1]) + ys[-1])
    exact = sum(Fr(c, len(co) - i) * (Fr(b) ** (len(co) - i) - Fr(a) ** (len(co) - i)) for i, c in enumerate(co))
    return {"prompt": f"Taksir ∫<sub>{a}</sub><sup>{n(b)}</sup> ({_poly_txt(co)}) dx dengan aturan trapesium n = {N}.", "correct": n(T),
            "distractors": [n(exact), n(h * sum(ys[:-1])), n(T * 2), n(h * (ys[0] + ys[-1]) / 2)],
            "steps": [f"h = ({n(b)} − {a})/{N} = {n(h)}; nilai f di titik bagi: {', '.join(n(y) for y in ys)}.",
                      "T = (h/2)[f₀ + 2(f₁ + … + fₙ₋₁) + fₙ].", f"T = <b>{n(T)}</b> (nilai eksak {n(exact)}; trapesium melebihkan untuk f cekung ke atas)."],
            "explanation": "Aturan trapesium: galat O(h²)."}


@register("num.simpson", NUM, (2, 3, 4, 5))
def num_simpson(rng, tier):
    a, N = rng.randint(0, 2), rng.choice([2, 4])
    h = Fr(1)
    b = a + N
    if tier <= 3 or rng.random() < 0.5:
        co = [rng.randint(-2, 2) or 1, rng.randint(-3, 3), rng.randint(-3, 3), rng.randint(-3, 5)]
        f = lambda x: _pev(co, x)
        ftxt = _poly_txt(co)
        note = "Simpson eksak untuk polinom derajat ≤ 3."
    else:
        co = None
        k = rng.randint(1, 3)
        f = lambda x: Fr(1, x + k)
        ftxt = f"1/(x + {k})"
        note = f"Bandingkan nilai eksak ln({b + k}/{a + k})."
    ys = [f(a + i) for i in range(N + 1)]
    S = h / 3 * (ys[0] + 4 * sum(ys[1:-1:2]) + 2 * sum(ys[2:-1:2]) + ys[-1])
    return {"prompt": f"Taksir ∫<sub>{a}</sub><sup>{b}</sup> {ftxt} dx dengan aturan Simpson n = {N}.", "correct": n(S),
            "distractors": [n(h / 2 * (ys[0] + 2 * sum(ys[1:-1]) + ys[-1])), n(S * 3), n(h / 3 * (ys[0] + 2 * sum(ys[1:-1]) + ys[-1])), n(S + 1)],
            "steps": [f"h = 1; f di titik bagi: {', '.join(n(y) for y in ys)}.", "S = (h/3)[f₀ + 4f₁ + 2f₂ + 4f₃ + … + fₙ].", f"S = <b>{n(S)}</b>. {note}"],
            "explanation": "Aturan Simpson memakai parabola: galat O(h⁴)."}


@register("num.bisection", NUM, (1, 2, 3))
def num_bisection(rng, tier):
    c = rng.choice([v for v in range(2, 40) if math.isqrt(v) ** 2 != v])
    lo = math.isqrt(c)
    a, b = Fr(lo), Fr(lo + 1)
    steps_n = tier
    log = []
    for _ in range(steps_n):
        m = (a + b) / 2
        if m * m - c < 0:
            a = m
        else:
            b = m
        log.append(f"m = {n(m)}: f(m) {'&lt;' if m * m - c < 0 else '&gt;'} 0")
    correct = f"[{n(a)}, {n(b)}]"
    return {"prompt": f"Metode bagi dua untuk f(x) = x² − {c} dimulai pada [{lo}, {lo + 1}]. Interval setelah {steps_n} langkah?", "correct": correct,
            "distractors": [f"[{n(a - (b - a))}, {n(a)}]", f"[{n(b)}, {n(b + (b - a))}]", f"[{n(a)}, {n(b + (b - a))}]", f"[{lo}, {n(Fr(2 * lo + 1, 2))}]" if correct != f"[{lo}, {n(Fr(2 * lo + 1, 2))}]" else f"[{n(Fr(2 * lo + 1, 2))}, {lo + 1}]"],
            "steps": ["Setiap langkah: hitung titik tengah m, simpan setengah interval yang tanda f-nya berubah.", "; ".join(log) + ".", f"<b>{correct}</b> (lebar 1/2ⁿ)."],
            "explanation": "Bisection selalu konvergen tetapi lambat (linear)."}


@register("num.newton", NUM, (1, 2, 3, 4, 5))
def num_newton(rng, tier):
    p, q = rng.randint(-5, 5), rng.randint(-9, 9)
    x0 = rng.randint(-3, 4)
    fx, dfx = x0 * x0 + p * x0 + q, 2 * x0 + p
    while dfx == 0:
        x0 += 1
        fx, dfx = x0 * x0 + p * x0 + q, 2 * x0 + p
    x1 = Fr(x0) - Fr(fx, dfx)
    f = terms([(1, "x²"), (p, "x")], q)
    if tier >= 3:
        x2 = x1 - (x1 * x1 + p * x1 + q) / (2 * x1 + p) if 2 * x1 + p else None
        if x2 is not None and tier >= 4:
            return {"prompt": f"Metode Newton untuk f(x) = {f} dengan x₀ = {x0}. Hitung x₂.", "correct": n(x2),
                    "distractors": [n(x1), n(x2 + 1), n(-x2), n(Fr(x0) + Fr(fx, dfx))],
                    "steps": ["xₙ₊₁ = xₙ − f(xₙ)/f′(xₙ).", f"x₁ = {x0} − {n(fx)}/{n(dfx)} = {n(x1)}.", f"x₂ = x₁ − f(x₁)/f′(x₁) = <b>{n(x2)}</b>."],
                    "explanation": "Newton–Raphson: garis singgung memotong sumbu-x di taksiran berikutnya."}
    return {"prompt": f"Metode Newton untuk f(x) = {f} dengan x₀ = {x0}. Hitung x₁.", "correct": n(x1),
            "distractors": [n(Fr(x0) + Fr(fx, dfx)), n(Fr(fx, dfx)), n(x0 - fx), n(x1 + 1)],
            "steps": ["xₙ₊₁ = xₙ − f(xₙ)/f′(xₙ).", f"f({x0}) = {n(fx)}, f′({x0}) = {n(dfx)}.", f"x₁ = {x0} − ({n(fx)})/({n(dfx)}) = <b>{n(x1)}</b>."],
            "explanation": "Newton–Raphson: garis singgung memotong sumbu-x di taksiran berikutnya."}


@register("num.galat", NUM, (4, 5))
def num_galat(rng, tier):
    L, M = rng.randint(1, 4), rng.randint(1, 12)
    if rng.random() < 0.5:
        k = rng.randint(1, 6)
        # trapesium: |E| ≤ L³M/(12n²) ≤ ε ⇒ n ≥ √(L³M/(12ε)); pilih ε agar n bulat
        nmin = k * rng.randint(2, 6)
        eps = Fr(L ** 3 * M, 12 * nmin * nmin)
        return {"prompt": f"|f″(x)| ≤ {M} pada interval sepanjang {L}. Berapa n minimum agar galat aturan trapesium ≤ {n(eps)} (pakai batas |E| ≤ (b − a)³M/(12n²))?",
                "correct": str(nmin), "distractors": [str(nmin * nmin), str(nmin + 1), str(nmin // 2) if nmin > 2 else str(nmin + 2), str(2 * nmin)],
                "steps": [f"{L}³·{M}/(12n²) ≤ {n(eps)} ⇔ n² ≥ {L ** 3 * M}/(12·{n(eps)}) = {nmin * nmin}.", f"n ≥ <b>{nmin}</b>."],
                "explanation": "Galat trapesium turun seperti 1/n²: menggandakan n memperkecil galat 4 kali."}
    m = rng.randint(2, 5)
    return {"prompt": f"Galat aturan Simpson sebanding dengan h⁴. Jika h dibagi {m}, galat menjadi kira-kira … kali semula.", "correct": f"1/{m ** 4}",
            "distractors": [f"1/{m * m}", f"1/{m}", f"1/{m ** 3}", f"{m ** 4}"],
            "steps": [f"(h/{m})⁴ = h⁴/{m ** 4}.", f"<b>1/{m ** 4}</b> — bandingkan trapesium (h²): 1/{m * m}."], "explanation": "Orde galat menentukan seberapa cepat metode membaik."}


# ════════════════════════ Pembuktian ε–δ (FMIPA) ═════════════════════════
@register("ed.bukti", ED, (1, 2, 3, 4, 5))
def ed_bukti(rng, tier):
    eps = rng.choice([Fr(1, 10), Fr(1, 20), Fr(1, 50), Fr(1, 100), Fr(3, 100), Fr(1, 1000)])
    if tier <= 2:
        m, b, c = nz(rng, -9, 9), rng.randint(-6, 6), rng.randint(-4, 4)
        L = m * c + b
        delta = eps / abs(m)
        return {"prompt": f"Untuk membuktikan lim<sub>x→{n(c)}</sub> ({terms([(m, 'x')], b)}) = {n(L)}, δ terbesar yang bekerja untuk ε = {n(eps)} adalah …", "correct": f"δ = {n(delta)}",
                "distractors": [f"δ = {n(eps * abs(m))}", f"δ = {n(eps)}", f"δ = {n(delta / 2)}", f"δ = {n(eps / (abs(m) + 1))}"],
                "steps": [f"|f(x) − {n(L)}| = {abs(m)}|x − {paren(c)}|.", f"&lt; ε ⇔ |x − {paren(c)}| &lt; ε/{abs(m)}.", f"<b>δ = {n(delta)}</b>."],
                "explanation": "Fungsi linear: δ = ε/|m| bekerja di setiap titik."}
    c = rng.randint(1, 9)
    if tier == 3:
        K = 2 * c + 1
        delta = min(Fr(1), eps / K)
        return {"prompt": f"Bukti lim<sub>x→{c}</sub> x² = {c * c}: dengan membatasi δ ≤ 1, konstanta K pada |x² − {c * c}| ≤ K|x − {c}| dan δ untuk ε = {n(eps)} adalah …",
                "correct": f"K = {K}, δ = {n(delta)}", "distractors": [f"K = {2 * c}, δ = {n(eps / (2 * c))}", f"K = {K}, δ = {n(eps)}", f"K = {c * c}, δ = {n(eps / (c * c))}", f"K = {K + 1}, δ = {n(eps / (K + 1))}"],
                "steps": [f"|x² − {c * c}| = |x − {c}||x + {c}|; δ ≤ 1 ⇒ x ∈ ({c - 1}, {c + 1}) ⇒ |x + {c}| &lt; {K}.", f"Ambil δ = min(1, ε/{K}) = <b>{n(delta)}</b>."],
                "explanation": "Fungsi nonlinear: batasi δ dulu agar faktor pengganggu terbatas."}
    if tier == 4:
        delta = min(Fr(c, 2), eps * c * c / 2)
        return {"prompt": f"Bukti lim<sub>x→{c}</sub> 1/x = 1/{c} memakai δ = min({n(Fr(c, 2))}, {c * c}ε/2). Berapa δ untuk ε = {n(eps)}?", "correct": f"δ = {n(delta)}",
                "distractors": [f"δ = {n(eps * c * c)}", f"δ = {n(eps)}", f"δ = {n(Fr(c, 2))}" if delta != Fr(c, 2) else f"δ = {n(eps * c)}", f"δ = {n(eps * c / 2)}"],
                "steps": [f"|1/x − 1/{c}| = |x − {c}|/(|x|·{c}).", f"δ ≤ {n(Fr(c, 2))} ⇒ |x| &gt; {n(Fr(c, 2))} ⇒ |1/x − 1/{c}| &lt; 2|x − {c}|/{c * c}.",
                          f"Cukup |x − {c}| &lt; {c * c}ε/2 ⇒ <b>δ = {n(delta)}</b>."],
                "explanation": "Jauhkan x dari 0 (titik singular) dengan membatasi δ ≤ c/2."}
    s = rng.randint(1, 9)
    delta = eps * s
    return {"prompt": f"Bukti lim<sub>x→{s * s}</sub> √x = {s}: dari |√x − {s}| = |x − {s * s}|/(√x + {s}) ≤ |x − {s * s}|/{s}, δ untuk ε = {n(eps)} adalah …", "correct": f"δ = {n(delta)}",
            "distractors": [f"δ = {n(eps / s)}", f"δ = {n(eps)}", f"δ = {n(eps * s * s)}", f"δ = {n(eps * 2 * s)}"],
            "steps": [f"Kalikan sekawan: |√x − {s}| = |x − {s * s}|/(√x + {s}) ≤ |x − {s * s}|/{s}.", f"&lt; ε bila |x − {s * s}| &lt; {s}ε.", f"<b>δ = {n(delta)}</b>."],
            "explanation": "Teknik sekawan untuk bukti ε–δ fungsi akar."}


@register("ed.barisan", ED, (1, 2, 3))
def ed_barisan(rng, tier):
    a, c = rng.randint(1, 6), rng.randint(1, 4)
    b, d = rng.randint(-5, 9), rng.randint(0, 5)
    while b * c - a * d == 0:
        b += 1
    E = rng.choice([10, 20, 50, 100, 1000])
    eps = Fr(1, E)
    L = Fr(a, c)
    N = 1
    while abs(Fr(a * N + b, c * N + d) - L) >= eps:
        N += 1
    num = abs(b * c - a * d)
    return {"prompt": f"aₙ = ({terms([(a, 'n')], b)})/({terms([(c, 'n')], d)}) → {n(L)}. N terkecil agar |aₙ − {n(L)}| &lt; 1/{E} untuk n ≥ N?", "correct": str(N),
            "distractors": [str(N + 1), str(max(1, N - 1)), str(E), str(num * E)],
            "steps": [f"|aₙ − {n(L)}| = {num}/({c}({terms([(c, 'n')], d)})).", f"&lt; 1/{E} ⇔ {terms([(c, 'n')], d)} &gt; {num * E}/{c} ⇒ n terkecil = {N}.", f"<b>N = {N}</b> (barisan turun menuju limit, jadi berlaku untuk semua n ≥ N)."],
            "explanation": "Definisi limit barisan: ∀ε ∃N ∀n ≥ N: |aₙ − L| < ε."}
