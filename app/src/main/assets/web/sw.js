const CACHE_NAME = 'orthofinixai-v1';

self.addEventListener('install', (event) => {
  self.skipWaiting();
});

self.addEventListener('activate', (event) => {
  event.waitUntil(self.clients.claim());
});

self.addEventListener('fetch', (event) => {
  // Let network handle dynamic API / AI requests
  event.respondWith(
    fetch(event.request).catch(() => caches.match(event.request))
  );
});
