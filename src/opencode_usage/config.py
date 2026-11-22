"""Ajustes de la aplicación: rutas y tiempos."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

DEFAULT_DB = Path.home() / ".local" / "share" / "opencode" / "opencode.db"


@dataclass(frozen=True)
class Settings:
    db_path: Path = field(default_factory=lambda: DEFAULT_DB)
    refresh_seconds: float = 5.0
    default_days: int | None = 30  # None = todo el histórico
