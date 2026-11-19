/**
 * Calculus Bridge — Lambang tier rank duel ("Geometric Cosmos").
 *
 * RankEmblem.svg(tier, { size, className, animated, label }) → string <svg>.
 *
 * Mechanism:
 *   - Setiap tier punya siluet sendiri, dibangun dari geometri yang dihitung (bukan gambar):
 *       Terra : ikosahedron (proyeksi sumbu lipat-3, 10 sisi berbayang) dalam pelat heksagon,
 *               garis kontur topografi (kurva) & strata tanah di dasar.
 *       Luna  : bulan sabit tajam (irisan dua lingkaran, titik potong dihitung) dibelah dua
 *               orbit elips miring (separuh di belakang, separuh di depan), vektor singgung
 *               & skala busur derajat di sisi kanan.
 *       Solar : semburan 12 segitiga runcing berfaset dua (terang/gelap), oktagram inti,
 *               spiral emas r = a·e^(bθ) dengan b = ln φ / (π/2), dan 4 vektor berpanah.
 *       Nova  : belah ketupat yang pecah menjadi 8 serpihan (digeser menjauh dari pusat),
 *               lapisan dalam, inti bintang empat bersinar, dan serpihan fraktal yang terlempar.
 *       Apex  : mahkota dari 5 lengkung runcing yang saling berpotongan, ditopang tiga
 *               lemniskat Bernoulli (∞) bertingkat dengan gradien holografik & inti putih.
 *   - Id <defs> diberi awalan unik per lambang, jadi banyak lambang di satu halaman tidak bentrok.
 *   - animated=true menambah animasi SMIL pelan (rotasi, denyut cahaya, benda mengorbit);
 *     dimatikan bila pengguna memilih prefers-reduced-motion.
 */
const RankEmblem = (() => {
  'use strict';

  let uid = 0;
  const r1 = (n) => Math.round(n * 10) / 10;
  const polar = (r, deg, cx = 100, cy = 100) => {
    const a = deg * Math.PI / 180;
    return [r1(cx + r * Math.cos(a)), r1(cy + r * Math.sin(a))];
  };
  const pts = (list) => list.map((p) => p.join(',')).join(' ');
  const ngon = (n, r, rot = -90, cx = 100, cy = 100) => Array.from({ length: n }, (_, i) => polar(r, rot + i * 360 / n, cx, cy));
  const centroid = (list) => list.reduce((s, p) => [s[0] + p[0] / list.length, s[1] + p[1] / list.length], [0, 0]);

  /** Warna di antara beberapa titik warna hex, t ∈ [0, 1]. */
  function mix(stops, t) {
    const x = Math.min(0.999, Math.max(0, t)) * (stops.length - 1);
    const i = Math.floor(x), k = x - i;
    const a = stops[i].match(/\w\w/g).map((h) => parseInt(h, 16));
    const b = stops[i + 1].match(/\w\w/g).map((h) => parseInt(h, 16));
    return `#${a.map((v, j) => Math.round(v + (b[j] - v) * k).toString(16).padStart(2, '0')).join('')}`;
  }

  const glowFilter = (id, blur = 3) => `
    <filter id="${id}" x="-50%" y="-50%" width="200%" height="200%">
      <feGaussianBlur stdDeviation="${blur}" result="b"/>
      <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>`;
  const spin = (on, dur, from = 0, to = 360) => (on
    ? `<animateTransform attributeName="transform" type="rotate" from="${from} 100 100" to="${to} 100 100" dur="${dur}s" repeatCount="indefinite"/>` : '');
  const pulse = (on, attr, values, dur) => (on ? `<animate attributeName="${attr}" values="${values}" dur="${dur}s" repeatCount="indefinite"/>` : '');
  /** Benda kecil di lintasan: diam di `at`, atau bergerak sepanjang `path` (koordinat absolut) bila animasi aktif. */
  const orbiter = (shape, fill, at, path, dur) => (path
    ? `<polygon points="${shape}" fill="${fill}"><animateMotion dur="${dur}s" repeatCount="indefinite" path="${path}" rotate="auto"/></polygon>`
    : `<polygon points="${shape}" fill="${fill}" transform="translate(${at.join(' ')})"/>`);

  /* ── TERRA: fondasi ──────────────────────────────────────────────── */
  function terra(id, anim) {
    const outer = ngon(6, 94, 0);               // heksagon datar (sisi atas & bawah rata)
    const plate = ngon(6, 84, 0);
    const O = ngon(6, 55, -90);                 // siluet ikosahedron
    const I = [polar(27, -30), polar(27, 90), polar(27, 210)];
    const faces = [
      [I[0], I[1], I[2]],
      [I[0], O[0], O[1]], [I[0], O[1], O[2]], [I[1], O[2], O[3]], [I[1], O[3], O[4]], [I[2], O[4], O[5]], [I[2], O[5], O[0]],
      [I[0], I[1], O[2]], [I[1], I[2], O[4]], [I[2], I[0], O[0]],
    ];
    const shade = ['#064E3B', '#047857', '#10B981', '#2DD4BF', '#99F6E4'];
    const facets = faces.map((f, i) => {
      const [cx, cy] = centroid(f);
      const lit = i === 0 ? 0.78 : 0.5 + 0.5 * ((-(cx - 100) * 0.6 - (cy - 100) * 0.8) / Math.hypot(cx - 100, cy - 100));
      return `<polygon points="${pts(f)}" fill="${mix(shade, lit)}"/>`;
    }).join('');
    const contour = (y, amp) => `M10 ${y} Q55 ${y - amp} 100 ${y} T190 ${y}`;
    const hexPath = `M${outer.map((p) => p.join(' ')).join('L')}Z`;
    return `
      <defs>
        <linearGradient id="${id}-plate" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0" stop-color="#064E3B"/><stop offset=".6" stop-color="#022C22"/><stop offset="1" stop-color="#2B1B0E"/>
        </linearGradient>
        <linearGradient id="${id}-rim" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0" stop-color="#5EEAD4"/><stop offset=".5" stop-color="#10B981"/><stop offset="1" stop-color="#92400E"/>
        </linearGradient>
        <clipPath id="${id}-clip"><polygon points="${pts(plate)}"/></clipPath>
        ${glowFilter(`${id}-glow`, 2.5)}
      </defs>
      <polygon points="${pts(outer)}" fill="none" stroke="url(#${id}-rim)" stroke-width="3"/>
      <polygon points="${pts(plate)}" fill="url(#${id}-plate)" stroke="#34D399" stroke-opacity=".5" stroke-width="1.2"/>
      <g clip-path="url(#${id}-clip)" fill="none">
        <polygon points="${pts(ngon(3, 84, -90))}" stroke="#5EEAD4" stroke-opacity=".18"/>
        <polygon points="${pts(ngon(3, 84, 90))}" stroke="#5EEAD4" stroke-opacity=".18"/>
        ${plate.map((p, i) => `<line x1="${p[0]}" y1="${p[1]}" x2="${O[(i + 1) % 6][0]}" y2="${O[(i + 1) % 6][1]}" stroke="#5EEAD4" stroke-opacity=".22"/>`).join('')}
        ${[52, 64].map((y) => `<path d="${contour(y, 5)}" stroke="#2DD4BF" stroke-opacity=".25"/>`).join('')}
        ${[150, 159, 168, 177].map((y, i) => `<path d="${contour(y, 4 + i)}" stroke="#B45309" stroke-opacity="${0.35 + i * 0.15}" stroke-width="${1.5 + i * 0.6}"/>`).join('')}
      </g>
      <g filter="url(#${id}-glow)">
        ${facets}
        <g fill="none" stroke="#D1FAE5" stroke-width="1.3" stroke-linejoin="round" stroke-opacity=".85">
          ${faces.map((f) => `<polygon points="${pts(f)}"/>`).join('')}
          ${pulse(anim, 'stroke-opacity', '.85;.35;.85', 4)}
        </g>
      </g>
      ${O.map((p) => `<polygon points="${pts(ngon(4, 3.2, 0, p[0], p[1]))}" fill="#ECFDF5"/>`).join('')}
      ${orbiter('0,-4 3,0 0,4 -3,0', '#FDE68A', outer[0], anim && hexPath, 14)}`;
  }

  /* ── LUNA: orbit ─────────────────────────────────────────────────── */
  function crescent(ax, ay, ra, bx, by, rb) {
    const dx = bx - ax, dy = by - ay, d = Math.hypot(dx, dy);
    const a = (ra * ra - rb * rb + d * d) / (2 * d), h = Math.sqrt(ra * ra - a * a);
    const mx = ax + a * dx / d, my = ay + a * dy / d;
    const p1 = [r1(mx - h * dy / d), r1(my + h * dx / d)];
    const p2 = [r1(mx + h * dy / d), r1(my - h * dx / d)];
    return `M${p2.join(' ')}A${ra} ${ra} 0 1 0 ${p1.join(' ')}A${rb} ${rb} 0 1 1 ${p2.join(' ')}Z`;
  }

  function luna(id, anim) {
    const rings = [{ rx: 90, ry: 24, rot: -24, w: 2.2 }, { rx: 76, ry: 17, rot: 34, w: 1.2, dash: '5 4' }];
    const half = (r, front) => `<path d="M${front ? r.rx : -r.rx} 0A${r.rx} ${r.ry} 0 0 1 ${front ? -r.rx : r.rx} 0" fill="none"
      stroke="url(#${id}-orbit)" stroke-width="${r.w}" ${r.dash ? `stroke-dasharray="${r.dash}"` : ''} stroke-opacity="${front ? 1 : 0.45}"/>`;
    const ring = (r, front) => `<g transform="translate(100 100) rotate(${r.rot})">${half(r, front)}</g>`;
    // vektor singgung di orbit utama (t = 35°): arah turunan (−rx sin t, ry cos t)
    const R = rings[0], t = 35 * Math.PI / 180;
    const px = R.rx * Math.cos(t), py = R.ry * Math.sin(t);
    const tx = -R.rx * Math.sin(t), ty = R.ry * Math.cos(t), tl = Math.hypot(tx, ty);
    const ticks = Array.from({ length: 15 }, (_, i) => {
      const deg = -70 + i * 10, long = i % 3 === 1;
      const [x1, y1] = polar(93, deg), [x2, y2] = polar(long ? 85 : 89, deg);
      return `<line x1="${x1}" y1="${y1}" x2="${x2}" y2="${y2}"/>`;
    }).join('');
    const orbitPath = `M${R.rx} 0A${R.rx} ${R.ry} 0 1 1 ${-R.rx} 0A${R.rx} ${R.ry} 0 1 1 ${R.rx} 0`;
    return `
      <defs>
        <radialGradient id="${id}-halo"><stop offset="0" stop-color="#E0F2FE" stop-opacity=".55"/><stop offset="1" stop-color="#E0F2FE" stop-opacity="0"/></radialGradient>
        <linearGradient id="${id}-moon" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0" stop-color="#FFFFFF"/><stop offset=".45" stop-color="#E2E8F0"/><stop offset="1" stop-color="#7DD3FC"/>
        </linearGradient>
        <linearGradient id="${id}-orbit" x1="0" y1="0" x2="1" y2="0">
          <stop offset="0" stop-color="#7DD3FC"/><stop offset=".5" stop-color="#F8FAFC"/><stop offset="1" stop-color="#94A3B8"/>
        </linearGradient>
        <marker id="${id}-arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="5" markerHeight="5" orient="auto-start-reverse">
          <path d="M0 0L10 5L0 10Z" fill="#BAE6FD"/>
        </marker>
        ${glowFilter(`${id}-glow`, 3)}
      </defs>
      <ellipse cx="96" cy="100" rx="82" ry="82" fill="url(#${id}-halo)">${pulse(anim, 'opacity', '1;.55;1', 5)}</ellipse>
      <path d="M${polar(93, -70).join(' ')}A93 93 0 0 1 ${polar(93, 70).join(' ')}" fill="none" stroke="#94A3B8" stroke-opacity=".5"/>
      <g stroke="#CBD5E1" stroke-opacity=".6" stroke-width="1.2">${ticks}</g>
      ${rings.map((r) => ring(r, false)).join('')}
      <g filter="url(#${id}-glow)">
        <path d="${crescent(90, 104, 56, 113, 91, 48)}" fill="url(#${id}-moon)" stroke="#F8FAFC" stroke-width="1.2" stroke-linejoin="miter"/>
      </g>
      <path d="${crescent(90, 104, 50, 113, 91, 48)}" fill="none" stroke="#38BDF8" stroke-opacity=".35"/>
      ${[[150, 6], [186, 4.5], [222, 3.5]].map(([deg, s]) => {
        const [cx, cy] = polar(42, deg, 90, 104);
        return `<polygon points="${pts(ngon(6, s, 0, cx, cy))}" fill="none" stroke="#64748B" stroke-width="1"/>`;
      }).join('')}
      ${rings.map((r) => ring(r, true)).join('')}
      <g transform="translate(100 100) rotate(${R.rot})">
        <line x1="${r1(px)}" y1="${r1(py)}" x2="${r1(px + tx / tl * 30)}" y2="${r1(py + ty / tl * 30)}" stroke="#BAE6FD" stroke-width="1.6" marker-end="url(#${id}-arrow)"/>
        <polygon points="${pts(ngon(4, 4.5, 0, r1(px), r1(py)))}" fill="#F8FAFC"/>
        ${orbiter('0,-5 4,0 0,5 -4,0', '#7DD3FC', [-R.rx, 0], anim && orbitPath, 11)}
      </g>`;
  }

  /* ── SOLAR: energi ───────────────────────────────────────────────── */
  function solar(id, anim) {
    const rays = Array.from({ length: 12 }, (_, i) => {
      const a = -90 + i * 30, tip = polar(i % 2 ? 72 : 95, a);
      const l = polar(30, a - 9), m = polar(30, a), r = polar(30, a + 9);
      return `<polygon points="${pts([l, tip, m])}" fill="url(#${id}-rayA)"/><polygon points="${pts([m, tip, r])}" fill="url(#${id}-rayB)"/>`;
    }).join('');
    const backRays = Array.from({ length: 12 }, (_, i) => {
      const a = -75 + i * 30;
      return `<polygon points="${pts([polar(28, a - 6), polar(60, a), polar(28, a + 6)])}"/>`;
    }).join('');
    const b = Math.log((1 + Math.sqrt(5)) / 2) / (Math.PI / 2);
    const spiral = Array.from({ length: 111 }, (_, i) => {
      const th = i * 0.1, r = 3 * Math.exp(b * th);
      return `${i ? 'L' : 'M'}${r1(100 + r * Math.cos(th))} ${r1(100 + r * Math.sin(th))}`;
    }).join('');
    const vectors = [45, 135, 225, 315].map((a) => {
      const [x1, y1] = polar(58, a), [x2, y2] = polar(93, a);
      return `<line x1="${x1}" y1="${y1}" x2="${x2}" y2="${y2}" marker-end="url(#${id}-arrow)"/>`;
    }).join('');
    return `
      <defs>
        <radialGradient id="${id}-rayA" gradientUnits="userSpaceOnUse" cx="100" cy="100" r="96">
          <stop offset=".3" stop-color="#FEF08A"/><stop offset=".65" stop-color="#F59E0B"/><stop offset="1" stop-color="#DC2626"/>
        </radialGradient>
        <radialGradient id="${id}-rayB" gradientUnits="userSpaceOnUse" cx="100" cy="100" r="96">
          <stop offset=".3" stop-color="#F59E0B"/><stop offset=".7" stop-color="#EA580C"/><stop offset="1" stop-color="#7F1D1D"/>
        </radialGradient>
        <radialGradient id="${id}-core" cx=".4" cy=".35">
          <stop offset="0" stop-color="#FFFBEB"/><stop offset=".5" stop-color="#FCD34D"/><stop offset="1" stop-color="#EA580C"/>
        </radialGradient>
        <radialGradient id="${id}-heat"><stop offset="0" stop-color="#F97316" stop-opacity=".55"/><stop offset="1" stop-color="#F97316" stop-opacity="0"/></radialGradient>
        <marker id="${id}-arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="5" markerHeight="5" orient="auto-start-reverse">
          <path d="M0 0L10 5L0 10Z" fill="#FEF3C7"/>
        </marker>
        ${glowFilter(`${id}-glow`, 3)}
      </defs>
      <ellipse cx="100" cy="100" rx="98" ry="98" fill="url(#${id}-heat)">${pulse(anim, 'opacity', '1;.6;1', 3)}</ellipse>
      <g fill="#B91C1C" fill-opacity=".7">${backRays}${spin(anim, 120, 360, 0)}</g>
      <g>${rays}${spin(anim, 90)}</g>
      <g stroke="#FEF3C7" stroke-width="1.4" stroke-opacity=".8">${vectors}</g>
      <g filter="url(#${id}-glow)">
        <polygon points="${pts(ngon(4, 31, -90))}" fill="#EA580C"/>
        <polygon points="${pts(ngon(4, 31, -45))}" fill="#F59E0B"/>
        <polygon points="${pts(ngon(16, 21, -90))}" fill="url(#${id}-core)" stroke="#FFFBEB" stroke-width="1"/>
      </g>
      <path d="${spiral}" fill="none" stroke="#FFFBEB" stroke-width="1.6" stroke-opacity=".85" stroke-linecap="round">${spin(anim, 40)}</path>`;
  }

  /* ── NOVA: ledakan ───────────────────────────────────────────────── */
  function nova(id, anim) {
    const P = [[100, 6], [145, 49], [178, 100], [138, 150], [100, 194], [58, 152], [22, 100], [60, 47]];
    const C = [103, 97];
    const shards = P.map((p, i) => {
      const tri = [C, p, P[(i + 1) % 8]];
      const [cx, cy] = centroid(tri);
      const d = Math.hypot(cx - C[0], cy - C[1]);
      const ox = r1((cx - C[0]) / d * 6), oy = r1((cy - C[1]) / d * 6);
      return `<polygon points="${pts(tri)}" transform="translate(${ox} ${oy})" fill="url(#${id}-shard${i % 2 ? 'B' : 'A'})"/>`;
    }).join('');
    const fractal = [45, 135, 225, 315].map((a) => [[70, 9], [84, 6], [94, 3.5]].map(([r, s]) => {
      const [x, y] = polar(r, a);
      return `<polygon points="${pts(ngon(4, s, -90, x, y))}"/>`;
    }).join('')).join('');
    const sparks = Array.from({ length: 8 }, (_, i) => {
      const a = 22.5 + i * 45, [x1, y1] = polar(24, a), [x2, y2] = polar(98, a);
      return `<line x1="${x1}" y1="${y1}" x2="${x2}" y2="${y2}"/>`;
    }).join('');
    return `
      <defs>
        <radialGradient id="${id}-space"><stop offset="0" stop-color="#E879F9" stop-opacity=".75"/><stop offset=".55" stop-color="#7E22CE" stop-opacity=".35"/><stop offset="1" stop-color="#0B0518" stop-opacity="0"/></radialGradient>
        <linearGradient id="${id}-shardA" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#D946EF"/><stop offset="1" stop-color="#2E1065"/></linearGradient>
        <linearGradient id="${id}-shardB" x1="1" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#8B5CF6"/><stop offset="1" stop-color="#14071F"/></linearGradient>
        <radialGradient id="${id}-core"><stop offset="0" stop-color="#FFFFFF"/><stop offset=".45" stop-color="#F5D0FE"/><stop offset="1" stop-color="#C026D3"/></radialGradient>
        ${glowFilter(`${id}-glow`, 4)}
      </defs>
      <ellipse cx="100" cy="100" rx="96" ry="96" fill="url(#${id}-space)">${pulse(anim, 'opacity', '1;.5;1', 2.6)}</ellipse>
      <g stroke="#F0ABFC" stroke-opacity=".35" stroke-dasharray="2 5">${sparks}</g>
      <g stroke="#F5D0FE" stroke-width="1" stroke-opacity=".8" stroke-linejoin="round">${shards}</g>
      <polygon points="${pts(ngon(4, 44, -45, C[0], C[1]))}" fill="#0B0518" stroke="#E879F9" stroke-width="1.4"/>
      <polygon points="${pts(ngon(4, 30, -90, C[0], C[1]))}" fill="none" stroke="#C084FC" stroke-opacity=".7"/>
      <g fill="#F0ABFC">${fractal}
        ${anim ? '<animateTransform attributeName="transform" type="scale" values="1;1.04;1" additive="sum" dur="2.6s" repeatCount="indefinite"/>' : ''}</g>
      <g filter="url(#${id}-glow)">
        <path d="M103 61Q107 93 139 97Q107 101 103 133Q99 101 67 97Q99 93 103 61Z" fill="url(#${id}-core)">
          ${pulse(anim, 'opacity', '1;.7;1', 1.6)}</path>
      </g>`;
  }

  /* ── APEX: puncak ────────────────────────────────────────────────── */
  function lemniscate(a, sy, cx = 100, cy = 134) {
    return Array.from({ length: 121 }, (_, i) => {
      const t = i / 120 * Math.PI * 2, d = 1 + Math.sin(t) ** 2;
      return `${i ? 'L' : 'M'}${r1(cx + a * Math.cos(t) / d)} ${r1(cy + sy * a * Math.sin(t) * Math.cos(t) / d)}`;
    }).join('') + 'Z';
  }

  function apex(id, anim) {
    const spikes = [[44, 66, 19], [156, 66, 19], [72, 42, 21], [128, 42, 21], [100, 12, 23]];
    const arch = (x, tip, w, base = 126) => {
      const c = base - (base - tip) * 0.55;
      return `M${x - w} ${base}C${x - w} ${c} ${x - 4} ${tip + 20} ${x} ${tip}C${x + 4} ${tip + 20} ${x + w} ${c} ${x + w} ${base}`;
    };
    return `
      <defs>
        <linearGradient id="${id}-holo" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0" stop-color="#22D3EE"/><stop offset=".35" stop-color="#A78BFA"/><stop offset=".6" stop-color="#F0ABFC"/>
          <stop offset=".8" stop-color="#FDE68A"/><stop offset="1" stop-color="#22D3EE"/>
          ${anim ? '<animateTransform attributeName="gradientTransform" type="rotate" from="0 .5 .5" to="360 .5 .5" dur="10s" repeatCount="indefinite"/>' : ''}
        </linearGradient>
        <linearGradient id="${id}-obsidian" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0" stop-color="#374151"/><stop offset=".5" stop-color="#111827"/><stop offset="1" stop-color="#030712"/>
        </linearGradient>
        <radialGradient id="${id}-core"><stop offset="0" stop-color="#FFFFFF"/><stop offset=".5" stop-color="#E0F2FE" stop-opacity=".8"/><stop offset="1" stop-color="#22D3EE" stop-opacity="0"/></radialGradient>
        ${glowFilter(`${id}-glow`, 3)}
      </defs>
      <g transform="translate(0 12)">
      <g fill="none" stroke="url(#${id}-holo)">
        <ellipse cx="100" cy="134" rx="94" ry="28" stroke-width="1.5" stroke-opacity=".5" stroke-dasharray="1 6"/>
      </g>
      ${spikes.map(([x, tip, w]) => `
        <path d="${arch(x, tip, w)}" fill="url(#${id}-obsidian)" stroke="url(#${id}-holo)" stroke-width="2.2" stroke-linejoin="round"/>
        <path d="${arch(x, tip + 14, w - 8)}" fill="none" stroke="#67E8F9" stroke-opacity=".45" stroke-width="1"/>
        <polygon points="${pts(ngon(4, x === 100 ? 7 : 5, -90, x, tip))}" fill="${x === 100 ? '#FDE68A' : '#67E8F9'}" filter="url(#${id}-glow)"/>`).join('')}
      <g fill="none" stroke-linejoin="round">
        <path d="${lemniscate(84, 1.25)}" stroke="#67E8F9" stroke-opacity=".55" stroke-width="1" stroke-dasharray="3 3"/>
        <path d="${lemniscate(84, 0.9)}" stroke="#030712" stroke-width="9"/>
        <path d="${lemniscate(84, 0.9)}" stroke="url(#${id}-holo)" stroke-width="5"/>
        <path d="${lemniscate(70, 0.45)}" stroke="#FDE68A" stroke-width="1.3" stroke-opacity=".9"/>
      </g>
      <g filter="url(#${id}-glow)">
        <ellipse cx="100" cy="134" rx="13" ry="13" fill="url(#${id}-core)">${pulse(anim, 'rx', '13;17;13', 2.4)}${pulse(anim, 'ry', '13;17;13', 2.4)}</ellipse>
        <path d="M100 124Q101.5 132.5 110 134Q101.5 135.5 100 144Q98.5 135.5 90 134Q98.5 132.5 100 124Z" fill="#FFFFFF"/>
      </g>
      </g>`;
  }

  const DRAW = { terra, luna, solar, nova, apex };
  const NAMES = { terra: 'Terra', luna: 'Luna', solar: 'Solar', nova: 'Nova', apex: 'Apex' };

  return {
    /** Lambang tier sebagai string SVG. */
    svg(tier, { size = 64, className = '', animated = false, label = '' } = {}) {
      const draw = DRAW[tier] || terra;
      const reduce = typeof window !== 'undefined' && window.matchMedia?.('(prefers-reduced-motion: reduce)').matches;
      const id = `rk${++uid}`;
      const name = label || `Lambang ${NAMES[tier] || 'Terra'}`;
      return `<svg class="rank-emblem ${className}" viewBox="0 0 200 200" width="${size}" height="${size}" role="img" aria-label="${name}" fill="none">
        ${draw(id, animated && !reduce)}</svg>`;
    },
  };
})();
