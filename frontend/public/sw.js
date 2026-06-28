// Cadence app-shell service worker.
// Strategy: network-first for navigations (fall back to cached shell when offline),
// cache-first for same-origin static assets. API calls are never cached.
const CACHE = "cadence-shell-v1";
const SHELL = ["/", "/index.html"];

self.addEventListener("install", (event) => {
  event.waitUntil(
    caches.open(CACHE).then((cache) => cache.addAll(SHELL)).then(() => self.skipWaiting()),
  );
});

self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches
      .keys()
      .then((keys) => Promise.all(keys.filter((k) => k !== CACHE).map((k) => caches.delete(k))))
      .then(() => self.clients.claim()),
  );
});

self.addEventListener("fetch", (event) => {
  const { request } = event;
  if (request.method !== "GET") return;

  const url = new URL(request.url);
  if (url.origin !== self.location.origin) return;
  if (url.pathname.startsWith("/api/")) return; // never cache the API

  // Navigations: network-first, fall back to cached shell.
  if (request.mode === "navigate") {
    event.respondWith(
      fetch(request)
        .then((resp) => {
          const copy = resp.clone();
          caches.open(CACHE).then((c) => c.put("/", copy));
          return resp;
        })
        .catch(() => caches.match("/").then((r) => r || caches.match("/index.html"))),
    );
    return;
  }

  // Static assets: cache-first, populate on miss.
  event.respondWith(
    caches.match(request).then(
      (cached) =>
        cached ||
        fetch(request).then((resp) => {
          if (resp.ok && (url.pathname.startsWith("/assets/") || resp.type === "basic")) {
            const copy = resp.clone();
            caches.open(CACHE).then((c) => c.put(request, copy));
          }
          return resp;
        }),
    ),
  );
});
