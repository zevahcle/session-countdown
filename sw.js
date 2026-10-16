// Offline support. The app is cached when first opened; every later launch is served from the
// cache at once, and the cache is refreshed in the background, so a new version shows on the next launch.
// Bump CACHE when the list of files changes.
const CACHE = 'session-countdown-v1';
const SHELL = [
  './', './index.html', './manifest.webmanifest', './icon.svg',
  './icon-192.png', './icon-512.png', './icon-maskable-512.png', './apple-touch-icon.png',
];

self.addEventListener('install', e => {
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(SHELL)).then(() => self.skipWaiting()));
});

self.addEventListener('activate', e => {
  e.waitUntil(caches.keys()
    .then(keys => Promise.all(keys.filter(k => k !== CACHE).map(k => caches.delete(k))))
    .then(() => self.clients.claim()));
});

self.addEventListener('fetch', e => {
  const req = e.request;
  if (req.method !== 'GET' || new URL(req.url).origin !== self.location.origin) return;
  const fresh = fetch(req).then(async res => {
    if (res.ok) { const copy = res.clone(); const c = await caches.open(CACHE); await c.put(req, copy); }
    return res;
  });
  e.waitUntil(fresh.catch(() => {}));
  e.respondWith(caches.match(req, { ignoreSearch: true })
    .then(hit => hit || (req.mode === 'navigate' ? caches.match('./') : undefined))
    .then(hit => hit || fresh));
});
