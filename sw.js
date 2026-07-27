const CACHE = 'precios-v3';
const SHELL = ['./', './index.html', './manifest.json', './icon-192.png', './icon-512.png',
  'https://cdn.jsdelivr.net/npm/chart.js@4.5.0/dist/chart.umd.js'];
const NETWORK_FIRST = ['index.html', 'manifest.json', 'icon-192.png', 'icon-512.png'];

self.addEventListener('install', e => {
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(SHELL)).then(() => self.skipWaiting()));
});
self.addEventListener('activate', e => {
  e.waitUntil(caches.keys().then(keys => Promise.all(keys.filter(k => k !== CACHE).map(k => caches.delete(k)))).then(() => self.clients.claim()));
});
self.addEventListener('fetch', e => {
  const url = new URL(e.request.url);
  const isNetFirst = url.pathname.endsWith('data.json') || NETWORK_FIRST.some(f => url.pathname.endsWith(f)) || url.pathname.endsWith('/');
  if (isNetFirst) {
    // red primero, caché si no hay conexión
    e.respondWith(
      fetch(e.request).then(r => {
        const copy = r.clone();
        caches.open(CACHE).then(c => c.put(e.request, copy));
        return r;
      }).catch(() => caches.match(e.request, {ignoreSearch:true}))
    );
  } else {
    // resto: caché primero, red como respaldo
    e.respondWith(caches.match(e.request, {ignoreSearch:true}).then(r => r || fetch(e.request)));
  }
});
