"""
frontend/screens/stock_list_screen.py
Stock screen matching the Figma StockPage:
- + Register Product (blue button)
- Search products or barcode
- Chips: All, Low, Near Expiry, Untracked
- DataTable with Barcode, Name, Category, Units, Cost, Price, Status
- Closing copy
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
    COLOR_BRAND_GREEN,
)
from frontend.components.status_badge import build_status_badge
from frontend.components.data_table import build_data_table

PRODUCTS_DATA = [
    ["4800010001", "Pandesal pack", "Bread", "12", "₱32.00", "₱45.00", "Expires soon", "red"],
    ["4800010002", "Sardines 155g", "Canned", "3", "₱20.00", "₱28.00", "Low", "amber"],
    ["4800010003", "Bottled water 500ml", "Drinks", "48", "₱14.00", "₱25.00", "OK", "green"],
    ["4800010004", "Notebook", "School supplies", "20", "₱40.00", "₱58.00", "Untracked", "green"],
    ["4800010005", "Instant noodles", "Canned", "60", "₱9.00", "₱14.00", "OK", "green"],
    ["4800010006", "Loaf bread", "Bread", "9", "₱48.00", "₱65.00", "Near expiry", "amber"],
]


def render(on_product_click=None, on_register_click=None):
    """Renders the Figma Stock inventory screen."""
    if ft is None:
        return None

    register_btn = ft.Container(
        content=ft.Text("+ Register Product", size=15, weight=ft.FontWeight.W_600, color=BTN_BLUE_TEXT),
        bgcolor=BTN_BLUE_BG,
        border_radius=24,
        padding=ft.padding.symmetric(horizontal=24, vertical=14),
        on_click=lambda _: on_register_click() if on_register_click else None,
    )

    search_field = ft.TextField(
        hint_text="Search products or barcode",
        border_color=COLOR_BORDER,
        border_radius=11,
        bgcolor=COLOR_SURFACE_ALT,
        color=COLOR_TEXT_MAIN,
        content_padding=ft.padding.symmetric(horizontal=17, vertical=14),
    )

    # Filter chips
    chips_row = ft.Row(
        controls=[
            ft.Container(content=ft.Text("All", size=14, weight=ft.FontWeight.W_600, color=BTN_BLUE_TEXT), bgcolor=BTN_BLUE_BG, border_radius=24, padding=ft.padding.symmetric(horizontal=24, vertical=12)),
            ft.Container(content=ft.Text("Low", size=14, color=BTN_LAVENDER_TEXT), bgcolor=BTN_LAVENDER_BG, border_radius=24, padding=ft.padding.symmetric(horizontal=24, vertical=12)),
            ft.Container(content=ft.Text("Near Expiry", size=14, color=BTN_LAVENDER_TEXT), bgcolor=BTN_LAVENDER_BG, border_radius=24, padding=ft.padding.symmetric(horizontal=24, vertical=12)),
            ft.Container(content=ft.Text("Untracked", size=14, color=BTN_LAVENDER_TEXT), bgcolor=BTN_LAVENDER_BG, border_radius=24, padding=ft.padding.symmetric(horizontal=24, vertical=12)),
        ],
        spacing=14,
    )

    # Table rows
    table_rows = []
    for p in PRODUCTS_DATA:
        badge = build_status_badge(p[6], p[7])
        table_rows.append([p[0], p[1], p[2], p[3], p[4], p[5], badge])

    data_table = build_data_table(
        headers=["Barcode", "Name", "Category", "Units", "Cost", "Price", "Status"],
        rows=table_rows,
    )

    closing_copy = ft.Column(
        controls=[
            ft.Text("Every shelf, a little more organized.", size=24, color=COLOR_BRAND_GREEN),
            ft.Text("Find your products, check availability, and spot what needs attention.", size=15, color=COLOR_TEXT_MUTED),
        ],
        spacing=6,
    )

    return ft.Column(
        controls=[
            ft.Row([ft.Container(expand=True), register_btn]),
            ft.Container(height=12),
            search_field,
            ft.Container(height=16),
            chips_row,
            ft.Container(height=16),
            data_table,
            ft.Container(height=32),
            closing_copy,
        ],
        spacing=0,
        expand=True,
        scroll=ft.ScrollMode.AUTO,
    )
