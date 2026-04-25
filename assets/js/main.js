/* Instant Heating and Air — site enhancement script
   - Mobile menu toggle
   - Modal open/close (Comfort Club signup, etc.)
   - AJAX form submit so users stay on page
   - CTA click tracking
*/
(function () {
  // ===== Mobile menu =====
  const toggle = document.querySelector('.menu-toggle');
  const nav = document.getElementById('site-nav');
  if (toggle && nav) {
    toggle.addEventListener('click', () => {
      const open = nav.classList.toggle('open');
      toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
      toggle.textContent = open ? '\u2715' : '\u2630';
    });
  }

  // ===== Modal =====
  function openModal(m) {
    if (!m) return;
    m.setAttribute('aria-hidden', 'false');
    document.body.classList.add('modal-open');
    const firstField = m.querySelector('input:not([type="hidden"]), select, textarea');
    if (firstField) setTimeout(() => firstField.focus(), 60);
  }
  function closeModal(m) {
    if (!m) return;
    m.setAttribute('aria-hidden', 'true');
    document.body.classList.remove('modal-open');
  }
  document.addEventListener('click', (e) => {
    const opener = e.target.closest('[data-modal-open]');
    if (opener) {
      e.preventDefault();
      const id = opener.getAttribute('data-modal-open');
      openModal(document.getElementById(id));
      return;
    }
    const closer = e.target.closest('[data-modal-close]');
    if (closer) {
      e.preventDefault();
      closeModal(closer.closest('.modal'));
    }
  });
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
      document.querySelectorAll('.modal[aria-hidden="false"]').forEach(closeModal);
    }
  });

  // ===== Comfort Club AJAX submit =====
  // Posts to FormSubmit's AJAX endpoint so we stay on the page and show success inline.
  // Falls back to standard form submit (with _next redirect) if fetch is unavailable.
  const cf = document.getElementById('comfort-form');
  if (cf && 'fetch' in window) {
    cf.addEventListener('submit', (e) => {
      e.preventDefault();
      const btn = cf.querySelector('button[type="submit"]');
      const orig = btn.textContent;
      btn.disabled = true;
      btn.textContent = 'Submitting\u2026';

      const data = new FormData(cf);
      // Use FormSubmit's AJAX endpoint (no redirect, returns JSON)
      fetch('https://formsubmit.co/ajax/service@instantheatingandair.com', {
        method: 'POST',
        headers: { 'Accept': 'application/json' },
        body: data
      })
        .then((res) => res.json())
        .then((json) => {
          if (json && (json.success === true || json.success === 'true')) {
            // Hide form, show success state
            cf.style.display = 'none';
            const success = cf.parentElement.querySelector('.modal-success');
            if (success) success.hidden = false;
          } else {
            throw new Error((json && json.message) || 'Submission failed');
          }
        })
        .catch((err) => {
          alert('Sorry, something went wrong submitting the form: ' + err.message + '\n\nYou can also call us at (623) 352-9802.');
          btn.disabled = false;
          btn.textContent = orig;
        });
    });
  }

  // ===== CTA click tracking (GA + GTM) =====
  document.addEventListener('click', (e) => {
    const t = e.target.closest('[data-track]');
    if (!t) return;
    const evt = t.getAttribute('data-track');
    if (window.gtag) window.gtag('event', evt, { event_category: 'engagement' });
    if (window.dataLayer) window.dataLayer.push({ event: evt });
  });
})();
