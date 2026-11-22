"""
tests/test_models_storage.py
Tests for SQLite schema, atomic sale persistence, and save/load (Task 2.5).
"""

import unittest
import sqlite3
from backend.db.schema import init_schema


class TestModelsStorage(unittest.TestCase):
    def test_schema_init(self):
        conn = sqlite3.connect(":memory:")
        init_schema(conn)
        cursor = conn.cursor()
        cursor.execute("SELECT version FROM schema_version")
        row = cursor.fetchone()
        self.assertEqual(row[0], 1)

