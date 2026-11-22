"""Pruebas de las agregaciones de uso."""

from __future__ import annotations

import sqlite3

from opencode_usage.data import queries


def test_load_messages_fills_usage(con: sqlite3.Connection) -> None:
    msgs = queries.load_messages(con)
    assert len(msgs) == 3  # sin tokens ni user
    m = msgs[0]
    assert m.model_id == "model-a"
    assert m.provider_id == "prov"
    assert m.agent == "build"
    assert m.input == 1000
    assert m.output == 200
    assert m.cache_read == 8000
    assert m.cost == 0.01


def test_load_messages_respects_start(con: sqlite3.Connection) -> None:
    # corte a media ventana: solo el mensaje del día 2
    start = int(queries.since_ms(None))  # desde siempre no filtra
    assert start == 0
    msgs = queries.load_messages(con, start_ms=0)
    assert len(msgs) == 3
    # corte futuro: nada
    msgs = queries.load_messages(con, start_ms=4_000_000_000_000)
    assert msgs == []


def test_totals(con: sqlite3.Connection) -> None:
    t = queries.totals(queries.load_messages(con))
    assert t.input == 1800
    assert t.output == 700
    assert t.reasoning == 70
    assert t.cache_read == 13_000
    assert abs(t.cost - 0.06) < 1e-9
    assert t.turns == 3
    assert t.sessions == 2
    # cache hit = cache_read / (input + cache_read)
    assert abs(t.cache_hit_ratio - 13_000 / 14_800) < 1e-9


def test_tokens_by_day(con: sqlite3.Connection) -> None:
    days = queries.tokens_by_day(queries.load_messages(con))
    assert len(days) == 2
    assert days[0].day.isoformat() == "2026-11-18"
    assert (days[0].input, days[0].output) == (1500, 300)
    assert days[1].day.isoformat() == "2026-11-19"
    assert (days[1].input, days[1].output) == (300, 400)


def test_tokens_by_day_fills_gaps(con: sqlite3.Connection) -> None:
    # agrega un mensaje 3 días después para forzar huecos
    from datetime import datetime

    from conftest import _msg

    con.execute(
        "INSERT INTO session_message VALUES (?, ?, ?, ?, ?, ?, ?)",
        _msg("m6", "s3", datetime(2026, 11, 22, 8, 0),
             inp=10, out=10),
    )
    days = queries.tokens_by_day(queries.load_messages(con))
    assert len(days) == 5  # 18,19,20,21,22
    assert (days[2].input, days[2].output) == (0, 0)


def test_heatmap(con: sqlite3.Connection) -> None:
    cells = queries.heatmap(queries.load_messages(con))
    grid = {(c.weekday, c.hour): c.tokens for c in cells}
    # 2026-11-18 es miércoles -> weekday 2, 10:00
    assert grid[(2, 10)] == 1200  # in 1000 + out 200
    # 2026-11-19 jueves 20:00
    assert grid[(3, 20)] == 700


def test_by_model(con: sqlite3.Connection) -> None:
    stats = queries.by_model(queries.load_messages(con))
    assert len(stats) == 2
    a, b = stats  # ordenado por uso total: a (1700+300) primero
    assert a.model_id == "model-a"
    assert a.turns == 2
    assert a.input == 1500
    assert b.model_id == "model-b"
    assert b.provider_id == "prov2"
    assert b.turns == 1
    assert abs(b.cost - 0.03) < 1e-9


def test_by_agent(con: sqlite3.Connection) -> None:
    stats = queries.by_agent(queries.load_messages(con))
    assert [s.agent for s in stats] == ["build", "plan"]
    assert stats[0].turns == 2
    assert stats[0].input == 1500
    assert stats[1].output == 400


def test_empty_db() -> None:
    con = sqlite3.connect(":memory:")
    con.row_factory = sqlite3.Row
    con.execute(
        "CREATE TABLE session_message ("
        " id TEXT, session_id TEXT, type TEXT, seq INTEGER,"
        " time_created INTEGER, time_updated INTEGER, data TEXT)"
    )
    msgs = queries.load_messages(con)
    assert msgs == []
    assert queries.totals(msgs).turns == 0
    assert queries.tokens_by_day(msgs) == []
    assert queries.heatmap(msgs) == []
    assert queries.by_model(msgs) == []
    assert queries.by_agent(msgs) == []
