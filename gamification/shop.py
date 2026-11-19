"""
Calculus Bridge - Item Shop (diamond).

Mechanism
---------
Mendapat diamond (semua lewat `award`):

* Naik level   : naik ke Level n memberi 10·n (Level 2 = 20, Level 3 = 30, …). Hadiah dihitung
                 dari level sebelum & sesudah XP bertambah (sessions.submit_session). XP tidak
                 pernah berkurang, jadi setiap level hanya memberi hadiah sekali. Level 1 = 0 diamond.
* Topik tuntas : +5 saat Sesi III sebuah topik lulus untuk pertama kali.
* Menang duel  : +2 (tidak berlaku bila lawan keluar di tengah duel, agar tidak bisa dipancing).

Belanja (`buy`) berjalan dalam transaksi dengan baris profil dikunci (select_for_update),
sehingga dua klik bersamaan tidak bisa membuat saldo negatif atau membeli barang dua kali.

Jenis barang (KATALOG):

* Habis pakai : nyawa (+1 / +3 / isi penuh) dan Perisai Bintang (satuan / paket 3, total
                tidak boleh melebihi MAX_SHIELDS). Perisai dipakai otomatis oleh
                duel.finish_match saat kalah duel yang akan mengurangi bintang.
* Kosmetik    : aksesori Archie (slot head/face/neck), bingkai avatar (frame), dan gelar (title).
                "icon" = nama ikon sprite (components/icons.html); aksesori ("archie") tampil sebagai Archie mini.
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

# kind: "hearts" | "shield" (habis pakai, `amount` = jumlah yang ditambah; nyawa tanpa amount = isi penuh)
#       · "cosmetic" (dengan slot)
CATALOG = [
    # Penguat
    {"key": "hearts-one", "kind": "hearts", "amount": 1, "name": "+1 Heart", "icon": "heart", "price": 6,
     "desc": "Nambah 1 heart, langsung kepake."},
    {"key": "hearts-three", "kind": "hearts", "amount": 3, "name": "+3 Heart", "icon": "heart", "price": 15,
     "desc": "3 heart sekaligus, lebih hemat daripada beli satu-satu."},
    {"key": "hearts-full", "kind": "hearts", "name": "Refill Penuh", "icon": "heart", "price": 30,
     "desc": "Langsung isi penuh heart biar gak perlu nunggu 24 jam."},
    {"key": "star-shield", "kind": "shield", "amount": 1, "name": "Streak Shield", "icon": "shield", "price": 15,
     "desc": f"Otomatis aktif kalau kamu kalah duel, jadi bintang rank kamu aman. Maksimal simpan {MAX_SHIELDS}."},
    {"key": "star-shield-3", "kind": "shield", "amount": 3, "name": "3× Streak Shield", "icon": "shield", "price": 40,
     "desc": "Tiga Streak Shield sekaligus, buat stok musim duel yang panjang."},
    # Aksesori Archie
    {"key": "acc-bunga", "kind": "cosmetic", "slot": "head", "name": "Bunga Rambut", "icon": "archie", "price": 25,
     "desc": "Hiasan bunga manis di kepala Archie."},
    {"key": "acc-headphone", "kind": "cosmetic", "slot": "head", "name": "Headphone", "icon": "archie", "price": 50,
     "desc": "Belajar sambil dengar musik lo-fi."},
    {"key": "acc-penyihir", "kind": "cosmetic", "slot": "head", "name": "Topi Penyihir", "icon": "archie", "price": 70,
     "desc": "Untuk penyihir integral sejati."},
    {"key": "acc-mahkota", "kind": "cosmetic", "slot": "head", "name": "Mahkota Emas", "icon": "archie", "price": 120,
     "desc": "Raja dan ratu kalkulus."},
    {"key": "acc-pesta", "kind": "cosmetic", "slot": "head", "name": "Topi Pesta", "icon": "archie", "price": 30,
     "desc": "Buat ngerayain tiap materi yang beres."},
    {"key": "acc-kucing", "kind": "cosmetic", "slot": "head", "name": "Telinga Kucing", "icon": "archie", "price": 45,
     "desc": "Lincah seperti kucing mengejar titik ekstrem."},
    {"key": "acc-kupluk", "kind": "cosmetic", "slot": "head", "name": "Topi Kupluk", "icon": "archie", "price": 35,
     "desc": "Rajutan hangat untuk belajar pagi-pagi."},
    {"key": "acc-koboi", "kind": "cosmetic", "slot": "head", "name": "Topi Koboi", "icon": "archie", "price": 60,
     "desc": "Menjinakkan soal liar di padang integral."},
    {"key": "acc-halo", "kind": "cosmetic", "slot": "head", "name": "Lingkaran Halo", "icon": "archie", "price": 90,
     "desc": "Untuk yang jawabannya selalu benar."},
    {"key": "acc-kacamata", "kind": "cosmetic", "slot": "face", "name": "Kacamata Hitam", "icon": "archie", "price": 40,
     "desc": "Terlalu keren untuk limit tak hingga."},
    {"key": "acc-kumis", "kind": "cosmetic", "slot": "face", "name": "Kumis Profesor", "icon": "archie", "price": 30,
     "desc": "Wibawa dosen kalkulus senior."},
    {"key": "acc-monokel", "kind": "cosmetic", "slot": "face", "name": "Monokel", "icon": "archie", "price": 45,
     "desc": "Biar teliti ngecek tiap langkah pembuktian."},
    {"key": "acc-3d", "kind": "cosmetic", "slot": "face", "name": "Kacamata 3D", "icon": "archie", "price": 50,
     "desc": "Lihat grafik fungsi jadi tiga dimensi."},
    {"key": "acc-hati", "kind": "cosmetic", "slot": "face", "name": "Kacamata Hati", "icon": "archie", "price": 55,
     "desc": "Jatuh cinta pada matematika."},
    {"key": "acc-bintang", "kind": "cosmetic", "slot": "face", "name": "Kacamata Bintang", "icon": "archie", "price": 65,
     "desc": "Bintang panggung kelas kalkulus."},
    {"key": "acc-dasi", "kind": "cosmetic", "slot": "neck", "name": "Dasi Kupu-kupu", "icon": "archie", "price": 25,
     "desc": "Rapi untuk presentasi tugas besar."},
    {"key": "acc-syal", "kind": "cosmetic", "slot": "neck", "name": "Syal Hangat", "icon": "archie", "price": 35,
     "desc": "Tetap hangat saat begadang belajar."},
    {"key": "acc-dasi-panjang", "kind": "cosmetic", "slot": "neck", "name": "Dasi Kantor", "icon": "archie", "price": 35,
     "desc": "Siap sidang tugas akhir."},
    {"key": "acc-kalung-pi", "kind": "cosmetic", "slot": "neck", "name": "Kalung π", "icon": "archie", "price": 50,
     "desc": "3,14159… selalu dekat di hati."},
    {"key": "acc-mutiara", "kind": "cosmetic", "slot": "neck", "name": "Kalung Mutiara", "icon": "archie", "price": 70,
     "desc": "Berkilau seperti jawaban yang rapi."},
    {"key": "acc-medali", "kind": "cosmetic", "slot": "neck", "name": "Medali Juara", "icon": "archie", "price": 100,
     "desc": "Juara olimpiade kalkulus kampus."},
    # Bingkai avatar
    {"key": "frame-perunggu", "kind": "cosmetic", "slot": "frame", "name": "Bingkai Perunggu", "icon": "sparkle", "price": 25,
     "desc": "Bingkai avatar buat profil & leaderboard."},
    {"key": "frame-perak", "kind": "cosmetic", "slot": "frame", "name": "Bingkai Perak", "icon": "sparkle", "price": 50,
     "desc": "Bingkai avatar buat profil & leaderboard."},
    {"key": "frame-emas", "kind": "cosmetic", "slot": "frame", "name": "Bingkai Emas", "icon": "sparkle", "price": 100,
     "desc": "Bingkai avatar buat profil & leaderboard."},
    {"key": "frame-es", "kind": "cosmetic", "slot": "frame", "name": "Bingkai Es", "icon": "sparkle", "price": 70,
     "desc": "Tetap tenang dan dingin saat ujian."},
    {"key": "frame-neon", "kind": "cosmetic", "slot": "frame", "name": "Bingkai Neon", "icon": "sparkle", "price": 80,
     "desc": "Paling mencolok di leaderboard."},
    {"key": "frame-api", "kind": "cosmetic", "slot": "frame", "name": "Bingkai Api", "icon": "sparkle", "price": 120,
     "desc": "Semangat belajar yang membara."},
    {"key": "frame-pelangi", "kind": "cosmetic", "slot": "frame", "name": "Bingkai Pelangi", "icon": "sparkle", "price": 150,
     "desc": "Bingkai berkilau yang berputar pelan."},
    {"key": "frame-galaksi", "kind": "cosmetic", "slot": "frame", "name": "Bingkai Galaksi", "icon": "sparkle", "price": 200,
     "desc": "Bingkai kosmik yang berputar pelan."},
    # Gelar
    {"key": "title-limit", "kind": "cosmetic", "slot": "title", "name": "Pejuang Limit", "icon": "m-limit", "price": 20,
     "desc": "Gelar keren di bawah namamu."},
    {"key": "title-turunan", "kind": "cosmetic", "slot": "title", "name": "Ahli Turunan", "icon": "m-tangent", "price": 40,
     "desc": "Gelar keren di bawah namamu."},
    {"key": "title-integral", "kind": "cosmetic", "slot": "title", "name": "Penakluk Integral", "icon": "∫", "price": 60,
     "desc": "Gelar keren di bawah namamu."},
    {"key": "title-rajin", "kind": "cosmetic", "slot": "title", "name": "Si Paling Rajin", "icon": "book", "price": 20,
     "desc": "Gelar keren di bawah namamu."},
    {"key": "title-prakalkulus", "kind": "cosmetic", "slot": "title", "name": "Master Prakalkulus", "icon": "lv-precalculus", "price": 30,
     "desc": "Gelar keren di bawah namamu."},
    {"key": "title-rantai", "kind": "cosmetic", "slot": "title", "name": "Raja Aturan Rantai", "icon": "m-chain", "price": 50,
     "desc": "Gelar keren di bawah namamu."},
    {"key": "title-tak-hingga", "kind": "cosmetic", "slot": "title", "name": "Penjelajah Tak Hingga", "icon": "infinity", "price": 80,
     "desc": "Gelar keren di bawah namamu."},
    {"key": "title-duel", "kind": "cosmetic", "slot": "title", "name": "Jagoan Duel", "icon": "swords", "price": 90,
     "desc": "Gelar keren di bawah namamu."},
    {"key": "title-diamond", "kind": "cosmetic", "slot": "title", "name": "Pemburu Diamond", "icon": "diamond", "price": 120,
     "desc": "Gelar keren di bawah namamu."},
    {"key": "title-legenda", "kind": "cosmetic", "slot": "title", "name": "Legenda Kalkulus", "icon": "crown", "price": 150,
     "desc": "Gelar keren di bawah namamu."},
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
        raise ShopError("Item-nya gak ketemu.")
    with transaction.atomic():
        profile = _locked_profile(user)
        if profile.gems < item["price"]:
            raise ShopError(f"Diamond kamu kurang: butuh {item['price']}, baru punya {profile.gems}.")
        fields = ["gems"]
        if item["kind"] == "hearts":
            profile.refresh_hearts()
            if profile.hearts >= profile.max_hearts:
                raise ShopError("Heart kamu udah penuh.")
            profile.hearts = min(profile.max_hearts, profile.hearts + item.get("amount", profile.max_hearts))
            if profile.hearts >= profile.max_hearts:
                profile.hearts_lost_at = None          # penuh → hitungan 24 jam berhenti
            fields += ["hearts", "hearts_lost_at"]
        elif item["kind"] == "shield":
            if profile.star_shields >= MAX_SHIELDS:
                raise ShopError(f"Streak Shield kamu udah maksimal ({MAX_SHIELDS}).")
            if profile.star_shields + item["amount"] > MAX_SHIELDS:
                raise ShopError(f"Slot Streak Shield tinggal {MAX_SHIELDS - profile.star_shields}, paket ini isinya {item['amount']}.")
            profile.star_shields += item["amount"]
            fields.append("star_shields")
        else:
            _, created = OwnedItem.objects.get_or_create(user=user, item=key)
            if not created:
                raise ShopError("Item ini udah kamu punya.")
            profile.equipped = {**(profile.equipped or {}), item["slot"]: key}
            fields.append("equipped")
        profile.gems -= item["price"]
        profile.save(update_fields=fields)
    return state(profile)


def equip(user, key, on=True):
    """Pasang (on=True) atau lepas kosmetik milik pengguna. Mengembalikan state() terbaru."""
    item = ITEMS.get(key)
    if not item or item["kind"] != "cosmetic":
        raise ShopError("Item ini gak bisa dipakai.")
    if not OwnedItem.objects.filter(user=user, item=key).exists():
        raise ShopError("Beli item ini dulu, ya.")
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
