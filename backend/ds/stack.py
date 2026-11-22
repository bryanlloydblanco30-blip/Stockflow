"""
backend/ds/stack.py
LIFO stack written strictly from scratch using custom StackNode.
Contract: docs/adt/stack.md
Used by: single-level undo and void operation in POS / transactions.
"""


class StackNode:
    """Internal node for stack linked structure."""

    def __init__(self, data, next_node=None):
        self.data = data
        self.next = next_node


class Stack:
    """
    LIFO stack written strictly from scratch with O(1) push, pop, and peek.
    Zero Python list shortcuts used for internal storage.
    """

    def __init__(self):
        self._top = None
        self._size = 0

    def push(self, item) -> None:
        """Place item on top of the stack in O(1) time."""
        self._top = StackNode(item, next_node=self._top)
        self._size += 1

    def pop(self):
        """Remove and return the top item in O(1) time. Raises IndexError if empty."""
        if self._top is None:
            raise IndexError("pop from empty stack")
        item = self._top.data
        self._top = self._top.next
        self._size -= 1
        return item

    def peek(self):
        """Return the top item without removing it in O(1) time. Raises IndexError if empty."""
        if self._top is None:
            raise IndexError("peek from empty stack")
        return self._top.data

    def size(self) -> int:
        """Return element count in O(1) time."""
        return self._size

    def is_empty(self) -> bool:
        """Return True if empty in O(1) time."""
        return self._size == 0
