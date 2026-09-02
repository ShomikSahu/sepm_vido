# Software Requirements Specification (SRS)
## Volcanic Image/Data Observatory (VIDO)

---

## 1. Introduction

### 1.1 Purpose
The purpose of this document is to define the functional and non-functional requirements for the **Volcanic Image/Data Observatory (VIDO)**, an undergraduate Software Engineering and Project Management (SEPM) project. VIDO is a lightweight scientific observation-management and spatial-temporal exploration system designed to unify terrestrial and planetary volcanology data.

### 1.2 Problem Statement
Volcanic research generates heterogeneous observational datasets across multiple platforms—ranging from ground photographs and thermal radiometry on Earth to planetary orbiter multispectral imaging on Mars, Io, and Venus. Current systems often isolate earth-bound datasets from planetary science datasets, or fail to handle heterogeneous observational metadata gracefully.

**Central Engineering Problem:**
> *"How can heterogeneous scientific observations of volcanic systems be represented, validated, stored, queried, and explored coherently across space and time?"*

### 1.3 System Overview
VIDO provides a unified conceptual domain model connecting celestial bodies, volcanic systems, observations, observation metadata facets, dynamic payload validation, and eruptive events. It enables multi-planet spatial-temporal exploration without introducing excessive enterprise complexity or heavy third-party framework overhead.

---

## 2. Conceptual Domain Hierarchy

The system enforces two foundational structural hierarchies:

```
Hierarchy A: Observational Hierarchy
Celestial Body / Planet (Coordinate Frame / Datum)
    ↓
Volcanic System / Volcano
    ↓
Observation
    ↓
Observation Metadata Facets (Image / Thermal / Planetary Orbital)
    ↓
Metadata Payload (Heterogeneous / Validated Composite)

Hierarchy B: Temporal Event Hierarchy
Volcanic System / Volcano
    ↓
Volcanic Event (Eruption / Thermal Unrest / Ongoing Episode)
    ↓
Temporal / Spatial Association with Observations (ObservationEventLink)
```

---

## 3. Functional Requirements (FR)

| ID | Title | Summary & Specification | Priority |
| :--- | :--- | :--- | :--- |
| **FR-01** | Browse and Search Volcanic Systems | The system **shall** allow users to browse a list of volcanic systems and search them by name, celestial body (e.g., Earth, Mars, Io, Venus), volcanic status, or classification type. | **Must Have** |
| **FR-02** | Display Volcanic System Details | The system **shall** display comprehensive details for any selected volcanic system, including its parent celestial body, planetary coordinates (latitude/longitude), elevation/altitude, region, and geological classification. | **Must Have** |
| **FR-03** | Store Composite & Heterogeneous Observations | The system **shall** store observations associated with a volcanic system, supporting composite metadata payloads comprising zero or more distinct metadata facets (Image, Thermal, Planetary Orbital). | **Must Have** |
| **FR-04** | Multi-Criteria Observation Filtering | The system **shall** allow users to filter observations by date range, metadata facet category (Image, Thermal, Planetary Orbital), data source (e.g., Sentinel-2, Mars Reconnaissance Orbiter, Ground Observatory), and associated volcanic system. | **Must Have** |
| **FR-05** | Display Detailed Observation Metadata | The system **shall** present complete raw and formatted observational metadata for any selected observation, including active metadata facets (sensor calibration, spectral parameters, thermal flux, orbital geometry), environmental conditions, and file artifacts. | **Must Have** |
| **FR-06** | Chronological Timeline Visualization | The system **shall** render a unified interactive chronological timeline displaying both observations and recorded volcanic events for a selected volcanic system. Open-ended/ongoing events (where end date is NULL) shall be explicitly represented as ongoing spans. | **Must Have** |
| **FR-07** | Spatial Coordinate Visualization | The system **shall** display observation locations spatially on visual maps or coordinate grids using body-appropriate coordinates. If observation coordinates are NULL, spatial visualization shall fall back to the parent VolcanicSystem coordinates; if neither is available, the observation shall be rendered in an unlocated observations listing. | **Must Have** |
| **FR-08** | Observation Metadata Validation | The system **shall** validate incoming observation payloads against predefined schema rules for each attached metadata facet (Image, Thermal, Planetary Orbital) before persisting the data. | **Must Have** |
| **FR-09** | Observation-Event Association | The system **shall** allow observations to be associated with specific volcanic events using temporal, spatial, or manual relationship classifications (`PRE_ERUPTIVE`, `CO_ERUPTIVE`, `POST_ERUPTIVE`, `UNRELATED`). | **Must Have** |
| **FR-10** | Dual Terrestrial & Planetary Support | The system **shall** support both Earth volcanoes and planetary volcanic features within the exact same underlying data model, accommodating body-specific coordinate reference frames (Earth -180° to +180°, planetary 0° to 360° Positive East). | **Must Have** |

---

## 4. Non-Functional Requirements (NFR)

### 4.1 Usability (NFR-01)
- The user interface shall provide intuitive navigation between celestial bodies, volcanic systems, timeline views, and detail modals without requiring specialized domain training.
- Search and filtering controls shall update or present search results within clear UI states.

### 4.2 Maintainability & Modularity (NFR-02)
- Codebase shall adhere to standard layered architecture (Presentation → API → Logic → Data Access).
- New observation facets/types should be addable through modular schema definitions without requiring changes to unrelated database tables or core API architecture.

### 4.3 Validation & Integrity (NFR-03)
- Invalid metadata payloads (e.g., negative Kelvin thermal temperatures, out-of-range latitude/longitude coordinates based on the celestial body's coordinate system) shall be rejected with detailed, actionable error responses.
- Temporal consistency rules must be enforced (e.g., event end date cannot precede start date when end date is provided).

### 4.4 Reliability & Resilience (NFR-04)
- Database interactions shall use transactions to ensure data consistency during creation or updating of observations and event links.
- Graceful error handling for missing media/image references or corrupted metadata fields.

### 4.5 Performance (NFR-05)
- For target dataset sizes (up to 1,000 volcanic systems and 10,000 observations):
  - API query responses for search/filter requests shall take < 200 ms.
  - Initial UI load time shall take < 1.0 second on local standard developer hardware.

### 4.6 Testability (NFR-06)
- The system logic and validation engine shall maintain > 80% automated unit test coverage.
- End-to-end API endpoints shall be fully testable via automated API test suites (`pytest`).

### 4.7 Documentation (NFR-07)
- OpenAPI (Swagger) documentation shall be automatically generated for all API endpoints.
- Complete domain model, requirements, architectural guidelines, and setup instructions must be maintained in the `docs/` repository.

### 4.8 Extensibility (NFR-08)
- The architecture must decouple data storage from visualization layers to permit future integration of GIS mapping tools, real-time data feeds, or computer vision modules.

---

## 5. Traceability Matrix

| Requirement | Domain Entity / Component | Use Case Reference | Test Verification Strategy |
| :--- | :--- | :--- | :--- |
| **FR-01** | `VolcanicSystem`, `CelestialBody` | UC-01: Browse Volcanic Systems | Unit tests for filter API & System Search |
| **FR-02** | `VolcanicSystem`, `CelestialBody` | UC-01: Browse Volcanic Systems | API Integration test for system detail query |
| **FR-03** | `Observation`, Facet Schemas | UC-07: Validate & Ingest Observation | Repository integration test for composite payload inserts |
| **FR-04** | `ObservationRepository`, Services | UC-02: Search Observations, UC-03: Filter Observations | Filter API query parameter test suite |
| **FR-05** | `Observation`, Facet Schemas | UC-04: View Observation Details | UI/API metadata payload inspection test |
| **FR-06** | `VolcanicEvent`, `Observation` | UC-05: View Volcanic Timeline | Timeline aggregation service test (including ongoing events) |
| **FR-07** | `VolcanicSystem`, `Observation` | UC-06: View Spatial Observations | Spatial coordinate serialization and fallback test |
| **FR-08** | `ValidationEngine`, Facet Schemas | UC-07: Validate & Ingest Observation | Schema boundary validation unit tests |
| **FR-09** | `ObservationEventLink` | UC-08: Associate Obs with Event | Event link persistence & relational query test |
| **FR-10** | `CelestialBody`, `VolcanicSystem` | UC-01, UC-06 | Dual Earth/Planetary coordinate convention unit verification |
 unit verification |
