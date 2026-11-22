# StockFlow Progress Log

## Task 0.1 / Task 0.2: Complete Scaffolding of Project File Tree & Requirements
- **Date**: 07 Nov 2026
- **What Changed**:
  - Generated the complete architectural file tree matching all project documentation (Docs 4.5, 6, 7, 8, 10, 11, 12, 17, and CHANGES_v2.1):
    - `backend/`: `ds/` (8 data structures), `models/` (7 models), `db/` (connection, schema, storage, backup), `services/` (9 domain services).
    - `frontend/`: `components/` (6 reusable widgets), `screens/` (16 desktop screens), `app.py`.
    - `docs/`: `decisions_log.md` (D1-D17), `assumptions_log.md`, `later_list.md`, `CHANGES_v2.1.md`, and all 8 ADT contracts in `docs/adt/`.
    - `design/`: `tokens.py` (WCAG AA color palette & sizes), `microcopy.md`.
    - `benchmarks/`: `baselines.py`, benchmarks B1 through B6, results directory.
    - `data/`: `generator.py`, `fixtures.py`.
    - `tests/`: 11 test modules covering data structures, persistence, services, and the 16 edge cases.
    - Root: `main.py`, `requirements.txt` (pinned flet, pytest, faker).
- **Tests Added & Result**:
  - Ran `python -m unittest discover tests`: 13 test suites passed (100% OK in 0.022s).
- **Rules / Edge Cases Covered**:
  - Full codebase skeleton strictly adheres to frontend/backend isolation and no UI imports in backend.
  - Pinned dependency file written with zero unapproved additions.
- **Anything Left Open**:
  - Proceed with packaging verification (Task 0.5) and Phase 1 data structures implementation.


## Task 1.1: Doubly Linked List Implementation
- **Date**: 23 Nov 2026
- **What Changed**:
  - `backend/ds/linked_list.py`: Implemented from-scratch doubly linked list (`Node`, `add_front`, `add_end`, `find`, `remove`, `traverse`, `size`, `is_empty`) with zero built-in list storage shortcuts.
  - `tests/test_ds_linked_list.py`: Added 12 comprehensive unit test cases covering empty list, single item, ordering, predicate find, removal cases (head, tail, middle, duplicate, non-existent), and 500-step randomized operations verified against a trusted oracle list.
- **Tests Added & Result**:
  - 12 new unit tests in `tests/test_ds_linked_list.py`. Full test suite: 24/24 passed in 0.44s.
- **Rules / Edge Cases Covered**:
  - Doc 12.1 ADT testing requirements (empty, single item, duplicates, deletion cases, large random input checked against trusted result).
  - Pure Python, zero `heapq`/`dict`/`sorted` used in `ds/`.
- **Anything Left Open**:
  - Proceed to Task 1.2: Stack implementation.

## Task 1.2: Stack Implementation
- **Date**: 23 Nov 2026
- **What Changed**:
  - `backend/ds/stack.py`: Implemented node-based LIFO stack (`StackNode`, `push`, `pop`, `peek`, `size`, `is_empty`) with zero built-in list shortcuts.
  - `tests/test_ds_stack.py`: Added 5 unit test cases covering empty stack errors (IndexError on pop/peek), single item lifecycle, strict LIFO order across multiple items, duplicates handling, and 500-step randomized push/pop sequence verified against trusted Python list.
- **Tests Added & Result**:
  - 5 new unit tests in `tests/test_ds_stack.py`. Full test suite: 28/28 passed in 0.45s.
- **Rules / Edge Cases Covered**:
  - Doc 12.1 ADT testing requirements (empty, single, duplicates, random against oracle).
  - Pure node-based implementation with zero `heapq`/`dict`/`sorted`.
- **Anything Left Open**:
  - Proceed to Task 1.3: Min-heap implementation.

## Task 1.3: Min-Heap Implementation
- **Date**: 23 Nov 2026
- **What Changed**:
  - `backend/ds/min_heap.py`: Implemented strictly from scratch Min-Heap (`_HeapEntry`, `insert`, `peek_min`, `extract_min`, `remove_specific`, `ordered_read`, `size`, `is_empty`) with $O(\log n)$ sift up/down, $O(n)$ search + $O(\log n)$ repair for remove_specific, and non-destructive ordered traversal. Zero `heapq` imported.
  - `tests/test_ds_heaps.py`: Added 6 unit tests covering empty heap errors, single item, compound key with tie-break comparison, non-destructive `ordered_read`, `remove_specific` (root, leaf, internal, non-existent), and 200-item randomized validation against sorted oracle.
- **Tests Added & Result**:
  - 6 new unit tests in `tests/test_ds_heaps.py`. Full test suite: 34/34 passed in 0.45s.
- **Rules / Edge Cases Covered**:
  - Doc 12.1 ADT testing requirements (empty, single, duplicates, deletion, randomized validation against trusted result, tie-breaks).
  - Hard rule: zero `heapq` in `ds/`.
- **Anything Left Open**:
  - Proceed to Task 1.4: Max-Heap implementation.

## Task 1.4: Max-Heap Implementation
- **Date**: 23 Nov 2026
- **What Changed**:
  - `backend/ds/max_heap.py`: Implemented strictly from scratch Max-Heap (`_MaxHeapEntry`, `insert`, `peek_max`, `extract_max`, `size`, `is_empty`) with $O(\log n)$ sift up/down and $O(1)$ peek for restock urgency ranking. Zero `heapq` imported.
  - `tests/test_ds_heaps.py`: Added `TestMaxHeap` suite with 5 unit tests covering empty heap errors (IndexError on peek/extract), single item, priority ordering, duplicate priorities, and 200-item randomized validation against reverse-sorted oracle.
- **Tests Added & Result**:
  - 5 new unit tests in `tests/test_ds_heaps.py`. Full test suite: 38/38 passed in 0.46s.
- **Rules / Edge Cases Covered**:
  - Doc 12.1 ADT testing requirements (empty, single, duplicates, randomized validation).
  - Hard rule: zero `heapq` in `ds/`.
- **Anything Left Open**:
  - Proceed to Task 1.5: BST implementation.
