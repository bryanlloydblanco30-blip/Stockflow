"""
backend/ds/max_heap.py
Max-Heap (Priority Queue) written from scratch for restock ranking.
Contract: docs/adt/max_heap.md
"""


class MaxHeap:
    def __init__(self):
        self._heap = []

    def insert(self, item, priority) -> None:
        pass

    def peek_max(self):
        pass

    def extract_max(self):
        pass

    def size(self) -> int:
        return len(self._heap)

    def is_empty(self) -> bool:
        return len(self._heap) == 0

