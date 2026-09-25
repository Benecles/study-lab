// Scrollytelling: each .step names the figure panel it needs (data-panel).
// Without JS the first panel of each stage stays visible and the text reads normally.
(function () {
  if (!('IntersectionObserver' in window)) return;
  document.querySelectorAll('.scrolly').forEach(function (block) {
    var panels = block.querySelectorAll('.panel');
    var caption = block.querySelector('.stage-count');
    var steps = Array.prototype.slice.call(block.querySelectorAll('.step'));
    function show(step) {
      steps.forEach(function (s) { s.classList.toggle('on', s === step); });
      var id = step.getAttribute('data-panel');
      panels.forEach(function (p) {
        var on = p.id === id;
        if (on && !p.classList.contains('on')) {
          // restart draw-on strokes each time a panel comes back
          p.querySelectorAll('.grow,.pop,.fade,.pulse').forEach(function (g) { g.style.animation = 'none'; g.getBoundingClientRect(); g.style.animation = ''; });
        }
        p.classList.toggle('on', on);
      });
      if (caption) caption.textContent = step.getAttribute('data-slides') || '';
      var counter = block.querySelector('.stage-step');
      if (counter) counter.textContent = (steps.indexOf(step) + 1) + ' / ' + steps.length;
    }
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) { if (e.isIntersecting) show(e.target); });
    }, { rootMargin: '-45% 0px -45% 0px' });
    steps.forEach(function (s) { io.observe(s); });
  });
})();

// Reading progress hairline + remember the last lesson opened (per-viewer convenience only).
(function () {
  var m = location.pathname.match(/aula-(\d\d)\.html$/);
  if (!m) return;
  var bar = document.createElement('div');
  bar.className = 'read-progress';
  bar.setAttribute('aria-hidden', 'true');
  document.body.appendChild(bar);
  function upd() {
    var h = document.documentElement.scrollHeight - innerHeight;
    bar.style.transform = 'scaleX(' + (h > 0 ? Math.min(1, scrollY / h) : 0) + ')';
  }
  addEventListener('scroll', upd, { passive: true });
  addEventListener('resize', upd);
  upd();
  try {
    var t = document.title.split(' · ')[0];
    localStorage.setItem('cufrgs-contratos-last', JSON.stringify({ n: m[1], t: t }));
  } catch (e) {}
})();

// Printing: light theme, every answer open, and each step printed next to its own figure.
(function () {
  var saved = null, opened = [], clones = [];
  addEventListener('beforeprint', function () {
    var r = document.documentElement;
    saved = r.dataset.theme || null; delete r.dataset.theme;
    document.querySelectorAll('details:not([open])').forEach(function (d) { d.open = true; opened.push(d); });
    document.querySelectorAll('.scrolly .step').forEach(function (s) {
      var p = document.getElementById(s.getAttribute('data-panel'));
      var card = s.querySelector('.card');
      if (!p || !card) return;
      var c = p.cloneNode(true);
      c.removeAttribute('id'); c.classList.remove('panel', 'on'); c.classList.add('print-fig');
      c.querySelectorAll('[id]').forEach(function (n) { n.id = n.id + '-print'; });
      c.querySelectorAll('[marker-end]').forEach(function (n) { n.setAttribute('marker-end', n.getAttribute('marker-end').replace(/\)$/, '-print)')); });
      card.insertBefore(c, card.firstChild); clones.push(c);
    });
  });
  addEventListener('afterprint', function () {
    if (saved) document.documentElement.dataset.theme = saved;
    opened.forEach(function (d) { d.open = false; }); opened = [];
    clones.forEach(function (c) { c.remove(); }); clones = [];
  });
})();
