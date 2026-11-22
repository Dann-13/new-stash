"""Tabla de modelos: input/output/turns/costo por modelo."""

from __future__ import annotations

from textual.widgets import DataTable

from ..data.models import ModelStat
from ..format import format_cost, format_tokens


class ModelsTable(DataTable[str]):
    """Lista de modelos ordenados por uso total."""

    def on_mount(self) -> None:
        self.cursor_type = "row"
        self.zebra_stripes = True
        self.add_columns("MODEL", "PROVIDER", "INPUT", "OUTPUT", "TURNS", "COST")

    def set_stats(self, stats: list[ModelStat]) -> None:
        self.clear()
        for s in stats:
            self.add_row(
                s.model_id,
                s.provider_id,
                format_tokens(s.input),
                format_tokens(s.output),
                str(s.turns),
                format_cost(s.cost),
                key=s.model_id,
            )
