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
)
from app.services import (
    CoordinateService,
    ValidationService,
    SpatialService,
    EventService,
    TimelineService,
)


def test_coordinate_service_body_conventions(repositories):
    cb_repo = repositories["celestial_body"]
    cb_repo.create(
        CelestialBody(
            id="earth",
            name="Earth",
            body_type=CelestialBodyType.PLANET,
            mean_radius_km=6371.0,
            coordinate_system="WGS84",
            longitude_convention=LongitudeConvention.EAST_WEST_180,
        )
    )
    cb_repo.create(
        CelestialBody(
            id="mars",
            name="Mars",
            body_type=CelestialBodyType.PLANET,
            mean_radius_km=3389.5,
            coordinate_system="IAU_2000_MARS",
            longitude_convention=LongitudeConvention.POSITIVE_EAST_360,
        )
    )

    coord_service = CoordinateService(cb_repo.db)

    # Earth checks
    ok, errors = coord_service.validate_coordinate_pair(37.75, 14.99, "earth")
    assert ok is True
    assert len(errors) == 0

    ok_invalid_earth, errors = coord_service.validate_coordinate_pair(37.75, 210.0, "earth")
    assert ok_invalid_earth is False
    assert any("out of bounds for body 'Earth'" in e for e in errors)

    # Mars checks
    ok_mars, errors = coord_service.validate_coordinate_pair(18.65, 226.2, "mars")
    assert ok_mars is True

    ok_invalid_mars, errors = coord_service.validate_coordinate_pair(18.65, -15.0, "mars")
    assert ok_invalid_mars is False
    assert any("out of bounds for body 'Mars'" in e for e in errors)

    # Universal Latitude checks
    ok_lat, errors = coord_service.validate_coordinate_pair(120.0, 10.0, "earth")
    assert ok_lat is False
    assert any("Latitude 120.0 is out of valid bounds" in e for e in errors)


def test_validation_service_composite_facets(repositories):
    cb_repo = repositories["celestial_body"]
    vs_repo = repositories["volcanic_system"]
    os_repo = repositories["observation_source"]

    cb_repo.create(
        CelestialBody(
            id="mars",
            name="Mars",
            body_type=CelestialBodyType.PLANET,
            mean_radius_km=3389.5,
            coordinate_system="IAU_2000_MARS",
            longitude_convention=LongitudeConvention.POSITIVE_EAST_360,
        )
    )
    vs_repo.create(
        VolcanicSystem(
            id="volc-olympus",
            celestial_body_id="mars",
            name="Olympus Mons",
            latitude=18.65,
            longitude=226.2,
            elevation_m=21229.0,
            region="Tharsis",
            volcanic_type="Shield Volcano",
            status=SystemStatus.DORMANT,
        )
    )
    os_repo.create(
        ObservationSource(
            id="src-mro",
            name="MRO CTX",
            platform_type=PlatformType.SATELLITE_ORBITER,
            operator_agency="NASA",
        )
    )

    val_service = ValidationService(cb_repo.db)

    # Valid Multi-Facet Observation
    valid_payload = {
        "id": "obs-val-01",
        "volcanic_system_id": "volc-olympus",
        "source_id": "src-mro",
        "timestamp": "2021-05-20T14:45:00Z",
        "latitude": 18.65,
        "longitude": 226.2,
        "summary": "Multi-facet observation",
        "metadata": {
            "active_facets": ["IMAGE", "THERMAL", "PLANETARY_ORBITAL"],
            "image_metadata": {
                "spectral_band": "NEAR_INFRARED",
                "spatial_resolution_m": 6.0,
                "cloud_cover_percentage": 0.0,
                "file_format": "GeoTIFF",
                "image_dimensions": {"width": 4096, "height": 4096},
                "sun_elevation_angle_deg": 52.3,
            },
            "thermal_metadata": {
                "brightness_temperature_kelvin": 210.0,
                "ambient_temperature_kelvin": 200.0,
                "thermal_flux_mw": 5.0,
                "anomaly_flag": False,
                "sensor_wavelength_um": 12.0,
                "saturation_threshold_exceeded": False,
            },
            "orbital_metadata": {
                "spacecraft_altitude_km": 310.5,
                "solar_incidence_angle_deg": 48.2,
                "emission_angle_deg": 5.1,
                "phase_angle_deg": 53.3,
                "target_planetary_datum": "IAU_MARS_2000",
            },
        },
    }

    res = val_service.validate_observation_payload(valid_payload)
    assert res.is_valid is True
    assert res.validated_observation is not None
    assert len(res.validated_observation.metadata["active_facets"]) == 3

    # Invalid Payload: Negative Kelvin Temperature
    invalid_thermal = dict(valid_payload)
    invalid_thermal["id"] = "obs-val-02"
    invalid_thermal["metadata"] = {
        "active_facets": ["THERMAL"],
        "thermal_metadata": {
            "brightness_temperature_kelvin": -50.0,  # Invalid
            "ambient_temperature_kelvin": 200.0,
            "thermal_flux_mw": 5.0,
            "anomaly_flag": False,
            "sensor_wavelength_um": 12.0,
            "saturation_threshold_exceeded": False,
        },
    }
    res_invalid = val_service.validate_observation_payload(invalid_thermal)
    assert res_invalid.is_valid is False
    assert any("brightness_temperature_kelvin must be positive" in e for e in res_invalid.errors)

    # Invalid Payload: Missing required facet fields
    missing_fields = dict(valid_payload)
    missing_fields["id"] = "obs-val-03"
    missing_fields["metadata"] = {
        "active_facets": ["IMAGE"],
        "image_metadata": {
            "spectral_band": "VISIBLE",
            # Missing spatial_resolution_m, cloud_cover_percentage, etc.
        },
    }
    res_missing = val_service.validate_observation_payload(missing_fields)
    assert res_missing.is_valid is False
    assert any("Metadata validation failure" in e for e in res_missing.errors)


def test_spatial_service_fallback_and_queries(repositories):
    cb_repo = repositories["celestial_body"]
    vs_repo = repositories["volcanic_system"]
    os_repo = repositories["observation_source"]
    obs_repo = repositories["observation"]

    cb_repo.create(
        CelestialBody(
            id="earth",
            name="Earth",
            body_type=CelestialBodyType.PLANET,
            mean_radius_km=6371.0,
            coordinate_system="WGS84",
            longitude_convention=LongitudeConvention.EAST_WEST_180,
        )
    )
    vs_repo.create(
        VolcanicSystem(
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
    )
    os_repo.create(
        ObservationSource(
            id="src-1",
            name="Webcam",
            platform_type=PlatformType.GROUND_OBSERVATORY,
            operator_agency="INGV",
        )
    )

    # Obs 1: Explicit coordinates
    obs_repo.create(
        Observation(
            id="obs-explicit",
            volcanic_system_id="volc-etna",
            source_id="src-1",
            timestamp="2020-12-14T00:00:00Z",
            latitude=37.760,
            longitude=14.990,
            summary="Explicit coords",
        )
    )
    # Obs 2: NULL coordinates (volcano fallback)
    obs_repo.create(
        Observation(
            id="obs-fallback",
            volcanic_system_id="volc-etna",
            source_id="src-1",
            timestamp="2020-12-14T01:00:00Z",
            latitude=None,
            longitude=None,
            summary="Fallback coords",
        )
    )

    spatial_service = SpatialService(cb_repo.db)
    result = spatial_service.get_spatial_observations_for_system("volc-etna")

    located = result["located_observations"]
    assert len(located) == 2

    obs_exp = next(o for o in located if o["observation_id"] == "obs-explicit")
    assert obs_exp["spatial_source"] == "OBSERVATION"
    assert obs_exp["latitude"] == 37.760

    obs_fall = next(o for o in located if o["observation_id"] == "obs-fallback")
    assert obs_fall["spatial_source"] == "VOLCANO_FALLBACK"
    assert obs_fall["latitude"] == 37.751  # Volcano latitude


def test_timeline_service_ongoing_and_bounded_events(repositories):
    cb_repo = repositories["celestial_body"]
    vs_repo = repositories["volcanic_system"]
    os_repo = repositories["observation_source"]
    obs_repo = repositories["observation"]
    ve_repo = repositories["volcanic_event"]
    link_repo = repositories["observation_event_link"]

    cb_repo.create(
        CelestialBody(
            id="earth",
            name="Earth",
            body_type=CelestialBodyType.PLANET,
            mean_radius_km=6371.0,
            coordinate_system="WGS84",
            longitude_convention=LongitudeConvention.EAST_WEST_180,
        )
    )
    vs_repo.create(
        VolcanicSystem(
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
    )
    os_repo.create(
        ObservationSource(
            id="src-1",
            name="Webcam",
            platform_type=PlatformType.GROUND_OBSERVATORY,
            operator_agency="USGS",
        )
    )

    # Bounded Event
    ve_repo.create(
        VolcanicEvent(
            id="evt-bounded",
            volcanic_system_id="volc-kilauea",
            title="2018 Eruption",
            event_type=EventType.ERUPTION,
            start_time="2018-05-03T00:00:00Z",
            end_time="2018-09-05T00:00:00Z",
            vei_rating=3,
            description="Bounded event",
        )
    )

    # Ongoing Event (end_time = NULL)
    ve_repo.create(
        VolcanicEvent(
            id="evt-ongoing",
            volcanic_system_id="volc-kilauea",
            title="Active Summit Lava Lake",
            event_type=EventType.LAVA_FLOW,
            start_time="2021-09-29T15:30:00Z",
            end_time=None,
            vei_rating=1,
            description="Ongoing event",
        )
    )

    obs_repo.create(
        Observation(
            id="obs-kilauea-1",
            volcanic_system_id="volc-kilauea",
            source_id="src-1",
            timestamp="2021-10-01T12:00:00Z",
            summary="Lava lake image",
        )
    )

    link_repo.create(
        ObservationEventLink(
            id="link-k1",
            observation_id="obs-kilauea-1",
            event_id="evt-ongoing",
            relationship_type=RelationshipType.CO_ERUPTIVE,
            temporal_offset_hours=44.5,
        )
    )

    timeline_service = TimelineService(cb_repo.db)
    override_time = "2026-09-01T21:30:00Z"
    timeline = timeline_service.get_timeline_for_system("volc-kilauea", current_time_override=override_time)

    assert timeline["events_count"] == 2
    assert timeline["observations_count"] == 1

    events_lane = timeline["events_lane"]
    bounded = next(e for e in events_lane if e["id"] == "evt-bounded")
    assert bounded["is_ongoing"] is False
    assert bounded["display_end_time"] == "2018-09-05T00:00:00Z"

    ongoing = next(e for e in events_lane if e["id"] == "evt-ongoing")
    assert ongoing["is_ongoing"] is True
    assert ongoing["end_time"] is None  # Underlying domain value remains NULL
    assert ongoing["display_end_time"] == override_time  # Open-ended span ends at timeline reference time

    # Check combined feed chronological order
    feed = timeline["combined_chronological_feed"]
    timestamps = [item["sort_timestamp"] for item in feed]
    assert timestamps == sorted(timestamps)


def test_event_service_linking_and_validation(repositories):
    cb_repo = repositories["celestial_body"]
    vs_repo = repositories["volcanic_system"]
    os_repo = repositories["observation_source"]
    obs_repo = repositories["observation"]
    ve_repo = repositories["volcanic_event"]

    cb_repo.create(
        CelestialBody(
            id="earth",
            name="Earth",
            body_type=CelestialBodyType.PLANET,
            mean_radius_km=6371.0,
            coordinate_system="WGS84",
            longitude_convention=LongitudeConvention.EAST_WEST_180,
        )
    )
    vs_repo.create(
        VolcanicSystem(
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
    )
    os_repo.create(
        ObservationSource(
            id="src-1",
            name="Webcam",
            platform_type=PlatformType.GROUND_OBSERVATORY,
            operator_agency="INGV",
        )
    )
    obs_repo.create(
        Observation(
            id="obs-etna-10",
            volcanic_system_id="volc-etna",
            source_id="src-1",
            timestamp="2020-12-14T02:00:00Z",
            summary="Paroxysm image",
        )
    )
    ve_repo.create(
        VolcanicEvent(
            id="evt-etna-10",
            volcanic_system_id="volc-etna",
            title="Paroxysm",
            event_type=EventType.ERUPTION,
            start_time="2020-12-13T21:00:00Z",
            end_time="2020-12-14T12:00:00Z",
            vei_rating=2,
            description="Paroxysm",
        )
    )

    event_service = EventService(cb_repo.db)
    link = event_service.link_observation_to_event(
        link_id="link-e10",
        observation_id="obs-etna-10",
        event_id="evt-etna-10",
        relationship_type=RelationshipType.CO_ERUPTIVE,
        notes="Co-eruptive observation during peak lava fountain",
    )

    assert link.relationship_type == RelationshipType.CO_ERUPTIVE
    assert link.temporal_offset_hours == 5.0  # 2020-12-14 02:00 vs 2020-12-13 21:00 is 5 hours

    # Attempt link to non-existent event
    with pytest.raises(ValueError, match="VolcanicEvent with ID 'evt-nonexistent' not found"):
        event_service.link_observation_to_event(
            link_id="link-bad",
            observation_id="obs-etna-10",
            event_id="evt-nonexistent",
            relationship_type=RelationshipType.CO_ERUPTIVE,
        )
