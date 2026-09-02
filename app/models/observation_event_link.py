from enum import Enum
from dataclasses import dataclass
from typing import Dict, Any, Optional


class RelationshipType(str, Enum):
    PRE_ERUPTIVE = "PRE_ERUPTIVE"
    CO_ERUPTIVE = "CO_ERUPTIVE"
    POST_ERUPTIVE = "POST_ERUPTIVE"
    UNRELATED = "UNRELATED"


@dataclass
class ObservationEventLink:
    """Domain model representing a contextual relationship between an Observation and a VolcanicEvent."""
    id: str
    observation_id: str
    event_id: str
    relationship_type: RelationshipType
    temporal_offset_hours: Optional[float] = None
    notes: Optional[str] = None

    def __post_init__(self):
        if not self.id or not isinstance(self.id, str):
            raise ValueError("ObservationEventLink id must be a non-empty string")
        if not self.observation_id:
            raise ValueError("observation_id must be non-empty")
        if not self.event_id:
            raise ValueError("event_id must be non-empty")
        if isinstance(self.relationship_type, str):
            self.relationship_type = RelationshipType(self.relationship_type)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "observation_id": self.observation_id,
            "event_id": self.event_id,
            "relationship_type": self.relationship_type.value,
            "temporal_offset_hours": self.temporal_offset_hours,
            "notes": self.notes,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ObservationEventLink":
        return cls(
            id=data["id"],
            observation_id=data["observation_id"],
            event_id=data["event_id"],
            relationship_type=RelationshipType(data["relationship_type"]),
            temporal_offset_hours=float(data["temporal_offset_hours"]) if data.get("temporal_offset_hours") is not None else None,
            notes=data.get("notes"),
        )
