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
      <div class="duel-split">
        <div class="duel-body" aria-live="polite"></div>
        <aside class="duel-board" aria-label="Papan tulis"></aside>
      </div>`;
    document.body.appendChild(el);
    el.querySelector('.duel-x').addEventListener('click', close);
    el.addEventListener('keydown', (e) => { if (e.key === 'Escape') close(); });
    el.addEventListener('click', onClick);
  }

  const body = (html) => { $('.duel-body').innerHTML = html; };

  /**
   * Papan tulis duel. Dipasang sekali di luar .duel-body supaya coretan tidak ikut
   * terhapus tiap soal dirender ulang; tiap soal punya papannya sendiri lewat load(kunci).
   * Hanya tampil selama soal berjalan, bukan di layar cari lawan / VS / hasil.
   */
  function showBoard(on, key) {
    if (!el) return;
    el.classList.toggle('with-board', on);
    if (!on || typeof Whiteboard === 'undefined') return;
    Whiteboard.mount($('.duel-board'))?.load(key);
  }

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
    showBoard(false);
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
    const oppPct = Math.min(100, (state.oppDone || 0) / state.total * 100);
    return `<div class="duel-score">
      <div class="duel-side me">${Avatar.html(state.me.avatar, state.me.name, state.me.username, 'duel-mini')}
        <div><b>${esc(state.me.name)}</b><span class="duel-pts">${state.scores.me}</span></div></div>
      <div class="duel-dots" aria-label="Soal ${state.index + 1} dari ${state.total}">${dots}</div>
      <div class="duel-side opp">
        <div><b>${esc(state.opp.name)}</b><span class="duel-pts">${state.scores.opp}</span></div>
        ${Avatar.html(state.opp.avatar, state.opp.name, state.opp.username, 'duel-mini duel-opp-av')}
      </div>
      <div class="duel-opp-track" aria-label="Progres lawan ${state.oppDone || 0} dari ${state.total}"><i style="width:${oppPct}%"></i></div>
      <small class="duel-opp-status" role="status"></small></div>`;
  }

  function showQuestion(q) {
    state.index = q.index;
    state.answered = false;
    state.oppDone = q.opponent_done;
    clearTimeout(state.oppTimer);
    showBoard(true, `duel:${state.id}:${q.index}`);
    body(`${scoreboard()}
      <div class="duel-timer-row"><div class="duel-timer"><div class="duel-timer-fill"></div></div><b class="duel-sec" aria-label="Sisa detik"></b></div>
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
    // Tekanan: lawan "menjawab" tepat pada waktunya (server hanya memberi waktu, bukan benar/salahnya).
    if (q.opponent_ms != null) {
      const startedAt = q.deadline - q.time_limit * 1000;
      state.oppTimer = setTimeout(() => enemyAnswered(q.index), Math.max(0, startedAt + q.opponent_ms - Date.now()));
    }
  }

  function enemyAnswered(index) {
    if (state.phase !== 'match' || state.index !== index || state.answered) return;
    state.oppDone = index + 1;
    const bar = $('.duel-opp-track i');
    if (bar) bar.style.width = `${Math.min(100, state.oppDone / state.total * 100)}%`;
    $('.duel-opp-track')?.classList.add('hit');
    $('.duel-opp-av')?.classList.add('glow');
    $('.duel-score')?.classList.add('opp-hit');
    const s = $('.duel-opp-status');
    if (s) s.innerHTML = `${Icon('bolt')} ${esc(state.opp.name)} udah jawab!`;
    SFX.click();
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
      const sec = $('.duel-sec');
      if (sec) sec.textContent = Math.ceil(left / 1000);
      $('.duel-timer-row')?.classList.toggle('critical', left > 0 && left <= 10000);
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
    clearTimeout(state.oppTimer);
    state.oppDone = r.index + 1;
    $('.duel-timer-row')?.classList.remove('critical');
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

  // ── Hasil: splash VICTORY/DEFEAT → rincian bertahap → animasi rank ─────────
  const WAIT = (ms) => new Promise((r) => { nextTimer = setTimeout(r, ms); });
  const REDUCED = () => window.matchMedia?.('(prefers-reduced-motion: reduce)').matches;

  function starSlots(r, extra = '') {
    return `<span class="fx-stars ${extra}">${Array.from({ length: r.max_stars }, (_, i) =>
      `<span class="fx-star${i < r.stars ? ' on' : ''}" data-i="${i}">★</span>`).join('')}</span>`;
  }

  /** Odometer: tiap digit satu kolom 0–9 yang digeser vertikal (transform), mis. 2400 → 2415. */
  function odoHTML(value, len) {
    const digits = String(Math.max(0, value)).padStart(len, '0').split('');
    return `<span class="fx-odo" aria-label="${value} Apex Points">${digits.map((d, i) => `<span class="odo-d">
      <span class="odo-col" style="--d:${d};--k:${len - 1 - i}">${'0123456789'.split('').map((x) => `<i>${x}</i>`).join('')}</span></span>`).join('')}
      <small>AP</small></span>`;
  }
  function rollOdo(node, value, len) {
    String(Math.max(0, value)).padStart(len, '0').split('').forEach((d, i) => {
      const col = node.querySelectorAll('.odo-col')[i];
      if (col) col.style.setProperty('--d', d);
    });
  }

  function rankFxHTML(res) {
    const b = res.rank_before, a = res.rank;
    const emblem = (t) => RankEmblem.svg(t, { size: 84, animated: true, label: `Lambang ${t}` });
    const top = `<div class="fx-emblem">${emblem(b.tier)}</div><p class="fx-label">${esc(b.label)}</p>`;
    let mid;
    if (b.tier === 'apex') {
      const end = a.tier === 'apex' ? a.apex_points : 0;
      mid = odoHTML(b.apex_points || 0, Math.max(String(b.apex_points || 0).length, String(end).length, 2));
    } else {
      mid = starSlots(b);
    }
    return `<div class="fx-rank" aria-live="polite">${top}<div class="fx-mid">${mid}
      ${res.shield_used ? `<span class="fx-shield" aria-hidden="true">${Icon('shield')}</span>` : ''}</div>
      <p class="fx-note"></p></div>`;
  }

  /** Urutan animasi rank sesuai hasil (menang/kalah/shield/Apex). */
  async function runRankFx(res) {
    const box = $('.fx-rank');
    if (!box) return;
    const b = res.rank_before, a = res.rank;
    const note = (html, cls = '') => { const n = box.querySelector('.fx-note'); n.className = `fx-note show ${cls}`; n.innerHTML = html; };
    const promoted = a.label !== b.label && res.delta > 0, demoted = a.label !== b.label && res.delta < 0;
    const swapTo = (r) => {
      box.querySelector('.fx-emblem').innerHTML = RankEmblem.svg(r.tier, { size: 84, animated: true, label: `Lambang ${r.label}` });
      box.querySelector('.fx-emblem').classList.add('fx-pop');
      box.querySelector('.fx-label').textContent = r.label;
      box.querySelector('.fx-mid').innerHTML = r.max_stars == null ? odoHTML(r.apex_points || 0, 2) : starSlots(r);
    };

    // Kalah tapi punya Streak Shield: perisai menahan serangan, lalu perisainya yang pecah.
    if (res.shield_used) {
      const sh = box.querySelector('.fx-shield');
      sh.classList.add('block');
      SFX.click();
      await WAIT(900);
      sh.classList.add('broken');
      note(`${Icon('shield')} Streak Shield menahan kekalahan — ${b.tier === 'apex' ? 'Apex Points' : 'bintang'} kamu tetap utuh`);
      return;
    }

    if (b.tier === 'apex') {                                         // Apex: odometer poin
      const odo = box.querySelector('.fx-odo');
      const end = a.tier === 'apex' ? a.apex_points : 0;
      const len = odo.querySelectorAll('.odo-col').length;
      odo.classList.add(res.delta >= 0 ? 'up' : 'down');
      rollOdo(odo, end, len);
      await WAIT(1300);
      note(res.delta > 0 ? `+${res.delta} Apex Points` : res.delta < 0 ? `${res.delta} Apex Points` : 'Apex Points tetap', res.delta > 0 ? 'up' : res.delta < 0 ? 'down' : '');
      if (a.tier !== 'apex') { await WAIT(700); swapTo(a); note(`Turun ke ${esc(a.label)}`, 'down'); }
      return;
    }

    if (res.delta > 0) {                                             // Menang: slot kosong terisi menyala
      const stars = [...box.querySelectorAll('.fx-star')];
      const from = b.stars, to = promoted ? stars.length : Math.min(stars.length, a.stars);
      for (let i = from; i < to; i += 1) {
        stars[i].classList.add('on', 'gain');
        SFX.correct();
        await WAIT(420);
      }
      if (promoted) {
        await WAIT(450);
        swapTo(a);
        if (a.max_stars != null) box.querySelectorAll('.fx-star.on').forEach((s) => s.classList.add('gain'));
        note(`Naik ke ${esc(a.label)}!`, 'up');
        SFX.fanfare();
      } else {
        note(`+${res.delta} ★`, 'up');
      }
      return;
    }

    if (res.delta < 0) {                                             // Kalah: bintang terakhir bergetar lalu pecah
      const stars = [...box.querySelectorAll('.fx-star')];
      const victim = stars[Math.max(0, b.stars - 1)];
      victim?.classList.add('shake');
      await WAIT(650);
      victim?.classList.add('shatter');
      SFX.wrong();
      await WAIT(650);
      if (demoted) { swapTo(a); note(`Turun ke ${esc(a.label)}`, 'down'); } else note('−1 ★', 'down');
      return;
    }

    note(res.verdict === 'draw' ? 'Imbang — bintang tetap'
      : res.terra_safe ? 'Bintang aman (di Terra III–II, kalah gak ngurangin bintang)' : 'Tetap');
  }

  function countUp(node, value, ms = 900) {
    const start = performance.now();
    const step = (now) => {
      const t = Math.min(1, (now - start) / ms);
      node.textContent = Math.round(value * (1 - (1 - t) ** 3));
      if (t < 1) requestAnimationFrame(step);
    };
    requestAnimationFrame(step);
  }

  async function showResult(res) {
    cancelAnimationFrame(timerRaf);
    clearTimeout(nextTimer);
    clearTimeout(state.oppTimer);
    stopWatching();
    showBoard(false);
    state.phase = 'done';
    const word = { win: 'VICTORY', lose: 'DEFEAT', draw: 'DRAW' }[res.verdict];
    const total = state.total || 10;
    if (res.verdict === 'win') SFX.fanfare(); else if (res.verdict === 'lose') SFX.wrong();
    if (res.gems_awarded && typeof State !== 'undefined') State.setGems(State.get().gems + res.gems_awarded);
    body(`<div class="duel-splash ${res.verdict}"><h2 class="duel-splash-word" aria-label="${res.verdict === 'win' ? 'Menang' : res.verdict === 'lose' ? 'Kalah' : 'Imbang'}">${word}</h2></div>
      <div class="duel-result ${res.verdict}">
        ${res.forfeit ? `<p class="duel-muted duel-stagger" style="--i:0">${state.left >= 2 ? `${Icon('x')} Kamu pindah tab 2 kali, jadi dihitung menyerah.` : 'Kamu keluar dari duel.'}</p>` : ''}
        <div class="duel-final">
          <div class="duel-stagger me" style="--i:1"><b data-count="${res.you.points}">0</b><small>poin kamu · ${res.you.correct}/${total} benar</small></div>
          <div class="duel-stagger opp" style="--i:2"><b data-count="${res.opponent.points}">0</b><small>poin ${esc(state.opp?.name || 'lawan')} · ${res.opponent.correct}/${total} benar</small></div>
        </div>
        <div class="duel-stagger" style="--i:3">${rankFxHTML(res)}</div>
        ${res.gems_awarded ? `<p class="duel-muted duel-stagger" style="--i:4">${Icon('diamond')} +${res.gems_awarded} diamond</p>` : ''}
        <div class="duel-actions duel-stagger" style="--i:5">
          <button type="button" class="btn btn-accent" data-act="again">${Icon('swords')} Duel lagi</button>
          <button type="button" class="btn btn-outline" data-act="close">Tutup</button>
        </div></div>`);
    if (typeof Leaderboard !== 'undefined') Leaderboard.setMyRank(res.rank);
    if (typeof Ranked !== 'undefined') Ranked.update(res.rank, res.shield_used);
    if (typeof State !== 'undefined') State.setStreak(res.streak);
    const fast = REDUCED();
    if (res.verdict === 'win' && !fast) Confetti.burst();
    await WAIT(fast ? 50 : 1500);                                     // splash raksasa dulu
    $('.duel-splash')?.classList.add('settled');
    $('.duel-result')?.classList.add('show');                         // rincian muncul bertahap
    await WAIT(fast ? 50 : 500);
    el.querySelectorAll('[data-count]').forEach((n) => (fast ? (n.textContent = n.dataset.count) : countUp(n, Number(n.dataset.count))));
    await WAIT(fast ? 50 : 900);
    if (state.phase === 'done') runRankFx(res);
  }

  async function close() {
    if (!el || el.hidden) return;
    if (state.phase === 'match') {
      if (!FocusGuard.confirm('Keluar di tengah duel = KALAH. Yakin mau keluar?')) return;
      try { await api(`${state.id}/menyerah/`); } catch (_) { /* duel lama otomatis dianggap menyerah saat mulai duel baru */ }
    }
    state.phase = 'closed';
    showBoard(false);
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
