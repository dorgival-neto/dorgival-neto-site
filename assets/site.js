/* Comportamentos comuns a todas as páginas */
(function () {
  // menu do celular: fecha ao tocar em um item (a página rola até a seção) ou fora do menu
  var nav = document.getElementById('navLinks');
  if (!nav) return;
  function close() { nav.classList.remove('open'); }
  nav.addEventListener('click', function (e) {
    if (e.target.closest && e.target.closest('a')) close();
  });
  document.addEventListener('click', function (e) {
    if (!nav.classList.contains('open')) return;
    var t = e.target;
    if (nav.contains(t) || (t.closest && t.closest('.nav-toggle'))) return;
    close();
  });
  window.addEventListener('hashchange', close);
  window.addEventListener('pageshow', close);
})();
