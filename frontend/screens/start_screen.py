"""
frontend/screens/start_screen.py
Landing / splash page with branding and navigation choices.
Ported from frontend/StockFlow/main.py StockFlow.start_page().
"""

from __future__ import annotations

import flet as ft

from design.tokens import COLOR_BRAND_GREEN, COLOR_TEXT_MUTED
from frontend.components.primitives import text, rounded_button, card
from frontend.components.nav_rail import NAV

GREEN = COLOR_BRAND_GREEN
MUTED = COLOR_TEXT_MUTED
ASSETS = "assets"


def render(on_select_page, compact: bool = False) -> ft.Control:
    """Render the start / landing page."""
    story = ft.Container(
        ft.Column(
            [
                ft.Row(
                    [
                        ft.Image(src=f"{ASSETS}/ea9fe.svg", width=48, height=48),
                        text("StockFlow", 13, "#5D765D"),
                    ],
                    spacing=18,
                ),
                ft.Container(height=38),
                text(
                    "Your store.\nA little happier.",
                    52 if not compact else 40,
                    GREEN,
                    ft.FontWeight.BOLD,
                    font_family="SF Pro Rounded",
                ),
                text(
                    "Everything you need for a good day of shopkeeping.",
                    17,
                    MUTED,
                ),
                ft.Image(
                    src=f"{ASSETS}/051ce.svg",
                    width=600 if not compact else None,
                    fit=ft.ImageFit.CONTAIN,
                ),
                text(
                    "Small shop. Big possibilities.",
                    22,
                    GREEN,
                    ft.FontWeight.BOLD,
                ),
                text(
                    "Sell, restock, and keep your business growing — all in one place.",
                    15,
                    MUTED,
                ),
            ],
            spacing=18,
        ),
        expand=True,
    )

    choices = ft.Column(
        [
            text(
                "StockFlow",
                27,
                GREEN,
                ft.FontWeight.BOLD,
                font_family="SF Pro Rounded",
            ),
            text("Choose where you'd like to start.", 16, MUTED),
            ft.Container(height=18),
            *[
                rounded_button(
                    label,
                    lambda _, r=route: on_select_page(r),
                    GREEN if route == "home" else "#F3F5EC",
                    "#FFFFFF" if route == "home" else GREEN,
                    icon=active if route == "home" else icon,
                    width=340,
                )
                for route, label, icon, active in NAV
            ],
        ],
        spacing=14,
    )

    choice_card = card(choices, padding=48, width=440)

    content = (
        ft.Column([story, choice_card], spacing=32)
        if compact
        else ft.Row(
            [story, choice_card],
            spacing=70,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )
    )

    return ft.Container(
        content,
        padding=ft.padding.symmetric(
            horizontal=36 if compact else 100, vertical=52
        ),
        expand=True,
    )
