"""Tabla de agentes: input/output/turns/costo por agente."""

from __future__ import annotations

from textual.widgets import DataTable

from ..data.models import AgentStat
from ..format import format_cost, format_tokens


class AgentsTable(DataTable[str]):
    """Lista de agentes ordenados por uso total."""

    def on_mount(self) -> None:
        self.cursor_type = "row"
        self.zebra_stripes = True
        self.add_columns("AGENT", "INPUT", "OUTPUT", "TURNS", "COST")

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
