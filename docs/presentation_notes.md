# Speaker Notes & Presentation Script
## Volcanic Image/Data Observatory (VIDO) - SEPM Evaluation

---

## Presentation Overview & Timing Guide

- **Total Duration:** 12–15 Minutes
- **Target Audience:** SEPM Evaluation Committee & Viva Evaluators
- **Core Framing:** Software Engineering & Project Management (SEPM) evaluation case study. Volcanology is the scientific application domain providing operational context; software design, architecture, requirements engineering, domain modeling, and verification are the primary subject.

---

## Slide 1: Title & Project Overview
- **Slide Title:** Volcanic Image/Data Observatory (VIDO)
- **Estimated Time:** 1.0 Minute
- **Speaker Script:**
  > "Good day, members of the evaluation committee. Welcome to our SEPM final presentation on the **Volcanic Image/Data Observatory (VIDO)**.
  > VIDO is a lightweight scientific software system engineered to organize, validate, relate, and explore heterogeneous terrestrial and planetary volcanology observations.
  > In this presentation, we demonstrate a professionally engineered software system designed for a complex scientific application domain—focusing on requirements engineering, UML modeling, layered architecture, composite metadata design, trade-offs, and empirical test verification."
- **Key Talking Points:**
  - Project Title: Volcanic Image/Data Observatory (VIDO).
  - Subject Context: Software Engineering & Project Management (SEPM) Evaluation Case Study.
  - Domain Scope: Terrestrial (Earth WGS84) & Planetary Volcanology (Mars, Io, Venus).
  - Verification Baseline: Core MVP fully implemented and verified with 37 passing automated tests.

---

## Slide 2: Problem Definition (Software Engineering Framing)
- **Slide Title:** 1. Problem Definition: Heterogeneous Scientific Data Management
- **Estimated Time:** 1.5 Minutes
- **Speaker Script:**
  > "From a software engineering perspective, scientific research environments present complex data management challenges. In volcanology, observations originate from heterogeneous streams—including optical imagery, thermal radiometry, orbital geometry, and spatial point coordinates across multiple celestial targets.
  > Our core engineering question is: *'How can heterogeneous scientific observations be represented, validated, related, and explored in a coherent and maintainable software system?'*
  > Key software engineering challenges include coordinate frame disparities between Earth WGS84 (-180° to +180°) and Planetary IAU (0° to 360° Positive East) conventions, schema rigidity caused by forcing multi-sensor attributes into flat SQL tables, and entity conflation when snapshot evidence is confused with physical eruptive events."
- **Key Talking Points:**
  - Core Engineering Question: Coherent representation, validation, and maintenance of heterogeneous observational data.
  - Domain Challenges: Earth WGS84 vs. Planetary IAU coordinate frame disparities.
  - Software Anti-Patterns Prevented: Schema bloat, sparse NULL columns, and entity conflation.

---

## Slide 3: Requirements Engineering
- **Slide Title:** 2. Requirements Engineering: Functional & Non-Functional Specifications
- **Estimated Time:** 1.0 Minute
- **Speaker Script:**
  > "We categorized our system requirements into Functional Requirements (FR) and Non-Functional Requirement (NFR) targets.
  > Functional requirements govern observation management across planetary bodies (FR-01), multi-criteria retrieval (FR-02), explicit observation-event association (FR-03), spatial coordinate exploration with fallback rules (FR-04), synchronized dual-lane timeline feeds (FR-05), and domain metadata validation (FR-06).
  > Non-functional targets emphasize maintainability through a 5-layer pipeline, extensibility via modular metadata facet schemas, testability of decoupled domain services, data integrity via Pydantic schema boundaries, and lightweight modular execution without heavy build tools."
- **Key Talking Points:**
  - FR Highlights: Observation management, retrieval, event association, spatial fallback, timeline feed, schema validation.
  - NFR Highlights: Layered maintainability, facet schema extensibility, testability, data integrity, modular execution.

---

## Slide 4: Use Case Analysis & UML Use Case Diagram
- **Slide Title:** 3. Use Case Analysis & Mandatory UML Use Case Diagram
- **Estimated Time:** 1.5 Minutes
- **Speaker Script:**
  > "The use-case model translates functional requirements into observable interactions between the user and VIDO.
  > On the right is our mandatory UML Use Case Diagram, showing the primary actor 'User', the system boundary 'Volcanic Image/Data Observatory (VIDO)', and simple associations with the six core use cases: UC-01 Browse Celestial Systems, UC-02 Search & Filter Observations, UC-03 Inspect Metadata Payloads, UC-04 Associate Observations with Events, UC-05 Explore Synchronized Timeline, and UC-06 Explore Spatial Coordinates.
  > The diagram uses standard UML notation without non-standard relationship extensions."
- **Key Talking Points:**
  - Mandatory Artefact: Genuine UML Use Case Diagram (PlantUML rendered).
  - Six Core Use Cases: UC-01 through UC-06 traceable to functional requirements.
  - Explanatory Framing: Translates functional requirements into observable user-system interactions.

---

## Slide 5: Requirements Traceability Matrix
- **Slide Title:** 4. Requirements Traceability: FR → UC → API → Service → Test
- **Estimated Time:** 1.0 Minute
- **Speaker Script:**
  > "To ensure software engineering rigor, we established end-to-end traceability across verified codebase components.
  > Every functional requirement traces cleanly from specification to automated test verification:
  > FR-01 maps to UC-02/03, POST /api/v1/observations, ValidationService, ObservationRepository, and tests in test_models.py and test_api.py.
  > FR-02 maps to UC-02, GET /api/v1/observations, ValidationService, ObservationRepository, and test_api.py.
  > FR-03 maps to UC-04, POST /api/v1/observation-event-links, EventService, ObservationEventLinkRepository, and test_domain_rules.py.
  > FR-04 maps to UC-06, GET /api/v1/systems/{id}/spatial, SpatialService/CoordinateService, VolcanicSystemRepository/ObservationRepository, and test_repositories.py.
  > FR-05 maps to UC-05, GET /api/v1/systems/{id}/timeline, TimelineService, VolcanicEventRepository/ObservationRepository, and test_services.py.
  > FR-06 maps to UC-02/03, Pydantic API Schemas, ValidationService/CoordinateService, and test_models.py."
- **Key Talking Points:**
  - Traceability Pipeline: Requirement → Use Case → API Endpoint → Service → Repository → Pytest Verification.
  - Verified Codebase Classes: ValidationService, CoordinateService, SpatialService, EventService, TimelineService, ObservationRepository, VolcanicSystemRepository, VolcanicEventRepository, ObservationEventLinkRepository.

---

## Slide 6: Software Design & UML Class Diagram
- **Slide Title:** 5. Software Design & Mandatory UML Class Diagram
- **Estimated Time:** 1.5 Minutes
- **Speaker Script:**
  > "On Slide 6, we present our core domain design and mandatory UML Class Diagram.
  > The diagram models six core classes: CelestialBody, VolcanicSystem, ObservationSource, Observation, VolcanicEvent, and ObservationEventLink.
  > Multiplicities reflect the domain relationships: CelestialBody 1 to * VolcanicSystem, VolcanicSystem 1 to * Observation, ObservationSource 1 to * Observation, Observation 1 to * ObservationEventLink, and VolcanicEvent 1 to * ObservationEventLink.
  > A crucial design principle is: **Observation ≠ VolcanicEvent**. Separating observations from physical events preserves distinct lifecycles and attributes while ObservationEventLink provides explicit association."
- **Key Talking Points:**
  - Mandatory Artefact: Genuine UML Class Diagram (PlantUML rendered).
  - Conceptual Boundary: Observation (scientific evidence snapshot) vs. VolcanicEvent (physical episode over time).
  - Explicit Association: ObservationEventLink models many-to-many relationship with relationship classification tags.

---

## Slide 7: Composite Metadata Facet Design
- **Slide Title:** 6. Composite Metadata Facet Architecture
- **Estimated Time:** 1.0 Minute
- **Speaker Script:**
  > "Rather than using rigid table subclassing or mutually exclusive type enums, VIDO implements a **Composite Metadata Facet Design**.
  > An Observation encapsulates zero or more active metadata facets: `IMAGE`, `THERMAL`, and `PLANETARY_ORBITAL`.
  > On the right, the JSON excerpt from Olympus Mons (Mars) shows optical image resolution, thermal brightness temperature, and planetary orbital geometry parameters operating in a single composite payload, validated by Pydantic v2 schemas at API boundaries."
- **Key Talking Points:**
  - Composite Facet Synergy: Observations combine IMAGE, THERMAL, and PLANETARY_ORBITAL facets dynamically.
  - Standardized Terminology: `PLANETARY_ORBITAL` standardized across API and documentation.
  - Schema Integrity: Pydantic v2 validates nested payload structures and attribute ranges at API boundaries.

---

## Slide 8: System Architecture
- **Slide Title:** 7. System Architecture: 5-Layer Software Pipeline
- **Estimated Time:** 1.0 Minute
- **Speaker Script:**
  > "VIDO uses a clean 5-layer software architecture enforcing separation of concerns:
  > 1. Presentation Layer: Vanilla HTML5/CSS3/ES6 JS with Leaflet maps and Canvas 2D grids.
  > 2. API Layer: FastAPI REST server executing Pydantic schema boundary validation and serving OpenAPI docs.
  > 3. Service Layer — Business & Domain Logic: Executes domain/business validation, coordinate resolution, spatial fallback rules, event rules, and timeline aggregation.
  > 4. Repository Layer: Data access abstraction isolating SQL operations.
  > 5. Database Layer: SQLite 3 engine with JSON1 metadata support."
- **Key Talking Points:**
  - 5-Layer Stack: Presentation → API → Services → Repositories → Database.
  - Pydantic Boundary: API layer validates schemas; Service layer handles domain business rules and spatial/timeline logic.

---

## Slide 9: Design Decisions & Engineering Trade-offs
- **Slide Title:** 8. Design Decisions & Engineering Trade-offs
- **Estimated Time:** 1.5 Minutes
- **Speaker Script:**
  > "Every architectural trade-off was driven by concrete software engineering rationale:
  > Relational SQL core + JSON metadata fields prevents schema rigidity while maintaining fast query capability.
  > Decoupling observation snapshots from eruptive events prevents data loss when linking multi-event observations.
  > Body-specific coordinate rules prevent projection errors between Earth WGS84 and Planetary IAU frames.
  > Explicit 3-step spatial fallback prevents coordinate fabrication for unlocated entries.
  > Service/repository abstraction prevents SQL leaks into API controllers."
- **Key Talking Points:**
  - Rationale Matrix: Problem → Design Decision → Software Engineering Benefit.

---

## Slide 10: Validation & Business Rules
- **Slide Title:** 9. Validation & Business Rules Architecture
- **Estimated Time:** 1.0 Minute
- **Speaker Script:**
  > "VIDO enforces validation across two distinct architectural tiers:
  > **Tier 1 (API Schema Validation):** Handled by Pydantic v2 at API entry points, validating data types, structural presence, and numeric ranges.
  > **Tier 2 (Domain & Business Validation):** Handled by the Service Layer, enforcing celestial body coordinate bounds (Earth WGS84 vs. Mars/Io IAU 360°), temporal sequence rules (`start_time <= end_time`), relationship tag classification, and spatial fallback rules."
- **Key Talking Points:**
  - Clear Distinction: API/Schema structural validation vs. Domain business rules enforcement.

---

## Slide 11: Development Process (SDLC Workflow)
- **Slide Title:** 10. Development Process: Phased SDLC Workflow
- **Estimated Time:** 1.0 Minute
- **Speaker Script:**
  > "We executed the project through an 8-phase development lifecycle:
  > 1. Problem Definition & SRS, 2. Requirements Audit, 3. Data Layer & Entities, 4. Business Logic Services, 5. API Layer, 6. Frontend Interface, 7. Automated Verification, and 8. Presentation & QC.
  > Controlled progression ensured each phase was verified against project baseline facts before advancing."
- **Key Talking Points:**
  - Phased Methodology: 8 structured phases with continuous iterative verification.

---

## Slide 12: Scope & Risk Management
- **Slide Title:** 11. Scope Control & Risk Management Strategy
- **Estimated Time:** 1.0 Minute
- **Speaker Script:**
  > "Project management required deliberate scope control.
  > Our implemented MVP scope includes the unified domain model, multi-body CRS rules, composite facet validation, 5-layer pipeline, dual-lane timeline visualizer, spatial fallback engine, REST API, and 37 automated tests.
  > Advanced features like streaming telemetry pipelines, computer vision anomaly workers, and GeoServer integration are explicitly designated as future scope.
  > Software risks were directly mitigated by explicit CRS rules, junction entity modeling, and automated test coverage."
- **Key Talking Points:**
  - Scope Boundary: Implemented MVP vs. Explicit Future Scope.
  - Risk Mitigation: Technical strategies resolving data, coordinate, ambiguity, and regression risks.

---

## Slide 13: Testing & Verification Results
- **Slide Title:** 12. Testing & System Verification Results
- **Estimated Time:** 1.0 Minute
- **Speaker Script:**
  > "To verify system correctness, our implementation was evaluated against automated test suites.
  > We confirm that **37 out of 37 automated tests pass cleanly**:
  > 15 API Endpoint Integration Tests, 5 Domain Rules & Boundary Tests, 6 Model & Facet Schema Tests, 5 Repository Persistence Tests, 5 Business Service Tests, and 1 Seed Data Verification Test.
  > This confirms fully verified core MVP implementation."
- **Key Talking Points:**
  - Empirical Evidence: 37 / 37 Automated Tests Passed (`pytest`).
  - Audited Category Breakdown: Complete verification across API, domain, schemas, repos, services, and seed data.

---

## Slide 14: Implementation Demonstration
- **Slide Title:** 13. Implementation Demonstration: Software Evidence
- **Estimated Time:** 1.5 Minutes
- **Speaker Script:**
  > "Slide 14 presents visual evidence of our working software system:
  > 1. **Mount Etna / Earth:** Demonstrates Leaflet map spatial representation and eruptive timeline feed under Earth WGS84.
  > 2. **Loki Patera / Io:** Demonstrates planetary coordinate rendering on a Canvas 2D grid using 0°–360° Positive East coordinates.
  > 3. **Olympus Mons / Mars:** Demonstrates the live Metadata Inspector modal rendering active `IMAGE`, `THERMAL`, and `PLANETARY_ORBITAL` facets."
- **Key Talking Points:**
  - Implementation Proof: Embedded screenshots of Earth/Etna Leaflet view, Io/Loki Patera 0°–360° Canvas grid, and Mars/Olympus Mons Metadata Inspector modal.

---

## Slide 15: Team, Limitations & Conclusion
- **Slide Title:** 14. Team Contributions, Limitations & SEPM Conclusion
- **Estimated Time:** 1.0 Minute
- **Speaker Script:**
  > "Team contributions were divided transparently according to technical focus:
  > Technical Implementation: Architecture, database schema, FastAPI backend, business validation services, frontend UI, and 37 automated tests.
  > Documentation & SRS: SRS specification, requirements audit, and system documentation.
  > Presentation & QC: Presentation deck, visual alignment, speaker notes, and quality audit.
  > In conclusion: *VIDO demonstrates the design and implementation of a modular scientific information system capable of representing heterogeneous observations, enforcing domain rules, relating observations to events, exposing functionality through a layered API, and supporting interactive exploration with automated verification.*
  > Thank you for your time. We welcome your questions."
- **Key Talking Points:**
  - Honest Contribution Breakdown: Technical implementation, documentation/SRS, presentation/QC.
  - Restrained Phrasing: *"Layered pipeline enforces separation of concerns and supports data integrity and testability."*
  - Final SEPM Conclusion Statement.

---

## Evaluator Viva Q&A Quick Reference Cheat Sheet

1. **Q: Is VIDO using AI or Machine Learning?**
   - *Answer:* No. VIDO is a deterministic scientific data observatory and spatial-temporal exploration software system. AI/ML thermal anomaly scoring workers are explicitly categorized as future scope.
2. **Q: How does VIDO handle satellite data ingestion?**
   - *Answer:* VIDO ingests validated observational records and composite metadata payloads via REST endpoints (`POST /api/v1/observations`). Streaming satellite telemetry pipelines are part of future scope.
3. **Q: How are planetary coordinates handled without Leaflet?**
   - *Answer:* CelestialBody entities define the coordinate convention (`POSITIVE_EAST_360` vs. `EAST_WEST_180`). Planetary spatial views render coordinates on a 0°–360° Canvas 2D grid relative to the planetary datum.
4. **Q: What is the exact automated test verification result?**
   - *Answer:* Exactly 37 out of 37 automated unit and integration tests pass cleanly via `pytest` (`python -m pytest`).
