import sqlite3
from datetime import datetime
from unittest.mock import patch

from conftest import SCHEMA, _msg

from opencode_usage.app import UsageApp
from opencode_usage.config import Settings
from opencode_usage.providers import deepseek
from opencode_usage.widgets.provider_panel import ProviderPanel


def _db_file(tmp_path):
    path = tmp_path / "opencode.db"
    with sqlite3.connect(path) as w:
        w.execute(SCHEMA)
        w.execute(
            "INSERT INTO session_message VALUES (?, ?, ?, ?, ?, ?, ?)",
            _msg("m1", "s1", datetime.now(), inp=1000, out=200, cost=1.0),
        )
    return path


async def test_panel_oculto_sin_clave(tmp_path, monkeypatch):
    monkeypatch.delenv("DEEPSEEK_API_KEY", raising=False)
    app = UsageApp(Settings(db_path=_db_file(tmp_path), refresh_seconds=60))
    async with app.run_test() as pilot:
        await pilot.pause()
        assert app.query_one("#provider", ProviderPanel).display is False


async def test_panel_muestra_saldo_con_clave(tmp_path, monkeypatch):
    monkeypatch.setenv("DEEPSEEK_API_KEY", "sk-test")
    balance = deepseek.DeepSeekBalance(True, "USD", 9.0, 1.0, 8.0)
    with patch.object(deepseek, "fetch_balance", return_value=balance):
        app = UsageApp(Settings(db_path=_db_file(tmp_path), refresh_seconds=60))
        async with app.run_test() as pilot:
            await app.workers.wait_for_complete()
            await pilot.pause()
            panel = app.query_one("#provider", ProviderPanel)
            assert panel.display is True
            assert "9.00 USD" in str(panel.render())


async def test_panel_muestra_error_seguro(tmp_path, monkeypatch):
    monkeypatch.setenv("DEEPSEEK_API_KEY", "sk-test")
    with patch.object(
        deepseek,
        "fetch_balance",
        side_effect=deepseek.DeepSeekError("sin conexión con DeepSeek"),
    ):
        app = UsageApp(Settings(db_path=_db_file(tmp_path), refresh_seconds=60))
        async with app.run_test() as pilot:
            await app.workers.wait_for_complete()
            await pilot.pause()
            panel = app.query_one("#provider", ProviderPanel)
            assert "sin conexión" in str(panel.render())
            assert "sk-test" not in str(panel.render())
