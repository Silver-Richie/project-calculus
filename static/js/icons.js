/**
 * Calculus Bridge — Ikon SVG untuk JS (pasangan tag {% icon %} di gamification/templatetags/icons.py).
 *
 * Icon('diamond')                       → '<svg class="ic ic-diamond" …><use href="#i-diamond"/></svg>'
 * Icon('heart', { size: 48, label: 'Nyawa' })
 * Icon.level(mainLevel)                 → ikon level kurikulum (lv-<slug>), atau emoji dari database
 *                                          bila level itu belum punya ikon.
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

  svg.level = (lvl) => (lvl && LEVELS.has(lvl.slug) ? svg(`lv-${lvl.slug}`) : (lvl?.icon || ''));
  return svg;
})();
