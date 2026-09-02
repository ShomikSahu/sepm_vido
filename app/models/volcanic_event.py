from enum import Enum
from dataclasses import dataclass
from typing import Dict, Any, Optional


class EventType(str, Enum):
    ERUPTION = "ERUPTION"
    ASH_PLUME = "ASH_PLUME"
    THERMAL_ANOMALY = "THERMAL_ANOMALY"
    LAVA_FLOW = "LAVA_FLOW"
    GAS_DEGASSING = "GAS_DEGASSING"


@dataclass
class VolcanicEvent:
    """Domain model representing a physical volcanic phenomenon occurring over time."""
    id: str
    volcanic_system_id: str
    title: str
    event_type: EventType
    start_time: str  # ISO-8601 string
    description: str
    end_time: Optional[str] = None  # NULL for active ongoing events
    vei_rating: Optional[int] = None  # Optional Volcanic Explosivity Index (0-8)

    def __post_init__(self):
        if not self.id or not isinstance(self.id, str):
            raise ValueError("VolcanicEvent id must be a non-empty string")
        if not self.volcanic_system_id:
            raise ValueError("volcanic_system_id must be non-empty")
        if not self.title:
            raise ValueError("title must be non-empty")
        if not self.start_time:
            raise ValueError("start_time must be non-empty")
        if isinstance(self.event_type, str):
            self.event_type = EventType(self.event_type)

        if self.vei_rating is not None:
            if not (0 <= self.vei_rating <= 8):
                raise ValueError(f"vei_rating {self.vei_rating} must be between 0 and 8")

        if self.end_time is not None:
            if self.start_time > self.end_time:
                raise ValueError(
                    f"Invalid event timestamps: start_time ({self.start_time}) cannot be later than end_time ({self.end_time})"
                )

    @property
    def is_ongoing(self) -> bool:
        """Returns True if the event is currently active/ongoing (end_time is NULL)."""
        return self.end_time is None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "volcanic_system_id": self.volcanic_system_id,
            "title": self.title,
            "event_type": self.event_type.value,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "vei_rating": self.vei_rating,
            "description": self.description,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "VolcanicEvent":
        return cls(
            id=data["id"],
            volcanic_system_id=data["volcanic_system_id"],
            title=data["title"],
            event_type=EventType(data["event_type"]),
            start_time=data["start_time"],
            end_time=data.get("end_time"),
            vei_rating=int(data["vei_rating"]) if data.get("vei_rating") is not None else None,
            description=data["description"],
        )
