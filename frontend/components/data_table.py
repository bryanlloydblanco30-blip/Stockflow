"""
frontend/components/data_table.py
Figma-styled DataTable container with clean borders and padded rows.
"""

try:
    import flet as ft
except ImportError:
    ft = None

from design.tokens import (
    COLOR_BORDER,
    COLOR_BORDER_LIGHT,
    COLOR_SURFACE_ALT,
    COLOR_TEXT_MUTED,
    COLOR_TEXT_MAIN,
)


def build_data_table(headers: list[str], rows: list[list]):
    """Builds a table container styled exactly like the Figma mockups."""
    if ft is None:
        return None

    col_controls = [
        ft.DataColumn(
            label=ft.Text(h, size=13, weight=ft.FontWeight.W_500, color=COLOR_TEXT_MUTED)
        )
        for h in headers
    ]

    row_controls = []
    for r in rows:
        cells = []
        for c in r:
            if isinstance(c, ft.Control):
                cells.append(ft.DataCell(c))
            else:
                cells.append(
                    ft.DataCell(
                        ft.Text(str(c), size=15, color=COLOR_TEXT_MAIN)
                    )
                )
        row_controls.append(ft.DataRow(cells=cells))

    table = ft.DataTable(
        columns=col_controls,
        rows=row_controls,
        heading_row_color=COLOR_SURFACE_ALT,
        divider_thickness=1,
        column_spacing=24,
        horizontal_margin=16,
    )

    return ft.Container(
        content=table,
        border=ft.border.all(1, COLOR_BORDER),
        border_radius=30,
        bgcolor=COLOR_SURFACE_ALT,
        padding=12,
        expand=True,
    )
