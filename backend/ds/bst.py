"""
backend/ds/bst.py
Binary Search Tree written from scratch for barcode lookup.
Contract: docs/adt/bst.md
"""


class BSTNode:
    def __init__(self, key, value):
        self.key = key
        self.value = value
        self.left = None
        self.right = None


class BST:
    def __init__(self):
        self.root = None
        self._size = 0

    def insert(self, key, value) -> None:
        pass

    def find(self, key):
        pass

    def delete(self, key) -> bool:
        pass

    def in_order(self):
        pass

    def size(self) -> int:
        return self._size

