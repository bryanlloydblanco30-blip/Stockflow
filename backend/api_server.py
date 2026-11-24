"""
backend/api_server.py
Lightweight Python stdlib HTTP API server exposing StockFlow backend services
to the React frontend (Decision D18). Zero external dependencies.
"""

from __future__ import annotations

import csv
import json
import math
import mimetypes
import random
import sqlite3
import sys
import threading
from datetime import date, datetime, timedelta
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, Dict, List, Optional
from urllib.parse import parse_qs, urlparse

from backend.db.backup import export_backup, restore_backup
from backend.db.connection import get_db_path
from backend.db.schema import init_schema
from backend.db.storage import StoreMemoryState, load_all_into_memory
from backend.services.alert_service import AlertService
from backend.services.category_service import CategoryService
from backend.services.fefo_service import FEFOService
from backend.services.inventory_service import InventoryService
from backend.services.pos_service import POSService
from backend.services.product_service import ProductService
from backend.services.report_service import ReportService
from backend.services.restock_service import RestockService
from backend.services.undo_service import UndoService

# PyInstaller bundle or standard source root
if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
    ROOT_DIR = Path(sys._MEIPASS)
else:
    ROOT_DIR = Path(__file__).resolve().parent.parent

CSV_SEED_PATH = ROOT_DIR / "data" / "inventory.csv"
BACKUP_DIR = ROOT_DIR / "backups"
DIST_DIR = ROOT_DIR / "frontend" / "dist"
CSV_SEED_PATH = ROOT_DIR / "data" / "inventory.csv"
BACKUP_DIR = ROOT_DIR / "backups"

CATEGORY_WARN_DAYS = {
    "Bakery": 7,
    "Dairy & Chilled": 7,
    "Dairy": 7,
    "Beverages": 14,
    "Canned Goods": 30,
    "Instant Noodles": 30,
    "Snacks": 14,
    "Condiments": 30,
    "Personal Care": 0,
    "Household": 0,
    "School Supplies": 0,
}


def _safe_float(val: float) -> Optional[float]:
    if math.isinf(val) or math.isnan(val):
        return None
    return val


class StockFlowBackend:
    """Thread-safe container wiring SQLite, StoreMemoryState, and all domain services."""

    def __init__(self, db_path: Optional[Path | str] = None, auto_seed: bool = True):
        self.db_path = Path(db_path) if db_path else get_db_path()
        self.lock = threading.RLock()
        self.conn = self._open_connection(self.db_path)
        init_schema(self.conn)
        self._init_services()
        if auto_seed and len(self.state.products) == 0 and CSV_SEED_PATH.is_file():
            self._seed_from_csv(CSV_SEED_PATH)
        if auto_seed and len(self.state.products) > 0:
            cur = self.conn.cursor()
            cur.execute("SELECT COUNT(*) FROM transactions;")
            if (cur.fetchone() or [0])[0] == 0:
                self._seed_sample_transactions()

    @staticmethod
    def _open_connection(path: Path) -> sqlite3.Connection:
        conn = sqlite3.connect(str(path), timeout=30.0, check_same_thread=False)
        conn.execute("PRAGMA foreign_keys = ON;")
        conn.execute("PRAGMA journal_mode = WAL;")
        return conn

    def _init_services(self) -> None:
        self.state: StoreMemoryState = load_all_into_memory(self.conn)
        self.alert_service = AlertService()
        self.category_service = CategoryService(self.conn, self.state)
        self.product_service = ProductService(self.conn, self.state)
        self.inventory_service = InventoryService(self.conn, self.state, self.alert_service)
        self.fefo_service = FEFOService(self.alert_service)
        self.pos_service = POSService(self.conn, self.state, self.fefo_service)
        self.undo_service = UndoService(self.conn, self.state, self.pos_service.undo_stack)
        self.restock_service = RestockService(self.conn, self.state, self.alert_service)
        self.report_service = ReportService(self.conn, self.state, self.alert_service)

    def reload_from_disk(self) -> None:
        with self.lock:
            self.conn.close()
            self.conn = self._open_connection(self.db_path)
            init_schema(self.conn)
            self._init_services()

    def _seed_from_csv(self, csv_path: Path) -> None:
        """Seeds initial sample data from data/inventory.csv on first run."""
        cat_map: Dict[str, int] = {}
        with csv_path.open("r", encoding="utf-8-sig", newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                cat_name = (row.get("category") or "").strip()
                tracks = (row.get("tracks_expiry") or "TRUE").strip().upper() == "TRUE"
                cat_id: Optional[int] = None
                if cat_name:
                    if cat_name not in cat_map:
                        warn_days = CATEGORY_WARN_DAYS.get(cat_name, 7 if tracks else 0)
                        cat = self.category_service.add_category(
                            name=cat_name,
                            tracks_expiry=tracks,
                            warn_days=warn_days,
                        )
                        cat_map[cat_name] = cat.id
                    cat_id = cat_map[cat_name]

                barcode = (row.get("barcode") or "").strip()
                name = (row.get("product_name") or "").strip()
                if not barcode or not name:
                    continue
                if self.product_service.find_by_barcode(barcode) is not None:
                    continue

                cost = float(row.get("cost_price") or 0)
                price = float(row.get("selling_price") or 0)
                reorder = int(float(row.get("reorder_level") or 0))
                stock = int(float(row.get("current_stock") or 0))
                rec_date = (row.get("received_date") or date.today().isoformat()).strip()
                exp_raw = (row.get("expiry_date") or "").strip()
                exp_date = exp_raw if (tracks and exp_raw) else None

                prod = self.product_service.register_product(
                    barcode=barcode,
                    name=name,
                    cost=cost,
                    price=price,
                    category_id=cat_id,
                    reorder_level=reorder,
                )
                if stock > 0:
                    self.inventory_service.receive_stock(
                        product_id=prod.id,
                        quantity=stock,
                        cost=cost,
                        expiry_date=exp_date,
                        received_date=rec_date,
                    )

        # Ensure default settings exist
        with self.conn:
            self.conn.execute(
                "INSERT OR IGNORE INTO settings (key, value) VALUES ('store_name', 'StockFlow Sample Store');"
            )
            self.conn.execute(
                "INSERT OR IGNORE INTO settings (key, value) VALUES ('default_warn_days', '7');"
            )
            self.conn.execute(
                "INSERT OR IGNORE INTO settings (key, value) VALUES ('target_cover_days', '14');"
            )

    def _seed_sample_transactions(self) -> None:
        """
        Generates deterministic sample sales, adjustments, spoilage write-offs, and a void
        over the past 30 days (seed=42) so Reports, Dashboard, Restock velocity, and History
        populate immediately with sample data.
        """
        rng = random.Random(42)
        today = date.today()

        # Collect active products that have at least one batch
        candidates = []
        for prod in self.state.products:
            if not prod.active:
                continue
            heap = self.state.get_product_heap(prod.id)
            if not heap or heap.is_empty():
                continue
            first_batch = heap.peek_min()
            candidates.append((prod, first_batch))

        if not candidates:
            return

        # Weight early products higher so Top-k / Bottom-k movers show clear contrast
        weights = [max(1, 25 - (i % 24)) for i in range(len(candidates))]

        with self.conn:
            cur = self.conn.cursor()

            # 1. Generate 30 days of sample sales (including today)
            for days_ago in range(29, -1, -1):
                sale_day = today - timedelta(days=days_ago)
                tx_count = rng.randint(4, 8) if days_ago > 0 else 5
                for t_idx in range(tx_count):
                    hour = 8 + (t_idx * 2) % 12
                    minute = rng.randint(0, 59)
                    dt_str = f"{sale_day.isoformat()} {hour:02d}:{minute:02d}:00"

                    num_lines = rng.randint(1, 4)
                    picked = rng.choices(candidates, weights=weights, k=num_lines)
                    # Deduplicate products within a single receipt
                    unique_picked = []
                    seen_p = set()
                    for p, b in picked:
                        if p.id not in seen_p:
                            seen_p.add(p.id)
                            unique_picked.append((p, b))

                    lines_data = []
                    total = 0.0
                    for p, b in unique_picked:
                        qty = rng.randint(1, 4)
                        total += qty * p.selling_price
                        lines_data.append((p.id, b.id, qty, p.selling_price, b.cost_price))

                    total = round(total, 2)
                    cash = float(math.ceil(total / 50.0) * 50)
                    change = round(cash - total, 2)

                    cur.execute("""
                        INSERT INTO transactions (type, date_time, total, cash_given, change, reverses_id, location_id)
                        VALUES ('sale', ?, ?, ?, ?, NULL, 1);
                    """, (dt_str, total, cash, change))
                    tx_id = cur.lastrowid

                    for pid, bid, qty, price, cost in lines_data:
                        cur.execute("""
                            INSERT INTO transaction_lines (transaction_id, product_id, batch_id, quantity, price_at_time, cost_at_time)
                            VALUES (?, ?, ?, ?, ?, ?);
                        """, (tx_id, pid, bid, qty, price, cost))

            # 2. Sample voided sale (excluded from financial totals)
            v_prod, v_batch = candidates[0]
            v_day = (today - timedelta(days=2)).isoformat()
            v_total = round(v_prod.selling_price * 2, 2)
            cur.execute("""
                INSERT INTO transactions (type, date_time, total, cash_given, change, reverses_id, location_id)
                VALUES ('sale', ?, ?, ?, 0.0, NULL, 1);
            """, (f"{v_day} 11:15:00", v_total, v_total))
            orig_id = cur.lastrowid
            cur.execute("""
                INSERT INTO transaction_lines (transaction_id, product_id, batch_id, quantity, price_at_time, cost_at_time)
                VALUES (?, ?, ?, 2, ?, ?);
            """, (orig_id, v_prod.id, v_batch.id, v_prod.selling_price, v_batch.cost_price))
            cur.execute("""
                INSERT INTO transactions (type, date_time, total, cash_given, change, reverses_id, location_id)
                VALUES ('void', ?, ?, 0.0, 0.0, ?, 1);
            """, (f"{v_day} 11:18:00", v_total, orig_id))

            # 3. Sample spoilage write-offs (perishable items only)
            perishables = [(p, b) for p, b in candidates if b.expiry_date]
            for idx, (p, b) in enumerate(perishables[:3]):
                w_day = (today - timedelta(days=3 + idx * 4)).isoformat()
                qty = rng.randint(2, 5)
                loss = round(qty * b.cost_price, 2)
                cur.execute("""
                    INSERT INTO transactions (type, date_time, total, cash_given, change, reverses_id, location_id)
                    VALUES ('writeoff', ?, ?, 0.0, 0.0, NULL, 1);
                """, (f"{w_day} 17:30:00", loss))
                w_tx_id = cur.lastrowid
                cur.execute("""
                    INSERT INTO transaction_lines (transaction_id, product_id, batch_id, quantity, price_at_time, cost_at_time)
                    VALUES (?, ?, ?, ?, 0.0, ?);
                """, (w_tx_id, p.id, b.id, qty, b.cost_price))

            # 4. Sample stock adjustments
            for idx, (p, b) in enumerate(candidates[1:3]):
                a_day = (today - timedelta(days=1 + idx * 3)).isoformat()
                diff = -2 if idx == 0 else 3
                cur.execute("""
                    INSERT INTO transactions (type, date_time, total, cash_given, change, reverses_id, location_id)
                    VALUES ('adjustment', ?, ?, 0.0, 0.0, NULL, 1);
                """, (f"{a_day} 09:05:00", round(diff * b.cost_price, 2)))
                a_tx_id = cur.lastrowid
                cur.execute("""
                    INSERT INTO transaction_lines (transaction_id, product_id, batch_id, quantity, price_at_time, cost_at_time)
                    VALUES (?, ?, ?, ?, 0.0, ?);
                """, (a_tx_id, p.id, b.id, diff, b.cost_price))

    def _serialize_product(self, prod, today: Optional[date] = None) -> Dict[str, Any]:
        curr_date = today or date.today()
        cat = self.state.get_category_by_id(prod.category_id) if prod.category_id else None
        tracks_expiry = cat.tracks_expiry if cat else True
        warn_days = cat.warn_days if cat else 7
        heap = self.state.get_or_create_product_heap(prod.id)

        batches_out: List[Dict[str, Any]] = []
        sellable_stock = 0
        expired_stock = 0
        worst_level = "NO_EXPIRY" if not tracks_expiry else "OK"
        level_rank = {"NO_EXPIRY": 0, "OK": 1, "AMBER": 2, "RED": 3, "EXPIRED": 4}
        earliest_expiry: Optional[str] = None

        for b in heap.ordered_read():
            if b.quantity <= 0:
                continue
            if tracks_expiry and b.expiry_date:
                lvl = self.alert_service.calculate_level(b.expiry_date, warn_days, curr_date)
                sellable = self.alert_service.is_sellable(b.expiry_date, curr_date)
                if earliest_expiry is None or b.expiry_date < earliest_expiry:
                    earliest_expiry = b.expiry_date
            elif tracks_expiry and not b.expiry_date:
                lvl = "NEEDS_EXPIRY"
                sellable = True
            else:
                lvl = "NO_EXPIRY"
                sellable = True

            if sellable:
                sellable_stock += b.quantity
            else:
                expired_stock += b.quantity

            if lvl in level_rank and level_rank[lvl] > level_rank.get(worst_level, 0):
                worst_level = lvl

            batches_out.append({
                "id": b.id,
                "product_id": b.product_id,
                "quantity": b.quantity,
                "cost_price": b.cost_price,
                "received_date": b.received_date,
                "expiry_date": b.expiry_date,
                "moved_to_front": b.moved_to_front,
                "level": lvl,
                "is_sellable": sellable,
            })

        is_low = sellable_stock < prod.reorder_level
        if worst_level == "EXPIRED":
            status_label = "Expired"
        elif worst_level == "RED":
            status_label = "Expires soon"
        elif worst_level == "AMBER":
            status_label = "Near expiry"
        elif not tracks_expiry:
            status_label = "Low" if is_low else "Untracked"
        elif is_low:
            status_label = "Low"
        else:
            status_label = "OK"

        return {
            "id": prod.id,
            "barcode": prod.barcode,
            "name": prod.name,
            "category_id": prod.category_id,
            "category_name": cat.name if cat else "Uncategorized",
            "tracks_expiry": tracks_expiry,
            "warn_days": warn_days,
            "cost_price": prod.cost_price,
            "selling_price": prod.selling_price,
            "reorder_level": prod.reorder_level,
            "sellable_stock": sellable_stock,
            "expired_stock": expired_stock,
            "is_low_stock": is_low,
            "earliest_expiry": earliest_expiry,
            "alert_level": worst_level,
            "status_label": status_label,
            "batches": batches_out,
        }

    # --- Endpoint Handlers ---

    def get_dashboard(self) -> Dict[str, Any]:
        with self.lock:
            today = date.today()
            kpis = self.report_service.get_dashboard_kpis(today=today)
            attention: List[Dict[str, Any]] = []

            for prod in self.state.products:
                if not prod.active:
                    continue
                p_data = self._serialize_product(prod, today=today)
                if p_data["alert_level"] in ("EXPIRED", "RED", "AMBER"):
                    exp = p_data["earliest_expiry"]
                    days_left = (date.fromisoformat(exp) - today).days if exp else 0
                    issue = (
                        f"Expired {abs(days_left)} day(s) ago"
                        if days_left < 0
                        else ("Expires today" if days_left == 0 else f"Expires in {days_left} day(s)")
                    )
                    urgency = "Expired" if p_data["alert_level"] == "EXPIRED" else (
                        "Red" if p_data["alert_level"] == "RED" else "Amber"
                    )
                    color = "red" if urgency in ("Expired", "Red") else "amber"
                    attention.append({
                        "product_id": prod.id,
                        "product_name": prod.name,
                        "issue": issue,
                        "urgency": urgency,
                        "color": color,
                        "priority": 0 if urgency == "Expired" else (1 if urgency == "Red" else 2),
                    })
                elif p_data["is_low_stock"]:
                    attention.append({
                        "product_id": prod.id,
                        "product_name": prod.name,
                        "issue": f"{p_data['sellable_stock']} units left (reorder at {prod.reorder_level})",
                        "urgency": "Low",
                        "color": "amber",
                        "priority": 3,
                    })

            attention.sort(key=lambda x: (x["priority"], x["product_name"]))
            return {
                "kpis": kpis,
                "attention": attention[:12],
                "today": today.isoformat(),
            }

    def get_categories(self) -> List[Dict[str, Any]]:
        with self.lock:
            out = []
            for c in self.state.categories:
                red_days = max(1, round(c.warn_days / 3)) if (c.tracks_expiry and c.warn_days > 0) else 0
                out.append({
                    "id": c.id,
                    "name": c.name,
                    "tracks_expiry": c.tracks_expiry,
                    "warn_days": c.warn_days,
                    "red_days": red_days,
                })
            return out

    def create_category(self, body: Dict[str, Any]) -> Dict[str, Any]:
        with self.lock:
            name = str(body.get("name", "")).strip()
            if not name:
                raise ValueError("Category name is required.")
            tracks = bool(body.get("tracks_expiry", True))
            warn_days = int(body.get("warn_days", 7))
            cat = self.category_service.add_category(name=name, tracks_expiry=tracks, warn_days=warn_days)
            return {
                "id": cat.id,
                "name": cat.name,
                "tracks_expiry": cat.tracks_expiry,
                "warn_days": cat.warn_days,
            }

    def update_category(self, category_id: int, body: Dict[str, Any]) -> Dict[str, Any]:
        with self.lock:
            cat = None
            if "name" in body and str(body["name"]).strip():
                cat = self.category_service.rename_category(category_id, str(body["name"]))
            if "tracks_expiry" in body or "warn_days" in body:
                existing = self.state.get_category_by_id(category_id)
                if not existing:
                    raise ValueError("Category not found.")
                tracks = bool(body.get("tracks_expiry", existing.tracks_expiry))
                warn_days = int(body.get("warn_days", existing.warn_days or 7))
                cat = self.category_service.toggle_tracking(category_id, tracks, warn_days)
            if not cat:
                raise ValueError("Category not found.")
            return {
                "id": cat.id,
                "name": cat.name,
                "tracks_expiry": cat.tracks_expiry,
                "warn_days": cat.warn_days,
            }

    def delete_category(self, category_id: int) -> Dict[str, Any]:
        with self.lock:
            affected = self.category_service.delete_category(category_id)
            return {"deleted_id": category_id, "affected_products": affected}

    def get_products(self) -> List[Dict[str, Any]]:
        with self.lock:
            today = date.today()
            return [
                self._serialize_product(p, today=today)
                for p in self.state.products
                if p.active
            ]

    def search_products(self, q: str) -> List[Dict[str, Any]]:
        with self.lock:
            today = date.today()
            clean = q.strip()
            if not clean:
                return []
            results = []
            seen_ids = set()
            by_code = self.product_service.find_by_barcode(clean)
            if by_code and by_code.active:
                results.append(self._serialize_product(by_code, today=today))
                seen_ids.add(by_code.id)
            for p in self.product_service.search_by_name_prefix(clean, limit=8):
                if p.active and p.id not in seen_ids:
                    results.append(self._serialize_product(p, today=today))
                    seen_ids.add(p.id)
            return results

    def create_product(self, body: Dict[str, Any]) -> Dict[str, Any]:
        with self.lock:
            barcode = str(body.get("barcode", "")).strip()
            name = str(body.get("name", "")).strip()
            if not barcode or not name:
                raise ValueError("Barcode and product name are required.")
            cost = float(body.get("cost_price", 0))
            price = float(body.get("selling_price", 0))
            reorder = int(body.get("reorder_level", 0))
            cat_id = body.get("category_id")
            if cat_id is not None and cat_id != "":
                cat_id = int(cat_id)
            else:
                cat_id = None

            prod = self.product_service.register_product(
                barcode=barcode,
                name=name,
                cost=cost,
                price=price,
                category_id=cat_id,
                reorder_level=reorder,
            )

            initial_qty = int(body.get("initial_stock", 0) or 0)
            expiry_date = (body.get("expiry_date") or "").strip() or None
            if initial_qty > 0:
                cat = self.state.get_category_by_id(cat_id) if cat_id else None
                if cat and not cat.tracks_expiry:
                    expiry_date = None
                self.inventory_service.receive_stock(
                    product_id=prod.id,
                    quantity=initial_qty,
                    cost=cost,
                    expiry_date=expiry_date,
                )

            return self._serialize_product(prod)

    def scan_barcode(self, barcode: str) -> Dict[str, Any]:
        with self.lock:
            res = self.pos_service.process_barcode_entry(barcode.strip())
            if res["status"] == "FOUND":
                return {
                    "status": "FOUND",
                    "product": self._serialize_product(res["product"]),
                }
            return {"status": "UNKNOWN", "barcode": barcode.strip()}

    def get_cart(self) -> Dict[str, Any]:
        with self.lock:
            lines = []
            for item in self.pos_service.cart.traverse():
                prod = self.state.get_product_by_id(item.product_id)
                p_data = self._serialize_product(prod) if prod else None
                lines.append({
                    "product_id": item.product_id,
                    "barcode": prod.barcode if prod else "",
                    "product_name": item.product_name,
                    "unit_price": item.unit_price,
                    "quantity": item.quantity,
                    "subtotal": round(item.unit_price * item.quantity, 2),
                    "sellable_stock": p_data["sellable_stock"] if p_data else 0,
                })
            return {
                "lines": lines,
                "item_count": sum(l["quantity"] for l in lines),
                "total": self.pos_service.get_cart_total(),
            }

    def add_to_cart(self, body: Dict[str, Any]) -> Dict[str, Any]:
        with self.lock:
            qty = int(body.get("quantity", 1))
            product_id = body.get("product_id")
            barcode = body.get("barcode")
            if product_id is None and barcode:
                scan = self.pos_service.process_barcode_entry(str(barcode).strip())
                if scan["status"] != "FOUND":
                    return {"status": "UNKNOWN", "barcode": str(barcode).strip(), "cart": self.get_cart()}
                product_id = scan["product"].id
            if product_id is None:
                raise ValueError("product_id or barcode is required.")

            prod = self.state.get_product_by_id(int(product_id))
            if not prod:
                raise ValueError("Product not found.")
            p_data = self._serialize_product(prod)
            existing = self.pos_service.cart.find(lambda i: i.product_id == prod.id)
            current_in_cart = existing.quantity if existing else 0
            if p_data["sellable_stock"] <= 0:
                raise ValueError(f'"{prod.name}" has no sellable stock (expired or out of stock).')
            if current_in_cart + qty > p_data["sellable_stock"]:
                raise ValueError(
                    f'Only {p_data["sellable_stock"]} sellable units of "{prod.name}" available.'
                )

            self.pos_service.add_to_cart(prod.id, qty)
            return {"status": "OK", "product": p_data, "cart": self.get_cart()}

    def update_cart_item(self, product_id: int, body: Dict[str, Any]) -> Dict[str, Any]:
        with self.lock:
            qty = int(body.get("quantity", 0))
            if qty > 0:
                prod = self.state.get_product_by_id(product_id)
                if prod:
                    p_data = self._serialize_product(prod)
                    if qty > p_data["sellable_stock"]:
                        raise ValueError(f'Only {p_data["sellable_stock"]} sellable units available.')
            self.pos_service.update_cart_quantity(product_id, qty)
            return self.get_cart()

    def remove_cart_item(self, product_id: int) -> Dict[str, Any]:
        with self.lock:
            self.pos_service.remove_from_cart(product_id)
            return self.get_cart()

    def clear_cart(self) -> Dict[str, Any]:
        with self.lock:
            self.pos_service.clear_cart()
            return self.get_cart()

    def checkout(self, body: Dict[str, Any]) -> Dict[str, Any]:
        with self.lock:
            cash_given = float(body.get("cash_given", 0))
            receipt = self.pos_service.checkout(cash_given=cash_given)
            return receipt

    def receive_stock(self, body: Dict[str, Any]) -> Dict[str, Any]:
        with self.lock:
            product_id = int(body["product_id"])
            quantity = int(body["quantity"])
            if quantity <= 0:
                raise ValueError("Quantity must be greater than zero.")
            prod = self.state.get_product_by_id(product_id)
            if not prod:
                raise ValueError("Product not found.")
            cost = float(body.get("cost_price", prod.cost_price))
            cat = self.state.get_category_by_id(prod.category_id) if prod.category_id else None
            expiry_date = (body.get("expiry_date") or "").strip() or None
            if cat and not cat.tracks_expiry:
                expiry_date = None
            res = self.inventory_service.receive_stock(
                product_id=product_id,
                quantity=quantity,
                cost=cost,
                expiry_date=expiry_date,
            )
            return {
                "batch": {
                    "id": res.batch.id,
                    "product_id": res.batch.product_id,
                    "quantity": res.batch.quantity,
                    "cost_price": res.batch.cost_price,
                    "received_date": res.batch.received_date,
                    "expiry_date": res.batch.expiry_date,
                },
                "older_batches_warning": res.older_batches_warning,
            }

    def adjust_stock(self, body: Dict[str, Any]) -> Dict[str, Any]:
        with self.lock:
            batch_id = int(body["batch_id"])
            new_qty = int(body["new_quantity"])
            reason = str(body.get("reason", "")).strip()
            if not reason:
                raise ValueError("Reason is required for stock adjustment.")
            if new_qty < 0:
                raise ValueError("New quantity cannot be negative.")
            return self.inventory_service.adjust_stock(batch_id, new_qty, reason)

    def write_off_expired(self, body: Dict[str, Any]) -> Dict[str, Any]:
        with self.lock:
            batch_id = int(body["batch_id"])
            reason = str(body.get("reason", "Expired on shelf")).strip() or "Expired on shelf"
            return self.inventory_service.write_off_expired(batch_id, reason)

    def mark_shelf_rotated(self, body: Dict[str, Any]) -> Dict[str, Any]:
        with self.lock:
            batch_id = int(body["batch_id"])
            ok = self.inventory_service.mark_shelf_rotated(batch_id)
            return {"batch_id": batch_id, "moved_to_front": ok}

    def get_alerts(self) -> Dict[str, Any]:
        with self.lock:
            today = date.today()
            near_expiry: List[Dict[str, Any]] = []
            expired: List[Dict[str, Any]] = []
            checklist: List[Dict[str, Any]] = []

            for prod in self.state.products:
                if not prod.active:
                    continue
                cat = self.state.get_category_by_id(prod.category_id) if prod.category_id else None
                if cat is not None and not cat.tracks_expiry:
                    continue
                warn_days = cat.warn_days if cat else 7
                heap = self.state.get_or_create_product_heap(prod.id)
                for b in heap.ordered_read():
                    if b.quantity <= 0 or not b.expiry_date:
                        continue
                    lvl = self.alert_service.calculate_level(b.expiry_date, warn_days, today)
                    days_left = (date.fromisoformat(b.expiry_date) - today).days
                    row = {
                        "batch_id": b.id,
                        "product_id": prod.id,
                        "product_name": prod.name,
                        "barcode": prod.barcode,
                        "category_name": cat.name if cat else "Uncategorized",
                        "quantity": b.quantity,
                        "cost_price": b.cost_price,
                        "loss_value": round(b.quantity * b.cost_price, 2),
                        "received_date": b.received_date,
                        "expiry_date": b.expiry_date,
                        "days_left": days_left,
                        "level": lvl,
                        "moved_to_front": b.moved_to_front,
                    }
                    if lvl == "EXPIRED":
                        expired.append(row)
                    elif lvl in ("RED", "AMBER"):
                        near_expiry.append(row)
                        checklist.append(row)
                    elif lvl == "OK":
                        break

            unresolved = self.inventory_service.get_unresolved_expiry_batches()
            return {
                "near_expiry": near_expiry,
                "expired": expired,
                "checklist": checklist,
                "unresolved_expiry": unresolved,
            }

    def get_restock(self) -> Dict[str, Any]:
        with self.lock:
            today = date.today()
            target_days = int(self._get_setting("target_cover_days", "14"))
            raw_queue = self.restock_service.build_restock_queue(
                target_cover_days=target_days,
                today=today,
            )
            queue = []
            for idx, item in enumerate(raw_queue):
                prod = self.state.get_product_by_id(item["product_id"])
                cat = self.state.get_category_by_id(prod.category_id) if (prod and prod.category_id) else None
                cover = _safe_float(item["days_of_cover"])
                stock = item["sellable_stock"]
                reorder_lvl = prod.reorder_level if prod else 0
                if stock == 0 or stock < reorder_lvl or (cover is not None and cover <= 3):
                    urgency = "Urgent"
                    color = "red"
                elif cover is not None and cover <= 7:
                    urgency = "Soon"
                    color = "amber"
                else:
                    urgency = "OK"
                    color = "green"
                queue.append({
                    **item,
                    "rank": idx + 1,
                    "days_of_cover": cover,
                    "category_name": cat.name if cat else "Uncategorized",
                    "cost_price": prod.cost_price if prod else 0.0,
                    "reorder_level": reorder_lvl,
                    "tracks_expiry": cat.tracks_expiry if cat else True,
                    "urgency": urgency,
                    "color": color,
                })
            return {
                "target_cover_days": target_days,
                "queue": queue,
                "top_sellers": self.report_service.get_top_sellers(k=10, metric="units"),
                "bottom_sellers": self.report_service.get_bottom_sellers(k=10, metric="units"),
            }

    def get_reports(self, period: str = "Week", start_str: Optional[str] = None, end_str: Optional[str] = None) -> Dict[str, Any]:
        with self.lock:
            today = date.today()
            if period == "Day":
                start_date, end_date = today, today
            elif period == "Month":
                start_date, end_date = today - timedelta(days=29), today
            elif period == "Custom" and start_str and end_str:
                start_date = date.fromisoformat(start_str)
                end_date = date.fromisoformat(end_str)
            else:
                start_date, end_date = today - timedelta(days=6), today

            summary = self.report_service.get_financial_summary(
                start_date=start_date,
                end_date=end_date,
                today=today,
            )
            prefix = self.report_service.build_daily_prefix_sums(start_date, end_date)
            total_days = (end_date - start_date).days + 1
            daily_series = []
            for i in range(total_days):
                d = start_date + timedelta(days=i)
                rev = round(prefix["revenue"].range_sum(i, i), 2)
                cogs = round(prefix["cogs"].range_sum(i, i), 2)
                units = int(prefix["units"].range_sum(i, i))
                daily_series.append({
                    "date": d.isoformat(),
                    "label": d.strftime("%d %b"),
                    "revenue": rev,
                    "cogs": cogs,
                    "profit": round(rev - cogs, 2),
                    "units": units,
                })

            top_sellers = self.report_service.get_top_sellers(k=5, metric="units")
            bottom_sellers = self.report_service.get_bottom_sellers(k=5, metric="units")

            # Profit per item
            cur = self.conn.cursor()
            cur.execute("""
                SELECT p.id, p.name, p.cost_price, p.selling_price,
                       COALESCE(SUM(tl.quantity), 0) AS qty_sold,
                       COALESCE(SUM(tl.quantity * tl.price_at_time), 0.0) AS rev,
                       COALESCE(SUM(tl.quantity * tl.cost_at_time), 0.0) AS cogs
                FROM transaction_lines tl
                JOIN transactions t ON tl.transaction_id = t.id
                JOIN products p ON tl.product_id = p.id
                WHERE t.type = 'sale'
                  AND DATE(t.date_time) >= ? AND DATE(t.date_time) <= ?
                  AND NOT EXISTS (
                      SELECT 1 FROM transactions v WHERE v.type = 'void' AND v.reverses_id = t.id
                  )
                GROUP BY p.id, p.name, p.cost_price, p.selling_price
                ORDER BY (rev - cogs) DESC;
            """, (start_date.isoformat(), end_date.isoformat()))
            profit_per_item = []
            for r in cur.fetchall():
                rev_v, cogs_v = round(r[5], 2), round(r[6], 2)
                prof_v = round(rev_v - cogs_v, 2)
                margin_v = round((prof_v / rev_v) * 100.0, 1) if rev_v > 0 else 0.0
                profit_per_item.append({
                    "product_id": r[0],
                    "product_name": r[1],
                    "cost_price": r[2],
                    "selling_price": r[3],
                    "units_sold": r[4],
                    "revenue": rev_v,
                    "total_profit": prof_v,
                    "margin_pct": margin_v,
                })

            # Spoilage rows
            cur.execute("""
                SELECT tl.batch_id, p.name, COALESCE(c.name, 'Uncategorized'),
                       tl.quantity, tl.cost_at_time, t.date_time
                FROM transaction_lines tl
                JOIN transactions t ON tl.transaction_id = t.id
                JOIN products p ON tl.product_id = p.id
                LEFT JOIN categories c ON p.category_id = c.id
                WHERE t.type IN ('writeoff', 'write-off')
                  AND DATE(t.date_time) >= ? AND DATE(t.date_time) <= ?
                ORDER BY t.id DESC;
            """, (start_date.isoformat(), end_date.isoformat()))
            spoilage_items = [
                {
                    "batch_id": r[0],
                    "product_name": r[1],
                    "category_name": r[2],
                    "quantity": r[3],
                    "unit_cost": r[4],
                    "total_loss": round(r[3] * r[4], 2),
                    "date_time": r[5],
                }
                for r in cur.fetchall()
            ]

            # Inventory valuation by category
            cat_val: Dict[str, Dict[str, Any]] = {}
            total_retail = 0.0
            total_cost = 0.0
            for prod in self.state.products:
                if not prod.active:
                    continue
                p_data = self._serialize_product(prod, today=today)
                cname = p_data["category_name"]
                if cname not in cat_val:
                    cat_val[cname] = {"category": cname, "units": 0, "cost_value": 0.0, "retail_value": 0.0}
                for b in p_data["batches"]:
                    if b["is_sellable"]:
                        c_val = b["quantity"] * b["cost_price"]
                        r_val = b["quantity"] * prod.selling_price
                        cat_val[cname]["units"] += b["quantity"]
                        cat_val[cname]["cost_value"] = round(cat_val[cname]["cost_value"] + c_val, 2)
                        cat_val[cname]["retail_value"] = round(cat_val[cname]["retail_value"] + r_val, 2)
                        total_cost += c_val
                        total_retail += r_val

            valuation_by_category = []
            for cv in cat_val.values():
                m = round(((cv["retail_value"] - cv["cost_value"]) / cv["retail_value"]) * 100.0, 1) if cv["retail_value"] > 0 else 0.0
                valuation_by_category.append({**cv, "margin_pct": m})

            return {
                "period": period,
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "summary": summary,
                "daily_series": daily_series,
                "top_sellers": top_sellers,
                "bottom_sellers": bottom_sellers,
                "profit_per_item": profit_per_item,
                "spoilage_items": spoilage_items,
                "inventory_valuation": {
                    "total_cost_value": round(total_cost, 2),
                    "total_retail_value": round(total_retail, 2),
                    "potential_profit": round(total_retail - total_cost, 2),
                    "by_category": valuation_by_category,
                },
            }

    def get_transactions(self, tx_type: Optional[str] = None) -> Dict[str, Any]:
        with self.lock:
            cur = self.conn.cursor()
            cur.execute("SELECT MAX(id) FROM transactions;")
            max_id_row = cur.fetchone()
            latest_id = max_id_row[0] if max_id_row and max_id_row[0] is not None else 0

            can_undo_id = None
            if not self.pos_service.undo_stack.is_empty():
                top_tx = self.pos_service.undo_stack.peek()["transaction"]
                if top_tx.id == latest_id:
                    can_undo_id = top_tx.id

            query = """
                SELECT t.id, t.type, t.date_time, t.total, t.cash_given, t.change, t.reverses_id
                FROM transactions t
            """
            params: List[Any] = []
            if tx_type and tx_type.lower() != "all":
                query += " WHERE LOWER(t.type) = ?"
                params.append(tx_type.lower())
            query += " ORDER BY t.id DESC LIMIT 200;"

            cur.execute(query, params)
            rows = cur.fetchall()
            out = []
            for r in rows:
                tid = r[0]
                cur.execute("""
                    SELECT p.name, tl.quantity, tl.price_at_time
                    FROM transaction_lines tl
                    JOIN products p ON tl.product_id = p.id
                    WHERE tl.transaction_id = ?;
                """, (tid,))
                lines = cur.fetchall()
                if r[1] == "void":
                    details = f"Voided transaction #{r[6]}"
                elif len(lines) == 1:
                    details = f"{lines[0][0]} × {lines[0][1]}"
                elif len(lines) > 1:
                    total_qty = sum(abs(l[1]) for l in lines)
                    details = f"{len(lines)} products ({total_qty} units)"
                else:
                    details = f"Transaction #{tid}"

                out.append({
                    "id": tid,
                    "type": r[1],
                    "date_time": r[2],
                    "total": round(r[3], 2),
                    "cash_given": round(r[4], 2),
                    "change": round(r[5], 2),
                    "reverses_id": r[6],
                    "details": details,
                    "can_undo": tid == can_undo_id,
                })
            return {"transactions": out, "can_undo_id": can_undo_id}

    def undo_last(self) -> Dict[str, Any]:
        with self.lock:
            void_tx = self.undo_service.void_last_transaction()
            return {
                "void_transaction_id": void_tx.id,
                "reverses_id": void_tx.reverses_id,
                "total": void_tx.total,
                "date_time": void_tx.date_time,
            }

    def _get_setting(self, key: str, default: str = "") -> str:
        cur = self.conn.cursor()
        cur.execute("SELECT value FROM settings WHERE key = ?;", (key,))
        row = cur.fetchone()
        return row[0] if row else default

    def get_settings(self) -> Dict[str, Any]:
        with self.lock:
            return {
                "store_name": self._get_setting("store_name", "StockFlow Store"),
                "default_warn_days": int(self._get_setting("default_warn_days", "7")),
                "target_cover_days": int(self._get_setting("target_cover_days", "14")),
                "db_path": str(self.db_path),
            }

    def update_settings(self, body: Dict[str, Any]) -> Dict[str, Any]:
        with self.lock:
            with self.conn:
                for key in ("store_name", "default_warn_days", "target_cover_days"):
                    if key in body:
                        self.conn.execute(
                            "INSERT INTO settings (key, value) VALUES (?, ?) "
                            "ON CONFLICT(key) DO UPDATE SET value = excluded.value;",
                            (key, str(body[key])),
                        )
            return self.get_settings()

    def export_db_backup(self) -> Dict[str, Any]:
        with self.lock:
            BACKUP_DIR.mkdir(parents=True, exist_ok=True)
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            dest = BACKUP_DIR / f"stockflow_backup_{ts}.db"
            self.conn.commit()
            export_backup(self.db_path, dest)
            return {
                "filename": dest.name,
                "path": str(dest),
                "size_bytes": dest.stat().st_size,
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }

    def list_backups(self) -> List[Dict[str, Any]]:
        if not BACKUP_DIR.exists():
            return []
        files = sorted(BACKUP_DIR.glob("*.db"), key=lambda p: p.stat().st_mtime, reverse=True)
        return [
            {
                "filename": f.name,
                "path": str(f),
                "size_bytes": f.stat().st_size,
                "modified_at": datetime.fromtimestamp(f.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
            }
            for f in files
        ]

    def restore_db_backup(self, body: Dict[str, Any]) -> Dict[str, Any]:
        with self.lock:
            filename = str(body.get("filename", "")).strip()
            if not filename or "/" in filename or "\\" in filename:
                raise ValueError("Invalid backup filename.")
            src = BACKUP_DIR / filename
            if not src.is_file():
                raise ValueError(f"Backup file '{filename}' not found.")
            self.conn.close()
            restore_backup(src, self.db_path)
            self.conn = self._open_connection(self.db_path)
            init_schema(self.conn)
            self._init_services()
            return {"restored": filename, "products_loaded": len(self.state.products)}


def make_handler(backend: StockFlowBackend):
    class StockFlowHandler(BaseHTTPRequestHandler):
        def log_message(self, format: str, *args: Any) -> None:
            pass  # keep terminal clean

        def _send_json(self, status: int, payload: Any) -> None:
            raw = json.dumps(payload).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(raw)))
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
            self.send_header("Access-Control-Allow-Headers", "Content-Type")
            self.end_headers()
            self.wfile.write(raw)

        def _read_json(self) -> Dict[str, Any]:
            length = int(self.headers.get("Content-Length", "0") or "0")
            if length <= 0:
                return {}
            data = self.rfile.read(length)
            return json.loads(data.decode("utf-8"))

        def do_OPTIONS(self) -> None:
            self._send_json(200, {"ok": True})

        def _serve_static(self, req_path: str) -> None:
            if not DIST_DIR.is_dir():
                self._send_json(404, {"error": "Frontend dist not built. Run 'npm run build' inside frontend/"})
                return
            clean_path = req_path.lstrip("/").split("?")[0].split("#")[0]
            target = (DIST_DIR / clean_path).resolve() if clean_path else (DIST_DIR / "index.html")

            # Prevent directory traversal attacks
            try:
                target.relative_to(DIST_DIR.resolve())
            except ValueError:
                self._send_json(403, {"error": "Access forbidden"})
                return

            if clean_path and target.is_file():
                file_to_send = target
            else:
                file_to_send = DIST_DIR / "index.html"

            if not file_to_send.is_file():
                self._send_json(404, {"error": f"File not found: {req_path}"})
                return

            ctype, _ = mimetypes.guess_type(str(file_to_send))
            if not ctype:
                ctype = "application/octet-stream"
            if ctype.startswith("text/") or ctype in ("application/javascript", "application/json"):
                ctype += "; charset=utf-8"

            data = file_to_send.read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(len(data)))
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(data)

        def do_GET(self) -> None:
            parsed = urlparse(self.path)
            path = parsed.path.rstrip("/")
            qs = parse_qs(parsed.query)
            try:
                if path == "/api/health":
                    self._send_json(200, {
                        "status": "ok",
                        "products": len(backend.state.products),
                        "categories": len(backend.state.categories),
                    })
                elif path == "/api/dashboard":
                    self._send_json(200, backend.get_dashboard())
                elif path == "/api/categories":
                    self._send_json(200, backend.get_categories())
                elif path == "/api/products":
                    self._send_json(200, backend.get_products())
                elif path == "/api/products/search":
                    q = qs.get("q", [""])[0]
                    self._send_json(200, backend.search_products(q))
                elif path == "/api/pos/scan":
                    barcode = qs.get("barcode", [""])[0]
                    self._send_json(200, backend.scan_barcode(barcode))
                elif path == "/api/pos/cart":
                    self._send_json(200, backend.get_cart())
                elif path == "/api/alerts":
                    self._send_json(200, backend.get_alerts())
                elif path == "/api/restock":
                    self._send_json(200, backend.get_restock())
                elif path == "/api/reports":
                    period = qs.get("period", ["Week"])[0]
                    start_s = qs.get("start", [None])[0]
                    end_s = qs.get("end", [None])[0]
                    self._send_json(200, backend.get_reports(period=period, start_str=start_s, end_str=end_s))
                elif path == "/api/transactions":
                    tx_type = qs.get("type", [None])[0]
                    self._send_json(200, backend.get_transactions(tx_type=tx_type))
                elif path == "/api/settings":
                    self._send_json(200, backend.get_settings())
                elif path == "/api/backup/list":
                    self._send_json(200, {"backups": backend.list_backups()})
                elif path.startswith("/api/"):
                    self._send_json(404, {"error": f"API endpoint not found: {path}"})
                else:
                    self._serve_static(parsed.path)
            except ValueError as e:
                self._send_json(400, {"error": str(e)})
            except Exception as e:
                self._send_json(500, {"error": str(e)})

        def do_POST(self) -> None:
            parsed = urlparse(self.path)
            path = parsed.path.rstrip("/")
            try:
                body = self._read_json()
                if path == "/api/categories":
                    self._send_json(201, backend.create_category(body))
                elif path == "/api/products":
                    self._send_json(201, backend.create_product(body))
                elif path == "/api/pos/cart":
                    self._send_json(200, backend.add_to_cart(body))
                elif path == "/api/pos/checkout":
                    self._send_json(200, backend.checkout(body))
                elif path == "/api/inventory/receive":
                    self._send_json(201, backend.receive_stock(body))
                elif path == "/api/inventory/adjust":
                    self._send_json(200, backend.adjust_stock(body))
                elif path == "/api/inventory/writeoff":
                    self._send_json(200, backend.write_off_expired(body))
                elif path == "/api/inventory/rotate":
                    self._send_json(200, backend.mark_shelf_rotated(body))
                elif path == "/api/undo":
                    self._send_json(200, backend.undo_last())
                elif path == "/api/backup/export":
                    self._send_json(201, backend.export_db_backup())
                elif path == "/api/backup/restore":
                    self._send_json(200, backend.restore_db_backup(body))
                else:
                    self._send_json(404, {"error": f"Not found: {path}"})
            except ValueError as e:
                self._send_json(400, {"error": str(e)})
            except sqlite3.IntegrityError as e:
                self._send_json(400, {"error": f"Duplicate or invalid record: {e}"})
            except Exception as e:
                self._send_json(500, {"error": str(e)})

        def do_PUT(self) -> None:
            parsed = urlparse(self.path)
            path = parsed.path.rstrip("/")
            try:
                body = self._read_json()
                if path.startswith("/api/categories/"):
                    cid = int(path.rsplit("/", 1)[-1])
                    self._send_json(200, backend.update_category(cid, body))
                elif path.startswith("/api/pos/cart/"):
                    pid = int(path.rsplit("/", 1)[-1])
                    self._send_json(200, backend.update_cart_item(pid, body))
                elif path == "/api/settings":
                    self._send_json(200, backend.update_settings(body))
                else:
                    self._send_json(404, {"error": f"Not found: {path}"})
            except ValueError as e:
                self._send_json(400, {"error": str(e)})
            except Exception as e:
                self._send_json(500, {"error": str(e)})

        def do_DELETE(self) -> None:
            parsed = urlparse(self.path)
            path = parsed.path.rstrip("/")
            try:
                if path.startswith("/api/categories/"):
                    cid = int(path.rsplit("/", 1)[-1])
                    self._send_json(200, backend.delete_category(cid))
                elif path == "/api/pos/cart":
                    self._send_json(200, backend.clear_cart())
                elif path.startswith("/api/pos/cart/"):
                    pid = int(path.rsplit("/", 1)[-1])
                    self._send_json(200, backend.remove_cart_item(pid))
                else:
                    self._send_json(404, {"error": f"Not found: {path}"})
            except ValueError as e:
                self._send_json(400, {"error": str(e)})
            except Exception as e:
                self._send_json(500, {"error": str(e)})

    return StockFlowHandler


def run_server(host: str = "127.0.0.1", port: int = 8000, db_path: Optional[Path | str] = None) -> None:
    backend = StockFlowBackend(db_path=db_path)
    server = ThreadingHTTPServer((host, port), make_handler(backend))
    print(f"StockFlow Backend API running at http://{host}:{port}")
    print(f"Database: {backend.db_path} ({len(backend.state.products)} products loaded)")
    print("React Frontend dev server: http://localhost:8443/")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down StockFlow API server...")
    finally:
        server.server_close()
        backend.conn.close()


if __name__ == "__main__":
    run_server()
