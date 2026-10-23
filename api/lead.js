const { appendLead } = require('./_sheet');

const ORIGENS = ['avaliacao', 'parceiro'];

function clip(v, max) {
  return typeof v === 'string' ? v.trim().slice(0, max) : '';
}

module.exports = async (req, res) => {
  if (req.method !== 'POST') {
    res.status(405).json({ error: 'method not allowed' });
    return;
  }

  const { origem, nome, whatsapp, detalhes } = req.body || {};

  if (!ORIGENS.includes(origem) || !clip(nome, 120) || !clip(whatsapp, 30)) {
    res.status(400).json({ error: 'dados invalidos' });
    return;
  }

  const ok = await appendLead({
    origem,
    nome: clip(nome, 120),
    whatsapp: clip(whatsapp, 30),
    detalhes: clip(detalhes, 1500)
  });

  res.status(200).json({ ok });
};
