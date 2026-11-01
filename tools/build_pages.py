"""Gera as páginas estáticas do site a partir de assets/data.js.

Uso:  python tools/build_pages.py
Gera: imovel/<codigo>/index.html, bairro/<slug>/index.html, avaliacao.html,
      corretor-parceiro.html, parceiros/ (lista + uma página por parceiro, de
      tools/parceiros.json), mercado/..., sitemap.xml e ajusta nav/rodapé/SEO das
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
LINKEDIN = re.search(r'linkedin:\s*"([^"]+)"', DATA).group(1)
EMAIL = re.search(r'email:\s*"([^"]+)"', DATA).group(1)
INVISTA_END = "R. Ivanice Martins da Câmara, 61 · Jardim Oceania, João Pessoa – PB · CEP 58037-115"
INVISTA_MAPA = "https://maps.app.goo.gl/pDK5F2TGNSeX4AjL7"

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


BOOK_STATUS = ("Lançamento", "Na planta", "Em construção")  # só estes têm book e tabela de vendas


def has_book(p):
    return p["status"] in BOOK_STATUS


def wa_imovel(p):
    """Mensagem de WhatsApp com código, dados e link direto da página do imóvel (igual a DN.waImovel em catalog.js)."""
    pedido = ", e gostaria de agendar uma apresentação do empreendimento e receber informações sobre os valores de investimento" if has_book(p) else ""
    return wa_link("Olá Dorgival! Tenho interesse no imóvel %s (%s), %s%s. Vi no seu site: %s/imovel/%s/" % (
        p["codigo"], p["titulo"], price_txt(p), pedido, BASE, p["codigo"]))


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


def excl_tag(p):
    return '<span class="card-track excl">Exclusividade</span>' if p.get("exclusivo") else ""

# prefixo do código por tipo de imóvel (código = prefixo + 4 dígitos, ex.: AP0001)
PREFIXOS = {"Apartamento": "AP", "Flat": "FL", "Terreno": "TE", "Casa": "CA", "Sala comercial": "SL", "Cobertura": "CO", "Garden": "GD"}
OLD_CODES = {"DN-BES-001": "AP0001", "DN-BAN-001": "AP0002", "DN-BAN-002": "AP0003"}  # códigos usados até 26/10/2026
OLD_IDS = {"elevatto-bessa": "AP0001", "360-house-tambau": "AP0004"}  # ids que traziam o nome do empreendimento (trocados em 29/10/2026)
for _p in PROPS:
    _pre = PREFIXOS.get(_p.get("categoria"))
    assert _pre and re.fullmatch(_pre + r"\d{4}", _p["codigo"]), "código inválido para %s: %s" % (_p["id"], _p["codigo"])
assert len({_p["codigo"] for _p in PROPS}) == len(PROPS), "código repetido"
BAIRROS = sorted({p["bairro"] for p in PROPS})

# parceiros de serviços (tools/parceiros.json); só os com "ativo": true aparecem
PARCEIROS = [x for x in json.loads(read("tools/parceiros.json"))["parceiros"] if x.get("ativo", True)]
for _x in PARCEIROS:
    assert re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", _x["slug"]), "slug inválido: %s" % _x["slug"]
    assert re.fullmatch(r"55\d{10,11}", _x["whatsapp"]), "whatsapp do parceiro %s: use 55 + DDD + número" % _x["slug"]
    for _f in (_x["logo"], _x["imagemServicos"]):
        assert os.path.exists(os.path.join(ROOT, _f)), "imagem não encontrada: %s" % _f
assert len({_x["slug"] for _x in PARCEIROS}) == len(PARCEIROS), "slug de parceiro repetido"


# ------------------------------------------------------------------ pedaços comuns
def nav_inner(active=""):
    items = [
        ("/", "Home"),
        ("/imoveis.html", "Imóveis"),
        ("/simulador/", "Simular investimento"),
        ("/avaliacao.html", "Avalie seu imóvel"),
        ("/#servicos", "Serviços"),
        ("/joao-pessoa.html", "João Pessoa"),
        ("/#depoimentos", "Depoimentos"),
        ("/#quemsou", "Quem sou eu"),
        ("/mercado/", "Notícias e Mercado"),
        ("/parceiros/", "Parceiros"),
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
        ("/parceiros/", "Parceiros de serviços"),
        ("/corretor-parceiro.html", "Sou corretor parceiro"),
        ("/mercado/", "Notícias e Mercado"),
        ("/simulador/", "Simulador de investimento"),
        ("/#guia", "Guia de compra"),
    ] + [("/bairro/%s/" % slugify(b), "Imóveis em %s" % b) for b in BAIRROS] + [("/privacidade.html", "Privacidade")]
    return "".join('<a href="%s">%s</a>' % l for l in links)


def seo_block(title, desc, path, image="/assets/og-image.jpg", noindex=False, og_type="website", jsonld=None, locale="pt_BR", alternates=None):
    url = BASE + path
    img = image if image.startswith("http") else BASE + image
    lines = [
        "<!-- SEO:start -->",
        '<meta name="description" content="%s">' % esc(desc),
        '<link rel="canonical" href="%s">' % url,
    ]
    for hl, href in (alternates or []):
        lines.append('<link rel="alternate" hreflang="%s" href="%s">' % (hl, BASE + href))
    if noindex:
        lines.append('<meta name="robots" content="noindex, follow">')
    lines += [
        '<meta name="theme-color" content="#141414">',
        '<link rel="icon" href="/favicon.ico" sizes="any">',
        '<link rel="icon" type="image/png" sizes="32x32" href="/assets/favicon-32.png">',
        '<link rel="apple-touch-icon" href="/assets/apple-touch-icon.png">',
        '<meta property="og:type" content="%s">' % og_type,
        '<meta property="og:locale" content="%s">' % locale,
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
CORE_JS = ('<script src="/assets/data.js"></script>\n<script src="/assets/catalog.js"></script>\n<script src="/assets/analytics.js"></script>\n<script src="/assets/site.js"></script>')

# ícones do rodapé (cada um com link; sem @ nem texto)
_SVG = {
    "whatsapp": '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M17.6 6.32A7.85 7.85 0 0 0 12.05 4a7.94 7.94 0 0 0-6.9 11.9L4 20l4.2-1.1a7.93 7.93 0 0 0 3.85 1h.01A7.94 7.94 0 0 0 20 12.05a7.9 7.9 0 0 0-2.4-5.73zM12.06 18.6h-.01a6.55 6.55 0 0 1-3.35-.92l-.24-.14-2.49.65.67-2.43-.16-.25a6.58 6.58 0 0 1 5.6-10.1 6.53 6.53 0 0 1 4.63 1.92 6.5 6.5 0 0 1 1.93 4.63 6.6 6.6 0 0 1-6.58 6.64zm3.6-4.93c-.2-.1-1.17-.58-1.35-.64-.18-.07-.31-.1-.44.1-.13.2-.5.64-.62.77-.11.13-.23.14-.42.05-.2-.1-.83-.3-1.58-.98-.58-.52-.98-1.16-1.1-1.36-.11-.2-.01-.3.09-.41.1-.1.22-.26.33-.39.11-.13.15-.22.22-.37.07-.14.03-.27-.03-.37-.07-.1-.32-.77-.44-1.06-.11-.28-.23-.24-.32-.24-.08 0-.18-.01-.28-.01-.1 0-.26.04-.4.19-.13.15-.51.5-.51 1.2 0 .71.51 1.4.58 1.5.07.1.99 1.51 2.4 2.06 1.42.55 1.42.37 1.68.35.26-.03.85-.35.97-.68.12-.34.12-.62.09-.68-.03-.06-.11-.1-.24-.16z"/></svg>',
    "instagram": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="18" height="18" rx="5"/><circle cx="12" cy="12" r="3.5"/><circle cx="17.3" cy="6.7" r="0.9" fill="currentColor" stroke="none"/></svg>',
    "linkedin": '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433a2.062 2.062 0 0 1-2.063-2.065 2.064 2.064 0 1 1 2.063 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/></svg>',
    "email": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="5" width="18" height="14" rx="2"/><path d="M4 6.5l8 6.5 8-6.5"/></svg>',
    "maps": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"><path d="M12 21.5s7-6.1 7-11.8a7 7 0 0 0-14 0c0 5.7 7 11.8 7 11.8z"/><circle cx="12" cy="9.7" r="2.6"/></svg>',
}

# bandeiras redondas do seletor de idioma
_FLAG = {
    "pt": '<svg viewBox="0 0 36 36"><defs><clipPath id="fl-pt"><circle cx="18" cy="18" r="18"/></clipPath></defs><g clip-path="url(#fl-pt)"><rect width="36" height="36" fill="#009c3b"/><polygon points="18,5 33,18 18,31 3,18" fill="#ffdf00"/><circle cx="18" cy="18" r="6.6" fill="#002776"/><path d="M11.8 16.4c4.2-1.1 8.7-.7 12.4 1.6" stroke="#fff" stroke-width="1.3" fill="none"/></g></svg>',
    "en": '<svg viewBox="0 0 36 36"><defs><clipPath id="fl-en"><circle cx="18" cy="18" r="18"/></clipPath></defs><g clip-path="url(#fl-en)"><rect width="36" height="36" fill="#fff"/><g fill="#b22234"><rect y="0" width="36" height="2.77"/><rect y="5.54" width="36" height="2.77"/><rect y="11.08" width="36" height="2.77"/><rect y="16.62" width="36" height="2.77"/><rect y="22.16" width="36" height="2.77"/><rect y="27.7" width="36" height="2.77"/><rect y="33.23" width="36" height="2.77"/></g><rect width="17" height="19.4" fill="#3c3b6e"/><g fill="#fff"><circle cx="4" cy="4" r="1"/><circle cx="8.5" cy="4" r="1"/><circle cx="13" cy="4" r="1"/><circle cx="6.2" cy="8.5" r="1"/><circle cx="10.8" cy="8.5" r="1"/><circle cx="4" cy="13" r="1"/><circle cx="8.5" cy="13" r="1"/><circle cx="13" cy="13" r="1"/><circle cx="6.2" cy="17" r="1"/><circle cx="10.8" cy="17" r="1"/></g></g></svg>',
    "es": '<svg viewBox="0 0 36 36"><defs><clipPath id="fl-es"><circle cx="18" cy="18" r="18"/></clipPath></defs><g clip-path="url(#fl-es)"><rect width="36" height="36" fill="#aa151b"/><rect y="9" width="36" height="18" fill="#f1bf00"/></g></svg>',
}
_LANG_LINKS = [("pt", "/", "Português", "pt-BR"), ("en", "/en/", "English", "en"), ("es", "/es/", "Español", "es")]
_FOOT_I18N = {
    "pt": dict(label="Idioma do site", addr="Atendimento presencial na Invista Imóveis", rights="Todos os direitos reservados.", maps="Localização no Google Maps"),
    "en": dict(label="Site language", addr="In-person service at Invista Imóveis", rights="All rights reserved.", maps="Location on Google Maps"),
    "es": dict(label="Idioma del sitio", addr="Atención presencial en Invista Imóveis", rights="Todos los derechos reservados.", maps="Ubicación en Google Maps"),
}


def footer_html(style="", lang="pt"):
    """Rodapé único do site inteiro (gerado aqui e aplicado também às páginas escritas à mão)."""
    t = _FOOT_I18N[lang]
    msg = {"pt": "Olá Dorgival! Vim pelo site e gostaria de falar com você.",
           "en": "Hello Dorgival! I found your website and would like to talk to you.",
           "es": "¡Hola Dorgival! Vi tu sitio web y me gustaría hablar contigo."}[lang]
    soc = [("WhatsApp", wa_link(msg), "whatsapp", True),
           ("Instagram", INSTAGRAM, "instagram", True), ("LinkedIn", LINKEDIN, "linkedin", True),
           ("E-mail", "mailto:" + EMAIL, "email", False),
           (t["maps"], INVISTA_MAPA, "maps", True)]
    icons = "".join('<a href="%s" aria-label="%s" title="%s"%s>%s</a>' % (
        h, n, n, ' target="_blank" rel="noopener"' if ext else "", _SVG[k]) for n, h, k, ext in soc)
    flags = "".join('<a href="%s" hreflang="%s" lang="%s" aria-label="%s" title="%s"%s>%s</a>' % (
        href, hl, hl, nm, nm, ' class="cur" aria-current="true"' if code == lang else "", _FLAG[code]) for code, href, nm, hl in _LANG_LINKS)
    links = foot_links() if lang == "pt" else '<a href="/privacidade.html">%s</a>' % {"en": "Privacy Policy (in Portuguese)", "es": "Política de Privacidad (en portugués)"}[lang]
    st = (' style="%s"' % style) if style else ""
    return f"""<footer class="site-footer"{st}>
  <div class="wrap" style="text-align:center;">
    <img class="logo" src="/assets/logo-branco.png" alt="Dorgival Neto" style="margin:0 auto 16px;">
    <div class="foot-social">{icons}</div>
    <p class="foot-addr">{t['addr']}<br>{INVISTA_END}</p>
    <div class="foot-lang"><span>{t['label']}</span><div>{flags}</div></div>
    <div class="foot-links"><!--FOOTLINKS-->{links}<!--/FOOTLINKS--></div>
    <div class="foot-bottom"><div>© Dorgival Neto Negócios Imobiliários Ltda.</div><div>CRECI 17191-F | CNAI 52963</div><div>{t['rights']}</div></div>
  </div>
</footer>"""


def page(title, desc, path, body, scripts="", extra_head="", active="", lang="pt-BR", nav_html=None, foot_html=None, home_href="/", fab_msg=None, **seo):
    return f"""<!doctype html>
<html lang="{lang}">
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
    <a href="{home_href}"><img class="logo" src="/assets/logo-branco.png" alt="Dorgival Neto"></a>
    <nav class="nav-links" id="navLinks">
      {nav_html or nav_inner(active)}
    </nav>
    <button class="nav-toggle" onclick="document.getElementById('navLinks').classList.toggle('open')">☰</button>
  </div>
</header>

{body}

<a id="fabWa" class="fab-wa" href="{wa_link(fab_msg or 'Olá Dorgival! Vim pelo site e gostaria de falar com você.')}" target="_blank" rel="noopener">💬 WhatsApp</a>

{foot_html or footer_html()}

{CORE_JS}
{scripts}
</body>
</html>
"""


# ------------------------------------------------------------------ cards estáticos (bairro / semelhantes)
def card_static(p):
    chips = "".join('<span class="card-chip">%s</span>' % esc(c) for c in invest_chips(p))
    tr = excl_tag(p) + "".join('<span class="card-track">%s</span>' % TRILHA[t] for t in p.get("trilhas", []))
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
    <div class="card-actions">{('<a class="btn btn-gold btn-sm" data-book="' + p['id'] + '" href="' + wa_imovel(p) + '" target="_blank" rel="noopener">Agendar apresentação</a><a class="btn btn-outline btn-sm" href="' + u + '">Ver detalhes</a>') if has_book(p) else '<a class="btn btn-gold btn-sm" href="' + u + '">Ver detalhes</a>'}</div>
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
    if p.get("quartos") and p.get("suites") != p.get("quartos"): specs.append(("Quartos", p["quartos"]))  # todos suítes: mostra só "Suítes"
    if p.get("suites"): specs.append(("Suítes", p["suites"]))
    specs.append(("Banheiros", p.get("banheiros", 0)))
    if p.get("vagas"): specs.append(("Vagas", p["vagas"]))
    specs += [("Área útil", num(p.get("areaUtil", 0)) + " m²"), ("Área total", num(p.get("areaTotal", 0)) + " m²")]
    specs_html = "".join('<div class="spec"><div class="v">%s</div><div class="k">%s</div></div>' % (v, k) for k, v in specs)
    diffs = "".join('<span class="chip">%s</span>' % esc(d) for d in p.get("diferenciais", []))
    tr = excl_tag(p) + "".join('<span class="card-track">%s</span>' % TRILHA[t] for t in p.get("trilhas", []))
    inv = p.get("investimento") or {}
    inv_rows = []
    for k, label in (("entrega", "Entrega"), ("entrada", "Entrada"), ("parcela", "Parcelas"), ("posicao", "Posição"), ("pagamento", "Pagamento")):
        if inv.get(k): inv_rows.append("<li><b>%s:</b> %s</li>" % (label, esc(inv[k])))
    if inv.get("unidadeRef"): inv_rows.append("<li><i>* %s.</i></li>" % esc(inv["unidadeRef"]))
    inv_html = ('<div class="p-section"><h2>Condições</h2><ul style="padding-left:20px;line-height:1.9;">%s</ul></div>' % "".join(inv_rows)) if inv_rows else ""
    cond = ('<div class="p-sub">Condomínio: %s</div>' % money(p["condominio"])) if p.get("condominio") else ""
    if has_book(p):
        wa_btn = '<a class="btn btn-gold" data-book="%s" href="%s" target="_blank" rel="noopener">💬 Agendar apresentação</a>' % (p["id"], wa_imovel(p))
    else:
        wa_btn = '<a class="btn btn-gold" href="%s" target="_blank" rel="noopener">💬 Falar no WhatsApp</a>' % wa_imovel(p)
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
        {wa_btn}
        {'<a class="btn btn-outline" href="/simulador/?imovel=' + p['codigo'] + '">📈 Simular investimento</a>' if has_book(p) else ''}
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
    desc = "%d imóvel(is) à venda no %s, em João Pessoa, selecionados por Dorgival Neto (CRECI 17191-F). Veja fotos, valores e fale direto com o corretor." % (len(lst), b)
    others = "".join('<a class="tab" href="/bairro/%s/">%s</a>' % (slugify(x), esc(x)) for x in BAIRROS if x != b)
    body = f"""<div class="wrap" style="padding-top:34px;padding-bottom:70px;">
  <div class="crumbs" style="padding-top:0;"><a href="/">Início</a> › <a href="/imoveis.html">Imóveis</a> › {esc(b)}</div>
  <span class="eyebrow" style="display:block;margin-top:14px;">Bairro</span>
  <h1 style="font-size:32px;margin-top:6px;">Imóveis à venda no {esc(b)}, João Pessoa</h1>
  <p style="color:var(--gray);margin-top:8px;font-size:14.5px;max-width:640px;">Veja os imóveis disponíveis no bairro {esc(b)} selecionados por Dorgival Neto (CRECI 17191-F). Todos têm código de referência: é só citá-lo ao falar comigo.</p>
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
        <div><label>Tipo de imóvel</label><select name="tipo_imovel" data-req="o tipo de imóvel" required><option value="" selected disabled>Selecione</option><option>Apartamento</option><option>Casa</option><option>Terreno</option><option>Sala comercial</option><option>Outro</option></select></div>
        <div><label>Finalidade</label><select name="finalidade" data-req="a finalidade da avaliação" required><option value="" selected disabled>Selecione</option><option>Venda</option><option>Compra</option><option>Garantia / financiamento</option><option>Revisão de impostos</option><option>Partilha / inventário</option><option>Processo judicial</option><option>Outra</option></select></div>
      </div>
      <label>Bairro / cidade do imóvel</label><input name="localizacao" type="text" placeholder="Ex.: Bessa, João Pessoa" data-req="o bairro e a cidade do imóvel" required>
      <label>Descrição do imóvel</label><textarea name="descricao_imovel" rows="3" style="min-height:0;" placeholder="Tamanho (m²), número de quartos, banheiros, vagas, estado de conservação..." data-req="a descrição do imóvel" required></textarea>
      <label>Informações adicionais (opcional)</label><input name="mensagem" type="text" placeholder="Prazo, situação do imóvel, outra informação importante...">

      <button class="btn btn-gold" type="submit" style="width:100%;justify-content:center;">Solicitar avaliação</button>
    </form>
  </div>
  <p style="font-size:12px;color:var(--gray);margin-top:12px;">Seus dados ficam só comigo — sem spam e sem mensagens automáticas.</p>
</div>"""
    js = LEAD_JS.replace("__ORIGEM__", "avaliacao").replace("__WAMSG__", "Olá Dorgival! Acabei de pedir uma avaliação de imóvel pelo site.")
    return page("Avaliação de Imóveis em João Pessoa — Laudo Técnico NBR 14.653 | Dorgival Neto",
                "Perícia e avaliação de imóveis em João Pessoa com laudo técnico baseado na NBR 14.653, por Perito Avaliador CNAI 52963. Para venda, compra, garantia, impostos, partilha ou processos.",
                "/avaliacao.html", body, ITI_JS + "\n" + js, extra_head=ITI_CSS, active="/avaliacao.html")


def corretor_parceiro_page():
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
                "/corretor-parceiro.html", body, ITI_JS + "\n" + js, extra_head=ITI_CSS, active="")


# ------------------------------------------------------------------ parceiros de serviços (/parceiros/)
def par_msg(par, servico=None):
    return "Olá, %s! Vim através da indicação do corretor Dorgival Neto, pela página de parceiros do site dorgivalneto.com.br. %sGostaria de pedir um orçamento." % (
        par["nome"], ("Preciso de: %s. " % servico) if servico else "")


def par_wa(par, servico=None):
    from urllib.parse import quote
    return "https://wa.me/%s?text=%s" % (par["whatsapp"], quote(par_msg(par, servico), safe=""))


def par_card(par):
    u = "/parceiros/%s/" % par["slug"]
    cats = "".join('<span class="card-chip">%s</span>' % esc(c) for c in par["categorias"])
    return f"""<article class="card par-card" data-cats="{esc('|'.join(par['categorias']))}">
  <a class="par-photo" href="{u}"><img src="/{par['logo']}" alt="Logomarca {esc(par['nome'])}" loading="lazy"></a>
  <div class="card-body">
    <a class="card-title" href="{u}">{esc(par['nome'])}</a>
    <div class="par-slogan">{esc(par['slogan'])}</div>
    <div class="card-loc" style="margin-top:6px;">📍 {esc(par['atendimento'])}</div>
    <div class="par-cats">{cats}</div>
    <div class="card-actions"><a class="btn btn-wa btn-sm" data-partner="{par['slug']}" href="{par_wa(par)}" target="_blank" rel="noopener">💬 WhatsApp</a><a class="btn btn-outline btn-sm" href="{u}">Ver parceiro</a></div>
  </div>
</article>"""


PAR_NOTE = "Os parceiros são profissionais que atendem os meus clientes. Orçamento, prazo e execução do serviço são combinados diretamente entre você e o profissional."


def parceiros_index_page():
    cats = []
    for par in PARCEIROS:
        for c in par["categorias"]:
            if c not in cats:
                cats.append(c)
    tabs = ""
    if len(cats) > 1:
        tabs = '<div class="tabs" id="parTabs" style="justify-content:flex-start;"><button type="button" class="tab active" data-cat="">Todos</button>%s</div>' % "".join(
            '<button type="button" class="tab" data-cat="%s">%s</button>' % (esc(c), esc(c)) for c in cats)
    ask = wa_link("Olá Dorgival! Vi sua página de parceiros e estou procurando um profissional na área de ...")
    join = wa_link("Olá Dorgival! Eu vi o seu site e gostaria de fazer parte da sua página de parceiros. Eu presto serviços de ...")
    body = f"""<div class="wrap" style="padding-top:34px;padding-bottom:70px;">
  <div class="crumbs" style="padding-top:0;"><a href="/">Início</a> › Parceiros</div>
  <span class="eyebrow" style="display:block;margin-top:14px;">Parceiros</span>
  <h1 style="font-size:34px;margin-top:6px;">Profissionais para cuidar do seu imóvel</h1>
  <p style="color:var(--gray);margin-top:8px;font-size:14.5px;max-width:680px;line-height:1.7;">Quem compra, vende, reforma ou aluga um imóvel sempre precisa de bons profissionais por perto. Reuni aqui os parceiros que atendem os meus clientes: é só escolher e chamar direto no WhatsApp, já com uma mensagem pronta me citando como indicação.</p>
  {tabs}
  <div class="grid" id="parGrid">{''.join(par_card(p) for p in PARCEIROS)}</div>
  <p class="par-note">{PAR_NOTE}</p>
  <div class="par-cta">
    <div><h3>Não achou o profissional que precisa?</h3><p>Me conte o que você procura que eu indico alguém. E se você presta serviços para o mercado imobiliário e quer fazer parte desta página, fale comigo.</p></div>
    <div class="acts"><a class="btn btn-gold btn-sm" href="{ask}" target="_blank" rel="noopener">Pedir uma indicação</a><a class="btn btn-outline-gold btn-sm" href="{join}" target="_blank" rel="noopener">Quero ser parceiro</a></div>
  </div>
</div>"""
    js = r"""<script>
(function(){
  var tabs = document.querySelectorAll('#parTabs .tab'), cards = document.querySelectorAll('#parGrid .par-card');
  tabs.forEach(function(t){ t.onclick = function(){
    tabs.forEach(function(x){ x.classList.toggle('active', x === t); });
    var c = t.getAttribute('data-cat');
    cards.forEach(function(el){ el.style.display = (!c || el.getAttribute('data-cats').split('|').indexOf(c) > -1) ? '' : 'none'; });
    if (c) DN.track('parceiros_filtro', { categoria: c });
  }; });
  document.querySelectorAll('[data-partner]').forEach(function(a){ a.addEventListener('click', function(){ DN.track('parceiro_whatsapp', { parceiro: a.getAttribute('data-partner'), origem: 'lista' }); }); });
})();
</script>"""
    ld = {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "Início", "item": BASE + "/"},
        {"@type": "ListItem", "position": 2, "name": "Parceiros", "item": BASE + "/parceiros/"}]}
    return page("Parceiros de Serviços para o seu Imóvel em João Pessoa | Dorgival Neto",
                "Eletricista, montador de móveis, bombeiro hidráulico e outros profissionais que atendem os clientes de Dorgival Neto em João Pessoa. Chame direto no WhatsApp.",
                "/parceiros/", body, js, active="/parceiros/", jsonld=[ld])


def parceiro_page(par):
    path = "/parceiros/%s/" % par["slug"]
    cover = "/" + par["logo"]
    picks = "".join('<button type="button" class="tab" aria-pressed="false" data-s="%s"><span class="mark">+</span>%s</button>' % (esc(c), esc(c)) for c in par.get("opcoes", par["categorias"]))
    alt = "Serviços da %s: %s" % (par["nome"], "; ".join(par["servicos"]))
    others = [p for p in PARCEIROS if p["slug"] != par["slug"]]
    more = ('<div class="p-section" style="margin-bottom:70px;"><h2>Outros parceiros</h2><div class="grid">%s</div></div>' % "".join(par_card(p) for p in others[:3])) if others else ""
    body = f"""<div class="wrap">
  <div class="crumbs"><a href="/">Início</a> › <a href="/parceiros/">Parceiros</a> › {esc(par['nome'])}</div>
  <div class="par-grid">
    <aside class="par-side">
      <div class="par-photo"><img src="{cover}" alt="Logomarca {esc(par['nome'])}"></div>
      <div class="par-side-body">
        <span class="eyebrow">Parceiro</span>
        <h1>{esc(par['nome'])}</h1>
        <div class="par-slogan">{esc(par['slogan'])}</div>
        <p style="font-size:14.5px;line-height:1.7;color:#39383a;margin-top:12px;">{esc(par['resumo'])}</p>
        <span class="par-label">Atendimento</span>
        <div style="font-size:14.5px;margin-top:4px;">📍 {esc(par['atendimento'])}</div>
        <div class="par-pickbox">
          <div class="par-pick-title">👇 Escolha os serviços que você precisa</div>
          <div class="par-pick-hint">Você pode marcar mais de uma opção. Elas vão já escritas na sua mensagem de WhatsApp (opcional).</div>
          <div class="par-pick" id="parPick">{picks}</div>
        </div>
        <div class="par-actions">
          <a class="btn btn-wa" id="parWa" data-partner="{par['slug']}" href="{par_wa(par)}" target="_blank" rel="noopener" style="justify-content:center;">💬 Chamar no WhatsApp · {esc(par['whatsappExibicao'])}</a>
          <button type="button" class="btn btn-outline btn-sm" id="parShare" style="justify-content:center;">↗ Compartilhar este parceiro</button>
        </div>
        <p class="par-note">{PAR_NOTE}</p>
      </div>
    </aside>
    <div>
      <a class="par-flyer" href="/{par['imagemServicos']}" target="_blank" rel="noopener" title="Abrir a imagem em tamanho maior"><img src="/{par['imagemServicos']}" alt="{esc(alt)}"></a>
    </div>
  </div>
  {more}
</div>"""
    js = """<script>
(function(){
  var PAR = __PAR__, sel = [];
  var wa = document.getElementById('parWa');
  function lista(){
    return sel.length > 1 ? sel.slice(0, -1).join(', ') + ' e ' + sel[sel.length - 1] : sel.join('');
  }
  function msg(){
    return 'Olá, ' + PAR.nome + '! Vim através da indicação do corretor Dorgival Neto, pela página de parceiros do site dorgivalneto.com.br. ' + (sel.length ? 'Preciso de: ' + lista() + '. ' : '') + 'Gostaria de pedir um orçamento.';
  }
  var tabs = document.querySelectorAll('#parPick .tab');
  tabs.forEach(function(t){ t.onclick = function(){
    var s = t.getAttribute('data-s'), i = sel.indexOf(s);
    if (i > -1) sel.splice(i, 1); else sel.push(s);
    sel = Array.prototype.map.call(tabs, function(x){ return x.getAttribute('data-s'); }).filter(function(v){ return sel.indexOf(v) > -1; });
    tabs.forEach(function(x){
      var on = sel.indexOf(x.getAttribute('data-s')) > -1;
      x.classList.toggle('active', on); x.setAttribute('aria-pressed', on ? 'true' : 'false'); x.firstChild.textContent = on ? '✓' : '+';
    });
    wa.href = 'https://wa.me/' + PAR.whatsapp + '?text=' + encodeURIComponent(msg());
  }; });
  wa.addEventListener('click', function(){ DN.track('parceiro_whatsapp', { parceiro: PAR.slug, servico: sel.length ? sel.join(', ') : 'geral', origem: 'pagina' }); });
  document.getElementById('parShare').onclick = function(){
    var url = location.origin + '/parceiros/' + PAR.slug + '/', data = { title: PAR.nome + ' — parceiro de Dorgival Neto', text: PAR.nome + ' — ' + PAR.slogan, url: url };
    DN.track('share', { item_id: PAR.slug, method: 'parceiro' });
    if (navigator.share) { navigator.share(data).catch(function(){}); return; }
    if (navigator.clipboard && navigator.clipboard.writeText) navigator.clipboard.writeText(url).then(function(){ DN.toast('Link copiado!'); }, function(){ window.prompt('Copie o link:', url); });
    else window.prompt('Copie o link:', url);
  };
})();
</script>""".replace("__PAR__", json.dumps({"slug": par["slug"], "nome": par["nome"], "slogan": par["slogan"], "whatsapp": par["whatsapp"]}, ensure_ascii=False))
    ld = [{
        "@context": "https://schema.org", "@type": "LocalBusiness", "name": par["nome"], "image": BASE + cover,
        "description": par["resumo"], "telephone": "+55 " + par["whatsappExibicao"], "url": BASE + path,
        "areaServed": {"@type": "City", "name": "João Pessoa"},
    }, {
        "@context": "https://schema.org", "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Início", "item": BASE + "/"},
            {"@type": "ListItem", "position": 2, "name": "Parceiros", "item": BASE + "/parceiros/"},
            {"@type": "ListItem", "position": 3, "name": par["nome"], "item": BASE + path},
        ],
    }]
    title = "%s — %s em João Pessoa | Parceiro de Dorgival Neto" % (par["nome"], par["slogan"].replace(" • ", ", ").title())
    desc = "%s Atendimento: %s. Chame direto no WhatsApp pela página de parceiros de Dorgival Neto." % (par["resumo"], par["atendimento"])
    return page(title, desc, path, body, js, active="/parceiros/", image=cover, jsonld=ld)


# ------------------------------------------------------------------ simulador de investimento
SIM_JS = r"""<script>
(function(){
  var CEN = [
    { nome: 'Conservador', occ: 0.50, val: 0.08 },
    { nome: 'Base', occ: 0.60, val: 0.10 },
    { nome: 'Otimista', occ: 0.70, val: 0.12 }
  ];
  var ADM = { temporada: 0.20, anual: 0.10 };
  var MONEY = ['simPreco', 'simDiaria', 'simAluguel', 'simCond', 'simIptu'];
  var $ = function(id){ return document.getElementById(id); };
  var used = false;
  // vindo da página de um imóvel (?imovel=AP0001), a mensagem de WhatsApp cita o imóvel
  var ref = (new URLSearchParams(location.search).get('imovel') || '').toUpperCase();
  var prop = PROPERTIES.filter(function(p){ return p.codigo === ref; })[0];

  function parse(v){
    var s = String(v == null ? '' : v).replace(/[^\d,.\-]/g, '');
    if (!s) return NaN;
    if (s.indexOf(',') > -1) s = s.replace(/\./g, '').replace(',', '.');
    else if ((s.match(/\./g) || []).length > 1 || /\.\d{3}$/.test(s)) s = s.replace(/\./g, '');
    return parseFloat(s);
  }
  function brl(v){ return (v < 0 ? '-' : '') + 'R$ ' + Math.abs(Math.round(v)).toLocaleString('pt-BR'); }
  function pct(v, d){ return (v * 100).toLocaleString('pt-BR', { minimumFractionDigits: d || 0, maximumFractionDigits: d == null ? 1 : d }) + '%'; }
  // máscara em reais: os dígitos digitados entram pela direita (ex.: 85075600 vira 850.756,00)
  function mask(el){
    var d = el.value.replace(/\D/g, '').replace(/^0+/, '');
    if (!d) { el.value = ''; return; }
    while (d.length < 3) d = '0' + d;
    el.value = d.slice(0, -2).replace(/\B(?=(\d{3})+(?!\d))/g, '.') + ',' + d.slice(-2);
  }
  function radio(name){ var r = document.querySelector('input[name="' + name + '"]:checked'); return r ? r.value : ''; }
  function anosTxt(a){ return (Math.round(a * 10) / 10).toLocaleString('pt-BR') + (a === 1 ? ' ano' : ' anos'); }

  function notes(loc, sit){
    var l = [];
    if (loc === 'anual') {
      l.push('<b>Aluguel:</b> recebido nos 12 meses do ano, sem vacância e sem reajuste durante o prazo.');
      l.push('<b>Administração:</b> 10% sobre o aluguel.');
      l.push('<b>Condomínio e IPTU:</b> na locação anual costumam ficar com o inquilino; só entram na conta se você preencher.');
    } else {
      l.push('<b>Ocupação:</b> 50% (conservador), 60% (base) e 70% (otimista) dos dias do ano.');
      l.push('<b>Administração:</b> 20% sobre a receita bruta.');
      l.push('<b>Diária:</b> valor informado, constante ao longo do prazo.');
    }
    l.push('<b>Valorização do imóvel:</b> 8% (conservador), 10% (base) e 12% (otimista) ao ano, sobre o preço de hoje.');
    if (sit === 'planta') l.push('<b>Entrega:</b> a renda só começa depois dos meses informados; a valorização conta desde a compra.');
    l.push('<b>Fora da conta:</b> imposto de renda, financiamento, correções e reajustes de valores.');
    l.push('<b>Referência:</b> os números são uma estimativa para orientar a conversa. Para valores e condições reais, agende uma apresentação.');
    l.push('Projeção não é promessa de rentabilidade.');
    return '<b>Premissas</b><ul>' + l.map(function(x){ return '<li>' + x + '</li>'; }).join('') + '</ul>';
  }

  function applyModes(){
    var loc = radio('simModo'), sit = radio('simSit');
    $('boxTemp').style.display = loc === 'temporada' ? '' : 'none';
    $('boxAnual').style.display = loc === 'anual' ? '' : 'none';
    $('simCustoHint').style.display = loc === 'anual' ? '' : 'none';
    $('boxPlanta').style.display = sit === 'planta' ? '' : 'none';
    $('simCond').placeholder = $('simIptu').placeholder = loc === 'anual' ? 'Opcional' : 'Preencha para um resultado fiel';
    document.querySelectorAll('.sim-modo label').forEach(function(l){ l.classList.toggle('on', l.querySelector('input').checked); });
    $('simNote').innerHTML = notes(loc, sit);
  }

  function calc(){
    var loc = radio('simModo'), sit = radio('simSit'), anual = loc === 'anual', planta = sit === 'planta';
    var preco = parse($('simPreco').value), valor = parse($(anual ? 'simAluguel' : 'simDiaria').value);
    var cond = parse($('simCond').value), iptu = parse($('simIptu').value);
    var anos = parseInt($('simAnos').value, 10);
    var meses = planta ? Math.max(0, parseInt($('simMeses').value, 10) || 0) : 0;
    var out = $('simTabela'), warn = $('simWarn'), cta = $('simCta');
    if (!(preco > 0) || !(valor > 0)) {
      out.innerHTML = '<p class="sim-note" style="margin:0;">' + (anual ? 'Informe o preço do imóvel e o aluguel mensal para ver a projeção.' : 'Informe o preço do imóvel e a diária média para ver a projeção.') + '</p>';
      warn.classList.remove('on'); cta.style.display = 'none';
      return;
    }
    var avisos = [];
    var semCustos = !anual && (isNaN(cond) || isNaN(iptu));
    if (semCustos) avisos.push('⚠ Condomínio e/ou IPTU não preenchidos: esses custos foram considerados como R$ 0, então o resultado abaixo pode estar acima do real. Preencha os campos para uma projeção mais fiel.');
    if (planta && !(meses > 0)) avisos.push('⚠ Meses até a entrega não informados: a renda foi contada desde o início, então o resultado pode estar acima do real.');
    warn.innerHTML = avisos.join('<br>');
    warn.classList.toggle('on', avisos.length > 0);
    var custos = (isNaN(cond) ? 0 : cond) * 12 + (isNaN(iptu) ? 0 : iptu);

    var adm = ADM[loc];
    var anosRenda = Math.max(0, anos - meses / 12);
    var rows = CEN.map(function(c){
      var bruta = anual ? valor * 12 : valor * 365 * c.occ, ad = bruta * adm, liq = bruta - ad - custos;
      var fut = preco * Math.pow(1 + c.val, anos), valoriz = fut - preco;
      var renda = liq * anosRenda, ganho = valoriz + renda;
      return { c: c, bruta: bruta, adm: ad, liq: liq, y: liq / preco, fut: fut, valoriz: valoriz, vp: valoriz / preco,
               renda: renda, rp: renda / preco, ganho: ganho, ret: ganho / preco };
    });
    function line(label, fn, cls, neg){
      return '<tr' + (cls ? ' class="' + cls + '"' : '') + '><td>' + label + '</td>' + rows.map(function(r){
        var v = fn(r); return '<td' + (neg && neg(r) ? ' class="neg"' : '') + '>' + v + '</td>';
      }).join('') + '</tr>';
    }
    out.innerHTML = '<table class="sim-table"><thead><tr><th></th>' + CEN.map(function(c){ return '<th>' + c.nome + '</th>'; }).join('') + '</tr></thead><tbody>' +
      (anual ? '' : line('Ocupação da diária', function(r){ return pct(r.c.occ); })) +
      line(anual ? 'Aluguel por ano (12 meses)' : 'Receita bruta por ano', function(r){ return brl(r.bruta); }) +
      line('Administração (' + pct(adm) + ')', function(r){ return '-' + brl(r.adm).replace('-', ''); }) +
      line(anual ? 'Condomínio + IPTU por ano (a seu cargo)' : 'Condomínio + IPTU por ano', function(r){ return semCustos && !custos ? 'não informado' : (custos ? '-' + brl(custos).replace('-', '') : brl(0)); }) +
      line('Renda líquida por ano', function(r){ return brl(r.liq); }, 'key', function(r){ return r.liq < 0; }) +
      line('Rendimento líquido sobre o preço', function(r){ return pct(r.y, 1) + ' a.a.'; }, '', function(r){ return r.y < 0; }) +
      line('Valorização do imóvel', function(r){ return pct(r.c.val) + ' a.a.'; }) +
      line('Valor estimado do imóvel em ' + anosTxt(anos), function(r){ return brl(r.fut); }, 'key') +
      line('Valorização acumulada', function(r){ return brl(r.valoriz); }) +
      line('Valorização acumulada sobre o preço', function(r){ return pct(r.vp, 1); }) +
      line('Renda acumulada (' + anosTxt(anosRenda) + ' de renda)', function(r){ return brl(r.renda); }, '', function(r){ return r.renda < 0; }) +
      line('Renda acumulada sobre o preço', function(r){ return pct(r.rp, 1); }, '', function(r){ return r.rp < 0; }) +
      line('Ganho total estimado', function(r){ return brl(r.ganho); }, 'key', function(r){ return r.ganho < 0; }) +
      line('Retorno total sobre o preço', function(r){ return pct(r.ret, 1); }, 'key', function(r){ return r.ret < 0; }) +
      '</tbody></table>';
    var base = rows[1], site = (window.SITE_CONFIG && SITE_CONFIG.siteUrl) || location.origin;
    cta.style.display = '';
    cta.href = DN.wa('Olá Dorgival! Fiz uma simulação de investimento no seu site' + (prop ? ' para o imóvel ' + prop.codigo + ' (' + prop.titulo + ')' : '') + ': preço ' + brl(preco) + ', ' + (anual ? 'locação anual com aluguel de ' + brl(valor) + ' por mês' : 'locação por temporada com diária de ' + brl(valor)) + ', prazo ' + anos + ' anos. No cenário base deu ganho de ' + brl(base.ganho) + '. Gostaria de agendar uma apresentação do empreendimento e receber informações sobre os valores de investimento.' + (prop ? ' ' + site + DN.url(prop) : ''));
    if (!used) { used = true; DN.track('simulador_uso', { item_id: prop ? prop.id : 'geral', modo: loc, situacao: sit }); }
  }

  document.querySelectorAll('input[name="simModo"], input[name="simSit"]').forEach(function(r){ r.addEventListener('change', function(){ applyModes(); calc(); }); });
  MONEY.forEach(function(id){ $(id).addEventListener('input', function(){ mask($(id)); calc(); }); });
  $('simMeses').addEventListener('input', function(){ $('simMeses').value = $('simMeses').value.replace(/\D/g, ''); calc(); });
  $('simAnos').addEventListener('change', calc);
  applyModes(); calc();
})();
</script>"""


def simulador_page():
    body = f"""<div class="article" style="max-width:1000px;">
  <span class="eyebrow">Investimento</span>
  <h1>Simulador de investimento</h1>
  <p>Veja, em três cenários, quanto um imóvel alugado por temporada (diária) ou por locação anual (aluguel mensal) pode render em renda e valorização ao longo dos anos. Ajuste os números e compare.</p>
  <div class="sim-disclaimer">⚠ Projeção não é promessa de rentabilidade. <span>Os resultados abaixo são simulações com premissas hipotéticas de diária, ocupação e valorização. O mercado pode ter desempenho diferente do projetado, inclusive com perda. Não é recomendação de investimento nem garantia de retorno — confirme valores e condições antes de decidir.</span></div>
  <div class="sim-grid">
    <form class="form-dark" id="simForm" onsubmit="return false;" autocomplete="off">
      <label>Preço do imóvel (R$)</label><input id="simPreco" type="text" inputmode="numeric" placeholder="0,00">
      <label>Situação do imóvel</label>
      <div class="sim-modo" id="simSitBox">
        <label class="on"><input type="radio" name="simSit" value="planta" checked> Na planta ou em construção</label>
        <label><input type="radio" name="simSit" value="pronto"> Pronto</label>
      </div>
      <div id="boxPlanta">
        <label>Meses até a entrega (sem renda)</label><input id="simMeses" type="text" inputmode="numeric" placeholder="Ex.: 36">
        <div class="sim-hint">Imóvel na planta só gera renda depois da entrega. Nesse período a renda não conta, mas a valorização sim.</div>
      </div>
      <label>Tipo de locação</label>
      <div class="sim-modo" id="simModo">
        <label class="on"><input type="radio" name="simModo" value="temporada" checked> Locação por temporada</label>
        <label><input type="radio" name="simModo" value="anual"> Locação anual (aluguel mensal)</label>
      </div>
      <div id="boxTemp">
        <label>Diária média (R$)</label><input id="simDiaria" type="text" inputmode="numeric" placeholder="Informe a diária média">
        <div class="sim-hint">A diária varia muito conforme a região, o bairro e o tipo de empreendimento. Use a sua pesquisa de mercado ou peça uma estimativa a mim.</div>
      </div>
      <div id="boxAnual" style="display:none;">
        <label>Aluguel mensal (R$)</label><input id="simAluguel" type="text" inputmode="numeric" placeholder="Informe o aluguel mensal">
        <div class="sim-hint">Valor do aluguel do contrato anual. A simulação considera o imóvel alugado nos 12 meses do ano, sem vacância.</div>
      </div>
      <label>Condomínio (R$ por mês)</label><input id="simCond" type="text" inputmode="numeric" placeholder="Preencha para um resultado fiel">
      <label>IPTU (R$ por ano)</label><input id="simIptu" type="text" inputmode="numeric" placeholder="Preencha para um resultado fiel">
      <div class="sim-hint" id="simCustoHint" style="display:none;">Na locação anual, condomínio e IPTU costumam ficar por conta do inquilino. Preencha só se forem custo seu.</div>
      <label>Prazo da análise</label>
      <select id="simAnos"><option value="3">3 anos</option><option value="5" selected>5 anos</option><option value="7">7 anos</option><option value="10">10 anos</option></select>
    </form>
    <div>
      <div class="sim-result">
        <div class="sim-warn" id="simWarn"></div>
        <div id="simTabela"></div>
        <div class="sim-note" id="simNote"></div>
      </div>
      <p style="margin-top:18px;"><a class="btn btn-gold" id="simCta" target="_blank" rel="noopener" href="#">💬 Agendar apresentação e simulação personalizada</a></p>
    </div>
  </div>
</div>"""
    return page("Simulador de Investimento Imobiliário em João Pessoa — Renda e Valorização | Dorgival Neto",
                "Simule o retorno de um imóvel em João Pessoa, por temporada ou locação anual, em três cenários (conservador, base e otimista): renda e valorização. Projeção, não promessa de rentabilidade.",
                "/simulador/", body, SIM_JS, active="/simulador/")


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


def post_cta(c):
    """Quadro escuro no fim da notícia, apontando para a seção do site ligada ao assunto (campo 'cta' em posts.json)."""
    for k in ("title", "text", "label", "href"):
        assert c.get(k), "cta sem %s" % k
    second = ('<a class="btn btn-outline-gold" href="%s">%s</a>' % (c["href2"], esc(c["label2"]))) if c.get("href2") else ""
    return ('<div class="form-dark" style="text-align:center;margin-top:40px;"><h3 style="color:#fff;font-size:22px;">%s</h3>'
            '<p style="color:#cfcdc6;margin-top:8px;font-size:14px;">%s</p>'
            '<div style="display:flex;flex-wrap:wrap;gap:10px;justify-content:center;margin-top:18px;"><a class="btn btn-gold" href="%s">%s</a>%s</div></div>') % (esc(c["title"]), esc(c["text"]), c["href"], esc(c["label"]), second)


def mercado_pages(posts):
    out = {}
    cards = "".join('<a class="post-card" href="/mercado/%s/"><div class="meta" style="margin:0 0 6px;color:var(--gray);font-size:12px;">%s</div><h3>%s</h3><p>%s</p></a>' % (
        p["slug"], pt_date(p["date"]), esc(p["title"]), esc(p["description"])) for p in sorted(posts, key=lambda x: x["date"], reverse=True))
    body = f"""<div class="article" style="max-width:880px;">
  <span class="eyebrow">Notícias e Mercado</span>
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
               "image": BASE + p.get("image", "/assets/og-image.jpg")}
        fig = ""
        if p.get("image"):
            assert os.path.exists(os.path.join(ROOT, p["image"].lstrip("/"))), p["image"]
            fig = '<figure class="post-fig"><img src="%s" alt="%s" width="%s" height="%s"></figure>' % (
                p["image"], esc(p.get("imageAlt", p["title"])), p.get("imageW", ""), p.get("imageH", ""))
        body = f"""<article class="article">
  <div class="crumbs" style="padding-top:0;"><a href="/mercado/">Notícias e Mercado</a> › {esc(p['title'])}</div>
  <h1>{esc(p['title'])}</h1>
  <div class="meta">Por Dorgival Neto · {pt_date(p['date'])}</div>
  {fig}{p['body']}
  {post_cta(p['cta'])}
</article>"""
        out["mercado/%s/index.html" % p["slug"]] = page(p["title"] + " | Dorgival Neto", p["description"], path, body, active="/mercado/", og_type="article", jsonld=[art],
                                                  image=p.get("image", "/assets/og-image.jpg"))
    return out


# ------------------------------------------------------------------ páginas escritas à mão
STATIC = {
    "index.html": dict(
        path="/", active="/", alternates=True,
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
    "sameAs": [INSTAGRAM, LINKEDIN],
}


HOME_ALTS = [("pt-BR", "/"), ("en", "/en/"), ("es", "/es/"), ("x-default", "/")]


def home_i18n(lang):
    """Gera /en/ e /es/ a partir do index.html (texto em português trocado pelas traduções de tools/i18n_home.py)."""
    import i18n_home as I
    col = {"en": 1, "es": 2}[lang]
    ui = I.UI[lang]
    h = read("index.html").replace("\r\n", "\n")
    a = h.index('<section class="hero"')
    b = h.index("<!-- MODAL GUIA -->")
    body = h[a:b]
    # sem o guia em PDF (só existe em português) nem o atalho para ele
    body = re.sub(r"<!-- GUIA DE COMPRA -->.*?</section>\n\n", "", body, count=1, flags=re.S)
    body, n = re.subn(r'\s*<a class="btn btn-outline" href="joao-pessoa.html#guiaJP">[^<]*</a>', "", body)
    assert n == 1, "atalho do guia de João Pessoa não encontrado"
    # caminhos absolutos (as páginas ficam em /en/ e /es/)
    for old, new in (('src="assets/', 'src="/assets/'), ('poster="assets/', 'poster="/assets/'), ('href="imoveis.html"', 'href="/imoveis.html"'),
                     ('href="joao-pessoa.html"', 'href="/joao-pessoa.html"'), ('href="depoimento.html"', 'href="/depoimento.html"')):
        assert old in body, old
        body = body.replace(old, new)
    # depoimentos (traduzidos do original), na ordem
    cards = list(re.finditer(r'(<div class="testi-card">.*?<p>)(.*?)(</p>)', body, flags=re.S))
    assert len(cards) == len(I.QUOTES), (len(cards), len(I.QUOTES))
    for m, q in reversed(list(zip(cards, I.QUOTES))):
        body = body[:m.start(2)] + q[col - 1] + body[m.end(2):]
    for row in I.REPLACE:
        pt, tr = row[0], row[col]
        assert pt in body, "texto da home mudou; tradução órfã: " + pt[:70]
        body = body.replace(pt, tr)
    h2t = {"en": "Testimonials from Clients and Partners</h2>", "es": "Testimonios de Clientes y Aliados</h2>"}[lang]
    assert h2t in body
    body = body.replace(h2t, h2t + '\\n    <p class="center" style="color:var(--gray);font-size:12.5px;margin-top:8px;">%s</p>' % ui["testi_note"], 1)
    body = body.replace('<a class="btn btn-gold" href="/imoveis.html">%s</a>' % ("View all properties" if lang == "en" else "Ver todos los inmuebles"),
                        '<a class="btn btn-gold" href="/imoveis.html">%s</a>\n      <p style="color:var(--gray);font-size:12.5px;margin-top:14px;">%s</p>' % (
                            "View all properties" if lang == "en" else "Ver todos los inmuebles", ui["pt_note"]), 1)
    # script: carrossel e vitrine copiados da home em português, com os rótulos traduzidos
    js = h[h.index("let teaserCarousel = null;"):h.index("applyContact();\ninitPhoneInput();")]
    for old, new in (("'Ir para '", "'%s'" % ui["carousel"][0]), ("'imóvel')", "'%s')" % ui["carousel"][1])):
        assert old in js, old
        js = js.replace(old, new)
    tail = """
function applyContact(){
  const wa = SITE_CONFIG.whatsapp;
  const link = m => `https://wa.me/${wa}?text=${encodeURIComponent(m)}`;
  document.getElementById('fabWa').href = link(%s);
  document.getElementById('ctaWaBtn').href = link(%s);
  const svc = %s;
  svc.forEach((m, i) => { const el = document.getElementById('svcWa' + (i + 1)); if (el) el.href = link(m); });
}
applyContact();
initCarousel('testiTrack', 'testiPrev', 'testiNext', 'testiDots', %s);
renderTeaser();
""" % (json.dumps(ui["fab_msg"], ensure_ascii=False), json.dumps(ui["fab_msg"], ensure_ascii=False),
       json.dumps(ui["svc"], ensure_ascii=False), json.dumps(ui["carousel"][2], ensure_ascii=False))
    scripts = "<script>\n" + js + tail + "</script>"
    nav = "\n      ".join('<a href="%s"%s>%s</a>' % (href, ' style="color:var(--gold);"' if i == 0 else "", label) for i, (href, label) in enumerate(ui["nav"]))
    nav += '\n      <a class="nav-cta" href="#contato">%s</a>' % ui["cta"]
    path = "/%s/" % lang
    alts = [("pt-BR", "/"), ("en", "/en/"), ("es", "/es/"), ("x-default", "/")]
    return page(ui["title"], ui["desc"], path, body, scripts, lang=ui["lang"], nav_html=nav, foot_html=footer_html(lang=lang),
                home_href=path, fab_msg=ui["fab_msg"], locale=ui["locale"], alternates=alts, jsonld=[AGENT_LD])


def patch_static(fname, cfg):
    h = read(fname)
    h = re.sub(r"<title>.*?</title>", "<title>%s</title>" % esc(cfg["title"]), h, count=1, flags=re.S)
    h = re.sub(r'[ \t]*<meta name="description" content="[^"]*">\r?\n', "", h)
    h = re.sub(r"<!-- SEO:start -->.*?<!-- SEO:end -->\r?\n", "", h, flags=re.S)
    alts = HOME_ALTS if cfg.get("alternates") else None
    block = seo_block(cfg["title"], cfg["desc"], cfg["path"], noindex=cfg.get("noindex", False), jsonld=[AGENT_LD] if cfg.get("jsonld") else None, alternates=alts)
    m = re.search(r'<meta name="viewport"[^>]*>\r?\n', h)
    h = h[:m.end()] + block + h[m.end():]
    # nav
    h = re.sub(r'(<nav class="nav-links" id="navLinks">).*?(</nav>)', lambda mm: mm.group(1) + "\n      " + nav_inner(cfg["active"]) + "\n    " + mm.group(2), h, count=1, flags=re.S)
    # rodapé
    mf = re.search(r'<footer class="site-footer"([^>]*)>', h)
    sty = re.search(r'style="([^"]*)"', mf.group(1))
    h = re.sub(r'<footer class="site-footer"[^>]*>.*?</footer>', lambda mm: footer_html(sty.group(1) if sty else ""), h, count=1, flags=re.S)
    # scripts de análise e comportamentos comuns (menu)
    if 'assets/analytics.js' not in h and '/assets/analytics.js' not in h:
        inc = ""
        if 'assets/data.js' not in h and '/assets/data.js' not in h:
            inc += '<script src="/assets/data.js"></script>\n'
        inc += '<script src="/assets/analytics.js"></script>\n'
        h = h.replace("</body>", inc + "</body>", 1)
    if 'assets/site.js' not in h:
        h = h.replace("</body>", '<script src="/assets/site.js"></script>\n</body>', 1)
    write(fname, h)


def main():
    for fname, cfg in STATIC.items():
        patch_static(fname, cfg)

    urls = [("/", "1.0"), ("/imoveis.html", "0.9"), ("/joao-pessoa.html", "0.7"), ("/avaliacao.html", "0.8"),
            ("/corretor-parceiro.html", "0.5"), ("/parceiros/", "0.7"), ("/mercado/", "0.7"), ("/simulador/", "0.7"), ("/en/", "0.6"), ("/es/", "0.6"), ("/privacidade.html", "0.2")]
    for par in PARCEIROS:
        write("parceiros/%s/index.html" % par["slug"], parceiro_page(par))
        urls.append(("/parceiros/%s/" % par["slug"], "0.6"))
    for p in PROPS:
        write("imovel/%s/index.html" % p["codigo"], property_page(p))
        urls.append(("/imovel/%s/" % p["codigo"], "0.9"))
    for b in BAIRROS:
        write("bairro/%s/index.html" % slugify(b), bairro_page(b))
        urls.append(("/bairro/%s/" % slugify(b), "0.8"))
    write("avaliacao.html", avaliacao_page())
    write("corretor-parceiro.html", corretor_parceiro_page())
    write("parceiros/index.html", parceiros_index_page())
    write("simulador/index.html", simulador_page())
    for lg in ("en", "es"):
        write("%s/index.html" % lg, home_i18n(lg))
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
        olds = [p["id"], p["codigo"].lower()] + [old for old, new in {**OLD_CODES, **OLD_IDS}.items() if new == p["codigo"]]
        for o in dict.fromkeys(olds):
            for s in ("/imovel/%s" % o, "/imovel/%s/" % o):
                redirects.append({"source": s, "destination": dest, "permanent": True})
    # a página de corretores parceiros mudou de /parceiros.html para /corretor-parceiro.html
    redirects.append({"source": "/parceiros.html", "destination": "/corretor-parceiro.html", "permanent": True})
    vercel = {"functions": {"api/send-guia.js": {"includeFiles": "api/_files/*.pdf"}}, "redirects": redirects}
    write("vercel.json", json.dumps(vercel, indent=2) + "\n")
    print("ok: %d imóveis, %d bairros, %d posts, %d urls no sitemap" % (len(PROPS), len(BAIRROS), len(posts), len(urls)))


if __name__ == "__main__":
    main()
