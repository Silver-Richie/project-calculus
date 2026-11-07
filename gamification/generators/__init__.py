"""
Generator soal berparameter untuk sesi latihan.

Mechanism
---------
Setiap generator adalah fungsi ``gen(rng, tier) -> dict`` yang didaftarkan lewat
``@register(key, topic, tiers)``. ``rng`` adalah ``random.Random`` yang sudah
di-seed, ``tier`` adalah nomor sesi (1 Mudah … 5 Olimpiade). Generator
mengembalikan::

    {
        "prompt": "<html soal>",
        "correct": "jawaban benar (teks opsi)",
        "distractors": ["pengecoh 1", "pengecoh 2", "pengecoh 3", ...],
        "steps": ["langkah 1", ...],            # pembahasan bertahap
        "answer": "ringkasan jawaban",          # opsional, default = correct
        "explanation": "konsep kunci",          # opsional
        "graphs": [spec GraphLab, ...],         # opsional, slider di pembahasan
    }

``generate(key, seed, tier)`` membungkus hasil itu: mengacak urutan opsi dengan
rng yang sama sehingga soal yang sama persis dapat dibangun ulang di server
untuk penilaian hanya dari (key, seed, tier).
"""

import random
import re
from dataclasses import dataclass, field

TIER_LABELS = {1: "Mudah", 2: "Sedang", 3: "Sulit", 4: "Tantangan", 5: "Olimpiade"}
TIER_SLUGS = {1: "mudah", 2: "sedang", 3: "sulit", 4: "tantangan", 5: "olimpiade"}
TIER_DIFFICULTY = {1: "basic", 2: "medium", 3: "high", 4: "high", 5: "high"}
OPTION_COUNT = 4


@dataclass
class Generator:
    key: str
    topics: tuple
    tiers: tuple
    func: callable = field(repr=False)
    weight: int = 1

    @property
    def topic(self):
        """Topik utama (pertama) — untuk laporan/kompatibilitas."""
        return self.topics[0]


REGISTRY: dict[str, Generator] = {}


def register(key, topic, tiers, weight=1):
    """
    Dekorator: daftarkan generator untuk `topic` pada sesi-sesi `tiers`.

    `topic` boleh berupa satu slug atau tuple slug (generator yang sama dipakai
    beberapa topik, mis. topik inti Level 4 milik FT, FMIPA, dan Fasilkom).
    """
    topics = (topic,) if isinstance(topic, str) else tuple(topic)

    def deco(func):
        if key in REGISTRY:
            raise ValueError(f"Generator ganda: {key}")
        REGISTRY[key] = Generator(key, topics, tuple(tiers), func, weight)
        return func
    return deco


def for_topic(topic, tier):
    """Generator yang tersedia untuk satu topik pada satu tingkat sesi."""
    return [g for g in REGISTRY.values() if topic in g.topics and tier in g.tiers]


def _numeric_neighbours(text):
    """
    Pengecoh cadangan untuk jawaban berupa angka (bulat/pecahan/desimal).

    Dipakai hanya bila pengecoh dari generator bertabrakan dengan jawaban benar
    (mis. karena angka acak kebetulan membuat dua rumus salah bernilai sama).
    """
    from fractions import Fraction
    from .fmt import n as fmt_n
    import re
    raw = text.replace("−", "-").replace(",", ".").strip()
    try:
        v = Fraction(raw)
    except (ValueError, ZeroDivisionError):
        v = None
    if v is not None:
        cands = [v + 1, v - 1, -v, v * 2, v + 2, v - 2, v / 2 if v else Fraction(1, 2), v + Fraction(1, 2)]
        return [fmt_n(c) for c in cands]
    # Teks berisi angka (interval, titik, persamaan): geser satu angka ±1.
    nums = list(re.finditer(r"−?\d+", text))
    out = []
    for delta in (1, -1, 2):
        for m in nums:
            val = int(m.group().replace("−", "-")) + delta
            out.append(text[:m.start()] + fmt_n(val) + text[m.end():])
    return out


def _options(rng, correct, distractors):
    """
    Menyusun 4 opsi unik (1 benar + 3 pengecoh) lalu mengacaknya.

    Pengecoh yang sama dengan jawaban benar / duplikat dibuang. Generator wajib
    menyediakan cukup pengecoh berbeda; jika tidak, ValueError (ditangkap tes).
    """
    seen = {correct}
    picked = []
    for d in distractors:
        if d not in seen:
            seen.add(d)
            picked.append(d)
        if len(picked) == OPTION_COUNT - 1:
            break
    if len(picked) < OPTION_COUNT - 1:
        for d in _numeric_neighbours(correct):
            if d not in seen:
                seen.add(d)
                picked.append(d)
            if len(picked) == OPTION_COUNT - 1:
                break
    if len(picked) < OPTION_COUNT - 1:
        raise ValueError(f"Pengecoh kurang: {correct!r} vs {distractors!r}")
    opts = [(correct, True)] + [(d, False) for d in picked]
    rng.shuffle(opts)
    return opts


_ONE = re.compile(r"(?<![\d.,/\w])1(?=[xyzt]|√|e|π)")
_ONE_FUNC = re.compile(r"(?<![\d.,/\w])1 ?(?=(?:sin|cos|tan|ln|log))")


def tidy(text):
    """Rapikan teks matematika hasil generator: '1x' → 'x', '+ −3' → '− 3'."""
    if not isinstance(text, str):
        return text
    text = re.sub(r"−1 (?=sin|cos|tan|ln|log)", "−", text)
    text = _ONE_FUNC.sub("", text)
    return _ONE.sub("", text).replace("+ −", "− ").replace("+ -", "− ")


def generate(key, seed, tier):
    """Bangun satu soal lengkap secara deterministik dari (key, seed, tier)."""
    gen = REGISTRY[key]
    rng = random.Random(f"{key}|{seed}|{tier}")
    raw = gen.func(rng, tier)
    # Rapikan teks dulu, baru buang duplikat (mis. "1e²" dan "e²" menjadi sama setelah dirapikan).
    options = _options(rng, tidy(raw["correct"]), [tidy(d) for d in raw["distractors"]])
    return {
        "key": key,
        "seed": seed,
        "tier": tier,
        "difficulty": TIER_DIFFICULTY[tier],
        "prompt": tidy(raw["prompt"]),
        "options": [{"id": i, "text": t, "is_correct": ok} for i, (t, ok) in enumerate(options)],
        "steps": [tidy(st) for st in raw.get("steps", [])],
        "answer": tidy(raw.get("answer", raw["correct"])),
        "explanation": raw.get("explanation", ""),
        "graphs": raw.get("graphs", []),
    }


# Daftarkan semua modul generator (import memicu @register).
from . import precalc, dasar, menengah, lanjut  # noqa: E402,F401
