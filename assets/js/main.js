/* Instant Heating and Air — minimal enhancement script
   - Mobile menu toggle
   - Defer any non-critical work
*/
(function () {
  const toggle = document.querySelector('.menu-toggle');
  const nav = document.getElementById('site-nav');
  if (toggle && nav) {
    toggle.addEventListener('click', () => {
      const open = nav.classList.toggle('open');
      toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
      toggle.textContent = open ? '✕' : '☰';
    });
  }

  // Track tel: and CTA clicks (wire up GA later)
  document.addEventListener('click', (e) => {
    const a = e.target.closest('a[data-track]');
    if (!a) return;
    const evt = a.getAttribute('data-track');
    if (window.gtag) window.gtag('event', evt, { event_category: 'engagement' });
    if (window.dataLayer) window.dataLayer.push({ event: evt });
  });
})();
