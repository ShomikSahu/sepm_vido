from pydantic import BaseModel, Field, ConfigDict
from app.models.celestial_body import CelestialBodyType, LongitudeConvention, CelestialBody


class CelestialBodyResponse(BaseModel):
    """API response model for CelestialBody entities."""
    model_config = ConfigDict(from_attributes=True)

    id: str = Field(..., description="Unique identifier e.g. 'earth', 'mars'")
    name: str = Field(..., description="Celestial body name")
    body_type: CelestialBodyType = Field(..., description="Type (PLANET or MOON)")
    mean_radius_km: float = Field(..., description="Mean radius in kilometers")
    coordinate_system: str = Field(..., description="Target CRS e.g. 'WGS84', 'IAU_2000_MARS'")
    longitude_convention: LongitudeConvention = Field(..., description="Convention (EAST_WEST_180 or POSITIVE_EAST_360)")

    @classmethod
    def from_domain(cls, body: CelestialBody) -> "CelestialBodyResponse":
        return cls.model_validate(body.to_dict())
