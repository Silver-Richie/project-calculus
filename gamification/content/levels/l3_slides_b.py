r"""
Kurikulum v2 — Batch 3 (bagian B): slide Level 3, aplikasi integral, PD orde satu, kurva bidang.

Topik: Luas Daerah & Volume Benda Putar · Kerja, Tekanan & Pusat Massa · Persamaan Diferensial Orde Satu ·
Kurva Parametrik & Koordinat Kutub · Irisan Kerucut.

Rujukan: Purcell Jil. 1 Bab 6 & 10; Stewart 9e §6.1–6.5, §8.1–8.3, §9.1–9.5, §10.1–10.5; OpenStax Calculus Vol 2 Bab 2, 4, 7.
"""

from ..helpers import param, readout
from .l1_slides import S, g, note, qa, steps
from .l3_slides import pohon

# ═══════════════════════════════════════════════════════════════════════════
# 6. Luas Daerah & Volume Benda Putar
# ═══════════════════════════════════════════════════════════════════════════
VOLUME = [
    S("intuition", "Iris, hitung, jumlahkan",
      r"""<p>Roti tawar diiris tipis: volume roti = jumlah volume tiap irisan. Printer 3D mencetak benda lapis demi lapis, dan CT scan
      merekonstruksi organ dari irisan-irisan penampang. Integral adalah versi limit dari ide ini: irisan setebal $dx$, lalu dijumlahkan.</p>
      <p>Resep yang sama untuk semua aplikasi: <b>(1)</b> gambar, <b>(2)</b> ambil satu irisan tipis, <b>(3)</b> tulis ukurannya
      (luas, volume, panjang) sebagai fungsi posisi, <b>(4)</b> integralkan.</p>""",
      "Jangan hafal rumus volume. Hafalkan cara MENGIRIS. Rumus apa pun bisa kamu turunkan ulang dari satu irisan."),
    S("theorem", "Luas daerah antara kurva",
      r"""<p>Irisan tegak (terhadap $x$) dan irisan mendatar (terhadap $y$):
      $$A = \int_a^b\big[f_{\text{atas}}(x) - g_{\text{bawah}}(x)\big]\,dx, \qquad A = \int_c^d\big[x_{\text{kanan}}(y) - x_{\text{kiri}}(y)\big]\,dy.$$</p>
      <p><b>Pohon keputusan arah irisan:</b></p>""" +
      pohon(r"Gambar daerahnya dan cari semua titik potong.",
            r"Kurva atas dan bawah sama di sepanjang interval? Iris tegak ($dx$).",
            r"Batas atas/bawah berganti di tengah, tetapi batas kanan/kiri tetap? Iris mendatar ($dy$), supaya cukup satu integral.",
            r"Kurva saling memotong di dalam interval? Pecah integral di titik potongnya.") +
      r"""<p><b>Contoh (dy lebih efisien).</b> Daerah antara $y^2 = 2x + 6$ dan $y = x - 1$. Titik potong di $y = -2$ dan $y = 4$.
      Kanan $x = y + 1$, kiri $x = \tfrac{y^2}{2} - 3$:
      $$A = \int_{-2}^{4}\left(y + 4 - \frac{y^2}{2}\right)dy = \left[\frac{y^2}{2} + 4y - \frac{y^3}{6}\right]_{-2}^{4} = 18.$$
      Dengan irisan tegak, soal ini butuh dua integral.</p>""",
      "Selalu tanya: 'atas dikurangi bawah' atau 'kanan dikurangi kiri'. Hasil negatif berarti urutannya terbalik."),
    S("theorem", "Volume benda putar: cakram, cincin, kulit",
      r"""<div class="table-scroll"><table class="lesson-table"><thead><tr><th>Metode</th><th>Irisan</th><th>Rumus</th></tr></thead><tbody>
        <tr><td>Cakram</td><td>tegak lurus sumbu, menempel sumbu</td><td>$V = \displaystyle\int_a^b\pi\,[R(x)]^2\,dx$</td></tr>
        <tr><td>Cincin (washer)</td><td>tegak lurus sumbu, berlubang</td><td>$V = \displaystyle\int_a^b\pi\left([R(x)]^2 - [r(x)]^2\right)dx$</td></tr>
        <tr><td>Kulit tabung</td><td>sejajar sumbu</td><td>$V = \displaystyle\int_a^b 2\pi\,(\text{jari-jari})(\text{tinggi})\,dx$</td></tr>
        <tr><td>Penampang umum</td><td>penampang diketahui</td><td>$V = \displaystyle\int_a^b A(x)\,dx$</td></tr>
      </tbody></table></div>
      <p>Kulit tabung: bayangkan tabung tipis dibuka menjadi lembaran persegi panjang berukuran $2\pi r \times h \times dx$.</p>""",
      "Rumus cincin adalah π(R² − r²), BUKAN π(R − r)². Dua lingkaran dikurangi, bukan jari-jarinya yang dikurangi dulu."),
    S("derivation", "Pohon keputusan: cakram/cincin atau kulit?",
      pohon(r"Tentukan sumbu putar dan gambar daerahnya.",
            r"Irisan <b>tegak lurus</b> sumbu mudah ditulis? Cakram (daerah menempel sumbu) atau cincin (ada celah ke sumbu).",
            r"Untuk memakai cakram kamu harus membalik fungsi yang sulit (misalnya $y = 2x^2 - x^3$ diputar terhadap sumbu $y$)? Pakai <b>kulit tabung</b>, irisan sejajar sumbu.",
            r"Sumbu putar bukan sumbu koordinat, misalnya $y = -1$ atau $x = 2$? Jari-jari = <b>jarak</b> ke sumbu: $R = f(x) - (-1)$, atau jari-jari kulit $= 2 - x$.",
            r"Tulis integral, cek batas, dan hitung.") +
      note(r"Ringkasnya: irisan $\perp$ sumbu → cakram/cincin; irisan $\parallel$ sumbu → kulit. Variabel integrasi mengikuti arah tebal irisan."),
      "Kalau ragu, coba keduanya di kertas coretan. Yang menghasilkan satu integral tanpa invers fungsi biasanya yang benar."),
    S("example", "Bedah soal: metode cincin",
      r"""<p><b>Soal.</b> Daerah antara $y = x$ dan $y = x^2$ diputar terhadap sumbu $x$. Hitung volumenya.</p>""" +
      steps(r"Titik potong $x = 0$ dan $x = 1$; pada $[0, 1]$ kurva luar $y = x$, kurva dalam $y = x^2$.",
            r"Irisan tegak lurus sumbu $x$ berlubang → cincin: $R = x$, $r = x^2$.",
            r"$V = \pi\displaystyle\int_0^1\left(x^2 - x^4\right)dx = \pi\left(\frac13 - \frac15\right) = \frac{2\pi}{15}$.") +
      note(r"Volume bola berjari-jari $r$ dengan cakram: $\pi\displaystyle\int_{-r}^{r}(r^2 - x^2)\,dx = \tfrac43\pi r^3$. Rumus SMP-mu ternyata integral."),
      "Geser x: luas cincin di posisi itu adalah π(R² − r²). Volume = jumlah semua cincin setebal dx.",
      [g("Daerah antara y = x dan y = x², diputar terhadap sumbu x", [-0.2, 1.3], [-1.2, 1.2], [param("X", "Posisi irisan x", 0, 1, 0.01, 0.6, "x")],
         [{"type": "fill", "upper": "x", "lower": "x*x", "from": 0, "to": 1, "color": "blue"},
          {"type": "fill", "upper": "-x*x", "lower": "-x", "from": 0, "to": 1, "color": "blue", "opacity": 0.12},
          {"type": "fn", "expr": "x", "color": "blue", "from": 0, "to": 1}, {"type": "fn", "expr": "x*x", "color": "orange", "from": 0, "to": 1},
          {"type": "fn", "expr": "-x", "color": "gray", "dash": True, "from": 0, "to": 1}, {"type": "fn", "expr": "-x*x", "color": "gray", "dash": True, "from": 0, "to": 1},
          {"type": "segment", "x1": "X", "y1": "-X", "x2": "X", "y2": "X", "color": "red", "width": 2}],
         [readout("R = x", "X", 3), readout("r = x²", "X*X", 3), readout("Luas cincin π(R² − r²)", "pi*(X*X - X*X*X*X)", 4), readout("Volume total 2π/15", "2*pi/15", 4)],
         "Bayangan abu-abu adalah pantulan daerah: begitulah penampang benda putarnya.")]),
    S("example", "Bedah soal: metode kulit tabung",
      r"""<p><b>Soal.</b> Daerah di bawah $y = 2x^2 - x^3$ dan di atas sumbu $x$ diputar terhadap sumbu $y$.</p>""" +
      steps(r"Dengan cincin kita perlu menyatakan $x$ dalam $y$ dari persamaan kubik. Sulit, jadi pilih kulit.",
            r"Irisan tegak di posisi $x$: jari-jari $x$, tinggi $2x^2 - x^3$, tebal $dx$, untuk $0 \le x \le 2$.",
            r"$V = \displaystyle\int_0^2 2\pi x\left(2x^2 - x^3\right)dx = 2\pi\left[\frac{x^4}{2} - \frac{x^5}{5}\right]_0^2 = 2\pi\left(8 - \frac{32}{5}\right) = \frac{16\pi}{5}$."),
      "Pada kulit tabung, jari-jari = jarak irisan ke sumbu putar. Sumbu y berarti jari-jari x; sumbu x = 3 berarti 3 − x.",
      [g("Kulit tabung: y = 2x² − x³ diputar terhadap sumbu y", [-0.2, 2.3], [-0.2, 1.5], [param("X", "Posisi kulit x", 0.05, 1.95, 0.01, 1.2, "x")],
         [{"type": "fill", "upper": "2*x*x - x*x*x", "from": 0, "to": 2, "color": "green"},
          {"type": "fn", "expr": "2*x*x - x*x*x", "color": "green", "from": 0, "to": 2, "label": "y = 2x² − x³"},
          {"type": "segment", "x1": "X", "y1": 0, "x2": "X", "y2": "2*X*X - X*X*X", "color": "red", "width": 4}],
         [readout("Jari-jari", "X", 3), readout("Tinggi", "2*X*X - X*X*X", 4), readout("Luas kulit 2π·r·h", "2*pi*X*(2*X*X - X*X*X)", 4), readout("Volume 16π/5", "16*pi/5", 4)],
         "Garis merah diputar mengelilingi sumbu y menjadi satu kulit tabung tipis.")]),
    S("theorem", "Panjang busur & luas permukaan",
      r"""<p>Irisan kecil kurva hampir lurus: $ds = \sqrt{dx^2 + dy^2} = \sqrt{1 + \left(\tfrac{dy}{dx}\right)^2}\,dx$. Maka
      $$L = \int_a^b\sqrt{1 + [f'(x)]^2}\,dx, \qquad S = \int_a^b 2\pi f(x)\sqrt{1 + [f'(x)]^2}\,dx\ \ (\text{diputar terhadap sumbu } x).$$</p>
      <p><b>Contoh.</b> Panjang $y = x^{3/2}$ dari $x = 0$ sampai $4$:</p>""" +
      steps(r"$f'(x) = \tfrac32x^{1/2}$, sehingga $1 + [f']^2 = 1 + \tfrac94x$.",
            r"$L = \displaystyle\int_0^4\sqrt{1 + \tfrac94x}\,dx = \frac{8}{27}\left[\left(1 + \tfrac94x\right)^{3/2}\right]_0^4 = \frac{8}{27}\left(10\sqrt{10} - 1\right) \approx 9.07$.") +
      note(r"Integral panjang busur jarang punya antiturunan elementer; di dunia nyata (panjang kabel, rel) dihitung numerik. Soal ujian sengaja dipilih agar $1 + [f']^2$ menjadi kuadrat sempurna atau linear."),
      "Kalau 1 + (f')² tidak bisa disederhanakan, cek ulang soalnya. Soal ujian hampir selalu dirancang 'cantik'."),
    S("pitfall", "Jebakan ujian",
      r"""<ul class="lesson-list">
        <li>Cincin: menulis $\pi(R - r)^2$, seharusnya $\pi(R^2 - r^2)$.</li>
        <li>Lupa faktor $\pi$ atau $2\pi$.</li>
        <li>Sumbu putar digeser ($y = -1$) tetapi jari-jari tetap ditulis $f(x)$, seharusnya $f(x) + 1$.</li>
        <li>Kulit tabung: tertukar antara jari-jari dan tinggi.</li>
        <li>Luas antar kurva yang saling memotong dihitung dengan satu integral, sehingga bagian positif dan negatif saling menghapus.</li>
        <li>Panjang busur: lupa akar atau lupa mengkuadratkan $f'$.</li>
      </ul>""",
      "Uji kewajaran: volume harus positif dan lebih kecil dari tabung yang membungkus benda itu."),
    S("checkpoint", "Mini checkpoint",
      qa(r"1. Luas daerah antara $y = \sin x$ dan $y = \cos x$ pada $\left[0, \tfrac{\pi}{2}\right]$.",
         r"<p>Pecah di $x = \tfrac{\pi}{4}$: $\displaystyle\int_0^{\pi/4}(\cos x - \sin x)\,dx + \int_{\pi/4}^{\pi/2}(\sin x - \cos x)\,dx = (\sqrt2 - 1) + (\sqrt2 - 1) = 2\sqrt2 - 2$.</p>") +
      qa(r"2. Daerah di bawah $y = \sqrt{x}$, $0 \le x \le 4$, diputar terhadap sumbu $x$. Volumenya?",
         r"<p>Cakram: $\pi\displaystyle\int_0^4 x\,dx = 8\pi$.</p>"),
      "Soal 1 adalah contoh kurva yang bersilangan. Tanpa dipecah, jawabannya menjadi 0."),
]

# ═══════════════════════════════════════════════════════════════════════════
# 7. Kerja, Tekanan & Pusat Massa
# ═══════════════════════════════════════════════════════════════════════════
FISIKA = [
    S("intuition", "Ketika gaya, kedalaman, atau massa tidak konstan",
      r"""<p>Rumus SMA $W = F\cdot d$ hanya berlaku untuk gaya konstan. Pegas makin sulit ditarik makin jauh; air di dasar bendungan menekan lebih keras
      daripada di permukaan; batang lengan robot tidak bermassa seragam. Semua kasus ini diselesaikan dengan resep yang sama:
      <b>iris tipis sampai besarannya hampir konstan, lalu jumlahkan dengan integral</b>.</p>
      <p>Bagi anak FT, inilah dasar mekanika fluida (desain bendungan, tangki) dan statika (titik berat struktur).</p>""",
      "Satuan adalah teman terbaik di topik ini. Kerja dalam joule (N·m), gaya dalam newton, massa dalam kg."),
    S("theorem", "Kerja oleh gaya berubah",
      r"""<p>$$W = \int_a^b F(x)\,dx$$</p>
      <ul class="lesson-list">
        <li><b>Hukum Hooke:</b> pegas yang diregangkan $x$ dari panjang alaminya butuh gaya $F = kx$.</li>
        <li><b>Memompa cairan:</b> iris cairan menjadi lapisan tipis; kerja satu lapisan = (berat lapisan) × (jarak angkat):
        $$W = \int \rho g\,A(y)\,D(y)\,dy,$$ dengan $A(y)$ luas penampang lapisan dan $D(y)$ jarak lapisan ke titik keluar.</li>
      </ul>""",
      "Dalam soal pompa, setiap lapisan diangkat sejauh yang BERBEDA. Itulah alasan butuh integral, bukan perkalian biasa."),
    S("example", "Bedah soal: pegas",
      r"""<p><b>Soal.</b> Gaya $40$ N menahan pegas teregang $0.1$ m dari panjang alaminya. Berapa kerja untuk meregangkannya dari $0.1$ m sampai $0.2$ m?</p>""" +
      steps(r"$40 = k(0.1) \Rightarrow k = 400$ N/m.",
            r"$W = \displaystyle\int_{0.1}^{0.2}400x\,dx = 200\left(0.2^2 - 0.1^2\right) = 6$ J."),
      "Batas integral pegas diukur dari PANJANG ALAMI, bukan dari panjang total pegas. Ini jebakan paling umum.",
      [g("Kerja = luas di bawah grafik F = 400x", [0, 0.35], [-5, 150], [param("b", "Regangan akhir (m)", 0.1, 0.3, 0.005, 0.2, "b")],
         [{"type": "fill", "upper": "400*x", "from": 0.1, "to": "b", "color": "amber"},
          {"type": "fn", "expr": "400*x", "color": "blue", "label": "F = 400x"}],
         [readout("W (J) = 200(b² − 0,01)", "200*(b*b - 0.01)", 4)],
         "Menggandakan regangan dari 0,1 ke 0,2 butuh 6 J, tapi dari 0,2 ke 0,3 butuh 10 J.")]),
    S("example", "Bedah soal: memompa air dari tangki",
      r"""<p><b>Soal.</b> Tangki silinder tegak berjari-jari $2$ m dan tinggi $5$ m penuh air ($\rho = 1000$ kg/m³, $g = 9.8$ m/s²).
      Berapa kerja memompa seluruh air keluar lewat tepi atas?</p>""" +
      steps(r"Ambil lapisan air setebal $dy$ pada ketinggian $y$ dari dasar ($0 \le y \le 5$).",
            r"Volume lapisan $\pi(2)^2dy = 4\pi\,dy$; beratnya $9800\cdot 4\pi\,dy$ N.",
            r"Jarak angkat ke tepi atas: $5 - y$.",
            r"$W = \displaystyle\int_0^5 39200\pi(5 - y)\,dy = 39200\pi\left[5y - \frac{y^2}{2}\right]_0^5 = 490000\pi \approx 1.54\times10^6$ J.") +
      note(r"Untuk tangki kerucut atau bola, luas penampang $A(y)$ ikut berubah; cari jari-jari lapisan dengan segitiga sebangun atau Pythagoras."),
      "Tetapkan sistem koordinat di awal (dasar = 0 atau atas = 0) dan konsisten. Jarak angkat mengikuti pilihan itu."),
    S("theorem", "Gaya hidrostatik pada dinding",
      r"""<p>Tekanan pada kedalaman $d$: $P = \rho g d$. Pada pelat tegak, iris mendatar setebal $dh$ di kedalaman $h$ dengan lebar $w(h)$:
      $$F = \int_a^b\rho g\,h\,w(h)\,dh.$$</p>
      <p><b>Contoh.</b> Pintu air persegi panjang lebar $3$ m dan tinggi $2$ m, tepi atasnya tepat di permukaan air:
      $$F = \int_0^2 9800\cdot h\cdot 3\,dh = 9800\cdot 3\cdot\frac{2^2}{2} = 58\,800\ \text{N}.$$</p>""" +
      note(r"Karena tekanan bertambah linear terhadap kedalaman, bendungan dibuat jauh lebih tebal di dasar daripada di puncak."),
      "Ukur h sebagai KEDALAMAN dari permukaan air, bukan ketinggian dari dasar. Rumus P = ρgh memakai kedalaman."),
    S("theorem", "Momen & pusat massa",
      r"""<p><b>Batang</b> dengan rapat massa $\rho(x)$ pada $[a, b]$: $\ m = \displaystyle\int_a^b\rho(x)\,dx$, $\ \bar{x} = \dfrac{1}{m}\displaystyle\int_a^b x\,\rho(x)\,dx$.</p>
      <p><b>Keping homogen</b> (lamina) di antara $y = f(x)$ dan $y = g(x)$ dengan luas $A$:
      $$\bar{x} = \frac1A\int_a^b x\big[f(x) - g(x)\big]dx, \qquad \bar{y} = \frac1A\int_a^b\frac12\big[f(x)^2 - g(x)^2\big]dx.$$</p>
      <p><b>Teorema Pappus:</b> volume benda putar = luas daerah × jarak yang ditempuh pusat massanya, $V = 2\pi\bar{r}A$.</p>""",
      "Faktor 1/2 pada ȳ datang dari titik tengah irisan tegak: irisan dari g ke f punya pusat di (f + g)/2."),
    S("example", "Bedah soal: pusat massa keping",
      r"""<p><b>Soal.</b> Pusat massa daerah di bawah $y = \sqrt{x}$, $0 \le x \le 4$.</p>""" +
      steps(r"$A = \displaystyle\int_0^4\sqrt{x}\,dx = \frac{16}{3}$.",
            r"$\bar{x} = \dfrac{3}{16}\displaystyle\int_0^4 x^{3/2}dx = \dfrac{3}{16}\cdot\dfrac{64}{5} = \dfrac{12}{5}$.",
            r"$\bar{y} = \dfrac{3}{16}\displaystyle\int_0^4\frac{x}{2}dx = \dfrac{3}{16}\cdot 4 = \dfrac34$.",
            r"Pusat massa $\left(\tfrac{12}{5}, \tfrac34\right)$. Cek Pappus: $V = 2\pi\cdot\tfrac34\cdot\tfrac{16}{3} = 8\pi$, sama dengan hasil cakram.") ,
      "Pusat massa condong ke arah bagian yang lebih 'gemuk'. Di sini daerah lebih lebar di kanan, jadi x̄ > 2.",
      [g("Pusat massa daerah di bawah √x", [-0.3, 4.5], [-0.3, 2.3], [],
         [{"type": "fill", "upper": "sqrt(x)", "from": 0, "to": 4, "color": "blue"},
          {"type": "fn", "expr": "sqrt(x)", "color": "blue", "from": 0, "to": 4, "label": "y = √x"},
          {"type": "point", "x": 2.4, "y": 0.75, "color": "red"},
          {"type": "text", "x": 2.5, "y": 0.95, "text": "(12/5, 3/4)", "color": "red"}],
         [readout("x̄", "12/5", 3), readout("ȳ", "3/4", 3)],
         "Daerah ini akan seimbang bila ditopang tepat di titik merah.")]),
    S("pitfall", "Jebakan ujian",
      r"""<ul class="lesson-list">
        <li>Memakai massa (kg) sebagai gaya. Berat = massa × $g$, dalam newton.</li>
        <li>Pegas: batas diukur dari panjang total, bukan dari panjang alami.</li>
        <li>Pompa: jarak angkat diukur ke dasar tangki, padahal seharusnya ke titik keluar (bisa di atas tangki).</li>
        <li>Hidrostatik: memakai ketinggian dari dasar sebagai kedalaman.</li>
        <li>Pusat massa: lupa membagi dengan luas atau massa total, atau lupa faktor $\tfrac12$ di $\bar{y}$.</li>
      </ul>""",
      "Cek kewajaran: pusat massa harus berada di dalam 'kotak pembungkus' daerah. Kalau di luar, ada yang salah."),
    S("checkpoint", "Mini checkpoint",
      qa(r"1. Butuh $2$ J untuk meregangkan pegas $0.2$ m dari panjang alaminya. Berapa $k$?",
         r"<p>$\displaystyle\int_0^{0.2}kx\,dx = 0.02k = 2 \Rightarrow k = 100$ N/m.</p>") +
      qa(r"2. Batang $0 \le x \le 2$ m dengan rapat massa $\rho(x) = 1 + x$ kg/m. Massa dan pusat massanya?",
         r"<p>$m = \displaystyle\int_0^2(1 + x)\,dx = 4$ kg; $\ \bar{x} = \tfrac14\displaystyle\int_0^2(x + x^2)\,dx = \tfrac14\cdot\tfrac{14}{3} = \tfrac76$ m.</p>"),
      "Soal 2: rapat massa naik ke kanan, jadi pusat massanya harus di kanan titik tengah 1 m. Benar, 7/6 > 1."),
]

# ═══════════════════════════════════════════════════════════════════════════
# 8. Persamaan Diferensial Orde Satu
# ═══════════════════════════════════════════════════════════════════════════
PD = [
    S("intuition", "Hukum perubahan, bukan rumus jadi",
      r"""<p>Fisika jarang memberi rumus $y(t)$ secara langsung. Yang diberikan adalah <b>hukum perubahannya</b>:
      "laju peluruhan sebanding dengan jumlah zat" ($\tfrac{dN}{dt} = -kN$), "arus di rangkaian RL berubah sesuai tegangan sisa",
      "kopi mendingin sebanding dengan selisih suhunya dengan ruangan".</p>
      <p>Persamaan diferensial (PD) menghubungkan fungsi dengan turunannya. Menyelesaikannya berarti mencari <b>fungsi</b>, bukan angka.
      Model epidemi, rangkaian listrik, populasi, bahkan <i>neural ODE</i> di machine learning semuanya berbentuk PD.</p>""",
      "Solusi PD adalah fungsi. Cek jawabanmu dengan mensubstitusikannya kembali ke persamaan."),
    S("theorem", "Istilah dasar, medan arah, metode Euler",
      r"""<ul class="lesson-list">
        <li><b>Orde</b> = turunan tertinggi. $y' = x - y$ berorde satu.</li>
        <li><b>Solusi umum</b> memuat konstanta $C$ (satu keluarga kurva); <b>masalah nilai awal</b> $y(x_0) = y_0$ memilih satu anggota.</li>
        <li><b>Medan arah:</b> untuk $y' = F(x, y)$, gambar ruas garis kecil berkemiringan $F(x, y)$ di tiap titik. Kurva solusi mengikuti arah ruas-ruas itu.</li>
        <li><b>Metode Euler:</b> melangkah sepanjang garis singgung, $\ y_{n+1} = y_n + h\,F(x_n, y_n)$, $x_{n+1} = x_n + h$.</li>
      </ul>""",
      "Euler adalah algoritma numerik pertama yang kamu pelajari. Semua simulator fisika game memakai ide yang sama.",
      [g("Metode Euler untuk y' = y, y(0) = 1", [-0.1, 2.2], [-0.5, 8], [param("h", "Ukuran langkah h", 0.05, 1, 0.05, 0.5, "h")],
         [{"type": "fn", "expr": "exp(x)", "color": "blue", "label": "solusi eksak eˣ"},
          {"type": "iter", "id": "E", "init": {"xs": 0, "ys": 1}, "update": {"xs": "xs + h", "ys": "ys + h*ys"}, "steps": "round(2/h)", "color": "red"}],
         [readout("Euler di x = 2", "E.ys", 5), readout("Eksak e²", "exp(2)", 5), readout("Galat", "exp(2) - E.ys", 5)],
         "Kecilkan h: titik-titik merah makin menempel kurva biru, tapi butuh lebih banyak langkah.")]),
    S("derivation", "Pohon keputusan: PD orde satu",
      pohon(r"Bisa ditulis $\dfrac{dy}{dx} = g(x)\,h(y)$? → <b>PD terpisah</b>: pisahkan lalu integralkan kedua ruas.",
            r"Bisa ditulis $y' + P(x)\,y = Q(x)$ ($y$ dan $y'$ berpangkat satu, tidak dikalikan)? → <b>PD linear</b>: faktor integrasi.",
            r"Berbentuk $y' + P(x)y = Q(x)y^n$? → <b>Bernoulli</b>: substitusi $v = y^{1-n}$ mengubahnya menjadi linear.",
            r"Bukan semuanya? → analisis kualitatif (medan arah, titik setimbang) atau numerik (Euler, Runge–Kutta).") +
      note(r"Sebagian PD masuk dua kategori, misalnya $y' = 2y$ terpisah sekaligus linear. Pilih yang paling cepat untukmu."),
      "Sebelum menghitung, tulis ulang PD dalam bentuk y' = ... Bentuk itu membuat jenisnya langsung terlihat."),
    S("example", "PD terpisah",
      r"""<p><b>Metode:</b> $\dfrac{dy}{h(y)} = g(x)\,dx$, integralkan kedua ruas, tambahkan <b>satu</b> konstanta, lalu selesaikan untuk $y$.</p>
      <p><b>Soal 1.</b> $\dfrac{dy}{dt} = ky$ (pertumbuhan/peluruhan): $\displaystyle\int\frac{dy}{y} = \int k\,dt \Rightarrow \ln|y| = kt + C \Rightarrow y = y_0e^{kt}$.</p>
      <p><b>Soal 2.</b> $\dfrac{dy}{dx} = xy^2$, $y(0) = 1$.</p>""" +
      steps(r"Pisahkan: $y^{-2}dy = x\,dx$.",
            r"Integralkan: $-\dfrac1y = \dfrac{x^2}{2} + C$.",
            r"$y(0) = 1$: $-1 = C$, sehingga $\dfrac1y = 1 - \dfrac{x^2}{2}$ dan $y = \dfrac{2}{2 - x^2}$.",
            r"Solusi hanya berlaku untuk $|x| &lt; \sqrt2$: di $x = \sqrt2$ solusinya meledak ke tak hingga.") +
      note(r"Membagi dengan $h(y)$ bisa menghilangkan solusi konstan $h(y) = 0$. Untuk $y' = xy^2$, $y = 0$ juga solusi."),
      "Konstanta C cukup ditulis di satu ruas. Dua konstanta di dua ruas bisa digabung jadi satu."),
    S("theorem", "PD linear & faktor integrasi",
      r"""<p>Untuk $y' + P(x)\,y = Q(x)$:</p>""" +
      steps(r"Hitung faktor integrasi $\mu(x) = e^{\int P(x)\,dx}$ (tanpa $+C$).",
            r"Kalikan seluruh persamaan dengan $\mu$; ruas kiri menjadi turunan perkalian: $(\mu y)' = \mu Q$.",
            r"Integralkan: $\mu y = \displaystyle\int\mu Q\,dx + C$.",
            r"Bagi dengan $\mu$: $\ y = \dfrac{1}{\mu}\left(\displaystyle\int\mu Q\,dx + C\right)$.") +
      r"""<p><b>Contoh.</b> $xy' + y = x^2$ ($x &gt; 0$). Bentuk baku: $y' + \tfrac1x y = x$, $\mu = e^{\ln x} = x$.
      Maka $(xy)' = x^2$, $xy = \tfrac{x^3}{3} + C$, dan $y = \tfrac{x^2}{3} + \tfrac{C}{x}$.</p>""",
      "Langkah 2 adalah inti ide: μ dipilih tepat agar ruas kiri menjadi hasil aturan perkalian (μy)'. Tidak perlu dihafal, cukup dipahami."),
    S("example", "Bedah soal: rangkaian RL (FT Elektro)",
      r"""<p><b>Soal.</b> Rangkaian RL dengan sumber $E$ volt: $L\dfrac{di}{dt} + Ri = E$, $i(0) = 0$. Cari arus $i(t)$.</p>""" +
      steps(r"Bentuk baku: $i' + \tfrac{R}{L}i = \tfrac{E}{L}$, sehingga $\mu = e^{Rt/L}$.",
            r"$\left(e^{Rt/L}i\right)' = \tfrac{E}{L}e^{Rt/L} \Rightarrow e^{Rt/L}i = \tfrac{E}{R}e^{Rt/L} + C$.",
            r"$i = \tfrac{E}{R} + Ce^{-Rt/L}$; $i(0) = 0 \Rightarrow C = -\tfrac{E}{R}$.",
            r"$i(t) = \dfrac{E}{R}\left(1 - e^{-Rt/L}\right)$. Arus naik menuju nilai tunak $\tfrac{E}{R}$ dengan konstanta waktu $\tau = \tfrac{L}{R}$.") ,
      "Setelah satu konstanta waktu τ, arus mencapai sekitar 63% nilai tunaknya. Setelah 5τ, praktis sudah tunak.",
      [g("Arus rangkaian RL, E = 12 V", [0, 5], [0, 7], [param("R", "Hambatan R (Ω)", 2, 12, 0.5, 4, "R"), param("L", "Induktansi L (H)", 0.2, 3, 0.1, 1, "L")],
         [{"type": "fn", "expr": "(12/R)*(1 - exp(-R*x/L))", "color": "blue", "label": "i(t)"},
          {"type": "hline", "y": "12/R", "color": "gray", "dash": True},
          {"type": "vline", "x": "L/R", "color": "orange", "dash": True}],
         [readout("Arus tunak E/R (A)", "12/R", 3), readout("Konstanta waktu L/R (s)", "L/R", 3), readout("i(τ) / (E/R)", "1 - exp(-1)", 3)],
         "Garis oranye menandai t = τ. Perbesar L: arus naik lebih lambat; perbesar R: nilai tunak turun.")]),
    S("example", "Bedah soal: hukum pendinginan Newton",
      r"""<p><b>Soal.</b> Kopi $90^\circ$C diletakkan di ruangan $25^\circ$C. Setelah $5$ menit suhunya $70^\circ$C. Kapan suhunya $40^\circ$C?</p>""" +
      steps(r"Model: $\dfrac{dT}{dt} = k(T - 25)$, PD terpisah, sehingga $T(t) = 25 + 65e^{kt}$ (dari $T(0) = 90$).",
            r"$T(5) = 70$: $65e^{5k} = 45 \Rightarrow k = \tfrac15\ln\tfrac{9}{13} \approx -0.0736$ per menit.",
            r"$40 = 25 + 65e^{kt} \Rightarrow e^{kt} = \tfrac{3}{13} \Rightarrow t = \dfrac{\ln(3/13)}{k} \approx 19.9$ menit.") +
      r"""<p><b>Model logistik.</b> Pertumbuhan dengan kapasitas $K$: $\dfrac{dP}{dt} = rP\left(1 - \dfrac{P}{K}\right)$. Dengan pemisahan variabel dan
      pecahan parsial $\dfrac{K}{P(K - P)} = \dfrac1P + \dfrac{1}{K - P}$, solusinya
      $$P(t) = \frac{K}{1 + Ae^{-rt}}, \qquad A = \frac{K - P_0}{P_0}.$$</p>""",
      "k negatif berarti suhu mendekati suhu ruangan. Kalau hasilmu k positif untuk kopi yang mendingin, ada tanda yang terbalik.",
      [g("Logistik vs eksponensial: pengguna aplikasi (K = 10 000)", [0, 20], [0, 12000],
         [param("r", "Laju r per bulan", 0.1, 1.5, 0.05, 0.5, "r"), param("P0", "Pengguna awal P₀", 100, 5000, 100, 1000, "P₀")],
         [{"type": "fn", "expr": "10000/(1 + ((10000 - P0)/P0)*exp(-r*x))", "color": "blue", "label": "logistik"},
          {"type": "fn", "expr": "P0*exp(r*x)", "color": "red", "dash": True, "label": "eksponensial"},
          {"type": "hline", "y": 10000, "color": "gray", "dash": True}],
         [readout("Waktu mencapai K/2 (bulan)", "ln((10000 - P0)/P0)/r", 3)],
         "Awalnya keduanya mirip; logistik melambat dan mendatar di K saat pasar jenuh.")]),
    S("pitfall", "Jebakan ujian",
      r"""<ul class="lesson-list">
        <li>Lupa $+C$, atau menambahkannya <b>setelah</b> menyelesaikan untuk $y$ (misal $y = e^{x^2} + C$ seharusnya $y = Ce^{x^2}$).</li>
        <li>$\ln|y| = kt + C \Rightarrow y = e^{kt} + e^{C}$. Salah: $y = e^{C}e^{kt} = Ae^{kt}$.</li>
        <li>PD linear: lupa membagi koefisien $y'$ dulu, sehingga $P(x)$ salah.</li>
        <li>Faktor integrasi dikalikan hanya ke ruas kiri, tidak ke $Q(x)$.</li>
        <li>Mengira $y' = y^2 + x$ linear. Ada $y^2$, jadi tidak linear dan juga tidak terpisah.</li>
        <li>Membagi dengan $y$ tanpa mencatat solusi $y = 0$ yang hilang.</li>
      </ul>""",
      "Jebakan kedua sering membuat jawaban kehilangan semua poin. e^(a + b) = e^a · e^b, bukan e^a + e^b."),
    S("checkpoint", "Mini checkpoint",
      qa(r"1. $y' = y\cos x$, $y(0) = 2$.", r"<p>Terpisah: $\ln|y| = \sin x + C$, jadi $y = 2e^{\sin x}$.</p>") +
      qa(r"2. $y' - y = e^{x}$.", r"<p>Linear, $\mu = e^{-x}$: $(e^{-x}y)' = 1$, jadi $y = (x + C)e^{x}$.</p>") +
      qa(r"3. Zat radioaktif berwaktu paruh $10$ tahun. Berapa persen tersisa setelah $25$ tahun?",
         r"<p>$N = N_0\left(\tfrac12\right)^{t/10}$; $\left(\tfrac12\right)^{2.5} \approx 0.177$, sekitar $17.7\%$.</p>"),
      "Soal 3: bentuk (1/2)^(t/T) adalah solusi y = y₀e^(kt) dengan k = −ln 2 / T. Keduanya setara."),
]

# ═══════════════════════════════════════════════════════════════════════════
# 9. Kurva Parametrik & Koordinat Kutub
# ═══════════════════════════════════════════════════════════════════════════
KUTUB = [
    S("intuition", "Lintasan, bukan sekadar grafik",
      r"""<p>Grafik $y = f(x)$ hanya memberi tahu <b>di mana</b> kurva berada. Persamaan parametrik $x = x(t)$, $y = y(t)$ memberi tahu
      <b>kapan</b> dan <b>bagaimana</b> titik bergerak: lintasan peluru, gerak lengan robot, dan kurva Bézier yang membentuk setiap huruf font di layarmu.</p>
      <p>Koordinat kutub $(r, \theta)$ menyatakan titik lewat jarak dan arah, cocok untuk radar, sonar, pola pancar antena, dan orbit.</p>""",
      "Bayangkan t sebagai waktu. Satu titik di kurva bisa dilewati lebih dari sekali pada t yang berbeda.",
      [g("Lintasan peluru: x = v cos α · t, y = v sin α · t − 4,9t²", [0, 95], [0, 50],
         [param("v", "Kecepatan awal v (m/s)", 5, 30, 1, 25, "v"), param("A", "Sudut α (derajat)", 10, 85, 1, 45, "α")],
         [{"type": "param", "x": "v*cos(A*pi/180)*t", "y": "v*sin(A*pi/180)*t - 4.9*t*t", "t": [0, "2*v*sin(A*pi/180)/9.8"], "color": "blue", "label": "lintasan"}],
         [readout("Jarak jangkau v²sin 2α / g (m)", "v*v*sin(2*A*pi/180)/9.8", 4), readout("Tinggi maksimum (m)", "pow(v*sin(A*pi/180), 2)/19.6", 4)],
         "Jarak terjauh tercapai di α = 45°. Sudut 30° dan 60° memberi jarak yang sama.")]),
    S("theorem", "Kalkulus kurva parametrik",
      r"""<p>Untuk $x = x(t)$, $y = y(t)$:
      $$\frac{dy}{dx} = \frac{dy/dt}{dx/dt}, \qquad \frac{d^2y}{dx^2} = \frac{\dfrac{d}{dt}\left(\dfrac{dy}{dx}\right)}{dx/dt},$$
      $$L = \int_\alpha^\beta\sqrt{\left(\frac{dx}{dt}\right)^2 + \left(\frac{dy}{dt}\right)^2}\,dt, \qquad A = \int_\alpha^\beta y(t)\,x'(t)\,dt.$$</p>
      <p>Garis singgung mendatar saat $\tfrac{dy}{dt} = 0$ (dan $\tfrac{dx}{dt} \ne 0$); tegak saat $\tfrac{dx}{dt} = 0$.</p>""",
      "Turunan kedua parametrik BUKAN (d²y/dt²)/(d²x/dt²). Turunkan dy/dx terhadap t, lalu bagi dengan dx/dt."),
    S("example", "Bedah soal: sikloid",
      r"""<p>Titik di tepi roda berjari-jari $r$ yang menggelinding membentuk <b>sikloid</b>: $x = r(t - \sin t)$, $y = r(1 - \cos t)$.</p>""" +
      steps(r"Kemiringan: $\dfrac{dy}{dx} = \dfrac{r\sin t}{r(1 - \cos t)} = \dfrac{\sin t}{1 - \cos t}$. Di $t = 2\pi$ (titik sentuh tanah) penyebutnya $0$: ujung runcing.",
            r"Panjang satu lengkung: $\left(x'\right)^2 + \left(y'\right)^2 = r^2\left[(1 - \cos t)^2 + \sin^2 t\right] = 2r^2(1 - \cos t) = 4r^2\sin^2\tfrac{t}{2}$.",
            r"$L = \displaystyle\int_0^{2\pi}2r\sin\tfrac{t}{2}\,dt = \Big[-4r\cos\tfrac{t}{2}\Big]_0^{2\pi} = 8r$.") +
      note(r"Sikloid adalah kurva <b>brakistokron</b>: lintasan luncur tercepat antara dua titik, lebih cepat dari garis lurus."),
      "Identitas 1 − cos t = 2 sin²(t/2) adalah kunci hampir semua soal sikloid. Simpan di kepalamu.",
      [g("Sikloid (r = 1)", [-0.5, 13], [-0.5, 3], [param("T", "Parameter t", 0.05, 12.5, 0.01, 2, "t")],
         [{"type": "param", "x": "t - sin(t)", "y": "1 - cos(t)", "t": [0, "4*pi"], "color": "blue", "label": "sikloid"},
          {"type": "param", "x": "T + cos(t)", "y": "1 + sin(t)", "t": [0, "2*pi"], "color": "gray", "dash": True},
          {"type": "point", "x": "T - sin(T)", "y": "1 - cos(T)", "color": "red"}],
         [readout("dy/dx = sin t / (1 − cos t)", "sin(T)/(1 - cos(T))", 4), readout("Panjang busur dari t = 0", "T <= 2*pi ? 4*(1 - cos(T/2)) : 8 + 4*(1 + cos(T/2))", 4)],
         "Lingkaran abu-abu adalah roda. Titik merah menempel di tepinya.")]),
    S("theorem", "Koordinat kutub & kurva-kurva klasik",
      r"""<p>$$x = r\cos\theta, \quad y = r\sin\theta, \qquad r^2 = x^2 + y^2, \quad \tan\theta = \frac{y}{x}.$$</p>
      <div class="table-scroll"><table class="lesson-table"><thead><tr><th>Persamaan</th><th>Kurva</th></tr></thead><tbody>
        <tr><td>$r = a$</td><td>lingkaran berpusat di titik asal</td></tr>
        <tr><td>$r = 2a\cos\theta$</td><td>lingkaran berpusat $(a, 0)$, sebab $x^2 + y^2 = 2ax$</td></tr>
        <tr><td>$r = a(1 + \cos\theta)$</td><td>kardioid (pola mikrofon kardioid)</td></tr>
        <tr><td>$r = \cos n\theta$</td><td>mawar: $n$ kelopak bila $n$ ganjil, $2n$ bila genap</td></tr>
        <tr><td>$r = a\theta$</td><td>spiral Archimedes</td></tr>
      </tbody></table></div>""",
      "Untuk mengubah ke Kartesius, kalikan dengan r bila perlu: r = 2 cos θ → r² = 2r cos θ → x² + y² = 2x.",
      [g("Kurva mawar r = cos(kθ)", [-1.3, 1.3], [-1.3, 1.3], [param("k", "k", 1, 7, 1, 3, "k")],
         [{"type": "param", "x": "cos(k*t)*cos(t)", "y": "cos(k*t)*sin(t)", "t": [0, "2*pi"], "samples": 600, "color": "pink", "label": "r = cos kθ"}],
         [readout("Jumlah kelopak", "k % 2 == 1 ? k : 2*k", 0)],
         "k ganjil: kurva menelusuri kelopak yang sama dua kali dalam 0 ≤ θ ≤ 2π. Penting saat menghitung luas.")]),
    S("theorem", "Kalkulus kutub",
      r"""<p>Dengan $r = f(\theta)$ dan $\theta$ sebagai parameter ($x = f(\theta)\cos\theta$, $y = f(\theta)\sin\theta$):
      $$\frac{dy}{dx} = \frac{r'\sin\theta + r\cos\theta}{r'\cos\theta - r\sin\theta}, \qquad A = \frac12\int_\alpha^\beta r^2\,d\theta, \qquad L = \int_\alpha^\beta\sqrt{r^2 + (r')^2}\,d\theta.$$</p>
      <p>Rumus luas datang dari juring tipis: luas juring berjari-jari $r$ dan sudut $d\theta$ adalah $\tfrac12r^2d\theta$.</p>
      <p><b>Luas antara dua kurva kutub:</b> $A = \tfrac12\displaystyle\int_\alpha^\beta\left(r_{\text{luar}}^2 - r_{\text{dalam}}^2\right)d\theta$.</p>""",
      "Irisan di koordinat kutub bukan persegi panjang, tapi juring (potongan pizza). Itulah asal faktor 1/2."),
    S("example", "Bedah soal: luas kutub",
      r"""<p><b>Soal 1.</b> Luas kardioid $r = 1 + \cos\theta$.</p>""" +
      steps(r"$A = \tfrac12\displaystyle\int_0^{2\pi}(1 + \cos\theta)^2d\theta = \tfrac12\int_0^{2\pi}\left(1 + 2\cos\theta + \cos^2\theta\right)d\theta$.",
            r"$\int_0^{2\pi}\cos\theta = 0$, $\int_0^{2\pi}\cos^2\theta = \pi$, sehingga $A = \tfrac12(2\pi + \pi) = \tfrac{3\pi}{2}$.") +
      r"""<p><b>Soal 2.</b> Luas daerah di dalam lingkaran $r = 3\cos\theta$ dan di luar kardioid $r = 1 + \cos\theta$.</p>""" +
      steps(r"Titik potong: $3\cos\theta = 1 + \cos\theta \Rightarrow \cos\theta = \tfrac12$, $\theta = \pm\tfrac{\pi}{3}$.",
            r"$A = \tfrac12\displaystyle\int_{-\pi/3}^{\pi/3}\left[9\cos^2\theta - (1 + \cos\theta)^2\right]d\theta = \int_0^{\pi/3}\left(8\cos^2\theta - 2\cos\theta - 1\right)d\theta$ (simetri).",
            r"$= \Big[3\theta + 2\sin 2\theta - 2\sin\theta\Big]_0^{\pi/3} = \pi + \sqrt3 - \sqrt3 = \pi$."),
      "Gambar dulu kedua kurva. Tanpa gambar, sulit menentukan mana r luar, mana r dalam, dan sampai θ berapa.",
      [g("r = 3 cos θ (biru) dan r = 1 + cos θ (oranye)", [-0.6, 3.3], [-1.7, 1.7], [],
         [{"type": "param", "x": "3*cos(t)*cos(t)", "y": "3*cos(t)*sin(t)", "t": [0, "pi"], "color": "blue", "label": "r = 3 cos θ"},
          {"type": "param", "x": "(1 + cos(t))*cos(t)", "y": "(1 + cos(t))*sin(t)", "t": [0, "2*pi"], "color": "orange", "label": "r = 1 + cos θ"},
          {"type": "point", "x": 0.75, "y": 1.299, "color": "red"}, {"type": "point", "x": 0.75, "y": -1.299, "color": "red"}],
         [readout("Luas daerah di antara keduanya", "pi", 5)],
         "Daerah yang dicari: di dalam biru tetapi di luar oranye, di antara dua titik merah (θ = ±π/3).")]),
    S("pitfall", "Jebakan ujian",
      r"""<ul class="lesson-list">
        <li>Lupa faktor $\tfrac12$ di rumus luas kutub.</li>
        <li>Interval $\theta$ salah: $r = \cos 3\theta$ pada $[0, 2\pi]$ menelusuri tiga kelopak <b>dua kali</b>. Hitung satu kelopak lalu kalikan.</li>
        <li>Titik potong di kutub (titik asal) tidak muncul dari menyamakan $r$, karena $r = 0$ bisa terjadi pada $\theta$ berbeda.</li>
        <li>Menulis $\tfrac{dy}{dx} = \tfrac{dx/dt}{dy/dt}$ (terbalik).</li>
        <li>Luas antara dua kurva kutub ditulis $\tfrac12\int(r_1 - r_2)^2d\theta$, seharusnya $\tfrac12\int(r_1^2 - r_2^2)d\theta$.</li>
      </ul>""",
      "Untuk luas kutub, selalu tanya: 'dari θ berapa ke θ berapa kurva ini menggambar daerahnya tepat sekali?'"),
    S("checkpoint", "Mini checkpoint",
      qa(r"1. Ubah $r = 4\sin\theta$ ke Kartesius.", r"<p>$r^2 = 4r\sin\theta \Rightarrow x^2 + y^2 = 4y \Rightarrow x^2 + (y - 2)^2 = 4$, lingkaran pusat $(0, 2)$, jari-jari $2$.</p>") +
      qa(r"2. Kemiringan $x = t^2$, $y = t^3$ di $t = 1$.", r"<p>$\dfrac{3t^2}{2t} = \dfrac32$.</p>") +
      qa(r"3. Luas satu kelopak $r = \cos 2\theta$.", r"<p>$\theta \in \left[-\tfrac{\pi}{4}, \tfrac{\pi}{4}\right]$: $\ \tfrac12\displaystyle\int\cos^2 2\theta\,d\theta = \tfrac{\pi}{8}$.</p>"),
      "Soal 3: batas satu kelopak didapat dari r = 0, yaitu cos 2θ = 0 → θ = ±π/4."),
]

# ═══════════════════════════════════════════════════════════════════════════
# 10. Irisan Kerucut
# ═══════════════════════════════════════════════════════════════════════════
KERUCUT = [
    S("intuition", "Satu kerucut, tiga kurva",
      r"""<p>Potong kerucut ganda dengan bidang: miring sedikit → <b>elips</b>, sejajar garis pelukis → <b>parabola</b>, curam memotong kedua kerucut → <b>hiperbola</b>.</p>
      <p>Kurva-kurva ini ada di sekitarmu: orbit planet dan satelit (elips, hukum Kepler), parabola antena dan lampu mobil (sifat pantul),
      menara pendingin PLTU (hiperboloid), dan navigasi lewat selisih waktu sinyal (hiperbola, prinsip yang mirip dengan GPS).</p>""",
      "Ketiganya didefinisikan lewat JARAK ke titik fokus. Pahami definisi jarak itu, persamaannya mengikuti."),
    S("theorem", "Parabola",
      r"""<p><b>Definisi:</b> himpunan titik yang berjarak sama ke titik fokus $F$ dan garis direktriks.</p>
      <p>$$x^2 = 4py:\ \text{fokus } (0, p),\ \text{direktriks } y = -p; \qquad y^2 = 4px:\ \text{fokus } (p, 0),\ \text{direktriks } x = -p.$$</p>
      <p><b>Sifat pantul:</b> sinar yang datang sejajar sumbu dipantulkan tepat ke fokus. Karena itu penerima antena parabola dipasang di fokusnya.</p>""",
      "Geser titik P di grafik: dua readout jarak selalu sama. Itulah definisi parabola, bukan sekadar 'kurva kuadrat'.",
      [g("Parabola x² = 4py: jarak ke fokus = jarak ke direktriks", [-6, 6], [-3, 7],
         [param("p", "p", 0.5, 2.5, 0.1, 1, "p"), param("X", "Absis titik P", -5, 5, 0.1, 3, "x")],
         [{"type": "fn", "expr": "x*x/(4*p)", "color": "blue", "label": "x² = 4py"},
          {"type": "hline", "y": "-p", "color": "gray", "dash": True},
          {"type": "point", "x": 0, "y": "p", "color": "red"},
          {"type": "point", "x": "X", "y": "X*X/(4*p)", "color": "blue"},
          {"type": "segment", "x1": "X", "y1": "X*X/(4*p)", "x2": 0, "y2": "p", "color": "red"},
          {"type": "segment", "x1": "X", "y1": "X*X/(4*p)", "x2": "X", "y2": "-p", "color": "orange"}],
         [readout("Jarak ke fokus", "sqrt(X*X + pow(X*X/(4*p) - p, 2))", 4), readout("Jarak ke direktriks", "X*X/(4*p) + p", 4)],
         "Titik merah = fokus, garis abu-abu = direktriks.")]),
    S("theorem", "Elips & hiperbola",
      r"""<div class="table-scroll"><table class="lesson-table"><thead><tr><th></th><th>Elips</th><th>Hiperbola</th></tr></thead><tbody>
        <tr><td>Definisi</td><td>$d_1 + d_2 = 2a$</td><td>$|d_1 - d_2| = 2a$</td></tr>
        <tr><td>Persamaan baku</td><td>$\dfrac{x^2}{a^2} + \dfrac{y^2}{b^2} = 1$, $a &gt; b$</td><td>$\dfrac{x^2}{a^2} - \dfrac{y^2}{b^2} = 1$</td></tr>
        <tr><td>Fokus $(\pm c, 0)$</td><td>$c^2 = a^2 - b^2$</td><td>$c^2 = a^2 + b^2$</td></tr>
        <tr><td>Eksentrisitas $e = c/a$</td><td>$0 \le e &lt; 1$</td><td>$e &gt; 1$</td></tr>
        <tr><td>Lainnya</td><td>puncak $(\pm a, 0)$, sumbu minor $2b$</td><td>asimtot $y = \pm\tfrac{b}{a}x$</td></tr>
      </tbody></table></div>
      <p>Eksentrisitas orbit bumi sekitar $0.017$, hampir lingkaran; komet Halley sekitar $0.97$, sangat lonjong.</p>""",
      "Elips: c² = a² − b² (fokus di DALAM). Hiperbola: c² = a² + b² (fokus di LUAR puncak). Tanda ini paling sering tertukar.",
      [g("Elips: d₁ + d₂ = 2a", [-6, 6], [-4, 4],
         [param("a", "a", 3, 5, 0.1, 4, "a"), param("b", "b", 1, 2.9, 0.1, 2.5, "b"), param("s", "Posisi titik P (sudut)", 0, 6.28, 0.01, 1, "s")],
         [{"type": "param", "x": "a*cos(t)", "y": "b*sin(t)", "t": [0, "2*pi"], "color": "blue", "label": "elips"},
          {"type": "point", "x": "sqrt(a*a - b*b)", "y": 0, "color": "red"}, {"type": "point", "x": "-sqrt(a*a - b*b)", "y": 0, "color": "red"},
          {"type": "segment", "x1": "a*cos(s)", "y1": "b*sin(s)", "x2": "sqrt(a*a - b*b)", "y2": 0, "color": "orange"},
          {"type": "segment", "x1": "a*cos(s)", "y1": "b*sin(s)", "x2": "-sqrt(a*a - b*b)", "y2": 0, "color": "orange"}],
         [readout("d₁ + d₂", "hypot(a*cos(s) - sqrt(a*a - b*b), b*sin(s)) + hypot(a*cos(s) + sqrt(a*a - b*b), b*sin(s))", 4),
          readout("2a", "2*a", 4), readout("Eksentrisitas e = c/a", "sqrt(a*a - b*b)/a", 3)],
         "Ini cara tukang taman menggambar elips: dua pasak di fokus dan seutas tali sepanjang 2a.")]),
    S("derivation", "Pohon keputusan: mengenali Ax² + Cy² + Dx + Ey + F = 0",
      pohon(r"Hanya satu variabel yang berpangkat dua ($A = 0$ atau $C = 0$)? → <b>parabola</b>.",
            r"$A$ dan $C$ bertanda sama? → <b>elips</b> (jika $A = C$: lingkaran).",
            r"$A$ dan $C$ berlawanan tanda? → <b>hiperbola</b>.",
            r"Lengkapkan kuadrat untuk tiap variabel, pindahkan konstanta ke kanan, lalu bagi agar ruas kanan $= 1$ (elips/hiperbola).",
            r"Baca pusat, $a$, $b$, hitung $c$, lalu fokus, puncak, dan asimtot. Ingat pergeseran $(h, k)$.") +
      note(r"Kasus degenerasi bisa muncul: ruas kanan nol atau negatif memberi satu titik, sepasang garis, atau himpunan kosong."),
      "Saat melengkapkan kuadrat dengan koefisien, misalnya 9(x² − 4x), jangan lupa yang ditambahkan ke ruas kanan adalah 9 × 4 = 36."),
    S("example", "Bedah soal: melengkapkan kuadrat",
      r"""<p><b>Soal 1.</b> Kenali $9x^2 + 4y^2 - 36x + 8y + 4 = 0$.</p>""" +
      steps(r"$A = 9$, $C = 4$ bertanda sama → elips.",
            r"$9(x^2 - 4x) + 4(y^2 + 2y) = -4 \Rightarrow 9(x - 2)^2 - 36 + 4(y + 1)^2 - 4 = -4$.",
            r"$9(x - 2)^2 + 4(y + 1)^2 = 36 \Rightarrow \dfrac{(x - 2)^2}{4} + \dfrac{(y + 1)^2}{9} = 1$.",
            r"Pusat $(2, -1)$; penyebut terbesar $9$ di bawah $y$: sumbu mayor tegak, $a = 3$, $b = 2$, $c = \sqrt5$; fokus $(2, -1 \pm \sqrt5)$.") +
      r"""<p><b>Soal 2.</b> Kenali $x^2 - 4y^2 - 2x - 16y - 19 = 0$.</p>""" +
      steps(r"Tanda berlawanan → hiperbola. $(x - 1)^2 - 1 - 4(y + 2)^2 + 16 = 19$.",
            r"$(x - 1)^2 - 4(y + 2)^2 = 4 \Rightarrow \dfrac{(x - 1)^2}{4} - \dfrac{(y + 2)^2}{1} = 1$.",
            r"Pusat $(1, -2)$, $a = 2$, $b = 1$, $c = \sqrt5$; asimtot $y + 2 = \pm\tfrac12(x - 1)$."),
      "Untuk elips, a selalu di bawah penyebut TERBESAR, entah di x atau di y. Itulah yang menentukan arah sumbu mayor."),
    S("example", "Bedah soal: antena parabola",
      r"""<p><b>Soal.</b> Antena parabola berdiameter $3$ m dan kedalaman $0.5$ m. Di mana penerima sinyal harus dipasang?</p>""" +
      steps(r"Letakkan puncak di titik asal, membuka ke atas: $x^2 = 4py$.",
            r"Tepi antena di $(1.5,\ 0.5)$: $2.25 = 4p(0.5) \Rightarrow p = 1.125$.",
            r"Penerima dipasang di fokus, $1.125$ m di atas puncak (dasar) antena.") +
      note(r"Prinsip yang sama dipakai terbalik pada lampu sorot: sumber cahaya di fokus menghasilkan berkas sejajar."),
      "Soal terapan kerucut hampir selalu dimulai dengan memilih sistem koordinat yang membuat puncak atau pusat di titik asal."),
    S("pitfall", "Jebakan ujian",
      r"""<ul class="lesson-list">
        <li>Memakai $c^2 = a^2 - b^2$ untuk hiperbola (seharusnya $a^2 + b^2$), atau sebaliknya untuk elips.</li>
        <li>Mengira $a$ selalu di bawah $x^2$. Pada elips, $a$ di bawah penyebut terbesar.</li>
        <li>Melengkapkan kuadrat dengan koefisien: lupa mengalikan konstanta yang ditambahkan.</li>
        <li>Asimtot hiperbola tergeser: lupa memasukkan pusat $(h, k)$.</li>
        <li>Parabola $x^2 = 4py$ dengan $p &lt; 0$ membuka ke bawah, bukan ke atas.</li>
      </ul>""",
      "Setelah selesai, cek satu titik: misalnya puncak hasil hitunganmu harus memenuhi persamaan asli."),
    S("checkpoint", "Mini checkpoint",
      qa(r"1. Kenali dan tentukan pusat $4x^2 - y^2 + 8x + 6y - 9 = 0$.",
         r"<p>$4(x + 1)^2 - (y - 3)^2 = 4 \Rightarrow (x + 1)^2 - \dfrac{(y - 3)^2}{4} = 1$: hiperbola berpusat $(-1, 3)$.</p>") +
      qa(r"2. Fokus elips $\dfrac{x^2}{25} + \dfrac{y^2}{16} = 1$?", r"<p>$c^2 = 25 - 16 = 9$, jadi fokus $(\pm 3, 0)$.</p>"),
      "Soal 1 melatih tiga langkah sekaligus: kenali tanda, lengkapkan kuadrat, dan normalisasi ruas kanan."),
]

SLIDES = {
    "km-apl-volume": VOLUME,
    "km-apl-fisika": FISIKA,
    "km-pd-konsep": PD,
    "km-kut-kalkulus": KUTUB,
    "km-ker-elips": KERUCUT,
}
