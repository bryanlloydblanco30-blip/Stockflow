"""
backend/services/restock_service.py
Calculates selling speed, days of cover, suggested reorder quantity, and Restock Max-Heap.
Tasks 5.1 to 5.3, RS-2 to RS-4, Doc 6.8.

RULES:
- Selling speed: 14-day average of non-voided sales units (Doc 6.8).
- Days of cover: sellable_stock / selling_speed.
- Suggested reorder: ceil(selling_speed * target_cover_days - sellable_stock), never below 0.
- Restock queue ranked via strictly from-scratch MaxHeap (Doc 6.8).
- Zero heapq, dict, or sorted imports.
"""

from datetime import date, timedelta
from typing import Optional, List, Dict, Any
import math
import sqlite3

from backend.ds.max_heap import MaxHeap
from backend.services.alert_service import AlertService
from backend.db.storage import StoreMemoryState


class RestockService:
    def __init__(
        self,
        conn: sqlite3.Connection,
        state: StoreMemoryState,
        alert_service: Optional[AlertService] = None,
    ):
        self.conn = conn
        self.state = state
        self.alert_service = alert_service or AlertService()

    def calculate_selling_speed(
        self,
        product_id: int,
        days: int = 14,
        today: Optional[date] = None,
    ) -> float:
        """
        Calculates average units sold per day over the trailing period (default 14 days).
        Strictly excludes voided sales transactions (Doc 6.8 / Task 5.1).
        """
        curr_date = today or date.today()
        start_date = curr_date - timedelta(days=days)

        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT COALESCE(SUM(tl.quantity), 0)
            FROM transaction_lines tl
            JOIN transactions t ON tl.transaction_id = t.id
            WHERE tl.product_id = ?
              AND t.type = 'sale'
              AND DATE(t.date_time) >= ?
              AND DATE(t.date_time) <= ?
              AND NOT EXISTS (
                  SELECT 1 FROM transactions v
                  WHERE v.type = 'void' AND v.reverses_id = t.id
              );
        """, (product_id, start_date.isoformat(), curr_date.isoformat()))

        row = cursor.fetchone()
        units_sold = row[0] if row else 0
        return units_sold / float(days)

    def calculate_days_of_cover(self, sellable_stock: int, selling_speed: float) -> float:
        """
        Days of cover: sellable_stock / selling_speed.
        If selling speed is 0: infinity if in stock, 0.0 if empty.
        """
        if selling_speed <= 0.0:
            return float("inf") if sellable_stock > 0 else 0.0
        return round(sellable_stock / selling_speed, 2)

    def calculate_suggested_reorder(
        self,
        selling_speed: float,
        sellable_stock: int,
        target_cover_days: int = 14,
    ) -> int:
        """
        Suggested reorder quantity:
        ceil(selling_speed * target_cover_days - sellable_stock), never below zero (Doc 6.8).
        """
        target_units = selling_speed * target_cover_days
        raw_qty = math.ceil(target_units - sellable_stock)
        return max(0, raw_qty)

    def build_restock_queue(
        self,
        target_cover_days: int = 14,
        today: Optional[date] = None,
    ) -> List[Dict[str, Any]]:
        """
        Constructs the restock priority queue using from-scratch MaxHeap (Task 5.2 / Doc 6.8).
        Ranking criteria:
        1. Days of cover (lowest first, inverted for MaxHeap)
        2. Selling speed (highest first)
        Each row contains human-readable reason text.
        """
        curr_date = today or date.today()
        heap = MaxHeap()

        for prod in self.state.products:
            if not prod.active:
                continue

            # Calculate sellable stock
            p_heap = self.state.get_or_create_product_heap(prod.id)
            sellable_stock = 0
            near_expiry_units = 0

            for b in p_heap.ordered_read():
                if b.quantity > 0:
                    if self.alert_service.is_sellable(b.expiry_date, curr_date):
                        sellable_stock += b.quantity
                        if b.expiry_date:
                            level = self.alert_service.calculate_level(b.expiry_date, 14, curr_date)
                            if level in ("RED", "AMBER"):
                                near_expiry_units += b.quantity

            speed = self.calculate_selling_speed(prod.id, days=14, today=curr_date)
            days_of_cover = self.calculate_days_of_cover(sellable_stock, speed)
            suggested_reorder = self.calculate_suggested_reorder(
                speed, sellable_stock, target_cover_days=target_cover_days
            )

            # Generate reason text (Doc 6.8)
            if sellable_stock == 0:
                reason = "Out of stock"
            elif sellable_stock < prod.reorder_level:
                reason = f"Below reorder level ({sellable_stock} left, reorder at {prod.reorder_level})"
            elif days_of_cover <= 3:
                reason = f"Critical cover ({days_of_cover:.1f} days left)"
            elif days_of_cover <= 7:
                reason = f"Low cover ({days_of_cover:.1f} days left)"
            else:
                reason = f"Sufficient stock ({days_of_cover:.1f} days cover)"

            # Priority for MaxHeap:
            # Days of cover inverted (-days_of_cover) so lower cover = higher priority.
            # Secondary key: selling speed (higher speed = higher priority).
            # Convert inf to -999999.0 so items with inf days of cover have lowest urgency.
            cover_score = -999999.0 if math.isinf(days_of_cover) else -days_of_cover
            priority = (cover_score, speed)

            entry = {
                "product_id": prod.id,
                "product_name": prod.name,
                "barcode": prod.barcode,
                "sellable_stock": sellable_stock,
                "selling_speed": round(speed, 3),
                "days_of_cover": days_of_cover,
                "suggested_reorder": suggested_reorder,
                "reason": reason,
            }
            heap.insert(item=entry, priority=priority)

        # Extract in priority order
        queue: List[Dict[str, Any]] = []
        while not heap.is_empty():
            queue.append(heap.extract_max())

        return queue
