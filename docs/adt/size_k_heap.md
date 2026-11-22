# ADT Specification: Size-k Heap Routine

**Module**: `backend/ds/size_k_heap.py`
**Target Role**: Top-k and bottom-k fast and slow mover analytics (Doc 10.1).

## Operations & Guarantees
- `feed(item, score)`: Evaluates item against bounded heap of size $k$ in $O(\log k)$ time.
- `get_top_k()`: Returns $k$ highest scoring items ranked descending.
- `get_bottom_k()`: Returns $k$ lowest scoring items ranked ascending.
- Total complexity for $n$ items: $O(n \log k)$.

## Rules & Constraints
- Must NOT use `sorted(list)` or `heapq.nlargest`.

