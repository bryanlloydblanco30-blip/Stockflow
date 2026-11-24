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

### 3. Launch the Desktop PC App (Instant Run)
You can launch the complete standalone desktop application with a single click:
- Double-click **`StockFlow.bat`** (or silent launcher **`StockFlow.vbs`**) in the root folder.
- Or directly run the packaged executable at **`dist/StockFlow/StockFlow.exe`**.

> Launches the embedded Python service, serves the built React interface, and opens a dedicated native desktop application window with zero browser URL bars or external dependencies.

### 4. Build the PC Desktop App from Source
To rebuild the standalone Windows desktop executable at any time:
```bash
# Run the automated build script (bundles React dist + PyInstaller .exe)
build_pc_app.bat
```
Or manually:
```bash
cd frontend && npm run build && cd ..
pyinstaller StockFlow.spec --noconfirm
```

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

## 📄 License
This project was developed for educational and portfolio demonstration of applied Data Structures and Algorithms in desktop enterprise applications.
