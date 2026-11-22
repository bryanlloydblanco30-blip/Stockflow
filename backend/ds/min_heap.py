"""
backend/ds/min_heap.py
Min-Heap written strictly from scratch.
Contract: docs/adt/min_heap.md
Used by: FEFO batch priority queue per product (earliest expiry first, received date tie-break).
Must NOT import heapq.
"""


class _HeapEntry:
    """Internal heap entry tracking key, tie-break, and payload."""

    __slots__ = ("key", "tie_break", "item")

    def __init__(self, key, tie_break, item):
        self.key = key
        self.tie_break = tie_break
        self.item = item

    def __lt__(self, other):
        if self.key != other.key:
            return self.key < other.key
        return self.tie_break < other.tie_break

    def __le__(self, other):
        if self.key != other.key:
            return self.key <= other.key
        return self.tie_break <= other.tie_break


class MinHeap:
    """
    Min-Heap written strictly from scratch supporting:
    - O(log n) insert and extract_min
    - O(1) peek_min
    - O(n) find + O(log n) restore for remove_specific (undoing receive)
    - Non-destructive ordered_read traversal
    """

    def __init__(self):
        self._heap: list[_HeapEntry] = []

    def _sift_up(self, idx: int) -> None:
        curr = idx
        while curr > 0:
            parent = (curr - 1) // 2
            if self._heap[curr] < self._heap[parent]:
                self._heap[curr], self._heap[parent] = (
                    self._heap[parent],
                    self._heap[curr],
                )
                curr = parent
            else:
                break

    def _sift_down(self, idx: int, heap_list: list[_HeapEntry] | None = None) -> None:
        h = self._heap if heap_list is None else heap_list
        curr = idx
        n = len(h)
        while True:
            left = 2 * curr + 1
            right = 2 * curr + 2
            smallest = curr

            if left < n and h[left] < h[smallest]:
                smallest = left
            if right < n and h[right] < h[smallest]:
                smallest = right

            if smallest != curr:
                h[curr], h[smallest] = h[smallest], h[curr]
                curr = smallest
            else:
                break

    def insert(self, item, key, tie_break=0) -> None:
        """Insert an item with a primary sorting key and secondary tie-break."""
        entry = _HeapEntry(key, tie_break, item)
        self._heap.append(entry)
        self._sift_up(len(self._heap) - 1)

    def peek_min(self):
        """Return the minimum item without removing it. Raises IndexError if empty."""
        if not self._heap:
            raise IndexError("peek from empty heap")
        return self._heap[0].item

    def extract_min(self):
        """Remove and return the minimum item. Raises IndexError if empty."""
        if not self._heap:
            raise IndexError("extract from empty heap")
        if len(self._heap) == 1:
            return self._heap.pop().item

        root_item = self._heap[0].item
        self._heap[0] = self._heap.pop()
        self._sift_down(0)
        return root_item

    def remove_specific(self, item_id) -> bool:
        """
        Locate and remove a specific batch by item.id or direct equality.
        Restores the heap invariant in O(log n) time.
        """
        target_idx = -1
        for i, entry in enumerate(self._heap):
            it = entry.item
            if (
                isinstance(it, dict) and it.get("id") == item_id
            ) or (
                hasattr(it, "id") and getattr(it, "id") == item_id
            ) or (
                it == item_id
            ):
                target_idx = i
                break

        if target_idx == -1:
            return False

        last_idx = len(self._heap) - 1
        if target_idx == last_idx:
            self._heap.pop()
            return True

        self._heap[target_idx] = self._heap.pop()
        self._sift_down(target_idx)
        self._sift_up(target_idx)
        return True

    def ordered_read(self):
        """
        Yield items in ascending order of (key, tie_break) without mutating the heap.
        Creates an internal copy and performs successive extractions.
        """
        if not self._heap:
            return

        copy_heap = list(self._heap)
        while copy_heap:
            if len(copy_heap) == 1:
                yield copy_heap.pop().item
                break
            min_item = copy_heap[0].item
            copy_heap[0] = copy_heap.pop()
            self._sift_down(0, copy_heap)
            yield min_item

    def size(self) -> int:
        """Return number of elements in the heap."""
        return len(self._heap)

    def is_empty(self) -> bool:
        """Return True if heap is empty."""
        return len(self._heap) == 0
