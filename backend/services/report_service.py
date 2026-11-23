"""
backend/services/report_service.py
Financial reports and analytics: Revenue, COGS, Gross Profit, Spoilage,
Prefix Sums daily arrays, and Top-k / Bottom-k sellers using SizeKHeap.
Tasks 5.4 to 5.7, RP-1 to RP-8, Doc 7.3 C, Doc 10.

RULES:
- Excludes voided sales from all financial totals.
- Margin is 0% when revenue is 0.
- Top-k and Bottom-k powered by custom SizeKHeap (Doc 10.1).
- Daily range sums powered by custom PrefixSums (Doc 7.3 C).
- Dashboard numbers: today's sales, profit, low stock count, near expiry count.
- Zero heapq, dict, or sorted imports.
"""

from datetime import date, timedelta
from typing import Optional, List, Dict, Any
import sqlite3

from backend.ds.prefix_sums import PrefixSums
from backend.ds.size_k_heap import SizeKHeap
from backend.services.alert_service import AlertService
from backend.db.storage import StoreMemoryState


class ReportService:
    def __init__(
        self,
        conn: sqlite3.Connection,
        state: StoreMemoryState,
        alert_service: Optional[AlertService] = None,
    ):
        self.conn = conn
        self.state = state
        self.alert_service = alert_service or AlertService()

    def get_financial_summary(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        today: Optional[date] = None,
    ) -> Dict[str, Any]:
        """
        Computes Revenue, COGS, Gross Profit, Margin %, Spoilage, and Inventory Value at Cost.
        Voided transactions are strictly excluded (Doc 10 / Task 5.6).
        """
        curr_date = today or date.today()
        cursor = self.conn.cursor()

        # 1. Revenue and COGS from non-voided sales
        query = """
            SELECT
                COALESCE(SUM(tl.quantity * tl.price_at_time), 0.0),
                COALESCE(SUM(tl.quantity * tl.cost_at_time), 0.0)
            FROM transaction_lines tl
            JOIN transactions t ON tl.transaction_id = t.id
            WHERE t.type = 'sale'
              AND NOT EXISTS (
                  SELECT 1 FROM transactions v
                  WHERE v.type = 'void' AND v.reverses_id = t.id
              )
        """
        params: List[Any] = []
        if start_date:
            query += " AND DATE(t.date_time) >= ?"
            params.append(start_date.isoformat())
        if end_date:
            query += " AND DATE(t.date_time) <= ?"
            params.append(end_date.isoformat())

        cursor.execute(query, params)
        row = cursor.fetchone()
        revenue = round(row[0], 2) if row else 0.0
        cogs = round(row[1], 2) if row else 0.0

        gross_profit = round(revenue - cogs, 2)
        margin_pct = round((gross_profit / revenue * 100.0), 2) if revenue > 0 else 0.0

        # 2. Spoilage from write-offs
        spoil_query = """
            SELECT COALESCE(SUM(tl.quantity * tl.cost_at_time), 0.0)
            FROM transaction_lines tl
            JOIN transactions t ON tl.transaction_id = t.id
            WHERE t.type IN ('writeoff', 'write-off')
        """
        spoil_params: List[Any] = []
        if start_date:
            spoil_query += " AND DATE(t.date_time) >= ?"
            spoil_params.append(start_date.isoformat())
        if end_date:
            spoil_query += " AND DATE(t.date_time) <= ?"
            spoil_params.append(end_date.isoformat())

        cursor.execute(spoil_query, spoil_params)
        spoil_row = cursor.fetchone()
        spoilage = round(spoil_row[0], 2) if spoil_row else 0.0

        # 3. Inventory Value at Cost (sum of current sellable stock across all active products)
        inventory_val = 0.0
        cursor.execute("""
            SELECT product_id, quantity, cost_price, expiry_date
            FROM batches
            WHERE quantity > 0;
        """)
        for b_row in cursor.fetchall():
            qty = b_row[1]
            cost = b_row[2]
            exp_date = b_row[3]
            # Exclude expired batches from sellable inventory value
            if self.alert_service.is_sellable(exp_date, curr_date):
                inventory_val += qty * cost

        return {
            "revenue": revenue,
            "cogs": cogs,
            "gross_profit": gross_profit,
            "margin_pct": margin_pct,
            "spoilage": spoilage,
            "inventory_value": round(inventory_val, 2),
        }

    def build_daily_prefix_sums(
        self,
        start_date: date,
        end_date: date,
    ) -> Dict[str, PrefixSums]:
        """
        Builds PrefixSums arrays for daily Revenue, Units, and COGS across date range (Doc 7.3 C / Task 5.5).
        Enables O(1) arbitrary range sum queries.
        """
        cursor = self.conn.cursor()

        # Query daily aggregate sums
        cursor.execute("""
            SELECT
                DATE(t.date_time) as sale_day,
                COALESCE(SUM(tl.quantity * tl.price_at_time), 0.0) as day_revenue,
                COALESCE(SUM(tl.quantity), 0) as day_units,
                COALESCE(SUM(tl.quantity * tl.cost_at_time), 0.0) as day_cogs
            FROM transaction_lines tl
            JOIN transactions t ON tl.transaction_id = t.id
            WHERE t.type = 'sale'
              AND NOT EXISTS (
                  SELECT 1 FROM transactions v
                  WHERE v.type = 'void' AND v.reverses_id = t.id
              )
              AND DATE(t.date_time) >= ?
              AND DATE(t.date_time) <= ?
            GROUP BY DATE(t.date_time)
            ORDER BY sale_day ASC;
        """, (start_date.isoformat(), end_date.isoformat()))

        rows = cursor.fetchall()

        # Build continuous daily lists for every day between start_date and end_date
        total_days = (end_date - start_date).days + 1
        daily_rev: List[float] = [0.0] * total_days
        daily_units: List[float] = [0.0] * total_days
        daily_cogs: List[float] = [0.0] * total_days

        for r in rows:
            day_str = r[0]
            curr = date.fromisoformat(day_str)
            idx = (curr - start_date).days
            if 0 <= idx < total_days:
                daily_rev[idx] = float(r[1])
                daily_units[idx] = float(r[2])
                daily_cogs[idx] = float(r[3])

        ps_rev = PrefixSums(daily_rev)
        ps_units = PrefixSums(daily_units)
        ps_cogs = PrefixSums(daily_cogs)

        return {
            "revenue": ps_rev,
            "units": ps_units,
            "cogs": ps_cogs,
        }

    def get_top_sellers(self, k: int = 5, metric: str = "units") -> List[Dict[str, Any]]:
        """
        Identifies top k sellers using strictly bounded SizeKHeap in mode='top' (Doc 10.1 / Task 5.4).
        """
        cursor = self.conn.cursor()
        field = "SUM(tl.quantity)" if metric == "units" else "SUM(tl.quantity * tl.price_at_time)"

        cursor.execute(f"""
            SELECT p.id, p.name, {field} as score
            FROM transaction_lines tl
            JOIN transactions t ON tl.transaction_id = t.id
            JOIN products p ON tl.product_id = p.id
            WHERE t.type = 'sale'
              AND NOT EXISTS (
                  SELECT 1 FROM transactions v
                  WHERE v.type = 'void' AND v.reverses_id = t.id
              )
            GROUP BY p.id, p.name;
        """)

        rows = cursor.fetchall()
        k_val = min(k, len(rows)) if len(rows) > 0 else 1
        heap = SizeKHeap(k=k_val, mode="top")

        for row in rows:
            prod_info = {"product_id": row[0], "product_name": row[1]}
            score = float(row[2])
            heap.feed(prod_info, score)

        ranked = heap.get_ranked()
        results: List[Dict[str, Any]] = []
        for item, score in ranked:
            results.append({
                "product_id": item["product_id"],
                "product_name": item["product_name"],
                "score": score,
            })
        return results

    def get_bottom_sellers(self, k: int = 5, metric: str = "units") -> List[Dict[str, Any]]:
        """
        Identifies bottom k sellers using strictly bounded SizeKHeap in mode='bottom' (Doc 10.1 / Task 5.4).
        """
        cursor = self.conn.cursor()
        field = "SUM(tl.quantity)" if metric == "units" else "SUM(tl.quantity * tl.price_at_time)"

        cursor.execute(f"""
            SELECT p.id, p.name, {field} as score
            FROM transaction_lines tl
            JOIN transactions t ON tl.transaction_id = t.id
            JOIN products p ON tl.product_id = p.id
            WHERE t.type = 'sale'
              AND NOT EXISTS (
                  SELECT 1 FROM transactions v
                  WHERE v.type = 'void' AND v.reverses_id = t.id
              )
            GROUP BY p.id, p.name;
        """)

        rows = cursor.fetchall()
        k_val = min(k, len(rows)) if len(rows) > 0 else 1
        heap = SizeKHeap(k=k_val, mode="bottom")

        for row in rows:
            prod_info = {"product_id": row[0], "product_name": row[1]}
            score = float(row[2])
            heap.feed(prod_info, score)

        ranked = heap.get_ranked()
        results: List[Dict[str, Any]] = []
        for item, score in ranked:
            results.append({
                "product_id": item["product_id"],
                "product_name": item["product_name"],
                "score": score,
            })
        return results

    def get_dashboard_kpis(self, today: Optional[date] = None) -> Dict[str, Any]:
        """
        Dashboard numbers (RP-8 / Task 5.7):
        - Today's sales (revenue from non-voided sales today).
        - Today's profit (gross profit today).
        - Low-stock count (sellable stock < reorder level).
        - Near-expiry count (RED or AMBER batches for tracked products only).
        """
        curr_date = today or date.today()
        cursor = self.conn.cursor()

        # 1. Today's sales & profit
        cursor.execute("""
            SELECT
                COALESCE(SUM(tl.quantity * tl.price_at_time), 0.0),
                COALESCE(SUM(tl.quantity * tl.cost_at_time), 0.0)
            FROM transaction_lines tl
            JOIN transactions t ON tl.transaction_id = t.id
            WHERE t.type = 'sale'
              AND DATE(t.date_time) = ?
              AND NOT EXISTS (
                  SELECT 1 FROM transactions v
                  WHERE v.type = 'void' AND v.reverses_id = t.id
              );
        """, (curr_date.isoformat(),))
        row = cursor.fetchone()
        today_sales = round(row[0], 2) if row else 0.0
        today_cogs = round(row[1], 2) if row else 0.0
        today_profit = round(today_sales - today_cogs, 2)

        # 2. Low-stock count
        low_stock_count = 0
        for prod in self.state.products:
            if not prod.active:
                continue
            heap = self.state.get_or_create_product_heap(prod.id)
            sellable = 0
            for b in heap.ordered_read():
                if self.alert_service.is_sellable(b.expiry_date, curr_date):
                    sellable += b.quantity
            if sellable < prod.reorder_level:
                low_stock_count += 1

        # 3. Near-expiry count (tracked products only: categories where tracks_expiry=True, level in RED/AMBER)
        near_expiry_count = 0
        for prod in self.state.products:
            if not prod.active:
                continue
            cat = self.state.get_category_by_id(prod.category_id) if prod.category_id else None
            if cat is None and prod.category_id:
                cursor.execute("SELECT id, name, tracks_expiry, warn_days FROM categories WHERE id = ?;", (prod.category_id,))
                cat_row = cursor.fetchone()
                if cat_row:
                    cat = Category(id=cat_row[0], name=cat_row[1], tracks_expiry=bool(cat_row[2]), warn_days=cat_row[3])
                    self.state.categories.append(cat)

            # Skip uncategorized or untracked categories
            if cat is not None and not cat.tracks_expiry:
                continue

            warn_days = cat.warn_days if cat else 7
            heap = self.state.get_or_create_product_heap(prod.id)
            for b in heap.ordered_read():
                if b.quantity > 0 and b.expiry_date:
                    lvl = self.alert_service.calculate_level(b.expiry_date, warn_days, curr_date)
                    if lvl in ("RED", "AMBER"):
                        near_expiry_count += 1

        return {
            "today_sales": today_sales,
            "today_profit": today_profit,
            "low_stock_count": low_stock_count,
            "near_expiry_count": near_expiry_count,
        }
