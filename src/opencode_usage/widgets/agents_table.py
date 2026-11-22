"""Tabla de agentes: input/output/turns/costo por agente."""

from __future__ import annotations

from textual.widgets import DataTable

from ..data.models import AgentStat
from ..format import format_cost, format_tokens
from ..i18n import t


class AgentsTable(DataTable[str]):
    """Lista de agentes ordenados por uso total."""

    def on_mount(self) -> None:
        self.cursor_type = "row"
        self.zebra_stripes = True
        self.add_columns(
            t("col_agent"), t("col_input"), t("col_output"),
            t("col_turns"), t("col_cost"),
        )

    def set_stats(self, stats: list[AgentStat]) -> None:
        self.clear()
        for s in stats:
            self.add_row(
                s.agent,
                format_tokens(s.input),
                format_tokens(s.output),
                str(s.turns),
                format_cost(s.cost),
                key=s.agent,
            )
