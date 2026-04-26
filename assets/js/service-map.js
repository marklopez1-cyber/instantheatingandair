/* Service-area map for /service-areas/ — Leaflet + OpenStreetMap.
   Renders only when both #service-map and the Leaflet global (L) exist. */
(function () {
  var mapEl = document.getElementById('service-map');
  if (!mapEl || typeof L === 'undefined') return;

  var ZONE_COLOR = '#C0392B';

  var map = L.map('service-map', {
    scrollWheelZoom: false,        // avoid hijacking page scroll
    zoomControl: true
  }).setView([33.66, -112.10], 9);

  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 18,
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
  }).addTo(map);

  // Outer service-area polygon (covers Anthem to Surprise / Glendale to N Scottsdale).
  // Approximated rectangle with slight bevels so the shape doesn't look like a screen-capture box.
  var serviceZone = [
    [33.96, -112.50], [33.96, -112.10], [33.96, -111.75],
    [33.70, -111.74], [33.50, -111.78],
    [33.42, -111.85], [33.42, -112.20], [33.42, -112.50],
    [33.65, -112.55], [33.85, -112.55]
  ];

  L.polygon(serviceZone, {
    color: ZONE_COLOR,
    weight: 2,
    dashArray: '8 6',
    fillColor: ZONE_COLOR,
    fillOpacity: 0.14
  }).addTo(map).bindPopup(
    '<strong>Instant Heating and Air</strong><br>Same-day HVAC service zone &mdash; Phoenix Valley'
  );

  // City centers + slugs to detail pages
  var cities = [
    { name: 'Phoenix',          slug: 'phoenix',          lat: 33.4484, lng: -112.0740 },
    { name: 'Peoria',           slug: 'peoria',           lat: 33.5806, lng: -112.2374 },
    { name: 'Scottsdale',       slug: 'north-scottsdale', lat: 33.6792, lng: -111.9261 },
    { name: 'Anthem',           slug: 'anthem',           lat: 33.8678, lng: -112.1391 },
    { name: 'New River',        slug: 'new-river',        lat: 33.9264, lng: -112.1339 },
    { name: 'Cave Creek',       slug: 'cave-creek',       lat: 33.8334, lng: -111.9509 },
    { name: 'Desert Hills',     slug: 'desert-hills',     lat: 33.8256, lng: -112.0931 },
    { name: 'Carefree',         slug: 'carefree',         lat: 33.8228, lng: -111.9181 },
    { name: 'Glendale',         slug: 'glendale',         lat: 33.5387, lng: -112.1860 },
    { name: 'Surprise',         slug: 'surprise',         lat: 33.6292, lng: -112.3679 }
  ];

  cities.forEach(function (c) {
    L.circleMarker([c.lat, c.lng], {
      radius: 7,
      color: '#fff',
      weight: 2,
      fillColor: ZONE_COLOR,
      fillOpacity: 0.95
    }).addTo(map).bindPopup(
      '<strong>' + c.name + ', AZ</strong><br>' +
      '<a href="/service-areas/' + c.slug + '.html">Service in ' + c.name + ' &rarr;</a>'
    );
  });
})();
