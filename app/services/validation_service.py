from datetime import datetime
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from app.db.database import DatabaseManager, db_manager
from app.models import (
    Observation,
    ObservationFacetCategory,
    validate_composite_metadata,
)
from app.repositories import (
    CelestialBodyRepository,
    VolcanicSystemRepository,
    ObservationSourceRepository,
    ObservationRepository,
)
from app.services.coordinate_service import CoordinateService


@dataclass
class ValidationResult:
    """Result container for business validation engine operations."""
    is_valid: bool
    errors: List[str] = field(default_factory=list)
    validated_observation: Optional[Observation] = None


class ValidationService:
    """Business service for validating observation records and composite metadata payloads."""

    def __init__(self, db: Optional[DatabaseManager] = None):
        self.db = db if db is not None else db_manager
        self.cb_repo = CelestialBodyRepository(self.db)
        self.vs_repo = VolcanicSystemRepository(self.db)
        self.os_repo = ObservationSourceRepository(self.db)
        self.obs_repo = ObservationRepository(self.db)
        self.coord_service = CoordinateService(self.db)

    def validate_iso_timestamp(self, timestamp_str: str) -> Tuple[bool, Optional[str]]:
        """Validates that a string is a valid ISO-8601 UTC timestamp."""
        if not timestamp_str or not isinstance(timestamp_str, str):
            return False, "Timestamp must be a non-empty ISO-8601 string"
        try:
            # Handle standard ISO-8601 format e.g. 2020-12-14T10:30:00Z or +00:00
            clean_ts = timestamp_str.replace("Z", "+00:00")
            datetime.fromisoformat(clean_ts)
            return True, None
        except ValueError:
            return False, f"Timestamp '{timestamp_str}' is not a valid ISO-8601 datetime format"

    def validate_observation_payload(self, payload: Dict[str, Any]) -> ValidationResult:
        """Validates a raw observation dictionary payload before database insertion."""
        errors: List[str] = []

        if not isinstance(payload, dict):
            return ValidationResult(is_valid=False, errors=["Observation payload must be a dictionary"])

        # 1. Validate Core Attributes Presence
        obs_id = payload.get("id")
        system_id = payload.get("volcanic_system_id")
        source_id = payload.get("source_id")
        timestamp = payload.get("timestamp")
        summary = payload.get("summary")

        if not obs_id or not isinstance(obs_id, str):
            errors.append("Field 'id' is required and must be a non-empty string")
        if not system_id or not isinstance(system_id, str):
            errors.append("Field 'volcanic_system_id' is required and must be a non-empty string")
        if not source_id or not isinstance(source_id, str):
            errors.append("Field 'source_id' is required and must be a non-empty string")
        if not summary or not isinstance(summary, str):
            errors.append("Field 'summary' is required and must be a non-empty string")

        # 2. Validate Timestamp
        if timestamp:
            ts_ok, ts_err = self.validate_iso_timestamp(timestamp)
            if not ts_ok:
                errors.append(ts_err)
        else:
            errors.append("Field 'timestamp' is required")

        # 3. Validate Referential Relationships (VolcanicSystem & ObservationSource existence)
        system = None
        if system_id:
            system = self.vs_repo.get_by_id(system_id)
            if not system:
                errors.append(f"Referenced volcanic_system_id '{system_id}' does not exist")

        if source_id:
            source = self.os_repo.get_by_id(source_id)
            if not source:
                errors.append(f"Referenced source_id '{source_id}' does not exist")

        # 4. Validate Coordinates against parent CelestialBody if present
        lat = payload.get("latitude")
        long = payload.get("longitude")
        if (lat is not None) or (long is not None):
            if system:
                coords_ok, coord_errs = self.coord_service.validate_coordinate_pair(lat, long, system.celestial_body_id)
                if not coords_ok:
                    errors.extend(coord_errs)
            else:
                # Basic spherical latitude check if system wasn't found
                if lat is not None and not (-90.0 <= lat <= 90.0):
                    errors.append(f"Latitude {lat} out of valid bounds [-90, +90]")

        # 5. Validate Dynamic Composite Metadata Payload
        raw_metadata = payload.get("metadata")
        validated_metadata = {"active_facets": []}
        if raw_metadata is not None:
            try:
                validated_metadata = validate_composite_metadata(raw_metadata)
            except ValueError as e:
                errors.append(f"Metadata validation failure: {str(e)}")

        if errors:
            return ValidationResult(is_valid=False, errors=errors)

        # Construct validated Observation domain object
        try:
            obs = Observation(
                id=obs_id,
                volcanic_system_id=system_id,
                source_id=source_id,
                timestamp=timestamp,
                summary=summary,
                latitude=float(lat) if lat is not None else None,
                longitude=float(long) if long is not None else None,
                media_path=payload.get("media_path"),
                metadata=validated_metadata,
            )
            return ValidationResult(is_valid=True, errors=[], validated_observation=obs)
        except ValueError as e:
            return ValidationResult(is_valid=False, errors=[str(e)])

    def ingest_observation(self, payload: Dict[str, Any]) -> Observation:
        """Validates payload and persists the observation via repository if clean."""
        res = self.validate_observation_payload(payload)
        if not res.is_valid:
            raise ValueError(f"Observation ingestion rejected: {'; '.join(res.errors)}")
        return self.obs_repo.create(res.validated_observation)
