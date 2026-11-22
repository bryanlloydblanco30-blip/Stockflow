"""
backend/ds/bst.py
Binary Search Tree written strictly from scratch.
Contract: docs/adt/bst.md
Used by: product barcode lookup (Doc 6.1, Phase 1.5).
Must NOT use dict shortcuts for the structure's core lookup job.
"""


class BSTNode:
    """Internal binary search tree node."""

    def __init__(self, key: str, value):
        self.key = key
        self.value = value
        self.left = None
        self.right = None


class BST:
    """
    Binary Search Tree written strictly from scratch.
    Supports insert, find, delete (leaf, 1 child, 2 children), in-order traversal, min, and max.
    Rejects duplicate keys with ValueError.
    """

    def __init__(self):
        self.root = None
        self._size = 0

    def insert(self, key: str, value) -> None:
        """Insert a key-value pair. Rejects duplicate keys with ValueError."""
        if self.root is None:
            self.root = BSTNode(key, value)
            self._size = 1
            return

        curr = self.root
        while True:
            if key == curr.key:
                raise ValueError(f"Duplicate key: {key}")
            elif key < curr.key:
                if curr.left is None:
                    curr.left = BSTNode(key, value)
                    self._size += 1
                    return
                curr = curr.left
            else:
                if curr.right is None:
                    curr.right = BSTNode(key, value)
                    self._size += 1
                    return
                curr = curr.right

    def find(self, key: str):
        """Find and return value associated with key, or None if not found."""
        curr = self.root
        while curr is not None:
            if key == curr.key:
                return curr.value
            elif key < curr.key:
                curr = curr.left
            else:
                curr = curr.right
        return None

    def min(self) -> tuple[str, any] | None:
        """Return (key, value) of minimum key, or None if empty."""
        if self.root is None:
            return None
        curr = self.root
        while curr.left is not None:
            curr = curr.left
        return (curr.key, curr.value)

    def max(self) -> tuple[str, any] | None:
        """Return (key, value) of maximum key, or None if empty."""
        if self.root is None:
            return None
        curr = self.root
        while curr.right is not None:
            curr = curr.right
        return (curr.key, curr.value)

    def delete(self, key: str) -> bool:
        """
        Delete key from the tree covering all cases:
        - leaf node
        - 1 child (left or right)
        - 2 children (replaces with in-order successor)
        Returns True if deleted, False if key was not found.
        """
        parent = None
        curr = self.root
        is_left_child = False

        # Locate node and its parent
        while curr is not None and curr.key != key:
            parent = curr
            if key < curr.key:
                curr = curr.left
                is_left_child = True
            else:
                curr = curr.right
                is_left_child = False

        if curr is None:
            return False

        # Case 1: Leaf node (no children)
        if curr.left is None and curr.right is None:
            if curr == self.root:
                self.root = None
            elif is_left_child:
                parent.left = None
            else:
                parent.right = None

        # Case 2: One child (only right child)
        elif curr.left is None:
            if curr == self.root:
                self.root = curr.right
            elif is_left_child:
                parent.left = curr.right
            else:
                parent.right = curr.right

        # Case 2: One child (only left child)
        elif curr.right is None:
            if curr == self.root:
                self.root = curr.left
            elif is_left_child:
                parent.left = curr.left
            else:
                parent.right = curr.left

        # Case 3: Two children
        else:
            # Find in-order successor (minimum in right subtree) and its parent
            successor_parent = curr
            successor = curr.right
            while successor.left is not None:
                successor_parent = successor
                successor = successor.left

            # Copy successor key & value to current node
            curr.key = successor.key
            curr.value = successor.value

            # Delete successor from its old position (successor has at most a right child)
            if successor_parent == curr:
                successor_parent.right = successor.right
            else:
                successor_parent.left = successor.right

        self._size -= 1
        return True

    def in_order(self):
        """Yield (key, value) pairs in ascending key order using in-order traversal."""
        stack = []
        curr = self.root
        while stack or curr is not None:
            if curr is not None:
                stack.append(curr)
                curr = curr.left
            else:
                curr = stack.pop()
                yield (curr.key, curr.value)
                curr = curr.right

    def size(self) -> int:
        """Return number of nodes in tree."""
        return self._size

    def is_empty(self) -> bool:
        """Return True if tree is empty."""
        return self._size == 0
