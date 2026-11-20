r"""
Kurikulum v2 — Batch 4 (bagian D): jalur spesialisasi Fakultas Teknik.

Topik: Persamaan Diferensial Orde Dua (osilator teredam, resonansi) · Deret Fourier · Transformasi Laplace.
Contoh disesuaikan untuk FT: sistem pegas–peredam, rangkaian RLC/RL, filter sinyal, dan sistem kendali.

Rujukan: Kreyszig, Advanced Engineering Mathematics Bab 2, 6, 11; Stewart 9e §17.1–17.3;
Boyce & DiPrima Bab 3 & 6; OpenStax Calculus Vol 3 Bab 7.
"""

from ..helpers import param, readout
from .l1_slides import S, g, note, qa, steps
from .l3_slides import pohon

# Solusi m = 1, x(0) = 1, x'(0) = 0 untuk x'' + c x' + k x = 0 (tiga kasus redaman dalam satu ekspresi).
_OSILATOR = ("(c*c - 4*k) < -1e-9 ? exp(-c*x/2)*(cos(sqrt(4*k - c*c)/2*x) + (c/sqrt(4*k - c*c))*sin(sqrt(4*k - c*c)/2*x))"
             " : ((c*c - 4*k) > 1e-9 ? (((-c - sqrt(c*c - 4*k))/2)*exp(((-c + sqrt(c*c - 4*k))/2)*x)"
             " - ((-c + sqrt(c*c - 4*k))/2)*exp(((-c - sqrt(c*c - 4*k))/2)*x))/(-sqrt(c*c - 4*k))"
             " : (1 + c*x/2)*exp(-c*x/2))")

# ═══════════════════════════════════════════════════════════════════════════
# FT 1. Persamaan Diferensial Orde Dua (topik baru)
# ═══════════════════════════════════════════════════════════════════════════
PD_ORDE2 = [
    S("intuition", "Hukum Newton melahirkan turunan kedua",
      r"""<p>$F = ma$ dan $a = x''$. Untuk massa pada pegas dengan peredam:
      $$m x'' + c x' + k x = F(t)$$
      (gaya pegas $-kx$, gaya redaman $-cx'$). Persamaan yang <b>persis sama</b> mengatur rangkaian RLC: $Lq'' + Rq' + \tfrac{1}{C}q = E(t)$,
      dengan induktor ↔ massa, resistor ↔ peredam, kapasitor ↔ pegas. Suspensi mobil, peredam gempa gedung, dan rangkaian tuning radio semuanya satu model.</p>""",
      "Ubah redaman c. Kecil: berosilasi lama (seperti per mobil rusak). Besar: kembali lambat tanpa osilasi. Di tengahnya ada titik ideal.",
      [g("x'' + c x' + k x = 0, x(0) = 1, x'(0) = 0", [0, 10], [-1.1, 1.1], [param("c", "Redaman c", 0, 8, 0.1, 0.6, "c"), param("k", "Kekakuan k", 1, 9, 0.25, 4, "k")],
         [{"type": "fn", "expr": _OSILATOR, "color": "blue", "label": "x(t)"},
          {"type": "fn", "expr": "exp(-c*x/2)", "color": "gray", "dash": True, "label": "selubung e^(−ct/2)"},
          {"type": "hline", "y": 0, "color": "gray"}],
         [readout("Rasio redaman ζ = c/(2√k)", "c/(2*sqrt(k))", 3), readout("Frekuensi alami ω₀ = √k", "sqrt(k)", 3),
          readout("Frekuensi teredam ω_d", "sqrt(max(k - c*c/4, 0))", 3)],
         "ζ < 1 kurang teredam (berosilasi), ζ = 1 teredam kritis, ζ > 1 terlalu teredam. Coba k = 4, c = 4.")]),
    S("theorem", "PD linear homogen berkoefisien konstan",
      r"""<p>Untuk $ay'' + by' + cy = 0$, coba $y = e^{rt}$: diperoleh <b>persamaan karakteristik</b> $ar^2 + br + c = 0$.</p>
      <div class="table-scroll"><table class="lesson-table"><thead><tr><th>Akar</th><th>Solusi umum</th></tr></thead><tbody>
        <tr><td>real berbeda $r_1 \ne r_2$</td><td>$y = C_1e^{r_1t} + C_2e^{r_2t}$</td></tr>
        <tr><td>real kembar $r$</td><td>$y = (C_1 + C_2t)e^{rt}$</td></tr>
        <tr><td>kompleks $\alpha \pm i\beta$</td><td>$y = e^{\alpha t}(C_1\cos\beta t + C_2\sin\beta t)$</td></tr>
      </tbody></table></div>
      <p>Kasus kompleks berasal dari rumus Euler $e^{i\beta t} = \cos\beta t + i\sin\beta t$ (deret Maclaurin dari Level 3!). <b>Prinsip superposisi:</b> kombinasi linear solusi juga solusi.</p>""",
      "PD orde dua butuh DUA syarat awal (posisi dan kecepatan) untuk menentukan C₁ dan C₂."),
    S("example", "Bedah soal: tiga kasus akar",
      r"""<p><b>Soal 1.</b> $y'' + y' - 6y = 0$, $y(0) = 1$, $y'(0) = 0$.</p>""" +
      steps(r"$r^2 + r - 6 = (r + 3)(r - 2) = 0$, jadi $y = C_1e^{2t} + C_2e^{-3t}$.",
            r"$C_1 + C_2 = 1$ dan $2C_1 - 3C_2 = 0$, sehingga $C_1 = \tfrac35$, $C_2 = \tfrac25$.") +
      r"""<p><b>Soal 2.</b> $y'' - 6y' + 13y = 0$: $r = \dfrac{6 \pm \sqrt{36 - 52}}{2} = 3 \pm 2i$, jadi $y = e^{3t}(C_1\cos 2t + C_2\sin 2t)$ (berosilasi dan membesar).</p>
      <p><b>Soal 3.</b> $y'' + 4y' + 4y = 0$: $(r + 2)^2 = 0$, akar kembar, jadi $y = (C_1 + C_2t)e^{-2t}$.</p>""",
      "Bagian real akar (α) menentukan tumbuh/meluruh, bagian imajiner (β) menentukan frekuensi osilasi."),
    S("theorem", "Klasifikasi redaman (sistem pegas–peredam)",
      r"""<p>Untuk $mx'' + cx' + kx = 0$: $\ \omega_0 = \sqrt{k/m}$ (frekuensi alami), $\ \zeta = \dfrac{c}{2\sqrt{mk}}$ (rasio redaman).</p>
      <div class="table-scroll"><table class="lesson-table"><thead><tr><th>$\zeta$</th><th>Akar</th><th>Perilaku</th><th>Contoh</th></tr></thead><tbody>
        <tr><td>$0 &lt; \zeta &lt; 1$</td><td>kompleks</td><td>berosilasi, amplitudo meluruh</td><td>garpu tala, per mobil aus</td></tr>
        <tr><td>$\zeta = 1$</td><td>kembar</td><td>kembali tercepat tanpa osilasi</td><td>target desain suspensi, alat ukur jarum</td></tr>
        <tr><td>$\zeta &gt; 1$</td><td>real berbeda</td><td>kembali lambat tanpa osilasi</td><td>penutup pintu hidrolik</td></tr>
      </tbody></table></div>
      <p>Frekuensi osilasi teredam $\omega_d = \omega_0\sqrt{1 - \zeta^2}$ sedikit lebih kecil dari $\omega_0$.</p>""",
      "Insinyur jarang memilih ζ tepat 1. Suspensi mobil biasanya sedikit di bawah 1 (sekitar 0,2–0,7) agar nyaman tapi tetap stabil."),
    S("theorem", "PD tak homogen: koefisien tak tentu",
      r"""<p>Solusi umum $y = y_h + y_p$: solusi homogen ditambah <b>satu</b> solusi khusus.</p>
      <div class="table-scroll"><table class="lesson-table"><thead><tr><th>Ruas kanan $F(t)$</th><th>Tebakan $y_p$</th></tr></thead><tbody>
        <tr><td>polinom derajat $n$</td><td>polinom derajat $n$ (semua koefisien)</td></tr>
        <tr><td>$e^{kt}$</td><td>$Ae^{kt}$</td></tr>
        <tr><td>$\cos\omega t$ atau $\sin\omega t$</td><td>$A\cos\omega t + B\sin\omega t$</td></tr>
        <tr><td>hasil kali dari yang di atas</td><td>hasil kali tebakannya</td></tr>
      </tbody></table></div>""" +
      pohon(r"Selesaikan $y_h$ dulu.",
            r"Tulis tebakan $y_p$ dari tabel.",
            r"Ada suku tebakan yang sudah merupakan solusi $y_h$? Kalikan tebakan dengan $t$ (atau $t^2$ bila akar kembar). Ini kasus <b>resonansi</b>.",
            r"Substitusi ke PD, samakan koefisien, lalu terapkan syarat awal pada $y = y_h + y_p$ (bukan pada $y_h$ saja).") +
      note(r"Untuk ruas kanan lain ($\tan t$, $\tfrac1t$) pakai <b>variasi parameter</b> atau transformasi Laplace."),
      "Langkah 3 sering terlupa. Tanpa faktor t, sistem persamaan koefisiennya tidak konsisten (misal 0 = 1)."),
    S("example", "Bedah soal: koefisien tak tentu",
      r"""<p><b>Soal.</b> $y'' + y' - 2y = x^2$.</p>""" +
      steps(r"$y_h$: $r^2 + r - 2 = (r + 2)(r - 1)$, sehingga $y_h = C_1e^{x} + C_2e^{-2x}$.",
            r"Tebakan $y_p = Ax^2 + Bx + C$: $\ y_p'' + y_p' - 2y_p = -2Ax^2 + (2A - 2B)x + (2A + B - 2C)$.",
            r"Samakan dengan $x^2$: $-2A = 1$, $2A - 2B = 0$, $2A + B - 2C = 0$, sehingga $A = -\tfrac12$, $B = -\tfrac12$, $C = -\tfrac34$.",
            r"$y = C_1e^{x} + C_2e^{-2x} - \tfrac12x^2 - \tfrac12x - \tfrac34$."),
      "Polinom derajat 2 di ruas kanan butuh tebakan LENGKAP Ax² + Bx + C, walaupun ruas kanannya cuma x²."),
    S("example", "Resonansi & kurva respons frekuensi",
      r"""<p>Sistem tak teredam $x'' + \omega_0^2x = F_0\cos\omega t$:</p>""" +
      steps(r"$\omega \ne \omega_0$: $x_p = \dfrac{F_0}{\omega_0^2 - \omega^2}\cos\omega t$. Amplitudo membesar saat $\omega$ mendekati $\omega_0$.",
            r"$\omega = \omega_0$: tebakan $\cos\omega_0t$ sudah ada di $y_h$, jadi kalikan $t$: $x_p = \dfrac{F_0}{2\omega_0}t\sin\omega_0t$. Amplitudo tumbuh tanpa batas: <b>resonansi</b>.") +
      r"""<p>Dengan redaman, amplitudo tetap terbatas: $A(\omega) = \dfrac{F_0}{\sqrt{(k - m\omega^2)^2 + (c\omega)^2}}$. Karena itu jembatan dan gedung dirancang
      dengan redaman cukup dan frekuensi alami yang jauh dari getaran pemicu (langkah kaki, angin, mesin), dan pasukan diminta tidak berbaris seirama saat melintasi jembatan.</p>""",
      "Perkecil c: puncak di ω₀ makin tinggi dan tajam. Inilah alasan radio bisa 'memilih' satu stasiun (rangkaian RLC beredaman kecil).",
      [g("Faktor pembesaran k·A(ω) (m = 1, k = 4)", [0, 5], [0, 8], [param("c", "Redaman c", 0.2, 4, 0.05, 0.5, "c")],
         [{"type": "fn", "expr": "4/sqrt(pow(4 - x*x, 2) + pow(c*x, 2))", "color": "red", "label": "pembesaran"},
          {"type": "vline", "x": 2, "color": "gray", "dash": True}],
         [readout("Pembesaran di ω₀ = 2", "4/(2*c)", 3), readout("ζ", "c/4", 3)],
         "Garis abu-abu = frekuensi alami ω₀ = 2.")]),
    S("pitfall", "Jebakan ujian",
      r"""<ul class="lesson-list">
        <li>Akar kembar ditulis $C_1e^{rt} + C_2e^{rt}$; itu hanya satu solusi. Butuh $(C_1 + C_2t)e^{rt}$.</li>
        <li>Akar kompleks: memakai $e^{\beta t}$ alih-alih $\cos\beta t$, $\sin\beta t$.</li>
        <li>Lupa mengalikan tebakan dengan $t$ saat tumpang tindih dengan $y_h$.</li>
        <li>Menerapkan syarat awal pada $y_h$ sebelum menambahkan $y_p$.</li>
        <li>Tebakan tidak lengkap: untuk $\sin\omega t$ hanya menulis $B\sin\omega t$ tanpa $A\cos\omega t$.</li>
      </ul>""",
      "Selalu cek: substitusi y_p kembali ke PD. Ini cara paling cepat menemukan salah koefisien."),
    S("checkpoint", "Mini checkpoint",
      qa(r"1. Massa $2$ kg, pegas $k = 50$ N/m, tanpa redaman. Frekuensi alami dan periodenya?", r"<p>$\omega_0 = \sqrt{50/2} = 5$ rad/s; periode $\tfrac{2\pi}{5} \approx 1.26$ s.</p>") +
      qa(r"2. Bentuk tebakan $y_p$ untuk $y'' - 4y = e^{2t}$.", r"<p>Akar $\pm2$; $e^{2t}$ sudah di $y_h$, jadi $y_p = Ate^{2t}$.</p>") +
      qa(r"3. Berapa $c$ agar $x'' + cx' + 9x = 0$ teredam kritis?", r"<p>$c^2 = 4\cdot 9$, jadi $c = 6$.</p>"),
      "Soal 3: teredam kritis tepat saat diskriminan persamaan karakteristik nol, c² = 4mk."),
]

# ═══════════════════════════════════════════════════════════════════════════
# FT 2. Deret Fourier (topik baru)
# ═══════════════════════════════════════════════════════════════════════════
FOURIER = [
    S("intuition", "Setiap sinyal periodik adalah paduan nada",
      r"""<p>Suara gitar, arus listrik dari inverter, dan getaran mesin semuanya periodik. Fourier menunjukkan bahwa sinyal periodik apa pun (bahkan gelombang kotak yang patah-patah)
      bisa ditulis sebagai jumlah sinus dan kosinus: frekuensi dasar plus <b>harmonik-harmoniknya</b>.</p>
      <p>Equalizer musik, kompresi MP3 dan JPEG, analisis getaran mesin, dan pengukuran distorsi harmonik di sistem tenaga listrik semuanya berdiri di atas ide ini.</p>""",
      "Tambah N. Gelombang kotak makin tajam, tapi selalu ada 'tanduk' sekitar 9% di dekat lompatan: fenomena Gibbs.",
      [g("Gelombang kotak & jumlah parsial Fourier", [-7, 7], [-1.6, 1.6], [param("N", "Banyak harmonik ganjil", 0, 30, 1, 3, "N")],
         [{"type": "fn", "expr": "sign(sin(x))", "color": "gray", "label": "gelombang kotak"},
          {"type": "fn", "expr": "sum(0, N, k => 4/pi*sin((2*k + 1)*x)/(2*k + 1))", "color": "blue", "label": "jumlah parsial"}],
         [readout("Puncak dekat lompatan", "sum(0, N, k => 4/pi*sin((2*k + 1)*pi/(2*N + 2))/(2*k + 1))", 4), readout("Batas Gibbs", "1.17898", 5)],
         "Lebar tanduk mengecil, tetapi tingginya mendekati ≈ 1,179 (bukan 1) sebanyak apa pun suku ditambahkan.")]),
    S("theorem", "Deret Fourier & ortogonalitas",
      r"""<p>Untuk $f$ berperiode $2L$:
      $$f(x) \sim \frac{a_0}{2} + \sum_{n=1}^{\infty}\left(a_n\cos\frac{n\pi x}{L} + b_n\sin\frac{n\pi x}{L}\right),$$
      $$a_n = \frac1L\int_{-L}^{L}f(x)\cos\frac{n\pi x}{L}\,dx, \qquad b_n = \frac1L\int_{-L}^{L}f(x)\sin\frac{n\pi x}{L}\,dx.$$</p>
      <p>Kunci di baliknya: <b>ortogonalitas</b>. Untuk $m \ne n$, $\int_{-\pi}^{\pi}\sin mx\sin nx\,dx = 0$, $\int_{-\pi}^{\pi}\cos mx\cos nx\,dx = 0$, dan $\int_{-\pi}^{\pi}\sin mx\cos nx\,dx = 0$ untuk semua $m, n$.</p>""",
      "Periode 2π: L = π, rumusnya jadi (1/π)∫ f cos nx dx. Cek periode soal sebelum memasukkan rumus."),
    S("derivation", "Mengapa koefisiennya seperti itu: proyeksi",
      r"""<p>Analogi aljabar linear: komponen vektor $\mathbf{v}$ pada basis ortogonal $\mathbf{e}_n$ adalah $\dfrac{\mathbf{v}\cdot\mathbf{e}_n}{\mathbf{e}_n\cdot\mathbf{e}_n}$.
      Untuk fungsi, "hasil kali titik"-nya adalah integral $\langle f, g\rangle = \int_{-\pi}^{\pi}f g\,dx$.</p>""" +
      steps(r"Kalikan kedua ruas deret dengan $\cos mx$ dan integralkan dari $-\pi$ ke $\pi$.",
            r"Ortogonalitas membuat <b>semua</b> suku lenyap kecuali suku $n = m$ pada bagian kosinus.",
            r"Suku itu bernilai $a_m\int_{-\pi}^{\pi}\cos^2mx\,dx = a_m\pi$.",
            r"Jadi $a_m = \dfrac1\pi\displaystyle\int_{-\pi}^{\pi}f(x)\cos mx\,dx$. Sama untuk $b_m$ dengan $\sin mx$.") ,
      "Koefisien Fourier = 'seberapa mirip f dengan cos mx'. Itulah yang ditampilkan grafik spektrum di equalizer."),
    S("example", "Bedah soal: gelombang kotak",
      r"""<p><b>Soal.</b> $f(x) = -1$ untuk $-\pi &lt; x &lt; 0$, $f(x) = 1$ untuk $0 &lt; x &lt; \pi$, berperiode $2\pi$.</p>""" +
      steps(r"$f$ ganjil, sehingga $a_n = 0$ untuk semua $n$ (integran ganjil pada interval simetris).",
            r"$b_n = \dfrac2\pi\displaystyle\int_0^{\pi}\sin nx\,dx = \dfrac{2}{\pi}\cdot\dfrac{1 - \cos n\pi}{n} = \dfrac{2(1 - (-1)^n)}{n\pi}$.",
            r"$b_n = \dfrac{4}{n\pi}$ untuk $n$ ganjil, $0$ untuk $n$ genap.",
            r"$f(x) = \dfrac4\pi\left(\sin x + \dfrac{\sin 3x}{3} + \dfrac{\sin 5x}{5} + \dots\right)$.") +
      note(r"Masukkan $x = \tfrac{\pi}{2}$: $1 = \tfrac4\pi\left(1 - \tfrac13 + \tfrac15 - \dots\right)$, jadi $\tfrac{\pi}{4} = 1 - \tfrac13 + \tfrac15 - \dots$ (deret Leibniz dari Level 3)."),
      "Gelombang kotak hanya punya harmonik ganjil, dengan amplitudo turun 1/n. Itulah 'suara' khasnya yang kasar."),
    S("theorem", "Konvergensi, simetri, dan Parseval",
      r"""<ul class="lesson-list">
        <li><b>Dirichlet:</b> untuk $f$ mulus sepotong-sepotong, deret konvergen ke $f(x)$ di titik kontinu dan ke <b>rata-rata</b> $\tfrac12[f(x^+) + f(x^-)]$ di titik lompatan.</li>
        <li><b>Gibbs:</b> di dekat lompatan, jumlah parsial melampaui sekitar $9\%$ dari besar lompatan, dan ini tidak hilang walau $N \to \infty$.</li>
        <li><b>Simetri:</b> $f$ genap → hanya kosinus ($b_n = 0$); $f$ ganjil → hanya sinus ($a_n = 0$). Integral cukup dihitung pada $[0, L]$ lalu dikali $2$.</li>
        <li><b>Parseval:</b> $\dfrac1L\displaystyle\int_{-L}^{L}f^2\,dx = \dfrac{a_0^2}{2} + \sum_{n=1}^{\infty}\left(a_n^2 + b_n^2\right)$. Energi sinyal terbagi ke harmonik-harmoniknya; dasar perhitungan nilai RMS dan THD.</li>
      </ul>""",
      "Cek simetri dulu. Separuh koefisien bisa langsung ditulis 0 tanpa menghitung satu integral pun."),
    S("example", "Bedah soal: gelombang gigi gergaji & soal Basel",
      r"""<p><b>Soal.</b> $f(x) = x$ pada $(-\pi, \pi)$, berperiode $2\pi$.</p>""" +
      steps(r"$f$ ganjil, jadi $a_n = 0$; $\ b_n = \dfrac2\pi\displaystyle\int_0^{\pi}x\sin nx\,dx$.",
            r"Parsial: $\displaystyle\int_0^{\pi}x\sin nx\,dx = \left[-\frac{x\cos nx}{n}\right]_0^{\pi} + \frac1n\int_0^{\pi}\cos nx\,dx = -\frac{\pi\cos n\pi}{n}$.",
            r"$b_n = \dfrac{2(-1)^{n+1}}{n}$, sehingga $x = 2\left(\sin x - \dfrac{\sin 2x}{2} + \dfrac{\sin 3x}{3} - \dots\right)$.",
            r"Parseval: $\dfrac1\pi\displaystyle\int_{-\pi}^{\pi}x^2dx = \dfrac{2\pi^2}{3} = \sum\dfrac{4}{n^2}$, jadi $\displaystyle\sum_{n=1}^{\infty}\frac{1}{n^2} = \frac{\pi^2}{6}$.") +
      note(r"Langkah 4 menjawab soal Basel (Euler, 1734) dalam dua baris. Bandingkan dengan grafik deret-$p$ di Level 3 yang mendatar di $\pi^2/6$."),
      "Integral x sin nx dan x cos nx adalah integral parsial yang muncul di hampir setiap soal Fourier. Hafalkan polanya."),
    S("example", "Fourier di dunia teknik: filter RC",
      r"""<p>Gelombang kotak masuk ke filter lolos-rendah RC. Setiap harmonik $\sin(nx)$ diperlakukan terpisah (sistem linear):
      amplitudonya dikali $\dfrac{1}{\sqrt{1 + (na)^2}}$ dan fasenya bergeser $-\arctan(na)$, dengan $a = \omega RC$. Harmonik tinggi diredam paling kuat,
      sehingga sudut-sudut tajam membulat.</p>
      <p>Pola "uraikan, olah tiap frekuensi, jumlahkan kembali" juga menyelesaikan persamaan panas $u_t = ku_{xx}$:
      $u(x, t) = \sum b_ne^{-n^2kt}\sin nx$, dan harmonik tinggi meluruh paling cepat.</p>""",
      "Naikkan a (RC lebih besar): keluaran makin halus dan mirip gelombang segitiga. Begitulah equalizer memotong frekuensi tinggi.",
      [g("Keluaran filter RC untuk masukan gelombang kotak", [-7, 7], [-1.6, 1.6], [param("a", "a = ωRC", 0, 3, 0.05, 0.5, "a")],
         [{"type": "fn", "expr": "sign(sin(x))", "color": "gray", "dash": True, "label": "masukan"},
          {"type": "fn", "expr": "sum(0, 40, k => 4/pi*sin((2*k + 1)*x - atan((2*k + 1)*a))/((2*k + 1)*sqrt(1 + pow((2*k + 1)*a, 2))))", "color": "blue", "label": "keluaran"}],
         [readout("Peredaman harmonik ke-1", "1/sqrt(1 + a*a)", 3), readout("Peredaman harmonik ke-9", "1/sqrt(1 + 81*a*a)", 3)],
         "a = 0: tanpa filter. Makin besar a, makin banyak harmonik tinggi yang hilang.")]),
    S("pitfall", "Jebakan ujian",
      r"""<ul class="lesson-list">
        <li>Periode $2L$ diperlakukan seperti $2\pi$: argumen harus $\tfrac{n\pi x}{L}$.</li>
        <li>Konvensi $\tfrac{a_0}{2}$ vs $a_0$: cek rumus $a_0$ yang dipakai dosenmu.</li>
        <li>$\cos n\pi$ ditulis $1$; yang benar $(-1)^n$.</li>
        <li>Nilai deret di titik lompatan dianggap sama dengan $f$; yang benar rata-rata kiri-kanan.</li>
        <li>Mengira fenomena Gibbs hilang dengan menambah suku.</li>
      </ul>""",
      "Tabel kecil yang menyelamatkan: sin nπ = 0, cos nπ = (−1)ⁿ, sin(nπ/2) = 0, 1, 0, −1 berulang."),
    S("checkpoint", "Mini checkpoint",
      qa(r"1. Deret Fourier $f(x) = x^2$ pada $(-\pi, \pi)$ memuat sinus atau kosinus? Hitung $a_0$.",
         r"<p>$f$ genap, jadi hanya kosinus. $a_0 = \tfrac1\pi\displaystyle\int_{-\pi}^{\pi}x^2dx = \tfrac{2\pi^2}{3}$.</p>") +
      qa(r"2. Nilai deret gelombang kotak di $x = 0$.", r"<p>Rata-rata lompatan $\tfrac12(1 + (-1)) = 0$; memang semua $\sin(0) = 0$.</p>") +
      qa(r"3. Mengapa gelombang kotak tidak punya harmonik genap?", r"<p>$b_n = \tfrac{2(1 - (-1)^n)}{n\pi} = 0$ untuk $n$ genap (simetri setengah gelombang).</p>"),
      "Soal 2 adalah teorema Dirichlet dalam satu baris."),
]

# ═══════════════════════════════════════════════════════════════════════════
# FT 3. Transformasi Laplace
# ═══════════════════════════════════════════════════════════════════════════
LAPLACE = [
    S("intuition", "Kalkulus menjadi aljabar",
      r"""<p>Logaritma mengubah perkalian menjadi penjumlahan. Transformasi Laplace mengubah <b>turunan menjadi perkalian dengan $s$</b>, sehingga PD menjadi
      persamaan aljabar biasa. Insinyur elektro dan kendali memakainya setiap hari: fungsi alih rangkaian, kestabilan sistem kendali, dan respons terhadap sakelar
      yang dinyalakan tiba-tiba atau pukulan sesaat (impuls).</p>""",
      "Geser s. Luas di bawah e^(−st)·sin t adalah L{sin t}(s) = 1/(s² + 1). Faktor e^(−st) 'meredam' f agar integral tak wajarnya konvergen.",
      [g("L{sin t}(s) = ∫₀^∞ e^(−st) sin t dt", [0, 12], [-0.6, 1], [param("s", "s", 0.3, 3, 0.05, 0.6, "s")],
         [{"type": "fill", "upper": "exp(-s*x)*sin(x)", "from": 0, "to": 12, "color": "blue"},
          {"type": "fn", "expr": "exp(-s*x)*sin(x)", "color": "blue", "from": 0, "label": "e^(−st) sin t"},
          {"type": "fn", "expr": "sin(x)", "color": "gray", "dash": True, "from": 0, "label": "sin t"}],
         [readout("Luas (numerik, 0 sampai 20)", "0.01*sum(1, 2000, j => exp(-s*(j - 0.5)*0.01)*sin((j - 0.5)*0.01))", 4), readout("1/(s² + 1)", "1/(s*s + 1)", 4)],
         "Luas bertanda: bagian negatif mengurangi. Makin besar s, makin cepat integran lenyap.")]),
    S("theorem", "Definisi & tabel transformasi",
      r"""<p>$$F(s) = \mathcal{L}\{f\}(s) = \int_0^\infty e^{-st}f(t)\,dt,$$ konvergen untuk $s &gt; a$ bila $|f(t)| \le Me^{at}$.</p>
      <div class="table-scroll"><table class="lesson-table"><thead><tr><th>$f(t)$</th><th>$F(s)$</th><th>$f(t)$</th><th>$F(s)$</th></tr></thead><tbody>
        <tr><td>$1$</td><td>$\dfrac1s$</td><td>$\sin\omega t$</td><td>$\dfrac{\omega}{s^2 + \omega^2}$</td></tr>
        <tr><td>$t^n$</td><td>$\dfrac{n!}{s^{n+1}}$</td><td>$\cos\omega t$</td><td>$\dfrac{s}{s^2 + \omega^2}$</td></tr>
        <tr><td>$e^{at}$</td><td>$\dfrac{1}{s - a}$</td><td>$e^{at}f(t)$</td><td>$F(s - a)$</td></tr>
        <tr><td>$u(t - c)f(t - c)$</td><td>$e^{-cs}F(s)$</td><td>$\delta(t - c)$</td><td>$e^{-cs}$</td></tr>
      </tbody></table></div>
      <p>$u(t - c)$ adalah fungsi tangga (sakelar menyala di $t = c$), $\delta$ adalah impuls (pukulan sesaat).</p>""",
      "Dua pergeseran berbeda: e^(at) di waktu menggeser s; tunda waktu c mengalikan e^(−cs). Jangan tertukar."),
    S("derivation", "Turunan menjadi perkalian dengan s",
      steps(r"$\mathcal{L}\{1\} = \displaystyle\int_0^\infty e^{-st}dt = \lim_{b \to \infty}\left[-\frac{e^{-st}}{s}\right]_0^b = \frac1s$ ($s &gt; 0$).",
            r"$\mathcal{L}\{f'\}$: parsial dengan $u = e^{-st}$, $dv = f'dt$: $\ \Big[e^{-st}f(t)\Big]_0^\infty + s\displaystyle\int_0^\infty e^{-st}f\,dt = sF(s) - f(0)$.",
            r"Terapkan dua kali: $\mathcal{L}\{f''\} = s^2F(s) - sf(0) - f'(0)$.") +
      note(r"Syarat awal masuk <b>otomatis</b> ke dalam persamaan. Tidak perlu mencari solusi umum lalu menghitung $C_1$, $C_2$ terpisah."),
      "Rumus turunan inilah seluruh alasan Laplace dipakai untuk PD. Hafalkan bentuk s²F − s f(0) − f′(0)."),
    S("derivation", "Pohon keputusan: menyelesaikan PD dengan Laplace",
      pohon(r"Transformasikan kedua ruas PD memakai rumus turunan dan tabel.",
            r"Selesaikan secara aljabar untuk $Y(s)$.",
            r"Uraikan $Y(s)$: <b>pecahan parsial</b> (Level 3) untuk faktor linear; <b>lengkapkan kuadrat</b> untuk faktor kuadrat tak tereduksi (menghasilkan $e^{at}\cos$, $e^{at}\sin$).",
            r"Ada faktor $e^{-cs}$? Pisahkan, invers bagian lainnya, lalu geser waktu dengan $u(t - c)$.",
            r"Baca invers dari tabel.") +
      note(r"<b>Kapan Laplace lebih unggul dari koefisien tak tentu?</b> Saat ruas kanan sepotong-sepotong (sakelar on/off), berupa impuls, atau saat syarat awal sudah diberikan dan kamu hanya butuh satu solusi khusus."),
      "Bagian tersulit hampir selalu langkah 3 (pecahan parsial), bukan transformasinya."),
    S("example", "Bedah soal: masalah nilai awal",
      r"""<p><b>Soal.</b> $y'' - y' - 2y = 0$, $y(0) = 1$, $y'(0) = 0$.</p>""" +
      steps(r"$\left(s^2Y - s - 0\right) - (sY - 1) - 2Y = 0$.",
            r"$Y(s^2 - s - 2) = s - 1$, sehingga $Y = \dfrac{s - 1}{(s - 2)(s + 1)}$.",
            r"Cover-up: $\dfrac{s - 1}{(s - 2)(s + 1)} = \dfrac{1/3}{s - 2} + \dfrac{2/3}{s + 1}$.",
            r"$y(t) = \tfrac13e^{2t} + \tfrac23e^{-t}$. Cek: $y(0) = 1$, $y'(0) = \tfrac23 - \tfrac23 = 0$.") ,
      "Pembilang s − 1 berasal dari syarat awal. Syarat awal yang berbeda hanya mengubah pembilang, penyebutnya tetap."),
    S("example", "Bedah soal: sakelar pada rangkaian RL",
      r"""<p><b>Soal.</b> Rangkaian RL, $Li' + Ri = E$ untuk $0 \le t &lt; T$, lalu sumber dimatikan. $i(0) = 0$. Ruas kanan: $E\left[u(t) - u(t - T)\right]$.</p>""" +
      steps(r"Transformasi: $LsI + RI = E\left(\dfrac1s - \dfrac{e^{-Ts}}{s}\right)$, sehingga $I = \dfrac{E}{s(Ls + R)}\left(1 - e^{-Ts}\right)$.",
            r"Pecahan parsial: $\dfrac{E}{s(Ls + R)} = \dfrac{E}{R}\left(\dfrac1s - \dfrac{1}{s + R/L}\right)$, inversnya $\dfrac{E}{R}\left(1 - e^{-Rt/L}\right)$ (cocok dengan Level 3).",
            r"Faktor $e^{-Ts}$ menggeser waktu: $i(t) = \dfrac{E}{R}\left(1 - e^{-Rt/L}\right) - u(t - T)\dfrac{E}{R}\left(1 - e^{-R(t - T)/L}\right)$."),
      "Sakelar yang mati di t = T cukup ditulis sebagai 'nyala' dikurangi 'nyala yang ditunda T'. Laplace mengurus sisanya.",
      [g("Arus RL saat sakelar dimatikan di t = T (E = 12 V)", [0, 8], [-0.3, 7], [param("R", "R (Ω)", 2, 10, 0.5, 4, "R"), param("L", "L (H)", 0.2, 3, 0.1, 1, "L"), param("T", "Waktu mati T (s)", 0.5, 6, 0.1, 3, "T")],
         [{"type": "fn", "expr": "(12/R)*((1 - exp(-R*x/L)) - (x >= T ? (1 - exp(-R*(x - T)/L)) : 0))", "color": "blue", "label": "i(t)"},
          {"type": "vline", "x": "T", "color": "gray", "dash": True}],
         [readout("Arus tunak E/R", "12/R", 3), readout("Konstanta waktu L/R", "L/R", 3)],
         "Setelah t = T arus meluruh dengan konstanta waktu yang sama L/R.")]),
    S("theorem", "Fungsi alih, kutub, dan kestabilan",
      r"""<p>Dengan syarat awal nol, sistem $ay'' + by' + cy = x(t)$ menjadi $Y(s) = H(s)X(s)$ dengan <b>fungsi alih</b>
      $$H(s) = \frac{1}{as^2 + bs + c}.$$</p>
      <ul class="lesson-list">
        <li><b>Kutub</b> $H$ = akar persamaan karakteristik (topik PD Orde Dua).</li>
        <li>Sistem <b>stabil</b> bila semua kutub di setengah bidang kiri ($\operatorname{Re} &lt; 0$); kutub di sumbu imajiner → berosilasi terus; di kanan → meledak.</li>
        <li><b>Konvolusi:</b> $\mathcal{L}\{f * g\} = F(s)G(s)$ dengan $(f * g)(t) = \int_0^t f(\tau)g(t - \tau)\,d\tau$. Keluaran = konvolusi masukan dengan respons impuls $h(t) = \mathcal{L}^{-1}\{H\}$.</li>
      </ul>""",
      "Peta kutub adalah 'rontgen' sistem kendali: satu pandangan menunjukkan stabil atau tidak, berosilasi atau tidak."),
    S("pitfall", "Jebakan ujian",
      r"""<ul class="lesson-list">
        <li>Lupa syarat awal di $\mathcal{L}\{y'\} = sY - y(0)$.</li>
        <li>Tertukar pergeseran $s$ ($e^{at}f$) dan pergeseran $t$ ($u(t - c)f(t - c)$).</li>
        <li>Invers $\dfrac{s}{s^2 + \omega^2}$ ditulis $\sin\omega t$; yang benar $\cos\omega t$.</li>
        <li>$\mathcal{L}^{-1}\left\{\dfrac{1}{s^2 + 9}\right\} = \sin 3t$. Salah, kurang faktor: $\tfrac13\sin 3t$.</li>
        <li>Lupa daerah konvergensi: $\mathcal{L}\{e^{at}\}$ hanya ada untuk $s &gt; a$.</li>
      </ul>""",
      "Untuk sin dan cos: pembilang ω → sin, pembilang s → cos. Kalau pembilangnya bukan ω, sesuaikan dengan faktor konstanta."),
    S("checkpoint", "Mini checkpoint",
      qa(r"1. $\mathcal{L}\{te^{3t}\}$", r"<p>$\mathcal{L}\{t\} = \tfrac{1}{s^2}$, digeser: $\dfrac{1}{(s - 3)^2}$.</p>") +
      qa(r"2. $\mathcal{L}^{-1}\left\{\dfrac{3}{s^2 + 9}\right\}$", r"<p>$\sin 3t$.</p>") +
      qa(r"3. $\mathcal{L}\{e^{-2t}\cos 3t\}$", r"<p>$\dfrac{s + 2}{(s + 2)^2 + 9}$.</p>"),
      "Soal 3 menggabungkan tabel dan pergeseran s. Pola (s + 2) muncul di pembilang DAN penyebut."),
]

NEW_TOPICS = [
    {"after": "kl-ft-fk-analisis", "slug": "kl-ft-pd-orde2", "title": "Persamaan Diferensial Orde Dua", "icon": "m-slope-field",
     "summary": "Persamaan karakteristik, osilator teredam, koefisien tak tentu, resonansi, rangkaian RLC.",
     "references": "Kreyszig Bab 2; Stewart §17.1–17.3; Boyce & DiPrima Bab 3"},
    {"after": "kl-ft-pd-orde2", "slug": "kl-ft-fourier", "title": "Deret Fourier", "icon": "m-sine",
     "summary": "Ortogonalitas, koefisien Fourier, simetri, Dirichlet & Gibbs, Parseval, filter sinyal.",
     "references": "Kreyszig Bab 11; Boyce & DiPrima Bab 10"},
]

SLIDES = {
    "kl-ft-pd-orde2": PD_ORDE2,
    "kl-ft-fourier": FOURIER,
    "kl-ft-laplace": LAPLACE,
}
