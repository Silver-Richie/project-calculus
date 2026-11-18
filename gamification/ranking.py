"""
Calculus Bridge - Rank duel: tier, sub-rank, bintang (mirip Mobile Legends) dan nilai kemampuan tersembunyi.

Tangga rank (bawah → atas):
    Terra III → Terra II → Terra I → Luna III … Luna I → Solar III … Solar I → Nova III … Nova I → Apex
Bintang yang harus penuh di tiap sub-rank: Terra 3, Luna 4, Solar 4, Nova 5.
Apex tidak punya sub-rank: bintang bertambah tanpa batas, dengan gelar
Apex (0–24★), Apex Orbit (25★+), Apex Galaksi (50★+), Apex Kosmos (100★+).

Aturan hasil duel (apply_result):
* Menang  → +1 bintang. Kemenangan beruntun ke-3, ke-6, … di Terra–Solar memberi +1 bintang bonus.
            Menang saat bintang sudah penuh → naik sub-rank (atau tier) dengan 1 bintang.
* Kalah   → −1 bintang, kecuali:
            - di Terra (ramah pemula) tidak kehilangan bintang;
            - kalah tipis (protected=True, selisih ≤ 1 soal benar) tidak kehilangan bintang.
            Kalah saat 0 bintang → turun satu sub-rank dengan bintang penuh − 1
            (Apex 0★ → Nova I 4★). Tidak bisa turun di bawah Terra III.
* Nilai kemampuan tersembunyi (Elo, mulai 1000, K = 32) dipakai untuk mencari lawan setara;
  tidak ditampilkan dan tidak mengubah jumlah bintang.

Urutan papan peringkat memakai ladder_points(): jumlah bintang sejak Terra III 0★, sehingga
satu angka bisa diurutkan langsung di database (seri dipecah nilai kemampuan).
"""

from dataclasses import dataclass, replace

TIERS = ["terra", "luna", "solar", "nova", "apex"]
TIER_NAMES = {"terra": "Terra", "luna": "Luna", "solar": "Solar", "nova": "Nova", "apex": "Apex"}
TIER_MEANING = {"terra": "Bumi", "luna": "Bulan", "solar": "Matahari", "nova": "Bintang Baru", "apex": "Puncak Tertinggi"}
STARS = {"terra": 3, "luna": 4, "solar": 4, "nova": 5}         # bintang penuh per sub-rank
DIVISIONS = (3, 2, 1)                                           # III → II → I
ROMAN = {3: "III", 2: "II", 1: "I"}
STREAK_BONUS_TIERS = ("terra", "luna", "solar")
STREAK_BONUS_EVERY = 3
APEX_TITLES = [(100, "Kosmos"), (50, "Galaksi"), (25, "Orbit")]

MMR_START = 1000
MMR_K = 32


@dataclass(frozen=True)
class RankState:
    tier: str = "terra"
    division: int | None = 3          # None untuk Apex
    stars: int = 0
    win_streak: int = 0


def _promote(st):
    """Naik satu sub-rank (atau tier) dengan 1 bintang."""
    if st.division and st.division > 1:
        return replace(st, division=st.division - 1, stars=1)
    nxt = TIERS[TIERS.index(st.tier) + 1]
    return replace(st, tier=nxt, division=None if nxt == "apex" else 3, stars=1)


def _demote(st):
    """Turun satu sub-rank dengan bintang penuh − 1; Terra III adalah lantai."""
    if st.tier == "apex":
        return replace(st, tier="nova", division=1, stars=STARS["nova"] - 1)
    if st.division < 3:
        return replace(st, division=st.division + 1, stars=STARS[st.tier] - 1)
    if st.tier == "terra":
        return st
    prev = TIERS[TIERS.index(st.tier) - 1]
    return replace(st, tier=prev, division=1, stars=STARS[prev] - 1)


def _add_star(st):
    if st.tier == "apex":
        return replace(st, stars=st.stars + 1)
    if st.stars < STARS[st.tier]:
        return replace(st, stars=st.stars + 1)
    return _promote(st)


def apply_result(st, won, protected=False):
    """
    Keadaan rank baru setelah satu duel.

    Returns: (RankState baru, perubahan_bintang_untuk_tampilan) — mis. +2 saat bonus beruntun,
    0 saat dilindungi, −1 saat kalah biasa.
    """
    if won:
        streak = st.win_streak + 1
        gain = 1 + (1 if st.tier in STREAK_BONUS_TIERS and streak % STREAK_BONUS_EVERY == 0 else 0)
        new = replace(st, win_streak=streak)
        for _ in range(gain):
            new = _add_star(new)
        return new, gain
    new = replace(st, win_streak=0)
    if st.tier == "terra" or protected:
        return new, 0
    if new.stars > 0:
        return replace(new, stars=new.stars - 1), -1
    return _demote(new), -1


def apex_title(stars):
    for minimum, name in APEX_TITLES:
        if stars >= minimum:
            return name
    return ""


def label(st):
    """Nama rank untuk tampilan, mis. 'Terra II' atau 'Apex Orbit'."""
    if st.tier == "apex":
        return f"Apex {apex_title(st.stars)}".strip()
    return f"{TIER_NAMES[st.tier]} {ROMAN[st.division]}"


def ladder_points(st):
    """Posisi di tangga sebagai satu angka (bintang kumulatif sejak Terra III 0★)."""
    pts = 0
    for tier in TIERS:
        if tier == st.tier:
            if tier == "apex":
                return pts + st.stars
            return pts + (3 - st.division) * STARS[tier] + st.stars
        pts += 3 * STARS[tier]
    raise ValueError(st.tier)


def describe(st):
    """Ringkasan untuk API/tampilan."""
    return {
        "tier": st.tier, "tier_name": TIER_NAMES[st.tier], "division": st.division,
        "division_roman": ROMAN.get(st.division, ""), "stars": st.stars,
        "max_stars": STARS.get(st.tier),           # None untuk Apex (tanpa batas)
        "label": label(st), "apex_title": apex_title(st.stars) if st.tier == "apex" else "",
        "win_streak": st.win_streak, "points": ladder_points(st),
    }


def elo_update(rating, opponent, score, k=MMR_K):
    """Nilai kemampuan baru; score = 1 menang, 0.5 seri, 0 kalah."""
    expected = 1 / (1 + 10 ** ((opponent - rating) / 400))
    return round(rating + k * (score - expected))
