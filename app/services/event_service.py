import sqlite3
from datetime import datetime
from typing import Dict, Any, List, Optional
from app.db.database import DatabaseManager, db_manager
from app.models.volcanic_event import VolcanicEvent, EventType
from app.models.observation_event_link import ObservationEventLink, RelationshipType
from app.repositories import (
    VolcanicEventRepository,
    ObservationRepository,
    ObservationEventLinkRepository,
    VolcanicSystemRepository,
)


class EventService:
    """Business service for volcanic events and observation-event relationship link management."""

    def __init__(self, db: Optional[DatabaseManager] = None):
        self.db = db if db is not None else db_manager
        self.ve_repo = VolcanicEventRepository(self.db)
        self.obs_repo = ObservationRepository(self.db)
        self.link_repo = ObservationEventLinkRepository(self.db)
        self.vs_repo = VolcanicSystemRepository(self.db)

    def calculate_temporal_offset_hours(self, obs_timestamp_str: str, event_start_str: str) -> Optional[float]:
        """Calculates difference in hours between observation timestamp and event start time."""
        try:
            obs_dt = datetime.fromisoformat(obs_timestamp_str.replace("Z", "+00:00"))
            evt_dt = datetime.fromisoformat(event_start_str.replace("Z", "+00:00"))
            diff_seconds = (obs_dt - evt_dt).total_seconds()
            return round(diff_seconds / 3600.0, 2)
        except Exception:
            return None

    def validate_and_create_event(self, payload: Dict[str, Any]) -> VolcanicEvent:
        """Validates payload and creates a new VolcanicEvent."""
        system_id = payload.get("volcanic_system_id")
        if not system_id or not self.vs_repo.get_by_id(system_id):
            raise ValueError(f"Referenced volcanic_system_id '{system_id}' does not exist")

        event = VolcanicEvent.from_dict(payload)
        return self.ve_repo.create(event)

    def link_observation_to_event(
        self,
        link_id: str,
        observation_id: str,
        event_id: str,
        relationship_type: RelationshipType,
        notes: Optional[str] = None,
    ) -> ObservationEventLink:
        """
        Associates an Observation with a VolcanicEvent.
        Calculates temporal_offset_hours automatically.
        Enforces uniqueness constraint.
        """
        observation = self.obs_repo.get_by_id(observation_id)
        if not observation:
            raise ValueError(f"Observation with ID '{observation_id}' not found")

        event = self.ve_repo.get_by_id(event_id)
        if not event:
            raise ValueError(f"VolcanicEvent with ID '{event_id}' not found")

        if isinstance(relationship_type, str):
            relationship_type = RelationshipType(relationship_type)

        offset_hours = self.calculate_temporal_offset_hours(observation.timestamp, event.start_time)

        link = ObservationEventLink(
            id=link_id,
            observation_id=observation_id,
            event_id=event_id,
            relationship_type=relationship_type,
            temporal_offset_hours=offset_hours,
            notes=notes,
        )

        try:
            return self.link_repo.create(link)
        except sqlite3.IntegrityError:
            raise ValueError(
                f"Relationship link between observation '{observation_id}' and event '{event_id}' already exists"
            )

    def get_event_links_for_observation(self, observation_id: str) -> List[Dict[str, Any]]:
        """Retrieves linked event context for an observation."""
        links = self.link_repo.get_links_for_observation(observation_id)
        res = []
        for link in links:
            event = self.ve_repo.get_by_id(link.event_id)
            res.append({
                "link_id": link.id,
                "relationship_type": link.relationship_type.value,
                "temporal_offset_hours": link.temporal_offset_hours,
                "notes": link.notes,
                "event_id": event.id if event else link.event_id,
                "event_title": event.title if event else "Unknown Event",
                "event_type": event.event_type.value if event else None,
                "event_start_time": event.start_time if event else None,
                "event_end_time": event.end_time if event else None,
                "is_ongoing": event.is_ongoing if event else False,
            })
        return res
