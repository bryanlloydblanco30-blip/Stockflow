"""
tests/test_services_reports.py
Comprehensive tests for Phase 5 (Tasks 5.1 to 5.7):
- Restock Service: Selling speed, days of cover, suggested reorder, Restock Max-Heap.
- Report Service: Prefix sums date-range queries, top-k/bottom-k via SizeKHeap,
  financial totals (Revenue, COGS, Profit, Margin, Spoilage, Inventory Value),
  and Dashboard numbers.
- Exit gate: Exact match with hand-calculated values on fixed dataset.
- Exclusion of voided sales from all reports.
"""

import unittest
import sqlite3
import math
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
from backend.services.inventory_service import InventoryService
from backend.services.restock_service import RestockService
from backend.services.report_service import ReportService


class TestPhase5RestockAndReports(unittest.TestCase):
    def setUp(self):
        self.conn = sqlite3.connect(":memory:")
        self.conn.execute("PRAGMA foreign_keys = ON;")
        init_schema(self.conn)
        self.state = load_all_into_memory(self.conn)

        self.alert_service = AlertService()
        self.fefo_service = FEFOService(self.alert_service)
        self.pos_service = POSService(self.conn, self.state, self.fefo_service)
        self.undo_service = UndoService(self.conn, self.state, self.pos_service.undo_stack)
        self.inv_service = InventoryService(self.conn, self.state, self.alert_service)
        self.restock_service = RestockService(self.conn, self.state, self.alert_service)
        self.report_service = ReportService(self.conn, self.state, self.alert_service)

        self.today = date(2026, 11, 23)

        # 1. Setup Fixed Dataset
        # Category A: Perishable Bakery (tracks_expiry=True, warn_days=14)
        self.cat_bakery = save_category(self.conn, Category(id=0, name="Bakery", tracks_expiry=True, warn_days=14))
        # Category B: Perishable Dairy (tracks_expiry=True, warn_days=10)
        self.cat_dairy = save_category(self.conn, Category(id=0, name="Dairy", tracks_expiry=True, warn_days=10))
        # Category C: Non-perishable Stationery (tracks_expiry=False, warn_days=0)
        self.cat_pens = save_category(self.conn, Category(id=0, name="Stationery", tracks_expiry=False, warn_days=0))
        self.state.categories.extend([self.cat_bakery, self.cat_dairy, self.cat_pens])

        # Products
        self.prod_bread = save_product(self.conn, Product(id=0, barcode="480001", name="Bread", cost_price=10.0, selling_price=20.0, category_id=self.cat_bakery.id, reorder_level=5))
        self.prod_milk = save_product(self.conn, Product(id=0, barcode="480002", name="Milk", cost_price=30.0, selling_price=50.0, category_id=self.cat_dairy.id, reorder_level=3))
        self.prod_pen = save_product(self.conn, Product(id=0, barcode="480003", name="Pen", cost_price=5.0, selling_price=10.0, category_id=self.cat_pens.id, reorder_level=10))

        self.state.products.extend([self.prod_bread, self.prod_milk, self.prod_pen])
        self.state.bst.insert(self.prod_bread.barcode, self.prod_bread)
        self.state.bst.insert(self.prod_milk.barcode, self.prod_milk)
        self.state.bst.insert(self.prod_pen.barcode, self.prod_pen)

        # Batches
        # Bread: Batch 1 (10 units, exp 2026-11-26 -> 3 days left -> RED), Batch 2 (10 units, exp 2026-12-03 -> 10 days left -> AMBER)
        self.b1 = save_batch(self.conn, Batch(id=0, product_id=self.prod_bread.id, quantity=10, cost_price=10.0, received_date="2026-11-15", expiry_date="2026-11-26"))
        self.b2 = save_batch(self.conn, Batch(id=0, product_id=self.prod_bread.id, quantity=10, cost_price=10.0, received_date="2026-11-18", expiry_date="2026-12-03"))
        heap_bread = self.state.get_or_create_product_heap(self.prod_bread.id)
        heap_bread.insert(item=self.b1, key=self.b1.expiry_date, tie_break=self.b1.received_date)
        heap_bread.insert(item=self.b2, key=self.b2.expiry_date, tie_break=self.b2.received_date)

        # Milk: Batch 3 (5 units, expired 2026-11-20), Batch 4 (10 units, exp 2026-12-13 -> 20 days left -> OK)
        self.b3 = save_batch(self.conn, Batch(id=0, product_id=self.prod_milk.id, quantity=5, cost_price=30.0, received_date="2026-11-01", expiry_date="2026-11-20"))
        self.b4 = save_batch(self.conn, Batch(id=0, product_id=self.prod_milk.id, quantity=10, cost_price=30.0, received_date="2026-11-10", expiry_date="2026-12-13"))
        heap_milk = self.state.get_or_create_product_heap(self.prod_milk.id)
        heap_milk.insert(item=self.b3, key=self.b3.expiry_date, tie_break=self.b3.received_date)
        heap_milk.insert(item=self.b4, key=self.b4.expiry_date, tie_break=self.b4.received_date)

        # Pen: Batch 5 (8 units, cost 5.0, untracked)
        self.b5 = save_batch(self.conn, Batch(id=0, product_id=self.prod_pen.id, quantity=8, cost_price=5.0, received_date="2026-11-05", expiry_date=None))
        heap_pen = self.state.get_or_create_product_heap(self.prod_pen.id)
        heap_pen.insert(item=self.b5, key=self.b5.received_date, tie_break=str(self.b5.id))

        # Perform Sales on specific dates:
        # Day 2026-11-20: Sale 1 (2 Bread)
        self.pos_service.add_to_cart(self.prod_bread.id, 2)
        self.pos_service.checkout(cash_given=50.0, today=date(2026, 11, 20))

        # Day 2026-11-20: Sale 2 (1 Bread) - then immediately voided
        self.pos_service.add_to_cart(self.prod_bread.id, 1)
        self.pos_service.checkout(cash_given=20.0, today=date(2026, 11, 20))
        self.undo_service.void_last_transaction(today=date(2026, 11, 20))

        # Day 2026-11-21: Sale 3 (4 Bread + 2 Milk)
        self.pos_service.add_to_cart(self.prod_bread.id, 4)
        self.pos_service.add_to_cart(self.prod_milk.id, 2)
        self.pos_service.checkout(cash_given=200.0, today=date(2026, 11, 21))

        # Day 2026-11-23 (Today): Sale 4 (2 Pens)
        self.pos_service.add_to_cart(self.prod_pen.id, 2)
        self.pos_service.checkout(cash_given=50.0, today=self.today)

        # Spoilage: Write off the 5 expired units of Milk (Batch 3)
        self.inv_service.write_off_expired(self.b3.id, reason="Expired dairy batch")

    def tearDown(self):
        self.conn.close()

    def test_task_5_6_financial_reports_exact_hand_calculated_values(self):
        """
        Verify Financial Totals:
        - Revenue: 40.0 (Sale 1) + 180.0 (Sale 3) + 20.0 (Sale 4) = 240.0
        - COGS: 20.0 + 100.0 + 10.0 = 130.0
        - Gross Profit: 240.0 - 130.0 = 110.0
        - Gross Margin: (110.0 / 240.0) * 100 = 45.83%
        - Spoilage: 5 * 30.0 = 150.0
        - Inventory Value at Cost: (14 * 10.0) + (8 * 30.0) + (6 * 5.0) = 140 + 240 + 30 = 410.0
        - Voided sale (Sale 2) strictly excluded from all numbers!
        """
        report = self.report_service.get_financial_summary(today=self.today)
        self.assertAlmostEqual(report["revenue"], 240.0, places=2)
        self.assertAlmostEqual(report["cogs"], 130.0, places=2)
        self.assertAlmostEqual(report["gross_profit"], 110.0, places=2)
        self.assertAlmostEqual(report["margin_pct"], 45.83, places=1)
        self.assertAlmostEqual(report["spoilage"], 150.0, places=2)
        self.assertAlmostEqual(report["inventory_value"], 410.0, places=2)

    def test_task_5_5_prefix_sums_daily_and_range_queries(self):
        """
        Tests Prefix Sums across the multi-day timeline:
        - Day 0 (2026-11-20): Revenue = 40.0
        - Day 1 (2026-11-21): Revenue = 180.0
        - Day 2 (2026-11-22): Revenue = 0.0
        - Day 3 (2026-11-23): Revenue = 20.0
        Range sum Day 0 to Day 1: 40 + 180 = 220.0
        Range sum Day 1 to Day 3: 180 + 0 + 20 = 200.0
        Range sum full (0 to 3): 240.0
        """
        prefix_sums = self.report_service.build_daily_prefix_sums(
            start_date=date(2026, 11, 20),
            end_date=date(2026, 11, 23),
        )
        self.assertEqual(prefix_sums["revenue"].size(), 4)
        self.assertAlmostEqual(prefix_sums["revenue"].range_sum(0, 1), 220.0, places=2)
        self.assertAlmostEqual(prefix_sums["revenue"].range_sum(1, 3), 200.0, places=2)
        self.assertAlmostEqual(prefix_sums["revenue"].range_sum(0, 3), 240.0, places=2)

    def test_task_5_4_top_and_bottom_sellers_via_size_k_heap(self):
        """
        Tests Size-k Heap analytics for top-k and bottom-k items:
        Bread sold 6 units. Milk sold 2 units. Pen sold 2 units.
        Top 1: Bread (6 units).
        """
        top_sellers = self.report_service.get_top_sellers(k=1, metric="units")
        self.assertEqual(len(top_sellers), 1)
        self.assertEqual(top_sellers[0]["product_name"], "Bread")
        self.assertEqual(top_sellers[0]["score"], 6)

        bottom_sellers = self.report_service.get_bottom_sellers(k=2, metric="units")
        self.assertEqual(len(bottom_sellers), 2)
        # Milk and Pen are tied at 2 units
        self.assertEqual(bottom_sellers[0]["score"], 2)
        self.assertEqual(bottom_sellers[1]["score"], 2)

    def test_task_5_7_dashboard_kpis(self):
        """
        RP-8 Dashboard Numbers for Today (2026-11-23):
        - Today's sales: 20.0
        - Today's profit: 10.0
        - Low stock count: Pen (sellable 6 < reorder 10) -> 1
        - Near expiry count: 2 batches (Batch 1 RED, Batch 2 AMBER). Non-perishable Pen ignored!
        """
        kpis = self.report_service.get_dashboard_kpis(today=self.today)
        self.assertAlmostEqual(kpis["today_sales"], 20.0, places=2)
        self.assertAlmostEqual(kpis["today_profit"], 10.0, places=2)
        self.assertEqual(kpis["low_stock_count"], 1)
        self.assertEqual(kpis["near_expiry_count"], 2)

    def test_tasks_5_1_to_5_3_restock_service(self):
        """
        Restock calculations (Doc 6.8):
        - Selling speed for Bread (14-day): 6 units / 14 days = 0.42857 units/day
        - Days of cover: 14 units / 0.42857 = 32.67 days
        - Suggested reorder for Pen:
          Pen has 6 sellable units. Speed = 2 / 14 = 0.14285 units/day.
          Target cover 14 days -> 0.14285 * 14 = 2. 2 - 6 = -4 -> Never below zero -> 0.
        - Restock Queue on MaxHeap:
          Pen has low stock (cover < reorder_level), ranked with reason text.
        """
        speed_bread = self.restock_service.calculate_selling_speed(self.prod_bread.id, days=14, today=self.today)
        self.assertAlmostEqual(speed_bread, 6.0 / 14.0, places=3)

        cover_bread = self.restock_service.calculate_days_of_cover(sellable_stock=14, selling_speed=speed_bread)
        self.assertAlmostEqual(cover_bread, 14.0 / (6.0 / 14.0), places=1)

        reorder = self.restock_service.calculate_suggested_reorder(selling_speed=speed_bread, sellable_stock=14, target_cover_days=14)
        self.assertEqual(reorder, 0)

        # Build restock queue using Max-Heap
        queue = self.restock_service.build_restock_queue(today=self.today)
        self.assertTrue(len(queue) > 0)
        # Pen is below reorder level (6 < 10)
        pen_entry = next((item for item in queue if item["product_id"] == self.prod_pen.id), None)
        self.assertIsNotNone(pen_entry)
        self.assertIn("reorder", pen_entry["reason"].lower())


if __name__ == "__main__":
    unittest.main()
