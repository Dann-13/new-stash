"""Punto de entrada: python -m opencode_usage."""

from __future__ import annotations

import argparse
from dataclasses import replace
from pathlib import Path

from .app import UsageApp
from .config import DEFAULT_DB, Settings, config_file, load_settings
from .i18n import resolve_language, set_language


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="opencode-usage",
        description="Dashboard en terminal del uso de tokens de OpenCode",
        epilog=f"Configuración opcional: {config_file()}",
    )
    parser.add_argument(
        "--db", type=Path, default=None,
        help=f"ruta a opencode.db (default: {DEFAULT_DB})",
    )
    parser.add_argument(
        "--refresh", type=float, default=None, metavar="SEG",
        help="segundos entre revisiones de cambios (default: 5)",
    )
    parser.add_argument(
        "--days", type=int, default=None, metavar="N",
        help="ventana inicial en días; 0 = todo (default: 30)",
    )
    parser.add_argument(
        "--lang", choices=["es", "en"], default=None,
        help="idioma de la interfaz (default: config.toml o auto)",
    )
    args = parser.parse_args()

    settings: Settings = load_settings()
    set_language(args.lang or resolve_language(settings.language))
    changes: dict[str, object] = {}
    if args.db is not None:
        changes["db_path"] = args.db
    if args.refresh is not None:
        changes["refresh_seconds"] = args.refresh
    if args.days is not None:
        changes["default_days"] = None if args.days == 0 else args.days
    UsageApp(replace(settings, **changes)).run()


if __name__ == "__main__":
    main()
