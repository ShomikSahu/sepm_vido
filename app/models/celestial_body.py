from enum import Enum
from dataclasses import dataclass
from typing import Dict, Any


class LongitudeConvention(str, Enum):
    """Supported coordinate reference conventions for celestial bodies."""
    EAST_WEST_180 = "EAST_WEST_180"       # Earth WGS84: -180.0° to +180.0°
    POSITIVE_EAST_360 = "POSITIVE_EAST_360" # Planetary IAU Standard: 0.0° to 360.0° Positive East


class CelestialBodyType(str, Enum):
    PLANET = "PLANET"
    MOON = "MOON"


@dataclass
class CelestialBody:
    """Domain model representing a celestial body (Planet or Moon)."""
    id: str
    name: str
    body_type: CelestialBodyType
    mean_radius_km: float
    coordinate_system: str
    longitude_convention: LongitudeConvention

    def __post_init__(self):
        if not self.id or not isinstance(self.id, str):
            raise ValueError("CelestialBody id must be a non-empty string")
        if not self.name:
            raise ValueError("CelestialBody name must be non-empty")
        if self.mean_radius_km <= 0:
            raise ValueError("mean_radius_km must be positive")
        if isinstance(self.body_type, str):
            self.body_type = CelestialBodyType(self.body_type)
        if isinstance(self.longitude_convention, str):
            self.longitude_convention = LongitudeConvention(self.longitude_convention)

    def validate_latitude(self, latitude: float) -> bool:
        """Validates that latitude is within the universal spherical bounds [-90°, +90°]."""
        if latitude is None:
            return False
        return -90.0 <= latitude <= 90.0

    def validate_longitude(self, longitude: float) -> bool:
        """Validates longitude against this body's explicit LongitudeConvention."""
        if longitude is None:
            return False
        if self.longitude_convention == LongitudeConvention.EAST_WEST_180:
            return -180.0 <= longitude <= 180.0
        elif self.longitude_convention == LongitudeConvention.POSITIVE_EAST_360:
            return 0.0 <= longitude <= 360.0
        return False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "body_type": self.body_type.value,
            "mean_radius_km": self.mean_radius_km,
            "coordinate_system": self.coordinate_system,
            "longitude_convention": self.longitude_convention.value,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CelestialBody":
        return cls(
            id=data["id"],
            name=data["name"],
            body_type=CelestialBodyType(data["body_type"]),
            mean_radius_km=float(data["mean_radius_km"]),
            coordinate_system=data["coordinate_system"],
            longitude_convention=LongitudeConvention(data["longitude_convention"]),
        )
