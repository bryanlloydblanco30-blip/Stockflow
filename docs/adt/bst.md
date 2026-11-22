# ADT Specification: Binary Search Tree (BST)

**Module**: `backend/ds/bst.py`
**Target Role**: Product lookup by barcode.

## Operations & Guarantees
- `insert(key, value)`: Inserts key-value node in average $O(\log n)$, worst $O(n)$. Rejects duplicates.
- `find(key)`: Returns value associated with key in average $O(\log n)$, worst $O(n)$.
- `delete(key)`: Removes key covering leaf, 1-child, and 2-children cases in average $O(\log n)$, worst $O(n)$.
- `in_order()`: Yields items in ascending sorted key order in $O(n)$ time.
- `min()` / `max()`: Returns minimum / maximum key in tree.
- `size()`: Returns total nodes.

## Rules & Constraints
- Must NOT use `dict` shortcuts for lookup.

