/**
 * Calculus Bridge — Pengingat & streak (Tahap 1 notifikasi, tanpa push/OAuth).
 *
 * - Banner streak di atas Skill Tree (#streak-banner) dari server-profile.streak (gamification/streak.py):
 *     nunggu → "Streak N hari-mu nunggu — main hari ini biar gak putus!", aman → sudah main hari ini,
 *     baru → ajakan memulai streak. State.setStreak(...) memanggil Reminder.setStreak setelah sesi/duel.
 * - Kartu Pengingat Harian di Profil (#reminder-card): jam pilihan pengguna + zona waktu browser →
 *     /pengingat/google/ (Google Calendar, acara berulang harian) dan /pengingat.ics (Apple/Outlook).
 * - Tombol pasang aplikasi (PWA): beforeinstallprompt di Android/desktop, petunjuk Add to Home Screen di iPhone.
 * Bergantung pada Icon (icons.js) dan Nav (app.js).
 */
const Reminder = (() => {
  'use strict';

  const profile = (() => {
    try { return JSON.parse(document.getElementById('server-profile')?.textContent || 'null') || {}; }
    catch (_) { return {}; }
  })();
  let streak = profile.streak || null;
  let installEvent = null;

  const $ = (id) => document.getElementById(id);
  const store = {
    get(k) { try { return localStorage.getItem(k); } catch (_) { return null; } },
    set(k, v) { try { localStorage.setItem(k, v); } catch (_) { /* mode privat: abaikan */ } },
  };
  const wibDate = () => new Date().toLocaleDateString('sv-SE', { timeZone: 'Asia/Jakarta' });   // YYYY-MM-DD
  const DISMISS = 'cb_streak_banner';

  // ── Banner streak ─────────────────────────────────────────────────────────
  function bannerHTML(st) {
    const d = st.days;
    const content = {
      nunggu: [`Streak ${d} hari-mu nunggu`, 'Main hari ini biar gak putus! Satu sesi latihan atau satu Ranked Duel udah cukup.'],
      aman: [`Mantap, streak ${d} hari aman!`, `Kamu udah main hari ini. Balik lagi besok buat hari ke-${d + 1}.`],
      baru: ['Nyalain api streak-mu hari ini', 'Selesaikan satu sesi latihan dan mulai hitung hari berturut-turut.'],
    }[st.state];
    const cta = st.state === 'aman' ? ''
      : `<button type="button" class="btn btn-accent btn-sm" data-streak="play">${Icon('play')} Main sekarang</button>`;
    return `
      <span class="streak-banner-flame" aria-hidden="true">${Icon('flame')}${st.state !== 'baru' ? `<b>${d}</b>` : ''}</span>
      <div class="streak-banner-text"><strong>${content[0]}</strong><span>${content[1]}</span></div>
      <div class="streak-banner-actions">${cta}
        <button type="button" class="link-btn" data-streak="remind">${Icon('clock')} Pasang pengingat</button>
      </div>
      <button type="button" class="streak-banner-x" data-streak="hide" aria-label="Sembunyikan untuk hari ini">×</button>`;
  }

  function renderBanner() {
    const el = $('streak-banner');
    if (!el || !streak) return;
    const hiddenKey = `${wibDate()}:${streak.state}`;
    el.hidden = store.get(DISMISS) === hiddenKey;
    el.className = `streak-banner state-${streak.state}`;
    el.innerHTML = bannerHTML(streak);
  }

  function onBannerClick(e) {
    const act = e.target.closest('[data-streak]')?.dataset.streak;
    if (act === 'hide') {
      store.set(DISMISS, `${wibDate()}:${streak.state}`);
      $('streak-banner').hidden = true;
    } else if (act === 'play') {
      const target = document.querySelector('.topic-node.topic-active') || $('skill-tree');
      target?.scrollIntoView({ behavior: 'smooth', block: 'center' });
    } else if (act === 'remind') {
      if (typeof Nav !== 'undefined') Nav.go('user');
      setTimeout(() => $('reminder-card')?.scrollIntoView({ behavior: 'smooth', block: 'start' }), 120);
    }
  }

  // ── Pengingat kalender ────────────────────────────────────────────────────
  const ZONES = { '-420': 'WIB', '-480': 'WITA', '-540': 'WIT' };

  function updateLinks() {
    const input = $('reminder-time');
    if (!input) return;
    const jam = input.value || '19:00';
    const tz = new Date().getTimezoneOffset();
    const q = `jam=${encodeURIComponent(jam)}&tz=${tz}`;
    $('reminder-google').href = `/pengingat/google/?${q}`;
    $('reminder-ics').href = `/pengingat.ics?${q}`;
    const zone = ZONES[String(tz)] || Intl.DateTimeFormat().resolvedOptions().timeZone || '';
    $('reminder-zone').textContent = `setiap hari, ${jam} ${zone}`.trim();
    store.set('cb_reminder_time', jam);
  }

  // ── Pasang aplikasi (PWA) ─────────────────────────────────────────────────
  function renderInstall() {
    const box = $('reminder-install');
    if (!box) return;
    const standalone = window.matchMedia?.('(display-mode: standalone)').matches || navigator.standalone;
    const ios = /iphone|ipad|ipod/i.test(navigator.userAgent);
    if (standalone) {
      box.hidden = false;
      box.innerHTML = `${Icon('check')} Calculus Bridge udah terpasang di perangkat ini.`;
    } else if (installEvent) {
      box.hidden = false;
      box.innerHTML = `<button type="button" class="btn btn-outline btn-sm" data-install>${Icon('sparkle')} Pasang aplikasi di perangkat ini</button>
        <small>Biar bisa dibuka langsung dari layar utama, kayak aplikasi biasa.</small>`;
    } else if (ios) {
      box.hidden = false;
      box.innerHTML = `${Icon('sparkle')} <span>Di iPhone/iPad: buka di Safari, ketuk <b>Bagikan</b>, lalu pilih
        <b>Tambahkan ke Layar Utama</b>. Ini juga syarat notifikasi di iPhone nanti.</span>`;
    } else {
      box.hidden = true;
    }
  }

  function init() {
    renderBanner();
    $('streak-banner')?.addEventListener('click', onBannerClick);
    const input = $('reminder-time');
    if (input) {
      input.value = store.get('cb_reminder_time') || input.value;
      input.addEventListener('input', updateLinks);
      updateLinks();
    }
    $('reminder-install')?.addEventListener('click', async (e) => {
      if (!e.target.closest('[data-install]') || !installEvent) return;
      installEvent.prompt();
      await installEvent.userChoice.catch(() => null);
      installEvent = null;
      renderInstall();
    });
    renderInstall();
  }

  window.addEventListener('beforeinstallprompt', (e) => {
    e.preventDefault();                 // tampilkan tombol kita sendiri, bukan pop-up otomatis browser
    installEvent = e;
    renderInstall();
  });
  window.addEventListener('appinstalled', () => { installEvent = null; renderInstall(); });

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();

  return {
    /** Status streak terbaru (State.setStreak setelah sesi latihan / duel). */
    setStreak(st) {
      if (!st) return;
      streak = st;
      renderBanner();
    },
  };
})();
