"""
Topik TERAPAN khusus Fakultas Teknik (Level Utama 4).
Rujukan: Strang (MIT) Bab 13–15; Stewart §14.4, §14.8, §15.5, §16.8–16.9; Laplace: Stewart (Bab tambahan) / Strang.
"""

from fractions import Fraction as Fr
import math

from .. import register
from ..fmt import MINUS, n, paren, sup
from ..graphs import fn, g2d, param, readout
from ..precalc.common import distinct, nz
from ..dasar.aplikasi import pi_txt

GL, LG, MS, FL, LP = "kl-ft-galat", "kl-ft-lagrange", "kl-ft-massa", "kl-ft-fluks", "kl-ft-laplace"


# ════════════════════════ Diferensial total & galat ════════════════════════
@register("ftg.suhu", GL, (1, 2, 3, 4, 5))
def ftg_suhu(rng, tier):
    a, b = rng.randint(1, 4), rng.randint(1, 4)
    x, y = rng.randint(-3, 3), rng.randint(-3, 3)
    T0 = 100
    if tier <= 2:
        val = T0 - a * x * x - b * y * y
        return {"prompt": f"Suhu pelat logam T(x, y) = {T0} − {a if a > 1 else ''}x² − {b if b > 1 else ''}y² (°C). Berapa suhu di titik ({n(x)}, {n(y)})?",
                "correct": f"{n(val)}°C", "distractors": [f"{n(val + 2 * a)}°C", f"{n(T0 - a * x - b * y)}°C", f"{n(T0 + a * x * x + b * y * y)}°C", f"{n(val - 1)}°C"],
                "steps": [f"T = {T0} − {a}·{x * x} − {b}·{y * y}.", f"<b>{n(val)}°C</b>."], "explanation": "Medan skalar: suhu sebagai fungsi posisi."}
    gx, gy = -2 * a * x, -2 * b * y
    if tier == 3:
        correct = f"⟨{n(gx)}, {n(gy)}⟩"
        return {"prompt": f"T(x, y) = {T0} − {a}x² − {b}y². Semut di ({n(x)}, {n(y)}) ingin bergerak ke arah suhu naik paling cepat. Arahnya?",
                "correct": correct, "distractors": [f"⟨{n(-gx)}, {n(-gy)}⟩", f"⟨{n(gy)}, {n(gx)}⟩", "⟨0, 0⟩", f"⟨{n(x)}, {n(y)}⟩"],
                "steps": ["Arah kenaikan tercepat = ∇T.", f"∇T = ⟨−{2 * a}x, −{2 * b}y⟩ = <b>{correct}</b> (menuju titik terpanas di asal)."], "explanation": "Gradien suhu menentukan arah aliran panas (berlawanan ∇T)."}
    p, q, h = rng.choice([(3, 4, 5), (4, 3, 5), (0, 1, 1), (1, 0, 1)])
    val = Fr(gx * p + gy * q, h)
    return {"prompt": f"T(x, y) = {T0} − {a}x² − {b}y². Laju perubahan suhu di ({n(x)}, {n(y)}) ke arah ⟨{p}, {q}⟩?", "correct": f"{n(val)} °C/satuan",
            "distractors": [f"{n(-val)} °C/satuan", f"{n(gx * p + gy * q)} °C/satuan", f"{n(Fr(gx + gy))} °C/satuan", "0 °C/satuan" if val else "1 °C/satuan"],
            "steps": [f"∇T = ⟨{n(gx)}, {n(gy)}⟩; u = ⟨{p}, {q}⟩/{h}.", f"D<sub>u</sub>T = <b>{n(val)}</b>."], "explanation": "Turunan berarah medan suhu."}


@register("ftg.diferensial", GL, (1, 2, 3))
def ftg_diferensial(rng, tier):
    x, y = rng.randint(2, 10), rng.randint(2, 10)
    dx, dy = Fr(rng.choice([1, 2, 5]), 100), Fr(rng.choice([1, 2, 5]), 100)
    if tier <= 2:
        dA = y * dx + x * dy
        return {"prompt": f"Pelat persegi panjang {x} m × {y} m diukur dengan galat dx = {n(dx)} m dan dy = {n(dy)} m. Taksir galat luas dengan diferensial.",
                "correct": f"{n(dA)} m²", "distractors": [f"{n(dx * dy)} m²", f"{n(x * dx + y * dy)} m²", f"{n(dA * 2)} m²", f"{n((x + dx) * (y + dy) - x * y)} m²"],
                "steps": ["A = xy ⇒ dA = A<sub>x</sub>dx + A<sub>y</sub>dy = y dx + x dy.", f"= {y}·{n(dx)} + {x}·{n(dy)} = <b>{n(dA)} m²</b>."],
                "explanation": "Diferensial total dz = f_x dx + f_y dy menaksir perubahan kecil."}
    r, h = rng.randint(2, 6), rng.randint(5, 15)
    dr, dh = Fr(1, 10), Fr(1, 10)
    dV = 2 * r * h * dr + r * r * dh
    return {"prompt": f"Silinder r = {r} cm, h = {h} cm; r dan h masing-masing bertambah {n(dr)} cm. Taksir perubahan volume.", "correct": pi_txt(dV, " cm³"),
            "distractors": [pi_txt(2 * r * h * dr, " cm³"), pi_txt(r * r * dh, " cm³"), pi_txt(dV * 2, " cm³"), n(dV) + " cm³"],
            "steps": ["V = πr²h ⇒ dV = 2πrh dr + πr² dh.", f"= π({2 * r * h}·{n(dr)} + {r * r}·{n(dh)}) = <b>{pi_txt(dV, ' cm³')}</b>."], "explanation": "Diferensial dalam toleransi manufaktur (FT)."}


@register("ftg.galat_relatif", GL, (2, 3, 4, 5))
def ftg_relatif(rng, tier):
    pr, ph = rng.randint(1, 3), rng.randint(1, 4)
    if tier <= 3:
        val = 2 * pr + ph
        return {"prompt": f"Volume silinder V = πr²h. Galat ukur r maksimal {pr}% dan h maksimal {ph}%. Taksir galat relatif maksimum V.", "correct": f"{val}%",
                "distractors": [f"{pr + ph}%", f"{2 * pr * ph}%", f"{pr + 2 * ph}%", f"{val * 2}%"],
                "steps": ["dV/V = 2(dr/r) + dh/h (turunkan ln V = ln π + 2 ln r + ln h).", f"≤ 2·{pr}% + {ph}% = <b>{val}%</b>."],
                "explanation": "Galat relatif produk pangkat: jumlah (pangkat × galat relatif)."}
    pm, pv = rng.randint(1, 3), rng.randint(1, 3)
    val = pm + 2 * pv
    return {"prompt": f"Energi kinetik E = ½mv². Galat relatif m maksimal {pm}% dan v maksimal {pv}%. Galat relatif maksimum E?", "correct": f"{val}%",
            "distractors": [f"{pm + pv}%", f"{2 * pm + pv}%", f"{pm * pv * 2}%", f"{val + 1}%"],
            "steps": ["dE/E = dm/m + 2 dv/v.", f"≤ {pm}% + 2·{pv}% = <b>{val}%</b>."], "explanation": "Analisis galat pengukuran (fisika & teknik)."}


# ════════════════════════ Optimasi desain & Lagrange ═══════════════════════
@register("ftl.ekstrem", LG, (1, 2))
def ftl_ekstrem(rng, tier):
    a, b = nz(rng, -4, 4) * 2, nz(rng, -4, 4) * 2
    x0, y0 = Fr(a, 2), Fr(b, 2)
    val = -(x0 * x0 + y0 * y0)
    return {"prompt": f"Tentukan nilai minimum f(x, y) = x² + y² − {n(a)}x − {n(b)}y.".replace("− −", "+ "), "correct": n(val),
            "distractors": [n(-val), "0" if val else "1", n(val - 1), n(Fr(a + b, 2))],
            "steps": ["f<sub>x</sub> = 2x − a = 0, f<sub>y</sub> = 2y − b = 0.", f"Titik kritis ({n(x0)}, {n(y0)}); f paraboloid terbuka ke atas ⇒ minimum.", f"f = <b>{n(val)}</b>."],
            "explanation": "Titik kritis: ∇f = 0."}


@register("ftl.lagrange", LG, (1, 2, 3))
def ftl_lagrange(rng, tier):
    if tier <= 2:
        P = 4 * rng.randint(2, 15)
        val = (P // 4) ** 2
        return {"prompt": f"Pagar sepanjang {P} m membentuk persegi panjang. Gunakan pengali Lagrange untuk luas maksimum.", "correct": f"{val} m²",
                "distractors": [f"{P * P // 8} m²", f"{(P // 4) * (P // 4 + 1)} m²", f"{P} m²", f"{val * 2} m²"],
                "steps": [f"Maksimumkan A = xy dengan kendala 2x + 2y = {P}.", "∇A = λ∇g: y = 2λ, x = 2λ ⇒ x = y.", f"x = y = {P // 4} ⇒ A = <b>{val} m²</b>."],
                "explanation": "Lagrange: di titik optimum ∇f sejajar ∇g."}
    r = rng.randint(1, 6)
    return {"prompt": f"Tentukan nilai maksimum f(x, y) = x + y pada lingkaran x² + y² = {r * r}.", "correct": f"{r}√2" if r > 1 else "√2",
            "distractors": [f"{2 * r}", f"{r}", f"{r * r}", f"{r}√3" if r > 1 else "√3"],
            "steps": ["∇f = ⟨1, 1⟩ = λ⟨2x, 2y⟩ ⇒ x = y.", f"2x² = {r * r} ⇒ x = y = {r}/√2.", f"f = 2·{r}/√2 = <b>{r}√2</b>."], "explanation": "Kendala lingkaran: titik optimum di arah ∇f."}


@register("ftl.kotak", LG, (2, 3, 4, 5))
def ftl_kotak(rng, tier):
    k = rng.randint(1, 5)
    V, S = 4 * k ** 3, 12 * k * k
    return {"prompt": f"Kotak tanpa tutup bervolume {V} m³ dibuat dengan bahan seminimal mungkin. Berapa luas bahan minimum?", "correct": f"{S} m²",
            "distractors": [f"{6 * k * k} m²", f"{16 * k * k} m²", f"{S + 4 * k * k} m²", f"{V} m²"],
            "steps": [f"Minimumkan S = xy + 2xz + 2yz dengan xyz = {V}.", "Simetri & Lagrange ⇒ x = y = 2z.", f"4z³ = {V} ⇒ z = {k}, x = y = {2 * k}.",
                      f"S = {4 * k * k} + {4 * k * k} + {4 * k * k} = <b>{S} m²</b>."], "explanation": "Optimasi desain wadah (Stewart §14.7)."}


@register("ftl.tiga_var", LG, (4, 5))
def ftl_tiga(rng, tier):
    if tier == 4:
        s = 3 * rng.randint(1, 6)
        return {"prompt": f"Tentukan nilai maksimum xyz dengan x + y + z = {s}, x, y, z &gt; 0.", "correct": n((s // 3) ** 3),
                "distractors": [n(s ** 3 // 9), n((s // 3) ** 2), n(s), n((s // 3) ** 3 * 2)],
                "steps": ["∇(xyz) = λ∇(x + y + z): yz = xz = xy = λ ⇒ x = y = z.", f"x = y = z = {s // 3} ⇒ <b>{(s // 3) ** 3}</b>."], "explanation": "Lagrange tiga variabel (juga AM–GM)."}
    a, b, c = rng.choice([(1, 2, 2), (2, 3, 6), (1, 4, 8), (2, 1, 2)])
    d = rng.randint(1, 9)
    m = a * a + b * b + c * c
    val = Fr(d * d, m)
    return {"prompt": f"Tentukan nilai minimum x² + y² + z² pada bidang {a if a > 1 else ''}x + {b if b > 1 else ''}y + {c if c > 1 else ''}z = {d}.", "correct": n(val),
            "distractors": [n(Fr(d, m)), n(Fr(d * d, a + b + c)), n(val * 2), n(d * d)],
            "steps": ["∇(x² + y² + z²) = λ⟨a, b, c⟩ ⇒ (x, y, z) = (λ/2)⟨a, b, c⟩.", f"Substitusi: λ/2 = {d}/{m}.", f"Minimum = {d}²/{m} = <b>{n(val)}</b> (kuadrat jarak bidang ke asal)."],
            "explanation": "Jarak bidang ax + by + cz = d ke titik asal = |d|/√(a² + b² + c²)."}


# ════════════════════════ Massa, momen inersia, pusat massa ═══════════════
@register("ftm.rms", MS, (1, 2))
def ftm_rms(rng, tier):
    V0 = rng.choice([10, 20, 100, 220, 311])
    if tier == 1:
        return {"prompt": f"Tegangan AC v(t) = {V0} sin(ωt). Nilai RMS-nya (√ rata-rata v² satu periode) adalah …", "correct": f"{V0}/√2 V",
                "distractors": [f"{V0} V", f"{V0}/2 V", "0 V", f"{V0}√2 V"],
                "steps": ["Rata-rata sin² dalam satu periode = 1/2.", f"v<sub>RMS</sub> = √({V0}²/2) = <b>{V0}/√2 V</b>."], "explanation": "RMS = nilai efektif arus/tegangan AC (berkas materi khusus FT)."}
    return {"prompt": f"Arus i(t) = {V0} sin t melalui resistor R. Berapa rata-rata i² pada [0, 2π]?", "correct": n(Fr(V0 * V0, 2)),
            "distractors": [n(V0 * V0), "0", n(Fr(V0, 2)), n(Fr(V0 * V0, 4))],
            "steps": ["(1/2π)∫₀^{2π} sin²t dt = 1/2.", f"Rata-rata i² = {V0}²/2 = <b>{n(Fr(V0 * V0, 2))}</b>."], "explanation": "Daya rata-rata P = R·⟨i²⟩."}


@register("ftm.massa", MS, (1, 2, 3))
def ftm_massa(rng, tier):
    a, b, k = rng.randint(1, 4), rng.randint(1, 4), rng.randint(1, 5)
    if tier <= 2:
        val = Fr(k * a * a * b, 2)
        dens = f"{k if k > 1 else ''}x"
    else:
        val = Fr(k * a * a * b * b, 4)
        dens = f"{k if k > 1 else ''}xy"
    return {"prompt": f"Pelat persegi panjang [0, {a}] × [0, {b}] memiliki rapat massa ρ(x, y) = {dens} kg/m². Hitung massanya.", "correct": f"{n(val)} kg",
            "distractors": [f"{n(val * 2)} kg", f"{k * a * b} kg", f"{n(val / 2)} kg", f"{n(val + k)} kg"],
            "steps": ["m = ∬ ρ dA.", f"∫₀^{a}∫₀^{b} {dens} dy dx = <b>{n(val)} kg</b>."], "explanation": "Massa lamina dengan rapat tidak seragam."}


@register("ftm.inersia", MS, (2, 3, 4, 5))
def ftm_inersia(rng, tier):
    if tier <= 3:
        a, b = rng.randint(1, 4), rng.randint(1, 4)
        val = Fr(a * b ** 3, 3)
        return {"prompt": f"Momen inersia luas I<sub>x</sub> = ∬ y² dA penampang balok [0, {a}] × [0, {b}] terhadap sumbu-x (alas).", "correct": n(val),
                "distractors": [n(Fr(a * b ** 3, 12)), n(Fr(a ** 3 * b, 3)), n(a * b * b), n(val * 2)],
                "steps": [f"∫₀^{a}∫₀^{b} y² dy dx = {a}·{b}³/3 = <b>{n(val)}</b>.", f"Terhadap sumbu berat (tengah) menjadi ab³/12 = {n(Fr(a * b ** 3, 12))} — dasar kekakuan balok (FT sipil)."],
                "explanation": "Momen inersia luas menentukan kekakuan lentur."}
    R = rng.randint(1, 4)
    val = Fr(R ** 4, 2)
    return {"prompt": f"Hitung momen inersia polar I<sub>0</sub> = ∬ (x² + y²) dA cakram berjari-jari {R} (rapat 1).", "correct": pi_txt(val),
            "distractors": [pi_txt(R ** 4), pi_txt(Fr(R ** 4, 4)), pi_txt(Fr(R ** 3, 3)), n(val)],
            "steps": ["Koordinat kutub: ∫₀^{2π}∫₀^R r²·r dr dθ.", f"= 2π·{R ** 4}/4 = <b>{pi_txt(val)}</b>. (Poros/as berbentuk lingkaran, FT mesin.)"],
            "explanation": "I₀ = I_x + I_y."}


@register("ftm.pusat", MS, (3, 4, 5))
def ftm_pusat(rng, tier):
    if tier == 3:
        a, b = rng.randint(1, 6), rng.randint(1, 6)
        return {"prompt": f"Tentukan sentroid segitiga dengan titik sudut (0, 0), ({a * 3}, 0), (0, {b * 3}).", "correct": f"({a}, {b})",
                "distractors": [f"({n(Fr(3 * a, 2))}, {n(Fr(3 * b, 2))})", f"({b}, {a})", f"({2 * a}, {2 * b})", f"({a}, {2 * b})"],
                "steps": ["x̄ = (1/A)∬ x dA; untuk segitiga = rata-rata titik sudut.", f"x̄ = {3 * a}/3 = {a}, ȳ = {3 * b}/3 = {b}.", f"<b>({a}, {b})</b>."], "explanation": "Sentroid segitiga = titik berat."}
    R = rng.randint(1, 6) * 3
    val = Fr(4 * R, 3)
    return {"prompt": f"Tentukan x̄ = ȳ untuk seperempat cakram x² + y² ≤ {R * R}, x, y ≥ 0.", "correct": f"{n(val)}/π",
            "distractors": [f"{n(Fr(R, 2))}", f"{n(Fr(2 * R, 3))}/π", f"{n(val)}", f"{n(Fr(R, 3))}"],
            "steps": [f"A = π{R * R}/4; ∬ x dA = ∫₀^{{π/2}}∫₀^{R} r cos θ·r dr dθ = {R ** 3}/3.", f"x̄ = ({R ** 3}/3)/(π{R * R}/4) = <b>{n(val)}/π</b>."], "explanation": "Sentroid seperempat lingkaran 4R/(3π)."}


# ════════════════════════ Fluks, divergensi, Stokes ═══════════════════════
@register("ftf.kerja", FL, (1, 2, 3))
def ftf_kerja(rng, tier):
    F = (rng.randint(-5, 9), rng.randint(-5, 9))
    d = (rng.randint(-4, 6), rng.randint(-4, 6))
    W = F[0] * d[0] + F[1] * d[1]
    return {"prompt": f"Gaya konstan F = ⟨{n(F[0])}, {n(F[1])}⟩ N memindahkan benda sejauh d = ⟨{n(d[0])}, {n(d[1])}⟩ m. Hitung kerjanya.", "correct": f"{n(W)} J",
            "distractors": [f"{n(F[0] * d[1] + F[1] * d[0])} J", f"{n(abs(F[0]) + abs(F[1]))} J", f"{n(-W)} J", f"{n(W + 1)} J"],
            "steps": ["W = F · d (hasil kali titik).", f"= {n(F[0])}·{paren(d[0])} + {n(F[1])}·{paren(d[1])} = <b>{n(W)} J</b>."], "explanation": "Kerja = ∫ F·dr; untuk F konstan dan lintasan lurus = F·d."}


@register("ftf.fluks_bidang", FL, (1, 2))
def ftf_bidang(rng, tier):
    E, A = rng.randint(2, 20), rng.randint(1, 5)
    deg = rng.choice([0, 60, 90]) if tier == 1 else rng.choice([30, 45, 60])
    cosv = {0: "1", 30: "√3/2", 45: "√2/2", 60: "1/2", 90: "0"}[deg]
    val = {0: f"{E * A}", 60: n(Fr(E * A, 2)), 90: "0", 30: f"{n(Fr(E * A, 2))}√3", 45: f"{n(Fr(E * A, 2))}√2"}[deg]
    return {"prompt": f"Medan listrik seragam {E} N/C menembus permukaan datar seluas {A} m² dengan sudut {deg}° terhadap normal permukaan. Berapa fluksnya?",
            "correct": f"{val} N·m²/C", "distractors": [f"{E * A} N·m²/C" if deg else "0 N·m²/C", f"{E + A} N·m²/C", f"{n(Fr(E, A))} N·m²/C", f"{E * A * 2} N·m²/C"],
            "steps": ["Φ = E·A·cos θ (θ terhadap normal).", f"= {E}·{A}·{cosv} = <b>{val}</b>."], "explanation": "Fluks = ∬ F·n dS."}


@register("ftf.divergensi", FL, (2, 3, 4))
def ftf_div(rng, tier):
    if tier <= 3:
        a, b, c = rng.randint(1, 5), rng.randint(1, 5), rng.randint(1, 5)
        val = a + b + c
        return {"prompt": f"Gunakan Teorema Divergensi untuk fluks keluar F = ⟨{a}x, {b}y, {c}z⟩ melalui permukaan kubus satuan [0, 1]³.", "correct": n(val),
                "distractors": [n(a * b * c), "0", n(val * 2), n(6 * val)],
                "steps": ["∯ F·n dS = ∭ div F dV.", f"div F = {a} + {b} + {c} = {val} (konstan).", f"× volume 1 = <b>{val}</b>."], "explanation": "Teorema Divergensi (Gauss)."}
    R = rng.randint(1, 4)
    return {"prompt": f"Hitung fluks keluar F = ⟨x, y, z⟩ melalui bola berjari-jari {R}.", "correct": pi_txt(4 * R ** 3),
            "distractors": [pi_txt(Fr(4 * R ** 3, 3)), pi_txt(4 * R * R), pi_txt(12 * R ** 3), "0"],
            "steps": ["div F = 3.", f"∭ 3 dV = 3·(4/3)π·{R ** 3}.", f"= <b>{pi_txt(4 * R ** 3)}</b>. (Cek langsung: F·n = R di permukaan, × luas 4πR².)"], "explanation": "Teorema Divergensi pada bola."}


@register("ftf.stokes", FL, (3, 4, 5))
def ftf_stokes(rng, tier):
    R, k = rng.randint(1, 4), rng.randint(1, 3)
    val = 2 * k * R * R
    return {"prompt": f"Hitung sirkulasi ∮ F·dr dengan F = ⟨−{k if k > 1 else ''}y, {k if k > 1 else ''}x, z⟩ mengelilingi lingkaran x² + y² = {R * R}, z = 0 (berlawanan jarum jam).",
            "correct": pi_txt(val), "distractors": [pi_txt(k * R * R), "0", pi_txt(2 * k * R), pi_txt(val * 2)],
            "steps": ["Teorema Stokes: ∮ F·dr = ∬ (curl F)·n dS.", f"curl F = ⟨0, 0, {2 * k}⟩, n = k̂ pada cakram.", f"{2 * k} × π{R * R} = <b>{pi_txt(val)}</b>."],
            "explanation": "Stokes menghubungkan sirkulasi dengan fluks curl (hukum Ampère, FT elektro)."}


@register("ftf.gauss", FL, (4, 5))
def ftf_gauss(rng, tier):
    q = rng.randint(1, 9)
    r1, r2 = distinct(rng, 1, 9, 2)
    return {"prompt": f"Muatan titik {q} μC di pusat. Fluks medan listrik melalui bola berjari-jari {r1} cm dibanding bola berjari-jari {r2} cm adalah …",
            "correct": "sama, yaitu q/ε₀", "distractors": [f"bola {max(r1, r2)} cm {max(r1, r2) ** 2 // min(r1, r2) ** 2 or 2} kali lebih besar", f"bola {min(r1, r2)} cm lebih besar",
                                                  "keduanya nol", f"berbanding {r1}:{r2}"],
            "steps": ["E ∝ 1/r² sedangkan luas bola ∝ r²: perkaliannya tidak bergantung r.", "Hukum Gauss: ∯ E·dS = q/ε₀ untuk permukaan tertutup apa pun yang melingkupi q.",
                      "<b>sama, yaitu q/ε₀</b>."], "explanation": "Hukum Gauss = Teorema Divergensi untuk medan listrik."}


# ════════════════════════ Transformasi Laplace ═════════════════════════════
@register("ftp.dasar", LP, (1, 2, 3))
def ftp_dasar(rng, tier):
    a = nz(rng, -4, 4)
    m = rng.randint(1, 4)
    b = rng.randint(1, 5)
    cases = [(f"e<sup>{n(a)}t</sup>", f"1/(s − {paren(a)})", [f"1/(s + {paren(a)})", f"{n(a)}/s", f"1/s{sup(2)}"]),
             (f"t{sup(m) if m > 1 else ''}", f"{math.factorial(m)}/s{sup(m + 1)}", [f"1/s{sup(m)}", f"{m}/s{sup(m)}", f"{math.factorial(m)}/s{sup(m)}"]),
             (f"sin({b}t)", f"{b}/(s² + {b * b})", [f"s/(s² + {b * b})", f"{b}/(s² − {b * b})", f"1/(s² + {b * b})"]),
             (f"cos({b}t)", f"s/(s² + {b * b})", [f"{b}/(s² + {b * b})", f"s/(s² − {b * b})", f"1/(s + {b})"])]
    f, F, wrong = rng.choice(cases[:2] if tier == 1 else cases)
    return {"prompt": f"Tentukan transformasi Laplace ℒ{{{f}}} = ∫<sub>0</sub><sup>∞</sup> e<sup>−st</sup>f(t) dt.", "correct": F, "distractors": wrong + ["tidak ada"],
            "steps": ["Hitung integral tak wajar ∫₀^∞ e<sup>−st</sup>f(t) dt (s cukup besar).", f"ℒ{{{f}}} = <b>{F}</b>."],
            "explanation": "Transformasi Laplace mengubah PD menjadi persamaan aljabar (FT kontrol & rangkaian)."}


@register("ftp.invers", LP, (1, 2, 3, 4, 5))
def ftp_invers(rng, tier):
    a, c = nz(rng, -3, 3), rng.randint(1, 9)
    if tier <= 2:
        F, f = f"{c}/(s − {paren(a)})", f"{c}e<sup>{n(a)}t</sup>"
        wrong = [f"{c}e<sup>{n(-a)}t</sup>", f"{c}t", f"e<sup>{n(a)}t</sup>/{c}"]
    elif tier == 3:
        m = rng.randint(1, 3)
        F, f = f"{math.factorial(m) * c}/s{sup(m + 1)}", f"{c}t{sup(m) if m > 1 else ''}"
        wrong = [f"{math.factorial(m) * c}t{sup(m) if m > 1 else ''}", f"{c}t{sup(m + 1)}", f"{c}e<sup>{m}t</sup>"]
    else:
        p, q = distinct(rng, -3, 3, 2, exclude=(0,))
        A, B = Fr(1, p - q), Fr(1, q - p)
        F = f"1/((s − {paren(p)})(s − {paren(q)}))"
        f = f"{n(A)}e<sup>{n(p)}t</sup> + {n(B)}e<sup>{n(q)}t</sup>".replace("+ −", "− ")
        wrong = [f"e<sup>{n(p)}t</sup> + e<sup>{n(q)}t</sup>", f"{n(B)}e<sup>{n(p)}t</sup> + {n(A)}e<sup>{n(q)}t</sup>".replace("+ −", "− "), f"te<sup>{n(p + q)}t</sup>"]
    return {"prompt": f"Tentukan ℒ<sup>−1</sup>{{{F}}}.", "correct": f, "distractors": wrong + ["0"],
            "steps": ["Cocokkan dengan tabel Laplace (gunakan pecahan parsial bila perlu).", f"<b>{f}</b>."], "explanation": "Invers Laplace lewat tabel & pecahan parsial."}


@register("ftp.pd", LP, (3, 4, 5))
def ftp_pd(rng, tier):
    a, y0 = rng.randint(1, 5), rng.randint(1, 9)
    if tier <= 4:
        return {"prompt": f"Selesaikan y′ + {a}y = 0, y(0) = {y0} dengan transformasi Laplace.", "correct": f"y = {y0}e<sup>−{a}t</sup>",
                "distractors": [f"y = {y0}e<sup>{a}t</sup>", f"y = e<sup>−{a}t</sup> + {y0 - 1}", f"y = {y0}/(s + {a})", f"y = {y0}cos({a}t)"],
                "steps": ["ℒ{y′} = sY − y(0).", f"sY − {y0} + {a}Y = 0 ⇒ Y = {y0}/(s + {a}).", f"Invers: <b>y = {y0}e<sup>−{a}t</sup></b>."],
                "explanation": "Laplace mengubah PD linear menjadi persamaan aljabar dalam Y(s)."}
    k = rng.randint(1, 5)
    return {"prompt": f"Selesaikan y″ + {k * k}y = 0, y(0) = {y0}, y′(0) = 0 dengan transformasi Laplace.", "correct": f"y = {y0}cos({k}t)",
            "distractors": [f"y = {y0}sin({k}t)", f"y = {y0}e<sup>−{k}t</sup>", f"y = {y0}cos({k * k}t)", f"y = {n(Fr(y0, k))}sin({k}t)",
                            f"y = {y0 + 1}cos({k}t)", f"y = {y0}cos({k + 1}t)"],
            "steps": ["ℒ{y″} = s²Y − s·y(0) − y′(0).", f"s²Y − {y0}s + {k * k}Y = 0 ⇒ Y = {y0}s/(s² + {k * k}).", f"<b>y = {y0}cos({k}t)</b> (osilasi pegas tanpa redaman)."],
            "graphs": [g2d("Osilasi y = y₀cos(kt)", [0, 10], [-y0 - 1, y0 + 1], [param("kk", "k", 0.5, 5, 0.5, k, "k")], [fn(f"{y0}*cos(kk*x)", "blue", "y(t)")], None,
                           "k = √(konstanta pegas/massa) menentukan frekuensi.")],
            "explanation": "Getaran mekanik & rangkaian LC."}
