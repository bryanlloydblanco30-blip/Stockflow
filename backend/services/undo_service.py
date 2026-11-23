"""
backend/services/undo_service.py
Single-level transaction undo using custom Stack (Task 4.7 / Doc 6.7 / Decision D2).
Restores stock to exact supplying batches and creates a void record.

RULES:
- Single-level undo only (Decision D2).
- Blocked if a newer transaction exists in the database (Doc 6.7 / Edge Case 15).
- Restores exact batches and quantities that were deducted.
- Re-inserts exhausted batches into the product's Min-Heap.
- Zero imports of heapq, dict, or sorted.
"""

from datetime import date
from typing import Optional, Dict, Any
import sqlite3

from backend.ds.stack import Stack
from backend.models.batch import Batch
from backend.models.transaction import Transaction
from backend.db.storage import StoreMemoryState


class UndoService:
    def __init__(
        self,
        conn: sqlite3.Connection,
        state: StoreMemoryState,
        undo_stack: Stack,
    ):
        self.conn = conn
        self.state = state
        self.stack = undo_stack

    def void_last_transaction(self, today: Optional[date] = None) -> Transaction:
        """
        Reverses the most recent transaction (one level only).
        Blocked if the stack is empty or if a newer transaction exists in SQLite.
        """
        if self.stack.is_empty():
            raise ValueError("No transaction to undo.")

        last_entry = self.stack.peek()
        original_tx: Transaction = last_entry["transaction"]

        # Check if newer transaction exists in SQLite (Doc 6.7 / Edge Case 15)
        cursor = self.conn.cursor()
        cursor.execute("SELECT MAX(id) FROM transactions;")
        row = cursor.fetchone()
        max_id = row[0] if row and row[0] is not None else 0

        if max_id != original_tx.id:
            raise ValueError("Cannot undo: a newer transaction exists.")

        # Reversal logic based on transaction type
        if original_tx.type == "sale":
            # Restore batch quantities
            for line in last_entry["lines"]:
                # 1. Update SQLite
                cursor.execute("""
                    UPDATE batches
                    SET quantity = quantity + ?
                    WHERE id = ?;
                """, (line.quantity, line.batch_id))

                # 2. Update In-Memory Min-Heap
                heap = self.state.get_or_create_product_heap(line.product_id)
                found = False
                for entry in heap._heap:
                    if entry.item.id == line.batch_id:
                        entry.item.quantity += line.quantity
                        found = True
                        break

                if not found:
                    # Batch was exhausted and removed from heap during sale; re-insert from DB
                    cursor.execute("""
                        SELECT id, product_id, quantity, cost_price, received_date, expiry_date, moved_to_front
                        FROM batches WHERE id = ?;
                    """, (line.batch_id,))
                    b_row = cursor.fetchone()
                    if b_row:
                        restored_batch = Batch(
                            id=b_row[0],
                            product_id=b_row[1],
                            quantity=b_row[2],
                            cost_price=b_row[3],
                            received_date=b_row[4],
                            expiry_date=b_row[5],
                            moved_to_front=bool(b_row[6]),
                        )
                        if restored_batch.expiry_date:
                            heap.insert(
                                item=restored_batch,
                                key=restored_batch.expiry_date,
                                tie_break=restored_batch.received_date,
                            )
                        else:
                            heap.insert(
                                item=restored_batch,
                                key=restored_batch.received_date,
                                tie_break=str(restored_batch.id),
                            )

            # Record void transaction
            curr_date = today or date.today()
            date_time_str = curr_date.strftime("%Y-%m-%d %H:%M:%S")

            cursor.execute("""
                INSERT INTO transactions (type, date_time, total, cash_given, change, reverses_id, location_id)
                VALUES (?, ?, ?, ?, ?, ?, ?);
            """, (
                "void",
                date_time_str,
                original_tx.total,
                0.0,
                0.0,
                original_tx.id,
                original_tx.location_id,
            ))
            void_tx_id = cursor.lastrowid
            self.conn.commit()

            # Pop from stack after successful undo
            self.stack.pop()

            return Transaction(
                id=void_tx_id,
                type="void",
                date_time=date_time_str,
                total=original_tx.total,
                cash_given=0.0,
                change=0.0,
                reverses_id=original_tx.id,
                location_id=original_tx.location_id,
            )

        raise ValueError(f"Undo for transaction type '{original_tx.type}' not supported.")
