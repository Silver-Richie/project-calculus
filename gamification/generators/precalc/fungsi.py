"""
Topik: Konsep Fungsi — relasi, nilai, domain, komposisi, invers, transformasi, genap/ganjil.
Rujukan: Stewart §1.1, §1.3, §1.5; Whitman §1.3–1.4; Strang (MIT) §4.3.
"""

from fractions import Fraction as Fr

from .. import register
from ..fmt import MINUS, interval, lin, n, paren, poly
from ..graphs import fn, g2d, param, pt, readout
from .common import distinct, nz

T = "pre-konsep-fungsi"


@register("fn.relasi", T, (1,))
def relasi(rng, tier):
    xs = distinct(rng, -5, 9, 3)
    ys = [rng.randint(-5, 9) for _ in xs]
    good = "{" + ", ".join(f"({n(x)}, {n(y)})" for x, y in zip(xs, ys)) + "}"
    bads = []
    for _ in range(4):
        rep = rng.choice(xs)
        y2 = rng.choice([v for v in range(-5, 10) if v not in ys])
        pairs = list(zip(xs, ys)) + [(rep, y2)]
        rng.shuffle(pairs)
        bads.append("{" + ", ".join(f"({n(x)}, {n(y)})" for x, y in pairs) + "}")
    return {
        "prompt": "Relasi manakah yang merupakan <b>fungsi</b> (dari x ke y)?",
        "correct": good, "distractors": bads,
        "steps": ["Fungsi memasangkan setiap x dengan <b>tepat satu</b> y.",
                  "Relasi yang memuat dua pasangan dengan x sama tetapi y berbeda (mis. (2, 1) dan (2, 5)) bukan fungsi — "
                  "secara grafik, garis tegak di x itu memotong lebih dari satu titik (uji garis vertikal).",
                  f"Hanya <b>{good}</b> yang setiap x-nya muncul sekali."],
        "explanation": "Uji garis vertikal: grafik adalah fungsi bila setiap garis tegak memotongnya paling banyak sekali.",
    }


@register("fn.nilai", T, (1,))
def nilai(rng, tier):
    a, b, c = nz(rng, -3, 4), rng.randint(-6, 6), rng.randint(-9, 9)
    k = rng.randint(-4, 4)
    val = a * k * k + b * k + c
    f = poly([a, b, c])
    return {
        "prompt": f"Diketahui f(x) = {f}. Hitung f({n(k)}).",
        "correct": n(val), "distractors": [n(-a * k * k + b * k + c), n(a * k * 2 + b * k + c), n(val + b), n(a * k * k - b * k + c)],
        "steps": [f"Substitusi x = {n(k)}: f({n(k)}) = {n(a)}·{paren(k)}² + ({n(b)})·{paren(k)} + ({n(c)}).",
                  f"= {n(a * k * k)} + ({n(b * k)}) + ({n(c)}) = <b>{n(val)}</b>.",
                  "Ingat (−k)² = k² (kuadrat bilangan negatif positif)."],
        "graphs": [g2d("Nilai fungsi sebagai titik pada grafik", [-6, 6], [-30, 30],
                       [param("k", "Masukan x = k", -5, 5, 0.1, k, "k")],
                       [fn(f"{a}*x**2+({b})*x+({c})", "blue", "f(x)"), pt("k", f"{a}*k**2+({b})*k+({c})", label="(k, f(k))")],
                       [readout("f(k)", f"{a}*k**2+({b})*k+({c})", 3)], "Geser k untuk membaca nilai f di titik lain.")],
    }


@register("fn.domain", T, (1, 2, 3))
def domain(rng, tier):
    a = rng.randint(-6, 6)
    if tier == 1:
        expr, correct = f"√({lin(1, -a)})", interval(a, None)
        wrong = [interval(a, None, lo_closed=False), interval(None, a), interval(-a, None), "ℝ"]
        steps = [f"Bilangan di bawah akar kuadrat harus ≥ 0: x − ({n(a)}) ≥ 0.", f"x ≥ {n(a)} ⇒ D = <b>{correct}</b>."]
        gexpr = f"sqrt(x-({a}))"
    elif tier == 2:
        k = rng.randint(1, 6)
        expr = f"1 / (x² − {k * k})"
        correct = f"ℝ ∖ {{{MINUS}{k}, {k}}}"
        wrong = [f"ℝ ∖ {{{k}}}", f"ℝ ∖ {{{k * k}}}", interval(-k, k, False, False), "ℝ"]
        steps = ["Penyebut tidak boleh 0.", f"x² − {k * k} = 0 ⇔ x = ±{k}.", f"D = <b>{correct}</b>."]
        gexpr = f"1/(x*x-{k * k})"
    else:
        b = rng.choice([v for v in range(-6, 7) if v != a])
        lo, hi = sorted([a, b])
        expr = f"√(({lin(1, -a)}) / ({lin(1, -b)}))"
        lc, hc = (lo == a), (hi == a)
        correct = f"{interval(None, lo, hi_closed=lc)} ∪ {interval(hi, None, lo_closed=hc)}"
        wrong = [interval(lo, hi, lc, hc), f"{interval(None, lo)} ∪ {interval(hi, None)}",
                 f"{interval(None, lo, hi_closed=False)} ∪ {interval(hi, None, lo_closed=False)}", f"ℝ ∖ {{{n(b)}}}"]
        steps = [f"Syarat: (x − {n(a)})/(x − {n(b)}) ≥ 0 dan x ≠ {n(b)}.",
                 "Pecahan ≥ 0 di luar kedua titik kritis (tanda + − +).",
                 f"x = {n(a)} boleh (pembilang 0), x = {n(b)} tidak boleh (penyebut 0): D = <b>{correct}</b>."]
        gexpr = f"sqrt((x-({a}))/(x-({b})))"
    return {"prompt": f"Tentukan domain alami fungsi f(x) = {expr}.", "correct": correct, "distractors": wrong, "steps": steps,
            "graphs": [g2d("Grafik hanya ada di dalam domain", [-10, 10], [-6, 8],
                           [param("s", "Titik uji x", -9.5, 9.5, 0.05, a + 1.5, "x")],
                           [fn(gexpr, "blue", "f(x)"), pt("s", gexpr.replace("x", "s"), label="f(x uji)")],
                           [readout("f(x uji)", gexpr.replace("x", "s"), 4)],
                           "Geser titik uji ke luar domain: titik merah hilang (nilai tidak terdefinisi, ditandai —).")],
            "explanation": "Domain alami: buang x yang membuat penyebut 0 atau bilangan di bawah akar genap negatif."}


@register("fn.komposisi", T, (2, 3))
def komposisi(rng, tier):
    a, b = nz(rng, -4, 4, (0, 1)), nz(rng, -5, 5)
    c = nz(rng, -5, 5)
    f, g = lin(a, b), poly([1, 0, c])
    if tier == 2:
        k = rng.randint(-3, 3)
        gk = k * k + c
        val = a * gk + b
        prompt = f"Diketahui f(x) = {f} dan g(x) = {g}. Hitung (f ∘ g)({n(k)})."
        correct = n(val)
        fk = a * k + b
        wrong = [n(fk * fk + c), n(a * k * k + b), n(val + a), n(a * (k * k) + c)]
        steps = [f"(f ∘ g)({n(k)}) = f(g({n(k)})). Hitung dulu yang di dalam: g({n(k)}) = {n(k * k)} + ({n(c)}) = {n(gk)}.",
                 f"f({n(gk)}) = {n(a)}·{paren(gk)} + ({n(b)}) = <b>{n(val)}</b>.",
                 f"Bandingkan: (g ∘ f)({n(k)}) = g({n(fk)}) = {n(fk * fk + c)} — komposisi tidak komutatif."]
    else:
        prompt = f"Diketahui f(x) = {f} dan g(x) = {g}. Tentukan (g ∘ f)(x)."
        correct = poly([a * a, 2 * a * b, b * b + c])
        wrong = [poly([a, 0, a * c + b]), poly([a * a, 0, b * b + c]), poly([a * a, 2 * a * b, b * b - c]), poly([a, 2 * a * b, b * b + c]),
                 poly([a * a, a * b, b * b + c]), poly([a * a, 2 * a * b, b + c])]
        steps = [f"(g ∘ f)(x) = g(f(x)) = (f(x))² + ({n(c)}).",
                 f"({f})² = {poly([a * a, 2 * a * b, b * b])}.", f"Tambah {n(c)}: <b>{correct}</b>."]
    return {"prompt": prompt, "correct": correct, "distractors": wrong, "steps": steps,
            "graphs": [g2d("f ∘ g dibanding g ∘ f", [-5, 5], [-20, 30],
                           [param("aa", "Koefisien a pada f", -4, 4, 0.5, a, "a")],
                           [fn(f"aa*(x*x+({c}))+({b})", "blue", "(f∘g)(x)"), fn(f"(aa*x+({b}))**2+({c})", "orange", "(g∘f)(x)")],
                           None, "Dua kurva berbeda: urutan komposisi penting. Ubah a dan lihat kapan keduanya mirip.")],
            "explanation": "(f ∘ g)(x) = f(g(x)): kerjakan fungsi paling dalam terlebih dahulu."}


@register("fn.invers", T, (2, 3, 4))
def invers(rng, tier):
    if tier == 2:
        a, b = nz(rng, -5, 5, (0, 1, -1)), nz(rng, -8, 8)
        prompt = f"Tentukan invers dari f(x) = {lin(a, b)}."
        correct = f"f⁻¹(x) = ({lin(1, -b)})/{paren(a)}" if a != -1 else f"f⁻¹(x) = {lin(-1, b)}"
        wrong = [f"f⁻¹(x) = ({lin(1, b)})/{paren(a)}", f"f⁻¹(x) = {lin(Fr(1, a), b)}", f"f⁻¹(x) = 1/({lin(a, b)})",
                 f"f⁻¹(x) = {lin(a, -b)}"]
        steps = [f"Tulis y = {lin(a, b)}, lalu selesaikan untuk x: x = (y − ({n(b)}))/{paren(a)}.",
                 f"Tukar nama variabel: <b>{correct}</b>.",
                 "Cek: f(f⁻¹(x)) = x. Grafik f⁻¹ adalah cerminan grafik f terhadap garis y = x."]
        fexpr, iexpr = f"{a}*x+({b})", f"(x-({b}))/{a}"
    elif tier == 3:
        a, b, c, d = nz(rng, -4, 4), rng.randint(-5, 5), nz(rng, -3, 3), rng.randint(-5, 5)
        while a * d - b * c == 0:
            d += 1
        prompt = f"Tentukan invers dari f(x) = ({lin(a, b)})/({lin(c, d)})."
        correct = f"f⁻¹(x) = ({lin(-d, b)})/({lin(c, -a)})"
        wrong = [f"f⁻¹(x) = ({lin(d, -b)})/({lin(c, -a)})", f"f⁻¹(x) = ({lin(c, d)})/({lin(a, b)})",
                 f"f⁻¹(x) = ({lin(-d, b)})/({lin(-c, a)})", f"f⁻¹(x) = ({lin(a, -b)})/({lin(-c, d)})"]
        steps = [f"y = ({lin(a, b)})/({lin(c, d)}) ⇒ y({lin(c, d)}) = {lin(a, b)}.",
                 f"Kumpulkan suku x: x({n(c)}y − {paren(a)}) = {n(b)} − {paren(d)}y.",
                 f"x = ({lin(-d, b, 'y')})/({lin(c, -a, 'y')}); tukar y ↔ x: <b>{correct}</b>.",
                 "Pola umum: invers (ax + b)/(cx + d) adalah (−dx + b)/(cx − a)."]
        fexpr, iexpr = f"({a}*x+({b}))/({c}*x+({d}))", f"(-({d})*x+({b}))/({c}*x-({a}))"
    else:
        p = rng.randint(-9, 9)
        t = rng.randint(-3, 3)
        k = 2 * t ** 3 + p
        prompt = f"Diketahui f(x) = 2x³ {'+' if p >= 0 else MINUS} {abs(p)}. Hitung f⁻¹({n(k)})."
        correct = n(t)
        wrong = [n(2 * k ** 3 + p) if abs(k) < 5 else n(-t if t else 1), n(t + 1), n(Fr(k - p, 2)), n(-t - 1)]
        steps = [f"f⁻¹({n(k)}) = x yang memenuhi f(x) = {n(k)}.",
                 f"2x³ + ({n(p)}) = {n(k)} ⇒ x³ = {n(Fr(k - p, 2))}.", f"x = ∛{n(Fr(k - p, 2))} = <b>{n(t)}</b>."]
        fexpr, iexpr = f"2*x**3+({p})", f"cbrt((x-({p}))/2)"
    graph = g2d("f, f⁻¹, dan cermin y = x", [-8, 8], [-8, 8],
                [param("s", "Titik pada f: x = s", -6, 6, 0.05, 1, "s")],
                [fn(fexpr, "blue", "f"), fn(iexpr, "orange", "f⁻¹"), fn("x", "gray", "y = x", dash=True),
                 pt("s", fexpr.replace("x", "s"), "blue"), pt(fexpr.replace("x", "s"), "s", "orange")],
                [readout("Titik di f: (s, f(s)) → f(s)", fexpr.replace("x", "s"), 3)],
                "Geser s: titik (s, f(s)) di f selalu bercermin ke (f(s), s) di f⁻¹ terhadap garis y = x.")
    return {"prompt": prompt, "correct": correct, "distractors": wrong, "steps": steps, "graphs": [graph],
            "explanation": "f⁻¹(y) = x ⇔ f(x) = y. Fungsi punya invers bila satu-satu (lolos uji garis horizontal)."}


@register("fn.transformasi", T, (2, 3))
def transformasi(rng, tier):
    h, k = nz(rng, -5, 5), nz(rng, -5, 5)
    base = rng.choice([("√x", "sqrt(x)", "titik awal"), ("x²", "x*x", "titik puncak"), ("|x|", "abs(x)", "titik sudut")])
    name, js, what = base
    if tier == 2:
        right = "kanan" if h > 0 else "kiri"
        up = "atas" if k > 0 else "bawah"
        prompt = f"Grafik y = {name} digeser {abs(h)} satuan ke {right} lalu {abs(k)} satuan ke {up}. Persamaan grafik barunya adalah …"

        def shifted(hh, kk):
            inner = f"x {MINUS} {hh}" if hh > 0 else f"x + {-hh}"
            body = {"√x": f"√({inner})", "x²": f"({inner})²", "|x|": f"|{inner}|"}[name]
            return f"y = {body} {'+' if kk > 0 else MINUS} {abs(kk)}"
        correct = shifted(h, k)
        wrong = [shifted(-h, k), shifted(k, h) if k != h else shifted(-h, -k), shifted(h, -k), shifted(-h, -k)]
        steps = ["Geser ke kanan h satuan: ganti x dengan (x − h). Geser ke kiri: ganti x dengan (x + h).",
                 "Geser ke atas k satuan: tambahkan k di luar fungsi.", f"Hasil: <b>{correct}</b>."]
        a = 1
    else:
        a = rng.choice([-2, -1, 2, 3, Fr(1, 2)])
        prompt = (f"Tentukan {what} grafik y = {n(a)}·f(x {MINUS if h > 0 else '+'} {abs(h)}) {'+' if k > 0 else MINUS} {abs(k)} "
                  f"dengan f(x) = {name}.")
        correct = f"({n(h)}, {n(k)})"
        wrong = [f"({n(-h)}, {n(k)})", f"({n(h)}, {n(-k)})", f"({n(k)}, {n(h)})", f"({n(a * h)}, {n(k)})",
                 f"({n(h + 1)}, {n(k)})", f"({n(h)}, {n(k + 1)})", f"({n(-h)}, {n(-k)})"]
        steps = [f"{what.capitalize()} f(x) = {name} ada di (0, 0).",
                 f"x − ({n(h)}) menggeser {abs(h)} satuan ke {'kanan' if h > 0 else 'kiri'}; + ({n(k)}) menggeser ke {'atas' if k > 0 else 'bawah'}.",
                 f"Faktor {n(a)} hanya meregang{' dan mencerminkan (karena negatif)' if a < 0 else ''} secara vertikal, tidak memindahkan titik ini.",
                 f"Jadi {what} = <b>{correct}</b>."]
    graph = g2d(f"y = a·f(x − h) + k dengan f(x) = {name}", [-10, 10], [-10, 10],
                [param("a", "Regangan a", -3, 3, 0.25, float(a), "a"), param("h", "Geser horizontal h", -6, 6, 0.5, h, "h"),
                 param("k", "Geser vertikal k", -6, 6, 0.5, k, "k")],
                [fn(js, "gray", "f(x) asli", dash=True), fn(f"a*({js.replace('x', '(x-h)')})+k", "blue", "hasil transformasi"),
                 pt("h", "k", label=what)],
                [readout(f"{what} (h, k)", "h", 2), readout("k", "k", 2)],
                "Geser h, k, a satu per satu untuk melihat efek masing-masing transformasi (Whitman §1.4).")
    return {"prompt": prompt, "correct": correct, "distractors": wrong, "steps": steps, "graphs": [graph],
            "explanation": "y = a·f(x − h) + k: h geser horizontal (berlawanan tanda), k geser vertikal, a regangan/cermin."}


@register("fn.genap_ganjil", T, (2, 3))
def genap_ganjil(rng, tier):
    even = [("x⁴ − 3x²", "x**4-3*x*x"), ("|x| + 2", "abs(x)+2"), ("cos x", "cos(x)"), ("x² + 1", "x*x+1"), ("x·sin x", "x*sin(x)")]
    odd = [("x³ − x", "x**3-x"), ("sin x", "sin(x)"), ("x·|x|", "x*abs(x)"), ("x⁵ + 2x", "x**5+2*x"), ("tan x", "tan(x)")]
    neither = [("x² + x", "x*x+x"), ("eˣ", "exp(x)"), ("(x − 1)²", "(x-1)**2"), ("x³ + 1", "x**3+1"), ("√x", "sqrt(x)")]
    want = rng.choice(["genap", "ganjil"])
    good = rng.choice(even if want == "genap" else odd)
    others = rng.sample((odd if want == "genap" else even), 1 if tier == 3 else 0) + rng.sample(neither, 4 if tier == 2 else 3)
    rule = "f(−x) = f(x)" if want == "genap" else "f(−x) = −f(x)"
    sym = "simetris terhadap sumbu y" if want == "genap" else "simetris terhadap titik asal (putar 180°)"
    return {
        "prompt": f"Manakah fungsi berikut yang merupakan fungsi <b>{want}</b>?",
        "correct": f"f(x) = {good[0]}", "distractors": [f"f(x) = {o[0]}" for o in others],
        "steps": [f"Fungsi {want} memenuhi {rule} untuk semua x di domain; grafiknya {sym}.",
                  f"Uji f(x) = {good[0]}: ganti x dengan −x dan sederhanakan — hasilnya memenuhi {rule}.",
                  "Fungsi lain gagal: mis. x² + x ⇒ f(−x) = x² − x, bukan f(x) maupun −f(x).",
                  f"Jawaban: <b>f(x) = {good[0]}</b>."],
        "graphs": [g2d("Uji simetri: titik (s, f(s)) dan (−s, f(−s))", [-4, 4], [-6, 6],
                       [param("s", "s", 0, 3.5, 0.05, 1.2, "s")],
                       [fn(good[1], "blue", good[0]), pt("s", good[1].replace("x", "s")), pt("-s", good[1].replace("x", "(-s)"), "orange")],
                       [readout("f(s)", good[1].replace("x", "s"), 3), readout("f(−s)", good[1].replace("x", "(-s)"), 3)],
                       "Bandingkan nilai f(s) dan f(−s) pada tabel saat s digeser.")],
        "explanation": "Genap: f(−x) = f(x). Ganjil: f(−x) = −f(x). Banyak fungsi tidak genap maupun ganjil.",
    }


@register("fn.iterasi", T, (4, 5))
def iterasi(rng, tier):
    k = rng.choice([v for v in (-3, -2, 2, 3, 4, 5) if v not in (0, 1)])
    nn = rng.randint(10, 40) if tier == 4 else rng.randint(2020, 2030)
    # f¹(k)=1/(1−k), f²(k)=(k−1)/k, f³(k)=k
    seq = [Fr(k), Fr(1, 1 - k), Fr(k - 1, k)]
    val = seq[nn % 3]
    return {
        "prompt": f"Diketahui f(x) = 1/(1 − x). Jika fⁿ berarti f dikomposisikan n kali, hitung f<sup>{nn}</sup>({n(k)}).",
        "correct": n(val), "distractors": [n(v) for v in seq if v != val] + [n(Fr(1, k)), n(-val)],
        "steps": ["Hitung beberapa iterasi: f(x) = 1/(1 − x).",
                  "f(f(x)) = 1/(1 − 1/(1 − x)) = (x − 1)/x, lalu f(f(f(x))) = x. Jadi f berulang dengan periode 3.",
                  f"{nn} = 3·{nn // 3} + {nn % 3} ⇒ f<sup>{nn}</sup> = f<sup>{nn % 3}</sup>.",
                  f"f<sup>{nn % 3}</sup>({n(k)}) = <b>{n(val)}</b>."],
        "explanation": "Cari pola periodik pada iterasi fungsi, lalu gunakan sisa pembagian.",
    }


@register("fn.fungsional", T, (4, 5))
def fungsional(rng, tier):
    p = nz(rng, -6, 6)
    q = rng.randint(-9, 9)
    while (2 * p + q) % 3:
        q += 1
    k = rng.randint(-4, 5)
    c0 = Fr(2 * p + q, 3)
    val = -p * k + c0
    return {
        "prompt": f"Fungsi f memenuhi f(x) + 2f(1 − x) = {lin(p, q)} untuk semua x. Hitung f({n(k)}).",
        "correct": n(val), "distractors": [n(p * k + c0), n(Fr(p * k + q, 3)), n(val + p), n(-val)],
        "steps": ["Ganti x dengan 1 − x: f(1 − x) + 2f(x) = p(1 − x) + q.",
                  "Sistem: f(x) + 2f(1−x) = px + q dan 2f(x) + f(1−x) = p − px + q.",
                  f"Kalikan persamaan kedua dengan 2 lalu kurangi yang pertama: 3f(x) = −3px + 2p + q ⇒ f(x) = {lin(-p, c0)}.",
                  f"f({n(k)}) = <b>{n(val)}</b>."],
        "explanation": "Persamaan fungsional: substitusi cerdas menghasilkan sistem persamaan dalam f(x) dan f(1 − x).",
    }
