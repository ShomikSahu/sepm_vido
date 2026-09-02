from typing import List, Optional
from app.repositories.base import BaseRepository
from app.repositories.celestial_body_repository import CelestialBodyRepository
from app.models.volcanic_system import VolcanicSystem


class VolcanicSystemRepository(BaseRepository):
    """Repository for persistence operations on VolcanicSystem entities."""

    def create(self, system: VolcanicSystem) -> VolcanicSystem:
        # Validate coordinates against parent body if available
        body_repo = CelestialBodyRepository(self.db)
        body = body_repo.get_by_id(system.celestial_body_id)
        if body:
            system.validate_coordinates_against_body(body)

        query = """
        INSERT INTO volcanic_systems (
            id, celestial_body_id, name, latitude, longitude, elevation_m, region, volcanic_type, status
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
        """
        with self.db.get_connection() as conn:
            conn.execute(
                query,
                (
                    system.id,
                    system.celestial_body_id,
                    system.name,
                    system.latitude,
                    system.longitude,
                    system.elevation_m,
                    system.region,
                    system.volcanic_type,
                    system.status.value,
                ),
            )
        return system

    def get_by_id(self, system_id: str) -> Optional[VolcanicSystem]:
        query = "SELECT * FROM volcanic_systems WHERE id = ?;"
        with self.db.get_connection() as conn:
            row = conn.execute(query, (system_id,)).fetchone()
            if row:
                return VolcanicSystem.from_dict(dict(row))
        return None

    def get_all(self) -> List[VolcanicSystem]:
        query = "SELECT * FROM volcanic_systems ORDER BY name ASC;"
        with self.db.get_connection() as conn:
            rows = conn.execute(query).fetchall()
            return [VolcanicSystem.from_dict(dict(r)) for r in rows]

    def get_by_celestial_body(self, celestial_body_id: str) -> List[VolcanicSystem]:
        query = "SELECT * FROM volcanic_systems WHERE celestial_body_id = ? ORDER BY name ASC;"
        with self.db.get_connection() as conn:
            rows = conn.execute(query, (celestial_body_id,)).fetchall()
            return [VolcanicSystem.from_dict(dict(r)) for r in rows]

    def delete(self, system_id: str) -> bool:
        query = "DELETE FROM volcanic_systems WHERE id = ?;"
        with self.db.get_connection() as conn:
            cursor = conn.execute(query, (system_id,))
            return cursor.rowcount > 0
