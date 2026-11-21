"""
Calculus Bridge - Rank duel: tier, sub-rank, bintang (mirip Mobile Legends) dan nilai kemampuan tersembunyi.

Tangga rank (bawah → atas):
    Terra III → Terra II → Terra I → Luna III … Luna I → Solar III … Solar I → Nova III … Nova I → Apex
Bintang yang harus penuh di tiap sub-rank: Terra 3, Luna 4, Solar 4, Nova 5.
Apex tidak punya sub-rank dan tidak memakai bintang: Apex Points (mirip ELO, terlihat) dengan gelar
Apex (0–249), Apex Orbit (250+), Apex Galaksi (500+), Apex Kosmos (1000+).

Aturan hasil duel (apply_result):
* Menang  → +1 bintang. Kemenangan beruntun ke-3, ke-6, … di Terra–Solar memberi +1 bintang bonus.
            Menang saat bintang sudah penuh → naik sub-rank (atau tier) dengan 1 bintang;
            masuk Apex dengan 0 Apex Points.
* Kalah   → −1 bintang, kecuali:
            - di Terra III & Terra II (ramah pemula) tidak kehilangan bintang;
            - protected=True (Streak Shield terpakai) tidak kehilangan bintang/poin.
            Kalah saat 0 bintang → turun satu sub-rank dengan bintang penuh − 1. Tidak bisa turun di bawah Terra III.
* Apex    → menang +apex_delta, kalah −apex_delta (10–20, lihat apex_delta: makin kuat lawan, makin besar
            hadiah menang dan makin kecil hukuman kalah). Poin di bawah 0 → turun ke Nova I 4★.
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
TERRA_SAFE_DIVISIONS = (3, 2)                                   # Terra III & II kebal kehilangan bintang
APEX_TITLES = [(1000, "Kosmos"), (500, "Galaksi"), (250, "Orbit")]   # ambang Apex Points
APEX_MIN_DELTA, APEX_MAX_DELTA = 10, 20

MMR_START = 1000
MMR_K = 32


@dataclass(frozen=True)
class RankState:
    tier: str = "terra"
    division: int | None = 3          # None untuk Apex
    stars: int = 0
    win_streak: int = 0
    apex_points: int = 0              # hanya bermakna di Apex


def _promote(st):
    """Naik satu sub-rank (atau tier) dengan 1 bintang."""
    if st.division and st.division > 1:
        return replace(st, division=st.division - 1, stars=1)
    nxt = TIERS[TIERS.index(st.tier) + 1]
    if nxt == "apex":
        return replace(st, tier="apex", division=None, stars=0, apex_points=0)
    return replace(st, tier=nxt, division=3, stars=1)


def _demote(st):
    """Turun satu sub-rank dengan bintang penuh − 1; Terra III adalah lantai."""
    if st.tier == "apex":
        return replace(st, tier="nova", division=1, stars=STARS["nova"] - 1, apex_points=0)
    if st.division < 3:
        return replace(st, division=st.division + 1, stars=STARS[st.tier] - 1)
    if st.tier == "terra":
        return st
    prev = TIERS[TIERS.index(st.tier) - 1]
    return replace(st, tier=prev, division=1, stars=STARS[prev] - 1)


def _add_star(st):
    if st.stars < STARS[st.tier]:
        return replace(st, stars=st.stars + 1)
    return _promote(st)


def apex_delta(my_mmr, opponent_mmr, won):
    """
    Perubahan Apex Points (10–20) dari peluang menang ala ELO.

    Menang lawan kuat → mendekati +20; menang lawan lemah → mendekati +10.
    Kalah dari lawan kuat → mendekati −10; kalah dari lawan lemah → mendekati −20.
    """
    expected = 1 / (1 + 10 ** ((opponent_mmr - my_mmr) / 400))
    span = APEX_MAX_DELTA - APEX_MIN_DELTA
    return round(APEX_MIN_DELTA + span * ((1 - expected) if won else expected))


def apply_result(st, won, protected=False, apex_change=APEX_MIN_DELTA):
    """
    Keadaan rank baru setelah satu duel.

    apex_change = besar perubahan Apex Points (hasil apex_delta) bila pemain di Apex.
    Returns: (RankState baru, perubahan_untuk_tampilan) — bintang (mis. +2 saat bonus beruntun,
    0 saat dilindungi, −1 saat kalah biasa) atau Apex Points bila pemain di Apex.
    """
    if st.tier == "apex":
        if won:
            return replace(st, win_streak=st.win_streak + 1, apex_points=st.apex_points + apex_change), apex_change
        new = replace(st, win_streak=0)
        if protected:
            return new, 0
        if st.apex_points - apex_change < 0:
            return _demote(new), -apex_change
        return replace(new, apex_points=st.apex_points - apex_change), -apex_change
    if won:
        streak = st.win_streak + 1
        gain = 1 + (1 if st.tier in STREAK_BONUS_TIERS and streak % STREAK_BONUS_EVERY == 0 else 0)
        new = replace(st, win_streak=streak)
        for _ in range(gain):
            if new.tier == "apex":
                break                                  # bintang bonus tidak terbawa ke Apex
            new = _add_star(new)
        return new, gain
    new = replace(st, win_streak=0)
    if (st.tier == "terra" and st.division in TERRA_SAFE_DIVISIONS) or protected:
        return new, 0
    if new.stars > 0:
        return replace(new, stars=new.stars - 1), -1
    return _demote(new), -1


def loses_on_defeat(st):
    """Apakah kekalahan (tanpa shield) akan mengurangi bintang/poin — dipakai untuk memutuskan konsumsi Streak Shield."""
    return st.tier == "apex" or apply_result(st, won=False)[1] < 0


def apex_title(points):
    for minimum, name in APEX_TITLES:
        if points >= minimum:
            return name
    return ""


def label(st):
    """Nama rank untuk tampilan, mis. 'Terra II' atau 'Apex Orbit'."""
    if st.tier == "apex":
        return f"Apex {apex_title(st.apex_points)}".strip()
    return f"{TIER_NAMES[st.tier]} {ROMAN[st.division]}"


def next_label(st):
    """Sub-rank berikutnya, mis. 'Luna II'; di Apex gelar Apex berikutnya ('' bila sudah Kosmos)."""
    if st.tier == "apex":
        title = next((name for minimum, name in reversed(APEX_TITLES) if st.apex_points < minimum), "")
        return f"Apex {title}" if title else ""
    return label(_promote(st))


def ladder_points(st):
    """Posisi di tangga sebagai satu angka (bintang kumulatif sejak Terra III 0★; di Apex ditambah Apex Points)."""
    pts = 0
    for tier in TIERS:
        if tier == st.tier:
            if tier == "apex":
                return pts + 1 + st.apex_points          # +1: Apex 0 poin tetap di atas Nova I bintang penuh
            return pts + (3 - st.division) * STARS[tier] + st.stars
        pts += 3 * STARS[tier]
    raise ValueError(st.tier)


def describe(st):
    """Ringkasan untuk API/tampilan."""
    return {
        "tier": st.tier, "tier_name": TIER_NAMES[st.tier], "division": st.division,
        "division_roman": ROMAN.get(st.division, ""), "stars": st.stars,
        "max_stars": STARS.get(st.tier),           # None untuk Apex (tanpa batas)
        "label": label(st), "apex_title": apex_title(st.apex_points) if st.tier == "apex" else "", "next_label": next_label(st),
        "win_streak": st.win_streak, "points": ladder_points(st), "apex_points": st.apex_points if st.tier == "apex" else None,
    }


def elo_update(rating, opponent, score, k=MMR_K):
    """Nilai kemampuan baru; score = 1 menang, 0.5 seri, 0 kalah."""
    expected = 1 / (1 + 10 ** ((opponent - rating) / 400))
    return round(rating + k * (score - expected))
