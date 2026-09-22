/* ============================================================
   DADOS DO SITE — Dorgival Neto Imóveis
   Para adicionar/editar imóveis, peça ao Claude para atualizar
   este arquivo com os dados do novo imóvel. Fotos: use links
   diretos (Google Drive, Imgur, Postimages etc.)
   ============================================================ */

const SITE_CONFIG = {
  whatsapp: "5583996336569",       // Dorgival Neto — número oficial
  instagram: "https://instagram.com/dorgivalneto.imoveis",
  email: "dorgivalneto.corretor@gmail.com"
};

const PROPERTIES = [
  {
    id: "elevatto-bessa",
    titulo: "Elevatto — Lançamento no Bessa",
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
    descricao: "Lançamento assinado pelo Mookamboo Studio (arquiteto Augusto Magno) para a Nordeste Construções, no coração do Bessa — perto de praia, restaurantes, bares, shopping, farmácias e mercados. 148 unidades de 64m² a 148m², com varanda integrada e suíte master. Estrutura completa de lazer: piscina, deck, solarium, academia, espaço kids, cinema, salão de festas, espaços gourmet, espaço wine, lounge de convivência, salão de jogos, coworking e bicicletário. * Preço e área referentes à unidade 1404 (66,43m², 2 quartos com 1 suíte master). Fluxo de pagamento facilitado direto com a construtora.",
    diferenciais: ["Lançamento","Varanda integrada","Suíte master","Piscina","Academia","Espaço gourmet","Cinema","Coworking","Pagamento facilitado"],
    fotos: [
      "assets/imoveis/elevatto/fachada-01.jpg",
      "assets/imoveis/elevatto/sala.jpg",
      "assets/imoveis/elevatto/cozinha.jpg",
      "assets/imoveis/elevatto/recepcao-01.jpg",
      "assets/imoveis/elevatto/recepcao-02.jpg",
      "assets/imoveis/elevatto/academia-01.jpg",
      "assets/imoveis/elevatto/academia-02.jpg",
      "assets/imoveis/elevatto/gourmet-01.jpg",
      "assets/imoveis/elevatto/gourmet-02.jpg",
      "assets/imoveis/elevatto/winebar.jpg",
      "assets/imoveis/elevatto/lounge.jpg",
      "assets/imoveis/elevatto/salao-festas-01.jpg",
      "assets/imoveis/elevatto/salao-festas-02.jpg",
      "assets/imoveis/elevatto/cinema.jpg",
      "assets/imoveis/elevatto/salao-jogos.jpg",
      "assets/imoveis/elevatto/kids.jpg",
      "assets/imoveis/elevatto/coworking.jpg",
      "assets/imoveis/elevatto/bicicletario.jpg"
    ],
    destaque: true
  },
  {
    id: "bancarios-reformado",
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
    descricao: "Apartamento totalmente reformado no bairro dos Bancários, com móveis planejados em todos os ambientes, projeto de iluminação especial e fechadura eletrônica. Um dos quartos foi transformado em closet, mas pode voltar a ser dormitório. A 300m do Parque das Três Ruas, próximo a padarias, restaurantes, supermercados e farmácias. Condomínio com piscina, academia, salões de festa, quadra poliesportiva, playground e portaria 24h.",
    diferenciais: ["Reformado","Móveis planejados","Fechadura eletrônica","Piscina","Academia","Portaria 24h"],
    fotos: [
      "assets/imoveis/bancarios-802b/20260912_100759.jpg",
      "assets/imoveis/bancarios-802b/20260912_100808.jpg",
      "assets/imoveis/bancarios-802b/20260912_100817.jpg",
      "assets/imoveis/bancarios-802b/20260912_100825.jpg",
      "assets/imoveis/bancarios-802b/20260912_100935.jpg",
      "assets/imoveis/bancarios-802b/20260912_101034.jpg",
      "assets/imoveis/bancarios-802b/20260912_100953.jpg",
      "assets/imoveis/bancarios-802b/20260912_101006.jpg",
      "assets/imoveis/bancarios-802b/20260824_172956.jpg",
      "assets/imoveis/bancarios-802b/20260824_172946.jpg"
    ],
    destaque: true
  },
  {
    id: "bancarios-69m2",
    titulo: "Apartamento 3 quartos com varanda — Bancários",
    tipo: "Venda",
    status: "Pronto para morar",
    bairro: "Bancários",
    cidade: "João Pessoa",
    preco: 439000,
    areaUtil: 67,
    areaTotal: 69,
    quartos: 3,
    suites: 1,
    banheiros: 2,
    vagas: 1,
    descricao: "Excelente apartamento de 67m² de área privativa, com 3 quartos (1 suíte), sala para dois ambientes com varanda e cozinha integrada com móveis planejados. Uma ótima opção para quem busca conforto, praticidade e uma estrutura completa de lazer em uma das regiões mais consolidadas de João Pessoa. A 300m do Parque das Três Ruas, com fácil acesso a padarias, restaurantes, supermercados, colégios, farmácias, academias, Mangabeira Shopping, centros universitários e demais serviços da região. Condomínio com piscina adulto e infantil, 2 espaços gourmet, 2 salões de festas, quadra poliesportiva, salão de jogos, academia, playground, espaço kids, mini mercado, bicicletários, espaço de estudos e portaria 24h. * Disponibilidade e valores sujeitos a alteração sem aviso prévio.",
    diferenciais: ["Varanda","Cozinha planejada","Blindex nos banheiros","Aceita financiamento","Piscina","Academia","Portaria 24h"],
    fotos: [
      "assets/imoveis/bancarios-504b/sala-tv.jpg",
      "assets/imoveis/bancarios-504b/sala-cozinha.jpg",
      "assets/imoveis/bancarios-504b/cozinha.jpg",
      "assets/imoveis/bancarios-504b/quarto.jpg",
      "assets/imoveis/bancarios-504b/banheiro.jpg",
      "assets/imoveis/bancarios-504b/vista.jpg",
      "assets/imoveis/bancarios-504b/lounge.jpg",
      "assets/imoveis/bancarios-504b/lazer.jpg"
    ],
    destaque: true
  }
];
