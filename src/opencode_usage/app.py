"""App Textual: dashboard de uso de tokens de OpenCode."""

from __future__ import annotations

import sqlite3
from datetime import datetime

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.widgets import Button, Footer, Static

from .config import Settings
from .data import db, queries
from .data.queries import MsgUsage
from .format import format_cost, format_percent, format_tokens
from .widgets.agents_table import AgentsTable
from .widgets.heatmap import Heatmap
from .widgets.models_table import ModelsTable
from .widgets.stat_card import StatCard
from .widgets.tokens_by_day import TokensByDay

_RANGES: dict[str, int | None] = {
    "7": 7,
    "30": 30,
    "90": 90,
    "all": None,
}


class UsageApp(App):
    """Dashboard en vivo."""

    CSS_PATH = "styles/app.tcss"
    TITLE = "opencode usage"

    BINDINGS = [
        Binding("q", "quit", "Salir"),
        Binding("r", "refresh", "Refrescar"),
        Binding("1", "set_range('7')", "7 días"),
        Binding("2", "set_range('30')", "30 días"),
        Binding("3", "set_range('90')", "90 días"),
        Binding("4", "set_range('all')", "Todo"),
    ]

    def __init__(self, settings: Settings | None = None) -> None:
        super().__init__()
        self.settings = settings or Settings()
        self._days: int | None = self.settings.default_days
        self._msgs: list[MsgUsage] = []

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
        with Horizontal(id="main"):
            with Vertical(id="left"):
                yield TokensByDay(id="tokens-by-day")
                yield Heatmap(id="heatmap")
            with Vertical(id="right"):
                yield ModelsTable(id="models")
                yield AgentsTable(id="agents")
        yield Footer()

    # ---- ciclo de vida ------------------------------------------------
    def on_mount(self) -> None:
        self.refresh_data()
        self.set_interval(self.settings.refresh_seconds, self.refresh_data)

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
        self.refresh_data()

    def action_refresh(self) -> None:
        self.refresh_data()

    # ---- datos --------------------------------------------------------
    def refresh_data(self) -> None:
        start = queries.since_ms(self._days)
        try:
            con = db.open_readonly(self.settings.db_path)
        except (FileNotFoundError, sqlite3.Error) as exc:
            self.query_one("#updated", Static).update(
                f"[red]error: {exc}[/red]"
            )
            return
        with con:
            self._msgs = queries.load_messages(con, start)

        t = queries.totals(self._msgs)
        cards = {
            "#card-input": (
                "INPUT TOKENS",
                format_tokens(t.input),
                f"{format_percent(t.cache_hit_ratio)} from cache",
            ),
            "#card-output": (
                "OUTPUT TOKENS",
                format_tokens(t.output),
                f"{format_tokens(t.turns and t.output // t.turns or 0)} per turn",
            ),
            "#card-turns": (
                "TURNS",
                str(t.turns),
                f"{t.sessions} sessions",
            ),
            "#card-cost": (
                "COST",
                format_cost(t.cost),
                "recorded by OpenCode",
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
        self.query_one("#updated", Static).update(
            f"[dim]actualizado {datetime.now().strftime('%H:%M:%S')}[/dim]"
        )
