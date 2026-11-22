"""
frontend/screens/stock_list_screen.py
Product inventory list with search, filter chips, and data table.
Ported from frontend/StockFlow/main.py StockFlow.stock().
"""

from __future__ import annotations

import flet as ft

from design.tokens import (
    COLOR_BRAND_GREEN,
    COLOR_TEXT_MAIN,
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

GREEN = COLOR_BRAND_GREEN
INK = COLOR_TEXT_MAIN
MUTED = COLOR_TEXT_MUTED

# ── Sample product data (will be replaced by backend services) ────────
PRODUCTS = [
    ("4800010001", "Pandesal pack", "Bread", "12", "₱32.00", "₱45.00", "Expires soon", "red"),
    ("4800010002", "Sardines 155g", "Canned", "3", "₱20.00", "₱28.00", "Low", "amber"),
    ("4800010003", "Bottled water 500ml", "Drinks", "48", "₱14.00", "₱25.00", "OK", "green"),
    ("4800010004", "Notebook", "School supplies", "20", "₱40.00", "₱58.00", "Untracked", "green"),
    ("4800010005", "Instant noodles", "Canned", "60", "₱9.00", "₱14.00", "OK", "green"),
    ("4800010006", "Loaf bread", "Bread", "9", "₱48.00", "₱65.00", "Near expiry", "amber"),
]


def render(
    on_product_click=None,
    stock_filter: str = "All",
    stock_query: str = "",
    on_filter_change=None,
    on_query_change=None,
    compact: bool = False,
) -> ft.Control:
    """Render the stock list screen."""
    query = stock_query.lower()
    filtered = []
    for product in PRODUCTS:
        if query and query not in " ".join(product).lower():
            continue
        if stock_filter == "Low" and product[6] != "Low":
            continue
        if stock_filter == "Near Expiry" and "expir" not in product[6].lower():
            continue
        if stock_filter == "Untracked" and product[6] != "Untracked":
            continue
        filtered.append((*product[:6], badge(product[6], product[7])))

    search = ft.TextField(
        hint_text="Search products or barcode",
        value=stock_query,
        on_change=on_query_change,
    )

    chips = ft.Row(
        [
            rounded_button(
                option,
                lambda _, v=option: on_filter_change(v) if on_filter_change else None,
                PALE_BLUE if stock_filter == option else PALE_LAVENDER,
            )
            for option in ["All", "Low", "Near Expiry", "Untracked"]
        ],
        wrap=True,
    )

    return ft.Column(
        [
            ft.Row(
                [
                    ft.Container(expand=True),
                    rounded_button("+ Register Product", bgcolor=PALE_BLUE),
                ]
            ),
            search,
            chips,
            ft.GestureDetector(
                content=card(
                    data_table(
                        ["Barcode", "Name", "Category", "Units", "Cost", "Price", "Status"],
                        filtered,
                    ),
                    padding=10,
                ),
                on_tap=lambda _: on_product_click() if on_product_click else None,
            ),
            ft.Column(
                [
                    text("Every shelf, a little more organized.", 23, GREEN),
                    text(
                        "Find your products, check availability, and spot what needs attention.",
                        14,
                        MUTED,
                    ),
                ]
            ),
        ],
        spacing=20,
    )
