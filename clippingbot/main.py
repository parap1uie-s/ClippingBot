from __future__ import annotations

from .config import load_settings
from .feishu_longconn import run_long_connection
from .server import run_server


def main() -> None:
    settings = load_settings()
    mode = settings.feishu_delivery_mode.lower()
    if mode == "longconn":
        run_long_connection()
        return
    run_server()


if __name__ == "__main__":
    main()

