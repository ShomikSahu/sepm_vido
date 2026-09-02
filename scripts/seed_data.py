"""
Seed Dataset Script for Volcanic Image/Data Observatory (VIDO)
Populates the SQLite database with a curated multi-body scientific dataset (Earth, Mars, Io, Venus).
"""

import sys
from pathlib import Path

# Add project root to Python path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.db.database import DatabaseManager, db_manager
from app.db.schema import init_db
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
from app.repositories import (
    CelestialBodyRepository,
    VolcanicSystemRepository,
    ObservationSourceRepository,
    ObservationRepository,
    VolcanicEventRepository,
    ObservationEventLinkRepository,
)


def seed_database(db: DatabaseManager = None) -> None:
    """Populates the target database with curated Earth and planetary seed data."""
    if db is None:
        db = db_manager

    # 1. Initialize Database Schema
    with db.get_connection() as conn:
        init_db(conn)

    cb_repo = CelestialBodyRepository(db)
    vs_repo = VolcanicSystemRepository(db)
    os_repo = ObservationSourceRepository(db)
    obs_repo = ObservationRepository(db)
    ve_repo = VolcanicEventRepository(db)
    link_repo = ObservationEventLinkRepository(db)

    # 2. Celestial Bodies
    earth = CelestialBody(
        id="earth",
        name="Earth",
        body_type=CelestialBodyType.PLANET,
        mean_radius_km=6371.0,
        coordinate_system="WGS84",
        longitude_convention=LongitudeConvention.EAST_WEST_180,
    )
    mars = CelestialBody(
        id="mars",
        name="Mars",
        body_type=CelestialBodyType.PLANET,
        mean_radius_km=3389.5,
        coordinate_system="IAU_2000_MARS",
        longitude_convention=LongitudeConvention.POSITIVE_EAST_360,
    )
    io = CelestialBody(
        id="io",
        name="Io",
        body_type=CelestialBodyType.MOON,
        mean_radius_km=1821.6,
        coordinate_system="IAU_2000_IO",
        longitude_convention=LongitudeConvention.POSITIVE_EAST_360,
    )
    venus = CelestialBody(
        id="venus",
        name="Venus",
        body_type=CelestialBodyType.PLANET,
        mean_radius_km=6051.8,
        coordinate_system="IAU_2000_VENUS",
        longitude_convention=LongitudeConvention.POSITIVE_EAST_360,
    )

    for cb in [earth, mars, io, venus]:
        if not cb_repo.get_by_id(cb.id):
            cb_repo.create(cb)

    # 3. Volcanic Systems
    etna = VolcanicSystem(
        id="volc-etna",
        celestial_body_id="earth",
        name="Mount Etna",
        latitude=37.751,
        longitude=14.993,  # -180..+180
        elevation_m=3357.0,
        region="Sicily, Italy",
        volcanic_type="Stratovolcano",
        status=SystemStatus.ACTIVE,
    )
    kilauea = VolcanicSystem(
        id="volc-kilauea",
        celestial_body_id="earth",
        name="Kilauea",
        latitude=19.421,
        longitude=-155.287,  # -180..+180
        elevation_m=1247.0,
        region="Hawaii, USA",
        volcanic_type="Shield Volcano",
        status=SystemStatus.ACTIVE,
    )
    olympus_mons = VolcanicSystem(
        id="volc-olympus-mons",
        celestial_body_id="mars",
        name="Olympus Mons",
        latitude=18.65,
        longitude=226.2,  # 0..360 Positive East
        elevation_m=21229.0,
        region="Tharsis Montes",
        volcanic_type="Shield Volcano",
        status=SystemStatus.DORMANT,
    )
    loki_patera = VolcanicSystem(
        id="volc-loki-patera",
        celestial_body_id="io",
        name="Loki Patera",
        latitude=13.0,
        longitude=309.5,  # 0..360 Positive East
        elevation_m=-1000.0,
        region="Tyre Region",
        volcanic_type="Patera",
        status=SystemStatus.ACTIVE,
    )
    maat_mons = VolcanicSystem(
        id="volc-maat-mons",
        celestial_body_id="venus",
        name="Maat Mons",
        latitude=-0.5,
        longitude=194.6,  # 0..360 Positive East
        elevation_m=8000.0,
        region="Atla Regio",
        volcanic_type="Shield Volcano",
        status=SystemStatus.ACTIVE,
    )

    for vs in [etna, kilauea, olympus_mons, loki_patera, maat_mons]:
        if not vs_repo.get_by_id(vs.id):
            vs_repo.create(vs)

    # 4. Observation Sources
    sentinel2 = ObservationSource(
        id="src-sentinel-2",
        name="Sentinel-2 MSI",
        platform_type=PlatformType.SATELLITE_ORBITER,
        operator_agency="ESA",
    )
    mro_ctx = ObservationSource(
        id="src-mro-ctx",
        name="MRO Context Camera",
        platform_type=PlatformType.SATELLITE_ORBITER,
        operator_agency="NASA / JPL",
    )
    etna_webcam = ObservationSource(
        id="src-etna-webcam",
        name="Etna Thermal WebCam",
        platform_type=PlatformType.GROUND_OBSERVATORY,
        operator_agency="INGV",
    )
    galileo_nims = ObservationSource(
        id="src-galileo-nims",
        name="Galileo NIMS",
        platform_type=PlatformType.SATELLITE_ORBITER,
        operator_agency="NASA / JPL",
    )

    for os_entry in [sentinel2, mro_ctx, etna_webcam, galileo_nims]:
        if not os_repo.get_by_id(os_entry.id):
            os_repo.create(os_entry)

    # 5. Observations (Composite Metadata & Coordinate Fallbacks)
    obs_etna = Observation(
        id="obs-etna-001",
        volcanic_system_id="volc-etna",
        source_id="src-etna-webcam",
        timestamp="2020-12-14T02:15:00Z",
        latitude=37.751,
        longitude=14.993,
        summary="Thermal radiometry and visual camera frame of Etna summit paroxysm.",
        media_path="media/etna_20201214.png",
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
                "brightness_temperature_kelvin": 920.5,
                "ambient_temperature_kelvin": 275.0,
                "thermal_flux_mw": 350.0,
                "anomaly_flag": True,
                "sensor_wavelength_um": 10.8,
                "saturation_threshold_exceeded": False,
            },
        },
    )

    # Multi-facet orbital + thermal + image observation on Mars
    obs_olympus = Observation(
        id="obs-olympus-001",
        volcanic_system_id="volc-olympus-mons",
        source_id="src-mro-ctx",
        timestamp="2021-05-20T14:45:00Z",
        latitude=18.65,
        longitude=226.2,
        summary="MRO CTX orbital multispectral scene over Olympus Mons caldera.",
        media_path="media/mro_olympus_caldera.tiff",
        metadata={
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
    )

    # Observation with NULL coordinates demonstrating spatial fallback to Loki Patera volcano coordinates
    obs_loki_fallback = Observation(
        id="obs-loki-001",
        volcanic_system_id="volc-loki-patera",
        source_id="src-galileo-nims",
        timestamp="2023-01-15T04:00:00Z",
        latitude=None,
        longitude=None,  # Nullable -> falls back to Loki Patera's (13.0, 309.5)
        summary="Galileo NIMS thermal spectrometer observation of active overturning lava lake.",
        media_path="media/galileo_loki_nims.dat",
        metadata={
            "active_facets": ["THERMAL", "PLANETARY_ORBITAL"],
            "thermal_metadata": {
                "brightness_temperature_kelvin": 450.0,
                "ambient_temperature_kelvin": 130.0,
                "thermal_flux_mw": 12000.0,
                "anomaly_flag": True,
                "sensor_wavelength_um": 4.8,
                "saturation_threshold_exceeded": True,
            },
            "orbital_metadata": {
                "spacecraft_altitude_km": 12500.0,
                "solar_incidence_angle_deg": 85.0,
                "emission_angle_deg": 12.0,
                "phase_angle_deg": 97.0,
                "target_planetary_datum": "IAU_IO_2000",
            },
        },
    )

    for obs in [obs_etna, obs_olympus, obs_loki_fallback]:
        if not obs_repo.get_by_id(obs.id):
            obs_repo.create(obs)

    # 6. Volcanic Events (Bounded & Ongoing Active Events)
    evt_etna = VolcanicEvent(
        id="evt-etna-2020",
        volcanic_system_id="volc-etna",
        title="Etna December 2020 Paroxysm",
        event_type=EventType.ERUPTION,
        start_time="2020-12-13T21:00:00Z",
        end_time="2020-12-14T12:00:00Z",
        vei_rating=2,
        description="Paroxysmal explosive eruption episode with lava fountains and ash plume at South-East Crater.",
    )

    # Active ongoing event on Earth (end_time = NULL)
    evt_kilauea = VolcanicEvent(
        id="evt-kilauea-ongoing",
        volcanic_system_id="volc-kilauea",
        title="Kilauea Halema'uma'u Crater Lava Lake Episode",
        event_type=EventType.LAVA_FLOW,
        start_time="2021-09-29T15:30:00Z",
        end_time=None,  # Ongoing active event
        vei_rating=1,
        description="Continuous effusive lava lake activity inside Halema'uma'u caldera crater.",
    )

    # Active ongoing event on Io with NULL vei_rating (effusive planetary thermal unrest)
    evt_loki = VolcanicEvent(
        id="evt-loki-flare",
        volcanic_system_id="volc-loki-patera",
        title="Loki Patera Overturning Thermal Flare",
        event_type=EventType.THERMAL_ANOMALY,
        start_time="2023-01-15T00:00:00Z",
        end_time=None,  # Ongoing planetary event
        vei_rating=None,  # Non-terrestrial effusive event without atmospheric VEI
        description="Cyclic crustal overturning and thermal emission flare across the Loki Patera silicate lava lake.",
    )

    for evt in [evt_etna, evt_kilauea, evt_loki]:
        if not ve_repo.get_by_id(evt.id):
            ve_repo.create(evt)

    # 7. ObservationEventLinks
    link_etna = ObservationEventLink(
        id="link-001",
        observation_id="obs-etna-001",
        event_id="evt-etna-2020",
        relationship_type=RelationshipType.CO_ERUPTIVE,
        temporal_offset_hours=5.25,
        notes="Thermal camera frame captured during peak lava fountaining phase.",
    )
    link_loki = ObservationEventLink(
        id="link-002",
        observation_id="obs-loki-001",
        event_id="evt-loki-flare",
        relationship_type=RelationshipType.CO_ERUPTIVE,
        temporal_offset_hours=4.0,
        notes="Galileo NIMS observation during initial thermal flare outbreak.",
    )
    link_unrelated = ObservationEventLink(
        id="link-003",
        observation_id="obs-olympus-001",
        event_id="evt-loki-flare",
        relationship_type=RelationshipType.UNRELATED,
        temporal_offset_hours=None,
        notes="Demonstration link verifying UNRELATED relationship classification across bodies.",
    )

    for link in [link_etna, link_loki, link_unrelated]:
        if not link_repo.get_by_id(link.id):
            link_repo.create(link)

    print("Seed data successfully populated!")


if __name__ == "__main__":
    seed_database()
