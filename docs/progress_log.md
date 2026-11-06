# StockFlow Progress Log

## Task 0.1: Create Folder Layout from Doc 4.5, plus docs/ and design/
- **Date**: 07 Nov 2026
- **What Changed**:
  - Restructured directory architecture with explicit `frontend/` and `backend/` separation:
    - `frontend/`: `ui` components and screens (`frontend/components/`, `frontend/screens/`).
    - `backend/`: `ds/`, `models/`, `db/`, `services/`.
  - Created asset & tracking folders: `docs/adt/`, `design/wireframes/`, `benchmarks/results/`, `scripts/`.
  - Added layout test: `tests/test_layout.py`.
- **Tests Added & Result**:
  - `tests/test_layout.py`: 2 tests (`test_packages_are_importable`, `test_required_directories_exist`).
  - Result: 2 passed (100% OK under `python -m unittest`).
- **Rules / Edge Cases Covered**:
  - Doc 4.5 folder architecture adapted for explicit frontend/backend directory boundaries.
  - Strict boundary: `backend/` has zero Flet or UI imports; `frontend/` calls `backend.services`.
- **Assumptions Made**:
  - Single offline desktop app preserved while separating frontend and backend packages cleanly.
- **Anything Left Open**:
  - Task 0.2: Pin Flet, pytest, and Faker in `requirements.txt`.

