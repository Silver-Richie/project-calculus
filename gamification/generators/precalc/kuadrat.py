"""
Topik: Fungsi Kuadrat — puncak, akar, diskriminan, Vieta, optimasi, parameter.
Rujukan: Stewart Lampiran C & §1.2; Whitman §1.4 (shifts); Strang (MIT) §0.2.
"""

from fractions import Fraction as Fr

from .. import register
from ..fmt import MINUS, n, paren, poly
from ..graphs import fn, g2d, hline, param, pt, readout
from .common import distinct, nz

T = "pre-fungsi-kuadrat"


def para_graph(title, a, b, c, caption, extra=None, reads=None):
    """Parabola y = ax² + bx + c dengan slider a, b, c; puncak ditandai."""
    vx = "(-b/(2*a))"
    return g2d(title, [-10, 10], [-15, 15],
               [param("a", "a", -3, 3, 0.25, float(a), "a"), param("b", "b", -10, 10, 0.5, float(b), "b"),
                param("c", "c", -12, 12, 0.5, float(c), "c")],
               [fn("a*x*x+b*x+c", "blue", "y = ax² + bx + c"), pt(vx, f"a*{vx}**2+b*{vx}+c", label="puncak")] + (extra or []),
               [readout("x puncak = −b/(2a)", vx, 3), readout("y puncak", f"a*{vx}**2+b*{vx}+c", 3),
                readout("Diskriminan D = b² − 4ac", "b*b-4*a*c", 3)] + (reads or []), caption)


@register("quad.puncak", T, (1, 2))
def puncak(rng, tier):
    a = nz(rng, -3, 3) if tier == 2 else rng.choice([1, -1])
    h, k = rng.randint(-5, 5), rng.randint(-8, 8)
    b, c = -2 * a * h, a * h * h + k
    correct = f"({n(h)}, {n(k)})"
    return {
        "prompt": f"Tentukan titik puncak parabola y = {poly([a, b, c])}.",
        "correct": correct, "distractors": [f"({n(-h)}, {n(k)})", f"({n(h)}, {n(c)})", f"({n(k)}, {n(h)})", f"({n(-h)}, {n(-k)})"],
        "steps": [f"x puncak = −b/(2a) = −({n(b)})/(2·{paren(a)}) = {n(h)}.",
                  f"y puncak = f({n(h)}) = {n(a)}·{paren(h)}² + ({n(b)})·{paren(h)} + {paren(c)} = {n(k)}.",
                  f"Puncak = <b>{correct}</b>; parabola terbuka ke {'atas (minimum)' if a > 0 else 'bawah (maksimum)'} karena a {'&gt;' if a > 0 else '&lt;'} 0."],
        "graphs": [para_graph("Parabola dan titik puncaknya", a, b, c,
                              "Geser a: lebar & arah buka. Geser b: puncak bergerak menyusuri parabola lain. Geser c: naik-turun.")],
        "explanation": "Puncak (−b/2a, f(−b/2a)); bentuk puncak y = a(x − h)² + k.",
    }


@register("quad.akar", T, (1, 2))
def akar(rng, tier):
    r1, r2 = distinct(rng, -7, 7, 2)
    a = 1 if tier == 1 else rng.choice([2, 3, -1, -2])
    co = [a, -a * (r1 + r2), a * r1 * r2]
    lo, hi = sorted([r1, r2])
    correct = f"x = {n(lo)} atau x = {n(hi)}"
    return {
        "prompt": f"Tentukan akar-akar persamaan {poly(co)} = 0.",
        "correct": correct,
        "distractors": [f"x = {n(-hi)} atau x = {n(-lo)}", f"x = {n(lo)} atau x = {n(-hi)}", f"x = {n(r1 * r2)} atau x = {n(r1 + r2)}",
                        f"x = {n(lo - 1)} atau x = {n(hi + 1)}"],
        "steps": [(f"Bagi dengan {n(a)}: " if a != 1 else "") + f"{poly([1, -(r1 + r2), r1 * r2])} = 0.",
                  f"Cari dua bilangan yang jumlahnya {n(r1 + r2)} dan hasil kalinya {n(r1 * r2)}: {n(r1)} dan {n(r2)}.",
                  f"(x − {paren(r1)})(x − {paren(r2)}) = 0 ⇒ <b>{correct}</b>."],
        "graphs": [para_graph("Akar = titik potong dengan sumbu-x", co[0], co[1], co[2],
                              "Geser c ke atas sampai parabola tidak lagi memotong sumbu-x: akar real hilang (D < 0).",
                              [hline(0)], [readout("x₁", "(-b-sqrt(b*b-4*a*c))/(2*a)", 3), readout("x₂", "(-b+sqrt(b*b-4*a*c))/(2*a)", 3)])],
        "explanation": "ax² + bx + c = 0 ⇔ a(x − x₁)(x − x₂) = 0. Rumus abc: x = (−b ± √D)/(2a).",
    }


@register("quad.diskriminan", T, (2, 3))
def diskriminan(rng, tier):
    if tier == 2:
        a, b, c = nz(rng, -3, 3), rng.randint(-8, 8), rng.randint(-8, 8)
        D = b * b - 4 * a * c
        kind = "dua akar real berbeda" if D > 0 else "satu akar real (kembar)" if D == 0 else "tidak punya akar real"
        others = [k for k in ["dua akar real berbeda", "satu akar real (kembar)", "tidak punya akar real"] if k != kind]
        return {"prompt": f"Berapa banyak akar real persamaan {poly([a, b, c])} = 0?",
                "correct": kind, "distractors": others + ["tiga akar real"],
                "steps": [f"D = b² − 4ac = {paren(b)}² − 4·{paren(a)}·{paren(c)} = {D}.",
                          "D &gt; 0: dua akar real; D = 0: satu akar kembar; D &lt; 0: tidak ada akar real.",
                          f"Jadi persamaan <b>{kind}</b>."],
                "graphs": [para_graph("Diskriminan menentukan banyak titik potong", a, b, c, "Ubah c perlahan dan amati tanda D pada tabel.")],
                "explanation": "Diskriminan D = b² − 4ac."}
    # tier 3: cari k agar akar kembar: x² + kx + m = 0 dengan m = s² ⇒ k = ±2s
    s = rng.randint(1, 7)
    m = s * s
    correct = f"k = {MINUS}{2 * s} atau k = {2 * s}"
    return {"prompt": f"Tentukan nilai k agar persamaan x² + kx + {m} = 0 mempunyai akar kembar.",
            "correct": correct, "distractors": [f"k = {2 * s}", f"k = {MINUS}{s} atau k = {s}", f"k = {m}", f"k = {MINUS}{4 * s} atau k = {4 * s}"],
            "steps": ["Akar kembar ⇔ D = 0.", f"D = k² − 4·1·{m} = 0 ⇒ k² = {4 * m}.", f"<b>{correct}</b>."],
            "graphs": [g2d("y = x² + kx + m: kapan menyinggung sumbu-x?", [-10, 10], [-10, 20],
                           [param("k", "Parameter k", -15, 15, 0.25, 2 * s, "k")],
                           [fn(f"x*x+k*x+{m}", "blue", "y"), hline(0), pt("-k/2", f"{m}-k*k/4", label="puncak")],
                           [readout("D = k² − 4m", f"k*k-{4 * m}", 3)],
                           f"Tepat di k = ±{2 * s} puncak parabola menyentuh sumbu-x (akar kembar).")],
            "explanation": "Akar kembar ⇔ D = 0 ⇔ parabola menyinggung sumbu-x."}


@register("quad.vieta", T, (3, 4))
def vieta(rng, tier):
    a = rng.choice([1, 2, 3]) if tier == 4 else 1
    b, c = nz(rng, -9, 9), nz(rng, -9, 9)
    S, P = Fr(-b, a), Fr(c, a)
    what = rng.choice(["x₁² + x₂²", "1/x₁ + 1/x₂"] if tier == 3 else ["x₁² + x₂²", "x₁³ + x₂³", "(x₁ − x₂)²"])
    if what == "x₁² + x₂²":
        val, form = S * S - 2 * P, "(x₁ + x₂)² − 2x₁x₂"
    elif what == "1/x₁ + 1/x₂":
        val, form = S / P, "(x₁ + x₂)/(x₁x₂)"
    elif what == "x₁³ + x₂³":
        val, form = S ** 3 - 3 * S * P, "(x₁ + x₂)³ − 3x₁x₂(x₁ + x₂)"
    else:
        val, form = S * S - 4 * P, "(x₁ + x₂)² − 4x₁x₂"
    return {
        "prompt": f"x₁ dan x₂ adalah akar-akar {poly([a, b, c])} = 0. Hitung {what}.",
        "correct": n(val), "distractors": [n(S * S + 2 * P), n(S * S - P), n(-val), n(S + P)],
        "steps": [f"Vieta: x₁ + x₂ = −b/a = {n(S)}, x₁x₂ = c/a = {n(P)}.", f"{what} = {form}.",
                  f"Substitusi: <b>{n(val)}</b>. (Akar tidak perlu dihitung satu per satu, bahkan bila tidak real.)"],
        "explanation": "Rumus Vieta: x₁ + x₂ = −b/a, x₁x₂ = c/a.",
    }


@register("quad.optimasi", T, (3, 4))
def optimasi(rng, tier):
    if rng.random() < 0.5:
        L = rng.choice([40, 60, 80, 100, 120])
        x = L // 4
        if tier == 3:
            prompt = f"Pagar sepanjang {L} m dipakai untuk mengelilingi kebun persegi panjang. Berapa luas maksimum kebun?"
            val, steps = x * x, [f"Keliling 2(p + l) = {L} ⇒ l = {L // 2} − p.", f"Luas A(p) = p({L // 2} − p) = −p² + {L // 2}p (parabola terbuka ke bawah).",
                                 f"Puncak di p = {L // 4} ⇒ l = {L // 4}: persegi! A = <b>{x * x}</b> m²."]
            expr, xr = f"x*({L // 2}-x)", L // 2
        else:
            prompt = (f"Pagar {L} m dipakai untuk memagari lahan persegi panjang di tepi sungai (sisi sungai tidak dipagar). "
                      "Berapa luas maksimum lahan?")
            val = L * L // 8
            steps = [f"Misal dua sisi tegak = x, sisi sejajar sungai = {L} − 2x.", f"A(x) = x({L} − 2x) = −2x² + {L}x.",
                     f"Puncak x = {L}/4 = {n(Fr(L, 4))}: A = <b>{n(Fr(L * L, 8))}</b> m²."]
            expr, xr = f"x*({L}-2*x)", L // 2
        return {"prompt": prompt, "correct": f"{n(Fr(val))} m²",
                "distractors": [f"{n(Fr(L * L, 4))} m²", f"{n(Fr(L * L, 16))} m²", f"{n(Fr(L * L, 32))} m²", f"{n(Fr(val) + L)} m²"],
                "steps": steps,
                "graphs": [g2d("Luas sebagai fungsi kuadrat", [0, xr], [0, val * 1.3],
                               [param("p", "Lebar x", 0, xr, 0.5, xr / 4, "x")],
                               [fn(expr, "blue", "A(x)"), pt("p", expr.replace("x", "p"), label="A")],
                               [readout("Luas A(x)", expr.replace("x", "p"), 2)],
                               "Geser x dan cari posisi saat luas terbesar: tepat di puncak parabola.")],
                "explanation": "Optimasi kuadrat: maksimum/minimum ada di puncak x = −b/(2a)."}
    v0 = rng.choice([20, 30, 40, 50])
    g = 10
    tmax = Fr(v0, g)
    hmax = Fr(v0 * v0, 2 * g)
    return {"prompt": f"Bola dilempar vertikal dengan h(t) = {v0}t − 5t² (meter, g = 10 m/s²). Berapa tinggi maksimumnya?",
            "correct": f"{n(hmax)} m", "distractors": [f"{n(hmax * 2)} m", f"{n(tmax)} m", f"{n(Fr(v0 * v0, g))} m", f"{n(hmax / 2)} m"],
            "steps": [f"h(t) parabola terbuka ke bawah, puncak di t = −b/(2a) = −{v0}/(2·(−5)) = {n(tmax)} s.",
                      f"h({n(tmax)}) = {v0}·{n(tmax)} − 5·{n(tmax)}² = <b>{n(hmax)} m</b>."],
            "graphs": [g2d("Lintasan vertikal h(t) = v₀t − 5t²", [0, float(2 * tmax) + 1], [0, float(hmax) * 1.6],
                           [param("v", "Kecepatan awal v₀", 5, 60, 1, v0, "v₀")],
                           [fn("v*x-5*x*x", "blue", "h(t)"), pt("v/10", "v*v/20", label="puncak")],
                           [readout("t puncak = v₀/10", "v/10", 3), readout("h maks = v₀²/20", "v*v/20", 3)],
                           "Gandakan v₀: waktu ke puncak ganda, tinggi maksimum menjadi 4 kali.")],
            "explanation": "Optimasi kuadrat: maksimum/minimum ada di puncak x = −b/(2a)."}


@register("quad.selisih_akar", T, (4, 5))
def selisih_akar(rng, tier):
    d = rng.randint(1, 6)
    c = rng.randint(-10, 10)
    # akar x² − kx + c: selisih² = k² − 4c = d² ⇒ k² = d² + 4c (harus kuadrat sempurna)
    for _ in range(200):
        k2 = d * d + 4 * c
        k = int(round(k2 ** 0.5)) if k2 > 0 else -1
        if k2 > 0 and k * k == k2:
            break
        c = rng.randint(-10, 20)
        d = rng.randint(1, 8)
    else:
        d, c, k = 2, 3, 4
    correct = f"k = {MINUS}{k} atau k = {k}" if k else "k = 0"
    return {
        "prompt": f"Akar-akar x² − kx {'+' if c >= 0 else MINUS} {abs(c)} = 0 berselisih {d}. Tentukan semua nilai k.",
        "correct": correct, "distractors": [f"k = {k}", f"k = {MINUS}{d} atau k = {d}", f"k = {MINUS}{k + 1} atau k = {k + 1}",
                                            f"k = {MINUS}{k * 2} atau k = {k * 2}"],
        "steps": ["(x₁ − x₂)² = (x₁ + x₂)² − 4x₁x₂.", f"Vieta: x₁ + x₂ = k, x₁x₂ = {n(c)} ⇒ {d}² = k² − 4·{paren(c)}.",
                  f"k² = {d * d} + {4 * c} = {k * k} ⇒ <b>{correct}</b>."],
        "graphs": [g2d("y = x² − kx + c: jarak antara dua akar", [-12, 12], [-20, 15],
                       [param("k", "Parameter k", -12, 12, 0.25, k, "k")],
                       [fn(f"x*x-k*x+({c})", "blue", "y"), hline(0)],
                       [readout("Selisih akar √(k² − 4c)", f"sqrt(k*k-4*({c}))", 3)],
                       "Selisih akar hanya bergantung pada k²: k dan −k memberi selisih sama (parabola tercermin).")],
        "explanation": "|x₁ − x₂| = √D / |a|.",
    }


@register("quad.akar_lebih", T, (5,))
def akar_lebih(rng, tier):
    t = rng.randint(1, 4)
    # x² − 2mx + (m² − 1) = 0 ⇒ akar m ± 1; keduanya > t ⇔ m − 1 > t ⇔ m > t + 1
    correct = f"m &gt; {t + 1}"
    return {
        "prompt": f"Tentukan semua m agar kedua akar x² − 2mx + m² − 1 = 0 lebih besar dari {t}.",
        "correct": correct, "distractors": [f"m &gt; {t}", f"m &gt; {t - 1}", f"m &lt; {t + 1}", f"{t - 1} &lt; m &lt; {t + 1}"],
        "steps": ["D = 4m² − 4(m² − 1) = 4 &gt; 0, jadi selalu ada dua akar real.",
                  "Akar: x = (2m ± 2)/2 = m ± 1.",
                  f"Akar terkecil m − 1 harus &gt; {t} ⇒ <b>{correct}</b>."],
        "graphs": [g2d("Kedua akar m − 1 dan m + 1 bergeser bersama m", [-4, 12], [-3, 10],
                       [param("m", "Parameter m", -2, 10, 0.1, t + 1.5, "m")],
                       [fn("x*x-2*m*x+m*m-1", "blue", "y"), hline(0), {"type": "vline", "x": t, "color": "red", "dash": True},
                        pt("m-1", 0), pt("m+1", 0)],
                       [readout("Akar kecil m − 1", "m-1", 3)],
                       f"Garis merah x = {t}. Kedua titik akar harus di kanan garis merah.")],
        "explanation": "Jika akar bisa dihitung eksplisit, syarat letak akar menjadi pertidaksamaan sederhana.",
    }


@register("quad.bentuk_puncak", T, (2, 3))
def bentuk_puncak(rng, tier):
    h, k = rng.randint(-5, 5), rng.randint(-6, 6)
    px, py = h + rng.choice([1, 2, -1, -2]), None
    a = nz(rng, -3, 3)
    py = a * (px - h) ** 2 + k
    co = [a, -2 * a * h, a * h * h + k]
    correct = f"y = {poly(co)}"
    return {
        "prompt": f"Parabola berpuncak di ({n(h)}, {n(k)}) dan melalui titik ({n(px)}, {n(py)}). Persamaannya adalah …",
        "correct": correct,
        "distractors": [f"y = {poly([-a, 2 * a * h, -a * h * h + k])}", f"y = {poly([a, 2 * a * h, a * h * h + k])}",
                        f"y = {poly([a, -2 * a * h, a * h * h - k])}", f"y = {poly([2 * a, -4 * a * h, 2 * a * h * h + k])}",
                        f"y = {poly([a, -2 * a * h, a * h * h + k + 1])}", f"y = {poly([a, -2 * a * (h + 1), a * (h + 1) ** 2 + k])}"],
        "steps": [f"Bentuk puncak: y = a(x − {paren(h)})² + {paren(k)}.",
                  f"Substitusi ({n(px)}, {n(py)}): {n(py)} = a·{(px - h) ** 2} + {paren(k)} ⇒ a = {n(a)}.",
                  f"Jabarkan: <b>{correct}</b>."],
        "graphs": [g2d("y = a(x − h)² + k", [-10, 10], [-15, 15],
                       [param("aa", "a", -3, 3, 0.25, a, "a"), param("h", "h", -6, 6, 0.5, h, "h"), param("k", "k", -8, 8, 0.5, k, "k")],
                       [fn("aa*(x-h)**2+k", "blue", "y"), pt("h", "k", label="puncak"), pt(px, py, "orange", label="titik soal")],
                       None, "Hanya satu nilai a yang membuat parabola berpuncak (h, k) melewati titik oranye.")],
        "explanation": "Bentuk puncak y = a(x − h)² + k cocok bila puncak diketahui.",
    }
