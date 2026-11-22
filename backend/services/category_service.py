"""
backend/services/category_service.py
Category management business logic (Tasks 3.1 & 3.9 / Doc 6.3 & 6.4).
"""


class CategoryService:
    def __init__(self, db_conn):
        self.conn = db_conn

    def add_category(self, name: str, tracks_expiry: bool = True, warn_days: int = 7):
        pass

    def rename_category(self, category_id: int, new_name: str):
        pass

    def delete_category(self, category_id: int):
        """Moves products to Uncategorized (D11 / Doc 6.4)."""
        pass

    def toggle_tracking(self, category_id: int, tracks_expiry: bool):
        pass

