# StockFlow Progress Log

## Task 0.1: Create Folder Layout from Doc 4.5, plus docs/ and design/
- **Date**: 07 Nov 2026
- **What Changed**:
  - Created package directories with `__init__.py`: `ds/`, `models/`, `services/`, `db/`, `ui/`, `ui/components/`, `ui/screens/`, `data/`, `benchmarks/`, `tests/`.
  - Created asset & tracking folders: `docs/adt/`, `design/wireframes/`, `benchmarks/results/`.
  - Added layout test: `tests/test_layout.py`.
- **Tests Added & Result**:
  - `tests/test_layout.py`: 2 tests (`test_packages_are_importable`, `test_required_directories_exist`).
  - Result: 2 passed (100% OK under `python -m unittest`).
- **Rules / Edge Cases Covered**:
  - Doc 4.5 project folder architecture.
  - Layering foundations: isolated `ds/`, `services/`, `db/` with zero UI dependencies.
- **Assumptions Made**:
  - Standard library `unittest` used as verification harness until `pytest` is pinned and installed in Task 0.2.
- **Anything Left Open**:
  - Task 0.2: Pin Flet, pytest, and Faker in `requirements.txt`.
