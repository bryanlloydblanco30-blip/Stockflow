"""
frontend/screens/reports_screen.py
Reports screen matching the Figma ReportsPage:
- Period chips: Day, Week, Month, Custom
- 4 StatCards: Revenue, Gross profit, Margin, COGS
- Sales and profit trend chart
- 4 Report link buttons
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
    COLOR_TEXT_MUTED,
)
from frontend.components.summary_card import build_summary_card


def render(on_drill_down=None):
    """Renders the Figma Reports analytics screen."""
    if ft is None:
        return None

    # Period chips
    period_chips = ft.Row(
        controls=[
            ft.Container(content=ft.Text("Day", size=14, color=BTN_LAVENDER_TEXT), bgcolor=BTN_LAVENDER_BG, border_radius=24, padding=ft.padding.symmetric(horizontal=24, vertical=12)),
            ft.Container(content=ft.Text("Week", size=14, weight=ft.FontWeight.BOLD, color=BTN_BLUE_TEXT), bgcolor=BTN_BLUE_BG, border_radius=24, padding=ft.padding.symmetric(horizontal=24, vertical=12)),
            ft.Container(content=ft.Text("Month", size=14, color=BTN_LAVENDER_TEXT), bgcolor=BTN_LAVENDER_BG, border_radius=24, padding=ft.padding.symmetric(horizontal=24, vertical=12)),
            ft.Container(content=ft.Text("Custom", size=14, color=BTN_LAVENDER_TEXT), bgcolor=BTN_LAVENDER_BG, border_radius=24, padding=ft.padding.symmetric(horizontal=24, vertical=12)),
        ],
        spacing=12,
        alignment=ft.MainAxisAlignment.END,
    )

    # 4 StatCards
    stat_cards = ft.Row(
        controls=[
            build_summary_card("Revenue", "₱31,400.00", tone="yellow"),
            build_summary_card("Gross profit", "₱8,250.00", tone="green"),
            build_summary_card("Margin", "26.3%", tone="yellow"),
            build_summary_card("COGS", "₱23,150.00", tone="rose"),
        ],
        spacing=18,
    )

    # Bar chart matching the Figma 7 daily bars
    bar_data = [
        ("Mon", 44, "#D9EACD"),
        ("Tue", 62, "#FFD7BF"),
        ("Wed", 36, "#FFF0C7"),
        ("Thu", 72, "#E7DAF4"),
        ("Fri", 56, "#D9EACD"),
        ("Sat", 88, "#246448"),
        ("Sun", 66, "#FFD7BF"),
    ]

    bar_slots = []
    for day, height_pct, bar_color in bar_data:
        slot = ft.Column(
            controls=[
                ft.Container(
                    bgcolor=bar_color,
                    border_radius=ft.border_radius.only(top_left=18, top_right=18),
                    height=height_pct * 2,
                    width=48,
                ),
                ft.Text(day, size=13, color=COLOR_TEXT_MUTED),
            ],
            alignment=ft.MainAxisAlignment.END,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=10,
        )
        bar_slots.append(slot)

    chart_panel = ft.Container(
        content=ft.Column(
            controls=[
                ft.Text("Sales and profit trend", size=21, weight=ft.FontWeight.W_600),
                ft.Container(height=16),
                ft.Container(
                    content=ft.Row(controls=bar_slots, alignment=ft.MainAxisAlignment.SPACE_AROUND, expand=True),
                    height=240,
                    alignment=ft.alignment.bottom_center,
                ),
            ],
            spacing=0,
        ),
        bgcolor=COLOR_SURFACE_ALT,
        border=ft.border.all(1, COLOR_BORDER),
        border_radius=30,
        padding=28,
    )

    # Report link buttons
    links = [
        "Best and worst sellers ›",
        "Profit per item ›",
        "Spoilage loss ›",
        "Inventory value ›",
    ]
    link_buttons = [
        ft.Container(
            content=ft.Text(lbl, size=14, weight=ft.FontWeight.W_500, color=BTN_LAVENDER_TEXT),
            bgcolor=BTN_LAVENDER_BG,
            border_radius=24,
            padding=ft.padding.symmetric(horizontal=20, vertical=14),
            alignment=ft.alignment.center,
            expand=True,
            on_click=lambda _, l=lbl: on_drill_down(l) if on_drill_down else None,
        )
        for lbl in links
    ]

    report_links_row = ft.Row(controls=link_buttons, spacing=16)

    return ft.Column(
        controls=[
            period_chips,
            ft.Container(height=16),
            stat_cards,
            ft.Container(height=24),
            chart_panel,
            ft.Container(height=24),
            report_links_row,
        ],
        spacing=0,
        expand=True,
        scroll=ft.ScrollMode.AUTO,
    )
