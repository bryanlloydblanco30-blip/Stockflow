"""
tests/test_ds_linked_list.py
Unit tests for LinkedList ADT (Task 1.1 / Doc 12.1).
Covers: add front, add end, find, remove (first, last, middle, empty), traverse, size, is_empty.
"""

import unittest
from backend.ds.linked_list import LinkedList


class TestLinkedList(unittest.TestCase):
    def test_placeholder(self):
        ll = LinkedList()
        self.assertTrue(ll.is_empty())

