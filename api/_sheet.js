// Registra o contato na planilha do Google (Apps Script) sem nunca derrubar o fluxo principal.
async function appendLead(lead) {
  const url = process.env.LEADS_WEBHOOK_URL;
  if (!url) return false;

  const ctrl = new AbortController();
  const timer = setTimeout(() => ctrl.abort(), 8000);
  try {
    const r = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'text/plain;charset=utf-8' },
      body: JSON.stringify(lead),
      redirect: 'follow',
      signal: ctrl.signal
    });
    return r.ok;
  } catch (err) {
    console.error('sheet: falha ao registrar contato', err);
    return false;
  } finally {
    clearTimeout(timer);
  }
}

module.exports = { appendLead };
