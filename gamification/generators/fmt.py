"""
Format angka & ekspresi matematika untuk teks soal (HTML ringan, notasi Indonesia).

Semua fungsi menerima int, float, atau Fraction dan memakai tanda minus
tipografis (−) serta koma desimal.
"""

from fractions import Fraction as Fr
import math

MINUS = "−"
_SUP = str.maketrans("0123456789-", "⁰¹²³⁴⁵⁶⁷⁸⁹⁻")


_SUB = str.maketrans("0123456789-", "₀₁₂₃₄₅₆₇₈₉₋")


def sub_(k):
    """Indeks bawah (mis. basis log): sub_(2) → '₂'. Selain angka ditulis dengan <sub>."""
    s = str(k)
    return s.translate(_SUB) if s.lstrip("-").isdigit() else f"<sub>{s}</sub>"


def sup(k):
    """Pangkat dalam karakter superskrip: sup(2) → '²'."""
    return str(k).translate(_SUP)


def n(v, digits=4):
    """Angka → teks. Pecahan ditulis a/b, desimal memakai koma."""
    if isinstance(v, Fr):
        if v.denominator == 1:
            v = v.numerator
        else:
            sign = MINUS if v < 0 else ""
            return f"{sign}{abs(v.numerator)}/{v.denominator}"
    if isinstance(v, float):
        if abs(v - round(v)) < 1e-9:
            v = int(round(v))
        else:
            s = f"{v:.{digits}g}"
            return s.replace("-", MINUS).replace(".", ",")
    return str(v).replace("-", MINUS)


def js(v):
    """Angka → literal JavaScript untuk spec grafik."""
    if isinstance(v, Fr):
        return float(v)
    return v


def frac_html(v):
    """Pecahan bertumpuk untuk tampilan pembahasan."""
    v = Fr(v)
    if v.denominator == 1:
        return n(v)
    sign = MINUS if v < 0 else ""
    return f'{sign}<span class="frac"><sup>{abs(v.numerator)}</sup>&frasl;<sub>{v.denominator}</sub></span>'


def term(c, var="x", power=1, first=False):
    """Satu suku polinom dengan tanda: term(-3,'x',2) → ' − 3x²'."""
    if c == 0:
        return ""
    c = Fr(c)
    mag = abs(c)
    if power == 0:
        body = n(mag)
    else:
        coef = "" if mag == 1 else n(mag)
        body = f"{coef}{var}{sup(power) if power != 1 else ''}"
    if first:
        return (MINUS if c < 0 else "") + body
    return f" {MINUS} {body}" if c < 0 else f" + {body}"


def poly(coeffs, var="x"):
    """Polinom dari koefisien (derajat tertinggi dulu): [2,-3,1] → '2x² − 3x + 1'."""
    deg = len(coeffs) - 1
    out = ""
    for i, c in enumerate(coeffs):
        out += term(c, var, deg - i, first=(out == ""))
    return out or "0"


def lin(a, b, var="x"):
    return poly([a, b], var)


def fac(a, var="x"):
    """Faktor linear (x − a) yang rapi: fac(0) → 'x', fac(-3) → '(x + 3)'."""
    if a == 0:
        return var
    return f"({var} {MINUS} {n(a)})" if a > 0 else f"({var} + {n(-a)})"


def poly_in(coeffs, token):
    """Polinom dalam ‘token’ sebagai variabel, mis. poly_in([1,-3,2], '2ˣ') → '(2ˣ)² − 3·2ˣ + 2'."""
    s = poly(coeffs, "u")
    s = s.replace("u²", f"({token})²")
    import re
    return re.sub(r"(\d)u", lambda m: f"{m.group(1)}·{token}", s).replace("u", token)


def terms(pairs, const=0):
    """
    Jumlah suku rapi dari [(koef, monomial), …]: suku berkoefisien 0 dibuang,
    koefisien ±1 tidak ditulis. terms([(3, 'x²'), (-1, 'xy'), (0, 'y')], 2) → '3x² − xy + 2'.
    """
    out = ""
    for c, mono in list(pairs) + [(const, "")]:
        if c == 0:
            continue
        c = Fr(c)
        mag = abs(c)
        body = (n(mag) if mag != 1 or not mono else "") + mono
        if out == "":
            out = (MINUS if c < 0 else "") + body
        else:
            out += f" {MINUS} {body}" if c < 0 else f" + {body}"
    return out or "0"


def signed(c):
    """' + 3' atau ' − 3' (untuk menyambung ekspresi)."""
    return term(c, "", 0)


def paren(v):
    """Bilangan negatif diberi kurung: (−3)."""
    return f"({n(v)})" if v < 0 else n(v)


def interval(lo, hi, lo_closed=True, hi_closed=True):
    """Notasi interval; lo/hi = None berarti tak hingga."""
    left = "(−∞" if lo is None else ("[" if lo_closed else "(") + n(lo)
    right = "∞)" if hi is None else n(hi) + ("]" if hi_closed else ")")
    return f"{left}, {right}"


def jsx(expr):
    """Ekspresi Python sederhana → ekspresi GraphLab (sudah kompatibel, hanya untuk kejelasan)."""
    return expr


def sqrt_simplify(k):
    """√k disederhanakan: 12 → (2, 3) berarti 2√3."""
    out, rest = 1, k
    f = 2
    while f * f <= rest:
        while rest % (f * f) == 0:
            out *= f
            rest //= f * f
        f += 1
    return out, rest


def surd(coef, rad):
    """Teks c√r (c dan r bilangan bulat)."""
    if rad == 1:
        return n(coef)
    if coef == 1:
        return f"√{rad}"
    if coef == -1:
        return f"{MINUS}√{rad}"
    return f"{n(coef)}√{rad}"


def gcd(a, b):
    return math.gcd(int(a), int(b))
