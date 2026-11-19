/**
 * Calculus Bridge — Render rumus LaTeX dengan KaTeX (static/vendor/katex, v0.16.11).
 *
 * Penulisan di konten (materi, slide, soal, pembahasan, tabel):
 *   inline  : $x^2 + 1$        atau \( x^2 + 1 \)
 *   blok    : $$\int_0^1 x\,dx$$ atau \[ … \]
 * Uang ditulis "Rp"/"USD", bukan "$", agar tidak terbaca sebagai rumus.
 *
 * Mechanism: satu MutationObserver memantau <body>; setiap kali HTML baru masuk (slide Kurikulum,
 * soal, pembahasan, duel, beranda), elemen yang memuat penanda rumus dirender dengan
 * renderMathInElement (dikelompokkan per frame agar ringan). Komponen tidak perlu memanggil apa pun.
 * MathRender.render(el) tersedia bila perlu memaksa render (mis. sebelum mengukur tinggi).
 * Rumus yang salah tulis tidak memecah halaman (throwOnError: false → teks merah KaTeX).
 */
const MathRender = (() => {
  'use strict';

  const OPTIONS = {
    delimiters: [
      { left: '$$', right: '$$', display: true },
      { left: '\\[', right: '\\]', display: true },
      { left: '$', right: '$', display: false },
      { left: '\\(', right: '\\)', display: false },
    ],
    ignoredTags: ['script', 'noscript', 'style', 'textarea', 'pre', 'code', 'option', 'svg'],
    ignoredClasses: ['no-math'],
    throwOnError: false,
    strict: 'ignore',
  };
  const HINT = /\$|\\\(|\\\[/;
  const pending = new Set();
  let scheduled = false;

  function render(el) {
    if (!el || typeof renderMathInElement === 'undefined' || !HINT.test(el.textContent || '')) return;
    renderMathInElement(el, OPTIONS);
  }

  function flush() {
    scheduled = false;
    const roots = [...pending];
    pending.clear();
    // render hanya akar terluar (anak dari akar lain sudah ikut)
    roots.filter((r) => r.isConnected && !roots.some((o) => o !== r && o.contains(r))).forEach(render);
  }

  function queue(node) {
    const el = node.nodeType === 1 ? node : node.parentElement;
    if (!el || el.closest('.katex')) return;   // hasil render KaTeX sendiri
    pending.add(el);
    if (!scheduled) { scheduled = true; requestAnimationFrame(flush); }
  }

  function init() {
    render(document.body);
    new MutationObserver((records) => {
      for (const r of records) {
        if (r.type === 'characterData') queue(r.target);
        else r.addedNodes.forEach(queue);
      }
    }).observe(document.body, { childList: true, subtree: true, characterData: true });
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();

  return { render };
})();
