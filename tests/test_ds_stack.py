"""
tests/test_ds_stack.py
Unit tests for Stack ADT (Task 1.2 / Doc 12.1).
Covers:
- Empty stack operations (is_empty True, size 0, pop raises IndexError, peek raises IndexError)
- Single item push, peek, pop
- Multiple items and LIFO ordering
- Duplicates handling
- Large randomized push/pop sequence checked against Python list as trusted oracle
"""

import random
import unittest
from backend.ds.stack import Stack


class TestStack(unittest.TestCase):
    def setUp(self):
        self.stack = Stack()

    def test_empty_stack(self):
        self.assertTrue(self.stack.is_empty())
        self.assertEqual(self.stack.size(), 0)
        with self.assertRaises(IndexError):
            self.stack.pop()
        with self.assertRaises(IndexError):
            self.stack.peek()

    def test_single_item(self):
        self.stack.push("tx_1")
        self.assertFalse(self.stack.is_empty())
        self.assertEqual(self.stack.size(), 1)
        self.assertEqual(self.stack.peek(), "tx_1")
        self.assertEqual(self.stack.size(), 1)  # peek must not remove item

        item = self.stack.pop()
        self.assertEqual(item, "tx_1")
        self.assertTrue(self.stack.is_empty())
        self.assertEqual(self.stack.size(), 0)

    def test_lifo_order(self):
        for i in range(1, 6):
            self.stack.push(f"action_{i}")

        self.assertEqual(self.stack.size(), 5)
        self.assertEqual(self.stack.peek(), "action_5")

        popped = []
        while not self.stack.is_empty():
            popped.append(self.stack.pop())

        self.assertEqual(
            popped,
            ["action_5", "action_4", "action_3", "action_2", "action_1"],
        )
        self.assertEqual(self.stack.size(), 0)

    def test_duplicates(self):
        self.stack.push(10)
        self.stack.push(20)
        self.stack.push(10)
        self.assertEqual(self.stack.pop(), 10)
        self.assertEqual(self.stack.pop(), 20)
        self.assertEqual(self.stack.pop(), 10)
        self.assertTrue(self.stack.is_empty())

    def test_random_operations_against_oracle(self):
        oracle = []
        rng = random.Random(1337)

        for _ in range(500):
            if not oracle or rng.random() > 0.4:
                val = rng.randint(1, 1000)
                self.stack.push(val)
                oracle.append(val)
            else:
                expected = oracle.pop()
                self.assertEqual(self.stack.peek(), expected)
                actual = self.stack.pop()
                self.assertEqual(actual, expected)

            self.assertEqual(self.stack.size(), len(oracle))
            self.assertEqual(self.stack.is_empty(), len(oracle) == 0)


if __name__ == "__main__":
    unittest.main()
