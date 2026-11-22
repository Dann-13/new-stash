"""Punto de entrada: python -m opencode_usage."""

from __future__ import annotations

import argparse
from pathlib import Path

from .app import UsageApp
from .config import DEFAULT_DB, Settings


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="opencode-usage",
        description="Dashboard en terminal del uso de tokens de OpenCode",
    )
    parser.add_argument(
        "--db", type=Path, default=DEFAULT_DB,
        help="ruta a opencode.db (default: %(default)s)",
    )
    parser.add_argument(
        "--refresh", type=float, default=5.0, metavar="SEG",
        help="segundos entre refrescos en vivo (default: %(default)s)",
    )
    parser.add_argument(
        "--days", type=int, default=30, metavar="N",
        help="ventana inicial en días; 0 = todo (default: %(default)s)",
    )
    args = parser.parse_args()

    settings = Settings(
        db_path=args.db,
        refresh_seconds=args.refresh,
        default_days=None if args.days == 0 else args.days,
    )
    UsageApp(settings).run()


if __name__ == "__main__":
    main()
