from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from app.models.volcanic_event import EventType, VolcanicEvent


class VolcanicEventCreateRequest(BaseModel):
    """API request model for creating a VolcanicEvent."""
    id: str = Field(..., description="Unique event identifier e.g. 'evt-etna-2020'")
    volcanic_system_id: str = Field(..., description="Target VolcanicSystem ID")
    title: str = Field(..., description="Event title")
    event_type: EventType = Field(..., description="Event type classification (ERUPTION, LAVA_FLOW, etc.)")
    start_time: str = Field(..., description="ISO-8601 start timestamp")
    description: str = Field(..., description="Detailed event description")
    end_time: Optional[str] = Field(default=None, description="Optional ISO-8601 end timestamp (NULL for ongoing active events)")
    vei_rating: Optional[int] = Field(default=None, description="Optional VEI rating (0-8)")


class VolcanicEventResponse(BaseModel):
    """API response model for VolcanicEvent entities."""
    model_config = ConfigDict(from_attributes=True)

    id: str = Field(..., description="Event ID")
    volcanic_system_id: str = Field(..., description="Target VolcanicSystem ID")
    title: str = Field(..., description="Event title")
    event_type: EventType = Field(..., description="Event type")
    start_time: str = Field(..., description="ISO-8601 start timestamp")
    end_time: Optional[str] = Field(default=None, description="ISO-8601 end timestamp (NULL if ongoing)")
    is_ongoing: bool = Field(..., description="True if end_time is NULL")
    vei_rating: Optional[int] = Field(default=None, description="Optional VEI rating (0-8 or None)")
    description: str = Field(..., description="Event description")

    @classmethod
    def from_domain(cls, event: VolcanicEvent) -> "VolcanicEventResponse":
        d = event.to_dict()
        d["is_ongoing"] = event.is_ongoing
        return cls.model_validate(d)
