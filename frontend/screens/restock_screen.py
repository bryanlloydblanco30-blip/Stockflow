"""
frontend/screens/restock_screen.py
Restock screen matching the Figma RestockPage:
- Chips: Priority Queue (blue) vs Fast / Slow Movers (lavender)
- DataTable: Score, Product, Days of cover, 14-day speed, Suggested qty, Urgency
- Restock callout banner
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
    CALLOUT_GREEN_BG,
    CALLOUT_GREEN_BORDER,
    COLOR_BRAND_GREEN_DARK,
    COLOR_TEXT_MUTED,
)
from frontend.components.status_badge import build_status_badge
from frontend.components.data_table import build_data_table


def render():
    """Renders the Figma Restock priority queue screen."""
    if ft is None:
        return None

    chips_row = ft.Row(
        controls=[
            ft.Container(
                content=ft.Text("Priority Queue", size=15, weight=ft.FontWeight.W_600, color=BTN_BLUE_TEXT),
                bgcolor=BTN_BLUE_BG,
                border_radius=24,
                padding=ft.padding.symmetric(horizontal=32, vertical=14),
            ),
            ft.Container(
                content=ft.Text("Fast / Slow Movers", size=15, weight=ft.FontWeight.W_500, color=BTN_LAVENDER_TEXT),
                bgcolor=BTN_LAVENDER_BG,
                border_radius=24,
                padding=ft.padding.symmetric(horizontal=32, vertical=14),
            ),
        ],
        spacing=16,
    )

    restock_rows = [
        ["92", "Sardines 155g", "1.5", "2.0 / day", "24", build_status_badge("Urgent", "red")],
        ["85", "Bottled water 500ml", "3.0", "16 / day", "60", build_status_badge("Urgent", "red")],
        ["61", "Pencil HB", "6.0", "1.0 / day", "12", build_status_badge("Soon", "amber")],
        ["48", "Instant noodles", "9.0", "6.5 / day", "40", build_status_badge("Soon", "amber")],
    ]

    table = build_data_table(
        headers=["Score", "Product", "Days of cover", "14-day speed", "Suggested qty", "Urgency"],
        rows=restock_rows,
    )

    callout = ft.Container(
        content=ft.Row(
            controls=[
                ft.Image(src="assets/4022f.svg", width=36, height=36),
                ft.Column(
                    controls=[
                        ft.Text(
                            "Keep your favorites on the shelf.",
                            size=20,
                            weight=ft.FontWeight.W_500,
                            color=COLOR_BRAND_GREEN_DARK,
                        ),
                        ft.Text(
                            "Start with urgent items, then work your way down the priority queue.",
                            size=15,
                            color=COLOR_TEXT_MUTED,
                        ),
                    ],
                    spacing=6,
                    expand=True,
                ),
            ],
            spacing=20,
        ),
        bgcolor=CALLOUT_GREEN_BG,
        border=ft.border.all(1, CALLOUT_GREEN_BORDER),
        border_radius=28,
        padding=24,
    )

    return ft.Column(
        controls=[
            chips_row,
            ft.Container(height=24),
            table,
            ft.Container(height=32),
            callout,
        ],
        spacing=0,
        expand=True,
        scroll=ft.ScrollMode.AUTO,
    )
