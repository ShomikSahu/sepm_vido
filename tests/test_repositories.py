import pytest
import sqlite3
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


def test_celestial_body_repository_crud(repositories):
    repo = repositories["celestial_body"]
    body = CelestialBody(
        id="mars",
        name="Mars",
        body_type=CelestialBodyType.PLANET,
        mean_radius_km=3389.5,
        coordinate_system="IAU_2000_MARS",
        longitude_convention=LongitudeConvention.POSITIVE_EAST_360,
    )
    repo.create(body)

    fetched = repo.get_by_id("mars")
    assert fetched is not None
    assert fetched.name == "Mars"
    assert fetched.longitude_convention == LongitudeConvention.POSITIVE_EAST_360

    all_bodies = repo.get_all()
    assert len(all_bodies) == 1

    assert repo.delete("mars") is True
    assert repo.get_by_id("mars") is None


def test_volcanic_system_repository_foreign_key_and_coords(repositories):
    cb_repo = repositories["celestial_body"]
    vs_repo = repositories["volcanic_system"]

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

    system = VolcanicSystem(
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
    vs_repo.create(system)

    fetched = vs_repo.get_by_id("volc-etna")
    assert fetched is not None
    assert fetched.name == "Mount Etna"
    assert fetched.status == SystemStatus.ACTIVE


def test_observation_repository_composite_facets_and_filtering(repositories):
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
            id="src-webcam",
            name="Etna WebCam",
            platform_type=PlatformType.GROUND_OBSERVATORY,
            operator_agency="INGV",
        )
    )

    obs = Observation(
        id="obs-etna-01",
        volcanic_system_id="volc-etna",
        source_id="src-webcam",
        timestamp="2020-12-14T02:00:00Z",
        latitude=37.751,
        longitude=14.993,
        summary="Thermal image of Etna eruption",
        metadata={
            "active_facets": ["IMAGE", "THERMAL"],
            "image_metadata": {
                "spectral_band": "VISIBLE_RGB",
                "spatial_resolution_m": 1.0,
                "cloud_cover_percentage": 0.0,
                "file_format": "PNG",
                "image_dimensions": {"width": 1920, "height": 1080},
                "sun_elevation_angle_deg": 0.0,
            },
            "thermal_metadata": {
                "brightness_temperature_kelvin": 900.0,
                "ambient_temperature_kelvin": 275.0,
                "thermal_flux_mw": 300.0,
                "anomaly_flag": True,
                "sensor_wavelength_um": 10.8,
                "saturation_threshold_exceeded": False,
            },
        },
    )
    obs_repo.create(obs)

    fetched = obs_repo.get_by_id("obs-etna-01")
    assert fetched is not None
    assert "IMAGE" in fetched.metadata["active_facets"]
    assert "THERMAL" in fetched.metadata["active_facets"]

    # Filter by facet
    thermal_obs = obs_repo.filter_by_facet("THERMAL")
    assert len(thermal_obs) == 1
    assert thermal_obs[0].id == "obs-etna-01"

    orbital_obs = obs_repo.filter_by_facet("PLANETARY_ORBITAL")
    assert len(orbital_obs) == 0


def test_volcanic_event_repository_ongoing(repositories):
    cb_repo = repositories["celestial_body"]
    vs_repo = repositories["volcanic_system"]
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

    evt1 = VolcanicEvent(
        id="evt-bounded",
        volcanic_system_id="volc-kilauea",
        title="2018 Eruption",
        event_type=EventType.ERUPTION,
        start_time="2018-05-03T00:00:00Z",
        end_time="2018-09-05T00:00:00Z",
        vei_rating=3,
        description="Major caldera collapse and lower East Rift Zone eruption.",
    )
    evt2 = VolcanicEvent(
        id="evt-ongoing",
        volcanic_system_id="volc-kilauea",
        title="Active Crater Lava Lake Episode",
        event_type=EventType.LAVA_FLOW,
        start_time="2021-09-29T15:30:00Z",
        end_time=None,  # Ongoing
        vei_rating=1,
        description="Ongoing eruption in Halema'uma'u crater.",
    )

    ve_repo.create(evt1)
    ve_repo.create(evt2)

    ongoing = ve_repo.get_ongoing_events()
    assert len(ongoing) == 1
    assert ongoing[0].id == "evt-ongoing"
    assert ongoing[0].is_ongoing is True


def test_observation_event_link_unique_constraint(repositories):
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
            id="obs-1",
            volcanic_system_id="volc-etna",
            source_id="src-1",
            timestamp="2020-12-14T00:00:00Z",
            summary="Obs 1",
        )
    )
    ve_repo.create(
        VolcanicEvent(
            id="evt-1",
            volcanic_system_id="volc-etna",
            title="Event 1",
            event_type=EventType.ERUPTION,
            start_time="2020-12-14T00:00:00Z",
            description="Event 1 desc",
        )
    )

    link1 = ObservationEventLink(
        id="link-1",
        observation_id="obs-1",
        event_id="evt-1",
        relationship_type=RelationshipType.CO_ERUPTIVE,
        temporal_offset_hours=0.0,
    )
    link_repo.create(link1)

    # Attempt duplicate link for same observation and event
    link2 = ObservationEventLink(
        id="link-2",
        observation_id="obs-1",
        event_id="evt-1",
        relationship_type=RelationshipType.PRE_ERUPTIVE,
        temporal_offset_hours=1.0,
    )
    with pytest.raises(sqlite3.IntegrityError):
        link_repo.create(link2)
