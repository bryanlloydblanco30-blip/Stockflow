"""
backend/services/product_service.py
Product management, BST barcode search, and Trie name search (Task 3.2 / Doc 6.1).
Enforces:
- BST for O(log n) barcode lookup, rejecting duplicate barcodes
- Trie for O(p) lowercase prefix search (limit 8)
- Soft deletion if transaction history exists
"""

import sqlite3
from typing import Optional, List
from backend.models.product import Product


class ProductService:
    def __init__(self, db_conn: sqlite3.Connection, memory_state):
        self.conn = db_conn
        self.state = memory_state

    def register_product(
        self,
        barcode: str,
        name: str,
        cost: float,
        price: float,
        category_id: Optional[int] = None,
        reorder_level: int = 0,
        location_id: int = 1,
    ) -> Product:
        """Registers a new Product, saving to SQLite and indexing in BST and Trie."""
        clean_barcode = barcode.strip()
        clean_name = name.strip()

        prod = Product(
            id=0,
            barcode=clean_barcode,
            name=clean_name,
            category_id=category_id,
            cost_price=float(cost),
            selling_price=float(price),
            reorder_level=int(reorder_level),
            location_id=location_id,
            active=True,
        )

        with self.conn:
            cur = self.conn.cursor()
            cur.execute("""
                INSERT INTO products (barcode, name, category_id, cost_price, selling_price, reorder_level, location_id, active)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?);
            """, (
                prod.barcode,
                prod.name,
                prod.category_id,
                prod.cost_price,
                prod.selling_price,
                prod.reorder_level,
                prod.location_id,
                int(prod.active),
            ))
            prod.id = cur.lastrowid

        # Index in memory
        self.state.products.append(prod)
        self.state.bst.insert(prod.barcode, prod)
        self.state.trie.insert(prod.name.lower(), prod)

        return prod

    def edit_product(self, product_id: int, **fields) -> Optional[Product]:
        """Updates product metadata."""
        prod = self.state.get_product_by_id(product_id)
        if not prod:
            return None

        for k, v in fields.items():
            if hasattr(prod, k):
                setattr(prod, k, v)

        with self.conn:
            self.conn.execute("""
                UPDATE products
                SET name = ?, category_id = ?, cost_price = ?, selling_price = ?, reorder_level = ?
                WHERE id = ?;
            """, (prod.name, prod.category_id, prod.cost_price, prod.selling_price, prod.reorder_level, prod.id))

        return prod

    def delete_product(self, product_id: int) -> bool:
        """Soft deletes product by setting active = 0 and removing from search indices."""
        prod = self.state.get_product_by_id(product_id)
        if not prod:
            return False

        with self.conn:
            self.conn.execute("UPDATE products SET active = 0 WHERE id = ?;", (product_id,))

        prod.active = False
        # Remove from BST and Trie
        try:
            self.state.bst.delete(prod.barcode)
        except Exception:
            pass
        try:
            self.state.trie.delete(prod.name.lower())
        except Exception:
            pass

        return True

    def find_by_barcode(self, barcode: str) -> Optional[Product]:
        """O(log n) barcode lookup using custom BST."""
        return self.state.bst.find(barcode.strip())

    def search_by_name_prefix(self, prefix: str, limit: int = 8) -> List[Product]:
        """O(p) prefix search using custom Trie."""
        clean = prefix.strip().lower()
        if not clean:
            return []
        return self.state.trie.list_under_prefix(clean, limit=limit)
