/**
 * Calculus Bridge — Duel kalkulus real-time (layar penuh), terhubung ke ws/duel/ (gamification/consumers.py).
 *
 * Layar: cari lawan → VS → 5 soal (pengatur waktu, skor kedua pemain) → kunci tiap soal → hasil & bintang.
 * Semua penilaian & waktu resmi ada di server; browser hanya menampilkan dan mengirim pilihan.
 * Menutup layar di tengah duel = keluar = kalah (dikonfirmasi dulu).
 * Anti-curang: selama duel FocusGuard (app.js) mengawasi keluar tab/jendela dan mengirim {"type": "left"}.
 * Keluar pertama = soal berjalan dianggap salah + peringatan; kedua = kalah (aturan di duel.leave_tab).
 * Memakai RankBadge (leaderboard.js) dan SFX/Confetti/FocusGuard (app.js).
 */
const Duel = (() => {
  'use strict';

  let ws = null, el = null, state = {}, timerRaf = 0, unwatch = null;
  const esc = (t) => String(t ?? '').replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
  const $ = (sel) => el.querySelector(sel);

  function mount() {
    if (el) return;
    el = document.createElement('div');
    el.className = 'duel-overlay';
    el.setAttribute('role', 'dialog');
    el.setAttribute('aria-modal', 'true');
    el.setAttribute('aria-label', 'Duel kalkulus');
    el.innerHTML = `
      <div class="duel-top">
        <span class="duel-brand">⚔️ Duel Kalkulus</span>
        <button type="button" class="btn-close duel-x" aria-label="Tutup duel">×</button>
      </div>
      <div class="duel-body" aria-live="polite"></div>`;
    document.body.appendChild(el);
    el.querySelector('.duel-x').addEventListener('click', close);
    el.addEventListener('keydown', (e) => { if (e.key === 'Escape') close(); });
    el.addEventListener('click', onClick);
  }

  const body = (html) => { $('.duel-body').innerHTML = html; };

  // ── Koneksi ───────────────────────────────────────────────────────────────
  function open() {
    mount();
    el.hidden = false;
    document.body.style.overflow = 'hidden';
    el.querySelector('.duel-x').focus();
    connect();
  }

  function connect() {
    state = { phase: 'connecting' };
    body('<div class="duel-center"><div class="duel-spin"></div><p>Menghubungkan…</p></div>');
    const proto = location.protocol === 'https:' ? 'wss' : 'ws';
    ws = new WebSocket(`${proto}://${location.host}/ws/duel/`);
    ws.onopen = () => send({ type: 'queue' });
    ws.onmessage = (e) => handle(JSON.parse(e.data));
    ws.onclose = () => {
      if (['connecting', 'queued', 'match'].includes(state.phase)) {
        body(`<div class="duel-center"><div class="duel-big">📡</div><p>${esc(state.closeMsg || 'Koneksi duel terputus.')}</p>
          <button type="button" class="btn btn-primary" data-act="again">Coba lagi</button></div>`);
        state.phase = 'closed';
      }
      cancelAnimationFrame(timerRaf);
      stopWatching();
    };
  }

  /** Mulai/berhenti mengawasi keluar tab (hanya selama duel berlangsung). */
  function startWatching() {
    stopWatching();
    unwatch = FocusGuard.watch({ leave: () => { state.left = (state.left || 0) + 1; send({ type: 'left' }); } });
  }
  function stopWatching() {
    unwatch?.();
    unwatch = null;
    FocusGuard.dismiss();
  }

  const send = (msg) => { if (ws && ws.readyState === WebSocket.OPEN) ws.send(JSON.stringify(msg)); };

  function close() {
    if (!el || el.hidden) return;
    if (state.phase === 'match' && !FocusGuard.confirm('Keluar di tengah duel dihitung KALAH. Yakin keluar?')) return;
    state.phase = 'closed';
    stopWatching();
    if (ws) ws.close();
    cancelAnimationFrame(timerRaf);
    el.hidden = true;
    document.body.style.overflow = '';
    document.getElementById('duel-start-btn')?.focus();
  }

  // ── Pesan server ──────────────────────────────────────────────────────────
  function handle(m) {
    if (m.type === 'queued') return showSearching(m.timeout);
    if (m.type === 'no_opponent') return showRetry('🕐', m.message);
    if (m.type === 'cancelled') return close();
    if (m.type === 'matched') return showVs(m);
    if (m.type === 'question') return showQuestion(m);
    if (m.type === 'answered') return;
    if (m.type === 'progress') return markOpponent(m.index);
    if (m.type === 'reveal') return showReveal(m);
    if (m.type === 'tab_warning') return showTabWarning(m);
    if (m.type === 'finished') return showResult(m);
    if (m.type === 'error') {
      if (m.code === 'level') { state.closeMsg = m.message; state.phase = 'locked'; return showRetry('🔒', m.message, false); }
      const note = $('.duel-note');
      if (note) note.textContent = m.message;
    }
  }

  function showSearching(timeout) {
    state.phase = 'queued';
    const start = Date.now();
    body(`<div class="duel-center">
      <div class="duel-radar"><span></span><span></span>⚔️</div>
      <h3>Mencari lawan setara…</h3>
      <p class="duel-muted">Lawan dicari dari pemain se-Indonesia dengan kemampuan mirip. <b class="duel-wait">0</b> dtk</p>
      <button type="button" class="btn btn-outline" data-act="cancel">Batal</button></div>`);
    const tick = () => {
      if (state.phase !== 'queued' || !el || el.hidden) return;
      const w = $('.duel-wait');
      if (w) w.textContent = Math.min(timeout, Math.floor((Date.now() - start) / 1000));
      setTimeout(tick, 500);
    };
    tick();
  }

  function showRetry(icon, message, canRetry = true) {
    state.phase = 'closed';
    body(`<div class="duel-center"><div class="duel-big">${icon}</div><p>${esc(message)}</p>
      ${canRetry ? '<button type="button" class="btn btn-primary" data-act="again">Cari lagi</button>' : ''}</div>`);
  }

  function card(p, side) {
    const sub = [p.faculty, p.campus].filter(Boolean).join(' · ');
    return `<div class="duel-card ${side}">
      <div class="duel-avatar">${esc((p.name[0] || '?').toUpperCase())}</div>
      <b>${esc(p.name)}</b><small>${esc(sub)}</small>
      ${RankBadge.html(p.rank)}<span class="duel-lv">Lv ${p.level}</span></div>`;
  }

  function showVs(m) {
    state = { phase: 'match', me: m.you, opp: m.opponent, total: m.total, scores: { me: 0, opp: 0 }, results: [] };
    startWatching();
    SFX.click();
    body(`<div class="duel-vs">${card(m.you, 'me')}<div class="duel-vs-mark">VS</div>${card(m.opponent, 'opp')}</div>
      <p class="duel-center duel-muted">${m.total} soal identik · ${m.time_limit} detik per soal · bersiap…</p>
      <p class="duel-center duel-muted">⚠️ Jangan keluar dari tab ini selama duel: sekali = soal dihitung salah, dua kali = kalah.</p>`);
  }

  function scoreboard() {
    const dots = Array.from({ length: state.total }, (_, i) => {
      const r = state.results[i];
      return `<i class="${r ? (r.me ? 'ok' : 'bad') : i === state.index ? 'now' : ''}"></i>`;
    }).join('');
    return `<div class="duel-score">
      <div class="duel-side me"><b>${esc(state.me.name)}</b><span class="duel-pts">${state.scores.me}</span></div>
      <div class="duel-dots" aria-label="Soal ${state.index + 1} dari ${state.total}">${dots}</div>
      <div class="duel-side opp"><b>${esc(state.opp.name)}</b><span class="duel-pts">${state.scores.opp}</span>
        <small class="duel-opp-status"></small></div></div>`;
  }

  function showQuestion(q) {
    state.index = q.index;
    state.answered = false;
    body(`${scoreboard()}
      <div class="duel-timer"><div class="duel-timer-fill"></div></div>
      <div class="duel-q">
        <p class="duel-muted">Soal ${q.index + 1} dari ${q.total} · ${esc(q.topic)}</p>
        <div class="quiz-prompt">${q.prompt}</div>
        <div class="options-list">${q.options.map((o, i) => `
          <button type="button" class="option-btn" data-option="${o.id}">
            <span class="opt-letter">${'ABCD'[i]}</span><span>${o.text}</span></button>`).join('')}
        </div>
        <p class="duel-note" role="status"></p>
      </div>`);
    runTimer(q.time_limit * 1000);
  }

  function runTimer(limit) {
    cancelAnimationFrame(timerRaf);
    const start = performance.now();
    const step = () => {
      const left = Math.max(0, limit - (performance.now() - start));
      const fill = $('.duel-timer-fill');
      if (!fill) return;
      fill.style.width = `${(left / limit) * 100}%`;
      fill.classList.toggle('low', left < limit * 0.25);
      if (left <= 0) {
        if (!state.answered) {
          el.querySelectorAll('.option-btn').forEach((b) => { b.disabled = true; });
          $('.duel-note').textContent = '⏰ Waktu habis!';
        }
        return;
      }
      timerRaf = requestAnimationFrame(step);
    };
    timerRaf = requestAnimationFrame(step);
  }

  function choose(btn) {
    if (state.answered || btn.disabled) return;
    state.answered = true;
    btn.classList.add('selected');
    el.querySelectorAll('.option-btn').forEach((b) => { b.disabled = true; });
    $('.duel-note').textContent = 'Jawaban terkirim. Menunggu lawan…';
    send({ type: 'answer', index: state.index, option: Number(btn.dataset.option) });
  }

  function showTabWarning(m) {
    if (m.voided != null && m.voided === state.index) {
      state.answered = true;
      el.querySelectorAll('.option-btn').forEach((b) => { b.disabled = true; });
      const note = $('.duel-note');
      if (note) note.textContent = '🚫 Kamu keluar dari tab: soal ini dihitung salah.';
    }
    FocusGuard.warn('Jangan keluar dari tab!',
      `${m.voided != null ? `Soal ${m.voided + 1} dihitung salah. ` : ''}Keluar sekali lagi = <b>kalah</b>
       (dihitung keluar dari duel, bintang bisa berkurang).`);
  }

  function markOpponent(index) {
    const s = $('.duel-opp-status');
    if (s && index === state.index) s.textContent = '✓ sudah menjawab';
  }

  function showReveal(r) {
    cancelAnimationFrame(timerRaf);
    const meId = String(state.me.id), oppId = String(state.opp.id);
    const mine = r.players[meId], theirs = r.players[oppId];
    state.scores = { me: r.totals[meId].points, opp: r.totals[oppId].points };
    state.results[r.index] = { me: mine.correct };
    el.querySelectorAll('.option-btn').forEach((b) => {
      const id = Number(b.dataset.option);
      b.disabled = true;
      if (id === r.correct_option) b.classList.add('correct');
      else if (id === mine.option) b.classList.add('incorrect');
    });
    mine.correct ? SFX.correct() : SFX.wrong();
    const board = $('.duel-score');
    if (board) board.outerHTML = scoreboard();
    $('.duel-timer-fill')?.style.setProperty('width', '0%');
    $('.duel-note').innerHTML = `${mine.correct ? `✓ Benar! <b>+${mine.points}</b>` : '✗ Belum tepat. +0'} ·
      Lawan: ${theirs.correct ? `benar <b>+${theirs.points}</b>` : 'salah'}${r.last ? '' : ' · soal berikutnya segera…'}`;
  }

  function showResult(m) {
    cancelAnimationFrame(timerRaf);
    stopWatching();
    state.phase = 'done';
    const me = m.you;
    const oppId = Object.keys(m.players).find((id) => id !== String(state.me?.id));
    const opp = m.players[oppId] || {};
    const title = { win: 'Menang! 🏆', lose: 'Kalah', draw: 'Imbang 🤝' }[me.verdict];
    const stars = me.star_delta > 0 ? `+${me.star_delta} ★` : me.star_delta < 0 ? `${me.star_delta} ★`
      : me.verdict === 'draw' ? 'Bintang tetap'
      : me.shield_used ? `${Icon('shield')} Perisai Bintang melindungi bintangmu`
      : me.rank.tier === 'terra' ? 'Bintang tetap (di Terra kalah tidak mengurangi bintang)'
      : '★ Bintang dilindungi (kalah tipis)';
    if (me.verdict === 'win') { SFX.fanfare(); Confetti.burst(); }
    if (me.gems_awarded && typeof State !== 'undefined') State.setGems(State.get().gems + me.gems_awarded);
    body(`<div class="duel-center duel-result ${me.verdict}">
      <h2>${title}</h2>
      ${m.forfeit ? `<p class="duel-muted">${me.verdict === 'win' ? 'Lawan keluar dari duel.'
        : state.left >= 2 ? '🚫 Kamu keluar dari tab 2 kali, jadi dihitung keluar dari duel.' : 'Kamu keluar dari duel.'}</p>` : ''}
      <div class="duel-final">
        <div><b>${me.points}</b><small>poin kamu · ${me.correct}/${state.total || 5} benar</small></div>
        <div><b>${opp.points ?? 0}</b><small>poin lawan · ${opp.correct ?? 0}/${state.total || 5} benar</small></div>
      </div>
      <p class="duel-stars ${me.star_delta > 0 ? 'up' : me.star_delta < 0 ? 'down' : ''}">${stars}</p>
      ${me.gems_awarded ? `<p class="duel-muted">${Icon('diamond')} +${me.gems_awarded} diamond</p>` : ''}
      ${RankBadge.html(me.rank, true)}
      <div class="duel-actions">
        <button type="button" class="btn btn-accent" data-act="again">⚔️ Duel lagi</button>
        <button type="button" class="btn btn-outline" data-act="close">Tutup</button>
      </div></div>`);
    if (typeof Leaderboard !== 'undefined') Leaderboard.setMyRank(me.rank);
    if (typeof Ranked !== 'undefined') Ranked.update(me.rank, me.shield_used);
  }

  function onClick(e) {
    const opt = e.target.closest('.option-btn');
    if (opt) return choose(opt);
    const act = e.target.closest('[data-act]')?.dataset.act;
    if (act === 'cancel') send({ type: 'cancel' });
    else if (act === 'close') close();
    else if (act === 'again') {
      if (ws && ws.readyState === WebSocket.OPEN && state.phase === 'done') { state.phase = 'connecting'; send({ type: 'queue' }); }
      else { if (ws) ws.close(); connect(); }
    }
  }

  function init() {
    const btn = document.getElementById('duel-start-btn');
    if (btn) btn.addEventListener('click', open);
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();

  return { open, close };
})();
