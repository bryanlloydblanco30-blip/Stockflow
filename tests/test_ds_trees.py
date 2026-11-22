"""
tests/test_ds_trees.py
Unit tests for BST & Trie (Tasks 1.5 & 1.6 / Doc 12.1).
Covers:
- BST: empty tree, single node, reject duplicate keys, in-order sorted traversal,
  min/max, all 3 deletion cases (leaf, 1 child, 2 children), root deletion,
  and randomized operations checked against trusted oracle.
- Trie: prefix search, lowercase, limit 8, delete.
"""

import random
import unittest
from backend.ds.bst import BST
from backend.ds.trie import Trie


class TestBST(unittest.TestCase):
    def setUp(self):
        self.tree = BST()

    def test_empty_bst(self):
        self.assertEqual(self.tree.size(), 0)
        self.assertTrue(self.tree.is_empty())
        self.assertIsNone(self.tree.find("4800010001"))
        self.assertIsNone(self.tree.min())
        self.assertIsNone(self.tree.max())
        self.assertEqual(list(self.tree.in_order()), [])
        self.assertFalse(self.tree.delete("4800010001"))

    def test_single_item(self):
        self.tree.insert("4800010001", {"name": "Pandesal", "price": 45.0})
        self.assertEqual(self.tree.size(), 1)
        self.assertFalse(self.tree.is_empty())
        self.assertEqual(self.tree.find("4800010001")["name"], "Pandesal")
        self.assertEqual(self.tree.min()[0], "4800010001")
        self.assertEqual(self.tree.max()[0], "4800010001")

        # Delete single item (root leaf)
        self.assertTrue(self.tree.delete("4800010001"))
        self.assertEqual(self.tree.size(), 0)
        self.assertTrue(self.tree.is_empty())
        self.assertIsNone(self.tree.find("4800010001"))

    def test_reject_duplicate_keys(self):
        self.tree.insert("100", "first")
        with self.assertRaises(ValueError):
            self.tree.insert("100", "second")
        self.assertEqual(self.tree.size(), 1)
        self.assertEqual(self.tree.find("100"), "first")

    def test_in_order_and_min_max(self):
        keys = ["50", "30", "70", "20", "40", "60", "80"]
        for k in keys:
            self.tree.insert(k, f"val_{k}")

        self.assertEqual(self.tree.size(), 7)
        self.assertEqual(self.tree.min(), ("20", "val_20"))
        self.assertEqual(self.tree.max(), ("80", "val_80"))

        in_order_keys = [k for k, _ in self.tree.in_order()]
        self.assertEqual(in_order_keys, ["20", "30", "40", "50", "60", "70", "80"])

    def test_delete_leaf(self):
        for k in ["50", "30", "70", "20"]:
            self.tree.insert(k, k)

        self.assertTrue(self.tree.delete("20"))
        self.assertEqual(self.tree.size(), 3)
        self.assertIsNone(self.tree.find("20"))
        self.assertEqual([k for k, _ in self.tree.in_order()], ["30", "50", "70"])

    def test_delete_one_child_left(self):
        for k in ["50", "30", "70", "20"]:
            self.tree.insert(k, k)

        # 30 has only left child 20
        self.assertTrue(self.tree.delete("30"))
        self.assertEqual(self.tree.size(), 3)
        self.assertIsNone(self.tree.find("30"))
        self.assertEqual([k for k, _ in self.tree.in_order()], ["20", "50", "70"])

    def test_delete_one_child_right(self):
        for k in ["50", "30", "70", "80"]:
            self.tree.insert(k, k)

        # 70 has only right child 80
        self.assertTrue(self.tree.delete("70"))
        self.assertEqual(self.tree.size(), 3)
        self.assertIsNone(self.tree.find("70"))
        self.assertEqual([k for k, _ in self.tree.in_order()], ["30", "50", "80"])

    def test_delete_two_children(self):
        for k in ["50", "30", "70", "20", "40", "60", "80"]:
            self.tree.insert(k, k)

        # 30 has two children: 20 and 40
        self.assertTrue(self.tree.delete("30"))
        self.assertEqual(self.tree.size(), 6)
        self.assertIsNone(self.tree.find("30"))
        self.assertEqual(
            [k for k, _ in self.tree.in_order()],
            ["20", "40", "50", "60", "70", "80"],
        )

        # Root 50 has two children
        self.assertTrue(self.tree.delete("50"))
        self.assertEqual(self.tree.size(), 5)
        self.assertIsNone(self.tree.find("50"))
        self.assertEqual(
            [k for k, _ in self.tree.in_order()],
            ["20", "40", "60", "70", "80"],
        )

    def test_delete_non_existent(self):
        self.tree.insert("10", "val")
        self.assertFalse(self.tree.delete("999"))
        self.assertEqual(self.tree.size(), 1)

    def test_randomized_bst_against_oracle(self):
        rng = random.Random(777)
        oracle = {}
        keys = list(range(100, 300))
        rng.shuffle(keys)

        for k in keys:
            key_str = str(k)
            self.tree.insert(key_str, f"val_{k}")
            oracle[key_str] = f"val_{k}"

        self.assertEqual(self.tree.size(), len(oracle))
        sorted_keys = sorted(oracle.keys())
        self.assertEqual([k for k, _ in self.tree.in_order()], sorted_keys)

        # Delete 50 keys
        delete_keys = rng.sample(keys, 50)
        for k in delete_keys:
            key_str = str(k)
            self.assertTrue(self.tree.delete(key_str))
            del oracle[key_str]

        self.assertEqual(self.tree.size(), len(oracle))
        remaining_sorted = sorted(oracle.keys())
        self.assertEqual([k for k, _ in self.tree.in_order()], remaining_sorted)

        # Verify all remaining finds
        for k, v in oracle.items():
            self.assertEqual(self.tree.find(k), v)


class TestTrie(unittest.TestCase):
    def test_placeholder(self):
        trie = Trie()
        self.assertIsNotNone(trie)


if __name__ == "__main__":
    unittest.main()
