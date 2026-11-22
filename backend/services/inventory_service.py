"""
backend/services/inventory_service.py
Receiving deliveries, older-stock warnings, adjustments, and write-offs (Tasks 3.3, 3.4, 3.7, 3.8).
"""


class InventoryService:
    def __init__(self, db_conn):
        self.conn = db_conn

    def receive_stock(self, product_id: int, quantity: int, cost: float, expiry_date: str = None):
        """Adds batch and checks for older batches to generate older-stock warning (IN-5)."""
        pass

    def get_older_stock_warning(self, product_id: int, new_expiry_date: str):
        pass

    def mark_shelf_rotated(self, batch_id: int):
        pass

    def write_off_expired(self, batch_id: int):
        pass

    def adjust_stock(self, product_id: int, new_quantity: int, reason: str):
        pass

