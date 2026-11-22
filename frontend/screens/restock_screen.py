"""
frontend/screens/restock_screen.py
Restock priority queue and fast/slow movers view.
Ported from frontend/StockFlow/main.py StockFlow.restock().
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
from frontend.components.primitives import (
    text,
    rounded_button,
    card,
    badge,
    data_table,
)

GREEN = COLOR_BRAND_GREEN
MUTED = COLOR_TEXT_MUTED


def render(compact: bool = False) -> ft.Control:
    """Render the restock priority screen."""
    rows = [
        ("92", "Sardines 155g", "1.5", "2.0 / day", "24", badge("Urgent", "red")),
        ("85", "Bottled water 500ml", "3", "16 / day", "60", badge("Urgent", "red")),
        ("61", "Pencil HB", "6", "1.0 / day", "12", badge("Soon", "amber")),
        ("48", "Instant noodles", "9", "6.5 / day", "40", badge("Soon", "amber")),
    ]

    return ft.Column(
        [
            ft.Row(
                [
                    rounded_button("Priority Queue", bgcolor=PALE_BLUE),
                    rounded_button("Fast / Slow Movers", bgcolor=PALE_LAVENDER),
                ],
                wrap=True,
            ),
            card(
                data_table(
                    ["Score", "Product", "Days of cover", "14-day speed", "Suggested qty", "Urgency"],
                    rows,
                ),
                padding=10,
            ),
            card(
                ft.Row(
                    [
                        ft.Icon(
                            ft.Icons.LOCAL_SHIPPING_OUTLINED,
                            size=36,
                            color=GREEN,
                        ),
                        ft.Column(
                            [
                                text(
                                    "Keep your favorites on the shelf.",
                                    21,
                                    GREEN,
                                ),
                                text(
                                    "Start with urgent items, then work your way down the priority queue.",
                                    14,
                                    MUTED,
                                ),
                            ]
                        ),
                    ],
                    spacing=28,
                ),
                bgcolor=PALE_GREEN,
                padding=30,
            ),
        ],
        spacing=26,
    )
