# Domain Model Specification
## Volcanic Image/Data Observatory (VIDO)

---

## 1. Executive Summary

The central conceptual challenge in the Volcanic Image/Data Observatory (VIDO) is modeling **heterogeneous scientific observations** across diverse planetary environments (Earth, Mars, Io, Venus) without forcing rigid table schemas or creating bloated class inheritance trees.

This domain model resolves this challenge through a hybrid pattern combining strong entity relationships for core concepts (Celestial Bodies, Volcanic Systems, Events, and Observations) with a **Composition & Strategy-based Facet Validation Pattern** for metadata. An observation represents a single observation event that may contain zero or more metadata facets (`IMAGE`, `THERMAL`, `PLANETARY_ORBITAL`) within a composite JSON payload.

---

## 2. Conceptual Domain Diagram (Entity-Relationship & Class View)

```
+-------------------+          1..*        +--------------------+
|   CelestialBody   | -------------------< |   VolcanicSystem   |
+-------------------+                      +--------------------+
| id                |                      | id                 |
| name              |                      | celestial_body_id  |
| body_type         |                      | name               |
| mean_radius_km    |                      | latitude           |
| coordinate_system |                      | longitude          |
| long_convention   |                      | elevation_m        |
+-------------------+                      | region             |
                                           | volcanic_type      |
                                           | status             |
                                           +--------------------+
                                             |                |
                                        1..* |                | 1..*
                                             v                v
+-----------------------+          1..*    +-------------+    +---------------+
|   ObservationSource   | ----------------<| Observation |    | VolcanicEvent |
+-----------------------+                  +-------------+    +---------------+
| id                    |                  | id          |    | id            |
| name                  |                  | system_id   |    | system_id     |
| platform_type         |                  | source_id   |    | title         |
| operator_agency       |                  | timestamp   |    | start_time    |
+-----------------------+                  | lat (null)  |    | end_time(null)|
                                           | long (null) |    | vei_rating    |
                                           | metadata    |    | event_type    |
                                           +-------------+    +---------------+
                                                  |                   |
                                                  +---------+---------+
                                                            |
                                                            v 0..*
                                               +-------------------------+
                                               | ObservationEventLink    |
                                               +-------------------------+
                                               | id                      |
                                               | observation_id          |
                                               | event_id                |
                                               | relationship_type       |
                                               | temporal_offset_hours   |
                                               +-------------------------+
```

---

## 3. Core Entity Definitions

### 3.1 `CelestialBody`
- **Description:** Represents a planet, moon, or astronomical body hosting volcanic activity.
- **Attributes:**
  - `id`: String (Primary Key, e.g., `"earth"`, `"mars"`, `"io"`, `"venus"`)
  - `name`: String (e.g., `"Earth"`, `"Mars"`, `"Io"`)
  - `body_type`: Enum (`PLANET`, `MOON`)
  - `mean_radius_km`: Float
  - `coordinate_system`: String (e.g., `"WGS84"`, `"IAU_2000_MARS"`, `"IAU_2000_IO"`)
  - `longitude_convention`: Enum (`EAST_WEST_180` [-180.0° to +180.0°], `POSITIVE_EAST_360` [0.0° to 360.0°])
- **Rationale:** Explicitly defining coordinate reference frames and longitude conventions allows planetary coordinate systems (e.g., IAU 0°–360° Positive East) to coexist seamlessly with Earth WGS84 coordinates without forcing Earth-centric assumptions.

### 3.2 `VolcanicSystem`
- **Description:** A localized volcanic complex, vent, patera, shield, or caldera.
- **Attributes:**
  - `id`: String (UUID or slug, e.g., `"volc-etna"`, `"volc-olympus-mons"`)
  - `celestial_body_id`: Foreign Key → `CelestialBody.id`
  - `name`: String (e.g., `"Mount Etna"`, `"Olympus Mons"`, `"Loki Patera"`)
  - `latitude`: Float (-90.0 to +90.0 degrees)
  - `longitude`: Float (Conforming to parent `CelestialBody.longitude_convention`: -180.0 to +180.0 degrees for Earth, 0.0 to 360.0 degrees Positive East for planetary bodies)
  - `elevation_m`: Float (Surface elevation relative to planetary datum in meters)
  - `region`: String (e.g., `"Sicily, Italy"`, `"Tharsis Montes"`, `"Tyre Region"`)
  - `volcanic_type`: String (e.g., `"Stratovolcano"`, `"Shield Volcano"`, `"Patera"`)
  - `status`: Enum (`ACTIVE`, `DORMANT`, `EXTINCT`, `UNKNOWN`)
- **Rationale:** Acts as the primary anchor point connecting space (coordinates), time (events), and scientific observations.

### 3.3 `ObservationSource`
- **Description:** The physical platform, instrument, sensor, or agency responsible for capturing observation data.
- **Attributes:**
  - `id`: String (e.g., `"src-sentinel-2"`, `"src-mro-ctx"`, `"src-ground-obs"`)
  - `name`: String (e.g., `"Sentinel-2 MSI"`, `"MRO Context Camera"`, `"Etna Thermal WebCam"`)
  - `platform_type`: Enum (`SATELLITE_ORBITER`, `GROUND_OBSERVATORY`, `AIRBORNE_DRONE`, `FIELD_STATION`)
  - `operator_agency`: String (e.g., `"ESA"`, `"NASA / JPL"`, `"INGV"`)
- **Rationale:** Decouples sensor platform attributes from the individual observation records.

### 3.4 `Observation` (Base Wrapper Entity)
- **Description:** Represents a single scientific observation event tied to a volcanic system at a specific timestamp and optional spatial location.
- **Attributes:**
  - `id`: String (UUID)
  - `volcanic_system_id`: Foreign Key → `VolcanicSystem.id`
  - `source_id`: Foreign Key → `ObservationSource.id`
  - `timestamp`: Datetime (ISO-8601 UTC)
  - `latitude`: Float (Optional / Nullable override; if NULL, spatial visualization falls back to `VolcanicSystem.latitude`)
  - `longitude`: Float (Optional / Nullable override; if NULL, spatial visualization falls back to `VolcanicSystem.longitude`)
  - `summary`: String
  - `media_path`: String (Optional / Nullable path or URL to associated asset e.g., image file, plot asset)
  - `metadata`: Dynamic Dictionary / JSON Object containing active metadata facet payloads (`image_metadata`, `thermal_metadata`, `orbital_metadata`)
- **Spatial Fallback & Unlocated Rule:**
  - If `latitude` and `longitude` are provided, use them for spatial visualization.
  - If `latitude` and `longitude` are NULL but parent `VolcanicSystem` coordinates exist, spatial views fall back to the `VolcanicSystem` coordinates (with a visual base indicator).
  - If neither observation nor volcano coordinates are available, the observation is listed in the "Unlocated Observations" drawer without inventing position data.

---

## 4. Modular Metadata Facet Schemas

Rather than forcing observations into a single mutually exclusive type enum (which prevents spacecraft observations from storing both orbital geometry and thermal radiometry), VIDO uses **Composite Metadata Facets**.

An `Observation` payload's `metadata` JSON field can contain any combination of validated facet payloads:

```json
{
  "active_facets": ["IMAGE", "THERMAL", "PLANETARY_ORBITAL"],
  "image_metadata": {
    "spectral_band": "NEAR_INFRARED",
    "spatial_resolution_m": 10.0,
    "cloud_cover_percentage": 4.5,
    "file_format": "PNG",
    "image_dimensions": {"width": 1920, "height": 1080},
    "sun_elevation_angle_deg": 48.2
  },
  "thermal_metadata": {
    "brightness_temperature_kelvin": 785.4,
    "ambient_temperature_kelvin": 288.1,
    "thermal_flux_mw": 142.6,
    "anomaly_flag": true,
    "sensor_wavelength_um": 10.8,
    "saturation_threshold_exceeded": false
  },
  "orbital_metadata": {
    "spacecraft_altitude_km": 310.5,
    "solar_incidence_angle_deg": 62.1,
    "emission_angle_deg": 12.4,
    "phase_angle_deg": 74.5,
    "target_planetary_datum": "IAU_MARS_2000"
  }
}
```

### 4.1 Facet Categories:
1. **`IMAGE` (`image_metadata`):** Spectral band, spatial resolution, cloud cover, dimensions, sun elevation.
2. **`THERMAL` (`thermal_metadata`):** Brightness temperature, ambient temperature, thermal flux, anomaly flag, wavelength.
3. **`PLANETARY_ORBITAL` (`orbital_metadata`):** Spacecraft altitude, solar incidence angle, emission angle, phase angle, planetary datum.

---

## 5. Volcanic Event & Association Model

### 5.1 `VolcanicEvent`
- **Description:** A physical eruptive episode, thermal unrest period, ash plume outbreak, or seismic swarm recorded at a volcanic system.
- **Attributes:**
  - `id`: String (UUID)
  - `volcanic_system_id`: Foreign Key → `VolcanicSystem.id`
  - `title`: String (e.g., `"Etna December 2020 Paroxysm"`, `"Olympus Mons Caldera Collapse Episode"`)
  - `event_type`: Enum (`ERUPTION`, `ASH_PLUME`, `THERMAL_ANOMALY`, `LAVA_FLOW`, `GAS_DEGASSING`)
  - `start_time`: Datetime (ISO-8601 UTC)
  - `end_time`: Datetime (ISO-8601 UTC, optional / NULL for active ongoing events)
  - `vei_rating`: Integer (Volcanic Explosivity Index 0–8, optional / NULL for non-terrestrial or unrated effusive events)
  - `description`: String
- **Ongoing Event Rule:** If `end_time` is `NULL`, the event is classified as ongoing. Timeline visualizations render ongoing events as open-ended spans extending to the current timestamp.

### 5.2 `ObservationEventLink` (Junction / Association Entity)
- **Description:** Captures the contextual temporal/spatial relationship between an `Observation` and a `VolcanicEvent`.
- **Attributes:**
  - `id`: String (UUID)
  - `observation_id`: Foreign Key → `Observation.id`
  - `event_id`: Foreign Key → `VolcanicEvent.id`
  - `relationship_type`: Enum (`PRE_ERUPTIVE`, `CO_ERUPTIVE`, `POST_ERUPTIVE`, `UNRELATED`)
  - `temporal_offset_hours`: Float (Calculated difference between observation timestamp and event start time)
  - `notes`: String
- **Rationale:** An observation (e.g., satellite scene) may capture evidence relevant to multiple events or serve as a baseline. An explicit junction entity preserves 1:N and N:M relationships cleanly.

---

## 6. Architectural Strategy: Composite Facets vs Single-Type Inheritance

### Why Composite Metadata Facets are Chosen:

1. **Avoidance of Rigid Single-Type Constraints:** Real-world planetary orbiter observations (e.g., MRO THEMIS) combine orbital geometry, multispectral images, and thermal measurements. Composite facets allow an observation to validate all active facet payloads without forcing the user to pick one type.
2. **Schema Validation at Application Boundary:** Each facet payload is validated by a focused Pydantic facet schema (`ImageFacetSchema`, `ThermalFacetSchema`, `OrbitalFacetSchema`).
3. **Coherent Querying Across Space and Time:** Standard queries filter on top-level `Observation` attributes (indexed `timestamp`, `volcanic_system_id`, `latitude`, `longitude`). Specific metadata filtering occurs within indexed JSON paths.

