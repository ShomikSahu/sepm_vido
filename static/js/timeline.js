/**
 * VIDO Timeline Module
 * Renders dual-lane (Events vs Observations) and interleaved chronological feeds.
 */

export function renderTimelineView(containerId, timelineData, onSelectObservation) {
  const container = document.getElementById(containerId);
  if (!container) return;

  if (!timelineData || (timelineData.events_count === 0 && timelineData.observations_count === 0)) {
    container.innerHTML = `<div style="color: var(--text-muted); font-size: 0.85rem; text-align: center; padding: 20px;">No timeline records available for this volcanic system.</div>`;
    return;
  }

  const events = timelineData.events_lane || [];
  const observations = timelineData.observations_lane || [];

  container.innerHTML = `
    <div class="timeline-container">
      <!-- Events Lane -->
      <div class="timeline-lane">
        <div class="lane-title">⚡ VOLCANIC EVENTS (${events.length})</div>
        <div class="timeline-items">
          ${events.length === 0 ? '<div style="font-size:0.75rem; color:var(--text-muted);">No eruptive events recorded</div>' : ''}
          ${events.map(evt => renderEventCard(evt)).join('')}
        </div>
      </div>

      <!-- Observations Lane -->
      <div class="timeline-lane">
        <div class="lane-title">📡 OBSERVATIONS (${observations.length})</div>
        <div class="timeline-items">
          ${observations.length === 0 ? '<div style="font-size:0.75rem; color:var(--text-muted);">No observations recorded</div>' : ''}
          ${observations.map(obs => renderObservationTimelineCard(obs)).join('')}
        </div>
      </div>
    </div>
  `;

  // Attach click handlers to observation timeline cards
  container.querySelectorAll('.timeline-item.obs-item').forEach(elem => {
    elem.addEventListener('click', () => {
      const obsId = elem.getAttribute('data-obs-id');
      if (obsId && onSelectObservation) onSelectObservation(obsId);
    });
  });
}

function renderEventCard(evt) {
  const isOngoing = evt.is_ongoing;
  const veiText = evt.vei_rating !== null ? `VEI ${evt.vei_rating}` : 'Effusive / N/A';

  return `
    <div class="timeline-item event-item ${isOngoing ? 'ongoing-event' : ''}">
      <div>
        <div style="font-weight: 600; color: #ffffff;">${escapeHtml(evt.title)}</div>
        <div style="font-size: 0.75rem; color: var(--text-secondary); font-family: var(--font-mono); margin-top: 2px;">
          ${evt.event_type} • ${formatDate(evt.start_time)} ➔ ${isOngoing ? '<span class="badge badge-ongoing">ACTIVE ONGOING</span>' : formatDate(evt.end_time)}
        </div>
      </div>
      <div>
        <span class="badge" style="background: rgba(255,255,255,0.08); color: var(--text-secondary);">${veiText}</span>
      </div>
    </div>
  `;
}

function renderObservationTimelineCard(obs) {
  const facets = obs.active_facets || [];
  const facetBadges = facets.map(f => `<span class="badge badge-facet">${f}</span>`).join(' ');

  return `
    <div class="timeline-item obs-item" data-obs-id="${obs.id}" style="cursor: pointer;">
      <div>
        <div style="font-weight: 600; color: var(--text-primary);">${escapeHtml(obs.summary)}</div>
        <div style="font-size: 0.75rem; color: var(--text-secondary); font-family: var(--font-mono); margin-top: 2px;">
          ${formatDate(obs.timestamp)} • Source Tag: ${obs.spatial_location ? obs.spatial_location.spatial_source : 'N/A'}
        </div>
      </div>
      <div style="display: flex; gap: 4px; align-items: center;">
        ${facetBadges}
      </div>
    </div>
  `;
}

function formatDate(isoStr) {
  if (!isoStr) return 'Present';
  return isoStr.split('T')[0];
}

function escapeHtml(str) {
  if (!str) return '';
  return String(str).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}
