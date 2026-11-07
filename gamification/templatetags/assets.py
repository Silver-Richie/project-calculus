"""
Tag {% asset 'js/app.js' %}: URL static + ?v=<waktu ubah berkas>.

Mechanism: browser menyimpan cache JS/CSS. Tanpa versi di URL, setelah berkas
diperbarui browser bisa tetap memakai versi lama (fitur baru tidak muncul).
Menambahkan waktu modifikasi berkas sebagai query string membuat URL berubah
setiap kali berkas berubah, sehingga browser otomatis mengunduh versi terbaru.
"""

import os

from django import template
from django.contrib.staticfiles import finders
from django.templatetags.static import static

register = template.Library()


@register.simple_tag
def asset(path):
    url = static(path)
    found = finders.find(path)
    if found:
        url += f"?v={int(os.path.getmtime(found))}"
    return url
