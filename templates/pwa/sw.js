/* Calculus Bridge — service worker (dilayani dari /sw.js oleh gamification.views.service_worker_view).
 * Tahap 1: aplikasi bisa dipasang + halaman cadangan saat offline. Soal, progres, dan API selalu lewat
 * jaringan (tidak di-cache) agar penilaian tetap di server. Tahap 2 (Web Push) menambah event 'push' di sini. */
const CACHE = 'cb-shell-{{ version }}';
const OFFLINE_URL = '{{ offline_url }}';
const PRECACHE = [OFFLINE_URL, '{{ icon }}'];

self.addEventListener('install', (event) => {
  event.waitUntil(caches.open(CACHE).then((cache) => cache.addAll(PRECACHE)));
  self.skipWaiting();
});

self.addEventListener('activate', (event) => {
  event.waitUntil(caches.keys().then((keys) => Promise.all(
    keys.filter((k) => k.startsWith('cb-shell-') && k !== CACHE).map((k) => caches.delete(k)))));
  self.clients.claim();
});

self.addEventListener('fetch', (event) => {
  if (event.request.mode !== 'navigate') return;            // aset & API: perilaku jaringan biasa
  event.respondWith(fetch(event.request).catch(() => caches.match(OFFLINE_URL)));
});
