"""
frontend/components/stepper.py
Quantity stepper (minus / value / plus) used in the sell screen cart rows.
"""

from __future__ import annotations

import flet as ft

from frontend.components.primitives import text


def quantity_stepper(
    value: int,
    on_minus=None,
    on_plus=None,
) -> ft.Row:
    """A compact −/value/+ row."""
    return ft.Row(
        [
            ft.IconButton(ft.Icons.REMOVE, on_click=on_minus),
            text(str(value)),
            ft.IconButton(ft.Icons.ADD, on_click=on_plus),
        ],
        spacing=0,
    )
