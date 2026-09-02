"""
VIDO Pydantic Schemas Package
Defines request and response schemas for REST API communication.
"""

from app.schemas.celestial_body import CelestialBodyResponse
from app.schemas.volcanic_system import VolcanicSystemResponse, VolcanicSystemDetailResponse
from app.schemas.observation_source import ObservationSourceResponse
from app.schemas.observation import (
    ObservationCreateRequest,
    ObservationResponse,
    ObservationSearchQuery,
)
from app.schemas.volcanic_event import VolcanicEventCreateRequest, VolcanicEventResponse
from app.schemas.observation_event_link import (
    ObservationEventLinkCreateRequest,
    ObservationEventLinkResponse,
    ObservationEventLinkDetailResponse,
)
from app.schemas.spatial import SpatialLocationResponse, SystemSpatialObservationsResponse
from app.schemas.timeline import TimelineResponse
from app.schemas.common import ErrorResponse

__all__ = [
    "CelestialBodyResponse",
    "VolcanicSystemResponse",
    "VolcanicSystemDetailResponse",
    "ObservationSourceResponse",
    "ObservationCreateRequest",
    "ObservationResponse",
    "ObservationSearchQuery",
    "VolcanicEventCreateRequest",
    "VolcanicEventResponse",
    "ObservationEventLinkCreateRequest",
    "ObservationEventLinkResponse",
    "ObservationEventLinkDetailResponse",
    "SpatialLocationResponse",
    "SystemSpatialObservationsResponse",
    "TimelineResponse",
    "ErrorResponse",
]
