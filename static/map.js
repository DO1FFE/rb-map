const map = L.map('map').setView([51.4556, 7.0116], 13);
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
  attribution: '© OpenStreetMap contributors'
}).addTo(map);

let selectedLine = typeof INITIAL_LINE !== 'undefined' ? INITIAL_LINE : '';
let selectedCourse = typeof INITIAL_COURSE !== 'undefined' ? INITIAL_COURSE : '';
const markers = {};
const courseListEl = document.getElementById('course-list');
const essenSelect = document.getElementById('essen-line-filter');
const courseDivs = {};

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

function loadEssenLines() {
  fetch('/essen_lines')
    .then(r => r.json())
    .then(lines => {
      essenSelect.innerHTML = '<option value="">Essener Linien</option>';
      lines.forEach(l => {
        const opt = document.createElement('option');
        opt.value = l;
        opt.textContent = l;
        essenSelect.appendChild(opt);
      });
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
        const tramIcon = L.divIcon({
          className: '',
          html: `<div class="tram-marker" style="border-bottom-color:${getColor(v.line)}"></div>`,
          iconSize: [16, 16],
          iconAnchor: [8, 8]
        });
        const marker = L.marker([v.lat, v.lon], {
          icon: tramIcon,
          rotationAngle: v.direction,
          rotationOrigin: 'center center'
        }).addTo(map);
        marker.bindPopup(`<b>Linie:</b> ${v.line}<br><b>Kurs:</b> ${v.course}`);
        markers[key] = marker;
      }
    });
}

function updateMissingCourses() {
  let url = '/missing_courses';
  const params = [];
  if (selectedLine) {
    params.push(`line=${encodeURIComponent(selectedLine)}`);
  }
  if (params.length > 0) {
    url += '?' + params.join('&');
  }
  fetch(url)
    .then(r => r.json())
    .then(data => {
      if (data.length === 0) {
        courseListEl.textContent = 'Keine Fahrten ohne Standort.';
        for (const key in courseDivs) {
          courseListEl.removeChild(courseDivs[key]);
          delete courseDivs[key];
        }
        return;
      }
      data.sort((a, b) => parseInt(b.line, 10) - parseInt(a.line, 10));
      const seen = new Set();
      data.forEach(c => {
        const key = `${c.line}-${c.course}`;
        const vehicle = c.vehicle ? ` (${c.vehicle})` : '';
        const text = `${c.line} | ${c.course}${vehicle} -> ${c.next_stop}`;
        seen.add(key);
        let div = courseDivs[key];
        if (div) {
          if (div.textContent !== text) {
            div.textContent = text;
            div.classList.add('updated');
            setTimeout(() => div.classList.remove('updated'), 2000);
          }
        } else {
          div = document.createElement('div');
          div.textContent = text;
          div.classList.add('updated');
          setTimeout(() => div.classList.remove('updated'), 2000);
          courseDivs[key] = div;
        }
        courseListEl.appendChild(div);
      });
      Object.keys(courseDivs).forEach(k => {
        if (!seen.has(k)) {
          courseListEl.removeChild(courseDivs[k]);
          delete courseDivs[k];
        }
      });
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
    updateMissingCourses();
  }
  updateVehicles();
  updateMissingCourses();
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
  updateMissingCourses();
});

essenSelect.addEventListener('change', ev => {
  const value = ev.target.value;
  document.getElementById('line-filter').value = value;
  const event = new Event('change');
  document.getElementById('line-filter').dispatchEvent(event);
});

loadEssenLines();

loadLines();
updateVehicles();
updateMissingCourses();
setInterval(() => { updateVehicles(); updateMissingCourses(); }, 10000);
