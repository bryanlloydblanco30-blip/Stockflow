"""
backend/ds/trie.py
Trie written from scratch for product name prefix search and autocomplete.
Contract: docs/adt/trie.md
"""


class TrieNode:
    def __init__(self):
        self.children = []  # list of (char, TrieNode)
        self.is_terminal = False
        self.value = None


class Trie:
    def __init__(self):
        self.root = TrieNode()

    def insert(self, word: str, value) -> None:
        pass

    def find_prefix(self, prefix: str):
        pass

    def list_under_prefix(self, prefix: str, limit: int = 8):
        pass

    def delete(self, word: str) -> bool:
        pass

