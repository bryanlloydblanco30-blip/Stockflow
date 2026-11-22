"""
backend/db/backup.py
SQLite file export, backup, and restore routines (Task 7.6 / Doc 9.6).
"""

from pathlib import Path
import shutil


def export_backup(source_db: Path, destination_path: Path) -> Path:
    """Creates a point-in-time copy of the SQLite database."""
    shutil.copy2(source_db, destination_path)
    return destination_path


def restore_backup(backup_file: Path, target_db: Path) -> None:
    """Restores database from an exported backup file."""
    shutil.copy2(backup_file, target_db)

