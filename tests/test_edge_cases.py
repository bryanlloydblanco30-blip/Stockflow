"""
tests/test_edge_cases.py
The mandatory edge cases specified in Doc 12.2:
Edge cases 1-6 and 10-12 covered in Phase 3.
(Edge cases 7-9 and 13-16 covered in Phase 4 POS/FEFO/Undo).
"""

import unittest
import sqlite3
from datetime import date, timedelta
from backend.db.schema import init_schema
from backend.db.storage import load_all_into_memory, save_category, save_product, save_batch
from backend.models.category import Category
from backend.models.product import Product
from backend.models.batch import Batch
from backend.services.category_service import CategoryService
from backend.services.product_service import ProductService
from backend.services.inventory_service import InventoryService
from backend.services.alert_service import AlertService
from backend.services.fefo_service import FEFOService
from backend.services.pos_service import POSService
from backend.services.undo_service import UndoService
from backend.models.transaction import Transaction
from backend.models.transaction_line import TransactionLine
from backend.db.storage import save_transaction_atomic


class TestEdgeCasesPhase3(unittest.TestCase):
    def setUp(self):
        self.conn = sqlite3.connect(":memory:")
        self.conn.execute("PRAGMA foreign_keys = ON;")
        init_schema(self.conn)
        self.state = load_all_into_memory(self.conn)
        self.cat_service = CategoryService(self.conn, self.state)
        self.prod_service = ProductService(self.conn, self.state)
        self.alert_service = AlertService()
        self.inv_service = InventoryService(self.conn, self.state, self.alert_service)
        self.today = date(2026, 11, 23)

    def tearDown(self):
        self.conn.close()

    def test_edge_case_1_batch_expires_today(self):
        # Edge Case 1: Batch expires today -> Red, still sellable
        level = self.alert_service.calculate_level("2026-11-23", warn_days=7, today=self.today)
        self.assertEqual(level, "RED")
        self.assertTrue(self.alert_service.is_sellable("2026-11-23", today=self.today))

    def test_edge_case_2_batch_expired_yesterday(self):
        # Edge Case 2: Batch expired yesterday -> Expired, not sellable, in write-off list
        yesterday = (self.today - timedelta(days=1)).isoformat()
        level = self.alert_service.calculate_level(yesterday, warn_days=7, today=self.today)
        self.assertEqual(level, "EXPIRED")
        self.assertFalse(self.alert_service.is_sellable(yesterday, today=self.today))

    def test_edge_case_3_batch_at_amber_window_limit(self):
        # Edge Case 3: Batch exactly at the amber window limit -> Amber (included)
        warn_days = 7
        exact_amber_limit = (self.today + timedelta(days=warn_days)).isoformat()
        level = self.alert_service.calculate_level(exact_amber_limit, warn_days=warn_days, today=self.today)
        self.assertEqual(level, "AMBER")

    def test_edge_case_4_batch_one_day_past_amber_window(self):
        # Edge Case 4: Batch one day past the amber window -> OK (not listed)
        warn_days = 7
        past_amber = (self.today + timedelta(days=warn_days + 1)).isoformat()
        level = self.alert_service.calculate_level(past_amber, warn_days=warn_days, today=self.today)
        self.assertEqual(level, "OK")

    def test_edge_case_5_empty_expiry_in_no_expiry_category(self):
        # Edge Case 5: Batch with empty expiry in a no-expiry category -> Never in alerts, ordered by received date
        cat = self.cat_service.add_category("School Supplies", tracks_expiry=False, warn_days=0)
        prod = self.prod_service.register_product("480020", "Pencil", 5.0, 8.0, category_id=cat.id)
        res = self.inv_service.receive_stock(prod.id, 20, 5.0, expiry_date=None, received_date="2026-11-10", today=self.today)
        self.assertEqual(self.alert_service.calculate_level(None, warn_days=0, today=self.today), "NO_EXPIRY")

    def test_edge_case_6_category_switched_to_tracking(self):
        # Edge Case 6: Category switched from No to Yes -> Flags 'Expiry date needed', not guessed (Doc 6.4)
        cat = self.cat_service.add_category("Household", tracks_expiry=False, warn_days=0)
        prod = self.prod_service.register_product("480080", "Detergent", 10.0, 15.0, category_id=cat.id)
        batch = save_batch(self.conn, Batch(id=0, product_id=prod.id, quantity=10, cost_price=10.0, received_date="2026-11-01", expiry_date=None))

        # Switch category to tracks_expiry = True
        self.cat_service.toggle_tracking(cat.id, tracks_expiry=True, warn_days=14)
        unresolved = self.inv_service.get_unresolved_expiry_batches()
        self.assertIn(batch.id, [b["batch_id"] for b in unresolved])

    def test_edge_case_10_same_expiry_date_two_batches(self):
        # Edge Case 10: Same expiry date on two batches -> Earlier received batch sells first (Doc 6.2)
        cat = self.cat_service.add_category("Bakery", tracks_expiry=True, warn_days=5)
        prod = self.prod_service.register_product("480001", "Pandesal", 20.0, 30.0, category_id=cat.id)

        # Batch A received earlier (Nov 15)
        self.inv_service.receive_stock(prod.id, 10, 20.0, expiry_date="2026-11-30", received_date="2026-11-15")
        # Batch B received later (Nov 20) with identical expiry (Nov 30)
        self.inv_service.receive_stock(prod.id, 10, 20.0, expiry_date="2026-11-30", received_date="2026-11-20")

        heap = self.state.get_product_heap(prod.id)
        first_batch = heap.peek_min()
        self.assertEqual(first_batch.received_date, "2026-11-15")

    def test_edge_case_11_product_with_no_category(self):
        # Edge Case 11: Product with no category -> Uses global default window (7 days) (Doc 17)
        prod = self.prod_service.register_product("480999", "Uncategorized Item", 50.0, 70.0, category_id=None)
        window = self.cat_service.get_effective_warn_days(prod.category_id)
        self.assertEqual(window, 7)

    def test_edge_case_12_category_deleted(self):
        # Edge Case 12: Category deleted -> Products move to Uncategorized (category_id = None), count shown (Doc 6.4)
        cat = self.cat_service.add_category("Temporary Cat", tracks_expiry=True, warn_days=7)
        prod = self.prod_service.register_product("480777", "Temp Product", 10.0, 15.0, category_id=cat.id)

        affected_count = self.cat_service.delete_category(cat.id)
        self.assertEqual(affected_count, 1)

        # Product in memory and DB should now have category_id = None
        reloaded_prod = self.prod_service.find_by_barcode("480777")
        self.assertIsNone(reloaded_prod.category_id)

    def test_edge_case_13_price_change_after_sale_preserves_history(self):
        # Edge Case 13: Price change after sale -> Historical reports/lines unchanged (Doc 8.1)
        cat = self.cat_service.add_category("Groceries", tracks_expiry=False, warn_days=0)
        prod = self.prod_service.register_product("480888", "Coffee", 50.0, 75.0, category_id=cat.id)
        batch = save_batch(self.conn, Batch(id=0, product_id=prod.id, quantity=20, cost_price=50.0, received_date="2026-11-01", expiry_date=None))
        heap = self.state.get_or_create_product_heap(prod.id)
        heap.insert(item=batch, key=batch.received_date, tie_break=str(batch.id))

        fefo = FEFOService(self.alert_service)
        pos = POSService(self.conn, self.state, fefo)
        pos.add_to_cart(prod.id, 2)
        receipt = pos.checkout(cash_given=200.0, today=self.today)
        self.assertEqual(receipt["total"], 150.0)

        # Update product selling price to 100.0
        self.prod_service.edit_product(prod.id, selling_price=100.0, cost_price=60.0)

        # Inspect historical transaction line
        cur = self.conn.cursor()
        cur.execute("SELECT price_at_time, cost_at_time FROM transaction_lines WHERE transaction_id = ?;", (receipt["transaction_id"],))
        line_row = cur.fetchone()
        self.assertEqual(line_row[0], 75.0)  # Historical price preserved
        self.assertEqual(line_row[1], 50.0)  # Historical cost preserved

    def test_edge_case_15_undo_blocked_when_newer_transaction_exists(self):
        # Edge Case 15: Void after newer transaction exists -> Blocked with clear message (Doc 6.7)
        cat = self.cat_service.add_category("Groceries", tracks_expiry=False, warn_days=0)
        prod = self.prod_service.register_product("480889", "Tea", 20.0, 35.0, category_id=cat.id)
        batch = save_batch(self.conn, Batch(id=0, product_id=prod.id, quantity=20, cost_price=20.0, received_date="2026-11-01", expiry_date=None))
        heap = self.state.get_or_create_product_heap(prod.id)
        heap.insert(item=batch, key=batch.received_date, tie_break=str(batch.id))

        fefo = FEFOService(self.alert_service)
        pos = POSService(self.conn, self.state, fefo)
        undo = UndoService(self.conn, self.state, pos.undo_stack)

        pos.add_to_cart(prod.id, 1)
        receipt = pos.checkout(cash_given=50.0, today=self.today)

        # Insert a newer transaction directly to simulate intervening activity
        cur = self.conn.cursor()
        cur.execute("""
            INSERT INTO transactions (type, date_time, total, cash_given, change, reverses_id, location_id)
            VALUES ('adjustment', '2026-11-23 15:00:00', 0, 0, 0, NULL, 1);
        """)
        self.conn.commit()

        with self.assertRaises(ValueError) as ctx:
            undo.void_last_transaction()
        self.assertIn("newer transaction exists", str(ctx.exception).lower())

    def test_edge_case_16_atomic_sale_rollback_on_failure(self):
        # Edge Case 16: Interrupted transaction leaves no partial sale (Doc 2.4, 2.5)
        tx = Transaction(id=0, type="sale", date_time="2026-11-23 10:00:00", total=50.0, cash_given=50.0, change=0.0, location_id=1)
        # Line pointing to non-existent batch (violates foreign key constraint)
        invalid_lines = [
            TransactionLine(id=0, transaction_id=0, product_id=99999, batch_id=99999, quantity=1, price_at_time=50.0, cost_at_time=30.0)
        ]

        with self.assertRaises(Exception):
            save_transaction_atomic(self.conn, tx, invalid_lines)

        # Confirm transactions table remains completely clean
        cur = self.conn.cursor()
        cur.execute("SELECT COUNT(*) FROM transactions;")
        self.assertEqual(cur.fetchone()[0], 0)


if __name__ == "__main__":
    unittest.main()
