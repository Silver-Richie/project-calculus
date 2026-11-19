/**
 * Calculus Bridge — Papan peringkat (Level & Rank Duel), lencana rank, dan isian asal kampus.
 *
 *  - RankBadge   : lencana tier (lambang RankEmblem, rank_emblem.js) + nama rank + bintang
 *                  (dipakai Profil, Ranked & duel.js).
 *  - Leaderboard : papan Level (urut total XP), Rank Duel (urut posisi tangga), dan Menang Duel
 *                  (urut jumlah kemenangan), gaya aplikasi (static/css/leaderboard.css): kartu Posisimu,
 *                  podium 3 teratas, daftar #4 dst → "Tampilkan N" → pemain di sekitarmu, dan state seri
 *                  bila belum ada duel; Rank Duel juga kolom sebaran tier. Cakupan
 *                  Global · Kampusku · Fakultasku (+ Top 100 Apex di tab Rank) dari
 *                  GET /api/peringkat/?board=…&scope=…; 50 teratas + posisimu sendiri.
 *                  Kampusku tanpa kampus (atau "Umum") → formulir isi kampus di tempat.
 *  - CampusEditor: baris "Asal kampus" di Profil + formulir ubah (POST /api/profile/campus/).
 *  Memakai postJSON dari app.js.
 */
const RankBadge = (() => {
  'use strict';

  /** Bintang: sub-rank biasa = ★ terisi / ☆ kosong sampai batas; Apex = ★ + angka (tanpa batas). */
  function stars(rank) {
    if (rank.max_stars == null) return `<span class="rb-stars apex">★ ${rank.stars}</span>`;
    return `<span class="rb-stars" aria-label="${rank.stars} dari ${rank.max_stars} bintang">${
      '★'.repeat(rank.stars)}<i>${'☆'.repeat(rank.max_stars - rank.stars)}</i></span>`;
  }

  function html(rank, big = false) {
    return `<span class="rank-badge tier-${rank.tier}${big ? ' big' : ''}">
      <span class="rb-icon" aria-hidden="true">${RankEmblem.svg(rank.tier, { size: big ? 40 : 22 })}</span>
      <span class="rb-text"><b>${rank.label}</b>${stars(rank)}</span></span>`;
  }

  /** Teks progres: berapa kemenangan lagi untuk naik / gelar Apex berikutnya. */
  function next(rank) {
    if (rank.max_stars == null) {
      return rank.apex_title === 'Kosmos' ? 'Gelar tertinggi Apex udah kamu raih!'
        : `Gelar berikutnya di ${rank.stars < 25 ? 25 : rank.stars < 50 ? 50 : 100}★`;
    }
    return `Butuh ${rank.max_stars - rank.stars + 1} kemenangan lagi buat naik tier`;   // bintang penuh + 1 menang = naik
  }

  return { html, next };
})();


const Leaderboard = (() => {
  'use strict';

  let board = 'level';
  let scope = 'global';
  let data = null;
  let expanded = false;          // baris "Tampilkan N pemain" sudah dibuka
  const root = () => document.getElementById('lb-root');
  const $ = (id) => document.getElementById(id);
  const esc = (t) => String(t ?? '').replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
  const fmt = (n) => Number(n || 0).toLocaleString('id-ID');
  const RESULT = { w: 'menang', l: 'kalah', d: 'imbang' };
  const MIN_DUEL_LEVEL = 3;      // = duel.MIN_LEVEL
  const PODIUM = 3;              // posisi 1–3 tampil sebagai kartu podium
  const TOP = 5;                 // baris teratas yang selalu tampil sebelum "Tampilkan N"
  const BOARDS = {
    level: { sub: 'XP dari sesi latihan tiap topik. Makin banyak sesi yang beres, makin tinggi levelmu.',
             cols: ['#', 'Pemain', 'Level', 'XP'] },
    rank: { sub: 'Makin sering menang, makin tinggi tier-mu. Mulai dari Terra sampai Apex di puncak.',
            cols: ['#', 'Pemain', '5 terakhir', 'Rekor', 'Poin'] },
    wins: { sub: 'Total kemenangan duel, apa pun rank-mu. Semua kemenangan dihitung.',
            cols: ['#', 'Pemain', '5 terakhir', 'Rekor', 'Menang'] },
  };

  /* ── potongan tampilan ──────────────────────────────────────────── */
  const where = (r) => [r.faculty, r.campus && r.campus !== 'Umum' ? r.campus : ''].filter(Boolean).join(' · ');
  const avatar = (r, cls = '') => Avatar.html(r.avatar, r.name, r.username, `lbx-av ${cls}${r.frame ? ` frame ${esc(r.frame)}` : ''}`);
  const chip = (r) => (board === 'level'
    ? `<span class="lbx-pill">Lv ${r.level}</span>`
    : `<span class="lbx-pill t-${r.tier}">${esc(r.rank.label)}</span>`);
  const score = (r) => (board === 'level' ? `${Icon('bolt')} ${fmt(r.xp)}`
    : board === 'rank' ? `${fmt(r.points)}` : `${Icon('trophy')} ${fmt(r.wins)}`);
  const player = (r) => `<span class="lbx-player">${avatar(r)}<span class="lbx-who">
    <b>${esc(r.name)}${r.me ? ' <em>(kamu)</em>' : ''}</b><small>${esc([where(r), r.title].filter(Boolean).join(' · ')) || '&nbsp;'}</small></span></span>`;

  function dots(recent) {
    if (!recent?.length) return '<span class="lbx-none">Belum duel</span>';
    const all = [...Array(5 - recent.length).fill('e'), ...recent];
    return `<span class="lbx-dots" aria-label="${recent.length} duel terakhir: ${recent.map((k) => RESULT[k]).join(', ')}">${
      all.map((k) => `<i class="${k}"></i>`).join('')}</span>`;
  }

  function rowHTML(r) {
    const cells = board === 'level'
      ? `${chip(r)}<span class="lbx-score">${score(r)}</span>`
      : `${dots(r.recent)}<span class="lbx-rec">${r.wins}–${r.losses}</span><span class="lbx-score">${score(r)}</span>`;
    return `<li class="lbx-row${board === 'level' ? ' is-level' : ''}${r.me ? ' me' : ''}"><span class="lbx-pos">${fmt(r.pos)}</span>${player(r)}${cells}</li>`;
  }

  const groupHTML = (label) => `<li class="lbx-group">${label}</li>`;
  const gapHTML = (text, button) =>
    `<li class="lbx-gap"><span>${text}</span>${button ? '<button type="button" data-lbx="more">Tampilkan</button>' : ''}</li>`;

  /* ── podium 1–3 ─────────────────────────────────────────────────── */
  function podiumHTML(rows) {
    const top = rows.slice(0, PODIUM);
    const ICON = ['crown', 'medal-silver', 'medal-bronze'];
    const order = [1, 0, 2].filter((i) => top[i]);          // #2 kiri · #1 tengah · #3 kanan
    return `<div class="lbx-podium">${order.map((i) => {
      const r = top[i];
      return `<article class="lbx-pod p${i + 1}${r.me ? ' me' : ''}">
        <span class="lbx-pod-pos">#${fmt(r.pos)}</span>
        <span class="lbx-pod-icon">${Icon(ICON[i], { label: `Peringkat ${r.pos}` })}</span>
        ${avatar(r)}
        <b>${esc(r.name)}${r.me ? ' (kamu)' : ''}</b>
        <small>${esc(where(r)) || '&nbsp;'}</small>
        ${chip(r)}
        <span class="lbx-pod-score">${score(r)}${board === 'rank' ? ' poin' : board === 'level' ? ' XP' : ''}</span>
      </article>`;
    }).join('')}</div>`;
  }

  /* ── daftar #4 dst: sampai posisi 5 → Tampilkan N → di sekitarmu ── */
  function listHTML(d) {
    const { rows } = d;
    const around = d.around || [];
    const head = `<li class="lbx-thead${board === 'level' ? ' is-level' : ''}">${BOARDS[board].cols.map((c) => `<span>${c}</span>`).join('')}</li>`;
    const first = around[0]?.index;
    let body;
    if (!around.length || first <= TOP) {
      // posisiku dekat puncak (atau di luar cakupan): satu daftar menerus
      const end = around.length ? Math.max(TOP, around[around.length - 1].index + 1) : TOP;
      const shown = (expanded ? rows : rows.slice(0, end)).slice(PODIUM);
      body = shown.map(rowHTML).join('')
        + (!expanded && rows.length > end ? gapHTML(`${fmt(rows.length - end)} pemain berikutnya`, true) : '');
    } else {
      const between = rows.slice(TOP, Math.min(rows.length, first));
      const rest = first - TOP - between.length;
      body = rows.slice(PODIUM, TOP).map(rowHTML).join('')
        + (expanded
          ? between.map(rowHTML).join('') + (rest > 0 ? gapHTML(`${fmt(rest)} pemain lagi di antaranya`, false) : '')
          : gapHTML(`${fmt(first - TOP)} pemain di antaranya`, true))
        + groupHTML('Di sekitarmu') + around.map(rowHTML).join('');
    }
    return body ? `<div class="lbx-card"><ol class="lbx-list">${head}${body}</ol></div>` : '';
  }

  /* ── kartu Posisimu ─────────────────────────────────────────────── */
  function duelButton(text) {
    // Server tanpa WebSocket (DUEL_ENABLED=False) menandai halaman Ranked dengan data-duel-off.
    if (document.querySelector('[data-duel-off]')) return `<button type="button" class="lbx-btn" disabled>${Icon('clock')} Duel segera hadir</button>`;
    const lv = (typeof State !== 'undefined' && State.get().level?.level) || 1;
    return lv >= MIN_DUEL_LEVEL
      ? `<button type="button" class="lbx-btn" data-lbx="duel">${Icon('swords')} ${text}</button>`
      : `<button type="button" class="lbx-btn" disabled>${Icon('lock')} Kebuka di Level ${MIN_DUEL_LEVEL}</button>`;
  }

  /** Teks & persen progres menuju sub-rank (atau gelar Apex) berikutnya. */
  function rankProgress(r) {
    if (r.max_stars == null) {
      if (!r.next_label) return ['Gelar tertinggi Apex udah kamu raih', 100];
      const goal = r.stars < 25 ? 25 : r.stars < 50 ? 50 : 100;
      return [`Butuh ${goal - r.stars} bintang lagi ke ${r.next_label}`, (r.stars / goal) * 100];
    }
    return [`Butuh ${r.max_stars - r.stars + 1} kemenangan lagi ke ${r.next_label}`, (r.stars / (r.max_stars + 1)) * 100];
  }

  function meCardHTML(d) {
    const m = d.me;
    if (board !== 'level' && !d.played) {
      return `<section class="lbx-me lbx-tie"><div>
        <h3>Semua ${fmt(d.total)} pemain masih seri</h3>
        <p>${board === 'rank'
          ? 'Belum ada duel yang dimainkan, jadi semua orang masih di Terra III dengan rekor 0–0. Menang sekali aja, kamu langsung jadi yang pertama naik.'
          : 'Belum ada duel yang dimainkan, jadi semua pemain masih 0 kemenangan. Menang sekali aja, kamu langsung di puncak.'}</p>
        ${duelButton('Cari lawan duel')}</div></section>`;
    }
    let note, pct = null;
    if (board === 'level') {
      const li = m.level_info;
      note = `${fmt(li.need - li.into)} XP lagi ke Level ${li.level + 1}`;
      pct = li.percent;
    } else if (board === 'rank') {
      [note, pct] = rankProgress(m.rank);
    } else {
      note = `${fmt(m.wins)} menang · ${fmt(m.losses)} kalah`;
    }
    const inScope = m.index != null;
    return `<section class="lbx-me">
      <div class="lbx-me-rank"><span><small>Posisimu</small><br><b>${inScope ? `#${fmt(m.pos)}` : '–'}</b></span></div>
      ${avatar(m, 'lg')}
      <div class="lbx-me-info">
        <p><b>${esc(m.name)}</b>${where(m) ? `<span class="lbx-badge">${Icon('school')} ${esc(where(m))}</span>` : ''}</p>
        <p>${chip(m)}<small>${inScope ? note : `Kamu belum di Apex · ${note}`}</small></p>
        ${pct != null ? `<div class="lbx-bar" role="progressbar" aria-valuenow="${Math.round(pct)}" aria-valuemin="0" aria-valuemax="100"><i style="width:${Math.min(100, Math.max(3, pct)).toFixed(1)}%"></i></div>` : ''}
      </div>
      ${board === 'level' ? '' : duelButton('Mulai duel')}
    </section>`;
  }

  /* ── state seri: semua di posisi 1 ──────────────────────────────── */
  function tieListHTML(d) {
    const all = [...d.rows].sort((a, b) => b.me - a.me);
    if (!all.some((r) => r.me) && d.me) all.unshift(d.me);
    const more = d.total - all.length;
    return `<div class="lbx-card"><ol class="lbx-list">${groupHTML('Semua di posisi 1 · seri')}
      ${all.map((r) => `<li class="lbx-row lbx-row-tie${r.me ? ' me' : ''}">${player(r)}<span class="lbx-none">Belum duel</span></li>`).join('')}
      ${more > 0 ? `<li class="lbx-more-note">dan ${fmt(more)} pemain lainnya</li>` : ''}</ol></div>`;
  }

  /* ── kolom Ketinggian (Rank Duel) ───────────────────────────────── */
  function altitudeHTML(d) {
    const total = d.tiers.reduce((s, t) => s + t.count, 0);
    const per = Math.max(1, Math.ceil(total / 60));
    const m = d.me;
    const layers = [...d.tiers].reverse().map((t, li) => {
      const faded = !t.count || (!d.played && t.tier !== 'terra');
      let seed = (li + 1) * 7919;
      const rnd = () => { seed = (seed * 9301 + 49297) % 233280; return seed / 233280; };
      const dotsHTML = d.played && t.count
        ? Array.from({ length: Math.max(1, Math.round(t.count / per)) }, () =>
          `<i style="left:${(6 + rnd() * 88).toFixed(1)}%;top:${(38 + rnd() * 54).toFixed(1)}%"></i>`).join('') : '';
      let mark = '';
      if (d.played && m.index != null && m.tier === t.tier) {
        const r = m.rank;
        const frac = r.max_stars == null ? Math.min(1, r.stars / 100) : ((3 - r.division) * r.max_stars + r.stars) / (3 * r.max_stars);
        mark = `<span class="lbx-mark" style="top:${(90 - frac * 50).toFixed(1)}%"><em>kamu</em></span>`;
      }
      const start = !d.played && t.tier === 'terra'
        ? `<div class="lbx-start">${'<i></i>'.repeat(Math.min(7, Math.max(0, t.count - 1)))}<i class="me"></i><small>Semua di Terra III, garis start</small></div>` : '';
      return `<div class="lbx-layer t-${t.tier}${faded ? ' empty' : ''}" style="flex-grow:${t.count}">
        <b>${t.name}</b><span class="lbx-layer-n">${t.count ? fmt(t.count) : 'kosong'}</span>${dotsHTML}${mark}${start}</div>`;
    }).join('');
    return `<aside class="lbx-alt" aria-label="Sebaran pemain per tier">
      <p class="lbx-alt-head"><b>Sebaran tier</b><span>${fmt(total)} pemain</span></p>
      <div class="lbx-layers">${layers}</div>
      <p class="lbx-alt-foot"><span>Terra</span><span>Apex</span></p>
      <p class="lbx-alt-note">${d.played
        ? `Tiap titik mewakili ${per > 1 ? `sekitar ${fmt(per)} pemain` : '1 pemain'}. Tebal lapisan mengikuti jumlah pemainnya.`
        : 'Belum ada yang naik dari Terra, jadi tier di atasnya masih kosong.'}</p>
    </aside>`;
  }

  function render(d) {
    data = d;
    const tie = board !== 'level' && !d.played;
    let body;
    if (!d.rows.length) {
      body = `<p class="lbx-empty">${d.scope === 'apex' ? 'Belum ada yang sampai Apex. Jadi yang pertama, yuk!' : 'Belum ada pemain.'}</p>`;
    } else {
      body = tie ? tieListHTML(d) : podiumHTML(d.rows) + listHTML(d);
    }
    const main = `<div class="lbx-main">${meCardHTML(d)}${body}</div>`;
    root().innerHTML = board === 'rank' && d.scope !== 'apex' ? `<div class="lbx-grid">${main}${altitudeHTML(d)}</div>` : main;
  }

  function setHeading() {
    $('lbx-sub').textContent = BOARDS[board].sub;
  }

  async function load(nextScope) {
    scope = nextScope || scope;
    if (scope === 'apex' && board !== 'rank') scope = 'global';
    expanded = false;
    setHeading();
    document.querySelectorAll('.lb-scope').forEach((b) => {
      b.classList.toggle('active', b.dataset.scope === scope);
      if (b.dataset.scope === 'apex') b.hidden = board !== 'rank';
    });
    root().innerHTML = '<p class="lbx-loading">Lagi nyiapin leaderboard…</p>';
    try {
      const res = await fetch(`/api/peringkat/?board=${board}&scope=${scope}`, { headers: { Accept: 'application/json' } });
      const d = await res.json();
      if (!res.ok) throw new Error(d.message || `HTTP ${res.status}`);
      if (d.status === 'need_campus') {
        root().innerHTML = `<div class="lb-need">
          <p>${d.campus === 'Umum'
            ? 'Akunmu tercatat <b>Umum</b>, jadi gak ikut leaderboard per kampus. Isi kampusmu kalau kamu mahasiswa.'
            : 'Isi asal kampusmu dulu buat lihat leaderboard sesama mahasiswa kampusmu.'}</p>
          ${CampusEditor.formHTML('')}</div>`;
        CampusEditor.bind(root(), (campus) => {
          const tab = $('lbx-scope-kampus');
          if (tab && campus && campus !== 'Umum') tab.textContent = campus;
          load('kampus');
        });
        return;
      }
      render(d);
    } catch (err) {
      root().innerHTML = `<p class="lbx-loading">Leaderboard gagal dimuat: ${esc(err.message)}</p>`;
    }
  }

  function showBoard(next, reload = true) {
    board = next;
    document.querySelectorAll('.lb-tab').forEach((t) => {
      t.classList.toggle('active', t.dataset.board === board);
      t.setAttribute('aria-selected', String(t.dataset.board === board));
    });
    if (reload) load();
  }

  /** Kartu rank di Profil: dari data server (json_script "server-profile") atau hasil duel terbaru. */
  function renderProfileRank(latest) {
    const box = document.getElementById('profile-rank');
    const raw = document.getElementById('server-profile');
    if (!box || !raw) return;
    const rank = latest || JSON.parse(raw.textContent || 'null')?.rank;
    if (!rank) return;
    box.innerHTML = `${RankBadge.html(rank, true)}
      <div class="profile-rank-meta"><span>${rank.wins} menang · ${rank.losses} kalah</span><small>${RankBadge.next(rank)}</small></div>`;
  }

  /** Dipanggil Duel setelah duel selesai: perbarui kartu Profil & papan Rank yang sedang tampil. */
  function setMyRank(rank) {
    renderProfileRank(rank);
    if (board !== 'level' && root()) load();
  }

  function init() {
    renderProfileRank();
    if (!root()) return;
    setHeading();
    document.querySelectorAll('.lb-scope').forEach((b) => b.addEventListener('click', () => load(b.dataset.scope)));
    document.querySelectorAll('.lb-tab').forEach((t) => t.addEventListener('click', () => showBoard(t.dataset.board)));
    root().addEventListener('click', (e) => {
      const act = e.target.closest('[data-lbx]')?.dataset.lbx;
      if (act === 'more') { expanded = true; render(data); }
      else if (act === 'duel' && typeof Duel !== 'undefined') Duel.open();
    });
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();

  return { load, setMyRank, show: showBoard };
})();


const CampusEditor = (() => {
  'use strict';

  const esc = (t) => String(t ?? '').replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));

  /** Formulir kampus (memakai <datalist id="campus-list"> yang ada di halaman). */
  function formHTML(value) {
    const umum = value === 'Umum';
    return `
      <form class="campus-form">
        <input type="text" name="campus" list="campus-list" maxlength="120" aria-label="Nama kampus"
               placeholder="Ketik nama kampus, mis. Universitas Indonesia" value="${umum ? '' : esc(value)}" ${umum ? 'disabled' : ''}>
        <label class="campus-umum"><input type="checkbox" name="umum" ${umum ? 'checked' : ''}> Umum (bukan mahasiswa / gak mau sebut)</label>
        <div class="campus-actions"><button type="submit" class="btn btn-primary btn-sm">Simpan</button></div>
        <p class="campus-msg" role="alert"></p>
      </form>`;
  }

  function bind(box, done) {
    const form = box.querySelector('.campus-form');
    const input = form.elements.campus, umum = form.elements.umum;
    umum.addEventListener('change', () => { input.disabled = umum.checked; if (!umum.checked) input.focus(); });
    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      const msg = form.querySelector('.campus-msg');
      try {
        const r = await postJSON('/api/profile/campus/', { campus: input.value, umum: umum.checked });
        setLabel(r.campus);
        done(r.campus);
      } catch (err) {
        msg.textContent = err.message;
      }
    });
  }

  function setLabel(campus) {
    const el = document.getElementById('profile-campus');
    if (el) el.textContent = campus || 'Belum diisi';
  }

  /** Tombol "Ubah" di Profil membuka formulir di bawah baris kampus. */
  function init() {
    const btn = document.getElementById('profile-campus-edit');
    const slot = document.getElementById('profile-campus-form');
    if (!btn || !slot) return;
    btn.addEventListener('click', () => {
      if (slot.childElementCount) { slot.innerHTML = ''; return; }
      const current = document.getElementById('profile-campus').dataset.value || '';
      slot.innerHTML = formHTML(current);
      bind(slot, (campus) => {
        document.getElementById('profile-campus').dataset.value = campus;
        slot.innerHTML = '';
      });
      slot.querySelector('input[name=campus]:not([disabled])')?.focus();
    });
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();

  return { formHTML, bind };
})();
