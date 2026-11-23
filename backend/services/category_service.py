"""
backend/services/category_service.py
Category management business logic (Tasks 3.1 & 3.9 / Doc 6.3 & 6.4).
Enforces:
- Dynamic red_days (1/3 of warn_days, min 1)
- Global default window for uncategorized products (7 days, Doc 17)
- Safe category deletion: Moves products to Uncategorized (category_id = None)
- Category switch handling: No -> Yes flags 'Expiry date needed', Yes -> No keeps dates but ignores them
"""

import sqlite3
from typing import Optional, List
from backend.models.category import Category


class CategoryService:
    def __init__(self, db_conn: sqlite3.Connection, memory_state):
        self.conn = db_conn
        self.state = memory_state

    def add_category(self, name: str, tracks_expiry: bool = True, warn_days: int = 7) -> Category:
        """Creates a new Category in SQLite and memory."""
        cat = Category(
            id=0,
            name=name.strip(),
            tracks_expiry=tracks_expiry,
            warn_days=warn_days if tracks_expiry else 0,
        )
        with self.conn:
            cur = self.conn.cursor()
            cur.execute(
                "INSERT INTO categories (name, tracks_expiry, warn_days) VALUES (?, ?, ?);",
                (cat.name, int(cat.tracks_expiry), cat.warn_days),
            )
            cat.id = cur.lastrowid
        self.state.categories.append(cat)
        return cat

    def rename_category(self, category_id: int, new_name: str) -> Optional[Category]:
        """Renames an existing category."""
        clean_name = new_name.strip()
        with self.conn:
            self.conn.execute(
                "UPDATE categories SET name = ? WHERE id = ?;",
                (clean_name, category_id),
            )
        cat = self.state.get_category_by_id(category_id)
        if cat:
            cat.name = clean_name
        return cat

    def delete_category(self, category_id: int) -> int:
        """
        Deletes category and moves its products to Uncategorized (category_id = None).
        Returns number of affected products (Doc 6.4 / Edge Case 12).
        """
        with self.conn:
            cur = self.conn.cursor()
            # Move products to None
            cur.execute("UPDATE products SET category_id = NULL WHERE category_id = ?;", (category_id,))
            affected = cur.rowcount
            # Delete category
            cur.execute("DELETE FROM categories WHERE id = ?;", (category_id,))

        # Update in-memory models
        for i, c in enumerate(self.state.categories):
            if c.id == category_id:
                self.state.categories.pop(i)
                break

        for p in self.state.products:
            if p.category_id == category_id:
                p.category_id = None

        return affected

    def toggle_tracking(self, category_id: int, tracks_expiry: bool, warn_days: int = 7) -> Optional[Category]:
        """
        Toggles tracks_expiry flag on a category (Doc 6.4 / Task 3.9).
        When switching No -> Yes, existing batches keep None and are flagged 'Expiry date needed'.
        """
        effective_warn = warn_days if tracks_expiry else 0
        with self.conn:
            self.conn.execute(
                "UPDATE categories SET tracks_expiry = ?, warn_days = ? WHERE id = ?;",
                (int(tracks_expiry), effective_warn, category_id),
            )
        cat = self.state.get_category_by_id(category_id)
        if cat:
            cat.tracks_expiry = tracks_expiry
            cat.warn_days = effective_warn
        return cat

    def get_effective_warn_days(self, category_id: Optional[int]) -> int:
        """Returns category warning window, or global default 7 days for uncategorized (Doc 17)."""
        if category_id is None:
            return 7
        cat = self.state.get_category_by_id(category_id)
        if cat is None:
            return 7
        return cat.warn_days if cat.tracks_expiry else 0
