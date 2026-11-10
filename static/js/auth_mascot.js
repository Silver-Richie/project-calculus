/**
 * Calculus Bridge — Reaksi maskot terhadap form Masuk/Daftar.
 *
 * Mekanisme:
 *  - Fokus/ketik di kolom teks        → pupil maskot kartu melirik ke kolom itu
 *                                       (makin panjang teks, makin ke kanan liriknya).
 *  - Fokus di kolom kata sandi        → kedua tangan maskot naik menutupi kacamata.
 *  - Klik tombol kirim (Masuk/Daftar) → maskot melompat gembira.
 *  Tiap reaksi juga disiarkan sebagai event window ('archie:look', 'archie:cover',
 *  'archie:type', 'archie:cheer') agar adegan latar (archie_family.js) ikut bereaksi tanpa kedua
 *  berkas saling bergantung. Pengiriman form sendiri tidak diubah.
 */
(() => {
  'use strict';

  const FIELDS = '.auth-card .auth-field input';
  const SUBMITS = '.auth-card .auth-pane .auth-submit[type="submit"]';

  const emit = (name, detail = null) => window.dispatchEvent(new CustomEvent(`archie:${name}`, { detail }));
  const focusedField = () => (document.activeElement && document.activeElement.matches(FIELDS) ? document.activeElement : null);

  function init() {
    const mascot = document.getElementById('mascot-card');
    if (!mascot) return;
    const pupils = mascot.querySelector('.mc-pupils');

    function lookAtField(input) {
      const progress = Math.min(input.value.length / 24, 1);   // 0 = awal kolom, 1 = ujung kanan
      pupils.style.transform = `translate(${(-4 + 9 * progress).toFixed(1)}px, 4px)`;
      const r = input.getBoundingClientRect();
      emit('look', { x: r.left + 40 + progress * (r.width - 60), y: r.top + r.height / 2 });
    }

    function onFocus(input) {
      const secret = input.type === 'password';
      mascot.classList.toggle('is-cover', secret);
      emit('cover', { on: secret });
      if (secret) pupils.style.transform = '';
      else lookAtField(input);
    }

    function onBlur() {
      // Jika fokus pindah ke kolom lain, onFocus kolom itu yang menangani.
      setTimeout(() => {
        if (focusedField()) return;
        mascot.classList.remove('is-cover');
        pupils.style.transform = '';
        emit('cover', { on: false });
        emit('look');
      }, 0);
    }

    document.querySelectorAll(FIELDS).forEach((input) => {
      input.addEventListener('focus', () => onFocus(input));
      input.addEventListener('blur', onBlur);
      input.addEventListener('input', () => {
        if (input.type !== 'password') lookAtField(input);
        emit('type');   // adegan: Hijau menulis rumus, Kuning melompat memberi semangat
      });
    });

    document.querySelectorAll(SUBMITS).forEach((btn) => {
      btn.addEventListener('click', () => {
        mascot.classList.remove('is-cover', 'is-cheer');
        void mascot.getBoundingClientRect();   // mulai ulang animasi lompat
        mascot.classList.add('is-cheer');
        emit('cover', { on: false });
        emit('cheer');
      });
    });
    mascot.addEventListener('animationend', () => mascot.classList.remove('is-cheer'));

    // Kolom ber-autofocus sudah fokus sebelum skrip ini berjalan.
    if (focusedField()) onFocus(focusedField());
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
})();
