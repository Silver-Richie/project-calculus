/**
 * Calculus Bridge — Adegan "Tim Archie" di halaman Masuk/Daftar.
 *
 * Cerita visual: tebing kiri = MASALAH (pohon apel, papan tulis), tebing kanan = SOLUSI
 * (tempat kartu login). Keduanya dihubungkan JEMBATAN berbentuk kurva fungsi kontinu
 * bridgeY(x) yang punya titik maksimum lokal (f′(x) = 0) dan lembah.
 *
 * Tokoh & peran (tiap tokoh punya 2 vibe yang tampil bergantian):
 *   archie (biru)  Leader & Penjelajah  — mendaki lalu menancapkan bendera di puncak kurva
 *                                          ↔ meluncur di jembatan seperti roller coaster
 *   hijau          Problem Solver       — mengukur kemiringan garis singgung (dahi berkerut)
 *                                          ↔ "Eureka!" saat menemukan titik potong grafik
 *   ungu           Sage / Penyihir      — melayang di piringan sihir, menyulap ∫ dan ∞ menuju
 *                                          gerbang (kartu) ↔ monokel melorot + kedipan jenaka
 *   kuning         Cheerleader/Pemburu  — menangkap apel gravitasi Newton dengan jaring
 *                                          (lintasan + panah kecepatan) ↔ menyeberang & tos
 *
 * Mekanisme:
 *  - Satu skrip = satu adegan di SCRIPTS dengan daftar tokoh yang dipakainya. runScript()
 *    mengunci tokoh itu (busy) agar dua adegan tidak berebut tokoh yang sama.
 *  - Sutradara (director) mengundi skrip yang tokohnya bebas, tanpa mengulang yang terakhir.
 *    Pertama kali, tim merakit papan jembatan yang masih bolong (skrip "rakit").
 *  - Klik tokoh → menjalankan vibe tokoh itu secara bergantian (VIBES). Klik papan → grafik
 *    baru; pohon → apel jatuh; matahari/bulan → siang/malam; bendera → Archie bangga;
 *    jembatan → roller coaster; item berkilau → dikumpulkan ke penghitung (HUD).
 *  - Form (event dari auth_mascot.js): look → semua menoleh ke kolom; cover → Archie &
 *    Kuning menutup mata; type → Hijau menulis rumus di papan & Kuning melompat kecil;
 *    cheer → semua melompat.
 *  - Tata letak: latar penuh layar (≥ 768px) atau banner di atas kartu (HP); lihat fit().
 *  - Hemat: berhenti saat tab tersembunyi; prefers-reduced-motion mematikan adegan otomatis.
 */
(() => {
  'use strict';

  const NS = 'http://www.w3.org/2000/svg';
  const INK = '#1E3A5F';
  const REDUCED = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const BANNER = window.matchMedia('(max-width: 767px)');   // HP: adegan jadi banner di atas kartu

  const rand = (a, b) => a + Math.random() * (b - a);
  const pick = (arr, not) => {
    const pool = arr.length > 1 ? arr.filter((x) => x !== not) : arr;
    return pool[Math.floor(Math.random() * pool.length)];
  };
  const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));
  const make = (tag, attrs = {}, html = '') => {
    const node = document.createElementNS(NS, tag);
    Object.entries(attrs).forEach(([k, v]) => node.setAttribute(k, v));
    if (html) node.innerHTML = html;
    return node;
  };
  const easeInOut = (t) => (t < 0.5 ? 2 * t * t : 1 - (-2 * t + 2) ** 2 / 2);
  const easeIn = (t) => t * t;
  const easeOut = (t) => 1 - (1 - t) ** 2;

  /** Animasi berbasis waktu: fn(t) dipanggil tiap frame dengan t 0→1 (sudah di-ease). */
  function tween(ms, fn, ease = easeInOut) {
    return new Promise((resolve) => {
      const t0 = performance.now();
      const step = (now) => {
        const t = Math.min(1, (now - t0) / ms);
        fn(ease(t));
        if (t < 1) requestAnimationFrame(step);
        else resolve();
      };
      requestAnimationFrame(step);
    });
  }

  // ── Jembatan kurva ─────────────────────────────────────────────
  // y turun = naik di layar. Puncak (maksimum lokal) di x ≈ 513, lembah di x ≈ 655.
  const BX0 = 384;   // ujung kiri (tebing masalah)
  const BX1 = 776;   // ujung kanan (tebing solusi)
  const bridgeY = (x) => 600 - 25 * ((x - 380) / 400)
    - 140 * Math.exp(-(((x - 512) / 75) ** 2)) + 30 * Math.exp(-(((x - 655) / 55) ** 2));
  const PEAK_X = 513;
  const PEAK_Y = bridgeY(PEAK_X);
  const deckY = (x) => bridgeY(x) - 4;   // tempat kaki berpijak
  const slopeDeg = (x) => (Math.atan2(bridgeY(x + 1) - bridgeY(x - 1), 2) * 180) / Math.PI;
  const GAP = [566, 600];                // papan yang masih bolong sebelum dirakit (terlihat, tidak tertutup kartu)
  const FLAG_X = PEAK_X + 66;

  // ── Tokoh ──────────────────────────────────────────────────────
  // home = titik kaki awal; s = skala; bx = geser gelembung agar tidak menabrak.
  const CHARS = {
    ungu:   { name: 'Ungu si Penyihir Kalkulus', home: [404, 328], s: 0.6, body: '#C4B5FD', line: '#7C3AED', belly: '#EDE9FE', gill: '#F0ABFC', gillLine: '#C026D3', bx: -10, float: true },
    archie: { name: 'Archie si Penjelajah', home: [PEAK_X, deckY(PEAK_X)], s: 0.8, body: '#93C5FD', line: '#2563EB', belly: '#DBEAFE', gill: '#F43F5E', gillLine: '#E11D48', bx: 8 },
    hijau:  { name: 'Hijau si Penemu', home: [318, 622], s: 0.8, body: '#86EFAC', line: '#16A34A', belly: '#DCFCE7', gill: '#F472B6', gillLine: '#DB2777', bx: 0 },
    kuning: { name: 'Kuning si Pemburu Apel', home: [130, 616], s: 0.62, body: '#FDE68A', line: '#D97706', belly: '#FEF9C3', gill: '#F9A8D4', gillLine: '#DB2777', bx: 10 },
  };
  const ORDER = ['ungu', 'archie', 'hijau', 'kuning'];   // urutan gambar (belakang → depan)

  const MOUTH = {
    smile: ['M90 118Q100 128 110 118', 'none'],
    open: ['M94 118Q100 132 106 118Z', '#9F1239'],
    grin: ['M84 115Q100 138 116 115Z', '#9F1239'],
    flat: ['M92 121H108', 'none'],
    wavy: ['M88 122q4-4 8 0t8 0t8 0', 'none'],
    o: ['M95 121a5 6 0 1 0 10 0a5 6 0 1 0-10 0', '#9F1239'],
  };

  const star4 = (x, y, r, d = 0, fill = '#FBBF24') => `<path class="ic-twinkle" style="--d:${d}s" d="M${x} ${y - r}Q${x} ${y} ${x + r} ${y}Q${x} ${y} ${x} ${y + r}Q${x} ${y} ${x - r} ${y}Q${x} ${y} ${x} ${y - r}Z" fill="${fill}"/>`;

  // Aksesori kepala (digambar paling depan).
  const ACC = {
    archie: `<g class="fam-cap"><path d="M100 50L143 66L100 82L57 66Z" fill="#1E3A5F" stroke="#6366F1" stroke-width="2.5"/>
      <path d="M125 74L133 90" stroke="#D97706" stroke-width="2.5" stroke-linecap="round"/><circle cx="133" cy="90" r="3" fill="#D97706"/></g>`,
    hijau: `<path d="M50 80Q100 60 150 80" stroke="#0F766E" stroke-width="5" fill="none" stroke-linecap="round"/>
      <circle cx="84" cy="72" r="11" fill="#CCFBF1" stroke="#0F766E" stroke-width="4"/><circle cx="116" cy="72" r="11" fill="#CCFBF1" stroke="#0F766E" stroke-width="4"/>
      <g class="fam-brows" stroke="#14532D" stroke-width="4.5" stroke-linecap="round"><path d="M62 84L88 90M138 84L112 90"/></g>`,
    ungu: `<path d="M62 86q14-10 28-1M110 85q14-9 28 1" stroke="#fff" stroke-width="7" stroke-linecap="round" fill="none"/>
      <g class="fam-monocle"><circle cx="124" cy="103" r="16" fill="rgba(255,255,255,.15)" stroke="#D97706" stroke-width="3"/>
        <path d="M140 106q8 18 2 34" stroke="#D97706" stroke-width="1.5" fill="none"/></g>
      <g class="fam-stache"><path d="M100 113q-8-8-20-2q-6 4-12 0q4 10 16 8q10-1 16-6q6 5 16 6q12 2 16-8q-6 4-12 0q-12-6-20 2z" fill="#fff" stroke="#D6D3D1" stroke-width="1.5"/></g>
      <g class="fam-hat"><path d="M52 80Q100 58 148 80Q100 94 52 80Z" fill="#5B21B6"/>
        <path d="M66 76L102 6Q108-2 114 8L134 74Z" fill="#6D28D9" stroke="#4C1D95" stroke-width="3" stroke-linejoin="round"/>
        ${star4(96, 48, 7, 0, '#FDE047')}<circle cx="117" cy="34" r="2.6" fill="#FDE047"/><circle cx="108" cy="62" r="2" fill="#FDE047"/></g>`,
    kuning: `<g class="fam-bow"><path d="M100 66L76 52L79 82Z" fill="#F472B6" stroke="#DB2777" stroke-width="3" stroke-linejoin="round"/>
      <path d="M100 66L124 52L121 82Z" fill="#F472B6" stroke="#DB2777" stroke-width="3" stroke-linejoin="round"/><circle cx="100" cy="67" r="7" fill="#DB2777"/></g>
      <g fill="#D97706" opacity=".5"><circle cx="58" cy="113" r="1.8"/><circle cx="64" cy="118" r="1.8"/><circle cx="142" cy="113" r="1.8"/><circle cx="136" cy="118" r="1.8"/></g>`,
  };

  // Benda di tangan kanan (disembunyikan saat menutup mata).
  const HAND = {
    archie: `<path d="M150 150l14-26" stroke="#F59E0B" stroke-width="6" stroke-linecap="round"/><path d="M164 124l3-6" stroke="${INK}" stroke-width="3" stroke-linecap="round"/>`,
    hijau: `<path d="M166 44L150 150M166 44L198 146" stroke="#475569" stroke-width="5" stroke-linecap="round"/>
      <path d="M198 146l3 10" stroke="#F59E0B" stroke-width="4" stroke-linecap="round"/>
      <path d="M154 98Q176 108 188 102" stroke="#94A3B8" stroke-width="3" fill="none"/>
      <circle cx="166" cy="44" r="7" fill="#94A3B8" stroke="#334155" stroke-width="2.5"/>`,
    ungu: `<path d="M150 150L180 102" stroke="#78350F" stroke-width="5" stroke-linecap="round"/>
      <path d="M182 88l3 7 7 1-5 5 1 7-6-3-6 3 1-7-5-5 7-1z" fill="#FDE047" stroke="#F59E0B" stroke-width="1.5"/>`,
    kuning: `<path d="M150 150L184 54" stroke="#92400E" stroke-width="5" stroke-linecap="round"/>
      <g class="fam-net"><ellipse cx="192" cy="34" rx="24" ry="13" fill="rgba(255,255,255,.35)" stroke="#F59E0B" stroke-width="4" transform="rotate(-20 192 34)"/>
      <path d="M172 40Q186 72 206 30M180 44Q190 62 198 33M174 34L208 26" stroke="#FCD34D" stroke-width="1.6" fill="none"/></g>`,
  };

  // Di belakang badan (piringan sihir Ungu) dan di depan badan (kereta roller coaster Archie).
  const BACK = {
    ungu: `<g class="fam-disc"><ellipse class="fam-disc-glow" cx="100" cy="184" rx="96" ry="24" fill="url(#fam-magic)"/>
      <ellipse cx="100" cy="181" rx="78" ry="15" fill="#4C1D95" stroke="#A78BFA" stroke-width="3"/>
      <ellipse class="fam-disc-ring" cx="100" cy="181" rx="62" ry="10" fill="none" stroke="#FDE047" stroke-width="2.5"/></g>`,
  };
  const FRONT = {
    archie: `<g class="fam-cart"><path d="M38 138H162L150 182H50Z" fill="#EF4444" stroke="#991B1B" stroke-width="4" stroke-linejoin="round"/>
      <path d="M46 152H154" stroke="#FCA5A5" stroke-width="4"/>
      <circle cx="70" cy="188" r="11" fill="#334155" stroke="#0F172A" stroke-width="3"/><circle cx="130" cy="188" r="11" fill="#334155" stroke="#0F172A" stroke-width="3"/></g>`,
  };

  function eyes(id, c) {
    if (id === 'archie') {
      return `<rect x="58" y="90" width="32" height="26" rx="8" fill="${INK}" stroke="#38BDF8" stroke-width="3"/>
        <rect x="110" y="90" width="32" height="26" rx="8" fill="${INK}" stroke="#38BDF8" stroke-width="3"/>
        <line x1="90" y1="102" x2="110" y2="102" stroke="#38BDF8" stroke-width="3" stroke-linecap="round"/>
        <g class="fam-eyes"><g class="fam-pupils">
          <ellipse cx="74" cy="103" rx="7" ry="8" fill="#38BDF8"/><circle cx="71" cy="100" r="3" fill="#fff"/>
          <ellipse cx="126" cy="103" rx="7" ry="8" fill="#38BDF8"/><circle cx="123" cy="100" r="3" fill="#fff"/>
        </g></g>`;
    }
    return `<g class="fam-eyes">
      <ellipse cx="76" cy="103" rx="12" ry="13" fill="#fff" stroke="${c.line}" stroke-width="2.5"/>
      <ellipse cx="124" cy="103" rx="12" ry="13" fill="#fff" stroke="${c.line}" stroke-width="2.5"/>
      <g class="fam-pupils"><circle cx="76" cy="104" r="6.5" fill="${INK}"/><circle cx="73.5" cy="101" r="2.2" fill="#fff"/>
        <circle cx="124" cy="104" r="6.5" fill="${INK}"/><circle cx="121.5" cy="101" r="2.2" fill="#fff"/></g></g>
      <g class="fam-wink"><ellipse cx="76" cy="103" rx="14" ry="15" fill="${c.body}"/>
        <path d="M65 105q11-8 22 0" stroke="${INK}" stroke-width="3" fill="none" stroke-linecap="round"/></g>`;
  }

  /** Satu axolotl (bentuk dasar = logo Archie, viewBox 200×200, kaki di y=172). */
  function axolotl(id) {
    const c = CHARS[id];
    const paint = `fill="${c.body}" stroke="${c.line}" stroke-width="3"`;
    const gill = (d) => `<path d="${d}" fill="${c.gill}" stroke="${c.gillLine}" stroke-width="3" stroke-linecap="round"/>`;
    return `<g class="fam-pos" data-pos="${id}">
      <g class="fam-char" data-char="${id}" tabindex="0" role="button" aria-label="${c.name}, tekan untuk beraksi" style="--d:${rand(0, 2).toFixed(2)}s">
        ${c.float ? '' : '<ellipse class="fam-shadow" cx="0" cy="2" rx="62" ry="9"/>'}
        <g class="fam-move"><g class="fam-breathe"><g transform="translate(-100 -172)">
          ${BACK[id] || ''}
          <path class="fam-tail" d="M148 150Q188 156 196 124Q178 140 150 136Z" ${paint} stroke-linejoin="round"/>
          <g class="fam-gill fam-gill-l">${gill('M42 95C25 80 15 95 28 112C15 118 20 135 38 128')}</g>
          <g class="fam-gill fam-gill-r">${gill('M158 95C175 80 185 95 172 112C185 118 180 135 162 128')}</g>
          <ellipse cx="100" cy="120" rx="58" ry="52" ${paint}/>
          <ellipse cx="100" cy="130" rx="34" ry="30" fill="${c.belly}" opacity=".9"/>
          <ellipse cx="78" cy="168" rx="14" ry="7" ${paint}/><ellipse cx="122" cy="168" rx="14" ry="7" ${paint}/>
          ${FRONT[id] || ''}
          <g class="fam-arm fam-arm-l"><ellipse cx="50" cy="140" rx="9" ry="15" ${paint}/></g>
          <g class="fam-arm fam-arm-r"><g class="fam-held">${HAND[id]}</g><ellipse cx="150" cy="140" rx="9" ry="15" ${paint}/></g>
          ${eyes(id, c)}
          <ellipse cx="56" cy="120" rx="7" ry="4" fill="#F43F5E" opacity=".5"/><ellipse cx="144" cy="120" rx="7" ry="4" fill="#F43F5E" opacity=".5"/>
          <path class="fam-mouth" d="${MOUTH.smile[0]}" fill="none" stroke="${INK}" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>
          ${ACC[id]}
        </g></g></g>
      </g></g>`;
  }

  function bubble(id) {
    const tx = (-CHARS[id].bx / 0.82).toFixed(1);   // ekor gelembung tetap menunjuk ke tokoh
    return `<g class="fam-banchor" data-banchor="${id}"><g class="fam-bubble" data-bubble="${id}">
        <path d="M-44,-86h88a14,14 0 0 1 14,14v40a14,14 0 0 1 -14,14H${+tx + 8}l-8,14l-8,-14H-44a14,14 0 0 1 -14,-14v-40a14,14 0 0 1 14,-14z"
              fill="#fff" stroke="${INK}" stroke-width="3" stroke-linejoin="round"/>
        <g class="fam-bubble-icon" transform="translate(0 -52)"></g>
      </g></g>`;
  }

  // ── Ikon gelembung (±30 × ±24, tanpa teks) ─────────────────────
  const AX = '<path d="M-30 16H30M-26 20V-24" stroke="#94A3B8" stroke-width="2"/>';
  const LEMNISCATE = 'M0,0C8,-14 26,-14 26,0C26,14 8,14 0,0C-8,-14 -26,-14 -26,0C-26,14 -8,14 0,0Z';
  const INTEGRAL = 'M9,-24C3,-30 -5,-25 -3,-13L3,13C5,25 -3,30 -9,24';
  const BULB = `<g class="ic-rays" stroke="#F59E0B" stroke-width="3" stroke-linecap="round"><path d="M0,-24V-30M17,-17L21,-21M-17,-17L-21,-21M23,-3H29M-23,-3H-29"/></g>
      <circle cx="0" cy="-4" r="13" fill="#FDE047" stroke="#CA8A04" stroke-width="3"/><path d="M-4,-4q4,6 8,0" stroke="#CA8A04" stroke-width="2" fill="none"/>
      <rect x="-6" y="9" width="12" height="9" rx="2" fill="#94A3B8"/>`;
  const ICONS = {
    question: `<g class="ic-wobble"><path d="M-8,-9C-8,-21 10,-21 10,-9C10,-1 1,-1 1,7" stroke="${INK}" stroke-width="5" fill="none" stroke-linecap="round"/><circle cx="1" cy="16" r="3.4" fill="${INK}"/></g>`,
    exclaim: `<g class="ic-pulse"><path d="M0,-18V5" stroke="#DC2626" stroke-width="6" stroke-linecap="round"/><circle cx="0" cy="15" r="3.8" fill="#DC2626"/></g>
      <path d="M-16,-14l-6,-5M16,-14l6,-5M-18,2h-7M18,2h7" stroke="#F59E0B" stroke-width="3" stroke-linecap="round"/>`,
    bulb: BULB,
    eureka: `<circle cx="0" cy="-4" r="24" fill="#FEF08A" opacity=".55" class="ic-pulse"/>${BULB}${star4(-24, -18, 7, 0)}${star4(24, -20, 6, 0.3)}${star4(22, 14, 5, 0.6)}`,
    heart: `<path class="ic-beat" d="M0,16C-26,0 -16,-22 0,-9C16,-22 26,0 0,16Z" fill="#F43F5E" stroke="#BE123C" stroke-width="2.5"/>
      <path class="ic-float" d="M22,-16C16,-20 18,-26 22,-22C26,-26 28,-20 22,-16Z" fill="#FB7185"/>`,
    peak: `${AX}<path class="ic-draw" pathLength="1" d="M-28,14C-18,-30 6,-30 14,0S26,10 30,4" stroke="#2563EB" stroke-width="3.5" fill="none" stroke-linecap="round"/>
      <path d="M-20,-21H8" stroke="#F59E0B" stroke-width="2.5" stroke-dasharray="4 3"/>
      <path d="M-6,-21V-36" stroke="#78350F" stroke-width="2.5"/><path class="ic-wobble" d="M-6,-36L8,-32L-6,-27Z" fill="#EF4444"/>`,
    slope: `<path d="M-28,16L26,-16" stroke="#2563EB" stroke-width="3.5" stroke-linecap="round"/>
      <path class="ic-draw" pathLength="1" d="M-8,4H14V-9" stroke="#DC2626" stroke-width="3" fill="none" stroke-dasharray="1" stroke-linejoin="round"/>
      <path d="M2,4A10,10 0 0,0 0.6,-1.6" stroke="#F59E0B" stroke-width="2.5" fill="none"/><circle cx="-8" cy="4" r="3" fill="#F59E0B"/>`,
    key: `<g class="ic-wobble"><circle cx="-13" cy="0" r="9" fill="none" stroke="#F59E0B" stroke-width="4.5"/>
      <path d="M-4,0H22M14,0V8M20,0V7" stroke="#F59E0B" stroke-width="4.5" stroke-linecap="round"/></g>${star4(18, -15, 7, 0.2)}`,
    wheee: `<path d="M-30,12Q-12,-26 6,4T30,-8" stroke="#92400E" stroke-width="3" fill="none"/>
      <g class="ic-float"><rect x="-4" y="-10" width="16" height="10" rx="2" fill="#EF4444" transform="rotate(-25 4 -5)"/></g>
      <path d="M-26,-14h-6M-24,-6h-7M-22,2h-5" stroke="#64748B" stroke-width="2.5" stroke-linecap="round"/>`,
    hammer: `<g class="ic-wobble"><path d="M-14,18L6,-4" stroke="#92400E" stroke-width="5" stroke-linecap="round"/>
      <path d="M-2,-14L14,2L8,8L-8,-8Z" fill="#64748B" stroke="#334155" stroke-width="2" stroke-linejoin="round"/></g>
      <path d="M18,-14l5,-5M22,-6h7M14,-20l1,-7" stroke="#F59E0B" stroke-width="2.5" stroke-linecap="round"/>`,
    integral: `<path d="${INTEGRAL}" stroke="#FDE68A" stroke-width="10" fill="none" stroke-linecap="round" opacity=".6"/>
      <path class="ic-draw" pathLength="1" d="${INTEGRAL}" stroke="#D97706" stroke-width="4.5" fill="none" stroke-linecap="round"/>${star4(-18, -14, 6, 0)}${star4(18, 10, 5, 0.4)}`,
    infinity: `<path d="${LEMNISCATE}" stroke="#7C3AED" stroke-width="4.5" fill="none"/>
      <circle r="4" fill="#F59E0B"><animateMotion dur="2.2s" repeatCount="indefinite" path="${LEMNISCATE}"/></circle>`,
    tangent: `${AX}<path class="ic-draw" pathLength="1" d="M-24,-20Q0,44 24,-20" stroke="#2563EB" stroke-width="3.5" fill="none" stroke-linecap="round"/>
      <path class="ic-draw" style="--d:.9s" pathLength="1" d="M0,20L25,-13.3" stroke="#DC2626" stroke-width="3" fill="none" stroke-linecap="round"/>
      <circle cx="12" cy="4" r="3.5" fill="#F59E0B"/>`,
    sine: `<path d="M-30,0H30" stroke="#94A3B8" stroke-width="2"/>
      <path class="ic-draw" pathLength="1" d="M-30,0C-24,-22 -16,-22 -10,0S4,22 10,0S24,-22 30,0" stroke="#0891B2" stroke-width="3.5" fill="none" stroke-linecap="round"/>`,
    area: `${AX}<path class="ic-grow" d="M-22,16V2Q-4,-30 24,-14V16Z" fill="#93C5FD"/>
      <path d="M-28,8Q-4,-34 28,-16" stroke="#2563EB" stroke-width="3.5" fill="none" stroke-linecap="round"/>`,
    riemann: `${AX}${[[-22, 12], [-10, 20], [2, 24], [14, 22]].map(([x, h], i) =>
      `<rect class="ic-grow" style="--d:${i * 0.18}s" x="${x}" y="${16 - h}" width="11" height="${h}" fill="#FDE047" stroke="#CA8A04" stroke-width="1.5"/>`).join('')}`,
    limit: `<path d="M-30,10H30" stroke="#94A3B8" stroke-width="2"/><path d="M20,-22V22" stroke="#DC2626" stroke-width="2.5" stroke-dasharray="4 4"/>
      <g class="ic-approach"><circle cx="0" cy="10" r="5.5" fill="#2563EB"/></g>`,
    stonks: `${AX}<path class="ic-draw" pathLength="1" d="M-24,10L-12,0L-4,6L8,-8L22,-18" stroke="#16A34A" stroke-width="3.5" fill="none" stroke-linejoin="round" stroke-linecap="round"/>`,
    pie: `<path d="M0,0L17.3,-10A20,20 0 1,0 17.3,10Z" fill="#FBBF24" stroke="#B45309" stroke-width="2.5" stroke-linejoin="round"/>
      <g class="ic-slice"><path d="M5,0L22.3,-10A20,20 0 0,1 22.3,10Z" fill="#FCD34D" stroke="#B45309" stroke-width="2.5" stroke-linejoin="round"/></g>`,
    apple: `<g class="ic-wobble"><circle cx="0" cy="4" r="15" fill="#EF4444" stroke="#B91C1C" stroke-width="2.5"/>
      <path d="M0,-10q2,-8 6,-10" stroke="#78350F" stroke-width="3" fill="none" stroke-linecap="round"/>
      <path d="M3,-14q10,-8 16,0q-8,6 -16,0z" fill="#22C55E"/><circle cx="-6" cy="-1" r="3" fill="#fff" opacity=".6"/></g>`,
    zzz: `<g class="ic-float" stroke="#6366F1" stroke-width="3.5" fill="none" stroke-linejoin="round" stroke-linecap="round">
      <path d="M-26,8h10l-10,10h10"/><path d="M-8,-4h13l-13,13h13"/><path d="M12,-20h16l-16,16h16"/></g>`,
    spiral: `<path class="ic-spin" d="M0,0m-2,0a2,2 0 1,1 4,0a5,5 0 1,1 -10,0a8,8 0 1,1 16,0a11,11 0 1,1 -22,0a14,14 0 1,1 28,0" stroke="#7C3AED" stroke-width="3" fill="none" stroke-linecap="round"/>`,
    sweat: `<g class="ic-drip"><path d="M8,-20C16,-6 18,2 8,10C-2,2 0,-6 8,-20Z" fill="#7DD3FC" stroke="#0284C7" stroke-width="2.5"/></g>
      <path d="M-14,-10l-8,-4M-14,0h-10M-14,10l-8,4" stroke="#0284C7" stroke-width="2.5" stroke-linecap="round"/>`,
    sparkle: star4(-14, 4, 13, 0) + star4(12, -10, 9, 0.3) + star4(16, 14, 6, 0.6),
    note: `<g class="ic-float" fill="#7C3AED"><ellipse cx="-12" cy="12" rx="7" ry="5"/><rect x="-6.5" y="-16" width="3" height="28"/>
      <path d="M-6.5,-16q12,4 10,14q-2,-8 -10,-8z"/><ellipse cx="14" cy="6" rx="6" ry="4.5"/><rect x="18.5" y="-18" width="3" height="24"/></g>`,
    laugh: `<g class="ic-shake"><circle r="20" fill="#FDE047" stroke="#CA8A04" stroke-width="2.5"/>
      <path d="M-11,-5q4,-6 8,0M3,-5q4,-6 8,0" stroke="#78350F" stroke-width="2.5" fill="none" stroke-linecap="round"/>
      <path d="M-11,4h22q-2,12 -11,12q-9,0 -11,-12z" fill="#9F1239"/></g>`,
    dots: [-14, 0, 14].map((x, i) => `<circle class="ic-dot" style="--d:${i * 0.15}s" cx="${x}" cy="0" r="5" fill="#64748B"/>`).join(''),
  };

  // ── Papan tulis ────────────────────────────────────────────────
  const OX = 260, OY = 328, SX = 23, SY = 17;
  const px = (x) => OX + x * SX;
  const py = (y) => OY - y * SY;
  function curve(f, a = -3.8, b = 3.8, n = 90) {
    let d = '';
    let pen = false;
    for (let i = 0; i <= n; i++) {
      const x = a + ((b - a) * i) / n;
      const y = py(f(x));
      if (!Number.isFinite(y) || y < 250 || y > 400) { pen = false; continue; }
      d += `${pen ? 'L' : 'M'}${px(x).toFixed(1)} ${y.toFixed(1)}`;
      pen = true;
    }
    return d;
  }
  const chalk = (d, color = '#F8FAFC') => `<path class="chalk" d="${d}" stroke="${color}" stroke-width="3" fill="none" stroke-linecap="round" stroke-linejoin="round"/>`;
  const dot = (x, y, color = '#FDE047', cls = 'chalk-dot') => `<circle class="${cls}" cx="${px(x)}" cy="${py(y)}" r="4.5" fill="${color}"/>`;
  const AXES = `<path d="M172 ${OY}H348M${OX} 264V386" stroke="#F8FAFC" stroke-width="1.5" opacity=".35"/>`;
  const wave = (x) => 1.1 + 0.35 * x + 0.5 * Math.sin(1.4 * x);
  const BOARD = {
    // Mengukur kemiringan garis singgung: segitiga naik/jalan + busur sudut (jangka).
    measure: () => {
      const f = (x) => (x * x) / 3 - 1;
      const a = 1.5, m = (2 * a) / 3;
      return chalk(curve(f)) + chalk(curve((x) => f(a) + m * (x - a), 0, 3.4), '#F9A8D4')
        + chalk(`M${px(a)} ${py(f(a))}H${px(a + 1.2)}V${py(f(a) + m * 1.2)}`, '#FDE047')
        + chalk(`M${px(a) + 16} ${py(f(a))}A16 16 0 0 0 ${(px(a) + 16 * Math.cos(Math.atan(m * SY / SX))).toFixed(1)} ${(py(f(a)) - 16 * Math.sin(Math.atan(m * SY / SX))).toFixed(1)}`, '#67E8F9')
        + dot(a, f(a));
    },
    // Titik potong parabola & garis — disorot berdenyut saat "Eureka!".
    intersect: () => {
      const f = (x) => (x * x) / 2 - 1.5;
      const g = (x) => 0.5 * x + 0.3;
      const r1 = (0.5 + Math.sqrt(0.25 + 3.6)) / 1, r2 = (0.5 - Math.sqrt(0.25 + 3.6)) / 1;   // akar x²/2 − x/2 − 1,8 = 0
      return chalk(curve(f)) + chalk(curve(g), '#86EFAC')
        + dot(r1, g(r1), '#FDE047', 'chalk-dot chalk-hit') + dot(r2, g(r2), '#FDE047', 'chalk-dot chalk-hit');
    },
    parabola: () => chalk(curve((x) => (x * x) / 3 - 1)),
    sine: () => chalk(curve((x) => 1.6 * Math.sin(1.7 * x)), '#67E8F9'),
    area: () => `<path class="chalk-dot" d="${curve(wave, -2, 2.2)}L${px(2.2)} ${OY}L${px(-2)} ${OY}Z" fill="#FDE047" opacity=".35"/>${chalk(curve(wave))}`,
    riemann: () => Array.from({ length: 6 }, (_, i) => {
      const x = -2 + 0.7 * i;
      const h = wave(x + 0.35);
      return `<rect class="chalk-bar" x="${px(x)}" y="${py(h)}" width="${0.7 * SX}" height="${h * SY}" fill="#FDE047" opacity=".45" stroke="#FDE047"/>`;
    }).join('') + chalk(curve(wave)),
    limit: () => {
      const f = (x) => (2.4 * Math.sin(1.8 * x)) / (1.8 * x);
      return chalk(curve(f, -3.8, -0.06)) + chalk(curve(f, 0.06, 3.8))
        + `<circle class="chalk-dot" cx="${OX}" cy="${py(2.4)}" r="4.5" fill="#14532D" stroke="#FDE047" stroke-width="2.5"/>`;
    },
    cubic: () => {
      const f = (x) => (x ** 3 - 4 * x) / 2.2;
      const e = 2 / Math.sqrt(3);
      return chalk(curve(f, -2.6, 2.6), '#86EFAC') + dot(-e, f(-e)) + dot(e, f(e), '#F9A8D4');
    },
    circle: () => `${chalk('M216 324a44 44 0 1 0 88 0a44 44 0 1 0 -88 0')}
      <path d="M260 324h44" stroke="#F9A8D4" stroke-width="3" stroke-linecap="round"><animateTransform attributeName="transform" type="rotate" from="0 260 324" to="360 260 324" dur="4s" repeatCount="indefinite"/></path>`,
  };
  const BOARD_ICON = { measure: 'slope', intersect: 'eureka', parabola: 'tangent', sine: 'sine', area: 'area', riemann: 'riemann', limit: 'limit', cubic: 'stonks', circle: 'pie' };
  // Rumus yang ditulis Hijau saat pengguna mengetik (bukan teks yang diketik pengguna).
  const FORMULAS = ["f'(x) = 0", '∫ x² dx = x³/3 + C', 'lim sin x / x = 1', 'd/dx eˣ = eˣ', 'Σ 1/n² = π²/6', 'dy/dx = 2x'];

  // ── Item koleksi ───────────────────────────────────────────────
  const ITEM_KINDS = {
    apel: { label: 'Apel emas Newton', svg: `<circle r="10" fill="url(#fam-gold)" stroke="#B45309" stroke-width="2"/><path d="M0 -10q1-5 4-6" stroke="#78350F" stroke-width="2" fill="none"/>
      <path d="M2 -12q7-6 11 0q-6 4-11 0z" fill="#22C55E"/><circle cx="-3" cy="-3" r="2.5" fill="#fff" opacity=".7"/>` },
    bintang: { label: 'Bintang titik ekstremum', svg: `<path d="M0-12l3.5 7.5 8 1-6 5.5 1.6 8L0 6l-7.1 4 1.6-8-6-5.5 8-1z" fill="url(#fam-gold)" stroke="#B45309" stroke-width="1.8" stroke-linejoin="round"/>
      <path d="M-5 3q5-8 10 0" stroke="#fff" stroke-width="1.6" fill="none" opacity=".85"/>` },
    dx: { label: 'Kristal dx', svg: `<path d="M0-13L10 0 0 13-10 0Z" fill="#67E8F9" stroke="#0E7490" stroke-width="2" stroke-linejoin="round"/>
      <path d="M0-13L4 0 0 13" stroke="#fff" stroke-width="1" opacity=".6" fill="none"/>
      <text y="3.5" text-anchor="middle" font-size="8" font-weight="800" fill="#0E7490" font-family="system-ui,sans-serif">dx</text>` },
  };
  const MAX_ITEMS = 5;

  // ── Adegan ─────────────────────────────────────────────────────
  const APPLES = [[32, 322], [98, 292], [122, 352], [66, 372], [88, 330]];
  const APPLE = '<circle r="9" fill="#EF4444" stroke="#B91C1C" stroke-width="2"/><path d="M0,-9q1,-5 4,-6" stroke="#78350F" stroke-width="2" fill="none"/><circle cx="-3" cy="-3" r="2" fill="#fff" opacity=".6"/>';

  // Langit, bukit, dan tebing diperluas ke kiri/kanan/bawah agar bisa jadi latar layar penuh.
  const X0 = -2400;
  const X1 = 3000;
  const YBOT = 2400;
  const LEFT_EDGE = 372;    // tebing masalah berakhir
  const RIGHT_EDGE = 790;   // tebing solusi dimulai
  const onLand = (x) => x < LEFT_EDGE - 30 || x > RIGHT_EDGE + 30;

  function hills(y, amp, step, fill) {
    let d = `M${X0} ${y}`;
    for (let x = X0, i = 0; x < X1; x += step, i++) d += `Q${x + step / 2} ${y + (i % 2 ? amp : -amp)} ${x + step} ${y}`;
    return `<path d="${d}V${YBOT}H${X0}Z" fill="${fill}"/>`;
  }
  function hillY(y, amp, step, x) {
    const i = Math.floor((x - X0) / step);
    const t = (x - X0) / step - i;
    return y + 2 * t * (1 - t) * (i % 2 ? amp : -amp);
  }
  const scatter = (n, x0, x1, y0, y1, fn) => Array.from({ length: n }, (_, i) => {
    const x = x0 + ((x1 - x0) * (i + rand(0.15, 0.85))) / n;
    return fn(x, rand(y0, y1), i);
  }).join('');

  const farTree = (x) => (x > 140 && x < 380 ? '' : `<g transform="translate(${x.toFixed(0)} ${(hillY(512, 26, 240, x) + 6).toFixed(0)}) scale(${rand(0.5, 0.9).toFixed(2)})">
    <rect x="-3" y="-6" width="6" height="16" fill="#7C9A6B"/><circle cy="-18" r="16" fill="#6CC08B"/><circle cx="-9" cy="-10" r="11" fill="#5DB37E"/><circle cx="9" cy="-11" r="12" fill="#5DB37E"/></g>`);
  const bush = (x) => (!onLand(x) || (x > -80 && x < 400) ? '' : `<g transform="translate(${x.toFixed(0)} ${x < LEFT_EDGE ? 614 : 592})"><g class="fam-bush" style="animation-delay:${rand(0, 3).toFixed(2)}s">
    <circle cx="-22" cy="-14" r="20" fill="#22C55E"/><circle cx="20" cy="-14" r="22" fill="#22C55E"/><circle cy="-26" r="26" fill="#34D399"/>
    <circle cx="-6" cy="-30" r="3.5" fill="#F9A8D4"/><circle cx="14" cy="-20" r="3.5" fill="#FDE047"/></g></g>`);
  const grass = (x, y) => (!onLand(x) ? '' : `<g transform="translate(${x.toFixed(0)} ${y.toFixed(0)})"><path class="fam-grass" style="animation-delay:${rand(0, 2.5).toFixed(2)}s"
    d="M-4 0q-1-7-7-11M-2 0q-1-10 1-15M1 0q1-8 5-13M3 0q3-5 9-7" stroke="${pick(['#16A34A', '#22A55A', '#15803D'])}" stroke-width="1.8" fill="none" stroke-linecap="round"/></g>`);
  const FLOWER_COLORS = ['#F472B6', '#FDE047', '#F87171', '#A78BFA', '#FFFFFF', '#FB923C'];
  const flower = (x, y, col = pick(FLOWER_COLORS)) => (!onLand(x) ? '' : `<g transform="translate(${x.toFixed(0)} ${y.toFixed(0)})"><g class="fam-flower" style="animation-delay:${rand(0, 2).toFixed(2)}s">
    <path d="M0 0V-16" stroke="#15803D" stroke-width="2.5"/><g transform="translate(0 -18)" fill="${col}">
    <circle cx="-4" r="4"/><circle cx="4" r="4"/><circle cy="-4" r="4"/><circle cy="4" r="4"/><circle r="2.6" fill="#F59E0B"/></g></g></g>`);
  const birds = (y, dur, delay) => `<g class="fam-bird" style="animation-duration:${dur}s;animation-delay:${delay}s">
    ${[[0, 0], [26, -10], [30, 14]].map(([bx, by]) => `<g transform="translate(${bx} ${y + by})"><path class="fam-bird-wing"
      d="M-9 0q4.5-6 9 0q4.5-6 9 0" stroke="#334155" stroke-width="2.2" fill="none" stroke-linecap="round" style="animation-delay:${rand(0, 0.5).toFixed(2)}s"/></g>`).join('')}</g>`;

  function bridgeMarkup() {
    const sample = (off, step = 6) => {
      let d = '';
      for (let x = BX0 - 4; x <= BX1 + 4; x += step) d += `${d ? 'L' : 'M'}${x} ${(bridgeY(x) + off).toFixed(1)}`;
      return d;
    };
    const pillars = [440, 560, 700].map((x) => `<path d="M${x} ${bridgeY(x) + 6}V780" stroke="#78350F" stroke-width="8" stroke-linecap="round"/>`).join('');
    const posts = [];
    const planks = [];
    for (let x = BX0 + 4, i = 0; x <= BX1 - 4; x += 11, i++) {
      const gap = x >= GAP[0] && x <= GAP[1];
      planks.push(`<rect class="fam-plank${gap ? ' missing' : ''}" x="-5" y="-3" width="10" height="7" rx="1.5" fill="#B45309" stroke="#78350F" stroke-width="1.2"
        transform="translate(${x} ${bridgeY(x).toFixed(1)}) rotate(${slopeDeg(x).toFixed(1)})"/>`);
      if (i % 4 === 0) posts.push(`<path d="M${x} ${bridgeY(x).toFixed(1)}V${(bridgeY(x) - 26).toFixed(1)}" stroke="#92400E" stroke-width="3" stroke-linecap="round"/>`);
    }
    return `<g class="fam-bridge" data-hit="bridge">
      ${pillars}<path d="M440 650L560 700M560 650L440 700M560 660L700 700M700 660L560 700" stroke="#92400E" stroke-width="3" opacity=".8"/>
      <path d="${sample(5)}" stroke="#78350F" stroke-width="4" fill="none"/>
      ${planks.join('')}${posts.join('')}
      <path d="${sample(-26)}" stroke="#92400E" stroke-width="3" fill="none" stroke-linecap="round"/>
      <path class="fam-peakline" d="M${PEAK_X - 62} ${PEAK_Y.toFixed(1)}H${PEAK_X + 62}" stroke="#FBBF24" stroke-width="3" stroke-dasharray="6 6"/>
    </g>
    <g class="fam-flag" data-hit="flag" transform="translate(${FLAG_X} ${deckY(FLAG_X).toFixed(1)})"><g class="fam-flag-in">
      <path d="M0 0V-104" stroke="#78350F" stroke-width="4" stroke-linecap="round"/>
      <path class="fam-flag-cloth" d="M2 -102L50 -88L2 -72Z" fill="#EF4444" stroke="#B91C1C" stroke-width="2" stroke-linejoin="round"/>
      ${star4(17, -87, 6, 0, '#FDE047')}</g></g>`;
  }

  function sceneMarkup() {
    const stars = Array.from({ length: 110 }, () =>
      `<circle class="fam-star" cx="${rand(X0, X1).toFixed(0)}" cy="${rand(-900, 300).toFixed(0)}" r="${rand(1, 2.4).toFixed(1)}" style="animation-delay:${rand(0, 3).toFixed(2)}s"/>`).join('');
    const rays = Array.from({ length: 12 }, (_, i) => {
      const a = (i * Math.PI) / 6;
      return `<path d="M${(Math.cos(a) * 41).toFixed(1)} ${(Math.sin(a) * 41).toFixed(1)}L${(Math.cos(a) * 52).toFixed(1)} ${(Math.sin(a) * 52).toFixed(1)}"/>`;
    }).join('');
    const fireflies = Array.from({ length: 30 }, () =>
      `<circle class="fam-firefly" cx="${rand(-1500, 2100).toFixed(0)}" cy="${rand(430, 660).toFixed(0)}" r="2.6" style="animation-delay:${rand(0, 3).toFixed(2)}s;--fx:${rand(-22, 22).toFixed(0)}px"/>`).join('');
    const cloud = (y, s, dur, delay) => `<g class="fam-cloud" style="animation-duration:${dur}s;animation-delay:${delay}s">
      <path transform="translate(0 ${y}) scale(${s})" d="M0 30a22 22 0 0 1 20-28a30 30 0 0 1 56 4a20 20 0 0 1 24 24z" fill="#fff" opacity=".92"/></g>`;
    const clouds = [[60, 1, 170], [150, 0.7, 240], [30, 0.55, 200], [-120, 1.3, 260], [-40, 0.8, 190], [220, 0.6, 280],
      [-220, 1.1, 230], [100, 0.9, 210], [-160, 0.7, 250], [190, 1.2, 300], [-60, 0.6, 180]]
      .map(([y, s, dur]) => cloud(y, s, dur, -rand(0, dur).toFixed(0))).join('');
    const LEFT_LAND = `M${X0} 604Q-1200 594 -600 600T300 600L${LEFT_EDGE - 12} 600Q${LEFT_EDGE + 4} 601 ${LEFT_EDGE + 10} 614L${LEFT_EDGE + 26} 690Q${LEFT_EDGE + 30} 730 ${LEFT_EDGE + 22} ${YBOT}H${X0}Z`;
    const RIGHT_LAND = `M${X1} 579H900Q830 576 ${RIGHT_EDGE + 8} 578Q${RIGHT_EDGE - 6} 580 ${RIGHT_EDGE - 12} 594L${RIGHT_EDGE - 26} 680Q${RIGHT_EDGE - 30} 730 ${RIGHT_EDGE - 22} ${YBOT}H${X1}Z`;
    const strata = (x, dir) => [640, 680, 720].map((y, i) => `M${x - dir * (8 + i * 2)} ${y}l${dir * 46} ${6 + i * 2}`).join('');

    return `<defs>
        <linearGradient id="fam-day" gradientUnits="userSpaceOnUse" x1="0" y1="-500" x2="0" y2="560"><stop offset="0" stop-color="#38BDF8"/><stop offset=".55" stop-color="#7DD3FC"/><stop offset="1" stop-color="#E0F2FE"/></linearGradient>
        <linearGradient id="fam-night" gradientUnits="userSpaceOnUse" x1="0" y1="-500" x2="0" y2="560"><stop offset="0" stop-color="#020617"/><stop offset=".5" stop-color="#0F172A"/><stop offset="1" stop-color="#3730A3"/></linearGradient>
        <linearGradient id="fam-gold" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#FEF3C7"/><stop offset=".5" stop-color="#FCD34D"/><stop offset="1" stop-color="#F59E0B"/></linearGradient>
        <linearGradient id="fam-river" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#7DD3FC"/><stop offset="1" stop-color="#0284C7"/></linearGradient>
        <radialGradient id="fam-magic"><stop offset="0" stop-color="#E9D5FF" stop-opacity=".95"/><stop offset=".6" stop-color="#A78BFA" stop-opacity=".45"/><stop offset="1" stop-color="#A78BFA" stop-opacity="0"/></radialGradient>
        <marker id="fam-arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0L10 5L0 10Z" fill="#F97316"/></marker>
        <clipPath id="fam-board-clip"><rect x="170" y="262" width="180" height="126" rx="4"/></clipPath>
        <clipPath id="fam-land"><path d="${LEFT_LAND}"/><path d="${RIGHT_LAND}"/></clipPath>
      </defs>
      <rect x="${X0}" y="-2000" width="${X1 - X0}" height="${YBOT + 2000}" fill="url(#fam-day)"/>
      <rect class="fam-night-sky" x="${X0}" y="-2000" width="${X1 - X0}" height="${YBOT + 2000}" fill="url(#fam-night)"/>
      <g class="fam-stars" fill="#fff">${stars}</g>
      <g class="fam-sun" data-hit="sun" transform="translate(560 110)"><g class="fam-sun-in">
        <g class="fam-rays" stroke="#FBBF24" stroke-width="5" stroke-linecap="round">${rays}</g>
        <circle r="32" fill="#FDE047" stroke="#F59E0B" stroke-width="3"/>
        <circle cx="-10" cy="-4" r="3" fill="#92400E"/><circle cx="10" cy="-4" r="3" fill="#92400E"/>
        <path d="M-9 8q9 8 18 0" stroke="#92400E" stroke-width="3" fill="none" stroke-linecap="round"/></g></g>
      <g class="fam-moon" data-hit="sun" transform="translate(560 110)">
        <path d="M8,-30A30,30 0 1,0 8,30A22,22 0 1,1 8,-30Z" fill="#FEF3C7" stroke="#FCD34D" stroke-width="2"/>
        <path d="M-14 -4q4 3 8 0" stroke="#92400E" stroke-width="2.5" fill="none" stroke-linecap="round"/></g>
      ${clouds}
      ${birds(40, 70, -20)}${birds(-60, 95, -70)}
      ${hills(478, 34, 600, '#CDEFE3')}
      ${hills(512, 26, 240, '#BBF7D0')}
      ${scatter(46, X0 + 100, X1 - 100, 500, 518, farTree)}
      <path d="M${LEFT_EDGE - 40} 560Q560 640 ${RIGHT_EDGE + 40} 556V800H${LEFT_EDGE - 40}Z" fill="#7CC79A"/>
      <path d="M${LEFT_EDGE - 40} 704Q470 690 590 706T${RIGHT_EDGE + 60} 698V800H${LEFT_EDGE - 40}Z" fill="url(#fam-river)"/>
      <g class="fam-shimmer" stroke="#fff" stroke-width="2" fill="none" stroke-linecap="round" opacity=".7">
        <path d="M420 716q10-4 20 0t20 0"/><path d="M560 724q10-4 20 0t20 0"/><path d="M680 714q10-4 20 0t20 0"/></g>
      ${bridgeMarkup()}
      <path d="${LEFT_LAND}" fill="#86EFAC"/>
      <path d="M${LEFT_EDGE - 26} 606Q${LEFT_EDGE + 2} 602 ${LEFT_EDGE + 10} 616L${LEFT_EDGE + 26} 690Q${LEFT_EDGE + 30} 730 ${LEFT_EDGE + 22} 800L${LEFT_EDGE - 40} 800L${LEFT_EDGE - 32} 660Z" fill="#C08A50"/>
      <path d="${strata(LEFT_EDGE - 10, 1)}" stroke="#A16A33" stroke-width="3" stroke-linecap="round"/>
      <path d="${RIGHT_LAND}" fill="#86EFAC"/>
      <path d="M${RIGHT_EDGE + 16} 584Q${RIGHT_EDGE - 4} 580 ${RIGHT_EDGE - 12} 594L${RIGHT_EDGE - 26} 680Q${RIGHT_EDGE - 30} 730 ${RIGHT_EDGE - 22} 800L${RIGHT_EDGE + 40} 800L${RIGHT_EDGE + 34} 650Z" fill="#C08A50"/>
      <path d="${strata(RIGHT_EDGE + 10, -1)}" stroke="#A16A33" stroke-width="3" stroke-linecap="round"/>
      <g clip-path="url(#fam-land)">${hills(652, 16, 400, '#4ADE80')}</g>
      <g class="fam-tree" data-hit="tree">
        <path d="M54 640C60 560 62 470 70 400L82 400C86 470 88 560 98 640Z" fill="#92400E" stroke="#78350F" stroke-width="3"/>
        <path d="M74 450Q50 430 40 410M80 430Q100 410 116 404" stroke="#78350F" stroke-width="6" fill="none" stroke-linecap="round"/>
        <g class="fam-crown"><circle cx="32" cy="335" r="52" fill="#22C55E"/><circle cx="120" cy="340" r="50" fill="#22C55E"/>
          <circle cx="76" cy="292" r="66" fill="#4ADE80"/><circle cx="74" cy="368" r="48" fill="#16A34A"/>
          ${APPLES.map(([x, y]) => `<g transform="translate(${x} ${y})">${APPLE}</g>`).join('')}</g>
      </g>
      <g class="fam-board" data-hit="board">
        <path d="M196 254L172 612M324 254L348 612" stroke="#92400E" stroke-width="8" stroke-linecap="round"/>
        <path d="M260 240V604" stroke="#78350F" stroke-width="6" stroke-linecap="round"/>
        <rect x="160" y="252" width="200" height="146" rx="8" fill="#A16207" stroke="#78350F" stroke-width="4"/>
        <rect x="170" y="262" width="180" height="126" rx="4" fill="#14532D"/>
        <g clip-path="url(#fam-board-clip)"><g class="fam-plot"></g></g>
        <rect x="176" y="398" width="168" height="8" rx="3" fill="#78350F"/>
        <rect x="296" y="391" width="13" height="7" rx="2" fill="#F8FAFC"/><rect x="314" y="390" width="16" height="8" rx="2" fill="#FDE047"/>
      </g>
      ${scatter(14, -2000, 2600, 0, 0, bush)}
      ${scatter(200, -2000, 2600, 640, 718, grass)}
      ${scatter(70, -1800, 2400, 650, 716, (x, y) => flower(x, y))}
      ${[[20, 690], [200, 704], [350, 686], [-60, 700]].map(([x, y], i) => flower(x, y, FLOWER_COLORS[i])).join('')}
      <rect class="fam-tint" x="${X0}" y="-2000" width="${X1 - X0}" height="${YBOT + 2000}" fill="#1E1B4B" pointer-events="none"/>
      <g class="fam-items"></g>
      ${ORDER.map(axolotl).join('')}
      <g class="fam-fireflies" fill="#FDE047" pointer-events="none">${fireflies}</g>
      <g class="fam-butterfly" data-hit="butterfly"><circle r="16" fill="transparent"/>
        <g class="fam-wing fam-wing-l"><ellipse cx="-7" cy="-4" rx="8" ry="6" fill="#F472B6"/><ellipse cx="-5" cy="5" rx="5" ry="4" fill="#FB923C"/></g>
        <g class="fam-wing fam-wing-r"><ellipse cx="7" cy="-4" rx="8" ry="6" fill="#F472B6"/><ellipse cx="5" cy="5" rx="5" ry="4" fill="#FB923C"/></g>
        <rect x="-1.5" y="-8" width="3" height="16" rx="1.5" fill="${INK}"/>
        <path d="M-1 -8q-3-5-6-6M1 -8q3-5 6-6" stroke="${INK}" stroke-width="1.2" fill="none"/></g>
      <g class="fam-fx" pointer-events="none"></g>
      ${ORDER.map(bubble).join('')}`;
  }

  // ── Keadaan ────────────────────────────────────────────────────
  let svg, plot, fx, tree, itemsLayer, hud, stageEl;
  const st = {};
  const pointer = { x: 0, y: 0, t: -1e9 };
  const bf = { x: 200, y: 190, t: 0, speed: 1, land: null, node: null };
  const counts = { apel: 0, bintang: 0, dx: 0 };
  let boardKind = 'measure';
  let writing = null;        // { f, c, lines } saat Hijau menulis rumus (pengguna mengetik)
  let writeTimer = 0;
  let lastHop = 0;
  let bridgeDone = false;
  let night = false;

  const visible = () => !document.hidden;
  const free = (id) => !st[id].busy && !st[id].sleeping;

  function setMouth(id, kind) {
    const [d, fill] = MOUTH[kind];
    st[id].mouth.setAttribute('d', d);
    st[id].mouth.setAttribute('fill', fill);
  }

  /** Pindahkan tokoh (kaki di x,y; miring rot derajat) beserta jangkar gelembungnya. */
  function setPos(id, x, y, rot = 0) {
    const s = st[id];
    const c = CHARS[id];
    s.x = x;
    s.y = y;
    s.pos.setAttribute('transform', `translate(${x.toFixed(1)} ${y.toFixed(1)}) rotate(${rot.toFixed(1)}) scale(${c.s})`);
    s.banchor.setAttribute('transform', `translate(${(x + c.bx).toFixed(1)} ${(y + (48 - 172) * c.s).toFixed(1)}) scale(.82)`);
  }
  const facePoint = (id) => ({ x: st[id].x, y: st[id].y + (110 - 172) * CHARS[id].s });

  function walk(id, x, y, ms, ease = easeInOut) {
    const x0 = st[id].x;
    const y0 = st[id].y;
    return tween(ms, (t) => setPos(id, x0 + (x - x0) * t, y0 + (y - y0) * t), ease);
  }
  /** Bergerak di sepanjang jembatan; lift = jarak kaki di atas dek; tilt = miring ikut kurva. */
  function alongBridge(id, x1, ms, { tilt = false, lift = 0, ease = easeInOut } = {}) {
    const x0 = st[id].x;
    return tween(ms, (t) => {
      const x = x0 + (x1 - x0) * t;
      setPos(id, x, deckY(x) - lift, tilt ? slopeDeg(x) : 0);
    }, ease);
  }

  const ANIM_MS = { jump: 600, hop: 380, spin: 800, shake: 900, nod: 800, wiggle: 1200, startle: 500, dizzy: 1300, bounce: 1000,
    stretch: 1400, wave: 1000, captoss: 1200, proud: 1400, measure: 1600, hammer: 900, netcatch: 600, monocle: 1700 };

  /** Jalankan satu aksi (kelas CSS do-*) dan tunggu sampai selesai. */
  function act(id, anim) {
    const node = st[id].el;
    [...node.classList].filter((k) => k.startsWith('do-')).forEach((k) => node.classList.remove(k));
    void node.getBoundingClientRect();
    node.classList.add(`do-${anim}`);
    clearTimeout(st[id].actTimer);
    st[id].actTimer = setTimeout(() => node.classList.remove(`do-${anim}`), ANIM_MS[anim]);
    return sleep(ANIM_MS[anim]);
  }

  function lookAt(id, ref, ms) { st[id].look = { ref, until: performance.now() + ms }; }

  function talk(id, ms) {
    const s = st[id];
    if (s.sleeping) return;
    clearInterval(s.talkTimer);
    const end = performance.now() + ms;
    let open = false;
    s.talkTimer = setInterval(() => {
      open = !open && performance.now() < end;
      setMouth(id, open ? 'open' : 'smile');
      if (performance.now() >= end) clearInterval(s.talkTimer);
    }, 150);
  }

  /** Gelembung ikon. Selesai (resolve) sedikit sebelum gelembung hilang. */
  function say(id, icon, hold = 2000, { mouth = true } = {}) {
    const s = st[id];
    s.icon.innerHTML = ICONS[icon];
    s.bubble.classList.remove('show');
    void s.bubble.getBoundingClientRect();
    s.bubble.classList.add('show');
    clearTimeout(s.bubbleTimer);
    s.bubbleTimer = setTimeout(() => s.bubble.classList.remove('show'), hold);
    if (mouth) talk(id, Math.min(900, hold));
    ORDER.filter((o) => o !== id).forEach((o) => lookAt(o, facePoint(id), hold * 0.8));
    return sleep(hold * 0.8);
  }

  /** Tokoh lain yang sedang bebas ikut bersorak (tidak ditunggu). */
  function cheerOthers(except, icons = ['sparkle', 'heart', 'laugh']) {
    ORDER.filter((o) => !except.includes(o) && free(o)).forEach((o, i) => {
      setTimeout(() => { act(o, 'jump'); say(o, pick(icons), 1500); }, 200 + i * 260);
    });
  }

  function sleepOn(id) { st[id].sleeping = true; st[id].el.classList.add('is-sleep'); setMouth(id, 'flat'); }
  function wake(id) { st[id].sleeping = false; st[id].el.classList.remove('is-sleep'); setMouth(id, 'smile'); }
  const toggle = (id, cls, on) => st[id].el.classList.toggle(cls, on);
  const setFlag = (on) => { svg.querySelector('.fam-flag-in').classList.toggle('is-down', !on); svg.querySelector('.fam-peakline').classList.toggle('on', on); };

  function board(kind = pick(Object.keys(BOARD), boardKind)) {
    boardKind = kind;
    if (writing) return;   // Hijau sedang menulis rumus; grafik digambar setelah selesai
    plot.innerHTML = AXES + BOARD[kind]();
    if (REDUCED) return;
    plot.querySelectorAll('.chalk').forEach((p, i) => {
      const len = p.getTotalLength();
      p.style.strokeDasharray = len;
      p.animate([{ strokeDashoffset: len }, { strokeDashoffset: 0 }], { duration: 1000, delay: i * 380, easing: 'ease-out', fill: 'both' });
    });
    plot.querySelectorAll('.chalk-dot').forEach((p) => p.animate([{ opacity: 0 }, { opacity: p.getAttribute('opacity') || 1 }], { duration: 500, delay: 1100, fill: 'backwards' }));
    plot.querySelectorAll('.chalk-bar').forEach((p, i) => p.animate([{ transform: 'scaleY(0)' }, { transform: 'scaleY(1)' }], { duration: 400, delay: 200 + i * 160, easing: 'ease-out', fill: 'backwards' }));
  }

  /** Saat pengguna mengetik: Hijau menulis satu karakter rumus per ketukan di papan. */
  function writeFormula() {
    if (!writing) writing = { f: Math.floor(rand(0, FORMULAS.length)), c: 0, lines: [''] };
    const formula = FORMULAS[writing.f % FORMULAS.length];
    writing.lines[writing.lines.length - 1] = formula.slice(0, ++writing.c);
    if (writing.c >= formula.length) { writing.f++; writing.c = 0; writing.lines.push(''); }
    if (writing.lines.length > 3) writing.lines = writing.lines.slice(-1);   // papan penuh: hapus
    plot.innerHTML = writing.lines.map((t, i) => `<text class="chalk-text" x="180" y="${294 + i * 34}">${t}</text>`).join('');
    clearTimeout(writeTimer);
    writeTimer = setTimeout(() => { writing = null; board(boardKind); }, 2600);
  }

  // ── Efek ───────────────────────────────────────────────────────
  const BITS = [
    '<circle r="5" fill="#F472B6"/>', '<path d="M0-6L6 5H-6Z" fill="#FBBF24"/>',
    '<path d="M-7 0q3.5-7 7 0t7 0" stroke="#2563EB" stroke-width="2.5" fill="none" stroke-linecap="round"/>',
    '<path d="M-5 0h10M0-5v10" stroke="#16A34A" stroke-width="3" stroke-linecap="round"/>',
    '<rect x="-4" y="-4" width="8" height="8" rx="2" fill="#38BDF8"/>',
  ];
  const GOLD = [star4(0, 0, 6, 0, '#FDE047'), '<circle r="3.5" fill="#FBBF24"/>', star4(0, 0, 4, 0, '#FEF3C7')];

  function burst(x, y, n = 9, bits = BITS) {
    for (let i = 0; i < n; i++) {
      const g = make('g', {}, pick(bits));
      fx.appendChild(g);
      const ang = (i / n) * Math.PI * 2 + rand(-0.3, 0.3);
      const dist = rand(30, 70);
      const tx = x + Math.cos(ang) * dist;
      const ty = y + Math.sin(ang) * dist;
      g.animate([
        { transform: `translate(${x}px, ${y}px) scale(.3)`, opacity: 1 },
        { transform: `translate(${tx}px, ${ty}px) scale(1.2) rotate(${rand(-200, 200)}deg)`, opacity: 1, offset: 0.6 },
        { transform: `translate(${tx}px, ${ty + 24}px) scale(.8) rotate(${rand(-300, 300)}deg)`, opacity: 0 },
      ], { duration: rand(800, 1200), easing: 'cubic-bezier(.2,.7,.3,1)' }).finished.then(() => g.remove());
    }
  }

  const fadeOut = (node, delay = 0) => node.animate([{ opacity: 1 }, { opacity: 0 }], { duration: 500, delay, fill: 'forwards' }).finished.then(() => node.remove());

  function rustleTree() {
    tree.classList.remove('do-rustle');
    void tree.getBoundingClientRect();
    tree.classList.add('do-rustle');
  }

  /**
   * Apel gravitasi jatuh dari (ax,ay) ke (tx,ty): x bergerak rata, y kuadratik (dipercepat).
   * Di belakangnya tergambar jejak lintasan melengkung + panah arah kecepatan.
   */
  function dropApple(ax, ay, tx, ty, ms) {
    const trail = make('path', { class: 'fam-trail', 'marker-end': 'url(#fam-arrow)' });
    const apple = make('g', {}, APPLE);
    fx.append(trail, apple);
    const at = (t) => [ax + (tx - ax) * t, ay + (ty - ay) * t * t];
    return tween(ms, (t) => {
      const [x, y] = at(t);
      apple.setAttribute('transform', `translate(${x.toFixed(1)} ${y.toFixed(1)}) rotate(${(t * 220).toFixed(0)})`);
      const pts = Array.from({ length: 12 }, (_, i) => at((t * i) / 11).map((v) => v.toFixed(1)).join(' '));
      trail.setAttribute('d', `M${pts.join('L')}`);
    }, (t) => t).then(() => ({ apple, trail }));
  }

  /** Simbol ∫ / ∞ berpendar emas (untuk mantra Ungu). */
  function glyph(d) {
    const g = make('g', { class: 'fam-glyph' }, `<path d="${d}" stroke="#FEF08A" stroke-width="12" fill="none" stroke-linecap="round" opacity=".55"/>
      <path d="${d}" stroke="#F59E0B" stroke-width="5" fill="none" stroke-linecap="round"/>`);
    fx.appendChild(g);
    return g;
  }

  /** Titik tepi kiri kartu login dalam koordinat adegan (gerbang menuju level berikutnya). */
  function gatePoint() {
    const card = document.querySelector('.auth-split .auth-card');
    const vb = svg.viewBox.baseVal;
    if (!card || BANNER.matches) return { x: vb.x + vb.width + 30, y: st.ungu.y - 60 };
    const r = card.getBoundingClientRect();
    return toSvg({ clientX: r.left + 12, clientY: r.top + r.height * 0.35 });
  }

  // ── Skrip adegan ───────────────────────────────────────────────
  const SCRIPTS = {
    // Tim merakit papan jembatan yang masih bolong (sekali di awal).
    rakit: {
      chars: ['hijau', 'archie'],
      when: () => !bridgeDone,
      async run() {
        const gx = (GAP[0] + GAP[1]) / 2;
        ORDER.forEach((o) => lookAt(o, { x: gx, y: bridgeY(gx) }, 4000));
        await say('archie', 'question', 1500);
        act('hijau', 'wave');
        await sleep(300);
        const plank = make('rect', { x: -16, y: -4, width: 32, height: 8, rx: 2, fill: '#B45309', stroke: '#78350F', 'stroke-width': 1.5 });
        fx.appendChild(plank);
        const [x0, y0] = [st.hijau.x + 40, st.hijau.y - 90];
        const [x1, y1] = [gx, bridgeY(gx)];
        await tween(1000, (t) => {
          const x = x0 + (x1 - x0) * t;
          const y = (1 - t) ** 2 * y0 + 2 * (1 - t) * t * (Math.min(y0, y1) - 160) + t * t * y1;   // lemparan parabola
          plank.setAttribute('transform', `translate(${x.toFixed(1)} ${y.toFixed(1)}) rotate(${(t * 540).toFixed(0)})`);
        }, (t) => t);
        plank.remove();
        svg.querySelectorAll('.fam-plank.missing').forEach((p, i) => setTimeout(() => p.classList.remove('missing'), i * 90));
        act('archie', 'hammer');
        say('archie', 'hammer', 1600);
        for (let i = 0; i < 3; i++) { burst(x1 + rand(-14, 14), y1, 5, GOLD); await sleep(300); }
        bridgeDone = true;
        cheerOthers(['archie'], ['sparkle', 'heart']);
        await say('hijau', 'sparkle', 1500);
      },
    },

    // Archie — menantang: turun ke kaki kurva, mendaki, lalu menancapkan bendera di maksimum lokal.
    archieClimb: {
      chars: ['archie'],
      async run() {
        setFlag(false);
        await say('archie', 'dots', 1200);
        await alongBridge('archie', BX0 + 24, 900, { tilt: true, ease: easeIn });
        setPos('archie', st.archie.x, st.archie.y);
        setMouth('archie', 'flat');
        say('archie', 'sweat', 1500, { mouth: false });
        const start = st.archie.x;
        for (let i = 1; i <= 7; i++) {
          act('archie', 'hop');
          await alongBridge('archie', start + ((PEAK_X - start) * i) / 7, 360);
        }
        setMouth('archie', 'grin');
        setFlag(true);
        burst(FLAG_X + 20, deckY(FLAG_X) - 96, 10, GOLD);
        act('archie', 'proud');
        await say('archie', 'peak', 2400, { mouth: false });
        cheerOthers(['archie']);
        setMouth('archie', 'smile');
      },
    },

    // Archie — menyenangkan: roller coaster di sepanjang kurva jembatan.
    archieCoaster: {
      chars: ['archie'],
      when: () => bridgeDone,
      async run() {
        setFlag(false);
        toggle('archie', 'is-riding', true);
        setMouth('archie', 'grin');
        ORDER.filter((o) => o !== 'archie').forEach((o) => lookAt(o, st.archie, 7500));
        await sleep(350);
        say('archie', 'wheee', 1700, { mouth: false });
        const ride = { tilt: true, lift: 12 };
        await alongBridge('archie', BX1 - 16, 2300, ride);
        await sleep(250);
        await alongBridge('archie', BX0 + 16, 2700, ride);
        await alongBridge('archie', PEAK_X, 1300, { ...ride, ease: easeOut });
        toggle('archie', 'is-riding', false);
        setPos('archie', PEAK_X, deckY(PEAK_X));
        setFlag(true);
        setMouth('archie', 'smile');
        await say('archie', 'heart', 1600);
      },
    },

    // Hijau — menantang: mengukur kemiringan garis singgung dengan dahi berkerut.
    hijauMeasure: {
      chars: ['hijau'],
      async run() {
        board('measure');
        toggle('hijau', 'is-frown', true);
        setMouth('hijau', 'wavy');
        act('hijau', 'measure');
        await say('hijau', 'dots', 1700, { mouth: false });
        act('hijau', 'measure');
        await say('hijau', 'slope', 2300, { mouth: false });
        toggle('hijau', 'is-frown', false);
        setMouth('hijau', 'smile');
        await act('hijau', 'nod');
      },
    },

    // Hijau — menyenangkan: menemukan titik potong grafik → "Eureka!" dengan cengiran lebar.
    hijauEureka: {
      chars: ['hijau'],
      async run() {
        board('intersect');
        await say('hijau', 'question', 1500);
        await sleep(700);
        setMouth('hijau', 'grin');
        act('hijau', 'jump');
        burst(st.hijau.x, st.hijau.y - 120, 8, GOLD);
        await say('hijau', 'eureka', 2400, { mouth: false });
        cheerOthers(['hijau']);
        setMouth('hijau', 'smile');
      },
    },

    // Ungu — menantang: menyulap ∫ dan ∞ yang berpendar, lalu dilontarkan ke gerbang (kartu).
    unguSpell: {
      chars: ['ungu'],
      async run() {
        toggle('ungu', 'is-casting', true);
        await say('ungu', 'integral', 1500);
        const a = glyph(INTEGRAL);
        const b = glyph(LEMNISCATE);
        const cx = () => st.ungu.x;
        const cy = () => st.ungu.y - 100 * CHARS.ungu.s - 20;
        let sparkAt = 0;
        await tween(1800, (t) => {
          const ang = t * Math.PI * 3;
          [[a, 0], [b, Math.PI]].forEach(([g, off]) => {
            const x = cx() + Math.cos(ang + off) * 52;
            const y = cy() + Math.sin(ang + off) * 18;
            g.setAttribute('transform', `translate(${x.toFixed(1)} ${y.toFixed(1)}) scale(${(0.6 + 0.4 * t).toFixed(2)})`);
            if (t - sparkAt > 0.12) burst(x, y, 2, GOLD);
          });
          if (t - sparkAt > 0.12) sparkAt = t;
        }, (t) => t);
        const gate = gatePoint();
        ORDER.forEach((o) => lookAt(o, gate, 2500));
        const from = [a, b].map((g) => g.transform.baseVal.consolidate().matrix);
        await tween(800, (t) => {
          [a, b].forEach((g, i) => {
            const x = from[i].e + (gate.x - from[i].e) * t;
            const y = from[i].f + (gate.y + (i ? 24 : -24) - from[i].f) * t - Math.sin(t * Math.PI) * 60;
            g.setAttribute('transform', `translate(${x.toFixed(1)} ${y.toFixed(1)}) scale(${(1 + t * 0.5).toFixed(2)})`);
          });
        }, easeIn);
        burst(gate.x, gate.y, 14, GOLD);
        [a, b].forEach((g) => fadeOut(g));
        document.body.classList.add('auth-gate');   // kartu berpendar (auth_card.css)
        setTimeout(() => document.body.classList.remove('auth-gate'), 1400);
        toggle('ungu', 'is-casting', false);
        cheerOthers(['ungu'], ['sparkle', 'exclaim']);
        await sleep(600);
      },
    },

    // Ungu — menyenangkan: monokel melorot + kedipan "gampang kalau tahu rahasianya".
    unguMonocle: {
      chars: ['ungu'],
      async run() {
        act('ungu', 'monocle');
        await sleep(500);
        toggle('ungu', 'is-wink', true);
        setMouth('ungu', 'grin');
        await say('ungu', 'key', 2200, { mouth: false });
        toggle('ungu', 'is-wink', false);
        setMouth('ungu', 'smile');
        cheerOthers(['ungu'], ['laugh', 'heart']);
        await sleep(600);
      },
    },

    // Kuning — menangkap apel gravitasi dengan jaring (kadang meleset & kena kepala).
    kuningApple: {
      chars: ['kuning'],
      async run() {
        const k = CHARS.kuning;
        const [hx, hy] = k.home;
        const netDX = (192 - 100) * k.s;
        const netDY = (34 - 172) * k.s;
        const [ax, ay] = pick(APPLES);
        const catchX = ax + rand(16, 34);
        const miss = Math.random() < 0.3;
        rustleTree();
        setMouth('kuning', 'o');
        say('kuning', 'exclaim', 1000, { mouth: false });
        lookAt('kuning', { x: ax, y: ay }, 1500);
        const standX = miss ? catchX + 4 : catchX - netDX;
        const [{ apple, trail }] = await Promise.all([
          dropApple(ax, ay, catchX, miss ? hy - 74 : hy + netDY, 950),
          walk('kuning', standX, hy, 650),
        ]);
        fadeOut(trail, 400);
        if (miss) {
          act('kuning', 'dizzy');
          burst(catchX, hy - 74, 6);
          const [x0, y0] = [catchX, hy - 74];
          await tween(700, (t) => apple.setAttribute('transform', `translate(${(x0 + 50 * t).toFixed(1)} ${(y0 - 40 * Math.sin(t * Math.PI) + (650 - y0) * t).toFixed(1)}) rotate(${(t * 300).toFixed(0)})`), (t) => t);
          fadeOut(apple, 600);
          await say('kuning', 'spiral', 1600, { mouth: false });
          cheerOthers(['kuning'], ['laugh']);
        } else {
          act('kuning', 'netcatch');
          burst(catchX, hy + netDY, 8, GOLD);
          apple.animate([{ opacity: 1 }, { opacity: 0 }], { duration: 300, delay: 300, fill: 'forwards' }).finished.then(() => apple.remove());
          setMouth('kuning', 'grin');
          await sleep(500);
          act('kuning', 'bounce');
          await say('kuning', 'apple', 1600, { mouth: false });
        }
        setMouth('kuning', 'smile');
        await walk('kuning', hx, hy, 700);
      },
    },

    // Kuning — menyeberangi jembatan sambil melompat, tos dengan Archie di puncak.
    kuningCross: {
      chars: ['kuning', 'archie'],
      when: () => bridgeDone,
      async run() {
        const [hx, hy] = CHARS.kuning.home;
        say('kuning', 'heart', 1200);
        await walk('kuning', BX0 - 4, 602, 900);
        for (let x = BX0 + 12; x < PEAK_X - 52; x += 18) {
          act('kuning', 'hop');
          await alongBridge('kuning', x, 300);
        }
        act('kuning', 'jump');
        act('archie', 'jump');
        await sleep(260);
        burst((st.kuning.x + st.archie.x) / 2, st.archie.y - 70, 10, GOLD);
        say('archie', 'sparkle', 1400);
        await say('kuning', 'laugh', 1400);
        await alongBridge('kuning', BX0 + 4, 1200);
        await walk('kuning', hx, hy, 900);
      },
    },
  };

  // Dua vibe tiap tokoh, dijalankan bergantian saat tokoh diklik.
  const VIBES = {
    archie: ['archieClimb', 'archieCoaster'],
    hijau: ['hijauMeasure', 'hijauEureka'],
    ungu: ['unguSpell', 'unguMonocle'],
    kuning: ['kuningApple', 'kuningCross'],
  };

  /** Jalankan skrip bila semua tokohnya bebas; tokoh dikunci selama skrip berjalan. */
  async function runScript(name) {
    const sc = SCRIPTS[name];
    if (sc.chars.some((id) => !free(id)) || (sc.when && !sc.when())) return false;
    sc.chars.forEach((id) => { st[id].busy = true; });
    try {
      await sc.run();
    } finally {
      sc.chars.forEach((id) => { st[id].busy = false; });
    }
    return true;
  }

  // Tingkah iseng di sela adegan.
  const ANTICS = {
    async butterflyVisit() {
      const id = pick(ORDER.filter(free));
      if (!id) return;
      bf.land = id;
      lookAt(id, bf, 4000);
      await sleep(2000);
      act(id, 'wiggle');
      await say(id, pick(['heart', 'sparkle', 'laugh']));
      bf.land = null;
      bf.speed = 3;
    },
    async yawn() {
      const id = pick(ORDER.filter(free));
      if (!id) return;
      setMouth(id, 'o');
      await act(id, 'stretch');
      setMouth(id, 'smile');
    },
    async dance() {
      ORDER.filter(free).forEach((id) => act(id, 'wiggle'));
      await sleep(1200);
    },
  };

  function poke(id) {
    const s = st[id];
    if (s.sleeping) { wake(id); act(id, 'startle'); say(id, 'exclaim', 1400); return; }
    ORDER.filter((o) => o !== id).forEach((o) => lookAt(o, facePoint(id), 1600));
    if (s.busy || REDUCED) { say(id, pick(['heart', 'sparkle', 'laugh']), 1400); return; }
    s.vibe = (s.vibe + 1) % VIBES[id].length;   // bergantian: menantang ↔ menyenangkan
    const [first, second] = [VIBES[id][s.vibe], VIBES[id][1 - s.vibe]];
    runScript(first).then((ok) => (ok ? true : runScript(second))).then((ok) => {
      if (!ok) { act(id, 'jump'); say(id, 'sparkle', 1400); }
    });
  }

  // ── Item koleksi ───────────────────────────────────────────────
  function buildHud() {
    hud = document.createElement('div');
    hud.className = 'fam-hud';
    hud.innerHTML = Object.entries(ITEM_KINDS).map(([k, it]) => `<span class="fam-hud-chip" data-chip="${k}" title="${it.label}">
      <svg viewBox="-16 -16 32 32" width="22" height="22" aria-hidden="true">${it.svg}</svg><b aria-label="${it.label}">0</b></span>`).join('');
    stageEl.appendChild(hud);
  }

  function spawnItem() {
    if (itemsLayer.childElementCount >= MAX_ITEMS) return;
    const vb = svg.viewBox.baseVal;
    const card = document.querySelector('.auth-split .auth-card');
    const right = card && !BANNER.matches ? toSvg({ clientX: card.getBoundingClientRect().left, clientY: 0 }).x : vb.x + vb.width;
    const x0 = vb.x + 30;
    const x1 = Math.min(right, vb.x + vb.width) - 30;
    const y0 = Math.max(vb.y + 90, 150);
    for (let tries = 0; tries < 12; tries++) {
      const x = rand(x0, x1);
      const y = rand(y0, 690);
      const nearChar = ORDER.some((id) => Math.hypot(st[id].x - x, st[id].y - 70 - y) < 80);
      const onBoard = x > 150 && x < 370 && y > 240 && y < 410;
      if (nearChar || onBoard) continue;
      const kind = pick(Object.keys(ITEM_KINDS));
      const g = make('g', { class: 'fam-item', 'data-item': kind, transform: `translate(${x.toFixed(0)} ${y.toFixed(0)})` },
        `<g class="fam-item-in" style="--d:${rand(0, 2).toFixed(2)}s"><circle class="fam-item-glow" r="17" fill="#FEF08A" opacity=".35"/>${ITEM_KINDS[kind].svg}</g>`);
      g.dataset.x = x;
      g.dataset.y = y;
      itemsLayer.appendChild(g);
      g.animate([{ opacity: 0 }, { opacity: 1 }], { duration: 500 });
      return;
    }
  }

  function collect(item) {
    if (item.dataset.taken) return;
    item.dataset.taken = '1';
    const kind = item.dataset.item;
    const x = +item.dataset.x;
    const y = +item.dataset.y;
    const chip = hud.querySelector(`[data-chip="${kind}"]`);
    const r = chip.getBoundingClientRect();
    const target = toSvg({ clientX: r.left + 14, clientY: r.top + r.height / 2 });
    burst(x, y, 8, GOLD);
    item.animate([
      { transform: `translate(${x}px, ${y}px) scale(1)` },
      { transform: `translate(${x}px, ${y - 30}px) scale(1.4)`, offset: 0.25 },
      { transform: `translate(${target.x}px, ${target.y}px) scale(.4)`, opacity: 0.6 },
    ], { duration: 750, easing: 'cubic-bezier(.4,0,.6,1)', fill: 'forwards' }).finished.then(() => {
      item.remove();
      counts[kind] += 1;
      chip.querySelector('b').textContent = counts[kind];
      chip.classList.remove('pop');
      void chip.offsetWidth;
      chip.classList.add('pop');
      setTimeout(spawnItem, rand(2500, 5000));
    });
    const fan = pick(ORDER.filter(free));
    if (fan) { act(fan, 'jump'); say(fan, pick(['sparkle', 'heart']), 1300); }
  }

  // ── Interaksi ──────────────────────────────────────────────────
  function toSvg(e) {
    const pt = svg.createSVGPoint();
    pt.x = e.clientX;
    pt.y = e.clientY;
    return pt.matrixTransform(svg.getScreenCTM().inverse());
  }

  function onClick(e) {
    const item = e.target.closest('.fam-item');
    if (item) { collect(item); return; }
    const ch = e.target.closest('.fam-char');
    if (ch) { poke(ch.dataset.char); return; }
    const hit = e.target.closest('[data-hit]');
    const kind = hit && hit.dataset.hit;
    if (kind === 'board') {
      board();
      if (free('hijau')) { act('hijau', 'jump'); say('hijau', BOARD_ICON[boardKind]); }
    } else if (kind === 'tree') {
      runScript('kuningApple').then((ok) => {
        if (ok) return;
        rustleTree();
        const [ax, ay] = pick(APPLES);
        dropApple(ax, ay, ax + 20, 640, 800).then(({ apple, trail }) => { fadeOut(trail, 300); fadeOut(apple, 1200); });
      });
    } else if (kind === 'sun') {
      toggleNight();
    } else if (kind === 'flag' && free('archie')) {
      act('archie', 'proud');
      say('archie', 'peak', 2000, { mouth: false });
    } else if (kind === 'bridge') {
      runScript('archieCoaster').then((ok) => { if (!ok) burst(toSvg(e).x, toSvg(e).y, 6); });
    } else if (kind === 'butterfly') {
      bf.land = null;
      bf.speed = 5;
      burst(bf.x, bf.y, 6);
      if (free('kuning')) { lookAt('kuning', bf, 2500); act('kuning', 'jump'); }
    } else {
      const p = toSvg(e);
      burst(p.x, p.y);
    }
  }

  function setNight(on) {
    night = on;
    svg.classList.toggle('is-night', on);
    document.body.classList.toggle('auth-night', on);   // kartu form ikut versi malam (auth_card.css)
  }

  function toggleNight() {
    setNight(!night);
    if (night) {
      if (free('ungu')) { sleepOn('ungu'); say('ungu', 'zzz', 2600, { mouth: false }); }
      if (free('kuning')) { act('kuning', 'jump'); say('kuning', 'sparkle'); }
    } else {
      ORDER.forEach((id) => { if (st[id].sleeping) wake(id); if (free(id)) act(id, 'jump'); });
      if (free('archie')) say('archie', 'sparkle');
    }
  }

  // ── Loop animasi: mata mengikuti sasaran, kupu-kupu terbang ─────
  function targetFor(id, now) {
    const s = st[id];
    if (now - pointer.t < 2200) return pointer;
    if (s.look && s.look.until > now) return s.look.ref;
    if (id === 'kuning') return bf;
    return null;
  }

  function moveButterfly() {
    bf.t += 0.006 * bf.speed;
    bf.speed += (1 - bf.speed) * 0.01;
    let tx;
    let ty;
    if (bf.land) {
      tx = st[bf.land].x;
      ty = st[bf.land].y + (48 - 172) * CHARS[bf.land].s + 4;
    } else {
      const t = bf.t;
      const d = 1 + Math.sin(t) ** 2;   // lemniskat Bernoulli (lintasan angka 8)
      tx = 200 + (95 * Math.cos(t)) / d;
      ty = 190 + (60 * Math.sin(t) * Math.cos(t)) / d - 18 * Math.sin(t * 3.1);
    }
    bf.x += (tx - bf.x) * 0.05;
    bf.y += (ty - bf.y) * 0.05;
    bf.node.setAttribute('transform', `translate(${bf.x.toFixed(1)} ${bf.y.toFixed(1)}) scale(1.3)`);
  }

  function tick(now) {
    requestAnimationFrame(tick);
    if (!visible()) return;
    if (!REDUCED) moveButterfly();
    for (const id of ORDER) {
      const s = st[id];
      const t = targetFor(id, now);
      let dx = 0;
      let dy = 1.5;
      if (t) {
        const vx = t.x - s.x;
        const vy = t.y - (s.y + (103 - 172) * CHARS[id].s);
        const len = Math.hypot(vx, vy) || 1;
        const k = Math.min(1, len / 120);
        dx = (vx / len) * 4.5 * k;
        dy = (vy / len) * 4 * k;
      }
      s.px += (dx - s.px) * 0.15;
      s.py += (dy - s.py) * 0.15;
      s.pupils.setAttribute('transform', `translate(${s.px.toFixed(2)} ${s.py.toFixed(2)})`);
    }
  }

  function blinkLoop(id) {
    setTimeout(() => {
      if (visible() && !st[id].sleeping) {
        st[id].el.classList.add('blink');
        setTimeout(() => st[id].el.classList.remove('blink'), 140);
      }
      blinkLoop(id);
    }, rand(2200, 5500));
  }

  /** Sutradara: rakit jembatan dulu, lalu undi adegan yang tokohnya bebas (tanpa mengulang). */
  async function director() {
    let last = null;
    let lastAntic = null;
    await sleep(1500);
    await runScript('rakit');
    for (;;) {
      if (!visible()) { await sleep(1000); continue; }
      const names = Object.keys(SCRIPTS).filter((n) => n !== last && SCRIPTS[n].chars.every(free) && (!SCRIPTS[n].when || SCRIPTS[n].when()));
      if (!names.length) { await sleep(800); continue; }
      last = pick(names);
      await runScript(last);
      await sleep(rand(1800, 3600));
      if (Math.random() < 0.45) {
        lastAntic = pick(Object.keys(ANTICS), lastAntic);
        await ANTICS[lastAntic]();
        await sleep(rand(1200, 2400));
      }
    }
  }

  /**
   * Sesuaikan viewBox dengan ukuran tempatnya.
   *  - Layar lebar: inti adegan (x 0–600) di tengah area kiri yang tidak tertutup kartu;
   *    jembatan berlanjut ke bawah kartu (tebing solusi).
   *  - Banner HP  : tebing, jembatan, dan tim (x −10…800, y ≈ 225–745) di tengah banner.
   */
  function fit() {
    const r = stageEl.getBoundingClientRect();
    if (!r.width || !r.height) return;
    let scale;
    let centerX;
    let core;
    if (BANNER.matches) {
      scale = Math.min(r.height / 520, r.width / 820);
      centerX = r.width / 2;
      core = 400;
    } else {
      const card = document.querySelector('.auth-split .auth-card');
      const freeW = card ? Math.max(card.getBoundingClientRect().left - r.left, 360) : r.width;
      scale = Math.min(r.height / 740, (freeW - 24) / 600, 1.5);
      centerX = freeW / 2;
      core = 300;
    }
    const w = r.width / scale;
    const h = r.height / scale;
    svg.setAttribute('viewBox', `${(core - centerX / scale).toFixed(1)} ${(745 - h).toFixed(1)} ${w.toFixed(1)} ${h.toFixed(1)}`);
  }

  /** Reaksi adegan pada form (event dari auth_mascot.js). */
  function listenToForm() {
    window.addEventListener('archie:look', (e) => {
      const p = e.detail && toSvg({ clientX: e.detail.x, clientY: e.detail.y });
      ORDER.forEach((id) => { st[id].look = p ? { ref: { x: p.x, y: p.y }, until: performance.now() + 8000 } : null; });
    });
    window.addEventListener('archie:cover', (e) => {
      ['archie', 'kuning'].forEach((id) => toggle(id, 'is-cover', e.detail.on));
    });
    window.addEventListener('archie:type', () => {
      writeFormula();
      toggle('hijau', 'is-writing', true);
      clearTimeout(st.hijau.writeTimer);
      st.hijau.writeTimer = setTimeout(() => toggle('hijau', 'is-writing', false), 450);
      const now = performance.now();
      if (free('kuning') && now - lastHop > 480) { lastHop = now; act('kuning', 'hop'); }
    });
    window.addEventListener('archie:cheer', () => {
      ORDER.forEach((id, i) => { if (st[id].sleeping) wake(id); if (!st[id].busy) setTimeout(() => act(id, 'jump'), i * 90); });
      if (free('archie')) say('archie', 'sparkle', 1500);
    });
  }

  function init() {
    stageEl = document.getElementById('family-stage');
    if (!stageEl) return;
    svg = make('svg', { class: 'fam', viewBox: '0 0 600 720', preserveAspectRatio: 'xMinYMin meet', role: 'group', 'aria-label': stageEl.getAttribute('aria-label') });
    svg.innerHTML = sceneMarkup();
    stageEl.replaceChildren(svg);
    buildHud();
    fit();
    window.addEventListener('resize', fit);
    BANNER.addEventListener('change', fit);

    plot = svg.querySelector('.fam-plot');
    fx = svg.querySelector('.fam-fx');
    tree = svg.querySelector('.fam-tree');
    itemsLayer = svg.querySelector('.fam-items');
    bf.node = svg.querySelector('.fam-butterfly');
    ORDER.forEach((id) => {
      const el = svg.querySelector(`[data-char="${id}"]`);
      st[id] = {
        el,
        pos: svg.querySelector(`[data-pos="${id}"]`),
        banchor: svg.querySelector(`[data-banchor="${id}"]`),
        mouth: el.querySelector('.fam-mouth'),
        pupils: el.querySelector('.fam-pupils'),
        bubble: svg.querySelector(`[data-bubble="${id}"]`),
        icon: svg.querySelector(`[data-bubble="${id}"] .fam-bubble-icon`),
        x: 0, y: 0, px: 0, py: 0, busy: false, sleeping: false, vibe: Math.random() < 0.5 ? 0 : 1,
      };
      setPos(id, ...CHARS[id].home);
      el.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); poke(id); }
      });
      blinkLoop(id);
    });
    setFlag(true);

    listenToForm();
    svg.addEventListener('click', onClick);
    svg.addEventListener('pointermove', (e) => {
      const p = toSvg(e);
      pointer.x = p.x;
      pointer.y = p.y;
      pointer.t = performance.now();
    });
    svg.addEventListener('pointerleave', () => { pointer.t = -1e9; });

    // Siang/malam awal mengikuti jam lokal, diterapkan tanpa transisi (kelas auth-instant).
    const hour = new Date().getHours();
    document.body.classList.add('auth-instant');
    setNight(hour >= 18 || hour < 6);
    void document.body.offsetWidth;
    requestAnimationFrame(() => document.body.classList.remove('auth-instant'));
    board('measure');
    for (let i = 0; i < MAX_ITEMS; i++) setTimeout(spawnItem, 600 + i * 700);
    requestAnimationFrame(tick);
    if (REDUCED) { bridgeDone = true; svg.querySelectorAll('.fam-plank.missing').forEach((p) => p.classList.remove('missing')); }
    else director();
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
})();
