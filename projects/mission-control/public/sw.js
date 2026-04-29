const CACHE_VERSION = "mc-v2-no-stale-ui";

self.addEventListener("install", (event) => {
  self.skipWaiting();
});

self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches
      .keys()
      .then((keys) => Promise.all(keys.map((key) => caches.delete(key))))
      .then(() => clients.claim())
  );
});

self.addEventListener("fetch", (event) => {
  const url = new URL(event.request.url);

  if (event.request.method !== "GET") return;

  // Never cache app shell, routes, or API responses. Mission Control must show the current build.
  if (url.pathname.startsWith("/api/") || event.request.mode === "navigate" || event.request.destination === "document") {
    event.respondWith(fetch(event.request, { cache: "no-store" }));
    return;
  }

  // Static assets are content-hashed by Next and safe to cache after the first network attempt.
  if (url.pathname.startsWith("/_next/static/")) {
    event.respondWith(
      fetch(event.request).catch(() => caches.match(event.request))
    );
  }
});
