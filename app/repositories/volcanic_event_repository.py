from typing import List, Optional
from app.repositories.base import BaseRepository
from app.models.volcanic_event import VolcanicEvent


class VolcanicEventRepository(BaseRepository):
    """Repository for persistence and query operations on VolcanicEvent entities."""

    def create(self, event: VolcanicEvent) -> VolcanicEvent:
        query = """
        INSERT INTO volcanic_events (
            id, volcanic_system_id, title, event_type, start_time, end_time, vei_rating, description
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?);
        """
        with self.db.get_connection() as conn:
            conn.execute(
                query,
                (
                    event.id,
                    event.volcanic_system_id,
                    event.title,
                    event.event_type.value,
                    event.start_time,
                    event.end_time,
                    event.vei_rating,
                    event.description,
                ),
            )
        return event

    def get_by_id(self, event_id: str) -> Optional[VolcanicEvent]:
        query = "SELECT * FROM volcanic_events WHERE id = ?;"
        with self.db.get_connection() as conn:
            row = conn.execute(query, (event_id,)).fetchone()
            if row:
                return VolcanicEvent.from_dict(dict(row))
        return None

    def get_all(self) -> List[VolcanicEvent]:
        query = "SELECT * FROM volcanic_events ORDER BY start_time DESC;"
        with self.db.get_connection() as conn:
            rows = conn.execute(query).fetchall()
            return [VolcanicEvent.from_dict(dict(r)) for r in rows]

    def get_by_system(self, volcanic_system_id: str) -> List[VolcanicEvent]:
        query = "SELECT * FROM volcanic_events WHERE volcanic_system_id = ? ORDER BY start_time DESC;"
        with self.db.get_connection() as conn:
            rows = conn.execute(query, (volcanic_system_id,)).fetchall()
            return [VolcanicEvent.from_dict(dict(r)) for r in rows]

    def get_ongoing_events(self) -> List[VolcanicEvent]:
        """Queries all active ongoing events (where end_time is NULL)."""
        query = "SELECT * FROM volcanic_events WHERE end_time IS NULL ORDER BY start_time DESC;"
        with self.db.get_connection() as conn:
            rows = conn.execute(query).fetchall()
            return [VolcanicEvent.from_dict(dict(r)) for r in rows]

    def delete(self, event_id: str) -> bool:
        query = "DELETE FROM volcanic_events WHERE id = ?;"
        with self.db.get_connection() as conn:
            cursor = conn.execute(query, (event_id,))
            return cursor.rowcount > 0
