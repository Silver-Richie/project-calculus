"""
Level Utama 2 — Kalkulus Dasar.

Sub-level (masing-masing 5 topik × 5 sesi; soal dari gamification/generators/dasar/*):
  1. Limit dan Kekontinuan        2. Turunan (Diferensial)
  3. Aplikasi Turunan             4. Integral Tentu & Tak Tentu

Konten lama berkas 1 & 3 (node umum-limit/umum-turunan/umum-integral) digabungkan
ke topik yang sesuai lewat ABSORB_SECTIONS dan FIXED_QUESTIONS (lihat seed_gamification).
Rujukan: Whitman (dasar/FMIPA), Strang MIT (FT), Stewart Early Transcendentals (visual/Fasilkom).
"""

from ..helpers import antiderivative_family, area_graph, bullets, limit_graph, param, readout, table, tangent_graph
from .l1_precalculus import g, ref

MAIN_LEVEL = {"slug": "kalkulus-dasar", "order": 2, "title": "Kalkulus Dasar",
              "subtitle": "Limit, turunan, aplikasi turunan, integral", "icon": "📐"}


def T(slug, title, icon, summary, references, sections):
    return {"slug": slug, "title": title, "icon": icon, "summary": summary, "references": references, "sections": sections}


def S(heading, body, graphs=None):
    return {"heading": heading, "body_html": body, "graphs": graphs or []}


# ═════════════════════════ Sub-level 1: Limit dan Kekontinuan ════════════════
LIMIT = [
    T("kd-lim-konsep", "Konsep Limit & Limit Sepihak", "🎯", "Makna limit, limit kiri/kanan, hukum limit.",
      "Stewart §2.2–2.3; Whitman §2.3; Strang §2.6", [
          S("Apa arti lim f(x) = L?",
            "<p>lim<sub>x→c</sub> f(x) = L berarti nilai f(x) dapat dibuat <b>sedekat mungkin</b> dengan L dengan mengambil x cukup dekat "
            "dengan c (x ≠ c). Nilai f(c) sendiri tidak berpengaruh — bahkan f boleh tidak terdefinisi di c.</p>"
            + bullets(["<b>Limit kiri</b> lim<sub>x→c⁻</sub>: x mendekat dari nilai lebih kecil.", "<b>Limit kanan</b> lim<sub>x→c⁺</sub>: dari nilai lebih besar.",
                       "lim f(x) ada ⇔ limit kiri = limit kanan."])
            + ref("Stewart §2.2 The Limit of a Function", "Whitman §2.3 Limits"),
            [limit_graph("f(x) = (x² − 1)/(x − 1) mendekati 2", "(x*x-1)/(x-1)", "1", "2", [-2, 4], [-1, 5])]),
          S("Hukum limit",
            table(["Hukum", "Rumus (jika lim f = A, lim g = B)"], [["Jumlah", "lim (f ± g) = A ± B"], ["Konstanta", "lim cf = cA"],
                                                                   ["Perkalian", "lim fg = AB"], ["Pembagian", "lim f/g = A/B, B ≠ 0"],
                                                                   ["Pangkat/akar", "lim fⁿ = Aⁿ, lim ⁿ√f = ⁿ√A"]])
            + "<p>Untuk polinom dan fungsi rasional (penyebut ≠ 0) limit = substitusi langsung.</p>"),
      ]),
    T("kd-lim-aljabar", "Teknik Aljabar Bentuk 0/0", "🧮", "Faktorisasi, kalikan sekawan, pecahan bersusun.",
      "Stewart §2.3; Whitman §2.3", [
          S("Bentuk tak tentu 0/0",
            "<p>Jika substitusi menghasilkan 0/0, limit <b>belum diketahui</b>. Sederhanakan dulu:</p>"
            + bullets(["<b>Faktorkan</b>: (x² − 9)/(x − 3) = x + 3 → 6.", "<b>Kalikan sekawan</b>: (√(x + 1) − 2)/(x − 3) → 1/4.",
                       "<b>Samakan penyebut</b>: (1/x − 1/2)/(x − 2) → −1/4.", "Pola umum: lim (xⁿ − aⁿ)/(x − a) = n·aⁿ⁻¹."]),
            [limit_graph("(√(x + 1) − 2)/(x − 3) → 1/4", "(sqrt(x+1)-2)/(x-3)", "3", "0.25", [-1, 8], [0, 0.6])]),
      ]),
    T("kd-lim-takhingga", "Limit di Tak Hingga & Asimtot", "♾️", "Perilaku ujung grafik, asimtot datar & tegak, bilangan e.",
      "Stewart §2.6, §3.6; Whitman §4.3; Strang §6.2", [
          S("Limit di tak hingga",
            "<p>lim<sub>x→∞</sub> 1/xᵖ = 0 (p &gt; 0). Untuk fungsi rasional bandingkan derajat:</p>"
            + table(["Derajat", "lim di ∞"], [["pembilang &lt; penyebut", "0"], ["sama", "rasio koefisien utama"], ["pembilang &gt; penyebut", "±∞"]])
            + "<p>Asimtot datar y = L bila lim<sub>x→±∞</sub> f = L; asimtot tegak x = c bila f → ±∞ saat x → c. Bentuk 1^∞ menghasilkan e: "
              "lim (1 + a/x)ˣ = eᵃ.</p>",
            [g("Fungsi rasional (ax + 1)/(x − 2)", [-8, 12], [-10, 10], [param("a", "a", -4, 4, 0.5, 2, "a")],
               [{"type": "fn", "expr": "(a*x+1)/(x-2)", "color": "blue", "label": "f"}, {"type": "hline", "y": "a", "color": "red", "dash": True},
                {"type": "vline", "x": 2, "color": "red", "dash": True}], [readout("asimtot datar y = a", "a", 2)],
               "Garis merah putus-putus = asimtot.")]),
      ]),
    T("kd-lim-trig", "Limit Trigonometri", "📡", "lim sin x / x = 1 dan turunannya.", "Whitman §4.3; Stewart §3.3", [
        S("Limit istimewa sin x / x",
          "<p><b>lim<sub>x→0</sub> sin x / x = 1</b> (x radian) dibuktikan dengan teorema apit: cos x ≤ sin x / x ≤ 1 (Whitman §4.3 “A hard limit”). "
          "Akibatnya: lim sin(ax)/(bx) = a/b, lim tan x / x = 1, lim (1 − cos x)/x² = 1/2.</p>",
          [g("sin x / x di sekitar 0", [-10, 10], [-0.4, 1.2], [param("d", "x", -9, 9, 0.01, 2, "x")],
             [{"type": "fn", "expr": "sin(x)/x", "color": "blue", "label": "sin x / x"}, {"type": "fn", "expr": "cos(x)", "color": "gray", "dash": True, "label": "cos x"},
              {"type": "hline", "y": 1, "color": "red", "dash": True}, {"type": "point", "x": "d", "y": "sin(d)/d", "color": "red"}],
             [readout("sin x / x", "sin(d)/d", 6)], "Kurva biru terjepit antara cos x dan 1, sehingga di x → 0 nilainya → 1.")]),
    ]),
    T("kd-lim-kontinu", "Kekontinuan & Pembuktian Limit", "🔗", "Tiga syarat kontinu, jenis diskontinuitas, TNA, bukti ε–δ.",
      "Stewart §2.4–2.5; Strang §2.7; Whitman §2.3", [
          S("Kekontinuan",
            "<p>f kontinu di c ⇔ (1) f(c) terdefinisi, (2) lim<sub>x→c</sub> f(x) ada, (3) lim f(x) = f(c). Diskontinuitas: <b>dapat dihapus</b> "
            "(lubang), <b>loncat</b>, dan <b>tak hingga</b>.</p><p><b>Teorema Nilai Antara</b>: f kontinu di [a, b] dan N di antara f(a), f(b) ⇒ "
            "ada c dengan f(c) = N. Dipakai untuk menjamin akar (metode bagi dua).</p>"),
          S("Definisi ε–δ (pembuktian limit)",
            "<p>lim<sub>x→c</sub> f(x) = L ⇔ untuk setiap ε &gt; 0 ada δ &gt; 0 sehingga 0 &lt; |x − c| &lt; δ ⇒ |f(x) − L| &lt; ε.</p>"
            "<p>Contoh: lim (3x − 1) = 5 di x = 2. |3x − 1 − 5| = 3|x − 2| &lt; ε bila δ = ε/3.</p>"
            + ref("Stewart §2.4 The Precise Definition of a Limit"),
            [g("Pita ε dan δ untuk f(x) = x²", [0, 4], [0, 9], [param("eps", "ε", 0.1, 2, 0.05, 1, "ε")],
               [{"type": "fn", "expr": "x*x", "color": "blue"}, {"type": "hband", "from": "4-eps", "to": "4+eps", "color": "red"},
                {"type": "vband", "from": "sqrt(4-eps)", "to": "sqrt(4+eps)", "color": "green"}],
               [readout("δ kiri 2 − √(4 − ε)", "2-sqrt(4-eps)", 4), readout("δ kanan √(4 + ε) − 2", "sqrt(4+eps)-2", 4)],
               "δ dipilih = yang lebih kecil dari kedua jarak, agar seluruh pita hijau masuk ke pita merah.")]),
      ]),
]

# ═════════════════════════ Sub-level 2: Turunan ════════════════════════════
TURUNAN = [
    T("kd-tur-definisi", "Definisi Turunan & Garis Singgung", "📍", "Laju perubahan, limit hasil bagi selisih, keterdiferensialan.",
      "Stewart §2.7–2.8; Whitman §2.1–2.4; Strang §2.1–2.3", [
          S("Turunan sebagai limit",
            "<p><b>f′(a) = lim<sub>h→0</sub> [f(a + h) − f(a)]/h</b> = gradien garis singgung = laju perubahan sesaat. "
            "Strang (MIT) memulai dari kecepatan: jarak f(t), kecepatan f′(t).</p>"
            "<p>Terdiferensialkan ⇒ kontinu, tetapi tidak sebaliknya: |x| kontinu di 0 namun punya sudut.</p>",
            [tangent_graph("Garis singgung y = x³ − 3x", "x**3-3*x", "3*x*x-3", "Titik a", -2.5, 2.5, 1.5, [-3, 3], [-6, 6])]),
      ]),
    T("kd-tur-dasar", "Aturan Pangkat, Konstanta & Jumlah", "✏️", "(xⁿ)′ = nxⁿ⁻¹, turunan tingkat tinggi.", "Stewart §3.1; Whitman §3.1–3.2", [
        S("Aturan dasar",
          table(["Fungsi", "Turunan"], [["c", "0"], ["xⁿ (n real)", "nxⁿ⁻¹"], ["c·f", "c·f′"], ["f ± g", "f′ ± g′"]])
          + "<p>Akar dan pecahan ditulis sebagai pangkat: √x = x<sup>1/2</sup>, 1/x³ = x<sup>−3</sup>. Turunan kedua f″ = (f′)′ "
            "(percepatan, kecekungan).</p>",
          [g("f(x) = xⁿ dan f′(x) = nxⁿ⁻¹", [-2, 2], [-6, 6], [param("nn", "n", 1, 5, 1, 3, "n")],
             [{"type": "fn", "expr": "x**nn", "color": "blue", "label": "xⁿ"}, {"type": "fn", "expr": "nn*x**(nn-1)", "color": "orange", "label": "nxⁿ⁻¹"}],
             None, "Di mana f naik, grafik f′ di atas sumbu-x.")]),
    ]),
    T("kd-tur-perkalian", "Aturan Perkalian & Pembagian", "✖️", "(uv)′ = u′v + uv′, (u/v)′ = (u′v − uv′)/v².", "Stewart §3.2; Whitman §3.3–3.4", [
        S("Perkalian dan pembagian",
          "<p><b>(uv)′ = u′v + uv′</b> dan <b>(u/v)′ = (u′v − uv′)/v²</b>. Turunan hasil kali bukan hasil kali turunan! "
          "Contoh: (x² sin x)′ = 2x sin x + x² cos x.</p>",
          [g("Luas persegi panjang u·v bertambah dua ‘pita’", [0, 6], [0, 6], [param("du", "Δu", 0, 1.5, 0.05, 0.6, "Δu"), param("dv", "Δv", 0, 1.5, 0.05, 0.4, "Δv")],
             [{"type": "fill", "upper": "4", "from": 0, "to": 3, "color": "blue"}, {"type": "fill", "upper": "4", "from": 3, "to": "3+du", "color": "orange"},
              {"type": "fill", "upper": "4+dv", "lower": "4", "from": 0, "to": 3, "color": "green"}],
             [readout("u·Δv + v·Δu", "3*dv+4*du", 3), readout("Δu·Δv (diabaikan)", "du*dv", 4)],
             "Δ(uv) = uΔv + vΔu + ΔuΔv; suku terakhir hilang saat dibagi Δx dan Δx → 0.")]),
    ]),
    T("kd-tur-rantai", "Aturan Rantai", "⛓️", "Turunan fungsi komposisi.", "Stewart §3.4; Whitman §3.5; Strang §4.1", [
        S("Aturan rantai",
          "<p>Jika y = f(u) dan u = g(x), maka <b>dy/dx = dy/du · du/dx</b>, yaitu (f(g(x)))′ = f′(g(x))·g′(x). "
          "Contoh: ((2x + 1)⁵)′ = 5(2x + 1)⁴·2 = 10(2x + 1)⁴ (soal U-D3).</p>",
          [tangent_graph("Komposisi sin(x²)", "sin(x*x)", "2*x*cos(x*x)", "a", -2.5, 2.5, 1, [-3, 3], [-2, 2],
                         caption="Kemiringan sin(x²) = cos(x²)·2x: faktor 2x membuat osilasi makin rapat.")]),
    ]),
    T("kd-tur-transenden", "Turunan Trig, Eksponen, Log & Implisit", "🌐", "sin, cos, tan, eˣ, ln x, turunan implisit & invers.",
      "Stewart §3.3, §3.5–3.6; Whitman Bab 4; Strang §4.2–4.4, §6.2", [
          S("Tabel turunan transenden",
            table(["f(x)", "f′(x)"], [["sin x", "cos x"], ["cos x", "−sin x"], ["tan x", "sec²x"], ["eˣ", "eˣ"], ["aˣ", "aˣ ln a"],
                                      ["ln x", "1/x"], ["log_a x", "1/(x ln a)"]])
            + "<p><b>Implisit</b>: turunkan kedua ruas terhadap x, ingat (y²)′ = 2y·y′. <b>Invers</b>: (f⁻¹)′(b) = 1/f′(a), f(a) = b.</p>",
            [tangent_graph("eˣ adalah turunannya sendiri", "exp(x)", "exp(x)", "a", -2, 2, 0.5, [-3, 3], [-1, 8],
                           caption="Nilai f(a) dan kemiringan f′(a) di tabel selalu sama.")]),
      ]),
]

# ═════════════════════════ Sub-level 3: Aplikasi Turunan ══════════════════
APLIKASI = [
    T("kd-apl-singgung", "Garis Singgung, Normal & Aproksimasi", "📐", "Persamaan singgung/normal, aproksimasi linear.",
      "Stewart §3.10; Whitman §6.4", [
          S("Garis singgung dan linearisasi",
            "<p>Garis singgung di x₀: y = f(x₀) + f′(x₀)(x − x₀). Garis normal tegak lurus: gradien −1/f′(x₀). "
            "<b>Aproksimasi linear</b> L(x) = f(a) + f′(a)(x − a) menaksir f di dekat a, mis. √4,1 ≈ 2 + 0,1/4 = 2,025.</p>",
            [tangent_graph("√x dan garis singgungnya di a", "sqrt(x)", "1/(2*sqrt(x))", "a", 0.3, 9, 4, [0, 10], [0, 4])]),
      ]),
    T("kd-apl-laju", "Laju Terkait", "⏱️", "Menurunkan hubungan antar besaran terhadap waktu.", "Stewart §3.9; Whitman §6.2", [
        S("Langkah laju terkait",
          "<ol class='lesson-list'><li>Gambar & beri nama variabel.</li><li>Tulis persamaan hubungan (Pythagoras, volume, sebangun).</li>"
          "<li>Turunkan terhadap t (aturan rantai).</li><li>Substitusi nilai sesaat <b>setelah</b> menurunkan.</li></ol>"
          "<p>Contoh tangga: x² + y² = L² ⇒ dy/dt = −(x/y)·dx/dt (soal U-S7).</p>"),
    ]),
    T("kd-apl-ekstrem", "Nilai Ekstrem & Uji Turunan", "⛰️", "Titik kritis, naik/turun, uji turunan pertama & kedua.",
      "Stewart §4.1–4.3; Whitman §5.1–5.3", [
          S("Mencari ekstrem",
            bullets(["Titik kritis: f′(c) = 0 atau f′(c) tidak ada.", "f′ &gt; 0 ⇒ naik; f′ &lt; 0 ⇒ turun.",
                     "Uji turunan pertama: tanda f′ berubah + → − (maks) atau − → + (min).", "Uji turunan kedua: f″(c) &lt; 0 maks, &gt; 0 min.",
                     "Ekstrem mutlak di [a, b]: bandingkan f di titik kritis dan ujung."]),
            [g("f = x³ − 3x² + 1, f′, dan titik kritis", [-2, 4], [-6, 6], [],
               [{"type": "fn", "expr": "x**3-3*x*x+1", "color": "blue", "label": "f"}, {"type": "fn", "expr": "3*x*x-6*x", "color": "orange", "dash": True, "label": "f′"},
                {"type": "point", "x": 0, "y": 1, "color": "red"}, {"type": "point", "x": 2, "y": -3, "color": "red"}, {"type": "hline", "y": 0, "color": "gray"}],
               None, "Ekstrem terjadi saat f′ (oranye) memotong sumbu-x.")]),
      ]),
    T("kd-apl-cekung", "Kecekungan & Sketsa Grafik", "〰️", "Titik belok, cekung atas/bawah, membaca grafik dari f′.",
      "Stewart §4.3–4.5; Whitman §5.4–5.5", [
          S("Kecekungan",
            "<p>f″ &gt; 0: cekung ke atas (∪), f″ &lt; 0: cekung ke bawah (∩). Titik belok: kecekungan berganti. "
            "Sketsa: domain, titik potong, asimtot, interval naik/turun, ekstrem, kecekungan.</p>",
            [g("Kecekungan y = x³ − 3x", [-3, 3], [-5, 5], [param("s", "x", -2.8, 2.8, 0.05, 1, "x")],
               [{"type": "fn", "expr": "x**3-3*x", "color": "blue"}, {"type": "point", "x": "s", "y": "s**3-3*s", "color": "red"},
                {"type": "fn", "expr": "(s**3-3*s)+(3*s*s-3)*(x-s)", "color": "orange", "dash": True}],
               [readout("f″(x) = 6x", "6*s", 3)], "Cekung atas: grafik di atas garis singgung; cekung bawah: di bawahnya.")]),
      ]),
    T("kd-apl-optimasi", "Optimasi, L'Hôpital & TNR", "🏆", "Masalah maksimum/minimum, aturan L'Hôpital, Teorema Nilai Rata-rata.",
      "Stewart §4.4, §4.7, §4.2; Whitman §6.1, §6.5", [
          S("Optimasi",
            "<p>Tentukan besaran yang dioptimalkan, nyatakan sebagai fungsi satu variabel (pakai kendala), cari titik kritis, cek ujung domain. "
            "Contoh FT: kotak tanpa tutup dari karton s × s ⇒ potongan optimal x = s/6.</p>"),
          S("L'Hôpital & Teorema Nilai Rata-rata",
            "<p><b>L'Hôpital</b>: untuk 0/0 atau ∞/∞, lim f/g = lim f′/g′. <b>TNR</b>: f kontinu di [a, b], terdiferensialkan di (a, b) ⇒ ada c dengan "
            "f′(c) = [f(b) − f(a)]/(b − a).</p>",
            [g("Teorema Nilai Rata-rata pada f(x) = x³", [-0.5, 3.5], [-2, 28], [param("c", "c", 0, 3, 0.01, 1, "c")],
               [{"type": "fn", "expr": "x**3", "color": "blue"}, {"type": "fn", "expr": "9*x", "color": "gray", "dash": True, "label": "sekan"},
                {"type": "fn", "expr": "c**3+3*c*c*(x-c)", "color": "red", "dash": True, "label": "singgung di c"}],
               [readout("f′(c) = 3c²", "3*c*c", 3), readout("gradien sekan", "9", 3)], "Cari c (≈ 1,732) saat garis merah sejajar sekan.")]),
      ]),
]

# ═════════════════════════ Sub-level 4: Integral ═══════════════════════════
INTEGRAL = [
    T("kd-int-antiturunan", "Antiturunan & Integral Tak Tentu", "🔙", "∫ xⁿ dx, tabel integral, syarat awal.", "Stewart §4.9, §5.4; Strang §5.2", [
        S("Antiturunan",
          "<p>F antiturunan f bila F′ = f. Semua antiturunan berbentuk F(x) + C. Notasi ∫ f(x) dx = F(x) + C.</p>"
          + table(["f(x)", "∫ f(x) dx"], [["xⁿ (n ≠ −1)", "xⁿ⁺¹/(n + 1) + C"], ["1/x", "ln|x| + C"], ["eˣ", "eˣ + C"], ["sin x", "−cos x + C"], ["cos x", "sin x + C"]]),
          [antiderivative_family("Keluarga antiturunan 3x²", "3*x*x", "x**3", [-2, 2], [-10, 10])]),
    ]),
    T("kd-int-riemann", "Notasi Sigma & Jumlah Riemann", "📊", "Σ, rumus jumlah, luas sebagai limit jumlah.", "Stewart §5.1–5.2; Whitman §7.1; Strang §5.3", [
        S("Dari jumlah ke integral",
          "<p>Bagi [a, b] menjadi n bagian Δx = (b − a)/n. Jumlah Riemann Σ f(xᵢ)Δx menaksir luas; integral tentu adalah limitnya untuk n → ∞.</p>"
          + bullets(["Σk = n(n + 1)/2", "Σk² = n(n + 1)(2n + 1)/6", "Σk³ = [n(n + 1)/2]²"]),
          [g("Jumlah Riemann untuk sin x pada [0, π]", [-0.2, 3.4], [-0.2, 1.3], [param("N", "n", 1, 50, 1, 6, "n")],
             [{"type": "riemann", "id": "R", "expr": "sin(x)", "from": 0, "to": "pi", "n": "N", "mode": "mid", "color": "amber"}, {"type": "fn", "expr": "sin(x)", "color": "blue"}],
             [readout("Jumlah titik tengah", "R", 6), readout("Eksak", "2", 6)], "Jumlah mendekati 2 saat n bertambah.")]),
    ]),
    T("kd-int-tentu", "Integral Tentu & Sifatnya", "📏", "Luas bertanda, linearitas, nilai mutlak, simetri.", "Stewart §5.2; Whitman §7.3", [
        S("Sifat integral tentu",
          bullets(["∫ₐᵇ (cf + g) = c∫ₐᵇ f + ∫ₐᵇ g", "∫ₐᶜ f = ∫ₐᵇ f + ∫ᵦᶜ f", "∫ₐᵇ f = −∫ᵦᵃ f, ∫ₐᵃ f = 0",
                   "f ganjil ⇒ ∫₋ₐᵃ f = 0; f genap ⇒ ∫₋ₐᵃ f = 2∫₀ᵃ f"]),
          [area_graph("Luas bertanda f(x) = x² − 2", "x*x-2", 0, param("b", "Batas atas b", 0, 3, 0.05, 2.5, "b"), "b**3/3-2*b", [-0.5, 3.2], [-3, 8],
                      caption="Bagian di bawah sumbu-x memberi kontribusi negatif.")]),
    ]),
    T("kd-int-tdk", "Teorema Dasar Kalkulus", "🌉", "Jembatan turunan–integral, nilai rata-rata.", "Stewart §5.3; Whitman §7.2; Strang §5.7", [
        S("Dua bagian TDK",
          "<p><b>TDK 1</b>: g(x) = ∫ₐˣ f(t) dt ⇒ g′(x) = f(x). <b>TDK 2</b>: ∫ₐᵇ f(x) dx = F(b) − F(a) untuk antiturunan F. "
          "Nilai rata-rata f̄ = (1/(b − a))∫ₐᵇ f dx.</p>",
          [g("Fungsi akumulasi g(x) = ∫₀ˣ cos t dt = sin x", [-0.2, 6.5], [-1.3, 1.3], [param("X", "x", 0, 6.28, 0.01, 1.5, "x")],
             [{"type": "fill", "upper": "cos(x)", "from": 0, "to": "X", "color": "amber"}, {"type": "fn", "expr": "cos(x)", "color": "blue", "label": "f = cos"},
              {"type": "fn", "expr": "sin(x)", "color": "red", "dash": True, "label": "g = ∫f"}, {"type": "point", "x": "X", "y": "sin(X)", "color": "red"}],
             [readout("luas terakumulasi g(x)", "sin(X)", 4), readout("g′(x) = f(x)", "cos(X)", 4)], "Laju pertambahan luas (g′) sama dengan tinggi f di x.")]),
    ]),
    T("kd-int-substitusi", "Integral Substitusi & Luas Daerah", "🧩", "Substitusi u, luas di bawah/antara kurva.", "Stewart §5.5, §6.1; Whitman §8.1, §9.1", [
        S("Substitusi dan luas",
          "<p><b>Substitusi</b>: ∫ f(g(x))g′(x) dx = ∫ f(u) du dengan u = g(x) (kebalikan aturan rantai). Untuk integral tentu, ubah juga batasnya.</p>"
          "<p><b>Luas antara dua kurva</b>: ∫ₐᵇ [atas − bawah] dx, dengan a, b titik potong. Luas parabola terhadap tali busurnya = |a|(q − p)³/6.</p>",
          [g("Luas antara y = x + 2 dan y = x² (soal U-S5)", [-2, 3], [-1, 5], [param("mm", "gradien garis", 0, 2, 0.05, 1, "m")],
             [{"type": "fill", "upper": "mm*x+2", "lower": "x*x", "from": "(mm-sqrt(mm*mm+8))/2", "to": "(mm+sqrt(mm*mm+8))/2", "color": "amber"},
              {"type": "fn", "expr": "x*x", "color": "blue"}, {"type": "fn", "expr": "mm*x+2", "color": "green"}],
             [readout("Luas", "pow(mm*mm+8,1.5)/6", 4)], "Untuk m = 1 luasnya 9/2.")]),
    ]),
]

SUBLEVELS = [
    {"slug": "kd-limit-kekontinuan", "title": "Limit dan Kekontinuan", "subtitle": "Konsep limit sampai pembuktian ε–δ", "icon": "🎯",
     "badge_label": "Kalkulus Dasar", "summary_html": "<p>Fondasi kalkulus: limit, teknik menghitungnya, dan kekontinuan.</p>", "topics": LIMIT},
    {"slug": "kd-turunan", "title": "Turunan (Diferensial)", "subtitle": "Definisi dan aturan-aturan turunan", "icon": "📈",
     "badge_label": "Kalkulus Dasar", "summary_html": "<p>Turunan sebagai laju perubahan dan seluruh aturan diferensiasi.</p>", "topics": TURUNAN},
    {"slug": "kd-aplikasi-turunan", "title": "Aplikasi Turunan", "subtitle": "Singgung, laju terkait, ekstrem, optimasi", "icon": "🛠️",
     "badge_label": "Kalkulus Dasar", "summary_html": "<p>Menggunakan turunan untuk menganalisis grafik dan memecahkan masalah nyata.</p>", "topics": APLIKASI},
    {"slug": "kd-integral", "title": "Integral Tentu & Tak Tentu", "subtitle": "Antiturunan, Riemann, TDK, substitusi, luas", "icon": "∫",
     "badge_label": "Kalkulus Dasar", "summary_html": "<p>Integral sebagai antiturunan dan sebagai luas, dihubungkan oleh Teorema Dasar Kalkulus.</p>", "topics": INTEGRAL},
]

# ── Penggabungan konten lama (berkas 1 & 3) ─────────────────────────────────
# Node lama yang diserap: materi dipindah ke topik, soal dipindah ke sub-level/sesi.
ABSORB_NODES = {"umum-limit": "kd-limit-kekontinuan", "umum-turunan": "kd-turunan", "umum-integral": "kd-integral"}
ABSORB_SECTIONS = {
    ("umum-limit", "Definisi dan sifat limit"): "kd-lim-konsep",
    ("umum-limit", "Limit penting"): "kd-lim-trig",
    ("umum-limit", "Bentuk tak tentu"): "kd-lim-aljabar",
    ("umum-limit", "Kontinuitas"): "kd-lim-kontinu",
    ("umum-turunan", "Definisi turunan"): "kd-tur-definisi",
    ("umum-turunan", "Tabel turunan dasar"): "kd-tur-transenden",
    ("umum-turunan", "Aturan turunan"): "kd-tur-perkalian",
    ("umum-turunan", "Aplikasi turunan"): "kd-apl-ekstrem",
    ("umum-integral", "Antiturunan & Teorema Dasar Kalkulus"): "kd-int-tdk",
    ("umum-integral", "Tabel integral dasar"): "kd-int-antiturunan",
    ("umum-integral", "Teknik integrasi"): "kd-int-substitusi",
    ("umum-integral", "Aplikasi integral"): "kd-int-substitusi",
}
# Soal lama → (topik, nomor sesi). None = tetap di Bank Soal (belum ada topik yang cocok di level ini).
FIXED_QUESTIONS = {
    "U-D1": ("kd-lim-aljabar", 1), "U-D2": ("kd-lim-takhingga", 2), "U-D3": ("kd-tur-rantai", 1), "U-D4": ("kd-tur-transenden", 2),
    "U-D5": ("kd-int-tentu", 1), "U-D6": ("kd-int-substitusi", 2), "U-S1": ("kd-apl-singgung", 2), "U-S2": ("kd-apl-ekstrem", 3),
    "U-S3": ("kd-int-substitusi", 3), "U-S4": None, "U-S5": ("kd-int-substitusi", 4), "U-S7": ("kd-apl-laju", 3),
}
