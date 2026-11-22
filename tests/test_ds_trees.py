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
    def setUp(self):
        self.trie = Trie()

    def test_empty_trie(self):
        self.assertIsNone(self.trie.find_prefix("pan"))
        self.assertEqual(self.trie.list_under_prefix("pan"), [])
        self.assertFalse(self.trie.delete("pan"))

    def test_single_word(self):
        self.trie.insert("Pandesal", {"id": "P1", "name": "Pandesal"})
        # Case insensitive prefix find
        node = self.trie.find_prefix("pan")
        self.assertIsNotNone(node)

        results = self.trie.list_under_prefix("PAN")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["name"], "Pandesal")

        # Delete
        self.assertTrue(self.trie.delete("pandesal"))
        self.assertIsNone(self.trie.find_prefix("pandesal"))
        self.assertEqual(self.trie.list_under_prefix("pan"), [])

    def test_prefix_listing_limit_8(self):
        # Insert 12 items starting with 'choc'
        for i in range(12):
            self.trie.insert(f"chocolate_{i:02d}", f"val_{i}")

        # Default limit is 8
        matches = self.trie.list_under_prefix("choc")
        self.assertEqual(len(matches), 8)

        # Custom limit
        all_matches = self.trie.list_under_prefix("choc", limit=15)
        self.assertEqual(len(all_matches), 12)

    def test_prefix_overlap_and_deletion(self):
        self.trie.insert("pan", "short")
        self.trie.insert("pandesal", "long")
        self.trie.insert("pancake", "other")

        # Delete "pan" - "pandesal" and "pancake" must remain
        self.assertTrue(self.trie.delete("pan"))
        self.assertFalse(self.trie.delete("pan"))  # already deleted

        matches = self.trie.list_under_prefix("pan")
        self.assertEqual(set(matches), {"long", "other"})

        # Delete "pandesal"
        self.assertTrue(self.trie.delete("pandesal"))
        matches_after = self.trie.list_under_prefix("pan")
        self.assertEqual(matches_after, ["other"])

    def test_randomized_trie_against_oracle(self):
        words = [
            "apple", "apricot", "avocado", "banana", "blackberry",
            "blueberry", "bread", "butter", "cheese", "cherry",
            "chocolate", "coffee", "cookies", "cream", "croissant"
        ]
        for w in words:
            self.trie.insert(w, w)

        # Check prefix matches for 'b'
        b_oracle = [w for w in words if w.startswith("b")]
        b_trie = self.trie.list_under_prefix("B", limit=10)
        self.assertEqual(set(b_trie), set(b_oracle))

        # Check prefix matches for 'ch'
        ch_oracle = [w for w in words if w.startswith("ch")]
        ch_trie = self.trie.list_under_prefix("CH", limit=10)
        self.assertEqual(set(ch_trie), set(ch_oracle))

        # Delete 'cheese'
        self.assertTrue(self.trie.delete("cheese"))
        self.assertNotIn("cheese", self.trie.list_under_prefix("ch"))


if __name__ == "__main__":
    unittest.main()
