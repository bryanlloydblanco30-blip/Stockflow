"""
tests/test_ds_prefix_topk.py
Unit tests for PrefixSums & SizeKHeap (Tasks 1.7 & 1.8 / Doc 12.1).
"""

import unittest
from backend.ds.prefix_sums import PrefixSums
from backend.ds.size_k_heap import SizeKHeap


class TestPrefixTopK(unittest.TestCase):
    def test_placeholder(self):
        ps = PrefixSums()
        sk = SizeKHeap(k=5)
        self.assertEqual(ps.size(), 0)
        self.assertEqual(sk.k, 5)

