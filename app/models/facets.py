from enum import Enum
from dataclasses import dataclass, asdict
from typing import Dict, Any, Optional, List


class ObservationFacetCategory(str, Enum):
    """Canonical observation metadata facet categories."""
    IMAGE = "IMAGE"
    THERMAL = "THERMAL"
    PLANETARY_ORBITAL = "PLANETARY_ORBITAL"


@dataclass
class ImageFacet:
    """Metadata facet payload for visual/multispectral imagery."""
    spectral_band: str
    spatial_resolution_m: float
    cloud_cover_percentage: float
    file_format: str
    image_dimensions: Dict[str, int]
    sun_elevation_angle_deg: float

    def __post_init__(self):
        if self.spatial_resolution_m <= 0:
            raise ValueError("spatial_resolution_m must be greater than 0")
        if not (0.0 <= self.cloud_cover_percentage <= 100.0):
            raise ValueError("cloud_cover_percentage must be between 0.0 and 100.0")

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ThermalFacet:
    """Metadata facet payload for thermal radiometry and heat flux."""
    brightness_temperature_kelvin: float
    ambient_temperature_kelvin: float
    thermal_flux_mw: float
    anomaly_flag: bool
    sensor_wavelength_um: float
    saturation_threshold_exceeded: bool

    def __post_init__(self):
        if self.brightness_temperature_kelvin <= 0:
            raise ValueError("brightness_temperature_kelvin must be positive (Kelvin)")
        if self.ambient_temperature_kelvin <= 0:
            raise ValueError("ambient_temperature_kelvin must be positive (Kelvin)")
        if self.sensor_wavelength_um <= 0:
            raise ValueError("sensor_wavelength_um must be positive")

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class OrbitalFacet:
    """Metadata facet payload for planetary spacecraft orbital geometry."""
    spacecraft_altitude_km: float
    solar_incidence_angle_deg: float
    emission_angle_deg: float
    phase_angle_deg: float
    target_planetary_datum: str

    def __post_init__(self):
        if self.spacecraft_altitude_km <= 0:
            raise ValueError("spacecraft_altitude_km must be positive")
        if not (0.0 <= self.solar_incidence_angle_deg <= 180.0):
            raise ValueError("solar_incidence_angle_deg must be between 0 and 180 degrees")
        if not (0.0 <= self.emission_angle_deg <= 180.0):
            raise ValueError("emission_angle_deg must be between 0 and 180 degrees")
        if not (0.0 <= self.phase_angle_deg <= 180.0):
            raise ValueError("phase_angle_deg must be between 0 and 180 degrees")

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def validate_composite_metadata(metadata: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validates a composite metadata dictionary containing active facets.
    Structure:
    {
        "active_facets": ["IMAGE", "THERMAL", ...],
        "image_metadata": {...},
        "thermal_metadata": {...},
        "orbital_metadata": {...}
    }
    """
    if not isinstance(metadata, dict):
        raise ValueError("Metadata payload must be a dictionary")

    active_facets = metadata.get("active_facets", [])
    if not isinstance(active_facets, list):
        raise ValueError("active_facets must be a list of facet category strings")

    validated_payload: Dict[str, Any] = {"active_facets": []}

    for facet_str in active_facets:
        try:
            category = ObservationFacetCategory(facet_str)
        except ValueError:
            raise ValueError(f"Invalid observation facet category: '{facet_str}'")

        if category.value not in validated_payload["active_facets"]:
            validated_payload["active_facets"].append(category.value)

    # Validate image_metadata if active
    if ObservationFacetCategory.IMAGE.value in validated_payload["active_facets"]:
        img_data = metadata.get("image_metadata")
        if not isinstance(img_data, dict):
            raise ValueError("Missing or invalid 'image_metadata' for active IMAGE facet")
        try:
            facet = ImageFacet(**img_data)
            validated_payload["image_metadata"] = facet.to_dict()
        except (TypeError, ValueError) as e:
            raise ValueError(f"Invalid 'image_metadata' facet payload: {str(e)}")

    # Validate thermal_metadata if active
    if ObservationFacetCategory.THERMAL.value in validated_payload["active_facets"]:
        thm_data = metadata.get("thermal_metadata")
        if not isinstance(thm_data, dict):
            raise ValueError("Missing or invalid 'thermal_metadata' for active THERMAL facet")
        try:
            facet = ThermalFacet(**thm_data)
            validated_payload["thermal_metadata"] = facet.to_dict()
        except (TypeError, ValueError) as e:
            raise ValueError(f"Invalid 'thermal_metadata' facet payload: {str(e)}")

    # Validate orbital_metadata if active
    if ObservationFacetCategory.PLANETARY_ORBITAL.value in validated_payload["active_facets"]:
        orb_data = metadata.get("orbital_metadata")
        if not isinstance(orb_data, dict):
            raise ValueError("Missing or invalid 'orbital_metadata' for active PLANETARY_ORBITAL facet")
        try:
            facet = OrbitalFacet(**orb_data)
            validated_payload["orbital_metadata"] = facet.to_dict()
        except (TypeError, ValueError) as e:
            raise ValueError(f"Invalid 'orbital_metadata' facet payload: {str(e)}")

    return validated_payload
