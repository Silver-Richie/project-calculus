/**
 * Calculus Bridge — GraphLab
 * ─────────────────────────────────────────────────────────────────────────────
 * Mesin grafik interaktif (vanilla JS + SVG, tanpa library eksternal) untuk
 * materi dan pembahasan soal. Setiap grafik dibangun dari "spec" JSON yang
 * disimpan di database (field `graphs` pada LessonSection dan Question).
 *
 * Mekanisme:
 *   1. Setiap parameter (`params`) menjadi slider. Nilai `value` = nilai di soal.
 *   2. Setiap kali slider digeser, seluruh elemen dihitung ulang dari ekspresi
 *      teks (mis. "a*x**2 + 1") lalu digambar ulang sebagai SVG.
 *   3. Pembandingan: begitu nilai slider berbeda dari nilai soal, grafik awal
 *      tampil sebagai bayangan abu-abu. Tombol "Pin" menyimpan kondisi saat ini
 *      sebagai bayangan berwarna sehingga beberapa kondisi bisa dibandingkan.
 *   4. `readouts` menampilkan nilai penting (awal vs sekarang) dalam tabel.
 *
 * Ringkasan spec 2D (lihat gamification/content/README.md untuk detail):
 *   { type:"2d", title, caption, x:[min,max], y:[min,max], xlabel, ylabel,
 *     params:[{id,label,min,max,step,value}],
 *     elements:[{type:"fn"|"param"|"fill"|"point"|"segment"|"hline"|"vline"|
 *                      "hband"|"vband"|"riemann"|"iter"|"bar"|"text", ...}],
 *     readouts:[{label, expr, digits}] }
 * Spec 3D: { type:"3d", surfaces:[{u:[a,b], v:[a,b], x, y, z, color}], ... }
 *
 * Ekspresi memakai sintaks JavaScript dengan fungsi Math tanpa awalan
 * (sin, cos, exp, ln, sqrt, pi, e, ...) ditambah fact(n), sum(a,b,k=>...),
 * sigmoid(z), clamp(v,lo,hi), fmt(v,digits). Konten berasal dari admin
 * (terpercaya), bukan dari input pengguna.
 */
const GraphLab = (() => {
  'use strict';

  const COLORS = {
    blue: '#2563EB', red: '#DC2626', green: '#16A34A', orange: '#F97316',
    amber: '#D97706', purple: '#7C3AED', gray: '#9A9387', navy: '#1E3A5F',
    teal: '#0D9488', pink: '#DB2777',
  };
  const PIN_COLORS = ['#7C3AED', '#DB2777', '#0D9488'];
  const GHOST_COLOR = '#A8A29E';
  const MAX_PINS = 3;
  const W = 560;
  const PAD = { l: 48, r: 16, t: 16, b: 34 };
  const SAMPLES = 320;

  /* ── Ekspresi ─────────────────────────────────────────────────── */
  const fact = (n) => { let r = 1; for (let i = 2; i <= Math.round(n); i++) r *= i; return r; };
  const sum = (a, b, f) => { let s = 0; for (let k = Math.round(a); k <= Math.round(b); k++) s += f(k); return s; };
  const fmt = (v, d = 3) => {
    if (typeof v !== 'number' || !isFinite(v)) return '—';
    const r = Math.abs(v) < 1e-12 ? 0 : v;
    return r.toLocaleString('id-ID', { maximumFractionDigits: d });
  };

  const BASE = Object.create(null);
  ['sin', 'cos', 'tan', 'asin', 'acos', 'atan', 'atan2', 'sinh', 'cosh', 'tanh', 'exp', 'sqrt', 'cbrt',
    'abs', 'min', 'max', 'pow', 'floor', 'ceil', 'round', 'sign', 'hypot', 'log10', 'log2']
    .forEach((k) => { BASE[k] = Math[k]; });
  Object.assign(BASE, {
    ln: Math.log, log: Math.log, pi: Math.PI, e: Math.E, inf: Infinity,
    fact, sum, fmt,
    sigmoid: (z) => 1 / (1 + Math.exp(-z)),
    clamp: (v, lo, hi) => Math.min(hi, Math.max(lo, v)),
  });

  const cache = new Map();
  function compile(expr) {
    if (cache.has(expr)) return cache.get(expr);
    let f;
    try {
      // `with` tidak boleh di strict mode, tetapi Function() selalu non-strict.
      // eslint-disable-next-line no-new-func
      // Angka negatif hasil generator (mis. "x-" + "-3") → "x- -3" agar tidak terbaca sebagai operator --.
      const src = String(expr).replace(/--/g, '- -');
      f = new Function('S', `with (S) { return (${src}); }`);
    } catch (err) {
      console.warn('[GraphLab] ekspresi tidak valid:', expr, err);
      f = () => NaN;
    }
    cache.set(expr, f);
    return f;
  }

  /** Evaluasi ekspresi (string atau angka) di dalam scope S. */
  function ev(expr, S, fallback = NaN) {
    if (expr === undefined || expr === null || expr === '') return fallback;
    if (typeof expr === 'number') return expr;
    try { return compile(String(expr))(S); } catch (_) { return fallback; }
  }

  /** Mengganti {{ ekspresi }} dalam teks dengan nilainya. */
  function template(str, S) {
    return String(str).replace(/\{\{(.+?)\}\}/g, (_, ex) => {
      const v = ev(ex.trim(), S);
      return typeof v === 'number' ? fmt(v, 3) : String(v);
    });
  }

  function makeScope(values) {
    const S = Object.create(BASE);
    Object.assign(S, values);
    return S;
  }

  const color = (c, fallback = 'blue') => COLORS[c] || c || COLORS[fallback];
  const esc = (s) => String(s).replace(/[&<>"]/g, (ch) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[ch]));

  /* ── Geometri 2D (koordinat data) ─────────────────────────────── */
  /**
   * Mengubah spec elemen menjadi "shape" berkoordinat data, sehingga kondisi
   * awal / pin dapat disimpan dan digambar ulang pada skala apa pun.
   */
  function build2D(spec, S, xr, yr) {
    const shapes = [];
    const ySpan = yr[1] - yr[0];

    (spec.elements || []).forEach((el) => {
      const col = color(el.color);
      const base = { color: col, dash: !!el.dash, width: el.width || 2.4, label: el.label ? template(el.label, S) : '' };
      switch (el.type) {
        case 'fn': {
          const a = ev(el.from, S, xr[0]);
          const b = ev(el.to, S, xr[1]);
          const f = compile(String(el.expr));
          let seg = [];
          let prev = null;
          for (let i = 0; i <= SAMPLES; i++) {
            const x = a + (b - a) * i / SAMPLES;
            S.x = x;
            let y;
            try { y = f(S); } catch (_) { y = NaN; }
            const ok = typeof y === 'number' && isFinite(y) && Math.abs(y) < 1e9;
            if (!ok || (prev !== null && Math.abs(y - prev) > ySpan * 3)) {
              if (seg.length > 1) shapes.push({ k: 'poly', pts: seg, ...base });
              seg = [];
            }
            if (ok) seg.push([x, y]);
            prev = ok ? y : null;
          }
          if (seg.length > 1) shapes.push({ k: 'poly', pts: seg, ...base });
          delete S.x;
          break;
        }
        case 'param': {
          const t0 = ev(el.t[0], S), t1 = ev(el.t[1], S);
          const n = el.samples || 200;
          const pts = [];
          for (let i = 0; i <= n; i++) {
            S.t = t0 + (t1 - t0) * i / n;
            const x = ev(el.x, S), y = ev(el.y, S);
            if (isFinite(x) && isFinite(y)) pts.push([x, y]);
          }
          delete S.t;
          if (pts.length > 1) shapes.push({ k: 'poly', pts, ...base });
          break;
        }
        case 'fill': {
          const a = ev(el.from, S, xr[0]);
          const b = ev(el.to, S, xr[1]);
          if (!(isFinite(a) && isFinite(b)) || b <= a) break;
          const top = [], bot = [];
          const n = 160;
          for (let i = 0; i <= n; i++) {
            S.x = a + (b - a) * i / n;
            const u = ev(el.upper, S), l = ev(el.lower ?? '0', S);
            if (isFinite(u) && isFinite(l)) { top.push([S.x, u]); bot.push([S.x, l]); }
          }
          delete S.x;
          shapes.push({ k: 'area', pts: top.concat(bot.reverse()), ...base, opacity: el.opacity ?? 0.28 });
          break;
        }
        case 'point': {
          const x = ev(el.x, S), y = ev(el.y, S);
          if (isFinite(x) && isFinite(y)) shapes.push({ k: 'dot', x, y, hollow: !!el.hollow, r: el.r || 5, ...base });
          break;
        }
        case 'segment': {
          const p = [ev(el.x1, S), ev(el.y1, S), ev(el.x2, S), ev(el.y2, S)];
          if (p.every(isFinite)) shapes.push({ k: 'poly', pts: [[p[0], p[1]], [p[2], p[3]]], arrow: !!el.arrow, ...base });
          break;
        }
        case 'hline': {
          const y = ev(el.y, S);
          if (isFinite(y)) shapes.push({ k: 'poly', pts: [[xr[0], y], [xr[1], y]], ...base, width: el.width || 1.6 });
          break;
        }
        case 'vline': {
          const x = ev(el.x, S);
          if (isFinite(x)) shapes.push({ k: 'poly', pts: [[x, yr[0]], [x, yr[1]]], ...base, width: el.width || 1.6 });
          break;
        }
        case 'hband': {
          const a = ev(el.from, S), b = ev(el.to, S);
          if (isFinite(a) && isFinite(b)) {
            shapes.push({ k: 'area', pts: [[xr[0], a], [xr[1], a], [xr[1], b], [xr[0], b]], ...base, opacity: el.opacity ?? 0.22 });
          }
          break;
        }
        case 'vband': {
          const a = ev(el.from, S), b = ev(el.to, S);
          if (isFinite(a) && isFinite(b)) {
            shapes.push({ k: 'area', pts: [[a, yr[0]], [b, yr[0]], [b, yr[1]], [a, yr[1]]], ...base, opacity: el.opacity ?? 0.22 });
          }
          break;
        }
        case 'riemann': {
          const a = ev(el.from, S), b = ev(el.to, S);
          const n = Math.max(1, Math.round(ev(el.n, S, 4)));
          const h = (b - a) / n;
          // mode boleh string tetap atau ekspresi angka (slider): 0 kiri, 1 kanan, 2 tengah, 3 trapesium
          const MODES = ['left', 'right', 'mid', 'trap'];
          const mode = MODES.includes(el.mode) ? el.mode
            : (el.mode === undefined ? 'right' : MODES[Math.round(ev(el.mode, S, 1))] || 'right');
          let total = 0;
          for (let i = 0; i < n; i++) {
            const xl = a + i * h, xrr = xl + h;
            if (mode === 'trap') {
              S.x = xl; const yl = ev(el.expr, S);
              S.x = xrr; const yrr = ev(el.expr, S);
              total += h * (yl + yrr) / 2;
              shapes.push({ k: 'area', pts: [[xl, 0], [xrr, 0], [xrr, yrr], [xl, yl]], ...base, opacity: 0.35, stroke: true });
            } else {
              const xs = mode === 'left' ? xl : mode === 'mid' ? xl + h / 2 : xrr;
              S.x = xs; const y = ev(el.expr, S);
              total += h * y;
              shapes.push({ k: 'area', pts: [[xl, 0], [xrr, 0], [xrr, y], [xl, y]], ...base, opacity: 0.35, stroke: true });
            }
          }
          delete S.x;
          if (el.id) S[el.id] = total;
          break;
        }
        case 'iter': {
          // Iterasi umum: state ← update(state), dipakai untuk gradient descent / Newton.
          const names = Object.keys(el.init);
          let st = {};
          names.forEach((k) => { st[k] = ev(el.init[k], S); });
          const steps = Math.max(0, Math.round(ev(el.steps, S, 5)));
          const px = el.px || names[0];
          const py = el.py || names[1] || '0';
          const pts = [];
          const pushPt = () => {
            const T = Object.assign(Object.create(S), st);
            const X = ev(px, T), Y = ev(py, T);
            if (isFinite(X) && isFinite(Y)) pts.push([X, Y]);
          };
          pushPt();
          for (let i = 0; i < steps; i++) {
            const T = Object.assign(Object.create(S), st);
            const next = {};
            names.forEach((k) => { next[k] = ev(el.update[k], T); });
            st = next;
            if (!names.every((k) => isFinite(st[k]) && Math.abs(st[k]) < 1e9)) break;
            pushPt();
          }
          if (el.id) S[el.id] = st;
          if (pts.length > 1) shapes.push({ k: 'poly', pts, ...base });
          pts.forEach((p, i) => shapes.push({ k: 'dot', x: p[0], y: p[1], r: i === pts.length - 1 ? 5 : 3.5, color: col, label: '' }));
          break;
        }
        case 'bar': {
          const x = ev(el.x, S), w = ev(el.w ?? 0.6, S), h = ev(el.h, S);
          if (isFinite(x) && isFinite(h)) {
            shapes.push({ k: 'area', pts: [[x - w / 2, 0], [x + w / 2, 0], [x + w / 2, h], [x - w / 2, h]], ...base, opacity: el.opacity ?? 0.85 });
            if (el.showValue !== false) shapes.push({ k: 'text', x, y: h, text: fmt(h, 3), color: col, anchor: 'middle', dy: h >= 0 ? -6 : 14 });
          }
          break;
        }
        case 'text': {
          const x = ev(el.x, S), y = ev(el.y, S);
          if (isFinite(x) && isFinite(y)) shapes.push({ k: 'text', x, y, text: template(el.text, S), color: col, anchor: el.anchor || 'start', dy: el.dy || 0 });
          break;
        }
        default:
          break;
      }
    });
    return shapes;
  }

  /* ── Geometri 3D (wireframe) ──────────────────────────────────── */
  function build3D(spec, S) {
    const lines = [];
    (spec.surfaces || []).forEach((sf) => {
      const col = color(sf.color);
      const u0 = ev(sf.u[0], S), u1 = ev(sf.u[1], S), v0 = ev(sf.v[0], S), v1 = ev(sf.v[1], S);
      const nu = sf.nu || 18, nv = sf.nv || 24;
      const grid = [];
      for (let i = 0; i <= nu; i++) {
        const row = [];
        for (let j = 0; j <= nv; j++) {
          S.u = u0 + (u1 - u0) * i / nu;
          S.v = v0 + (v1 - v0) * j / nv;
          row.push([ev(sf.x, S), ev(sf.y, S), ev(sf.z, S)]);
        }
        grid.push(row);
      }
      delete S.u; delete S.v;
      for (let i = 0; i <= nu; i++) lines.push({ pts: grid[i], color: col });
      for (let j = 0; j <= nv; j++) lines.push({ pts: grid.map((r) => r[j]), color: col });
    });
    return lines;
  }

  /* ── SVG helpers ──────────────────────────────────────────────── */
  function niceStep(span) {
    const raw = span / 6;
    const mag = Math.pow(10, Math.floor(Math.log10(raw)));
    const n = raw / mag;
    return (n < 1.5 ? 1 : n < 3.5 ? 2 : n < 7.5 ? 5 : 10) * mag;
  }

  function pathD(pts, X, Y) {
    return pts.map((p, i) => `${i ? 'L' : 'M'}${X(p[0]).toFixed(1)},${Y(p[1]).toFixed(1)}`).join('');
  }

  function shapeSVG(sh, X, Y, override) {
    const col = override || sh.color;
    const ghost = !!override;
    switch (sh.k) {
      case 'poly': {
        const dash = sh.dash || ghost ? ' stroke-dasharray="6 4"' : '';
        const marker = sh.arrow && !ghost ? ' marker-end="url(#gl-arrow)"' : '';
        return `<path d="${pathD(sh.pts, X, Y)}" fill="none" stroke="${col}" stroke-width="${ghost ? 1.8 : sh.width}"${dash}${marker} stroke-linejoin="round" stroke-linecap="round" opacity="${ghost ? 0.75 : 1}"/>`;
      }
      case 'area': {
        if (ghost) return `<path d="${pathD(sh.pts, X, Y)}Z" fill="none" stroke="${col}" stroke-width="1.2" stroke-dasharray="4 3" opacity=".7"/>`;
        const stroke = sh.stroke ? ` stroke="${col}" stroke-width="1"` : '';
        return `<path d="${pathD(sh.pts, X, Y)}Z" fill="${col}" fill-opacity="${sh.opacity}"${stroke}/>`;
      }
      case 'dot': {
        const fill = sh.hollow ? '#fff' : col;
        const lbl = sh.label && !ghost ? `<text x="${X(sh.x) + 8}" y="${Y(sh.y) - 8}" class="gl-label" fill="${col}">${esc(sh.label)}</text>` : '';
        return `<circle cx="${X(sh.x)}" cy="${Y(sh.y)}" r="${ghost ? 3.5 : sh.r}" fill="${fill}" stroke="${col}" stroke-width="2" opacity="${ghost ? 0.75 : 1}"/>${lbl}`;
      }
      case 'text':
        if (ghost) return '';
        return `<text x="${X(sh.x)}" y="${Y(sh.y) + (sh.dy || 0)}" text-anchor="${sh.anchor}" class="gl-label" fill="${col}">${esc(sh.text)}</text>`;
      default:
        return '';
    }
  }

  function axesSVG(xr, yr, X, Y, H, spec) {
    let s = '';
    const sx = niceStep(xr[1] - xr[0]);
    const sy = niceStep(yr[1] - yr[0]);
    for (let v = Math.ceil(xr[0] / sx) * sx; v <= xr[1] + 1e-9; v += sx) {
      s += `<line x1="${X(v)}" y1="${PAD.t}" x2="${X(v)}" y2="${H - PAD.b}" class="gl-grid"/>`;
      s += `<text x="${X(v)}" y="${H - PAD.b + 16}" text-anchor="middle" class="gl-tick">${fmt(v, 2)}</text>`;
    }
    for (let v = Math.ceil(yr[0] / sy) * sy; v <= yr[1] + 1e-9; v += sy) {
      s += `<line x1="${PAD.l}" y1="${Y(v)}" x2="${W - PAD.r}" y2="${Y(v)}" class="gl-grid"/>`;
      s += `<text x="${PAD.l - 6}" y="${Y(v) + 4}" text-anchor="end" class="gl-tick">${fmt(v, 2)}</text>`;
    }
    const ax = yr[0] <= 0 && yr[1] >= 0 ? Y(0) : H - PAD.b;
    const ay = xr[0] <= 0 && xr[1] >= 0 ? X(0) : PAD.l;
    s += `<line x1="${PAD.l}" y1="${ax}" x2="${W - PAD.r}" y2="${ax}" class="gl-axis"/>`;
    s += `<line x1="${ay}" y1="${PAD.t}" x2="${ay}" y2="${H - PAD.b}" class="gl-axis"/>`;
    if (spec.xlabel) s += `<text x="${W - PAD.r}" y="${ax - 6}" text-anchor="end" class="gl-axlabel">${esc(spec.xlabel)}</text>`;
    if (spec.ylabel) s += `<text x="${ay + 6}" y="${PAD.t + 10}" class="gl-axlabel">${esc(spec.ylabel)}</text>`;
    return s;
  }

  /* ── Instance ─────────────────────────────────────────────────── */
  function defaults(spec) {
    const v = {};
    (spec.params || []).forEach((p) => { v[p.id] = Number(p.value); });
    return v;
  }

  function isDefault(inst) {
    return (inst.spec.params || []).every((p) => p.id.startsWith('_') || Math.abs(inst.values[p.id] - Number(p.value)) < 1e-12);
  }

  function describeValues(inst, values) {
    return (inst.spec.params || [])
      .filter((p) => !p.id.startsWith('_'))
      .map((p) => `${p.symbol || p.id} = ${fmt(values[p.id], 3)}`).join(', ');
  }

  function render(inst) {
    const { spec, values } = inst;
    const H = spec.height || 340;
    const svg = inst.el.querySelector('.gl-svg');
    let body = '';

    if (spec.type === '3d') {
      body = render3D(inst, H);
    } else {
      const S = makeScope(values);
      const xr = [ev(spec.x?.[0] ?? -5, S), ev(spec.x?.[1] ?? 5, S)];
      const yr = [ev(spec.y?.[0] ?? -5, S), ev(spec.y?.[1] ?? 5, S)];
      const X = (x) => PAD.l + (x - xr[0]) / (xr[1] - xr[0]) * (W - PAD.l - PAD.r);
      const Y = (y) => H - PAD.b - (y - yr[0]) / (yr[1] - yr[0]) * (H - PAD.t - PAD.b);
      const shapes = build2D(spec, S, xr, yr);
      inst.lastScope = S;

      body += axesSVG(xr, yr, X, Y, H, spec);
      body += `<g clip-path="url(#gl-clip-${inst.uid})">`;
      // Bayangan kondisi soal (nilai awal) jika slider sudah digeser
      if (inst.showOriginal && !isDefault(inst)) {
        const S0 = makeScope(inst.initial);
        build2D(spec, S0, xr, yr).forEach((sh) => { body += shapeSVG(sh, X, Y, GHOST_COLOR); });
      }
      inst.pins.forEach((pin) => {
        const Sp = makeScope(pin.values);
        build2D(spec, Sp, xr, yr).forEach((sh) => { body += shapeSVG(sh, X, Y, pin.color); });
      });
      shapes.filter((s) => s.k === 'area').forEach((sh) => { body += shapeSVG(sh, X, Y); });
      shapes.filter((s) => s.k !== 'area').forEach((sh) => { body += shapeSVG(sh, X, Y); });
      body += '</g>';
    }

    svg.setAttribute('viewBox', `0 0 ${W} ${H}`);
    svg.innerHTML = `
      <defs>
        <clipPath id="gl-clip-${inst.uid}"><rect x="${PAD.l}" y="${PAD.t}" width="${W - PAD.l - PAD.r}" height="${H - PAD.t - PAD.b}"/></clipPath>
        <marker id="gl-arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
          <path d="M0,0L10,5L0,10z" fill="currentColor"/>
        </marker>
      </defs>${body}`;

    renderReadouts(inst);
    renderLegend(inst);
    (spec.params || []).forEach((p) => {
      const out = inst.el.querySelector(`[data-out="${p.id}"]`);
      if (out) out.textContent = fmt(values[p.id], 4);
    });
    const origToggle = inst.el.querySelector('.gl-orig-note');
    if (origToggle) origToggle.hidden = isDefault(inst) || !inst.showOriginal;
  }

  function render3D(inst, H) {
    const { spec, values } = inst;
    const S = makeScope(values);
    inst.lastScope = S;
    const yaw = (values._yaw ?? 35) * Math.PI / 180;
    const tilt = (values._tilt ?? 25) * Math.PI / 180;
    const lines = build3D(spec, S);

    // Skala tetap berdasarkan spec.extent agar perubahan parameter terlihat jelas.
    const ext = spec.extent || 2;
    const scale = Math.min(W, H) * 0.36 / ext;
    const cx = W / 2, cy = H / 2 + 10;
    const proj = ([x, y, z]) => {
      const xr = x * Math.cos(yaw) - y * Math.sin(yaw);
      const yr = x * Math.sin(yaw) + y * Math.cos(yaw);
      return [cx + xr * scale, cy - (z * Math.cos(tilt) + yr * Math.sin(tilt)) * scale];
    };
    const poly = (pts, col, w, op, dash) => {
      const d = pts.filter((p) => p.every(isFinite)).map((p, i) => { const [a, b] = proj(p); return `${i ? 'L' : 'M'}${a.toFixed(1)},${b.toFixed(1)}`; }).join('');
      return d ? `<path d="${d}" fill="none" stroke="${col}" stroke-width="${w}" stroke-opacity="${op}"${dash ? ' stroke-dasharray="5 4"' : ''}/>` : '';
    };

    let s = '';
    const ax = spec.axes || [ext, ext, ext];
    [[[-ax[0], 0, 0], [ax[0], 0, 0], 'x'], [[0, -ax[1], 0], [0, ax[1], 0], 'y'], [[0, 0, 0], [0, 0, ax[2]], 'z']].forEach(([a, b, name]) => {
      s += poly([a, b], '#5A5347', 1.2, 0.8);
      const [tx, ty] = proj(b);
      s += `<text x="${tx + 4}" y="${ty}" class="gl-axlabel">${name}</text>`;
    });
    if (inst.showOriginal && !isDefault(inst)) {
      build3D(spec, makeScope(inst.initial)).forEach((l) => { s += poly(l.pts, GHOST_COLOR, 1, 0.5, true); });
    }
    inst.pins.forEach((pin) => {
      build3D(spec, makeScope(pin.values)).forEach((l) => { s += poly(l.pts, pin.color, 1, 0.55, true); });
    });
    lines.forEach((l) => { s += poly(l.pts, l.color, 1.1, 0.75); });
    return s;
  }

  function renderReadouts(inst) {
    const box = inst.el.querySelector('.gl-readouts');
    const list = inst.spec.readouts || [];
    if (!box || !list.length) return;
    const S = inst.lastScope;
    const S0 = makeScope(inst.initial);
    // Elemen iterasi/riemann menulis hasilnya ke scope; hitung ulang untuk nilai awal.
    if (inst.spec.type !== '3d') {
      const xr = [ev(inst.spec.x?.[0] ?? -5, S0), ev(inst.spec.x?.[1] ?? 5, S0)];
      const yr = [ev(inst.spec.y?.[0] ?? -5, S0), ev(inst.spec.y?.[1] ?? 5, S0)];
      build2D(inst.spec, S0, xr, yr);
    }
    const changed = !isDefault(inst);
    box.innerHTML = `
      <table class="gl-table">
        <thead><tr><th>Besaran</th><th>Nilai soal</th>${changed ? '<th>Sekarang</th>' : ''}</tr></thead>
        <tbody>${list.map((r) => {
          const d = r.digits ?? 4;
          const v0 = fmt(ev(r.expr, S0), d);
          const v1 = fmt(ev(r.expr, S), d);
          return `<tr><td>${r.label}</td><td>${v0}</td>${changed ? `<td class="${v0 !== v1 ? 'gl-diff' : ''}">${v1}</td>` : ''}</tr>`;
        }).join('')}</tbody>
      </table>`;
  }

  function renderLegend(inst) {
    const box = inst.el.querySelector('.gl-legend');
    if (!box) return;
    let html = '';
    const S = inst.lastScope || makeScope(inst.values);
    (inst.spec.elements || []).filter((e) => e.label && e.legend !== false).forEach((e) => {
      html += `<span class="gl-chip"><i style="background:${color(e.color)}"></i>${esc(template(e.label, S))}</span>`;
    });
    (inst.spec.surfaces || []).filter((e) => e.label).forEach((e) => {
      html += `<span class="gl-chip"><i style="background:${color(e.color)}"></i>${esc(e.label)}</span>`;
    });
    if (inst.showOriginal && !isDefault(inst)) {
      html += `<span class="gl-chip gl-chip-ghost"><i style="background:${GHOST_COLOR}"></i>Kondisi soal (${esc(describeValues(inst, inst.initial))})</span>`;
    }
    inst.pins.forEach((p, i) => {
      html += `<span class="gl-chip gl-chip-ghost"><i style="background:${p.color}"></i>Pin ${i + 1}: ${esc(describeValues(inst, p.values))}</span>`;
    });
    box.innerHTML = html;
  }

  let uidCounter = 0;

  /**
   * Membuat grafik interaktif di dalam `container`.
   * @param {HTMLElement} container
   * @param {object} spec  Spec grafik (lihat header file).
   */
  function create(container, spec) {
    spec = JSON.parse(JSON.stringify(spec || {}));
    if (spec.type === '3d') {
      spec.params = (spec.params || []).concat([
        { id: '_yaw', label: 'Putar tampilan (°)', min: 0, max: 360, step: 1, value: spec.yaw ?? 35 },
        { id: '_tilt', label: 'Kemiringan kamera (°)', min: 0, max: 85, step: 1, value: spec.tilt ?? 25 },
      ]);
    }
    const inst = {
      uid: ++uidCounter,
      spec,
      values: defaults(spec),
      initial: defaults(spec),
      pins: [],
      showOriginal: spec.compare !== false,
      el: document.createElement('div'),
    };
    const hasParams = (spec.params || []).some((p) => !p.id.startsWith('_'));
    inst.el.className = 'graphlab';
    inst.el.innerHTML = `
      ${spec.title ? `<div class="gl-title">${esc(spec.title)}</div>` : ''}
      <svg class="gl-svg" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="${esc(spec.title || 'Grafik interaktif')}"></svg>
      <div class="gl-legend"></div>
      ${(spec.params || []).length ? `
        <div class="gl-controls">
          ${spec.params.map((p) => `
            <label class="gl-slider">
              <span class="gl-slider-label">${p.label} <b data-out="${p.id}"></b></span>
              <input type="range" min="${p.min}" max="${p.max}" step="${p.step || 'any'}" value="${p.value}" data-param="${p.id}">
            </label>`).join('')}
        </div>
        ${hasParams ? `
        <div class="gl-actions">
          <button type="button" class="gl-btn" data-act="pin">📌 Pin untuk dibandingkan</button>
          <button type="button" class="gl-btn" data-act="reset">↺ Kembali ke nilai soal</button>
          <label class="gl-check"><input type="checkbox" data-act="orig" ${inst.showOriginal ? 'checked' : ''}> Tampilkan grafik soal</label>
        </div>` : ''}` : ''}
      <div class="gl-readouts"></div>
      ${spec.caption ? `<div class="gl-caption">${spec.caption}</div>` : ''}`;
    container.appendChild(inst.el);

    let raf = null;
    const schedule = () => {
      if (raf) return;
      raf = requestAnimationFrame(() => { raf = null; render(inst); });
    };

    inst.el.addEventListener('input', (ev2) => {
      const id = ev2.target.dataset.param;
      if (id) { inst.values[id] = Number(ev2.target.value); schedule(); }
    });
    inst.el.addEventListener('change', (ev2) => {
      if (ev2.target.dataset.act === 'orig') { inst.showOriginal = ev2.target.checked; schedule(); }
    });
    inst.el.addEventListener('click', (ev2) => {
      const act = ev2.target.closest('[data-act]')?.dataset.act;
      if (act === 'pin') {
        if (inst.pins.length >= MAX_PINS) inst.pins.shift();
        const used = inst.pins.map((p) => p.color);
        const col = PIN_COLORS.find((c) => !used.includes(c)) || PIN_COLORS[0];
        inst.pins.push({ values: { ...inst.values }, color: col });
        schedule();
      } else if (act === 'reset') {
        const keepView = { _yaw: inst.values._yaw, _tilt: inst.values._tilt };
        inst.values = defaults(spec);
        if (spec.type === '3d') Object.assign(inst.values, keepView);
        inst.pins = [];
        inst.el.querySelectorAll('input[data-param]').forEach((inp) => { inp.value = inst.values[inp.dataset.param]; });
        schedule();
      }
    });

    render(inst);
    return inst;
  }

  /** Merender daftar spec ke dalam container (dipakai materi & pembahasan). */
  function mountList(container, specs) {
    if (!container || !Array.isArray(specs)) return;
    specs.forEach((s) => create(container, s));
  }

  return { create, mountList, evaluate: ev, fmt };
})();
