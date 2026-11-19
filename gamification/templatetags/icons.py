"""
Tag {% icon "diamond" %}: ikon SVG dari sprite templates/components/icons.html.

Mechanism: sprite <symbol id="i-…"> dimuat sekali di base.html; tag ini hanya menulis
<svg><use href="#i-…"/></svg>, sehingga desain ikon ada di satu tempat dan juga dipakai
JS lewat Icon() (static/js/icons.js) dengan keluaran yang sama.
Tanpa `size`, ikon mengikuti ukuran teks (kelas .ic, 1.15em).
"""

from django import template
from django.utils.html import format_html

register = template.Library()


@register.simple_tag
def icon(name, size=None, cls="", label=""):
    dims = format_html(' width="{0}" height="{0}"', size) if size else ""
    a11y = format_html('role="img" aria-label="{}"', label) if label else format_html('aria-hidden="true"')
    return format_html('<svg class="ic ic-{} {}"{} {} focusable="false"><use href="#i-{}"/></svg>',
                       name, cls, dims, a11y, name)
