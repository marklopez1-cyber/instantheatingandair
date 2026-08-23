#!/usr/bin/env python3
"""Static site generator for Instant Heating and Air.

Produces every HTML file under /site/ from templates + data modules.
Run: python3 build/build.py
"""

import os
import re
import sys
import json
import html
import time
import hashlib
import base64
from pathlib import Path

# Set BASE_PATH=/instantheatingandair (or similar) for GitHub Pages project sites
# Leave empty for production / root-served hosts
BASE_PATH = os.environ.get("BASE_PATH", "").rstrip("/")

# Cache-busting build stamp. Appended as ?v=ASSET_VERSION on every CSS/JS link.
# Browsers (and CDNs) treat the URL as new on each deploy, so visitors always
# get the latest stylesheet and scripts even if their cached HTML is stale.
ASSET_VERSION = time.strftime("%Y%m%d%H%M")

# Make the data folder importable
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "build"))

from data.site import SITE, NAV, FOOTER_SERVICES, FOOTER_AREAS, HOME_FAQ, WHY_US, REDIRECTS
from data.services import SERVICES, SERVICES_BY_SLUG
from data.areas import AREAS, AREAS_BY_SLUG
from data.reviews import REVIEWS, reviews_for_city, reviews_for_service
from data.posts import POSTS, POSTS_BY_SLUG
from data.google_reviews import (
    LIVE_REVIEWS, TOTAL_REVIEWS, AVG_RATING,
    GOOGLE_PROFILE_URL, LAST_FETCHED,
)
from data.chatbot import INTENTS, QUICK_REPLIES, FALLBACK, SYSTEM_PROMPT

# Auto-sync site-wide rating + review count from the live Google data.
# Falls back to whatever's hardcoded in site.py if the JSON is missing.
if TOTAL_REVIEWS:
    SITE['total_reviews'] = TOTAL_REVIEWS
if AVG_RATING:
    SITE['avg_rating'] = f"{float(AVG_RATING):.1f}"

OUT = ROOT / "site"

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _inline_script_hashes(html_text):
    """Extract all inline <script> blocks (no src=) and return SHA-256 hashes
    formatted for CSP script-src (e.g. "'sha256-BASE64='").

    Chrome enforces CSP script-src on ALL <script> tags — including
    application/ld+json — even though JSON-LD is just data, not code.
    Without hashing, structured-data blocks trigger console errors on
    every page load. Whitelisting their hashes lets CSP stay strict
    (no 'unsafe-inline') while allowing our own JSON-LD to load.
    """
    hashes = set()
    for m in re.finditer(
        r'<script(?![^>]*\ssrc=)[^>]*>(.*?)</script>',
        html_text,
        re.DOTALL | re.IGNORECASE,
    ):
        content = m.group(1)
        digest = hashlib.sha256(content.encode('utf-8')).digest()
        hashes.add("'sha256-" + base64.b64encode(digest).decode('ascii') + "'")
    return sorted(hashes)


def _inject_csp_hashes(html_text):
    """Post-process HTML: inject SHA-256 hashes of all inline scripts into
    the CSP meta tag's script-src directive. Also normalizes: drops
    'frame-ancestors' since browsers ignore it when set via <meta>."""
    hashes = _inline_script_hashes(html_text)
    if not hashes:
        return html_text

    def _fix(match):
        csp = match.group(1)
        # Add hashes into script-src (before the semicolon that ends it)
        csp = re.sub(
            r"(script-src[^;]*)",
            lambda m: m.group(1) + ' ' + ' '.join(hashes),
            csp,
            count=1,
        )
        # frame-ancestors via <meta> is silently ignored by browsers per spec
        # (only works via HTTP header). Strip it to keep the console clean.
        csp = re.sub(r"\s*frame-ancestors[^;]*;?", "", csp)
        # Collapse any double spaces left behind
        csp = re.sub(r"\s{2,}", " ", csp).strip()
        return f'content="{csp}"'

    return re.sub(
        r'content="(default-src[^"]*)"',
        _fix,
        html_text,
        count=1,
    )


def write(path, content):
    full = OUT / path
    full.parent.mkdir(parents=True, exist_ok=True)
    full.write_text(_inject_csp_hashes(content), encoding="utf-8")
    print(f"  wrote {path}")

def rel_to_root(path):
    """Return '../' prefix needed for assets based on output path depth."""
    depth = path.count("/")
    return "../" * depth

def jsonld(data):
    return '<script type="application/ld+json">' + json.dumps(data, separators=(",", ":")) + "</script>"

def esc(s):
    return html.escape(s, quote=True) if s else ""

def email_html(addr):
    """Return an email address with the @ encoded as HTML entity.
    Cloudflare's auto Email Address Obfuscation feature (which Sevalla's CDN
    inherits) rewrites unencoded `name@domain.com` patterns into a [email protected]
    /cdn-cgi/l/email-protection link. That kills NAP consistency for local
    SEO because Google can no longer associate the address with the business.
    Encoding the @ as &#64; in the source HTML bypasses the obfuscation regex
    while still rendering the literal email to humans and search crawlers
    (both decode HTML entities the same way)."""
    if not addr or '@' not in addr:
        return addr or ""
    return addr.replace('@', '&#64;')

def email_link(addr):
    """Return an entity-encoded mailto: link that bypasses Cloudflare's
    email obfuscation. Encoding the @ as &#64; in both the href and the
    visible text avoids triggering Cloudflare's auto-rewrite while still
    clicking through to the user's mail client."""
    if not addr or '@' not in addr:
        return addr or ""
    enc = addr.replace('@', '&#64;')
    return f'<a href="mailto:{enc}">{enc}</a>'

# Icon SVGs (Lucide-style, inlined — zero extra requests)
ICONS = {
    "snowflake": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="22" height="22"><path d="M2 12h20M12 2v20M4.93 4.93l14.14 14.14M19.07 4.93L4.93 19.07"/></svg>',
    "home": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="22" height="22"><path d="m3 9 9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/></svg>',
    "wrench": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="22" height="22"><path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z"/></svg>',
    "flame": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="22" height="22"><path d="M8.5 14.5A2.5 2.5 0 0 0 11 12c0-1.38-.5-2-1-3-1.072-2.143-.224-4.054 2-6 .5 2.5 2 4.9 4 6.5 2 1.6 3 3.5 3 5.5a7 7 0 1 1-14 0c0-1.153.433-2.294 1-3a2.5 2.5 0 0 0 2.5 2.5z"/></svg>',
    "clock": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="22" height="22"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>',
    "building": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="22" height="22"><rect width="16" height="20" x="4" y="2" rx="2"/><path d="M9 22v-4h6v4"/><path d="M8 6h.01M16 6h.01M12 6h.01M12 10h.01M12 14h.01M16 10h.01M16 14h.01M8 10h.01M8 14h.01"/></svg>',
    "wind": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="22" height="22"><path d="M17.7 7.7a2.5 2.5 0 1 1 1.8 4.3H2M9.6 4.6A2 2 0 1 1 11 8H2M12.6 19.4A2 2 0 1 0 14 16H2"/></svg>',
    "chat": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="22" height="22"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>',
    "sun": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="22" height="22"><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.93 4.93l1.41 1.41M17.66 17.66l1.41 1.41M2 12h2M20 12h2M6.34 17.66l-1.41 1.41M19.07 4.93l-1.41 1.41"/></svg>',
    "shield": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="22" height="22"><path d="M20 13c0 5-3.5 7.5-7.66 8.95a1 1 0 0 1-.67-.01C7.5 20.5 4 18 4 13V6a1 1 0 0 1 1-1c2 0 4.5-1.2 6.24-2.72a1.17 1.17 0 0 1 1.52 0C14.51 3.81 17 5 19 5a1 1 0 0 1 1 1z"/></svg>',
    "star": '<svg viewBox="0 0 24 24" fill="currentColor" stroke="none" width="18" height="18"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg>',
}

def icon(name):
    return ICONS.get(name, ICONS["home"])

# ---------------------------------------------------------------------------
# Layout fragments
# ---------------------------------------------------------------------------

def head(title, description, path="", og_type="website", extra_head="", canonical=None):
    """Full <head> block. title must already include the brand-suffix logic."""
    canonical_url = canonical or f"{SITE['base_url']}/{path}".rstrip("/")
    if not canonical_url.startswith("http"):
        canonical_url = SITE["base_url"]
    # Ensure trailing slash/no index.html mess — for index pages, canonical is the folder
    if path == "" or path == "index.html":
        canonical_url = SITE["base_url"] + "/"
    elif path.endswith("/index.html"):
        canonical_url = f"{SITE['base_url']}/{path[:-len('index.html')]}"
    # Google Analytics — render gtag.js + html data-ga attr only if ID is set.
    ga_id = SITE.get('ga4_id', '')
    ga_attr = f' data-ga="{esc(ga_id)}"' if ga_id else ''
    ga_script = f'<script async src="https://www.googletagmanager.com/gtag/js?id={esc(ga_id)}"></script>' if ga_id else ''
    # CSP additions when GA is enabled
    ga_csp_script = ' https://www.googletagmanager.com' if ga_id else ''
    # GA4 sends beacons to multiple endpoints depending on features enabled:
    #   www.google-analytics.com          → primary hit endpoint (/g/collect for GA4)
    #   *.google-analytics.com            → regional collectors (region1, region2, …)
    #   analytics.google.com              → enhanced measurement, DebugView
    #   *.analytics.google.com            → subdomains of the above
    #   www.google.com                    → /g/collect relay used when Signals/Ads are on
    #   stats.g.doubleclick.net           → Google Signals / audiences beacons
    # Whitelist all six so pageviews and events aren't silently dropped by CSP.
    ga_csp_connect = ' https://www.google-analytics.com https://*.google-analytics.com https://analytics.google.com https://*.analytics.google.com https://www.google.com https://stats.g.doubleclick.net' if ga_id else ''

    return f"""<!DOCTYPE html>
<html lang="en"{ga_attr}>
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
  <meta name="theme-color" content="#143C5E">
  <title>{esc(title)}</title>
  <meta name="description" content="{esc(description)}">
  <link rel="canonical" href="{canonical_url}">
  <meta name="robots" content="index,follow,max-image-preview:large,max-snippet:-1,max-video-preview:-1">
  <meta name="geo.region" content="US-AZ">
  <meta name="geo.placename" content="Phoenix">
  <meta name="geo.position" content="{SITE['address']['lat']};{SITE['address']['lng']}">
  <meta name="ICBM" content="{SITE['address']['lat']}, {SITE['address']['lng']}">

  <!-- Security headers (delivered via meta — GitHub Pages doesn't expose HTTP headers) -->
  <meta http-equiv="Content-Security-Policy" content="default-src 'self'; script-src 'self' https://unpkg.com{ga_csp_script}; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com https://unpkg.com; font-src 'self' https://fonts.gstatic.com data:; img-src 'self' data: https:; frame-src https://instant-hvac-quote.com https://book.housecallpro.com https://www.google.com https://maps.google.com; form-action 'self' https://formsubmit.co; connect-src 'self' https://formsubmit.co https://api.open-meteo.com https://api.weather.gov{ga_csp_connect}; base-uri 'self'; object-src 'none'; frame-ancestors 'self'; upgrade-insecure-requests">
  <meta http-equiv="X-Content-Type-Options" content="nosniff">
  <meta name="referrer" content="strict-origin-when-cross-origin">
  <meta http-equiv="Permissions-Policy" content="camera=(), microphone=(), geolocation=(), payment=(), usb=(), magnetometer=(), gyroscope=(), accelerometer=(), interest-cohort=()">
  {ga_script}

  <!-- Open Graph -->
  <meta property="og:type" content="{og_type}">
  <meta property="og:site_name" content="{esc(SITE['name'])}">
  <meta property="og:title" content="{esc(title)}">
  <meta property="og:description" content="{esc(description)}">
  <meta property="og:url" content="{canonical_url}">
  <meta property="og:image" content="{SITE['base_url']}/assets/img/og-image.jpg">
  <meta property="og:image:width" content="1200">
  <meta property="og:image:height" content="630">
  <meta property="og:locale" content="en_US">

  <!-- Twitter -->
  <meta property="og:image:alt" content="Instant Heating and Air — Phoenix HVAC professionals you can trust">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{esc(title)}">
  <meta name="twitter:description" content="{esc(description)}">
  <meta name="twitter:image" content="{SITE['base_url']}/assets/img/og-image.jpg">
  <meta name="twitter:image:alt" content="Instant Heating and Air — Phoenix HVAC professionals you can trust">

  <!-- Favicons -->
  <link rel="icon" href="/assets/img/favicon-32.png" sizes="32x32">
  <link rel="icon" href="/assets/img/favicon-16.png" sizes="16x16">
  <link rel="apple-touch-icon" href="/assets/img/apple-touch-icon.png">
  <link rel="manifest" href="/site.webmanifest">

  <!-- Preconnects for fonts + the embedded quote tool (LCP boost) -->
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link rel="preconnect" href="https://instant-hvac-quote.com">
  <link rel="dns-prefetch" href="https://instant-hvac-quote.com">
  <link href="https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@700;800&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">

  <!-- Stylesheet (versioned for cache-busting) -->
  <link rel="stylesheet" href="/assets/css/styles.css?v={ASSET_VERSION}">

{extra_head}
</head>
<body>
  <a class="skip-link" href="#main">Skip to content</a>
"""

_TEMP_SVG = '<svg class="temp-icon" viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M14 14.76V3.5a2.5 2.5 0 0 0-5 0v11.26a4.5 4.5 0 1 0 5 0z"/><circle cx="11.5" cy="17.5" r="1.5" fill="currentColor"/></svg>'

def topbar():
    return f"""<div class="topbar">
  <div class="container row">
    <div class="lic">AZ {SITE['license']} · Licensed · Bonded · Insured · Family Owned</div>
    <div class="topbar-right">
      <span class="temp-chip temp-chip-dark" data-phx-temp hidden aria-live="polite">
        {_TEMP_SVG}
        Phoenix <span data-phx-temp-value>--</span>°F
      </span>
      <span class="pill">Open Now</span>
      <a href="tel:{SITE['phone_link']}" data-track="phone_click">📞 {SITE['phone_display']}</a>
    </div>
  </div>
</div>"""

def header(current=""):
    links = ""
    for label, url in NAV:
        active = ' aria-current="page"' if url == current else ""
        links += f'<a href="{url}"{active}>{label}</a>'
    return f"""{topbar()}
<header class="header">
  <div class="container row">
    <div class="header-left">
      <a class="brand" href="/" aria-label="{esc(SITE['name'])} — home">
        <img src="/assets/img/logo-full.png" alt="{esc(SITE['name'])} logo — Phoenix HVAC professionals you can trust" width="180" height="56">
      </a>
      <a class="btn btn-orange cta-quote" href="/book.html" data-track="quote_click">New AC Quote</a>
    </div>
    <span class="temp-chip temp-chip-light" data-phx-temp hidden aria-live="polite">
      {_TEMP_SVG}
      <span data-phx-temp-value>--</span>°F
    </span>
    <button class="menu-toggle" aria-label="Toggle navigation menu" aria-expanded="false" aria-controls="site-nav">☰</button>
    <nav class="nav" id="site-nav" aria-label="Main navigation">
      {links}
    </nav>
  </div>
</header>"""

def final_cta(title_h2=None, p=None):
    title_h2 = title_h2 or 'Comfort is Our <span class="o">Obsession.</span>'
    p = p or "Let's get your home back to the temperature you pay for. Same-day service, straight-shooter pricing, written warranties."
    return f"""<section class="finalcta">
  <div class="container">
    <h2>{title_h2}</h2>
    <p>{p}</p>
    <div class="ctas">
      <button type="button" class="btn btn-orange" data-modal-open="estimate-modal" data-track="estimate_click">Request Service →</button>
      <a class="btn btn-white" href="tel:{SITE['phone_link']}" data-track="phone_click">📞 {SITE['phone_display']}</a>
    </div>
    <div class="lic-line">AZ {SITE['license']} · Licensed · Bonded · Insured · Family Owned</div>
  </div>
</section>"""

def estimate_modal():
    """Generic estimate-request modal — included on every page via footer()."""
    return f"""<!-- Estimate request modal — opened by [data-modal-open="estimate-modal"] -->
<div class="modal" id="estimate-modal" aria-hidden="true">
  <div class="modal-backdrop" data-modal-close></div>
  <div class="modal-dialog" role="dialog" aria-labelledby="est-heading" aria-modal="true">
    <button type="button" class="modal-close" data-modal-close aria-label="Close form">&times;</button>

    <form class="club-signup ajax-form" id="estimate-form" action="{SITE['form_endpoints']['contact']}" method="POST">
      <h3 id="est-heading">Request Service</h3>
      <p class="cc-policy" style="margin:-4px 0 12px;font-size:0.85rem;color:#5d6b7a;line-height:1.45">
        <strong>Free in-home estimates</strong> for new system installations and replacements.
        Service calls and repairs include an <strong>$84.50 diagnostic fee</strong> &mdash;
        waived when you approve the repair.
      </p>
      <input type="hidden" name="_subject" value="New Estimate Request — Instant Heating and Air">
      <input type="hidden" name="_template" value="table">
      <input type="hidden" name="_captcha" value="false">
      <input type="hidden" name="_next" value="{SITE['success_redirect']}">
      <input type="hidden" name="form_type" value="estimate_request">
      <!-- Bot traps: both hidden by CSS. Real users won't touch them; bots
           auto-fill anything with a legit-looking name attribute. -->
      <input type="text" name="_honey" class="hp-field" tabindex="-1" autocomplete="off" aria-hidden="true">
      <div class="hp-field" aria-hidden="true">
        <label>Website (leave blank)</label>
        <input type="text" name="website" tabindex="-1" autocomplete="off">
      </div>

      <div class="cc-field">
        <label for="est-name">Full name</label>
        <input id="est-name" name="name" type="text" required minlength="2" autocomplete="name" placeholder="Your name">
      </div>

      <div class="cc-row2">
        <div class="cc-field">
          <label for="est-phone">Phone</label>
          <input id="est-phone" name="phone" type="tel" required pattern="[\\d\\s().+\\-]{{10,}}" autocomplete="tel" placeholder="(623) 555-0123" title="Please enter a valid phone number (at least 10 digits)">
        </div>
        <div class="cc-field">
          <label for="est-email">Email</label>
          <input id="est-email" name="email" type="email" required autocomplete="email" placeholder="you@email.com">
        </div>
      </div>

      <div class="cc-field">
        <label for="est-address">Service address</label>
        <input id="est-address" name="address" type="text" required minlength="10" autocomplete="street-address" placeholder="Street, City, AZ ZIP" title="Please enter your full street address including city and ZIP">
      </div>

      <div class="cc-row2">
        <div class="cc-field">
          <label for="est-service">What do you need?</label>
          <select id="est-service" name="service">
            <option value="ac-repair">AC repair / not cooling</option>
            <option value="ac-install">New AC install or replacement</option>
            <option value="ac-tuneup">AC tune-up / maintenance</option>
            <option value="heating-repair">Heating repair</option>
            <option value="heating-install">New heating install</option>
            <option value="emergency">24/7 emergency service</option>
            <option value="commercial">Commercial HVAC</option>
            <option value="iaq">Indoor air quality / duct cleaning</option>
            <option value="other">Other / not sure</option>
          </select>
        </div>
        <div class="cc-field">
          <label for="est-when">Best time to reach you</label>
          <select id="est-when" name="best_time">
            <option value="anytime">Any time today</option>
            <option value="morning">Morning</option>
            <option value="afternoon">Afternoon</option>
            <option value="evening">Evening</option>
            <option value="weekend">Weekend</option>
          </select>
        </div>
      </div>

      <div class="cc-field">
        <label for="est-notes">Tell us about your project</label>
        <textarea id="est-notes" name="notes" rows="2" required minlength="10" placeholder="System age, what's going on, urgency..." title="Please give us a brief description (at least 10 characters)"></textarea>
      </div>

      <button type="submit" class="btn btn-orange cc-submit">Send My Request &rarr;</button>
      <p class="cc-foot">No spam. We'll review and reach out by phone or text within one business day.</p>
    </form>

    <div class="modal-success" hidden>
      <div class="modal-success-icon" aria-hidden="true">&#10003;</div>
      <h3>Got It!</h3>
      <p>We received your request. A real human will get back to you within one business day with honest pricing and next steps.</p>
      <p style="font-size:0.875rem">If it's urgent, call us at <a href="tel:{SITE['phone_link']}">{SITE['phone_display']}</a>.</p>
      <button type="button" class="btn btn-orange" data-modal-close>Done</button>
    </div>
  </div>
</div>"""


def footer():
    svc_links = "".join(f'<a href="{u}">{esc(l)}</a>' for l, u in FOOTER_SERVICES)
    area_links = "".join(f'<a href="{u}">{esc(l)}</a>' for l, u in FOOTER_AREAS)
    fb, ig = SITE['social']['facebook'], SITE['social']['instagram']
    return f"""<footer>
  <div class="container">
    <div class="row">
      <div class="brand-footer">
        <img src="/assets/img/logo-full.png" alt="{esc(SITE['name'])}" width="200">
        <p>{esc(SITE['tagline'])}. Family-owned HVAC pros serving Phoenix, Anthem, and the entire North Valley. Your comfort is our obsession.</p>
        <div class="lic">AZ {SITE['license']} · Licensed · Bonded · Insured</div>
        <div class="social">
          <a href="{fb}" aria-label="Facebook" rel="noopener">f</a>
          <a href="{ig}" aria-label="Instagram" rel="noopener">ig</a>
          <a href="{SITE['social']['google']}" aria-label="Google Business Profile" rel="noopener">G</a>
        </div>
      </div>
      <div>
        <h4>SERVICES</h4>
        {svc_links}
      </div>
      <div>
        <h4>SERVICE AREAS</h4>
        {area_links}
      </div>
      <div>
        <h4>CONTACT</h4>
        <a href="tel:{SITE['phone_link']}" data-track="phone_click">📞 {SITE['phone_display']}</a>
        <a href="/contact.html">✉️ Send a Message</a>
        <a href="https://maps.google.com/?q={esc(SITE['address']['street']+', '+SITE['address']['city']+', '+SITE['address']['region'])}" rel="noopener">{SITE['address']['street']}<br>{SITE['address']['city']}, {SITE['address']['region']} {SITE['address']['postal']}</a>
        <a href="#">{SITE['hours']}</a>
      </div>
    </div>
    <div class="base">
      <div>© 2026 {esc(SITE['legal_name'])}. All rights reserved.</div>
      <div>
        <a href="/privacy.html" style="display:inline;margin-right:14px">Privacy</a>
        <a href="/terms.html" style="display:inline;margin-right:14px">Terms</a>
        <a href="/accessibility.html" style="display:inline;margin-right:14px">Accessibility</a>
        <a href="/sitemap.xml" style="display:inline">Sitemap</a>
      </div>
    </div>
  </div>
</footer>
{estimate_modal()}
<script src="/assets/js/main.js?v={ASSET_VERSION}" defer></script>
<script src="/assets/js/chatbot.js?v={ASSET_VERSION}" defer></script>
<script src="/assets/js/weather-alerts.js?v={ASSET_VERSION}" defer></script>
</body>
</html>"""

# ---------------------------------------------------------------------------
# Schema (JSON-LD) helpers
# ---------------------------------------------------------------------------

def schema_localbusiness():
    return {
        "@context": "https://schema.org",
        "@type": "HVACBusiness",
        "@id": f"{SITE['base_url']}/#localbusiness",
        "name": SITE['legal_name'],
        "alternateName": SITE['name'],
        "url": SITE['base_url'],
        "telephone": SITE['phone_display'],
        "email": SITE['email'],
        "image": f"{SITE['base_url']}/assets/img/logo-full.png",
        "logo": f"{SITE['base_url']}/assets/img/logo-full.png",
        "priceRange": "$$",
        "address": {
            "@type": "PostalAddress",
            "streetAddress": SITE['address']['street'],
            "addressLocality": SITE['address']['city'],
            "addressRegion": SITE['address']['region'],
            "postalCode": SITE['address']['postal'],
            "addressCountry": SITE['address']['country'],
        },
        "geo": {
            "@type": "GeoCoordinates",
            "latitude": SITE['address']['lat'],
            "longitude": SITE['address']['lng'],
        },
        "areaServed": [
            {"@type": "City", "name": a['name'], "sameAs": f"{SITE['base_url']}/service-areas/{a['slug']}.html"} for a in AREAS
        ],
        "serviceArea": {
            "@type": "GeoCircle",
            "geoMidpoint": {"@type": "GeoCoordinates", "latitude": SITE['address']['lat'], "longitude": SITE['address']['lng']},
            "geoRadius": SITE['service_radius_miles'] * 1609,  # meters
        },
        "openingHoursSpecification": [
            {"@type": "OpeningHoursSpecification", "dayOfWeek": ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"], "opens": "00:00", "closes": "23:59"}
        ],
        # sameAs links canonical identity to authoritative external profiles.
        # GOOGLE_PROFILE_URL is the canonical GBP maps URL from the Places API —
        # tells Google "this website IS that business" (helps knowledge panel).
        "sameAs": [SITE['social']['facebook'], SITE['social']['instagram'], SITE['social']['yelp'], GOOGLE_PROFILE_URL],
        "hasOfferCatalog": {
            "@type": "OfferCatalog",
            "name": "HVAC services",
            "itemListElement": [
                {"@type": "Offer", "itemOffered": {"@type": "Service", "name": s['title_short'], "url": f"{SITE['base_url']}/services/{s['slug']}.html"}} for s in SERVICES
            ]
        },
        "aggregateRating": {
            "@type": "AggregateRating",
            "ratingValue": SITE.get('avg_rating', '5.0'),
            "reviewCount": str(SITE.get('total_reviews', len(REVIEWS))),
            "bestRating": "5",
            "worstRating": "1"
        },
        # Tells Google there is an actionable lead-gen quote tool on the site
        # so it can surface "Get Quote" buttons in business knowledge panels.
        "potentialAction": [
            {
                "@type": "ReserveAction",
                "name": "Get a free HVAC replacement estimate",
                "target": {
                    "@type": "EntryPoint",
                    "urlTemplate": SITE['quote_tool_url'],
                    "actionPlatform": [
                        "https://schema.org/DesktopWebPlatform",
                        "https://schema.org/MobileWebPlatform"
                    ]
                }
            },
            {
                "@type": "CallAction",
                "name": "Call Instant Heating and Air 24/7",
                "target": f"tel:{SITE['phone_link']}"
            }
        ]
    }

def schema_website():
    return {
        "@context": "https://schema.org",
        "@type": "WebSite",
        "@id": f"{SITE['base_url']}/#website",
        "url": SITE['base_url'],
        "name": SITE['name'],
        "publisher": {"@id": f"{SITE['base_url']}/#localbusiness"},
        "inLanguage": "en-US"
    }

def schema_organization():
    """Standalone Organization schema — helps Google build a knowledge panel
    and link the brand identity to socials."""
    return {
        "@context": "https://schema.org",
        "@type": "Organization",
        "@id": f"{SITE['base_url']}/#organization",
        "name": SITE['legal_name'],
        "alternateName": SITE['name'],
        "url": SITE['base_url'],
        "logo": {
            "@type": "ImageObject",
            "url": f"{SITE['base_url']}/assets/img/logo-full.png",
            "width": 1614,
            "height": 470
        },
        "telephone": SITE['phone_display'],
        "email": SITE['email'],
        "foundingDate": str(SITE['founded_year']),
        "sameAs": [
            SITE['social']['facebook'],
            SITE['social']['instagram'],
            SITE['social']['yelp'],
            SITE['social']['nextdoor'],
            GOOGLE_PROFILE_URL,  # canonical GBP link
        ]
    }

def schema_review(review):
    """Individual Review schema — unlocks star-rating rich snippets in search."""
    # Strip emoji from review body for schema cleanliness (Google's parser is strict)
    text = re.sub(r'[\U0001F000-\U0001FFFF\U00002600-\U000027BF\uFE0F\u200D]', '', review['text'])
    text = re.sub(r'\s+', ' ', text).strip()

    city_name = AREAS_BY_SLUG.get(review['city'], {}).get('name', review['city'].title())
    schema = {
        "@context": "https://schema.org",
        "@type": "Review",
        "itemReviewed": {"@id": f"{SITE['base_url']}/#localbusiness"},
        "author": {
            "@type": "Person",
            "name": review['author']
        },
        "reviewBody": text,
        "reviewRating": {
            "@type": "Rating",
            "ratingValue": "5",
            "bestRating": "5",
            "worstRating": "1"
        },
        "publisher": {"@type": "Organization", "name": review.get('source', 'Google')},
        "locationCreated": {"@type": "Place", "name": f"{city_name}, AZ"}
    }
    if review.get('date'):
        schema['datePublished'] = review['date']
    return schema

def schema_breadcrumbs(items):
    """items: list of (name, url_path)."""
    return {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {
                "@type": "ListItem",
                "position": i + 1,
                "name": name,
                "item": f"{SITE['base_url']}{path}" if path else None
            } for i, (name, path) in enumerate(items)
        ]
    }

def schema_faq(pairs):
    return {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}}
            for q, a in pairs
        ]
    }

def schema_service(svc, area_name=None):
    name = svc['title_long'] if not area_name else f"{svc['title_short']} in {area_name}, AZ"
    return {
        "@context": "https://schema.org",
        "@type": "Service",
        "serviceType": svc['title_short'],
        "name": name,
        "description": svc['meta_description'],
        "provider": {"@id": f"{SITE['base_url']}/#localbusiness"},
        "areaServed": [{"@type": "City", "name": a['name']} for a in AREAS],
        "url": f"{SITE['base_url']}/services/{svc['slug']}.html"
    }

def schema_place(area):
    return {
        "@context": "https://schema.org",
        "@type": "Place",
        "name": f"{area['name']}, AZ",
        "geo": {"@type": "GeoCoordinates", "latitude": area['lat'], "longitude": area['lng']},
        "address": {"@type": "PostalAddress", "addressLocality": area['name'], "addressRegion": "AZ", "addressCountry": "US"}
    }

def schema_quote_tool(page_url):
    """WebApplication schema describing the embedded instant HVAC quote tool.
    Iframes are opaque to Googlebot, which means without explicit structured
    data Google can't tell that the homepage hosts a working pricing/quote tool.
    This schema declares it explicitly so Google can:
      1. Show the tool as a feature in the knowledge panel / business listing
      2. Surface 'Get Quote' or 'Estimate' actions in rich results
      3. Associate the tool with HVAC pricing keywords
    """
    return {
        "@context": "https://schema.org",
        "@type": "WebApplication",
        "@id": f"{page_url}#quote-tool",
        "name": "Instant HVAC Quote Tool",
        "alternateName": ["Free AC Replacement Estimate", "Instant HVAC Pricing Calculator"],
        "description": (
            "Free online HVAC pricing tool that delivers an instant, itemized "
            "estimate for a new air conditioner, furnace, or heat pump system "
            "for homes in Phoenix and the North Valley — no phone call required, "
            "results in about 90 seconds."
        ),
        "url": page_url,
        "applicationCategory": "BusinessApplication",
        "operatingSystem": "Web Browser",
        "browserRequirements": "Requires JavaScript and cookies",
        "isAccessibleForFree": True,
        "offers": {
            "@type": "Offer",
            "price": "0",
            "priceCurrency": "USD",
            "description": "Free instant estimate — no obligation"
        },
        "publisher": {"@id": f"{SITE['base_url']}/#localbusiness"},
        "potentialAction": {
            "@type": "ReserveAction",
            "name": "Get a free HVAC replacement estimate",
            "target": {
                "@type": "EntryPoint",
                "urlTemplate": SITE['quote_tool_url'],
                "actionPlatform": [
                    "https://schema.org/DesktopWebPlatform",
                    "https://schema.org/MobileWebPlatform"
                ]
            },
            "result": {
                "@type": "Reservation",
                "name": "HVAC system replacement estimate appointment"
            }
        }
    }

def _fmt_date(iso):
    """Convert 'YYYY-MM-DD' to 'Month D, YYYY' for human-friendly display."""
    try:
        y, m, d = iso.split('-')
        months = ['January','February','March','April','May','June',
                  'July','August','September','October','November','December']
        return f"{months[int(m)-1]} {int(d)}, {y}"
    except Exception:
        return iso

def schema_article(post):
    # dateModified defaults to datePublished but posts can override with an
    # explicit 'updated' field. Google favors recently-updated content in
    # search rankings, so surfacing an accurate update date matters.
    return {
        "@context": "https://schema.org",
        "@type": "BlogPosting",
        "headline": post['title'],
        "description": post['meta_description'],
        "datePublished": post['date'],
        "dateModified": post.get('updated', post['date']),
        "author": {"@type": "Organization", "name": SITE['name']},
        "publisher": {"@id": f"{SITE['base_url']}/#localbusiness"},
        "image": f"{SITE['base_url']}/assets/img/og-image.jpg",
        "mainEntityOfPage": {"@type": "WebPage", "@id": f"{SITE['base_url']}/blog/{post['slug']}.html"}
    }

# ---------------------------------------------------------------------------
# Reusable content blocks
# ---------------------------------------------------------------------------

def rev_card(r):
    return f"""<div class="rev">
  <div class="stars" aria-label="5-star review">★★★★★</div>
  <blockquote>"{esc(r['text'])}"</blockquote>
  <cite><b>{esc(r['author'])}</b> · {esc(dict(AREAS_BY_SLUG).get(r['city'], {}).get('name', r['city'].title()))}, AZ · {esc(r['source'])}</cite>
</div>"""


def google_rev_card(r):
    """Render a live Google review card with profile photo, name, time, and quote.

    Used in the homepage 'Verified Google Reviews' section. Pulls fresh data
    from the Google Places API (see data/google_reviews.py).
    """
    # Trim Google's profile photo to a smaller cached size for faster load
    photo = r.get('profile_photo_url', '')
    if 'googleusercontent.com' in photo and '=s' in photo:
        photo = photo.split('=s')[0] + '=s96-c'

    if photo:
        photo_el = (
            f'<img class="g-rev-photo" src="{esc(photo)}" alt="" '
            f'loading="lazy" width="48" height="48" '
            f'referrerpolicy="no-referrer" decoding="async">'
        )
    else:
        initial = esc(r['author'][:1].upper()) if r.get('author') else 'G'
        photo_el = f'<div class="g-rev-photo g-rev-photo-empty" aria-hidden="true">{initial}</div>'

    author_url = r.get('author_url', '')
    author_link_open = f'<a href="{esc(author_url)}" target="_blank" rel="noopener nofollow">' if author_url else ''
    author_link_close = '</a>' if author_url else ''

    return f"""<article class="g-rev">
  <div class="g-rev-head">
    {photo_el}
    <div class="g-rev-meta">
      <b>{author_link_open}{esc(r['author'])}{author_link_close}</b>
      <span class="g-rev-time">{esc(r.get('relative_time', ''))}</span>
    </div>
    <img class="g-rev-source" src="/assets/img/google-g.svg" alt="Google" width="20" height="20" loading="lazy">
  </div>
  <div class="stars" aria-label="{r.get('rating', 5)}-star review">★★★★★</div>
  <blockquote>"{esc(r['text'])}"</blockquote>
</article>"""

def faq_html(pairs):
    items = ""
    for q, a in pairs:
        items += f"""<details><summary>{esc(q)}</summary><p>{a}</p></details>"""
    return f'<div class="faq">{items}</div>'

def services_grid(limit=None, order=None):
    """Render service cards. Pass `order` (list of slugs) to control sequence
    (used on the homepage to feature a curated subset). Without args,
    renders all services in their default services.py order (used on /services/)."""
    if order:
        by_slug = {s['slug']: s for s in SERVICES}
        svcs = [by_slug[slug] for slug in order if slug in by_slug]
    elif limit:
        svcs = SERVICES[:limit]
    else:
        svcs = SERVICES
    cards = ""
    for s in svcs:
        if s.get('bg_image'):
            # Photo-backed variant — image with dark gradient overlay, white text
            cards += f"""<a class="svc-card svc-card-photo" href="/services/{s['slug']}.html" style="background-image:linear-gradient(180deg,rgba(11,36,54,0.05) 0%,rgba(11,36,54,0.15) 45%,rgba(11,36,54,0.78) 100%),url('{s['bg_image']}');background-size:100% 100%,contain;background-repeat:no-repeat,no-repeat;background-position:0 0,center top;">
  <div class="ic">{icon(s['icon'])}</div>
  <h3>{esc(s['title_short'])}</h3>
  <p>{esc(s['short_desc'])}</p>
  <span class="more">Learn more →</span>
</a>"""
        else:
            cards += f"""<a class="svc-card" href="/services/{s['slug']}.html">
  <div class="ic">{icon(s['icon'])}</div>
  <h3>{esc(s['title_short'])}</h3>
  <p>{esc(s['short_desc'])}</p>
  <span class="more">Learn more →</span>
</a>"""
    return f'<div class="svc-grid">{cards}</div>'

def area_chips():
    chips = "".join(f'<a class="chip" href="/service-areas/{a["slug"]}.html">{esc(a["name"])}</a>' for a in AREAS)
    return f'<div class="chips">{chips}</div>'

def brand_wall():
    """Render a brand wall. Uses image logo from /assets/img/brands/<slug>.<ext>
    if it exists, otherwise falls back to a text chip. This means you can drop
    logos in one at a time and the page picks them up on the next build.

    Looks in BOTH the output tree (site/) — used by local builds — AND at repo
    root — used by the GitHub Actions rebuild, where static assets live at root
    because the workflow promotes site/ contents to root after each build. Either
    location working is enough to produce an <img> tag; the served file is at
    /assets/img/brands/... in both cases.
    """
    items = []
    for b in SITE['brands_serviced']:
        slug = b.lower().replace(' ', '-')
        logo_url = None
        for ext in ('svg', 'png', 'webp', 'jpg', 'jpeg'):
            candidates = (
                OUT / 'assets' / 'img' / 'brands' / f'{slug}.{ext}',
                ROOT / 'assets' / 'img' / 'brands' / f'{slug}.{ext}',
            )
            if any(p.exists() for p in candidates):
                logo_url = f'/assets/img/brands/{slug}.{ext}'
                break
        if logo_url:
            items.append(
                f'<div class="brand-logo-wrap" title="{esc(b)}">'
                f'<img src="{logo_url}" alt="{esc(b)} HVAC equipment serviced by {esc(SITE["name"])}" loading="lazy" class="brand-logo">'
                f'</div>'
            )
        else:
            items.append(f'<span class="brand-chip">{esc(b)}</span>')
    return '<div class="brands">' + "".join(items) + '</div>'

def why_us_grid():
    cards = ""
    for w in WHY_US:
        slug = w.get('slug', '')
        slug_class = f" why-card-{slug}" if slug else ""
        cards += f"""<div class="card-item why-card{slug_class}">
  <div class="why-card-scrim"></div>
  <div class="why-card-body">
    <div class="ic">{icon(w['icon'])}</div>
    <h3>{esc(w['title'])}</h3>
    <p>{esc(w['body'])}</p>
  </div>
</div>"""
    return f'<div class="grid-3">{cards}</div>'

def trust_strip():
    return f"""<div class="trustbar"><div class="container row">
  <div class="item"><span class="ic">AZ</span>{SITE['license']}</div>
  <div class="item"><span class="ic">✓</span>Upfront Pricing</div>
  <div class="item"><span class="ic">⚡</span>24/7 Emergency</div>
  <div class="item"><span class="ic">★</span>5-Star Reviewed</div>
  <div class="item"><span class="ic">$</span>Flexible Financing</div>
</div></div>"""

def club_band():
    return f"""<section class="club">
  <div class="container row">
    <div>
      <span class="eyebrow" style="color:var(--orange)">The Comfort Club</span>
      <h2>$18 a month keeps your system <span class="o">humming.</span></h2>
      <p>Two precision tune-ups a year, 15% off repairs, priority dispatch, no overtime charges. Pays for itself the first time we catch something.</p>
      <ul>
        <li>2 seasonal tune-ups</li>
        <li>15% off all repairs</li>
        <li>Priority dispatch</li>
        <li>No overtime fees</li>
        <li>Extended warranty credit</li>
        <li>Cancel any time</li>
      </ul>
    </div>
    <div style="text-align:right">
      <a class="btn btn-orange" href="/maintenance-plan.html">Join the Comfort Club →</a>
    </div>
  </div>
</section>"""

# ---------------------------------------------------------------------------
# Individual page builders
# ---------------------------------------------------------------------------

def build_home():
    title = f"Phoenix HVAC | AC Repair, R-454B Install & 24/7 Emergency | {SITE['name']}"
    desc = f"Honest Phoenix HVAC — {SITE['avg_rating']}★ on {SITE['total_reviews']} Google reviews. Same-day AC repair, 2026 R-454B installs, SRP Cool Cash rebates handled. 24/7 emergency across Phoenix, Anthem & North Valley. {SITE['phone_display']}."

    # Live Google reviews — fetched from the Places API (data/google_reviews.py)
    # Each rebuild picks up the freshest snapshot in google_reviews.json.
    g_rev_cards = "".join(google_rev_card(r) for r in LIVE_REVIEWS)

    faq_pairs = [(q['q'], q['a']) for q in HOME_FAQ]

    extra_schema = jsonld({
        "@context": "https://schema.org",
        "@graph": [
            schema_localbusiness(),
            schema_organization(),
            schema_website(),
            schema_faq(faq_pairs),
            schema_quote_tool(SITE['base_url'] + "/")
        ]
    })

    body = f"""{header('/')}
<main id="main">
  <!-- HERO with embedded estimate tool -->
  <section class="hero hero-quote">
    <div class="container">
      <!-- Live NWS weather-alert callout. Only renders when Phoenix has an
           active advisory/warning. Empty on quiet days (zero layout impact). -->
      <div id="wx-alerts" class="wx-alerts-mount" aria-live="polite"></div>
    </div>
    <div class="container hero-quote-grid">
      <div class="hero-text">
        <span class="badge"><span class="stars">★★★★★</span> {SITE['avg_rating']} · Google Verified · Phoenix &amp; Anthem</span>
        <h1>Phoenix HVAC<br>Done Right the <span class="o">First Time.</span></h1>
        <p class="lead">Honest pricing, same-day service, and the work you'd want a family member doing. Pricing a new system? Get your free instant estimate right here. Need a repair? Call us — we'll diagnose for $84.50 (waived with the repair).</p>
        <div class="hero-phone">
          <a class="btn btn-outline-white" href="tel:{SITE['phone_link']}" data-track="phone_click">📞 {SITE['phone_display']}</a>
          <span class="hero-phone-note">Or call us — we pick up 24/7 for emergencies.</span>
        </div>
        <div class="trust"><span>Licensed &amp; Bonded</span><span>Upfront Pricing</span><span>24/7 Emergency</span><span>100% Satisfaction</span></div>
      </div>
      <!-- Embedded instant HVAC quote tool — wrapped in a semantic <section>
           with descriptive text + WebApplication schema (in <head>) so Google
           can understand what the iframe contains and surface it as a feature
           in business knowledge panels and rich results. -->
      <section class="hero-quote-frame" aria-labelledby="quote-tool-heading" itemscope itemtype="https://schema.org/WebApplication">
        <meta itemprop="name" content="Instant HVAC Quote Tool">
        <meta itemprop="applicationCategory" content="BusinessApplication">
        <meta itemprop="operatingSystem" content="Web Browser">
        <div class="quote-frame-label">
          <span class="dot-live"></span><h2 id="quote-tool-heading" class="quote-tool-h">Instant HVAC Replacement Estimate</h2>
        </div>
        <p class="visually-hidden" itemprop="description">
          Free online HVAC pricing tool. Get an instant, itemized estimate for
          a new air conditioner, furnace, or heat pump system in your Phoenix
          or North Valley home — about 90 seconds, no phone call required.
        </p>
        <div class="quote-wrap quote-wrap-hero">
          <iframe src="{SITE['quote_tool_url']}"
                  title="Instant Heating and Air — free HVAC replacement estimate tool"
                  loading="eager"
                  allow="clipboard-write"
                  sandbox="allow-forms allow-scripts allow-popups allow-popups-to-escape-sandbox allow-same-origin"
                  referrerpolicy="strict-origin-when-cross-origin"
                  itemprop="url"></iframe>
          <noscript>
            <div class="quote-noscript">
              <p><strong>Want an instant HVAC replacement estimate?</strong>
              Our online quote tool gives you itemized pricing for a new AC,
              furnace, or heat pump system in about 90 seconds.</p>
              <p><a href="{SITE['quote_tool_url']}" rel="noopener">Open the
              instant HVAC quote tool &rarr;</a> &nbsp;or&nbsp;
              <a href="tel:{SITE['phone_link']}">call {SITE['phone_display']}</a>.</p>
            </div>
          </noscript>
        </div>
        <p class="quote-fallback">Trouble loading? <a href="{SITE['quote_tool_url']}" target="_blank" rel="noopener">Open the free HVAC quote tool in a new tab →</a></p>
      </section>
    </div>
  </section>

  {trust_strip()}

  <!-- 2026 update strip — surfaces the latest industry-shift keywords
       (R-454B refrigerant, SRP Cool Cash rebates) in the first viewport
       so Google sees them weighted higher and visitors immediately
       see we're current with industry changes. -->
  <section class="update-strip" aria-label="2026 HVAC updates we handle">
    <div class="container update-strip-inner">
      <a class="update-chip" href="/blog/r-454b-refrigerant-phoenix-2026.html">
        <span class="update-chip-icon" aria-hidden="true">🆕</span>
        <span><strong>Now installing R-454B systems</strong><br><span class="update-chip-sub">2026 refrigerant standard</span></span>
      </a>
      <a class="update-chip" href="/services/ac-installation.html#rebates">
        <span class="update-chip-icon" aria-hidden="true">💰</span>
        <span><strong>SRP Cool Cash rebates handled</strong><br><span class="update-chip-sub">Up to $1,125 back · we file the paperwork</span></span>
      </a>
      <a class="update-chip" href="/about.html">
        <span class="update-chip-icon" aria-hidden="true">🛡️</span>
        <span><strong>Family-owned · AZ ROC #348556</strong><br><span class="update-chip-sub">Licensed · bonded · insured</span></span>
      </a>
    </div>
  </section>

  <!-- Why us -->
  <section class="section">
    <div class="container">
      <div class="sec-head">
        <span class="eyebrow">Why the North Valley calls us first</span>
        <h2>The HVAC Company Your Neighbors Actually Recommend.</h2>
        <p>We built Instant on a simple idea: treat every home like it's our own, explain what's wrong in plain English, and charge what we said we would.</p>
      </div>
      {why_us_grid()}
    </div>
  </section>

  <!-- Services -->
  <section class="section section-sand">
    <div class="container">
      <div class="sec-head">
        <span class="eyebrow">What we do</span>
        <h2>Full-Service Heating &amp; Cooling for Every Arizona Home.</h2>
        <p>Residential and light commercial. From a tune-up to a new 5-ton system, we handle it.</p>
      </div>
      {services_grid(order=['ac-repair', 'ac-installation', 'ac-maintenance', 'heating-repair', 'commercial-hvac', 'emergency-hvac'])}
      <div class="text-center" style="margin-top:32px"><a class="btn btn-outline" href="/services/">See All Services →</a></div>
    </div>
  </section>

  {club_band()}

  <!-- Reviews — pulled LIVE from Google Places API on every build -->
  <section class="section section-google-reviews" id="reviews">
    <div class="container">
      <div class="sec-head">
        <span class="eyebrow">
          <img src="/assets/img/google-g.svg" alt="" width="18" height="18" class="eyebrow-g">
          Verified Google Reviews
        </span>
        <h2>{SITE['avg_rating']} ★ from {SITE['total_reviews']} Verified Google Reviews</h2>
        <p>Real reviews from real Phoenix-area customers — straight from Google. Updated automatically.</p>
      </div>

      <div class="g-reviews-carousel" data-autoplay="6000" aria-roledescription="carousel" aria-label="Customer reviews from Google">
        <div class="g-reviews-track" tabindex="0">
          {g_rev_cards}
        </div>
        <button type="button" class="g-rev-arrow g-rev-prev" aria-label="Previous review">‹</button>
        <button type="button" class="g-rev-arrow g-rev-next" aria-label="Next review">›</button>
        <div class="g-rev-dots" role="tablist" aria-label="Choose review">
          {"".join(f'<button type="button" role="tab" aria-label="Show review {i+1}" aria-selected="false"></button>' for i in range(len(LIVE_REVIEWS)))}
        </div>
      </div>

      <div class="g-reviews-cta">
        <a class="btn btn-orange" href="{GOOGLE_PROFILE_URL}" target="_blank" rel="noopener" data-track="google_reviews_click">
          See All {SITE['total_reviews']} on Google →
        </a>
        <a class="btn btn-outline" href="/reviews.html">More Customer Stories →</a>
      </div>

      <p class="g-reviews-fineprint">
        Reviews auto-synced from our Google Business Profile. Last refreshed {LAST_FETCHED}.
      </p>
    </div>
  </section>

  <!-- Areas -->
  <section class="section section-sand">
    <div class="container">
      <div class="sec-head">
        <span class="eyebrow">Proudly serving</span>
        <h2>The North Valley and Beyond.</h2>
        <p>From your first call to final walk-through, we show up — anywhere in the greater Phoenix metro.</p>
      </div>
      {area_chips()}
    </div>
  </section>

  <!-- Brands -->
  <section class="section">
    <div class="container">
      <div class="sec-head">
        <span class="eyebrow">All major brands</span>
        <h2>The Equipment You Own — Serviced &amp; Installed.</h2>
      </div>
      {brand_wall()}
    </div>
  </section>

  <!-- FAQ -->
  <section class="section section-sand">
    <div class="container">
      <div class="sec-head">
        <span class="eyebrow">Common questions</span>
        <h2>Answers, Upfront.</h2>
      </div>
      {faq_html(faq_pairs)}
    </div>
  </section>

  {final_cta()}
</main>
{footer()}"""
    write("index.html", head(title, desc, "") + extra_schema + body)

def build_service_hub():
    title = f"HVAC Services in Phoenix & the North Valley | {SITE['name']}"
    desc = "Full-service Phoenix HVAC: AC repair & installation, heating, indoor air quality, 24/7 emergency, commercial. Licensed, bonded, same-day."
    crumbs = [("Home", "/"), ("Services", None)]
    page_schema = jsonld({"@context": "https://schema.org", "@graph": [schema_localbusiness(), schema_breadcrumbs([("Home","/"),("Services","/services/")])]})

    body = f"""{header('/services/')}
<main id="main">
  <div class="crumbs"><div class="container"><a href="/">Home</a> → <b>Services</b></div></div>
  <section class="page-head">
    <div class="container">
      <span class="eyebrow">Every service we offer</span>
      <h1>HVAC Services in Phoenix, AZ</h1>
      <p>From a 2am emergency AC call to a full system replacement, every job we take is backed by a written warranty and flat-rate pricing approved before we start.</p>
    </div>
  </section>
  <section class="section">
    <div class="container">{services_grid()}</div>
  </section>
  {trust_strip()}
  {final_cta()}
</main>
{footer()}"""
    write("services/index.html", head(title, desc, "services/index.html") + page_schema + body)

def build_service_page(svc):
    title = svc['meta_title']
    desc = svc['meta_description']
    crumbs = [("Home","/"),("Services","/services/"),(svc['title_short'], f"/services/{svc['slug']}.html")]

    included = "".join(f"<li>{esc(x)}</li>" for x in svc['included'])
    signs = "".join(f"<li>{esc(x)}</li>" for x in svc['signs'])
    steps = "".join(f'<div class="step"><div class="n">{i+1}</div><h3>{esc(t)}</h3><p>{esc(d)}</p></div>' for i,(t,d) in enumerate(svc['process']))

    related_items = ""
    for rel in svc['related']:
        r = SERVICES_BY_SLUG.get(rel)
        if r:
            related_items += f'<a href="/services/{r["slug"]}.html">{esc(r["title_short"])} <span style="color:var(--orange)">→</span></a>'

    svc_reviews = reviews_for_service(svc['slug'], 2)
    rev_html = '<div class="grid-3">' + "".join(rev_card(r) for r in svc_reviews) + '</div>'

    faq = faq_html(svc['faqs'])

    # Split title_long into lead ("AC Repair") and location ("Phoenix, AZ") for the H1
    if " in " in svc['title_long']:
        lead, location = svc['title_long'].rsplit(" in ", 1)
    else:
        lead, location = svc['title_short'], "Phoenix, AZ"

    page_schema = jsonld({"@context":"https://schema.org","@graph":[
        schema_localbusiness(),
        schema_breadcrumbs([(c[0], c[1]) for c in crumbs]),
        schema_service(svc),
        schema_faq(svc['faqs'])
    ]})

    # Context-aware CTA copy — free estimates are reserved for system replacements
    # and large projects. Repairs, tune-ups, and emergency calls carry a $84.50
    # diagnostic fee (waived with completed repair), so saying "free" would be
    # misleading on those pages.
    cta_type = svc.get('cta_type', 'service_call')
    if cta_type == 'free_estimate':
        cta_button_label  = "Get Free Estimate →"
        cta_aside_heading = "Free In-Home Estimate"
        cta_aside_subtext = "Same-day appointments in Phoenix &amp; Anthem."
    else:  # service_call
        cta_button_label  = "Schedule Service →"
        cta_aside_heading = "Schedule a Service Visit"
        cta_aside_subtext = "Same-day appointments in Phoenix &amp; Anthem. Diagnostic fee waived with any completed repair."

    body = f"""{header('/services/')}
<main id="main">
  <div class="crumbs"><div class="container"><a href="/">Home</a> → <a href="/services/">Services</a> → <b>{esc(svc['title_short'])}</b></div></div>
  <section class="svc-hero">
    <div class="container row">
      <div>
        <span class="eyebrow">Phoenix, AZ · Serving the North Valley</span>
        <h1>{esc(lead)} in <span class="o">{esc(location)}</span></h1>
        <p class="intro">{svc['intro']}</p>
        <div class="kv">
          <div class="i"><b>{esc(svc['pricing_label'])}</b><span>{esc(svc['pricing_value'])} — {esc(svc['pricing_note'])}</span></div>
          <div class="i"><b>Response Time</b><span>Same-day · most emergencies within 4 hrs</span></div>
          <div class="i"><b>Warranty</b><span>{svc.get('warranty_label', '10-year manufacturer parts · labor warranty as paid add-on' if svc.get('cta_type') == 'free_estimate' else '90-day parts warranty on repairs')}</span></div>
          <div class="i"><b>Coverage</b><span>Phoenix, Anthem &amp; North Valley</span></div>
        </div>
        <div class="ctas">
          <button type="button" class="btn btn-orange" data-modal-open="estimate-modal" data-track="estimate_click">{cta_button_label}</button>
          <a class="btn btn-outline" href="tel:{SITE['phone_link']}" data-track="phone_click">📞 {SITE['phone_display']}</a>
        </div>
      </div>
      <aside class="side">
        <h4>{cta_aside_heading}</h4>
        <p>{cta_aside_subtext}</p>
        <div class="price">{esc(svc['pricing_value'])}</div>
        <small>{esc(svc['pricing_label'])} — {esc(svc['pricing_note'])}</small>
        <button type="button" class="btn btn-orange" data-modal-open="estimate-modal" data-track="estimate_click" style="width:100%">{cta_button_label}</button>
        <a class="btn btn-outline-white" href="tel:{SITE['phone_link']}">📞 Call Now</a>
      </aside>
    </div>
  </section>

  <section class="process">
    <div class="container">
      <div class="sec-head">
        <span class="eyebrow">Our 4-step process</span>
        <h2>How We Fix It Right — The First Time.</h2>
      </div>
      <div class="grid">{steps}</div>
    </div>
  </section>

  <section class="section">
    <div class="container">
      <div class="twocol">
        <div>
          <span class="eyebrow">Call us when you notice</span>
          <h2>Signs You Need {esc(svc['title_short'])}.</h2>
          <ul class="checklist">{signs}</ul>
        </div>
        <div>
          <span class="eyebrow">What's included</span>
          <h2>Every {esc(svc['title_short'])} Visit Includes:</h2>
          <ul class="checklist">{included}</ul>
        </div>
      </div>
    </div>
  </section>

  <section class="section section-sand">
    <div class="container">
      <div class="sec-head">
        <span class="eyebrow">Real reviews</span>
        <h2>What Customers Say About Our {esc(svc['title_short'])}.</h2>
      </div>
      {rev_html}
    </div>
  </section>

  <section class="section">
    <div class="container">
      <div class="sec-head">
        <span class="eyebrow">FAQs</span>
        <h2>{esc(svc['title_short'])} Questions, Answered.</h2>
      </div>
      {faq}
    </div>
  </section>

  <section class="section section-sand">
    <div class="container">
      <div class="sec-head">
        <span class="eyebrow">Related services</span>
        <h2>You Might Also Need.</h2>
      </div>
      <div class="related">{related_items}</div>
    </div>
  </section>

  {final_cta()}
</main>
{footer()}"""
    write(f"services/{svc['slug']}.html", head(title, desc, f"services/{svc['slug']}.html") + page_schema + body)

def build_area_hub():
    title = f"HVAC Service Areas | Phoenix, Anthem, North Valley — {SITE['name']}"
    desc = "Instant Heating and Air proudly serves Phoenix, Anthem, New River, Cave Creek, Desert Hills, North Scottsdale, Carefree, Glendale, Peoria, and Surprise."
    cards = ""
    for a in AREAS:
        cards += f"""<a class="svc-card" href="/service-areas/{a['slug']}.html">
  <div class="ic">📍</div>
  <h3>{esc(a['name'])}, AZ</h3>
  <p>{esc(a['landmarks'])}</p>
  <span class="more">See {esc(a['name'])} service →</span>
</a>"""

    page_schema = jsonld({"@context":"https://schema.org","@graph":[
        schema_localbusiness(),
        schema_breadcrumbs([("Home","/"),("Service Areas","/service-areas/")])
    ]})

    # Leaflet CSS in head; Leaflet JS + custom service-map.js loaded after body.
    leaflet_css = (
        '<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" '
        'integrity="sha256-p4NxAoJBhIIN+hmNHrzRCf9tD/miZyoHS5obTRR9BMY=" crossorigin="anonymous">'
    )

    body = f"""{header('/service-areas/')}
<main id="main">
  <div class="crumbs"><div class="container"><a href="/">Home</a> → <b>Service Areas</b></div></div>
  <section class="page-head">
    <div class="container">
      <span class="eyebrow">Phoenix Metro &amp; the North Valley</span>
      <h1>HVAC Service Areas</h1>
      <p>Same-day HVAC service across the greater Phoenix metro. We stage trucks in the North Valley so response times in Anthem, New River, and Desert Hills are measured in minutes — not hours.</p>
    </div>
  </section>

  <!-- Interactive service-area map (Leaflet + OpenStreetMap, red service zone) -->
  <section class="section section-sand" aria-labelledby="service-map-heading">
    <div class="container">
      <div class="sec-head">
        <span class="eyebrow">Where we work</span>
        <h2 id="service-map-heading">Our Phoenix Valley Service Zone.</h2>
        <p>The dashed red zone covers the entire greater Phoenix metro we serve &mdash; including Peoria, Scottsdale, and every city pinned below. Click any pin to jump to that area's page.</p>
      </div>
      <div class="service-map">
        <div id="service-map" role="img" aria-label="Map of the Instant Heating and Air service zone covering the Phoenix Valley"></div>
      </div>
    </div>
  </section>

  <section class="section">
    <div class="container"><div class="svc-grid">{cards}</div></div>
  </section>
  {final_cta()}
  <!-- Leaflet runtime + map init (loaded only on this page) -->
  <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js" integrity="sha256-20nQCchB9co0qIjJZRGuk2/Z9VM+kNiyxNV1lvTlZBo=" crossorigin="anonymous" defer></script>
  <script src="/assets/js/service-map.js?v={ASSET_VERSION}" defer></script>
</main>
{footer()}"""
    write("service-areas/index.html", head(title, desc, "service-areas/index.html", extra_head=leaflet_css) + page_schema + body)

def build_area_page(area):
    title = f"HVAC in {area['name']}, AZ | AC Repair, Install & Heating — {SITE['name']}"
    desc = f"Same-day HVAC service in {area['name']}, AZ. AC repair, installation, heating, and maintenance for every {area['name']} ZIP. Licensed, bonded. Call {SITE['phone_display']}."
    crumbs = [("Home","/"),("Service Areas","/service-areas/"),(area['name'], f"/service-areas/{area['slug']}.html")]

    area_reviews = reviews_for_city(area['slug'], 3)
    rev_html = '<div class="grid-3">' + "".join(rev_card(r) for r in area_reviews) + '</div>'

    service_links = ""
    for s in SERVICES:
        service_links += f'<a href="/services/{s["slug"]}.html">{esc(s["title_short"])} in {esc(area["name"])} →</a><br>'

    zip_list = ", ".join(area['zip_samples'])

    page_schema = jsonld({"@context":"https://schema.org","@graph":[
        schema_localbusiness(),
        schema_breadcrumbs([(c[0], c[1]) for c in crumbs]),
        schema_place(area)
    ]})

    body = f"""{header('/service-areas/')}
<main id="main">
  <div class="crumbs"><div class="container"><a href="/">Home</a> → <a href="/service-areas/">Service Areas</a> → <b>{esc(area['name'])}</b></div></div>
  <section class="svc-hero">
    <div class="container row">
      <div>
        <span class="eyebrow">Serving {esc(area['name'])}, AZ · {esc(zip_list)}</span>
        <h1>HVAC Service in <span class="o">{esc(area['name'])}, AZ</span></h1>
        <p class="intro">{esc(area['local_detail'])}</p>
        <p class="intro">{esc(area['climate_note'])}</p>
        <div class="kv">
          <div class="i"><b>Response</b><span>{esc(area['response_claim'])}</span></div>
          <div class="i"><b>Zip codes</b><span>{esc(zip_list)}</span></div>
          <div class="i"><b>Landmarks</b><span>{esc(area['landmarks'])}</span></div>
          <div class="i"><b>License</b><span>AZ {SITE['license']}</span></div>
        </div>
        <div class="ctas">
          <button type="button" class="btn btn-orange" data-modal-open="estimate-modal" data-track="estimate_click">Get {esc(area['name'])} Estimate →</button>
          <a class="btn btn-outline" href="tel:{SITE['phone_link']}" data-track="phone_click">📞 {SITE['phone_display']}</a>
        </div>
      </div>
      <aside class="side">
        <h4>Service in {esc(area['name'])}</h4>
        <p>Same-day appointments. Most {esc(area['name'])} jobs scheduled the same day you call.</p>
        <p style="font-size:0.875rem;color:#c9d7e3"><strong>Services offered in {esc(area['name'])}:</strong></p>
        <div style="font-size:0.875rem;color:#c9d7e3;line-height:1.8">{service_links}</div>
        <a class="btn btn-orange" href="/book.html" style="margin-top:12px">New AC Quote →</a>
      </aside>
    </div>
  </section>

  <section class="section section-sand">
    <div class="container">
      <div class="sec-head">
        <span class="eyebrow">{esc(area['name'])} reviews</span>
        <h2>What {esc(area['name'])} Homeowners Are Saying.</h2>
      </div>
      {rev_html}
    </div>
  </section>

  <section class="section">
    <div class="container">
      <div class="sec-head">
        <span class="eyebrow">Our services in {esc(area['name'])}</span>
        <h2>Everything We Do — Done Locally.</h2>
        <p>Every service below is offered in {esc(area['name'])} with the same response times, warranties, and flat-rate pricing as our core Phoenix service.</p>
      </div>
      {services_grid()}
    </div>
  </section>

  {final_cta(title_h2=f'Need HVAC Help in <span class="o">{esc(area["name"])}?</span>', p=f"We're stocked, staged, and scheduled to serve {esc(area['name'])} every day of the week. Same-day service is the norm — most emergency calls on-site within 4 hours.")}
</main>
{footer()}"""
    write(f"service-areas/{area['slug']}.html", head(title, desc, f"service-areas/{area['slug']}.html") + page_schema + body)

def build_about():
    title = f"About Instant Heating and Air | Family-Owned Phoenix HVAC"
    desc = "Locally owned Phoenix HVAC serving Phoenix, Anthem, and the North Valley. Licensed, bonded, and built on honest pricing and written warranties."
    body = f"""{header('/about.html')}
<main id="main">
  <div class="crumbs"><div class="container"><a href="/">Home</a> → <b>About</b></div></div>
  <section class="page-head">
    <div class="container">
      <span class="eyebrow">About {esc(SITE['name'])}</span>
      <h1>Professionals You Can Trust.</h1>
      <p>We started Instant Heating and Air with one simple idea: treat every home like it's our own, charge what we said we would, and explain the work in plain English.</p>
    </div>
  </section>
  <section class="section">
    <div class="container" style="max-width:820px">
      <div class="prose">
        <h2>Who we are</h2>
        <p>We're a family-owned, locally-operated HVAC contractor based in north Phoenix, serving Phoenix, Anthem, and every community across the North Valley. Every technician on our team is licensed, insured, background-checked, and lives in the area we serve. That matters — because we know the floor plans, the climate, and the quirks of the homes we work on.</p>

        <h2>How we're different</h2>
        <p>The big-name HVAC shops in the Valley got big by being everywhere, advertising constantly, and running a script at the kitchen table. That's not us. We've intentionally stayed small enough to keep our standards tight: same-day service, flat-rate pricing approved before work begins, written warranties, and clean trucks that show up when we said they would.</p>
        <p>Our technicians are paid on flat rate — not on how much they sell you. That single structural decision removes every incentive to upsell, panic-sell, or recommend a new system when a $200 capacitor is the actual answer.</p>

        <h2>Our values</h2>
        <ul>
          <li><strong>Honesty:</strong> You see the price before we start. If we can't fix it for what we quoted, that's on us — not you.</li>
          <li><strong>Craft:</strong> Every install is done to code, commissioned properly, and documented in writing.</li>
          <li><strong>Respect:</strong> Shoe covers, drop cloths, clean trucks, on-time arrivals, text-before-we-show-up courtesy.</li>
          <li><strong>Accountability:</strong> Every repair and install is backed by a written warranty. If it fails, we come back.</li>
        </ul>

        <h2>Credentials</h2>
        <p>Arizona ROC License #348556. Fully licensed, bonded, and insured. EPA-certified technicians. Ongoing training on every major residential brand — Carrier, Trane, Lennox, Goodman, Rheem, Amana, Bryant, American Standard, York, Daikin, and Mitsubishi.</p>

        <h2>Our promise</h2>
        <p>Your comfort is our obsession. That's not a slogan — that's the single organizing principle for every decision we make, from which trucks we buy to which parts we stock to how we talk to you in your kitchen. If we ever fall short of it, tell us. We'll fix it.</p>
      </div>
    </div>
  </section>
  {club_band()}
  {final_cta()}
</main>
{footer()}"""
    page_schema = jsonld({"@context":"https://schema.org","@graph":[schema_localbusiness(), schema_breadcrumbs([("Home","/"),("About","/about.html")])]})
    write("about.html", head(title, desc, "about.html") + page_schema + body)

def build_reviews():
    title = f"Reviews | {SITE['name']} — 5-Star Rated HVAC in Phoenix"
    desc = "Read real customer reviews of Instant Heating and Air. Phoenix and Anthem homeowners on honest pricing, fast response, and professional service."
    rev_cards = "".join(f'<div>{rev_card(r)}</div>' for r in REVIEWS)
    body = f"""{header('/reviews.html')}
<main id="main">
  <div class="crumbs"><div class="container"><a href="/">Home</a> → <b>Reviews</b></div></div>
  <section class="page-head">
    <div class="container">
      <span class="eyebrow">{SITE['avg_rating']} ★ · Verified Google Reviews</span>
      <h1>What Your Neighbors Say.</h1>
      <p>Reviews from real Phoenix, Anthem, and North Valley homeowners. We'll never use a review we didn't earn.</p>
    </div>
  </section>
  <section class="section">
    <div class="container"><div class="grid-3">{rev_cards}</div></div>
  </section>
  {final_cta()}
</main>
{footer()}"""
    review_schemas = [schema_review(r) for r in REVIEWS]
    page_schema = jsonld({"@context":"https://schema.org","@graph":[
        schema_localbusiness(),
        schema_breadcrumbs([("Home","/"),("Reviews","/reviews.html")]),
        *review_schemas
    ]})
    write("reviews.html", head(title, desc, "reviews.html") + page_schema + body)

def build_maintenance_plan():
    title = "The $18/mo Comfort Club | HVAC Maintenance Plan | Instant Heating and Air"
    desc = "$18/mo HVAC maintenance plan in Phoenix. Two tune-ups/year, 15% off repairs, priority dispatch, no overtime fees. Cancel anytime."
    body = f"""{header('/maintenance-plan.html')}
<main id="main">
  <div class="crumbs"><div class="container"><a href="/">Home</a> → <b>Comfort Club</b></div></div>
  <section class="hero" style="padding:60px 0 70px">
    <div class="container" style="max-width:760px;text-align:center">
      <span class="badge">The Comfort Club</span>
      <h1>$18 a Month. <span class="o">Peace of Mind.</span></h1>
      <p class="lead" style="margin:0 auto 26px">Two precision tune-ups a year, 15% off all repairs, priority dispatch, no overtime charges. Pays for itself the first time we catch something before summer does.</p>
      <div class="ctas" style="justify-content:center">
        <button type="button" class="btn btn-orange" data-modal-open="comfort-modal" data-track="comfort_club_click">Sign Me Up →</button>
        <a class="btn btn-outline-white" href="tel:{SITE['phone_link']}">📞 {SITE['phone_display']}</a>
      </div>
    </div>
  </section>

  <!-- Comfort Club signup modal — opens via [data-modal-open="comfort-modal"] -->
  <div class="modal" id="comfort-modal" aria-hidden="true">
    <div class="modal-backdrop" data-modal-close></div>
    <div class="modal-dialog" role="dialog" aria-labelledby="cc-heading" aria-modal="true">
      <button type="button" class="modal-close" data-modal-close aria-label="Close form">&times;</button>

      <form class="club-signup ajax-form" id="comfort-form" action="{SITE['form_endpoints']['comfort_club']}" method="POST">
        <h3 id="cc-heading">Sign Up in 30 Seconds</h3>
        <input type="hidden" name="_subject" value="Comfort Club Signup — Instant Heating and Air">
        <input type="hidden" name="_template" value="table">
        <input type="hidden" name="_captcha" value="false">
        <input type="hidden" name="_next" value="{SITE['success_redirect']}">
        <input type="hidden" name="form_type" value="comfort_club">
        <input type="text" name="_honey" class="hp-field" tabindex="-1" autocomplete="off" aria-hidden="true">
        <div class="hp-field" aria-hidden="true">
          <label>Website (leave blank)</label>
          <input type="text" name="website" tabindex="-1" autocomplete="off">
        </div>

        <div class="cc-field">
          <label for="cc-name">Full name</label>
          <input id="cc-name" name="name" type="text" required minlength="2" autocomplete="name" placeholder="Your name">
        </div>

        <div class="cc-row2">
          <div class="cc-field">
            <label for="cc-phone">Phone</label>
            <input id="cc-phone" name="phone" type="tel" required pattern="[\\d\\s().+\\-]{{10,}}" autocomplete="tel" placeholder="(623) 555-0123" title="Please enter a valid phone number (at least 10 digits)">
          </div>
          <div class="cc-field">
            <label for="cc-email">Email</label>
            <input id="cc-email" name="email" type="email" required autocomplete="email" placeholder="you@email.com">
          </div>
        </div>

        <div class="cc-field">
          <label for="cc-address">Service address</label>
          <input id="cc-address" name="address" type="text" required minlength="10" autocomplete="street-address" placeholder="Street, City, AZ ZIP" title="Please enter your full street address including city and ZIP">
        </div>

        <div class="cc-row2">
          <div class="cc-field">
            <label for="cc-systems">How many systems?</label>
            <select id="cc-systems" name="systems">
              <option value="1">1 system — $18/mo</option>
              <option value="2">2 systems — $36/mo</option>
              <option value="3">3 systems — $54/mo</option>
              <option value="4+">4 or more — call for pricing</option>
            </select>
          </div>
          <div class="cc-field">
            <label for="cc-when">Best time to call</label>
            <select id="cc-when" name="best_time">
              <option value="anytime">Any time today</option>
              <option value="morning">Morning</option>
              <option value="afternoon">Afternoon</option>
              <option value="evening">Evening</option>
              <option value="weekend">Weekend</option>
            </select>
          </div>
        </div>

        <div class="cc-field">
          <label for="cc-notes">Anything we should know? <span class="cc-optional">(optional)</span></label>
          <textarea id="cc-notes" name="notes" rows="2" placeholder="System age, recent issues, second home, etc."></textarea>
        </div>

        <button type="submit" class="btn btn-orange cc-submit">Sign Me Up →</button>
        <p class="cc-foot">We'll call within 1 business day to confirm and schedule your first tune-up. No charge until that visit.</p>
      </form>

      <div class="modal-success" hidden>
        <div class="modal-success-icon" aria-hidden="true">&#10003;</div>
        <h3>You're In!</h3>
        <p>We got your info. A real human will call within one business day to confirm and schedule your first tune-up.</p>
        <p style="font-size:0.875rem">If it's urgent, call us at <a href="tel:{SITE['phone_link']}">{SITE['phone_display']}</a>.</p>
        <button type="button" class="btn btn-orange" data-modal-close>Done</button>
      </div>
    </div>
  </div>
  <section class="section">
    <div class="container">
      <div class="twocol">
        <div>
          <span class="eyebrow">Everything included</span>
          <h2>What You Get — Every Year.</h2>
          <ul class="checklist">
            <li>One precision spring AC tune-up</li>
            <li>One precision fall heating tune-up</li>
            <li>15% off any and all repairs</li>
            <li>Priority dispatch (same-day guaranteed)</li>
            <li>No overtime or after-hours charges</li>
            <li>No trip charges</li>
            <li>Extended warranty credit</li>
            <li>Annual service history on file — kept forever</li>
          </ul>
        </div>
        <div>
          <span class="eyebrow">The fine print (there isn't much)</span>
          <h2>How the Plan Works.</h2>
          <ul class="checklist">
            <li>$18/month per system — flat rate</li>
            <li>Billed monthly — cancel any time, no penalty</li>
            <li>Members get a no-breakdown guarantee between tune-ups</li>
            <li>Plan transfers with you if you sell the home</li>
            <li>No hidden fees, no contracts, no deductibles</li>
          </ul>
        </div>
      </div>
    </div>
  </section>
  <section class="section section-sand">
    <div class="container">
      <div class="sec-head">
        <span class="eyebrow">Frequently asked</span>
        <h2>Is the Comfort Club Worth It?</h2>
      </div>
      {faq_html([
        ("Is $18/month really worth it?", "For most Phoenix homes, yes — and by a wide margin. Two tune-ups at retail are $198. The club is $216/year and includes 15% repair discounts, priority dispatch, and no overtime. A single avoided summer breakdown pays for 3+ years of membership."),
        ("Can I cancel?", "Any time — no penalty, no phone tree. Just send us a note or call."),
        ("What if I have more than one system?", "Each system is $18/mo — flat rate. So 2 systems is $36/mo, 3 is $54/mo. Same benefits per system."),
        ("Is there a contract?", "No. We're confident enough in the service that we don't need to lock you in."),
        ("Does it transfer if I sell the home?", "Yes. New owner keeps the plan for the balance of the year — or cancels.")
      ])}
    </div>
  </section>
  {final_cta(title_h2='Start Saving Right <span class="o">Now.</span>', p="Sign up online in 2 minutes or call and we'll set it up in 30 seconds.")}
</main>
{footer()}"""
    faq_pairs = [
        ("Is $18/month really worth it?", "For most Phoenix homes, yes — and by a wide margin. Two tune-ups at retail are $198. The club is $216/year and includes 15% repair discounts, priority dispatch, and no overtime. A single avoided summer breakdown pays for 3+ years of membership."),
        ("Can I cancel?", "Any time — no penalty, no phone tree. Just send us a note or call."),
        ("What if I have more than one system?", "Each system is $18/mo — flat rate. So 2 systems is $36/mo, 3 is $54/mo. Same benefits per system."),
        ("Is there a contract?", "No. We're confident enough in the service that we don't need to lock you in."),
        ("Does it transfer if I sell the home?", "Yes. New owner keeps the plan for the balance of the year — or cancels.")
    ]
    page_schema = jsonld({"@context":"https://schema.org","@graph":[schema_localbusiness(), schema_breadcrumbs([("Home","/"),("Comfort Club","/maintenance-plan.html")]), schema_faq(faq_pairs)]})
    write("maintenance-plan.html", head(title, desc, "maintenance-plan.html") + page_schema + body)

def build_financing():
    title = "HVAC Financing in Phoenix | 0% APR Options | Instant Heating and Air"
    desc = "Flexible HVAC financing in Phoenix — 0% APR options, 12–120 month terms, quick approval. Make new installs affordable from $109/mo OAC."
    body = f"""{header('/financing.html')}
<main id="main">
  <div class="crumbs"><div class="container"><a href="/">Home</a> → <b>Financing</b></div></div>
  <section class="page-head">
    <div class="container">
      <span class="eyebrow">Make comfort affordable</span>
      <h1>HVAC Financing That Actually Works.</h1>
      <p>A new AC or heating system shouldn't mean draining your savings. We partner with top HVAC financing providers to offer competitive monthly payment plans — 0% APR for qualified buyers, terms up to 120 months, quick approvals that don't hammer your credit.</p>
    </div>
  </section>
  <section class="section">
    <div class="container">
      <div class="twocol">
        <div>
          <span class="eyebrow">How it works</span>
          <h2>Three Simple Steps.</h2>
          <ol class="checklist" style="list-style:decimal;padding-left:20px">
            <li>Apply online in about 2 minutes — soft credit pull, no hard-check ding.</li>
            <li>Get instant approval decisions most cases.</li>
            <li>Sign, we install, you pay monthly — no surprises.</li>
          </ol>
          <p style="margin-top:24px"><a class="btn btn-orange" href="/contact.html">Start Your Application →</a></p>
        </div>
        <div>
          <span class="eyebrow">Typical payments</span>
          <h2>What It Costs Per Month.</h2>
          <ul class="checklist">
            <li>$7,800 install → from $109/mo (60 mo)</li>
            <li>$10,500 install → from $147/mo (60 mo)</li>
            <li>$14,000 install → from $196/mo (60 mo)</li>
            <li>0% APR for 18–24 months for qualifying customers</li>
            <li>Deferred payment options available</li>
          </ul>
          <p style="font-size:0.8125rem;color:var(--mute)">All payment examples are on approved credit. Actual terms based on creditworthiness and lender requirements.</p>
        </div>
      </div>
    </div>
  </section>
  {final_cta()}
</main>
{footer()}"""
    page_schema = jsonld({"@context":"https://schema.org","@graph":[schema_localbusiness(), schema_breadcrumbs([("Home","/"),("Financing","/financing.html")])]})
    write("financing.html", head(title, desc, "financing.html") + page_schema + body)

def build_contact():
    title = f"Contact Instant Heating and Air | Phoenix HVAC | {SITE['phone_display']}"
    # Drop email from meta description so Cloudflare's auto email-obfuscation
    # doesn't mangle the description into garbage text in search snippets.
    desc = f"Contact Instant Heating and Air in Phoenix, AZ. Call {SITE['phone_display']}, send a message, or book online. 24/7 emergency service across Phoenix and the North Valley."
    body = f"""{header('/contact.html')}
<main id="main">
  <div class="crumbs"><div class="container"><a href="/">Home</a> → <b>Contact</b></div></div>
  <section class="page-head">
    <div class="container">
      <span class="eyebrow">We pick up the phone</span>
      <h1>Get in Touch.</h1>
      <p>Call, text, email, or book online — whichever is easiest. Someone human will respond during business hours; 24/7 for emergencies.</p>
    </div>
  </section>
  <section class="section">
    <div class="container" style="max-width:1000px">
      <div class="twocol">
        <div>
          <h2>Contact</h2>
          <p><strong>Phone:</strong> <a href="tel:{SITE['phone_link']}" data-track="phone_click">{SITE['phone_display']}</a> (24/7 for emergencies)</p>
          <p><strong>Message us:</strong> use the contact form on this page &mdash; goes straight to our service team and we reply within one business day.</p>
          <p><strong>Address:</strong><br>{SITE['address']['street']}<br>{SITE['address']['city']}, {SITE['address']['region']} {SITE['address']['postal']}</p>
          <p><strong>Hours:</strong> {SITE['hours']}</p>
          <p><strong>License:</strong> AZ {SITE['license']} · Licensed · Bonded · Insured</p>
          <h3 style="margin-top:32px">Follow us</h3>
          <p><a href="{SITE['social']['facebook']}" rel="noopener">Facebook</a> · <a href="{SITE['social']['instagram']}" rel="noopener">Instagram</a> · <a href="{SITE['social']['yelp']}" rel="noopener">Yelp</a> · <a href="{SITE['social']['nextdoor']}" rel="noopener">Nextdoor</a></p>
        </div>
        <div>
          <h2>Send us a note</h2>
          <form action="{SITE['form_endpoints']['contact']}" method="POST" class="standard timed-form" id="contact-form" aria-label="Contact form">
            <input type="hidden" name="_subject" value="Contact form — Instant Heating and Air">
            <input type="hidden" name="_template" value="table">
            <input type="hidden" name="_captcha" value="false">
            <input type="hidden" name="_next" value="{SITE['success_redirect']}">
            <input type="hidden" name="form_type" value="contact_page">
            <input type="text" name="_honey" class="hp-field" tabindex="-1" autocomplete="off" aria-hidden="true">
            <div class="hp-field" aria-hidden="true">
              <label>Website (leave blank)</label>
              <input type="text" name="website" tabindex="-1" autocomplete="off">
            </div>
            <label for="c-name">Name</label>
            <input id="c-name" name="name" required minlength="2" autocomplete="name">
            <label for="c-email">Email</label>
            <input id="c-email" name="email" type="email" required autocomplete="email">
            <label for="c-phone">Phone</label>
            <input id="c-phone" name="phone" type="tel" pattern="[\\d\\s().+\\-]{{10,}}" autocomplete="tel" title="Please enter a valid phone number (at least 10 digits)">
            <label for="c-msg">How can we help?</label>
            <textarea id="c-msg" name="message" required minlength="10" title="Please give us a brief description (at least 10 characters)"></textarea>
            <button type="submit" class="btn btn-orange">Send Message</button>
          </form>
          <div class="modal-success" hidden style="text-align:left;padding:20px 0">
            <h3 style="color:var(--success)">Got It!</h3>
            <p>Your message is in. We'll respond within one business day.</p>
          </div>
        </div>
      </div>
    </div>
  </section>
  {final_cta()}
</main>
{footer()}"""
    page_schema = jsonld({"@context":"https://schema.org","@graph":[schema_localbusiness(), schema_breadcrumbs([("Home","/"),("Contact","/contact.html")])]})
    write("contact.html", head(title, desc, "contact.html") + page_schema + body)

def build_book():
    title = f"Get a Free HVAC Replacement Estimate | {SITE['name']} Phoenix HVAC"
    desc = "Get an instant estimate on a new HVAC system in about 90 seconds. Free in-home quotes on system replacements across Phoenix and the North Valley. Repair calls carry an $84.50 diagnostic fee, waived with completed repair."
    body = f"""{header('/book.html')}
<main id="main">
  <div class="crumbs"><div class="container"><a href="/">Home</a> → <b>Get an Estimate</b></div></div>
  <section class="page-head">
    <div class="container">
      <span class="eyebrow">No calls · no pressure · for new systems</span>
      <h1>Get a Free <span class="o">Replacement</span> Estimate.</h1>
      <p>Pricing a new AC, furnace, or heat pump? Answer a few quick questions and we'll show you honest pricing — the same numbers we'd give our own family. Already have a unit acting up? Repair visits are <a href="/contact.html" style="color:#fff;text-decoration:underline">scheduled here</a> with an $84.50 diagnostic fee that we waive the moment you approve the repair.</p>
    </div>
  </section>
  <section class="section" aria-labelledby="quote-tool-h2" itemscope itemtype="https://schema.org/WebApplication">
    <meta itemprop="name" content="Instant HVAC Quote Tool">
    <meta itemprop="applicationCategory" content="BusinessApplication">
    <meta itemprop="operatingSystem" content="Web Browser">
    <div class="container" style="max-width:920px">
      <h2 id="quote-tool-h2" class="visually-hidden">Free Instant HVAC Replacement Quote Tool</h2>
      <p class="visually-hidden" itemprop="description">
        Online HVAC pricing tool. Get an instant, itemized estimate for a new
        air conditioner, furnace, heat pump, or dual-fuel system in your
        Phoenix-area home in about 90 seconds — no phone call, no pressure.
      </p>
      <div class="quote-wrap">
        <iframe src="{SITE['quote_tool_url']}"
                title="Instant Heating and Air — free HVAC replacement estimate tool"
                loading="lazy"
                allow="clipboard-write"
                sandbox="allow-forms allow-scripts allow-popups allow-popups-to-escape-sandbox allow-same-origin"
                referrerpolicy="strict-origin-when-cross-origin"
                itemprop="url"></iframe>
        <noscript>
          <div class="quote-noscript">
            <p><strong>JavaScript is disabled — but the quote tool needs it to run.</strong>
            Open the instant HVAC replacement estimate tool directly:</p>
            <p><a href="{SITE['quote_tool_url']}" rel="noopener">Free instant HVAC quote &rarr;</a> &nbsp;or&nbsp;
            <a href="tel:{SITE['phone_link']}">call {SITE['phone_display']}</a> for a free in-home estimate.</p>
          </div>
        </noscript>
      </div>
      <p class="quote-fallback">Having trouble seeing the form? <a href="{SITE['quote_tool_url']}" target="_blank" rel="noopener">Open it in a new tab →</a> · Or call <a href="tel:{SITE['phone_link']}">{SITE['phone_display']}</a> — we pick up 24/7 for emergencies.</p>
    </div>
  </section>
  {final_cta()}
</main>
{footer()}"""
    page_schema = jsonld({"@context":"https://schema.org","@graph":[
        schema_localbusiness(),
        schema_breadcrumbs([("Home","/"),("Get an Estimate","/book.html")]),
        schema_quote_tool(SITE['base_url'] + "/book.html")
    ]})
    write("book.html", head(title, desc, "book.html") + page_schema + body)

# ---------------------------------------------------------------------------
# Blog
# ---------------------------------------------------------------------------

def render_block(block):
    kind, content = block
    if kind == "h2":
        return f"<h2>{esc(content)}</h2>"
    if kind == "h3":
        return f"<h3>{esc(content)}</h3>"
    if kind == "p":
        return f"<p>{content}</p>"  # may contain HTML
    if kind == "ul":
        return "<ul>" + "".join(f"<li>{esc(i)}</li>" for i in content) + "</ul>"
    if kind == "table":
        rows = ""
        for i, row in enumerate(content):
            tag = "th" if i == 0 else "td"
            rows += "<tr>" + "".join(f"<{tag}>{esc(c)}</{tag}>" for c in row) + "</tr>"
        return f"<table>{rows}</table>"
    return ""

def build_post(post):
    title = f"{post['title']} | {SITE['name']} Blog"
    desc = post['meta_description']
    body_html = "".join(render_block(b) for b in post['body'])

    related = SERVICES_BY_SLUG.get(post.get('related_service'))
    related_cta = ""
    if related:
        related_cta = f"""<section class="section section-sand">
  <div class="container" style="max-width:820px;text-align:center">
    <span class="eyebrow">Related service</span>
    <h2>Need {esc(related['title_short'])}?</h2>
    <p style="color:var(--mute);margin-bottom:20px">{esc(related['short_desc'])}</p>
    <a class="btn btn-orange" href="/services/{related['slug']}.html">Learn About {esc(related['title_short'])} →</a>
  </div>
</section>"""

    crumbs = [("Home","/"),("Blog","/blog/"),(post['title'], f"/blog/{post['slug']}.html")]
    page_schema = jsonld({"@context":"https://schema.org","@graph":[schema_localbusiness(), schema_breadcrumbs([(c[0], c[1]) for c in crumbs]), schema_article(post)]})

    # Build the byline. Always show Published; if the post has been genuinely
    # updated (post['updated'] > post['date']), show a second "Updated" line
    # so visitors AND Google can tell the content is fresh.
    pub_iso = post['date']
    upd_iso = post.get('updated', pub_iso)
    byline = (
        f'<span class="eyebrow">{esc(post["category"])} · '
        f'Published <time datetime="{esc(pub_iso)}">{esc(_fmt_date(pub_iso))}</time>'
    )
    if upd_iso and upd_iso != pub_iso:
        byline += (
            f' · Updated <time datetime="{esc(upd_iso)}">{esc(_fmt_date(upd_iso))}</time>'
        )
    byline += '</span>'

    body = f"""{header('/blog/')}
<main id="main">
  <div class="crumbs"><div class="container"><a href="/">Home</a> → <a href="/blog/">Blog</a> → <b>{esc(post['category'])}</b></div></div>
  <article>
    <header class="page-head">
      <div class="container" style="max-width:820px">
        {byline}
        <h1>{esc(post['title'])}</h1>
        <p>{esc(post['hero_dek'])}</p>
      </div>
    </header>
    <section class="section">
      <div class="container"><div class="prose">{body_html}</div></div>
    </section>
  </article>
  {related_cta}
  {final_cta()}
</main>
{footer()}"""
    write(f"blog/{post['slug']}.html", head(title, desc, f"blog/{post['slug']}.html", og_type="article") + page_schema + body)

def build_blog_index():
    title = f"Phoenix HVAC Blog | {SITE['name']}"
    desc = "Tips, decision guides, and honest HVAC advice from licensed Phoenix technicians. Written for homeowners, not salespeople."
    cards = ""
    for p in POSTS:
        pub_iso = p['date']
        upd_iso = p.get('updated', pub_iso)
        # Show updated date if newer than published, else show published
        card_date_iso = upd_iso if upd_iso != pub_iso else pub_iso
        card_date_label = ("Updated " if upd_iso != pub_iso else "") + _fmt_date(card_date_iso)
        cards += f"""<a class="svc-card" href="/blog/{p['slug']}.html">
  <div class="ic">📝</div>
  <h3>{esc(p['title'])}</h3>
  <p>{esc(p['hero_dek'])}</p>
  <span class="post-card-date"><time datetime="{esc(card_date_iso)}">{esc(card_date_label)}</time> · {esc(p['category'])}</span>
  <span class="more">Read more →</span>
</a>"""
    body = f"""{header('/blog/')}
<main id="main">
  <div class="crumbs"><div class="container"><a href="/">Home</a> → <b>Blog</b></div></div>
  <section class="page-head">
    <div class="container">
      <span class="eyebrow">Tips &amp; guides</span>
      <h1>Phoenix HVAC Blog.</h1>
      <p>Written for homeowners, not salespeople. Decision guides, buying advice, and honest answers to the questions you didn't know to ask.</p>
    </div>
  </section>
  <section class="section">
    <div class="container"><div class="svc-grid">{cards}</div></div>
  </section>
  {final_cta()}
</main>
{footer()}"""
    page_schema = jsonld({"@context":"https://schema.org","@graph":[schema_localbusiness(), schema_breadcrumbs([("Home","/"),("Blog","/blog/")])]})
    write("blog/index.html", head(title, desc, "blog/index.html") + page_schema + body)

# ---------------------------------------------------------------------------
# Legal pages
# ---------------------------------------------------------------------------

def build_legal(slug, h1, intro, sections):
    title = f"{h1} | {SITE['name']}"
    desc = f"{h1} for {SITE['legal_name']}."
    sec_html = ""
    for h, body in sections:
        sec_html += f"<h2>{esc(h)}</h2><p>{body}</p>"
    body_html = f"""{header('/'+slug)}
<main id="main">
  <div class="crumbs"><div class="container"><a href="/">Home</a> → <b>{esc(h1)}</b></div></div>
  <section class="page-head">
    <div class="container"><h1>{esc(h1)}</h1><p>{esc(intro)}</p></div>
  </section>
  <section class="section"><div class="container"><div class="prose">{sec_html}</div></div></section>
</main>
{footer()}"""
    page_schema = jsonld({"@context":"https://schema.org","@graph":[schema_localbusiness(), schema_breadcrumbs([("Home","/"),(h1, "/"+slug)])]})
    write(slug, head(title, desc, slug) + page_schema + body_html)

def build_thanks():
    title = f"Thanks — We Got It | {SITE['name']}"
    desc = "Thanks for reaching out. We'll be in touch within one business day."
    body = f"""{header()}
<main id="main">
  <section class="page-head" style="text-align:center;padding:90px 0">
    <div class="container">
      <span class="eyebrow">You're in</span>
      <h1>Thanks — We Got It.</h1>
      <p style="margin:0 auto;max-width:540px">A real human will call or email within one business day to confirm your details and schedule your first visit. If it's urgent or after hours, call us at <a href="tel:{SITE['phone_link']}" style="color:#FFC78F">{SITE['phone_display']}</a>.</p>
      <div style="margin-top:28px">
        <a class="btn btn-orange" href="/">← Back to Home</a>
      </div>
    </div>
  </section>
</main>
{footer()}"""
    page_schema = jsonld({"@context":"https://schema.org","@graph":[schema_localbusiness()]})
    write("thanks.html", head(title, desc, "thanks.html") + page_schema + body)


def build_404():
    title = "Page Not Found | " + SITE['name']
    desc = "The page you're looking for isn't here."
    body = f"""{header()}
<main id="main">
  <section class="page-head" style="text-align:center;padding:100px 0">
    <div class="container">
      <h1>404 — Page Not Found</h1>
      <p>This page doesn't exist. But our AC techs do, and they're ready to help.</p>
      <div style="margin-top:24px">
        <a class="btn btn-orange" href="/">← Back to Home</a>
        <a class="btn btn-outline" href="tel:{SITE['phone_link']}" style="margin-left:10px">📞 {SITE['phone_display']}</a>
      </div>
    </div>
  </section>
</main>
{footer()}"""
    write("404.html", head(title, desc, "404.html") + body)

# ---------------------------------------------------------------------------
# Sitemap / robots / manifest
# ---------------------------------------------------------------------------

def build_sitemap():
    """Sitemap with per-URL <lastmod>, per-URL image entries, and the
    image sitemap namespace so Google Images can index photos alongside pages.

    lastmod uses the current build time — every deploy triggers a full
    rebuild, so all URLs are legitimately "modified" at build time. This
    signals freshness to Google (higher crawl priority) without lying.

    Each URL includes one or more <image:image> entries so photos on that
    page (service hero shot, brand logos, OG banner) get indexed. Image
    search sends real traffic for HVAC — "AC coil freezing" queries surface
    photo results.
    """
    base = SITE['base_url']
    lastmod = time.strftime("%Y-%m-%d", time.gmtime())
    og_image = f"{base}/assets/img/og-image.jpg"
    logo_image = f"{base}/assets/img/logo-full.png"

    # (path, priority, [image_urls])
    urls = [
        ("/",                        "1.0", [og_image, logo_image, f"{base}/assets/img/rooftop-banner.jpg"]),
        ("/about.html",              "0.7", [og_image, logo_image]),
        ("/contact.html",            "0.7", [og_image]),
        ("/book.html",               "0.9", [og_image]),
        ("/reviews.html",            "0.6", [og_image]),
        ("/maintenance-plan.html",   "0.8", [og_image]),
        ("/financing.html",          "0.6", [og_image]),
        ("/services/",               "0.9", [og_image]),
        ("/service-areas/",          "0.9", [og_image]),
        ("/blog/",                   "0.6", [og_image]),
        ("/privacy.html",            "0.2", []),
        ("/terms.html",              "0.2", []),
        ("/accessibility.html",      "0.2", []),
    ]
    for s in SERVICES:
        svc_img = s.get('bg_image', '')
        imgs = [f"{base}{svc_img}"] if svc_img else [og_image]
        urls.append((f"/services/{s['slug']}.html", "0.9", imgs))
    for a in AREAS:
        urls.append((f"/service-areas/{a['slug']}.html", "0.9", [og_image]))
    for p in POSTS:
        urls.append((f"/blog/{p['slug']}.html", "0.6", [og_image]))

    xml = '<?xml version="1.0" encoding="UTF-8"?>\n'
    xml += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"\n'
    xml += '        xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">\n'
    for path, pri, images in urls:
        xml += f'  <url>\n'
        xml += f'    <loc>{base}{path}</loc>\n'
        xml += f'    <lastmod>{lastmod}</lastmod>\n'
        xml += f'    <changefreq>weekly</changefreq>\n'
        xml += f'    <priority>{pri}</priority>\n'
        for img in images:
            xml += f'    <image:image><image:loc>{img}</image:loc></image:image>\n'
        xml += f'  </url>\n'
    xml += '</urlset>\n'
    write("sitemap.xml", xml)

def build_robots():
    txt = f"""User-agent: *
Allow: /
Disallow: /api/
Disallow: /admin/

Sitemap: {SITE['base_url']}/sitemap.xml
"""
    write("robots.txt", txt)


def build_chatbot_knowledge():
    """Emit /assets/data/iha-knowledge.json — a single portable JSON file
    that consolidates everything the chatbot widget (and any downstream
    LLM / external integration) needs to know about Instant Heating and Air.

    Anyone integrating downstream can fetch this URL and have:
      - company metadata (NAP, license, hours)
      - the full live service catalog with pricing + FAQs + warranty per service
      - service areas with ZIPs + landmarks + response promises
      - brands serviced + 2026 incentive landscape
      - 20+ pre-built intents with patterns, responses, and action chips
      - quick-reply chips for warm-start UX
      - an LLM system prompt to plug straight into a custom GPT or RAG pipeline
    """
    knowledge = {
        "version": "1.0.0",
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "company": {
            "name": SITE['name'],
            "legal_name": SITE['legal_name'],
            "tagline": SITE['tagline'],
            "mission": SITE['mission'],
            "phone_display": SITE['phone_display'],
            "phone_link": SITE['phone_link'],
            "email": SITE['email'],
            "domain": SITE['domain'],
            "base_url": SITE['base_url'],
            "address": SITE['address'],
            "license": SITE['license'],
            "hours": SITE['hours'],
            "founded_year": SITE['founded_year'],
            "service_radius_miles": SITE['service_radius_miles'],
            "rating": float(SITE['avg_rating']),
            "review_count": int(SITE['total_reviews']),
            "google_profile_url": GOOGLE_PROFILE_URL,
            "booking_url": SITE['booking_url'],
            "quote_tool_url": SITE['quote_tool_url'],
            "social": SITE['social'],
        },
        "services": [
            {
                "slug": s['slug'],
                "name": s['title_short'],
                "title_long": s['title_long'],
                "short_desc": s['short_desc'],
                "url": f"/services/{s['slug']}.html",
                "keywords": s.get('keywords', []),
                "pricing": {
                    "label": s['pricing_label'],
                    "value": s['pricing_value'],
                    "note": s['pricing_note'],
                },
                "cta_type": s.get('cta_type', ''),
                "warranty": s.get('warranty_label', ''),
                "included": s.get('included', []),
                "signs_you_need_this": s.get('signs', []),
                "process": [{"step": p[0], "description": p[1]} for p in s.get('process', [])],
                "faqs": [{"q": q, "a": a} for (q, a) in s.get('faqs', [])],
            }
            for s in SERVICES
        ],
        "service_areas": [
            {
                "slug": a['slug'],
                "name": a['name'],
                "url": f"/service-areas/{a['slug']}.html",
                "zip_samples": a.get('zip_samples', []),
                "landmarks": a.get('landmarks', ''),
                "lat": a.get('lat'),
                "lng": a.get('lng'),
                "climate_note": a.get('climate_note', ''),
                "response_claim": a.get('response_claim', ''),
                "local_detail": a.get('local_detail', ''),
            }
            for a in AREAS
        ],
        "brands_serviced": SITE.get('brands_serviced', []),
        "homepage_faqs": [{"q": f['q'], "a": f['a']} for f in HOME_FAQ],
        "incentives_2026": {
            "srp_cool_cash": "Active. Pays $75/ton single-stage, $150/ton two-stage, $225/ton variable-speed (up to $1,125 on 5-ton variable-speed). We file the paperwork for SRP customers at no charge.",
            "aps_rebates": "Ended January 1, 2026. APS-territory customers no longer receive a utility rebate on residential installs.",
            "federal_25c_credit": "EXPIRED December 31, 2025 for air-source heat pumps. Geothermal still 30% through 2032.",
            "arizona_hear": "Active. Income-qualifying households up to $8,000 toward HVAC and electrification.",
            "arizona_homes": "Launching in Arizona later 2026. No income cap, performance-based, up to $4,000 per home.",
        },
        "refrigerant_transition_2026": {
            "new_standard": "R-454B (also sold as Puron Advance, Opteon XL41, Solstice 454B). Some manufacturers use R-32.",
            "old_standard": "R-410A — phased out for new residential installs as of January 1, 2026 per the EPA AIM Act.",
            "price_impact": "New R-454B systems cost approximately 5-10% more than equivalent 2025 R-410A models, due to added safety equipment (leak sensors, redesigned valves).",
            "existing_r410a_systems": "Still fine. R-410A refrigerant remains available for service, parts are still being manufactured, and the rule only affects new system installs.",
            "safety": "A2L classification = mildly flammable, but at concentrations that are exceedingly difficult to reach in a properly installed residential system. Equivalent to automotive A/C refrigerant safety class.",
        },
        "response_times": {
            "standard_service": "Same-day appointments are the norm",
            "emergencies": "Most emergency calls in Phoenix and the North Valley are on-site within 4 hours",
            "after_hours": "We answer the phone 24/7. After-hours emergency call-out: $149, waived with completed repair, $0 for Comfort Club members",
        },
        "warranty_policy": {
            "residential_repairs": "90-day parts warranty on the work performed",
            "residential_installs_ac_heating": {
                "manufacturer_parts": "10-year parts warranty provided by the equipment manufacturer; covers the equipment itself (compressor, motors, coil, etc.). Instant Heating and Air registers the warranty on the customer's behalf and assists with claims.",
                "labor": "2-year labor warranty from Instant Heating and Air; covers the labor required to replace any manufacturer-covered part during the 2-year period (e.g., condenser fan motor, blower motor, compressor swap).",
                "craftsmanship": "Lifetime craftsmanship warranty from Instant Heating and Air; covers the original installation workmanship (brazed connections, equipment mounting, line-set routing, condensate management) for the life of the installed unit. Separate from and in addition to the labor warranty.",
                "optional_extended_labor": "10-year extended labor warranty available as a paid add-on at the time of sale; pricing and terms quoted at sale.",
            },
            "commercial_installs": "1-year manufacturer parts AND labor warranty",
            "indoor_air_quality": "Manufacturer's parts warranty (varies by product) + 90-day labor",
        },
        "chatbot": {
            "quick_replies": QUICK_REPLIES,
            "intents": INTENTS,
            "fallback": FALLBACK,
            "match_threshold": 0.5,
            "greeting": INTENTS[0]['response'] if INTENTS else "Hi! How can I help?",
        },
        "llm_system_prompt": SYSTEM_PROMPT,
        "site_pages": {
            "home": "/",
            "services_hub": "/services/",
            "service_areas_hub": "/service-areas/",
            "blog": "/blog/",
            "about": "/about.html",
            "reviews": "/reviews.html",
            "contact": "/contact.html",
            "financing": "/financing.html",
            "comfort_club": "/maintenance-plan.html",
            "instant_quote_tool": SITE['quote_tool_url'],
        },
    }

    # Write a pretty-printed copy at a stable public URL.
    out_dir = OUT / "assets" / "data"
    out_dir.mkdir(parents=True, exist_ok=True)
    json_path = out_dir / "iha-knowledge.json"
    json_path.write_text(json.dumps(knowledge, indent=2, ensure_ascii=False))
    print(f"  wrote assets/data/iha-knowledge.json ({json_path.stat().st_size} bytes)")


def build_redirects():
    """Generate two layers of redirects from legacy URLs to current pages:

    1. A `_redirects` file at the site root (Netlify / Cloudflare Pages /
       Sevalla-friendly format). Hosts that support it serve a true 301 —
       optimal for SEO and the cleanest user experience.

    2. A small HTML stub at every legacy path with:
         - `<link rel="canonical">` pointing to the new URL
         - `<meta http-equiv="refresh" content="0; ...">` for instant redirect
         - `<meta name="robots" content="noindex">` so the stub itself doesn't
           pollute search results
         - A JS redirect as triple-belt fallback
         - A clickable link in the body for users on browsers that ignore all
           of the above

    The stub layer ensures redirects work on any static host even if the
    `_redirects` file isn't picked up.
    """
    if not REDIRECTS:
        return

    base = SITE['base_url']

    # ---- Layer 1: _redirects file -----------------------------------------
    redirects_txt = "# Auto-generated by build_redirects() in build/build.py\n"
    redirects_txt += "# Legacy URLs from the previous Wix site → current pages.\n"
    redirects_txt += "# Format: <from> <to> <status>\n\n"
    for old_path, new_path in REDIRECTS.items():
        redirects_txt += f"{old_path:<70} {new_path:<55} 301\n"
    write("_redirects", redirects_txt)

    # ---- Layer 2: per-URL meta-refresh HTML stubs -------------------------
    for old_path, new_path in REDIRECTS.items():
        target = f"{base}{new_path}"
        # Strip the leading slash, then place the file at <path>/index.html
        # so the URL resolves cleanly (Sevalla serves index.html for folders).
        relpath = old_path.strip("/")
        # Edge case: if old_path is "/", we don't want to overwrite the
        # real index.html — skip it.
        if not relpath:
            continue
        out_file = f"{relpath}/index.html"
        stub = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Page moved — Instant Heating and Air</title>
<link rel="canonical" href="{target}">
<meta name="robots" content="noindex,follow">
<meta http-equiv="refresh" content="0; url={target}">
<meta name="description" content="This page has moved. Redirecting to {target}.">
<script>window.location.replace({json.dumps(target)});</script>
<style>body{{font-family:system-ui,sans-serif;max-width:560px;margin:80px auto;padding:0 20px;color:#143C5E;line-height:1.55}}</style>
</head>
<body>
<h1>This page has moved.</h1>
<p>You should be redirected automatically. If not,
<a href="{target}">click here to continue to {target}</a>.</p>
</body>
</html>
"""
        write(out_file, stub)


def build_google_verification_files():
    """Emit one or more Google Search Console verification files at the site
    root. The filename is provided by Google when you choose the HTML-file
    verification method. The file content is the standard one-liner GSC
    expects: 'google-site-verification: <filename>'.
    """
    for filename in SITE.get("google_verification_files", []):
        # Defensive: only emit files that look like Google verification names
        # (prevents writing arbitrary HTML if someone fat-fingers the list).
        if not (filename.startswith("google") and filename.endswith(".html")):
            print(f"  skipped suspicious verification name: {filename}")
            continue
        write(filename, f"google-site-verification: {filename}\n")

def build_manifest():
    mf = {
        "name": SITE['name'],
        "short_name": "Instant HVAC",
        "description": SITE['tagline'],
        "start_url": f"{BASE_PATH}/" if BASE_PATH else "/",
        "display": "standalone",
        "background_color": "#ffffff",
        "theme_color": "#143C5E",
        "icons": [
            {"src": f"{BASE_PATH}/assets/img/android-192.png", "sizes": "192x192", "type": "image/png"},
            {"src": f"{BASE_PATH}/assets/img/android-512.png", "sizes": "512x512", "type": "image/png"},
        ]
    }
    write("site.webmanifest", json.dumps(mf, indent=2))


def apply_base_path():
    """Post-process: prefix all internal href/src/action paths with BASE_PATH.

    Matches internal paths (starting with `/`) in href=, src=, and action= attributes.
    Skips protocol-relative URLs (`//...`), anchors (`#...`), mailto:, tel:, and full URLs.
    Only runs when BASE_PATH is set.
    """
    if not BASE_PATH:
        return

    # Allow: /something, /a/b/c, and bare /
    # Exclude: //cdn.example, /#anchor (not applicable — hrefs to /# are weird)
    path_attr = re.compile(r'\b(href|src|action)="(/(?![/])[^"#]*)"')
    updated = 0
    for html_file in OUT.rglob("*.html"):
        content = html_file.read_text(encoding="utf-8")
        new_content = path_attr.sub(
            lambda m: f'{m.group(1)}="{BASE_PATH}{m.group(2)}"',
            content,
        )
        if new_content != content:
            html_file.write_text(new_content, encoding="utf-8")
            updated += 1
    print(f"  applied BASE_PATH={BASE_PATH} to {updated} HTML files")

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    print(f"Building site into {OUT}")

    build_home()
    build_service_hub()
    for s in SERVICES:
        build_service_page(s)
    build_area_hub()
    for a in AREAS:
        build_area_page(a)
    build_about()
    build_reviews()
    build_maintenance_plan()
    build_financing()
    build_contact()
    build_book()
    build_blog_index()
    for p in POSTS:
        build_post(p)

    # Legal
    build_legal("privacy.html", "Privacy Policy",
        f"Last updated April 2026. Instant Heating and Air, LLC respects your privacy. This policy explains what we collect, why, and how we use it.",
        [
            ("What we collect", "When you contact us (by form, phone, or booking), we collect your name, address, phone, email, and the details of your service request. We also collect basic analytics data (pages visited, device type, approximate location) via Google Analytics."),
            ("How we use it", "Strictly to provide the service you requested, send appointment confirmations, and follow up after service. We do not sell, rent, or trade your information."),
            ("Who sees it", "Only our dispatch and technician team, plus trusted service providers (payment processing, calendar, email) under contract to handle data securely."),
            ("Your choices", "You can request deletion of your data at any time using our <a href=\"/contact.html\">contact form</a> or by calling (623) 352-9802."),
            ("Cookies", "We use essential cookies for site functionality and analytics cookies to understand aggregate usage. You can disable cookies in your browser settings."),
            ("Contact", "Questions? Use our <a href=\"/contact.html\">contact form</a> or call (623) 352-9802.")
        ])
    build_legal("terms.html", "Terms of Service",
        "Terms governing the use of our website and services. Last updated April 2026.",
        [
            ("Services", "All services provided by Instant Heating and Air, LLC are subject to a written agreement or work order signed at the time of service."),
            ("Warranty", "The Company provides the following warranties on labor and materials used in its services. All warranties begin on the date of original installation and are conditioned on payment in full and proof of original work. <strong>New System Installations:</strong> Equipment installed by the Company is covered by the equipment manufacturer's 10-year parts warranty, subject to the manufacturer's terms and conditions; the Company will register the manufacturer's warranty on the customer's behalf and assist with claims. The Company warrants the labor required to replace manufacturer-covered equipment — such as condenser fan motors, blower motors, and compressors — for 2 years from the date of installation; after the 2-year period the customer is responsible for labor costs even if the part remains under the manufacturer's warranty. The Company warrants the craftsmanship of the original installation — including brazed connections, equipment mounting, line-set routing, and condensate management — for the life of the installed unit. An extended 10-year labor warranty is available as a paid add-on with pricing and terms quoted at the time of sale. <strong>Repair Work and Replacement Parts:</strong> Replacement parts installed during a repair are warranted for 1 year from the date of installation unless covered by a separate manufacturer warranty. Labor tied to replacement parts installed during a repair is warranted for 6 months from the date of installation unless covered by a separate manufacturer warranty. <strong>Commercial Installations:</strong> 1-year manufacturer parts and labor warranty. <strong>Indoor Air Quality:</strong> Manufacturer's parts warranty varies by product, plus 90-day labor. <strong>Exclusions:</strong> All warranties exclude damage caused by misuse or neglect; modification or repair by anyone other than the Company; lack of recommended maintenance; acts of God; power surges; pre-existing conditions; or any work performed without the Company's prior written approval. Failure to pay invoices in full voids all warranties."),
            ("Limitation of Liability", "Our liability is limited to the amount paid for the specific service at issue. We are not responsible for consequential or incidental damages."),
            ("Payment", "Payment is due at the time of service unless financing has been arranged in advance. We accept credit card, check, ACH, and approved financing."),
            ("Governing Law", "These terms are governed by the laws of the State of Arizona.")
        ])
    build_legal("accessibility.html", "Accessibility Statement",
        "We are committed to making our website usable by everyone, including people with disabilities.",
        [
            ("Our commitment", "This site is built with accessibility in mind: semantic HTML, proper heading structure, color contrast meeting WCAG 2.1 AA, keyboard-navigable controls, and screen-reader-friendly labels."),
            ("Ongoing improvements", "We audit the site regularly and continue to address any accessibility issues as we find them."),
            ("Feedback", "If you encounter an accessibility issue, please use our <a href=\"/contact.html\">contact form</a> or call (623) 352-9802. We will respond within 2 business days.")
        ])

    build_thanks()
    build_404()
    build_sitemap()
    build_robots()
    build_manifest()
    build_google_verification_files()
    build_redirects()
    build_chatbot_knowledge()

    # If a BASE_PATH is set (e.g. "/instantheatingandair" for GitHub Pages project site),
    # prefix every internal path in the rendered HTML. This runs last so it catches
    # every page written by the builders above.
    apply_base_path()

    print("Done.")

if __name__ == "__main__":
    main()
