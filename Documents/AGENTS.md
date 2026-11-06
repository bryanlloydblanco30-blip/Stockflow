## StockFlow: Agent Workflow Guide (v2.1, PC first)

Put this file in the repository root. It tells an AI coding agent what to build, in what order, how to check its own work, and when to stop and ask a human.

Source of truth: StockFlow Project Documentation v2.0 (PDF) plusdocs/CHANGES_v2.1.md (platform change to PC first). Section numbers below (for example "Doc 6.3") refer to the PDF. Keep both in docs/ of the repo. Where the PDF says Android, APK or phone, CHANGES_v2.1.md wins.

## 1. Mission

Build StockFlow: an offline desktop (PC first) inventory, point-of-sale and reporting app for small stores. Python 3, Flet UI, SQLite storage. Android is an optional later extra. Every major feature runs on a data structure written from scratch and is benchmarked against a naive method.

Two things are graded and must never be traded away for speed or polish:

- 1. The from-scratch data structures with their tests.

- 2. The benchmark results against naive baselines.

## 2. Source-of-truth order

When two sources disagree, the higher one wins.

- 1. A written instruction from the human in the current session.

- 2. docs/CHANGES_v2.1.md (platform decisions D15 to D17).

- 3. Decisions register (Doc 3) and business rules (Doc 6).

- 4. Requirements (Doc 5) and data model (Doc 8).

- 5. Design guide (Doc 11, as adapted for desktop in CHANGES_v2.1) and designers' specs in design/ .

- 6. This file.

- 7. Your own judgement. Anything you decide here goes into docs/assumptions_log.md .

## 3. Hard rules (never break)

## Structure

- Layers: ui/ calls services/ , which calls ds/ , models/ , db/ . A layer never calls upward. No business rule lives in ui/ .

- ds/ , services/ , db/ contain no Flet imports. They must run under pytest with no UI.

- ds/ , services/ , db/ are platform neutral: no Windows-only or Android-only calls. The database file location comes from one function in db/ so each platform can choose its own folder (D17).

## Data structures

- Linked list, min-heap, max-heap, BST, trie, stack, prefix sums and the size-k heap are written from scratch in ds/ .


- heapq , dict and sorted are allowed only inside benchmarks/ as the naive baseline. Not in ds/ , not in services/ .

- Category list uses a plain dynamic array (D13).

## Business rules

- Expired batches are never sold (D10).

- FEFO per product, one min-heap per product (D3). No-expiry products use the same heap with received date as the key (D8).

- Price and cost are stored on each sale line at the time of sale. Old reports never change.

- Alert level is calculated from the date when needed. It is never stored (D9).

- Undo reverses only the most recent transaction, one level (D2).

- Core is single-location. Every product, batch and transaction still carries a location id (D1).

- Payment is cash only. No tax, cards or e-wallets.

- Money is PHP, shown as PHP 1,250.00. Dates are shown as 12 Nov 2026.

## Project

- Primary target is a desktop PC (Windows assumed, D15). Android is optional and comes after the release (D16).

- Pin the Flet version in requirements.txt . Never upgrade it without human approval.

- Barcode input goes through one barcode entry function. A USB or Bluetooth scanner (types like a keyboard), typed entry, webcam and simulate-scan all call it. The simulate-scan button must always work.

- Do not add heavy native libraries (OpenCV, Matplotlib).

- Never invent data that looks real. Sample data is labelled as sample.

## 4. Workflow map

## 4.1 Phase map

```
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

## 4.2 The loop for every task

- 1. Read requirement and rules.

- 2. Check open questions. If blocked, ask the human (Section 7).

- 3. Plan: files, tests, risks.

- 4. Write tests first from rules and edge cases.

- 5. Implement the smallest change.

- 6. Run all tests. If they fail, go back to step 5.

- 7. Self-review against the hard rules.

- 8. Log and report (Section 9).

- 9. Commit, one task per commit.

## Rules for the loop:

- One task at a time. One commit per task, with a one-line message saying what and why.

- Tests come before code for anything in ds/ and services/ .

- A task is not done until the full test suite passes, not just the new tests.

- If a fix needs more than two failed attempts, stop and report (Section 8).

## 5. Phase details

Each phase lists entry condition, ordered tasks, files, and the exit gate. Do not leave a phase until its gate passes.

## Phase 0: Foundations

Entry: empty repo.


| # Task | Output |
| --- | --- |
| 0.1 Create the folder layout from Doc 4.5, plus docs/ and design/ . | Empty packages with |
|   | __init__ files |
| 0.2 Write requirements.txt | with the Flet version pinned, plus pytest and Pinned file |
| Faker. |   |
| 0.3 Create a minimal Flet app that shows one screen. Run it withflet run | main.py |
| main.py . |   |
| 0.4 Create docs/progress_log.md , docs/assumptions_log.md , | Three logs |
| docs/decisions_log.md . Copy D15 to D17 into the decisions log. |   |
| 0.5 Package the tiny app for desktop (flet pack or flet build windows , | Executable or folder |
| whichever works with the pinned Flet). |   |
| 0.6 HUMAN: run the packaged app on the target PC and confirm it opens. Confirmation |   |

Exit gate: the tiny packaged app runs on the target PC. If the packaging fails twice, stop and report.

## Phase 1: Data structures

Entry: Phase 0 gate passed.

Build in this order. For each one, first write docs/adt/<name>.md (operations and what each promises), then tests, then code.


| # Structure Must support | Notes |
| --- | --- |
| 1.1 Linked list add front, add end, find, remove, | Used by cart, batches, log |
| traverse, size, is empty |   |
| 1.2 Stack | push, pop, peek, size, is empty Used by undo |
| 1.3 Min-heap insert, peek, extract, size, ordered | Takes a key and a tie-break. Ordered read is |
| read without destroying the heap, | needed for the alert scan. Remove-specific is |
| remove a specific item | needed for undoing a receive. |
| 1.4 Max-heap insert, peek, extract, size | Restock priority queue |
| insert, find, delete (leaf, one child, 1.5 BST | Barcode lookup. Reject duplicate keys. |
| two children), in-order, min, max |   |
| 1.6 Trie | insert, prefix find, list under prefix Lowercase names |
| (limit 8), delete |   |
| 1.7 Prefix sums build, range sum | Revenue, units, COGS per day |
| 1.8 Size-k heap feed values, keep k best or worst, | Top-k and bottom-k |
| routine ranked output |   |

Tests required (Doc 12.1): empty structure, single item, duplicates, deletion cases, large random input checked against a trusted result, tie-breaks.

Exit gate: all structure tests pass. Every structure has an ADT file. Nothing in ds/ imports heapq , dict-based lookup shortcuts for the structure's core job, or sorted .

## Phase 2: Models and storage

Entry: Phase 1 gate passed.

| # Task |
| --- |
| 2.1 Models: Category, Product, Batch, Transaction, TransactionLine, Settings, Location (Doc 8.1). |
| 2.2 SQLite schema with a database version number. Database path comes from one function (D17). |
| 2.3 Load: read categories, products, batches, then build the BST, trie and each product's heap. |
| 2.4 Save: write each change right after it succeeds in memory. A sale is written as one unit. |
| 2.5 Tests: save then load gives identical data; interrupted write leaves no half-saved sale. |


Exit gate: close and reopen gives the same state. Atomic-sale test passes.

## Phase 3: Products, categories, inventory, alerts

Entry: Phase 2 gate passed. Requirements PM-1 to PM-6, IN-1 to IN-8.

| # Task | Rules to read |
| --- | --- |
|   | first |
| 3.1 Category service: add, rename, delete, tracks-expiry, warning days, red days | Doc 6.3, 6.4 |
| (calculated) |   |
| 3.2 Product service: register, edit, soft delete, barcode search (BST), name search | Doc 6.1 |
| (trie), sort |   |
| 3.3 Receive stock: add batch, validate, hide expiry for no-expiry categories | Doc 6.2 |
| 3.4 Older-stock message data: return older batches (date, units, level) when a new | IN-5 |
| batch is received |   |
| 3.5 Alert service: levels Expired, Red, Amber, OK, No expiry. Scan stops at first batch | Doc 6.3 |
| outside the window. |   |
| 3.6 Shelf-rotation list and moved-to-front flag | IN-6 |
| 3.7 Write-off: remove expired batch, record loss | IN-7 |
| 3.8 Stock adjustment with reason and old/new count | IN-8 |
| 3.9 Category switch handling: No to Yes flags 'Expiry date needed'; Yes to No keeps | Doc 6.4 |
| dates but ignores them |   |

Exit gate: the whole stock lifecycle runs from tests with no UI. All edge cases 1 to 6, 10 to 12 in Doc 12.2 pass.

## Phase 4: Point of sale

Entry: Phase 3 gate passed. Requirements POS-1 to POS-7, TL-1 to TL-3.


| # Task | Rules to read |
| --- | --- |
|   | first |
| 4.1 One barcode entry function. USB scanner, typed entry, webcam and simulate-scan | Doc 4.3, D17 |
| all call it. |   |
| 4.2 Cart on a linked list: add (merge same product), change quantity, remove | Doc 6.6 |
| 4.3 Checkout: total, cash check, change | Doc 6.6 |
| 4.4 Deduct stock: FEFO or FIFO per item, skip expired, span batches, record batch and | Doc 6.2 |
| quantity on each sale line |   |
| 4.5 Receipt data from the cart traversal | POS-6 |
| 4.6 Transaction log (all types) | TL-1, TL-2 |
| 4.7 Undo with the stack: restore to the same batches, log a void, block when a newer | Doc 6.7 |
| transaction exists |   |
| 4.8 Low-stock check after each sale | RS-1 |
| 4.9 Unknown barcode result that the UI can turn into 'Register product' | Doc 9.4 |

Exit gate: a full sale, including one that spans two batches and one mixed cart, works end to end with no UI. Edge cases 7 to 9, 13 to 16 pass.

## Phase 5: Restock and reports

Entry: Phase 4 gate passed. Requirements RS-2 to RS-4, RP-1 to RP-8.


| # Task | Rules to read |
| --- | --- |
|   | first |
| 5.1 Selling speed (14-day average), days of cover | Doc 6.8 |
| 5.2 Restock queue on the max-heap, reason text per row | Doc 6.8 |
| 5.3 Suggested reorder quantity, never below zero | Doc 6.8 |
| 5.4 Top-k and bottom-k sellers with the size-k heap | Doc 10.1 |
| 5.5 Daily totals and prefix sums for revenue, units, COGS | Doc 7.3 C |
| 5.6 Reports: revenue, COGS, gross profit, margin, spoilage, inventory value, profit per | Doc 10 |
| item |   |
| 5.7 Dashboard numbers: today's sales, profit, low-stock count, near-expiry count | RP-8 |
| (tracked products only) |   |

Exit gate: report numbers equal hand-calculated values on a small fixed data set. Voided sales are excluded from totals.

## Phase 6: Sample data and benchmarks

Entry: Phase 5 gate passed.

| # Task | Rules |
| --- | --- |
| 6.1 Generator with a fixed seed. 30 to 100 products, 6 to 8 categories, 20 to 30 percent no- | Doc 8.3 |
| expiry, 30 to 90 days of sales. |   |
| 6.2 Benchmarks B1 to B6 | Doc |
|   | 12.3 |
| 6.3 Results table and one chart per benchmark, saved in benchmarks/results/ | Doc |
|   | 12.3 |

## Benchmark protocol:

- Use time.perf_counter() . Warm up first. Repeat at least 30 times. Report median, minimum and maximum.

- Same machine and data. Record the machine and Python version. (Benchmarks run on the PC, which is now also the target.)

- B3 and B4 use identical simulated sales for both methods, tracked products only for B3.


- Include the BST sorted-insertion worst case in B1.

- Report results honestly, including cases where the naive method wins.

Exit gate: all six benchmarks have saved results. Feature freeze: after this gate, new ideas go to docs/later_list.md , not into the build.

## Phase 7: Desktop UI

Entry: freeze in place. Designers' desktop specs exist in design/ (or the human says to build from Doc 11.4 as adapted in CHANGES_v2.1).

| # Task | Rules |
| --- | --- |
| 7.1 Design tokens and shared components built once Colors, type, spacing, status badge, list |   |
|   | row, chip, stepper, snackbar, confirm |
|   | dialog (Doc 11.3, sizes adapted for |
|   | desktop) |
| 7.2 Navigation: side navigation rail with Home, Sell, Stock, | CHANGES_v2.1 |
| Restock, Reports. More menu for history, shelf rotation, |   |
| backup, settings. |   |
| 7.3 Screens in this order: Sell, Checkout, Receipt, Stock list, | Doc 11.4 |
| Product detail, Receive stock, Register product, Home, |   |
| Near-expiry list, Checklist, Write-off list, Restock, |   |
| Reports, History, Settings, Backup |   |
| 7.4 Every screen handles empty, loading, error and success | Doc 11.5 |
| states |   |
| 7.5 Keyboard support: Enter confirms, Esc cancels, Tab | CHANGES_v2.1 |
| order follows visual order, shortcut to focus the barcode |   |
| field |   |
| 7.6 Export, restore, backup reminder (file picker for the | Doc 9.6 |
| backup location) |   |
| 7.7 HUMAN: scanner test on the target PC (USB scanner | Doc 4.3 |
| and, if available, webcam) |   |
| 7.8 HUMAN: usability test with 2 or 3 outsiders | Doc 12.4 |

UI rules:


- The UI only displays data from services and sends user actions to them. If a screen needs a rule, add it to services/ first.

- Use the exact wording from the designers' microcopy sheet. Do not invent text.

- Status always shows icon, word and color together.

- Click and tap targets stay generous (at least 40 px, keep 48 where there is room so a later Android build needs little change). Lists show 5 to 7 rows then See all, or a scrollable table on wide screens. One primary button per screen.

- The window must resize without breaking. Minimum window size is set in one place.

- If a design cannot be built with a standard Flet control, stop and report (Section 8). Do not build a custom control without approval.

Exit gate: all screens exist with all states. Contrast, keyboard-only and font-scaling checks (Doc 11.7, adapted) done. Usability test round complete.

## Phase 8: Release

- \# Task

- 8.1 Fresh-clone test: install and run from the pinned requirements.

- 8.2 Re-run all tests and all benchmarks on the final code.

- 8.3 Build the final packaged desktop app. HUMAN: run it on the demo PC from a cold start.

- 8.4 Walk the Release Checklist (Doc Appendix A, adapted in CHANGES_v2.1).

- 8.5 Update README, decisions log and the documentation to match what was built.

Exit gate: the demo runs on the demo PC using simulate-scan (or a USB scanner if available). Webcam scanning is a bonus.

## Optional later: Android

Not part of the graded build. Only after Phase 8, and only if the human asks. Tracked in docs/later_list.md : flet build apk , phone layout (bottom bar, portrait), touch-target review, camera scanner test on a real phone.

## 6. Quick rule sheet

Open the PDF for full detail. These are the rules agents most often get wrong.


| Topic | Rule |
| --- | --- |
| Alert levels Days left = expiry minus today. Below 0: Expired. 0 up to red limit: Red. Up to amber |   |
|   | window: Amber. Above: OK. |
| Red limit One-third of the amber window, rounded, minimum 1 day. (3 gives 1, 5 gives 2, 7 gives |   |
|   | 2, 14 gives 5, 30 gives 10) |
| Expiry today Red and still sellable. Expired starts the next day. |   |
| Window source Category warning days. No category: global default, 7 days. |   |
| Deduction order Tracked: earliest expiry, tie then earlier received. No expiry: earliest received, tie then |   |
|   | lower batch id. |
| Deduction span Take what the front batch has, then continue with the next. Record every batch and |   |
|   | quantity on the sale line. |
| Sellable stock Excludes expired batches. Low-stock checks use sellable stock. |   |
| No-expiry | Never in alerts, checklist, write-off or spoilage. Included in value, revenue, COGS, |
| products | profit, low-stock. |
| Undo | Latest transaction only. Blocked if a newer one exists. Undo of a receive is refused if |
|   | any of its units were sold. |
| Reports | Voided sales removed from all totals. Margin is 0 percent when revenue is 0. |
| Restock rank Days of cover (lowest first), then selling speed (highest first), then expiry pressure. |   |
|   | Starting formula, may be tuned. |
| Reorder quantity Selling speed times target cover days (default 14) minus sellable stock, rounded up, |   |
|   | never below zero. |

## 7. When to ask the human

Stop and ask if any of these happen. Do not guess.


| Trigger | Why |
| --- | --- |
| Two documents disagree and the order in Section 2 does not settle it Risk of building the wrong |   |
|   | rule |
| A requirement is missing, unclear or contradicts a business rule | Avoid silent assumptions |
| You need a new dependency | Packaging is fragile |
| You want to change the Flet version | Pinned on purpose |
| A design needs a custom control Flet cannot provide | Scope and effort risk |
| You want to change a data structure's role or use a built-in in ds/ | Breaks the graded rule |
| The same problem fails after two fix attempts | Report rather than loop |
| Any step needs the target PC, a real person or a decision (marked | Cannot be done by an agent |
| HUMAN) |   |
| A change would delete or rewrite existing data or history | Safety |
| The human asks to start the Android build | It is outside the graded build |

Proceed with the default and log it for the open items below (Doc 17):


| Open item | Default to use |
| --- | --- |
| Target operating system Windows (D15). Ask if the human says macOS or Linux. |   |
| Android | Optional, after release (D16) |
| Uncategorized products | Track expiry, 7-day window |
| Undo scope | One level, most recent only |
| Expired batches | Blocked from sale |
| Returns of older sales | Not supported. Use stock adjustment. |
| Receipt | On-screen only |
| Restock formula | As in Doc 6.8 |
| PIN lock, push notifications Not built |   |
| Hash table benchmark | BST only |
| Deadline | 12-week template |

Write every default you use into docs/assumptions_log.md with the date and the task.

## 8. Stop-and-report format

When blocked, stop and write this and nothing more:

Task: the task number

What I tried: the attempts, briefly

What failed: exact error or conflict in plain words

Options: two or three ways forward with a trade-off each

My recommendation: one option and why

What I need from you: one clear question

## 9. Reporting and logs

After every task, add one entry to docs/progress_log.md :

- Task number and name

- What changed (files)

- Tests added and the full-suite result

- Rules or edge cases covered (by Doc number)


- Assumptions made

- Anything left open

## Keep three logs current:

- docs/progress_log.md : what was done.

- docs/assumptions_log.md : every default or guess, with date.

- docs/decisions_log.md : decisions confirmed by the human. Mirrors Doc 3 plus D15 to D17.

At each phase gate, write a short gate report: gate criteria, pass or fail for each, and the next phase.

## 10. Dependency map

| Needs | Before |
| --- | --- |
| Linked list, stack | Cart, transaction log, undo |
| Min-heap with ordered read and remove- | Alerts, FEFO, undo of a receive |
| specific |   |
| BST | Barcode lookup, POS |
| Trie | Name search |
| Max-heap | Restock queue |
| Prefix sums, size-k heap | Reports, top-k |
| Category service | Alerts, receive stock, product form |
| Alert service | Near-expiry list, checklist, older-stock message, |
|   | dashboard |
| Transaction lines with batch ids | Undo, spoilage report, COGS |
| Services complete (Phases 3 to 5) | Any UI work |
| Designers' desktop specs and tokens | Phase 7 screens |

## 11. Anti-patterns (do not do these)

- Writing code before the ADT and tests exist for a data structure.

- Using heapq , dict or sorted in ds/ or services/ to save time.

- Putting a rule in a Flet screen because it was faster.

- Storing the alert level instead of calculating it.

- Selling from an expired batch, or from a batch that is not at the front of its order.


- Editing history to fix a mistake. Use an adjustment or a void instead.

- Guessing an expiry date when a category switches to tracking.

- Adding features after the freeze.

- Building a custom control, or adding a dependency, without approval.

- Putting OS-specific code or hard-coded file paths in ds/ , services/ or db/ .

- Running a long task with no commit, no log entry and no test run.

- Marking a task done while any test fails.

- Reporting estimated benchmark numbers. Only measured ones.

## 12. Definition of done

## Every task

- Tests written first, and the full suite passes.

- Matches the business rules and the hard rules above.

- No layer violations. No built-ins in ds/ .

- Logged in the progress log. One commit.

## Every phase

- Exit gate criteria all pass and a gate report is written.

## The project

- Phases 1 to 6 complete with tests and benchmark results.

- All screens built with all states.

- Packaged desktop app runs on the demo PC. Backup export works.

- Release Checklist complete. Documentation matches the final app.
