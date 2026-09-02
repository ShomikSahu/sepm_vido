# Phased Implementation Plan & SEPM Risk Management
## Volcanic Image/Data Observatory (VIDO)

---

## 1. Project Phase Breakdown & Recommended Implementation Sequence

To ensure systematic incremental development in accordance with SEPM standards, implementation is partitioned into six sequential phases.

```
Phase 1: Requirements & Architecture (Current)
   │
   ▼
Phase 2: Core Domain Models & Data Layer Setup
   │
   ▼
Phase 3: Service Layer & Metadata Facet Validation Engine
   │
   ▼
Phase 4: API Layer & Endpoint Implementation
   │
   ▼
Phase 5: Presentation & Visualization UI Development
   │
   ▼
Phase 6: Quality Assurance, Verification & Audit
```

---

### Phase 1: Requirements & Architectural Specification (COMPLETE)
- **Goal:** Establish formal requirements, domain models, architectural boundaries, use cases, scope boundaries, test strategy, and phased plan.
- **Deliverables:** `docs/` repository documents (`requirements.md`, `use_cases.md`, `domain_model.md`, `architecture.md`, `scope.md`, `test_strategy.md`, `implementation_plan.md`).

---

### Phase 2: Core Domain Models & Data Access Layer
- **Goal:** Establish Python data models, database connection, ORM/SQLModel setup, and repository layer.
- **Tasks:**
  1. Define Pydantic base domain schemas for `CelestialBody` (including `longitude_convention`), `VolcanicSystem` (with `status`), `ObservationSource`, `Observation`, `VolcanicEvent`, `ObservationEventLink`.
  2. Implement SQLite database session manager and table migrations with JSON metadata column support.
  3. Build repository classes: `SystemRepository`, `ObservationRepository`, `EventRepository`, `LinkRepository`.
  4. Create seed dataset script (`scripts/seed_data.py`) containing Earth (Etna, Kilauea), Mars (Olympus Mons), Io (Loki Patera), and Venus (Maat Mons) records.

---

### Phase 3: Service Layer & Facet Validation Engine
- **Goal:** Implement domain business logic, composite facet validation, coordinate system resolution, and temporal aggregation services.
- **Tasks:**
  1. Implement `ValidationEngine` with specific Pydantic facet schemas (`ImageFacetSchema`, `ThermalFacetSchema`, `OrbitalFacetSchema`).
  2. Build `TimelineService` to merge observations and events into chronologically ordered timeline payloads (supporting ongoing events where `end_time` is NULL).
  3. Build `SpatialService` to evaluate coordinate reference conventions (Earth -180°..+180° vs Planetary 0°..360° Positive East) and apply coordinate fallback logic (Observation coords → Volcano coords → Unlocated drawer).
  4. Write unit tests for validation rules, coordinate boundaries, and services (`tests/unit/`).

---

### Phase 4: API Layer & Endpoints
- **Goal:** Build and expose RESTful JSON API using FastAPI.
- **Tasks:**
  1. Implement System endpoints: `GET /api/v1/volcanoes`, `GET /api/v1/volcanoes/{id}`.
  2. Implement Observation endpoints: `GET /api/v1/observations`, `POST /api/v1/observations`, `GET /api/v1/observations/{id}`.
  3. Implement Timeline & Event endpoints: `GET /api/v1/timeline/{volcano_id}`, `POST /api/v1/events/link` (supporting `PRE_ERUPTIVE`, `CO_ERUPTIVE`, `POST_ERUPTIVE`, `UNRELATED`).
  4. Integrate automatic OpenAPI Swagger documentation.
  5. Write API integration tests (`tests/integration/`).

---

### Phase 5: Presentation & Visualization UI
- **Goal:** Build lightweight, responsive web interface using HTML5, CSS3, and JavaScript.
- **Tasks:**
  1. Implement layout shell, sidebar navigation, and header controls.
  2. Build **Volcanic System Browser** card view with search/filter controls.
  3. Build **Multi-Criteria Observation Filter & Data Table** (filtering by `IMAGE`, `THERMAL`, `PLANETARY_ORBITAL` facets).
  4. Build **Interactive Dual-Lane Timeline Visualizer** using Plotly.js / Canvas.
  5. Build **Spatial Map Explorer** using Leaflet.js (for Earth WGS84) and Canvas/SVG coordinate grid (for planetary 0°..360° Positive East).
  6. Build **Observation Detail Modal** with formatted metadata facet inspector.

---

### Phase 6: Quality Assurance, Verification & Final Polish
- **Goal:** Complete end-to-end testing, audit against requirements, and final documentation polish.
- **Tasks:**
  1. Run full `pytest` suite and generate test coverage report (> 85% target).
  2. Verify all 10 Functional Requirements (FR-01 to FR-10).
  3. Perform UI/UX exploratory testing across sample datasets.
  4. Finalize project README and SEPM submission summary.

---

## 2. SEPM Risk Management Matrix

| Risk ID | Identified Project Risk | Impact | Likelihood | Risk Category | Proposed Mitigation Strategy |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **R-01** | **Heterogeneous Data Modeling Risk:** Inconsistent metadata schemas across different observation types causing database query failures. | High | Medium | Architecture / Data | Use a composite JSON payload structure backed by Pydantic facet schemas (`IMAGE`, `THERMAL`, `PLANETARY_ORBITAL`). Standardize universal top-level properties (id, timestamp, lat/long). |
| **R-02** | **External Data Dependency Risk:** External satellite APIs breaking or changing rate limits during development. | High | High | External | **MVP Safeguard:** Eliminate live external API dependencies. Populate the system using local seed JSON datasets and local image assets. |
| **R-03** | **GIS & Map Complexity Risk:** Enterprise GIS map servers (GeoServer/ArcGIS) requiring complex spatial projections and server setups. | Medium | High | Complexity | **MVP Safeguard:** Use Leaflet.js with standard WGS84 coordinates for Earth, and lightweight Canvas/SVG grid views for planetary bodies. |
| **R-04** | **Image Processing Overload:** Attempting complex image analysis or computer vision, distracting from core SEPM goals. | High | Medium | Scope Creep | **MVP Safeguard:** Treat images as media artifacts with metadata attributes. Explicitly defer computer vision and automated detection to future extensions. |
| **R-05** | **Scope Creep Risk:** Adding unnecessary enterprise features (Auth, Webhooks, React build pipelines) leading to missed deadlines. | High | High | Project Mgmt | Enforce strict MoSCoW scope boundary defined in `docs/scope.md`. Require change control review for any new feature. |
| **R-06** | **Scientific Data Accuracy Risk:** Incorrect planetary datums or inverted coordinate values leading to confusing visual displays. | Medium | Medium | Scientific Data | Utilize standard IAU planetocentric coordinate conventions (0°..360° Positive East vs -180°..+180°) and document coordinate reference frames in `CelestialBody` records. |
| **R-07** | **Visualization Complexity Risk:** Timeline rendering becoming overcrowded when hundreds of observations exist for a single event. | Medium | Medium | UI/UX | Implement timeline binning/clustering, open-ended span rendering for ongoing events, and interactive filter controls. |

---

## 3. SEPM Core Principles Alignment

This project explicitly demonstrates key Software Engineering & Project Management principles:

1. **Requirements Engineering:** Clear functional (FR-01 to FR-10) and non-functional requirements linked directly to Use Cases and Test Cases.
2. **Modular Layered Architecture:** Decoupling Presentation, API, Business Logic, Data Access, and Persistence.
3. **Defensive Validation Engineering:** Runtime schema validation rejecting bad payloads before persistence.
4. **Scope Control & Governance:** Explicit MVP boundary definition preventing scope bloat.
5. **Traceability:** Full two-way mapping between Requirements → Domain Entities → Use Cases → Test Suite.
6. **Risk-Driven Planning:** Proactive identification and mitigation of scientific data, GIS, and architectural risks.
