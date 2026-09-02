from typing import List, Optional
from app.repositories.base import BaseRepository
from app.models.celestial_body import CelestialBody


class CelestialBodyRepository(BaseRepository):
    """Repository for persistence operations on CelestialBody entities."""

    def create(self, body: CelestialBody) -> CelestialBody:
        query = """
        INSERT INTO celestial_bodies (id, name, body_type, mean_radius_km, coordinate_system, longitude_convention)
        VALUES (?, ?, ?, ?, ?, ?);
        """
        with self.db.get_connection() as conn:
            conn.execute(
                query,
                (
                    body.id,
                    body.name,
                    body.body_type.value,
                    body.mean_radius_km,
                    body.coordinate_system,
                    body.longitude_convention.value,
                ),
            )
        return body

    def get_by_id(self, body_id: str) -> Optional[CelestialBody]:
        query = "SELECT * FROM celestial_bodies WHERE id = ?;"
        with self.db.get_connection() as conn:
            row = conn.execute(query, (body_id,)).fetchone()
            if row:
                return CelestialBody.from_dict(dict(row))
        return None

    def get_all(self) -> List[CelestialBody]:
        query = "SELECT * FROM celestial_bodies ORDER BY name ASC;"
        with self.db.get_connection() as conn:
            rows = conn.execute(query).fetchall()
            return [CelestialBody.from_dict(dict(r)) for r in rows]

    def delete(self, body_id: str) -> bool:
        query = "DELETE FROM celestial_bodies WHERE id = ?;"
        with self.db.get_connection() as conn:
            cursor = conn.execute(query, (body_id,))
            return cursor.rowcount > 0
