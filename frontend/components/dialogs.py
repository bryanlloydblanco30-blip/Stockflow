"""
frontend/components/dialogs.py
Page header with title, subtitle, and "More" popup menu.
Ported from frontend/StockFlow/main.py StockFlow.header().
"""

from __future__ import annotations

import flet as ft

from frontend.components.primitives import text, rounded_button

INK = "#202334"
MUTED = "#69756B"

# ── Page metadata ─────────────────────────────────────────────────────
META = {
    "home": ("Home", "Your store at a glance"),
    "sell": ("Sell", "Build a sale and checkout"),
    "stock": ("Stock", "Manage products and availability"),
    "restock": ("Restock", "Plan your next replenishment"),
    "reports": ("Reports", "Understand your store performance"),
    "sell_states": ("Sell states", "Checkout and inventory availability states"),
    "adjust": ("Adjust count · Fresh Milk 1L", "Update the physical count for this batch"),
    "history": ("Transaction history", "Review sales and inventory movements"),
}


def build_page_header(
    page_id: str,
    on_navigate,
    compact: bool = False,
) -> ft.Control:
    """Build the top header row with title, subtitle, and More menu."""
    title, subtitle = META.get(page_id, ("StockFlow", ""))

    menu = ft.PopupMenuButton(
        content=rounded_button("More⌄", width=150),
        items=[
            ft.PopupMenuItem(
                content="Sell states",
                on_click=lambda _: on_navigate("sell_states"),
            ),
            ft.PopupMenuItem(
                content="Adjust stock",
                on_click=lambda _: on_navigate("adjust"),
            ),
            ft.PopupMenuItem(
                content="History",
                on_click=lambda _: on_navigate("history"),
            ),
        ],
    )

    return ft.Row(
        [
            ft.Column(
                [
                    text("YOUR STORE, SIMPLIFIED", 10, "#778579"),
                    text(
                        title,
                        34 if not compact else 28,
                        INK,
                        ft.FontWeight.BOLD,
                        font_family="SF Pro Rounded",
                    ),
                    text(subtitle, 15, MUTED),
                ],
                spacing=8,
            ),
            menu,
        ],
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        vertical_alignment=ft.CrossAxisAlignment.START,
    )
