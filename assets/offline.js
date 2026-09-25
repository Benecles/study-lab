/* CUFRGS · modo ônibus: a discreet corner button that saves the whole site
   on this device (via sw.js) so it can be read without a connection. */
(function () {
  if (!('serviceWorker' in navigator) || !('caches' in window)) return;
  var KEY = 'cufrgs-offline';
  var root = new URL('..', document.currentScript.src).href; // site root
  function get() { try { return localStorage.getItem(KEY); } catch (e) { return null; } }
  function set(v) { try { v ? localStorage.setItem(KEY, v) : localStorage.removeItem(KEY); } catch (e) {} }

  var css = document.createElement('style');
  css.textContent =
    '.cu-bus{position:fixed;left:10px;bottom:10px;z-index:80;width:30px;height:30px;border-radius:50%;border:1px solid currentColor;' +
    'background:var(--paper,#f2eee3);color:var(--ink-2,#4a4f55);opacity:.28;cursor:pointer;display:grid;place-items:center;padding:0;transition:opacity .2s}' +
    '.cu-bus:hover,.cu-bus:focus-visible,.cu-bus[aria-expanded="true"]{opacity:1}' +
    '.cu-bus.on{opacity:.6;color:var(--dif,#2b5597)}' +
    '.cu-bus svg{width:16px;height:16px}' +
    '.cu-pop{position:fixed;left:10px;bottom:48px;z-index:81;width:min(300px,calc(100vw - 20px));background:var(--paper,#f2eee3);color:var(--ink,#1d2530);' +
    'border:1.5px solid var(--ink,#1d2530);box-shadow:4px 4px 0 var(--grid-major,#c9c1aa);padding:14px 14px 12px;font:14px/1.45 Georgia,serif}' +
    '.cu-pop[hidden]{display:none}' +
    '.cu-pop b.t{display:block;font:700 15px Helvetica,Arial,sans-serif;margin-bottom:4px}' +
    '.cu-pop p{margin:0 0 10px}' +
    '.cu-pop .row{display:flex;gap:8px;flex-wrap:wrap}' +
    '.cu-pop button{font:600 13px Helvetica,Arial,sans-serif;padding:7px 10px;border:1.5px solid var(--ink,#1d2530);background:var(--paper,#f2eee3);color:var(--ink,#1d2530);cursor:pointer}' +
    '.cu-pop button.go{background:var(--ink,#1d2530);color:var(--paper,#f2eee3)}' +
    '.cu-pop .bar{height:4px;background:var(--grid,#d8d2c0);margin:6px 0 8px}.cu-pop .bar i{display:block;height:100%;width:0;background:var(--conc,#b4432a);transition:width .2s}' +
    '.cu-pop small{display:block;color:var(--muted,#7a7566);font:11px/1.4 Menlo,monospace;margin-top:6px}' +
    '@media print{.cu-bus,.cu-pop{display:none!important}}';
  document.head.appendChild(css);

  var btn = document.createElement('button');
  btn.className = 'cu-bus'; btn.type = 'button';
  btn.setAttribute('aria-label', 'Modo ônibus: ler o site sem internet');
  btn.setAttribute('aria-expanded', 'false');
  btn.title = 'Modo ônibus';
  btn.innerHTML = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" aria-hidden="true"><rect x="4" y="3" width="16" height="15" rx="3"/><path d="M4 11h16M8 18v3M16 18v3"/><circle cx="8" cy="14.5" r="1"/><circle cx="16" cy="14.5" r="1"/></svg>';
  var pop = document.createElement('div');
  pop.className = 'cu-pop'; pop.hidden = true; pop.setAttribute('role', 'dialog'); pop.setAttribute('aria-label', 'Modo ônibus');
  document.body.appendChild(btn); document.body.appendChild(pop);

  function view(state, extra) {
    extra = extra || {};
    btn.classList.toggle('on', get() === 'on');
    if (state === 'off') pop.innerHTML = '<b class="t">Modo ônibus</b><p>Guarda o site inteiro neste aparelho (cerca de 8 MB) para você ler sem internet: numa viagem, no metrô, sem sinal. Os links continuam funcionando.</p><div class="row"><button class="go" data-a="on">Ativar</button><button data-a="close">Agora não</button></div>';
    if (state === 'busy') pop.innerHTML = '<b class="t">Guardando o site…</b><div class="bar"><i style="width:' + (extra.pct || 0) + '%"></i></div><p>' + (extra.done || 0) + ' de ' + (extra.total || '…') + ' arquivos. Pode continuar lendo.</p>';
    if (state === 'on') pop.innerHTML = '<b class="t">Modo ônibus ativo</b><p>O site está guardado neste navegador e abre mesmo sem internet. Com conexão, as páginas continuam se atualizando.</p><div class="row"><button data-a="refresh">Atualizar cópia</button><button data-a="off">Desativar</button><button data-a="close">Fechar</button></div>' + (extra.note ? '<small>' + extra.note + '</small>' : '');
    if (state === 'error') pop.innerHTML = '<b class="t">Não deu para guardar</b><p>Precisa de conexão para baixar a cópia. Tente de novo com internet.</p><div class="row"><button class="go" data-a="on">Tentar de novo</button><button data-a="close">Fechar</button></div>';
  }
  function open(v) { pop.hidden = !v; btn.setAttribute('aria-expanded', String(!!v)); }

  function withWorker(cb) {
    navigator.serviceWorker.register(root + 'sw.js', { scope: root }).then(function () {
      return navigator.serviceWorker.ready;
    }).then(function (reg) { cb(reg.active); }).catch(function () { view('error'); open(true); });
  }
  navigator.serviceWorker.addEventListener('message', function (e) {
    var d = e.data || {};
    if (d.type === 'offline-progress') view('busy', { done: d.done, total: d.total, pct: Math.round(100 * d.done / d.total) });
    if (d.type === 'offline-done') { set('on'); view('on', { note: d.files + ' arquivos guardados' + (d.failed ? ', ' + d.failed + ' falharam' : '') + '.' }); }
    if (d.type === 'offline-error') view('error');
  });

  pop.addEventListener('click', function (e) {
    var a = e.target.getAttribute && e.target.getAttribute('data-a');
    if (!a) return;
    if (a === 'close') open(false);
    if (a === 'on' || a === 'refresh') {
      if (!navigator.onLine) { view('error'); return; }
      view('busy', {});
      withWorker(function (w) { w.postMessage({ type: 'offline-download', force: a === 'refresh' }); });
    }
    if (a === 'off') {
      set(null);
      navigator.serviceWorker.getRegistrations().then(function (rs) {
        rs.forEach(function (r) { if (r.active) r.active.postMessage({ type: 'offline-wipe' }); r.unregister(); });
      });
      caches.keys().then(function (ks) { ks.forEach(function (k) { if (k.indexOf('cufrgs-offline-') === 0) caches.delete(k); }); });
      view('off'); open(false);
    }
  });
  btn.addEventListener('click', function () {
    if (pop.hidden) { view(get() === 'on' ? 'on' : 'off'); open(true); } else open(false);
  });
  document.addEventListener('keydown', function (e) { if (e.key === 'Escape') open(false); });

  if (get() === 'on') {
    btn.classList.add('on');
    // quietly refresh the saved copy when the site has changed
    if (navigator.onLine) withWorker(function (w) { w.postMessage({ type: 'offline-check' }); });
  } else if (navigator.serviceWorker.controller) {
    navigator.serviceWorker.getRegistrations().then(function (rs) { rs.forEach(function (r) { r.unregister(); }); });
  }
})();
