"""
Topik: Nilai Mutlak (definisi, persamaan, pertidaksamaan, ketaksamaan segitiga).
Rujukan: Stewart Lampiran A (Absolute Value), Whitman Bab 1, Strang (MIT) §0.1.
"""

from fractions import Fraction as Fr

from .. import register
from ..fmt import MINUS, interval, lin, n
from ..graphs import fn, g2d, param, pt, readout, vband
from .common import distinct, nz

T = "pre-nilai-mutlak"


def xm(a):
    """Teks 'x − a' dengan tanda yang benar."""
    return f"x {MINUS} {a}" if a > 0 else (f"x + {-a}" if a < 0 else "x")


def abs_graph(title, expr, c_label, c_value, c_range, xr, yr, bands, caption, reads=None):
    return g2d(title, xr, yr, [param("c", c_label, c_range[0], c_range[1], 0.5, c_value, "c")],
               [fn(expr, "blue", "y"), {"type": "hline", "y": "c", "color": "red", "dash": True}] + bands,
               reads, caption)


@register("abs.hitung", T, (1,))
def hitung(rng, tier):
    a, b, c, d = distinct(rng, -9, 9, 4)
    e = nz(rng, -9, 9)
    val = abs(a - b) - abs(c - d) + abs(e)
    return {
        "prompt": f"Hitung |{n(a)} − ({n(b)})| − |{n(c)} − ({n(d)})| + |{n(e)}|.",
        "correct": n(val),
        "distractors": [n((a - b) - (c - d) + e), n(abs(a - b) + abs(c - d) + abs(e)),
                        n(abs(a + b) - abs(c + d) + abs(e)), n(val + 2), n(val - 2)],
        "steps": [f"|{n(a)} − ({n(b)})| = |{n(a - b)}| = {abs(a - b)}.",
                  f"|{n(c)} − ({n(d)})| = |{n(c - d)}| = {abs(c - d)}.", f"|{n(e)}| = {abs(e)}.",
                  f"{abs(a - b)} − {abs(c - d)} + {abs(e)} = <b>{n(val)}</b>."],
        "explanation": "|a| adalah jarak a ke 0, jadi selalu ≥ 0; |a − b| adalah jarak antara a dan b.",
    }


@register("abs.konsep", T, (1, 2))
def konsep(rng, tier):
    a = nz(rng, -7, 7)
    if tier == 1:
        prompt = f"Jika x &lt; {n(a)}, maka |{xm(a)}| sama dengan …"
        correct = lin(-1, a) if a else f"{MINUS}x"
        wrong = [xm(a), lin(1, a), lin(-1, -a)]
        steps = [f"Untuk x &lt; {n(a)}, nilai {xm(a)} negatif.",
                 "Definisi: |u| = u bila u ≥ 0 dan |u| = −u bila u &lt; 0.",
                 f"Jadi |{xm(a)}| = −({xm(a)}) = <b>{correct}</b>."]
    else:
        prompt = "Untuk setiap bilangan real x, √(x²) sama dengan …"
        correct, wrong = "|x|", ["x", f"{MINUS}x", "x²", "±x"]
        steps = ["√ selalu menghasilkan bilangan tak negatif.",
                 "Jika x = −3 maka √((−3)²) = √9 = 3 = |−3|, bukan −3.", "Jadi √(x²) = <b>|x|</b>."]
    return {"prompt": prompt, "correct": correct, "distractors": wrong, "steps": steps,
            "graphs": [g2d("y = |x − a| sebagai dua potong garis", [-10, 10], [-2, 12],
                           [param("aa", "Geser a", -7, 7, 0.5, a, "a")],
                           [fn("abs(x-aa)", "blue", "|x − a|"), fn("aa-x", "orange", "a − x (bagian kiri)", dash=True),
                            fn("x-aa", "green", "x − a (bagian kanan)", dash=True), pt("aa", 0)],
                           [readout("Titik patah x = a", "aa", 2)],
                           "Di kiri titik a grafik |x − a| berimpit dengan a − x; di kanan berimpit dengan x − a.")],
            "explanation": "|u| = u (u ≥ 0) dan |u| = −u (u < 0)."}


@register("abs.persamaan", T, (1, 2))
def persamaan(rng, tier):
    a = 1 if tier == 1 else rng.choice([2, 3, -2, 3])
    x1, x2 = sorted(distinct(rng, -8, 8, 2))
    # |a x + b| = c dengan akar x1, x2: a x1 + b = −(a x2 + b) ⇒ b = −a(x1 + x2)/2 ; pilih x1 + x2 genap
    if (x1 + x2) % 2:
        x2 += 1
        if x2 == x1:
            x2 += 2
    b = -a * (x1 + x2) // 2
    c = abs(a * x1 + b)
    if c == 0:
        x2 += 2
        b = -a * (x1 + x2) // 2
        c = abs(a * x1 + b)
    sol = sorted([x1, x2])
    correct = f"x = {n(sol[0])} atau x = {n(sol[1])}"
    wrong = [f"x = {n(Fr(c - b, a))} saja", f"x = {n(-sol[1])} atau x = {n(-sol[0])}",
             f"x = {n(sol[0] - 1)} atau x = {n(sol[1] + 1)}", "tidak ada penyelesaian"]
    return {
        "prompt": f"Selesaikan |{lin(a, b)}| = {c}.",
        "correct": correct, "distractors": wrong,
        "steps": [f"|u| = {c} (dengan {c} &gt; 0) ⇔ u = {c} atau u = −{c}.",
                  f"{lin(a, b)} = {c} ⇒ x = {n(Fr(c - b, a))}.", f"{lin(a, b)} = −{c} ⇒ x = {n(Fr(-c - b, a))}.",
                  f"Jadi <b>{correct}</b>."],
        "graphs": [abs_graph("Perpotongan y = |ax + b| dengan y = c", f"abs({a}*x+({b}))", "Nilai kanan c", c, (-3, c + 8),
                             [min(sol) - 6, max(sol) + 6], [-3, c + 10],
                             [pt(f"(c-({b}))/{a}", "c"), pt(f"(-c-({b}))/{a}", "c")],
                             "Geser c: dua titik potong (c > 0), satu titik (c = 0), atau tidak ada penyelesaian (c < 0).",
                             [readout("x₁", f"(c-({b}))/{a}", 3), readout("x₂", f"(-c-({b}))/{a}", 3)])],
        "explanation": "|u| = c punya 2 solusi jika c > 0, 1 solusi jika c = 0, dan tidak ada jika c < 0.",
    }


@register("abs.kurang_dari", T, (2, 3))
def kurang_dari(rng, tier):
    a = rng.choice([1, 1, 2, 3]) if tier == 3 else 1
    m = rng.randint(-6, 6)
    r = rng.randint(1, 6) * a
    b = -a * m
    op = rng.choice(["&lt;", "≤"])
    closed = op == "≤"
    lo, hi = Fr(-r - b, a), Fr(r - b, a)
    correct = interval(lo, hi, closed, closed)
    wrong = [f"{interval(None, lo, hi_closed=closed)} ∪ {interval(hi, None, lo_closed=closed)}",
             interval(lo, hi, not closed, not closed), interval(-hi, -lo, closed, closed), interval(lo - 1, hi + 1, closed, closed)]
    return {
        "prompt": f"Tentukan himpunan penyelesaian |{lin(a, b)}| {op} {r}.",
        "correct": correct, "distractors": wrong,
        "steps": [f"|u| {op} r ⇔ −r {op} u {op} r (jarak u ke 0 kurang dari r).",
                  f"−{r} {op} {lin(a, b)} {op} {r}.",
                  f"Kurangi {n(b)}, bagi {a}: {n(lo)} {op} x {op} {n(hi)}.", f"Jadi <b>{correct}</b>."],
        "graphs": [abs_graph("|ax + b| di bawah garis y = c", f"abs({a}*x+({b}))", "Batas c", r, (0, r + 8),
                             [float(lo) - 5, float(hi) + 5], [-2, r + 10],
                             [vband(f"(-c-({b}))/{a}", f"(c-({b}))/{a}")],
                             "Daerah hijau = x yang membuat grafik berada di bawah garis merah.",
                             [readout("Lebar penyelesaian", f"2*c/{a}", 3)])],
        "explanation": "|u| < r ⇔ −r < u < r (satu interval).",
    }


@register("abs.lebih_dari", T, (2, 3))
def lebih_dari(rng, tier):
    a = rng.choice([1, 2, 3]) if tier == 3 else 1
    m = rng.randint(-6, 6)
    r = rng.randint(1, 6) * a
    b = -a * m
    op = rng.choice(["&gt;", "≥"])
    closed = op == "≥"
    lo, hi = Fr(-r - b, a), Fr(r - b, a)
    correct = f"{interval(None, lo, hi_closed=closed)} ∪ {interval(hi, None, lo_closed=closed)}"
    wrong = [interval(lo, hi, closed, closed), f"{interval(None, lo, hi_closed=not closed)} ∪ {interval(hi, None, lo_closed=not closed)}",
             f"{interval(None, -hi, hi_closed=closed)} ∪ {interval(-lo, None, lo_closed=closed)}", interval(hi, None, lo_closed=closed)]
    return {
        "prompt": f"Tentukan himpunan penyelesaian |{lin(a, b)}| {op} {r}.",
        "correct": correct, "distractors": wrong,
        "steps": [f"|u| {op} r ⇔ u {op} r <b>atau</b> u {'≤' if closed else '&lt;'} −r.",
                  f"{lin(a, b)} {op} {r} ⇒ x {op} {n(hi)}.", f"{lin(a, b)} {'≤' if closed else '&lt;'} −{r} ⇒ x {'≤' if closed else '&lt;'} {n(lo)}.",
                  f"Gabungkan: <b>{correct}</b>."],
        "graphs": [abs_graph("|ax + b| di atas garis y = c", f"abs({a}*x+({b}))", "Batas c", r, (0, r + 8),
                             [float(lo) - 6, float(hi) + 6], [-2, r + 10],
                             [vband(float(lo) - 6, f"(-c-({b}))/{a}"), vband(f"(c-({b}))/{a}", float(hi) + 6)],
                             "Daerah hijau = x yang membuat grafik di atas garis merah (dua bagian terpisah).")],
        "explanation": "|u| > r ⇔ u > r atau u < −r (gabungan dua interval).",
    }


@register("abs.dua_mutlak", T, (3, 4))
def dua_mutlak(rng, tier):
    a, b = distinct(rng, -8, 8, 2)
    if tier == 3:
        if (a + b) % 2:
            b += 1 if b + 1 != a else -1
        sol = Fr(a + b, 2)
        prompt = f"Selesaikan |{xm(a)}| = |{xm(b)}|."
        correct = f"x = {n(sol)}"
        wrong = [f"x = {n(Fr(a - b, 2))}", f"x = {n(a)} atau x = {n(b)}", f"x = {n(sol + 1)}", "semua bilangan real"]
        steps = ["|x − a| = |x − b| artinya jarak x ke a sama dengan jarak x ke b.",
                 f"Titik yang berjarak sama dari {n(a)} dan {n(b)} adalah titik tengahnya.",
                 f"x = ({n(a)} + {n(b)})/2 = <b>{n(sol)}</b>. (Cek aljabar: kuadratkan kedua ruas ⇒ persamaan linear.)"]
        k = 1
    else:
        while (a + 2 * b) % 3:
            a += 1
        if a == b:
            a += 3
        s1, s2 = sorted([2 * b - a, Fr(a + 2 * b, 3)])
        prompt = f"Selesaikan |{xm(a)}| = 2|{xm(b)}|."
        correct = f"x = {n(s1)} atau x = {n(s2)}"
        wrong = [f"x = {n(2 * b - a)} saja", f"x = {n(Fr(a + b, 2))}", f"x = {n(-s2)} atau x = {n(-s1)}", f"x = {n(s1 + 1)} atau x = {n(s2 + 1)}"]
        steps = ["|u| = |v| ⇔ u = v atau u = −v.",
                 f"x − {n(a)} = 2(x − {n(b)}) ⇒ x = {n(2 * b - a)}.",
                 f"x − {n(a)} = −2(x − {n(b)}) ⇒ 3x = {n(a + 2 * b)} ⇒ x = {n(Fr(a + 2 * b, 3))}.",
                 f"Jadi <b>{correct}</b>."]
        k = 2
    return {"prompt": prompt, "correct": correct, "distractors": wrong, "steps": steps,
            "graphs": [g2d("Perpotongan dua grafik nilai mutlak", [min(a, b) - 8, max(a, b) + 8], [-1, 16],
                           [param("kk", "Pengali k di ruas kanan", 0.5, 3, 0.5, k, "k")],
                           [fn(f"abs(x-({a}))", "blue", "|x − a|"), fn(f"kk*abs(x-({b}))", "orange", "k|x − b|")],
                           None, "Ubah k: untuk k = 1 hanya ada satu titik potong (titik tengah); untuk k ≠ 1 ada dua.")],
            "explanation": "|u| = |v| ⇔ u² = v² ⇔ u = ±v."}


@register("abs.jumlah", T, (4, 5))
def jumlah(rng, tier):
    a, b = sorted(distinct(rng, -6, 6, 2))
    k = (b - a) + 2 * rng.randint(1, 4)
    lo, hi = Fr(a + b - k, 2), Fr(a + b + k, 2)
    if tier == 4:
        prompt = f"Selesaikan |{xm(a)}| + |{xm(b)}| = {k}."
        correct = f"x = {n(lo)} atau x = {n(hi)}"
        wrong = [interval(lo, hi), f"x = {n(a)} atau x = {n(b)}", f"x = {n(lo - 1)} atau x = {n(hi + 1)}", "tidak ada penyelesaian"]
        last = f"Jadi <b>{correct}</b>."
    else:
        prompt = f"Tentukan himpunan penyelesaian |{xm(a)}| + |{xm(b)}| ≤ {k}."
        correct = interval(lo, hi)
        wrong = [interval(a, b), f"{interval(None, lo)} ∪ {interval(hi, None)}", interval(lo, hi, False, False), interval(lo + 1, hi - 1)]
        last = f"Nilai di antara keduanya ≤ {k}, jadi <b>{correct}</b>."
    return {
        "prompt": prompt, "correct": correct, "distractors": wrong,
        "steps": [f"Bagi garis bilangan di titik {n(a)} dan {n(b)}.",
                  f"Untuk {n(a)} ≤ x ≤ {n(b)}: jumlahnya konstan = {b - a} (&lt; {k}), jadi tidak ada solusi persamaan di sini.",
                  f"Untuk x &gt; {n(b)}: 2x − ({n(a + b)}) = {k} ⇒ x = {n(hi)}.  Untuk x &lt; {n(a)}: −2x + ({n(a + b)}) = {k} ⇒ x = {n(lo)}.",
                  last],
        "graphs": [g2d("y = |x − a| + |x − b| (bentuk ‘bak mandi’)", [a - 8, b + 8], [-1, k + 10],
                       [param("c", "Nilai kanan k", 0, k + 8, 0.5, k, "k")],
                       [fn(f"abs(x-({a}))+abs(x-({b}))", "blue", "y"), {"type": "hline", "y": "c", "color": "red", "dash": True},
                        vband(f"({a + b}-c)/2", f"({a + b}+c)/2")],
                       [readout("Nilai minimum = |a − b|", str(b - a), 2)],
                       f"Geser k di bawah {b - a}: tidak ada solusi. Tepat {b - a}: semua titik di [a, b]. Di atasnya: dua solusi.")],
        "explanation": "|x − a| + |x − b| ≥ |a − b|, dengan kesamaan untuk x di antara a dan b.",
    }


@register("abs.bulat_jarak", T, (4, 5))
def bulat_jarak(rng, tier):
    a, b = sorted(distinct(rng, -15, 15, 2))
    cnt = b - a + 1
    return {
        "prompt": f"Berapa banyak bilangan <b>bulat</b> x yang memenuhi |{xm(a)}| + |{xm(b)}| = {b - a}?",
        "correct": str(cnt), "distractors": [str(cnt - 1), str(cnt + 1), "2", str(cnt - 2)],
        "steps": [f"Ketaksamaan segitiga: |x − {n(a)}| + |{n(b)} − x| ≥ |{n(b)} − {n(a)}| = {b - a}.",
                  f"Kesamaan terjadi tepat untuk {n(a)} ≤ x ≤ {n(b)} (x berada di antara kedua titik).",
                  f"Bilangan bulat dari {n(a)} sampai {n(b)}: {n(b)} − ({n(a)}) + 1 = <b>{cnt}</b>."],
        "explanation": "|u| + |v| ≥ |u + v| (ketaksamaan segitiga), sama dengan bila u dan v sejenis tanda.",
    }


@register("abs.selisih_maks", T, (4, 5))
def selisih_maks(rng, tier):
    a, b = rng.randint(1, 9), rng.randint(1, 9)
    mx = a + b
    return {
        "prompt": f"Tentukan nilai maksimum f(x) = |x + {a}| − |x − {b}| untuk x real.",
        "correct": n(mx), "distractors": [n(abs(a - b)) if a != b else n(mx + 2), n(2 * mx), "tidak ada maksimum", n(max(a, b))],
        "steps": ["Ketaksamaan segitiga terbalik: |u| − |v| ≤ |u − v|.",
                  f"Ambil u = x + {a}, v = x − {b}: u − v = {a + b}, jadi f(x) ≤ {a + b}.",
                  f"Nilai {a + b} tercapai untuk semua x ≥ {b}. Maksimum = <b>{mx}</b>."],
        "graphs": [g2d("f(x) = |x + a| − |x − b|", [-a - 8, b + 8], [-mx - 3, mx + 3],
                       [param("aa", "a", 1, 9, 1, a, "a"), param("bb", "b", 1, 9, 1, b, "b")],
                       [fn("abs(x+aa)-abs(x-bb)", "blue", "f(x)"), {"type": "hline", "y": "aa+bb", "color": "red", "dash": True},
                        {"type": "hline", "y": "-(aa+bb)", "color": "gray", "dash": True}],
                       [readout("Maksimum a + b", "aa+bb", 2)],
                       "Grafiknya mendatar di kiri (−(a+b)) dan di kanan (a+b), dengan garis miring di tengah.")],
        "explanation": "||u| − |v|| ≤ |u − v|.",
    }
