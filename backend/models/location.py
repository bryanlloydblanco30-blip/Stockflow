"""
backend/models/location.py
Location model (Doc 8.1 / D1).
Single location for core release.
"""

from dataclasses import dataclass


@dataclass
class Location:
    id: int = 1
    name: str = "Main Branch"

