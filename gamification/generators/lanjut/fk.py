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
from ..dasar.aplikasi import pi_txt

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
    m = rng.randint(2, 10)
    p = Fr(rng.randint(1, m - 1), m)
    if tier == 3:
        val = p * (1 - p)
        return {"prompt": f"Pada neuron sigmoid σ(z) = 1/(1 + e<sup>−z</sup>), keluaran σ(z) = {n(p)}. Berapa σ′(z)?", "correct": n(val),
                "distractors": [n(p), n(1 - p), n(p * p), n(Fr(1, 4)) if val != Fr(1, 4) else "1/2"],
                "steps": ["σ′(z) = σ(z)(1 − σ(z)) (FK-S1).", f"= {n(p)}·{n(1 - p)} = <b>{n(val)}</b>."], "explanation": "Turunan sigmoid dihitung dari keluarannya sendiri — efisien untuk backpropagation."}
    x, y = rng.randint(1, 5), rng.choice([0, 1])
    if tier == 4 or rng.random() < 0.5:
        val = 2 * (p - y) * p * (1 - p) * x
        return {"prompt": f"Neuron ŷ = σ(wx) dengan kerugian kuadrat L = (ŷ − y)². Untuk x = {x}, target y = {y}, keluaran saat ini ŷ = {n(p)}. Hitung ∂L/∂w.",
                "correct": n(val), "distractors": [n(-val), n(2 * (p - y) * x), n((p - y) * x), n(val / 2)],
                "steps": ["Rantai: ∂L/∂w = 2(ŷ − y)·σ′(wx)·x dengan σ′ = ŷ(1 − ŷ).", f"= 2({n(p - y)})·{n(p * (1 - p))}·{x}.", f"= <b>{n(val)}</b>."],
                "explanation": "Backpropagation = aturan rantai lapis demi lapis."}
    val = (p - y) * x
    return {"prompt": f"Neuron logistik ŷ = σ(wx) dengan kerugian entropi silang L = −[y ln ŷ + (1 − y) ln(1 − ŷ)]. Untuk x = {x}, y = {y}, ŷ = {n(p)}, hitung ∂L/∂w.",
            "correct": n(val), "distractors": [n(-val), n(2 * (p - y) * p * (1 - p) * x), n(p * (1 - p) * x), n((p - y))],
            "steps": ["∂L/∂ŷ = −y/ŷ + (1 − y)/(1 − ŷ); dikali σ′ = ŷ(1 − ŷ) menjadi ŷ − y.", f"∂L/∂w = (ŷ − y)·x = ({n(p - y)})·{x} = <b>{n(val)}</b>.",
                      "Faktor σ′ hilang — alasan entropi silang dipakai bersama sigmoid (gradien tidak ‘mati’)."],
            "explanation": "Entropi silang + sigmoid memberi gradien sederhana (ŷ − y)x."}


@register("fkg.konvergensi", GD, (4, 5))
def fkg_konv(rng, tier):
    a, b = rng.randint(1, 10), rng.randint(1, 10)
    if tier == 4:
        if rng.random() < 0.5:
            c = rng.randint(-5, 5)
            f = f"{a}x²/2 {'+' if c >= 0 else MINUS} {abs(c)}x".replace(" + 0x", "")
            return {"prompt": f"Gradient descent pada f(x) = {f} konvergen untuk laju belajar η pada interval …", "correct": f"0 &lt; η &lt; {n(Fr(2, a))}",
                    "distractors": [f"0 &lt; η &lt; {n(Fr(1, a))}", f"0 &lt; η &lt; {2 * a}", "semua η &gt; 0", f"η &gt; {n(Fr(2, a))}"],
                    "steps": [f"Galat e = x − x* memenuhi e ← (1 − {a}η)e (suku linear hanya menggeser minimum).", f"Konvergen ⇔ |1 − {a}η| &lt; 1 ⇔ 0 &lt; η &lt; 2/{a}.", f"<b>0 &lt; η &lt; {n(Fr(2, a))}</b>."],
                    "explanation": "Laju belajar terlalu besar ⇒ divergen (osilasi membesar)."}
        M = max(a, b)
        return {"prompt": f"Gradient descent pada f(x, y) = ({a}x² + {b}y²)/2 konvergen untuk η pada interval …", "correct": f"0 &lt; η &lt; {n(Fr(2, M))}",
                "distractors": [f"0 &lt; η &lt; {n(Fr(2, min(a, b)))}" if a != b else f"0 &lt; η &lt; {n(Fr(1, M))}", f"0 &lt; η &lt; {n(Fr(4, a + b))}" if Fr(4, a + b) != Fr(2, M) else f"0 &lt; η &lt; {2 * M}",
                                "semua η &gt; 0", f"0 &lt; η &lt; {n(Fr(2, a * b))}"],
                "steps": [f"Setiap koordinat: x ← (1 − {a}η)x, y ← (1 − {b}η)y.", f"Keduanya harus |1 − kη| &lt; 1 ⇒ η &lt; 2/{a} dan η &lt; 2/{b}.", f"Kelengkungan terbesar menentukan: <b>0 &lt; η &lt; {n(Fr(2, M))}</b>."],
                "explanation": "Arah paling curam (nilai eigen Hessian terbesar) membatasi laju belajar."}
    if rng.random() < 0.5:
        return {"prompt": f"Untuk f(x) = {a}x²/2, laju belajar η berapa yang membuat gradient descent mencapai minimum dalam SATU langkah dari titik mana pun?",
                "correct": f"η = {n(Fr(1, a))}", "distractors": [f"η = {n(Fr(2, a))}", f"η = {a}", "η = 1" if a != 1 else "η = 1/2", "tidak ada"],
                "steps": [f"x₁ = (1 − {a}η)x₀ = 0 untuk semua x₀ ⇔ {a}η = 1.", f"<b>η = {n(Fr(1, a))}</b> = 1/f″ — inilah ide metode Newton."],
                "explanation": "η optimal = 1/kelengkungan; Hessian berperan pada kasus banyak variabel."}
    if a == b:
        b = a + 1
    lo, hi = min(a, b), max(a, b)
    eta = Fr(2, lo + hi)
    rate = Fr(hi - lo, hi + lo)
    return {"prompt": f"Untuk f(x, y) = ({a}x² + {b}y²)/2, η tetap berapa yang meminimumkan faktor kontraksi terburuk max|1 − kη| (k = {lo}, {hi}), dan berapa faktornya?",
            "correct": f"η = {n(eta)}, faktor {n(rate)}", "distractors": [f"η = {n(Fr(1, hi))}, faktor {n(1 - Fr(lo, hi))}", f"η = {n(Fr(1, lo))}, faktor 0", f"η = {n(eta)}, faktor 0",
                                                                     f"η = {n(Fr(2, hi))}, faktor {n(rate)}"],
            "steps": [f"Seimbangkan kedua arah: 1 − {lo}η = −(1 − {hi}η) ⇒ η = 2/({lo} + {hi}).", f"Faktor = ({hi} − {lo})/({hi} + {lo}) = {n(rate)} = (κ − 1)/(κ + 1), κ = {n(Fr(hi, lo))}.",
                      f"<b>η = {n(eta)}, faktor {n(rate)}</b>."],
            "explanation": "Bilangan kondisi κ = λmax/λmin menentukan kecepatan GD — motivasi normalisasi fitur."}


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


def rpow(m):
    """(x² + y²)^{m/2} sebagai teks."""
    return {1: "√(x² + y²)", 2: "(x² + y²)", 3: "(x² + y²)<sup>3/2</sup>", 4: "(x² + y²)²"}[m]


@register("fkp.gabungan", PL, (1, 2, 3))
def fkp_gab(rng, tier):
    if tier <= 2:
        p, q = rng.randint(0, 2), rng.randint(1, 2)
        a, b = (1, 1) if tier == 1 else (rng.randint(1, 2), rng.randint(1, 3))
        u, v = rng.choice([Fr(1, 2), Fr(1, 3), Fr(2, 3)]), rng.choice([Fr(1, 2), Fr(1, 3), Fr(2, 3)])
        k = Fr((p + 1) * (q + 1), a ** (p + 1) * b ** (q + 1))
        P = u ** (p + 1) * v ** (q + 1)
        s, t = u * a, v * b
        dens = f"k{'x' if p == 1 else f'x{sup(p)}' if p else ''}{'y' if q == 1 else f'y{sup(q)}'}"
        correct = f"k = {n(k)}, P = {n(P)}"
        return {"prompt": f"f(x, y) = {dens} pada [0, {a}] × [0, {b}] adalah kepadatan gabungan. Tentukan k dan P(X ≤ {n(s)}, Y ≤ {n(t)}).", "correct": correct,
                "distractors": [f"k = {n(k)}, P = {n(u * v)}", f"k = {n(1 / k)}, P = {n(P)}", f"k = {n(k)}, P = {n(P * 2)}", f"k = {n(k * 2)}, P = {n(P)}"],
                "steps": [f"∬ f dA = k·({a}{sup(p + 1)}/{p + 1})({b}{sup(q + 1)}/{q + 1}) = 1 ⇒ k = {n(k)}.".replace("/1)", ")"),
                          f"Karena f terpisah (x dan y), P = ({n(s)}/{a}){sup(p + 1)}·({n(t)}/{b}){sup(q + 1)} = {n(P)}.".replace("/1)", ")"), f"<b>{correct}</b>."],
                "explanation": "Peluang gabungan = integral ganda kepadatan pada daerah kejadian."}
    if rng.random() < 0.5:
        a, b = rng.randint(1, 5), rng.randint(1, 5)
        val = 1 - Fr(a, 2 * b) if a <= b else Fr(b, 2 * a)
        return {"prompt": f"X ~ seragam[0, {a}] dan Y ~ seragam[0, {b}] saling bebas. Hitung P(X &lt; Y).", "correct": n(val),
                "distractors": [n(Fr(1, 2)) if val != Fr(1, 2) else "1/4", n(1 - val) if 1 - val != val else "1/3", n(Fr(min(a, b), max(a, b))), n(Fr(a, a + b))],
                "steps": [f"Kepadatan gabungan 1/({a}·{b}) pada persegi panjang [0, {a}] × [0, {b}].",
                          "P(X &lt; Y) = (luas daerah x &lt; y di dalam persegi panjang)/(luas persegi panjang).",
                          f"Luas daerah = {n(val * a * b)} dari {a * b} ⇒ <b>{n(val)}</b>."],
                "explanation": "Peluang seragam = rasio luas."}
    c = rng.choice([Fr(1, 2), Fr(1, 3), Fr(2, 3), Fr(3, 4), Fr(1, 4), Fr(3, 2), Fr(4, 3), Fr(5, 4), Fr(5, 3)])
    val = c * c / 2 if c <= 1 else 1 - (2 - c) ** 2 / 2
    return {"prompt": f"X dan Y saling bebas, masing-masing seragam pada [0, 1]. Hitung P(X + Y ≤ {n(c)}).", "correct": n(val),
            "distractors": [n(c / 2), n(c * c), n(1 - val), n(c * c / 4)],
            "steps": ["Daerah kejadian: bagian persegi [0, 1]² di bawah garis x + y = c.",
                      f"c = {n(c)} {'≤ 1: segitiga siku-siku dengan kaki c ⇒ c²/2' if c <= 1 else '&gt; 1: persegi dikurangi segitiga pojok berkaki 2 − c ⇒ 1 − (2 − c)²/2'}.",
                      f"<b>{n(val)}</b>."],
            "explanation": "Peluang gabungan seragam = luas daerah."}


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
        N = rng.choice([1000, 2000, 4000, 5000, 10000, 20000])
        k = round(N * math.pi / 4) + rng.randint(-40, 40)
        est = Fr(4 * k, N)
        return {"prompt": f"Dari {N} titik acak seragam di persegi [0, 1]², sebanyak {k} jatuh di dalam seperempat lingkaran x² + y² ≤ 1. Taksiran π?", "correct": n(float(est)),
                "distractors": [n(float(Fr(k, N))), n(float(Fr(2 * k, N))), n(float(Fr(4 * N, k))), "3,14159"],
                "steps": ["Peluang titik di dalam = luas seperempat lingkaran = π/4.", f"π ≈ 4·{k}/{N} = <b>{n(float(est))}</b>."],
                "graphs": [g2d("Monte Carlo: titik di dalam seperempat lingkaran", [0, 1], [0, 1], [], [{"type": "param", "t": [0, "pi/2"], "x": "cos(t)", "y": "sin(t)", "color": "red"},
                                                                                                    {"type": "fill", "upper": "sqrt(1-x*x)", "from": 0, "to": 1, "color": "amber"}], None,
                               "Rasio luas berwarna terhadap persegi = π/4.")],
                "explanation": "Integrasi Monte Carlo: integral ≈ rata-rata sampel acak."}
    if rng.random() < 0.5:
        m = rng.randint(2, 12)
        return {"prompt": f"Galat integrasi Monte Carlo sebanding dengan 1/√N. Agar galat menjadi 1/{m} kali semula, banyak sampel harus dikali …", "correct": str(m * m),
                "distractors": [str(m), str(2 * m), str(m ** 3), f"√{m}"],
                "steps": [f"1/√(kN) = (1/{m})·1/√N ⇒ √k = {m}.", f"k = <b>{m * m}</b>."], "explanation": "Konvergensi Monte Carlo lambat tetapi tak bergantung dimensi."}
    s, q = rng.randint(1, 9), rng.choice([10, 20, 25, 50, 100])
    N = q * q
    val = Fr(s, q)
    return {"prompt": f"Integrand acak memiliki simpangan baku σ = {s}. Dengan N = {N} sampel, galat baku taksiran Monte Carlo (σ/√N) adalah …", "correct": n(float(val)),
            "distractors": [n(float(Fr(s, N))), n(float(Fr(s * s, q))), n(float(val * 2)), n(float(Fr(1, q)))],
            "steps": ["Galat baku rata-rata sampel = σ/√N (teorema limit pusat).", f"{s}/√{N} = {s}/{q} = <b>{n(float(val))}</b>."],
            "explanation": "Galat Monte Carlo turun seperti 1/√N, berapa pun dimensinya."}


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
    if tier <= 4:
        a, b, R = rng.randint(1, 4), rng.randint(1, 4), rng.randint(1, 4)
        p, q = rng.randint(-2, 2), rng.randint(-2, 2)
        P, Q = terms([(p, "x"), (-a, "y")]), terms([(b, "x"), (q, "y")])
        curl, circ, div = a + b, (a + b) * R * R, p + q
        if tier == 3:
            correct = f"curl = {curl}, sirkulasi = {circ}π"
            wrong = [f"curl = {n(b - a)}, sirkulasi = {pi_txt(b - a) if b != a else '0'}", f"curl = {curl}, sirkulasi = {curl * R}π", f"curl = {curl}, sirkulasi = {2 * circ}π", f"curl = {n(div)}, sirkulasi = {pi_txt(div * R * R) if div else '0'}"]
            ask = f"Hitung curl (skalar) dan sirkulasi mengelilingi lingkaran berjari-jari {R} (berlawanan jarum jam)."
        else:
            correct = f"div = {n(div)}, curl = {curl}"
            wrong = [f"div = {curl}, curl = {n(div)}", f"div = {n(div)}, curl = {n(b - a)}", f"div = {n(p - q)}, curl = {curl}", f"div = {n(div + 1)}, curl = {curl}"]
            ask = "Hitung divergensi dan curl (skalar) medan ini: apakah fluida memancar dan/atau berputar?"
        return {"prompt": f"Medan kecepatan fluida dalam simulasi: F = ⟨{P}, {Q}⟩. {ask}", "correct": correct, "distractors": wrong,
                "steps": [f"div F = ∂P/∂x + ∂Q/∂y = {n(p)} + {paren(q)} = {n(div)}.", f"curl F = ∂Q/∂x − ∂P/∂y = {b} − ({n(-a)}) = {curl}.",
                          f"Green: sirkulasi = ∬ curl dA = {curl}·π{R * R} = {circ}π." if tier == 3 else "div &gt; 0: sumber; curl ≠ 0: pusaran.", f"<b>{correct}</b>."],
                "explanation": "Curl mendeteksi pusaran, divergensi mendeteksi sumber — dipakai pada simulasi fluida di grafika."}
    m, c = rng.randint(1, 4), rng.randint(1, 3)
    dim3 = rng.random() < 0.4
    d = 3 if dim3 else 2
    r = "√(x² + y² + z²)" if dim3 else rpow(1)
    rm = ({1: r, 2: "(x² + y² + z²)", 3: "(x² + y² + z²)<sup>3/2</sup>", 4: "(x² + y² + z²)²"} if dim3 else {k: rpow(k) for k in (1, 2, 3, 4)})[m]
    coef = c * (d - m)
    correct = "0" if coef == 0 else f"{n(coef)}/{rm}"
    vec = "⟨x, y, z⟩" if dim3 else "⟨x, y⟩"
    return {"prompt": f"Medan radial F = {c if c > 1 else ''}{vec}/{rm} di titik selain asal. Hitung div F.", "correct": correct,
            "distractors": [f"{n(c * d)}/{rm}", f"{n(c * (d - m + 1))}/{rm}" if d - m + 1 else "1", "0" if coef else f"{c}/{rm}", f"{n(-coef) if coef else c * d}/{rm}"],
            "steps": [f"Tulis r = {r}; F = {c if c > 1 else ''}r⃗/r{sup(m) if m > 1 else ''} dengan ∂r/∂x = x/r.",
                      f"div(r⃗/rᵐ) = {d}/rᵐ − m·r²/r<sup>m+2</sup> = ({d} − m)/rᵐ.", f"m = {m}: <b>{correct}</b>" + (" — inilah hukum kuadrat terbalik: medan gravitasi/listrik bebas sumber di luar asal." if coef == 0 and dim3 else ".")],
            "explanation": "Divergensi medan radial r⃗/rᵐ di ℝᵈ adalah (d − m)/rᵐ."}


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
    k, c = rng.randint(2, 9), rng.randint(2, 9 if tier == 3 else 19)
    if tier == 3:
        cases = [(f"log₂(n!)", "Θ(n log n)", "Stirling: ln n! = n ln n − n + O(ln n)."),
                 (f"log(n{sup(k)}·n!)", "Θ(n log n)", f"= {k} log n + log n! — suku log n! dominan."),
                 (f"log((n!){sup(k)})", "Θ(n log n)", f"= {k}·log n! = Θ(n log n)."),
                 (f"log({k}ⁿ)", "Θ(n)", f"= n log {k}."),
                 (f"log(n{sup(k)})", "Θ(log n)", f"= {k} log n."),
                 (f"log(C(2n, n))", "Θ(n)", "C(2n, n) ≈ 4ⁿ/√(πn) (Stirling) ⇒ log ≈ n log 4 − ½ log(πn)."),
                 (f"log((n!)/({c}ⁿ))", "Θ(n log n)", f"= log n! − n log {c}; n log n mengalahkan n.")]
        f, ans, why = rng.choice(cases)
        return {"prompt": f"Dengan aproksimasi Stirling, {f} termasuk kelas …", "correct": ans,
                "distractors": [v for v in ["Θ(n log n)", "Θ(n)", "Θ(log n)", "Θ(n²)", "Θ(n!)"] if v != ans],
                "steps": ["Stirling: n! ≈ √(2πn)(n/e)ⁿ, sehingga log n! = n log n − n log e + O(log n).", why, f"<b>{ans}</b>."],
                "explanation": "log₂(n!) = Θ(n log n) adalah batas bawah pengurutan berbasis perbandingan."}
    if tier == 4:
        kind = rng.choice(["akar", "akar", "binom"])
        if kind == "binom":
            kk = rng.choice([2, 3])
            correct = "4ⁿ/√(πn)" if kk == 2 else "27ⁿ·√3/(2πn)"
            return {"prompt": f"Dengan rumus Stirling, ({kk}n)!/(n!){sup(kk)} untuk n besar kira-kira …", "correct": correct,
                    "distractors": ["4ⁿ", "2ⁿ/√n", "4ⁿ·√(πn)", "27ⁿ/(2πn)"] if kk == 2 else ["27ⁿ", "9ⁿ/√n", "27ⁿ/√(2πn)", "4ⁿ/√(πn)"],
                    "steps": ["Ganti setiap faktorial dengan √(2πm)(m/e)ᵐ.", f"Pangkat: ({kk}n/e)<sup>{kk}n</sup>/(n/e)<sup>{kk}n</sup> = {kk ** kk}ⁿ; akar: √(2π·{kk}n)/(2πn)<sup>{kk}/2</sup>.",
                              f"<b>{correct}</b>."],
                    "explanation": "Stirling mengubah rasio faktorial menjadi eksponensial × koreksi akar."}
        val = Fr(c)
        return {"prompt": f"Hitung lim<sub>n→∞</sub> {c}n/(n!)<sup>1/n</sup>.", "correct": f"{c}e",
                "distractors": [str(c), f"{c}/e", "∞", "e"],
                "steps": ["Stirling: (n!)<sup>1/n</sup> ≈ (2πn)<sup>1/(2n)</sup>·n/e.", "(2πn)<sup>1/(2n)</sup> → 1, jadi (n!)<sup>1/n</sup>/n → 1/e.", f"{c}n/(n!)<sup>1/n</sup> → <b>{c}e</b>."],
                "explanation": "(n!)^{1/n} tumbuh seperti n/e."}
    kk = rng.randint(1, 5)
    if rng.random() < 0.5:
        correct = f"{kk ** kk}/e{sup(kk)}" if kk > 1 else "1/e"
        return {"prompt": f"Hitung lim<sub>n→∞</sub> (({kk if kk > 1 else ''}n)!)<sup>1/n</sup>/n{sup(kk) if kk > 1 else ''}.", "correct": correct,
                "distractors": [f"{kk ** kk}" if kk > 1 else "1", f"{kk}/e" if kk > 1 else "e", "0", "∞"],
                "steps": [f"Stirling: ({kk}n)! ≈ √(2π·{kk}n)·({kk}n/e)<sup>{kk}n</sup>.".replace("·1n", "·n").replace("(1n", "(n"),
                          f"Akar pangkat n: ({kk}n/e){sup(kk)}·(faktor → 1) = {kk ** kk}n{sup(kk)}/e{sup(kk)}.".replace("{sup(1)}", ""), f"Bagi n{sup(kk)}: <b>{correct}</b>."],
                "explanation": "((kn)!)^{1/n} ≈ (kn/e)^k."}
    correct = f"{c}/e"
    return {"prompt": f"Hitung lim<sub>n→∞</sub> ({c}ⁿ·n!)<sup>1/n</sup>/n.", "correct": correct, "distractors": [str(c), f"{c}e", "1/e", "∞"],
            "steps": [f"({c}ⁿ·n!)<sup>1/n</sup> = {c}·(n!)<sup>1/n</sup>.", "Stirling: (n!)<sup>1/n</sup>/n → 1/e.", f"<b>{correct}</b>."],
            "explanation": "(n!)^{1/n} tumbuh seperti n/e."}


@register("fka.newton", AS, (4, 5))
def fka_newton(rng, tier):
    if tier == 4:
        cube = rng.random() < 0.4
        x0 = rng.randint(1, 4)
        if cube:
            c = rng.choice([v for v in range(2, 40) if round(v ** (1 / 3)) ** 3 != v])
            x1 = Fr(2 * x0 ** 3 + c, 3 * x0 * x0)
            f, it = f"x³ − {c}", f"xₙ₊₁ = xₙ − (xₙ³ − {c})/(3xₙ²) = (2xₙ³ + {c})/(3xₙ²)"
            wrong = [n(Fr(x0 + c, 2)), n(Fr(x0 ** 3 + c, 3 * x0 * x0)), n(Fr(c, x0 * x0)), n(x1 + 1)]
        else:
            c = rng.choice([v for v in range(2, 40) if math.isqrt(v) ** 2 != v])
            x1 = Fr(x0 * x0 + c, 2 * x0)
            f, it = f"x² − {c}", f"xₙ₊₁ = xₙ − (xₙ² − {c})/(2xₙ) = (xₙ + {c}/xₙ)/2"
            wrong = [n(Fr(x0 + c, 2)), n(x0 - Fr(x0 * x0 - c, x0)), n(Fr(c, x0)), n(x1 + 1)]
        return {"prompt": f"Metode Newton untuk f(x) = {f} dengan x₀ = {x0}. Hitung x₁.", "correct": n(x1), "distractors": wrong,
                "steps": ["xₙ₊₁ = xₙ − f(xₙ)/f′(xₙ).", f"{it}.", f"x₁ = <b>{n(x1)}</b>."], "explanation": "Newton–Raphson (berkas Fasilkom)."}
    if rng.random() < 0.5:
        k, C = rng.randint(1, 6), rng.choice([1, 2, 3, 5])
        correct = f"≈ {'' if C == 1 else f'{C}·'}10{sup(-2 * k)}"
        return {"prompt": f"Galat Newton memenuhi eₙ₊₁ ≈ {'' if C == 1 else C}eₙ². Jika eₙ ≈ 10{sup(-k)}, berapa kira-kira eₙ₊₁?", "correct": correct,
                "distractors": [f"≈ {'' if C == 1 else f'{C}·'}10{sup(-k - 1)}", f"≈ 10{sup(-k)}", f"≈ {'' if C == 1 else f'{C}·'}10{sup(-3 * k)}", f"≈ {2 * C}·10{sup(-k)}"],
                "steps": ["Konvergensi kuadratik: eₙ₊₁ ≈ C·eₙ².", f"{'' if C == 1 else f'{C}·'}(10{sup(-k)})² = {correct[2:]}: banyak digit benar kira-kira berlipat dua.", f"<b>{correct}</b>."],
                "explanation": "Newton jauh lebih cepat dari bisection (linear)."}
    d = rng.choice([4, 6, 8, 10, 12, 16, 20, 24, 32])
    steps_n = math.ceil(math.log2(d))
    bis = math.ceil((d - 1) * math.log2(10))   # bisection: 2ᵐ ≥ 10^(d−1)
    return {"prompt": f"Galat awal 10⁻¹. Dengan konvergensi kuadratik (eₙ₊₁ ≈ eₙ²), berapa langkah Newton minimum agar galat ≤ 10{sup(-d)}?", "correct": str(steps_n),
            "distractors": [str(d - 1), str(steps_n + 1), str(d), str(bis)],
            "steps": ["Setiap langkah menggandakan eksponen: 10⁻¹ → 10⁻² → 10⁻⁴ → 10⁻⁸ → …", f"Setelah m langkah: 10<sup>−2ᵐ</sup> ≤ 10{sup(-d)} ⇔ 2ᵐ ≥ {d}.",
                      f"m = <b>{steps_n}</b> (bandingkan bisection yang butuh ±{bis} langkah)."],
            "explanation": "Kuadratik vs linear: inilah alasan Newton dipakai di pustaka numerik."}
