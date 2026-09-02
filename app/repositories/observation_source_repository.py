from typing import List, Optional
from app.repositories.base import BaseRepository
from app.models.observation_source import ObservationSource


class ObservationSourceRepository(BaseRepository):
    """Repository for persistence operations on ObservationSource entities."""

    def create(self, source: ObservationSource) -> ObservationSource:
        query = """
        INSERT INTO observation_sources (id, name, platform_type, operator_agency)
        VALUES (?, ?, ?, ?);
        """
        with self.db.get_connection() as conn:
            conn.execute(
                query,
                (
                    source.id,
                    source.name,
                    source.platform_type.value,
                    source.operator_agency,
                ),
            )
        return source

    def get_by_id(self, source_id: str) -> Optional[ObservationSource]:
        query = "SELECT * FROM observation_sources WHERE id = ?;"
        with self.db.get_connection() as conn:
            row = conn.execute(query, (source_id,)).fetchone()
            if row:
                return ObservationSource.from_dict(dict(row))
        return None

    def get_all(self) -> List[ObservationSource]:
        query = "SELECT * FROM observation_sources ORDER BY name ASC;"
        with self.db.get_connection() as conn:
            rows = conn.execute(query).fetchall()
            return [ObservationSource.from_dict(dict(r)) for r in rows]

    def delete(self, source_id: str) -> bool:
        query = "DELETE FROM observation_sources WHERE id = ?;"
        with self.db.get_connection() as conn:
            cursor = conn.execute(query, (source_id,))
            return cursor.rowcount > 0
