from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any


class SpatialLocationResponse(BaseModel):
    """API response model for resolved spatial location data."""
    observation_id: str
    volcanic_system_id: str
    volcanic_system_name: Optional[str] = None
    celestial_body_id: Optional[str] = None
    celestial_body_name: Optional[str] = None
    coordinate_system: str
    longitude_convention: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    spatial_source: str = Field(..., description="OBSERVATION, VOLCANO_FALLBACK, or UNLOCATED")
    media_path: Optional[str] = None
    summary: str
    timestamp: str


class SystemSpatialObservationsResponse(BaseModel):
    """API response payload grouping located vs unlocated observations for a system or body."""
    located_observations: List[SpatialLocationResponse]
    unlocated_observations: List[SpatialLocationResponse]
