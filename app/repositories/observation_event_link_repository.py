from typing import List, Optional
from app.repositories.base import BaseRepository
from app.models.observation_event_link import ObservationEventLink


class ObservationEventLinkRepository(BaseRepository):
    """Repository for persistence and query operations on ObservationEventLink association entities."""

    def create(self, link: ObservationEventLink) -> ObservationEventLink:
        query = """
        INSERT INTO observation_event_links (
            id, observation_id, event_id, relationship_type, temporal_offset_hours, notes
        ) VALUES (?, ?, ?, ?, ?, ?);
        """
        with self.db.get_connection() as conn:
            conn.execute(
                query,
                (
                    link.id,
                    link.observation_id,
                    link.event_id,
                    link.relationship_type.value,
                    link.temporal_offset_hours,
                    link.notes,
                ),
            )
        return link

    def get_by_id(self, link_id: str) -> Optional[ObservationEventLink]:
        query = "SELECT * FROM observation_event_links WHERE id = ?;"
        with self.db.get_connection() as conn:
            row = conn.execute(query, (link_id,)).fetchone()
            if row:
                return ObservationEventLink.from_dict(dict(row))
        return None

    def get_all(self) -> List[ObservationEventLink]:
        query = "SELECT * FROM observation_event_links;"
        with self.db.get_connection() as conn:
            rows = conn.execute(query).fetchall()
            return [ObservationEventLink.from_dict(dict(r)) for r in rows]

    def get_links_for_observation(self, observation_id: str) -> List[ObservationEventLink]:
        query = "SELECT * FROM observation_event_links WHERE observation_id = ?;"
        with self.db.get_connection() as conn:
            rows = conn.execute(query, (observation_id,)).fetchall()
            return [ObservationEventLink.from_dict(dict(r)) for r in rows]

    def get_links_for_event(self, event_id: str) -> List[ObservationEventLink]:
        query = "SELECT * FROM observation_event_links WHERE event_id = ?;"
        with self.db.get_connection() as conn:
            rows = conn.execute(query, (event_id,)).fetchall()
            return [ObservationEventLink.from_dict(dict(r)) for r in rows]

    def delete(self, link_id: str) -> bool:
        query = "DELETE FROM observation_event_links WHERE id = ?;"
        with self.db.get_connection() as conn:
            cursor = conn.execute(query, (link_id,))
            return cursor.rowcount > 0
