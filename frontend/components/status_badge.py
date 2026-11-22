"""
frontend/components/status_badge.py
Status badge matching the Figma design.
Tones: green, red, amber.
"""

try:
    import flet as ft
except ImportError:
    ft = None

from design.tokens import (
    BADGE_GREEN_BG,
    BADGE_GREEN_TEXT,
    BADGE_RED_BG,
    BADGE_RED_TEXT,
    BADGE_AMBER_BG,
    BADGE_AMBER_TEXT,
)

BADGE_TONE_MAP = {
    "green": (BADGE_GREEN_BG, BADGE_GREEN_TEXT),
    "red": (BADGE_RED_BG, BADGE_RED_TEXT),
    "amber": (BADGE_AMBER_BG, BADGE_AMBER_TEXT),
}


def build_status_badge(text: str, tone: str = "green"):
    """Builds a pill-shaped status badge matching Figma."""
    if ft is None:
        return None

    # Normalize tone
    tone_key = tone.lower()
    if tone_key in ["urgent", "expired"]:
        tone_key = "red"
    elif tone_key in ["soon", "low", "near expiry"]:
        tone_key = "amber"
    elif tone_key in ["ok", "untracked"]:
        tone_key = "green"

    bg_color, text_color = BADGE_TONE_MAP.get(tone_key, (BADGE_GREEN_BG, BADGE_GREEN_TEXT))

    return ft.Container(
        content=ft.Text(text, size=13, weight=ft.FontWeight.W_500, color=text_color),
        bgcolor=bg_color,
        border_radius=18,
        padding=ft.padding.symmetric(horizontal=14, vertical=4),
        alignment=ft.alignment.center,
    )
