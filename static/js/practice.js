/**
 * Calculus Bridge — Practice (kurikulum 4 level)
 *
 * Menangani node sub-level yang memiliki Topik:
 *   Drawer → daftar topik → ringkasan topik (materi lengkap: slide di halaman Pelajaran) → 5 sesi latihan berlapis.
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
 *     Node disambung jalur tinta (drawInk): tinta penuh sampai topik aktif, garis pensil
 *     putus-putus ke topik terkunci. Warna mengikuti level utama (--tone ← --lv-N).
 *   - Anti-curang: selama sesi berjalan FocusGuard (app.js) mengawasi keluar tab/jendela dan
 *     melapor ke POST /api/session/<id>/keluar-tab/. Keluar pertama = peringatan; keluar kedua,
 *     menutup/memuat ulang halaman, atau meninggalkan sesi (tutup drawer) = sesi gagal
 *     (aturan & hitungan di server, sessions.leave_tab).
 *
 * Bergantung pada modul global di app.js: Curriculum, Drawer, QuizEngine, State,
 * Mascot, SFX, Confetti, postJSON, FocusGuard; dan Lessons (lessons.js) untuk tombol materi.
 */
const Practice = (() => {
  let node = null;
  let topic = null;
  let nodeLocked = false;
  let running = null;    // { session, attempt, tabLeaves, maxTabLeaves, done, unwatch }

  const TIER_ICON = { mudah: 'sprout', sedang: 'leaf', sulit: 'mountain', tantangan: 'flame', olimpiade: 'medal' };
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
    // Topik tanpa sesi soal: dianggap lewat begitu urutannya tercapai (tidak melompati topik sebelumnya).
    if (!t.sessions.length) return topicUnlocked(t);
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
    const tone = level ? `style="--tone: var(--lv-${level.order}, var(--clr-primary))"` : '';
    return `
      <div class="unit-banner" ${tone}>
        ${level ? `<span class="unit-level">${Icon.level(level)} ${level.title}</span>` : ''}
        <span class="unit-title">${n.title}</span>
      </div>
      <div class="unit-path" data-node="${n.slug}" ${tone}>
        ${n.topics.map((t, i) => {
          const dx = DX[i % DX.length];
          return `
          <div class="topic-node" id="topic-${t.slug}" data-topic="${t.slug}" style="--dx:${dx}px">
            <div class="topic-node-inner">
              <span class="topic-node-label ${dx > 0 ? 'label-left' : 'label-right'}">${t.title}</span>
              <button class="topic-node-btn" title="${t.title}" onclick="Practice.openFromTree('${t.slug}')">
                <span class="topic-node-icon">${Icon.of(t.icon)}</span>
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
      el.querySelector('.topic-node-icon').innerHTML = st === 'locked' ? Icon('lock') : Icon.of(t.icon);
      el.querySelector('.topic-node-dots').innerHTML = t.sessions.map((s) => {
        const p = Curriculum.sessionProgress(s.id);
        return `<i class="${p && p.passed ? 'on' : ''}" title="${s.title}"></i>`;
      }).join('');
      if (st === 'active' && !active) active = el;
    });
    placeArchie(active);
    document.querySelectorAll('.unit-path').forEach(watchInk);
  }

  /* ── jalur tinta antar-node ──────────────────────────────────────── */
  const SVG_NS = 'http://www.w3.org/2000/svg';
  const inkSeen = new WeakSet();
  const inkRO = typeof ResizeObserver !== 'undefined' ? new ResizeObserver((es) => es.forEach((e) => drawInk(e.target))) : null;

  function watchInk(path) {
    drawInk(path);
    if (inkRO && !inkSeen.has(path)) { inkSeen.add(path); inkRO.observe(path); }
  }

  /** Gambar kurva antar pusat tombol node; ruas menuju node terkunci jadi garis pensil. */
  function drawInk(path) {
    const btns = [...path.querySelectorAll('.topic-node-btn')];
    const box = path.getBoundingClientRect();
    if (btns.length < 2 || !box.width) return;
    let svg = path.querySelector(':scope > .unit-ink');
    if (!svg) {
      svg = document.createElementNS(SVG_NS, 'svg');
      svg.setAttribute('class', 'unit-ink');
      svg.setAttribute('aria-hidden', 'true');
      svg.innerHTML = '<path class="ink-done"/><path class="ink-todo"/>';
      path.prepend(svg);
    }
    svg.setAttribute('viewBox', `0 0 ${box.width} ${box.height}`);
    // Ruas mulai di bawah titik sesi node sebelumnya dan berhenti di tepi atas node berikutnya.
    const pts = btns.map((b) => {
      const r = b.getBoundingClientRect();
      const dots = b.parentElement.querySelector('.topic-node-dots')?.getBoundingClientRect();
      return { x: r.left - box.left + r.width / 2, top: r.top - box.top - 4, out: (dots && dots.height ? dots.bottom : r.bottom) - box.top + 4 };
    });
    let done = '', todo = '';
    for (let i = 1; i < pts.length; i++) {
      const x0 = pts[i - 1].x, y0 = pts[i - 1].out, x1 = pts[i].x, y1 = pts[i].top, m = (y1 - y0) / 2;
      const seg = `M${x0} ${y0}C${x0} ${y0 + m} ${x1} ${y1 - m} ${x1} ${y1}`;
      if (btns[i].closest('.topic-locked')) todo += seg; else done += seg;
    }
    svg.querySelector('.ink-done').setAttribute('d', done);
    svg.querySelector('.ink-todo').setAttribute('d', todo);
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
      <div class="topic-progress">${Icon('check')} ${done}/${node.topics.length} topik selesai
        <small>(selesai = lulus Sesi I–${['', 'I', 'II', 'III', 'IV', 'V'][Curriculum.requiredSessions]}; Sesi IV–V bonus XP)</small></div>
      ${nodeLocked ? `<p class="lesson-note">${Icon('lock')} Mode baca aja: beresin sub-level sebelumnya dulu buat buka latihannya.</p>` : ''}
      <div class="topic-grid">
        ${node.topics.map((t, i) => `
          <button class="topic-card${topicDone(t) ? ' done' : ''}${topicUnlocked(t) ? '' : ' locked'}" onclick="Practice.openTopic('${t.slug}')">
            <span class="topic-icon">${topicUnlocked(t) || topicDone(t) ? Icon.of(t.icon) : Icon('lock')}</span>
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

  /** Ringkasan topik; materi lengkap dipelajari sebagai slide di halaman Pelajaran (Lessons, lessons.js). */
  function renderTopic() {
    const box = document.getElementById('drawer-lesson-content');
    const read = Lessons.status(topic.slug);
    const graphs = topic.sections.reduce((a, s) => a + (s.graphs || []).length, 0);
    box.innerHTML = `
      <button class="btn btn-outline btn-sm btn-back" onclick="Practice.backToTopics()">← Semua topik</button>
      ${topic.references ? `<div class="source-tag">${Icon('book')} ${topic.references}</div>` : ''}
      <div class="lesson-brief">
        ${topic.summary ? `<p class="lesson-brief-sum">${topic.summary}</p>` : ''}
        <h4>Yang bakal kamu pelajari</h4>
        <ul class="lesson-brief-list">${[...new Set(topic.sections.map((s) => s.heading))].map((h) => `<li>${h}</li>`).join('')}</ul>
        <p class="lesson-brief-status status-${read}">${read === 'done' ? '✓ Materinya udah kamu pelajari'
          : read === 'started' ? '▶ Lagi kamu pelajari' : `${Icon('book')} Belum kamu pelajari`}</p>
        <button class="btn btn-primary" onclick="Lessons.openFromDrawer('${topic.slug}')">
          ${Icon('play')} ${read === 'done' ? 'Ulang' : read === 'started' ? 'Lanjutin' : 'Mulai'} materi${graphs ? ` · ${graphs} grafik interaktif` : ''}</button>
      </div>`;
    const startBtn = document.getElementById('drawer-start-quiz');
    if (startBtn) { startBtn.hidden = false; startBtn.textContent = 'Lanjut latihan ➔'; }
  }

  /* ── nyawa ─────────────────────────────────────────────────────────── */
  /** Panel nyawa habis: sesi terkunci sampai nyawa terisi ulang (materi tetap bisa dibaca). */
  function noHeartsHTML() {
    return `
      <div class="level-complete hearts-out">
        <div class="trophy-anim">${Icon('heart-broken')}</div>
        <h3>Heart kamu habis</h3>
        <p>Tiap gagal lulus sesi, heart kamu berkurang satu. Semua ${State.get().maxHearts} heart bakal penuh lagi dalam
          <strong>${State.refillText()}</strong>.</p>
        <p class="lesson-note">Sambil nunggu, kamu tetap bisa baca materi atau latihan di Bank Soal (gak pakai heart).</p>
        <div class="offer-actions">
          <button class="btn btn-accent" onclick="Shop.refillHearts()">${Icon('heart')} Refill penuh · ${Shop.price('hearts-full')}</button>
          <button class="btn btn-outline" onclick="Drawer.switchTab('materi')">${Icon('book')} Baca materi</button>
          <button class="btn btn-outline" onclick="Practice.renderSessions()">Daftar sesi</button>
        </div>
      </div>`;
  }

  function showNoHearts(hearts) {
    if (hearts) State.setHearts(hearts);
    QuizBoard.hide();
    document.getElementById('quiz-container').innerHTML = noHeartsHTML();
    SFX.wrong();
    Mascot.setMood('comfort', `${Icon('heart-broken')} Heart habis. Rehat dulu, heart penuh lagi dalam ${State.refillText()}.`);
  }

  /* ── tampilan sesi ───────────────────────────────────────────────── */
  function renderSessions() {
    const box = document.getElementById('quiz-container');
    if (!box) return;
    QuizBoard.hide();
    if (!topic) {
      box.innerHTML = `
        <div class="level-complete">
          <div class="trophy-anim">${Icon('compass')}</div>
          <h3>Pilih topik dulu</h3>
          <p>Tiap topik punya materi + 5 sesi latihan (10 soal per sesi).</p>
          <div class="topic-pick">${node.topics.map((t) => `
            <button class="btn btn-outline btn-sm" onclick="Practice.openTopic('${t.slug}', 'kuis')">${Icon.of(t.icon)} ${t.title}</button>`).join('')}
          </div>
        </div>`;
      return;
    }
    if (!topic.sessions.length) {
      box.innerHTML = `
        <div class="level-complete">
          <div class="trophy-anim">${Icon('book')}</div>
          <h3>Latihan topik ini menyusul</h3>
          <p>Materinya udah lengkap di Kurikulum. Pelajari dulu di sana; topik ini gak menghalangi progresmu.</p>
          <button class="btn btn-primary" onclick="Lessons.openFromDrawer('${topic.slug}')">${Icon('play')} Buka materi</button>
        </div>`;
      return;
    }
    const noHearts = !State.hasHearts();
    box.innerHTML = `
      ${noHearts ? `<div class="hearts-banner">${Icon('heart-broken')} Heart habis, sesi dikunci dulu. Penuh lagi dalam <b>${State.refillText()}</b>.</div>` : ''}
      <div class="session-head">
        <button class="btn btn-outline btn-sm" onclick="Practice.backToTopics()">← Topik</button>
        <span>${Icon.of(topic.icon)} <b>${topic.title}</b></span>
      </div>
      <div class="session-list">
        ${topic.sessions.map((s) => {
          const st = sessionState(topic, s);
          const p = Curriculum.sessionProgress(s.id);
          const req = s.number <= Curriculum.requiredSessions;
          return `
            <div class="session-row session-${st}">
              <span class="session-icon">${Icon(st === 'locked' ? 'lock' : st === 'passed' ? 'check' : TIER_ICON[s.tier] || 'target')}</span>
              <span class="session-info">
                <b>${s.title}</b>
                <small>${s.question_count} soal · lulus ≥ ${s.pass_score} · ${s.xp_per_question} XP/soal · ${req ? 'wajib' : 'bonus'}</small>
                ${p ? `<small>Skor terbaik ${p.best}/${s.question_count} · ${p.attempts}× dicoba</small>` : ''}
              </span>
              <button class="btn ${st === 'passed' ? 'btn-outline' : 'btn-primary'} btn-sm" ${st === 'locked' || noHearts ? 'disabled' : ''}
                      onclick="Practice.start(${s.id})">${st === 'passed' ? 'Coba lagi' : st === 'open' ? 'Mulai ➔' : 'Terkunci'}</button>
            </div>`;
        }).join('')}
      </div>
      <p class="graph-hint">${Icon('dice')} Soal tiap sesi diacak khusus buat akunmu, jadi tiap ngulang angkanya beda.
        XP cuma nambah kalau skor terbaikmu naik. ${Icon('heart')} Gagal lulus = −1 heart.</p>`;
  }

  async function start(sessionId) {
    const box = document.getElementById('quiz-container');
    if (!State.hasHearts()) { showNoHearts(); return; }
    box.innerHTML = '<p class="loading-text">Lagi ngacak soal buat kamu…</p>';
    SFX.click();
    try {
      const res = await fetch(`/api/session/${sessionId}/`);
      const data = await res.json();
      if (data.status === 'no_hearts') { showNoHearts(data.hearts); return; }
      if (!res.ok) throw new Error(data.message || `HTTP ${res.status}`);
      stopWatching();
      running = { session: data.session, attempt: data.attempt, tabLeaves: data.tab_leaves, maxTabLeaves: data.max_tab_leaves };
      running.unwatch = FocusGuard.watch({ leave: () => reportLeave(false), unload: () => reportLeave(true) });
      QuizEngine.start(node.slug, data.questions, 'session');
      Mascot.setMood('thinking', data.tab_leaves
        ? `${Icon('warning')} ${data.session.title}: kamu udah sekali keluar tab di percobaan ini. Sekali lagi, sesinya gagal!`
        : `${data.session.title}: semangat! Jangan pindah tab sampai sesinya beres, ya.`);
    } catch (err) {
      box.innerHTML = `<p class="loading-text">Sesi gagal dimuat: ${err.message}</p>`;
    }
  }

  /* ── anti-curang: keluar tab ────────────────────────────────────── */
  const isRunning = () => !!running && !running.done;

  function stopWatching() {
    if (!running) return;
    running.done = true;
    running.unwatch?.();
    FocusGuard.dismiss();
  }

  /**
   * Lapor keluar tab ke server. quit=true (halaman ditutup / sesi ditinggalkan) langsung menggagalkan.
   * keepalive agar laporan tetap terkirim walau halaman sedang ditutup.
   */
  async function reportLeave(quit) {
    if (!isRunning()) return null;
    const run = running;
    let r;
    try {
      const res = await fetch(`/api/session/${run.session.id}/keluar-tab/`, {
        method: 'POST', keepalive: true,
        headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrfToken() },
        body: JSON.stringify({ attempt: run.attempt, quit }),
      });
      r = await res.json();
    } catch (_) { return null; }
    if (run !== running || run.done) return r;
    if (r.status === 'warning') {
      run.tabLeaves = r.tab_leaves;
      FocusGuard.warn('Eits, jangan pindah tab!',
        `Selama sesi jalan, kamu gak boleh pindah tab atau jendela. Ini peringatan terakhir: sekali lagi
         keluar, <b>sesinya gagal</b> (−1 heart, gak dapat XP).`);
      Mascot.setMood('comfort', `${Icon('warning')} Stay di tab ini sampai sesinya beres, ya!`);
    } else if (r.status === 'failed') {
      stopWatching();
      QuizBoard.hide();
      showResult(r, quit ? 'Sesinya ditinggal sebelum beres, jadi dihitung gagal.'
        : `Sesinya gagal karena kamu keluar tab ${run.maxTabLeaves} kali.`);
    }
    return r;
  }

  async function finish(answers) {
    if (!isRunning()) return;
    stopWatching();
    const box = document.getElementById('quiz-container');
    box.innerHTML = '<p class="loading-text">Menilai jawaban…</p>';
    let r;
    try {
      r = await postJSON(`/api/session/${running.session.id}/submit/`, { attempt: running.attempt, answers });
    } catch (err) {
      if (err.data?.status === 'no_hearts') { showNoHearts(err.data.hearts); return; }
      box.innerHTML = `<div class="level-complete"><div class="trophy-anim">${Icon('warning')}</div><h3>Jawaban gagal dinilai</h3>
        <p>${err.message}</p><button class="btn btn-primary" onclick="Practice.renderSessions()">Kembali</button></div>`;
      return;
    }
    showResult(r);
  }

  /** Hasil sesi (dari submit, atau dari sesi yang digagalkan karena keluar tab: `failNote`). */
  function showResult(r, failNote) {
    const box = document.getElementById('quiz-container');
    const s = running.session;
    Curriculum.setSessionProgress(s.id, { attempts: r.attempts, best: r.best, last: r.score, passed: r.passed || !!Curriculum.sessionProgress(s.id)?.passed });
    State.setLevel(r.level, r.xp_awarded);
    State.setStreak(r.streak);
    if (r.leveled_up) LevelUp.show(r.level, r.gems_awarded);
    if (r.gems != null) State.setGems(r.gems);
    if (r.hearts) State.setHearts(r.hearts);
    if (r.passed) { SFX.fanfare(); Confetti.burst(); } else SFX.wrong();
    if (r.node_completed) State.completeNode(node.slug, r.next_node || Curriculum.nextOf(node.slug));
    Mascot.setMood(r.passed ? 'celebrate' : 'comfort',
      r.passed ? `${Icon('trophy')} Lulus! Sesi berikutnya udah kebuka.`
        : !State.hasHearts() ? `${Icon('heart-broken')} Heart habis. Penuh lagi dalam ${State.refillText()}.`
        : failNote ? `${Icon('x')} Sesinya gagal karena kamu keluar tab. Kerjain sendiri, ya!`
        : 'Dikit lagi! Baca pembahasannya, terus coba lagi pakai soal baru.');

    const next = topic.sessions.find((x) => x.number === s.number + 1);
    box.innerHTML = Review.tabs(`
      <div class="level-complete session-result ${r.passed ? 'pass' : 'fail'}">
        <div class="trophy-anim">${Icon(r.passed ? 'trophy' : 'book')}</div>
        <h3>${s.title}: ${r.score}/${r.total}</h3>
        ${failNote ? `<p class="lesson-note tabwarn-note">${Icon('x')} ${failNote}</p>` : ''}
        <p>${r.passed ? 'Lulus!' : `Belum lulus. Butuh minimal ${r.pass_score} benar.`}
           ${r.xp_awarded ? ` <strong>+${r.xp_awarded} XP</strong>` : ''}${r.gems_awarded ? ` <strong>+${r.gems_awarded} ${Icon('diamond')}</strong>` : ''}</p>
        ${r.heart_lost ? `<p class="lesson-note hearts-note">${Icon('heart-broken')} −1 Heart · sisa ${State.get().hearts}/${State.get().maxHearts}${
          State.hasHearts() ? '' : `. Heart habis, penuh lagi dalam ${State.refillText()}.`}</p>` : ''}
        ${r.node_completed ? `<p class="lesson-note">${Icon('sparkle')} Semua topik di sub-level ini beres! Sub-level berikutnya udah kebuka di Skill Tree.</p>`
          : r.topic_done && s.number === Curriculum.requiredSessions ? `<p class="lesson-note">${Icon('check')} Materi selesai! Sesi IV–V jadi tantangan bonus.</p>` : ''}
        <div class="offer-actions">
          ${State.hasHearts() ? `<button class="btn btn-outline" onclick="Practice.start(${s.id})">${Icon('refresh')} Coba lagi</button>` : ''}
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
        Mascot.setMood('comfort', `${Icon('lock')} Beresin topik sebelumnya dulu (lulus Sesi I–III) buat buka topik ini!`);
        const el = document.getElementById(`topic-${slug}`);
        if (el) { el.classList.add('node-shake'); setTimeout(() => el.classList.remove('node-shake'), 500); }
        return;
      }
      node = found.node;
      nodeLocked = false;
      Drawer.setMode('topic');
      this.openTopic(slug);
      Drawer.ui.show();
      Mascot.setMood('wave', `Topik <strong>${found.topic.title}</strong>: baca materinya dulu, terus taklukin 5 sesinya!`);
    },
    openNode(n, opts = {}) {
      node = n;
      topic = null;
      nodeLocked = !!opts.locked;
      Drawer.ui.setHeader(n.badge_label, n.title, n.subtitle);
      Drawer.ui.setTabs(`${Icon('book')} Topik & Materi`, `${Icon('target')} Latihan Bertahap`);
      renderTopicList();
      Drawer.switchTab('materi');
      Drawer.ui.show();
      SFX.click();
      Mascot.setMood('wave', `Masuk ke <strong>${n.title}</strong>! Pilih topik, baca materinya, terus taklukin 5 sesinya.`);
    },
    openTopic(slug, tab = 'materi') {
      const found = Curriculum.topic(slug);
      if (!found) return;
      ({ node, topic } = found);
      const idx = node.topics.indexOf(topic) + 1;
      Drawer.ui.setHeader(`${node.title} · Topik ${idx}/${node.topics.length}`, topic.title, topic.summary);
      Drawer.ui.setTabs(`${Icon('book')} Materi`, `${Icon('target')} Latihan (5 sesi)`);
      renderTopic();
      Drawer.switchTab(tab);
      document.querySelector('.drawer-body')?.scrollTo({ top: 0 });
      SFX.click();
    },
    backToTopics() {
      topic = null;
      Drawer.ui.setHeader(node.badge_label, node.title, node.subtitle);
      Drawer.ui.setTabs(`${Icon('book')} Topik & Materi`, `${Icon('target')} Latihan Bertahap`);
      renderTopicList();
      Drawer.switchTab('materi');
    },
    renderSessions,
    start,
    finish,
    /**
     * Dipanggil Drawer.close(): meninggalkan sesi yang sedang berjalan = gagal, jadi minta konfirmasi.
     * Mengembalikan false bila pengguna batal (drawer tetap terbuka).
     */
    confirmLeave() {
      if (!isRunning()) return true;
      if (!FocusGuard.confirm(`${running.session.title} masih jalan. Kalau keluar sekarang, sesinya GAGAL (−1 heart, gak dapat XP). Yakin mau keluar?`)) return false;
      reportLeave(true);
      return true;
    },
  };
})();
