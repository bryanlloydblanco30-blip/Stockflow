"""
backend/models/category.py
Category model (Doc 8.1).
"""

from dataclasses import dataclass


@dataclass
class Category:
    id: int
    name: str
    tracks_expiry: bool = True
    warn_days: int = 7

    @property
    def red_days(self) -> int:
        """Calculated automatically as 1/3 of warn_days, minimum 1 day (D7)."""
        return max(1, round(self.warn_days / 3))

