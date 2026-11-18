"""
Calculus Bridge - Toko Diamond 💎.

Mechanism
---------
Mendapat diamond (semua lewat `award`):

* Naik level   : naik ke Level n memberi 10·n (Level 2 = 20, Level 3 = 30, …). Hadiah dihitung
                 dari level sebelum & sesudah XP bertambah (sessions.submit_session). XP tidak
                 pernah berkurang, jadi setiap level hanya memberi hadiah sekali. Level 1 = 0 💎.
* Topik tuntas : +5 saat Sesi III sebuah topik lulus untuk pertama kali.
* Menang duel  : +2 (tidak berlaku bila lawan keluar di tengah duel, agar tidak bisa dipancing).

Belanja (`buy`) berjalan dalam transaksi dengan baris profil dikunci (select_for_update),
sehingga dua klik bersamaan tidak bisa membuat saldo negatif atau membeli barang dua kali.

Jenis barang (KATALOG):

* Habis pakai : nyawa (+1 / isi penuh) dan Perisai Bintang. Perisai dipakai otomatis oleh
                duel.finish_match saat kalah duel yang akan mengurangi bintang.
* Kosmetik    : aksesori Archie (slot head/face/neck), bingkai avatar (frame), dan gelar (title).
                Dibeli sekali (OwnedItem), lalu dipasang/dilepas per slot (UserProfile.equipped).
                Gambar aksesori ada di frontend (static/js/shop.js), kuncinya harus sama.
"""

from django.db import transaction
from django.db.models import F

from .models import OwnedItem, UserProfile

LEVEL_REWARD = 10        # × level baru
TOPIC_REWARD = 5
DUEL_WIN_REWARD = 2
MAX_SHIELDS = 5

# kind: "hearts" | "shield" (habis pakai) · "cosmetic" (dengan slot)
CATALOG = [
    # Penguat
    {"key": "hearts-one", "kind": "hearts", "name": "+1 Nyawa", "icon": "❤️", "price": 6,
     "desc": "Tambah satu nyawa sekarang juga."},
    {"key": "hearts-full", "kind": "hearts", "name": "Isi Penuh Nyawa", "icon": "💖", "price": 30,
     "desc": "Semua nyawa langsung penuh, tanpa menunggu 24 jam."},
    {"key": "star-shield", "kind": "shield", "name": "Perisai Bintang", "icon": "🛡️", "price": 15,
     "desc": f"Terpakai otomatis saat kalah duel: bintang rank tidak berkurang. Simpan maksimal {MAX_SHIELDS}."},
    # Aksesori Archie
    {"key": "acc-bunga", "kind": "cosmetic", "slot": "head", "name": "Bunga Rambut", "icon": "🌸", "price": 25,
     "desc": "Hiasan bunga manis di kepala Archie."},
    {"key": "acc-headphone", "kind": "cosmetic", "slot": "head", "name": "Headphone", "icon": "🎧", "price": 50,
     "desc": "Belajar sambil dengar musik lo-fi."},
    {"key": "acc-penyihir", "kind": "cosmetic", "slot": "head", "name": "Topi Penyihir", "icon": "🧙", "price": 70,
     "desc": "Untuk penyihir integral sejati."},
    {"key": "acc-mahkota", "kind": "cosmetic", "slot": "head", "name": "Mahkota Emas", "icon": "👑", "price": 120,
     "desc": "Raja dan ratu kalkulus."},
    {"key": "acc-kacamata", "kind": "cosmetic", "slot": "face", "name": "Kacamata Hitam", "icon": "🕶️", "price": 40,
     "desc": "Terlalu keren untuk limit tak hingga."},
    {"key": "acc-dasi", "kind": "cosmetic", "slot": "neck", "name": "Dasi Kupu-kupu", "icon": "🎀", "price": 25,
     "desc": "Rapi untuk presentasi tugas besar."},
    {"key": "acc-syal", "kind": "cosmetic", "slot": "neck", "name": "Syal Hangat", "icon": "🧣", "price": 35,
     "desc": "Tetap hangat saat begadang belajar."},
    # Bingkai avatar
    {"key": "frame-perunggu", "kind": "cosmetic", "slot": "frame", "name": "Bingkai Perunggu", "icon": "🥉", "price": 25,
     "desc": "Bingkai avatar di profil dan papan peringkat."},
    {"key": "frame-perak", "kind": "cosmetic", "slot": "frame", "name": "Bingkai Perak", "icon": "🥈", "price": 50,
     "desc": "Bingkai avatar di profil dan papan peringkat."},
    {"key": "frame-emas", "kind": "cosmetic", "slot": "frame", "name": "Bingkai Emas", "icon": "🥇", "price": 100,
     "desc": "Bingkai avatar di profil dan papan peringkat."},
    {"key": "frame-pelangi", "kind": "cosmetic", "slot": "frame", "name": "Bingkai Pelangi", "icon": "🌈", "price": 150,
     "desc": "Bingkai berkilau yang berputar pelan."},
    # Gelar
    {"key": "title-limit", "kind": "cosmetic", "slot": "title", "name": "Pejuang Limit", "icon": "🎯", "price": 20,
     "desc": "Gelar di bawah namamu."},
    {"key": "title-turunan", "kind": "cosmetic", "slot": "title", "name": "Ahli Turunan", "icon": "📈", "price": 40,
     "desc": "Gelar di bawah namamu."},
    {"key": "title-integral", "kind": "cosmetic", "slot": "title", "name": "Penakluk Integral", "icon": "∫", "price": 60,
     "desc": "Gelar di bawah namamu."},
    {"key": "title-legenda", "kind": "cosmetic", "slot": "title", "name": "Legenda Kalkulus", "icon": "🏛️", "price": 150,
     "desc": "Gelar di bawah namamu."},
]
ITEMS = {it["key"]: it for it in CATALOG}
SLOTS = ("head", "face", "neck", "frame", "title")


class ShopError(Exception):
    """Pembelian/pemasangan ditolak; pesannya ditampilkan ke pengguna."""


# ── mendapat diamond ────────────────────────────────────────────────────────
def level_reward(level):
    """Diamond untuk naik ke `level`."""
    return LEVEL_REWARD * level


def level_rewards_between(before, after):
    """Total hadiah naik level dari `before` ke `after` (bisa melompati beberapa level sekaligus)."""
    return sum(level_reward(n) for n in range(before + 1, after + 1))


def award(user_id, amount):
    """Tambah diamond secara atomik di database (aman dipanggil di dalam transaksi lain)."""
    if amount > 0:
        UserProfile.objects.filter(user_id=user_id).update(gems=F("gems") + amount)
    return amount


# ── tampilan ────────────────────────────────────────────────────────────────
def appearance(profile):
    """Kosmetik terpasang untuk ditampilkan (profil, papan peringkat): slot → kunci, plus teks gelar."""
    eq = {slot: key for slot, key in (profile.equipped or {}).items() if key in ITEMS}
    return {**eq, "title_text": ITEMS[eq["title"]]["name"] if "title" in eq else ""}


def state(profile):
    """Isi toko untuk satu pengguna: saldo, stok perisai, nyawa, dan katalog bertanda dimiliki/terpasang."""
    owned = set(OwnedItem.objects.filter(user_id=profile.user_id).values_list("item", flat=True))
    equipped = appearance(profile)
    return {
        "gems": profile.gems,
        "star_shields": profile.star_shields,
        "max_shields": MAX_SHIELDS,
        "hearts": profile.hearts_state(),
        "equipped": equipped,
        "rewards": {"level": LEVEL_REWARD, "topic": TOPIC_REWARD, "duel_win": DUEL_WIN_REWARD},
        "items": [
            {**it, "owned": it["key"] in owned,
             "equipped": it.get("slot") is not None and equipped.get(it["slot"]) == it["key"]}
            for it in CATALOG
        ],
    }


# ── belanja & memasang ──────────────────────────────────────────────────────
def _locked_profile(user):
    UserProfile.objects.get_or_create(user=user)
    return UserProfile.objects.select_for_update().get(user=user)


def buy(user, key):
    """
    Beli satu barang. Mengembalikan state() terbaru; ShopError bila ditolak.

    Kosmetik yang baru dibeli langsung terpasang di slotnya.
    """
    item = ITEMS.get(key)
    if not item:
        raise ShopError("Barang tidak dikenal.")
    with transaction.atomic():
        profile = _locked_profile(user)
        if profile.gems < item["price"]:
            raise ShopError(f"Diamond kurang: butuh 💎 {item['price']}, kamu punya 💎 {profile.gems}.")
        fields = ["gems"]
        if item["kind"] == "hearts":
            profile.refresh_hearts()
            if profile.hearts >= profile.max_hearts:
                raise ShopError("Nyawamu sudah penuh.")
            profile.hearts = profile.max_hearts if key == "hearts-full" else profile.hearts + 1
            if profile.hearts >= profile.max_hearts:
                profile.hearts_lost_at = None          # penuh → hitungan 24 jam berhenti
            fields += ["hearts", "hearts_lost_at"]
        elif item["kind"] == "shield":
            if profile.star_shields >= MAX_SHIELDS:
                raise ShopError(f"Perisai Bintang sudah maksimal ({MAX_SHIELDS}).")
            profile.star_shields += 1
            fields.append("star_shields")
        else:
            _, created = OwnedItem.objects.get_or_create(user=user, item=key)
            if not created:
                raise ShopError("Barang ini sudah kamu miliki.")
            profile.equipped = {**(profile.equipped or {}), item["slot"]: key}
            fields.append("equipped")
        profile.gems -= item["price"]
        profile.save(update_fields=fields)
    return state(profile)


def equip(user, key, on=True):
    """Pasang (on=True) atau lepas kosmetik milik pengguna. Mengembalikan state() terbaru."""
    item = ITEMS.get(key)
    if not item or item["kind"] != "cosmetic":
        raise ShopError("Barang ini tidak bisa dipasang.")
    if not OwnedItem.objects.filter(user=user, item=key).exists():
        raise ShopError("Beli barang ini dulu.")
    with transaction.atomic():
        profile = _locked_profile(user)
        eq = dict(profile.equipped or {})
        if on:
            eq[item["slot"]] = key
        elif eq.get(item["slot"]) == key:
            del eq[item["slot"]]
        profile.equipped = eq
        profile.save(update_fields=["equipped"])
    return state(profile)
