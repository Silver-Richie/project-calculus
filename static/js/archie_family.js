/**
 * Calculus Bridge — Panel animasi "Keluarga Archie" di halaman Masuk/Daftar.
 *
 * Mekanisme:
 *  - Adegan SVG dibangun di sini. axolotl(id) dipakai ulang untuk 4 tokoh
 *    (Kakek, Ibu, Archie, Adik); bedanya hanya warna, aksesori, dan benda di tangan.
 *  - Tokoh "mengobrol" lewat gelembung berisi ikon/grafik (tanpa teks). Satu obrolan
 *    = satu fungsi di SCRIPTS. Sutradara (director) mengundi skrip secara acak tanpa
 *    mengulang yang terakhir, diselingi tingkah iseng (ANTICS), jadi tidak monoton.
 *  - Interaksi: klik tokoh → reaksi acak khas tokoh (REACT); klik papan → grafik baru;
 *    klik pohon → apel jatuh; klik matahari/bulan → siang/malam; klik kupu-kupu → kabur;
 *    klik area kosong → letupan konfeti matematika. Mata semua tokoh mengikuti kursor.
 *  - Tata letak: latar penuh layar (≥ 768px) atau banner ringkas di atas kartu (HP); lihat fit().
 *  - Form: mendengarkan event 'archie:look' / 'archie:cover' / 'archie:cheer' dari
 *    auth_mascot.js (melirik ke kolom, menutup mata saat kata sandi, melompat saat kirim).
 *  - Hemat: tidak bergerak saat tab tersembunyi. Dengan prefers-reduced-motion,
 *    obrolan otomatis dimatikan; klik tetap memunculkan gelembung.
 *  - Malam otomatis bila jam lokal 18.00–05.59.
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

  // ── Tokoh ──────────────────────────────────────────────────────
  // x,y = titik kaki di adegan (600×720); s = skala; bx = geser gelembung agar tidak keluar panel.
  const CHARS = {
    kakek:  { name: 'Kakek',  x: 108, y: 614, s: .78, body: '#C4B5FD', line: '#7C3AED', belly: '#EDE9FE', gill: '#F0ABFC', gillLine: '#C026D3', bx: 26 },
    ibu:    { name: 'Ibu',    x: 256, y: 644, s: .84, body: '#86EFAC', line: '#16A34A', belly: '#DCFCE7', gill: '#F472B6', gillLine: '#DB2777', bx: 0 },
    archie: { name: 'Archie', x: 410, y: 646, s: .92, body: '#93C5FD', line: '#2563EB', belly: '#DBEAFE', gill: '#F43F5E', gillLine: '#E11D48', bx: 0 },
    adik:   { name: 'Adik',   x: 536, y: 676, s: .6,  body: '#FDE68A', line: '#D97706', belly: '#FEF9C3', gill: '#F9A8D4', gillLine: '#DB2777', bx: -30 },
  };
  const ORDER = ['kakek', 'ibu', 'archie', 'adik'];

  const MOUTH = {
    smile: ['M90 118Q100 128 110 118', 'none'],
    open: ['M94 118Q100 132 106 118Z', '#9F1239'],
    grin: ['M86 116Q100 136 114 116Z', '#9F1239'],
    flat: ['M92 121H108', 'none'],
    o: ['M95 121a5 6 0 1 0 10 0a5 6 0 1 0-10 0', '#9F1239'],
  };

  const ACC = {
    archie: `<g class="fam-cap"><path d="M100 50L143 66L100 82L57 66Z" fill="#1E3A5F" stroke="#6366F1" stroke-width="2.5"/>
      <path d="M125 74L133 90" stroke="#D97706" stroke-width="2.5" stroke-linecap="round"/><circle cx="133" cy="90" r="3" fill="#D97706"/></g>`,
    ibu: `<path d="M50 80Q100 60 150 80" stroke="#0F766E" stroke-width="5" fill="none" stroke-linecap="round"/>
      <circle cx="84" cy="73" r="11" fill="#CCFBF1" stroke="#0F766E" stroke-width="4"/><circle cx="116" cy="73" r="11" fill="#CCFBF1" stroke="#0F766E" stroke-width="4"/>
      <circle cx="80" cy="70" r="3" fill="#fff"/><circle cx="112" cy="70" r="3" fill="#fff"/>`,
    kakek: `<path d="M62 84q14-10 28-1M110 83q14-9 28 1" stroke="#fff" stroke-width="7" stroke-linecap="round" fill="none"/>
      <circle cx="124" cy="103" r="16" fill="none" stroke="#D97706" stroke-width="3"/><path d="M140 106q8 18 2 34" stroke="#D97706" stroke-width="1.5" fill="none"/>
      <g class="fam-stache"><path d="M100 113q-8-8-20-2q-6 4-12 0q4 10 16 8q10-1 16-6q6 5 16 6q12 2 16-8q-6 4-12 0q-12-6-20 2z" fill="#fff" stroke="#D6D3D1" stroke-width="1.5"/></g>`,
    adik: `<g class="fam-bow"><path d="M100 66L76 52L79 82Z" fill="#F472B6" stroke="#DB2777" stroke-width="3" stroke-linejoin="round"/>
      <path d="M100 66L124 52L121 82Z" fill="#F472B6" stroke="#DB2777" stroke-width="3" stroke-linejoin="round"/><circle cx="100" cy="67" r="7" fill="#DB2777"/></g>
      <g fill="#D97706" opacity=".5"><circle cx="58" cy="113" r="1.8"/><circle cx="64" cy="118" r="1.8"/><circle cx="142" cy="113" r="1.8"/><circle cx="136" cy="118" r="1.8"/></g>`,
  };

  // Benda di tangan kanan (ikut bergerak saat melambai).
  const HAND = {
    archie: `<path d="M150 150l14-26" stroke="#F59E0B" stroke-width="6" stroke-linecap="round"/><path d="M164 124l3-6" stroke="${INK}" stroke-width="3" stroke-linecap="round"/>`,
    ibu: `<path d="M150 120h14v12l13 22a5 5 0 0 1-4 7h-32a5 5 0 0 1-4-7l13-22z" fill="#F0FDFA" stroke="#0F766E" stroke-width="3" stroke-linejoin="round"/>
      <path d="M142 150h30l3 5a5 5 0 0 1-4 6h-28a5 5 0 0 1-4-6z" fill="#A78BFA"/><circle cx="153" cy="152" r="2.5" fill="#fff"/><circle cx="161" cy="146" r="2" fill="#fff"/>`,
    kakek: `<path d="M152 150V196" stroke="#78350F" stroke-width="5" stroke-linecap="round"/><path d="M152 150q0-12 12-10" stroke="#78350F" stroke-width="5" fill="none" stroke-linecap="round"/>`,
    adik: `<path d="M150 152Q166 110 174 70" stroke="#94A3B8" stroke-width="2" fill="none"/>
      <g class="fam-balloon"><ellipse cx="176" cy="50" rx="17" ry="20" fill="#F43F5E" stroke="#BE123C" stroke-width="2.5"/>
      <path d="M172 70l4 4l4-4z" fill="#BE123C"/><ellipse cx="170" cy="42" rx="4" ry="6" fill="#fff" opacity=".6"/></g>`,
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
        <circle cx="124" cy="104" r="6.5" fill="${INK}"/><circle cx="121.5" cy="101" r="2.2" fill="#fff"/></g></g>`;
  }

  /** Satu axolotl. Bentuk dasar sama dengan logo Archie (viewBox 200×200, kaki di y=172). */
  function axolotl(id) {
    const c = CHARS[id];
    const paint = `fill="${c.body}" stroke="${c.line}" stroke-width="3"`;
    const gill = (d) => `<path d="${d}" fill="${c.gill}" stroke="${c.gillLine}" stroke-width="3" stroke-linecap="round"/>`;
    return `<g class="fam-walk" data-walk="${id}"><g transform="translate(${c.x} ${c.y}) scale(${c.s})">
      <g class="fam-char" data-char="${id}" tabindex="0" role="button" aria-label="${c.name}, tekan untuk bereaksi" style="--d:${rand(0, 2).toFixed(2)}s">
        <ellipse class="fam-shadow" cx="0" cy="2" rx="62" ry="9"/>
        <g class="fam-move"><g class="fam-breathe"><g transform="translate(-100 -172)">
          <path class="fam-tail" d="M148 150Q188 156 196 124Q178 140 150 136Z" ${paint} stroke-linejoin="round"/>
          <g class="fam-gill fam-gill-l">${gill('M42 95C25 80 15 95 28 112C15 118 20 135 38 128')}</g>
          <g class="fam-gill fam-gill-r">${gill('M158 95C175 80 185 95 172 112C185 118 180 135 162 128')}</g>
          <ellipse cx="100" cy="120" rx="58" ry="52" ${paint}/>
          <ellipse cx="100" cy="130" rx="34" ry="30" fill="${c.belly}" opacity=".9"/>
          <ellipse cx="78" cy="168" rx="14" ry="7" ${paint}/><ellipse cx="122" cy="168" rx="14" ry="7" ${paint}/>
          <g class="fam-arm fam-arm-l"><ellipse cx="50" cy="140" rx="9" ry="15" ${paint}/></g>
          <g class="fam-arm fam-arm-r"><g class="fam-held">${HAND[id]}</g><ellipse cx="150" cy="140" rx="9" ry="15" ${paint}/></g>
          ${eyes(id, c)}
          <ellipse cx="56" cy="120" rx="7" ry="4" fill="#F43F5E" opacity=".5"/><ellipse cx="144" cy="120" rx="7" ry="4" fill="#F43F5E" opacity=".5"/>
          <path class="fam-mouth" d="${MOUTH.smile[0]}" fill="none" stroke="${INK}" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>
          ${ACC[id]}
        </g></g></g>
      </g></g></g>`;
  }

  const headY = (id) => CHARS[id].y + (48 - 172) * CHARS[id].s;
  const facePoint = (id) => ({ x: CHARS[id].x + st[id].wx, y: CHARS[id].y + (110 - 172) * CHARS[id].s });

  function bubble(id) {
    const c = CHARS[id];
    const tx = (-c.bx / .82).toFixed(1);   // ekor gelembung tetap menunjuk ke tokoh
    return `<g class="fam-bwalk" data-bwalk="${id}"><g transform="translate(${c.x + c.bx} ${headY(id)}) scale(.82)">
      <g class="fam-bubble" data-bubble="${id}">
        <path d="M-44,-86h88a14,14 0 0 1 14,14v40a14,14 0 0 1 -14,14H${+tx + 8}l-8,14l-8,-14H-44a14,14 0 0 1 -14,-14v-40a14,14 0 0 1 14,-14z"
              fill="#fff" stroke="${INK}" stroke-width="3" stroke-linejoin="round"/>
        <g class="fam-bubble-icon" transform="translate(0 -52)"></g>
      </g></g></g>`;
  }

  // ── Ikon gelembung (±30 × ±24) ─────────────────────────────────
  const star4 = (x, y, r, d) => `<path class="ic-twinkle" style="--d:${d}s" d="M${x} ${y - r}Q${x} ${y} ${x + r} ${y}Q${x} ${y} ${x} ${y + r}Q${x} ${y} ${x - r} ${y}Q${x} ${y} ${x} ${y - r}Z" fill="#FBBF24"/>`;
  const AX = '<path d="M-30 16H30M-26 20V-24" stroke="#94A3B8" stroke-width="2"/>';
  const LEMNISCATE = 'M0,0C8,-14 26,-14 26,0C26,14 8,14 0,0C-8,-14 -26,-14 -26,0C-26,14 -8,14 0,0Z';
  const ICONS = {
    question: `<g class="ic-wobble"><path d="M-8,-9C-8,-21 10,-21 10,-9C10,-1 1,-1 1,7" stroke="${INK}" stroke-width="5" fill="none" stroke-linecap="round"/><circle cx="1" cy="16" r="3.4" fill="${INK}"/></g>`,
    exclaim: `<g class="ic-pulse"><path d="M0,-18V5" stroke="#DC2626" stroke-width="6" stroke-linecap="round"/><circle cx="0" cy="15" r="3.8" fill="#DC2626"/></g>
      <path d="M-16,-14l-6,-5M16,-14l6,-5M-18,2h-7M18,2h7" stroke="#F59E0B" stroke-width="3" stroke-linecap="round"/>`,
    bulb: `<g class="ic-rays" stroke="#F59E0B" stroke-width="3" stroke-linecap="round"><path d="M0,-24V-30M17,-17L21,-21M-17,-17L-21,-21M23,-3H29M-23,-3H-29"/></g>
      <circle cx="0" cy="-4" r="13" fill="#FDE047" stroke="#CA8A04" stroke-width="3"/><path d="M-4,-4q4,6 8,0" stroke="#CA8A04" stroke-width="2" fill="none"/>
      <rect x="-6" y="9" width="12" height="9" rx="2" fill="#94A3B8"/>`,
    heart: `<path class="ic-beat" d="M0,16C-26,0 -16,-22 0,-9C16,-22 26,0 0,16Z" fill="#F43F5E" stroke="#BE123C" stroke-width="2.5"/>
      <path class="ic-float" d="M22,-16C16,-20 18,-26 22,-22C26,-26 28,-20 22,-16Z" fill="#FB7185"/>`,
    tangent: `${AX}<path class="ic-draw" pathLength="1" d="M-24,-20Q0,44 24,-20" stroke="#2563EB" stroke-width="3.5" fill="none" stroke-linecap="round"/>
      <path class="ic-draw" style="--d:.9s" pathLength="1" d="M0,20L25,-13.3" stroke="#DC2626" stroke-width="3" fill="none" stroke-linecap="round"/>
      <circle cx="12" cy="4" r="3.5" fill="#F59E0B"/>`,
    sine: `<path d="M-30,0H30" stroke="#94A3B8" stroke-width="2"/>
      <path class="ic-draw" pathLength="1" d="M-30,0C-24,-22 -16,-22 -10,0S4,22 10,0S24,-22 30,0" stroke="#0891B2" stroke-width="3.5" fill="none" stroke-linecap="round"/>
      <circle r="4" fill="#F59E0B"><animateMotion dur="1.8s" repeatCount="indefinite" path="M-30,0C-24,-22 -16,-22 -10,0S4,22 10,0S24,-22 30,0"/></circle>`,
    area: `${AX}<path class="ic-grow" d="M-22,16V2Q-4,-30 24,-14V16Z" fill="#93C5FD"/>
      <path d="M-28,8Q-4,-34 28,-16" stroke="#2563EB" stroke-width="3.5" fill="none" stroke-linecap="round"/>`,
    riemann: `${AX}${[[-22, 12], [-10, 20], [2, 24], [14, 22]].map(([x, h], i) =>
      `<rect class="ic-grow" style="--d:${i * .18}s" x="${x}" y="${16 - h}" width="11" height="${h}" fill="#FDE047" stroke="#CA8A04" stroke-width="1.5"/>`).join('')}
      <path d="M-26,6Q-2,-16 28,-6" stroke="#2563EB" stroke-width="3" fill="none" stroke-linecap="round"/>`,
    infinity: `<path d="${LEMNISCATE}" stroke="#7C3AED" stroke-width="4.5" fill="none"/>
      <circle r="4" fill="#F59E0B"><animateMotion dur="2.2s" repeatCount="indefinite" path="${LEMNISCATE}"/></circle>`,
    limit: `<path d="M-30,10H30" stroke="#94A3B8" stroke-width="2"/><path d="M20,-22V22" stroke="#DC2626" stroke-width="2.5" stroke-dasharray="4 4"/>
      <circle cx="20" cy="10" r="6" fill="none" stroke="#DC2626" stroke-width="2"/><g class="ic-approach"><circle cx="0" cy="10" r="5.5" fill="#2563EB"/></g>`,
    apple: `<g class="ic-wobble"><circle cx="0" cy="4" r="15" fill="#EF4444" stroke="#B91C1C" stroke-width="2.5"/>
      <path d="M0,-10q2,-8 6,-10" stroke="#78350F" stroke-width="3" fill="none" stroke-linecap="round"/>
      <path d="M3,-14q10,-8 16,0q-8,6 -16,0z" fill="#22C55E"/><circle cx="-6" cy="-1" r="3" fill="#fff" opacity=".6"/></g>`,
    zzz: `<g class="ic-float" stroke="#6366F1" stroke-width="3.5" fill="none" stroke-linejoin="round" stroke-linecap="round">
      <path d="M-26,8h10l-10,10h10"/><path d="M-8,-4h13l-13,13h13"/><path d="M12,-20h16l-16,16h16"/></g>`,
    spiral: `<path class="ic-spin" d="M0,0m-2,0a2,2 0 1,1 4,0a5,5 0 1,1 -10,0a8,8 0 1,1 16,0a11,11 0 1,1 -22,0a14,14 0 1,1 28,0" stroke="#7C3AED" stroke-width="3" fill="none" stroke-linecap="round"/>`,
    sweat: `<g class="ic-drip"><path d="M8,-20C16,-6 18,2 8,10C-2,2 0,-6 8,-20Z" fill="#7DD3FC" stroke="#0284C7" stroke-width="2.5"/></g>
      <path d="M-14,-10l-8,-4M-14,0h-10M-14,10l-8,4" stroke="#0284C7" stroke-width="2.5" stroke-linecap="round"/>`,
    sparkle: star4(-14, 4, 13, 0) + star4(12, -10, 9, .3) + star4(16, 14, 6, .6),
    note: `<g class="ic-float" fill="#7C3AED"><ellipse cx="-12" cy="12" rx="7" ry="5"/><rect x="-6.5" y="-16" width="3" height="28"/>
      <path d="M-6.5,-16q12,4 10,14q-2,-8 -10,-8z"/><ellipse cx="14" cy="6" rx="6" ry="4.5"/><rect x="18.5" y="-18" width="3" height="24"/></g>`,
    laugh: `<g class="ic-shake"><circle r="20" fill="#FDE047" stroke="#CA8A04" stroke-width="2.5"/>
      <path d="M-11,-5q4,-6 8,0M3,-5q4,-6 8,0" stroke="#78350F" stroke-width="2.5" fill="none" stroke-linecap="round"/>
      <path d="M-11,4h22q-2,12 -11,12q-9,0 -11,-12z" fill="#9F1239"/>
      <path d="M-23,-12q-4,5 -1,9M23,-12q4,5 1,9" stroke="#38BDF8" stroke-width="2.5" fill="none" stroke-linecap="round"/></g>`,
    tea: `<path d="M-16,-2h28v8a14,14 0 0 1 -28,0z" fill="#fff" stroke="#78350F" stroke-width="2.5"/>
      <path d="M12,2a6,6 0 0 1 0,10" stroke="#78350F" stroke-width="2.5" fill="none"/><path d="M-22,20h40" stroke="#78350F" stroke-width="2.5" stroke-linecap="round"/>
      <g class="ic-float" stroke="#94A3B8" stroke-width="2.5" fill="none" stroke-linecap="round"><path d="M-8,-8q-4,-6 0,-10q4,-4 0,-10"/><path d="M4,-8q-4,-6 0,-10q4,-4 0,-10"/></g>`,
    circle: `<circle r="19" fill="none" stroke="#16A34A" stroke-width="3"/>
      <path d="M0,0H19" stroke="#DC2626" stroke-width="3" stroke-linecap="round"><animateTransform attributeName="transform" type="rotate" from="0" to="360" dur="2.4s" repeatCount="indefinite"/></path>
      <circle r="3" fill="${INK}"/>`,
    pie: `<path d="M0,0L17.3,-10A20,20 0 1,0 17.3,10Z" fill="#FBBF24" stroke="#B45309" stroke-width="2.5" stroke-linejoin="round"/>
      <g class="ic-slice"><path d="M5,0L22.3,-10A20,20 0 0,1 22.3,10Z" fill="#FCD34D" stroke="#B45309" stroke-width="2.5" stroke-linejoin="round"/></g>
      <circle cx="-8" cy="-6" r="2" fill="#B45309"/><circle cx="-4" cy="8" r="2" fill="#B45309"/>`,
    stonks: `${AX}<path class="ic-draw" pathLength="1" d="M-24,10L-12,0L-4,6L8,-8L22,-18" stroke="#16A34A" stroke-width="3.5" fill="none" stroke-linejoin="round" stroke-linecap="round"/>
      <path d="M13,-20L23,-19L21,-9" stroke="#16A34A" stroke-width="3.5" fill="none" stroke-linecap="round" stroke-linejoin="round"/>`,
    crash: `${AX}<path class="ic-draw" pathLength="1" d="M-24,8L-6,-18L2,-10L22,14" stroke="#DC2626" stroke-width="3.5" fill="none" stroke-linejoin="round" stroke-linecap="round"/>
      <path d="M12,13L23,15L22,4" stroke="#DC2626" stroke-width="3.5" fill="none" stroke-linecap="round" stroke-linejoin="round"/>`,
    dots: [-14, 0, 14].map((x, i) => `<circle class="ic-dot" style="--d:${i * .15}s" cx="${x}" cy="0" r="5" fill="#64748B"/>`).join(''),
  };

  // ── Papan tulis ────────────────────────────────────────────────
  const OX = 330, OY = 300, SX = 28, SY = 20;
  const px = (x) => OX + x * SX;
  const py = (y) => OY - y * SY;
  function curve(f, a = -3.6, b = 3.6, n = 90) {
    let d = '';
    let pen = false;
    for (let i = 0; i <= n; i++) {
      const x = a + ((b - a) * i) / n;
      const y = py(f(x));
      if (!Number.isFinite(y) || y < 205 || y > 375) { pen = false; continue; }
      d += `${pen ? 'L' : 'M'}${px(x).toFixed(1)} ${y.toFixed(1)}`;
      pen = true;
    }
    return d;
  }
  const chalk = (d, color = '#F8FAFC') => `<path class="chalk" d="${d}" stroke="${color}" stroke-width="3.2" fill="none" stroke-linecap="round" stroke-linejoin="round"/>`;
  const dot = (x, y, color = '#FDE047') => `<circle class="chalk-dot" cx="${px(x)}" cy="${py(y)}" r="5" fill="${color}"/>`;
  const AXES = `<path d="M232 ${OY}H428M${OX} 220V360" stroke="#F8FAFC" stroke-width="1.5" opacity=".35"/>`;
  const wave = (x) => 1.1 + 0.35 * x + 0.5 * Math.sin(1.4 * x);
  const BOARD = {
    parabola: () => {
      const f = (x) => (x * x) / 3 - 1;
      return chalk(curve(f)) + chalk(curve((x) => f(1.5) + (x - 1.5), 0.2, 2.9), '#F9A8D4') + dot(1.5, f(1.5));
    },
    sine: () => chalk(curve((x) => 1.6 * Math.sin(1.7 * x)), '#67E8F9'),
    area: () => `<path class="chalk-dot" d="${curve(wave, -2, 2.2)}L${px(2.2)} ${OY}L${px(-2)} ${OY}Z" fill="#FDE047" opacity=".35"/>${chalk(curve(wave))}`,
    riemann: () => Array.from({ length: 6 }, (_, i) => {
      const x = -2 + 0.7 * i;
      const h = wave(x + 0.35);
      return `<rect class="chalk-bar" x="${px(x)}" y="${py(h)}" width="${0.7 * SX}" height="${h * SY}" fill="#FDE047" opacity=".45" stroke="#FDE047"/>`;
    }).join('') + chalk(curve(wave)),
    limit: () => {
      const f = (x) => (2.4 * Math.sin(1.8 * x)) / (1.8 * x);
      return chalk(curve(f, -3.6, -0.06)) + chalk(curve(f, 0.06, 3.6))
        + `<path d="M${OX} ${py(2.4)}H${px(-3)}" stroke="#F9A8D4" stroke-width="2" stroke-dasharray="5 5"/>`
        + `<circle class="chalk-dot" cx="${OX}" cy="${py(2.4)}" r="5" fill="#14532D" stroke="#FDE047" stroke-width="2.5"/>`;
    },
    cubic: () => {
      const f = (x) => (x ** 3 - 4 * x) / 2.2;
      const e = 2 / Math.sqrt(3);
      return chalk(curve(f, -2.6, 2.6), '#86EFAC') + dot(-e, f(-e)) + dot(e, f(e), '#F9A8D4');
    },
    circle: () => `${chalk('M274 290a56 56 0 1 0 112 0a56 56 0 1 0 -112 0')}
      <path d="M330 290h56" stroke="#F9A8D4" stroke-width="3" stroke-linecap="round"><animateTransform attributeName="transform" type="rotate" from="0 330 290" to="360 330 290" dur="4s" repeatCount="indefinite"/></path>
      <circle class="chalk-dot" cx="330" cy="290" r="4" fill="#FDE047"/>`,
  };
  const BOARD_ICON = { parabola: 'tangent', sine: 'sine', area: 'area', riemann: 'riemann', limit: 'limit', cubic: 'stonks', circle: 'pie' };

  // ── Adegan ─────────────────────────────────────────────────────
  const APPLES = [[62, 322], [128, 292], [152, 352], [96, 372], [118, 330]];
  const APPLE = '<circle r="9" fill="#EF4444" stroke="#B91C1C" stroke-width="2"/><path d="M0,-9q1,-5 4,-6" stroke="#78350F" stroke-width="2" fill="none"/><circle cx="-3" cy="-3" r="2" fill="#fff" opacity=".6"/>';

  // Inti adegan (tokoh, papan, pohon apel) ada di x 0–600, y 0–720. Langit, bukit, dan
  // rumput diperluas ke kiri/kanan/bawah supaya adegan bisa menjadi latar satu layar penuh.
  const X0 = -2400;
  const X1 = 3000;
  const YBOT = 2400;
  const SKIP_CORE = (x) => x > 120 && x < 480;   // area papan tulis & tokoh: jangan ditimpa hiasan

  /** Bukit bergelombang selebar adegan (puncak & lembah bergantian tiap `step`). */
  function hills(y, amp, step, fill) {
    let d = `M${X0} ${y}`;
    for (let x = X0, i = 0; x < X1; x += step, i++) {
      d += `Q${x + step / 2} ${y + (i % 2 ? amp : -amp)} ${x + step} ${y}`;
    }
    return `<path d="${d}V${YBOT}H${X0}Z" fill="${fill}"/>`;
  }

  /** Tinggi permukaan hills(y, amp, step) di titik x (kurva Bezier kuadrat per segmen). */
  function hillY(y, amp, step, x) {
    const i = Math.floor((x - X0) / step);
    const t = (x - X0) / step - i;
    return y + 2 * t * (1 - t) * (i % 2 ? amp : -amp);
  }

  const scatter = (n, x0, x1, y0, y1, fn) => Array.from({ length: n }, (_, i) => {
    const x = x0 + ((x1 - x0) * (i + rand(0.15, 0.85))) / n;   // tersebar merata + sedikit acak
    return fn(x, rand(y0, y1), i);
  }).join('');

  const farTree = (x) => (SKIP_CORE(x) ? '' : `<g transform="translate(${x.toFixed(0)} ${(hillY(512, 26, 240, x) + 6).toFixed(0)}) scale(${rand(0.5, 0.9).toFixed(2)})">
    <rect x="-3" y="-6" width="6" height="16" fill="#7C9A6B"/><circle cy="-18" r="16" fill="#6CC08B"/><circle cx="-9" cy="-10" r="11" fill="#5DB37E"/><circle cx="9" cy="-11" r="12" fill="#5DB37E"/></g>`);

  const bush = (x) => (x > -60 && x < 640 ? '' : `<g transform="translate(${x.toFixed(0)} ${(hillY(556, 22, 300, x) + 16).toFixed(0)})"><g class="fam-bush" style="animation-delay:${rand(0, 3).toFixed(2)}s">
    <circle cx="-22" cy="-14" r="20" fill="#22C55E"/><circle cx="20" cy="-14" r="22" fill="#22C55E"/><circle cy="-26" r="26" fill="#34D399"/>
    <circle cx="-6" cy="-30" r="3.5" fill="#F9A8D4"/><circle cx="14" cy="-20" r="3.5" fill="#FDE047"/></g></g>`);

  const grass = (x, y) => `<g transform="translate(${x.toFixed(0)} ${y.toFixed(0)})"><path class="fam-grass" style="animation-delay:${rand(0, 2.5).toFixed(2)}s"
    d="M-4 0q-1-7-7-11M-2 0q-1-10 1-15M1 0q1-8 5-13M3 0q3-5 9-7" stroke="${pick(['#16A34A', '#22A55A', '#15803D'])}" stroke-width="1.8" fill="none" stroke-linecap="round"/></g>`;

  const flower = (x, y, col) => `<g transform="translate(${x.toFixed(0)} ${y.toFixed(0)})"><g class="fam-flower" style="animation-delay:${rand(0, 2).toFixed(2)}s">
    <path d="M0 0V-16" stroke="#15803D" stroke-width="2.5"/><g transform="translate(0 -18)" fill="${col}">
    <circle cx="-4" r="4"/><circle cx="4" r="4"/><circle cy="-4" r="4"/><circle cy="4" r="4"/><circle r="2.6" fill="#F59E0B"/></g></g></g>`;
  const FLOWER_COLORS = ['#F472B6', '#FDE047', '#F87171', '#A78BFA', '#FFFFFF', '#FB923C'];

  const birds = (y, dur, delay) => `<g class="fam-bird" style="animation-duration:${dur}s;animation-delay:${delay}s">
    ${[[0, 0], [26, -10], [30, 14]].map(([bx, by]) => `<g transform="translate(${bx} ${y + by})"><path class="fam-bird-wing"
      d="M-9 0q4.5-6 9 0q4.5-6 9 0" stroke="#334155" stroke-width="2.2" fill="none" stroke-linecap="round" style="animation-delay:${rand(0, 0.5).toFixed(2)}s"/></g>`).join('')}</g>`;

  function sceneMarkup() {
    const stars = Array.from({ length: 110 }, () =>
      `<circle class="fam-star" cx="${rand(X0, X1).toFixed(0)}" cy="${rand(-900, 300).toFixed(0)}" r="${rand(1, 2.4).toFixed(1)}" style="animation-delay:${rand(0, 3).toFixed(2)}s"/>`).join('');
    const rays = Array.from({ length: 12 }, (_, i) => {
      const a = (i * Math.PI) / 6;
      return `<path d="M${(Math.cos(a) * 41).toFixed(1)} ${(Math.sin(a) * 41).toFixed(1)}L${(Math.cos(a) * 52).toFixed(1)} ${(Math.sin(a) * 52).toFixed(1)}"/>`;
    }).join('');
    const flowers = [[40, 690], [190, 702], [335, 690], [468, 706], [578, 684], [250, 676]]
      .map(([x, y], i) => flower(x, y, FLOWER_COLORS[i])).join('')
      + scatter(60, -1800, 2400, 668, 716, (x, y) => (x > -20 && x < 620 ? '' : flower(x, y, pick(FLOWER_COLORS))));
    const fireflies = Array.from({ length: 30 }, () =>
      `<circle class="fam-firefly" cx="${rand(-1500, 2100).toFixed(0)}" cy="${rand(430, 640).toFixed(0)}" r="2.6" style="animation-delay:${rand(0, 3).toFixed(2)}s;--fx:${rand(-22, 22).toFixed(0)}px"/>`).join('');
    const cloud = (y, s, dur, delay) => `<g class="fam-cloud" style="animation-duration:${dur}s;animation-delay:${delay}s">
      <path transform="translate(0 ${y}) scale(${s})" d="M0 30a22 22 0 0 1 20-28a30 30 0 0 1 56 4a20 20 0 0 1 24 24z" fill="#fff" opacity=".92"/></g>`;
    const clouds = [[60, 1, 170], [150, 0.7, 240], [30, 0.55, 200], [-120, 1.3, 260], [-40, 0.8, 190], [220, 0.6, 280],
      [-220, 1.1, 230], [100, 0.9, 210], [-160, 0.7, 250], [190, 1.2, 300], [-60, 0.6, 180]]
      .map(([y, s, dur]) => cloud(y, s, dur, -rand(0, dur).toFixed(0))).join('');

    return `<defs>
        <linearGradient id="fam-day" gradientUnits="userSpaceOnUse" x1="0" y1="-500" x2="0" y2="560"><stop offset="0" stop-color="#38BDF8"/><stop offset=".55" stop-color="#7DD3FC"/><stop offset="1" stop-color="#E0F2FE"/></linearGradient>
        <linearGradient id="fam-night" gradientUnits="userSpaceOnUse" x1="0" y1="-500" x2="0" y2="560"><stop offset="0" stop-color="#020617"/><stop offset=".5" stop-color="#0F172A"/><stop offset="1" stop-color="#3730A3"/></linearGradient>
        <clipPath id="fam-board-clip"><rect x="230" y="218" width="200" height="144" rx="4"/></clipPath>
      </defs>
      <rect x="${X0}" y="-2000" width="${X1 - X0}" height="${YBOT + 2000}" fill="url(#fam-day)"/>
      <rect class="fam-night-sky" x="${X0}" y="-2000" width="${X1 - X0}" height="${YBOT + 2000}" fill="url(#fam-night)"/>
      <g class="fam-stars" fill="#fff">${stars}</g>
      <g class="fam-sun" data-hit="sun" transform="translate(510 110)"><g class="fam-sun-in">
        <g class="fam-rays" stroke="#FBBF24" stroke-width="5" stroke-linecap="round">${rays}</g>
        <circle r="32" fill="#FDE047" stroke="#F59E0B" stroke-width="3"/>
        <circle cx="-10" cy="-4" r="3" fill="#92400E"/><circle cx="10" cy="-4" r="3" fill="#92400E"/>
        <path d="M-9 8q9 8 18 0" stroke="#92400E" stroke-width="3" fill="none" stroke-linecap="round"/></g></g>
      <g class="fam-moon" data-hit="sun" transform="translate(510 110)">
        <path d="M8,-30A30,30 0 1,0 8,30A22,22 0 1,1 8,-30Z" fill="#FEF3C7" stroke="#FCD34D" stroke-width="2"/>
        <path d="M-14 -4q4 3 8 0" stroke="#92400E" stroke-width="2.5" fill="none" stroke-linecap="round"/></g>
      ${clouds}
      ${birds(40, 70, -20)}${birds(-60, 95, -70)}
      ${hills(478, 34, 600, '#CDEFE3')}
      ${hills(512, 26, 240, '#BBF7D0')}
      ${scatter(46, X0 + 100, X1 - 100, 500, 518, farTree)}
      <g class="fam-tree" data-hit="tree">
        <path d="M84 640C90 560 92 470 100 400L112 400C116 470 118 560 128 640Z" fill="#92400E" stroke="#78350F" stroke-width="3"/>
        <path d="M104 450Q80 430 70 410M110 430Q130 410 146 404" stroke="#78350F" stroke-width="6" fill="none" stroke-linecap="round"/>
        <g class="fam-crown"><circle cx="62" cy="335" r="52" fill="#22C55E"/><circle cx="150" cy="340" r="50" fill="#22C55E"/>
          <circle cx="106" cy="292" r="66" fill="#4ADE80"/><circle cx="104" cy="368" r="48" fill="#16A34A"/>
          ${APPLES.map(([x, y]) => `<g transform="translate(${x} ${y})">${APPLE}</g>`).join('')}</g>
      </g>
      <g class="fam-board" data-hit="board">
        <path d="M262 210L232 596M398 210L428 596" stroke="#92400E" stroke-width="9" stroke-linecap="round"/>
        <path d="M330 196V586" stroke="#78350F" stroke-width="7" stroke-linecap="round"/>
        <rect x="220" y="208" width="220" height="164" rx="8" fill="#A16207" stroke="#78350F" stroke-width="4"/>
        <rect x="230" y="218" width="200" height="144" rx="4" fill="#14532D"/>
        <g clip-path="url(#fam-board-clip)"><g class="fam-plot"></g></g>
        <rect x="236" y="372" width="188" height="8" rx="3" fill="#78350F"/>
        <rect x="380" y="364" width="14" height="8" rx="2" fill="#F8FAFC"/><rect x="400" y="363" width="18" height="9" rx="2" fill="#FDE047"/>
      </g>
      ${hills(556, 22, 300, '#86EFAC')}
      ${scatter(14, -2000, 2600, 586, 600, bush)}
      ${hills(650, 18, 400, '#4ADE80')}
      ${scatter(170, -2000, 2600, 660, 718, (x, y) => (x > 60 && x < 600 ? '' : grass(x, y)))}
      <ellipse cx="108" cy="628" rx="72" ry="22" fill="#A8A29E" stroke="#78716C" stroke-width="3"/>
      <path d="M64 619q24-9 48-5" stroke="#D6D3D1" stroke-width="3" fill="none" stroke-linecap="round"/>
      ${flowers}
      <rect class="fam-tint" x="${X0}" y="-2000" width="${X1 - X0}" height="${YBOT + 2000}" fill="#1E1B4B" pointer-events="none"/>
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
  let svg, plot, fx, tree;
  const st = {};
  const pointer = { x: 0, y: 0, t: -1e9 };
  const bf = { x: 470, y: 380, t: 0, speed: 1, land: null, node: null };
  let boardKind = null;
  let night = false;

  const visible = () => !document.hidden;

  function setMouth(id, kind) {
    const [d, fill] = MOUTH[kind];
    st[id].mouth.setAttribute('d', d);
    st[id].mouth.setAttribute('fill', fill);
  }

  const ANIM_MS = { jump: 600, hop: 400, spin: 800, shake: 900, nod: 800, wiggle: 1200, startle: 500, dizzy: 1300, bounce: 1000, stretch: 1400, wave: 1000, captoss: 1200, stache: 900 };

  /** Jalankan satu aksi (kelas CSS do-*) dan tunggu sampai selesai. */
  function act(id, anim) {
    const node = st[id].el;
    [...node.classList].filter((k) => k.startsWith('do-')).forEach((k) => node.classList.remove(k));
    void node.getBoundingClientRect();   // mulai ulang animasi yang sama
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

  /** Tampilkan gelembung ikon. Selesai (resolve) sedikit sebelum gelembung hilang. */
  function say(id, icon, hold = 2000) {
    const s = st[id];
    s.icon.innerHTML = ICONS[icon];
    s.bubble.classList.remove('show');
    void s.bubble.getBoundingClientRect();
    s.bubble.classList.add('show');
    clearTimeout(s.bubbleTimer);
    s.bubbleTimer = setTimeout(() => s.bubble.classList.remove('show'), hold);
    talk(id, Math.min(900, hold));
    ORDER.filter((o) => o !== id).forEach((o) => lookAt(o, facePoint(id), hold * 0.8));
    return sleep(hold * 0.8);
  }

  function sleepOn(id) { st[id].sleeping = true; st[id].el.classList.add('is-sleep'); setMouth(id, 'flat'); }
  function wake(id) { st[id].sleeping = false; st[id].el.classList.remove('is-sleep'); setMouth(id, 'smile'); }

  function walkTo(id, dx) {
    st[id].wx = dx;
    st[id].walk.style.transform = st[id].bwalk.style.transform = `translateX(${dx}px)`;
  }

  function board(kind = pick(Object.keys(BOARD), boardKind)) {
    boardKind = kind;
    plot.innerHTML = AXES + BOARD[kind]();
    if (REDUCED) return;
    plot.querySelectorAll('.chalk').forEach((p, i) => {
      const len = p.getTotalLength();
      p.style.strokeDasharray = len;
      p.animate([{ strokeDashoffset: len }, { strokeDashoffset: 0 }], { duration: 1100, delay: i * 450, easing: 'ease-out', fill: 'both' });
    });
    plot.querySelectorAll('.chalk-dot').forEach((p) => p.animate([{ opacity: 0 }, { opacity: p.getAttribute('opacity') || 1 }], { duration: 500, delay: 1000, fill: 'backwards' }));
    plot.querySelectorAll('.chalk-bar').forEach((p, i) => p.animate([{ transform: 'scaleY(0)' }, { transform: 'scaleY(1)' }], { duration: 400, delay: 200 + i * 160, easing: 'ease-out', fill: 'backwards' }));
  }

  // ── Efek ───────────────────────────────────────────────────────
  const BITS = [
    '<circle r="5" fill="#F472B6"/>',
    '<path d="M0-6L6 5H-6Z" fill="#FBBF24"/>',
    '<path d="M-7 0q3.5-7 7 0t7 0" stroke="#2563EB" stroke-width="2.5" fill="none" stroke-linecap="round"/>',
    '<path d="M-5 0h10M0-5v10" stroke="#16A34A" stroke-width="3" stroke-linecap="round"/>',
    '<path d="M-6-4h12M-3-4v9M3-4q0 6 2 9" stroke="#7C3AED" stroke-width="2.5" fill="none" stroke-linecap="round"/>',
    '<rect x="-4" y="-4" width="8" height="8" rx="2" fill="#38BDF8"/>',
  ];

  function burst(x, y, n = 9) {
    for (let i = 0; i < n; i++) {
      const g = make('g', {}, pick(BITS));
      fx.appendChild(g);
      const ang = (i / n) * Math.PI * 2 + rand(-0.3, 0.3);
      const dist = rand(36, 80);
      const tx = x + Math.cos(ang) * dist;
      const ty = y + Math.sin(ang) * dist;
      g.animate([
        { transform: `translate(${x}px, ${y}px) scale(.3)`, opacity: 1 },
        { transform: `translate(${tx}px, ${ty}px) scale(1.2) rotate(${rand(-200, 200)}deg)`, opacity: 1, offset: 0.6 },
        { transform: `translate(${tx}px, ${ty + 30}px) scale(.8) rotate(${rand(-300, 300)}deg)`, opacity: 0 },
      ], { duration: rand(900, 1300), easing: 'cubic-bezier(.2,.7,.3,1)' }).finished.then(() => g.remove());
    }
  }

  function flaskBubbles() {
    const c = CHARS.ibu;
    const x0 = c.x + st.ibu.wx + 57 * c.s;
    const y0 = c.y + (125 - 172) * c.s;
    for (let i = 0; i < 6; i++) {
      const b = make('circle', { r: rand(3, 6).toFixed(1), fill: pick(['#A78BFA', '#F0ABFC', '#67E8F9']) });
      fx.appendChild(b);
      b.animate([
        { transform: `translate(${x0}px, ${y0}px)`, opacity: 0.9 },
        { transform: `translate(${x0 + rand(-14, 14)}px, ${y0 - rand(50, 90)}px)`, opacity: 0 },
      ], { duration: rand(900, 1500), delay: i * 120, easing: 'ease-out', fill: 'backwards' }).finished.then(() => b.remove());
    }
  }

  /** Apel jatuh dari pohon; bila ada sasaran, mendarat di kepalanya dulu. Selesai saat benturan. */
  async function appleFall(target) {
    const [ax, ay] = pick(APPLES);
    const g = make('g', {}, APPLE);
    fx.appendChild(g);
    const T = (x, y, r = 0) => ({ transform: `translate(${x}px, ${y}px) rotate(${r}deg)` });
    const hx = target ? CHARS[target].x + st[target].wx : ax + rand(-10, 10);
    const hy = target ? headY(target) + 14 : 655;
    const frames = target
      ? [{ ...T(ax, ay), easing: 'cubic-bezier(.5,0,1,1)' }, { ...T(hx, hy, 40), offset: 0.45, easing: 'ease-out' },
        { ...T(hx + 35, hy - 45, 160), offset: 0.65, easing: 'ease-in' }, { ...T(hx + 70, 655, 300), offset: 0.85 }, T(hx + 95, 655, 420)]
      : [{ ...T(ax, ay), easing: 'cubic-bezier(.5,0,1,1)' }, { ...T(hx, 655, 90), offset: 0.6, easing: 'ease-out' },
        { ...T(hx + 18, 640, 160), offset: 0.75, easing: 'ease-in' }, T(hx + 40, 655, 320)];
    const dur = target ? 1500 : 1200;
    g.animate(frames, { duration: dur, fill: 'forwards' }).finished
      .then(() => g.animate([{ opacity: 1 }, { opacity: 0 }], { duration: 600, delay: 2500, fill: 'forwards' }).finished)
      .then(() => g.remove());
    await sleep(dur * (target ? 0.45 : 0.6));
    if (target) { burst(hx, hy - 6, 6); act(target, 'startle'); }
  }

  async function shakeTree() {
    tree.classList.remove('do-rustle');
    void tree.getBoundingClientRect();
    tree.classList.add('do-rustle');
    const bonk = Math.random() < 0.45;
    await appleFall(bonk ? 'kakek' : null);
    if (bonk) {
      wake('kakek');
      await say('kakek', 'exclaim', 1200);
      act('adik', 'shake');
      say('adik', 'laugh');
      await say('kakek', 'bulb');
    } else {
      act('adik', 'jump');
      await say('adik', 'apple');
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
      sleepOn('kakek');
      say('kakek', 'zzz', 2600);
      act('adik', 'jump');
      say('adik', 'sparkle');
    } else {
      ORDER.forEach((id) => { wake(id); act(id, 'jump'); });
      say('archie', 'sparkle');
    }
  }

  // ── Obrolan (skrip) ────────────────────────────────────────────
  async function theWave() {
    for (const id of ORDER) { act(id, 'jump'); await sleep(170); }
    await sleep(500);
  }

  /** Gag limit: Adik melangkah ke papan, jaraknya selalu tinggal setengah, tak pernah sampai. */
  async function adikApproach() {
    lookAt('adik', { x: OX, y: OY }, 5000);
    for (const dx of [-90, -135, -158, -169, -175, -178]) {
      act('adik', 'hop');
      walkTo('adik', dx);
      await sleep(520);
    }
    await say('adik', 'sweat', 1600);
    walkTo('adik', 0);
    act('adik', 'hop');
    await sleep(500);
  }

  const SCRIPTS = {
    async turunan() {
      board('parabola');
      await say('adik', 'question');
      act('archie', 'wave');
      await say('archie', 'tangent', 2600);
      await say('adik', 'dots', 1400);
      act('adik', 'jump');
      await say('adik', 'bulb');
      act('kakek', 'nod');
      await say('ibu', 'heart');
    },
    async integral() {
      board('area');
      await say('ibu', 'area', 2400);
      act('archie', 'dizzy');
      await say('archie', 'spiral');
      board('riemann');
      await say('ibu', 'riemann', 2600);
      act('archie', 'jump');
      await say('archie', 'bulb');
      act('adik', 'bounce');
      await say('adik', 'sparkle');
    },
    async newton() {
      sleepOn('kakek');
      await say('kakek', 'zzz', 3000);
      await appleFall('kakek');
      wake('kakek');
      await say('kakek', 'exclaim', 1200);
      await say('kakek', 'apple', 1800);
      await say('kakek', 'bulb');
      act('adik', 'shake');
      act('archie', 'shake');
      say('ibu', 'laugh');
      await say('adik', 'laugh');
    },
    async limit() {
      board('limit');
      await say('archie', 'limit', 2600);
      await adikApproach();
      act('ibu', 'shake');
      await say('ibu', 'laugh');
    },
    async gelombang() {
      board('sine');
      await say('ibu', 'sine', 2200);
      await theWave();
      await theWave();
      say('adik', 'note');
      await say('kakek', 'note');
    },
    async takHingga() {
      await say('archie', 'infinity', 2600);
      act('adik', 'dizzy');
      await say('adik', 'spiral');
      await say('kakek', 'tea', 2400);
      await say('ibu', 'heart');
    },
    async pi() {
      board('circle');
      await say('ibu', 'circle', 2400);
      act('adik', 'jump');
      await say('adik', 'pie', 2200);
      act('archie', 'shake');
      await say('archie', 'sweat');
      act('kakek', 'stache');
      await say('kakek', 'laugh');
    },
    async puncak() {
      board('cubic');
      act('archie', 'wiggle');
      await say('archie', 'stonks', 2200);
      await say('kakek', 'dots', 1400);
      await say('kakek', 'crash', 2200);
      act('archie', 'dizzy');
      await say('archie', 'sweat');
      act('adik', 'bounce');
      await say('adik', 'laugh');
    },
  };

  // Tingkah iseng di sela obrolan.
  const ANTICS = {
    async butterflyVisit() {
      const id = pick(ORDER);
      bf.land = id;
      lookAt(id, bf, 4000);
      await sleep(2000);
      act(id, 'wiggle');
      await say(id, pick(['heart', 'sparkle', 'laugh']));
      bf.land = null;
      bf.speed = 3;
    },
    async nap() {
      sleepOn('kakek');
      await say('kakek', 'zzz', 3500);
      await sleep(1500);
      wake('kakek');
      setMouth('kakek', 'o');
      await act('kakek', 'stretch');
      setMouth('kakek', 'smile');
    },
    async yawn() {
      const id = pick(ORDER.filter((x) => !st[x].sleeping));
      setMouth(id, 'o');
      await act(id, 'stretch');
      setMouth(id, 'smile');
    },
    async chase() {
      lookAt('adik', bf, 3000);
      await act('adik', 'hop');
      await act('adik', 'hop');
      await say('adik', 'heart', 1500);
    },
    async dance() {
      ORDER.forEach((id) => act(id, 'wiggle'));
      await say('archie', 'note');
    },
  };

  // Reaksi saat tokoh diklik (diundi, tidak mengulang reaksi terakhir).
  const REACT = {
    archie: [
      async () => { await act('archie', 'captoss'); say('archie', 'sparkle', 1500); },
      async () => { act('archie', 'jump'); await say('archie', pick(['bulb', 'tangent', 'infinity'])); },
      async () => { act('archie', 'wave'); await say('archie', 'heart'); },
      async () => { act('archie', 'spin'); await say('archie', 'stonks'); },
    ],
    ibu: [
      async () => { flaskBubbles(); await say('ibu', 'sparkle'); },
      async () => { act('ibu', 'wave'); await say('ibu', pick(['area', 'riemann', 'circle'])); },
      async () => { act('ibu', 'spin'); await say('ibu', 'heart'); },
      async () => { act('ibu', 'nod'); await say('ibu', 'bulb'); },
    ],
    kakek: [
      async () => { act('kakek', 'stache'); await say('kakek', 'laugh'); },
      async () => { await say('kakek', 'tea', 2400); },
      async () => { act('kakek', 'wave'); await say('kakek', 'note'); },
      async () => { sleepOn('kakek'); await say('kakek', 'zzz', 2600); wake('kakek'); act('kakek', 'startle'); },
    ],
    adik: [
      async () => { act('adik', 'bounce'); await say('adik', 'heart'); },
      async () => { act('adik', 'spin'); await say('adik', 'spiral'); },
      async () => { act('adik', 'jump'); await say('adik', 'question'); },
      async () => { act('adik', 'wave'); await say('adik', 'sparkle'); },
    ],
  };

  function poke(id) {
    const s = st[id];
    if (s.sleeping) {
      wake(id);
      act(id, 'startle');
      say(id, 'exclaim', 1400);
      return;
    }
    s.lastReact = pick(REACT[id], s.lastReact);
    s.lastReact();
    // Keluarga ikut menoleh; kadang ada yang menanggapi.
    ORDER.filter((o) => o !== id).forEach((o) => lookAt(o, facePoint(id), 1600));
    const awake = ORDER.filter((o) => o !== id && !st[o].sleeping);
    if (awake.length && Math.random() < 0.35) {
      const other = pick(awake);
      setTimeout(() => say(other, pick(['laugh', 'heart', 'sparkle', 'question']), 1600), 900);
    }
  }

  // ── Interaksi ──────────────────────────────────────────────────
  function toSvg(e) {
    const pt = svg.createSVGPoint();
    pt.x = e.clientX;
    pt.y = e.clientY;
    return pt.matrixTransform(svg.getScreenCTM().inverse());
  }

  function onClick(e) {
    const ch = e.target.closest('.fam-char');
    if (ch) { poke(ch.dataset.char); return; }
    const hit = e.target.closest('[data-hit]');
    const kind = hit && hit.dataset.hit;
    if (kind === 'board') {
      board();
      const id = pick(ORDER.filter((x) => !st[x].sleeping));
      act(id, 'jump');
      say(id, BOARD_ICON[boardKind]);
    } else if (kind === 'tree') {
      shakeTree();
    } else if (kind === 'sun') {
      toggleNight();
    } else if (kind === 'butterfly') {
      bf.land = null;
      bf.speed = 5;
      burst(bf.x, bf.y, 6);
      lookAt('adik', bf, 2500);
      act('adik', 'jump');
    } else {
      const p = toSvg(e);
      burst(p.x, p.y);
      if (Math.random() < 0.4) say(pick(ORDER), pick(['question', 'sparkle', 'exclaim']), 1400);
    }
  }

  // ── Loop animasi: mata mengikuti sasaran, kupu-kupu terbang ─────
  function targetFor(id, now) {
    const s = st[id];
    if (now - pointer.t < 2200) return pointer;
    if (s.look && s.look.until > now) return s.look.ref;
    if (id === 'adik') return bf;
    return null;
  }

  function moveButterfly() {
    bf.t += 0.006 * bf.speed;
    bf.speed += (1 - bf.speed) * 0.01;
    let tx;
    let ty;
    if (bf.land) {
      tx = CHARS[bf.land].x + st[bf.land].wx;
      ty = headY(bf.land) + 4;
    } else {
      const t = bf.t;
      const d = 1 + Math.sin(t) ** 2;   // lemniskat Bernoulli (lintasan angka 8)
      tx = 465 + (95 * Math.cos(t)) / d;
      ty = 380 + (70 * Math.sin(t) * Math.cos(t)) / d - 20 * Math.sin(t * 3.1);
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
      const c = CHARS[id];
      const t = targetFor(id, now);
      let dx = 0;
      let dy = 1.5;
      if (t) {
        const vx = t.x - (c.x + s.wx);
        const vy = t.y - (c.y + (103 - 172) * c.s);
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

  /** Sutradara: undi obrolan acak (tanpa mengulang), selingi tingkah iseng. */
  async function director() {
    let lastScript = null;
    let lastAntic = null;
    await sleep(1800);
    for (;;) {
      if (!visible()) { await sleep(1000); continue; }
      lastScript = pick(Object.keys(SCRIPTS), lastScript);
      await SCRIPTS[lastScript]();
      await sleep(rand(2200, 4200));
      if (Math.random() < 0.6) {
        lastAntic = pick(Object.keys(ANTICS), lastAntic);
        await ANTICS[lastAntic]();
        await sleep(rand(1500, 3000));
      }
    }
  }

  /**
   * Sesuaikan viewBox dengan ukuran tempatnya; sisa ruang terisi langit, bukit, dan rumput.
   *  - Layar lebar: inti adegan (600×720) di tengah area kiri yang tidak tertutup kartu,
   *    kaki tokoh menempel di dasar layar.
   *  - Banner HP  : hanya papan tulis + keluarga (y ≈ 200–735), di tengah banner.
   */
  function fit(stage) {
    const r = stage.getBoundingClientRect();
    if (!r.width || !r.height) return;
    let scale;
    let centerX;
    if (BANNER.matches) {
      scale = Math.min(r.height / 535, r.width / 620);
      centerX = r.width / 2;
    } else {
      const card = document.querySelector('.auth-split .auth-card');
      const free = card ? Math.max(card.getBoundingClientRect().left - r.left, 360) : r.width;
      scale = Math.min(r.height / 740, (free - 24) / 600, 1.5);
      centerX = free / 2;
    }
    const w = r.width / scale;
    const h = r.height / scale;
    const bottom = BANNER.matches ? 735 : 740;
    svg.setAttribute('viewBox', `${(300 - centerX / scale).toFixed(1)} ${(bottom - h).toFixed(1)} ${w.toFixed(1)} ${h.toFixed(1)}`);
  }

  /** Reaksi adegan pada form (event dari auth_mascot.js). */
  function listenToForm() {
    window.addEventListener('archie:look', (e) => {
      const p = e.detail && toSvg({ clientX: e.detail.x, clientY: e.detail.y });
      ORDER.forEach((id) => { st[id].look = p ? { ref: { x: p.x, y: p.y }, until: performance.now() + 8000 } : null; });
    });
    window.addEventListener('archie:cover', (e) => {
      ['archie', 'adik'].forEach((id) => st[id].el.classList.toggle('is-cover', e.detail.on));
    });
    window.addEventListener('archie:cheer', () => {
      ORDER.forEach((id, i) => { wake(id); setTimeout(() => act(id, 'jump'), i * 90); });
      say('archie', 'sparkle', 1500);
    });
  }

  function init() {
    const stage = document.getElementById('family-stage');
    if (!stage) return;
    svg = make('svg', { class: 'fam', viewBox: '0 0 600 720', preserveAspectRatio: 'xMinYMin meet', role: 'group', 'aria-label': stage.getAttribute('aria-label') });
    svg.innerHTML = sceneMarkup();
    stage.replaceChildren(svg);
    fit(stage);
    window.addEventListener('resize', () => fit(stage));
    BANNER.addEventListener('change', () => fit(stage));

    plot = svg.querySelector('.fam-plot');
    fx = svg.querySelector('.fam-fx');
    tree = svg.querySelector('.fam-tree');
    bf.node = svg.querySelector('.fam-butterfly');
    ORDER.forEach((id) => {
      const el = svg.querySelector(`[data-char="${id}"]`);
      st[id] = {
        el,
        mouth: el.querySelector('.fam-mouth'),
        pupils: el.querySelector('.fam-pupils'),
        walk: svg.querySelector(`[data-walk="${id}"]`),
        bwalk: svg.querySelector(`[data-bwalk="${id}"]`),
        bubble: svg.querySelector(`[data-bubble="${id}"]`),
        icon: svg.querySelector(`[data-bubble="${id}"] .fam-bubble-icon`),
        wx: 0, px: 0, py: 0, sleeping: false,
      };
      el.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); poke(id); }
      });
      blinkLoop(id);
    });

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
    board('parabola');
    requestAnimationFrame(tick);
    if (!REDUCED) director();
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
})();
