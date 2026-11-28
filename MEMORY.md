# STOCKFLOW AGENT MEMORY & STATE

## 1. Project Profile & Stack
- **Project**: StockFlow (Offline Desktop Inventory, POS & Financial Reporting)
- **Target Platform**: Desktop PC (Windows assumed, platform-neutral core logic)
- **Runtime & Language**: Python 3 (Tested on Python 3.13)
- **UI Framework**: React (React 19 + TypeScript + Vite + Tailwind CSS in `frontend/`; switched from Flet per owner decision D18)
- **Storage**: SQLite (`sqlite3`, stored locally, platform-neutral path provider)
- **Currency & Formatting**: PHP (`PHP 1,250.00`), Dates (`12 Nov 2026`)

## 2. Hard Architectural Rules (Never Break)
- **Frontend / Backend Separation**:
  - `frontend/`: UI screens & components using React + TypeScript + Vite (`npm run dev`).
  - `backend/`: Core business logic (`services/`), custom data structures (`ds/`), models (`models/`), and persistence (`db/`).
  - `frontend/` calls `backend.services` (via API/bridge). Layers talk strictly downward. No business rules in `frontend/`.
  - `backend/` contains **NO UI framework imports** and runs under `pytest` with no UI.
- **From-Scratch Data Structures in `ds/`**:
  - Linked List, Stack, Min-Heap, Max-Heap, BST, Trie, Prefix Sums, Size-k Heap.
  - **ABSOLUTE BAN**: `heapq`, `dict`, and `sorted` are prohibited in `ds/` and `services/` (allowed ONLY inside `benchmarks/` as naive baselines).
  - Category list uses a plain dynamic array (D13).
- **Core Business Rules**:
  - Expired batches are never sold (D10).
  - FEFO per product: 1 Min-Heap per product (expiry key, received date tie-break). No-expiry uses FIFO.
  - Alert level calculated on the fly, never stored (D9).
  - Undo reverses only the most recent transaction, 1 level via Stack (D2).
  - Cash payment only. Exact historical batch prices and costs recorded on sale lines.

## 3. Workflow & Definition of Done
- Order: ADT spec (`docs/adt/<name>.md`) -> Unit Tests (`tests/`) -> Implementation (`ds/`, `services/`).
- One task at a time. Tests must pass 100% before closing a task.
- Log task completions in `docs/progress_log.md` and keep `MEMORY.md` synchronized.

## 4. Current State & Next Steps
- **Active Phase**: Phase 7: React UI
- **Current Task**: User visual/hardware verification of icons and webcam barcode scan
- **Last Completed Task**: Fixed Bugs 1-4, removed UI DSA labels, rebuilt StockFlowSetup-1.1.0.exe (on 27 Nov 2026, 23:28)
- **Last Test Status**: 100 passed (pytest), tsc 0 errors
