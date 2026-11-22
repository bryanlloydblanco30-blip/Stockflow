# ADT Specification: Min-Heap

**Module**: `backend/ds/min_heap.py`
**Target Role**: FEFO batch management per product (earliest expiry first; received date tie-break).

## Operations & Guarantees
- `insert(item, key, tie_break)`: Adds element and sifts up in $O(\log n)$ time.
- `peek_min()`: Inspects root element in $O(1)$ time without mutation.
- `extract_min()`: Removes and returns root item in $O(\log n)$ time.
- `remove_specific(item_id)`: Locates and removes a specific batch (for undoing receive) in $O(n)$ time and restores heap invariant in $O(\log n)$.
- `ordered_read()`: Iterates through items in sorted order without destroying the heap.
- `size()`: Returns item count in $O(1)$ time.
- `is_empty()`: Returns `True` if heap is empty in $O(1)$ time.

## Rules & Constraints
- Must NOT import `heapq`. Written strictly from scratch.

