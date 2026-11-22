"""Heatmap: día de la semana × hora local."""

from __future__ import annotations

from rich.text import Text
from textual.widgets import Static

from ..data.models import HeatCell
from ..i18n import t

# rampa de intensidad: vacío -> azul tenue -> azul fuerte (hex: el parser
# de rich/textual no acepta "grey18" como color)
_RAMP = ["#161b22", "#30363d", "#484f58", "#1f6feb",
         "#388bfd", "#58a6ff", "#79c0ff"]


class Heatmap(Static):
    """Celdas 7×24 coloreadas por intensidad de tokens."""

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self._cells: dict[tuple[int, int], int] = {}
        self.can_focus = False

    def set_cells(self, cells: list[HeatCell]) -> None:
        self._cells = {(c.weekday, c.hour): c.tokens for c in cells}
        self.refresh()

    def render(self) -> Text:
        text = Text(no_wrap=True)
        if not self._cells:
            text.append(t("no_data"), style="dim")
            return text

        weekdays = t("weekdays").split(",")
        peak = max(self._cells.values()) or 1

        # cabecera de horas cada 3
        text.append("     ", style="dim")
        for h in range(24):
            if h % 6 == 0:
                text.append(f"{h:<6}", style="dim")
            else:
                text.append(" ")
        text.append("\n")

        for wd in range(7):
            text.append(f"{weekdays[wd]:>4} ", style="dim")
            for hour in range(24):
                tokens = self._cells.get((wd, hour), 0)
                if tokens == 0:
                    text.append("·", style=_RAMP[0])
                else:
                    ratio = tokens / peak
                    idx = min(int(ratio * (len(_RAMP) - 1)) + 1, len(_RAMP) - 1)
                    text.append("█", style=_RAMP[idx])
            text.append("\n")

        text.append("     ", style="dim")
        text.append(t("most_active"), style="dim")
        wd, hour, top = max(
            ((wd, h, t_) for (wd, h), t_ in self._cells.items()), key=lambda x: x[2]
        )
        text.append(f"{weekdays[wd]} {hour}h", style="bold")
        return text
