r"""
Kurikulum v2 — Batch 4 (bagian A): slide Level 4, ruang & turunan multivariabel.

Topik: Geometri Ruang & Kuadrik · Fungsi Vektor & Kelengkungan · Turunan Parsial & Bidang Singgung ·
Aturan Rantai Multivariabel & Gradien · Optimasi & Pengali Lagrange.
Level 4 berjalur fakultas: satu dek dipasang ke salinan topik inti tiap fakultas (lihat akhir l4_kalkulus_lanjut.py).

Rujukan: Stewart 9e §12.1–12.6, §13.1–13.4, §14.1–14.8; Purcell Jil. 2 Bab 11–12; OpenStax Calculus Vol 3 Bab 2–4.
"""

from ..helpers import param, readout
from .l1_slides import S, g, note, qa, steps
from .l3_slides import pohon


def ruang(title, params, surfaces, readouts=None, caption=None, extent=2):
    """Grafik 3D GraphLab (kamera bisa diputar). Kurva ruang = permukaan dengan v:[0,0], nv:1."""
    spec = {"type": "3d", "title": title, "params": params, "surfaces": surfaces, "extent": extent}
    if readouts:
        spec["readouts"] = readouts
    if caption:
        spec["caption"] = caption
    return spec


def kurva3(x, y, z, t0, t1, color="red", n=120):
    """Kurva ruang r(u) = (x, y, z) untuk u dari t0 ke t1."""
    return {"u": [t0, t1], "v": [0, 0], "nu": n, "nv": 1, "x": x, "y": y, "z": z, "color": color}


# ═══════════════════════════════════════════════════════════════════════════
# 1. Geometri Ruang & Permukaan Kuadrik
# ═══════════════════════════════════════════════════════════════════════════
GEOMETRI_RUANG = [
    S("intuition", "Dari bidang ke ruang",
      r"""<p>Fungsi satu variabel menggambar <b>kurva</b>. Fungsi dua variabel $z = f(x, y)$ menggambar <b>permukaan</b>: bayangkan peta ketinggian (heightmap)
      di game, sebaran suhu pada pelat logam, atau "lanskap loss" yang dituruni algoritma machine learning.</p>
      <p>Cara membaca permukaan tanpa software 3D: lihat <b>kurva tingkat</b> $f(x, y) = k$, persis garis kontur di peta topografi.
      Kontur rapat berarti lereng curam.</p>""",
      "Putar grafik 3D dengan menyeret. Lalu ubah b menjadi negatif: mangkuk berubah menjadi pelana.",
      [ruang("Permukaan z = a·x² + b·y²", [param("a", "a", -1, 1, 0.1, 0.5, "a"), param("b", "b", -1, 1, 0.1, 0.5, "b")],
             [{"u": [-1.6, 1.6], "v": [-1.6, 1.6], "x": "u", "y": "v", "z": "a*u*u + b*v*v", "color": "blue"}],
             [readout("Jenis (tanda a·b): + mangkuk, − pelana", "a*b", 3)],
             "a dan b bertanda sama: paraboloid eliptik. Berbeda tanda: paraboloid hiperbolik (pelana).")]),
    S("theorem", "Alat dasar di ℝ³",
      r"""<ul class="lesson-list">
        <li>Jarak: $|P_1P_2| = \sqrt{(x_2 - x_1)^2 + (y_2 - y_1)^2 + (z_2 - z_1)^2}$; bola: $(x - h)^2 + (y - k)^2 + (z - l)^2 = r^2$.</li>
        <li>Hasil kali titik $\mathbf{a}\cdot\mathbf{b} = |\mathbf{a}||\mathbf{b}|\cos\theta$ (sudut, proyeksi); hasil kali silang $\mathbf{a}\times\mathbf{b}$ tegak lurus keduanya, panjangnya = luas jajargenjang.</li>
        <li>Garis: $\mathbf{r}(t) = \mathbf{r}_0 + t\mathbf{v}$. Bidang dengan normal $\mathbf{n} = \langle a, b, c\rangle$ melalui $(x_0, y_0, z_0)$: $a(x - x_0) + b(y - y_0) + c(z - z_0) = 0$.</li>
        <li>Di ℝ³, persamaan dengan variabel yang hilang adalah <b>silinder</b>: $x^2 + y^2 = 1$ adalah tabung tak hingga sepanjang sumbu $z$, bukan lingkaran.</li>
      </ul>""",
      "Normal bidang dibaca langsung dari koefisien x, y, z. Bidang 2x − y + 3z = 6 punya normal ⟨2, −1, 3⟩."),
    S("theorem", "Fungsi dua variabel & permukaan kuadrik",
      r"""<p>$f: D \subseteq \mathbb{R}^2 \to \mathbb{R}$; domain ditentukan akar, logaritma, dan penyebut. Kurva tingkat $f(x, y) = k$; untuk $F(x, y, z)$ ada <b>permukaan tingkat</b> $F = k$.</p>
      <div class="table-scroll"><table class="lesson-table"><thead><tr><th>Persamaan</th><th>Permukaan</th><th>Penampang khas</th></tr></thead><tbody>
        <tr><td>$\dfrac{x^2}{a^2} + \dfrac{y^2}{b^2} + \dfrac{z^2}{c^2} = 1$</td><td>elipsoid</td><td>semua elips</td></tr>
        <tr><td>$z = \dfrac{x^2}{a^2} + \dfrac{y^2}{b^2}$</td><td>paraboloid eliptik</td><td>elips (mendatar), parabola (tegak)</td></tr>
        <tr><td>$z = \dfrac{y^2}{b^2} - \dfrac{x^2}{a^2}$</td><td>paraboloid hiperbolik (pelana)</td><td>hiperbola, parabola</td></tr>
        <tr><td>$\dfrac{z^2}{c^2} = \dfrac{x^2}{a^2} + \dfrac{y^2}{b^2}$</td><td>kerucut</td><td>elips, sepasang garis</td></tr>
        <tr><td>$\dfrac{x^2}{a^2} + \dfrac{y^2}{b^2} - \dfrac{z^2}{c^2} = 1$</td><td>hiperboloid satu lembar</td><td>elips, hiperbola</td></tr>
        <tr><td>$-\dfrac{x^2}{a^2} - \dfrac{y^2}{b^2} + \dfrac{z^2}{c^2} = 1$</td><td>hiperboloid dua lembar</td><td>elips (bila ada), hiperbola</td></tr>
      </tbody></table></div>""",
      "Metode penampang (trace): potong dengan bidang x = k, y = k, z = k. Tiga kurva 2D yang kamu kenal menyusun gambaran 3D.",
      [ruang("x² + y² − z² = k: hiperboloid dan kerucut", [param("k", "k", -1, 1, 0.05, 0.5, "k")],
             [{"u": [0, "2*pi"], "v": [-1.6, 1.6], "x": "sqrt(max(k + v*v, 0))*cos(u)", "y": "sqrt(max(k + v*v, 0))*sin(u)", "z": "v", "color": "teal"}],
             [readout("k", "k", 2)],
             "k > 0: hiperboloid satu lembar (menara pendingin). k = 0: kerucut. k < 0: dua lembar terpisah.")]),
    S("derivation", "Pohon keputusan: mengenali kuadrik",
      pohon(r"Ada variabel yang hanya berpangkat <b>satu</b>? → <b>paraboloid</b>, membuka ke arah variabel itu. Kuadrat lainnya bertanda sama → eliptik; berlawanan → hiperbolik (pelana).",
            r"Semua berpangkat dua dan ruas kanan $0$ (setelah dirapikan)? → <b>kerucut</b>.",
            r"Semua berpangkat dua, ruas kanan $1$: hitung banyak tanda minus. Nol → <b>elipsoid</b>; satu → <b>hiperboloid satu lembar</b>; dua → <b>hiperboloid dua lembar</b>.",
            r"Ada suku linear seperti $-6x$? Lengkapkan kuadrat dulu untuk menemukan pusat atau puncak.",
            r"Konfirmasi dengan dua atau tiga penampang.") +
      note(r"Sumbu simetri hiperboloid adalah variabel yang tandanya <b>berbeda</b> dari dua lainnya. Untuk satu lembar, itu variabel bertanda minus; untuk dua lembar, variabel bertanda plus."),
      "Jumlah tanda minus menentukan jumlah 'lembar' secara terbalik: satu minus = satu lembar, dua minus = dua lembar."),
    S("example", "Bedah soal: identifikasi kuadrik",
      r"""<p><b>Soal 1.</b> $4x^2 - y^2 + 2z^2 + 4 = 0$.</p>""" +
      steps(r"Bagi dengan $-4$: $-x^2 + \dfrac{y^2}{4} - \dfrac{z^2}{2} = 1$.",
            r"Semua kuadrat, ruas kanan $1$, dua tanda minus → hiperboloid dua lembar, sumbunya sumbu $y$.",
            r"Penampang $y = k$: $x^2 + \tfrac{z^2}{2} = \tfrac{k^2}{4} - 1$, elips untuk $|k| &gt; 2$ dan kosong untuk $|k| &lt; 2$. Itulah celah di antara dua lembar.") +
      r"""<p><b>Soal 2.</b> $x^2 + 2z^2 - 6x - y + 10 = 0$.</p>""" +
      steps(r"$y$ berpangkat satu → paraboloid yang membuka ke arah $y$.",
            r"Lengkapkan kuadrat: $(x - 3)^2 - 9 + 2z^2 - y + 10 = 0 \Rightarrow y - 1 = (x - 3)^2 + 2z^2$.",
            r"Kuadrat bertanda sama → paraboloid eliptik dengan puncak $(3, 1, 0)$, membuka ke $y$ positif."),
      "Soal 1 adalah contoh mengapa langkah 'bagi agar ruas kanan = 1' penting. Tanda-tandanya baru jelas setelah itu."),
    S("pitfall", "Jebakan ujian",
      r"""<ul class="lesson-list">
        <li>$x^2 + y^2 = 1$ di ℝ³ adalah tabung, bukan lingkaran.</li>
        <li>Tertukar $z = x^2 + y^2$ (paraboloid) dengan $z^2 = x^2 + y^2$ (kerucut).</li>
        <li>Tertukar hiperboloid satu dan dua lembar karena tidak menormalkan ruas kanan.</li>
        <li>Kurva tingkat (di bidang $xy$, nilai $f$ tetap) dicampur dengan penampang tegak.</li>
        <li>Domain $f(x, y) = \ln(x + y)$ ditulis $x &gt; 0, y &gt; 0$, padahal syaratnya $x + y &gt; 0$.</li>
      </ul>""",
      "Domain fungsi dua variabel adalah DAERAH di bidang. Gambar daerahnya, jangan berhenti di ketaksamaan."),
    S("checkpoint", "Mini checkpoint",
      qa(r"1. Domain dan daerah hasil $f(x, y) = \sqrt{9 - x^2 - y^2}$.", r"<p>Domain cakram $x^2 + y^2 \le 9$; daerah hasil $[0, 3]$. Grafiknya setengah bola atas.</p>") +
      qa(r"2. Kenali $z^2 = 4x^2 + y^2$.", r"<p>Ruas kanan nol setelah dipindah ($4x^2 + y^2 - z^2 = 0$): kerucut eliptik bersumbu $z$.</p>") +
      qa(r"3. Kenali $x^2 + y^2 - z^2 = 1$.", r"<p>Satu tanda minus: hiperboloid satu lembar bersumbu $z$.</p>"),
      "Soal 2 dan 3 hanya berbeda di ruas kanan, tapi permukaannya sangat berbeda. Selalu cek ruas kanan."),
]

# ═══════════════════════════════════════════════════════════════════════════
# 2. Fungsi Vektor & Kelengkungan (topik baru)
# ═══════════════════════════════════════════════════════════════════════════
FUNGSI_VEKTOR = [
    S("intuition", "Lintasan benda di ruang",
      r"""<p>Posisi drone, satelit, atau ujung lengan robot setiap saat adalah <b>fungsi vektor</b> $\mathbf{r}(t) = \langle x(t), y(t), z(t)\rangle$.
      Turunannya kecepatan (arah singgung), turunan keduanya percepatan. Desain rel roller coaster, jalur kamera di animasi, dan
      perencanaan gerak robot semuanya mengatur <b>seberapa tajam</b> lintasan berbelok: kelengkungan.</p>""",
      "Putar heliks di grafik. Jari-jari kecil berarti belokan tajam (kelengkungan besar); jari-jari besar berarti landai.",
      [ruang("Heliks r(t) = ⟨R cos t, R sin t, c·t⟩", [param("R", "Jari-jari R", 0.3, 1.8, 0.05, 1, "R"), param("c", "Kenaikan c", 0.05, 0.15, 0.01, 0.12, "c")],
             [kurva3("R*cos(u)", "R*sin(u)", "c*u - 0.75", 0, "4*pi", "red", 160)],
             [readout("Laju |r′| = √(R² + c²)", "sqrt(R*R + c*c)", 4), readout("Kelengkungan κ = R/(R² + c²)", "R/(R*R + c*c)", 4)],
             "Saat c → 0, heliks menjadi lingkaran dan κ → 1/R.")]),
    S("theorem", "Turunan & integral fungsi vektor",
      r"""<p>Semuanya dihitung <b>per komponen</b>: $\mathbf{r}'(t) = \langle x'(t), y'(t), z'(t)\rangle$, $\ \int\mathbf{r}\,dt = \left\langle\int x, \int y, \int z\right\rangle$.</p>
      <ul class="lesson-list">
        <li>$\mathbf{r}'(t)$ adalah vektor singgung; $\mathbf{T}(t) = \dfrac{\mathbf{r}'(t)}{|\mathbf{r}'(t)|}$ vektor singgung satuan.</li>
        <li>Aturan: $(\mathbf{u}\cdot\mathbf{v})' = \mathbf{u}'\cdot\mathbf{v} + \mathbf{u}\cdot\mathbf{v}'$, $\ (\mathbf{u}\times\mathbf{v})' = \mathbf{u}'\times\mathbf{v} + \mathbf{u}\times\mathbf{v}'$ (urutan silang dijaga).</li>
        <li>Jika $|\mathbf{r}(t)|$ konstan, maka $\mathbf{r}\cdot\mathbf{r}' = 0$: kecepatan tegak lurus posisi (gerak melingkar).</li>
        <li><b>Panjang busur:</b> $L = \displaystyle\int_a^b|\mathbf{r}'(t)|\,dt$; fungsi panjang busur $s(t) = \int_a^t|\mathbf{r}'(\tau)|\,d\tau$.</li>
      </ul>""",
      "Fakta 'panjang konstan → tegak lurus' muncul lagi di kelengkungan: T punya panjang 1, jadi T′ tegak lurus T."),
    S("theorem", "Kelengkungan",
      r"""<p>Kelengkungan mengukur seberapa cepat <b>arah</b> berubah per satuan <b>jarak</b> (bukan per waktu):
      $$\kappa = \left|\frac{d\mathbf{T}}{ds}\right| = \frac{|\mathbf{T}'(t)|}{|\mathbf{r}'(t)|} = \frac{|\mathbf{r}'(t)\times\mathbf{r}''(t)|}{|\mathbf{r}'(t)|^3}.$$</p>
      <p>Untuk grafik $y = f(x)$: $\ \kappa = \dfrac{|f''(x)|}{\left(1 + [f'(x)]^2\right)^{3/2}}$. Lingkaran berjari-jari $R$ punya $\kappa = \tfrac1R$ di mana-mana;
      <b>lingkaran oskulasi</b> adalah lingkaran yang paling pas menempel kurva, berjari-jari $\tfrac{1}{\kappa}$.</p>""" +
      note(r"Jalan tol dan rel kereta tidak langsung menyambung garis lurus ke busur lingkaran, karena $\kappa$ akan melompat dari $0$ ke $\tfrac1R$ dan penumpang merasakan sentakan. Insinyur menyisipkan kurva transisi (klotoid) yang kelengkungannya naik bertahap."),
      "Mengapa dibagi |r′|? Agar κ tidak bergantung pada seberapa cepat kamu menelusuri kurva, hanya pada bentuknya.",
      [g("Lingkaran oskulasi y = x²", [-3, 3], [-0.5, 4.5], [param("a", "Titik a", -1.5, 1.5, 0.01, 0.5, "a")],
         [{"type": "fn", "expr": "x*x", "color": "blue", "label": "y = x²"},
          {"type": "param", "x": "-4*a*a*a + 0.5*pow(1 + 4*a*a, 1.5)*cos(t)", "y": "a*a + (1 + 4*a*a)/2 + 0.5*pow(1 + 4*a*a, 1.5)*sin(t)",
           "t": [0, "2*pi"], "color": "orange", "label": "lingkaran oskulasi"},
          {"type": "point", "x": "a", "y": "a*a", "color": "red"}],
         [readout("κ = 2/(1 + 4a²)^(3/2)", "2/pow(1 + 4*a*a, 1.5)", 4), readout("Jari-jari 1/κ", "pow(1 + 4*a*a, 1.5)/2", 4)],
         "Di puncak (a = 0) belokan paling tajam: κ = 2, jari-jari 1/2.")]),
    S("theorem", "Kecepatan, percepatan, dan komponennya",
      r"""<p>$\mathbf{v} = \mathbf{r}'$, laju $v = |\mathbf{r}'|$, $\mathbf{a} = \mathbf{r}''$. Percepatan selalu terurai menjadi dua komponen:
      $$\mathbf{a} = \underbrace{v'}_{a_T}\,\mathbf{T} + \underbrace{\kappa v^2}_{a_N}\,\mathbf{N}, \qquad a_T = \frac{\mathbf{r}'\cdot\mathbf{r}''}{|\mathbf{r}'|}, \quad a_N = \frac{|\mathbf{r}'\times\mathbf{r}''|}{|\mathbf{r}'|}.$$</p>
      <p>$a_T$ mengubah <b>laju</b> (gas/rem), $a_N$ mengubah <b>arah</b> (belok). Di gerak melingkar beraturan $a_T = 0$ dan $a_N = \tfrac{v^2}{R}$: percepatan sentripetal dari fisika SMA.</p>""",
      "Saat mobil berbelok dengan laju dua kali lipat, gaya ke samping naik EMPAT kali (v²). Itu sebabnya ada batas kecepatan di tikungan."),
    S("example", "Bedah soal: heliks",
      r"""<p><b>Soal.</b> $\mathbf{r}(t) = \langle\cos t, \sin t, t\rangle$. Hitung panjang satu putaran dan kelengkungannya.</p>""" +
      steps(r"$\mathbf{r}' = \langle -\sin t, \cos t, 1\rangle$, $\ |\mathbf{r}'| = \sqrt{\sin^2 t + \cos^2 t + 1} = \sqrt2$.",
            r"Panjang $0 \le t \le 2\pi$: $L = \displaystyle\int_0^{2\pi}\sqrt2\,dt = 2\sqrt2\,\pi$.",
            r"$\mathbf{r}'' = \langle -\cos t, -\sin t, 0\rangle$; $\ \mathbf{r}'\times\mathbf{r}'' = \langle \sin t, -\cos t, 1\rangle$, panjangnya $\sqrt2$.",
            r"$\kappa = \dfrac{\sqrt2}{(\sqrt2)^3} = \dfrac12$, konstan di sepanjang heliks.") +
      note(r"Cocok dengan rumus grafik sebelumnya: $\kappa = \tfrac{R}{R^2 + c^2}$ dengan $R = c = 1$."),
      "Heliks punya kelengkungan konstan, sama seperti lingkaran. Itulah alasan pegas dan tangga putar bentuknya heliks."),
    S("example", "Bedah soal: komponen percepatan",
      r"""<p><b>Soal.</b> Partikel bergerak dengan $\mathbf{r}(t) = \langle t, t^2, t^3\rangle$. Pada $t = 1$, apakah partikel sedang dipercepat? Seberapa tajam belokannya?</p>""" +
      steps(r"$\mathbf{r}'(1) = \langle 1, 2, 3\rangle$, $|\mathbf{r}'| = \sqrt{14}$; $\ \mathbf{r}''(1) = \langle 0, 2, 6\rangle$.",
            r"$a_T = \dfrac{\mathbf{r}'\cdot\mathbf{r}''}{|\mathbf{r}'|} = \dfrac{0 + 4 + 18}{\sqrt{14}} = \dfrac{22}{\sqrt{14}} &gt; 0$: laju sedang <b>bertambah</b>.",
            r"$\mathbf{r}'\times\mathbf{r}'' = \langle 12 - 6,\ 0 - 6,\ 2 - 0\rangle = \langle 6, -6, 2\rangle$, panjangnya $\sqrt{76} = 2\sqrt{19}$.",
            r"$a_N = \dfrac{2\sqrt{19}}{\sqrt{14}}$ dan $\kappa = \dfrac{2\sqrt{19}}{14\sqrt{14}} \approx 0.166$."),
      "Hasil kali silang dihitung dengan determinan 3×3. Tulis baris i, j, k dulu agar komponen tengah tidak salah tanda."),
    S("pitfall", "Jebakan ujian",
      r"""<ul class="lesson-list">
        <li>Panjang busur tanpa nilai mutlak: $\int\mathbf{r}'\,dt$ adalah perpindahan (vektor), bukan panjang.</li>
        <li>Kelengkungan $|\mathbf{T}'(t)|$ tanpa dibagi $|\mathbf{r}'(t)|$.</li>
        <li>Pangkat penyebut rumus silang: $|\mathbf{r}'|^3$, bukan $|\mathbf{r}'|^2$.</li>
        <li>$(\mathbf{u}\times\mathbf{v})' = \mathbf{v}'\times\mathbf{u} + \dots$: urutan hasil kali silang tertukar, tanda berubah.</li>
        <li>Lupa normalisasi saat diminta vektor <b>satuan</b> $\mathbf{T}$ atau $\mathbf{N}$.</li>
      </ul>""",
      "Uji cepat rumus kelengkungan: masukkan lingkaran r = ⟨R cos t, R sin t⟩. Kalau hasilnya bukan 1/R, ada yang salah."),
    S("checkpoint", "Mini checkpoint",
      qa(r"1. Kelengkungan $\mathbf{r}(t) = \langle 2\cos t, 2\sin t\rangle$.", r"<p>Lingkaran berjari-jari $2$: $\kappa = \tfrac12$.</p>") +
      qa(r"2. Kelengkungan $y = x^2$ di titik asal.", r"<p>$\dfrac{|2|}{(1 + 0)^{3/2}} = 2$.</p>") +
      qa(r"3. Vektor singgung satuan $\langle t, t^2, t^3\rangle$ di $t = 1$.", r"<p>$\mathbf{T} = \dfrac{\langle 1, 2, 3\rangle}{\sqrt{14}}$.</p>"),
      "Soal 1 bisa dijawab tanpa hitungan: kelengkungan lingkaran selalu 1/R."),
]

# ═══════════════════════════════════════════════════════════════════════════
# 3. Turunan Parsial & Bidang Singgung
# ═══════════════════════════════════════════════════════════════════════════
TURUNAN_PARSIAL = [
    S("intuition", "Kemiringan ke arah timur dan ke arah utara",
      r"""<p>Berdiri di lereng gunung $z = f(x, y)$. Berjalan ke timur (hanya $x$ berubah) memberi satu kemiringan; ke utara (hanya $y$) memberi kemiringan lain.
      Masing-masing adalah <b>turunan parsial</b>: iris permukaan dengan bidang $y = b$, lalu ambil turunan biasa dari kurva irisan itu.</p>
      <p>Contoh nyata: sensitivitas biaya produksi terhadap satu bahan baku saat bahan lain tetap, atau seberapa besar loss berubah bila hanya satu bobot jaringan saraf digeser.</p>""",
      "Geser a dan b. Kurva merah adalah irisan y = b; garis oranye adalah singgungnya, kemiringannya f_x(a, b).",
      [ruang("Irisan z = f(x, b) dan singgungnya", [param("a", "a", -1.2, 1.2, 0.05, 0.6, "a"), param("b", "b", -1, 1, 0.05, 0.4, "b")],
             [{"u": [-1.5, 1.5], "v": [-1.5, 1.5], "x": "u", "y": "v", "z": "(4 - u*u - 2*v*v)/2 - 1", "color": "blue"},
              kurva3("u", "b", "(4 - u*u - 2*b*b)/2 - 1", -1.5, 1.5, "red", 60),
              kurva3("a + u", "b", "(4 - a*a - 2*b*b)/2 - 1 - a*u", -0.7, 0.7, "orange", 10)],
             [readout("f_x(a, b) = −a", "-a", 3), readout("f_y(a, b) = −2b", "-2*b", 3)],
             "f(x, y) = (4 − x² − 2y²)/2 − 1: arah y dua kali lebih curam daripada arah x.")]),
    S("theorem", "Sebelum turunan: limit & kekontinuan",
      r"""<p>$\displaystyle\lim_{(x, y) \to (a, b)}f(x, y) = L$ jika $f$ mendekati $L$ dari <b>semua</b> arah, bukan hanya kiri dan kanan.</p>""" +
      pohon(r"Substitusi langsung bisa (fungsi kontinu)? Selesai.",
            r"Bentuk $\tfrac00$? Coba beberapa <b>jalur</b>: $y = 0$, $x = 0$, $y = mx$, $y = x^2$. Dua jalur berbeda nilai → limit <b>tidak ada</b>.",
            r"Semua jalur sama? Itu belum bukti. Buktikan dengan koordinat kutub ($|f - L| \le g(r) \to 0$ tanpa bergantung $\theta$) atau teorema apit.") +
      r"""<p><b>Contoh.</b> $f = \dfrac{xy}{x^2 + y^2}$ sepanjang $y = mx$ bernilai $\dfrac{m}{1 + m^2}$, bergantung $m$, jadi limit di $(0, 0)$ tidak ada.
      Sebaliknya $\dfrac{x^2y}{x^2 + y^2}$: dalam kutub $|f| = r|\cos^2\theta\sin\theta| \le r \to 0$, limitnya $0$.</p>""",
      "Satu jalur yang berbeda sudah cukup untuk membuktikan TIDAK ada. Untuk membuktikan ADA, kamu butuh argumen untuk semua arah sekaligus.",
      [g("Nilai xy/(x² + y²) sepanjang y = mx", [-0.5, 3], [-0.8, 0.8], [param("m", "Kemiringan jalur m", -3, 3, 0.05, 1, "m")],
         [{"type": "fn", "expr": "m/(1 + m*m) + 0*x", "color": "blue", "label": "nilai di sepanjang jalur"}],
         [readout("Limit sepanjang y = mx", "m/(1 + m*m)", 4)],
         "Nilai berubah bila m berubah, jadi tidak ada satu limit untuk semua arah.")]),
    S("theorem", "Definisi & aturan menghitung",
      r"""<p>$$f_x(a, b) = \lim_{h \to 0}\frac{f(a + h, b) - f(a, b)}{h}, \qquad f_y(a, b) = \lim_{h \to 0}\frac{f(a, b + h) - f(a, b)}{h}.$$</p>
      <p>Cara menghitung: turunkan terhadap satu variabel, perlakukan variabel lain sebagai <b>konstanta</b>. Notasi: $f_x = \dfrac{\partial f}{\partial x} = \partial_x f$.</p>
      <p><b>Orde dua:</b> $f_{xx}$, $f_{yy}$, $f_{xy} = (f_x)_y$. <b>Teorema Clairaut:</b> jika $f_{xy}$ dan $f_{yx}$ kontinu, maka $f_{xy} = f_{yx}$.</p>
      <p><b>Turunan implisit:</b> untuk $F(x, y, z) = 0$, $\ \dfrac{\partial z}{\partial x} = -\dfrac{F_x}{F_z}$ dan $\dfrac{\partial z}{\partial y} = -\dfrac{F_y}{F_z}$.</p>""",
      "Saat menghitung f_x, coret mental semua y menjadi angka, misalnya 5. Lalu turunkan seperti Kalkulus 1."),
    S("example", "Bedah soal: turunan parsial & implisit",
      r"""<p><b>Soal 1.</b> $f(x, y) = x^3 + x^2y^3 - 2y^2$. Hitung $f_x(2, 1)$, $f_y(2, 1)$, dan cek Clairaut.</p>""" +
      steps(r"$f_x = 3x^2 + 2xy^3$, sehingga $f_x(2, 1) = 12 + 4 = 16$.",
            r"$f_y = 3x^2y^2 - 4y$, sehingga $f_y(2, 1) = 12 - 4 = 8$.",
            r"$f_{xy} = (3x^2 + 2xy^3)_y = 6xy^2$ dan $f_{yx} = (3x^2y^2 - 4y)_x = 6xy^2$. Sama, sesuai Clairaut.") +
      r"""<p><b>Soal 2.</b> $x^3 + y^3 + z^3 + 6xyz = 1$. Cari $\dfrac{\partial z}{\partial x}$.</p>""" +
      steps(r"$F = x^3 + y^3 + z^3 + 6xyz - 1$: $F_x = 3x^2 + 6yz$, $F_z = 3z^2 + 6xy$.",
            r"$\dfrac{\partial z}{\partial x} = -\dfrac{3x^2 + 6yz}{3z^2 + 6xy} = -\dfrac{x^2 + 2yz}{z^2 + 2xy}$."),
      "Clairaut adalah cek gratis: kalau f_xy ≠ f_yx untuk fungsi polinom, pasti ada salah hitung."),
    S("theorem", "Bidang singgung, linearisasi, diferensial total",
      r"""<p>Bidang singgung pada $z = f(x, y)$ di $(a, b, f(a, b))$:
      $$z - f(a, b) = f_x(a, b)(x - a) + f_y(a, b)(y - b).$$</p>
      <p><b>Linearisasi</b> $L(x, y)$ adalah ruas kanan ditambah $f(a, b)$; untuk titik dekat $(a, b)$, $f \approx L$.
      <b>Diferensial total:</b> $dz = f_x\,dx + f_y\,dy$ menaksir perubahan kecil $\Delta z$.</p>
      <p><b>Terdiferensialkan</b> berarti bidang singgung benar-benar menempel; cukup bila $f_x$ dan $f_y$ ada dan kontinu di sekitar titik.
      Hati-hati: $\tfrac{xy}{x^2 + y^2}$ (dengan $f(0, 0) = 0$) punya $f_x(0, 0) = f_y(0, 0) = 0$, tetapi tidak kontinu, apalagi terdiferensialkan.</p>""",
      "Bidang singgung = versi 3D dari garis singgung. Dua kemiringan parsial cukup untuk menentukan satu bidang."),
    S("example", "Bedah soal: bidang singgung & analisis galat (FT)",
      r"""<p><b>Soal 1.</b> Bidang singgung $z = 2x^2 + y^2$ di $(1, 1, 3)$.</p>""" +
      steps(r"$f_x = 4x = 4$, $f_y = 2y = 2$ di $(1, 1)$.",
            r"$z - 3 = 4(x - 1) + 2(y - 1)$, atau $z = 4x + 2y - 3$.") +
      r"""<p><b>Soal 2.</b> Silinder diukur $r = 10 \pm 0.1$ cm dan $h = 25 \pm 0.1$ cm. Taksir galat maksimum volumenya.</p>""" +
      steps(r"$V = \pi r^2h$, sehingga $dV = 2\pi rh\,dr + \pi r^2\,dh$.",
            r"$dV = 2\pi(10)(25)(0.1) + \pi(100)(0.1) = 50\pi + 10\pi = 60\pi \approx 188$ cm³.",
            r"Galat relatif: $\dfrac{dV}{V} = 2\dfrac{dr}{r} + \dfrac{dh}{h} = 0.02 + 0.004 = 2.4\%$.") +
      note(r"Perhatikan faktor $2$ pada $\tfrac{dr}{r}$: galat jari-jari dihitung dua kali karena $r$ dikuadratkan. Ini dasar menentukan toleransi alat ukur."),
      "Untuk galat maksimum, semua suku diambil positif (galat terburuk menumpuk ke arah yang sama)."),
    S("pitfall", "Jebakan ujian",
      r"""<ul class="lesson-list">
        <li>Menganggap limit ada karena dua jalur memberi nilai sama.</li>
        <li>Menurunkan $y$ juga saat menghitung $f_x$ (misal $(x^2y^3)_x = 2xy^3 + 3x^2y^2$). Salah, $y$ itu konstanta.</li>
        <li>Lupa tanda minus di $\tfrac{\partial z}{\partial x} = -\tfrac{F_x}{F_z}$.</li>
        <li>Menyimpulkan terdiferensialkan hanya karena $f_x$ dan $f_y$ ada.</li>
        <li>Bidang singgung ditulis dengan $f_x(x, y)$ alih-alih nilainya di titik $(a, b)$.</li>
      </ul>""",
      "Persamaan bidang singgung harus linear dalam x dan y. Kalau masih ada x² di jawabanmu, kamu lupa mengevaluasi turunan di titiknya."),
    S("checkpoint", "Mini checkpoint",
      qa(r"1. $f = e^{xy}\sin y$. Hitung $f_x$.", r"<p>$f_x = ye^{xy}\sin y$ ($\sin y$ konstanta terhadap $x$).</p>") +
      qa(r"2. Apakah $\displaystyle\lim_{(x, y) \to (0, 0)}\frac{x^2 - y^2}{x^2 + y^2}$ ada?", r"<p>Jalur $y = 0$ memberi $1$, jalur $x = 0$ memberi $-1$. Tidak ada.</p>") +
      qa(r"3. Linearisasi $f = \sqrt{x^2 + y^2}$ di $(3, 4)$, lalu taksir $f(3.1, 3.9)$.",
         r"<p>$f = 5$, $f_x = \tfrac35$, $f_y = \tfrac45$: $L = 5 + 0.6(0.1) + 0.8(-0.1) = 4.98$. Nilai sebenarnya $\approx 4.9819$.</p>"),
      "Soal 3 adalah cara insinyur menghitung cepat tanpa kalkulator: linearisasi di titik yang 'cantik'."),
]

# ═══════════════════════════════════════════════════════════════════════════
# 4. Aturan Rantai Multivariabel & Gradien
# ═══════════════════════════════════════════════════════════════════════════
GRADIEN = [
    S("intuition", "Arah paling curam",
      r"""<p>Di lereng gunung yang berkabut, kamu ingin naik secepat mungkin. Ke mana melangkah? Jawabannya satu vektor:
      <b>gradien</b> $\nabla f = \langle f_x, f_y\rangle$. Ia menunjuk ke arah kenaikan tercuram, panjangnya adalah kecuraman itu, dan selalu
      <b>tegak lurus garis kontur</b>.</p>
      <p>Panas mengalir ke arah $-\nabla T$, air mengalir menuruni $-\nabla h$, dan gradient descent di machine learning melangkah ke $-\nabla L$.</p>""",
      "Geser titik. Panah biru (gradien) selalu memotong elips kontur secara tegak lurus.",
      [g("Kontur f = x² + 2y² dan gradiennya", [-3.2, 3.2], [-2.4, 2.4], [param("a", "x titik", -2.5, 2.5, 0.05, 1.5, "a"), param("b", "y titik", -1.6, 1.6, 0.05, 0.8, "b")],
         [{"type": "param", "x": f"sqrt({k})*cos(t)", "y": f"sqrt({k}/2)*sin(t)", "t": [0, "2*pi"], "color": "gray"} for k in (1, 2, 4, 6, 8)] +
         [{"type": "point", "x": "a", "y": "b", "color": "red"},
          {"type": "segment", "x1": "a", "y1": "b", "x2": "a + 0.25*2*a", "y2": "b + 0.25*4*b", "color": "blue", "arrow": True, "width": 3}],
         [readout("∇f = (2x, 4y): komponen x", "2*a", 3), readout("komponen y", "4*b", 3), readout("|∇f| = laju naik maksimum", "sqrt(4*a*a + 16*b*b)", 4)],
         "Kontur lebih rapat di arah y: gradien di sana lebih besar.")]),
    S("theorem", "Aturan rantai multivariabel",
      r"""<p>Jika $z = f(x, y)$ dengan $x = x(t)$, $y = y(t)$:
      $$\frac{dz}{dt} = \frac{\partial f}{\partial x}\frac{dx}{dt} + \frac{\partial f}{\partial y}\frac{dy}{dt}.$$
      Jika $x = x(s, t)$, $y = y(s, t)$: $\ \dfrac{\partial z}{\partial s} = f_x\,x_s + f_y\,y_s$, dan serupa untuk $t$.</p>
      <p><b>Diagram pohon:</b> gambar $z$ di atas, cabang ke $x$ dan $y$, lalu ke $s$ dan $t$. Turunan = jumlah dari semua jalur dari $z$ ke variabel tujuan,
      dengan mengalikan turunan di sepanjang setiap jalur.</p>
      <p>Dalam notasi vektor: $\dfrac{dz}{dt} = \nabla f\cdot\mathbf{r}'(t)$. Inilah aturan rantai yang dipakai <i>backpropagation</i>.</p>""",
      "Hitung jalur di diagram pohon. Jumlah suku di jawabanmu = jumlah jalur dari z ke variabel itu."),
    S("example", "Bedah soal: aturan rantai",
      r"""<p><b>Soal 1.</b> $z = x^2y + 3xy^4$, $x = \sin 2t$, $y = \cos t$. Hitung $\dfrac{dz}{dt}$ di $t = 0$.</p>""" +
      steps(r"Di $t = 0$: $x = 0$, $y = 1$, $x' = 2\cos 2t = 2$, $y' = -\sin t = 0$.",
            r"$z_x = 2xy + 3y^4 = 3$; $\ z_y = x^2 + 12xy^3 = 0$.",
            r"$\dfrac{dz}{dt} = 3(2) + 0(0) = 6$.") +
      r"""<p><b>Soal 2.</b> $z = e^x\sin y$, $x = st^2$, $y = s^2t$. Cari $\dfrac{\partial z}{\partial s}$.</p>""" +
      steps(r"Jalur $z \to x \to s$: $e^x\sin y\cdot t^2$. Jalur $z \to y \to s$: $e^x\cos y\cdot 2st$.",
            r"$\dfrac{\partial z}{\partial s} = t^2e^{st^2}\sin(s^2t) + 2st\,e^{st^2}\cos(s^2t)$."),
      "Masukkan angka sedini mungkin (seperti Soal 1) bila yang ditanya hanya nilai di satu titik. Jauh lebih ringkas."),
    S("theorem", "Turunan berarah & gradien",
      r"""<p>Laju perubahan $f$ di $(a, b)$ ke arah vektor <b>satuan</b> $\mathbf{u}$:
      $$D_{\mathbf{u}}f = \nabla f\cdot\mathbf{u} = |\nabla f|\cos\theta.$$</p>
      <ul class="lesson-list">
        <li>Maksimum saat $\mathbf{u}$ searah $\nabla f$: nilai maksimumnya $|\nabla f|$. Minimum (turun tercepat) ke arah $-\nabla f$.</li>
        <li>$D_{\mathbf{u}}f = 0$ saat $\mathbf{u} \perp \nabla f$, yaitu menyusuri kontur. Jadi $\nabla f$ tegak lurus kurva tingkat.</li>
        <li>Di ℝ³, $\nabla F$ tegak lurus permukaan tingkat $F = k$. Bidang singgungnya: $\nabla F(P)\cdot\langle x - x_0, y - y_0, z - z_0\rangle = 0$.</li>
      </ul>""",
      "Kata kunci 'arah' dalam soal berarti vektor satuan. Normalkan dulu sebelum dikalikan titik dengan gradien."),
    S("example", "Bedah soal: turunan berarah & bidang singgung",
      r"""<p><b>Soal 1.</b> $f = x^2y^3 - 4y$ di $(2, -1)$ ke arah $\mathbf{v} = \langle 2, 5\rangle$.</p>""" +
      steps(r"$\nabla f = \langle 2xy^3,\ 3x^2y^2 - 4\rangle = \langle -4, 8\rangle$ di $(2, -1)$.",
            r"$\mathbf{u} = \tfrac{1}{\sqrt{29}}\langle 2, 5\rangle$.",
            r"$D_{\mathbf{u}}f = \dfrac{-8 + 40}{\sqrt{29}} = \dfrac{32}{\sqrt{29}}$. Laju maksimum di titik itu $|\nabla f| = \sqrt{80} = 4\sqrt5$.") +
      r"""<p><b>Soal 2.</b> Bidang singgung elipsoid $\tfrac{x^2}{4} + y^2 + \tfrac{z^2}{9} = 3$ di $(-2, 1, -3)$.</p>""" +
      steps(r"$\nabla F = \left\langle\tfrac{x}{2}, 2y, \tfrac{2z}{9}\right\rangle = \left\langle -1, 2, -\tfrac23\right\rangle$.",
            r"$-(x + 2) + 2(y - 1) - \tfrac23(z + 3) = 0$."),
      "Cara gradien untuk bidang singgung bekerja pada permukaan apa pun, bahkan yang tidak bisa ditulis z = f(x, y)."),
    S("example", "Bedah soal: medan suhu",
      r"""<p><b>Soal.</b> Suhu dalam bola logam $T(x, y, z) = \dfrac{80}{1 + x^2 + 2y^2 + 3z^2}$ (°C, meter). Di titik $(1, 1, -2)$, ke mana suhu naik paling cepat, dan berapa lajunya?</p>""" +
      steps(r"$\nabla T = -\dfrac{80}{(1 + x^2 + 2y^2 + 3z^2)^2}\langle 2x, 4y, 6z\rangle$.",
            r"Di $(1, 1, -2)$: penyebut $16^2 = 256$, sehingga $\nabla T = -\tfrac{80}{256}\langle 2, 4, -12\rangle = \tfrac58\langle -1, -2, 6\rangle$.",
            r"Arah kenaikan tercepat: $\langle -1, -2, 6\rangle$ (menuju pusat yang lebih panas).",
            r"Laju maksimum: $|\nabla T| = \tfrac58\sqrt{41} \approx 4$ °C/m.") +
      note(r"Hukum Fourier: fluks panas $\mathbf{q} = -k\nabla T$. Panas mengalir ke arah yang berlawanan dengan gradien, dari panas ke dingin."),
      "Arah boleh dijawab sebagai vektor apa pun yang searah; laju harus panjang gradien yang sebenarnya, lengkap dengan faktor 5/8."),
    S("pitfall", "Jebakan ujian",
      r"""<ul class="lesson-list">
        <li>Memakai vektor arah yang belum satuan: $\nabla f\cdot\langle 2, 5\rangle$ alih-alih dibagi $\sqrt{29}$.</li>
        <li>Menjawab "laju maksimum $= \nabla f$". Laju adalah angka $|\nabla f|$; arahnya vektor $\nabla f$.</li>
        <li>Aturan rantai: satu jalur di diagram pohon terlewat.</li>
        <li>Untuk grafik $z = f(x, y)$, normal permukaannya $\langle f_x, f_y, -1\rangle$, bukan $\langle f_x, f_y\rangle$. Gradien 2D tegak lurus <b>kontur</b>, bukan permukaan.</li>
        <li>Lupa mengevaluasi gradien di titik sebelum dikalikan titik.</li>
      </ul>""",
      "Jebakan keempat sering muncul di soal 'vektor normal permukaan'. Tulis permukaan sebagai F(x, y, z) = f(x, y) − z = 0, lalu ambil ∇F."),
    S("checkpoint", "Mini checkpoint",
      qa(r"1. $f = xe^y$ di $P(2, 0)$ ke arah titik $Q\left(\tfrac12, 2\right)$.", r"<p>$\overrightarrow{PQ} = \left\langle -\tfrac32, 2\right\rangle$, $\mathbf{u} = \left\langle -\tfrac35, \tfrac45\right\rangle$, $\nabla f = \langle 1, 2\rangle$: $D_{\mathbf{u}}f = -\tfrac35 + \tfrac85 = 1$.</p>") +
      qa(r"2. Pada soal 1, laju naik maksimum dan arahnya?", r"<p>$|\nabla f| = \sqrt5$ ke arah $\langle 1, 2\rangle$.</p>") +
      qa(r"3. $w = xy + z^2$, $x = t$, $y = t^2$, $z = t^3$. Hitung $\tfrac{dw}{dt}$.", r"<p>$y + 2tx + 2z\cdot 3t^2 = t^2 + 2t^2 + 6t^5 = 3t^2 + 6t^5$. Cek: $w = t^3 + t^6$.</p>"),
      "Soal 3 bisa dicek dengan substitusi langsung. Pakai cara ini untuk memverifikasi aturan rantai saat latihan."),
]

# ═══════════════════════════════════════════════════════════════════════════
# 5. Optimasi & Pengali Lagrange
# ═══════════════════════════════════════════════════════════════════════════
OPTIMASI_LAGRANGE = [
    S("intuition", "Puncak, lembah, dan pelana",
      r"""<p>Di permukaan dua variabel ada tiga jenis titik datar ($\nabla f = \mathbf{0}$): puncak, lembah, dan <b>pelana</b>
      (naik di satu arah, turun di arah lain, seperti keripik Pringles). Optimasi multivariabel dipakai untuk desain dengan bahan minimum,
      memaksimumkan keuntungan dengan anggaran terbatas, dan melatih model machine learning.</p>""",
      "Ubah c dari positif ke negatif. Titik asal berubah dari lembah menjadi pelana, padahal gradiennya tetap nol.",
      [ruang("z = (x² + c·y²)/2", [param("c", "c", -2, 2, 0.1, 1, "c")],
             [{"u": [-1.6, 1.6], "v": [-1.6, 1.6], "x": "u", "y": "v", "z": "(u*u + c*v*v)/2", "color": "purple"}],
             [readout("D = f_xx·f_yy − f_xy² = c", "c", 2)],
             "D > 0 dengan f_xx > 0: minimum lokal. D < 0: titik pelana. D = 0: uji gagal.")]),
    S("theorem", "Titik kritis & uji turunan kedua",
      r"""<p>Titik kritis: $\nabla f = \mathbf{0}$ (atau salah satu turunan parsial tidak ada). Di titik kritis $(a, b)$, hitung
      $$D = f_{xx}f_{yy} - f_{xy}^2 = \det\begin{pmatrix} f_{xx} &amp; f_{xy} \\ f_{xy} &amp; f_{yy}\end{pmatrix}.$$</p>
      <div class="table-scroll"><table class="lesson-table"><thead><tr><th>Kondisi</th><th>Kesimpulan</th></tr></thead><tbody>
        <tr><td>$D &gt; 0$, $f_{xx} &gt; 0$</td><td>minimum lokal</td></tr>
        <tr><td>$D &gt; 0$, $f_{xx} &lt; 0$</td><td>maksimum lokal</td></tr>
        <tr><td>$D &lt; 0$</td><td>titik pelana</td></tr>
        <tr><td>$D = 0$</td><td>tidak dapat disimpulkan</td></tr>
      </tbody></table></div>
      <p>Matriks tersebut adalah <b>Hessian</b> $H$. Dalam bahasa aljabar linear: kedua nilai eigen $H$ positif → minimum; keduanya negatif → maksimum; berlawanan tanda → pelana.</p>""",
      "D < 0 langsung pelana, tidak perlu cek f_xx. Tanda f_xx hanya dipakai saat D > 0."),
    S("example", "Bedah soal: klasifikasi titik kritis",
      r"""<p><b>Soal.</b> $f(x, y) = x^4 + y^4 - 4xy + 1$.</p>""" +
      steps(r"$f_x = 4x^3 - 4y = 0 \Rightarrow y = x^3$; $\ f_y = 4y^3 - 4x = 0 \Rightarrow x = y^3$.",
            r"Substitusi: $x = x^9 \Rightarrow x(x^8 - 1) = 0 \Rightarrow x = 0, 1, -1$. Titik kritis $(0, 0)$, $(1, 1)$, $(-1, -1)$.",
            r"$f_{xx} = 12x^2$, $f_{yy} = 12y^2$, $f_{xy} = -4$, sehingga $D = 144x^2y^2 - 16$.",
            r"$(0, 0)$: $D = -16 &lt; 0$ → pelana. $(\pm1, \pm1)$: $D = 128 &gt; 0$, $f_{xx} = 12 &gt; 0$ → minimum lokal dengan $f = -1$.") +
      note(r"Saat mencari titik kritis, jangan membagi dengan $x$ dari $x = x^9$; faktorkan agar $x = 0$ tidak hilang."),
      "Sistem f_x = 0, f_y = 0 adalah bagian tersulit. Cari satu persamaan yang mudah dinyatakan sebagai y = ..., lalu substitusi."),
    S("theorem", "Ekstrem mutlak pada daerah tertutup",
      r"""<p>Fungsi kontinu pada daerah <b>tertutup dan terbatas</b> $D$ pasti mencapai maksimum dan minimum mutlak (analog interval tertutup di Kalkulus 1).</p>""" +
      steps(r"Cari titik kritis di <b>dalam</b> $D$ dan hitung nilainya.",
            r"Cari nilai ekstrem di <b>batas</b> $D$: parametrisasi tiap potongan batas menjadi fungsi satu variabel, atau pakai Lagrange.",
            r"Bandingkan semua nilai: terbesar = maks mutlak, terkecil = min mutlak."),
      "Batas segitiga atau persegi panjang dipecah menjadi beberapa ruas garis. Jangan lupa titik-titik sudutnya."),
    S("theorem", "Pengali Lagrange",
      r"""<p>Untuk mengoptimumkan $f(x, y)$ dengan kendala $g(x, y) = c$, selesaikan
      $$\nabla f = \lambda\nabla g, \qquad g(x, y) = c.$$</p>
      <p><b>Intuisi geometri:</b> telusuri kurva kendala sambil memperhatikan kontur $f$. Selama kurva <b>memotong</b> kontur, kamu masih bisa naik atau turun.
      Nilai ekstrem terjadi saat kurva kendala hanya <b>menyinggung</b> satu kontur. Di sana kedua kurva punya garis singgung yang sama, jadi normalnya ($\nabla f$ dan $\nabla g$) sejajar.</p>
      <p>Dua kendala $g = c$ dan $h = k$: $\nabla f = \lambda\nabla g + \mu\nabla h$.</p>""",
      "Geser k. Kontur terjauh yang masih menyentuh lingkaran adalah maksimum, dan di sana garis itu menyinggung lingkaran.",
      [g("Maksimumkan f = x + 2y pada lingkaran x² + y² = 4", [-3.5, 3.5], [-3, 3], [param("k", "Nilai f = x + 2y = k", -5, 5, 0.05, 2, "k")],
         [{"type": "param", "x": "2*cos(t)", "y": "2*sin(t)", "t": [0, "2*pi"], "color": "blue", "label": "kendala"},
          {"type": "fn", "expr": "(k - x)/2", "color": "red", "dash": True, "label": "kontur x + 2y = k"},
          {"type": "point", "x": "2/sqrt(5)", "y": "4/sqrt(5)", "color": "green"}],
         [readout("k sekarang", "k", 3), readout("Maksimum 2√5", "2*sqrt(5)", 4)],
         "Titik hijau (2/√5, 4/√5): ∇f = ⟨1, 2⟩ sejajar ∇g = ⟨2x, 2y⟩.")]),
    S("derivation", "Pohon keputusan: optimasi multivariabel",
      pohon(r"Tanpa kendala, domain terbuka (seluruh bidang)? → $\nabla f = \mathbf{0}$ + uji turunan kedua.",
            r"Daerah tertutup dan terbatas? → titik kritis dalam + nilai di batas + bandingkan (metode daerah tertutup).",
            r"Kendala persamaan $g = c$ yang mudah diselesaikan untuk satu variabel? → substitusi, jadikan satu variabel.",
            r"Kendala persamaan yang rumit atau simetris? → <b>Lagrange</b>, lalu bandingkan nilai $f$ di semua kandidat.",
            r"Kendala ketaksamaan $g \le c$? → dalam ($\nabla f = 0$) + batas (Lagrange); di machine learning diperumum menjadi syarat KKT.") +
      note(r"Lagrange hanya memberi <b>kandidat</b>. Tentukan mana maksimum dan mana minimum dengan membandingkan nilai $f$."),
      "Nilai λ sendiri jarang ditanya. Pakai λ sebagai alat untuk menghubungkan x, y, z, lalu buang."),
    S("example", "Soal UAS: kotak tanpa tutup",
      r"""<p><b>Soal.</b> Kotak tanpa tutup bervolume $32$ m³. Ukuran berapa yang meminimumkan luas bahan?</p>""" +
      steps(r"$S = xy + 2xz + 2yz$ dengan kendala $V = xyz = 32$.",
            r"$\nabla S = \lambda\nabla V$: $y + 2z = \lambda yz$, $\ x + 2z = \lambda xz$, $\ 2x + 2y = \lambda xy$.",
            r"Kalikan berturut-turut dengan $x$, $y$, $z$: ruas kanan sama-sama $\lambda xyz$, sehingga $xy + 2xz = xy + 2yz = 2xz + 2yz$.",
            r"Persamaan pertama = kedua: $xz = yz \Rightarrow x = y$. Kedua = ketiga: $xy = 2xz \Rightarrow y = 2z$.",
            r"$x = y = 2z$ dan $4z^3 = 32$, jadi $z = 2$, $x = y = 4$. Luas minimum $S = 16 + 16 + 16 = 48$ m².") +
      note(r"Trik 'kalikan agar ruas kanan sama' sangat sering dipakai untuk sistem Lagrange yang simetris."),
      "Kotak tanpa tutup optimal tingginya setengah sisi alas. Hasil yang mudah diingat dan sering dipakai sebagai cek."),
    S("example", "Bedah soal: ekstrem pada cakram",
      r"""<p><b>Soal.</b> Nilai ekstrem $f(x, y) = x^2 + 2y^2$ pada cakram $x^2 + y^2 \le 1$.</p>""" +
      steps(r"Dalam: $\nabla f = \langle 2x, 4y\rangle = \mathbf{0}$ hanya di $(0, 0)$, $f = 0$.",
            r"Batas (Lagrange, $g = x^2 + y^2$): $2x = 2\lambda x$, $4y = 2\lambda y$.",
            r"Dari persamaan pertama: $x = 0$ atau $\lambda = 1$. Jika $x = 0$: $y = \pm1$, $f = 2$. Jika $\lambda = 1$: $y = 0$, $x = \pm1$, $f = 1$.",
            r"Bandingkan $\{0, 2, 1\}$: maksimum $2$ di $(0, \pm1)$, minimum $0$ di $(0, 0)$."),
      "Langkah 3 menunjukkan cara aman: tulis 'x = 0 ATAU λ = 1', jangan membagi dengan x."),
    S("pitfall", "Jebakan ujian",
      r"""<ul class="lesson-list">
        <li>$D = 0$ disimpulkan "bukan ekstrem". Seharusnya: tidak dapat disimpulkan.</li>
        <li>Lupa memeriksa batas pada daerah tertutup.</li>
        <li>Membagi dengan variabel yang mungkin nol saat menyelesaikan sistem, sehingga solusi hilang.</li>
        <li>Menganggap semua kandidat Lagrange adalah maksimum.</li>
        <li>Salah tanda $f_{xy}$ pada $D = f_{xx}f_{yy} - f_{xy}^2$ (kuadrat membuat tandanya tak berpengaruh, tetapi lupa mengkuadratkan berakibat fatal).</li>
      </ul>""",
      "Untuk sistem persamaan, faktorkan. Setiap faktor nol adalah cabang yang harus kamu telusuri."),
    S("checkpoint", "Mini checkpoint",
      qa(r"1. Klasifikasikan titik kritis $f = x^2 + xy + y^2 - 3x$.",
         r"<p>$2x + y = 3$, $x + 2y = 0 \Rightarrow (2, -1)$. $D = 4 - 1 = 3 &gt; 0$, $f_{xx} = 2 &gt; 0$: minimum lokal, $f = -3$.</p>") +
      qa(r"2. Maksimumkan $xy$ dengan kendala $x + y = 10$.", r"<p>$y = \lambda$, $x = \lambda$, jadi $x = y = 5$, $xy = 25$.</p>"),
      "Soal 2 juga bisa disubstitusi: xy = x(10 − x). Lagrange dan substitusi harus memberi jawaban yang sama."),
]

NEW_TOPICS = [
    *[{"after": f"kl-{f}-pb-limit", "slug": f"kl-{f}-fungsi-vektor", "title": "Fungsi Vektor & Kelengkungan", "icon": "m-arc",
       "summary": "Turunan & integral fungsi vektor, panjang busur, kelengkungan, komponen percepatan.",
       "references": "Stewart §13.1–13.4; OpenStax Vol 3 Bab 3"} for f in ("ft", "fm", "fk")],
    {"after": "kl-fk-tp-gradien", "slug": "kl-fk-lagrange", "title": "Optimasi & Pengali Lagrange", "icon": "m-lagrange",
     "summary": "Uji turunan kedua, Hessian, ekstrem pada daerah tertutup, pengali Lagrange.",
     "references": "Stewart §14.7–14.8; OpenStax Vol 3 §4.7–4.8"},
]

CORE_SLIDES = {
    "pb-fungsi": GEOMETRI_RUANG,
    "tp-parsial": TURUNAN_PARSIAL,
    "tp-gradien": GRADIEN,
}

SLIDES = {
    "kl-ft-lagrange": OPTIMASI_LAGRANGE,
    "kl-fm-hessian": OPTIMASI_LAGRANGE,
    "kl-fk-lagrange": OPTIMASI_LAGRANGE,
    **{f"kl-{f}-fungsi-vektor": FUNGSI_VEKTOR for f in ("ft", "fm", "fk")},
}
