/**
 * VIDO Observation Detail Inspector Module
 * Renders full observation details and composite facet panels.
 */

export function openDetailInspector(obsData, linkData = []) {
  const backdrop = document.getElementById('inspector-modal');
  const modalBody = document.getElementById('inspector-modal-body');
  const modalTitle = document.getElementById('inspector-modal-title');

  if (!backdrop || !modalBody) return;

  modalTitle.textContent = `Observation Details: ${obsData.id}`;

  const metadata = obsData.metadata || {};
  const activeFacets = metadata.active_facets || [];

  modalBody.innerHTML = `
    <!-- Core Attributes Block -->
    <div class="facet-block">
      <div class="facet-block-header">🛰️ Core Observation Metadata</div>
      <div class="facet-grid">
        <div class="facet-field">
          <span class="facet-label">Observation ID</span>
          <span class="facet-value">${obsData.id}</span>
        </div>
        <div class="facet-field">
          <span class="facet-label">Volcanic System ID</span>
          <span class="facet-value">${obsData.volcanic_system_id}</span>
        </div>
        <div class="facet-field">
          <span class="facet-label">Source Instrument</span>
          <span class="facet-value">${obsData.source_id}</span>
        </div>
        <div class="facet-field">
          <span class="facet-label">ISO-8601 Timestamp</span>
          <span class="facet-value">${obsData.timestamp}</span>
        </div>
        <div class="facet-field">
          <span class="facet-label">Coordinates (Lat / Long)</span>
          <span class="facet-value">${obsData.latitude !== null ? `${obsData.latitude}°, ${obsData.longitude}°` : 'NULL (Volcano Fallback)'}</span>
        </div>
        <div class="facet-field">
          <span class="facet-label">Media Asset Path</span>
          <span class="facet-value">${obsData.media_path || 'None'}</span>
        </div>
      </div>
      <div style="margin-top: 10px; font-size: 0.85rem; color: var(--text-secondary);">
        <strong>Summary:</strong> ${escapeHtml(obsData.summary)}
      </div>
    </div>

    <!-- Active Composite Facets Banner -->
    <div style="font-size: 0.8rem; font-family: var(--font-mono); color: var(--accent-cyan); display: flex; align-items: center; gap: 8px;">
      <span>COMPOSITE FACETS DETECTED (${activeFacets.length}):</span>
      ${activeFacets.map(f => `<span class="badge badge-facet">${f}</span>`).join(' ')}
    </div>

    <!-- IMAGE Facet Block -->
    ${activeFacets.includes('IMAGE') && metadata.image_metadata ? renderImageFacet(metadata.image_metadata) : ''}

    <!-- THERMAL Facet Block -->
    ${activeFacets.includes('THERMAL') && metadata.thermal_metadata ? renderThermalFacet(metadata.thermal_metadata) : ''}

    <!-- PLANETARY ORBITAL Facet Block -->
    ${activeFacets.includes('PLANETARY_ORBITAL') && metadata.orbital_metadata ? renderOrbitalFacet(metadata.orbital_metadata) : ''}

    <!-- Linked Volcanic Events Block -->
    ${renderLinkedEventsBlock(linkData)}
  `;

  backdrop.classList.add('active');
}

export function closeDetailInspector() {
  const backdrop = document.getElementById('inspector-modal');
  if (backdrop) backdrop.classList.remove('active');
}

function renderImageFacet(img) {
  return `
    <div class="facet-block" style="border-left: 3px solid var(--accent-cyan);">
      <div class="facet-block-header">📷 IMAGE FACET PAYLOAD</div>
      <div class="facet-grid">
        <div class="facet-field">
          <span class="facet-label">Spectral Band</span>
          <span class="facet-value">${img.spectral_band}</span>
        </div>
        <div class="facet-field">
          <span class="facet-label">Spatial Resolution</span>
          <span class="facet-value">${img.spatial_resolution_m} meters/pixel</span>
        </div>
        <div class="facet-field">
          <span class="facet-label">Cloud Cover</span>
          <span class="facet-value">${img.cloud_cover_percentage}%</span>
        </div>
        <div class="facet-field">
          <span class="facet-label">File Format</span>
          <span class="facet-value">${img.file_format}</span>
        </div>
        <div class="facet-field">
          <span class="facet-label">Dimensions</span>
          <span class="facet-value">${img.image_dimensions ? `${img.image_dimensions.width} x ${img.image_dimensions.height}` : 'N/A'}</span>
        </div>
        <div class="facet-field">
          <span class="facet-label">Sun Elevation Angle</span>
          <span class="facet-value">${img.sun_elevation_angle_deg}°</span>
        </div>
      </div>
    </div>
  `;
}

function renderThermalFacet(thm) {
  return `
    <div class="facet-block" style="border-left: 3px solid var(--accent-thermal);">
      <div class="facet-block-header">🔥 THERMAL FACET PAYLOAD</div>
      <div class="facet-grid">
        <div class="facet-field">
          <span class="facet-label">Brightness Temp</span>
          <span class="facet-value">${thm.brightness_temperature_kelvin} K</span>
        </div>
        <div class="facet-field">
          <span class="facet-label">Ambient Temp</span>
          <span class="facet-value">${thm.ambient_temperature_kelvin} K</span>
        </div>
        <div class="facet-field">
          <span class="facet-label">Thermal Flux</span>
          <span class="facet-value">${thm.thermal_flux_mw} MW</span>
        </div>
        <div class="facet-field">
          <span class="facet-label">Sensor Wavelength</span>
          <span class="facet-value">${thm.sensor_wavelength_um} µm</span>
        </div>
        <div class="facet-field">
          <span class="facet-label">Thermal Anomaly</span>
          <span class="facet-value" style="color: ${thm.anomaly_flag ? '#ffab00' : 'var(--text-secondary)'};">${thm.anomaly_flag ? 'YES (Detected)' : 'No'}</span>
        </div>
        <div class="facet-field">
          <span class="facet-label">Sensor Saturation</span>
          <span class="facet-value">${thm.saturation_threshold_exceeded ? 'Exceeded' : 'Normal'}</span>
        </div>
      </div>
    </div>
  `;
}

function renderOrbitalFacet(orb) {
  return `
    <div class="facet-block" style="border-left: 3px solid var(--accent-purple);">
      <div class="facet-block-header">🪐 PLANETARY ORBITAL FACET PAYLOAD</div>
      <div class="facet-grid">
        <div class="facet-field">
          <span class="facet-label">Spacecraft Altitude</span>
          <span class="facet-value">${orb.spacecraft_altitude_km} km</span>
        </div>
        <div class="facet-field">
          <span class="facet-label">Solar Incidence Angle</span>
          <span class="facet-value">${orb.solar_incidence_angle_deg}°</span>
        </div>
        <div class="facet-field">
          <span class="facet-label">Emission Angle</span>
          <span class="facet-value">${orb.emission_angle_deg}°</span>
        </div>
        <div class="facet-field">
          <span class="facet-label">Phase Angle</span>
          <span class="facet-value">${orb.phase_angle_deg}°</span>
        </div>
        <div class="facet-field">
          <span class="facet-label">Target Planetary Datum</span>
          <span class="facet-value">${orb.target_planetary_datum}</span>
        </div>
      </div>
    </div>
  `;
}

function renderLinkedEventsBlock(linkData) {
  if (!linkData || linkData.length === 0) {
    return `
      <div class="facet-block">
        <div class="facet-block-header" style="color: var(--text-secondary);">VOLCANIC EVENT RELATIONSHIPS</div>
        <div style="font-size: 0.8rem; color: var(--text-muted);">No eruptive event links associated with this observation.</div>
      </div>
    `;
  }

  return `
    <div class="facet-block">
      <div class="facet-block-header">⚡ VOLCANIC EVENT RELATIONSHIPS (${linkData.length})</div>
      <div style="display: flex; flex-direction: column; gap: 8px;">
        ${linkData.map(l => `
          <div style="font-size: 0.85rem; padding: 8px 12px; background: rgba(255,255,255,0.03); border-radius: 4px; border: 1px solid var(--border-color); display: flex; justify-content: space-between; align-items: center;">
            <div>
              <strong>${escapeHtml(l.event_title)}</strong>
              <div style="font-size: 0.75rem; color: var(--text-secondary); font-family: var(--font-mono);">
                Type: ${l.event_type || 'N/A'} • Offset: ${l.temporal_offset_hours !== null ? `${l.temporal_offset_hours} hours` : 'N/A'}
              </div>
            </div>
            <div>
              <span class="badge" style="background: rgba(0,229,255,0.15); color: var(--accent-cyan);">${l.relationship_type}</span>
            </div>
          </div>
        `).join('')}
      </div>
    </div>
  `;
}

function escapeHtml(str) {
  if (!str) return '';
  return String(str).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}
