"""
frontend/screens/adjust_screen.py
Stock count adjustment screen matching the Figma AdjustPage:
- Cancel button
- Left: Form card (Batch select, Current count, New count, Reason, Save button, history note)
- Right: "A fresh count" message card
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
    COLOR_TEXT_MUTED,
    CALLOUT_GREEN_BG,
    CALLOUT_GREEN_BORDER,
    COLOR_BRAND_GREEN_DARK,
)


def render(on_cancel):
    """Renders the Figma Adjust count screen."""
    if ft is None:
        return None

    cancel_btn = ft.Container(
        content=ft.Text("Cancel", size=15, weight=ft.FontWeight.W_600, color=BTN_LAVENDER_TEXT),
        bgcolor=BTN_LAVENDER_BG,
        border_radius=24,
        padding=ft.padding.symmetric(horizontal=28, vertical=14),
        on_click=lambda _: on_cancel(),
        cursor=ft.MouseCursor.CLICK,
    )

    # Left form card
    batch_dropdown = ft.Dropdown(
        options=[ft.dropdown.Option("Batch A · exp 12 Nov 2026")],
        value="Batch A · exp 12 Nov 2026",
        border_color=COLOR_BORDER,
        border_radius=11,
        bgcolor=COLOR_SURFACE_ALT,
    )

    current_count_field = ft.TextField(
        value="8",
        read_only=True,
        border_color=COLOR_BORDER,
        border_radius=11,
        bgcolor="#F3F5EC",
    )

    new_count_field = ft.TextField(
        value="6",
        border_color=COLOR_BORDER,
        border_radius=11,
        bgcolor=COLOR_SURFACE_ALT,
    )

    reason_field = ft.TextField(
        value="Counted 6 on shelf",
        border_color=COLOR_BORDER,
        border_radius=11,
        bgcolor=COLOR_SURFACE_ALT,
    )

    save_btn = ft.Container(
        content=ft.Text("Save adjustment", size=16, weight=ft.FontWeight.BOLD, color=BTN_BLUE_TEXT),
        bgcolor=BTN_BLUE_BG,
        border_radius=24,
        padding=ft.padding.symmetric(vertical=16),
        alignment=ft.alignment.center,
        cursor=ft.MouseCursor.CLICK,
    )

    history_note = ft.Text(
        "Saved with old count, new count and reason. History is never edited.",
        size=13,
        color=COLOR_TEXT_MUTED,
    )

    form_card = ft.Container(
        content=ft.Column(
            controls=[
                ft.Text("Batch", size=14, color=COLOR_TEXT_MUTED),
                batch_dropdown,
                ft.Text("Current count", size=14, color=COLOR_TEXT_MUTED),
                current_count_field,
                ft.Text("New count (after physical check)", size=14, color=COLOR_TEXT_MUTED),
                new_count_field,
                ft.Text("Reason", size=14, color=COLOR_TEXT_MUTED),
                reason_field,
                ft.Container(height=12),
                save_btn,
                history_note,
            ],
            spacing=10,
        ),
        bgcolor=COLOR_SURFACE_ALT,
        border=ft.border.all(1, COLOR_BORDER),
        border_radius=30,
        padding=28,
        expand=2,
    )

    # Right message card
    fresh_card = ft.Container(
        content=ft.Column(
            controls=[
                ft.Image(src="assets/bf69b.svg", width=36, height=36),
                ft.Text("A fresh count.", size=22, weight=ft.FontWeight.W_500, color=COLOR_BRAND_GREEN_DARK),
                ft.Text(
                    "Count what's on your shelf,\nthen leave a reason to keep\nyour stock history clear.",
                    size=15,
                    color=COLOR_TEXT_MUTED,
                ),
            ],
            spacing=14,
        ),
        bgcolor=CALLOUT_GREEN_BG,
        border=ft.border.all(1, CALLOUT_GREEN_BORDER),
        border_radius=28,
        padding=24,
        expand=1,
    )

    return ft.Column(
        controls=[
            ft.Row([ft.Container(expand=True), cancel_btn]),
            ft.Container(height=16),
            ft.Row([form_card, fresh_card], spacing=24, vertical_alignment=ft.CrossAxisAlignment.START),
        ],
        spacing=0,
        expand=True,
    )
