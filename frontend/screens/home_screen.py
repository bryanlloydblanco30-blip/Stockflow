"""
frontend/screens/home_screen.py
Dashboard home page: stats cards, needs-attention table, callout.
Ported from frontend/StockFlow/main.py StockFlow.home().
"""

from __future__ import annotations

import flet as ft

from design.tokens import (
    COLOR_BRAND_GREEN,
    COLOR_TEXT_MAIN,
    COLOR_TEXT_MUTED,
    PALE_YELLOW,
    PALE_GREEN,
    PALE_PEACH,
    PALE_LAVENDER,
)
from frontend.components.primitives import (
    text,
    rounded_button,
    card,
    stat_card,
    badge,
    data_table,
)

GREEN = COLOR_BRAND_GREEN
INK = COLOR_TEXT_MAIN
MUTED = COLOR_TEXT_MUTED


def render(on_navigate=None, compact: bool = False) -> ft.Control:
    """Render the home dashboard."""
    stats = ft.ResponsiveRow(
        [
            ft.Container(
                stat_card("Today's Sales", "₱4,860.00", PALE_YELLOW),
                col={"sm": 6, "lg": 3},
            ),
            ft.Container(
                stat_card("Today's Profit", "₱1,120.00", PALE_GREEN, "#1D6538"),
                col={"sm": 6, "lg": 3},
            ),
            ft.Container(
                stat_card("Low Stock Items", "7", PALE_PEACH),
                col={"sm": 6, "lg": 3},
            ),
            ft.Container(
                stat_card("Near Expiry Batches", "4", PALE_LAVENDER),
                col={"sm": 6, "lg": 3},
            ),
        ],
        spacing=16,
        run_spacing=16,
    )

    rows = [
        ("Pandesal pack", "Expires in 1 day", badge("Red", "red")),
        ("Canned sardines 155g", "3 units left", badge("Amber", "amber")),
        ("Bottled water 500ml", "Reorder level reached", badge("Amber", "amber")),
        ("Loaf bread", "Expires in 3 days", badge("Amber", "amber")),
        ("Pencil HB", "6 units left", badge("Low")),
    ]
    table = data_table(["Product", "Issue", "Urgency"], rows)

    callout = card(
        ft.Row(
            [
                ft.Column(
                    [
                        text("Ready for your next customer?", 20, GREEN),
                        text(
                            "Start a sale, check your shelves, and keep things moving.",
                            14,
                            MUTED,
                        ),
                    ]
                ),
                ft.Icon(ft.Icons.SHOPPING_CART_OUTLINED, color=GREEN),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        ),
        bgcolor=PALE_GREEN,
    )

    return ft.Column(
        [
            ft.Row(
                [
                    ft.Container(expand=True),
                    rounded_button(
                        "START SALE",
                        lambda _: on_navigate("sell") if on_navigate else None,
                        PALE_PEACH,
                        GREEN,
                    ),
                ]
            ),
            stats,
            card(
                ft.Column(
                    [
                        text("Needs attention", 20, INK, ft.FontWeight.W_600),
                        table,
                    ]
                )
            ),
            ft.GestureDetector(
                content=callout,
                on_tap=lambda _: on_navigate("sell") if on_navigate else None,
            ),
        ],
        spacing=24,
    )
