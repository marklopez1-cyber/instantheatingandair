"""Site-wide constants — NAP, brand, social links, nav."""

SITE = {
    "name": "Instant Heating and Air",
    "legal_name": "Instant Heating and Air, LLC",
    "tagline": "Professionals You Can Trust",
    "mission": "Your comfort is our obsession.",
    "domain": "instantheatingandair.com",
    "base_url": "https://instantheatingandair.com",
    "phone_display": "(623) 352-9802",
    "phone_link": "+16233529802",
    "email": "service@instantheatingandair.com",
    "address": {
        "street": "34975 N. Valley Parkway, Suite 152",
        "city": "Phoenix",
        "region": "AZ",
        "postal": "85086",
        "country": "US",
        "lat": 33.8540,
        "lng": -112.1476
    },
    "license": "ROC #348556",
    "hours": "Mon–Sun · 24/7 Emergency",
    "service_radius_miles": 40,
    "founded_year": 2019,
    "booking_url": "https://book.housecallpro.com/book/Instant-Heating-and-Air/",
    "quote_tool_url": "https://instant-hvac-quote.com",
    # FormSubmit.co endpoint — submissions email service@instantheatingandair.com.
    # First submission triggers a one-click confirmation email to that address.
    # No account or API key needed.
    "form_endpoints": {
        "comfort_club": "https://formsubmit.co/service@instantheatingandair.com",
        "contact":      "https://formsubmit.co/service@instantheatingandair.com",
    },
    "success_redirect": "https://instantheatingandair.com/thanks.html",
    # Google Analytics 4 measurement ID — paste your G-XXXXXXXXXX here after
    # creating the GA4 property (see analytics.google.com → Admin → Data Streams).
    # Leave empty string to disable GA entirely.
    "ga4_id": "G-NCGVDZ7G74",
    # Service-area map shown on /services/. Replace with a Google My Maps embed
    # URL like https://www.google.com/maps/d/embed?mid=YOUR_MAP_ID once you've
    # created the custom map with pinned job locations.
    "service_area_map_url": "",
    # Google Business Profile rating + count. These are now AUTO-SYNCED at build
    # time from the Google Places API (see build/data/google_reviews.py and
    # google_reviews.json). build.py overrides these values from the live JSON
    # before rendering. The numbers below are only used as a fallback if the
    # JSON file is missing or unreadable.
    "avg_rating": "5.0",
    "total_reviews": 56,
    "social": {
        "facebook": "https://www.facebook.com/instantheatingandair/",
        "instagram": "https://www.instagram.com/instantheatingandair/",
        "google": "https://www.google.com/search?q=Instant+Heating+and+Air+Phoenix",
        "yelp": "https://www.yelp.com/biz/instant-heating-and-air-anthem",
        "nextdoor": "https://nextdoor.com/pages/instant-heating-and-air-anthem-az/"
    },
    "brands_serviced": [
        "Carrier", "Trane", "Lennox", "Goodman", "Rheem",
        "Amana", "Bryant", "American Standard", "York",
        "Daikin", "Mitsubishi", "Bosch"
    ]
}

# Main nav (top of every page)
NAV = [
    ("Services", "/services/"),
    ("Service Areas", "/service-areas/"),
    ("Comfort Club", "/maintenance-plan.html"),
    ("Financing", "/financing.html"),
    ("Reviews", "/reviews.html"),
    ("Blog", "/blog/"),
    ("About", "/about.html"),
]

# Footer column links
FOOTER_SERVICES = [
    ("AC Repair", "/services/ac-repair.html"),
    ("AC Installation", "/services/ac-installation.html"),
    ("AC Maintenance", "/services/ac-maintenance.html"),
    ("Heating Repair", "/services/heating-repair.html"),
    ("Heating Installation", "/services/heating-installation.html"),
    ("Indoor Air Quality", "/services/indoor-air-quality.html"),
    ("Commercial HVAC", "/services/commercial-hvac.html"),
    ("24/7 Emergency", "/services/emergency-hvac.html"),
]

FOOTER_AREAS = [
    ("Phoenix", "/service-areas/phoenix.html"),
    ("Anthem", "/service-areas/anthem.html"),
    ("New River", "/service-areas/new-river.html"),
    ("Cave Creek", "/service-areas/cave-creek.html"),
    ("Desert Hills", "/service-areas/desert-hills.html"),
    ("North Scottsdale", "/service-areas/north-scottsdale.html"),
    ("Carefree", "/service-areas/carefree.html"),
    ("Glendale", "/service-areas/glendale.html"),
    ("Peoria", "/service-areas/peoria.html"),
    ("Surprise", "/service-areas/surprise.html"),
]

# Homepage FAQ — mirrored into FAQPage JSON-LD
HOME_FAQ = [
    {
        "q": "How much does a new AC unit cost in Phoenix?",
        "a": "For a standard 3-ton single-stage R-454B system installed in a Phoenix-area home, expect $8,400–$12,500 depending on efficiency (SEER2), brand, and ductwork condition. High-efficiency variable-speed systems run $13,200–$17,000. Prices ticked up about 5–10% in 2026 because of the new A2L refrigerant requirement. We give itemized estimates — no mystery numbers."
    },
    {
        "q": "What is R-454B and will my old R-410A system still work?",
        "a": "R-454B is the new low-global-warming-potential refrigerant required by the EPA's AIM Act for all residential AC and heat pump systems installed January 1, 2026 or later. It replaces R-410A. Your existing R-410A system is fine — R-410A refrigerant remains available for service and parts will be supported for years. The mandate only affects new system installations. New R-454B systems cost roughly 5–10% more than equivalent 2025 R-410A models. We exclusively install R-454B-compatible equipment from Carrier, Trane, Lennox, Bosch, and others."
    },
    {
        "q": "Do you handle SRP Cool Cash and other Phoenix rebates?",
        "a": "Yes — every install we do for SRP customers includes the Cool Cash rebate paperwork at no charge. SRP's 2026 rebate pays $75 per ton for single-stage, $150/ton for two-stage, and $225/ton for variable-speed inverter systems — up to $1,125 back on a 5-ton variable-speed heat pump. APS ended residential rebates on January 1, 2026, so APS-territory customers no longer get a utility rebate. For income-qualifying households, Arizona's HEAR program offers up to $8,000 toward HVAC and electrification projects. We walk through the available options on every estimate."
    },
    {
        "q": "Do you offer free estimates?",
        "a": "Yes — free in-home estimates on full system replacements (new AC, furnace, heat pump, or IAQ system). For repair calls, we charge an $84.50 diagnostic fee that covers the trip, a full system inspection, and a written, flat-rate repair quote. The $84.50 is waived the moment you approve the repair, so most repair customers pay nothing extra. Comfort Club members pay $0 for diagnostics."
    },
    {
        "q": "How often should I tune up my AC in Arizona?",
        "a": "Twice a year in the Phoenix metro — once in the spring before cooling season, once in the fall before heating kicks on. Our $18/month Comfort Club includes both visits plus 15% off any repairs."
    },
    {
        "q": "Do you offer 24/7 emergency service?",
        "a": "Yes. 118° summer nights don't wait. Call (623) 352-9802 any time and we'll dispatch the closest licensed technician — typically within 2 hours in Phoenix, Anthem, and the North Valley."
    },
    {
        "q": "What HVAC brands do you service?",
        "a": "All major residential and light-commercial brands: Carrier, Trane, Lennox, Goodman, Rheem, Amana, Bryant, American Standard, York, Daikin, and Mitsubishi. We also service plenty of older units other shops won't touch."
    },
    {
        "q": "Do you offer financing for new installations?",
        "a": "Yes — flexible monthly payment plans through our financing partners, including 0% APR options for qualified buyers. Apply in minutes on our financing page."
    },
    {
        "q": "How quickly can you get to me in Anthem or New River?",
        "a": "Same-day appointments are the norm in Anthem, New River, Desert Hills, and Cave Creek. Emergency calls typically see a tech within 2 hours — we stage trucks in the North Valley precisely because these are our home ZIPs."
    },
    {
        "q": "Are you licensed, bonded, and insured?",
        "a": "Absolutely. Arizona ROC License #348556. Every technician is fully insured and background-checked. We carry this on the truck and every invoice because you should never wonder."
    },
    {
        "q": "What's included in the $18/month Comfort Club?",
        "a": "Two precision tune-ups per year (spring + fall), 15% off all repairs, priority dispatch when you need us, no after-hours or overtime fees, an extended warranty credit, and a no-breakdown guarantee between tune-ups. You can cancel any time."
    }
]

# "Why us" 3-up. Each card's `slug` drives a CSS class (.why-card-<slug>)
# that paints the matching photo from /assets/img/why/why-<slug>.jpg as a
# dark-overlaid background — so the text stays sharp white over a real
# Instant Heating and Air scene.
WHY_US = [
    {
        "icon": "chat",
        "slug": "straight-shooter",
        "title": "Straight-Shooter Pricing",
        "body": "You see the price before we start. No surprise fees, no panic-sells, no upsells you didn't ask for."
    },
    {
        "icon": "sun",
        "slug": "techs-local",
        "title": "Techs Who Live Here",
        "body": "We know what a 118° attic does to a condenser because we've been in one this week. Local homes, local solutions."
    },
    {
        "icon": "shield",
        "slug": "fixed-right",
        "title": "Fixed Right, Guaranteed",
        "body": "Every repair and every install is backed by a written warranty. If it's not right, we come back until it is."
    }
]
