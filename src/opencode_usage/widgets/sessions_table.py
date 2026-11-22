"""Tabla de sesiones: las que más gastan primero."""

from __future__ import annotations

from textual.widgets import DataTable

from ..data.models import SessionStat
from ..format import format_cost, format_tokens
from ..i18n import t


class SessionsTable(DataTable[str]):
    """Ranking de sesiones por costo, con tokens y turnos."""

    def on_mount(self) -> None:
        self.cursor_type = "row"
        self.zebra_stripes = True
        self.add_columns(
            t("col_session"), t("col_input"), t("col_output"),
            t("col_turns"), t("col_cost"),
        )

    def set_stats(self, stats: list[SessionStat]) -> None:
        self.clear()
        for s in stats:
            self.add_row(
                s.session_id[:14],
                format_tokens(s.input),
                format_tokens(s.output),
                str(s.turns),
                format_cost(s.cost),
                key=s.session_id,
            )
