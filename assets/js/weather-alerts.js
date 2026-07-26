/* Instant Heating and Air — Live weather alert banner
 * ----------------------------------------------------
 * Fetches active National Weather Service alerts for Phoenix (33.4484,-112.0740),
 * picks the most severe active alert, and renders an eye-catching callout at
 * the top of the hero section. If no alerts are active, nothing is rendered
 * (zero layout impact).
 *
 * Why NWS?
 *   - Free, no API key
 *   - CORS-enabled (works from browser)
 *   - Authoritative for U.S. weather warnings
 *
 * Runs on any page that includes a <div id="wx-alerts"></div> mount point.
 */
(function () {
  'use strict';

  const MOUNT = document.getElementById('wx-alerts');
  if (!MOUNT) return;

  // Phoenix (downtown). NWS 'point' endpoint returns every alert whose polygon
  // covers this lat/lng — county, zone, marine, everything.
  const NWS_URL = 'https://api.weather.gov/alerts/active?point=33.4484,-112.0740';

  // sessionStorage cache — avoid re-hitting NWS on every SPA-ish navigation
  const CACHE_KEY = 'iha-wx-cache';
  const CACHE_MINUTES = 15;

  // Severity → visual rank (higher wins)
  const SEV_RANK = { Extreme: 4, Severe: 3, Moderate: 2, Minor: 1, Unknown: 0 };
  // Severity → CSS modifier class
  const SEV_CLASS = {
    Extreme: 'wx-alert--extreme',
    Severe:  'wx-alert--severe',
    Moderate:'wx-alert--moderate',
    Minor:   'wx-alert--minor',
    Unknown: 'wx-alert--minor'
  };

  // Best-guess icon + HVAC-relevant angle based on event name substrings.
  // Order matters: first match wins.
  const EVENT_PROFILE = [
    { match: /heat/i,              icon: '🌡️', pitch: 'Extreme heat pushes AC systems to their limit — if yours starts struggling, call us the moment it happens.' },
    { match: /freeze|frost|cold/i, icon: '❄️', pitch: 'Cold snaps spike heat-strip failures and frozen coils — we\'re standing by for same-day heating service.' },
    { match: /winter storm|snow|ice/i, icon: '🌨️', pitch: 'Winter storms strain heating systems — get your furnace or heat pump checked before it fails when you need it most.' },
    { match: /dust|blowing/i,      icon: '🌪️', pitch: 'Dust clogs filters and coils fast. If your AC struggled during the storm, a same-day tune-up will restore airflow.' },
    { match: /thunderstorm|lightning/i, icon: '⛈️', pitch: 'Lightning surges can fry capacitors and control boards — same-day diagnostic if your system won\'t start after the storm.' },
    { match: /flood/i,             icon: '🌊', pitch: 'If your outdoor unit was submerged, do NOT turn it back on — call us for a safety inspection first.' },
    { match: /wind|hurricane|tornado/i, icon: '💨', pitch: 'High winds can damage outdoor units and disconnects — we\'ll inspect and get you running fast.' },
    { match: /fire|smoke|red flag/i,  icon: '🔥', pitch: 'Smoke and ash overload air filters — swap yours and consider an IAQ check.' },
    { match: /fog/i,               icon: '🌫️', pitch: 'Reduced visibility on the roads — drive safe. We\'re here when you need us.' },
    { match: /air quality/i,       icon: '😷', pitch: 'Poor air quality is a good time to check your indoor filters and consider an air purifier upgrade.' },
    { match: /.*/,                 icon: '⚠️', pitch: 'Stay safe out there. We\'re standing by if you need us.' }
  ];

  // Phone number pulled from the topbar link — keeps one source of truth
  // (build/data/site.py). Returns null if no tel: link is found, in which
  // case we skip rendering the call button rather than ship a stale number.
  function getPhone() {
    const a = document.querySelector('a[href^="tel:"]');
    if (!a) return null;
    return {
      href: a.getAttribute('href'),
      display: (a.textContent || '').replace(/[^\d\s().-]/g, '').trim() || 'Call now'
    };
  }

  // ---- Fetch + cache ------------------------------------------------------

  function readCache() {
    try {
      const raw = sessionStorage.getItem(CACHE_KEY);
      if (!raw) return null;
      const obj = JSON.parse(raw);
      const ageMs = Date.now() - (obj.ts || 0);
      if (ageMs > CACHE_MINUTES * 60 * 1000) return null;
      return obj.data;
    } catch (_) { return null; }
  }

  function writeCache(data) {
    try {
      sessionStorage.setItem(CACHE_KEY, JSON.stringify({ ts: Date.now(), data }));
    } catch (_) { /* private mode, quota — silently ignore */ }
  }

  function fetchAlerts() {
    const cached = readCache();
    if (cached) return Promise.resolve(cached);
    // NWS asks for a User-Agent but the browser sets its own — that's fine,
    // they still serve requests. `Accept` picks the GeoJSON representation.
    return fetch(NWS_URL, { headers: { 'Accept': 'application/geo+json' } })
      .then(r => r.ok ? r.json() : Promise.reject('NWS ' + r.status))
      .then(json => {
        writeCache(json);
        return json;
      });
  }

  // ---- Alert selection ----------------------------------------------------

  function pickAlerts(json) {
    const features = (json && json.features) || [];
    // Dedupe by event name (NWS often issues near-duplicates across overlapping zones)
    const seen = new Set();
    const alerts = [];
    features.forEach(f => {
      const p = f.properties || {};
      const key = (p.event || '') + '|' + (p.severity || '');
      if (seen.has(key)) return;
      seen.add(key);
      // Skip if the user has dismissed this one this session
      if (sessionStorage.getItem('wx-dismissed-' + (p.id || key))) return;
      alerts.push({
        id: p.id || key,
        event: p.event || 'Weather Alert',
        severity: p.severity || 'Unknown',
        headline: p.headline || '',
        description: p.description || '',
        instruction: p.instruction || '',
        ends: p.ends || p.expires || '',
        senderName: p.senderName || 'National Weather Service',
        url: (f.id) || '',
        areaDesc: p.areaDesc || ''
      });
    });
    // Sort: most severe first
    alerts.sort((a, b) => (SEV_RANK[b.severity] || 0) - (SEV_RANK[a.severity] || 0));
    return alerts;
  }

  function profileFor(event) {
    for (let i = 0; i < EVENT_PROFILE.length; i++) {
      if (EVENT_PROFILE[i].match.test(event)) return EVENT_PROFILE[i];
    }
    return EVENT_PROFILE[EVENT_PROFILE.length - 1];
  }

  // ---- Rendering ----------------------------------------------------------

  function fmtEnds(iso) {
    if (!iso) return '';
    try {
      const d = new Date(iso);
      if (isNaN(d.getTime())) return '';
      const opts = { weekday: 'short', hour: 'numeric', minute: '2-digit', timeZone: 'America/Phoenix' };
      return 'In effect until ' + d.toLocaleString('en-US', opts) + ' MST';
    } catch (_) { return ''; }
  }

  function esc(s) {
    return String(s || '').replace(/[&<>"']/g, ch => ({
      '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
    })[ch]);
  }

  function cleanNwsText(s) {
    // NWS uses hard newlines inside paragraphs and * bullets — normalize to
    // spaces + real line breaks so the description reads cleanly in HTML.
    return String(s || '')
      .replace(/\r/g, '')
      .replace(/\n\n+/g, '\n\n')      // collapse runs of blank lines
      .split('\n\n')                   // split on paragraph breaks
      .map(p => p.replace(/\n/g, ' ')) // join intra-paragraph line-wraps
      .join('\n\n')
      .trim();
  }

  function render(alerts) {
    if (!alerts.length) {
      MOUNT.innerHTML = '';
      return;
    }

    const phone = getPhone();
    let idx = 0;

    function draw() {
      const a = alerts[idx];
      const prof = profileFor(a.event);
      const sevClass = SEV_CLASS[a.severity] || 'wx-alert--minor';
      const endsTxt = fmtEnds(a.ends);
      const desc = cleanNwsText(a.description);
      const instr = cleanNwsText(a.instruction);
      const descHtml = desc
        ? desc.split('\n\n').map(p => `<p>${esc(p)}</p>`).join('')
        : '';
      const instrHtml = instr
        ? `<div class="wx-alert__instruction"><strong>What to do:</strong> ${esc(instr).replace(/\n\n/g, '<br>')}</div>`
        : '';

      const pagerHtml = alerts.length > 1
        ? `<div class="wx-alert__pager">
             <button type="button" class="wx-alert__nav wx-alert__prev" aria-label="Previous alert">‹</button>
             <span class="wx-alert__count">${idx + 1} of ${alerts.length}</span>
             <button type="button" class="wx-alert__nav wx-alert__next" aria-label="Next alert">›</button>
           </div>`
        : '';

      MOUNT.innerHTML = `
        <div class="wx-alert ${sevClass}" role="alert" data-severity="${esc(a.severity)}">
          <div class="wx-alert__inner">
            <div class="wx-alert__icon" aria-hidden="true">${prof.icon}<span class="wx-alert__pulse"></span></div>
            <div class="wx-alert__body">
              <div class="wx-alert__title">
                <strong>${esc(a.event)}</strong>
                <span class="wx-alert__badge" title="Issued by ${esc(a.senderName)}">NWS</span>
                ${endsTxt ? `<span class="wx-alert__meta">· ${esc(endsTxt)}</span>` : ''}
              </div>
              <div class="wx-alert__pitch">${esc(prof.pitch)}</div>
            </div>
            <div class="wx-alert__actions">
              ${phone ? `<a class="wx-alert__cta" href="${esc(phone.href)}" data-track="wx_alert_call">
                <span aria-hidden="true">📞</span> Call ${esc(phone.display)}
              </a>` : ''}
              <button type="button" class="wx-alert__more" aria-expanded="false">Details</button>
              <button type="button" class="wx-alert__dismiss" aria-label="Dismiss this alert">×</button>
            </div>
          </div>
          <div class="wx-alert__detail" hidden>
            ${descHtml}
            ${instrHtml}
            <div class="wx-alert__source">Source: ${esc(a.senderName)}${a.areaDesc ? ' · ' + esc(a.areaDesc) : ''}</div>
          </div>
          ${pagerHtml}
        </div>`;

      // Wire up interactions -------------------------------------------------
      const root = MOUNT.querySelector('.wx-alert');
      if (!root) return;

      // Details toggle
      const moreBtn = root.querySelector('.wx-alert__more');
      const detail = root.querySelector('.wx-alert__detail');
      if (moreBtn && detail) {
        moreBtn.addEventListener('click', () => {
          const isOpen = detail.hasAttribute('hidden') === false;
          if (isOpen) {
            detail.setAttribute('hidden', '');
            moreBtn.setAttribute('aria-expanded', 'false');
            moreBtn.textContent = 'Details';
          } else {
            detail.removeAttribute('hidden');
            moreBtn.setAttribute('aria-expanded', 'true');
            moreBtn.textContent = 'Hide details';
          }
        });
      }

      // Dismiss (session-scoped so a new alert still shows next visit)
      const dismissBtn = root.querySelector('.wx-alert__dismiss');
      if (dismissBtn) {
        dismissBtn.addEventListener('click', () => {
          try { sessionStorage.setItem('wx-dismissed-' + a.id, '1'); } catch (_) {}
          // Remove this alert from the queue and either show the next or clear
          alerts.splice(idx, 1);
          if (!alerts.length) { MOUNT.innerHTML = ''; return; }
          if (idx >= alerts.length) idx = alerts.length - 1;
          draw();
        });
      }

      // Pager
      const prev = root.querySelector('.wx-alert__prev');
      const next = root.querySelector('.wx-alert__next');
      if (prev) prev.addEventListener('click', () => { idx = (idx - 1 + alerts.length) % alerts.length; draw(); });
      if (next) next.addEventListener('click', () => { idx = (idx + 1) % alerts.length; draw(); });
    }

    draw();
  }

  // ---- Kick it off --------------------------------------------------------

  if (!('fetch' in window)) return; // ancient browsers — silently skip
  fetchAlerts()
    .then(pickAlerts)
    .then(render)
    .catch(() => {
      // Never block the page on a weather-alert failure. Stay silent.
      MOUNT.innerHTML = '';
    });
})();
