from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from app.models.observation_event_link import RelationshipType, ObservationEventLink


class ObservationEventLinkCreateRequest(BaseModel):
    """API request model for linking an Observation to a VolcanicEvent."""
    id: str = Field(..., description="Unique link identifier e.g. 'link-001'")
    observation_id: str = Field(..., description="Target Observation ID")
    event_id: str = Field(..., description="Target VolcanicEvent ID")
    relationship_type: RelationshipType = Field(..., description="PRE_ERUPTIVE, CO_ERUPTIVE, POST_ERUPTIVE, UNRELATED")
    notes: Optional[str] = Field(default=None, description="Optional association notes")


class ObservationEventLinkResponse(BaseModel):
    """API response model for ObservationEventLink entities."""
    model_config = ConfigDict(from_attributes=True)

    id: str = Field(..., description="Link ID")
    observation_id: str = Field(..., description="Observation ID")
    event_id: str = Field(..., description="VolcanicEvent ID")
    relationship_type: RelationshipType = Field(..., description="Relationship type")
    temporal_offset_hours: Optional[float] = Field(default=None, description="Calculated offset in hours")
    notes: Optional[str] = Field(default=None, description="Association notes")

    @classmethod
    def from_domain(cls, link: ObservationEventLink) -> "ObservationEventLinkResponse":
        return cls.model_validate(link.to_dict())


class ObservationEventLinkDetailResponse(BaseModel):
    """Detailed response model combining link metadata with event context."""
    link_id: str
    relationship_type: RelationshipType
    temporal_offset_hours: Optional[float] = None
    notes: Optional[str] = None
    event_id: str
    event_title: str
    event_type: Optional[str] = None
    event_start_time: Optional[str] = None
    event_end_time: Optional[str] = None
    is_ongoing: bool = False
