"""
frontend/screens/reports_screen.py
Financial reports: period selector, stat cards, bar chart, drill-down links.
Ported from frontend/StockFlow/main.py StockFlow.reports().
"""

from __future__ import annotations

import flet as ft

from design.tokens import (
    COLOR_BRAND_GREEN,
    COLOR_TEXT_MAIN,
    COLOR_TEXT_MUTED,
    PALE_BLUE,
    PALE_GREEN,
    PALE_YELLOW,
    PALE_LAVENDER,
    PALE_ROSE,
)
from frontend.components.primitives import (
    text,
    rounded_button,
    card,
    stat_card,
)

GREEN = COLOR_BRAND_GREEN
INK = COLOR_TEXT_MAIN
MUTED = COLOR_TEXT_MUTED


def render(
    on_drill_down=None,
    report_period: str = "Week",
    on_period_change=None,
    compact: bool = False,
) -> ft.Control:
    """Render the reports / analytics screen."""

    periods = ft.Row(
        [
            rounded_button(
                option,
                lambda _, v=option: on_period_change(v) if on_period_change else None,
                PALE_BLUE if report_period == option else PALE_LAVENDER,
            )
            for option in ["Day", "Week", "Month", "Custom"]
        ],
        wrap=True,
        alignment=ft.MainAxisAlignment.END,
    )

    stats = ft.ResponsiveRow(
        [
            ft.Container(
                stat_card("Revenue", "₱31,400.00"), col={"sm": 6, "lg": 3}
            ),
            ft.Container(
                stat_card("Gross profit", "₱8,250.00", PALE_GREEN, "#1D6538"),
                col={"sm": 6, "lg": 3},
            ),
            ft.Container(
                stat_card("Margin", "26.3%", PALE_YELLOW),
                col={"sm": 6, "lg": 3},
            ),
            ft.Container(
                stat_card("COGS", "₱23,150.00", PALE_ROSE),
                col={"sm": 6, "lg": 3},
            ),
        ],
        spacing=16,
        run_spacing=16,
    )

    values = [44, 62, 36, 72, 56, 88, 66]
    colors = [
        "#D9EACD", "#FFD7BF", "#FFF0C7", "#E7DAF4",
        "#D9EACD", GREEN, "#FFD7BF",
    ]
    chart = ft.BarChart(
        bar_groups=[
            ft.BarChartGroup(
                x=i,
                bar_rods=[
                    ft.BarChartRod(
                        from_y=0,
                        to_y=value,
                        width=38,
                        color=colors[i],
                        border_radius=ft.border_radius.only(
                            top_left=12, top_right=12
                        ),
                    )
                ],
            )
            for i, value in enumerate(values)
        ],
        bottom_axis=ft.ChartAxis(
            labels=[
                ft.ChartAxisLabel(value=i, label=text(day, 12, MUTED))
                for i, day in enumerate(
                    ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
                )
            ]
        ),
        left_axis=ft.ChartAxis(labels_size=0),
        max_y=100,
        height=280,
        interactive=True,
    )

    links = ft.ResponsiveRow(
        [
            ft.Container(
                rounded_button(
                    label,
                    lambda _, l=label: on_drill_down(l) if on_drill_down else None,
                    PALE_LAVENDER,
                ),
                col={"sm": 6, "lg": 3},
            )
            for label in [
                "Best and worst sellers ›",
                "Profit per item ›",
                "Spoilage loss ›",
                "Inventory value ›",
            ]
        ],
        spacing=14,
        run_spacing=14,
    )

    return ft.Column(
        [
            periods,
            stats,
            card(
                ft.Column(
                    [
                        text(
                            "Sales and profit trend",
                            20,
                            INK,
                            ft.FontWeight.W_600,
                        ),
                        chart,
                    ]
                )
            ),
            links,
        ],
        spacing=22,
    )
