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

## Task 1.5: Binary Search Tree (BST) Implementation
- **Date**: 23 Nov 2026
- **What Changed**:
  - `backend/ds/bst.py`: Implemented from-scratch Binary Search Tree (`BSTNode`, `insert`, `find`, `delete`, `in_order`, `min`, `max`, `size`, `is_empty`) with duplicate key rejection and all 3 deletion cases (leaf, single child left/right, and two children with in-order successor replacement). Zero dict shortcuts used for lookup.
  - `tests/test_ds_trees.py`: Added 10 unit test cases covering empty BST, single node lifecycle, duplicate key rejection (ValueError), min/max, in-order ordering, all deletion cases, and 200-node randomized insertion/deletion verified against Python dict oracle.
- **Tests Added & Result**:
  - 10 new unit tests in `tests/test_ds_trees.py`. Full test suite: 48/48 passed in 0.47s.
- **Rules / Edge Cases Covered**:
  - Doc 12.1 ADT testing requirements (empty, single, duplicates, leaf/1-child/2-child deletion, random input checked against trusted result).
  - Hard rule: zero `dict` lookup shortcuts in `ds/`.
- **Anything Left Open**:
  - Proceed to Task 1.6: Trie implementation.

## Task 1.6: Trie Implementation
- **Date**: 23 Nov 2026
- **What Changed**:
  - `backend/ds/trie.py`: Implemented strictly from scratch prefix Trie (`TrieNode`, `insert`, `find_prefix`, `list_under_prefix`, `delete`) with lowercase normalization, depth-first collection with configurable limit (default 8), and recursive node pruning on deletion. Node children stored in a list of `(char, TrieNode)` pairs with zero dict shortcuts.
  - `tests/test_ds_trees.py`: Added 5 unit tests covering empty trie, single word insert/find/delete, case insensitivity, prefix listing limit (8), overlapping prefixes deletion, and randomized prefix validation against Python string filtering.
- **Tests Added & Result**:
  - 5 new unit tests in `tests/test_ds_trees.py`. Full test suite: 52/52 passed in 0.52s.
- **Rules / Edge Cases Covered**:
  - Doc 12.1 ADT testing requirements (empty, single, prefix match, limit 8, deletion, random oracle).
  - Hard rule: zero `dict` shortcuts for trie lookup.
- **Anything Left Open**:
  - Proceed to Task 1.7: Prefix Sums implementation.

## Task 1.7: Prefix Sums Implementation
- **Date**: 23 Nov 2026
- **What Changed**:
  - `backend/ds/prefix_sums.py`: Implemented from-scratch Prefix Sums array (`build`, `range_sum`, `size`, `is_empty`) providing $O(n)$ construction and $O(1)$ range sum queries for date-range financial reporting.
  - `tests/test_ds_prefix_topk.py`: Added 5 unit tests covering empty array, single element, full/sub/single range queries, index bounds validation, and 100-step randomized queries verified against Python `sum()`.
- **Tests Added & Result**:
  - 5 new unit tests in `tests/test_ds_prefix_topk.py`.
- **Rules / Edge Cases Covered**:
  - Doc 12.1 ADT requirements. Zero built-ins in `ds/`.

## Task 1.8: Size-k Heap Routine Implementation & Phase 1 Exit Gate Passed
- **Date**: 23 Nov 2026
- **What Changed**:
  - `backend/ds/size_k_heap.py`: Implemented from-scratch Size-k Heap routine supporting bounded $O(n \log k)$ top-k (using MinHeap) and bottom-k (using MaxHeap) rankings without full list sorting or built-in shortcuts.
  - `tests/test_ds_prefix_topk.py`: Added 5 unit tests covering top-k ($< k$, $= k$, $> k$), bottom-k, duplicate scores, and 500-element randomized streams verified against trusted sort oracle.
- **Tests Added & Result**:
  - Total 61/61 unit tests passing across all 8 data structures and project layout in 0.50s.
- **Phase 1 Exit Gate**:
  - All 8 data structures implemented from scratch. Every ADT document in `docs/adt/` fulfilled.
  - Zero imports of `heapq`, `sorted`, or `dict` lookup shortcuts in `backend/ds/`.
- **Anything Left Open**:
  - Phase 1 complete. Proceed to Phase 2: Models and Storage.

## Phase 2: Models and SQLite Storage Engine (Tasks 2.1 – 2.5) & Exit Gate Passed
- **Date**: 23 Nov 2026
- **What Changed**:
  - `backend/db/storage.py`: Implemented `StoreMemoryState`, `load_all_into_memory()`, `save_category()`, `save_product()`, `save_batch()`, and atomic sale persistence `save_transaction_atomic()`.
    - Automatically builds custom in-memory indices upon load:
      - `BST`: Barcode -> Product mapping without dict shortcuts.
      - `Trie`: Lowercase product name prefix search.
      - `MinHeap`: Per-product FEFO priority queue (earliest expiry first; received_date tie-break / key for untracked).
      - Plain dynamic array for categories (Decision D13).
    - `save_transaction_atomic()`: Enforces single SQLite unit-of-work with atomic rollback and simultaneous batch quantity deductions.
  - `backend/db/schema.py`: Stamped schema version and initialized default location (Main Store) with foreign keys enabled.
  - `tests/test_models_storage.py`: Implemented comprehensive test suite covering schema init, category/product persistence, load into in-memory structures, atomic sale commit, rollback on constraint violation, and save-then-load consistency.
- **Tests Added & Result**:
  - 5 comprehensive tests added in `tests/test_models_storage.py`.
  - Full test suite: 66/66 passed (100% OK in 0.30s).
- **Rules / Edge Cases Covered**:
  - Phase 2 exit gate: Close and reopen gives identical state; atomic sale test passes; zero banned built-ins in `backend/db/storage.py`.
- **Anything Left Open**:
  - Phase 2 complete. Proceed to Phase 3: Products, Categories, Inventory, and Alert Services.

## Phase 3: Products, Categories, Inventory, Alerts (Tasks 3.1 – 3.9) & Exit Gate Passed
- **Date**: 23 Nov 2026
- **What Changed**:
  - `backend/services/category_service.py`: Implemented add, rename, delete (moves products to Uncategorized with count), toggle tracking (flags 'Expiry date needed' on No -> Yes without guessing dates), dynamic red days (1/3 of warn_days, min 1), and 7-day default window for uncategorized products.
  - `backend/services/product_service.py`: Implemented product registration, editing, soft delete (active=0, pruning from indices), BST barcode search, and Trie lowercase prefix autocomplete (limit 8).
  - `backend/services/alert_service.py`: Implemented dynamic alert level calculation (`EXPIRED`, `RED`, `AMBER`, `OK`, `NO_EXPIRY`) from date without storing in DB (D9). Added `is_sellable()` (expiry today is Red and sellable; expired is blocked from sale, D10) and Min-Heap ordered scan optimization (stops at first batch outside window, Doc 6.3).
  - `backend/services/inventory_service.py`: Implemented batch receiving with older-stock warning (IN-5), shelf-rotation flag `moved_to_front` (IN-6), expired write-off logging in PHP (IN-7), physical stock adjustments with mandatory audit reasons (IN-8), and unresolved expiry batch flagging (Task 3.9).
  - `tests/test_services_inventory.py`: Added 8 tests covering category CRUD, product search/deletion, alert levels, older-stock warnings, shelf rotation, write-offs, and stock adjustments.
  - `tests/test_edge_cases.py`: Implemented and verified Edge Cases 1–6 and 10–12 from Doc 12.2.
- **Tests Added & Result**:
  - 15 new unit tests added across `tests/test_services_inventory.py` and `tests/test_edge_cases.py`.
  - Full test suite: 81/81 passed (100% OK in 0.39s).
- **Rules / Edge Cases Covered**:
  - Edge Case 1: Batch expires today -> Red, sellable.
  - Edge Case 2: Batch expired yesterday -> Expired, not sellable.
  - Edge Case 3: Exactly at amber window -> Amber.
  - Edge Case 4: One day past amber window -> OK.
  - Edge Case 5: Empty expiry in no-expiry category -> Never in alerts, ordered by received date.
  - Edge Case 6: Category switched to tracking -> Flagged 'Expiry date needed', not guessed.
  - Edge Case 10: Same expiry on two batches -> Earlier received sells first.
  - Edge Case 11: Product with no category -> Global default 7 days.
  - Edge Case 12: Category deleted -> Products move to Uncategorized.
- **Phase 3 Exit Gate**:
  - Entire stock lifecycle runs from tests with no UI. All Doc 12.2 Phase 3 edge cases pass. Zero banned built-ins in `services/`.
- **Anything Left Open**:
  - Phase 3 complete. Proceed to Phase 4: Point of Sale, FEFO Engine, Receipt Data, and Undo (Tasks 4.1 – 4.9).

## Phase 4: Point of Sale, FEFO Deduction, Receipt Formatting, and Undo (Tasks 4.1 – 4.9) & Exit Gate Passed
- **Date**: 23 Nov 2026
- **What Changed**:
  - `backend/services/fefo_service.py`: Implemented FEFO deduction engine:
    - Pre-deduction check: validates total sellable stock and blocks sales if only expired stock remains (D10 / Edge Case 8).
    - Multi-batch deduction: extracts batches from Min-Heap, skips un-sellable/expired batches (preserving them for alerts/write-offs), deducts from front batch, spans to subsequent batches (Edge Case 7), and re-inserts partially depleted batches.
    - Untracked batches handled via FIFO with `received_date` priority (D8).
  - `backend/services/pos_service.py`: Implemented POS service and cart:
    - Cart implemented strictly on custom `Doubly LinkedList` (Task 4.2 / Doc 6.6) with O(1) operations, automatic line merging, quantity editing, removal, and traversal total.
    - Unified barcode entry `process_barcode_entry()` resolving known barcodes via custom BST and flagging unknown barcodes as `UNKNOWN` to guide product registration (Tasks 4.1 & 4.9 / Doc 9.4).
    - Checkout cash validation: verifies cash given >= total, calculates change in PHP, and rejects underpayment (Task 4.3 / Edge Case 14).
    - End-to-end receipt formatting: generates itemized receipt breakdown directly from cart traversal (Task 4.5 / POS-6).
    - RS-1 Low-stock notification: scans post-checkout sellable stock against reorder levels (Task 4.8).
  - `backend/services/undo_service.py`: Implemented single-level Undo via custom `Stack` (Task 4.7 / Doc 6.7 / Decision D2):
    - Validates stack state and checks SQLite to block undo if any newer transaction has occurred (Doc 6.7 / Edge Case 15).
    - Restores exact batch quantities to SQLite and re-inserts exhausted batches into the product's in-memory Min-Heap.
    - Creates an auditable `void` transaction header referencing `reverses_id`.
  - `tests/test_services_pos_fefo.py`: Comprehensive test suite for unified barcode entry, cart linked list, multi-batch FEFO deduction, cash checkout, mixed cart, and low-stock checks.
  - `tests/test_services_undo.py`: Test suite for single-level undo, exact batch restoration, and rejection if newer transactions exist.
  - `tests/test_edge_cases.py`: Added tests covering Edge Case 13 (historical prices frozen on transaction lines despite catalog price changes), Edge Case 15 (void blocked on newer transaction), and Edge Case 16 (atomic rollback on database write failure).
- **Tests Added & Result**:
  - 11 new unit tests added across `tests/test_services_pos_fefo.py`, `tests/test_services_undo.py`, and `tests/test_edge_cases.py`.
  - Full test suite: 92/92 passed (100% OK in 0.37s).
- **Rules / Edge Cases Covered**:
  - Edge Case 7: Spanning multiple batches during FEFO deduction.
  - Edge Case 8: Sale blocked when only expired stock remains.
  - Edge Case 9: Cart with mixed tracked and no-expiry items.
  - Edge Case 13: Price change after sale leaves historical transactions unchanged.
  - Edge Case 14: Insufficient cash payment blocked.
  - Edge Case 15: Undo blocked if newer transaction exists.
  - Edge Case 16: Interrupted transaction leaves no partial sale (atomic sale rollback).
- **Phase 4 Exit Gate**:
  - Full sale (single batch, multi-batch spanning, mixed cart) works end-to-end with no UI.
  - Edge cases 7 to 9, 13 to 16 pass 100%.
  - Zero imports of `heapq`, `dict`, or `sorted` in `backend/ds/` or `backend/services/`.
- **Anything Left Open**:
  - Phase 4 complete. Proceed to Phase 5: Restock Priority Queue and Financial Reporting (Tasks 5.1 – 5.7).

