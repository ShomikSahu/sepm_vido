import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_DIR = BASE_DIR / "data"
DB_PATH = DB_DIR / "vido.db"

# Ensure data directory exists
DB_DIR.mkdir(parents=True, exist_ok=True)
