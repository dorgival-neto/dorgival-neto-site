/* ============================================================
   DADOS DO SITE — Dorgival Neto Imóveis
   Para adicionar/editar imóveis, peça ao Claude para atualizar
   este arquivo com os dados do novo imóvel.

   Campos de cada imóvel:
   - id: nome interno do imóvel (favoritos e comparador) — não mude depois
   - codigo: prefixo do tipo + 4 dígitos em ordem crescente por tipo, ex.: AP0001.
     Prefixos: AP apartamento, FL flat, TE terreno, CA casa, SL sala comercial,
     CO cobertura, GD garden. É também o endereço da página (/imovel/AP0001/) e o
     nome da pasta das fotos (assets/imoveis/AP0001/): não mude depois de divulgar
   - exclusivo (opcional): true mostra a tag "Exclusividade" (imóvel só meu).
     Nos demais, NÃO cite nome do empreendimento, construtora, arquiteto, rua,
     número da unidade ou pontos de referência exatos (evita captação por terceiros)
   - categoria: tipo do imóvel ("Apartamento", "Sala comercial"...), combina com o prefixo
   - trilhas: ["investir"], ["morar"] ou as duas
   - investimento (opcional): aPartirDe (true/false), entrega, entrada,
     parcela, posicao, pagamento — só aparece o que estiver preenchido
   - simulador (opcional): diaria (R$), condominio (R$/mês), iptu (R$/ano) —
     valores iniciais do simulador de investimento (/simulador/); o imóvel
     só aparece lá se tiver este campo. Deixe condominio/iptu null se ainda
     não souber: o visitante preenche e o simulador avisa se ficar vazio.
   ============================================================ */

const SITE_CONFIG = {
  whatsapp: "5583996336569",       // Dorgival Neto — número oficial
  instagram: "https://instagram.com/dorgivalneto.imoveis",
  email: "dorgivalneto.corretor@gmail.com",
  ga4Id: "G-8GRWXGK9C0",           // Google Analytics 4 (conta dorgivalneto.corretor@gmail.com)
  pixelId: ""                      // ex.: "1234567890" (Meta Pixel)
};
window.SITE_CONFIG = SITE_CONFIG;  // catalog.js e analytics.js leem por window

const PROPERTIES = [
  {
    id: "ap0001",
    codigo: "AP0001",
    categoria: "Apartamento",
    trilhas: ["investir", "morar"],
    investimento: {
      aPartirDe: true,
      pagamento: "Fluxo de pagamento facilitado",
      unidadeRef: "Preço e metragem da unidade de 2 quartos (66,43m²)"
    },
    simulador: { diaria: null, condominio: null, iptu: null },
    titulo: "Lançamento 2 quartos com varanda integrada — Bessa",
    tipo: "Venda",
    status: "Lançamento",
    bairro: "Bessa",
    cidade: "João Pessoa",
    preco: 850756,
    areaUtil: 66.43,
    areaTotal: 66.43,
    quartos: 2,
    suites: 1,
    banheiros: 2,
    descricao: "Lançamento no coração do Bessa — perto de praia, restaurantes, bares, shopping, farmácias e mercados. Unidades com varanda integrada e suíte master. Estrutura completa de lazer: piscina, deck, solarium, academia, espaço kids, cinema, salão de festas, espaços gourmet, espaço wine, lounge de convivência, salão de jogos, coworking e bicicletário. * Preço e área referentes a uma unidade de 66,43m² (2 quartos, sendo 1 suíte master). Fluxo de pagamento facilitado direto com a construtora.",
    diferenciais: ["Lançamento","Varanda integrada","Suíte master","Piscina","Academia","Espaço gourmet","Cinema","Coworking","Pagamento facilitado"],
    fotos: [
      "assets/imoveis/AP0001/fachada-01.jpg",
      "assets/imoveis/AP0001/sala.jpg",
      "assets/imoveis/AP0001/cozinha.jpg",
      "assets/imoveis/AP0001/recepcao-01.jpg",
      "assets/imoveis/AP0001/recepcao-02.jpg",
      "assets/imoveis/AP0001/academia-01.jpg",
      "assets/imoveis/AP0001/academia-02.jpg",
      "assets/imoveis/AP0001/gourmet-01.jpg",
      "assets/imoveis/AP0001/gourmet-02.jpg",
      "assets/imoveis/AP0001/winebar.jpg",
      "assets/imoveis/AP0001/lounge.jpg",
      "assets/imoveis/AP0001/salao-festas-01.jpg",
      "assets/imoveis/AP0001/salao-festas-02.jpg",
      "assets/imoveis/AP0001/cinema.jpg",
      "assets/imoveis/AP0001/salao-jogos.jpg",
      "assets/imoveis/AP0001/kids.jpg",
      "assets/imoveis/AP0001/coworking.jpg",
      "assets/imoveis/AP0001/bicicletario.jpg"
    ],
    destaque: true
  },
  {
    id: "bancarios-reformado",
    codigo: "AP0002",
    categoria: "Apartamento",
    trilhas: ["morar"],
    titulo: "Apartamento reformado 3 quartos — Bancários",
    tipo: "Venda",
    status: "Pronto para morar",
    bairro: "Bancários",
    cidade: "João Pessoa",
    preco: 597000,
    condominio: 550,
    areaUtil: 68,
    areaTotal: 68,
    quartos: 3,
    suites: 1,
    banheiros: 2,
    vagas: 2,
    descricao: "Apartamento totalmente reformado no bairro dos Bancários, com móveis planejados em todos os ambientes, projeto de iluminação especial e fechadura eletrônica. Um dos quartos foi transformado em closet, mas pode voltar a ser dormitório. Próximo a parque, padarias, restaurantes, supermercados e farmácias. Condomínio com piscina, academia, salões de festa, quadra poliesportiva, playground e portaria 24h.",
    diferenciais: ["Reformado","Móveis planejados","Fechadura eletrônica","Piscina","Academia","Portaria 24h"],
    fotos: [
      "assets/imoveis/AP0002/20260912_100759.jpg",
      "assets/imoveis/AP0002/20260912_100808.jpg",
      "assets/imoveis/AP0002/20260912_100817.jpg",
      "assets/imoveis/AP0002/20260912_100825.jpg",
      "assets/imoveis/AP0002/20260912_100935.jpg",
      "assets/imoveis/AP0002/20260912_101034.jpg",
      "assets/imoveis/AP0002/20260912_100953.jpg",
      "assets/imoveis/AP0002/20260912_101006.jpg",
      "assets/imoveis/AP0002/20260824_172956.jpg",
      "assets/imoveis/AP0002/20260824_172946.jpg"
    ],
    destaque: true
  },
  {
    id: "bancarios-69m2",
    codigo: "AP0003",
    exclusivo: true,
    categoria: "Apartamento",
    trilhas: ["morar"],
    titulo: "Apartamento 3 quartos com varanda — Bancários",
    tipo: "Venda",
    status: "Pronto para morar",
    bairro: "Bancários",
    cidade: "João Pessoa",
    preco: 437000,
    areaUtil: 68,
    areaTotal: 68,
    quartos: 3,
    suites: 1,
    banheiros: 2,
    vagas: 1,
    descricao: "Excelente apartamento de 68m² de área privativa, com 3 quartos (1 suíte), sala para dois ambientes com varanda e cozinha integrada com móveis planejados. Uma ótima opção para quem busca conforto, praticidade e uma estrutura completa de lazer em uma das regiões mais consolidadas de João Pessoa. Próximo a parque, com fácil acesso a padarias, restaurantes, supermercados, colégios, farmácias, academias, shopping, centros universitários e demais serviços da região. Condomínio com piscina adulto e infantil, 2 espaços gourmet, 2 salões de festas, quadra poliesportiva, salão de jogos, academia, playground, espaço kids, mini mercado, bicicletários, espaço de estudos e portaria 24h. * Disponibilidade e valores sujeitos a alteração sem aviso prévio.",
    diferenciais: ["Varanda","Cozinha planejada","Blindex nos banheiros","Aceita financiamento","Piscina","Academia","Portaria 24h"],
    fotos: [
      "assets/imoveis/AP0003/piscina.jpg",
      "assets/imoveis/AP0003/sala-tv.jpg",
      "assets/imoveis/AP0003/sala-cozinha.jpg",
      "assets/imoveis/AP0003/cozinha.jpg",
      "assets/imoveis/AP0003/quarto.jpg",
      "assets/imoveis/AP0003/banheiro.jpg",
      "assets/imoveis/AP0003/vista.jpg",
      "assets/imoveis/AP0003/lounge.jpg",
      "assets/imoveis/AP0003/lazer.jpg"
    ],
    destaque: true
  },
  {
    id: "sala-jardim-oceania",
    codigo: "SL0001",
    categoria: "Sala comercial",
    trilhas: ["investir"],
    titulo: "Sala comercial 27m² porteira fechada — Jardim Oceania",
    tipo: "Venda",
    status: "Porteira fechada",
    bairro: "Jardim Oceania",
    cidade: "João Pessoa",
    preco: 360000,
    areaUtil: 27,
    areaTotal: 27,
    quartos: 0,
    suites: 0,
    banheiros: 1,
    descricao: "Sala comercial de 27m² no Jardim Oceania, entregue porteira fechada: projetada, com 2 estações de trabalho, cadeiras, mesas, mesa de reunião, ar-condicionado, fechadura digital, máquina de café e frigobar — é só chegar e começar a operar. A sala conta com banheiro privativo e o edifício tem elevador, portaria 12h durante o dia e portaria virtual à noite, com reconhecimento facial, além de vagas de garagem rotativas. Uma opção prática para quem quer abrir o escritório sem obra, ou investir em um espaço pronto para uso. Aceita financiamento bancário. * Disponibilidade e valores sujeitos a alteração sem aviso prévio.",
    diferenciais: ["Porteira fechada","Projetada","Ar-condicionado","Fechadura digital","Elevador","Portaria com reconhecimento facial","Garagem rotativa","Aceita financiamento"],
    fotos: [
      "assets/imoveis/SL0001/sala-reuniao.jpg",
      "assets/imoveis/SL0001/estacoes-trabalho.jpg",
      "assets/imoveis/SL0001/sala-reuniao-02.jpg",
      "assets/imoveis/SL0001/ambiente.jpg",
      "assets/imoveis/SL0001/estacoes-trabalho-02.jpg",
      "assets/imoveis/SL0001/estacao-copa.jpg",
      "assets/imoveis/SL0001/copa.jpg",
      "assets/imoveis/SL0001/copa-02.jpg",
      "assets/imoveis/SL0001/detalhe.jpg",
      "assets/imoveis/SL0001/wc.jpg"
    ],
    destaque: true
  },
  {
    id: "ap0004",
    codigo: "AP0004",
    categoria: "Apartamento",
    trilhas: ["morar"],
    titulo: "Apartamento 3 suítes e 145m² — Tambaú",
    tipo: "Venda",
    status: "Pronto para morar",
    bairro: "Tambaú",
    cidade: "João Pessoa",
    preco: 1780000,
    areaUtil: 145,
    areaTotal: 145,
    quartos: 3,
    suites: 3,
    banheiros: 4,
    vagas: 2,
    descricao: "O espaço de uma casa, a vista dos seus sonhos. Localizado em Tambaú, é um empreendimento único, inteligente e diferenciado, com localização privilegiada. Traz a comodidade e a sensação de morar em uma casa, com toda a segurança e a estrutura de um empreendimento de alto padrão. Além da exclusividade de ser um apartamento por andar, tem grandes esquadrias para ventilação e iluminação naturais, todos os quartos voltados para o leste e espaços amplos. São 145m² com 3 suítes (1 master), sala ampla para 2 ambientes, varanda gourmet, cozinha, lavabo, área de serviço e DCE completo (o cliente pode optar por não ter o DCE). O empreendimento tem 2 elevadores, sendo o social com acesso por biometria, áreas comuns com acesso por biometria, placas de energia solar para alimentar as áreas comuns, guarda-volumes, academia, piscina adulto e infantil, salão de festas, playground e snooker bar. * Disponibilidade e valores sujeitos a alteração sem aviso prévio.",
    diferenciais: ["Um apartamento por andar","3 suítes (1 master)","Varanda gourmet","DCE completo (opcional)","Quartos voltados para o leste","Elevador social com biometria","Energia solar nas áreas comuns","Piscina adulto e infantil","Academia","Snooker bar","Salão de festas","Playground","Guarda-volumes"],
    fotos: [
      "assets/imoveis/AP0004/sala-varanda.jpg",
      "assets/imoveis/AP0004/sala-cozinha.jpg",
      "assets/imoveis/AP0004/cozinha.jpg",
      "assets/imoveis/AP0004/varanda.jpg",
      "assets/imoveis/AP0004/suite-01.jpg",
      "assets/imoveis/AP0004/suite-02.jpg",
      "assets/imoveis/AP0004/suite-03.jpg",
      "assets/imoveis/AP0004/fachada-entrada.jpg",
      "assets/imoveis/AP0004/hall.jpg",
      "assets/imoveis/AP0004/piscina.jpg",
      "assets/imoveis/AP0004/academia.jpg",
      "assets/imoveis/AP0004/salao-festas.jpg",
      "assets/imoveis/AP0004/salao-festas-varanda.jpg",
      "assets/imoveis/AP0004/snooker-bar.jpg",
      "assets/imoveis/AP0004/playground.jpg",
      "assets/imoveis/AP0004/area-gourmet.jpg",
      "assets/imoveis/AP0004/area-externa.jpg"
    ],
    destaque: true
  }
];
