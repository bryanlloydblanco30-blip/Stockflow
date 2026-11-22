"""
tests/test_ds_linked_list.py
Unit tests for LinkedList ADT (Task 1.1 / Doc 12.1).
Covers:
- Empty structure (size 0, is_empty True, traverse empty, find returns None, remove returns False)
- Single item (add_front, add_end, find, remove)
- Multiple items and ordering (add_front, add_end, mixed)
- Duplicates handling
- Deletion cases (head, tail, middle, non-existent, all items)
- Large random input checked against Python list as trusted ground truth
"""

import random
import unittest
from backend.ds.linked_list import LinkedList


class TestLinkedList(unittest.TestCase):
    def setUp(self):
        self.ll = LinkedList()

    def test_empty_list(self):
        self.assertTrue(self.ll.is_empty())
        self.assertEqual(self.ll.size(), 0)
        self.assertIsNone(self.ll.find(lambda x: True))
        self.assertFalse(self.ll.remove(lambda x: True))
        self.assertEqual(list(self.ll.traverse()), [])

    def test_single_item_add_front(self):
        self.ll.add_front(42)
        self.assertFalse(self.ll.is_empty())
        self.assertEqual(self.ll.size(), 1)
        self.assertEqual(self.ll.find(lambda x: x == 42), 42)
        self.assertEqual(list(self.ll.traverse()), [42])

        # Remove single item
        self.assertTrue(self.ll.remove(lambda x: x == 42))
        self.assertTrue(self.ll.is_empty())
        self.assertEqual(self.ll.size(), 0)
        self.assertEqual(list(self.ll.traverse()), [])

    def test_single_item_add_end(self):
        self.ll.add_end("alpha")
        self.assertFalse(self.ll.is_empty())
        self.assertEqual(self.ll.size(), 1)
        self.assertEqual(self.ll.find(lambda x: x == "alpha"), "alpha")
        self.assertEqual(list(self.ll.traverse()), ["alpha"])

        self.assertTrue(self.ll.remove(lambda x: x == "alpha"))
        self.assertTrue(self.ll.is_empty())
        self.assertEqual(self.ll.size(), 0)

    def test_add_front_ordering(self):
        self.ll.add_front(1)
        self.ll.add_front(2)
        self.ll.add_front(3)
        self.assertEqual(self.ll.size(), 3)
        self.assertEqual(list(self.ll.traverse()), [3, 2, 1])

    def test_add_end_ordering(self):
        self.ll.add_end(10)
        self.ll.add_end(20)
        self.ll.add_end(30)
        self.assertEqual(self.ll.size(), 3)
        self.assertEqual(list(self.ll.traverse()), [10, 20, 30])

    def test_find_with_predicate(self):
        self.ll.add_end({"id": 1, "name": "Apple"})
        self.ll.add_end({"id": 2, "name": "Banana"})
        self.ll.add_end({"id": 3, "name": "Cherry"})

        found = self.ll.find(lambda item: item["id"] == 2)
        self.assertIsNotNone(found)
        self.assertEqual(found["name"], "Banana")

        not_found = self.ll.find(lambda item: item["id"] == 999)
        self.assertIsNone(not_found)

    def test_remove_head(self):
        self.ll.add_end(1)
        self.ll.add_end(2)
        self.ll.add_end(3)

        self.assertTrue(self.ll.remove(lambda x: x == 1))
        self.assertEqual(self.ll.size(), 2)
        self.assertEqual(list(self.ll.traverse()), [2, 3])

    def test_remove_tail(self):
        self.ll.add_end(1)
        self.ll.add_end(2)
        self.ll.add_end(3)

        self.assertTrue(self.ll.remove(lambda x: x == 3))
        self.assertEqual(self.ll.size(), 2)
        self.assertEqual(list(self.ll.traverse()), [1, 2])

    def test_remove_middle(self):
        self.ll.add_end(1)
        self.ll.add_end(2)
        self.ll.add_end(3)

        self.assertTrue(self.ll.remove(lambda x: x == 2))
        self.assertEqual(self.ll.size(), 2)
        self.assertEqual(list(self.ll.traverse()), [1, 3])

    def test_remove_non_existent(self):
        self.ll.add_end(100)
        self.ll.add_end(200)

        self.assertFalse(self.ll.remove(lambda x: x == 999))
        self.assertEqual(self.ll.size(), 2)
        self.assertEqual(list(self.ll.traverse()), [100, 200])

    def test_remove_first_duplicate_only(self):
        self.ll.add_end("dup")
        self.ll.add_end("unique")
        self.ll.add_end("dup")

        self.assertTrue(self.ll.remove(lambda x: x == "dup"))
        self.assertEqual(self.ll.size(), 2)
        self.assertEqual(list(self.ll.traverse()), ["unique", "dup"])

    def test_large_random_operations_against_oracle(self):
        oracle = []
        rng = random.Random(42)

        for _ in range(500):
            op = rng.choice(["add_front", "add_end", "find", "remove"])
            val = rng.randint(1, 100)

            if op == "add_front":
                self.ll.add_front(val)
                oracle.insert(0, val)
            elif op == "add_end":
                self.ll.add_end(val)
                oracle.append(val)
            elif op == "find":
                ll_found = self.ll.find(lambda x, v=val: x == v)
                oracle_found = val if val in oracle else None
                self.assertEqual(ll_found, oracle_found)
            elif op == "remove":
                ll_removed = self.ll.remove(lambda x, v=val: x == v)
                if val in oracle:
                    oracle.remove(val)
                    oracle_removed = True
                else:
                    oracle_removed = False
                self.assertEqual(ll_removed, oracle_removed)

            self.assertEqual(self.ll.size(), len(oracle))
            self.assertEqual(self.ll.is_empty(), len(oracle) == 0)

        # Final state check
        self.assertEqual(list(self.ll.traverse()), oracle)


if __name__ == "__main__":
    unittest.main()
