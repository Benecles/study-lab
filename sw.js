/* CUFRGS · modo ônibus
   Service worker that only does anything after a reader turns on offline mode
   (assets/offline.js). It then keeps a copy of every page listed in
   offline-manifest.json so the site works without a connection. */
const PREFIX = 'cufrgs-offline-';
const FONT_CACHE = 'cufrgs-offline-fonts';
const ROOT = self.registration.scope; // …/study-lab/
const NAV_TIMEOUT = 3500;

self.addEventListener('install', () => self.skipWaiting());
self.addEventListener('activate', (e) => e.waitUntil(self.clients.claim()));

async function currentCache() {
  const keys = (await caches.keys()).filter((k) => k.startsWith(PREFIX) && k !== FONT_CACHE);
  return keys.length ? caches.open(keys.sort().pop()) : null;
}

async function broadcast(msg) {
  for (const c of await self.clients.matchAll({ includeUncontrolled: true })) c.postMessage(msg);
}

async function cacheFonts(texts) {
  const fonts = await caches.open(FONT_CACHE);
  const cssUrls = new Set();
  for (const t of texts) for (const m of t.matchAll(/https:\/\/fonts\.googleapis\.com\/css2\?[^"')\s]+/g)) cssUrls.add(m[0].replace(/&amp;/g, '&'));
  for (const u of cssUrls) {
    try {
      const r = await fetch(u, { mode: 'cors' });
      if (!r.ok) continue;
      const css = await r.clone().text();
      await fonts.put(u, r);
      for (const m of css.matchAll(/url\((https:\/\/fonts\.gstatic\.com\/[^)]+)\)/g)) {
        if (await fonts.match(m[1])) continue;
        try { const f = await fetch(m[1], { mode: 'cors' }); if (f.ok) await fonts.put(m[1], f); } catch (e) {}
      }
    } catch (e) {}
  }
}

async function download(force) {
  const res = await fetch(new URL('offline-manifest.json', ROOT), { cache: 'no-store' });
  const man = await res.json();
  const name = PREFIX + man.version;
  if (!force && (await caches.has(name))) { await broadcast({ type: 'offline-done', version: man.version, files: man.files.length, fresh: false }); return; }
  const cache = await caches.open(name);
  const texts = [];
  let done = 0, failed = 0;
  const queue = man.files.slice();
  async function worker() {
    while (queue.length) {
      const path = queue.shift();
      const url = new URL(path, ROOT).href;
      try {
        const r = await fetch(url, { cache: 'no-cache' });
        if (!r.ok) throw new Error(r.status);
        if (/\.(html|css)$|\/$/.test(path)) texts.push(await r.clone().text());
        await cache.put(url, r);
      } catch (e) { failed++; }
      done++;
      if (done % 5 === 0 || done === man.files.length) broadcast({ type: 'offline-progress', done, total: man.files.length });
    }
  }
  await Promise.all([worker(), worker(), worker(), worker()]);
  await cacheFonts(texts);
  for (const k of await caches.keys()) if (k.startsWith(PREFIX) && k !== name && k !== FONT_CACHE) await caches.delete(k);
  await broadcast({ type: 'offline-done', version: man.version, files: man.files.length, failed, fresh: true });
}

async function wipe() {
  for (const k of await caches.keys()) if (k.startsWith(PREFIX)) await caches.delete(k);
  await broadcast({ type: 'offline-wiped' });
}

self.addEventListener('message', (e) => {
  const t = e.data && e.data.type;
  if (t === 'offline-download') e.waitUntil(download(!!e.data.force).catch((err) => broadcast({ type: 'offline-error', message: String(err) })));
  if (t === 'offline-check') e.waitUntil(download(false).catch(() => {}));
  if (t === 'offline-wipe') e.waitUntil(wipe());
});

function timeout(ms) { return new Promise((_, rej) => setTimeout(() => rej(new Error('timeout')), ms)); }

async function fromCache(req) {
  const cache = await currentCache();
  if (!cache) return null;
  let hit = await cache.match(req, { ignoreSearch: true });
  if (!hit && req.mode === 'navigate') {
    const u = new URL(req.url);
    if (u.pathname.endsWith('/')) hit = await cache.match(u.origin + u.pathname + 'index.html', { ignoreSearch: true });
    if (!hit) hit = await cache.match(new URL('index.html', ROOT).href);
  }
  return hit || null;
}

self.addEventListener('fetch', (e) => {
  const req = e.request;
  if (req.method !== 'GET') return;
  const url = new URL(req.url);
  if (url.hostname === 'fonts.googleapis.com' || url.hostname === 'fonts.gstatic.com') {
    e.respondWith((async () => {
      const fonts = await caches.open(FONT_CACHE);
      const hit = await fonts.match(req.url);
      if (hit) return hit;
      const r = await fetch(req);
      if (r.ok && (await currentCache())) fonts.put(req.url, r.clone());
      return r;
    })());
    return;
  }
  if (!req.url.startsWith(ROOT) || url.pathname.endsWith('/sw.js') || url.pathname.endsWith('offline-manifest.json')) return;
  if (req.mode === 'navigate') {
    // Network first (so updates show up), cached copy when offline or slow.
    e.respondWith((async () => {
      try { return await Promise.race([fetch(req), timeout(NAV_TIMEOUT)]); }
      catch (err) { return (await fromCache(req)) || new Response('<h1>Sem conexão</h1><p>Esta página ainda não foi guardada no modo ônibus.</p>', { status: 503, headers: { 'Content-Type': 'text/html; charset=utf-8' } }); }
    })());
    return;
  }
  e.respondWith((async () => (await fromCache(req)) || fetch(req))());
});
