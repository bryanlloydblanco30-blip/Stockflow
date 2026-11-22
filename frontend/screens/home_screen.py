"""
frontend/screens/home_screen.py
Home dashboard matching the Figma HomePage.
- START SALE button (peach)
- 4 StatCards: Today's Sales, Today's Profit, Low Stock Items, Near Expiry Batches
- Needs attention DataTable
- Green callout banner
"""

try:
    import flet as ft
except ImportError:
    ft = None

from design.tokens import (
    BTN_PEACH_BG,
    BTN_PEACH_TEXT,
    CALLOUT_GREEN_BG,
    CALLOUT_GREEN_BORDER,
    COLOR_BRAND_GREEN_DARK,
    COLOR_TEXT_MUTED,
)
from frontend.components.summary_card import build_summary_card
from frontend.components.status_badge import build_status_badge
from frontend.components.data_table import build_data_table


def render(on_navigate):
    """Renders the Figma Home page."""
    if ft is None:
        return None

    # Top START SALE button
    start_sale_btn = ft.Container(
        content=ft.Text("START SALE", size=15, weight=ft.FontWeight.BOLD, color=BTN_PEACH_TEXT),
        bgcolor=BTN_PEACH_BG,
        border_radius=24,
        padding=ft.padding.symmetric(horizontal=32, vertical=14),
        on_click=lambda _: on_navigate("sell"),
    )

    # 4 StatCards
    stat_cards = ft.Row(
        controls=[
            build_summary_card("Today's Sales", "₱4,860.00", tone="yellow"),
            build_summary_card("Today's Profit", "₱1,120.00", tone="green"),
            build_summary_card("Low Stock Items", "7", tone="peach"),
            build_summary_card("Near Expiry Batches", "4", tone="lavender"),
        ],
        spacing=18,
    )

    # Needs attention table
    attention_rows = [
        ["Pandesal pack", "Expires in 1 day", build_status_badge("Red", "red")],
        ["Canned sardines 155g", "3 units left", build_status_badge("Amber", "amber")],
        ["Bottled water 500ml", "Reorder level reached", build_status_badge("Amber", "amber")],
        ["Loaf bread", "Expires in 3 days", build_status_badge("Amber", "amber")],
        ["Pencil HB", "6 units left", build_status_badge("Low", "amber")],
    ]
    attention_table = build_data_table(
        headers=["Product", "Issue", "Urgency"],
        rows=attention_rows,
    )

    needs_attention_panel = ft.Container(
        content=ft.Column(
            controls=[
                ft.Text("Needs attention", size=21, weight=ft.FontWeight.W_600),
                ft.Container(height=8),
                attention_table,
            ],
            spacing=12,
        ),
        bgcolor="#FFFDFB",
        border=ft.border.all(1, "#E3E0D2"),
        border_radius=30,
        padding=28,
    )

    # Green callout banner
    callout = ft.Container(
        content=ft.Row(
            controls=[
                ft.Column(
                    controls=[
                        ft.Text(
                            "Ready for your next customer?",
                            size=21,
                            weight=ft.FontWeight.W_500,
                            color=COLOR_BRAND_GREEN_DARK,
                        ),
                        ft.Text(
                            "Start a sale, check your shelves, and keep things moving.",
                            size=15,
                            color=COLOR_TEXT_MUTED,
                        ),
                    ],
                    spacing=6,
                    expand=True,
                ),
                ft.Image(src="assets/0b38a.svg", width=32, height=32),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        ),
        bgcolor=CALLOUT_GREEN_BG,
        border=ft.border.all(1, CALLOUT_GREEN_BORDER),
        border_radius=28,
        padding=ft.padding.symmetric(horizontal=28, vertical=22),
        on_click=lambda _: on_navigate("sell"),
    )

    return ft.Column(
        controls=[
            ft.Row([ft.Container(expand=True), start_sale_btn]),
            ft.Container(height=10),
            stat_cards,
            ft.Container(height=24),
            needs_attention_panel,
            ft.Container(height=24),
            callout,
        ],
        spacing=0,
        expand=True,
        scroll=ft.ScrollMode.AUTO,
    )
