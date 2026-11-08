/* ════════════════════════════════════════════════════════════════
   FREE PRACTICE — Latihan Bebas: tanpa nyawa, tanpa XP, murni latihan.
   Alur: fakultas → level → topik (boleh banyak) → jumlah soal (1–15) → mulai.
   Soal diambil dari /api/latihan-bebas/mulai/ (acak tiap kali) lalu dijalankan
   QuizEngine mode 'free' di drawer; penilaian dilakukan di browser.
   ════════════════════════════════════════════════════════════════ */
const FreePractice = (() => {
  const FACULTIES = [['fasilkom', '💻 Fasilkom'], ['fmipa', '🔬 FMIPA'], ['ft', '⚙️ Fak. Teknik']];
  const MAX = 15;
  const catalogs = {};          // { faculty: [level...] } dari server
  const sel = { faculty: null, level: null, topics: new Set(), count: 10 };
  let questions = [];

  const esc = (t) => String(t).replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
  const root = () => document.getElementById('free-practice-root');
  const levels = () => catalogs[sel.faculty] || [];
  const level = () => levels().find((l) => l.slug === sel.level);

  async function loadCatalog(fac) {
    if (catalogs[fac]) return;
    const res = await fetch(`/api/latihan-bebas/?faculty=${encodeURIComponent(fac)}`);
    const data = await res.json();
    if (!res.ok) throw new Error(data.message || `HTTP ${res.status}`);
    catalogs[fac] = data.levels;
  }

  /** Tampilkan halaman pemilihan (dipanggil saat tab Latihan dibuka). */
  async function render() {
    const box = root();
    if (!box) return;
    sel.faculty = sel.faculty || State.get().faculty || 'fasilkom';
    try {
      await loadCatalog(sel.faculty);
    } catch (err) {
      box.innerHTML = `<p class="loading-text">Gagal memuat materi: ${esc(err.message)}</p>`;
      return;
    }
    if (!level()) { sel.level = levels()[0]?.slug || null; sel.topics.clear(); }
    const lv = level();
    const canStart = sel.topics.size > 0 && sel.count > 0;

    box.innerHTML = `
      <section class="fp-step">
        <h3 class="fp-step-title">1. Pilih jalur</h3>
        <div class="fp-options">${FACULTIES.map(([slug, label]) => `
          <button class="btn btn-sm ${slug === sel.faculty ? 'btn-primary' : 'btn-outline'}"
                  onclick="FreePractice.setFaculty('${slug}')">${label}</button>`).join('')}
        </div>
      </section>

      <section class="fp-step">
        <h3 class="fp-step-title">2. Pilih level</h3>
        <div class="fp-options">${levels().map((l) => `
          <button class="btn btn-sm ${l.slug === sel.level ? 'btn-primary' : 'btn-outline'}"
                  onclick="FreePractice.setLevel('${l.slug}')">${l.icon || ''} ${esc(l.title)}</button>`).join('')}
        </div>
      </section>

      <section class="fp-step">
        <div class="fp-step-head">
          <h3 class="fp-step-title">3. Pilih materi <small>(boleh lebih dari satu)</small></h3>
          <span>
            <button class="btn btn-outline btn-sm" onclick="FreePractice.selectAll(true)">Pilih semua</button>
            <button class="btn btn-outline btn-sm" onclick="FreePractice.selectAll(false)">Kosongkan</button>
          </span>
        </div>
        <div class="fp-topics">${(lv ? lv.topics : []).map((t) => `
          <label class="fp-topic ${sel.topics.has(t.slug) ? 'on' : ''}">
            <input type="checkbox" ${sel.topics.has(t.slug) ? 'checked' : ''} onchange="FreePractice.toggle('${t.slug}')">
            <span>${t.icon || '📘'} ${esc(t.title)}</span>
          </label>`).join('')}
        </div>
      </section>

      <section class="fp-step">
        <h3 class="fp-step-title">4. Jumlah soal: <b id="fp-count-val">${sel.count}</b></h3>
        <input type="range" class="fp-range" min="0" max="${MAX}" step="1" value="${sel.count}"
               oninput="FreePractice.setCount(this.value)">
        <div class="fp-range-scale"><span>0</span><span>${MAX}</span></div>
      </section>

      <button class="btn btn-growth btn-lg fp-start" id="fp-start" ${canStart ? '' : 'disabled'} onclick="FreePractice.start()">
        Mulai Latihan ➔</button>
      <p class="graph-hint" id="fp-hint">${canStart ? `${sel.count} soal dari ${sel.topics.size} materi.`
        : 'Pilih minimal satu materi dan jumlah soal lebih dari 0.'}</p>`;
  }

  /** Perbarui tombol mulai tanpa menggambar ulang seluruh halaman (agar slider tetap halus). */
  function refreshStart() {
    const ok = sel.topics.size > 0 && sel.count > 0;
    const btn = document.getElementById('fp-start');
    if (btn) btn.disabled = !ok;
    const hint = document.getElementById('fp-hint');
    if (hint) hint.textContent = ok ? `${sel.count} soal dari ${sel.topics.size} materi.`
      : 'Pilih minimal satu materi dan jumlah soal lebih dari 0.';
  }

  async function start() {
    if (!sel.topics.size || !sel.count) return;
    SFX.click();
    const lv = level();
    const titles = lv.topics.filter((t) => sel.topics.has(t.slug)).map((t) => t.title);
    Drawer.setMode('free');
    Drawer.ui.setHeader('🎯 Latihan Bebas · tanpa nyawa & XP', lv.title,
      titles.length > 3 ? `${titles.slice(0, 3).join(', ')} +${titles.length - 3} materi` : titles.join(', '));
    Drawer.ui.setTabs('', `🎯 ${sel.count} soal`);
    Drawer.ui.show();
    document.getElementById('quiz-container').innerHTML = '<p class="loading-text">Mengacak soal untukmu…</p>';
    Drawer.switchTab('kuis');
  }

  /** Dipanggil Drawer.switchTab('kuis') saat mode 'free': ambil soal baru lalu jalankan kuis. */
  async function renderQuiz() {
    const box = document.getElementById('quiz-container');
    try {
      const data = await postJSON('/api/latihan-bebas/mulai/',
        { faculty: sel.faculty, topics: [...sel.topics], count: sel.count });
      questions = data.questions;
      QuizEngine.start('free', questions, 'free');
      Mascot.setMood('thinking', '🎯 Latihan bebas: santai saja, tidak ada nyawa yang hilang!');
    } catch (err) {
      box.innerHTML = `<p class="loading-text">Gagal memuat soal: ${esc(err.message)}</p>`;
    }
  }

  /** Ringkasan akhir: skor total dan per materi (tidak disimpan, tidak memberi XP). */
  function finish(answers) {
    const box = document.getElementById('quiz-container');
    const right = answers.filter((a) => a.correct).length;
    const total = answers.length;
    const pct = total ? Math.round((100 * right) / total) : 0;
    const per = {};
    answers.forEach((a) => {
      const r = per[a.topic] || (per[a.topic] = { right: 0, total: 0 });
      r.total++; if (a.correct) r.right++;
    });
    if (pct >= 70) { SFX.fanfare(); Confetti.burst(); }
    Mascot.setMood(pct >= 70 ? 'celebrate' : 'comfort',
      pct >= 70 ? '🎉 Mantap! Latihan bebasmu keren.' : 'Tetap semangat! Ulangi dengan soal baru untuk memperkuat pemahaman.');
    box.innerHTML = `
      <div class="level-complete session-result ${pct >= 70 ? 'pass' : 'fail'}">
        <div class="trophy-anim">${pct >= 70 ? '🎯' : '📚'}</div>
        <h3>Benar ${right}/${total} (${pct}%)</h3>
        <p>Latihan bebas tidak mengubah nyawa, XP, maupun peringkat.</p>
        <ul class="fp-summary">${Object.entries(per).map(([t, r]) => `
          <li><span>${esc(t)}</span><b>${r.right}/${r.total}</b></li>`).join('')}
        </ul>
        <div class="offer-actions">
          <button class="btn btn-primary" onclick="FreePractice.again()">🔁 Soal baru (pilihan sama)</button>
          <button class="btn btn-outline" onclick="FreePractice.change()">Ubah pilihan</button>
        </div>
      </div>`;
  }

  return {
    render,
    renderQuiz,
    finish,
    start,
    async setFaculty(f) { sel.faculty = f; sel.level = null; sel.topics.clear(); SFX.click(); await render(); },
    setLevel(l) { sel.level = l; sel.topics.clear(); SFX.click(); render(); },
    toggle(slug) {
      if (sel.topics.has(slug)) sel.topics.delete(slug); else sel.topics.add(slug);
      document.querySelectorAll('.fp-topic').forEach((el) => el.classList.toggle('on', el.querySelector('input').checked));
      refreshStart();
    },
    selectAll(on) {
      sel.topics.clear();
      if (on) (level()?.topics || []).forEach((t) => sel.topics.add(t.slug));
      render();
    },
    setCount(v) {
      sel.count = Math.max(0, Math.min(MAX, parseInt(v, 10) || 0));
      const el = document.getElementById('fp-count-val');
      if (el) el.textContent = sel.count;
      refreshStart();
    },
    again() { Drawer.switchTab('kuis'); },
    change() { Drawer.close(); Nav.go('free'); },
  };
})();
