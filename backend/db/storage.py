"""
backend/db/storage.py
Persistence engine: Loads entities into custom in-memory data structures on start,
and writes transactions and state updates atomically to SQLite (Tasks 2.3 & 2.4).

HARD RULES COMPLIANCE:
- Zero imports of heapq, dict lookup shortcuts, or sorted for structure duties.
- Custom BST for barcode lookup.
- Custom Trie for lowercase product name prefix searching.
- Custom Min-Heap per product for FEFO batches.
- Category list stored in a plain dynamic array.
"""

from typing import Optional, List
import sqlite3

from backend.ds.bst import BST
from backend.ds.trie import Trie
from backend.ds.min_heap import MinHeap
from backend.models.category import Category
from backend.models.product import Product
from backend.models.batch import Batch
from backend.models.transaction import Transaction
from backend.models.transaction_line import TransactionLine


class StoreMemoryState:
    """
    In-memory state populated on application boot from SQLite.
    Maintains all primary indices on custom data structures written from scratch.
    """

    def __init__(self):
        # 1. Barcode index: Binary Search Tree (Task 1.5 / Doc 6.1)
        self.bst = BST()

        # 2. Name search index: Trie (Task 1.6 / Doc 6.1)
        self.trie = Trie()

        # 3. Association list of (product_id, MinHeap) for FEFO tracking (Task 1.3 / Doc 6.2)
        # Using a list of tuples to strictly adhere to custom data structures without built-in dicts
        self._product_heaps: List[tuple[int, MinHeap]] = []

        # 4. Categories dynamic array (Decision D13)
        self.categories: List[Category] = []

        # 5. Products list (for ID-based resolution without dict shortcuts)
        self.products: List[Product] = []

    def get_product_heap(self, product_id: int) -> Optional[MinHeap]:
        """Finds or returns the Min-Heap assigned to a product ID."""
        for pid, heap in self._product_heaps:
            if pid == product_id:
                return heap
        return None

    def get_or_create_product_heap(self, product_id: int) -> MinHeap:
        """Retrieves the Min-Heap for a product, or instantiates and attaches a new one."""
        existing = self.get_product_heap(product_id)
        if existing is not None:
            return existing
        new_heap = MinHeap()
        self._product_heaps.append((product_id, new_heap))
        return new_heap

    def get_product_by_id(self, product_id: int) -> Optional[Product]:
        """Finds a product entity by integer ID."""
        for p in self.products:
            if p.id == product_id:
                return p
        return None

    def get_category_by_id(self, category_id: int) -> Optional[Category]:
        """Finds a category entity by integer ID."""
        for c in self.categories:
            if c.id == category_id:
                return c
        return None


def load_all_into_memory(conn: sqlite3.Connection) -> StoreMemoryState:
    """
    Reads categories, active products, and available batches from SQLite.
    Populates BST, Trie, Min-Heaps, and category dynamic array (Task 2.3).
    """
    state = StoreMemoryState()
    cursor = conn.cursor()

    # 1. Load Categories
    cursor.execute("SELECT id, name, tracks_expiry, warn_days FROM categories ORDER BY id ASC;")
    for row in cursor.fetchall():
        cat = Category(
            id=row[0],
            name=row[1],
            tracks_expiry=bool(row[2]),
            warn_days=row[3],
        )
        state.categories.append(cat)

    # 2. Load Products into BST and Trie
    cursor.execute("""
        SELECT id, barcode, name, category_id, cost_price, selling_price, reorder_level, location_id, active
        FROM products
        WHERE active = 1
        ORDER BY id ASC;
    """)
    for row in cursor.fetchall():
        prod = Product(
            id=row[0],
            barcode=row[1],
            name=row[2],
            category_id=row[3],
            cost_price=row[4],
            selling_price=row[5],
            reorder_level=row[6],
            location_id=row[7],
            active=bool(row[8]),
        )
        state.products.append(prod)

        # Index in BST by barcode
        state.bst.insert(prod.barcode, prod)

        # Index in Trie by lowercase product name
        state.trie.insert(prod.name.lower(), prod)

    # 3. Load Batches into per-product Min-Heaps (FEFO order)
    cursor.execute("""
        SELECT id, product_id, quantity, cost_price, received_date, expiry_date, moved_to_front
        FROM batches
        WHERE quantity > 0
        ORDER BY id ASC;
    """)
    for row in cursor.fetchall():
        batch = Batch(
            id=row[0],
            product_id=row[1],
            quantity=row[2],
            cost_price=row[3],
            received_date=row[4],
            expiry_date=row[5],
            moved_to_front=bool(row[6]),
        )

        heap = state.get_or_create_product_heap(batch.product_id)

        # FEFO key logic (Decision D3 & D8):
        # Perishable items: key = expiry_date, tie-break = received_date
        # No-expiry items: key = received_date, tie-break = batch.id
        if batch.expiry_date:
            heap.insert(
                item=batch,
                key=batch.expiry_date,
                tie_break=batch.received_date,
            )
        else:
            heap.insert(
                item=batch,
                key=batch.received_date,
                tie_break=str(batch.id),
            )

    return state


def save_category(conn: sqlite3.Connection, category: Category) -> Category:
    """Inserts or updates a Category record in SQLite."""
    with conn:
        cursor = conn.cursor()
        if category.id == 0:
            cursor.execute(
                "INSERT INTO categories (name, tracks_expiry, warn_days) VALUES (?, ?, ?);",
                (category.name, int(category.tracks_expiry), category.warn_days),
            )
            category.id = cursor.lastrowid
        else:
            cursor.execute(
                "UPDATE categories SET name = ?, tracks_expiry = ?, warn_days = ? WHERE id = ?;",
                (category.name, int(category.tracks_expiry), category.warn_days, category.id),
            )
    return category


def save_product(conn: sqlite3.Connection, product: Product) -> Product:
    """Inserts or updates a Product record in SQLite."""
    with conn:
        cursor = conn.cursor()
        if product.id == 0:
            cursor.execute("""
                INSERT INTO products (barcode, name, category_id, cost_price, selling_price, reorder_level, location_id, active)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?);
            """, (
                product.barcode,
                product.name,
                product.category_id,
                product.cost_price,
                product.selling_price,
                product.reorder_level,
                product.location_id,
                int(product.active),
            ))
            product.id = cursor.lastrowid
        else:
            cursor.execute("""
                UPDATE products
                SET barcode = ?, name = ?, category_id = ?, cost_price = ?, selling_price = ?,
                    reorder_level = ?, location_id = ?, active = ?
                WHERE id = ?;
            """, (
                product.barcode,
                product.name,
                product.category_id,
                product.cost_price,
                product.selling_price,
                product.reorder_level,
                product.location_id,
                int(product.active),
                product.id,
            ))
    return product


def save_batch(conn: sqlite3.Connection, batch: Batch) -> Batch:
    """Inserts or updates a Batch record in SQLite."""
    with conn:
        cursor = conn.cursor()
        if batch.id == 0:
            cursor.execute("""
                INSERT INTO batches (product_id, quantity, cost_price, received_date, expiry_date, moved_to_front)
                VALUES (?, ?, ?, ?, ?, ?);
            """, (
                batch.product_id,
                batch.quantity,
                batch.cost_price,
                batch.received_date,
                batch.expiry_date,
                int(batch.moved_to_front),
            ))
            batch.id = cursor.lastrowid
        else:
            cursor.execute("""
                UPDATE batches
                SET product_id = ?, quantity = ?, cost_price = ?, received_date = ?, expiry_date = ?, moved_to_front = ?
                WHERE id = ?;
            """, (
                batch.product_id,
                batch.quantity,
                batch.cost_price,
                batch.received_date,
                batch.expiry_date,
                int(batch.moved_to_front),
                batch.id,
            ))
    return batch


def save_transaction_atomic(
    conn: sqlite3.Connection,
    transaction: Transaction,
    lines: List[TransactionLine],
) -> Transaction:
    """
    Writes a completed sale and its line items in a single atomic transaction (Task 2.4).
    Deducts batch quantities simultaneously. Rollbacks entirely if any step fails.
    """
    with conn:
        cursor = conn.cursor()

        # 1. Insert transaction header
        cursor.execute("""
            INSERT INTO transactions (type, date_time, total, cash_given, change, reverses_id, location_id)
            VALUES (?, ?, ?, ?, ?, ?, ?);
        """, (
            transaction.type,
            transaction.date_time,
            transaction.total,
            transaction.cash_given,
            transaction.change,
            transaction.reverses_id,
            transaction.location_id,
        ))
        transaction.id = cursor.lastrowid

        # 2. Insert transaction lines & decrement corresponding batch quantities
        for line in lines:
            line.transaction_id = transaction.id
            cursor.execute("""
                INSERT INTO transaction_lines (transaction_id, product_id, batch_id, quantity, price_at_time, cost_at_time)
                VALUES (?, ?, ?, ?, ?, ?);
            """, (
                line.transaction_id,
                line.product_id,
                line.batch_id,
                line.quantity,
                line.price_at_time,
                line.cost_at_time,
            ))
            line.id = cursor.lastrowid

            # Deduct quantity from batch
            cursor.execute("""
                UPDATE batches
                SET quantity = quantity - ?
                WHERE id = ?;
            """, (line.quantity, line.batch_id))

    return transaction
