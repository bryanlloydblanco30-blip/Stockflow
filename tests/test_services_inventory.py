"""
tests/test_services_inventory.py
Comprehensive unit tests for Phase 3 domain services:
- CategoryService (Task 3.1 & 3.9)
- ProductService (Task 3.2)
- InventoryService (Task 3.3, 3.4, 3.6, 3.7, 3.8)
- AlertService (Task 3.5 / Doc 6.3)
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


class TestInventoryService(unittest.TestCase):
    def setUp(self):
        self.conn = sqlite3.connect(":memory:")
        self.conn.execute("PRAGMA foreign_keys = ON;")
        init_schema(self.conn)
        self.state = load_all_into_memory(self.conn)
        self.cat_service = CategoryService(self.conn, self.state)
        self.prod_service = ProductService(self.conn, self.state)
        self.alert_service = AlertService()
        self.inv_service = InventoryService(self.conn, self.state, self.alert_service)

    def tearDown(self):
        self.conn.close()

    def test_category_red_days_calculation(self):
        # Doc 6.3 / D7: 3 -> 1, 5 -> 2, 7 -> 2, 14 -> 5, 30 -> 10
        self.assertEqual(Category(id=1, name="Bread", warn_days=3).red_days, 1)
        self.assertEqual(Category(id=2, name="Dairy", warn_days=5).red_days, 2)
        self.assertEqual(Category(id=3, name="Snacks", warn_days=7).red_days, 2)
        self.assertEqual(Category(id=4, name="Drinks", warn_days=14).red_days, 5)
        self.assertEqual(Category(id=5, name="Canned", warn_days=30).red_days, 10)

    def test_category_service_crud_and_rename(self):
        cat = self.cat_service.add_category("Bakery", tracks_expiry=True, warn_days=5)
        self.assertGreater(cat.id, 0)
        self.assertEqual(cat.name, "Bakery")
        self.assertEqual(cat.red_days, 2)

        # In-memory and DB consistency
        self.assertIsNotNone(self.state.get_category_by_id(cat.id))

        # Rename
        renamed = self.cat_service.rename_category(cat.id, "Baked Goods")
        self.assertEqual(renamed.name, "Baked Goods")
        self.assertEqual(self.state.get_category_by_id(cat.id).name, "Baked Goods")

    def test_product_service_register_search_and_soft_delete(self):
        cat = self.cat_service.add_category("Beverages", tracks_expiry=True, warn_days=14)
        prod = self.prod_service.register_product(
            barcode="4800111300018",
            name="Coca-Cola Sakto 200ml",
            cost=11.0,
            price=15.0,
            category_id=cat.id,
            reorder_level=20,
        )

        # 1. BST Barcode search
        found_by_barcode = self.prod_service.find_by_barcode("4800111300018")
        self.assertIsNotNone(found_by_barcode)
        self.assertEqual(found_by_barcode.name, "Coca-Cola Sakto 200ml")

        # 2. Trie Prefix search (case-insensitive)
        prefix_matches = self.prod_service.search_by_name_prefix("coca")
        self.assertEqual(len(prefix_matches), 1)
        self.assertEqual(prefix_matches[0].barcode, "4800111300018")

        # 3. Soft delete
        self.prod_service.delete_product(prod.id)
        self.assertIsNone(self.prod_service.find_by_barcode("4800111300018"))
        self.assertEqual(len(self.prod_service.search_by_name_prefix("coca")), 0)

    def test_alert_service_levels(self):
        today = date(2026, 11, 23)
        warn_days = 6  # red_limit = round(6/3) = 2

        # Expired: days < 0
        self.assertEqual(self.alert_service.calculate_level("2026-11-22", warn_days, today), "EXPIRED")
        # Red: 0 <= days <= red_limit (2 days)
        self.assertEqual(self.alert_service.calculate_level("2026-11-23", warn_days, today), "RED")
        self.assertEqual(self.alert_service.calculate_level("2026-11-25", warn_days, today), "RED")
        # Amber: red_limit < days <= warn_days (3 to 6 days)
        self.assertEqual(self.alert_service.calculate_level("2026-11-26", warn_days, today), "AMBER")
        self.assertEqual(self.alert_service.calculate_level("2026-11-29", warn_days, today), "AMBER")
        # OK: days > warn_days (> 6 days)
        self.assertEqual(self.alert_service.calculate_level("2026-11-30", warn_days, today), "OK")
        # Untracked: No expiry date
        self.assertEqual(self.alert_service.calculate_level(None, warn_days, today), "NO_EXPIRY")

    def test_receive_stock_and_older_stock_message(self):
        cat = self.cat_service.add_category("Dairy", tracks_expiry=True, warn_days=7)
        prod = self.prod_service.register_product(
            barcode="4800145400059",
            name="Selecta Fresh Milk 1L",
            cost=92.0,
            price=112.0,
            category_id=cat.id,
        )

        today = date(2026, 11, 23)

        # Batch 1: Expiring in 4 days (2026-11-27)
        res1 = self.inv_service.receive_stock(
            product_id=prod.id,
            quantity=5,
            cost=92.0,
            expiry_date="2026-11-27",
            received_date="2026-11-23",
            today=today,
        )
        self.assertEqual(len(res1.older_batches_warning), 0)

        # Batch 2: Newly received with a LATER expiry (2026-12-15)
        # IN-5: Must return warning that older stock (Batch 1, 5 units) still exists!
        res2 = self.inv_service.receive_stock(
            product_id=prod.id,
            quantity=10,
            cost=92.0,
            expiry_date="2026-12-15",
            received_date="2026-11-23",
            today=today,
        )
        self.assertEqual(len(res2.older_batches_warning), 1)
        older = res2.older_batches_warning[0]
        self.assertEqual(older["expiry_date"], "2026-11-27")
        self.assertEqual(older["units"], 5)
        self.assertEqual(older["level"], "AMBER")

    def test_shelf_rotation_flag(self):
        cat = self.cat_service.add_category("Bakery", tracks_expiry=True, warn_days=5)
        prod = self.prod_service.register_product(barcode="480036", name="Bread", cost=20.0, price=30.0, category_id=cat.id)
        batch = save_batch(self.conn, Batch(id=0, product_id=prod.id, quantity=10, cost_price=20.0, received_date="2026-11-20", expiry_date="2026-11-25"))
        self.assertFalse(batch.moved_to_front)

        # Mark shelf rotated
        self.inv_service.mark_shelf_rotated(batch.id)
        cur = self.conn.cursor()
        cur.execute("SELECT moved_to_front FROM batches WHERE id = ?", (batch.id,))
        self.assertEqual(cur.fetchone()[0], 1)

    def test_write_off_expired_batch(self):
        cat = self.cat_service.add_category("Dairy", tracks_expiry=True, warn_days=5)
        prod = self.prod_service.register_product(barcode="480037", name="Yogurt", cost=30.0, price=45.0, category_id=cat.id)
        batch = save_batch(self.conn, Batch(id=0, product_id=prod.id, quantity=4, cost_price=30.0, received_date="2026-11-01", expiry_date="2026-11-15"))

        loss_record = self.inv_service.write_off_expired(batch.id, reason="Expired on shelf")
        self.assertEqual(loss_record["units_lost"], 4)
        self.assertEqual(loss_record["loss_amount"], 120.0)

        # Quantity in batches should now be 0
        cur = self.conn.cursor()
        cur.execute("SELECT quantity FROM batches WHERE id = ?", (batch.id,))
        self.assertEqual(cur.fetchone()[0], 0)

    def test_adjust_stock_count_and_reason(self):
        cat = self.cat_service.add_category("Canned", tracks_expiry=True, warn_days=30)
        prod = self.prod_service.register_product(barcode="480038", name="Sardines", cost=15.0, price=20.0, category_id=cat.id)
        batch = save_batch(self.conn, Batch(id=0, product_id=prod.id, quantity=10, cost_price=15.0, received_date="2026-11-01", expiry_date="2027-11-01"))

        # Adjust from 10 to 7 units
        adj = self.inv_service.adjust_stock(batch.id, new_quantity=7, reason="Physical shelf check: 3 damaged cans")
        self.assertEqual(adj["old_quantity"], 10)
        self.assertEqual(adj["new_quantity"], 7)
        self.assertEqual(adj["difference"], -3)

        cur = self.conn.cursor()
        cur.execute("SELECT quantity FROM batches WHERE id = ?", (batch.id,))
        self.assertEqual(cur.fetchone()[0], 7)


if __name__ == "__main__":
    unittest.main()
