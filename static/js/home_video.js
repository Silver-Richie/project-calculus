/**
 * Calculus Bridge — Pemutar "video" animasi di homepage (tanpa file video).
 *
 * Mekanisme:
 *  - Setiap bab (CHAPTERS) berisi beberapa adegan { cap, dur, html, tick? }:
 *      cap  : narasi Archie (teks di bawah layar, juga dibacakan pembaca layar)
 *      dur  : lama adegan (ms)
 *      html : isi kanvas 640×360 (dibangun ulang tiap adegan dimulai → animasi CSS mulai dari awal)
 *      tick : opsional, dipanggil tiap frame dengan waktu adegan (ms) untuk animasi berbasis JS
 *  - Jam pemutar maju lewat requestAnimationFrame hanya saat diputar; jeda = kelas .is-paused yang
 *    juga menghentikan semua animasi CSS di kanvas, jadi jam JS dan animasi CSS tetap sinkron.
 *  - open('tour') memutar pembuka + semua bab + penutup; open('<bab>') memutar satu bab saja.
 *  - Kanvas berukuran tetap lalu diskalakan (--s) mengikuti lebar layar.
 *  Keyboard saat terbuka: Spasi = putar/jeda, ←/→ = adegan sebelum/berikutnya, Esc = tutup.
 */
const HomeVideo = (() => {
  'use strict';

  const W = 640;

  // ── Potongan HTML adegan ─────────────────────────────────────────────────────
  const at = (l, t, more = '') => `style="left:${l}px;top:${t}px;${more}"`;
  const d = (sec, more = '') => `--d:${sec}s;${more}`;

  /** Archie di kanvas. Kelas 'mascot-*' dipasang di svg-nya agar tidak bentrok dengan animasi muncul. */
  function archie(size, l, t, cls = 'v-pop', more = '') {
    const tpl = document.getElementById('archie-tpl');
    const svg = tpl.content.firstElementChild.cloneNode(true);
    svg.setAttribute('width', size);
    svg.setAttribute('height', size);
    const mood = cls.split(' ').filter((c) => c.startsWith('mascot-'));
    svg.classList.add(...mood);
    cls = cls.split(' ').filter((c) => !c.startsWith('mascot-')).join(' ');
    return `<div class="v-abs ${cls}" ${at(l, t, more)}>${svg.outerHTML}</div>`;
  }

  const cursor = (l, t, cls = '', more = '') =>
    `<svg class="v-cursor ${cls}" ${at(l, t, more)} viewBox="0 0 24 24"><path d="M3 2l7 19 2.5-7.5L20 11z" fill="#fff" stroke="#0F172A" stroke-width="1.5" stroke-linejoin="round"/></svg>`;

  const title = (text, sec = 0) => `<div class="v-title v-in" style="${d(sec)}">${text}</div>`;

  /** Angka gaya Indonesia: koma desimal, tanda minus asli. */
  const num = (v, digits = 2) => v.toFixed(digits).replace('.', ',').replace('-', '−');

  // ── Grafik garis singgung y = x² (bab Grafik) ───────────────────────────────
  const GX = (x) => 200 + x * 80;
  const GY = (y) => 190 - y * 40;
  const PARABOLA = (() => {
    let p = '';
    for (let x = -2.3; x <= 2.31; x += 0.1) p += `${p ? 'L' : 'M'}${GX(x).toFixed(1)} ${GY(x * x).toFixed(1)} `;
    return p;
  })();

  function graphHTML(extra = '') {
    const grid = [-2, -1, 1, 2].map((x) => `<line x1="${GX(x)}" y1="0" x2="${GX(x)}" y2="220" stroke="#1E293B"/>`).join('')
      + [1, 2, 3, 4].map((y) => `<line x1="0" y1="${GY(y)}" x2="400" y2="${GY(y)}" stroke="#1E293B"/>`).join('');
    return `
      <div class="v-card v-in" ${at(110, 14, 'width:420px;height:300px;')}></div>
      <svg class="v-abs" ${at(120, 24, 'width:400px;height:220px;overflow:hidden;border-radius:10px;background:#0F172A')} viewBox="0 0 400 220">
        ${grid}
        <line x1="0" y1="${GY(0)}" x2="400" y2="${GY(0)}" stroke="#64748B" stroke-width="1.4"/>
        <line x1="${GX(0)}" y1="0" x2="${GX(0)}" y2="220" stroke="#64748B" stroke-width="1.4"/>
        <path d="${PARABOLA}" fill="none" stroke="#3B82F6" stroke-width="3"/>
        <text x="${GX(1.75)}" y="${GY(4.2)}" fill="#93C5FD" font-size="14" font-weight="700">y = x²</text>
        ${extra}
        <line id="v-tan" stroke="#F97316" stroke-width="3" stroke-linecap="round"/>
        <circle id="v-pt" r="6" fill="#F97316" stroke="#fff" stroke-width="2"/>
      </svg>
      <div class="v-abs" ${at(150, 258, 'width:340px;height:6px;border-radius:3px;background:#334155')}></div>
      <div class="v-abs" id="v-thumb" ${at(150, 252, 'width:18px;height:18px;margin-left:-9px;border-radius:50%;background:#3B82F6;border:3px solid #fff')}></div>
      <div class="v-abs" ${at(126, 250, 'font-weight:800;color:#94A3B8')}>a</div>
      <div class="v-pill" id="v-read" ${at(190, 278, 'font-size:13px;background:#172554;border-color:#3B82F6')}></div>`;
  }

  function setTangent(canvas, a) {
    const line = canvas.querySelector('#v-tan');
    if (!line) return;
    const x1 = a - 1.3, x2 = a + 1.3;
    const yAt = (x) => a * a + 2 * a * (x - a);
    line.setAttribute('x1', GX(x1)); line.setAttribute('y1', GY(yAt(x1)));
    line.setAttribute('x2', GX(x2)); line.setAttribute('y2', GY(yAt(x2)));
    const pt = canvas.querySelector('#v-pt');
    pt.setAttribute('cx', GX(a)); pt.setAttribute('cy', GY(a * a));
    canvas.querySelector('#v-thumb').style.left = `${150 + ((a + 2) / 4) * 340}px`;
    canvas.querySelector('#v-read').innerHTML = `a = ${num(a)} &nbsp;·&nbsp; f′(a) = 2a = <b style="color:#FDBA74">${num(2 * a)}</b>`;
  }

  // ── Bab & adegan ─────────────────────────────────────────────────────────────
  const QUIZ_CARD = (opts) => `
    <div class="v-card ${opts.enter ? 'v-in' : ''}" ${at(110, 22, 'width:420px;height:316px;padding:18px;')}>
      <div style="display:flex;justify-content:space-between;align-items:center;font-size:12px;color:#94A3B8;font-weight:700">
        Soal 3 dari 10 <span class="v-chip" style="background:rgba(34,197,94,.16);color:#4ADE80">Mudah</span></div>
      <div style="margin-top:10px;padding:12px 14px;border-radius:10px;background:#273449;font-size:16px;font-weight:600">
        Turunan dari f(x) = 3x² + 5x adalah …</div>
      <div class="v-opt ${opts.a || ''}" style="${opts.ad || ''}"><b>A</b>6x + 5</div>
      <div class="v-opt ${opts.enter ? 'v-in' : ''}" style="${d(0.5)}"><b>B</b>3x + 5</div>
      <div class="v-opt ${opts.enter ? 'v-in' : ''}" style="${d(0.65)}"><b>C</b>6x² + 5</div>
      <div class="v-opt ${opts.enter ? 'v-in' : ''}" style="${d(0.8)}"><b>D</b>6x</div>
    </div>`;

  const write = (text, l, t, sec, ms, size = 40, color = '#1E1B16') =>
    `<div class="v-abs v-write" ${at(l, t, `${d(sec)}--t:${ms}ms;font:700 ${size}px 'Segoe Print','Comic Sans MS','Bradley Hand',cursive;color:${color}`)}>${text}</div>`;

  const CHAPTERS = {
    intro: {
      title: 'Halo dari Archie',
      scenes: [{
        cap: 'Halo! Aku Archie. Ayo kenalan dengan Calculus Bridge, jembatanmu menuju kalkulus!',
        dur: 5000,
        html: () => `
          <svg class="v-abs" ${at(40, 170, 'width:560px;height:170px')} viewBox="0 0 560 170">
            <path d="M0 120 Q30 110 60 128 L60 170 L0 170Z M500 128 Q530 110 560 120 L560 170 L500 170Z" fill="#273449"/>
            <path class="v-draw" style="${d(0.9, '--len:640;--t:1.4s')}" d="M50 128 C150 128 190 20 280 20 S410 128 510 128" fill="none" stroke="#3B82F6" stroke-width="6" stroke-linecap="round"/>
          </svg>
          ${archie(150, 245, 40, 'v-pop v-wave')}
          <div class="v-title v-in" style="top:282px;${d(0.6)}">Calculus <span style="color:#60A5FA">Bridge</span></div>
          <div class="v-sub v-in" style="top:318px;${d(1.4)}">Jembatanmu menuju kalkulus · FT · FMIPA · Fasilkom</div>`,
      }],
    },

    peta: {
      title: 'Peta Belajar 4 Level',
      scenes: [
        {
          cap: 'Kurikulumnya punya 4 level, dari PreCalculus sampai Kalkulus Tingkat Lanjut.',
          dur: 4500,
          html: () => `
            ${title('Peta Belajar Kalkulus')}
            <div class="v-pill v-pop" ${at(40, 280, d(0.3))}>🧱 PreCalculus</div>
            <div class="v-pill v-pop" ${at(130, 222, d(0.7))}>📐 Kalkulus Dasar</div>
            <div class="v-pill v-pop" ${at(230, 164, d(1.1))}>🌀 Kalkulus Tingkat Menengah</div>
            <div class="v-pill v-pop" ${at(360, 106, d(1.5, 'border-color:#F59E0B'))}>🚀 Kalkulus Tingkat Lanjut</div>
            ${archie(90, 500, 230, 'v-pop v-wave', d(1.9))}`,
        },
        {
          cap: 'Selesaikan satu node untuk membuka node berikutnya, seperti peta di game.',
          dur: 5000,
          html: () => `
            ${title('Buka node satu per satu')}
            <svg class="v-abs" ${at(0, 0, 'width:640px;height:360px')} viewBox="0 0 640 360">
              <path d="M149 289 L289 199 L429 269 L549 149" fill="none" stroke="#334155" stroke-width="5" stroke-dasharray="4 10" stroke-linecap="round"/>
            </svg>
            <div class="v-node done v-turn-done" ${at(120, 260, d(1))}><span class="v-fade-out" style="${d(0.8)}">🔢</span></div>
            <div class="v-abs v-pop" ${at(139, 270, d(1.1, 'font-size:26px;font-weight:900;color:#fff'))}>✓</div>
            <div class="v-xp v-float-up" ${at(110, 220, d(1.2))}>+10 XP</div>
            <div class="v-node on v-turn-on" ${at(260, 170, d(2))}><span class="v-fade-out" style="${d(1.8)}">🔒</span></div>
            <div class="v-abs v-pop" ${at(276, 183, d(2.1, 'font-size:24px'))}>📈</div>
            <div class="v-node" ${at(400, 240)}>🔒</div>
            <div class="v-node" ${at(520, 120)}>🔒</div>
            ${archie(54, 262, 108, 'v-hop', d(2.3, '--fx:-140px;--fy:90px;--t:.9s'))}`,
        },
        {
          cap: 'Tiap topik punya 5 sesi latihan: Mudah, Sedang, Sulit, Tantangan, dan Olimpiade.',
          dur: 4500,
          html: () => `
            ${title('5 sesi latihan per topik')}
            <div class="v-row on v-left" ${at(150, 76, d(0.2))}>🌱 Sesi I · Mudah<em class="v-glow" style="${d(1.4)}">Mulai ➔</em></div>
            <div class="v-row v-left" ${at(150, 124, d(0.4))}>🔒 Sesi II · Sedang<em>Terkunci</em></div>
            <div class="v-row v-left" ${at(150, 172, d(0.6))}>🔒 Sesi III · Sulit<em>Terkunci</em></div>
            <div class="v-row v-left" ${at(150, 220, d(0.8))}>🔒 Sesi IV · Tantangan<em>Terkunci</em></div>
            <div class="v-row v-left" ${at(150, 268, d(1))}>🔒 Sesi V · Olimpiade<em>Terkunci</em></div>
            ${archie(80, 520, 250, 'v-pop', d(1.3))}`,
        },
      ],
    },

    latihan: {
      title: 'Latihan & Pembahasan',
      scenes: [
        {
          cap: 'Soal diacak khusus untukmu, jadi angkanya baru setiap kali mencoba.',
          dur: 5000,
          html: () => `
            ${QUIZ_CARD({ enter: true, a: 'sel v-turn-sel', ad: d(2.8) })}
            ${cursor(420, 138, 'v-move', d(1.6, '--fx:150px;--fy:150px;--t:1.1s'))}`,
        },
        {
          cap: 'Langsung tahu benar atau salah. Bingung? Minta hint bertahap.',
          dur: 4500,
          html: () => `
            ${QUIZ_CARD({ a: 'ok v-turn-ok', ad: d(0.3) })}
            <div class="v-toast v-pop" ${at(462, 190, d(0.5))}>✓ Benar! +10 XP</div>
            <div class="v-pill v-pop v-glow" ${at(520, 60, d(1.2, 'background:#F97316;border-color:#F97316;color:#fff;font-size:13px'))}>💡 Hint</div>
            ${archie(84, 540, 262, 'v-pop mascot-celebrate', d(0.9))}`,
        },
        {
          cap: 'Pembahasan langkah demi langkah selalu tersedia setelah menjawab.',
          dur: 5000,
          html: () => `
            <div class="v-card v-in" ${at(110, 30, 'width:420px;height:290px;padding:20px 22px;')}>
              <div style="font-weight:800;color:#4ADE80;font-size:16px">📚 Pembahasan</div>
              <ol style="margin:12px 0 0 20px;font-size:15px;line-height:1.5">
                <li class="v-in" style="${d(0.5)}">Turunkan tiap suku: (3x²)′ = 6x</li>
                <li class="v-in" style="${d(1.4)}">(5x)′ = 5</li>
                <li class="v-in" style="${d(2.3)}">Jadi f′(x) = <b>6x + 5</b></li>
              </ol>
              <div class="v-in" style="${d(3.1, 'margin-top:16px;padding:10px 14px;border-radius:10px;background:rgba(34,197,94,.16);border:1px solid #22C55E;font-weight:700')}">Jawaban: 6x + 5</div>
              <div class="v-in" style="${d(3.6, 'margin-top:12px;font-size:12px;color:#94A3B8')}">💬 Aturan pangkat: (axⁿ)′ = n·axⁿ⁻¹</div>
            </div>`,
        },
        {
          cap: 'Mau santai? Latihan Bebas: pilih topik sesukamu, tanpa nyawa dan tanpa XP.',
          dur: 4500,
          html: () => {
            const topics = ['Aturan Rantai', 'Limit Fungsi', 'Integral Tentu', 'Optimasi'];
            return `
              ${title('Latihan Bebas')}
              <div class="v-sub v-in" style="${d(0.2)}">❤️ tanpa nyawa · ⚡ tanpa XP · 🎲 soal acak</div>
              ${topics.map((tp, i) => `
                <div class="v-row v-left" ${at(150, 92 + i * 48, d(0.3 + i * 0.15))}>
                  <span style="position:relative;width:20px;height:20px;border-radius:5px;border:2px solid #64748B">
                    ${i !== 2 ? `<span class="v-pop" style="${d(1.2 + i * 0.35, 'position:absolute;inset:-2px;border-radius:5px;background:#22C55E;display:grid;place-items:center;font-size:12px;color:#fff')}">✓</span>` : ''}
                  </span>${tp}</div>`).join('')}
              <div class="v-pill v-pop" ${at(268, 296, d(2.8, 'background:#3B82F6;border-color:#3B82F6'))}>Mulai ➔</div>`;
          },
        },
      ],
    },

    grafik: {
      title: 'Grafik Interaktif',
      scenes: [
        {
          cap: 'Materi disusun bertahap dengan rujukan Whitman, Strang (MIT), dan Stewart.',
          dur: 4500,
          html: () => `
            <div class="v-card v-in" ${at(130, 36, 'width:380px;height:280px;padding:22px;')}>
              <span class="v-chip">📚 Whitman · Strang · Stewart</span>
              <div style="font:800 19px var(--font-head);margin-top:12px">Turunan = gradien garis singgung</div>
              <div class="v-line v-left" style="${d(0.5, 'width:95%')}"></div>
              <div class="v-line v-left" style="${d(0.7, 'width:88%')}"></div>
              <div class="v-line v-left" style="${d(0.9, 'width:70%')}"></div>
              <div class="v-in" style="${d(1.4, 'margin-top:16px;padding:10px;border-radius:10px;background:#273449;text-align:center;font-size:17px;font-weight:700')}">f′(a) = lim<sub>h→0</sub> (f(a+h) − f(a)) / h</div>
              <div class="v-line v-left" style="${d(1.9, 'width:92%')}"></div>
              <div class="v-line v-left" style="${d(2.1, 'width:60%')}"></div>
            </div>
            ${archie(80, 520, 240, 'v-pop', d(1))}`,
        },
        {
          cap: 'Geser slidernya, garis singgung y = x² ikut bergerak. Gradiennya f′(a) = 2a!',
          dur: 6000,
          html: () => graphHTML(),
          tick: (c, t) => setTangent(c, -1.6 + 3.2 * (0.5 - 0.5 * Math.cos((Math.PI * t) / 3000))),
        },
        {
          cap: 'Tekan 📌 Pin untuk menyimpan kondisi, lalu bandingkan dengan kondisi lain.',
          dur: 5000,
          html: () => graphHTML(`
            <line class="v-in" style="${d(0.6)}" x1="${GX(-0.3)}" y1="${GY(-1.6)}" x2="${GX(2.3)}" y2="${GY(3.6)}" stroke="#A78BFA" stroke-width="3" stroke-dasharray="7 5"/>
            <circle class="v-in" style="${d(0.6)}" cx="${GX(1)}" cy="${GY(1)}" r="6" fill="#A78BFA"/>`) + `
            <div class="v-pill v-pop" ${at(400, 30, d(0.7, 'font-size:12px;border-color:#A78BFA;color:#C4B5FD'))}>📌 Pin 1: a = 1 · f′ = 2</div>`,
          tick: (c, t) => setTangent(c, -1.7 + 1.3 * Math.min(t / 4000, 1)),
        },
      ],
    },

    papan: {
      title: 'Papan Coret-coret',
      scenes: [
        {
          cap: 'Setiap soal punya papan coret-coret. Bisa pakai mouse, jari, atau stylus.',
          dur: 4500,
          html: () => `
            <div class="v-board v-in"></div>
            <div class="v-tools v-in" style="${d(0.2)}">
              <span class="v-swatch on" style="--c:#1E1B16"></span><span class="v-swatch" style="--c:#2563EB"></span>
              <span class="v-swatch" style="--c:#DC2626"></span><span class="v-swatch" style="--c:#16A34A"></span>
              <span class="v-tool">✏️ Pena</span><span class="v-tool">🧽 Hapus</span><span class="v-tool">↶ Undo</span><span class="v-tool">▦ Petak</span>
            </div>
            ${write('∫ 2x dx', 130, 90, 0.6, 1400, 46)}
            ${write('= x² + C', 160, 175, 2.2, 1300, 46, '#2563EB')}`,
        },
        {
          cap: 'Ganti warna, lingkari jawaban, hapus, atau undo. Latarnya bisa polos, garis, atau petak.',
          dur: 4500,
          html: () => `
            <div class="v-board"></div>
            <div class="v-tools">
              <span class="v-swatch" style="--c:#1E1B16"></span><span class="v-swatch" style="--c:#2563EB"></span>
              <span class="v-swatch on v-pop" style="--c:#DC2626;${d(0.3)}"></span><span class="v-swatch" style="--c:#16A34A"></span>
              <span class="v-tool">✏️ Pena</span><span class="v-tool">🧽 Hapus</span><span class="v-tool">↶ Undo</span><span class="v-tool">▦ Petak</span>
            </div>
            ${write('∫ 2x dx', 130, 90, 0, 1, 46)}
            ${write('= x² + C', 160, 175, 0, 1, 46, '#2563EB')}
            <svg class="v-abs" ${at(0, 0, 'width:640px;height:360px')} viewBox="0 0 640 360">
              <ellipse class="v-draw" style="${d(0.7, '--len:620;--t:1.3s')}" cx="300" cy="205" rx="130" ry="46" fill="none" stroke="#DC2626" stroke-width="5" stroke-linecap="round"/>
              <path class="v-draw" style="${d(2.1, '--len:120;--t:.5s')}" d="M440 180 l40 -40 m-14 0 h14 v14" fill="none" stroke="#DC2626" stroke-width="5" stroke-linecap="round"/>
            </svg>
            ${write('jawab!', 470, 92, 2.6, 600, 30, '#DC2626')}`,
        },
        {
          cap: 'Pindah soal? Coretanmu tersimpan dan muncul lagi saat kamu kembali.',
          dur: 4500,
          html: () => `
            ${[['Soal 1', '∫ 2x dx = x² + C', 30, 0.2], ['Soal 2', 'lim sin x / x = 1', 340, 1.4]].map(([lbl, txt, l, s]) => `
              <div class="v-abs v-in" ${at(l, 40, d(s, 'font-weight:800;font-size:14px'))}>${lbl}</div>
              <div class="v-board v-in" ${at(l, 66, d(s, 'width:270px;height:190px'))}></div>
              ${write(txt, l + 16, 130, s + 0.4, 1000, 21)}
              <div class="v-pill v-pop" ${at(l + 40, 272, d(s + 1.6, 'font-size:12px;border-color:#22C55E;color:#4ADE80'))}>💾 tersimpan untuk ${lbl.toLowerCase()}</div>`).join('')}`,
        },
      ],
    },

    gamifikasi: {
      title: 'XP, Streak & Nyawa',
      scenes: [
        {
          cap: 'Setiap jawaban benar memberi XP. Belajar tiap hari untuk menjaga streak 🔥.',
          dur: 4500,
          html: () => `
            <div class="v-pill v-pop" ${at(90, 110, d(0.1, 'font-size:24px;padding:14px 22px;color:#93C5FD'))}>⚡ <span id="v-xpnum">0</span> XP</div>
            <div class="v-pill v-pop" ${at(330, 110, d(0.3, 'font-size:24px;padding:14px 22px;color:#FDBA74'))}>🔥
              <span style="position:relative;display:inline-block;width:18px"><span class="v-fade-out" style="${d(2.6, 'position:absolute')}">2</span><span class="v-pop" style="${d(2.8)}">3</span></span></div>
            <div class="v-pill v-pop" ${at(460, 110, d(0.5, 'font-size:24px;padding:14px 22px;color:#4ADE80'))}>💎 100</div>
            <div class="v-abs" ${at(90, 200, 'width:460px;height:14px;border-radius:7px;background:#334155;overflow:hidden')}>
              <div class="v-fill" style="${d(0.5, '--t:2s;width:75%;height:100%;background:linear-gradient(90deg,#3B82F6,#22C55E)')}"></div></div>
            <div class="v-sub" style="top:226px">Menuju level berikutnya</div>
            <div class="v-xp v-float-up" ${at(260, 70, d(1))}>+10 XP</div>
            <div class="v-xp v-float-up" ${at(190, 70, d(1.8))}>+10 XP</div>
            ${archie(70, 285, 260, 'v-pop mascot-celebrate', d(2.8))}`,
          tick: (c, t) => {
            const el = c.querySelector('#v-xpnum');
            if (el) el.textContent = Math.round(150 * Math.min(Math.max((t - 500) / 2000, 0), 1));
          },
        },
        {
          cap: 'Gagal lulus sesi mengurangi 1 nyawa. Nyawa penuh lagi 24 jam setelah nyawa pertama hilang.',
          dur: 4500,
          html: () => `
            ${title('Nyawa')}
            <div class="v-abs" ${at(110, 120, 'display:flex;gap:6px')}>
              ${Array.from({ length: 10 }, (_, i) => i < 9
                ? `<span class="v-heart v-pop" style="${d(0.1 + i * 0.06)}">❤️</span>`
                : `<span style="position:relative"><span class="v-heart v-break" style="${d(1.4)}"><span class="v-fade-out" style="${d(1.9)}">❤️</span></span><span class="v-heart v-pop" style="${d(2.1, 'position:absolute;left:0;top:0')}">🤍</span></span>`).join('')}
            </div>
            <div class="v-pill" ${at(270, 180, 'font-size:18px;color:#FCA5A5')}>
              <span style="position:relative;display:inline-block;width:48px"><span class="v-fade-out" style="${d(1.9, 'position:absolute')}">10/10</span><span class="v-pop" style="${d(2.1)}">9/10</span></span></div>
            <div class="v-pill v-in" ${at(150, 250, d(2.6, 'font-size:13px;color:#CBD5E1'))}>⏳ Penuh lagi 24 jam setelah nyawa pertama hilang</div>`,
        },
        {
          cap: 'Kumpulkan XP dan naik di papan peringkat!',
          dur: 5000,
          html: () => {
            const row = (rank, name, xp, color, top, cls = '', more = '') =>
              `<div class="v-rank ${cls}" ${at(150, top, more)}><b style="width:16px">${rank}</b><span class="av" style="background:${color}">${name[0]}</span><span>${name}</span><span>${xp} XP</span></div>`;
            return `
              ${title('Papan Peringkat')}
              ${row(1, 'Andi', '1.840', '#D97706', 80, 'v-in')}
              ${row(3, 'Sari', '1.620', '#6B7280', 180, 'v-move', d(1.6, '--fy:-50px;--t:.7s'))}
              ${row(4, 'Rizky', '1.380', '#B45309', 230, 'v-move', d(1.6, '--fy:-50px;--t:.7s'))}
              ${row(2, 'Kamu', '1.700', '#3B82F6', 130, 'me v-move', d(1.6, '--fy:150px;--t:.7s;z-index:2'))}
              <div class="v-xp v-float-up" ${at(500, 120, d(1.5))}>+400 XP</div>
              ${archie(70, 540, 270, 'v-pop mascot-celebrate', d(2.4))}`;
          },
        },
      ],
    },

    diagnostik: {
      title: 'Jalur Fakultas & Tes Awal',
      scenes: [
        {
          cap: 'Pilih jalurmu: Fasilkom, FMIPA, atau Fakultas Teknik. Materinya ikut menyesuaikan.',
          dur: 4500,
          html: () => `
            ${title('Pilih jalurmu')}
            <div class="v-fac on v-pop v-turn-sel" ${at(50, 110, d(0.2, 'animation-name:vPop,vTurnSel;animation-delay:.2s,2.4s;animation-duration:.45s,.3s'))}><i>💻</i>Fasilkom<small>Gradient descent, AI math</small></div>
            <div class="v-fac v-pop" ${at(240, 110, d(0.4))}><i>🔬</i>FMIPA<small>Pembuktian ε-δ, analisis</small></div>
            <div class="v-fac v-pop" ${at(430, 110, d(0.6))}><i>⚙️</i>Fak. Teknik<small>Laju terkait, optimasi</small></div>
            ${cursor(150, 215, 'v-move', d(1.2, '--fx:300px;--fy:100px;--t:1s'))}`,
        },
        {
          cap: 'Ikuti tes awal 10 soal (opsional) untuk mengukur kemampuanmu.',
          dur: 5000,
          html: () => {
            const res = [1, 1, 1, 0, 1, 1, 0, 1, 1, 1];
            return `
              ${title('Tes kemampuan awal')}
              <div class="v-card v-in" ${at(120, 90, 'width:400px;height:200px;padding:22px;')}>
                <div style="font-weight:700;color:#94A3B8;font-size:13px">Soal <span id="v-qn">1</span> dari 10</div>
                <div style="margin-top:10px;height:10px;border-radius:5px;background:#334155;overflow:hidden">
                  <div class="v-fill" style="${d(0.3, '--t:3.2s;width:100%;height:100%;background:linear-gradient(90deg,#3B82F6,#22C55E)')}"></div></div>
                <div style="display:flex;gap:10px;margin-top:26px;justify-content:center">
                  ${res.map((ok, i) => `<span class="v-pop" style="${d(0.5 + i * 0.3, `width:24px;height:24px;border-radius:50%;background:${ok ? '#22C55E' : '#F87171'}`)}"></span>`).join('')}
                </div>
                <div style="margin-top:22px;text-align:center;font-size:13px;color:#94A3B8">5 mudah · 3 sedang · 2 sulit</div>
              </div>`;
          },
          tick: (c, t) => {
            const el = c.querySelector('#v-qn');
            if (el) el.textContent = Math.min(10, 1 + Math.floor(Math.max(t - 500, 0) / 300));
          },
        },
        {
          cap: 'Hasilnya langsung keluar, lengkap dengan rekomendasi titik mulai.',
          dur: 4500,
          html: () => `
            <div class="v-card v-in" ${at(110, 30, 'width:420px;height:300px;padding:22px;')}>
              <div style="display:flex;align-items:center;gap:16px">
                <div style="font:800 46px var(--font-head)">8<small style="font-size:22px;color:#94A3B8">/10</small></div>
                <div style="color:#94A3B8;font-weight:600">jawaban benar</div>
              </div>
              <div class="v-in" style="${d(0.6, 'margin-top:12px;padding:12px 14px;border-radius:12px;background:rgba(34,197,94,.14);border:1px solid #22C55E')}">
                <b>Siap belajar!</b><div style="font-size:13px;color:#CBD5E1;margin-top:4px">Titik mulaimu: <b style="color:#4ADE80">Kalkulus Dasar</b></div></div>
              ${[['PreCalculus', '5/5', 'lulus'], ['Kalkulus Dasar', '2/3', 'lulus'], ['Lanjutan', '1/2', 'perlu latihan']].map(([a, b, c], i) => `
                <div class="v-in" style="${d(1.2 + i * 0.3, 'display:flex;justify-content:space-between;margin-top:10px;padding:8px 12px;border-radius:10px;background:#273449;font-size:13px')}"><span>${a}</span><b>${b}</b><em style="font-style:normal;color:${c === 'lulus' ? '#4ADE80' : '#FBBF24'}">${c}</em></div>`).join('')}
            </div>
            ${archie(90, 530, 230, 'v-pop mascot-celebrate', d(0.4))}`,
        },
      ],
    },

    outro: {
      title: 'Siap menyeberang?',
      scenes: [{
        cap: 'Siap menyeberang? Coba 5 soal di halaman ini atau daftar untuk menyimpan progresmu.',
        dur: 5000,
        html: () => `
          ${archie(140, 250, 40, 'v-pop mascot-celebrate')}
          <div class="v-title v-in" style="top:200px;${d(0.4)}">Siap menyeberang?</div>
          <div class="v-pill v-pop" ${at(170, 262, d(0.9, 'background:#F97316;border-color:#F97316;font-size:16px'))}>🎯 Coba 5 soal</div>
          <div class="v-pill v-pop" ${at(360, 262, d(1.2, 'background:#3B82F6;border-color:#3B82F6;font-size:16px'))}>📝 Daftar</div>`,
      }],
    },
  };

  const TOUR = ['peta', 'latihan', 'grafik', 'papan', 'gamifikasi', 'diagnostik'];

  // ── Pemutar ──────────────────────────────────────────────────────────────────
  const $ = (id) => document.getElementById(id);
  let root, canvas, list = [], idx = 0, t = 0, playing = false, last = 0, raf = 0, opener = null, isTour = false;

  const total = () => list.reduce((s, sc) => s + sc.dur, 0);
  const elapsed = () => list.slice(0, idx).reduce((s, sc) => s + sc.dur, 0) + t;
  const clock = (ms) => { const s = Math.floor(ms / 1000); return `${Math.floor(s / 60)}:${String(s % 60).padStart(2, '0')}`; };

  /** Lama satu bab (ms) — dipakai homepage untuk label "▶ Tonton 14 dtk". */
  const chapterLength = (id) => CHAPTERS[id].scenes.reduce((s, sc) => s + sc.dur, 0);

  function fit() {
    const w = $('vp-screen').clientWidth;
    if (w) canvas.style.setProperty('--s', (w / W).toFixed(4));
  }

  function buildTrack() {
    $('vp-track').innerHTML = list.map((sc, i) =>
      `<button type="button" class="vp-seg" style="--w:${sc.dur}" data-i="${i}" aria-label="Adegan ${i + 1}: ${sc.chapterTitle}"><i></i></button>`).join('');
    const chapters = $('vp-chapters');
    chapters.hidden = !isTour;
    if (isTour) {
      chapters.innerHTML = ['intro', ...TOUR, 'outro'].map((id) =>
        `<button type="button" data-ch="${id}">${CHAPTERS[id].title}</button>`).join('');
    }
  }

  function paintProgress() {
    $('vp-track').querySelectorAll('.vp-seg').forEach((seg, i) =>
      seg.style.setProperty('--f', i < idx ? 1 : i > idx ? 0 : Math.min(t / list[i].dur, 1)));
    $('vp-time').textContent = `${clock(elapsed())} / ${clock(total())}`;
  }

  function go(i) {
    idx = Math.max(0, Math.min(list.length - 1, i));
    t = 0;
    const sc = list[idx];
    canvas.innerHTML = sc.html();
    sc.tick?.(canvas, 0);
    $('vp-cap').textContent = sc.cap;
    $('vp-end').hidden = true;
    $('vp-chapters').querySelectorAll('button').forEach((b) => b.classList.toggle('active', b.dataset.ch === sc.chapter));
    paintProgress();
  }

  function setPlaying(on) {
    playing = on;
    root.classList.toggle('is-paused', !on);
    $('vp-play').textContent = on ? '⏸' : '▶';
    $('vp-play').setAttribute('aria-label', on ? 'Jeda' : 'Putar');
    cancelAnimationFrame(raf);
    if (on) { last = performance.now(); raf = requestAnimationFrame(frame); }
  }

  function frame(now) {
    if (!playing) return;
    t += now - last;
    last = now;
    const sc = list[idx];
    if (t >= sc.dur) {
      if (idx < list.length - 1) go(idx + 1);
      else { t = sc.dur; paintProgress(); finish(); return; }
    } else {
      sc.tick?.(canvas, t);
      paintProgress();
    }
    raf = requestAnimationFrame(frame);
  }

  function finish() {
    setPlaying(false);
    $('vp-end').hidden = false;
  }

  function toggle() {
    if (!$('vp-end').hidden) { go(0); setPlaying(true); return; }
    setPlaying(!playing);
  }

  function open(id, from) {
    if (!CHAPTERS[id] && id !== 'tour') return;
    isTour = id === 'tour';
    const ids = isTour ? ['intro', ...TOUR, 'outro'] : [id];
    list = ids.flatMap((ch) => CHAPTERS[ch].scenes.map((sc) => ({ ...sc, chapter: ch, chapterTitle: CHAPTERS[ch].title })));
    $('vp-title').textContent = isTour ? 'Pengenalan Calculus Bridge' : CHAPTERS[id].title;
    opener = from || document.activeElement;
    buildTrack();
    root.hidden = false;
    document.body.style.overflow = 'hidden';
    fit();
    go(0);
    setPlaying(true);
    root.querySelector('.vp-x').focus();
  }

  function close() {
    if (root.hidden) return;
    setPlaying(false);
    root.hidden = true;
    canvas.innerHTML = '';
    document.body.style.overflow = '';
    opener?.focus?.();
  }

  function init() {
    root = $('vp');
    if (!root) return;
    canvas = $('vp-canvas');

    root.addEventListener('click', (e) => {
      if (e.target.closest('[data-vp-close]')) { close(); return; }
      const seg = e.target.closest('.vp-seg');
      if (seg) { go(+seg.dataset.i); if (!playing) setPlaying(true); return; }
      const ch = e.target.closest('[data-ch]');
      if (ch) { go(list.findIndex((sc) => sc.chapter === ch.dataset.ch)); if (!playing) setPlaying(true); return; }
      if (e.target.closest('#vp-screen') && !e.target.closest('#vp-end')) toggle();
    });
    $('vp-play').addEventListener('click', toggle);
    $('vp-prev').addEventListener('click', () => go(idx - 1));
    $('vp-next').addEventListener('click', () => go(idx + 1));
    $('vp-replay').addEventListener('click', (e) => { e.stopPropagation(); go(0); setPlaying(true); });

    document.addEventListener('keydown', (e) => {
      if (root.hidden) return;
      if (e.key === 'Escape') close();
      else if (e.key === ' ' && !e.target.closest('button, a')) { e.preventDefault(); toggle(); }
      else if (e.key === 'ArrowRight') go(idx + 1);
      else if (e.key === 'ArrowLeft') go(idx - 1);
      else if (e.key === 'Tab') {   // fokus tetap di dalam dialog
        const items = [...root.querySelectorAll('button:not([hidden]), a[href]')].filter((el) => el.offsetParent);
        const first = items[0], lastEl = items[items.length - 1];
        if (e.shiftKey && document.activeElement === first) { e.preventDefault(); lastEl.focus(); }
        else if (!e.shiftKey && document.activeElement === lastEl) { e.preventDefault(); first.focus(); }
      }
    });
    document.addEventListener('visibilitychange', () => { if (document.hidden && !root.hidden) setPlaying(false); });
    new ResizeObserver(fit).observe($('vp-screen'));
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();

  return { open, close, chapterLength };
})();
