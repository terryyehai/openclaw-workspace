// IPTV Web App Service Worker
const CACHE_NAME = 'iptv-v1';
const STATIC_ASSETS = [
    '/iptv-web-app/',
    '/iptv-web-app/index.html',
    '/iptv-web-app/css/style.css',
    '/iptv-web-app/js/app.js',
    '/iptv-web-app/js/player.js',
    '/iptv-web-app/js/storage.js',
    '/iptv-web-app/js/m3u8.js'
];

// Install event
self.addEventListener('install', (event) => {
    event.waitUntil(
        caches.open(CACHE_NAME).then((cache) => {
            return cache.addAll(STATIC_ASSETS);
        })
    );
    self.skipWaiting();
});

// Activate event
self.addEventListener('activate', (event) => {
    event.waitUntil(
        caches.keys().then((cacheNames) => {
            return Promise.all(
                cacheNames
                    .filter((name) => name !== CACHE_NAME)
                    .map((name) => caches.delete(name))
            );
        })
    );
    self.clients.claim();
});

// Fetch event
self.addEventListener('fetch', (event) => {
    const url = new URL(event.request.url);
    
    // Skip cross-origin requests except for M3U8 and images
    if (url.origin !== location.origin && 
        !url.pathname.endsWith('.m3u8') &&
        !url.pathname.endsWith('.png') &&
        !url.pathname.endsWith('.jpg') &&
        !url.pathname.endsWith('.jpeg') &&
        !url.pathname.endsWith('.svg') &&
        !url.pathname.endsWith('.gif')) {
        return;
    }
    
    // Network first for M3U8 (streaming)
    if (url.pathname.endsWith('.m3u8')) {
        event.respondWith(
            fetch(event.request).catch(() => {
                return new Response('#EXTM3U\n#EXTINF:-1,Offline\n', {
                    headers: { 'Content-Type': 'application/vnd.apple.mpegurl' }
                });
            })
        );
        return;
    }
    
    // Cache first for static assets
    event.respondWith(
        caches.match(event.request).then((response) => {
            if (response) {
                return response;
            }
            return fetch(event.request).then((networkResponse) => {
                // Cache successful responses
                if (networkResponse.ok) {
                    const responseClone = networkResponse.clone();
                    caches.open(CACHE_NAME).then((cache) => {
                        cache.put(event.request, responseClone);
                    });
                }
                return networkResponse;
            }).catch(() => {
                // Return offline page for navigation requests
                if (event.request.mode === 'navigate') {
                    return caches.match('/iptv-web-app/index.html');
                }
            });
        })
    );
});
