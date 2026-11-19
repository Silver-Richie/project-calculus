"""
Calculus Bridge - Level pemain dari total XP.

Mechanism
---------
* XP hanya didapat dari sesi latihan topik (lihat sessions.submit_session: hanya selisih
  skor terbaik yang dihitung, jadi mengulang sesi tidak bisa menggandakan XP).
* Level tidak disimpan di database: selalu dihitung dari total XP, jadi tidak pernah
  tidak sinkron dan papan peringkat cukup mengurutkan XP.
* Naik dari Level n ke n+1 butuh 100 + 50·(n − 1) XP:
      Level 1 → 2 : 100 XP     (total 100)
      Level 2 → 3 : 150 XP     (total 250)
      Level 3 → 4 : 200 XP     (total 450)
  Total XP untuk mencapai Level n = 100(n−1) + 25(n−1)(n−2).
"""

BASE = 100   # XP untuk Level 1 → 2
STEP = 50    # tambahan kebutuhan XP tiap level


def xp_to_next(level):
    """XP yang dibutuhkan untuk naik dari `level` ke `level + 1`."""
    return BASE + STEP * (level - 1)


def total_xp_for(level):
    """Total XP minimal untuk berada di `level`."""
    n = level - 1
    return BASE * n + STEP * n * (n - 1) // 2


def level_for(xp):
    """Level untuk total `xp` (minimal 1)."""
    level = 1
    while xp >= total_xp_for(level + 1):
        level += 1
    return level


def level_info(xp):
    """Ringkasan untuk tampilan: level, XP di level ini, dan XP yang dibutuhkan ke level berikutnya."""
    level = level_for(xp)
    into = xp - total_xp_for(level)
    need = xp_to_next(level)
    return {"level": level, "xp": xp, "into": into, "need": need, "percent": round(100 * into / need)}
