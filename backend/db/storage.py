"""
backend/db/storage.py
Persistence engine: Loads entities into custom in-memory data structures on start,
and writes transactions and state updates atomically to SQLite (Tasks 2.3 & 2.4).
"""

from typing import Tuple


def load_all_into_memory(conn) -> Tuple:
    """
    Reads categories, products, and batches from SQLite.
    Populates BST, Trie, Min-Heaps, and category dynamic array.
    """
    pass


def save_transaction_atomic(conn, transaction, lines: list) -> None:
    """Writes a completed sale and its line items in a single atomic transaction."""
    pass

