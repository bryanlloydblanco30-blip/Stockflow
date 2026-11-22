"""
backend/ds/size_k_heap.py
Size-k heap routine for top-k and bottom-k sellers without full sorting.
Contract: docs/adt/size_k_heap.md
"""


class SizeKHeap:
    def __init__(self, k: int, mode: str = "top"):
        self.k = k
        self.mode = mode  # 'top' uses min-heap of size k; 'bottom' uses max-heap of size k
        self._heap = []

    def feed(self, item, score: float) -> None:
        pass

    def get_ranked(self) -> list:
        pass

