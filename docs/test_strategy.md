# Quality Assurance & Test Strategy
## Volcanic Image/Data Observatory (VIDO)

---

## 1. Overview & Quality Philosophy

The verification strategy for VIDO guarantees that heterogeneous scientific observations are strictly validated, accurately persisted, correctly queried, and faithfully presented over space and time across both terrestrial and planetary coordinate systems.

In accordance with SEPM best practices, testing spans multiple automated levels using `pytest` and `httpx`.

---

## 2. Testing Levels & Scope

```
                      +------------------------+
                      |   End-to-End System    |  Manual UI Verification
                      |   & UI Exploratory     |  & Spatial/Timeline Audit
                      +------------------------+
                      |    API Integration     |  FastAPI TestClient / HTTPX
                      |      Test Suite        |  Endpoint Status & Payload Tests
                      +------------------------+
                      |   Domain Logic & Schema|  Pydantic Boundary Tests
                      |   Facet Validation     |  Data Integrity & Fallback Checks
                      +------------------------+
```

### 2.1 Unit Testing (Domain & Validation Layer)
- **Tooling:** `pytest`
- **Scope:** Isolated testing of domain model methods, metadata facet validators (`IMAGE`, `THERMAL`, `PLANETARY_ORBITAL`), coordinate convention checkers (Earth -180°..+180° vs Planetary 0°..360°), spatial fallback logic, and timeline aggregation helper functions.
- **Coverage Target:** > 85% line coverage on service and validation logic.

### 2.2 Integration Testing (API & Repository Layer)
- **Tooling:** `pytest`, `fastapi.testclient`, SQLite in-memory database (`:memory:`).
- **Scope:** Validates interactions between API routes, service controllers, repositories, and SQLite persistence. Verifies SQL/JSON query execution for composite metadata.
- **Coverage Target:** 100% route coverage across all API endpoints.

### 2.3 System & Exploratory Verification (Presentation Layer)
- **Tooling:** Browser inspection & API contract validation.
- **Scope:** Verifies cross-browser layout rendering, Leaflet Earth map marker accuracy, Canvas planetary coordinate grid plotting, timeline node highlighting (including ongoing events), and detail modal responses.

---

## 3. Data Validation & Boundary Testing Suite

Validation is the core defensive layer of VIDO. Tests explicitly target boundary conditions for metadata facets, coordinate systems, temporal logic, and spatial fallback rules:

| Category | Test Scenario | Input Data | Expected Result |
| :--- | :--- | :--- | :--- |
| `THERMAL` Facet | Valid thermal payload | `brightness_temp_k = 750.0` | Pass facet validation |
| `THERMAL` Facet | Negative Kelvin temperature | `brightness_temp_k = -10.0` | HTTP 422 Unprocessable Entity |
| `IMAGE` Facet | Missing spectral band | `"cloud_cover": 5.0` (missing `spectral_band`) | HTTP 422 Validation Error |
| `IMAGE` Facet | Cloud cover > 100% | `cloud_cover_percentage = 105.0` | HTTP 422 Boundary Failure |
| `COORDINATES` | Earth out-of-bounds longitude | `longitude = 210.0` on Earth (`EAST_WEST_180`) | HTTP 422 Coordinate Boundary Error |
| `COORDINATES` | Mars valid planetary longitude | `longitude = 226.5` on Mars (`POSITIVE_EAST_360`) | Pass validation |
| `COMPOSITE` | Multi-facet payload | `metadata` containing `IMAGE` and `THERMAL` facets | HTTP 201 / Pass composite validation |
| `TEMPORAL` | Inverted event timestamps | `start_time > end_time` | HTTP 400 Bad Request |
| `ONGOING_EVENT` | Active ongoing event | `end_time = NULL` | HTTP 201 / Render open-ended span |
| `SPATIAL_FALLBACK`| NULL observation coordinates | `latitude = NULL`, `longitude = NULL` | Fallback to volcano coordinates |
| `UNLOCATED` | NULL observation & volcano coords | both coordinates `NULL` | Route to Unlocated drawer |

---

## 4. Master Test Cases Matrix

| Test ID | Test Category | Target Requirement | Description | Success Criteria |
| :--- | :--- | :--- | :--- | :--- |
| **TC-01** | Unit | FR-10, FR-01 | Verify system filtering by Celestial Body and coordinate reference frame. | Query returns matching systems with correct longitude bounds. |
| **TC-02** | Unit / Validation | FR-08 | Validate `IMAGE` and `THERMAL` facet schema rules. | Rejects invalid payloads; accepts valid multi-facet payload. |
| **TC-03** | Integration | FR-03, FR-05 | POST composite observation payload to `/api/v1/observations`. | Returns 201 Created; json metadata reflects active facets. |
| **TC-04** | Integration | FR-04 | Filter observations by date range and metadata facet category. | Result set matches exact date boundary and facet filter. |
| **TC-05** | Service Unit | FR-06 | Aggregate timeline entries for a volcano (including ongoing events). | Combines events and observations in strict chronological order; ongoing events rendered as open spans. |
| **TC-06** | Integration | FR-09 | Create `ObservationEventLink` association with `UNRELATED` tag. | Link entry created; query retrieves linked events for observation. |
| **TC-07** | Integration | FR-02 | Fetch non-existent volcano ID. | Returns HTTP 404 Not Found with clean JSON error payload. |
| **TC-08** | E2E | FR-07, FR-10 | Load Spatial Map view for Mars volcanoes. | Spatial pins render at correct 0°..360° relative planetary coordinates; fallback rules applied correctly. |

---

## 5. Automated Test Execution Plan

Test execution is fully automated using `pytest` commands executable from the project root:

```bash
# Run unit and integration tests with coverage report
pytest --cov=app --cov-report=term-missing tests/

# Run validation facet schema tests specifically
pytest tests/unit/test_validation.py

# Run API endpoint integration tests
pytest tests/integration/test_api.py
```

