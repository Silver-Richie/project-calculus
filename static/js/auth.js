/**
 * Calculus Bridge — Auth & Onboarding UI (templates/auth/)
 *
 * PageTransition : animasi masuk/keluar pada <main id="auth-main"> saat
 *                  berpindah halaman lewat link [data-nav] atau form [data-transition].
 * AuthTabs       : tab "Masuk" / "Daftar" pada halaman login.
 * DiagStepper    : menampilkan soal tes kemampuan awal satu per satu.
 */

const PageTransition = (() => {
  const LEAVE_MS = 260;
  let leaving = false;

  function main() { return document.getElementById('auth-main'); }

  /** Jalankan animasi keluar lalu lanjutkan navigasi. */
  function leave(go) {
    const m = main();
    if (!m || leaving) { go(); return; }
    leaving = true;
    m.classList.add('is-leaving');
    setTimeout(go, LEAVE_MS);
  }

  function init() {
    const m = main();
    if (m) requestAnimationFrame(() => m.classList.add('is-entered'));

    document.addEventListener('click', (e) => {
      const a = e.target.closest('a[data-nav]');
      if (!a || e.metaKey || e.ctrlKey || e.shiftKey || a.target === '_blank') return;
      e.preventDefault();
      leave(() => { window.location.href = a.href; });
    });

    document.addEventListener('submit', (e) => {
      const form = e.target;
      if (!form.matches('form[data-transition]') || form.dataset.submitting) return;
      if (typeof form.checkValidity === 'function' && form.hasAttribute('data-stepper') && !form.checkValidity()) return;
      e.preventDefault();
      form.dataset.submitting = '1';
      leave(() => HTMLFormElement.prototype.submit.call(form));
    });

    // Kembali lewat tombol "back" browser (bfcache): reset animasi keluar.
    window.addEventListener('pageshow', (e) => {
      if (e.persisted && main()) {
        leaving = false;
        main().classList.remove('is-leaving');
        document.querySelectorAll('form[data-submitting]').forEach((f) => delete f.dataset.submitting);
      }
    });
  }

  return { init, leave };
})();

const AuthTabs = (() => {
  function show(tab) {
    const card = document.querySelector('[data-active-tab]');
    if (!card) return;
    card.dataset.activeTab = tab;
    card.querySelectorAll('.auth-tab').forEach((t) => t.classList.toggle('active', t.dataset.tab === tab));
    card.querySelectorAll('.auth-pane').forEach((p) => p.classList.toggle('active', p.id === `pane-${tab}`));
    const title = card.querySelector('.auth-title');
    if (title) title.textContent = title.dataset[`title${tab[0].toUpperCase()}${tab.slice(1)}`] || title.textContent;
    const first = card.querySelector(`#pane-${tab} input:not([type=hidden])`);
    if (first) first.focus({ preventScroll: true });
  }

  function init() {
    document.querySelectorAll('[data-active-tab] [data-tab]').forEach((btn) => {
      btn.addEventListener('click', () => show(btn.dataset.tab));
    });
  }

  return { init, show };
})();

const DiagStepper = (() => {
  let idx = 0;
  let items = [];
  let form = null;
  let board = null;      // papan tulis per soal (static/js/whiteboard.js)

  function answered(fs) { return !!fs.querySelector('input[type=radio]:checked'); }

  function update() {
    items.forEach((fs, i) => fs.classList.toggle('active', i === idx));
    if (board) board.load(`diag:${items[idx].dataset.index}`);
    const done = items.filter(answered).length;
    const bar = document.getElementById('diag-progress');
    if (bar) bar.style.width = `${Math.round((done / items.length) * 100)}%`;
    const counter = document.getElementById('diag-counter');
    if (counter) counter.textContent = `${done}/${items.length} terjawab`;

    const prev = form.querySelector('[data-step=prev]');
    const next = form.querySelector('[data-step=next]');
    const submit = form.querySelector('[data-step=submit]');
    const last = idx === items.length - 1;
    prev.disabled = idx === 0;
    next.hidden = last;
    next.disabled = !answered(items[idx]);
    submit.hidden = !last;
    submit.disabled = done < items.length;
  }

  function go(delta) {
    const n = Math.min(items.length - 1, Math.max(0, idx + delta));
    if (n === idx) return;
    idx = n;
    update();
  }

  function init() {
    form = document.querySelector('form[data-stepper]');
    if (!form) return;
    items = [...form.querySelectorAll('fieldset.dq')];
    if (!items.length) return;
    form.classList.add('stepper-on');
    if (typeof Whiteboard !== 'undefined') board = Whiteboard.mount(document.getElementById('diag-board'));
    // Mulai dari soal pertama yang belum dijawab (mis. setelah validasi gagal).
    const firstOpen = items.findIndex((fs) => !answered(fs));
    idx = firstOpen === -1 ? items.length - 1 : firstOpen;

    form.addEventListener('change', (e) => {
      if (e.target.type !== 'radio') return;
      const fs = e.target.closest('fieldset.dq');
      fs.querySelectorAll('.dq-option').forEach((l) => l.classList.toggle('selected', l.contains(e.target)));
      update();
      // Lanjut otomatis setelah memilih, kecuali di soal terakhir.
      if (items.indexOf(fs) === idx && idx < items.length - 1) setTimeout(() => go(1), 350);
    });
    form.querySelector('[data-step=prev]').addEventListener('click', () => go(-1));
    form.querySelector('[data-step=next]').addEventListener('click', () => go(1));
    items.forEach((fs) => fs.querySelectorAll('.dq-option').forEach((l) => {
      l.classList.toggle('selected', l.querySelector('input').checked);
    }));
    update();
  }

  return { init };
})();

document.addEventListener('DOMContentLoaded', () => {
  PageTransition.init();
  AuthTabs.init();
  DiagStepper.init();
});
