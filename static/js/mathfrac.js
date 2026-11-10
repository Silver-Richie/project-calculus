/**
 * Calculus Bridge — Pecahan bertumpuk untuk teks matematika.
 *
 * Soal, opsi, pembahasan, dan materi menulis pecahan sebagai "a/b" (dari generator, bank soal,
 * dan berkas materi). Skrip ini mengubahnya di browser menjadi pecahan bertumpuk, misalnya
 * "1/2", "dy/dx", "(x + 4)(x + 5) / (x + 4)", "e<sup>2x</sup>/2", "∫ xρ dx / ∫ ρ dx".
 *
 * Mekanisme:
 *  - Hanya bekerja di area matematika (SCOPES), jadi angka seperti nyawa "10/10" di HUD tidak berubah.
 *  - Setiap deretan simpul sebaris (teks + <sup>/<sub>/<b>/… ) dijadikan satu string; elemen sebaris
 *    diwakili satu karakter placeholder agar "e<sup>2x</sup>/2" tetap dikenali sebagai satu pecahan.
 *  - Dua tahap: dulu garis miring rapat ("1/2", "dy/dx"), lalu garis miring berspasi
 *    ("(x + 1) / (x − 2)", "sin x / cos x"). Pecahan dari tahap pertama menjadi satu kesatuan pada
 *    tahap kedua, sehingga "4/5 / −3/5" menjadi pecahan bersarang.
 *  - Operand: angka/variabel/simbol tanpa spasi, kelompok (…) […] ⟨…⟩ {…} |…|, panggilan fungsi f(a);
 *    pada garis miring berspasi juga nama fungsi + argumen ("sin x", "ln 2") dan integral/sigma utuh.
 *    Kurung ( ) / [ ] luar operand dibuang (garis pecahan sudah mengelompokkan); |…| dan ⟨…⟩ tetap.
 *  - Dibiarkan sebagai garis miring: satuan ("m/s", "cm²/s"), pilihan kata ("naik/turun",
 *    "Ampère / Faraday"), dan isi grafik GraphLab.
 *  - MutationObserver merender konten yang baru ditambahkan (kuis, pembahasan, materi, homepage).
 *  - Pembaca layar & salin-tempel tetap mendapat "a/b" lewat garis miring tersembunyi.
 */
const MathFrac = (() => {
  'use strict';

  const SCOPES = [
    '.quiz-prompt', '.option-btn', '.rv-options', '.steps-list', '.answer-box', '.expl-note',
    '.hint-card-body', '.lesson-body', '.diag-review', '.qbank-prompt',
  ].join(',');
  const SKIP = 'script, style, pre, textarea, svg, sup, sub, .mfrac, [class*="gl-"]';   // pangkat x^(1/3) tetap a/b
  const INLINE = new Set(['SUP', 'SUB', 'B', 'I', 'EM', 'STRONG', 'SPAN', 'VAR', 'SMALL', 'U']);

  const FN = 'arcsin|arccos|arctan|sinh|cosh|tanh|sin|cos|tan|cot|sec|csc|ln|log|exp|lim|max|min';
  const SUPS = '⁰¹²³⁴⁵⁶⁷⁸⁹⁻';
  const FN_WORD = new RegExp(`^(?:${FN})[${SUPS}]*$`);
  const FN_BEFORE = new RegExp(`(?:^|[^\\p{L}])((?:${FN})[${SUPS}]*) +$`, 'u');
  const FN_ANY = new RegExp(FN, 'g');
  const UNITS = new Set([
    'm', 'cm', 'mm', 'km', 's', 'detik', 'menit', 'jam', 'hari', 'minggu', 'bulan', 'tahun',
    'kg', 'gram', 'L', 'liter', 'mL', 'ml', 'N', 'J', 'W', 'C', '°C', 'K', 'rad', 'mol',
    'Rp', 'orang', 'unit', 'satuan', 'buah', 'ekor', 'Pa', 'V', 'Ω', 'kWh',
  ]);

  const PH_FRAC = 0xE000;   // placeholder pecahan hasil konversi
  const PH_NODE = 0xF000;   // placeholder elemen sebaris (<sup>, <b>, …)
  const TOK = /[\p{L}\p{N}\p{M}π∞√′″!·°∂'^-]/u;
  // Pada garis miring rapat "·" memisahkan faktor: π·1/9·h² = π·(1/9)·h²; pada yang berspasi ikut operand.
  const isTok = (c, spaced) => c !== undefined && TOK.test(c) && (spaced || c !== '·');
  const isDigit = (c) => c !== undefined && /\p{Nd}/u.test(c);
  const PAIRS = { '(': ')', '[': ']', '⟨': '⟩', '{': '}' };
  const OPENER = Object.fromEntries(Object.entries(PAIRS).map(([o, c]) => [c, o]));
  const BIG_OP = /^[∫∬∭∮Σ∑]/;
  const SEG_STOP = /[=;:,≈⇒→<>≤≥]/;

  /** Indeks pasangan kurung untuk s[i] (ke kiri bila s[i] kurung tutup), atau -1. */
  function match(s, i) {
    const c = s[i];
    const fwd = c in PAIRS, open = fwd ? c : OPENER[c], close = PAIRS[open];
    let depth = 0;
    for (let j = i; fwd ? j < s.length : j >= 0; j += fwd ? 1 : -1) {
      if (s[j] === (fwd ? open : close)) depth++;
      else if (s[j] === (fwd ? close : open) && --depth === 0) return j;
    }
    return -1;
  }

  /** Awal operand kiri yang berakhir tepat sebelum `end`. */
  function scanLeft(s, end, spaced) {
    let j = end;
    while (j > 0) {
      const c = s[j - 1];
      if (c in OPENER) {
        const o = match(s, j - 1);
        if (o < 0) break;
        j = o;
      } else if (c === '|' && j === end) {   // |…| hanya sebagai operand utuh: "|x|/2"
        const o = s.lastIndexOf('|', j - 2);
        if (o < 0) break;
        j = o;
      } else if (isTok(c, spaced) || ((c === ',' || c === '.') && isDigit(s[j - 2]) && isDigit(s[j]))) {
        j--;
      } else break;
    }
    return j;
  }

  /** Akhir (eksklusif) operand kanan yang dimulai di `start` (boleh diawali tanda minus). */
  function scanRight(s, start, spaced) {
    let j = start;
    if (s[j] === '−' || s[j] === '-') j++;
    const body = j;
    while (j < s.length) {
      const c = s[j];
      if (c in PAIRS) {
        const e = match(s, j);
        if (e < 0) break;
        j = e + 1;
      } else if (c === '|' && j === body) {  // "1/|x|"
        const e = s.indexOf('|', j + 1);
        if (e < 0) break;
        j = e + 1;
      } else if (isTok(c, spaced) || ((c === ',' || c === '.') && isDigit(s[j - 1]) && isDigit(s[j + 1]))) {
        j++;
      } else break;
    }
    return j === body ? start : j;
  }

  /** Batas "ruas" di sekitar garis miring berspasi (berhenti di =, koma, ⇒, … atau kurung terbuka). */
  function segment(s, from, dir) {
    let j = from, depth = 0;
    for (; dir < 0 ? j > 0 : j < s.length; j += dir) {
      const c = dir < 0 ? s[j - 1] : s[j];
      if ((dir < 0 ? c in OPENER : c in PAIRS)) depth++;
      else if ((dir < 0 ? c in PAIRS : c in OPENER) && --depth < 0) break;
      else if (depth === 0 && (SEG_STOP.test(c) || (c === '.' && !isDigit(s[j + 1])))) break;
    }
    return j;
  }

  /** Buang kurung ( ) / [ ] luar bila membungkus seluruh operand: "(x + 1)" → "x + 1". */
  const wrapped = (op) => (op[0] === '(' || op[0] === '[') && match(op, 0) === op.length - 1;
  const unwrap = (op) => (wrapped(op) ? op.slice(1, -1) : op);

  const plainOf = (op) => op.replace(/[-]/g, '');
  const isWordy = (op) => !wrapped(op) && /[A-Za-zÀ-ž]{3,}/.test(plainOf(op).replace(FN_ANY, ''));
  const isUnit = (op) => plainOf(op).replace(/[⁰¹²³⁴⁵⁶⁷⁸⁹⁻]/g, '').split('·').every((u) => UNITS.has(u));

  /**
   * Ubah semua garis miring pecahan di `s` (rapat atau berspasi, sesuai `spaced`). Pecahan diganti
   * satu karakter placeholder; isinya disimpan di `table` (indeks = kode − PH_FRAC).
   */
  function convert(s, table, spaced) {
    let pos = 0;
    for (;;) {
      const i = s.indexOf('/', pos);
      if (i < 0) return s;
      pos = i + 1;
      const spaceL = /\s/.test(s[i - 1] || ''), spaceR = /\s/.test(s[i + 1] || '');
      if (spaced !== (spaceL || spaceR) || s[i - 1] === '/' || s[i + 1] === '/') continue;

      let end = i;
      while (end > 0 && /\s/.test(s[end - 1])) end--;
      let start = scanLeft(s, end, spaced);
      let rs = i + 1;
      while (rs < s.length && /\s/.test(s[rs])) rs++;
      let rend = scanRight(s, rs, spaced);

      // "…/ln 2", "… / sin x": nama fungsi di kanan membawa argumennya.
      if (FN_WORD.test(s.slice(rs, rend)) && s[rend] === ' ') {
        const more = scanRight(s, rend + 1, spaced);
        if (more > rend + 1) rend = more;
      }
      // Koefisien "4/5x", "128/15π", "10/7(√6 + 1)" = (a/b)·sisanya, seperti ditulis generator.
      if (!spaced && /^\p{N}+(?:[.,]\p{N}+)?$/u.test(s.slice(start, end))) {
        const lead = s.slice(rs, rend).match(/^\p{Nd}+(?:[.,]\p{Nd}+)?/u);
        if (lead) rend = rs + lead[0].length;
      }
      if (spaced) {
        // "sin x / cos x", "ln 2 / 10": nama fungsi + argumen di kiri menjadi satu operand.
        const m = s.slice(0, start).match(FN_BEFORE);
        if (m) start -= m[1].length + (m[0].length - m[0].trimEnd().length);
        // "∫ xρ dx / ∫ ρ dx": integral/sigma diambil seruas penuh.
        let segL = segment(s, end, -1);
        while (/\s/.test(s[segL])) segL++;
        if (BIG_OP.test(s.slice(segL, end))) start = Math.min(start, segL);
        let segR = segment(s, rs, 1);
        while (segR > rs && /\s/.test(s[segR - 1])) segR--;
        if (BIG_OP.test(s.slice(rs, segR))) rend = Math.max(rend, segR);
      }

      const num = s.slice(start, end), den = s.slice(rs, rend);
      if (!num || !den) continue;
      if (isWordy(num) || isWordy(den)) continue;        // "naik/turun", "Ampère / Faraday"
      if (isUnit(num) && isUnit(den)) continue;          // "m/s", "cm²/s"

      // Pecahan di dalam operand ("8/n" dalam "8/(√(1 − 8/n) + 1)") ikut diubah.
      const inner = (op) => convert(convert(op, table, false), table, true);
      const id = table.push({ num: inner(unwrap(num)), den: inner(/^[−-]/.test(den) ? den : unwrap(den)) }) - 1;
      s = s.slice(0, start) + String.fromCharCode(PH_FRAC + id) + s.slice(rend);
      pos = start + 1;
    }
  }

  function build(str, table, nodes) {
    const frag = document.createDocumentFragment();
    let buf = '';
    const flush = () => { if (buf) { frag.appendChild(document.createTextNode(buf)); buf = ''; } };
    for (const ch of str) {
      const code = ch.charCodeAt(0);
      if (code >= PH_NODE && code - PH_NODE < nodes.length) {
        flush();
        frag.appendChild(nodes[code - PH_NODE]);
      } else if (code >= PH_FRAC && code - PH_FRAC < table.length) {
        flush();
        const f = table[code - PH_FRAC];
        const part = (cls, content) => {
          const el = document.createElement('span');
          el.className = cls;
          if (typeof content === 'string') el.textContent = content;
          else el.appendChild(content);
          return el;
        };
        const el = document.createElement('span');
        el.className = 'mfrac';
        el.append(part('mfrac-n', build(f.num, table, nodes)), part('mfrac-sr', '/'),
                  part('mfrac-d', build(f.den, table, nodes)));
        frag.appendChild(el);
      } else buf += ch;
    }
    flush();
    return frag;
  }

  /** Ubah satu deretan simpul sebaris (teks + elemen sebaris) bila mengandung pecahan. */
  function renderRun(run) {
    const texts = run.filter((n) => n.nodeType === 3);
    if (!texts.some((n) => n.data.includes('/')) || texts.some((n) => /[-]/.test(n.data))) return;
    const nodes = [];
    let s = '';
    for (const n of run) {
      if (n.nodeType === 3) s += n.data;
      else { s += String.fromCharCode(PH_NODE + nodes.length); nodes.push(n); }
    }
    const table = [];
    const out = convert(convert(s, table, false), table, true);
    if (!table.length) return;
    const marker = document.createTextNode('');
    run[0].before(marker);
    const frag = build(out, table, nodes);
    run.forEach((n) => n.nodeType === 3 && n.remove());
    marker.replaceWith(frag);
  }

  /** Proses `el` dan turunannya: elemen dalam lebih dulu, lalu deretan simpul sebaris milik `el`. */
  function renderElement(el) {
    if (el.matches(SKIP)) return;
    [...el.children].forEach(renderElement);
    let run = [];
    for (const n of [...el.childNodes]) {
      if (n.nodeType === 3 || (n.nodeType === 1 && INLINE.has(n.tagName) && !n.matches('.mfrac-sr'))) run.push(n);
      else { renderRun(run); run = []; }
    }
    renderRun(run);
  }

  /** Render semua pecahan di dalam `root` (hanya bagian di dalam SCOPES; aman dipanggil berulang). */
  function render(root) {
    if (!root || root.nodeType !== 1 || root.closest(SKIP)) return;
    const scope = root.closest(SCOPES);
    if (scope) renderElement(scope);
    else root.querySelectorAll(SCOPES).forEach((s) => { if (!s.parentElement.closest(SCOPES)) renderElement(s); });
  }

  // Konten baru (kuis, pembahasan, materi) → render pada microtask berikutnya.
  const pending = new Set();
  let queued = false;
  function flushPending() {
    queued = false;
    pending.forEach((el) => { if (el.isConnected) render(el); });
    pending.clear();
  }
  function observe() {
    render(document.body);
    new MutationObserver((records) => {
      records.forEach((r) => r.addedNodes.forEach((n) => {
        const el = n.nodeType === 1 ? n : n.parentElement;
        if (el && !el.closest('.mfrac')) pending.add(el);
      }));
      if (pending.size && !queued) { queued = true; queueMicrotask(flushPending); }
    }).observe(document.body, { childList: true, subtree: true });
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', observe);
  else observe();

  return { render };
})();
