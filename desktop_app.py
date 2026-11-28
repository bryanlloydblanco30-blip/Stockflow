"""
desktop_app.py
StockFlow Standalone PC Desktop Application (pywebview + WebView2).
Runs backend logic and the compiled React UI in a single process with zero HTTP server or ports.
"""

from __future__ import annotations

import ctypes
import json
import logging
import os
import sys
import traceback
from pathlib import Path
from typing import Any, Dict

APP_VERSION = "1.1.0"

# Support PyInstaller frozen environment
if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
    BUNDLE_DIR = Path(sys._MEIPASS)
else:
    BUNDLE_DIR = Path(__file__).resolve().parent

if str(BUNDLE_DIR) not in sys.path:
    sys.path.insert(0, str(BUNDLE_DIR))

from backend.api_server import StockFlowBackend, dispatch_api
from backend.db.connection import get_app_data_dir


def _setup_logging(log_path: Path) -> logging.Logger:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        filename=str(log_path),
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
    )
    return logging.getLogger("stockflow")


def _show_error_dialog(title: str, message: str) -> None:
    if os.name == "nt":
        try:
            ctypes.windll.user32.MessageBoxW(0, message, title, 0x10)
            return
        except Exception:
            pass
    print(f"{title}: {message}", file=sys.stderr)


class PyWebViewApi:
    """In-process JS-to-Python bridge exposed as window.pywebview.api."""

    def __init__(self, backend: StockFlowBackend) -> None:
        self._backend = backend

    def request(self, method: str, url: str, body_json: str = "") -> Dict[str, Any]:
        body: Dict[str, Any] | None = None
        if body_json:
            body = json.loads(body_json)
        status, data = dispatch_api(self._backend, method, url, body)
        return {"status": status, "data": data}

    def get_app_info(self) -> Dict[str, str]:
        return {
            "version": APP_VERSION,
            "db_path": str(self._backend.db_path),
        }


def main() -> None:
    app_data_dir = get_app_data_dir()
    log_path = app_data_dir / "stockflow.log"
    logger = _setup_logging(log_path)

    try:
        import webview

        dist_index = BUNDLE_DIR / "frontend" / "dist" / "index.html"
        if not dist_index.is_file():
            raise FileNotFoundError(
                f"Built UI not found at {dist_index}. Run 'npm run build' in frontend/ first."
            )

        logger.info("Starting StockFlow v%s", APP_VERSION)
        backend = StockFlowBackend(auto_seed=False)
        logger.info("Database ready at %s (%d products)", backend.db_path, len(backend.state.products))

        api = PyWebViewApi(backend)
        window = webview.create_window(
            title=f"StockFlow v{APP_VERSION}",
            url=dist_index.as_uri(),
            js_api=api,
            width=1280,
            height=820,
            min_size=(960, 640),
        )
        webview.start(
            gui="edgechromium",
            http_server=False,
            private_mode=False,
            storage_path=str(app_data_dir / "webview_profile"),
        )
        logger.info("StockFlow window closed cleanly.")
    except Exception as exc:
        logger.error("Startup/runtime failure:\n%s", traceback.format_exc())
        _show_error_dialog(
            f"StockFlow v{APP_VERSION} - Startup Error",
            f"StockFlow could not start:\n\n{exc}\n\nDetails were written to:\n{log_path}",
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
