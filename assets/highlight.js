/* CUFRGS · marca-texto: select reading text and mark it in one of five colours.
   Marks are kept in this browser only (localStorage), one list per page. */
(function () {
  if (!window.getSelection || !document.createTreeWalker || !Element.prototype.closest) return;
  var KEY = 'cufrgs-hl:' + location.pathname.replace(/index\.html$/, '');
  // Only running text can be marked; interface, figures and controls cannot.
  var BLOCK = 'p,li,td,th,blockquote,figcaption,dd,dt,h2,h3,h4';
  var SKIP = 'nav,button,select,input,textarea,summary,svg,script,style,label,[contenteditable],' +
    '.topbar,.label,.kicker,.titleblock,.endnav,.course-nav,.stage,.deck-wrap,.deck-tools,.art-tools,.art-key,' +
    '.heading-anchor,.chapter-nav,.chapter-pagination,.skip-link,.site-return,.num,.tag,.cu-pop,.cu-hlbar';
  var COLORS = [['1', 'amarelo'], ['2', 'verde'], ['3', 'azul'], ['4', 'rosa'], ['5', 'lilás']];

  var css = document.createElement('style');
  css.textContent =
    '.cu-hl[data-c="1"],.cu-hlbar [data-c="1"]{--hl:#f4d35e}.cu-hl[data-c="2"],.cu-hlbar [data-c="2"]{--hl:#bcd98a}' +
    '.cu-hl[data-c="3"],.cu-hlbar [data-c="3"]{--hl:#a9c7ea}.cu-hl[data-c="4"],.cu-hlbar [data-c="4"]{--hl:#f0b2a4}' +
    '.cu-hl[data-c="5"],.cu-hlbar [data-c="5"]{--hl:#d3bde8}' +
    ':root[data-theme="dark"] .cu-hl[data-c="1"],:root[data-theme="dark"] .cu-hlbar [data-c="1"]{--hl:rgba(240,196,72,.40)}' +
    ':root[data-theme="dark"] .cu-hl[data-c="2"],:root[data-theme="dark"] .cu-hlbar [data-c="2"]{--hl:rgba(142,192,102,.32)}' +
    ':root[data-theme="dark"] .cu-hl[data-c="3"],:root[data-theme="dark"] .cu-hlbar [data-c="3"]{--hl:rgba(112,166,226,.36)}' +
    ':root[data-theme="dark"] .cu-hl[data-c="4"],:root[data-theme="dark"] .cu-hlbar [data-c="4"]{--hl:rgba(226,126,106,.36)}' +
    ':root[data-theme="dark"] .cu-hl[data-c="5"],:root[data-theme="dark"] .cu-hlbar [data-c="5"]{--hl:rgba(176,136,222,.40)}' +
    // a marker stroke: centred on the letters, chisel-cut ends, ink multiplies into the paper
    'mark.cu-hl{color:inherit;background-color:transparent;cursor:pointer;background-repeat:no-repeat;background-size:100% 60%;background-position:0 50%;' +
    'background-image:linear-gradient(var(--hl),var(--hl));-webkit-box-decoration-break:clone;box-decoration-break:clone;mix-blend-mode:multiply;' +
    '-webkit-print-color-adjust:exact;print-color-adjust:exact}' +
    ':root[data-theme="dark"] mark.cu-hl{mix-blend-mode:normal}' +
    'mark.cu-hl.hl-a{padding-left:.16em;margin-left:-.16em;background-image:linear-gradient(104deg,transparent .1em,var(--hl) .3em)}' +
    'mark.cu-hl.hl-z{padding-right:.16em;margin-right:-.16em;background-image:linear-gradient(104deg,var(--hl) calc(100% - .3em),transparent calc(100% - .1em))}' +
    'mark.cu-hl.hl-a.hl-z{background-image:linear-gradient(104deg,transparent .1em,var(--hl) .3em,var(--hl) calc(100% - .3em),transparent calc(100% - .1em))}' +
    'mark.cu-hl.hl-new{animation:cu-hl-in .5s cubic-bezier(.3,.7,.3,1) both}' +
    '@keyframes cu-hl-in{from{background-size:0 60%}to{background-size:100% 60%}}' +
    '.cu-hlbar{position:absolute;z-index:90;display:flex;align-items:center;gap:2px;padding:4px;background:var(--paper,#f2eee3);color:var(--ink,#1d2530);' +
    'border:1.5px solid var(--ink,#1d2530);box-shadow:3px 3px 0 var(--grid-major,#c9c1aa);animation:cu-hlbar-in .14s ease-out}' +
    '.cu-hlbar[hidden]{display:none}' +
    '@keyframes cu-hlbar-in{from{opacity:0;transform:translateY(3px)}}' +
    '.cu-hlbar button{width:30px;height:28px;padding:0;border:0;background:none;color:inherit;cursor:pointer;display:grid;place-items:center}' +
    '.cu-hlbar .sw i{display:block;width:19px;height:11px;background:var(--hl);transform:skewX(-14deg);border-radius:1px 3px 1px 3px;transition:transform .12s}' +
    ':root:not([data-theme="dark"]) .cu-hlbar .sw i{box-shadow:inset 0 0 0 1px rgba(29,37,48,.12)}' +
    '.cu-hlbar .sw:hover i,.cu-hlbar .sw:focus-visible i{transform:skewX(-14deg) scale(1.18)}' +
    '.cu-hlbar .sw[aria-pressed="true"] i{outline:1.5px solid currentColor;outline-offset:3px}' +
    '.cu-hlbar .rm{border-left:1px solid var(--grid-major,#c9c1aa);margin-left:2px;width:32px;color:var(--ink-2,#4a4f55)}' +
    '.cu-hlbar .rm:hover{color:var(--conc,#b4432a)}.cu-hlbar .rm[hidden]{display:none}' +
    '.cu-hlbar button:focus-visible{outline:2px solid var(--dif,#2b5597);outline-offset:-2px}' +
    '@media (prefers-reduced-motion:reduce){mark.cu-hl.hl-new,.cu-hlbar{animation:none}}' +
    '@media print{.cu-hlbar{display:none!important}}';
  document.head.appendChild(css);

  var ok = new WeakMap();
  function allowed(el) {
    if (!el) return false;
    if (ok.has(el)) return ok.get(el);
    var v = !!el.closest(BLOCK) && !el.closest(SKIP);
    ok.set(el, v); return v;
  }
  // Every markable text node in reading order, with its offset in the page's markable text.
  function index() {
    var w = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT, {
      acceptNode: function (n) { return n.nodeValue && allowed(n.parentElement) ? 1 : 3; }
    });
    var arr = [], pos = 0, parts = [], n;
    while ((n = w.nextNode())) { arr.push({ n: n, s: pos }); parts.push(n.nodeValue); pos += n.nodeValue.length; }
    return { arr: arr, text: parts.join('') };
  }
  function rangeOffsets(r) {
    var ix = index(), s = -1, e = -1;
    ix.arr.forEach(function (x) {
      if (!r.intersectsNode(x.n)) return;
      var a = x.n === r.startContainer ? r.startOffset : 0;
      var b = x.n === r.endContainer ? r.endOffset : x.n.nodeValue.length;
      if (a >= b) return;
      if (s < 0) s = x.s + a;
      e = x.s + b;
    });
    if (s < 0) return null;
    while (s < e && /\s/.test(ix.text[s])) s++;
    while (e > s && /\s/.test(ix.text[e - 1])) e--;
    return e > s ? { s: s, e: e, text: ix.text } : null;
  }

  function paint(h, fresh) {
    var marks = [];
    index().arr.forEach(function (x) {
      var len = x.n.nodeValue.length, a = Math.max(h.s, x.s) - x.s, b = Math.min(h.e, x.s + len) - x.s;
      if (a >= b) return;
      var n = x.n;
      if (b < len) n.splitText(b);
      if (a > 0) n = n.splitText(a);
      var m = document.createElement('mark');
      m.className = 'cu-hl'; m.setAttribute('data-c', h.c); m.setAttribute('data-h', h.id);
      n.parentNode.insertBefore(m, n); m.appendChild(n); marks.push(m);
    });
    marks.forEach(function (m, i) {
      var blk = m.parentElement.closest(BLOCK);
      if (!marks[i - 1] || marks[i - 1].parentElement.closest(BLOCK) !== blk) m.classList.add('hl-a');
      if (!marks[i + 1] || marks[i + 1].parentElement.closest(BLOCK) !== blk) m.classList.add('hl-z');
      if (fresh) m.classList.add('hl-new');
    });
  }
  function unpaint(id) {
    [].forEach.call(document.querySelectorAll('mark.cu-hl[data-h="' + id + '"]'), function (m) {
      var p = m.parentNode;
      while (m.firstChild) p.insertBefore(m.firstChild, m);
      p.removeChild(m); p.normalize();
    });
  }

  var hl = [];
  function save() {
    try { hl.length ? localStorage.setItem(KEY, JSON.stringify(hl)) : localStorage.removeItem(KEY); } catch (e) {}
  }
  function restore() {
    var saved = [];
    try { saved = JSON.parse(localStorage.getItem(KEY)) || []; } catch (e) {}
    if (!saved.length) return;
    var text = index().text;
    saved.forEach(function (h) {
      // if the page changed since, find the same passage again or drop the mark
      if (text.slice(h.s, h.e) !== h.q) { var i = text.indexOf(h.q); if (i < 0) return; h.s = i; h.e = i + h.q.length; }
      if (hl.some(function (o) { return o.s < h.e && h.s < o.e; })) return;
      hl.push(h);
    });
    hl.sort(function (a, b) { return a.s - b.s; }).forEach(function (h) { paint(h, false); });
    save();
  }

  var bar = document.createElement('div');
  bar.className = 'cu-hlbar'; bar.hidden = true;
  bar.setAttribute('role', 'toolbar'); bar.setAttribute('aria-label', 'Marca-texto');
  bar.innerHTML = COLORS.map(function (c) {
    return '<button type="button" class="sw" data-c="' + c[0] + '" aria-label="Marcar em ' + c[1] + '" title="' + c[1] + '"><i></i></button>';
  }).join('') + '<button type="button" class="rm" aria-label="Remover marcação" title="Remover"><svg width="14" height="14" viewBox="0 0 14 14" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" aria-hidden="true"><path d="M3 3l8 8M11 3l-8 8"/></svg></button>';
  document.body.appendChild(bar);
  var rm = bar.querySelector('.rm'), pending = null;

  function place(rects, below) {
    bar.hidden = false;
    var bw = bar.offsetWidth, bh = bar.offsetHeight;
    var r = below ? rects[rects.length - 1] : rects[0];
    var x = Math.max(8, Math.min(r.left + r.width / 2 - bw / 2, document.documentElement.clientWidth - bw - 8));
    var y = below ? r.bottom + 12 : r.top - bh - 10;
    if (!below && y < 8) y = rects[rects.length - 1].bottom + 10;
    bar.style.left = (x + window.pageXOffset) + 'px';
    bar.style.top = (y + window.pageYOffset) + 'px';
  }
  function hide() { bar.hidden = true; pending = null; }
  function sync(c) {
    [].forEach.call(bar.querySelectorAll('.sw'), function (b) { b.setAttribute('aria-pressed', String(b.getAttribute('data-c') === c)); });
  }
  var coarse = window.matchMedia && matchMedia('(pointer:coarse)').matches;

  function fromSelection() {
    var sel = getSelection();
    if (!sel.rangeCount || sel.isCollapsed) { if (pending && pending.s != null) hide(); return; }
    var r = sel.getRangeAt(0), off = rangeOffsets(r);
    if (!off) { hide(); return; }
    var rects = [].filter.call(r.getClientRects(), function (q) { return q.width > 0; });
    if (!rects.length) return;
    pending = off; rm.hidden = true; sync(null);
    place(rects, coarse); // on touch screens the system menu sits above the selection
  }
  var t;
  document.addEventListener('selectionchange', function () { clearTimeout(t); t = setTimeout(fromSelection, coarse ? 350 : 180); });
  document.addEventListener('mouseup', function (e) { if (!bar.contains(e.target)) { clearTimeout(t); t = setTimeout(fromSelection, 10); } });

  document.addEventListener('click', function (e) {
    var m = e.target.closest && e.target.closest('mark.cu-hl');
    if (!m || e.target.closest('a') || !getSelection().isCollapsed) return;
    var id = m.getAttribute('data-h'), rects = [];
    [].forEach.call(document.querySelectorAll('mark.cu-hl[data-h="' + id + '"]'), function (x) { rects.push.apply(rects, [].slice.call(x.getClientRects())); });
    pending = { id: id }; rm.hidden = false; sync(m.getAttribute('data-c'));
    place(rects, false);
  });
  document.addEventListener('mousedown', function (e) { if (!bar.hidden && !bar.contains(e.target) && !(e.target.closest && e.target.closest('mark.cu-hl'))) hide(); });
  document.addEventListener('keydown', function (e) { if (e.key === 'Escape' && !bar.hidden) hide(); });
  window.addEventListener('resize', hide);
  bar.addEventListener('mousedown', function (e) { e.preventDefault(); }); // keep the text selected

  bar.addEventListener('click', function (e) {
    var b = e.target.closest('button'); if (!b || !pending) return;
    var p = pending;
    if (b === rm) {
      unpaint(p.id); hl = hl.filter(function (h) { return h.id !== p.id; });
    } else if (p.id) {
      var c = b.getAttribute('data-c');
      hl.forEach(function (h) { if (h.id === p.id) h.c = c; });
      [].forEach.call(document.querySelectorAll('mark.cu-hl[data-h="' + p.id + '"]'), function (m) { m.setAttribute('data-c', c); });
    } else {
      // marking over existing marks merges them into the new stroke
      var s = p.s, en = p.e;
      hl = hl.filter(function (h) {
        if (h.s < en && s < h.e) { s = Math.min(s, h.s); en = Math.max(en, h.e); unpaint(h.id); return false; }
        return true;
      });
      var h = { id: Date.now().toString(36) + Math.random().toString(36).slice(2, 6), s: s, e: en, c: b.getAttribute('data-c'), q: index().text.slice(s, en) };
      hl.push(h); paint(h, true);
      var sel = getSelection(); if (sel.removeAllRanges) sel.removeAllRanges();
    }
    save(); hide();
  });

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', restore); else restore();
})();
