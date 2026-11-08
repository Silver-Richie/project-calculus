/**
 * Calculus Bridge — App Engine v4
 * Konten (materi, soal, pembahasan, grafik) dimuat dari database lewat
 * /api/curriculum/; tidak ada lagi materi yang ditulis langsung di JS.
 *
 * Modules:
 *   SFX             – Web Audio synthesizer
 *   State           – LocalStorage game state (progres per fakultas)
 *   Nav             – Bottom nav + sidebar routing
 *   Mascot          – Reactive SVG character
 *   Curriculum      – Data kurikulum dari API
 *   SkillTree       – Peta belajar (Level Up)
 *   Catalogue       – Halaman Lesson, dikelompokkan per berkas sumber
 *   QuizEngine      – Kuis hint bertahap + pembahasan dengan grafik slider (GraphLab)
 *   Drawer          – Panel materi/kuis/bank soal (node bertopik diteruskan ke Practice, static/js/practice.js)
 *   DiagnosticModal – Tes diagnostik adaptif (dinilai di server)
 *   Confetti        – Canvas particle burst
 */

/** Token CSRF Django dari cookie (untuk fetch POST). */
function csrfToken() {
  return document.cookie.split('; ').find((c) => c.startsWith('csrftoken='))?.split('=')[1] || '';
}

/** POST JSON ke API Django; mengembalikan objek JSON (atau melempar Error). */
async function postJSON(url, body) {
  const res = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrfToken() },
    body: JSON.stringify(body || {}),
  });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(data.message || `HTTP ${res.status}`);
  return data;
}

/* ════════════════════════════════════════════════════════════════
   SFX — Minimal Web Audio synthesizer (no external files needed)
   ════════════════════════════════════════════════════════════════ */
const SFX = (() => {
  let ctx = null;
  let on = true;

  function init() {
    if (!ctx) ctx = new (window.AudioContext || window.webkitAudioContext)();
  }

  function tone(freq, type = 'sine', dur = 0.12, delay = 0, vol = 0.1) {
    if (!on) return;
    init();
    try {
      const osc = ctx.createOscillator();
      const gain = ctx.createGain();
      osc.type = type;
      osc.frequency.setValueAtTime(freq, ctx.currentTime + delay);
      gain.gain.setValueAtTime(vol, ctx.currentTime + delay);
      gain.gain.exponentialRampToValueAtTime(0.0001, ctx.currentTime + delay + dur);
      osc.connect(gain);
      gain.connect(ctx.destination);
      osc.start(ctx.currentTime + delay);
      osc.stop(ctx.currentTime + delay + dur);
    } catch (_) { }
  }

  return {
    toggle() {
      on = !on;
      const btn = document.getElementById('sound-toggle-btn');
      if (btn) { btn.textContent = on ? '🔊 Suara' : '🔇 Mute'; btn.classList.toggle('muted', !on); }
      if (on) this.click();
      return on;
    },
    click() { tone(600, 'triangle', 0.04); },
    correct() { [523, 659, 784, 1046].forEach((f, i) => tone(f, 'triangle', 0.18, i * 0.08, 0.14)); },
    wrong() { tone(220, 'sine', 0.18); tone(185, 'sine', 0.25, 0.14); },
    fanfare() {
      [[523, .12, 0], [659, .12, .1], [784, .14, .2], [1046, .35, .32]].forEach(([f, d, t]) => tone(f, 'sine', d, t, .18));
    },
    hint() { tone(440, 'sine', 0.1); },
  };
})();

/* ════════════════════════════════════════════════════════════════
   STATE — LocalStorage persistence
   Progres disimpan per fakultas karena tiap fakultas punya skill tree sendiri
   (Tahap 1–5 umum + Tahap 6–8 khusus fakultas).
   ════════════════════════════════════════════════════════════════ */
const State = (() => {
  // Profil akun yang login (dikirim server lewat json_script di index.html)
  const SERVER = (() => {
    try { return JSON.parse(document.getElementById('server-profile')?.textContent || 'null'); }
    catch (_) { return null; }
  })();
  // State disimpan per akun agar beberapa akun di satu browser tidak tercampur.
  const KEY = SERVER ? `cb_state_v4:${SERVER.username}` : 'cb_state_v4';
  const DEFAULTS = {
    faculty: 'fasilkom',
    xp: 0, streak: 1, hearts: 5, maxHearts: 5, gems: 100,
    progress: {},   // { ft: { completed: [slug...], active: slug|null } }
    sound: true,
  };
  const FAC_LABELS = { fasilkom: '💻 Fasilkom', fmipa: '🔬 FMIPA', ft: '⚙️ Fak. Teknik' };

  let s = (() => {
    try { return Object.assign({}, DEFAULTS, JSON.parse(localStorage.getItem(KEY))); }
    catch (_) { return { ...DEFAULTS }; }
  })();

  /**
   * Menggabungkan data server ke state lokal: fakultas akun, XP, dan progres
   * hasil tes diagnostik (node yang dilewati = selesai, node rekomendasi = aktif).
   */
  if (SERVER) {
    if (SERVER.faculty) s.faculty = SERVER.faculty;
    s.xp = Math.max(s.xp || 0, SERVER.xp || 0);
    const p = s.progress[s.faculty] || (s.progress[s.faculty] = { completed: [], active: null });
    (SERVER.completed || []).forEach((slug) => { if (!p.completed.includes(slug)) p.completed.push(slug); });
    if (SERVER.active && !p.completed.includes(SERVER.active) && !p.active) p.active = SERVER.active;
  }

  /** Simpan pilihan fakultas ke akun (UserProfile) di server. */
  function syncFaculty(f) {
    if (!SERVER) return;
    postJSON('/api/profile/faculty/', { faculty: f }).catch(() => {});
  }

  function prog() {
    if (!s.progress[s.faculty]) s.progress[s.faculty] = { completed: [], active: null };
    return s.progress[s.faculty];
  }

  function save() {
    try { localStorage.setItem(KEY, JSON.stringify(s)); } catch (_) { }
    updateHUD();
  }

  function setText(id, val) {
    const el = document.getElementById(id);
    if (el) el.textContent = val;
  }

  function updateHUD() {
    setText('hud-xp', `⚡ ${s.xp} XP`);
    setText('hud-streak', `🔥 ${s.streak}`);
    setText('hud-hearts-val', `${s.hearts}/${s.maxHearts}`);
    setText('hud-gems', `💎 ${s.gems}`);
    setText('profile-xp', s.xp);
    setText('profile-streak', s.streak);
    setText('profile-hearts', s.hearts);
    setText('profile-gems', s.gems);
    setText('rank-my-xp', `${s.xp} XP`);
    setText('hud-faculty-badge', FAC_LABELS[s.faculty] || 'Fasilkom');

    ['fasilkom', 'fmipa', 'ft'].forEach((f) => {
      const el = document.getElementById(`sidebar-${f}`);
      if (el) el.classList.toggle('active', f === s.faculty);
    });
    document.querySelectorAll('.fac-card').forEach((c) => {
      c.classList.toggle('active', c.dataset.fac === s.faculty);
    });
    if (typeof SkillTree !== 'undefined') SkillTree.refreshStates();
  }

  function floatXP(amount) {
    const el = document.getElementById('hud-xp');
    if (!el) return;
    const r = el.getBoundingClientRect();
    const tag = document.createElement('span');
    tag.className = 'float-xp';
    tag.textContent = `+${amount} XP!`;
    tag.style.cssText = `left:${r.left + 8}px;top:${r.top - 10}px;`;
    document.body.appendChild(tag);
    setTimeout(() => tag.remove(), 1200);
  }

  return {
    get: () => s,
    progress: prog,
    addXP(n) { s.xp += n; save(); floatXP(n); },
    loseHeart() {
      if (s.hearts > 0) { s.hearts--; save(); }
      const p = document.getElementById('hud-hearts-pill');
      if (p) { p.classList.add('hearts-shake'); setTimeout(() => p.classList.remove('hearts-shake'), 500); }
    },
    setFaculty(f) {
      if (s.faculty === f) return;
      s.faculty = f; save(); SFX.click();
      syncFaculty(f);
      Curriculum.load(f);
    },
    /** Status node: 'completed' | 'active' | 'locked'. Node pertama otomatis aktif. */
    nodeStatus(slug, tree) {
      const p = prog();
      if (p.completed.includes(slug)) return 'completed';
      const active = p.active || tree.find((n) => !p.completed.includes(n.slug))?.slug;
      return slug === active ? 'active' : 'locked';
    },
    completeNode(slug, nextSlug) {
      const p = prog();
      if (!p.completed.includes(slug)) p.completed.push(slug);
      if (SERVER) postJSON('/api/progress/node/', { slug }).catch(() => {});
      if (nextSlug && !p.completed.includes(nextSlug)) p.active = nextSlug;
      else if (!nextSlug) p.active = null;
      save();
    },
    /** Dipakai diagnostik: semua node sebelum `slug` dianggap lulus, `slug` menjadi aktif. */
    startFrom(slug, tree) {
      const p = prog();
      const idx = tree.findIndex((n) => n.slug === slug);
      tree.slice(0, Math.max(0, idx)).forEach((n) => { if (!p.completed.includes(n.slug)) p.completed.push(n.slug); });
      p.active = slug;
      save();
    },
    save, updateHUD,
  };
})();

/* ════════════════════════════════════════════════════════════════
   NAV — Bottom navigation + page routing
   ════════════════════════════════════════════════════════════════ */
const Nav = (() => {
  const pages = ['levelup', 'lesson', 'rank', 'user'];

  return {
    go(page) {
      SFX.click();
      pages.forEach(p => {
        const sec = document.getElementById(`page-${p}`);
        const btn = document.getElementById(`bnav-${p}`);
        const sbr = null; // sidebar items don't have ids for pages
        if (sec) sec.classList.toggle('active', p === page);
        if (btn) btn.classList.toggle('active', p === page);
      });
    },
  };
})();

/* ════════════════════════════════════════════════════════════════
   MASCOT — Archie the Axolotl reactive states
   ════════════════════════════════════════════════════════════════ */
const Mascot = (() => {
  const moods = ['idle', 'celebrate', 'thinking', 'comfort'];
  const quotes = [
    "Halo! Aku Archie, pemandumu taklukkan kalkulus! 🦎",
    "Tahukah kamu? dy/dx dibuat Leibniz, Newton pakai notasi titik ẏ!",
    "Limit itu seperti mendekati gebetan — sedekat mungkin tanpa disentuh 😄",
    "Turunan = speedometer mobilmu — laju perubahan sesaat!",
    "Integral = menghitung area di bawah kurva — menjumlahkan hal kecil.",
    "Salah itu normal — otakmu sedang membentuk sinapsis baru!",
    "Satu kuis sehari, kalkulus jadi teman sejati 🌟",
  ];

  function setMood(mood, text) {
    const svg = document.getElementById('mascot-svg');
    if (svg) {
      moods.forEach(m => svg.classList.remove(`mascot-${m}`));
      svg.classList.add(`mascot-${mood}`);
    }
    if (text) say(text);
  }

  function say(text) {
    const el = document.getElementById('mascot-speech');
    if (!el) return;
    el.innerHTML = text;
    el.classList.remove('bubble-pop');
    void el.offsetWidth;
    el.classList.add('bubble-pop');
  }

  return {
    setMood,
    say,
    randomQuote() {
      const q = quotes[Math.floor(Math.random() * quotes.length)];
      setMood('wave', q);
      SFX.click();
    },
  };
})();

/* ════════════════════════════════════════════════════════════════
   CURRICULUM — data materi & soal dari database (/api/curriculum/)
   ════════════════════════════════════════════════════════════════ */
const Curriculum = (() => {
  let data = { tree: [], documents: [], references: [], faculties: [], main_levels: [], session_progress: {} };
  const FAC_DESC = {
    fasilkom: 'Jalur <strong>Fasilkom</strong> — Kalkulus untuk Komputasi dan AI',
    fmipa: 'Jalur <strong>FMIPA</strong> — Analisis dan Ketelitian Konsep',
    ft: 'Jalur <strong>Fak. Teknik</strong> — Kalkulus untuk Pemodelan Rekayasa',
  };

  async function load(faculty) {
    const treeEl = document.getElementById('skill-tree');
    if (treeEl) treeEl.innerHTML = '<p class="loading-text">Memuat peta belajar…</p>';
    try {
      const res = await fetch(`/api/curriculum/?faculty=${encodeURIComponent(faculty)}`);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      data = await res.json();
    } catch (err) {
      console.error('[Curriculum] gagal memuat', err);
      if (treeEl) treeEl.innerHTML = '<p class="loading-text">Gagal memuat materi. Pastikan server berjalan dan data sudah di-seed.</p>';
      return;
    }
    const desc = document.getElementById('tree-fac-desc');
    if (desc) desc.innerHTML = FAC_DESC[faculty] || '';
    SkillTree.render();
    Catalogue.render();
  }

  return {
    load,
    get tree() { return data.tree || []; },
    get mainLevels() { return data.main_levels || []; },
    get requiredSessions() { return data.required_sessions || 3; },
    /** Progres sesi user: { [sessionId]: { attempts, best, last, passed } } */
    sessionProgress(id) { return (data.session_progress || {})[id] || null; },
    setSessionProgress(id, p) { (data.session_progress || (data.session_progress = {}))[id] = p; },
    /** Cari topik beserta node induknya. */
    topic(slug) {
      for (const n of data.tree || []) {
        const t = (n.topics || []).find((x) => x.slug === slug);
        if (t) return { topic: t, node: n };
      }
      return null;
    },
    get documents() { return data.documents || []; },
    node(slug) { return (data.tree || []).find((n) => n.slug === slug) || (data.references || []).find((n) => n.slug === slug); },
    question(code) {
      for (const n of data.tree || []) {
        const q = (n.questions || []).find((x) => x.code === code);
        if (q) return { q, node: n };
      }
      return null;
    },
    nextOf(slug) {
      const t = data.tree || [];
      const i = t.findIndex((n) => n.slug === slug);
      return i >= 0 && i + 1 < t.length ? t[i + 1].slug : null;
    },
  };
})();

const DIFF_LABEL = { basic: 'Dasar / Mudah', medium: 'Sedang', high: 'Sulit' };

/**
 * Papan tulis kuis. Saat soal tampil, drawer menjadi layar penuh (kelas .quiz-mode):
 * kiri soal & jawaban, kanan papan tulis. Setiap soal memakai papan sendiri
 * (kunci = id/kode soal), jadi soal baru selalu kosong dan coretan lama kembali
 * bila soal yang sama dibuka lagi.
 */
const QuizBoard = {
  show(key) {
    const drawer = document.getElementById('lesson-drawer');
    if (!drawer || typeof Whiteboard === 'undefined') return;
    drawer.classList.add('quiz-mode');
    Whiteboard.mount(document.getElementById('quiz-board'))?.load(`quiz:${key}`);
  },
  hide() {
    document.getElementById('lesson-drawer')?.classList.remove('quiz-mode');
  },
};

/* ════════════════════════════════════════════════════════════════
   SKILL TREE — Peta belajar (halaman Level Up)
   ════════════════════════════════════════════════════════════════ */
const SkillTree = (() => {
  function render() {
    const wrap = document.getElementById('skill-tree');
    if (!wrap) return;
    const tree = Curriculum.tree;
    const levels = Object.fromEntries(Curriculum.mainLevels.map((m) => [m.slug, m]));
    let lastGroup = null;
    wrap.innerHTML = tree.map((n, i) => {
      // Level utama hanya tampil sebagai judul pengelompokan.
      const group = n.main_level || (n.faculty ? 'khusus' : 'umum');
      const connector0 = i < tree.length - 1 ? '<div class="tree-connector"></div>' : '';
      // Sub-level bertopik: banner (level + sub-level) lalu satu node per topik (Practice.pathHTML).
      if ((n.topics || []).length) {
        lastGroup = group;
        return Practice.pathHTML(n, levels[group]) + connector0;
      }
      let header = '';
      if (group !== lastGroup) {
        const lvl = levels[group];
        header = lvl
          ? `<div class="tree-level-label"><span>${lvl.icon}</span> Level Utama ${lvl.order}: ${lvl.title}</div>`
          : `<div class="tree-group-label">${group === 'umum' ? '📘 Materi Umum' : '🎓 Materi Khusus'}</div>`;
        lastGroup = group;
      }
      const connector = i < tree.length - 1 ? '<div class="tree-connector"></div>' : '';
      const zig = ['zig-left', '', 'zig-right', ''][i % 4];
      return `${header}
        <div class="tree-node${n.is_boss ? ' node-boss' : ''} ${zig}" id="node-${n.slug}" data-slug="${n.slug}"
             onclick="Drawer.open('${n.slug}')">
          <button class="node-btn" title="${n.title}">${n.icon}</button>
          <span class="node-label">${n.title.replace(/^Tahap \d+:\s*/, '')}${(n.topics || []).length ? `<small>${n.topics.length} topik</small>` : ''}</span>
        </div>${connector}`;
    }).join('');
    refreshStates();
  }

  function refreshStates() {
    const tree = Curriculum.tree;
    document.querySelectorAll('#skill-tree .tree-node').forEach((el) => {
      const st = State.nodeStatus(el.dataset.slug, tree);
      el.classList.remove('node-completed', 'node-active', 'node-locked');
      el.classList.add(`node-${st}`);
      const btn = el.querySelector('.node-btn');
      const n = Curriculum.node(el.dataset.slug);
      if (btn && n) btn.textContent = st === 'completed' ? '✓' : st === 'locked' ? '🔒' : n.icon;
    });
    if (typeof Practice !== 'undefined') Practice.refreshPath();
    if (typeof Catalogue !== 'undefined') Catalogue.refreshStates();
  }

  return { render, refreshStates };
})();

/* ════════════════════════════════════════════════════════════════
   CATALOGUE — Halaman Lesson, dikelompokkan per berkas sumber
   ════════════════════════════════════════════════════════════════ */
const Catalogue = (() => {
  const CAT_ICON = { materi: '📖', soal: '📝', lampiran: '📚', buku: '📕' };

  function nodeCard(n) {
    return `
      <div class="lesson-card" data-slug="${n.slug}" onclick="Drawer.open('${n.slug}', { browse: true })">
        <div class="lesson-card-icon">${n.icon}</div>
        <div class="lesson-card-title">${n.title}</div>
        <div class="lesson-card-desc">${n.subtitle || ''}</div>
        <div class="lesson-card-meta">
          ${n.kind === 'reference' ? 'Bacaan referensi' : (n.topics || []).length
            ? `${n.topics.length} topik · ${n.topics.length * 5} sesi latihan`
            : `${(n.sections || []).length} bagian · ${(n.questions || []).length} soal`}
          <span class="lesson-card-status" data-status-for="${n.slug}"></span>
        </div>
      </div>`;
  }

  function questionRow(code) {
    const found = Curriculum.question(code);
    if (!found) return '';
    const { q } = found;
    const plain = q.prompt.replace(/<[^>]+>/g, '');
    return `
      <button class="qbank-row" onclick="Drawer.openQuestion('${q.code}')">
        <span class="qbank-code">${q.code}</span>
        <span class="quiz-diff-badge diff-${q.difficulty}">${DIFF_LABEL[q.difficulty] || q.difficulty}</span>
        <span class="qbank-prompt">${plain.length > 110 ? plain.slice(0, 110) + '…' : plain}</span>
        ${(q.graphs || []).length ? '<span class="qbank-graph" title="Pembahasan memiliki grafik interaktif">🎛️</span>' : ''}
      </button>`;
  }

  function render() {
    const box = document.getElementById('lesson-catalogue');
    if (!box) return;
    const levelNodes = Curriculum.tree.filter((n) => (n.topics || []).length);
    const levelsHTML = levelNodes.length ? `
      <section class="doc-section">
        <header class="doc-header">
          <span class="doc-icon">🏔️</span>
          <div>
            <div class="doc-filename">Kurikulum 4 Level · Whitman · MIT (Strang) · Stewart</div>
            <h3 class="doc-title">Level Utama → Sub-level → Topik → 5 Sesi Latihan</h3>
            <p class="doc-sub">Soal tiap sesi diacak khusus untuk akunmu, lengkap dengan pembahasan &amp; grafik slider.</p>
          </div>
        </header>
        <div class="lesson-grid">${levelNodes.map(nodeCard).join('')}</div>
      </section>` : '';
    box.innerHTML = levelsHTML + Curriculum.documents.map((doc) => `
      <section class="doc-section">
        <header class="doc-header">
          <span class="doc-icon">${CAT_ICON[doc.category] || '📄'}</span>
          <div>
            <div class="doc-filename">${doc.filename}</div>
            <h3 class="doc-title">${doc.title}</h3>
            ${doc.subtitle ? `<p class="doc-sub">${doc.subtitle}</p>` : ''}
          </div>
        </header>
        ${doc.category === 'soal' || doc.category === 'buku'
          ? `<div class="qbank-list">${doc.items.map(questionRow).join('')}</div>`
          : `<div class="lesson-grid">${doc.items.map((slug) => Curriculum.node(slug)).filter(Boolean).map(nodeCard).join('')}</div>`}
      </section>`).join('');
    refreshStates();
  }

  function refreshStates() {
    const tree = Curriculum.tree;
    document.querySelectorAll('[data-status-for]').forEach((el) => {
      const slug = el.dataset.statusFor;
      if (!tree.find((n) => n.slug === slug)) { el.textContent = ''; return; }
      const st = State.nodeStatus(slug, tree);
      el.className = `lesson-card-status status-${st === 'completed' ? 'done' : st}`;
      el.textContent = st === 'completed' ? '✓ Selesai' : st === 'active' ? '▶ Aktif' : '🔒 Kuis terkunci';
    });
  }

  return { render, refreshStates };
})();

/* ════════════════════════════════════════════════════════════════
   LESSON RENDERING — bagian materi + grafik interaktif
   ════════════════════════════════════════════════════════════════ */
function renderSections(container, node) {
  container.innerHTML = '';
  if (node.source) {
    container.insertAdjacentHTML('beforeend', `<div class="source-tag">📄 Sumber: ${node.source.filename}</div>`);
  }
  (node.sections || []).forEach((sec) => {
    const block = document.createElement('div');
    block.className = 'lesson-block';
    block.innerHTML = `<h4>${sec.heading}</h4>${sec.source ? `<div class="source-tag">📄 Dari berkas: ${sec.source}</div>` : ''}<div class="lesson-body">${sec.body_html}</div>`;
    container.appendChild(block);
    if ((sec.graphs || []).length) {
      const g = document.createElement('div');
      g.className = 'lesson-graphs';
      block.appendChild(g);
      GraphLab.mountList(g, sec.graphs);
    }
  });
}

/**
 * Fisher-Yates shuffle: salinan acak dari `arr` (array asli tidak diubah).
 * Mechanism: dari elemen terakhir ke depan, tukar elemen i dengan elemen acak j ∈ [0, i],
 * sehingga setiap urutan punya peluang sama (O(n)).
 */
function shuffle(arr) {
  const a = arr.slice();
  for (let i = a.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [a[i], a[j]] = [a[j], a[i]];
  }
  return a;
}

/* ════════════════════════════════════════════════════════════════
   QUIZ ENGINE — hint bertahap + pembahasan lengkap dengan grafik slider
   Mode 'level'   : kuis node skill tree (membuka node berikutnya).
   Mode 'practice': satu soal dari Bank Soal (tanpa XP/nyawa).
   ════════════════════════════════════════════════════════════════ */
const QuizEngine = (() => {
  let nodeSlug = null;
  let questions = [];
  let idx = 0;
  let hintsUsed = 0;
  let answered = false;
  let mode = 'level';      // 'level' | 'practice' | 'session'
  let answers = [];        // mode session: [{ id, option }] dikirim ke server di akhir sesi

  /** Hint = langkah pembahasan kecuali langkah terakhir (agar jawaban tidak langsung bocor). */
  function hintsOf(q) {
    const steps = q.steps || [];
    if (steps.length > 1) return steps.slice(0, -1);
    return q.explanation ? [q.explanation] : [];
  }

  function pembahasanHTML(q) {
    return `
      <div class="pembahasan" id="pembahasan">
        <h5>📚 Pembahasan</h5>
        <ol class="steps-list">${(q.steps || []).map((s) => `<li>${s}</li>`).join('')}</ol>
        <div class="answer-box"><strong>Jawaban:</strong> ${q.answer || ''}</div>
        ${q.explanation ? `<p class="expl-note">💬 ${q.explanation}</p>` : ''}
        ${(q.graphs || []).length ? `
          <div class="pembahasan-graphs" id="pembahasan-graphs">
            <p class="graph-hint">🎛️ Geser slider untuk memanipulasi variabel. Grafik soal tetap tampil sebagai bayangan abu-abu,
            dan tombol <b>📌 Pin</b> menyimpan kondisi untuk dibandingkan.</p>
          </div>` : ''}
        <div class="source-tag">📄 ${q.source || 'Soal acak khusus akunmu'} · ${q.code}</div>
      </div>`;
  }

  function render() {
    const container = document.getElementById('quiz-container');
    if (!container) return;

    if (!questions.length) {
      QuizBoard.hide();
      container.innerHTML = `
        <div class="level-complete">
          <div class="trophy-anim">📖</div>
          <h3>Tahap ini berisi materi saja</h3>
          <p>Berkas soal tidak memuat latihan untuk tahap ini. Tandai selesai setelah membaca materinya.</p>
          <button class="btn btn-growth btn-lg" onclick="QuizEngine.finish()">✓ Tandai Selesai</button>
        </div>`;
      return;
    }
    if (idx >= questions.length) {
      QuizBoard.hide();
      if (mode === 'session') { Practice.finish(answers); return; }
      showComplete();
      return;
    }

    const q = questions[idx];
    const hints = hintsOf(q);
    const progress = Math.round((idx / questions.length) * 100);
    answered = false;
    hintsUsed = 0;

    container.innerHTML = `
      <div class="quiz-wrap">
        ${mode !== 'practice' ? `<div class="quiz-progress-bar"><div class="quiz-progress-fill" style="width:${progress}%"></div></div>` : ''}
        <div class="quiz-meta">
          <span class="quiz-num">${mode !== 'practice' ? `Soal ${idx + 1} dari ${questions.length} · ` : ''}${q.code}</span>
          <span class="quiz-diff-badge diff-${q.difficulty}">${q.difficulty_label || DIFF_LABEL[q.difficulty] || q.difficulty}</span>
        </div>
        <div class="quiz-prompt">${q.prompt}</div>

        <div class="options-list" id="options-list">
          ${q.options.map((o, i) => `
            <button class="option-btn" id="opt-${i}" onclick="QuizEngine.select(${i})">
              <span class="opt-letter">${'ABCDEF'[i]}</span>
              <span>${o.text}</span>
            </button>`).join('')}
        </div>

        <div class="quiz-actions">
          ${hints.length ? `<button class="btn btn-accent btn-sm" id="btn-hint" onclick="QuizEngine.showNextHint()">
            💡 Minta Hint (${hints.length} tersedia)</button>` : ''}
          <button class="btn btn-primary" id="btn-submit" onclick="QuizEngine.submit()" disabled>✅ Jawab</button>
        </div>

        <div class="hint-section" id="hint-section"></div>
        <div id="pembahasan-slot"></div>
      </div>`;

    hideFeedback();
    QuizBoard.show(q.id || q.code);
  }

  function revealPembahasan(q) {
    const slot = document.getElementById('pembahasan-slot');
    if (!slot || slot.childElementCount) return;
    slot.innerHTML = pembahasanHTML(q);
    document.getElementById('btn-reveal')?.remove();
    const g = document.getElementById('pembahasan-graphs');
    if (g) GraphLab.mountList(g, q.graphs);
  }

  function finishNode() {
    if (mode !== 'level' || !nodeSlug) return;
    State.completeNode(nodeSlug, Curriculum.nextOf(nodeSlug));
  }

  function showComplete() {
    const container = document.getElementById('quiz-container');
    if (!container) return;
    SFX.fanfare();
    Confetti.burst();
    Mascot.setMood('celebrate', '🏆 Selamat! Level ini berhasil kamu taklukkan!');
    State.addXP(50);
    finishNode();
    const next = Curriculum.nextOf(nodeSlug);
    container.innerHTML = `
      <div class="level-complete">
        <div class="trophy-anim">🏆</div>
        <h3>Level Selesai!</h3>
        <p>Kamu mendapatkan <strong>+50 Bonus XP</strong>${next ? ' dan membuka tahap berikutnya!' : '. Semua tahap jalur ini tuntas!'}</p>
        <button class="btn btn-growth btn-lg" onclick="Drawer.close(); Nav.go('levelup');">Kembali ke Peta Belajar 🗺️</button>
      </div>`;
  }

  return {
    start(slug, qs, m = 'level') {
      nodeSlug = slug;
      // Mode session sudah diacak server (urutan harus sama saat dinilai), jadi tidak dikocok ulang.
      // Mode lain: kocok urutan soal (level) dan opsi; benar/salah dicek lewat is_correct, bukan posisi.
      questions = (qs || []).map((q) => (m === 'session' ? q : { ...q, options: shuffle(q.options || []) }));
      if (m === 'level') questions = shuffle(questions);
      mode = m;
      idx = 0;
      answers = [];
      render();
    },

    select(i) {
      if (answered) return;
      SFX.click();
      document.querySelectorAll('#options-list .option-btn').forEach((b, j) => b.classList.toggle('selected', j === i));
      const btn = document.getElementById('btn-submit');
      if (btn) { btn.dataset.sel = i; btn.removeAttribute('disabled'); }
    },

    submit() {
      if (answered) return;
      const btn = document.getElementById('btn-submit');
      if (!btn || btn.disabled) return;
      const sel = parseInt(btn.dataset.sel, 10);
      const q = questions[idx];
      const correct = q.options.findIndex((o) => o.is_correct);
      answered = true;
      if (mode === 'session') answers.push({ id: q.id, option: q.options[sel].id });
      btn.disabled = true;
      const hintBtn = document.getElementById('btn-hint');
      if (hintBtn) hintBtn.disabled = true;

      document.querySelectorAll('#options-list .option-btn').forEach((b, j) => {
        if (j === correct) b.classList.add('correct');
        else if (j === sel) b.classList.add('incorrect');
        b.disabled = true;
      });
      revealPembahasan(q);

      const isLast = idx + 1 >= questions.length;
      const actionLabel = mode === 'practice' ? 'Tutup' : isLast ? 'Selesai ➔' : 'Lanjut ➔';
      if (sel === correct) {
        SFX.correct();
        if (mode === 'level') State.addXP(q.xp_reward || 20);
        Mascot.setMood('celebrate', '🎉 Jawaban tepat! Coba geser slider di pembahasan.');
        showFeedback(true, mode === 'level' ? `+${q.xp_reward || 20} XP — Jawaban Tepat!` : 'Jawaban Tepat!',
          `Jawaban: ${q.answer}`, actionLabel);
      } else {
        SFX.wrong();
        if (mode !== 'practice') State.loseHeart();
        Mascot.setMood('comfort', 'Jangan menyerah! Baca pembahasannya ya.');
        showFeedback(false, mode !== 'practice' ? 'Belum tepat (−1 Nyawa)' : 'Belum tepat',
          'Baca pembahasan langkah demi langkah di atas.', actionLabel);
      }
    },

    nextQuestion() {
      hideFeedback();
      if (mode === 'practice') { Drawer.close(); return; }
      idx++;
      render();
      document.querySelector('.drawer-body')?.scrollTo({ top: 0, behavior: 'smooth' });
    },

    finish() {
      finishNode();
      SFX.fanfare();
      Mascot.setMood('celebrate', '📖 Materi tuntas! Tahap berikutnya terbuka.');
      Drawer.close();
      Nav.go('levelup');
    },

    showNextHint() {
      const q = questions[idx];
      const hints = q ? hintsOf(q) : [];
      if (!q || hintsUsed >= hints.length) return;
      SFX.hint();
      const card = document.createElement('div');
      card.className = 'hint-card open';
      card.innerHTML = `
        <div class="hint-card-header" onclick="this.parentElement.classList.toggle('open')">
          <span>💡 Petunjuk ${hintsUsed + 1}/${hints.length}</span>
          <span style="font-size:.75rem;color:var(--clr-muted);">▾</span>
        </div>
        <div class="hint-card-body">${hints[hintsUsed]}</div>`;
      document.getElementById('hint-section').appendChild(card);
      hintsUsed++;
      const hintBtn = document.getElementById('btn-hint');
      if (hintBtn) {
        const left = hints.length - hintsUsed;
        hintBtn.textContent = left > 0 ? `💡 Hint Berikutnya (${left} tersisa)` : '🚫 Semua Hint Telah Digunakan';
        if (left === 0) hintBtn.disabled = true;
      }
      Mascot.setMood('thinking', '🤔 Semoga petunjuknya membantu!');
    },

    /** Mode latihan: tampilkan pembahasan tanpa menjawab. */
    reveal() {
      const q = questions[idx];
      if (q) revealPembahasan(q);
    },
  };
})();

function showFeedback(success, title, body, actionLabel = 'Lanjut ➔') {
  const bar = document.getElementById('feedback-bar');
  const ttl = document.getElementById('feedback-title');
  const bdy = document.getElementById('feedback-body');
  const btn = document.getElementById('feedback-action-btn');
  if (!bar) return;
  bar.className = `feedback-bar shown ${success ? 'success' : 'error'}`;
  if (ttl) { ttl.textContent = title; ttl.className = success ? 'success-text' : 'error-text'; }
  if (bdy) bdy.innerHTML = body;
  if (btn) btn.textContent = actionLabel;
}
function hideFeedback() {
  const bar = document.getElementById('feedback-bar');
  if (bar) bar.className = 'feedback-bar';
}

/* ════════════════════════════════════════════════════════════════
   DRAWER — Panel materi/kuis
   ════════════════════════════════════════════════════════════════ */
const Drawer = (() => {
  let current = null;      // slug node
  let quizMode = 'level';  // 'level' | 'practice' | 'locked' | 'none'
  let practiceCode = null;

  function setHeader(badge, title, sub) {
    document.getElementById('drawer-badge').textContent = badge || '';
    document.getElementById('drawer-title').textContent = title || '';
    document.getElementById('drawer-sub').textContent = sub || '';
  }

  function setTabs(materiLabel, kuisLabel) {
    const tabs = document.querySelectorAll('.drawer-tab');
    tabs[0].textContent = materiLabel;
    tabs[0].hidden = !materiLabel;
    tabs[1].textContent = kuisLabel || '';
    tabs[1].hidden = !kuisLabel;
  }

  function show() {
    document.getElementById('lesson-drawer').classList.add('open');
    document.querySelector('.drawer-body')?.scrollTo({ top: 0 });
  }

  return {
    /** Dipakai modul Practice (practice.js) untuk mengisi header/tab drawer. */
    ui: { setHeader, setTabs, show },
    setMode(m) { quizMode = m; },

    /**
     * Membuka node. Dari skill tree node terkunci ditolak; dari katalog (browse)
     * materi selalu bisa dibaca, tetapi kuis tetap terkunci.
     * Node kurikulum baru (punya topik) ditangani Practice.openNode().
     */
    open(slug, opts = {}) {
      const node = Curriculum.node(slug);
      if (!node) return;
      const isRef = node.kind === 'reference';
      const status = isRef ? 'active' : State.nodeStatus(slug, Curriculum.tree);

      if (status === 'locked' && !opts.browse) {
        SFX.wrong();
        Mascot.setMood('comfort', '🔒 Selesaikan tahap sebelumnya untuk membuka ini!');
        const el = document.getElementById(`node-${slug}`);
        if (el) { el.classList.add('node-shake'); setTimeout(() => el.classList.remove('node-shake'), 500); }
        return;
      }

      current = slug;
      practiceCode = null;
      if ((node.topics || []).length) {
        quizMode = 'topic';
        Practice.openNode(node, { locked: status === 'locked' });
        return;
      }
      quizMode = isRef ? 'none' : status === 'locked' ? 'locked' : 'level';
      SFX.click();
      setHeader(node.badge_label, node.title, node.subtitle);
      setTabs('📖 Materi', isRef ? '' : `🎯 Kuis (${(node.questions || []).length} soal)`);
      renderSections(document.getElementById('drawer-lesson-content'), node);
      const startBtn = document.getElementById('drawer-start-quiz');
      if (startBtn) startBtn.hidden = isRef;
      this.switchTab('materi');
      show();
      Mascot.setMood('wave', `Selamat datang di <strong>${node.title}</strong>! Pelajari materi dulu ya.`);
    },

    /** Bank Soal: buka satu soal beserta pembahasannya. */
    openQuestion(code) {
      const found = Curriculum.question(code);
      if (!found) return;
      const { q, node } = found;
      current = node.slug;
      practiceCode = code;
      quizMode = 'practice';
      SFX.click();
      setHeader(`Bank Soal · ${q.code}`, q.source, `Latihan dari ${node.title}`);
      setTabs('', '🎯 Soal & Pembahasan');
      this.switchTab('kuis');
      show();
    },

    close() {
      QuizBoard.hide();
      document.getElementById('lesson-drawer').classList.remove('open');
      hideFeedback();
      SFX.click();
    },

    switchTab(tab) {
      document.querySelectorAll('.drawer-tab').forEach((t) => t.classList.toggle('active', t.dataset.tab === tab));
      document.querySelectorAll('.tab-pane').forEach((p) => p.classList.toggle('active', p.id === `tab-${tab}`));
      hideFeedback();
      QuizBoard.hide();
      if (tab !== 'kuis') return;

      const node = Curriculum.node(current);
      const container = document.getElementById('quiz-container');
      if (quizMode === 'topic') {
        Practice.renderSessions();
      } else if (quizMode === 'practice') {
        const { q } = Curriculum.question(practiceCode);
        QuizEngine.start(current, [q], 'practice');
        const actions = container.querySelector('.quiz-actions');
        if (actions) actions.insertAdjacentHTML('beforeend',
          '<button class="btn btn-outline btn-sm" id="btn-reveal" onclick="QuizEngine.reveal()">👀 Lihat Pembahasan</button>');
      } else if (quizMode === 'locked') {
        container.innerHTML = `
          <div class="level-complete">
            <div class="trophy-anim">🔒</div>
            <h3>Kuis masih terkunci</h3>
            <p>Selesaikan tahap sebelumnya di Peta Belajar. Soal tetap bisa dilatih lewat Bank Soal di halaman Lesson.</p>
          </div>`;
      } else if (node) {
        QuizEngine.start(current, node.questions || [], 'level');
      }
    },

    get current() { return current; },
  };
})();

/* ════════════════════════════════════════════════════════════════
   DIAGNOSTIC MODAL — soal dari /api/diagnostic/, dinilai di server
   ════════════════════════════════════════════════════════════════ */
const DiagnosticModal = (() => {
  let step = 0;
  let qs = [];
  let answers = [];

  function container() { return document.getElementById('diag-content'); }

  function render() {
    const q = qs[step];
    const pct = Math.round((step / qs.length) * 100);
    container().innerHTML = `
      <h3 class="diag-title">🧪 Tes Diagnostik</h3>
      <p class="diag-sub">Soal ${step + 1} dari ${qs.length} · <span class="quiz-diff-badge diff-${q.difficulty}">${q.difficulty_label}</span></p>
      <div class="quiz-progress-bar" style="margin-bottom:1.5rem;"><div class="quiz-progress-fill" style="width:${pct}%;"></div></div>
      <div class="quiz-prompt">${q.prompt}</div>
      <div class="options-list">
        ${q.options.map((o, i) => `
          <button class="option-btn" data-opt="${o.id}" onclick="DiagnosticModal.select(${i})">
            <span class="opt-letter">${'ABCDEF'[i]}</span><span>${o.text}</span>
          </button>`).join('')}
      </div>
      <div style="text-align:right;margin-top:1rem;">
        <button class="btn btn-accent" id="diag-submit" onclick="DiagnosticModal.submit()" disabled>Jawab &amp; Lanjut ➔</button>
      </div>`;
  }

  async function finish() {
    container().innerHTML = '<p class="loading-text">Menilai jawaban…</p>';
    const faculty = State.get().faculty;
    let result;
    try {
      const res = await fetch('/api/diagnostic/submit/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ faculty, answers }),
      });
      result = await res.json();
      if (result.status !== 'success') throw new Error(result.message);
    } catch (err) {
      container().innerHTML = `<p class="loading-text">Gagal menilai: ${err.message}</p>`;
      return;
    }

    const cls = { weak_foundation: 'warning', ready_for_calculus: 'ready', mastery: 'mastery' }[result.evaluation] || 'ready';
    if (result.evaluation === 'weak_foundation') {
      Mascot.setMood('comfort', 'Jangan khawatir! Kita perkuat fondasi dulu ya!');
    } else {
      Mascot.setMood('celebrate', 'Kamu siap! Selamat belajar Kalkulus!');
      SFX.fanfare(); Confetti.burst();
    }
    State.addXP(result.xp_awarded || 40);
    if (result.recommended_node) State.startFrom(result.recommended_node, Curriculum.tree);

    container().innerHTML = `
      <div style="text-align:center;padding:1rem 0 .5rem;">
        <div style="font-size:3rem;margin-bottom:.75rem;">✨</div>
        <h3 class="diag-title">Evaluasi Selesai!</h3>
        <div class="diag-result-card ${cls}" style="margin:1.25rem 0;text-align:left;"><p>${result.message}</p></div>
        <div class="diag-summary">
          ${result.results.map((r) => `
            <div>${r.code} (${r.difficulty_label || r.difficulty}):
              <strong style="color:${r.is_correct ? 'var(--clr-growth)' : 'var(--clr-danger)'}">${r.is_correct ? '✅ Benar' : '❌ Salah'}</strong>
              — Jawaban: ${r.answer || ''}</div>`).join('')}
        </div>
        <button class="btn btn-primary btn-lg" style="margin-top:1.25rem;" onclick="DiagnosticModal.close(); Nav.go('levelup');">
          Lihat Peta Belajar 🗺️
        </button>
      </div>`;
  }

  return {
    async open() {
      step = 0; answers = []; qs = [];
      document.getElementById('diagnostic-modal').classList.add('open');
      container().innerHTML = '<p class="loading-text">Menyiapkan soal…</p>';
      SFX.click();
      Mascot.setMood('thinking', 'Ayo ukur kemampuan dasarmu! Santai saja 😊');
      try {
        const res = await fetch(`/api/diagnostic/?faculty=${encodeURIComponent(State.get().faculty)}`);
        qs = (await res.json()).questions || [];
      } catch (_) { qs = []; }
      if (!qs.length) { container().innerHTML = '<p class="loading-text">Soal diagnostik belum tersedia.</p>'; return; }
      render();
    },
    close() {
      document.getElementById('diagnostic-modal').classList.remove('open');
      SFX.click();
    },
    select(i) {
      SFX.click();
      container().querySelectorAll('.option-btn').forEach((b, j) => b.classList.toggle('selected', j === i));
      const sb = document.getElementById('diag-submit');
      if (sb) { sb.dataset.sel = i; sb.removeAttribute('disabled'); }
    },
    submit() {
      const sb = document.getElementById('diag-submit');
      if (!sb || sb.disabled) return;
      const q = qs[step];
      answers.push({ code: q.code, option_id: q.options[parseInt(sb.dataset.sel, 10)].id });
      step++;
      if (step < qs.length) render();
      else finish();
    },
  };
})();

/* ════════════════════════════════════════════════════════════════
   CONFETTI — Canvas particle burst
   ════════════════════════════════════════════════════════════════ */
const Confetti = (() => ({
  burst() {
    const canvas = document.getElementById('confetti-canvas');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;

    const colors = ['#2563EB', '#16A34A', '#F97316', '#D97706', '#EC4899', '#38BDF8'];
    const pts = Array.from({ length: 80 }, () => ({
      x: canvas.width / 2, y: canvas.height / 2,
      vx: (Math.random() - .5) * 14,
      vy: (Math.random() - .9) * 15,
      r: Math.random() * 6 + 3,
      color: colors[Math.floor(Math.random() * colors.length)],
      angle: Math.random() * 6,
    }));

    let f = 0;
    function draw() {
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      pts.forEach(p => {
        p.vy += .35; p.x += p.vx; p.y += p.vy; p.angle += .08;
        ctx.save();
        ctx.translate(p.x, p.y);
        ctx.rotate(p.angle);
        ctx.fillStyle = p.color;
        ctx.fillRect(-p.r / 2, -p.r / 2, p.r, p.r * .5);
        ctx.restore();
      });
      if (++f < 110) requestAnimationFrame(draw);
      else ctx.clearRect(0, 0, canvas.width, canvas.height);
    }
    draw();
  }
}))();

/* ════════════════════════════════════════════════════════════════
   BOOT
   ════════════════════════════════════════════════════════════════ */
document.addEventListener('DOMContentLoaded', () => {
  State.updateHUD();
  Curriculum.load(State.get().faculty);
  SFX.toggle(); SFX.toggle(); // init sound state from saved
});
