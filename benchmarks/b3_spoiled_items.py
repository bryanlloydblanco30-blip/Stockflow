"""
benchmarks/b3_spoiled_items.py
Benchmark B3: Spoiled items (FEFO Min-Heap vs FIFO / Random order) (Doc 12.3).
Simulated periods: 30, 60, 90 days on tracked products only.

Protocol:
- Identical simulated sales and restock arrivals across all three methods.
- 30 simulation runs per period, reporting min, median, max spoiled units.
"""

import random
import statistics
from datetime import date, timedelta
from typing import Any, Dict, List

from backend.ds.min_heap import MinHeap


class _SimBatch:
    __slots__ = ("id", "qty", "expiry", "received")

    def __init__(self, batch_id: int, qty: int, expiry: date, received: date):
        self.id = batch_id
        self.qty = qty
        self.expiry = expiry
        self.received = received


def _simulate_period(days: int, seed: int, mode: str) -> int:
    rng = random.Random(seed)
    start_day = date(2026, 1, 1)
    num_products = 20
    spoiled_units = 0
    batch_seq = 1

    # Initialize batches per tracked product
    if mode == "fefo":
        stores = [MinHeap() for _ in range(num_products)]
    else:
        stores = [[] for _ in range(num_products)]

    for p_idx in range(num_products):
        for _ in range(2):
            qty = rng.randint(8, 16)
            shelf_life = rng.randint(5, 18)
            b = _SimBatch(batch_seq, qty, start_day + timedelta(days=shelf_life), start_day)
            batch_seq += 1
            if mode == "fefo":
                stores[p_idx].insert(b, key=b.expiry, tie_break=(b.received, b.id))
            else:
                stores[p_idx].append(b)

    for day_offset in range(days):
        today = start_day + timedelta(days=day_offset)

        # 1. Restock every 4 days with varying shelf-life batches (some shorter than existing)
        if day_offset > 0 and day_offset % 4 == 0:
            for p_idx in range(num_products):
                qty = rng.randint(10, 20)
                shelf_life = rng.randint(4, 16)
                b = _SimBatch(batch_seq, qty, today + timedelta(days=shelf_life), today)
                batch_seq += 1
                if mode == "fefo":
                    stores[p_idx].insert(b, key=b.expiry, tie_break=(b.received, b.id))
                else:
                    stores[p_idx].append(b)

        # 2. Daily customer demand (identical sequence per seed)
        for p_idx in range(num_products):
            demand = rng.randint(2, 6)

            if mode == "fefo":
                heap = stores[p_idx]
                while demand > 0 and not heap.is_empty():
                    b = heap.extract_min()
                    if b.expiry < today:
                        spoiled_units += b.qty
                        continue
                    take = min(demand, b.qty)
                    b.qty -= take
                    demand -= take
                    if b.qty > 0:
                        heap.insert(b, key=b.expiry, tie_break=(b.received, b.id))
            else:
                batches = stores[p_idx]
                # Remove expired batches first
                alive = []
                for b in batches:
                    if b.expiry < today:
                        spoiled_units += b.qty
                    else:
                        alive.append(b)
                stores[p_idx] = alive

                while demand > 0 and stores[p_idx]:
                    idx = 0 if mode == "fifo" else rng.randrange(len(stores[p_idx]))
                    b = stores[p_idx][idx]
                    take = min(demand, b.qty)
                    b.qty -= take
                    demand -= take
                    if b.qty == 0:
                        stores[p_idx].pop(idx)

    # Flush any remaining expired at end of period
    end_day = start_day + timedelta(days=days)
    for p_idx in range(num_products):
        if mode == "fefo":
            heap = stores[p_idx]
            while not heap.is_empty():
                b = heap.extract_min()
                if b.expiry < end_day:
                    spoiled_units += b.qty
        else:
            for b in stores[p_idx]:
                if b.expiry < end_day:
                    spoiled_units += b.qty

    return spoiled_units


def run_b3(
    periods: List[int] = [30, 60, 90],
    iterations: int = 30,
) -> Dict[str, Any]:
    results: Dict[str, Any] = {}

    for days in periods:
        fefo_spoiled = [_simulate_period(days, 1000 + i, "fefo") for i in range(iterations)]
        fifo_spoiled = [_simulate_period(days, 1000 + i, "fifo") for i in range(iterations)]
        rand_spoiled = [_simulate_period(days, 1000 + i, "random") for i in range(iterations)]

        results[f"{days}d"] = {
            "fefo_min_heap": {
                "min_units": min(fefo_spoiled),
                "median_units": statistics.median(fefo_spoiled),
                "max_units": max(fefo_spoiled),
            },
            "fifo_baseline": {
                "min_units": min(fifo_spoiled),
                "median_units": statistics.median(fifo_spoiled),
                "max_units": max(fifo_spoiled),
            },
            "random_baseline": {
                "min_units": min(rand_spoiled),
                "median_units": statistics.median(rand_spoiled),
                "max_units": max(rand_spoiled),
            },
        }

    return results


if __name__ == "__main__":
    print("B3 Results:", run_b3())
