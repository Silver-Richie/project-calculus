"""
Sub-level: Aplikasi Integral (Level Utama 3 — Kalkulus Menengah).
Rujukan: Stewart §6.1–6.5, §8.1–8.3, §8.5; Whitman Bab 9; Strang (MIT) Bab 8.
"""

from fractions import Fraction as Fr
import math

from .. import register
from ..fmt import MINUS, lin, n, paren, sup
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


# ════════════════════════ Topik 1: Luas lanjutan ═══════════════════════════
@register("al.luas_sin", LS, (1, 2))
def luas_sin(rng, tier):
    if tier == 1:
        k = rng.randint(1, 4)
        return {"prompt": f"Hitung luas total daerah antara y = sin x dan sumbu-x pada [0, {k if k > 1 else ''}π].", "correct": n(2 * k),
                "distractors": ["0", n(k), n(4 * k), "2" if k > 1 else "1"],
                "steps": ["Setiap setengah gelombang [mπ, (m + 1)π] memiliki luas ∫ |sin x| dx = 2.", f"Ada {k} setengah gelombang ⇒ <b>{2 * k}</b>.",
                          "Perhatikan: integral bertanda ∫₀^{kπ} sin x dx bisa 0, tetapi luas selalu positif."],
                "graphs": [region("|sin x| pada [0, kπ]", "abs(sin(x))", "0", 0, round(k * math.pi, 3), "Luas = jumlah semua ‘bukit’.", yr=(-1.5, 1.5))],
                "explanation": "Luas = ∫|f|, bukan ∫f."}
    return {"prompt": "Hitung luas daerah yang dibatasi y = sin x dan y = cos x pada [π/4, 5π/4].", "correct": "2√2",
            "distractors": ["√2", "2", "4", "0"],
            "steps": ["Di (π/4, 5π/4) sin x ≥ cos x.", "∫ (sin x − cos x) dx = [−cos x − sin x] = (√2/2 + √2/2) − (−√2/2 − √2/2).", "<b>2√2</b>."],
            "graphs": [region("Antara sin x dan cos x", "sin(x)", "cos(x)", 0.785, 3.927, "Kedua kurva berpotongan di π/4 dan 5π/4.", yr=(-1.5, 1.5))],
            "explanation": "Luas antara kurva = ∫ (atas − bawah)."}


@register("al.dua_parabola", LS, (1, 2, 3))
def dua_parabola(rng, tier):
    s = rng.randint(1, 3)
    k = 2 * s * s
    val = Fr(8 * s ** 3, 3)
    return {"prompt": f"Hitung luas daerah yang dibatasi y = x² dan y = {k} − x².", "correct": n(val),
            "distractors": [n(val / 2), n(Fr(4 * s ** 3, 3)), n(val * 2), n(k * s)],
            "steps": [f"Titik potong: x² = {k} − x² ⇒ x = ±{s}.", f"Luas = ∫₋{s}^{s} ({k} − 2x²) dx = 2[{k}x − 2x³/3]₀^{s}.", f"= 2({k * s} − {n(Fr(2 * s ** 3, 3))}) = <b>{n(val)}</b>."],
            "graphs": [region("Daerah lensa antara dua parabola", f"{k}-x*x", "x*x", -s, s, "Simetris terhadap sumbu-y: hitung separuh lalu kalikan 2.", yr=(-1, k + 2))],
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
    m = rng.randint(1, 3)
    val = Fr(m ** 4, 2)
    return {"prompt": f"Hitung luas total daerah yang dibatasi y = x³ dan y = {m * m if m > 1 else ''}x.", "correct": n(val),
            "distractors": ["0", n(val / 2), n(m ** 4), n(Fr(m ** 4, 4))],
            "steps": [f"Titik potong: x³ = {m * m}x ⇒ x = 0, ±{m}.", "Daerah terdiri dari dua bagian simetris (fungsi ganjil); integral bertanda di [−m, m] = 0, jadi hitung satu bagian lalu ×2.",
                      f"2∫₀^{m} ({m * m}x − x³) dx = 2({m ** 4}/2 − {m ** 4}/4) = <b>{n(val)}</b>."],
            "graphs": [region("Dua daerah antara x³ dan m²x", f"{m * m}*x", "x**3", 0, m, "Bagian kiri adalah cerminan titik bagian kanan.", xr=[-m - 1, m + 1], yr=(-m ** 3 - 2, m ** 3 + 2))],
            "explanation": "Pecah daerah di setiap titik potong; jangan sampai luas saling menghapus."}


@register("al.luas_eksp", LS, (4, 5))
def luas_eksp(rng, tier):
    k = rng.randint(2, 6)
    val = Fr(k) + Fr(1, k) - 2
    return {"prompt": f"Hitung luas daerah yang dibatasi y = eˣ, y = e⁻ˣ, dan garis x = ln {k}.", "correct": n(val),
            "distractors": [n(Fr(k) - Fr(1, k)), n(k - 1), n(val + 2), n(Fr(k - 1, k))],
            "steps": ["Kedua kurva berpotongan di x = 0; untuk x &gt; 0, eˣ di atas.", f"∫₀^{{ln {k}}} (eˣ − e⁻ˣ) dx = [eˣ + e⁻ˣ]₀^{{ln {k}}} = ({k} + 1/{k}) − 2.", f"= <b>{n(val)}</b>."],
            "graphs": [region("Antara eˣ dan e⁻ˣ", "exp(x)", "exp(-x)", 0, round(math.log(k), 3), "Luas = cosh-type: (k + 1/k) − 2.", yr=(0, k + 1))],
            "explanation": "e^(ln k) = k, e^(−ln k) = 1/k."}


# ════════════════════════ Topik 2: Volume benda putar ══════════════════════
@register("vol.cakram", VL, (1, 2, 3))
def cakram(rng, tier):
    a = rng.randint(1, 4)
    if tier == 1:
        val, f, js = Fr(a * a, 2), "√x", "sqrt(x)"
        work = f"π∫₀^{a} x dx = π·{a * a}/2"
    elif tier == 2:
        val, f, js = Fr(a ** 5, 5), "x²", "x*x"
        work = f"π∫₀^{a} x⁴ dx = π·{a ** 5}/5"
    else:
        m = rng.randint(1, 3)
        val, f, js = Fr(m * m * a ** 3, 3), f"{m if m > 1 else ''}x", f"{m}*x"
        work = f"π∫₀^{a} {m * m}x² dx = π·{m * m * a ** 3}/3 (volume kerucut ⅓πr²h)"
    return {"prompt": f"Daerah di bawah y = {f}, 0 ≤ x ≤ {a}, diputar mengelilingi sumbu-x. Hitung volumenya.", "correct": pi_txt(val),
            "distractors": [pi_txt(val * 2), n(val), pi_txt(val * Fr(3, 2)), pi_txt(val / 2)],
            "steps": ["Metode cakram: V = π∫ₐᵇ [f(x)]² dx (setiap irisan berbentuk cakram berjari-jari f(x)).", f"{work}.", f"V = <b>{pi_txt(val)}</b>."],
            "graphs": [solid_graph("Irisan cakram", js, 0, a, "Geser posisi: luas cakram πf(x)² dijumlahkan sepanjang sumbu-x.")],
            "explanation": "Volume = ∫ luas penampang dx."}


@register("vol.cincin", VL, (1, 2, 3, 4))
def cincin(rng, tier):
    k = rng.randint(1, 3)
    val = Fr(2 * k ** 5, 15)
    return {"prompt": f"Daerah antara y = {k if k > 1 else ''}x dan y = x² diputar mengelilingi sumbu-x. Hitung volumenya.", "correct": pi_txt(val),
            "distractors": [pi_txt(Fr(k ** 5, 15)), pi_txt(Fr(k ** 3, 6)), pi_txt(val * 2), pi_txt(Fr(k ** 5, 5))],
            "steps": [f"Titik potong x = 0 dan x = {k}. Penampang berupa cincin: R = {k}x, r = x².",
                      f"V = π∫₀^{k} ({k * k}x² − x⁴) dx = π({k ** 5}/3 − {k ** 5}/5).", f"= <b>{pi_txt(val)}</b>."],
            "graphs": [region("Daerah yang diputar", f"{k}*x", "x*x", 0, k, "Jari-jari luar = garis, jari-jari dalam = parabola.", yr=(-0.5, k * k + 1))],
            "explanation": "Metode cincin (washer): V = π∫ (R² − r²) dx."}


@register("vol.kulit", VL, (3, 4, 5))
def kulit(rng, tier):
    a = rng.randint(1, 4)
    if tier <= 4:
        val = Fr(a ** 4, 6)
        return {"prompt": f"Daerah di bawah y = x({a} − x), 0 ≤ x ≤ {a}, diputar mengelilingi sumbu-y. Hitung volumenya (metode kulit tabung).",
                "correct": pi_txt(val), "distractors": [pi_txt(Fr(a ** 4, 12)), pi_txt(Fr(a ** 5, 30)), pi_txt(val * 2), pi_txt(Fr(a ** 3, 6))],
                "steps": ["Kulit tabung: V = 2π∫ x·f(x) dx (keliling 2πx × tinggi f(x) × tebal dx).", f"2π∫₀^{a} ({a}x² − x³) dx = 2π({a ** 4}/3 − {a ** 4}/4).", f"= <b>{pi_txt(val)}</b>."],
                "graphs": [region("Daerah dan satu kulit", f"x*({a}-x)", "0", 0, a, "Diputar terhadap sumbu-y: setiap pita tegak menjadi kulit tabung.", yr=(-0.5, a * a / 4 + 1))],
                "explanation": "Kulit tabung cocok bila diputar terhadap sumbu yang sejajar pita."}
    R, r = rng.randint(3, 6), rng.randint(1, 2)
    val = 2 * R * r * r
    return {"prompt": f"Lingkaran (x − {R})² + y² = {r * r} diputar mengelilingi sumbu-y membentuk torus. Hitung volumenya.",
            "correct": f"{val}π²", "distractors": [f"{2 * R * r}π²", f"{val}π", f"{R * r * r}π²", f"{4 * R * r * r}π²"],
            "steps": [f"Teorema Pappus: V = (luas daerah)·(jarak lintasan pusat massa) = π·{r * r}·2π·{R}.", f"= <b>{val}π²</b>.",
                      "(Dapat diverifikasi dengan kulit tabung: 2π∫ x·2√(r² − (x − R)²) dx.)"],
            "explanation": "Teorema Pappus: V = A·2π·d."}


@register("vol.penampang", VL, (4, 5))
def penampang(rng, tier):
    r = rng.randint(1, 4)
    if tier == 4:
        val, shape = Fr(16 * r ** 3, 3), "persegi"
        work = f"sisi = 2√({r * r} − x²) ⇒ A(x) = 4({r * r} − x²); V = ∫₋{r}^{r} 4({r * r} − x²) dx"
        correct = n(val)
        wrong = [n(val / 2), pi_txt(val), n(Fr(4 * r ** 3, 3)), n(val * 2)]
    else:
        val, shape = Fr(2 * r ** 3, 3), "setengah lingkaran (diameter di alas)"
        work = f"jari-jari = √({r * r} − x²) ⇒ A(x) = (π/2)({r * r} − x²); V = (π/2)∫₋{r}^{r} ({r * r} − x²) dx"
        correct = pi_txt(val)
        wrong = [pi_txt(val * 2), n(val), pi_txt(Fr(4 * r ** 3, 3)), pi_txt(val / 2)]
    return {"prompt": f"Alas benda adalah cakram x² + y² ≤ {r * r}. Setiap penampang tegak lurus sumbu-x berbentuk {shape}. Hitung volumenya.",
            "correct": correct, "distractors": wrong, "steps": ["V = ∫ A(x) dx dengan A(x) luas penampang.", work + ".", f"= <b>{correct}</b>."],
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
    s = rng.randint(2, 4)
    a = s * s - 1
    val = Fr(2, 3) * (s ** 3 - 1)
    return {"prompt": f"Hitung panjang busur y = (2/3)x<sup>3/2</sup> dari x = 0 sampai x = {a}.", "correct": n(val),
            "distractors": [n(Fr(2, 3) * s ** 3), n(val * 2), n(Fr(a ** 1.5 * 2 / 3).limit_denominator(10)) if a != s * s else n(a), n(val - 1)],
            "steps": ["y′ = x<sup>1/2</sup> ⇒ √(1 + y′²) = √(1 + x).", f"L = ∫₀^{a} √(1 + x) dx = (2/3)[(1 + x)<sup>3/2</sup>]₀^{a}.", f"= (2/3)({s}³ − 1) = <b>{n(val)}</b>."],
            "graphs": [g2d("Kurva y = (2/3)x^(3/2)", [-0.5, a + 1], [-0.5, a ** 1.5 * 0.7 + 1], [], [fn("2/3*pow(x,1.5)", "blue", "y", **{"from": 0})], None,
                           "Panjang busur selalu ≥ jarak lurus antara kedua ujung.")],
            "explanation": "Pilih kurva yang membuat 1 + y′² mudah diakarkan."}


@register("pb.cosh", PJ, (3, 4, 5))
def pb_cosh(rng, tier):
    if tier <= 4:
        k = rng.randint(2, 7)
        val = Fr(k * k - 1, 2 * k)
        return {"prompt": f"Hitung panjang busur rantai y = cosh x dari x = 0 sampai x = ln {k}.", "correct": n(val),
                "distractors": [n(Fr(k * k + 1, 2 * k)), n(k - 1), n(val * 2), "ln " + str(k)],
                "steps": ["y′ = sinh x, 1 + sinh²x = cosh²x ⇒ √(1 + y′²) = cosh x.", f"L = sinh(ln {k}) = ({k} − 1/{k})/2.", f"= <b>{n(val)}</b>."],
                "explanation": "Kurva rantai (catenary, kabel listrik FT) memiliki panjang busur sinh x."}
    a = rng.randint(2, 4)
    val = Fr(a * a - 1, 8)
    correct = f"{n(val)} + ln {a}"
    return {"prompt": f"Hitung panjang busur y = x²/8 − ln x dari x = 1 sampai x = {a}.", "correct": correct,
            "distractors": [f"{n(val)} − ln {a}", f"{n(val)}", f"{n(val * 2)} + ln {a}", f"ln {a}"],
            "steps": ["y′ = x/4 − 1/x ⇒ 1 + y′² = (x/4 + 1/x)² (kuadrat sempurna!).", f"L = ∫₁^{a} (x/4 + 1/x) dx = [x²/8 + ln x]₁^{a}.", f"= <b>{correct}</b>."],
            "explanation": "Soal panjang busur dirancang agar 1 + y′² menjadi kuadrat sempurna."}


@register("pb.permukaan", PJ, (4, 5))
def permukaan(rng, tier):
    if tier == 4:
        r = rng.randint(1, 6)
        return {"prompt": f"Hitung luas permukaan bola berjari-jari {r} dengan memutar y = √({r * r} − x²) mengelilingi sumbu-x.", "correct": pi_txt(4 * r * r),
                "distractors": [pi_txt(2 * r * r), pi_txt(Fr(4 * r ** 3, 3)), pi_txt(r * r), pi_txt(8 * r * r)],
                "steps": ["S = 2π∫ y√(1 + y′²) dx.", f"y√(1 + y′²) = √({r * r} − x²)·{r}/√({r * r} − x²) = {r}.", f"S = 2π∫₋{r}^{r} {r} dx = <b>{pi_txt(4 * r * r)}</b>."],
                "explanation": "Luas permukaan benda putar: S = 2π∫ f(x)√(1 + f′²) dx."}
    a = rng.randint(2, 6) * 4
    val = Fr(15 * a * a, 16)
    return {"prompt": f"Garis y = (3/4)x, 0 ≤ x ≤ {a}, diputar mengelilingi sumbu-x. Hitung luas permukaan kerucut yang terbentuk.", "correct": pi_txt(val),
            "distractors": [pi_txt(Fr(3 * a * a, 4)), pi_txt(val * 2), pi_txt(Fr(9 * a * a, 16)), pi_txt(Fr(5 * a * a, 4))],
            "steps": ["S = 2π∫₀^{a} (3x/4)·√(1 + 9/16) dx = 2π·(3/4)(5/4)·a²/2.", f"= <b>{pi_txt(val)}</b> (cocok dengan πrℓ = π·{n(Fr(3 * a, 4))}·{n(Fr(5 * a, 4))})."],
            "explanation": "Rumus selimut kerucut πrℓ muncul dari integral luas permukaan."}


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
        m = rng.randint(1, 5)
        val = Fr(m + 1, m + 2)
        return {"prompt": f"Tentukan x̄ (pusat massa/sentroid) daerah di bawah y = x{sup(m) if m > 1 else ''} pada 0 ≤ x ≤ 1.", "correct": n(val),
                "distractors": [n(Fr(1, 2)), n(Fr(m, m + 1)), n(Fr(m + 2, m + 3)), n(Fr(1, m + 2))],
                "steps": ["x̄ = ∫ x·f dx / ∫ f dx.", f"∫₀¹ x{sup(m + 1)} dx = 1/{m + 2}; ∫₀¹ x{sup(m)} dx = 1/{m + 1}.", f"x̄ = {m + 1}/{m + 2} = <b>{n(val)}</b>."],
                "explanation": "Sentroid daerah: x̄ = (1/A)∫ x f(x) dx."}
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
    L = rng.randint(1, 4)
    k = Fr(2, L * L)
    if tier == 1:
        return {"prompt": f"f(x) = kx untuk 0 ≤ x ≤ {L} (nol di luar) adalah fungsi kepadatan peluang. Tentukan k.", "correct": f"k = {n(k)}",
                "distractors": [f"k = {n(Fr(1, L))}", f"k = {n(Fr(1, L * L))}", f"k = {n(k * 2)}", "k = 1"],
                "steps": ["Syarat kepadatan: ∫ f(x) dx = 1.", f"∫₀^{L} kx dx = k·{L * L}/2 = 1 ⇒ <b>k = {n(k)}</b>."],
                "explanation": "Total peluang = luas di bawah kepadatan = 1 (FMIPA statistika)."}
    a = Fr(L, 2)
    P = k * a * a / 2
    return {"prompt": f"X berkepadatan f(x) = {n(k)}x pada [0, {L}]. Hitung P(X ≤ {n(a)}).", "correct": n(P),
            "distractors": [n(Fr(1, 2)), n(P * 2), n(1 - P), n(k * a)],
            "steps": [f"P(X ≤ {n(a)}) = ∫₀^{{{n(a)}}} {n(k)}x dx = {n(k)}·({n(a)})²/2.", f"= <b>{n(P)}</b>."],
            "graphs": [g2d("Peluang = luas di bawah kepadatan", [-0.2, L + 0.2], [0, float(k * L) * 1.2], [param("t", "batas t", 0, L, 0.01, float(a), "t")],
                           [{"type": "fill", "upper": f"{float(k)}*x", "from": 0, "to": "t", "color": "amber"}, fn(f"{float(k)}*x", "blue", "f(x)", **{"from": 0, "to": L})],
                           [readout("P(X ≤ t)", f"{float(k)}*t*t/2", 4)], "Geser t: peluang kumulatif naik dari 0 ke 1.")],
            "explanation": "P(a ≤ X ≤ b) = ∫ₐᵇ f(x) dx."}
