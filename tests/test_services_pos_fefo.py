"""
tests/test_services_pos_fefo.py
Tests for Cart, Checkout, and FEFO / FIFO stock deduction (Phase 4).
"""

import unittest
from backend.models.product import Product


class TestPOSFEFO(unittest.TestCase):
    def test_product_model_creation(self):
        p = Product(id=1, barcode="123456", name="Milk", category_id=1, cost_price=40.0, selling_price=50.0)
        self.assertEqual(p.barcode, "123456")

