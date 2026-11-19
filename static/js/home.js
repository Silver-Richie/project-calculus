/**
 * Calculus Bridge — Interaksi homepage publik (templates/home/homepage.html).
 *
 *  - Navigasi   : bayangan saat halaman digulir; elemen [data-reveal] muncul saat terlihat.
 *  - Archie hero: klik → melompat + tips kalkulus bergantian di gelembung.
 *  - Video      : tombol [data-video] membuka HomeVideo (home_video.js); label durasi dihitung
 *                 dari adegannya sehingga selalu cocok.
 *  - TrialQuiz  : kuis coba 5 soal dari GET /api/coba-soal/ (tanpa login). Penilaian di
 *                 browser, hasil tidak disimpan. Pembahasan + grafik GraphLab bisa dibuka.
 */
(() => {
  'use strict';

  const $ = (sel, root = document) => root.querySelector(sel);
  const esc = (t) => String(t).replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));

  // ── Navigasi & muncul saat digulir ──────────────────────────────────────────
  function initNav() {
    const nav = $('#hp-nav');
    const onScroll = () => nav.classList.toggle('is-scrolled', window.scrollY > 8);
    window.addEventListener('scroll', onScroll, { passive: true });
    onScroll();

    const targets = document.querySelectorAll('.hp-feature, .hp-steps li, .hp-faq details, .hp-head, .hp-final');
    if (!('IntersectionObserver' in window)) return;
    const io = new IntersectionObserver((entries) => entries.forEach((en) => {
      if (en.isIntersecting) { en.target.classList.add('is-in'); io.unobserve(en.target); }
    }), { rootMargin: '0px 0px -8% 0px' });
    targets.forEach((el, i) => {
      el.setAttribute('data-reveal', '');
      el.style.transitionDelay = `${(i % 3) * 80}ms`;
      io.observe(el);
    });
  }

  // ── Archie di hero ──────────────────────────────────────────────────────────
  const TIPS = [
    'Turunan itu laju perubahan, kayak speedometer motormu!',
    '∫ artinya ngejumlahin potongan-potongan yang super kecil.',
    'Di puncak bukit, garis singgungnya datar: f′(x) = 0.',
    'lim<sub>x→0</sub> sin x / x = 1. Coba buktikan di grafik!',
    'Mau nyoba? Ada 5 soal di bawah, gak perlu daftar.',
    'Klik ▶ <b>Tonton pengenalan</b> buat tur singkat bareng aku.',
  ];

  function initHero() {
    const btn = $('#hero-archie');
    const bubble = $('#hero-bubble');
    if (!btn || !bubble) return;
    let i = 0;
    btn.addEventListener('click', () => {
      bubble.innerHTML = TIPS[i++ % TIPS.length];
      bubble.classList.remove('is-new');
      btn.classList.remove('is-bounce');
      void btn.offsetWidth;   // mulai ulang animasi
      bubble.classList.add('is-new');
      btn.classList.add('is-bounce');
    });
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
          <div class="tq-big">${Icon('target')}</div>
          <h3>Tes dirimu pakai 5 soal</h3>
          <p>Soal acak lengkap sama pembahasannya. Gak ada heart yang hilang, tenang aja!</p>
          <ul class="tq-plan">
            <li>${Icon('lv-kalkulus-dasar')} 3 × Kalkulus Dasar</li><li>${Icon('lv-kalkulus-menengah')} 2 × Kalkulus Tingkat Menengah</li><li>${Icon('sprout')} Mudah–Sedang</li>
          </ul>
          <button type="button" class="btn btn-accent btn-lg" data-tq="start">Mulai coba ➔</button>
        </div>`;
    }

    async function start() {
      root.innerHTML = '<div class="tq-loading"><div><div class="tq-spin"></div>Archie lagi nyiapin soal…</div></div>';
      coach('Semangat! Baca soalnya pelan-pelan, ya.');
      try {
        const res = await fetch(root.dataset.api, { headers: { Accept: 'application/json' } });
        const data = await res.json();
        if (!res.ok || !data.questions?.length) throw new Error(data.message || `HTTP ${res.status}`);
        questions = data.questions;
      } catch (err) {
        root.innerHTML = `
          <div class="tq-intro">
            <div class="tq-big">${Icon('warning')}</div>
            <h3>Soal gagal dimuat</h3>
            <p>${esc(err.message)}. Coba lagi bentar, ya.</p>
            <button type="button" class="btn btn-primary" data-tq="start">↺ Coba lagi</button>
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
          <p class="tq-meta-topic">${Icon('book')} ${esc(q.topic)}</p>
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
          ${ok ? '✓ Benar!' : '✗ Belum tepat.'} <span>Jawaban: ${q.answer}</span>
        </div>
        <div class="tq-actions">
          <button type="button" class="btn btn-outline btn-sm" data-tq="explain">${Icon('book')} Lihat pembahasan</button>
          <button type="button" class="btn btn-primary" data-tq="next">${last ? `Lihat hasil ${Icon('flag')}` : 'Lanjut ➔'}</button>
        </div>
        <div id="tq-explain"></div>`;
      coach(ok ? ['Mantap!', 'Tepat banget!', 'Keren, lanjut!'][idx % 3]
               : 'Gapapa, cek pembahasannya, ya.', ok ? 'is-happy' : 'is-sad');
      $('[data-tq="next"]', root).focus({ preventScroll: true });
    }

    function explain(btn) {
      const q = questions[idx];
      const box = $('#tq-explain', root);
      if (box.childElementCount) { box.innerHTML = ''; btn.innerHTML = `${Icon('book')} Lihat pembahasan`; return; }
      btn.innerHTML = `${Icon('book')} Tutup pembahasan`;
      box.innerHTML = `
        <div class="pembahasan">
          <h5>${Icon('book')} Pembahasan</h5>
          <ol class="steps-list">${(q.steps || []).map((s) => `<li>${s}</li>`).join('')}</ol>
          <div class="answer-box"><strong>Jawaban:</strong> ${q.answer || ''}</div>
          ${q.explanation ? `<p class="expl-note">${Icon('chat')} ${q.explanation}</p>` : ''}
          ${(q.graphs || []).length ? `<p class="graph-hint">${Icon('sliders')} Geser slider buat ngubah-ngubah grafiknya.</p><div class="tq-graphs"></div>` : ''}
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
      const msg = score === 5 ? ['Sempurna!', 'Kamu siap melompat ke level yang lebih tinggi.']
        : score >= 3 ? ['Keren banget!', 'Fondasimu udah kuat, tinggal diasah lagi.']
        : score >= 1 ? ['Awal yang bagus!', 'Skill tree bakal nuntun kamu step-by-step.']
        : ['Jangan nyerah!', 'Mulai dari PreCalculus dulu, Archie temenin.'];
      root.innerHTML = `
        <div class="tq-end tq-intro">
          <div class="tq-score" style="--p:${score * 20}"><b>${score}/5</b></div>
          <div class="tq-dots">${results.map((ok) => `<i class="${ok ? 'ok' : ''}"></i>`).join('')}</div>
          <h3>${msg[0]}</h3>
          <p>${msg[1]} Daftar buat nyimpen progres, ngumpulin XP, dan buka semua level.</p>
          <div class="tq-cta">
            <a class="btn btn-growth btn-lg" href="${root.dataset.signup}">Daftar &amp; simpan progres ➔</a>
            <button type="button" class="btn btn-outline" data-tq="start">↺ Coba soal baru</button>
          </div>
        </div>`;
      coach(score >= 3 ? `${score} dari 5! Aku bangga sama kamu!` : 'Yuk belajar bareng aku, pasti bisa!', score >= 3 ? 'is-happy' : null);
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

  function init() {
    initNav();
    initHero();
    initVideos();
    TrialQuiz.init();
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
})();
