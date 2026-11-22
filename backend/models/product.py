"""
backend/models/product.py
Product model (Doc 8.1).
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class Product:
    id: int
    barcode: str
    name: str
    category_id: Optional[int]
    cost_price: float
    selling_price: float
    reorder_level: int = 0
    location_id: int = 1
    active: bool = True

