"""
Level Utama 1 — PreCalculus.

Sub-level  : Sistem Bilangan dan Fungsi
Sub-topik  : 9 topik, masing-masing berisi materi (LessonSection) + 5 sesi latihan
             (soal dibangkitkan oleh gamification/generators/precalc/*).

Rujukan buku (folder Downloads user):
  - Whitman Calculus (Bab 1 Analytic Geometry, §4.1, §4.6)       → kalkulus dasar & FMIPA
  - Strang, MIT Calculus (Bab 0–1, §6.1–6.4)                       → keteknikan (FT)
  - Stewart, Calculus Early Transcendentals 9e (Bab 1, Lamp. A–D)  → visual, latihan, Fasilkom
"""

from ..helpers import bullets, param, readout, table

MAIN_LEVEL = {
    "slug": "precalculus",
    "order": 1,
    "title": "PreCalculus",
    "subtitle": "Fondasi aljabar & fungsi sebelum kalkulus",
    "icon": "🧱",
}


def g(title, x, y, params, elements, readouts=None, caption=None):
    spec = {"type": "2d", "title": title, "x": x, "y": y, "params": params, "elements": elements}
    if readouts:
        spec["readouts"] = readouts
    if caption:
        spec["caption"] = caption
    return spec


def ref(*items):
    return '<p class="book-ref">📚 Rujukan: ' + " · ".join(items) + "</p>"


# ─────────────────────────────────────────────────────────────────────────────
TOPICS = [
    {
        "slug": "pre-bilangan-real",
        "title": "Sistem Bilangan Real & Interval",
        "icon": "🔢",
        "summary": "Himpunan bilangan, notasi interval, sifat eksponen & bentuk akar.",
        "references": "Stewart Lamp. A; Whitman Bab 1; Strang §0.1",
        "sections": [
            {
                "heading": "Himpunan bilangan ℕ ⊂ ℤ ⊂ ℚ ⊂ ℝ",
                "body_html": (
                    "<p>Kalkulus bekerja di himpunan <b>bilangan real ℝ</b>. Bilangan real dibangun bertahap:</p>"
                    + table(["Himpunan", "Isi", "Contoh"], [
                        ["ℕ (asli)", "bilangan untuk mencacah", "1, 2, 3, …"],
                        ["ℤ (bulat)", "ℕ, nol, dan negatifnya", "…, −2, −1, 0, 1, 2, …"],
                        ["ℚ (rasional)", "p/q dengan p, q ∈ ℤ, q ≠ 0", "−3/4, 0,25, 0,333… = 1/3"],
                        ["Irasional", "tidak dapat ditulis p/q", "√2, π, e, √3 + 1"],
                    ])
                    + "<p>Desimal bilangan rasional selalu <b>berhenti</b> atau <b>berulang</b>; desimal bilangan irasional "
                      "tidak berhenti dan tidak berulang. Contoh klasik: √2 irasional, sebab jika √2 = p/q (pecahan paling "
                      "sederhana) maka p² = 2q², sehingga p dan q sama-sama genap — kontradiksi.</p>"
                    + "<p><b>Desimal berulang → pecahan.</b> Untuk x = 0,<span style='text-decoration:overline'>27</span>: "
                      "100x − x = 27 ⇒ x = 27/99 = 3/11. Kalikan dengan 10ᵏ sesuai panjang blok yang berulang.</p>"
                    + ref("Stewart Lampiran A (Numbers)", "Whitman §1 pendahuluan", "Strang §0.1")
                ),
                "graphs": [g("Desimal 0,999… = 1? Jumlah parsial 9/10 + 9/100 + …", [0, 10], [0, 1.15],
                             [param("N", "Banyak digit 9", 1, 10, 1, 2, "N")],
                             [{"type": "fn", "expr": "1-pow(10,-floor(x))", "color": "blue", "label": "0,99…9 (N digit)"},
                              {"type": "hline", "y": 1, "color": "red", "dash": True},
                              {"type": "point", "x": "N", "y": "1-pow(10,-N)", "color": "red"}],
                             [readout("0,99…9 (N digit)", "1-pow(10,-N)", 10), readout("Selisih dengan 1", "pow(10,-N)", 10)],
                             "Selisihnya 10⁻ᴺ menuju 0, sehingga 0,999… (tak berhingga) tepat sama dengan 1.")],
            },
            {
                "heading": "Interval dan garis bilangan",
                "body_html": (
                    "<p>Himpunan bilangan real di antara dua batas ditulis sebagai <b>interval</b>. Kurung siku "
                    "<code>[ ]</code> berarti ujung termasuk (titik penuh), kurung biasa <code>( )</code> berarti tidak "
                    "termasuk (titik kosong). Tak hingga ∞ bukan bilangan, sehingga selalu memakai kurung biasa.</p>"
                    + table(["Notasi", "Himpunan", "Garis bilangan"], [
                        ["(a, b)", "{x | a &lt; x &lt; b}", "○━━━○"], ["[a, b]", "{x | a ≤ x ≤ b}", "●━━━●"],
                        ["[a, b)", "{x | a ≤ x &lt; b}", "●━━━○"], ["(a, ∞)", "{x | x &gt; a}", "○━━━━▶"],
                        ["(−∞, b]", "{x | x ≤ b}", "◀━━━━●"], ["(−∞, ∞)", "ℝ", "◀━━━━▶"],
                    ])
                    + "<p>Operasi himpunan: <b>A ∩ B</b> (irisan, “dan”), <b>A ∪ B</b> (gabungan, “atau”), "
                      "<b>A ∖ B</b> (anggota A yang bukan anggota B).</p>"
                    + ref("Stewart Lampiran A, Tabel 1 (Intervals)")
                ),
                "graphs": [g("Irisan dua interval A = [a, 2] dan B = (−1, b]", [-6, 6], [-1.5, 2.5],
                             [param("a", "Ujung kiri A", -5, 2, 0.5, -3, "a"), param("b", "Ujung kanan B", -1, 5, 0.5, 4, "b")],
                             [{"type": "segment", "x1": "a", "y1": 1.5, "x2": 2, "y2": 1.5, "color": "blue", "width": 6},
                              {"type": "segment", "x1": -1, "y1": 0.8, "x2": "b", "y2": 0.8, "color": "orange", "width": 6},
                              {"type": "segment", "x1": "max(a,-1)", "y1": 0, "x2": "min(2,b)", "y2": 0, "color": "green", "width": 8},
                              {"type": "text", "x": -5.5, "y": 1.5, "text": "A"}, {"type": "text", "x": -5.5, "y": 0.8, "text": "B"},
                              {"type": "text", "x": -5.5, "y": 0, "text": "A∩B"}],
                             [readout("Ujung kiri irisan max(a, −1)", "max(a,-1)", 2), readout("Ujung kanan irisan min(2, b)", "min(2,b)", 2)],
                             "Irisan dimulai dari ujung kiri terbesar dan berakhir di ujung kanan terkecil.")],
            },
            {
                "heading": "Eksponen dan bentuk akar",
                "body_html": (
                    bullets([
                        "aᵐ · aⁿ = aᵐ⁺ⁿ,  aᵐ / aⁿ = aᵐ⁻ⁿ,  (aᵐ)ⁿ = aᵐⁿ,  (ab)ⁿ = aⁿbⁿ",
                        "a⁰ = 1 (a ≠ 0),  a⁻ⁿ = 1/aⁿ",
                        "a<sup>p/q</sup> = (ᵠ√a)ᵖ, contoh 8<sup>2/3</sup> = (∛8)² = 4",
                        "√(ab) = √a·√b dan √(a/b) = √a/√b untuk a, b ≥ 0 — tetapi √(a + b) ≠ √a + √b!",
                    ])
                    + "<p><b>Merasionalkan penyebut:</b> kalikan dengan sekawan. "
                      "1/(√5 − 2) = (√5 + 2)/((√5)² − 2²) = √5 + 2.</p>"
                    + "<p><b>Akar bersusun:</b> √(a ± 2√b) = √p ± √q bila p + q = a dan pq = b. "
                      "Contoh √(7 + 2√10) = √5 + √2.</p>"
                    + ref("Stewart Lampiran A", "Strang §0.2 (pangkat xⁿ)")
                ),
                "graphs": [g("y = aˣ: aturan aᵐ·aⁿ = aᵐ⁺ⁿ terlihat sebagai perkalian tinggi", [-3, 4], [0, 20],
                             [param("bb", "Basis a", 1.1, 3, 0.05, 2, "a"), param("m", "m", -2, 2, 0.5, 1, "m"), param("nn", "n", -2, 2, 0.5, 1.5, "n")],
                             [{"type": "fn", "expr": "pow(bb,x)", "color": "blue", "label": "aˣ"},
                              {"type": "point", "x": "m", "y": "pow(bb,m)", "color": "orange"},
                              {"type": "point", "x": "nn", "y": "pow(bb,nn)", "color": "orange"},
                              {"type": "point", "x": "m+nn", "y": "pow(bb,m+nn)", "color": "red", "label": "aᵐ⁺ⁿ"}],
                             [readout("aᵐ · aⁿ", "pow(bb,m)*pow(bb,nn)", 4), readout("aᵐ⁺ⁿ", "pow(bb,m+nn)", 4)],
                             "Kedua nilai di tabel selalu sama, berapa pun a, m, n yang dipilih.")],
            },
        ],
    },
    {
        "slug": "pre-pertidaksamaan",
        "title": "Pertidaksamaan",
        "icon": "⚖️",
        "summary": "Aturan pertidaksamaan, linear, ganda, kuadrat, rasional, dan AM–GM.",
        "references": "Stewart Lamp. A (Inequalities); Whitman Bab 1",
        "sections": [
            {
                "heading": "Aturan dasar pertidaksamaan",
                "body_html": (
                    "<p>Untuk bilangan real a, b, c (Stewart, Rules for Inequalities):</p>"
                    + bullets([
                        "Jika a &lt; b maka a + c &lt; b + c (menambah tidak mengubah arah).",
                        "Jika a &lt; b dan c &gt; 0 maka ac &lt; bc.",
                        "Jika a &lt; b dan c &lt; 0 maka ac <b>&gt;</b> bc — <b>arah dibalik</b>.",
                        "Jika 0 &lt; a &lt; b maka 1/a &gt; 1/b.",
                    ])
                    + "<p><b>Linear:</b> 3 − 2x &lt; 7 ⇒ −2x &lt; 4 ⇒ x &gt; −2 (dibagi −2, tanda dibalik) ⇒ (−2, ∞).</p>"
                    + "<p><b>Ganda:</b> −1 ≤ 2x + 3 &lt; 9 ⇒ −4 ≤ 2x &lt; 6 ⇒ −2 ≤ x &lt; 3 ⇒ [−2, 3).</p>"
                    + ref("Stewart Lampiran A (Inequalities)")
                ),
                "graphs": [g("Mengalikan dengan c membalik urutan bila c < 0", [-10, 10], [-1, 3],
                             [param("c", "Pengali c", -3, 3, 0.25, -1, "c")],
                             [{"type": "point", "x": -2, "y": 2, "color": "blue", "label": "a = −2"},
                              {"type": "point", "x": 4, "y": 2, "color": "orange", "label": "b = 4"},
                              {"type": "point", "x": "-2*c", "y": 0.7, "color": "blue", "label": "ac"},
                              {"type": "point", "x": "4*c", "y": 0.7, "color": "orange", "label": "bc"}],
                             [readout("ac", "-2*c", 2), readout("bc", "4*c", 2)],
                             "Saat c negatif, titik biru (ac) berpindah ke kanan titik oranye (bc): tanda < berubah menjadi >.")],
            },
            {
                "heading": "Kuadrat & rasional: metode garis bilangan tanda",
                "body_html": (
                    "<ol class='lesson-list'><li>Pindahkan semua suku ke satu ruas: P(x)/Q(x) ⋚ 0.</li>"
                    "<li>Cari titik kritis: akar pembilang dan akar penyebut.</li>"
                    "<li>Uji tanda di setiap selang (cukup satu titik uji per selang).</li>"
                    "<li>Pilih selang sesuai tanda. Akar penyebut <b>tidak pernah</b> ikut; akar pembilang ikut bila ≤ atau ≥.</li></ol>"
                    + "<p>Contoh: x² − x − 6 ≤ 0 ⇒ (x − 3)(x + 2) ≤ 0 ⇒ [−2, 3]. "
                      "Contoh rasional: (x − 1)/(x + 2) ≥ 0 ⇒ (−∞, −2) ∪ [1, ∞).</p>"
                    + "<p class='lesson-note'>⚠️ Jangan mengalikan silang dengan penyebut yang tandanya belum diketahui.</p>"
                ),
                "graphs": [g("Tanda (x − r₁)(x − r₂): positif di luar akar, negatif di antara", [-8, 8], [-15, 20],
                             [param("r1", "Akar r₁", -6, 6, 0.5, -2, "r₁"), param("r2", "Akar r₂", -6, 6, 0.5, 3, "r₂")],
                             [{"type": "fn", "expr": "(x-r1)*(x-r2)", "color": "blue", "label": "(x − r₁)(x − r₂)"},
                              {"type": "vband", "from": "min(r1,r2)", "to": "max(r1,r2)", "color": "red"},
                              {"type": "hline", "y": 0, "color": "gray"}],
                             [readout("Lebar daerah negatif", "abs(r2-r1)", 2)],
                             "Daerah merah = penyelesaian ≤ 0. Jika r₁ = r₂, daerah negatif lenyap (kuadrat sempurna ≥ 0).")],
            },
            {
                "heading": "Ketaksamaan AM–GM",
                "body_html": (
                    "<p>Untuk a, b ≥ 0: <b>(a + b)/2 ≥ √(ab)</b>, kesamaan saat a = b. Akibatnya untuk x &gt; 0, "
                    "x + 1/x ≥ 2. Ketaksamaan ini sering dipakai pada soal optimasi tingkat olimpiade sebelum mengenal turunan.</p>"
                ),
                "graphs": [g("Rata-rata aritmetika vs geometri", [0, 10], [0, 10],
                             [param("b", "b (a = 4 tetap)", 0, 10, 0.1, 9, "b")],
                             [{"type": "bar", "x": 3, "w": 1.2, "h": "(4+b)/2", "color": "blue"},
                              {"type": "bar", "x": 6, "w": 1.2, "h": "sqrt(4*b)", "color": "orange"},
                              {"type": "text", "x": 3, "y": 0.4, "text": "AM"}, {"type": "text", "x": 6, "y": 0.4, "text": "GM"}],
                             [readout("AM (a+b)/2", "(4+b)/2", 3), readout("GM √(ab)", "sqrt(4*b)", 3)],
                             "Batang AM selalu setinggi atau lebih tinggi dari GM; sama tinggi tepat saat b = 4.")],
            },
        ],
    },
    {
        "slug": "pre-nilai-mutlak",
        "title": "Nilai Mutlak",
        "icon": "📏",
        "summary": "Nilai mutlak sebagai jarak, persamaan & pertidaksamaan nilai mutlak, ketaksamaan segitiga.",
        "references": "Stewart Lamp. A (Absolute Value); Whitman Bab 1",
        "sections": [
            {
                "heading": "Definisi: nilai mutlak adalah jarak",
                "body_html": (
                    "<p>|a| = a jika a ≥ 0, dan |a| = −a jika a &lt; 0. Secara geometri |a| adalah jarak a ke 0, "
                    "dan <b>|a − b| adalah jarak antara a dan b</b> di garis bilangan.</p>"
                    + bullets(["|ab| = |a||b|,  |a/b| = |a|/|b|", "√(a²) = |a| (bukan a!)",
                               "Ketaksamaan segitiga: |a + b| ≤ |a| + |b|"])
                    + ref("Stewart Lampiran A, Properties of Absolute Values")
                ),
                "graphs": [g("y = |x − a|: grafik berbentuk V dengan titik sudut di x = a", [-8, 8], [-1, 10],
                             [param("a", "Pusat a", -5, 5, 0.5, 2, "a"), param("k", "Kemiringan k", 0.5, 3, 0.25, 1, "k")],
                             [{"type": "fn", "expr": "k*abs(x-a)", "color": "blue", "label": "k|x − a|"},
                              {"type": "point", "x": "a", "y": 0, "color": "red"}],
                             None, "Geser a: titik sudut V berpindah. Geser k: V makin curam atau landai.")],
            },
            {
                "heading": "Persamaan & pertidaksamaan nilai mutlak",
                "body_html": (
                    table(["Bentuk (r > 0)", "Setara dengan", "Penyelesaian"], [
                        ["|x − a| = r", "x − a = r atau x − a = −r", "x = a ± r"],
                        ["|x − a| &lt; r", "−r &lt; x − a &lt; r", "(a − r, a + r)"],
                        ["|x − a| &gt; r", "x − a &gt; r atau x − a &lt; −r", "(−∞, a − r) ∪ (a + r, ∞)"],
                    ])
                    + "<p>Bacaan geometris: |x − 3| &lt; 2 artinya “x berjarak kurang dari 2 dari 3”, yaitu (1, 5).</p>"
                    + "<p>Konsep ini dipakai langsung di definisi limit ε–δ: |f(x) − L| &lt; ε setiap kali 0 &lt; |x − c| &lt; δ.</p>"
                ),
                "graphs": [g("|x − a| < r: semua x dalam jarak r dari a", [-8, 8], [-1, 8],
                             [param("a", "Pusat a", -4, 4, 0.5, 1, "a"), param("r", "Jari-jari r", 0, 6, 0.25, 2, "r")],
                             [{"type": "fn", "expr": "abs(x-a)", "color": "blue", "label": "|x − a|"},
                              {"type": "hline", "y": "r", "color": "red", "dash": True},
                              {"type": "vband", "from": "a-r", "to": "a+r", "color": "green"}],
                             [readout("a − r", "a-r", 2), readout("a + r", "a+r", 2)],
                             "Daerah hijau = penyelesaian |x − a| < r.")],
            },
        ],
    },
    {
        "slug": "pre-konsep-fungsi",
        "title": "Konsep Fungsi",
        "icon": "🧩",
        "summary": "Definisi fungsi, domain & range, komposisi, invers, transformasi, fungsi genap/ganjil.",
        "references": "Stewart §1.1, §1.3, §1.5; Whitman §1.3–1.4; Strang §4.3",
        "sections": [
            {
                "heading": "Fungsi, domain, dan range",
                "body_html": (
                    "<p><b>Fungsi</b> f adalah aturan yang memasangkan setiap x di domain D dengan <b>tepat satu</b> f(x). "
                    "Range adalah himpunan semua nilai f(x). Fungsi dapat disajikan secara verbal, numerik (tabel), "
                    "visual (grafik), dan aljabar (rumus) — empat cara representasi Stewart §1.1.</p>"
                    + bullets(["<b>Uji garis vertikal:</b> kurva adalah grafik fungsi bila tiap garis tegak memotongnya paling banyak sekali.",
                               "<b>Domain alami:</b> buang x yang membuat penyebut 0 atau bilangan di bawah akar genap negatif.",
                               "Contoh: f(x) = √(4 − x²) ⇒ D = [−2, 2], range = [0, 2]."])
                    + ref("Stewart §1.1", "Whitman §1.3")
                ),
                "graphs": [g("Uji garis vertikal pada lingkaran vs setengah lingkaran", [-3, 3], [-3, 3],
                             [param("s", "Posisi garis tegak x = s", -2.5, 2.5, 0.05, 0.8, "s")],
                             [{"type": "param", "t": [0, "2*pi"], "x": "2*cos(t)", "y": "2*sin(t)", "color": "gray"},
                              {"type": "fn", "expr": "sqrt(4-x*x)", "color": "blue", "label": "y = √(4 − x²)"},
                              {"type": "vline", "x": "s", "color": "red", "dash": True}],
                             [readout("Titik potong dengan lingkaran", "abs(s)<2?2:(abs(s)==2?1:0)", 0)],
                             "Lingkaran penuh dipotong 2 kali → bukan fungsi. Setengah lingkaran atas (biru) dipotong sekali → fungsi.")],
            },
            {
                "heading": "Komposisi dan invers",
                "body_html": (
                    "<p><b>Komposisi</b> (f ∘ g)(x) = f(g(x)): kerjakan g dulu, hasilnya dimasukkan ke f. Umumnya f ∘ g ≠ g ∘ f.</p>"
                    "<p><b>Invers</b> f⁻¹ ada bila f satu-satu (lolos <b>uji garis horizontal</b>). f⁻¹(y) = x ⇔ f(x) = y, "
                    "sehingga f(f⁻¹(x)) = x. Grafik f⁻¹ adalah cerminan grafik f terhadap garis y = x.</p>"
                    "<p>Cara mencari: tulis y = f(x), selesaikan untuk x, lalu tukar x ↔ y. Contoh f(x) = (2x + 1)/(x − 3) ⇒ "
                    "f⁻¹(x) = (3x + 1)/(x − 2).</p>" + ref("Stewart §1.3, §1.5", "Strang §4.3")
                ),
                "graphs": [g("Cerminan terhadap y = x", [-4, 6], [-4, 6],
                             [param("m", "Gradien f(x) = mx + 1", 0.25, 4, 0.05, 2, "m")],
                             [{"type": "fn", "expr": "m*x+1", "color": "blue", "label": "f"},
                              {"type": "fn", "expr": "(x-1)/m", "color": "orange", "label": "f⁻¹"},
                              {"type": "fn", "expr": "x", "color": "gray", "dash": True, "label": "y = x"}],
                             [readout("gradien f", "m", 3), readout("gradien f⁻¹ = 1/m", "1/m", 3)],
                             "Gradien invers adalah kebalikan gradien f — cikal bakal rumus turunan fungsi invers.")],
            },
            {
                "heading": "Transformasi grafik & simetri",
                "body_html": (
                    table(["Bentuk", "Efek pada grafik y = f(x)"], [
                        ["y = f(x − h)", "geser h ke kanan (h &gt; 0)"], ["y = f(x) + k", "geser k ke atas"],
                        ["y = a·f(x)", "regang vertikal |a|; dicerminkan terhadap sumbu x bila a &lt; 0"],
                        ["y = f(bx)", "mampat horizontal faktor b"], ["y = f(−x)", "cermin terhadap sumbu y"],
                    ])
                    + "<p><b>Genap:</b> f(−x) = f(x), simetris sumbu y (x², cos x). <b>Ganjil:</b> f(−x) = −f(x), "
                      "simetris titik asal (x³, sin x).</p>" + ref("Whitman §1.4 Shifts and Dilations", "Stewart §1.3")
                ),
                "graphs": [g("y = a·(x − h)² + k", [-8, 8], [-8, 10],
                             [param("a", "a", -3, 3, 0.25, 1, "a"), param("h", "h", -5, 5, 0.5, 2, "h"), param("k", "k", -5, 5, 0.5, -1, "k")],
                             [{"type": "fn", "expr": "x*x", "color": "gray", "dash": True, "label": "y = x²"},
                              {"type": "fn", "expr": "a*(x-h)**2+k", "color": "blue", "label": "hasil"},
                              {"type": "point", "x": "h", "y": "k", "color": "red"}],
                             None, "Geser satu slider pada satu waktu untuk melihat efek setiap transformasi.")],
            },
        ],
    },
    {
        "slug": "pre-fungsi-linear",
        "title": "Fungsi Linear",
        "icon": "📈",
        "summary": "Gradien, persamaan garis, sejajar & tegak lurus, titik potong, jarak titik ke garis.",
        "references": "Whitman §1.1–1.2; Stewart Lamp. B; Strang §1.1",
        "sections": [
            {
                "heading": "Gradien dan bentuk persamaan garis",
                "body_html": (
                    "<p>Gradien (kemiringan) garis melalui (x₁, y₁) dan (x₂, y₂): <b>m = Δy/Δx = (y₂ − y₁)/(x₂ − x₁)</b>. "
                    "Gradien adalah laju perubahan y terhadap x — gagasan yang nanti menjadi <b>turunan</b> (Strang §1.1: "
                    "kecepatan = kemiringan grafik jarak).</p>"
                    + table(["Bentuk", "Persamaan", "Kapan dipakai"], [
                        ["Gradien–titik potong", "y = mx + c", "m dan titik potong sumbu-y diketahui"],
                        ["Titik–gradien", "y − y₁ = m(x − x₁)", "m dan satu titik diketahui"],
                        ["Umum", "ax + by + c = 0", "termasuk garis tegak (b = 0)"],
                    ]) + ref("Whitman §1.1 Lines", "Strang §1.1")
                ),
                "graphs": [g("y = mx + c", [-10, 10], [-10, 10],
                             [param("m", "Gradien m", -5, 5, 0.25, 1.5, "m"), param("c", "Titik potong c", -8, 8, 0.5, -2, "c")],
                             [{"type": "fn", "expr": "m*x+c", "color": "blue", "label": "y = mx + c"},
                              {"type": "point", "x": 0, "y": "c", "color": "red", "label": "(0, c)"},
                              {"type": "segment", "x1": 0, "y1": "c", "x2": 1, "y2": "c", "color": "orange", "dash": True},
                              {"type": "segment", "x1": 1, "y1": "c", "x2": 1, "y2": "m+c", "color": "green", "dash": True}],
                             [readout("Naik per 1 langkah ke kanan", "m", 3), readout("Titik potong sumbu-x", "-c/m", 3)],
                             "Segitiga oranye–hijau: maju 1 satuan, naik m satuan.")],
            },
            {
                "heading": "Sejajar, tegak lurus, dan jarak",
                "body_html": (
                    bullets(["Sejajar: m₁ = m₂.", "Tegak lurus: m₁ · m₂ = −1 (gradien saling negatif-kebalikan).",
                             "Jarak dua titik: d = √((x₂ − x₁)² + (y₂ − y₁)²) (Pythagoras).",
                             "Jarak titik (x₀, y₀) ke garis ax + by + c = 0: d = |ax₀ + by₀ + c| / √(a² + b²)."])
                    + "<p><b>Aplikasi:</b> penyusutan linear aset mesin (FT), biaya tetap + biaya per unit (ekonomi), "
                      "waktu eksekusi algoritma O(n) (Fasilkom).</p>" + ref("Whitman §1.2 Distance Between Two Points", "Stewart Lamp. B")
                ),
                "graphs": [g("Garis tegak lurus melalui titik asal", [-6, 6], [-6, 6],
                             [param("m", "Gradien garis biru", -4, 4, 0.1, 0.5, "m")],
                             [{"type": "fn", "expr": "m*x", "color": "blue", "label": "y = mx"},
                              {"type": "fn", "expr": "-x/m", "color": "orange", "label": "y = −x/m"}],
                             [readout("m₁ · m₂", "m*(-1/m)", 3)], "Hasil kali gradien selalu −1: sudut di antara keduanya 90°.")],
            },
        ],
    },
    {
        "slug": "pre-fungsi-kuadrat",
        "title": "Fungsi Kuadrat",
        "icon": "⛰️",
        "summary": "Bentuk umum/puncak/faktor, diskriminan, rumus Vieta, optimasi kuadrat.",
        "references": "Stewart Lamp. C & §1.2; Whitman §1.4; Strang §0.2",
        "sections": [
            {
                "heading": "Tiga bentuk fungsi kuadrat",
                "body_html": (
                    table(["Bentuk", "Rumus", "Informasi langsung"], [
                        ["Umum", "y = ax² + bx + c", "titik potong sumbu-y (0, c); arah buka dari tanda a"],
                        ["Puncak", "y = a(x − h)² + k", "puncak (h, k), sumbu simetri x = h"],
                        ["Faktor", "y = a(x − x₁)(x − x₂)", "akar x₁, x₂"],
                    ])
                    + "<p>Melengkapkan kuadrat mengubah bentuk umum ke bentuk puncak: h = −b/(2a), k = f(h). "
                      "Rumus abc: x = (−b ± √D)/(2a) dengan <b>D = b² − 4ac</b>.</p>"
                ),
                "graphs": [g("y = ax² + bx + c", [-10, 10], [-15, 15],
                             [param("a", "a", -3, 3, 0.25, 1, "a"), param("b", "b", -10, 10, 0.5, -2, "b"), param("c", "c", -12, 12, 0.5, -3, "c")],
                             [{"type": "fn", "expr": "a*x*x+b*x+c", "color": "blue", "label": "y"},
                              {"type": "point", "x": "-b/(2*a)", "y": "c-b*b/(4*a)", "color": "red", "label": "puncak"},
                              {"type": "hline", "y": 0, "color": "gray"}],
                             [readout("D = b² − 4ac", "b*b-4*a*c", 3), readout("Puncak x", "-b/(2*a)", 3), readout("Puncak y", "c-b*b/(4*a)", 3)],
                             "D > 0: dua akar, D = 0: menyinggung, D < 0: tidak memotong sumbu-x.")],
            },
            {
                "heading": "Vieta dan optimasi",
                "body_html": (
                    "<p><b>Rumus Vieta:</b> x₁ + x₂ = −b/a, x₁x₂ = c/a. Berguna untuk menghitung x₁² + x₂² = (x₁ + x₂)² − 2x₁x₂ "
                    "tanpa mencari akar.</p>"
                    "<p><b>Optimasi:</b> nilai maksimum/minimum fungsi kuadrat ada di puncak. Contoh MIT/Strang: bola dilempar "
                    "h(t) = v₀t − 5t² mencapai puncak pada t = v₀/10 dengan tinggi v₀²/20. Contoh Stewart: pagar keliling L "
                    "memberi luas maksimum saat persegi panjang menjadi persegi.</p>" + ref("Strang §0.2", "Stewart §1.2")
                ),
                "graphs": [g("Luas persegi panjang dengan keliling 40", [0, 20], [0, 120],
                             [param("p", "Panjang p", 0, 20, 0.25, 6, "p")],
                             [{"type": "fn", "expr": "x*(20-x)", "color": "blue", "label": "A(p) = p(20 − p)"},
                              {"type": "point", "x": "p", "y": "p*(20-p)", "color": "red"}],
                             [readout("Lebar 20 − p", "20-p", 2), readout("Luas", "p*(20-p)", 2)],
                             "Luas maksimum 100 tercapai di p = 10 (persegi).")],
            },
        ],
    },
    {
        "slug": "pre-fungsi-trigonometri",
        "title": "Fungsi Trigonometri",
        "icon": "🌊",
        "summary": "Radian, lingkaran satuan, sudut istimewa, identitas, grafik sinusoidal, persamaan trigonometri.",
        "references": "Stewart Lamp. D; Strang §1.4–1.5; Whitman §4.1",
        "sections": [
            {
                "heading": "Radian dan lingkaran satuan",
                "body_html": (
                    "<p>Dalam kalkulus sudut <b>selalu</b> diukur dalam radian: θ radian = panjang busur pada lingkaran berjari-jari 1. "
                    "π rad = 180°. Titik pada lingkaran satuan di sudut θ adalah (cos θ, sin θ) (Strang §1.4: gerak melingkar).</p>"
                    + table(["θ", "0", "π/6", "π/4", "π/3", "π/2"], [
                        ["sin θ", "0", "1/2", "√2/2", "√3/2", "1"], ["cos θ", "1", "√3/2", "√2/2", "1/2", "0"],
                        ["tan θ", "0", "√3/3", "1", "√3", "—"]])
                    + "<p>Tanda per kuadran: I semua positif, II hanya sin, III hanya tan, IV hanya cos.</p>"
                    + ref("Stewart Lampiran D", "Strang §1.4 Circular Motion")
                ),
                "graphs": [g("Lingkaran satuan", [-1.6, 1.6], [-1.3, 1.3],
                             [param("th", "θ (radian)", 0, 6.283, 0.01, 0.785, "θ")],
                             [{"type": "param", "t": [0, "2*pi"], "x": "cos(t)", "y": "sin(t)", "color": "gray"},
                              {"type": "segment", "x1": 0, "y1": 0, "x2": "cos(th)", "y2": "sin(th)", "color": "blue"},
                              {"type": "segment", "x1": "cos(th)", "y1": 0, "x2": "cos(th)", "y2": "sin(th)", "color": "red", "dash": True},
                              {"type": "segment", "x1": 0, "y1": 0, "x2": "cos(th)", "y2": 0, "color": "green", "dash": True},
                              {"type": "point", "x": "cos(th)", "y": "sin(th)", "color": "red"}],
                             [readout("θ dalam derajat", "th*180/pi", 2), readout("sin θ (merah)", "sin(th)", 4), readout("cos θ (hijau)", "cos(th)", 4)],
                             "Geser θ: sin θ = tinggi titik, cos θ = jarak mendatarnya.")],
            },
            {
                "heading": "Identitas dan grafik sinusoidal",
                "body_html": (
                    bullets(["sin²θ + cos²θ = 1;  1 + tan²θ = sec²θ", "sin(−θ) = −sin θ (ganjil), cos(−θ) = cos θ (genap)",
                             "sin(A ± B) = sin A cos B ± cos A sin B;  sin 2θ = 2 sin θ cos θ",
                             "a sin x + b cos x = R sin(x + φ), R = √(a² + b²)"])
                    + "<p>Grafik y = A sin(Bx + C) + D: amplitudo |A|, periode 2π/|B|, geser fase −C/B, garis tengah y = D. "
                      "Model getaran pegas & arus AC (FT), gelombang suara & sinyal (Fasilkom).</p>"
                    + ref("Strang §1.5 A Review of Trigonometry", "Stewart Lamp. D")
                ),
                "graphs": [g("y = A sin(Bx + C) + D", [-6.3, 6.3], [-6, 6],
                             [param("A", "Amplitudo A", -4, 4, 0.25, 2, "A"), param("B", "Frekuensi B", 0.25, 4, 0.25, 1, "B"),
                              param("C", "Fase C", -3.14, 3.14, 0.05, 0, "C"), param("D", "Geser D", -3, 3, 0.25, 0, "D")],
                             [{"type": "fn", "expr": "sin(x)", "color": "gray", "dash": True, "label": "sin x"},
                              {"type": "fn", "expr": "A*sin(B*x+C)+D", "color": "blue", "label": "y"}],
                             [readout("Periode 2π/B", "2*pi/B", 4), readout("Maks", "D+abs(A)", 3), readout("Min", "D-abs(A)", 3)],
                             "Bandingkan dengan sin x (abu-abu) sambil menggeser setiap parameter.")],
            },
        ],
    },
    {
        "slug": "pre-fungsi-eksponensial",
        "title": "Fungsi Eksponensial",
        "icon": "🚀",
        "summary": "Fungsi bˣ, bilangan e, grafik & asimtot, persamaan/pertidaksamaan, pertumbuhan & peluruhan.",
        "references": "Stewart §1.4; Strang §6.1–6.3; Whitman §4.6",
        "sections": [
            {
                "heading": "Fungsi f(x) = bˣ dan bilangan e",
                "body_html": (
                    "<p>Untuk b &gt; 0, b ≠ 1, fungsi eksponensial f(x) = bˣ memiliki domain ℝ, range (0, ∞), melalui (0, 1), "
                    "naik bila b &gt; 1 dan turun bila 0 &lt; b &lt; 1, dengan asimtot datar y = 0.</p>"
                    "<p>Bilangan istimewa <b>e ≈ 2,71828</b> = lim (1 + 1/n)ⁿ. Fungsi eˣ adalah satu-satunya fungsi eksponensial "
                    "yang kemiringannya di setiap titik sama dengan nilainya (Strang §6.2) — inilah alasan e dipakai di kalkulus.</p>"
                    + ref("Stewart §1.4 Exponential Functions", "Strang §6.2 The Exponential eˣ")
                ),
                "graphs": [g("(1 + 1/n)ⁿ menuju e", [1, 60], [1.8, 2.9],
                             [param("N", "n", 1, 60, 1, 5, "n")],
                             [{"type": "fn", "expr": "pow(1+1/x,x)", "color": "blue", "label": "(1 + 1/n)ⁿ"},
                              {"type": "hline", "y": "e", "color": "red", "dash": True},
                              {"type": "point", "x": "N", "y": "pow(1+1/N,N)", "color": "red"}],
                             [readout("(1 + 1/n)ⁿ", "pow(1+1/N,N)", 6), readout("e", "e", 6)],
                             "Bunga majemuk n kali per tahun dengan bunga 100% → faktor (1 + 1/n)ⁿ, mendekati e.")],
            },
            {
                "heading": "Persamaan eksponensial dan model pertumbuhan",
                "body_html": (
                    "<p><b>Samakan basis:</b> 4ˣ = 8ˣ⁻¹ ⇒ 2²ˣ = 2³ˣ⁻³ ⇒ x = 3. <b>Substitusi:</b> 4ˣ − 3·2ˣ + 2 = 0, misal u = 2ˣ &gt; 0.</p>"
                    "<p><b>Pertidaksamaan:</b> basis &gt; 1 tanda tetap; basis 0–1 tanda dibalik.</p>"
                    "<p><b>Model:</b> N(t) = N₀·2^(t/T) (penggandaan, bakteri FMIPA), m(t) = m₀(1/2)^(t/h) (waktu paruh), "
                    "A = P(1 + r)ᵗ (bunga majemuk). Laju perubahan sebanding dengan besarannya: y′ = ky (Strang §6.3).</p>"
                ),
                "graphs": [g("Pertumbuhan & peluruhan: y = y₀·eᵏᵗ", [0, 10], [0, 20],
                             [param("y0", "y₀", 0.5, 10, 0.5, 2, "y₀"), param("k", "Laju k", -1, 1, 0.05, 0.3, "k")],
                             [{"type": "fn", "expr": "y0*exp(k*x)", "color": "blue", "label": "y₀eᵏᵗ"}],
                             [readout("Waktu ganda/paruh ln2/|k|", "log(2)/abs(k)", 3)],
                             "k > 0 tumbuh, k < 0 meluruh. Waktu penggandaan tidak bergantung pada y₀.")],
            },
        ],
    },
    {
        "slug": "pre-fungsi-logaritma",
        "title": "Fungsi Logaritma",
        "icon": "🔁",
        "summary": "Logaritma sebagai invers eksponen, sifat, ganti basis, persamaan/pertidaksamaan, aplikasi pH & bit.",
        "references": "Stewart §1.5; Strang §6.4; Whitman §4.6",
        "sections": [
            {
                "heading": "Logaritma: invers fungsi eksponensial",
                "body_html": (
                    "<p>log_b x = y ⇔ bʸ = x (b &gt; 0, b ≠ 1, x &gt; 0). Fungsi log_b x adalah invers bˣ: domain (0, ∞), "
                    "range ℝ, asimtot tegak x = 0. Logaritma natural ln x = logₑ x.</p>"
                    + table(["Sifat", "Rumus"], [
                        ["Perkalian", "log(xy) = log x + log y"], ["Pembagian", "log(x/y) = log x − log y"],
                        ["Pangkat", "log(xʳ) = r log x"], ["Ganti basis", "log_b x = (ln x)/(ln b)"],
                        ["Invers", "b^(log_b x) = x,  log_b(bˣ) = x"]])
                    + ref("Stewart §1.5 Inverse Functions and Logarithms", "Strang §6.4 Logarithms")
                ),
                "graphs": [g("bˣ dan log_b x bercermin terhadap y = x", [-4, 8], [-4, 8],
                             [param("b", "Basis b", 1.2, 6, 0.1, 2, "b")],
                             [{"type": "fn", "expr": "pow(b,x)", "color": "orange", "label": "bˣ"},
                              {"type": "fn", "expr": "log(x)/log(b)", "color": "blue", "label": "log_b x", "from": 0.01},
                              {"type": "fn", "expr": "x", "color": "gray", "dash": True}],
                             [readout("log_b 8", "log(8)/log(b)", 4)], "Basis makin besar → logaritma makin landai.")],
            },
            {
                "heading": "Persamaan logaritma & aplikasi",
                "body_html": (
                    "<p>Langkah aman: (1) tulis syarat numerus &gt; 0, (2) gabungkan dengan sifat log, (3) ubah ke bentuk "
                    "eksponen, (4) <b>cek</b> setiap akar terhadap syarat.</p>"
                    "<p><b>Aplikasi:</b> pH = −log[H⁺] (kimia, FMIPA); desibel 10 log(I/I₀) (akustik, FT); jumlah bit "
                    "⌈log₂ N⌉ dan binary search O(log n) (Fasilkom). Logaritma tumbuh sangat lambat: log₂(10⁶) ≈ 20.</p>"
                ),
                "graphs": [g("n vs log₂ n: mengapa O(log n) sangat cepat", [1, 1024], [0, 60],
                             [param("N", "Ukuran data n", 1, 1024, 1, 256, "n")],
                             [{"type": "fn", "expr": "log2(x)", "color": "blue", "label": "log₂ n"},
                              {"type": "fn", "expr": "x/20", "color": "orange", "dash": True, "label": "n/20"},
                              {"type": "point", "x": "N", "y": "log2(N)", "color": "red"}],
                             [readout("log₂ n (langkah binary search)", "log2(N)", 3)],
                             "Menggandakan data hanya menambah satu langkah pencarian biner.")],
            },
        ],
    },
]

SUBLEVELS = [
    {
        "slug": "pre-sistem-bilangan-fungsi",
        "title": "Sistem Bilangan dan Fungsi",
        "subtitle": "Pertidaksamaan, nilai mutlak, dan jenis-jenis fungsi",
        "icon": "🧮",
        "badge_label": "PreCalculus",
        "summary_html": "<p>Fondasi aljabar sebelum limit: bilangan real, pertidaksamaan, nilai mutlak, dan fungsi "
                        "linear, kuadrat, trigonometri, eksponensial, serta logaritma.</p>",
        "topics": TOPICS,
    },
]
