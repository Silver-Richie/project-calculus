r"""
Kurikulum v2 — Batch 3 (bagian C): slide Level 3, barisan & deret tak hingga.

Topik: Barisan & Uji Konvergensi Deret · Deret Pangkat, Taylor & Maclaurin.
Keduanya topik terpadat Kalkulus 2, jadi diberi pohon keputusan ("uji mana yang dipakai?",
"bagaimana mendapat deret suatu fungsi?") dan banyak bedah soal.

Rujukan: Purcell Jil. 2 Bab 9; Stewart 9e §11.1–11.11; OpenStax Calculus Vol 2 Bab 5–6.
"""

from ..helpers import param, readout
from .l1_slides import S, g, note, qa, steps
from .l3_slides import pohon

# ═══════════════════════════════════════════════════════════════════════════
# 11. Barisan & Uji Konvergensi Deret
# ═══════════════════════════════════════════════════════════════════════════
DERET_UJI = [
    S("intuition", "Menjumlahkan tak hingga banyak suku",
      r"""<p>Berjalan setengah jarak ke pintu, lalu setengah sisanya, dan seterusnya: $\tfrac12 + \tfrac14 + \tfrac18 + \dots = 1$. Tak hingga suku, jumlahnya berhingga.
      Tetapi deret harmonik $1 + \tfrac12 + \tfrac13 + \dots$ yang sukunya juga mengecil ke nol ternyata <b>tak terbatas</b>.</p>
      <p>Pertanyaan utama topik ini: <b>kapan</b> jumlah tak hingga itu konvergen? Jawabannya dipakai untuk analisis algoritma
      (rata-rata perbandingan quicksort sebanding dengan $\sum\tfrac1k \approx \ln n$), galat metode numerik, dan pemrosesan sinyal.</p>""",
      "Suku menuju nol itu SYARAT PERLU, bukan syarat cukup. Deret harmonik adalah bukti terkenalnya.",
      [g("Jumlah parsial Sₙ dari Σ 1/kᵖ", [0, 62], [0, 5.5],
         [param("p", "Pangkat p", 0.5, 3, 0.1, 1, "p"), param("N", "Banyak suku N", 2, 60, 1, 30, "N")],
         [{"type": "iter", "id": "P", "init": {"n": 1, "s": 1}, "update": {"n": "n + 1", "s": "s + 1/pow(n + 1, p)"}, "steps": "N - 1", "color": "blue"},
          {"type": "fn", "expr": "ln(x) + 0.5772", "from": 1, "color": "orange", "dash": True, "label": "ln n + γ"},
          {"type": "hline", "y": "pi*pi/6", "color": "green", "dash": True}],
         [readout("S_N", "P.s", 5), readout("π²/6 (batas untuk p = 2)", "pi*pi/6", 5)],
         "p = 1: titik biru mengikuti ln n dan terus naik. p = 2: titik biru mendatar di garis hijau π²/6.")]),
    S("theorem", "Barisan, deret, dan tiga deret patokan",
      r"""<p>Deret $\sum_{n=1}^\infty a_n$ <b>konvergen</b> ke $S$ jika barisan jumlah parsial $S_N = \sum_{n=1}^{N}a_n$ menuju $S$.</p>
      <ul class="lesson-list">
        <li><b>Geometri:</b> $\displaystyle\sum_{n=1}^\infty ar^{n-1} = \frac{a}{1 - r}$ jika $|r| &lt; 1$; divergen jika $|r| \ge 1$.</li>
        <li><b>Teleskopik:</b> $\displaystyle\sum_{n=1}^\infty\frac{1}{n(n + 1)} = \sum\left(\frac1n - \frac{1}{n + 1}\right)$; suku tengah saling hapus, $S_N = 1 - \frac{1}{N + 1} \to 1$.</li>
        <li><b>Harmonik</b> divergen: $1 + \tfrac12 + \left(\tfrac13 + \tfrac14\right) + \left(\tfrac15 + \dots + \tfrac18\right) + \dots \ge 1 + \tfrac12 + \tfrac12 + \tfrac12 + \dots$</li>
      </ul>""",
      "Deret geometri dan deret-p adalah 'deret patokan'. Hampir semua uji perbandingan memakai salah satu dari keduanya."),
    S("theorem", "Uji suku ke-n, uji integral, dan deret-p",
      r"""<p><b>Uji suku ke-$n$ (uji divergensi):</b> jika $\displaystyle\lim_{n \to \infty}a_n \ne 0$ (atau tidak ada), maka $\sum a_n$ <b>divergen</b>.
      Jika limitnya $0$, uji ini tidak menyimpulkan apa pun.</p>
      <p><b>Uji integral:</b> jika $f$ positif, kontinu, dan turun pada $[1, \infty)$ dengan $a_n = f(n)$, maka
      $$\sum_{n=1}^\infty a_n \text{ dan } \int_1^\infty f(x)\,dx \text{ sama-sama konvergen atau sama-sama divergen.}$$</p>
      <p><b>Deret-$p$:</b> $\displaystyle\sum\frac{1}{n^p}$ konvergen $\iff p &gt; 1$ (langsung dari uji integral dan uji-$p$ integral tak wajar).</p>""",
      "Uji suku ke-n hanya bisa berkata 'DIVERGEN'. Ia tidak pernah membuktikan konvergen."),
    S("theorem", "Uji perbandingan & limit perbandingan",
      r"""<p>Untuk deret bersuku <b>positif</b>:</p>
      <ul class="lesson-list">
        <li><b>Perbandingan langsung:</b> $0 \le a_n \le b_n$. Jika $\sum b_n$ konvergen maka $\sum a_n$ konvergen; jika $\sum a_n$ divergen maka $\sum b_n$ divergen.</li>
        <li><b>Limit perbandingan:</b> jika $\displaystyle\lim_{n \to \infty}\frac{a_n}{b_n} = L$ dengan $0 &lt; L &lt; \infty$, keduanya berperilaku sama.</li>
      </ul>
      <p><b>Cara memilih $b_n$:</b> ambil suku dominan pembilang dan penyebut.</p>""" +
      steps(r"$\displaystyle\sum\frac{3n^2 + 1}{n^4 + 5}$: dominan $\dfrac{3n^2}{n^4}$, jadi bandingkan dengan $b_n = \dfrac{1}{n^2}$.",
            r"$\dfrac{a_n}{b_n} = \dfrac{3n^4 + n^2}{n^4 + 5} \to 3$, dan $\sum\tfrac{1}{n^2}$ konvergen ($p = 2$). Jadi konvergen.",
            r"$\displaystyle\sum\frac{1}{\sqrt{n} + 1}$: bandingkan dengan $\tfrac{1}{\sqrt n}$, $L = 1$, deret-$p$ dengan $p = \tfrac12$ divergen. Jadi divergen."),
      "Limit perbandingan lebih ramah daripada perbandingan langsung: kamu tidak perlu membuktikan ketaksamaan, cukup hitung limit."),
    S("theorem", "Uji rasio & uji akar",
      r"""<p>Hitung
      $$L = \lim_{n \to \infty}\left|\frac{a_{n+1}}{a_n}\right| \quad\text{(rasio)} \qquad\text{atau}\qquad L = \lim_{n \to \infty}\sqrt[n]{|a_n|}\quad\text{(akar)}.$$</p>
      <ul class="lesson-list">
        <li>$L &lt; 1$ → konvergen <b>mutlak</b>.</li>
        <li>$L &gt; 1$ atau $L = \infty$ → divergen.</li>
        <li>$L = 1$ → <b>tidak dapat disimpulkan</b>; pakai uji lain.</li>
      </ul>
      <p><b>Contoh.</b> $\displaystyle\sum\frac{2^n}{n!}$: $\ \dfrac{a_{n+1}}{a_n} = \dfrac{2^{n+1}}{(n + 1)!}\cdot\dfrac{n!}{2^n} = \dfrac{2}{n + 1} \to 0 &lt; 1$. Konvergen (jumlahnya $e^2 - 1$).</p>""",
      "Uji rasio paling bersinar saat ada n! atau aⁿ, karena rasionya saling coret dengan rapi."),
    S("theorem", "Deret ganti tanda, konvergen mutlak & bersyarat",
      r"""<p><b>Uji deret ganti tanda (Leibniz):</b> jika $b_n &gt; 0$, $b_{n+1} \le b_n$, dan $b_n \to 0$, maka $\sum(-1)^{n-1}b_n$ konvergen, dengan taksiran galat
      $$|S - S_N| \le b_{N+1}.$$</p>
      <ul class="lesson-list">
        <li><b>Konvergen mutlak:</b> $\sum|a_n|$ konvergen. Ini menjamin $\sum a_n$ konvergen.</li>
        <li><b>Konvergen bersyarat:</b> $\sum a_n$ konvergen tetapi $\sum|a_n|$ divergen. Contoh: $1 - \tfrac12 + \tfrac13 - \dots = \ln 2$.</li>
      </ul>""" +
      note(r"Fakta mengejutkan (Riemann): suku deret konvergen bersyarat bisa disusun ulang sehingga jumlahnya menjadi bilangan apa pun. Deret konvergen mutlak tidak punya masalah ini."),
      "Taksiran galat Leibniz sangat praktis: galat tidak lebih besar dari suku pertama yang kamu buang."),
    S("derivation", "Pohon keputusan: uji mana yang dipakai?",
      pohon(r"$\lim a_n \ne 0$? → <b>Divergen</b> (uji suku ke-$n$). Selesai.",
            r"Deret patokan? Geometri $\sum ar^n$ (cek $|r| &lt; 1$), deret-$p$ $\sum\tfrac{1}{n^p}$ (cek $p &gt; 1$), atau teleskopik (pecahan parsial).",
            r"Ada $(-1)^n$? Cek konvergen mutlak dulu dengan uji lain. Jika tidak mutlak, pakai Leibniz → konvergen bersyarat.",
            r"Ada $n!$, $a^n$, atau $n^n$? → <b>Uji rasio</b>.",
            r"Seluruh suku berbentuk $(\dots)^n$? → <b>Uji akar</b>.",
            r"Fungsi rasional atau akar dari $n$? → <b>Limit perbandingan</b> dengan suku dominan $\tfrac{1}{n^p}$.",
            r"$a_n = f(n)$ dengan $f$ turun dan mudah diintegralkan, seperti $\tfrac{1}{n\ln n}$ atau $\tfrac{\ln n}{n^2}$? → <b>Uji integral</b>.") +
      r"""<div class="table-scroll"><table class="lesson-table"><thead><tr><th></th><th>Uji rasio</th><th>Uji integral</th></tr></thead><tbody>
        <tr><td>Cocok untuk</td><td>$n!$, $a^n$, $n^n$, deret pangkat</td><td>$\ln n$, $\tfrac{1}{n(\ln n)^p}$, fungsi turun yang bisa diintegralkan</td></tr>
        <tr><td>Gagal untuk</td><td>rasional dan deret-$p$ (selalu $L = 1$)</td><td>faktorial, suku tidak monoton, $\sin n$</td></tr>
        <tr><td>Hasil</td><td>konvergen <b>mutlak</b> atau divergen</td><td>konvergen atau divergen (suku positif)</td></tr>
      </tbody></table></div>""",
      "Uji rasio memberi L = 1 untuk SEMUA deret rasional. Jangan buang waktu: rasional → limit perbandingan."),
    S("example", "Bedah soal: pilih uji yang tepat",
      r"""<div class="table-scroll"><table class="lesson-table"><thead><tr><th>Deret</th><th>Ciri</th><th>Uji</th><th>Kesimpulan</th></tr></thead><tbody>
        <tr><td>$\sum\dfrac{n}{2n + 1}$</td><td>$a_n \to \tfrac12$</td><td>suku ke-$n$</td><td>divergen</td></tr>
        <tr><td>$\sum\dfrac{n^2}{3^n}$</td><td>ada $3^n$</td><td>rasio: $L = \tfrac13$</td><td>konvergen</td></tr>
        <tr><td>$\sum_{n \ge 2}\dfrac{1}{n\ln n}$</td><td>ada $\ln n$</td><td>integral: $\ln(\ln x) \to \infty$</td><td>divergen</td></tr>
        <tr><td>$\sum\dfrac{(-1)^n}{\sqrt n}$</td><td>ganti tanda</td><td>mutlak: $p = \tfrac12$ gagal; Leibniz</td><td>konvergen bersyarat</td></tr>
        <tr><td>$\sum\left(\dfrac{2n + 1}{3n + 2}\right)^n$</td><td>pangkat $n$</td><td>akar: $L = \tfrac23$</td><td>konvergen</td></tr>
      </tbody></table></div>
      <p><b>Rinci:</b> $\displaystyle\sum\frac{n!}{n^n}$.</p>""" +
      steps(r"Ada $n!$ dan $n^n$ → uji rasio.",
            r"$\dfrac{a_{n+1}}{a_n} = \dfrac{(n + 1)!}{(n + 1)^{n+1}}\cdot\dfrac{n^n}{n!} = \dfrac{n^n}{(n + 1)^n} = \left(\dfrac{n}{n + 1}\right)^n$.",
            r"$\left(1 + \tfrac1n\right)^{-n} \to e^{-1} \approx 0.37 &lt; 1$. Konvergen (mutlak)."),
      "Tuliskan 'ciri' sebelum memilih uji, persis seperti kolom kedua tabel. Ciri menentukan uji, bukan tebakan."),
    S("pitfall", "Jebakan ujian",
      r"""<ul class="lesson-list">
        <li>"$a_n \to 0$, jadi konvergen." Salah, lihat deret harmonik.</li>
        <li>Uji rasio memberi $L = 1$, lalu disimpulkan konvergen atau divergen. Seharusnya: tidak dapat disimpulkan.</li>
        <li>Perbandingan ke arah salah: "lebih kecil dari deret divergen" tidak menyimpulkan apa pun.</li>
        <li>Leibniz tanpa mengecek $b_n$ turun dan menuju $0$.</li>
        <li>Mencampur limit <b>barisan</b> $a_n$ dengan jumlah <b>deret</b> $\sum a_n$.</li>
        <li>Deret geometri yang dimulai dari $n = 0$ vs $n = 1$: suku pertama $a$ berbeda, rumus $\tfrac{a}{1 - r}$ memakai suku pertama yang sebenarnya.</li>
      </ul>""",
      "Tulis kesimpulan lengkap: nama uji, nilai L atau pembanding, dan kata 'konvergen/divergen'. Dosen menilai alasannya, bukan hanya jawabannya."),
    S("checkpoint", "Mini checkpoint",
      qa(r"1. $\displaystyle\sum\frac{3^n}{n!}$", r"<p>Rasio: $\tfrac{3}{n + 1} \to 0$. Konvergen (mutlak).</p>") +
      qa(r"2. $\displaystyle\sum\frac{n + 1}{n^2\sqrt n}$", r"<p>Suku dominan $\tfrac{n}{n^{5/2}} = \tfrac{1}{n^{3/2}}$; limit perbandingan $L = 1$, $p = \tfrac32 &gt; 1$. Konvergen.</p>") +
      qa(r"3. $\displaystyle\sum(-1)^n\frac{n}{n + 1}$", r"<p>Suku tidak menuju $0$ ($|a_n| \to 1$), jadi divergen. Leibniz tidak perlu dicoba.</p>"),
      "Soal 3 menguji urutan pohon keputusan: cek suku ke-n DULU, sebelum tergoda memakai Leibniz."),
]

# ═══════════════════════════════════════════════════════════════════════════
# 12. Deret Pangkat, Taylor & Maclaurin
# ═══════════════════════════════════════════════════════════════════════════
DERET_PANGKAT = [
    S("intuition", "Fungsi rumit sebagai polinom tak hingga",
      r"""<p>Kalkulator dan pustaka matematika di komputer tidak "tahu" $\sin x$ atau $e^x$. Mereka menghitung <b>polinom</b> yang sangat mirip fungsi itu.
      Fisikawan memakai ide yang sama: untuk sudut kecil $\sin\theta \approx \theta$ (bandul sederhana), dan untuk kecepatan rendah
      rumus relativitas Einstein menyusut menjadi energi kinetik $\tfrac12mv^2$.</p>
      <p>Deret Taylor menjawab: polinom mana yang <b>paling mirip</b> dengan sebuah fungsi di sekitar satu titik?</p>""",
      "Tambah suku N di grafik. Tiap suku baru 'menempelkan' polinom ke sin x sedikit lebih jauh dari 0.",
      [g("Polinom Taylor sin x: x − x³/3! + x⁵/5! − …", [-10, 10], [-3, 3],
         [param("N", "Banyak suku (N + 1)", 0, 8, 1, 2, "N"), param("X", "Titik x", -9, 9, 0.1, 3, "x")],
         [{"type": "fn", "expr": "sin(x)", "color": "blue", "label": "sin x"},
          {"type": "fn", "expr": "sum(0, N, k => pow(-1, k)*pow(x, 2*k + 1)/fact(2*k + 1))", "color": "red", "label": "polinom Taylor"},
          {"type": "point", "x": "X", "y": "sin(X)", "color": "blue"}],
         [readout("Derajat polinom", "2*N + 1", 0), readout("sin x", "sin(X)", 5),
          readout("Polinom di x", "sum(0, N, k => pow(-1, k)*pow(X, 2*k + 1)/fact(2*k + 1))", 5)],
         "Hampiran sangat baik di dekat 0 dan memburuk jauh dari 0. Itulah sifat lokal deret Taylor.")]),
    S("theorem", "Deret pangkat & jari-jari konvergensi",
      r"""<p>Deret pangkat di sekitar $a$: $\displaystyle\sum_{n=0}^{\infty}c_n(x - a)^n$. Selalu tepat satu dari tiga kemungkinan:</p>
      <ul class="lesson-list">
        <li>konvergen hanya di $x = a$ ($R = 0$);</li>
        <li>konvergen untuk semua $x$ ($R = \infty$);</li>
        <li>ada $R &gt; 0$: konvergen mutlak untuk $|x - a| &lt; R$, divergen untuk $|x - a| &gt; R$. Ujung $x = a \pm R$ harus <b>dicek terpisah</b>.</li>
      </ul>
      <p>$R$ dicari dengan uji rasio: tuntut $\displaystyle\lim\left|\frac{a_{n+1}}{a_n}\right| &lt; 1$ dengan $a_n = c_n(x - a)^n$.</p>""",
      "Contoh terpenting: 1/(1 − x) = 1 + x + x² + … hanya untuk |x| < 1. Geser N: di luar (−1, 1) polinomnya meledak.",
      [g("1/(1 − x) dan jumlah parsial 1 + x + … + xᴺ", [-1.6, 1.6], [-3, 8], [param("N", "Derajat N", 1, 30, 1, 5, "N")],
         [{"type": "fn", "expr": "1/(1 - x)", "color": "blue", "label": "1/(1 − x)"},
          {"type": "fn", "expr": "sum(0, N, k => pow(x, k))", "color": "red", "label": "jumlah parsial"},
          {"type": "vband", "from": -1, "to": 1, "color": "green", "opacity": 0.08}],
         [], "Pita hijau = interval konvergensi (−1, 1). Di luarnya, jumlah parsial menjauh dari fungsi.")]),
    S("example", "Bedah soal: interval konvergensi",
      r"""<p><b>Soal.</b> Interval konvergensi $\displaystyle\sum_{n=1}^\infty\frac{(x - 3)^n}{n\,2^n}$.</p>""" +
      steps(r"Uji rasio: $\left|\dfrac{(x - 3)^{n+1}}{(n + 1)2^{n+1}}\cdot\dfrac{n\,2^n}{(x - 3)^n}\right| = \dfrac{n}{n + 1}\cdot\dfrac{|x - 3|}{2} \to \dfrac{|x - 3|}{2}$.",
            r"Konvergen jika $\tfrac{|x - 3|}{2} &lt; 1$, yaitu $1 &lt; x &lt; 5$. Jari-jari $R = 2$.",
            r"Ujung $x = 5$: $\sum\tfrac{2^n}{n2^n} = \sum\tfrac1n$, harmonik, divergen.",
            r"Ujung $x = 1$: $\sum\tfrac{(-1)^n}{n}$, Leibniz, konvergen.",
            r"Interval konvergensi: $[1, 5)$.") +
      note(r"Pembanding cepat: $\sum\tfrac{x^n}{n!}$ punya $R = \infty$ (rasio $\tfrac{|x|}{n + 1} \to 0$), sedangkan $\sum n!\,x^n$ punya $R = 0$."),
      "Uji rasio TIDAK berlaku di ujung interval (di sana L = 1). Itulah alasan ujung selalu dicek dengan uji lain."),
    S("theorem", "Deret Taylor & Maclaurin",
      r"""<p>Jika $f$ punya deret pangkat di sekitar $a$, koefisiennya pasti
      $$f(x) = \sum_{n=0}^{\infty}\frac{f^{(n)}(a)}{n!}(x - a)^n = f(a) + f'(a)(x - a) + \frac{f''(a)}{2!}(x - a)^2 + \dots$$
      Untuk $a = 0$ disebut deret <b>Maclaurin</b>.</p>
      <p><b>Mengapa $n!$?</b> Turunkan $f(x) = c_0 + c_1(x - a) + c_2(x - a)^2 + \dots$ sebanyak $n$ kali lalu masukkan $x = a$:
      semua suku lenyap kecuali $n!\,c_n$, sehingga $c_n = \dfrac{f^{(n)}(a)}{n!}$.</p>
      <p>Polinom Taylor derajat $n$, $T_n(x)$, adalah potongan deret sampai suku ke-$n$. $T_1$ tidak lain adalah garis singgung (linearisasi).</p>""",
      "T₁ = garis singgung, T₂ = parabola yang juga cocok kelengkungannya. Taylor adalah generalisasi linearisasi."),
    S("theorem", "Tabel Maclaurin penting & operasi suku demi suku",
      r"""<div class="table-scroll"><table class="lesson-table"><thead><tr><th>Fungsi</th><th>Deret</th><th>Berlaku</th></tr></thead><tbody>
        <tr><td>$\dfrac{1}{1 - x}$</td><td>$\sum x^n = 1 + x + x^2 + \dots$</td><td>$|x| &lt; 1$</td></tr>
        <tr><td>$e^x$</td><td>$\sum\dfrac{x^n}{n!} = 1 + x + \dfrac{x^2}{2!} + \dots$</td><td>semua $x$</td></tr>
        <tr><td>$\sin x$</td><td>$\sum\dfrac{(-1)^n x^{2n+1}}{(2n + 1)!} = x - \dfrac{x^3}{3!} + \dots$</td><td>semua $x$</td></tr>
        <tr><td>$\cos x$</td><td>$\sum\dfrac{(-1)^n x^{2n}}{(2n)!} = 1 - \dfrac{x^2}{2!} + \dots$</td><td>semua $x$</td></tr>
        <tr><td>$\ln(1 + x)$</td><td>$\sum_{n \ge 1}\dfrac{(-1)^{n-1}x^n}{n} = x - \dfrac{x^2}{2} + \dots$</td><td>$-1 &lt; x \le 1$</td></tr>
        <tr><td>$\arctan x$</td><td>$\sum\dfrac{(-1)^n x^{2n+1}}{2n + 1} = x - \dfrac{x^3}{3} + \dots$</td><td>$|x| \le 1$</td></tr>
        <tr><td>$(1 + x)^k$</td><td>$\sum\dbinom{k}{n}x^n = 1 + kx + \dfrac{k(k - 1)}{2!}x^2 + \dots$</td><td>$|x| &lt; 1$</td></tr>
      </tbody></table></div>
      <p>Di dalam interval konvergensi, deret boleh <b>diturunkan dan diintegralkan suku demi suku</b> (jari-jari tetap sama). Contoh:
      $\tfrac{1}{1 + x^2} = \sum(-1)^nx^{2n}$, diintegralkan menjadi deret $\arctan x$; di $x = 1$ menghasilkan $\tfrac{\pi}{4} = 1 - \tfrac13 + \tfrac15 - \dots$</p>""",
      "Hafalkan empat baris pertama dengan sungguh-sungguh. Sisanya bisa diturunkan dari deret geometri dan binomial."),
    S("derivation", "Pohon keputusan: mencari deret suatu fungsi",
      pohon(r"Fungsinya hasil substitusi dari tabel, misalnya $e^{-x^2}$, $\sin 2x$, $\tfrac{1}{1 + 4x}$? → <b>substitusi</b> ke deret yang sudah dikenal.",
            r"Ada faktor $x^k$ di depan, misalnya $x^2\cos x$? → kalikan deret tabel dengan $x^k$.",
            r"Bentuk rasional $\tfrac{c}{a - bx}$? → manipulasi menjadi $\tfrac{c}{a}\cdot\tfrac{1}{1 - (bx/a)}$, deret geometri. Pecahan parsial dulu bila penyebutnya berderajat dua.",
            r"Fungsinya turunan atau integral dari fungsi yang dikenal ($\ln$, $\arctan$, $\tfrac{1}{(1 - x)^2}$)? → <b>turunkan atau integralkan</b> suku demi suku.",
            r"Tidak ada jalan pintas, atau diminta di sekitar $a \ne 0$? → hitung $f^{(n)}(a)$ dan pakai rumus Taylor langsung.") +
      note(r"Contoh cepat: $e^{-x^2} = \sum\dfrac{(-1)^nx^{2n}}{n!}$ (substitusi $x \to -x^2$). Contoh lain: $\dfrac{1}{(1 - x)^2} = \dfrac{d}{dx}\dfrac{1}{1 - x} = \sum n x^{n-1}$."),
      "Rumus Taylor langsung adalah jalan terakhir. Menurunkan f sampai n kali sering panjang dan rawan salah."),
    S("example", "Bedah soal: integral & limit dengan deret",
      r"""<p><b>Soal 1.</b> Taksir $\displaystyle\int_0^1 e^{-x^2}dx$ dengan galat $&lt; 0.001$ (tidak punya antiturunan elementer).</p>""" +
      steps(r"$e^{-x^2} = 1 - x^2 + \dfrac{x^4}{2!} - \dfrac{x^6}{3!} + \dots$",
            r"Integralkan suku demi suku: $\displaystyle\int_0^1 e^{-x^2}dx = 1 - \frac13 + \frac{1}{10} - \frac{1}{42} + \frac{1}{216} - \frac{1}{1320} + \dots$",
            r"Deret ganti tanda: galat $\le$ suku pertama yang dibuang. Suku $\tfrac{1}{1320} \approx 0.00076 &lt; 0.001$.",
            r"Ambil lima suku: $1 - 0.33333 + 0.1 - 0.02381 + 0.00463 \approx 0.7475$ (nilai sebenarnya $0.74682\dots$).") +
      r"""<p><b>Soal 2.</b> $\displaystyle\lim_{x \to 0}\frac{\sin x - x}{x^3}$.</p>""" +
      steps(r"$\sin x - x = -\dfrac{x^3}{6} + \dfrac{x^5}{120} - \dots$",
            r"Bagi $x^3$: $-\dfrac16 + \dfrac{x^2}{120} - \dots \to -\dfrac16$. Tanpa tiga kali L'Hôpital."),
      "Integral e^(−x²) adalah inti distribusi normal. Begitulah tabel-z statistik dihitung sebelum ada komputer."),
    S("example", "Bedah soal: sisa Taylor & ketelitian aproksimasi",
      r"""<p><b>Ketaksamaan Taylor:</b> jika $|f^{(n+1)}(x)| \le M$ di antara $a$ dan $x$, maka
      $$|R_n(x)| = |f(x) - T_n(x)| \le \frac{M}{(n + 1)!}|x - a|^{n+1}.$$</p>
      <p><b>Soal.</b> Taksir $\sqrt{4.1}$ dengan $T_2$ di sekitar $a = 4$ dan batasi galatnya.</p>""" +
      steps(r"$f = \sqrt x$: $f(4) = 2$, $f'(4) = \tfrac{1}{2\sqrt4} = \tfrac14$, $f''(4) = -\tfrac14\cdot 4^{-3/2} = -\tfrac{1}{32}$.",
            r"$T_2(x) = 2 + \dfrac{x - 4}{4} - \dfrac{(x - 4)^2}{64}$, sehingga $\sqrt{4.1} \approx 2 + 0.025 - 0.00015625 = 2.02484$.",
            r"$f'''(x) = \tfrac38x^{-5/2} \le \tfrac38\cdot 4^{-5/2} = \tfrac{3}{256}$ pada $[4, 4.1]$.",
            r"$|R_2| \le \dfrac{3/256}{3!}(0.1)^3 \approx 1.95\times10^{-6}$. Nilai sebenarnya $2.0248457\dots$, galat nyata $\approx 1.7\times10^{-6}$.") +
      note(r"Untuk bandul, $\sin\theta \approx \theta$ dengan galat $\le \tfrac{|\theta|^3}{6}$. Pada $\theta = 0.2$ rad (sekitar $11^\circ$) galatnya $&lt; 0.0014$."),
      "Pilih pusat a sedekat mungkin dengan x dan yang nilai turunannya mudah dihitung, seperti 4 untuk √4,1."),
    S("pitfall", "Jebakan ujian",
      r"""<ul class="lesson-list">
        <li>Lupa mengecek kedua ujung interval konvergensi, atau mengeceknya dengan uji rasio (pasti $L = 1$).</li>
        <li>Uji rasio pada deret pangkat tanpa nilai mutlak: harus $|x - a|$.</li>
        <li>Salah indeks faktorial: suku $\sin x$ memakai $(2n + 1)!$, bukan $(2n)!$.</li>
        <li>Substitusi tanpa menyesuaikan interval: $\tfrac{1}{1 + x^2} = \sum(-1)^nx^{2n}$ hanya untuk $|x| &lt; 1$, walau fungsinya terdefinisi di semua $x$.</li>
        <li>Menganggap deret Taylor selalu sama dengan fungsinya. Contoh FMIPA: $f(x) = e^{-1/x^2}$ ($f(0) = 0$) punya deret Maclaurin nol, padahal $f \ne 0$.</li>
        <li>Menulis $T_n$ dengan $f^{(n)}(x)$ alih-alih $f^{(n)}(a)$.</li>
      </ul>""",
      "Untuk menentukan suku umum, tulis tiga atau empat suku pertama secara eksplisit, lalu cari polanya. Jangan langsung menebak rumus."),
    S("checkpoint", "Mini checkpoint",
      qa(r"1. Deret Maclaurin $x\cos x$.", r"<p>$\displaystyle\sum_{n=0}^{\infty}\frac{(-1)^nx^{2n+1}}{(2n)!} = x - \frac{x^3}{2!} + \frac{x^5}{4!} - \dots$, berlaku untuk semua $x$.</p>") +
      qa(r"2. Interval konvergensi $\displaystyle\sum_{n=1}^\infty\frac{x^n}{n\,4^n}$.", r"<p>Rasio $\to \tfrac{|x|}{4}$, jadi $R = 4$. Di $x = 4$: harmonik, divergen; di $x = -4$: Leibniz, konvergen. Interval $[-4, 4)$.</p>") +
      qa(r"3. Nilai $\displaystyle\sum_{n=0}^\infty\frac{(-1)^n}{(2n + 1)!}$.", r"<p>Ini deret $\sin x$ di $x = 1$: jumlahnya $\sin 1 \approx 0.8415$.</p>"),
      "Soal 3 dibaca terbalik: kenali deret di tabel, lalu tebak fungsi dan nilai x-nya."),
]

SLIDES = {
    "km-der-uji": DERET_UJI,
    "km-der-pangkat": DERET_PANGKAT,
}
