import json
from dataclasses import dataclass
from typing import Dict, Any, Optional
from app.models.volcanic_system import VolcanicSystem
from app.models.celestial_body import CelestialBody
from app.models.facets import validate_composite_metadata


@dataclass
class Observation:
    """Domain model representing a single scientific observation event."""
    id: str
    volcanic_system_id: str
    source_id: str
    timestamp: str  # ISO-8601 UTC string e.g. "2020-12-14T10:30:00Z"
    summary: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    media_path: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        if not self.id or not isinstance(self.id, str):
            raise ValueError("Observation id must be a non-empty string")
        if not self.volcanic_system_id:
            raise ValueError("volcanic_system_id must be non-empty")
        if not self.source_id:
            raise ValueError("source_id must be non-empty")
        if not self.timestamp:
            raise ValueError("timestamp must be non-empty")
        if self.latitude is not None:
            if not (-90.0 <= self.latitude <= 90.0):
                raise ValueError(f"Observation latitude {self.latitude} out of bounds [-90, +90]")
        
        # Ensure metadata is validated if provided
        if self.metadata is None:
            self.metadata = {"active_facets": []}
        else:
            self.metadata = validate_composite_metadata(self.metadata)

    def validate_coordinates_against_body(self, body: CelestialBody) -> None:
        """Validates observation-level coordinates against a target CelestialBody convention if present."""
        if self.latitude is not None and not body.validate_latitude(self.latitude):
            raise ValueError(f"Observation latitude {self.latitude} out of bounds for body {body.name}")
        if self.longitude is not None and not body.validate_longitude(self.longitude):
            raise ValueError(
                f"Observation longitude {self.longitude} is invalid for celestial body '{body.name}' "
                f"using convention '{body.longitude_convention.value}'"
            )

    def resolve_spatial_location(self, volcanic_system: Optional[VolcanicSystem] = None) -> Dict[str, Any]:
        """
        Applies approved spatial resolution fallback logic:
        1. Explicit observation coordinates (source = "OBSERVATION")
        2. Parent VolcanicSystem coordinates (source = "VOLCANO_FALLBACK")
        3. Neither available (source = "UNLOCATED")
        """
        if self.latitude is not None and self.longitude is not None:
            return {
                "latitude": self.latitude,
                "longitude": self.longitude,
                "source": "OBSERVATION",
            }
        elif volcanic_system is not None and volcanic_system.latitude is not None and volcanic_system.longitude is not None:
            return {
                "latitude": volcanic_system.latitude,
                "longitude": volcanic_system.longitude,
                "source": "VOLCANO_FALLBACK",
            }
        else:
            return {
                "latitude": None,
                "longitude": None,
                "source": "UNLOCATED",
            }

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "volcanic_system_id": self.volcanic_system_id,
            "source_id": self.source_id,
            "timestamp": self.timestamp,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "summary": self.summary,
            "media_path": self.media_path,
            "metadata": json.dumps(self.metadata),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Observation":
        raw_meta = data.get("metadata")
        if isinstance(raw_meta, str):
            meta_dict = json.loads(raw_meta)
        elif isinstance(raw_meta, dict):
            meta_dict = raw_meta
        else:
            meta_dict = {"active_facets": []}

        return cls(
            id=data["id"],
            volcanic_system_id=data["volcanic_system_id"],
            source_id=data["source_id"],
            timestamp=data["timestamp"],
            summary=data["summary"],
            latitude=float(data["latitude"]) if data.get("latitude") is not None else None,
            longitude=float(data["longitude"]) if data.get("longitude") is not None else None,
            media_path=data.get("media_path"),
            metadata=meta_dict,
        )
