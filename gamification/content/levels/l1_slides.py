r"""
Kurikulum v2 — Batch 1: slide Level 1 (PreCalculus & Fondasi).

SLIDES[slug] = daftar slide (LessonSlide) untuk topik itu; NEW_TOPICS = topik baru (materi saja,
latihan menyusul). Alur tiap topik: intuisi → definisi formal → eksplorasi grafik → bedah soal
bertahap → jebakan ujian → mini checkpoint. Semua rumus LaTeX ($…$ / $$…$$, dirender KaTeX).

Rujukan: Purcell Kalkulus Jil. 1 Bab 0–1; Stewart 9e Bab 1 & Lamp. A–D; OpenStax Calculus Vol 1 Bab 1.
"""

from ..helpers import param, readout


def S(kind, title, body, tip, graphs=None):
    return {"kind": kind, "title": title, "body_html": body, "tip": tip, "graphs": graphs or []}


def g(title, x, y, params, elements, readouts=None, caption=None):
    spec = {"type": "2d", "title": title, "x": x, "y": y, "params": params, "elements": elements}
    if readouts:
        spec["readouts"] = readouts
    if caption:
        spec["caption"] = caption
    return spec


def steps(*items):
    return '<ol class="steps-list">' + "".join(f"<li><b>Langkah {i}.</b> {s}</li>" for i, s in enumerate(items, 1)) + "</ol>"


def qa(question, answer):
    return f'<div class="lesson-check"><p>{question}</p><details><summary>Lihat jawaban</summary>{answer}</details></div>'


def note(text):
    return f'<p class="lesson-note">{text}</p>'


# ═══════════════════════════════════════════════════════════════════════════
# 1. Sistem Bilangan Real & Interval
# ═══════════════════════════════════════════════════════════════════════════
BILANGAN_REAL = [
    S("intuition", "Garis bilangan: tempat semua angka tinggal",
      r"""<p>Semua besaran yang kamu ukur — waktu render, suhu reaktor, galat model — hidup di <b>garis bilangan real</b> $\mathbb{R}$.
      Tiap titik di garis itu satu bilangan, dan tidak ada "lubang": di antara dua bilangan selalu ada bilangan lain.</p>
      <p>Kenapa ini penting buat kalkulus? Limit, turunan, dan integral semuanya bicara soal "mendekat sedekat mungkin".
      Itu cuma masuk akal kalau garisnya utuh tanpa celah.</p>
      <p>Di komputer, float hanya <i>meniru</i> $\mathbb{R}$ dengan jumlah titik terbatas. Itulah kenapa $0.1 + 0.2 \ne 0.3$ di Python.</p>""",
      "Bayangkan garis bilangan sebagai penggaris tanpa batas yang bisa di-zoom selamanya. Kalkulus hidup di zoom-zoom itu."),
    S("theorem", "Hirarki himpunan bilangan",
      r"""<p>$$\mathbb{N} \subset \mathbb{Z} \subset \mathbb{Q} \subset \mathbb{R}$$</p>
      <ul class="lesson-list">
        <li>$\mathbb{N} = \{1, 2, 3, \dots\}$ bilangan asli; $\mathbb{Z}$ bilangan bulat (tambah $0$ dan negatif).</li>
        <li>$\mathbb{Q} = \left\{\tfrac{p}{q} : p, q \in \mathbb{Z},\ q \ne 0\right\}$: desimalnya berhenti atau berulang, mis. $\tfrac{1}{7} = 0.\overline{142857}$.</li>
        <li>Irasional $= \mathbb{R} \setminus \mathbb{Q}$: desimal tak berhenti dan tak berulang, mis. $\sqrt{2}$, $\pi$, $e$.</li>
      </ul>
      <p><b>Sifat kelengkapan:</b> setiap himpunan tak kosong yang terbatas di atas punya batas atas terkecil (supremum).
      Sifat inilah yang membedakan $\mathbb{R}$ dari $\mathbb{Q}$, dan jadi fondasi teorema nilai antara nanti.</p>""",
      "Cara cepat cek rasional: desimalnya berhenti atau berulang. Kalau tidak dua-duanya, irasional."),
    S("theorem", "Notasi interval",
      r"""<p>Interval = himpunan semua bilangan real di antara dua ujung.</p>
      <div class="table-scroll"><table class="lesson-table"><thead><tr><th>Notasi</th><th>Himpunan</th><th>Ujung</th></tr></thead><tbody>
        <tr><td>$[a, b]$</td><td>$\{x : a \le x \le b\}$</td><td>tertutup: dua ujung ikut</td></tr>
        <tr><td>$(a, b)$</td><td>$\{x : a < x < b\}$</td><td>terbuka: dua ujung tidak ikut</td></tr>
        <tr><td>$[a, b)$</td><td>$\{x : a \le x < b\}$</td><td>setengah terbuka</td></tr>
        <tr><td>$(a, \infty)$</td><td>$\{x : x > a\}$</td><td>$\infty$ selalu pakai kurung biasa</td></tr>
      </tbody></table></div>
      <p>Operasi: irisan $A \cap B$ (anggota keduanya) dan gabungan $A \cup B$ (anggota salah satu).</p>""",
      "Kurung siku = ujungnya ikut (titik penuh), kurung biasa = tidak ikut (titik kosong). ∞ bukan bilangan, jadi gak pernah dikurung siku.",
      [g("Irisan A = [a, 2] dan B = (−1, b]", [-6, 6], [-1.5, 2.5],
         [param("a", "Ujung kiri A", -5, 2, 0.5, -3, "a"), param("b", "Ujung kanan B", -1, 5, 0.5, 4, "b")],
         [{"type": "segment", "x1": "a", "y1": 1.5, "x2": 2, "y2": 1.5, "color": "blue", "width": 6},
          {"type": "segment", "x1": -1, "y1": 0.8, "x2": "b", "y2": 0.8, "color": "orange", "width": 6},
          {"type": "segment", "x1": "max(a,-1)", "y1": 0, "x2": "min(2,b)", "y2": 0, "color": "green", "width": 8},
          {"type": "text", "x": -5.5, "y": 1.5, "text": "A"}, {"type": "text", "x": -5.5, "y": 0.8, "text": "B"},
          {"type": "text", "x": -5.5, "y": 0, "text": "A∩B"}],
         [readout("Ujung kiri irisan", "max(a,-1)", 2), readout("Ujung kanan irisan", "min(2,b)", 2)],
         "Irisan mulai dari ujung kiri terbesar dan berhenti di ujung kanan terkecil.")]),
    S("theorem", "Eksponen & bentuk akar",
      r"""<p>Untuk $a, b > 0$ dan $m, n$ real:</p>
      <p>$$a^m a^n = a^{m+n}, \qquad \frac{a^m}{a^n} = a^{m-n}, \qquad (a^m)^n = a^{mn}, \qquad (ab)^n = a^n b^n$$</p>
      <p>$$a^{-n} = \frac{1}{a^n}, \qquad a^{p/q} = \sqrt[q]{a^p}, \qquad a^0 = 1$$</p>
      <p>Merasionalkan penyebut: kalikan dengan sekawan, $\dfrac{1}{\sqrt{a} - \sqrt{b}} = \dfrac{\sqrt{a} + \sqrt{b}}{a - b}$.
      Trik ini nanti dipakai terus untuk limit bentuk $\tfrac{0}{0}$.</p>""",
      "Hafalkan a^(p/q) = akar q dari a^p. Banyak soal turunan jadi gampang kalau akar diubah ke pangkat pecahan dulu."),
    S("example", "Bedah soal: interval dan bentuk akar",
      r"""<p><b>Soal 1.</b> Tentukan $[-3, 2) \cap (-1, 5]$ dan $[-3, 2) \cup (-1, 5]$.</p>""" +
      steps(r"Ujung kiri irisan $= \max(-3, -1) = -1$, dan $-1$ tidak termasuk di $(-1, 5]$, jadi pakai kurung biasa.",
            r"Ujung kanan irisan $= \min(2, 5) = 2$, dan $2$ tidak termasuk di $[-3, 2)$, jadi kurung biasa.",
            r"Irisan $= (-1, 2)$. Gabungan $= [-3, 5]$ (dua interval saling tumpang tindih).") +
      r"""<p><b>Soal 2.</b> Sederhanakan $\dfrac{8^{2/3} \cdot 4^{-1/2}}{2^{-3}}$.</p>""" +
      steps(r"Ubah ke basis 2: $8^{2/3} = (2^3)^{2/3} = 2^2$ dan $4^{-1/2} = (2^2)^{-1/2} = 2^{-1}$.",
            r"Pembilang $= 2^{2 + (-1)} = 2^1$.",
            r"Bagi: $2^{1 - (-3)} = 2^4 = 16$."),
      "Trik utama soal eksponen: samakan basisnya dulu, baru jumlah/kurangi pangkatnya."),
    S("pitfall", "Jebakan ujian",
      r"""<ul class="lesson-list">
        <li>$\sqrt{x^2} = |x|$, <b>bukan</b> $x$. Contoh: $\sqrt{(-3)^2} = 3$.</li>
        <li>$\sqrt{a + b} \ne \sqrt{a} + \sqrt{b}$. Coba $a = 9, b = 16$: kiri $5$, kanan $7$.</li>
        <li>$(a + b)^2 \ne a^2 + b^2$; yang benar $a^2 + 2ab + b^2$.</li>
        <li>$-2^2 = -4$, sedangkan $(-2)^2 = 4$. Pangkat dikerjakan sebelum tanda minus.</li>
        <li>$0.\overline{9} = 1$ tepat, bukan "hampir 1": selisihnya $10^{-N} \to 0$.</li>
      </ul>""",
      "Jebakan √(x²) = |x| ini sering banget keluar di UTS, terutama di soal limit dan domain. Tandai baik-baik."),
    S("checkpoint", "Mini checkpoint",
      qa(r"1. Apakah $0.1010010001\ldots$ (banyak nol bertambah satu-satu) rasional?",
         r"<p>Tidak. Desimalnya tak berhenti dan tak berulang dengan pola periodik tetap, jadi irasional.</p>") +
      qa(r"2. Tulis $\{x : -2 < x \le 7\} \cap \{x : x \ge 3\}$ dalam notasi interval.",
         r"<p>$[3, 7]$.</p>"),
      "Jawab dulu di kepala atau kertas, baru buka jawabannya. Bedanya jauh buat ingatan jangka panjang."),
]

# ═══════════════════════════════════════════════════════════════════════════
# 2. Pertidaksamaan & Nilai Mutlak
# ═══════════════════════════════════════════════════════════════════════════
PERTIDAKSAMAAN = [
    S("intuition", "Kapan sesuatu cukup?",
      r"""<p>Pertidaksamaan menjawab "untuk nilai berapa saja syaratnya terpenuhi?". Contoh nyata:
      batas toleransi baut $|d - 10| \le 0.05$ mm, atau syarat konvergensi $|f(x) - L| < \varepsilon$ yang jadi inti definisi limit.</p>
      <p>Jawaban pertidaksamaan hampir selalu <b>interval</b>, bukan satu angka.</p>""",
      "Nilai mutlak |x − a| itu jarak x ke a. Hampir semua soal nilai mutlak jadi gampang kalau dibaca sebagai jarak."),
    S("theorem", "Aturan formal",
      r"""<ul class="lesson-list">
        <li>Menambah/mengurangi kedua ruas tidak mengubah tanda.</li>
        <li>Mengali/membagi dengan bilangan <b>positif</b>: tanda tetap. Dengan bilangan <b>negatif</b>: tanda <b>dibalik</b>.</li>
        <li>Nilai mutlak: $|x| = \begin{cases} x & x \ge 0 \\ -x & x < 0 \end{cases}$, dan untuk $a > 0$:
          $$|x| < a \iff -a < x < a, \qquad |x| > a \iff x < -a \ \text{atau}\ x > a$$</li>
        <li>Ketaksamaan segitiga: $|a + b| \le |a| + |b|$.</li>
      </ul>""",
      "Ingat dua bentuk ini: |x| < a jadi satu interval 'diapit', |x| > a pecah jadi dua sinar ke luar."),
    S("derivation", "Metode titik kritis untuk pertidaksamaan rasional",
      r"""<p>Untuk $\dfrac{P(x)}{Q(x)} \ge 0$:</p>""" +
      steps(r"Pindahkan semua suku ke satu ruas, ruas lain $0$. <b>Jangan</b> kali silang.",
            r"Faktorkan pembilang dan penyebut.",
            r"Titik kritis = pembuat nol pembilang dan penyebut. Tandai di garis bilangan.",
            r"Uji tanda di tiap interval (cukup satu titik uji per interval).",
            r"Ambil interval yang sesuai. Pembuat nol penyebut <b>selalu</b> dikecualikan (kurung biasa).") +
      r"""<p>Untuk polinomial, tanda berganti di akar berderajat ganjil dan tetap di akar berderajat genap, mis. di $(x - 1)^2$.</p>""",
      "Titik uji paling cepat: angka bulat sederhana di tiap interval, seperti 0, 1, atau −10."),
    S("example", "Bedah soal: rasional dan nilai mutlak",
      r"""<p><b>Soal 1.</b> Selesaikan $\dfrac{x - 3}{x + 2} \le 1$.</p>""" +
      steps(r"Kurangi 1: $\dfrac{x - 3}{x + 2} - 1 = \dfrac{x - 3 - (x + 2)}{x + 2} = \dfrac{-5}{x + 2} \le 0$.",
            r"Pembilang $-5$ selalu negatif, jadi pecahan $\le 0$ tepat ketika penyebut positif: $x + 2 > 0$.",
            r"Jawaban: $x > -2$, yaitu $(-2, \infty)$. Perhatikan $x = -2$ dikecualikan.") +
      r"""<p><b>Soal 2.</b> Selesaikan $|2x - 5| \ge 3$.</p>""" +
      steps(r"Bentuk $|u| \ge 3$ artinya $u \le -3$ atau $u \ge 3$.",
            r"$2x - 5 \le -3 \Rightarrow x \le 1$; $\quad 2x - 5 \ge 3 \Rightarrow x \ge 4$.",
            r"Jawaban: $(-\infty, 1] \cup [4, \infty)$."),
      "Di Soal 1, kalau kamu kali silang dengan (x + 2), kamu harus pecah dua kasus tanda. Metode 'pindah ruas' jauh lebih aman.",
      [g("Grafik y = |2x − 5| dan garis y = c", [-2, 8], [-1, 9], [param("c", "Batas c", 0, 7, 0.5, 3, "c")],
         [{"type": "fn", "expr": "abs(2*x-5)", "color": "blue", "label": "|2x − 5|"},
          {"type": "hline", "y": "c", "color": "red", "dash": True},
          {"type": "point", "x": "(5-c)/2", "y": "c", "color": "red"}, {"type": "point", "x": "(5+c)/2", "y": "c", "color": "red"}],
         [readout("Batas kiri (5 − c)/2", "(5-c)/2", 2), readout("Batas kanan (5 + c)/2", "(5+c)/2", 2)],
         "Bagian grafik di atas garis merah adalah solusi |2x − 5| ≥ c.")]),
    S("pitfall", "Jebakan ujian",
      r"""<ul class="lesson-list">
        <li><b>Kali silang</b> dengan penyebut yang tandanya belum tentu positif. Kalau penyebut negatif, tanda harus dibalik.</li>
        <li>Lupa membalik tanda saat membagi dengan bilangan negatif: $-2x < 6 \Rightarrow x > -3$, bukan $x < -3$.</li>
        <li>Memasukkan pembuat nol penyebut ke jawaban. Pembagian dengan nol tidak terdefinisi.</li>
        <li>Mengkuadratkan kedua ruas tanpa syarat. Itu sah hanya kalau kedua ruas tak negatif, mis. $|x| < |y| \iff x^2 < y^2$.</li>
        <li>Menulis $|x| < -2$ punya solusi. Jarak tidak pernah negatif, jadi himpunan solusinya kosong.</li>
      </ul>""",
      "Soal UTS favorit dosen: pertidaksamaan pecahan yang menggoda buat dikali silang. Jangan tergoda!"),
    S("checkpoint", "Mini checkpoint",
      qa(r"1. Selesaikan $x^2 - x - 6 < 0$.", r"<p>$(x - 3)(x + 2) < 0 \Rightarrow -2 < x < 3$, yaitu $(-2, 3)$.</p>") +
      qa(r"2. Untuk nilai $\varepsilon = 0.01$, interval apa yang memenuhi $|x - 4| < \varepsilon$?", r"<p>$(3.99,\ 4.01)$.</p>"),
      "Soal kedua ini persis bentuk yang akan kamu temui di definisi limit ε–δ. Udah latihan duluan!"),
]

# ═══════════════════════════════════════════════════════════════════════════
# 3. Fungsi & Komposisi
# ═══════════════════════════════════════════════════════════════════════════
FUNGSI = [
    S("intuition", "Fungsi = mesin input-output",
      r"""<p>Fungsi $f$ memasangkan <b>setiap</b> input $x$ dengan <b>tepat satu</b> output $f(x)$. Di pemrograman: fungsi murni tanpa efek samping.
      Di fisika: posisi sebagai fungsi waktu $s(t)$.</p>
      <p>Komposisi $f \circ g$ = pipa: hasil $g$ langsung jadi input $f$. Seperti pipeline data: <code>normalize</code> lalu <code>predict</code>.</p>""",
      "Uji garis vertikal: kalau ada garis tegak yang memotong grafik dua kali, itu bukan fungsi."),
    S("theorem", "Domain, range, dan operasi fungsi",
      r"""<ul class="lesson-list">
        <li><b>Domain</b> $D_f$: semua input yang membuat $f$ terdefinisi. Syarat umum: penyebut $\ne 0$, isi akar genap $\ge 0$, isi log $> 0$.</li>
        <li><b>Range</b> $R_f$: semua output yang mungkin.</li>
        <li>$(f \pm g)(x) = f(x) \pm g(x)$, $(fg)(x) = f(x) g(x)$, $\left(\tfrac{f}{g}\right)(x) = \tfrac{f(x)}{g(x)}$ dengan domain $D_f \cap D_g$ (dan $g \ne 0$ untuk pembagian).</li>
        <li>Komposisi: $(f \circ g)(x) = f(g(x))$ dengan domain $\{x \in D_g : g(x) \in D_f\}$.</li>
      </ul>
      <p>Simetri: $f$ <b>genap</b> jika $f(-x) = f(x)$ (simetri sumbu $y$), <b>ganjil</b> jika $f(-x) = -f(x)$ (simetri titik asal).</p>""",
      "Domain komposisi sering dijebak: harus lolos syarat g dulu, BARU hasilnya lolos syarat f."),
    S("intuition", "Eksplorasi: transformasi grafik",
      r"""<p>Dari grafik dasar $y = f(x)$:</p>
      <ul class="lesson-list">
        <li>$y = f(x - h) + k$: geser kanan $h$, naik $k$.</li>
        <li>$y = a f(x)$: regang vertikal dengan faktor $a$ (dan cermin terhadap sumbu $x$ bila $a < 0$).</li>
        <li>$y = f(bx)$: mampat horizontal dengan faktor $\tfrac{1}{b}$.</li>
      </ul>""",
      "Perhatikan: f(x − h) geser ke KANAN walau tandanya minus. Ini paling sering kebalik.",
      [g("Transformasi y = a·(x − h)² + k", [-6, 6], [-6, 8],
         [param("a", "Regangan a", -2, 2, 0.25, 1, "a"), param("h", "Geser h", -3, 3, 0.5, 1, "h"), param("k", "Geser k", -3, 3, 0.5, -2, "k")],
         [{"type": "fn", "expr": "x*x", "color": "gray", "label": "y = x²"},
          {"type": "fn", "expr": "a*(x-h)*(x-h)+k", "color": "blue", "label": "y = a(x − h)² + k"},
          {"type": "point", "x": "h", "y": "k", "color": "red"}],
         [readout("Puncak (h, k): h", "h", 2), readout("k", "k", 2)],
         "Titik merah adalah puncak yang ikut bergeser ke (h, k).")]),
    S("example", "Bedah soal: domain komposisi",
      r"""<p><b>Soal.</b> $f(x) = \sqrt{x - 1}$ dan $g(x) = \dfrac{1}{x - 3}$. Tentukan $(f \circ g)(x)$ dan domainnya.</p>""" +
      steps(r"$(f \circ g)(x) = f\!\left(\tfrac{1}{x - 3}\right) = \sqrt{\dfrac{1}{x - 3} - 1} = \sqrt{\dfrac{4 - x}{x - 3}}$.",
            r"Syarat $g$: $x \ne 3$.",
            r"Syarat $f$: $\dfrac{4 - x}{x - 3} \ge 0$. Titik kritis $3$ dan $4$; uji tanda: positif di $(3, 4)$, nol di $x = 4$.",
            r"Domain $= (3, 4]$.") +
      r"""<p><b>Soal 2.</b> Tunjukkan $f(x) = x^3 - x$ ganjil.</p>""" +
      steps(r"$f(-x) = (-x)^3 - (-x) = -x^3 + x = -(x^3 - x) = -f(x)$. Terbukti ganjil."),
      "Untuk domain komposisi, sederhanakan dulu rumusnya, tapi syarat g yang awal (x ≠ 3) JANGAN dibuang."),
    S("pitfall", "Jebakan ujian",
      r"""<ul class="lesson-list">
        <li>$f \circ g \ne g \circ f$ pada umumnya. Coba $f(x) = x^2$, $g(x) = x + 1$.</li>
        <li>$f(a + b) \ne f(a) + f(b)$ kecuali $f$ linear tanpa konstanta. $\sin(a + b) \ne \sin a + \sin b$.</li>
        <li>$f^{-1}(x)$ (invers) $\ne \dfrac{1}{f(x)}$ (kebalikan).</li>
        <li>Menghitung domain dari rumus yang sudah disederhanakan saja, sehingga syarat lama hilang. Contoh: $\tfrac{x^2 - 1}{x - 1} = x + 1$ tetapi $x \ne 1$.</li>
      </ul>""",
      "Kalimat sakti: domain ditentukan rumus ASLI, bukan rumus yang udah dicoret-coret."),
    S("checkpoint", "Mini checkpoint",
      qa(r"1. Jika $f(x) = 2x + 1$ dan $g(x) = x^2$, hitung $(f \circ g)(3)$ dan $(g \circ f)(3)$.", r"<p>$(f \circ g)(3) = f(9) = 19$; $(g \circ f)(3) = g(7) = 49$.</p>") +
      qa(r"2. Domain $h(x) = \ln(4 - x^2)$?", r"<p>$4 - x^2 > 0 \Rightarrow -2 < x < 2$, yaitu $(-2, 2)$.</p>"),
      "Kalau dua hasil di soal 1 sama, cek lagi: komposisi itu tidak komutatif."),
]

# ═══════════════════════════════════════════════════════════════════════════
# 4. Fungsi Invers (baru)
# ═══════════════════════════════════════════════════════════════════════════
INVERS = [
    S("intuition", "Membalik mesin",
      r"""<p>Kalau $f$ mengubah suhu Celsius ke Fahrenheit, $f^{-1}$ mengubah Fahrenheit balik ke Celsius. Invers "membatalkan" kerja $f$:
      $$f^{-1}(f(x)) = x \quad\text{dan}\quad f(f^{-1}(y)) = y.$$</p>
      <p>Di kriptografi, enkripsi harus punya invers (dekripsi); di grafika, transformasi kamera dibalik untuk memetakan piksel ke dunia 3D.</p>""",
      "Invers cuma ada kalau tiap output datang dari satu input saja. Kalau dua input menghasilkan output sama, mesin gak bisa dibalik."),
    S("theorem", "Syarat invers: fungsi satu-satu",
      r"""<p>$f$ <b>satu-satu</b> (injektif) jika $f(x_1) = f(x_2) \Rightarrow x_1 = x_2$. Secara grafis: lolos <b>uji garis horizontal</b>.</p>
      <p>Bila $f$ satu-satu dengan domain $D$ dan range $R$, maka $f^{-1}: R \to D$ dengan
      $$f^{-1}(y) = x \iff f(x) = y.$$</p>
      <p>Domain $f^{-1}$ = range $f$, dan range $f^{-1}$ = domain $f$. Fungsi yang monoton murni (selalu naik atau selalu turun) pasti satu-satu.</p>""",
      "Uji garis horizontal: geser garis mendatar ke atas-bawah. Kalau ada posisi yang memotong grafik dua kali, gak punya invers."),
    S("derivation", "Cara mencari rumus invers",
      steps(r"Tulis $y = f(x)$.",
            r"Selesaikan persamaan untuk $x$ dalam $y$.",
            r"Tukar nama variabel: $x \leftrightarrow y$, hasilnya $y = f^{-1}(x)$.",
            r"Cek domain dan range, serta verifikasi $f(f^{-1}(x)) = x$.") +
      r"""<p>Grafik $f^{-1}$ adalah cerminan grafik $f$ terhadap garis $y = x$.</p>""",
      "Selalu verifikasi dengan substitusi balik. Dua detik, menyelamatkan satu soal penuh.",
      [g("Cerminan terhadap y = x: f(x) = m·x + c", [-5, 5], [-5, 5],
         [param("m", "Kemiringan m", -3, 3, 0.25, 2, "m"), param("c", "Konstanta c", -3, 3, 0.5, 1, "c")],
         [{"type": "fn", "expr": "x", "color": "gray", "dash": True, "label": "y = x"},
          {"type": "fn", "expr": "m*x+c", "color": "blue", "label": "f(x)"},
          {"type": "fn", "expr": "(x-c)/m", "color": "orange", "label": "f⁻¹(x)"}],
         [readout("Kemiringan invers 1/m", "1/m", 3)],
         "Kemiringan invers adalah kebalikan kemiringan f. Coba m = 0: inversnya lenyap karena f tidak satu-satu.")]),
    S("example", "Bedah soal: invers fungsi rasional & kuadrat terbatas",
      r"""<p><b>Soal 1.</b> Cari invers $f(x) = \dfrac{2x + 1}{x - 3}$, $x \ne 3$.</p>""" +
      steps(r"$y(x - 3) = 2x + 1 \Rightarrow xy - 3y = 2x + 1$.",
            r"Kumpulkan $x$: $x(y - 2) = 3y + 1 \Rightarrow x = \dfrac{3y + 1}{y - 2}$.",
            r"$f^{-1}(x) = \dfrac{3x + 1}{x - 2}$, domain $x \ne 2$ (= range $f$, asimtot datar $y = 2$).") +
      r"""<p><b>Soal 2.</b> $f(x) = x^2 - 4x$ pada $x \ge 2$. Cari $f^{-1}$.</p>""" +
      steps(r"Lengkapkan kuadrat: $y = (x - 2)^2 - 4$, jadi $(x - 2)^2 = y + 4$.",
            r"Karena $x \ge 2$, ambil akar positif: $x = 2 + \sqrt{y + 4}$.",
            r"$f^{-1}(x) = 2 + \sqrt{x + 4}$, $x \ge -4$."),
      "Soal 2: pembatasan domain x ≥ 2 itulah yang memilih tanda + pada akar. Tanpa itu, f tidak punya invers."),
    S("pitfall", "Jebakan ujian",
      r"""<ul class="lesson-list">
        <li>$f^{-1}(x) \ne \dfrac{1}{f(x)}$. Notasi $-1$ di sini bukan pangkat.</li>
        <li>Lupa $\pm$ saat mengakarkan, atau memilih tanda tanpa melihat batasan domain.</li>
        <li>Lupa menukar domain dan range: domain $f^{-1}$ = range $f$.</li>
        <li>Mengklaim $f(x) = x^2$ punya invers $\sqrt{x}$ di seluruh $\mathbb{R}$. Hanya benar bila domain dibatasi ke $x \ge 0$.</li>
      </ul>""",
      "Ini nanti penting banget di arcsin, arccos, arctan: semuanya invers dari fungsi trig yang domainnya DIBATASI."),
    S("checkpoint", "Mini checkpoint",
      qa(r"1. Apakah $f(x) = x^3 + 1$ punya invers? Kalau ya, cari rumusnya.", r"<p>Ya, monoton naik. $f^{-1}(x) = \sqrt[3]{x - 1}$.</p>") +
      qa(r"2. Jika $f(2) = 7$, berapa $f^{-1}(7)$?", r"<p>$f^{-1}(7) = 2$.</p>"),
      "Soal 2 itu definisi murni. Kalau ragu, balik ke kalimat: f⁻¹(y) = x kalau dan hanya kalau f(x) = y."),
]

# ═══════════════════════════════════════════════════════════════════════════
# 5. Polinomial & Fungsi Rasional (baru)
# ═══════════════════════════════════════════════════════════════════════════
POLINOMIAL = [
    S("intuition", "Bahan dasar hampir semua model",
      r"""<p>Polinomial $P(x) = a_n x^n + \dots + a_1 x + a_0$ adalah fungsi paling "jinak": mulus, terdefinisi di mana-mana, mudah diturunkan.
      Deret Taylor nanti menunjukkan bahwa hampir semua fungsi bisa didekati polinomial.</p>
      <p>Fungsi rasional $R(x) = \dfrac{P(x)}{Q(x)}$ muncul di fungsi transfer sistem kendali (FT), kompleksitas algoritma (Fasilkom), dan laju reaksi (FMIPA).</p>""",
      "Derajat polinomial menentukan 'nasib ujung' grafiknya: lihat suku pangkat tertinggi saja."),
    S("theorem", "Sifat polinomial",
      r"""<ul class="lesson-list">
        <li><b>Perilaku ujung</b> ditentukan suku utama $a_n x^n$: derajat genap → kedua ujung searah; ganjil → berlawanan.</li>
        <li><b>Teorema sisa:</b> sisa pembagian $P(x)$ oleh $(x - c)$ adalah $P(c)$.</li>
        <li><b>Teorema faktor:</b> $(x - c)$ faktor dari $P(x) \iff P(c) = 0$.</li>
        <li><b>Akar rasional:</b> calon akar rasional $\dfrac{p}{q}$ dengan $p \mid a_0$ dan $q \mid a_n$.</li>
        <li>Polinomial derajat $n$ punya paling banyak $n$ akar real.</li>
      </ul>""",
      "Teorema sisa itu jalan pintas: gak perlu bagi panjang, cukup substitusi x = c."),
    S("theorem", "Fungsi rasional & asimtot",
      r"""<p>Untuk $R(x) = \dfrac{P(x)}{Q(x)}$ yang sudah disederhanakan:</p>
      <ul class="lesson-list">
        <li><b>Asimtot tegak</b> $x = c$ di pembuat nol $Q$ yang <i>tidak</i> menjadi nol $P$.</li>
        <li><b>Lubang</b> di $x = c$ bila faktor $(x - c)$ tercoret dari pembilang dan penyebut.</li>
        <li><b>Asimtot datar</b>: $\deg P < \deg Q \Rightarrow y = 0$; $\deg P = \deg Q \Rightarrow y = \dfrac{a_n}{b_n}$; $\deg P > \deg Q$ → tidak ada (bila selisih derajat 1: asimtot miring dari pembagian).</li>
      </ul>""",
      "Lubang vs asimtot: kalau faktornya bisa dicoret, itu lubang. Kalau tersisa di penyebut, itu asimtot.",
      [g("R(x) = (x² − 1)/(x − a)", [-6, 6], [-10, 10], [param("a", "Pembuat nol penyebut a", -3, 3, 0.5, 2, "a")],
         [{"type": "fn", "expr": "(x*x-1)/(x-a)", "color": "blue", "label": "R(x)"},
          {"type": "fn", "expr": "x+a", "color": "gray", "dash": True, "label": "asimtot miring y = x + a"}],
         [readout("R(0)", "(0-1)/(0-a)", 3)],
         "Coba a = 1 atau a = −1: asimtot tegaknya hilang dan berganti lubang, karena faktornya tercoret.")]),
    S("example", "Bedah soal: faktorisasi & analisis rasional",
      r"""<p><b>Soal 1.</b> Faktorkan $P(x) = x^3 - 4x^2 + x + 6$.</p>""" +
      steps(r"Calon akar rasional: $\pm 1, \pm 2, \pm 3, \pm 6$.",
            r"$P(-1) = -1 - 4 - 1 + 6 = 0$, jadi $(x + 1)$ faktor.",
            r"Bagi sintetik: $P(x) = (x + 1)(x^2 - 5x + 6) = (x + 1)(x - 2)(x - 3)$.") +
      r"""<p><b>Soal 2.</b> Analisis $R(x) = \dfrac{2x^2 - 8}{x^2 - x - 2}$.</p>""" +
      steps(r"Faktorkan: $\dfrac{2(x - 2)(x + 2)}{(x - 2)(x + 1)}$.",
            r"Faktor $(x - 2)$ tercoret: <b>lubang</b> di $x = 2$, dengan nilai $\dfrac{2(4)}{3} = \tfrac{8}{3}$.",
            r"Sisa penyebut nol di $x = -1$: <b>asimtot tegak</b> $x = -1$.",
            r"Derajat sama: <b>asimtot datar</b> $y = \tfrac{2}{1} = 2$."),
      "Di soal 2, banyak yang langsung bilang 'asimtot tegak x = 2'. Faktorkan dulu, baru simpulkan."),
    S("pitfall", "Jebakan ujian",
      r"""<ul class="lesson-list">
        <li>Mencoret suku, bukan faktor: $\dfrac{x + 2}{x} \ne 2$. Yang boleh dicoret hanya <b>faktor</b> perkalian.</li>
        <li>Menyebut asimtot tegak sebelum menyederhanakan, sehingga lubang salah dikira asimtot.</li>
        <li>Mengira grafik tidak pernah memotong asimtot datar. Asimtot datar boleh dipotong; asimtot <b>tegak</b> yang tidak boleh.</li>
        <li>Salah tanda di pembagian sintetik saat membagi oleh $(x + c)$: gunakan $-c$.</li>
      </ul>""",
      "Mencoret suku itu dosa aljabar paling klasik. Cek: apakah yang dicoret dikalikan dengan semua sisanya?"),
    S("checkpoint", "Mini checkpoint",
      qa(r"1. Sisa pembagian $x^4 - 3x + 5$ oleh $(x - 2)$?", r"<p>$P(2) = 16 - 6 + 5 = 15$.</p>") +
      qa(r"2. Asimtot datar $R(x) = \dfrac{5x^3 + 1}{2x^3 - x}$?", r"<p>Derajat sama: $y = \tfrac{5}{2}$.</p>"),
      "Kalau cepat jawab soal 1 tanpa bagi panjang, teorema sisa udah masuk ke tangan kamu."),
]

# ═══════════════════════════════════════════════════════════════════════════
# 6. Trigonometri & Identitas
# ═══════════════════════════════════════════════════════════════════════════
TRIGONOMETRI = [
    S("intuition", "Lingkaran satuan: pabrik gelombang",
      r"""<p>Titik yang berputar di lingkaran berjari-jari $1$ dengan sudut $\theta$ berada di $(\cos\theta, \sin\theta)$.
      Saat titik itu berputar terus, proyeksinya membentuk gelombang. Itulah kenapa sinyal suara, arus AC, dan getaran semuanya trigonometri.</p>
      <p>Di kalkulus, sudut <b>selalu</b> dalam radian: $\pi \text{ rad} = 180^\circ$. Rumus seperti $\tfrac{d}{dx}\sin x = \cos x$ hanya benar dalam radian.</p>""",
      "Satu radian = sudut yang busurnya sepanjang jari-jari. Bukan angka ajaib, cuma satuan yang paling alami."),
    S("theorem", "Definisi & grafik dasar",
      r"""<p>$$\tan\theta = \frac{\sin\theta}{\cos\theta}, \quad \sec\theta = \frac{1}{\cos\theta}, \quad \csc\theta = \frac{1}{\sin\theta}, \quad \cot\theta = \frac{\cos\theta}{\sin\theta}$$</p>
      <ul class="lesson-list">
        <li>$\sin$ dan $\cos$: domain $\mathbb{R}$, range $[-1, 1]$, periode $2\pi$.</li>
        <li>$\tan$: domain $x \ne \tfrac{\pi}{2} + k\pi$, range $\mathbb{R}$, periode $\pi$.</li>
        <li>$y = A\sin(B(x - C)) + D$: amplitudo $|A|$, periode $\tfrac{2\pi}{|B|}$, geser fase $C$, garis tengah $y = D$.</li>
      </ul>""",
      "Periode 2π/|B|: makin besar B, gelombangnya makin rapat.",
      [g("y = A·sin(B(x − C)) + D", [-7, 7], [-5, 5],
         [param("A", "Amplitudo A", -3, 3, 0.25, 2, "A"), param("B", "Frekuensi B", 0.25, 4, 0.25, 1, "B"),
          param("C", "Geser fase C", -3, 3, 0.25, 0, "C"), param("D", "Garis tengah D", -2, 2, 0.25, 0, "D")],
         [{"type": "fn", "expr": "sin(x)", "color": "gray", "label": "sin x"},
          {"type": "fn", "expr": "A*sin(B*(x-C))+D", "color": "blue", "label": "A sin(B(x − C)) + D"},
          {"type": "hline", "y": "D", "color": "orange", "dash": True}],
         [readout("Periode 2π/B", "2*pi/B", 3), readout("Amplitudo |A|", "abs(A)", 2)],
         "Geser satu slider dalam satu waktu, supaya kamu tahu efek tiap parameter.")]),
    S("theorem", "Identitas yang wajib hafal",
      r"""<p><b>Pythagoras:</b> $\sin^2\theta + \cos^2\theta = 1$, $\ 1 + \tan^2\theta = \sec^2\theta$, $\ 1 + \cot^2\theta = \csc^2\theta$.</p>
      <p><b>Jumlah sudut:</b>
      $$\sin(a \pm b) = \sin a \cos b \pm \cos a \sin b, \qquad \cos(a \pm b) = \cos a \cos b \mp \sin a \sin b$$</p>
      <p><b>Sudut ganda:</b> $\sin 2\theta = 2\sin\theta\cos\theta$, $\ \cos 2\theta = \cos^2\theta - \sin^2\theta = 1 - 2\sin^2\theta = 2\cos^2\theta - 1$.</p>
      <p><b>Setengah sudut</b> (kunci integral trig nanti): $\sin^2\theta = \dfrac{1 - \cos 2\theta}{2}$, $\ \cos^2\theta = \dfrac{1 + \cos 2\theta}{2}$.</p>""",
      "Cukup hafal sin²+cos²=1 dan rumus jumlah sudut. Sisanya bisa diturunkan dari situ dalam 30 detik."),
    S("example", "Bedah soal: identitas & persamaan trig",
      r"""<p><b>Soal 1.</b> Buktikan $\dfrac{1 - \cos 2x}{\sin 2x} = \tan x$.</p>""" +
      steps(r"Pembilang: $1 - \cos 2x = 1 - (1 - 2\sin^2 x) = 2\sin^2 x$.",
            r"Penyebut: $\sin 2x = 2\sin x\cos x$.",
            r"Bagi: $\dfrac{2\sin^2 x}{2\sin x\cos x} = \dfrac{\sin x}{\cos x} = \tan x$ (untuk $\sin x \ne 0$, $\cos x \ne 0$).") +
      r"""<p><b>Soal 2.</b> Selesaikan $2\sin^2 x - \sin x - 1 = 0$ pada $[0, 2\pi)$.</p>""" +
      steps(r"Misalkan $u = \sin x$: $2u^2 - u - 1 = (2u + 1)(u - 1) = 0$.",
            r"$\sin x = 1 \Rightarrow x = \tfrac{\pi}{2}$.",
            r"$\sin x = -\tfrac{1}{2} \Rightarrow x = \tfrac{7\pi}{6}$ atau $x = \tfrac{11\pi}{6}$ (kuadran III dan IV).",
            r"Solusi: $\left\{\tfrac{\pi}{2}, \tfrac{7\pi}{6}, \tfrac{11\pi}{6}\right\}$."),
      "Persamaan trig kuadrat: substitusi u = sin x dulu, selesaikan kuadratnya, baru balik ke sudut di semua kuadran."),
    S("pitfall", "Jebakan ujian",
      r"""<ul class="lesson-list">
        <li>Kalkulator di mode <b>derajat</b> saat soal kalkulus. Selalu radian.</li>
        <li>$\sin^2 x$ berarti $(\sin x)^2$, sedangkan $\sin^{-1} x$ berarti $\arcsin x$, <b>bukan</b> $\tfrac{1}{\sin x}$.</li>
        <li>Membagi persamaan dengan $\sin x$ sehingga solusi $\sin x = 0$ hilang. Faktorkan, jangan bagi.</li>
        <li>Hanya mengambil satu solusi dari $\sin x = c$. Ada dua per periode (kecuali $c = \pm 1$).</li>
        <li>$\sin(2x) \ne 2\sin x$ dan $\cos(a + b) \ne \cos a + \cos b$.</li>
      </ul>""",
      "Membagi dengan sin x itu cara tercepat kehilangan setengah jawaban. Pindah ruas lalu faktorkan."),
    S("checkpoint", "Mini checkpoint",
      qa(r"1. Hitung $\cos\tfrac{\pi}{12}$ secara eksak.", r"<p>$\cos(\tfrac{\pi}{3} - \tfrac{\pi}{4}) = \tfrac12\cdot\tfrac{\sqrt2}{2} + \tfrac{\sqrt3}{2}\cdot\tfrac{\sqrt2}{2} = \dfrac{\sqrt6 + \sqrt2}{4}$.</p>") +
      qa(r"2. Periode $y = 3\cos(4x) - 1$?", r"<p>$\tfrac{2\pi}{4} = \tfrac{\pi}{2}$.</p>"),
      "π/12 = 15°. Pecah jadi selisih dua sudut istimewa yang kamu hafal."),
]

# ═══════════════════════════════════════════════════════════════════════════
# 7. Eksponensial & Logaritma
# ═══════════════════════════════════════════════════════════════════════════
EKSPONENSIAL = [
    S("intuition", "Tumbuh sebanding dengan dirinya sendiri",
      r"""<p>Bakteri, bunga majemuk, peluruhan radioaktif, dan banyaknya kemungkinan password: semuanya berubah sebanding dengan ukurannya sekarang.
      Itulah fungsi eksponensial $f(x) = a^x$.</p>
      <p>Logaritma adalah kebalikannya: "berapa kali harus dikali?". Pencarian biner butuh $\log_2 n$ langkah; skala desibel dan pH juga logaritmik.</p>""",
      "Eksponensial = 'berapa hasilnya setelah x kali dikali', logaritma = 'berapa kali dikali sampai hasilnya segini'."),
    S("theorem", "Definisi & sifat",
      r"""<p>Untuk $a > 0$, $a \ne 1$: $\ y = \log_a x \iff a^y = x$, dengan domain log $x > 0$.</p>
      <p>$$\log_a(xy) = \log_a x + \log_a y, \qquad \log_a\frac{x}{y} = \log_a x - \log_a y, \qquad \log_a x^r = r\log_a x$$</p>
      <p>$$\log_a x = \frac{\ln x}{\ln a}, \qquad a^{\log_a x} = x, \qquad \log_a a^x = x$$</p>
      <p>Bilangan $e = \lim_{n\to\infty}\left(1 + \tfrac1n\right)^n \approx 2.71828$, dan $\ln x = \log_e x$. Basis $e$ paling alami karena $\tfrac{d}{dx}e^x = e^x$.</p>""",
      "Rumus ganti basis log_a x = ln x / ln a itu penyelamat kalau kalkulator cuma punya tombol ln.",
      [g("y = aˣ dan inversnya y = logₐ x", [-4, 6], [-4, 6], [param("a", "Basis a", 0.2, 4, 0.1, 2, "a")],
         [{"type": "fn", "expr": "pow(a,x)", "color": "blue", "label": "aˣ"},
          {"type": "fn", "expr": "log(x)/log(a)", "color": "orange", "label": "logₐ x"},
          {"type": "fn", "expr": "x", "color": "gray", "dash": True, "label": "y = x"}],
         [readout("a² ", "pow(a,2)", 3), readout("logₐ 10", "log(10)/log(a)", 3)],
         "Basis a < 1 membuat aˣ turun. Kedua grafik selalu bercermin terhadap y = x.")]),
    S("derivation", "Dari bunga majemuk ke bilangan e",
      r"""<p>Modal $1$ dengan bunga $100\%$ per tahun, dibungakan $n$ kali setahun, menjadi $\left(1 + \tfrac1n\right)^n$ di akhir tahun.</p>""" +
      steps(r"$n = 1$: $2$. $\quad n = 12$: $\left(1 + \tfrac{1}{12}\right)^{12} \approx 2.613$. $\quad n = 365$: $\approx 2.7146$.",
            r"Makin sering dibungakan, hasilnya naik tapi melambat dan tidak meledak.",
            r"Batasnya $e = \displaystyle\lim_{n\to\infty}\left(1 + \tfrac1n\right)^n \approx 2.71828$.",
            r"Untuk bunga $r$ selama $t$ tahun secara kontinu: $A = P e^{rt}$.") +
      note(r"Inilah alasan $e$ disebut basis alami: ia muncul sendiri dari proses tumbuh yang kontinu."),
      "Ini contoh pertama limit di kurikulum. Di Level 2 kamu bakal membuktikan limit ini dengan cara yang lebih formal.",
      [g("(1 + 1/n)ⁿ menuju e", [1, 60], [1.8, 3], [param("n", "Banyak periode n", 1, 60, 1, 12, "n")],
         [{"type": "fn", "expr": "pow(1+1/x,x)", "color": "blue", "label": "(1 + 1/n)ⁿ"},
          {"type": "hline", "y": "e", "color": "red", "dash": True},
          {"type": "point", "x": "n", "y": "pow(1+1/n,n)", "color": "orange"}],
         [readout("(1 + 1/n)ⁿ", "pow(1+1/n,n)", 6), readout("Selisih dengan e", "e-pow(1+1/n,n)", 6)],
         "Selisihnya mengecil kira-kira sebanding 1/n.")]),
    S("example", "Bedah soal: persamaan eksponen & log",
      r"""<p><b>Soal 1.</b> Selesaikan $3^{2x} - 4\cdot 3^x + 3 = 0$.</p>""" +
      steps(r"Misalkan $u = 3^x > 0$: $u^2 - 4u + 3 = (u - 1)(u - 3) = 0$.",
            r"$3^x = 1 \Rightarrow x = 0$; $\quad 3^x = 3 \Rightarrow x = 1$.",
            r"Solusi: $x \in \{0, 1\}$.") +
      r"""<p><b>Soal 2.</b> Selesaikan $\log_2(x + 2) + \log_2(x - 2) = 5$.</p>""" +
      steps(r"Syarat: $x + 2 > 0$ dan $x - 2 > 0 \Rightarrow x > 2$.",
            r"Gabung: $\log_2\big((x + 2)(x - 2)\big) = 5 \Rightarrow x^2 - 4 = 32$.",
            r"$x^2 = 36 \Rightarrow x = \pm 6$. Cek syarat: hanya $x = 6$ yang memenuhi.") +
      r"""<p><b>Soal 3 (waktu paruh).</b> Zat meluruh $m(t) = m_0 e^{-kt}$ dengan waktu paruh $5$ tahun. Cari $k$.</p>""" +
      steps(r"$\tfrac12 m_0 = m_0 e^{-5k} \Rightarrow e^{-5k} = \tfrac12$.",
            r"$-5k = \ln\tfrac12 = -\ln 2 \Rightarrow k = \dfrac{\ln 2}{5} \approx 0.139$ per tahun."),
      "Di soal log, tulis syarat domain PALING AWAL. Biar akar palsu seperti x = −6 langsung ketahuan."),
    S("pitfall", "Jebakan ujian",
      r"""<ul class="lesson-list">
        <li>$\log(x + y) \ne \log x + \log y$. Sifatnya untuk <b>perkalian</b>, bukan penjumlahan.</li>
        <li>$(\ln x)^2 \ne \ln(x^2) = 2\ln x$.</li>
        <li>Lupa memeriksa syarat isi log $> 0$, sehingga akar palsu ikut dijawab.</li>
        <li>$\dfrac{\ln a}{\ln b} \ne \ln\dfrac{a}{b}$.</li>
        <li>Mengira $a^x$ bisa nol atau negatif. Untuk $a > 0$, selalu $a^x > 0$.</li>
      </ul>""",
      "Kalau ragu sama sifat log, uji dengan angka kecil: log 2 + log 3 = log 6, bukan log 5."),
    S("checkpoint", "Mini checkpoint",
      qa(r"1. Sederhanakan $\log_3 54 - \log_3 2$.", r"<p>$\log_3 27 = 3$.</p>") +
      qa(r"2. Selesaikan $e^{2x} = 7$.", r"<p>$x = \tfrac{\ln 7}{2} \approx 0.973$.</p>"),
      "Soal 2: ambil ln kedua ruas, karena ln adalah invers dari e^x."),
]

# ═══════════════════════════════════════════════════════════════════════════
# 8. Barisan & Notasi Sigma (baru)
# ═══════════════════════════════════════════════════════════════════════════
BARISAN = [
    S("intuition", "Daftar bernomor dan penjumlahan panjang",
      r"""<p>Barisan $(a_n)$ adalah fungsi dengan domain bilangan asli: $a_1, a_2, a_3, \dots$. Contoh: saldo tabungan tiap bulan, galat iterasi Newton tiap langkah.</p>
      <p>Notasi sigma meringkas penjumlahan panjang. Loop <code>for k in range(1, n+1): s += f(k)</code> di Python persis $\displaystyle\sum_{k=1}^{n} f(k)$.</p>
      <p>Di Level 2, jumlah Riemann (dasar integral) ditulis dengan sigma. Di Level 3, deret tak hingga juga.</p>""",
      "Baca Σ seperti for-loop: indeks bawah = nilai awal, atas = nilai akhir, rumus di kanan = isi loop."),
    S("theorem", "Barisan aritmetika & geometri",
      r"""<ul class="lesson-list">
        <li><b>Aritmetika</b> (selisih tetap $b$): $a_n = a_1 + (n - 1)b$, $\quad S_n = \dfrac{n}{2}(a_1 + a_n)$.</li>
        <li><b>Geometri</b> (rasio tetap $r$): $a_n = a_1 r^{n-1}$, $\quad S_n = a_1\dfrac{1 - r^n}{1 - r}$ ($r \ne 1$).</li>
        <li>Deret geometri tak hingga konvergen untuk $|r| < 1$: $\displaystyle\sum_{n=1}^{\infty} a_1 r^{n-1} = \frac{a_1}{1 - r}$.</li>
      </ul>""",
      "Bunga majemuk = geometri, cicilan tetap = aritmetika. Kenali polanya dari selisih atau rasionya.",
      [g("Jumlah parsial deret geometri a₁ = 1, rasio r", [0, 20], [-1, 6], [param("r", "Rasio r", -0.9, 0.9, 0.05, 0.5, "r")],
         [{"type": "fn", "expr": "(1-pow(r,floor(x)))/(1-r)", "color": "blue", "label": "Sₙ"},
          {"type": "fn", "expr": "1/(1-r)", "color": "red", "dash": True, "label": "1/(1 − r)"}],
         [readout("Limit 1/(1 − r)", "1/(1-r)", 4), readout("S₁₀", "(1-pow(r,10))/(1-r)", 4)],
         "Untuk |r| < 1 jumlah parsialnya mendekati garis merah. Coba r negatif: mendekatnya zig-zag.")]),
    S("theorem", "Sifat & rumus sigma",
      r"""<p>$$\sum_{k=1}^{n}(c\,a_k + b_k) = c\sum_{k=1}^{n}a_k + \sum_{k=1}^{n}b_k$$</p>
      <p>$$\sum_{k=1}^{n} 1 = n, \quad \sum_{k=1}^{n} k = \frac{n(n + 1)}{2}, \quad \sum_{k=1}^{n} k^2 = \frac{n(n + 1)(2n + 1)}{6}, \quad \sum_{k=1}^{n} k^3 = \left(\frac{n(n + 1)}{2}\right)^2$$</p>
      <p><b>Teleskopik:</b> $\displaystyle\sum_{k=1}^{n}(a_{k+1} - a_k) = a_{n+1} - a_1$ (suku tengah saling menghapus).</p>""",
      "Rumus Σk dan Σk² ini akan kamu pakai lagi persis waktu menghitung luas dengan jumlah Riemann."),
    S("example", "Bedah soal: sigma & teleskopik",
      r"""<p><b>Soal 1.</b> Hitung $\displaystyle\sum_{k=1}^{20}(3k^2 - 2k + 1)$.</p>""" +
      steps(r"Pecah: $3\sum k^2 - 2\sum k + \sum 1$.",
            r"$\sum k^2 = \tfrac{20\cdot21\cdot41}{6} = 2870$, $\sum k = 210$, $\sum 1 = 20$.",
            r"Hasil: $3(2870) - 2(210) + 20 = 8610 - 420 + 20 = 8210$.") +
      r"""<p><b>Soal 2.</b> Hitung $\displaystyle\sum_{k=1}^{n}\frac{1}{k(k + 1)}$.</p>""" +
      steps(r"Pecahan parsial: $\dfrac{1}{k(k + 1)} = \dfrac1k - \dfrac{1}{k + 1}$.",
            r"Teleskopik: $\left(1 - \tfrac12\right) + \left(\tfrac12 - \tfrac13\right) + \dots + \left(\tfrac1n - \tfrac{1}{n + 1}\right)$.",
            r"Sisa: $1 - \dfrac{1}{n + 1} = \dfrac{n}{n + 1}$, dan menuju $1$ saat $n \to \infty$."),
      "Pola 1/(k(k+1)) itu klasik banget. Tiap lihat perkalian dua faktor berurutan di penyebut, curigai teleskopik."),
    S("pitfall", "Jebakan ujian",
      r"""<ul class="lesson-list">
        <li>$\sum a_k b_k \ne \left(\sum a_k\right)\left(\sum b_k\right)$.</li>
        <li>Salah menghitung banyak suku: $\sum_{k=3}^{10}$ punya $10 - 3 + 1 = 8$ suku, bukan $7$.</li>
        <li>$\sum_{k=1}^{n} c = nc$, bukan $c$.</li>
        <li>Memakai $\tfrac{a_1}{1 - r}$ saat $|r| \ge 1$. Deretnya divergen.</li>
        <li>Lupa menggeser indeks saat mengganti batas: $\sum_{k=1}^{n} a_{k-1} = \sum_{j=0}^{n-1} a_j$.</li>
      </ul>""",
      "Selisih indeks plus satu. Kesalahan 'off-by-one' ini juga favorit bug di loop program, lho."),
    S("checkpoint", "Mini checkpoint",
      qa(r"1. $1 + 4 + 7 + \dots + 100$ = ?", r"<p>Aritmetika, $b = 3$, $n = 34$: $S = \tfrac{34}{2}(1 + 100) = 1717$.</p>") +
      qa(r"2. Nilai $0.\overline{3}$ sebagai deret geometri?", r"<p>$\tfrac{3}{10} + \tfrac{3}{100} + \dots = \dfrac{3/10}{1 - 1/10} = \tfrac13$.</p>"),
      "Soal 1: cari n dulu dari a_n = 1 + (n − 1)·3 = 100."),
]

# ═══════════════════════════════════════════════════════════════════════════
# 9. Pengantar Vektor & Matriks Dasar (baru)
# ═══════════════════════════════════════════════════════════════════════════
VEKTOR = [
    S("intuition", "Besaran yang punya arah",
      r"""<p>Kecepatan angin, gaya pada jembatan, gradien loss di machine learning: semuanya butuh <b>besar</b> dan <b>arah</b>. Itulah vektor.
      Matriks adalah tabel bilangan yang bisa mengubah vektor: memutar, meregang, atau memproyeksikannya.</p>
      <p>Di Kalkulus 3 (Level 4), turunan fungsi banyak variabel berbentuk vektor (gradien), dan perubahan koordinat memakai matriks (Jacobian).</p>""",
      "Bayangkan vektor sebagai panah yang boleh digeser ke mana saja asal panjang dan arahnya sama."),
    S("theorem", "Operasi vektor",
      r"""<p>Untuk $\mathbf{u} = \langle u_1, u_2 \rangle$, $\mathbf{v} = \langle v_1, v_2 \rangle$:</p>
      <ul class="lesson-list">
        <li>Jumlah: $\mathbf{u} + \mathbf{v} = \langle u_1 + v_1,\ u_2 + v_2 \rangle$; skalar: $c\mathbf{u} = \langle cu_1, cu_2 \rangle$.</li>
        <li>Panjang: $\|\mathbf{u}\| = \sqrt{u_1^2 + u_2^2}$; vektor satuan $\hat{\mathbf{u}} = \dfrac{\mathbf{u}}{\|\mathbf{u}\|}$.</li>
        <li>Hasil kali titik: $\mathbf{u}\cdot\mathbf{v} = u_1v_1 + u_2v_2 = \|\mathbf{u}\|\|\mathbf{v}\|\cos\theta$.</li>
        <li>$\mathbf{u} \perp \mathbf{v} \iff \mathbf{u}\cdot\mathbf{v} = 0$.</li>
        <li>Proyeksi: $\operatorname{proj}_{\mathbf{v}}\mathbf{u} = \dfrac{\mathbf{u}\cdot\mathbf{v}}{\|\mathbf{v}\|^2}\mathbf{v}$.</li>
      </ul>""",
      "Dot product besar dan positif = searah, nol = tegak lurus, negatif = berlawanan arah. Ini intuisi kemiripan kosinus di ML.",
      [g("Sudut antara u = ⟨2, 1⟩ dan v = ⟨cos t, sin t⟩·3", [-4, 4], [-4, 4], [param("t", "Sudut v (rad)", 0, 6.28, 0.05, 1.2, "t")],
         [{"type": "segment", "x1": 0, "y1": 0, "x2": 2, "y2": 1, "color": "blue", "width": 4},
          {"type": "segment", "x1": 0, "y1": 0, "x2": "3*cos(t)", "y2": "3*sin(t)", "color": "orange", "width": 4},
          {"type": "point", "x": 2, "y": 1, "color": "blue"}, {"type": "point", "x": "3*cos(t)", "y": "3*sin(t)", "color": "orange"}],
         [readout("u·v", "2*3*cos(t)+1*3*sin(t)", 3), readout("cos θ", "(6*cos(t)+3*sin(t))/(3*sqrt(5))", 3)],
         "Cari posisi saat u·v = 0: kedua panah tegak lurus.")]),
    S("theorem", "Matriks 2×2 dan determinan",
      r"""<p>$$A = \begin{pmatrix} a & b \\ c & d \end{pmatrix}, \qquad A\mathbf{x} = \begin{pmatrix} a x_1 + b x_2 \\ c x_1 + d x_2 \end{pmatrix}$$</p>
      <p>Perkalian $AB$: baris $A$ dikali kolom $B$. Umumnya $AB \ne BA$.</p>
      <p>$$\det A = ad - bc, \qquad A^{-1} = \frac{1}{ad - bc}\begin{pmatrix} d & -b \\ -c & a \end{pmatrix} \ (\det A \ne 0)$$</p>
      <p>$|\det A|$ = faktor perubahan luas oleh transformasi $A$. Determinan nol berarti bidang "gepeng" jadi garis, sehingga tidak bisa dibalik.</p>""",
      "Determinan itu faktor skala luas. Ide ini nanti muncul lagi persis di Jacobian integral lipat."),
    S("example", "Bedah soal: sudut vektor & sistem persamaan",
      r"""<p><b>Soal 1.</b> Sudut antara $\mathbf{u} = \langle 1, 2 \rangle$ dan $\mathbf{v} = \langle 3, -1 \rangle$?</p>""" +
      steps(r"$\mathbf{u}\cdot\mathbf{v} = 3 - 2 = 1$.",
            r"$\|\mathbf{u}\| = \sqrt5$, $\|\mathbf{v}\| = \sqrt{10}$, jadi $\cos\theta = \dfrac{1}{\sqrt{50}} = \dfrac{1}{5\sqrt2}$.",
            r"$\theta = \arccos\dfrac{1}{5\sqrt2} \approx 81.9^\circ$.") +
      r"""<p><b>Soal 2.</b> Selesaikan $\begin{cases} 2x + y = 5 \\ x - 3y = -1 \end{cases}$ dengan invers matriks.</p>""" +
      steps(r"$A = \begin{pmatrix} 2 & 1 \\ 1 & -3 \end{pmatrix}$, $\det A = -6 - 1 = -7$.",
            r"$A^{-1} = -\tfrac17\begin{pmatrix} -3 & -1 \\ -1 & 2 \end{pmatrix}$.",
            r"$\begin{pmatrix} x \\ y \end{pmatrix} = A^{-1}\begin{pmatrix} 5 \\ -1 \end{pmatrix} = -\tfrac17\begin{pmatrix} -14 \\ -7 \end{pmatrix} = \begin{pmatrix} 2 \\ 1 \end{pmatrix}$."),
      "Selalu cek jawaban sistem persamaan dengan substitusi balik: 2(2) + 1 = 5 dan 2 − 3 = −1. Cocok."),
    S("pitfall", "Jebakan ujian",
      r"""<ul class="lesson-list">
        <li>$AB \ne BA$. Urutan perkalian matriks penting.</li>
        <li>$\|\mathbf{u} + \mathbf{v}\| \ne \|\mathbf{u}\| + \|\mathbf{v}\|$ pada umumnya (hanya $\le$, ketaksamaan segitiga).</li>
        <li>Hasil dot product adalah <b>skalar</b>, bukan vektor.</li>
        <li>Lupa tanda di invers $2\times2$: tukar $a, d$, <b>negasikan</b> $b, c$, bagi determinan.</li>
        <li>Mengalikan matriks berukuran tidak cocok: $(m\times n)(p\times q)$ butuh $n = p$.</li>
      </ul>""",
      "Rumus invers 2×2: 'tukar diagonal utama, negasikan diagonal lain, bagi determinan'. Ucapkan tiga kali."),
    S("checkpoint", "Mini checkpoint",
      qa(r"1. Untuk $k$ berapa $\langle k, 2 \rangle \perp \langle 3, -6 \rangle$?", r"<p>$3k - 12 = 0 \Rightarrow k = 4$.</p>") +
      qa(r"2. $\det\begin{pmatrix} 4 & 2 \\ 6 & 3 \end{pmatrix}$ dan artinya?", r"<p>$12 - 12 = 0$: matriks singular, tidak punya invers (kolomnya sejajar).</p>"),
      "Determinan nol = baris/kolom saling kelipatan. Lihat: (6, 3) = 1,5 × (4, 2)."),
]

SLIDES = {
    "pre-bilangan-real": BILANGAN_REAL,
    "pre-pertidaksamaan": PERTIDAKSAMAAN,
    "pre-konsep-fungsi": FUNGSI,
    "pre-fungsi-invers": INVERS,
    "pre-polinomial-rasional": POLINOMIAL,
    "pre-fungsi-trigonometri": TRIGONOMETRI,
    "pre-fungsi-eksponensial": EKSPONENSIAL,
    "pre-barisan-sigma": BARISAN,
    "pre-vektor-matriks": VEKTOR,
}

# Topik baru (materi saja; latihan menyusul) — disisipkan setelah topik `after` di skill tree.
NEW_TOPICS = [
    {"after": "pre-konsep-fungsi", "slug": "pre-fungsi-invers", "title": "Fungsi Invers", "icon": "m-mapping",
     "summary": "Fungsi satu-satu, uji garis horizontal, mencari rumus invers.", "references": "Stewart §1.5; Purcell §0.6; OpenStax Vol 1 §1.4"},
    {"after": "pre-fungsi-kuadrat", "slug": "pre-polinomial-rasional", "title": "Polinomial & Fungsi Rasional", "icon": "m-asymptote",
     "summary": "Teorema sisa & faktor, akar rasional, asimtot dan lubang.", "references": "Stewart Lamp. & §1.2; OpenStax Precalculus Bab 5"},
    {"after": "pre-fungsi-logaritma", "slug": "pre-barisan-sigma", "title": "Barisan & Notasi Sigma", "icon": "Σ",
     "summary": "Barisan aritmetika & geometri, sifat sigma, deret teleskopik.", "references": "Stewart Lamp. E; Purcell §4.1"},
    {"after": "pre-barisan-sigma", "slug": "pre-vektor-matriks", "title": "Pengantar Vektor & Matriks Dasar", "icon": "m-vector-field",
     "summary": "Operasi vektor, hasil kali titik, matriks 2×2, determinan & invers.", "references": "Stewart §12.2–12.3; OpenStax Vol 3 §2.1–2.3"},
]
