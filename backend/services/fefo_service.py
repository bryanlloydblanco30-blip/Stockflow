"""
backend/services/fefo_service.py
FEFO stock deduction logic (Task 4.4 / Doc 6.2).
Deducts from min-heap, spans multiple batches if needed, skips expired stock.

RULES:
- Expired batches are never sold (Decision D10).
- Multi-batch deduction: takes all available units from front batch, spans to next.
- FIFO for untracked products (Decision D8, received_date key).
- No heapq, dict, or sorted imports.
"""

from datetime import date
from typing import Optional, List, Dict, Any
from backend.services.alert_service import AlertService


class FEFOService:
    def __init__(self, alert_service: Optional[AlertService] = None):
        self.alert_service = alert_service or AlertService()

    def deduct_stock(
        self,
        product,
        quantity_needed: int,
        batch_min_heap,
        today: Optional[date] = None,
    ) -> List[Dict[str, Any]]:
        """
        Deducts units across batches using FEFO (or FIFO for untracked products).
        Returns list of allocation dicts: [{"batch_id": int, "quantity": int, "cost_at_time": float}].
        """
        if quantity_needed <= 0:
            return []

        curr_date = today or date.today()

        # 1. Inspect available stock in heap to validate before mutating
        total_sellable = 0
        expired_count = 0

        for b in batch_min_heap.ordered_read():
            if b.quantity > 0:
                if self.alert_service.is_sellable(b.expiry_date, curr_date):
                    total_sellable += b.quantity
                else:
                    expired_count += 1

        if total_sellable == 0 and expired_count > 0:
            raise ValueError(f"Only expired stock remains for product '{product.name}'; sale blocked.")

        if total_sellable < quantity_needed:
            raise ValueError(
                f"Insufficient sellable stock for product '{product.name}': "
                f"needed {quantity_needed}, only {total_sellable} available."
            )

        # 2. Perform multi-batch deduction in FEFO order
        remaining_needed = quantity_needed
        allocations: List[Dict[str, Any]] = []
        skipped_expired_batches = []

        while remaining_needed > 0 and not batch_min_heap.is_empty():
            batch = batch_min_heap.extract_min()

            # Skip expired batches (they remain unsold)
            if not self.alert_service.is_sellable(batch.expiry_date, curr_date):
                skipped_expired_batches.append(batch)
                continue

            take_qty = min(remaining_needed, batch.quantity)
            batch.quantity -= take_qty
            remaining_needed -= take_qty

            allocations.append({
                "batch_id": batch.id,
                "quantity": take_qty,
                "cost_at_time": batch.cost_price,
            })

            # If batch still has units left, re-insert back into heap
            if batch.quantity > 0:
                if batch.expiry_date:
                    batch_min_heap.insert(
                        item=batch,
                        key=batch.expiry_date,
                        tie_break=batch.received_date,
                    )
                else:
                    batch_min_heap.insert(
                        item=batch,
                        key=batch.received_date,
                        tie_break=str(batch.id),
                    )

        # 3. Restore any skipped expired batches back to the heap
        for exp_batch in skipped_expired_batches:
            if exp_batch.expiry_date:
                batch_min_heap.insert(
                    item=exp_batch,
                    key=exp_batch.expiry_date,
                    tie_break=exp_batch.received_date,
                )
            else:
                batch_min_heap.insert(
                    item=exp_batch,
                    key=exp_batch.received_date,
                    tie_break=str(exp_batch.id),
                )

        return allocations
