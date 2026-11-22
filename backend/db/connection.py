"""
backend/db/connection.py
Platform-neutral database connection and path provider (Decision D17).
"""

import os
from pathlib import Path
import sqlite3


def get_db_path() -> Path:
    """
    Returns the platform-neutral path to the SQLite database.
    Can be overridden via STOCKFLOW_DB_PATH environment variable.
    """
    env_path = os.getenv("STOCKFLOW_DB_PATH")
    if env_path:
        return Path(env_path)
    return Path(__file__).resolve().parent.parent.parent / "stockflow.db"


def get_connection(db_path: Path | str | None = None) -> sqlite3.Connection:
    """Opens a SQLite connection with foreign keys enabled and WAL mode."""
    target_path = Path(db_path) if db_path else get_db_path()
    conn = sqlite3.connect(target_path, timeout=30.0)
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.execute("PRAGMA journal_mode = WAL;")
    return conn

