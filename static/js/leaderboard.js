/**
 * Calculus Bridge — Papan peringkat (Level & Rank Duel), lencana rank, dan isian asal kampus.
 *
 *  - RankBadge   : lencana tier + nama rank + bintang (dipakai papan peringkat, Profil & duel.js).
 *  - Leaderboard : tab Level (urut total XP) dan Rank Duel (urut posisi tangga), cakupan
 *                  Global · Kampusku · Fakultasku (+ Top 100 Apex di tab Rank) dari
 *                  GET /api/peringkat/?board=…&scope=…; 50 teratas + posisimu sendiri.
 *                  Kampusku tanpa kampus (atau "Umum") → formulir isi kampus di tempat.
 *  - CampusEditor: baris "Asal kampus" di Profil + formulir ubah (POST /api/profile/campus/).
 *  Memakai postJSON dari app.js.
 */
const RankBadge = (() => {
  'use strict';

  const ICON = { terra: '🌍', luna: '🌙', solar: '☀️', nova: '🌟', apex: '👑' };

  /** Bintang: sub-rank biasa = ★ terisi / ☆ kosong sampai batas; Apex = ★ + angka (tanpa batas). */
  function stars(rank) {
    if (rank.max_stars == null) return `<span class="rb-stars apex">★ ${rank.stars}</span>`;
    return `<span class="rb-stars" aria-label="${rank.stars} dari ${rank.max_stars} bintang">${
      '★'.repeat(rank.stars)}<i>${'☆'.repeat(rank.max_stars - rank.stars)}</i></span>`;
  }

  function html(rank, big = false) {
    return `<span class="rank-badge tier-${rank.tier}${big ? ' big' : ''}">
      <span class="rb-icon" aria-hidden="true">${ICON[rank.tier]}</span>
      <span class="rb-text"><b>${rank.label}</b>${stars(rank)}</span></span>`;
  }

  return { html };
})();


const Leaderboard = (() => {
  'use strict';

  let board = 'level';
  let scope = 'global';
  const root = () => document.getElementById('lb-root');
  const esc = (t) => String(t ?? '').replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
  const COLORS = ['#2563EB', '#16A34A', '#D97706', '#DB2777', '#7C3AED', '#0D9488', '#DC2626', '#4B5563'];
  const colorOf = (name) => COLORS[[...name].reduce((h, c) => (h * 31 + c.charCodeAt(0)) >>> 0, 7) % COLORS.length];
  const fmt = (n) => n.toLocaleString('id-ID');

  function rowHTML(r) {
    const medal = { 1: '🥇', 2: '🥈', 3: '🥉' }[r.pos];
    const sub = [r.faculty, r.campus && r.campus !== 'Umum' ? r.campus : ''].filter(Boolean).join(' · ');
    const score = r.rank
      ? `<span class="lb-rank">${RankBadge.html(r.rank)}</span><span class="lb-wl" title="Menang–Kalah">${r.wins}–${r.losses}</span>`
      : `<span class="lb-level">Lv ${r.level}</span><span class="lb-xp">${fmt(r.xp)} XP</span>`;
    return `
      <li class="lb-row${r.rank ? ' is-rank' : ''}${r.me ? ' me' : ''}">
        <span class="lb-pos">${medal || r.pos}</span>
        <span class="lb-avatar${r.frame ? ` frame ${esc(r.frame)}` : ''}" style="background:${colorOf(r.username)}">${esc(r.name[0] || '?').toUpperCase()}</span>
        <span class="lb-who"><b>${esc(r.name)}${r.me ? ' <em>(kamu)</em>' : ''}</b>${r.title ? `<span class="lb-title">${esc(r.title)}</span>` : ''}<small>${esc(sub) || '&nbsp;'}</small></span>
        ${score}
      </li>`;
  }

  function render(data) {
    const inTop = data.rows.some((r) => r.me);
    const empty = data.scope === 'apex' ? 'Belum ada pemain yang mencapai Apex. Jadilah yang pertama!' : 'Belum ada pemain.';
    root().innerHTML = `
      <p class="lb-caption">${esc(data.label)} · ${fmt(data.total)} pemain</p>
      ${data.rows.length ? `<ol class="lb-list">${data.rows.map(rowHTML).join('')}</ol>` : `<p class="loading-text">${empty}</p>`}
      ${inTop || data.scope === 'apex' ? '' : `<p class="lb-caption">Posisimu</p><ol class="lb-list">${rowHTML(data.me)}</ol>`}`;
  }

  async function load(nextScope) {
    scope = nextScope || scope;
    if (scope === 'apex' && board !== 'rank') scope = 'global';
    document.querySelectorAll('.lb-scope').forEach((b) => {
      b.classList.toggle('active', b.dataset.scope === scope);
      if (b.dataset.scope === 'apex') b.hidden = board !== 'rank';
    });
    root().innerHTML = '<p class="loading-text">Memuat peringkat…</p>';
    try {
      const res = await fetch(`/api/peringkat/?board=${board}&scope=${scope}`, { headers: { Accept: 'application/json' } });
      const data = await res.json();
      if (!res.ok) throw new Error(data.message || `HTTP ${res.status}`);
      if (data.status === 'need_campus') {
        root().innerHTML = `<div class="lb-need">
          <p>${data.campus === 'Umum'
            ? 'Akunmu tercatat <b>Umum</b>, jadi tidak ikut peringkat per kampus. Isi kampusmu bila kamu mahasiswa.'
            : 'Isi asal kampusmu untuk melihat peringkat sesama mahasiswa di kampusmu.'}</p>
          ${CampusEditor.formHTML('')}</div>`;
        CampusEditor.bind(root(), () => load('kampus'));
        return;
      }
      render(data);
    } catch (err) {
      root().innerHTML = `<p class="loading-text">Gagal memuat peringkat: ${esc(err.message)}</p>`;
    }
  }

  function showBoard(next) {
    board = next;
    document.querySelectorAll('.lb-tab').forEach((t) => {
      t.classList.toggle('active', t.dataset.board === board);
      t.setAttribute('aria-selected', String(t.dataset.board === board));
    });
    document.querySelectorAll('.lb-panel').forEach((p) => { p.hidden = p.dataset.panel !== board; });
    load();
  }

  /** Kartu rank di Profil: dari data server (json_script "server-profile") atau hasil duel terbaru. */
  function renderProfileRank(latest) {
    const box = document.getElementById('profile-rank');
    const raw = document.getElementById('server-profile');
    if (!box || !raw) return;
    const rank = latest || JSON.parse(raw.textContent || 'null')?.rank;
    if (!rank) return;
    const next = rank.max_stars == null
      ? (rank.apex_title === 'Kosmos' ? 'Gelar tertinggi Apex tercapai!' : `Gelar berikutnya di ${rank.stars < 25 ? 25 : rank.stars < 50 ? 50 : 100}★`)
      : `${rank.max_stars - rank.stars + 1} kemenangan lagi untuk naik`;   // bintang penuh + 1 menang = naik
    box.innerHTML = `${RankBadge.html(rank, true)}
      <div class="profile-rank-meta"><span>${rank.wins} menang · ${rank.losses} kalah</span><small>${next}</small></div>`;
  }

  /** Dipanggil Duel setelah duel selesai: perbarui kartu Profil & papan Rank yang sedang tampil. */
  function setMyRank(rank) {
    renderProfileRank(rank);
    if (board === 'rank' && root()) load();
  }

  function init() {
    renderProfileRank();
    if (!root()) return;
    document.querySelectorAll('.lb-scope').forEach((b) => b.addEventListener('click', () => load(b.dataset.scope)));
    document.querySelectorAll('.lb-tab').forEach((t) => t.addEventListener('click', () => showBoard(t.dataset.board)));
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();

  return { load, setMyRank };
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
        <label class="campus-umum"><input type="checkbox" name="umum" ${umum ? 'checked' : ''}> Umum — bukan mahasiswa / tidak disebutkan</label>
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
