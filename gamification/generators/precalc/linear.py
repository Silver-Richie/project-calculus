"""
Topik: Fungsi Linear — gradien, persamaan garis, sejajar/tegak lurus, titik potong, jarak, aplikasi.
Rujukan: Whitman §1.1–1.2; Stewart Lampiran B (Coordinate Geometry and Lines); Strang (MIT) §1.1.
"""

from fractions import Fraction as Fr

from .. import register
from ..fmt import MINUS, gcd, lin, n, paren
from ..graphs import fn, g2d, param, pt, readout
from .common import distinct, nz

T = "pre-fungsi-linear"


def y_eq(m, c):
    return f"y = {lin(m, c)}"


def line_graph(title, m, c, caption, extra=None, reads=None):
    return g2d(title, [-10, 10], [-10, 10],
               [param("m", "Gradien m", -5, 5, 0.25, float(m), "m"), param("c", "Titik potong sumbu-y c", -8, 8, 0.5, float(c), "c")],
               [fn("m*x+c", "blue", "y = mx + c"), pt(0, "c", label="(0, c)")] + (extra or []),
               [readout("Gradien m", "m", 3), readout("Titik potong sumbu-x", "-c/m", 3)] + (reads or []), caption)


@register("lin.gradien", T, (1, 2))
def gradien(rng, tier):
    x1, x2 = distinct(rng, -6, 6, 2)
    y1, y2 = rng.randint(-8, 8), rng.randint(-8, 8)
    m = Fr(y2 - y1, x2 - x1)
    return {
        "prompt": f"Tentukan gradien garis yang melalui titik ({n(x1)}, {n(y1)}) dan ({n(x2)}, {n(y2)}).",
        "correct": n(m), "distractors": [n(Fr(x2 - x1, y2 - y1)) if y2 != y1 else "tidak terdefinisi", n(-m),
                                         n(Fr(y2 + y1, x2 - x1)), n(Fr(y2 - y1, x2 + x1)) if x2 + x1 else n(m + 1)],
        "steps": ["Gradien m = Δy/Δx = (y₂ − y₁)/(x₂ − x₁).",
                  f"Δy = {n(y2)} − {paren(y1)} = {n(y2 - y1)}, Δx = {n(x2)} − {paren(x1)} = {n(x2 - x1)}.",
                  f"m = {n(y2 - y1)}/{n(x2 - x1)} = <b>{n(m)}</b>."
                  + (" Gradien 0 berarti garis mendatar." if m == 0 else "")],
        "graphs": [g2d("Gradien = naik / maju", [-10, 10], [-10, 10],
                       [param("px", "x titik kedua", -8, 8, 0.5, x2, "x₂"), param("py", "y titik kedua", -8, 8, 0.5, y2, "y₂")],
                       [fn(f"{y1}+(py-({y1}))/(px-({x1}))*(x-({x1}))", "blue", "garis"), pt(x1, y1, "navy"), pt("px", "py"),
                        {"type": "segment", "x1": x1, "y1": y1, "x2": "px", "y2": y1, "color": "orange", "dash": True},
                        {"type": "segment", "x1": "px", "y1": y1, "x2": "px", "y2": "py", "color": "green", "dash": True}],
                       [readout("Δx (oranye)", f"px-({x1})", 2), readout("Δy (hijau)", f"py-({y1})", 2),
                        readout("m = Δy/Δx", f"(py-({y1}))/(px-({x1}))", 4)],
                       "Geser titik kedua: rasio Δy/Δx tetap sama selama titik berada di garis yang sama.")],
        "explanation": "Gradien positif: garis naik; negatif: turun; nol: mendatar; Δx = 0: tegak (gradien tak terdefinisi).",
    }


@register("lin.persamaan_garis", T, (1, 2))
def persamaan_garis(rng, tier):
    m = Fr(nz(rng, -4, 4)) if tier == 1 else Fr(nz(rng, -5, 5), rng.choice([1, 2, 3]))
    x1, y1 = rng.randint(-5, 5), rng.randint(-6, 6)
    c = y1 - m * x1
    correct = y_eq(m, c)
    return {
        "prompt": f"Persamaan garis dengan gradien {n(m)} yang melalui titik ({n(x1)}, {n(y1)}) adalah …",
        "correct": correct, "distractors": [y_eq(m, y1 + m * x1), y_eq(-m, y1 + m * x1), y_eq(m, -c), y_eq(Fr(1) / m, c),
                        y_eq(m, c + 1), y_eq(m, c - 2), y_eq(-m, c)],
        "steps": ["Bentuk titik–gradien: y − y₁ = m(x − x₁).",
                  f"y − {paren(y1)} = {n(m)}(x − {paren(x1)}).",
                  f"y = {n(m)}x − {paren(m * x1)} + {paren(y1)} = <b>{lin(m, c)}</b>."],
        "graphs": [line_graph("Garis y = mx + c", m, c, "Geser m (kemiringan) dan c (titik potong sumbu-y); titik merah = titik yang harus dilalui.",
                              [pt(x1, y1, "red", label="titik soal")], [readout("y di x₁", f"m*{x1}+c", 3)])],
        "explanation": "y − y₁ = m(x − x₁) langsung memberi persamaan garis bila gradien dan satu titik diketahui.",
    }


@register("lin.sejajar_tegak", T, (2, 3))
def sejajar_tegak(rng, tier):
    a, b = nz(rng, -5, 5), nz(rng, -5, 5)
    k = rng.randint(-9, 9)
    m0 = Fr(-a, b)
    kind = rng.choice(["sejajar", "tegak lurus"])
    m = m0 if kind == "sejajar" else Fr(-1) / m0
    x1, y1 = rng.randint(-4, 4), rng.randint(-5, 5)
    c = y1 - m * x1
    correct = y_eq(m, c)
    other = Fr(-1) / m0 if kind == "sejajar" else m0
    return {
        "prompt": f"Tentukan persamaan garis yang <b>{kind}</b> dengan garis {lin(a, 0)} {'+' if b > 0 else MINUS} {abs(b)}y = {n(k)} "
                  f"dan melalui titik ({n(x1)}, {n(y1)}).",
        "correct": correct, "distractors": [y_eq(other, y1 - other * x1), y_eq(-m, y1 + m * x1), y_eq(m, -c), y_eq(-m, c),
                        y_eq(m, c + 1), y_eq(other, c - 1), y_eq(m, c - 2)],
        "steps": [f"Ubah ke bentuk y = mx + c: y = {n(m0)}x + …, jadi gradien garis awal m₀ = {n(m0)}.",
                  "Sejajar ⇒ gradien sama; tegak lurus ⇒ m·m₀ = −1." + (f" Jadi m = {n(m)}." if kind == "sejajar" else f" Jadi m = −1/{paren(m0)} = {n(m)}."),
                  f"y − {paren(y1)} = {n(m)}(x − {paren(x1)}) ⇒ <b>{lin(m, c)}</b>."],
        "graphs": [g2d("Garis acuan (abu-abu) dan garis baru", [-10, 10], [-10, 10],
                       [param("mm", "Gradien garis baru", -5, 5, 0.05, float(m), "m")],
                       [fn(f"{float(m0)}*x+{float(Fr(k, b))}", "gray", "garis acuan"),
                        fn(f"mm*(x-({x1}))+({y1})", "blue", "garis baru"), pt(x1, y1)],
                       [readout("m · m₀", f"mm*{float(m0)}", 4)],
                       "Saat m · m₀ = −1 kedua garis membentuk sudut siku-siku; saat m = m₀ keduanya sejajar.")],
        "explanation": "Sejajar: m₁ = m₂. Tegak lurus: m₁·m₂ = −1.",
    }


@register("lin.titik_potong", T, (2, 3))
def titik_potong(rng, tier):
    x0, y0 = rng.randint(-5, 5), rng.randint(-5, 5)
    m1, m2 = distinct(rng, -4, 4, 2, exclude=(0,))
    c1, c2 = y0 - m1 * x0, y0 - m2 * x0
    if tier == 2:
        prompt = f"Tentukan titik potong garis {y_eq(m1, c1)} dan {y_eq(m2, c2)}."
        first = f"Samakan: {lin(m1, c1)} = {lin(m2, c2)} ⇒ {n(m1 - m2)}x = {n(c2 - c1)} ⇒ x = {n(x0)}."
    else:
        a1, b1 = -m1, 1
        k = rng.choice([2, 3])
        prompt = (f"Tentukan titik potong garis {lin(k * a1, 0)} + {k}y = {n(k * c1)} dan "
                  f"{lin(-m2, 0)} + y = {n(c2)}.").replace("+ −", "− ")
        first = f"Bagi persamaan pertama dengan {k} lalu eliminasi y: ({n(m2)} − {paren(m1)})x = {n(c1)} − {paren(c2)} ⇒ x = {n(x0)}."
    correct = f"({n(x0)}, {n(y0)})"
    return {
        "prompt": prompt, "correct": correct,
        "distractors": [f"({n(y0)}, {n(x0)})", f"({n(-x0)}, {n(y0)})", f"({n(x0)}, {n(-y0)})", f"({n(x0 + 1)}, {n(y0 + m1)})"],
        "steps": [first, f"Substitusi ke salah satu garis: y = {n(m1)}·{paren(x0)} + {paren(c1)} = {n(y0)}.",
                  f"Titik potong: <b>{correct}</b>."],
        "graphs": [g2d("Dua garis berpotongan", [x0 - 10, x0 + 10], [y0 - 12, y0 + 12],
                       [param("m1", "Gradien garis 1", -5, 5, 0.25, m1, "m₁"), param("m2", "Gradien garis 2", -5, 5, 0.25, m2, "m₂")],
                       [fn(f"m1*(x-({x0}))+({y0})", "blue", "garis 1"), fn(f"m2*(x-({x0}))+({y0})", "orange", "garis 2"), pt(x0, y0)],
                       None, "Kedua garis selalu melewati titik potong soal. Jika m₁ = m₂, garis berimpit (tak hingga banyak titik potong).")],
        "explanation": "Titik potong = penyelesaian sistem dua persamaan linear (substitusi/eliminasi).",
    }


@register("lin.jarak", T, (3, 4))
def jarak(rng, tier):
    a, b, h = rng.choice([(3, 4, 5), (4, 3, 5), (5, 12, 13), (12, 5, 13), (6, 8, 10), (8, 15, 17)])
    a *= rng.choice([1, -1])
    x0, y0 = rng.randint(-4, 4), rng.randint(-4, 4)
    d = rng.randint(1, 4)
    c = -(a * x0 + b * y0) + d * h * rng.choice([1, -1])
    if tier == 3:
        prompt = f"Hitung jarak titik ({n(x0)}, {n(y0)}) ke garis {lin(a, 0)} + {b}y {'+' if c >= 0 else MINUS} {abs(c)} = 0."
        val = Fr(abs(a * x0 + b * y0 + c), h)
        steps = ["Rumus jarak titik (x₀, y₀) ke garis ax + by + c = 0: d = |ax₀ + by₀ + c| / √(a² + b²).",
                 f"|{n(a)}·{paren(x0)} + {b}·{paren(y0)} + {paren(c)}| = {abs(a * x0 + b * y0 + c)}; √({a * a} + {b * b}) = {h}.",
                 f"d = <b>{n(val)}</b>."]
    else:
        c2 = c + h * rng.randint(1, 3) * rng.choice([1, -1])
        prompt = (f"Hitung jarak antara dua garis sejajar {lin(a, 0)} + {b}y {'+' if c >= 0 else MINUS} {abs(c)} = 0 dan "
                  f"{lin(a, 0)} + {b}y {'+' if c2 >= 0 else MINUS} {abs(c2)} = 0.")
        val = Fr(abs(c - c2), h)
        steps = ["Dua garis ax + by + c₁ = 0 dan ax + by + c₂ = 0 sejajar (gradien sama).",
                 "Jaraknya d = |c₁ − c₂| / √(a² + b²).", f"d = |{n(c)} − {paren(c2)}| / {h} = <b>{n(val)}</b>."]
    return {"prompt": prompt.replace("+ −", "− "), "correct": n(val),
            "distractors": [n(val * h), n(val + 1), n(Fr(val.numerator * h, h * h + 1)), n(val * 2)],
            "steps": steps,
            "graphs": [g2d("Jarak terpendek = ruas tegak lurus ke garis", [x0 - 10, x0 + 10], [y0 - 10, y0 + 10],
                           [param("px", "x titik", x0 - 8, x0 + 8, 0.5, x0, "x₀"), param("py", "y titik", y0 - 8, y0 + 8, 0.5, y0, "y₀")],
                           [fn(f"(-({a})*x-({c}))/{b}", "blue", "garis"), pt("px", "py"),
                            {"type": "segment", "x1": "px", "y1": "py",
                             "x2": f"px-({a})*({a}*px+{b}*py+({c}))/{h * h}", "y2": f"py-{b}*({a}*px+{b}*py+({c}))/{h * h}",
                             "color": "red", "dash": True}],
                           [readout("Jarak", f"abs({a}*px+{b}*py+({c}))/{h}", 4)],
                           "Geser titik: ruas merah selalu tegak lurus garis dan panjangnya = jarak.")],
            "explanation": "Jarak titik ke garis diukur sepanjang garis tegak lurus (terpendek)."}


@register("lin.aplikasi", T, (2, 3))
def aplikasi(rng, tier):
    if rng.random() < 0.5:
        v0 = rng.choice([120, 150, 200, 240]) * 1_000_000
        years = rng.choice([8, 10, 12])
        rate = v0 // years
        t = rng.randint(2, years - 1)
        val = v0 - rate * t
        prompt = (f"Mesin produksi (FT) dibeli seharga Rp{v0:,} dan nilainya menyusut <b>linear</b> menjadi Rp0 dalam {years} tahun. "
                  f"Berapa nilainya setelah {t} tahun?").replace(",", ".")
        fmt = lambda v: f"Rp{v:,}".replace(",", ".")
        correct = fmt(val)
        wrong = [fmt(rate * t), fmt(v0 - rate * (t + 1)), fmt(v0 // t), fmt(val + rate // 2)]
        steps = [f"Model linear: V(t) = V₀ − r·t dengan r = {fmt(v0)}/{years} = {fmt(rate)} per tahun.",
                 f"V({t}) = {fmt(v0)} − {t}·{fmt(rate)} = <b>{correct}</b>."]
        graph = g2d("Penyusutan linear V(t)", [0, years + 2], [0, v0 / 1e6 * 1.2],
                    [param("tt", "Waktu t (tahun)", 0, years, 0.5, t, "t")],
                    [fn(f"{v0 / 1e6}-{rate / 1e6}*x", "blue", "V(t) dalam juta Rp", **{"to": years}), pt("tt", f"{v0 / 1e6}-{rate / 1e6}*tt")],
                    [readout("V(t) (juta Rp)", f"{v0 / 1e6}-{rate / 1e6}*tt", 2)],
                    "Gradien garis = −laju penyusutan per tahun.")
    else:
        c0 = rng.choice([5, 8, 10])
        r = rng.choice([2, 3, 4])
        target = c0 + r * rng.randint(5, 15)
        prompt = (f"Waktu eksekusi program (Fasilkom) adalah T(n) = {c0} + {r}n milidetik untuk input berukuran n. "
                  f"Untuk n berapa T(n) = {target} ms?")
        val = Fr(target - c0, r)
        correct = f"n = {n(val)}"
        wrong = [f"n = {n(Fr(target, r))}", f"n = {n(Fr(target + c0, r))}", f"n = {n(target - c0)}", f"n = {n(val + 1)}"]
        steps = [f"{c0} + {r}n = {target} ⇒ {r}n = {target - c0}.", f"n = <b>{n(val)}</b>."]
        graph = g2d("Waktu eksekusi linear T(n)", [0, float(val) * 2], [0, target * 2],
                    [param("T", "Target waktu (ms)", c0, target * 2, 1, target, "T")],
                    [fn(f"{c0}+{r}*x", "blue", "T(n)"), {"type": "hline", "y": "T", "color": "red", "dash": True}, pt(f"(T-{c0})/{r}", "T")],
                    [readout("n", f"(T-{c0})/{r}", 3)], "Algoritma linear O(n): menggandakan n kira-kira menggandakan waktu.")
    return {"prompt": prompt, "correct": correct, "distractors": wrong, "steps": steps, "graphs": [graph],
            "explanation": "Model linear: besaran berubah dengan laju tetap (gradien)."}


@register("lin.luas_segitiga", T, (4, 5))
def luas_segitiga(rng, tier):
    a, b = nz(rng, -6, 6), nz(rng, -6, 6)
    c = a * b * rng.choice([1, 2, -1, -2])
    area = Fr(c * c, 2 * abs(a * b))
    return {
        "prompt": f"Garis {lin(a, 0)} {'+' if b > 0 else MINUS} {abs(b)}y = {n(c)} memotong sumbu-x dan sumbu-y. "
                  "Berapa luas segitiga yang dibentuk garis itu dengan kedua sumbu koordinat?",
        "correct": n(area), "distractors": [n(area * 2), n(Fr(abs(c), 2)), n(Fr(c * c, abs(a * b))), n(area + 1)],
        "steps": [f"Titik potong sumbu-x (y = 0): x = {n(c)}/{paren(a)} = {n(Fr(c, a))}.",
                  f"Titik potong sumbu-y (x = 0): y = {n(c)}/{paren(b)} = {n(Fr(c, b))}.",
                  f"Luas = ½·|{n(Fr(c, a))}|·|{n(Fr(c, b))}| = c²/(2|ab|) = <b>{n(area)}</b>."],
        "graphs": [g2d("Segitiga oleh garis dan sumbu", [-14, 14], [-14, 14],
                       [param("cc", "Konstanta c", -30, 30, 1, c, "c")],
                       [{"type": "fill", "upper": f"(cc-({a})*x)/({b})", "lower": "0", "from": f"min(0,cc/{a})", "to": f"max(0,cc/{a})",
                         "color": "amber"},
                        fn(f"(cc-({a})*x)/({b})", "blue", "garis")],
                       [readout("Luas = c²/(2|ab|)", f"cc*cc/(2*abs({a * b}))", 3)],
                       "Gandakan c: luas menjadi 4 kali (bergantung pada c²).")],
        "explanation": "Bentuk intersep x/p + y/q = 1 memberi titik potong (p, 0) dan (0, q).",
    }


@register("lin.titik_kisi", T, (4, 5))
def titik_kisi(rng, tier):
    while True:
        x1, y1 = rng.randint(-10, 5), rng.randint(-10, 5)
        dx, dy = rng.randint(2, 30), rng.randint(2, 30)
        g = gcd(dx, dy)
        if g > 1:
            break
    x2, y2 = x1 + dx, y1 + dy
    cnt = g + 1
    return {
        "prompt": f"Berapa banyak titik dengan koordinat <b>bulat</b> pada ruas garis dari ({n(x1)}, {n(y1)}) ke ({n(x2)}, {n(y2)}) "
                  "(termasuk kedua ujungnya)?",
        "correct": str(cnt), "distractors": [str(g), str(cnt + 1), str(min(dx, dy) + 1), str(max(dx, dy) + 1)],
        "steps": [f"Selisih koordinat: Δx = {dx}, Δy = {dy}.",
                  f"Langkah terkecil yang tetap bulat: (Δx/d, Δy/d) dengan d = FPB({dx}, {dy}) = {g}.",
                  f"Ruas terbagi menjadi {g} langkah sama ⇒ {g} + 1 = <b>{cnt}</b> titik kisi."],
        "explanation": "Banyak titik kisi pada ruas dari (x₁,y₁) ke (x₂,y₂) = FPB(|Δx|, |Δy|) + 1.",
    }
