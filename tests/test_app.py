import sqlite3
from datetime import datetime

from conftest import SCHEMA, _msg
from textual.widgets import Input

from opencode_usage.app import UsageApp
from opencode_usage.config import Settings
from opencode_usage.i18n import set_language
from opencode_usage.widgets.budget_bar import BudgetBar
from opencode_usage.widgets.export_screen import ExportScreen
from opencode_usage.widgets.sessions_table import SessionsTable


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


async def test_app_ingles_traduce_footer_y_presupuesto(tmp_path):
    set_language("en")
    settings = Settings(
        db_path=_db_file(tmp_path),
        refresh_seconds=60,
        monthly_budget_usd=10.0,
    )
    app = UsageApp(settings)
    async with app.run_test() as pilot:
        await pilot.pause()
        bar = app.query_one("#budget", BudgetBar)
        assert "month" in str(bar.render())
        footer = {k: ab.binding.description for k, ab in app.active_bindings.items()}
        assert footer["q"] == "Quit"
        assert footer["1"] == "7 days"


async def test_app_muestra_tabla_sesiones(tmp_path):
    settings = Settings(db_path=_db_file(tmp_path), refresh_seconds=60)
    app = UsageApp(settings)
    async with app.run_test() as pilot:
        await pilot.pause()
        table = app.query_one("#sessions", SessionsTable)
        assert table.row_count == 1


async def test_export_dialogo_elige_carpeta(tmp_path):
    settings = Settings(db_path=_db_file(tmp_path), refresh_seconds=60)
    app = UsageApp(settings)
    dest = tmp_path / "salida"
    async with app.run_test() as pilot:
        await pilot.pause()
        await pilot.press("e")
        await pilot.pause()
        assert isinstance(app.screen, ExportScreen)
        app.screen.query_one("#export-input", Input).value = str(dest)
        await pilot.press("enter")
        await pilot.pause()
        assert not isinstance(app.screen, ExportScreen)
        assert list(dest.glob("opencode-usage-*.csv"))
        assert list(dest.glob("opencode-usage-*.md"))


async def test_export_dialogo_cancelar_no_exporta(tmp_path):
    settings = Settings(db_path=_db_file(tmp_path), refresh_seconds=60)
    app = UsageApp(settings)
    async with app.run_test() as pilot:
        await pilot.pause()
        await pilot.press("e")
        await pilot.pause()
        assert isinstance(app.screen, ExportScreen)
        await pilot.press("escape")
        await pilot.pause()
        assert not isinstance(app.screen, ExportScreen)
        assert not list(tmp_path.glob("opencode-usage-*.csv"))
