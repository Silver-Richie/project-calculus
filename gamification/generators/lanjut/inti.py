"""
Topik INTI Level Utama 4 (Kalkulus Tingkat Lanjut) — dipakai bersama oleh jalur FT, FMIPA, dan Fasilkom.

Setiap generator didaftarkan ke tiga topik sekaligus (kl-ft-…, kl-fm-…, kl-fk-…).
Rujukan: Stewart Bab 12–16; Whitman Bab 14–16; Strang (MIT) Bab 11–15.
"""

from fractions import Fraction as Fr
import math

from .. import register
from ..fmt import MINUS, n, paren, poly, sup, terms
from ..graphs import fn, g2d, param, pt, readout
from ..precalc.common import distinct, nz
from ..dasar.aplikasi import pi_txt

FAC = ("ft", "fm", "fk")


def core(key):
    """Tuple slug topik inti untuk ketiga fakultas."""
    return tuple(f"kl-{f}-{key}" for f in FAC)


PBF, PBL, TPP, TPG, ILG, ILK, KVM, KVG, FKG, FKA = (core(k) for k in (
    "pb-fungsi", "pb-limit", "tp-parsial", "tp-gradien", "il-ganda", "il-koordinat", "kv-medan", "kv-garis", "fk-gamma", "fk-analisis"))


# ════════════════════════ Fungsi dua variabel ═══════════════════════════════
@register("pf.nilai", PBF, (1, 2))
def pf_nilai(rng, tier):
    a, b, c = nz(rng, -3, 3), rng.randint(-4, 4), rng.randint(-3, 3)
    x, y = rng.randint(-3, 3), rng.randint(-3, 3)
    if tier == 1:
        val = a * x * x + b * x * y + c * y * y
        f = f"{n(a)}x² + {n(b)}xy + {n(c)}y²".replace("+ −", "− ")
    else:
        val = Fr(a * x + b, 1) * (y * y + 1)
        f = f"({n(a)}x + {n(b)})(y² + 1)".replace("+ −", "− ")
    return {"prompt": f"Diketahui f(x, y) = {f}. Hitung f({n(x)}, {n(y)}).", "correct": n(val),
            "distractors": [n(val + 1), n(-val), n(val * 2), n(a * y * y + b * x * y + c * x * x) if tier == 1 else n((a * y + b) * (x * x + 1))],
            "steps": ["Fungsi dua variabel memasangkan setiap titik (x, y) dengan satu bilangan f(x, y).", f"Substitusi x = {n(x)}, y = {n(y)}: <b>{n(val)}</b>."],
            "explanation": "f: ℝ² → ℝ; grafiknya permukaan z = f(x, y) di ruang tiga dimensi."}


@register("pf.domain", PBF, (1, 2, 3))
def pf_domain(rng, tier):
    r = rng.randint(1, 6)
    cases = [(f"√({r * r} − x² − y²)", f"cakram tertutup x² + y² ≤ {r * r}", "bilangan di bawah akar ≥ 0."),
             ("ln(x − y)", "setengah bidang x &gt; y", "argumen ln harus &gt; 0."),
             (f"1/(x² + y² − {r * r})", f"semua (x, y) kecuali lingkaran x² + y² = {r * r}", "penyebut tidak boleh 0."),
             ("√(y − x²)", "daerah di atas (dan pada) parabola y = x²", "y − x² ≥ 0.")]
    pool = cases[:2] if tier == 1 else cases
    f, dom, why = rng.choice(pool)
    return {"prompt": f"Tentukan domain alami f(x, y) = {f}.", "correct": dom, "distractors": [c[1] for c in cases if c[1] != dom] + ["seluruh ℝ²"],
            "steps": [f"Syarat: {why}", f"Domain: <b>{dom}</b>."], "explanation": "Domain fungsi dua variabel berupa daerah di bidang-xy."}


@register("pf.kurva_tingkat", PBF, (2, 3, 4, 5))
def kurva_tingkat(rng, tier):
    k = rng.randint(1, 9)
    a, b = rng.randint(1, 3), rng.randint(1, 3)
    cases = [("x² + y²", f"lingkaran berjari-jari √{k}" if int(k ** 0.5) ** 2 != k else f"lingkaran berjari-jari {int(k ** 0.5)}", f"x*x+y*y", "circle"),
             ("y − x²", f"parabola y = x² + {k}", "y-x*x", "parab"),
             (f"{a * a if a > 1 else ''}x² + {b * b if b > 1 else ''}y²", "elips", "", "ell"),
             ("x² − y²", "hiperbola", "", "hyp")]
    pool = cases[:2] if tier == 2 else cases
    f, shape, _, kind = rng.choice(pool)
    return {"prompt": f"Kurva tingkat f(x, y) = {f} pada ketinggian k = {k} berbentuk …", "correct": shape,
            "distractors": [c[1] for c in cases if c[1] != shape] + ["garis lurus"],
            "steps": ["Kurva tingkat = himpunan titik dengan f(x, y) = k (seperti garis kontur peta).", f"{f} = {k} ⇒ <b>{shape}</b>."],
            "graphs": [g2d("Peta kontur: beberapa kurva tingkat", [-4, 4], [-4, 4], [param("kk", "k", 0.5, 9, 0.5, k, "k")],
                           [{"type": "param", "t": [0, "2*pi"], "x": "sqrt(kk)*cos(t)", "y": "sqrt(kk)*sin(t)", "color": "blue"},
                            {"type": "param", "t": [0, "2*pi"], "x": "sqrt(kk/2)*cos(t)", "y": "sqrt(kk/2)*sin(t)", "color": "gray"}] if kind == "circle" else
                           [fn("x*x+kk", "blue", "y = x² + k"), fn("x*x+kk/2", "gray", dash=True)] if kind == "parab" else
                           [{"type": "param", "t": [0, "2*pi"], "x": f"sqrt(kk)/{a}*cos(t)", "y": f"sqrt(kk)/{b}*sin(t)", "color": "blue"}] if kind == "ell" else
                           [{"type": "param", "t": [-2, 2], "x": "sqrt(kk)*cosh(t)", "y": "sqrt(kk)*sinh(t)", "color": "blue"},
                            {"type": "param", "t": [-2, 2], "x": "-sqrt(kk)*cosh(t)", "y": "sqrt(kk)*sinh(t)", "color": "blue"}],
                           None, "Geser k: kurva tingkat untuk ketinggian lain dari permukaan yang sama.")],
            "explanation": "Kurva tingkat adalah ‘irisan mendatar’ permukaan z = f(x, y)."}


@register("pf.permukaan", PBF, (3, 4, 5))
def permukaan(rng, tier):
    cases = [("z = x² + y²", "paraboloid (mangkuk)"), ("z = x² − y²", "paraboloid hiperbolik (pelana)"), ("z = √(x² + y²)", "kerucut"),
             ("z = 6 − 2x − 3y", "bidang datar"), ("z = √(9 − x² − y²)", "setengah bola"), ("z = y²", "silinder parabolik")]
    f, shape = rng.choice(cases)
    return {"prompt": f"Grafik {f} adalah …", "correct": shape, "distractors": [c[1] for c in cases if c[1] != shape],
            "steps": ["Lihat irisan dengan bidang z = k (kurva tingkat) dan dengan bidang x = 0 / y = 0.", f"<b>{shape}</b>."],
            "explanation": "Mengenali permukaan dari irisan-irisannya (Stewart §12.6)."}


# ════════════════════════ Limit & kekontinuan dua variabel ══════════════════
@register("pl.substitusi", PBL, (1, 2))
def pl_substitusi(rng, tier):
    a, b = rng.randint(-3, 3), rng.randint(-3, 3)
    p, q = nz(rng, -3, 3), rng.randint(-4, 4)
    if tier == 1:
        val = Fr(p * a * a + q * a * b)
        prompt = f"Hitung lim<sub>(x,y)→({n(a)},{n(b)})</sub> ({n(p)}x² + {n(q)}xy).".replace("+ −", "− ")
    else:
        den = a * a + b * b + 1
        val = Fr(p * a + q * b, den)
        prompt = f"Hitung lim<sub>(x,y)→({n(a)},{n(b)})</sub> ({n(p)}x + {n(q)}y)/(x² + y² + 1).".replace("+ −", "− ")
    return {"prompt": prompt, "correct": n(val), "distractors": [n(val + 1), n(-val), "tidak ada", "0" if val else "1"],
            "steps": ["Polinom dan fungsi rasional (penyebut ≠ 0) kontinu ⇒ substitusi langsung.", f"<b>{n(val)}</b>."],
            "explanation": "Fungsi kontinu: limit = nilai fungsi."}


@register("pl.kontinu", PBL, (1, 2, 3))
def pl_kontinu(rng, tier):
    a = rng.randint(1, 5)
    return {"prompt": f"Agar f(x, y) = sin({a if a > 1 else ''}(x² + y²))/(x² + y²) untuk (x, y) ≠ (0, 0) kontinu di (0, 0), nilai f(0, 0) haruslah …",
            "correct": n(a), "distractors": ["0", "1" if a != 1 else "2", "tidak ada nilai yang cocok", n(a * a)],
            "steps": ["Misal r² = x² + y² → 0.", f"sin({a}r²)/r² = {a}·sin({a}r²)/({a}r²) → {a}·1.", f"f(0, 0) = <b>{a}</b>."],
            "explanation": "Kontinu ⇔ nilai fungsi = limit."}


@register("pl.jalur", PBL, (2, 3, 4, 5))
def pl_jalur(rng, tier):
    if tier <= 3:
        m = rng.randint(1, 4)
        val = Fr(1 - m * m, 1 + m * m)
        return {"prompt": f"Untuk f(x, y) = (x² − y²)/(x² + y²), hitung limit f sepanjang garis y = {m if m > 1 else ''}x saat (x, y) → (0, 0).",
                "correct": n(val), "distractors": ["0", "1", n(-val), "tidak ada"],
                "steps": [f"Substitusi y = {m}x: (x² − {m * m}x²)/(x² + {m * m}x²) = (1 − {m * m})/(1 + {m * m}).", f"= <b>{n(val)}</b>.",
                          "Nilai bergantung pada m ⇒ limit dua variabel di (0, 0) TIDAK ADA."],
                "graphs": [g2d("Nilai limit sepanjang y = mx bergantung m", [-4, 4], [-1.2, 1.2], [], [fn("(1-x*x)/(1+x*x)", "blue", "(1 − m²)/(1 + m²)")], None,
                               "Sumbu horizontal = gradien jalur m. Karena nilainya berbeda-beda, limit tidak ada.")],
                "explanation": "Dua jalur dengan nilai limit berbeda ⇒ limit tidak ada."}
    if tier == 4:
        return {"prompt": "Apakah lim<sub>(x,y)→(0,0)</sub> xy/(x² + y²) ada?", "correct": "tidak ada (y = x memberi 1/2, y = 0 memberi 0)",
                "distractors": ["ada, nilainya 0", "ada, nilainya 1/2", "ada, nilainya 1", "tidak ada karena penyebut 0"],
                "steps": ["Jalur y = 0: f = 0.", "Jalur y = x: f = x²/(2x²) = 1/2.", "Berbeda ⇒ <b>tidak ada</b>."], "explanation": "Uji dua jalur."}
    return {"prompt": "Apakah lim<sub>(x,y)→(0,0)</sub> xy²/(x² + y⁴) ada?", "correct": "tidak ada (x = y² memberi 1/2, garis lurus memberi 0)",
            "distractors": ["ada, nilainya 0 (semua garis lurus memberi 0)", "ada, nilainya 1/2", "ada, nilainya 1", "tidak ada karena tak terbatas"],
            "steps": ["Sepanjang setiap garis y = mx: f = m²x³/(x² + m⁴x⁴) → 0.", "Sepanjang parabola x = y²: f = y⁴/(2y⁴) = 1/2.",
                      "Semua garis memberi 0, tetapi parabola memberi 1/2 ⇒ <b>tidak ada</b>. Memeriksa garis saja tidak cukup!"],
            "explanation": "Limit dua variabel harus sama di SEMUA jalur."}


@register("pl.polar", PBL, (3, 4, 5))
def pl_polar(rng, tier):
    cases = [("x²y/(x² + y²)", "0", "r cos²θ sin θ → 0 karena |cos²θ sin θ| ≤ 1."), ("(x³ + y³)/(x² + y²)", "0", "r(cos³θ + sin³θ) → 0."),
             ("(x² + y²)·ln(x² + y²)", "0", "r² ln r² → 0 (L'Hôpital)."), ("(1 − cos(x² + y²))/(x² + y²)²", "1/2", "(1 − cos u)/u² → 1/2 dengan u = r².")]
    f, val, why = rng.choice(cases[:2] if tier == 3 else cases)
    return {"prompt": f"Gunakan koordinat kutub untuk menghitung lim<sub>(x,y)→(0,0)</sub> {f}.", "correct": val, "distractors": [v for v in ["0", "1", "1/2", "tidak ada", "∞"] if v != val],
            "steps": ["x = r cos θ, y = r sin θ; (x, y) → (0, 0) ⇔ r → 0 untuk SEMUA θ.", why, f"<b>{val}</b>."],
            "explanation": "Jika bentuk kutub ≤ g(r) → 0 tanpa bergantung θ, limitnya ada."}


# ════════════════════════ Turunan parsial ═══════════════════════════════════
@register("tpp.notasi", TPP, (1, 2))
def tpp_notasi(rng, tier):
    a = rng.randint(2, 5)
    xa1 = "x" if a == 2 else f"x{sup(a - 1)}"
    cases = [(f"x{sup(a)} sin y", f"{a}{xa1} sin y", [f"x{sup(a)} cos y", f"{a}{xa1} cos y", f"{a}{xa1}"]),
             (f"e<sup>{a}x</sup>y²", f"{a}e<sup>{a}x</sup>y²", [f"2ye<sup>{a}x</sup>", f"e<sup>{a}x</sup>y²", f"{a}e<sup>{a}x</sup>·2y"]),
             (f"ln(x{sup(a)} + y)", f"{a}{xa1}/(x{sup(a)} + y)", [f"1/(x{sup(a)} + y)", f"{a}{xa1}", f"(x{sup(a)} + y)/{a}x"])]
    f, good, bad = rng.choice(cases)
    return {"prompt": f"Tentukan ∂f/∂x untuk f(x, y) = {f}.", "correct": good, "distractors": bad + ["0"],
            "steps": ["∂f/∂x: turunkan terhadap x dan perlakukan y sebagai konstanta.", f"<b>{good}</b>."],
            "explanation": "Turunan parsial = laju perubahan saat hanya satu variabel bergerak."}


@register("tpp.parsial", TPP, (1, 2, 3))
def tpp_parsial(rng, tier):
    a, b = nz(rng, -3, 3), nz(rng, -3, 4)
    m, k = rng.randint(1, 3), rng.randint(1, 3)
    x, y = rng.randint(-2, 2), rng.randint(-2, 2)
    fx = a * m * x ** (m - 1) * y ** k + b * y
    fy = a * k * x ** m * y ** (k - 1) + b * x
    ask = rng.choice(["x", "y"])
    val = fx if ask == "x" else fy
    xm = "x" if m == 1 else f"x{sup(m)}"
    yk = "y" if k == 1 else f"y{sup(k)}"
    return {"prompt": f"f(x, y) = {n(a)}{xm}{yk} + {n(b)}xy. Hitung ∂f/∂{ask} di ({n(x)}, {n(y)}).".replace("+ −", "− "), "correct": n(val),
            "distractors": [n(fy if ask == "x" else fx), n(val + b), n(-val), n(a * x ** m * y ** k + b * x * y)],
            "steps": [f"∂f/∂x = {n(a * m)}x{sup(m - 1) if m > 2 else ('' if m == 1 else '')}{'' if m > 1 else ''}{yk if m >= 1 else ''} + {n(b)}y (y konstan)." if ask == "x" else
                      f"∂f/∂y = {n(a * k)}{xm}y{sup(k - 1) if k > 2 else ''} + {n(b)}x (x konstan).", f"Di ({n(x)}, {n(y)}): <b>{n(val)}</b>."],
            "graphs": [g2d(f"Irisan permukaan pada {'y' if ask == 'x' else 'x'} tetap", [-3, 3], [-30, 30], [param("c", f"{'y' if ask == 'x' else 'x'} tetap", -3, 3, 0.1, y if ask == "x" else x, "c")],
                           [fn(f"{a}*x**{m}*c**{k}+({b})*x*c" if ask == "x" else f"{a}*c**{m}*x**{k}+({b})*c*x", "blue", "irisan")], None,
                           f"∂f/∂{ask} adalah kemiringan kurva irisan ini.")],
            "explanation": "Soal U-S6 (berkas soal dasar) adalah contoh tetapnya."}


@register("tpp.orde2", TPP, (2, 3, 4))
def tpp_orde2(rng, tier):
    a, m, k = nz(rng, -3, 3), rng.randint(1, 4), rng.randint(1, 4)
    x, y = rng.randint(1, 2), rng.randint(-2, 2)
    if tier <= 3:
        val = a * m * k * x ** (m - 1) * y ** (k - 1)
        prompt = f"f(x, y) = {n(a)}x{sup(m) if m > 1 else ''}y{sup(k) if k > 1 else ''}. Hitung f<sub>xy</sub>({x}, {n(y)})."
        steps = [f"f<sub>x</sub> = {n(a * m)}x{sup(m - 1)}y{sup(k)}, lalu turunkan terhadap y: f<sub>xy</sub> = {n(a * m * k)}x{sup(m - 1)}y{sup(k - 1)}.",
                 "Teorema Clairaut: f<sub>xy</sub> = f<sub>yx</sub> bila keduanya kontinu.", f"Nilai: <b>{n(val)}</b>."]
        correct = n(val)
        wrong = [n(a * m * (m - 1) * x ** max(m - 2, 0) * y ** k), n(val * 2), n(-val), n(val + 1)]
    else:
        x, y = rng.choice([(1, 1), (1, 2), (2, 1), (1, 3), (2, -1), (1, -2)])
        correct = f"{n(1 + x * y)}e{sup(x * y)}" if x * y != 1 else "2e"
        prompt = f"f(x, y) = e<sup>xy</sup>. Hitung f<sub>xy</sub>({x}, {n(y)})."
        steps = ["f<sub>x</sub> = y·e<sup>xy</sup>.", "f<sub>xy</sub> = e<sup>xy</sup> + xy·e<sup>xy</sup> = (1 + xy)e<sup>xy</sup>.", f"Di ({x}, {n(y)}): <b>{correct}</b>."]
        wrong = [f"e{sup(x * y)}", f"{n(x * y)}e{sup(x * y)}", f"{n(y * y)}e{sup(x * y)}", f"{n(1 - x * y)}e{sup(x * y)}"]
    return {"prompt": prompt, "correct": correct, "distractors": wrong, "steps": steps, "explanation": "Turunan parsial orde dua dan teorema Clairaut."}


@register("tpp.rantai", TPP, (3, 4, 5))
def tpp_rantai(rng, tier):
    t = rng.randint(1, 2)
    if tier <= 4:
        p, q = rng.randint(1, 3), rng.randint(1, 3)
        # z = x²y, x = t^p, y = t^q ⇒ z = t^{2p + q} ⇒ dz/dt = (2p + q) t^{2p+q−1}
        val = (2 * p + q) * t ** (2 * p + q - 1)
        return {"prompt": f"z = x²y dengan x = t{sup(p) if p > 1 else ''}, y = t{sup(q) if q > 1 else ''}. Hitung dz/dt saat t = {t}.", "correct": n(val),
                "distractors": [n(2 * p * t ** (2 * p + q - 1)), n(val + 1), n(t ** (2 * p + q)), n(val * 2)],
                "steps": ["Aturan rantai: dz/dt = (∂z/∂x)(dx/dt) + (∂z/∂y)(dy/dt) = 2xy·x′ + x²·y′.",
                          f"Di t = {t}: x = {t ** p}, y = {t ** q}, x′ = {p * t ** (p - 1)}, y′ = {q * t ** (q - 1)}.",
                          f"dz/dt = 2·{t ** p}·{t ** q}·{p * t ** (p - 1)} + {t ** (2 * p)}·{q * t ** (q - 1)} = <b>{val}</b>."],
                "explanation": "Aturan rantai multivariabel: jumlahkan kontribusi setiap jalur."}
    s = rng.randint(1, 3)
    val = 2 * s + 2 * s   # z = x² + y², x = s + t, y = s − t ⇒ ∂z/∂s = 2x + 2y = 4s
    return {"prompt": f"z = x² + y² dengan x = s + t, y = s − t. Hitung ∂z/∂s di (s, t) = ({s}, {t}).", "correct": n(4 * s),
            "distractors": [n(4 * t), n(2 * s), n(2 * (s + t)), "0"],
            "steps": ["∂z/∂s = z_x·x_s + z_y·y_s = 2x·1 + 2y·1.", f"x = {s + t}, y = {s - t} ⇒ 2({s + t}) + 2({s - t}) = <b>{4 * s}</b>."],
            "explanation": "Pohon aturan rantai untuk variabel antara."}


@register("tpp.implisit", TPP, (4, 5))
def tpp_implisit(rng, tier):
    x0, y0, z0 = rng.randint(1, 3), rng.randint(1, 3), rng.randint(1, 3)
    c = x0 * x0 + y0 * y0 + z0 * z0 + x0 * y0 * z0
    val = Fr(-(2 * x0 + y0 * z0), 2 * z0 + x0 * y0)
    return {"prompt": f"Permukaan x² + y² + z² + xyz = {c} memuat titik ({x0}, {y0}, {z0}). Hitung ∂z/∂x di titik itu.", "correct": n(val),
            "distractors": [n(-val), n(Fr(-(2 * x0), 2 * z0)), n(Fr(2 * z0 + x0 * y0, 2 * x0 + y0 * z0)), n(val - 1)],
            "steps": ["F(x, y, z) = 0 ⇒ ∂z/∂x = −F<sub>x</sub>/F<sub>z</sub>.", f"F<sub>x</sub> = 2x + yz = {2 * x0 + y0 * z0}, F<sub>z</sub> = 2z + xy = {2 * z0 + x0 * y0}.",
                      f"∂z/∂x = <b>{n(val)}</b>."], "explanation": "Turunan implisit multivariabel."}


# ════════════════════════ Gradien & turunan berarah ═════════════════════════
def _f_grad(rng):
    a, b, c = nz(rng, -3, 3), nz(rng, -3, 3), rng.randint(-3, 3)
    x, y = rng.randint(-2, 2), rng.randint(-2, 2)
    fx, fy = 2 * a * x + c * y, 2 * b * y + c * x
    f = terms([(a, "x²"), (b, "y²"), (c, "xy")])
    return f, x, y, fx, fy


@register("tg.gradien", TPG, (1, 2))
def tg_gradien(rng, tier):
    f, x, y, fx, fy = _f_grad(rng)
    correct = f"⟨{n(fx)}, {n(fy)}⟩"
    return {"prompt": f"Tentukan ∇f({n(x)}, {n(y)}) untuk f(x, y) = {f}.", "correct": correct,
            "distractors": [f"⟨{n(fy)}, {n(fx)}⟩", f"⟨{n(-fx)}, {n(-fy)}⟩", f"⟨{n(fx + 1)}, {n(fy)}⟩", f"⟨{n(fx)}, {n(fx)}⟩"],
            "steps": ["∇f = ⟨f<sub>x</sub>, f<sub>y</sub>⟩.", f"f<sub>x</sub>({n(x)}, {n(y)}) = {n(fx)}, f<sub>y</sub>({n(x)}, {n(y)}) = {n(fy)}.", f"<b>{correct}</b>."],
            "explanation": "Gradien menunjuk arah kenaikan tercepat dan tegak lurus kurva tingkat."}


@register("tg.ortho", TPG, (1, 2))
def tg_ortho(rng, tier):
    good = "tegak lurus kurva tingkat dan menunjuk arah kenaikan tercepat"
    return {"prompt": "Di setiap titik, vektor gradien ∇f(x, y) …", "correct": good,
            "distractors": ["sejajar (menyinggung) kurva tingkat", "menunjuk arah penurunan tercepat", "selalu bernilai nol", "searah sumbu-x"],
            "steps": ["Sepanjang kurva tingkat f konstan ⇒ D<sub>u</sub>f = ∇f·u = 0 untuk u menyinggung kurva.", "Jadi ∇f ⟂ kurva tingkat, dan D<sub>u</sub>f maksimum saat u searah ∇f.",
                      f"<b>{good}</b>."], "explanation": "Sifat geometris gradien (dasar gradient descent)."}


@register("tg.berarah", TPG, (2, 3, 4))
def tg_berarah(rng, tier):
    f, x, y, fx, fy = _f_grad(rng)
    p, q, h = rng.choice([(3, 4, 5), (4, 3, 5), (-3, 4, 5), (5, 12, 13), (12, -5, 13), (0, 1, 1), (1, 0, 1)])
    val = Fr(fx * p + fy * q, h)
    return {"prompt": f"f(x, y) = {f}. Hitung turunan berarah di ({n(x)}, {n(y)}) dalam arah vektor ⟨{n(p)}, {n(q)}⟩.", "correct": n(val),
            "distractors": [n(fx * p + fy * q), n(-val), n(Fr(fx + fy, 1)), n(val + 1)],
            "steps": [f"Satuan arah: u = ⟨{n(p)}, {n(q)}⟩/{h}.", f"∇f = ⟨{n(fx)}, {n(fy)}⟩.", f"D<sub>u</sub>f = ∇f·u = ({n(fx)}·{paren(p)} + {n(fy)}·{paren(q)})/{h} = <b>{n(val)}</b>."],
            "explanation": "Turunan berarah D_u f = ∇f · u (u vektor satuan!)."}


@register("tg.maks_arah", TPG, (3, 4, 5))
def tg_maks(rng, tier):
    p, q, h = rng.choice([(3, 4, 5), (6, 8, 10), (5, 12, 13), (8, 15, 17)])
    # f = (p/2)x² + q·y di (1, y0) ⇒ ∇f = (p, q)
    return {"prompt": f"f(x, y) = {n(Fr(p, 2))}x² + {q}y. Berapa laju kenaikan maksimum f di (1, 5) dan ke arah mana?",
            "correct": f"{h}, arah ⟨{p}, {q}⟩", "distractors": [f"{p + q}, arah ⟨{p}, {q}⟩", f"{h}, arah ⟨{q}, {p}⟩", f"{h * h}, arah ⟨{p}, {q}⟩", f"{h}, arah ⟨{-p}, {-q}⟩"],
            "steps": [f"∇f = ⟨{n(p)}x, {q}⟩ = ⟨{p}, {q}⟩ di (1, 5).", f"Laju maksimum = |∇f| = √({p * p} + {q * q}) = {h}, searah ∇f.", f"<b>{h}, arah ⟨{p}, {q}⟩</b>."],
            "explanation": "max D_u f = |∇f|, dicapai saat u searah ∇f; minimum −|∇f| (berlawanan)."}


@register("tg.bidang_singgung", TPG, (3, 4, 5))
def tg_bidang(rng, tier):
    a, b = nz(rng, -2, 3), nz(rng, -2, 3)
    x0, y0 = rng.randint(-2, 2), rng.randint(-2, 2)
    z0 = a * x0 * x0 + b * y0 * y0
    fx, fy = 2 * a * x0, 2 * b * y0
    c = z0 - fx * x0 - fy * y0
    pl = lambda p, q, r: "z = " + terms([(p, "x"), (q, "y")], r)
    correct = pl(fx, fy, c)
    return {"prompt": f"Tentukan bidang singgung permukaan z = {terms([(a, 'x²'), (b, 'y²')])} di titik ({n(x0)}, {n(y0)}, {n(z0)}).", "correct": correct,
            "distractors": [pl(fx, fy, z0), pl(fy, fx, c), pl(a, b, c), pl(-fx, -fy, c), pl(fx, fy, c + 1)],
            "steps": ["z − z₀ = f<sub>x</sub>(x − x₀) + f<sub>y</sub>(y − y₀).", f"f<sub>x</sub> = {n(fx)}, f<sub>y</sub> = {n(fy)}.", f"<b>{correct}</b> (linearisasi dua variabel)."],
            "explanation": "Bidang singgung = aproksimasi linear L(x, y)."}


# ════════════════════════ Integral ganda ════════════════════════════════════
@register("ig.volume", ILG, (1, 2))
def ig_volume(rng, tier):
    if tier == 1:
        c, p, q = rng.randint(1, 9), rng.randint(1, 5), rng.randint(1, 5)
        return {"prompt": f"Hitung ∬<sub>R</sub> {c} dA dengan R = [0, {p}] × [0, {q}].", "correct": n(c * p * q),
                "distractors": [n(c * (p + q)), n(p * q), n(c * p * q * 2), n(Fr(c * p * q, 2))],
                "steps": ["∬ c dA = c × luas R.", f"{c}·{p}·{q} = <b>{c * p * q}</b> (volume balok)."], "explanation": "Integral ganda = volume di bawah permukaan."}
    a, b, c = rng.randint(1, 4), rng.randint(1, 4), rng.randint(1, 6)
    val = Fr(a * b * c, 6)
    return {"prompt": f"Hitung volume benda di oktan pertama di bawah bidang x/{a} + y/{b} + z/{c} = 1.", "correct": n(val),
            "distractors": [n(Fr(a * b * c, 2)), n(Fr(a * b * c, 3)), n(a * b * c), n(val + 1)],
            "steps": [f"z = {c}(1 − x/{a} − y/{b}) di atas segitiga 0 ≤ x ≤ {a}, 0 ≤ y ≤ {b}(1 − x/{a}).", "∬ z dA = (1/3)·(luas alas)·tinggi = (1/3)(ab/2)c.", f"= <b>{n(val)}</b> (limas segitiga)."],
            "explanation": "Volume = ∬ f(x, y) dA."}


@register("ig.persegi", ILG, (1, 2, 3))
def ig_persegi(rng, tier):
    p, q = rng.randint(1, 4), rng.randint(1, 4)
    a, b = nz(rng, -3, 4), nz(rng, -3, 4)
    if tier <= 2:
        val = Fr(a * p * p * q, 2) + Fr(b * p * q * q, 2)
        f = f"{n(a)}x + {n(b)}y".replace("+ −", "− ")
    else:
        val = Fr(a * p * p * q ** 3, 6)
        f = f"{n(a)}xy²"
    return {"prompt": f"Hitung ∬<sub>R</sub> ({f}) dA dengan R = [0, {p}] × [0, {q}].", "correct": n(val),
            "distractors": [n(val * 2), n(-val), n(val + 1), n(Fr(a * p * q, 2))],
            "steps": ["Teorema Fubini: ∬ = ∫₀^p ∫₀^q f dy dx (urutan bebas untuk persegi panjang).",
                      f"Integral dalam lalu integral luar memberi <b>{n(val)}</b>."],
            "explanation": "Integral berulang pada persegi panjang."}


@register("ig.daerah", ILG, (2, 3, 4, 5))
def ig_daerah(rng, tier):
    k = rng.randint(1, 3)
    if tier <= 3:
        val = Fr(k ** 4, 12)
        prompt = f"Hitung ∬<sub>D</sub> x dA, D dibatasi y = x² dan y = {k if k > 1 else ''}x."
        steps = [f"Titik potong x = 0 dan x = {k}; untuk 0 ≤ x ≤ {k}: x² ≤ y ≤ {k}x.", f"∫₀^{k} x({k}x − x²) dx = {k}·{k}³/3 − {k}⁴/4.", f"= <b>{n(val)}</b>."]
    else:
        val = Fr(k ** 6, 24)
        prompt = f"Hitung ∬<sub>D</sub> xy dA, D dibatasi y = x² dan y = {k if k > 1 else ''}x (soal FM-H3 untuk k = 1)."
        steps = [f"∫₀^{k} ∫<sub>x²</sub><sup>{k}x</sup> xy dy dx = ∫₀^{k} x({k * k}x² − x⁴)/2 dx.", f"= ({k * k}·{k}⁴/4 − {k}⁶/6)/2 = <b>{n(val)}</b>."]
    return {"prompt": prompt, "correct": n(val), "distractors": [n(val * 2), n(val / 2), n(Fr(k ** 3, 6)), n(val + 1)], "steps": steps,
            "graphs": [g2d("Daerah D", [-0.5, k + 0.5], [-0.5, k * k + 1], [], [{"type": "fill", "upper": f"{k}*x", "lower": "x*x", "from": 0, "to": k, "color": "amber"},
                                                                              fn(f"{k}*x", "green"), fn("x*x")], None, "Batas dalam y dari parabola ke garis.")],
            "explanation": "Daerah tipe I: a ≤ x ≤ b, g₁(x) ≤ y ≤ g₂(x)."}


@register("ig.urutan", ILG, (3, 4, 5))
def ig_urutan(rng, tier):
    a = rng.randint(1, 2)
    correct = f"(e{sup(a * a)} − 1)/2" if a > 1 else "(e − 1)/2"
    return {"prompt": f"Hitung ∫<sub>0</sub><sup>{a}</sup> ∫<sub>x</sub><sup>{a}</sup> e<sup>y²</sup> dy dx dengan menukar urutan integrasi.", "correct": correct,
            "distractors": [f"e{sup(a * a)} − 1" if a > 1 else "e − 1", f"(e{sup(a)} − 1)/2", "tidak dapat dihitung", f"e{sup(a * a)}/2"],
            "steps": ["e<sup>y²</sup> tidak punya antiturunan elementer ⇒ tukar urutan.", f"Daerah: 0 ≤ x ≤ y ≤ {a} ⇒ ∫₀^{a} ∫₀^y e<sup>y²</sup> dx dy = ∫₀^{a} y·e<sup>y²</sup> dy.",
                      f"= [e<sup>y²</sup>/2]₀^{a} = <b>{correct}</b>."], "explanation": "Menukar urutan integrasi dapat membuat integral mustahil menjadi mudah."}


# ════════════════════════ Integral lipat koordinat kutub/silinder/bola ══════
@register("ik.jacobian_polar", ILK, (1, 2))
def ik_jac(rng, tier):
    return {"prompt": "Dalam koordinat kutub, elemen luas dA sama dengan …", "correct": "r dr dθ", "distractors": ["dr dθ", "r² dr dθ", "dr dθ / r", "r sin θ dr dθ"],
            "steps": ["Sektor kecil berukuran Δr (radial) × rΔθ (busur).", "Luas ≈ r Δr Δθ ⇒ dA = <b>r dr dθ</b> (determinan Jacobian = r)."],
            "explanation": "Jangan lupa faktor r saat mengubah ke koordinat kutub."}


@register("ik.polar", ILK, (1, 2, 3))
def ik_polar(rng, tier):
    R = rng.randint(1, 4)
    if tier == 1:
        correct, prompt = pi_txt(R * R), f"Gunakan koordinat kutub untuk menghitung luas cakram x² + y² ≤ {R * R}."
        steps = [f"∫₀^{{2π}} ∫₀^{R} r dr dθ = 2π·{R * R}/2.", f"= <b>{pi_txt(R * R)}</b>."]
        wrong = [pi_txt(2 * R), pi_txt(Fr(R * R, 2)), n(R * R), pi_txt(2 * R * R)]
    elif tier == 2:
        val = Fr(R ** 4, 2)
        correct, prompt = pi_txt(val), f"Hitung ∬<sub>D</sub> (x² + y²) dA, D: x² + y² ≤ {R * R}."
        steps = ["x² + y² = r², dA = r dr dθ.", f"∫₀^{{2π}} ∫₀^{R} r³ dr dθ = 2π·{R ** 4}/4.", f"= <b>{correct}</b>."]
        wrong = [pi_txt(R ** 4), pi_txt(Fr(R ** 4, 4)), pi_txt(Fr(R ** 3, 3) * 2), n(val)]
    else:
        correct, prompt = f"π(1 − e{sup(-R * R)})", f"Hitung ∬<sub>D</sub> e<sup>−(x² + y²)</sup> dA, D: x² + y² ≤ {R * R}."
        steps = ["∫₀^{2π} ∫₀^R e<sup>−r²</sup> r dr dθ = 2π·[−e<sup>−r²</sup>/2]₀^R.", f"= <b>{correct}</b>. Untuk R → ∞: π, sehingga ∫ e<sup>−x²</sup> dx = √π."]
        wrong = [f"2π(1 − e{sup(-R * R)})", f"π(1 − e{sup(-R)})", "π", f"π e{sup(-R * R)}"]
    return {"prompt": prompt, "correct": correct, "distractors": wrong, "steps": steps,
            "graphs": [g2d("Daerah cakram dalam koordinat kutub", [-5, 5], [-5, 5], [param("RR", "R", 0.5, 4.5, 0.1, R, "R")],
                           [{"type": "param", "t": [0, "2*pi"], "x": "RR*cos(t)", "y": "RR*sin(t)", "color": "blue"}], None,
                           "Batas cakram sederhana dalam (r, θ): 0 ≤ r ≤ R, 0 ≤ θ ≤ 2π.")],
            "explanation": "Daerah lingkaran → koordinat kutub."}


@register("ik.cincin", ILK, (2, 3, 4, 5))
def ik_cincin(rng, tier):
    a, b = sorted(distinct(rng, 1, 5, 2))
    if tier <= 3:
        val = Fr(2 * (b ** 3 - a ** 3), 3)
        correct, prompt = pi_txt(val), f"Hitung ∬<sub>D</sub> √(x² + y²) dA, D: {a * a} ≤ x² + y² ≤ {b * b}."
        steps = [f"√(x² + y²) = r ⇒ ∫₀^{{2π}} ∫<sub>{a}</sub><sup>{b}</sup> r·r dr dθ.", f"= 2π({b}³ − {a}³)/3 = <b>{correct}</b>."]
        wrong = [pi_txt(val / 2), pi_txt(b * b - a * a), pi_txt(Fr(b ** 3 - a ** 3, 3)), n(val)]
    else:
        correct, prompt = f"2π ln {n(Fr(b, a))}" if Fr(b, a).denominator == 1 else f"2π ln({n(Fr(b, a))})", f"Hitung ∬<sub>D</sub> dA/(x² + y²), D: {a * a} ≤ x² + y² ≤ {b * b}."
        steps = ["1/r²·r dr = dr/r.", f"∫₀^{{2π}} ∫<sub>{a}</sub><sup>{b}</sup> dr/r dθ = 2π ln({b}/{a}).", f"<b>{correct}</b>."]
        wrong = [f"π ln({n(Fr(b, a))})", f"2π({b} − {a})", f"2π ln({b * b - a * a})", "divergen"]
    return {"prompt": prompt, "correct": correct, "distractors": wrong, "steps": steps, "explanation": "Cincin (annulus): a ≤ r ≤ b."}


@register("ik.silinder_bola", ILK, (3, 4, 5))
def ik_silinder_bola(rng, tier):
    R = rng.randint(1, 3)
    if tier == 3:
        val = Fr(R ** 4, 2)
        return {"prompt": f"Hitung volume di bawah paraboloid z = {R * R} − x² − y² dan di atas bidang z = 0 (koordinat silinder).", "correct": pi_txt(val),
                "distractors": [pi_txt(R ** 4), pi_txt(Fr(R ** 4, 4)), pi_txt(Fr(2 * R ** 3, 3)), n(val)],
                "steps": [f"z = {R * R} − r², bayangan di bidang-xy: r ≤ {R}.", f"∫₀^{{2π}} ∫₀^{R} ({R * R} − r²) r dr dθ = 2π({R ** 4}/2 − {R ** 4}/4).", f"= <b>{pi_txt(val)}</b>."],
                "explanation": "Koordinat silinder: dV = r dz dr dθ."}
    if tier == 4:
        return {"prompt": f"Turunkan volume bola berjari-jari {R} dengan koordinat bola.", "correct": pi_txt(Fr(4 * R ** 3, 3)),
                "distractors": [pi_txt(4 * R * R), pi_txt(Fr(2 * R ** 3, 3)), pi_txt(R ** 3), pi_txt(Fr(4 * R ** 3, 3) * 2)],
                "steps": ["dV = ρ² sin φ dρ dφ dθ.", f"∫₀^{{2π}} ∫₀^π ∫₀^{R} ρ² sin φ dρ dφ dθ = 2π·2·{R ** 3}/3.", f"= <b>{pi_txt(Fr(4 * R ** 3, 3))}</b>."],
                "explanation": "Koordinat bola: dV = ρ² sin φ dρ dφ dθ."}
    val = Fr(4 * R ** 5, 5)
    return {"prompt": f"Hitung ∭<sub>B</sub> (x² + y² + z²) dV, B bola berjari-jari {R} berpusat di asal.", "correct": pi_txt(val),
            "distractors": [pi_txt(Fr(4 * R ** 3, 3)), pi_txt(Fr(R ** 5, 5)), pi_txt(val * 2), pi_txt(Fr(4 * R ** 4, 4))],
            "steps": ["x² + y² + z² = ρ².", f"∫∫∫ ρ²·ρ² sin φ = 2π·2·{R ** 5}/5.", f"= <b>{pi_txt(val)}</b>."], "explanation": "Simetri bola → koordinat bola."}


# ════════════════════════ Medan vektor, divergensi, curl ═══════════════════
@register("kvm.gambar", KVM, (1, 2))
def kvm_gambar(rng, tier):
    cases = [("F = ⟨−y, x⟩", "berputar berlawanan arah jarum jam mengelilingi titik asal"), ("F = ⟨x, y⟩", "memancar keluar dari titik asal (radial)"),
             ("F = ⟨1, 0⟩", "seragam ke arah sumbu-x positif"), ("F = ⟨y, −x⟩", "berputar searah jarum jam")]
    f, d = rng.choice(cases)
    js = {"F = ⟨−y, x⟩": ("-y", "x"), "F = ⟨x, y⟩": ("x", "y"), "F = ⟨1, 0⟩": ("1", "0"), "F = ⟨y, −x⟩": ("y", "-x")}[f]
    els = []
    for i in range(-3, 4):
        for j in range(-3, 4):
            P, Q = js[0].replace("x", str(i)).replace("y", str(j)), js[1].replace("x", str(i)).replace("y", str(j))
            els.append({"type": "segment", "x1": i, "y1": j, "x2": f"{i}+0.25*({P})", "y2": f"{j}+0.25*({Q})", "color": "blue", "arrow": True, "width": 1.6})
    return {"prompt": f"Medan vektor {f} paling tepat digambarkan sebagai …", "correct": d, "distractors": [c[1] for c in cases if c[1] != d] + ["nol di semua titik"],
            "steps": ["Gambar beberapa vektor F(x, y) di titik-titik sampel.", f"<b>{d}</b>."],
            "graphs": [g2d(f"Medan {f}", [-4, 4], [-4, 4], [], els, None, "Setiap panah menunjukkan arah dan besar F di titik itu.")],
            "explanation": "Medan vektor memasangkan vektor ke setiap titik (aliran fluida, gaya, angin)."}


@register("kvm.divergensi", KVM, (1, 2, 3))
def kvm_div(rng, tier):
    a, b, c = nz(rng, -3, 3), nz(rng, -3, 3), nz(rng, -3, 3)
    x, y, z = rng.randint(-2, 2), rng.randint(-2, 2), rng.randint(-2, 2)
    if tier == 1:
        val = a + b
        prompt = f"Hitung div F untuk F = ⟨{n(a)}x, {n(b)}y⟩."
        steps = ["div F = ∂P/∂x + ∂Q/∂y.", f"= {n(a)} + {paren(b)} = <b>{n(val)}</b>."]
    else:
        val = 2 * a * x + b * z + c * x * y
        prompt = f"Hitung div F di ({n(x)}, {n(y)}, {n(z)}) untuk F = ⟨{n(a)}x², {n(b)}yz, {n(c)}xyz⟩."
        steps = ["div F = ∂P/∂x + ∂Q/∂y + ∂R/∂z.", f"= {n(2 * a)}x + {n(b)}z + {n(c)}xy.", f"Di titik itu: <b>{n(val)}</b>."]
    return {"prompt": prompt, "correct": n(val), "distractors": [n(val + 1), n(-val), "0" if val else "1", n(val * 2)], "steps": steps,
            "explanation": "Divergensi = laju ‘keluarnya’ fluida per volume (sumber > 0, sumur < 0)."}


@register("kvm.curl", KVM, (2, 3, 4, 5))
def kvm_curl(rng, tier):
    a, b = nz(rng, -3, 3), nz(rng, -3, 3)
    if tier <= 3:
        val = a - b
        prompt = f"Hitung curl skalar (∂Q/∂x − ∂P/∂y) untuk F = ⟨{n(b)}y, {n(a)}x⟩."
        steps = ["Untuk F = ⟨P, Q⟩: curl = ∂Q/∂x − ∂P/∂y.", f"= {n(a)} − {paren(b)} = <b>{n(val)}</b>."]
        correct = n(val)
        wrong = [n(a + b), n(b - a), "0" if val else "1", n(val * 2)]
    else:
        prompt = f"Hitung curl F untuk F = ⟨0, {terms([(a, 'z')])}, {terms([(b, 'x')])}⟩."
        correct = f"⟨{n(-a)}, {n(-b)}, 0⟩"
        steps = ["curl F = ⟨R<sub>y</sub> − Q<sub>z</sub>, P<sub>z</sub> − R<sub>x</sub>, Q<sub>x</sub> − P<sub>y</sub>⟩.",
                 f"P = 0, Q = {n(a)}z, R = {n(b)}x ⇒ ⟨0 − {paren(a)}, 0 − {paren(b)}, 0 − 0⟩.", f"<b>{correct}</b>."]
        wrong = [f"⟨{n(a)}, {n(b)}, 0⟩", f"⟨{n(-b)}, {n(-a)}, 0⟩", "⟨0, 0, 0⟩", f"⟨0, {n(-a)}, {n(-b)}⟩"]
    return {"prompt": prompt, "correct": correct, "distractors": wrong, "steps": steps, "explanation": "Curl mengukur kecenderungan berputar (rotasi lokal)."}


@register("kvm.konservatif", KVM, (3, 4, 5))
def kvm_kons(rng, tier):
    a, b, c = nz(rng, -3, 3), nz(rng, -3, 3), rng.randint(-3, 3)
    cons = rng.random() < 0.6
    P = terms([(2 * a, "x"), (c, "y")])
    Q = terms([(c if cons else c + 1, "x"), (2 * b, "y")])
    if cons:
        correct = f"konservatif, f = {n(a)}x² + {n(c)}xy + {n(b)}y²".replace("+ −", "− ")
        why = f"P<sub>y</sub> = {n(c)} = Q<sub>x</sub>; integralkan: f = {n(a)}x² + {n(c)}xy + {n(b)}y² (+ konstanta)."
    else:
        correct = "tidak konservatif"
        why = f"P<sub>y</sub> = {n(c)} ≠ Q<sub>x</sub> = {n(c + 1)}."
    return {"prompt": f"Apakah F = ⟨{P}, {Q}⟩ konservatif? Jika ya, tentukan fungsi potensialnya.", "correct": correct,
            "distractors": ["tidak konservatif" if cons else f"konservatif, f = {n(a)}x² + {n(c)}xy + {n(b)}y²".replace("+ −", "− "),
                            f"konservatif, f = {n(2 * a)}x² + {n(2 * b)}y²".replace("+ −", "− "), f"konservatif, f = {n(a)}x² + {n(b)}y²".replace("+ −", "− "), "konservatif, f = 0"],
            "steps": ["F = ⟨P, Q⟩ (di daerah terhubung sederhana) konservatif ⇔ ∂P/∂y = ∂Q/∂x.", why, f"<b>{correct}</b>."],
            "explanation": "Medan konservatif = gradien suatu fungsi potensial."}


# ════════════════════════ Integral garis & Green ═══════════════════════════
@register("kvg.param", KVG, (1, 2))
def kvg_param(rng, tier):
    A = (rng.randint(-3, 3), rng.randint(-3, 3))
    B = (rng.randint(-3, 5), rng.randint(-3, 5))
    while B == A:
        B = (B[0] + 1, B[1])
    d = (B[0] - A[0], B[1] - A[1])
    correct = f"r(t) = ⟨{n(A[0])} + {n(d[0])}t, {n(A[1])} + {n(d[1])}t⟩, 0 ≤ t ≤ 1".replace("+ −", "− ")
    return {"prompt": f"Parametrisasi ruas garis dari A({n(A[0])}, {n(A[1])}) ke B({n(B[0])}, {n(B[1])}) adalah …", "correct": correct,
            "distractors": [f"r(t) = ⟨{n(B[0])} + {n(d[0])}t, {n(B[1])} + {n(d[1])}t⟩, 0 ≤ t ≤ 1".replace("+ −", "− "),
                            f"r(t) = ⟨{n(A[0])} + {n(B[0])}t, {n(A[1])} + {n(B[1])}t⟩, 0 ≤ t ≤ 1".replace("+ −", "− "),
                            f"r(t) = ⟨{n(d[0])}t, {n(d[1])}t⟩, 0 ≤ t ≤ 1", f"r(t) = ⟨{n(A[0])} + {n(d[0])}t, {n(A[1])} + {n(d[1])}t⟩, 0 ≤ t ≤ 2".replace("+ −", "− ")],
            "steps": ["r(t) = A + t(B − A), 0 ≤ t ≤ 1.", f"B − A = ⟨{n(d[0])}, {n(d[1])}⟩ ⇒ <b>{correct}</b>."], "explanation": "Parametrisasi adalah langkah pertama integral garis."}


@register("kvg.skalar", KVG, (1, 2, 3))
def kvg_skalar(rng, tier):
    r = rng.randint(1, 4)
    if tier <= 2:
        c = rng.randint(1, 5)
        val = 2 * c * r
        return {"prompt": f"Hitung ∫<sub>C</sub> {c} ds dengan C lingkaran x² + y² = {r * r}.", "correct": pi_txt(val),
                "distractors": [pi_txt(c * r), pi_txt(c * r * r), n(val), pi_txt(val * 2)],
                "steps": ["∫ c ds = c × panjang kurva.", f"Keliling 2π·{r} ⇒ <b>{pi_txt(val)}</b>."], "explanation": "∫_C f ds dengan f konstan = f × panjang C."}
    return {"prompt": f"Hitung ∫<sub>C</sub> (x² + y²) ds dengan C lingkaran berjari-jari {r} berpusat di asal.", "correct": pi_txt(2 * r ** 3),
            "distractors": [pi_txt(2 * r * r), pi_txt(r ** 3), pi_txt(Fr(4 * r ** 3, 3)), n(2 * r ** 3)],
            "steps": [f"Pada C: x² + y² = {r * r} dan ds = {r} dt.", f"∫₀^{{2π}} {r * r}·{r} dt = <b>{pi_txt(2 * r ** 3)}</b>."], "explanation": "ds = |r′(t)| dt."}


@register("kvg.kerja", KVG, (2, 3, 4))
def kvg_kerja(rng, tier):
    a = nz(rng, -3, 3)
    x1, y1 = rng.randint(1, 3), rng.randint(1, 3)
    val = a * x1 * y1
    return {"prompt": f"Hitung kerja ∫<sub>C</sub> F·dr dengan F = ⟨{n(a)}y, {n(a)}x⟩ sepanjang kurva r(t) = ⟨{x1}t, {y1}t²⟩, 0 ≤ t ≤ 1.", "correct": n(val),
            "distractors": [n(2 * val), "0", n(-val), n(a * (x1 + y1))],
            "steps": [f"Cara langsung: F(r(t))·r′(t) = {n(a)}·{y1}t²·{x1} + {n(a)}·{x1}t·{2 * y1}t = {n(3 * a * x1 * y1)}t²; ∫₀¹ = {n(val)}.",
                      f"Atau: F = ∇({n(a)}xy) konservatif ⇒ kerja = f(akhir) − f(awal) = {n(a)}·{x1}·{y1} − 0.", f"<b>{n(val)}</b>."],
            "explanation": "Kerja = ∫ F·dr; untuk medan konservatif hanya bergantung ujung-ujungnya."}


@register("kvg.green", KVG, (3, 4, 5))
def kvg_green(rng, tier):
    k = rng.randint(1, 3)
    if tier <= 4:
        r = rng.randint(1, 4)
        val = 2 * k * r * r
        return {"prompt": f"Gunakan Teorema Green untuk ∮<sub>C</sub> (−{k if k > 1 else ''}y dx + {k if k > 1 else ''}x dy), C lingkaran berjari-jari {r} berlawanan arah jarum jam.",
                "correct": pi_txt(val), "distractors": [pi_txt(k * r * r), pi_txt(val * 2), "0", pi_txt(2 * k * r)],
                "steps": ["Green: ∮ P dx + Q dy = ∬ (Q<sub>x</sub> − P<sub>y</sub>) dA.", f"Q<sub>x</sub> − P<sub>y</sub> = {k} + {k} = {2 * k}.", f"{2 * k} × luas (π{r * r}) = <b>{pi_txt(val)}</b>."],
                "explanation": "Teorema Green menghubungkan integral garis tertutup dengan integral ganda (luas = ½∮ x dy − y dx)."}
    a, b = rng.randint(1, 4), rng.randint(1, 4)
    # P = −y², Q = x² pada [0, a] × [0, b]: Q_x − P_y = 2x + 2y ⇒ ∬ = a²b + ab²
    val = a * a * b + a * b * b
    return {"prompt": f"Hitung ∮<sub>C</sub> (−y² dx + x² dy) dengan C batas persegi panjang [0, {a}] × [0, {b}] (berlawanan jarum jam).", "correct": n(val),
            "distractors": [n(a * b), n(2 * a * b), "0", n(Fr(val, 2))],
            "steps": ["Q<sub>x</sub> − P<sub>y</sub> = 2x + 2y.", f"∬ (2x + 2y) dA = {a}²·{b} + {a}·{b}² = <b>{val}</b>."], "explanation": "Green mengubah 4 integral garis menjadi satu integral ganda."}


@register("kvg.fundamental", KVG, (4, 5))
def kvg_fundamental(rng, tier):
    A = (rng.randint(-2, 2), rng.randint(-2, 2))
    B = (rng.randint(-2, 3), rng.randint(-2, 3))
    f = lambda p: p[0] ** 2 * p[1] + p[1] ** 3
    val = f(B) - f(A)
    return {"prompt": f"Hitung ∫<sub>C</sub> ∇f·dr untuk f(x, y) = x²y + y³, C sembarang kurva dari ({n(A[0])}, {n(A[1])}) ke ({n(B[0])}, {n(B[1])}).", "correct": n(val),
            "distractors": [n(-val), n(f(B)), "0", "bergantung pada lintasan"],
            "steps": ["Teorema fundamental integral garis: ∫ ∇f·dr = f(B) − f(A) (tak bergantung lintasan).", f"f(B) = {n(f(B))}, f(A) = {n(f(A))}.", f"<b>{n(val)}</b>."],
            "explanation": "Kurva tertutup ⇒ ∮ ∇f·dr = 0."}


# ════════════════════════ Fungsi Gamma, Beta ═══════════════════════════════
@register("fg.gamma", FKG, (1, 2, 3, 4, 5))
def fg_gamma(rng, tier):
    if tier <= 2:
        m = rng.randint(2, 7)
        return {"prompt": f"Hitung Γ({m}) dengan Γ(x) = ∫<sub>0</sub><sup>∞</sup> t<sup>x−1</sup>e<sup>−t</sup> dt.", "correct": n(math.factorial(m - 1)),
                "distractors": [n(math.factorial(m)), n(m - 1), n(math.factorial(m - 2)), n(m * m)],
                "steps": ["Integral parsial: Γ(x + 1) = xΓ(x), Γ(1) = 1.", f"Γ({m}) = ({m} − 1)! = <b>{math.factorial(m - 1)}</b>."],
                "explanation": "Gamma memperluas faktorial: Γ(n) = (n − 1)!."}
    k = {3: 1, 4: 2, 5: 3}[tier]
    # Γ(k + 1/2) = (2k)!√π / (4^k k!)
    coef = Fr(math.factorial(2 * k), 4 ** k * math.factorial(k))
    correct = f"{n(coef)}√π"
    return {"prompt": f"Hitung Γ({k} + 1/2) = Γ({n(Fr(2 * k + 1, 2))}) jika Γ(1/2) = √π.", "correct": correct,
            "distractors": [f"{n(coef * 2)}√π", "√π", f"{n(Fr(math.factorial(k)))}√π", f"{n(coef)}π"],
            "steps": ["Γ(x + 1) = xΓ(x) berulang dari Γ(1/2) = √π.", " · ".join(f"{n(Fr(2 * j + 1, 2))}" for j in range(k)) + " · √π.", f"= <b>{correct}</b>."],
            "explanation": "Γ(1/2) = √π berasal dari integral Gauss."}


@register("fg.erf", FKG, (1, 2))
def fg_erf(rng, tier):
    if tier == 1:
        return {"prompt": "Untuk fungsi galat erf(x) = (2/√π)∫<sub>0</sub><sup>x</sup> e<sup>−t²</sup> dt, berapa lim<sub>x→∞</sub> erf(x)?", "correct": "1",
                "distractors": ["0", "√π", "∞", "1/2"],
                "steps": ["∫₀^∞ e<sup>−t²</sup> dt = √π/2.", "(2/√π)·(√π/2) = <b>1</b>."], "explanation": "erf dipakai di statistika (distribusi normal) dan difusi panas (FT)."}
    return {"prompt": "Hitung ∫<sub>−∞</sub><sup>∞</sup> e<sup>−x²/2</sup> dx.", "correct": "√(2π)", "distractors": ["√π", "2π", "1", "π/2"],
            "steps": ["Substitusi x = √2·u: dx = √2 du.", "√2·∫ e<sup>−u²</sup> du = √2·√π = <b>√(2π)</b> (konstanta normalisasi distribusi normal)."],
            "explanation": "Integral Gauss dalam berbagai skala."}


@register("fg.integral_gamma", FKG, (2, 3, 4))
def fg_integral(rng, tier):
    m, a = rng.randint(1, 4), rng.randint(1, 3)
    val = Fr(math.factorial(m), a ** (m + 1))
    return {"prompt": f"Hitung ∫<sub>0</sub><sup>∞</sup> x{sup(m) if m > 1 else ''}e<sup>−{a if a > 1 else ''}x</sup> dx dengan fungsi Gamma.", "correct": n(val),
            "distractors": [n(math.factorial(m)), n(Fr(math.factorial(m), a ** m)), n(Fr(1, a)), n(val * 2)],
            "steps": [f"Substitusi u = {a}x: ∫ = (1/{a}{sup(m + 1)})∫₀^∞ u{sup(m)}e⁻ᵘ du = Γ({m + 1})/{a ** (m + 1)}.", f"= {m}!/{a ** (m + 1)} = <b>{n(val)}</b>."],
            "explanation": "∫₀^∞ xⁿe^{−ax} dx = n!/a^{n+1}."}


@register("fg.beta", FKG, (3, 4, 5))
def fg_beta(rng, tier):
    p, q = rng.randint(1, 4), rng.randint(1, 4)
    val = Fr(math.factorial(p) * math.factorial(q), math.factorial(p + q + 1))
    return {"prompt": f"Hitung ∫<sub>0</sub><sup>1</sup> x{sup(p) if p > 1 else ''}(1 − x){sup(q) if q > 1 else ''} dx dengan fungsi Beta.", "correct": n(val),
            "distractors": [n(Fr(1, p + q + 1)), n(Fr(math.factorial(p + q), math.factorial(p + q + 1))), n(val * 2), n(Fr(1, (p + 1) * (q + 1)))],
            "steps": ["B(a, b) = ∫₀¹ x<sup>a−1</sup>(1 − x)<sup>b−1</sup> dx = Γ(a)Γ(b)/Γ(a + b).", f"a = {p + 1}, b = {q + 1}: {p}!·{q}!/{p + q + 1}!.", f"= <b>{n(val)}</b>."],
            "explanation": "Fungsi Beta: dasar distribusi Beta (statistika Bayes)."}


# ════════════════════════ Dasar analisis real ══════════════════════════════
@register("fa.archimedes", FKA, (1, 2))
def fa_arch(rng, tier):
    k = rng.choice([7, 10, 25, 100, 3, 1000])
    eps = Fr(1, k) if tier == 1 else Fr(2, k)
    N = int(1 / eps) + 1
    return {"prompt": f"Berapa bilangan asli n terkecil sehingga 1/n &lt; {n(eps)}?", "correct": str(N), "distractors": [str(N - 1), str(N + 1), str(k), str(2 * N)],
            "steps": [f"1/n &lt; {n(eps)} ⇔ n &gt; {n(1 / eps)}.", f"n terkecil = <b>{N}</b> (sifat Archimedes: selalu ada n seperti ini)."],
            "explanation": "Sifat Archimedes menjadi dasar setiap bukti ε–N."}


@register("fa.sup", FKA, (1, 2, 3))
def fa_sup(rng, tier):
    k = rng.randint(1, 5)
    cases = [(f"{{{k} − 1/n : n ∈ ℕ}}", f"sup = {k}, inf = {n(k - 1)}", f"{k} − 1/n naik mendekati {k} (tak tercapai), terkecil saat n = 1: {k - 1}."),
             ("{(−1)ⁿ + 1/n : n ∈ ℕ}", "sup = 3/2, inf = −1", "n = 2 memberi 3/2 (terbesar); n ganjil memberi −1 + 1/n yang turun ke −1 (tak tercapai)."),
             (f"({n(-k)}, {k}]", f"sup = {k}, inf = {n(-k)}", "sup tercapai (anggota), inf tidak tercapai."),
             (f"{{x : x² &lt; {k * k}}}", f"sup = {k}, inf = {n(-k)}", f"himpunan = ({n(-k)}, {k}).")]
    s, ans, why = rng.choice(cases[:3] if tier == 1 else cases)
    return {"prompt": f"Tentukan supremum dan infimum himpunan {s}.", "correct": ans, "distractors": [c[1] for c in cases if c[1] != ans] + ["sup dan inf tidak ada"],
            "steps": ["sup = batas atas terkecil, inf = batas bawah terbesar (tidak harus anggota himpunan).", why, f"<b>{ans}</b>."],
            "explanation": "Aksioma kelengkapan: setiap himpunan tak kosong yang terbatas di atas punya supremum di ℝ."}


@register("fa.eps_n", FKA, (2, 3, 4, 5))
def fa_eps(rng, tier):
    a, c = rng.randint(1, 4), rng.randint(1, 3)
    b = rng.randint(1, 5)
    # aₙ = (a n + b)/(c n) → a/c ; |aₙ − a/c| = b/(c n) < ε ⇔ n > b/(c ε)
    eps = Fr(1, rng.choice([10, 100, 20, 50]))
    bound = Fr(b) / (c * eps)
    N = math.floor(bound) + 1
    return {"prompt": f"aₙ = ({a}n + {b})/({c if c > 1 else ''}n) → {n(Fr(a, c))}. Untuk ε = {n(eps)}, tentukan N terkecil agar |aₙ − {n(Fr(a, c))}| &lt; ε untuk semua n ≥ N.",
            "correct": str(N), "distractors": [str(N - 1), str(N + 1), str(int(1 / eps)), str(N * 2)],
            "steps": [f"|aₙ − {n(Fr(a, c))}| = {b}/({c}n).", f"{b}/({c}n) &lt; {n(eps)} ⇔ n &gt; {n(bound)}.", f"N = <b>{N}</b>."],
            "explanation": "Definisi limit barisan: ∀ε > 0 ∃N ∀n ≥ N: |aₙ − L| < ε."}


@register("fa.pernyataan", FKA, (3, 4, 5))
def fa_pernyataan(rng, tier):
    cases = [("Setiap barisan konvergen pasti terbatas.", "benar"), ("Setiap barisan terbatas pasti konvergen.", "salah (contoh (−1)ⁿ)"),
             ("Setiap barisan terbatas punya sub-barisan konvergen.", "benar (Bolzano–Weierstrass)"), ("Barisan Cauchy di ℝ pasti konvergen.", "benar (kelengkapan ℝ)"),
             ("Barisan Cauchy di ℚ pasti konvergen di ℚ.", "salah (contoh pendekatan desimal √2)"), ("Barisan monoton naik pasti konvergen.", "salah (contoh aₙ = n)")]
    s, ans = rng.choice(cases)
    opts = ["benar", "salah (contoh (−1)ⁿ)", "benar (Bolzano–Weierstrass)", "benar (kelengkapan ℝ)", "salah (contoh pendekatan desimal √2)", "salah (contoh aₙ = n)"]
    return {"prompt": f"Benar atau salah: “{s}”", "correct": ans, "distractors": [o for o in opts if o != ans],
            "steps": ["Periksa definisi, lalu cari bukti singkat atau contoh penyangkal.", f"<b>{ans}</b>."],
            "explanation": "Analisis real menuntut bukti atau contoh penyangkal, bukan intuisi grafik."}
