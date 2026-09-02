/**
 * VIDO Spatial Visualization Module
 * Handles Earth Leaflet map rendering and Planetary Positive East (0-360) 2D Grid Canvas rendering.
 */

let leafletMap = null;
let leafletMarkers = [];

export function renderSpatialView(containerId, body, system, spatialData, onSelectObservation) {
  const leafletElem = document.getElementById('leaflet-container');
  const canvasContainer = document.getElementById('planetary-canvas-container');
  const unlocatedContainer = document.getElementById('unlocated-list');

  // Clear unlocated list
  if (unlocatedContainer) unlocatedContainer.innerHTML = '';

  const locatedObs = spatialData.located_observations || [];
  const unlocatedObs = spatialData.unlocated_observations || [];

  // Render Unlocated Observations List separately
  if (unlocatedContainer && unlocatedObs.length > 0) {
    unlocatedContainer.style.display = 'block';
    unlocatedContainer.innerHTML = `
      <div style="font-size: 0.75rem; font-family: var(--font-mono); color: var(--text-muted); margin-bottom: 6px;">
        UNLOCATED OBSERVATIONS (${unlocatedObs.length})
      </div>
      ${unlocatedObs.map(obs => `
        <div class="unlocated-item" style="font-size: 0.8rem; padding: 4px 8px; background: rgba(255,255,255,0.03); border-radius: 4px; margin-bottom: 4px; display: flex; justify-content: space-between;">
          <span>${escapeHtml(obs.summary)}</span>
          <span style="color: var(--text-muted); font-family: var(--font-mono);">${obs.timestamp.split('T')[0]}</span>
        </div>
      `).join('')}
    `;
  } else if (unlocatedContainer) {
    unlocatedContainer.style.display = 'none';
  }

  // Determine view mode based on CelestialBody convention
  const isEarthConvention = body.longitude_convention === 'EAST_WEST_180';

  if (isEarthConvention) {
    // Show Leaflet Map
    if (canvasContainer) canvasContainer.style.display = 'none';
    if (leafletElem) leafletElem.style.display = 'block';

    renderLeafletMap(system, locatedObs, onSelectObservation);
  } else {
    // Show Planetary Canvas Grid (0-360 Positive East)
    if (leafletElem) leafletElem.style.display = 'none';
    if (canvasContainer) canvasContainer.style.display = 'block';

    renderPlanetaryCanvas(body, system, locatedObs, onSelectObservation);
  }
}

function renderLeafletMap(system, locatedObs, onSelectObservation) {
  if (typeof L === 'undefined') return;

  const lat = system ? system.latitude : 0;
  const lng = system ? system.longitude : 0;
if (!leafletMap) {
  leafletMap = L.map('leaflet-container').setView([lat, lng], 5);

  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; OpenStreetMap contributors',
    maxZoom: 19
  }).addTo(leafletMap);

} else {
  leafletMap.setView([lat, lng], 5);
  leafletMarkers.forEach(m => leafletMap.removeLayer(m));
  leafletMarkers = [];
}

  // Add System Marker
  if (system) {
    const sysMarker = L.circleMarker([system.latitude, system.longitude], {
      radius: 8,
      fillColor: '#ffab00',
      color: '#ffffff',
      weight: 2,
      opacity: 1,
      fillOpacity: 0.9
    }).addTo(leafletMap);
    sysMarker.bindPopup(`<b>${escapeHtml(system.name)}</b><br/>Volcanic System (Parent)`);
    leafletMarkers.push(sysMarker);
  }

  // Add Observation Markers
  locatedObs.forEach(obs => {
    if (obs.latitude !== null && obs.longitude !== null) {
      const isFallback = obs.spatial_source === 'VOLCANO_FALLBACK';
      const color = isFallback ? '#ffab00' : '#00e5ff';

      const obsMarker = L.circleMarker([obs.latitude, obs.longitude], {
        radius: isFallback ? 5 : 6,
        fillColor: color,
        color: '#ffffff',
        weight: 1,
        opacity: 0.9,
        fillOpacity: 0.8
      }).addTo(leafletMap);

      obsMarker.bindPopup(`
        <b>${escapeHtml(obs.summary)}</b><br/>
        <small>Source Tag: ${obs.spatial_source}</small><br/>
        <small>Date: ${obs.timestamp}</small>
      `);

      if (onSelectObservation) {
        obsMarker.on('click', () => onSelectObservation(obs.observation_id));
      }

      leafletMarkers.push(obsMarker);
    }
  });

  setTimeout(() => leafletMap.invalidateSize(), 100);
}

function renderPlanetaryCanvas(body, system, locatedObs, onSelectObservation) {
  const canvas = document.getElementById('planetary-canvas');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');

  // Resize canvas to match display container
  canvas.width = canvas.parentElement.clientWidth || 600;
  canvas.height = canvas.parentElement.clientHeight || 360;

  const w = canvas.width;
  const h = canvas.height;
  const padding = 40;

  // Clear background
  ctx.fillStyle = '#05070a';
  ctx.fillRect(0, 0, w, h);

  // Draw Grid Lines (Longitude 0 to 360, Latitude -90 to +90)
  ctx.strokeStyle = '#1e293b';
  ctx.lineWidth = 1;
  ctx.font = '10px SFMono-Regular, monospace';
  ctx.fillStyle = '#64748b';

  // Longitude Vertical Lines (every 45 degrees)
  for (let long = 0; long <= 360; long += 45) {
    const x = padding + (long / 360) * (w - 2 * padding);
    ctx.beginPath();
    ctx.moveTo(x, padding);
    ctx.lineTo(x, h - padding);
    ctx.stroke();

    ctx.fillText(`${long}°E`, x - 10, h - padding + 15);
  }

  // Latitude Horizontal Lines (every 30 degrees)
  for (let lat = -90; lat <= 90; lat += 30) {
    const y = h - padding - ((lat + 90) / 180) * (h - 2 * padding);
    ctx.beginPath();
    ctx.moveTo(padding, y);
    ctx.lineTo(w - padding, y);
    ctx.stroke();

    ctx.fillText(`${lat}°`, padding - 25, y + 3);
  }

  // Draw Title Overlay
  ctx.fillStyle = '#94a3b8';
  ctx.font = '11px SFMono-Regular, monospace';
  ctx.fillText(`${body.name.toUpperCase()} PLANETARY COORDINATE GRID (${body.coordinate_system})`, padding, 20);

  // Helper coordinate mapper
  const mapCoords = (lat, long) => {
    const x = padding + (long / 360) * (w - 2 * padding);
    const y = h - padding - ((lat + 90) / 180) * (h - 2 * padding);
    return { x, y };
  };

  // Plot Volcanic System Anchor
  if (system) {
    const sysPos = mapCoords(system.latitude, system.longitude);
    ctx.fillStyle = '#ffab00';
    ctx.strokeStyle = '#ffffff';
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.arc(sysPos.x, sysPos.y, 7, 0, 2 * Math.PI);
    ctx.fill();
    ctx.stroke();

    ctx.fillStyle = '#ffab00';
    ctx.font = 'bold 11px sans-serif';
    ctx.fillText(system.name, sysPos.x + 10, sysPos.y + 4);
  }

  // Plot Observations
  locatedObs.forEach(obs => {
    if (obs.latitude !== null && obs.longitude !== null) {
      const pos = mapCoords(obs.latitude, obs.longitude);
      const isFallback = obs.spatial_source === 'VOLCANO_FALLBACK';

      ctx.fillStyle = isFallback ? '#ffab00' : '#00e5ff';
      ctx.strokeStyle = '#ffffff';
      ctx.lineWidth = 1;
      ctx.beginPath();
      ctx.arc(pos.x, pos.y, isFallback ? 4 : 5, 0, 2 * Math.PI);
      ctx.fill();
      ctx.stroke();
    }
  });
}

function escapeHtml(str) {
  if (!str) return '';
  return String(str).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}
