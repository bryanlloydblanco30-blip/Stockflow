"""
frontend/components/nav_rail.py
Sidebar component matching the Figma design:
Brand header, 5 nav buttons (Home, Sell, Stock, Restock, Reports),
shop companion illustration, "Made for the corner of the world" card, and Back button.
"""

from pathlib import Path
try:
    import flet as ft
except ImportError:
    ft = None

from design.tokens import (
    COLOR_SURFACE,
    COLOR_BORDER,
    COLOR_BRAND_GREEN,
    COLOR_BRAND_GREEN_DARK,
    COLOR_TEXT_MAIN,
    COLOR_TEXT_MUTED,
    CALLOUT_PEACH_BG,
    CALLOUT_PEACH_BORDER,
)

NAV_ITEMS = [
    ("home", "Home", "assets/af3ce.svg", "assets/229d1.svg"),
    ("sell", "Sell", "assets/0b38a.svg", "assets/5a3bb.svg"),
    ("stock", "Stock", "assets/bf69b.svg", "assets/5c8bf.svg"),
    ("restock", "Restock", "assets/4022f.svg", "assets/90354.svg"),
    ("reports", "Reports", "assets/b5de1.svg", "assets/3ba0c.svg"),
]


def build_sidebar(active_page: str, on_navigate, on_back_to_start):
    """Builds the 268px desktop sidebar exactly like Figma."""
    if ft is None:
        return None

    # Normalize active section
    section = active_page
    if active_page == "sell-states":
        section = "sell"
    elif active_page == "adjust":
        section = "stock"
    elif active_page == "history":
        section = "reports"

    # Brand header
    brand_logo = ft.Image(src="assets/18451.svg", width=42, height=42)
    brand_title = ft.Column(
        controls=[
            ft.Text("StockFlow", size=17, weight=ft.FontWeight.W_600, color=COLOR_TEXT_MAIN),
            ft.Text("POINT OF SALE", size=9, weight=ft.FontWeight.BOLD, color=COLOR_TEXT_MUTED),
        ],
        spacing=2,
    )
    brand_header = ft.Container(
        content=ft.Row(controls=[brand_logo, brand_title], spacing=12),
        on_click=lambda _: on_back_to_start(),
        cursor=ft.MouseCursor.CLICK,
    )

    # Nav buttons
    nav_buttons = []
    for page_id, label, icon_path, active_icon_path in NAV_ITEMS:
        is_active = (section == page_id)
        icon_to_use = active_icon_path if is_active else icon_path
        bg_col = COLOR_BRAND_GREEN if is_active else "transparent"
        txt_col = "#FFFFFF" if is_active else "#4E7666"

        btn = ft.Container(
            content=ft.Row(
                controls=[
                    ft.Image(src=icon_to_use, width=22, height=22),
                    ft.Text(label, size=16, weight=ft.FontWeight.W_500, color=txt_col),
                ],
                spacing=16,
            ),
            bgcolor=bg_col,
            border_radius=28,
            padding=ft.padding.symmetric(horizontal=20, vertical=14),
            on_click=lambda _, pid=page_id: on_navigate(pid),
            cursor=ft.MouseCursor.CLICK,
        )
        nav_buttons.append(btn)

    nav_column = ft.Column(controls=nav_buttons, spacing=9)

    # Shop companion illustration
    companion_img = ft.Image(src="assets/45491.svg", width=180, height=120, fit=ft.ImageFit.CONTAIN)

    # Made card
    made_card = ft.Container(
        content=ft.Column(
            controls=[
                ft.Image(src="assets/af3ce.svg", width=24, height=24),
                ft.Text(
                    "Made for the\ncorner of the world.",
                    size=15,
                    weight=ft.FontWeight.W_600,
                    color=COLOR_BRAND_GREEN_DARK,
                ),
            ],
            spacing=10,
        ),
        bgcolor=CALLOUT_PEACH_BG,
        border=ft.border.all(1, CALLOUT_PEACH_BORDER),
        border_radius=28,
        padding=20,
    )

    # Back button
    back_btn = ft.Container(
        content=ft.Text("Back", size=16, weight=ft.FontWeight.W_600, color=COLOR_BRAND_GREEN_DARK),
        bgcolor="#FFFFFF",
        border_radius=28,
        padding=ft.padding.symmetric(vertical=14),
        alignment=ft.alignment.center,
        on_click=lambda _: on_back_to_start(),
        cursor=ft.MouseCursor.CLICK,
    )

    return ft.Container(
        content=ft.Column(
            controls=[
                brand_header,
                ft.Container(height=30),
                nav_column,
                ft.Container(expand=True),
                ft.Container(content=companion_img, alignment=ft.alignment.center),
                made_card,
                ft.Container(height=12),
                back_btn,
            ],
            spacing=0,
            expand=True,
        ),
        width=268,
        bgcolor=COLOR_SURFACE,
        border=ft.border.all(1, COLOR_BORDER),
        border_radius=44,
        padding=ft.padding.all(22),
    )
