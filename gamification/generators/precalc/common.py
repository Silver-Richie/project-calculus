"""Bagian bersama generator PreCalculus: pengambilan angka acak & grafik garis bilangan."""

from ..graphs import g2d, param, pt, readout, seg


def nz(rng, lo, hi, exclude=(0,)):
    """Bilangan bulat acak di [lo, hi] selain nilai di `exclude`."""
    while True:
        v = rng.randint(lo, hi)
        if v not in exclude:
            return v


def distinct(rng, lo, hi, k, exclude=()):
    """k bilangan bulat berbeda dari [lo, hi]."""
    pool = [v for v in range(lo, hi + 1) if v not in exclude]
    return rng.sample(pool, k)


def number_line(title, lo, hi, lo_closed, hi_closed, caption, xr=None, labels=("a", "b")):
    """
    Garis bilangan untuk himpunan/interval dengan slider ujung a (dan b).

    lo/hi = None berarti tak terbatas (ruas digambar sampai tepi grafik).
    Titik penuh = ujung termasuk, titik kosong = ujung tidak termasuk.
    """
    vals = [v for v in (lo, hi) if v is not None]
    if xr is None:
        xr = [min(vals) - 4, max(vals) + 4]
    params, els, reads = [], [], []
    left, right = (f"{xr[0]}", f"{xr[1]}")
    if lo is not None:
        params.append(param("a", f"Ujung kiri {labels[0]}", xr[0] + 1, xr[1] - 1, 0.5, float(lo), labels[0]))
        left = "a"
        reads.append(readout(f"Ujung kiri {labels[0]}", "a", 2))
    if hi is not None:
        params.append(param("b", f"Ujung kanan {labels[1]}", xr[0] + 1, xr[1] - 1, 0.5, float(hi), labels[1]))
        right = "b"
        reads.append(readout(f"Ujung kanan {labels[1]}", "b", 2))
    els.append(seg(left, 0, right, 0, color="green", width=7))
    if lo is not None:
        els.append(pt("a", 0, color="green", hollow=not lo_closed))
    if hi is not None:
        els.append(pt("b", 0, color="green", hollow=not hi_closed))
    if lo is not None and hi is not None:
        reads.append(readout("Panjang interval b − a", "b-a", 2))
    return g2d(title, xr, [-1.5, 1.5], params, els, reads, caption)
