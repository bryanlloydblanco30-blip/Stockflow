"""
frontend/app.py
StockFlow desktop master application container.
Coordinates sidebar navigation rail, top header with More menu, and dynamic page routing.
"""

import sys
from pathlib import Path

try:
    import flet as ft
except ImportError:
    ft = None

from design.tokens import COLOR_BG
from frontend.components.nav_rail import build_sidebar
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


def main(page):
    """Main desktop application entrypoint for Flet."""
    if ft is None:
        print("[Error] Flet is not installed.")
        return

    page.title = "StockFlow Desktop (Point of Sale)"
    page.bgcolor = COLOR_BG
    page.window.min_width = 1100
    page.window.min_height = 760
    page.padding = 0

    current_page = "start"
    workspace_container = ft.Container(expand=True)

    def navigate_to(page_id: str):
        nonlocal current_page
        current_page = page_id
        refresh_view()

    def get_screen_content(page_id: str):
        if page_id == "home":
            return home_screen.render(on_navigate=navigate_to)
        elif page_id == "sell":
            return sell_screen.render()
        elif page_id == "stock":
            return stock_list_screen.render(on_product_click=lambda: navigate_to("adjust"))
        elif page_id == "restock":
            return restock_screen.render()
        elif page_id == "reports":
            return reports_screen.render(on_drill_down=lambda _: navigate_to("history"))
        elif page_id == "sell-states":
            return sell_states_screen.render()
        elif page_id == "adjust":
            return adjust_screen.render(on_cancel=lambda: navigate_to("stock"))
        elif page_id == "history":
            return history_screen.render()
        return home_screen.render(on_navigate=navigate_to)

    def refresh_view():
        page.controls.clear()

        if current_page == "start":
            page.add(start_screen.render(on_select_page=navigate_to))
        else:
            sidebar = build_sidebar(
                active_page=current_page,
                on_navigate=navigate_to,
                on_back_to_start=lambda: navigate_to("start"),
            )

            header = build_page_header(
                page_id=current_page,
                on_navigate=navigate_to,
            )

            screen_body = get_screen_content(current_page)

            workspace = ft.Container(
                content=ft.Column(
                    controls=[
                        header,
                        ft.Container(height=24),
                        ft.Container(content=screen_body, expand=True),
                    ],
                    spacing=0,
                    expand=True,
                ),
                padding=ft.padding.only(top=14, bottom=40, right=24),
                expand=True,
            )

            layout = ft.Container(
                content=ft.Row(
                    controls=[sidebar, ft.Container(width=24), workspace],
                    spacing=0,
                    vertical_alignment=ft.CrossAxisAlignment.START,
                    expand=True,
                ),
                bgcolor=COLOR_BG,
                padding=24,
                expand=True,
            )

            page.add(layout)

        page.update()

    refresh_view()
