/* AllYouCanWedding — statistiche (Google Analytics 4) e Pixel di Meta.
   Si attivano SOLO se il visitatore ha accettato i cookie (chiave aycw_cookie_consent = accepted). */
(function () {
  var GA_ID = 'G-XXXXXXXXXX';      // codice di misurazione Google Analytics 4
  var PIXEL_ID = '1465490775487753'; // ID del Pixel di Meta
  var KEY = 'aycw_cookie_consent';
  var loaded = false;

  function getConsent() { try { return localStorage.getItem(KEY); } catch (e) { return null; } }
  function setConsent(v) { try { localStorage.setItem(KEY, v); } catch (e) {} }

  function load() {
    if (loaded) return; loaded = true;
    if (GA_ID.indexOf('XXXX') < 0) {
      var s = document.createElement('script'); s.async = true;
      s.src = 'https://www.googletagmanager.com/gtag/js?id=' + GA_ID;
      document.head.appendChild(s);
      window.dataLayer = window.dataLayer || [];
      window.gtag = function () { dataLayer.push(arguments); };
      gtag('js', new Date());
      gtag('config', GA_ID, { anonymize_ip: true });
    }
    if (!/^0+$/.test(PIXEL_ID)) {
      !function (f, b, e, v, n, t, s) { if (f.fbq) return; n = f.fbq = function () { n.callMethod ? n.callMethod.apply(n, arguments) : n.queue.push(arguments) };
        if (!f._fbq) f._fbq = n; n.push = n; n.loaded = !0; n.version = '2.0'; n.queue = []; t = b.createElement(e); t.async = !0;
        t.src = v; s = b.getElementsByTagName(e)[0]; s.parentNode.insertBefore(t, s) }(window, document, 'script', 'https://connect.facebook.net/en_US/fbevents.js');
      fbq('init', PIXEL_ID); fbq('track', 'PageView');
    }
  }

  // Clic su email, WhatsApp o telefono = contatto
  document.addEventListener('click', function (ev) {
    var a = ev.target.closest && ev.target.closest('a[href]'); if (!a || !loaded) return;
    var h = a.getAttribute('href') || '', tipo = /^mailto:/i.test(h) ? 'email' : /wa\.me|whatsapp/i.test(h) ? 'whatsapp' : /^tel:/i.test(h) ? 'telefono' : '';
    if (!tipo) return;
    if (window.gtag) gtag('event', 'contatto', { metodo: tipo, pagina: location.pathname });
    if (window.fbq) fbq('track', 'Contact', { content_category: tipo });
  }, true);

  function banner() {
    var d = document.createElement('div');
    d.setAttribute('role', 'dialog'); d.setAttribute('aria-label', 'Consenso cookie');
    d.style.cssText = 'position:fixed;left:0;right:0;bottom:0;z-index:9999;background:#2a2e2a;color:#f7f3ee;padding:1rem 1.25rem;display:flex;flex-wrap:wrap;gap:.8rem;align-items:center;font:14px/1.5 Georgia,serif';
    d.innerHTML = '<p style="flex:1;min-width:240px;margin:0">Usiamo cookie tecnici e, con il tuo consenso, cookie di terze parti (Google Fonts, Google Analytics, Meta Pixel) per statistiche e per mostrarti i nostri annunci. <a href="cookie-policy.html" style="color:#b5c4b5">Cookie Policy</a></p>'
      + '<button type="button" data-v="accepted" style="background:#8a9e8a;color:#fff;border:0;padding:.6rem 1.2rem;cursor:pointer">Accetta</button>'
      + '<button type="button" data-v="declined" style="background:transparent;color:#f7f3ee;border:1px solid #b5c4b5;padding:.6rem 1.2rem;cursor:pointer">Rifiuta</button>';
    d.addEventListener('click', function (ev) {
      var v = ev.target.getAttribute && ev.target.getAttribute('data-v'); if (!v) return;
      setConsent(v); d.remove(); if (v === 'accepted') load();
    });
    document.body.appendChild(d);
  }

  var c = getConsent();
  if (c === 'accepted') load();
  var acc = document.getElementById('cookie-accept'); // banner della home
  if (acc) acc.addEventListener('click', load);
  else if (!c) banner();
})();
