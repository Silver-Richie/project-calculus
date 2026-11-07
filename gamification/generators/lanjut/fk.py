"""
Topik TERAPAN khusus Fasilkom (Level Utama 4): norma & kerugian, gradient descent, peluang & Monte Carlo,
medan vektor dalam simulasi, analisis asimtotik.
Rujukan: Stewart §12.2–12.3, §14.6, §15.7 (probabilitas); Strang (MIT) §13–14; materi khusus Fasilkom (berkas 2 & 6).
"""

from fractions import Fraction as Fr
import math

from .. import register
from ..fmt import MINUS, fac, n, paren, sup, terms
from ..graphs import fn, g2d, param, pt, readout
from ..precalc.common import distinct, nz

NR, GD, PL, SM, AS = "kl-fk-norma", "kl-fk-gd", "kl-fk-peluang", "kl-fk-simulasi", "kl-fk-asimtotik"


# ════════════════════════ Norma, jarak, fungsi kerugian ═══════════════════
@register("fkn.norma", NR, (1, 2, 3))
def fkn_norma(rng, tier):
    v = rng.choice([(3, 4, 0, 5), (2, 3, 6, 7), (1, 4, 8, 9), (6, 8, 0, 10), (2, 6, 9, 11)])
    s = [rng.choice([1, -1]) for _ in range(3)]
    x = [v[i] * s[i] for i in range(3)]
    kind = "L2" if tier == 1 else rng.choice(["L2", "L1", "L∞"])
    val = {"L2": v[3], "L1": sum(v[:3]), "L∞": max(v[:3])}[kind]
    return {"prompt": f"Hitung norma {kind} dari vektor x = ({', '.join(n(t) for t in x)}).", "correct": n(val),
            "distractors": [n(v[3]) if kind != "L2" else n(sum(v[:3])), n(max(v[:3])) if kind != "L∞" else n(v[3] ** 2), n(sum(x)), n(val + 1)],
            "steps": ["L2 = √(Σxᵢ²), L1 = Σ|xᵢ|, L∞ = max|xᵢ|.", f"‖x‖<sub>{kind[1:]}</sub> = <b>{val}</b>."],
            "explanation": "Norma mengukur ‘besar’ vektor — dipakai sebagai regularisasi (L1/L2) di machine learning."}


@register("fkn.jarak", NR, (1, 2))
def fkn_jarak(rng, tier):
    a, b, h = rng.choice([(3, 4, 5), (6, 8, 10), (5, 12, 13), (8, 15, 17)])
    p = (rng.randint(-5, 5), rng.randint(-5, 5))
    q = (p[0] + a * rng.choice([1, -1]), p[1] + b * rng.choice([1, -1]))
    pt_ = lambda t: f"({n(t[0])}, {n(t[1])})"
    return {"prompt": f"Dalam algoritma k-NN, hitung jarak Euclid antara titik data {pt_(p)} dan {pt_(q)}.", "correct": n(h),
            "distractors": [n(a + b), n(h * h), n(max(a, b)), n(h + 1)],
            "steps": ["d = √((x₂ − x₁)² + (y₂ − y₁)²).", f"√({a * a} + {b * b}) = <b>{h}</b>. (Jarak Manhattan = {a + b}.)"], "explanation": "Jarak Euclid = norma L2 selisih."}


@register("fkn.mse", NR, (2, 3, 4, 5))
def fkn_mse(rng, tier):
    m = 3 if tier == 2 else 4
    y = [rng.randint(0, 9) for _ in range(m)]
    e = [rng.randint(-3, 3) for _ in range(m)]
    yh = [y[i] + e[i] for i in range(m)]
    val = Fr(sum(t * t for t in e), m)
    return {"prompt": f"Label y = {y} dan prediksi ŷ = {yh}. Hitung Mean Squared Error.", "correct": n(val),
            "distractors": [n(Fr(sum(abs(t) for t in e), m)), n(sum(t * t for t in e)), n(Fr(sum(e), m)), n(val + 1)],
            "steps": ["MSE = (1/m)Σ(ŷᵢ − yᵢ)².", f"Galat: {e}; kuadrat dijumlahkan = {sum(t * t for t in e)}.", f"MSE = {sum(t * t for t in e)}/{m} = <b>{n(val)}</b>."],
            "explanation": "MSE adalah fungsi kerugian (loss) regresi; meminimalkannya = kalkulus peubah banyak."}


@register("fkn.kosinus", NR, (3, 4, 5))
def fkn_kosinus(rng, tier):
    a = rng.choice([(3, 4), (4, 3), (0, 5), (5, 0)])
    b = rng.choice([(5, 12), (12, 5), (0, 13), (13, 0), (-5, 12)])
    val = Fr(a[0] * b[0] + a[1] * b[1], 5 * 13)
    return {"prompt": f"Hitung kemiripan kosinus vektor dokumen u = ⟨{n(a[0])}, {n(a[1])}⟩ dan v = ⟨{n(b[0])}, {n(b[1])}⟩.", "correct": n(val),
            "distractors": [n(a[0] * b[0] + a[1] * b[1]), n(-val), n(Fr(a[0] * b[1] + a[1] * b[0], 65)), "1"],
            "steps": ["cos θ = u·v/(‖u‖‖v‖).", f"u·v = {a[0] * b[0] + a[1] * b[1]}, ‖u‖ = 5, ‖v‖ = 13.", f"= <b>{n(val)}</b>."],
            "explanation": "Kemiripan kosinus dipakai di temu kembali informasi & embedding."}


# ════════════════════════ Gradient descent & backpropagation ══════════════
@register("fkg.gd1", GD, (1, 2, 3))
def fkg_gd1(rng, tier):
    a = rng.randint(-5, 5)
    x0 = rng.randint(-5, 8)
    eta = Fr(1, rng.choice([10, 4, 5])) if tier < 3 else Fr(rng.choice([1, 3]), 10)
    steps_n = 1 if tier == 1 else 2
    x = Fr(x0)
    lines = []
    for _ in range(steps_n):
        g = 2 * (x - a)
        nxt = x - eta * g
        lines.append(f"x = {n(x)}: f′ = 2({n(x)} − {paren(a)}) = {n(g)} ⇒ x ← {n(x)} − {n(eta)}·{paren(g)} = {n(nxt)}")
        x = nxt
    return {"prompt": f"Kerugian f(x) = {fac(a) if a else 'x'}² diminimalkan dengan gradient descent, laju belajar η = {n(eta)}, mulai x₀ = {x0}. Nilai x setelah {steps_n} langkah?",
            "correct": n(x), "distractors": [n(Fr(a)), n(x0 - eta * 2 * (x0 - a) * steps_n), n(x + eta), n(2 * x - x0)],
            "steps": ["Aturan GD: x ← x − η f′(x).", *lines, f"<b>{n(x)}</b> (bergerak menuju minimum x = {a})."],
            "graphs": [g2d("Langkah gradient descent", [a - 8, a + 10], [-5, 120], [param("et", "η", 0.05, 1.05, 0.05, float(eta), "η")],
                           [fn(f"(x-({a}))**2", "blue", "f(x)"),
                            {"type": "iter", "id": "G", "init": {"x": x0}, "update": {"x": f"x-et*2*(x-({a}))"}, "steps": 8, "px": "x", "py": f"(x-({a}))**2", "color": "red"}],
                           [readout("x setelah 8 langkah", f"{a}+({x0}-({a}))*pow(1-2*et,8)", 4)], "η > 1 membuat langkah ‘melompati’ minimum dan divergen.")],
            "explanation": "Soal FK-M1 (berkas Fasilkom) adalah versi tetapnya."}


@register("fkg.gd2", GD, (2, 3, 4))
def fkg_gd2(rng, tier):
    c = rng.randint(2, 5)
    x0, y0 = rng.randint(-4, 4), rng.randint(-3, 3)
    eta = Fr(1, 10)
    x1, y1 = x0 - eta * 2 * x0, y0 - eta * 2 * c * y0
    correct = f"({n(x1)}, {n(y1)})"
    return {"prompt": f"f(x, y) = x² + {c}y². Satu langkah gradient descent dengan η = 0,1 dari ({n(x0)}, {n(y0)}) menghasilkan …", "correct": correct,
            "distractors": [f"({n(x0 + eta * 2 * x0)}, {n(y0 + eta * 2 * c * y0)})", f"({n(x1)}, {n(y0 - eta * 2 * y0)})", f"({n(x0 - eta * 2)}, {n(y0 - eta * 2 * c)})", "(0, 0)"],
            "steps": [f"∇f = ⟨2x, {2 * c}y⟩ = ⟨{n(2 * x0)}, {n(2 * c * y0)}⟩.", f"(x, y) ← (x, y) − 0,1·∇f = <b>{correct}</b>.",
                      "Arah y menyusut lebih cepat karena kurva tingkat (elips) lebih curam di arah y — penyebab ‘zig-zag’ (FK-H1)."],
            "explanation": "GD bergerak berlawanan arah gradien, tegak lurus kurva tingkat."}


@register("fkg.sigmoid", GD, (3, 4, 5))
def fkg_sigmoid(rng, tier):
    if tier == 3:
        p = rng.choice([Fr(1, 2), Fr(1, 4), Fr(3, 4), Fr(1, 5), Fr(9, 10)])
        val = p * (1 - p)
        return {"prompt": f"Pada neuron sigmoid σ(z) = 1/(1 + e<sup>−z</sup>), keluaran σ(z) = {n(p)}. Berapa σ′(z)?", "correct": n(val),
                "distractors": [n(p), n(1 - p), n(p * p), n(Fr(1, 4))],
                "steps": ["σ′(z) = σ(z)(1 − σ(z)) (FK-S1).", f"= {n(p)}·{n(1 - p)} = <b>{n(val)}</b>."], "explanation": "Turunan sigmoid dihitung dari keluarannya sendiri — efisien untuk backpropagation."}
    x, y = rng.randint(1, 3), rng.choice([0, 1])
    # L = (σ(wx) − y)², w = 0 ⇒ σ = 1/2, σ′ = 1/4 ⇒ dL/dw = 2(1/2 − y)(1/4)x
    val = 2 * (Fr(1, 2) - y) * Fr(1, 4) * x
    return {"prompt": f"Neuron ŷ = σ(wx) dengan kerugian L = (ŷ − y)². Untuk x = {x}, y = {y}, w = 0, hitung ∂L/∂w (backpropagation).", "correct": n(val),
            "distractors": [n(-val), n(2 * (Fr(1, 2) - y) * x), n(Fr(x, 4)), "0"],
            "steps": ["Rantai: ∂L/∂w = 2(ŷ − y)·σ′(wx)·x.", f"w = 0 ⇒ ŷ = 1/2, σ′ = 1/4.", f"= 2({n(Fr(1, 2) - y)})(1/4)({x}) = <b>{n(val)}</b>."],
            "explanation": "Backpropagation = aturan rantai lapis demi lapis."}


@register("fkg.konvergensi", GD, (4, 5))
def fkg_konv(rng, tier):
    a = rng.randint(1, 10)
    if tier == 4:
        return {"prompt": f"Gradient descent pada f(x) = {a}x²/2 konvergen untuk laju belajar η pada interval …", "correct": f"0 &lt; η &lt; {n(Fr(2, a))}",
                "distractors": [f"0 &lt; η &lt; {n(Fr(1, a))}", f"0 &lt; η &lt; {2 * a}", "semua η &gt; 0", f"η &gt; {n(Fr(2, a))}"],
                "steps": [f"x ← x − η{a}x = (1 − {a}η)x.", f"Konvergen ⇔ |1 − {a}η| &lt; 1 ⇔ 0 &lt; η &lt; 2/{a}.", f"<b>0 &lt; η &lt; {n(Fr(2, a))}</b>."],
                "explanation": "Laju belajar terlalu besar ⇒ divergen (osilasi membesar)."}
    return {"prompt": f"Untuk f(x) = {a}x²/2, laju belajar η berapa yang membuat gradient descent mencapai minimum dalam SATU langkah dari titik mana pun?",
            "correct": f"η = {n(Fr(1, a))}", "distractors": [f"η = {n(Fr(2, a))}", f"η = {a}", "η = 1", "tidak ada"],
            "steps": [f"x₁ = (1 − {a}η)x₀ = 0 untuk semua x₀ ⇔ {a}η = 1.", f"<b>η = {n(Fr(1, a))}</b> = 1/f″ — inilah ide metode Newton."],
            "explanation": "η optimal = 1/kelengkungan; Hessian berperan pada kasus banyak variabel."}


@register("fkg.softmax", GD, (1, 2))
def fkg_softmax(rng, tier):
    w = rng.sample([1, 2, 3, 4, 5, 6], 3)
    total = sum(w)
    i = rng.randrange(3)
    val = Fr(w[i], total)
    zs = ", ".join("0" if t == 1 else f"ln {t}" for t in w)
    return {"prompt": f"Logit z = ({zs}). Berapa probabilitas softmax kelas ke-{i + 1}?", "correct": n(val),
            "distractors": [n(Fr(1, 3)), n(Fr(w[i], max(w))), n(1 - val), n(Fr(w[(i + 1) % 3], total))],
            "steps": ["softmax(z)ᵢ = e<sup>zᵢ</sup>/Σⱼ e<sup>zⱼ</sup>.", f"e<sup>z</sup> = ({', '.join(str(t) for t in w)}), jumlah {total}.", f"pᵢ = {w[i]}/{total} = <b>{n(val)}</b> (FK-H2)."],
            "explanation": "Softmax mengubah skor menjadi distribusi peluang."}


# ════════════════════════ Peluang gabungan & Monte Carlo ══════════════════
@register("fkp.ekspektasi", PL, (1, 2))
def fkp_eksp(rng, tier):
    a, b = sorted(distinct(rng, 0, 12, 2))
    if tier == 1:
        return {"prompt": f"Waktu respons server X berdistribusi seragam pada [{a}, {b}] ms. Berapa E[X]?", "correct": f"{n(Fr(a + b, 2))} ms",
                "distractors": [f"{n(Fr(b - a, 2))} ms", f"{b} ms", f"{n(Fr(b * b - a * a, 2))} ms", f"{a + b} ms"],
                "steps": ["f(x) = 1/(b − a) di [a, b].", f"E[X] = ∫ x f(x) dx = (a + b)/2 = <b>{n(Fr(a + b, 2))} ms</b>."], "explanation": "Nilai harapan = integral x·f(x)."}
    val = Fr((b - a) ** 2, 12)
    return {"prompt": f"X seragam pada [{a}, {b}]. Hitung Var(X) = E[X²] − (E[X])².", "correct": n(val),
            "distractors": [n(Fr((b - a) ** 2, 4)), n(Fr(b - a, 12)), n(Fr((b - a) ** 2, 6)), n(Fr(a + b, 2))],
            "steps": [f"E[X²] = (a² + ab + b²)/3, E[X] = (a + b)/2.", f"Var = (b − a)²/12 = <b>{n(val)}</b>."], "explanation": "Variansi distribusi seragam."}


@register("fkp.gabungan", PL, (1, 2, 3))
def fkp_gab(rng, tier):
    if tier <= 2:
        k = 4
        p = Fr(1, 16)
        return {"prompt": "f(x, y) = kxy pada [0, 1]² adalah kepadatan gabungan. Tentukan k dan P(X ≤ 1/2, Y ≤ 1/2).", "correct": f"k = {k}, P = {n(p)}",
                "distractors": [f"k = 1, P = 1/4", f"k = 4, P = 1/4", f"k = 2, P = 1/16", f"k = 4, P = 1/8"],
                "steps": ["∬ kxy dA = k·(1/2)(1/2) = 1 ⇒ k = 4.", "P = ∫₀^{1/2}∫₀^{1/2} 4xy dy dx = 4·(1/8)(1/8).", f"<b>k = 4, P = 1/16</b>."],
                "explanation": "Peluang gabungan = integral ganda kepadatan."}
    a = rng.randint(1, 4)
    val = Fr(1, 2)
    return {"prompt": f"X, Y saling bebas dan masing-masing seragam pada [0, {a}]. Hitung P(X &lt; Y).", "correct": n(val),
            "distractors": ["1/4", "1/3", n(Fr(1, a)), "1"],
            "steps": [f"Kepadatan gabungan 1/{a * a} pada persegi [0, {a}]².", "Daerah X &lt; Y adalah setengah persegi (simetri).", "<b>1/2</b>."],
            "explanation": "Peluang = luas daerah × kepadatan (kasus seragam)."}


@register("fkp.eksponensial", PL, (2, 3, 4, 5))
def fkp_expo(rng, tier):
    lam = rng.choice([Fr(1, 2), Fr(1, 5), Fr(2), Fr(1, 10)])
    t = rng.randint(1, 4)
    if tier == 2:
        return {"prompt": f"Waktu antar-kedatangan paket berdistribusi eksponensial f(x) = λe<sup>−λx</sup>, λ = {n(lam)}. Berapa rata-ratanya?", "correct": n(1 / lam),
                "distractors": [n(lam), n(1 / lam / 2), n(1 / lam ** 2), "1"],
                "steps": ["E[X] = ∫₀^∞ x λe<sup>−λx</sup> dx = 1/λ (parsial).", f"= <b>{n(1 / lam)}</b>."], "explanation": "Model antrian & jaringan (Fasilkom)."}
    k = lam * t
    correct = f"e{sup(-k)}" if k.denominator == 1 else f"e<sup>{MINUS}{n(k)}</sup>"
    return {"prompt": f"X eksponensial dengan λ = {n(lam)}. Hitung P(X &gt; {t}).", "correct": correct,
            "distractors": [f"1 − {correct}", f"e<sup>{MINUS}{t}</sup>", n(lam * t), f"e<sup>{MINUS}{n(t / lam)}</sup>"],
            "steps": [f"P(X &gt; t) = ∫ₜ^∞ λe<sup>−λx</sup> dx = e<sup>−λt</sup>.", f"= <b>{correct}</b>. (Sifat tanpa memori: P(X &gt; s + t | X &gt; s) = P(X &gt; t).)"],
            "explanation": "Fungsi survival distribusi eksponensial."}


@register("fkp.monte_carlo", PL, (3, 4, 5))
def fkp_mc(rng, tier):
    if tier <= 4:
        N = rng.choice([1000, 2000, 4000, 10000])
        k = round(N * math.pi / 4) + rng.randint(-20, 20)
        est = Fr(4 * k, N)
        return {"prompt": f"Dari {N} titik acak seragam di persegi [0, 1]², sebanyak {k} jatuh di dalam seperempat lingkaran x² + y² ≤ 1. Taksiran π?", "correct": n(float(est)),
                "distractors": [n(float(Fr(k, N))), n(float(Fr(2 * k, N))), n(float(Fr(4 * N, k))), "3,14159"],
                "steps": ["Peluang titik di dalam = luas seperempat lingkaran = π/4.", f"π ≈ 4·{k}/{N} = <b>{n(float(est))}</b>."],
                "graphs": [g2d("Monte Carlo: titik di dalam seperempat lingkaran", [0, 1], [0, 1], [], [{"type": "param", "t": [0, "pi/2"], "x": "cos(t)", "y": "sin(t)", "color": "red"},
                                                                                                    {"type": "fill", "upper": "sqrt(1-x*x)", "from": 0, "to": 1, "color": "amber"}], None,
                               "Rasio luas berwarna terhadap persegi = π/4.")],
                "explanation": "Integrasi Monte Carlo: integral ≈ rata-rata sampel acak."}
    m = rng.choice([2, 3, 10])
    return {"prompt": f"Galat integrasi Monte Carlo sebanding dengan 1/√N. Agar galat menjadi 1/{m} kali semula, banyak sampel harus dikali …", "correct": str(m * m),
            "distractors": [str(m), str(2 * m), str(m ** 3), f"√{m}"],
            "steps": [f"1/√(kN) = (1/{m})·1/√N ⇒ √k = {m}.", f"k = <b>{m * m}</b>."], "explanation": "Konvergensi Monte Carlo lambat tetapi tak bergantung dimensi."}


# ════════════════════════ Medan vektor dalam simulasi ═════════════════════
@register("fks.normal", SM, (1, 2))
def fks_normal(rng, tier):
    a, b = nz(rng, -3, 3), nz(rng, -3, 3)
    x0, y0 = rng.randint(-2, 2), rng.randint(-2, 2)
    fx, fy = 2 * a * x0, 2 * b * y0
    correct = f"⟨{n(-fx)}, {n(-fy)}, 1⟩"
    return {"prompt": f"Untuk shading 3D, tentukan vektor normal (ke atas) permukaan z = {terms([(a, 'x²'), (b, 'y²')])} di titik dengan (x, y) = ({n(x0)}, {n(y0)}).",
            "correct": correct, "distractors": [f"⟨{n(fx)}, {n(fy)}, 1⟩", f"⟨{n(-fx)}, {n(-fy)}, 0⟩", f"⟨{n(fx)}, {n(fy)}, −1⟩", "⟨0, 0, 1⟩" if (fx, fy) != (0, 0) else "⟨1, 1, 1⟩"],
            "steps": ["Permukaan z = f(x, y) ⇔ F = f(x, y) − z = 0; normal ∇F = ⟨f<sub>x</sub>, f<sub>y</sub>, −1⟩, normal ke atas = ⟨−f<sub>x</sub>, −f<sub>y</sub>, 1⟩.",
                      f"f<sub>x</sub> = {n(fx)}, f<sub>y</sub> = {n(fy)} ⇒ <b>{correct}</b>."], "explanation": "Vektor normal menentukan intensitas cahaya (model Lambert) di grafika komputer."}


@register("fks.partikel", SM, (1, 2, 3))
def fks_partikel(rng, tier):
    x0, y0 = rng.randint(-3, 3), rng.randint(-3, 3)
    h = Fr(1, rng.choice([2, 4, 10]))
    x1, y1 = x0 + h * (-y0), y0 + h * x0
    correct = f"({n(x1)}, {n(y1)})"
    return {"prompt": f"Partikel di ({n(x0)}, {n(y0)}) bergerak mengikuti medan kecepatan F = ⟨−y, x⟩. Satu langkah Euler dengan h = {n(h)} memindahkannya ke …",
            "correct": correct, "distractors": [f"({n(x0 + h * y0)}, {n(y0 - h * x0)})", f"({n(x0 - h * x0)}, {n(y0 - h * y0)})", f"({n(x0)}, {n(y0)})", f"({n(x1 + h)}, {n(y1)})"],
            "steps": ["Posisi baru = posisi + h·F(posisi).", f"F({n(x0)}, {n(y0)}) = ⟨{n(-y0)}, {n(x0)}⟩.", f"<b>{correct}</b>."],
            "graphs": [g2d("Integrasi Euler partikel pada medan rotasi", [-4, 4], [-4, 4], [param("hh", "h", 0.02, 0.5, 0.02, float(h), "h")],
                           [{"type": "param", "t": [0, "2*pi"], "x": f"{math.hypot(x0, y0) or 1}*cos(t)", "y": f"{math.hypot(x0, y0) or 1}*sin(t)", "color": "gray"},
                            {"type": "iter", "id": "P", "init": {"x": x0 or 1, "y": y0}, "update": {"x": "x-hh*y", "y": "y+hh*x"}, "steps": "floor(6.28/hh)", "px": "x", "py": "y", "color": "red"}],
                           None, "Euler eksplisit membuat lintasan melingkar perlahan ‘mengembang’ — alasan memakai metode yang lebih baik (RK4) di game & simulasi.")],
            "explanation": "Simulasi partikel = menyelesaikan PD r′ = F(r) secara numerik."}


@register("fks.kerja", SM, (2, 3, 4, 5))
def fks_kerja(rng, tier):
    k = nz(rng, -3, 3)
    A = (rng.randint(-2, 2), rng.randint(-2, 2))
    B = (rng.randint(-2, 3), rng.randint(-2, 3))
    phi = lambda p: k * (p[0] ** 2 + p[1] ** 2)
    val = phi(B) - phi(A)
    return {"prompt": f"Karakter game bergerak dalam medan gaya F = ⟨{n(2 * k)}x, {n(2 * k)}y⟩ dari ({n(A[0])}, {n(A[1])}) ke ({n(B[0])}, {n(B[1])}). Berapa kerja yang dilakukan medan?",
            "correct": n(val), "distractors": [n(-val), n(phi(B)), "0" if val else "1", "bergantung lintasan"],
            "steps": [f"F = ∇({n(k)}(x² + y²)) konservatif.", f"W = φ(B) − φ(A) = {n(phi(B))} − {paren(phi(A))} = <b>{n(val)}</b>."], "explanation": "Medan konservatif: kerja hanya bergantung titik awal & akhir."}


@register("fks.rotasi", SM, (3, 4, 5))
def fks_rotasi(rng, tier):
    k, R = rng.randint(1, 4), rng.randint(1, 4)
    if tier <= 4:
        return {"prompt": f"Pusaran fluida dalam simulasi: F = ⟨−{k if k > 1 else ''}y, {k if k > 1 else ''}x⟩. Hitung curl (skalar) dan sirkulasi mengelilingi lingkaran berjari-jari {R}.",
                "correct": f"curl = {2 * k}, sirkulasi = {2 * k * R * R}π", "distractors": [f"curl = {k}, sirkulasi = {k * R * R}π", f"curl = 0, sirkulasi = 0", f"curl = {2 * k}, sirkulasi = {2 * k * R}π",
                                                                                     f"curl = {2 * k}, sirkulasi = {4 * k * R * R}π"],
                "steps": [f"curl = Q<sub>x</sub> − P<sub>y</sub> = {k} + {k} = {2 * k} (dua kali kecepatan sudut {k}).", f"Green: sirkulasi = {2 * k} × π{R * R}.", f"<b>curl = {2 * k}, sirkulasi = {2 * k * R * R}π</b>."],
                "explanation": "Curl mendeteksi pusaran — dipakai pada simulasi fluida (Navier–Stokes) di grafika."}
    return {"prompt": "Medan F = ⟨x, y⟩/(x² + y²)<sup>1/2</sup> (arah radial satuan). Berapa divergensinya di (x, y) ≠ (0, 0)?", "correct": "1/√(x² + y²)",
            "distractors": ["0", "2", "2/√(x² + y²)", "1"],
            "steps": ["Tulis r = √(x² + y²); F = ⟨x/r, y/r⟩.", "∂(x/r)/∂x = y²/r³, ∂(y/r)/∂y = x²/r³.", "Jumlah = (x² + y²)/r³ = <b>1/r</b>."],
            "explanation": "Divergensi medan radial."}


# ════════════════════════ Analisis asimtotik ═══════════════════════════════
@register("fka.loop", AS, (1, 2))
def fka_loop(rng, tier):
    N = rng.choice([10, 20, 50, 100])
    if tier == 1:
        val = N * (N + 1) // 2
        return {"prompt": f"for i in 1..{N}: for j in 1..i: kerjakan(). Berapa kali kerjakan() dipanggil?", "correct": str(val),
                "distractors": [str(N * N), str(N * (N - 1) // 2), str(2 * N), str(val + N)],
                "steps": ["Untuk setiap i, loop dalam berjalan i kali.", f"Σᵢ i = n(n + 1)/2 = <b>{val}</b> ⇒ Θ(n²) (FK-S3)."], "explanation": "Menghitung kompleksitas dengan notasi sigma."}
    val = N * (N + 1) * (2 * N + 1) // 6
    return {"prompt": f"for i in 1..{N}: for j in 1..i: for k in 1..i: kerjakan(). Berapa kali kerjakan() dipanggil?", "correct": str(val),
            "distractors": [str(N ** 3), str(N * (N + 1) // 2), str(val // 2), str(N ** 2)],
            "steps": ["Untuk setiap i: i·i = i² panggilan.", f"Σ i² = n(n + 1)(2n + 1)/6 = <b>{val}</b> ⇒ Θ(n³)."], "explanation": "Σk² ≈ n³/3."}


@register("fka.urutan", AS, (1, 2, 3))
def fka_urutan(rng, tier):
    funcs = [("log n", 1), ("√n", 2), ("n", 3), ("n log n", 4), ("n²", 5), ("2ⁿ", 6), ("n!", 7)]
    pick = rng.sample(funcs, 4)
    best = max(pick, key=lambda t: t[1])
    return {"prompt": f"Untuk n → ∞, fungsi mana yang tumbuh paling cepat: {', '.join(p[0] for p in pick)}?", "correct": best[0],
            "distractors": [p[0] for p in pick if p != best],
            "steps": ["Urutan baku: log n ≪ √n ≪ n ≪ n log n ≪ n² ≪ 2ⁿ ≪ n!.", "Bukti: lim f/g = 0 (L'Hôpital/rasio).", f"<b>{best[0]}</b>."],
            "graphs": [g2d("Laju pertumbuhan (skala log)", [1, 20], [0, 20], [], [fn("log(x)", "gray", "log n"), fn("log(x*x)", "blue", "log n²"),
                                                                                 fn("x*log(2)", "red", "log 2ⁿ")], None, "Pada skala logaritmik, eksponensial tampak linear dan polinom tampak logaritmik.")],
            "explanation": "Hierarki laju pertumbuhan (berkas Fasilkom: perbandingan laju pertumbuhan)."}


@register("fka.limit_rasio", AS, (2, 3, 4))
def fka_limit(rng, tier):
    a, b = rng.randint(1, 6), rng.randint(1, 9)
    c = rng.randint(1, 5)
    val = Fr(a, c)
    return {"prompt": f"T(n) = {a}n² + {b}n. Hitung lim<sub>n→∞</sub> T(n)/({c if c > 1 else ''}n² + 5) dan simpulkan kelas kompleksitas T.", "correct": f"{n(val)}, jadi T(n) = Θ(n²)",
            "distractors": [f"{n(val)}, jadi T(n) = Θ(n)", f"0, jadi T(n) = O(n)", f"∞, jadi T(n) = Θ(n³)", f"{n(Fr(b, c))}, jadi T(n) = Θ(n²)"],
            "steps": ["Bagi dengan n²: (a + b/n)/(c + 5/n²) → a/c.", f"Limit berhingga dan positif ⇒ T dan n² sekelas: <b>{n(val)}, Θ(n²)</b> (FK-M2)."],
            "explanation": "0 < lim f/g < ∞ ⇔ f = Θ(g)."}


@register("fka.stirling", AS, (3, 4, 5))
def fka_stirling(rng, tier):
    if tier <= 4:
        return {"prompt": "Dengan aproksimasi Stirling ln n! ≈ n ln n − n, batas bawah banyak perbandingan pengurutan berbasis perbandingan log₂(n!) termasuk kelas …",
                "correct": "Θ(n log n)", "distractors": ["Θ(n)", "Θ(n²)", "Θ(log n)", "Θ(n!)"],
                "steps": ["Pohon keputusan pengurutan punya ≥ n! daun ⇒ tinggi ≥ log₂(n!).", "log₂(n!) = (n ln n − n + O(ln n))/ln 2.", "<b>Θ(n log n)</b> — mergesort optimal."],
                "explanation": "Stirling: n! ≈ √(2πn)(n/e)ⁿ."}
    nn = rng.choice([5, 10, 20])
    return {"prompt": f"Berapa lim<sub>n→∞</sub> n! / (√(2πn)(n/e)ⁿ)?", "correct": "1", "distractors": ["0", "e", "√(2π)", "∞"],
            "steps": ["Rumus Stirling menyatakan rasio ini → 1 (galat relatif ≈ 1/(12n)).", f"Untuk n = {nn} galat relatifnya sekitar {100 / (12 * nn):.2f}%.".replace(".", ","), "<b>1</b>."],
            "explanation": "Stirling diturunkan dari fungsi Gamma dan metode Laplace."}


@register("fka.newton", AS, (4, 5))
def fka_newton(rng, tier):
    c = rng.choice([2, 3, 5, 10])
    x0 = rng.randint(1, 3)
    x1 = Fr(x0 * x0 + c, 2 * x0)
    if tier == 4:
        return {"prompt": f"Metode Newton untuk f(x) = x² − {c} dengan x₀ = {x0}. Hitung x₁.", "correct": n(x1),
                "distractors": [n(Fr(x0 + c, 2)), n(x0 - Fr(x0 * x0 - c, x0)), n(Fr(c, x0)), n(x1 + 1)],
                "steps": ["xₙ₊₁ = xₙ − f(xₙ)/f′(xₙ) = (xₙ + c/xₙ)/2.", f"x₁ = ({x0} + {c}/{x0})/2 = <b>{n(x1)}</b>."], "explanation": "Newton–Raphson (berkas Fasilkom)."}
    return {"prompt": "Jika galat Newton eₙ ≈ 10⁻³, berapa kira-kira galat langkah berikutnya (konvergensi kuadratik)?", "correct": "≈ 10⁻⁶",
            "distractors": ["≈ 10⁻⁴", "≈ 10⁻³", "≈ 5·10⁻⁴", "≈ 10⁻⁹"],
            "steps": ["Konvergensi kuadratik: eₙ₊₁ ≈ C·eₙ².", "(10⁻³)² = 10⁻⁶: jumlah digit benar kira-kira berlipat dua setiap langkah.", "<b>≈ 10⁻⁶</b>."],
            "explanation": "Newton jauh lebih cepat dari bisection (linear)."}
