r"""
Kurikulum v2 — Batch 4 (bagian B): slide Level 4, integral lipat & kalkulus vektor.

Topik: Integral Lipat Dua & Tiga · Koordinat Silinder & Bola · Medan Vektor, Divergensi & Curl ·
Integral Garis & Teorema Green · Integral Permukaan, Stokes & Divergensi Gauss.
Penekanan: intuisi geometri lebih dulu (mengapa faktor Jacobian muncul, orientasi permukaan,
fluks vs sirkulasi) sebelum perhitungan integral lipat tiga.

Rujukan: Stewart 9e §15.1–15.9, §16.1–16.9; Purcell Jil. 2 Bab 13–14; OpenStax Calculus Vol 3 Bab 5–6.
"""

from ..helpers import param, readout
from .l1_slides import S, g, note, qa, steps
from .l3_slides import pohon
from .l4_slides import kurva3, ruang


def panah(P, Q, lim=2.5, n=7, s=0.18, color="blue"):
    """Medan vektor 2D sebagai grid panah. P, Q: ekspresi JS dengan {x} dan {y} (boleh memakai slider)."""
    grid = [round(-lim + 2 * lim * i / (n - 1), 3) for i in range(n)]
    els = []
    for x in grid:
        for y in grid:
            px, qy = P.format(x=f"({x})", y=f"({y})"), Q.format(x=f"({x})", y=f"({y})")
            els.append({"type": "segment", "x1": x, "y1": y, "x2": f"{x} + {s}*({px})", "y2": f"{y} + {s}*({qy})",
                        "color": color, "arrow": True, "width": 1.3})
    return els


# ═══════════════════════════════════════════════════════════════════════════
# 6. Integral Lipat Dua & Tiga
# ═══════════════════════════════════════════════════════════════════════════
INTEGRAL_LIPAT = [
    S("intuition", "Volume sebagai tumpukan kolom",
      r"""<p>Integral tunggal menjumlahkan persegi panjang tipis menjadi luas. Integral lipat dua menjumlahkan <b>kolom-kolom</b> tipis berpenampang $\Delta A$
      dan tinggi $f(x, y)$ menjadi volume di bawah permukaan. Lebih umum, $\iint_D f\,dA$ menjumlahkan "kepadatan × luas": massa pelat dengan rapat
      massa berbeda-beda, total curah hujan di suatu wilayah, atau peluang suatu kejadian dari fungsi kepadatan peluang gabungan.</p>""",
      "Integral lipat bukan rumus baru, melainkan integral biasa yang dilakukan dua kali: sekali untuk tiap arah irisan."),
    S("theorem", "Integral lipat dua pada persegi panjang & Teorema Fubini",
      r"""<p>$$\iint_R f(x, y)\,dA = \lim_{m, n \to \infty}\sum_{i=1}^{m}\sum_{j=1}^{n}f(x_{ij}^*, y_{ij}^*)\,\Delta A.$$</p>
      <p><b>Fubini:</b> untuk $f$ kontinu pada $R = [a, b]\times[c, d]$, urutan integrasi boleh ditukar:
      $$\iint_R f\,dA = \int_a^b\int_c^d f(x, y)\,dy\,dx = \int_c^d\int_a^b f(x, y)\,dx\,dy.$$</p>
      <p><b>Contoh.</b> $R = [0, 2]\times[1, 2]$: $\displaystyle\int_0^2\int_1^2(x - 3y^2)\,dy\,dx = \int_0^2\Big[xy - y^3\Big]_{y=1}^{y=2}dx = \int_0^2(x - 7)\,dx = -12$.</p>""",
      "Integral dalam dikerjakan lebih dulu, dengan variabel luar dianggap konstanta. Persis seperti turunan parsial, tapi kebalikannya."),
    S("theorem", "Daerah umum: tipe I dan tipe II",
      r"""<p><b>Tipe I</b> (irisan tegak): $D = \{a \le x \le b,\ g_1(x) \le y \le g_2(x)\}$, sehingga $\displaystyle\iint_D f\,dA = \int_a^b\int_{g_1(x)}^{g_2(x)}f\,dy\,dx$.</p>
      <p><b>Tipe II</b> (irisan mendatar): $D = \{c \le y \le d,\ h_1(y) \le x \le h_2(y)\}$.</p>""" +
      pohon(r"Gambar daerah $D$ dan cari semua titik potong batasnya.",
            r"Pilih arah irisan yang batas bawah dan atasnya masing-masing <b>satu</b> rumus. Jika tidak bisa, pecah daerahnya.",
            r"Integral dalam mustahil dihitung (misalnya $\int e^{x^2}dx$ atau $\int\sin(y^2)dy$)? <b>Tukar urutan</b>: gambar ulang daerah, tulis batas baru.",
            r"Batas luar selalu <b>konstanta</b>; batas dalam boleh bergantung pada variabel luar.") ,
      "Geser x di grafik. Ruas merah adalah satu irisan tegak: ujung bawahnya g₁(x), ujung atasnya g₂(x).",
      [g("Daerah tipe I: 2x² ≤ y ≤ 1 + x²", [-1.5, 1.5], [-0.3, 2.3], [param("X", "Posisi irisan x", -1, 1, 0.01, 0.4, "x")],
         [{"type": "fill", "upper": "1 + x*x", "lower": "2*x*x", "from": -1, "to": 1, "color": "blue"},
          {"type": "fn", "expr": "1 + x*x", "color": "blue", "label": "y = 1 + x²"},
          {"type": "fn", "expr": "2*x*x", "color": "orange", "label": "y = 2x²"},
          {"type": "segment", "x1": "X", "y1": "2*X*X", "x2": "X", "y2": "1 + X*X", "color": "red", "width": 3}],
         [readout("Batas bawah y = 2x²", "2*X*X", 3), readout("Batas atas y = 1 + x²", "1 + X*X", 3)],
         "Titik potong x = ±1 menjadi batas luar (konstanta).")]),
    S("example", "Bedah soal: daerah umum & menukar urutan",
      r"""<p><b>Soal 1.</b> $\displaystyle\iint_D(x + 2y)\,dA$, $D$ di antara $y = 2x^2$ dan $y = 1 + x^2$.</p>""" +
      steps(r"Titik potong $2x^2 = 1 + x^2 \Rightarrow x = \pm1$; daerah tipe I.",
            r"$\displaystyle\int_{-1}^{1}\Big[xy + y^2\Big]_{2x^2}^{1 + x^2}dx = \int_{-1}^{1}\left(-3x^4 - x^3 + 2x^2 + x + 1\right)dx$.",
            r"$= \left[-\tfrac35x^5 - \tfrac14x^4 + \tfrac23x^3 + \tfrac12x^2 + x\right]_{-1}^{1} = \dfrac{32}{15}$.") +
      r"""<p><b>Soal 2.</b> $\displaystyle\int_0^1\int_x^1\sin(y^2)\,dy\,dx$ (integral dalam tidak elementer).</p>""" +
      steps(r"Daerah: $0 \le x \le 1$, $x \le y \le 1$. Gambar: segitiga di atas garis $y = x$.",
            r"Sebagai tipe II: $0 \le y \le 1$, $0 \le x \le y$.",
            r"$\displaystyle\int_0^1\int_0^y\sin(y^2)\,dx\,dy = \int_0^1 y\sin(y^2)\,dy = \tfrac12(1 - \cos 1) \approx 0.2298$."),
      "Soal 2 adalah pola soal UAS favorit: integral yang 'mustahil' menjadi mudah setelah urutannya ditukar."),
    S("theorem", "Mengapa ada faktor Jacobian?",
      r"""<p>Saat berganti koordinat $(u, v) \mapsto (x, y)$, satu persegi kecil $du \times dv$ di bidang $uv$ dipetakan menjadi <b>jajargenjang</b> kecil di bidang $xy$,
      dengan sisi $\mathbf{r}_u\,du$ dan $\mathbf{r}_v\,dv$. Luasnya adalah panjang hasil kali silang:
      $$dA = |\mathbf{r}_u\times\mathbf{r}_v|\,du\,dv = \left|\frac{\partial(x, y)}{\partial(u, v)}\right|du\,dv, \qquad \frac{\partial(x, y)}{\partial(u, v)} = \det\begin{pmatrix} x_u &amp; x_v \\ y_u &amp; y_v\end{pmatrix}.$$</p>
      <p>Jacobian adalah <b>faktor pembesaran luas</b> lokal dari pemetaan itu, sama seperti $|\det A|$ adalah faktor pembesaran luas transformasi linear $A$.</p>
      <p><b>Kutub:</b> sel kutub berukuran $dr$ ke arah radial dan $r\,d\theta$ ke arah melingkar (busur makin panjang makin jauh dari pusat), jadi
      $dA = r\,dr\,d\theta$. Itulah asal huruf $r$ yang sering terlupa.</p>""",
      "Geser r: sel dengan Δr dan Δθ sama ternyata luasnya membesar sebanding r. Faktor r bukan hiasan, itu koreksi luas.",
      [g("Sel kutub: luas ≈ r·Δr·Δθ", [-0.5, 4.5], [-0.5, 4.5],
         [param("R0", "Jari-jari r", 0.3, 3, 0.05, 1.5, "r"), param("dR", "Δr", 0.1, 0.8, 0.05, 0.5, "Δr"), param("dT", "Δθ", 0.1, 0.8, 0.05, 0.4, "Δθ")],
         [{"type": "param", "x": f"{k}*cos(t)", "y": f"{k}*sin(t)", "t": [0, "pi/2"], "color": "gray", "dash": True} for k in (1, 2, 3, 4)] +
         [{"type": "param", "x": "R0*cos(t)", "y": "R0*sin(t)", "t": [0.3, "0.3 + dT"], "color": "red"},
          {"type": "param", "x": "(R0 + dR)*cos(t)", "y": "(R0 + dR)*sin(t)", "t": [0.3, "0.3 + dT"], "color": "red"},
          {"type": "segment", "x1": "R0*cos(0.3)", "y1": "R0*sin(0.3)", "x2": "(R0 + dR)*cos(0.3)", "y2": "(R0 + dR)*sin(0.3)", "color": "red"},
          {"type": "segment", "x1": "R0*cos(0.3 + dT)", "y1": "R0*sin(0.3 + dT)", "x2": "(R0 + dR)*cos(0.3 + dT)", "y2": "(R0 + dR)*sin(0.3 + dT)", "color": "red"}],
         [readout("Luas eksak ½((r + Δr)² − r²)Δθ", "0.5*((R0 + dR)*(R0 + dR) - R0*R0)*dT", 4),
          readout("Hampiran r·Δr·Δθ", "R0*dR*dT", 4), readout("Δr·Δθ saja (tanpa Jacobian)", "dR*dT", 4)],
         "Hampiran dengan faktor r makin akurat untuk sel kecil; tanpa r, luasnya salah besar jauh dari pusat.")]),
    S("example", "Bedah soal: integral lipat dalam kutub",
      r"""<p><b>Soal 1.</b> $\displaystyle\iint_D(3x + 4y^2)\,dA$, $D$ setengah cincin atas $1 \le x^2 + y^2 \le 4$, $y \ge 0$.</p>""" +
      steps(r"Dalam kutub: $1 \le r \le 2$, $0 \le \theta \le \pi$, dan $dA = r\,dr\,d\theta$.",
            r"$\displaystyle\int_0^{\pi}\int_1^2\left(3r\cos\theta + 4r^2\sin^2\theta\right)r\,dr\,d\theta = \int_0^{\pi}\left(7\cos\theta + 15\sin^2\theta\right)d\theta$.",
            r"$= 0 + 15\cdot\dfrac{\pi}{2} = \dfrac{15\pi}{2}$.") +
      r"""<p><b>Soal 2 (integral Gauss).</b> $I = \displaystyle\int_{-\infty}^{\infty}e^{-x^2}dx$ tidak punya antiturunan elementer, tetapi</p>""" +
      steps(r"$I^2 = \displaystyle\int_{-\infty}^{\infty}e^{-x^2}dx\int_{-\infty}^{\infty}e^{-y^2}dy = \iint_{\mathbb{R}^2}e^{-(x^2 + y^2)}dA$.",
            r"Kutub: $\displaystyle\int_0^{2\pi}\int_0^{\infty}e^{-r^2}r\,dr\,d\theta = 2\pi\cdot\frac12 = \pi$. Faktor $r$ dari Jacobian justru yang membuat integral ini bisa dihitung.",
            r"$I = \sqrt{\pi}$. Inilah konstanta di fungsi kepadatan distribusi normal $\tfrac{1}{\sqrt{2\pi}}e^{-z^2/2}$."),
      "Pakai kutub saat daerah berbentuk lingkaran/cincin/juring, atau integran memuat x² + y²."),
    S("theorem", "Integral lipat tiga",
      r"""<p>$\displaystyle\iiint_E f(x, y, z)\,dV$ menjumlahkan kepadatan di dalam benda padat. Dengan $f = 1$ hasilnya volume; dengan $f = \rho$ (rapat massa) hasilnya massa.</p>
      <p>Daerah tipe 1: $E = \{(x, y) \in D,\ u_1(x, y) \le z \le u_2(x, y)\}$, sehingga
      $$\iiint_E f\,dV = \iint_D\left[\int_{u_1(x, y)}^{u_2(x, y)}f\,dz\right]dA.$$</p>
      <p><b>Strategi:</b> tentukan "lantai" dan "atap" benda untuk batas $z$, lalu proyeksikan benda ke bidang $xy$ untuk mendapat $D$.</p>
      <p><b>Contoh.</b> Volume tetrahedron yang dibatasi $x + 2y + z = 2$, $x = 2y$, $x = 0$, $z = 0$:
      lantai $z = 0$, atap $z = 2 - x - 2y$; proyeksi $D$: $0 \le x \le 1$, $\tfrac{x}{2} \le y \le 1 - \tfrac{x}{2}$.
      $$V = \int_0^1\int_{x/2}^{1 - x/2}(2 - x - 2y)\,dy\,dx = \int_0^1(1 - x)^2dx = \frac13.$$</p>""",
      "Integral lipat tiga = integral lipat dua dari 'tinggi kolom'. Selesaikan z dulu, sisanya soal lipat dua yang sudah kamu kuasai."),
    S("pitfall", "Jebakan ujian",
      r"""<ul class="lesson-list">
        <li>Batas luar memuat variabel: $\int_0^x\int_0^1\dots$. Batas paling luar harus konstanta.</li>
        <li>Lupa faktor $r$ dalam koordinat kutub.</li>
        <li>Menukar urutan integrasi hanya dengan menukar batas angka, tanpa menggambar ulang daerah.</li>
        <li>Menulis $dA = dx\,dy$ lalu mengintegralkan dengan batas yang cocok untuk $dy\,dx$.</li>
        <li>Volume dengan $\iint_D f\,dA$ ketika $f$ bernilai negatif di sebagian $D$ (hasilnya volume bertanda).</li>
      </ul>""",
      "Setiap kali menukar urutan atau koordinat, gambar daerahnya. Ini satu-satunya cara andal mendapat batas yang benar."),
    S("checkpoint", "Mini checkpoint",
      qa(r"1. $\displaystyle\int_0^1\int_0^2 xy\,dx\,dy$", r"<p>$\displaystyle\int_0^1 2y\,dy = 1$.</p>") +
      qa(r"2. Tukar urutan $\displaystyle\int_0^4\int_{\sqrt x}^{2}f(x, y)\,dy\,dx$.", r"<p>Daerah $0 \le y \le 2$, $0 \le x \le y^2$: $\displaystyle\int_0^2\int_0^{y^2}f\,dx\,dy$.</p>") +
      qa(r"3. Luas cakram berjari-jari $a$ dengan kutub.", r"<p>$\displaystyle\int_0^{2\pi}\int_0^a r\,dr\,d\theta = \pi a^2$.</p>"),
      "Soal 3 adalah uji kewajaran faktor Jacobian: tanpa r, luas lingkaran akan menjadi 2πa. Salah dimensi!"),
]

# ═══════════════════════════════════════════════════════════════════════════
# 7. Koordinat Silinder & Bola
# ═══════════════════════════════════════════════════════════════════════════
SILINDER_BOLA = [
    S("intuition", "Pilih koordinat yang cocok dengan simetri",
      r"""<p>Pipa, kaleng, dan tangki air simetri terhadap satu sumbu: pakai <b>koordinat silinder</b>. Planet, bola lampu yang memancar ke segala arah,
      dan pola radiasi antena simetri terhadap satu titik: pakai <b>koordinat bola</b>. Koordinat yang tepat membuat batas integral menjadi konstanta dan integrannya sederhana.</p>""",
      "Ubah sudut kerucut φ₀ dan jari-jari R. Daerah 'es krim' ini batasnya cuma ρ ≤ R dan φ ≤ φ₀ dalam koordinat bola.",
      [ruang("Kerucut es krim: 0 ≤ ρ ≤ R, 0 ≤ φ ≤ φ₀", [param("R", "Jari-jari R", 0.5, 1.8, 0.05, 1.5, "R"), param("p", "Sudut kerucut φ₀", 0.2, 1.5, 0.02, 0.785, "φ₀")],
             [{"u": [0, "R"], "v": [0, "2*pi"], "nu": 6, "nv": 24, "x": "u*sin(p)*cos(v)", "y": "u*sin(p)*sin(v)", "z": "u*cos(p)", "color": "orange"},
              {"u": [0, "p"], "v": [0, "2*pi"], "nu": 8, "nv": 24, "x": "R*sin(u)*cos(v)", "y": "R*sin(u)*sin(v)", "z": "R*cos(u)", "color": "blue"}],
             [readout("Volume = (2π/3)R³(1 − cos φ₀)", "2*pi/3*R*R*R*(1 - cos(p))", 4)],
             "φ₀ = π: seluruh bola, dan rumusnya menjadi (4/3)πR³.")]),
    S("theorem", "Koordinat silinder",
      r"""<p>$$x = r\cos\theta, \quad y = r\sin\theta, \quad z = z, \qquad dV = r\,dz\,dr\,d\theta.$$</p>
      <p>Ini koordinat kutub ditambah tinggi $z$, jadi Jacobiannya tetap $r$: sel silinder berukuran $dr \times r\,d\theta \times dz$.</p>
      <div class="table-scroll"><table class="lesson-table"><thead><tr><th>Kartesius</th><th>Silinder</th></tr></thead><tbody>
        <tr><td>tabung $x^2 + y^2 = a^2$</td><td>$r = a$</td></tr>
        <tr><td>paraboloid $z = x^2 + y^2$</td><td>$z = r^2$</td></tr>
        <tr><td>kerucut $z = \sqrt{x^2 + y^2}$</td><td>$z = r$</td></tr>
        <tr><td>bidang $y = x$ ($x &gt; 0$)</td><td>$\theta = \tfrac{\pi}{4}$</td></tr>
      </tbody></table></div>""",
      "Koordinat silinder = kutub + z. Kalau kamu lancar kutub di integral lipat dua, kamu sudah lancar silinder."),
    S("theorem", "Koordinat bola & Jacobian ρ² sin φ",
      r"""<p>$$x = \rho\sin\phi\cos\theta, \quad y = \rho\sin\phi\sin\theta, \quad z = \rho\cos\phi, \qquad \rho \ge 0,\ 0 \le \phi \le \pi.$$</p>
      <p>$\rho$ = jarak ke titik asal, $\phi$ = sudut dari sumbu $z$ positif (seperti "90° dikurangi lintang"), $\theta$ = sudut seperti bujur.</p>
      <p><b>Mengapa $dV = \rho^2\sin\phi\,d\rho\,d\phi\,d\theta$?</b> Sel bola punya tiga rusuk: $d\rho$ (radial), $\rho\,d\phi$ (busur meridian berjari-jari $\rho$),
      dan $\rho\sin\phi\,d\theta$ (busur lingkaran lintang, yang jari-jarinya hanya $\rho\sin\phi$). Hasil kalinya $\rho^2\sin\phi\,d\rho\,d\phi\,d\theta$.
      Di dekat kutub ($\phi \approx 0$) lingkaran lintang menyusut, persis seperti garis bujur di globe yang merapat di Kutub Utara.</p>""",
      "Konvensi fisika menukar huruf: banyak buku fisika memakai θ untuk sudut dari sumbu z dan φ untuk bujur. Cek dulu notasi buku/dosenmu."),
    S("derivation", "Pohon keputusan: Kartesius, silinder, atau bola?",
      pohon(r"Benda dibatasi bidang-bidang datar (kotak, tetrahedron)? → <b>Kartesius</b>.",
            r"Ada simetri terhadap satu sumbu: tabung $x^2 + y^2 = a^2$, paraboloid, atau integran memuat $x^2 + y^2$? → <b>silinder</b>.",
            r"Ada bola $x^2 + y^2 + z^2 = a^2$, kerucut $z = \sqrt{x^2 + y^2}$, atau integran memuat $x^2 + y^2 + z^2$? → <b>bola</b>.",
            r"Tulis setiap permukaan batas dalam koordinat baru, tentukan rentang tiap variabel, dan <b>jangan lupa Jacobian</b>.") +
      note(r"Kerucut $z = \sqrt{x^2 + y^2}$ dalam koordinat bola sangat sederhana: $\rho\cos\phi = \rho\sin\phi$, yaitu $\phi = \tfrac{\pi}{4}$."),
      "Tanda paling jelas untuk bola: muncul x² + y² + z². Untuk silinder: muncul x² + y² tanpa z²."),
    S("example", "Bedah soal: koordinat silinder",
      r"""<p><b>Soal.</b> Benda $E$ di dalam tabung $x^2 + y^2 = 1$, di bawah bidang $z = 4$, di atas paraboloid $z = 1 - x^2 - y^2$. Rapat massanya sebanding dengan jarak ke sumbu: $\rho = K\sqrt{x^2 + y^2}$. Hitung massanya.</p>""" +
      steps(r"Silinder: lantai $z = 1 - r^2$, atap $z = 4$, $0 \le r \le 1$, $0 \le \theta \le 2\pi$; rapat massa $Kr$.",
            r"$m = \displaystyle\int_0^{2\pi}\int_0^1\int_{1 - r^2}^{4}(Kr)\,r\,dz\,dr\,d\theta = K\int_0^{2\pi}\int_0^1 r^2(3 + r^2)\,dr\,d\theta$.",
            r"$= 2\pi K\left[r^3 + \dfrac{r^5}{5}\right]_0^1 = \dfrac{12\pi K}{5}$.") +
      note(r"Perhatikan dua $r$ yang berbeda asal: satu dari rapat massa, satu dari Jacobian. Keduanya harus ada."),
      "Tulis Jacobian di baris yang sama saat mengganti koordinat. Jangan menunda sampai 'nanti saja', karena pasti terlupa."),
    S("example", "Bedah soal: koordinat bola",
      r"""<p><b>Soal 1.</b> Volume benda di atas kerucut $z = \sqrt{x^2 + y^2}$ dan di bawah bola $x^2 + y^2 + z^2 = z$.</p>""" +
      steps(r"Bola: $\rho^2 = \rho\cos\phi \Rightarrow \rho = \cos\phi$. Kerucut: $\phi = \tfrac{\pi}{4}$.",
            r"$V = \displaystyle\int_0^{2\pi}\int_0^{\pi/4}\int_0^{\cos\phi}\rho^2\sin\phi\,d\rho\,d\phi\,d\theta = 2\pi\int_0^{\pi/4}\frac{\cos^3\phi\sin\phi}{3}\,d\phi$.",
            r"$= \dfrac{2\pi}{3}\left[-\dfrac{\cos^4\phi}{4}\right]_0^{\pi/4} = \dfrac{2\pi}{3}\cdot\dfrac14\left(1 - \dfrac14\right) = \dfrac{\pi}{8}$.") +
      r"""<p><b>Soal 2.</b> $\displaystyle\iiint_B e^{(x^2 + y^2 + z^2)^{3/2}}dV$, $B$ bola satuan.</p>""" +
      steps(r"$\displaystyle\int_0^{2\pi}\int_0^{\pi}\int_0^1 e^{\rho^3}\rho^2\sin\phi\,d\rho\,d\phi\,d\theta = 2\pi\cdot 2\cdot\frac{e - 1}{3} = \frac{4\pi}{3}(e - 1)$.",
            r"Faktor $\rho^2$ dari Jacobian adalah turunan $\rho^3$ (dibagi 3), sehingga substitusi $u = \rho^3$ langsung berhasil."),
      "Soal 2 tidak mungkin dihitung dalam Kartesius. Jacobian bola justru 'membantu' integralnya."),
    S("pitfall", "Jebakan ujian",
      r"""<ul class="lesson-list">
        <li>Lupa Jacobian $r$ (silinder) atau $\rho^2\sin\phi$ (bola).</li>
        <li>Rentang $\phi$ ditulis $0$ sampai $2\pi$. Seharusnya $0$ sampai $\pi$; yang memutar penuh adalah $\theta$.</li>
        <li>Mencampur $r$ (jarak ke sumbu $z$) dengan $\rho$ (jarak ke titik asal). Hubungannya $r = \rho\sin\phi$.</li>
        <li>Notasi fisika vs matematika untuk $\theta$ dan $\phi$ tertukar.</li>
        <li>Batas $\rho$ masih memuat $x$, $y$, $z$, belum diubah ke $\rho$ dan $\phi$.</li>
      </ul>""",
      "Uji cepat semua rumus: hitung volume bola berjari-jari a. Kalau tidak keluar (4/3)πa³, ada yang salah di Jacobian atau batas."),
    S("checkpoint", "Mini checkpoint",
      qa(r"1. Volume bola berjari-jari $a$.", r"<p>$\displaystyle\int_0^{2\pi}\int_0^{\pi}\int_0^a\rho^2\sin\phi\,d\rho\,d\phi\,d\theta = 2\pi\cdot 2\cdot\frac{a^3}{3} = \frac43\pi a^3$.</p>") +
      qa(r"2. Tulis $z = x^2 + y^2$ dalam silinder dan bola.", r"<p>Silinder: $z = r^2$. Bola: $\rho\cos\phi = \rho^2\sin^2\phi$, yaitu $\rho = \dfrac{\cos\phi}{\sin^2\phi}$.</p>") +
      qa(r"3. Massa tabung $r \le 2$, $0 \le z \le 3$ dengan rapat massa $\delta = r$.", r"<p>$\displaystyle\int_0^{2\pi}\int_0^2\int_0^3 r\cdot r\,dz\,dr\,d\theta = 2\pi\cdot 3\cdot\frac83 = 16\pi$.</p>"),
      "Soal 2 menunjukkan paraboloid jauh lebih rapi dalam silinder daripada dalam bola."),
]

# ═══════════════════════════════════════════════════════════════════════════
# 8. Medan Vektor, Divergensi & Curl
# ═══════════════════════════════════════════════════════════════════════════
MEDAN_VEKTOR = [
    S("intuition", "Panah di setiap titik",
      r"""<p>Peta angin BMKG, arus laut, medan gravitasi, medan listrik di sekitar muatan, dan kecepatan partikel asap dalam simulasi grafika:
      semuanya memasang satu <b>vektor</b> di setiap titik. Itulah medan vektor $\mathbf{F}(x, y) = \langle P(x, y), Q(x, y)\rangle$.</p>
      <p>Dua pertanyaan alami tentang aliran: apakah di suatu titik fluida <b>menyembur keluar</b> (sumber) atau tersedot (sumur)? Dan apakah fluida
      <b>berputar</b> di sekitarnya? Keduanya dijawab divergensi dan curl.</p>""",
      "Mainkan a dan b. a mengatur sumber/sumur (panah menjauh/mendekat pusat), b mengatur putaran.",
      [g("F = ⟨ax − by, bx + ay⟩", [-3.2, 3.2], [-3.2, 3.2], [param("a", "Sumber a", -1, 1, 0.1, 0, "a"), param("b", "Putaran b", -1, 1, 0.1, 1, "b")],
         panah("a*{x} - b*{y}", "b*{x} + a*{y}"),
         [readout("div F = 2a", "2*a", 2), readout("curl F (komponen z) = 2b", "2*b", 2)],
         "a = 0, b = 1: putaran murni (div 0). a = 1, b = 0: sumber murni (curl 0).")]),
    S("theorem", "Medan vektor & medan gradien",
      r"""<ul class="lesson-list">
        <li>Medan di ℝ³: $\mathbf{F} = \langle P, Q, R\rangle$. Contoh: gravitasi $\mathbf{F} = -\dfrac{GMm}{|\mathbf{r}|^3}\mathbf{r}$ (selalu menunjuk ke pusat).</li>
        <li><b>Medan gradien:</b> $\mathbf{F} = \nabla f$. Medan seperti ini disebut <b>konservatif</b>, dan $f$ disebut <b>fungsi potensial</b>.</li>
        <li>Garis aliran (streamline) adalah kurva yang di setiap titik searah dengan $\mathbf{F}$.</li>
      </ul>
      <p>Medan gravitasi dan medan listrik statis konservatif: kerja yang dilakukan hanya bergantung pada titik awal dan akhir, sehingga ada "energi potensial".</p>""",
      "Konservatif = ada fungsi potensial = kerja tidak bergantung lintasan. Tiga cara menyebut hal yang sama."),
    S("theorem", "Divergensi & curl: fluks keluar vs sirkulasi",
      r"""<p>Dengan operator $\nabla = \left\langle\tfrac{\partial}{\partial x}, \tfrac{\partial}{\partial y}, \tfrac{\partial}{\partial z}\right\rangle$:
      $$\operatorname{div}\mathbf{F} = \nabla\cdot\mathbf{F} = P_x + Q_y + R_z, \qquad \operatorname{curl}\mathbf{F} = \nabla\times\mathbf{F} = \langle R_y - Q_z,\ P_z - R_x,\ Q_x - P_y\rangle.$$</p>
      <div class="table-scroll"><table class="lesson-table"><thead><tr><th></th><th>Divergensi (skalar)</th><th>Curl (vektor)</th></tr></thead><tbody>
        <tr><td>Mengukur</td><td><b>fluks</b> keluar per satuan volume: aliran <b>menembus</b> batas kotak kecil</td><td><b>sirkulasi</b> per satuan luas: aliran <b>menyusuri</b> batas lingkaran kecil</td></tr>
        <tr><td>Bayangkan</td><td>tinta yang menyebar dari satu titik</td><td>kincir kecil yang ikut berputar</td></tr>
        <tr><td>Nol berarti</td><td>tak termampatkan (inkompresibel)</td><td>tak berotasi (irotasional)</td></tr>
      </tbody></table></div>
      <p>Identitas: $\operatorname{curl}(\nabla f) = \mathbf{0}$ dan $\operatorname{div}(\operatorname{curl}\mathbf{F}) = 0$. Laplacian $\nabla^2 f = \nabla\cdot\nabla f$ muncul di persamaan panas dan elektrostatika.</p>""",
      "Fluks = komponen NORMAL (menembus), sirkulasi = komponen TANGENSIAL (menyusuri). Dua ide ini kembali di Green, Stokes, dan Gauss."),
    S("derivation", "Pohon keputusan: apakah F konservatif & bagaimana mencari potensial?",
      pohon(r"2D: cek $P_y = Q_x$; 3D: cek $\operatorname{curl}\mathbf{F} = \mathbf{0}$.",
            r"Domainnya <b>terhubung sederhana</b> (tanpa lubang)? Jika ya, uji di Cek 1 menjamin konservatif. Jika ada lubang, hati-hati.",
            r"Cari potensial: $f = \int P\,dx + g(y, z)$.",
            r"Turunkan terhadap $y$, samakan dengan $Q$ untuk mendapat $g$; ulangi untuk $z$.",
            r"Cek: $\nabla f$ harus kembali menjadi $\mathbf{F}$.") +
      r"""<p><b>Contoh.</b> $\mathbf{F} = \langle 3 + 2xy,\ x^2 - 3y^2\rangle$: $P_y = 2x = Q_x$, konservatif.
      $f = 3x + x^2y + g(y)$; $f_y = x^2 + g'(y) = x^2 - 3y^2 \Rightarrow g = -y^3$. Jadi $f = 3x + x^2y - y^3 + K$.</p>""",
      "Saat mengintegralkan terhadap x, 'konstanta' integrasinya adalah fungsi dari variabel lain, bukan sekadar angka."),
    S("example", "Bedah soal: divergensi & curl",
      r"""<p><b>Soal.</b> $\mathbf{F} = \langle xz,\ xyz,\ -y^2\rangle$.</p>""" +
      steps(r"$\operatorname{div}\mathbf{F} = (xz)_x + (xyz)_y + (-y^2)_z = z + xz$.",
            r"Komponen $x$ curl: $R_y - Q_z = -2y - xy$.",
            r"Komponen $y$: $P_z - R_x = x - 0 = x$.",
            r"Komponen $z$: $Q_x - P_y = yz - 0 = yz$.",
            r"$\operatorname{curl}\mathbf{F} = \langle -y(2 + x),\ x,\ yz\rangle \ne \mathbf{0}$, jadi tidak konservatif.") +
      note(r"Cara menghafal curl: determinan $\begin{vmatrix}\mathbf{i} &amp; \mathbf{j} &amp; \mathbf{k} \\ \partial_x &amp; \partial_y &amp; \partial_z \\ P &amp; Q &amp; R\end{vmatrix}$, sama seperti hasil kali silang."),
      "Komponen tengah curl adalah yang paling sering salah tanda. Pola siklik: x → y → z → x, komponen y = P_z − R_x."),
    S("pitfall", "Jebakan ujian",
      r"""<ul class="lesson-list">
        <li>Divergensi ditulis sebagai vektor, atau curl sebagai skalar.</li>
        <li>Salah tanda komponen tengah curl.</li>
        <li>$P_y = Q_x$ tetapi domain berlubang: $\mathbf{F} = \dfrac{\langle -y, x\rangle}{x^2 + y^2}$ memenuhi $P_y = Q_x$ di luar titik asal, tetapi <b>tidak</b> konservatif (sirkulasinya mengelilingi titik asal $2\pi$).</li>
        <li>Lupa fungsi $g(y, z)$ saat mencari potensial.</li>
        <li>Tertukar $\nabla f$ (vektor dari fungsi skalar), $\nabla\cdot\mathbf{F}$ (skalar), dan $\nabla\times\mathbf{F}$ (vektor).</li>
      </ul>""",
      "Contoh ⟨−y, x⟩/(x² + y²) adalah favorit dosen FMIPA. Ingat: syarat 'terhubung sederhana' itu bukan hiasan."),
    S("checkpoint", "Mini checkpoint",
      qa(r"1. Apakah $\mathbf{F} = \langle y\cos x,\ \sin x + 2y\rangle$ konservatif? Jika ya, cari potensialnya.",
         r"<p>$P_y = \cos x = Q_x$. $f = y\sin x + y^2 + K$.</p>") +
      qa(r"2. $\operatorname{div}\langle x^2, y^2, z^2\rangle$", r"<p>$2x + 2y + 2z$.</p>") +
      qa(r"3. $\operatorname{curl}\langle -y, x, 0\rangle$", r"<p>$\langle 0, 0, 2\rangle$: putaran berlawanan arah jarum jam terhadap sumbu $z$.</p>"),
      "Soal 3 cocok dengan grafik pembuka: curl = 2b dengan b = 1."),
]

# ═══════════════════════════════════════════════════════════════════════════
# 9. Integral Garis & Teorema Green
# ═══════════════════════════════════════════════════════════════════════════
INTEGRAL_GARIS = [
    S("intuition", "Menjumlahkan sepanjang lintasan",
      r"""<p>Robot bergerak melewati medan gaya: berapa kerja total? Kawat melengkung dengan rapat massa berubah: berapa massanya?
      <b>Integral garis</b> menjumlahkan besaran sepanjang kurva, bukan sepanjang sumbu.</p>
      <p>Untuk medan aliran di bidang, ada dua jumlah yang berbeda di sepanjang kurva tertutup: <b>sirkulasi</b> (berapa banyak aliran menyusuri kurva)
      dan <b>fluks</b> (berapa banyak aliran menembus kurva keluar). Teorema Green menghubungkan keduanya dengan curl dan divergensi di dalam kurva.</p>""",
      "Ubah R: sirkulasi dan fluks sama-sama sebanding dengan luas lingkaran. Itulah isi Teorema Green.",
      [g("Lingkaran berjari-jari R dalam medan F = ⟨ax − by, bx + ay⟩", [-3.2, 3.2], [-3.2, 3.2],
         [param("a", "Sumber a", -1, 1, 0.1, 0.5, "a"), param("b", "Putaran b", -1, 1, 0.1, 1, "b"), param("R", "Jari-jari R", 0.5, 2.8, 0.1, 1.5, "R")],
         panah("a*{x} - b*{y}", "b*{x} + a*{y}", color="gray") +
         [{"type": "param", "x": "R*cos(t)", "y": "R*sin(t)", "t": [0, "2*pi"], "color": "red", "label": "kurva C"}],
         [readout("Sirkulasi ∮F·T ds = 2b·πR²", "2*b*pi*R*R", 4), readout("Fluks ∮F·n ds = 2a·πR²", "2*a*pi*R*R", 4)],
         "Sirkulasi = (curl) × luas; fluks = (div) × luas, karena curl dan div medan ini konstan.")]),
    S("theorem", "Dua jenis integral garis",
      r"""<p>Untuk kurva $C$: $\mathbf{r}(t)$, $a \le t \le b$:</p>
      <p>$$\int_C f\,ds = \int_a^b f(\mathbf{r}(t))\,|\mathbf{r}'(t)|\,dt \qquad\text{(skalar: massa kawat, luas tirai)}$$</p>
      <p>$$\int_C\mathbf{F}\cdot d\mathbf{r} = \int_a^b\mathbf{F}(\mathbf{r}(t))\cdot\mathbf{r}'(t)\,dt = \int_C P\,dx + Q\,dy\ (+ R\,dz) \qquad\text{(vektor: kerja, sirkulasi)}$$</p>
      <p><b>Orientasi:</b> membalik arah kurva <b>mengubah tanda</b> integral vektor, tetapi tidak mengubah integral skalar $ds$ (panjang selalu positif).</p>""",
      "Integral garis vektor mengukur seberapa 'searah' F dengan lintasan. Bergerak melawan angin memberi kerja negatif."),
    S("example", "Bedah soal: menghitung langsung",
      r"""<p><b>Soal 1.</b> Kerja $\mathbf{F} = \langle x^2, -xy\rangle$ sepanjang seperempat lingkaran $\mathbf{r}(t) = \langle\cos t, \sin t\rangle$, $0 \le t \le \tfrac{\pi}{2}$.</p>""" +
      steps(r"$\mathbf{F}(\mathbf{r}(t)) = \langle\cos^2 t, -\cos t\sin t\rangle$, $\ \mathbf{r}'(t) = \langle -\sin t, \cos t\rangle$.",
            r"$\mathbf{F}\cdot\mathbf{r}' = -\cos^2 t\sin t - \cos^2 t\sin t = -2\cos^2 t\sin t$.",
            r"$W = \displaystyle\int_0^{\pi/2}-2\cos^2 t\sin t\,dt = \left[\tfrac23\cos^3 t\right]_0^{\pi/2} = -\tfrac23$.") +
      r"""<p><b>Soal 2.</b> $\displaystyle\int_C(2 + x^2y)\,ds$, $C$ setengah lingkaran satuan atas.</p>""" +
      steps(r"$|\mathbf{r}'| = 1$, sehingga $\displaystyle\int_0^{\pi}(2 + \cos^2 t\sin t)\,dt = 2\pi + \tfrac23$."),
      "Resep integral garis selalu sama: parametrisasi, substitusi semua x, y, dx, dy dalam t, lalu integral biasa."),
    S("theorem", "Teorema dasar integral garis",
      r"""<p>Jika $\mathbf{F} = \nabla f$ (konservatif) dan $C$ dari titik $A$ ke $B$:
      $$\int_C\nabla f\cdot d\mathbf{r} = f(B) - f(A).$$</p>
      <p>Akibatnya: integral <b>tidak bergantung lintasan</b>, dan integral pada kurva <b>tertutup</b> bernilai $0$. Ini versi multivariabel dari TDK II.</p>
      <p><b>Fisika:</b> kerja gravitasi hanya bergantung pada perubahan ketinggian, bukan pada jalur seluncuran; itulah hukum kekekalan energi.</p>""",
      "Begitu tahu F konservatif, lupakan lintasannya. Cari potensial, masukkan titik akhir dan awal, selesai."),
    S("derivation", "Pohon keputusan: menghitung ∫_C F · dr",
      pohon(r"$\mathbf{F}$ konservatif (cek $P_y = Q_x$ atau curl $= \mathbf{0}$ pada domain tanpa lubang)? → cari potensial, $f(B) - f(A)$; kurva tertutup → $0$.",
            r"$C$ tertutup di bidang, mengelilingi daerah $D$ tempat $\mathbf{F}$ mulus? → <b>Teorema Green</b>.",
            r"$C$ tertutup di ruang? → <b>Teorema Stokes</b> (topik berikutnya).",
            r"Bukan semuanya? → parametrisasi tiap potongan kurva dan hitung langsung; jumlahkan potongannya.") +
      note(r"Trik gabungan: $\mathbf{F} = \nabla f + \mathbf{G}$ dengan $\mathbf{G}$ sederhana. Bagian konservatif dihitung lewat titik ujung, sisanya langsung."),
      "Cek konservatif selalu jadi langkah pertama karena paling hemat waktu bila berhasil."),
    S("theorem", "Teorema Green",
      r"""<p>Untuk kurva tertutup sederhana $C$ yang <b>berorientasi positif</b> (berlawanan arah jarum jam; daerah $D$ selalu di sebelah kiri):
      $$\oint_C P\,dx + Q\,dy = \iint_D\left(Q_x - P_y\right)dA.$$</p>
      <p><b>Intuisi:</b> bagi $D$ menjadi persegi-persegi kecil. Sirkulasi tiap persegi ≈ curl × luasnya. Di sisi yang dipakai bersama dua persegi,
      kontribusinya saling menghapus (arahnya berlawanan). Yang tersisa hanya sisi-sisi di batas luar, yaitu $\oint_C$.</p>
      <p><b>Bentuk fluks:</b> $\oint_C\mathbf{F}\cdot\mathbf{n}\,ds = \iint_D\operatorname{div}\mathbf{F}\,dA$. <b>Luas:</b> $A = \tfrac12\oint_C x\,dy - y\,dx$ (prinsip alat planimeter).</p>""",
      "Green = 'sirkulasi di batas = jumlah putaran kecil di dalam'. Kalimat yang sama berlaku untuk Stokes."),
    S("example", "Bedah soal: Teorema Green",
      r"""<p><b>Soal 1.</b> $\displaystyle\oint_C x^4\,dx + xy\,dy$, $C$ segitiga $(0, 0) \to (1, 0) \to (0, 1) \to (0, 0)$.</p>""" +
      steps(r"Arahnya berlawanan jarum jam (positif). $P = x^4$, $Q = xy$: $\ Q_x - P_y = y$.",
            r"$\displaystyle\iint_D y\,dA = \int_0^1\int_0^{1 - x}y\,dy\,dx = \int_0^1\frac{(1 - x)^2}{2}dx = \frac16$.",
            r"Bandingkan: menghitung langsung butuh tiga parametrisasi ruas garis.") +
      r"""<p><b>Soal 2.</b> Luas elips $x = a\cos t$, $y = b\sin t$ dengan $A = \tfrac12\oint x\,dy - y\,dx$.</p>""" +
      steps(r"$\tfrac12\displaystyle\int_0^{2\pi}\left(ab\cos^2 t + ab\sin^2 t\right)dt = \tfrac12\cdot 2\pi ab = \pi ab$."),
      "Green paling menguntungkan saat kurvanya terdiri dari banyak potongan tetapi Q_x − P_y sederhana."),
    S("pitfall", "Jebakan ujian",
      r"""<ul class="lesson-list">
        <li>Orientasi searah jarum jam dipakai di Green tanpa membalik tanda.</li>
        <li>Lupa $|\mathbf{r}'(t)|$ di integral skalar $ds$.</li>
        <li>Green dipakai saat $\mathbf{F}$ punya singularitas di dalam $D$ (misal di titik asal) atau kurvanya tidak tertutup.</li>
        <li>Teorema dasar dipakai pada medan yang tidak konservatif.</li>
        <li>Urutan $f(B) - f(A)$ terbalik.</li>
        <li>Tertukar $Q_x - P_y$ menjadi $P_y - Q_x$.</li>
      </ul>""",
      "Mnemonik Green: 'Q turun x, kurangi P turun y'. Huruf kedua (Q) diturunkan terhadap variabel pertama (x)."),
    S("checkpoint", "Mini checkpoint",
      qa(r"1. $\displaystyle\oint_C -y\,dx + x\,dy$, $C$ lingkaran berjari-jari $2$ berlawanan jarum jam.", r"<p>Green: $Q_x - P_y = 2$, jadi $2\cdot\pi(2)^2 = 8\pi$.</p>") +
      qa(r"2. $\displaystyle\int_C\nabla(x^2y)\cdot d\mathbf{r}$ dari $(0, 0)$ ke $(2, 1)$ lewat lintasan apa pun.", r"<p>$f(2, 1) - f(0, 0) = 4 - 0 = 4$.</p>") +
      qa(r"3. $\displaystyle\oint_C 3y\,dx + 5x\,dy$, $C$ lingkaran satuan positif.", r"<p>$Q_x - P_y = 5 - 3 = 2$, hasilnya $2\pi$.</p>"),
      "Soal 1: hasilnya 2 × luas. Itu sebabnya ½∮x dy − y dx memberi luas."),
]

# ═══════════════════════════════════════════════════════════════════════════
# 10. Integral Permukaan, Stokes & Divergensi Gauss
# ═══════════════════════════════════════════════════════════════════════════
PERMUKAAN_STOKES = [
    S("intuition", "Fluks menembus jaring",
      r"""<p>Pasang jaring di sungai: berapa liter air menembusnya per detik? Itu <b>fluks</b> melalui permukaan, dan jawabannya bergantung pada sisi mana yang
      kita sebut "depan". Memilih sisi itu disebut <b>orientasi</b>, ditentukan oleh vektor normal satuan $\mathbf{n}$. Pita Möbius hanya punya satu sisi,
      jadi tidak bisa diberi orientasi, dan fluks melaluinya tidak terdefinisi.</p>
      <p>Topik ini menutup cerita panjang kalkulus. Semua teorema besarnya berpola sama: <b>integral turunan di dalam = integral fungsi di batas</b>.</p>
      <div class="table-scroll"><table class="lesson-table"><thead><tr><th>Teorema</th><th>Di dalam</th><th>Di batas</th></tr></thead><tbody>
        <tr><td>TDK</td><td>$\int_a^b F'(x)\,dx$</td><td>$F(b) - F(a)$</td></tr>
        <tr><td>Integral garis</td><td>$\int_C\nabla f\cdot d\mathbf{r}$</td><td>$f(B) - f(A)$</td></tr>
        <tr><td>Green</td><td>$\iint_D(Q_x - P_y)\,dA$</td><td>$\oint_C P\,dx + Q\,dy$</td></tr>
        <tr><td>Stokes</td><td>$\iint_S\operatorname{curl}\mathbf{F}\cdot d\mathbf{S}$</td><td>$\oint_C\mathbf{F}\cdot d\mathbf{r}$</td></tr>
        <tr><td>Gauss</td><td>$\iiint_E\operatorname{div}\mathbf{F}\,dV$</td><td>$\oiint_S\mathbf{F}\cdot d\mathbf{S}$</td></tr>
      </tbody></table></div>""",
      "Lihat tabel ini sebagai satu teorema dalam lima dimensi. Kalau polanya dipahami, hafalannya jadi ringan."),
    S("theorem", "Permukaan parametrik & luas permukaan",
      r"""<p>Permukaan $\mathbf{r}(u, v) = \langle x(u, v), y(u, v), z(u, v)\rangle$. Vektor $\mathbf{r}_u$ dan $\mathbf{r}_v$ menyinggung permukaan;
      $\mathbf{r}_u\times\mathbf{r}_v$ tegak lurus permukaan, dan panjangnya adalah luas jajargenjang kecil (ide Jacobian yang sama dengan topik integral lipat):
      $$A(S) = \iint_D|\mathbf{r}_u\times\mathbf{r}_v|\,du\,dv.$$</p>
      <p>Untuk grafik $z = g(x, y)$: $\ dS = \sqrt{1 + g_x^2 + g_y^2}\,dA$. Untuk bola berjari-jari $a$: $|\mathbf{r}_\phi\times\mathbf{r}_\theta| = a^2\sin\phi$.</p>""",
      "Geser φ₀. Luas tudung bola = 2π(1 − cos φ₀), dihitung dari ∬ sin φ dφ dθ. Di φ₀ = π hasilnya 4π, luas bola satuan.",
      [ruang("Tudung bola satuan 0 ≤ φ ≤ φ₀", [param("p", "φ₀", 0.1, 3.14, 0.02, 1, "φ₀")],
             [{"u": [0, "pi"], "v": [0, "2*pi"], "nu": 10, "nv": 20, "x": "sin(u)*cos(v)", "y": "sin(u)*sin(v)", "z": "cos(u)", "color": "gray"},
              {"u": [0, "p"], "v": [0, "2*pi"], "nu": 10, "nv": 24, "x": "1.01*sin(u)*cos(v)", "y": "1.01*sin(u)*sin(v)", "z": "1.01*cos(u)", "color": "red"}],
             [readout("Luas tudung 2π(1 − cos φ₀)", "2*pi*(1 - cos(p))", 4), readout("Bagian dari luas bola", "(1 - cos(p))/2", 3)],
             "Archimedes sudah tahu: luas tudung sama dengan luas selimut tabung pembungkusnya.")]),
    S("theorem", "Integral permukaan & fluks",
      r"""<p><b>Skalar:</b> $\displaystyle\iint_S f\,dS = \iint_D f(\mathbf{r}(u, v))\,|\mathbf{r}_u\times\mathbf{r}_v|\,du\,dv$ (massa lembaran, muatan permukaan).</p>
      <p><b>Fluks</b> medan $\mathbf{F}$ melalui permukaan berorientasi $S$:
      $$\iint_S\mathbf{F}\cdot d\mathbf{S} = \iint_S\mathbf{F}\cdot\mathbf{n}\,dS = \iint_D\mathbf{F}(\mathbf{r}(u, v))\cdot(\mathbf{r}_u\times\mathbf{r}_v)\,du\,dv.$$</p>
      <ul class="lesson-list">
        <li>Hanya komponen normal $\mathbf{F}\cdot\mathbf{n}$ yang menembus; komponen tangensial hanya "menggeser" di sepanjang permukaan.</li>
        <li>Untuk $z = g(x, y)$ dengan normal ke atas: $\displaystyle\iint_S\mathbf{F}\cdot d\mathbf{S} = \iint_D\left(-Pg_x - Qg_y + R\right)dA$.</li>
        <li>Permukaan tertutup: konvensinya normal menunjuk <b>keluar</b>.</li>
      </ul>""",
      "Jika r_u × r_v menunjuk ke arah yang salah (misal ke dalam bola), cukup kalikan hasilnya dengan −1."),
    S("example", "Bedah soal: fluks langsung",
      r"""<p><b>Soal 1.</b> Fluks $\mathbf{F} = \langle x, y, z\rangle$ keluar dari bola $x^2 + y^2 + z^2 = a^2$.</p>""" +
      steps(r"Di bola, normal keluar $\mathbf{n} = \tfrac{\langle x, y, z\rangle}{a}$, sehingga $\mathbf{F}\cdot\mathbf{n} = \tfrac{x^2 + y^2 + z^2}{a} = a$.",
            r"Fluks $= a\cdot\text{luas} = a\cdot 4\pi a^2 = 4\pi a^3$.") +
      r"""<p><b>Soal 2.</b> Fluks $\mathbf{F} = \langle y, x, z\rangle$ ke atas melalui paraboloid $z = 1 - x^2 - y^2$, $z \ge 0$.</p>""" +
      steps(r"$g_x = -2x$, $g_y = -2y$: $-Pg_x - Qg_y + R = 2xy + 2xy + 1 - x^2 - y^2$.",
            r"Kutub di cakram satuan: $\displaystyle\int_0^{2\pi}\int_0^1\left(1 - r^2 + 4r^2\cos\theta\sin\theta\right)r\,dr\,d\theta$.",
            r"Suku $\cos\theta\sin\theta$ lenyap; sisanya $2\pi\left(\tfrac12 - \tfrac14\right) = \tfrac{\pi}{2}$."),
      "Soal 1 tidak butuh parametrisasi sama sekali: saat F·n konstan, fluks = konstanta × luas."),
    S("theorem", "Teorema Stokes",
      r"""<p>Untuk permukaan berorientasi $S$ dengan kurva batas $C$:
      $$\oint_C\mathbf{F}\cdot d\mathbf{r} = \iint_S\operatorname{curl}\mathbf{F}\cdot d\mathbf{S}.$$</p>
      <p><b>Orientasi (aturan tangan kanan):</b> ibu jari searah $\mathbf{n}$, jari-jari yang menekuk menunjukkan arah menelusuri $C$. Berjalan di tepi permukaan dengan kepala searah $\mathbf{n}$, permukaannya ada di kirimu.</p>
      <p><b>Intuisi:</b> sama seperti Green. Sirkulasi kecil di tiap keping permukaan saling menghapus di sisi bersama, tersisa sirkulasi di tepi. Akibat penting:
      fluks curl melalui <b>permukaan apa pun</b> dengan batas $C$ yang sama bernilai sama (jaring kupu-kupu boleh dalam atau dangkal).</p>""",
      "Geser h: permukaan berubah dari kubah ke cakram datar ke mangkuk terbalik, tetapi sirkulasi di tepinya tetap 2π.",
      [ruang("Permukaan berbeda, batas sama: lingkaran satuan", [param("h", "Kedalaman jaring h", -1.5, 1.5, 0.05, 1, "h")],
             [{"u": [0, 1], "v": [0, "2*pi"], "nu": 8, "nv": 24, "x": "u*cos(v)", "y": "u*sin(v)", "z": "h*(1 - u*u)", "color": "teal"},
              kurva3("cos(u)", "sin(u)", "0", 0, "2*pi", "red", 80)],
             [readout("∮ F·dr untuk F = ⟨−y, x, 0⟩", "2*pi", 4), readout("∬ curl F · dS (sama untuk setiap h)", "2*pi", 4)],
             "Lingkaran merah adalah kurva batas C. Semua permukaan teal punya C yang sama.")]),
    S("example", "Bedah soal: Teorema Stokes",
      r"""<p><b>Soal.</b> $\displaystyle\oint_C\mathbf{F}\cdot d\mathbf{r}$ untuk $\mathbf{F} = \langle -y^2, x, z^2\rangle$, $C$ perpotongan bidang $y + z = 2$ dan tabung $x^2 + y^2 = 1$, berlawanan jarum jam dilihat dari atas.</p>""" +
      steps(r"$\operatorname{curl}\mathbf{F} = \langle 0 - 0,\ 0 - 0,\ 1 + 2y\rangle = \langle 0, 0, 1 + 2y\rangle$.",
            r"Pilih permukaan paling sederhana dengan batas $C$: potongan bidang $z = 2 - y$ di atas cakram $D$: $x^2 + y^2 \le 1$, normal ke atas.",
            r"$d\mathbf{S} = \langle -g_x, -g_y, 1\rangle dA = \langle 0, 1, 1\rangle dA$, sehingga $\operatorname{curl}\mathbf{F}\cdot d\mathbf{S} = (1 + 2y)\,dA$.",
            r"$\displaystyle\iint_D(1 + 2y)\,dA = \pi + 0 = \pi$ (integral $y$ lenyap karena simetri).") +
      note(r"Menghitung langsung butuh parametrisasi elips miring $C$ dan integral yang jauh lebih panjang."),
      "Stokes membebaskanmu memilih permukaan. Pilih yang paling datar dan sederhana, biasanya potongan bidang."),
    S("theorem", "Teorema Divergensi Gauss",
      r"""<p>Untuk benda padat $E$ dengan permukaan batas tertutup $S$ berorientasi keluar:
      $$\oiint_S\mathbf{F}\cdot d\mathbf{S} = \iiint_E\operatorname{div}\mathbf{F}\,dV.$$</p>
      <p><b>Intuisi:</b> total aliran yang keluar menembus kulit benda = total "produksi" sumber di dalamnya. Kotak-kotak kecil saling bertukar fluks di sisi bersama
      (yang keluar dari satu kotak masuk ke tetangganya), tersisa fluks di kulit terluar.</p>
      <p><b>Hukum Gauss</b> di fisika: fluks medan listrik keluar dari permukaan tertutup $= \tfrac{Q_{\text{dalam}}}{\varepsilon_0}$. Muatan adalah sumber, dan divergensinya sebanding dengan rapat muatan.</p>""",
      "Gauss hanya untuk permukaan TERTUTUP. Untuk permukaan terbuka, tutup dulu dengan 'tutup' sederhana, lalu kurangi fluks tutupnya."),
    S("example", "Bedah soal: Teorema Divergensi",
      r"""<p><b>Soal 1.</b> Cek ulang Soal 1 fluks: $\mathbf{F} = \langle x, y, z\rangle$, $\operatorname{div}\mathbf{F} = 3$, sehingga fluks $= 3\cdot\tfrac43\pi a^3 = 4\pi a^3$. Cocok.</p>
      <p><b>Soal 2.</b> Fluks $\mathbf{F} = \langle xy,\ y^2 + e^{xz^2},\ \sin(xy)\rangle$ keluar dari benda yang dibatasi $z = 1 - x^2$, $z = 0$, $y = 0$, $y + z = 2$.</p>""" +
      steps(r"Menghitung langsung butuh empat permukaan dan integran $e^{xz^2}$, $\sin(xy)$ yang mengerikan. Pakai Gauss.",
            r"$\operatorname{div}\mathbf{F} = y + 2y + 0 = 3y$; suku-suku sulit lenyap.",
            r"$\displaystyle\iiint_E 3y\,dV = \int_{-1}^{1}\int_0^{1 - x^2}\int_0^{2 - z}3y\,dy\,dz\,dx = \int_{-1}^{1}\frac{8 - (1 + x^2)^3}{2}dx$.",
            r"$= \dfrac12\left[16 - \left(2 + 2 + \tfrac65 + \tfrac27\right)\right] = \dfrac{184}{35}$."),
      "Tanda kuat untuk Gauss: permukaan tertutup dan komponen F yang rumit justru tidak bergantung pada variabel turunannya."),
    S("derivation", "Pohon keputusan: teorema mana yang dipakai?",
      pohon(r"Integral garis pada kurva <b>tertutup di bidang</b>? → <b>Green</b>.",
            r"Integral garis pada kurva <b>tertutup di ruang</b>? → <b>Stokes</b>; pilih permukaan paling sederhana yang dibatasi kurva itu.",
            r"Fluks curl melalui permukaan <b>terbuka</b>? → Stokes: hitung $\oint$ di tepinya, atau ganti dengan permukaan lain bertepi sama.",
            r"Fluks melalui permukaan <b>tertutup</b>? → <b>Gauss</b>: hitung $\iiint\operatorname{div}\mathbf{F}\,dV$.",
            r"Fluks melalui permukaan terbuka, $\operatorname{div}\mathbf{F}$ sederhana? → tutup dengan permukaan datar, pakai Gauss, lalu kurangi fluks tutupnya.",
            r"Tidak ada yang cocok? → parametrisasi dan hitung langsung dengan $\mathbf{r}_u\times\mathbf{r}_v$.") ,
      "Pertanyaan pertama selalu: kurva atau permukaan? Terbuka atau tertutup? Dua jawaban itu hampir selalu menentukan teoremanya."),
    S("pitfall", "Jebakan ujian",
      r"""<ul class="lesson-list">
        <li>Orientasi: normal permukaan dan arah kurva tidak cocok dengan aturan tangan kanan, sehingga tanda terbalik.</li>
        <li>Memakai Gauss pada permukaan terbuka (misal hanya kubah tanpa alas).</li>
        <li>Lupa $|\mathbf{r}_u\times\mathbf{r}_v|$ di integral skalar, atau memakai panjangnya (bukan vektornya) di fluks.</li>
        <li>Saat menutup permukaan, tanda fluks tutup salah: normal tutup harus mengarah keluar dari benda gabungan.</li>
        <li>$\operatorname{curl}\mathbf{F}$ dihitung salah tanda di komponen tengah, sehingga seluruh fluks Stokes salah.</li>
      </ul>""",
      "Sketsa permukaan dengan satu panah normal dan satu panah arah kurva sebelum menghitung. Sepuluh detik yang menyelamatkan tanda."),
    S("checkpoint", "Mini checkpoint",
      qa(r"1. Fluks $\mathbf{F} = \langle x, y, z\rangle$ keluar dari bola berjari-jari $2$.", r"<p>Gauss: $3\cdot\tfrac43\pi(2)^3 = 32\pi$.</p>") +
      qa(r"2. $\displaystyle\iint_S\operatorname{curl}\mathbf{F}\cdot d\mathbf{S}$, $\mathbf{F} = \langle -y, x, 0\rangle$, $S$ setengah bola atas $x^2 + y^2 + z^2 = 1$ (normal keluar).",
         r"<p>Stokes: sama dengan $\oint$ di lingkaran satuan berlawanan jarum jam, yaitu $2\pi$.</p>") +
      qa(r"3. Fluks medan $\mathbf{F} = \langle y, z, x\rangle$ keluar dari permukaan tertutup apa pun.", r"<p>$\operatorname{div}\mathbf{F} = 0$, jadi fluksnya $0$.</p>"),
      "Soal 3: medan dengan divergensi nol tidak punya sumber. Yang masuk sama dengan yang keluar."),
]

CORE_SLIDES = {
    "il-ganda": INTEGRAL_LIPAT,
    "il-koordinat": SILINDER_BOLA,
    "kv-medan": MEDAN_VEKTOR,
    "kv-garis": INTEGRAL_GARIS,
}

NEW_TOPICS = [
    {"after": f"kl-{f}-{after}", "slug": f"kl-{f}-stokes-gauss", "title": "Integral Permukaan, Stokes & Divergensi Gauss", "icon": "m-flux",
     "summary": "Permukaan parametrik, fluks, orientasi, Teorema Stokes dan Teorema Divergensi Gauss.",
     "references": "Stewart §16.6–16.9; OpenStax Vol 3 §6.6–6.8"}
    for f, after in (("fm", "potensial"), ("fk", "simulasi"))
]

SLIDES = {
    "kl-ft-fluks": PERMUKAAN_STOKES,
    "kl-fm-stokes-gauss": PERMUKAAN_STOKES,
    "kl-fk-stokes-gauss": PERMUKAAN_STOKES,
}
