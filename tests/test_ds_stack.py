"""
tests/test_ds_stack.py
Unit tests for Stack ADT (Task 1.2 / Doc 12.1).
"""

import unittest
from backend.ds.stack import Stack


class TestStack(unittest.TestCase):
    def test_placeholder(self):
        s = Stack()
        self.assertTrue(s.is_empty())

