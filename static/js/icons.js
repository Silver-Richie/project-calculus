/**
 * Calculus Bridge — Ikon SVG & foto profil (Avatar) untuk JS (pasangan tag {% icon %} di gamification/templatetags/icons.py).
 *
 * Icon('diamond')                       → '<svg class="ic ic-diamond" …><use href="#i-diamond"/></svg>'
 * Icon('heart', { size: 48, label: 'Nyawa' })
 * Icon.of(nilai)                        → nilai dari data (fakultas, level, node, topik, item toko):
 *                                          nama ikon sprite → <svg>; selain itu (simbol matematika
 *                                          seperti ∂, Γ, Σ, d/dx) → lencana glyph .ic-glyph.
 * Icon.level(mainLevel)                 → ikon level kurikulum (sama dengan Icon.of(mainLevel.icon)).
 *
 * Mechanism: sprite <symbol id="i-…"> ada di templates/components/icons.html (dimuat di base.html).
 * Tanpa size, ikon mengikuti ukuran teks (kelas .ic di style.css).
 */
const Icon = (() => {
  'use strict';

  const LEVELS = new Set(['precalculus', 'kalkulus-dasar', 'kalkulus-menengah', 'kalkulus-lanjut']);

  function svg(name, { size, className = '', label = '' } = {}) {
    const dims = size ? ` width="${size}" height="${size}"` : '';
    const a11y = label ? `role="img" aria-label="${String(label).replace(/"/g, '&quot;')}"` : 'aria-hidden="true"';
    return `<svg class="ic ic-${name} ${className}"${dims} ${a11y} focusable="false"><use href="#i-${name}"/></svg>`;
  }

  const esc = (t) => String(t).replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));

  svg.of = (value, opts) => {
    if (!value) return '';
    if (/^[a-z][a-z0-9-]*$/.test(value) && document.getElementById(`i-${value}`)) return svg(value, opts);
    return `<span class="ic-glyph${opts?.className ? ` ${opts.className}` : ''}" aria-hidden="true">${esc(value)}</span>`;
  };
  svg.level = (lvl) => (lvl && LEVELS.has(lvl.slug) ? svg(`lv-${lvl.slug}`) : svg.of(lvl?.icon));
  return svg;
})();

/**
 * Foto profil (gamification/avatar.py): polos (inisial berwarna), template (gradien + ikon), atau unggahan.
 * Avatar.html(av, name, username, cls)  → <span class="cls avatar-…">…</span>
 * Avatar.paint(el, av, name, username)  → perbarui elemen yang sudah ada (sidebar/Profil) tanpa
 *                                         membuang kelas lain (mis. bingkai dari toko).
 * Warna polos = hash username, sama dengan tag {% avatar %} (templatetags/icons.py).
 */
const Avatar = (() => {
  'use strict';

  const COLORS = ['#2563EB', '#16A34A', '#D97706', '#DB2777', '#7C3AED', '#0D9488', '#DC2626', '#4B5563'];
  const esc = (t) => String(t ?? '').replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
  const colorOf = (key) => COLORS[[...String(key || '?')].reduce((h, c) => (h * 31 + c.codePointAt(0)) >>> 0, 7) % COLORS.length];

  function parts(av, name, username) {
    const kind = av?.kind === 'upload' && av.url ? 'upload' : av?.kind === 'preset' && av.icon ? 'preset' : 'initial';
    if (kind === 'upload') return { kind, style: '', inner: `<img src="${esc(av.url)}" alt="" loading="lazy">` };
    if (kind === 'preset') return { kind, style: `--a1:${av.bg[0]};--a2:${av.bg[1]}`, inner: Icon(av.icon) };
    return { kind, style: `--av:${colorOf(username || name)}`, inner: esc((String(name || '?')[0] || '?').toUpperCase()) };
  }

  return {
    colorOf,
    html(av, name, username, cls = '') {
      const p = parts(av, name, username);
      return `<span class="${cls} avatar avatar-${p.kind}" style="${p.style}">${p.inner}</span>`;
    },
    paint(el, av, name, username) {
      if (!el) return;
      const p = parts(av, name, username);
      el.classList.remove('avatar-initial', 'avatar-preset', 'avatar-upload');
      el.classList.add('avatar', `avatar-${p.kind}`);
      el.style.cssText = p.style;
      el.innerHTML = p.inner;
    },
  };
})();
