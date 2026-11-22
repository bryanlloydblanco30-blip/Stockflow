"""
frontend/components/barcode_input.py
Barcode text field with Scan and Simulate buttons.
All barcode entry goes through one function (Doc 4.3, D17).
"""

from __future__ import annotations

import flet as ft

from design.tokens import PALE_BLUE, PALE_LAVENDER
from frontend.components.primitives import rounded_button


def barcode_input_row(
    on_scan=None,
    on_simulate=None,
    on_submit=None,
) -> ft.ResponsiveRow:
    """Barcode entry row: text field + Scan + Simulate buttons."""
    return ft.ResponsiveRow(
        [
            ft.TextField(
                hint_text="Scan or type barcode",
                on_submit=on_submit,
                col={"sm": 12, "md": 7},
            ),
            ft.Container(
                rounded_button("Scan", on_click=on_scan, bgcolor=PALE_BLUE),
                col={"sm": 6, "md": 2},
            ),
            ft.Container(
                rounded_button("Simulate", on_click=on_simulate, bgcolor=PALE_LAVENDER),
                col={"sm": 6, "md": 3},
            ),
        ]
    )
