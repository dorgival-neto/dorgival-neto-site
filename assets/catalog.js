(function () {
  var DN = (window.DN = window.DN || {});
  var cfg = function () { return window.SITE_CONFIG || {}; };

  DN.esc = function (s) {
    return String(s == null ? '' : s).replace(/[&<>"']/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
    });
  };
  DN.money = function (v) {
    return Number(v || 0).toLocaleString('pt-BR', { style: 'currency', currency: 'BRL', maximumFractionDigits: 0 });
  };
  DN.url = function (p) { return '/imovel/' + p.id + '/'; };
  DN.wa = function (msg) { return 'https://wa.me/' + cfg().whatsapp + '?text=' + encodeURIComponent(msg); };
  DN.bookUrl = function (p) {
    return DN.wa('Olá Dorgival! Quero ver o book/tabela do imóvel ' + p.codigo + ' — ' + p.titulo + ' (' + p.bairro + ').');
  };
  DN.price = function (p) {
    var pre = p.investimento && p.investimento.aPartirDe ? 'a partir de ' : '';
    return pre + DN.money(p.preco) + (p.tipo === 'Aluguel' ? '/mês' : '');
  };
  DN.trilhaLabel = { investir: 'Para investir', morar: 'Para morar' };

  DN.track = function (name, params) {
    try {
      if (window.gtag) window.gtag('event', name, params || {});
      if (window.fbq) window.fbq('trackCustom', name, params || {});
    } catch (e) {}
  };

  DN.favs = function () {
    try { return JSON.parse(localStorage.getItem('dn_favs') || '[]'); } catch (e) { return []; }
  };
  DN.isFav = function (id) { return DN.favs().indexOf(id) !== -1; };
  DN.toggleFav = function (id) {
    var f = DN.favs();
    var i = f.indexOf(id);
    if (i === -1) f.push(id); else f.splice(i, 1);
    try { localStorage.setItem('dn_favs', JSON.stringify(f)); } catch (e) {}
    DN.track(i === -1 ? 'add_to_wishlist' : 'remove_from_wishlist', { item_id: id });
    return i === -1;
  };

  DN.toast = function (msg) {
    var t = document.getElementById('dnToast');
    if (!t) {
      t = document.createElement('div');
      t.id = 'dnToast';
      t.className = 'dn-toast';
      document.body.appendChild(t);
    }
    t.textContent = msg;
    t.classList.add('show');
    clearTimeout(DN._toastT);
    DN._toastT = setTimeout(function () { t.classList.remove('show'); }, 2200);
  };

  DN.share = function (p) {
    var url = location.origin + DN.url(p);
    var data = { title: p.titulo, text: p.titulo + ' — ' + DN.price(p) + ' (' + p.codigo + ')', url: url };
    DN.track('share', { item_id: p.id, method: 'button' });
    if (navigator.share) {
      return navigator.share(data).catch(function () {});
    }
    if (navigator.clipboard && navigator.clipboard.writeText) {
      return navigator.clipboard.writeText(url).then(function () { DN.toast('Link copiado!'); }, function () { window.prompt('Copie o link:', url); });
    }
    window.prompt('Copie o link:', url);
  };

  function investChips(p) {
    var inv = p.investimento || {};
    var c = [];
    if (inv.entrega) c.push('Entrega: ' + inv.entrega);
    if (inv.entrada) c.push('Entrada: ' + inv.entrada);
    if (inv.parcela) c.push('Parcelas: ' + inv.parcela);
    if (inv.posicao) c.push('Posição: ' + inv.posicao);
    if (inv.pagamento) c.push(inv.pagamento);
    return c;
  }
  DN.investChips = investChips;

  DN.cardHTML = function (p, opts) {
    opts = opts || {};
    var foto = (p.fotos && p.fotos[0]) || '';
    var chips = investChips(p).map(function (c) { return '<span class="card-chip">' + DN.esc(c) + '</span>'; }).join('');
    var tr = (p.trilhas || []).map(function (t) { return '<span class="card-track">' + DN.trilhaLabel[t] + '</span>'; }).join('');
    var fav = DN.isFav(p.id) ? ' on' : '';
    return '<article class="card" data-id="' + p.id + '">' +
      '<a class="card-photo" href="' + DN.url(p) + '">' +
      '<img src="/' + foto + '" alt="' + DN.esc(p.titulo) + '" loading="lazy">' +
      '<span class="card-badge ' + (p.tipo === 'Aluguel' ? 'aluguel' : '') + '">' + DN.esc(p.status) + '</span>' +
      '<span class="card-code">' + DN.esc(p.codigo) + '</span>' +
      '</a>' +
      '<button type="button" class="card-fav' + fav + '" data-fav="' + p.id + '" aria-label="Favoritar ' + DN.esc(p.titulo) + '">&#9829;</button>' +
      '<div class="card-body">' +
      (tr ? '<div class="card-tracks">' + tr + '</div>' : '') +
      '<div class="card-price">' + DN.esc(DN.price(p)) + '</div>' +
      '<a class="card-title" href="' + DN.url(p) + '">' + DN.esc(p.titulo) + '</a>' +
      '<div class="card-loc">' + DN.esc(p.bairro) + ' · ' + DN.esc(p.cidade) + '</div>' +
      '<div class="card-specs"><span>🛏 ' + (p.quartos || 0) + '</span><span>🚿 ' + (p.banheiros || 0) + '</span>' +
      (p.vagas ? '<span>🚗 ' + p.vagas + '</span>' : '') + '<span>📐 ' + (p.areaUtil || 0) + 'm²</span></div>' +
      (chips ? '<div class="card-chips">' + chips + '</div>' : '') +
      '<div class="card-actions">' +
      '<a class="btn btn-gold btn-sm" data-book="' + p.id + '" href="' + DN.bookUrl(p) + '" target="_blank" rel="noopener">Quero ver book/tabela</a>' +
      '<a class="btn btn-outline btn-sm" href="' + DN.url(p) + '">Ver detalhes</a>' +
      '</div>' +
      (opts.compare ? '<label class="card-compare"><input type="checkbox" data-compare="' + p.id + '"> Comparar</label>' : '') +
      '</div></article>';
  };

  DN.teaserHTML = function (p) {
    var foto = (p.fotos && p.fotos[0]) || '';
    return '<div class="cat-card">' +
      '<a class="cat-link" href="' + DN.url(p) + '" aria-label="' + DN.esc(p.titulo) + '"></a>' +
      '<img src="/' + foto + '" alt="' + DN.esc(p.titulo) + '" loading="lazy">' +
      '<div class="overlay">' +
      '<span class="tag">' + DN.esc(p.status) + ' · ' + DN.esc(p.codigo) + '</span>' +
      '<div class="price">' + DN.esc(DN.price(p)) + '</div>' +
      '<div class="loc">' + DN.esc(p.bairro) + ' · ' + DN.esc(p.cidade) + '</div>' +
      '<a class="cat-book" data-book="' + p.id + '" href="' + DN.bookUrl(p) + '" target="_blank" rel="noopener">Quero ver book/tabela</a>' +
      '</div></div>';
  };

  // cliques globais: favoritar e medir pedidos de book/tabela
  document.addEventListener('click', function (e) {
    var fav = e.target.closest && e.target.closest('[data-fav]');
    if (fav) {
      e.preventDefault();
      var on = DN.toggleFav(fav.getAttribute('data-fav'));
      document.querySelectorAll('[data-fav="' + fav.getAttribute('data-fav') + '"]').forEach(function (b) { b.classList.toggle('on', on); });
      DN.toast(on ? 'Imóvel salvo nos favoritos' : 'Removido dos favoritos');
      if (typeof DN.onFavChange === 'function') DN.onFavChange();
      return;
    }
    var book = e.target.closest && e.target.closest('[data-book]');
    if (book) DN.track('generate_lead', { method: 'book_tabela', item_id: book.getAttribute('data-book') });
  });
})();
