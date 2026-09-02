import pytest
from app.db.database import DatabaseManager, db_manager
from app.db.schema import init_db
from app.repositories import (
    CelestialBodyRepository,
    VolcanicSystemRepository,
    ObservationSourceRepository,
    ObservationRepository,
    VolcanicEventRepository,
    ObservationEventLinkRepository,
)


@pytest.fixture
def in_memory_db():
    """Provides a fresh SQLite in-memory database manager for each test, overriding db_manager."""
    db = DatabaseManager(db_path=":memory:")
    with db.get_connection() as conn:
        init_db(conn)

    # Backup original shared_conn and set db_manager to point to test db
    orig_path = db_manager.db_path
    orig_conn = db_manager._shared_conn
    db_manager.db_path = ":memory:"
    db_manager._shared_conn = db._shared_conn

    yield db

    db.close()
    db_manager.db_path = orig_path
    db_manager._shared_conn = orig_conn


@pytest.fixture
def repositories(in_memory_db):
    """Provides instantiated repositories connected to an in-memory database."""
    return {
        "celestial_body": CelestialBodyRepository(in_memory_db),
        "volcanic_system": VolcanicSystemRepository(in_memory_db),
        "observation_source": ObservationSourceRepository(in_memory_db),
        "observation": ObservationRepository(in_memory_db),
        "volcanic_event": VolcanicEventRepository(in_memory_db),
        "observation_event_link": ObservationEventLinkRepository(in_memory_db),
    }
