# StockFlow Decisions Register

These decisions were confirmed with the project owner and are treated as fixed unless explicitly changed. They reflect Doc 3 and platform decisions D15 to D17 in `CHANGES_v2.1.md`.

| ID | Decision | Why | Status |
| :--- | :--- | :--- | :--- |
| **D1** | The core is single-location. Products, batches and transactions still store a location id. | Multi-location is an extension. Storing the id now avoids a redesign later. | Confirmed |
| **D2** | Undo reverses only the most recent transaction, one level. | Matches Version 1.0. The stack can be widened later with no structural change. | Confirmed |
| **D3** | FEFO uses one min-heap per product, ordered by expiry date. | A sale is for one product at a time. A global heap would not help find a product's batches. | Confirmed |
| **D4** | FEFO is also a shelf-rotation tool. The app warns about close-to-expiry batches and tells the clerk to put new stock behind older stock. | Physical shelf order must match system order, or customers take newer stock first. | Confirmed |
| **D5** | Near-expiry alerts list every batch inside the warning window, not only the front batch. | A product can have several batches inside the window. | Confirmed |
| **D6** | Warning windows are set per category. A global default is used for uncategorized products. | Bread and canned goods need very different lead times. | Confirmed |
| **D7** | Red level starts at one-third of the category's amber window, minimum 1 day, calculated automatically. | One number per category keeps the settings screen simple. | Confirmed |
| **D8** | Categories can turn expiry tracking off. Their products need no expiry date and are sold oldest-received-first (FIFO). | School supplies, hygiene items and batteries have no expiry. | Confirmed |
| **D9** | Alert level is calculated from the date when needed, not stored. | Changing a window updates all batches at once. No data migration. | Confirmed |
| **D10** | Expired batches are never sold. They appear in a write-off list. | Selling expired goods is unsafe. This also feeds the spoilage report. | Confirmed |
| **D11** | Uncategorized products track expiry by default, with the global default window of 7 days. | Safest choice for a store. | Assumed, to confirm |
| **D12** | Barcode lookup uses a BST. A hash table is a later benchmark comparison once covered in class. | Hash tables are not yet covered in the course. | Confirmed |
| **D13** | The category list uses a plain dynamic array. | Only 5 to 15 categories. `dict` is reserved for benchmark baselines. | Confirmed |
| **D14** | The in-app alert list and checklist come first. Phone push notifications are an upgrade. | Notification support is uncertain and out of core scope. | Confirmed |
| **D15** | The primary target is a desktop PC. Windows is assumed until the team says otherwise. | The store computer is the main device. Flet runs the same Python code as a desktop app. | Confirmed |
| **D16** | Android is optional and comes after the release. It is not part of the graded build. | Keeps scope small. Core logic is platform neutral, so Android stays possible. | Confirmed |
| **D17** | `backend/ds/`, `backend/services/` and `backend/db/` stay platform neutral. The database path comes from one function. Barcode input comes from one entry function that accepts USB scanner, typed entry, webcam and simulate-scan. | A later Android build then needs only UI and path changes. | Confirmed |
| **D18** | Frontend UI framework changed from Flet to React (React 19 + TypeScript + Vite + Tailwind CSS in `frontend/`). | Project owner switched frontend stack from Flet to React (24 Nov 2026). Python `backend/` remains platform-neutral and UI-agnostic. | Confirmed |

