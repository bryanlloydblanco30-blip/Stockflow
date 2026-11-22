"""
frontend/components/primitives.py
Shared helper functions used across all screens: text(), rounded_button(),
card(), stat_card(), badge(), summary_line(), data_table().
Ported from frontend/StockFlow/main.py.
"""

from __future__ import annotations

import flet as ft

from design.tokens import (
    COLOR_BORDER,
    COLOR_SURFACE,
    COLOR_TEXT_MAIN,
    COLOR_TEXT_MUTED,
    BORDER_RADIUS_BTN,
    BORDER_RADIUS_CARD,
    BORDER_RADIUS_BADGE,
)

# ── Short aliases used throughout ─────────────────────────────────────
INK = COLOR_TEXT_MAIN
MUTED = COLOR_TEXT_MUTED
BORDER = COLOR_BORDER
SURFACE = COLOR_SURFACE


def text(
    value: str,
    size: int = 15,
    color: str = INK,
    weight=None,
    **kwargs,
) -> ft.Text:
    """Create a styled Text control."""
    return ft.Text(value, size=size, color=color, weight=weight, **kwargs)


def rounded_button(
    label: str,
    on_click=None,
    bgcolor: str = SURFACE,
    color: str = INK,
    icon=None,
    width: int | None = None,
    disabled: bool = False,
) -> ft.ElevatedButton:
    """Pill-shaped button matching the Figma design."""
    return ft.ElevatedButton(
        content=label,
        icon=icon,
        on_click=on_click,
        disabled=disabled,
        width=width,
        height=48,
        style=ft.ButtonStyle(
            bgcolor=bgcolor,
            color=color,
            shape=ft.RoundedRectangleBorder(radius=BORDER_RADIUS_BTN),
            padding=ft.padding.symmetric(horizontal=24),
            elevation=0,
        ),
    )


def card(
    content,
    bgcolor: str = SURFACE,
    padding: int = 24,
    expand=False,
    **kwargs,
) -> ft.Container:
    """Rounded card container with 1px border."""
    return ft.Container(
        content=content,
        bgcolor=bgcolor,
        border=ft.border.all(1, BORDER),
        border_radius=BORDER_RADIUS_CARD,
        padding=padding,
        expand=expand,
        **kwargs,
    )


def stat_card(
    label: str,
    value: str,
    bgcolor: str = SURFACE,
    value_color: str = INK,
) -> ft.Container:
    """Dashboard statistic card with label and large value."""
    return card(
        ft.Column(
            [
                text(label, 13, MUTED, ft.FontWeight.W_600),
                text(value, 28, value_color, ft.FontWeight.BOLD),
            ],
            spacing=18,
        ),
        bgcolor=bgcolor,
        padding=24,
        expand=True,
        height=145,
    )


def badge(label: str, tone: str = "green") -> ft.Container:
    """Small coloured pill badge for status indicators."""
    tones = {
        "green": ("#D8F0DF", "#175E36"),
        "red": ("#FFDCE1", "#C30023"),
        "amber": ("#FFEDC9", "#8C5100"),
    }
    bg, fg = tones.get(tone, tones["green"])
    return ft.Container(
        text(label, 12, fg),
        bgcolor=bg,
        border_radius=BORDER_RADIUS_BADGE,
        padding=ft.padding.symmetric(horizontal=14, vertical=5),
        alignment=ft.alignment.center,
    )


def summary_line(label: str, value: str, large: bool = False) -> ft.Control:
    """Key-value row used in the checkout summary panel."""
    return ft.Row(
        [
            text(label, 16 if large else 14),
            text(value, 26 if large else 14, INK, ft.FontWeight.BOLD),
        ],
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
    )


def data_table(headers: list[str], rows) -> ft.Control:
    """Horizontally scrollable data table."""

    def cell(value):
        return ft.DataCell(
            value if isinstance(value, ft.Control) else text(str(value), 14)
        )

    table = ft.DataTable(
        columns=[
            ft.DataColumn(text(header, 12, MUTED, ft.FontWeight.W_600))
            for header in headers
        ],
        rows=[
            ft.DataRow(cells=[cell(value) for value in row])
            for row in rows
        ],
        column_spacing=26,
        horizontal_lines=ft.BorderSide(1, "#EBE8E1"),
        heading_row_height=48,
        data_row_min_height=52,
    )
    return ft.Row([table], scroll=ft.ScrollMode.AUTO)
