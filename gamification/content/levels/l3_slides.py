r"""
Kurikulum v2 — Batch 3 (bagian A): slide Level 3, Teknik Pengintegralan.

Topik: Integrasi Parsial · Integral Trigonometri & Substitusi Trigonometri · Pecahan Parsial ·
Aturan L'Hôpital (topik baru, materi saja) · Integral Tak Wajar.
Topik padat diberi pohon keputusan (helper `pohon`) agar mahasiswa tahu KAPAN memakai teknik apa.

Rujukan: Purcell Jil. 1 Bab 7–8; Stewart 9e §4.4, §7.1–7.5, §7.8; OpenStax Calculus Vol 2 Bab 3.
"""

from ..helpers import param, readout
from .l1_slides import S, g, note, qa, steps


def pohon(*items):
    """Pohon keputusan: daftar pertanyaan berurutan, berhenti di cabang pertama yang cocok."""
    return '<ol class="steps-list">' + "".join(f"<li><b>Cek {i}.</b> {s}</li>" for i, s in enumerate(items, 1)) + "</ol>"


# ═══════════════════════════════════════════════════════════════════════════
# 1. Integrasi Parsial
# ═══════════════════════════════════════════════════════════════════════════
PARSIAL = [
    S("intuition", "Aturan perkalian, dibaca terbalik",
      r"""<p>Substitusi adalah aturan rantai yang dibalik. Lalu bagaimana dengan integral <b>perkalian</b> dua fungsi yang tidak saling berhubungan,
      seperti $\int x e^{x}\,dx$ atau $\int x\cos x\,dx$? Jawabannya: balik <b>aturan perkalian</b>.</p>
      <p>$$(uv)' = u'v + uv' \;\Longrightarrow\; uv = \int v\,du + \int u\,dv.$$</p>
      <p>Integral seperti ini muncul di mana-mana: nilai harapan distribusi eksponensial $\int x\lambda e^{-\lambda x}dx$ (statistika),
      transformasi Laplace $\int t e^{-st}dt$ (teknik kendali), dan energi sinyal $\int t\sin(\omega t)\,dt$.</p>""",
      "Parsial itu 'tukar tambah': kamu menukar integral sulit ∫u dv dengan integral yang (semoga) lebih mudah ∫v du."),
    S("theorem", "Rumus integrasi parsial",
      r"""<p>$$\int u\,dv = uv - \int v\,du$$</p>
      <p>Untuk integral tentu: $$\int_a^b u\,dv = \Big[uv\Big]_a^b - \int_a^b v\,du.$$</p>
      <p>Syarat pilihan yang baik:</p>
      <ul class="lesson-list">
        <li>$u$ makin <b>sederhana</b> bila diturunkan (polinom turun derajat, $\ln x$ jadi $\tfrac1x$).</li>
        <li>$dv$ harus <b>bisa diintegralkan</b> dengan mudah.</li>
        <li>Integral baru $\int v\,du$ harus lebih mudah dari semula. Kalau lebih sulit, tukar pilihanmu.</li>
      </ul>""",
      "Tulis empat kotak dulu: u, dv, du, v. Mengisi kotak ini sebelum menulis rumus mencegah hampir semua salah tanda."),
    S("derivation", "Strategi memilih u: aturan LIATE",
      r"""<p>Pilih $u$ dari jenis fungsi yang muncul <b>paling awal</b> dalam urutan berikut; sisanya menjadi $dv$.</p>
      <div class="table-scroll"><table class="lesson-table"><thead><tr><th>Urutan</th><th>Jenis</th><th>Contoh</th></tr></thead><tbody>
        <tr><td>L</td><td>Logaritma</td><td>$\ln x$, $\log_2 x$</td></tr>
        <tr><td>I</td><td>Invers trigonometri</td><td>$\arctan x$, $\arcsin x$</td></tr>
        <tr><td>A</td><td>Aljabar (polinom, pangkat)</td><td>$x^2$, $3x + 1$, $\sqrt{x}$</td></tr>
        <tr><td>T</td><td>Trigonometri</td><td>$\sin x$, $\cos 3x$</td></tr>
        <tr><td>E</td><td>Eksponen</td><td>$e^{x}$, $2^{x}$</td></tr>
      </tbody></table></div>
      <p><b>Pohon keputusan sebelum mulai:</b></p>""" +
      pohon(r"Apakah integran berbentuk $f(g(x))\,g'(x)$, misalnya $\int x e^{x^2}dx$? Pakai <b>substitusi</b>, bukan parsial.",
            r"Ada $\ln x$ atau invers trigonometri? Jadikan itu $u$; turunannya berbentuk aljabar.",
            r"Hanya satu fungsi seperti $\int \ln x\,dx$ atau $\int \arctan x\,dx$? Ambil $dv = dx$.",
            r"Polinom kali $e^{ax}$, $\sin$, atau $\cos$? $u$ = polinom; derajat tinggi → pakai <b>metode tabel</b>.",
            r"$e^{ax}$ kali $\sin bx$ atau $\cos bx$? Parsial dua kali → <b>integral siklik</b>, selesaikan secara aljabar."),
      "LIATE itu panduan, bukan hukum. Pengecualian terkenal: ∫x³e^(x²)dx lebih mudah dengan u = x² dan dv = x·e^(x²)dx."),
    S("example", "Bedah soal: polinom × eksponen & logaritma",
      r"""<p><b>Soal 1.</b> $\displaystyle\int_0^b x e^{-x}\,dx$.</p>""" +
      steps(r"$u = x$, $dv = e^{-x}dx$, sehingga $du = dx$, $v = -e^{-x}$.",
            r"$\displaystyle\Big[-xe^{-x}\Big]_0^b + \int_0^b e^{-x}dx = -be^{-b} + \left(1 - e^{-b}\right)$.",
            r"Hasil: $1 - (b + 1)e^{-b}$. Saat $b \to \infty$ nilainya mendekati $1$ (bahas lagi di Integral Tak Wajar).") +
      r"""<p><b>Soal 2.</b> $\displaystyle\int \ln x\,dx$.</p>""" +
      steps(r"$u = \ln x$, $dv = dx$; $du = \tfrac{1}{x}dx$, $v = x$.",
            r"$x\ln x - \displaystyle\int x\cdot\frac1x\,dx = x\ln x - x + C$."),
      "Geser b di grafik. Luas di bawah x·e^(−x) naik menuju 1 tapi tidak pernah melewatinya.",
      [g("Luas di bawah x·e^(−x) dari 0 sampai b", [-0.3, 10], [-0.05, 0.45], [param("b", "Batas atas b", 0.2, 10, 0.1, 3, "b")],
         [{"type": "fill", "upper": "x*exp(-x)", "from": 0, "to": "b", "color": "blue"},
          {"type": "fn", "expr": "x*exp(-x)", "color": "blue", "label": "x·e^(−x)"},
          {"type": "vline", "x": "b", "color": "gray", "dash": True}],
         [readout("Luas = 1 − (b + 1)e^(−b)", "1 - (b + 1)*exp(-b)", 5)],
         "Bandingkan dengan nilai harapan distribusi eksponensial λ = 1, yang hasilnya tepat 1.")]),
    S("derivation", "Metode tabel untuk polinom berderajat tinggi",
      r"""<p>Untuk $\int p(x) f(x)\,dx$ dengan $p$ polinom: turunkan $p$ sampai $0$ (kolom D), integralkan $f$ berulang (kolom I), lalu kalikan menyilang dengan tanda bergantian $+, -, +, \dots$</p>
      <p><b>Contoh:</b> $\displaystyle\int x^2\sin x\,dx$.</p>
      <div class="table-scroll"><table class="lesson-table"><thead><tr><th>Tanda</th><th>D (turunkan)</th><th>I (integralkan)</th></tr></thead><tbody>
        <tr><td>$+$</td><td>$x^2$</td><td>$\sin x$</td></tr>
        <tr><td>$-$</td><td>$2x$</td><td>$-\cos x$</td></tr>
        <tr><td>$+$</td><td>$2$</td><td>$-\sin x$</td></tr>
        <tr><td></td><td>$0$</td><td>$\cos x$</td></tr>
      </tbody></table></div>""" +
      steps(r"Kalikan tiap baris D dengan baris I <b>berikutnya</b>: $(+)\,x^2(-\cos x)$, $(-)\,2x(-\sin x)$, $(+)\,2\cos x$.",
            r"Jumlahkan: $-x^2\cos x + 2x\sin x + 2\cos x + C$.",
            r"Cek dengan menurunkan: $(2x\cos x$ dan $-2x\cos x$ saling hapus$)$, sisa $x^2\sin x$. Benar."),
      "Metode tabel hanya hemat kalau kolom D benar-benar habis jadi 0. Untuk e^x·sin x kolomnya tidak pernah habis."),
    S("example", "Bedah soal: integral siklik",
      r"""<p><b>Soal.</b> $I = \displaystyle\int e^{x}\sin x\,dx$.</p>""" +
      steps(r"Parsial pertama: $u = \sin x$, $dv = e^x dx$: $\ I = e^x\sin x - \displaystyle\int e^x\cos x\,dx$.",
            r"Parsial kedua (pilihan <b>sejenis</b>: trig tetap jadi $u$): $u = \cos x$, $dv = e^x dx$: $\ \displaystyle\int e^x\cos x\,dx = e^x\cos x + I$.",
            r"Substitusi balik: $I = e^x\sin x - e^x\cos x - I$.",
            r"Pindahkan $I$: $2I = e^x(\sin x - \cos x)$, jadi $I = \tfrac12 e^x(\sin x - \cos x) + C$.") +
      note(r"Integral bentuk ini muncul di rangkaian RLC dan getaran teredam, di mana sinyal berbentuk $e^{-at}\sin(\omega t)$."),
      "Kalau di parsial kedua kamu mengganti pilihan (eksponen jadi u), kamu akan mendapat 0 = 0. Tetap konsisten."),
    S("example", "Bedah soal: invers trigonometri & rumus reduksi",
      r"""<p><b>Soal 1.</b> $\displaystyle\int_0^1 \arctan x\,dx$.</p>""" +
      steps(r"$u = \arctan x$, $dv = dx$; $du = \dfrac{dx}{1 + x^2}$, $v = x$.",
            r"$\Big[x\arctan x\Big]_0^1 - \displaystyle\int_0^1 \frac{x}{1 + x^2}dx = \frac{\pi}{4} - \Big[\tfrac12\ln(1 + x^2)\Big]_0^1$.",
            r"$= \dfrac{\pi}{4} - \dfrac{\ln 2}{2} \approx 0.4388$. Integral kedua diselesaikan dengan substitusi.") +
      r"""<p><b>Rumus reduksi.</b> Parsial sekali menurunkan pangkat satu tingkat:
      $$\int (\ln x)^n dx = x(\ln x)^n - n\int (\ln x)^{n-1}dx.$$
      Contoh: $\int (\ln x)^2dx = x(\ln x)^2 - 2\left(x\ln x - x\right) + C$.</p>""",
      "Rumus reduksi itu 'resep berulang'. Terapkan terus sampai pangkatnya 0 atau 1 yang sudah kamu tahu jawabannya."),
    S("pitfall", "Jebakan ujian",
      r"""<ul class="lesson-list">
        <li>Salah pilih $u$: $\int x e^x dx$ dengan $u = e^x$ menghasilkan $\int \tfrac{x^2}{2}e^x dx$, malah makin sulit.</li>
        <li>Lupa tanda minus di $-\int v\,du$, atau tanda bergantian di metode tabel.</li>
        <li>Integral tentu: lupa mengevaluasi $[uv]_a^b$ di kedua batas.</li>
        <li>Integral siklik: berganti jenis pilihan di parsial kedua, hasilnya $I = I$.</li>
        <li>Memakai parsial padahal substitusi cukup, misalnya $\int x\cos(x^2)\,dx$.</li>
        <li>Menulis $v$ dengan $+C$ di tengah jalan. Konstanta cukup sekali di jawaban akhir.</li>
      </ul>""",
      "Cek akhir paling murah: turunkan jawabanmu. Satu menit untuk mengecek lebih baik dari kehilangan seluruh poin soal."),
    S("checkpoint", "Mini checkpoint",
      qa(r"1. $\displaystyle\int x\cos 3x\,dx$", r"<p>$u = x$, $dv = \cos 3x\,dx$, $v = \tfrac13\sin 3x$: $\ \tfrac{x}{3}\sin 3x + \tfrac19\cos 3x + C$.</p>") +
      qa(r"2. $\displaystyle\int x^2\ln x\,dx$", r"<p>LIATE: $u = \ln x$, $dv = x^2dx$: $\ \tfrac{x^3}{3}\ln x - \displaystyle\int\tfrac{x^2}{3}dx = \tfrac{x^3}{3}\ln x - \tfrac{x^3}{9} + C$.</p>") +
      qa(r"3. Teknik apa untuk $\displaystyle\int x e^{x^2}dx$?", r"<p>Substitusi $u = x^2$, bukan parsial: hasilnya $\tfrac12 e^{x^2} + C$.</p>"),
      "Soal 3 sengaja menjebak. Selalu jalankan Cek 1 di pohon keputusan: apakah ini substitusi?"),
]

# ═══════════════════════════════════════════════════════════════════════════
# 2. Integral Trigonometri & Substitusi Trigonometri
# ═══════════════════════════════════════════════════════════════════════════
TRIG = [
    S("intuition", "Akar yang dijinakkan identitas",
      r"""<p>Luas lingkaran, panjang kabel melengkung, dan medan listrik dari batang bermuatan semuanya memunculkan integral berisi
      $\sqrt{a^2 - x^2}$, $\sqrt{a^2 + x^2}$, atau $\sqrt{x^2 - a^2}$. Akar seperti ini tidak bisa diselesaikan substitusi biasa.</p>
      <p>Triknya: ganti $x$ dengan fungsi trigonometri sehingga identitas $1 - \sin^2\theta = \cos^2\theta$ menghapus akarnya.
      Sebelum itu, kita perlu lancar mengintegralkan pangkat $\sin$ dan $\cos$.</p>""",
      "Bagian pertama topik ini: pangkat sin/cos/tan/sec. Bagian kedua: substitusi trigonometri. Keduanya saling butuh."),
    S("theorem", "Identitas & integral dasar",
      r"""<p>$$\sin^2 x + \cos^2 x = 1, \qquad 1 + \tan^2 x = \sec^2 x$$</p>
      <p>$$\sin^2 x = \frac{1 - \cos 2x}{2}, \qquad \cos^2 x = \frac{1 + \cos 2x}{2}, \qquad \sin x\cos x = \tfrac12\sin 2x$$</p>
      <p>$$\int \tan x\,dx = \ln|\sec x| + C, \qquad \int \sec x\,dx = \ln|\sec x + \tan x| + C$$</p>
      <p>Pasangan turunan yang menjadi kunci substitusi: $(\tan x)' = \sec^2 x$ dan $(\sec x)' = \sec x\tan x$.</p>""",
      "Identitas setengah sudut adalah satu-satunya jalan untuk ∫sin²x dan ∫cos²x. Hafalkan bentuknya."),
    S("derivation", "Pohon keputusan: pangkat trigonometri",
      r"""<p><b>Bentuk $\int \sin^m x\cos^n x\,dx$:</b></p>""" +
      pohon(r"$m$ ganjil? Sisihkan satu $\sin x$, ubah sisanya dengan $\sin^2 x = 1 - \cos^2 x$, lalu $u = \cos x$.",
            r"$n$ ganjil? Sisihkan satu $\cos x$, ubah sisanya dengan $\cos^2 x = 1 - \sin^2 x$, lalu $u = \sin x$.",
            r"Keduanya genap? Pakai identitas setengah sudut, ulangi bila pangkatnya masih genap.") +
      r"""<p><b>Bentuk $\int \tan^m x\sec^n x\,dx$:</b></p>""" +
      pohon(r"$n$ genap ($n \ge 2$)? Sisihkan $\sec^2 x$, ubah sisanya dengan $\sec^2 x = 1 + \tan^2 x$, lalu $u = \tan x$.",
            r"$m$ ganjil? Sisihkan $\sec x\tan x$, ubah sisanya dengan $\tan^2 x = \sec^2 x - 1$, lalu $u = \sec x$.",
            r"Lainnya? Tulis ulang dalam $\sin$ dan $\cos$, atau gunakan rumus reduksi."),
      "Prinsipnya sama: sisihkan satu faktor yang menjadi du, ubah sisanya ke fungsi u memakai identitas Pythagoras."),
    S("example", "Bedah soal: pangkat sin, cos, tan",
      r"""<p><b>Soal 1.</b> $\displaystyle\int \sin^3 x\cos^2 x\,dx$ ($m = 3$ ganjil).</p>""" +
      steps(r"$\sin^3 x = (1 - \cos^2 x)\sin x$, sehingga integran $= (1 - \cos^2 x)\cos^2 x\sin x$.",
            r"$u = \cos x$, $du = -\sin x\,dx$: $\ -\displaystyle\int (u^2 - u^4)\,du = -\frac{u^3}{3} + \frac{u^5}{5} + C$.",
            r"Hasil: $-\dfrac{\cos^3 x}{3} + \dfrac{\cos^5 x}{5} + C$.") +
      r"""<p><b>Soal 2.</b> $\displaystyle\int_0^{\pi}\sin^2 x\,dx = \int_0^{\pi}\frac{1 - \cos 2x}{2}dx = \left[\frac{x}{2} - \frac{\sin 2x}{4}\right]_0^{\pi} = \frac{\pi}{2}$.</p>
      <p><b>Soal 3.</b> $\displaystyle\int \tan^2 x\sec^4 x\,dx$ ($n = 4$ genap): $\sec^4 x = (1 + \tan^2 x)\sec^2 x$, $u = \tan x$:
      $\displaystyle\int u^2(1 + u^2)\,du = \frac{\tan^3 x}{3} + \frac{\tan^5 x}{5} + C$.</p>""",
      "Soal 2 punya makna fisika: daya rata-rata arus bolak-balik sebanding dengan rata-rata sin², yaitu 1/2."),
    S("theorem", "Substitusi trigonometri",
      r"""<div class="table-scroll"><table class="lesson-table"><thead><tr><th>Bentuk</th><th>Substitusi</th><th>Identitas</th><th>Akar menjadi</th></tr></thead><tbody>
        <tr><td>$\sqrt{a^2 - x^2}$</td><td>$x = a\sin\theta$, $-\tfrac{\pi}{2} \le \theta \le \tfrac{\pi}{2}$</td><td>$1 - \sin^2\theta = \cos^2\theta$</td><td>$a\cos\theta$</td></tr>
        <tr><td>$\sqrt{a^2 + x^2}$</td><td>$x = a\tan\theta$, $-\tfrac{\pi}{2} &lt; \theta &lt; \tfrac{\pi}{2}$</td><td>$1 + \tan^2\theta = \sec^2\theta$</td><td>$a\sec\theta$</td></tr>
        <tr><td>$\sqrt{x^2 - a^2}$</td><td>$x = a\sec\theta$, $0 \le \theta &lt; \tfrac{\pi}{2}$</td><td>$\sec^2\theta - 1 = \tan^2\theta$</td><td>$a\tan\theta$</td></tr>
      </tbody></table></div>
      <p><b>Pohon keputusan:</b></p>""" +
      pohon(r"Ada faktor $x$ di luar akar yang merupakan turunan isi akar, misalnya $\int x\sqrt{a^2 - x^2}\,dx$? Substitusi biasa $u = a^2 - x^2$ lebih cepat.",
            r"Isi akar berbentuk $ax^2 + bx + c$? <b>Lengkapkan kuadrat</b> dulu agar menjadi salah satu dari tiga bentuk di tabel.",
            r"Cocokkan dengan tabel, ganti $x$, $dx$, dan akar sekaligus.",
            r"Setelah integral dalam $\theta$ selesai, gambar <b>segitiga siku-siku</b> untuk kembali ke $x$."),
      "Batasan θ di tabel menjamin akar = a cos θ (bukan −a cos θ). Itu sebabnya tidak perlu nilai mutlak."),
    S("example", "Bedah soal: luas lingkaran dengan x = 3 sin θ",
      r"""<p><b>Soal.</b> $\displaystyle\int \sqrt{9 - x^2}\,dx$.</p>""" +
      steps(r"$x = 3\sin\theta$, $dx = 3\cos\theta\,d\theta$, $\sqrt{9 - x^2} = 3\cos\theta$.",
            r"$\displaystyle\int 9\cos^2\theta\,d\theta = \frac92\int(1 + \cos 2\theta)\,d\theta = \frac92\left(\theta + \sin\theta\cos\theta\right) + C$.",
            r"Segitiga: $\sin\theta = \tfrac{x}{3}$, sisi miring $3$, sisi samping $\sqrt{9 - x^2}$, jadi $\cos\theta = \tfrac{\sqrt{9 - x^2}}{3}$.",
            r"Hasil: $\dfrac92\arcsin\dfrac{x}{3} + \dfrac{x}{2}\sqrt{9 - x^2} + C$.") +
      note(r"Cek: dari $0$ sampai $3$ hasilnya $\tfrac92\cdot\tfrac{\pi}{2} = \tfrac{9\pi}{4}$, tepat seperempat luas lingkaran berjari-jari $3$."),
      "Geser b sampai 3. Luas yang dihitung rumus arcsin sama persis dengan seperempat lingkaran.",
      [g("∫₀ᵇ √(9 − x²) dx", [-3.5, 3.5], [-0.5, 3.5], [param("b", "Batas atas b", 0, 3, 0.05, 1.5, "b")],
         [{"type": "fill", "upper": "sqrt(9 - x*x)", "from": 0, "to": "b", "color": "teal"},
          {"type": "fn", "expr": "sqrt(9 - x*x)", "color": "blue", "label": "y = √(9 − x²)"},
          {"type": "segment", "x1": 0, "y1": 0, "x2": "b", "y2": "sqrt(9 - b*b)", "color": "orange", "dash": True}],
         [readout("θ = arcsin(b/3)", "asin(b/3)", 4), readout("Luas", "4.5*asin(b/3) + (b/2)*sqrt(9 - b*b)", 5), readout("9π/4", "9*pi/4", 5)],
         "Garis oranye adalah jari-jari pada sudut θ: daerahnya terdiri dari juring dan segitiga.")]),
    S("example", "Bedah soal: x = a tan θ & melengkapkan kuadrat",
      r"""<p><b>Soal 1.</b> $\displaystyle\int \frac{dx}{x^2\sqrt{x^2 + 4}}$.</p>""" +
      steps(r"$x = 2\tan\theta$, $dx = 2\sec^2\theta\,d\theta$, $\sqrt{x^2 + 4} = 2\sec\theta$.",
            r"$\displaystyle\int \frac{2\sec^2\theta}{4\tan^2\theta\cdot 2\sec\theta}d\theta = \frac14\int\frac{\cos\theta}{\sin^2\theta}d\theta = -\frac{1}{4\sin\theta} + C$.",
            r"Segitiga: depan $x$, samping $2$, miring $\sqrt{x^2 + 4}$, jadi $\sin\theta = \tfrac{x}{\sqrt{x^2 + 4}}$.",
            r"Hasil: $-\dfrac{\sqrt{x^2 + 4}}{4x} + C$.") +
      r"""<p><b>Soal 2.</b> $\displaystyle\int \frac{dx}{\sqrt{x^2 + 2x + 5}}$.</p>""" +
      steps(r"Lengkapkan kuadrat: $x^2 + 2x + 5 = (x + 1)^2 + 4$.",
            r"$x + 1 = 2\tan\theta$: integral menjadi $\displaystyle\int\sec\theta\,d\theta = \ln|\sec\theta + \tan\theta| + C$.",
            r"Kembali ke $x$: $\ln\left(\sqrt{x^2 + 2x + 5} + x + 1\right) + C'$ (faktor $\tfrac12$ diserap ke konstanta)."),
      "Medan listrik batang bermuatan memakai integral ∫dx/(x² + a²)^(3/2). Polanya persis Soal 1: x = a tan θ."),
    S("pitfall", "Jebakan ujian",
      r"""<ul class="lesson-list">
        <li>Lupa mengganti $dx$: $x = 3\sin\theta$ berarti $dx = 3\cos\theta\,d\theta$, bukan $d\theta$.</li>
        <li>Jawaban akhir masih dalam $\theta$. Soal ditanya dalam $x$, jadi gambar segitiga.</li>
        <li>Integral tentu: lupa mengganti batas ke $\theta$, atau mengganti batas lalu tetap kembali ke $x$.</li>
        <li>Memakai substitusi trigonometri untuk $\int\tfrac{x}{\sqrt{x^2 + 1}}dx$, padahal cukup $u = x^2 + 1$.</li>
        <li>Tanda identitas setengah sudut tertukar: $\sin^2$ memakai <b>minus</b>, $\cos^2$ memakai <b>plus</b>.</li>
        <li>$\int\sin^2 x\,dx \ne \tfrac{\sin^3 x}{3}$, karena tidak ada faktor $\cos x$ sebagai $du$.</li>
      </ul>""",
      "Satu cara mengingat setengah sudut: di x = 0, sin² = 0 sehingga rumusnya harus (1 − cos 0)/2 = 0. Pakai minus."),
    S("checkpoint", "Mini checkpoint",
      qa(r"1. $\displaystyle\int\cos^3 x\,dx$", r"<p>$n$ ganjil: $(1 - \sin^2 x)\cos x$, $u = \sin x$: $\ \sin x - \tfrac{\sin^3 x}{3} + C$.</p>") +
      qa(r"2. $\displaystyle\int_0^2\sqrt{4 - x^2}\,dx$ tanpa menghitung panjang", r"<p>Seperempat lingkaran berjari-jari $2$: $\ \tfrac14\pi(2)^2 = \pi$.</p>") +
      qa(r"3. Substitusi apa untuk $\displaystyle\int\frac{\sqrt{x^2 - 9}}{x}dx$?", r"<p>$x = 3\sec\theta$, sehingga akar menjadi $3\tan\theta$. Hasil akhirnya $\sqrt{x^2 - 9} - 3\,\mathrm{arcsec}\tfrac{x}{3} + C$.</p>"),
      "Soal 2 mengingatkan: sebelum menghitung, cek apakah integralnya punya arti geometri yang langsung terlihat."),
]

# ═══════════════════════════════════════════════════════════════════════════
# 3. Pecahan Parsial
# ═══════════════════════════════════════════════════════════════════════════
PECAHAN = [
    S("intuition", "Menyamakan penyebut, dibalik",
      r"""<p>Di SMA kamu menjumlahkan pecahan: $\dfrac{2}{x - 1} - \dfrac{1}{x + 2} = \dfrac{x + 5}{(x - 1)(x + 2)}$.
      Pecahan parsial adalah <b>kebalikannya</b>: memecah satu fungsi rasional menjadi pecahan-pecahan sederhana yang integralnya langsung $\ln$ atau $\arctan$.</p>
      <p>Teknik ini dipakai di model logistik (pertumbuhan pengguna aplikasi, epidemi), laju reaksi kimia, dan invers transformasi Laplace di teknik kendali.</p>""",
      "Pecahan parsial mengubah satu integral sulit menjadi beberapa integral mudah. Kerja kerasnya ada di aljabar, bukan kalkulus.",
      [g("Satu pecahan rumit = jumlah dua pecahan sederhana", [-5, 4], [-8, 8], [],
         [{"type": "fn", "expr": "(x + 5)/((x + 2)*(x - 1))", "color": "blue", "label": "(x + 5)/((x + 2)(x − 1))"},
          {"type": "fn", "expr": "2/(x - 1)", "color": "orange", "dash": True, "label": "2/(x − 1)"},
          {"type": "fn", "expr": "-1/(x + 2)", "color": "green", "dash": True, "label": "−1/(x + 2)"}],
         [], "Kurva biru = oranye + hijau di setiap x. Asimtot tegaknya datang dari masing-masing pecahan.")]),
    S("theorem", "Syarat & bentuk dekomposisi",
      r"""<p>Untuk $\dfrac{P(x)}{Q(x)}$ yang <b>sejati</b> ($\deg P &lt; \deg Q$), faktorkan $Q$ menjadi faktor linear dan kuadrat tak tereduksi ($b^2 - 4ac &lt; 0$):</p>
      <div class="table-scroll"><table class="lesson-table"><thead><tr><th>Faktor di $Q(x)$</th><th>Suku dekomposisi</th></tr></thead><tbody>
        <tr><td>Linear berbeda $(x - a)$</td><td>$\dfrac{A}{x - a}$</td></tr>
        <tr><td>Linear berulang $(x - a)^k$</td><td>$\dfrac{A_1}{x - a} + \dfrac{A_2}{(x - a)^2} + \dots + \dfrac{A_k}{(x - a)^k}$</td></tr>
        <tr><td>Kuadrat tak tereduksi $ax^2 + bx + c$</td><td>$\dfrac{Ax + B}{ax^2 + bx + c}$</td></tr>
        <tr><td>Kuadrat berulang $(ax^2 + bx + c)^k$</td><td>$\dfrac{A_1x + B_1}{ax^2 + bx + c} + \dots + \dfrac{A_kx + B_k}{(ax^2 + bx + c)^k}$</td></tr>
      </tbody></table></div>
      <p>Integral-integral yang muncul: $\displaystyle\int\frac{dx}{x - a} = \ln|x - a|$, $\ \displaystyle\int\frac{dx}{(x - a)^k} = -\frac{1}{(k - 1)(x - a)^{k-1}}$, $\ \displaystyle\int\frac{dx}{x^2 + a^2} = \frac1a\arctan\frac{x}{a}$.</p>""",
      "Jumlah konstanta yang dicari selalu sama dengan derajat penyebut. Hitung dulu supaya tidak ada suku yang terlewat."),
    S("derivation", "Pohon keputusan: integral fungsi rasional",
      pohon(r"$\deg P \ge \deg Q$? <b>Bagi panjang</b> dulu: $\dfrac{P}{Q} = $ polinom $+ \dfrac{R}{Q}$ dengan $\deg R &lt; \deg Q$.",
            r"Pembilang (kelipatan) turunan penyebut? Substitusi $u = Q(x)$, hasilnya $\ln|Q(x)|$. Selesai.",
            r"Faktorkan $Q(x)$ selengkapnya.",
            r"Tulis bentuk dekomposisi sesuai tabel, satu suku untuk setiap pangkat faktor.",
            r"Cari konstanta: <b>cover-up Heaviside</b> untuk faktor linear berbeda; untuk sisanya, substitusi nilai $x$ yang praktis atau samakan koefisien.",
            r"Integralkan tiap suku: $\ln$, pangkat negatif, atau $\arctan$ (lengkapkan kuadrat bila perlu).") +
      note(r"<b>Cover-up Heaviside:</b> untuk $\dfrac{x + 5}{(x - 1)(x + 2)}$, nilai $A$ di atas $(x - 1)$ = tutup faktor $(x - 1)$, lalu masukkan $x = 1$: $\dfrac{1 + 5}{1 + 2} = 2$."),
      "Cover-up cuma berlaku untuk faktor linear berbeda (atau pangkat tertinggi faktor berulang). Sisanya pakai samakan koefisien."),
    S("example", "Bedah soal: faktor linear berbeda",
      r"""<p><b>Soal.</b> $\displaystyle\int\frac{x + 5}{x^2 + x - 2}\,dx$.</p>""" +
      steps(r"Derajat pembilang $1 &lt; 2$: sudah sejati. Faktorkan: $x^2 + x - 2 = (x - 1)(x + 2)$.",
            r"Bentuk: $\dfrac{A}{x - 1} + \dfrac{B}{x + 2}$.",
            r"Cover-up: $A = \dfrac{1 + 5}{1 + 2} = 2$, $\ B = \dfrac{-2 + 5}{-2 - 1} = -1$.",
            r"$\displaystyle\int\left(\frac{2}{x - 1} - \frac{1}{x + 2}\right)dx = 2\ln|x - 1| - \ln|x + 2| + C$.") +
      note(r"Bisa ditulis ringkas: $\ln\left|\dfrac{(x - 1)^2}{x + 2}\right| + C$."),
      "Cek dekomposisi dengan memasukkan satu nilai x, misalnya x = 0: kiri −5/2, kanan −2 − 1/2 = −5/2. Cocok."),
    S("example", "Bedah soal: faktor linear berulang",
      r"""<p><b>Soal.</b> $\displaystyle\int\frac{x^2 + 1}{x(x - 1)^2}\,dx$.</p>""" +
      steps(r"Bentuk: $\dfrac{A}{x} + \dfrac{B}{x - 1} + \dfrac{C}{(x - 1)^2}$ (tiga konstanta, derajat penyebut $3$).",
            r"Kalikan penyebut: $x^2 + 1 = A(x - 1)^2 + Bx(x - 1) + Cx$.",
            r"$x = 0$: $1 = A$. $\ x = 1$: $2 = C$. Koefisien $x^2$: $1 = A + B \Rightarrow B = 0$.",
            r"$\displaystyle\int\left(\frac1x + \frac{2}{(x - 1)^2}\right)dx = \ln|x| - \frac{2}{x - 1} + C$.") +
      note(r"$B = 0$ itu wajar dan tetap harus dicari. Kalau sejak awal suku $\tfrac{B}{x - 1}$ dihilangkan, sistem persamaannya bisa tidak konsisten di soal lain."),
      "Substitusi akar faktor (x = 0, x = 1) dulu karena langsung memberi konstanta. Sisanya pakai koefisien pangkat tertinggi."),
    S("example", "Bedah soal: kuadrat tak tereduksi",
      r"""<p><b>Soal.</b> $\displaystyle\int\frac{2x^2 - x + 4}{x^3 + 4x}\,dx$.</p>""" +
      steps(r"$x^3 + 4x = x(x^2 + 4)$; $x^2 + 4$ tak tereduksi ($b^2 - 4ac = -16 &lt; 0$).",
            r"Bentuk: $\dfrac{A}{x} + \dfrac{Bx + C}{x^2 + 4}$, sehingga $2x^2 - x + 4 = (A + B)x^2 + Cx + 4A$.",
            r"Samakan koefisien: $4A = 4$, $C = -1$, $A + B = 2$, jadi $A = 1$, $B = 1$, $C = -1$.",
            r"$\displaystyle\int\frac{dx}{x} + \int\frac{x\,dx}{x^2 + 4} - \int\frac{dx}{x^2 + 4} = \ln|x| + \tfrac12\ln(x^2 + 4) - \tfrac12\arctan\tfrac{x}{2} + C$.") +
      r"""<p><b>Soal tambahan (pecahan tak sejati).</b> $\displaystyle\int\frac{x^3 + x}{x - 1}dx$: bagi panjang $x^3 + x = (x - 1)(x^2 + x + 2) + 2$, sehingga
      hasilnya $\tfrac{x^3}{3} + \tfrac{x^2}{2} + 2x + 2\ln|x - 1| + C$.</p>""",
      "Suku (Bx + C)/(x² + 4) dipecah dua: bagian Bx menjadi ln (substitusi), bagian C menjadi arctan."),
    S("pitfall", "Jebakan ujian",
      r"""<ul class="lesson-list">
        <li>Lupa bagi panjang saat $\deg P \ge \deg Q$, sehingga dekomposisinya mustahil.</li>
        <li>Faktor berulang $(x - 1)^2$ hanya ditulis satu suku $\tfrac{B}{(x - 1)^2}$.</li>
        <li>Faktor kuadrat diberi pembilang konstanta saja ($\tfrac{B}{x^2 + 4}$), seharusnya $\tfrac{Bx + C}{x^2 + 4}$.</li>
        <li>Memecah $x^2 + 4$ menjadi $(x + 2)(x - 2)$. Itu hanya untuk $x^2 - 4$.</li>
        <li>Lupa nilai mutlak di $\ln|x - a|$ dan faktor $\tfrac1a$ di $\tfrac1a\arctan\tfrac{x}{a}$.</li>
      </ul>""",
      "Sebelum memfaktorkan kuadrat, hitung diskriminannya. Negatif berarti tak tereduksi, berarti arctan."),
    S("checkpoint", "Mini checkpoint",
      qa(r"1. Tulis bentuk dekomposisi $\dfrac{x + 1}{(x - 2)^2(x^2 + 1)}$ (tanpa mencari konstanta).",
         r"<p>$\dfrac{A}{x - 2} + \dfrac{B}{(x - 2)^2} + \dfrac{Cx + D}{x^2 + 1}$, empat konstanta untuk penyebut berderajat $4$.</p>") +
      qa(r"2. $\displaystyle\int\frac{dx}{x^2 - 9}$",
         r"<p>$\dfrac{1}{(x - 3)(x + 3)} = \dfrac16\left(\dfrac{1}{x - 3} - \dfrac{1}{x + 3}\right)$, jadi $\dfrac16\ln\left|\dfrac{x - 3}{x + 3}\right| + C$.</p>"),
      "Soal 2 adalah pola klasik 1/(x² − a²). Hasilnya selalu (1/2a)·ln|(x − a)/(x + a)|."),
]

# ═══════════════════════════════════════════════════════════════════════════
# 4. Aturan L'Hôpital (topik baru)
# ═══════════════════════════════════════════════════════════════════════════
LHOPITAL = [
    S("intuition", "Dua fungsi yang sama-sama menuju nol",
      r"""<p>Saat $f(a) = g(a) = 0$, di dekat $a$ kedua fungsi hampir lurus: $f(x) \approx f'(a)(x - a)$ dan $g(x) \approx g'(a)(x - a)$.
      Faktor $(x - a)$ saling coret, sehingga $\dfrac{f(x)}{g(x)} \approx \dfrac{f'(a)}{g'(a)}$.
      Jadi yang menentukan limit adalah <b>seberapa cepat</b> keduanya menuju nol, yaitu turunannya.</p>
      <p>Di Fasilkom, ide yang sama dipakai untuk membandingkan laju pertumbuhan algoritma: apakah $n\log n$ lebih lambat dari $n^{1.1}$?</p>""",
      "L'Hôpital = membandingkan laju. Kalau pembilang dan penyebut sama-sama lenyap, siapa yang lenyap lebih cepat?",
      [g("sin x / x di dekat 0", [-4, 4], [-1.5, 2], [param("X", "Titik x", -3.5, 3.5, 0.01, 1, "x")],
         [{"type": "fn", "expr": "sin(x)", "color": "blue", "label": "f = sin x"},
          {"type": "fn", "expr": "x", "color": "orange", "label": "g = x"},
          {"type": "fn", "expr": "sin(x)/x", "color": "green", "dash": True, "label": "f/g"},
          {"type": "point", "x": "X", "y": "sin(X)/X", "color": "green"}],
         [readout("f(x)/g(x)", "sin(X)/X", 5), readout("f'(x)/g'(x) = cos x", "cos(X)", 5)],
         "Geser x menuju 0: kedua rasio mendekati 1.")]),
    S("theorem", "Aturan L'Hôpital",
      r"""<p>Misalkan $f$ dan $g$ terdiferensialkan di sekitar $a$ (kecuali mungkin di $a$), $g'(x) \ne 0$ di sekitar $a$, dan
      $\displaystyle\lim_{x \to a}\frac{f(x)}{g(x)}$ berbentuk $\dfrac00$ atau $\dfrac{\pm\infty}{\pm\infty}$. Jika $\displaystyle\lim_{x \to a}\frac{f'(x)}{g'(x)}$ ada (atau $\pm\infty$), maka
      $$\lim_{x \to a}\frac{f(x)}{g(x)} = \lim_{x \to a}\frac{f'(x)}{g'(x)}.$$</p>
      <p>Berlaku juga untuk limit sepihak dan $x \to \pm\infty$. Perhatikan: turunkan pembilang dan penyebut <b>terpisah</b>, bukan aturan pembagian.</p>""",
      "Sebelum menurunkan, tulis dulu bentuknya, misalnya '[0/0]'. Kebiasaan ini mencegah memakai L'Hôpital di tempat yang salah."),
    S("derivation", "Pohon keputusan bentuk tak tentu",
      pohon(r"Substitusi langsung memberi angka? Selesai, <b>jangan</b> pakai L'Hôpital.",
            r"Bentuk $\tfrac00$ atau $\tfrac{\infty}{\infty}$? Langsung L'Hôpital (boleh berulang).",
            r"Bentuk $0\cdot\infty$? Tulis $fg = \dfrac{f}{1/g}$ atau $\dfrac{g}{1/f}$; pilih yang turunannya lebih sederhana.",
            r"Bentuk $\infty - \infty$? Samakan penyebut, faktorkan, atau kalikan sekawan untuk menghasilkan $\tfrac00$ atau $\tfrac{\infty}{\infty}$.",
            r"Bentuk pangkat $1^\infty$, $0^0$, $\infty^0$? Misalkan $y = f^g$, hitung $\lim \ln y = \lim g\ln f$, lalu $\lim y = e^{\lim\ln y}$.") +
      note(r"Bentuk $\tfrac{1}{0}$, $\tfrac{\infty}{0}$, $0^{\infty}$, dan $\infty + \infty$ <b>bukan</b> bentuk tak tentu; hasilnya langsung $\pm\infty$ atau $0$."),
      "Pohon ini sama dengan langkah Batch 2 di limit, tapi kini kamu punya senjata tambahan untuk bentuk yang tidak bisa difaktorkan."),
    S("example", "Bedah soal: 0/0, ∞/∞, dan hierarki pertumbuhan",
      r"""<p><b>Soal 1.</b> $\displaystyle\lim_{x \to 0}\frac{e^x - 1 - x}{x^2}$ $\ [\tfrac00]$</p>""" +
      steps(r"L'Hôpital: $\displaystyle\lim_{x \to 0}\frac{e^x - 1}{2x}$, masih $[\tfrac00]$.",
            r"Sekali lagi: $\displaystyle\lim_{x \to 0}\frac{e^x}{2} = \frac12$.") +
      r"""<p><b>Soal 2.</b> $\displaystyle\lim_{x \to \infty}\frac{x^2}{e^x}$ $\ [\tfrac{\infty}{\infty}] = \lim\frac{2x}{e^x} = \lim\frac{2}{e^x} = 0$.</p>
      <p><b>Soal 3.</b> $\displaystyle\lim_{x \to \infty}\frac{\ln x}{\sqrt{x}} = \lim\frac{1/x}{1/(2\sqrt{x})} = \lim\frac{2}{\sqrt{x}} = 0$.</p>""" +
      note(r"<b>Hierarki pertumbuhan</b> untuk $n \to \infty$: $\ \ln n \ll n^p \ll a^n \ll n! \ll n^n$ ($p &gt; 0$, $a &gt; 1$). Inilah dasar notasi Big-O: algoritma $O(n\log n)$ selalu kalah lambat-nya dari $O(n^2)$ untuk $n$ besar."),
      "Eksponen mengalahkan polinom apa pun, dan polinom apa pun mengalahkan logaritma. Ingat urutan ini, banyak limit selesai tanpa hitungan."),
    S("example", "Bedah soal: 0·∞, ∞ − ∞, dan bentuk pangkat",
      r"""<p><b>Soal 1.</b> $\displaystyle\lim_{x \to 0^+}x\ln x$ $\ [0\cdot\infty]$</p>""" +
      steps(r"Tulis $\dfrac{\ln x}{1/x}$ $\ [\tfrac{-\infty}{\infty}]$.",
            r"$\displaystyle\lim\frac{1/x}{-1/x^2} = \lim(-x) = 0$.") +
      r"""<p><b>Soal 2.</b> $\displaystyle\lim_{x \to 0}\left(\frac1x - \frac{1}{\sin x}\right)$ $\ [\infty - \infty]$</p>""" +
      steps(r"Samakan penyebut: $\dfrac{\sin x - x}{x\sin x}$ $\ [\tfrac00]$.",
            r"L'Hôpital: $\dfrac{\cos x - 1}{\sin x + x\cos x}$, masih $[\tfrac00]$.",
            r"Sekali lagi: $\dfrac{-\sin x}{2\cos x - x\sin x} \to \dfrac{0}{2} = 0$.") +
      r"""<p><b>Soal 3.</b> $\displaystyle\lim_{x \to \infty}\left(1 + \frac3x\right)^x$ $\ [1^\infty]$</p>""" +
      steps(r"$\ln y = x\ln\left(1 + \tfrac3x\right) = \dfrac{\ln(1 + 3/x)}{1/x}$ $\ [\tfrac00]$.",
            r"L'Hôpital: $\dfrac{\frac{-3/x^2}{1 + 3/x}}{-1/x^2} = \dfrac{3}{1 + 3/x} \to 3$.",
            r"Jadi $y \to e^3$. Ini rumus bunga majemuk kontinu: $\left(1 + \tfrac{r}{n}\right)^{nt} \to e^{rt}$."),
      "Bentuk pangkat: JANGAN lupa langkah terakhir, yaitu mengembalikan dari ln y ke y = e^(limit)."),
    S("pitfall", "Jebakan ujian",
      r"""<ul class="lesson-list">
        <li>Memakai L'Hôpital tanpa bentuk tak tentu: $\displaystyle\lim_{x \to 1}\frac{x^2 + 1}{x + 1} = 1$, tetapi "L'Hôpital" memberi $\lim\frac{2x}{1} = 2$. Salah.</li>
        <li>Memakai aturan pembagian $\left(\tfrac{f}{g}\right)'$ alih-alih $\tfrac{f'}{g'}$.</li>
        <li>Menyimpulkan limit tidak ada karena $\lim\tfrac{f'}{g'}$ tidak ada. Contoh: $\displaystyle\lim_{x \to \infty}\frac{x + \sin x}{x} = 1$, padahal $\tfrac{1 + \cos x}{1}$ berosilasi.</li>
        <li>Membuktikan $\displaystyle\lim_{x \to 0}\frac{\sin x}{x} = 1$ dengan L'Hôpital. Itu melingkar, karena rumus $(\sin x)' = \cos x$ sendiri diturunkan dari limit tersebut.</li>
        <li>Lupa mengembalikan $\ln y$ ke $y$ pada bentuk pangkat.</li>
      </ul>""",
      "Jebakan pertama adalah favorit dosen. Selalu substitusi langsung dulu sebelum menurunkan."),
    S("checkpoint", "Mini checkpoint",
      qa(r"1. $\displaystyle\lim_{x \to 0}\frac{1 - \cos x}{x^2}$", r"<p>$[\tfrac00]$: $\lim\tfrac{\sin x}{2x} = \tfrac12$.</p>") +
      qa(r"2. $\displaystyle\lim_{x \to 0^+}x^x$", r"<p>$[0^0]$: $\ln y = x\ln x \to 0$ (Soal 1 slide sebelumnya), jadi $y \to e^0 = 1$.</p>") +
      qa(r"3. $\displaystyle\lim_{x \to \infty}\frac{(\ln x)^2}{x}$", r"<p>$[\tfrac{\infty}{\infty}]$: $\lim\tfrac{2\ln x/x}{1} = \lim\tfrac{2\ln x}{x} = \lim\tfrac{2}{x} = 0$.</p>"),
      "Soal 3 butuh L'Hôpital dua kali. Hasilnya sesuai hierarki: pangkat logaritma kalah dari x."),
]

# ═══════════════════════════════════════════════════════════════════════════
# 5. Integral Tak Wajar
# ═══════════════════════════════════════════════════════════════════════════
TAKWAJAR = [
    S("intuition", "Daerah tak terbatas, luas terbatas?",
      r"""<p>Daerah di bawah $y = \tfrac{1}{x^2}$ dari $x = 1$ sampai tak hingga panjangnya tak berujung, tetapi luasnya tepat $1$.
      Sebaliknya, daerah di bawah $y = \tfrac1x$ yang tampak mirip punya luas tak hingga.</p>
      <p>Integral tak wajar dipakai untuk kecepatan lepas roket (kerja melawan gravitasi sampai jarak tak hingga),
      fungsi kepadatan peluang yang total luasnya harus $1$, dan transformasi Laplace di teknik elektro.</p>""",
      "Geser b jauh ke kanan dan bandingkan dua readout. Yang satu berhenti di 1, yang lain terus naik pelan-pelan.",
      [g("Luas dari 1 sampai b: 1/x² vs 1/x", [0, 20], [-0.1, 1.2], [param("b", "Batas atas b", 1.1, 20, 0.1, 5, "b")],
         [{"type": "fill", "upper": "1/x", "lower": "1/(x*x)", "from": 1, "to": "b", "color": "orange"},
          {"type": "fill", "upper": "1/(x*x)", "from": 1, "to": "b", "color": "blue"},
          {"type": "fn", "expr": "1/(x*x)", "color": "blue", "from": 0.3, "label": "1/x²"},
          {"type": "fn", "expr": "1/x", "color": "orange", "from": 0.3, "label": "1/x"}],
         [readout("∫₁ᵇ 1/x² dx = 1 − 1/b", "1 - 1/b", 5), readout("∫₁ᵇ 1/x dx = ln b", "ln(b)", 5)],
         "Biru menuju 1, oranye + biru (= ln b) tumbuh tanpa batas.")]),
    S("theorem", "Dua tipe integral tak wajar",
      r"""<p><b>Tipe 1, batas tak hingga:</b>
      $$\int_a^\infty f(x)\,dx = \lim_{b \to \infty}\int_a^b f(x)\,dx, \qquad \int_{-\infty}^{\infty}f = \int_{-\infty}^{c}f + \int_{c}^{\infty}f.$$</p>
      <p><b>Tipe 2, integran tak terbatas</b> (misalnya $f$ tak kontinu di $b$):
      $$\int_a^b f(x)\,dx = \lim_{t \to b^-}\int_a^t f(x)\,dx.$$
      Jika titik bermasalah $c$ ada di dalam $(a, b)$, pecah menjadi $\int_a^c + \int_c^b$.</p>
      <p>Integral <b>konvergen</b> jika limitnya ada (berhingga); <b>divergen</b> jika tidak. Bila dipecah, <b>semua</b> bagian harus konvergen.</p>
      <p><b>Uji-$p$:</b> $\displaystyle\int_1^\infty\frac{dx}{x^p}$ konvergen $\iff p &gt; 1$ (nilainya $\tfrac{1}{p - 1}$); $\ \displaystyle\int_0^1\frac{dx}{x^p}$ konvergen $\iff p &lt; 1$ (nilainya $\tfrac{1}{1 - p}$).</p>""",
      "Uji-p di ∞ dan di 0 arahnya berlawanan. Di ∞ butuh p > 1 (turun cepat), di 0 butuh p < 1 (meledak pelan)."),
    S("example", "Bedah soal: tipe 1",
      r"""<p><b>Soal 1.</b> $\displaystyle\int_0^\infty xe^{-x}\,dx$.</p>""" +
      steps(r"Dari topik Integrasi Parsial: $\displaystyle\int_0^b xe^{-x}dx = 1 - (b + 1)e^{-b}$.",
            r"$\displaystyle\lim_{b \to \infty}\frac{b + 1}{e^b} = \lim\frac{1}{e^b} = 0$ (L'Hôpital).",
            r"Konvergen, nilainya $1$.") +
      r"""<p><b>Soal 2.</b> $\displaystyle\int_{-\infty}^{\infty}\frac{dx}{1 + x^2}$.</p>""" +
      steps(r"Pecah di $0$: $\displaystyle\int_0^\infty\frac{dx}{1 + x^2} = \lim_{b \to \infty}\arctan b = \frac{\pi}{2}$.",
            r"Karena simetri, bagian kiri juga $\tfrac{\pi}{2}$. Total $\pi$ (konvergen).") +
      note(r"<b>Kecepatan lepas.</b> Kerja memindahkan massa $m$ dari permukaan bumi ($R$) ke tak hingga: $W = \displaystyle\int_R^\infty\frac{GMm}{r^2}dr = \frac{GMm}{R}$. Dengan $\tfrac12mv^2 = W$: $v = \sqrt{2GM/R} \approx 11{,}2$ km/s."),
      "Tipe 1 selalu tiga langkah: ganti ∞ dengan b, hitung integral biasa, ambil limit b → ∞."),
    S("example", "Bedah soal: tipe 2",
      r"""<p><b>Soal 1.</b> $\displaystyle\int_0^1\ln x\,dx$ ($\ln x \to -\infty$ di $0$).</p>""" +
      steps(r"$\displaystyle\lim_{t \to 0^+}\Big[x\ln x - x\Big]_t^1 = (0 - 1) - \lim_{t \to 0^+}(t\ln t - t)$.",
            r"$\displaystyle\lim_{t \to 0^+}t\ln t = 0$ (L'Hôpital), jadi hasilnya $-1$. Konvergen.") +
      r"""<p><b>Soal 2.</b> $\displaystyle\int_{-1}^{1}\frac{dx}{x^2}$ (bermasalah di $x = 0$, di <b>dalam</b> interval).</p>""" +
      steps(r"Pecah: $\displaystyle\int_{-1}^{0}\frac{dx}{x^2} + \int_0^1\frac{dx}{x^2}$.",
            r"$\displaystyle\int_0^1\frac{dx}{x^2}$: uji-$p$ dengan $p = 2 \ge 1$, divergen.",
            r"Satu bagian divergen sudah cukup: seluruh integral <b>divergen</b> (bukan $-2$ seperti hitungan TDK yang keliru)."),
      "Sebelum memakai TDK, scan integrannya: ada pembagian nol atau log nol di dalam interval? Kalau ya, itu integral tak wajar."),
    S("theorem", "Uji perbandingan untuk integral",
      r"""<p>Untuk $0 \le f(x) \le g(x)$ pada $[a, \infty)$:</p>
      <ul class="lesson-list">
        <li>$\int_a^\infty g$ konvergen $\Rightarrow$ $\int_a^\infty f$ konvergen (yang lebih kecil dari terbatas pasti terbatas).</li>
        <li>$\int_a^\infty f$ divergen $\Rightarrow$ $\int_a^\infty g$ divergen.</li>
        <li><b>Uji limit perbandingan:</b> jika $\displaystyle\lim_{x \to \infty}\frac{f(x)}{g(x)} = L$ dengan $0 &lt; L &lt; \infty$, keduanya konvergen atau keduanya divergen.</li>
      </ul>
      <p><b>Pohon keputusan:</b></p>""" +
      pohon(r"Antiturunan mudah dicari? Hitung langsung dengan limit.",
            r"Tidak bisa (misalnya $e^{-x^2}$)? Ambil suku dominan untuk $x$ besar sebagai pembanding, biasanya $\tfrac{1}{x^p}$ atau $e^{-x}$.",
            r"Lebih kecil dari yang konvergen → konvergen. Lebih besar dari yang divergen → divergen.",
            r"Ketaksamaan sulit dibuktikan? Pakai uji limit perbandingan.") +
      r"""<p><b>Contoh:</b> $\int_1^\infty e^{-x^2}dx$ konvergen karena $e^{-x^2} \le e^{-x}$ untuk $x \ge 1$. $\ \int_1^\infty\frac{1 + \sin^2 x}{\sqrt{x}}dx$ divergen karena integrannya $\ge \tfrac{1}{\sqrt{x}}$ ($p = \tfrac12$).</p>""",
      "Uji perbandingan hanya memberi KONVERGEN atau DIVERGEN, bukan nilainya. Untuk ∫e^(−x²) nilainya di jalur FMIPA (fungsi error)."),
    S("pitfall", "Jebakan ujian",
      r"""<ul class="lesson-list">
        <li>Memperlakukan $\infty$ seperti angka: $\left[-\tfrac1x\right]_1^\infty = -\tfrac{1}{\infty} + 1$. Tulis limitnya secara eksplisit.</li>
        <li>Menghitung $\int_{-\infty}^{\infty}x\,dx$ sebagai $\displaystyle\lim_{b \to \infty}\int_{-b}^{b}x\,dx = 0$. Salah: kedua bagian harus konvergen sendiri-sendiri, dan $\int_0^\infty x\,dx$ divergen.</li>
        <li>Tidak melihat titik bermasalah di dalam interval (seperti $\int_{-1}^{1}\tfrac{dx}{x^2}$).</li>
        <li>Membandingkan ke arah yang salah: "lebih kecil dari yang divergen" tidak menyimpulkan apa pun.</li>
        <li>Mengira $f(x) \to 0$ saat $x \to \infty$ menjamin konvergen. $\int_1^\infty\tfrac{dx}{x}$ membantahnya.</li>
      </ul>""",
      "Jebakan kedua ada di hampir setiap UTS Kalkulus 2. Dua bagian, dua limit terpisah."),
    S("checkpoint", "Mini checkpoint",
      qa(r"1. $\displaystyle\int_2^\infty\frac{dx}{x\ln x}$", r"<p>$u = \ln x$: $\displaystyle\lim_{b \to \infty}\Big[\ln(\ln x)\Big]_2^b = \infty$. Divergen.</p>") +
      qa(r"2. $\displaystyle\int_0^4\frac{dx}{\sqrt{x}}$", r"<p>Tipe 2, $p = \tfrac12 &lt; 1$: $\displaystyle\lim_{t \to 0^+}\Big[2\sqrt{x}\Big]_t^4 = 4$. Konvergen.</p>") +
      qa(r"3. Konvergen atau divergen: $\displaystyle\int_1^\infty\frac{x}{x^3 + 1}dx$?", r"<p>Suku dominan $\tfrac{x}{x^3} = \tfrac{1}{x^2}$; limit perbandingan $L = 1$, dan $p = 2 &gt; 1$. Konvergen.</p>"),
      "Soal 1 dan 2 bisa juga dijawab dengan uji-p versi lain. Biasakan memprediksi dulu, baru menghitung."),
]

NEW_TOPICS = [
    {"after": "km-tek-pecahan", "slug": "km-lhopital", "title": "Aturan L'Hôpital", "icon": "m-limit",
     "summary": "Bentuk tak tentu 0/0, ∞/∞, 0·∞, ∞ − ∞, dan bentuk pangkat; hierarki laju pertumbuhan.",
     "references": "Stewart §4.4; Purcell §8.1–8.2; OpenStax Vol 1 §4.8"},
]

SLIDES = {
    "km-tek-parsial": PARSIAL,
    "km-tek-trig": TRIG,
    "km-tek-pecahan": PECAHAN,
    "km-lhopital": LHOPITAL,
    "km-tek-takwajar": TAKWAJAR,
}
