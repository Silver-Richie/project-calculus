/**
 * Calculus Bridge — Toko Diamond 💎 (halaman Toko + tampilan kosmetik di seluruh aplikasi)
 *
 * Mechanism:
 *   - Katalog, saldo, dan kepemilikan selalu dari server (GET /api/toko/). Pembelian dan
 *     pemasangan dikirim ke server (POST /api/toko/beli/, /api/toko/pakai/), yang memeriksa
 *     saldo dan mengunci profil; frontend hanya menampilkan hasilnya.
 *   - Kosmetik terpasang (`look`: slot → kunci barang) awalnya dari json_script server-profile.
 *     dressAll() memasang gambar aksesori ke SEMUA SVG Archie di aplikasi: aksesori digambar
 *     sebagai <g class="archie-acc"> di koordinat viewBox 200×200 maskot (components/mascot.html);
 *     aksesori kepala menyembunyikan topi toga bawaan (<g class="archie-cap">).
 *   - Archie besar di halaman Toko memakai `preview`: klik kartu aksesori untuk mencobanya
 *     sebelum membeli.
 *   - Membeli butuh dua klik (klik pertama = "Beli?"), agar diamond tidak terbelanjakan tak sengaja.
 *
 * Bergantung pada modul global: State, Nav, SFX, Mascot, Practice, postJSON.
 */
const Shop = (() => {
  /** Titik-titik bintang 5 sudut berpusat di (cx, cy), untuk atribut points <polygon>. */
  const starPoints = (cx, cy, R, r) => Array.from({ length: 10 }, (_, i) => {
    const a = (i * 36 - 90) * Math.PI / 180;
    const d = i % 2 ? r : R;
    return `${(cx + Math.cos(a) * d).toFixed(1)},${(cy + Math.sin(a) * d).toFixed(1)}`;
  }).join(' ');
  const HEART = 'M0 8C-18-4-14-18 0-9C14-18 18-4 0 8Z';

  // Gambar aksesori (kunci = shop.py CATALOG).
  const ACC = {
    'acc-bunga': `
      <g transform="translate(74 62)">
        ${[0, 72, 144, 216, 288].map((a) => `<circle cx="${(Math.cos(a * Math.PI / 180) * 9).toFixed(1)}" cy="${(Math.sin(a * Math.PI / 180) * 9).toFixed(1)}" r="8" fill="#F472B6" stroke="#DB2777" stroke-width="2"/>`).join('')}
        <circle r="6" fill="#FDE047" stroke="#CA8A04" stroke-width="2"/>
      </g>`,
    'acc-headphone': `
      <path d="M46 106Q46 38 100 38Q154 38 154 106" stroke="#1F2937" stroke-width="9" fill="none" stroke-linecap="round"/>
      <rect x="32" y="90" width="22" height="36" rx="9" fill="#EF4444" stroke="#1F2937" stroke-width="3"/>
      <rect x="146" y="90" width="22" height="36" rx="9" fill="#EF4444" stroke="#1F2937" stroke-width="3"/>`,
    'acc-penyihir': `
      <path d="M70 76L106 8L132 76Z" fill="#7C3AED" stroke="#4C1D95" stroke-width="3" stroke-linejoin="round"/>
      <path d="M52 80Q100 62 148 80" stroke="#4C1D95" stroke-width="10" stroke-linecap="round" fill="none"/>
      <path d="M100 38l3 7 7 1-5 5 1 7-6-3-6 3 1-7-5-5 7-1z" fill="#FDE047"/>`,
    'acc-mahkota': `
      <path d="M62 76L68 38L85 58L100 30L115 58L132 38L138 76Z" fill="#FACC15" stroke="#CA8A04" stroke-width="3" stroke-linejoin="round"/>
      <circle cx="100" cy="60" r="5" fill="#EF4444"/>
      <circle cx="79" cy="66" r="3.5" fill="#3B82F6"/>
      <circle cx="121" cy="66" r="3.5" fill="#22C55E"/>`,
    'acc-kacamata': `
      <rect x="55" y="88" width="38" height="30" rx="9" fill="#111827" stroke="#000" stroke-width="2"/>
      <rect x="107" y="88" width="38" height="30" rx="9" fill="#111827" stroke="#000" stroke-width="2"/>
      <line x1="93" y1="100" x2="107" y2="100" stroke="#000" stroke-width="4" stroke-linecap="round"/>
      <path d="M62 95l10 0M114 95l10 0" stroke="#fff" stroke-width="3" stroke-linecap="round" opacity=".6"/>`,
    'acc-dasi': `
      <path d="M100 160L80 148L80 172Z" fill="#EF4444" stroke="#B91C1C" stroke-width="2.5" stroke-linejoin="round"/>
      <path d="M100 160L120 148L120 172Z" fill="#EF4444" stroke="#B91C1C" stroke-width="2.5" stroke-linejoin="round"/>
      <circle cx="100" cy="160" r="6" fill="#B91C1C"/>`,
    'acc-syal': `
      <path d="M54 146Q100 170 146 146L148 160Q100 186 52 160Z" fill="#F97316" stroke="#C2410C" stroke-width="2.5" stroke-linejoin="round"/>
      <path d="M118 164L126 194L110 194L106 168Z" fill="#F97316" stroke="#C2410C" stroke-width="2.5" stroke-linejoin="round"/>`,
    // kepala
    'acc-pesta': `
      <path d="M84 72L104 18L122 70Z" fill="#22D3EE" stroke="#0E7490" stroke-width="3" stroke-linejoin="round"/>
      <path d="M91 56L116 54M96 40L111 39" stroke="#FDE047" stroke-width="4" stroke-linecap="round"/>
      <circle cx="104" cy="18" r="6" fill="#F472B6" stroke="#DB2777" stroke-width="2"/>`,
    'acc-kucing': `
      <path d="M62 84L66 44L94 70Z" fill="#374151" stroke="#111827" stroke-width="3" stroke-linejoin="round"/>
      <path d="M138 84L134 44L106 70Z" fill="#374151" stroke="#111827" stroke-width="3" stroke-linejoin="round"/>
      <path d="M69 72L70 55L84 67Z" fill="#F9A8D4"/>
      <path d="M131 72L130 55L116 67Z" fill="#F9A8D4"/>`,
    'acc-kupluk': `
      <path d="M58 80Q58 34 100 34Q142 34 142 80Z" fill="#10B981" stroke="#047857" stroke-width="3" stroke-linejoin="round"/>
      <rect x="54" y="72" width="92" height="14" rx="7" fill="#34D399" stroke="#047857" stroke-width="3"/>
      <circle cx="100" cy="30" r="9" fill="#FDE047" stroke="#CA8A04" stroke-width="2.5"/>`,
    'acc-koboi': `
      <path d="M68 76Q66 40 84 38Q100 46 116 38Q134 40 132 76Q100 84 68 76Z" fill="#B45309" stroke="#78350F" stroke-width="3" stroke-linejoin="round"/>
      <path d="M68 66Q100 74 132 66" stroke="#FDE047" stroke-width="5" fill="none"/>
      <path d="M38 72Q100 92 162 72Q152 88 100 90Q48 88 38 72Z" fill="#92400E" stroke="#78350F" stroke-width="3" stroke-linejoin="round"/>`,
    'acc-halo': `
      <ellipse cx="100" cy="44" rx="34" ry="9" fill="none" stroke="#FACC15" stroke-width="6"/>
      <ellipse cx="100" cy="44" rx="34" ry="9" fill="none" stroke="#FEF9C3" stroke-width="2"/>`,
    // wajah (Archie sudah berkacamata: lensa di x 58–90 & 110–142, y 90–116)
    'acc-kumis': `
      <path d="M100 114Q90 107 80 111Q70 117 64 111Q69 126 84 122Q94 120 100 117Q106 120 116 122Q131 126 136 111Q130 117 120 111Q110 107 100 114Z" fill="#78350F" stroke="#451A03" stroke-width="2" stroke-linejoin="round"/>`,
    'acc-monokel': `
      <circle cx="126" cy="103" r="18" fill="#FEF3C7" fill-opacity=".25" stroke="#CA8A04" stroke-width="4"/>
      <path d="M142 112Q152 132 140 152" stroke="#CA8A04" stroke-width="2" fill="none" stroke-dasharray="3 3"/>`,
    'acc-3d': `
      <rect x="52" y="86" width="96" height="34" rx="6" fill="#F8FAFC" stroke="#334155" stroke-width="3"/>
      <rect x="58" y="91" width="34" height="24" rx="4" fill="#EF4444" opacity=".85"/>
      <rect x="108" y="91" width="34" height="24" rx="4" fill="#06B6D4" opacity=".85"/>`,
    'acc-hati': `
      <path d="${HEART}" transform="translate(74 107) scale(1.5)" fill="#EF4444" stroke="#991B1B" stroke-width="1.5" stroke-linejoin="round"/>
      <path d="${HEART}" transform="translate(126 107) scale(1.5)" fill="#EF4444" stroke="#991B1B" stroke-width="1.5" stroke-linejoin="round"/>
      <line x1="96" y1="98" x2="104" y2="98" stroke="#991B1B" stroke-width="3" stroke-linecap="round"/>`,
    'acc-bintang': `
      <polygon points="${starPoints(74, 104, 21, 10)}" fill="#FACC15" stroke="#CA8A04" stroke-width="2.5" stroke-linejoin="round"/>
      <polygon points="${starPoints(126, 104, 21, 10)}" fill="#FACC15" stroke="#CA8A04" stroke-width="2.5" stroke-linejoin="round"/>
      <line x1="92" y1="100" x2="108" y2="100" stroke="#CA8A04" stroke-width="3" stroke-linecap="round"/>`,
    // leher
    'acc-dasi-panjang': `
      <path d="M93 146L107 146L104 156L96 156Z" fill="#1D4ED8" stroke="#1E3A8A" stroke-width="2" stroke-linejoin="round"/>
      <path d="M96 156L104 156L109 176L100 185L91 176Z" fill="#2563EB" stroke="#1E3A8A" stroke-width="2" stroke-linejoin="round"/>
      <path d="M95 166L106 162M93 175L108 170" stroke="#FDE047" stroke-width="2"/>`,
    'acc-kalung-pi': `
      <path d="M66 140Q100 166 134 140" stroke="#CBD5E1" stroke-width="3" fill="none"/>
      <circle cx="100" cy="160" r="11" fill="#6366F1" stroke="#312E81" stroke-width="2.5"/>
      <text x="100" y="165" text-anchor="middle" font-size="15" font-weight="800" font-family="serif" fill="#fff">π</text>`,
    'acc-mutiara': Array.from({ length: 11 }, (_, i) => {
      const t = i / 10;
      const x = (1 - t) ** 2 * 64 + 2 * (1 - t) * t * 100 + t ** 2 * 136;
      const y = (1 - t) ** 2 * 140 + 2 * (1 - t) * t * 170 + t ** 2 * 140;
      return `<circle cx="${x.toFixed(1)}" cy="${y.toFixed(1)}" r="4.5" fill="#F8FAFC" stroke="#94A3B8" stroke-width="1.5"/>`;
    }).join(''),
    'acc-medali': `
      <path d="M80 142L96 166L104 166L120 142L110 142L100 158L90 142Z" fill="#3B82F6" stroke="#1D4ED8" stroke-width="2" stroke-linejoin="round"/>
      <circle cx="100" cy="172" r="11" fill="#FACC15" stroke="#CA8A04" stroke-width="3"/>
      <polygon points="${starPoints(100, 172, 6, 2.6)}" fill="#FEF9C3"/>`,
  };
  const ACC_SLOTS = ['head', 'face', 'neck'];
  // Satu tab per bagian; hanya isi tab aktif yang ditampilkan.
  const TABS = [
    { id: 'penguat', label: '⚡ Penguat', sub: 'Habis pakai', match: (it) => it.kind !== 'cosmetic' },
    { id: 'head', label: '🎩 Kepala', sub: 'Aksesori kepala Archie · klik kartu untuk mencoba', match: (it) => it.slot === 'head' },
    { id: 'face', label: '🕶️ Wajah', sub: 'Aksesori wajah Archie · klik kartu untuk mencoba', match: (it) => it.slot === 'face' },
    { id: 'neck', label: '🧣 Leher', sub: 'Aksesori leher Archie · klik kartu untuk mencoba', match: (it) => it.slot === 'neck' },
    { id: 'frame', label: '🖼️ Bingkai', sub: 'Tampil di profil & papan peringkat', match: (it) => it.slot === 'frame' },
    { id: 'title', label: '🏷️ Gelar', sub: 'Tampil di bawah namamu', match: (it) => it.slot === 'title' },
  ];
  const SLOT_LABEL = { head: 'kepala', face: 'wajah', neck: 'leher' };
  let tab = TABS[0].id;

  let data = null;
  let look = (() => {
    try { return JSON.parse(document.getElementById('server-profile')?.textContent || 'null')?.look || {}; }
    catch (_) { return {}; }
  })();
  let preview = null;           // { slot, key } aksesori yang sedang dicoba di Archie toko
  let confirmKey = null;
  let confirmTimer = null;

  /* ── tampilan kosmetik ───────────────────────────────────────────── */
  function dress(svg, eq) {
    svg.querySelectorAll('.archie-acc').forEach((g) => g.remove());
    const cap = svg.querySelector('.archie-cap');
    if (cap) cap.style.display = eq.head ? 'none' : '';
    ACC_SLOTS.forEach((slot) => {
      if (ACC[eq[slot]]) svg.insertAdjacentHTML('beforeend', `<g class="archie-acc">${ACC[eq[slot]]}</g>`);
    });
  }

  function dressAll() {
    document.querySelectorAll('#app svg[aria-label^="Archie"]').forEach((svg) => {
      dress(svg, svg.id === 'shop-archie-svg' && preview ? { ...look, [preview.slot]: preview.key } : look);
    });
    const av = document.getElementById('profile-avatar-lg');
    if (av) {
      av.className = av.className.replace(/\s*frame(-[\w-]+)?/g, '');
      if (look.frame) av.classList.add('frame', look.frame);
    }
    const title = document.getElementById('profile-title');
    if (title) title.textContent = look.title_text || '';
  }

  /* ── halaman toko ────────────────────────────────────────────────── */
  function actionHTML(it) {
    if (it.kind === 'cosmetic' && it.owned) {
      return `<button class="btn ${it.equipped ? 'btn-outline' : 'btn-growth'} btn-sm" onclick="Shop.equip('${it.key}', ${!it.equipped})">
        ${it.equipped ? 'Lepas' : 'Pakai'}</button>`;
    }
    const poor = data.gems < it.price;
    const asking = confirmKey === it.key;
    return `<button class="btn ${asking ? 'btn-accent' : 'btn-primary'} btn-sm" ${poor ? 'disabled title="Diamond kurang"' : ''}
      onclick="Shop.buy('${it.key}')">${asking ? `Beli? 💎 ${it.price}` : `💎 ${it.price}`}</button>`;
  }

  function stockHTML(it) {
    if (it.kind === 'shield') return `<small class="shop-stock">Punya ${data.star_shields}/${data.max_shields}</small>`;
    if (it.kind === 'hearts') return `<small class="shop-stock">Nyawa ${data.hearts.hearts}/${data.hearts.max_hearts}</small>`;
    if (ACC_SLOTS.includes(it.slot)) return `<small class="shop-stock">Slot ${SLOT_LABEL[it.slot]}${it.equipped ? ' · dipakai' : it.owned ? ' · dimiliki' : ''}</small>`;
    return it.equipped ? '<small class="shop-stock">Dipakai</small>' : it.owned ? '<small class="shop-stock">Dimiliki</small>' : '';
  }

  function cardHTML(it) {
    const tryOn = ACC_SLOTS.includes(it.slot);
    const icon = it.slot === 'frame' ? `<span class="frame-demo frame ${it.key}">A</span>` : it.icon;
    return `
      <div class="shop-item${it.owned ? ' owned' : ''}${it.equipped ? ' equipped' : ''}${preview?.key === it.key ? ' previewing' : ''}"
           ${tryOn ? `role="button" tabindex="0" onclick="Shop.tryOn('${it.key}', event)"` : ''}>
        <div class="shop-item-icon">${icon}</div>
        <div class="shop-item-body">
          <b>${it.name}</b>
          <p>${it.desc}</p>
          ${stockHTML(it)}
        </div>
        <div class="shop-item-action">${actionHTML(it)}</div>
      </div>`;
  }

  function render() {
    const box = document.getElementById('shop-catalog');
    if (!box || !data) return;
    document.getElementById('shop-gems').textContent = data.gems;
    const lv = State.get().level;
    const nextLv = (lv?.level || 1) + 1;
    document.getElementById('shop-earn').innerHTML = `
      <li>🎓 Naik level: <b>${data.rewards.level} × level baru</b>
        <small>Level ${nextLv}: +💎 ${data.rewards.level * nextLv}${lv ? ` · ${lv.need - lv.into} XP lagi` : ''}</small></li>
      <li>✅ Topik tuntas (lulus Sesi III): <b>+💎 ${data.rewards.topic}</b></li>
      <li>⚔️ Menang duel: <b>+💎 ${data.rewards.duel_win}</b></li>`;
    const name = document.getElementById('shop-preview-name');
    if (name) {
      const p = preview && data.items.find((x) => x.key === preview.key);
      name.textContent = p ? `Mencoba: ${p.name}` : look.title_text || 'Archie';
    }
    const g = TABS.find((t) => t.id === tab);
    box.innerHTML = `
      <div class="shop-tabs" role="tablist" aria-label="Bagian toko">
        ${TABS.map((t) => `<button type="button" class="shop-tab${t.id === tab ? ' active' : ''}" role="tab"
          aria-selected="${t.id === tab}" onclick="Shop.tab('${t.id}')">${t.label}
          <span class="shop-tab-count">${data.items.filter(t.match).length}</span></button>`).join('')}
      </div>
      <p class="shop-msg" id="shop-msg" role="status"></p>
      <section class="shop-group" role="tabpanel">
        <header><small>${g.sub}</small></header>
        <div class="shop-grid">${data.items.filter(g.match).map(cardHTML).join('')}</div>
      </section>`;
    dressAll();
  }

  function message(text, ok) {
    const el = document.getElementById('shop-msg');
    if (!el) return;
    el.textContent = text;
    el.className = `shop-msg ${ok ? 'ok' : 'err'}`;
  }

  function apply(d) {
    data = d;
    look = d.equipped || {};
    State.setGems(d.gems);
    if (d.hearts) State.setHearts(d.hearts);
    if (typeof Ranked !== 'undefined') Ranked.setShields(d.star_shields);
    render();
  }

  async function load() {
    try {
      const res = await fetch('/api/toko/');
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      apply(await res.json());
    } catch (err) {
      const box = document.getElementById('shop-catalog');
      if (box) box.innerHTML = `<p class="loading-text">Gagal memuat toko: ${err.message}</p>`;
    }
  }

  async function purchase(key) {
    const d = await postJSON('/api/toko/beli/', { item: key });
    apply(d);
    SFX.correct();
    return d;
  }

  document.addEventListener('DOMContentLoaded', () => { dressAll(); load(); });

  return {
    load,
    dressAll,
    /** Pindah tab bagian toko. */
    tab(id) {
      if (id === tab) return;
      tab = id;
      SFX.click();
      render();
    },
    /** Harga barang (untuk tombol di luar toko); '' bila katalog belum dimuat. */
    price(key) {
      const it = data?.items.find((x) => x.key === key);
      return it ? `💎 ${it.price}` : '💎';
    },
    async buy(key) {
      if (confirmKey !== key) {                     // klik pertama: minta konfirmasi
        confirmKey = key;
        clearTimeout(confirmTimer);
        confirmTimer = setTimeout(() => { confirmKey = null; render(); }, 4000);
        SFX.click();
        render();
        return;
      }
      confirmKey = null;
      clearTimeout(confirmTimer);
      try {
        await purchase(key);
        const it = data.items.find((x) => x.key === key);
        if (preview?.key === key) preview = null;
        render();
        message(`✅ ${it.name} berhasil dibeli!`, true);
        Mascot.setMood('celebrate', `Asyik, ${it.name}! 💎`);
      } catch (err) {
        SFX.wrong();
        render();
        message(err.message, false);
      }
    },
    async equip(key, on) {
      try {
        apply(await postJSON('/api/toko/pakai/', { item: key, on }));
        if (on && preview?.key === key) { preview = null; render(); }
        SFX.click();
      } catch (err) {
        SFX.wrong();
        message(err.message, false);
      }
    },
    /** Coba aksesori di Archie toko (klik kartu; klik lagi untuk berhenti mencoba). */
    tryOn(key, e) {
      if (e?.target.closest('button')) return;
      const it = data?.items.find((x) => x.key === key);
      if (!it) return;
      preview = preview?.key === key ? null : { slot: it.slot, key };
      SFX.click();
      render();
    },
    /** Tombol di panel "nyawa habis" (practice.js): isi penuh nyawa lalu kembali ke daftar sesi. */
    async refillHearts() {
      try {
        await purchase('hearts-full');
        Mascot.setMood('celebrate', '💖 Nyawa penuh lagi. Ayo lanjut latihan!');
        Practice.renderSessions();
      } catch (err) {
        SFX.wrong();
        Mascot.setMood('comfort', `${err.message} Naik level atau tuntaskan topik untuk dapat diamond.`);
      }
    },
  };
})();
