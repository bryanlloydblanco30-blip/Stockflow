"""
backend/models/transaction.py
Transaction model (Doc 8.1).
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class Transaction:
    id: int
    type: str  # 'sale', 'receive', 'write-off', 'adjustment', 'void'
    date_time: str
    total: float
    cash_given: float
    change: float
    reverses_id: Optional[int] = None
    location_id: int = 1

