"""
frontend/screens/start_screen.py
Hero landing page matching the Figma StartPage.
Left: Hero story & corner store illustration.
Right: Start window with navigation choices.
"""

try:
    import flet as ft
except ImportError:
    ft = None

from design.tokens import (
    COLOR_BG,
    COLOR_SURFACE,
    COLOR_BORDER,
    COLOR_BRAND_GREEN,
    COLOR_BRAND_GREEN_DARK,
    COLOR_SPARKLE,
    COLOR_TEXT_MAIN,
    COLOR_TEXT_MUTED,
)

START_NAV_OPTIONS = [
    ("home", "Home", "assets/229d1.svg", True),
    ("sell", "Sell", "assets/0b38a.svg", False),
    ("stock", "Stock", "assets/bf69b.svg", False),
    ("restock", "Restock", "assets/4022f.svg", False),
    ("reports", "Reports", "assets/b5de1.svg", False),
]


def render(on_select_page):
    """Renders the full Figma hero start page."""
    if ft is None:
        return None

    # Left story section
    brand_tag = ft.Row(
        controls=[
            ft.Image(src="assets/ea9fe.svg", width=48, height=48),
            ft.Text("StockFlow", size=18, weight=ft.FontWeight.W_600, color=COLOR_BRAND_GREEN_DARK),
        ],
        spacing=16,
    )

    hero_title = ft.Column(
        controls=[
            ft.Row([ft.Text("✦", size=24, color=COLOR_SPARKLE)]),
            ft.Text(
                "Your store.\nA little happier.",
                size=54,
                weight=ft.FontWeight.BOLD,
                color=COLOR_BRAND_GREEN_DARK,
                height=1.1,
            ),
            ft.Text(
                "Everything you need for a good day of shopkeeping.",
                size=17,
                color=COLOR_TEXT_MUTED,
            ),
        ],
        spacing=12,
    )

    hero_shop_img = ft.Image(
        src="assets/051ce.svg",
        width=520,
        height=280,
        fit=ft.ImageFit.CONTAIN,
    )

    hero_footer = ft.Column(
        controls=[
            ft.Text(
                "Small shop. Big possibilities.",
                size=23,
                weight=ft.FontWeight.BOLD,
                color=COLOR_BRAND_GREEN_DARK,
            ),
            ft.Text(
                "Sell, restock, and keep your business growing — all in one place.",
                size=16,
                color=COLOR_TEXT_MUTED,
            ),
        ],
        spacing=6,
    )

    story_section = ft.Column(
        controls=[brand_tag, ft.Container(height=20), hero_title, hero_shop_img, hero_footer],
        spacing=16,
        expand=True,
    )

    # Right start window
    window_header = ft.Column(
        controls=[
            ft.Text("StockFlow", size=28, weight=ft.FontWeight.BOLD, color=COLOR_BRAND_GREEN_DARK),
            ft.Text("Choose where you'd like to start.", size=16, color=COLOR_TEXT_MUTED),
        ],
        spacing=8,
    )

    nav_buttons = []
    for page_id, label, icon_path, is_primary in START_NAV_OPTIONS:
        bg_col = COLOR_BRAND_GREEN if is_primary else "#F3F5EC"
        txt_col = "#FFFFFF" if is_primary else "#4F7967"

        btn = ft.Container(
            content=ft.Row(
                controls=[
                    ft.Image(src=icon_path, width=26, height=26),
                    ft.Text(label, size=17, weight=ft.FontWeight.BOLD, color=txt_col, expand=True),
                ],
                spacing=16,
            ),
            bgcolor=bg_col,
            border_radius=26,
            padding=ft.padding.symmetric(horizontal=24, vertical=16),
            on_click=lambda _, pid=page_id: on_select_page(pid),
            cursor=ft.MouseCursor.CLICK,
        )
        nav_buttons.append(btn)

    window_content = ft.Container(
        content=ft.Column(
            controls=[
                window_header,
                ft.Container(height=24),
                ft.Column(controls=nav_buttons, spacing=14),
            ],
            spacing=0,
            alignment=ft.MainAxisAlignment.CENTER,
        ),
        width=440,
        bgcolor=COLOR_SURFACE,
        border=ft.border.all(2, "#E0DEC4"),
        border_radius=44,
        padding=48,
    )

    return ft.Container(
        content=ft.Row(
            controls=[story_section, window_content],
            alignment=ft.MainAxisAlignment.CENTER,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=64,
        ),
        bgcolor=COLOR_BG,
        padding=ft.padding.symmetric(horizontal=64, vertical=40),
        expand=True,
    )
