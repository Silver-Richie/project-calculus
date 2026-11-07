"""
Topik: Sistem Bilangan Real & Interval.
Rujukan: Stewart Lampiran A (Numbers, Inequalities), Whitman Bab 1, Strang (MIT) §0.1.
"""

from fractions import Fraction as Fr
import math

from .. import register
from ..fmt import MINUS, interval, n, surd, sup
from ..graphs import fn, g2d, hline, param, pt, readout
from .common import distinct, number_line

T = "pre-bilangan-real"
OVL = '<span style="text-decoration:overline">{}</span>'


@register("bil.klasifikasi", T, (1, 2))
def klasifikasi(rng, tier):
    nonsq = rng.choice([2, 3, 5, 6, 7, 10, 11, 13])
    sq = rng.randint(2, 9)
    p, q = distinct(rng, 2, 9, 2)
    irr = rng.choice([f"√{nonsq}", "π", f"{rng.randint(1, 5)} + √{nonsq}"])
    rational = [f"√{sq * sq}", f"{p}/{q}", "0," + OVL.format(str(rng.randint(1, 8))), f"{MINUS}{rng.randint(2, 30)}"]
    if tier >= 2:
        k = rng.choice([2, 3, 5])
        m = rng.randint(2, 6)
        irr = rng.choice([f"√{k} · √{k * 4 + 1 if k != 5 else 7}", f"√{2 * k * k}", f"{m}√{k} {MINUS} √{k}"])
        rational = [f"√{k * m * m} / √{k}", f"(√{k})²", f"√{sq * sq * 4}/{sq}", "0,12" + OVL.format("34")]
    rng.shuffle(rational)
    return {
        "prompt": "Manakah bilangan berikut yang merupakan <b>bilangan irasional</b>?",
        "correct": irr,
        "distractors": rational,
        "steps": [
            "Bilangan rasional dapat ditulis sebagai p/q dengan p, q bulat dan q ≠ 0; desimalnya berhenti atau berulang.",
            "Akar dari bilangan kuadrat sempurna (mis. √49 = 7) dan desimal berulang (0,333… = 1/3) termasuk rasional. "
            "Hasil bagi/kali akar yang menghasilkan bilangan bulat juga rasional, mis. √(k·m²)/√k = m dan (√k)² = k.",
            f"Akar dari bilangan yang bukan kuadrat sempurna (√2, √3, …) dan π tidak bisa ditulis sebagai p/q, "
            f"sehingga <b>{irr}</b> irasional.",
        ],
        "explanation": "ℝ = ℚ ∪ (bilangan irasional). Jumlah rasional + irasional selalu irasional.",
    }


@register("bil.notasi_interval", T, (1, 2))
def notasi_interval(rng, tier):
    a, b = sorted(distinct(rng, -6, 8, 2))
    if tier == 1:
        lc, hc = rng.choice([(True, False), (False, True), (True, True), (False, False)])
        sym_l = "≤" if lc else "<"
        sym_h = "≤" if hc else "<"
        setb = f"{{ x ∈ ℝ | {n(a)} {sym_l} x {sym_h} {n(b)} }}"
        correct = interval(a, b, lc, hc)
        wrong = [interval(a, b, not lc, hc), interval(a, b, lc, not hc), interval(a, b, not lc, not hc)]
        graph = number_line("Interval pada garis bilangan", a, b, lc, hc,
                            "Geser ujung a dan b. Titik penuh = ujung ikut (kurung siku), titik kosong = tidak ikut (kurung biasa).")
        steps = [
            f"Tanda {sym_l} di kiri: ujung {n(a)} {'termasuk → kurung siku [' if lc else 'tidak termasuk → kurung biasa ('}.",
            f"Tanda {sym_h} di kanan: ujung {n(b)} {'termasuk → kurung siku ]' if hc else 'tidak termasuk → kurung biasa )'}.",
            f"Jadi himpunannya ditulis <b>{correct}</b>.",
        ]
    else:
        setb = f"{{ x ∈ ℝ | x ≤ {n(a)} atau x > {n(b)} }}"
        correct = f"{interval(None, a, hi_closed=True)} ∪ {interval(b, None, lo_closed=False)}"
        wrong = [
            f"{interval(None, a, hi_closed=False)} ∪ {interval(b, None, lo_closed=True)}",
            f"{interval(None, a, hi_closed=True)} ∩ {interval(b, None, lo_closed=False)}",
            interval(a, b, True, False),
        ]
        graph = number_line("Bagian yang TIDAK termasuk: (a, b]", a, b, False, True,
                            "Ruas hijau adalah komplemen himpunan soal. Himpunan soal = semua bilangan di luar ruas ini.")
        steps = [
            f"“x ≤ {n(a)}” adalah semua bilangan dari −∞ sampai {n(a)} termasuk {n(a)} → {interval(None, a)}.",
            f"“x > {n(b)}” adalah semua bilangan setelah {n(b)} → {interval(b, None, lo_closed=False)}.",
            "Kata “atau” berarti gabungan (∪), bukan irisan.",
            f"Jadi <b>{correct}</b>. Tak hingga selalu memakai kurung biasa.",
        ]
    return {"prompt": f"Tuliskan himpunan {setb} dalam notasi interval.", "correct": correct,
            "distractors": wrong, "steps": steps, "graphs": [graph],
            "explanation": "[ ] = ujung termasuk, ( ) = ujung tidak termasuk; ∞ tidak pernah termasuk."}


@register("bil.operasi_interval", T, (2, 3))
def operasi_interval(rng, tier):
    a, c, b, d = sorted(distinct(rng, -7, 9, 4))   # a < c < b < d → A=[a,b), B=(c,d] beririsan
    op = rng.choice(["∩", "∪"]) if tier == 2 else rng.choice(["∩", "∪", "∖"])
    A, B = interval(a, b, True, False), interval(c, d, False, True)
    if op == "∩":
        correct = interval(c, b, False, False)
        wrong = [interval(a, d, True, True), interval(c, b, True, True), interval(c, b, False, True)]
        why = f"Irisan = bagian yang dimiliki keduanya: dari max({n(a)}, {n(c)}) = {n(c)} (tidak termasuk, karena B buka di {n(c)}) " \
              f"sampai min({n(b)}, {n(d)}) = {n(b)} (tidak termasuk, karena A buka di {n(b)})."
        lo, hi, lc, hc = c, b, False, False
    elif op == "∪":
        correct = interval(a, d, True, True)
        wrong = [interval(c, b, False, False), interval(a, d, False, False), interval(a, d, True, False)]
        why = f"Gabungan = semua bilangan di salah satu interval. Karena keduanya beririsan, hasilnya satu interval " \
              f"dari {n(a)} (termasuk di A) sampai {n(d)} (termasuk di B)."
        lo, hi, lc, hc = a, d, True, True
    else:
        correct = interval(a, c, True, True)
        wrong = [interval(a, c, True, False), interval(b, d, True, True), interval(c, b, False, False)]
        why = f"A ∖ B = anggota A yang bukan anggota B. B dimulai setelah {n(c)} (buka), jadi {n(c)} masih milik A ∖ B."
        lo, hi, lc, hc = a, c, True, True
    return {
        "prompt": f"Diketahui A = {A} dan B = {B}. Tentukan A {op} B.",
        "correct": correct, "distractors": wrong,
        "steps": [f"Gambar kedua interval di garis bilangan: A dari {n(a)} sampai {n(b)}, B dari {n(c)} sampai {n(d)}.",
                  why, f"Hasil: <b>{correct}</b>."],
        "graphs": [number_line(f"Hasil A {op} B", lo, hi, lc, hc,
                               "Geser ujung hasil untuk melihat bagaimana panjang dan jenis ujung interval berubah.",
                               xr=[a - 3, d + 3])],
        "explanation": "∩ = dan (keduanya), ∪ = atau (salah satu), ∖ = selisih.",
    }


@register("bil.desimal_berulang", T, (2, 3, 4))
def desimal_berulang(rng, tier):
    if tier == 2:
        d = rng.randint(1, 8)
        val, shown = Fr(d, 9), "0," + OVL.format(str(d))
        work = [f"Misal x = {shown} = 0,{d}{d}{d}…", f"10x = {d},{d}{d}{d}…",
                f"10x − x = {d} ⇒ 9x = {d} ⇒ x = {d}/9."]
        wrong = [Fr(d, 10), Fr(d, 99), Fr(d + 1, 9)]
    elif tier == 3:
        ab = rng.choice([v for v in range(10, 99) if v % 11])
        val, shown = Fr(ab, 99), "0," + OVL.format(str(ab))
        work = [f"Misal x = {shown} (blok berulang 2 digit, jadi kalikan 100).", f"100x = {ab},{ab}{ab}…",
                f"100x − x = {ab} ⇒ 99x = {ab} ⇒ x = {ab}/99."]
        wrong = [Fr(ab, 100), Fr(ab, 90), Fr(ab, 999)]
    else:
        a, b = rng.randint(1, 9), rng.randint(1, 9)
        while a == b:
            b = rng.randint(1, 9)
        val, shown = Fr(10 * a + b - a, 90), f"0,{a}" + OVL.format(str(b))
        work = [f"Misal x = {shown} = 0,{a}{b}{b}{b}…", f"100x = {a}{b},{b}{b}…  dan  10x = {a},{b}{b}…",
                f"100x − 10x = {10 * a + b} − {a} ⇒ 90x = {10 * a + b - a} ⇒ x = {10 * a + b - a}/90."]
        wrong = [Fr(10 * a + b, 99), Fr(10 * a + b, 90), Fr(10 * a + b - a, 99)]
    fv = float(val)
    work.append(f"Sederhanakan: x = <b>{n(val)}</b>.")
    graph = g2d("Jumlah parsial desimal mendekati nilai pecahan", [0, 8], [0, max(1.0, fv * 1.3)],
                [param("N", "Banyak digit yang diambil N", 1, 8, 1, 3, "N")],
                [fn(f"{fv}*(1-pow(10,-floor(x)))", "blue", "nilai desimal dipotong"),
                 hline(fv, "red"), pt("N", f"{fv}*(1-pow(10,-N))", "red", label="N digit")],
                [readout("Desimal dipotong N digit (≈)", f"{fv}*(1-pow(10,-N))", 8), readout("Nilai pecahan", str(fv), 8),
                 readout("Selisih", f"{fv}*pow(10,-N)", 10)],
                "Tambah N: selisih mengecil 10 kali lipat setiap digit. Desimal berulang adalah limit barisan ini.")
    return {"prompt": f"Nyatakan desimal berulang {shown} sebagai pecahan paling sederhana.",
            "correct": n(val), "distractors": [n(w) for w in wrong] + [n(val + Fr(1, 9))],
            "steps": work, "graphs": [graph],
            "explanation": "Kalikan dengan 10ᵏ (k = panjang blok berulang) lalu kurangkan agar ekor berulang hilang."}


@register("bil.eksponen", T, (1, 2, 3))
def eksponen(rng, tier):
    if tier == 1:
        base = rng.choice([2, 3])
        m, k = rng.randint(2, 5), rng.randint(1, 4)
        nn = rng.randint(1, 4)
        e = m + nn - k
        while e < 0 or e > 6:
            k = rng.randint(1, 4)
            e = m + nn - k
        prompt = f"Hitung nilai ({base}{sup(m)} · {base}{sup(nn)}) / {base}{sup(k)}."
        correct = n(base ** e)
        wrong = [n(base ** (m + nn + k)), n(base ** (e + 1)), n(base * e), n(base ** e + base), n(base ** (e + 2))]
        steps = [f"aᵐ · aⁿ = aᵐ⁺ⁿ: {base}{sup(m)} · {base}{sup(nn)} = {base}{sup(m + nn)}.",
                 f"aᵐ / aᵏ = aᵐ⁻ᵏ: {base}{sup(m + nn)} / {base}{sup(k)} = {base}{sup(e)}.",
                 f"{base}{sup(e)} = <b>{base ** e}</b>."]
    elif tier == 2:
        p, q, r, s = rng.randint(2, 6), rng.randint(1, 5), rng.randint(1, 4), rng.randint(2, 6)
        ex, ey = p - r, q * 2 - s
        prompt = f"Sederhanakan (x{sup(p)} · (y{sup(q)})²) / (x{sup(r)} · y{sup(s)}), dengan x, y ≠ 0."

        def mono(a, b):
            parts = [f"x{sup(a) if a != 1 else ''}" if a else "", f"y{sup(b) if b != 1 else ''}" if b else ""]
            return "".join(parts) or "1"
        correct = mono(ex, ey)
        wrong = [mono(p - r, q + 2 - s), mono(p + r, 2 * q + s), mono(p * r, q * s),
                 mono(ex + 1, ey), mono(ex, ey - 1), mono(ex - 1, ey + 1)]
        steps = [f"(y{sup(q)})² = y{sup(2 * q)} (pangkat dipangkatkan → dikali).",
                 f"Pangkat x: {p} − {r} = {n(ex)}; pangkat y: {2 * q} − {s} = {n(ey)}.",
                 f"Hasil: <b>{correct}</b> (pangkat negatif berarti berada di penyebut)."]
    else:
        b0, q = rng.choice([(2, 3), (3, 3), (2, 4), (3, 2), (2, 5), (4, 2), (5, 2)])
        p = rng.choice([v for v in (1, 2, 3, -1, -2, -3) if v % q and abs(v) < q + 2])
        a = b0 ** q
        val = Fr(b0) ** p
        prompt = f"Hitung {a}<sup>{n(Fr(p, q))}</sup>."
        correct = n(val)
        wrong = [n(Fr(a * p, q)), n(Fr(b0) ** (-p)), n(Fr(b0) ** (p + (1 if p > 0 else -1)))]
        steps = [f"a<sup>p/q</sup> = (ᵠ√a)ᵖ. Akar pangkat {q} dari {a} adalah {b0} karena {b0}{sup(q)} = {a}.",
                 f"Lalu pangkatkan {n(p)}: {b0}{sup(p)} = <b>{correct}</b>"
                 + (" (pangkat negatif = kebalikan)." if p < 0 else ".")]
    return {"prompt": prompt, "correct": correct, "distractors": wrong, "steps": steps,
            "explanation": "aᵐ·aⁿ = aᵐ⁺ⁿ, aᵐ/aⁿ = aᵐ⁻ⁿ, (aᵐ)ⁿ = aᵐⁿ, a⁻ⁿ = 1/aⁿ, a^(p/q) = (ᵠ√a)ᵖ."}


@register("bil.rasionalisasi", T, (3, 4))
def rasionalisasi(rng, tier):
    while True:
        b = rng.choice([2, 3, 5, 6, 7, 10, 11])
        c = rng.randint(1, 4)
        den = b - c * c
        if den not in (0, 1, -1):
            break
    a = den * rng.choice([1, 2, 3, -1, -2])
    k = Fr(a, den)
    sgn = rng.choice(["+", MINUS]) if tier == 4 else MINUS
    plus = sgn == "+"
    conj = MINUS if plus else "+"
    num_c = -c if plus else c

    def form(kk, cc):
        inner = f"√{b} {MINUS if cc < 0 else '+'} {abs(cc)}"
        if kk == 1:
            return inner
        return f"{MINUS}({inner})" if kk == -1 else f"{n(kk)}({inner})"
    correct = form(k, num_c)
    wrong = [form(k, -num_c), form(Fr(a, b + c * c), num_c), form(-k, num_c)]
    return {
        "prompt": f"Rasionalkan penyebut dari {n(a)} / (√{b} {sgn} {c}).",
        "correct": correct, "distractors": wrong,
        "steps": [f"Kalikan pembilang & penyebut dengan sekawan penyebut: (√{b} {conj} {c}).",
                  f"Penyebut: (√{b} {sgn} {c})(√{b} {conj} {c}) = {b} − {c * c} = {n(den)}.",
                  f"Hasil: {n(a)}(√{b} {conj} {c}) / {n(den)} = <b>{correct}</b>."],
        "explanation": "(√p + q)(√p − q) = p − q² menghilangkan akar dari penyebut.",
    }


@register("bil.akar_bersusun", T, (4, 5))
def akar_bersusun(rng, tier):
    p, q = rng.sample([2, 3, 5, 6, 7, 10, 11, 13], 2)
    p, q = max(p, q), min(p, q)
    m, k = p + q, p * q
    sign = "+" if tier == 4 else rng.choice(["+", MINUS])
    correct = f"√{p} {sign} √{q}"
    other = MINUS if sign == "+" else "+"
    wrong = [f"√{p} {other} √{q}", f"√{m} {sign} √{k}", f"√{m + 1} {sign} √{k - 1}", f"√{k} {sign} 1"]
    return {
        "prompt": f"Sederhanakan √({m} {sign} 2√{k}).",
        "correct": correct, "distractors": wrong,
        "steps": [f"Cari bentuk (√p {sign} √q)² = p + q {sign} 2√(pq).",
                  f"Perlu p + q = {m} dan p·q = {k}. Pasangan yang cocok: p = {p}, q = {q}.",
                  f"Karena p > q maka √p {sign} √q bernilai positif, jadi √({m} {sign} 2√{k}) = <b>{correct}</b>."],
        "explanation": "√(a ± 2√b) = √p ± √q bila p + q = a dan pq = b (p ≥ q).",
    }


@register("bil.teleskopik", T, (5,))
def teleskopik(rng, tier):
    s = rng.randint(4, 12)
    N = s * s - 1
    return {
        "prompt": f"Hitung 1/(√1 + √2) + 1/(√2 + √3) + … + 1/(√{N} + √{N + 1}).",
        "correct": n(s - 1), "distractors": [n(s), n(s + 1), n(N // 2), n(s * 2 - 1)],
        "steps": ["Rasionalkan setiap suku: 1/(√k + √(k+1)) = (√(k+1) − √k) / ((k+1) − k) = √(k+1) − √k.",
                  f"Jumlahnya teleskopik: (√2 − √1) + (√3 − √2) + … + (√{N + 1} − √{N}).",
                  f"Semua suku tengah saling menghapus: √{N + 1} − 1 = {s} − 1 = <b>{s - 1}</b>."],
        "graphs": [g2d("Jumlah parsial S(N) = √(N+1) − 1", [0, N + 5], [0, s + 1],
                       [param("M", "Banyak suku M", 1, N + 4, 1, N, "M")],
                       [fn("sqrt(x+1)-1", "blue", "S(x) = √(x+1) − 1"),
                        pt("M", "sqrt(M+1)-1", "red", label="S(M)")],
                       [readout("S(M)", "sqrt(M+1)-1", 5)],
                       "Geser M: jumlah tumbuh seperti √M (lambat), tetapi tidak pernah berhenti naik.")],
        "explanation": "Teknik teleskopik: tulis suku sebagai selisih f(k+1) − f(k).",
    }


@register("bil.banding_pangkat", T, (4, 5))
def banding_pangkat(rng, tier):
    pairs = [(2, 3, 8), (3, 2, 9), (5, 1, 5), (7, 1, 7), (2, 2, 4), (6, 1, 6), (3, 1, 3)]
    chosen = rng.sample(pairs, 4)
    k = rng.choice([100, 50, 25]) if tier == 4 else rng.choice([111, 37, 125])
    label = [f"{b}<sup>{e * k}</sup>" for b, e, _ in chosen]
    best = max(range(4), key=lambda i: chosen[i][2])
    return {
        "prompt": f"Manakah bilangan terbesar di antara: {', '.join(label)}?",
        "correct": label[best], "distractors": [lbl for i, lbl in enumerate(label) if i != best],
        "steps": [f"Semua pangkat adalah kelipatan {k}, jadi tulis aⁿᵏ = (aⁿ)ᵏ.",
                  "Bandingkan bilangan dasarnya: " + ", ".join(f"{b}{sup(e)} = {v}" for b, e, v in chosen) + ".",
                  f"Karena pangkat sama ({k}) dan semua basis positif, yang terbesar adalah basis terbesar → <b>{label[best]}</b>."],
        "explanation": "Untuk x, y > 0 dan k > 0: x < y ⇔ xᵏ < yᵏ.",
    }
