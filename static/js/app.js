/**
 * Calculus Bridge — App Engine v3
 * Modules:
 *   SFX           – Web Audio synthesizer
 *   State         – LocalStorage game state
 *   Nav           – Bottom nav + sidebar routing
 *   Mascot        – Reactive SVG character
 *   Drawer        – Lesson/Quiz slide-in sheet
 *   QuizEngine    – Progressive-hint quiz system
 *   DiagnosticModal – Adaptive 3-question diagnostic
 *   Confetti      – Canvas particle burst
 */

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
   ════════════════════════════════════════════════════════════════ */
const State = (() => {
  const KEY = 'cb_state_v3';
  const DEFAULTS = {
    faculty: 'fasilkom',
    xp: 60, streak: 3, hearts: 5, maxHearts: 5, gems: 120,
    completedNodes: ['node-precalc'],
    activeNode: 'node-limit',
    sound: true,
  };

  let s = (() => {
    try { return Object.assign({}, DEFAULTS, JSON.parse(localStorage.getItem(KEY))); }
    catch (_) { return { ...DEFAULTS }; }
  })();

  function save() {
    try { localStorage.setItem(KEY, JSON.stringify(s)); } catch (_) { }
    updateHUD();
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

    const facLabels = { fasilkom: '💻 Fasilkom', fmipa: '🔬 FMIPA', ft: '⚙️ Fak. Teknik' };
    setText('hud-faculty-badge', facLabels[s.faculty] || 'Fasilkom');

    // Sidebar active
    ['fasilkom', 'fmipa', 'ft'].forEach(f => {
      const el = document.getElementById(`sidebar-${f}`);
      if (el) el.classList.toggle('active', f === s.faculty);
    });
    // Faculty cards (profile page)
    document.querySelectorAll('.fac-card').forEach(c => {
      c.classList.toggle('active', c.dataset.fac === s.faculty);
    });
    // Tree nodes
    updateTree();
  }

  function updateTree() {
    document.querySelectorAll('.tree-node').forEach(n => {
      n.classList.remove('node-completed', 'node-active', 'node-locked');
      if (s.completedNodes.includes(n.id)) n.classList.add('node-completed');
      else if (n.id === s.activeNode) n.classList.add('node-active');
      else n.classList.add('node-locked');
    });
  }

  function setText(id, val) {
    const el = document.getElementById(id);
    if (el) el.textContent = val;
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
    addXP(n) { s.xp += n; save(); floatXP(n); },
    loseHeart() {
      if (s.hearts > 0) { s.hearts--; save(); SFX.wrong(); }
      const p = document.getElementById('hud-hearts-pill');
      if (p) { p.classList.add('hearts-shake'); setTimeout(() => p.classList.remove('hearts-shake'), 500); }
    },
    setFaculty(f) {
      s.faculty = f; save(); SFX.click();
      const facDescs = {
        fasilkom: 'Jalur <strong>Fasilkom</strong> — Gradient Descent, Limit Kompleksitas & Turunan Numerik',
        fmipa: 'Jalur <strong>FMIPA</strong> — Pembuktian ε-δ, MVT & Analisis Formal Ketat',
        ft: 'Jalur <strong>Fak. Teknik</strong> — Laju Terkait, Optimasi Struktur & Kalkulus Vektor',
      };
      setText('tree-fac-desc', '');
      const el = document.getElementById('tree-fac-desc');
      if (el) el.innerHTML = facDescs[f] || '';
    },
    completeNode(nodeId, nextId) {
      if (!s.completedNodes.includes(nodeId)) s.completedNodes.push(nodeId);
      if (nextId) s.activeNode = nextId;
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
   LEVEL DATA — Curriculum content (materi + kuis + hints)
   ════════════════════════════════════════════════════════════════ */
const LEVELS = {
  'node-precalc': {
    badge: 'Tahap 1', title: 'Precalculus Bridge', sub: 'Pemfaktoran & Manipulasi Aljabar',
    nextNode: 'node-limit',
    lesson: `
      <div class="lesson-block">
        <h4>Mengapa Precalculus Penting?</h4>
        <p>90% kesalahan kalkulus bukan pada rumus turunannya, melainkan kegagalan memanipulasi aljabar dasar. Kuasai ini dulu!</p>
      </div>
      <div class="formula-box">
        <code>a² - b² = (a - b)(a + b)</code>
        <span>Selisih Dua Kuadrat — paling sering muncul di soal limit</span>
      </div>
      <div class="formula-box">
        <code>a³ - b³ = (a - b)(a² + ab + b²)</code>
        <span>Selisih Dua Kubik</span>
      </div>
      <div class="video-card">
        <div class="video-play">▶</div>
        <div class="video-info">
          <strong>Rahasia Aljabar Mahasiswa Baru UI</strong>
          <span>Durasi: 08:45 · Dosen Pengampu Kalkulus</span>
        </div>
      </div>`,
    quiz: [
      {
        q: 'Sederhanakan untuk x ≠ 3: (x² - 9) / (x - 3)',
        diff: 'basic',
        options: ['x - 3', 'x + 3', '3x', 'x² + 3'],
        correct: 1,
        hints: [
          '💡 Coba lihat pembilangnya — apakah x² - 9 bisa difaktorkan?',
          '📐 Ingat rumus: a² - b² = (a-b)(a+b). Di sini a = x, b = 3.',
          '✂️ Setelah difaktorkan: (x-3)(x+3)/(x-3). Sekarang apa yang bisa disederhanakan?',
        ],
        explanation: 'Pembilang x² - 9 = (x-3)(x+3). Dibagi (x-3) → tersisa (x+3). Jadi jawabannya x + 3.'
      },
      {
        q: 'Jika f(x) = 2x + 1, berapakah f(x+h) - f(x)?',
        diff: 'basic',
        options: ['2h', '2x + 2h', 'h', '2h + 1'],
        correct: 0,
        hints: [
          '💡 Hitung f(x+h) dulu: masukkan (x+h) sebagai pengganti x dalam f(x) = 2x + 1.',
          '📐 f(x+h) = 2(x+h) + 1 = 2x + 2h + 1.',
          '✂️ Sekarang kurangi f(x): f(x+h) - f(x) = (2x + 2h + 1) - (2x + 1) = ?',
        ],
        explanation: 'f(x+h) = 2(x+h)+1 = 2x+2h+1. Dikurangi f(x) = 2x+1 → hasilnya 2h.'
      }
    ]
  },
  'node-limit': {
    badge: 'Tahap 2', title: 'Limit & Kekontinuan', sub: 'Intuisi Mendekati Nilai Fungsi',
    nextNode: 'node-deriv',
    lesson: `
      <div class="lesson-block">
        <h4>Intuisi Limit: "Mendekati, Bukan Menyentuh"</h4>
        <p>Limit f(x) saat x → c adalah nilai L yang dituju oleh f(x) ketika x bergerak sangat dekat ke c dari kiri maupun kanan, tanpa harus tepat di c.</p>
      </div>
      <div class="formula-box">
        <code>lim_{x→0} sin(x)/x = 1</code>
        <span>Teorema limit trigonometri fundamental — hafal ini!</span>
      </div>
      <div class="formula-box">
        <code>Bentuk 0/0 → Faktorkan → Kurangkan → Substitusi</code>
        <span>Strategi utama menghadapi bentuk tak tentu</span>
      </div>
      <div class="video-card">
        <div class="video-play">▶</div>
        <div class="video-info">
          <strong>Intuisi Limit & Garis Singgung</strong>
          <span>Durasi: 12:10 · Visualisasi Interaktif</span>
        </div>
      </div>`,
    quiz: [
      {
        q: 'Hitung: lim_{x→3} (x² - 9) / (x - 3)',
        diff: 'medium',
        options: ['0', '6', '3', 'Tak terdefinisi'],
        correct: 1,
        hints: [
          '💡 Coba substitusi x=3 langsung. Apa yang terjadi pada pembilang dan penyebut?',
          '📐 Kamu mendapat 0/0 (bentuk tak tentu). Strategi: faktorkan pembilangnya terlebih dahulu.',
          '✂️ x² - 9 = (x-3)(x+3). Coret faktor (x-3), lalu substitusi x=3 ke (x+3).',
        ],
        explanation: 'Faktorkan (x-3)(x+3)/(x-3) = x+3. Substitusi x=3 → 3+3 = 6.'
      },
      {
        q: 'Suatu fungsi f(x) kontinu di x = c jika...',
        diff: 'medium',
        options: [
          'f(c) ada, lim ada, dan lim = f(c)',
          'Grafiknya berupa garis lurus',
          'f(c) > 0',
          'Turunan keduanya nol'
        ],
        correct: 0,
        hints: [
          '💡 Kontinuitas punya 3 syarat ketat. Syarat pertama: apakah f(c) terdefinisi?',
          '📐 Syarat kedua: apakah lim_{x→c} f(x) ada (limit kiri = limit kanan)?',
          '✂️ Syarat ketiga: apakah nilai limit sama dengan nilai fungsinya di c?',
        ],
        explanation: 'Tiga syarat kontinuitas: (1) f(c) ada, (2) lim_{x→c} f(x) ada, (3) keduanya sama nilainya.'
      }
    ]
  },
  'node-deriv': {
    badge: 'Tahap 3', title: 'Dasar Turunan', sub: 'Laju Perubahan Sesaat & Power Rule',
    nextNode: 'node-chain',
    lesson: `
      <div class="lesson-block">
        <h4>Definisi Limit Turunan</h4>
        <p>f'(x) = lim_{h→0} [f(x+h) - f(x)] / h. Ini adalah kemiringan garis singgung di titik x — seperti speedometer sesaat.</p>
      </div>
      <div class="formula-box">
        <code>d/dx [xⁿ] = n · xⁿ⁻¹</code>
        <span>Power Rule — berlaku untuk semua n real</span>
      </div>`,
    quiz: [
      {
        q: "Tentukan turunan: f(x) = 5x⁴ - 3x² + 7",
        diff: 'medium',
        options: ['20x³ - 6x', '20x⁴ - 6x²', '5x³ - 3x', '20x³ - 6x + 7'],
        correct: 0,
        hints: [
          '💡 Gunakan Power Rule: d/dx[xⁿ] = n·xⁿ⁻¹. Turunkan tiap suku secara terpisah.',
          '📐 d/dx(5x⁴) = 5·4·x³ = 20x³',
          '✂️ d/dx(-3x²) = -3·2·x = -6x, dan d/dx(7) = 0 (konstanta).',
        ],
        explanation: 'd/dx(5x⁴) = 20x³, d/dx(-3x²) = -6x, d/dx(7) = 0. Total: 20x³ - 6x.'
      }
    ]
  },
  'node-chain': {
    badge: 'Tahap 4', title: 'Aturan Rantai', sub: 'Turunan Fungsi Komposisi f(g(x))',
    nextNode: 'node-app',
    lesson: `
      <div class="lesson-block">
        <h4>Aturan Rantai: Kupas Kulit Buah</h4>
        <p>Turunkan fungsi terluar dengan membiarkan fungsi dalam tetap, lalu kalikan turunan fungsi dalamnya.</p>
      </div>
      <div class="formula-box">
        <code>d/dx[f(g(x))] = f'(g(x)) · g'(x)</code>
        <span>Chain Rule — kunci turunan fungsi bersarang</span>
      </div>`,
    quiz: [
      {
        q: 'Jika y = sin(3x²), maka dy/dx adalah...',
        diff: 'high',
        options: ['6x·cos(3x²)', 'cos(3x²)', '6x·sin(3x²)', '3x²·cos(6x)'],
        correct: 0,
        hints: [
          '💡 Ini fungsi komposisi: f(u) = sin(u) dan g(x) = 3x². Turunkan f dulu.',
          '📐 Turunan sin(u) = cos(u). Jadi f\'(g(x)) = cos(3x²).',
          '✂️ Sekarang kalikan dengan g\'(x). g(x) = 3x², maka g\'(x) = 6x.',
        ],
        explanation: 'Turunan terluar sin → cos. Turunan dalam 3x² → 6x. Hasil: 6x·cos(3x²).'
      }
    ]
  },
  'node-app': {
    badge: 'Tahap 5', title: 'Aplikasi & Optimasi', sub: 'Nilai Maks, Min & Desain Efisien',
    nextNode: null,
    lesson: `
      <div class="lesson-block">
        <h4>Mencari Nilai Ekstrem</h4>
        <p>Titik kritis terjadi ketika f'(x) = 0 atau tidak ada. Uji f''(x): positif = minimum, negatif = maksimum.</p>
      </div>`,
    quiz: [
      {
        q: 'Nilai x yang meminimumkan C(x) = 2x² - 8x + 50 adalah...',
        diff: 'high',
        options: ['x = 2', 'x = 4', 'x = -2', 'x = 0'],
        correct: 0,
        hints: [
          '💡 Cari titik kritis: turunkan C(x) dan set C\'(x) = 0.',
          '📐 C\'(x) = 4x - 8 = 0. Selesaikan untuk x.',
          '✂️ 4x = 8 → x = 2. Konfirmasi: C\'\'(2) = 4 > 0 → titik minimum.',
        ],
        explanation: 'C\'(x) = 4x - 8 = 0 → x = 2. C\'\'(2) = 4 > 0 membuktikan x = 2 adalah minimum lokal.'
      }
    ]
  },
  'node-boss': {
    badge: 'Boss Quest', title: 'Ujian Akhir Kalkulus', sub: 'Tantangan Gabungan Semua Topik',
    nextNode: null,
    lesson: `<div class="lesson-block"><h4>🏆 Kamu hampir di puncak!</h4><p>Selesaikan semua tahap terlebih dahulu untuk membuka Boss Quest ini.</p></div>`,
    quiz: []
  }
};

/* ════════════════════════════════════════════════════════════════
   QUIZ ENGINE — Progressive hint system
   ════════════════════════════════════════════════════════════════ */
const QuizEngine = (() => {
  let nodeId = null;
  let questions = [];
  let idx = 0;
  let hintsUsed = 0;
  let answered = false;

  function render() {
    const container = document.getElementById('quiz-container');
    if (!container) return;

    if (idx >= questions.length) { showComplete(); return; }

    const q = questions[idx];
    const progress = Math.round((idx / questions.length) * 100);
    answered = false;
    hintsUsed = 0;

    container.innerHTML = `
      <div class="quiz-wrap">
        <div class="quiz-progress-bar">
          <div class="quiz-progress-fill" id="qpf" style="width:${progress}%"></div>
        </div>
        <div class="quiz-meta">
          <span class="quiz-num">Soal ${idx + 1} dari ${questions.length}</span>
          <span class="quiz-diff-badge diff-${q.diff}">${diffLabel(q.diff)}</span>
        </div>
        <div class="quiz-prompt">${q.q}</div>

        <div class="options-list" id="options-list">
          ${q.options.map((o, i) => `
            <button class="option-btn" id="opt-${i}" onclick="QuizEngine.select(${i})">
              <span class="opt-letter">${'ABCD'[i]}</span>
              ${o}
            </button>`).join('')}
        </div>

        <div class="quiz-actions">
          <button class="btn btn-accent btn-sm" id="btn-hint" onclick="QuizEngine.showNextHint()">
            💡 Minta Hint (${q.hints.length} tersedia)
          </button>
          <button class="btn btn-primary" id="btn-submit" onclick="QuizEngine.submit()" disabled>
            ✅ Jawab
          </button>
        </div>

        <!-- Progressive Hints (collapsed by default) -->
        <div class="hint-section" id="hint-section"></div>

        <!-- Full explanation — revealed only after answer -->
        <div class="full-explanation" id="full-explanation">
          <h5>📚 Langkah Penyelesaian Lengkap</h5>
          <p>${q.explanation}</p>
        </div>
      </div>`;

    hideFeedback();
  }

  function diffLabel(d) {
    return { basic: 'Dasar', medium: 'Menengah', high: 'Tinggi' }[d] || d;
  }

  return {
    init(nid) {
      nodeId = nid;
      questions = (LEVELS[nid] || {}).quiz || [];
      idx = 0;
      render();
    },

    select(i) {
      if (answered) return;
      SFX.click();
      document.querySelectorAll('.option-btn').forEach((b, j) => {
        b.classList.toggle('selected', j === i);
      });
      const btn = document.getElementById('btn-submit');
      if (btn) { btn.dataset.sel = i; btn.removeAttribute('disabled'); }
    },

    submit() {
      if (answered) return;
      const btn = document.getElementById('btn-submit');
      if (!btn || btn.disabled) return;
      const sel = parseInt(btn.dataset.sel);
      const q = questions[idx];
      const correct = q.correct;
      answered = true;

      // Mark options
      document.querySelectorAll('.option-btn').forEach((b, j) => {
        if (j === correct) b.classList.add('correct');
        else if (j === sel && j !== correct) b.classList.add('incorrect');
        b.disabled = true;
      });

      // Reveal full explanation now
      const expl = document.getElementById('full-explanation');
      if (expl) expl.classList.add('revealed');

      if (sel === correct) {
        SFX.correct();
        State.addXP(20);
        Mascot.setMood('celebrate', '🎉 Jawaban tepat! Luar biasa!');
        showFeedback(true, '+20 XP — Jawaban Tepat!', q.explanation);
      } else {
        SFX.wrong();
        State.loseHeart();
        Mascot.setMood('comfort', 'Jangan menyerah! Baca pembahasannya ya.');
        showFeedback(false, 'Belum tepat (-1 Nyawa)', q.explanation);
      }
    },

    nextQuestion() {
      hideFeedback();
      idx++;
      render();
    },

    showNextHint() {
      const q = questions[idx];
      if (!q || hintsUsed >= q.hints.length) return;
      SFX.hint();

      const section = document.getElementById('hint-section');
      const hint = q.hints[hintsUsed];

      const card = document.createElement('div');
      card.className = 'hint-card open';
      card.innerHTML = `
        <div class="hint-card-header" onclick="this.parentElement.classList.toggle('open')">
          <span>💡 Petunjuk ${hintsUsed + 1}/${q.hints.length}</span>
          <span style="font-size:.75rem;color:var(--clr-muted);">▾</span>
        </div>
        <div class="hint-card-body">${hint}</div>`;
      section.appendChild(card);

      hintsUsed++;

      // Update button label
      const hintBtn = document.getElementById('btn-hint');
      if (hintBtn) {
        const left = q.hints.length - hintsUsed;
        hintBtn.textContent = left > 0
          ? `💡 Hint Berikutnya (${left} tersisa)`
          : '🚫 Semua Hint Telah Digunakan';
        if (left === 0) hintBtn.disabled = true;
      }

      Mascot.setMood('thinking', '🤔 Semoga petunjuknya membantu!');
    },
  };
})();

function showFeedback(success, title, body) {
  const bar = document.getElementById('feedback-bar');
  const ttl = document.getElementById('feedback-title');
  const bdy = document.getElementById('feedback-body');
  if (!bar) return;
  bar.className = `feedback-bar shown ${success ? 'success' : 'error'}`;
  if (ttl) { ttl.textContent = title; ttl.className = success ? 'success-text' : 'error-text'; }
  if (bdy) bdy.textContent = body;
}
function hideFeedback() {
  const bar = document.getElementById('feedback-bar');
  if (bar) bar.className = 'feedback-bar';
}

function showComplete() {
  const container = document.getElementById('quiz-container');
  if (!container) return;

  SFX.fanfare();
  Confetti.burst();
  Mascot.setMood('celebrate', '🏆 Selamat! Level ini berhasil kamu taklukkan!');
  State.addXP(50);

  const lv = LEVELS[QuizEngine._nodeId] || {};
  const nextId = (LEVELS[container.dataset?.nodeId] || {}).nextNode || null;

  container.innerHTML = `
    <div class="level-complete">
      <div class="trophy-anim">🏆</div>
      <h3>Level Selesai!</h3>
      <p>Kamu mendapatkan <strong>+50 Bonus XP</strong> dan membuka level berikutnya!</p>
      <button class="btn btn-growth btn-lg" onclick="Drawer.close()">
        Kembali ke Peta Belajar 🗺️
      </button>
    </div>`;
}

/* ════════════════════════════════════════════════════════════════
   DRAWER — Slide-in lesson/quiz panel
   ════════════════════════════════════════════════════════════════ */
const Drawer = (() => {
  let currentNode = null;

  return {
    open(nodeId) {
      const s = State.get();
      const isOk = s.completedNodes.includes(nodeId) || s.activeNode === nodeId;

      if (!isOk && nodeId !== 'node-boss') {
        SFX.wrong();
        Mascot.setMood('comfort', '🔒 Selesaikan tahap sebelumnya untuk membuka ini!');
        const el = document.getElementById(nodeId);
        if (el) { el.classList.add('node-shake'); setTimeout(() => el.classList.remove('node-shake'), 500); }
        return;
      }

      currentNode = nodeId;
      const lv = LEVELS[nodeId] || {};
      SFX.click();

      document.getElementById('drawer-badge').textContent = lv.badge || '';
      document.getElementById('drawer-title').textContent = lv.title || '';
      document.getElementById('drawer-sub').textContent = lv.sub || '';
      document.getElementById('drawer-lesson-content').innerHTML = lv.lesson || '';

      this.switchTab('materi');
      document.getElementById('lesson-drawer').classList.add('open');
      Mascot.setMood('wave', `Selamat datang di <strong>${lv.title}</strong>! Pelajari materi dulu ya.`);
    },

    close() {
      document.getElementById('lesson-drawer').classList.remove('open');
      hideFeedback();
      SFX.click();
    },

    switchTab(tab) {
      SFX.click();
      document.querySelectorAll('.drawer-tab').forEach(t => {
        t.classList.toggle('active', t.dataset.tab === tab);
      });
      document.querySelectorAll('.tab-pane').forEach(p => {
        p.classList.toggle('active', p.id === `tab-${tab}`);
      });
      if (tab === 'kuis') {
        QuizEngine.init(currentNode);
      }
      hideFeedback();
    },

    get current() { return currentNode; },
  };
})();

// Expose nextQuestion on QuizEngine for feedback button
QuizEngine.nextQuestion = QuizEngine.nextQuestion || function () { };

/* ════════════════════════════════════════════════════════════════
   DIAGNOSTIC MODAL
   ════════════════════════════════════════════════════════════════ */
const DIAG_QUESTIONS = {
  fasilkom: [
    {
      level: 'Dasar', diff: 'basic',
      q: 'Sederhanakan untuk x ≠ 3: (x² - 9) / (x - 3)',
      opts: ['x - 3', 'x + 3', '3x', 'x² + 3'], correct: 1,
      expl: 'x² - 9 = (x-3)(x+3). Dibagi (x-3) → x + 3.'
    },
    {
      level: 'Menengah', diff: 'medium',
      q: 'lim_{x→2} (x² + x - 6) / (x - 2) = ?',
      opts: ['0', '5', '4', 'Tak terdefinisi'], correct: 1,
      expl: 'Faktorkan: (x+3)(x-2)/(x-2) = x+3. Substitusi x=2 → 5.'
    },
    {
      level: 'Tinggi', diff: 'high',
      q: "f(x) = (3x² + 1)³ → f'(x) = ?",
      opts: ['9(3x²+1)²', '18x(3x²+1)²', '6x(3x²+1)²', '3(6x)²'], correct: 1,
      expl: 'Chain Rule: 3(3x²+1)² · 6x = 18x(3x²+1)².'
    }
  ]
};

const DiagnosticModal = (() => {
  let step = 0, answers = [];

  function render() {
    const fac = State.get().faculty;
    const qs = DIAG_QUESTIONS[fac] || DIAG_QUESTIONS.fasilkom;
    const q = qs[step];
    const pct = Math.round((step / qs.length) * 100);
    const container = document.getElementById('diag-content');
    if (!container) return;

    container.innerHTML = `
      <h3 style="font-family:var(--font-head);font-size:1.3rem;margin-bottom:.5rem;">🧪 Tes Diagnostik</h3>
      <p style="font-size:.88rem;color:var(--clr-text-sec);margin-bottom:1.25rem;">
        Soal ${step + 1} dari ${qs.length}  •  <span class="quiz-diff-badge diff-${q.diff}" style="display:inline;">${q.level}</span>
      </p>
      <div class="quiz-progress-bar" style="margin-bottom:1.5rem;">
        <div class="quiz-progress-fill" style="width:${pct}%;"></div>
      </div>
      <div class="quiz-prompt">${q.q}</div>
      <div class="options-list" id="diag-opts">
        ${q.opts.map((o, i) => `
          <button class="option-btn" id="dopt-${i}" onclick="DiagnosticModal.select(${i})">
            <span class="opt-letter">${'ABCD'[i]}</span>${o}
          </button>`).join('')}
      </div>
      <div style="text-align:right;margin-top:1rem;">
        <button class="btn btn-accent" id="diag-submit" onclick="DiagnosticModal.submit()" disabled>
          Jawab & Lanjut ➔
        </button>
      </div>`;
  }

  return {
    open() {
      step = 0; answers = [];
      Mascot.setMood('thinking', 'Ayo ukur kemampuan dasarmu! Santai saja 😊');
      document.getElementById('diagnostic-modal').classList.add('open');
      SFX.click();
      render();
    },
    close() {
      document.getElementById('diagnostic-modal').classList.remove('open');
      SFX.click();
    },
    select(i) {
      SFX.click();
      document.querySelectorAll('.option-btn[id^=dopt]').forEach((b, j) => {
        b.classList.toggle('selected', j === i);
      });
      const sb = document.getElementById('diag-submit');
      if (sb) { sb.dataset.sel = i; sb.removeAttribute('disabled'); }
    },
    submit() {
      const fac = State.get().faculty;
      const qs = DIAG_QUESTIONS[fac] || DIAG_QUESTIONS.fasilkom;
      const sb = document.getElementById('diag-submit');
      if (!sb || sb.disabled) return;
      const sel = parseInt(sb.dataset.sel);
      answers.push({ diff: qs[step].diff, correct: sel === qs[step].correct });
      step++;
      if (step < qs.length) { render(); return; }

      // Evaluate
      const basicOk = answers.find(a => a.diff === 'basic')?.correct ?? false;
      const highOk = answers.find(a => a.diff === 'high')?.correct ?? false;
      let rec = 'node-limit', msg = '', cls = 'ready';

      if (!basicOk) {
        rec = 'node-precalc'; cls = 'warning';
        msg = '🛡️ Fondasi aljabar perlu diperkuat. Jalur Precalculus Bridge disiapkan untukmu.';
        Mascot.setMood('comfort', 'Jangan khawatir! Kita perkuat fondasi dulu ya!');
      } else if (!highOk) {
        msg = '🚀 Fondasi kuat! Langsung masuk Kalkulus 1 — Limit & Turunan.';
        Mascot.setMood('celebrate', 'Kamu siap! Selamat belajar Kalkulus!');
        SFX.fanfare(); Confetti.burst();
      } else {
        rec = 'node-chain'; cls = 'mastery';
        msg = '👑 Penguasaan tinggi! Jalur Akselerasi Aturan Rantai terbuka.';
        Mascot.setMood('celebrate', 'Wow, kamu berbakat! 🌟');
        SFX.fanfare(); Confetti.burst();
      }

      State.addXP(40);
      const st = State.get(); st.activeNode = rec;
      State.save();

      document.getElementById('diag-content').innerHTML = `
        <div style="text-align:center;padding:1rem 0 .5rem;">
          <div style="font-size:3rem;margin-bottom:.75rem;">✨</div>
          <h3 style="font-family:var(--font-head);margin-bottom:.5rem;">Evaluasi Selesai!</h3>
          <div class="diag-result-card ${cls}" style="margin:1.25rem 0;text-align:left;">
            <p>${msg}</p>
          </div>
          <div style="margin-top:.5rem;padding:.6rem;background:var(--clr-cream);border-radius:var(--radius-md);font-size:.85rem;color:var(--clr-text-sec);">
            ${answers.map((a, i) => `<div>${qs[i].level}: <strong style="color:${a.correct ? 'var(--clr-growth)' : 'var(--clr-danger)'}">${a.correct ? '✅ Benar' : '❌ Salah'}</strong> — ${qs[i].expl}</div>`).join('')}
          </div>
          <button class="btn btn-primary btn-lg" style="margin-top:1.25rem;" onclick="DiagnosticModal.close(); Nav.go('levelup');">
            Lihat Peta Belajar 🗺️
          </button>
        </div>`;
    }
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
  SFX.toggle(); SFX.toggle(); // init sound state from saved
});
