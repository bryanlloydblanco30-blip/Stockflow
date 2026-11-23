"""
tests/test_services_pos_fefo.py
Comprehensive unit tests for Phase 4:
- POS Cart backed by Doubly LinkedList (Task 4.2)
- Unified barcode entry (Task 4.1 & 4.9)
- FEFO and FIFO multi-batch deduction spanning batches (Task 4.4 / Doc 6.2)
- Checkout, cash validation, change in PHP (Task 4.3)
- Receipt data generated from cart traversal (Task 4.5 / POS-6)
- Low-stock check after sale (Task 4.8 / RS-1)
- Edge Cases 7, 8, 9, 14
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


class TestPOSFEFOService(unittest.TestCase):
    def setUp(self):
        self.conn = sqlite3.connect(":memory:")
        self.conn.execute("PRAGMA foreign_keys = ON;")
        init_schema(self.conn)
        self.state = load_all_into_memory(self.conn)
        self.alert_service = AlertService()
        self.fefo_service = FEFOService(self.alert_service)
        self.pos_service = POSService(self.conn, self.state, self.fefo_service)
        self.today = date(2026, 11, 23)

    def tearDown(self):
        self.conn.close()

    def test_barcode_entry_known_and_unknown(self):
        cat = save_category(self.conn, Category(id=0, name="Bakery", tracks_expiry=True, warn_days=5))
        prod = save_product(self.conn, Product(id=0, barcode="480036", name="Pandesal", cost_price=20.0, selling_price=30.0, category_id=cat.id))
        self.state.bst.insert(prod.barcode, prod)

        # 1. Known barcode
        res = self.pos_service.process_barcode_entry("480036")
        self.assertEqual(res["status"], "FOUND")
        self.assertEqual(res["product"].name, "Pandesal")

        # 2. Unknown barcode -> Signals UI to open Register Product (Doc 9.4 / Task 4.9)
        unknown_res = self.pos_service.process_barcode_entry("999999")
        self.assertEqual(unknown_res["status"], "UNKNOWN")
        self.assertEqual(unknown_res["barcode"], "999999")

    def test_cart_linked_list_operations(self):
        cat = save_category(self.conn, Category(id=0, name="Drinks", tracks_expiry=True, warn_days=14))
        p1 = save_product(self.conn, Product(id=0, barcode="480010", name="Water", cost_price=10.0, selling_price=15.0, category_id=cat.id))
        p2 = save_product(self.conn, Product(id=0, barcode="480011", name="Juice", cost_price=18.0, selling_price=25.0, category_id=cat.id))
        self.state.bst.insert(p1.barcode, p1)
        self.state.bst.insert(p2.barcode, p2)

        # Add P1 (qty 1)
        self.pos_service.add_to_cart(p1.id, quantity=1)
        self.assertEqual(self.pos_service.get_cart_item_count(), 1)
        self.assertEqual(self.pos_service.get_cart_total(), 15.0)

        # Add P1 again -> must merge into same line item (Doc 6.6 / Task 4.2)
        self.pos_service.add_to_cart(p1.id, quantity=2)
        self.assertEqual(self.pos_service.get_cart_item_count(), 1)
        self.assertEqual(self.pos_service.get_cart_total(), 45.0)

        # Add P2
        self.pos_service.add_to_cart(p2.id, quantity=1)
        self.assertEqual(self.pos_service.get_cart_item_count(), 2)
        self.assertEqual(self.pos_service.get_cart_total(), 70.0)

        # Update quantity
        self.pos_service.update_cart_quantity(p1.id, new_quantity=1)
        self.assertEqual(self.pos_service.get_cart_total(), 40.0)

        # Remove P2
        self.pos_service.remove_from_cart(p2.id)
        self.assertEqual(self.pos_service.get_cart_item_count(), 1)
        self.assertEqual(self.pos_service.get_cart_total(), 15.0)

    def test_edge_case_7_fefo_deduction_spanning_multiple_batches(self):
        # Edge Case 7: Sale needs more units than front batch has -> Takes rest from next batch, records both
        cat = save_category(self.conn, Category(id=0, name="Bakery", tracks_expiry=True, warn_days=5))
        prod = save_product(self.conn, Product(id=0, barcode="480036", name="Pandesal", cost_price=20.0, selling_price=30.0, category_id=cat.id))

        # Batch 1 (earlier expiry): 4 units at cost 20.0
        b1 = save_batch(self.conn, Batch(id=0, product_id=prod.id, quantity=4, cost_price=20.0, received_date="2026-11-20", expiry_date="2026-11-26"))
        # Batch 2 (later expiry): 10 units at cost 22.0
        b2 = save_batch(self.conn, Batch(id=0, product_id=prod.id, quantity=10, cost_price=22.0, received_date="2026-11-22", expiry_date="2026-12-05"))

        heap = self.state.get_or_create_product_heap(prod.id)
        heap.insert(item=b1, key=b1.expiry_date, tie_break=b1.received_date)
        heap.insert(item=b2, key=b2.expiry_date, tie_break=b2.received_date)

        # Deduct 6 units: should take 4 from Batch 1 and 2 from Batch 2
        allocations = self.fefo_service.deduct_stock(prod, quantity_needed=6, batch_min_heap=heap, today=self.today)
        self.assertEqual(len(allocations), 2)

        self.assertEqual(allocations[0]["batch_id"], b1.id)
        self.assertEqual(allocations[0]["quantity"], 4)
        self.assertEqual(allocations[0]["cost_at_time"], 20.0)

        self.assertEqual(allocations[1]["batch_id"], b2.id)
        self.assertEqual(allocations[1]["quantity"], 2)
        self.assertEqual(allocations[1]["cost_at_time"], 22.0)

        # Batch 1 should be exhausted and removed from heap; Batch 2 should have 8 units remaining
        self.assertEqual(heap.size(), 1)
        remaining = heap.peek_min()
        self.assertEqual(remaining.id, b2.id)
        self.assertEqual(remaining.quantity, 8)

    def test_edge_case_8_only_expired_stock_remains_sale_blocked(self):
        # Edge Case 8: Only expired stock remains -> Sale blocked with clear message (Decision D10)
        cat = save_category(self.conn, Category(id=0, name="Dairy", tracks_expiry=True, warn_days=5))
        prod = save_product(self.conn, Product(id=0, barcode="480037", name="Milk", cost_price=40.0, selling_price=55.0, category_id=cat.id))
        b_expired = save_batch(self.conn, Batch(id=0, product_id=prod.id, quantity=5, cost_price=40.0, received_date="2026-11-01", expiry_date="2026-11-20"))

        heap = self.state.get_or_create_product_heap(prod.id)
        heap.insert(item=b_expired, key=b_expired.expiry_date, tie_break=b_expired.received_date)

        with self.assertRaises(ValueError) as ctx:
            self.fefo_service.deduct_stock(prod, quantity_needed=1, batch_min_heap=heap, today=self.today)
        self.assertIn("expired", str(ctx.exception).lower())

    def test_edge_case_9_cart_mixed_tracked_and_untracked(self):
        # Edge Case 9: Cart has tracked and no-expiry product -> Each uses its own rule
        cat_exp = save_category(self.conn, Category(id=0, name="Bread", tracks_expiry=True, warn_days=5))
        cat_no = save_category(self.conn, Category(id=0, name="Pens", tracks_expiry=False, warn_days=0))

        p_tracked = save_product(self.conn, Product(id=0, barcode="480111", name="Bun", cost_price=10.0, selling_price=15.0, category_id=cat_exp.id))
        p_untracked = save_product(self.conn, Product(id=0, barcode="480222", name="Pen", cost_price=5.0, selling_price=8.0, category_id=cat_no.id))
        self.state.bst.insert(p_tracked.barcode, p_tracked)
        self.state.bst.insert(p_untracked.barcode, p_untracked)

        b_tracked = save_batch(self.conn, Batch(id=0, product_id=p_tracked.id, quantity=10, cost_price=10.0, received_date="2026-11-20", expiry_date="2026-11-28"))
        b_untracked = save_batch(self.conn, Batch(id=0, product_id=p_untracked.id, quantity=20, cost_price=5.0, received_date="2026-11-01", expiry_date=None))

        heap_t = self.state.get_or_create_product_heap(p_tracked.id)
        heap_t.insert(item=b_tracked, key=b_tracked.expiry_date, tie_break=b_tracked.received_date)

        heap_u = self.state.get_or_create_product_heap(p_untracked.id)
        heap_u.insert(item=b_untracked, key=b_untracked.received_date, tie_break=str(b_untracked.id))

        self.pos_service.add_to_cart(p_tracked.id, 2)
        self.pos_service.add_to_cart(p_untracked.id, 3)

        self.assertEqual(self.pos_service.get_cart_total(), 2 * 15.0 + 3 * 8.0)  # 30 + 24 = 54.0

        receipt = self.pos_service.checkout(cash_given=100.0, today=self.today)
        self.assertEqual(receipt["total"], 54.0)
        self.assertEqual(receipt["change"], 46.0)
        self.assertEqual(len(receipt["lines"]), 2)

    def test_edge_case_14_cash_less_than_total_blocked(self):
        # Edge Case 14: Cash less than total -> Payment blocked (Doc 6.6)
        cat = save_category(self.conn, Category(id=0, name="Bread", tracks_expiry=True, warn_days=5))
        p = save_product(self.conn, Product(id=0, barcode="480111", name="Bun", cost_price=10.0, selling_price=50.0, category_id=cat.id))
        self.state.bst.insert(p.barcode, p)
        b = save_batch(self.conn, Batch(id=0, product_id=p.id, quantity=10, cost_price=10.0, received_date="2026-11-20", expiry_date="2026-11-28"))
        heap = self.state.get_or_create_product_heap(p.id)
        heap.insert(item=b, key=b.expiry_date, tie_break=b.received_date)

        self.pos_service.add_to_cart(p.id, 1)

        with self.assertRaises(ValueError) as ctx:
            self.pos_service.checkout(cash_given=40.0, today=self.today)
        self.assertIn("insufficient", str(ctx.exception).lower())

    def test_low_stock_check_after_sale(self):
        # RS-1: Low stock notification triggered when sellable stock drops below reorder level
        cat = save_category(self.conn, Category(id=0, name="Bread", tracks_expiry=True, warn_days=5))
        p = save_product(self.conn, Product(id=0, barcode="480111", name="Bun", cost_price=10.0, selling_price=20.0, category_id=cat.id, reorder_level=5))
        self.state.bst.insert(p.barcode, p)
        b = save_batch(self.conn, Batch(id=0, product_id=p.id, quantity=6, cost_price=10.0, received_date="2026-11-20", expiry_date="2026-11-28"))
        heap = self.state.get_or_create_product_heap(p.id)
        heap.insert(item=b, key=b.expiry_date, tie_break=b.received_date)

        self.pos_service.add_to_cart(p.id, 2)  # 6 - 2 = 4 units left (below reorder_level 5)
        receipt = self.pos_service.checkout(cash_given=50.0, today=self.today)

        self.assertEqual(len(receipt["low_stock_alerts"]), 1)
        alert = receipt["low_stock_alerts"][0]
        self.assertEqual(alert["product_id"], p.id)
        self.assertEqual(alert["remaining_stock"], 4)
        self.assertEqual(alert["reorder_level"], 5)


if __name__ == "__main__":
    unittest.main()
