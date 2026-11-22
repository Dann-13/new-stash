"""Ajustes de la aplicación: rutas, tiempos y archivo config.toml."""

from __future__ import annotations

import os
import sys
import tomllib
from dataclasses import dataclass, field
from pathlib import Path


def _default_db() -> Path:
    base = os.environ.get("XDG_DATA_HOME")
    root = Path(base) if base else Path.home() / ".local" / "share"
    return root / "opencode" / "opencode.db"


def config_file() -> Path:
    """Ruta de config.toml: %APPDATA% en Windows, ~/.config en Linux."""
    if sys.platform == "win32":
        root = Path(os.environ.get("APPDATA", Path.home()))
    else:
        base = os.environ.get("XDG_CONFIG_HOME")
        root = Path(base) if base else Path.home() / ".config"
    return root / "opencode-usage" / "config.toml"


DEFAULT_DB = _default_db()


@dataclass(frozen=True)
class Settings:
    db_path: Path = field(default_factory=lambda: DEFAULT_DB)
    refresh_seconds: float = 5.0
    default_days: int | None = 30  # None = todo el histórico
    monthly_budget_usd: float | None = None  # None = sin presupuesto
    config_error: str | None = None


def load_settings(path: Path | None = None) -> Settings:
    """Lee config.toml. Si falta, usa valores por defecto sin error.

    Valores inválidos se ignoran y se explican en ``config_error``.
    """
    path = path or config_file()
    if not path.exists():
        return Settings()
    try:
        raw = tomllib.loads(path.read_text(encoding="utf-8"))
    except (OSError, tomllib.TOMLDecodeError) as exc:
        return Settings(config_error=f"config.toml no se pudo leer: {exc}")

    budget = raw.get("monthly_budget_usd")
    if budget is None:
        return Settings()
    if isinstance(budget, bool) or not isinstance(budget, (int, float)) or budget <= 0:
        return Settings(
            config_error="monthly_budget_usd debe ser un número mayor que 0"
        )
    return Settings(monthly_budget_usd=float(budget))
