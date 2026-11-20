"""
Topik Level 3 kurikulum v2 yang semula hanya materi: Aturan L'Hôpital (semua bentuk tak tentu).
Rujukan: Stewart §4.4; Whitman §4.7; Strang (MIT) §2.6.
"""

from fractions import Fraction as Fr

from .. import attach, register
from ..fmt import MINUS, n, sup
from ..precalc.common import distinct, nz

LH = "km-lhopital"

attach(LH, "apl.lhopital")


def ax(a, var="x"):
    return var if a == 1 else f"{MINUS}{var}" if a == -1 else f"{n(a)}{var}"


def epow(k):
    return "1" if k == 0 else "e" if k == 1 else f"e{sup(k)}" if isinstance(k, int) else f"e<sup>{n(k)}</sup>"


@register("lh.bentuk", LH, (1, 2, 3, 4, 5))
def lh_bentuk(rng, tier):
    a, b = nz(rng, -6, 6), nz(rng, -6, 6)
    if tier == 1:
        kind = rng.choice(["sin", "pangkat"])
        if kind == "sin":
            val = Fr(a, b)
            prompt, form = f"lim<sub>x→0</sub> sin({ax(a)})/({ax(b)})", "0/0"
            work = f"Turunkan atas & bawah: {n(a)}cos({ax(a)})/{n(b)} → {n(a)}/{n(b)}."
        else:
            c, m = nz(rng, -3, 4), rng.randint(2, 6)
            val = Fr(m * c ** (m - 1))
            xc = f"x {MINUS} {c}" if c > 0 else f"x + {-c}"
            prompt, form = f"lim<sub>x→{n(c)}</sub> (x{sup(m)} − {n(c ** m)})/({xc})".replace("− −", "+ "), "0/0"
            work = f"Turunkan: {m}x{sup(m - 1) if m > 2 else ''}/1 di x = {n(c)}."
    elif tier == 2:
        kind = rng.choice(["dua_exp", "cos"])
        if kind == "dua_exp":
            a, b = distinct(rng, -5, 5, 2)
            val = Fr(a - b)
            prompt, form = f"lim<sub>x→0</sub> (e<sup>{ax(a)}</sup> − e<sup>{ax(b)}</sup>)/x".replace("e<sup>0</sup>", "1").replace("e<sup>0x</sup>", "1"), "0/0"
            work = f"Turunkan: ({n(a)}e<sup>{n(a)}x</sup> − {n(b)}e<sup>{n(b)}x</sup>)/1 → {n(a)} − {n(b)}."
        else:
            val = Fr(a * a, 2 * b)
            prompt, form = f"lim<sub>x→0</sub> (1 − cos({ax(a)}))/({n(b)}x²)", "0/0"
            work = f"L'Hôpital dua kali: {n(a * a)}cos({ax(a)})/({n(2 * b)}) → {n(a * a)}/{n(2 * b)}."
    elif tier == 3:
        a, b = rng.randint(1, 6), rng.randint(1, 6)
        kind = rng.choice(["ln", "lnexp", "polinom"])
        if kind == "ln":
            val = Fr(a, b)
            prompt, form = f"lim<sub>x→∞</sub> ({a}x + ln x)/({b}x − ln x)", "∞/∞"
            work = f"Turunkan: ({a} + 1/x)/({b} − 1/x) → {a}/{b}."
        elif kind == "lnexp":
            val = Fr(a, b)
            prompt, form = f"lim<sub>x→∞</sub> ln(1 + e<sup>{ax(a)}</sup>)/({b}x)", "∞/∞"
            work = f"Turunkan: [{a}e<sup>{a}x</sup>/(1 + e<sup>{a}x</sup>)]/{b} → {a}/{b}."
        else:
            m = rng.randint(1, 4)
            val = Fr(0)
            prompt, form = f"lim<sub>x→∞</sub> (ln x){sup(m) if m > 1 else ''}/x<sup>{n(Fr(1, a))}</sup>", "∞/∞"
            work = f"Logaritma (pangkat berapa pun) kalah oleh xᵖ, p &gt; 0: L'Hôpital {m} kali menyisakan konstanta·(ln x)⁰/x<sup>{n(Fr(1, a))}</sup> → 0."
    elif tier == 4:
        kind = rng.choice(["xln", "xexp", "selisih"])
        if kind == "xln":
            val = Fr(a)
            prompt, form = f"lim<sub>x→∞</sub> x·ln(1 + {n(a)}/x)".replace("+ −", "− "), "∞·0"
            work = f"Tulis ln(1 + {n(a)}/x)/(1/x) (0/0), substitusi t = 1/x: ln(1 + {n(a)}t)/t → {n(a)}."
        elif kind == "xexp":
            val = Fr(a)
            prompt, form = f"lim<sub>x→∞</sub> x(e<sup>{n(a)}/x</sup> − 1)", "∞·0"
            work = f"t = 1/x: (e<sup>{n(a)}t</sup> − 1)/t → {n(a)}."
        else:
            val = Fr(a, 2)
            prompt, form = f"lim<sub>x→0</sub> [1/x − {n(a)}/(e<sup>{ax(a)}</sup> − 1)]", "∞ − ∞"
            work = f"Samakan penyebut: (e<sup>{n(a)}x</sup> − 1 − {n(a)}x)/(x(e<sup>{n(a)}x</sup> − 1)) (0/0); L'Hôpital dua kali → {n(a * a)}/(2·{n(a)})."
    else:
        kind = rng.choice(["e1", "e2", "cos"])
        if kind == "e1":
            val = Fr(a * b)
            prompt, form = f"lim<sub>x→∞</sub> (1 + {n(a)}/x)<sup>{ax(b)}</sup>".replace("+ −", "− "), "1<sup>∞</sup>"
            work = f"ln L = lim {n(b)}x·ln(1 + {n(a)}/x) = {n(b)}·{n(a)}."
        elif kind == "e2":
            val = Fr(a * b)
            prompt, form = f"lim<sub>x→0</sub> (1 + {ax(a)})<sup>{n(b)}/x</sup>".replace("+ −", "− "), "1<sup>∞</sup>"
            work = f"ln L = lim {n(b)}·ln(1 + {n(a)}x)/x = {n(b)}·{n(a)}."
        else:
            b = rng.randint(1, 4)
            val = Fr(-a * a * b, 2)
            prompt, form = f"lim<sub>x→0</sub> (cos({ax(a)}))<sup>{b}/x²</sup>", "1<sup>∞</sup>"
            work = f"ln L = lim {b}·ln cos({n(a)}x)/x² (0/0); L'Hôpital dua kali → −{b}·{n(a * a)}/2."
        correct = epow(val.numerator) if val.denominator == 1 else epow(val)
        wrong = [epow(-val.numerator) if val.denominator == 1 else epow(-val), n(val), "1", epow(val.numerator + 1) if val.denominator == 1 else "∞", "∞"]
        return {"prompt": f"Hitung {prompt}.", "correct": correct, "distractors": wrong,
                "steps": [f"Bentuk {form}: ambil logaritma, L = e<sup>ln L</sup>.", work, f"L = <b>{correct}</b>."],
                "explanation": "Bentuk pangkat (1^∞, 0⁰, ∞⁰): ubah ke eksponen ln, lalu pakai L'Hôpital pada eksponennya."}
    correct = n(val)
    return {"prompt": f"Hitung {prompt}.", "correct": correct, "distractors": [n(-val) if val else "1", n(val * 2) if val else "∞", "tidak ada", n(val + 1)],
            "steps": [f"Bentuk {form}{' — ubah dulu ke 0/0 atau ∞/∞' if form not in ('0/0', '∞/∞') else ''}.", work, f"= <b>{correct}</b>."],
            "explanation": "L'Hôpital: untuk 0/0 atau ∞/∞, lim f/g = lim f′/g′ (bila limit kanan ada)."}
