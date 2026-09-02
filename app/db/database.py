import sqlite3
from contextlib import contextmanager
from typing import Generator, Optional
from app.config import DB_PATH


class DatabaseManager:
    """Manages SQLite database connections and transactions."""

    def __init__(self, db_path: Optional[str] = None):
        self.db_path = str(db_path) if db_path else str(DB_PATH)
        self._shared_conn: Optional[sqlite3.Connection] = None

    def get_raw_connection(self) -> sqlite3.Connection:
        """Returns a raw SQLite connection configured with foreign keys and dict-like row factory."""
        if self.db_path == ":memory:":
            if self._shared_conn is None:
                conn = sqlite3.connect(":memory:", check_same_thread=False)
                conn.row_factory = sqlite3.Row
                conn.execute("PRAGMA foreign_keys = ON;")
                self._shared_conn = conn
            return self._shared_conn
        else:
            conn = sqlite3.connect(self.db_path, check_same_thread=False)
            conn.row_factory = sqlite3.Row
            conn.execute("PRAGMA foreign_keys = ON;")
            return conn

    @contextmanager
    def get_connection(self) -> Generator[sqlite3.Connection, None, None]:
        """Context manager yielding an open database connection."""
        conn = self.get_raw_connection()
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            if self.db_path != ":memory:":
                conn.close()

    def close(self):
        """Closes the shared connection if operating in memory mode."""
        if self._shared_conn:
            self._shared_conn.close()
            self._shared_conn = None


# Default singleton database manager instance for the app
db_manager = DatabaseManager()

