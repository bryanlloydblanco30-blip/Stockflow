"""
frontend/screens/sell_states_screen.py
Sell states screen matching the Figma SellStatesPage:
- Empty cart
- Not enough stock
- Only expired stock left
"""

try:
    import flet as ft
except ImportError:
    ft = None

from design.tokens import (
    COLOR_BORDER,
    COLOR_SURFACE_ALT,
    COLOR_TEXT_MAIN,
    COLOR_TEXT_MUTED,
    BTN_BLUE_BG,
    BTN_BLUE_TEXT,
    TONE_YELLOW_BG,
    TONE_ROSE_BG,
)
from frontend.components.stepper import build_stepper


def render():
    """Renders the Figma Sell States screen."""
    if ft is None:
        return None

    # Card 1: Empty cart
    card1 = ft.Container(
        content=ft.Column(
            controls=[
                ft.Row([ft.Image(src="assets/0b38a.svg", width=22, height=22), ft.Text("Empty cart", size=14, color=COLOR_TEXT_MUTED)]),
                ft.Text("Cart is empty. Scan a product to start.", size=17, weight=ft.FontWeight.BOLD, color=COLOR_TEXT_MAIN),
                ft.Container(
                    content=ft.Text("Checkout", size=16, color="#666674"),
                    bgcolor="#CFCED8",
                    border_radius=24,
                    padding=ft.padding.symmetric(horizontal=24, vertical=12),
                    alignment=ft.alignment.center,
                ),
            ],
            spacing=16,
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        ),
        bgcolor=COLOR_SURFACE_ALT,
        border=ft.border.all(1, COLOR_BORDER),
        border_radius=30,
        padding=28,
        expand=True,
    )

    # Card 2: Not enough stock
    card2 = ft.Container(
        content=ft.Column(
            controls=[
                ft.Row([ft.Image(src="assets/bf69b.svg", width=22, height=22), ft.Text("Not enough stock", size=14, color=COLOR_TEXT_MUTED)]),
                ft.Text("Fresh Milk 1L × 5", size=16, color=COLOR_TEXT_MAIN),
                ft.Text("Only 3 left. Lower the quantity.", size=17, weight=ft.FontWeight.BOLD, color="#C70028"),
                build_stepper(5),
            ],
            spacing=16,
        ),
        bgcolor=TONE_YELLOW_BG,
        border=ft.border.all(1, COLOR_BORDER),
        border_radius=30,
        padding=28,
        expand=True,
    )

    # Card 3: Only expired stock left
    card3 = ft.Container(
        content=ft.Column(
            controls=[
                ft.Row([ft.Image(src="assets/bf69b.svg", width=22, height=22), ft.Text("Only expired stock left", size=14, color=COLOR_TEXT_MUTED)]),
                ft.Text("Only expired stock left. It cannot be sold.", size=17, weight=ft.FontWeight.BOLD, color="#C70028"),
                ft.Text("Go to write-off list ›", size=15, weight=ft.FontWeight.W_600, color="#C70028"),
            ],
            spacing=16,
        ),
        bgcolor=TONE_ROSE_BG,
        border=ft.border.all(1, COLOR_BORDER),
        border_radius=30,
        padding=28,
        expand=True,
    )

    return ft.Column(
        controls=[
            ft.Row(controls=[card1, card2], spacing=24),
            ft.Container(height=24),
            ft.Row(controls=[card3, ft.Container(expand=True)], spacing=24),
        ],
        spacing=0,
        expand=True,
    )
