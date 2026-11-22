"""
main.py
StockFlow desktop application entry point.
Starts the Flet desktop app shell.
"""

import sys
from pathlib import Path

# Add project root to path
ROOT_DIR = Path(__file__).resolve().parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))


def main():
    print("StockFlow Desktop App Initializing...")
    try:
        import flet as ft
        from frontend.app import main as app_main

        is_web = "--web" in sys.argv
        view_mode = ft.AppView.WEB_BROWSER if is_web else ft.AppView.FLET_APP
        port = 8550 if is_web else 0

        ft.app(target=app_main, assets_dir="assets", port=port, view=view_mode)
    except ImportError:
        print("[Notice] Flet is not yet installed. Install with: pip install -r requirements.txt")


if __name__ == "__main__":
    main()
