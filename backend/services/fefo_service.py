"""
backend/services/fefo_service.py
FEFO stock deduction logic (Task 4.4 / Doc 6.2).
Deducts from min-heap, spans multiple batches if needed, skips expired stock.
"""


class FEFOService:
    @staticmethod
    def deduct_stock(product, quantity_needed: int, batch_min_heap):
        """
        Deducts units across batches using FEFO (or FIFO for untracked).
        Returns list of (batch_id, quantity_taken, cost_price).
        """
        pass

