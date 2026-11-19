"""
Tag {% icon "diamond" %}: ikon SVG dari sprite templates/components/icons.html.

Mechanism: sprite <symbol id="i-…"> dimuat sekali di base.html; tag ini hanya menulis
<svg><use href="#i-…"/></svg>, sehingga desain ikon ada di satu tempat dan juga dipakai
JS lewat Icon() (static/js/icons.js) dengan keluaran yang sama.
Tanpa `size`, ikon mengikuti ukuran teks (kelas .ic, 1.15em).
{% icon_of nilai %}: untuk nilai dari data (mis. Faculty.icon) — nama ikon sprite → <svg>,
selain itu (simbol matematika) → lencana glyph .ic-glyph; sama dengan Icon.of() di JS.
"""

import re
from functools import lru_cache
from pathlib import Path

from django import template
from django.conf import settings
from django.utils.html import format_html

register = template.Library()


@lru_cache(maxsize=1)
def _sprite_names():
    sprite = Path(settings.BASE_DIR) / "templates" / "components" / "icons.html"
    return frozenset(re.findall(r'<symbol id="i-([\w-]+)"', sprite.read_text()))


@register.simple_tag
def icon(name, size=None, cls="", label=""):
    dims = format_html(' width="{0}" height="{0}"', size) if size else ""
    a11y = format_html('role="img" aria-label="{}"', label) if label else format_html('aria-hidden="true"')
    return format_html('<svg class="ic ic-{} {}"{} {} focusable="false"><use href="#i-{}"/></svg>',
                       name, cls, dims, a11y, name)


@register.simple_tag
def icon_of(value, size=None, cls=""):
    if not value:
        return ""
    if value in _sprite_names():
        return icon(value, size=size, cls=cls)
    return format_html('<span class="ic-glyph {}" aria-hidden="true">{}</span>', cls, value)
