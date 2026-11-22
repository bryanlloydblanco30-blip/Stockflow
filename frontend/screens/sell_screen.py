"""
frontend/screens/sell_screen.py
Sell screen matching the Figma SellPage.
Split pane:
- Left: Barcode scan row + Cart table with steppers, unit price, subtotal, and remove.
- Right: Sticky summary card (items, subtotal, tax 0%, total, Checkout button) + message card.
"""

try:
    import flet as ft
except ImportError:
    ft = None

from design.tokens import (
    BTN_BLUE_BG,
    BTN_BLUE_TEXT,
    BTN_LAVENDER_BG,
    BTN_LAVENDER_TEXT,
    COLOR_BORDER,
    COLOR_SURFACE_ALT,
    COLOR_TEXT_MAIN,
    COLOR_TEXT_MUTED,
    CALLOUT_GREEN_BG,
    CALLOUT_GREEN_BORDER,
    COLOR_BRAND_GREEN_DARK,
)
from frontend.components.barcode_input import build_barcode_input
from frontend.components.stepper import build_stepper


def render(on_checkout_click=None):
    """Renders the Figma Sell POS split-view layout."""
    if ft is None:
        return None

    # Sample cart data from Figma mockup
    cart_items = [
        {"name": "Pandesal pack", "qty": 1, "price": 45.00},
        {"name": "Sardines 155g", "qty": 2, "price": 28.00},
        {"name": "Bottled water 500ml", "qty": 1, "price": 25.00},
        {"name": "Notebook", "qty": 1, "price": 58.00},
    ]

    total_amount = sum(item["qty"] * item["price"] for item in cart_items)
    total_items = sum(item["qty"] for item in cart_items)

    # Scan row
    scan_row = build_barcode_input()

    # Cart header row
    cart_header = ft.Container(
        content=ft.Row(
            controls=[
                ft.Text("Item", size=13, weight=ft.FontWeight.W_500, color=COLOR_TEXT_MUTED, expand=3),
                ft.Text("Qty", size=13, weight=ft.FontWeight.W_500, color=COLOR_TEXT_MUTED, expand=2),
                ft.Text("Unit price", size=13, weight=ft.FontWeight.W_500, color=COLOR_TEXT_MUTED, expand=2),
                ft.Text("Line total", size=13, weight=ft.FontWeight.W_500, color=COLOR_TEXT_MUTED, expand=2),
                ft.Container(width=80),
            ],
        ),
        padding=ft.padding.symmetric(vertical=12),
        border=ft.border.only(bottom=ft.BorderSide(1, "#EBE8E1")),
    )

    # Cart rows
    cart_row_controls = []
    for item in cart_items:
        line_subtotal = item["qty"] * item["price"]

        remove_btn = ft.Container(
            content=ft.Text("Remove", size=13, weight=ft.FontWeight.W_500, color=BTN_LAVENDER_TEXT),
            bgcolor=BTN_LAVENDER_BG,
            border_radius=18,
            padding=ft.padding.symmetric(horizontal=16, vertical=8),
        )

        row_ctrl = ft.Container(
            content=ft.Row(
                controls=[
                    ft.Text(item["name"], size=15, weight=ft.FontWeight.W_500, color=COLOR_TEXT_MAIN, expand=3),
                    ft.Container(content=build_stepper(item["qty"]), expand=2),
                    ft.Text(f"₱{item['price']:.2f}", size=15, color=COLOR_TEXT_MAIN, expand=2),
                    ft.Text(f"₱{line_subtotal:.2f}", size=15, weight=ft.FontWeight.BOLD, color=COLOR_TEXT_MAIN, expand=2),
                    ft.Container(content=remove_btn, width=80),
                ],
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=ft.padding.symmetric(vertical=16),
            border=ft.border.only(bottom=ft.BorderSide(1, "#EBE8E1")),
        )
        cart_row_controls.append(row_ctrl)

    cart_panel = ft.Container(
        content=ft.Column(
            controls=[
                scan_row,
                ft.Container(height=16),
                cart_header,
                *cart_row_controls,
            ],
            spacing=0,
        ),
        bgcolor=COLOR_SURFACE_ALT,
        border=ft.border.all(1, COLOR_BORDER),
        border_radius=30,
        padding=24,
        expand=2,
    )

    # Right summary panel
    summary_panel = ft.Container(
        content=ft.Column(
            controls=[
                ft.Text("Summary", size=18, weight=ft.FontWeight.BOLD, color="#5D6475"),
                ft.Container(height=16),
                ft.Row([ft.Text("Items", size=15, color=COLOR_TEXT_MUTED), ft.Text(str(total_items), size=16, weight=ft.FontWeight.BOLD)], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Row([ft.Text("Subtotal", size=15, color=COLOR_TEXT_MUTED), ft.Text(f"₱{total_amount:.2f}", size=16, weight=ft.FontWeight.BOLD)], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Row([ft.Text("Tax 0%", size=15, color=COLOR_TEXT_MUTED), ft.Text("₱0.00", size=16, weight=ft.FontWeight.BOLD)], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Divider(color="#E8E4DD", thickness=1, height=32),
                ft.Row(
                    controls=[
                        ft.Text("Total", size=18, weight=ft.FontWeight.BOLD),
                        ft.Text(f"₱{total_amount:.2f}", size=31, weight=ft.FontWeight.BOLD, color=COLOR_TEXT_MAIN),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                ft.Container(height=24),
                ft.Container(
                    content=ft.Text("Checkout (Enter)", size=18, weight=ft.FontWeight.BOLD, color=BTN_BLUE_TEXT),
                    bgcolor=BTN_BLUE_BG,
                    border_radius=24,
                    padding=ft.padding.symmetric(vertical=16),
                    alignment=ft.alignment.center,
                    on_click=lambda _: on_checkout_click() if on_checkout_click else None,
                ),
            ],
            spacing=8,
        ),
        bgcolor=COLOR_SURFACE_ALT,
        border=ft.border.all(1, COLOR_BORDER),
        border_radius=30,
        padding=28,
    )

    message_card = ft.Container(
        content=ft.Column(
            controls=[
                ft.Text("A smooth checkout,\na happy customer.", size=22, color=COLOR_BRAND_GREEN_DARK),
                ft.Text("Scan items, review, and you're ready.", size=15, color=COLOR_TEXT_MUTED),
            ],
            spacing=8,
        ),
        bgcolor=CALLOUT_GREEN_BG,
        border=ft.border.all(1, CALLOUT_GREEN_BORDER),
        border_radius=28,
        padding=24,
    )

    checkout_column = ft.Column(
        controls=[summary_panel, message_card],
        spacing=24,
        expand=1,
    )

    return ft.Row(
        controls=[cart_panel, checkout_column],
        spacing=24,
        vertical_alignment=ft.CrossAxisAlignment.START,
        expand=True,
    )
