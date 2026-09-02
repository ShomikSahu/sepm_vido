from typing import Tuple, List, Optional
from app.models.celestial_body import CelestialBody, LongitudeConvention
from app.repositories.celestial_body_repository import CelestialBodyRepository
from app.db.database import DatabaseManager, db_manager


class CoordinateService:
    """Business service for validating coordinates against celestial body reference conventions."""

    def __init__(self, db: Optional[DatabaseManager] = None):
        self.db = db if db is not None else db_manager
        self.cb_repo = CelestialBodyRepository(self.db)

    def validate_latitude(self, latitude: float) -> Tuple[bool, Optional[str]]:
        """Validates universal spherical latitude bounds [-90°, +90°]."""
        if latitude is None:
            return False, "Latitude cannot be None"
        if not isinstance(latitude, (int, float)):
            return False, f"Latitude must be a number, got {type(latitude).__name__}"
        if not (-90.0 <= latitude <= 90.0):
            return False, f"Latitude {latitude} is out of valid bounds [-90.0, +90.0]"
        return True, None

    def validate_longitude(self, longitude: float, body: CelestialBody) -> Tuple[bool, Optional[str]]:
        """Validates longitude against the body's explicit LongitudeConvention."""
        if longitude is None:
            return False, "Longitude cannot be None"
        if not isinstance(longitude, (int, float)):
            return False, f"Longitude must be a number, got {type(longitude).__name__}"
        if not isinstance(body, CelestialBody):
            return False, "Target body must be a valid CelestialBody instance"

        if body.longitude_convention == LongitudeConvention.EAST_WEST_180:
            if not (-180.0 <= longitude <= 180.0):
                return False, (
                    f"Longitude {longitude} is out of bounds for body '{body.name}' "
                    f"using '{body.longitude_convention.value}' [-180.0, +180.0]"
                )
        elif body.longitude_convention == LongitudeConvention.POSITIVE_EAST_360:
            if not (0.0 <= longitude <= 360.0):
                return False, (
                    f"Longitude {longitude} is out of bounds for body '{body.name}' "
                    f"using '{body.longitude_convention.value}' [0.0, 360.0]"
                )
        else:
            return False, f"Unsupported longitude convention: {body.longitude_convention}"

        return True, None

    def validate_coordinate_pair(
        self, latitude: Optional[float], longitude: Optional[float], celestial_body_id: str
    ) -> Tuple[bool, List[str]]:
        """Validates a lat/long coordinate pair against a celestial body ID."""
        errors: List[str] = []
        if latitude is None and longitude is None:
            return True, []  # Nullable coordinate pair is valid (indicates unlocated or fallback)
        if (latitude is None) != (longitude is None):
            errors.append("Latitude and longitude must both be provided or both be NULL")
            return False, errors

        body = self.cb_repo.get_by_id(celestial_body_id)
        if not body:
            errors.append(f"Celestial body with ID '{celestial_body_id}' not found")
            return False, errors

        lat_ok, lat_err = self.validate_latitude(latitude)
        if not lat_ok:
            errors.append(lat_err)

        long_ok, long_err = self.validate_longitude(longitude, body)
        if not long_ok:
            errors.append(long_err)

        return len(errors) == 0, errors
