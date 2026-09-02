import json
from typing import List, Optional
from app.repositories.base import BaseRepository
from app.repositories.volcanic_system_repository import VolcanicSystemRepository
from app.repositories.celestial_body_repository import CelestialBodyRepository
from app.models.observation import Observation


class ObservationRepository(BaseRepository):
    """Repository for persistence and query operations on Observation entities."""

    def create(self, observation: Observation) -> Observation:
        # Validate coordinates against parent system/body if observation coordinates exist
        if observation.latitude is not None or observation.longitude is not None:
            sys_repo = VolcanicSystemRepository(self.db)
            system = sys_repo.get_by_id(observation.volcanic_system_id)
            if system:
                body_repo = CelestialBodyRepository(self.db)
                body = body_repo.get_by_id(system.celestial_body_id)
                if body:
                    observation.validate_coordinates_against_body(body)

        obs_dict = observation.to_dict()
        query = """
        INSERT INTO observations (
            id, volcanic_system_id, source_id, timestamp, latitude, longitude, summary, media_path, metadata
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
        """
        with self.db.get_connection() as conn:
            conn.execute(
                query,
                (
                    obs_dict["id"],
                    obs_dict["volcanic_system_id"],
                    obs_dict["source_id"],
                    obs_dict["timestamp"],
                    obs_dict["latitude"],
                    obs_dict["longitude"],
                    obs_dict["summary"],
                    obs_dict["media_path"],
                    obs_dict["metadata"],
                ),
            )
        return observation

    def get_by_id(self, observation_id: str) -> Optional[Observation]:
        query = "SELECT * FROM observations WHERE id = ?;"
        with self.db.get_connection() as conn:
            row = conn.execute(query, (observation_id,)).fetchone()
            if row:
                return Observation.from_dict(dict(row))
        return None

    def get_all(self) -> List[Observation]:
        query = "SELECT * FROM observations ORDER BY timestamp DESC;"
        with self.db.get_connection() as conn:
            rows = conn.execute(query).fetchall()
            return [Observation.from_dict(dict(r)) for r in rows]

    def get_by_system(self, volcanic_system_id: str) -> List[Observation]:
        query = "SELECT * FROM observations WHERE volcanic_system_id = ? ORDER BY timestamp DESC;"
        with self.db.get_connection() as conn:
            rows = conn.execute(query, (volcanic_system_id,)).fetchall()
            return [Observation.from_dict(dict(r)) for r in rows]

    def filter_by_facet(self, facet_category: str) -> List[Observation]:
        """Queries observations that contain a specific active metadata facet category (IMAGE, THERMAL, PLANETARY_ORBITAL)."""
        all_obs = self.get_all()
        matching = []
        for obs in all_obs:
            active_facets = obs.metadata.get("active_facets", []) if obs.metadata else []
            if facet_category in active_facets:
                matching.append(obs)
        return matching

    def filter_by_date_range(self, start_timestamp: Optional[str] = None, end_timestamp: Optional[str] = None) -> List[Observation]:
        """Filters observations falling within an ISO-8601 date range."""
        query = "SELECT * FROM observations WHERE 1=1"
        params = []
        if start_timestamp:
            query += " AND timestamp >= ?"
            params.append(start_timestamp)
        if end_timestamp:
            query += " AND timestamp <= ?"
            params.append(end_timestamp)
        query += " ORDER BY timestamp DESC;"

        with self.db.get_connection() as conn:
            rows = conn.execute(query, params).fetchall()
            return [Observation.from_dict(dict(r)) for r in rows]

    def delete(self, observation_id: str) -> bool:
        query = "DELETE FROM observations WHERE id = ?;"
        with self.db.get_connection() as conn:
            cursor = conn.execute(query, (observation_id,))
            return cursor.rowcount > 0
