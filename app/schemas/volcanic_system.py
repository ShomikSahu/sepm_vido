from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from app.models.volcanic_system import SystemStatus, VolcanicSystem
from app.schemas.celestial_body import CelestialBodyResponse


class VolcanicSystemResponse(BaseModel):
    """API response model for VolcanicSystem entities."""
    model_config = ConfigDict(from_attributes=True)

    id: str = Field(..., description="Unique volcanic system identifier e.g. 'volc-etna'")
    celestial_body_id: str = Field(..., description="ID of parent celestial body")
    name: str = Field(..., description="Volcanic system name")
    latitude: float = Field(..., description="Latitude coordinate")
    longitude: float = Field(..., description="Longitude coordinate")
    elevation_m: float = Field(..., description="Elevation in meters")
    region: str = Field(..., description="Geographical or planetary region")
    volcanic_type: str = Field(..., description="Volcano classification e.g. Stratovolcano, Shield")
    status: SystemStatus = Field(..., description="Activity status (ACTIVE, DORMANT, EXTINCT, UNKNOWN)")

    @classmethod
    def from_domain(cls, system: VolcanicSystem) -> "VolcanicSystemResponse":
        return cls.model_validate(system.to_dict())


class VolcanicSystemDetailResponse(VolcanicSystemResponse):
    """Detailed response model including parent celestial body reference."""
    celestial_body: Optional[CelestialBodyResponse] = None
