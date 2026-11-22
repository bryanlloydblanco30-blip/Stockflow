"""
frontend/components/summary_card.py
StatCard metric indicator matching the Figma design.
Tones: yellow, green, peach, lavender, rose.
"""

try:
    import flet as ft
except ImportError:
    ft = None

from design.tokens import (
    TONE_YELLOW_BG,
    TONE_GREEN_BG,
    TONE_GREEN_TEXT,
    TONE_PEACH_BG,
    TONE_LAVENDER_BG,
    TONE_ROSE_BG,
    TONE_CARD_BORDER,
    COLOR_TEXT_MAIN,
    COLOR_TEXT_MUTED,
)

TONE_MAP = {
    "yellow": (TONE_YELLOW_BG, COLOR_TEXT_MAIN),
    "green": (TONE_GREEN_BG, TONE_GREEN_TEXT),
    "peach": (TONE_PEACH_BG, COLOR_TEXT_MAIN),
    "lavender": (TONE_LAVENDER_BG, COLOR_TEXT_MAIN),
    "rose": (TONE_ROSE_BG, COLOR_TEXT_MAIN),
}


def build_summary_card(label: str, value: str, tone: str = "yellow", on_click=None):
    """Builds a rounded Figma StatCard."""
    if ft is None:
        return None

    bg_color, text_color = TONE_MAP.get(tone, (TONE_YELLOW_BG, COLOR_TEXT_MAIN))

    return ft.Container(
        content=ft.Column(
            controls=[
                ft.Text(label, size=14, weight=ft.FontWeight.W_600, color=COLOR_TEXT_MUTED),
                ft.Text(value, size=31, weight=ft.FontWeight.BOLD, color=text_color),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            spacing=18,
        ),
        bgcolor=bg_color,
        border=ft.border.all(1, TONE_CARD_BORDER),
        border_radius=30,
        padding=ft.padding.symmetric(vertical=24, horizontal=24),
        expand=True,
        on_click=on_click,
    )
