"""
tests/test_services_undo.py
Tests for single-level undo and void transaction (Task 4.7 / Doc 6.7).
"""

import unittest
from backend.ds.stack import Stack


class TestUndoService(unittest.TestCase):
    def test_undo_stack_placeholder(self):
        s = Stack()
        self.assertEqual(s.size(), 0)

