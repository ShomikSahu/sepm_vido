/**
 * VIDO API Client
 * Encapsulates async REST API calls to /api/v1 endpoints.
 */

const API_BASE = '/api/v1';

export async function fetchJson(endpoint, options = {}) {
  try {
    const response = await fetch(`${API_BASE}${endpoint}`, options);
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ detail: response.statusText }));
      throw new Error(errorData.detail || `HTTP Error ${response.status}`);
    }
    return await response.json();
  } catch (err) {
    console.error(`[API Error] ${endpoint}:`, err);
    throw err;
  }
}

export async function getCelestialBodies() {
  return await fetchJson('/celestial-bodies');
}

export async function getVolcanicSystems(celestialBodyId = null) {
  const query = celestialBodyId ? `?celestial_body_id=${encodeURIComponent(celestialBodyId)}` : '';
  return await fetchJson(`/volcanic-systems${query}`);
}

export async function getVolcanicSystemDetail(systemId) {
  return await fetchJson(`/volcanic-systems/${encodeURIComponent(systemId)}`);
}

export async function getSystemSpatial(systemId) {
  return await fetchJson(`/volcanic-systems/${encodeURIComponent(systemId)}/spatial`);
}

export async function getSystemTimeline(systemId) {
  return await fetchJson(`/volcanic-systems/${encodeURIComponent(systemId)}/timeline`);
}

export async function getObservationSources() {
  return await fetchJson('/observation-sources');
}

export async function getObservations(filters = {}) {
  const params = new URLSearchParams();
  if (filters.volcanic_system_id) params.append('volcanic_system_id', filters.volcanic_system_id);
  if (filters.celestial_body_id) params.append('celestial_body_id', filters.celestial_body_id);
  if (filters.source_id) params.append('source_id', filters.source_id);
  if (filters.facet) params.append('facet', filters.facet);
  if (filters.start_date) params.append('start_date', filters.start_date);
  if (filters.end_date) params.append('end_date', filters.end_date);

  const query = params.toString() ? `?${params.toString()}` : '';
  return await fetchJson(`/observations${query}`);
}

export async function getObservationDetail(observationId) {
  return await fetchJson(`/observations/${encodeURIComponent(observationId)}`);
}

export async function getVolcanicEvents(systemId = null, ongoingOnly = false) {
  const params = new URLSearchParams();
  if (systemId) params.append('volcanic_system_id', systemId);
  if (ongoingOnly) params.append('ongoing_only', 'true');
  const query = params.toString() ? `?${params.toString()}` : '';
  return await fetchJson(`/volcanic-events${query}`);
}

export async function getObservationLinks(observationId) {
  return await fetchJson(`/observations/${encodeURIComponent(observationId)}/links`);
}
