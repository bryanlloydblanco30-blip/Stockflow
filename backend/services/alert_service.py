"""
backend/services/alert_service.py
Calculates alert levels dynamically from today's date (never stored, D9 / Doc 6.3).
Levels: Expired (<0), Red (0 to red_limit), Amber (red_limit to warn_days), OK, and NO_EXPIRY.

Rule: Red limit is 1/3 of amber window, rounded, minimum 1 day.
(3 -> 1, 5 -> 2, 7 -> 2, 14 -> 5, 30 -> 10)
"""

from datetime import date, datetime
from typing import Optional, List, Dict, Any


class AlertService:
    @staticmethod
    def calculate_level(expiry_date_str: Optional[str], warn_days: int, today: Optional[date] = None) -> str:
        """
        Dynamically computes: EXPIRED, RED, AMBER, OK, or NO_EXPIRY.
        Never stored in database (Decision D9).
        """
        if not expiry_date_str:
            return "NO_EXPIRY"

        curr_date = today or date.today()
        if isinstance(expiry_date_str, str):
            exp_date = datetime.strptime(expiry_date_str, "%Y-%m-%d").date()
        else:
            exp_date = expiry_date_str

        days_left = (exp_date - curr_date).days

        if days_left < 0:
            return "EXPIRED"

        # Red limit: max(1, round(warn_days / 3))
        red_limit = max(1, round(warn_days / 3)) if warn_days > 0 else 1

        if days_left <= red_limit:
            return "RED"

        if days_left <= warn_days:
            return "AMBER"

        return "OK"

    @staticmethod
    def is_sellable(expiry_date_str: Optional[str], today: Optional[date] = None) -> bool:
        """
        Expired batches are never sold (Decision D10).
        Expiry today is Red and still sellable. Expired starts the next day.
        """
        if not expiry_date_str:
            return True

        curr_date = today or date.today()
        exp_date = datetime.strptime(expiry_date_str, "%Y-%m-%d").date()
        return (exp_date - curr_date).days >= 0

    def scan_near_expiry_batches(
        self,
        products_with_heaps: List[tuple[Any, Any]],
        today: Optional[date] = None,
    ) -> List[Dict[str, Any]]:
        """
        Uses non-destructive ordered_read on Min-Heaps.
        Stops scanning at the first batch outside the window (Doc 6.3).
        """
        alerts: List[Dict[str, Any]] = []
        curr_date = today or date.today()

        for product, heap in products_with_heaps:
            batches_ordered = heap.ordered_read()
            warn_days = product.warn_days if hasattr(product, "warn_days") else 7

            for batch in batches_ordered:
                if not batch.expiry_date:
                    continue

                level = self.calculate_level(batch.expiry_date, warn_days, curr_date)

                if level in ("EXPIRED", "RED", "AMBER"):
                    alerts.append({
                        "product_id": product.id,
                        "product_name": product.name,
                        "batch_id": batch.id,
                        "quantity": batch.quantity,
                        "expiry_date": batch.expiry_date,
                        "level": level,
                    })
                elif level == "OK":
                    # Optimization from Doc 6.3: Stop at first batch outside window
                    break

        return alerts
