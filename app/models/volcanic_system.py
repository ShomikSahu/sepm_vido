from enum import Enum
from dataclasses import dataclass
from typing import Dict, Any, Optional
from app.models.celestial_body import CelestialBody


class SystemStatus(str, Enum):
    ACTIVE = "ACTIVE"
    DORMANT = "DORMANT"
    EXTINCT = "EXTINCT"
    UNKNOWN = "UNKNOWN"


@dataclass
class VolcanicSystem:
    """Domain model representing a volcanic complex, vent, or caldera."""
    id: str
    celestial_body_id: str
    name: str
    latitude: float
    longitude: float
    elevation_m: float
    region: str
    volcanic_type: str
    status: SystemStatus

    def __post_init__(self):
        if not self.id or not isinstance(self.id, str):
            raise ValueError("VolcanicSystem id must be a non-empty string")
        if not self.celestial_body_id:
            raise ValueError("celestial_body_id must be non-empty")
        if not self.name:
            raise ValueError("VolcanicSystem name must be non-empty")
        if not (-90.0 <= self.latitude <= 90.0):
            raise ValueError(f"Latitude {self.latitude} is out of spherical bounds [-90, +90]")
        if isinstance(self.status, str):
            self.status = SystemStatus(self.status)

    def validate_coordinates_against_body(self, body: CelestialBody) -> None:
        """Validates this system's coordinates against a parent CelestialBody's convention."""
        if not body.validate_latitude(self.latitude):
            raise ValueError(f"Latitude {self.latitude} out of bounds for body {body.name}")
        if not body.validate_longitude(self.longitude):
            raise ValueError(
                f"Longitude {self.longitude} is invalid for celestial body '{body.name}' "
                f"using convention '{body.longitude_convention.value}'"
            )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "celestial_body_id": self.celestial_body_id,
            "name": self.name,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "elevation_m": self.elevation_m,
            "region": self.region,
            "volcanic_type": self.volcanic_type,
            "status": self.status.value,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "VolcanicSystem":
        return cls(
            id=data["id"],
            celestial_body_id=data["celestial_body_id"],
            name=data["name"],
            latitude=float(data["latitude"]),
            longitude=float(data["longitude"]),
            elevation_m=float(data["elevation_m"]),
            region=data["region"],
            volcanic_type=data["volcanic_type"],
            status=SystemStatus(data["status"]),
        )
