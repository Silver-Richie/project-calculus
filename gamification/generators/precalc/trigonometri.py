"""
Topik: Fungsi Trigonometri — radian, sudut istimewa, identitas, grafik sinusoidal, persamaan.
Rujukan: Stewart Lampiran D (Trigonometry) & §1.2; Strang (MIT) §1.4–1.5; Whitman §4.1.
"""

from fractions import Fraction as Fr
import math

from .. import register
from ..fmt import MINUS, n
from ..graphs import fn, g2d, hline, param, pt, readout

T = "pre-fungsi-trigonometri"

# Nilai eksak untuk sudut acuan di kuadran I.
_SIN = {0: "0", 30: "1/2", 45: "√2/2", 60: "√3/2", 90: "1"}
_COS = {0: "1", 30: "√3/2", 45: "√2/2", 60: "1/2", 90: "0"}
_TAN = {0: "0", 30: "√3/3", 45: "1", 60: "√3", 90: "tidak terdefinisi"}
ALL_VALUES = ["0", "1/2", "√2/2", "√3/2", "1", "√3/3", "√3", f"{MINUS}1/2", f"{MINUS}√2/2", f"{MINUS}√3/2", f"{MINUS}1",
              f"{MINUS}√3/3", f"{MINUS}√3"]


def neg(s):
    if s in ("0", "tidak terdefinisi"):
        return s
    return s[1:] if s.startswith(MINUS) else MINUS + s


def exact(func, deg):
    """Nilai eksak sin/cos/tan untuk kelipatan 30° atau 45° (0 ≤ deg < 360)."""
    deg %= 360
    q = deg // 90
    ref = {0: deg, 1: 180 - deg, 2: deg - 180, 3: 360 - deg}[q] if deg % 90 else (0 if deg in (0, 180) else 90)
    base = {"sin": _SIN, "cos": _COS, "tan": _TAN}[func][ref]
    sign = {"sin": math.sin, "cos": math.cos, "tan": math.tan}[func](math.radians(deg))
    if func == "tan" and deg % 180 == 90:
        return "tidak terdefinisi"
    return neg(base) if sign < -1e-9 else base


def rad_text(deg):
    """Derajat → radian dalam bentuk kelipatan π."""
    f = Fr(deg, 180)
    if f == 0:
        return "0"
    num = "" if abs(f.numerator) == 1 else str(abs(f.numerator))
    s = f"{num}π" + (f"/{f.denominator}" if f.denominator != 1 else "")
    return (MINUS + s) if f < 0 else s


def unit_circle(deg, caption):
    return g2d("Lingkaran satuan: titik (cos θ, sin θ)", [-1.6, 1.6], [-1.3, 1.3],
               [param("th", "Sudut θ (derajat)", 0, 360, 1, deg, "θ")],
               [{"type": "param", "t": [0, "2*pi"], "x": "cos(t)", "y": "sin(t)", "color": "gray"},
                {"type": "segment", "x1": 0, "y1": 0, "x2": "cos(th*pi/180)", "y2": "sin(th*pi/180)", "color": "blue"},
                {"type": "segment", "x1": "cos(th*pi/180)", "y1": 0, "x2": "cos(th*pi/180)", "y2": "sin(th*pi/180)", "color": "red", "dash": True},
                pt("cos(th*pi/180)", "sin(th*pi/180)", label="(cos θ, sin θ)")],
               [readout("sin θ", "sin(th*pi/180)", 4), readout("cos θ", "cos(th*pi/180)", 4), readout("tan θ", "tan(th*pi/180)", 4)],
               caption)


@register("trig.konversi", T, (1,))
def konversi(rng, tier):
    deg = rng.choice([30, 45, 60, 90, 120, 135, 150, 180, 210, 225, 240, 270, 300, 315, 330, 360])
    to_rad = rng.random() < 0.5
    if to_rad:
        prompt, correct = f"Nyatakan {deg}° dalam radian.", rad_text(deg)
        wrong = [rad_text(deg * 2), rad_text(deg // 2 if deg % 2 == 0 else deg + 30), rad_text(360 - deg if deg != 180 else 90), f"{deg}π"]
        steps = ["180° = π radian, jadi 1° = π/180 rad.", f"{deg}° × π/180 = <b>{correct}</b>."]
    else:
        prompt, correct = f"Nyatakan {rad_text(deg)} radian dalam derajat.", f"{deg}°"
        wrong = [f"{deg * 2}°", f"{deg // 2}°", f"{360 - deg if deg != 180 else 90}°", f"{deg + 30}°"]
        steps = ["π rad = 180°.", f"Ganti π dengan 180°: {rad_text(deg)} = <b>{deg}°</b>."]
    return {"prompt": prompt, "correct": correct, "distractors": wrong, "steps": steps,
            "graphs": [unit_circle(deg, "Panjang busur dari sumbu-x positif sampai titik = θ dalam radian (karena jari-jari 1).")],
            "explanation": "Radian = panjang busur pada lingkaran berjari-jari 1. 2π rad = 360°."}


@register("trig.sudut_istimewa", T, (1, 2))
def sudut_istimewa(rng, tier):
    func = rng.choice(["sin", "cos", "tan"])
    deg = rng.choice([30, 45, 60]) if tier == 1 else rng.choice([120, 135, 150, 210, 225, 240, 300, 315, 330])
    val = exact(func, deg)
    show = f"{deg}°" if rng.random() < 0.5 else rad_text(deg)
    ref = {1: 180 - deg, 2: deg - 180, 3: 360 - deg}.get(deg // 90, deg)
    wrong = [v for v in ALL_VALUES if v != val]
    rng.shuffle(wrong)
    wrong = [neg(val)] + wrong
    steps = [f"Sudut acuan: {ref}° (kuadran {deg // 90 + 1}).",
             f"{func} {ref}° = {exact(func, ref)}.",
             "Tanda per kuadran (“Semua Sindikat Tangan Kosong”): I semua +, II sin +, III tan +, IV cos +.",
             f"Jadi {func} {show} = <b>{val}</b>."]
    if tier == 1:
        steps = [f"Gunakan segitiga istimewa 30°–60°–90° (sisi 1 : √3 : 2) atau 45°–45°–90° (sisi 1 : 1 : √2).",
                 f"{func} {show} = <b>{val}</b>."]
    return {"prompt": f"Tentukan nilai eksak {func} {show}.", "correct": val, "distractors": wrong, "steps": steps,
            "graphs": [unit_circle(deg, "Geser θ: sin θ = koordinat y, cos θ = koordinat x. Tanda ikut kuadran.")],
            "explanation": "sin θ = y, cos θ = x pada lingkaran satuan; tan θ = y/x."}


@register("trig.identitas", T, (2, 3))
def identitas(rng, tier):
    a, b, c = rng.choice([(3, 4, 5), (5, 12, 13), (8, 15, 17), (7, 24, 25)])
    if rng.random() < 0.5:
        a, b = b, a
    quad = rng.choice([2, 3, 4]) if tier == 3 else rng.choice([1, 2])
    sx = {1: 1, 2: -1, 3: -1, 4: 1}[quad]
    sy = {1: 1, 2: 1, 3: -1, 4: -1}[quad]
    sinv, cosv = Fr(sy * a, c), Fr(sx * b, c)
    ask = rng.choice(["cos θ", "tan θ"])
    val = cosv if ask == "cos θ" else sinv / cosv
    names = {1: "I", 2: "II", 3: "III", 4: "IV"}
    return {
        "prompt": f"Diketahui sin θ = {n(sinv)} dan θ di kuadran {names[quad]}. Tentukan {ask}.",
        "correct": n(val), "distractors": [n(-val), n(Fr(c, b * sx)), n(Fr(sy * b, sx * a)) if ask == "tan θ" else n(Fr(sy * a, sx * b)), n(Fr(b, c))],
        "steps": [f"sin²θ + cos²θ = 1 ⇒ cos²θ = 1 − {a * a}/{c * c} = {b * b}/{c * c} ⇒ |cos θ| = {b}/{c}.",
                  f"Di kuadran {names[quad]} cos θ {'positif' if sx > 0 else 'negatif'}: cos θ = {n(cosv)}."]
                 + ([f"tan θ = sin θ / cos θ = {n(sinv)} / {n(cosv)} = <b>{n(val)}</b>."] if ask == "tan θ" else [f"Jawaban: <b>{n(cosv)}</b>."]),
        "graphs": [unit_circle(round(math.degrees(math.atan2(float(sinv), float(cosv)))) % 360,
                               "Titik pada lingkaran satuan memenuhi x² + y² = 1, itulah identitas sin²θ + cos²θ = 1.")],
        "explanation": "Identitas Pythagoras sin²θ + cos²θ = 1; tanda ditentukan kuadran.",
    }


@register("trig.grafik", T, (2, 3))
def grafik(rng, tier):
    A = rng.choice([1, 2, 3, 4, -2, -3])
    B = rng.choice([1, 2, 3, 4, Fr(1, 2)])
    D = rng.randint(-3, 3)
    func = rng.choice(["sin", "cos"])
    period = Fr(2) / B
    bx = "x/2" if B == Fr(1, 2) else ("x" if B == 1 else f"{n(B)}x")
    per_txt = rad_text(int(period * 180)) if (period * 180).denominator == 1 else f"{n(period)}π"
    if tier == 2:
        ask = rng.choice(["amplitudo", "periode"])
        prompt = f"Tentukan {ask} fungsi y = {n(A) if A != 1 else ''}{func}({bx}){' + ' + str(D) if D > 0 else (' − ' + str(-D) if D < 0 else '')}."
        if ask == "amplitudo":
            correct = str(abs(A))
            wrong = [n(A) if A < 0 else n(A + 1), n(abs(A) * 2), n(abs(A) + abs(D)) if D else n(abs(A) + 2), per_txt]
            steps = ["Amplitudo = |A| (setengah jarak puncak ke lembah).", f"|{n(A)}| = <b>{abs(A)}</b>. Konstanta D hanya menggeser naik/turun."]
        else:
            correct = per_txt
            cands = [period * 2, period / 2, Fr(2), Fr(1), B, period * 4, Fr(4)]
            wrong = [rad_text(int(p * 180)) if (p * 180).denominator == 1 else f"{n(p)}π" for p in cands if p != period]
            steps = ["Periode sin(Bx) dan cos(Bx) adalah 2π/|B|.", f"2π/{n(B)} = <b>{correct}</b>."]
    else:
        tail = "" if D == 0 else f" {'+' if D > 0 else MINUS} {abs(D)}"
        prompt = f"Tentukan daerah hasil (range) y = {n(A)}{func}({bx}){tail}."
        lo, hi = D - abs(A), D + abs(A)
        correct = f"[{n(lo)}, {n(hi)}]"
        wrong = [f"[{n(-abs(A))}, {n(abs(A))}]", f"[{n(lo - 1)}, {n(hi + 1)}]", f"[{n(D - abs(A) * 2)}, {n(D + abs(A) * 2)}]", f"({n(lo)}, {n(hi)})"]
        steps = [f"{func}(…) bernilai dari −1 sampai 1.", f"Dikalikan {n(A)}: dari −{abs(A)} sampai {abs(A)} (urutan dibalik bila A negatif).",
                 f"Ditambah {n(D)}: <b>{correct}</b>."]
    return {"prompt": prompt, "correct": correct, "distractors": wrong, "steps": steps,
            "graphs": [g2d(f"y = A·{func}(Bx + C) + D", [-2 * math.pi, 2 * math.pi], [-8, 8],
                           [param("A", "Amplitudo A", -5, 5, 0.25, float(A), "A"), param("B", "Frekuensi B", 0.25, 5, 0.25, float(B), "B"),
                            param("C", "Geser fase C", -3.2, 3.2, 0.05, 0, "C"), param("D", "Geser vertikal D", -4, 4, 0.25, D, "D")],
                           [fn(f"A*{func}(B*x+C)+D", "blue", "y"), {"type": "hline", "y": "D", "color": "gray", "dash": True},
                            {"type": "hline", "y": "D+abs(A)", "color": "red", "dash": True}, {"type": "hline", "y": "D-abs(A)", "color": "red", "dash": True}],
                           [readout("Periode 2π/B", "2*pi/B", 4), readout("Maksimum", "D+abs(A)", 3), readout("Minimum", "D-abs(A)", 3)],
                           "Geser A, B, C, D satu per satu. FT: model getaran/arus AC; Fasilkom: sinyal digital.")],
            "explanation": "y = A sin(Bx + C) + D: amplitudo |A|, periode 2π/|B|, garis tengah y = D."}


@register("trig.persamaan", T, (3, 4))
def persamaan(rng, tier):
    if tier == 3:
        func = rng.choice(["sin", "cos"])
        targets = ["1/2", "√2/2", "√3/2", f"{MINUS}1/2", f"{MINUS}√2/2", f"{MINUS}√3/2"]
        val = rng.choice(targets)
        sols = [d for d in sorted(set(range(0, 360, 30)) | set(range(0, 360, 45))) if exact(func, d) == val]
        prompt = f"Tentukan himpunan penyelesaian {func} x = {val} untuk 0 ≤ x &lt; 2π."
        steps = [f"Sudut acuan dengan {func} = {val.replace(MINUS, '')}: {[d for d in (30, 45, 60) if exact(func, d) == val.replace(MINUS, '')][0]}°.",
                 f"{func} {'positif' if not val.startswith(MINUS) else 'negatif'} di kuadran "
                 + ({"sin": "I & II" if not val.startswith(MINUS) else "III & IV", "cos": "I & IV" if not val.startswith(MINUS) else "II & III"}[func]) + ".",
                 "Jawaban: <b>{" + ", ".join(rad_text(d) for d in sols) + "}</b>."]
        expr = f"{func}(x)"
        hval = round({"sin": math.sin, "cos": math.cos}[func](math.radians(sols[0])), 4)
    else:
        # 2cos²x − cos x − 1 = 0 → cos x = 1 atau −1/2  /  2sin²x + sin x − 1 = 0 → sin x = 1/2 atau −1
        func = rng.choice(["sin", "cos"])
        if func == "cos":
            prompt = "Tentukan himpunan penyelesaian 2cos²x − cos x − 1 = 0 untuk 0 ≤ x &lt; 2π."
            sols = [0, 120, 240]
            steps = ["Misal u = cos x: 2u² − u − 1 = 0 ⇒ (2u + 1)(u − 1) = 0 ⇒ u = −1/2 atau u = 1.",
                     "cos x = 1 ⇒ x = 0; cos x = −1/2 ⇒ x = 2π/3 atau 4π/3."]
            expr, hval = "2*cos(x)**2-cos(x)-1", 0
        else:
            prompt = "Tentukan himpunan penyelesaian 2sin²x + sin x − 1 = 0 untuk 0 ≤ x &lt; 2π."
            sols = [30, 150, 270]
            steps = ["Misal u = sin x: 2u² + u − 1 = 0 ⇒ (2u − 1)(u + 1) = 0 ⇒ u = 1/2 atau u = −1.",
                     "sin x = 1/2 ⇒ x = π/6 atau 5π/6; sin x = −1 ⇒ x = 3π/2."]
            expr, hval = "2*sin(x)**2+sin(x)-1", 0
        steps.append("Jawaban: <b>{" + ", ".join(rad_text(d) for d in sols) + "}</b>.")
    correct = "{" + ", ".join(rad_text(d) for d in sols) + "}"
    alt = [[(d + 180) % 360 for d in sols], [d for d in sols[:1]], [(360 - d) % 360 for d in sols], [(d + 30) % 360 for d in sols],
           [(180 - d) % 360 for d in sols]]
    wrong = ["{" + ", ".join(rad_text(d) for d in sorted(set(a))) + "}" for a in alt]
    return {"prompt": prompt, "correct": correct, "distractors": wrong, "steps": steps,
            "graphs": [g2d("Penyelesaian = titik potong kurva dengan garis", [0, 2 * math.pi], [-3, 3],
                           [param("hv", "Nilai ruas kanan", -1.5, 1.5, 0.01, hval, "k")],
                           [fn(expr, "blue", "y"), {"type": "hline", "y": "hv", "color": "red", "dash": True}],
                           None, "Geser garis merah: banyak titik potong di [0, 2π) = banyak penyelesaian.")],
            "explanation": "Persamaan trigonometri: cari sudut acuan, lalu semua kuadran dengan tanda yang sesuai dalam satu periode."}


@register("trig.maksimum", T, (4, 5))
def maksimum(rng, tier):
    a, b, r = rng.choice([(3, 4, 5), (5, 12, 13), (8, 15, 17), (6, 8, 10), (4, 3, 5), (12, 5, 13)])
    a *= rng.choice([1, -1])
    c = rng.randint(-5, 5) if tier == 5 else 0
    ask = rng.choice(["maksimum", "minimum"]) if tier == 5 else "maksimum"
    val = (r if ask == "maksimum" else -r) + c
    return {
        "prompt": f"Tentukan nilai {ask} f(x) = {n(a)} sin x + {b} cos x" + (f" {'+' if c > 0 else MINUS} {abs(c)}" if c else "") + ".",
        "correct": n(val), "distractors": [n(abs(a) + b + c), n(-val + 2 * c), n(r * r + c), n(val + 1)],
        "steps": ["a sin x + b cos x = R sin(x + φ) dengan R = √(a² + b²).", f"R = √({a * a} + {b * b}) = {r}.",
                  f"sin(…) bernilai antara −1 dan 1 ⇒ f berkisar dari {n(-r + c)} sampai {n(r + c)}.", f"Nilai {ask} = <b>{n(val)}</b>."],
        "graphs": [g2d("a sin x + b cos x adalah sinusoid beramplitudo √(a² + b²)", [-2 * math.pi, 2 * math.pi], [-20, 20],
                       [param("aa", "a", -12, 12, 1, a, "a"), param("bb", "b", -12, 12, 1, b, "b")],
                       [fn(f"aa*sin(x)+bb*cos(x)+{c}", "blue", "f(x)"), fn(f"{c}+sqrt(aa*aa+bb*bb)", "red", "maks", dash=True),
                        fn(f"{c}-sqrt(aa*aa+bb*bb)", "red", "min", dash=True)],
                       [readout("R = √(a² + b²)", "sqrt(aa*aa+bb*bb)", 4)],
                       "Ubah a dan b: puncak gelombang selalu √(a² + b²), bukan |a| + |b|.")],
        "explanation": "Bentuk R sin(x + φ): amplitudo R = √(a² + b²).",
    }


@register("trig.jumlah_kuadrat", T, (4, 5))
def jumlah_kuadrat(rng, tier):
    a = rng.randint(0, 10)
    func = rng.choice(["sin", "cos"])
    terms = 91 - 2 * a
    val = Fr(terms, 2)
    return {
        "prompt": f"Hitung {func}²{a}° + {func}²{a + 1}° + {func}²{a + 2}° + … + {func}²{90 - a}°.",
        "correct": n(val), "distractors": [n(val + Fr(1, 2)), n(val - Fr(1, 2)), n(terms), n(Fr(terms - 1, 2) + 1)],
        "steps": [f"Pasangkan sudut k° dengan (90 − k)°: {func}²k° + {func}²(90 − k)° = {func}²k° + {'cos' if func == 'sin' else 'sin'}²k° = 1.",
                  f"Banyak suku: {90 - a} − {a} + 1 = {terms} (ganjil), jadi ada {(terms - 1) // 2} pasangan dan satu suku tengah {func}²45° = 1/2.",
                  f"Jumlah = {(terms - 1) // 2} + 1/2 = <b>{n(val)}</b>."],
        "explanation": "sin(90° − x) = cos x, sehingga sin²x + sin²(90° − x) = 1.",
    }


@register("trig.sederhana", T, (2, 3))
def sederhana(rng, tier):
    items = [
        ("(1 − cos²x) / sin x", "sin x", ["cos x", "1", "tan x", "sec x"]),
        ("sin x · cot x", "cos x", ["sin x", "tan x", "1", "csc x"]),
        ("(1 + tan²x) · cos²x", "1", ["sin²x", "sec x", "tan²x", "cos x"]),
        ("sin⁴x − cos⁴x", "sin²x − cos²x", ["1", "sin²x + cos²x", "2sin²x", "cos 2x"]),
        ("(sin x + cos x)² − 2 sin x cos x", "1", ["sin 2x", "0", "2", "sin x + cos x"]),
        ("tan x · cos x / sin x", "1", ["tan x", "sec x", "cos x", "0"]),
    ]
    expr, correct, wrong = rng.choice(items[:3] if tier == 2 else items)
    return {"prompt": f"Sederhanakan {expr} (untuk x di mana ekspresi terdefinisi).", "correct": correct, "distractors": wrong,
            "steps": ["Identitas dasar: sin²x + cos²x = 1, tan x = sin x / cos x, 1 + tan²x = sec²x, cot x = cos x / sin x.",
                      "Ubah semua ke sin dan cos, lalu gunakan identitas Pythagoras.",
                      f"Hasil: <b>{correct}</b>."],
            "explanation": "Identitas trigonometri berlaku untuk semua x di domain — cek dengan memasukkan satu nilai x."}
