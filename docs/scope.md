# Project Scope & MVP Boundary Specification
## Volcanic Image/Data Observatory (VIDO)

---

## 1. Executive Summary & Scope Strategy

The goal of Phase 1 Scope Definition is to establish a **crisp, achievable Minimum Viable Product (MVP)** for an undergraduate Software Engineering and Project Management (SEPM) term project. The MVP demonstrates rigorous requirements engineering, domain modeling, metadata facet validation, and spatial-temporal exploration without introducing unmanageable enterprise risks.

---

## 2. In-Scope MVP Capabilities

The MVP focuses on solving the core problem: *representing, validating, storing, querying, and exploring heterogeneous observations across space and time.*

### Core MVP Feature Modules

1. **Multi-Planet Volcanic System Browser:**
   - Interactive browsing and keyword search for volcanic systems across Earth, Mars, Io, and Venus.
   - Profile view displaying planetary coordinates, elevation, region, coordinate system, and geological classification.

2. **Heterogeneous Observation Repository & Facet Payload Validation:**
   - Support for three observation metadata facets: `IMAGE`, `THERMAL`, and `PLANETARY_ORBITAL` within composite observation payloads.
   - Pydantic facet schema validation rejecting illegal payloads before storage.
   - Full metadata inspection dialog displaying active facets.

3. **Multi-Criteria Filter Engine:**
   - Filtering by volcanic system, celestial body, date range, metadata facet category (`IMAGE`, `THERMAL`, `PLANETARY_ORBITAL`), and data source.

4. **Dual-Lane Chronological Timeline Visualizer:**
   - Synchronized visual timeline displaying eruptive events alongside observations (rendering ongoing events with NULL `end_time` as open-ended spans).
   - Interactive event/observation contextual node selection.

5. **Spatial Coordinate Map / Grid Renderer:**
   - Visualization of observations and volcanoes using body-appropriate coordinates (Leaflet.js for Earth WGS84 -180°..+180°, lightweight Canvas/SVG grids for planetary 0°..360° Positive East).
   - Coordinate fallback resolution: if observation coordinates are NULL, fall back to volcano coordinates; if both are NULL, display in unlocated drawer.

6. **Observation-Event Context Linker:**
   - Ability to associate observations with volcanic eruptive events with relationship tags (`PRE_ERUPTIVE`, `CO_ERUPTIVE`, `POST_ERUPTIVE`, `UNRELATED`).

7. **Curated Multi-Body Seed Dataset:**
   - Pre-populated sample dataset featuring Earth volcanoes (Etna, Kilauea), Martian features (Olympus Mons, Hecates Tholus), Io features (Loki Patera, Pele), and Venus features (Maat Mons).

---

## 3. Explicitly Out-of-Scope (Future Extensions)

To safeguard project timelines, the following capabilities are **explicitly excluded from the MVP phase**:

| Out-of-Scope Feature | Reason for Exclusion | Future Architecture Path |
| :--- | :--- | :--- |
| **External Live Satellite Ingestion** | Network dependency risk, API rate limits | REST Ingestion Service Hook |
| **Real-Time Data Feeds / Webhooks** | Infrastructure complexity | Event-driven queue (e.g., Celery/Redis) |
| **Computer Vision / Image Analysis** | High research overhead | Standalone Python CV worker module |
| **Automated Thermal Anomaly Detection** | Algorithm tuning complexity | Background metadata analytical engine |
| **Full GIS Map Server (GeoServer / ArcMap)** | Excessive framework bloat | Leaflet/WMS layer client integration |
| **Cloud Infrastructure / Kubernetes** | DevOps overhead | Docker containerized deployment |
| **User Authentication / Role Management** | Out of scope for SEPM core focus | OAuth2 / JWT FastAPI middleware |
| **React / Angular / Vue Frameworks** | Dependency build tool overhead | SPA single-page architecture |

---

## 4. MoSCoW Scope Prioritization Matrix

```
MUST HAVE (MVP Core)
--------------------+------------------------------------------------------
- FR-01: Browse & Search Volcanic Systems
- FR-02: Display Volcanic System Profile
- FR-03: Store Composite & Heterogeneous Observations
- FR-04: Multi-Criteria Filter Engine
- FR-05: View Observation Details & Metadata Facets
- FR-06: Chronological Timeline Visualization (including ongoing events)
- FR-07: Spatial Coordinate Mapping & Fallback Rules
- FR-08: Metadata Payload Validation Engine
- FR-09: Observation-Event Association (PRE/CO/POST/UNRELATED)
- FR-10: Dual Terrestrial & Planetary Support (-180°..+180° / 0°..360°)
- Curated Multi-Body Seed Dataset (Etna, Kilauea, Olympus Mons, Loki Patera)

SHOULD HAVE (Target Release Polish)
----------------------------------+----------------------------------------
- Interactive seed data management CLI helper script
- Timeline zoom/pan controls
- Metadata export to JSON format

COULD HAVE (Bonus Features)
--------------------------+------------------------------------------------
- Export spatial view as GeoJSON
- Observation count analytics dashboard widget

WON'T HAVE (Strictly Out of Scope for MVP)
----------------------------------------+----------------------------------
- Live satellite streaming, computer vision, machine learning, auth.
```

---

## 5. Scope Management & Change Control Process

To prevent scope creep during development:

1. **Scope Baseline Sign-off:** Any proposed feature addition must be documented against existing FRs.
2. **Feature Freeze:** Core feature development closes at Phase 5. Phase 6 is strictly reserved for verification, bug fixes, and documentation audit.
3. **Change Impact Evaluation:** Any request to modify schema structures or add observation facets must be evaluated for impact on validation schemas and existing API contracts.

