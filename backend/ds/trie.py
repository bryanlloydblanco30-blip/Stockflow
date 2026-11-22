"""
backend/ds/trie.py
Trie written strictly from scratch.
Contract: docs/adt/trie.md
Used by: product name search and instant autocomplete (Doc 6.1, Task 1.6).
Children are stored in a simple list of (char, TrieNode) pairs without using dict shortcuts.
"""


class TrieNode:
    """Internal trie node tracking character children, terminal flag, and payload."""

    __slots__ = ("children", "is_terminal", "value")

    def __init__(self):
        self.children: list[tuple[str, "TrieNode"]] = []
        self.is_terminal = False
        self.value = None

    def get_child(self, char: str) -> "TrieNode | None":
        for c, node in self.children:
            if c == char:
                return node
        return None

    def add_child(self, char: str) -> "TrieNode":
        for c, node in self.children:
            if c == char:
                return node
        new_node = TrieNode()
        self.children.append((char, new_node))
        return new_node

    def remove_child(self, char: str) -> bool:
        for i, (c, _) in enumerate(self.children):
            if c == char:
                self.children.pop(i)
                return True
        return False


class Trie:
    """
    Prefix tree for fast string search and autocomplete.
    Normalizes all keys to lowercase.
    """

    def __init__(self):
        self.root = TrieNode()

    def insert(self, word: str, value) -> None:
        """Insert a word and associated payload in O(L) time."""
        curr = self.root
        for ch in word.lower():
            curr = curr.add_child(ch)
        curr.is_terminal = True
        curr.value = value

    def find_prefix(self, prefix: str) -> TrieNode | None:
        """Traverse to node matching prefix in O(p) time. Returns node or None."""
        curr = self.root
        for ch in prefix.lower():
            child = curr.get_child(ch)
            if child is None:
                return None
            curr = child
        return curr

    def list_under_prefix(self, prefix: str, limit: int = 8) -> list:
        """
        Collect up to `limit` matching item values beneath the prefix node.
        Uses depth-first traversal.
        """
        node = self.find_prefix(prefix)
        if node is None:
            return []

        results = []

        def _dfs(curr: TrieNode):
            if len(results) >= limit:
                return
            if curr.is_terminal:
                results.append(curr.value)
            for _, child in curr.children:
                if len(results) >= limit:
                    break
                _dfs(child)

        _dfs(node)
        return results

    def delete(self, word: str) -> bool:
        """
        Remove a word from the trie and prune dangling nodes.
        Returns True if the word was found and deleted, False otherwise.
        """
        clean_word = word.lower()

        def _delete_helper(curr: TrieNode, idx: int) -> tuple[bool, bool]:
            """
            Returns (deleted_flag, should_prune_child).
            """
            if idx == len(clean_word):
                if not curr.is_terminal:
                    return (False, False)
                curr.is_terminal = False
                curr.value = None
                # Should prune if curr has no other children
                return (True, len(curr.children) == 0)

            ch = clean_word[idx]
            child = curr.get_child(ch)
            if child is None:
                return (False, False)

            deleted, should_prune = _delete_helper(child, idx + 1)
            if should_prune and not child.is_terminal and len(child.children) == 0:
                curr.remove_child(ch)

            can_prune_curr = not curr.is_terminal and len(curr.children) == 0
            return (deleted, can_prune_curr)

        deleted, _ = _delete_helper(self.root, 0)
        return deleted
