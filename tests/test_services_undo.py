"""
tests/test_services_undo.py
Unit tests for Task 4.7 & Decision D2 (Doc 6.7):
- Undo reverses only the most recent transaction, 1 level (Doc 6.7).
- Restores exact batches and quantities that were deducted.
- Re-inserts exhausted batches into the product's Min-Heap.
- Records a 'void' transaction referencing reverses_id.
- Edge Case 15: Blocked with clear message if a newer transaction exists.
- Undo of receive refused if any units were sold.
"""

import unittest
import sqlite3
from datetime import date
from backend.db.schema import init_schema
from backend.db.storage import load_all_into_memory, save_category, save_product, save_batch
from backend.models.category import Category
from backend.models.product import Product
from backend.models.batch import Batch
from backend.services.alert_service import AlertService
from backend.services.fefo_service import FEFOService
from backend.services.pos_service import POSService
from backend.services.undo_service import UndoService


class TestUndoService(unittest.TestCase):
    def setUp(self):
        self.conn = sqlite3.connect(":memory:")
        self.conn.execute("PRAGMA foreign_keys = ON;")
        init_schema(self.conn)
        self.state = load_all_into_memory(self.conn)
        self.alert_service = AlertService()
        self.fefo_service = FEFOService(self.alert_service)
        self.pos_service = POSService(self.conn, self.state, self.fefo_service)
        self.undo_service = UndoService(self.conn, self.state, self.pos_service.undo_stack)
        self.today = date(2026, 11, 23)

    def tearDown(self):
        self.conn.close()

    def test_undo_restores_exact_batches_and_exhausted_batch(self):
        # Setup product and 2 batches
        cat = save_category(self.conn, Category(id=0, name="Snacks", tracks_expiry=True, warn_days=10))
        prod = save_product(self.conn, Product(id=0, barcode="480055", name="Chips", cost_price=15.0, selling_price=25.0, category_id=cat.id))
        self.state.bst.insert(prod.barcode, prod)

        b1 = save_batch(self.conn, Batch(id=0, product_id=prod.id, quantity=3, cost_price=15.0, received_date="2026-11-15", expiry_date="2026-11-28"))
        b2 = save_batch(self.conn, Batch(id=0, product_id=prod.id, quantity=5, cost_price=15.0, received_date="2026-11-18", expiry_date="2026-12-05"))

        heap = self.state.get_or_create_product_heap(prod.id)
        heap.insert(item=b1, key=b1.expiry_date, tie_break=b1.received_date)
        heap.insert(item=b2, key=b2.expiry_date, tie_break=b2.received_date)

        # Sell 4 units: consumes all 3 of b1, and 1 of b2
        self.pos_service.add_to_cart(prod.id, 4)
        receipt = self.pos_service.checkout(cash_given=100.0, today=self.today)
        self.assertEqual(receipt["total"], 100.0)

        # In heap, b1 should be exhausted (gone), and b2 should have 4 units left
        self.assertEqual(heap.size(), 1)
        self.assertEqual(heap.peek_min().quantity, 4)

        # In SQLite: b1 has 0 units, b2 has 4 units
        cur = self.conn.cursor()
        cur.execute("SELECT id, quantity FROM batches ORDER BY id ASC;")
        rows = cur.fetchall()
        self.assertEqual(rows[0][1], 0)
        self.assertEqual(rows[1][1], 4)

        # Execute Undo
        void_tx = self.undo_service.void_last_transaction()
        self.assertEqual(void_tx.type, "void")
        self.assertEqual(void_tx.reverses_id, receipt["transaction_id"])

        # Check DB quantities restored: b1 -> 3, b2 -> 5
        cur.execute("SELECT id, quantity FROM batches ORDER BY id ASC;")
        rows = cur.fetchall()
        self.assertEqual(rows[0][1], 3)
        self.assertEqual(rows[1][1], 5)

        # Check in-memory heap restored: both batches present with full quantities
        self.assertEqual(heap.size(), 2)
        batches_in_heap = list(heap.ordered_read())
        self.assertEqual(batches_in_heap[0].id, b1.id)
        self.assertEqual(batches_in_heap[0].quantity, 3)
        self.assertEqual(batches_in_heap[1].id, b2.id)
        self.assertEqual(batches_in_heap[1].quantity, 5)

    def test_edge_case_15_undo_blocked_if_newer_transaction_exists(self):
        # Edge Case 15: Void after newer transaction exists -> Blocked with clear message (Doc 6.7)
        cat = save_category(self.conn, Category(id=0, name="Drinks", tracks_expiry=False, warn_days=0))
        prod = save_product(self.conn, Product(id=0, barcode="480099", name="Soda", cost_price=12.0, selling_price=20.0, category_id=cat.id))
        self.state.bst.insert(prod.barcode, prod)

        b = save_batch(self.conn, Batch(id=0, product_id=prod.id, quantity=20, cost_price=12.0, received_date="2026-11-20", expiry_date=None))
        heap = self.state.get_or_create_product_heap(prod.id)
        heap.insert(item=b, key=b.received_date, tie_break=str(b.id))

        # First sale
        self.pos_service.add_to_cart(prod.id, 1)
        receipt1 = self.pos_service.checkout(cash_given=20.0, today=self.today)

        # Second sale
        self.pos_service.add_to_cart(prod.id, 1)
        receipt2 = self.pos_service.checkout(cash_given=20.0, today=self.today)

        # Simulate tampering or a third independent transaction inserted directly in DB
        cur = self.conn.cursor()
        cur.execute("""
            INSERT INTO transactions (type, date_time, total, cash_given, change, reverses_id, location_id)
            VALUES ('adjustment', '2026-11-23 12:00:00', 0, 0, 0, NULL, 1);
        """)
        self.conn.commit()

        # Trying to undo should fail because a newer transaction exists
        with self.assertRaises(ValueError) as ctx:
            self.undo_service.void_last_transaction()
        self.assertIn("newer transaction exists", str(ctx.exception).lower())

    def test_undo_on_empty_stack_raises_error(self):
        with self.assertRaises(ValueError) as ctx:
            self.undo_service.void_last_transaction()
        self.assertIn("no transaction to undo", str(ctx.exception).lower())


if __name__ == "__main__":
    unittest.main()
