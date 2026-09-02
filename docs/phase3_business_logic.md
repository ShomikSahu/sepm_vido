# Phase 3 Business Logic & Service Layer Specification

## 1. Overview & Service Responsibilities

Phase 3 introduces the business logic and service orchestration layer for the Volcanic Image/Data Observatory (VIDO). It isolates scientific domain rules, schema validation, dynamic coordinate system resolution, spatial location fallbacks, and chronological timeline aggregation from both database queries (Phase 2 repositories) and future API/UI controllers (Phase 4 & 5).

```
[ Presentation Layer / REST API ] (Phase 4 & 5)
                │
                ▼
+-------------------------------------------------------------+
|                  BUSINESS LOGIC / SERVICE LAYER             |
|  - ValidationService: Composite Metadata & Ingestion        |
|  - CoordinateService: Dynamic Celestial Body Conventions    |
|  - SpatialService: Coordinate Resolution & Fallbacks        |
|  - EventService: Eruptive Event & Link Management          |
|  - TimelineService: Chronological Aggregation & Ongoing Evts|
+-------------------------------------------------------------+
                │
                ▼
[ Repository & Database Persistence Layer ] (Phase 2)
```

---

## 2. Service Architecture & Component Responsibilities

### 2.1 `CoordinateService` (`app/services/coordinate_service.py`)
- **Responsibility:** Enforces body-specific spatial coordinate reference conventions.
- **Rules Enforced:**
  - **Earth WGS84 (`EAST_WEST_180`):** Latitude `[-90.0°, +90.0°]`, Longitude `[-180.0°, +180.0°]`.
  - **Planetary Positive East (`POSITIVE_EAST_360`):** Latitude `[-90.0°, +90.0°]`, Longitude `[0.0°, 360.0°]`.
- **Dynamic Resolution:** Rather than hardcoding celestial body names (e.g., `"Earth"` vs `"Mars"`), the service dynamically retrieves `CelestialBody.longitude_convention` from the `CelestialBodyRepository`.

### 2.2 `ValidationService` (`app/services/validation_service.py`)
- **Responsibility:** Validates observation submission payloads before database persistence.
- **Core Checks:**
  - Required top-level attributes: `id`, `volcanic_system_id`, `source_id`, `timestamp` (validates ISO-8601 UTC string format), `summary`.
  - Referential integrity: verifies existence of target `VolcanicSystem` and `ObservationSource` in repositories.
  - Coordinate checking: delegates lat/long pair checking to `CoordinateService`.
- **Composite Metadata Validation:**
  - Validates `metadata` JSON documents containing `active_facets` (`IMAGE`, `THERMAL`, `PLANETARY_ORBITAL`).
  - **Non-Mutually Exclusive:** A single observation can validate and store multiple facets simultaneously (e.g. `ImageFacet` + `ThermalFacet` + `OrbitalFacet`).
  - Rejects missing required facet fields, negative Kelvin temperatures, out-of-bounds cloud cover (> 100%), and illegal orbital angles (> 180°).

### 2.3 `SpatialService` (`app/services/spatial_service.py`)
- **Responsibility:** Resolves spatial location for presentation layers using approved fallback rules.
- **Approved Fallback Order:**
  1. **Explicit Observation Coordinates (`OBSERVATION`):** Used if `latitude` and `longitude` are present on the `Observation`.
  2. **Parent Volcanic System Coordinates (`VOLCANO_FALLBACK`):** Used if `Observation` coordinates are `NULL` but `VolcanicSystem` coordinates exist.
  3. **Neither Available (`UNLOCATED`):** Assigned when neither coordinate pair is available, placing the observation entry in an unlocated listing without inventing position data.
- **Output:** Returns structured spatial payloads containing `spatial_source` tags, latitude, longitude, and parent celestial body datum metadata.

### 2.4 `EventService` (`app/services/event_service.py`)
- **Responsibility:** Manages physical eruptive events and observation-event relationship links.
- **Rules Enforced:**
  - Distinguishes `Observation` (measurement/evidence at a timestamp) from `VolcanicEvent` (physical phenomenon occurring over a duration).
  - Validates timestamp ordering (`start_time <= end_time` when `end_time` is provided).
  - Maintains optional `vei_rating` (0–8 for explosive Earth eruptions, `NULL` for effusive or non-terrestrial events).
  - Calculates `temporal_offset_hours` automatically between `observation.timestamp` and `event.start_time`.
  - Links entities via `ObservationEventLink` using approved relationship types (`PRE_ERUPTIVE`, `CO_ERUPTIVE`, `POST_ERUPTIVE`, `UNRELATED`).
  - Enforces database unique link constraint (`UNIQUE(observation_id, event_id)`).

### 2.5 `TimelineService` (`app/services/timeline_service.py`)
- **Responsibility:** Aggregates multi-entity chronological timeline views for a selected volcanic system.
- **Ongoing Event Handling:**
  - Events with `end_time = NULL` are treated as active ongoing events (`is_ongoing == True`).
  - The timeline service provides a `display_end_time` equal to the current reference timestamp for open-ended timeline rendering, while preserving `NULL` in the underlying domain object and database.
- **Chronological Sorting:** Generates an interleaved chronological feed sorting both events (`start_time`) and observations (`timestamp`).

---

## 3. Automated Test Strategy & Verification

The Phase 3 test suite ([`tests/test_services.py`](file:///c:/Users/91979/Desktop/Volcanic_Image_Data_Observatory_SEPM_PROJECT/tests/test_services.py)) provides comprehensive verification across 5 major categories:

1. **Composite Metadata Validation:** Verified valid `IMAGE`, `THERMAL`, `PLANETARY_ORBITAL` payloads, multi-facet observations, negative Kelvin rejection, and missing field rejection.
2. **Body-Specific Coordinate Validation:** Verified Earth [-180°..+180°] vs Mars [0°..360°] longitude rules and latitude boundary checks [-90°..+90°].
3. **Spatial Coordinate Fallback:** Verified resolution across explicit observation coords (`OBSERVATION`), parent volcano fallback (`VOLCANO_FALLBACK`), and missing coords (`UNLOCATED`).
4. **Timeline Aggregation:** Verified bounded events, ongoing events (`end_time = NULL`), display span resolution, and strict chronological sorting.
5. **Event/Observation Associations:** Verified `PRE_ERUPTIVE`, `CO_ERUPTIVE`, `POST_ERUPTIVE`, `UNRELATED` relationship tags, automatic temporal offset calculations, and duplicate link prevention.
