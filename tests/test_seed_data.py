from scripts.seed_data import seed_database
from app.repositories import (
    CelestialBodyRepository,
    VolcanicSystemRepository,
    ObservationSourceRepository,
    ObservationRepository,
    VolcanicEventRepository,
    ObservationEventLinkRepository,
)


def test_seed_database_execution_and_integrity(in_memory_db):
    seed_database(in_memory_db)

    cb_repo = CelestialBodyRepository(in_memory_db)
    vs_repo = VolcanicSystemRepository(in_memory_db)
    os_repo = ObservationSourceRepository(in_memory_db)
    obs_repo = ObservationRepository(in_memory_db)
    ve_repo = VolcanicEventRepository(in_memory_db)
    link_repo = ObservationEventLinkRepository(in_memory_db)

    # Check celestial bodies (Earth, Mars, Io, Venus)
    bodies = cb_repo.get_all()
    assert len(bodies) >= 4
    body_ids = {b.id for b in bodies}
    assert {"earth", "mars", "io", "venus"}.issubset(body_ids)

    # Check volcanic systems
    systems = vs_repo.get_all()
    assert len(systems) >= 5
    system_ids = {s.id for s in systems}
    assert {"volc-etna", "volc-kilauea", "volc-olympus-mons", "volc-loki-patera", "volc-maat-mons"}.issubset(system_ids)

    # Check observations & composite facets
    observations = obs_repo.get_all()
    assert len(observations) >= 3
    olympus_obs = obs_repo.get_by_id("obs-olympus-001")
    assert olympus_obs is not None
    assert set(olympus_obs.metadata["active_facets"]) == {"IMAGE", "THERMAL", "PLANETARY_ORBITAL"}

    # Check ongoing events & optional VEI
    events = ve_repo.get_all()
    assert len(events) >= 3
    ongoing_events = ve_repo.get_ongoing_events()
    assert len(ongoing_events) >= 2  # Kilauea and Loki Patera flares

    # Check links
    links = link_repo.get_all()
    assert len(links) >= 3
