"""Conexión SQLite en modo solo lectura a la base de OpenCode."""

from __future__ import annotations

import sqlite3
from pathlib import Path

from ..config import DEFAULT_DB


def open_readonly(path: Path | None = None) -> sqlite3.Connection:
    """Abre opencode.db en modo lectura. Nunca escribe.

    Usa file: URI con mode=ro para garantizar solo lectura aunque
    la conexión reciba executes por error.
    """
    db = Path(path) if path is not None else DEFAULT_DB
    if not db.exists():
        raise FileNotFoundError(f"no existe la base de OpenCode: {db}")
    uri = f"{db.resolve().as_uri()}?mode=ro"
    con = sqlite3.connect(uri, uri=True)
    con.row_factory = sqlite3.Row
    return con
