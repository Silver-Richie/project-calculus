"""
Pembuat spec GraphLab untuk pembahasan soal hasil generator.

Semua grafik memakai slider (`params`) dengan nilai awal = nilai di soal, sehingga
user bisa membandingkan bentuk grafik ketika variabel dimanipulasi (bayangan abu-abu
= kondisi soal). Format spec: gamification/content/README.md.
"""

from gamification.content.helpers import param, readout  # noqa: F401  (diekspor ulang)


def g2d(title, x, y, params, elements, readouts=None, caption=None):
    spec = {"type": "2d", "title": title, "x": list(x), "y": list(y),
            "params": params, "elements": elements}
    if readouts:
        spec["readouts"] = readouts
    if caption:
        spec["caption"] = caption
    return spec


def fn(expr, color="blue", label=None, dash=False, **kw):
    el = {"type": "fn", "expr": expr, "color": color}
    if label:
        el["label"] = label
    if dash:
        el["dash"] = True
    el.update(kw)
    return el


def pt(x, y, color="red", hollow=False, label=None):
    el = {"type": "point", "x": x, "y": y, "color": color, "hollow": hollow}
    if label:
        el["label"] = label
    return el


def vband(a, b, color="green"):
    return {"type": "vband", "from": a, "to": b, "color": color}


def hline(y, color="gray", dash=True):
    return {"type": "hline", "y": y, "color": color, "dash": dash}


def vline(x, color="gray", dash=True):
    return {"type": "vline", "x": x, "color": color, "dash": dash}


def seg(x1, y1, x2, y2, color="green", width=6, dash=False):
    el = {"type": "segment", "x1": x1, "y1": y1, "x2": x2, "y2": y2, "color": color, "width": width}
    if dash:
        el["dash"] = True
    return el


def text(x, y, s, color="navy"):
    return {"type": "text", "x": x, "y": y, "text": s, "color": color}


def span(*vals, pad=2, min_half=4):
    """Rentang sumbu yang memuat semua nilai + margin."""
    lo, hi = min(vals), max(vals)
    mid = (lo + hi) / 2
    half = max((hi - lo) / 2 + pad, min_half)
    return [round(mid - half, 2), round(mid + half, 2)]
