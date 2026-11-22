"""
tests/test_ds_heaps.py
Unit tests for MinHeap & MaxHeap (Tasks 1.3 & 1.4 / Doc 12.1).
"""

import unittest
from backend.ds.min_heap import MinHeap
from backend.ds.max_heap import MaxHeap


class TestHeaps(unittest.TestCase):
    def test_placeholder(self):
        min_h = MinHeap()
        max_h = MaxHeap()
        self.assertTrue(min_h.is_empty())
        self.assertTrue(max_h.is_empty())

