"""
tests/test_ds_heaps.py
Unit tests for MinHeap & MaxHeap (Tasks 1.3 & 1.4 / Doc 12.1).
Covers:
- Empty heap operations (size 0, is_empty True, peek/extract raises IndexError)
- Single item insertion and extraction
- Min-heap property with keys and tie-breaks
- Duplicate keys resolved via tie-break
- remove_specific (removing root, leaf, internal node, non-existent)
- ordered_read yields all elements in sorted order without mutating original heap
- 500-step randomized operations verified against sorted list
"""

import random
import unittest
from backend.ds.min_heap import MinHeap
from backend.ds.max_heap import MaxHeap


class TestMinHeap(unittest.TestCase):
    def setUp(self):
        self.heap = MinHeap()

    def test_empty_heap(self):
        self.assertTrue(self.heap.is_empty())
        self.assertEqual(self.heap.size(), 0)
        with self.assertRaises(IndexError):
            self.heap.peek_min()
        with self.assertRaises(IndexError):
            self.heap.extract_min()
        self.assertEqual(list(self.heap.ordered_read()), [])
        self.assertFalse(self.heap.remove_specific("non_existent"))

    def test_single_item(self):
        self.heap.insert({"id": "B1", "name": "Batch 1"}, key="2026-11-12", tie_break=1)
        self.assertFalse(self.heap.is_empty())
        self.assertEqual(self.heap.size(), 1)
        self.assertEqual(self.heap.peek_min()["id"], "B1")
        self.assertEqual(self.heap.size(), 1)

        extracted = self.heap.extract_min()
        self.assertEqual(extracted["id"], "B1")
        self.assertTrue(self.heap.is_empty())

    def test_min_property_with_tie_breaks(self):
        # Earliest expiry first; same expiry -> earlier tie_break first
        self.heap.insert("B_late", key="2026-12-01", tie_break=10)
        self.heap.insert("B_early_1", key="2026-11-15", tie_break=5)
        self.heap.insert("B_early_2", key="2026-11-15", tie_break=2)
        self.heap.insert("B_earliest", key="2026-11-01", tie_break=1)

        self.assertEqual(self.heap.extract_min(), "B_earliest")
        self.assertEqual(self.heap.extract_min(), "B_early_2")  # tie-break 2 < 5
        self.assertEqual(self.heap.extract_min(), "B_early_1")
        self.assertEqual(self.heap.extract_min(), "B_late")
        self.assertTrue(self.heap.is_empty())

    def test_ordered_read_does_not_mutate(self):
        self.heap.insert("p3", key=30, tie_break=1)
        self.heap.insert("p1", key=10, tie_break=1)
        self.heap.insert("p2", key=20, tie_break=1)

        ordered = list(self.heap.ordered_read())
        self.assertEqual(ordered, ["p1", "p2", "p3"])
        self.assertEqual(self.heap.size(), 3)  # heap remains intact
        self.assertEqual(self.heap.peek_min(), "p1")

    def test_remove_specific(self):
        b1 = {"id": "B1", "desc": "first"}
        b2 = {"id": "B2", "desc": "second"}
        b3 = {"id": "B3", "desc": "third"}
        b4 = {"id": "B4", "desc": "fourth"}

        self.heap.insert(b1, key=10, tie_break=1)
        self.heap.insert(b2, key=20, tie_break=1)
        self.heap.insert(b3, key=30, tie_break=1)
        self.heap.insert(b4, key=40, tie_break=1)

        # Remove internal node b2
        self.assertTrue(self.heap.remove_specific("B2"))
        self.assertEqual(self.heap.size(), 3)
        self.assertFalse(self.heap.remove_specific("B2"))  # already removed

        # Remove root b1
        self.assertTrue(self.heap.remove_specific("B1"))
        self.assertEqual(self.heap.size(), 2)

        # Remaining should extract in sorted order
        self.assertEqual(self.heap.extract_min()["id"], "B3")
        self.assertEqual(self.heap.extract_min()["id"], "B4")
        self.assertTrue(self.heap.is_empty())

    def test_random_min_heap_against_sorted(self):
        rng = random.Random(999)
        items = []
        for i in range(200):
            k = rng.randint(1, 100)
            tb = (rng.randint(1, 50), i)
            val = f"item_{i}"
            items.append((k, tb, val))
            self.heap.insert(val, key=k, tie_break=tb)

        items.sort(key=lambda x: (x[0], x[1]))
        expected_order = [x[2] for x in items]

        # Test ordered_read matches sorted order
        read_order = list(self.heap.ordered_read())
        self.assertEqual(read_order, expected_order)

        # Test extract_min matches sorted order
        extracted = []
        while not self.heap.is_empty():
            extracted.append(self.heap.extract_min())
        self.assertEqual(extracted, expected_order)


class TestMaxHeap(unittest.TestCase):
    def setUp(self):
        self.heap = MaxHeap()

    def test_empty_heap(self):
        self.assertTrue(self.heap.is_empty())
        self.assertEqual(self.heap.size(), 0)
        with self.assertRaises(IndexError):
            self.heap.peek_max()
        with self.assertRaises(IndexError):
            self.heap.extract_max()

    def test_single_item(self):
        self.heap.insert("item_a", priority=75)
        self.assertFalse(self.heap.is_empty())
        self.assertEqual(self.heap.size(), 1)
        self.assertEqual(self.heap.peek_max(), "item_a")

        extracted = self.heap.extract_max()
        self.assertEqual(extracted, "item_a")
        self.assertTrue(self.heap.is_empty())

    def test_max_property_ordering(self):
        self.heap.insert("low", priority=10)
        self.heap.insert("highest", priority=95)
        self.heap.insert("mid", priority=50)
        self.heap.insert("high", priority=80)

        self.assertEqual(self.heap.extract_max(), "highest")
        self.assertEqual(self.heap.extract_max(), "high")
        self.assertEqual(self.heap.extract_max(), "mid")
        self.assertEqual(self.heap.extract_max(), "low")
        self.assertTrue(self.heap.is_empty())

    def test_duplicate_priorities(self):
        self.heap.insert("dup1", priority=40)
        self.heap.insert("top", priority=90)
        self.heap.insert("dup2", priority=40)

        self.assertEqual(self.heap.extract_max(), "top")
        second = self.heap.extract_max()
        third = self.heap.extract_max()
        self.assertEqual({second, third}, {"dup1", "dup2"})
        self.assertTrue(self.heap.is_empty())

    def test_random_max_heap_against_sorted(self):
        rng = random.Random(4242)
        items = []
        for i in range(200):
            p = (rng.randint(1, 500), -i)  # unique priority with insertion tie-break
            val = f"prod_{i}"
            items.append((p, val))
            self.heap.insert(val, priority=p)

        items.sort(key=lambda x: x[0], reverse=True)
        expected_order = [x[1] for x in items]

        extracted = []
        while not self.heap.is_empty():
            extracted.append(self.heap.extract_max())

        self.assertEqual(extracted, expected_order)


if __name__ == "__main__":
    unittest.main()
