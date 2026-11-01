(function () {
  var DN = (window.DN = window.DN || {});
  var cfg = function () { return window.SITE_CONFIG || {}; };

  DN.esc = function (s) {
    return String(s == null ? '' : s).replace(/[&<>"']/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
    });
  };
  // idioma da página (<html lang>): pt (padrão), en ou es — usado nas páginas /en/ e /es/
  var LANG = (document.documentElement.lang || 'pt').slice(0, 2).toLowerCase();
  if (LANG !== 'en' && LANG !== 'es') LANG = 'pt';
  DN.lang = LANG;
  var LOCALE = { pt: 'pt-BR', en: 'en-US', es: 'es-CL' }[LANG];
  var TXT = {
    pt: { from: 'a partir de ', month: '/mês', book: 'Agendar apresentação', hi: 'Olá Dorgival! Tenho interesse no imóvel ',
          ask: ', e gostaria de agendar uma apresentação do empreendimento e receber informações sobre os valores de investimento', saw: '. Vi no seu site: ', excl: 'Exclusividade' },
    en: { from: 'from ', month: '/month', book: 'Schedule a presentation', hi: "Hello Dorgival! I'm interested in property ",
          ask: ', and I would like to schedule a presentation of the development and receive information about investment values', saw: '. I saw it on your website: ', excl: 'Exclusive' },
    es: { from: 'desde ', month: '/mes', book: 'Agendar una presentación', hi: '¡Hola Dorgival! Me interesa el inmueble ',
          ask: ', y me gustaría agendar una presentación del emprendimiento y recibir información sobre los valores de inversión', saw: '. Lo vi en tu sitio web: ', excl: 'Exclusividad' }
  }[LANG];
  var STATUS = {
    en: { 'Lançamento': 'Launch', 'Na planta': 'Off-plan', 'Em construção': 'Under construction', 'Pronto para morar': 'Ready to move in', 'Porteira fechada': 'Turnkey' },
    es: { 'Lançamento': 'Lanzamiento', 'Na planta': 'En planos', 'Em construção': 'En construcción', 'Pronto para morar': 'Listo para habitar', 'Porteira fechada': 'Llave en mano' }
  }[LANG] || {};
  DN.title = function (p) { return p['titulo_' + LANG] || p.titulo; };
  DN.statusLabel = function (p) { return STATUS[p.status] || p.status; };
  DN.money = function (v) {
    var n = Number(v || 0);
    if (LANG === 'pt') return n.toLocaleString(LOCALE, { style: 'currency', currency: 'BRL', maximumFractionDigits: 0 });
    return 'R$ ' + n.toLocaleString(LOCALE, { maximumFractionDigits: 0 });
  };
  DN.url = function (p) { return '/imovel/' + p.codigo + '/'; };
  DN.wa = function (msg) { return 'https://wa.me/' + cfg().whatsapp + '?text=' + encodeURIComponent(msg); };
  DN.price = function (p) {
    var pre = p.investimento && p.investimento.aPartirDe ? TXT.from : '';
    return pre + DN.money(p.preco) + (p.tipo === 'Aluguel' ? TXT.month : '');
  };
  // só lançamento / na planta / em construção tem book e tabela de vendas
  DN.hasBook = function (p) { return ['Lançamento', 'Na planta', 'Em construção'].indexOf(p.status) !== -1; };
  // mensagem de WhatsApp com código, dados e link direto do imóvel (igual a wa_imovel em build_pages.py)
  DN.waImovel = function (p) {
    var site = cfg().siteUrl || location.origin;
    return DN.wa(TXT.hi + p.codigo + ' (' + DN.title(p) + '), ' + DN.price(p) +
      (DN.hasBook(p) ? TXT.ask : '') + TXT.saw + site + DN.url(p));
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
    var tr = (p.exclusivo ? '<span class="card-track excl">' + TXT.excl + '</span>' : '') +
      (p.trilhas || []).map(function (t) { return '<span class="card-track">' + DN.trilhaLabel[t] + '</span>'; }).join('');
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
      '<div class="card-specs">' + (p.quartos ? '<span>🛏 ' + p.quartos + '</span>' : '') + '<span>🚿 ' + (p.banheiros || 0) + '</span>' +
      (p.vagas ? '<span>🚗 ' + p.vagas + '</span>' : '') + '<span>📐 ' + (p.areaUtil || 0) + 'm²</span></div>' +
      (chips ? '<div class="card-chips">' + chips + '</div>' : '') +
      '<div class="card-actions">' +
      (DN.hasBook(p)
        ? '<a class="btn btn-gold btn-sm" data-book="' + p.id + '" href="' + DN.waImovel(p) + '" target="_blank" rel="noopener">Agendar apresentação</a>' +
          '<a class="btn btn-outline btn-sm" href="' + DN.url(p) + '">Ver detalhes</a>'
        : '<a class="btn btn-gold btn-sm" href="' + DN.url(p) + '">Ver detalhes</a>') +
      '</div>' +
      (opts.compare ? '<label class="card-compare"><input type="checkbox" data-compare="' + p.id + '"> Comparar</label>' : '') +
      '</div></article>';
  };

  DN.teaserHTML = function (p) {
    var foto = (p.fotos && p.fotos[0]) || '';
    return '<div class="cat-card">' +
      '<a class="cat-link" href="' + DN.url(p) + '" aria-label="' + DN.esc(DN.title(p)) + '"></a>' +
      '<img src="/' + foto + '" alt="' + DN.esc(DN.title(p)) + '" loading="lazy">' +
      '<div class="overlay">' +
      '<span class="tag">' + DN.esc(DN.statusLabel(p)) + ' · ' + DN.esc(p.codigo) + '</span>' +
      '<div class="price">' + DN.esc(DN.price(p)) + '</div>' +
      '<div class="loc">' + DN.esc(p.bairro) + ' · ' + DN.esc(p.cidade) + '</div>' +
      (DN.hasBook(p) ? '<a class="cat-book" data-book="' + p.id + '" href="' + DN.waImovel(p) + '" target="_blank" rel="noopener">' + TXT.book + '</a>' : '') +
      '</div></div>';
  };

  // cliques globais: favoritar e medir pedidos de apresentação
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
    if (book) DN.track('generate_lead', { method: 'agendar_apresentacao', item_id: book.getAttribute('data-book') });
  });
})();
