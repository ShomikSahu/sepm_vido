from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any


class TimelineResponse(BaseModel):
    """API response model for unified chronological timeline feeds."""
    volcanic_system_id: str
    volcanic_system_name: str
    celestial_body_id: Optional[str] = None
    celestial_body_name: Optional[str] = None
    timeline_reference_time: str
    events_count: int
    observations_count: int
    events_lane: List[Dict[str, Any]] = Field(..., description="Events sorted chronologically by start_time")
    observations_lane: List[Dict[str, Any]] = Field(..., description="Observations sorted chronologically by timestamp")
    combined_chronological_feed: List[Dict[str, Any]] = Field(..., description="Interleaved chronological feed")
