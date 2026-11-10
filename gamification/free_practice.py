"""
Latihan Bebas (free practice): latihan murni tanpa nyawa dan tanpa XP.

Mechanism
---------
* Pengguna memilih fakultas → level → satu atau beberapa topik, lalu jumlah soal (1–15).
* Kumpulan soal tiap topik = semua generator topik itu + soal bank/PDF yang menempel
  ke sesi topik itu (hanya yang terlihat untuk fakultas terpilih).
* Soal diambil bergiliran antar-topik (topik dikocok, isi tiap topik dikocok
  Fisher-Yates) agar campurannya seimbang; soal tetap tidak berulang dalam satu set,
  generator boleh muncul lagi dengan angka baru. Seed benar-benar acak setiap kali.
* Tidak ada yang disimpan dan tidak ada XP, jadi kunci jawaban ikut dikirim dan
  penilaian dilakukan langsung di browser.
"""

import random

from django.db.models import Count, Q

from . import generators
from .models import MainLevel, Question, Topic
from .sessions import _fixed_question_payload

MAX_QUESTIONS = 15
FREE_TIERS = (1, 2, 3)          # tingkat generator yang dipakai: Mudah, Sedang, Sulit
BANK_LABELS = {"basic": "Mudah", "medium": "Sedang", "high": "Sulit"}


def _visible_topics(faculty):
    """Topik yang terlihat di jalur fakultas (umum + khusus fakultas itu)."""
    return (Topic.objects.filter(Q(node__faculty__isnull=True) | Q(node__faculty=faculty))
            .select_related("node__main_level").order_by("node__order", "order"))


def catalog(faculty):
    """
    Pilihan level → topik untuk satu fakultas, beserta perkiraan jumlah variasi soal per topik.

    Returns: [{"slug", "title", "icon", "topics": [{"slug", "title", "icon", "count"}]}, ...]
    """
    bank = dict(
        Question.objects.filter(session__isnull=False)
        .filter(Q(faculty__isnull=True) | Q(faculty=faculty))
        .values_list("session__topic__slug").annotate(n=Count("id"))
    )
    gens = {}
    for g in generators.REGISTRY.values():
        for slug in g.topics:
            gens[slug] = gens.get(slug, 0) + 1
    levels = {m.slug: {"slug": m.slug, "title": m.title, "icon": m.icon, "topics": []}
              for m in MainLevel.objects.order_by("order")}
    for t in _visible_topics(faculty):
        n = bank.get(t.slug, 0) + gens.get(t.slug, 0)
        if n and t.node.main_level_id:
            levels[t.node.main_level.slug]["topics"].append(
                {"slug": t.slug, "title": t.title, "icon": t.icon, "count": n})
    return [lvl for lvl in levels.values() if lvl["topics"]]


def _pool(topic, faculty):
    gens = [("g", g.key) for g in generators.REGISTRY.values() if topic.slug in g.topics]
    fixed = (Question.objects.filter(session__topic=topic)
             .filter(Q(faculty__isnull=True) | Q(faculty=faculty)).values_list("code", flat=True))
    return gens + [("q", code) for code in fixed]


def build_quiz(faculty, topic_slugs, count, rng=None):
    """
    Susun `count` soal acak dari topik terpilih (lihat docstring modul).

    Raise ValueError bila tidak ada topik valid untuk fakultas ini.
    """
    rng = rng or random.Random()
    count = max(1, min(MAX_QUESTIONS, int(count)))
    topics = [t for t in _visible_topics(faculty) if t.slug in set(topic_slugs)]
    pools = {t.slug: _pool(t, faculty) for t in topics}
    pools = {slug: items for slug, items in pools.items() if items}
    if not pools:
        raise ValueError("Pilih minimal satu topik yang tersedia.")
    titles = {t.slug: t.title for t in topics}

    order = list(pools)
    rng.shuffle(order)
    bags = {slug: [] for slug in order}
    used, picked = set(), []
    while len(picked) < count:
        progressed = False
        for slug in order:
            if len(picked) == count:
                break
            if not bags[slug]:
                bags[slug] = [it for it in pools[slug] if not (it[0] == "q" and it[1] in used)]
                rng.shuffle(bags[slug])
            if not bags[slug]:
                continue
            kind, key = bags[slug].pop()
            if kind == "q":
                used.add(key)
            picked.append((slug, kind, key))
            progressed = True
        if not progressed:      # semua topik hanya berisi soal tetap yang sudah terpakai
            break
    rng.shuffle(picked)

    fixed = {q.code: q for q in Question.objects.filter(code__in=[k for _, kind, k in picked if kind == "q"])
             .prefetch_related("options")}
    out = []
    for i, (slug, kind, key) in enumerate(picked, start=1):
        seed = rng.randrange(10 ** 9)
        if kind == "g":
            gen = generators.REGISTRY[key]
            tier = rng.choice([t for t in gen.tiers if t in FREE_TIERS] or [min(gen.tiers)])
            q = generators.generate(key, seed, tier)
            q["id"] = f"f:{key}:{seed}:{tier}"
            q["code"] = f"LB-{i:02d}"
            q["difficulty_label"] = generators.TIER_LABELS[tier]
        else:
            q = _fixed_question_payload(fixed[key], seed)
            q["difficulty_label"] = BANK_LABELS[fixed[key].difficulty]
        q["topic"] = titles[slug]
        out.append(q)
    return out


# ── Kuis coba untuk tamu (homepage, tanpa login) ──────────────────────────────
TRIAL_PLAN = (("kalkulus-dasar", 3), ("kalkulus-menengah", 2))   # (level, jumlah soal)
TRIAL_TIERS = (1, 2)                                              # Mudah & Sedang


def trial_quiz(rng=None):
    """
    5 soal coba untuk homepage: 3 dari level Kalkulus Dasar lalu 2 dari Kalkulus Tingkat
    Menengah, tingkat Mudah/Sedang, masing-masing dari topik umum yang berbeda.

    Hanya memakai generator (angka baru setiap kali). Tidak ada yang disimpan, jadi kunci
    jawaban ikut dikirim dan penilaian dilakukan di browser — sama seperti Latihan Bebas.
    """
    rng = rng or random.Random()
    out = []
    for level_slug, n in TRIAL_PLAN:
        topics = (Topic.objects.filter(node__faculty__isnull=True, node__main_level__slug=level_slug)
                  .select_related("node__main_level"))
        cands = [(t, g) for t in topics for g in generators.REGISTRY.values()
                 if t.slug in g.topics and set(g.tiers) & set(TRIAL_TIERS)]
        rng.shuffle(cands)
        used = set()
        for topic, gen in cands:
            if len(used) == n:
                break
            if topic.slug in used:
                continue
            used.add(topic.slug)
            tier = rng.choice([t for t in gen.tiers if t in TRIAL_TIERS])
            seed = rng.randrange(10 ** 9)
            q = generators.generate(gen.key, seed, tier)
            q["code"] = f"COBA-{len(out) + 1}"
            q["difficulty_label"] = generators.TIER_LABELS[tier]
            q["topic"] = topic.title
            q["level"] = topic.node.main_level.title
            out.append(q)
    return out
