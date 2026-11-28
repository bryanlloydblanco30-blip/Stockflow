"""
backend/db/connection.py
Platform-neutral database connection and path provider (Decision D17).
"""

import os
from pathlib import Path
import shutil
import sqlite3
import sys
from typing import Iterable, Optional


def get_app_data_dir() -> Path:
    """
    Returns the platform-neutral per-user application data directory for StockFlow.
    - Windows: %APPDATA%/StockFlow
    - macOS: ~/Library/Application Support/StockFlow
    - Linux/other: $XDG_DATA_HOME/StockFlow or ~/.local/share/StockFlow
    Can be overridden via STOCKFLOW_DATA_DIR environment variable.
    """
    env_dir = os.getenv("STOCKFLOW_DATA_DIR")
    if env_dir:
        data_dir = Path(env_dir)
    elif os.name == "nt" and os.getenv("APPDATA"):
        data_dir = Path(os.environ["APPDATA"]) / "StockFlow"
    elif sys.platform == "darwin":
        data_dir = Path.home() / "Library" / "Application Support" / "StockFlow"
    else:
        xdg = os.getenv("XDG_DATA_HOME") or str(Path.home() / ".local" / "share")
        data_dir = Path(xdg) / "StockFlow"
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir


def _default_legacy_db_candidates() -> list[Path]:
    """Ordered candidate paths where a pre-migration stockflow.db may exist."""
    candidates: list[Path] = [Path.cwd() / "stockflow.db"]
    if getattr(sys, "frozen", False):
        exe_dir = Path(sys.executable).resolve().parent
        candidates.append(exe_dir / "stockflow.db")
        candidates.append(exe_dir / "_internal" / "stockflow.db")
        if hasattr(sys, "_MEIPASS"):
            candidates.append(Path(sys._MEIPASS) / "stockflow.db")
    else:
        candidates.append(Path(__file__).resolve().parent.parent.parent / "stockflow.db")
    return candidates


def migrate_legacy_db_if_needed(
    target_db: Path,
    legacy_candidates: Optional[Iterable[Path]] = None,
) -> bool:
    """
    Idempotent one-time migration: copies an existing stockflow.db (including WAL)
    to `target_db` ONLY if `target_db` does not exist yet. Never overwrites or
    deletes existing data.
    Returns True if migration ran, False otherwise.
    """
    if target_db.exists():
        return False

    candidates = list(legacy_candidates) if legacy_candidates is not None else _default_legacy_db_candidates()
    source_db: Optional[Path] = None
    for cand in candidates:
        if cand.resolve() == target_db.resolve():
            continue
        if cand.is_file() and cand.stat().st_size > 0:
            source_db = cand
            break

    if source_db is None:
        return False

    target_db.parent.mkdir(parents=True, exist_ok=True)
    tmp_db = target_db.with_suffix(".db.migrating")
    if tmp_db.exists():
        tmp_db.unlink()

    try:
        src_conn = sqlite3.connect(str(source_db), timeout=30.0)
        dst_conn = sqlite3.connect(str(tmp_db), timeout=30.0)
        try:
            src_conn.backup(dst_conn)
        finally:
            dst_conn.close()
            src_conn.close()
    except sqlite3.Error:
        if tmp_db.exists():
            tmp_db.unlink()
        shutil.copy2(source_db, tmp_db)

    os.replace(tmp_db, target_db)
    return True


def get_db_path() -> Path:
    """
    Returns the platform-neutral path to the SQLite database in the device's
    app-data directory (%APPDATA%/StockFlow/stockflow.db on Windows).
    Can be overridden via STOCKFLOW_DB_PATH environment variable.
    """
    env_path = os.getenv("STOCKFLOW_DB_PATH")
    if env_path:
        return Path(env_path)

    target_db = get_app_data_dir() / "stockflow.db"
    migrate_legacy_db_if_needed(target_db)
    return target_db


def get_connection(db_path: Path | str | None = None) -> sqlite3.Connection:
    """Opens a SQLite connection with foreign keys enabled and WAL mode."""
    target_path = Path(db_path) if db_path else get_db_path()
    conn = sqlite3.connect(target_path, timeout=30.0)
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.execute("PRAGMA journal_mode = WAL;")
    return conn

