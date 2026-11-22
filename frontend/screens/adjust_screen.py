"""
frontend/screens/adjust_screen.py
Stock count adjustment form with batch selector and reason field.
Ported from frontend/StockFlow/main.py StockFlow.adjust().
"""

from __future__ import annotations

import flet as ft

from design.tokens import (
    COLOR_BRAND_GREEN,
    COLOR_TEXT_MUTED,
    PALE_BLUE,
    PALE_GREEN,
    PALE_LAVENDER,
)
from frontend.components.primitives import text, rounded_button, card

GREEN = COLOR_BRAND_GREEN
MUTED = COLOR_TEXT_MUTED


def render(on_cancel=None, compact: bool = False) -> ft.Control:
    """Render the adjust-count screen."""
    status = ft.Text("", color=GREEN)

    def save(_):
        status.value = "Adjustment saved"
        status.update()

    form = card(
        ft.Column(
            [
                ft.Dropdown(
                    label="Batch",
                    value="batch-a",
                    options=[
                        ft.dropdown.Option(
                            key="batch-a", text="Batch A · exp 12 Nov 2026"
                        )
                    ],
                ),
                ft.TextField(label="Current count", value="8", read_only=True),
                ft.TextField(
                    label="New count (after physical check)", value="6"
                ),
                ft.TextField(label="Reason", value="Counted 6 on shelf"),
                rounded_button("Save adjustment", save, PALE_BLUE),
                status,
                text(
                    "Saved with old count, new count and reason. History is never edited.",
                    12,
                    MUTED,
                ),
            ],
            spacing=14,
        ),
        expand=True,
    )

    note = card(
        ft.Column(
            [
                ft.Icon(ft.Icons.INVENTORY_2_OUTLINED, size=38, color=GREEN),
                text("A fresh count.", 21, GREEN),
                text(
                    "Count what's on your shelf,\nthen leave a reason to keep\nyour stock history clear.",
                    14,
                    MUTED,
                ),
            ]
        ),
        bgcolor=PALE_GREEN,
        width=None if compact else 320,
    )

    controls = [
        ft.Row(
            [
                ft.Container(expand=True),
                rounded_button(
                    "Cancel",
                    lambda _: on_cancel() if on_cancel else None,
                    PALE_LAVENDER,
                ),
            ]
        )
    ]

    if compact:
        controls.append(ft.Column([form, note], spacing=20))
    else:
        controls.append(
            ft.Row(
                [form, note],
                spacing=24,
                vertical_alignment=ft.CrossAxisAlignment.START,
            )
        )

    return ft.Column(controls, spacing=18)
