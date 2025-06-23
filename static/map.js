const map = L.map('map').setView([51.4556, 7.0116], 13);
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
  attribution: '© OpenStreetMap contributors'
}).addTo(map);

let selectedLine = typeof INITIAL_LINE !== 'undefined' ? INITIAL_LINE : '';
const markers = {};

function getColor(line) {
  const colors = ['red', 'blue', 'green', 'orange', 'purple', 'brown'];
  let idx = 0;
  for (let i = 0; i < line.length; i++) {
    idx = (idx + line.charCodeAt(i)) % colors.length;
  }
  return colors[idx];
}

function loadLines() {
  fetch('/vehicles')
    .then(r => r.json())
    .then(data => {
      const select = document.getElementById('line-filter');
      const lines = [...new Set(data.map(v => v.line))].sort();
      lines.forEach(l => {
        const opt = document.createElement('option');
        opt.value = l;
        opt.textContent = l;
        if (l === selectedLine) opt.selected = true;
        select.appendChild(opt);
      });
    });
}

function updateVehicles() {
  const url = selectedLine ? `/vehicles?line=${encodeURIComponent(selectedLine)}` : '/vehicles';
  fetch(url)
    .then(r => r.json())
    .then(data => {
      for (const key in markers) {
        map.removeLayer(markers[key]);
      }
      for (const v of data) {
        const key = `${v.line}-${v.course}`;
        const icon = L.divIcon({
          className: '',
          html: `<div class="tram-marker" style="border-bottom-color:${getColor(v.line)}"></div>`,
          iconSize: [16, 16],
          iconAnchor: [8, 8]
        });
        const marker = L.marker([v.lat, v.lon], { icon, rotationAngle: v.direction }).addTo(map);
        marker.bindPopup(`<b>Linie:</b> ${v.line}<br><b>Kurs:</b> ${v.course}`);
        markers[key] = marker;
      }
    });
}

document.getElementById('line-filter').addEventListener('change', ev => {
  const line = ev.target.value;
  if (line) {
    window.location.search = '?line=' + encodeURIComponent(line);
  } else {
    window.location.search = location.pathname;
  }
});

loadLines();
updateVehicles();
setInterval(updateVehicles, 15000);
