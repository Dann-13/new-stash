"""Ajustes de la aplicación: rutas y tiempos."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path


def _default_db() -> Path:
    base = os.environ.get("XDG_DATA_HOME")
    root = Path(base) if base else Path.home() / ".local" / "share"
    return root / "opencode" / "opencode.db"


DEFAULT_DB = _default_db()


@dataclass(frozen=True)
class Settings:
    db_path: Path = field(default_factory=lambda: DEFAULT_DB)
    refresh_seconds: float = 5.0
    default_days: int | None = 30  # None = todo el histórico
