/**
 * Calculus Bridge — Ganti foto profil (tombol "Ganti foto" di Profil).
 *
 * Mechanism:
 *   - Tiga pilihan: Polos (inisial berwarna), Template bawaan (server-profile.avatar_presets),
 *     atau foto dari galeri HP / komputer (<input type="file" accept="image/*">).
 *   - Foto dipotong persegi di browser: gambar digambar ke <canvas> 256×256 dengan zoom (slider)
 *     dan geser (seret), lalu dikirim sebagai WebP/JPEG kecil (< 300 KB) ke POST /api/profile/avatar/.
 *     Server tetap memeriksa ukuran & jenis berkas (gamification/avatar.py).
 *   - Setelah tersimpan, semua avatar milik pengguna di halaman diperbarui lewat Avatar.paint()
 *     (sidebar & Profil), bingkai toko dipasang ulang, dan Leaderboard dimuat ulang.
 *
 * Bergantung pada: Avatar & Icon (icons.js), csrfToken/SFX/Mascot (app.js), Shop, Leaderboard.
 */
const AvatarPicker = (() => {
  'use strict';

  const SIZE = 256;
  const MAX_BYTES = 300 * 1024;
  const profile = (() => {
    try { return JSON.parse(document.getElementById('server-profile')?.textContent || 'null') || {}; }
    catch (_) { return {}; }
  })();
  let current = profile.avatar || { kind: 'initial' };
  let choice = null;          // { kind, preset? } atau { kind: 'upload' } saat foto sedang dipotong
  let img = null;             // Image yang sedang dipotong
  let crop = { zoom: 1, x: 0, y: 0 };
  let el = null;

  const name = () => profile.display_name || profile.username || '?';
  const $ = (sel) => el.querySelector(sel);

  /* ── dialog ─────────────────────────────────────────────────────── */
  function mount() {
    el = document.createElement('div');
    el.className = 'levelup-overlay avp-overlay';
    el.innerHTML = `
      <div class="avp-card" role="dialog" aria-modal="true" aria-labelledby="avp-title">
        <header class="avp-head">
          <h3 id="avp-title">Ganti foto profil</h3>
          <button type="button" class="btn-close" data-avp="close" aria-label="Tutup">×</button>
        </header>
        <div class="avp-preview">
          <div class="avp-stage" id="avp-stage"></div>
          <div class="avp-zoom" hidden>
            <label>Zoom <input type="range" min="1" max="3" step="0.01" value="1" data-avp="zoom"></label>
            <small>Seret foto buat ngatur posisinya.</small>
          </div>
        </div>
        <section class="avp-section">
          <h4>Pilih gaya</h4>
          <div class="avp-grid">
            <button type="button" class="avp-opt" data-avp="initial" title="Polos">${Avatar.html({ kind: 'initial' }, name(), profile.username, 'avp-thumb')}<span>Polos</span></button>
            ${(profile.avatar_presets || []).map((p) => `
              <button type="button" class="avp-opt" data-avp="preset" data-key="${p.key}" title="Template">
                ${Avatar.html({ kind: 'preset', ...p }, name(), profile.username, 'avp-thumb')}</button>`).join('')}
          </div>
        </section>
        <section class="avp-section">
          <h4>Dari galeri atau komputer</h4>
          <label class="btn btn-outline avp-upload">${Icon('doc')} Pilih foto
            <input type="file" accept="image/*" data-avp="file" hidden></label>
          <small class="avp-help">JPG, PNG, atau WebP. Nanti dipotong jadi persegi.</small>
        </section>
        <p class="avp-msg" role="status"></p>
        <footer class="avp-foot">
          <button type="button" class="btn btn-outline" data-avp="close">Batal</button>
          <button type="button" class="btn btn-primary" data-avp="save" disabled>Simpan</button>
        </footer>
      </div>`;
    document.body.appendChild(el);
    el.addEventListener('click', onClick);
    el.addEventListener('input', (e) => { if (e.target.dataset.avp === 'zoom') { crop.zoom = Number(e.target.value); clampCrop(); draw(); } });
    el.addEventListener('change', (e) => { if (e.target.dataset.avp === 'file') loadFile(e.target.files[0]); });
    el.addEventListener('keydown', (e) => { if (e.key === 'Escape') close(); });
    bindDrag();
  }

  function open() {
    if (!el) mount();
    choice = null;
    img = null;
    message('');
    showPreview(current);
    el.hidden = false;
    $('[data-avp=close]').focus();
  }

  function close() {
    if (el) el.hidden = true;
  }

  function message(text, err) {
    const m = $('.avp-msg');
    m.textContent = text;
    m.classList.toggle('err', !!err);
  }

  function showPreview(av) {
    $('.avp-zoom').hidden = true;
    $('#avp-stage').innerHTML = Avatar.html(av, name(), profile.username, 'avp-big');
    el.querySelectorAll('.avp-opt').forEach((b) => b.classList.toggle('on',
      (av.kind === 'initial' && b.dataset.avp === 'initial') || (av.kind === 'preset' && b.dataset.key === av.key)));
    $('[data-avp=save]').disabled = !choice;
  }

  /* ── potong foto ────────────────────────────────────────────────── */
  function loadFile(file) {
    if (!file) return;
    if (!file.type.startsWith('image/')) { message('Berkasnya bukan gambar.', true); return; }
    const reader = new FileReader();
    reader.onload = () => {
      const image = new Image();
      image.onload = () => {
        img = image;
        crop = { zoom: 1, x: 0, y: 0 };
        choice = { kind: 'upload' };
        $('#avp-stage').innerHTML = `<canvas class="avp-big avp-canvas" width="${SIZE}" height="${SIZE}"></canvas>`;
        $('.avp-zoom').hidden = false;
        $('[data-avp=zoom]').value = 1;
        el.querySelectorAll('.avp-opt').forEach((b) => b.classList.remove('on'));
        $('[data-avp=save]').disabled = false;
        message('');
        draw();
      };
      image.onerror = () => message('Fotonya gak bisa dibaca. Coba foto lain, ya.', true);
      image.src = reader.result;
    };
    reader.readAsDataURL(file);
  }

  /** Sisi persegi sumber (piksel gambar) yang tampil, dan batas geser agar tidak keluar gambar. */
  function clampCrop() {
    const side = Math.min(img.width, img.height) / crop.zoom;
    const maxX = (img.width - side) / 2, maxY = (img.height - side) / 2;
    crop.x = Math.max(-maxX, Math.min(maxX, crop.x));
    crop.y = Math.max(-maxY, Math.min(maxY, crop.y));
    return side;
  }

  function draw(target) {
    const canvas = target || $('.avp-canvas');
    if (!canvas || !img) return;
    const side = clampCrop();
    const sx = (img.width - side) / 2 + crop.x, sy = (img.height - side) / 2 + crop.y;
    const ctx = canvas.getContext('2d');
    ctx.clearRect(0, 0, SIZE, SIZE);
    ctx.drawImage(img, sx, sy, side, side, 0, 0, SIZE, SIZE);
  }

  function bindDrag() {
    let start = null;
    el.addEventListener('pointerdown', (e) => {
      if (!e.target.classList.contains('avp-canvas')) return;
      start = { x: e.clientX, y: e.clientY, cx: crop.x, cy: crop.y, w: e.target.clientWidth };
      e.target.setPointerCapture(e.pointerId);
    });
    el.addEventListener('pointermove', (e) => {
      if (!start || !img) return;
      const scale = (Math.min(img.width, img.height) / crop.zoom) / start.w;   // piksel gambar per piksel layar
      crop.x = start.cx - (e.clientX - start.x) * scale;
      crop.y = start.cy - (e.clientY - start.y) * scale;
      draw();
    });
    el.addEventListener('pointerup', () => { start = null; });
  }

  /** Canvas → Blob kecil (WebP bila didukung, selain itu JPEG), turunkan kualitas sampai < MAX_BYTES. */
  async function exportBlob() {
    const canvas = document.createElement('canvas');
    canvas.width = canvas.height = SIZE;
    draw(canvas);
    for (const q of [0.9, 0.8, 0.65, 0.5]) {
      let blob = await new Promise((r) => canvas.toBlob(r, 'image/webp', q));
      if (!blob || blob.type !== 'image/webp') blob = await new Promise((r) => canvas.toBlob(r, 'image/jpeg', q));
      if (blob && blob.size <= MAX_BYTES) return blob;
    }
    throw new Error('Fotonya masih kegedean. Coba foto lain, ya.');
  }

  /* ── simpan ─────────────────────────────────────────────────────── */
  async function save() {
    if (!choice) return;
    const btn = $('[data-avp=save]');
    btn.disabled = true;
    message('Lagi nyimpen…');
    try {
      let res;
      if (choice.kind === 'upload') {
        const form = new FormData();
        form.append('kind', 'upload');
        const blob = await exportBlob();
        form.append('file', blob, blob.type === 'image/webp' ? 'avatar.webp' : 'avatar.jpg');
        res = await fetch('/api/profile/avatar/', { method: 'POST', headers: { 'X-CSRFToken': csrfToken() }, body: form });
      } else {
        res = await fetch('/api/profile/avatar/', {
          method: 'POST', headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrfToken() }, body: JSON.stringify(choice),
        });
      }
      const data = await res.json().catch(() => ({}));
      if (!res.ok) throw new Error(data.message || `HTTP ${res.status}`);
      apply(data.avatar);
      SFX.correct();
      close();
      Mascot.setMood('celebrate', 'Foto profil baru, makin keren!');
    } catch (err) {
      message(err.message, true);
      btn.disabled = false;
    }
  }

  /** Pasang foto baru di semua tempat yang sedang tampil. */
  function apply(av) {
    current = av;
    profile.avatar = av;
    ['sidebar-avatar', 'profile-avatar-lg'].forEach((id) => Avatar.paint(document.getElementById(id), av, name(), profile.username));
    if (typeof Shop !== 'undefined') Shop.dressAll();
    if (typeof Leaderboard !== 'undefined' && document.getElementById('page-rank')?.classList.contains('active')) Leaderboard.load();
  }

  function onClick(e) {
    if (e.target === el) return close();
    const b = e.target.closest('[data-avp]');
    if (!b) return;
    const act = b.dataset.avp;
    if (act === 'close') close();
    else if (act === 'save') save();
    else if (act === 'initial') { choice = { kind: 'initial' }; img = null; showPreview({ kind: 'initial' }); }
    else if (act === 'preset') {
      const p = (profile.avatar_presets || []).find((x) => x.key === b.dataset.key);
      choice = { kind: 'preset', preset: p.key };
      img = null;
      showPreview({ kind: 'preset', ...p });
    }
  }

  function init() {
    document.querySelectorAll('[data-avatar-edit]').forEach((b) => b.addEventListener('click', open));
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();

  return { open };
})();
