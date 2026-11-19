"""Helper penulisan soal bank: satu panggilan ``q(...)`` = satu soal pilihan ganda."""

# Akhiran kode untuk salinan per fakultas (kode soal maksimal 20 karakter).
FACULTY_SUFFIX = {"ft": "T", "fm": "M", "fk": "K"}


def q(code, topic, difficulty, prompt, correct, wrong, steps, explanation="", diag=False,
      prefix="WH", source="buku-whitman"):
    """
    Bangun dict soal bank.

    `correct` = teks opsi benar, `wrong` = 3 pengecoh (kesalahan yang sering terjadi).
    Urutan opsi tidak penting: opsi selalu diacak saat soal ditampilkan.
    `topic` boleh berupa tuple slug (lihat ``kl``): soal disalin ke tiap topik itu.
    `source` = slug SourceDocument asal soal, `prefix` = awalan kode.
    """
    if len(wrong) != 3 or correct in wrong or len(set(wrong)) != 3:
        raise ValueError(f"{code}: butuh 3 pengecoh unik yang berbeda dari jawaban")
    return {
        "code": f"{prefix}-{code}",
        "topic": topic,
        "difficulty": difficulty,
        "is_diagnostic": diag,
        "prompt": prompt,
        "options": [(correct, True)] + [(w, False) for w in wrong],
        "steps": list(steps),
        "answer": correct,
        "explanation": explanation,
        "source": source,
    }


def kl(name):
    """Topik Kalkulus Lanjut yang sama di ketiga jalur: kl("tp-parsial") → (kl-ft-…, kl-fm-…, kl-fk-…)."""
    return tuple(f"kl-{fac}-{name}" for fac in FACULTY_SUFFIX)


def expand(questions):
    """
    Pecah soal bertopik tuple menjadi satu salinan per topik.

    Mechanism: topik Kalkulus Lanjut dibuat terpisah per fakultas (kl-ft-…, kl-fm-…,
    kl-fk-…). Soal yang sama dipakai di ketiganya; tiap salinan mendapat akhiran kode
    fakultas (T/M/K) agar kode tetap unik dan bisa dibatasi ke fakultasnya saat seed.
    """
    out = []
    for d in questions:
        if isinstance(d["topic"], str):
            out.append(d)
            continue
        for slug in d["topic"]:
            fac = slug.split("-")[1]
            out.append({**d, "topic": slug, "code": d["code"] + FACULTY_SUFFIX[fac]})
    return out
