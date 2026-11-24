"""
benchmarks/b4_stockouts.py
Benchmark B4: Stockouts (Priority Restock Max-Heap Queue vs No Alerts) (Doc 12.3).
Measures out-of-stock product-days over 30, 60, 90 days simulation.

Protocol:
- Identical daily demand stream for both methods across 30 runs per period.
- Both methods share a realistic per-cycle restock slot cap (e.g. top 5 items restocked per order).
- Reports min, median, max stockout product-days.
"""

import random
import statistics
from typing import Any, Dict, List

from backend.ds.max_heap import MaxHeap


def _simulate_stockouts(days: int, seed: int, use_priority_queue: bool) -> int:
    rng = random.Random(seed)
    num_products = 25
    # Each product has initial stock, base daily demand, and lead time (2 days)
    stock = [rng.randint(12, 30) for _ in range(num_products)]
    base_demand = [rng.uniform(1.5, 6.0) for _ in range(num_products)]
    sales_history = [[] for _ in range(num_products)]
    in_transit = [0] * num_products  # arrives next day

    stockout_days = 0
    max_orders_per_cycle = 5

    for day in range(days):
        # Receive yesterday's restock order
        for p in range(num_products):
            if in_transit[p] > 0:
                stock[p] += in_transit[p]
                in_transit[p] = 0

        # Simulate identical daily demand
        for p in range(num_products):
            demand = max(0, int(round(rng.gauss(base_demand[p], 1.2))))
            sold = min(stock[p], demand)
            stock[p] -= sold
            sales_history[p].append(demand)
            if stock[p] == 0:
                stockout_days += 1

        # Restock decision every 2 days
        if day % 2 == 1:
            if use_priority_queue:
                pq = MaxHeap()
                for p in range(num_products):
                    recent = sales_history[p][-14:]
                    avg_speed = sum(recent) / len(recent) if recent else 1.0
                    days_cover = stock[p] / avg_speed if avg_speed > 0 else 999.0
                    if days_cover < 5.0:
                        # Priority: lowest days_cover first, highest speed tie-break
                        pq.insert(p, priority=(-days_cover, avg_speed))
                ordered = 0
                while not pq.is_empty() and ordered < max_orders_per_cycle:
                    p = pq.extract_max()
                    recent = sales_history[p][-14:]
                    avg_speed = sum(recent) / len(recent) if recent else 1.0
                    in_transit[p] = max(10, int(round(avg_speed * 7)))
                    ordered += 1
            else:
                # No alerts baseline: only notices when stock hits 0, picks in arbitrary ID order
                ordered = 0
                for p in range(num_products):
                    if stock[p] == 0 and ordered < max_orders_per_cycle:
                        in_transit[p] = 20
                        ordered += 1

    return stockout_days


def run_b4(
    periods: List[int] = [30, 60, 90],
    iterations: int = 30,
) -> Dict[str, Any]:
    results: Dict[str, Any] = {}

    for days in periods:
        pq_days = [_simulate_stockouts(days, 2000 + i, True) for i in range(iterations)]
        no_alert_days = [_simulate_stockouts(days, 2000 + i, False) for i in range(iterations)]

        results[f"{days}d"] = {
            "priority_queue": {
                "min_stockout_days": min(pq_days),
                "median_stockout_days": statistics.median(pq_days),
                "max_stockout_days": max(pq_days),
            },
            "no_alerts": {
                "min_stockout_days": min(no_alert_days),
                "median_stockout_days": statistics.median(no_alert_days),
                "max_stockout_days": max(no_alert_days),
            },
        }

    return results


if __name__ == "__main__":
    print("B4 Results:", run_b4())
