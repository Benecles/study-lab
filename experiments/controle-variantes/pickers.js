
// Theme variants: ?tema=sakura|washi|yugure|himawari|soda. The picker appears only when a theme is requested.
(function () {
  var themes = [
    ['', 'Original', '#b4432a', '#2b5597'],
    ['sakura', 'Sakura', '#e0457f', '#3059b0'],
    ['washi', 'Washi', '#c65a36', '#3f7f6a'],
    ['yugure', 'Yūgure', '#d4555f', '#8c9ae0'],
    ['himawari', 'Himawari', '#ffcc2e', '#12808a'],
    ['soda', 'Soda', '#e2574c', '#7fd4c4']
  ];
  var params = new URLSearchParams(location.search);
  if (!params.has('tema')) return;
  var current = params.get('tema') || '';
  if (current) document.documentElement.setAttribute('data-theme', current);
  var nav = document.createElement('nav');
  nav.className = 'tema-picker';
  nav.setAttribute('aria-label', 'Variantes de estilo');
  themes.forEach(function (t) {
    var a = document.createElement('a');
    a.href = '?tema=' + t[0] + location.hash;
    a.innerHTML = '<i style="--a:' + t[2] + ';--b:' + t[3] + '"></i>' + t[1];
    if (t[0] === current) a.setAttribute('aria-current', 'true');
    a.addEventListener('click', function (e) {
      e.preventDefault();
      if (t[0]) document.documentElement.setAttribute('data-theme', t[0]); else document.documentElement.removeAttribute('data-theme');
      nav.querySelectorAll('a').forEach(function (x) { x.removeAttribute('aria-current'); });
      a.setAttribute('aria-current', 'true');
      history.replaceState(null, '', '?tema=' + t[0] + location.hash);
    });
    nav.appendChild(a);
  });
  document.body.appendChild(nav);
})();

// Background variants for the original look: ?fundo=suave|pontos|margem|foco|prancheta|vegetal
(function () {
  var opts = [['', 'Atual'], ['suave', '1 Suave'], ['pontos', '2 Pontos'], ['margem', '3 Margem'], ['foco', '4 Foco'], ['prancheta', '5 Prancheta'], ['vegetal', '6 Vegetal']];
  var params = new URLSearchParams(location.search);
  if (!params.has('fundo')) return;
  var cur = params.get('fundo') || '';
  function set(v) { if (v) document.documentElement.setAttribute('data-fundo', v); else document.documentElement.removeAttribute('data-fundo'); }
  set(cur);
  var nav = document.createElement('nav');
  nav.className = 'fundo-picker';
  nav.setAttribute('aria-label', 'Variantes de fundo');
  opts.forEach(function (o) {
    var a = document.createElement('a');
    a.href = '?fundo=' + o[0];
    a.textContent = o[1];
    if (o[0] === cur) a.setAttribute('aria-current', 'true');
    a.addEventListener('click', function (e) {
      e.preventDefault(); set(o[0]);
      nav.querySelectorAll('a').forEach(function (x) { x.removeAttribute('aria-current'); });
      a.setAttribute('aria-current', 'true');
      history.replaceState(null, '', '?fundo=' + o[0] + location.hash);
    });
    nav.appendChild(a);
  });
  document.body.appendChild(nav);
})();
