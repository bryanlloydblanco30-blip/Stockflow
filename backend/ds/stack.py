"""
backend/ds/stack.py
LIFO stack written from scratch.
Contract: docs/adt/stack.md
"""


class Stack:
    def __init__(self):
        self._items = []

    def push(self, item) -> None:
        pass

    def pop(self):
        pass

    def peek(self):
        pass

    def size(self) -> int:
        return len(self._items)

    def is_empty(self) -> bool:
        return len(self._items) == 0

