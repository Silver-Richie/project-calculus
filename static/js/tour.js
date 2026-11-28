/**
 * Calculus Bridge — Tur panduan kontekstual (spotlight Archie per halaman/fitur), tanpa pustaka eksternal.
 *
 * Mechanism:
 *   - TOURS = konfigurasi langkah per slug (home, quiz, ranked, shop, leaderboard, lesson; sama dengan
 *     gamification/tutorials.PAGES). Tur suatu halaman berjalan otomatis sekali saja: bila slug-nya belum ada
 *     di server-profile.completed_tutorials. Selesai/Lewati → POST /api/tutorial/selesai/ {"page": slug}.
 *   - Pemicu: Tour.onPage(page) dari Nav.go (app.js) untuk menu; Tour.maybe('quiz', {mode}) dari QuizEngine
 *     saat soal pertama sesi latihan / Mode Latihan tampil; beranda saat halaman dimuat.
 *   - Spotlight: .tour-hole (fixed) + box-shadow raksasa meredupkan sisa layar; .tour-blocker menahan klik.
 *     Target = kelompok selector alternatif, dipakai kelompok pertama yang terlihat (gabungan persegi);
 *     langkah `optional` dilewati bila targetnya tidak ada (mis. tombol hint).
 *   - Kotak dialog Archie: di bawah target bila muat, di atas bila tidak, selain itu lembar di sisi layar yang
 *     kosong (HP). Dihitung ulang saat resize/scroll. Begitu ditutup, overlay tidak lagi menerima klik.
 *   - "Ulangi Panduan Aplikasi" ([data-tour-replay]) → POST /api/tutorial/ulang/ lalu tur beranda dimulai lagi.
 * Bergantung pada Icon (icons.js), Nav & postJSON (app.js); Archie dari <template id="tour-archie">.
 */
const Tour = (() => {
  'use strict';

  const TOURS = {
    home: () => [
      { targets: [['.topic-node.topic-active .topic-node-inner'], ['#skill-tree']], wait: true,
        text: 'Halo! Aku Archie. Klik node yang menyala ini untuk mulai latihan kalkulus pertamamu.' },
      { targets: [['#hud-xp', '#hud-hearts-pill'], ['.hud-info']],
        text: 'Setiap jawaban benar memberimu XP. Hati-hati: gagal lulus sebuah sesi mengurangi 1 Heart-mu.' },
      { targets: [['#streak-banner'], ['#hud-streak']],
        text: 'Mainkan minimal 1 sesi setiap hari untuk menjaga api Streak tetap menyala!' },
      { targets: [['[data-tour="ranked"]']],
        text: 'Sudah mencapai Level 3? Uji kecepatanmu berduel kalkulus melawan pemain lain di sini!' },
      { targets: [['#sidebar-fasilkom', '#sidebar-fmipa', '#sidebar-ft'], ['#hud-faculty-badge']],
        text: 'Kamu bisa mengganti jalur materi sesuai fakultasmu (Teknik, Fasilkom, FMIPA) kapan saja.',
        mobileNote: 'Gantinya lewat halaman Profil.' },
    ],
    quiz: ({ mode } = {}) => [
      { targets: [['#quiz-container .quiz-meta', '#quiz-container .quiz-prompt']], wait: true,
        text: 'Ini soalmu. Rumusnya ditulis seperti di buku (pecahan bertumpuk, pangkat, akar). Di atasnya ada nomor soal dan tingkat kesulitannya.' },
      { targets: [['#quiz-board']], optional: true,
        text: 'Butuh coret-coret? Pakai papan tulis ini untuk menghitung. Tiap soal punya papan sendiri.' },
      { targets: [['#btn-hint']], optional: true,
        text: 'Mentok? Tekan "Minta hint" untuk petunjuk bertahap, satu per satu.' },
      { targets: [['#options-list', '#btn-submit']],
        text: 'Pilih satu jawaban, lalu tekan Jawab. Benar atau salah, pembahasan langkah demi langkah langsung muncul.' },
      { targets: [['#quiz-container .quiz-progress-bar']], optional: true,
        text: mode === 'free'
          ? 'Bar ini progres latihanmu. Di Mode Latihan tidak ada Heart yang hilang dan tidak ada XP, jadi bebas mencoba.'
          : 'Bar ini progres sesimu. Kamu lulus kalau jawaban benarnya cukup; gagal lulus sesi mengurangi 1 Heart, jadi teliti ya!' },
    ],
    ranked: () => [
      { targets: [['#page-ranked .ranked-emblem-wrap']], wait: true,
        text: 'Ini rank-mu. Tangganya Terra → Luna → Solar → Nova → Apex. Menang = +1 bintang; bintang penuh lalu menang lagi = naik sub-rank. Di Apex, bintang diganti Apex Points.' },
      { targets: [['#page-ranked .ranked-shield']],
        text: 'Streak Shield dari Item Shop otomatis menjaga bintangmu saat kalah. Di Terra III & II bintangmu juga aman dari kekalahan.' },
      { targets: [['#duel-start-btn'], ['#page-ranked .ranked-play']],
        text: 'Duel = 10 soal yang sama untukmu dan lawan selevel. Jawab benar dan cepat untuk skor tertinggi; menang dapat +2 Diamond. Terbuka mulai Level 3.' },
    ],
    shop: () => [
      { targets: [['#page-shop .shop-balance']], wait: true,
        text: 'Ini saldo Diamond-mu. Diamond didapat dari naik level, menuntaskan topik, dan menang duel.' },
      { targets: [['#page-shop .shop-tabs']], wait: true,
        text: 'Tukar Diamond di tab Booster: isi ulang Heart atau beli Streak Shield pelindung bintang. Tab lainnya berisi aksesori untuk Archie.' },
    ],
    leaderboard: () => [
      { targets: [['#page-rank .lbx-seg']], wait: true,
        text: 'Pilih papannya: Level (total XP), Rank Duel, atau jumlah Menang Duel.' },
      { targets: [['#page-rank .lbx-scopes']],
        text: 'Bandingkan dirimu se-Indonesia, sekampus, atau sefakultas. Yang tampil 100 besar, dan posisimu selalu terlihat di kartu Posisimu.' },
    ],
    lesson: () => [
      { targets: [['#page-lesson .lesson-tabs']], wait: true,
        text: 'Kurikulum berisi semua materi dalam slide interaktif. Tab kedua berisi Bank Soal & Referensi.' },
      { targets: [['#lp-outline-body']], optional: true,
        text: 'Pilih topik dari daftar ini untuk membuka slidenya. Progres bacamu tersimpan otomatis.' },
    ],
  };
  // Halaman (Nav.go) → slug tur
  const PAGE_TOUR = { levelup: 'home', ranked: 'ranked', shop: 'shop', rank: 'leaderboard', lesson: 'lesson' };
  const PAD = 8, GAP = 14, MARGIN = 12;

  const profile = (() => {
    try { return JSON.parse(document.getElementById('server-profile')?.textContent || 'null'); } catch (_) { return null; }
  })();
  let completed = new Set(profile?.completed_tutorials || []);
  let root = null, slug = null, steps = [], index = 0, raf = 0, lastFocus = null;
  const reduced = () => window.matchMedia?.('(prefers-reduced-motion: reduce)').matches;
  const available = () => !!(profile && document.getElementById('tour-archie'));

  // ── target ────────────────────────────────────────────────────────────────
  function visible(el) {
    const r = el.getBoundingClientRect();
    if (r.width === 0 || r.height === 0) return false;
    return el.checkVisibility ? el.checkVisibility({ visibilityProperty: true, opacityProperty: true }) : true;
  }
  const matches = (group) => group.flatMap((sel) => [...document.querySelectorAll(sel)]).filter(visible);

  /** Elemen dari kelompok alternatif pertama yang punya elemen terlihat. */
  function targetsOf(step) {
    for (const group of step.targets) {
      const els = matches(group);
      if (els.length) return els;
    }
    return [];
  }

  function unionRect(els) {
    const rs = els.map((e) => e.getBoundingClientRect());
    const left = Math.min(...rs.map((r) => r.left)) - PAD, top = Math.min(...rs.map((r) => r.top)) - PAD;
    const right = Math.max(...rs.map((r) => r.right)) + PAD, bottom = Math.max(...rs.map((r) => r.bottom)) + PAD;
    return { left, top, right, bottom, width: right - left, height: bottom - top, cx: (left + right) / 2 };
  }

  /** Tunggu target utama muncul (konten dirender asinkron), maks ~5 detik. */
  function waitFor(step, ms = 5000) {
    return new Promise((resolve) => {
      const t0 = performance.now();
      const tick = () => (matches(step.targets[0]).length || performance.now() - t0 > ms ? resolve() : setTimeout(tick, 150));
      tick();
    });
  }

  // ── tampilan ──────────────────────────────────────────────────────────────
  function mount() {
    root = document.createElement('div');
    root.className = 'tour-root';
    root.setAttribute('role', 'dialog');
    root.setAttribute('aria-modal', 'true');
    root.setAttribute('aria-labelledby', 'tour-text');
    const archie = document.getElementById('tour-archie')?.content.cloneNode(true);
    root.innerHTML = `
      <div class="tour-blocker"></div>
      <div class="tour-hole" aria-hidden="true"></div>
      <div class="tour-card">
        <span class="tour-arrow" aria-hidden="true"></span>
        <div class="tour-archie"></div>
        <div class="tour-body">
          <p class="tour-step"></p>
          <p class="tour-text" id="tour-text"></p>
          <div class="tour-dots" aria-hidden="true"></div>
          <div class="tour-actions">
            <button type="button" class="link-btn tour-skip" data-tour-act="skip">Lewati Tutorial</button>
            <button type="button" class="btn btn-primary btn-sm tour-next" data-tour-act="next"></button>
          </div>
        </div>
      </div>`;
    if (archie) root.querySelector('.tour-archie').appendChild(archie);
    document.body.appendChild(root);
    root.addEventListener('click', onClick);
    document.addEventListener('keydown', onKey, true);
    window.addEventListener('resize', schedule);
    window.addEventListener('scroll', schedule, true);
  }

  function schedule() {
    cancelAnimationFrame(raf);
    raf = requestAnimationFrame(place);
  }

  /** Letakkan lubang spotlight & kotak dialog sesuai target langkah saat ini. */
  function place() {
    if (!root) return;
    const els = targetsOf(steps[index]);
    const hole = root.querySelector('.tour-hole'), card = root.querySelector('.tour-card');
    const vw = window.innerWidth, vh = window.innerHeight;
    card.classList.toggle('narrow', vw < 560);
    if (!els.length) {                                   // target tidak ada: dialog di tengah, layar diredupkan penuh
      hole.style.cssText = `left:${vw / 2}px;top:${vh / 2}px;width:0;height:0`;
      card.dataset.place = 'center';
      card.style.left = `${Math.max(MARGIN, (vw - card.offsetWidth) / 2)}px`;
      card.style.top = `${Math.max(MARGIN, (vh - card.offsetHeight) / 2)}px`;
      return;
    }
    const r = unionRect(els);
    hole.style.cssText = `left:${r.left}px;top:${r.top}px;width:${r.width}px;height:${r.height}px`;
    const cw = card.offsetWidth, ch = card.offsetHeight;
    let top, where;
    if (vh - r.bottom >= ch + GAP + MARGIN) { top = r.bottom + GAP; where = 'below'; }
    else if (r.top >= ch + GAP + MARGIN) { top = r.top - GAP - ch; where = 'above'; }
    else {                                               // tidak muat: lembar di sisi layar yang kosong
      top = (r.top + r.bottom) / 2 > vh / 2 ? MARGIN : vh - ch - MARGIN;
      where = 'sheet';
    }
    const left = Math.min(Math.max(MARGIN, r.cx - cw / 2), Math.max(MARGIN, vw - cw - MARGIN));
    card.dataset.place = where;
    card.style.left = `${left}px`;
    card.style.top = `${Math.max(MARGIN, top)}px`;
    card.style.setProperty('--arrow-x', `${Math.min(Math.max(22, r.cx - left), cw - 22)}px`);
  }

  async function show(i) {
    // Langkah opsional tanpa target (mis. tidak ada tombol hint) dilewati.
    while (i < steps.length && steps[i].optional && !targetsOf(steps[i]).length) i += 1;
    if (i >= steps.length) { finish(); return; }
    index = i;
    const step = steps[i];
    const last = !steps.slice(i + 1).some((s) => !s.optional || targetsOf(s).length);
    root.querySelector('.tour-step').textContent = `Archie · langkah ${i + 1} dari ${steps.length}`;
    const note = step.mobileNote && !targetsOf(step).some((el) => el.id.startsWith('sidebar-')) ? ` ${step.mobileNote}` : '';
    root.querySelector('.tour-text').textContent = step.text + note;
    root.querySelector('.tour-dots').innerHTML = steps.map((_, k) => `<i class="${k <= i ? 'on' : ''}"></i>`).join('');
    const next = root.querySelector('.tour-next');
    next.innerHTML = last ? `${Icon('check')} Selesai` : `Lanjut ${Icon('next')}`;
    const card = root.querySelector('.tour-card');
    card.classList.remove('pop');
    void card.offsetWidth;                                // ulangi animasi muncul
    card.classList.add('pop');
    if (step.wait) await waitFor(step);
    if (!root) return;
    const els = targetsOf(step);
    const r = els.length ? unionRect(els) : null;
    if (r && (r.top < 70 || r.bottom > window.innerHeight - 80)) {
      els[0].scrollIntoView({ block: 'center', behavior: reduced() ? 'auto' : 'smooth' });
      setTimeout(place, reduced() ? 0 : 380);
    }
    place();
    next.focus({ preventScroll: true });
  }

  function onClick(e) {
    const act = e.target.closest('[data-tour-act]')?.dataset.tourAct;
    if (act === 'next') show(index + 1);
    else if (act === 'skip') finish();
  }

  function onKey(e) {
    if (!root) return;
    if (e.key === 'Escape') { e.preventDefault(); finish(); return; }
    if (e.key === 'Tab') {                                  // fokus tetap di dalam dialog
      const btns = [...root.querySelectorAll('button')];
      const i = btns.indexOf(document.activeElement);
      e.preventDefault();
      btns[(i + (e.shiftKey ? btns.length - 1 : 1)) % btns.length].focus();
      return;
    }
    // Pintasan keyboard halaman di bawahnya (mis. memilih opsi soal) tidak boleh jalan selama tur
    if (!root.contains(e.target)) { e.stopPropagation(); e.preventDefault(); }
  }

  // ── mulai / selesai ───────────────────────────────────────────────────────
  function start(name, ctx = {}) {
    if (root || !TOURS[name] || !available()) return false;
    slug = name;
    steps = TOURS[name](ctx);
    lastFocus = document.activeElement;
    if (name === 'home') window.scrollTo({ top: 0 });
    mount();
    show(0);
    return true;
  }

  /** Jalankan tur `name` hanya bila belum pernah selesai/dilewati. */
  function maybe(name, ctx) {
    if (completed.has(name)) return false;
    return start(name, ctx);
  }

  /** Tutup tur (Selesai atau Lewati) dan catat di server agar tidak muncul otomatis lagi di halaman ini. */
  function finish() {
    if (!root) return;
    const el = root, done = slug;
    root = null;
    slug = null;
    document.removeEventListener('keydown', onKey, true);
    window.removeEventListener('resize', schedule);
    window.removeEventListener('scroll', schedule, true);
    cancelAnimationFrame(raf);
    el.classList.add('closing');                          // pointer-events: none → halaman langsung bisa diklik
    setTimeout(() => el.remove(), reduced() ? 0 : 220);
    lastFocus?.focus?.({ preventScroll: true });
    completed.add(done);
    if (typeof postJSON === 'function') postJSON('/api/tutorial/selesai/', { page: done }).catch(() => {});
  }

  /** Dipanggil Nav.go (app.js) setiap pindah halaman. */
  function onPage(page) {
    const name = PAGE_TOUR[page];
    if (name) setTimeout(() => maybe(name), 450);         // beri waktu halaman (mis. toko/leaderboard) dirender
  }

  async function replay() {
    if (root) return;
    try {
      const r = await postJSON('/api/tutorial/ulang/', {});
      completed = new Set(r.completed_tutorials || []);
    } catch (_) {
      completed = new Set();
    }
    if (typeof Nav !== 'undefined' && !document.getElementById('page-levelup')?.classList.contains('active')) Nav.go('levelup');
    else maybe('home');
  }

  function init() {
    document.addEventListener('click', (e) => { if (e.target.closest('[data-tour-replay]')) replay(); });
    if (document.getElementById('page-levelup')?.classList.contains('active')) setTimeout(() => maybe('home'), 700);
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();

  return { maybe, onPage, start, finish, replay };
})();
