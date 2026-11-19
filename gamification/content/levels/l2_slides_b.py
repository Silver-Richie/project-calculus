r"""
Kurikulum v2 — Batch 2B: slide paruh kedua Level 2 (Kalkulus Dasar).

Topik: Aturan Turunan & Rantai · Turunan Implisit & Laju Terkait · Ekstremum & Teorema Nilai Rata-Rata ·
Sketsa Kurva & Optimasi · Integral Tak Tentu & Jumlah Riemann · Teorema Dasar Kalkulus · Teknik Substitusi.
Soal cerita (laju terkait, optimasi) memakai kerangka: Diketahui → Ditanya → Model Matematis → Turunkan → Evaluasi.

Rujukan: Purcell Jil. 1 Bab 2–5; Stewart 9e §3.1–3.9, §4.1–4.9, §5.1–5.5; OpenStax Calculus Vol 1 Bab 3–5.
"""

from ..helpers import param, readout
from .l1_slides import S, g, note, qa, steps


def kerangka(diketahui, ditanya, model, turunkan, evaluasi):
    """Kerangka soal cerita (laju terkait & optimasi) sebagai tabel lima baris."""
    rows = [("Diketahui", diketahui), ("Ditanya", ditanya), ("Model matematis", model), ("Turunkan", turunkan), ("Evaluasi", evaluasi)]
    body = "".join(f"<tr><th>{k}</th><td>{v}</td></tr>" for k, v in rows)
    return f'<div class="table-scroll"><table class="lesson-table kerangka"><tbody>{body}</tbody></table></div>'


# ═══════════════════════════════════════════════════════════════════════════
# 5. Aturan Turunan & Aturan Rantai
# ═══════════════════════════════════════════════════════════════════════════
RANTAI = [
    S("intuition", "Laju yang dikalikan berantai",
      r"""<p>Roda gigi A berputar 3 kali lebih cepat dari B, dan B 2 kali lebih cepat dari C. Maka A berputar $3 \times 2 = 6$ kali lebih cepat dari C.
      Itulah aturan rantai: laju perubahan fungsi bersusun = <b>perkalian</b> laju tiap lapisan.</p>
      <p>Di machine learning, <i>backpropagation</i> tidak lain adalah aturan rantai yang diterapkan lapis demi lapis dari loss ke tiap bobot.</p>""",
      "Aturan rantai = 'turunan luar (isi dibiarkan) × turunan dalam'. Ucapkan ini tiap kali ketemu fungsi bersusun."),
    S("theorem", "Aturan dasar: pangkat, perkalian, pembagian",
      r"""<p>$$\frac{d}{dx}c = 0, \qquad \frac{d}{dx}x^n = nx^{n-1}\ (n \in \mathbb{R}), \qquad (cf)' = cf', \qquad (f \pm g)' = f' \pm g'$$</p>
      <p>$$(fg)' = f'g + fg', \qquad \left(\frac{f}{g}\right)' = \frac{f'g - fg'}{g^2}$$</p>
      <p>Jembatan keledai aturan bagi: "<b>bawah</b> kali turunan atas <b>dikurangi</b> atas kali turunan bawah, per bawah kuadrat".</p>""",
      "Aturan pembagian itu urutannya penting karena ada tanda minus. Selalu mulai dari f'g (turunan ATAS dulu)."),
    S("theorem", "Tabel turunan fungsi transenden",
      r"""<div class="table-scroll"><table class="lesson-table"><thead><tr><th>$f(x)$</th><th>$f'(x)$</th><th>$f(x)$</th><th>$f'(x)$</th></tr></thead><tbody>
        <tr><td>$\sin x$</td><td>$\cos x$</td><td>$e^x$</td><td>$e^x$</td></tr>
        <tr><td>$\cos x$</td><td>$-\sin x$</td><td>$a^x$</td><td>$a^x \ln a$</td></tr>
        <tr><td>$\tan x$</td><td>$\sec^2 x$</td><td>$\ln|x|$</td><td>$\dfrac1x$</td></tr>
        <tr><td>$\sec x$</td><td>$\sec x \tan x$</td><td>$\log_a x$</td><td>$\dfrac{1}{x \ln a}$</td></tr>
        <tr><td>$\arcsin x$</td><td>$\dfrac{1}{\sqrt{1 - x^2}}$</td><td>$\arctan x$</td><td>$\dfrac{1}{1 + x^2}$</td></tr>
      </tbody></table></div>""",
      "Pola cepat: turunan fungsi berawalan 'co' (cos, cot, csc) selalu bertanda minus."),
    S("theorem", "Aturan rantai",
      r"""<p>Jika $y = f(u)$ dan $u = g(x)$ keduanya terdiferensialkan:
      $$\frac{dy}{dx} = \frac{dy}{du}\cdot\frac{du}{dx} \qquad\Longleftrightarrow\qquad \big(f(g(x))\big)' = f'(g(x))\,g'(x).$$</p>
      <p>Bentuk umum yang paling sering dipakai:</p>
      <p>$$\frac{d}{dx}[g(x)]^n = n[g(x)]^{n-1}g'(x), \qquad \frac{d}{dx}e^{g(x)} = e^{g(x)}g'(x), \qquad \frac{d}{dx}\ln g(x) = \frac{g'(x)}{g(x)}$$</p>""",
      "Untuk fungsi berlapis tiga atau lebih, kupas dari luar ke dalam satu per satu, dan kalikan semua turunannya.",
      [g("h(x) = sin(x²): singgung dengan kemiringan 2a·cos(a²)", [-3, 3], [-2, 2], [param("a", "Titik a", -2.5, 2.5, 0.05, 1, "a")],
         [{"type": "fn", "expr": "sin(x*x)", "color": "blue", "label": "sin(x²)"},
          {"type": "fn", "expr": "sin(a*a) + 2*a*cos(a*a)*(x - a)", "color": "red", "dash": True, "label": "singgung"},
          {"type": "point", "x": "a", "y": "sin(a*a)", "color": "red"}],
         [readout("h'(a) = 2a·cos(a²)", "2*a*cos(a*a)", 4)],
         "Makin jauh dari 0, faktor dalam 2a membuat grafik makin curam dan makin rapat.")]),
    S("example", "Bedah soal: perkalian & pembagian",
      r"""<p><b>Soal 1.</b> $\dfrac{d}{dx}\left(x^2 e^x\right)$.</p>""" +
      steps(r"Aturan perkalian dengan $f = x^2$, $g = e^x$: $2x \cdot e^x + x^2 \cdot e^x$.",
            r"Faktorkan: $x e^x (x + 2)$.") +
      r"""<p><b>Soal 2.</b> $\dfrac{d}{dx}\left(\dfrac{x^2 + 1}{x - 1}\right)$.</p>""" +
      steps(r"$f = x^2 + 1$, $f' = 2x$; $g = x - 1$, $g' = 1$.",
            r"$\dfrac{2x(x - 1) - (x^2 + 1)(1)}{(x - 1)^2} = \dfrac{x^2 - 2x - 1}{(x - 1)^2}$."),
      "Sebelum memakai aturan bagi, cek dulu apakah bisa disederhanakan jadi perkalian atau pangkat. Sering lebih cepat."),
    S("example", "Bedah soal: rantai berlapis",
      r"""<p><b>Soal 1.</b> $\dfrac{d}{dx}\sqrt{1 + \sin^2(3x)}$.</p>""" +
      steps(r"Lapisan luar: $\sqrt{\square}$, turunannya $\dfrac{1}{2\sqrt{\square}}$.",
            r"Lapisan tengah: $\sin^2(3x) = [\sin(3x)]^2$, turunannya $2\sin(3x)$.",
            r"Lapisan dalam: $\sin(3x) \to 3\cos(3x)$.",
            r"Kalikan: $\dfrac{2\sin(3x)\cdot 3\cos(3x)}{2\sqrt{1 + \sin^2(3x)}} = \dfrac{3\sin(3x)\cos(3x)}{\sqrt{1 + \sin^2(3x)}}$.") +
      r"""<p><b>Soal 2.</b> $\dfrac{d}{dx}\ln(\cos x) = \dfrac{-\sin x}{\cos x} = -\tan x$.</p>
      <p><b>Soal 3.</b> $\dfrac{d}{dx}e^{-x^2} = -2x\,e^{-x^2}$ (kurva lonceng distribusi normal).</p>""",
      "Tulis lapisan-lapisannya dulu seperti di Soal 1. Ini mencegah lupa satu faktor turunan dalam."),
    S("example", "Bedah soal: fungsi sigmoid (Fasilkom)",
      r"""<p><b>Soal.</b> Tunjukkan untuk $\sigma(z) = \dfrac{1}{1 + e^{-z}}$ berlaku $\sigma'(z) = \sigma(z)\big(1 - \sigma(z)\big)$.</p>""" +
      steps(r"Tulis $\sigma = (1 + e^{-z})^{-1}$; aturan rantai: $\sigma' = -(1 + e^{-z})^{-2}\cdot(-e^{-z}) = \dfrac{e^{-z}}{(1 + e^{-z})^2}$.",
            r"Pecah: $\dfrac{1}{1 + e^{-z}}\cdot\dfrac{e^{-z}}{1 + e^{-z}}$.",
            r"Faktor kedua $= \dfrac{(1 + e^{-z}) - 1}{1 + e^{-z}} = 1 - \sigma(z)$. Terbukti.") +
      note(r"Inilah alasan sigmoid populer di jaringan saraf awal: turunannya bisa dihitung ulang dari nilai fungsinya sendiri, murah secara komputasi."),
      "Trik 'tambah 1 kurangi 1' di Langkah 3 sering dipakai untuk memunculkan bentuk yang sudah kamu kenal."),
    S("pitfall", "Jebakan ujian",
      r"""<ul class="lesson-list">
        <li>$(fg)' \ne f'g'$ dan $\left(\tfrac{f}{g}\right)' \ne \tfrac{f'}{g'}$.</li>
        <li>Lupa turunan dalam: $\dfrac{d}{dx}\sin(5x) = 5\cos(5x)$, bukan $\cos(5x)$.</li>
        <li>$\dfrac{d}{dx}e^{2x} \ne e^{2x}$; yang benar $2e^{2x}$. Dan $\dfrac{d}{dx}x^e = e\,x^{e-1}$ (pangkat konstanta), beda dengan $e^x$.</li>
        <li>$\dfrac{d}{dx}2^x \ne x\,2^{x-1}$. Aturan pangkat hanya untuk <b>basis</b> variabel, bukan pangkat variabel.</li>
        <li>Urutan pembilang aturan bagi terbalik, sehingga tandanya salah.</li>
      </ul>""",
      "Bedakan x^e (aturan pangkat) dan e^x (eksponensial). Lihat di mana variabelnya: di basis atau di pangkat."),
    S("checkpoint", "Mini checkpoint",
      qa(r"1. $\dfrac{d}{dx}\tan^3(2x)$", r"<p>$3\tan^2(2x)\cdot\sec^2(2x)\cdot 2 = 6\tan^2(2x)\sec^2(2x)$.</p>") +
      qa(r"2. $\dfrac{d}{dx}\dfrac{\ln x}{x}$", r"<p>$\dfrac{\tfrac1x\cdot x - \ln x}{x^2} = \dfrac{1 - \ln x}{x^2}$.</p>"),
      "Soal 1 punya tiga lapisan: pangkat 3, tan, lalu 2x. Pastikan ada tiga faktor di jawabanmu."),
]

# ═══════════════════════════════════════════════════════════════════════════
# 6. Turunan Implisit & Laju Terkait
# ═══════════════════════════════════════════════════════════════════════════
LAJU = [
    S("intuition", "Kurva yang bukan grafik fungsi",
      r"""<p>Lingkaran $x^2 + y^2 = 25$ tidak bisa ditulis sebagai satu fungsi $y = f(x)$, tapi tetap punya garis singgung di tiap titik.
      <b>Turunan implisit</b> memperlakukan $y$ sebagai fungsi $x$ yang "tersembunyi", lalu menurunkan kedua ruas.</p>
      <p>Konsep yang sama, tetapi terhadap <b>waktu</b>, memberi <b>laju terkait</b>: kalau beberapa besaran terhubung oleh satu persamaan dan semuanya berubah terhadap waktu, laju-lajunya ikut terhubung.</p>""",
      "Kunci implisit: setiap kali menurunkan sesuatu yang mengandung y, kalikan dengan dy/dx (aturan rantai)."),
    S("derivation", "Langkah turunan implisit",
      steps(r"Turunkan kedua ruas terhadap $x$. Ingat $\dfrac{d}{dx}y^n = ny^{n-1}\dfrac{dy}{dx}$.",
            r"Kumpulkan semua suku yang mengandung $\dfrac{dy}{dx}$ di satu ruas.",
            r"Faktorkan $\dfrac{dy}{dx}$, lalu bagi.") +
      r"""<p><b>Contoh:</b> $x^2 + y^2 = 25 \Rightarrow 2x + 2y\dfrac{dy}{dx} = 0 \Rightarrow \dfrac{dy}{dx} = -\dfrac{x}{y}$.
      Di titik $(3, 4)$: kemiringan $-\tfrac34$.</p>""",
      "Jawaban turunan implisit boleh mengandung x DAN y. Itu wajar, karena kemiringan bergantung pada titik di kurva.",
      [g("Singgung pada lingkaran x² + y² = 25", [-7, 7], [-7, 7], [param("th", "Sudut titik (rad)", 0.2, 2.9, 0.05, 0.93, "θ")],
         [{"type": "fn", "expr": "sqrt(25 - x*x)", "color": "blue", "label": "lingkaran"},
          {"type": "fn", "expr": "-sqrt(25 - x*x)", "color": "blue"},
          {"type": "fn", "expr": "5*sin(th) + (-cos(th)/sin(th))*(x - 5*cos(th))", "color": "red", "dash": True, "label": "singgung"},
          {"type": "point", "x": "5*cos(th)", "y": "5*sin(th)", "color": "red"}],
         [readout("x", "5*cos(th)", 3), readout("y", "5*sin(th)", 3), readout("dy/dx = −x/y", "-cos(th)/sin(th)", 4)],
         "Garis singgung selalu tegak lurus jari-jari. Cek: kemiringan jari-jari y/x dikali −x/y = −1.")]),
    S("example", "Bedah soal: turunan implisit",
      r"""<p><b>Soal.</b> Daun Descartes $x^3 + y^3 = 6xy$. Cari $\dfrac{dy}{dx}$ dan garis singgung di $(3, 3)$.</p>""" +
      steps(r"Turunkan: $3x^2 + 3y^2 y' = 6y + 6x y'$ (aturan perkalian di ruas kanan).",
            r"Kumpulkan $y'$: $y'(3y^2 - 6x) = 6y - 3x^2$.",
            r"$y' = \dfrac{2y - x^2}{y^2 - 2x}$.",
            r"Di $(3, 3)$: $y' = \dfrac{6 - 9}{9 - 6} = -1$, jadi singgung $y = -x + 6$."),
      "Ruas kanan 6xy itu perkalian x dan y. Banyak yang lupa aturan perkalian di sini."),
    S("theorem", "Kerangka laju terkait",
      kerangka(r"Semua besaran yang <b>diketahui</b> beserta lajunya, misalnya $\tfrac{dV}{dt} = 2$ m³/menit. Gambar sketsa.",
               r"Laju yang dicari, <b>pada saat</b> tertentu, misalnya $\tfrac{dh}{dt}$ ketika $h = 3$ m.",
               r"Persamaan yang menghubungkan besaran-besaran itu (geometri, Pythagoras, segitiga sebangun). Eliminasi variabel yang tidak perlu.",
               r"Turunkan kedua ruas terhadap waktu $t$ (aturan rantai: tiap variabel menghasilkan $\tfrac{d\square}{dt}$).",
               r"<b>Baru sekarang</b> substitusi nilai pada saat itu. Selesaikan, cek tanda dan satuan.") +
      note(r"Nilai sesaat (seperti $h = 3$) disubstitusi <b>setelah</b> menurunkan. Kalau sebelum, besaran itu jadi konstanta dan turunannya hilang."),
      "Laju yang mengecil harus bertanda NEGATIF. Kalau air keluar 2 m³/menit, tulis dV/dt = −2."),
    S("example", "Soal UTS: tangga yang tergelincir",
      r"""<p>Tangga sepanjang $10$ m bersandar di dinding. Kaki tangga ditarik menjauh dengan laju $1$ m/s. Seberapa cepat ujung atas turun saat kaki tangga berjarak $6$ m dari dinding?</p>""" +
      kerangka(r"Panjang tangga $10$ m; $\tfrac{dx}{dt} = 1$ m/s ($x$ = jarak kaki ke dinding).",
               r"$\tfrac{dy}{dt}$ saat $x = 6$ ($y$ = tinggi ujung atas).",
               r"$x^2 + y^2 = 100$ (Pythagoras).",
               r"$2x\tfrac{dx}{dt} + 2y\tfrac{dy}{dt} = 0 \Rightarrow \tfrac{dy}{dt} = -\tfrac{x}{y}\tfrac{dx}{dt}$.",
               r"Saat $x = 6$: $y = \sqrt{100 - 36} = 8$. $\ \tfrac{dy}{dt} = -\tfrac{6}{8}(1) = -0.75$ m/s. Ujung atas <b>turun</b> $0.75$ m/s."),
      "Perhatikan: makin jauh kaki ditarik, ujung atas turun makin cepat. Geser slider x mendekati 10 dan lihat dy/dt meledak.",
      [g("Tangga 10 m: posisi kaki x", [-1, 11], [-1, 11], [param("x0", "Jarak kaki x (m)", 0.5, 9.8, 0.1, 6, "x")],
         [{"type": "segment", "x1": "x0", "y1": 0, "x2": 0, "y2": "sqrt(100 - x0*x0)", "color": "orange", "width": 5},
          {"type": "point", "x": "x0", "y": 0, "color": "blue"}, {"type": "point", "x": 0, "y": "sqrt(100 - x0*x0)", "color": "red"}],
         [readout("Tinggi y (m)", "sqrt(100 - x0*x0)", 3), readout("dy/dt (m/s) bila dx/dt = 1", "-x0/sqrt(100 - x0*x0)", 4)],
         "Di x = 6, dy/dt = −0,75 m/s.")]),
    S("example", "Soal UTS: tangki kerucut terbalik",
      r"""<p>Tangki kerucut terbalik berjari-jari atas $2$ m dan tinggi $4$ m. Air dipompa masuk $2$ m³/menit. Seberapa cepat permukaan air naik saat kedalamannya $3$ m?</p>""" +
      kerangka(r"$\tfrac{dV}{dt} = 2$ m³/menit; kerucut $R = 2$, $H = 4$.",
               r"$\tfrac{dh}{dt}$ saat $h = 3$ m.",
               r"$V = \tfrac13\pi r^2 h$. Segitiga sebangun: $\tfrac{r}{h} = \tfrac24 \Rightarrow r = \tfrac{h}{2}$, sehingga $V = \tfrac{\pi}{12}h^3$.",
               r"$\tfrac{dV}{dt} = \tfrac{\pi}{4}h^2\tfrac{dh}{dt}$.",
               r"$2 = \tfrac{\pi}{4}(9)\tfrac{dh}{dt} \Rightarrow \tfrac{dh}{dt} = \tfrac{8}{9\pi} \approx 0.283$ m/menit.") +
      note(r"Eliminasi $r$ <b>sebelum</b> menurunkan, karena kita tidak tahu $\tfrac{dr}{dt}$. Segitiga sebangun adalah trik standar soal kerucut."),
      "Soal kerucut hampir selalu butuh segitiga sebangun untuk membuang satu variabel. Cari dulu rasio r/h."),
    S("pitfall", "Jebakan ujian",
      r"""<ul class="lesson-list">
        <li>Substitusi nilai sesaat sebelum menurunkan, misalnya menulis $x = 6$ dulu sehingga $\tfrac{dx}{dt}$ lenyap.</li>
        <li>Lupa tanda negatif untuk besaran yang berkurang.</li>
        <li>$\dfrac{d}{dx}(y^2) = 2y$; yang benar $2y\dfrac{dy}{dx}$.</li>
        <li>Mencampur satuan (cm dan m, menit dan detik).</li>
        <li>Menjawab dengan rumus, padahal yang ditanya adalah angka beserta satuan dan arti tanda (naik/turun).</li>
      </ul>""",
      "Tulis jawaban akhir sebagai kalimat lengkap: 'ujung atas turun dengan laju 0,75 m/s'. Banyak dosen memberi poin di situ."),
    S("checkpoint", "Mini checkpoint",
      qa(r"1. Balon bulat dipompa $100$ cm³/s. Seberapa cepat jari-jarinya bertambah saat $r = 5$ cm?",
         r"<p>$V = \tfrac43\pi r^3 \Rightarrow \tfrac{dV}{dt} = 4\pi r^2 \tfrac{dr}{dt}$. $100 = 100\pi\,\tfrac{dr}{dt} \Rightarrow \tfrac{dr}{dt} = \tfrac{1}{\pi} \approx 0.318$ cm/s.</p>") +
      qa(r"2. Cari $\dfrac{dy}{dx}$ dari $\sin(xy) = x$.",
         r"<p>$\cos(xy)(y + xy') = 1 \Rightarrow y' = \dfrac{1 - y\cos(xy)}{x\cos(xy)}$.</p>"),
      "Soal 1 memakai kerangka yang sama: model V(r), turunkan terhadap t, baru masukkan r = 5."),
]

# ═══════════════════════════════════════════════════════════════════════════
# 7. Ekstremum & Teorema Nilai Rata-Rata
# ═══════════════════════════════════════════════════════════════════════════
EKSTREM = [
    S("intuition", "Puncak dan lembah",
      r"""<p>Di puncak bukit atau dasar lembah yang mulus, garis singgung mendatar: kemiringan $0$. Ide sederhana ini adalah inti optimasi:
      biaya minimum, keuntungan maksimum, loss terkecil saat melatih model.</p>""",
      "Ekstrem terjadi di tempat kemiringan nol ATAU di tempat yang 'patah' atau ujung interval. Jangan cuma cari f' = 0."),
    S("theorem", "Definisi, nilai ekstrem, titik kritis",
      r"""<ul class="lesson-list">
        <li>$f(c)$ <b>maksimum mutlak</b> pada $D$ jika $f(c) \ge f(x)$ untuk semua $x \in D$; <b>maksimum lokal</b> jika hanya berlaku di sekitar $c$.</li>
        <li><b>Teorema nilai ekstrem:</b> $f$ kontinu pada $[a, b]$ tertutup pasti mencapai maks dan min mutlak.</li>
        <li><b>Teorema Fermat:</b> jika $f$ punya ekstrem lokal di $c$ dan $f'(c)$ ada, maka $f'(c) = 0$.</li>
        <li><b>Titik kritis:</b> $c$ di domain dengan $f'(c) = 0$ atau $f'(c)$ tidak ada.</li>
      </ul>""",
      "Teorema Fermat cuma satu arah. f'(c) = 0 TIDAK menjamin ekstrem. Contohnya x³ di 0."),
    S("derivation", "Metode interval tertutup & uji turunan",
      r"""<p><b>Maks/min mutlak</b> pada $[a, b]$ (fungsi kontinu):</p>""" +
      steps(r"Cari semua titik kritis di $(a, b)$.",
            r"Hitung $f$ di titik kritis dan di ujung $a$, $b$.",
            r"Terbesar = maks mutlak, terkecil = min mutlak.") +
      r"""<p><b>Uji turunan pertama:</b> $f'$ berubah $+ \to -$ di $c$ → maks lokal; $- \to +$ → min lokal; tidak berubah → bukan ekstrem.</p>
      <p><b>Uji turunan kedua:</b> $f'(c) = 0$ dan $f''(c) < 0$ → maks lokal; $f''(c) > 0$ → min lokal; $f''(c) = 0$ → tidak bisa disimpulkan.</p>""",
      "Untuk interval tertutup, tabel nilai (titik kritis + ujung) adalah cara paling aman. Gak perlu uji turunan."),
    S("example", "Bedah soal: interval tertutup",
      r"""<p><b>Soal.</b> Maks dan min mutlak $f(x) = x^3 - 3x^2 - 9x + 5$ pada $[-2, 4]$.</p>""" +
      steps(r"$f'(x) = 3x^2 - 6x - 9 = 3(x - 3)(x + 1)$; titik kritis $x = -1$ dan $x = 3$ (keduanya di dalam interval).",
            r"$f(-2) = -8 - 12 + 18 + 5 = 3$; $\ f(-1) = -1 - 3 + 9 + 5 = 10$.",
            r"$f(3) = 27 - 27 - 27 + 5 = -22$; $\ f(4) = 64 - 48 - 36 + 5 = -15$.",
            r"Maks mutlak $10$ di $x = -1$; min mutlak $-22$ di $x = 3$."),
      "Geser interval [a, b] di grafik. Saat interval tidak lagi memuat x = 3, minimumnya pindah ke ujung.",
      [g("f(x) = x³ − 3x² − 9x + 5 dan f'(x)", [-3, 5], [-30, 20],
         [param("a", "Ujung a", -2.5, 0, 0.1, -2, "a"), param("b", "Ujung b", 1, 4.5, 0.1, 4, "b")],
         [{"type": "fn", "expr": "x*x*x - 3*x*x - 9*x + 5", "color": "blue", "label": "f"},
          {"type": "fn", "expr": "3*x*x - 6*x - 9", "color": "orange", "dash": True, "label": "f'"},
          {"type": "point", "x": "a", "y": "a*a*a - 3*a*a - 9*a + 5", "color": "green"},
          {"type": "point", "x": "b", "y": "b*b*b - 3*b*b - 9*b + 5", "color": "green"}],
         [readout("f(a)", "a*a*a - 3*a*a - 9*a + 5", 3), readout("f(b)", "b*b*b - 3*b*b - 9*b + 5", 3), readout("f(−1)", "10", 2), readout("f(3)", "-22", 2)],
         "Kurva oranye (f') memotong nol tepat di titik kritis x = −1 dan x = 3.")]),
    S("theorem", "Teorema Rolle & Nilai Rata-Rata",
      r"""<p><b>Teorema Nilai Rata-Rata (TNR):</b> jika $f$ kontinu pada $[a, b]$ dan terdiferensialkan pada $(a, b)$, ada $c \in (a, b)$ dengan
      $$f'(c) = \frac{f(b) - f(a)}{b - a}.$$</p>
      <p>Artinya: di suatu titik, kemiringan singgung = kemiringan sekan. Contoh nyata: kalau rata-rata kecepatanmu di tol 100 km/jam,
      pasti ada saat speedometer menunjuk tepat 100.</p>
      <p><b>Rolle</b> adalah kasus $f(a) = f(b)$: ada $c$ dengan $f'(c) = 0$.</p>""",
      "TNR dipakai bukan untuk menghitung c, tapi untuk MEMBUKTIKAN ketaksamaan. Lihat contoh berikut.",
      [g("TNR pada f(x) = x³, [0, 2]", [-0.5, 2.5], [-1, 9], [param("c", "Titik c", 0.05, 1.95, 0.01, 0.8, "c")],
         [{"type": "fn", "expr": "x*x*x", "color": "blue", "label": "f(x) = x³"},
          {"type": "fn", "expr": "4*x", "color": "gray", "dash": True, "label": "sekan, kemiringan 4"},
          {"type": "fn", "expr": "c*c*c + 3*c*c*(x - c)", "color": "red", "label": "singgung di c"},
          {"type": "point", "x": "c", "y": "c*c*c", "color": "red"}],
         [readout("f'(c) = 3c²", "3*c*c", 4), readout("Kemiringan sekan", "4", 2), readout("c yang dijamin TNR = 2/√3", "2/sqrt(3)", 4)],
         "Cari c saat garis merah sejajar garis abu-abu: c = 2/√3 ≈ 1,155.")]),
    S("example", "Bedah soal: pembuktian dengan TNR",
      r"""<p><b>Soal.</b> Buktikan $|\sin a - \sin b| \le |a - b|$ untuk semua $a, b$.</p>""" +
      steps(r"$f(x) = \sin x$ kontinu dan terdiferensialkan di mana-mana.",
            r"Menurut TNR ada $c$ di antara $a$ dan $b$: $\sin a - \sin b = \cos c\,(a - b)$.",
            r"Karena $|\cos c| \le 1$: $|\sin a - \sin b| = |\cos c|\,|a - b| \le |a - b|$. Terbukti."),
      "Pola bukti TNR: ubah selisih nilai fungsi jadi f'(c) × selisih input, lalu batasi |f'(c)|."),
    S("pitfall", "Jebakan ujian",
      r"""<ul class="lesson-list">
        <li>Lupa mengecek <b>ujung interval</b>, sehingga maks/min mutlak salah.</li>
        <li>Mengabaikan titik di mana $f'$ tidak ada: $f(x) = x^{2/3}$ punya minimum di $0$ walau $f'(0)$ tak terdefinisi.</li>
        <li>Menyimpulkan ekstrem dari $f'(c) = 0$ saja ($x^3$ di $0$ bukan ekstrem).</li>
        <li>Uji turunan kedua dengan $f''(c) = 0$ dianggap "bukan ekstrem". Seharusnya: tidak bisa disimpulkan, pakai uji turunan pertama.</li>
        <li>Memakai TNR pada fungsi yang tidak terdiferensialkan, misalnya $|x|$ di $[-1, 1]$.</li>
      </ul>""",
      "Titik kritis = f' = 0 ATAU f' tidak ada. Bagian kedua paling sering dilupakan di soal x^(2/3) atau |x − 2|."),
    S("checkpoint", "Mini checkpoint",
      qa(r"1. Titik kritis $f(x) = x^{2/3}(x - 5)$?", r"<p>$f'(x) = \tfrac{5}{3}x^{2/3} - \tfrac{10}{3}x^{-1/3} = \dfrac{5(x - 2)}{3x^{1/3}}$. Titik kritis: $x = 2$ ($f' = 0$) dan $x = 0$ ($f'$ tak ada).</p>") +
      qa(r"2. Cari $c$ yang dijamin TNR untuk $f(x) = x^2$ pada $[1, 5]$.", r"<p>$2c = \tfrac{25 - 1}{4} = 6 \Rightarrow c = 3$.</p>"),
      "Soal 1 menguji dua jenis titik kritis sekaligus. Jangan lewatkan x = 0."),
]

# ═══════════════════════════════════════════════════════════════════════════
# 8. Sketsa Kurva & Optimasi
# ═══════════════════════════════════════════════════════════════════════════
OPTIMASI = [
    S("intuition", "Turunan sebagai detektif bentuk kurva",
      r"""<p>$f'$ memberi tahu <b>naik atau turun</b>; $f''$ memberi tahu <b>cara menikung</b>: cekung ke atas (seperti mangkuk, $f'' > 0$) atau cekung ke bawah (seperti topi, $f'' < 0$).
      Dengan keduanya kamu bisa menggambar grafik akurat tanpa kalkulator, dan menemukan nilai terbaik di soal optimasi.</p>""",
      "f'' > 0 = tersenyum (mangkuk), f'' < 0 = cemberut (topi). Titik belok = tempat ekspresinya berganti."),
    S("theorem", "Kecekungan & daftar periksa sketsa",
      r"""<ul class="lesson-list">
        <li>$f'' > 0$ pada $I$ → cekung ke atas; $f'' < 0$ → cekung ke bawah.</li>
        <li><b>Titik belok</b>: titik di grafik tempat kecekungan berubah (cek tanda $f''$ berganti, bukan hanya $f'' = 0$).</li>
      </ul>
      <p><b>Daftar periksa sketsa kurva:</b></p>""" +
      steps(r"Domain, titik potong sumbu, simetri.",
            r"Asimtot tegak, datar, atau miring.",
            r"$f'$: interval naik/turun dan ekstrem lokal.",
            r"$f''$: interval cekung dan titik belok.",
            r"Gabungkan semuanya dalam satu tabel tanda, lalu gambar."),
      "Tabel tanda (garis bilangan untuk f' dan f'') adalah alat paling ampuh. Hampir semua dosen memintanya di soal sketsa."),
    S("example", "Bedah soal: sketsa f(x) = x e^{−x}",
      steps(r"Domain $\mathbb{R}$; $f(0) = 0$; $\displaystyle\lim_{x \to \infty} xe^{-x} = 0$ (asimtot datar $y = 0$ di kanan), $\displaystyle\lim_{x \to -\infty} = -\infty$.",
            r"$f'(x) = e^{-x}(1 - x)$: naik di $(-\infty, 1)$, turun di $(1, \infty)$; maks lokal $f(1) = \tfrac1e \approx 0.368$.",
            r"$f''(x) = e^{-x}(x - 2)$: cekung bawah di $(-\infty, 2)$, cekung atas di $(2, \infty)$; titik belok $(2, \tfrac{2}{e^2}) \approx (2, 0.271)$.",
            r"Gambar: naik dari $-\infty$, puncak di $(1, 0.368)$, menikung di $x = 2$, lalu meluruh ke $0$."),
      "Fungsi seperti x·e^(−x) muncul di model respons obat dan sinyal. Bentuknya 'naik cepat, turun pelan'.",
      [g("f = x·e^(−x), f' dan f''", [-1, 7], [-1, 1.2], [param("X", "Titik x", -0.5, 6.5, 0.05, 1, "x")],
         [{"type": "fn", "expr": "x*exp(-x)", "color": "blue", "label": "f"},
          {"type": "fn", "expr": "exp(-x)*(1 - x)", "color": "orange", "dash": True, "label": "f'"},
          {"type": "fn", "expr": "exp(-x)*(x - 2)", "color": "green", "dash": True, "label": "f''"},
          {"type": "point", "x": "X", "y": "X*exp(-X)", "color": "red"}],
         [readout("f'(x)", "exp(-X)*(1 - X)", 4), readout("f''(x)", "exp(-X)*(X - 2)", 4)],
         "Saat kurva oranye nol, f mencapai puncak. Saat kurva hijau nol, f berganti kecekungan.")]),
    S("theorem", "Kerangka optimasi",
      kerangka(r"Besaran yang tetap dan batasannya (keliling, volume, bahan). Gambar dan beri nama variabel.",
               r"Besaran yang dimaksimumkan atau diminimumkan (fungsi tujuan).",
               r"Tulis fungsi tujuan; gunakan <b>kendala</b> untuk menjadikannya fungsi <b>satu variabel</b>; tentukan <b>domain</b> yang masuk akal.",
               r"Cari titik kritis: turunan fungsi tujuan $= 0$ (atau tak ada).",
               r"Bandingkan dengan ujung domain atau pakai uji turunan; pastikan maks/min yang benar; jawab pertanyaan dengan satuan.") +
      note(r"Yang ditanya bisa berupa <b>ukuran</b> (nilai $x$) atau <b>nilai optimal</b> (luas/volume maksimum). Baca ulang pertanyaannya sebelum menulis jawaban akhir."),
      "Kendala gunanya mengurangi jumlah variabel. Fungsi tujuan harus tinggal SATU variabel sebelum diturunkan."),
    S("example", "Soal UTS: kotak tanpa tutup",
      r"""<p>Dari karton persegi $12 \times 12$ cm, keempat sudutnya dipotong persegi berukuran $x$, lalu sisinya dilipat jadi kotak tanpa tutup. Tentukan volume maksimum.</p>""" +
      kerangka(r"Karton $12 \times 12$ cm; potongan sudut $x \times x$.",
               r"Volume maksimum kotak.",
               r"Alas $(12 - 2x)^2$, tinggi $x$: $V(x) = x(12 - 2x)^2$, domain $0 \le x \le 6$.",
               r"$V'(x) = (12 - 2x)^2 - 4x(12 - 2x) = (12 - 2x)(12 - 6x) = 0 \Rightarrow x = 2$ atau $x = 6$.",
               r"$V(0) = V(6) = 0$, $V(2) = 2 \cdot 8^2 = 128$. Volume maksimum $128$ cm³ saat $x = 2$ cm."),
      "Ujung domain x = 0 dan x = 6 menghasilkan kotak 'gepeng' bervolume nol. Itu alasan cepat bahwa x = 2 adalah maksimum.",
      [g("V(x) = x(12 − 2x)²", [-0.5, 6.5], [-10, 150], [param("x0", "Potongan x (cm)", 0, 6, 0.05, 1, "x")],
         [{"type": "fn", "expr": "x*(12 - 2*x)*(12 - 2*x)", "color": "blue", "label": "V(x)"},
          {"type": "point", "x": "x0", "y": "x0*(12 - 2*x0)*(12 - 2*x0)", "color": "red"}],
         [readout("V(x) (cm³)", "x0*(12 - 2*x0)*(12 - 2*x0)", 4), readout("V'(x)", "(12 - 2*x0)*(12 - 6*x0)", 4)],
         "Puncak di x = 2 dengan V = 128.")]),
    S("example", "Soal UTS: kaleng hemat bahan",
      r"""<p>Kaleng silinder bertutup harus bervolume $1$ liter $= 1000$ cm³. Tentukan ukuran yang meminimumkan luas bahan.</p>""" +
      kerangka(r"$V = \pi r^2 h = 1000$ cm³.",
               r"$r$ dan $h$ yang meminimumkan luas permukaan $A$.",
               r"$A = 2\pi r^2 + 2\pi r h$. Dari kendala, $h = \tfrac{1000}{\pi r^2}$, jadi $A(r) = 2\pi r^2 + \tfrac{2000}{r}$, $r > 0$.",
               r"$A'(r) = 4\pi r - \tfrac{2000}{r^2} = 0 \Rightarrow r^3 = \tfrac{500}{\pi} \Rightarrow r = \sqrt[3]{500/\pi} \approx 5.42$ cm.",
               r"$A''(r) = 4\pi + \tfrac{4000}{r^3} > 0$, jadi minimum. $h = \tfrac{1000}{\pi r^2} = 2r \approx 10.84$ cm.") +
      note(r"Hasil cantik: kaleng paling hemat punya tinggi = diameter. Kaleng di supermarket sering lebih tinggi karena faktor lain (label, pegangan)."),
      "Domain r > 0 terbuka, jadi tidak ada ujung yang bisa dicek. Uji turunan kedua yang menjamin minimumnya."),
    S("example", "Soal: titik terdekat pada kurva",
      r"""<p>Titik pada $y = \sqrt{x}$ yang paling dekat ke $(3, 0)$?</p>""" +
      kerangka(r"Titik $(x, \sqrt{x})$ pada kurva, titik tetap $(3, 0)$.",
               r"$x$ yang meminimumkan jarak.",
               r"Minimumkan kuadrat jarak (lebih mudah, minimumnya di titik yang sama): $D(x) = (x - 3)^2 + x$, $x \ge 0$.",
               r"$D'(x) = 2(x - 3) + 1 = 0 \Rightarrow x = \tfrac52$.",
               r"$D(0) = 9$, $D(\tfrac52) = \tfrac14 + \tfrac52 = \tfrac{11}{4}$. Titik terdekat $\left(\tfrac52, \sqrt{\tfrac52}\right)$, jarak $\tfrac{\sqrt{11}}{2} \approx 1.66$."),
      "Trik kuadrat jarak: hilangkan akar karena √ naik monoton. Minimum D² sama letaknya dengan minimum D."),
    S("pitfall", "Jebakan ujian",
      r"""<ul class="lesson-list">
        <li>Menurunkan fungsi tujuan yang masih dua variabel. Pakai kendala dulu.</li>
        <li>Lupa domain fisik, misalnya panjang negatif atau melebihi bahan.</li>
        <li>Tidak memverifikasi bahwa titik kritis memang maks (bukan min) atau sebaliknya.</li>
        <li>Menjawab $x = 2$ padahal yang ditanya volume maksimum.</li>
        <li>Titik belok: $f''(c) = 0$ belum cukup; $f(x) = x^4$ punya $f''(0) = 0$ tapi tidak berbelok.</li>
      </ul>""",
      "Kalimat penutup jawaban optimasi: 'nilai maksimum ... tercapai saat ...'. Dua informasi, dua-duanya harus ada."),
    S("checkpoint", "Mini checkpoint",
      qa(r"1. Pagar $200$ m membatasi lahan persegi panjang di tepi sungai (sisi sungai tidak dipagari). Luas maksimum?",
         r"<p>$2x + y = 200$, $A = x(200 - 2x)$, $A' = 200 - 4x = 0 \Rightarrow x = 50$, $y = 100$, $A = 5000$ m².</p>") +
      qa(r"2. Titik belok $f(x) = x^3 - 6x^2 + 1$?", r"<p>$f'' = 6x - 12$, berganti tanda di $x = 2$: titik belok $(2, -15)$.</p>"),
      "Soal 1 klasik: sisi sungai tidak butuh pagar, jadi kendalanya 2x + y, bukan 2x + 2y."),
]

# ═══════════════════════════════════════════════════════════════════════════
# 9. Integral Tak Tentu & Jumlah Riemann
# ═══════════════════════════════════════════════════════════════════════════
RIEMANN = [
    S("intuition", "Membalik turunan & menjumlah potongan tipis",
      r"""<p>Integral punya dua wajah. <b>Antiturunan:</b> diketahui kecepatan, cari posisi; diketahui laju pertumbuhan, cari populasi.
      <b>Integral tentu:</b> luas di bawah kurva, didekati dengan menjumlahkan banyak persegi panjang tipis.</p>
      <p>Teorema Dasar Kalkulus (topik berikutnya) membuktikan bahwa kedua wajah ini sebenarnya sama.</p>""",
      "Antiturunan menjawab 'fungsi apa yang turunannya ini?'. Jawabannya selalu satu keluarga, dibedakan oleh +C."),
    S("theorem", "Antiturunan dasar",
      r"""<p>$$\int x^n\,dx = \frac{x^{n+1}}{n + 1} + C\ (n \ne -1), \qquad \int \frac{1}{x}\,dx = \ln|x| + C, \qquad \int e^x\,dx = e^x + C$$</p>
      <p>$$\int \sin x\,dx = -\cos x + C, \qquad \int \cos x\,dx = \sin x + C, \qquad \int \sec^2 x\,dx = \tan x + C, \qquad \int \frac{dx}{1 + x^2} = \arctan x + C$$</p>
      <p>Linear: $\int (af + bg) = a\int f + b\int g$. <b>Masalah nilai awal</b>: konstanta $C$ ditentukan dari satu titik yang diketahui.</p>""",
      "Cek antiturunan dengan menurunkan jawabanmu. Kalau kembali ke integran, jawabanmu benar.",
      [g("Keluarga antiturunan dari 2x: y = x² + C", [-3, 3], [-4, 8], [param("C", "Konstanta C", -3, 4, 0.5, 1, "C")],
         [{"type": "fn", "expr": "x*x - 2", "color": "gray"}, {"type": "fn", "expr": "x*x", "color": "gray"}, {"type": "fn", "expr": "x*x + 2", "color": "gray"},
          {"type": "fn", "expr": "x*x + C", "color": "blue", "label": "x² + C"},
          {"type": "fn", "expr": "C + 2*(x - 1) + 1", "color": "red", "dash": True, "label": "singgung di x = 1"}],
         [readout("Kemiringan di x = 1", "2", 2)],
         "Semua anggota keluarga punya kemiringan sama di x yang sama. C hanya menggeser naik-turun.")]),
    S("example", "Bedah soal: antiturunan & nilai awal",
      r"""<p><b>Soal 1.</b> $\displaystyle\int \left(3x^2 - \frac{4}{x} + 2\sqrt{x} + e^x\right)dx = x^3 - 4\ln|x| + \tfrac43 x^{3/2} + e^x + C$.</p>
      <p><b>Soal 2.</b> Bola dilempar ke atas: $a(t) = -9.8$ m/s², $v(0) = 20$ m/s, $s(0) = 0$. Kapan mencapai puncak, dan seberapa tinggi?</p>""" +
      steps(r"$v(t) = \int -9.8\,dt = -9.8t + C_1$; $v(0) = 20 \Rightarrow v(t) = 20 - 9.8t$.",
            r"$s(t) = \int v\,dt = 20t - 4.9t^2 + C_2$; $s(0) = 0 \Rightarrow C_2 = 0$.",
            r"Puncak saat $v = 0$: $t = \tfrac{20}{9.8} \approx 2.04$ s.",
            r"Tinggi $s(2.04) \approx 20(2.04) - 4.9(2.04)^2 \approx 20.4$ m."),
      "Tiap kali mengintegralkan muncul konstanta baru. Dua integrasi berarti butuh dua kondisi awal."),
    S("theorem", "Jumlah Riemann & integral tentu",
      r"""<p>Bagi $[a, b]$ menjadi $n$ bagian selebar $\Delta x = \tfrac{b - a}{n}$, pilih titik sampel $x_i^*$ di tiap bagian:
      $$\int_a^b f(x)\,dx = \lim_{n \to \infty} \sum_{i=1}^{n} f(x_i^*)\,\Delta x.$$</p>
      <p>Untuk $f \ge 0$ ini luas di bawah kurva; secara umum <b>luas bertanda</b> (bagian di bawah sumbu $x$ dihitung negatif).</p>
      <p>Sifat: $\int_a^b c\,dx = c(b - a)$, $\ \int_a^a f = 0$, $\ \int_b^a f = -\int_a^b f$, $\ \int_a^b f + \int_b^c f = \int_a^c f$.</p>""",
      "Geser mode sampel (kiri, kanan, tengah, trapesium) dan n di grafik. Titik tengah biasanya paling akurat untuk n kecil.",
      [g("Jumlah Riemann untuk x² pada [0, 2]", [-0.2, 2.3], [-0.3, 4.5],
         [param("N", "Banyak potongan n", 1, 40, 1, 4, "n"), param("M", "Mode (0 kiri, 1 kanan, 2 tengah, 3 trapesium)", 0, 3, 1, 1, "m")],
         [{"type": "riemann", "id": "R", "expr": "x*x", "from": 0, "to": 2, "n": "N", "mode": "M", "color": "amber"},
          {"type": "fn", "expr": "x*x", "color": "blue", "label": "x²"}],
         [readout("Jumlah Riemann", "R", 6), readout("Nilai eksak 8/3", "8/3", 6), readout("Galat", "R - 8/3", 6)],
         "Galat mengecil saat n naik. Sampel kiri meremehkan, kanan melebihkan (karena x² naik).")]),
    S("derivation", "Menghitung integral tentu dengan definisi",
      r"""<p><b>Hitung</b> $\displaystyle\int_0^2 x^2\,dx$ dengan jumlah Riemann kanan.</p>""" +
      steps(r"$\Delta x = \tfrac{2}{n}$, titik kanan $x_i = \tfrac{2i}{n}$.",
            r"$\displaystyle\sum_{i=1}^{n} \left(\frac{2i}{n}\right)^2 \frac{2}{n} = \frac{8}{n^3}\sum_{i=1}^{n} i^2 = \frac{8}{n^3}\cdot\frac{n(n + 1)(2n + 1)}{6}$.",
            r"$= \dfrac{4}{3}\left(1 + \tfrac1n\right)\left(2 + \tfrac1n\right)$.",
            r"$n \to \infty$: $\dfrac43 \cdot 1 \cdot 2 = \dfrac83$.") +
      note(r"Rumus $\sum i^2$ dari Level 1 (Barisan & Notasi Sigma) dipakai persis di sini."),
      "Cara definisi ini panjang, tapi sering keluar di UTS sebagai 'hitung dengan limit jumlah Riemann'. Kuasai polanya."),
    S("pitfall", "Jebakan ujian",
      r"""<ul class="lesson-list">
        <li>Lupa $+C$ pada integral tak tentu.</li>
        <li>$\int x^{-1}dx = \dfrac{x^0}{0}$: tidak terdefinisi. Yang benar $\ln|x| + C$, dengan nilai mutlak.</li>
        <li>$\int f g \ne \left(\int f\right)\left(\int g\right)$ dan $\int \dfrac{f}{g} \ne \dfrac{\int f}{\int g}$.</li>
        <li>Menganggap integral tentu selalu luas positif. Kalau $f < 0$, integralnya negatif.</li>
        <li>$\int \sin x\,dx = \cos x$: tanda salah. Turunkan $-\cos x$ untuk mengecek.</li>
      </ul>""",
      "Tanda di ∫ sin x dan ∫ cos x sering tertukar. Selalu cek dengan menurunkan balik."),
    S("checkpoint", "Mini checkpoint",
      qa(r"1. Cari $f$ jika $f'(x) = 6x - 2$ dan $f(1) = 5$.", r"<p>$f(x) = 3x^2 - 2x + C$; $3 - 2 + C = 5 \Rightarrow C = 4$. $f(x) = 3x^2 - 2x + 4$.</p>") +
      qa(r"2. Tanpa menghitung: tanda $\displaystyle\int_{\pi}^{2\pi}\sin x\,dx$?", r"<p>Negatif, karena $\sin x \le 0$ di $[\pi, 2\pi]$. Nilainya $-2$.</p>"),
      "Soal 2 melatih membaca integral sebagai luas bertanda, tanpa menghitung apa pun."),
]

# ═══════════════════════════════════════════════════════════════════════════
# 10. Teorema Dasar Kalkulus
# ═══════════════════════════════════════════════════════════════════════════
TDK = [
    S("intuition", "Fungsi akumulasi",
      r"""<p>Bayangkan keran yang mengalirkan air dengan laju $f(t)$ liter/menit. Jumlah air yang terkumpul sejak menit $0$ sampai menit $x$ adalah
      $$A(x) = \int_0^x f(t)\,dt.$$
      Seberapa cepat $A$ bertambah saat menit $x$? Tentu saja sebesar laju keran saat itu, yaitu $f(x)$. Itulah inti Teorema Dasar Kalkulus:
      <b>turunan dari akumulasi = laju</b>.</p>""",
      "TDK adalah jembatan Calculus Bridge yang sebenarnya: turunan dan integral saling membatalkan.",
      [g("Fungsi akumulasi A(x) = ∫₀ˣ (1 + sin t) dt", [-0.5, 8], [-0.5, 9], [param("X", "Batas atas x", 0, 7.5, 0.05, 3, "x")],
         [{"type": "fill", "upper": "1 + sin(x)", "from": 0, "to": "X", "color": "blue"},
          {"type": "fn", "expr": "1 + sin(x)", "color": "blue", "label": "f(t) = 1 + sin t"},
          {"type": "fn", "expr": "x - cos(x) + 1", "color": "orange", "label": "A(x)"},
          {"type": "point", "x": "X", "y": "X - cos(X) + 1", "color": "orange"}],
         [readout("A(x) = luas biru", "X - cos(X) + 1", 4), readout("f(x) = laju bertambahnya A", "1 + sin(X)", 4)],
         "Saat f besar, kurva oranye naik curam; saat f kecil, naiknya landai.")]),
    S("theorem", "TDK bagian I",
      r"""<p>Jika $f$ kontinu pada $[a, b]$, maka $A(x) = \displaystyle\int_a^x f(t)\,dt$ terdiferensialkan dan
      $$\frac{d}{dx}\int_a^x f(t)\,dt = f(x).$$</p>
      <p>Dengan aturan rantai: $\displaystyle\frac{d}{dx}\int_a^{g(x)} f(t)\,dt = f(g(x))\,g'(x)$, dan untuk dua batas variabel
      $\displaystyle\frac{d}{dx}\int_{h(x)}^{g(x)} f(t)\,dt = f(g(x))g'(x) - f(h(x))h'(x)$.</p>""",
      "Pola TDK I: masukkan batas atas ke integran, lalu kalikan dengan turunan batas atas. Gak perlu menghitung integralnya."),
    S("theorem", "TDK bagian II (evaluasi)",
      r"""<p>Jika $f$ kontinu pada $[a, b]$ dan $F$ sembarang antiturunan $f$ ($F' = f$), maka
      $$\int_a^b f(x)\,dx = F(b) - F(a) = \Big[F(x)\Big]_a^b.$$</p>
      <p>Konstanta $C$ tidak perlu ditulis karena saling menghapus. Hasil ini menggantikan perhitungan limit jumlah Riemann yang panjang:
      $\int_0^2 x^2\,dx = \left[\tfrac{x^3}{3}\right]_0^2 = \tfrac83$, cocok dengan topik sebelumnya.</p>""",
      "Bandingkan: topik sebelumnya butuh enam baris untuk 8/3, sekarang cuma satu baris. Itulah kekuatan TDK."),
    S("example", "Bedah soal: TDK I dengan aturan rantai",
      r"""<p><b>Soal 1.</b> $\dfrac{d}{dx}\displaystyle\int_1^{x^2}\sin(t^3)\,dt$.</p>""" +
      steps(r"Batas atas $g(x) = x^2$, $g'(x) = 2x$.",
            r"Hasil: $\sin\!\left((x^2)^3\right)\cdot 2x = 2x\sin(x^6)$.") +
      r"""<p><b>Soal 2.</b> $\dfrac{d}{dx}\displaystyle\int_x^{3}\sqrt{1 + t^4}\,dt$.</p>""" +
      steps(r"Balik batas: $= -\displaystyle\int_3^{x}\sqrt{1 + t^4}\,dt$.",
            r"Hasil: $-\sqrt{1 + x^4}$."),
      "Batas variabel di BAWAH? Balik dulu batasnya dan beri tanda minus, baru pakai TDK I."),
    S("example", "Bedah soal: TDK II",
      r"""<p><b>Soal 1.</b> $\displaystyle\int_1^4 \left(\sqrt{x} - \frac{1}{x^2}\right)dx$.</p>""" +
      steps(r"Antiturunan: $F(x) = \tfrac23 x^{3/2} + \dfrac1x$.",
            r"$F(4) = \tfrac{16}{3} + \tfrac14$, $\ F(1) = \tfrac23 + 1$.",
            r"$F(4) - F(1) = \tfrac{14}{3} - \tfrac34 = \tfrac{47}{12}$.") +
      r"""<p><b>Soal 2.</b> $\displaystyle\int_0^{\pi}\sin x\,dx = \Big[-\cos x\Big]_0^{\pi} = 1 - (-1) = 2$.</p>""",
      "Tulis F(b) dan F(a) dalam kurung terpisah. Kesalahan tanda paling sering muncul saat mengurangi F(a)."),
    S("example", "Bedah soal: perpindahan vs jarak tempuh",
      r"""<p>Partikel bergerak dengan $v(t) = t^2 - 4t + 3$ m/s pada $0 \le t \le 4$. Hitung perpindahan dan jarak total.</p>""" +
      steps(r"Perpindahan $= \displaystyle\int_0^4 v\,dt = \left[\tfrac{t^3}{3} - 2t^2 + 3t\right]_0^4 = \tfrac{64}{3} - 32 + 12 = \tfrac43$ m.",
            r"$v = (t - 1)(t - 3)$: positif di $[0, 1)$, negatif di $(1, 3)$, positif di $(3, 4]$.",
            r"$\int_0^1 v = \tfrac43$, $\ \int_1^3 v = -\tfrac43$, $\ \int_3^4 v = \tfrac43$.",
            r"Jarak total $= \tfrac43 + \tfrac43 + \tfrac43 = 4$ m.") +
      r"""<p><b>Nilai rata-rata</b> fungsi pada $[a, b]$: $f_{\text{avg}} = \dfrac{1}{b - a}\displaystyle\int_a^b f(x)\,dx$. Contoh: rata-rata $x^2$ pada $[0, 3]$ adalah $\tfrac13 \cdot 9 = 3$.</p>""",
      "Jarak tempuh = ∫|v| dt. Pecah di titik saat v = 0, lalu jumlahkan nilai mutlak tiap bagian."),
    S("pitfall", "Jebakan ujian",
      r"""<ul class="lesson-list">
        <li>Memakai TDK II pada fungsi yang tidak kontinu: $\int_{-1}^{1}\tfrac{1}{x^2}dx \ne \left[-\tfrac1x\right]_{-1}^{1} = -2$. Integran positif tidak mungkin menghasilkan nilai negatif; integral ini divergen (Level 3: integral tak wajar).</li>
        <li>Lupa faktor turunan batas di TDK I.</li>
        <li>Menyamakan perpindahan dengan jarak tempuh.</li>
        <li>Menulis $\frac{d}{dx}\int_a^x f(t)dt = f(x) - f(a)$. Yang benar cukup $f(x)$.</li>
      </ul>""",
      "Contoh 1/x² di [−1, 1] itu peringatan keras: selalu cek kontinuitas integran di seluruh interval."),
    S("checkpoint", "Mini checkpoint",
      qa(r"1. $\dfrac{d}{dx}\displaystyle\int_{0}^{\sin x} e^{t^2}\,dt$", r"<p>$e^{\sin^2 x}\cos x$.</p>") +
      qa(r"2. $\displaystyle\int_0^{1}(4x^3 + 2x)\,dx$", r"<p>$\left[x^4 + x^2\right]_0^1 = 2$.</p>"),
      "Soal 1: batas atasnya sin x, jadi jangan lupa faktor cos x."),
]

# ═══════════════════════════════════════════════════════════════════════════
# 11. Teknik Substitusi
# ═══════════════════════════════════════════════════════════════════════════
SUBSTITUSI = [
    S("intuition", "Aturan rantai dibalik",
      r"""<p>Aturan rantai: $\tfrac{d}{dx}\sin(x^2) = \cos(x^2)\cdot 2x$. Jadi kalau kamu melihat $\int \cos(x^2)\,2x\,dx$, jawabannya pasti $\sin(x^2) + C$.</p>
      <p>Substitusi adalah cara sistematis mengenali pola "<b>fungsi dalam, dikalikan turunannya</b>".</p>""",
      "Cari 'fungsi di dalam' yang turunannya (kurang lebih konstanta) juga muncul di integran. Itu calon u."),
    S("theorem", "Aturan substitusi",
      r"""<p>Jika $u = g(x)$ maka $du = g'(x)\,dx$ dan
      $$\int f(g(x))\,g'(x)\,dx = \int f(u)\,du.$$</p>
      <p><b>Integral tentu:</b> ubah juga batasnya, $\displaystyle\int_a^b f(g(x))g'(x)\,dx = \int_{g(a)}^{g(b)} f(u)\,du$, tanpa perlu kembali ke $x$.</p>
      <p><b>Simetri:</b> pada $[-a, a]$, fungsi genap: $\int_{-a}^a f = 2\int_0^a f$; fungsi ganjil: $\int_{-a}^a f = 0$.</p>""",
      "Untuk integral tentu, mengganti batas ke u menghemat langkah dan menghindari salah substitusi balik."),
    S("derivation", "Langkah-langkah substitusi",
      steps(r"Pilih $u$: biasanya isi akar, pangkat, eksponen, atau penyebut.",
            r"Hitung $du = u'(x)\,dx$, lalu nyatakan $dx$ atau bagian integran dalam $du$.",
            r"Tulis ulang <b>seluruh</b> integran dalam $u$; tidak boleh ada $x$ yang tersisa.",
            r"Integralkan terhadap $u$.",
            r"Kembali ke $x$ (integral tak tentu) atau pakai batas baru (integral tentu).") +
      note(r"Kalau setelah langkah 3 masih ada $x$, kemungkinan pilihan $u$ kurang tepat, atau $x$ itu perlu dinyatakan lewat $u$ (misal $x = u - 1$)."),
      "Faktor konstanta boleh 'diakali': kalau du = 2x dx tapi integran cuma punya x dx, tulis x dx = du/2."),
    S("example", "Bedah soal: integral tak tentu",
      r"""<p><b>Soal 1.</b> $\displaystyle\int x\sqrt{x^2 + 1}\,dx$.</p>""" +
      steps(r"$u = x^2 + 1$, $du = 2x\,dx \Rightarrow x\,dx = \tfrac{du}{2}$.",
            r"$\displaystyle\int \sqrt{u}\,\frac{du}{2} = \frac12\cdot\frac{2}{3}u^{3/2} + C = \frac13(x^2 + 1)^{3/2} + C$.") +
      r"""<p><b>Soal 2.</b> $\displaystyle\int \tan x\,dx = \int\frac{\sin x}{\cos x}dx$.</p>""" +
      steps(r"$u = \cos x$, $du = -\sin x\,dx$.",
            r"$\displaystyle\int -\frac{du}{u} = -\ln|u| + C = -\ln|\cos x| + C = \ln|\sec x| + C$.") +
      r"""<p><b>Soal 3.</b> $\displaystyle\int x\sqrt{x + 1}\,dx$ (sisa $x$ dinyatakan lewat $u$).</p>""" +
      steps(r"$u = x + 1$, $du = dx$, dan $x = u - 1$.",
            r"$\displaystyle\int (u - 1)u^{1/2}du = \int (u^{3/2} - u^{1/2})du = \tfrac25 u^{5/2} - \tfrac23 u^{3/2} + C$.",
            r"$= \tfrac25(x + 1)^{5/2} - \tfrac23(x + 1)^{3/2} + C$."),
      "Soal 3 menunjukkan trik penting: x yang tersisa bisa ditulis ulang sebagai u − 1."),
    S("example", "Bedah soal: integral tentu & luas antar kurva",
      r"""<p><b>Soal 1.</b> $\displaystyle\int_0^1 x e^{x^2}dx$.</p>""" +
      steps(r"$u = x^2$, $du = 2x\,dx$; batas: $x = 0 \to u = 0$, $x = 1 \to u = 1$.",
            r"$\displaystyle\frac12\int_0^1 e^u\,du = \frac12(e - 1) \approx 0.859$.") +
      r"""<p><b>Soal 2 (luas).</b> Luas daerah antara $y = x$ dan $y = x^2$.</p>""" +
      steps(r"Titik potong: $x = x^2 \Rightarrow x = 0, 1$. Pada $[0, 1]$, $x \ge x^2$ (kurva atas $y = x$).",
            r"$L = \displaystyle\int_0^1 (x - x^2)\,dx = \left[\tfrac{x^2}{2} - \tfrac{x^3}{3}\right]_0^1 = \tfrac16$."),
      "Luas antar kurva = ∫(atas − bawah). Tentukan dulu mana kurva atas di interval itu.",
      [g("Luas antara y = x dan y = x²", [-0.3, 1.5], [-0.3, 1.5], [],
         [{"type": "fill", "upper": "x", "lower": "x*x", "from": 0, "to": 1, "color": "green"},
          {"type": "fn", "expr": "x", "color": "blue", "label": "y = x"},
          {"type": "fn", "expr": "x*x", "color": "orange", "label": "y = x²"}],
         [readout("Luas", "1/6", 5)],
         "Daerah hijau = ∫₀¹ (x − x²) dx = 1/6.")]),
    S("pitfall", "Jebakan ujian",
      r"""<ul class="lesson-list">
        <li>Masih ada $x$ setelah substitusi, misalnya $\int x^2\sqrt{x^2 + 1}\,dx$ dengan $u = x^2 + 1$ meninggalkan $x$ yang tidak bisa dibuang.</li>
        <li>Lupa mengganti batas pada integral tentu, atau mengganti batas <i>dan</i> substitusi balik sekaligus.</li>
        <li>Lupa faktor konstanta dari $du$, misalnya $\tfrac12$.</li>
        <li>Mengira semua integral bisa disubstitusi: $\int e^{x^2}dx$ tidak punya antiturunan elementer (butuh fungsi error, jalur FMIPA).</li>
        <li>$\int \tfrac{1}{u}du = \ln u$ tanpa nilai mutlak.</li>
      </ul>""",
      "Cek akhir: turunkan jawabanmu. Kalau kembali ke integran asli (termasuk faktor konstantanya), substitusimu benar."),
    S("checkpoint", "Mini checkpoint",
      qa(r"1. $\displaystyle\int \frac{\ln x}{x}\,dx$", r"<p>$u = \ln x$, $du = \tfrac{dx}{x}$: $\displaystyle\int u\,du = \tfrac12(\ln x)^2 + C$.</p>") +
      qa(r"2. $\displaystyle\int_0^{\pi/2}\sin^3 x\cos x\,dx$", r"<p>$u = \sin x$, batas $0 \to 1$: $\displaystyle\int_0^1 u^3du = \tfrac14$.</p>") +
      qa(r"3. $\displaystyle\int_{-2}^{2} x^3\cos x\,dx$", r"<p>Integran ganjil pada interval simetris, jadi hasilnya $0$.</p>"),
      "Soal 3 bisa dijawab dalam lima detik kalau kamu ingat sifat fungsi ganjil. Kenali sebelum menghitung."),
]

SLIDES = {
    "kd-tur-rantai": RANTAI,
    "kd-apl-laju": LAJU,
    "kd-apl-ekstrem": EKSTREM,
    "kd-apl-optimasi": OPTIMASI,
    "kd-int-riemann": RIEMANN,
    "kd-int-tdk": TDK,
    "kd-int-substitusi": SUBSTITUSI,
}
