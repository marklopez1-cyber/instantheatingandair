"""Knowledge-base content for the Instant Heating and Air chatbot.

The build script (build.py) combines this file with the live SITE / SERVICES /
AREAS / google_reviews data to emit /assets/data/iha-knowledge.json — a single
portable JSON file that powers:

  - the on-site chatbot widget (site/assets/js/chatbot.js)
  - any future LLM-powered assistant (the JSON includes a SYSTEM_PROMPT)
  - third-party integrations (Dialogflow, Microsoft Bot Framework, custom GPTs)

To add or change a bot response, edit INTENTS below. The site rebuilds and
the JSON refreshes automatically — no JS changes required.
"""

# ---------------------------------------------------------------------------
# Quick-reply chips shown when the chat panel first opens. Each chip becomes
# a tappable button that submits its `query` to the bot.
# ---------------------------------------------------------------------------
QUICK_REPLIES = [
    {"label": "💸 Free estimate",          "query": "I'd like a free estimate"},
    {"label": "❄️ My AC isn't cooling",    "query": "My AC isn't cooling"},
    {"label": "🆕 What is R-454B?",         "query": "What is R-454B?"},
    {"label": "💰 SRP rebates",             "query": "Do you handle SRP Cool Cash rebates?"},
    {"label": "🛠️ Tune-up & maintenance",  "query": "How often should I tune up my AC?"},
    {"label": "📞 Talk to a person",        "query": "I want to talk to someone"},
]

# ---------------------------------------------------------------------------
# Intent library. Pattern matching is simple keyword-scoring (see chatbot.js):
# each pattern is a list of words/phrases that, when found together in the
# user's message, raise that intent's score. The highest score wins. If no
# intent beats the threshold, FALLBACK fires.
#
# `actions` is a list of one-tap CTA chips shown beneath the response. Each
# action has `label` (button text), `kind` ("call" | "link" | "modal" | "quick"),
# and a `target` (phone number, URL, modal id, or follow-up query).
# ---------------------------------------------------------------------------
INTENTS = [
    {
        "id": "greeting",
        "patterns": [["hi"], ["hello"], ["hey"], ["good morning"], ["good afternoon"],
                     ["good evening"], ["what's up"], ["howdy"], ["greetings"]],
        "response": "Hi there! 👋 I'm the Instant Heating and Air virtual assistant. I can help with pricing, scheduling, what's covered under warranty, our R-454B installs, SRP Cool Cash rebates, or anything else HVAC-related. What can I help you with?",
        "actions": [
            {"label": "💸 Free estimate", "kind": "quick", "target": "free estimate"},
            {"label": "📞 Call us", "kind": "call", "target": "+16233529802"},
        ],
    },
    {
        "id": "ac_not_cooling",
        "patterns": [
            ["ac", "not", "cooling"], ["ac", "not", "cool"], ["ac", "broken"],
            ["ac", "hot", "air"], ["blowing", "hot"], ["not", "cold"],
            ["ac", "wont", "work"], ["ac", "won't", "work"], ["ac", "down"],
            ["no", "cold", "air"], ["air conditioner", "broken"],
            ["ac", "stopped"], ["ac", "broke"], ["no", "ac"],
        ],
        "response": "Sorry — that's the worst, especially this time of year. Most AC \"no cool\" calls in Phoenix come down to one of a few things (low refrigerant, weak capacitor, dirty coil, frozen evaporator). We can usually diagnose it same-day. Our diagnostic visit is <strong>$84.50, waived the moment you approve the repair</strong>. Want to schedule, or call us right now?",
        "actions": [
            {"label": "📞 Call now (24/7)", "kind": "call", "target": "+16233529802"},
            {"label": "🛠️ Schedule service", "kind": "modal", "target": "estimate-modal"},
            {"label": "📖 AC troubleshooting tips", "kind": "link", "target": "/blog/ac-freezing-up-phoenix.html"},
        ],
    },
    {
        "id": "emergency",
        "patterns": [
            ["emergency"], ["urgent"], ["asap"], ["right now"], ["right away"],
            ["middle of", "night"], ["after hours"], ["24/7"], ["24 hour"],
            ["no ac", "now"], ["no heat", "now"], ["weekend"], ["holiday"],
        ],
        "response": "We answer the phone <strong>24/7</strong> for emergencies. Call <strong>(623) 352-9802</strong> any time and we'll dispatch the closest licensed tech — most Phoenix-area emergencies are on-site within 4 hours. After-hours emergency call-out is $149 (waived with completed repair, $0 for Comfort Club members).",
        "actions": [
            {"label": "📞 Call (623) 352-9802", "kind": "call", "target": "+16233529802"},
            {"label": "🛠️ Request service", "kind": "modal", "target": "estimate-modal"},
        ],
    },
    {
        "id": "new_ac_cost",
        "patterns": [
            ["new ac", "cost"], ["new ac", "price"], ["ac", "how much"],
            ["replace", "ac"], ["replacement", "ac"], ["new system", "cost"],
            ["price", "new"], ["how much", "system"], ["ac install", "cost"],
            ["new hvac", "cost"], ["new unit", "cost"], ["cost of new"],
            ["ac installation", "cost"], ["how much", "ac"], ["ac", "estimate"],
        ],
        "response": "A new R-454B AC installed in a Phoenix-area home in 2026 typically runs <strong>$8,400 – $17,000</strong>, with most 3-ton replacements landing between $10,000 and $12,500. Prices stepped up about 5–10% this year because of the new A2L refrigerant requirement. We give free in-home estimates with itemized pricing — no mystery numbers. SRP customers, we file the Cool Cash rebate paperwork at no extra charge (up to $1,125 back).",
        "actions": [
            {"label": "💸 Get free estimate", "kind": "modal", "target": "estimate-modal"},
            {"label": "🧮 Instant online estimate", "kind": "link", "target": "https://instant-hvac-quote.com"},
            {"label": "📖 Full pricing guide", "kind": "link", "target": "/blog/how-much-new-ac-unit-cost-phoenix-2026.html"},
        ],
    },
    {
        "id": "r454b_refrigerant",
        "patterns": [
            ["r-454b"], ["r454b"], ["a2l"], ["new refrigerant"], ["refrigerant", "2026"],
            ["puron advance"], ["r-32"], ["r32"], ["r-410a"], ["r410a"],
            ["refrigerant", "change"], ["refrigerant", "phase"],
        ],
        "response": "R-454B is the low-GWP refrigerant the EPA now requires on every new residential AC and heat pump installed starting 1/1/2026. It replaces R-410A (78% less global warming potential) and costs about 5–10% more because of redesigned safety equipment. <strong>Your existing R-410A system is fine</strong> — refrigerant and parts are still available for years; the rule only affects new installs. We exclusively install R-454B-compatible systems from Carrier, Trane, Lennox, Bosch and others.",
        "actions": [
            {"label": "📖 Full R-454B guide", "kind": "link", "target": "/blog/r-454b-refrigerant-phoenix-2026.html"},
            {"label": "💸 Get install estimate", "kind": "modal", "target": "estimate-modal"},
        ],
    },
    {
        "id": "srp_cool_cash",
        "patterns": [
            ["srp"], ["cool cash"], ["rebate"], ["rebates"], ["aps"],
            ["utility", "rebate"], ["incentive"], ["incentives"],
        ],
        "response": "<strong>SRP Cool Cash is still active in 2026</strong> and pays $75/ton for single-stage, $150/ton for two-stage, and $225/ton for variable-speed systems — up to <strong>$1,125 back on a 5-ton variable-speed install</strong>. We file the paperwork for you at no charge if you're an SRP customer. <strong>APS ended residential rebates on 1/1/2026</strong>. For income-qualifying households, Arizona's HEAR program offers up to $8,000.",
        "actions": [
            {"label": "💸 Get an estimate", "kind": "modal", "target": "estimate-modal"},
            {"label": "📞 Ask a tech", "kind": "call", "target": "+16233529802"},
        ],
    },
    {
        "id": "federal_tax_credit",
        "patterns": [
            ["tax credit"], ["federal", "credit"], ["25c"], ["ira"], ["inflation reduction"],
            ["heat pump", "tax"], ["federal", "rebate"],
        ],
        "response": "Quick honest update: the federal 25C tax credit for air-source heat pumps <strong>expired December 31, 2025</strong>. Air-source heat pumps installed in 2026 don't qualify for the 30%/$2,000 credit anymore. Geothermal heat pumps still get a 30% federal credit through 2032. State-administered IRA programs are filling the gap — Arizona's HEAR (income-qualifying, up to $8,000) and the upcoming HOMES program.",
        "actions": [
            {"label": "💰 SRP rebates", "kind": "quick", "target": "Do you handle SRP Cool Cash rebates?"},
            {"label": "📖 Heat pump guide", "kind": "link", "target": "/blog/heat-pump-vs-ac-furnace-phoenix.html"},
        ],
    },
    {
        "id": "maintenance",
        "patterns": [
            ["tune up"], ["tune-up"], ["tuneup"], ["maintenance"],
            ["how often", "service"], ["service my ac"], ["preventive"],
            ["19 point"], ["how often", "tune"],
        ],
        "response": "Twice a year in Phoenix — once in spring before cooling season, once in fall before heat kicks on. A single 19-point tune-up is <strong>$99</strong>. Better deal for most homeowners: our <strong>Comfort Club at $18/month</strong> covers both annual tune-ups plus 15% off any repairs, priority dispatch, and no overtime fees. Pays for itself the first time we catch something.",
        "actions": [
            {"label": "📅 Schedule tune-up", "kind": "modal", "target": "estimate-modal"},
            {"label": "🏆 Join Comfort Club", "kind": "link", "target": "/maintenance-plan.html"},
        ],
    },
    {
        "id": "comfort_club",
        "patterns": [
            ["comfort club"], ["membership"], ["maintenance plan"], ["service plan"],
            ["monthly plan"], ["subscription"], ["join"],
        ],
        "response": "The Comfort Club is <strong>$18/month per system</strong> and includes: 2 precision tune-ups per year, 15% off all repairs, priority dispatch when you need us, no after-hours or overtime fees, an extended warranty credit, and a no-breakdown guarantee between tune-ups. Cancel any time.",
        "actions": [
            {"label": "🏆 Join now", "kind": "link", "target": "/maintenance-plan.html"},
            {"label": "📞 Questions? Call us", "kind": "call", "target": "+16233529802"},
        ],
    },
    {
        "id": "free_estimate",
        "patterns": [
            ["free estimate"], ["free quote"], ["estimate"], ["quote"],
            ["consultation"], ["evaluation"], ["bid"],
        ],
        "response": "Free in-home estimates on full system replacements (new AC, furnace, heat pump, or IAQ system). For repair calls there's an $84.50 diagnostic fee that covers the trip + a full inspection + a written flat-rate repair quote — and it's waived the second you approve the repair. Want me to set up the visit?",
        "actions": [
            {"label": "💸 Request free estimate", "kind": "modal", "target": "estimate-modal"},
            {"label": "🧮 Instant online estimate", "kind": "link", "target": "https://instant-hvac-quote.com"},
            {"label": "📞 Call to schedule", "kind": "call", "target": "+16233529802"},
        ],
    },
    {
        "id": "diagnostic_fee",
        "patterns": [
            ["diagnostic"], ["service call"], ["call out", "fee"], ["trip charge"],
            ["how much", "come out"], ["how much", "visit"], ["84.50"], ["84"],
        ],
        "response": "Our diagnostic fee is <strong>$84.50</strong> for residential service calls. That covers the trip, a full system inspection, and a written flat-rate repair quote. It's <strong>waived the moment you approve the repair</strong>, so most repair customers pay nothing extra. Comfort Club members pay $0 for diagnostics. After-hours emergencies are $149 (also waived on completed repair).",
        "actions": [
            {"label": "🛠️ Schedule service", "kind": "modal", "target": "estimate-modal"},
            {"label": "📞 Call (623) 352-9802", "kind": "call", "target": "+16233529802"},
        ],
    },
    {
        "id": "financing",
        "patterns": [
            ["financing"], ["finance"], ["payment plan"], ["monthly payment"],
            ["installment"], ["afford"], ["zero down"], ["0% apr"], ["loan"],
        ],
        "response": "Yes — flexible monthly payments through our financing partners, including <strong>0% APR for qualified buyers</strong> plus 12-, 24-, 36-, and 60-month terms. For a typical $10,500 install that's roughly $115–$175/month. Apply in minutes online.",
        "actions": [
            {"label": "💳 Financing options", "kind": "link", "target": "/financing.html"},
            {"label": "💸 Get an estimate first", "kind": "modal", "target": "estimate-modal"},
        ],
    },
    {
        "id": "service_areas",
        "patterns": [
            ["service area"], ["do you serve"], ["do you cover"], ["service my"],
            ["anthem"], ["phoenix"], ["glendale"], ["cave creek"], ["peoria"],
            ["surprise"], ["scottsdale"], ["new river"], ["desert hills"], ["carefree"],
            ["where", "service"], ["my area"], ["my zip"], ["zip code"],
        ],
        "response": "We serve the entire greater Phoenix metro — Phoenix, Anthem, New River, Cave Creek, Desert Hills, North Scottsdale, Carefree, Glendale, Peoria, and Surprise. Our trucks stage in the North Valley, so North Valley ZIPs (85086, 85087, 85083, 85262) usually see us fastest.",
        "actions": [
            {"label": "🗺️ See service area map", "kind": "link", "target": "/services/"},
            {"label": "📞 Call to confirm coverage", "kind": "call", "target": "+16233529802"},
        ],
    },
    {
        "id": "hours_contact",
        "patterns": [
            ["hours"], ["open"], ["closed"], ["when", "open"],
            ["phone number"], ["call you"], ["contact"], ["address"],
            ["location"], ["where", "you"], ["office"],
        ],
        "response": "We answer the phone <strong>24/7</strong> for emergencies. Office address: 34975 N. Valley Parkway, Suite 152, Phoenix, AZ 85086. Main line: <strong>(623) 352-9802</strong>. Or use the contact form on our site — we respond within one business day.",
        "actions": [
            {"label": "📞 Call (623) 352-9802", "kind": "call", "target": "+16233529802"},
            {"label": "✉️ Send a message", "kind": "link", "target": "/contact.html"},
        ],
    },
    {
        "id": "brands",
        "patterns": [
            ["brand"], ["brands"], ["carrier"], ["trane"], ["lennox"], ["goodman"],
            ["rheem"], ["amana"], ["bryant"], ["york"], ["daikin"], ["mitsubishi"], ["bosch"],
            ["work on", "my"], ["what brand"],
        ],
        "response": "We service all major residential and light-commercial brands: Carrier, Trane, Lennox, Goodman, Rheem, Amana, Bryant, American Standard, York, Daikin, Mitsubishi, and Bosch. We'll also work on plenty of older units that other shops won't touch.",
        "actions": [
            {"label": "🛠️ Book a service", "kind": "modal", "target": "estimate-modal"},
        ],
    },
    {
        "id": "installation_includes_general",
        "patterns": [
            ["what", "included"], ["what's", "included"], ["whats included"],
            ["what", "come with"], ["what", "comes with"],
            ["what", "you install"], ["installation", "includes"], ["install", "includes"],
            ["new ac", "include"], ["new ac", "what"], ["full install"],
            ["scope of work"], ["what do i get"], ["what's in"], ["whats in"],
            ["new install", "include"], ["new system", "include"],
            ["install package"], ["package includes"], ["package include"],
        ],
        "response": "Great question — what's included depends on where your unit is installed. We have two install scopes:<br><br>• <strong>Package System</strong> — if your unit sits on the roof.<br>• <strong>Split System</strong> — if your unit is in the attic, garage, closet, or on a ground pad outside.<br><br>Which one fits your home? (If you're not sure, look outside: a single big box on the roof = package; an indoor unit + an outdoor condenser at ground level = split.)",
        "actions": [
            {"label": "🏠 Split system (ground/attic)", "kind": "quick", "target": "what's included with a split system install"},
            {"label": "🏢 Package system (roof unit)", "kind": "quick", "target": "what's included with a package system install"},
            {"label": "📞 Not sure — call us", "kind": "call", "target": "+16233529802"},
        ],
    },
    {
        "id": "split_system_includes",
        "patterns": [
            ["split system", "install"], ["split system", "include"], ["split system", "what"],
            ["split system", "come with"],
            ["split", "installation"], ["split", "package"],
            ["ground pad"], ["attic unit"], ["indoor unit", "outdoor"],
            ["not on the roof"], ["not on roof"], ["not a rooftop"],
            ["unit in", "attic"], ["unit in", "garage"], ["unit in", "closet"],
        ],
        "response": "Every Instant Heating and Air <strong>split-system installation</strong> (ground/attic-mounted unit) includes — no surprise add-ons after the quote:<br><br>✓ Licensed contractor installation<br>✓ 10-year manufacturer warranty<br>✓ 2-year labor warranty<br>✓ 2-year workmanship warranty<br>✓ Emergency drain overflow shutoff switch<br>✓ P-trap with cleanout<br>✓ B-vent for furnace installs<br>✓ Air-handler hang kit<br>✓ Drain pan<br>✓ Line-set flush<br>✓ Plenums<br>✓ Wi-Fi-capable thermostat<br>✓ Electrical whip / disconnect<br>✓ New condenser pad<br><br>Want a written quote for your home?",
        "actions": [
            {"label": "💸 Get free estimate", "kind": "modal", "target": "estimate-modal"},
            {"label": "🧮 Instant online quote", "kind": "link", "target": "https://instant-hvac-quote.com"},
            {"label": "📞 Talk to an installer", "kind": "call", "target": "+16233529802"},
        ],
    },
    {
        "id": "package_system_includes",
        "patterns": [
            ["package system"], ["package", "install"], ["package", "include"],
            ["package", "come with"], ["package unit"],
            ["roof unit"], ["rooftop unit"], ["rooftop", "install"], ["rooftop", "include"],
            ["on the roof"], ["unit on roof"], ["unit on the roof"],
            ["rtu"], ["rooftop ac"], ["roof ac"], ["roof top"],
        ],
        "response": "Every Instant Heating and Air <strong>package-system installation</strong> (rooftop unit) includes — no surprise add-ons after the quote:<br><br>✓ Licensed contractor installation<br>✓ 10-year manufacturer warranty<br>✓ 2-year labor warranty<br>✓ 2-year workmanship warranty<br>✓ Emergency drain overflow shutoff switch<br>✓ P-trap / PVC drain<br>✓ Sheetmetal curb or elbow and stand<br>✓ Crane (residential)<br>✓ Wi-Fi-capable thermostat<br>✓ Electrical whip / disconnect<br><br>Want a written quote for your home?",
        "actions": [
            {"label": "💸 Get free estimate", "kind": "modal", "target": "estimate-modal"},
            {"label": "🧮 Instant online quote", "kind": "link", "target": "https://instant-hvac-quote.com"},
            {"label": "📞 Talk to an installer", "kind": "call", "target": "+16233529802"},
        ],
    },
    {
        "id": "warranty",
        "patterns": [
            ["warranty"], ["warrantee"], ["guarantee"], ["covered"], ["labor warranty"],
            ["parts warranty"], ["10 year"], ["10-year"], ["90 day"], ["90-day"],
        ],
        "response": "Honest breakdown:<br><br>• <strong>Residential repairs / tune-ups / emergency service</strong> — 90-day parts warranty on the work performed.<br>• <strong>New residential installs (AC + heating)</strong> — 10-year manufacturer parts warranty + 2-year labor warranty + 2-year workmanship warranty, all included as standard. Want longer labor coverage? An extended 10-year labor warranty is available as a paid add-on.<br>• <strong>Commercial installs</strong> — 1-year manufacturer parts and labor warranty.<br><br>All warranties are in writing.",
        "actions": [
            {"label": "💸 Install estimate", "kind": "modal", "target": "estimate-modal"},
            {"label": "📞 Ask about labor coverage", "kind": "call", "target": "+16233529802"},
        ],
    },
    {
        "id": "heating",
        "patterns": [
            ["heat pump"], ["furnace"], ["heater"], ["heating"], ["no heat"],
            ["heater broken"], ["heat not working"], ["mini split"], ["dual fuel"],
        ],
        "response": "Yes — heating is half our business (the North Valley does get cold). We service and install all furnace + heat pump brands, including modern variable-speed inverter heat pumps that work great in Phoenix down to about 5°F. Heat pump vs. AC + gas furnace decision usually comes down to operating cost — we'll show you the 10-year math on every install estimate.",
        "actions": [
            {"label": "📖 Heat pump vs furnace", "kind": "link", "target": "/blog/heat-pump-vs-ac-furnace-phoenix.html"},
            {"label": "💸 Get heating estimate", "kind": "modal", "target": "estimate-modal"},
            {"label": "📞 Emergency? Call us", "kind": "call", "target": "+16233529802"},
        ],
    },
    {
        "id": "indoor_air_quality",
        "patterns": [
            ["air quality"], ["iaq"], ["dust"], ["allergies"], ["allergen"],
            ["air filter"], ["uv lamp"], ["air purifier"], ["duct cleaning"],
            ["merv"], ["pollen"], ["mold"],
        ],
        "response": "Phoenix air is harder on homes than most cities — desert dust, monsoon mold, and 6+ months of closed-up cooling. Our three-layer stack: (1) MERV 11 media filter cabinet, (2) UV-C germicidal lamp inside the air handler, (3) active purifier like iWave. Full stack typically runs $1,500–$2,200 installed.",
        "actions": [
            {"label": "📖 Phoenix IAQ guide", "kind": "link", "target": "/blog/indoor-air-quality-phoenix-dust-monsoon.html"},
            {"label": "💸 IAQ estimate", "kind": "modal", "target": "estimate-modal"},
        ],
    },
    {
        "id": "commercial",
        "patterns": [
            ["commercial"], ["business"], ["property manager"], ["restaurant"],
            ["retail"], ["office"], ["rtu"], ["rooftop unit"], ["pm contract"],
        ],
        "response": "Yes — we run a commercial PM program from $149/mo per rooftop unit, including 2 visits/year and priority response. We handle 3-ton through 25-ton packaged and split systems, work with property managers on whatever invoicing cadence you need, and have a dedicated night-and-weekend crew for restaurants and retail that can't take a daytime outage. Commercial installs carry a 1-year manufacturer parts and labor warranty.",
        "actions": [
            {"label": "💸 Request a walkthrough", "kind": "modal", "target": "estimate-modal"},
            {"label": "📞 Talk to commercial", "kind": "call", "target": "+16233529802"},
        ],
    },
    {
        "id": "reviews_social_proof",
        "patterns": [
            ["review"], ["reviews"], ["rating"], ["star"], ["google review"],
            ["testimonial"], ["yelp"], ["nextdoor"], ["bbb"], ["how good"],
        ],
        "response": "<strong>5.0 ★ across 56 Google reviews</strong> — all verified, displayed live on our homepage from the Google Places API so you can see the most recent ones any time. The most common compliment we get: honest pricing and no panic-selling.",
        "actions": [
            {"label": "⭐ Read all reviews", "kind": "link", "target": "/reviews.html"},
            {"label": "🗺️ Open Google profile", "kind": "link", "target": "https://maps.google.com/?cid=2213854254172440049"},
        ],
    },
    {
        "id": "about_company",
        "patterns": [
            ["who are you"], ["about you"], ["about the company"], ["family owned"],
            ["how long"], ["years in business"], ["licensed"], ["bonded"], ["insured"],
            ["roc"], ["owner"],
        ],
        "response": "We're <strong>Instant Heating and Air, LLC</strong> — family-owned and based in the North Phoenix Valley since 2019. Arizona ROC License #348556, fully bonded and insured, all technicians background-checked. Our techs live in the same North Valley ZIPs we serve, which is why we know what a 118° attic does to a condenser.",
        "actions": [
            {"label": "📄 About us", "kind": "link", "target": "/about.html"},
            {"label": "⭐ See our reviews", "kind": "link", "target": "/reviews.html"},
        ],
    },
    {
        "id": "talk_to_person",
        "patterns": [
            ["talk to", "person"], ["talk to", "someone"], ["talk to", "human"],
            ["speak to", "person"], ["speak to", "someone"], ["real person"],
            ["agent"], ["representative"], ["customer service"],
        ],
        "response": "Of course — we answer the phone live, no call center, no recordings. Call <strong>(623) 352-9802</strong> any time. Or if you'd rather we reach out to you, fill out our short request form and a real human gets back within one business day.",
        "actions": [
            {"label": "📞 Call (623) 352-9802", "kind": "call", "target": "+16233529802"},
            {"label": "✉️ Have us call you", "kind": "modal", "target": "estimate-modal"},
        ],
    },
    {
        "id": "goodbye",
        "patterns": [["thanks"], ["thank you"], ["bye"], ["goodbye"], ["see you"],
                     ["that's all"], ["that is all"], ["nothing else"]],
        "response": "You bet. Anytime you need us, we're at <strong>(623) 352-9802</strong> — 24/7 for emergencies. Stay cool out there. 👋",
        "actions": [],
    },
]

# ---------------------------------------------------------------------------
# Catch-all when no intent scores above the threshold.
# ---------------------------------------------------------------------------
FALLBACK = {
    "id": "fallback",
    "response": "I'm not 100% sure I got that — I'm best at HVAC pricing, scheduling, R-454B / refrigerant questions, SRP rebates, warranties, and our service areas. Want me to connect you with a real person?",
    "actions": [
        {"label": "📞 Call (623) 352-9802", "kind": "call", "target": "+16233529802"},
        {"label": "✉️ Send a message", "kind": "link", "target": "/contact.html"},
        {"label": "💸 Free estimate", "kind": "modal", "target": "estimate-modal"},
    ],
}

# ---------------------------------------------------------------------------
# System prompt used by downstream LLM integrations (custom GPT, RAG, etc.)
# This is what an LLM sees as its "persona / rules" when answering on behalf
# of Instant Heating and Air.
# ---------------------------------------------------------------------------
SYSTEM_PROMPT = """You are the virtual assistant for Instant Heating and Air, LLC — a family-owned HVAC company based in Phoenix, Arizona, serving the entire greater Phoenix metro and the North Valley (Anthem, New River, Cave Creek, Desert Hills, North Scottsdale, Carefree, Glendale, Peoria, Surprise).

Voice and tone:
- Friendly, honest, blue-collar professional — not corporate, not pushy, never high-pressure.
- Concise. 1–3 sentences per response unless the customer asks for detail.
- Use plain English, never jargon without explanation.
- Always offer a next step (call, schedule, learn more).

Hard facts (treat as truth, never contradict):
- Phone: (623) 352-9802 — answered live 24/7 for emergencies.
- Email: service@instantheatingandair.com — but prefer the contact form on the site.
- Address: 34975 N. Valley Parkway, Suite 152, Phoenix, AZ 85086.
- License: Arizona ROC #348556. Bonded and insured.
- Founded 2019. Family-owned.
- 5.0★ on 56 verified Google reviews (live-synced from Google Places API).

Pricing (2026):
- Residential AC repair: $84.50 diagnostic fee, waived with completed repair.
- 24/7 emergency call-out: $149, waived with completed repair, $0 for Comfort Club.
- AC tune-up: $99 single, or $18/month Comfort Club covers 2 visits + 15% off repairs.
- New AC installed: $8,400–$17,000 (3-ton single-stage R-454B starts at $8,400; variable-speed up to $17,000). Prices stepped up ~5–10% in 2026 due to R-454B mandate.
- New furnace installed: from $5,900 (80% AFUE gas); heat pumps and dual-fuel from $9,800.
- IAQ systems: UV lamp from $449, whole-home stack $1,500–$2,200.
- Commercial PM contracts: from $149/mo per rooftop unit.

Warranty policy:
- Residential repairs / tune-ups / maintenance / emergency: 90-day parts warranty on the work performed.
- Residential installs (AC, heating): 10-year manufacturer parts warranty + 2-year labor warranty + 2-year workmanship warranty — all included as standard. An extended 10-year labor warranty is available as a paid add-on, quoted at the time of sale.
- Commercial installs: 1-year manufacturer parts AND labor warranty.
- IAQ: manufacturer's parts warranty varies by product + 90-day labor.

2026 industry shifts to know:
- R-454B (also sold as Puron Advance, Opteon XL41, Solstice 454B) is mandatory on all new residential systems installed 1/1/2026 and later, replacing R-410A. About 78% lower GWP. New systems cost ~5–10% more due to added safety equipment.
- Existing R-410A systems are fine — R-410A refrigerant remains available for service for years.
- SRP Cool Cash rebate: still active. $75/ton single-stage, $150/ton two-stage, $225/ton variable-speed (up to $1,125 on 5-ton variable-speed). We file the paperwork.
- APS ended all residential rebates 1/1/2026.
- Federal 25C tax credit on air-source heat pumps EXPIRED 12/31/2025. Geothermal still gets 30% through 2032. Arizona HEAR (income-qualifying, $8K) and upcoming HOMES (no income cap, $4K) are the alternatives.

Response time honesty:
- Same-day service is the norm.
- Most emergency calls in Phoenix and the North Valley are on-site within 4 hours.
- Never promise a specific time-of-day commitment.

What to never do:
- Never quote a specific repair price without diagnosis. Always: "We'd diagnose, then give you a flat-rate quote before any work starts."
- Never push a new system on someone with a fixable old one. The honest pitch is: "Under 10 years old and under $1,500 repair, almost always repair."
- Never claim a lifetime workmanship warranty (we don't offer one — the standard install warranty is 10-yr parts + 2-yr labor + 2-yr workmanship, with an optional 10-yr labor add-on).
- Never claim a 2-hour emergency response (real promise is "most within 4 hours").
- Never share customer reviews verbatim that you haven't been given.
- If asked about something outside HVAC (politics, jokes, unrelated chitchat), redirect kindly back to HVAC or offer to connect them with a real person.

Always end with a clear next step: call (623) 352-9802, request a quote, or visit a specific page on the site."""
