"""Fixtures: base SQLite en memoria con el esquema mínimo de session_message."""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime

import pytest

SCHEMA = """
CREATE TABLE session_message (
    id TEXT PRIMARY KEY,
    session_id TEXT NOT NULL,
    type TEXT NOT NULL,
    seq INTEGER NOT NULL,
    time_created INTEGER NOT NULL,
    time_updated INTEGER NOT NULL,
    data TEXT NOT NULL
)
"""


def _msg(
    id: str,
    session_id: str,
    ts: datetime,
    *,
    type: str = "assistant",
    model_id: str = "model-a",
    provider: str = "prov",
    agent: str = "build",
    inp: int = 0,
    out: int = 0,
    reasoning: int = 0,
    cache_read: int = 0,
    cache_write: int = 0,
    cost: float = 0.0,
    with_tokens: bool = True,
) -> tuple:
    data: dict = {
        "model": {"id": model_id, "providerID": provider},
        "agent": agent,
        "time": {"created": int(ts.timestamp() * 1000)},
    }
    if with_tokens:
        data["tokens"] = {
            "input": inp,
            "output": out,
            "reasoning": reasoning,
            "cache": {"read": cache_read, "write": cache_write},
        }
        data["cost"] = cost
    return (
        id,
        session_id,
        type,
        1,
        int(ts.timestamp() * 1000),
        int(ts.timestamp() * 1000),
        json.dumps(data),
    )


@pytest.fixture
def con() -> sqlite3.Connection:
    """Conexión en memoria con datos de prueba.

    Escenario:
    - 2026-11-18 10:00 (mié)  s1 build  model-a  in=1000 out=200 cost=0.01
    - 2026-11-18 15:00 (mié)  s1 build  model-a  in=500  out=100 cost=0.02
    - 2026-11-19 20:00 (jue)  s2 plan   model-b  in=300  out=400 cost=0.03
    - 1 assistant sin tokens (se ignora)
    - 1 mensaje user (se ignora)
    """
    con = sqlite3.connect(":memory:")
    con.row_factory = sqlite3.Row
    con.execute(SCHEMA)
    rows = [
        _msg("m1", "s1", datetime(2026, 11, 18, 10, 0),
             model_id="model-a", inp=1000, out=200, reasoning=50,
             cache_read=8000, cost=0.01),
        _msg("m2", "s1", datetime(2026, 11, 18, 15, 0),
             model_id="model-a", inp=500, out=100, reasoning=20,
             cache_read=4000, cost=0.02),
        _msg("m3", "s2", datetime(2026, 11, 19, 20, 0),
             model_id="model-b", provider="prov2", agent="plan",
             inp=300, out=400, cache_read=1000, cost=0.03),
        _msg("m4", "s2", datetime(2026, 11, 19, 21, 0), with_tokens=False),
        _msg("m5", "s2", datetime(2026, 11, 19, 22, 0), type="user",
             inp=9999, out=9999),
    ]
    con.executemany(
        "INSERT INTO session_message VALUES (?, ?, ?, ?, ?, ?, ?)", rows
    )
    con.commit()
    return con
