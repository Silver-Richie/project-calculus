/**
 * Calculus Bridge — Kelas Interaktif (halaman Pelajaran)
 *
 * Halaman Pelajaran = tempat BELAJAR seluruh kurikulum (Level Utama → Sub-level → Topik),
 * sedangkan skill tree (Level Up) = tempat LATIHAN. Materi tiap topik diputar sebagai slide.
 *
 * Mechanism:
 *   - Slide dibangun di browser dari materi topik yang sudah ada (/api/curriculum/, lewat Curriculum):
 *       Pembuka → slide materi (satu per bagian; bagian panjang dipecah) → slide grafik slider
 *       → Cek Pemahaman (3 soal) → Rangkuman.
 *   - Di slide materi, setiap paragraf/tabel dan setiap butir daftar adalah satu "langkah":
 *     tombol Lanjut memunculkan langkah berikutnya dulu (seperti presentasi), baru pindah slide.
 *     Slide yang pernah dilewati tampil utuh saat dibuka lagi.
 *   - Rujukan buku (p.book-ref) dikumpulkan dari semua bagian ke slide Rangkuman.
 *   - Cek Pemahaman memakai API Latihan Bebas (POST /api/latihan-bebas/mulai/): soal acak topik
 *     ini, dinilai di browser, tanpa nyawa dan tanpa XP.
 *   - Progres baca (slide terakhir, tuntas, skor cek) disimpan di localStorage per akun; hanya
 *     kenyamanan pengguna, tidak memengaruhi progres latihan di server.
 *
 * Bergantung pada modul global: Curriculum, State, Nav, SFX, Confetti, GraphLab, Practice, Drawer, postJSON.
 */
const Lessons = (() => {
  const KEY = (() => {
    try {
      const p = JSON.parse(document.getElementById('server-profile')?.textContent || 'null');
      return p ? `cb_lessons_v1:${p.username}` : 'cb_lessons_v1';
    } catch (_) { return 'cb_lessons_v1'; }
  })();
  const MAX_CHARS = 650;      // bagian materi lebih panjang dari ini dipecah ke beberapa slide
  const CHECK_COUNT = 3;
  const TIPS = [
    'Santai aja bacanya. Kalau udah paham, tekan <b>Lanjut</b>.',
    'Coba tebak langkah berikutnya sebelum muncul.',
    'Ambil kertas, tulis ulang rumusnya pakai bahasamu sendiri.',
    'Bingung? Balik ke slide sebelumnya juga gapapa.',
  ];

  let progress = loadProgress();
  let topic = null;
  let node = null;
  let slides = [];
  let cur = 0;
  let check = null;           // { slug, qs, i, score, answered, error }

  /* ── progres baca ────────────────────────────────────────────────── */
  function loadProgress() {
    try { return JSON.parse(localStorage.getItem(KEY)) || {}; } catch (_) { return {}; }
  }
  function saveProgress() {
    try { localStorage.setItem(KEY, JSON.stringify(progress)); } catch (_) { }
  }
  const rec = (slug) => progress[slug] || {};

  /* ── data kurikulum ──────────────────────────────────────────────── */
  function allTopics() {
    return Curriculum.tree.flatMap((n) => (n.topics || []).map((t) => ({ t, n })));
  }
  function levelOf(n) {
    return Curriculum.mainLevels.find((l) => l.slug === n.main_level) || null;
  }
  function groups() {
    const nodes = Curriculum.tree.filter((n) => (n.topics || []).length);
    return Curriculum.mainLevels
      .map((level) => ({ level, nodes: nodes.filter((n) => n.main_level === level.slug) }))
      .filter((g) => g.nodes.length);
  }
  function nextTopic() {
    const all = allTopics();
    const i = all.findIndex((x) => x.t === topic);
    return i >= 0 && i + 1 < all.length ? all[i + 1] : null;
  }

  /* ── membangun slide ─────────────────────────────────────────────── */
  /** Pecah isi satu bagian menjadi kelompok blok (tiap kelompok ≤ MAX_CHARS, minimal satu blok). */
  function chunkBlocks(blocks) {
    const chunks = [];
    let cur = [];
    let size = 0;
    blocks.forEach((b) => {
      const w = b.querySelector?.('table') || b.tagName === 'TABLE' ? 450 : b.textContent.length;
      if (cur.length && size + w > MAX_CHARS) { chunks.push(cur); cur = []; size = 0; }
      cur.push(b);
      size += w;
    });
    if (cur.length) chunks.push(cur);
    return chunks;
  }

  /** Tandai langkah tampil bertahap: tiap butir daftar satu langkah, blok lain satu langkah utuh. */
  function markSteps(block) {
    if (block.tagName === 'UL' || block.tagName === 'OL') {
      block.querySelectorAll(':scope > li').forEach((li) => li.classList.add('lp-step'));
    } else {
      block.classList.add('lp-step');
    }
    return block.outerHTML;
  }

  const SLIDE_KIND = {
    intuition: 'Intuisi', derivation: 'Penurunan', theorem: 'Teorema',
    example: 'Contoh', pitfall: 'Jebakan', checkpoint: 'Cek Pemahaman',
  };

  /** Topik kurikulum v2 menulis slide sendiri (jenis + judul + isi); urutan & jumlah bebas. */
  function authoredSlides(t) {
    const out = [{ kind: 'intro' }];
    const refs = t.references ? [t.references] : [];
    t.slides.forEach((sl, i) => {
      const tmp = document.createElement('div');
      tmp.innerHTML = sl.body_html;
      tmp.querySelectorAll('.book-ref').forEach((r) => r.remove());
      out.push({
        kind: 'content', type: sl.kind, heading: sl.title, sec: i, secCount: t.slides.length, part: 1, parts: 1,
        html: [...tmp.children].map(markSteps).join(''), tip: sl.tip,
      });
      if ((sl.graphs || []).length) out.push({ kind: 'graph', heading: sl.title, graphs: sl.graphs, tip: sl.tip });
    });
    out.push({ kind: 'check' });
    out.push({ kind: 'summary', refs });
    return out;
  }

  function buildSlides(t) {
    if ((t.slides || []).length) return authoredSlides(t);
    const out = [{ kind: 'intro' }];
    const refs = [];
    const secCount = t.sections.length;
    t.sections.forEach((sec, si) => {
      const tmp = document.createElement('div');
      tmp.innerHTML = sec.body_html;
      tmp.querySelectorAll('.book-ref').forEach((r) => {
        const txt = r.innerHTML.replace(/^.*?Rujukan:\s*/, '');
        if (!refs.includes(txt)) refs.push(txt);
        r.remove();
      });
      // Teks lepas di luar elemen dibungkus <p> agar bisa menjadi langkah.
      const blocks = [...tmp.childNodes].map((nd) => {
        if (nd.nodeType === Node.ELEMENT_NODE) return nd;
        if (nd.nodeType === Node.TEXT_NODE && nd.textContent.trim()) {
          const p = document.createElement('p');
          p.textContent = nd.textContent;
          return p;
        }
        return null;
      }).filter(Boolean);
      const chunks = chunkBlocks(blocks);
      chunks.forEach((c, ci) => out.push({
        kind: 'content', heading: sec.heading, sec: si, secCount, part: ci + 1, parts: chunks.length,
        html: c.map(markSteps).join(''),
      }));
      if ((sec.graphs || []).length) out.push({ kind: 'graph', heading: sec.heading, graphs: sec.graphs });
    });
    out.push({ kind: 'check' });
    out.push({ kind: 'summary', refs });
    return out;
  }

  const LABEL = { intro: 'Pembuka', content: 'Materi', graph: 'Grafik interaktif', check: 'Cek pemahaman', summary: 'Rangkuman' };

  /* ── isi tiap jenis slide ────────────────────────────────────────── */
  function slideHTML(s) {
    const headings = [...new Set(topic.sections.map((x) => x.heading))];
    if (s.kind === 'intro') {
      const lvl = levelOf(node);
      const k = node.topics.indexOf(topic) + 1;
      const graphs = slides.filter((x) => x.kind === 'graph').length;
      const reads = slides.filter((x) => x.kind === 'content').length;
      return `
        <div class="lp-intro">
          <div class="lp-intro-icon lp-in" style="--i:0">${Icon.of(topic.icon)}</div>
          <div class="lp-kicker lp-in" style="--i:1">${lvl ? `${Icon.level(lvl)} ${lvl.title} · ` : ''}${node.title} · Topik ${k}/${node.topics.length}</div>
          <h2 class="lp-in" style="--i:2">${topic.title}</h2>
          ${topic.summary ? `<p class="lp-lead lp-in" style="--i:3">${topic.summary}</p>` : ''}
          <div class="lp-agenda lp-in" style="--i:4">
            <h4>Yang bakal kamu pelajari</h4>
            <ol>${headings.map((h) => `<li>${h}</li>`).join('')}</ol>
          </div>
          <div class="lp-chips lp-in" style="--i:5">
            <span>${Icon('book')} ${reads} slide materi</span>
            ${graphs ? `<span>${Icon('sliders')} ${graphs} grafik interaktif</span>` : ''}
            <span>${Icon('check')} ${CHECK_COUNT} soal kuis singkat</span>
          </div>
        </div>`;
    }
    if (s.kind === 'content') {
      return `
        <div class="lp-kicker">${s.type ? `<span class="lp-kind lp-kind-${s.type}">${SLIDE_KIND[s.type]}</span> Slide ${s.sec + 1} dari ${s.secCount}`
          : `Bagian ${s.sec + 1} dari ${s.secCount}${s.parts > 1 ? ` · lanjutan ${s.part}/${s.parts}` : ''}`}</div>
        <h3 class="lp-slide-title">${s.heading}</h3>
        <div class="lesson-body lp-body">${s.html}</div>`;
    }
    if (s.kind === 'graph') {
      return `
        <div class="lp-kicker">${Icon('sliders')} Coba sendiri</div>
        <h3 class="lp-slide-title">${s.heading}</h3>
        <p class="lp-hint">Geser slidernya, terus perhatiin apa yang berubah di grafik.</p>
        <div class="lesson-graphs"></div>`;
    }
    if (s.kind === 'check') {
      return `
        <div class="lp-kicker">${Icon('check')} Kuis singkat</div>
        <h3 class="lp-slide-title">${CHECK_COUNT} soal kilat</h3>
        <p class="lp-hint">Gak pakai heart, gak dapat XP. Boleh di-skip pakai tombol Lanjut.</p>
        <div class="lp-check"></div>`;
    }
    // summary
    const nt = nextTopic();
    const r = rec(topic.slug);
    return `
      <div class="lp-done">
        <div class="lp-done-badge lp-in" style="--i:0">${Icon('flag')}</div>
        <h2 class="lp-in" style="--i:1">Topik selesai!</h2>
        <p class="lp-lead lp-in" style="--i:2">${Icon.of(topic.icon)} ${topic.title}</p>
        <ul class="lp-recap lp-in" style="--i:3">${headings.map((h) => `<li>${h}</li>`).join('')}</ul>
        ${r.check != null ? `<p class="lp-score lp-in" style="--i:4">Kuis singkat: <b>${r.check}/${r.checkTotal}</b> benar</p>` : ''}
        ${s.refs.length || topic.references ? `
          <div class="lp-refs lp-in" style="--i:5">
            <h4>${Icon('book')} Bacaan lanjut</h4>
            ${s.refs.map((x) => `<p>${x}</p>`).join('')}
            ${topic.references && !s.refs.length ? `<p>${topic.references}</p>` : ''}
          </div>` : ''}
        <div class="lp-done-actions lp-in" style="--i:6">
          <button class="btn btn-primary" onclick="Lessons.practice()">${Icon('target')} Latihan topik ini</button>
          ${nt ? `<button class="btn btn-growth" onclick="Lessons.open('${nt.t.slug}')">Topik berikutnya: ${Icon.of(nt.t.icon)} ${nt.t.title} ▶</button>` : ''}
        </div>
      </div>`;
  }

  /* ── narasi Archie ───────────────────────────────────────────────── */
  function narrate(s, i) {
    let text;
    let mood = 'mascot-idle';
    if (s.tip) {                                   // slide kurikulum v2: tip khusus dari penulis materi
      text = s.tip;
      mood = s.kind === 'graph' ? 'mascot-idle' : 'mascot-thinking';
    } else if (s.kind === 'intro') {
      text = `Halo! Topik <b>${topic.title}</b> ada ${slides.length} slide. Tekan <b>Lanjut</b>, tombol panah →, atau geser layar.`;
    } else if (s.kind === 'content') {
      const tmp = document.createElement('div');
      tmp.innerHTML = s.html;
      if (tmp.querySelector('table')) text = 'Tabel ini merangkum polanya. Bandingkan baris demi baris.';
      else if (/contoh/i.test(tmp.textContent)) text = 'Ada contoh soal! Coba kerjain sendiri dulu sebelum intip jawabannya.';
      else if (s.part > 1) text = `Masih lanjutan <b>${s.heading}</b>.`;
      else text = TIPS[i % TIPS.length];
      mood = 'mascot-thinking';
    } else if (s.kind === 'graph') {
      const cap = s.graphs.map((g) => g.caption).filter(Boolean)[0];
      text = `${Icon('sliders')} Geser slidernya!${cap ? ` ${cap}` : ''}`;
    } else if (s.kind === 'check') {
      text = 'Waktunya kuis singkat. Santai, ini bukan ujian kok.';
      mood = 'mascot-thinking';
    } else {
      text = `${Icon('sparkle')} Mantap! Kalau udah siap, taklukin latihannya di Skill Tree.`;
      mood = 'mascot-celebrate';
    }
    const svg = document.getElementById('lp-archie-svg');
    if (svg) svg.setAttribute('class', mood);
    const b = document.getElementById('lp-bubble');
    if (!b) return;
    b.innerHTML = text;
    b.classList.remove('bubble-pop');
    void b.offsetWidth;
    b.classList.add('bubble-pop');
  }

  /* ── pemutar ─────────────────────────────────────────────────────── */
  function steps(el) { return [...el.querySelectorAll('.lp-step')]; }

  function applySteps() {
    const el = document.querySelector('#lp-viewport .lp-slide');
    if (!el) return;
    const s = slides[cur];
    steps(el).forEach((st, k) => st.classList.toggle('lp-shown', k < s.shown));
  }

  function hiddenLeft() {
    const el = document.querySelector('#lp-viewport .lp-slide');
    return el ? steps(el).length - slides[cur].shown : 0;
  }

  function show(i, dir = 1) {
    if (slides[cur] && cur !== i) slides[cur].seen = true;
    cur = i;
    const s = slides[i];
    const vp = document.getElementById('lp-viewport');
    const el = document.createElement('article');
    el.className = `lp-slide lp-${s.kind} ${dir < 0 ? 'from-left' : 'from-right'}`;
    el.innerHTML = slideHTML(s);
    vp.replaceChildren(el);
    vp.scrollTop = 0;
    const n = steps(el).length;
    s.shown = s.seen ? n : Math.max(s.shown || 0, Math.min(1, n));
    applySteps();
    if (s.kind === 'graph') GraphLab.mountList(el.querySelector('.lesson-graphs'), s.graphs);
    if (s.kind === 'check') runCheck();

    const r = progress[topic.slug] = { ...rec(topic.slug), at: i, total: slides.length };
    if (s.kind === 'summary' && !r.done) {
      r.done = true;
      SFX.fanfare();
      Confetti.burst();
    }
    saveProgress();
    narrate(s, i);
    chrome();
    if (s.kind === 'summary') renderOutline();
  }

  /** Bilah progres, penghitung, dan label tombol. */
  function chrome() {
    document.getElementById('lp-progress').innerHTML = slides.map((s, k) => `
      <button class="lp-seg lp-seg-${s.kind}${k < cur ? ' done' : k === cur ? ' now' : ''}"
              title="${k + 1}. ${LABEL[s.kind]}${s.heading ? `: ${s.heading.replace(/<[^>]+>/g, '')}` : ''}"
              aria-label="Slide ${k + 1}" onclick="Lessons.go(${k})"></button>`).join('');
    document.getElementById('lp-count').textContent = `${cur + 1} / ${slides.length}`;
    document.getElementById('lp-prev').disabled = cur === 0;
    const next = document.getElementById('lp-next');
    const nt = nextTopic();
    const last = cur === slides.length - 1;
    next.disabled = last && !nt;
    next.textContent = hiddenLeft() > 0 ? 'Lanjut ▼' : last ? (nt ? 'Topik berikutnya ▶' : 'Selesai') : 'Lanjut ▶';
  }

  /* ── cek pemahaman ───────────────────────────────────────────────── */
  async function runCheck() {
    if (!check || check.slug !== topic.slug) {
      const slug = topic.slug;
      check = { slug, qs: null, i: 0, score: 0, answered: false };
      drawCheck();
      try {
        const d = await postJSON('/api/latihan-bebas/mulai/', { faculty: State.get().faculty, topics: [slug], count: CHECK_COUNT });
        if (check.slug === slug) check.qs = d.questions || [];
      } catch (err) {
        if (check.slug === slug) { check.qs = []; check.error = err.message; }
      }
    }
    drawCheck();
  }

  function drawCheck() {
    const box = document.querySelector('#lp-viewport .lp-check');
    if (!box || !check) return;
    if (!check.qs) { box.innerHTML = '<p class="loading-text">Menyiapkan soal…</p>'; return; }
    if (!check.qs.length) {
      box.innerHTML = `<p class="lp-hint">Soal untuk topik ini belum tersedia${check.error ? ` (${check.error})` : ''}. Langsung lanjut ke rangkuman aja.</p>`;
      return;
    }
    const n = check.qs.length;
    if (check.i >= n) {
      progress[topic.slug] = { ...rec(topic.slug), check: check.score, checkTotal: n };
      saveProgress();
      const good = check.score === n;
      box.innerHTML = `
        <div class="lp-check-result">
          <div class="lp-check-big">${check.score}/${n}</div>
          <p>${good ? 'Perfect! Kamu udah siap latihan.' : check.score ? 'Lumayan! Baca lagi bagian yang masih bikin ragu.' : 'Gapapa. Ulang materinya pelan-pelan, terus coba lagi.'}</p>
          <div class="lp-done-actions">
            <button class="btn btn-outline" onclick="Lessons.retryCheck()">${Icon('refresh')} Coba soal lain</button>
            <button class="btn btn-primary" onclick="Lessons.next()">Rangkuman ▶</button>
          </div>
        </div>`;
      document.getElementById('lp-bubble').innerHTML = good ? `${Icon('sparkle')} Keren, bener semua!` : 'Salah itu bagian dari belajar. Pembahasannya udah kamu baca, kan?';
      return;
    }
    const q = check.qs[check.i];
    check.answered = false;
    box.innerHTML = `
      <div class="lp-check-head">
        <span>Soal ${check.i + 1} dari ${n}</span>
        <span class="lp-check-dots">${check.qs.map((_, k) => `<i class="${k < check.i ? 'on' : k === check.i ? 'now' : ''}"></i>`).join('')}</span>
      </div>
      <div class="quiz-prompt">${q.prompt}</div>
      <div class="lp-options">${q.options.map((o) => `<button class="option-btn" data-id="${o.id}" onclick="Lessons.answer(${JSON.stringify(o.id).replace(/"/g, '&quot;')})">${o.text}</button>`).join('')}</div>
      <div class="lp-feedback"></div>`;
  }

  function answer(id) {
    if (!check || check.answered) return;
    check.answered = true;
    const q = check.qs[check.i];
    const ok = q.options.find((o) => o.id === id)?.is_correct;
    if (ok) { check.score++; SFX.correct(); } else SFX.wrong();
    document.querySelectorAll('#lp-viewport .lp-options .option-btn').forEach((b) => {
      const o = q.options.find((x) => String(x.id) === b.dataset.id);
      b.disabled = true;
      if (o?.is_correct) b.classList.add('correct');
      else if (String(id) === b.dataset.id) b.classList.add('incorrect');
    });
    const fb = document.querySelector('#lp-viewport .lp-feedback');
    const last = check.i + 1 >= check.qs.length;
    fb.innerHTML = `
      <div class="lp-fb ${ok ? 'ok' : 'no'}">
        <h5>${ok ? `${Icon('check')} Tepat!` : `${Icon('x')} Belum tepat`}</h5>
        ${(q.steps || []).length ? `<ol class="steps-list">${q.steps.map((x) => `<li>${x}</li>`).join('')}</ol>` : ''}
        <div class="answer-box"><strong>Jawaban:</strong> ${q.answer || ''}</div>
        ${q.explanation ? `<p class="expl-note">${Icon('chat')} ${q.explanation}</p>` : ''}
        ${(q.graphs || []).length ? '<div class="lesson-graphs"></div>' : ''}
        <button class="btn btn-primary btn-sm" onclick="Lessons.nextQuestion()">${last ? 'Lihat hasil ▶' : 'Soal berikutnya ▶'}</button>
      </div>`;
    if ((q.graphs || []).length) GraphLab.mountList(fb.querySelector('.lesson-graphs'), q.graphs);
    document.getElementById('lp-bubble').innerHTML = ok ? 'Betul! Cek pembahasannya untuk memastikan alasanmu juga benar.' : 'Hampir! Baca langkah pembahasannya pelan-pelan.';
    fb.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
  }

  /* ── daftar isi & layar sambutan ─────────────────────────────────── */
  function renderOutline() {
    const box = document.getElementById('lp-outline-body');
    if (!box) return;
    const all = allTopics();
    const done = all.filter((x) => rec(x.t.slug).done).length;
    const pct = all.length ? Math.round((done / all.length) * 100) : 0;
    document.getElementById('lp-overall').innerHTML = `
      <div class="lp-meter"><i style="width:${pct}%"></i></div>
      <span>${done}/${all.length} topik dibaca · ${pct}%</span>`;
    const focus = topic || all.find((x) => !rec(x.t.slug).done)?.t;
    box.innerHTML = groups().map(({ level, nodes }) => {
      const ts = nodes.flatMap((n) => n.topics);
      const d = ts.filter((t) => rec(t.slug).done).length;
      return `
        <details class="lp-level" ${ts.includes(focus) ? 'open' : ''}>
          <summary>
            <span class="lp-level-icon">${Icon.level(level)}</span>
            <span class="lp-level-name"><small>Level ${level.order}</small>${level.title}</span>
            <span class="lp-level-count">${d}/${ts.length}</span>
          </summary>
          ${nodes.map((n) => `
            <div class="lp-unit">
              <div class="lp-unit-title">${n.title}</div>
              ${n.topics.map((t) => {
                const r = rec(t.slug);
                const st = r.done ? 'done' : r.at ? 'started' : '';
                return `
                  <button class="lp-topic ${st}${t === topic ? ' current' : ''}" onclick="Lessons.open('${t.slug}')">
                    <span class="lp-topic-icon">${r.done ? Icon('check') : Icon.of(t.icon)}</span>
                    <span class="lp-topic-title">${t.title}</span>
                    ${st === 'started' ? `<small>${r.at + 1}/${r.total}</small>` : ''}
                  </button>`;
              }).join('')}
            </div>`).join('')}
        </details>`;
    }).join('');
  }

  function renderWelcome() {
    const box = document.getElementById('lp-welcome');
    if (!box) return;
    const all = allTopics();
    if (!all.length) { box.innerHTML = '<p class="loading-text">Lagi nyiapin kurikulum…</p>'; return; }
    const resume = all.find((x) => rec(x.t.slug).at && !rec(x.t.slug).done) || all.find((x) => !rec(x.t.slug).done);
    const graphs = all.reduce((sum, x) => sum + x.t.sections.reduce((a, s) => a + (s.graphs || []).length, 0), 0);
    box.innerHTML = `
      <div class="lp-hero">
        <div>
          <div class="lp-kicker">Kelas Interaktif</div>
          <h2>Pahami kalkulus pelan-pelan, slide demi slide.</h2>
          <p class="lp-lead">Bareng Archie, materinya dibahas bertahap. Kamu bisa geser-geser grafiknya sendiri, terus
            ditutup kuis singkat buat ngecek pemahamanmu. Kalau udah paham, latihan di Skill Tree.</p>
          <div class="lp-chips">
            <span>${Icon('mountain')} ${groups().length} level</span><span>${Icon('book')} ${all.length} topik</span><span>${Icon('sliders')} ${graphs} grafik interaktif</span>
          </div>
          ${resume ? `<button class="btn btn-primary btn-lg" onclick="Lessons.open('${resume.t.slug}')">
            ▶ ${rec(resume.t.slug).at ? 'Lanjutin' : 'Mulai'}: ${Icon.of(resume.t.icon)} ${resume.t.title}</button>` : ''}
        </div>
      </div>
      <div class="lp-level-cards">
        ${groups().map(({ level, nodes }) => {
          const ts = nodes.flatMap((n) => n.topics);
          const d = ts.filter((t) => rec(t.slug).done).length;
          const first = ts.find((t) => !rec(t.slug).done) || ts[0];
          return `
            <button class="lp-level-card" onclick="Lessons.open('${first.slug}')">
              <span class="lp-level-card-icon">${Icon.level(level)}</span>
              <small>Level ${level.order}</small>
              <b>${level.title}</b>
              <span class="lp-level-card-sub">${level.subtitle || ''}</span>
              <span class="lp-meter"><i style="width:${ts.length ? Math.round((d / ts.length) * 100) : 0}%"></i></span>
              <span class="lp-level-card-sub">${d}/${ts.length} topik · ${nodes.length} sub-level</span>
            </button>`;
        }).join('')}
      </div>`;
  }

  /* ── input: keyboard & geser ─────────────────────────────────────── */
  function playing() {
    return document.getElementById('page-lesson')?.classList.contains('active')
      && !document.getElementById('lp-player')?.hidden
      && !document.getElementById('lesson-drawer')?.classList.contains('open');
  }

  document.addEventListener('keydown', (e) => {
    if (!playing() || e.target.closest('input, textarea, select')) return;
    if (e.key === 'ArrowRight') { e.preventDefault(); api.next(); }
    if (e.key === 'ArrowLeft') { e.preventDefault(); api.prev(); }
  });

  let touch = null;
  document.addEventListener('touchstart', (e) => {
    const vp = e.target.closest?.('#lp-viewport');
    // Jangan mengganggu slider/grafik GraphLab dan tabel yang digulir ke samping.
    touch = vp && !e.target.closest('.lesson-graphs, .table-scroll, input') ? { x: e.touches[0].clientX, y: e.touches[0].clientY } : null;
  }, { passive: true });
  document.addEventListener('touchend', (e) => {
    if (!touch || !playing()) return;
    const dx = e.changedTouches[0].clientX - touch.x;
    const dy = e.changedTouches[0].clientY - touch.y;
    touch = null;
    if (Math.abs(dx) > 60 && Math.abs(dy) < 50) { if (dx < 0) api.next(); else api.prev(); }
  }, { passive: true });

  /* ── API publik ──────────────────────────────────────────────────── */
  const api = {
    /** Dipanggil Curriculum.load(): gambar ulang daftar isi & sambutan, tutup pemutar. */
    render() {
      topic = null;
      api.close(true);
      renderOutline();
      renderWelcome();
    },
    open(slug) {
      const found = Curriculum.topic(slug);
      if (!found) return;
      if (!document.getElementById('page-lesson')?.classList.contains('active')) Nav.go('lesson');
      api.tab('kelas');
      ({ topic, node } = found);
      slides = buildSlides(topic);
      check = null;
      const r = rec(slug);
      const start = !r.done && r.at > 0 && r.at < slides.length ? r.at : 0;
      slides.slice(0, start).forEach((s) => { s.seen = true; });
      cur = start;
      document.getElementById('lp-welcome').hidden = true;
      document.getElementById('lp-player').hidden = false;
      document.getElementById('lesson-player').classList.add('lp-playing');
      const lvl = levelOf(node);
      document.getElementById('lp-crumb').innerHTML = `${lvl ? `${Icon.level(lvl)} ${lvl.title} › ` : ''}${node.title}`;
      document.getElementById('lp-title').innerHTML = `${Icon.of(topic.icon)} ${topic.title}`;
      renderOutline();
      show(start);
      document.querySelector('.site-main')?.scrollTo({ top: 0 });
    },
    /** Tombol "Pelajari" di drawer topik skill tree. */
    openFromDrawer(slug) {
      if (Drawer.close() === false) return;
      api.open(slug);
    },
    close(silent) {
      topic = null;
      const player = document.getElementById('lp-player');
      if (!player) return;
      player.hidden = true;
      document.getElementById('lp-welcome').hidden = false;
      document.getElementById('lesson-player').classList.remove('lp-playing');
      if (!silent) { SFX.click(); renderOutline(); renderWelcome(); }
    },
    next() {
      if (!topic) return;
      if (hiddenLeft() > 0) {
        slides[cur].shown++;
        applySteps();
        chrome();
        SFX.click();
        [...document.querySelectorAll('#lp-viewport .lp-step.lp-shown')].pop()
          ?.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        return;
      }
      if (cur < slides.length - 1) { SFX.click(); show(cur + 1, 1); return; }
      const nt = nextTopic();
      if (nt) api.open(nt.t.slug);
    },
    prev() {
      if (!topic || cur === 0) return;
      SFX.click();
      slides[cur - 1].seen = true;
      show(cur - 1, -1);
    },
    go(i) {
      if (!topic || i === cur) return;
      SFX.click();
      show(i, i < cur ? -1 : 1);
    },
    answer,
    nextQuestion() {
      if (!check) return;
      check.i++;
      drawCheck();
    },
    retryCheck() {
      check = null;
      runCheck();
    },
    /** Dari slide Rangkuman: buka drawer latihan topik ini di Peta Belajar. */
    practice() {
      const slug = topic?.slug;
      if (!slug) return;
      Nav.go('levelup');
      // langsung ke drawer latihan (bukan modal pilihan riwayat): dari slide Rangkuman niatnya jelas berlatih
      Practice.openTopicFromTree(slug);
    },
    /** Tab halaman Pelajaran: 'kelas' (slide) | 'arsip' (bank soal & referensi). */
    tab(name) {
      document.querySelectorAll('.lesson-tab').forEach((b) => b.classList.toggle('active', b.dataset.ltab === name));
      document.querySelectorAll('.lesson-pane').forEach((p) => p.classList.toggle('active', p.id === `lesson-pane-${name}`));
    },
    /** Status baca topik untuk ringkasan di drawer skill tree. */
    status(slug) {
      const r = rec(slug);
      return r.done ? 'done' : r.at ? 'started' : 'new';
    },
  };
  return api;
})();
