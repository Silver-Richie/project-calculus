"""
Topik: Pertidaksamaan (linear, ganda, kuadrat, rasional, polinom, AM-GM).
Rujukan: Stewart Lampiran A (Inequalities), Whitman Bab 1, Strang (MIT) §0.1.
"""

from fractions import Fraction as Fr

from .. import register
from ..fmt import MINUS, fac, interval, lin, n, paren, poly
from ..graphs import fn, g2d, hline, param, pt, readout, vband, vline
from .common import distinct, nz

T = "pre-pertidaksamaan"
FLIP = {"<": ">", ">": "<", "≤": "≥", "≥": "≤"}
STRICT = {"<": True, ">": True, "≤": False, "≥": False}


def ray(x0, op):
    """Himpunan {x | x op x0} sebagai interval."""
    if op in ("<", "≤"):
        return interval(None, x0, hi_closed=not STRICT[op])
    return interval(x0, None, lo_closed=not STRICT[op])


@register("ineq.sifat", T, (1, 2))
def sifat(rng, tier):
    a, b = sorted(distinct(rng, -9, 9, 2))
    c = nz(rng, -6, -1, ()) if tier == 1 else rng.choice([nz(rng, -6, -1, ()), nz(rng, 1, 6, ())])
    neg = c < 0
    correct = f"{n(a)}·({n(c)}) {'>' if neg else '<'} {n(b)}·({n(c)})"
    wrong = [f"{n(a)}·({n(c)}) {'<' if neg else '>'} {n(b)}·({n(c)})",
             f"{n(a)} + ({n(c)}) > {n(b)} + ({n(c)})", f"{n(a)} − ({n(c)}) > {n(b)} − ({n(c)})",
             f"{n(a)}·({n(c)}) = {n(b)}·({n(c)})"]
    return {
        "prompt": f"Diketahui {n(a)} &lt; {n(b)} dan c = {n(c)}. Pernyataan mana yang <b>benar</b>?",
        "correct": correct, "distractors": wrong,
        "steps": ["Menambah/mengurangi bilangan yang sama di kedua ruas tidak mengubah arah tanda.",
                  "Mengalikan dengan bilangan <b>positif</b> mempertahankan arah tanda; dengan bilangan <b>negatif</b> "
                  "arah tanda <b>dibalik</b>.",
                  f"c = {n(c)} {'negatif' if neg else 'positif'}, sehingga {n(a)}c = {n(a * c)} dan {n(b)}c = {n(b * c)}: "
                  f"<b>{correct}</b>."],
        "explanation": "Aturan kunci: kali/bagi dengan bilangan negatif → balik tanda pertidaksamaan.",
    }


@register("ineq.linear", T, (1, 2))
def linear(rng, tier):
    x0 = rng.randint(-6, 6)
    if tier == 1:
        a, c = nz(rng, -5, 5), 0
    else:
        a, c = distinct(rng, -5, 5, 2)
        if a == c:
            c += 1
    b = rng.randint(-9, 9)
    d = (a - c) * x0 + b
    op = rng.choice(["<", ">", "≤", "≥"])
    k = a - c
    res_op = op if k > 0 else FLIP[op]
    lhs, rhs = lin(a, b), lin(c, d) if c else n(d)
    correct = ray(x0, res_op)
    wrong = [ray(x0, FLIP[res_op]), ray(-x0 if x0 else x0 + 1, res_op),
             ray(x0, {"<": "≤", "≤": "<", ">": "≥", "≥": ">"}[res_op]), ray(x0 + 1, res_op)]
    steps = [f"Kumpulkan suku x di kiri, konstanta di kanan: {lin(k, 0)} {op} {n(d)} − {paren(b)} = {n(d - b)}."]
    if k < 0:
        steps.append(f"Bagi dengan {n(k)} (negatif) ⇒ tanda dibalik: x {res_op} {n(x0)}.")
    else:
        steps.append(f"Bagi dengan {n(k)} (positif) ⇒ tanda tetap: x {res_op} {n(x0)}.")
    steps.append(f"Himpunan penyelesaian: <b>{correct}</b>.")
    lo_edge, hi_edge = x0 - 8, x0 + 8
    xb = f"(dd-({b}))/({k})"
    band = vband(xb, hi_edge) if res_op in (">", "≥") else vband(lo_edge, xb)
    graph = g2d("Kapan garis kiri berada di bawah/atas garis kanan?", [lo_edge, hi_edge], [-25, 25],
                [param("dd", "Konstanta ruas kanan d", d - 10, d + 10, 1, d, "d")],
                [fn(f"{a}*x+({b})", "blue", f"kiri: {lhs}"), fn(f"{c}*x+dd", "orange", "kanan: cx + d"),
                 vline(xb, "red"), band, pt(xb, f"{a}*{xb}+({b})", "red")],
                [readout("Titik batas x = (d − b)/(a − c)", xb, 3)],
                "Geser d: titik potong kedua garis (batas penyelesaian) ikut bergeser. Daerah hijau = penyelesaian.")
    return {"prompt": f"Tentukan himpunan penyelesaian {lhs} {op} {rhs}.", "correct": correct,
            "distractors": wrong, "steps": steps, "graphs": [graph],
            "explanation": "Selesaikan seperti persamaan, tetapi balik tanda saat membagi/mengali bilangan negatif."}


@register("ineq.ganda", T, (1, 2))
def ganda(rng, tier):
    m = nz(rng, 1, 5) if tier == 1 else nz(rng, -5, 5)
    lo_x, hi_x = sorted(distinct(rng, -6, 7, 2))
    q = rng.randint(-8, 8)
    p_, r_ = m * lo_x + q, m * hi_x + q
    if m < 0:
        p_, r_ = r_, p_
    lc, hc = rng.choice([(True, True), (False, True), (True, False), (False, False)])
    sl, sh = ("≤" if lc else "<"), ("≤" if hc else "<")
    # Untuk m < 0 ujung kiri/kanan bertukar setelah dibagi.
    x_lc, x_hc = (lc, hc) if m > 0 else (hc, lc)
    correct = interval(lo_x, hi_x, x_lc, x_hc)
    wrong = [interval(lo_x, hi_x, not x_lc, not x_hc), interval(-hi_x, -lo_x, x_lc, x_hc),
             interval(p_ - q, r_ - q, x_lc, x_hc), interval(lo_x - 1, hi_x + 1, x_lc, x_hc)]
    steps = [f"Kurangi ketiga ruas dengan {n(q)}: {n(p_ - q)} {sl} {lin(m, 0)} {sh} {n(r_ - q)}.",
             f"Bagi ketiga ruas dengan {n(m)}" + (" (negatif ⇒ semua tanda dibalik, lalu tulis dari kecil ke besar)." if m < 0 else "."),
             f"Hasil: <b>{correct}</b>."]
    graph = g2d("Garis y = mx + q di dalam pita [p, r]", [lo_x - 6, hi_x + 6], [min(p_, r_) - 12, max(p_, r_) + 12],
                [param("p", "Batas bawah p", p_ - 10, p_ + 10, 1, p_, "p"),
                 param("r", "Batas atas r", r_ - 10, r_ + 10, 1, r_, "r")],
                [{"type": "hband", "from": "p", "to": "r", "color": "amber"}, fn(f"{m}*x+{q}", "blue", "y = mx + q"),
                 vband(f"min((p-{q})/{m},(r-{q})/{m})", f"max((p-{q})/{m},(r-{q})/{m})", "green")],
                [readout("x dari p", f"(p-{q})/{m}", 3), readout("x dari r", f"(r-{q})/{m}", 3)],
                "Pita kuning = nilai y yang diizinkan. Bagian x yang membuat garis berada di pita = daerah hijau.")
    return {"prompt": f"Selesaikan {n(p_)} {sl} {lin(m, q)} {sh} {n(r_)}.", "correct": correct,
            "distractors": wrong, "steps": steps, "graphs": [graph],
            "explanation": "Pertidaksamaan ganda diselesaikan sekaligus pada ketiga ruas."}


@register("ineq.kuadrat", T, (2, 3))
def kuadrat(rng, tier):
    r1, r2 = sorted(distinct(rng, -6, 7, 2))
    if r1 == -r2:
        r2 += 1
    k = 1 if tier == 2 else rng.choice([-1, 2, -2, 3])
    coeffs = [k, -k * (r1 + r2), k * r1 * r2]
    op = rng.choice(["<", ">", "≤", "≥"])
    closed = not STRICT[op]
    # tanda efektif setelah membagi k
    eff = op if k > 0 else FLIP[op]
    inside = eff in ("<", "≤")
    if inside:
        correct = interval(r1, r2, closed, closed)
        wrong_main = f"{interval(None, r1, hi_closed=closed)} ∪ {interval(r2, None, lo_closed=closed)}"
        bands = [vband("r1", "r2")]
    else:
        correct = f"{interval(None, r1, hi_closed=closed)} ∪ {interval(r2, None, lo_closed=closed)}"
        wrong_main = interval(r1, r2, closed, closed)
        bands = [vband(r1 - 8, "r1"), vband("r2", r2 + 8)]
    wrong = [wrong_main, interval(-r2, -r1, closed, closed), interval(r1, r2, not closed, not closed),
             f"{interval(None, -r2, hi_closed=closed)} ∪ {interval(-r1, None, lo_closed=closed)}"]
    steps = [f"Faktorkan: {poly(coeffs)} = {n(k) + '·' if k != 1 else ''}(x {MINUS if r1 >= 0 else '+'} {abs(r1)})(x {MINUS if r2 >= 0 else '+'} {abs(r2)}). "
             f"Akar: x = {n(r1)} dan x = {n(r2)}."]
    if k < 0:
        steps.append(f"Bagi dengan {n(k)} (negatif) ⇒ tanda dibalik menjadi “{eff} 0”.")
    steps += [f"Uji tanda: (x − r₁)(x − r₂) negatif di antara akar dan positif di luar akar.",
              f"Karena tanda “{eff}”, ambil daerah {'di antara' if inside else 'di luar'} akar"
              f"{' (akar termasuk)' if closed else ''}: <b>{correct}</b>."]
    graph = g2d("Parabola y = k(x − r₁)(x − r₂)", [r1 - 8, r2 + 8], [-30, 30],
                [param("r1", "Akar r₁", r1 - 6, r1 + 6, 0.5, r1, "r₁"), param("r2", "Akar r₂", r2 - 6, r2 + 6, 0.5, r2, "r₂"),
                 param("k", "Koefisien k", -3, 3, 0.5, k, "k")],
                [fn("k*(x-r1)*(x-r2)", "blue", "y"), pt("r1", 0), pt("r2", 0)] + bands,
                [readout("Puncak (x)", "(r1+r2)/2", 2), readout("Nilai di puncak", "-k*(r2-r1)**2/4", 3)],
                "Daerah hijau = penyelesaian soal. Ubah k menjadi negatif: parabola terbalik sehingga daerah tanda ikut berubah.")
    return {"prompt": f"Tentukan himpunan penyelesaian {poly(coeffs)} {op} 0.", "correct": correct,
            "distractors": wrong, "steps": steps, "graphs": [graph],
            "explanation": "Cari akar → buat garis bilangan tanda → pilih daerah sesuai tanda pertidaksamaan."}


@register("ineq.rasional", T, (3, 4))
def rasional(rng, tier):
    a, b = distinct(rng, -6, 6, 2)
    op = rng.choice(["<", ">", "≤", "≥"])
    if tier == 4:
        # (x − a)/(x − b) op 2  ⇔  (x − (2b − a))/(x − b) FLIP(op) 0
        a2 = 2 * b - a
        prompt = f"Tentukan himpunan penyelesaian (x {MINUS if a >= 0 else '+'} {abs(a)}) / (x {MINUS if b >= 0 else '+'} {abs(b)}) {op} 2."
        root, eff = a2, FLIP[op]
        pre = [f"Pindahkan 2 ke kiri: [(x − {n(a)}) − 2(x − {n(b)})]/(x − {n(b)}) {op} 0 ⇒ (−x + {n(2 * b - a)})/(x − {n(b)}) {op} 0.",
               f"Kalikan pembilang dengan −1 (tanda dibalik): (x − {n(a2)})/(x − {n(b)}) {eff} 0."]
        expr = f"(x-{a})/(x-{b})-2"
    else:
        prompt = f"Tentukan himpunan penyelesaian (x {MINUS if a >= 0 else '+'} {abs(a)}) / (x {MINUS if b >= 0 else '+'} {abs(b)}) {op} 0."
        root, eff, pre = a, op, []
        expr = f"(x-{a})/(x-{b})"
    lo, hi = sorted([root, b])
    if lo == -hi:
        return rasional(rng, tier)
    lo_c = (lo == root) and not STRICT[eff]
    hi_c = (hi == root) and not STRICT[eff]
    if eff in ("<", "≤"):
        correct = interval(lo, hi, lo_c, hi_c)
        wrong = [f"{interval(None, lo, hi_closed=lo_c)} ∪ {interval(hi, None, lo_closed=hi_c)}", interval(lo, hi, True, True)]
        bands = [vband(lo, hi)]
    else:
        correct = f"{interval(None, lo, hi_closed=lo_c)} ∪ {interval(hi, None, lo_closed=hi_c)}"
        wrong = [interval(lo, hi, lo_c, hi_c), f"{interval(None, lo, hi_closed=True)} ∪ {interval(hi, None, lo_closed=True)}"]
        bands = [vband(lo - 8, lo), vband(hi, hi + 8)]
    wrong += [interval(lo, hi, not lo_c, not hi_c), f"{interval(None, -hi, hi_closed=lo_c)} ∪ {interval(-lo, None, lo_closed=hi_c)}",
              interval(-hi, -lo, lo_c, hi_c)]
    steps = pre + [f"Titik kritis: pembuat nol pembilang x = {n(root)} dan pembuat nol penyebut x = {n(b)}.",
                   "Tanda pecahan sama dengan tanda (x − pembuat nol pembilang)(x − pembuat nol penyebut): negatif di antara, positif di luar.",
                   f"x = {n(b)} <b>tidak pernah</b> termasuk (penyebut nol). x = {n(root)} termasuk hanya bila tanda ≤ atau ≥.",
                   f"Jawaban: <b>{correct}</b>."]
    graph = g2d("Grafik ruas kiri (setelah dipindah ke bentuk … op 0)", [lo - 8, hi + 8], [-8, 8], [],
                [fn(expr, "blue", "f(x)"), vline(b, "red"), hline(0)] + bands, None,
                "Garis merah = asimtot tegak x = b (tidak terdefinisi). Daerah hijau = penyelesaian.")
    graph["params"] = [param("s", "Geser titik uji x", lo - 7, hi + 7, 0.05, (lo + hi) / 2, "x")]
    graph["elements"].append(pt("s", expr.replace("x", "s"), "orange", label="uji"))
    graph["readouts"] = [readout("f(x uji)", expr.replace("x", "s"), 4)]
    return {"prompt": prompt, "correct": correct, "distractors": wrong, "steps": steps, "graphs": [graph],
            "explanation": "Jangan mengalikan silang dengan penyebut yang tandanya belum diketahui; gunakan garis bilangan tanda."}


@register("ineq.aplikasi", T, (2, 3))
def aplikasi(rng, tier):
    if rng.random() < 0.5:
        F1 = rng.choice([41, 50, 59, 68])
        F2 = F1 + 9 * rng.randint(2, 6)
        c1, c2 = Fr(5, 9) * (F1 - 32), Fr(5, 9) * (F2 - 32)
        prompt = (f"Mesin di laboratorium (FT) harus bekerja pada suhu {F1} ≤ F ≤ {F2} derajat Fahrenheit. "
                  "Dengan C = 5/9 (F − 32), berapa rentang suhunya dalam Celsius?")
        correct = f"{n(c1)} ≤ C ≤ {n(c2)}"
        wrong = [f"{n(Fr(9, 5) * F1 + 32)} ≤ C ≤ {n(Fr(9, 5) * F2 + 32)}", f"{n(Fr(5, 9) * F1 - 32)} ≤ C ≤ {n(Fr(5, 9) * F2 - 32)}",
                 f"{n(c1)} &lt; C &lt; {n(c2)}", f"{n(c1 + 5)} ≤ C ≤ {n(c2 + 5)}"]
        steps = ["Kurangi ketiga ruas dengan 32, lalu kalikan dengan 5/9 (positif, arah tanda tetap).",
                 f"{F1} − 32 = {F1 - 32} → ×5/9 = {n(c1)};  {F2} − 32 = {F2 - 32} → ×5/9 = {n(c2)}.",
                 f"Jadi <b>{correct}</b>."]
        graph = g2d("Konversi F → C", [0, 120], [-20, 50], [param("F", "Suhu F", 0, 120, 1, F1, "F")],
                    [fn("5/9*(x-32)", "blue", "C = 5/9(F − 32)"), vband(F1, F2), pt("F", "5/9*(F-32)")],
                    [readout("C", "5/9*(F-32)", 2)], "Geser F di dalam pita hijau dan perhatikan nilai C.")
    else:
        fixed = rng.choice([25000, 30000, 40000])
        per = rng.choice([3000, 4000, 5000])
        gb = rng.randint(8, 20)
        budget = fixed + per * gb + rng.randint(0, per - 1)
        prompt = (f"Layanan cloud (Fasilkom) menagih Rp{fixed:,} per bulan ditambah Rp{per:,} per GB. "
                  f"Anggaran maksimal Rp{budget:,}. Berapa GB (bilangan bulat) terbanyak yang dapat dipakai?").replace(",", ".")
        correct = f"{gb} GB"
        wrong = [f"{gb + 1} GB", f"{gb - 1} GB", f"{budget // per} GB", f"{(budget - fixed) // (per // 2) // 2 + 2} GB"]
        steps = [f"Model: {fixed} + {per}·g ≤ {budget}.".replace(",", "."),
                 f"g ≤ ({budget} − {fixed}) / {per} = {n(Fr(budget - fixed, per))}.",
                 f"g bilangan bulat ⇒ g terbesar = <b>{gb}</b>."]
        graph = g2d("Biaya vs pemakaian", [0, gb + 10], [0, budget * 1.4],
                    [param("B", "Anggaran (Rp)", fixed, budget * 1.3, 1000, budget, "B")],
                    [fn(f"{fixed}+{per}*x", "blue", "biaya"), {"type": "hline", "y": "B", "color": "red", "dash": True},
                     vband(0, f"(B-{fixed})/{per}")],
                    [readout("GB maksimum (real)", f"(B-{fixed})/{per}", 3), readout("GB bulat", f"floor((B-{fixed})/{per})", 0)],
                    "Naikkan/turunkan anggaran: batas pemakaian = titik potong garis biaya dengan garis anggaran.")
    return {"prompt": prompt, "correct": correct, "distractors": wrong, "steps": steps, "graphs": [graph],
            "explanation": "Terjemahkan kalimat menjadi pertidaksamaan, selesaikan, lalu sesuaikan dengan konteks (mis. bilangan bulat)."}


@register("ineq.polinom", T, (4, 5))
def polinom(rng, tier):
    a, b, c = sorted(distinct(rng, -6, 7, 3))
    if tier == 4:
        prompt = f"Selesaikan {fac(a)}{fac(b)}{fac(c)} &lt; 0."
        correct = f"{interval(None, a, hi_closed=False)} ∪ {interval(b, c, False, False)}"
        wrong = [f"{interval(a, b, False, False)} ∪ {interval(c, None, lo_closed=False)}", interval(a, c, False, False),
                 f"{interval(None, a, hi_closed=True)} ∪ {interval(b, c, True, True)}", interval(None, a, hi_closed=False)]
        steps = [f"Akar: {n(a)} &lt; {n(b)} &lt; {n(c)}. Untuk x sangat besar, ketiga faktor positif ⇒ hasil positif.",
                 "Setiap melewati akar berderajat ganjil, tanda berganti: (+) di kanan c, (−) di (b, c), (+) di (a, b), (−) di kiri a.",
                 f"Ambil daerah negatif: <b>{correct}</b>."]
        expr = f"(x-{a})*(x-{b})*(x-{c})/10"
    else:
        # (x − d)² (x − b)(x − c) ≤ 0 dengan d di luar [b, c]
        d = rng.choice([v for v in range(-8, 10) if v < b - 1 or v > c + 1] or [c + 3])
        prompt = f"Selesaikan {fac(d) if d else '(x)'}²{fac(b)}{fac(c)} ≤ 0."
        correct = f"{interval(b, c)} ∪ {{{n(d)}}}"
        wrong = [interval(b, c), interval(b, c, False, False), f"{interval(min(b, d), max(c, d))}",
                 f"{interval(None, b)} ∪ {interval(c, None)}"]
        steps = [f"(x − {n(d)})² ≥ 0 selalu, dan bernilai 0 hanya di x = {n(d)}.",
                 f"Untuk x ≠ {n(d)}, tanda ditentukan oleh (x − {n(b)})(x − {n(c)}) ≤ 0 ⇒ {interval(b, c)}.",
                 f"Tambahkan x = {n(d)} (hasil kali 0 memenuhi ≤ 0): <b>{correct}</b>. Akar berderajat genap tidak mengganti tanda."]
        expr = f"(x-{d})**2*(x-{b})*(x-{c})/40"
    graph = g2d("Grafik polinom (diskalakan) dan tanda tiap daerah", [min(a, b) - 5, max(c, b) + 6], [-12, 12],
                [param("s", "Titik uji x", min(a, b) - 4, max(c, b) + 5, 0.05, (b + c) / 2, "x")],
                [fn(expr, "blue", "p(x)"), hline(0), pt("s", expr.replace("x", "s"), "orange", label="uji")],
                [readout("p(x uji)", expr.replace("x", "s"), 4)],
                "Geser titik uji melewati setiap akar: tanda berganti di akar ganjil, tetap di akar genap.")
    return {"prompt": prompt, "correct": correct, "distractors": wrong, "steps": steps, "graphs": [graph],
            "explanation": "Metode garis bilangan tanda: akar berderajat ganjil mengganti tanda, akar berderajat genap tidak."}


@register("ineq.amgm", T, (4, 5))
def amgm(rng, tier):
    s = rng.randint(2, 7)
    a = 1 if tier == 4 else rng.choice([1, 4, 9])
    b = s * s
    # minimum ax + b/x (x > 0) = 2√(ab), dicapai di x = √(b/a); a kuadrat sempurna ⇒ √(ab) bulat
    ab = a * b
    root = int(round(ab ** 0.5))
    mn = 2 * root
    xs = Fr(root, a)
    prompt = f"Untuk x &gt; 0, tentukan nilai minimum f(x) = {'' if a == 1 else a}x + {b}/x."
    return {
        "prompt": prompt, "correct": n(mn), "distractors": [n(mn + 1), n(root), n(b + a), n(2 * b)],
        "steps": ["Ketaksamaan AM–GM: untuk p, q &gt; 0 berlaku (p + q)/2 ≥ √(pq).",
                  f"Ambil p = {'' if a == 1 else a}x dan q = {b}/x: p·q = {ab} (konstan!).",
                  f"Maka f(x) ≥ 2√{ab} = {mn}, dengan kesamaan saat p = q ⇔ x = {n(xs)}.",
                  f"Nilai minimum = <b>{mn}</b>."],
        "graphs": [g2d("f(x) = ax + b/x untuk x > 0", [0.2, 3 * float(xs) + 2], [0, mn * 2.5],
                       [param("aa", "Koefisien a", 0.5, 9, 0.5, a, "a"), param("bb", "Konstanta b", 1, 60, 1, b, "b")],
                       [fn("aa*x+bb/x", "blue", "f(x)", **{"from": 0.05}), pt("sqrt(bb/aa)", "2*sqrt(aa*bb)", "red", label="minimum"),
                        {"type": "hline", "y": "2*sqrt(aa*bb)", "color": "gray", "dash": True}],
                       [readout("x minimum = √(b/a)", "sqrt(bb/aa)", 3), readout("Nilai minimum 2√(ab)", "2*sqrt(aa*bb)", 3)],
                       "Geser a dan b: titik minimum selalu terjadi saat ax = b/x.")],
        "explanation": "AM–GM: jumlah dua bilangan positif dengan hasil kali tetap minimum ketika keduanya sama.",
    }


@register("ineq.definit", T, (4, 5))
def definit(rng, tier):
    p = rng.randint(2, 5)
    c = p * (p - 1)
    # x² − 2mx + (m + c) > 0 ∀x ⇔ D < 0 ⇔ m² − m − c < 0 ⇔ (m − p)(m + p − 1) < 0
    lo, hi = 1 - p, p
    correct = f"{n(lo)} &lt; m &lt; {n(hi)}"
    wrong = [f"m &lt; {n(lo)} atau m &gt; {n(hi)}", f"{n(lo)} ≤ m ≤ {n(hi)}", f"{n(-hi)} &lt; m &lt; {n(-lo)}", f"m &gt; {n(hi)}"]
    return {
        "prompt": f"Tentukan semua nilai m agar x² − 2mx + (m + {c}) &gt; 0 untuk <b>setiap</b> bilangan real x.",
        "correct": correct, "distractors": wrong,
        "steps": ["Parabola terbuka ke atas (a = 1 &gt; 0). Agar selalu positif, parabola tidak boleh menyentuh sumbu x ⇒ diskriminan D &lt; 0.",
                  f"D = (−2m)² − 4·1·(m + {c}) = 4m² − 4m − {4 * c} &lt; 0 ⇔ m² − m − {c} &lt; 0.",
                  f"Faktorkan: (m − {p})(m + {p - 1}) &lt; 0 ⇒ <b>{correct}</b>."],
        "graphs": [g2d("y = x² − 2mx + (m + c)", [-8, 8], [-10, 30],
                       [param("m", "Parameter m", lo - 3, hi + 3, 0.1, (lo + hi) / 2, "m")],
                       [fn(f"x**2-2*m*x+m+{c}", "blue", "y"), pt("m", f"-m*m+m+{c}", "red", label="puncak"), hline(0)],
                       [readout("Diskriminan D", f"4*m*m-4*(m+{c})", 3), readout("y puncak", f"-m*m+m+{c}", 3)],
                       f"Geser m keluar dari interval ({lo}, {hi}): puncak turun di bawah sumbu x (D ≥ 0) sehingga parabola tidak lagi selalu positif.")],
        "explanation": "ax² + bx + c > 0 untuk semua x ⇔ a > 0 dan D < 0 (definit positif).",
    }
