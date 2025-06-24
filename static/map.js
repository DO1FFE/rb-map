const map = L.map('map').setView([51.4556, 7.0116], 13);
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
  attribution: '© OpenStreetMap contributors'
}).addTo(map);

let selectedLine = typeof INITIAL_LINE !== 'undefined' ? INITIAL_LINE : '';
let selectedCourse = typeof INITIAL_COURSE !== 'undefined' ? INITIAL_COURSE : '';
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
  fetch('/lines')
    .then(r => r.json())
    .then(lines => {
      const select = document.getElementById('line-filter');
      select.innerHTML = '<option value="">Alle Linien</option>';
      lines.forEach(l => {
        const opt = document.createElement('option');
        opt.value = l;
        opt.textContent = l;
        if (l === selectedLine) opt.selected = true;
        select.appendChild(opt);
      });
      if (selectedLine) {
        loadCourses(selectedLine);
      }
    });
}

function loadCourses(line) {
  fetch(`/courses?line=${encodeURIComponent(line)}`)
    .then(r => r.json())
    .then(courses => {
      const select = document.getElementById('course-filter');
      select.style.display = 'block';
      select.innerHTML = '<option value="">Alle Kurse</option>';
      courses.forEach(c => {
        const opt = document.createElement('option');
        opt.value = c;
        opt.textContent = c;
        if (c === selectedCourse) opt.selected = true;
        select.appendChild(opt);
      });
    });
}

function updateVehicles() {
  let url = '/vehicles';
  const params = [];
  if (selectedLine) {
    params.push(`line=${encodeURIComponent(selectedLine)}`);
  }
  if (selectedCourse) {
    params.push(`course=${encodeURIComponent(selectedCourse)}`);
  }
  if (params.length > 0) {
    url += '?' + params.join('&');
  }
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
  selectedLine = ev.target.value;
  selectedCourse = '';
  const courseSelect = document.getElementById('course-filter');
  if (selectedLine) {
    loadCourses(selectedLine);
    const params = new URLSearchParams(window.location.search);
    params.set('line', selectedLine);
    params.delete('course');
    window.history.replaceState({}, '', `?${params.toString()}`);
  } else {
    courseSelect.style.display = 'none';
    courseSelect.innerHTML = '<option value="">Alle Kurse</option>';
    const params = new URLSearchParams(window.location.search);
    params.delete('line');
    params.delete('course');
    const url = params.toString() ? `?${params.toString()}` : location.pathname;
    window.history.replaceState({}, '', url);
    updateVehicles();
  }
  updateVehicles();
});

document.getElementById('course-filter').addEventListener('change', ev => {
  selectedCourse = ev.target.value;
  const params = new URLSearchParams(window.location.search);
  if (selectedCourse) {
    params.set('course', selectedCourse);
  } else {
    params.delete('course');
  }
  window.history.replaceState({}, '', `?${params.toString()}`);
  updateVehicles();
});

loadLines();
updateVehicles();
setInterval(updateVehicles, 15000);
