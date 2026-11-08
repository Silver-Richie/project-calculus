"""Helper penulisan soal bank: satu panggilan ``q(...)`` = satu soal pilihan ganda."""


def q(code, topic, difficulty, prompt, correct, wrong, steps, explanation="", diag=False):
    """
    Bangun dict soal bank.

    `correct` = teks opsi benar, `wrong` = 3 pengecoh (kesalahan yang sering terjadi).
    Urutan opsi tidak penting: opsi selalu diacak saat soal ditampilkan.
    Jawaban ringkas (`answer`) disamakan dengan opsi benar.
    """
    if len(wrong) != 3 or correct in wrong or len(set(wrong)) != 3:
        raise ValueError(f"{code}: butuh 3 pengecoh unik yang berbeda dari jawaban")
    return {
        "code": f"WH-{code}",
        "topic": topic,
        "difficulty": difficulty,
        "is_diagnostic": diag,
        "prompt": prompt,
        "options": [(correct, True)] + [(w, False) for w in wrong],
        "steps": list(steps),
        "answer": correct,
        "explanation": explanation,
    }
