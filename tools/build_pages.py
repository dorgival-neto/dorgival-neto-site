"""Gera as páginas estáticas do site a partir de assets/data.js.

Uso:  python tools/build_pages.py
Gera: imovel/<id>/index.html, bairro/<slug>/index.html, avaliacao.html,
      parceiros.html, mercado/..., sitemap.xml e ajusta nav/rodapé/SEO das
      páginas escritas à mão (index, imoveis, joao-pessoa, depoimento).
"""
import html as H
import json
import os
import re
import unicodedata

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = "https://dorgivalneto.com.br"
NOW_ISO = "2026-10-27"


# ------------------------------------------------------------------ dados
def read(p):
    with open(os.path.join(ROOT, p), encoding="utf-8") as f:
        return f.read()


def write(p, content):
    full = os.path.join(ROOT, p)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w", encoding="utf-8", newline="") as f:
        f.write(content)


def js_array_to_json(src, name):
    i = src.index("const %s = [" % name)
    j = src.index("[", i)
    depth, k, in_str = 0, j, None
    while True:
        c = src[k]
        if in_str:
            if c == "\\":
                k += 2
                continue
            if c == in_str:
                in_str = None
        else:
            if c in "\"'":
                in_str = c
            elif c == "[":
                depth += 1
            elif c == "]":
                depth -= 1
                if depth == 0:
                    break
        k += 1
    arr = src[j:k + 1]
    pat = re.compile(r'("(?:\\.|[^"\\])*")|([A-Za-z_]\w*)(?=\s*:)|(,)(?=\s*[}\]])')

    def sub(m):
        if m.group(1):
            return m.group(1)
        if m.group(2):
            return '"%s"' % m.group(2)
        return ""

    return json.loads(pat.sub(sub, arr))


DATA = read("assets/data.js")
PROPS = js_array_to_json(DATA, "PROPERTIES")
WA = re.search(r'whatsapp:\s*"(\d+)"', DATA).group(1)
INSTAGRAM = re.search(r'instagram:\s*"([^"]+)"', DATA).group(1)

esc = lambda s: H.escape(str(s), quote=True)


def slugify(s):
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


def money(v):
    return "R$ " + f"{v:,.0f}".replace(",", ".")


def num(v):
    s = ("%.2f" % v).rstrip("0").rstrip(".")
    return s.replace(".", ",")


def price_txt(p):
    pre = "a partir de " if (p.get("investimento") or {}).get("aPartirDe") else ""
    return pre + money(p["preco"]) + ("/mês" if p["tipo"] == "Aluguel" else "")


def wa_link(msg):
    from urllib.parse import quote
    return "https://wa.me/%s?text=%s" % (WA, quote(msg, safe=""))


def book_link(p):
    return wa_link("Olá Dorgival! Quero ver o book/tabela do imóvel %s — %s (%s)." % (p["codigo"], p["titulo"], p["bairro"]))


def invest_chips(p):
    inv = p.get("investimento") or {}
    out = []
    if inv.get("entrega"): out.append("Entrega: " + inv["entrega"])
    if inv.get("entrada"): out.append("Entrada: " + inv["entrada"])
    if inv.get("parcela"): out.append("Parcelas: " + inv["parcela"])
    if inv.get("posicao"): out.append("Posição: " + inv["posicao"])
    if inv.get("pagamento"): out.append(inv["pagamento"])
    return out


TRILHA = {"investir": "Para investir", "morar": "Para morar"}

# prefixo do código por tipo de imóvel (código = prefixo + 4 dígitos, ex.: AP0001)
PREFIXOS = {"Apartamento": "AP", "Flat": "FL", "Terreno": "TE", "Casa": "CA", "Sala comercial": "SL", "Cobertura": "CO", "Garden": "GD"}
OLD_CODES = {"DN-BES-001": "AP0001", "DN-BAN-001": "AP0002", "DN-BAN-002": "AP0003"}  # códigos usados até 26/10/2026
for _p in PROPS:
    _pre = PREFIXOS.get(_p.get("categoria"))
    assert _pre and re.fullmatch(_pre + r"\d{4}", _p["codigo"]), "código inválido para %s: %s" % (_p["id"], _p["codigo"])
assert len({_p["codigo"] for _p in PROPS}) == len(PROPS), "código repetido"
BAIRROS = sorted({p["bairro"] for p in PROPS})


# ------------------------------------------------------------------ pedaços comuns
def nav_inner(active=""):
    items = [
        ("/imoveis.html", "Imóveis"),
        ("/avaliacao.html", "Avalie seu imóvel"),
        ("/#servicos", "Serviços"),
        ("/joao-pessoa.html", "João Pessoa"),
        ("/#depoimentos", "Depoimentos"),
        ("/#quemsou", "Quem sou eu"),
        ("/mercado/", "Mercado"),
    ]
    out = []
    for href, label in items:
        st = ' style="color:var(--gold);"' if active and href == active else ""
        out.append('<a href="%s"%s>%s</a>' % (href, st, label))
    out.append('<a class="nav-cta" href="/#contato">Falar comigo</a>')
    return "\n      ".join(out)


def foot_links():
    links = [
        ("/imoveis.html", "Imóveis"),
        ("/avaliacao.html", "Avalie seu imóvel"),
        ("/parceiros.html", "Sou corretor parceiro"),
        ("/mercado/", "Mercado"),
        ("/simulador/", "Simulador de investimento"),
        ("/#guia", "Guia de compra"),
    ] + [("/bairro/%s/" % slugify(b), "Imóveis em %s" % b) for b in BAIRROS] + [("/privacidade.html", "Privacidade")]
    return "".join('<a href="%s">%s</a>' % l for l in links)


def seo_block(title, desc, path, image="/assets/og-image.jpg", noindex=False, og_type="website", jsonld=None):
    url = BASE + path
    img = image if image.startswith("http") else BASE + image
    lines = [
        "<!-- SEO:start -->",
        '<meta name="description" content="%s">' % esc(desc),
        '<link rel="canonical" href="%s">' % url,
    ]
    if noindex:
        lines.append('<meta name="robots" content="noindex, follow">')
    lines += [
        '<meta name="theme-color" content="#141414">',
        '<link rel="icon" href="/favicon.ico" sizes="any">',
        '<link rel="icon" type="image/png" sizes="32x32" href="/assets/favicon-32.png">',
        '<link rel="apple-touch-icon" href="/assets/apple-touch-icon.png">',
        '<meta property="og:type" content="%s">' % og_type,
        '<meta property="og:locale" content="pt_BR">',
        '<meta property="og:site_name" content="Dorgival Neto">',
        '<meta property="og:title" content="%s">' % esc(title),
        '<meta property="og:description" content="%s">' % esc(desc),
        '<meta property="og:url" content="%s">' % url,
        '<meta property="og:image" content="%s">' % img,
    ]
    if image == "/assets/og-image.jpg":
        lines += ['<meta property="og:image:width" content="1200">', '<meta property="og:image:height" content="630">']
    lines.append('<meta name="twitter:card" content="summary_large_image">')
    for j in (jsonld or []):
        lines.append('<script type="application/ld+json">%s</script>' % json.dumps(j, ensure_ascii=False))
    lines.append("<!-- SEO:end -->")
    return "\n".join(lines) + "\n"


FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com">\n<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
         '<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@500;600;700&family=Poppins:wght@400;500;600;700&display=swap" rel="stylesheet">\n'
         '<link rel="stylesheet" href="/assets/styles.css">')
ITI_CSS = '<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/intl-tel-input@18.2.1/build/css/intlTelInput.css">'
ITI_JS = '<script src="https://cdn.jsdelivr.net/npm/intl-tel-input@18.2.1/build/js/intlTelInput.min.js"></script>'
CORE_JS = ('<script src="/assets/data.js"></script>\n<script src="/assets/catalog.js"></script>\n<script src="/assets/analytics.js"></script>')


def page(title, desc, path, body, scripts="", extra_head="", active="", **seo):
    return f"""<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{esc(title)}</title>
{seo_block(title, desc, path, **seo)}{FONTS}
{extra_head}
</head>
<body>

<header class="site-nav">
  <div class="nav-inner">
    <a href="/"><img class="logo" src="/assets/logo-branco.png" alt="Dorgival Neto"></a>
    <nav class="nav-links" id="navLinks">
      {nav_inner(active)}
    </nav>
    <button class="nav-toggle" onclick="document.getElementById('navLinks').classList.toggle('open')">☰</button>
  </div>
</header>

{body}

<a id="fabWa" class="fab-wa" href="{wa_link('Olá Dorgival! Vim pelo site e gostaria de falar com você.')}" target="_blank" rel="noopener">💬 WhatsApp</a>

<footer class="site-footer">
  <div class="wrap" style="text-align:center;">
    <img class="logo" src="/assets/logo-branco.png" alt="Dorgival Neto" style="margin:0 auto 14px;">
    <div class="foot-links"><!--FOOTLINKS-->{foot_links()}<!--/FOOTLINKS--></div>
    <div class="foot-bottom" style="margin-top:0;border-top:none;">CRECI 17191-F · CNAI 52963</div>
  </div>
</footer>

{CORE_JS}
{scripts}
</body>
</html>
"""


# ------------------------------------------------------------------ cards estáticos (bairro / semelhantes)
def card_static(p):
    chips = "".join('<span class="card-chip">%s</span>' % esc(c) for c in invest_chips(p))
    tr = "".join('<span class="card-track">%s</span>' % TRILHA[t] for t in p.get("trilhas", []))
    u = "/imovel/%s/" % p["codigo"]
    specs = '%s<span>🚿 %s</span>%s<span>📐 %sm²</span>' % (
        ('<span>🛏 %s</span>' % p["quartos"]) if p.get("quartos") else "",
        p.get("banheiros", 0), ('<span>🚗 %s</span>' % p["vagas"]) if p.get("vagas") else "", num(p.get("areaUtil", 0)))
    return f"""<article class="card">
  <a class="card-photo" href="{u}"><img src="/{p['fotos'][0]}" alt="{esc(p['titulo'])}" loading="lazy"><span class="card-badge">{esc(p['status'])}</span><span class="card-code">{esc(p['codigo'])}</span></a>
  <div class="card-body">
    {('<div class="card-tracks">' + tr + '</div>') if tr else ''}
    <div class="card-price">{esc(price_txt(p))}</div>
    <a class="card-title" href="{u}">{esc(p['titulo'])}</a>
    <div class="card-loc">{esc(p['bairro'])} · {esc(p['cidade'])}</div>
    <div class="card-specs">{specs}</div>
    {('<div class="card-chips">' + chips + '</div>') if chips else ''}
    <div class="card-actions"><a class="btn btn-gold btn-sm" data-book="{p['id']}" href="{book_link(p)}" target="_blank" rel="noopener">Quero ver book/tabela</a><a class="btn btn-outline btn-sm" href="{u}">Ver detalhes</a></div>
  </div>
</article>"""


# ------------------------------------------------------------------ página do imóvel
def property_page(p):
    path = "/imovel/%s/" % p["codigo"]
    url = BASE + path
    fotos = p["fotos"]
    cover = "/" + fotos[0]
    t_title = "%s — %s | Dorgival Neto" % (p["titulo"], price_txt(p))
    quartos_txt = ("%s quarto(s), " % p["quartos"]) if p.get("quartos") else ""
    desc = "%s em %s, João Pessoa: %s%sm², %s. Código %s. Atendimento de Dorgival Neto, CRECI 17191-F." % (
        p["status"], p["bairro"], quartos_txt, num(p.get("areaUtil", 0)), price_txt(p), p["codigo"])
    thumbs = "".join('<img src="/%s" alt="%s" class="%s" data-i="%d" loading="lazy">' % (f, esc(p["titulo"]), "on" if i == 0 else "", i) for i, f in enumerate(fotos))
    specs = []
    if p.get("quartos"): specs.append(("Quartos", p["quartos"]))
    if p.get("suites"): specs.append(("Suítes", p["suites"]))
    specs.append(("Banheiros", p.get("banheiros", 0)))
    if p.get("vagas"): specs.append(("Vagas", p["vagas"]))
    specs += [("Área útil", num(p.get("areaUtil", 0)) + " m²"), ("Área total", num(p.get("areaTotal", 0)) + " m²")]
    specs_html = "".join('<div class="spec"><div class="v">%s</div><div class="k">%s</div></div>' % (v, k) for k, v in specs)
    diffs = "".join('<span class="chip">%s</span>' % esc(d) for d in p.get("diferenciais", []))
    tr = "".join('<span class="card-track">%s</span>' % TRILHA[t] for t in p.get("trilhas", []))
    inv = p.get("investimento") or {}
    inv_rows = []
    for k, label in (("entrega", "Entrega"), ("entrada", "Entrada"), ("parcela", "Parcelas"), ("posicao", "Posição"), ("pagamento", "Pagamento")):
        if inv.get(k): inv_rows.append("<li><b>%s:</b> %s</li>" % (label, esc(inv[k])))
    if inv.get("unidadeRef"): inv_rows.append("<li><i>* %s.</i></li>" % esc(inv["unidadeRef"]))
    inv_html = ('<div class="p-section"><h2>Condições</h2><ul style="padding-left:20px;line-height:1.9;">%s</ul></div>' % "".join(inv_rows)) if inv_rows else ""
    cond = ('<div class="p-sub">Condomínio: %s</div>' % money(p["condominio"])) if p.get("condominio") else ""
    wa_msg = wa_link("Olá Dorgival! Tenho interesse no imóvel %s — %s (%s) que vi no seu site." % (p["codigo"], p["titulo"], p["bairro"]))
    jsonld = [
        {
            "@context": "https://schema.org", "@type": "Product", "name": p["titulo"], "sku": p["codigo"],
            "image": [BASE + "/" + f for f in fotos[:6]], "description": p["descricao"],
            "brand": {"@type": "Brand", "name": "Dorgival Neto"},
            "offers": {"@type": "Offer", "priceCurrency": "BRL", "price": p["preco"], "availability": "https://schema.org/InStock", "url": url},
        },
        {
            "@context": "https://schema.org", "@type": "BreadcrumbList",
            "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "Início", "item": BASE + "/"},
                {"@type": "ListItem", "position": 2, "name": "Imóveis", "item": BASE + "/imoveis.html"},
                {"@type": "ListItem", "position": 3, "name": p["bairro"], "item": BASE + "/bairro/%s/" % slugify(p["bairro"])},
                {"@type": "ListItem", "position": 4, "name": p["titulo"], "item": url},
            ],
        },
    ]
    body = f"""<div class="wrap">
  <div class="crumbs"><a href="/">Início</a> › <a href="/imoveis.html">Imóveis</a> › <a href="/bairro/{slugify(p['bairro'])}/">{esc(p['bairro'])}</a> › {esc(p['titulo'])}</div>
  <div class="prop-grid">
    <div>
      <div class="p-gallery">
        <div class="p-main"><img id="pMain" src="/{fotos[0]}" alt="{esc(p['titulo'])}"><span class="card-code" data-copy="{esc(p['codigo'])}" title="Toque para copiar o código">{esc(p['codigo'])}</span><button class="p-nav prev" id="pPrev" aria-label="Foto anterior">‹</button><button class="p-nav next" id="pNext" aria-label="Próxima foto">›</button></div>
        <div class="p-thumbs" id="pThumbs">{thumbs}</div>
      </div>
      <div class="p-section">
        <h1 class="p-title">{esc(p['titulo'])}</h1>
        <div class="card-loc" style="margin-top:6px;">{esc(p['bairro'])} · {esc(p['cidade'])}</div>
        <div class="card-tracks" style="margin-top:10px;">{tr}</div>
      </div>
      <div class="p-specs">{specs_html}</div>
      <div class="p-section"><h2>Sobre o imóvel</h2><p>{esc(p['descricao'])}</p></div>
      {('<div class="p-section"><h2>Diferenciais</h2><div class="chips">' + diffs + '</div></div>') if diffs else ''}
      {inv_html}
    </div>
    <aside class="p-side">
      <div class="p-code">Código {esc(p['codigo'])} · {esc(p['status'])}</div>
      <div class="p-price">{esc(price_txt(p))}</div>
      {cond}
      <div class="p-actions">
        <a class="btn btn-gold" data-book="{p['id']}" href="{book_link(p)}" target="_blank" rel="noopener">Quero ver book/tabela</a>
        <a class="btn btn-outline" href="{wa_msg}" target="_blank" rel="noopener">💬 Falar no WhatsApp</a>
        {'<a class="btn btn-outline" href="/simulador/">📈 Simular investimento</a>' if p.get("simulador") else ''}
        <div class="p-row">
          <button type="button" class="btn btn-outline btn-sm" id="btnShare">↗ Compartilhar</button>
          <button type="button" class="btn fav-btn btn-sm" data-fav="{p['id']}">♥ Favoritar</button>
        </div>
      </div>
      <p style="font-size:11px;color:var(--gray);margin-top:14px;line-height:1.5;">Disponibilidade e valores sujeitos a alteração sem aviso prévio. Cite o código <b>{esc(p['codigo'])}</b> ao falar comigo.</p>
    </aside>
  </div>
  <div class="p-section" style="margin-bottom:70px;">
    <h2>Outros imóveis que podem interessar</h2>
    <div class="grid" id="similares"></div>
  </div>
</div>"""
    scripts = f"""<script>
(function(){{
  var ID = {json.dumps(p['id'])};
  var P = PROPERTIES.find(function(x){{ return x.id === ID; }});
  var fotos = P.fotos, i = 0;
  var main = document.getElementById('pMain'), thumbs = document.querySelectorAll('#pThumbs img');
  function go(n){{ i = (n + fotos.length) % fotos.length; main.src = '/' + fotos[i]; thumbs.forEach(function(t, k){{ t.classList.toggle('on', k === i); }}); }}
  document.getElementById('pPrev').onclick = function(){{ go(i - 1); }};
  document.getElementById('pNext').onclick = function(){{ go(i + 1); }};
  thumbs.forEach(function(t){{ t.onclick = function(){{ go(parseInt(t.getAttribute('data-i'))); }}; }});
  document.getElementById('btnShare').onclick = function(){{ DN.share(P); }};
  document.querySelectorAll('[data-copy]').forEach(function(b){{ b.onclick = function(){{
    var v = b.getAttribute('data-copy');
    var done = function(){{ DN.toast('Código ' + v + ' copiado'); }};
    if (navigator.clipboard && navigator.clipboard.writeText) navigator.clipboard.writeText(v).then(done, done); else done();
  }}; }});
  var fav = document.querySelector('.fav-btn'); if (DN.isFav(ID)) fav.classList.add('on');
  var outros = PROPERTIES.filter(function(x){{ return x.id !== ID; }}).sort(function(a, b){{ return (b.bairro === P.bairro) - (a.bairro === P.bairro); }}).slice(0, 3);
  var box = document.getElementById('similares');
  if (outros.length) box.innerHTML = outros.map(function(x){{ return DN.cardHTML(x); }}).join(''); else box.parentNode.style.display = 'none';
  DN.track('view_item', {{ item_id: ID, item_name: P.titulo }});
}})();
</script>"""
    return page(t_title, desc, path, body, scripts, active="/imoveis.html", image=cover, og_type="product", jsonld=jsonld)


# ------------------------------------------------------------------ página do bairro
def bairro_page(b):
    slug = slugify(b)
    lst = [p for p in PROPS if p["bairro"] == b]
    path = "/bairro/%s/" % slug
    title = "Imóveis à venda no %s, João Pessoa | Dorgival Neto" % b
    desc = "%d imóvel(is) à venda no %s, em João Pessoa, selecionados por Dorgival Neto (CRECI 17191-F). Veja fotos, valores e peça o book/tabela." % (len(lst), b)
    others = "".join('<a class="tab" href="/bairro/%s/">%s</a>' % (slugify(x), esc(x)) for x in BAIRROS if x != b)
    body = f"""<div class="wrap" style="padding-top:34px;padding-bottom:70px;">
  <div class="crumbs" style="padding-top:0;"><a href="/">Início</a> › <a href="/imoveis.html">Imóveis</a> › {esc(b)}</div>
  <span class="eyebrow" style="display:block;margin-top:14px;">Bairro</span>
  <h1 style="font-size:32px;margin-top:6px;">Imóveis à venda no {esc(b)}, João Pessoa</h1>
  <p style="color:var(--gray);margin-top:8px;font-size:14.5px;max-width:640px;">Veja os imóveis disponíveis no bairro {esc(b)} selecionados por Dorgival Neto (CRECI 17191-F). Todos têm código de referência: é só citá-lo ao falar comigo para receber o book ou a tabela.</p>
  <div class="grid">{''.join(card_static(p) for p in lst)}</div>
  {('<h2 style="font-size:22px;margin-top:44px;">Outros bairros</h2><div class="tabs" style="justify-content:flex-start;">' + others + '</div>') if others else ''}
  <div class="center" style="margin-top:40px;"><a class="btn btn-outline" href="/imoveis.html">Ver todos os imóveis</a></div>
</div>"""
    return page(title, desc, path, body, active="/imoveis.html")


# ------------------------------------------------------------------ formulários (avaliação / parceiro)
LEAD_JS = r"""<script>
(function(){
  var iti = window.intlTelInput(document.getElementById('whats'), { initialCountry: 'br', preferredCountries: ['br'], separateDialCode: true, utilsScript: 'https://cdn.jsdelivr.net/npm/intl-tel-input@18.2.1/build/js/utils.js' });
  document.getElementById('leadForm').addEventListener('submit', async function(e){
    e.preventDefault();
    var f = e.target, whats = document.getElementById('whats'), err = document.getElementById('whatsError');
    err.style.display = 'none';
    var wrap = whats.closest('.iti'); if (wrap) wrap.classList.remove('iti-error');
    var req = f.querySelectorAll('[data-req]');
    for (var k = 0; k < req.length; k++) { if (!req[k].value.trim()) { alert('Preencha: ' + req[k].getAttribute('data-req') + '.'); req[k].focus(); return; } }
    if (!whats.value.trim() || !iti.isValidNumber()) { err.style.display = 'block'; if (wrap) wrap.classList.add('iti-error'); whats.focus(); return; }
    var btn = f.querySelector('button[type=submit]'); btn.disabled = true; var label = btn.textContent; btn.textContent = 'Enviando...';
    var fd = new FormData(f); fd.set('whatsapp', iti.getNumber()); fd.set('origem', '__ORIGEM__');
    var ok = false;
    var det = [];
    fd.forEach(function (v, k) { if (v && ['nome', 'whatsapp', 'whatsapp_digitado', 'origem'].indexOf(k) < 0) det.push(k + ': ' + v); });
    fetch('/api/lead', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ origem: '__ORIGEM__', nome: fd.get('nome'), whatsapp: fd.get('whatsapp'), detalhes: det.join(' | ') }) }).catch(function () {});
    try { var r = await fetch('https://formspree.io/f/xgaverke', { method: 'POST', headers: { 'Accept': 'application/json' }, body: fd }); ok = r.ok; } catch (x) {}
    if (ok) {
      DN.track('generate_lead', { method: '__ORIGEM__' });
      document.getElementById('formBox').outerHTML = '<div class="form-dark" style="text-align:center;padding:48px 36px;"><h3 style="color:#fff;font-size:24px;">Recebi sua solicitação!</h3><p style="color:#cfcdc6;margin-top:10px;font-size:14.5px;">Vou analisar e entrar em contato pelo WhatsApp informado.</p><a class="btn btn-gold" style="margin-top:20px;" target="_blank" rel="noopener" href="' + DN.wa('__WAMSG__') + '">💬 Adiantar pelo WhatsApp</a></div>';
    } else {
      btn.disabled = false; btn.textContent = label;
      alert('Não consegui enviar agora. Tente novamente em instantes ou me chame direto no WhatsApp.');
    }
  });
})();
</script>"""

WHATS_FIELD = """<label>Seu WhatsApp</label>
      <input id="whats" name="whatsapp_digitado" type="tel" placeholder="83 9 9999-9999" required>
      <div class="field-error" id="whatsError">Digite um número de telefone válido e completo para o país selecionado.</div>"""


def avaliacao_page():
    feats = [
        ("Metodologia reconhecida", "Avaliação com base na NBR 14.653 — Avaliação de Bens, a norma técnica brasileira para esse tipo de trabalho."),
        ("Laudo técnico", "Documento fundamentado, assinado por Perito Avaliador com registro CNAI sob nº 52963."),
        ("Para cada finalidade", "Compra, venda, garantia, revisão de impostos, partilha ou processos judiciais."),
        ("Atendimento pessoal", "Você fala diretamente comigo, do primeiro contato à entrega do laudo."),
    ]
    steps = ["Você preenche o formulário com os dados básicos do imóvel e a finalidade da avaliação.",
             "Entro em contato pelo WhatsApp para entender o imóvel e o que você precisa.",
             "Alinhamos o escopo e as condições do trabalho.",
             "Realizo a avaliação e entrego o laudo técnico."]
    body = f"""<div class="article" style="max-width:880px;">
  <span class="eyebrow">Perícia e avaliação</span>
  <h1>Quanto vale o seu imóvel? Avaliação técnica com laudo.</h1>
  <p>Seja para vender, comprar, dar em garantia, revisar impostos, fazer uma partilha ou instruir um processo, uma avaliação feita por um profissional habilitado traz segurança e argumento técnico para a sua decisão.</p>
  <div class="feature-list">{''.join('<div class="feature"><h3>%s</h3><p>%s</p></div>' % f for f in feats)}</div>
  <h2>Como funciona</h2>
  <ol style="padding-left:20px;">{''.join('<li>%s</li>' % s for s in steps)}</ol>
  <h2>Peça sua avaliação</h2>
  <div class="form-dark" id="formBox">
    <form id="leadForm">
      <label>Seu nome</label><input name="nome" type="text" placeholder="Como posso te chamar?" data-req="seu nome" required>
      {WHATS_FIELD}
      <div class="form-row">
        <div><label>Tipo de imóvel</label><select name="tipo_imovel"><option>Apartamento</option><option>Casa</option><option>Terreno</option><option>Sala comercial</option><option>Outro</option></select></div>
        <div><label>Finalidade</label><select name="finalidade"><option>Venda</option><option>Compra</option><option>Garantia / financiamento</option><option>Revisão de impostos</option><option>Partilha / inventário</option><option>Processo judicial</option><option>Outra</option></select></div>
      </div>
      <label>Bairro / cidade do imóvel</label><input name="localizacao" type="text" placeholder="Ex.: Bessa, João Pessoa" data-req="o bairro e a cidade do imóvel" required>
      <label>Algo importante para saber? (opcional)</label><textarea name="mensagem" placeholder="Área aproximada, situação do imóvel, prazo..."></textarea>
      <button class="btn btn-gold" type="submit" style="width:100%;justify-content:center;">Solicitar avaliação</button>
    </form>
  </div>
  <p style="font-size:12px;color:var(--gray);margin-top:12px;">Seus dados ficam só comigo — sem spam e sem mensagens automáticas.</p>
</div>"""
    js = LEAD_JS.replace("__ORIGEM__", "avaliacao").replace("__WAMSG__", "Olá Dorgival! Acabei de pedir uma avaliação de imóvel pelo site.")
    return page("Avaliação de Imóveis em João Pessoa — Laudo Técnico NBR 14.653 | Dorgival Neto",
                "Perícia e avaliação de imóveis em João Pessoa com laudo técnico baseado na NBR 14.653, por Perito Avaliador CNAI 52963. Para venda, compra, garantia, impostos, partilha ou processos.",
                "/avaliacao.html", body, ITI_JS + "\n" + js, extra_head=ITI_CSS, active="/avaliacao.html")


def parceiros_page():
    body = f"""<div class="article" style="max-width:880px;">
  <span class="eyebrow">Parcerias</span>
  <h1>Sou corretor parceiro</h1>
  <p>Se você é corretor ou imobiliária e quer trabalhar junto em lançamentos e imóveis em João Pessoa — apresentando meus imóveis aos seus clientes ou trazendo os seus para a minha carteira — vamos conversar.</p>
  <p>As condições de cada parceria são alinhadas caso a caso, com transparência desde o início.</p>
  <h2>Fale comigo</h2>
  <div class="form-dark" id="formBox">
    <form id="leadForm">
      <div class="form-row">
        <div><label>Nome</label><input name="nome" type="text" placeholder="Seu nome" data-req="seu nome" required></div>
        <div><label>CRECI</label><input name="creci" type="text" placeholder="Ex.: 12345-F" data-req="seu CRECI" required></div>
      </div>
      {WHATS_FIELD}
      <label>Imobiliária (opcional)</label><input name="imobiliaria" type="text" placeholder="Onde você atua">
      <label>Como podemos trabalhar juntos?</label><textarea name="mensagem" placeholder="Conte um pouco sobre sua atuação e o que você procura..."></textarea>
      <button class="btn btn-gold" type="submit" style="width:100%;justify-content:center;">Enviar</button>
    </form>
  </div>
</div>"""
    js = LEAD_JS.replace("__ORIGEM__", "parceiro").replace("__WAMSG__", "Olá Dorgival! Sou corretor(a) e acabei de enviar um contato de parceria pelo site.")
    return page("Sou Corretor Parceiro | Parcerias em Imóveis em João Pessoa | Dorgival Neto",
                "Corretor ou imobiliária? Vamos trabalhar juntos em lançamentos e imóveis em João Pessoa. Fale com Dorgival Neto, CRECI 17191-F.",
                "/parceiros.html", body, ITI_JS + "\n" + js, extra_head=ITI_CSS, active="/parceiros.html")


# ------------------------------------------------------------------ simulador de investimento
SIM_JS = r"""<script>
(function(){
  var SIM = PROPERTIES.filter(function(p){ return p.simulador; });
  if (!SIM.length) return;
  var CEN = [
    { nome: 'Conservador', occ: 0.45, val: 0.10 },
    { nome: 'Base', occ: 0.55, val: 0.12 },
    { nome: 'Otimista', occ: 0.65, val: 0.15 }
  ];
  var ADM = 0.20;
  var $ = function(id){ return document.getElementById(id); };
  var used = false;

  function parse(v){
    var s = String(v == null ? '' : v).replace(/[^\d,.\-]/g, '');
    if (!s) return NaN;
    if (s.indexOf(',') > -1) s = s.replace(/\./g, '').replace(',', '.');
    else if ((s.match(/\./g) || []).length > 1 || /\.\d{3}$/.test(s)) s = s.replace(/\./g, '');
    return parseFloat(s);
  }
  function brl(v){ return (v < 0 ? '-' : '') + 'R$ ' + Math.abs(Math.round(v)).toLocaleString('pt-BR'); }
  function pct(v, d){ return (v * 100).toLocaleString('pt-BR', { minimumFractionDigits: d || 0, maximumFractionDigits: d == null ? 1 : d }) + '%'; }
  function cur(){ return SIM.filter(function(p){ return p.id === $('simImovel').value; })[0] || SIM[0]; }

  function fill(p){
    $('simPreco').value = p.preco ? String(p.preco).replace(/\B(?=(\d{3})+(?!\d))/g, '.') : '';
    $('simDiaria').value = p.simulador.diaria || '';
    $('simCond').value = p.simulador.condominio == null ? '' : p.simulador.condominio;
    $('simIptu').value = p.simulador.iptu == null ? '' : p.simulador.iptu;
    $('simEntrega').value = p.simulador.entregaAnos || 0;
    document.querySelectorAll('.cond').forEach(function(c){ c.style.display = c.getAttribute('data-id') === p.id ? '' : 'none'; });
  }

  function calc(){
    var p = cur();
    var preco = parse($('simPreco').value), diaria = parse($('simDiaria').value);
    var cond = parse($('simCond').value), iptu = parse($('simIptu').value);
    var anos = parseInt($('simAnos').value, 10);
    var entrega = Math.max(0, parseFloat($('simEntrega').value) || 0);
    var out = $('simTabela'), warn = $('simWarn'), cta = $('simCta');
    if (!(preco > 0) || !(diaria > 0)) {
      out.innerHTML = '<p class="sim-note" style="margin:0;">Informe o preço do imóvel e a diária média para ver a projeção.</p>';
      warn.classList.remove('on'); cta.style.display = 'none';
      return;
    }
    var semCustos = isNaN(cond) || isNaN(iptu);
    warn.classList.toggle('on', semCustos);
    var custos = (isNaN(cond) ? 0 : cond) * 12 + (isNaN(iptu) ? 0 : iptu);
    var anosRenda = Math.max(0, anos - entrega);
    var rows = CEN.map(function(c){
      var bruta = diaria * 365 * c.occ, adm = bruta * ADM, liq = bruta - adm - custos;
      var fut = preco * Math.pow(1 + c.val, anos), valoriz = fut - preco;
      var renda = liq * anosRenda, ganho = valoriz + renda;
      return { c: c, bruta: bruta, adm: adm, liq: liq, y: liq / preco, fut: fut, renda: renda, ganho: ganho, ret: ganho / preco };
    });
    function line(label, fn, cls, neg){
      return '<tr' + (cls ? ' class="' + cls + '"' : '') + '><td>' + label + '</td>' + rows.map(function(r){
        var v = fn(r); return '<td' + (neg && neg(r) ? ' class="neg"' : '') + '>' + v + '</td>';
      }).join('') + '</tr>';
    }
    out.innerHTML = '<table class="sim-table"><thead><tr><th></th>' + CEN.map(function(c){ return '<th>' + c.nome + '</th>'; }).join('') + '</tr></thead><tbody>' +
      line('Ocupação da diária', function(r){ return pct(r.c.occ); }) +
      line('Receita bruta por ano', function(r){ return brl(r.bruta); }) +
      line('Administração (' + pct(ADM) + ')', function(r){ return '-' + brl(r.adm).replace('-', ''); }) +
      line('Condomínio + IPTU por ano', function(r){ return semCustos && !custos ? 'não informado' : '-' + brl(custos).replace('-', ''); }) +
      line('Renda líquida por ano', function(r){ return brl(r.liq); }, 'key', function(r){ return r.liq < 0; }) +
      line('Rendimento líquido sobre o preço', function(r){ return pct(r.y, 1) + ' a.a.'; }, '', function(r){ return r.y < 0; }) +
      line('Valorização do imóvel', function(r){ return pct(r.c.val) + ' a.a.'; }) +
      line('Valor estimado em ' + anos + ' anos', function(r){ return brl(r.fut); }, 'key') +
      line('Renda acumulada (' + anosRenda + (anosRenda === 1 ? ' ano' : ' anos') + ' de renda)', function(r){ return brl(r.renda); }, '', function(r){ return r.renda < 0; }) +
      line('Ganho total estimado', function(r){ return brl(r.ganho); }, 'key', function(r){ return r.ganho < 0; }) +
      line('Retorno total sobre o preço', function(r){ return pct(r.ret, 0); }, '', function(r){ return r.ret < 0; }) +
      '</tbody></table>';
    var base = rows[1];
    cta.style.display = '';
    cta.href = DN.wa('Olá Dorgival! Fiz a simulação do ' + p.codigo + ' (' + p.titulo + ') no site: preço ' + brl(preco) + ', diária ' + brl(diaria) + ', prazo ' + anos + ' anos. No cenário base deu ganho de ' + brl(base.ganho) + '. Quero a tabela e uma simulação personalizada.');
    if (!used) { used = true; DN.track('simulador_uso', { item_id: p.id }); }
  }

  var sel = $('simImovel');
  if (SIM.length > 1) {
    sel.innerHTML = SIM.map(function(p){ return '<option value="' + p.id + '">' + p.titulo + '</option>'; }).join('');
    sel.onchange = function(){ fill(cur()); calc(); };
  } else { sel.parentNode.style.display = 'none'; sel.innerHTML = '<option value="' + SIM[0].id + '"></option>'; }
  ['simPreco', 'simDiaria', 'simCond', 'simIptu', 'simEntrega', 'simAnos'].forEach(function(id){ $(id).addEventListener('input', calc); $(id).addEventListener('change', calc); });
  fill(SIM[0]); calc();
})();
</script>"""


def simulador_page():
    sim = [p for p in PROPS if p.get("simulador")]
    names = ", ".join(p["titulo"] for p in sim)
    rows_for = lambda p: [
        ("Preço de referência", price_txt(p) + (" (%s)" % p["investimento"]["unidadeRef"].replace("Preço e metragem da ", "") if (p.get("investimento") or {}).get("unidadeRef") else "")),
        ("Entrega", (p.get("investimento") or {}).get("entrega")),
        ("Entrada", (p.get("investimento") or {}).get("entrada")),
        ("Parcelas", (p.get("investimento") or {}).get("parcela")),
        ("Posição", (p.get("investimento") or {}).get("posicao")),
        ("Pagamento", (p.get("investimento") or {}).get("pagamento")),
    ]
    conds = ""
    for p in sim:
        trs = "".join('<tr><td>%s</td><td>%s</td></tr>' % (k, esc(v) if v else '<span class="pend">A confirmar — peça a tabela atualizada</span>') for k, v in rows_for(p))
        conds += '<div class="cond" data-id="%s"><h3 style="font-size:20px;margin-top:6px;">%s</h3><table class="cond-table">%s</table></div>' % (p["id"], esc(p["titulo"]), trs)
    first = sim[0] if sim else None
    body = f"""<div class="article" style="max-width:1000px;">
  <span class="eyebrow">Investimento</span>
  <h1>Simulador de investimento</h1>
  <p>Veja, em três cenários, quanto um imóvel de temporada (diária) pode render em renda e valorização ao longo dos anos: {esc(names)}. Ajuste os números e compare.</p>
  <div class="sim-disclaimer">⚠ Projeção não é promessa de rentabilidade. <span>Os resultados abaixo são simulações com premissas hipotéticas de diária, ocupação e valorização. O mercado pode ter desempenho diferente do projetado, inclusive com perda. Não é recomendação de investimento nem garantia de retorno — confirme valores e condições antes de decidir.</span></div>
  <div class="sim-grid">
    <form class="form-dark" id="simForm" onsubmit="return false;" autocomplete="off">
      <div><label>Imóvel</label><select id="simImovel"></select></div>
      <label>Preço do imóvel (R$)</label><input id="simPreco" type="text" inputmode="decimal">
      <label>Diária média (R$)</label><input id="simDiaria" type="text" inputmode="decimal" placeholder="Informe a diária média">
      <div class="sim-hint">A diária varia muito conforme a região, o bairro e o tipo de empreendimento. Use a sua pesquisa de mercado ou peça uma estimativa a mim.</div>
      <label>Condomínio (R$ por mês)</label><input id="simCond" type="text" inputmode="decimal" placeholder="Preencha para um resultado fiel">
      <label>IPTU (R$ por ano)</label><input id="simIptu" type="text" inputmode="decimal" placeholder="Preencha para um resultado fiel">
      <label>Prazo da análise</label>
      <select id="simAnos"><option value="3">3 anos</option><option value="5" selected>5 anos</option><option value="7">7 anos</option><option value="10">10 anos</option></select>
      <label>Anos até a entrega (sem renda)</label><input id="simEntrega" type="text" inputmode="decimal" value="0">
      <div class="sim-hint">Imóvel na planta só gera renda depois da entrega. Informe quantos anos faltam: nesse período a renda não conta, mas a valorização sim.</div>
    </form>
    <div>
      <div class="sim-result">
        <div class="sim-warn" id="simWarn">⚠ Condomínio e/ou IPTU não preenchidos: esses custos foram considerados como R$ 0, então o resultado abaixo pode estar acima do real. Preencha os campos para uma projeção mais fiel.</div>
        <div id="simTabela"></div>
        <p class="sim-note">Premissas: administração de 20% sobre a receita bruta; ocupação de 45% / 55% / 65% e valorização de 10% / 12% / 15% ao ano (conservador / base / otimista), valores constantes ao longo do prazo, sem impostos sobre a renda, financiamento ou correção da diária. Projeção não é promessa de rentabilidade.</p>
      </div>
      <p style="margin-top:18px;"><a class="btn btn-gold" id="simCta" target="_blank" rel="noopener" href="#">💬 Quero a tabela e uma simulação personalizada</a></p>
    </div>
  </div>
  <h2>Condições de pagamento</h2>
  <p>Resumo das condições do empreendimento. O que ainda estiver como “a confirmar” eu envio atualizado pelo WhatsApp.</p>
  {conds}
</div>"""
    return page("Simulador de Investimento Imobiliário em João Pessoa — Renda e Valorização | Dorgival Neto",
                "Simule o retorno de um imóvel de temporada em João Pessoa em três cenários (conservador, base e otimista): renda com diária e valorização. Projeção, não promessa de rentabilidade.",
                "/simulador/", body, SIM_JS, active="")


# ------------------------------------------------------------------ privacidade (LGPD)
def privacidade_page():
    body = """<div class="article">
  <span class="eyebrow">Privacidade</span>
  <h1>Política de Privacidade</h1>
  <div class="meta">Atualizada em 23 de outubro de 2026</div>
  <p>Este site é mantido por <b>Dorgival Neto Negócios Imobiliários Ltda</b> (CNPJ 63.932.753/0001-55), responsável pelo tratamento dos dados descritos abaixo, conforme a Lei Geral de Proteção de Dados (LGPD, Lei 13.709/2018).</p>
  <h2>Quais dados coletamos</h2>
  <ul>
    <li><b>Dados que você informa</b> nos formulários: nome, e-mail, WhatsApp e as informações que você escrever (por exemplo, dados do imóvel numa avaliação, ou seu depoimento).</li>
    <li><b>Dados de navegação</b>, apenas se você aceitar os cookies de medição: páginas visitadas, tipo de aparelho e origem do acesso, de forma agregada.</li>
  </ul>
  <h2>Para que usamos</h2>
  <ul>
    <li>Enviar o material que você pediu (guias em PDF) e responder à sua solicitação.</li>
    <li>Entrar em contato por WhatsApp ou e-mail sobre o assunto que você demonstrou interesse — como imóveis, avaliações ou parcerias.</li>
    <li>Publicar o seu depoimento, somente quando você autorizar.</li>
    <li>Entender como o site é usado e melhorá-lo (medição, só com o seu aceite).</li>
  </ul>
  <h2>Com quem os dados passam</h2>
  <p>Usamos prestadores para operar o site: hospedagem (Vercel), recebimento de formulários (Formspree), e-mail e planilha de contatos (Google) e, se você aceitar os cookies de medição, Google Analytics e Meta. Não vendemos seus dados.</p>
  <h2>Cookies</h2>
  <p>O site só carrega ferramentas de medição depois que você clica em “Aceitar” no aviso de cookies. Se recusar, tudo continua funcionando. Para mudar sua escolha, use o botão abaixo.</p>
  <p><button type="button" class="btn btn-outline btn-sm" onclick="DN.resetConsent()">Rever minha escolha de cookies</button></p>
  <h2>Por quanto tempo guardamos</h2>
  <p>Mantemos seus dados pelo tempo necessário para atender à sua solicitação e manter o relacionamento comercial, ou até você pedir a exclusão.</p>
  <h2>Seus direitos</h2>
  <p>Você pode pedir confirmação de que tratamos seus dados, acesso, correção, anonimização, portabilidade, informação sobre compartilhamento e a exclusão, além de revogar o consentimento a qualquer momento. Escreva para <a href="mailto:dorgivalneto.corretor@gmail.com">dorgivalneto.corretor@gmail.com</a> ou chame no WhatsApp.</p>
</div>"""
    return page("Política de Privacidade | Dorgival Neto", "Como o site de Dorgival Neto trata seus dados pessoais, cookies de medição e seus direitos pela LGPD.",
                "/privacidade.html", body, active="")


# ------------------------------------------------------------------ mercado (blog)
def pt_date(iso):
    y, m, d = iso.split("-")
    meses = ["janeiro", "fevereiro", "março", "abril", "maio", "junho", "julho", "agosto", "setembro", "outubro", "novembro", "dezembro"]
    return "%d de %s de %s" % (int(d), meses[int(m) - 1], y)


def mercado_pages(posts):
    out = {}
    cards = "".join('<a class="post-card" href="/mercado/%s/"><div class="meta" style="margin:0 0 6px;color:var(--gray);font-size:12px;">%s</div><h3>%s</h3><p>%s</p></a>' % (
        p["slug"], pt_date(p["date"]), esc(p["title"]), esc(p["description"])) for p in sorted(posts, key=lambda x: x["date"], reverse=True))
    body = f"""<div class="article" style="max-width:880px;">
  <span class="eyebrow">Mercado</span>
  <h1>O mercado imobiliário de João Pessoa</h1>
  <p>Análises e indicadores para quem quer comprar, vender ou investir com mais segurança.</p>
  <div class="post-list">{cards}</div>
</div>"""
    out["mercado/index.html"] = page("Mercado Imobiliário de João Pessoa — Análises e Indicadores | Dorgival Neto",
                                     "Análises e indicadores do mercado imobiliário de João Pessoa para quem quer comprar, vender ou investir.",
                                     "/mercado/", body, active="/mercado/")
    for p in posts:
        path = "/mercado/%s/" % p["slug"]
        art = {"@context": "https://schema.org", "@type": "Article", "headline": p["title"], "datePublished": p["date"],
               "author": {"@type": "Person", "name": "Dorgival Neto"}, "mainEntityOfPage": BASE + path,
               "image": BASE + "/assets/og-image.jpg"}
        body = f"""<article class="article">
  <div class="crumbs" style="padding-top:0;"><a href="/mercado/">Mercado</a> › {esc(p['title'])}</div>
  <h1>{esc(p['title'])}</h1>
  <div class="meta">Por Dorgival Neto · {pt_date(p['date'])}</div>
  {p['body']}
  <div class="form-dark" style="text-align:center;margin-top:40px;"><h3 style="color:#fff;font-size:22px;">Quer conversar sobre o seu objetivo?</h3><p style="color:#cfcdc6;margin-top:8px;font-size:14px;">Me conte se você quer investir ou morar e eu te mostro as melhores opções.</p><a class="btn btn-gold" style="margin-top:18px;" href="/imoveis.html">Ver imóveis</a></div>
</article>"""
        out["mercado/%s/index.html" % p["slug"]] = page(p["title"] + " | Dorgival Neto", p["description"], path, body, active="/mercado/", og_type="article", jsonld=[art])
    return out


# ------------------------------------------------------------------ páginas escritas à mão
STATIC = {
    "index.html": dict(
        path="/", active="",
        title="Corretor de Imóveis em João Pessoa | Dorgival Neto — CRECI 17191-F",
        desc="Administrador, corretor, perito e avaliador imobiliário em João Pessoa. Imóveis de médio e alto padrão, lançamentos e investimento. CRECI 17191-F · CNAI 52963.",
        jsonld=True),
    "imoveis.html": dict(
        path="/imoveis.html", active="/imoveis.html",
        title="Imóveis à Venda em João Pessoa — Para Investir e Para Morar | Dorgival Neto",
        desc="Catálogo de lançamentos e imóveis prontos em João Pessoa: Bessa, Bancários e mais. Para investir ou para morar. Atendimento de Dorgival Neto, CRECI 17191-F."),
    "joao-pessoa.html": dict(
        path="/joao-pessoa.html", active="/joao-pessoa.html",
        title="Mercado Imobiliário de João Pessoa em Números | Dorgival Neto",
        desc="PIB, rating AAA, valorização do m² e o Polo Cabo Branco: veja por que João Pessoa vive um dos melhores momentos do Nordeste para morar e investir."),
    "depoimento.html": dict(
        path="/depoimento.html", active="", noindex=True,
        title="Deixe seu Depoimento | Dorgival Neto",
        desc="Compartilhe sua experiência com Dorgival Neto — Corretor, Perito e Avaliador Imobiliário em João Pessoa."),
}

AGENT_LD = {
    "@context": "https://schema.org", "@type": "RealEstateAgent", "name": "Dorgival Neto", "url": BASE + "/",
    "image": BASE + "/assets/og-image.jpg", "logo": BASE + "/assets/icon-512.png",
    "description": "Administrador, corretor, perito e avaliador imobiliário em João Pessoa (PB). Imóveis de médio e alto padrão, lançamentos e investimento imobiliário.",
    "telephone": "+55 83 99633-6569", "email": "dorgivalneto.corretor@gmail.com", "identifier": "CRECI 17191-F",
    "areaServed": {"@type": "City", "name": "João Pessoa"},
    "address": {"@type": "PostalAddress", "addressLocality": "João Pessoa", "addressRegion": "PB", "addressCountry": "BR"},
    "sameAs": [INSTAGRAM],
}


def patch_static(fname, cfg):
    h = read(fname)
    h = re.sub(r"<title>.*?</title>", "<title>%s</title>" % esc(cfg["title"]), h, count=1, flags=re.S)
    h = re.sub(r'[ \t]*<meta name="description" content="[^"]*">\r?\n', "", h)
    h = re.sub(r"<!-- SEO:start -->.*?<!-- SEO:end -->\r?\n", "", h, flags=re.S)
    block = seo_block(cfg["title"], cfg["desc"], cfg["path"], noindex=cfg.get("noindex", False), jsonld=[AGENT_LD] if cfg.get("jsonld") else None)
    m = re.search(r'<meta name="viewport"[^>]*>\r?\n', h)
    h = h[:m.end()] + block + h[m.end():]
    # nav
    h = re.sub(r'(<nav class="nav-links" id="navLinks">).*?(</nav>)', lambda mm: mm.group(1) + "\n      " + nav_inner(cfg["active"]) + "\n    " + mm.group(2), h, count=1, flags=re.S)
    # rodapé
    fl = "<!--FOOTLINKS-->%s<!--/FOOTLINKS-->" % foot_links()
    if "<!--FOOTLINKS-->" in h:
        h = re.sub(r"<!--FOOTLINKS-->.*?<!--/FOOTLINKS-->", lambda mm: fl, h, flags=re.S)
    else:
        h = h.replace('<div class="foot-bottom" style="margin-top:0;border-top:none;">', '<div class="foot-links">%s</div>\n    <div class="foot-bottom" style="margin-top:0;border-top:none;">' % fl, 1)
    # scripts de análise
    if 'assets/analytics.js' not in h and '/assets/analytics.js' not in h:
        inc = ""
        if 'assets/data.js' not in h and '/assets/data.js' not in h:
            inc += '<script src="/assets/data.js"></script>\n'
        inc += '<script src="/assets/analytics.js"></script>\n'
        h = h.replace("</body>", inc + "</body>", 1)
    write(fname, h)


def main():
    for fname, cfg in STATIC.items():
        patch_static(fname, cfg)

    urls = [("/", "1.0"), ("/imoveis.html", "0.9"), ("/joao-pessoa.html", "0.7"), ("/avaliacao.html", "0.8"),
            ("/parceiros.html", "0.5"), ("/mercado/", "0.7"), ("/simulador/", "0.7"), ("/privacidade.html", "0.2")]
    for p in PROPS:
        write("imovel/%s/index.html" % p["codigo"], property_page(p))
        urls.append(("/imovel/%s/" % p["codigo"], "0.9"))
    for b in BAIRROS:
        write("bairro/%s/index.html" % slugify(b), bairro_page(b))
        urls.append(("/bairro/%s/" % slugify(b), "0.8"))
    write("avaliacao.html", avaliacao_page())
    write("parceiros.html", parceiros_page())
    write("simulador/index.html", simulador_page())
    write("privacidade.html", privacidade_page())
    posts = json.loads(read("tools/posts.json"))
    for path, content in mercado_pages(posts).items():
        write(path, content)
    for p in posts:
        urls.append(("/mercado/%s/" % p["slug"], "0.6"))

    sm = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    for u, pr in urls:
        sm += "  <url><loc>%s%s</loc><lastmod>%s</lastmod><priority>%s</priority></url>\n" % (BASE, u, NOW_ISO, pr)
    sm += "</urlset>\n"
    write("sitemap.xml", sm)
    write(".vercelignore", "tools/\ncadastro/\n")

    # endereços antigos (pelo nome interno e pelos códigos DN-...) levam ao endereço pelo código
    redirects = []
    for p in PROPS:
        dest = "/imovel/%s/" % p["codigo"]
        # a Vercel diferencia maiúsculas/minúsculas (testado): o código em minúsculas também leva à página
        olds = [p["id"], p["codigo"].lower()] + [old for old, new in OLD_CODES.items() if new == p["codigo"]]
        for o in olds:
            for s in ("/imovel/%s" % o, "/imovel/%s/" % o):
                redirects.append({"source": s, "destination": dest, "permanent": True})
    vercel = {"functions": {"api/send-guia.js": {"includeFiles": "api/_files/*.pdf"}}, "redirects": redirects}
    write("vercel.json", json.dumps(vercel, indent=2) + "\n")
    print("ok: %d imóveis, %d bairros, %d posts, %d urls no sitemap" % (len(PROPS), len(BAIRROS), len(posts), len(urls)))


if __name__ == "__main__":
    main()
