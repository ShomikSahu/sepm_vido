# Phase 4 API Layer Specification

## 1. Overview & Architecture

Phase 4 implements the RESTful API layer for the Volcanic Image/Data Observatory (VIDO) using FastAPI and Pydantic v2. The API acts as a thin controller layer that validates incoming JSON payloads, delegates domain validation and business orchestration to Phase 3 services, interacts with Phase 2 SQLite repositories, and returns structured JSON responses matching the approved domain model.

```
HTTP Request
    │
    ▼
[ FastAPI Controller / Router (`/api/v1/...`) ]
    │ (Pydantic Schema Validation)
    ▼
[ Phase 3 Business Services ]
 (ValidationService, CoordinateService, SpatialService, EventService, TimelineService)
    │
    ▼
[ Phase 2 Repositories ]
 (CelestialBodyRepository, VolcanicSystemRepository, ObservationRepository, etc.)
    │
    ▼
[ SQLite Database (`data/vido.db`) ]
```

---

## 2. Endpoint Catalogue

All endpoints are versioned under `/api/v1`:

| Method | Endpoint Path | Description |
| :--- | :--- | :--- |
| `GET` | `/health` | Service operational health check |
| `GET` | `/api/v1/celestial-bodies` | List all celestial bodies |
| `GET` | `/api/v1/celestial-bodies/{id}` | Get metadata for a specific celestial body |
| `GET` | `/api/v1/volcanic-systems` | List volcanic systems (optional `celestial_body_id` filter) |
| `GET` | `/api/v1/volcanic-systems/{id}` | Get detailed volcanic system with parent body metadata |
| `GET` | `/api/v1/volcanic-systems/{id}/spatial` | Get spatial observation coordinates and fallback source tags |
| `GET` | `/api/v1/volcanic-systems/{id}/timeline` | Get unified dual-lane and interleaved chronological timeline feed |
| `GET` | `/api/v1/observation-sources` | List observation sources and platforms |
| `GET` | `/api/v1/observation-sources/{id}` | Get metadata for a specific observation source |
| `POST` | `/api/v1/observations` | Ingest/create a scientific observation with facet validation |
| `GET` | `/api/v1/observations/{id}` | Get a specific observation record by ID |
| `GET` | `/api/v1/observations` | Search & filter observations (`volcanic_system_id`, `celestial_body_id`, `source_id`, `facet`, date range) |
| `POST` | `/api/v1/volcanic-events` | Create a physical volcanic event (bounded or ongoing) |
| `GET` | `/api/v1/volcanic-events/{id}` | Get a specific volcanic event by ID |
| `GET` | `/api/v1/volcanic-events` | List volcanic events (optional `volcanic_system_id` or `ongoing_only` filter) |
| `POST` | `/api/v1/observation-event-links` | Create a relationship link between an observation and an event |
| `GET` | `/api/v1/observations/{id}/links` | Get linked event context for a specific observation |

---

## 3. Status Codes & Error Handling

Domain exceptions and service validation results are mapped directly to standard HTTP status codes:

* **`200 OK`**: Successful query or retrieval.
* **`201 Created`**: Successful creation of an observation, event, or relationship link.
* **`400 Bad Request`**: Business rule or coordinate validation failure (e.g. Earth longitude > 180°, invalid facet payload, inverted event timestamps).
* **`404 Not Found`**: Target resource (system, observation, event, body) does not exist.
* **`409 Conflict`**: Duplicate ID or duplicate observation-event relationship link (`UNIQUE(observation_id, event_id)`).
* **`422 Unprocessable Entity`**: Request body fails Pydantic schema validation.
* **`500 Internal Server Error`**: Unexpected system or database exception.

---

## 4. Representative API Examples

### 4.1 Ingesting a Multi-Facet Observation (`POST /api/v1/observations`)
```json
{
  "id": "obs-olympus-001",
  "volcanic_system_id": "volc-olympus-mons",
  "source_id": "src-mro-ctx",
  "timestamp": "2021-05-20T14:45:00Z",
  "latitude": 18.65,
  "longitude": 226.2,
  "summary": "MRO CTX orbital scene over Olympus Mons.",
  "metadata": {
    "active_facets": ["IMAGE", "THERMAL", "PLANETARY_ORBITAL"],
    "image_metadata": {
      "spectral_band": "NEAR_INFRARED",
      "spatial_resolution_m": 6.0,
      "cloud_cover_percentage": 0.0,
      "file_format": "GeoTIFF",
      "image_dimensions": {"width": 4096, "height": 4096},
      "sun_elevation_angle_deg": 52.3
    },
    "thermal_metadata": {
      "brightness_temperature_kelvin": 210.0,
      "ambient_temperature_kelvin": 200.0,
      "thermal_flux_mw": 5.0,
      "anomaly_flag": false,
      "sensor_wavelength_um": 12.0,
      "saturation_threshold_exceeded": false
    },
    "orbital_metadata": {
      "spacecraft_altitude_km": 310.5,
      "solar_incidence_angle_deg": 48.2,
      "emission_angle_deg": 5.1,
      "phase_angle_deg": 53.3,
      "target_planetary_datum": "IAU_MARS_2000"
    }
  }
}
```

### 4.2 Querying System Timeline (`GET /api/v1/volcanic-systems/volc-kilauea/timeline`)
```json
{
  "volcanic_system_id": "volc-kilauea",
  "volcanic_system_name": "Kilauea",
  "celestial_body_id": "earth",
  "celestial_body_name": "Earth",
  "timeline_reference_time": "2026-09-01T21:40:00Z",
  "events_count": 2,
  "observations_count": 1,
  "events_lane": [
    {
      "id": "evt-kilauea-ongoing",
      "title": "Active Summit Lava Lake",
      "start_time": "2021-09-29T15:30:00Z",
      "end_time": null,
      "display_end_time": "2026-09-01T21:40:00Z",
      "is_ongoing": true,
      "vei_rating": 1
    }
  ]
}
```

---

## 5. Automated API Integration Testing

The API test suite ([`tests/test_api.py`](file:///c:/Users/91979/Desktop/Volcanic_Image_Data_Observatory_SEPM_PROJECT/tests/test_api.py)) uses FastAPI's `TestClient` with isolated in-memory SQLite databases to verify:
- OpenAPI documentation generation (`/openapi.json`).
- Celestial body and volcanic system listing and retrieval.
- Observation creation and retrieval with multi-facet validation.
- Rejection of invalid Earth (-180°..+180°) and planetary (0°..360° Positive East) longitudes (400 Bad Request).
- Duplicate relationship link conflict handling (409 Conflict).
- Missing resource handling (404 Not Found).
- Spatial fallback tagging (`OBSERVATION`, `VOLCANO_FALLBACK`, `UNLOCATED`).
- Ongoing event `NULL` representation in responses.
