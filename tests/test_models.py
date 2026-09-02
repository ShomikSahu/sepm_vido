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
    validate_composite_metadata,
)


def test_celestial_body_creation_and_longitude_conventions():
    earth = CelestialBody(
        id="earth",
        name="Earth",
        body_type=CelestialBodyType.PLANET,
        mean_radius_km=6371.0,
        coordinate_system="WGS84",
        longitude_convention=LongitudeConvention.EAST_WEST_180,
    )
    assert earth.validate_latitude(37.75) is True
    assert earth.validate_latitude(95.0) is False
    assert earth.validate_longitude(14.99) is True
    assert earth.validate_longitude(210.0) is False

    mars = CelestialBody(
        id="mars",
        name="Mars",
        body_type=CelestialBodyType.PLANET,
        mean_radius_km=3389.5,
        coordinate_system="IAU_2000_MARS",
        longitude_convention=LongitudeConvention.POSITIVE_EAST_360,
    )
    assert mars.validate_latitude(18.65) is True
    assert mars.validate_longitude(226.2) is True
    assert mars.validate_longitude(-15.0) is False


def test_volcanic_system_coordinate_validation():
    earth = CelestialBody(
        id="earth",
        name="Earth",
        body_type=CelestialBodyType.PLANET,
        mean_radius_km=6371.0,
        coordinate_system="WGS84",
        longitude_convention=LongitudeConvention.EAST_WEST_180,
    )
    valid_system = VolcanicSystem(
        id="volc-etna",
        celestial_body_id="earth",
        name="Mount Etna",
        latitude=37.751,
        longitude=14.993,
        elevation_m=3357.0,
        region="Sicily",
        volcanic_type="Stratovolcano",
        status=SystemStatus.ACTIVE,
    )
    valid_system.validate_coordinates_against_body(earth)

    invalid_system = VolcanicSystem(
        id="volc-bad",
        celestial_body_id="earth",
        name="Bad Longitude Volcano",
        latitude=10.0,
        longitude=250.0,  # Invalid for Earth EAST_WEST_180
        elevation_m=100.0,
        region="Test",
        volcanic_type="Test",
        status=SystemStatus.ACTIVE,
    )
    with pytest.raises(ValueError, match="Longitude 250.0 is invalid"):
        invalid_system.validate_coordinates_against_body(earth)


def test_composite_metadata_validation():
    payload = {
        "active_facets": ["IMAGE", "THERMAL"],
        "image_metadata": {
            "spectral_band": "VISIBLE_RGB",
            "spatial_resolution_m": 10.0,
            "cloud_cover_percentage": 5.0,
            "file_format": "PNG",
            "image_dimensions": {"width": 1920, "height": 1080},
            "sun_elevation_angle_deg": 45.0,
        },
        "thermal_metadata": {
            "brightness_temperature_kelvin": 800.0,
            "ambient_temperature_kelvin": 290.0,
            "thermal_flux_mw": 150.0,
            "anomaly_flag": True,
            "sensor_wavelength_um": 10.8,
            "saturation_threshold_exceeded": False,
        },
    }
    validated = validate_composite_metadata(payload)
    assert "IMAGE" in validated["active_facets"]
    assert "THERMAL" in validated["active_facets"]
    assert validated["image_metadata"]["spectral_band"] == "VISIBLE_RGB"
    assert validated["thermal_metadata"]["brightness_temperature_kelvin"] == 800.0


def test_spatial_fallback_logic():
    volcano = VolcanicSystem(
        id="volc-kilauea",
        celestial_body_id="earth",
        name="Kilauea",
        latitude=19.421,
        longitude=-155.287,
        elevation_m=1247.0,
        region="Hawaii",
        volcanic_type="Shield Volcano",
        status=SystemStatus.ACTIVE,
    )

    # 1. Observation with explicit coordinates
    obs1 = Observation(
        id="obs-1",
        volcanic_system_id="volc-kilauea",
        source_id="src-1",
        timestamp="2020-01-01T00:00:00Z",
        latitude=19.430,
        longitude=-155.290,
        summary="Test obs",
    )
    loc1 = obs1.resolve_spatial_location(volcano)
    assert loc1["source"] == "OBSERVATION"
    assert loc1["latitude"] == 19.430

    # 2. Observation with NULL coordinates falling back to parent volcano
    obs2 = Observation(
        id="obs-2",
        volcanic_system_id="volc-kilauea",
        source_id="src-1",
        timestamp="2020-01-01T00:00:00Z",
        latitude=None,
        longitude=None,
        summary="Null coords obs",
    )
    loc2 = obs2.resolve_spatial_location(volcano)
    assert loc2["source"] == "VOLCANO_FALLBACK"
    assert loc2["latitude"] == 19.421
    assert loc2["longitude"] == -155.287

    # 3. Observation without volcano reference
    loc3 = obs2.resolve_spatial_location(None)
    assert loc3["source"] == "UNLOCATED"
    assert loc3["latitude"] is None


def test_ongoing_event_and_optional_vei():
    # Ongoing active event (end_time = None)
    ongoing_event = VolcanicEvent(
        id="evt-1",
        volcanic_system_id="volc-1",
        title="Active Eruption",
        event_type=EventType.ERUPTION,
        start_time="2021-09-29T15:30:00Z",
        end_time=None,
        vei_rating=1,
        description="Ongoing lava flow",
    )
    assert ongoing_event.is_ongoing is True

    # Non-terrestrial event without VEI
    planetary_event = VolcanicEvent(
        id="evt-2",
        volcanic_system_id="volc-loki",
        title="Io Thermal Flare",
        event_type=EventType.THERMAL_ANOMALY,
        start_time="2023-01-01T00:00:00Z",
        end_time=None,
        vei_rating=None,  # Optional VEI
        description="Loki Patera thermal flare",
    )
    assert planetary_event.vei_rating is None
    assert planetary_event.is_ongoing is True


def test_event_timestamp_validation():
    with pytest.raises(ValueError, match="cannot be later than end_time"):
        VolcanicEvent(
            id="evt-bad",
            volcanic_system_id="volc-1",
            title="Bad Timestamps",
            event_type=EventType.ERUPTION,
            start_time="2022-01-02T00:00:00Z",
            end_time="2022-01-01T00:00:00Z",  # Inverted timestamps
            vei_rating=2,
            description="Invalid event",
        )
