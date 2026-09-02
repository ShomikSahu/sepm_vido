import sqlite3
from typing import Optional
from app.db.database import DatabaseManager, db_manager


class BaseRepository:
    """Base repository encapsulating SQLite connection management and row formatting."""

    def __init__(self, db: Optional[DatabaseManager] = None):
        self.db = db if db is not None else db_manager

    def _get_connection(self) -> sqlite3.Connection:
        return self.db.get_raw_connection()
