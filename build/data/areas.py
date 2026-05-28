"""10 service-area pages with locally-relevant detail (no copy-paste city swaps)."""

AREAS = [
    {
        "slug": "phoenix",
        "name": "Phoenix",
        "zip_samples": ["85086", "85085", "85083", "85024", "85027"],
        "landmarks": "Deer Valley, Desert Ridge, Tramonto, Sonoran Preserve",
        "lat": 33.6054,
        "lng": -112.1318,
        "climate_note": (
            "Central and North Phoenix homes bear the worst of the summer heat — 115°+ day after day for weeks at a time. "
            "AC capacity and coil cleanliness matter more here than almost anywhere in the country."
        ),
        "response_claim": "Same-day service across Phoenix ZIPs 85086, 85085, 85083, 85024, and 85027. Most emergency calls on-site within 4 hours.",
        "local_detail": (
            "Phoenix is where Instant Heating and Air started — most of our technicians live in the North Phoenix corridor, "
            "which means we've been inside the same floor plans you're standing in. The big-name Phoenix HVAC shops have gotten "
            "bigger, busier, and more expensive. We're the local alternative — licensed, bonded, and still close enough that when "
            "we say same-day, we mean before dinner."
        )
    },
    {
        "slug": "anthem",
        "name": "Anthem",
        "zip_samples": ["85086", "85087"],
        "landmarks": "Anthem Country Club, Daisy Mountain, Outlets at Anthem, Pioneer Village",
        "lat": 33.8678,
        "lng": -112.1391,
        "climate_note": (
            "Anthem sits at roughly 2,100 ft elevation — noticeably cooler overnight than central Phoenix and regularly in the low 30s "
            "in January. Heat pump and furnace sizing matters more here than you'd think, and summer afternoons still hit 110°+."
        ),
        "response_claim": "Anthem is our home turf — typical response in 30 minutes from Anthem Way. Same-day service is the default, not the exception.",
        "local_detail": (
            "We service most of the Anthem Country Club, Parkside, Sierra Ridge, Anthem Parkside, and the newer builds off Memorial Way. "
            "Because Anthem's homes are mostly 2000-era construction, we see a lot of original 20+-year-old split systems finally giving up. "
            "When they do, we're usually the closest licensed team."
        )
    },
    {
        "slug": "new-river",
        "name": "New River",
        "zip_samples": ["85087"],
        "landmarks": "New River Mountain, Circle Mountain, Black Canyon City border",
        "lat": 33.9264,
        "lng": -112.1339,
        "climate_note": (
            "New River and the Carefree Highway corridor push 2,200 ft — winter lows regularly hit the upper 20s. Homes out here are often "
            "on propane rather than natural gas, which changes the math on heat pump vs. furnace decisions."
        ),
        "response_claim": "Same-day in New River. Emergency dispatch typically within 90 minutes — we stage trucks nearby.",
        "local_detail": (
            "New River homes tend to be larger, on bigger lots, and frequently have two or three HVAC systems serving the main house, casita, and shop. "
            "We're set up for that — multi-unit pricing, dual-thermostat callouts, and evening appointments to fit working owners."
        )
    },
    {
        "slug": "cave-creek",
        "name": "Cave Creek",
        "zip_samples": ["85331", "85262"],
        "landmarks": "Black Mountain, Cave Creek Recreation Area, Tonto National Forest entrance",
        "lat": 33.8334,
        "lng": -111.9509,
        "climate_note": (
            "Cave Creek and nearby Carefree see big day-to-night swings — 105°+ summer afternoons into low 60s overnight. That swing is "
            "actually brutal on HVAC systems, which constantly cycle between max cooling and long idle periods."
        ),
        "response_claim": "Same-day Cave Creek service. Most emergency calls on-site within 4 hours.",
        "local_detail": (
            "Cave Creek has a lot of architecturally ambitious homes — ranch-style with tile roofs and brick-heavy construction that holds heat "
            "well into the night. Oversized ACs here are a common problem we inherit from original installs. We right-size and re-commission rather "
            "than just swap like-for-like."
        )
    },
    {
        "slug": "desert-hills",
        "name": "Desert Hills",
        "zip_samples": ["85086"],
        "landmarks": "Desert Hills Park, North of Carefree Highway, Border of Anthem",
        "lat": 33.8256,
        "lng": -112.0931,
        "climate_note": (
            "Desert Hills sits just north of Carefree Highway and behaves climatically like Anthem and Tramonto — hot summer days, cool nights, "
            "and plenty of dust kicked up by monsoon storms that love to roll down the I-17 corridor."
        ),
        "response_claim": "Same-day Desert Hills service. North Valley-based dispatch keeps us 20 minutes away most days.",
        "local_detail": (
            "Desert Hills homes are often on 1+ acre lots with long driveways and detached shops — we're used to it. Our trucks carry duct, "
            "filter, and coil supplies sized for main-home plus outbuilding work in a single visit."
        )
    },
    {
        "slug": "north-scottsdale",
        "name": "North Scottsdale",
        "zip_samples": ["85255", "85262", "85266"],
        "landmarks": "Troon, DC Ranch, Grayhawk, McDowell Sonoran Preserve",
        "lat": 33.6792,
        "lng": -111.9261,
        "climate_note": (
            "North Scottsdale's foothills see slightly cooler overnights than central Phoenix but harder daytime sun exposure on south-facing "
            "elevations. High-end homes here often have 3+ zoned systems, variable-speed compressors, and premium filtration built in."
        ),
        "response_claim": "Full service in Troon, DC Ranch, Grayhawk, and the 85255/85262/85266 ZIPs. Same-day standard.",
        "local_detail": (
            "North Scottsdale is where we do a lot of our premium-tier work — Lennox Signature, Carrier Infinity, Mitsubishi Hyper-Heat. "
            "Every one of our senior techs is trained on zoned and variable-speed systems, so we're not 'figuring it out' on your $30,000 install."
        )
    },
    {
        "slug": "carefree",
        "name": "Carefree",
        "zip_samples": ["85377"],
        "landmarks": "Carefree Sundial, Boulders Resort, Spanish Bell Road",
        "lat": 33.8228,
        "lng": -111.9181,
        "climate_note": (
            "Carefree sits at ~2,400 ft — the highest of our service areas — which makes it a few degrees cooler year-round than central Phoenix. "
            "That changes the HVAC calculus, especially for winter heat."
        ),
        "response_claim": "Carefree is inside our regular route — same-day is the default.",
        "local_detail": (
            "Carefree homes lean toward custom builds with specific aesthetic requirements — concealed linesets, custom grille locations, "
            "quiet outdoor units staged away from patios. We know how to do HVAC work that stays invisible when it needs to."
        )
    },
    {
        "slug": "glendale",
        "name": "Glendale",
        "zip_samples": ["85308", "85310", "85304"],
        "landmarks": "Arrowhead, State Farm Stadium, Peoria/Glendale border",
        "lat": 33.5387,
        "lng": -112.1860,
        "climate_note": (
            "Glendale's West Valley climate runs a couple degrees hotter than Phoenix proper — lots of reflective surfaces, more pavement, "
            "and neighborhoods with less mature tree canopy. Your AC works harder here."
        ),
        "response_claim": "Same-day Glendale service from our Phoenix dispatch. Most emergency calls on-site within 4 hours.",
        "local_detail": (
            "Glendale has a mix of 1970s–1990s housing stock — a lot of the ductwork is original, R-6 flex with historical leakage rates of 15–30%. "
            "Before spending on a new AC, we always check whether duct sealing would solve half the complaint for a tenth of the cost."
        )
    },
    {
        "slug": "peoria",
        "name": "Peoria",
        "zip_samples": ["85381", "85382", "85383"],
        "landmarks": "Lake Pleasant, Vistancia, Sun City corridor",
        "lat": 33.5806,
        "lng": -112.2374,
        "climate_note": (
            "Peoria's northern edge (Vistancia, Lake Pleasant) cools off overnight much like Anthem; central Peoria runs hot like West Phoenix. "
            "Sizing really does matter by neighborhood."
        ),
        "response_claim": "Same-day Peoria service. Strong coverage across 85381, 85382, and 85383 ZIPs.",
        "local_detail": (
            "Lake Pleasant homes often have a different vibe than a typical Phoenix HVAC call — second homes, part-time occupancy, and a real "
            "need for 'remote eyes' on a system between owner visits. Our Comfort Club is genuinely perfect for this."
        )
    },
    {
        "slug": "surprise",
        "name": "Surprise",
        "zip_samples": ["85374", "85378", "85379", "85387", "85388"],
        "landmarks": "Sun City Grand, Marley Park, Surprise Stadium",
        "lat": 33.6292,
        "lng": -112.3679,
        "climate_note": (
            "Surprise runs similarly hot to West Phoenix — in the peak of summer the difference between a 14 SEER and an 18 SEER system "
            "is $70–$100 a month on the utility bill."
        ),
        "response_claim": "Same-day Surprise service. Most emergency calls on-site within 4 hours.",
        "local_detail": (
            "Surprise has large active-adult communities (Sun City Grand, Sun City West border) where fast, respectful, shoe-cover-on, "
            "text-before-arrival service is non-negotiable. That's how we work by default — not just for 55+ customers."
        )
    }
]

AREAS_BY_SLUG = {a["slug"]: a for a in AREAS}
