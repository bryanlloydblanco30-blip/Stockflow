"""
tests/test_models_storage.py
Tests for SQLite schema, atomic sale persistence, and save/load (Task 2.5 / Phase 2 Exit Gate).
"""

import unittest
import sqlite3
from backend.db.schema import init_schema
from backend.db.storage import (
    load_all_into_memory,
    save_transaction_atomic,
    save_product,
    save_batch,
    save_category,
    StoreMemoryState,
)
from backend.models.category import Category
from backend.models.product import Product
from backend.models.batch import Batch
from backend.models.transaction import Transaction
from backend.models.transaction_line import TransactionLine


class TestModelsStorage(unittest.TestCase):
    def setUp(self):
        self.conn = sqlite3.connect(":memory:")
        self.conn.execute("PRAGMA foreign_keys = ON;")
        init_schema(self.conn)

    def tearDown(self):
        self.conn.close()

    def test_schema_init(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT version FROM schema_version")
        row = cursor.fetchone()
        self.assertEqual(row[0], 1)

    def test_save_category_and_product(self):
        cat = Category(id=0, name="Bakery", tracks_expiry=True, warn_days=5)
        saved_cat = save_category(self.conn, cat)
        self.assertGreater(saved_cat.id, 0)
        self.assertEqual(saved_cat.name, "Bakery")
        self.assertEqual(saved_cat.red_days, 2)

        prod = Product(
            id=0,
            barcode="4800361000014",
            name="Pandesal 10s",
            category_id=saved_cat.id,
            cost_price=22.0,
            selling_price=30.0,
            reorder_level=10,
        )
        saved_prod = save_product(self.conn, prod)
        self.assertGreater(saved_prod.id, 0)
        self.assertEqual(saved_prod.barcode, "4800361000014")

    def test_load_all_into_memory(self):
        # 1. Seed Categories
        cat1 = save_category(self.conn, Category(id=0, name="Bakery", tracks_expiry=True, warn_days=5))
        cat2 = save_category(self.conn, Category(id=0, name="School Supplies", tracks_expiry=False, warn_days=0))

        # 2. Seed Products
        p1 = save_product(self.conn, Product(id=0, barcode="480001", name="Pandesal pack", category_id=cat1.id, cost_price=20.0, selling_price=30.0, reorder_level=5))
        p2 = save_product(self.conn, Product(id=0, barcode="480002", name="Mongol Pencil", category_id=cat2.id, cost_price=5.0, selling_price=8.0, reorder_level=10))

        # 3. Seed Batches (P1 has 2 batches with different expiries)
        b1_earlier = save_batch(self.conn, Batch(id=0, product_id=p1.id, quantity=10, cost_price=20.0, received_date="2026-11-20", expiry_date="2026-11-25"))
        b1_later = save_batch(self.conn, Batch(id=0, product_id=p1.id, quantity=15, cost_price=20.0, received_date="2026-11-22", expiry_date="2026-12-01"))
        b2_untracked = save_batch(self.conn, Batch(id=0, product_id=p2.id, quantity=50, cost_price=5.0, received_date="2026-11-15", expiry_date=None))

        # Load into memory
        state: StoreMemoryState = load_all_into_memory(self.conn)

        # A. BST verification: lookup by barcode
        found_p1 = state.bst.find("480001")
        self.assertIsNotNone(found_p1)
        self.assertEqual(found_p1.name, "Pandesal pack")

        found_p2 = state.bst.find("480002")
        self.assertIsNotNone(found_p2)
        self.assertEqual(found_p2.name, "Mongol Pencil")

        self.assertIsNone(state.bst.find("999999"))

        # B. Trie verification: prefix search
        matches = state.trie.list_under_prefix("pan", limit=8)
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0].name, "Pandesal pack")

        matches_pencil = state.trie.list_under_prefix("mon", limit=8)
        self.assertEqual(len(matches_pencil), 1)
        self.assertEqual(matches_pencil[0].name, "Mongol Pencil")

        # C. Min-Heap verification: FEFO order for P1
        heap_p1 = state.get_product_heap(p1.id)
        self.assertIsNotNone(heap_p1)
        self.assertEqual(heap_p1.size(), 2)

        # Earliest expiry should be first
        earliest_batch = heap_p1.peek_min()
        self.assertEqual(earliest_batch.id, b1_earlier.id)
        self.assertEqual(earliest_batch.expiry_date, "2026-11-25")

        # Untracked category uses received_date as key
        heap_p2 = state.get_product_heap(p2.id)
        self.assertIsNotNone(heap_p2)
        self.assertEqual(heap_p2.size(), 1)
        self.assertEqual(heap_p2.peek_min().id, b2_untracked.id)

    def test_save_transaction_atomic_success(self):
        cat = save_category(self.conn, Category(id=0, name="Drinks", tracks_expiry=True, warn_days=14))
        p = save_product(self.conn, Product(id=0, barcode="480010", name="Water 500ml", category_id=cat.id, cost_price=10.0, selling_price=15.0))
        b = save_batch(self.conn, Batch(id=0, product_id=p.id, quantity=20, cost_price=10.0, received_date="2026-11-01", expiry_date="2027-01-01"))

        # Create a sale of 5 units
        tx = Transaction(
            id=0,
            type="sale",
            date_time="2026-11-23 10:30:00",
            total=75.0,
            cash_given=100.0,
            change=25.0,
        )
        lines = [
            TransactionLine(
                id=0,
                transaction_id=0,
                product_id=p.id,
                batch_id=b.id,
                quantity=5,
                price_at_time=15.0,
                cost_at_time=10.0,
            )
        ]

        saved_tx = save_transaction_atomic(self.conn, tx, lines)
        self.assertGreater(saved_tx.id, 0)

        # Verify transaction and lines are stored
        cur = self.conn.cursor()
        cur.execute("SELECT total, cash_given, change FROM transactions WHERE id = ?", (saved_tx.id,))
        tx_row = cur.fetchone()
        self.assertEqual(tx_row[0], 75.0)
        self.assertEqual(tx_row[1], 100.0)
        self.assertEqual(tx_row[2], 25.0)

        cur.execute("SELECT quantity, price_at_time FROM transaction_lines WHERE transaction_id = ?", (saved_tx.id,))
        line_row = cur.fetchone()
        self.assertEqual(line_row[0], 5)
        self.assertEqual(line_row[1], 15.0)

        # Verify batch was decremented from 20 -> 15
        cur.execute("SELECT quantity FROM batches WHERE id = ?", (b.id,))
        self.assertEqual(cur.fetchone()[0], 15)

    def test_save_transaction_atomic_rollback_on_failure(self):
        cat = save_category(self.conn, Category(id=0, name="Drinks", tracks_expiry=True, warn_days=14))
        p = save_product(self.conn, Product(id=0, barcode="480010", name="Water 500ml", category_id=cat.id, cost_price=10.0, selling_price=15.0))
        b = save_batch(self.conn, Batch(id=0, product_id=p.id, quantity=10, cost_price=10.0, received_date="2026-11-01", expiry_date="2027-01-01"))

        tx = Transaction(id=0, type="sale", date_time="2026-11-23 10:30:00", total=30.0, cash_given=50.0, change=20.0)
        # Line 2 intentionally references an invalid product_id=9999 to trigger foreign key constraint failure
        lines = [
            TransactionLine(id=0, transaction_id=0, product_id=p.id, batch_id=b.id, quantity=2, price_at_time=15.0, cost_at_time=10.0),
            TransactionLine(id=0, transaction_id=0, product_id=99999, batch_id=b.id, quantity=1, price_at_time=15.0, cost_at_time=10.0),
        ]

        with self.assertRaises(sqlite3.IntegrityError):
            save_transaction_atomic(self.conn, tx, lines)

        # Entire transaction must have rolled back: no tx inserted, batch unchanged
        cur = self.conn.cursor()
        cur.execute("SELECT COUNT(*) FROM transactions")
        self.assertEqual(cur.fetchone()[0], 0)

        cur.execute("SELECT COUNT(*) FROM transaction_lines")
        self.assertEqual(cur.fetchone()[0], 0)

        cur.execute("SELECT quantity FROM batches WHERE id = ?", (b.id,))
        self.assertEqual(cur.fetchone()[0], 10)  # Unchanged!

    def test_save_then_load_gives_identical_data(self):
        # 1. Populate
        cat = save_category(self.conn, Category(id=0, name="Bakery", tracks_expiry=True, warn_days=5))
        p = save_product(self.conn, Product(id=0, barcode="480111", name="Loaf bread", category_id=cat.id, cost_price=40.0, selling_price=55.0, reorder_level=8))
        b = save_batch(self.conn, Batch(id=0, product_id=p.id, quantity=14, cost_price=40.0, received_date="2026-11-20", expiry_date="2026-11-28"))

        # 2. First load
        state1 = load_all_into_memory(self.conn)

        # 3. Simulate another connection reading the exact same database
        state2 = load_all_into_memory(self.conn)

        # Assert identical in-memory values
        p_from_s1 = state1.bst.find("480111")
        p_from_s2 = state2.bst.find("480111")
        self.assertEqual(p_from_s1.name, p_from_s2.name)
        self.assertEqual(p_from_s1.cost_price, p_from_s2.cost_price)
        self.assertEqual(p_from_s1.selling_price, p_from_s2.selling_price)

        batch_s1 = state1.get_product_heap(p.id).peek_min()
        batch_s2 = state2.get_product_heap(p.id).peek_min()
        self.assertEqual(batch_s1.id, batch_s2.id)
        self.assertEqual(batch_s1.quantity, batch_s2.quantity)
        self.assertEqual(batch_s1.expiry_date, batch_s2.expiry_date)


if __name__ == "__main__":
    unittest.main()
