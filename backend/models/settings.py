"""
backend/models/settings.py
Global application settings model (Doc 8.1).
"""

from dataclasses import dataclass


@dataclass
class Settings:
    global_default_days: int = 7
    currency: str = "PHP"
    date_format: str = "%d %b %Y"
    undo_mode: str = "last_only"

