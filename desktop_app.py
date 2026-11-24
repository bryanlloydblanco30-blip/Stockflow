"""
desktop_app.py
StockFlow PC Desktop Application Launcher.
Starts the embedded StockFlow server and opens a dedicated native desktop application window.
"""

from __future__ import annotations

import os
import socket
import subprocess
import sys
import time
import urllib.request
import webbrowser
from pathlib import Path
from threading import Thread

# Support PyInstaller frozen environment
if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
    BUNDLE_DIR = Path(sys._MEIPASS)
else:
    BUNDLE_DIR = Path(__file__).resolve().parent

if str(BUNDLE_DIR) not in sys.path:
    sys.path.insert(0, str(BUNDLE_DIR))

from backend.api_server import run_server


def find_free_port(preferred: int = 8000) -> int:
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(("127.0.0.1", preferred))
            return preferred
    except OSError:
        pass
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def wait_for_server(url: str, timeout: float = 10.0) -> bool:
    start = time.time()
    while time.time() - start < timeout:
        try:
            with urllib.request.urlopen(f"{url}/api/health", timeout=1.0) as resp:
                if resp.status == 200:
                    return True
        except Exception:
            time.sleep(0.1)
    return False


def get_desktop_browser_cmd(url: str) -> list[str] | None:
    """Finds MS Edge or Chrome to run in dedicated standalone desktop app mode."""
    candidates = [
        # Edge on Windows
        os.path.expandvars(r"%ProgramFiles(x86)%\Microsoft\Edge\Application\msedge.exe"),
        os.path.expandvars(r"%ProgramFiles%\Microsoft\Edge\Application\msedge.exe"),
        os.path.expandvars(r"%LocalAppData%\Microsoft\Edge\Application\msedge.exe"),
        # Chrome on Windows
        os.path.expandvars(r"%ProgramFiles%\Google\Chrome\Application\chrome.exe"),
        os.path.expandvars(r"%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe"),
        os.path.expandvars(r"%LocalAppData%\Google\Chrome\Application\chrome.exe"),
    ]
    for exe in candidates:
        if exe and os.path.isfile(exe):
            return [
                exe,
                f"--app={url}",
                "--window-size=1280,820",
                "--app-id=StockFlow",
            ]
    return None


def main():
    port = find_free_port(8000)
    base_url = f"http://127.0.0.1:{port}"

    # Start backend server in a background daemon thread
    server_thread = Thread(
        target=run_server,
        kwargs={"host": "127.0.0.1", "port": port},
        daemon=True,
    )
    server_thread.start()

    if not wait_for_server(base_url, timeout=10.0):
        print(f"Error: StockFlow server failed to start on {base_url}", file=sys.stderr)
        sys.exit(1)

    print(f"StockFlow desktop server is running at {base_url}")

    # Launch desktop application window
    app_cmd = get_desktop_browser_cmd(base_url)
    if app_cmd:
        try:
            proc = subprocess.Popen(app_cmd)
            # Wait for user to close the desktop window
            proc.wait()
            sys.exit(0)
        except Exception as e:
            print(f"Could not open native desktop window: {e}. Falling back to default browser.", file=sys.stderr)

    webbrowser.open(base_url)
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
