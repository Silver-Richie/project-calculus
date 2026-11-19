"""
Calculus Bridge - Asal kampus pemain (untuk papan peringkat per kampus).

Mechanism
---------
* Diisi saat onboarding (halaman pilih fakultas) dan bisa diubah di Profil.
* Isian bebas, dibantu daftar saran (SUGGESTIONS) agar penulisan nama kampus seragam;
  spasi dirapikan. "Umum" = bukan mahasiswa / tidak ingin menyebutkan kampus, dan
  tidak ikut papan peringkat per kampus.
"""

UMUM = "Umum"
MAX_LEN = 120

SUGGESTIONS = [
    "Universitas Indonesia",
    "Institut Teknologi Bandung",
    "Universitas Gadjah Mada",
    "Institut Teknologi Sepuluh Nopember",
    "IPB University",
    "Universitas Airlangga",
    "Universitas Padjadjaran",
    "Universitas Diponegoro",
    "Universitas Brawijaya",
    "Universitas Sebelas Maret",
    "Universitas Hasanuddin",
    "Universitas Sumatera Utara",
    "Universitas Andalas",
    "Universitas Sriwijaya",
    "Universitas Udayana",
    "Universitas Negeri Yogyakarta",
    "Universitas Negeri Malang",
    "Universitas Negeri Surabaya",
    "Universitas Negeri Semarang",
    "Universitas Pendidikan Indonesia",
    "Universitas Negeri Jakarta",
    "Universitas Jember",
    "Universitas Lampung",
    "Universitas Riau",
    "Universitas Syiah Kuala",
    "Universitas Mulawarman",
    "Universitas Lambung Mangkurat",
    "Universitas Sam Ratulangi",
    "Universitas Tanjungpura",
    "Universitas Mataram",
    "Universitas Pembangunan Nasional Veteran Jakarta",
    "Universitas Pembangunan Nasional Veteran Yogyakarta",
    "Universitas Pembangunan Nasional Veteran Jawa Timur",
    "Institut Teknologi Sumatera",
    "Institut Teknologi Kalimantan",
    "Politeknik Negeri Jakarta",
    "Politeknik Negeri Bandung",
    "Politeknik Elektronika Negeri Surabaya",
    "Telkom University",
    "Universitas Bina Nusantara",
    "Universitas Trisakti",
    "Universitas Islam Indonesia",
    "Universitas Muhammadiyah Yogyakarta",
    "Universitas Muhammadiyah Malang",
    "Universitas Islam Negeri Syarif Hidayatullah Jakarta",
    "Universitas Katolik Parahyangan",
    "Universitas Kristen Petra",
    "Universitas Atma Jaya Yogyakarta",
    "Universitas Tarumanagara",
    "Universitas Gunadarma",
    "Universitas Mercu Buana",
    "Universitas Pelita Harapan",
    "Universitas Esa Unggul",
    "Universitas Dian Nuswantoro",
]


def normalize(name):
    """Rapikan spasi; "umum" (huruf apa pun) → UMUM. Kosong tetap kosong."""
    name = " ".join((name or "").split())[:MAX_LEN]
    return UMUM if name.lower() == UMUM.lower() else name
