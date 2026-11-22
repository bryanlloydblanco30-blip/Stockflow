"""
tests/test_services_inventory.py
Tests for inventory receiving, batch tracking, shelf-rotation, and write-offs (Phase 3).
"""

import unittest
from backend.models.category import Category


class TestInventoryService(unittest.TestCase):
    def test_category_red_days_calculation(self):
        # Doc 6.3 / D7: 3 -> 1, 5 -> 2, 7 -> 2, 14 -> 5, 30 -> 10
        c3 = Category(id=1, name="Bread", warn_days=3)
        c5 = Category(id=2, name="Dairy", warn_days=5)
        c7 = Category(id=3, name="Snacks", warn_days=7)
        c14 = Category(id=4, name="Drinks", warn_days=14)
        c30 = Category(id=5, name="Canned", warn_days=30)
        self.assertEqual(c3.red_days, 1)
        self.assertEqual(c5.red_days, 2)
        self.assertEqual(c7.red_days, 2)
        self.assertEqual(c14.red_days, 5)
        self.assertEqual(c30.red_days, 10)

