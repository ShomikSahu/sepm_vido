/**
 * VIDO Main Application Controller
 * Coordinates UI state, celestial body selection, filtering, spatial rendering, timeline, and modal inspection.
 */

import * as API from './api.js';
import { renderSpatialView } from './spatial.js';
import { renderTimelineView } from './timeline.js';
import { openDetailInspector, closeDetailInspector } from './inspector.js';

let state = {
  celestialBodies: [],
  activeBody: null,
  volcanicSystems: [],
  activeSystem: null,
  observations: [],
  activeFacetFilter: 'ALL',
  searchQuery: '',
};

document.addEventListener('DOMContentLoaded', async () => {
  initEventListeners();
  await loadInitialData();
});

function initEventListeners() {
  // System Select Dropdown
  const sysSelect = document.getElementById('system-select');
  if (sysSelect) {
    sysSelect.addEventListener('change', (e) => {
      const selectedId = e.target.value;
      state.activeSystem = state.volcanicSystems.find(s => s.id === selectedId) || null;
      refreshDashboardViews();
    });
  }

  // Facet Filter Buttons
  document.querySelectorAll('.facet-btn').forEach(btn => {
    btn.addEventListener('click', (e) => {
      document.querySelectorAll('.facet-btn').forEach(b => b.classList.remove('active'));
      e.target.classList.add('active');
      state.activeFacetFilter = e.target.getAttribute('data-facet');
      refreshObservationsExplorer();
    });
  });

  // Search Input
  const searchInput = document.getElementById('search-input');
  if (searchInput) {
    searchInput.addEventListener('input', (e) => {
      state.searchQuery = e.target.value.trim().toLowerCase();
      refreshObservationsExplorer();
    });
  }

  // Modal Close
  const closeBtn = document.getElementById('modal-close-btn');
  const backdrop = document.getElementById('inspector-modal');
  if (closeBtn) closeBtn.addEventListener('click', closeDetailInspector);
  if (backdrop) {
    backdrop.addEventListener('click', (e) => {
      if (e.target === backdrop) closeDetailInspector();
    });
  }
}

async function loadInitialData() {
  try {
    showLoadingState(true);
    state.celestialBodies = await API.getCelestialBodies();
    
    renderCelestialBodyPills();

    // Default to Earth
    if (state.celestialBodies.length > 0) {
      await selectCelestialBody(state.celestialBodies[0].id);
    }
  } catch (err) {
    showErrorMessage(`Failed to initialize observatory data: ${err.message}`);
  } finally {
    showLoadingState(false);
  }
}

function renderCelestialBodyPills() {
  const container = document.getElementById('body-pills-container');
  if (!container) return;

  container.innerHTML = state.celestialBodies.map(body => {
    const isEarth = body.longitude_convention === 'EAST_WEST_180';
    const crsText = isEarth ? 'WGS84 • -180° to +180°' : `${body.coordinate_system} • Positive East 0° to 360°`;

    return `
      <div class="body-pill ${state.activeBody && state.activeBody.id === body.id ? 'active' : ''}" data-body-id="${body.id}">
        <span>${escapeHtml(body.name)}</span>
        <span class="crs-info">${crsText}</span>
      </div>
    `;
  }).join('');

  container.querySelectorAll('.body-pill').forEach(pill => {
    pill.addEventListener('click', async () => {
      const bodyId = pill.getAttribute('data-body-id');
      await selectCelestialBody(bodyId);
    });
  });
}

async function selectCelestialBody(bodyId) {
  state.activeBody = state.celestialBodies.find(b => b.id === bodyId) || null;
  renderCelestialBodyPills();

  // Update Volcanic Systems Dropdown
  state.volcanicSystems = await API.getVolcanicSystems(bodyId);
  const sysSelect = document.getElementById('system-select');
  if (sysSelect) {
    sysSelect.innerHTML = state.volcanicSystems.map(sys => `
      <option value="${sys.id}">${escapeHtml(sys.name)} (${sys.volcanic_type})</option>
    `).join('');

    if (state.volcanicSystems.length > 0) {
      sysSelect.value = state.volcanicSystems[0].id;
      state.activeSystem = state.volcanicSystems[0];
    } else {
      state.activeSystem = null;
    }
  }

  await refreshDashboardViews();
}

async function refreshDashboardViews() {
  if (!state.activeSystem) return;

  try {
    showLoadingState(true);

    // Fetch Spatial, Timeline, and Observations data in parallel
    const [spatialData, timelineData, observations] = await Promise.all([
      API.getSystemSpatial(state.activeSystem.id),
      API.getSystemTimeline(state.activeSystem.id),
      API.getObservations({ volcanic_system_id: state.activeSystem.id }),
    ]);

    state.observations = observations;

    // Render Spatial View (Leaflet or Planetary Canvas Grid)
    renderSpatialView('spatial-panel-body', state.activeBody, state.activeSystem, spatialData, inspectObservationById);

    // Render Chronological Timeline View
    renderTimelineView('timeline-panel-body', timelineData, inspectObservationById);

    // Render Observation Explorer Feed
    refreshObservationsExplorer();

  } catch (err) {
    showErrorMessage(`Error refreshing observatory views: ${err.message}`);
  } finally {
    showLoadingState(false);
  }
}

function refreshObservationsExplorer() {
  const container = document.getElementById('obs-explorer-list');
  if (!container) return;

  let filtered = state.observations;

  // Facet Filter
  if (state.activeFacetFilter !== 'ALL') {
    filtered = filtered.filter(obs => {
      const facets = obs.metadata ? obs.metadata.active_facets || [] : [];
      return facets.includes(state.activeFacetFilter);
    });
  }

  // Search Query
  if (state.searchQuery) {
    filtered = filtered.filter(obs => 
      obs.summary.toLowerCase().includes(state.searchQuery) ||
      obs.id.toLowerCase().includes(state.searchQuery) ||
      obs.source_id.toLowerCase().includes(state.searchQuery)
    );
  }

  if (filtered.length === 0) {
    container.innerHTML = `<div style="color: var(--text-muted); padding: 20px; text-align: center;">No observations match current filter criteria.</div>`;
    return;
  }

  container.innerHTML = `
    <div class="obs-list">
      ${filtered.map(obs => renderObservationSummaryCard(obs)).join('')}
    </div>
  `;

  // Attach card click handlers
  container.querySelectorAll('.obs-card').forEach(card => {
    card.addEventListener('click', () => {
      const obsId = card.getAttribute('data-obs-id');
      inspectObservationById(obsId);
    });
  });
}

function renderObservationSummaryCard(obs) {
  const metadata = obs.metadata || {};
  const activeFacets = metadata.active_facets || [];
  const facetPills = activeFacets.map(f => `<span class="badge badge-facet">${f}</span>`).join(' ');

  return `
    <div class="obs-card" data-obs-id="${obs.id}">
      <div class="obs-header">
        <div class="obs-title">${escapeHtml(obs.summary)}</div>
        <span class="badge" style="background: rgba(255,255,255,0.06); color: var(--text-secondary); font-family: var(--font-mono);">${obs.id}</span>
      </div>
      <div class="obs-meta">
        <span>📅 ${obs.timestamp}</span>
        <span>📡 ${obs.source_id}</span>
        <span>📍 ${obs.latitude !== null ? `${obs.latitude}°, ${obs.longitude}°` : 'Volcano Fallback'}</span>
      </div>
      <div class="facet-pills">
        ${facetPills || '<span class="badge" style="color:var(--text-muted);">No Facets</span>'}
      </div>
    </div>
  `;
}

async function inspectObservationById(obsId) {
  try {
    const [obsData, linkData] = await Promise.all([
      API.getObservationDetail(obsId),
      API.getObservationLinks(obsId).catch(() => []),
    ]);
    openDetailInspector(obsData, linkData);
  } catch (err) {
    alert(`Unable to load observation details: ${err.message}`);
  }
}

function showLoadingState(isLoading) {
  const loader = document.getElementById('loading-indicator');
  if (loader) loader.style.display = isLoading ? 'flex' : 'none';
}

function showErrorMessage(msg) {
  const errorContainer = document.getElementById('error-banner');
  if (errorContainer) {
    errorContainer.textContent = msg;
    errorContainer.style.display = 'block';
    setTimeout(() => { errorContainer.style.display = 'none'; }, 5000);
  }
}

function escapeHtml(str) {
  if (!str) return '';
  return String(str).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}
