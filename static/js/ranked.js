/**
 * Calculus Bridge — Halaman Ranked (layar rank duel bergaya lobi game).
 *
 * Mechanism:
 *   - Data awal dari json_script "server-profile" (rank = ranking.describe + menang/kalah,
 *     star_shields, max_shields). Setelah duel selesai duel.js memanggil Ranked.update(rank, shieldUsed);
 *     setelah membeli perisai di toko shop.js memanggil Ranked.setShields(n).
 *   - Lambang tier dari RankEmblem (rank_emblem.js): besar & beranimasi di panggung, kecil di
 *     Jalan menuju Apex dan daftar tier.
 *   - Tombol Mulai Duel (#duel-start-btn) dihubungkan oleh duel.js; Papan Rank membuka halaman
 *     Peringkat pada tab Rank Duel.
 *
 * Bergantung pada modul global: RankEmblem (rank_emblem.js), RankBadge, Leaderboard (leaderboard.js), Nav (app.js).
 */
const Ranked = (() => {
  'use strict';

  const TIERS = ['terra', 'luna', 'solar', 'nova', 'apex'];
  const NAME = { terra: 'Terra', luna: 'Luna', solar: 'Solar', nova: 'Nova', apex: 'Apex' };
  const ROAD_NOTE = { terra: '3★ × 3', luna: '4★ × 3', solar: '4★ × 3', nova: '5★ × 3', apex: 'Apex Points' };

  const profile = (() => {
    try { return JSON.parse(document.getElementById('server-profile')?.textContent || 'null') || {}; }
    catch (_) { return {}; }
  })();
  let rank = profile.rank || null;
  let shields = profile.star_shields || 0;
  const maxShields = profile.max_shields || 5;

  const $ = (id) => document.getElementById(id);

  function starsHTML(r) {
    if (r.max_stars == null) return `<span class="ranked-apex-stars">${r.apex_points ?? 0} AP</span>`;
    return Array.from({ length: r.max_stars }, (_, i) => `<span class="rs${i < r.stars ? ' on' : ''}">★</span>`).join('');
  }

  function roadHTML(r) {
    const cur = TIERS.indexOf(r.tier);
    return TIERS.map((t, i) => `
      <li class="tier-${t} ${i < cur ? 'done' : i === cur ? 'now' : 'next'}">
        <span class="rr-icon">${RankEmblem.svg(t, { size: 34 })}</span><b>${NAME[t]}</b><small>${ROAD_NOTE[t]}</small>
      </li>`).join('');
  }

  function render() {
    const hero = $('ranked-hero');
    if (!hero || !rank) return;
    hero.className = `ranked-hero tier-${rank.tier}`;
    $('ranked-label').textContent = rank.label;
    $('ranked-emblem').innerHTML = RankEmblem.svg(rank.tier, { size: 200, animated: true, label: `Lambang ${rank.label}` });
    $('ranked-stars').innerHTML = starsHTML(rank);
    $('ranked-next').textContent = RankBadge.next(rank);
    const wins = rank.wins || 0, total = wins + (rank.losses || 0);
    $('ranked-winrate').textContent = total ? `${(wins / total * 100).toFixed(1)}%` : '–';
    $('ranked-total').textContent = total;
    $('ranked-streak').innerHTML = rank.win_streak ? `${Icon('flame')} ${rank.win_streak}` : '0';
    $('ranked-shields').textContent = `${shields}/${maxShields}`;
    $('ranked-shield-bar').style.width = `${Math.min(100, shields / maxShields * 100)}%`;
    $('ranked-road').innerHTML = roadHTML(rank);
  }

  function init() {
    render();
    document.querySelectorAll('.tier-emb').forEach((el) => { el.innerHTML = RankEmblem.svg(el.dataset.tier, { size: 28 }); });
    document.querySelectorAll('[data-ranked]').forEach((b) => b.addEventListener('click', () => {
      if (b.dataset.ranked === 'board') {
        Leaderboard.show('rank', false);
        Nav.go('rank');
        return;
      }
      const info = $('ranked-info');
      info.open = true;
      info.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }));
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();

  return {
    render,
    /** Rank terbaru setelah duel (duel.js); shieldUsed = Perisai Bintang terpakai di duel itu. */
    update(next, shieldUsed) {
      rank = { ...rank, ...next };
      if (shieldUsed) shields = Math.max(0, shields - 1);
      render();
    },
    /** Stok Perisai Bintang terbaru (shop.js). */
    setShields(n) {
      shields = n;
      render();
    },
  };
})();
