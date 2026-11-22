"""
frontend/components/nav_rail.py
Sidebar navigation and mobile bottom bar.
Ported from frontend/StockFlow/main.py StockFlow.sidebar() and .mobile_nav().
"""

from __future__ import annotations

import flet as ft

from design.tokens import (
    COLOR_BRAND_GREEN,
    COLOR_TEXT_MAIN,
    PALE_GREEN,
)
from frontend.components.primitives import text, card, rounded_button

# ── Navigation definition ─────────────────────────────────────────────
NAV = [
    ("home", "Home", ft.Icons.HOME_OUTLINED, ft.Icons.HOME_ROUNDED),
    ("sell", "Sell", ft.Icons.SHOPPING_CART_OUTLINED, ft.Icons.SHOPPING_CART_ROUNDED),
    ("stock", "Stock", ft.Icons.INVENTORY_2_OUTLINED, ft.Icons.INVENTORY_2_ROUNDED),
    ("restock", "Restock", ft.Icons.LOCAL_SHIPPING_OUTLINED, ft.Icons.LOCAL_SHIPPING_ROUNDED),
    ("reports", "Reports", ft.Icons.BAR_CHART_OUTLINED, ft.Icons.BAR_CHART_ROUNDED),
]

GREEN = COLOR_BRAND_GREEN
INK = COLOR_TEXT_MAIN
MUTED = "#69756B"
ASSETS = "assets"


def active_section(route: str) -> str:
    """Map sub-routes back to their parent nav section."""
    return {
        "sell_states": "sell",
        "adjust": "stock",
        "history": "reports",
    }.get(route, route)


def build_sidebar(active_page: str, on_navigate, on_back_to_start) -> ft.Control:
    """Build the full desktop sidebar with branding, nav items, and illustration."""
    active = active_section(active_page)

    nav_controls = []
    for route, label, icon, active_icon in NAV:
        selected = active == route
        nav_controls.append(
            ft.ListTile(
                leading=ft.Icon(
                    active_icon if selected else icon,
                    color="#FFFFFF" if selected else GREEN,
                ),
                title=text(
                    label, 15,
                    "#FFFFFF" if selected else "#4E7666",
                    ft.FontWeight.W_500,
                ),
                bgcolor=GREEN if selected else None,
                shape=ft.RoundedRectangleBorder(radius=26),
                on_click=lambda _, r=route: on_navigate(r),
            )
        )

    return card(
        ft.Column(
            [
                ft.Row(
                    [
                        ft.Image(src=f"{ASSETS}/18451.svg", width=42, height=42),
                        ft.Column(
                            [
                                text("StockFlow", 16, INK, ft.FontWeight.W_600),
                                text("POINT OF SALE", 9, MUTED),
                            ],
                            spacing=2,
                        ),
                    ]
                ),
                ft.Container(height=42),
                *nav_controls,
                ft.Container(height=20),
                ft.Image(src=f"{ASSETS}/45491.svg", height=132, fit=ft.ImageFit.CONTAIN),
                ft.Container(
                    ft.Column(
                        [
                            ft.Icon(ft.Icons.HOME_OUTLINED, color=GREEN),
                            text("Made for the\ncorner of the world.", 14, GREEN),
                        ]
                    ),
                    bgcolor="#FFE8D7",
                    border=ft.border.all(1, "#F3C9AD"),
                    border_radius=28,
                    padding=20,
                ),
                ft.Container(expand=True),
                rounded_button("Back", lambda _: on_back_to_start(), width=190),
            ],
            spacing=8,
            expand=True,
        ),
        padding=18,
        expand=True,
    )


def build_mobile_nav(active_page: str, on_navigate) -> ft.Control:
    """Build the bottom navigation bar for compact/mobile layout."""
    active = active_section(active_page)
    return ft.NavigationBar(
        selected_index=next(
            (i for i, item in enumerate(NAV) if item[0] == active), 0
        ),
        bgcolor="#FFFEFA",
        indicator_color=PALE_GREEN,
        on_change=lambda e: on_navigate(NAV[e.control.selected_index][0]),
        destinations=[
            ft.NavigationBarDestination(
                icon=icon, selected_icon=active_icon, label=label
            )
            for _, label, icon, active_icon in NAV
        ],
    )
