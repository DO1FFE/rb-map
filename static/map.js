const map = L.map('map').setView([51.45, 7.01], 13);
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
  attribution: '© OpenStreetMap-Mitwirkende'
}).addTo(map);

let markers = {};

function updateVehicles() {
  fetch('/api/vehicles')
    .then(res => res.json())
    .then(data => {
      for (const id in markers) {
        map.removeLayer(markers[id]);
      }
      markers = {};

      data.forEach(v => {
        const key = `${v.line}-${v.course}`;
        const marker = L.marker([v.lat, v.lon]).addTo(map)
          .bindPopup(`<b>Linie:</b> ${v.line}<br><b>Kurs:</b> ${v.course}`);
        markers[key] = marker;
      });
    });
}

updateVehicles();
setInterval(updateVehicles, 15000);
