"""Barra de presupuesto mensual: gasto del mes frente al límite."""

from __future__ import annotations

from rich.text import Text
from textual.widgets import Static

from ..format import format_cost
from ..i18n import t

BAR_WIDTH = 24
_OK = "#3fb950"
_WARN = "#d29922"
_OVER = "#f85149"


class BudgetBar(Static):
    """Muestra gasto del mes. Solo informa, nunca bloquea nada."""

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.can_focus = False

    def set_budget(self, spent: float, budget: float | None) -> None:
        if budget is None:
            self.update(Text(t("budget_none"), style="dim"))
            return
        ratio = spent / budget
        style = _OK if ratio < 0.8 else _WARN if ratio < 1 else _OVER
        filled = min(BAR_WIDTH, round(min(ratio, 1) * BAR_WIDTH))
        text = Text(no_wrap=True)
        text.append(t("budget_month"), style="dim")
        text.append(f"{format_cost(spent)} / {format_cost(budget)} ", style=style)
        text.append("█" * filled, style=style)
        text.append("░" * (BAR_WIDTH - filled), style="#30363d")
        text.append(f" {ratio * 100:.0f}%", style=style)
        if ratio >= 1:
            text.append(t("budget_over"), style=_OVER)
        elif ratio >= 0.8:
            text.append(t("budget_near"), style=_WARN)
        self.update(text)
