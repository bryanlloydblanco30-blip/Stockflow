"""
frontend/components/dialogs.py
Header component with More dropdown menu and confirmation dialogs matching Figma.
"""

try:
    import flet as ft
except ImportError:
    ft = None

from design.tokens import (
    COLOR_TEXT_MAIN,
    COLOR_TEXT_MUTED,
    COLOR_SPARKLE,
    COLOR_BORDER,
    BTN_LAVENDER_BG,
    BTN_LAVENDER_TEXT,
    COLOR_SURFACE,
)

PAGE_META = {
    "home": ("Home", "Your store at a glance"),
    "sell": ("Sell", "Build a sale and checkout"),
    "stock": ("Stock", "Manage products and availability"),
    "restock": ("Restock", "Plan your next replenishment"),
    "reports": ("Reports", "Understand your store performance"),
    "sell-states": ("Sell states", "Checkout and inventory availability states"),
    "adjust": ("Adjust count · Fresh Milk 1L", "Update the physical count for this batch"),
    "history": ("Transaction history", "Review sales and inventory movements"),
}


def build_page_header(page_id: str, on_navigate):
    """Builds the Figma page header with subtitle, title, sparkle, and More menu."""
    if ft is None:
        return None

    title, subtitle = PAGE_META.get(page_id, ("StockFlow", "Your store, simplified"))

    left_block = ft.Column(
        controls=[
            ft.Text("YOUR STORE, SIMPLIFIED", size=10, weight=ft.FontWeight.BOLD, color=COLOR_TEXT_MUTED),
            ft.Text(title, size=35, weight=ft.FontWeight.BOLD, color=COLOR_TEXT_MAIN),
            ft.Text(subtitle, size=16, color=COLOR_TEXT_MUTED),
        ],
        spacing=6,
    )

    sparkle = ft.Text("✦", size=28, color=COLOR_SPARKLE)

    # PopupMenu for More actions
    more_btn = ft.PopupMenuButton(
        content=ft.Container(
            content=ft.Text("More ⌄", size=16, weight=ft.FontWeight.W_500, color=COLOR_TEXT_MAIN),
            padding=ft.padding.symmetric(horizontal=24, vertical=12),
            border=ft.border.all(1, COLOR_BORDER),
            border_radius=24,
            bgcolor=COLOR_SURFACE,
        ),
        items=[
            ft.PopupMenuItem(
                text="Sell states",
                on_click=lambda _: on_navigate("sell-states"),
            ),
            ft.PopupMenuItem(
                text="Adjust stock",
                on_click=lambda _: on_navigate("adjust"),
            ),
            ft.PopupMenuItem(
                text="Transaction History",
                on_click=lambda _: on_navigate("history"),
            ),
        ],
    )

    right_block = ft.Row(
        controls=[sparkle, more_btn],
        spacing=24,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
    )

    return ft.Row(
        controls=[left_block, right_block],
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        vertical_alignment=ft.CrossAxisAlignment.START,
    )
