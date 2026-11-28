# StockFlow 📦🚀

> **Offline-first Inventory, Point-of-Sale (POS), and Intelligent Reporting System**  
> Built with custom from-scratch Data Structures & Algorithms in Python, paired with a modern React 19 + TypeScript + Tailwind CSS desktop UI.

---

## 🌟 Key Highlights

- **From-Scratch DSA**: Core data structures (MinHeap, MaxHeap, BST, Trie, LinkedList, Stack, PrefixSums, SizeKHeap) are built completely from scratch without standard library shortcuts (`heapq`, `dict` shortcuts, or `sorted`) in domain layers.
- **First-Expired, First-Out (FEFO)**: Automated inventory batch deduction using product-specific Min-Heaps to prevent food and medicine spoilage.
- **Fast Search & Lookup**: Instant barcode lookup via Binary Search Tree ($O(\log n)$) and real-time product name autocomplete via Trie ($O(L)$).
- **Offline & Desktop First**: Fully self-contained with SQLite storage, zero external cloud dependencies, and a resilient local architecture.
- **Intelligent Restock & Analytics**: Restock priority queue powered by Max-Heap; daily revenue/COGS range queries accelerated by Prefix Sums; top/bottom seller rankings computed by Size-K Heap routines.

---

## 🏗️ Architecture & Tech Stack

```text
┌────────────────────────────────────────────────────────┐
│               Frontend: React 19 + TypeScript          │
│               Vite + Tailwind CSS + Lucide Icons       │
│               Running at http://localhost:5173         │
└───────────────────────────┬────────────────────────────┘
                            │ HTTP API (Vite Proxy)
┌───────────────────────────▼────────────────────────────┐
│         Backend API Server: Python stdlib              │
│       ThreadingHTTPServer (No Flask/FastAPI deps)      │
│               Running at http://localhost:8443         │
├────────────────────────────────────────────────────────┤
│                   Domain Services                      │
│   ProductService  •  CategoryService  •  AlertService  │
│   Cart / POS      •  RestockService   •  ReportService │
├────────────────────────────────────────────────────────┤
│           Custom Data Structures (`backend/ds/`)        │
│   MinHeap • MaxHeap • BST • Trie • LinkedList • Stack  │
│              PrefixSums • SizeKHeap                    │
├────────────────────────────────────────────────────────┤
│                 Persistence Layer                      │
│        SQLite Database (`stockflow.db`) + Models       │
└────────────────────────────────────────────────────────┘
```

- **Frontend**: React 19, TypeScript, Vite, Tailwind CSS, Lucide Icons.
- **Backend API**: Python 3 standard library (`http.server.ThreadingHTTPServer`, zero external framework dependencies).
- **Core Domain & DSA**: Pure Python 3, 100% test-driven with `pytest`.
- **Database**: SQLite 3 (`stockflow.db`).

---

## 🧠 Data Structures & Algorithms

Every core capability is powered by a custom-built data structure:

| Data Structure | Implementation File | Primary Role | Complexity |
| :--- | :--- | :--- | :--- |
| **Binary Search Tree (BST)** | `backend/ds/bst.py` | Barcode index & instant product lookup | Search: $O(\log n)$ avg |
| **Trie (Prefix Tree)** | `backend/ds/trie.py` | Fast product name prefix search & autocomplete | Search: $O(L)$ |
| **Min-Heap** | `backend/ds/min_heap.py` | FEFO stock deduction & near-expiry alert scanning | Extract/Insert: $O(\log n)$ |
| **Max-Heap** | `backend/ds/max_heap.py` | Reorder priority queue based on days-of-cover | Extract/Insert: $O(\log n)$ |
| **Doubly Linked List** | `backend/ds/linked_list.py` | POS shopping cart & batch inventory records | Traversal: $O(n)$, Add: $O(1)$ |
| **Stack** | `backend/ds/stack.py` | Single-level atomic transaction rollback (Undo) | Push/Pop: $O(1)$ |
| **Prefix Sums** | `backend/ds/prefix_sums.py` | Daily sales, revenue, and COGS range aggregation | Range Query: $O(1)$ |
| **Size-K Heap** | `backend/ds/size_k_heap.py` | Top-K best sellers & Bottom-K slow-moving stock | Stream Processing: $O(N \log K)$ |

All structures include formal specifications in `docs/adt/` and comprehensive unit test suites in `tests/`.

---

## 🚀 Quick Start

### 1. Prerequisites
- **Python 3.10+**
- **Node.js 18+** & **npm**

### 2. Clone the Repository
```bash
git clone https://github.com/bryanlloydblanco30-blip/Stockflow.git
cd Stockflow
```

### 3. How to Install & Run (End Users — Windows)
1. Download **`StockFlowSetup-1.0.0.exe`** (from `dist/installer/`).
2. Double-click `StockFlowSetup-1.0.0.exe` (no administrator rights or Python/Node.js required; if Microsoft Edge WebView2 Runtime is missing, the installer downloads and installs it automatically).
3. **Windows SmartScreen Notice:** Because the installer is not code-signed with a commercial certificate, Windows Defender SmartScreen may show *"Windows protected your PC"*. Click **More info** → **Run anyway** to proceed.
4. Launch **StockFlow** from the **Start Menu** or Desktop shortcut.
5. **Upgrading / Uninstalling:** Installing a newer version upgrades in place and preserves your data. Uninstalling removes only the application files, never your database.

### 💾 Local Device Storage & Migration
- All active data is stored locally in your device's application data folder:
  - **Windows:** `%APPDATA%\StockFlow\stockflow.db` (backups in `%APPDATA%\StockFlow\backups\`, startup/error log in `%APPDATA%\StockFlow\stockflow.log`)
  - **macOS:** `~/Library/Application Support/StockFlow/stockflow.db`
  - **Linux:** `~/.local/share/StockFlow/stockflow.db`
- New installations start with an empty database.
- On first launch on an existing machine, if the app-data database does not exist yet and a legacy `stockflow.db` is found in the project or executable directory, StockFlow performs a **safe, idempotent one-time migration** using SQLite's backup API so existing records are preserved without overwriting.

### 4. Build the PC Desktop App & Installer from Source
To rebuild the standalone `pywebview` executable and Inno Setup installer:
```bash
cd frontend && npm run build && cd ..
pyinstaller StockFlow.spec --noconfirm
"C:\Program Files (x86)\Inno Setup 6\ISCC.exe" installer\StockFlowSetup.iss
```
> Produces `dist\StockFlow\StockFlow.exe` and `dist\installer\StockFlowSetup-1.0.0.exe`.
> Internally, `desktop_app.py` loads `frontend/dist/index.html` directly inside a native WebView2 window (`pywebview`) and communicates with Python over `window.pywebview.api` with zero HTTP server or local ports.

### 5. Development Mode
For live code development with hot reloading:
```bash
# Terminal 1: Backend API & static server
python main.py

# Terminal 2: Vite React dev server
cd frontend
npm install
npm run dev
```
> Open your browser at **`http://localhost:5173`** (or proxy port `http://localhost:8443`).

---

## 🧪 Testing & Verification

### Run Pytest Suite
```bash
pytest -v
```
All 97 unit and integration tests verify:
- ADT invariant properties, boundary conditions, edge cases, and tie-breaking.
- Atomic POS transactions, batch splits across expiry dates, and single-level undo.
- Zero banned built-ins in domain and data structure modules.

### Run Benchmarks
Run the full empirical benchmark suite comparing custom DSA implementations against naive baselines:
```bash
python -m benchmarks.run_all
```
Generated benchmark charts and tabular metrics are stored in `benchmarks/results/`.

---

## 📁 Project Structure

```text
Stockflow/
├── backend/
│   ├── api_server.py         # HTTP REST API server (Python stdlib)
│   ├── db/                   # SQLite schema, connection, and seeders
│   ├── ds/                   # From-scratch Data Structures (BST, Trie, Heaps, etc.)
│   ├── models/               # Dataclass entities (Product, Batch, Transaction, etc.)
│   └── services/             # Domain logic (Inventory, Cart, Alerts, Reports, Restock)
├── benchmarks/               # Empirical performance benchmarks (B1 - B6)
├── docs/                     # ADT specifications, decisions log, progress log
├── frontend/                 # React 19 + TypeScript + Vite + Tailwind CSS app
│   ├── src/
│   │   ├── api.ts            # REST client connecting to Python backend
│   │   ├── components/       # UI widgets (Sidebar, Scanner, Modals, Badges)
│   │   └── pages/            # Views (Dashboard, POS, Inventory, Alerts, Restock, Reports)
├── tests/                    # 97 Pytest test cases
├── main.py                   # Main backend application entry point
└── stockflow.db              # Seeded SQLite database
```

---

## 📜 Business Rules & Decisions
- **FEFO Guarantee**: Expired batches are automatically blocked from sale. Oldest valid batches are deducted first.
- **Atomic Undo**: Rolling back the last transaction restores exact quantities to their original batch IDs.
- **Reporting Invariance**: Historic sale lines freeze cost and price at the exact moment of transaction.
- **Currency & Formatting**: Designed for Philippine Peso (`PHP 1,250.00`) and standard retail store operation.

---

## 🗺️ DSA Usage Map (UI Plain-Language Mapping)

All user-facing DSA terminology was replaced with plain-language storekeeper copy while keeping the underlying custom `backend/ds/` structures unchanged:

| Feature / Screen | Backend Data Structure | Plain-Language UI Copy |
| :--- | :--- | :--- |
| Barcode scan & lookup (`SellPage`, `StockPage`) | `BST` (`backend/ds/bst.py`) | Barcode search / ready for sale |
| Product name autocomplete (`StockPage`) | `Trie` (`backend/ds/trie.py`) | Product catalog search |
| POS cart items (`SellPage`) | `LinkedList` (`backend/ds/linked_list.py`) | Cart items list |
| Earliest-expiry deduction & alerts (`SellPage`, `StockPage`, `AlertsPage`) | `MinHeap` (`backend/ds/min_heap.py`) | Sorted by earliest expiry / Scanning expiring batches |
| 1-level transaction void (`HistoryPage`) | `Stack` (`backend/ds/stack.py`) | Undo available only on the latest transaction |
| Restock priority queue (`RestockPage`) | `MaxHeap` (`backend/ds/max_heap.py`) | Priority Queue (ranked by days of cover & selling speed) |
| Daily revenue & COGS totals (`ReportsPage`) | `PrefixSums` (`backend/ds/prefix_sums.py`) | Revenue |
| Fast/slow movers & top/bottom sellers (`RestockPage`, `ReportsPage`) | `SizeKHeap` (`backend/ds/size_k_heap.py`) | Fast Movers / Slow Movers / Best and Worst Sellers |
| Category tracking labels (`SettingsPage`) | `MinHeap` (FEFO vs FIFO key) | Yes (earliest expiry first) / No (oldest received first) |

---

## 📄 License
This project was developed for educational and portfolio demonstration of applied Data Structures and Algorithms in desktop enterprise applications.
