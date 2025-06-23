const map = L.map('map').setView([51.45, 7.01], 13);
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
  attribution: '© OpenStreetMap-Mitwirkende'
}).addTo(map);

function loadLines() {
  fetch('/api/lines')
    .then(res => res.json())
    .then(lines => {
      const select = document.getElementById('line-filter');
      lines.forEach(line => {
        const opt = document.createElement('option');
        opt.value = line;
        opt.textContent = line;
        select.appendChild(opt);
      });
    });
}

let markers = {};

function updateVehicles() {
  const line = document.getElementById('line-filter').value;
  const url = line ? `/api/vehicles?line=${encodeURIComponent(line)}` : '/api/vehicles';
  fetch(url)
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

loadLines();
updateVehicles();
setInterval(updateVehicles, 15000);
