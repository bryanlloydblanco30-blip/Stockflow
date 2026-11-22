# ADT Specification: Linked List

**Module**: `backend/ds/linked_list.py`
**Target Role**: Cart items, batches list per product, in-memory transaction log.

## Operations & Guarantees
- `add_front(item)`: Inserts a new element at the head in $O(1)$ time.
- `add_end(item)`: Inserts a new element at the tail in $O(1)$ time.
- `find(predicate)`: Linearly searches for first matching element in $O(n)$ time.
- `remove(predicate)`: Removes first matching element, repairing surrounding node links, in $O(n)$ time.
- `traverse()`: Yields elements in sequential order from head to tail in $O(n)$ time.
- `size()`: Returns current element count in $O(1)$ time.
- `is_empty()`: Returns `True` if size is 0, else `False` in $O(1)$ time.

## Rules & Constraints
- Must be written strictly from scratch using custom `Node` objects.
- No Python built-in list shortcuts for internal linked storage.

