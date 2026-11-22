"""
frontend/components/stepper.py
Quantity stepper control matching Figma: [ - ] count [ + ]
"""

try:
    import flet as ft
except ImportError:
    ft = None

from design.tokens import BTN_LAVENDER_BG, BTN_LAVENDER_TEXT, COLOR_TEXT_MAIN


def build_stepper(value: int, on_decrement=None, on_increment=None):
    """Builds the Figma pill stepper control."""
    if ft is None:
        return None

    btn_dec = ft.Container(
        content=ft.Text("−", size=18, weight=ft.FontWeight.BOLD, color=BTN_LAVENDER_TEXT),
        bgcolor=BTN_LAVENDER_BG,
        border_radius=18,
        width=36,
        height=36,
        alignment=ft.alignment.center,
        on_click=on_decrement,
    )

    count_txt = ft.Text(str(value), size=16, weight=ft.FontWeight.BOLD, color=COLOR_TEXT_MAIN)

    btn_inc = ft.Container(
        content=ft.Text("+", size=18, weight=ft.FontWeight.BOLD, color=BTN_LAVENDER_TEXT),
        bgcolor=BTN_LAVENDER_BG,
        border_radius=18,
        width=36,
        height=36,
        alignment=ft.alignment.center,
        on_click=on_increment,
    )

    return ft.Row(
        controls=[btn_dec, count_txt, btn_inc],
        spacing=12,
        alignment=ft.MainAxisAlignment.START,
    )
