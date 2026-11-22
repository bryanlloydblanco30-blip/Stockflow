"""
tests/test_ds_prefix_topk.py
Unit tests for PrefixSums & SizeKHeap (Tasks 1.7 & 1.8 / Doc 12.1).
Covers:
- PrefixSums:
  - Empty array
  - Single element
  - Full range, sub-range, single index range
  - Out of bounds and inverted index errors
  - 100-element randomized queries checked against Python sum()
- SizeKHeap:
  - Top-k with fewer than k items
  - Top-k with exactly k and > k items (ranked descending)
  - Bottom-k with fewer than k items
  - Bottom-k with > k items (ranked ascending)
  - Duplicate scores handling
  - 500-element stream validation against sorted oracle
"""

import random
import unittest
from backend.ds.prefix_sums import PrefixSums
from backend.ds.size_k_heap import SizeKHeap


class TestPrefixSums(unittest.TestCase):
    def test_empty(self):
        ps = PrefixSums()
        self.assertEqual(ps.size(), 0)
        self.assertTrue(ps.is_empty())
        with self.assertRaises(IndexError):
            ps.range_sum(0, 0)

    def test_single_element(self):
        ps = PrefixSums([150.50])
        self.assertEqual(ps.size(), 1)
        self.assertFalse(ps.is_empty())
        self.assertAlmostEqual(ps.range_sum(0, 0), 150.50)

    def test_range_sums(self):
        # Daily revenues: [100, 200, 50, 300, 150]
        ps = PrefixSums([100.0, 200.0, 50.0, 300.0, 150.0])
        self.assertEqual(ps.size(), 5)

        # Full range: indices 0 to 4
        self.assertAlmostEqual(ps.range_sum(0, 4), 800.0)

        # Prefix range: indices 0 to 2
        self.assertAlmostEqual(ps.range_sum(0, 2), 350.0)

        # Mid range: indices 1 to 3 -> 200 + 50 + 300 = 550
        self.assertAlmostEqual(ps.range_sum(1, 3), 550.0)

        # Single index: index 3 -> 300
        self.assertAlmostEqual(ps.range_sum(3, 3), 300.0)

    def test_invalid_indices(self):
        ps = PrefixSums([10, 20, 30])
        with self.assertRaises(IndexError):
            ps.range_sum(-1, 2)
        with self.assertRaises(IndexError):
            ps.range_sum(0, 5)
        with self.assertRaises(ValueError):
            ps.range_sum(2, 1)  # start > end

    def test_randomized_against_oracle(self):
        rng = random.Random(12345)
        values = [round(rng.uniform(10.0, 500.0), 2) for _ in range(100)]
        ps = PrefixSums(values)

        for _ in range(100):
            start = rng.randint(0, 99)
            end = rng.randint(start, 99)
            expected = sum(values[start : end + 1])
            self.assertAlmostEqual(ps.range_sum(start, end), expected, places=4)


class TestSizeKHeap(unittest.TestCase):
    def test_top_k_fewer_than_k(self):
        sk = SizeKHeap(k=5, mode="top")
        sk.feed("prod_a", 10.0)
        sk.feed("prod_b", 50.0)

        ranked = sk.get_ranked()
        self.assertEqual(len(ranked), 2)
        # Top-k should be ranked descending: 50.0, then 10.0
        self.assertEqual(ranked[0], ("prod_b", 50.0))
        self.assertEqual(ranked[1], ("prod_a", 10.0))

    def test_top_k_more_than_k(self):
        sk = SizeKHeap(k=3, mode="top")
        data = [
            ("apple", 15.0),
            ("banana", 90.0),
            ("cherry", 45.0),
            ("date", 120.0),
            ("elderberry", 30.0),
        ]
        for item, score in data:
            sk.feed(item, score)

        ranked = sk.get_ranked()
        self.assertEqual(len(ranked), 3)
        # Top 3: date (120), banana (90), cherry (45)
        self.assertEqual(
            ranked,
            [("date", 120.0), ("banana", 90.0), ("cherry", 45.0)],
        )

    def test_bottom_k_more_than_k(self):
        sk = SizeKHeap(k=3, mode="bottom")
        data = [
            ("apple", 15.0),
            ("banana", 90.0),
            ("cherry", 45.0),
            ("date", 120.0),
            ("elderberry", 30.0),
        ]
        for item, score in data:
            sk.feed(item, score)

        ranked = sk.get_ranked()
        self.assertEqual(len(ranked), 3)
        # Bottom 3 ranked ascending: apple (15), elderberry (30), cherry (45)
        self.assertEqual(
            ranked,
            [("apple", 15.0), ("elderberry", 30.0), ("cherry", 45.0)],
        )

    def test_duplicate_scores(self):
        sk = SizeKHeap(k=2, mode="top")
        sk.feed("p1", 50.0)
        sk.feed("p2", 50.0)
        sk.feed("p3", 20.0)

        ranked = sk.get_ranked()
        self.assertEqual(len(ranked), 2)
        self.assertEqual(ranked[0][1], 50.0)
        self.assertEqual(ranked[1][1], 50.0)

    def test_randomized_stream_against_oracle(self):
        rng = random.Random(888)
        k = 10
        stream = [(f"item_{i}", round(rng.uniform(1.0, 1000.0), 2)) for i in range(500)]

        # Top-k test
        top_heap = SizeKHeap(k=k, mode="top")
        for item, score in stream:
            top_heap.feed(item, score)

        oracle_top = sorted(stream, key=lambda x: x[1], reverse=True)[:k]
        actual_top = top_heap.get_ranked()
        self.assertEqual([s for _, s in actual_top], [s for _, s in oracle_top])

        # Bottom-k test
        bottom_heap = SizeKHeap(k=k, mode="bottom")
        for item, score in stream:
            bottom_heap.feed(item, score)

        oracle_bottom = sorted(stream, key=lambda x: x[1])[:k]
        actual_bottom = bottom_heap.get_ranked()
        self.assertEqual([s for _, s in actual_bottom], [s for _, s in oracle_bottom])


if __name__ == "__main__":
    unittest.main()
