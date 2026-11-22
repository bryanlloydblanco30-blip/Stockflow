# StockFlow Documentation: Changes in Version 2.1

**Date**: 6 November 2026
**Reason**: Main platform is now a desktop PC (Windows assumed). Android is an optional extra after release.
**Rule**: Where Version 2.0 says Android, APK or phone, this file wins.

---

## New Decisions (Section 3)

| ID | Decision | Why | Status |
| :--- | :--- | :--- | :--- |
| **D15** | The primary target is a desktop PC. Windows is assumed until the team says otherwise. | The store computer is the main device. Flet runs the same Python code as a desktop app. | Confirmed |
| **D16** | Android is optional and comes after the release. It is not part of the graded build. | Keeps scope small. Core logic is platform neutral, so Android stays possible. | Confirmed |
| **D17** | `backend/ds/`, `backend/services/` and `backend/db/` stay platform neutral. The database path comes from one function. Barcode input comes from one entry function that accepts USB scanner, typed entry, webcam and simulate-scan. | A later Android build then needs only UI and path changes. | Confirmed |

---

## Key Section Changes
- **Navigation**: Side navigation rail replaces mobile bottom bar on desktop.
- **Sell Screen**: Split-pane layout: Cart table on the left, sticky checkout totals on the right.
- **Stock Screen**: Sortable data table with instant trie autocomplete.
- **Barcode Input**: USB/Bluetooth barcode scanner acts as primary hardware; simulate-scan button always available.
- **Accessibility**: WCAG AA contrast (4.5:1), keyboard navigation (Tab/Enter/Esc), 40px minimum click target.

