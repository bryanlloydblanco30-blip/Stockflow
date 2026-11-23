"""
backend/db/schema.py
SQLite schema DDL with version number for migrations (Task 2.2).
"""

SCHEMA_VERSION = 1

CREATE_TABLES_SQL = """
CREATE TABLE IF NOT EXISTS schema_version (
    version INTEGER PRIMARY KEY
);

CREATE TABLE IF NOT EXISTS locations (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    tracks_expiry INTEGER NOT NULL DEFAULT 1,
    warn_days INTEGER NOT NULL DEFAULT 7
);

CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    barcode TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    category_id INTEGER REFERENCES categories(id),
    cost_price REAL NOT NULL,
    selling_price REAL NOT NULL,
    reorder_level INTEGER NOT NULL DEFAULT 0,
    location_id INTEGER REFERENCES locations(id) DEFAULT 1,
    active INTEGER NOT NULL DEFAULT 1
);

CREATE TABLE IF NOT EXISTS batches (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INTEGER NOT NULL REFERENCES products(id),
    quantity INTEGER NOT NULL,
    cost_price REAL NOT NULL,
    received_date TEXT NOT NULL,
    expiry_date TEXT,
    moved_to_front INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    type TEXT NOT NULL,
    date_time TEXT NOT NULL,
    total REAL NOT NULL,
    cash_given REAL NOT NULL,
    change REAL NOT NULL,
    reverses_id INTEGER REFERENCES transactions(id),
    location_id INTEGER REFERENCES locations(id) DEFAULT 1
);

CREATE TABLE IF NOT EXISTS transaction_lines (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    transaction_id INTEGER NOT NULL REFERENCES transactions(id),
    product_id INTEGER NOT NULL REFERENCES products(id),
    batch_id INTEGER NOT NULL REFERENCES batches(id),
    quantity INTEGER NOT NULL,
    price_at_time REAL NOT NULL,
    cost_at_time REAL NOT NULL
);

CREATE TABLE IF NOT EXISTS settings (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
);
"""


def init_schema(conn) -> None:
    """Initializes tables and stamps schema version."""
    with conn:
        conn.executescript(CREATE_TABLES_SQL)
        conn.execute("INSERT OR IGNORE INTO schema_version (version) VALUES (?)", (SCHEMA_VERSION,))
        conn.execute("INSERT OR IGNORE INTO locations (id, name) VALUES (1, 'Main Store');")

