"""
Helper kecil untuk menulis konten (HTML & spec grafik) dengan ringkas.
"""

import re


def at(expr, value):
    """Substitusi variabel x dengan `value` (hanya token x yang berdiri sendiri, bukan 'exp')."""
    return re.sub(r"\bx\b", f"({value})", expr)


def param(pid, label, vmin, vmax, step, value, symbol=None):
    """Slider parameter GraphLab. `value` = nilai yang dipakai di soal."""
    p = {"id": pid, "label": label, "min": vmin, "max": vmax, "step": step, "value": value}
    if symbol:
        p["symbol"] = symbol
    return p


def readout(label, expr, digits=4):
    """Baris tabel nilai (dihitung ulang setiap slider digeser)."""
    return {"label": label, "expr": expr, "digits": digits}


def table(headers, rows):
    """Membuat tabel HTML sederhana bergaya .lesson-table."""
    head = "".join(f"<th>{h}</th>" for h in headers)
    body = "".join("<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>" for r in rows)
    return f'<div class="table-scroll"><table class="lesson-table"><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div>'


def bullets(items):
    return "<ul class=\"lesson-list\">" + "".join(f"<li>{i}</li>" for i in items) + "</ul>"


def tangent_graph(title, expr, dexpr, a_label, a_min, a_max, a_value, x, y,
                  extra_params=None, extra_readouts=None, caption=None, fn_label="f(x)"):
    """Grafik fungsi + garis singgung di x = a (slider a)."""
    params = [param("a", a_label, a_min, a_max, 0.01, a_value, "a")] + (extra_params or [])
    fa = at(expr, 'a')
    dfa = at(dexpr, 'a')
    spec = {
        "type": "2d",
        "title": title,
        "x": x,
        "y": y,
        "params": params,
        "elements": [
            {"type": "fn", "expr": expr, "color": "blue", "label": fn_label},
            {"type": "fn", "expr": f"({fa}) + ({dfa})*(x-(a))", "color": "red", "dash": True,
             "label": "garis singgung di x = a"},
            {"type": "point", "x": "a", "y": fa, "color": "red"},
        ],
        "readouts": [readout("a", "a", 3), readout("f(a)", fa), readout("f′(a) = kemiringan", dfa)]
        + (extra_readouts or []),
    }
    if caption:
        spec["caption"] = caption
    return spec


def antiderivative_family(title, integrand, antiderivative, x, y, x0=1.0, caption=None):
    """Integrand f(x) dan keluarga antiturunan F(x) + C (slider C)."""
    spec = {
        "type": "2d",
        "title": title,
        "x": x,
        "y": y,
        "params": [
            param("C", "Konstanta integrasi C", -5, 5, 0.1, 0, "C"),
            param("x0", "Titik uji x₀", x[0], x[1], 0.01, x0, "x₀"),
        ],
        "elements": [
            {"type": "fn", "expr": integrand, "color": "orange", "label": "integran f(x)"},
            {"type": "fn", "expr": f"({antiderivative}) + C", "color": "blue", "label": "F(x) + C"},
            {"type": "fn", "expr": f"({at(antiderivative, 'x0')}) + C + ({at(integrand, 'x0')})*(x-x0)",
             "color": "red", "dash": True, "label": "singgung F di x₀"},
            {"type": "point", "x": "x0", "y": f"({at(antiderivative, 'x0')}) + C", "color": "red"},
        ],
        "readouts": [
            readout("Kemiringan F di x₀", at(integrand, 'x0')),
            readout("f(x₀)", at(integrand, 'x0')),
        ],
        "caption": caption or "Geser C: kurva F(x) + C hanya bergeser naik/turun, tetapi kemiringannya di setiap x "
                              "tetap sama dengan f(x). Itulah sebabnya integral tak tentu selalu ditulis + C.",
    }
    return spec


def limit_graph(title, expr, c, L, x, y, c_param=None, extra_params=None, extra_readouts=None, caption=None):
    """Grafik limit: titik berlubang di (c, L) dan titik bergerak x = c + d."""
    params = (extra_params or []) + [param("d", "Jarak x ke titik limit (d)", -1, 1, 0.005, 0.5, "d")]
    if c_param:
        params = [c_param] + params
    spec = {
        "type": "2d",
        "title": title,
        "x": x,
        "y": y,
        "params": params,
        "elements": [
            {"type": "fn", "expr": expr, "color": "blue", "label": "f(x)"},
            {"type": "hline", "y": L, "color": "gray", "dash": True},
            {"type": "point", "x": c, "y": L, "hollow": True, "color": "blue"},
            {"type": "point", "x": f"({c}) + d", "y": at(expr, f"({c}) + d"), "color": "red",
             "label": "x = {{" + c + " + d}}"},
        ],
        "readouts": [
            readout("x = c + d", f"({c}) + d"),
            readout("f(x)", at(expr, f"({c}) + d"), 5),
            readout("Nilai limit", L),
        ] + (extra_readouts or []),
        "caption": caption or "Geser d mendekati 0 dari kiri maupun kanan: nilai f(x) mendekati nilai limit, "
                              "walaupun f tidak terdefinisi tepat di titik itu (lingkaran kosong).",
    }
    return spec


def area_graph(title, expr, a, b_param, closed_form, x, y, caption=None, extra_params=None, extra_readouts=None):
    """Luas di bawah kurva dari a sampai b (slider b)."""
    return {
        "type": "2d",
        "title": title,
        "x": x,
        "y": y,
        "params": [b_param] + (extra_params or []),
        "elements": [
            {"type": "fill", "upper": expr, "from": a, "to": "b", "color": "amber"},
            {"type": "fn", "expr": expr, "color": "blue", "label": "f(x)"},
            {"type": "vline", "x": "b", "color": "red", "dash": True},
        ],
        "readouts": [readout("Batas atas b", "b", 4), readout("∫ f(x) dx (luas bertanda)", closed_form, 5)]
        + (extra_readouts or []),
        "caption": caption or "Geser batas atas b dan lihat bagaimana luas bertanda (integral tentu) berubah.",
    }
