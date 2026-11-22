"""
backend/ds/min_heap.py
Min-Heap written from scratch (FEFO per-product batch priority queue).
Contract: docs/adt/min_heap.md
"""


class MinHeap:
    def __init__(self):
        self._heap = []

    def insert(self, item, key, tie_break) -> None:
        pass

    def peek_min(self):
        pass

    def extract_min(self):
        pass

    def remove_specific(self, item_id) -> bool:
        pass

    def ordered_read(self):
        pass

    def size(self) -> int:
        return len(self._heap)

    def is_empty(self) -> bool:
        return len(self._heap) == 0

