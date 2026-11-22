"""
frontend/screens/sell_screen.py
Point-of-sale screen: barcode input, cart list, summary panel.
Ported from frontend/StockFlow/main.py StockFlow.sell().
"""

from __future__ import annotations

import flet as ft

from design.tokens import (
    COLOR_BRAND_GREEN,
    COLOR_TEXT_MAIN,
    COLOR_TEXT_MUTED,
    PALE_BLUE,
    PALE_GREEN,
    PALE_LAVENDER,
)
from frontend.components.primitives import (
    text,
    rounded_button,
    card,
    summary_line,
)
from frontend.components.barcode_input import barcode_input_row

GREEN = COLOR_BRAND_GREEN
INK = COLOR_TEXT_MAIN
MUTED = COLOR_TEXT_MUTED


# ── Sample cart data (will be replaced by backend services) ───────────
_SAMPLE_CART = [
    {"name": "Pandesal pack", "qty": 1, "price": 45},
    {"name": "Sardines 155g", "qty": 2, "price": 28},
    {"name": "Bottled water 500ml", "qty": 1, "price": 25},
    {"name": "Notebook", "qty": 1, "price": 58},
]


def render(compact: bool = False, cart=None) -> ft.Control:
    """Render the sell / POS screen."""
    if cart is None:
        cart = _SAMPLE_CART

    total = sum(item["qty"] * item["price"] for item in cart)

    items = []
    for i, item in enumerate(cart):
        items.append(
            ft.Row(
                [
                    ft.Container(text(item["name"]), expand=2),
                    ft.Row(
                        [
                            ft.IconButton(ft.Icons.REMOVE),
                            text(str(item["qty"])),
                            ft.IconButton(ft.Icons.ADD),
                        ],
                        spacing=0,
                    ),
                    ft.Container(text(f"₱{item['price']:.2f}"), expand=1),
                    ft.Container(
                        text(f"₱{item['price'] * item['qty']:.2f}"), expand=1
                    ),
                    rounded_button("Remove", bgcolor=PALE_LAVENDER),
                ],
                spacing=8,
            )
        )
        items.append(ft.Divider(color="#EBE8E1", height=1))

    cart_card = card(
        ft.Column(
            [
                barcode_input_row(),
                *items,
            ],
            spacing=14,
            scroll=ft.ScrollMode.AUTO,
        ),
        expand=True,
    )

    summary = card(
        ft.Column(
            [
                text("Summary", 14, MUTED, ft.FontWeight.W_600),
                summary_line("Items", str(sum(i["qty"] for i in cart))),
                summary_line("Subtotal", f"₱{total:.2f}"),
                summary_line("Tax 0%", "₱0.00"),
                ft.Divider(),
                summary_line("Total", f"₱{total:.2f}", True),
                rounded_button("Checkout (Enter)", bgcolor=PALE_BLUE, width=300),
            ],
            spacing=14,
        )
    )

    side = ft.Column(
        [
            summary,
            card(
                ft.Column(
                    [
                        text(
                            "A smooth checkout,\na happy customer.",
                            20,
                            GREEN,
                        ),
                        text(
                            "Scan items, review, and you're ready.",
                            13,
                            MUTED,
                        ),
                    ]
                ),
                bgcolor=PALE_GREEN,
            ),
        ],
        width=None if compact else 330,
    )

    if compact:
        return ft.Column([cart_card, side], spacing=18)
    return ft.Row(
        [cart_card, side],
        spacing=22,
        vertical_alignment=ft.CrossAxisAlignment.START,
    )
