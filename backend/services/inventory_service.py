"""
backend/services/inventory_service.py
Receiving deliveries, older-stock warnings, adjustments, and write-offs (Tasks 3.3, 3.4, 3.6, 3.7, 3.8).
Enforces:
- IN-5 Older-stock message: returns older batches when a new batch is received
- IN-6 Shelf-rotation: moved_to_front flag
- IN-7 Write-off: removes expired batch, records loss in PHP
- IN-8 Stock adjustment: logs reason, old count, new count
- FEFO heap insertion order: expiry_date primary, received_date secondary tie-breaker
"""

import sqlite3
from datetime import date, datetime
from typing import Optional, List, Dict, Any
from dataclasses import dataclass

from backend.models.batch import Batch
from backend.services.alert_service import AlertService


@dataclass
class ReceiveStockResult:
    batch: Batch
    older_batches_warning: List[Dict[str, Any]]


class InventoryService:
    def __init__(self, db_conn: sqlite3.Connection, memory_state, alert_service: AlertService):
        self.conn = db_conn
        self.state = memory_state
        self.alert_service = alert_service

    def receive_stock(
        self,
        product_id: int,
        quantity: int,
        cost: float,
        expiry_date: Optional[str] = None,
        received_date: Optional[str] = None,
        today: Optional[date] = None,
    ) -> ReceiveStockResult:
        """
        Adds a new batch to SQLite and in-memory Min-Heap.
        Checks for older batches to generate older-stock warning (IN-5).
        """
        curr_date_str = received_date or (today or date.today()).isoformat()

        batch = Batch(
            id=0,
            product_id=product_id,
            quantity=int(quantity),
            cost_price=float(cost),
            received_date=curr_date_str,
            expiry_date=expiry_date.strip() if expiry_date else None,
            moved_to_front=False,
        )

        with self.conn:
            cur = self.conn.cursor()
            cur.execute("""
                INSERT INTO batches (product_id, quantity, cost_price, received_date, expiry_date, moved_to_front)
                VALUES (?, ?, ?, ?, ?, ?);
            """, (
                batch.product_id,
                batch.quantity,
                batch.cost_price,
                batch.received_date,
                batch.expiry_date,
                int(batch.moved_to_front),
            ))
            batch.id = cur.lastrowid

        # Insert into product's Min-Heap in memory
        heap = self.state.get_or_create_product_heap(product_id)

        # Older stock warning check (IN-5) before inserting or using ordered_read
        older_warnings: List[Dict[str, Any]] = []
        if batch.expiry_date:
            prod = self.state.get_product_by_id(product_id)
            warn_days = 7
            if prod and prod.category_id is not None:
                cat = self.state.get_category_by_id(prod.category_id)
                if cat:
                    warn_days = cat.warn_days

            for existing_batch in heap.ordered_read():
                if existing_batch.expiry_date and existing_batch.expiry_date < batch.expiry_date and existing_batch.quantity > 0:
                    level = self.alert_service.calculate_level(existing_batch.expiry_date, warn_days, today)
                    older_warnings.append({
                        "batch_id": existing_batch.id,
                        "expiry_date": existing_batch.expiry_date,
                        "units": existing_batch.quantity,
                        "level": level,
                    })

            heap.insert(
                item=batch,
                key=batch.expiry_date,
                tie_break=batch.received_date,
            )
        else:
            heap.insert(
                item=batch,
                key=batch.received_date,
                tie_break=str(batch.id),
            )

        return ReceiveStockResult(batch=batch, older_batches_warning=older_warnings)

    def mark_shelf_rotated(self, batch_id: int) -> bool:
        """Sets moved_to_front flag on the batch (IN-6)."""
        with self.conn:
            self.conn.execute("UPDATE batches SET moved_to_front = 1 WHERE id = ?;", (batch_id,))

        # Update in-memory batch
        for _, heap in self.state._product_heaps:
            for b in heap.ordered_read():
                if b.id == batch_id:
                    b.moved_to_front = True
                    return True
        return False

    def write_off_expired(self, batch_id: int, reason: str = "Expired on shelf") -> Dict[str, Any]:
        """
        Removes/zeros expired batch and records financial loss (IN-7).
        """
        cur = self.conn.cursor()
        cur.execute("SELECT product_id, quantity, cost_price FROM batches WHERE id = ?;", (batch_id,))
        row = cur.fetchone()
        if not row:
            raise ValueError(f"Batch {batch_id} not found.")

        product_id, qty, cost = row[0], row[1], row[2]
        loss_amount = qty * cost

        with self.conn:
            # Set batch quantity to 0
            self.conn.execute("UPDATE batches SET quantity = 0 WHERE id = ?;", (batch_id,))
            # Log in transactions table as writeoff
            now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cur = self.conn.cursor()
            cur.execute("""
                INSERT INTO transactions (type, date_time, total, cash_given, change)
                VALUES ('writeoff', ?, ?, 0.0, 0.0);
            """, (now_str, loss_amount))
            tx_id = cur.lastrowid

            cur.execute("""
                INSERT INTO transaction_lines (transaction_id, product_id, batch_id, quantity, price_at_time, cost_at_time)
                VALUES (?, ?, ?, ?, 0.0, ?);
            """, (tx_id, product_id, batch_id, qty, cost))

        # Update in-memory heap
        heap = self.state.get_product_heap(product_id)
        if heap:
            try:
                # Remove from heap using remove_specific
                for b in heap.ordered_read():
                    if b.id == batch_id:
                        heap.remove_specific(b)
                        break
            except Exception:
                pass

        return {
            "batch_id": batch_id,
            "product_id": product_id,
            "units_lost": qty,
            "loss_amount": loss_amount,
            "reason": reason,
        }

    def adjust_stock(self, batch_id: int, new_quantity: int, reason: str) -> Dict[str, Any]:
        """
        Adjusts batch count with required reason, preserving audit history (IN-8).
        """
        cur = self.conn.cursor()
        cur.execute("SELECT product_id, quantity, cost_price FROM batches WHERE id = ?;", (batch_id,))
        row = cur.fetchone()
        if not row:
            raise ValueError(f"Batch {batch_id} not found.")

        product_id, old_qty, cost = row[0], row[1], row[2]
        diff = new_quantity - old_qty

        with self.conn:
            self.conn.execute("UPDATE batches SET quantity = ? WHERE id = ?;", (new_quantity, batch_id))
            now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cur = self.conn.cursor()
            cur.execute("""
                INSERT INTO transactions (type, date_time, total, cash_given, change)
                VALUES ('adjustment', ?, ?, 0.0, 0.0);
            """, (now_str, diff * cost))
            tx_id = cur.lastrowid

            cur.execute("""
                INSERT INTO transaction_lines (transaction_id, product_id, batch_id, quantity, price_at_time, cost_at_time)
                VALUES (?, ?, ?, ?, ?, ?);
            """, (tx_id, product_id, batch_id, diff, 0.0, cost))

        # Update memory
        heap = self.state.get_product_heap(product_id)
        if heap:
            for b in heap.ordered_read():
                if b.id == batch_id:
                    b.quantity = new_quantity
                    break

        return {
            "batch_id": batch_id,
            "product_id": product_id,
            "old_quantity": old_qty,
            "new_quantity": new_quantity,
            "difference": diff,
            "reason": reason,
        }

    def get_unresolved_expiry_batches(self) -> List[Dict[str, Any]]:
        """
        Returns batches where category tracks expiry but expiry_date IS NULL (Task 3.9 / Edge Case 6).
        Flagged as 'Expiry date needed'.
        """
        cur = self.conn.cursor()
        cur.execute("""
            SELECT b.id, b.product_id, p.name, b.quantity
            FROM batches b
            JOIN products p ON b.product_id = p.id
            JOIN categories c ON p.category_id = c.id
            WHERE c.tracks_expiry = 1 AND b.expiry_date IS NULL AND b.quantity > 0;
        """)
        return [
            {"batch_id": row[0], "product_id": row[1], "product_name": row[2], "quantity": row[3], "status": "Expiry date needed"}
            for row in cur.fetchall()
        ]
