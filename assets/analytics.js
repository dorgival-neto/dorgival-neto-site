(function () {
  var cfg = window.SITE_CONFIG || {};
  var DN = (window.DN = window.DN || {});
  if (!DN.track) DN.track = function () {};

  var KEY = 'dn_consent';
  function getConsent() { try { return localStorage.getItem(KEY); } catch (e) { return null; } }
  function setConsent(v) { try { localStorage.setItem(KEY, v); } catch (e) {} }

  function loadTrackers() {
    if (cfg.ga4Id) {
      var s = document.createElement('script');
      s.async = true;
      s.src = 'https://www.googletagmanager.com/gtag/js?id=' + encodeURIComponent(cfg.ga4Id);
      document.head.appendChild(s);
      window.dataLayer = window.dataLayer || [];
      window.gtag = function () { window.dataLayer.push(arguments); };
      window.gtag('js', new Date());
      window.gtag('config', cfg.ga4Id);
    }

    if (cfg.pixelId) {
      !function (f, b, e, v, n, t, s) {
        if (f.fbq) return; n = f.fbq = function () { n.callMethod ? n.callMethod.apply(n, arguments) : n.queue.push(arguments); };
        if (!f._fbq) f._fbq = n; n.push = n; n.loaded = !0; n.version = '2.0'; n.queue = [];
        t = b.createElement(e); t.async = !0; t.src = v; s = b.getElementsByTagName(e)[0]; s.parentNode.insertBefore(t, s);
      }(window, document, 'script', 'https://connect.facebook.net/en_US/fbevents.js');
      window.fbq('init', cfg.pixelId);
      window.fbq('track', 'PageView');
    }
  }

  // Medição só começa depois do aceite (LGPD). Sem IDs configurados, nada é carregado nem perguntado.
  function showBanner() {
    var box = document.createElement('div');
    box.className = 'cookie-banner';
    box.setAttribute('role', 'dialog');
    box.setAttribute('aria-label', 'Aviso de cookies');
    box.innerHTML =
      '<p>Uso cookies de medição para entender como o site é usado e melhorar a sua experiência. ' +
      'Você pode aceitar ou recusar — o site funciona igual. <a href="/privacidade.html">Política de Privacidade</a></p>' +
      '<div class="cookie-actions"><button type="button" class="btn btn-gold btn-sm" data-c="granted">Aceitar</button>' +
      '<button type="button" class="btn btn-outline btn-sm" data-c="denied">Recusar</button></div>';
    box.addEventListener('click', function (e) {
      var v = e.target.getAttribute && e.target.getAttribute('data-c');
      if (!v) return;
      setConsent(v);
      box.remove();
      if (v === 'granted') loadTrackers();
    });
    document.body.appendChild(box);
  }

  if (cfg.ga4Id || cfg.pixelId) {
    var c = getConsent();
    if (c === 'granted') loadTrackers();
    else if (c !== 'denied') showBanner();
  }

  document.addEventListener('click', function (e) {
    var a = e.target.closest && e.target.closest('a[href*="wa.me"]');
    if (a && !a.hasAttribute('data-book')) {
      DN.track('whatsapp_click', { link_url: a.getAttribute('href') });
      if (window.fbq) window.fbq('track', 'Contact');
    }
  });

  // Usado pela página de privacidade para o visitante rever a escolha.
  DN.resetConsent = function () { try { localStorage.removeItem(KEY); } catch (e) {} location.reload(); };
})();
