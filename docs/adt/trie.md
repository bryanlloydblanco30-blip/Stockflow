# ADT Specification: Trie

**Module**: `backend/ds/trie.py`
**Target Role**: Product name search and instant autocomplete.

## Operations & Guarantees
- `insert(word, value)`: Inserts lowercased word in $O(L)$ where $L$ is word length.
- `find_prefix(prefix)`: Traverses prefix in $O(p)$ where $p$ is prefix length.
- `list_under_prefix(prefix, limit=8)`: Collects up to 8 matching items beneath node in $O(p + k)$.
- `delete(word)`: Unmarks word and prunes dangling nodes.

## Rules & Constraints
- Case-insensitive (normalizes to lowercase).

