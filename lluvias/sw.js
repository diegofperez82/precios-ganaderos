const CACHE = 'lluvias-v2';
const SHELL = ['./', './index.html', './manifest.json', './icon-192.png', './icon-512.png',
  'https://cdn.jsdelivr.net/npm/chart.js@4.5.0/dist/chart.umd.js'];

self.addEventListener('install', e => {
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(SHELL)).then(() => self.skipWaiting()));
});
self.addEventListener('activate', e => {
  e.waitUntil(caches.keys().then(keys => Promise.all(keys.filter(k => k !== CACHE).map(k => caches.delete(k)))).then(() => self.clients.claim()));
});
self.addEventListener('fetch', e => {
  if (e.request.method !== 'GET') return;                    // los envios al formulario van directo
  const url = e.request.url;
  if (url.includes('docs.google.com')) return;               // el CSV siempre por red
  // pagina e iconos: primero red (asi las actualizaciones entran solas), cache si no hay senal
  if (e.request.mode === 'navigate' 