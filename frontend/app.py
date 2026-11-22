"""
frontend/app.py
StockFlow desktop master application container.
Class-based architecture ported from frontend/StockFlow/main.py.
Coordinates sidebar navigation, top header, responsive layout, and dynamic page routing.
"""

from __future__ import annotations

import flet as ft

from design.tokens import (
    COLOR_BG,
    COLOR_BRAND_GREEN,
)
from frontend.components.nav_rail import build_sidebar, build_mobile_nav
from frontend.components.dialogs import build_page_header

# Screens
from frontend.screens import (
    start_screen,
    home_screen,
    sell_screen,
    stock_list_screen,
    restock_screen,
    reports_screen,
    sell_states_screen,
    adjust_screen,
    history_screen,
)

GREEN = COLOR_BRAND_GREEN


class StockFlowApp:
    """Main application controller — manages routing, state, and layout."""

    def __init__(self, page: ft.Page):
        self.page = page
        self.route = "start"

        # Screen-level state
        self.stock_filter = "All"
        self.stock_query = ""
        self.report_period = "Week"
        self.history_filter = "All"

        # Page configuration
        page.title = "StockFlow"
        page.bgcolor = COLOR_BG
        page.padding = 0
        page.theme_mode = ft.ThemeMode.LIGHT
        page.theme = ft.Theme(
            color_scheme_seed=GREEN,
            use_material3=True,
            font_family="Inter",
        )
        page.fonts = {
            "Inter": "https://static.figma.com/font/Inter_1",
            "SF Pro Rounded": "https://static.figma.com/font/SF-Pro-Rounded-Bold_1",
        }
        page.on_resized = self._on_resize

        self.render()

    # ── Navigation ────────────────────────────────────────────────────

    def go(self, route: str):
        """Navigate to a route."""
        self.route = route
        self.render()

    def _on_resize(self, _):
        self.render()

    @property
    def compact(self) -> bool:
        """True when the window is narrower than 920px (mobile-like)."""
        return bool(self.page.width and self.page.width < 920)

    # ── Rendering ─────────────────────────────────────────────────────

    def render(self):
        """Clear and rebuild the entire page."""
        self.page.controls.clear()

        if self.route == "start":
            self.page.add(
                start_screen.render(
                    on_select_page=lambda r: self.go(r),
                    compact=self.compact,
                )
            )
        else:
            self.page.add(self._app_shell())

        self.page.update()

    def _app_shell(self) -> ft.Control:
        """The main app layout: sidebar + header + current screen."""
        header = build_page_header(
            page_id=self.route,
            on_navigate=lambda r: self.go(r),
            compact=self.compact,
        )

        screen_body = self._current_view()

        content = ft.Column(
            [header, screen_body],
            spacing=22,
            expand=True,
            scroll=ft.ScrollMode.AUTO,
        )

        if self.compact:
            return ft.Column(
                [
                    build_mobile_nav(self.route, lambda r: self.go(r)),
                    ft.Container(content, padding=20, expand=True),
                ],
                spacing=0,
                expand=True,
            )

        sidebar = build_sidebar(
            active_page=self.route,
            on_navigate=lambda r: self.go(r),
            on_back_to_start=lambda: self.go("start"),
        )

        return ft.Row(
            [
                ft.Container(sidebar, width=268, padding=24),
                ft.Container(
                    content,
                    expand=True,
                    padding=ft.padding.only(top=38, right=44, bottom=44),
                ),
            ],
            spacing=34,
            expand=True,
            vertical_alignment=ft.CrossAxisAlignment.START,
        )

    def _current_view(self) -> ft.Control:
        """Return the screen content for the current route."""
        c = self.compact

        if self.route == "home":
            return home_screen.render(
                on_navigate=lambda r: self.go(r),
                compact=c,
            )
        elif self.route == "sell":
            return sell_screen.render(compact=c)
        elif self.route == "stock":
            return stock_list_screen.render(
                on_product_click=lambda: self.go("adjust"),
                stock_filter=self.stock_filter,
                stock_query=self.stock_query,
                on_filter_change=lambda v: self._set_stock_filter(v),
                on_query_change=lambda e: self._set_stock_query(e.control.value),
                compact=c,
            )
        elif self.route == "restock":
            return restock_screen.render(compact=c)
        elif self.route == "reports":
            return reports_screen.render(
                on_drill_down=lambda _: self.go("history"),
                report_period=self.report_period,
                on_period_change=lambda v: self._set_report_period(v),
                compact=c,
            )
        elif self.route == "sell_states":
            return sell_states_screen.render(compact=c)
        elif self.route == "adjust":
            return adjust_screen.render(
                on_cancel=lambda: self.go("stock"),
                compact=c,
            )
        elif self.route == "history":
            return history_screen.render(
                history_filter=self.history_filter,
                on_filter_change=lambda v: self._set_history_filter(v),
                compact=c,
            )
        # Fallback
        return home_screen.render(
            on_navigate=lambda r: self.go(r),
            compact=c,
        )

    # ── State helpers ─────────────────────────────────────────────────

    def _set_stock_filter(self, value: str):
        self.stock_filter = value
        self.render()

    def _set_stock_query(self, value: str):
        self.stock_query = value
        self.render()

    def _set_report_period(self, value: str):
        self.report_period = value
        self.render()

    def _set_history_filter(self, value: str):
        self.history_filter = value
        self.render()


def main(page: ft.Page):
    """Flet app entry point."""
    StockFlowApp(page)
