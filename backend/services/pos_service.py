"""
backend/services/pos_service.py
Point of sale operations, cart management on custom linked list, and cash checkout.
Tasks 4.1 to 4.9, POS-1 to POS-7, RS-1.

RULES:
- Cart backed strictly by custom Doubly LinkedList (Task 4.2).
- Zero imports of heapq, dict, or sorted.
- Unified barcode entry function for USB scanner, typed entry, and simulated scans.
- Atomically persists sale and writes lines (Task 2.4 / 4.4).
- Pushes to undo stack (Doc 6.7).
- Low-stock notification triggered if sellable stock drops below reorder level (RS-1).
"""

from datetime import date
from typing import Optional, List, Dict, Any
import sqlite3

from backend.ds.linked_list import LinkedList
from backend.ds.stack import Stack
from backend.models.product import Product
from backend.models.transaction import Transaction
from backend.models.transaction_line import TransactionLine
from backend.db.storage import StoreMemoryState, save_transaction_atomic
from backend.services.fefo_service import FEFOService


class CartLine:
    """Internal cart line representation stored inside the custom Doubly LinkedList."""

    def __init__(self, product_id: int, product_name: str, unit_price: float, quantity: int = 1):
        self.product_id = product_id
        self.product_name = product_name
        self.unit_price = unit_price
        self.quantity = quantity


class POSService:
    def __init__(
        self,
        conn: sqlite3.Connection,
        state: StoreMemoryState,
        fefo_service: Optional[FEFOService] = None,
    ):
        self.conn = conn
        self.state = state
        self.fefo_service = fefo_service or FEFOService()
        self.cart = LinkedList()
        self.undo_stack = Stack()

    def _get_product(self, product_id: int) -> Product:
        """Helper to resolve a product by ID from state or database without dict shortcuts."""
        prod = self.state.get_product_by_id(product_id)
        if prod is not None:
            return prod

        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT id, barcode, name, category_id, cost_price, selling_price, reorder_level, location_id, active
            FROM products WHERE id = ?;
        """, (product_id,))
        row = cursor.fetchone()
        if not row:
            raise ValueError(f"Product with ID {product_id} not found.")

        prod = Product(
            id=row[0],
            barcode=row[1],
            name=row[2],
            category_id=row[3],
            cost_price=row[4],
            selling_price=row[5],
            reorder_level=row[6],
            location_id=row[7],
            active=bool(row[8]),
        )
        self.state.products.append(prod)
        if self.state.bst.find(prod.barcode) is None:
            self.state.bst.insert(prod.barcode, prod)
        return prod

    def process_barcode_entry(self, barcode: str) -> Dict[str, Any]:
        """
        Unified barcode entry function for USB scanner, typed entry, and simulated scan.
        Task 4.1 & 4.9: If found returns FOUND; if unknown returns UNKNOWN to prompt registration.
        """
        prod = self.state.bst.find(barcode)
        if prod is None:
            # Fallback query from SQLite in case of dynamically added data
            cursor = self.conn.cursor()
            cursor.execute("""
                SELECT id, barcode, name, category_id, cost_price, selling_price, reorder_level, location_id, active
                FROM products WHERE barcode = ?;
            """, (barcode,))
            row = cursor.fetchone()
            if row:
                prod = Product(
                    id=row[0],
                    barcode=row[1],
                    name=row[2],
                    category_id=row[3],
                    cost_price=row[4],
                    selling_price=row[5],
                    reorder_level=row[6],
                    location_id=row[7],
                    active=bool(row[8]),
                )
                self.state.products.append(prod)
                if self.state.bst.find(prod.barcode) is None:
                    self.state.bst.insert(prod.barcode, prod)

        if prod is not None:
            return {"status": "FOUND", "product": prod}
        return {"status": "UNKNOWN", "barcode": barcode}

    def add_to_cart(self, product_id: int, quantity: int = 1) -> CartLine:
        """Adds a product to the cart. Merges into existing line if already in cart (Doc 6.6)."""
        if quantity <= 0:
            raise ValueError("Quantity must be positive.")

        prod = self._get_product(product_id)
        existing = self.cart.find(lambda item: item.product_id == product_id)
        if existing is not None:
            existing.quantity += quantity
            return existing

        new_line = CartLine(
            product_id=prod.id,
            product_name=prod.name,
            unit_price=prod.selling_price,
            quantity=quantity,
        )
        self.cart.add_end(new_line)
        return new_line

    def update_cart_quantity(self, product_id: int, new_quantity: int) -> None:
        """Updates quantity of an item in the cart. Removes if quantity <= 0."""
        if new_quantity <= 0:
            self.remove_from_cart(product_id)
            return

        existing = self.cart.find(lambda item: item.product_id == product_id)
        if existing is not None:
            existing.quantity = new_quantity

    def remove_from_cart(self, product_id: int) -> bool:
        """Removes a product line from the cart linked list."""
        return self.cart.remove(lambda item: item.product_id == product_id)

    def get_cart_item_count(self) -> int:
        """Returns number of distinct product lines in cart."""
        return self.cart.size()

    def get_cart_total(self) -> float:
        """Computes subtotal of all items in cart using linked list traversal."""
        total = 0.0
        for item in self.cart.traverse():
            total += item.quantity * item.unit_price
        return round(total, 2)

    def clear_cart(self) -> None:
        """Clears all items from the cart."""
        self.cart = LinkedList()

    def checkout(
        self,
        cash_given: float,
        today: Optional[date] = None,
    ) -> Dict[str, Any]:
        """
        Executes POS checkout:
        1. Validates cash >= total (Edge Case 14).
        2. Deducts batches using FEFO via FEFOService (Edge Cases 7, 8, 9).
        3. Atomically persists transaction and line items to SQLite.
        4. Pushes transaction to Undo Stack (Task 4.7).
        5. Checks low-stock trigger (RS-1 / Task 4.8).
        6. Generates receipt breakdown (Task 4.5 / POS-6).
        """
        if self.cart.is_empty():
            raise ValueError("Cart is empty.")

        total = self.get_cart_total()
        if cash_given < total:
            raise ValueError(
                f"Insufficient cash provided. Total is PHP {total:,.2f}, received PHP {cash_given:,.2f}."
            )

        change = round(cash_given - total, 2)
        curr_date = today or date.today()
        date_time_str = curr_date.strftime("%Y-%m-%d %H:%M:%S")

        tx = Transaction(
            id=0,
            type="sale",
            date_time=date_time_str,
            total=total,
            cash_given=cash_given,
            change=change,
            reverses_id=None,
            location_id=1,
        )

        tx_lines: List[TransactionLine] = []
        receipt_lines: List[Dict[str, Any]] = []
        low_stock_alerts: List[Dict[str, Any]] = []

        # Deduct stock for each cart item
        for item in self.cart.traverse():
            prod = self._get_product(item.product_id)
            heap = self.state.get_or_create_product_heap(prod.id)
            allocations = self.fefo_service.deduct_stock(prod, item.quantity, heap, today=curr_date)

            for alloc in allocations:
                line = TransactionLine(
                    id=0,
                    transaction_id=0,
                    product_id=prod.id,
                    batch_id=alloc["batch_id"],
                    quantity=alloc["quantity"],
                    price_at_time=item.unit_price,
                    cost_at_time=alloc["cost_at_time"],
                )
                tx_lines.append(line)

            subtotal = round(item.quantity * item.unit_price, 2)
            receipt_lines.append({
                "product_id": prod.id,
                "product_name": prod.name,
                "quantity": item.quantity,
                "unit_price": item.unit_price,
                "subtotal": subtotal,
            })

            # Check low stock (RS-1)
            remaining_sellable = 0
            for b in heap.ordered_read():
                if self.fefo_service.alert_service.is_sellable(b.expiry_date, curr_date):
                    remaining_sellable += b.quantity

            if remaining_sellable < prod.reorder_level:
                low_stock_alerts.append({
                    "product_id": prod.id,
                    "product_name": prod.name,
                    "remaining_stock": remaining_sellable,
                    "reorder_level": prod.reorder_level,
                })

        # Atomic persistence of transaction and stock deduction
        saved_tx = save_transaction_atomic(self.conn, tx, tx_lines)

        # Push to in-memory undo stack
        self.undo_stack.push({
            "transaction": saved_tx,
            "lines": tx_lines,
        })

        self.clear_cart()

        return {
            "transaction_id": saved_tx.id,
            "date_time": saved_tx.date_time,
            "total": saved_tx.total,
            "cash_given": saved_tx.cash_given,
            "change": saved_tx.change,
            "lines": receipt_lines,
            "low_stock_alerts": low_stock_alerts,
        }
