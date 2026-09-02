import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.db.database import DatabaseManager
from app.db.schema import init_db
from scripts.seed_data import seed_database


@pytest.fixture
def client(in_memory_db):
    """Provides a FastAPI TestClient using an isolated in-memory SQLite database."""
    init_db(in_memory_db.get_raw_connection())
    seed_database(in_memory_db)
    
    # Create client with FastAPI app instance
    with TestClient(app) as c:
        yield c


def test_openapi_json_generation(client):
    response = client.get("/openapi.json")
    assert response.status_code == 200
    schema = response.json()
    assert schema["info"]["title"] == "Volcanic Image/Data Observatory (VIDO) API"
    assert "/api/v1/celestial-bodies" in schema["paths"]
    assert "/api/v1/observations" in schema["paths"]


def test_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_list_celestial_bodies(client):
    response = client.get("/api/v1/celestial-bodies")
    assert response.status_code == 200
    bodies = response.json()
    assert len(bodies) >= 4
    body_ids = {b["id"] for b in bodies}
    assert {"earth", "mars", "io", "venus"}.issubset(body_ids)


def test_get_celestial_body_by_id(client):
    response = client.get("/api/v1/celestial-bodies/earth")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Earth"
    assert data["longitude_convention"] == "EAST_WEST_180"


def test_list_volcanic_systems(client):
    response = client.get("/api/v1/volcanic-systems")
    assert response.status_code == 200
    systems = response.json()
    assert len(systems) >= 5

    # Test filtering by celestial body
    mars_res = client.get("/api/v1/volcanic-systems?celestial_body_id=mars")
    assert mars_res.status_code == 200
    mars_systems = mars_res.json()
    assert len(mars_systems) == 1
    assert mars_systems[0]["id"] == "volc-olympus-mons"


def test_get_volcanic_system_detail(client):
    response = client.get("/api/v1/volcanic-systems/volc-etna")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Mount Etna"
    assert data["celestial_body"]["name"] == "Earth"


def test_observation_creation_and_retrieval(client):
    new_obs = {
        "id": "obs-api-test-01",
        "volcanic_system_id": "volc-etna",
        "source_id": "src-etna-webcam",
        "timestamp": "2021-01-01T12:00:00Z",
        "latitude": 37.75,
        "longitude": 14.99,
        "summary": "API Test Observation",
        "media_path": "media/test.png",
        "metadata": {
            "active_facets": ["IMAGE", "THERMAL"],
            "image_metadata": {
                "spectral_band": "VISIBLE_RGB",
                "spatial_resolution_m": 1.0,
                "cloud_cover_percentage": 5.0,
                "file_format": "PNG",
                "image_dimensions": {"width": 1920, "height": 1080},
                "sun_elevation_angle_deg": 45.0,
            },
            "thermal_metadata": {
                "brightness_temperature_kelvin": 500.0,
                "ambient_temperature_kelvin": 280.0,
                "thermal_flux_mw": 100.0,
                "anomaly_flag": True,
                "sensor_wavelength_um": 10.0,
                "saturation_threshold_exceeded": False,
            },
        },
    }
    # Create Observation
    create_res = client.post("/api/v1/observations", json=new_obs)
    assert create_res.status_code == 201
    created_data = create_res.json()
    assert created_data["id"] == "obs-api-test-01"

    # Retrieve Observation
    get_res = client.get("/api/v1/observations/obs-api-test-01")
    assert get_res.status_code == 200
    retrieved = get_res.json()
    assert retrieved["summary"] == "API Test Observation"
    assert set(retrieved["metadata"]["active_facets"]) == {"IMAGE", "THERMAL"}


def test_composite_observation_multiple_facets(client):
    # Retrieve Olympus Mons observation created by seed
    res = client.get("/api/v1/observations/obs-olympus-001")
    assert res.status_code == 200
    data = res.json()
    active_facets = data["metadata"]["active_facets"]
    assert set(active_facets) == {"IMAGE", "THERMAL", "PLANETARY_ORBITAL"}
    assert "image_metadata" in data["metadata"]
    assert "thermal_metadata" in data["metadata"]
    assert "orbital_metadata" in data["metadata"]


def test_invalid_coordinates_rejected_by_api(client):
    # Invalid Earth longitude (210°)
    bad_earth_obs = {
        "id": "obs-bad-earth",
        "volcanic_system_id": "volc-etna",
        "source_id": "src-etna-webcam",
        "timestamp": "2021-01-01T12:00:00Z",
        "latitude": 37.75,
        "longitude": 210.0,  # Invalid for Earth [-180, +180]
        "summary": "Bad Earth long",
    }
    res_earth = client.post("/api/v1/observations", json=bad_earth_obs)
    assert res_earth.status_code == 400
    assert "out of bounds for body 'Earth'" in res_earth.json()["detail"]

    # Invalid Mars longitude (-15°)
    bad_mars_obs = {
        "id": "obs-bad-mars",
        "volcanic_system_id": "volc-olympus-mons",
        "source_id": "src-mro-ctx",
        "timestamp": "2021-01-01T12:00:00Z",
        "latitude": 18.65,
        "longitude": -15.0,  # Invalid for Mars Positive East [0, 360]
        "summary": "Bad Mars long",
    }
    res_mars = client.post("/api/v1/observations", json=bad_mars_obs)
    assert res_mars.status_code == 400
    assert "out of bounds for body 'Mars'" in res_mars.json()["detail"]


def test_observation_search_and_facet_filtering(client):
    res_thermal = client.get("/api/v1/observations?facet=THERMAL")
    assert res_thermal.status_code == 200
    results = res_thermal.json()
    assert len(results) >= 2

    res_system = client.get("/api/v1/observations?volcanic_system_id=volc-etna")
    assert res_system.status_code == 200
    sys_results = res_system.json()
    assert len(sys_results) >= 1


def test_ongoing_event_api_representation(client):
    res = client.get("/api/v1/volcanic-events/evt-kilauea-ongoing")
    assert res.status_code == 200
    evt = res.json()
    assert evt["end_time"] is None
    assert evt["is_ongoing"] is True


def test_duplicate_link_returns_409_conflict(client):
    # Link that already exists in seed dataset
    duplicate_link = {
        "id": "link-duplicate",
        "observation_id": "obs-etna-001",
        "event_id": "evt-etna-2020",
        "relationship_type": "CO_ERUPTIVE",
    }
    res = client.post("/api/v1/observation-event-links", json=duplicate_link)
    assert res.status_code == 409
    assert "already exists" in res.json()["detail"]


def test_missing_resource_returns_404(client):
    res = client.get("/api/v1/observations/obs-nonexistent")
    assert res.status_code == 404
    assert "not found" in res.json()["detail"]


def test_system_spatial_endpoint(client):
    res = client.get("/api/v1/volcanic-systems/volc-loki-patera/spatial")
    assert res.status_code == 200
    spatial_data = res.json()
    located = spatial_data["located_observations"]
    assert len(located) >= 1
    # Check fallback resolution to volcano coords
    loki_obs = next(o for o in located if o["observation_id"] == "obs-loki-001")
    assert loki_obs["spatial_source"] == "VOLCANO_FALLBACK"
    assert loki_obs["latitude"] == 13.0


def test_system_timeline_endpoint(client):
    res = client.get("/api/v1/volcanic-systems/volc-etna/timeline")
    assert res.status_code == 200
    timeline = res.json()
    assert timeline["events_count"] >= 1
    assert timeline["observations_count"] >= 1
    assert len(timeline["combined_chronological_feed"]) >= 2
