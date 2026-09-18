const nodemailer = require('nodemailer');
const fs = require('fs');
const path = require('path');

const GUIAS = {
  compra: { file: 'guia-compra-joao-pessoa.pdf', label: 'Como comprar um imóvel em João Pessoa com segurança' },
  cidade: { file: 'conhecendo-joao-pessoa.pdf', label: 'Conhecendo João Pessoa' }
};

function isValidEmail(v) {
  return typeof v === 'string' && /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(v);
}

module.exports = async (req, res) => {
  if (req.method !== 'POST') {
    res.status(405).json({ error: 'method not allowed' });
    return;
  }

  const { nome, email, guia } = req.body || {};
  const guiaInfo = GUIAS[guia];

  if (!nome || !isValidEmail(email) || !guiaInfo) {
    res.status(400).json({ error: 'dados invalidos' });
    return;
  }

  const filePath = path.join(process.cwd(), 'assets', guiaInfo.file);
  if (!fs.existsSync(filePath)) {
    res.status(500).json({ error: 'arquivo nao encontrado' });
    return;
  }

  try {
    const transporter = nodemailer.createTransport({
      service: 'gmail',
      auth: {
        user: process.env.GMAIL_USER,
        pass: process.env.GMAIL_APP_PASSWORD
      }
    });

    await transporter.sendMail({
      from: `Dorgival Neto <${process.env.GMAIL_USER}>`,
      to: email,
      subject: `Seu guia: ${guiaInfo.label}`,
      html: `
        <p>Olá, ${nome}!</p>
        <p>Segue em anexo o guia <b>${guiaInfo.label}</b>, como você pediu no site.</p>
        <p>Qualquer dúvida, me chame no WhatsApp.</p>
        <p>— Dorgival Neto</p>
      `,
      attachments: [{ filename: guiaInfo.file, path: filePath }]
    });

    res.status(200).json({ ok: true });
  } catch (err) {
    res.status(500).json({ error: 'falha ao enviar e-mail' });
  }
};
