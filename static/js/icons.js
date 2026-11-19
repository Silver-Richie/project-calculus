/**
 * Calculus Bridge — Ikon SVG untuk JS (pasangan tag {% icon %} di gamification/templatetags/icons.py).
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
