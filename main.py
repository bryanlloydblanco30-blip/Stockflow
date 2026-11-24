"""
main.py
StockFlow backend API entry point for the React desktop/web frontend (Decision D18).
Starts the local stdlib HTTP API server exposing backend/services/ and SQLite persistence.
"""

import sys
from pathlib import Path

# Add project root to path
ROOT_DIR = Path(__file__).resolve().parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))


def main():
    from backend.api_server import run_server

    port = 8000
    for arg in sys.argv[1:]:
        if arg.startswith("--port="):
            port = int(arg.split("=", 1)[1])

    run_server(host="127.0.0.1", port=port)


if __name__ == "__main__":
    main()
