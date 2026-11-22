"""
backend/models/batch.py
Batch model (Doc 8.1).
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class Batch:
    id: int
    product_id: int
    quantity: int
    cost_price: float
    received_date: str
    expiry_date: Optional[str] = None
    moved_to_front: bool = False

