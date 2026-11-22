"""
backend/ds/linked_list.py
Doubly/singly linked list written from scratch.
Contract: docs/adt/linked_list.md
"""


class Node:
    def __init__(self, data, prev_node=None, next_node=None):
        self.data = data
        self.prev = prev_node
        self.next = next_node


class LinkedList:
    def __init__(self):
        self.head = None
        self.tail = None
        self._size = 0

    def add_front(self, item) -> None:
        pass

    def add_end(self, item) -> None:
        pass

    def find(self, predicate):
        pass

    def remove(self, predicate) -> bool:
        pass

    def traverse(self):
        pass

    def size(self) -> int:
        return self._size

    def is_empty(self) -> bool:
        return self._size == 0

