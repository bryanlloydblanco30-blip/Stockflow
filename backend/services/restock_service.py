"""
backend/services/restock_service.py
Calculates selling speed, days of cover, suggested reorder qty, and Restock Max-Heap (Tasks 5.1 - 5.3).
"""


class RestockService:
    def __init__(self, restock_max_heap):
        self.max_heap = restock_max_heap

    def calculate_selling_speed(self, product_id: int, days: int = 14) -> float:
        pass

    def calculate_days_of_cover(self, sellable_stock: int, selling_speed: float) -> float:
        pass

    def calculate_suggested_reorder(self, selling_speed: float, sellable_stock: int, target_cover_days: int = 14) -> int:
        pass

    def build_restock_queue(self, products):
        pass

