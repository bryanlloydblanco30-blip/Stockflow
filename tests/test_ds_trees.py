"""
tests/test_ds_trees.py
Unit tests for BST & Trie (Tasks 1.5 & 1.6 / Doc 12.1).
"""

import unittest
from backend.ds.bst import BST
from backend.ds.trie import Trie


class TestTrees(unittest.TestCase):
    def test_placeholder(self):
        tree = BST()
        trie = Trie()
        self.assertEqual(tree.size(), 0)
        self.assertIsNotNone(trie)

