/**
 * Calculus Bridge — Riwayat Pengerjaan & Arsip Coret-coretan (Mode Level Up)
 *
 * Alur:
 *   Node topik yang sudah tuntas di Skill Tree → modal dua pilihan (Practice.openFromTree):
 *     "Coba Ulang Level"        → buka drawer topik seperti biasa
 *     "Lihat Riwayat Pengerjaan" → daftar percobaan topik itu (terbaru dulu) → rincian per soal
 *
 * Mechanism:
 *   - Data dari GET /api/riwayat/topik/<slug>/ (daftar) dan GET /api/riwayat/<id>/ (rincian).
 *     Server juga yang membuang riwayat lebih dari 30 hari (gamification/history.py).
 *   - Coretan papan tulis disimpan sebagai VEKTOR, lalu digambar ulang di sini oleh StrokeView:
 *     kanvas read-only dengan pan (geser) & zoom, jadi garisnya tetap tajam diperbesar berapa pun.
 *     `space` pada data menentukan satuan titik: 'norm' (pecahan lebar papan) atau 'world' (piksel).
 *   - Kertas coretan sengaja tetap putih di tema gelap (tintanya hitam/biru/merah/hijau);
 *     bingkai dan panelnya yang mengikuti tema.
 *
 * Bergantung pada modul global: Icon (icons.js), SFX & Practice (app.js/practice.js).
 */
const LevelHistory = (() => {
  const NORM_UNIT = 1000;        // 1 satuan lebar papan = 1000 px dunia saat space = 'norm'
  const MIN_K = 0.1;
  const MAX_K = 8;
  let el = null;                 // overlay yang sedang terbuka
  let views = [];                // StrokeView aktif (dibersihkan saat overlay ditutup)

  /* ── viewer coretan (read-only) ──────────────────────────────────── */
  class StrokeView {
    constructor(host, payload) {
      this.host = host;
      this.space = payload.space === 'world' ? 'world' : 'norm';
      this.unit = this.space === 'norm' ? NORM_UNIT : 1;
      this.strokes = payload.strokes || [];
      this.view = { x: 0, y: 0, k: 1 };
      this.pointers = new Map();
      this.build();
      this.bind();
      this.resize();
    }

    build() {
      this.host.innerHTML = `
        <canvas class="sv-canvas"></canvas>
        <div class="sv-tools">
          <button type="button" class="sv-btn" data-sv="out" title="Perkecil" aria-label="Perkecil">−</button>
          <button type="button" class="sv-btn" data-sv="in" title="Perbesar" aria-label="Perbesar">+</button>
          <button type="button" class="sv-btn sv-reset" data-sv="fit" title="Pas layar">Pas</button>
        </div>
        <span class="sv-zoom">100%</span>`;
      this.canvas = this.host.querySelector('.sv-canvas');
      this.ink = document.createElement('canvas');   // lapis tinta terpisah agar penghapus tidak mengikis kertas
      this.label = this.host.querySelector('.sv-zoom');
    }

    bind() {
      this.host.querySelector('.sv-tools').addEventListener('click', (e) => {
        const act = e.target.closest('button')?.dataset.sv;
        if (!act) return;
        if (act === 'fit') this.fit();
        else this.zoomAt(this.W / 2, this.H / 2, act === 'in' ? 1.25 : 0.8);
      });
      const c = this.canvas;
      c.addEventListener('pointerdown', (e) => {
        c.setPointerCapture?.(e.pointerId);
        this.pointers.set(e.pointerId, [e.clientX, e.clientY]);
        this.pinch = this.pointers.size === 2 ? this.pinchData() : null;
      });
      c.addEventListener('pointermove', (e) => {
        const prev = this.pointers.get(e.pointerId);
        if (!prev) return;
        this.pointers.set(e.pointerId, [e.clientX, e.clientY]);
        if (this.pointers.size >= 2) { this.pinchMove(); return; }
        this.panBy(e.clientX - prev[0], e.clientY - prev[1]);
      });
      ['pointerup', 'pointercancel', 'pointerleave'].forEach((t) => c.addEventListener(t, (e) => {
        this.pointers.delete(e.pointerId);
        this.pinch = this.pointers.size === 2 ? this.pinchData() : null;
      }));
      // Scroll biasa/dua jari = geser · Ctrl/Cmd + scroll (cubit trackpad) = zoom — sama dengan papan tulis.
      c.addEventListener('wheel', (e) => {
        e.preventDefault();
        const line = e.deltaMode === 1 ? 16 : 1;
        if (e.ctrlKey || e.metaKey) {
          const r = c.getBoundingClientRect();
          this.zoomAt(e.clientX - r.left, e.clientY - r.top, Math.exp(-e.deltaY * (e.deltaMode === 1 ? .08 : .01)));
          return;
        }
        this.panBy(-e.deltaX * line, -e.deltaY * line);
      }, { passive: false });
      this.ro = new ResizeObserver(() => this.resize());
      this.ro.observe(this.host);
    }

    destroy() { this.ro?.disconnect(); }

    get W() { return this.canvas.clientWidth || 1; }
    get H() { return this.canvas.clientHeight || 1; }

    resize() {
      const dpr = window.devicePixelRatio || 1;
      [this.canvas, this.ink].forEach((cv) => { cv.width = Math.round(this.W * dpr); cv.height = Math.round(this.H * dpr); });
      this.dpr = dpr;
      if (!this.fitted) { this.fit(); this.fitted = true; } else this.draw();
    }

    /** Kotak pembatas semua coretan dalam koordinat dunia. */
    bounds() {
      let x0 = Infinity, y0 = Infinity, x1 = -Infinity, y1 = -Infinity;
      this.strokes.forEach((s) => (s.pts || []).forEach((p) => {
        x0 = Math.min(x0, p[0]); y0 = Math.min(y0, p[1]);
        x1 = Math.max(x1, p[0]); y1 = Math.max(y1, p[1]);
      }));
      if (!Number.isFinite(x0)) return null;
      const u = this.unit;
      return { x0: x0 * u, y0: y0 * u, x1: x1 * u, y1: y1 * u };
    }

    /** Pas layar: seluruh coretan terlihat, dengan sedikit margin. */
    fit() {
      const b = this.bounds();
      if (!b) { this.view = { x: 0, y: 0, k: 1 }; this.draw(); return; }
      const pad = 24;
      const w = Math.max(b.x1 - b.x0, 1), h = Math.max(b.y1 - b.y0, 1);
      const k = Math.min((this.W - pad * 2) / w, (this.H - pad * 2) / h, MAX_K);
      this.k0 = Math.max(MIN_K, k);
      this.view = {
        k: this.k0,
        x: (this.W - w * k) / 2 - b.x0 * k,
        y: (this.H - h * k) / 2 - b.y0 * k,
      };
      this.draw();
    }

    panBy(dx, dy) { this.view.x += dx; this.view.y += dy; this.draw(); }

    zoomAt(sx, sy, factor) {
      const v = this.view;
      const k = Math.min(MAX_K, Math.max(MIN_K, v.k * factor));
      v.x = sx - ((sx - v.x) / v.k) * k;
      v.y = sy - ((sy - v.y) / v.k) * k;
      v.k = k;
      this.draw();
    }

    pinchData() {
      const [a, b] = [...this.pointers.values()];
      const r = this.canvas.getBoundingClientRect();
      return {
        dist: Math.hypot(a[0] - b[0], a[1] - b[1]) || 1,
        mid: [(a[0] + b[0]) / 2 - r.left, (a[1] + b[1]) / 2 - r.top],
      };
    }

    pinchMove() {
      const now = this.pinchData();
      if (this.pinch) {
        this.panBy(now.mid[0] - this.pinch.mid[0], now.mid[1] - this.pinch.mid[1]);
        this.zoomAt(now.mid[0], now.mid[1], now.dist / this.pinch.dist);
      }
      this.pinch = now;
    }

    apply(ctx) {
      const { x, y, k } = this.view;
      ctx.setTransform(this.dpr * k, 0, 0, this.dpr * k, this.dpr * x, this.dpr * y);
    }

    draw() {
      const ctx = this.canvas.getContext('2d');
      const { W, H, dpr } = this;
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      ctx.fillStyle = '#FFFEFB';
      ctx.fillRect(0, 0, W, H);
      this.grid(ctx);
      const ink = this.ink.getContext('2d');
      ink.setTransform(dpr, 0, 0, dpr, 0, 0);
      ink.clearRect(0, 0, W, H);
      this.apply(ink);
      this.strokes.forEach((s) => this.stroke(ink, s));
      ink.setTransform(1, 0, 0, 1, 0, 0);
      ctx.setTransform(1, 0, 0, 1, 0, 0);
      ctx.drawImage(this.ink, 0, 0);
      // Persen dihitung relatif terhadap "Pas layar" (= 100%), karena satuan koordinat
      // coretan berbeda antar versi papan tulis sehingga 1:1 piksel tidak berarti apa-apa.
      this.label.textContent = `${Math.round((this.view.k / (this.k0 || this.view.k)) * 100)}%`;
    }

    /** Petak tipis seperti kertas papan tulis, ikut digeser & di-zoom. */
    grid(ctx) {
      const { k } = this.view;
      let step = this.space === 'norm' ? NORM_UNIT * .034 : 24;   // ±24 px di papan aslinya
      while (step * k < 14) step *= 2;
      const [x0, y0] = [(0 - this.view.x) / k, (0 - this.view.y) / k];
      const [x1, y1] = [(this.W - this.view.x) / k, (this.H - this.view.y) / k];
      this.apply(ctx);
      ctx.strokeStyle = 'rgba(37,99,235,.12)';
      ctx.lineWidth = 1 / k;
      ctx.beginPath();
      for (let x = Math.floor(x0 / step) * step; x < x1; x += step) { ctx.moveTo(x, y0); ctx.lineTo(x, y1); }
      for (let y = Math.floor(y0 / step) * step; y < y1; y += step) { ctx.moveTo(x0, y); ctx.lineTo(x1, y); }
      ctx.stroke();
      ctx.setTransform(1, 0, 0, 1, 0, 0);
    }

    /** Gambar satu coretan — aturannya sama dengan papan tulis (whiteboard.js drawStroke). */
    stroke(ctx, s) {
      const pts = s.pts || [];
      if (!pts.length) return;
      const u = this.unit;
      const P = (i) => [pts[i][0] * u, pts[i][1] * u];
      ctx.save();
      ctx.lineCap = s.tool === 'highlighter' ? 'butt' : 'round';
      ctx.lineJoin = 'round';
      ctx.globalCompositeOperation = s.tool === 'eraser' ? 'destination-out' : 'source-over';
      ctx.globalAlpha = s.tool === 'highlighter' ? .32 : 1;
      ctx.strokeStyle = s.tool === 'eraser' ? '#000' : (s.color || '#1E1B16');
      ctx.fillStyle = ctx.strokeStyle;
      const base = (s.size || .004) * u;
      if (pts.length === 1) {
        const [x, y] = P(0);
        ctx.beginPath();
        ctx.arc(x, y, base / 2, 0, Math.PI * 2);
        ctx.fill();
      } else if (s.pressure) {
        for (let i = 1; i < pts.length; i++) {
          ctx.beginPath();
          ctx.lineWidth = base * (0.35 + (pts[i][2] ?? .5) * 1.3);
          ctx.moveTo(...P(i - 1));
          ctx.lineTo(...P(i));
          ctx.stroke();
        }
      } else {
        ctx.beginPath();
        ctx.lineWidth = base;
        ctx.moveTo(...P(0));
        for (let i = 1; i < pts.length - 1; i++) {
          const [ax, ay] = P(i), [bx, by] = P(i + 1);
          ctx.quadraticCurveTo(ax, ay, (ax + bx) / 2, (ay + by) / 2);
        }
        ctx.lineTo(...P(pts.length - 1));
        ctx.stroke();
      }
      ctx.restore();
    }
  }

  /* ── overlay ─────────────────────────────────────────────────────── */
  function close() {
    views.forEach((v) => v.destroy());
    views = [];
    el?.remove();
    el = null;
  }

  function overlay(inner, wide) {
    close();
    el = document.createElement('div');
    el.className = `modal-overlay hist-overlay${wide ? ' hist-wide' : ''}`;
    el.innerHTML = `<div class="modal-card hist-card" role="dialog" aria-modal="true" aria-label="Riwayat pengerjaan">${inner}</div>`;
    el.addEventListener('click', (e) => { if (e.target === el || e.target.closest('[data-hist=close]')) close(); });
    document.addEventListener('keydown', onEsc);
    document.body.appendChild(el);
    requestAnimationFrame(() => el.classList.add('open'));
    return el;
  }

  function onEsc(e) {
    if (e.key !== 'Escape' || !el) return;
    document.removeEventListener('keydown', onEsc);
    close();
  }

  const esc = (s) => String(s ?? '').replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));

  function dateText(iso) {
    const d = new Date(iso);
    if (Number.isNaN(d.getTime())) return iso || '';
    return d.toLocaleString('id-ID', { day: 'numeric', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit' });
  }

  function durText(sec) {
    if (!sec) return '';
    const m = Math.floor(sec / 60);
    return m ? `${m} mnt ${sec % 60} dtk` : `${sec} dtk`;
  }

  async function get(url) {
    const res = await fetch(url);
    const data = await res.json();
    if (!res.ok) throw new Error(data.message || `HTTP ${res.status}`);
    return data;
  }

  function loading(box) {
    box.innerHTML = '<p class="loading-text">Memuat riwayat…</p>';
  }

  return {
    /** Modal dua pilihan untuk node topik yang sudah tuntas. */
    offer(slug, title) {
      overlay(`
        <h3 class="hist-h">${esc(title)}</h3>
        <p class="hist-sub">Topik ini udah kamu tuntasin. Mau ngulang buat naikin skor, atau lihat pengerjaan lamamu?</p>
        <div class="hist-offer">
          <button type="button" class="btn btn-primary" data-hist="replay">${Icon('refresh')} Coba Ulang Level</button>
          <button type="button" class="btn btn-outline" data-hist="open">${Icon('clock')} Lihat Riwayat Pengerjaan</button>
        </div>
        <button type="button" class="btn btn-ghost btn-sm hist-close" data-hist="close">Tutup</button>`);
      el.querySelector('[data-hist=replay]').addEventListener('click', () => { close(); Practice.openTopicFromTree(slug); });
      el.querySelector('[data-hist=open]').addEventListener('click', () => this.open(slug, title));
      el.querySelector('[data-hist=replay]').focus();
    },

    /** Daftar percobaan pada satu topik, terbaru dulu. */
    async open(slug, title) {
      const box = overlay(`<div class="hist-body"></div>`, true).querySelector('.hist-body');
      loading(box);
      let data;
      try {
        data = await get(`/api/riwayat/topik/${slug}/`);
      } catch (err) {
        box.innerHTML = `<p class="loading-text">Riwayat gagal dimuat: ${esc(err.message)}</p>`;
        return;
      }
      const head = `
        <div class="hist-head">
          <div>
            <h3 class="hist-h">${Icon('clock')} Riwayat Pengerjaan</h3>
            <p class="hist-sub">${esc(data.topic.title || title || '')} · tersimpan 30 hari terakhir</p>
          </div>
          <button type="button" class="btn btn-outline btn-sm" data-hist="close">${Icon('x')} Tutup</button>
        </div>`;
      if (!data.attempts.length) {
        box.innerHTML = `${head}
          <div class="hist-empty">${Icon('book')}<p>Belum ada percobaan yang tercatat buat topik ini.
            Riwayat mulai terisi dari sesi yang kamu kerjakan setelah fitur ini aktif, dan disimpan 30 hari.</p></div>`;
        return;
      }
      box.innerHTML = `${head}
        <ul class="hist-list">
          ${data.attempts.map((a) => `
            <li>
              <button type="button" class="hist-item" data-rec="${a.id}">
                <span class="hist-when"><b>Percobaan #${a.attempt_no}</b><small>${esc(dateText(a.created_at))}</small></span>
                <span class="hist-meta">
                  <span class="hist-score ${a.passed ? 'ok' : 'bad'}">${Icon(a.passed ? 'check' : 'x')} Benar ${a.score_correct}/${a.total}</span>
                  <small>${esc(a.session_title)}${a.duration_seconds ? ` · ${durText(a.duration_seconds)}` : ''}${a.scratchpads ? ` · ${a.scratchpads} coretan` : ''}</small>
                </span>
                <span class="hist-go">${Icon('next')}</span>
              </button>
            </li>`).join('')}
        </ul>`;
      box.querySelectorAll('[data-rec]').forEach((b) => b.addEventListener('click', () => this.attempt(+b.dataset.rec, slug, data.topic.title)));
    },

    /** Rincian satu percobaan: tiap soal, jawaban, dan arsip coretannya. */
    async attempt(id, slug, title) {
      const box = overlay(`<div class="hist-body"></div>`, true).querySelector('.hist-body');
      loading(box);
      let data;
      try {
        data = await get(`/api/riwayat/${id}/`);
      } catch (err) {
        box.innerHTML = `<p class="loading-text">Rincian gagal dimuat: ${esc(err.message)}</p>`;
        return;
      }
      box.innerHTML = `
        <div class="hist-head">
          <div>
            <h3 class="hist-h">Percobaan #${data.attempt_no || ''} · ${esc(data.session_title)}</h3>
            <p class="hist-sub">${esc(dateText(data.created_at))} · Benar ${data.score_correct}/${data.total}
              ${data.duration_seconds ? ` · ${durText(data.duration_seconds)}` : ''} · ${data.passed ? 'Lulus' : 'Belum lulus'}</p>
          </div>
          <span class="hist-head-act">
            <button type="button" class="btn btn-outline btn-sm" data-hist="back">${Icon('prev')} Daftar</button>
            <button type="button" class="btn btn-outline btn-sm" data-hist="close">${Icon('x')} Tutup</button>
          </span>
        </div>
        <ol class="hist-q">
          ${data.questions.map((q) => `
            <li class="hist-qrow ${q.is_correct ? 'ok' : 'bad'}">
              <div class="hist-qhead">
                <span class="hist-badge">${Icon(q.is_correct ? 'check' : 'x')} Soal ${q.number}</span>
                <span class="hist-prompt">${esc(q.prompt)}</span>
              </div>
              <div class="hist-ans">
                <span class="hist-a ${q.is_correct ? 'ok' : 'bad'}"><small>Jawabanmu</small>${esc(q.user_answer) || '<i>tidak dijawab</i>'}</span>
                ${q.is_correct ? '' : `<span class="hist-a key"><small>Kunci</small>${esc(q.correct_answer) || '—'}</span>`}
              </div>
              ${(q.scratchpad?.strokes || []).length
                ? `<div class="hist-pad" data-pad='${esc(JSON.stringify(q.scratchpad))}'></div>`
                : q.scratchpad?.trimmed
                  ? `<p class="hist-nopad">${Icon('warning')} Coretan soal ini terlalu besar, jadi gak disimpan.</p>`
                  : `<p class="hist-nopad">${Icon('pen')} Gak ada coretan di soal ini.</p>`}
            </li>`).join('')}
        </ol>`;
      box.querySelector('[data-hist=back]').addEventListener('click', () => this.open(slug, title));
      box.querySelectorAll('.hist-pad').forEach((pad) => {
        let payload;
        try { payload = JSON.parse(pad.dataset.pad); } catch (_) { return; }
        views.push(new StrokeView(pad, payload));
      });
    },

    close,
  };
})();
