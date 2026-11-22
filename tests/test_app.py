import sqlite3
from datetime import datetime

from conftest import SCHEMA, _msg

from opencode_usage.app import UsageApp
from opencode_usage.config import Settings
from opencode_usage.widgets.budget_bar import BudgetBar


def _db_file(tmp_path):
    path = tmp_path / "opencode.db"
    with sqlite3.connect(path) as w:
        w.execute(SCHEMA)
        w.execute(
            "INSERT INTO session_message VALUES (?, ?, ?, ?, ?, ?, ?)",
            _msg("m1", "s1", datetime.now(), inp=1000, out=200, cost=5.0),
        )
    return path


async def test_app_muestra_presupuesto_y_sesion(tmp_path):
    settings = Settings(
        db_path=_db_file(tmp_path),
        refresh_seconds=60,
        default_days=30,
        monthly_budget_usd=10.0,
    )
    app = UsageApp(settings)
    async with app.run_test() as pilot:
        await pilot.pause()
        bar = app.query_one("#budget", BudgetBar)
        assert "mes" in str(bar.render())
        assert "50%" in str(bar.render())


async def test_app_sin_presupuesto_muestra_aviso(tmp_path):
    settings = Settings(db_path=_db_file(tmp_path), refresh_seconds=60)
    app = UsageApp(settings)
    async with app.run_test() as pilot:
        await pilot.pause()
        bar = app.query_one("#budget", BudgetBar)
        assert "no definido" in str(bar.render())
