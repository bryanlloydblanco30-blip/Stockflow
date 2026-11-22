# ADT Specification: Stack

**Module**: `backend/ds/stack.py`
**Target Role**: LIFO storage for single-level transaction undo and void operations.

## Operations & Guarantees
- `push(item)`: Places item on top of the stack in $O(1)$ time.
- `pop()`: Removes and returns the top item in $O(1)$ time. Raises `IndexError` on empty.
- `peek()`: Returns top item without removing it in $O(1)$ time. Raises `IndexError` on empty.
- `size()`: Returns current item count in $O(1)$ time.
- `is_empty()`: Returns `True` if size is 0, else `False` in $O(1)$ time.

## Rules & Constraints
- Must be written from scratch (node-based or bounded array).

