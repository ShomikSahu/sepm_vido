# Phase 2 Data Layer Implementation Specification

## 1. Package & Component Architecture

```
app/
├── config.py                                 # Project path & database configuration
├── db/
│   ├── database.py                           # SQLite connection manager & transaction context
│   └── schema.py                             # Normalized DDL table definitions
├── models/
│   ├── celestial_body.py                     # CelestialBody & LongitudeConvention enum
│   ├── volcanic_system.py                    # VolcanicSystem & SystemStatus enum
│   ├── observation_source.py                 # ObservationSource & PlatformType enum
│   ├── observation.py                        # Observation entity & spatial fallback resolver
│   ├── volcanic_event.py                     # VolcanicEvent, EventType enum & ongoing event flag
│   ├── observation_event_link.py             # ObservationEventLink & RelationshipType enum
│   └── facets.py                             # Composite metadata facet schemas (Image, Thermal, Orbital)
└── repositories/
    ├── base.py                               # Base repository class
    ├── celestial_body_repository.py          # CelestialBody data access
    ├── volcanic_system_repository.py         # VolcanicSystem data access with coordinate validation
    ├── observation_source_repository.py      # ObservationSource data access
    ├── observation_repository.py             # Observation data access & facet filtering
    ├── volcanic_event_repository.py          # VolcanicEvent data access & ongoing event queries
    └── observation_event_link_repository.py # ObservationEventLink data access
scripts/
└── seed_data.py                              # Curated Earth + Planetary seed dataset generator
tests/
├── conftest.py                               # Pytest fixtures and in-memory DB isolation
├── test_models.py                            # Domain model unit tests
├── test_repositories.py                      # Database & repository integration tests
├── test_seed_data.py                         # Seed data integrity tests
└── test_domain_rules.py                      # Explicit domain rule verification tests
```

---

## 2. Database Schema Summary

The database schema is fully normalized in SQLite 3 (`data/vido.db`):

| Table Name | Primary Key | Key Foreign Keys | Purpose |
| :--- | :--- | :--- | :--- |
| `celestial_bodies` | `id` | None | Stores celestial body metadata and coordinate conventions (`EAST_WEST_180` vs `POSITIVE_EAST_360`). |
| `volcanic_systems` | `id` | `celestial_body_id` | Anchor entity for volcanic features, calderas, shields, and paterae. |
| `observation_sources` | `id` | None | Physical platform or sensor instrument (orbiters, ground observatories). |
| `observations` | `id` | `volcanic_system_id`, `source_id` | Core observation records holding universal spatial-temporal fields and validated JSON facet metadata. |
| `volcanic_events` | `id` | `volcanic_system_id` | Physical volcanic phenomena occurring over time (supports ongoing events where `end_time` IS NULL). |
| `observation_event_links` | `id` | `observation_id`, `event_id` | Junction entity for N:M contextual relationships (`PRE_ERUPTIVE`, `CO_ERUPTIVE`, `POST_ERUPTIVE`, `UNRELATED`). |

---

## 3. Core Domain Rules Implemented

1. **No `EVENT_RECORD` Observation Type**: Observations represent evidence/measurements, while `VolcanicEvent` represents physical phenomena. Connected via `ObservationEventLink`.
2. **Composite Metadata Facets**: Observations support any combination of active facets (`IMAGE`, `THERMAL`, `PLANETARY_ORBITAL`) within the `metadata` JSON object.
3. **Dual Coordinate Conventions**: Earth WGS84 (`-180°` to `+180°`) and Planetary IAU standards (`0°` to `360°` Positive East) are validated against parent `CelestialBody` definitions.
4. **Spatial Coordinate Fallback**: Resolves spatial location in order: explicit observation coordinates → parent volcano coordinates → unlocated.
5. **Ongoing Volcanic Events**: `VolcanicEvent.end_time = NULL` explicitly identifies active ongoing events (`is_ongoing == True`).
6. **Optional VEI Rating**: `vei_rating` is optional and `NULL` for planetary or non-explosive effusive events.
7. **Relationship Classifications**: Supports `PRE_ERUPTIVE`, `CO_ERUPTIVE`, `POST_ERUPTIVE`, and `UNRELATED`.
