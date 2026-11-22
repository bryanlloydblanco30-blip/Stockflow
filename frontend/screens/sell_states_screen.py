"""
frontend/screens/sell_states_screen.py
Checkout and inventory availability state cards.
Ported from frontend/StockFlow/main.py StockFlow.sell_states().
"""

from __future__ import annotations

import flet as ft

from design.tokens import COLOR_BRAND_GREEN, COLOR_TEXT_MUTED
from frontend.components.primitives import text, rounded_button, card

GREEN = COLOR_BRAND_GREEN
MUTED = COLOR_TEXT_MUTED


def render(compact: bool = False) -> ft.Control:
    """Render the sell-states reference screen."""
    controls = [
        card(
            ft.Column(
                [
                    ft.Row(
                        [
                            ft.Icon(ft.Icons.SHOPPING_CART_OUTLINED, color=GREEN),
                            text("Empty cart", color=MUTED),
                        ]
                    ),
                    text(
                        "Cart is empty. Scan a product to start.",
                        weight=ft.FontWeight.W_600,
                    ),
                    rounded_button("Checkout", disabled=True),
                ],
                spacing=18,
            ),
            height=245,
        ),
        card(
            ft.Column(
                [
                    ft.Row(
                        [
                            ft.Icon(ft.Icons.INVENTORY_2_OUTLINED, color=GREEN),
                            text("Not enough stock", color=MUTED),
                        ]
                    ),
                    text("Fresh Milk 1L × 5"),
                    text(
                        "Only 3 left. Lower the quantity.",
                        color="#C70028",
                        weight=ft.FontWeight.W_600,
                    ),
                    ft.Row(
                        [
                            ft.IconButton(ft.Icons.REMOVE),
                            text("5"),
                            ft.IconButton(ft.Icons.ADD),
                        ]
                    ),
                ],
                spacing=14,
            ),
            bgcolor="#FFF3DC",
            height=245,
        ),
        card(
            ft.Column(
                [
                    ft.Row(
                        [
                            ft.Icon(ft.Icons.INVENTORY_2_OUTLINED, color=GREEN),
                            text("Only expired stock left", color=MUTED),
                        ]
                    ),
                    text(
                        "Only expired stock left. It cannot be sold.",
                        color="#C70028",
                        weight=ft.FontWeight.W_600,
                    ),
                    ft.TextButton("Go to write-off list"),
                ],
                spacing=16,
            ),
            bgcolor="#FBEAE4",
            height=200,
        ),
    ]

    return ft.ResponsiveRow(
        [
            ft.Container(control, col={"sm": 12, "md": 6})
            for control in controls
        ],
        spacing=22,
        run_spacing=22,
    )
