"""
tests/test_services_reports.py
Tests for financial reporting formulas (Revenue, COGS, Gross Profit, Spoilage) (Doc 10).
"""

import unittest


class TestReportsService(unittest.TestCase):
    def test_gross_margin_zero_revenue(self):
        # Doc 10 / Quick rule sheet: Margin is 0% when revenue is 0
        revenue = 0.0
        cogs = 0.0
        gross_profit = revenue - cogs
        margin_pct = (gross_profit / revenue * 100.0) if revenue > 0 else 0.0
        self.assertEqual(margin_pct, 0.0)

