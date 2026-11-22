r"""
Kurikulum v2 — Batch 4 (bagian C): jalur spesialisasi Fasilkom & FMIPA.

Fasilkom: Laju Pertumbuhan Asimtotik (Big-O lewat limit) · Metode Numerik (Newton-Raphson & Simpson) ·
Gradient Descent & Backpropagation.
FMIPA: Pembuktian Formal Limit (ε–δ) · Fungsi Gamma, Beta & Error · Pengantar Analisis Real.

Rujukan: Cormen dkk. (CLRS) Bab 3; Burden & Faires, Numerical Analysis Bab 2 & 4; Goodfellow dkk., Deep Learning Bab 4 & 6;
Bartle & Sherbert, Introduction to Real Analysis Bab 2–3, 5, 8; Stewart 9e §2.4, §7.7, §11.11.
"""

from ..helpers import param, readout
from .l1_slides import S, g, note, qa, steps
from .l3_slides import pohon


def kode(src):
    """Potongan kode (tidak diproses KaTeX maupun pecahan otomatis)."""
    return f'<pre class="lesson-code"><code>{src}</code></pre>'


# ═══════════════════════════════════════════════════════════════════════════
# Fasilkom 1. Laju Pertumbuhan Asimtotik (Big-O lewat Limit)
# ═══════════════════════════════════════════════════════════════════════════
ASIMTOTIK = [
    S("intuition", "Membandingkan algoritma saat n membesar",
      r"""<p>Linear search memeriksa $n$ elemen, binary search hanya sekitar $\log_2 n$. Untuk $n = 10^9$ itu satu miliar langkah dibanding sekitar $30$.
      Analisis algoritma tidak peduli konstanta kecil atau $n$ kecil; yang dipedulikan adalah <b>perilaku saat $n \to \infty$</b>. Itu persis bahasa limit.</p>""",
      "Geser n. Perhatikan rasio n log n / n² menuju 0: algoritma n log n 'akhirnya' selalu menang, berapa pun konstantanya.",
      [g("Pertumbuhan fungsi", [1, 30], [0, 400], [param("N", "n", 2, 30, 1, 10, "n")],
         [{"type": "fn", "expr": "10*log2(x)", "color": "gray", "label": "10 log₂ n"},
          {"type": "fn", "expr": "x*log2(x)", "color": "green", "label": "n log₂ n"},
          {"type": "fn", "expr": "x*x", "color": "blue", "label": "n²"},
          {"type": "fn", "expr": "pow(2, x)", "color": "red", "label": "2ⁿ"},
          {"type": "vline", "x": "N", "color": "gray", "dash": True}],
         [readout("n log₂ n / n²", "N*log2(N)/(N*N)", 4), readout("n² / 2ⁿ", "N*N/pow(2, N)", 6)],
         "Eksponensial meninggalkan semua polinom setelah n sekitar 10.")]),
    S("theorem", "Definisi O, Ω, Θ, o dan uji limit",
      r"""<ul class="lesson-list">
        <li>$f = O(g)$: ada $c &gt; 0$ dan $n_0$ sehingga $f(n) \le c\,g(n)$ untuk semua $n \ge n_0$ (batas atas).</li>
        <li>$f = \Omega(g)$: $f(n) \ge c\,g(n)$ untuk $n \ge n_0$ (batas bawah). $\ f = \Theta(g)$: keduanya.</li>
        <li>$f = o(g)$: $f$ tumbuh <b>jauh</b> lebih lambat, $\lim f/g = 0$.</li>
      </ul>
      <p><b>Uji limit</b> (untuk $f, g &gt; 0$, bila limitnya ada): misalkan $L = \displaystyle\lim_{n \to \infty}\frac{f(n)}{g(n)}$.</p>
      <div class="table-scroll"><table class="lesson-table"><thead><tr><th>$L$</th><th>Kesimpulan</th></tr></thead><tbody>
        <tr><td>$0$</td><td>$f = o(g)$, sehingga $f = O(g)$ tetapi bukan $\Theta$</td></tr>
        <tr><td>$0 &lt; L &lt; \infty$</td><td>$f = \Theta(g)$</td></tr>
        <tr><td>$\infty$</td><td>$f = \Omega(g)$ tetapi bukan $O(g)$</td></tr>
      </tbody></table></div>""",
      "Uji limit cuma alat bantu. Kalau limitnya tidak ada, definisi dengan c dan n₀ tetap berlaku."),
    S("example", "Bedah soal: membandingkan dengan limit & L'Hôpital",
      steps(r"$3n^2 + 5n\log n + 7 = \Theta(n^2)$: $\ \dfrac{3n^2 + 5n\log n + 7}{n^2} \to 3$ karena $\tfrac{\log n}{n} \to 0$.",
            r"$\log_a n = \Theta(\log_b n)$: rasionya $\tfrac{\ln b}{\ln a}$, sebuah konstanta. Itulah alasan basis log tidak ditulis dalam Big-O.",
            r"$(\ln n)^{10} = o(n^{0.1})$: L'Hôpital sepuluh kali, atau substitusi $n = e^m$ menjadi $\tfrac{m^{10}}{e^{0.1m}} \to 0$.",
            r"$2^{n+1} = \Theta(2^n)$ (rasio $2$), tetapi $4^n \ne O(2^n)$ karena $\tfrac{4^n}{2^n} = 2^n \to \infty$.") +
      note(r"Hierarki: $1 \ll \log n \ll \sqrt n \ll n \ll n\log n \ll n^2 \ll n^3 \ll 2^n \ll n! \ll n^n$."),
      "Basis logaritma tidak penting, tetapi basis eksponen SANGAT penting. Jebakan ini sering muncul di soal pilihan ganda."),
    S("theorem", "Jumlah, integral, dan Stirling",
      r"""<p>Banyak analisis algoritma bermuara pada jumlah. Kalkulus memberi taksiran lewat integral (seperti uji integral deret):
      $$\int_1^{n}f(x)\,dx \le \sum_{k=1}^{n}f(k) \le f(1) + \int_1^{n}f(x)\,dx \quad (f \text{ turun}).$$</p>
      <ul class="lesson-list">
        <li>$\sum_{k=1}^{n}k^p = \Theta(n^{p+1})$ untuk $p \ge 0$.</li>
        <li>Bilangan harmonik: $\ln(n + 1) \le H_n = \sum_{k=1}^{n}\tfrac1k \le 1 + \ln n$, jadi $H_n = \Theta(\log n)$.</li>
        <li><b>Stirling:</b> $n! \approx \sqrt{2\pi n}\left(\tfrac{n}{e}\right)^n$, sehingga $\log_2(n!) = \Theta(n\log n)$.</li>
      </ul>
      <p>Akibat Stirling: algoritma pengurutan berbasis perbandingan butuh paling sedikit $\log_2(n!)$ perbandingan (pohon keputusan dengan $n!$ daun), yaitu $\Omega(n\log n)$.
      Merge sort optimal.</p>""",
      "Batas bawah Ω(n log n) untuk sorting adalah salah satu bukti terindah di ilmu komputer, dan intinya kalkulus."),
    S("example", "Bedah soal: menganalisis loop",
      kode("for i in range(1, n + 1):\n    j = 1\n    while j &lt;= n:\n        kerja_O1()\n        j += i") +
      steps(r"Untuk $i$ tetap, loop dalam berjalan sekitar $\tfrac{n}{i}$ kali.",
            r"Total $\displaystyle\sum_{i=1}^{n}\frac{n}{i} = n\,H_n$.",
            r"$H_n = \Theta(\log n)$, jadi totalnya $\Theta(n\log n)$.") +
      r"""<p>Pola lain: loop $j$ <b>dikali dua</b> tiap langkah ($j \mathrel{*}= 2$) berjalan $\Theta(\log n)$ kali; loop bersarang $j \le i$ memberi
      $\sum i = \tfrac{n(n + 1)}{2} = \Theta(n^2)$; rekurensi merge sort $T(n) = 2T(n/2) + n$ memberi $\Theta(n\log n)$.</p>""",
      "Ubah loop menjadi jumlah (sigma) dulu. Setelah jadi sigma, tinggal pakai rumus jumlah atau taksiran integral."),
    S("pitfall", "Jebakan ujian",
      r"""<ul class="lesson-list">
        <li>Mengira $O$ berarti "tepat". $n = O(n^2)$ itu benar (hanya batas atas); yang ketat adalah $\Theta$.</li>
        <li>$2^{2n} = O(2^n)$. Salah: $2^{2n} = 4^n$.</li>
        <li>Uji limit dipakai saat limit tidak ada: $n(2 + \sin n) = \Theta(n)$ walau $\tfrac{n(2 + \sin n)}{n}$ berosilasi. Kembali ke definisi ($n \le f \le 3n$).</li>
        <li>Mencampur kasus terburuk, rata-rata, dan terbaik dalam satu kesimpulan Big-O.</li>
        <li>Menjumlahkan Big-O secara keliru: $O(n) + O(n) + \dots$ sebanyak $n$ kali adalah $O(n^2)$, bukan $O(n)$.</li>
      </ul>""",
      "Saat ragu, tulis definisinya: cari c dan n₀ yang konkret. Bukti dengan angka tidak pernah salah."),
    S("checkpoint", "Mini checkpoint",
      qa(r"1. Urutkan: $n^{1.5}$, $n\log^2 n$, $2^{\sqrt n}$, $n!$.", r"<p>$n\log^2 n \ll n^{1.5} \ll 2^{\sqrt n} \ll n!$. (Cek $\tfrac{\log^2 n}{n^{0.5}} \to 0$ dan $\tfrac{1.5\log_2 n}{\sqrt n} \to 0$.)</p>") +
      qa(r"2. Benar atau salah: $\log(n!) = \Theta(n\log n)$.", r"<p>Benar, dari Stirling: $\log(n!) = n\log n - n\log e + O(\log n)$.</p>") +
      qa(r"3. Kompleksitas loop: $i = n$; selama $i &gt; 1$: $i = i/2$.", r"<p>$\Theta(\log n)$.</p>"),
      "Soal 1 trik: 2^√n = n^(√n / log₂ n), dan pangkat √n / log n terus naik, jadi mengalahkan polinom apa pun."),
]

# ═══════════════════════════════════════════════════════════════════════════
# Fasilkom 2. Metode Numerik: Newton-Raphson & Simpson (topik baru)
# ═══════════════════════════════════════════════════════════════════════════
NUMERIK = [
    S("intuition", "Ketika rumus eksak tidak ada",
      r"""<p>Persamaan $x^5 - x - 1 = 0$ tidak punya rumus akar. Integral $\int_0^1 e^{-x^2}dx$ tidak punya antiturunan elementer. Komputer tetap menjawab keduanya
      dalam mikrodetik, memakai <b>metode numerik</b>: fungsi <code>sqrt</code> di prosesor, solver di physics engine, dan optimizer di machine learning.</p>
      <p>Dua pertanyaan selalu menyertai metode numerik: <b>seberapa akurat</b> (galat) dan <b>seberapa cepat</b> (berapa langkah sampai akurat).</p>""",
      "Metode numerik adalah kalkulus yang diubah menjadi algoritma. Turunan dan polinom Taylor bekerja di balik layar."),
    S("theorem", "Metode Newton-Raphson",
      r"""<p>Ganti kurva dengan garis singgungnya di $x_n$, lalu cari titik potong garis itu dengan sumbu $x$:
      $$x_{n+1} = x_n - \frac{f(x_n)}{f'(x_n)}.$$</p>
      <p>Ulangi sampai $|x_{n+1} - x_n|$ cukup kecil. Ini linearisasi (Level 2) yang dipakai berulang-ulang.</p>""",
      "Geser tebakan awal dan jumlah iterasi. Hanya 3–4 langkah sudah memberi akurasi belasan digit.",
      [g("Newton untuk f(x) = x³ − 2x − 5", [0.5, 4], [-12, 40], [param("x0", "Tebakan awal x₀", 1.2, 3.8, 0.05, 3.5, "x₀"), param("N", "Iterasi", 0, 6, 1, 2, "n")],
         [{"type": "fn", "expr": "x*x*x - 2*x - 5", "color": "blue", "label": "f(x)"},
          {"type": "hline", "y": 0, "color": "gray"},
          {"type": "fn", "expr": "(3*x0*x0 - 2)*(x - x0) + x0*x0*x0 - 2*x0 - 5", "color": "orange", "dash": True, "label": "singgung di x₀"},
          {"type": "iter", "id": "NW", "init": {"xs": "x0", "ys": 0}, "update": {"xs": "xs - (xs*xs*xs - 2*xs - 5)/(3*xs*xs - 2)", "ys": 0},
           "steps": "N", "color": "red"}],
         [readout("xₙ", "NW.xs", 10), readout("f(xₙ)", "NW.xs*NW.xs*NW.xs - 2*NW.xs - 5", 10)],
         "Akar sebenarnya ≈ 2,0945514815. Ini contoh yang dipakai Newton sendiri.")]),
    S("theorem", "Konvergensi kuadratik & kapan Newton gagal",
      r"""<p>Dekat akar sederhana $r$ (dengan $f'(r) \ne 0$), galat $e_n = x_n - r$ memenuhi
      $$e_{n+1} \approx \frac{f''(r)}{2f'(r)}\,e_n^2.$$
      Galat dikuadratkan tiap langkah, sehingga <b>jumlah digit benar kira-kira berlipat dua</b> per iterasi.</p>
      <p><b>Kegagalan:</b> $f'(x_n) \approx 0$ (garis singgung hampir datar, loncatan sangat jauh); siklus, misalnya $f = x^3 - 2x + 2$ dari $x_0 = 0$ berputar $0 \to 1 \to 0$;
      divergen, misalnya $f = x^{1/3}$. <b>Biseksi</b> lebih lambat (galat hanya separuh tiap langkah) tetapi pasti berhasil bila $f(a)f(b) &lt; 0$ (Teorema Nilai Antara).
      Solver praktis menggabungkan keduanya.</p>""",
      "Strategi aman: biseksi beberapa langkah untuk mendekati akar, lalu Newton untuk 'finishing' yang super cepat."),
    S("example", "Bedah soal: menghitung √2 seperti prosesor",
      r"""<p>Akar dari $f(x) = x^2 - 2$. Rumus Newton menjadi $x_{n+1} = x_n - \dfrac{x_n^2 - 2}{2x_n} = \dfrac12\left(x_n + \dfrac{2}{x_n}\right)$ (metode Heron/Babilonia).</p>
      <div class="table-scroll"><table class="lesson-table"><thead><tr><th>$n$</th><th>$x_n$</th><th>Digit benar</th></tr></thead><tbody>
        <tr><td>0</td><td>1</td><td>1</td></tr>
        <tr><td>1</td><td>1.5</td><td>1</td></tr>
        <tr><td>2</td><td>1.416666…</td><td>3</td></tr>
        <tr><td>3</td><td>1.414215686…</td><td>6</td></tr>
        <tr><td>4</td><td>1.41421356237469…</td><td>12</td></tr>
      </tbody></table></div>""" +
      kode("def newton(f, df, x, tol=1e-12, maks=50):\n    for _ in range(maks):\n        langkah = f(x) / df(x)\n        x -= langkah\n        if abs(langkah) &lt; tol:\n            return x\n    raise RuntimeError(\"tidak konvergen\")"),
      "Perhatikan kolom digit benar: 3 → 6 → 12. Itulah konvergensi kuadratik dalam angka."),
    S("theorem", "Integrasi numerik: trapesium & Simpson",
      r"""<p>Bagi $[a, b]$ menjadi $n$ bagian selebar $h = \tfrac{b - a}{n}$, $x_i = a + ih$, $f_i = f(x_i)$.</p>
      <p><b>Trapesium</b> (hampiran garis lurus): $\ T_n = \dfrac{h}{2}\left[f_0 + 2f_1 + \dots + 2f_{n-1} + f_n\right]$, $\ |E_T| \le \dfrac{K_2(b - a)^3}{12n^2}$.</p>
      <p><b>Simpson</b> ($n$ genap, hampiran parabola melalui tiap tiga titik):
      $$S_n = \frac{h}{3}\left[f_0 + 4f_1 + 2f_2 + 4f_3 + \dots + 4f_{n-1} + f_n\right], \qquad |E_S| \le \frac{K_4(b - a)^5}{180n^4},$$
      dengan $K_2 \ge |f''|$ dan $K_4 \ge |f^{(4)}|$ pada $[a, b]$.</p>""",
      "Gandakan n: galat trapesium turun 4 kali, galat Simpson turun 16 kali. Coba di grafik dengan ∫₀¹ 4/(1 + x²) dx = π.",
      [g("∫₀¹ 4/(1 + x²) dx = π: trapesium vs Simpson", [-0.05, 1.05], [-0.2, 4.4], [param("N", "n (genap)", 2, 20, 2, 4, "n")],
         [{"type": "riemann", "id": "T", "expr": "4/(1 + x*x)", "from": 0, "to": 1, "n": "N", "mode": "trap", "color": "amber"},
          {"type": "fn", "expr": "4/(1 + x*x)", "color": "blue", "label": "4/(1 + x²)"}],
         [readout("Trapesium Tₙ", "T", 8), readout("Galat trapesium", "T - pi", 8),
          readout("Simpson Sₙ", "(1/(3*N))*(4 + 2 + sum(1, N - 1, k => (k % 2 == 1 ? 4 : 2)*4/(1 + (k/N)*(k/N))))", 10),
          readout("Galat Simpson", "(1/(3*N))*(4 + 2 + sum(1, N - 1, k => (k % 2 == 1 ? 4 : 2)*4/(1 + (k/N)*(k/N)))) - pi", 10)],
         "Dengan n = 10, Simpson sudah benar sampai sekitar 8 digit.")]),
    S("example", "Bedah soal: Simpson vs trapesium untuk ln 2",
      r"""<p><b>Soal.</b> Taksir $\displaystyle\int_1^2\frac{dx}{x} = \ln 2 \approx 0.693147$ dengan $n = 4$.</p>""" +
      steps(r"$h = 0.25$; nilai $f$: $1,\ 0.8,\ 0.666667,\ 0.571429,\ 0.5$.",
            r"Trapesium: $\tfrac{0.25}{2}\left[1 + 2(0.8 + 0.666667 + 0.571429) + 0.5\right] = 0.697024$ (galat $\approx 3.9\times10^{-3}$).",
            r"Simpson: $\tfrac{0.25}{3}\left[1 + 4(0.8) + 2(0.666667) + 4(0.571429) + 0.5\right] = 0.693254$ (galat $\approx 1.1\times10^{-4}$).",
            r"Batas galat Simpson: $f^{(4)} = \tfrac{24}{x^5} \le 24$, sehingga $|E_S| \le \tfrac{24\cdot 1^5}{180\cdot 4^4} \approx 5.2\times10^{-4}$. Galat nyata memang di bawah batas itu."),
      "Batas galat memberi JAMINAN. Untuk soal 'tentukan n agar galat < 10⁻⁶', selesaikan ketaksamaan batas galatnya untuk n."),
    S("pitfall", "Jebakan ujian",
      r"""<ul class="lesson-list">
        <li>Newton dengan tebakan awal di dekat titik $f' = 0$: loncatan menjauh atau berosilasi.</li>
        <li>Berhenti hanya karena $|f(x_n)|$ kecil. Fungsi yang sangat landai bisa kecil jauh dari akar; cek juga $|x_{n+1} - x_n|$.</li>
        <li>Simpson dengan $n$ ganjil. Rumus koefisien $1, 4, 2, 4, \dots, 4, 1$ butuh $n$ genap.</li>
        <li>Batas galat memakai nilai turunan di satu titik, padahal harus <b>maksimum</b> pada seluruh interval.</li>
        <li>Membandingkan galat dengan hasil yang dibulatkan terlalu dini.</li>
      </ul>""",
      "Di kode, selalu pasang batas iterasi maksimum. Loop Newton tanpa batas adalah bug klasik."),
    S("checkpoint", "Mini checkpoint",
      qa(r"1. Satu langkah Newton untuk $f = x^2 - 5$ dari $x_0 = 2$.", r"<p>$x_1 = 2 - \dfrac{-1}{4} = 2.25$ (nilai sebenarnya $\sqrt5 \approx 2.2361$).</p>") +
      qa(r"2. Jika $n$ digandakan, galat Simpson menjadi berapa kali lebih kecil? Trapesium?", r"<p>Simpson $2^4 = 16$ kali; trapesium $2^2 = 4$ kali.</p>"),
      "Soal 2 adalah alasan Simpson jadi default di banyak pustaka sebelum ada metode adaptif."),
]

# ═══════════════════════════════════════════════════════════════════════════
# Fasilkom 3. Gradient Descent & Backpropagation
# ═══════════════════════════════════════════════════════════════════════════
GRADIENT_DESCENT = [
    S("intuition", "Turun gunung dalam kabut",
      r"""<p>Melatih model machine learning berarti mencari parameter $\mathbf{w}$ (bisa jutaan) yang meminimumkan <b>fungsi loss</b> $L(\mathbf{w})$.
      Kita tidak bisa melihat seluruh lanskap, tetapi bisa merasakan kemiringan di bawah kaki: gradien. Melangkahlah sedikit ke arah $-\nabla L$, ulangi.</p>""",
      "Naikkan learning rate η perlahan. Di sekitar η = 0,2 langkahnya mulai bolak-balik liar, lalu meledak: inilah 'divergen'.",
      [g("Gradient descent pada L = x² + 5y²", [-5, 5], [-3, 3],
         [param("eta", "Learning rate η", 0.01, 0.21, 0.005, 0.08, "η"), param("N", "Iterasi", 0, 40, 1, 15, "n")],
         [{"type": "param", "x": f"sqrt({k})*cos(t)", "y": f"sqrt({k}/5)*sin(t)", "t": [0, "2*pi"], "color": "gray"} for k in (1, 4, 9, 16, 25)] +
         [{"type": "iter", "id": "GD", "init": {"a": -4.5, "b": 2}, "update": {"a": "a - eta*2*a", "b": "b - eta*10*b"}, "steps": "N", "color": "red"}],
         [readout("Loss akhir", "GD.a*GD.a + 5*GD.b*GD.b", 6), readout("Faktor arah y: |1 − 10η| (< 1 agar konvergen)", "abs(1 - 10*eta)", 3)],
         "Kontur lonjong membuat lintasan zig-zag: arah y curam, arah x landai.")]),
    S("theorem", "Aturan pembaruan & mengapa −∇L",
      r"""<p>$$\mathbf{w}_{k+1} = \mathbf{w}_k - \eta\,\nabla L(\mathbf{w}_k).$$</p>
      <p>Dari topik gradien: turunan berarah $D_{\mathbf{u}}L = \nabla L\cdot\mathbf{u} \ge -|\nabla L|$, dan nilai paling negatif dicapai saat $\mathbf{u}$ searah $-\nabla L$.
      Jadi $-\nabla L$ adalah arah turun tercuram secara lokal. Untuk $\eta$ kecil, linearisasi menjamin $L(\mathbf{w}_{k+1}) \approx L(\mathbf{w}_k) - \eta|\nabla L|^2 &lt; L(\mathbf{w}_k)$.</p>
      <p><b>Memilih $\eta$:</b> pada loss kuadratik dengan Hessian $H$, iterasi stabil bila $0 &lt; \eta &lt; \dfrac{2}{\lambda_{\max}(H)}$. Untuk $L = x^2 + 5y^2$, $\lambda_{\max} = 10$, jadi $\eta &lt; 0.2$.</p>""",
      "Learning rate terlalu kecil: lambat. Terlalu besar: divergen. Batas atasnya ditentukan arah paling curam (nilai eigen terbesar Hessian)."),
    S("example", "Bedah soal: regresi linear dengan MSE",
      r"""<p>Data $(1, 2), (2, 3), (3, 5)$, model $\hat y = wx + b$, loss $L = \dfrac1n\sum_i(wx_i + b - y_i)^2$.</p>""" +
      steps(r"Turunan parsial: $\dfrac{\partial L}{\partial w} = \dfrac2n\sum_i(wx_i + b - y_i)\,x_i$, $\ \dfrac{\partial L}{\partial b} = \dfrac2n\sum_i(wx_i + b - y_i)$.",
            r"Mulai $w = b = 0$: residu $-2, -3, -5$.",
            r"$\dfrac{\partial L}{\partial w} = \tfrac23(-2 - 6 - 15) = -15.33$, $\ \dfrac{\partial L}{\partial b} = \tfrac23(-10) = -6.67$.",
            r"Dengan $\eta = 0.1$: $w = 1.533$, $b = 0.667$. Loss turun dari $12.67$ ke sekitar $0.22$.") +
      kode("for epoch in range(1000):\n    r = w * x + b - y              # residu (vektor numpy)\n    w -= eta * 2 * (r * x).mean()\n    b -= eta * 2 * r.mean()"),
      "Faktor 1/n (rata-rata) membuat besar gradien tidak bergantung pada jumlah data. Lupa faktor ini = learning rate efektif membengkak."),
    S("theorem", "Backpropagation = aturan rantai",
      r"""<p>Satu neuron: $z = wx + b$, $\hat y = \sigma(z)$, $L = (\hat y - y)^2$. Diagram pohon aturan rantai memberi
      $$\frac{\partial L}{\partial w} = \underbrace{2(\hat y - y)}_{\partial L/\partial\hat y}\cdot\underbrace{\sigma(z)\big(1 - \sigma(z)\big)}_{\partial\hat y/\partial z}\cdot\underbrace{x}_{\partial z/\partial w}.$$</p>
      <p>Pada jaringan berlapis, faktor-faktor ini dikalikan lapis demi lapis dari belakang (loss) ke depan (input). Menghitung dari belakang membuat setiap
      faktor perantara dipakai ulang: itulah efisiensi backpropagation.</p>
      <p><b>Vanishing gradient:</b> $\sigma'(z) \le \tfrac14$, jadi perkalian banyak lapis sigmoid membuat gradien mengecil eksponensial. Salah satu alasan ReLU populer.</p>""",
      "Backprop bukan sihir: ia aturan rantai Level 2 dan Level 4 yang disusun rapi dalam graf komputasi."),
    S("example", "Bedah soal: satu langkah backprop",
      r"""<p>$x = 1$, target $y = 1$, mulai $w = b = 0$, $\eta = 1$.</p>""" +
      steps(r"Maju: $z = 0$, $\hat y = \sigma(0) = 0.5$, $L = 0.25$.",
            r"Mundur: $\tfrac{\partial L}{\partial\hat y} = 2(0.5 - 1) = -1$; $\ \sigma'(0) = 0.25$; $\ \tfrac{\partial L}{\partial z} = -0.25$.",
            r"$\tfrac{\partial L}{\partial w} = -0.25\cdot x = -0.25$, $\ \tfrac{\partial L}{\partial b} = -0.25$.",
            r"Perbarui: $w = 0.25$, $b = 0.25$. Maju lagi: $z = 0.5$, $\hat y = \sigma(0.5) \approx 0.6225$, $L \approx 0.1425$. Loss turun.") +
      note(r"<b>Cek gradien</b> (gradient checking): bandingkan dengan beda pusat $\dfrac{L(w + h) - L(w - h)}{2h}$ untuk $h \approx 10^{-5}$. Kalau berbeda jauh, implementasi backprop-mu salah."),
      "Gradient checking adalah teknik debugging wajib saat menulis backprop sendiri. Ia memakai definisi turunan secara numerik."),
    S("theorem", "Varian praktis & lanskap non-konveks",
      r"""<ul class="lesson-list">
        <li><b>SGD / mini-batch:</b> gradien ditaksir dari sebagian data; lebih murah per langkah, dan derau membantu keluar dari titik pelana.</li>
        <li><b>Momentum:</b> $\mathbf{v} \leftarrow \beta\mathbf{v} + \nabla L$, $\ \mathbf{w} \leftarrow \mathbf{w} - \eta\mathbf{v}$; meredam zig-zag pada kontur lonjong.</li>
        <li><b>Adam:</b> menskala langkah per parameter memakai rata-rata gradien dan kuadratnya.</li>
        <li><b>Penskalaan fitur:</b> menyamakan skala input membuat kontur loss lebih bundar, sehingga GD jauh lebih cepat.</li>
        <li>Loss jaringan saraf <b>tidak konveks</b>: ada minimum lokal dan banyak titik pelana (lihat uji Hessian di topik Optimasi).</li>
      </ul>""",
      "Grafik pembuka: kontur lonjong = fitur tidak diskalakan. Normalisasi data adalah 'mengubah elips menjadi lingkaran'."),
    S("pitfall", "Jebakan ujian",
      r"""<ul class="lesson-list">
        <li>Tanda terbalik: $\mathbf{w} + \eta\nabla L$ adalah gradient <b>ascent</b> (naik).</li>
        <li>$\eta$ terlalu besar sehingga divergen, terlalu kecil sehingga tidak bergerak berarti.</li>
        <li>Lupa faktor $\tfrac1n$ atau faktor $2$ dari turunan kuadrat.</li>
        <li>Aturan rantai backprop melewatkan $\sigma'(z)$.</li>
        <li>Mengira gradient descent selalu menemukan minimum global.</li>
      </ul>""",
      "Gambar graf komputasi (x → z → ŷ → L) dan tulis turunan lokal di tiap panah. Kalikan sepanjang jalur."),
    S("checkpoint", "Mini checkpoint",
      qa(r"1. Satu langkah GD untuk $L = (w - 3)^2$ dari $w_0 = 0$, $\eta = 0.1$.", r"<p>$L' = 2(w - 3) = -6$, sehingga $w_1 = 0 - 0.1(-6) = 0.6$.</p>") +
      qa(r"2. Untuk $L = 5w^2$, berapa $\eta$ maksimum agar GD stabil?", r"<p>$w \leftarrow (1 - 10\eta)w$; stabil bila $|1 - 10\eta| &lt; 1$, yaitu $0 &lt; \eta &lt; 0.2$.</p>"),
      "Soal 2 adalah inti analisis stabilitas: GD pada kuadrat adalah barisan geometri dengan rasio 1 − ηλ."),
]

# ═══════════════════════════════════════════════════════════════════════════
# FMIPA 1. Pembuktian Formal Limit (ε–δ) (topik baru)
# ═══════════════════════════════════════════════════════════════════════════
EPSILON_DELTA = [
    S("intuition", "Permainan toleransi",
      r"""<p>"$f(x)$ mendekati $L$" terdengar jelas, tapi seberapa dekat? Definisi ε–δ mengubahnya menjadi permainan: lawanmu memberi toleransi keluaran $\varepsilon$
      sekecil apa pun; kamu harus menjawab dengan toleransi masukan $\delta$ sehingga setiap $x$ dalam jarak $\delta$ dari $a$ menghasilkan $f(x)$ dalam jarak $\varepsilon$ dari $L$.
      Jika kamu <b>selalu</b> bisa menjawab, limitnya $L$.</p>
      <p>Insinyur mengenalnya sebagai toleransi: agar diameter poros meleset kurang dari $\varepsilon$, mesin bubut harus disetel dengan ketelitian $\delta$.</p>""",
      "Perkecil ε, lalu cari δ terbesar yang membuat kurva di pita hijau seluruhnya masuk pita oranye.",
      [g("lim_{x→2} x² = 4: pita ε dan δ", [0.5, 3.5], [0, 10], [param("eps", "ε", 0.1, 3, 0.05, 1.5, "ε"), param("d", "δ", 0.02, 1, 0.01, 0.3, "δ")],
         [{"type": "hband", "from": "4 - eps", "to": "4 + eps", "color": "orange", "opacity": 0.18},
          {"type": "vband", "from": "2 - d", "to": "2 + d", "color": "green", "opacity": 0.15},
          {"type": "fn", "expr": "x*x", "color": "blue", "label": "f(x) = x²"},
          {"type": "point", "x": 2, "y": 4, "color": "red", "hollow": True}],
         [readout("max |x² − 4| untuk |x − 2| < δ = 4δ + δ²", "4*d + d*d", 4), readout("ε", "eps", 3),
          readout("δ yang dijamin cukup: min(1, ε/5)", "min(1, eps/5)", 4)],
         "δ sah bila 4δ + δ² ≤ ε. Pilihan min(1, ε/5) selalu sah, walau tidak selalu yang terbesar.")]),
    S("theorem", "Definisi & cara membacanya",
      r"""<p>$$\lim_{x \to a}f(x) = L \iff \forall\varepsilon &gt; 0\ \exists\delta &gt; 0\ \forall x:\ 0 &lt; |x - a| &lt; \delta \Rightarrow |f(x) - L| &lt; \varepsilon.$$</p>
      <ul class="lesson-list">
        <li>Urutan kuantor penting: $\varepsilon$ diberikan dulu, $\delta$ boleh bergantung pada $\varepsilon$ (dan $a$), <b>tidak</b> boleh bergantung pada $x$.</li>
        <li>$0 &lt; |x - a|$: nilai di $x = a$ sendiri tidak dipedulikan.</li>
        <li><b>Negasi</b> (limit bukan $L$): $\exists\varepsilon &gt; 0\ \forall\delta &gt; 0\ \exists x$ dengan $0 &lt; |x - a| &lt; \delta$ tetapi $|f(x) - L| \ge \varepsilon$.</li>
        <li>Varian: $\lim_{x \to \infty}f = L \iff \forall\varepsilon\ \exists M:\ x &gt; M \Rightarrow |f - L| &lt; \varepsilon$; $\ \lim_{x \to a}f = \infty \iff \forall M\ \exists\delta:\ 0 &lt; |x - a| &lt; \delta \Rightarrow f &gt; M$.</li>
      </ul>""",
      "Menegasikan kalimat berkuantor: tukar ∀ ↔ ∃ dan negasikan bagian akhirnya. Latih ini, karena muncul di setiap ujian analisis."),
    S("derivation", "Struktur bukti: coretan dulu, bukti kemudian",
      steps(r"<b>Analisis (di kertas coretan):</b> mulai dari $|f(x) - L|$, sederhanakan sampai muncul faktor $|x - a|$: $\ |f(x) - L| \le C\,|x - a|$.",
            r"Jika $C$ masih bergantung pada $x$, <b>batasi</b> $\delta \le 1$ (atau angka lain) dulu agar $x$ terkurung, lalu taksir $C$ dengan konstanta.",
            r"Pilih $\delta = \min\left(1, \tfrac{\varepsilon}{C}\right)$.",
            r"<b>Bukti (ditulis maju):</b> 'Ambil $\varepsilon &gt; 0$ sembarang. Pilih $\delta = \dots$. Jika $0 &lt; |x - a| &lt; \delta$, maka $|f(x) - L| \le \dots &lt; \varepsilon$. Terbukti.'") +
      note(r"Coretan bergerak mundur dari kesimpulan; bukti bergerak maju dari pilihan $\delta$. Jangan menyerahkan coretan sebagai bukti."),
      "Dosen menilai urutan logika. Kalimat 'Ambil ε > 0 sembarang' di awal sudah menunjukkan kamu paham struktur kuantornya."),
    S("example", "Bedah soal: limit linear",
      r"""<p><b>Buktikan</b> $\displaystyle\lim_{x \to 3}(4x - 5) = 7$.</p>""" +
      steps(r"Coretan: $|(4x - 5) - 7| = |4x - 12| = 4|x - 3|$. Ingin $&lt; \varepsilon$, cukup $|x - 3| &lt; \tfrac{\varepsilon}{4}$.",
            r"Bukti: ambil $\varepsilon &gt; 0$ sembarang, pilih $\delta = \tfrac{\varepsilon}{4}$.",
            r"Jika $0 &lt; |x - 3| &lt; \delta$, maka $|(4x - 5) - 7| = 4|x - 3| &lt; 4\delta = \varepsilon$. $\blacksquare$"),
      "Untuk fungsi linear f(x) = mx + c, δ = ε/|m| selalu berhasil. Kemiringan curam butuh δ lebih kecil."),
    S("example", "Bedah soal: limit kuadrat (trik membatasi δ)",
      r"""<p><b>Buktikan</b> $\displaystyle\lim_{x \to 2}x^2 = 4$.</p>""" +
      steps(r"Coretan: $|x^2 - 4| = |x - 2|\,|x + 2|$. Faktor $|x + 2|$ bergantung pada $x$, jadi perlu dikurung.",
            r"Batasi $\delta \le 1$: maka $|x - 2| &lt; 1 \Rightarrow 1 &lt; x &lt; 3 \Rightarrow |x + 2| &lt; 5$.",
            r"Sehingga $|x^2 - 4| &lt; 5|x - 2|$; cukup $|x - 2| &lt; \tfrac{\varepsilon}{5}$.",
            r"Bukti: ambil $\varepsilon &gt; 0$, pilih $\delta = \min\left(1, \tfrac{\varepsilon}{5}\right)$. Jika $0 &lt; |x - 2| &lt; \delta$, maka $|x + 2| &lt; 5$ dan $|x^2 - 4| &lt; 5\delta \le \varepsilon$. $\blacksquare$"),
      "Mengapa min? δ ≤ 1 menjamin |x + 2| < 5; δ ≤ ε/5 menjamin hasil akhirnya. Keduanya harus berlaku sekaligus."),
    S("example", "Bedah soal: limit tidak ada & hukum jumlah",
      r"""<p><b>Soal 1.</b> Buktikan $\displaystyle\lim_{x \to 0}\frac{|x|}{x}$ tidak ada.</p>""" +
      steps(r"Andaikan limitnya $L$. Ambil $\varepsilon = \tfrac12$ (negasi: cukup <b>satu</b> $\varepsilon$).",
            r"Untuk $\delta$ sembarang, $x_1 = \tfrac{\delta}{2}$ memberi $f = 1$ dan $x_2 = -\tfrac{\delta}{2}$ memberi $f = -1$.",
            r"Keduanya harus dalam jarak $\tfrac12$ dari $L$, padahal jarak $1$ dan $-1$ adalah $2 &gt; 2\cdot\tfrac12$. Kontradiksi.") +
      r"""<p><b>Soal 2.</b> Jika $\lim f = L$ dan $\lim g = M$, buktikan $\lim(f + g) = L + M$.</p>""" +
      steps(r"Ambil $\varepsilon &gt; 0$. Ada $\delta_1$ dengan $|f - L| &lt; \tfrac{\varepsilon}{2}$ dan $\delta_2$ dengan $|g - M| &lt; \tfrac{\varepsilon}{2}$.",
            r"Pilih $\delta = \min(\delta_1, \delta_2)$. Ketaksamaan segitiga: $|(f + g) - (L + M)| \le |f - L| + |g - M| &lt; \tfrac{\varepsilon}{2} + \tfrac{\varepsilon}{2} = \varepsilon$. $\blacksquare$"),
      "Trik ε/2 dan min(δ₁, δ₂) akan kamu pakai puluhan kali di Analisis Real. Kuasai polanya sekarang."),
    S("pitfall", "Jebakan ujian",
      r"""<ul class="lesson-list">
        <li>$\delta$ bergantung pada $x$, misalnya $\delta = \tfrac{\varepsilon}{|x + 2|}$. Tidak sah.</li>
        <li>Menulis bukti mundur (dimulai dari $|f(x) - L| &lt; \varepsilon$ lalu "maka" ke $|x - a| &lt; \delta$).</li>
        <li>Lupa membatasi $\delta$ untuk fungsi tak linear, sehingga konstanta $C$ tidak terkendali.</li>
        <li>Membuktikan limit tidak ada dengan satu $\varepsilon$ tetapi memilih $x$ yang tidak memenuhi $0 &lt; |x - a| &lt; \delta$.</li>
        <li>Membalik kuantor: "ada $\delta$ untuk semua $\varepsilon$" adalah pernyataan lain yang jauh lebih kuat.</li>
      </ul>""",
      "Tes cepat δ: apakah rumus δ-mu hanya memuat ε (dan konstanta)? Kalau ada x di dalamnya, buktinya belum sah."),
    S("checkpoint", "Mini checkpoint",
      qa(r"1. $\delta$ untuk $\displaystyle\lim_{x \to 1}(3x + 2) = 5$.", r"<p>$|3x - 3| = 3|x - 1|$, jadi $\delta = \tfrac{\varepsilon}{3}$.</p>") +
      qa(r"2. $\delta$ untuk $\displaystyle\lim_{x \to 3}x^2 = 9$.", r"<p>$\delta \le 1 \Rightarrow |x + 3| &lt; 7$, jadi $\delta = \min\left(1, \tfrac{\varepsilon}{7}\right)$.</p>") +
      qa(r"3. Tulis negasi dari pernyataan &ldquo;$f$ kontinu di $a$&rdquo;.", r"<p>$\exists\varepsilon &gt; 0\ \forall\delta &gt; 0\ \exists x$: $|x - a| &lt; \delta$ tetapi $|f(x) - f(a)| \ge \varepsilon$.</p>"),
      "Soal 3: definisi kontinu sama dengan limit, hanya L diganti f(a) dan syarat 0 < |x − a| dilonggarkan."),
]

# ═══════════════════════════════════════════════════════════════════════════
# FMIPA 2. Fungsi Khusus: Gamma, Beta & Error
# ═══════════════════════════════════════════════════════════════════════════
GAMMA = [
    S("intuition", "Faktorial untuk bilangan tak bulat",
      r"""<p>$5! = 120$ jelas, tapi berapa $\left(\tfrac12\right)!$? Fungsi Gamma memperluas faktorial ke bilangan real (dan kompleks) secara mulus.
      Ia muncul di distribusi peluang (Gamma, khi-kuadrat, Student-t), konstanta normalisasi distribusi normal, volume bola berdimensi $n$, dan fisika statistik.</p>""",
      "Geser x. Luas di bawah tⁿ⁻¹e⁻ᵗ adalah Γ(x); di bilangan bulat nilainya tepat (x − 1)!.",
      [g("Γ(x) = ∫₀^∞ t^(x−1) e^(−t) dt sebagai luas", [-0.3, 16], [-0.05, 5], [param("X", "x", 1, 5, 0.05, 3, "x")],
         [{"type": "fill", "upper": "pow(x, X - 1)*exp(-x)", "from": 0, "to": 16, "color": "purple"},
          {"type": "fn", "expr": "pow(x, X - 1)*exp(-x)", "color": "purple", "from": 0, "label": "t^(x−1)e^(−t)"}],
         [readout("Γ(x) (numerik)", "0.01*sum(1, 2400, k => pow((k - 0.5)*0.01, X - 1)*exp(-(k - 0.5)*0.01))", 4),
          readout("(x − 1)! bila x bulat", "fact(X - 1)", 4)],
         "Puncak integran ada di t = x − 1, dan luasnya tumbuh sangat cepat, persis seperti faktorial.")]),
    S("theorem", "Definisi & sifat dasar Gamma",
      r"""<p>$$\Gamma(x) = \int_0^\infty t^{x-1}e^{-t}\,dt, \qquad x &gt; 0.$$</p>
      <p>Ini integral tak wajar di <b>kedua</b> ujung: di $\infty$ konvergen karena $e^{-t}$ mengalahkan pangkat apa pun; di $0$ konvergen karena $t^{x-1}$ dengan $x - 1 &gt; -1$ (uji-$p$).</p>
      <ul class="lesson-list">
        <li>$\Gamma(x + 1) = x\,\Gamma(x)$ dan $\Gamma(1) = 1$, sehingga $\Gamma(n + 1) = n!$.</li>
        <li>$\Gamma\left(\tfrac12\right) = \sqrt\pi$, jadi $\left(\tfrac12\right)! = \Gamma\left(\tfrac32\right) = \tfrac{\sqrt\pi}{2}$.</li>
        <li>Rumus pantulan: $\Gamma(x)\Gamma(1 - x) = \dfrac{\pi}{\sin\pi x}$. Gamma tidak terdefinisi di $0, -1, -2, \dots$ (kutub).</li>
      </ul>""",
      "Γ(n) = (n − 1)!, BUKAN n!. Pergeseran satu ini sumber salah paling umum."),
    S("derivation", "Membuktikan Γ(x + 1) = xΓ(x) dan Γ(½) = √π",
      r"""<p><b>Rekurensi</b> dengan integrasi parsial, $u = t^x$, $dv = e^{-t}dt$:</p>""" +
      steps(r"$\Gamma(x + 1) = \Big[-t^xe^{-t}\Big]_0^\infty + x\displaystyle\int_0^\infty t^{x-1}e^{-t}dt$.",
            r"Suku batas nol di kedua ujung ($x &gt; 0$; di $\infty$ eksponen menang, L'Hôpital).",
            r"Tersisa $x\,\Gamma(x)$. $\blacksquare$") +
      r"""<p><b>Nilai setengah</b> dengan substitusi $t = u^2$, $dt = 2u\,du$:</p>""" +
      steps(r"$\Gamma\left(\tfrac12\right) = \displaystyle\int_0^\infty t^{-1/2}e^{-t}dt = \int_0^\infty\frac{1}{u}e^{-u^2}2u\,du = 2\int_0^\infty e^{-u^2}du$.",
            r"Integral Gauss (topik Integral Lipat, lewat koordinat kutub): $\displaystyle\int_0^\infty e^{-u^2}du = \tfrac{\sqrt\pi}{2}$. Jadi $\Gamma\left(\tfrac12\right) = \sqrt\pi$."),
      "Perhatikan bagaimana tiga topik berbeda (parsial, integral tak wajar, kutub) bertemu di satu fungsi."),
    S("theorem", "Fungsi Beta & fungsi error",
      r"""<p><b>Beta:</b> $$B(x, y) = \int_0^1 t^{x-1}(1 - t)^{y-1}dt = \frac{\Gamma(x)\Gamma(y)}{\Gamma(x + y)}, \qquad x, y &gt; 0.$$
      Bentuk trigonometri (substitusi $t = \sin^2\theta$): $B(x, y) = 2\displaystyle\int_0^{\pi/2}\sin^{2x-1}\theta\cos^{2y-1}\theta\,d\theta$, sehingga integral Wallis jadi satu baris.</p>
      <p><b>Error function:</b> $$\operatorname{erf}(x) = \frac{2}{\sqrt\pi}\int_0^x e^{-t^2}dt, \qquad \Phi(z) = \frac12\left[1 + \operatorname{erf}\left(\frac{z}{\sqrt2}\right)\right],$$
      dengan $\Phi$ fungsi distribusi kumulatif normal baku (tabel-$z$ statistika). Faktor $\tfrac{2}{\sqrt\pi}$ membuat $\operatorname{erf}(\infty) = 1$.</p>""",
      "Ingat 'parameter Beta = pangkat + 1'. Integran t²(1 − t)³ memberi B(3, 4), bukan B(2, 3)."),
    S("example", "Bedah soal: menghitung dengan Gamma & Beta",
      steps(r"$\Gamma\left(\tfrac52\right) = \tfrac32\cdot\tfrac12\cdot\Gamma\left(\tfrac12\right) = \tfrac{3\sqrt\pi}{4}$.",
            r"$\displaystyle\int_0^\infty x^4e^{-2x}dx$: substitusi $t = 2x$ memberi $\tfrac{1}{2^5}\Gamma(5) = \tfrac{24}{32} = \tfrac34$.",
            r"$\displaystyle\int_0^1 x^2(1 - x)^3dx = B(3, 4) = \frac{\Gamma(3)\Gamma(4)}{\Gamma(7)} = \frac{2\cdot 6}{720} = \frac{1}{60}$.",
            r"$\displaystyle\int_0^{\pi/2}\sin^4\theta\cos^2\theta\,d\theta = \tfrac12B\left(\tfrac52, \tfrac32\right) = \tfrac12\cdot\dfrac{\tfrac{3\sqrt\pi}{4}\cdot\tfrac{\sqrt\pi}{2}}{\Gamma(4)} = \dfrac{\pi}{32}$.") +
      note(r"Volume bola satuan berdimensi $n$: $V_n = \dfrac{\pi^{n/2}}{\Gamma\left(\tfrac n2 + 1\right)}$. Untuk $n = 3$: $\dfrac{\pi^{3/2}}{\Gamma(5/2)} = \tfrac43\pi$."),
      "Langkah 4 tanpa Beta butuh identitas setengah sudut berkali-kali. Dengan Beta, cukup baca pangkatnya."),
    S("pitfall", "Jebakan ujian",
      r"""<ul class="lesson-list">
        <li>$\Gamma(n) = n!$. Salah: $\Gamma(n) = (n - 1)!$.</li>
        <li>Parameter Beta diambil sama dengan pangkat, bukan pangkat $+1$.</li>
        <li>Lupa faktor skala saat substitusi, misalnya $t = 2x$ menghasilkan $\tfrac{1}{2^{x}}$ di depan.</li>
        <li>Memakai $\Gamma$ di bilangan bulat non-positif ($\Gamma(0)$ tidak ada).</li>
        <li>Melupakan faktor $\tfrac{2}{\sqrt\pi}$ atau $\sqrt2$ saat mengubah $\operatorname{erf}$ ke $\Phi$.</li>
      </ul>""",
      "Uji kewajaran: Γ(1) = Γ(2) = 1, Γ(3) = 2. Cek rumusmu di nilai-nilai ini."),
    S("checkpoint", "Mini checkpoint",
      qa(r"1. $\Gamma\left(\tfrac72\right)$", r"<p>$\tfrac52\cdot\tfrac32\cdot\tfrac12\sqrt\pi = \tfrac{15\sqrt\pi}{8}$.</p>") +
      qa(r"2. $\displaystyle\int_0^\infty x^2e^{-x^2}dx$", r"<p>$t = x^2$: $\tfrac12\displaystyle\int_0^\infty t^{1/2}e^{-t}dt = \tfrac12\Gamma\left(\tfrac32\right) = \tfrac{\sqrt\pi}{4}$.</p>") +
      qa(r"3. $\displaystyle\int_0^1\sqrt x\,(1 - x)\,dx$ dengan Beta.", r"<p>$B\left(\tfrac32, 2\right) = \dfrac{\Gamma(3/2)\Gamma(2)}{\Gamma(7/2)} = \dfrac{\sqrt\pi/2}{15\sqrt\pi/8} = \dfrac{4}{15}$. Cek langsung: $\tfrac23 - \tfrac25 = \tfrac{4}{15}$.</p>"),
      "Soal 2 adalah momen kedua distribusi normal yang tersembunyi. Gamma membuatnya satu baris."),
]

# ═══════════════════════════════════════════════════════════════════════════
# FMIPA 3. Pengantar Analisis Real
# ═══════════════════════════════════════════════════════════════════════════
ANALISIS = [
    S("intuition", "Mengapa kalkulus butuh fondasi",
      r"""<p>Teorema Nilai Antara, Teorema Nilai Ekstrem, dan konvergensi deret semuanya bergantung pada satu sifat ℝ yang tidak dimiliki ℚ:
      <b>kelengkapan</b>. Di ℚ, persamaan $x^2 = 2$ tidak punya solusi, sehingga $f(x) = x^2 - 2$ berganti tanda di $[1, 2]$ tanpa pernah nol.</p>
      <p>Analisis real juga menjawab pertanyaan berbahaya: bolehkah limit dan integral ditukar? Bolehkah deret diturunkan suku demi suku? Jawabannya "tidak selalu", dan analisis memberi tahu kapan.</p>""",
      "Analisis Real adalah 'Kalkulus dengan bukti'. Hampir semua yang kamu pakai di Kalkulus 1–3 dibuktikan ulang di sini."),
    S("theorem", "Aksioma kelengkapan: supremum & infimum",
      r"""<p>Setiap himpunan tak kosong $A \subset \mathbb{R}$ yang terbatas di atas punya <b>batas atas terkecil</b> $\sup A$ di ℝ.</p>
      <p><b>Karakterisasi ε:</b> $s = \sup A$ jika dan hanya jika (i) $a \le s$ untuk semua $a \in A$, dan (ii) untuk setiap $\varepsilon &gt; 0$ ada $a \in A$ dengan $a &gt; s - \varepsilon$.</p>
      <p><b>Sifat Archimedes:</b> untuk setiap $x \in \mathbb{R}$ ada $n \in \mathbb{N}$ dengan $n &gt; x$. Akibatnya $\inf\{\tfrac1n\} = 0$.</p>
      <p><b>Contoh:</b> $\sup\left\{1 - \tfrac1n\right\} = 1$, tetapi $1$ tidak termuat di himpunan: supremum tidak harus dicapai. Jika dicapai, ia disebut maksimum.</p>""",
      "Bukti supremum selalu dua bagian: tunjukkan s batas atas, lalu tunjukkan tidak ada batas atas yang lebih kecil (pakai ε)."),
    S("theorem", "Barisan: definisi ε–N & teorema konvergensi",
      r"""<p>$a_n \to L \iff \forall\varepsilon &gt; 0\ \exists N\ \forall n \ge N:\ |a_n - L| &lt; \varepsilon$.</p>
      <ul class="lesson-list">
        <li><b>Teorema Konvergensi Monoton:</b> barisan monoton dan terbatas pasti konvergen (ke sup atau inf-nya). Inilah kelengkapan yang bekerja.</li>
        <li><b>Bolzano–Weierstrass:</b> setiap barisan terbatas punya subbarisan yang konvergen.</li>
        <li><b>Barisan Cauchy:</b> $\forall\varepsilon\ \exists N\ \forall m, n \ge N:\ |a_m - a_n| &lt; \varepsilon$. Di ℝ, Cauchy $\iff$ konvergen; berguna saat limitnya belum diketahui.</li>
      </ul>""",
      "Perkecil ε dan lihat N yang dibutuhkan membesar. Setelah indeks N, semua titik merah harus berada di pita.",
      [g("aₙ = 1 + (−1)ⁿ/n dan pita ε", [0, 31], [-0.1, 2.1], [param("eps", "ε", 0.04, 0.6, 0.01, 0.2, "ε")],
         [{"type": "hband", "from": "1 - eps", "to": "1 + eps", "color": "green", "opacity": 0.18},
          {"type": "iter", "init": {"n": 1, "a": 0}, "update": {"n": "n + 1", "a": "1 + pow(-1, n + 1)/(n + 1)"}, "steps": 29, "color": "red"},
          {"type": "vline", "x": "1/eps", "color": "orange", "dash": True}],
         [readout("N > 1/ε", "1/eps", 3)],
         "|aₙ − 1| = 1/n < ε tepat ketika n > 1/ε (garis oranye).")]),
    S("example", "Bedah soal: bukti ε–N & barisan rekursif",
      r"""<p><b>Soal 1.</b> Buktikan $\dfrac{n}{n + 1} \to 1$.</p>""" +
      steps(r"Coretan: $\left|\dfrac{n}{n + 1} - 1\right| = \dfrac{1}{n + 1} &lt; \dfrac1n$. Cukup $n &gt; \tfrac1\varepsilon$.",
            r"Bukti: ambil $\varepsilon &gt; 0$; menurut Archimedes ada $N &gt; \tfrac1\varepsilon$. Untuk $n \ge N$: $\left|\tfrac{n}{n + 1} - 1\right| &lt; \tfrac1n \le \tfrac1N &lt; \varepsilon$. $\blacksquare$") +
      r"""<p><b>Soal 2.</b> $a_1 = \sqrt2$, $a_{n+1} = \sqrt{2 + a_n}$. Buktikan konvergen dan cari limitnya.</p>""" +
      steps(r"Terbatas: induksi, jika $a_n &lt; 2$ maka $a_{n+1} &lt; \sqrt{4} = 2$.",
            r"Naik: $a_{n+1}^2 - a_n^2 = 2 + a_n - a_n^2 = (2 - a_n)(1 + a_n) &gt; 0$.",
            r"Monoton dan terbatas, jadi konvergen ke suatu $L$. Ambil limit kedua ruas: $L = \sqrt{2 + L} \Rightarrow L = 2$ (tolak $L = -1$)."),
      "Urutan di Soal 2 penting: buktikan konvergen DULU, baru boleh mengambil limit kedua ruas."),
    S("theorem", "Kontinuitas seragam",
      r"""<p>$f$ <b>kontinu seragam</b> pada $I$ jika $\forall\varepsilon &gt; 0\ \exists\delta &gt; 0\ \forall x, y \in I:\ |x - y| &lt; \delta \Rightarrow |f(x) - f(y)| &lt; \varepsilon$.
      Bedanya dengan kontinu biasa: satu $\delta$ berlaku untuk <b>semua</b> titik sekaligus.</p>
      <ul class="lesson-list">
        <li>$f(x) = \tfrac1x$ pada $(0, 1)$ kontinu tetapi tidak seragam: makin dekat $0$, makin curam, $\delta$ harus makin kecil.</li>
        <li>$f(x) = x^2$ pada ℝ juga tidak seragam (makin curam ke tak hingga), tetapi seragam pada $[0, 10]$.</li>
        <li><b>Teorema Heine:</b> fungsi kontinu pada interval tertutup dan terbatas pasti kontinu seragam. Inilah alasan fungsi kontinu pada $[a, b]$ terintegralkan Riemann.</li>
      </ul>""",
      "Kontinu seragam = ada satu 'tingkat toleransi mesin' yang cukup di seluruh domain, tidak perlu disetel ulang di tiap titik."),
    S("theorem", "Konvergensi titik demi titik vs seragam",
      r"""<p>$f_n \to f$ <b>titik demi titik</b> jika untuk tiap $x$, $f_n(x) \to f(x)$ ($N$ boleh bergantung pada $x$).
      <b>Seragam</b> jika $\displaystyle\sup_{x \in I}|f_n(x) - f(x)| \to 0$ (satu $N$ untuk semua $x$).</p>
      <ul class="lesson-list">
        <li>$f_n(x) = x^n$ pada $[0, 1]$ menuju fungsi tak kontinu ($0$ untuk $x &lt; 1$, $1$ di $x = 1$): konvergen titik demi titik, tidak seragam.</li>
        <li>Limit seragam fungsi kontinu adalah kontinu, dan $\lim\int f_n = \int\lim f_n$ boleh.</li>
        <li><b>Contoh tukar limit yang gagal:</b> $f_n(x) = nx(1 - x^2)^n$ pada $[0, 1]$ menuju $0$ titik demi titik, tetapi $\int_0^1 f_n = \tfrac{n}{2(n + 1)} \to \tfrac12 \ne 0$.</li>
        <li><b>Uji-M Weierstrass:</b> jika $|f_n(x)| \le M_n$ dan $\sum M_n$ konvergen, maka $\sum f_n$ konvergen seragam.</li>
      </ul>""",
      "Geser n: kurva xⁿ selalu punya titik dekat x = 1 yang masih jauh dari 0. Itulah mengapa sup|fₙ − f| tidak menuju 0.",
      [g("fₙ(x) = xⁿ pada [0, 1]", [-0.05, 1.1], [-0.05, 1.1], [param("N", "n", 1, 60, 1, 5, "n"), param("c", "Batas kanan c < 1", 0.5, 0.99, 0.01, 0.9, "c")],
         [{"type": "fn", "expr": "pow(x, N)", "color": "blue", "from": 0, "to": 1, "label": "xⁿ"},
          {"type": "vline", "x": "c", "color": "orange", "dash": True}],
         [readout("sup |xⁿ − 0| pada [0, c] = cⁿ", "pow(c, N)", 5), readout("sup pada [0, 1) (selalu)", "1", 1)],
         "Pada [0, c] dengan c < 1 konvergensinya seragam (cⁿ → 0); pada [0, 1) tidak.")]),
    S("example", "Bedah soal: membuktikan (tidak) seragam",
      r"""<p><b>Soal 1.</b> $x^n \to 0$ seragam pada $\left[0, \tfrac12\right]$?</p>""" +
      steps(r"$\sup_{[0, 1/2]}|x^n - 0| = \left(\tfrac12\right)^n \to 0$. Ya, seragam.") +
      r"""<p><b>Soal 2.</b> Pada $[0, 1)$?</p>""" +
      steps(r"Untuk setiap $n$, pilih $x_n = \left(\tfrac12\right)^{1/n} \in [0, 1)$: $x_n^n = \tfrac12$.",
            r"Jadi $\sup|x^n| \ge \tfrac12$ untuk semua $n$, tidak menuju $0$. Tidak seragam.") +
      r"""<p><b>Soal 3.</b> $\displaystyle\sum_{n=1}^\infty\frac{\sin(nx)}{n^2}$ kontinu di ℝ?</p>""" +
      steps(r"$\left|\tfrac{\sin nx}{n^2}\right| \le \tfrac{1}{n^2} = M_n$, dan $\sum\tfrac{1}{n^2}$ konvergen.",
            r"Uji-M: konvergen seragam; tiap suku kontinu, jadi jumlahnya kontinu."),
      "Untuk membuktikan TIDAK seragam, cari barisan titik xₙ yang 'mengejar' kegagalan, seperti xₙ = (1/2)^(1/n)."),
    S("pitfall", "Jebakan ujian",
      r"""<ul class="lesson-list">
        <li>Menganggap supremum selalu anggota himpunan.</li>
        <li>Bukti konvergensi seragam dengan $N$ yang bergantung pada $x$.</li>
        <li>Menukar limit dengan integral atau turunan tanpa alasan (lihat $nx(1 - x^2)^n$).</li>
        <li>Kontinu disamakan dengan kontinu seragam.</li>
        <li>Bolzano–Weierstrass dipakai pada barisan yang tidak terbatas.</li>
        <li>Mengambil limit kedua ruas rumus rekursif sebelum membuktikan barisannya konvergen (misal $a_{n+1} = 2a_n$ "memberi" $L = 0$).</li>
      </ul>""",
      "Jebakan terakhir contoh klasik: aₙ₊₁ = 2aₙ dengan a₁ = 1 jelas divergen, tapi 'L = 2L' memberi L = 0."),
    S("checkpoint", "Mini checkpoint",
      qa(r"1. $\sup$ dan $\inf$ dari $\left\{(-1)^n + \tfrac1n : n \in \mathbb{N}\right\}$.",
         r"<p>Anggota: $0, \tfrac32, -\tfrac23, \tfrac54, \dots$. $\sup = \tfrac32$ (dicapai di $n = 2$); $\inf = -1$ (tidak dicapai).</p>") +
      qa(r"2. Apakah $f_n(x) = \tfrac{x}{n}$ konvergen seragam pada $[0, 1]$? Pada ℝ?",
         r"<p>Pada $[0, 1]$: $\sup = \tfrac1n \to 0$, seragam. Pada ℝ: $\sup = \infty$, tidak seragam.</p>"),
      "Soal 2 menunjukkan bahwa domain menentukan keseragaman. Fungsi yang sama, kesimpulan berbeda."),
]

NEW_TOPICS = [
    {"after": "kl-fk-asimtotik", "slug": "kl-fk-numerik", "title": "Metode Numerik: Newton-Raphson & Simpson", "icon": "m-tangent",
     "summary": "Newton-Raphson, biseksi, konvergensi kuadratik, aturan trapesium & Simpson beserta batas galat.",
     "references": "Burden & Faires Bab 2 & 4; Stewart §4.8, §7.7"},
    {"after": "kl-fm-fk-gamma", "slug": "kl-fm-epsilon-delta", "title": "Pembuktian Formal Limit (ε–δ)", "icon": "m-limit",
     "summary": "Definisi ε–δ, struktur bukti, membatasi δ, negasi kuantor, bukti hukum limit.",
     "references": "Stewart §2.4; Bartle & Sherbert Bab 4"},
]

SLIDES = {
    "kl-fk-asimtotik": ASIMTOTIK,
    "kl-fk-numerik": NUMERIK,
    "kl-fk-gd": GRADIENT_DESCENT,
    "kl-fm-epsilon-delta": EPSILON_DELTA,
    "kl-fm-fk-gamma": GAMMA,
    "kl-fm-fk-analisis": ANALISIS,
}
