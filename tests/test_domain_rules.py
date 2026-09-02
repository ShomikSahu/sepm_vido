import pytest
from app.models import (
    CelestialBody,
    CelestialBodyType,
    LongitudeConvention,
    VolcanicSystem,
    SystemStatus,
    ObservationSource,
    PlatformType,
    Observation,
    VolcanicEvent,
    EventType,
    ObservationEventLink,
    RelationshipType,
    ObservationFacetCategory,
    validate_composite_metadata,
)


def test_no_event_record_observation_type():
    """Rule Check: Verify EVENT_RECORD is not present in ObservationFacetCategory enums."""
    facet_values = [f.value for f in ObservationFacetCategory]
    assert "EVENT_RECORD" not in facet_values
    assert "ORBITAL_RADAR" not in facet_values
    assert set(facet_values) == {"IMAGE", "THERMAL", "PLANETARY_ORBITAL"}


def test_non_mutually_exclusive_composite_facets():
    """Rule Check: One observation can legitimately contain multiple metadata facets."""
    composite_payload = {
        "active_facets": ["IMAGE", "THERMAL", "PLANETARY_ORBITAL"],
        "image_metadata": {
            "spectral_band": "NEAR_INFRARED",
            "spatial_resolution_m": 5.0,
            "cloud_cover_percentage": 0.0,
            "file_format": "GeoTIFF",
            "image_dimensions": {"width": 2048, "height": 2048},
            "sun_elevation_angle_deg": 60.0,
        },
        "thermal_metadata": {
            "brightness_temperature_kelvin": 350.0,
            "ambient_temperature_kelvin": 210.0,
            "thermal_flux_mw": 50.0,
            "anomaly_flag": True,
            "sensor_wavelength_um": 10.0,
            "saturation_threshold_exceeded": False,
        },
        "orbital_metadata": {
            "spacecraft_altitude_km": 300.0,
            "solar_incidence_angle_deg": 40.0,
            "emission_angle_deg": 10.0,
            "phase_angle_deg": 50.0,
            "target_planetary_datum": "IAU_MARS_2000",
        },
    }
    validated = validate_composite_metadata(composite_payload)
    assert len(validated["active_facets"]) == 3
    assert "image_metadata" in validated
    assert "thermal_metadata" in validated
    assert "orbital_metadata" in validated


def test_earth_vs_planetary_longitude_conventions():
    """Rule Check: Explicit coordinate frame models support Earth -180..+180 and Planetary 0..360."""
    earth = CelestialBody(
        id="earth",
        name="Earth",
        body_type=CelestialBodyType.PLANET,
        mean_radius_km=6371.0,
        coordinate_system="WGS84",
        longitude_convention=LongitudeConvention.EAST_WEST_180,
    )
    io = CelestialBody(
        id="io",
        name="Io",
        body_type=CelestialBodyType.MOON,
        mean_radius_km=1821.6,
        coordinate_system="IAU_2000_IO",
        longitude_convention=LongitudeConvention.POSITIVE_EAST_360,
    )

    # Earth longitude 14.993 is valid; 309.5 is invalid for Earth
    assert earth.validate_longitude(14.993) is True
    assert earth.validate_longitude(309.5) is False

    # Io longitude 309.5 is valid; -155.0 is invalid for 0..360 Positive East convention
    assert io.validate_longitude(309.5) is True
    assert io.validate_longitude(-155.0) is False


def test_optional_vei_for_planetary_events():
    """Rule Check: VEI rating must be optional and NULL for planetary or effusive events."""
    loki_event = VolcanicEvent(
        id="evt-loki-01",
        volcanic_system_id="volc-loki",
        title="Loki Overturning",
        event_type=EventType.THERMAL_ANOMALY,
        start_time="2023-01-01T00:00:00Z",
        end_time=None,  # Ongoing active event
        vei_rating=None,  # Optional VEI rating
        description="Loki Patera thermal flare",
    )
    assert loki_event.vei_rating is None
    assert loki_event.is_ongoing is True


def test_observation_event_linking_with_unrelated():
    """Rule Check: Observation connects to VolcanicEvent via ObservationEventLink with UNRELATED type."""
    link = ObservationEventLink(
        id="link-test",
        observation_id="obs-01",
        event_id="evt-01",
        relationship_type=RelationshipType.UNRELATED,
        temporal_offset_hours=None,
        notes="Unrelated baseline observation",
    )
    assert link.relationship_type == RelationshipType.UNRELATED
    assert link.relationship_type.value == "UNRELATED"
