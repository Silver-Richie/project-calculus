"""
Sub-level: Aplikasi Integral (Level Utama 3 — Kalkulus Menengah).
Rujukan: Stewart §6.1–6.5, §8.1–8.3, §8.5; Whitman Bab 9; Strang (MIT) Bab 8.
"""

from fractions import Fraction as Fr
import math

from .. import register
from ..fmt import MINUS, frac_terms, lin, n, over, paren, sup, terms, times
from ..graphs import fn, g2d, param, readout
from ..precalc.common import distinct, nz
from ..dasar.aplikasi import per_pi, pi_txt

LS, VL, PJ, FS = "km-apl-luas", "km-apl-volume", "km-apl-panjang", "km-apl-fisika"


def region(title, upper, lower, a, b, caption, xr=None, yr=None, params=None, reads=None):
    return g2d(title, xr or [a - 1, b + 1], yr or [-3, 10], params or [],
               [{"type": "fill", "upper": upper, "lower": lower, "from": a, "to": b, "color": "amber"},
                fn(upper, "blue", "atas"), fn(lower, "green", "bawah")], reads, caption)


def solid_graph(title, expr, a, b, caption):
    """Penampang benda putar: kurva dan cerminannya (cakram berjari-jari f(x))."""
    return g2d(title, [a - 0.5, b + 0.5], None or [-4, 4], [param("X", "posisi cakram x", a, b, 0.01, (a + b) / 2, "x")],
               [{"type": "fill", "upper": expr, "lower": f"-({expr})", "from": a, "to": b, "color": "amber"},
                fn(expr, "blue", "f(x)"), fn(f"-({expr})", "blue", dash=True),
                {"type": "segment", "x1": "X", "y1": expr.replace("x", "X"), "x2": "X", "y2": f"-({expr.replace('x', 'X')})", "color": "red", "width": 3}],
               [readout("Jari-jari cakram f(x)", expr.replace("x", "X"), 4), readout("Luas cakram πf(x)²", f"pi*({expr.replace('x', 'X')})**2", 4)], caption)


def kx(k):
    return "x" if k == 1 else f"{k}x"


def xpow(k):
    return "x" if k == 1 else f"x{sup(k)}"


def _inv(c, e):
    """c/xᵉ sebagai teks: 1/(2x), 2/x², 1/(4x³)."""
    c = Fr(c)
    xe = xpow(e)
    return f"{c.numerator}/{xe}" if c.denominator == 1 else f"{c.numerator}/({c.denominator}{xe})"


def coef(c):
    """Koefisien di depan simbol: 1 → '', 3 → '3', 2/3 → '(2/3)'."""
    c = Fr(c)
    return "" if c == 1 else n(c) if c.denominator == 1 else f"({n(c)})"


# ════════════════════════ Topik 1: Luas lanjutan ═══════════════════════════
@register("al.luas_sin", LS, (1, 2))
def luas_sin(rng, tier):
    A, b = rng.randint(1, 5), rng.randint(1, 4 if tier == 2 else 3)
    f = f"{A if A > 1 else ''}sin({kx(b)})"
    if tier == 1:
        k = rng.randint(1, 4)
        val = Fr(2 * A * k, b)
        return {"prompt": f"Hitung luas total daerah antara y = {f} dan sumbu-x pada [0, {times(Fr(k, b), 'π')}].", "correct": n(val),
                "distractors": ["0", n(Fr(A * k, b)), n(val * 2), n(Fr(2 * A, b)) if k > 1 else n(val + 1)],
                "steps": [f"Satu ‘bukit’ {f} selebar π/{b} (dari nol ke nol berikutnya) memiliki luas ∫ |{f}| dx = {A}·2/{b} = {n(Fr(2 * A, b))}.".replace("π/1 ", "π "),
                          f"Interval [0, {times(Fr(k, b), 'π')}] memuat {k} bukit ⇒ luas = <b>{n(val)}</b>.",
                          "Perhatikan: integral bertanda bisa 0 (bukit di bawah sumbu bernilai negatif), tetapi luas selalu positif."],
                "graphs": [region(f"|{f}| pada [0, kπ/{b}]", f"abs({A}*sin({b}*x))", "0", 0, round(k * math.pi / b, 3), "Luas = jumlah semua ‘bukit’.", yr=(-A - 0.5, A + 0.5))],
                "explanation": "Luas = ∫|f|, bukan ∫f."}
    g = f"{A if A > 1 else ''}cos({kx(b)})"
    kind = rng.choice(["lensa", "awal", "simetri"])
    if kind == "lensa":
        lo, hi, val = times(Fr(1, 4 * b), "π"), times(Fr(5, 4 * b), "π"), [(Fr(2 * A, b), "√2")]
        work = f"Pada interval itu {f} ≥ {g}; ∫ ({f} − {g}) dx = ({A}/{b})[−cos u − sin u] dari π/4 ke 5π/4 = ({A}/{b})·2√2."
        upper, lower, a0, b0 = f"{A}*sin({b}*x)", f"{A}*cos({b}*x)", math.pi / (4 * b), 5 * math.pi / (4 * b)
    elif kind == "awal":
        lo, hi, val = "0", times(Fr(1, 4 * b), "π"), [(Fr(A, b), "√2"), (Fr(-A, b), "")]
        work = f"Pada [0, π/{4 * b}] {g} ≥ {f}; ∫ ({g} − {f}) dx = ({A}/{b})[sin u + cos u] dari 0 ke π/4 = ({A}/{b})(√2 − 1).".replace("π/4 ", "π/4 ")
        upper, lower, a0, b0 = f"{A}*cos({b}*x)", f"{A}*sin({b}*x)", 0, math.pi / (4 * b)
    else:
        lo, hi, val = "0", times(Fr(1, b), "π"), [(Fr(4 * A, b), "")]
        g = f"{MINUS}{A if A > 1 else ''}sin({kx(b)})"
        work = f"Kurva {g} adalah cerminan {f}; luas = 2∫₀^{{π/{b}}} {f} dx = 2·{n(Fr(2 * A, b))}."
        upper, lower, a0, b0 = f"{A}*sin({b}*x)", f"-{A}*sin({b}*x)", 0, math.pi / b
    correct = over([p for p in val if p[1]], sum((p[0] for p in val if not p[1]), Fr(0)))
    alt = lambda pairs: over([p for p in pairs if p[1]], sum((p[0] for p in pairs if not p[1]), Fr(0)))
    wrong = [alt([(c * 2, s) for c, s in val]), alt([(c / 2, s) for c, s in val]), alt([(c, s) for c, s in val if s]) if len(val) > 1 else alt([(val[0][0], "√2" if not val[0][1] else "")]), "0"]
    return {"prompt": f"Hitung luas daerah yang dibatasi y = {f} dan y = {g} pada [{lo}, {hi}].", "correct": correct, "distractors": wrong,
            "steps": ["Cari kurva yang di atas pada interval itu, lalu integralkan (atas − bawah).", work, f"<b>{correct}</b>."],
            "graphs": [region("Daerah antara dua kurva trigonometri", upper, lower, round(a0, 3), round(b0, 3), "Arsir = (atas − bawah) di sepanjang interval.", yr=(-A - 0.5, A + 0.5))],
            "explanation": "Luas antara kurva = ∫ (atas − bawah)."}


@register("al.dua_parabola", LS, (1, 2, 3))
def dua_parabola(rng, tier):
    a, b, s = rng.randint(1, 3), rng.randint(1, 3), rng.randint(1, 3)
    d = 0 if tier == 1 else rng.randint(-2, 2)
    U = (a + b) * s * s + d
    val = Fr(4 * (a + b) * s ** 3, 3)
    low, up = terms([(a, "x²")], d), terms([(-b, "x²")], U)
    return {"prompt": f"Hitung luas daerah yang dibatasi y = {low} dan y = {up}.", "correct": n(val),
            "distractors": [n(val / 2), n(Fr(2 * (a + b) * s ** 3, 3)), n(val * 2), n((a + b) * s ** 3)],
            "steps": [f"Titik potong: {low} = {up} ⇒ {a + b}x² = {(a + b) * s * s} ⇒ x = ±{s}.",
                      f"Atas − bawah = {terms([(-(a + b), 'x²')], (a + b) * s * s)} (konstanta {n(d)} saling menghapus)." if d else f"Atas − bawah = {terms([(-(a + b), 'x²')], (a + b) * s * s)}.",
                      f"Luas = 2∫₀^{s} ({terms([(-(a + b), 'x²')], (a + b) * s * s)}) dx = 2({(a + b) * s ** 3} − {n(Fr((a + b) * s ** 3, 3))}) = <b>{n(val)}</b>."],
            "graphs": [region("Daerah lensa antara dua parabola", f"{U}-{b}*x*x", f"{a}*x*x+({d})", -s, s, "Simetris terhadap sumbu-y: hitung separuh lalu kalikan 2.",
                              yr=(min(d, 0) - 1, U + 2))],
            "explanation": "Cari titik potong dulu, lalu integralkan selisih atas − bawah."}


@register("al.luas_y", LS, (2, 3, 4))
def luas_y(rng, tier):
    p, q = sorted(distinct(rng, -3, 4, 2))
    m, c = p + q, -p * q
    val = Fr((q - p) ** 3, 6)
    return {"prompt": f"Hitung luas daerah yang dibatasi x = y² dan x = {lin(m, c, 'y')}.", "correct": n(val),
            "distractors": [n(val * 2), n(Fr((q - p) ** 2, 2)), n(val + 1), n(Fr((q - p) ** 3, 3))],
            "steps": [f"Integralkan terhadap y (kurva berupa fungsi y): y² = {lin(m, c, 'y')} ⇒ y = {n(p)}, {n(q)}.",
                      f"Kanan − kiri: ({lin(m, c, 'y')}) − y²; Luas = ∫<sub>{n(p)}</sub><sup>{n(q)}</sup> [{lin(m, c, 'y')} − y²] dy.", f"= ({q} − {paren(p)})³/6 = <b>{n(val)}</b>."],
            "explanation": "Jika batas kiri/kanan lebih mudah sebagai x = g(y), integralkan terhadap y."}


@register("al.kubik_garis", LS, (3, 4, 5))
def kubik_garis(rng, tier):
    a, m, c = rng.randint(1, 3), rng.randint(1, 3), rng.randint(-3, 3)
    val = Fr(a * m ** 4, 2)
    cub, line = terms([(a, "x³"), (c, "x")]), terms([(a * m * m + c, "x")])
    return {"prompt": f"Hitung luas total daerah yang dibatasi y = {cub} dan y = {line}.", "correct": n(val),
            "distractors": ["0", n(val / 2), n(val * 2), n(Fr(a * m ** 4, 4))],
            "steps": [f"Titik potong: {cub} = {line} ⇒ {a if a > 1 else ''}x³ = {a * m * m}x ⇒ x = 0, ±{m}.",
                      "Selisih kedua kurva adalah fungsi ganjil, jadi integral bertanda di [−m, m] = 0: hitung satu bagian lalu ×2.",
                      f"2∫₀^{m} ({a * m * m}x − {a if a > 1 else ''}x³) dx = 2({n(Fr(a * m ** 4, 2))} − {n(Fr(a * m ** 4, 4))}) = <b>{n(val)}</b>."],
            "graphs": [region("Dua daerah antara kubik dan garis", f"{a * m * m + c}*x", f"{a}*x**3+({c})*x", 0, m, "Bagian kiri adalah cerminan titik bagian kanan.",
                              xr=[-m - 1, m + 1], yr=(-abs(a * m ** 3 + c * m) - 2, abs(a * m ** 3 + c * m) + 2))],
            "explanation": "Pecah daerah di setiap titik potong; jangan sampai luas saling menghapus."}


@register("al.luas_eksp", LS, (4, 5))
def luas_eksp(rng, tier):
    A, k = rng.randint(1, 4), rng.randint(2, 7)
    Ae = (lambda s: f"{A}{s}" if A > 1 else s)
    kind = rng.choice(["cosh", "dua", "datar"])
    if kind == "cosh":
        val = A * (Fr(k) + Fr(1, k) - 2)
        prompt = f"Hitung luas daerah yang dibatasi y = {Ae('eˣ')}, y = {Ae('e⁻ˣ')}, dan garis x = ln {k}."
        steps = ["Kedua kurva berpotongan di x = 0; untuk x &gt; 0, eˣ di atas.", f"∫₀^{{ln {k}}} {A if A > 1 else ''}(eˣ − e⁻ˣ) dx = {A if A > 1 else ''}[eˣ + e⁻ˣ]₀^{{ln {k}}} = {A if A > 1 else ''}(({k} + 1/{k}) − 2)."]
        correct, wrong = n(val), [n(A * (Fr(k) - Fr(1, k))), n(A * (k - 1)), n(val + 2 * A), n(val * 2)]
        g = region("Antara eˣ dan e⁻ˣ", f"{A}*exp(x)", f"{A}*exp(-x)", 0, round(math.log(k), 3), "e^(ln k) = k, e^(−ln k) = 1/k.", yr=(0, A * k + 1))
    elif kind == "dua":
        val = Fr(A * (k - 1) ** 2, 2)
        prompt = f"Hitung luas daerah yang dibatasi y = {Ae('e<sup>2x</sup>')}, y = {Ae('eˣ')}, dan garis x = ln {k}."
        steps = ["Kedua kurva berpotongan di x = 0; untuk x &gt; 0, e<sup>2x</sup> di atas.",
                 f"∫₀^{{ln {k}}} {A if A > 1 else ''}(e<sup>2x</sup> − eˣ) dx = {A if A > 1 else ''}[e<sup>2x</sup>/2 − eˣ]₀^{{ln {k}}} = {A if A > 1 else ''}(({k * k} − 1)/2 − ({k} − 1))."]
        correct, wrong = n(val), [n(Fr(A * (k * k - 1), 2)), n(A * (k - 1)), n(val * 2), n(Fr(A * (k * k - 1), 2) + A * (k - 1))]
        g = region("Antara e^(2x) dan eˣ", f"{A}*exp(2*x)", f"{A}*exp(x)", 0, round(math.log(k), 3), "e^(2 ln k) = k².", yr=(0, A * k * k + 1))
    else:
        correct = f"{A * k} ln {k} − {A * (k - 1)}"
        prompt = f"Hitung luas daerah yang dibatasi y = {Ae('eˣ')}, garis y = {A * k}, dan sumbu-y."
        steps = [f"Titik potong {Ae('eˣ')} = {A * k} ⇒ x = ln {k}; garis di atas kurva pada [0, ln {k}].",
                 f"∫₀^{{ln {k}}} ({A * k} − {Ae('eˣ')}) dx = {A * k} ln {k} − {A if A > 1 else ''}({k} − 1)."]
        wrong = [f"{A * k} ln {k} + {A * (k - 1)}", f"{A * k} ln {k} − {A * k}", f"{A * (k - 1)} − ln {k}", f"{A * k} ln {k}"]
        g = region("Antara garis datar dan eˣ", f"{A * k}+0*x", f"{A}*exp(x)", 0, round(math.log(k), 3), "Batas kanan: titik potong x = ln k.", yr=(0, A * k + 1))
    return {"prompt": prompt, "correct": correct, "distractors": wrong, "steps": steps + [f"= <b>{correct}</b>."], "graphs": [g],
            "explanation": "e^(ln k) = k: batas berbentuk ln k membuat hasil bersih."}


# ════════════════════════ Topik 2: Volume benda putar ══════════════════════
@register("vol.cakram", VL, (1, 2, 3))
def cakram(rng, tier):
    a, c = rng.randint(1, 6 if tier == 1 else 4), rng.randint(1, 3)
    lo = 0
    if tier == 1:
        kind = rng.choice(["akar", "silinder"])
        if kind == "akar":
            val, f, js, work = Fr(c * c * a * a, 2), f"{c if c > 1 else ''}√x", f"{c}*sqrt(x)", f"π∫₀^{a} {c * c if c > 1 else ''}x dx = π·{c * c}·{a * a}/2"
        else:
            val, f, js, work = Fr(c * c * a), str(c), f"{c}+0*x", f"π∫₀^{a} {c * c} dx = π·{c * c}·{a} (volume tabung πr²h)"
    elif tier == 2:
        kind = rng.choice(["x2", "x32"])
        if kind == "x2":
            val, f, js, work = Fr(c * c * a ** 5, 5), f"{c if c > 1 else ''}x²", f"{c}*x*x", f"π∫₀^{a} {c * c if c > 1 else ''}x⁴ dx = π·{c * c}·{a ** 5}/5"
        else:
            val, f, js, work = Fr(c * c * a ** 4, 4), f"{c if c > 1 else ''}x<sup>3/2</sup>", f"{c}*pow(x,1.5)", f"π∫₀^{a} {c * c if c > 1 else ''}x³ dx = π·{c * c}·{a ** 4}/4"
    else:
        kind = rng.choice(["kerucut", "bola", "hiperbola"])
        m = rng.randint(1, 4)
        if kind == "kerucut":
            val, f, js, work = Fr(m * m * a ** 3, 3), f"{m if m > 1 else ''}x", f"{m}*x", f"π∫₀^{a} {m * m if m > 1 else ''}x² dx = π·{m * m * a ** 3}/3 (volume kerucut ⅓πr²h)"
        elif kind == "bola":
            r = rng.randint(1, 6)
            val, f, js, lo, a = Fr(4 * r ** 3, 3), f"√({r * r} − x²)", f"sqrt(max(0,{r * r}-x*x))", -r, r
            work = f"π∫₋{r}^{r} ({r * r} − x²) dx = π(2·{r ** 3} − 2·{r ** 3}/3) (volume bola 4πr³/3)"
        else:
            a = rng.randint(2, 5)
            val, f, js, lo = Fr(c * c * (a - 1), a), f"{c}/x" if c > 1 else "1/x", f"{c}/x", 1
            work = f"π∫₁^{a} {c * c}/x² dx = π·{c * c}(1 − 1/{a})"
    rng_txt = f"{n(lo)} ≤ x ≤ {a}"
    return {"prompt": f"Daerah di bawah y = {f}, {rng_txt}, diputar mengelilingi sumbu-x. Hitung volumenya.", "correct": times(val, "π"),
            "distractors": [times(val * 2, "π"), n(val), times(val * Fr(3, 2), "π"), times(val / 2, "π")],
            "steps": ["Metode cakram: V = π∫ₐᵇ [f(x)]² dx (setiap irisan berbentuk cakram berjari-jari f(x)).", f"{work}.", f"V = <b>{times(val, 'π')}</b>."],
            "graphs": [solid_graph("Irisan cakram", js, lo, a, "Geser posisi: luas cakram πf(x)² dijumlahkan sepanjang sumbu-x.")],
            "explanation": "Volume = ∫ luas penampang dx."}


@register("vol.cincin", VL, (1, 2, 3, 4))
def cincin(rng, tier):
    a, b = rng.randint(1, 4), rng.randint(1, 3)
    h = rng.randint(0, 1) if tier <= 2 else rng.randint(0, 3)
    s = Fr(a, b)
    val = Fr(2 * a ** 5, 15 * b ** 3) + Fr(h * a ** 3, 3 * b * b)
    axis = "sumbu-x" if h == 0 else f"garis y = {MINUS}{h}"
    R, r = (f"{kx(a)}", f"{coef(b)}x²") if h == 0 else (f"{kx(a)} + {h}", f"{coef(b)}x² + {h}")
    return {"prompt": f"Daerah antara y = {kx(a)} dan y = {coef(b)}x² diputar mengelilingi {axis}. Hitung volumenya.", "correct": times(val, "π"),
            "distractors": [times(Fr(2 * a ** 5, 15 * b ** 3), "π") if h else times(val * 2, "π"), times(Fr(a ** 5, 15 * b ** 3) + Fr(h * a ** 3, 3 * b * b), "π"),
                            times(val + Fr(h * h * a, b), "π"), n(val), times(val / 2, "π")],
            "steps": [f"Titik potong: {kx(a)} = {coef(b)}x² ⇒ x = 0 dan x = {n(s)}. Penampang berupa cincin.",
                      f"Jarak ke sumbu putar: R = {R} (garis), r = {r} (parabola)." + (" Sumbu digeser ⇒ tambahkan jarak sumbu ke kedua jari-jari!" if h else ""),
                      f"V = π∫₀^{{{n(s)}}} (R² − r²) dx = <b>{times(val, 'π')}</b>."],
            "graphs": [region("Daerah yang diputar", f"{a}*x", f"{b}*x*x", 0, float(s), "Jari-jari luar = garis, jari-jari dalam = parabola" + (" (ditambah jarak ke sumbu)." if h else "."),
                              yr=(-h - 0.5, a * float(s) + 1))],
            "explanation": "Metode cincin (washer): V = π∫ (R² − r²) dx; R dan r diukur dari SUMBU PUTAR."}


@register("vol.sumbu_geser", VL, (3, 4, 5))
def sumbu_geser(rng, tier):
    a, b, c = rng.randint(1, 3), rng.randint(1, 2), rng.randint(1, 3)
    bx = f"{b if b > 1 else ''}"
    kind = rng.choice(["kulit_kiri", "kulit_kanan", "cincin_bawah", "cincin_atas"] if tier >= 4 else ["kulit_kiri", "cincin_bawah"])
    shape = rng.choice(["parabola_tutup", "x2"]) if kind.startswith("kulit") else "x2"
    if kind.startswith("kulit"):
        if shape == "parabola_tutup":
            f, js = f"{bx}x({a} − x)", f"{b}*x*({a}-x)"
            val = Fr(b * a ** 3 * (a + 2 * c), 6)
        else:
            f, js = f"{bx}x²", f"{b}*x*x"
            val = Fr(b * a ** 3 * (3 * a + 4 * c), 6) if kind == "kulit_kiri" else Fr(b * a ** 3 * (a + 4 * c), 6)
        axis = f"x = {MINUS}{c}" if kind == "kulit_kiri" else f"x = {a + c}"
        rad = f"x + {c}" if kind == "kulit_kiri" else f"{a + c} − x"
        work = [f"Sumbu putar tegak ({axis}) ⇒ metode kulit tabung: V = 2π∫ (jari-jari)(tinggi) dx.",
                f"Jari-jari kulit = jarak ke sumbu = {rad}; tinggi = {f}.", f"V = 2π∫₀^{a} ({rad})·{f} dx = <b>{times(val, 'π')}</b>."]
        wrong = [times(Fr(b * a ** 4, 6) if shape == "parabola_tutup" else Fr(b * a ** 4, 2), "π"), times(val * 2, "π"), times(val / 2, "π"), n(val)]
    else:
        f, js = f"{bx}x²", f"{b}*x*x"
        if kind == "cincin_bawah":
            H = c
            val = Fr(b * b * a ** 5, 5) + Fr(2 * H * b * a ** 3, 3)
            axis = f"y = {MINUS}{H}"
            work = [f"Sumbu mendatar y = −{H} di bawah daerah ⇒ metode cincin: R = {f} + {H}, r = {H}.",
                    f"V = π∫₀^{a} [({f} + {H})² − {H * H}] dx = π∫₀^{a} ({b * b if b > 1 else ''}x⁴ + {2 * H * b}x²) dx.", f"= <b>{times(val, 'π')}</b>."]
            wrong = [times(Fr(b * b * a ** 5, 5), "π"), times(Fr(b * b * a ** 5, 5) + Fr(H * H * a), "π"), times(val * 2, "π"), n(val)]
        else:
            H = b * a * a + rng.randint(0, 2)
            val = Fr(2 * H * b * a ** 3, 3) - Fr(b * b * a ** 5, 5)
            axis = f"y = {H}"
            work = [f"Sumbu mendatar y = {H} di atas daerah ⇒ metode cincin: R = {H} (ke sumbu-x), r = {H} − {f} (ke parabola).",
                    f"V = π∫₀^{a} [{H * H} − ({H} − {f})²] dx = π∫₀^{a} ({2 * H * b}x² − {b * b if b > 1 else ''}x⁴) dx.", f"= <b>{times(val, 'π')}</b>."]
            wrong = [times(Fr(b * b * a ** 5, 5), "π"), times(Fr(H * H * a) - Fr(b * b * a ** 5, 5), "π"), times(val * 2, "π"), n(val)]
    return {"prompt": f"Daerah di bawah y = {f}, 0 ≤ x ≤ {a}, di atas sumbu-x diputar mengelilingi garis {axis}. Hitung volumenya.", "correct": times(val, "π"),
            "distractors": wrong, "steps": work,
            "graphs": [g2d("Daerah dan sumbu putar (garis merah)", [-c - 1, a + c + 1], [-c - 1, b * a * a + 3], [],
                           [{"type": "fill", "upper": js, "lower": "0", "from": 0, "to": a, "color": "amber"}, fn(js, "blue", "f(x)"),
                            ({"type": "vline", "x": -c if kind == "kulit_kiri" else a + c, "color": "red", "dash": True} if kind.startswith("kulit") else
                             {"type": "hline", "y": -c if kind == "cincin_bawah" else H, "color": "red", "dash": True})], None,
                           "Jari-jari selalu diukur dari sumbu putar, bukan dari sumbu koordinat.")],
            "explanation": "Sumbu putar digeser: ukur ulang jari-jari (kulit: jarak horizontal ke sumbu; cincin: jarak vertikal ke sumbu)."}


@register("vol.kulit", VL, (3, 4, 5))
def kulit(rng, tier):
    a, b = rng.randint(1, 4), rng.randint(1, 3)
    if tier <= 4:
        if rng.random() < 0.5:
            val, f, js = Fr(b * a ** 4, 6), f"{b if b > 1 else ''}x({a} − x)", f"{b}*x*({a}-x)"
            work = f"2π∫₀^{a} x·{f} dx = 2π·{b}({a ** 4}/3 − {a ** 4}/4)"
            wrong = [times(val / 2, "π"), times(Fr(b * a ** 5, 30), "π"), times(val * 2, "π"), times(Fr(b * a ** 3, 6), "π")]
        else:
            m = rng.randint(1, 3)
            val, f, js = Fr(2 * b * a ** (m + 2), m + 2), f"{b if b > 1 else ''}{xpow(m)}", f"{b}*x**{m}"
            work = f"2π∫₀^{a} x·{f} dx = 2π·{b}·{a}{sup(m + 2)}/{m + 2}"
            wrong = [times(Fr(b * a ** (m + 1), m + 1), "π"), times(Fr(b * b * a ** (2 * m + 1), 2 * m + 1), "π"), times(val * 2, "π"), times(val / 2, "π")]
        return {"prompt": f"Daerah di bawah y = {f}, 0 ≤ x ≤ {a}, diputar mengelilingi sumbu-y. Hitung volumenya (metode kulit tabung).",
                "correct": times(val, "π"), "distractors": wrong,
                "steps": ["Kulit tabung: V = 2π∫ x·f(x) dx (keliling 2πx × tinggi f(x) × tebal dx).", f"{work}.", f"= <b>{times(val, 'π')}</b>."],
                "graphs": [region("Daerah dan satu kulit", js, "0", 0, a, "Diputar terhadap sumbu-y: setiap pita tegak menjadi kulit tabung.", yr=(-0.5, b * a ** 3 + 1))],
                "explanation": "Kulit tabung cocok bila diputar terhadap sumbu yang sejajar pita."}
    if rng.random() < 0.5:
        r = rng.randint(1, 3)
        R = rng.randint(r + 1, 8)
        val = 2 * R * r * r
        return {"prompt": f"Lingkaran (x − {R})² + y² = {r * r} diputar mengelilingi sumbu-y membentuk torus. Hitung volumenya.",
                "correct": f"{val}π²", "distractors": [f"{2 * R * r}π²", f"{val}π", f"{R * r * r}π²", f"{4 * R * r * r}π²"],
                "steps": [f"Teorema Pappus: V = (luas daerah)·(jarak lintasan pusat massa) = π·{r * r}·2π·{R}.", f"= <b>{val}π²</b>.",
                          "(Dapat diverifikasi dengan kulit tabung: 2π∫ x·2√(r² − (x − R)²) dx.)"],
                "explanation": "Teorema Pappus: V = A·2π·d."}
    c, a = rng.randint(1, 4), rng.randint(1, 3)
    ex = f"e{sup(-a * a)}"
    correct = f"{c if c > 1 else ''}π(1 − {ex})"
    return {"prompt": f"Daerah di bawah y = {c if c > 1 else ''}e<sup>−x²</sup>, 0 ≤ x ≤ {a}, diputar mengelilingi sumbu-y. Hitung volumenya.", "correct": correct,
            "distractors": [f"{2 * c}π(1 − {ex})", f"{c if c > 1 else ''}π{ex}", f"{c if c > 1 else ''}π(1 − e{sup(-a)})", f"{c if c > 1 else ''}π/2·(1 − {ex})"],
            "steps": ["Integral ∫ e<sup>−x²</sup> dx tidak elementer, tetapi kulit tabung memberi faktor x: V = 2π∫ x·f(x) dx.",
                      f"2π∫₀^{a} {c if c > 1 else ''}x e<sup>−x²</sup> dx; substitusi u = x²: = {c if c > 1 else ''}π[−e<sup>−u</sup>]₀^{{{a * a}}}.", f"= <b>{correct}</b>."],
            "explanation": "Pilihan metode bisa membuat integral mustahil menjadi mudah."}


@register("vol.penampang", VL, (4, 5))
def penampang(rng, tier):
    shapes = [("persegi", Fr(1), ""), ("segitiga siku-siku sama kaki dengan kaki di alas", Fr(1, 2), ""), ("segitiga siku-siku sama kaki dengan sisi miring di alas", Fr(1, 4), "")]
    if tier == 5:
        shapes += [("segitiga sama sisi", Fr(1, 4), "√3"), ("setengah lingkaran (diameter di alas)", Fr(1, 8), "π")]
    shape, kappa, sym = rng.choice(shapes)
    if rng.random() < 0.5:
        r = rng.randint(1, 6)
        base, I = f"cakram x² + y² ≤ {r * r}", Fr(16 * r ** 3, 3)
        work = [f"Penampang di posisi x memotong alas sepanjang s = 2√({r * r} − x²) ⇒ s² = 4({r * r} − x²).",
                f"∫₋{r}^{r} s² dx = 4(2·{r ** 3} − 2·{r ** 3}/3) = {n(I)}."]
        axis = "sumbu-x"
    else:
        h = rng.randint(1, 6)
        base, I = f"daerah antara parabola y = x² dan garis y = {h}", Fr(2 * h * h)
        work = [f"Penampang tegak lurus sumbu-y di ketinggian y memotong alas sepanjang s = 2√y ⇒ s² = 4y.",
                f"∫₀^{h} 4y dy = {n(I)}."]
        axis = "sumbu-y"
    val = kappa * I
    correct = times(val, sym) if sym else n(val)
    alt = (lambda v: times(v, sym) if sym else n(v))
    return {"prompt": f"Alas benda adalah {base}. Setiap penampang tegak lurus {axis} berbentuk {shape}. Hitung volumenya.",
            "correct": correct, "distractors": [alt(val * 2), alt(I), alt(val / 2), times(val, "π") if sym != "π" else n(val)],
            "steps": [f"Luas penampang {shape} bersisi s: A = {times(kappa, sym + 's²')}.", *work,
                      f"V = ∫ A = {times(kappa, sym) + '·' if kappa != 1 or sym else ''}{n(I)} = <b>{correct}</b>."],
            "explanation": "Metode irisan: V = ∫ A(x) dx untuk penampang apa pun."}


# ════════════════════════ Topik 3: Panjang busur & luas permukaan ══════════
@register("pb.garis", PJ, (1, 2))
def pb_garis(rng, tier):
    a, b, h = rng.choice([(3, 4, 5), (4, 3, 5), (5, 12, 13), (8, 15, 17)])
    dx = b * rng.randint(1, 3)
    m = Fr(a, b)
    val = Fr(h, b) * dx
    return {"prompt": f"Gunakan rumus panjang busur untuk y = {n(m)}x + 1 dari x = 0 sampai x = {dx}.", "correct": n(val),
            "distractors": [n(dx), n(m * dx), n(val + 1), n(Fr(a + b, b) * dx)],
            "steps": ["L = ∫ₐᵇ √(1 + (y′)²) dx.", f"y′ = {n(m)} ⇒ √(1 + {n(m * m)}) = {n(Fr(h, b))}.", f"L = {n(Fr(h, b))}·{dx} = <b>{n(val)}</b> (cocok dengan Pythagoras)."],
            "explanation": "Panjang busur menjumlahkan potongan √(dx² + dy²)."}


@register("pb.parametrik", PJ, (1, 2, 3))
def pb_parametrik(rng, tier):
    r = rng.randint(1, 6)
    k = rng.choice([1, 2, 3])
    val = Fr(r * k, 2) if tier < 3 else Fr(8 * r)
    if tier < 3:
        return {"prompt": f"Hitung panjang lintasan x = {r} cos t, y = {r} sin t untuk 0 ≤ t ≤ {k if k > 1 else ''}π/2.", "correct": pi_txt(val),
                "distractors": [pi_txt(val * 2), n(val), pi_txt(r * k), pi_txt(val / 2)],
                "steps": ["L = ∫ √((dx/dt)² + (dy/dt)²) dt.", f"√({r * r} sin²t + {r * r} cos²t) = {r}.", f"L = {r}·{k}π/2 = <b>{pi_txt(val)}</b> (busur lingkaran rθ)."],
                "explanation": "Kurva parametrik: L = ∫ √(x′² + y′²) dt."}
    return {"prompt": f"Hitung panjang satu lengkung sikloida x = {r}(t − sin t), y = {r}(1 − cos t), 0 ≤ t ≤ 2π.", "correct": n(val),
            "distractors": [pi_txt(2 * r), n(4 * r), pi_txt(8 * r), n(6 * r)],
            "steps": [f"x′² + y′² = {r * r}[(1 − cos t)² + sin²t] = {2 * r * r}(1 − cos t) = {4 * r * r} sin²(t/2).", f"L = ∫₀^{{2π}} {2 * r}|sin(t/2)| dt = {2 * r}·4.", f"= <b>{n(val)}</b>."],
            "graphs": [g2d("Sikloida: titik pada roda yang menggelinding", [-1, 2 * math.pi * r + 1], [-0.5, 2 * r + 1], [param("T", "t", 0, 6.28, 0.01, 3.14, "t")],
                           [{"type": "param", "t": [0, "2*pi"], "x": f"{r}*(t-sin(t))", "y": f"{r}*(1-cos(t))", "color": "blue"},
                            {"type": "point", "x": f"{r}*(T-sin(T))", "y": f"{r}*(1-cos(T))", "color": "red"}], None, "Panjang satu lengkung = 8r (Wren, 1658).")],
            "explanation": "Kurva parametrik: L = ∫ √(x′² + y′²) dt."}


@register("pb.kurva32", PJ, (2, 3, 4))
def kurva32(rng, tier):
    c = rng.choice([Fr(2, 3), Fr(4, 3), Fr(2), Fr(1, 3)])
    t = Fr(9, 4) * c * c
    p = 1 if tier == 2 and rng.random() < 0.5 else rng.randint(1, 3)
    q = rng.randint(p + 1, p + 4)
    x0, x1 = (p * p - 1) / t, (q * q - 1) / t
    val = Fr(2, 3) / t * (q ** 3 - p ** 3)
    return {"prompt": f"Hitung panjang busur y = {coef(c)}x<sup>3/2</sup> dari x = {n(x0)} sampai x = {n(x1)}.", "correct": n(val),
            "distractors": [n(Fr(2, 3) / t * q ** 3), n(val * 2), n(Fr(2, 3) * (q ** 3 - p ** 3)) if t != 1 else n(val + 1), n(x1 - x0)],
            "steps": [f"y′ = {coef(c * Fr(3, 2)) or '1'}·x<sup>1/2</sup> ⇒ 1 + y′² = 1 + {coef(t)}x.".replace("1·", ""),
                      f"L = ∫ √(1 + {coef(t)}x) dx = {coef(Fr(2, 3) / t)}[(1 + {coef(t)}x)<sup>3/2</sup>].",
                      f"Di batas: 1 + {coef(t)}x = {p * p} dan {q * q} (kuadrat sempurna!) ⇒ L = {n(Fr(2, 3) / t)}({q}³ − {p}³) = <b>{n(val)}</b>."],
            "graphs": [g2d("Kurva y = c·x^(3/2)", [-0.2, float(x1) + 1], [-0.5, float(c) * float(x1) ** 1.5 + 1], [],
                           [fn(f"{float(c)}*pow(x,1.5)", "blue", "y", **{"from": 0})], None, "Panjang busur selalu ≥ jarak lurus antara kedua ujung.")],
            "explanation": "Pilih batas yang membuat 1 + y′² kuadrat sempurna."}


@register("pb.cosh", PJ, (3, 4, 5))
def pb_cosh(rng, tier):
    if tier <= 4:
        a, k = rng.randint(1, 3), rng.randint(2, 7)
        sym = rng.random() < 0.4
        val = Fr(k * k - 1, 2 * k * a) * (2 if sym else 1)
        f = "cosh x" if a == 1 else f"(1/{a})cosh({a}x)"
        end = f"ln {k}" if a == 1 else f"(ln {k})/{a}"
        rng_txt = f"x = {MINUS}{end} sampai x = {end}" if sym else f"x = 0 sampai x = {end}"
        return {"prompt": f"Hitung panjang busur rantai y = {f} dari {rng_txt}.", "correct": n(val),
                "distractors": [n(Fr(k * k + 1, 2 * k * a) * (2 if sym else 1)), n(val * a) if a > 1 else n(k - 1), n(val * 2) if not sym else n(val / 2), "ln " + str(k)],
                "steps": [f"y′ = sinh({kx(a)}), 1 + sinh²u = cosh²u ⇒ √(1 + y′²) = cosh({kx(a)}).",
                          f"L = ∫ cosh({kx(a)}) dx = sinh({kx(a)})/{a}" .replace("/1", "") + f"; sinh(ln {k}) = ({k} − 1/{k})/2." + (" Kurva simetris ⇒ kalikan 2." if sym else ""),
                          f"= <b>{n(val)}</b>."],
                "explanation": "Kurva rantai (catenary, kabel listrik FT) memiliki panjang busur sinh."}
    c, b = rng.choice([Fr(1), Fr(2), Fr(3), Fr(1, 2)]), rng.randint(2, 6)
    const = Fr(b * b - 1) / (8 * c)
    f = frac_terms([(1 / (8 * c), "x²"), (-c, "ln x")])
    lnb = frac_terms([(c, f"ln {b}")])
    correct = f"{n(const)} + {lnb}"
    return {"prompt": f"Hitung panjang busur y = {f} dari x = 1 sampai x = {b}.", "correct": correct,
            "distractors": [f"{n(const)} − {lnb}", n(const), f"{n(const * 2)} + {lnb}", lnb],
            "steps": [f"y′ = {frac_terms([(1 / (4 * c), 'x')])} − {_inv(c, 1)}; hasil kali kedua suku = 1/4 ⇒ 1 + y′² = ({frac_terms([(1 / (4 * c), 'x')])} + {_inv(c, 1)})² (kuadrat sempurna).",
                      f"L = ∫₁^{b} ({frac_terms([(1 / (4 * c), 'x')])} + {_inv(c, 1)}) dx = [{frac_terms([(1 / (8 * c), 'x²'), (c, 'ln x')])}]₁^{b}.", f"= <b>{correct}</b>."],
            "explanation": "Soal panjang busur dirancang agar 1 + y′² menjadi kuadrat sempurna."}


@register("pb.kuadrat_sempurna", PJ, (3, 4, 5))
def kuadrat_sempurna(rng, tier):
    # y′ = αx^{p−1} − βx^{1−p} dengan αβ = 1/4 ⇒ 1 + y′² = (αx^{p−1} + βx^{1−p})²
    beta = rng.choice([Fr(1, 2), Fr(1, 4), Fr(1), Fr(2)])
    alpha = 1 / (4 * beta)
    p = rng.choice([3, 4] if tier < 5 else [3, 4, 5])
    b = rng.randint(2, 3 if p > 3 else 4)
    A, B = alpha / p, beta / (p - 2)
    F = lambda x: A * Fr(x) ** p - B * Fr(x) ** (2 - p)
    val = F(b) - F(1)
    f = f"{frac_terms([(A, xpow(p))])} + {_inv(B, p - 2)}"
    Fw = lambda x: A * Fr(x) ** p + B * Fr(x) ** (2 - p)
    return {"prompt": f"Hitung panjang busur y = {f} dari x = 1 sampai x = {b}.", "correct": n(val),
            "distractors": [n(Fw(b) - Fw(1)), n(A * (b ** p - 1)), n(val * 2), n(val + 1)],
            "steps": [f"y′ = {frac_terms([(alpha, xpow(p - 1))])} − {_inv(beta, p - 1)}; hasil kali kedua suku = {n(alpha * beta)} = 1/4.",
                      f"Maka 1 + y′² = ({frac_terms([(alpha, xpow(p - 1))])} + {_inv(beta, p - 1)})² — kuadrat sempurna, akarnya hilang!",
                      f"L = ∫₁^{b} ({frac_terms([(alpha, xpow(p - 1))])} + {_inv(beta, p - 1)}) dx = [{frac_terms([(A, xpow(p))])} − {_inv(B, p - 2)}]₁^{b} = <b>{n(val)}</b>."],
            "explanation": "Kunci soal panjang busur ‘bersih’: (u − v)² + 4uv = (u + v)² dengan uv = 1/4."}


@register("pb.permukaan", PJ, (4, 5))
def permukaan(rng, tier):
    if tier == 4:
        r = rng.randint(2, 6)
        lo, hi = sorted(distinct(rng, -r, r, 2))
        val = 2 * r * (hi - lo)
        return {"prompt": f"Busur y = √({r * r} − x²), {n(lo)} ≤ x ≤ {n(hi)}, diputar mengelilingi sumbu-x. Hitung luas permukaan (zona bola) yang terbentuk.",
                "correct": times(val, "π"), "distractors": [times(r * (hi - lo), "π"), times(4 * r * r, "π"), times(val * 2, "π"), times((hi - lo) ** 2, "π")],
                "steps": ["S = 2π∫ y√(1 + y′²) dx.", f"y√(1 + y′²) = √({r * r} − x²)·{r}/√({r * r} − x²) = {r} (konstan!).",
                          f"S = 2π∫<sub>{n(lo)}</sub><sup>{n(hi)}</sup> {r} dx = 2π·{r}·{hi - lo} = <b>{times(val, 'π')}</b> (teorema ‘kotak topi’ Archimedes)."],
                "explanation": "Luas permukaan benda putar: S = 2π∫ f(x)√(1 + f′²) dx."}
    if rng.random() < 0.6:
        pp, qq, hh = rng.choice([(3, 4, 5), (4, 3, 5), (5, 12, 13), (12, 5, 13), (8, 15, 17), (15, 8, 17), (7, 24, 25)])
        j = rng.randint(1, 4)
        A = qq * j
        val = pp * hh * j * j
        return {"prompt": f"Garis y = ({pp}/{qq})x, 0 ≤ x ≤ {A}, diputar mengelilingi sumbu-x. Hitung luas permukaan kerucut yang terbentuk.", "correct": times(val, "π"),
                "distractors": [times(pp * qq * j * j, "π"), times(val * 2, "π"), times(pp * pp * j * j, "π"), times(Fr(val, 2), "π")],
                "steps": [f"√(1 + ({pp}/{qq})²) = {hh}/{qq}.", f"S = 2π∫₀^{A} ({pp}x/{qq})·({hh}/{qq}) dx = 2π·{pp * hh}/{qq * qq}·{A * A}/2.",
                          f"= <b>{times(val, 'π')}</b> (cocok dengan πrℓ = π·{pp * j}·{hh * j})."],
                "explanation": "Rumus selimut kerucut πrℓ muncul dari integral luas permukaan."}
    d = rng.randint(1, 2)
    q = rng.randint(d + 1, d + 4)
    X = q * q - d * d
    val = Fr(8 * d * (q ** 3 - d ** 3), 3)
    return {"prompt": f"Kurva y = {2 * d}√x, 0 ≤ x ≤ {X}, diputar mengelilingi sumbu-x. Hitung luas permukaannya.", "correct": times(val, "π"),
            "distractors": [times(Fr(8 * d * q ** 3, 3), "π"), times(val * 2, "π"), times(Fr(4 * d * (q ** 3 - d ** 3), 3), "π"), n(val)],
            "steps": [f"y√(1 + y′²) = {2 * d}√x·√(1 + {d * d}/x) = {2 * d}√(x + {d * d}).",
                      f"S = 2π∫₀^{X} {2 * d}√(x + {d * d}) dx = {4 * d}π·(2/3)[(x + {d * d})<sup>3/2</sup>]₀^{X} = {n(Fr(8 * d, 3))}π({q}³ − {d}³).", f"= <b>{times(val, 'π')}</b>."],
            "explanation": "Paraboloid: x + d² membuat batas menjadi kuadrat sempurna."}


# ════════════════════════ Topik 4: Terapan fisika & peluang ════════════════
@register("fis.pegas", FS, (1, 2, 3))
def pegas(rng, tier):
    F0 = rng.choice([10, 20, 30, 40, 60])
    x0 = Fr(rng.choice([1, 2, 5]), 10)
    k = F0 / x0
    a, b = (Fr(0), x0 * 2) if tier == 1 else (x0, x0 * 3)
    W = k * (b * b - a * a) / 2
    return {"prompt": f"Gaya {F0} N meregangkan pegas sejauh {n(x0)} m (hukum Hooke). Berapa kerja untuk meregangkannya dari {n(a)} m menjadi {n(b)} m?",
            "correct": f"{n(W)} J", "distractors": [f"{n(F0 * (b - a))} J", f"{n(W * 2)} J", f"{n(k * (b - a))} J", f"{n(W / 2)} J"],
            "steps": [f"F = kx ⇒ k = {F0}/{n(x0)} = {n(k)} N/m.", f"W = ∫<sub>{n(a)}</sub><sup>{n(b)}</sup> {n(k)}x dx = {n(k)}·({n(b)}² − {n(a)}²)/2.", f"= <b>{n(W)} J</b>."],
            "graphs": [g2d("Kerja = luas di bawah grafik gaya", [0, float(b) * 1.2], [0, float(k * b) * 1.2], [],
                           [{"type": "fill", "upper": f"{float(k)}*x", "from": float(a), "to": float(b), "color": "amber"}, fn(f"{float(k)}*x", "blue", "F(x) = kx")],
                           None, "Gaya berubah terhadap posisi, sehingga kerja = ∫ F dx (bukan F × jarak).")],
            "explanation": "Kerja oleh gaya variabel: W = ∫ F(x) dx."}


@register("fis.gaya_variabel", FS, (2, 3))
def gaya_variabel(rng, tier):
    a, b = nz(rng, 1, 4), rng.randint(0, 9)
    d = rng.randint(1, 4)
    W = Fr(a * d ** 3, 3) + b * d
    return {"prompt": f"Benda dipindahkan dari x = 0 sampai x = {d} m oleh gaya F(x) = {a}x² + {b} N. Hitung kerjanya.", "correct": f"{n(W)} J",
            "distractors": [f"{n((a * d * d + b) * d)} J", f"{n(2 * a * d)} J", f"{n(W * 2)} J", f"{n(Fr(a * d ** 3, 3))} J"],
            "steps": [f"W = ∫₀^{d} ({a}x² + {b}) dx.", f"= {a}·{d}³/3 + {b}·{d} = <b>{n(W)} J</b>."], "explanation": "W = ∫ F dx."}


@register("fis.pusat_massa", FS, (3, 4, 5))
def pusat_massa(rng, tier):
    if tier == 3:
        L = rng.randint(1, 9)
        correct = f"x̄ = {n(Fr(2 * L, 3))} m"
        return {"prompt": f"Batang sepanjang {L} m memiliki rapat massa ρ(x) = kx (x dari ujung kiri). Di mana pusat massanya?", "correct": correct,
                "distractors": [f"x̄ = {n(Fr(L, 2))} m", f"x̄ = {n(Fr(L, 3))} m", f"x̄ = {n(Fr(3 * L, 4))} m", f"x̄ = {L} m"],
                "steps": ["x̄ = ∫ xρ dx / ∫ ρ dx.", f"∫₀^{L} kx² dx / ∫₀^{L} kx dx = (k{L}³/3)/(k{L}²/2).", f"<b>{correct}</b> (bergeser ke ujung yang lebih berat)."],
                "explanation": "Pusat massa = rata-rata posisi berbobot massa."}
    if tier == 4:
        m, a, c = rng.randint(1, 4), rng.randint(1, 3), rng.randint(1, 3)
        f = f"{c if c > 1 else ''}{xpow(m)}"
        if rng.random() < 0.5:
            val = Fr(a * (m + 1), m + 2)
            return {"prompt": f"Tentukan x̄ (sentroid) daerah di bawah y = {f} pada 0 ≤ x ≤ {a}.", "correct": n(val),
                    "distractors": [n(Fr(a, 2)), n(Fr(a * m, m + 1)), n(Fr(a * (m + 2), m + 3)), n(Fr(a, m + 2))],
                    "steps": ["x̄ = ∫ x·f dx / ∫ f dx (konstanta c saling menghapus).", f"∫₀^{a} x{sup(m + 1)} dx = {a}{sup(m + 2)}/{m + 2}; ∫₀^{a} {xpow(m)} dx = {a}{sup(m + 1)}/{m + 1}.",
                              f"x̄ = {a}·{m + 1}/{m + 2} = <b>{n(val)}</b>."],
                    "explanation": "Sentroid daerah: x̄ = (1/A)∫ x f(x) dx."}
        val = Fr(c * a ** m * (m + 1), 2 * (2 * m + 1))
        return {"prompt": f"Tentukan ȳ (sentroid) daerah di bawah y = {f} pada 0 ≤ x ≤ {a}.", "correct": n(val),
                "distractors": [n(Fr(c * a ** m, 2)), n(val * 2), n(Fr(c * a ** m * (m + 1), m + 2)), n(val / 2)],
                "steps": ["ȳ = (1/A)∫ ½[f(x)]² dx.", f"A = {n(Fr(c * a ** (m + 1), m + 1))}; ∫₀^{a} ½·{c * c if c > 1 else ''}x{sup(2 * m)} dx = {n(Fr(c * c * a ** (2 * m + 1), 2 * (2 * m + 1)))}.",
                          f"ȳ = <b>{n(val)}</b>."],
                "explanation": "Sentroid daerah: ȳ = (1/A)∫ ½f(x)² dx (rata-rata ketinggian pita)."}
    r = rng.randint(1, 6)
    correct = f"ȳ = {per_pi(Fr(4 * r, 3))}"
    return {"prompt": f"Tentukan ȳ (sentroid) daerah setengah lingkaran x² + y² ≤ {r * r}, y ≥ 0.", "correct": correct,
            "distractors": [f"ȳ = {n(Fr(r, 2))}", f"ȳ = {per_pi(Fr(2 * r, 3))}", f"ȳ = {n(Fr(4 * r, 3))}", f"ȳ = {n(Fr(r, 3))}"],
            "steps": ["ȳ = (1/A)∫ (1/2)[f(x)]² dx dengan A = πr²/2.", f"(1/2)∫₋{r}^{r} ({r * r} − x²) dx = {n(Fr(2 * r ** 3, 3))}.", f"ȳ = {n(Fr(2 * r ** 3, 3))}/(π{r * r}/2) = <b>{correct}</b>."],
            "explanation": "Sentroid setengah lingkaran 4r/(3π) — dipakai di statika (FT)."}


@register("fis.pompa", FS, (4, 5))
def pompa(rng, tier):
    R, H = rng.randint(1, 3), rng.randint(2, 6)
    if tier == 4:
        W = 4900 * R * R * H * H
        prompt = f"Tangki silinder tegak (jari-jari {R} m, tinggi {H} m) penuh air. Berapa kerja memompa seluruh air keluar lewat bibir atas? (ρg = 9800 N/m³)"
        steps = ["Irisan air pada kedalaman y (dari atas) setebal dy: berat 9800·πR²dy, diangkat sejauh y.", f"W = ∫₀^{H} 9800π·{R * R}·y dy = 9800π·{R * R}·{H * H}/2.", f"= <b>{W}π J</b>."]
    else:
        h = rng.randint(1, H - 1)
        W = 4900 * R * R * (H * H - h * h)
        prompt = (f"Tangki silinder tegak (jari-jari {R} m, tinggi {H} m) berisi air setinggi {H - h} m dari dasar. Berapa kerja memompa semua air keluar lewat bibir atas? "
                  "(ρg = 9800 N/m³)")
        steps = [f"Air mengisi kedalaman y dari {h} sampai {H} (diukur dari atas).", f"W = ∫<sub>{h}</sub><sup>{H}</sup> 9800π·{R * R}·y dy = 4900π·{R * R}·({H * H} − {h * h}).", f"= <b>{W}π J</b>."]
    return {"prompt": prompt, "correct": f"{W}π J", "distractors": [f"{W * 2}π J", f"{9800 * R * R * H}π J", f"{W // 2}π J", f"{W}J"], "steps": steps,
            "explanation": "Kerja memompa: jumlahkan (berat irisan) × (jarak angkat)."}


@register("fis.peluang", FS, (1, 2))
def peluang(rng, tier):
    L, m = rng.randint(1, 5), rng.randint(1, 4)
    k = Fr(m + 1, L ** (m + 1))
    f = f"k{xpow(m)}"
    if tier == 1:
        return {"prompt": f"f(x) = {f} untuk 0 ≤ x ≤ {L} (nol di luar) adalah fungsi kepadatan peluang. Tentukan k.", "correct": f"k = {n(k)}",
                "distractors": [f"k = {n(Fr(1, L ** m))}", f"k = {n(Fr(1, L ** (m + 1)))}", f"k = {n(k * 2)}", f"k = {n(Fr(m + 1, L))}"],
                "steps": ["Syarat kepadatan: ∫ f(x) dx = 1.", f"∫₀^{L} {f} dx = k·{L}{sup(m + 1)}/{m + 1} = 1 ⇒ <b>k = {n(k)}</b>."],
                "explanation": "Total peluang = luas di bawah kepadatan = 1 (FMIPA statistika)."}
    j = rng.randint(1, 3)
    a = Fr(j * L, 4)
    P = (a / L) ** (m + 1)
    kf = f"{n(k)}{xpow(m)}"
    return {"prompt": f"X berkepadatan f(x) = {kf} pada [0, {L}]. Hitung P(X ≤ {n(a)}).", "correct": n(P),
            "distractors": [n(Fr(j, 4)), n(1 - P), n(P * 2) if P * 2 < 1 else n(P / 2), n(k * a ** m)],
            "steps": [f"P(X ≤ {n(a)}) = ∫₀^{{{n(a)}}} {kf} dx = {n(k)}·({n(a)}){sup(m + 1)}/{m + 1}.", f"= ({n(a)}/{L}){sup(m + 1)} = <b>{n(P)}</b>."],
            "graphs": [g2d("Peluang = luas di bawah kepadatan", [-0.2, L + 0.2], [0, float(k * L ** m) * 1.2], [param("t", "batas t", 0, L, 0.01, float(a), "t")],
                           [{"type": "fill", "upper": f"{float(k)}*x**{m}", "from": 0, "to": "t", "color": "amber"}, fn(f"{float(k)}*x**{m}", "blue", "f(x)", **{"from": 0, "to": L})],
                           [readout("P(X ≤ t)", f"pow(t/{L},{m + 1})", 4)], "Geser t: peluang kumulatif naik dari 0 ke 1.")],
            "explanation": "P(a ≤ X ≤ b) = ∫ₐᵇ f(x) dx."}
