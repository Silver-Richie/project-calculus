/**
 * Calculus Bridge — Papan Tulis (Whiteboard)
 *
 * Komponen papan coret-coret untuk kuis, sesi latihan, dan tes diagnostik.
 *
 * Mechanism:
 *   - Coretan disimpan sebagai VEKTOR (daftar titik ternormalisasi terhadap lebar papan),
 *     bukan gambar, sehingga undo/redo, simpan per soal, dan ubah ukuran layar tetap tajam.
 *   - Tiga lapis canvas: latar (polos/garis/petak) · tinta (coretan selesai) · live (coretan
 *     yang sedang digambar). Penghapus bekerja langsung di lapis tinta (destination-out),
 *     jadi latar petak tidak ikut terhapus.
 *   - Setiap soal punya papan sendiri: load(key) menyimpan papan lama ke memori lalu
 *     memuat papan soal itu (soal baru = papan kosong; kembali ke soal = coretan muncul lagi).
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
  const memory = new Map();           // key → { strokes, past, future, bg }

  class Board {
    constructor(host) {
      this.host = host;
      this.tool = 'pen';              // pen | highlighter | line | eraser
      this.color = COLORS[0].c;
      this.sizeIdx = 1;
      this.eraserIdx = 1;
      this.state = { strokes: [], past: [], future: [], bg: 'petak' };
      this.key = null;
      this.live = null;
      this.build();
      this.bind();
    }

    /* ── DOM ─────────────────────────────────────────────────────── */
    build() {
      this.host.classList.add('wb');
      this.host.innerHTML = `
        <div class="wb-toolbar" role="toolbar" aria-label="Alat papan tulis">
          <div class="wb-group">
            <button type="button" class="wb-btn active" data-tool="pen" title="Spidol">🖊️</button>
            <button type="button" class="wb-btn" data-tool="highlighter" title="Stabilo">🖍️</button>
            <button type="button" class="wb-btn" data-tool="line" title="Garis lurus">📏</button>
            <button type="button" class="wb-btn" data-tool="eraser" title="Penghapus">🧽</button>
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
            <button type="button" class="wb-btn" data-act="clear" title="Hapus semua">🗑️</button>
            <button type="button" class="wb-btn wb-bg" data-act="bg" title="Ganti latar">▦</button>
          </div>
        </div>
        <div class="wb-surface">
          <canvas class="wb-layer wb-bg-layer"></canvas>
          <canvas class="wb-layer wb-ink"></canvas>
          <canvas class="wb-layer wb-live"></canvas>
          <span class="wb-hint">Papan tulis ✏️ — coret-coret di sini</span>
        </div>`;
      this.surface = this.host.querySelector('.wb-surface');
      [this.bgCanvas, this.inkCanvas, this.liveCanvas] = this.host.querySelectorAll('canvas');
      this.hint = this.host.querySelector('.wb-hint');
    }

    bind() {
      const tb = this.host.querySelector('.wb-toolbar');
      tb.addEventListener('click', (e) => {
        const b = e.target.closest('button');
        if (!b) return;
        if (b.dataset.tool) this.setTool(b.dataset.tool);
        if (b.dataset.color) { this.color = b.dataset.color; if (this.tool === 'eraser') this.setTool('pen'); this.mark('.wb-color', b); }
        if (b.dataset.size) {
          const i = +b.dataset.size;
          if (this.tool === 'eraser') this.eraserIdx = i; else this.sizeIdx = i;
          this.mark('.wb-size', b);
        }
        if (b.dataset.act === 'undo') this.undo();
        if (b.dataset.act === 'redo') this.redo();
        if (b.dataset.act === 'clear') this.clear();
        if (b.dataset.act === 'bg') this.cycleBg();
      });

      const c = this.liveCanvas;
      c.addEventListener('pointerdown', (e) => this.down(e));
      c.addEventListener('pointermove', (e) => this.move(e));
      ['pointerup', 'pointercancel', 'pointerleave'].forEach((t) => c.addEventListener(t, (e) => this.up(e)));
      this.host.addEventListener('keydown', (e) => {
        if (!(e.ctrlKey || e.metaKey)) return;
        if (e.key === 'z') { e.preventDefault(); this.undo(); }
        if (e.key === 'y') { e.preventDefault(); this.redo(); }
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

    /* ── ukuran & gambar ulang ───────────────────────────────────── */
    get W() { return this.surface.clientWidth || 1; }
    get H() { return this.surface.clientHeight || 1; }

    resize() {
      const dpr = window.devicePixelRatio || 1;
      [this.bgCanvas, this.inkCanvas, this.liveCanvas].forEach((cv) => {
        cv.width = Math.round(this.W * dpr);
        cv.height = Math.round(this.H * dpr);
        cv.getContext('2d').setTransform(dpr, 0, 0, dpr, 0, 0);
      });
      this.drawBg();
      this.redraw();
    }

    drawBg() {
      const ctx = this.bgCanvas.getContext('2d');
      const { W, H } = this;
      ctx.clearRect(0, 0, W, H);
      ctx.fillStyle = '#FFFEFB';
      ctx.fillRect(0, 0, W, H);
      const bg = this.state.bg;
      if (bg === 'polos') return;
      const step = bg === 'petak' ? 24 : 32;
      ctx.strokeStyle = bg === 'petak' ? 'rgba(37,99,235,.12)' : 'rgba(37,99,235,.18)';
      ctx.lineWidth = 1;
      ctx.beginPath();
      for (let y = step; y < H; y += step) { ctx.moveTo(0, y + .5); ctx.lineTo(W, y + .5); }
      if (bg === 'petak') for (let x = step; x < W; x += step) { ctx.moveTo(x + .5, 0); ctx.lineTo(x + .5, H); }
      ctx.stroke();
      const btn = this.host.querySelector('[data-act=bg]');
      if (btn) btn.textContent = { petak: '▦', garis: '☰', polos: '▢' }[bg];
    }

    drawStroke(ctx, s) {
      const W = this.W;
      const pts = s.pts;
      if (!pts.length) return;
      ctx.save();
      ctx.lineCap = s.tool === 'highlighter' ? 'butt' : 'round';
      ctx.lineJoin = 'round';
      ctx.globalCompositeOperation = s.tool === 'eraser' ? 'destination-out' : 'source-over';
      ctx.globalAlpha = s.tool === 'highlighter' ? 0.32 : 1;
      ctx.strokeStyle = s.tool === 'eraser' ? '#000' : s.color;
      ctx.fillStyle = ctx.strokeStyle;
      const base = s.size * W;
      if (pts.length === 1) {
        ctx.beginPath();
        ctx.arc(pts[0][0] * W, pts[0][1] * W, base / 2, 0, Math.PI * 2);
        ctx.fill();
      } else if (s.pressure) {
        // ketebalan berubah per segmen mengikuti tekanan stylus
        for (let i = 1; i < pts.length; i++) {
          ctx.beginPath();
          ctx.lineWidth = base * (0.35 + pts[i][2] * 1.3);
          ctx.moveTo(pts[i - 1][0] * W, pts[i - 1][1] * W);
          ctx.lineTo(pts[i][0] * W, pts[i][1] * W);
          ctx.stroke();
        }
      } else {
        ctx.beginPath();
        ctx.lineWidth = base;
        ctx.moveTo(pts[0][0] * W, pts[0][1] * W);
        for (let i = 1; i < pts.length - 1; i++) {        // kurva halus lewat titik tengah
          const mx = (pts[i][0] + pts[i + 1][0]) / 2, my = (pts[i][1] + pts[i + 1][1]) / 2;
          ctx.quadraticCurveTo(pts[i][0] * W, pts[i][1] * W, mx * W, my * W);
        }
        const last = pts[pts.length - 1];
        ctx.lineTo(last[0] * W, last[1] * W);
        ctx.stroke();
      }
      ctx.restore();
    }

    redraw() {
      const ctx = this.inkCanvas.getContext('2d');
      ctx.clearRect(0, 0, this.W, this.H);
      this.state.strokes.forEach((s) => this.drawStroke(ctx, s));
      this.hint.hidden = this.state.strokes.length > 0;
    }

    /* ── input pointer ───────────────────────────────────────────── */
    pos(e) {
      const r = this.liveCanvas.getBoundingClientRect();
      const p = e.pointerType === 'pen' && e.pressure > 0 ? e.pressure : 0.5;
      return [(e.clientX - r.left) / this.W, (e.clientY - r.top) / this.W, p];
    }

    down(e) {
      if (e.button > 0) return;
      e.preventDefault();
      try { this.liveCanvas.setPointerCapture(e.pointerId); } catch (_) { /* pointer sintetis / sudah dilepas */ }
      const sizePx = this.tool === 'eraser' ? ERASER_SIZES[this.eraserIdx]
        : this.tool === 'highlighter' ? SIZES[this.sizeIdx].px * 4 + 6 : SIZES[this.sizeIdx].px;
      const p = this.pos(e);
      this.live = { tool: this.tool, color: this.color, size: sizePx / this.W, pressure: e.pointerType === 'pen' && this.tool === 'pen', pts: [p] };
      if (this.tool === 'line') this.live.pts.push(p);
      this.hint.hidden = true;
      this.paintLive();
    }

    move(e) {
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
      if (s.tool === 'eraser') {
        // penghapus langsung bekerja di lapis tinta agar terlihat seketika
        this.redraw();
        this.drawStroke(this.inkCanvas.getContext('2d'), s);
        return;
      }
      const ctx = this.liveCanvas.getContext('2d');
      ctx.clearRect(0, 0, this.W, this.H);
      this.drawStroke(ctx, s);
    }

    up() {
      if (!this.live) return;
      const s = this.live;
      this.live = null;
      this.liveCanvas.getContext('2d').clearRect(0, 0, this.W, this.H);
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
      this.state = memory.get(key) || { strokes: [], past: [], future: [], bg: lastBg };
      this.live = null;
      this.drawBg();
      this.redraw();
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
