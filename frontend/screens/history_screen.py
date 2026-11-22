"""
frontend/screens/history_screen.py
Transaction history with type filter chips and void button.
Ported from frontend/StockFlow/main.py StockFlow.history().
"""

from __future__ import annotations

import flet as ft

from design.tokens import (
    COLOR_TEXT_MUTED,
    PALE_BLUE,
    PALE_LAVENDER,
)
from frontend.components.primitives import (
    text,
    rounded_button,
    card,
    badge,
    data_table,
)

MUTED = COLOR_TEXT_MUTED

# ── Sample history data (will be replaced by backend services) ────────
_HISTORY_DATA = [
    ("7 Nov 10:42", "Sale", "3 items", "PHP 184.00", "green"),
    ("7 Nov 09:15", "Receive", "Fresh Milk 1L × 24", "PHP 1,152.00", "amber"),
    ("6 Nov 17:30", "Write-off", "Yogurt cup × 2", "PHP 70.00", "red"),
    ("6 Nov 12:05", "Sale", "2 items", "PHP 90.00", "green"),
]


def render(
    history_filter: str = "All",
    on_filter_change=None,
    compact: bool = False,
) -> ft.Control:
    """Render the transaction history screen."""
    rows = []
    for index, row in enumerate(_HISTORY_DATA):
        if history_filter != "All" and row[1] != history_filter:
            continue
        action = (
            rounded_button("Void last sale", bgcolor=PALE_LAVENDER)
            if index == 0 and history_filter == "All"
            else text("")
        )
        rows.append((row[0], badge(row[1], row[4]), row[2], row[3], action))

    filters = ft.Row(
        [
            rounded_button(
                option,
                lambda _, v=option: on_filter_change(v)
                if on_filter_change
                else None,
                PALE_BLUE if history_filter == option else PALE_LAVENDER,
            )
            for option in [
                "All", "Sale", "Receive", "Void", "Adjustment", "Write-off"
            ]
        ],
        wrap=True,
    )

    return ft.Column(
        [
            filters,
            card(
                data_table(["Date", "Type", "Details", "Amount", ""], rows),
                padding=10,
            ),
            text(
                "Undo is available only on the latest transaction.",
                13,
                MUTED,
            ),
        ],
        spacing=22,
    )
