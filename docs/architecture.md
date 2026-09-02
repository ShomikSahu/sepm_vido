# System Architecture Specification
## Volcanic Image/Data Observatory (VIDO)

---

## 1. Architectural Style & Overview

VIDO adopts a **Lightweight Layered Architecture** (Presentation → API Layer → Domain / Service Layer → Data Access Layer → Database) designed specifically for clear separation of concerns, high testability, and undergraduate project maintainability.

### High-Level Architecture Diagram

```
+-----------------------------------------------------------------------+
|                         PRESENTATION LAYER                            |
|  Vanilla HTML5 / Modern CSS3 (CSS Variables, Flex/Grid) / JS (ES6+)    |
|  - System Browser UI      - Timeline Renderer (Plotly.js / Canvas)    |
|  - Spatial Map View       - Observation Detail Modal / Filter Drawer  |
|    (Leaflet Earth / Canvas Planetary Grid)                            |
+-----------------------------------------------------------------------+
                                   |
                             HTTP / REST (JSON)
                                   v
+-----------------------------------------------------------------------+
|                            API LAYER                                  |
|  Python FastAPI Web Server                                            |
|  - Endpoint Routers       - Request/Response Serialization            |
|  - OpenAPI Auto-Docs      - HTTP Error Handling & Status Codes        |
+-----------------------------------------------------------------------+
                                   |
                            Service Contracts
                                   v
+-----------------------------------------------------------------------+
|                   SERVICE / BUSINESS LOGIC LAYER                      |
|  - Facet Validation Engine - Spatial-Temporal Query Coordinator       |
|  - Timeline Aggregator     - Event-Observation Association Logic      |
|    (Ongoing Event & Spatial Fallback Rules)                           |
+-----------------------------------------------------------------------+
                                   |
                            Data Abstraction
                                   v
+-----------------------------------------------------------------------+
|                    REPOSITORY / DATA ACCESS LAYER                     |
|  - System Repository      - Observation Repository (JSON Filtering)   |
|  - Event Repository       - Link Repository                           |
+-----------------------------------------------------------------------+
                                   |
                               SQL / JSON
                                   v
+-----------------------------------------------------------------------+
|                            DATABASE LAYER                             |
|  SQLite 3 Embedded Relational Engine (with native JSON1 extension)    |
+-----------------------------------------------------------------------+
```

---

## 2. Layer Rationale & Responsibilities

### 2.1 Presentation Layer
- **Responsibility:** Renders user interfaces for browsing volcanoes, filtering observations, visualizing chronological timelines, and interacting with spatial maps.
- **Why it exists:** Isolates user interaction and visual rendering from core scientific domain logic. Uses clean, modern vanilla JavaScript and standard web assets (HTML/CSS) to avoid heavy frontend build step complexity while delivering a responsive visual experience. Uses Leaflet.js for Earth spatial maps and a lightweight Canvas/SVG coordinate grid for planetary features.

### 2.2 API Layer
- **Responsibility:** Exposes RESTful JSON endpoints (`GET /api/v1/volcanoes`, `POST /api/v1/observations`, `GET /api/v1/timeline/{id}`, etc.) and handles input parsing/deserialization.
- **Why it exists:** Decouples the client frontend from backend logic. Automatically generates interactive Swagger API documentation.

### 2.3 Service / Business Logic Layer
- **Responsibility:** Implements domain rules, coordinates multi-repository transactions, executes Pydantic facet payload validation (`IMAGE`, `THERMAL`, `PLANETARY_ORBITAL`), handles coordinate system resolution (Earth -180°..+180° vs planetary 0°..360° Positive East), applies spatial coordinate fallback rules, and aggregates timeline event payloads (including ongoing events with NULL `end_time`).
- **Why it exists:** Prevents data validation rules or business logic from leaking into API controllers or database queries.

### 2.4 Repository / Data Access Layer
- **Responsibility:** Encapsulates raw database queries (SQL / SQLAlchemy / SQLModel abstractions) and provides clean domain object persistence interfaces.
- **Why it exists:** Protects application logic from database implementation details.

### 2.5 Database Layer
- **Responsibility:** Provides persistent, ACID-compliant storage for system entities and composite metadata payloads (`metadata` JSON column).
- **Why it exists:** Guarantees data durability and enables efficient indexing across spatial coordinates, timestamps, and metadata JSON keys using SQLite's native JSON capabilities.

---

## 3. Recommended Technology Stack & Rationale

| Layer | Recommended Technology | Technical Rationale |
| :--- | :--- | :--- |
| **Backend Language** | **Python 3.11+** | Industry standard for data science and volcanology tooling; clean syntax, rich ecosystem. |
| **Web Framework** | **FastAPI** | High-performance asynchronous framework, native Pydantic validation, automatic OpenAPI specs. |
| **Database Engine** | **SQLite 3** | Zero-configuration, file-based embedded SQL engine; eliminates server installation overhead while supporting JSON queries. |
| **Data Validation** | **Pydantic v2** | Enforces strict schema definitions and runtime data type checking for composite observation metadata facets. |
| **Frontend Framework** | **Vanilla HTML5 / CSS3 / ES6 JS** | Lightweight, zero-build-step deployment; fast rendering without Webpack/Vite complexity. |
| **Visualization Libraries** | **Leaflet.js / Plotly.js** | Leaflet.js for Earth spatial maps; Plotly.js for interactive dual-lane temporal timelines; Canvas/SVG for planetary grids. |

---

## 4. Design for Extensibility & Future Capabilities

The architecture is explicitly designed to support future SEPM extensions without requiring architectural rewrites:

```
                                  [ VIDO Core API ]
                                          |
        +---------------------------------+---------------------------------+
        |                                 |                                 |
        v                                 v                                 v
[ External Satellite Connector ]  [ Computer Vision Engine ]     [ Real-Time Ingest Pipeline ]
 (Fetch Sentinel / MRO feed)      (Thermal anomaly detection)    (Webhook / Stream listener)
```

1. **External Satellite Ingestion:** New ingestion jobs simply POST valid payloads to `POST /api/v1/observations`, leveraging the existing validation engine.
2. **Computer Vision & Thermal Anomaly Detection:** Background analytical scripts can process image paths stored in `Observation` and post anomaly scores back into the `thermal_metadata` facet payload.
3. **Advanced GIS / Planetary Mapping:** Coordinate data is stored with explicit body datum attributes, enabling seamless expansion to web GIS services or GeoJSON overlays.

