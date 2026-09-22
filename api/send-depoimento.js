const nodemailer = require('nodemailer');

function escapeHtml(str) {
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

module.exports = async (req, res) => {
  if (req.method !== 'POST') {
    res.status(405).json({ error: 'method not allowed' });
    return;
  }

  const { nome, sobrenome, whatsapp, texto, arquivo } = req.body || {};

  if (!nome || !sobrenome || !whatsapp || !texto) {
    res.status(400).json({ error: 'dados invalidos' });
    return;
  }

  const MAX_FILE_BYTES = 3 * 1024 * 1024;
  let attachments;
  if (arquivo && arquivo.dataBase64) {
    const buffer = Buffer.from(arquivo.dataBase64, 'base64');
    if (buffer.length > MAX_FILE_BYTES) {
      res.status(400).json({ error: 'arquivo muito grande' });
      return;
    }
    attachments = [{
      filename: arquivo.filename || 'anexo',
      content: buffer,
      contentType: arquivo.contentType || 'application/octet-stream'
    }];
  }

  if (!process.env.GMAIL_USER || !process.env.GMAIL_APP_PASSWORD) {
    console.error('send-depoimento: GMAIL_USER/GMAIL_APP_PASSWORD nao configurados');
    res.status(500).json({ error: 'credenciais de e-mail nao configuradas' });
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
      from: `Site Dorgival Neto <${process.env.GMAIL_USER}>`,
      to: process.env.GMAIL_USER,
      subject: `Novo depoimento no site: ${nome} ${sobrenome}`,
      html: `
        <p><b>Nome:</b> ${escapeHtml(nome)} ${escapeHtml(sobrenome)}</p>
        <p><b>WhatsApp:</b> ${escapeHtml(whatsapp)}</p>
        <p><b>Depoimento:</b></p>
        <p>${escapeHtml(texto).replace(/\n/g, '<br>')}</p>
        ${attachments ? '<p><i>Anexo incluído nesta mensagem.</i></p>' : ''}
      `,
      attachments
    });

    res.status(200).json({ ok: true });
  } catch (err) {
    console.error('send-depoimento: falha ao enviar e-mail', err);
    res.status(500).json({ error: 'falha ao enviar e-mail' });
  }
};
