"""
tests/test_api_server.py
Integration tests for the stdlib HTTP API backend container (backend/api_server.py).
"""

import tempfile
import unittest
from pathlib import Path
from datetime import date, timedelta

from backend.api_server import StockFlowBackend


class TestStockFlowBackendAPI(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.tmpdir.name) / "test_api.db"
        self.api = StockFlowBackend(db_path=self.db_path, auto_seed=False)

    def tearDown(self):
        self.api.conn.close()
        self.tmpdir.cleanup()

    def test_full_api_workflow(self):
        # 1. Category & product registration
        cat = self.api.create_category({"name": "Bakery", "tracks_expiry": True, "warn_days": 7})
        self.assertEqual(cat["name"], "Bakery")

        exp_soon = (date.today() + timedelta(days=2)).isoformat()
        prod = self.api.create_product({
            "barcode": "4800000001",
            "name": "Pandesal Pack",
            "category_id": cat["id"],
            "cost_price": 20.0,
            "selling_price": 30.0,
            "reorder_level": 5,
            "initial_stock": 10,
            "expiry_date": exp_soon,
        })
        self.assertEqual(prod["sellable_stock"], 10)
        self.assertEqual(prod["alert_level"], "RED")

        # 2. Scan barcode (BST) & Trie prefix search
        scan = self.api.scan_barcode("4800000001")
        self.assertEqual(scan["status"], "FOUND")
        unknown = self.api.scan_barcode("9999999999")
        self.assertEqual(unknown["status"], "UNKNOWN")

        found_trie = self.api.search_products("pan")
        self.assertEqual(len(found_trie), 1)

        # 3. Cart + Checkout (FEFO) + Undo
        add_res = self.api.add_to_cart({"barcode": "4800000001", "quantity": 3})
        self.assertEqual(add_res["status"], "OK")
        self.assertEqual(add_res["cart"]["total"], 90.0)

        receipt = self.api.checkout({"cash_given": 100.0})
        self.assertEqual(receipt["total"], 90.0)
        self.assertEqual(receipt["change"], 10.0)

        # Stock should be 7 now
        products = self.api.get_products()
        self.assertEqual(products[0]["sellable_stock"], 7)

        # Undo should restore stock to 10
        void_res = self.api.undo_last()
        self.assertEqual(void_res["reverses_id"], receipt["transaction_id"])
        products_after_undo = self.api.get_products()
        self.assertEqual(products_after_undo[0]["sellable_stock"], 10)

        # 4. Alerts, Restock, Reports, Settings
        alerts = self.api.get_alerts()
        self.assertEqual(len(alerts["near_expiry"]), 1)

        restock = self.api.get_restock()
        self.assertEqual(len(restock["queue"]), 1)

        reports = self.api.get_reports(period="Week")
        self.assertEqual(reports["summary"]["revenue"], 0.0)

        settings = self.api.update_settings({"store_name": "My Store", "target_cover_days": 21})
        self.assertEqual(settings["store_name"], "My Store")
        self.assertEqual(settings["target_cover_days"], 21)


if __name__ == "__main__":
    unittest.main()
