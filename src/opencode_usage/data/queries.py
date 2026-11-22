"""Agregaciones de uso sobre la base de OpenCode.

Fuente de datos: tabla ``session_message`` con ``type='assistant'``.
Cada fila trae en su columna ``data`` (JSON) los tokens por mensaje::

    {"model": {"id": "...", "providerID": "..."},
     "agent": "build",
     "tokens": {"input": n, "output": n, "reasoning": n,
                "cache": {"read": n, "write": n}},
     "cost": 0.001,
     "time": {"created": <ms epoch>}}

Ventana de tiempo: ``since_ms`` en milisegundos epoch (hora local).
Todas las funciones son puras: reciben mensajes ya parseados o una
conexión, y devuelven dataclasses de ``data.models``.
"""

from __future__ import annotations

import json
import sqlite3
import time
from dataclasses import dataclass
from datetime import date, datetime, timedelta

from .models import AgentStat, DayTokens, HeatCell, ModelStat, TokenTotals


@dataclass(frozen=True)
class MsgUsage:
    ts_ms: int
    session_id: str
    model_id: str
    provider_id: str
    agent: str
    input: int
    output: int
    reasoning: int
    cache_read: int
    cache_write: int
    cost: float


def since_ms(days: int | None) -> int:
    """Inicio de la ventana: hace ``days`` días. ``None`` = desde siempre."""
    if days is None:
        return 0
    return int((time.time() - days * 86_400) * 1000)


def load_messages(con: sqlite3.Connection, start_ms: int = 0) -> list[MsgUsage]:
    """Lee los mensajes assistant con usage desde ``start_ms``."""
    rows = con.execute(
        "SELECT session_id, time_created, data FROM session_message "
        "WHERE type = 'assistant' AND time_created >= ? "
        "ORDER BY time_created",
        (start_ms,),
    )
    out: list[MsgUsage] = []
    for row in rows:
        msg = _parse_message(row["session_id"], row["time_created"], row["data"])
        if msg is not None:
            out.append(msg)
    return out


def _parse_message(session_id: str, ts_ms: int, data: str) -> MsgUsage | None:
    try:
        d = json.loads(data)
    except (json.JSONDecodeError, TypeError):
        return None
    tokens = d.get("tokens")
    if not isinstance(tokens, dict):
        return None
    cache = tokens.get("cache") or {}
    model = d.get("model") or {}
    return MsgUsage(
        ts_ms=int(ts_ms),
        session_id=session_id,
        model_id=str(model.get("id") or "unknown"),
        provider_id=str(model.get("providerID") or "unknown"),
        agent=str(d.get("agent") or "unknown"),
        input=int(tokens.get("input") or 0),
        output=int(tokens.get("output") or 0),
        reasoning=int(tokens.get("reasoning") or 0),
        cache_read=int(cache.get("read") or 0),
        cache_write=int(cache.get("write") or 0),
        cost=float(d.get("cost") or 0),
    )


def totals(msgs: list[MsgUsage]) -> TokenTotals:
    return TokenTotals(
        input=sum(m.input for m in msgs),
        output=sum(m.output for m in msgs),
        reasoning=sum(m.reasoning for m in msgs),
        cache_read=sum(m.cache_read for m in msgs),
        cache_write=sum(m.cache_write for m in msgs),
        cost=sum(m.cost for m in msgs),
        turns=len(msgs),
        sessions=len({m.session_id for m in msgs}),
    )


def tokens_by_day(msgs: list[MsgUsage]) -> list[DayTokens]:
    """Agrega por día local, incluye días vacíos entre medio."""
    if not msgs:
        return []
    buckets: dict[date, list[int]] = {}
    for m in msgs:
        day = datetime.fromtimestamp(m.ts_ms / 1000).date()
        b = buckets.setdefault(day, [0, 0])
        b[0] += m.input
        b[1] += m.output
    first, last = min(buckets), max(buckets)
    out: list[DayTokens] = []
    day = first
    while day <= last:
        b = buckets.get(day, [0, 0])
        out.append(DayTokens(day=day, input=b[0], output=b[1]))
        day += timedelta(days=1)
    return out


def heatmap(msgs: list[MsgUsage]) -> list[HeatCell]:
    """Tokens por (día de la semana, hora) en hora local. 0 = lunes."""
    grid: dict[tuple[int, int], int] = {}
    for m in msgs:
        dt = datetime.fromtimestamp(m.ts_ms / 1000)
        key = (dt.weekday(), dt.hour)
        grid[key] = grid.get(key, 0) + m.input + m.output
    return [
        HeatCell(weekday=wd, hour=h, tokens=tokens)
        for (wd, h), tokens in sorted(grid.items())
    ]


def by_model(msgs: list[MsgUsage]) -> list[ModelStat]:
    agg: dict[tuple[str, str], list[float]] = {}
    for m in msgs:
        key = (m.model_id, m.provider_id)
        a = agg.setdefault(key, [0, 0, 0, 0, 0.0, 0])
        a[0] += m.input
        a[1] += m.output
        a[2] += m.reasoning
        a[3] += m.cache_read
        a[4] += m.cost
        a[5] += 1
    stats = [
        ModelStat(
            model_id=k[0],
            provider_id=k[1],
            input=int(a[0]),
            output=int(a[1]),
            reasoning=int(a[2]),
            cache_read=int(a[3]),
            cost=float(a[4]),
            turns=int(a[5]),
        )
        for k, a in agg.items()
    ]
    stats.sort(key=lambda s: s.input + s.output, reverse=True)
    return stats


def by_agent(msgs: list[MsgUsage]) -> list[AgentStat]:
    agg: dict[str, list[float]] = {}
    for m in msgs:
        a = agg.setdefault(m.agent, [0, 0, 0.0, 0])
        a[0] += m.input
        a[1] += m.output
        a[2] += m.cost
        a[3] += 1
    stats = [
        AgentStat(agent=name, input=int(a[0]), output=int(a[1]),
                  cost=float(a[2]), turns=int(a[3]))
        for name, a in agg.items()
    ]
    stats.sort(key=lambda s: s.input + s.output, reverse=True)
    return stats
