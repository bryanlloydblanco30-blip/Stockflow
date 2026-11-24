"""
benchmarks/b5_range_sales.py
Benchmark B5: Date-range sales (Prefix Sums vs Raw Record Loop) (Doc 12.3).
Sizes: 1,000 to 1,000,000 records.

Protocol:
- time.perf_counter(), 5 warmups, 30 timed iterations.
- Reports min, median, max in microseconds for 20 range queries per iteration.
"""

import random
import statistics
import time
from typing import Any, Dict, List

from backend.ds.prefix_sums import PrefixSums


def _naive_range_loop(values: List[float], start: int, end: int) -> float:
    total = 0.0
    for i in range(start, end + 1):
        total += values[i]
    return total


def run_b5(
    sizes: List[int] = [1000, 10000, 100000, 1000000],
    iterations: int = 30,
) -> Dict[str, Any]:
    rng = random.Random(42)
    results: Dict[str, Any] = {}

    for n in sizes:
        values = [round(rng.uniform(100.0, 5000.0), 2) for _ in range(n)]
        ps = PrefixSums(values)

        # Generate 20 random query ranges spanning ~25% to 75% of the series
        queries = []
        for _ in range(20):
            s = rng.randint(0, n // 2)
            e = rng.randint(s + max(1, n // 4), n - 1)
            queries.append((s, e))

        # Benchmark Naive Raw Loop
        times_naive: List[float] = []
        for _ in range(2):  # warmup (kept light for 1M size)
            for s, e in queries[:3]:
                _naive_range_loop(values, s, e)
        for _ in range(iterations):
            start = time.perf_counter()
            for s, e in queries:
                _naive_range_loop(values, s, e)
            times_naive.append((time.perf_counter() - start) * 1e6)

        # Benchmark Prefix Sums O(1)
        times_prefix: List[float] = []
        for _ in range(5):  # warmup
            for s, e in queries:
                ps.range_sum(s, e)
        for _ in range(iterations):
            start = time.perf_counter()
            for s, e in queries:
                ps.range_sum(s, e)
            times_prefix.append((time.perf_counter() - start) * 1e6)

        results[str(n)] = {
            "naive_loop": {
                "min_us": min(times_naive),
                "median_us": statistics.median(times_naive),
                "max_us": max(times_naive),
            },
            "prefix_sums": {
                "min_us": min(times_prefix),
                "median_us": statistics.median(times_prefix),
                "max_us": max(times_prefix),
            },
        }

    return results


if __name__ == "__main__":
    print("B5 Results:", run_b5())
