"""
Calculus Bridge - Foto profil.

Mechanism
---------
Tiga jenis (UserProfile.avatar_kind):

* initial : polos — huruf pertama nama di lingkaran berwarna (warna dari hash username,
            sama dengan frontend).
* preset  : template bawaan PRESETS — lingkaran bergradien + ikon dari sprite ikon
            (templates/components/icons.html). Hanya kunci yang dikenal yang diterima.
* upload  : foto dari galeri HP / komputer. Browser memotong persegi & mengecilkan ke 256×256
            (static/js/avatar.js), jadi server tidak perlu Pillow: cukup batasi ukuran (MAX_BYTES)
            dan cek tanda tangan berkas (JPEG/PNG/WebP) — bukan percaya ekstensi/Content-Type.
            Foto lama dihapus saat diganti.

describe(profile) → {"kind", ...} untuk API & template (preset: key/bg/icon, upload: url); dirender oleh Avatar.html()
(JS) dan tag {% avatar %} (templatetags/icons.py) dengan aturan yang sama.
"""

import uuid

from django.core.files.base import ContentFile

MAX_BYTES = 300 * 1024

# kunci → (warna gradien atas, bawah, nama ikon sprite)
PRESETS = {
    "integral": ("#60A5FA", "#1D4ED8", "lv-kalkulus-menengah"),
    "tangent": ("#93C5FD", "#2563EB", "lv-kalkulus-dasar"),
    "venn": ("#FDBA74", "#EA580C", "lv-precalculus"),
    "surface": ("#6EE7B7", "#059669", "lv-kalkulus-lanjut"),
    "sine": ("#A5B4FC", "#4F46E5", "m-sine"),
    "infinity": ("#C4B5FD", "#7C3AED", "infinity"),
    "parabola": ("#F9A8D4", "#DB2777", "m-parabola"),
    "polar": ("#67E8F9", "#0891B2", "m-polar"),
    "flame": ("#FDE68A", "#F97316", "flame"),
    "diamond": ("#A5F3FC", "#0EA5E9", "diamond"),
    "crown": ("#FDE68A", "#D97706", "crown"),
    "compass": ("#BBF7D0", "#16A34A", "compass"),
}

SIGNATURES = (b"\xff\xd8\xff", b"\x89PNG\r\n\x1a\n")   # JPEG, PNG; WebP dicek terpisah (RIFF....WEBP)
EXT = {b"\xff\xd8\xff": "jpg", b"\x89PNG\r\n\x1a\n": "png"}


class AvatarError(Exception):
    """Pilihan foto ditolak; pesannya ditampilkan ke pengguna."""


def preset_info(key):
    top, bottom, icon = PRESETS[key]
    return {"key": key, "bg": [top, bottom], "icon": icon}


def describe(profile):
    """Foto profil untuk API/template; data yang tidak lengkap jatuh kembali ke polos (inisial)."""
    if profile.avatar_kind == "upload" and profile.avatar_file:
        return {"kind": "upload", "url": profile.avatar_file.url}
    if profile.avatar_kind == "preset" and profile.avatar_preset in PRESETS:
        return {"kind": "preset", **preset_info(profile.avatar_preset)}
    return {"kind": "initial"}


def all_presets():
    return [preset_info(k) for k in PRESETS]


def _image_ext(data):
    for sig in SIGNATURES:
        if data.startswith(sig):
            return EXT[sig]
    if data[:4] == b"RIFF" and data[8:12] == b"WEBP":
        return "webp"
    return None


def _drop_old_file(profile):
    if profile.avatar_file:
        profile.avatar_file.delete(save=False)


def set_initial(profile):
    _drop_old_file(profile)
    profile.avatar_kind, profile.avatar_preset = "initial", ""
    profile.save(update_fields=["avatar_kind", "avatar_preset", "avatar_file"])


def set_preset(profile, key):
    if key not in PRESETS:
        raise AvatarError("Template foto itu gak ada.")
    _drop_old_file(profile)
    profile.avatar_kind, profile.avatar_preset = "preset", key
    profile.save(update_fields=["avatar_kind", "avatar_preset", "avatar_file"])


def set_upload(profile, uploaded):
    if not uploaded:
        raise AvatarError("Pilih fotonya dulu, ya.")
    if uploaded.size > MAX_BYTES:
        raise AvatarError("Fotonya kegedean. Maksimal 300 KB setelah dipotong.")
    data = uploaded.read()
    ext = _image_ext(data)
    if not ext:
        raise AvatarError("Berkasnya bukan gambar JPG, PNG, atau WebP.")
    _drop_old_file(profile)
    profile.avatar_file.save(f"{profile.user_id}-{uuid.uuid4().hex[:10]}.{ext}", ContentFile(data), save=False)
    profile.avatar_kind, profile.avatar_preset = "upload", ""
    profile.save(update_fields=["avatar_kind", "avatar_preset", "avatar_file"])
