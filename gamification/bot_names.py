"""
Calculus Bridge - Identitas bot Ranked Duel yang terlihat seperti pemain sungguhan.

Mechanism: nama = pola acak (nama+angka, kampus/jurusan, istilah kalkulus, gaya gamer, angkatan, …)
diisi bagian-bagian acak, lalu gaya hurufnya divariasikan. Fakultas di kartu selalu cocok dengan
petunjuk di nama (mis. "Maba_MIPA" → FMIPA, "Rizky_Sipil" → FT). Ribuan kombinasi, jarang berulang.
Nama yang kebetulan sama dengan username pengguna asli diacak ulang (bot tidak pernah meniru orang nyata).
"""

NAMES = """
adit adi agus agung aldi alif alya amel anisa anggi annisa ardi arief ariel arya asep ayu bagas bayu bella bima
budi cahya caca citra dafa dandi danu dea dewi dhika dian dika dimas dina dinda dio dita doni eka elsa evan fadil
fahri fajar farah farel fauzan febri fikri fira gabriel galih gita gilang hafiz hana hanif hendra ica ilham indah
intan irfan irma jaka joko joshua kevin kezia kirana laila laras lia lukman made maya mega mira nabila nadia nanda
naufal nayla nia nisa novi nurul oka okta pandu putra putri rafi raka rani rara rehan reza ria rian rifqi rina
rizky robby salsa sandi sari satria seno sinta stefani syifa taufik teguh tiara tika tio tommy tri ucup udin
vania vina wahyu wayan widi wulan yoga yosua yudha yuni zaki zahra zidan ketut nyoman gede putu ucok butet
""".split()

KAMPUS = ["UI", "ITB", "UGM", "ITS", "IPB", "Unpad", "Undip", "Unair", "UB", "UNS", "Telkom", "Binus", "UNY",
          "UPI", "Unhas", "USU", "Unand", "Unsri", "Udayana", "UMY", "Gunadarma", "Trisakti", "UPN", "Tel-U"]

# fakultas tampilan, kata di nama, jurusan
FAKULTAS = {
    "FT": ("Teknik", ["Sipil", "Mesin", "Elektro", "TekKim", "Industri", "Arsi", "Lingkungan", "Metal", "Kapal", "Geodesi"]),
    "FMIPA": ("MIPA", ["Mat", "Fisika", "Kimia", "Bio", "Statistik", "Aktuaria", "Geofis", "Astro"]),
    "Fasilkom": ("Fasilkom", ["IF", "SI", "Ilkom", "DataSains", "CS", "SisInfo"]),
}

KALKULUS = ["Integral", "Turunan", "Limit", "Sigma", "Deret", "Vektor", "Matriks", "Gradien", "Fourier", "Taylor",
            "Euler", "Laplace", "Lagrange", "Jacobian", "Kalkulus", "Epsilon", "Delta", "Pi", "Tangen", "Asimtot"]

CITA = ["Insinyur", "Programmer", "DataScientist", "Fisikawan", "Aktuaris", "Matematikawan", "Peneliti",
        "Dosen", "Arsitek", "Engineer", "Analis", "Developer"]

# {nama} {nama2} {kampus} {fac} {jur} {kalk} {cita} {n1} {n2} {n3} {n4} {thn}
POLA = [
    "{nama}{n2}", "{nama}{n3}", "{nama}_{n2}", "{nama}.{n3}", "{nama}{thn}", "{nama}.{nama2}", "{nama}_{nama2}",
    "{nama}_{kampus}", "{nama}{kampus}{thn}", "{nama}_{jur}", "{jur}{thn}_{nama}", "{nama}.{jur}",
    "Maba_{fac}", "Maba{kampus}{thn}", "Maba_{jur}{n2}", "Anonim_{fac}", "Ambis_{fac}", "Ambis{kampus}",
    "Anak{fac}{n2}", "Anak{jur}", "Pejuang{jur}", "MhsTingkatAkhir{n2}", "Semester{n1}_{jur}",
    "Guest{n4}", "Player{n4}", "user{n4}", "Anonim{n4}", "{nama}{n4}",
    "PejuangKalkulus", "PejuangKalkulus{n2}", "{kalk}Master", "{kalk}_{nama}", "Raja{kalk}", "Si{kalk}{n2}",
    "{kalk}{n2}", "{kalk}Lover", "Ratu{kalk}", "dy_dx_{n2}", "NoLimit{n2}", "IntegralKehidupan", "TurunanPertama{n2}",
    "LimitTakHingga", "SigmaGrindset{n2}", "KopiDanKalkulus", "Calon{cita}", "Calon{cita}{n2}", "{nama}Calon{cita}",
    "{nama}Ngoding", "{nama}DiLab", "{nama}GakBolos", "AnakKos{n2}", "BegadangLagi{n2}", "UTSMenanti", "{nama}Ambis",
    "xX{nama}Xx", "{nama}_official", "the.{nama}", "{nama}{nama2}{n2}", "not{nama}", "real{nama}{n2}",
]


def _style(name, rng):
    """Variasi gaya huruf seperti username sungguhan."""
    r = rng.random()
    if r < 0.45:
        return name
    if r < 0.85:
        return name.lower()
    if r < 0.95:
        return name[:1].upper() + name[1:]
    return name.upper()


def generate(rng, taken=lambda name: False, tries=8):
    """
    Identitas bot: {"name", "username", "faculty"}. `taken(nama)` → True bila nama dipakai pengguna asli
    (nama diacak ulang). Fakultas kartu mengikuti petunjuk fakultas/jurusan di nama; selain itu acak.
    """
    for _ in range(tries):
        short = rng.choice(list(FAKULTAS))
        fac, jurusan = FAKULTAS[short]
        nama = rng.choice(NAMES)
        nama2 = rng.choice([x for x in NAMES if x != nama])
        part = lambda s: s.title() if rng.random() < 0.55 else s      # noqa: E731
        name = rng.choice(POLA).format(
            nama=part(nama), nama2=part(nama2), kampus=rng.choice(KAMPUS), fac=fac, jur=rng.choice(jurusan),
            kalk=rng.choice(KALKULUS), cita=rng.choice(CITA), n1=rng.randint(1, 8), n2=rng.randint(10, 99),
            n3=rng.randint(100, 999), n4=rng.randint(1000, 9999), thn=rng.randint(21, 25))
        if name.isalpha() and rng.random() < 0.6:                       # pola tetap (mis. LimitTakHingga) diberi angka
            name += str(rng.randint(2, 99))
        name = _style(name, rng)
        if not taken(name):
            return {"name": name, "username": name.lower(), "faculty": short}
    return {"name": f"Guest{rng.randint(10000, 99999)}", "username": "", "faculty": short}
