from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from app.db.database import DatabaseManager, db_manager
from app.models.volcanic_system import VolcanicSystem
from app.repositories import (
    VolcanicSystemRepository,
    VolcanicEventRepository,
    ObservationRepository,
    ObservationEventLinkRepository,
    CelestialBodyRepository,
)
from app.services.spatial_service import SpatialService


class TimelineService:
    """Business service for aggregating chronological timeline views of volcanic systems."""

    def __init__(self, db: Optional[DatabaseManager] = None):
        self.db = db if db is not None else db_manager
        self.vs_repo = VolcanicSystemRepository(self.db)
        self.ve_repo = VolcanicEventRepository(self.db)
        self.obs_repo = ObservationRepository(self.db)
        self.link_repo = ObservationEventLinkRepository(self.db)
        self.cb_repo = CelestialBodyRepository(self.db)
        self.spatial_service = SpatialService(self.db)

    def get_timeline_for_system(
        self, system_id: str, current_time_override: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Produces a chronological timeline payload for a volcanic system.
        Merges bounded and ongoing volcanic events with observations and association links.
        """
        system = self.vs_repo.get_by_id(system_id)
        if not system:
            raise ValueError(f"VolcanicSystem with ID '{system_id}' not found")

        body = self.cb_repo.get_by_id(system.celestial_body_id)
        events = self.ve_repo.get_by_system(system_id)
        observations = self.obs_repo.get_by_system(system_id)

        # Default open-ended timestamp for ongoing events (ISO-8601 UTC)
        if current_time_override:
            present_timestamp = current_time_override
        else:
            present_timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

        # 1. Format Events Lane
        formatted_events: List[Dict[str, Any]] = []
        for evt in events:
            # Render ongoing event with display_end_time = present_timestamp while preserving NULL in domain
            display_end = evt.end_time if evt.end_time is not None else present_timestamp

            formatted_events.append({
                "item_type": "EVENT",
                "id": evt.id,
                "title": evt.title,
                "event_type": evt.event_type.value,
                "start_time": evt.start_time,
                "end_time": evt.end_time,  # Domain value (None if ongoing)
                "display_end_time": display_end,  # Open-ended timeline span boundary
                "is_ongoing": evt.is_ongoing,
                "vei_rating": evt.vei_rating,
                "description": evt.description,
            })

        # Sort events chronologically by start_time
        formatted_events.sort(key=lambda e: e["start_time"])

        # 2. Format Observations Lane
        formatted_observations: List[Dict[str, Any]] = []
        for obs in observations:
            links = self.link_repo.get_links_for_observation(obs.id)
            linked_event_ids = [l.event_id for l in links]
            spatial_info = self.spatial_service.resolve_observation_spatial_location(obs, system)

            formatted_observations.append({
                "item_type": "OBSERVATION",
                "id": obs.id,
                "timestamp": obs.timestamp,
                "summary": obs.summary,
                "media_path": obs.media_path,
                "active_facets": obs.metadata.get("active_facets", []) if obs.metadata else [],
                "spatial_location": spatial_info,
                "linked_event_ids": linked_event_ids,
                "relationship_count": len(links),
            })

        # Sort observations chronologically by timestamp
        formatted_observations.sort(key=lambda o: o["timestamp"])

        # 3. Interleaved Chronological Sequence (Combined Feed)
        combined_feed: List[Dict[str, Any]] = []
        for evt in formatted_events:
            item = dict(evt)
            item["sort_timestamp"] = evt["start_time"]
            combined_feed.append(item)

        for obs in formatted_observations:
            item = dict(obs)
            item["sort_timestamp"] = obs["timestamp"]
            combined_feed.append(item)

        combined_feed.sort(key=lambda item: item["sort_timestamp"])

        return {
            "volcanic_system_id": system.id,
            "volcanic_system_name": system.name,
            "celestial_body_id": body.id if body else None,
            "celestial_body_name": body.name if body else None,
            "timeline_reference_time": present_timestamp,
            "events_count": len(formatted_events),
            "observations_count": len(formatted_observations),
            "events_lane": formatted_events,
            "observations_lane": formatted_observations,
            "combined_chronological_feed": combined_feed,
        }
