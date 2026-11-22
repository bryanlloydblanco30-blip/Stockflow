"""
backend/services/pos_service.py
Point of sale operations, cart management on linked list, and cash checkout (Tasks 4.1 to 4.3).
"""


class POSService:
    def __init__(self, bst_index, undo_stack, db_conn):
        self.bst = bst_index
        self.undo_stack = undo_stack
        self.conn = db_conn

    def process_barcode_entry(self, barcode: str):
        """Unified barcode entry function for USB scanner, typed, and simulate-scan."""
        return self.bst.find(barcode)

    def add_to_cart(self, product_id: int, quantity: int = 1):
        pass

    def update_cart_quantity(self, product_id: int, new_quantity: int):
        pass

    def checkout(self, cash_given: float):
        """Validates cash >= total and computes change in PHP."""
        pass

