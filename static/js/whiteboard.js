/**
 * Calculus Bridge — Papan Tulis (Whiteboard)
 *
 * Komponen papan coret-coret untuk kuis, sesi latihan, dan tes diagnostik.
 *
 * Mechanism:
 *   - Kanvas tak terbatas ala Figma: coretan disimpan dalam KOORDINAT DUNIA (piksel pada
 *     zoom 100%), lalu digambar lewat transformasi tampilan view = {x, y, k}:
 *     layar = dunia × k + (x, y). Geser mengubah x/y, zoom mengubah k.
 *   - Coretan berupa VEKTOR (daftar titik), bukan gambar, sehingga tetap tajam saat di-zoom
 *     dan mendukung undo/redo serta papan terpisah per soal.
 *   - Tiga lapis canvas: latar (petak/garis/polos, digambar mengikuti view) · tinta (coretan
 *     selesai) · live (coretan yang sedang digambar). Penghapus bekerja di lapis tinta
 *     (destination-out), jadi latar petak tidak ikut terhapus.
 *   - Tebal pena dibagi k saat mulai menggores, jadi di layar tebalnya selalu terasa sama:
 *     zoom in = garis lebih halus (buat nulis di sela-sela), zoom out = garis lebih kasar.
 *   - Kebiasaan geser/zoom mengikuti Figma. Geser: alat tangan, Spasi+seret, klik tengah,
 *     scroll dua jari, atau dua jari di layar sentuh. Zoom: Ctrl/Cmd+scroll (cubit trackpad),
 *     cubit dua jari, tombol +/−, dan tombol persen untuk kembali ke 100%.
 *   - Pointer Events: mendukung mouse, jari, dan stylus (tebal mengikuti tekanan pena).
 *
 * Pemakaian: const board = Whiteboard.mount(elemen); board.load('id-soal');
 */
const Whiteboard = (() => {
  const COLORS = [
    { c: '#1E1B16', name: 'Hitam' }, { c: '#2563EB', name: 'Biru' },
    { c: '#DC2626', name: 'Merah' }, { c: '#16A34A', name: 'Hijau' },
  ];
  const SIZES = [{ px: 2, name: 'Tipis' }, { px: 4, name: 'Sedang' }, { px: 8, name: 'Tebal' }];
  const ERASER_SIZES = [12, 28, 56];
  const BACKGROUNDS = [{ id: 'petak', label: '▦ Petak' }, { id: 'garis', label: '☰ Garis' }, { id: 'polos', label: '▢ Polos' }];
  const MIN_K = 0.2, MAX_K = 5;
  const memory = new Map();           // key → { strokes, past, future, bg, view }

  const clamp = (v, lo, hi) => Math.min(hi, Math.max(lo, v));
  const newState = (bg = 'petak') => ({ strokes: [], past: [], future: [], bg, view: { x: 0, y: 0, k: 1 } });

  class Board {
    constructor(host) {
      this.host = host;
      this.tool = 'pen';              // pen | highlighter | line | eraser | pan
      this.color = COLORS[0].c;
      this.sizeIdx = 1;
      this.eraserIdx = 1;
      this.state = newState();
      this.key = null;
      this.live = null;
      this.ptrs = new Map();          // pointerId → {x, y} untuk cubit dua jari
      this.pan = null;                // {x, y} posisi pointer terakhir saat menggeser
      this.pinch = null;              // {dist, mid}
      this.spaceDown = false;
      this.hover = false;
      this.build();
      this.bind();
    }

    get view() { return this.state.view; }

    /* ── DOM ─────────────────────────────────────────────────────── */
    build() {
      this.host.classList.add('wb');
      this.host.innerHTML = `
        <div class="wb-toolbar" role="toolbar" aria-label="Alat papan tulis">
          <div class="wb-group">
            <button type="button" class="wb-btn active" data-tool="pen" title="Spidol">${Icon('pen')}</button>
            <button type="button" class="wb-btn" data-tool="highlighter" title="Stabilo">${Icon('highlighter')}</button>
            <button type="button" class="wb-btn" data-tool="line" title="Garis lurus">${Icon('ruler')}</button>
            <button type="button" class="wb-btn" data-tool="eraser" title="Penghapus">${Icon('eraser')}</button>
            <button type="button" class="wb-btn" data-tool="pan" title="Geser kanvas (atau tahan Spasi sambil seret)">${Icon('hand')}</button>
          </div>
          <div class="wb-group wb-colors">
            ${COLORS.map((k, i) => `<button type="button" class="wb-color${i === 0 ? ' active' : ''}" data-color="${k.c}" title="${k.name}" style="--c:${k.c}"></button>`).join('')}
          </div>
          <div class="wb-group wb-sizes">
            ${SIZES.map((s, i) => `<button type="button" class="wb-size${i === 1 ? ' active' : ''}" data-size="${i}" title="${s.name}"><i style="--s:${s.px + 2}px"></i></button>`).join('')}
          </div>
          <div class="wb-group">
            <button type="button" class="wb-btn" data-act="undo" title="Batalkan (Ctrl+Z)">↶</button>
            <button type="button" class="wb-btn" data-act="redo" title="Ulangi (Ctrl+Y)">↷</button>
            <button type="button" class="wb-btn" data-act="clear" title="Hapus semua">${Icon('trash')}</button>
            <button type="button" class="wb-btn wb-bg" data-act="bg" title="Ganti latar">▦</button>
          </div>
        </div>
        <div class="wb-surface">
          <canvas class="wb-layer wb-bg-layer"></canvas>
          <canvas class="wb-layer wb-ink"></canvas>
          <canvas class="wb-layer wb-live"></canvas>
          <span class="wb-hint">Kanvas Coretan · corat-coret di sini
            <small>Kanvasnya tanpa batas — scroll dua jari, tahan Spasi, atau pakai alat tangan buat geser cari ruang kosong.</small>
          </span>
          <div class="wb-zoom" role="group" aria-label="Perbesaran papan">
            <button type="button" class="wb-zoom-btn" data-act="zoom-out" title="Perkecil" aria-label="Perkecil">−</button>
            <button type="button" class="wb-zoom-pct" data-act="zoom-reset" title="Kembali ke tampilan awal (100%)">100%</button>
            <button type="button" class="wb-zoom-btn" data-act="zoom-in" title="Perbesar" aria-label="Perbesar">+</button>
          </div>
        </div>`;
      this.surface = this.host.querySelector('.wb-surface');
      [this.bgCanvas, this.inkCanvas, this.liveCanvas] = this.host.querySelectorAll('canvas');
      this.hint = this.host.querySelector('.wb-hint');
      this.pct = this.host.querySelector('.wb-zoom-pct');
    }

    bind() {
      this.host.addEventListener('click', (e) => {
        const b = e.target.closest('button');
        if (!b || !this.host.contains(b)) return;
        if (b.dataset.tool) this.setTool(b.dataset.tool);
        if (b.dataset.color) { this.color = b.dataset.color; if (this.tool === 'eraser' || this.tool === 'pan') this.setTool('pen'); this.mark('.wb-color', b); }
        if (b.dataset.size) {
          const i = +b.dataset.size;
          if (this.tool === 'eraser') this.eraserIdx = i; else this.sizeIdx = i;
          this.mark('.wb-size', b);
        }
        const act = b.dataset.act;
        if (act === 'undo') this.undo();
        if (act === 'redo') this.redo();
        if (act === 'clear') this.clear();
        if (act === 'bg') this.cycleBg();
        if (act === 'zoom-in' || act === 'zoom-out') {
          const r = this.surface.getBoundingClientRect();     // zoom dari tengah papan
          this.zoomAt(r.width / 2, r.height / 2, act === 'zoom-in' ? 1.25 : 1 / 1.25);
        }
        if (act === 'zoom-reset') this.resetView();
      });

      const c = this.liveCanvas;
      c.addEventListener('pointerdown', (e) => this.down(e));
      c.addEventListener('pointermove', (e) => this.move(e));
      ['pointerup', 'pointercancel', 'pointerleave'].forEach((t) => c.addEventListener(t, (e) => this.up(e)));
      c.addEventListener('wheel', (e) => this.onWheel(e), { passive: false });

      this.host.addEventListener('keydown', (e) => {
        if (!(e.ctrlKey || e.metaKey)) return;
        if (e.key === 'z') { e.preventDefault(); this.undo(); }
        if (e.key === 'y') { e.preventDefault(); this.redo(); }
      });
      this.surface.addEventListener('pointerenter', () => { this.hover = true; });
      this.surface.addEventListener('pointerleave', () => { this.hover = false; });
      // Spasi + seret = geser kanvas, hanya saat kursor ada di atas papan
      window.addEventListener('keydown', (e) => {
        if (e.code !== 'Space' || !this.hover || this.spaceDown) return;
        e.preventDefault();
        this.spaceDown = true;
        this.surface.classList.add('wb-grab');
      });
      window.addEventListener('keyup', (e) => {
        if (e.code !== 'Space') return;
        this.spaceDown = false;
        this.surface.classList.remove('wb-grab');
      });
      this.host.tabIndex = 0;
      new ResizeObserver(() => this.resize()).observe(this.surface);
    }

    mark(sel, btn) {
      this.host.querySelectorAll(sel).forEach((x) => x.classList.toggle('active', x === btn));
    }

    setTool(t) {
      this.tool = t;
      this.host.querySelectorAll('[data-tool]').forEach((x) => x.classList.toggle('active', x.dataset.tool === t));
      // tombol ukuran menunjukkan ukuran alat aktif (spidol vs penghapus)
      const idx = t === 'eraser' ? this.eraserIdx : this.sizeIdx;
      this.host.querySelectorAll('.wb-size').forEach((x, i) => x.classList.toggle('active', i === idx));
      this.surface.dataset.tool = t;
    }

    /* ── ukuran, tampilan (pan/zoom) & gambar ulang ──────────────── */
    get W() { return this.surface.clientWidth || 1; }
    get H() { return this.surface.clientHeight || 1; }

    /** Posisi pointer relatif terhadap sudut kiri-atas papan (piksel layar). */
    local(e) {
      const r = this.surface.getBoundingClientRect();
      return [e.clientX - r.left, e.clientY - r.top];
    }

    /** Piksel layar (relatif papan) → koordinat dunia. */
    toWorld(sx, sy) {
      const v = this.view;
      return [(sx - v.x) / v.k, (sy - v.y) / v.k];
    }

    /** Pasang transformasi dunia→layar pada sebuah context. */
    applyView(ctx) {
      const dpr = window.devicePixelRatio || 1;
      const v = this.view;
      ctx.setTransform(dpr * v.k, 0, 0, dpr * v.k, dpr * v.x, dpr * v.y);
    }

    /** Zoom di sekitar satu titik layar, sehingga titik dunia di bawahnya tidak bergeser. */
    zoomAt(sx, sy, factor) {
      const v = this.view;
      const k = clamp(v.k * factor, MIN_K, MAX_K);
      v.x = sx - (sx - v.x) * (k / v.k);
      v.y = sy - (sy - v.y) * (k / v.k);
      v.k = k;
      this.refresh();
    }

    panBy(dx, dy) {
      this.view.x += dx;
      this.view.y += dy;
      this.refresh();
    }

    /**
     * Roda scroll / trackpad, mengikuti kebiasaan Figma:
     *   scroll biasa (dua jari) = geser kanvas · Ctrl/Cmd + scroll (cubit trackpad) = zoom
     * Halaman di belakang sengaja tidak ikut scroll selama kursor ada di atas papan.
     */
    onWheel(e) {
      e.preventDefault();
      const line = e.deltaMode === 1;                  // sebagian mouse melaporkan baris, bukan piksel
      if (e.ctrlKey || e.metaKey) {
        const p = this.local(e);
        this.zoomAt(p[0], p[1], Math.exp(-e.deltaY * (line ? 0.08 : 0.01)));
        return;
      }
      const f = line ? 16 : 1;
      const dx = e.shiftKey && !e.deltaX ? e.deltaY : e.deltaX;   // Shift+roda = geser mendatar
      const dy = e.shiftKey && !e.deltaX ? 0 : e.deltaY;
      this.panBy(-dx * f, -dy * f);
    }

    resetView() {
      this.state.view = { x: 0, y: 0, k: 1 };
      this.refresh();
    }

    refresh() {
      this.drawBg();
      this.redraw();
      if (this.live) this.paintLive();
      if (this.pct) this.pct.textContent = `${Math.round(this.view.k * 100)}%`;
    }

    resize() {
      const dpr = window.devicePixelRatio || 1;
      [this.bgCanvas, this.inkCanvas, this.liveCanvas].forEach((cv) => {
        cv.width = Math.round(this.W * dpr);
        cv.height = Math.round(this.H * dpr);
      });
      this.refresh();
    }

    drawBg() {
      const ctx = this.bgCanvas.getContext('2d');
      const dpr = window.devicePixelRatio || 1;
      const { W, H } = this;
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      ctx.clearRect(0, 0, W, H);
      ctx.fillStyle = '#FFFEFB';
      ctx.fillRect(0, 0, W, H);
      const btn = this.host.querySelector('[data-act=bg]');
      if (btn) btn.textContent = { petak: '▦', garis: '☰', polos: '▢' }[this.state.bg];
      if (this.state.bg === 'polos') return;

      const k = this.view.k;
      let step = this.state.bg === 'petak' ? 24 : 32;
      while (step * k < 14) step *= 2;                  // zoom jauh: garis dirapikan biar tidak gelap
      const [x0, y0] = this.toWorld(0, 0);
      const [x1, y1] = this.toWorld(W, H);
      this.applyView(ctx);
      ctx.strokeStyle = this.state.bg === 'petak' ? 'rgba(37,99,235,.12)' : 'rgba(37,99,235,.18)';
      ctx.lineWidth = 1 / k;                            // tetap setipis 1 piksel layar
      ctx.beginPath();
      for (let y = Math.ceil(y0 / step) * step; y < y1; y += step) { ctx.moveTo(x0, y); ctx.lineTo(x1, y); }
      if (this.state.bg === 'petak') {
        for (let x = Math.ceil(x0 / step) * step; x < x1; x += step) { ctx.moveTo(x, y0); ctx.lineTo(x, y1); }
      }
      ctx.stroke();
    }

    drawStroke(ctx, s) {
      const pts = s.pts;
      if (!pts.length) return;
      ctx.save();
      ctx.lineCap = s.tool === 'highlighter' ? 'butt' : 'round';
      ctx.lineJoin = 'round';
      ctx.globalCompositeOperation = s.tool === 'eraser' ? 'destination-out' : 'source-over';
      ctx.globalAlpha = s.tool === 'highlighter' ? 0.32 : 1;
      ctx.strokeStyle = s.tool === 'eraser' ? '#000' : s.color;
      ctx.fillStyle = ctx.strokeStyle;
      const base = s.size;
      if (pts.length === 1) {
        ctx.beginPath();
        ctx.arc(pts[0][0], pts[0][1], base / 2, 0, Math.PI * 2);
        ctx.fill();
      } else if (s.pressure) {
        // ketebalan berubah per segmen mengikuti tekanan stylus
        for (let i = 1; i < pts.length; i++) {
          ctx.beginPath();
          ctx.lineWidth = base * (0.35 + pts[i][2] * 1.3);
          ctx.moveTo(pts[i - 1][0], pts[i - 1][1]);
          ctx.lineTo(pts[i][0], pts[i][1]);
          ctx.stroke();
        }
      } else {
        ctx.beginPath();
        ctx.lineWidth = base;
        ctx.moveTo(pts[0][0], pts[0][1]);
        for (let i = 1; i < pts.length - 1; i++) {        // kurva halus lewat titik tengah
          const mx = (pts[i][0] + pts[i + 1][0]) / 2, my = (pts[i][1] + pts[i + 1][1]) / 2;
          ctx.quadraticCurveTo(pts[i][0], pts[i][1], mx, my);
        }
        const last = pts[pts.length - 1];
        ctx.lineTo(last[0], last[1]);
        ctx.stroke();
      }
      ctx.restore();
    }

    redraw() {
      const ctx = this.inkCanvas.getContext('2d');
      ctx.setTransform(1, 0, 0, 1, 0, 0);
      ctx.clearRect(0, 0, this.inkCanvas.width, this.inkCanvas.height);
      this.applyView(ctx);
      this.state.strokes.forEach((s) => this.drawStroke(ctx, s));
      this.hint.hidden = this.state.strokes.length > 0;
    }

    /* ── input pointer ───────────────────────────────────────────── */
    pos(e) {
      const [sx, sy] = this.local(e);
      const p = e.pointerType === 'pen' && e.pressure > 0 ? e.pressure : 0.5;
      const [wx, wy] = this.toWorld(sx, sy);
      return [wx, wy, p];
    }

    /** Buang coretan yang sedang berjalan (mis. karena jari kedua menyentuh layar). */
    cancelLive() {
      if (!this.live) return;
      this.live = null;
      const ctx = this.liveCanvas.getContext('2d');
      ctx.setTransform(1, 0, 0, 1, 0, 0);
      ctx.clearRect(0, 0, this.liveCanvas.width, this.liveCanvas.height);
      this.redraw();                                    // penghapus menggambar langsung di lapis tinta
    }

    down(e) {
      e.preventDefault();
      try { this.liveCanvas.setPointerCapture(e.pointerId); } catch (_) { /* pointer sintetis / sudah dilepas */ }
      this.ptrs.set(e.pointerId, { x: e.clientX, y: e.clientY });
      if (this.ptrs.size === 2) {                       // dua jari: cubit untuk zoom + geser
        this.cancelLive();
        this.pan = null;
        this.pinch = this.pinchData();
        return;
      }
      if (this.ptrs.size > 2) return;
      if (e.button === 1 || this.tool === 'pan' || this.spaceDown) {
        this.pan = { x: e.clientX, y: e.clientY };
        this.surface.classList.add('wb-grabbing');
        return;
      }
      if (e.button > 0) return;
      const sizePx = this.tool === 'eraser' ? ERASER_SIZES[this.eraserIdx]
        : this.tool === 'highlighter' ? SIZES[this.sizeIdx].px * 4 + 6 : SIZES[this.sizeIdx].px;
      const p = this.pos(e);
      this.live = {
        tool: this.tool, color: this.color,
        size: sizePx / this.view.k,                     // tebal di layar tetap sama di zoom berapa pun
        pressure: e.pointerType === 'pen' && this.tool === 'pen',
        pts: [p],
      };
      if (this.tool === 'line') this.live.pts.push(p);
      this.hint.hidden = true;
      this.paintLive();
    }

    /** Jarak & titik tengah dua pointer yang sedang menyentuh layar. */
    pinchData() {
      const [a, b] = [...this.ptrs.values()];
      return {
        dist: Math.hypot(a.x - b.x, a.y - b.y) || 1,
        mid: { x: (a.x + b.x) / 2, y: (a.y + b.y) / 2 },
      };
    }

    move(e) {
      if (this.ptrs.has(e.pointerId)) this.ptrs.set(e.pointerId, { x: e.clientX, y: e.clientY });
      if (this.pinch && this.ptrs.size >= 2) {
        e.preventDefault();
        const now = this.pinchData();
        this.view.x += now.mid.x - this.pinch.mid.x;    // dua jari digeser bareng = geser kanvas
        this.view.y += now.mid.y - this.pinch.mid.y;
        const r = this.surface.getBoundingClientRect();
        const factor = now.dist / this.pinch.dist;
        this.pinch = now;
        this.zoomAt(now.mid.x - r.left, now.mid.y - r.top, factor);   // zoomAt sudah memanggil refresh
        return;
      }
      if (this.pan) {
        e.preventDefault();
        this.panBy(e.clientX - this.pan.x, e.clientY - this.pan.y);
        this.pan = { x: e.clientX, y: e.clientY };
        return;
      }
      if (!this.live) return;
      e.preventDefault();
      const p = this.pos(e);
      if (this.live.tool === 'line') {
        this.live.pts[1] = p;
        if (e.shiftKey) {                                   // Shift: kunci horizontal/vertikal
          const [a] = this.live.pts;
          if (Math.abs(p[0] - a[0]) > Math.abs(p[1] - a[1])) this.live.pts[1] = [p[0], a[1], p[2]];
          else this.live.pts[1] = [a[0], p[1], p[2]];
        }
      } else {
        const co = e.getCoalescedEvents ? e.getCoalescedEvents() : [];
        const evs = co.length ? co : [e];          // sebagian event (mis. sintetis) tidak punya coalesced events
        evs.forEach((ev) => this.live.pts.push(this.pos(ev)));
      }
      this.paintLive();
    }

    paintLive() {
      const s = this.live;
      if (!s) return;
      if (s.tool === 'eraser') {
        // penghapus langsung bekerja di lapis tinta agar terlihat seketika
        this.redraw();
        const ink = this.inkCanvas.getContext('2d');
        this.applyView(ink);
        this.drawStroke(ink, s);
        return;
      }
      const ctx = this.liveCanvas.getContext('2d');
      ctx.setTransform(1, 0, 0, 1, 0, 0);
      ctx.clearRect(0, 0, this.liveCanvas.width, this.liveCanvas.height);
      this.applyView(ctx);
      this.drawStroke(ctx, s);
    }

    up(e) {
      if (e) this.ptrs.delete(e.pointerId);
      if (this.pinch && this.ptrs.size < 2) this.pinch = null;
      if (this.pan) {
        this.pan = null;
        this.surface.classList.remove('wb-grabbing');
        return;
      }
      if (!this.live) return;
      const s = this.live;
      this.live = null;
      const ctx = this.liveCanvas.getContext('2d');
      ctx.setTransform(1, 0, 0, 1, 0, 0);
      ctx.clearRect(0, 0, this.liveCanvas.width, this.liveCanvas.height);
      this.commit(() => this.state.strokes.push(s));
    }

    /* ── riwayat ─────────────────────────────────────────────────── */
    commit(fn) {
      this.state.past.push(this.state.strokes.slice());
      if (this.state.past.length > 100) this.state.past.shift();
      this.state.future = [];
      fn();
      this.redraw();
    }

    undo() {
      if (!this.state.past.length) return;
      this.state.future.push(this.state.strokes);
      this.state.strokes = this.state.past.pop();
      this.redraw();
    }

    redo() {
      if (!this.state.future.length) return;
      this.state.past.push(this.state.strokes);
      this.state.strokes = this.state.future.pop();
      this.redraw();
    }

    clear() {
      if (!this.state.strokes.length) return;
      this.commit(() => { this.state.strokes = []; });
    }

    cycleBg() {
      const ids = BACKGROUNDS.map((b) => b.id);
      this.state.bg = ids[(ids.indexOf(this.state.bg) + 1) % ids.length];
      this.drawBg();
    }

    /* ── papan per soal ──────────────────────────────────────────── */
    load(key) {
      if (this.key !== null) memory.set(this.key, this.state);
      this.key = key;
      const lastBg = this.state.bg;
      this.state = memory.get(key) || newState(lastBg);
      this.live = null;
      this.pan = null;
      this.pinch = null;
      this.ptrs.clear();
      this.refresh();
    }
  }

  return {
    /** Pasang papan tulis pada elemen `host` (sekali saja per elemen). */
    mount(host) {
      if (!host) return null;
      if (!host._wb) host._wb = new Board(host);
      return host._wb;
    },
  };
})();
