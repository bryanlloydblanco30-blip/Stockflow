"""
benchmarks/b2_name_search.py
Benchmark B2: Name search (Trie vs Linear String Scan) (Doc 12.3).
Sizes: 100, 1,000, 10,000, 100,000 products.

Protocol:
- time.perf_counter(), 5 warmups, 30 timed iterations.
- Reports min, median, max in microseconds.
"""

import random
import statistics
import time
from typing import Any, Dict, List

from backend.ds.trie import Trie
from benchmarks.baselines import naive_string_scan


_WORDS_A = [
    "Pandesal", "Sardines", "Bottled", "Instant", "Fresh", "Canned",
    "Organic", "Spicy", "Sweet", "Salted", "Choco", "Vanilla",
    "Coffee", "Green", "Golden", "Crispy", "Soft", "Pure",
]
_WORDS_B = [
    "Milk", "Bread", "Water", "Noodles", "Tuna", "Crackers",
    "Biscuits", "Juice", "Tea", "Sugar", "Rice", "Oil",
    "Soap", "Shampoo", "Notebook", "Pencil", "Cheese", "Butter",
]


def run_b2(
    sizes: List[int] = [100, 1000, 10000, 100000],
    iterations: int = 30,
) -> Dict[str, Any]:
    rng = random.Random(42)
    results: Dict[str, Any] = {}

    for n in sizes:
        product_names = [
            f"{rng.choice(_WORDS_A)} {rng.choice(_WORDS_B)} {i}"
            for i in range(n)
        ]

        trie = Trie()
        for name in product_names:
            trie.insert(name, name)

        # Sample 10 query prefixes (mix of 2-char and 4-char prefixes)
        prefixes = ["pa", "sa", "bo", "in", "fr", "ch", "co", "mi", "zz", "or"]

        # Benchmark Naive Linear String Scan
        times_naive: List[float] = []
        for _ in range(5):
            for p in prefixes:
                naive_string_scan(product_names, p, limit=8)
        for _ in range(iterations):
            start = time.perf_counter()
            for p in prefixes:
                naive_string_scan(product_names, p, limit=8)
            times_naive.append((time.perf_counter() - start) * 1e6)

        # Benchmark Trie Prefix Search
        times_trie: List[float] = []
        for _ in range(5):
            for p in prefixes:
                trie.list_under_prefix(p, limit=8)
        for _ in range(iterations):
            start = time.perf_counter()
            for p in prefixes:
                trie.list_under_prefix(p, limit=8)
            times_trie.append((time.perf_counter() - start) * 1e6)

        results[str(n)] = {
            "naive_scan": {
                "min_us": min(times_naive),
                "median_us": statistics.median(times_naive),
                "max_us": max(times_naive),
            },
            "trie": {
                "min_us": min(times_trie),
                "median_us": statistics.median(times_trie),
                "max_us": max(times_trie),
            },
        }

    return results


if __name__ == "__main__":
    print("B2 Results:", run_b2())
