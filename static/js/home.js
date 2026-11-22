/**
 * Calculus Bridge — Interaksi homepage publik (templates/home/homepage.html).
 *
 *  - Navigasi   : garis bawah saat halaman digulir.
 *  - Ikon       : ic() memakai sprite garis homepage (#hl-*), bukan Icon() berwarna milik aplikasi.
 *  - Archie hero: pembuka (kurva tergambar, Archie berjalan ke puncak), mata mengikuti kursor,
 *                 berkedip, klik → lompat + tips, menyapa sendiri, bereaksi pada tombol hero.
 *  - Zoom       : komponen membesar sedikit saat disorot dan muncul dengan zoom-in saat digulir.
 *  - Video      : tombol [data-video] membuka HomeVideo (home_video.js); label durasi dihitung
 *                 dari adegannya sehingga selalu cocok.
 *  - TrialQuiz  : kuis coba 5 soal dari GET /api/coba-soal/ (tanpa login). Penilaian di
 *                 browser, hasil tidak disimpan. Pembahasan + grafik GraphLab bisa dibuka.
 */
(() => {
  'use strict';

  const $ = (sel, root = document) => root.querySelector(sel);
  const ic = (name) => `<svg class="ic" aria-hidden="true"><use href="#hl-${name}"/></svg>`;
  const esc = (t) => String(t).replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));

  // ── Navigasi ────────────────────────────────────────────────────────────────
  function initNav() {
    const nav = $('#hp-nav');
    const onScroll = () => nav.classList.toggle('is-scrolled', window.scrollY > 8);
    window.addEventListener('scroll', onScroll, { passive: true });
    onScroll();
  }

  // ── Archie di hero ──────────────────────────────────────────────────────────
  const TIPS = [
    'Turunan itu laju perubahan, kayak speedometer motormu.',
    '∫ artinya ngejumlahin potongan-potongan yang super kecil.',
    'Di puncak bukit, garis singgungnya datar: f′(x) = 0.',
    'lim<sub>x→0</sub> sin x / x = 1. Coba buktiin di grafik.',
    'Mau nyoba? Ada 5 soal di bawah, gak perlu daftar.',
    'Klik <b>Tonton pengenalan</b> buat tur singkat bareng aku.',
  ];

  const HOVER_SAY = {
    tour: 'Videonya cuma sebentar, yuk tonton bareng',
    coba: '5 soal aja, gak perlu daftar',
  };
  const reduceMotion = () => window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  function initHero() {
    const btn = $('#hero-archie');
    const bubble = $('#hero-bubble');
    const art = $('.hp-hero-art');
    const curve = $('#hero-curve');
    if (!btn || !bubble || !art || !curve) return;

    let i = 0;
    let lastTouch = 0;     // terakhir pengunjung berinteraksi dengan Archie
    let autoCount = 0;

    const say = (html, hop = true) => {
      bubble.innerHTML = html;
      bubble.classList.remove('is-new');
      void bubble.offsetWidth;   // mulai ulang animasi
      bubble.classList.add('is-new');
      if (hop) {
        btn.classList.remove('is-bounce');
        void btn.offsetWidth;
        btn.classList.add('is-bounce');
      }
    };
    btn.addEventListener('animationend', (e) => { if (e.animationName === 'hpBounce') btn.classList.remove('is-bounce'); });
    btn.addEventListener('click', () => { lastTouch = Date.now(); say(TIPS[i++ % TIPS.length]); });

    // Bereaksi saat tombol hero disorot
    document.querySelectorAll('.hp-cta [data-video="tour"], .hp-cta-alt').forEach((el) => {
      const key = el.matches('.hp-cta-alt') ? 'coba' : 'tour';
      el.addEventListener('mouseenter', () => { lastTouch = Date.now(); say(HOVER_SAY[key], false); });
    });

    // Mata mengikuti kursor + berkedip
    const svg = btn.querySelector('svg');
    const eyes = [...svg.querySelectorAll('ellipse[cx="74"], circle[cx="71"], ellipse[cx="126"], circle[cx="123"]')];
    eyes.forEach((el) => el.classList.add('hp-eye'));
    let look = { x: 0, y: 0 }, blink = 1, raf = 0;
    const paintEyes = () => { raf = 0; eyes.forEach((el) => { el.style.transform = `translate(${look.x}px, ${look.y}px) scaleY(${blink})`; }); };
    const queue = () => { if (!raf) raf = requestAnimationFrame(paintEyes); };
    const scene = art.querySelector('.hp-bridge');
    window.addEventListener('pointermove', (e) => {
      const a = art.getBoundingClientRect();   // parallax simbol: -1..1 relatif ke tengah adegan
      art.style.setProperty('--mx', Math.max(-1, Math.min(1, (e.clientX - a.left - a.width / 2) / a.width)).toFixed(3));
      art.style.setProperty('--my', Math.max(-1, Math.min(1, (e.clientY - a.top - a.height / 2) / a.height)).toFixed(3));
      const r = svg.getBoundingClientRect();
      const dx = e.clientX - (r.left + r.width / 2), dy = e.clientY - (r.top + r.height * .5);
      const d = Math.hypot(dx, dy) || 1, k = Math.min(1, d / 240);
      look = { x: (dx / d) * 4 * k, y: (dy / d) * 3 * k };
      queue();
    }, { passive: true });
    const blinkLoop = () => {
      setTimeout(() => {
        blink = .1; queue();
        setTimeout(() => { blink = 1; queue(); blinkLoop(); }, 130);
      }, 2500 + Math.random() * 3000);
    };
    blinkLoop();

    // Menyapa sendiri selama hero terlihat dan pengunjung belum mengajaknya bicara
    let visible = true;
    new IntersectionObserver(([en]) => { visible = en.isIntersecting; }).observe(art);
    setInterval(() => {
      if (!visible || document.hidden || autoCount >= 4 || Date.now() - lastTouch < 15000) return;
      autoCount++;
      say(TIPS[i++ % TIPS.length]);
    }, 10000);

    // Pembuka: kurva jembatan tergambar sekali, Archie berjalan di ujung penanya sampai puncak.
    // Kapsul rumus (SMIL) dijeda sampai pembuka selesai; tetap dijeda (tersembunyi) jika gerak dikurangi.
    scene.pauseAnimations();
    if (reduceMotion()) return;
    const L = curve.getTotalLength();
    const place = (len) => {
      const p = curve.getPointAtLength(len);
      btn.style.left = `${(p.x / 520) * 100}%`;
      btn.style.bottom = `${((400 - p.y) / 400) * 100 - 7}%`;
    };
    curve.style.strokeDasharray = `${L}`;
    curve.style.strokeDashoffset = `${L}`;
    art.classList.add('is-intro');
    place(0);
    const WALK = 1700, REST = 700, DELAY = 400;
    const ease = (t) => t < .5 ? 2 * t * t : 1 - ((-2 * t + 2) ** 2) / 2;
    let t0 = 0;
    const step = (now) => {
      if (!t0) t0 = now;
      const ms = now - t0 - DELAY;
      if (ms < 0) { requestAnimationFrame(step); return; }
      btn.classList.add('is-walking');
      let drawn;
      if (ms < WALK) {
        drawn = ease(ms / WALK) * (L / 2);
        place(drawn);
      } else {
        btn.classList.remove('is-walking');
        place(L / 2);
        drawn = L / 2 + Math.min(1, (ms - WALK) / REST) * (L / 2);
      }
      curve.style.strokeDashoffset = `${L - drawn}`;
      if (ms < WALK + REST) { requestAnimationFrame(step); return; }
      curve.style.strokeDasharray = curve.style.strokeDashoffset = '';
      btn.style.left = btn.style.bottom = '';
      art.classList.remove('is-intro');
      scene.setCurrentTime(0);
      scene.unpauseAnimations();
      say('Halo, aku <b>Archie</b>. Klik aku buat tips kalkulus');
    };
    requestAnimationFrame(step);
  }

  // ── Tombol video ────────────────────────────────────────────────────────────
  function initVideos() {
    document.querySelectorAll('[data-video]').forEach((btn) => {
      const small = btn.querySelector('small');
      if (small && btn.dataset.video !== 'tour') small.textContent = `${Math.round(HomeVideo.chapterLength(btn.dataset.video) / 1000)} dtk`;
      btn.addEventListener('click', () => HomeVideo.open(btn.dataset.video, btn));
    });
  }

  // ── Kuis coba 5 soal ────────────────────────────────────────────────────────
  const TrialQuiz = (() => {
    let root, questions = [], idx = 0, results = [];

    const coach = (text, mood) => {
      const say = $('#coach-say'), box = $('#coach-archie');
      if (!say || !box) return;
      say.innerHTML = text;
      say.classList.remove('is-new'); box.classList.remove('is-happy', 'is-sad');
      void say.offsetWidth;
      say.classList.add('is-new');
      if (mood) box.classList.add(mood);
    };

    function intro() {
      root.innerHTML = `
        <div class="tq-intro">
          <div class="tq-big">${ic('target')}</div>
          <h3>Tes dirimu pakai 5 soal</h3>
          <p>Soal acak lengkap sama pembahasannya. Gak ada heart yang hilang, tenang aja.</p>
          <ul class="tq-plan">
            <li><b>3</b> Kalkulus Dasar</li><li><b>2</b> Kalkulus Tingkat Menengah</li><li>Mudah–Sedang</li>
          </ul>
          <button type="button" class="btn btn-primary btn-lg" data-tq="start">Mulai coba</button>
        </div>`;
    }

    async function start() {
      root.innerHTML = '<div class="tq-loading"><div><div class="tq-spin"></div>Archie lagi nyiapin soal…</div></div>';
      coach('Semangat. Baca soalnya pelan-pelan, ya');
      try {
        const res = await fetch(root.dataset.api, { headers: { Accept: 'application/json' } });
        const data = await res.json();
        if (!res.ok || !data.questions?.length) throw new Error(data.message || `HTTP ${res.status}`);
        questions = data.questions;
      } catch (err) {
        root.innerHTML = `
          <div class="tq-intro">
            <div class="tq-big">${ic('warning')}</div>
            <h3>Soal gagal dimuat</h3>
            <p>${esc(err.message)}. Coba lagi bentar, ya.</p>
            <button type="button" class="btn btn-primary" data-tq="start">Coba lagi</button>
          </div>`;
        return;
      }
      idx = 0;
      results = [];
      render();
    }

    function render() {
      const q = questions[idx];
      root.innerHTML = `
        <div class="tq-card">
          <div class="quiz-progress-bar"><div class="quiz-progress-fill" style="width:${(idx / questions.length) * 100}%"></div></div>
          <div class="quiz-meta">
            <span class="quiz-num">Soal ${idx + 1} dari ${questions.length} · ${esc(q.level)}</span>
            <span class="quiz-diff-badge diff-${q.difficulty}">${esc(q.difficulty_label)}</span>
          </div>
          <p class="tq-meta-topic">${ic('book')} ${esc(q.topic)}</p>
          <div class="quiz-prompt">${q.prompt}</div>
          <div class="options-list">
            ${q.options.map((o, i) => `
              <button type="button" class="option-btn" data-opt="${i}">
                <span class="opt-letter">${'ABCD'[i]}</span><span>${o.text}</span>
              </button>`).join('')}
          </div>
          <div id="tq-after"></div>
        </div>`;
      root.querySelector('.option-btn')?.focus({ preventScroll: true });
    }

    function answer(i) {
      const q = questions[idx];
      const ok = q.options[i].is_correct;
      results.push(ok);
      root.querySelectorAll('.option-btn').forEach((b, j) => {
        b.disabled = true;
        if (q.options[j].is_correct) b.classList.add('correct');
        else if (j === i) b.classList.add('incorrect');
      });
      const last = idx === questions.length - 1;
      $('#tq-after', root).innerHTML = `
        <div class="tq-feedback ${ok ? 'ok' : 'bad'}">
          ${ok ? 'Benar' : 'Belum tepat'} <span>· Jawaban: ${q.answer}</span>
        </div>
        <div class="tq-actions">
          <button type="button" class="btn btn-outline btn-sm" data-tq="explain">${ic('book')} Lihat pembahasan</button>
          <button type="button" class="btn btn-primary" data-tq="next">${last ? 'Lihat hasil' : 'Lanjut'}</button>
        </div>
        <div id="tq-explain"></div>`;
      coach(ok ? ['Mantap', 'Tepat banget', 'Keren, lanjut'][idx % 3]
               : 'Gapapa, cek pembahasannya, ya', ok ? 'is-happy' : 'is-sad');
      $('[data-tq="next"]', root).focus({ preventScroll: true });
    }

    function explain(btn) {
      const q = questions[idx];
      const box = $('#tq-explain', root);
      if (box.childElementCount) { box.innerHTML = ''; btn.innerHTML = `${ic('book')} Lihat pembahasan`; return; }
      btn.innerHTML = `${ic('book')} Tutup pembahasan`;
      box.innerHTML = `
        <div class="pembahasan">
          <h5>${ic('book')} Pembahasan</h5>
          <ol class="steps-list">${(q.steps || []).map((s) => `<li>${s}</li>`).join('')}</ol>
          <div class="answer-box"><strong>Jawaban:</strong> ${q.answer || ''}</div>
          ${q.explanation ? `<p class="expl-note">${ic('chat')} ${q.explanation}</p>` : ''}
          ${(q.graphs || []).length ? `<p class="graph-hint">${ic('sliders')} Geser slider buat ngubah-ngubah grafiknya.</p><div class="tq-graphs"></div>` : ''}
        </div>`;
      const g = $('.tq-graphs', box);
      if (g && window.GraphLab) GraphLab.mountList(g, q.graphs);
    }

    function next() {
      idx += 1;
      if (idx < questions.length) { render(); root.scrollIntoView({ block: 'nearest', behavior: 'smooth' }); return; }
      end();
    }

    function end() {
      const score = results.filter(Boolean).length;
      const msg = score === 5 ? ['Sempurna', 'Kamu siap melompat ke level yang lebih tinggi.']
        : score >= 3 ? ['Keren banget', 'Fondasimu udah kuat, tinggal diasah lagi.']
        : score >= 1 ? ['Awal yang bagus', 'Skill tree bakal nuntun kamu step-by-step.']
        : ['Jangan nyerah', 'Mulai dari PreCalculus dulu, Archie temenin.'];
      root.innerHTML = `
        <div class="tq-end tq-intro">
          <div class="tq-score" style="--p:${score * 20}"><b>${score}/5</b></div>
          <div class="tq-dots">${results.map((ok) => `<i class="${ok ? 'ok' : ''}"></i>`).join('')}</div>
          <h3>${msg[0]}</h3>
          <p>${msg[1]} Daftar buat nyimpen progres, ngumpulin XP, dan buka semua level.</p>
          <div class="tq-cta">
            <a class="btn btn-primary btn-lg" href="${root.dataset.signup}">Daftar &amp; simpan progres</a>
            <button type="button" class="btn btn-outline btn-lg" data-tq="start">Coba soal baru</button>
          </div>
        </div>`;
      coach(score >= 3 ? `${score} dari 5. Aku bangga sama kamu` : 'Yuk belajar bareng aku, pasti bisa', score >= 3 ? 'is-happy' : null);
    }

    function init() {
      root = $('#trial-root');
      if (!root) return;
      root.addEventListener('click', (e) => {
        const opt = e.target.closest('[data-opt]');
        if (opt && !opt.disabled) { answer(+opt.dataset.opt); return; }
        const act = e.target.closest('[data-tq]');
        if (!act) return;
        if (act.dataset.tq === 'start') start();
        else if (act.dataset.tq === 'next') next();
        else if (act.dataset.tq === 'explain') explain(act);
      });
      intro();
    }

    return { init };
  })();

  // ── Zoom kecil: komponen membesar saat disorot, muncul dengan zoom-in saat digulir ──
  const ZOOM = '.hp-eyebrow, .hp-stats li, .hp-bubble, .hp-feature, .hp-try-card, .hp-coach, .hp-steps li, .hp-faq details, .hp-final';
  const REVEAL = '.hp-hero-copy > *, .hp-head, .hp-feature, .hp-try-side, .hp-try-card, .hp-steps li, .hp-faq details, .hp-final';
  function initZoom() {
    document.querySelectorAll(ZOOM).forEach((el) => el.classList.add('hp-zoom'));
    if (reduceMotion() || !('IntersectionObserver' in window)) return;
    const els = [...document.querySelectorAll(REVEAL)];
    // Urutan kemunculan bertahap di dalam satu kelompok (saudara kandung)
    els.forEach((el) => {
      const sibs = [...el.parentElement.children].filter((c) => els.includes(c));
      el.style.setProperty('--i', String(Math.min(sibs.indexOf(el), 6)));
      el.classList.add('rv');
    });
    const io = new IntersectionObserver((entries) => entries.forEach((en) => {
      if (!en.isIntersecting) return;
      const el = en.target;
      io.unobserve(el);
      el.classList.add('is-in');
      // Setelah muncul, lepas kelas reveal agar transisi hover (.hp-zoom) kembali normal
      setTimeout(() => el.classList.remove('rv', 'is-in'), 700 + Number(el.style.getPropertyValue('--i')) * 70);
    }), { threshold: .12, rootMargin: '0px 0px -40px 0px' });
    els.forEach((el) => io.observe(el));
  }

  function init() {
    initNav();
    initZoom();
    initHero();
    initVideos();
    TrialQuiz.init();
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
})();
