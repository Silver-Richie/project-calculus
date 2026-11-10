/**
 * Calculus Bridge — Mode gelap / terang untuk beranda.
 *
 * Dimuat di <head> (bukan di akhir body) agar tema terpasang sebelum halaman
 * digambar, sehingga tidak ada kilatan putih saat membuka beranda dalam mode gelap.
 *  - Pilihan pengguna disimpan di localStorage ('cb-theme').
 *  - Belum pernah memilih → mengikuti setelan sistem (prefers-color-scheme).
 *  - Tombol #theme-toggle-btn di HUD menukar tema.
 */
(() => {
  'use strict';

  const KEY = 'cb-theme';
  const root = document.documentElement;

  function saved() {
    try { return localStorage.getItem(KEY); } catch (e) { return null; }
  }

  function apply(theme) {
    root.dataset.theme = theme;
    const btn = document.getElementById('theme-toggle-btn');
    if (!btn) return;
    const dark = theme === 'dark';
    btn.textContent = dark ? '☀️' : '🌙';
    btn.title = dark ? 'Ganti ke mode terang' : 'Ganti ke mode gelap';
    btn.setAttribute('aria-label', btn.title);
    btn.setAttribute('aria-pressed', String(dark));
  }

  apply(saved() || (matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'));

  document.addEventListener('DOMContentLoaded', () => {
    const btn = document.getElementById('theme-toggle-btn');
    if (!btn) return;
    apply(root.dataset.theme);
    btn.addEventListener('click', () => {
      const next = root.dataset.theme === 'dark' ? 'light' : 'dark';
      apply(next);
      try { localStorage.setItem(KEY, next); } catch (e) { /* mode privat: cukup untuk sesi ini */ }
    });
  });
})();
