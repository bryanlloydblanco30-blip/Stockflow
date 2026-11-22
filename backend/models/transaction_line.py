"""
backend/models/transaction_line.py
TransactionLine model (Doc 8.1).
Records snapshot prices and the supplying batch id at the moment of sale.
"""

from dataclasses import dataclass


@dataclass
class TransactionLine:
    id: int
    transaction_id: int
    product_id: int
    batch_id: int
    quantity: int
    price_at_time: float
    cost_at_time: float

