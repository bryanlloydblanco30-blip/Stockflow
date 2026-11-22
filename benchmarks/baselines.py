"""
benchmarks/baselines.py
Naive baseline algorithms used strictly for empirical benchmarking against custom DSA (Doc 12.3).
Note: heapq, dict, and sorted are permitted ONLY within benchmarks/ as comparison baselines.
"""


def naive_linear_search(products: list, barcode: str):
    """B1 baseline: O(n) linear scan through list."""
    for p in products:
        if p.barcode == barcode:
            return p
    return None


def naive_string_scan(product_names: list[str], prefix: str, limit: int = 8) -> list[str]:
    """B2 baseline: O(n * m) substring check across all names."""
    results = []
    prefix_lower = prefix.lower()
    for name in product_names:
        if name.lower().startswith(prefix_lower):
            results.append(name)
            if len(results) == limit:
                break
    return results


def naive_full_sort(sales_items: list, k: int = 5, top: bool = True) -> list:
    """B6 baseline: O(n log n) full Python sorted() call."""
    return sorted(sales_items, key=lambda x: x[1], reverse=top)[:k]

