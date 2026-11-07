"""
Topik: Fungsi Logaritma — definisi, sifat, ganti basis, persamaan, pertidaksamaan, invers, aplikasi.
Rujukan: Stewart §1.5 (Inverse Functions and Logarithms); Strang (MIT) §6.4; Whitman §4.6.
"""

from fractions import Fraction as Fr
import math

from .. import register
from ..fmt import MINUS, interval, n, paren, poly_in, sub_, sup
from ..graphs import fn, g2d, hline, param, pt, readout
from .common import distinct, nz

T = "pre-fungsi-logaritma"


def lg(b, arg):
    """Teks log basis b: lg(2, 'x') → '²log x' ditulis log₂ x."""
    return f"log{sub_(b)} {arg}"


@register("log.nilai", T, (1, 2))
def nilai(rng, tier):
    b = rng.choice([2, 3, 5, 10])
    k = rng.randint(-3, 4) if tier == 2 else rng.randint(1, 4)
    if tier == 1:
        arg, val = b ** k, Fr(k)
        prompt = f"Hitung {lg(b, arg)}."
        steps = ["logᵦ a = c ⇔ bᶜ = a.", f"Cari c dengan {b}ᶜ = {arg}: {b}{sup(k)} = {arg}.", f"Jadi <b>{k}</b>."]
    else:
        m = rng.choice([2, 3])
        bb = b ** m if b ** m < 200 else b
        mm = m if bb != b else 1
        arg = f"1/{b ** -k}" if k < 0 else str(b ** k)
        val = Fr(k, mm)
        prompt = f"Hitung {lg(bb, arg)}."
        steps = [f"Tulis kedua bilangan dalam basis {b}: {bb} = {b}{sup(mm)}, {arg} = {b}{sup(k)}.",
                 f"log<sub>{b}{sup(mm)}</sub> {b}{sup(k)} = {k}/{mm}.", f"Jadi <b>{n(val)}</b>."]
    return {"prompt": prompt, "correct": n(val), "distractors": [n(-val), n(val + 1), n(Fr(1, 1) / val if val else 2), n(val * 2)],
            "steps": steps,
            "graphs": [g2d("y = log_b x dan y = bˣ saling invers", [-4, 10], [-4, 6],
                           [param("bb", "Basis b", 1.2, 10, 0.1, b, "b"), param("s", "x", 0.1, 9, 0.05, 2, "x")],
                           [fn("log(x)/log(bb)", "blue", "log_b x", **{"from": 0.01}), fn("pow(bb,x)", "orange", "bˣ"), fn("x", "gray", "y = x", dash=True),
                            pt("s", "log(s)/log(bb)")],
                           [readout("log_b x", "log(s)/log(bb)", 4)],
                           "Logaritma menjawab: “b dipangkatkan berapa supaya menjadi x?”")],
            "explanation": "logᵦ a = c ⇔ bᶜ = a (b > 0, b ≠ 1, a > 0)."}


@register("log.sifat", T, (1, 2))
def sifat(rng, tier):
    b = rng.choice([2, 3, 5, 10])
    k = rng.randint(1, 4)
    p = rng.choice([2, 3, 5, 6, 7])
    q = b ** k * p
    if tier == 1:
        prompt = f"Sederhanakan {lg(b, q)} − {lg(b, p)}."
        val = Fr(k)
        steps = ["logᵦ a − logᵦ c = logᵦ(a/c).", f"{lg(b, f'({q}/{p})')} = {lg(b, b ** k)} = <b>{k}</b>."]
    else:
        r = rng.choice([2, 3, 4])
        prompt = f"Sederhanakan {r}·{lg(b, p)} + {lg(b, q)} − {lg(b, p ** (r + 1))}."
        val = Fr(k)
        steps = [f"{r}·{lg(b, p)} = {lg(b, p ** r)} (sifat pangkat).",
                 f"Gabungkan: {lg(b, f'({p ** r}·{q}/{p ** (r + 1)})')} = {lg(b, b ** k)}.", f"= <b>{k}</b>."]
    return {"prompt": prompt, "correct": n(val), "distractors": [n(val + 1), n(Fr(q, p)), n(val - 1), n(math.log(q - p, b)) if q - p > 0 else n(val + 2)],
            "steps": steps,
            "explanation": "log(ac) = log a + log c; log(a/c) = log a − log c; log(aⁿ) = n log a."}


@register("log.ganti_basis", T, (2, 3))
def ganti_basis(rng, tier):
    p = rng.choice([2, 3])
    if tier == 2:
        m, nn = distinct(rng, 1, 5, 2)
        prompt = f"Hitung {lg(p ** m, p ** nn)}."
        val = Fr(nn, m)
        steps = ["Ganti basis: logₐ b = log b / log a (basis apa pun).",
                 f"= log {p}{sup(nn)} / log {p}{sup(m)} = {nn}·log {p} / ({m}·log {p}) = <b>{n(val)}</b>."]
    else:
        q = 5 if p != 5 else 7
        e = rng.randint(2, 5)
        prompt = f"Hitung {lg(p, q)} · {lg(q, p ** e)}."
        val = Fr(e)
        steps = ["Rantai: logₐ b · log_b c = logₐ c (tulis keduanya dengan basis yang sama, faktor log b saling coret).",
                 f"= {lg(p, p ** e)} = <b>{e}</b>."]
    return {"prompt": prompt, "correct": n(val), "distractors": [n(Fr(1) / val), n(val + 1), n(val * 2), n(val - Fr(1, 2))], "steps": steps,
            "explanation": "logₐ b = (log_c b)/(log_c a)."}


@register("log.persamaan", T, (2, 3, 4))
def persamaan(rng, tier):
    b = rng.choice([2, 3])
    if tier == 2:
        k, p = rng.randint(1, 4), rng.randint(-6, 6)
        x = b ** k - p
        prompt = f"Selesaikan {lg(b, f'(x {MINUS if p < 0 else '+'} {abs(p)})')} = {k}."
        correct = f"x = {n(x)}"
        wrong = [f"x = {n(b * k - p)}", f"x = {n(b ** k + p)}", f"x = {n(k ** b - p)}", f"x = {n(x + 1)}"]
        steps = [f"Definisi: x {'+' if p >= 0 else MINUS} {abs(p)} = {b}{sup(k)} = {b ** k}.", f"x = <b>{n(x)}</b>. Cek: argumen {b ** k} &gt; 0 ✓."]
    elif tier == 3:
        # log_b x + log_b (x − d) = k ⇒ x(x − d) = b^k, pilih akar bulat
        while True:
            r = rng.randint(2, 9)
            d = rng.randint(1, r - 1)
            if math.log(r * (r - d), b).is_integer():
                break
            if b == 2 and r * (r - d) in (2, 4, 8, 16, 32, 64):
                break
        k = round(math.log(r * (r - d), b))
        other = -(r - d)
        prompt = f"Selesaikan {lg(b, 'x')} + {lg(b, f'(x − {d})')} = {k}."
        correct = f"x = {n(r)}"
        wrong = [f"x = {n(r)} atau x = {n(other)}", f"x = {n(other)}", f"x = {n(r + 1)}", f"x = {n(b ** k)}"]
        steps = [f"Gabungkan: {lg(b, f'x(x − {d})')} = {k} ⇒ x² − {d}x = {b ** k}.",
                 f"x² − {d}x − {b ** k} = 0 ⇒ (x − {r})(x + {r - d}) = 0 ⇒ x = {r} atau x = {n(other)}.",
                 f"Syarat: x &gt; {d} (argumen log positif). x = {n(other)} ditolak. Jawaban: <b>x = {r}</b>."]
    else:
        r1, r2 = distinct(rng, -1, 4, 2)
        S, P = r1 + r2, r1 * r2
        prompt = f"Selesaikan {poly_in([1, -S, P], lg(b, 'x'))} = 0."
        xs = sorted([Fr(b) ** r1, Fr(b) ** r2])
        correct = f"x = {n(xs[0])} atau x = {n(xs[1])}"
        wrong = [f"x = {n(min(r1, r2))} atau x = {n(max(r1, r2))}", f"x = {n(xs[1])}", f"x = {n(xs[0] * b)} atau x = {n(xs[1] * b)}",
                 f"x = {n(Fr(b) ** -r1)} atau x = {n(Fr(b) ** -r2)}"]
        steps = [f"Misal u = {lg(b, 'x')}: u² {MINUS if S > 0 else '+'} {abs(S)}u {'+' if P >= 0 else MINUS} {abs(P)} = 0 ⇒ u = {r1} atau u = {r2}.",
                 f"x = {b}ᵘ ⇒ <b>{correct}</b>. (u boleh negatif; x tetap positif.)"]
    return {"prompt": prompt, "correct": correct, "distractors": wrong, "steps": steps,
            "graphs": [g2d(f"y = log_{b} x: hanya terdefinisi untuk x > 0", [-3, 20], [-4, 6],
                           [param("s", "x uji", 0.1, 19, 0.05, 3, "x")],
                           [fn(f"log(x)/log({b})", "blue", f"log{sub_(b)} x", **{"from": 0.01}), pt("s", f"log(s)/log({b})")],
                           [readout(f"log{sub_(b)} x", f"log(s)/log({b})", 4)],
                           "Grafik log tidak ada di x ≤ 0: itulah sebabnya akar yang membuat argumen ≤ 0 harus ditolak.")],
            "explanation": "Selalu cek syarat numerus (argumen) logaritma > 0 setelah menyelesaikan."}


@register("log.aplikasi", T, (2, 3))
def aplikasi(rng, tier):
    kind = rng.choice(["ph", "bit", "biner"])
    if kind == "ph":
        k = rng.randint(2, 12)
        prompt = f"Larutan (FMIPA) memiliki [H⁺] = 10<sup>{MINUS}{k}</sup> mol/L. Dengan pH = −log[H⁺], berapa pH-nya?"
        correct, wrong = str(k), [f"{MINUS}{k}", str(10 - k if k != 5 else 6), str(k * 10), str(14 - k if 14 - k != k else k + 1)]
        steps = [f"log 10<sup>−{k}</sup> = −{k}.", f"pH = −(−{k}) = <b>{k}</b>. {'Asam' if k < 7 else 'Netral' if k == 7 else 'Basa'}."]
        expr, xr, x0 = "-log10(x)", [1e-12, 1e-1], 10 ** -k
    elif kind == "bit":
        N = rng.choice([100, 200, 300, 500, 1000, 1500, 3000, 5000])
        bits = math.ceil(math.log2(N))
        prompt = f"Berapa bit minimum (Fasilkom) untuk memberi kode unik kepada {N} pengguna?"
        correct, wrong = f"{bits} bit", [f"{bits - 1} bit", f"{bits + 1} bit", f"{len(str(N))} bit", f"{N // 2} bit"]
        steps = [f"Dengan b bit ada 2ᵇ kode berbeda. Perlu 2ᵇ ≥ {N} ⇒ b ≥ log₂ {N} ≈ {math.log2(N):.2f}.",
                 f"b bulat ⇒ b = ⌈{math.log2(N):.2f}⌉ = <b>{bits}</b>. (2{sup(bits - 1)} = {2 ** (bits - 1)} masih kurang.)"]
        expr, xr, x0 = "log2(x)", [1, 6000], N
    else:
        N = rng.choice([1000, 10_000, 100_000, 1_000_000, 50_000])
        steps_n = math.floor(math.log2(N)) + 1
        prompt = f"Binary search pada data terurut berisi {N:,} elemen memerlukan paling banyak berapa perbandingan?".replace(",", ".")
        correct, wrong = str(steps_n), [str(N // 2), str(steps_n + 3), str(round(math.log10(N))), str(steps_n * 2)]
        steps = ["Setiap perbandingan membuang separuh data: setelah k langkah tersisa N/2ᵏ.",
                 f"Berhenti saat tersisa 1 elemen: k ≈ log₂ N = {math.log2(N):.2f} ⇒ paling banyak ⌊log₂ N⌋ + 1 = <b>{steps_n}</b>."]
        expr, xr, x0 = "floor(log2(x))+1", [1, N * 1.2], N
    return {"prompt": prompt, "correct": correct, "distractors": wrong, "steps": steps,
            "graphs": [g2d("Logaritma tumbuh sangat lambat", [1, 2000 if kind != "ph" else 14], [0, 14],
                           [param("s", "x", 1, 2000 if kind != "ph" else 14, 1 if kind != "ph" else 0.1, min(x0, 2000) if kind != "ph" else k, "x")],
                           [fn("log2(x)" if kind != "ph" else "x", "blue", "log₂ x" if kind != "ph" else "pH"),
                            fn("x/100" if kind != "ph" else "7", "orange", "x/100 (linear)" if kind != "ph" else "netral", dash=True)],
                           [readout("log₂ x" if kind != "ph" else "[H⁺] = 10^(−pH)", "log2(s)" if kind != "ph" else "pow(10,-s)", 6)],
                           "Menggandakan x hanya menambah log₂ x sebesar 1 — inilah efisiensi algoritma O(log n).")],
            "explanation": "Logaritma mengubah perkalian menjadi penjumlahan; dipakai untuk skala (pH, dB) dan kompleksitas algoritma."}


@register("log.invers", T, (2, 3))
def invers(rng, tier):
    b = rng.choice([2, 3, 10])
    h, k = nz(rng, -4, 4), nz(rng, -4, 4)
    if tier == 2:
        prompt = f"Tentukan invers f(x) = {b}ˣ."
        correct, wrong = f"f⁻¹(x) = {lg(b, 'x')}", [f"f⁻¹(x) = {lg('x', b)}", f"f⁻¹(x) = x/{b}", f"f⁻¹(x) = {b}⁻ˣ", f"f⁻¹(x) = x^(1/{b})"]
        steps = [f"y = {b}ˣ ⇔ x = {lg(b, 'y')}.", f"Tukar variabel: <b>{correct}</b>."]
        fexpr, iexpr = f"pow({b},x)", f"log(x)/log({b})"
    else:
        prompt = f"Tentukan invers f(x) = {b}<sup>x {MINUS if h > 0 else '+'} {abs(h)}</sup> {'+' if k > 0 else MINUS} {abs(k)}."
        correct = f"f⁻¹(x) = {lg(b, f'(x {MINUS if k > 0 else '+'} {abs(k)})')} {'+' if h > 0 else MINUS} {abs(h)}"
        wrong = [f"f⁻¹(x) = {lg(b, f'(x {MINUS if h > 0 else '+'} {abs(h)})')} {'+' if k > 0 else MINUS} {abs(k)}",
                 f"f⁻¹(x) = {lg(b, f'(x {'+' if k > 0 else MINUS} {abs(k)})')} {MINUS if h > 0 else '+'} {abs(h)}",
                 f"f⁻¹(x) = {lg(b, 'x')} {MINUS if k > 0 else '+'} {abs(k)}", f"f⁻¹(x) = {lg(b, f'(x {MINUS if k > 0 else '+'} {abs(k)})')}"]
        steps = [f"y − {paren(k)} = {b}<sup>x − {paren(h)}</sup> ⇒ x − {paren(h)} = {lg(b, f'(y − {paren(k)})')}.",
                 f"Tukar variabel: <b>{correct}</b>. Asimtot datar y = {k} pada f menjadi asimtot tegak x = {k} pada f⁻¹."]
        fexpr, iexpr = f"pow({b},x-({h}))+({k})", f"log(x-({k}))/log({b})+({h})"
    return {"prompt": prompt, "correct": correct, "distractors": wrong, "steps": steps,
            "graphs": [g2d("f dan f⁻¹ bercermin terhadap y = x", [-8, 10], [-8, 10],
                           [param("s", "s", -6, 4, 0.05, 0, "s")],
                           [fn(fexpr, "blue", "f"), fn(iexpr, "orange", "f⁻¹"), fn("x", "gray", "y = x", dash=True),
                            pt("s", fexpr.replace("x", "s"), "blue"), pt(fexpr.replace("x", "s"), "s", "orange")],
                           None, "Titik (s, f(s)) dan (f(s), s) selalu simetris terhadap garis y = x.")],
            "explanation": "Logaritma adalah invers eksponen: b^(log_b x) = x dan log_b(bˣ) = x."}


@register("log.pertidaksamaan", T, (4, 5))
def pertidaksamaan(rng, tier):
    a = rng.randint(-5, 5)
    k = rng.randint(1, 3)
    small = tier == 5 and rng.random() < 0.6
    base = "1/2" if small else "2"
    op = rng.choice(["&lt;", "&gt;"])
    if not small:
        bound = a + 2 ** k
        correct = interval(a, bound, False, False) if op == "&lt;" else interval(bound, None, lo_closed=False)
        wrong = [interval(None, bound, hi_closed=False) if op == "&lt;" else interval(a, bound, False, False), interval(a, a + 2 * k, False, False),
                 interval(a, bound, True, False), interval(bound, None, lo_closed=False) if op == "&lt;" else interval(None, bound, hi_closed=False)]
        steps = [f"Syarat numerus: x − {paren(a)} &gt; 0 ⇒ x &gt; {a}.", f"Basis 2 &gt; 1 (naik), tanda tetap: x − {paren(a)} {op} 2{sup(k)} = {2 ** k}.",
                 f"Gabungkan dengan syarat: <b>{correct}</b>."]
    else:
        bound = a + Fr(1, 2 ** k)
        correct = interval(a, bound, False, False) if op == "&gt;" else interval(bound, None, lo_closed=False)
        wrong = [interval(bound, None, lo_closed=False) if op == "&gt;" else interval(a, bound, False, False), interval(a, a + 2 ** k, False, False),
                 interval(None, bound, hi_closed=False), interval(a, bound, True, True)]
        steps = [f"Syarat numerus: x &gt; {a}.", f"Basis 1/2 (fungsi turun) ⇒ tanda dibalik: x − {paren(a)} {'&lt;' if op == '&gt;' else '&gt;'} (1/2){sup(k)} = 1/{2 ** k}.",
                 f"Gabungkan dengan syarat: <b>{correct}</b>."]
    return {"prompt": f"Selesaikan log<sub>{base}</sub>(x {MINUS if a > 0 else '+'} {abs(a)}) {op} {k}.", "correct": correct, "distractors": wrong,
            "steps": steps,
            "graphs": [g2d("Grafik log dan garis y = k", [a - 1, a + 10], [-5, 5],
                           [param("kk", "k", -3, 4, 0.5, k, "k")],
                           [fn(f"log(x-({a}))/log({0.5 if small else 2})", "blue", "y", **{"from": a + 0.01}),
                            {"type": "hline", "y": "kk", "color": "red", "dash": True},
                            {"type": "vline", "x": a, "color": "gray", "dash": True}],
                           [readout("batas x", f"{a}+pow({0.5 if small else 2},kk)", 4)],
                           "Garis abu-abu = asimtot tegak (syarat numerus). Penyelesaian = bagian grafik di bawah/atas garis merah.")],
            "explanation": "Pertidaksamaan log: (1) syarat numerus > 0, (2) basis > 1 tanda tetap, 0 < basis < 1 tanda dibalik."}


@register("log.basis_berantai", T, (4, 5))
def basis_berantai(rng, tier):
    L = rng.choice([4, 8, 12]) if tier == 4 else rng.choice([8, 16])
    if tier == 4:
        target = Fr(7 * L, 4)
        prompt = f"Selesaikan log₂ x + log₄ x + log₁₆ x = {n(target)}."
        steps = ["Ubah ke basis 2: log₄ x = (log₂ x)/2, log₁₆ x = (log₂ x)/4.",
                 f"(1 + 1/2 + 1/4)·log₂ x = 7/4·log₂ x = {n(target)} ⇒ log₂ x = {L}.", f"x = 2{sup(L)} = <b>{2 ** L}</b>."]
    else:
        target = Fr(15 * L, 8)
        prompt = f"Selesaikan log₂ x + log₄ x + log₁₆ x + log₂₅₆ x = {n(target)}."
        steps = ["Ubah ke basis 2: log₄ x = (log₂ x)/2, log₁₆ x = (log₂ x)/4, log₂₅₆ x = (log₂ x)/8.",
                 f"15/8 · log₂ x = {n(target)} ⇒ log₂ x = {L}.", f"x = 2{sup(L)} = <b>{2 ** L}</b>."]
    return {"prompt": prompt, "correct": n(2 ** L), "distractors": [n(L), n(2 ** (L - 1)), n(4 ** L) if L < 10 else n(2 ** (L + 1)), n(2 ** (L // 2))],
            "steps": steps, "explanation": "log_{bⁿ} x = (log_b x)/n."}
