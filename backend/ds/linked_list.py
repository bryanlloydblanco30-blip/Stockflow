"""
backend/ds/linked_list.py
Doubly linked list written strictly from scratch.
Contract: docs/adt/linked_list.md
Used by: cart, batches per product, in-memory transaction log.
"""


class Node:
    """Internal doubly linked list node."""

    def __init__(self, data, prev_node=None, next_node=None):
        self.data = data
        self.prev = prev_node
        self.next = next_node


class LinkedList:
    """
    Doubly linked list supporting $O(1)$ front/end additions and $O(n)$ search/removal.
    Written strictly from scratch with no built-in list shortcuts for storage.
    """

    def __init__(self):
        self.head = None
        self.tail = None
        self._size = 0

    def add_front(self, item) -> None:
        """Insert element at head in O(1) time."""
        new_node = Node(item, prev_node=None, next_node=self.head)
        if self.head is not None:
            self.head.prev = new_node
        else:
            self.tail = new_node
        self.head = new_node
        self._size += 1

    def add_end(self, item) -> None:
        """Insert element at tail in O(1) time."""
        new_node = Node(item, prev_node=self.tail, next_node=None)
        if self.tail is not None:
            self.tail.next = new_node
        else:
            self.head = new_node
        self.tail = new_node
        self._size += 1

    def find(self, predicate):
        """Linearly search for first matching element in O(n) time. Returns item or None."""
        curr = self.head
        while curr is not None:
            if predicate(curr.data):
                return curr.data
            curr = curr.next
        return None

    def remove(self, predicate) -> bool:
        """
        Remove first element matching predicate, repairing surrounding node links.
        Returns True if an element was removed, False otherwise.
        """
        curr = self.head
        while curr is not None:
            if predicate(curr.data):
                # Detach curr
                if curr.prev is not None:
                    curr.prev.next = curr.next
                else:
                    self.head = curr.next

                if curr.next is not None:
                    curr.next.prev = curr.prev
                else:
                    self.tail = curr.prev

                self._size -= 1
                return True
            curr = curr.next
        return False

    def traverse(self):
        """Yield elements in sequential order from head to tail."""
        curr = self.head
        while curr is not None:
            yield curr.data
            curr = curr.next

    def size(self) -> int:
        """Return element count in O(1) time."""
        return self._size

    def is_empty(self) -> bool:
        """Return True if list is empty in O(1) time."""
        return self._size == 0
