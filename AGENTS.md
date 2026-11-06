# StockFlow: Agent Workflow Guide (v2.1, PC first)

Put this file in the repository root. It tells an AI coding agent what to build, in what order, how to check its own work, and when to stop and ask a human.

**Source of truth**: `Documents/StockFlow_Project_Documentation_v2.pdf` plus `docs/CHANGES_v2.1.md` (platform change to PC first). Section numbers below (for example "Doc 6.3") refer to the PDF. Keep both in `docs/` of the repo once initialized. Where the PDF says Android, APK or phone, `CHANGES_v2.1.md` wins.

---

## 1. Mission

Build StockFlow: an offline desktop (PC first) inventory, point-of-sale and reporting app for small stores. Python 3, Flet UI, SQLite storage. Android is an optional later extra. Every major feature runs on a data structure written from scratch and is benchmarked against a naive method.

Two things are graded and must never be traded away for speed or polish:
1. The from-scratch data structures with their tests.
2. The benchmark results against naive baselines.

---

## 2. Source-of-Truth Order

When two sources disagree, the higher one wins:
1. A written instruction from the human in the current session.
2. `docs/CHANGES_v2.1.md` (platform decisions D15 to D17).
3. Decisions register (Doc 3) and business rules (Doc 6).
4. Requirements (Doc 5) and data model (Doc 8).
5. Design guide (Doc 11, as adapted for desktop in `CHANGES_v2.1`) and designers' specs in `design/`.
6. This file (`AGENTS.md`).
7. Your own judgement. Anything you decide here goes into `docs/assumptions_log.md`.

---

## 3. Hard Rules (Never Break)

### Structure
- **Frontend / Backend Separation**:
  - `frontend/` (Flet UI screens & components) calls `backend/services/`, which calls `backend/ds/`, `backend/models/`, `backend/db/`. A layer never calls upward. No business rule lives in `frontend/`.
  - `backend/` (`ds/`, `services/`, `db/`, `models/`) contains **no Flet imports**. It must run under pytest with no UI.
  - `backend/` is **platform neutral**: no Windows-only or Android-only calls. The database file location comes from one function in `backend/db/` so each platform can choose its own folder (D17).

### Data Structures
- Linked list, min-heap, max-heap, BST, trie, stack, prefix sums and the size-k heap are **written from scratch** in `ds/`.
- `heapq`, `dict` and `sorted` are allowed **only inside `benchmarks/`** as the naive baseline. **Not in `ds/`, not in `services/`.**
- Category list uses a plain dynamic array (D13).

### Business Rules
- Expired batches are never sold (D10).
- FEFO per product, one min-heap per product (D3). No-expiry products use the same heap with received date as the key (D8).
- Price and cost are stored on each sale line at the time of sale. Old reports never change.
- Alert level is calculated from the date when needed. It is never stored (D9).
- Undo reverses only the most recent transaction, one level (D2).
- Core is single-location. Every product, batch and transaction still carries a location id (D1).
- Payment is cash only. No tax, cards or e-wallets.
- Money is PHP, shown as `PHP 1,250.00`. Dates are shown as `12 Nov 2026`.

### Project
- Primary target is a desktop PC (Windows assumed, D15). Android is optional and comes after the release (D16).
- Pin the Flet version in `requirements.txt`. Never upgrade it without human approval.
- Barcode input goes through one barcode entry function. A USB or Bluetooth scanner (types like a keyboard), typed entry, webcam and simulate-scan all call it. The simulate-scan button must always work.
- Do not add heavy native libraries (OpenCV, Matplotlib).
- Never invent data that looks real. Sample data is labelled as sample.

---

## 4. Workflow Map

### 4.1 Phase Map
```text
Phase 0 Foundations: tiny desktop app runs on the target PC, packaged build works
-> Phase 1 Data structures: ADT spec, tests, code
-> Phase 2 Models and SQLite
-> Phase 3 Products, categories, inventory, alerts
-> Phase 4 POS, FEFO, receipt, undo
-> Phase 5 Restock and reports
-> Phase 6 Sample data and benchmarks
-> FEATURE FREEZE (new ideas go to docs/later_list.md)
-> Phase 7 Flet desktop UI, backup, scanner/webcam test (needs designer specs)
-> Phase 8 Release: packaged desktop app and demo
-> Optional later: Android build (docs/later_list.md)
HUMAN gates (target-PC tests, decisions, usability test) block Phases 0, 7 and 8.
```

Phases 1 to 6 are the complete graded project. Do not start Phase 7 before the freeze.

### 4.2 The Loop for Every Task
1. **Read requirement and rules**: Check specific docs, ADT requirements, and edge cases.
2. **Check open questions**: If blocked, ask the human (Section 7).
3. **Plan**: Identify target files, tests to write, and risks.
4. **Write tests first**: Tests come before code for anything in `ds/` and `services/`.
5. **Implement the smallest change**: Write pure, clean code fulfilling the test.
6. **Run all tests**: Run `pytest`. If any fail, go back to step 5.
7. **Self-review against the hard rules**: Confirm no layer violations, no banned built-ins (`heapq`, `dict`, `sorted`) in `ds/` or `services/`.
8. **Autonomous Memory & Progress Logging**:
   - Add task entry to `docs/progress_log.md` (Section 9).
   - **Autonomously update `MEMORY.md` via script**:
     ```bash
     python scripts/update_memory.py --finish "<Task Completed>" --next "<Next Task>" --tests "<Test Status>"
     ```
9. **Commit**: One task per commit, with a one-line message saying what and why.

#### Rules for the loop:
- One task at a time. One commit per task, with a one-line message saying what and why.
- Tests come before code for anything in `ds/` and `services/`.
- A task is not done until the full test suite passes, not just the new tests.
- If a fix needs more than two failed attempts, stop and report (Section 8).

---

## 5. Phase Details

Each phase lists entry condition, ordered tasks, files, and the exit gate. Do not leave a phase until its gate passes.

### Phase 0: Foundations
**Entry**: empty repo.

| # Task | Output |
| :--- | :--- |
| **0.1** Create the folder layout from Doc 4.5, plus `docs/` and `design/`. | Empty packages with `__init__` files |
| **0.2** Write `requirements.txt` with the Flet version pinned, plus `pytest` and `Faker`. | Pinned file |
| **0.3** Create a minimal Flet app that shows one screen. Run it with `flet run main.py`. | `main.py` |
| **0.4** Create `docs/progress_log.md`, `docs/assumptions_log.md`, `docs/decisions_log.md`. Copy D15 to D17 into the decisions log. | Three logs |
| **0.5** Package the tiny app for desktop (`flet pack` or `flet build windows`, whichever works with the pinned Flet). | Executable or folder |
| **0.6** HUMAN: run the packaged app on the target PC and confirm it opens. | Confirmation |

**Exit gate**: The tiny packaged app runs on the target PC. If the packaging fails twice, stop and report.

---

### Phase 1: Data Structures
**Entry**: Phase 0 gate passed.

Build in this order. For each one, first write `docs/adt/<name>.md` (operations and what each promises), then tests, then code.

| # Structure | Must Support | Notes |
| :--- | :--- | :--- |
| **1.1 Linked list** | add front, add end, find, remove, traverse, size, is empty | Used by cart, batches, log |
| **1.2 Stack** | push, pop, peek, size, is empty | Used by undo |
| **1.3 Min-heap** | insert, peek, extract, size, ordered read without destroying the heap, remove a specific item | Takes a key and a tie-break. Ordered read is needed for alert scan. Remove-specific is needed for undoing a receive. |
| **1.4 Max-heap** | insert, peek, extract, size | Restock priority queue |
| **1.5 BST** | insert, find, delete (leaf, one child, two children), in-order, min, max | Barcode lookup. Reject duplicate keys. |
| **1.6 Trie** | insert, prefix find, list under prefix (limit 8), delete | Lowercase names |
| **1.7 Prefix sums** | build, range sum | Revenue, units, COGS per day |
| **1.8 Size-k heap routine** | feed values, keep k best or worst, ranked output | Top-k and bottom-k |

**Tests required (Doc 12.1)**: empty structure, single item, duplicates, deletion cases, large random input checked against a trusted result, tie-breaks.
**Exit gate**: All structure tests pass. Every structure has an ADT file. Nothing in `ds/` imports `heapq`, dict-based lookup shortcuts for the structure's core job, or `sorted`.

---

### Phase 2: Models and Storage
**Entry**: Phase 1 gate passed.

| # Task | Description |
| :--- | :--- |
| **2.1** | Models: `Category`, `Product`, `Batch`, `Transaction`, `TransactionLine`, `Settings`, `Location` (Doc 8.1). |
| **2.2** | SQLite schema with a database version number. Database path comes from one function (D17). |
| **2.3** | Load: read categories, products, batches, then build the BST, trie and each product's heap. |
| **2.4** | Save: write each change right after it succeeds in memory. A sale is written as one unit. |
| **2.5** | Tests: save then load gives identical data; interrupted write leaves no half-saved sale. |

**Exit gate**: Close and reopen gives the same state. Atomic-sale test passes.

---

### Phase 3: Products, Categories, Inventory, Alerts
**Entry**: Phase 2 gate passed. Requirements PM-1 to PM-6, IN-1 to IN-8.

| # Task | Description | Rules to read first |
| :--- | :--- | :--- |
| **3.1** | Category service: add, rename, delete, tracks-expiry, warning days, red days (calculated) | Doc 6.3, 6.4 |
| **3.2** | Product service: register, edit, soft delete, barcode search (BST), name search (trie), sort | Doc 6.1 |
| **3.3** | Receive stock: add batch, validate, hide expiry for no-expiry categories | Doc 6.2 |
| **3.4** | Older-stock message data: return older batches (date, units, level) when a new batch is received | IN-5 |
| **3.5** | Alert service: levels Expired, Red, Amber, OK, No expiry. Scan stops at first batch outside the window. | Doc 6.3 |
| **3.6** | Shelf-rotation list and moved-to-front flag | IN-6 |
| **3.7** | Write-off: remove expired batch, record loss | IN-7 |
| **3.8** | Stock adjustment with reason and old/new count | IN-8 |
| **3.9** | Category switch handling: No to Yes flags 'Expiry date needed'; Yes to No keeps dates but ignores them | Doc 6.4 |

**Exit gate**: The whole stock lifecycle runs from tests with no UI. All edge cases 1 to 6, 10 to 12 in Doc 12.2 pass.

---

### Phase 4: Point of Sale
**Entry**: Phase 3 gate passed. Requirements POS-1 to POS-7, TL-1 to TL-3.

| # Task | Description | Rules to read first |
| :--- | :--- | :--- |
| **4.1** | One barcode entry function. USB scanner, typed entry, webcam and simulate-scan all call it. | Doc 4.3, D17 |
| **4.2** | Cart on a linked list: add (merge same product), change quantity, remove | Doc 6.6 |
| **4.3** | Checkout: total, cash check, change | Doc 6.6 |
| **4.4** | Deduct stock: FEFO or FIFO per item, skip expired, span batches, record batch and quantity on each sale line | Doc 6.2 |
| **4.5** | Receipt data from the cart traversal | POS-6 |
| **4.6** | Transaction log (all types) | TL-1, TL-2 |
| **4.7** | Undo with the stack: restore to the same batches, log a void, block when a newer transaction exists | Doc 6.7 |
| **4.8** | Low-stock check after each sale | RS-1 |
| **4.9** | Unknown barcode result that the UI can turn into 'Register product' | Doc 9.4 |

**Exit gate**: A full sale, including one that spans two batches and one mixed cart, works end to end with no UI. Edge cases 7 to 9, 13 to 16 pass.

---

### Phase 5: Restock and Reports
**Entry**: Phase 4 gate passed. Requirements RS-2 to RS-4, RP-1 to RP-8.

| # Task | Description | Rules to read first |
| :--- | :--- | :--- |
| **5.1** | Selling speed (14-day average), days of cover | Doc 6.8 |
| **5.2** | Restock queue on the max-heap, reason text per row | Doc 6.8 |
| **5.3** | Suggested reorder quantity, never below zero | Doc 6.8 |
| **5.4** | Top-k and bottom-k sellers with the size-k heap | Doc 10.1 |
| **5.5** | Daily totals and prefix sums for revenue, units, COGS | Doc 7.3 C |
| **5.6** | Reports: revenue, COGS, gross profit, margin, spoilage, inventory value, profit per item | Doc 10 |
| **5.7** | Dashboard numbers: today's sales, profit, low-stock count, near-expiry count (tracked products only) | RP-8 |

**Exit gate**: Report numbers equal hand-calculated values on a small fixed data set. Voided sales are excluded from totals.

---

### Phase 6: Sample Data and Benchmarks
**Entry**: Phase 5 gate passed.

| # Task | Description | Rules |
| :--- | :--- | :--- |
| **6.1** | Generator with a fixed seed. 30 to 100 products, 6 to 8 categories, 20 to 30 percent no-expiry, 30 to 90 days of sales. | Doc 8.3 |
| **6.2** | Benchmarks B1 to B6 | Doc 12.3 |
| **6.3** | Results table and one chart per benchmark, saved in `benchmarks/results/` | Doc 12.3 |

**Benchmark protocol**:
- Use `time.perf_counter()`. Warm up first. Repeat at least 30 times. Report median, minimum and maximum.
- Same machine and data. Record machine and Python version.
- B3 and B4 use identical simulated sales for both methods (tracked products only for B3).
- Include the BST sorted-insertion worst case in B1.
- Report results honestly, including cases where naive method wins.

**Exit gate**: All six benchmarks have saved results. **Feature freeze**: after this gate, new ideas go to `docs/later_list.md`, not into the build.

---

### Phase 7: Desktop UI
**Entry**: Feature freeze in place. Designers' desktop specs exist in `design/` (or follow Doc 11.4 as adapted in `CHANGES_v2.1`).

| # Task | Description | Rules |
| :--- | :--- | :--- |
| **7.1** | Design tokens and shared components built once (Colors, type, spacing, status badge, list row, chip, stepper, snackbar, confirm dialog) | Doc 11.3, sizes adapted for desktop |
| **7.2** | Navigation: side navigation rail with Home, Sell, Stock, Restock, Reports. More menu for history, shelf rotation, backup, settings. | CHANGES_v2.1 |
| **7.3** | Screens in this order: Sell, Checkout, Receipt, Stock list, Product detail, Receive stock, Register product, Home, Near-expiry list, Checklist, Write-off list, Restock, Reports, History, Settings, Backup | Doc 11.4 |
| **7.4** | Every screen handles empty, loading, error and success states | Doc 11.5 |
| **7.5** | Keyboard support: Enter confirms, Esc cancels, Tab order follows visual order, shortcut to focus barcode field | CHANGES_v2.1 |
| **7.6** | Export, restore, backup reminder (file picker for backup location) | Doc 9.6 |
| **7.7** | HUMAN: scanner test on target PC (USB scanner and, if available, webcam) | Doc 4.3 |
| **7.8** | HUMAN: usability test with 2 or 3 outsiders | Doc 12.4 |

**UI rules**:
- The UI only displays data from services and sends user actions to them. If a screen needs a rule, add it to `services/` first.
- Use exact wording from the designers' microcopy sheet. Do not invent text.
- Status always shows icon, word and color together.
- Click targets stay generous ($\ge 40$ px). Lists show 5 to 7 rows then "See all", or scrollable table. One primary button per screen.
- Window must resize without breaking. Minimum window size set in one place.
- If a design cannot be built with standard Flet controls, stop and report. Do not build custom controls without approval.

**Exit gate**: All screens exist with all states. Contrast, keyboard-only and font-scaling checks done. Usability test round complete.

---

### Phase 8: Release
| # Task | Description |
| :--- | :--- |
| **8.1** | Fresh-clone test: install and run from pinned `requirements.txt`. |
| **8.2** | Re-run all tests and all benchmarks on the final code. |
| **8.3** | Build final packaged desktop app. HUMAN: run it on demo PC from a cold start. |
| **8.4** | Walk Release Checklist (Doc Appendix A, adapted in `CHANGES_v2.1`). |
| **8.5** | Update README, decisions log and documentation to match what was built. |

**Exit gate**: The demo runs on the demo PC using simulate-scan (or USB scanner if available). Webcam is a bonus.

---

### Optional Later: Android
Not part of the graded build. Only after Phase 8, and only if the human asks. Tracked in `docs/later_list.md`: `flet build apk`, phone layout (bottom bar, portrait), touch-target review, camera scanner test on real phone.

---

## 6. Quick Rule Sheet

| Topic | Rule |
| :--- | :--- |
| **Alert levels** | Days left = expiry minus today. Below 0: Expired. 0 up to red limit: Red. Up to amber window: Amber. Above: OK. |
| **Red limit** | One-third of amber window, rounded, minimum 1 day. (3 gives 1, 5 gives 2, 7 gives 2, 14 gives 5, 30 gives 10). |
| **Expiry today** | Red and still sellable. Expired starts the next day. |
| **Window source** | Category warning days. No category: global default, 7 days. |
| **Deduction order**| Tracked: earliest expiry, tie then earlier received. No expiry: earliest received, tie then lower batch id. |
| **Deduction span** | Take what front batch has, then continue with next. Record every batch and quantity on sale line. |
| **Sellable stock** | Excludes expired batches. Low-stock checks use sellable stock. |
| **No-expiry products** | Never in alerts, checklist, write-off or spoilage. Included in value, revenue, COGS, profit, low-stock. |
| **Undo** | Latest transaction only. Blocked if newer transaction exists. Undo of receive refused if any units were sold. |
| **Reports** | Voided sales removed from all totals. Margin is 0% when revenue is 0. |
| **Restock rank** | Days of cover (lowest first), then selling speed (highest first), then expiry pressure. |
| **Reorder quantity** | Selling speed $\times$ target cover days (default 14) minus sellable stock, rounded up, never below zero. |

---

## 7. When to Ask the Human

Stop and ask if any of these happen. Do not guess:
1. Two documents disagree and the order in Section 2 does not settle it.
2. A requirement is missing, unclear or contradicts a business rule.
3. You need a new dependency.
4. You want to change the Flet version.
5. A design needs a custom control Flet cannot provide.
6. You want to change a data structure's role or use a built-in in `ds/`.
7. The same problem fails after two fix attempts.
8. Any step needs the target PC, a real person or a decision (marked HUMAN).
9. A change would delete or rewrite existing data or history.
10. The human asks to start the Android build.

**Proceed with defaults for open items (Doc 17)**:
- Target OS: Windows (D15).
- Android: Optional, after release (D16).
- Uncategorized products: Track expiry, 7-day window.
- Undo scope: One level, most recent only.
- Expired batches: Blocked from sale.
- Returns of older sales: Not supported. Use stock adjustment.
- Receipt: On-screen only.
- Restock formula: As in Doc 6.8.
- PIN lock, push notifications: Not built.
- Hash table benchmark: BST only.
- Deadline: 12-week template.

Write every default used into `docs/assumptions_log.md` with the date and task.

---

## 8. Stop-and-Report Format

When blocked, stop and write this and nothing more:
```text
Task: the task number
What I tried: the attempts, briefly
What failed: exact error or conflict in plain words
Options: two or three ways forward with a trade-off each
My recommendation: one option and why
What I need from you: one clear question
```

---

## 9. Reporting and Logs

After every task, add one entry to `docs/progress_log.md`:
- Task number and name
- What changed (files)
- Tests added and full-suite result
- Rules or edge cases covered (by Doc number)
- Assumptions made
- Anything left open

**Keep three logs current**:
- `docs/progress_log.md`: what was done.
- `docs/assumptions_log.md`: every default or guess, with date.
- `docs/decisions_log.md`: decisions confirmed by the human. Mirrors Doc 3 plus D15 to D17.

---

## 10. Dependency Map

| Needs | Before |
| :--- | :--- |
| Linked list, stack | Cart, transaction log, undo |
| Min-heap with ordered read and remove-specific | Alerts, FEFO, undo of a receive |
| BST | Barcode lookup, POS |
| Trie | Name search |
| Max-heap | Restock queue |
| Prefix sums, size-k heap | Reports, top-k |
| Category service | Alerts, receive stock, product form |
| Alert service | Near-expiry list, checklist, older-stock message, dashboard |
| Transaction lines with batch ids | Undo, spoilage report, COGS |
| Services complete (Phases 3 to 5) | Any UI work |
| Designers' desktop specs and tokens | Phase 7 screens |

---

## 11. Anti-Patterns (Do NOT Do These)
- Writing code before the ADT and tests exist for a data structure.
- Using `heapq`, `dict` or `sorted` in `ds/` or `services/` to save time.
- Putting a rule in a Flet screen because it was faster.
- Storing the alert level instead of calculating it.
- Selling from an expired batch, or from a batch not at the front of its order.
- Editing history to fix a mistake. Use an adjustment or a void instead.
- Guessing an expiry date when a category switches to tracking.
- Adding features after the freeze.
- Building a custom control, or adding a dependency, without approval.
- Putting OS-specific code or hard-coded file paths in `ds/`, `services/` or `db/`.
- Running a long task with no commit, no log entry and no test run.
- Marking a task done while any test fails.
- Reporting estimated benchmark numbers. Only measured ones.

---

## 12. Definition of Done
### Every task:
- Tests written first, and the full suite passes.
- Matches all business rules and hard rules.
- No layer violations. No built-ins in `ds/`.
- Logged in the progress log. One commit.
- `MEMORY.md` updated via `scripts/update_memory.py`.

### Every phase:
- Exit gate criteria all pass and a gate report is written.

### The project:
- Phases 1 to 6 complete with tests and benchmark results.
- All screens built with all states.
- Packaged desktop app runs on demo PC. Backup export works.
- Release Checklist complete. Documentation matches final app.
