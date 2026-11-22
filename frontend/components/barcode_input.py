"""
frontend/components/barcode_input.py
Scan row component matching Figma:
[ Input field ] [ Scan (blue) ] [ Simulate (lavender) ]
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
    COLOR_TEXT_MAIN,
)


def build_barcode_input(input_ref=None, on_submit=None, on_scan=None, on_simulate=None):
    """Builds the Figma scan row."""
    if ft is None:
        return None

    text_field = ft.TextField(
        ref=input_ref,
        hint_text="Scan or type barcode",
        border_color=COLOR_BORDER,
        border_radius=11,
        bgcolor=COLOR_SURFACE_ALT,
        color=COLOR_TEXT_MAIN,
        content_padding=ft.padding.symmetric(horizontal=17, vertical=14),
        expand=True,
        on_submit=on_submit,
    )

    scan_btn = ft.Container(
        content=ft.Text("Scan", size=15, weight=ft.FontWeight.W_600, color=BTN_BLUE_TEXT),
        bgcolor=BTN_BLUE_BG,
        border_radius=24,
        padding=ft.padding.symmetric(horizontal=24, vertical=14),
        alignment=ft.alignment.center,
        on_click=on_scan,
    )

    sim_btn = ft.Container(
        content=ft.Text("Simulate", size=15, weight=ft.FontWeight.W_600, color=BTN_LAVENDER_TEXT),
        bgcolor=BTN_LAVENDER_BG,
        border_radius=24,
        padding=ft.padding.symmetric(horizontal=24, vertical=14),
        alignment=ft.alignment.center,
        on_click=on_simulate,
    )

    return ft.Row(
        controls=[text_field, scan_btn, sim_btn],
        spacing=12,
        alignment=ft.MainAxisAlignment.START,
    )
