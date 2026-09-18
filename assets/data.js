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
    id: "urbi-mare",
    titulo: "Urbi Mare — Lançamento em Manaíra",
    tipo: "Venda",
    status: "Lançamento",
    bairro: "Manaíra",
    cidade: "João Pessoa",
    preco: 980000,
    condominio: 780,
    areaUtil: 88,
    areaTotal: 96,
    quartos: 3,
    suites: 1,
    banheiros: 2,
    vagas: 2,
    descricao: "Lançamento assinado pela arquiteta Leila Azzouz, a poucos metros da orla de Manaíra. Projeto pensado para quem busca qualidade de vida, lazer completo e valorização em uma das regiões mais desejadas de João Pessoa.",
    diferenciais: ["Vista mar parcial","Piscina","Academia","Salão de festas","Espaço gourmet","Playground"],
    fotos: [
      "https://images.unsplash.com/photo-1613977257363-707ba9348227?q=80&w=1200",
      "https://images.unsplash.com/photo-1512917774080-9991f1c4c750?q=80&w=1200"
    ],
    destaque: true
  },
  {
    id: "exemplo-cabo-branco",
    titulo: "Apartamento vista mar — Cabo Branco",
    tipo: "Venda",
    status: "Pronto para morar",
    bairro: "Cabo Branco",
    cidade: "João Pessoa",
    preco: 1250000,
    condominio: 950,
    areaUtil: 120,
    areaTotal: 135,
    quartos: 3,
    suites: 2,
    banheiros: 3,
    vagas: 2,
    descricao: "Apartamento amplo e reformado, com vista mar frontal, a poucos passos do calçadão de Cabo Branco. Prédio com infraestrutura completa de lazer.",
    diferenciais: ["Vista mar frontal","Reformado","Piscina","Segurança 24h"],
    fotos: [
      "https://images.unsplash.com/photo-1502672260266-1c1ef2d93688?q=80&w=1200",
      "https://images.unsplash.com/photo-1560184897-ae75f418493e?q=80&w=1200"
    ],
    destaque: true
  },
  {
    id: "exemplo-bessa",
    titulo: "Apartamento 2 quartos — Bessa",
    tipo: "Aluguel",
    status: "Pronto para morar",
    bairro: "Bessa",
    cidade: "João Pessoa",
    preco: 2400,
    condominio: 420,
    areaUtil: 65,
    areaTotal: 70,
    quartos: 2,
    suites: 0,
    banheiros: 1,
    vagas: 1,
    descricao: "Ótimo custo-benefício no Bessa, próximo a comércio, praia e vias de acesso. Ideal para quem busca praticidade no dia a dia.",
    diferenciais: ["Próximo à praia","Área de lazer","Portaria 24h"],
    fotos: [
      "https://images.unsplash.com/photo-1522708323590-d24dbb6b0267?q=80&w=1200"
    ],
    destaque: true
  }
];
