"""
benchmarks/b1_product_lookup.py
Benchmark B1: Product lookup (BST vs Naive Linear Search) (Doc 12.3).
Sizes: 100, 1,000, 10,000 products.
Includes:
- BST average case (random insertion) -> O(log n)
- BST worst case (sorted insertion) -> O(n)
- Naive Linear Search -> O(n)

Protocol:
- time.perf_counter(), 5 warmups, 30 timed iterations.
- Reports min, median, max.
"""

import time
import random
import statistics
from typing import Dict, Any, List
from backend.ds.bst import BST
from backend.models.product import Product
from benchmarks.baselines import naive_linear_search


def run_b1(sizes: List[int] = [100, 1000, 10000], iterations: int = 30) -> Dict[str, Any]:
    rng = random.Random(42)
    results: Dict[str, Any] = {}

    for n in sizes:
        # Generate random unique barcodes
        barcodes = [f"480{rng.randint(1000000, 9999999)}" for _ in range(n)]
        # Ensure unique
        barcodes = list(set(barcodes))
        while len(barcodes) < n:
            barcodes.append(f"480{rng.randint(1000000, 9999999)}")
            barcodes = list(set(barcodes))

        products = [
            Product(id=i, barcode=bc, name=f"Product {i}", category_id=1, cost_price=10.0, selling_price=20.0, reorder_level=5, location_id=1, active=True)
            for i, bc in enumerate(barcodes)
        ]

        # 1. Build BST (Average Case - random order)
        bst_avg = BST()
        for p in products:
            bst_avg.insert(p.barcode, p)

        # 2. Build BST (Worst Case - sorted order insertion)
        sorted_products = sorted(products, key=lambda x: x.barcode)
        bst_worst = BST()
        for p in sorted_products:
            bst_worst.insert(p.barcode, p)

        # Query targets (sample of 10 keys)
        targets = rng.sample(barcodes, min(10, n))

        # Benchmark Naive Linear Search
        times_naive = []
        for _ in range(5):  # warmup
            for t in targets:
                naive_linear_search(products, t)
        for _ in range(iterations):
            start = time.perf_counter()
            for t in targets:
                naive_linear_search(products, t)
            times_naive.append((time.perf_counter() - start) * 1e6)  # microseconds

        # Benchmark BST Average Case
        times_bst_avg = []
        for _ in range(5):  # warmup
            for t in targets:
                bst_avg.find(t)
        for _ in range(iterations):
            start = time.perf_counter()
            for t in targets:
                bst_avg.find(t)
            times_bst_avg.append((time.perf_counter() - start) * 1e6)

        # Benchmark BST Worst Case (sorted insertion)
        times_bst_worst = []
        for _ in range(5):  # warmup
            for t in targets:
                bst_worst.find(t)
        for _ in range(iterations):
            start = time.perf_counter()
            for t in targets:
                bst_worst.find(t)
            times_bst_worst.append((time.perf_counter() - start) * 1e6)

        results[str(n)] = {
            "naive_linear": {
                "min_us": min(times_naive),
                "median_us": statistics.median(times_naive),
                "max_us": max(times_naive),
            },
            "bst_avg": {
                "min_us": min(times_bst_avg),
                "median_us": statistics.median(times_bst_avg),
                "max_us": max(times_bst_avg),
            },
            "bst_worst": {
                "min_us": min(times_bst_worst),
                "median_us": statistics.median(times_bst_worst),
                "max_us": max(times_bst_worst),
            },
        }

    return results


if __name__ == "__main__":
    res = run_b1()
    print("B1 Results:", res)
