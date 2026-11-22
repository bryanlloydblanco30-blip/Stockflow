"""
backend/services/alert_service.py
Calculates alert levels dynamically from today's date (never stored, D9 / Doc 6.3).
Levels: Expired (<0), Red (0 to red_limit), Amber (red_limit to warn_days), OK.
"""

from datetime import date


class AlertService:
    @staticmethod
    def calculate_level(expiry_date_str: str | None, warn_days: int, today: date | None = None) -> str:
        """Dynamically computes Expired, Red, Amber, or OK."""
        if not expiry_date_str:
            return "NO_EXPIRY"
        # Implemented in Phase 3
        return "OK"

    def scan_near_expiry_batches(self, products_with_heaps, today: date | None = None):
        """Scans heaps in expiry order and stops at first batch outside window."""
        pass

