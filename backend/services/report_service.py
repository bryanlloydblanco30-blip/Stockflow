"""
backend/services/report_service.py
Financial reports: Revenue, COGS, Gross Profit, Spoilage, Top-k/Bottom-k (Tasks 5.4 to 5.7 / Doc 10).
"""


class ReportService:
    def __init__(self, prefix_sums, size_k_heap, db_conn):
        self.prefix_sums = prefix_sums
        self.size_k_heap = size_k_heap
        self.conn = db_conn

    def get_dashboard_kpis(self):
        """Today's sales, profit, low stock count, near expiry count."""
        pass

    def get_range_financials(self, start_day: int, end_day: int):
        pass

    def get_top_bottom_sellers(self, k: int = 5):
        pass

    def get_spoilage_report(self):
        pass

