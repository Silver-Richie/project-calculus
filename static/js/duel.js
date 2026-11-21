/**
 * Calculus Bridge — Ranked Duel asinkron (layar penuh), lewat API /api/ranked/… (gamification/ranked_duel.py).
 *
 * Layar: cari lawan → VS (+ kesulitan 10 soal) → 10 soal satu per satu → kunci & skor tiap soal → hasil & bintang.
 * Lawan tampil sebagai pemain (hantu atau bot — server tidak memberi tahu yang mana); hasil lawan per soal
 * ditampilkan setelah kamu menjawab.
 * Server membuka soal & mencatat waktu, lalu menilai jawaban: browser hanya menampilkan dan mengirim pilihan.
 * Skor benar = skor dasar (Mudah 100 / Sedang 200 / Sulit 300) + sisa detik; salah / waktu habis = 0.
 * Menutup layar di tengah duel = menyerah = kalah (dikonfirmasi dulu).
 * Anti-curang: selama duel FocusGuard (app.js) mengawasi keluar tab/jendela → POST keluar-tab.
 * Keluar pertama = soal berjalan dihitung salah + peringatan; kedua = kalah.
 * Memakai RankBadge (leaderboard.js), Avatar (avatar.js), postJSON/SFX/Confetti/FocusGuard (app.js).
 */
const Duel = (() => {
  'use strict';

  let el = null, state = {}, timerRaf = 0, unwatch = null, nextTimer = 0;
  const esc = (t) => String(t ?? '').replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
  const $ = (sel) => el.querySelector(sel);
  const DIFF = { easy: 'Mudah', medium: 'Sedang', hard: 'Sulit' };
  const api = (path, body) => postJSON(`/api/ranked/${path}`, body);

  function mount() {
    if (el) return;
    el = document.createElement('div');
    el.className = 'duel-overlay';
    el.setAttribute('role', 'dialog');
    el.setAttribute('aria-modal', 'true');
    el.setAttribute('aria-label', 'Ranked Duel');
    el.innerHTML = `
      <div class="duel-top">
        <span class="duel-brand">${Icon('swords')} Ranked Duel</span>
        <button type="button" class="btn-close duel-x" aria-label="Tutup duel">×</button>
      </div>
      <div class="duel-body" aria-live="polite"></div>`;
    document.body.appendChild(el);
    el.querySelector('.duel-x').addEventListener('click', close);
    el.addEventListener('keydown', (e) => { if (e.key === 'Escape') close(); });
    el.addEventListener('click', onClick);
  }

  const body = (html) => { $('.duel-body').innerHTML = html; };

  function open() {
    mount();
    el.hidden = false;
    document.body.style.overflow = 'hidden';
    el.querySelector('.duel-x').focus();
    start();
  }

  // ── Cari lawan ────────────────────────────────────────────────────────────
  async function start() {
    clearTimeout(nextTimer);
    state = { phase: 'searching' };
    body(`<div class="duel-center">
      <div class="duel-radar"><span></span><span></span>${Icon('swords')}</div>
      <h3>Lagi nyari lawan selevel…</h3>
      <p class="duel-muted">Nyiapin 10 soal acak lintas fakultas.</p></div>`);
    try {
      const intro = await api('mulai/');
      showVs(intro);
    } catch (err) {
      showRetry(err.status === 400 ? Icon('lock') : Icon('signal-off'), err.message || 'Gagal nyari lawan.', err.status !== 400);
    }
  }

  function showRetry(icon, message, canRetry = true) {
    state.phase = 'closed';
    body(`<div class="duel-center"><div class="duel-big">${icon}</div><p>${esc(message)}</p>
      ${canRetry ? '<button type="button" class="btn btn-primary" data-act="again">Coba lagi</button>' : ''}</div>`);
  }

  function card(p, side) {
    const sub = [p.faculty, p.campus].filter(Boolean).join(' · ');
    return `<div class="duel-card ${side}">
      ${Avatar.html(p.avatar, p.name, p.username, 'duel-avatar')}
      <b>${esc(p.name)}</b><small>${esc(sub)}</small>
      ${RankBadge.html(p.rank)}<span class="duel-lv">Lv ${p.level}</span></div>`;
  }

  function showVs(m) {
    state = { phase: 'match', id: m.match_id, me: m.you, opp: m.opponent, total: m.total, diffs: m.difficulties,
              scores: { me: 0, opp: 0 }, results: [], left: 0 };
    startWatching();
    SFX.click();
    const r = m.rules;
    const chips = m.difficulties.map((d, i) => `<span class="duel-chip ${d}" title="Soal ${i + 1}">${DIFF[d]}</span>`).join('');
    body(`<div class="duel-vs">${card(m.you, 'me')}<div class="duel-vs-mark">VS</div>${card(m.opponent, 'opp')}</div>
      <p class="duel-center duel-muted">Kamu dan lawan dapat 10 soal yang sama persis, urutannya pun sama.</p>
      <div class="duel-chips" aria-label="Kesulitan 10 soal">${chips}</div>
      <p class="duel-center duel-muted">Benar = skor dasar + sisa detik · Mudah ${r.easy.base} (${r.easy.time} dtk) ·
        Sedang ${r.medium.base} (${r.medium.time} dtk) · Sulit ${r.hard.base} (${r.hard.time} dtk)</p>
      <p class="duel-center duel-muted">${Icon('warning')} Jangan pindah tab: sekali = soal itu dihitung salah, dua kali = kalah.</p>
      <div class="duel-actions"><button type="button" class="btn btn-accent" data-act="go">${Icon('play')} Mulai</button></div>`);
  }

  // ── Soal ──────────────────────────────────────────────────────────────────
  async function nextQuestion() {
    try {
      const { question } = await api(`${state.id}/soal/`);
      showQuestion(question);
    } catch (err) {
      showRetry(Icon('signal-off'), err.message || 'Soal gagal dimuat.');
    }
  }

  function scoreboard() {
    const dots = Array.from({ length: state.total }, (_, i) => {
      const r = state.results[i];
      return `<i class="${r ? (r.me ? 'ok' : 'bad') : i === state.index ? 'now' : ''}"></i>`;
    }).join('');
    return `<div class="duel-score">
      <div class="duel-side me"><b>${esc(state.me.name)}</b><span class="duel-pts">${state.scores.me}</span></div>
      <div class="duel-dots" aria-label="Soal ${state.index + 1} dari ${state.total}">${dots}</div>
      <div class="duel-side opp"><b>${esc(state.opp.name)}</b><span class="duel-pts">${state.scores.opp}</span></div></div>`;
  }

  function showQuestion(q) {
    state.index = q.index;
    state.answered = false;
    body(`${scoreboard()}
      <div class="duel-timer"><div class="duel-timer-fill"></div></div>
      <div class="duel-q">
        <p class="duel-muted">Soal ${q.index + 1} dari ${q.total} · <span class="duel-chip ${q.difficulty}">${esc(q.difficulty_label)}</span>
          ${q.base} poin + sisa detik · ${esc(q.topic)}</p>
        <div class="quiz-prompt">${q.prompt}</div>
        <div class="options-list">${q.options.map((o, i) => `
          <button type="button" class="option-btn" data-option="${o.id}">
            <span class="opt-letter">${'ABCD'[i]}</span><span>${o.text}</span></button>`).join('')}
        </div>
        <p class="duel-note" role="status"></p>
      </div>`);
    // Sisa waktu dari tenggat server (aman bila halaman sempat dimuat ulang).
    runTimer(q.time_limit * 1000, Math.max(0, q.deadline - Date.now()));
  }

  function runTimer(limit, left0) {
    cancelAnimationFrame(timerRaf);
    const start = performance.now();
    const step = () => {
      const left = Math.max(0, left0 - (performance.now() - start));
      const fill = $('.duel-timer-fill');
      if (!fill) return;
      fill.style.width = `${(left / limit) * 100}%`;
      fill.classList.toggle('low', left < limit * 0.25);
      if (left <= 0) {
        if (!state.answered) {
          el.querySelectorAll('.option-btn').forEach((b) => { b.disabled = true; });
          $('.duel-note').innerHTML = `${Icon('clock')} Waktu habis!`;
          submit(null);
        }
        return;
      }
      timerRaf = requestAnimationFrame(step);
    };
    timerRaf = requestAnimationFrame(step);
  }

  function choose(btn) {
    if (state.answered || btn.disabled) return;
    btn.classList.add('selected');
    submit(Number(btn.dataset.option));
  }

  async function submit(option) {
    if (state.answered) return;
    state.answered = true;
    el.querySelectorAll('.option-btn').forEach((b) => { b.disabled = true; });
    try {
      showReveal(await api(`${state.id}/jawab/`, { index: state.index, option }));
    } catch (err) {
      const note = $('.duel-note');
      if (note) note.textContent = err.message || 'Jawaban gagal dikirim.';
    }
  }

  function showReveal(r, voided = false) {
    cancelAnimationFrame(timerRaf);
    state.scores = { me: r.totals.you.points, opp: r.totals.opponent.points };
    state.results[r.index] = { me: r.you.correct };
    el.querySelectorAll('.option-btn').forEach((b) => {
      const id = Number(b.dataset.option);
      b.disabled = true;
      if (id === r.correct_option) b.classList.add('correct');
      else if (id === r.you.option) b.classList.add('incorrect');
    });
    r.you.correct ? SFX.correct() : SFX.wrong();
    const board = $('.duel-score');
    if (board) board.outerHTML = scoreboard();
    $('.duel-timer-fill')?.style.setProperty('width', '0%');
    const opp = r.opponent;
    const note = $('.duel-note');
    if (note) {
      note.innerHTML = `${voided ? `${Icon('x')} Kamu pindah tab, soal ini dihitung salah.`
        : r.you.correct ? `✓ Bener! <b>+${r.you.points}</b>` : '✗ Belum tepat. +0'} ·
        ${esc(state.opp.name)}: ${opp.correct ? `bener <b>+${opp.points}</b> (${(opp.ms / 1000).toFixed(1)} dtk)` : 'salah'}`;
    }
    if (r.result) {
      nextTimer = setTimeout(() => showResult(r.result), 1600);
      return;
    }
    nextTimer = setTimeout(() => { if (state.phase === 'match') nextQuestion(); }, 1800);
  }

  // ── Anti-curang ───────────────────────────────────────────────────────────
  function startWatching() {
    stopWatching();
    unwatch = FocusGuard.watch({ leave: onLeave });
  }
  function stopWatching() {
    unwatch?.();
    unwatch = null;
    FocusGuard.dismiss();
  }

  async function onLeave() {
    if (state.phase !== 'match') return;
    state.left += 1;
    try {
      const r = await api(`${state.id}/keluar-tab/`);
      if (!r || r.forfeit === undefined) return;
      if (r.forfeit) return showResult(r.result);
      if (r.reveal) {
        state.answered = true;
        clearTimeout(nextTimer);
        showReveal(r.reveal, true);
      }
      FocusGuard.warn('Eits, jangan pindah tab!',
        `${r.voided != null ? `Soal ${r.voided + 1} dihitung salah. ` : ''}Sekali lagi keluar, kamu <b>kalah</b>.`);
    } catch (_) { /* koneksi putus: server tetap menilai soal yang kedaluwarsa sebagai salah */ }
  }

  // ── Hasil ─────────────────────────────────────────────────────────────────
  function showResult(res) {
    cancelAnimationFrame(timerRaf);
    clearTimeout(nextTimer);
    stopWatching();
    state.phase = 'done';
    const title = { win: `Menang! ${Icon('trophy')}`, lose: 'Kalah', draw: 'Imbang' }[res.verdict];
    const unit = res.apex ? ' Apex Points' : ' ★';
    const change = res.delta > 0 ? `+${res.delta}${unit}` : res.delta < 0 ? `${res.delta}${unit}`
      : res.verdict === 'draw' ? (res.apex ? 'Apex Points tetap' : 'Bintang tetap')
      : res.shield_used ? `${Icon('shield')} Streak Shield nyelamatin ${res.apex ? 'poinmu' : 'bintangmu'}`
      : res.terra_safe ? 'Bintang aman (di Terra III–II, kalah gak ngurangin bintang)' : 'Tetap';
    if (res.verdict === 'win') { SFX.fanfare(); Confetti.burst(); }
    if (res.gems_awarded && typeof State !== 'undefined') State.setGems(State.get().gems + res.gems_awarded);
    const total = state.total || 10;
    body(`<div class="duel-center duel-result ${res.verdict}">
      <h2>${title}</h2>
      ${res.forfeit ? `<p class="duel-muted">${state.left >= 2 ? `${Icon('x')} Kamu pindah tab 2 kali, jadi dihitung menyerah.` : 'Kamu keluar dari duel.'}</p>` : ''}
      <div class="duel-final">
        <div><b>${res.you.points}</b><small>poin kamu · ${res.you.correct}/${total} benar</small></div>
        <div><b>${res.opponent.points}</b><small>poin ${esc(state.opp?.name || 'lawan')} · ${res.opponent.correct}/${total} benar</small></div>
      </div>
      <p class="duel-stars ${res.delta > 0 ? 'up' : res.delta < 0 ? 'down' : ''}">${change}</p>
      ${res.gems_awarded ? `<p class="duel-muted">${Icon('diamond')} +${res.gems_awarded} diamond</p>` : ''}
      ${RankBadge.html(res.rank, true)}
      <div class="duel-actions">
        <button type="button" class="btn btn-accent" data-act="again">${Icon('swords')} Duel lagi</button>
        <button type="button" class="btn btn-outline" data-act="close">Tutup</button>
      </div></div>`);
    if (typeof Leaderboard !== 'undefined') Leaderboard.setMyRank(res.rank);
    if (typeof Ranked !== 'undefined') Ranked.update(res.rank, res.shield_used);
  }

  async function close() {
    if (!el || el.hidden) return;
    if (state.phase === 'match') {
      if (!FocusGuard.confirm('Keluar di tengah duel = KALAH. Yakin mau keluar?')) return;
      try { await api(`${state.id}/menyerah/`); } catch (_) { /* duel lama otomatis dianggap menyerah saat mulai duel baru */ }
    }
    state.phase = 'closed';
    stopWatching();
    cancelAnimationFrame(timerRaf);
    clearTimeout(nextTimer);
    el.hidden = true;
    document.body.style.overflow = '';
    document.getElementById('duel-start-btn')?.focus();
  }

  function onClick(e) {
    const opt = e.target.closest('.option-btn');
    if (opt) return choose(opt);
    const act = e.target.closest('[data-act]')?.dataset.act;
    if (act === 'go') nextQuestion();
    else if (act === 'close') close();
    else if (act === 'again') start();
  }

  function init() {
    const btn = document.getElementById('duel-start-btn');
    if (btn) btn.addEventListener('click', open);
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();

  return { open, close };
})();
