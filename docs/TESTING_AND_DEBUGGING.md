# Testing and Debugging — StockFlow

## 1. Test Cases, Expected Results, and Actual Results

| Test ID | Area / Module | Test Case Description | Expected Result | Actual Result | Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **TC-01** | Data Structures (`tests/test_ds_trees.py`) | BST insert, lookup, delete (leaf, 1 child, 2 children), duplicate key rejection, and randomized oracle check. | All BST operations match sorted reference behavior; duplicate keys rejected. | All 10 BST tests pass against reference oracle. | **PASS** |
| **TC-02** | Data Structures (`tests/test_ds_trees.py`) | Trie insert, prefix lookup (limit 8), deletion, and randomized prefix oracle check. | Returns up to 8 matching products per prefix; deletion removes only target word. | All 5 Trie tests pass. | **PASS** |
| **TC-03** | Data Structures (`tests/test_ds_heaps.py`) | Min-Heap & Max-Heap insert, peek, extract, tie-breaks, non-destructive ordered read, and remove-specific item. | Heap invariant preserved across tie-breaks, removals, and large random inputs. | All 11 Heap tests pass. | **PASS** |
| **TC-04** | Data Structures (`tests/test_ds_linked_list.py`, `test_ds_stack.py`) | LinkedList add front/end, find, remove head/middle/tail; Stack LIFO push/pop/peek. | Operations match Python list/oracle behavior for empty, single, duplicate, and random cases. | All 17 LinkedList & Stack tests pass. | **PASS** |
| **TC-05** | Analytics DS (`tests/test_ds_prefix_topk.py`) | PrefixSums range queries; Size-K Heap top-k and bottom-k ranking with ties. | Range sums and top/bottom-k match brute-force oracle. | All 10 PrefixSums & Size-K Heap tests pass. | **PASS** |
| **TC-06** | Storage & Migration (`tests/test_models_storage.py`, `test_db_migration.py`) | Save/load round-trip, atomic sale rollback on failure, and one-time idempotent migration to `%APPDATA%\StockFlow\stockflow.db`. | Reopening DB restores identical state; failed sale writes nothing; migration runs once safely. | All 9 storage & migration tests pass. | **PASS** |
| **TC-07** | POS & FEFO (`tests/test_services_pos_fefo.py`) | Barcode entry (known/unknown), cart merge, FEFO deduction spanning multiple batches, expired batch blocked, insufficient cash blocked. | Earliest valid batch deducted first; expired stock never sold; low-stock alert triggered. | All 7 POS/FEFO tests pass. | **PASS** |
| **TC-08** | Undo (`tests/test_services_undo.py`) | Void latest sale and restore exact quantities to original batches; block undo when newer transaction exists. | Stock restored to exact batch IDs; non-latest undo raises error. | All 3 Undo tests pass. | **PASS** |
| **TC-09** | Inventory & Edge Cases (`tests/test_services_inventory.py`, `test_edge_cases.py`) | Expiry boundary checks (expires today vs. yesterday, amber window), category switch, write-off, stock adjustment. | Expiry-today is Red & sellable; expired-yesterday is blocked; category switch flags unresolved batches. | All 20 inventory & edge-case tests pass. | **PASS** |
| **TC-10** | Reports & Restock (`tests/test_services_reports.py`) | Hand-calculated revenue, COGS, gross profit, margin, spoilage, inventory value, dashboard KPIs, and restock queue. | Report numbers match hand calculations with voided sales excluded. | All 5 report & restock tests pass. | **PASS** |
| **TC-11** | API & Layout (`tests/test_api_server.py`, `test_layout.py`) | End-to-end API workflow (categories, products, POS, undo, reports, backup/restore) and package layout check. | Full workflow succeeds and all packages import cleanly. | All 3 layout & API integration tests pass. | **PASS** |
| **TC-12** | Frontend TypeScript (`npx tsc --noEmit`) | Static type-check across all React 19 + TypeScript pages and components. | Zero TypeScript compilation errors. | `tsc --noEmit` exited with code `0`. | **PASS** |
| **TC-13** | Packaged Desktop App (`StockFlowSetup-1.1.0.exe`) | Per-user install, double-click launch without HTTP server, icon rendering, and data persistence (`83` products). | App opens in `pywebview`, icons render offline, DB counts remain intact (`83` products, `12` categories, `180` transactions). | Verified in installed `StockFlow.exe` and `stockflow.log`. | **PASS** |

---

## 2. Errors Encountered and Corrections Applied

| # | Error Encountered | Root Cause | Correction Applied | Files Modified |
| :--- | :--- | :--- | :--- | :--- |
| **1** | `127.0.0.1 refused to connect (ERR_CONNECTION_REFUSED)` when launching via Edge `--app` mode. | Edge handed off to an existing background browser process and exited the launcher early, leaving no backend running. | Replaced Edge `--app` + local HTTP dependency with an in-process `pywebview` (WebView2) desktop window using the `window.pywebview.api` JS-to-Python bridge. | `desktop_app.py`, `backend/api_server.py`, `frontend/src/api.ts` |
| **2** | Sidebar, navigation, and welcome-screen icons failed to load in the packaged `.exe`. | `Shell.tsx` and `StartingPage.tsx` used root-relative `/assets/...` paths, which resolved to `file:///C:/assets/...` under `file://`. `index.css` also loaded `@font-face` fonts from an external CDN. | Changed asset paths to relative `./assets/...` and removed external `@font-face` URLs in favor of local system font fallbacks. | `frontend/src/components/Shell.tsx`, `frontend/src/pages/StartingPage.tsx`, `frontend/src/index.css` |
| **3** | Webcam barcode scanner failed with `NotReadableError`, could not persist permissions, and later produced false-positive reads. | `BarcodeScanner.tsx` opened `getUserMedia` twice (`NotReadableError`), `pywebview` defaulted to `private_mode=True`, and permissive formats (`ITF`/`CODABAR`) + contrast filters misread background noise on a single frame. | Switched to single-stream `decodeFromCanvas` ROI scanning, restricted formats to checksum-protected retail codes (`EAN_13`, `UPC_A`, `CODE_128`, `QR_CODE`, etc.), added 2-hit confirmation within `1.2s`, and set `private_mode=False` with a dedicated `storage_path`. | `frontend/src/components/BarcodeScanner.tsx`, `desktop_app.py` |
| **4** | `test_task_5_6_financial_reports_exact_hand_calculated_values` failed (`370.0 != 410.0`). | Fragile date-dependent test: `get_financial_summary()` was called without `today=self.today` (`2026-11-23`), so it used `date.today()` (`2026-11-27`), expiring a `2026-11-26` fixture batch worth `PHP 40.00`. | Passed `today=self.today` explicitly to `get_financial_summary(today=self.today)`. | `tests/test_services_reports.py` |
| **5** | Inno Setup silent upgrade skipped overwriting `StockFlow.exe` when an older instance was running. | Background `StockFlow.exe` held a file lock during silent upgrade, causing RestartManager to abort. | Closed running `StockFlow.exe` before upgrading and verified `v1.1.0` installed cleanly. | `installer/StockFlowSetup.iss` (version bumped to `1.1.0`) |

---

## 3. Evidence of Successful Testing

### A. Automated Python Test Suite (`pytest -v`)
```text
============================= test session starts =============================
platform win32 -- Python 3.13.4, pytest-8.4.2, pluggy-1.7.0
rootdir: C:\Users\bryan\Desktop\STOCKFLOW
collecting ... collected 100 items
...
============================= 100 passed in 0.55s =============================
```

### B. Frontend Type-Check & Production Build
```text
> npx tsc --noEmit   -> exit code 0 (0 errors)
> npm run build      -> vite v8.3.8 built in 355ms (dist/index.html, dist/assets/*)
```

### C. Installed Desktop App Log (`%APPDATA%\StockFlow\stockflow.log`) & Database Integrity
```text
2026-11-27 23:28:43,476 [INFO] Starting StockFlow v1.1.0
2026-11-27 23:28:43,487 [INFO] Database ready at C:\Users\bryan\AppData\Roaming\StockFlow\stockflow.db (83 products)
```
Verified SQLite row counts after fixes and upgrade:
- `categories`: 12
- `products`: 83
- `batches`: 83
- `transactions`: 180
- `transaction_lines`: 452
- `settings`: 3
- `locations`: 1

### D. Empirical Benchmarks (`B1`–`B6`)
- Results table and methodology: `benchmarks/results/RESULTS.md`
- Generated charts: `benchmarks/results/b1_chart.svg` through `benchmarks/results/b6_chart.svg`
