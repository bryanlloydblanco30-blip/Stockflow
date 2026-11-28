"""
tests/test_db_migration.py
Tests for platform-neutral app-data storage and idempotent one-time DB migration.
"""

import sqlite3
from pathlib import Path

from backend.db.connection import get_app_data_dir, get_db_path, migrate_legacy_db_if_needed


def _create_sample_db(path: Path, value: str) -> None:
    conn = sqlite3.connect(str(path))
    conn.execute("PRAGMA journal_mode = WAL;")
    conn.execute("CREATE TABLE items (id INTEGER PRIMARY KEY, name TEXT);")
    conn.execute("INSERT INTO items (name) VALUES (?);", (value,))
    conn.commit()
    conn.close()


def test_app_data_dir_respects_env(tmp_path, monkeypatch):
    custom_dir = tmp_path / "CustomAppData"
    monkeypatch.setenv("STOCKFLOW_DATA_DIR", str(custom_dir))
    resolved = get_app_data_dir()
    assert resolved == custom_dir
    assert resolved.is_dir()


def test_migration_copies_once_and_is_idempotent(tmp_path, monkeypatch):
    legacy_db = tmp_path / "legacy" / "stockflow.db"
    legacy_db.parent.mkdir(parents=True, exist_ok=True)
    _create_sample_db(legacy_db, "original_item")

    target_dir = tmp_path / "appdata" / "StockFlow"
    target_db = target_dir / "stockflow.db"

    # First run: target does not exist -> migrates
    migrated_first = migrate_legacy_db_if_needed(target_db, legacy_candidates=[legacy_db])
    assert migrated_first is True
    assert target_db.is_file()

    # Verify content in target matches legacy
    conn = sqlite3.connect(str(target_db))
    rows = conn.execute("SELECT name FROM items;").fetchall()
    assert rows == [("original_item",)]
    # Mutate target to simulate user adding data after migration
    conn.execute("INSERT INTO items (name) VALUES ('new_user_item');")
    conn.commit()
    conn.close()

    # Second run: target already exists -> must NOT overwrite or delete new data
    migrated_second = migrate_legacy_db_if_needed(target_db, legacy_candidates=[legacy_db])
    assert migrated_second is False

    conn2 = sqlite3.connect(str(target_db))
    rows2 = conn2.execute("SELECT name FROM items ORDER BY id;").fetchall()
    conn2.close()
    assert rows2 == [("original_item",), ("new_user_item",)]


def test_get_db_path_uses_app_data_dir(tmp_path, monkeypatch):
    monkeypatch.delenv("STOCKFLOW_DB_PATH", raising=False)
    monkeypatch.setenv("STOCKFLOW_DATA_DIR", str(tmp_path / "AppDataStockFlow"))
    monkeypatch.chdir(tmp_path)  # no legacy db in cwd

    db_path = get_db_path()
    assert db_path == tmp_path / "AppDataStockFlow" / "stockflow.db"
