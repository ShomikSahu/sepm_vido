# Use Case Specifications
## Volcanic Image/Data Observatory (VIDO)

---

## 1. Overview of Primary Actors

- **Volcanologist / Scientific Researcher (Primary Actor):** Queries observations, analyzes spatial-temporal relationships between observations and events, and explores multi-body volcanic data.
- **Data Manager / Administrator:** Submits new observations, defines validation schemas, and links observations to volcanic eruptive events.
- **System / Automated Validation Subsystem:** Enforces metadata validation rules upon observation submission.

---

## 2. Use Case Index

| Use Case ID | Title | Primary Actor | Target Requirement |
| :--- | :--- | :--- | :--- |
| **UC-01** | Browse Volcanic Systems | Scientific Researcher | FR-01, FR-02, FR-10 |
| **UC-02** | Search Observations | Scientific Researcher | FR-04 |
| **UC-03** | Filter Observations | Scientific Researcher | FR-04 |
| **UC-04** | View Observation Details | Scientific Researcher | FR-05 |
| **UC-05** | View Volcanic Timeline | Scientific Researcher | FR-06, FR-09 |
| **UC-06** | View Spatial Observations | Scientific Researcher | FR-07, FR-10 |
| **UC-07** | Validate & Ingest Observation | Data Manager / System | FR-03, FR-08 |
| **UC-08** | Associate Observation with Event | Data Manager | FR-09 |

---

## 3. Detailed Use Case Specifications

---

### UC-01: Browse Volcanic Systems

- **Actor:** Scientific Researcher
- **Preconditions:** The system database is populated with celestial bodies and volcanic systems (Earth and Planetary).
- **Main Success Scenario:**
  1. The user navigates to the "Volcanic Systems Explorer" view.
  2. The system presents a selectable grid/list of celestial bodies (Earth, Mars, Io, Venus).
  3. The user selects a celestial body or chooses "All Celestial Bodies".
  4. The system retrieves and displays matching volcanic systems with summary information (Name, Celestial Body, Coordinate Frame, Geographic/Planetary Coords, Status, System Type).
  5. The user clicks on a specific volcanic system (e.g., Mount Etna or Olympus Mons).
  6. The system displays the detailed profile card for the selected volcano, including region, classification, elevation, coordinate system, and observation counts.
- **Alternative / Exception Flows:**
  - *Alt 1a (Search Keyword Filter):* User enters a search query (e.g., "Mons" or "Etna") in the search input. System dynamically filters the system list matching the keyword.
  - *Exc 1b (No Systems Found):* If no volcanic system matches the search criteria, the system presents a friendly "No Volcanic Systems Found" message with a reset filter button.
- **Postconditions:** The user is presented with the profile details of the selected volcanic system.

---

### UC-02: Search Observations

- **Actor:** Scientific Researcher
- **Preconditions:** System contains recorded observations associated with volcanic systems.
- **Main Success Scenario:**
  1. User navigates to the "Observation Repository" view.
  2. User enters search keywords targeting observation titles, sensor source names, or metadata tags (e.g., "Sentinel-2", "Thermal anomaly", "THEMIS").
  3. User triggers the search action.
  4. The system queries the observation repository across core fields and dynamic metadata key-value payloads.
  5. System returns a paginated table/grid of matching observation summaries.
- **Alternative / Exception Flows:**
  - *Exc 2a (Invalid Query Syntax):* System detects special characters or illegal search terms, displays a validation error notification, and prompts the user to re-enter search text.
  - *Exc 2b (Empty Result Set):* System returns zero results and offers suggestions to widen search criteria.
- **Postconditions:** Matching observation summaries are displayed to the user.

---

### UC-03: Filter Observations

- **Actor:** Scientific Researcher
- **Preconditions:** User is viewing the observation listing or a specific volcano detail page.
- **Main Success Scenario:**
  1. User opens the Filter Drawer or Control Panel.
  2. User selects filter options:
     - Date Range (Start Date to End Date)
     - Metadata Facet Category (Image, Thermal, Planetary Orbital)
     - Data Source (e.g., MODIS, Landsat, MRO CTX, Ground Camera)
     - Celestial Body / Volcanic System
  3. User applies the filter set.
  4. System updates the observation display list to show only observations meeting *all* combined filter criteria.
- **Alternative / Exception Flows:**
  - *Alt 3a (Reset Filters):* User clicks "Reset Filters", restoring the view to all observations for the selected system.
  - *Exc 3b (Inverted Date Range):* User sets Start Date later than End Date. System alerts user: "Start date must be earlier than or equal to end date" and highlights the input fields.
- **Postconditions:** System displays the filtered sub-set of observations.

---

### UC-04: View Observation Details

- **Actor:** Scientific Researcher
- **Preconditions:** User is viewing a list, timeline, or spatial map of observations.
- **Main Success Scenario:**
  1. User clicks on an observation record or card.
  2. System opens the Observation Detail modal/view.
  3. System renders:
     - Core properties (ID, Timestamp, Source, Target Volcano, Planet, Spatial Coords).
     - Associated Media Preview (Ground image, thermal map render, or orbital frame).
     - Heterogeneous Metadata Inspection Panel (rendering active metadata facets in structured key-value format e.g., brightness temperature, spectral band resolution, spacecraft altitude).
     - Linked Volcanic Events (if any).
  4. User inspects metadata facets and linked event contexts.
- **Alternative / Exception Flows:**
  - *Exc 4a (Media File Missing):* If local image asset URL is unresolvable, system displays a fallback placeholder icon alongside raw metadata attributes.
- **Postconditions:** Detailed observational data and metadata facets are presented to the user.

---

### UC-05: View Volcanic Timeline

- **Actor:** Scientific Researcher
- **Preconditions:** User has selected a specific Volcanic System.
- **Main Success Scenario:**
  1. User selects the "Timeline View" tab for the active volcanic system.
  2. System fetches all observations and eruptive events associated with the system, ordered chronologically.
  3. System renders an interactive dual-lane timeline view:
     - Upper lane: Volcanic Events (rendering bounded duration bars for completed events, and open-ended/ongoing visual indicators extending to the present date for active events where `end_time` is NULL).
     - Lower lane: Observations marked as point events or time-stamped markers.
  4. User hovers/clicks on a timeline node.
  5. System highlights the associated observation/event details in a contextual quick-view pane.
- **Alternative / Exception Flows:**
  - *Alt 5a (Timeline Zoom/Pan):* User adjusts timeline scale (e.g., Year, Month, Day view). System updates resolution of timeline markers.
  - *Exc 5b (Sparse Data):* Volcanic system has events but zero observations (or vice versa). System displays available entries with a notification "No observations recorded during this timeframe."
- **Postconditions:** Combined temporal relationship between observations and events (including ongoing events) is visually rendered.

---

### UC-06: View Spatial Observations

- **Actor:** Scientific Researcher
- **Preconditions:** Celestial body and volcanic system spatial data are loaded.
- **Main Success Scenario:**
  1. User switches to the "Spatial Map View" for a volcanic system or celestial body.
  2. System determines the coordinate reference system for the celestial body (Earth geographic lat/long -180°..+180° or Planetary coordinate grid 0°..360° Positive East based on `CelestialBody.coordinate_system`).
  3. System renders the base surface map or coordinate grid centered on the volcanic feature.
  4. System plots observation spatial markers using coordinate resolution rules:
     - If observation has explicit latitude/longitude, plot pin at observation coordinates.
     - If observation coordinates are NULL but parent `VolcanicSystem` has coordinates, plot pin at `VolcanicSystem` location with a fallback visual indicator.
  5. User clicks on a spatial marker to display a mini summary popup containing timestamp, active facets, and link to UC-04 View Observation Details.
- **Alternative / Exception Flows:**
  - *Alt 6a (Unlocated Observations):* Observations lacking both observation-level coordinates and parent volcano coordinates are listed in an "Unlocated Observations" side panel without assigning an invented spatial position.
- **Postconditions:** Observations are visually located across spatial space relative to the volcanic system coordinate frame.

---

### UC-07: Validate & Ingest Observation

- **Actor:** Data Manager / System Validation Subsystem
- **Preconditions:** A new observation payload is prepared for submission via API or ingest form.
- **Main Success Scenario:**
  1. Actor submits an observation payload containing core attributes and dynamic JSON metadata containing zero or more facet payloads (`IMAGE`, `THERMAL`, `PLANETARY_ORBITAL`).
  2. Validation engine inspects each attached metadata facet.
  3. System retrieves designated Pydantic validation rules for each active facet.
  4. System checks field presence, data types, and value boundaries (e.g., `brightness_temp_k > 0`, coordinate bounds conforming to celestial body convention).
  5. Validation passes cleanly.
  6. System stores observation record and returns HTTP 201 Created with validated observation payload.
- **Alternative / Exception Flows:**
  - *Exc 7a (Schema Validation Error):* Required facet key is missing or invalid type/boundary. System rejects request with HTTP 422 Unprocessable Entity and detailed validation failure log.
- **Postconditions:** Observation payload is guaranteed to conform to strict type metadata rules before database persistence.

---

### UC-08: Associate Observation with Event

- **Actor:** Data Manager
- **Preconditions:** Target `Observation` and `VolcanicEvent` exist in the system database.
- **Main Success Scenario:**
  1. User selects an observation and opens "Link to Volcanic Event" dialog.
  2. System presents events associated with the same volcanic system.
  3. User selects the matching `VolcanicEvent`.
  4. User designates relationship classification (`PRE_ERUPTIVE`, `CO_ERUPTIVE`, `POST_ERUPTIVE`, or `UNRELATED`).
  5. User submits association request.
  6. System writes an entry to `ObservationEventLink` repository and updates temporal view correlations.
- **Alternative / Exception Flows:**
  - *Exc 8a (Duplicate Link):* Association between exact observation and event already exists. System notifies user "Relationship link already recorded" and prevents duplicate entry.
- **Postconditions:** Observation is explicitly linked to volcanic event context in space and time.

