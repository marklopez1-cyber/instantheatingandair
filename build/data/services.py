"""All 10 service pages. Each one produces a dedicated URL, schema block,
and inbound link from the homepage + footer + related-services cluster.

cta_type controls the language of the call-to-action and aside panel:
  - "free_estimate"  → for system replacement/install/large projects.
                       Button: "Get Free Estimate →"
                       Aside heading: "Free Estimate"
  - "service_call"   → for repairs, tune-ups, and emergency service.
                       Button: "Schedule Service →"
                       Aside heading: "Schedule a Visit"
                       (estimates are NOT free — $84.50 diagnostic fee applies,
                        waived when the customer approves the repair.)"""

SERVICES = [
    {
        "slug": "ac-repair",
        "title_short": "AC Repair",
        "title_long": "AC Repair in Phoenix, AZ",
        "icon": "snowflake",
        "bg_image": "/assets/img/services/ac-repair-tech.jpg",
        "bg_alt": "Instant Heating and Air technician repairing an AC unit on a Phoenix-area home",
        "meta_title": "AC Repair Phoenix, AZ | Same-Day | Instant Heating and Air",
        "meta_description": "Fast, honest AC repair in Phoenix and the North Valley. Same-day service, flat-rate pricing, 90-day parts warranty on every repair. Call (623) 352-9802 — open 24/7.",
        "keywords": ["ac repair phoenix", "air conditioning repair phoenix", "emergency ac repair phoenix az", "ac not cooling phoenix"],
        "short_desc": "Same-day diagnosis, honest fix, cold air fast. All makes, all models.",
        "hero_subhead": "Your AC quit. It's 112° outside. Here's what happens next.",
        "intro": (
            "Your AC quit. It's 112° outside. Here's what happens next: you call (623) 352-9802, we roll a truck the same day, "
            "a licensed technician diagnoses the problem, you see the price <em>before</em> we start, and we fix it with a 90-day written parts warranty. "
            "No surprise fees, no panic-selling you a new system you don't need. That's AC repair the way it should be — and exactly why "
            "homeowners across Phoenix, Anthem, and the North Valley keep our number on the fridge."
        ),
        "included": [
            "Full diagnostic by a licensed tech",
            "Flat-rate repair pricing — no hourly surprises",
            "Refrigerant check and top-off (R-410A / R-454B / legacy R-22 where legal)",
            "Capacitor, contactor, and breaker inspection",
            "Condensate line clearing",
            "Coil temperature-drop and static-pressure test",
            "90-day written parts warranty on repairs"
        ],
        "signs": [
            "Warm air coming from the vents",
            "Weak airflow or short cycling",
            "Unusual sounds — grinding, hissing, clicking",
            "Musty or burning smells when the system runs",
            "Water pooling near the indoor unit",
            "Ice on the copper line or evaporator coil",
            "A sudden jump on your APS or SRP bill"
        ],
        "process": [
            ("Diagnose", "Full system inspection. Thermostat, refrigerant, electrical, coil, compressor — all of it."),
            ("Explain", "We show you what's wrong in plain English. You approve a flat-rate price before we touch a thing."),
            ("Fix", "Licensed, insured techs with a truck full of common parts — most repairs are done in a single visit."),
            ("Guarantee", "90-day parts warranty on the repair, in writing. If a part we replaced fails within 90 days, we come back at no charge.")
        ],
        "pricing_label": "Diagnostic Fee",
        "pricing_value": "$84.50",
        "pricing_note": "Waived with any completed repair",
        "cta_type": "service_call",
        "warranty_label": "90-day parts warranty on every repair",
        "faqs": [
            ("How fast can you get here?", "Same-day in almost every case. Most emergency calls in Phoenix, Anthem, and the North Valley are on-site within 4 hours."),
            ("Do you work on all brands?", "Yes — Carrier, Trane, Lennox, Goodman, Rheem, Amana, Bryant, American Standard, York, Daikin, Mitsubishi, and plenty of older units other shops won't touch."),
            ("How do you charge?", "Flat-rate repair pricing approved before we start. No hourly surprises and no fine-print labor multipliers."),
            ("Is the diagnostic visit free?", "No — the diagnostic visit is $84.50. That covers the trip, a full system inspection, and a written, flat-rate repair quote. The $84.50 is waived the moment you approve the repair, so most customers pay nothing extra. Free estimates are reserved for full system replacements."),
            ("Will you try to sell me a new unit?", "Only if it's genuinely the smart call. Plenty of Arizona repairs are a capacitor or contactor — a $200 fix, not a $10,000 one.")
        ],
        "related": ["ac-maintenance", "ac-installation", "emergency-hvac"]
    },
    {
        "slug": "ac-installation",
        "title_short": "AC Installation",
        "title_long": "AC Installation & Replacement in Phoenix, AZ",
        "icon": "home",
        "bg_image": "/assets/img/services/ac-installation-job.jpg",
        "bg_alt": "Newly installed packaged HVAC unit on a tile-roof Phoenix home by Instant Heating and Air",
        "meta_title": "AC Installation Phoenix | New Unit & Replacement | Instant Heating and Air",
        "meta_description": "Phoenix R-454B AC installation done right — Manual-J load calc, SRP Cool Cash rebates handled, 10-yr parts + 2-yr labor + lifetime craftsmanship warranty, 0% financing. 5.0★ on 56 Google reviews.",
        "keywords": ["ac installation phoenix", "new ac unit phoenix", "air conditioner replacement phoenix", "ac install cost phoenix", "r-454b phoenix", "srp cool cash rebate", "a2l refrigerant phoenix"],
        "short_desc": "Right-sized systems, proper load calc, 10-yr parts + 2-yr labor + lifetime craftsmanship warranty standard.",
        "hero_subhead": "The new AC you'll forget about — because it just works.",
        "intro": (
            "A new AC is the single biggest appliance purchase most Arizona homeowners make. We treat it that way. Every Instant install "
            "starts with a Manual-J load calculation — no lazy 'same size as the old one' guesswork — because an oversized Phoenix AC is "
            "the #1 cause of humid homes, short cycling, and premature compressor failure. As of 2026 we exclusively install R-454B "
            "(A2L) systems per federal requirements, and we file the SRP Cool Cash rebate paperwork for SRP customers at no extra "
            "charge — that's up to $1,125 back on a variable-speed system. We right-size, install clean, and stand behind every install with three "
            "warranties: the equipment manufacturer's full 10-year parts warranty (we register it for you), a 2-year labor warranty covering the "
            "labor to replace any manufacturer-covered part (fan motors, blower motors, compressors), and a lifetime craftsmanship warranty on the "
            "original installation workmanship — brazing, mounting, line-set routing. Want longer labor coverage? An extended 10-year labor warranty "
            "is available as a paid add-on at the time of sale."
        ),
        "included": [
            "Manual-J load calculation sized to your home — not your neighbor's",
            "R-454B (A2L) refrigerant compliant with 2026 EPA AIM Act requirements",
            "Code-compliant refrigerant line, pad, and disconnect",
            "New Nest or Ecobee smart thermostat (your pick)",
            "Duct inspection and minor sealing at no charge",
            "SRP Cool Cash rebate paperwork filed for you (SRP customers, up to $1,125 back)",
            "Haul-away of the old unit",
            "Full commissioning with superheat/subcooling log",
            "10-year manufacturer parts warranty + 2-year labor warranty (covers labor to replace manufacturer-covered parts) + lifetime craftsmanship warranty (covers original install workmanship) — all included · optional 10-year extended labor warranty available as a paid add-on"
        ],
        "signs": [
            "Your AC is 12+ years old",
            "Recent repair bills are adding up",
            "Uneven temperatures between rooms",
            "Unit uses R-22 refrigerant (being phased out)",
            "APS / SRP bills keep climbing",
            "Excessive dust or humidity you can't shake",
            "The outdoor unit is visibly rusted or corroded"
        ],
        "process": [
            ("Assess", "In-home load calculation, ductwork check, and system sizing. Takes about 45 minutes."),
            ("Design", "Three options — good, better, best — with line-item pricing. Financing approvals the same day."),
            ("Install", "Clean, quiet install crew. Drop cloths down, shoe covers on, old unit hauled away."),
            ("Commission", "Full system startup, refrigerant charge logged, thermostat programmed, walk-through before we leave.")
        ],
        "pricing_label": "Installed From",
        "pricing_value": "$8,400",
        "pricing_note": "3-ton 14.3 SEER2 R-454B — financing from $115/mo OAC · Free in-home estimate · SRP Cool Cash filed for you",
        "cta_type": "free_estimate",
        "warranty_label": "10-yr mfr parts + 2-yr labor + lifetime craftsmanship · 10-yr labor add-on available",
        "faqs": [
            ("What does a new AC cost in Phoenix in 2026?", "Installed pricing ranges from $8,400 for a basic 3-ton single-stage R-454B system up to $17,000 for a high-efficiency variable-speed system. Most North Valley homes land in the $10,000–$12,500 range. Prices ticked up roughly 5–10% in 2026 because of the new A2L refrigerant requirement."),
            ("What is R-454B and why does my new AC use it?", "R-454B is the low-global-warming-potential refrigerant the EPA's AIM Act required for all new residential systems installed January 1, 2026 or later. It replaces R-410A. The chemistry is different (78% lower GWP), the safety equipment is more extensive, and the install cost runs 5–10% higher — but performance, efficiency, and reliability are functionally the same. Your existing R-410A system is fine; the change only affects new installs."),
            ("Do you handle SRP Cool Cash rebates?", "Yes — every install we do for SRP customers includes the Cool Cash rebate paperwork at no charge. SRP's 2026 program pays $75 per ton for single-stage, $150/ton for two-stage, and $225/ton for variable-speed inverter systems — up to $1,125 back on a 5-ton variable-speed install. APS ended residential rebates on January 1, 2026, so APS-territory customers no longer receive a utility rebate."),
            ("What about federal tax credits?", "The federal 25C tax credit for air-source heat pumps expired December 31, 2025, so air-source heat pumps installed in 2026 do not qualify. Geothermal heat pumps still get a 30% federal credit through 2032. State-administered IRA programs are still active in Arizona — HEAR for income-qualifying households (up to $8,000) and the upcoming HOMES program (no income cap, up to $4,000)."),
            ("What SEER rating should I buy in Arizona?", "SEER2 15.2 is the 2023+ federal minimum for the Southwest. For most Phoenix homes, 16–18 SEER2 is the efficiency sweet spot — higher ratings only pay back in large, heavily-cooled homes."),
            ("How long does the install take?", "Most residential replacements are done in a single day. Full-system changeouts with new line-set and duct work can run into a second day."),
            ("Do you offer financing?", "Yes — 0% APR for qualified buyers plus 12-, 24-, 36-, and 60-month terms through our financing partners."),
            ("Is there a warranty?", "Yes — every new install includes three warranties as standard: <strong>(1) the equipment manufacturer's 10-year parts warranty</strong> (we register it for you), <strong>(2) a 2-year labor warranty</strong> covering the labor to replace any manufacturer-covered part (condenser fan motor, blower motor, compressor, etc.), and <strong>(3) a lifetime craftsmanship warranty</strong> covering the original installation workmanship — brazed connections, equipment mounting, line-set routing — for the life of the unit. If you want longer labor coverage, an extended 10-year labor warranty is available as a paid add-on at the time of sale. All warranties are in writing.")
        ],
        "related": ["ac-repair", "ac-maintenance", "heating-installation"]
    },
    {
        "slug": "ac-maintenance",
        "title_short": "AC Tune-Ups",
        "title_long": "AC Maintenance & Tune-Ups in Phoenix, AZ",
        "icon": "wrench",
        "bg_image": "/assets/img/services/ac-maintenance-tuneup.jpg",
        "bg_alt": "Instant Heating and Air technician performing a precision tune-up with a digital diagnostic meter",
        "meta_title": "AC Tune-Up Phoenix | 19-Point Maintenance | Instant Heating and Air",
        "meta_description": "Precision AC maintenance in Phoenix & Anthem. 19-point tune-up, Comfort Club plans from $18/mo. Catch small issues before summer turns them into big ones.",
        "keywords": ["ac tune up phoenix", "ac maintenance phoenix", "hvac tune up arizona", "ac service phoenix"],
        "short_desc": "19-point precision tune-up to catch problems before Phoenix summer does.",
        "hero_subhead": "The single cheapest way to avoid a $9,000 surprise in July.",
        "intro": (
            "Phoenix doesn't ask your AC to work — it demands it, for 6 straight months, at 40% higher duty cycle than any other US metro. "
            "Skipping maintenance here isn't 'rolling the dice' — it's betting against the house. Our 19-point tune-up catches the small stuff "
            "(a weak capacitor, a leaking Schrader valve, a filthy coil stealing 25% of your capacity) before it becomes a 2am compressor failure "
            "at 112 degrees."
        ),
        "included": [
            "Refrigerant pressure and superheat/subcooling check",
            "Capacitor and contactor microfarad test",
            "Condenser coil wash-down",
            "Evaporator coil inspection",
            "Blower amp-draw reading",
            "Thermostat calibration",
            "Condensate line flush",
            "Electrical terminal tightening",
            "Delta-T temperature-drop test",
            "Written report card with photos"
        ],
        "signs": [
            "It's been over a year since your last tune-up",
            "Unit short-cycles on hot afternoons",
            "Longer run times to hit your setpoint",
            "Rising utility bills with no usage change",
            "Mild musty smell when the AC kicks on",
            "A 'sizzle' or 'buzz' at the outdoor unit"
        ],
        "process": [
            ("Inspect", "19-point mechanical, electrical, and refrigerant inspection."),
            ("Clean", "Coil wash, line flush, filter swap — the things that silently steal capacity."),
            ("Test", "Delta-T, superheat, and amp-draw readings logged and kept on file."),
            ("Report", "Photo report card emailed to you — no high-pressure upsells, just facts.")
        ],
        "pricing_label": "Single Tune-Up",
        "pricing_value": "$99",
        "pricing_note": "Or $18/mo Comfort Club includes 2 visits + 15% off repairs",
        "cta_type": "service_call",
        "warranty_label": "90-day parts warranty on any repairs made",
        "faqs": [
            ("How often should I tune up my AC?", "Twice a year in Phoenix — once before cooling season, once before heating season. Our Comfort Club covers both."),
            ("Does maintenance really save money?", "Typically 10–30% on utility bills plus the catastrophic-failure avoidance. A $20 capacitor caught in April is a $2,000 compressor avoided in August."),
            ("Is the Comfort Club worth it?", "For almost every homeowner, yes. Two tune-ups at retail are $198 — the club is $216/year and includes 15% repair discounts, priority dispatch, and no overtime fees."),
            ("What if I have a second unit?", "Each system is its own membership at $18/mo. So two systems is $36/mo, three is $54/mo, and so on — flat rate, all the same benefits per system.")
        ],
        "related": ["ac-repair", "indoor-air-quality", "ac-installation"]
    },
    {
        "slug": "heating-repair",
        "title_short": "Heating Repair",
        "title_long": "Heating & Furnace Repair in Phoenix, AZ",
        "icon": "flame",
        "bg_image": "/assets/img/services/heating-repair-furnace.jpg",
        "bg_alt": "Open furnace cabinet with burners glowing blue during a heating repair by Instant Heating and Air",
        "meta_title": "Furnace & Heating Repair Phoenix | Instant Heating and Air",
        "meta_description": "Fast furnace and heat pump repair across Phoenix and the North Valley. Gas, electric, heat pump — all makes serviced same-day. (623) 352-9802.",
        "keywords": ["heating repair phoenix", "furnace repair phoenix", "heat pump repair phoenix", "no heat phoenix"],
        "short_desc": "Furnaces and heat pumps fixed right — the North Valley gets cold.",
        "hero_subhead": "Anthem nights drop below 30°. Your heat shouldn't drop at all.",
        "intro": (
            "Phoenix 'mild' winters are a myth the second you head north of Loop 303. Anthem, Cave Creek, and New River regularly see 28–35° overnight, "
            "and that's exactly when your furnace or heat pump decides to quit. We're stocked for it — gas furnaces, electric strip heat, and every "
            "flavor of heat pump on the market. Same-day diagnosis, flat-rate pricing, fixed the first time."
        ),
        "included": [
            "Furnace ignition, flame sensor, and gas valve diagnostics",
            "Heat pump reversing-valve and defrost-cycle test",
            "Heat exchanger inspection and CO safety check",
            "Electric strip heater element continuity test",
            "Thermostat wiring and control-board verification",
            "Blower motor and inducer amp-draw check",
            "90-day written parts warranty on repairs"
        ],
        "signs": [
            "Furnace lights and then shuts off (short cycling)",
            "Cold air blowing from vents in heat mode",
            "Burning or gas smell on startup",
            "Heat pump outdoor unit iced over",
            "Thermostat reads below setpoint for hours",
            "Loud banging or clicking on ignition"
        ],
        "process": [
            ("Diagnose", "Full heat-side inspection — gas, electrical, and refrigerant as applicable."),
            ("Explain", "Plain-English findings and a flat-rate repair number approved before we start."),
            ("Fix", "Common parts (ignitors, flame sensors, capacitors, boards) stocked on the truck."),
            ("Guarantee", "90-day written parts warranty on every heating repair.")
        ],
        "pricing_label": "Diagnostic Fee",
        "pricing_value": "$84.50",
        "pricing_note": "Waived with any completed repair",
        "cta_type": "service_call",
        "warranty_label": "90-day parts warranty on every repair",
        "faqs": [
            ("What brands of furnaces do you service?", "All major brands — Carrier, Trane, Lennox, Goodman, Rheem, American Standard, York, Amana, Bryant, and many more."),
            ("Do heat pumps really work in the desert?", "Modern variable-speed heat pumps work beautifully in the Phoenix metro — most are your most efficient heat source down to about 30°F, with electric strip heat as backup."),
            ("Is a gas smell dangerous?", "Treat any gas smell as an emergency — turn off the gas, leave the house, and call us or 911. We respond 24/7."),
            ("How long should a furnace last in Phoenix?", "Because they run so few hours per year here, gas furnaces routinely make it 20–25 years. If yours is older, it's living on borrowed time.")
        ],
        "related": ["heating-installation", "heating-maintenance", "emergency-hvac"]
    },
    {
        "slug": "heating-installation",
        "title_short": "Heating Installation",
        "title_long": "Heating Installation in Phoenix, AZ",
        "icon": "flame",
        "bg_image": "/assets/img/services/heating-installation-crane.jpg",
        "bg_alt": "Crane lifting a new HVAC unit onto a Phoenix tile-roof home for an Instant Heating and Air install",
        "meta_title": "Furnace & Heat Pump Installation Phoenix | Instant Heating and Air",
        "meta_description": "New furnace and heat pump installation in Phoenix and the North Valley. Right-sized, code-compliant, 10-yr manufacturer parts + 2-yr labor + lifetime craftsmanship warranty included.",
        "keywords": ["heating installation phoenix", "new furnace phoenix", "heat pump installation arizona", "furnace replacement phoenix"],
        "short_desc": "Gas furnace, heat pump, or dual-fuel — sized and installed right.",
        "hero_subhead": "The last heating system you'll think about for 20 years.",
        "intro": (
            "Arizona's mild heat load makes right-sizing even more important than it is for cooling — oversized furnaces short cycle, leaving cold "
            "spots and wasted gas. We spec new heating installs around your actual load, your ductwork, and your electric vs. gas rates. Most North "
            "Valley homes save noticeably on their utility bill with a high-efficiency heat pump, even when gas is already in the house."
        ),
        "included": [
            "Manual-J heat-load calculation",
            "Dual-fuel controls where applicable (heat pump + gas backup)",
            "New smart thermostat",
            "Code-compliant flue, gas-line, and condensate",
            "CO and combustion-air testing",
            "Haul-away of the old unit",
            "10-year manufacturer parts warranty + 2-year labor warranty (covers labor to replace manufacturer-covered parts) + lifetime craftsmanship warranty (covers original install workmanship) — all included · optional 10-year extended labor warranty available as a paid add-on"
        ],
        "signs": [
            "Furnace is 15+ years old",
            "Repair bills adding up fast",
            "Noisy blower or cracked heat exchanger",
            "Uneven heating between rooms",
            "Considering a dual-fuel or full-electric switch",
            "Planning a new AC and want a matched system"
        ],
        "process": [
            ("Assess", "Load calc, duct check, and rebate review in a single home visit."),
            ("Design", "Three options — good, better, best — with financing approvals the same day."),
            ("Install", "Clean single-day install. Code-compliant flue, gas, and condensate."),
            ("Commission", "Combustion analysis, CO check, thermostat programming, full walk-through.")
        ],
        "pricing_label": "Installed From",
        "pricing_value": "$5,900",
        "pricing_note": "80% AFUE gas furnace — heat pumps and dual-fuel from $9,800 · Free in-home estimate",
        "cta_type": "free_estimate",
        "warranty_label": "10-yr mfr parts + 2-yr labor + lifetime craftsmanship · 10-yr labor add-on available",
        "faqs": [
            ("Heat pump or furnace in Phoenix?", "For most homes, a heat pump wins on operating cost and moves less carbon. If you already have cheap gas and a newer AC, a matched gas furnace is still fine."),
            ("What's dual-fuel?", "A heat pump that does the heavy lifting down to ~30°F, handing off to a gas furnace below that. Best of both worlds for the North Valley."),
            ("Are there rebates?", "APS, SRP, and the federal Inflation Reduction Act all offer rebates and tax credits for qualifying heat pump installs. We handle the paperwork."),
            ("Will this affect my AC?", "If your AC is also aging, we'll show you the math on replacing the matched system — it's often much cheaper than doing them separately a year apart.")
        ],
        "related": ["heating-repair", "heating-maintenance", "ac-installation"]
    },
    {
        "slug": "heating-maintenance",
        "title_short": "Heating Maintenance",
        "title_long": "Heating Maintenance & Tune-Ups in Phoenix, AZ",
        "icon": "wrench",
        "bg_image": "/assets/img/services/heating-maintenance-co.jpg",
        "bg_alt": "Furnace burners glowing blue during a heating-maintenance safety inspection by Instant Heating and Air",
        "meta_title": "Furnace Tune-Up & Heating Maintenance Phoenix | Instant Heating and Air",
        "meta_description": "Pre-winter furnace tune-ups and heat pump maintenance across Phoenix and the North Valley. Safety-first, CO-tested, $99 or $18/mo Comfort Club.",
        "keywords": ["furnace tune up phoenix", "heating maintenance phoenix", "heat pump maintenance arizona"],
        "short_desc": "Fall precision tune-up to keep heat running safely all winter.",
        "hero_subhead": "Combustion appliances need a once-a-year look. This is that look.",
        "intro": (
            "A gas furnace or heat pump left alone for a decade eventually fails — often in the coldest week of the year, sometimes with a carbon "
            "monoxide leak you can't smell. Our fall tune-up is a safety inspection first and an efficiency service second. Clean burner, sealed "
            "flue, calibrated gas valve, CO-tested and signed off in writing."
        ),
        "included": [
            "Burner, flame sensor, and ignitor clean",
            "Heat exchanger visual and CO test",
            "Gas pressure and manifold adjustment",
            "Heat pump reversing valve and defrost test",
            "Blower amp-draw and motor inspection",
            "Thermostat calibration and battery swap",
            "Filter replacement",
            "Written report card"
        ],
        "signs": [
            "You haven't serviced the furnace in 12+ months",
            "No CO detector, or older than 7 years",
            "Short cycling on startup",
            "Higher-than-normal gas bills",
            "Slight 'gas' or 'hot plastic' smell",
            "Yellow (not blue) burner flame"
        ],
        "process": [
            ("Inspect", "Full safety and efficiency inspection including CO test."),
            ("Clean", "Burner, flame sensor, and blower — the three parts that hoard dust all summer."),
            ("Test", "Gas pressure, combustion air, and temperature rise logged."),
            ("Report", "Written report card with photos and an honest condition grade.")
        ],
        "pricing_label": "Single Tune-Up",
        "pricing_value": "$99",
        "pricing_note": "Or $18/mo Comfort Club includes AC + heat tune-ups",
        "cta_type": "service_call",
        "warranty_label": "90-day parts warranty on any repairs made",
        "faqs": [
            ("Do I really need this every year?", "For combustion appliances (gas furnaces), yes — it's a safety inspection as much as a tune-up. For heat pumps, every other year is acceptable."),
            ("Will you install a CO detector?", "Yes — we can add one during the tune-up at cost."),
            ("Is it covered by the Comfort Club?", "Yes. One AC and one heat tune-up per year are included in the $18/mo plan.")
        ],
        "related": ["heating-repair", "ac-maintenance", "indoor-air-quality"]
    },
    {
        "slug": "emergency-hvac",
        "title_short": "24/7 Emergency HVAC",
        "title_long": "24/7 Emergency HVAC in Phoenix, AZ",
        "icon": "clock",
        "bg_image": "/assets/img/services/emergency-hvac-rooftop.jpg",
        "bg_alt": "Instant Heating and Air technicians on a Phoenix rooftop at sunrise during a 24/7 emergency call",
        "meta_title": "24 Hour AC & Heating Repair Phoenix | Emergency HVAC | Instant Heating and Air",
        "meta_description": "24/7 emergency AC and heating repair across Phoenix, Anthem, and the North Valley. Same-day dispatch, most emergencies on-site within 4 hours. Call (623) 352-9802.",
        "keywords": ["24 hour ac repair phoenix", "emergency hvac phoenix", "after hours ac repair phoenix"],
        "short_desc": "Same-day dispatch — most emergencies on-site within 4 hours, day, night, or holiday.",
        "hero_subhead": "A 118° bedroom at 3am is not a wait-till-Monday problem.",
        "intro": (
            "We run a live 24/7 dispatch because Phoenix heat doesn't care about business hours. Elderly parents, newborns, pets, home offices — "
            "when the AC quits in July, it's a real emergency. Our on-call techs roll with a truck stocked for the 20 most common Phoenix-area "
            "failures: capacitors, contactors, run caps, fuses, boards, thermostats. Most calls are back online within 90 minutes of pickup."
        ),
        "included": [
            "Live (human) dispatch 24/7/365",
            "Most emergencies on-site within 4 hours in Phoenix and the North Valley",
            "Flat-rate emergency pricing — you see the number before work starts",
            "Fully stocked trucks for the most common Phoenix-area failures",
            "90-day parts warranty on every emergency repair",
            "Comfort Club members: no overtime or after-hours surcharges"
        ],
        "signs": [
            "Indoor temps over 85° with vulnerable occupants",
            "Visible refrigerant leak, gas smell, or smoke",
            "Breaker tripping repeatedly",
            "Standing water around indoor unit",
            "Total heat loss in temperatures below 45°"
        ],
        "process": [
            ("Call", "Phone is answered live by our dispatch — not a recording, not a call center."),
            ("Dispatch", "Closest available technician is routed. You get a tracking text with ETA."),
            ("Arrive", "Flat-rate emergency price quoted on-site before any work begins."),
            ("Fix", "Most calls resolved on the first visit with parts stocked on the truck.")
        ],
        "pricing_label": "Emergency Call-Out",
        "pricing_value": "$149",
        "pricing_note": "Diagnostic + dispatch — waived with repair · $0 for Comfort Club members",
        "cta_type": "service_call",
        "warranty_label": "90-day parts warranty on emergency repairs",
        "faqs": [
            ("What counts as an emergency?", "Any condition that creates a safety, health, or serious comfort risk. Use your judgment — if you're unsure, call and we'll help you decide."),
            ("How long until you get here?", "Most Phoenix metro emergencies are on-site within 4 hours. North Valley ZIPs (85086, 85087, 85083, 85262) are often faster because we're based here. We'll text you a real ETA the moment your call is dispatched — no vague \"sometime today\" runarounds."),
            ("Is after-hours more expensive?", "Yes for non-members — about 20% above standard rates. Comfort Club members pay no overtime, period."),
            ("Do you work on weekends and holidays?", "Yes. 24/7/365. Including Christmas Eve at 11:30pm — a real call we handled.")
        ],
        "related": ["ac-repair", "heating-repair"]
    },
    {
        "slug": "commercial-hvac",
        "title_short": "Commercial HVAC",
        "title_long": "Commercial HVAC Service in Phoenix, AZ",
        "icon": "building",
        "bg_image": "/assets/img/services/commercial-hvac-job.jpg",
        "bg_alt": "Instant Heating and Air branded service van at a Phoenix commercial property with a crane lifting a new rooftop unit overhead",
        "meta_title": "Commercial HVAC Phoenix | Rooftop, Split & VRF Service | Instant Heating and Air",
        "meta_description": "Commercial HVAC installation, repair, and planned maintenance across Phoenix. Retail, office, restaurant, and light industrial. (623) 352-9802.",
        "keywords": ["commercial hvac phoenix", "commercial ac repair phoenix", "rooftop unit phoenix", "commercial hvac maintenance"],
        "short_desc": "Retail, office, and restaurant rooftop units serviced on your schedule.",
        "hero_subhead": "Keep the doors open and the customers cool.",
        "intro": (
            "Commercial HVAC downtime is revenue downtime. We service small-to-mid-size commercial clients across the Phoenix metro — retail, "
            "offices, medical, and restaurants — with planned-maintenance contracts that prevent the 110° Saturday emergency and 24/7 coverage for "
            "when it happens anyway. Rooftop units, split systems, and VRF platforms all serviced."
        ),
        "included": [
            "Planned-maintenance contracts (PM agreements)",
            "Rooftop package unit (RTU) service and replacement",
            "Split and VRF system service",
            "Preventive filter and belt programs",
            "Refrigerant compliance and leak management",
            "Thermostat and BAS integration",
            "Night and weekend appointments to avoid customer impact"
        ],
        "signs": [
            "Tenant complaints increasing",
            "Aging RTUs with rising repair bills",
            "No current PM agreement in place",
            "Retail or restaurant open-door heat loss",
            "Refrigerant leaks requiring ongoing top-off"
        ],
        "process": [
            ("Survey", "Free property walk-through and unit inventory."),
            ("Propose", "Right-sized PM plan with photo-documented baseline."),
            ("Service", "Scheduled visits with digital reports to your facilities team."),
            ("Respond", "24/7 reactive calls with priority dispatch for PM customers.")
        ],
        "pricing_label": "PM Contracts From",
        "pricing_value": "$149/mo",
        "pricing_note": "Per rooftop unit — includes 2 visits/yr and priority response · Free site walk-through",
        "cta_type": "free_estimate",
        "warranty_label": "1-year manufacturer parts and labor",
        "faqs": [
            ("Do you bid replacement RTUs?", "Yes — 3-ton through 25-ton packaged and split systems. Typically 2-bid competitive pricing."),
            ("Do you work with property managers?", "Absolutely. We invoice and report on whatever cadence your management company requires."),
            ("Do you service refrigeration?", "We service refrigeration-style HVAC and walk-in split systems. Dedicated commercial refrigeration (freezers, display cases) is outside our scope — we'll refer you."),
            ("Can you do night work?", "Yes — we run a dedicated night-and-weekend crew for retail and restaurants that can't take a daytime outage.")
        ],
        "related": ["ac-installation", "ac-maintenance", "emergency-hvac"]
    },
    {
        "slug": "indoor-air-quality",
        "title_short": "Indoor Air Quality",
        "title_long": "Indoor Air Quality in Phoenix, AZ",
        "icon": "wind",
        "bg_image": "/assets/img/services/indoor-air-quality.jpg",
        "bg_alt": "Cleaning a dust-laden return-air vent grille — Indoor Air Quality service by Instant Heating and Air",
        "meta_title": "Indoor Air Quality Phoenix | Air Purifier, UV, Duct Cleaning | Instant Heating and Air",
        "meta_description": "Clean indoor air in Phoenix. Air purifiers, UV germicidal lamps, whole-home filtration, and duct cleaning. Allergy, monsoon, and dust season ready.",
        "keywords": ["indoor air quality phoenix", "air purifier phoenix", "duct cleaning phoenix", "uv light hvac phoenix"],
        "short_desc": "Air purifiers, UV germicidal lamps, whole-home filtration, and duct cleaning.",
        "hero_subhead": "Phoenix dust + monsoon + pollen — handled.",
        "intro": (
            "Three things make Arizona indoor air harder than most: dust that never quits, monsoon-season mold spores, and closed-up homes running "
            "AC 6+ months a year recirculating the same air. We install the three-tier stack — whole-home media filtration, UV germicidal lamps, "
            "and polarized-media purifiers — and perform NADCA-style duct cleanings for homes that have never had one. Allergies, asthma, and "
            "general haze typically improve within a week."
        ),
        "included": [
            "Whole-home media filtration (MERV 11–16)",
            "UV germicidal lamps for coil sterilization",
            "Polarized-media air purifiers (iWave, APCO)",
            "NADCA-style duct cleaning",
            "Dryer vent cleaning",
            "Fresh-air ventilation integration",
            "Humidity and CO₂ monitoring"
        ],
        "signs": [
            "Visible dust returning within days of cleaning",
            "Allergy or asthma symptoms inside the home",
            "Musty smell when the AC first kicks on",
            "Yellow or black film on vent covers",
            "Family members who smoke or pets shedding",
            "Home built before 2000 with original ductwork"
        ],
        "process": [
            ("Assess", "Visual duct inspection plus air-quality reading for dust and humidity."),
            ("Recommend", "Right-fit stack: filtration, UV, purifier, duct clean — only what will actually help."),
            ("Install", "Clean, quiet installs — most complete in a single half-day."),
            ("Validate", "Post-install air test so you can see the change.")
        ],
        "pricing_label": "IAQ Systems From",
        "pricing_value": "$449",
        "pricing_note": "UV lamp install — full whole-home systems from $1,200 · Free in-home estimate",
        "cta_type": "free_estimate",
        "warranty_label": "Manufacturer's parts warranty (varies by product) · 90-day labor",
        "faqs": [
            ("Does duct cleaning actually help?", "In older Phoenix homes with original flex duct or homes after a remodel, yes — very noticeably. In newer, clean homes, the ROI is marginal and we'll tell you so."),
            ("Are UV lamps safe?", "Yes — they live inside the ductwork and never expose occupants. They sterilize the coil and drastically reduce mold growth during monsoon season."),
            ("What MERV filter should I use?", "MERV 11 is the sweet spot for most residential systems. MERV 13+ can restrict airflow — we'll confirm your blower can handle it before recommending."),
            ("How often should ducts be cleaned?", "Every 3–5 years for most Phoenix homes. Post-remodel or post-rodent-infestation, immediately.")
        ],
        "related": ["ac-maintenance", "heating-maintenance", "ac-installation"]
    }
]

# Build a quick lookup for templates
SERVICES_BY_SLUG = {s["slug"]: s for s in SERVICES}
