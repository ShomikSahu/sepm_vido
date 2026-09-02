from enum import Enum
from dataclasses import dataclass
from typing import Dict, Any


class PlatformType(str, Enum):
    SATELLITE_ORBITER = "SATELLITE_ORBITER"
    GROUND_OBSERVATORY = "GROUND_OBSERVATORY"
    AIRBORNE_DRONE = "AIRBORNE_DRONE"
    FIELD_STATION = "FIELD_STATION"


@dataclass
class ObservationSource:
    """Domain model representing a physical sensor platform or agency."""
    id: str
    name: str
    platform_type: PlatformType
    operator_agency: str

    def __post_init__(self):
        if not self.id or not isinstance(self.id, str):
            raise ValueError("ObservationSource id must be a non-empty string")
        if not self.name:
            raise ValueError("ObservationSource name must be non-empty")
        if isinstance(self.platform_type, str):
            self.platform_type = PlatformType(self.platform_type)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "platform_type": self.platform_type.value,
            "operator_agency": self.operator_agency,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ObservationSource":
        return cls(
            id=data["id"],
            name=data["name"],
            platform_type=PlatformType(data["platform_type"]),
            operator_agency=data["operator_agency"],
        )
