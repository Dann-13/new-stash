"""App Textual: dashboard de uso de tokens de OpenCode."""

from __future__ import annotations

import os
import sqlite3
import time
from datetime import datetime
from pathlib import Path

from textual import work
from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Button, Footer, Static

from . import export
from .config import Settings
from .data import db, queries
from .data.queries import MsgUsage
from .format import format_cost, format_percent, format_tokens
from .i18n import t
from .providers import deepseek
from .widgets.agents_table import AgentsTable
from .widgets.budget_bar import BudgetBar
from .widgets.export_screen import ExportScreen
from .widgets.heatmap import Heatmap
from .widgets.models_table import ModelsTable
from .widgets.provider_panel import ProviderPanel
from .widgets.session_live import SessionLive
from .widgets.sessions_table import SessionsTable
from .widgets.stat_card import StatCard
from .widgets.tokens_by_day import TokensByDay

_RANGES: dict[str, int | None] = {
    "7": 7,
    "30": 30,
    "90": 90,
    "all": None,
}

DEEPSEEK_POLL_SECONDS = 60


class UsageApp(App):
    """Dashboard en vivo."""

    CSS_PATH = "styles/app.tcss"
    TITLE = "opencode usage"

    def __init__(self, settings: Settings | None = None) -> None:
        super().__init__()
        self.settings = settings or Settings()
        self._days: int | None = self.settings.default_days
        self._msgs: list[MsgUsage] = []
        self._fingerprint: tuple | None = None
        self._last_full = 0.0
        self._export_dir: Path = self.settings.export_dir or Path.cwd()

    # ---- composición -------------------------------------------------
    def compose(self) -> ComposeResult:
        with Horizontal(id="range-bar"):
            yield Static("[b]opencode usage[/b]", id="title")
            for label in ("7", "30", "90", "all"):
                yield Button(label, id=f"range-{label}",
                             variant="primary" if label == str(self._days) or
                             (label == "all" and self._days is None)
                             else "default")
            yield Static("", id="updated")
        with Horizontal(id="cards"):
            yield StatCard(id="card-input")
            yield StatCard(id="card-output")
            yield StatCard(id="card-turns")
            yield StatCard(id="card-cost")
        with Vertical(id="status"):
            yield BudgetBar(id="budget")
            yield SessionLive(id="session")
            yield ProviderPanel(id="provider")
        with Horizontal(id="main"):
            with Vertical(id="left"):
                yield TokensByDay(id="tokens-by-day")
                yield Heatmap(id="heatmap")
            with Vertical(id="right"):
                yield ModelsTable(id="models")
                yield AgentsTable(id="agents")
                yield SessionsTable(id="sessions")
        yield Footer()

    # ---- ciclo de vida ------------------------------------------------
    def on_mount(self) -> None:
        self._bind_keys()
        if self.settings.config_error:
            self.notify(self.settings.config_error, severity="warning", timeout=10)
        self.refresh_data()
        self.set_interval(self.settings.refresh_seconds, self.refresh_data)
        self._setup_deepseek()

    def _bind_keys(self) -> None:
        """Enlaza teclas con descripciones traducidas para el Footer."""
        self.bind("q", "quit", description=t("quit"))
        self.bind("r", "refresh", description=t("refresh"))
        self.bind("e", "export", description=t("export"))
        self.bind("1", "set_range('7')", description=t("days_7"))
        self.bind("2", "set_range('30')", description=t("days_30"))
        self.bind("3", "set_range('90')", description=t("days_90"))
        self.bind("4", "set_range('all')", description=t("all"))

    def _setup_deepseek(self) -> None:
        """Muestra el panel solo si el usuario definió DEEPSEEK_API_KEY."""
        panel = self.query_one("#provider", ProviderPanel)
        if not os.environ.get("DEEPSEEK_API_KEY"):
            panel.display = False
            return
        panel.set_loading()
        self.poll_deepseek()
        self.set_interval(DEEPSEEK_POLL_SECONDS, self.poll_deepseek)

    @work(thread=True, exclusive=True, group="deepseek")
    def poll_deepseek(self) -> None:
        """Consulta el saldo en un hilo: la UI nunca espera la red."""
        key = os.environ.get("DEEPSEEK_API_KEY", "")
        try:
            balance = deepseek.fetch_balance(key)
        except deepseek.DeepSeekError as exc:
            self.call_from_thread(self._show_deepseek_error, str(exc))
            return
        self.call_from_thread(self._show_deepseek_balance, balance)

    def _show_deepseek_balance(self, balance: deepseek.DeepSeekBalance) -> None:
        self.query_one("#provider", ProviderPanel).set_balance(balance)

    def _show_deepseek_error(self, message: str) -> None:
        self.query_one("#provider", ProviderPanel).set_error(message)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id and event.button.id.startswith("range-"):
            self.action_set_range(event.button.id.removeprefix("range-"))

    # ---- acciones -----------------------------------------------------
    def action_set_range(self, label: str) -> None:
        if label not in _RANGES:
            return
        self._days = _RANGES[label]
        for btn in self.query(Button):
            if btn.id and btn.id.startswith("range-"):
                btn.variant = "primary" if btn.id == f"range-{label}" else "default"
        self.refresh_data(force=True)

    def action_refresh(self) -> None:
        self.refresh_data(force=True)

    def action_export(self) -> None:
        """Abre el diálogo para elegir la carpeta destino del export."""
        self.push_screen(ExportScreen(str(self._export_dir)), self._export_to)

    def _export_to(self, chosen: str | None) -> None:
        """Exporta CSV y Markdown a la carpeta elegida (None = cancelado)."""
        if not chosen:
            return
        folder = Path(os.path.expandvars(chosen)).expanduser()
        try:
            folder.mkdir(parents=True, exist_ok=True)
        except OSError as exc:
            self.notify(t("export_bad_dir", exc=exc), severity="error")
            return
        self._export_dir = folder
        stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        label = t("range_all") if self._days is None else t("range_days", n=self._days)
        csv_path = folder / f"opencode-usage-{stamp}.csv"
        md_path = folder / f"opencode-usage-{stamp}.md"
        try:
            export.export_csv(csv_path, queries.tokens_by_day(self._msgs))
            export.export_markdown(
                md_path,
                label,
                queries.totals(self._msgs),
                queries.by_model(self._msgs),
                queries.by_agent(self._msgs),
            )
        except OSError as exc:
            self.notify(t("export_fail", exc=exc), severity="error")
            return
        self.notify(t("export_ok", csv=csv_path.name, md=md_path.name))

    # ---- datos --------------------------------------------------------
    def _db_fingerprint(self) -> tuple:
        """Mtime y tamaño de la DB y su -wal. Cambian solo al escribir OpenCode."""
        db_path = Path(self.settings.db_path)
        parts = []
        for p in (db_path, Path(f"{db_path}-wal")):
            try:
                st = p.stat()
                parts.append((st.st_mtime_ns, st.st_size))
            except OSError:
                parts.append(None)
        return tuple(parts)

    def refresh_data(self, force: bool = False) -> None:
        fp = self._db_fingerprint()
        now = time.monotonic()
        # Sin cambios en la DB no se relee. Cada 60 s se relee igual,
        # para que la ventana de días avance.
        if not force and fp == self._fingerprint and now - self._last_full < 60:
            return
        self._fingerprint = fp
        self._last_full = now
        start = queries.since_ms(self._days)
        budget = self.settings.monthly_budget_usd
        try:
            con = db.open_readonly(self.settings.db_path)
        except (FileNotFoundError, sqlite3.Error) as exc:
            self.query_one("#updated", Static).update(
                f"[red]{t('db_error', exc=exc)}[/red]"
            )
            return
        with con:
            self._msgs = queries.load_messages(con, start)
            month_msgs = (
                queries.load_messages(con, queries.month_start_ms())
                if budget is not None else []
            )

        t_ = queries.totals(self._msgs)
        cards = {
            "#card-input": (
                t("card_input"),
                format_tokens(t_.input),
                t("from_cache", pct=format_percent(t_.cache_hit_ratio)),
            ),
            "#card-output": (
                t("card_output"),
                format_tokens(t_.output),
                t("per_turn", n=format_tokens(t_.turns and t_.output // t_.turns or 0)),
            ),
            "#card-turns": (
                t("card_turns"),
                str(t_.turns),
                t("sessions", n=t_.sessions),
            ),
            "#card-cost": (
                t("card_cost"),
                format_cost(t_.cost),
                t("recorded"),
            ),
        }
        for selector, (label, value, sub) in cards.items():
            self.query_one(selector, StatCard).set_stat(label, value, sub)

        self.query_one("#tokens-by-day", TokensByDay).set_days(
            queries.tokens_by_day(self._msgs)
        )
        self.query_one("#heatmap", Heatmap).set_cells(
            queries.heatmap(self._msgs)
        )
        self.query_one("#models", ModelsTable).set_stats(
            queries.by_model(self._msgs)
        )
        self.query_one("#agents", AgentsTable).set_stats(
            queries.by_agent(self._msgs)
        )
        self.query_one("#sessions", SessionsTable).set_stats(
            queries.top_sessions(self._msgs)
        )
        self.query_one("#budget", BudgetBar).set_budget(
            queries.totals(month_msgs).cost, budget
        )
        self.query_one("#session", SessionLive).set_session(
            queries.current_session(self._msgs)
        )
        self.query_one("#updated", Static).update(
            f"[dim]{t('updated', time=datetime.now().strftime('%H:%M:%S'))}[/dim]"
        )
