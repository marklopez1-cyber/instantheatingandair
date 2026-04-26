/* Instant Heating and Air — site enhancement script
   - Google Analytics 4 init (ID baked into <html data-ga="...">)
   - Mobile menu toggle
   - Modal open/close (Comfort Club signup, Get Estimate)
   - AJAX form submit so users stay on page
   - CTA click tracking (auto-routed to gtag if loaded)
*/
(function () {
  // ===== Google Analytics 4 =====
  // Reads the measurement ID from <html data-ga="G-XXXXXXXXXX">.
  // No inline script tags needed — keeps CSP script-src strict.
  const ga4Id = document.documentElement.getAttribute('data-ga');
  if (ga4Id) {
    window.dataLayer = window.dataLayer || [];
    window.gtag = function () { window.dataLayer.push(arguments); };
    window.gtag('js', new Date());
    window.gtag('config', ga4Id, {
      send_page_view: true,
      anonymize_ip: true
    });
  }

  // ===== Live Phoenix temperature =====
  // Free, no API key needed. Open-Meteo returns ~current temp in F.
  const tempChip = document.getElementById('phx-temp');
  const tempValue = document.getElementById('phx-temp-value');
  if (tempChip && tempValue && 'fetch' in window) {
    // Coordinates: Phoenix Sky Harbor International Airport (KPHX) —
    // the standard Phoenix weather reference station.
    const url = 'https://api.open-meteo.com/v1/forecast?latitude=33.4373&longitude=-112.0078&current=temperature_2m&temperature_unit=fahrenheit&timezone=America%2FPhoenix';
    fetch(url)
      .then((r) => (r.ok ? r.json() : Promise.reject('Weather fetch failed')))
      .then((data) => {
        const t = data && data.current && data.current.temperature_2m;
        if (typeof t !== 'number' || !isFinite(t)) return;
        const temp = Math.round(t);
        tempValue.textContent = temp;
        if (temp >= 95) tempChip.classList.add('temp-hot');
        else if (temp <= 50) tempChip.classList.add('temp-cold');
        tempChip.hidden = false;
      })
      .catch(() => {
        // Quietly stay hidden if the API fails — never block the page.
      });
  }

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

  // ===== AJAX form submit =====
  // Any form with class="ajax-form" submits via FormSubmit's AJAX endpoint —
  // user stays on the page, success state shown inline in the parent modal.
  // Falls back to standard form submit (with _next redirect) if fetch unavailable.
  function setupAjaxForm(form) {
    if (!('fetch' in window)) return;
    form.addEventListener('submit', (e) => {
      e.preventDefault();
      const btn = form.querySelector('button[type="submit"]');
      const orig = btn.textContent;
      btn.disabled = true;
      btn.textContent = 'Submitting\u2026';

      const data = new FormData(form);
      fetch('https://formsubmit.co/ajax/service@instantheatingandair.com', {
        method: 'POST',
        headers: { 'Accept': 'application/json' },
        body: data
      })
        .then((res) => res.json())
        .then((json) => {
          if (json && (json.success === true || json.success === 'true')) {
            form.style.display = 'none';
            const success = form.parentElement.querySelector('.modal-success');
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
  document.querySelectorAll('form.ajax-form').forEach(setupAjaxForm);

  // ===== Reviews carousel — auto-rotating, swipeable, accessible =====
  const reduceMotion = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  document.querySelectorAll('.reviews-carousel').forEach((carousel) => {
    const track = carousel.querySelector('.reviews-track');
    const prev = carousel.querySelector('.rev-prev');
    const next = carousel.querySelector('.rev-next');
    const autoplayMs = parseInt(carousel.dataset.autoplay || '0', 10);

    if (!track || track.children.length === 0) return;

    function step(direction) {
      const firstCard = track.children[0];
      if (!firstCard) return;
      const cardWidth = firstCard.offsetWidth;
      const gap = parseInt(getComputedStyle(track).gap || '20', 10);
      const stride = cardWidth + gap;
      // Advance a full "page" per rotation — number of cards currently visible.
      // Desktop = 3, tablet = 2, mobile = 1.
      const cardsInView = Math.max(1, Math.round(track.clientWidth / stride));
      const distance = cardsInView * stride;
      const maxScroll = track.scrollWidth - track.clientWidth;

      let target = track.scrollLeft + direction * distance;
      // Loop: if at/past end going forward, jump to start
      if (direction > 0 && track.scrollLeft >= maxScroll - 5) {
        target = 0;
      } else if (direction < 0 && track.scrollLeft <= 5) {
        target = maxScroll;
      }
      track.scrollTo({ left: target, behavior: 'smooth' });
    }

    let timer = null;
    function start() {
      if (autoplayMs <= 0 || reduceMotion) return;
      stop();
      timer = setInterval(() => step(1), autoplayMs);
    }
    function stop() {
      if (timer) { clearInterval(timer); timer = null; }
    }

    if (prev) prev.addEventListener('click', () => { step(-1); start(); });
    if (next) next.addEventListener('click', () => { step(1); start(); });

    // Pause on hover / focus / touch
    carousel.addEventListener('mouseenter', stop);
    carousel.addEventListener('mouseleave', start);
    track.addEventListener('focusin', stop);
    track.addEventListener('focusout', start);
    track.addEventListener('touchstart', stop, { passive: true });
    track.addEventListener('touchend', () => setTimeout(start, 4000), { passive: true });

    // Keyboard navigation when track is focused
    track.addEventListener('keydown', (e) => {
      if (e.key === 'ArrowRight') { e.preventDefault(); step(1); start(); }
      if (e.key === 'ArrowLeft')  { e.preventDefault(); step(-1); start(); }
    });

    start();
  });

  // ===== CTA click tracking (GA + GTM) =====
  document.addEventListener('click', (e) => {
    const t = e.target.closest('[data-track]');
    if (!t) return;
    const evt = t.getAttribute('data-track');
    if (window.gtag) window.gtag('event', evt, { event_category: 'engagement' });
    if (window.dataLayer) window.dataLayer.push({ event: evt });
  });
})();
