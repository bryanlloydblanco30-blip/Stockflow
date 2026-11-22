"""
frontend/screens/history_screen.py
Transaction history log screen matching the Figma HistoryPage:
- Filter chips: All, Sale, Receive, Void, Adjustment, Write-off
- DataTable with Date, Type, Details, Amount, and action button (Void last sale)
- Undo hint
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
    COLOR_TEXT_MUTED,
)
from frontend.components.status_badge import build_status_badge
from frontend.components.data_table import build_data_table

HISTORY_DATA = [
    ["7 Nov 10:42", "Sale", "3 items", "PHP 184.00", "green"],
    ["7 Nov 09:15", "Receive", "Fresh Milk 1L × 24", "PHP 1,152.00", "amber"],
    ["6 Nov 17:30", "Write-off", "Yogurt cup × 2", "PHP 70.00", "red"],
    ["6 Nov 12:05", "Sale", "2 items", "PHP 90.00", "green"],
]


def render(on_void_last=None):
    """Renders the Figma Transaction History screen."""
    if ft is None:
        return None

    # Filter chips
    filter_chips = ft.Row(
        controls=[
            ft.Container(content=ft.Text("All", size=14, weight=ft.FontWeight.BOLD, color=BTN_BLUE_TEXT), bgcolor=BTN_BLUE_BG, border_radius=24, padding=ft.padding.symmetric(horizontal=24, vertical=12)),
            ft.Container(content=ft.Text("Sale", size=14, color=BTN_LAVENDER_TEXT), bgcolor=BTN_LAVENDER_BG, border_radius=24, padding=ft.padding.symmetric(horizontal=24, vertical=12)),
            ft.Container(content=ft.Text("Receive", size=14, color=BTN_LAVENDER_TEXT), bgcolor=BTN_LAVENDER_BG, border_radius=24, padding=ft.padding.symmetric(horizontal=24, vertical=12)),
            ft.Container(content=ft.Text("Void", size=14, color=BTN_LAVENDER_TEXT), bgcolor=BTN_LAVENDER_BG, border_radius=24, padding=ft.padding.symmetric(horizontal=24, vertical=12)),
            ft.Container(content=ft.Text("Adjustment", size=14, color=BTN_LAVENDER_TEXT), bgcolor=BTN_LAVENDER_BG, border_radius=24, padding=ft.padding.symmetric(horizontal=24, vertical=12)),
            ft.Container(content=ft.Text("Write-off", size=14, color=BTN_LAVENDER_TEXT), bgcolor=BTN_LAVENDER_BG, border_radius=24, padding=ft.padding.symmetric(horizontal=24, vertical=12)),
        ],
        spacing=12,
    )

    # Table rows
    table_rows = []
    for i, r in enumerate(HISTORY_DATA):
        badge = build_status_badge(r[1], r[4])
        action = ""
        if i == 0:
            action = ft.Container(
                content=ft.Text("Void last sale", size=13, weight=ft.FontWeight.W_500, color=BTN_LAVENDER_TEXT),
                bgcolor=BTN_LAVENDER_BG,
                border_radius=18,
                padding=ft.padding.symmetric(horizontal=16, vertical=8),
                on_click=lambda _: on_void_last() if on_void_last else None,
                cursor=ft.MouseCursor.CLICK,
            )
        table_rows.append([r[0], badge, r[2], r[3], action])

    table = build_data_table(
        headers=["Date", "Type", "Details", "Amount", ""],
        rows=table_rows,
    )

    hint = ft.Text(
        "Undo is available only on the latest transaction.",
        size=14,
        color=COLOR_TEXT_MUTED,
    )

    return ft.Column(
        controls=[
            filter_chips,
            ft.Container(height=16),
            table,
            ft.Container(height=16),
            hint,
        ],
        spacing=0,
        expand=True,
        scroll=ft.ScrollMode.AUTO,
    )
