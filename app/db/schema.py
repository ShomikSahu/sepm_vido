import sqlite3

DDL_STATEMENTS = """
-- Celestial Bodies Table
CREATE TABLE IF NOT EXISTS celestial_bodies (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    body_type TEXT NOT NULL,
    mean_radius_km REAL NOT NULL,
    coordinate_system TEXT NOT NULL,
    longitude_convention TEXT NOT NULL
);

-- Volcanic Systems Table
CREATE TABLE IF NOT EXISTS volcanic_systems (
    id TEXT PRIMARY KEY,
    celestial_body_id TEXT NOT NULL,
    name TEXT NOT NULL,
    latitude REAL NOT NULL,
    longitude REAL NOT NULL,
    elevation_m REAL NOT NULL,
    region TEXT NOT NULL,
    volcanic_type TEXT NOT NULL,
    status TEXT NOT NULL,
    FOREIGN KEY (celestial_body_id) REFERENCES celestial_bodies (id) ON DELETE CASCADE
);

-- Observation Sources Table
CREATE TABLE IF NOT EXISTS observation_sources (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    platform_type TEXT NOT NULL,
    operator_agency TEXT NOT NULL
);

-- Observations Table
CREATE TABLE IF NOT EXISTS observations (
    id TEXT PRIMARY KEY,
    volcanic_system_id TEXT NOT NULL,
    source_id TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    latitude REAL,
    longitude REAL,
    summary TEXT NOT NULL,
    media_path TEXT,
    metadata TEXT NOT NULL,
    FOREIGN KEY (volcanic_system_id) REFERENCES volcanic_systems (id) ON DELETE CASCADE,
    FOREIGN KEY (source_id) REFERENCES observation_sources (id) ON DELETE RESTRICT
);

-- Volcanic Events Table
CREATE TABLE IF NOT EXISTS volcanic_events (
    id TEXT PRIMARY KEY,
    volcanic_system_id TEXT NOT NULL,
    title TEXT NOT NULL,
    event_type TEXT NOT NULL,
    start_time TEXT NOT NULL,
    end_time TEXT,
    vei_rating INTEGER,
    description TEXT NOT NULL,
    FOREIGN KEY (volcanic_system_id) REFERENCES volcanic_systems (id) ON DELETE CASCADE
);

-- Observation Event Links Table
CREATE TABLE IF NOT EXISTS observation_event_links (
    id TEXT PRIMARY KEY,
    observation_id TEXT NOT NULL,
    event_id TEXT NOT NULL,
    relationship_type TEXT NOT NULL,
    temporal_offset_hours REAL,
    notes TEXT,
    FOREIGN KEY (observation_id) REFERENCES observations (id) ON DELETE CASCADE,
    FOREIGN KEY (event_id) REFERENCES volcanic_events (id) ON DELETE CASCADE,
    UNIQUE (observation_id, event_id)
);
"""


def init_db(conn: sqlite3.Connection) -> None:
    """Executes schema DDL statements to create database tables."""
    conn.executescript(DDL_STATEMENTS)
