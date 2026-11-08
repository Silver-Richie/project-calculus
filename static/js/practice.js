/**
 * Calculus Bridge — Practice (kurikulum 4 level)
 *
 * Menangani node sub-level yang memiliki Topik:
 *   Drawer → daftar topik → materi topik (grafik slider) → 5 sesi latihan berlapis.
 *
 * Mechanism:
 *   - Soal sesi diambil dari GET /api/session/<id>/ (diacak per akun oleh server).
 *   - QuizEngine (mode 'session') menampilkan soal + hint + pembahasan seperti biasa,
 *     lalu memanggil Practice.finish(answers) di akhir sesi.
 *   - Jawaban dikirim ke POST /api/session/<id>/submit/; server menilai ulang,
 *     menyimpan progres, memberi XP, dan membuka sesi/sub-level berikutnya.
 *   - Topik dibuka berurutan (topik k terbuka bila topik k−1 lulus Sesi I–III) dan
 *     sesi n terbuka bila sesi n−1 lulus — sama dengan aturan server (sessions.py).
 *   - Di skill tree, setiap topik tampil sebagai node bulat pada jalur zig-zag
 *     (pathHTML) dengan 5 titik sesi; Archie berdiri di samping topik aktif.
 *
 * Bergantung pada modul global di app.js: Curriculum, Drawer, QuizEngine, State,
 * Mascot, SFX, Confetti, renderSections, postJSON.
 */
const Practice = (() => {
  let node = null;
  let topic = null;
  let nodeLocked = false;
  let running = null;    // { session, attempt }

  const TIER_ICON = { mudah: '🌱', sedang: '🌿', sulit: '🌳', tantangan: '🔥', olimpiade: '🏅' };
  // Geser horizontal node topik (px) membentuk jalur ular; label di sisi berlawanan.
  const DX = [0, 70, 110, 70, 0, -70, -110, -70];

  /* ── status ──────────────────────────────────────────────────────── */
  function parentOf(t) { return Curriculum.topic(t.slug)?.node; }

  function topicUnlocked(t) {
    const n = parentOf(t);
    if (!n || State.nodeStatus(n.slug, Curriculum.tree) === 'locked') return false;
    const i = n.topics.indexOf(t);
    return i <= 0 || topicDone(n.topics[i - 1]);
  }

  /** 'done' | 'active' | 'locked' untuk node topik di skill tree. */
  function topicStatus(t) {
    if (topicDone(t)) return 'done';
    return topicUnlocked(t) ? 'active' : 'locked';
  }

  function sessionState(t, s) {
    if (nodeLocked) return 'locked';
    const p = Curriculum.sessionProgress(s.id);
    if (p && p.passed) return 'passed';
    if (s.number === 1) return topicUnlocked(t) ? 'open' : 'locked';
    const prev = t.sessions.find((x) => x.number === s.number - 1);
    const pp = prev && Curriculum.sessionProgress(prev.id);
    return pp && pp.passed ? 'open' : 'locked';
  }

  function topicDone(t) {
    const req = t.sessions.find((s) => s.number === Curriculum.requiredSessions);
    return !!(req && Curriculum.sessionProgress(req.id)?.passed);
  }

  function dots(t) {
    return `<span class="topic-dots">${t.sessions.map((s) => {
      const st = sessionState(t, s);
      return `<i class="dot dot-${st}" title="${s.title}: ${st === 'passed' ? 'lulus' : st === 'open' ? 'terbuka' : 'terkunci'}"></i>`;
    }).join('')}</span>`;
  }

  /* ── jalur topik di skill tree ───────────────────────────────────── */
  function pathHTML(n, level) {
    return `
      <div class="unit-banner">
        ${level ? `<span class="unit-level">${level.icon} ${level.title}</span>` : ''}
        <span class="unit-title">${n.title}</span>
      </div>
      <div class="unit-path" data-node="${n.slug}">
        ${n.topics.map((t, i) => {
          const dx = DX[i % DX.length];
          return `
          <div class="topic-node" id="topic-${t.slug}" data-topic="${t.slug}" style="--dx:${dx}px">
            <div class="topic-node-inner">
              <span class="topic-node-label ${dx > 0 ? 'label-left' : 'label-right'}">${t.title}</span>
              <button class="topic-node-btn" title="${t.title}" onclick="Practice.openFromTree('${t.slug}')">
                <span class="topic-node-icon">${t.icon}</span>
              </button>
              <span class="topic-node-dots" data-dots="${t.slug}"></span>
            </div>
          </div>`;
        }).join('')}
      </div>`;
  }

  /** Perbarui status node topik, titik sesi, dan posisi Archie. */
  function refreshPath() {
    let active = null;
    document.querySelectorAll('.topic-node').forEach((el) => {
      const found = Curriculum.topic(el.dataset.topic);
      if (!found) return;
      const t = found.topic;
      const st = topicStatus(t);
      el.classList.remove('topic-done', 'topic-active', 'topic-locked');
      el.classList.add(`topic-${st}`);
      el.querySelector('.topic-node-icon').textContent = st === 'locked' ? '🔒' : t.icon;
      el.querySelector('.topic-node-dots').innerHTML = t.sessions.map((s) => {
        const p = Curriculum.sessionProgress(s.id);
        return `<i class="${p && p.passed ? 'on' : ''}" title="${s.title}"></i>`;
      }).join('');
      if (st === 'active' && !active) active = el;
    });
    placeArchie(active);
  }

  // Referensi disimpan: SkillTree.render() mengganti isi #skill-tree sehingga elemen
  // yang sedang menempel di node topik ikut terlepas dari DOM.
  let archieEl = null;
  function placeArchie(el) {
    archieEl = archieEl || document.getElementById('path-archie');
    const archie = archieEl;
    if (!archie) return;
    if (!el) { archie.hidden = true; return; }
    const dx = parseInt(getComputedStyle(el).getPropertyValue('--dx'), 10) || 0;
    archie.classList.toggle('archie-left', dx <= 0);  // label di kanan bila dx ≤ 0 → Archie di kiri
    el.appendChild(archie);
    archie.hidden = false;
  }

  /* ── tampilan materi ─────────────────────────────────────────────── */
  function renderTopicList() {
    const box = document.getElementById('drawer-lesson-content');
    const done = node.topics.filter(topicDone).length;
    box.innerHTML = `
      ${node.summary ? `<div class="lesson-block">${node.summary}</div>` : ''}
      <div class="topic-progress">✅ ${done}/${node.topics.length} topik tuntas
        <small>(tuntas = lulus Sesi I–${['', 'I', 'II', 'III', 'IV', 'V'][Curriculum.requiredSessions]}; Sesi IV–V bonus XP)</small></div>
      ${nodeLocked ? '<p class="lesson-note">🔒 Mode baca: selesaikan sub-level sebelumnya untuk membuka latihan.</p>' : ''}
      <div class="topic-grid">
        ${node.topics.map((t, i) => `
          <button class="topic-card${topicDone(t) ? ' done' : ''}${topicUnlocked(t) ? '' : ' locked'}" onclick="Practice.openTopic('${t.slug}')">
            <span class="topic-icon">${topicUnlocked(t) || topicDone(t) ? t.icon : '🔒'}</span>
            <span class="topic-body">
              <span class="topic-num">Topik ${i + 1}</span>
              <span class="topic-title">${t.title}</span>
              <span class="topic-sum">${t.summary || ''}</span>
              ${dots(t)}
            </span>
          </button>`).join('')}
      </div>`;
    const startBtn = document.getElementById('drawer-start-quiz');
    if (startBtn) startBtn.hidden = true;
  }

  function renderTopic() {
    const box = document.getElementById('drawer-lesson-content');
    renderSections(box, { sections: topic.sections });
    box.insertAdjacentHTML('afterbegin', `
      <button class="btn btn-outline btn-sm btn-back" onclick="Practice.backToTopics()">← Semua topik</button>
      ${topic.references ? `<div class="source-tag">📚 ${topic.references}</div>` : ''}`);
    const startBtn = document.getElementById('drawer-start-quiz');
    if (startBtn) { startBtn.hidden = false; startBtn.textContent = 'Lanjut ke Latihan Bertahap ➔'; }
  }

  /* ── nyawa ─────────────────────────────────────────────────────────── */
  /** Panel nyawa habis: sesi terkunci sampai nyawa terisi ulang (materi tetap bisa dibaca). */
  function noHeartsHTML() {
    return `
      <div class="level-complete hearts-out">
        <div class="trophy-anim">💔</div>
        <h3>Nyawamu habis</h3>
        <p>Nyawa berkurang setiap kali gagal lulus sesi. Semua ${State.get().maxHearts} nyawa penuh kembali dalam
          <strong>${State.refillText()}</strong>.</p>
        <p class="lesson-note">Sambil menunggu, kamu tetap bisa membaca materi dan berlatih di Bank Soal (tanpa nyawa).</p>
        <div class="offer-actions">
          <button class="btn btn-outline" onclick="Drawer.switchTab('materi')">📖 Baca materi</button>
          <button class="btn btn-outline" onclick="Practice.renderSessions()">Daftar sesi</button>
        </div>
      </div>`;
  }

  function showNoHearts(hearts) {
    if (hearts) State.setHearts(hearts);
    QuizBoard.hide();
    document.getElementById('quiz-container').innerHTML = noHeartsHTML();
    SFX.wrong();
    Mascot.setMood('comfort', `💔 Nyawa habis. Istirahat dulu, nyawa penuh lagi dalam ${State.refillText()}.`);
  }

  /* ── tampilan sesi ───────────────────────────────────────────────── */
  function renderSessions() {
    const box = document.getElementById('quiz-container');
    if (!box) return;
    QuizBoard.hide();
    if (!topic) {
      box.innerHTML = `
        <div class="level-complete">
          <div class="trophy-anim">🧭</div>
          <h3>Pilih topik dulu</h3>
          <p>Setiap topik punya materi dan 5 sesi latihan (10 soal per sesi).</p>
          <div class="topic-pick">${node.topics.map((t) => `
            <button class="btn btn-outline btn-sm" onclick="Practice.openTopic('${t.slug}', 'kuis')">${t.icon} ${t.title}</button>`).join('')}
          </div>
        </div>`;
      return;
    }
    const noHearts = !State.hasHearts();
    box.innerHTML = `
      ${noHearts ? `<div class="hearts-banner">💔 Nyawa habis: sesi terkunci. Penuh lagi dalam <b>${State.refillText()}</b>.</div>` : ''}
      <div class="session-head">
        <button class="btn btn-outline btn-sm" onclick="Practice.backToTopics()">← Topik</button>
        <span>${topic.icon} <b>${topic.title}</b></span>
      </div>
      <div class="session-list">
        ${topic.sessions.map((s) => {
          const st = sessionState(topic, s);
          const p = Curriculum.sessionProgress(s.id);
          const req = s.number <= Curriculum.requiredSessions;
          return `
            <div class="session-row session-${st}">
              <span class="session-icon">${st === 'locked' ? '🔒' : st === 'passed' ? '✅' : TIER_ICON[s.tier] || '🎯'}</span>
              <span class="session-info">
                <b>${s.title}</b>
                <small>${s.question_count} soal · lulus ≥ ${s.pass_score} · ${s.xp_per_question} XP/soal · ${req ? 'wajib' : 'bonus'}</small>
                ${p ? `<small>Skor terbaik ${p.best}/${s.question_count} · ${p.attempts}× dicoba</small>` : ''}
              </span>
              <button class="btn ${st === 'passed' ? 'btn-outline' : 'btn-primary'} btn-sm" ${st === 'locked' || noHearts ? 'disabled' : ''}
                      onclick="Practice.start(${s.id})">${st === 'passed' ? 'Ulangi (soal baru)' : st === 'open' ? 'Mulai ➔' : 'Terkunci'}</button>
            </div>`;
        }).join('')}
      </div>
      <p class="graph-hint">🎲 Soal setiap sesi diacak khusus untuk akunmu. Mengulang sesi memberi angka baru;
        XP hanya bertambah bila skor terbaikmu naik. ❤️ Gagal lulus sesi mengurangi 1 nyawa.</p>`;
  }

  async function start(sessionId) {
    const box = document.getElementById('quiz-container');
    if (!State.hasHearts()) { showNoHearts(); return; }
    box.innerHTML = '<p class="loading-text">Menyiapkan soal acak untukmu…</p>';
    SFX.click();
    try {
      const res = await fetch(`/api/session/${sessionId}/`);
      const data = await res.json();
      if (data.status === 'no_hearts') { showNoHearts(data.hearts); return; }
      if (!res.ok) throw new Error(data.message || `HTTP ${res.status}`);
      running = { session: data.session, attempt: data.attempt };
      QuizEngine.start(node.slug, data.questions, 'session');
      Mascot.setMood('thinking', `${data.session.title}: semangat! Pakai hint bila buntu.`);
    } catch (err) {
      box.innerHTML = `<p class="loading-text">Gagal memuat sesi: ${err.message}</p>`;
    }
  }

  async function finish(answers) {
    const box = document.getElementById('quiz-container');
    box.innerHTML = '<p class="loading-text">Menilai jawaban…</p>';
    let r;
    try {
      r = await postJSON(`/api/session/${running.session.id}/submit/`, { attempt: running.attempt, answers });
    } catch (err) {
      if (err.data?.status === 'no_hearts') { showNoHearts(err.data.hearts); return; }
      box.innerHTML = `<div class="level-complete"><div class="trophy-anim">⚠️</div><h3>Gagal menilai</h3>
        <p>${err.message}</p><button class="btn btn-primary" onclick="Practice.renderSessions()">Kembali</button></div>`;
      return;
    }
    const s = running.session;
    Curriculum.setSessionProgress(s.id, { attempts: r.attempts, best: r.best, last: r.score, passed: r.passed || !!Curriculum.sessionProgress(s.id)?.passed });
    if (r.xp_awarded) State.addXP(r.xp_awarded);
    if (r.hearts) State.setHearts(r.hearts);
    if (r.passed) { SFX.fanfare(); Confetti.burst(); } else SFX.wrong();
    if (r.node_completed) State.completeNode(node.slug, r.next_node || Curriculum.nextOf(node.slug));
    Mascot.setMood(r.passed ? 'celebrate' : 'comfort',
      r.passed ? '🏆 Sesi lulus! Sesi berikutnya terbuka.'
        : !State.hasHearts() ? `💔 Nyawa habis. Nyawa penuh lagi dalam ${State.refillText()}.`
        : 'Hampir! Baca lagi pembahasannya lalu coba dengan soal baru.');

    const next = topic.sessions.find((x) => x.number === s.number + 1);
    box.innerHTML = Review.tabs(`
      <div class="level-complete session-result ${r.passed ? 'pass' : 'fail'}">
        <div class="trophy-anim">${r.passed ? '🏆' : '📚'}</div>
        <h3>${s.title}: ${r.score}/${r.total}</h3>
        <p>${r.passed ? 'Lulus!' : `Belum lulus — perlu minimal ${r.pass_score} benar.`}
           ${r.xp_awarded ? ` <strong>+${r.xp_awarded} XP</strong>` : ''}</p>
        ${r.heart_lost ? `<p class="lesson-note hearts-note">💔 −1 Nyawa · sisa ${State.get().hearts}/${State.get().maxHearts}${
          State.hasHearts() ? '' : `. Nyawa habis, penuh lagi dalam ${State.refillText()}.`}</p>` : ''}
        ${r.node_completed ? '<p class="lesson-note">🎉 Semua topik sub-level ini tuntas! Sub-level berikutnya terbuka di Peta Belajar.</p>'
          : r.topic_done && s.number === Curriculum.requiredSessions ? '<p class="lesson-note">✅ Topik tuntas! Sesi IV–V tersedia sebagai tantangan bonus.</p>' : ''}
        <div class="offer-actions">
          ${State.hasHearts() ? `<button class="btn btn-outline" onclick="Practice.start(${s.id})">🔁 Ulangi (soal baru)</button>` : ''}
          ${r.passed && next ? `<button class="btn btn-primary" onclick="Practice.start(${next.id})">Lanjut ${next.title} ➔</button>` : ''}
          <button class="btn btn-outline" onclick="Practice.renderSessions()">Daftar sesi</button>
        </div>
      </div>`, QuizEngine.history());
    SkillTree.refreshStates();
  }

  return {
    pathHTML,
    refreshPath,
    /** Klik node topik di skill tree: buka drawer materi + latihan topik itu. */
    openFromTree(slug) {
      const found = Curriculum.topic(slug);
      if (!found) return;
      if (topicStatus(found.topic) === 'locked') {
        SFX.wrong();
        Mascot.setMood('comfort', '🔒 Tuntaskan topik sebelumnya dulu (lulus Sesi I–III) untuk membuka topik ini!');
        const el = document.getElementById(`topic-${slug}`);
        if (el) { el.classList.add('node-shake'); setTimeout(() => el.classList.remove('node-shake'), 500); }
        return;
      }
      node = found.node;
      nodeLocked = false;
      Drawer.setMode('topic');
      this.openTopic(slug);
      Drawer.ui.show();
      Mascot.setMood('wave', `Topik <strong>${found.topic.title}</strong>: baca materinya, lalu taklukkan 5 sesinya!`);
    },
    openNode(n, opts = {}) {
      node = n;
      topic = null;
      nodeLocked = !!opts.locked;
      Drawer.ui.setHeader(n.badge_label, n.title, n.subtitle);
      Drawer.ui.setTabs('📖 Topik & Materi', '🎯 Latihan Bertahap');
      renderTopicList();
      Drawer.switchTab('materi');
      Drawer.ui.show();
      SFX.click();
      Mascot.setMood('wave', `Selamat datang di <strong>${n.title}</strong>! Pilih topik, baca materinya, lalu taklukkan 5 sesinya.`);
    },
    openTopic(slug, tab = 'materi') {
      const found = Curriculum.topic(slug);
      if (!found) return;
      ({ node, topic } = found);
      const idx = node.topics.indexOf(topic) + 1;
      Drawer.ui.setHeader(`${node.title} · Topik ${idx}/${node.topics.length}`, topic.title, topic.summary);
      Drawer.ui.setTabs('📖 Materi', '🎯 Latihan (5 sesi)');
      renderTopic();
      Drawer.switchTab(tab);
      document.querySelector('.drawer-body')?.scrollTo({ top: 0 });
      SFX.click();
    },
    backToTopics() {
      topic = null;
      Drawer.ui.setHeader(node.badge_label, node.title, node.subtitle);
      Drawer.ui.setTabs('📖 Topik & Materi', '🎯 Latihan Bertahap');
      renderTopicList();
      Drawer.switchTab('materi');
    },
    renderSessions,
    start,
    finish,
  };
})();
