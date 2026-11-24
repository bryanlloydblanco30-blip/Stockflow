"""
benchmarks/b6_topk_sellers.py
Benchmark B6: Top-k sellers (Size-k Heap vs Full Sort) (Doc 12.3).
Sizes: 100 to 100,000 products, k = 5 and k = 10.

Protocol:
- time.perf_counter(), 5 warmups, 30 timed iterations.
- Reports min, median, max in microseconds.
- Reports results honestly (Python's C-implemented Timsort sorted() can outperform pure-Python loops).
"""

import random
import statistics
import time
from typing import Any, Dict, List

from backend.ds.size_k_heap import SizeKHeap
from benchmarks.baselines import naive_full_sort


def run_b6(
    sizes: List[int] = [100, 1000, 10000, 100000],
    ks: List[int] = [5, 10],
    iterations: int = 30,
) -> Dict[str, Any]:
    rng = random.Random(42)
    results: Dict[str, Any] = {}

    for k in ks:
        k_results: Dict[str, Any] = {}
        for n in sizes:
            sales_items = [(f"P{i}", round(rng.uniform(1.0, 5000.0), 2)) for i in range(n)]

            # Benchmark Full Sort
            times_sort: List[float] = []
            for _ in range(5):
                naive_full_sort(sales_items, k=k, top=True)
            for _ in range(iterations):
                start = time.perf_counter()
                naive_full_sort(sales_items, k=k, top=True)
                times_sort.append((time.perf_counter() - start) * 1e6)

            # Benchmark Size-k Heap
            times_heap: List[float] = []
            for _ in range(5):
                sk = SizeKHeap(k=k, mode="top")
                for item, score in sales_items:
                    sk.feed(item, score)
                sk.get_ranked()
            for _ in range(iterations):
                start = time.perf_counter()
                sk = SizeKHeap(k=k, mode="top")
                for item, score in sales_items:
                    sk.feed(item, score)
                sk.get_ranked()
                times_heap.append((time.perf_counter() - start) * 1e6)

            k_results[str(n)] = {
                "full_sort": {
                    "min_us": min(times_sort),
                    "median_us": statistics.median(times_sort),
                    "max_us": max(times_sort),
                },
                "size_k_heap": {
                    "min_us": min(times_heap),
                    "median_us": statistics.median(times_heap),
                    "max_us": max(times_heap),
                },
            }
        results[f"k={k}"] = k_results

    return results


if __name__ == "__main__":
    print("B6 Results:", run_b6())
