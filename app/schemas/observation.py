import json
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Dict, Any, List
from app.models.observation import Observation


class ObservationCreateRequest(BaseModel):
    """API request model for ingesting a new scientific Observation."""
    id: str = Field(..., description="Unique observation ID e.g. 'obs-001'")
    volcanic_system_id: str = Field(..., description="Target VolcanicSystem ID")
    source_id: str = Field(..., description="ObservationSource platform ID")
    timestamp: str = Field(..., description="ISO-8601 UTC timestamp e.g. '2020-12-14T10:30:00Z'")
    summary: str = Field(..., description="Observation summary description")
    latitude: Optional[float] = Field(default=None, description="Optional latitude override")
    longitude: Optional[float] = Field(default=None, description="Optional longitude override")
    media_path: Optional[str] = Field(default=None, description="Optional file path to imagery or binary data")
    metadata: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Composite metadata payload with active facets ('active_facets': ['IMAGE', 'THERMAL', ...])",
    )


class ObservationResponse(BaseModel):
    """API response model for Observation entities."""
    model_config = ConfigDict(from_attributes=True)

    id: str = Field(..., description="Observation ID")
    volcanic_system_id: str = Field(..., description="Target VolcanicSystem ID")
    source_id: str = Field(..., description="ObservationSource ID")
    timestamp: str = Field(..., description="ISO-8601 UTC timestamp")
    summary: str = Field(..., description="Summary text")
    latitude: Optional[float] = Field(default=None, description="Latitude override (or None)")
    longitude: Optional[float] = Field(default=None, description="Longitude override (or None)")
    media_path: Optional[str] = Field(default=None, description="Media asset file path")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Parsed composite metadata object")

    @classmethod
    def from_domain(cls, obs: Observation) -> "ObservationResponse":
        meta = obs.metadata
        if isinstance(meta, str):
            try:
                meta = json.loads(meta)
            except Exception:
                meta = {}
        elif meta is None:
            meta = {}

        return cls(
            id=obs.id,
            volcanic_system_id=obs.volcanic_system_id,
            source_id=obs.source_id,
            timestamp=obs.timestamp,
            summary=obs.summary,
            latitude=obs.latitude,
            longitude=obs.longitude,
            media_path=obs.media_path,
            metadata=meta,
        )


class ObservationSearchQuery(BaseModel):
    """Query parameters model for filtering observation collections."""
    volcanic_system_id: Optional[str] = None
    celestial_body_id: Optional[str] = None
    source_id: Optional[str] = None
    facet: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
