r"""
Kurikulum v2 — Batch 2A: slide paruh pertama Level 2 (Kalkulus Dasar).

Topik: Intuisi Limit & Limit Sepihak · Hukum Limit & Bentuk Tak Tentu · Kontinuitas & Teorema Nilai Antara ·
Definisi Turunan & Garis Singgung. Alur sama dengan Batch 1 (l1_slides.py): intuisi & visual dulu, baru definisi
formal, eksplorasi grafik, bedah soal bertahap, jebakan ujian, mini checkpoint. Rumus LaTeX (KaTeX).

Rujukan: Purcell Jil. 1 Bab 1–2; Stewart 9e §2.1–2.8; OpenStax Calculus Vol 1 Bab 2–3.1; Whitman §2, §4.3.
"""

from ..helpers import param, readout
from .l1_slides import S, g, note, qa, steps

# ═══════════════════════════════════════════════════════════════════════════
# 1. Intuisi Limit & Limit Sepihak
# ═══════════════════════════════════════════════════════════════════════════
LIMIT_KONSEP = [
    S("intuition", "Mendekat tanpa harus menyentuh",
      r"""<p>Speedometer menunjukkan kecepatan <i>saat ini</i>, padahal kecepatan selalu dihitung dari jarak dibagi waktu.
      Kalau selang waktunya $0$, kita dapat $\tfrac{0}{0}$. Solusinya: lihat apa yang terjadi saat selang waktunya
      <b>makin kecil</b>, tanpa pernah benar-benar nol. Itulah ide limit.</p>
      <p>Contoh: $f(x) = \dfrac{x^2 - 1}{x - 1}$ tidak terdefinisi di $x = 1$. Tapi untuk $x$ dekat $1$, nilai $f(x)$ makin dekat ke $2$.
      Kita tulis $$\lim_{x \to 1} \frac{x^2 - 1}{x - 1} = 2.$$</p>""",
      "Limit menanyakan 'f(x) mendekati apa saat x mendekati a', BUKAN 'berapa f(a)'. Nilai di titik itu sendiri tidak dihitung."),
    S("intuition", "Eksplorasi: mendekati lubang dari dua arah",
      r"""<p>Geser $h$ makin kecil dan perhatikan nilai $f(1 - h)$ (dari kiri) dan $f(1 + h)$ (dari kanan).</p>
      <p>Grafiknya adalah garis $y = x + 1$ dengan <b>lubang</b> di $(1, 2)$: titik itu sendiri tidak ada, tapi semua titik di sekitarnya mengarah ke sana.</p>""",
      "Perhatikan dua readout di bawah: makin kecil h, keduanya makin rapat ke 2 dari arah yang berbeda.",
      [g("f(x) = (x² − 1)/(x − 1) di sekitar x = 1", [-1, 3], [0, 4], [param("h", "Jarak h ke 1", 0.01, 1, 0.01, 0.5, "h")],
         [{"type": "fn", "expr": "(x*x-1)/(x-1)", "color": "blue", "label": "f(x)"},
          {"type": "point", "x": "1-h", "y": "(pow(1-h,2)-1)/(-h)", "color": "orange"},
          {"type": "point", "x": "1+h", "y": "(pow(1+h,2)-1)/h", "color": "green"},
          {"type": "hline", "y": 2, "color": "red", "dash": True}],
         [readout("f(1 − h) (kiri)", "(pow(1-h,2)-1)/(-h)", 5), readout("f(1 + h) (kanan)", "(pow(1+h,2)-1)/h", 5)],
         "Lubang di (1, 2): f(1) tidak ada, tapi limitnya 2.")]),
    S("theorem", "Definisi intuitif & limit sepihak",
      r"""<p>$\displaystyle\lim_{x \to a} f(x) = L$ artinya $f(x)$ bisa dibuat sedekat apa pun ke $L$ dengan mengambil $x$ cukup dekat ke $a$ (tetapi $x \ne a$).</p>
      <ul class="lesson-list">
        <li>Limit kiri: $\displaystyle\lim_{x \to a^-} f(x)$, yaitu $x$ mendekati $a$ dari nilai yang lebih kecil.</li>
        <li>Limit kanan: $\displaystyle\lim_{x \to a^+} f(x)$, yaitu $x$ mendekati $a$ dari nilai yang lebih besar.</li>
      </ul>
      <p>$$\lim_{x \to a} f(x) = L \iff \lim_{x \to a^-} f(x) = L \ \text{ dan } \ \lim_{x \to a^+} f(x) = L$$</p>
      <p>Kalau limit kiri $\ne$ limit kanan, limit dua sisi <b>tidak ada</b>.</p>""",
      "Limit dua sisi itu seperti dua tim yang harus ketemu di titik yang sama. Beda titik pertemuan, limitnya gagal."),
    S("intuition", "Eksplorasi: lompatan pada fungsi sepotong-sepotong",
      r"""<p>Fungsi $f(x) = \begin{cases} x + 1 & x < 1 \\ x + 1 + j & x \ge 1 \end{cases}$ punya lompatan sebesar $j$ di $x = 1$.</p>
      <p>Limit kiri selalu $2$, limit kanan $2 + j$. Limit dua sisi hanya ada kalau $j = 0$.</p>""",
      "Coba set j = 0. Dua potong grafik menyambung, dan limit dua sisinya baru ada.",
      [g("Lompatan sebesar j di x = 1", [-2, 4], [-2, 6], [param("j", "Lompatan j", -2, 2, 0.25, 1, "j")],
         [{"type": "fn", "expr": "x < 1 ? x + 1 : x + 1 + j", "color": "blue", "label": "f(x)"},
          {"type": "point", "x": 1, "y": 2, "color": "orange"}, {"type": "point", "x": 1, "y": "2+j", "color": "green"}],
         [readout("Limit kiri", "2", 3), readout("Limit kanan", "2+j", 3)],
         "Titik oranye = arah kiri, titik hijau = arah kanan.")]),
    S("example", "Bedah soal: limit sepihak",
      r"""<p><b>Soal 1.</b> Tentukan $\displaystyle\lim_{x \to 0} \frac{|x|}{x}$.</p>""" +
      steps(r"Untuk $x > 0$: $|x| = x$, jadi $\dfrac{|x|}{x} = 1$. Limit kanan $= 1$.",
            r"Untuk $x < 0$: $|x| = -x$, jadi $\dfrac{|x|}{x} = -1$. Limit kiri $= -1$.",
            r"Kiri $\ne$ kanan, jadi $\displaystyle\lim_{x \to 0} \frac{|x|}{x}$ <b>tidak ada</b>.") +
      r"""<p><b>Soal 2.</b> $f(x) = \begin{cases} x^2 + 1 & x < 2 \\ 3x - 1 & x \ge 2 \end{cases}$. Hitung $\displaystyle\lim_{x \to 2} f(x)$.</p>""" +
      steps(r"Limit kiri: pakai potongan $x < 2$: $2^2 + 1 = 5$.",
            r"Limit kanan: pakai potongan $x \ge 2$: $3(2) - 1 = 5$.",
            r"Keduanya $5$, jadi $\displaystyle\lim_{x \to 2} f(x) = 5$."),
      "Soal fungsi sepotong-sepotong: SELALU hitung kiri dan kanan terpisah pakai potongan yang tepat."),
    S("example", "Bedah soal: limit tak hingga & asimtot tegak",
      r"""<p><b>Soal.</b> Tentukan $\displaystyle\lim_{x \to 3^-} \frac{2}{x - 3}$ dan $\displaystyle\lim_{x \to 3^+} \frac{2}{x - 3}$.</p>""" +
      steps(r"Dari kiri, $x - 3$ kecil dan <b>negatif</b>: pecahan menuju $-\infty$.",
            r"Dari kanan, $x - 3$ kecil dan <b>positif</b>: pecahan menuju $+\infty$.",
            r"Garis $x = 3$ adalah <b>asimtot tegak</b>. Limit dua sisi tidak ada (dan bukan $\infty$, karena tandanya beda).") +
      note(r"Menulis $\lim = \infty$ itu cara menjelaskan <i>bagaimana</i> limitnya gagal ada, bukan berarti limitnya adalah bilangan $\infty$."),
      "Trik tanda: substitusi angka sangat dekat, misalnya x = 2,999 dan 3,001, lalu lihat tanda penyebutnya."),
    S("pitfall", "Jebakan ujian",
      r"""<ul class="lesson-list">
        <li>Menyamakan $\lim_{x \to a} f(x)$ dengan $f(a)$. Limit boleh ada walau $f(a)$ tidak ada, dan sebaliknya.</li>
        <li>Menyimpulkan limit dari satu sisi saja.</li>
        <li>Percaya penuh pada tabel kalkulator. $\sin\!\left(\tfrac{\pi}{x}\right)$ di $x = 0.1, 0.01, 0.001$ semuanya $0$, padahal limitnya tidak ada (berosilasi).</li>
        <li>Menulis $\tfrac{2}{0} = \infty$. Pembagian dengan nol tidak terdefinisi; yang benar adalah analisis tanda limit sepihak.</li>
      </ul>""",
      "Jebakan sin(π/x) itu klasik: tabel bisa bohong kalau titik ujinya kebetulan 'beruntung'. Selalu cek dengan aljabar."),
    S("checkpoint", "Mini checkpoint",
      qa(r"1. $\displaystyle\lim_{x \to 4} \frac{x^2 - 16}{x - 4}$ = ?", r"<p>$\dfrac{(x - 4)(x + 4)}{x - 4} = x + 4 \to 8$.</p>") +
      qa(r"2. $f(x) = \lfloor x \rfloor$ (pembulatan ke bawah). Berapa limit kiri dan kanan di $x = 2$?",
         r"<p>Kiri: $1$; kanan: $2$. Limit dua sisi tidak ada.</p>"),
      "Soal 2: gambar tangga ⌊x⌋ sebentar. Di bilangan bulat, grafiknya selalu meloncat."),
]

# ═══════════════════════════════════════════════════════════════════════════
# 2. Hukum Limit & Bentuk Tak Tentu
# ═══════════════════════════════════════════════════════════════════════════
LIMIT_ALJABAR = [
    S("intuition", "Kapan cukup substitusi, kapan harus bongkar",
      r"""<p>Untuk fungsi "jinak" (polinomial, rasional dengan penyebut $\ne 0$, akar, trig, eksponen di domainnya), limit = nilai fungsi: cukup <b>substitusi langsung</b>.</p>
      <p>Masalah muncul saat substitusi menghasilkan <b>bentuk tak tentu</b>: $\tfrac{0}{0}$, $\tfrac{\infty}{\infty}$, $\infty - \infty$, $0 \cdot \infty$, $1^\infty$.
      Bentuk ini bukan jawaban. Ia sinyal bahwa ada faktor tersembunyi yang perlu dibongkar dulu.</p>""",
      "Langkah pertama SELALU substitusi. Kalau dapat angka biasa, selesai. Kalau dapat 0/0, baru kerja aljabar."),
    S("theorem", "Hukum limit",
      r"""<p>Jika $\lim_{x \to a} f(x) = L$ dan $\lim_{x \to a} g(x) = M$ ada, maka:</p>
      <p>$$\lim (f \pm g) = L \pm M, \quad \lim (cf) = cL, \quad \lim (fg) = LM, \quad \lim \frac{f}{g} = \frac{L}{M}\ (M \ne 0)$$</p>
      <p>$$\lim [f(x)]^n = L^n, \qquad \lim \sqrt[n]{f(x)} = \sqrt[n]{L}\ \ (L > 0 \text{ bila } n \text{ genap})$$</p>
      <p><b>Teorema apit:</b> jika $g(x) \le f(x) \le h(x)$ di sekitar $a$ dan $\lim g = \lim h = L$, maka $\lim f = L$.</p>""",
      "Hukum limit cuma boleh dipakai kalau limit tiap bagiannya ADA. 0/0 tidak memenuhi syarat hukum pembagian."),
    S("derivation", "Strategi membongkar bentuk tak tentu",
      r"""<div class="table-scroll"><table class="lesson-table"><thead><tr><th>Bentuk</th><th>Strategi</th></tr></thead><tbody>
        <tr><td>$\tfrac{0}{0}$ polinomial/rasional</td><td>faktorkan, coret faktor $(x - a)$</td></tr>
        <tr><td>$\tfrac{0}{0}$ dengan akar</td><td>kalikan sekawan</td></tr>
        <tr><td>$\tfrac{0}{0}$ pecahan bersusun</td><td>samakan penyebut dulu</td></tr>
        <tr><td>$\tfrac{0}{0}$ trigonometri</td><td>bentuk ke $\tfrac{\sin u}{u} \to 1$</td></tr>
        <tr><td>$\tfrac{\infty}{\infty}$ di $x \to \pm\infty$</td><td>bagi dengan pangkat tertinggi penyebut</td></tr>
        <tr><td>$\infty - \infty$ dengan akar</td><td>kalikan sekawan, lalu jadi $\tfrac{\infty}{\infty}$</td></tr>
      </tbody></table></div>""" + note(r"Aturan L'Hôpital juga bisa dipakai untuk $\tfrac00$ dan $\tfrac{\infty}{\infty}$, tapi baru dibahas di Level 3. Kuasai cara aljabar dulu: dosen sering melarang L'Hôpital di soal limit dasar."),
      "Simpan tabel ini. Hampir semua soal limit UTS Kalkulus 1 masuk salah satu baris di sini."),
    S("example", "Bedah soal: faktorisasi & sekawan",
      r"""<p><b>Soal 1.</b> $\displaystyle\lim_{x \to 2} \frac{x^3 - 8}{x - 2}$.</p>""" +
      steps(r"Substitusi: $\tfrac{0}{0}$, jadi bongkar.",
            r"Selisih kubik: $x^3 - 8 = (x - 2)(x^2 + 2x + 4)$.",
            r"Coret $(x - 2)$: limit $= 2^2 + 2(2) + 4 = 12$.") +
      r"""<p><b>Soal 2.</b> $\displaystyle\lim_{x \to 0} \frac{\sqrt{x + 4} - 2}{x}$.</p>""" +
      steps(r"Substitusi: $\tfrac{0}{0}$. Ada akar, jadi kalikan sekawan $\sqrt{x + 4} + 2$.",
            r"Pembilang: $(x + 4) - 4 = x$. Bentuknya jadi $\dfrac{x}{x(\sqrt{x + 4} + 2)}$.",
            r"Coret $x$: limit $= \dfrac{1}{\sqrt{4} + 2} = \dfrac14$."),
      "Sekawan dari √A − B adalah √A + B. Tujuannya membuat (√A)² supaya akarnya hilang."),
    S("theorem", "Limit trigonometri istimewa",
      r"""<p>$$\lim_{x \to 0} \frac{\sin x}{x} = 1, \qquad \lim_{x \to 0} \frac{1 - \cos x}{x} = 0, \qquad \lim_{x \to 0} \frac{\tan x}{x} = 1$$</p>
      <p>Bukti $\tfrac{\sin x}{x} \to 1$ memakai teorema apit dan geometri lingkaran satuan: $\cos x \le \dfrac{\sin x}{x} \le 1$ untuk $x$ kecil.</p>
      <p>Versi umum: kalau $u \to 0$, maka $\dfrac{\sin u}{u} \to 1$, dengan $u$ boleh berupa $5x$, $x^2$, dan seterusnya. Argumen sinus harus <b>sama persis</b> dengan penyebutnya.</p>""",
      "Rumus ini hanya berlaku di radian. Itu salah satu alasan kalkulus selalu pakai radian.",
      [g("y = sin(kx)/x mendekati k di x = 0", [-8, 8], [-1.5, 4], [param("k", "Koefisien k", 0.5, 3, 0.25, 1, "k")],
         [{"type": "fn", "expr": "sin(k*x)/x", "color": "blue", "label": "sin(kx)/x"},
          {"type": "hline", "y": "k", "color": "red", "dash": True}],
         [readout("Nilai di x = 0,001", "sin(k*0.001)/0.001", 5)],
         "Garis merah y = k: itulah limitnya. Lubang di x = 0 tidak terlihat, tapi ada.")]),
    S("example", "Bedah soal: limit trigonometri",
      r"""<p><b>Soal 1.</b> $\displaystyle\lim_{x \to 0} \frac{\sin 5x}{\tan 3x}$.</p>""" +
      steps(r"Tulis ulang: $\dfrac{\sin 5x}{5x} \cdot \dfrac{3x}{\tan 3x} \cdot \dfrac{5x}{3x}$.",
            r"Dua faktor pertama masing-masing $\to 1$.",
            r"Sisa: $\dfrac{5}{3}$. Jadi limitnya $\dfrac53$.") +
      r"""<p><b>Soal 2.</b> $\displaystyle\lim_{x \to 0} \frac{1 - \cos x}{x^2}$.</p>""" +
      steps(r"Identitas: $1 - \cos x = 2\sin^2\tfrac{x}{2}$.",
            r"$\dfrac{2\sin^2(x/2)}{x^2} = \dfrac{2}{4}\left(\dfrac{\sin(x/2)}{x/2}\right)^2$.",
            r"Limit $= \dfrac12 \cdot 1^2 = \dfrac12$."),
      "Trik utama: kalikan dan bagi dengan 'pasangan' yang tepat supaya muncul sin u / u dengan u yang sama."),
    S("example", "Bedah soal: limit di tak hingga",
      r"""<p><b>Aturan derajat</b> untuk $\dfrac{P(x)}{Q(x)}$ di $x \to \pm\infty$: derajat atas &lt; bawah → $0$; sama → rasio koefisien utama; atas &gt; bawah → $\pm\infty$.</p>
      <p><b>Soal 1.</b> $\displaystyle\lim_{x \to \infty} \frac{3x^2 - x + 5}{2x^2 + 7}$.</p>""" +
      steps(r"Bagi pembilang & penyebut dengan $x^2$: $\dfrac{3 - \tfrac1x + \tfrac{5}{x^2}}{2 + \tfrac{7}{x^2}}$.",
            r"Suku $\tfrac{1}{x}, \tfrac{1}{x^2} \to 0$. Limit $= \dfrac32$.") +
      r"""<p><b>Soal 2.</b> $\displaystyle\lim_{x \to \infty} \left(\sqrt{x^2 + 3x} - x\right)$ (bentuk $\infty - \infty$).</p>""" +
      steps(r"Kalikan sekawan: $\dfrac{(x^2 + 3x) - x^2}{\sqrt{x^2 + 3x} + x} = \dfrac{3x}{\sqrt{x^2 + 3x} + x}$.",
            r"Bagi dengan $x$ (untuk $x > 0$, $\sqrt{x^2} = x$): $\dfrac{3}{\sqrt{1 + \tfrac3x} + 1}$.",
            r"Limit $= \dfrac{3}{1 + 1} = \dfrac32$."),
      "Di x → −∞, hati-hati: √(x²) = |x| = −x. Tanda di langkah 'bagi dengan x' bisa berbalik.",
      [g("y = (3x² − x + 5)/(2x² + 7) menuju asimtot datar", [-30, 30], [-1, 3], [param("X", "Titik x", 1, 30, 1, 10, "X")],
         [{"type": "fn", "expr": "(3*x*x-x+5)/(2*x*x+7)", "color": "blue", "label": "f(x)"},
          {"type": "hline", "y": 1.5, "color": "red", "dash": True},
          {"type": "point", "x": "X", "y": "(3*X*X-X+5)/(2*X*X+7)", "color": "orange"}],
         [readout("f(X)", "(3*X*X-X+5)/(2*X*X+7)", 5)],
         "Makin besar X, titik oranye makin menempel ke y = 3/2.")]),
    S("pitfall", "Jebakan ujian",
      r"""<ul class="lesson-list">
        <li>$\tfrac{0}{0} = 0$ atau $1$? <b>Bukan dua-duanya.</b> Bentuk tak tentu bisa bernilai berapa saja.</li>
        <li>$\tfrac{\infty}{\infty} = 1$ dan $\infty - \infty = 0$: salah. Bandingkan $\lim \tfrac{2x}{x} = 2$ dan $\lim (x^2 - x) = \infty$.</li>
        <li>$\dfrac{\sin 5x}{x} = 5$ karena "coret sin": tidak, hasilnya $5$ karena $\tfrac{\sin 5x}{5x} \cdot 5$. Cara berpikirnya harus benar.</li>
        <li>Lupa $\sqrt{x^2} = |x|$ untuk $x \to -\infty$, sehingga tanda jawaban terbalik.</li>
        <li>Memakai hukum pembagian saat limit penyebut $0$.</li>
      </ul>""",
      "Paling sering kena: ∞ − ∞ dianggap nol. Ingat contoh √(x² + 3x) − x → 3/2, bukan 0."),
    S("checkpoint", "Mini checkpoint",
      qa(r"1. $\displaystyle\lim_{x \to 3} \frac{x^2 - 9}{x^2 - 2x - 3}$", r"<p>$\dfrac{(x - 3)(x + 3)}{(x - 3)(x + 1)} \to \dfrac{6}{4} = \dfrac32$.</p>") +
      qa(r"2. $\displaystyle\lim_{x \to -\infty} \frac{\sqrt{4x^2 + 1}}{x}$", r"<p>$\sqrt{4x^2 + 1} \approx 2|x| = -2x$ untuk $x < 0$, jadi limit $= -2$.</p>"),
      "Soal 2 sengaja menguji jebakan √(x²) = |x|. Kalau kamu jawab 2, cek lagi tandanya."),
]

# ═══════════════════════════════════════════════════════════════════════════
# 3. Kontinuitas & Teorema Nilai Antara
# ═══════════════════════════════════════════════════════════════════════════
KONTINUITAS = [
    S("intuition", "Menggambar tanpa mengangkat pensil",
      r"""<p>Secara intuitif, $f$ kontinu kalau grafiknya bisa digambar tanpa mengangkat pensil: tanpa lubang, lompatan, atau ledakan ke tak hingga.</p>
      <p>Kenapa penting? Besaran fisis (suhu, posisi) berubah kontinu; algoritma pencari akar seperti bisection <b>hanya</b> dijamin bekerja untuk fungsi kontinu;
      dan hampir semua teorema kalkulus (nilai ekstrem, nilai rata-rata, teorema dasar) mensyaratkan kontinuitas.</p>""",
      "Kontinuitas = 'limit dan nilai fungsinya akur'. Itu inti definisi formal di slide berikut."),
    S("theorem", "Definisi & jenis diskontinuitas",
      r"""<p>$f$ <b>kontinu di</b> $a$ jika tiga syarat terpenuhi:</p>
      <ol class="lesson-list"><li>$f(a)$ terdefinisi,</li><li>$\displaystyle\lim_{x \to a} f(x)$ ada,</li><li>$\displaystyle\lim_{x \to a} f(x) = f(a)$.</li></ol>
      <div class="table-scroll"><table class="lesson-table"><thead><tr><th>Jenis</th><th>Ciri</th><th>Contoh di $x = 0$</th></tr></thead><tbody>
        <tr><td>Dapat dihapus</td><td>limit ada, tapi $\ne f(a)$ atau $f(a)$ tak ada</td><td>$\tfrac{\sin x}{x}$</td></tr>
        <tr><td>Lompatan</td><td>limit kiri $\ne$ limit kanan (keduanya hingga)</td><td>$\tfrac{|x|}{x}$</td></tr>
        <tr><td>Tak hingga</td><td>salah satu sisi menuju $\pm\infty$</td><td>$\tfrac{1}{x}$</td></tr>
        <tr><td>Berosilasi</td><td>nilai tidak menetap</td><td>$\sin\tfrac1x$</td></tr>
      </tbody></table></div>
      <p>Kontinu pada $[a, b]$: kontinu di $(a, b)$, kontinu kanan di $a$, kontinu kiri di $b$.</p>""",
      "Untuk soal 'tunjukkan kontinu', tulis eksplisit ketiga syarat. Penilai biasanya memberi poin per syarat."),
    S("intuition", "Eksplorasi: menyambung fungsi sepotong-sepotong",
      r"""<p>$f(x) = \begin{cases} x^2 & x < 2 \\ cx - 1 & x \ge 2 \end{cases}$. Limit kiri di $2$ adalah $4$, sedangkan limit kanan $2c - 1$.</p>
      <p>Geser $c$ sampai kedua potongan bersambung. Secara aljabar: $2c - 1 = 4 \Rightarrow c = \tfrac52$.</p>""",
      "Cara cepat soal 'tentukan konstanta agar kontinu': samakan limit kiri, limit kanan, dan nilai fungsi di titik sambung.",
      [g("Mencari c agar f kontinu di x = 2", [-1, 5], [-2, 12], [param("c", "Konstanta c", 0, 5, 0.25, 1.5, "c")],
         [{"type": "fn", "expr": "x < 2 ? x*x : c*x - 1", "color": "blue", "label": "f(x)"},
          {"type": "point", "x": 2, "y": 4, "color": "orange"}, {"type": "point", "x": 2, "y": "2*c-1", "color": "green"}],
         [readout("Limit kiri", "4", 3), readout("Limit kanan = f(2)", "2*c-1", 3)],
         "Kontinu tepat saat titik oranye dan hijau berimpit, yaitu c = 2,5.")]),
    S("theorem", "Sifat fungsi kontinu",
      r"""<ul class="lesson-list">
        <li>Jumlah, selisih, hasil kali, dan hasil bagi (penyebut $\ne 0$) fungsi kontinu tetap kontinu.</li>
        <li>Polinomial kontinu di $\mathbb{R}$; fungsi rasional kontinu di domainnya; $\sin, \cos, e^x$ kontinu di $\mathbb{R}$; $\ln x$ di $(0, \infty)$.</li>
        <li><b>Komposisi:</b> jika $\lim_{x \to a} g(x) = b$ dan $f$ kontinu di $b$, maka
          $$\lim_{x \to a} f(g(x)) = f\!\left(\lim_{x \to a} g(x)\right).$$</li>
      </ul>""",
      "Sifat komposisi ini yang membolehkan kamu 'memasukkan limit ke dalam' √, e^, atau ln, asal fungsi luarnya kontinu."),
    S("theorem", "Teorema Nilai Antara (TNA)",
      r"""<p>Jika $f$ <b>kontinu pada</b> $[a, b]$ dan $N$ berada di antara $f(a)$ dan $f(b)$, maka ada $c \in (a, b)$ dengan $f(c) = N$.</p>
      <p>Akibat penting: kalau $f(a)$ dan $f(b)$ berbeda tanda, ada akar $f(c) = 0$ di antara keduanya.
      Ini dasar <b>metode bagi dua</b> (bisection) di metode numerik: bagi interval dua, ambil separuh yang ujungnya berbeda tanda, ulangi.</p>""",
      "TNA cuma menjamin akar ADA, bukan memberi tahu di mana tepatnya. Lokasinya dicari dengan bisection.",
      [g("TNA pada f(x) = x³ − x − 1", [-1, 3], [-4, 8],
         [param("a", "Ujung kiri a", 0, 2, 0.05, 1, "a"), param("b", "Ujung kanan b", 0.5, 2.5, 0.05, 2, "b")],
         [{"type": "fn", "expr": "x*x*x - x - 1", "color": "blue", "label": "f(x)"},
          {"type": "hline", "y": 0, "color": "gray"},
          {"type": "point", "x": "a", "y": "a*a*a-a-1", "color": "orange"}, {"type": "point", "x": "b", "y": "b*b*b-b-1", "color": "green"}],
         [readout("f(a)", "a*a*a-a-1", 4), readout("f(b)", "b*b*b-b-1", 4), readout("Titik tengah", "(a+b)/2", 4)],
         "Persempit [a, b] sambil menjaga f(a) dan f(b) tetap berbeda tanda. Akarnya sekitar 1,3247.")]),
    S("example", "Bedah soal: konstanta, klasifikasi, dan TNA",
      r"""<p><b>Soal 1.</b> Klasifikasikan diskontinuitas $f(x) = \dfrac{x^2 - x - 2}{x^2 - 4}$.</p>""" +
      steps(r"Faktorkan: $\dfrac{(x - 2)(x + 1)}{(x - 2)(x + 2)}$; diskontinu di $x = 2$ dan $x = -2$.",
            r"Di $x = 2$: faktor tercoret, limit $= \tfrac{3}{4}$ ada → <b>dapat dihapus</b> (definisikan $f(2) = \tfrac34$).",
            r"Di $x = -2$: penyebut tetap nol, pembilang $-1 \ne 0$ → <b>tak hingga</b> (asimtot tegak).") +
      r"""<p><b>Soal 2.</b> Tunjukkan $x^3 - x - 1 = 0$ punya akar di $[1, 2]$, lalu persempit dengan dua langkah bisection.</p>""" +
      steps(r"$f(x) = x^3 - x - 1$ polinomial, jadi kontinu di $[1, 2]$.",
            r"$f(1) = -1 < 0$ dan $f(2) = 5 > 0$. Menurut TNA ada $c \in (1, 2)$ dengan $f(c) = 0$.",
            r"$f(1.5) = 0.875 > 0$ → akar di $[1, 1.5]$.",
            r"$f(1.25) \approx -0.297 < 0$ → akar di $[1.25, 1.5]$."),
      "Di soal TNA, kalimat 'f kontinu pada [a, b]' WAJIB ditulis. Tanpa itu, penerapan TNA tidak sah."),
    S("derivation", "Sekilas definisi formal ε–δ",
      r"""<p>Definisi presisi limit (dibahas tuntas di jalur FMIPA):
      $$\lim_{x \to a} f(x) = L \iff \forall \varepsilon > 0\ \exists \delta > 0:\ 0 < |x - a| < \delta \Rightarrow |f(x) - L| < \varepsilon.$$</p>
      <p><b>Contoh:</b> buktikan $\displaystyle\lim_{x \to 2}(3x - 1) = 5$.</p>""" +
      steps(r"Kita ingin $|(3x - 1) - 5| = |3x - 6| = 3|x - 2| < \varepsilon$.",
            r"Cukup $|x - 2| < \tfrac{\varepsilon}{3}$. Pilih $\delta = \tfrac{\varepsilon}{3}$.",
            r"Maka $0 < |x - 2| < \delta \Rightarrow |f(x) - 5| = 3|x - 2| < 3\delta = \varepsilon$. Terbukti."),
      "Bacanya seperti tantangan: kamu ditantang dengan ε sekecil apa pun, dan harus selalu bisa membalas dengan δ."),
    S("pitfall", "Jebakan ujian",
      r"""<ul class="lesson-list">
        <li>Memakai TNA pada fungsi yang tidak kontinu: $\tfrac1x$ di $[-1, 1]$ berubah tanda tetapi tidak punya akar.</li>
        <li>Mengira terdefinisi = kontinu. $\lfloor x \rfloor$ terdefinisi di mana-mana tetapi diskontinu di tiap bilangan bulat.</li>
        <li>Lupa memeriksa syarat (3): limit ada dan $f(a)$ ada, tetapi tidak sama.</li>
        <li>Menyebut $\tfrac{\sin x}{x}$ "diskontinu tak hingga" di $0$. Itu jenis dapat dihapus, karena limitnya $1$.</li>
      </ul>""",
      "Contoh 1/x di [−1, 1] itu kontra-contoh favorit dosen. Hafalkan sebagai alarm sebelum memakai TNA."),
    S("checkpoint", "Mini checkpoint",
      qa(r"1. Tentukan $k$ agar $f(x) = \begin{cases} kx^2 & x \le 1 \\ 2x + k & x > 1 \end{cases}$ kontinu.",
         r"<p>$k(1)^2 = 2(1) + k \Rightarrow k = 2 + k$, mustahil. Tidak ada $k$ yang membuatnya kontinu.</p>") +
      qa(r"2. Apakah $\cos x = x$ punya solusi di $[0, \tfrac{\pi}{2}]$?",
         r"<p>$g(x) = \cos x - x$ kontinu; $g(0) = 1 > 0$, $g(\tfrac{\pi}{2}) = -\tfrac{\pi}{2} < 0$. Menurut TNA ada solusi.</p>"),
      "Soal 1 sengaja menjebak: jawaban 'tidak ada' itu sah, asal ditunjukkan dengan aljabar yang benar."),
]

# ═══════════════════════════════════════════════════════════════════════════
# 4. Definisi Turunan & Garis Singgung
# ═══════════════════════════════════════════════════════════════════════════
TURUNAN_DEFINISI = [
    S("intuition", "Dari kemiringan rata-rata ke kemiringan sesaat",
      r"""<p>Mobil menempuh $s(t)$ meter. Kecepatan rata-rata pada $[t, t + h]$ adalah $\dfrac{s(t + h) - s(t)}{h}$: kemiringan <b>garis sekan</b> yang memotong grafik di dua titik.</p>
      <p>Makin kecil $h$, garis sekan makin mirip <b>garis singgung</b>, dan kecepatan rata-rata makin mirip kecepatan sesaat.
      Turunan adalah limit proses itu.</p>""",
      "Sekan = 'dua titik', singgung = 'satu titik'. Turunan adalah apa yang terjadi saat dua titik itu menyatu."),
    S("intuition", "Eksplorasi: sekan berubah menjadi singgung",
      r"""<p>Pada $f(x) = x^2$, sekan melalui $(a, a^2)$ dan $(a + h, (a + h)^2)$ punya kemiringan
      $$\frac{(a + h)^2 - a^2}{h} = 2a + h.$$
      Saat $h \to 0$, kemiringannya menuju $2a$: kemiringan garis singgung.</p>""",
      "Geser h ke nol pelan-pelan. Garis biru (sekan) akan menempel ke garis merah putus-putus (singgung).",
      [g("Sekan menuju singgung pada f(x) = x²", [-3, 4], [-2, 10],
         [param("a", "Titik a", -2, 2.5, 0.25, 1, "a"), param("h", "Jarak h", -1.5, 2, 0.05, 1.5, "h")],
         [{"type": "fn", "expr": "x*x", "color": "gray", "label": "f(x) = x²"},
          {"type": "fn", "expr": "a*a + (2*a + h)*(x - a)", "color": "blue", "label": "sekan"},
          {"type": "fn", "expr": "a*a + 2*a*(x - a)", "color": "red", "dash": True, "label": "singgung"},
          {"type": "point", "x": "a", "y": "a*a", "color": "red"}, {"type": "point", "x": "a+h", "y": "(a+h)*(a+h)", "color": "blue"}],
         [readout("Kemiringan sekan 2a + h", "2*a+h", 4), readout("Kemiringan singgung 2a", "2*a", 4)],
         "Selisih kedua kemiringan persis h, jadi menuju 0.")]),
    S("theorem", "Definisi turunan",
      r"""<p>$$f'(a) = \lim_{h \to 0} \frac{f(a + h) - f(a)}{h} \qquad \text{atau setara} \qquad f'(a) = \lim_{x \to a} \frac{f(x) - f(a)}{x - a}$$</p>
      <p>bila limitnya ada; $f$ disebut <b>terdiferensialkan</b> di $a$.</p>
      <ul class="lesson-list">
        <li>Garis singgung di $(a, f(a))$: $\ y - f(a) = f'(a)(x - a)$.</li>
        <li>Garis normal (tegak lurus singgung): $\ y - f(a) = -\dfrac{1}{f'(a)}(x - a)$, bila $f'(a) \ne 0$.</li>
        <li>Notasi: $f'(x) = \dfrac{dy}{dx} = \dfrac{d}{dx}f(x) = Df(x)$.</li>
        <li>Satuan $f'$ = satuan output per satuan input, misalnya m/s, rupiah/unit, atau loss/parameter.</li>
      </ul>""",
      "Bentuk kedua (x → a) sering lebih cepat untuk soal 'hitung f'(a) di satu titik'."),
    S("derivation", "Menurunkan dari definisi",
      r"""<p><b>(a)</b> $f(x) = \dfrac{1}{x}$:</p>""" +
      steps(r"$\dfrac{f(x + h) - f(x)}{h} = \dfrac{1}{h}\left(\dfrac{1}{x + h} - \dfrac1x\right) = \dfrac{1}{h} \cdot \dfrac{x - (x + h)}{x(x + h)}$.",
            r"$= \dfrac{-h}{h\,x(x + h)} = \dfrac{-1}{x(x + h)}$.",
            r"$h \to 0$: $\ f'(x) = -\dfrac{1}{x^2}$.") +
      r"""<p><b>(b)</b> $f(x) = \sqrt{x}$:</p>""" +
      steps(r"$\dfrac{\sqrt{x + h} - \sqrt{x}}{h} \cdot \dfrac{\sqrt{x + h} + \sqrt{x}}{\sqrt{x + h} + \sqrt{x}} = \dfrac{h}{h(\sqrt{x + h} + \sqrt{x})}$.",
            r"$h \to 0$: $\ f'(x) = \dfrac{1}{2\sqrt{x}}$ untuk $x > 0$."),
      "Pola tetap: susun hasil bagi selisih, sederhanakan sampai h di penyebut bisa dicoret, BARU masukkan h = 0."),
    S("example", "Bedah soal: garis singgung & normal",
      r"""<p><b>Soal.</b> Tentukan garis singgung dan garis normal $f(x) = \sqrt{x}$ di $x = 4$.</p>""" +
      steps(r"Titik: $f(4) = 2$, jadi $(4, 2)$.",
            r"Kemiringan: $f'(4) = \dfrac{1}{2\sqrt4} = \dfrac14$.",
            r"Singgung: $y - 2 = \tfrac14(x - 4) \Rightarrow y = \tfrac14 x + 1$.",
            r"Normal: kemiringan $-4$, jadi $y - 2 = -4(x - 4) \Rightarrow y = -4x + 18$.") +
      r"""<p><b>Aproksimasi:</b> garis singgung bisa dipakai menaksir nilai dekat titik itu: $\sqrt{4.1} \approx \tfrac14(4.1) + 1 = 2.025$ (nilai asli $2.0248\ldots$).</p>""",
      "Cek cepat garis singgung: substitusi x = 4 ke persamaanmu harus menghasilkan y = 2."),
    S("theorem", "Terdiferensialkan ⇒ kontinu (tapi tidak sebaliknya)",
      r"""<p><b>Teorema:</b> jika $f'(a)$ ada, maka $f$ kontinu di $a$.</p>
      <p>Kebalikannya <b>salah</b>. Fungsi bisa kontinu tetapi gagal terdiferensialkan di:</p>
      <ul class="lesson-list">
        <li><b>Sudut tajam:</b> $f(x) = |x|$ di $0$; kemiringan kiri $-1$, kanan $+1$.</li>
        <li><b>Singgung tegak:</b> $f(x) = x^{1/3}$ di $0$; kemiringan $\to \infty$.</li>
        <li><b>Diskontinuitas</b> apa pun otomatis tidak terdiferensialkan.</li>
      </ul>""",
      "Di grafik, 'terdiferensialkan' artinya kalau di-zoom terus, grafiknya kelihatan seperti garis lurus. Sudut tajam tidak pernah jadi lurus.",
      [g("Kemiringan sekan |x| dari kiri dan kanan 0", [-3, 3], [-1, 3], [param("h", "Jarak h", 0.05, 2, 0.05, 1, "h")],
         [{"type": "fn", "expr": "abs(x)", "color": "blue", "label": "|x|"},
          {"type": "point", "x": "-h", "y": "h", "color": "orange"}, {"type": "point", "x": "h", "y": "h", "color": "green"}],
         [readout("Kemiringan sekan kiri", "-1", 2), readout("Kemiringan sekan kanan", "1", 2)],
         "Berapa pun h-nya, kemiringan kiri tetap −1 dan kanan +1. Limitnya tidak sama, jadi f'(0) tidak ada.")]),
    S("pitfall", "Jebakan ujian",
      r"""<ul class="lesson-list">
        <li>Memasukkan $h = 0$ sebelum menyederhanakan, sehingga dapat $\tfrac{0}{0}$ lalu bingung.</li>
        <li>Menulis $f(a + h) = f(a) + h$. Contoh: $(a + h)^2 = a^2 + 2ah + h^2$, bukan $a^2 + h$.</li>
        <li>Lupa tanda kurung di $f(x + h)$ untuk fungsi rumit, misalnya $3(x + h)^2 - 2(x + h)$.</li>
        <li>Mengira kontinu pasti terdiferensialkan. $|x|$ adalah kontra-contoh standar.</li>
        <li>Garis normal pakai kemiringan $-f'(a)$; yang benar $-\dfrac{1}{f'(a)}$.</li>
      </ul>""",
      "Soal 'turunkan dengan definisi' DILARANG pakai aturan cepat. Tulis limit hasil bagi selisihnya, atau poinnya hilang."),
    S("checkpoint", "Mini checkpoint",
      qa(r"1. Dengan definisi, hitung $f'(x)$ untuk $f(x) = 3x^2 - 5x$.",
         r"<p>$\dfrac{3(x + h)^2 - 5(x + h) - 3x^2 + 5x}{h} = \dfrac{6xh + 3h^2 - 5h}{h} = 6x + 3h - 5 \to 6x - 5$.</p>") +
      qa(r"2. Limit $\displaystyle\lim_{h \to 0} \frac{(2 + h)^4 - 16}{h}$ adalah turunan fungsi apa, di titik mana? Berapa nilainya?",
         r"<p>$f(x) = x^4$ di $a = 2$; $f'(2) = 4 \cdot 2^3 = 32$.</p>"),
      "Soal 2 membalik arah: kenali pola f(a + h) − f(a) di pembilangnya. Ini sering muncul di pilihan ganda."),
]

SLIDES = {
    "kd-lim-konsep": LIMIT_KONSEP,
    "kd-lim-aljabar": LIMIT_ALJABAR,
    "kd-lim-kontinu": KONTINUITAS,
    "kd-tur-definisi": TURUNAN_DEFINISI,
}
