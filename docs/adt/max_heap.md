# ADT Specification: Max-Heap (Priority Queue)

**Module**: `backend/ds/max_heap.py`
**Target Role**: Urgency ranking for restock candidates.

## Operations & Guarantees
- `insert(item, priority)`: Inserts element into heap in $O(\log n)$ time.
- `peek_max()`: Returns element with highest priority in $O(1)$ time.
- `extract_max()`: Removes and returns element with highest priority in $O(\log n)$ time.
- `size()`: Returns current count in $O(1)$ time.
- `is_empty()`: Returns `True` if size is 0, else `False` in $O(1)$ time.

## Rules & Constraints
- Must NOT import `heapq`.

