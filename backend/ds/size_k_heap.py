"""
backend/ds/size_k_heap.py
Size-k heap routine for top-k and bottom-k sellers without full sorting.
Contract: docs/adt/size_k_heap.md
Used by: fast and slow mover analytics (Doc 10.1, Phase 1.8).
Zero built-in sorting (heapq, sorted, dict) used.
"""

from backend.ds.min_heap import MinHeap
from backend.ds.max_heap import MaxHeap


class SizeKHeap:
    """
    Size-k heap routine:
    - mode="top": uses a Min-Heap of size k to retain the top k elements in O(n log k) time.
    - mode="bottom": uses a Max-Heap of size k to retain the bottom k elements in O(n log k) time.
    """

    def __init__(self, k: int, mode: str = "top"):
        if k <= 0:
            raise ValueError("k must be a positive integer")
        self.k = k
        self.mode = mode
        if mode == "top":
            self._heap = MinHeap()
        elif mode == "bottom":
            self._heap = MaxHeap()
        else:
            raise ValueError(f"Invalid mode '{mode}'. Expected 'top' or 'bottom'.")

    def feed(self, item, score: float) -> None:
        """Feed a candidate item and score into the bounded heap in O(log k) time."""
        if self.mode == "top":
            if self._heap.size() < self.k:
                self._heap.insert((item, score), key=score)
            else:
                _, min_score = self._heap.peek_min()
                if score > min_score:
                    self._heap.extract_min()
                    self._heap.insert((item, score), key=score)
        else:
            if self._heap.size() < self.k:
                self._heap.insert((item, score), priority=score)
            else:
                _, max_score = self._heap.peek_max()
                if score < max_score:
                    self._heap.extract_max()
                    self._heap.insert((item, score), priority=score)

    def get_ranked(self) -> list[tuple[any, float]]:
        """
        Return the collected k items ranked:
        - top mode: ranked descending (highest score first)
        - bottom mode: ranked ascending (lowest score first)
        """
        if self.mode == "top":
            # ordered_read yields ascending, reverse for descending ranking
            items = list(self._heap.ordered_read())
            items.reverse()
            return items
        else:
            # Drain a copy of max heap to sort ascending
            copy_heap = MaxHeap()
            copy_heap._heap = list(self._heap._heap)
            items = []
            while not copy_heap.is_empty():
                items.append(copy_heap.extract_max())
            # items are descending, reverse for ascending ranking
            items.reverse()
            return items

    def size(self) -> int:
        """Return number of currently held items (at most k)."""
        return self._heap.size()
