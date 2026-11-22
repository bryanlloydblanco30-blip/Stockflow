"""
backend/ds/max_heap.py
Max-Heap (Priority Queue) written strictly from scratch.
Contract: docs/adt/max_heap.md
Used by: restock priority queue (Doc 6.8).
Must NOT import heapq.
"""


class _MaxHeapEntry:
    """Internal max-heap entry tracking priority and payload."""

    __slots__ = ("priority", "item")

    def __init__(self, priority, item):
        self.priority = priority
        self.item = item

    def __lt__(self, other):
        # Higher priority comes first
        return self.priority > other.priority

    def __le__(self, other):
        return self.priority >= other.priority


class MaxHeap:
    """
    Max-Heap (Priority Queue) written strictly from scratch.
    Supports O(log n) insert and extract_max, and O(1) peek_max.
    """

    def __init__(self):
        self._heap: list[_MaxHeapEntry] = []

    def _sift_up(self, idx: int) -> None:
        curr = idx
        while curr > 0:
            parent = (curr - 1) // 2
            # Compare priorities: child > parent -> swap
            if self._heap[curr].priority > self._heap[parent].priority:
                self._heap[curr], self._heap[parent] = (
                    self._heap[parent],
                    self._heap[curr],
                )
                curr = parent
            else:
                break

    def _sift_down(self, idx: int) -> None:
        curr = idx
        n = len(self._heap)
        while True:
            left = 2 * curr + 1
            right = 2 * curr + 2
            largest = curr

            if (
                left < n
                and self._heap[left].priority > self._heap[largest].priority
            ):
                largest = left
            if (
                right < n
                and self._heap[right].priority > self._heap[largest].priority
            ):
                largest = right

            if largest != curr:
                self._heap[curr], self._heap[largest] = (
                    self._heap[largest],
                    self._heap[curr],
                )
                curr = largest
            else:
                break

    def insert(self, item, priority) -> None:
        """Insert element with priority in O(log n) time."""
        entry = _MaxHeapEntry(priority, item)
        self._heap.append(entry)
        self._sift_up(len(self._heap) - 1)

    def peek_max(self):
        """Return element with highest priority in O(1) time. Raises IndexError if empty."""
        if not self._heap:
            raise IndexError("peek from empty heap")
        return self._heap[0].item

    def extract_max(self):
        """Remove and return element with highest priority in O(log n) time."""
        if not self._heap:
            raise IndexError("extract from empty heap")
        if len(self._heap) == 1:
            return self._heap.pop().item

        root_item = self._heap[0].item
        self._heap[0] = self._heap.pop()
        self._sift_down(0)
        return root_item

    def size(self) -> int:
        """Return element count in O(1) time."""
        return len(self._heap)

    def is_empty(self) -> bool:
        """Return True if heap is empty."""
        return len(self._heap) == 0
