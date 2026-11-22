"""Gráfica de barras apiladas: tokens por día (input gris, output azul)."""

from __future__ import annotations

from rich.text import Text
from textual.widgets import Static

from ..data.models import DayTokens
from ..format import format_percent, format_tokens
from ..i18n import t

HEIGHT = 8  # filas de la gráfica

_INPUT_STYLE = "#8b949e"
_OUTPUT_STYLE = "#58a6ff"
_COST_STYLE = "#d2a8ff"
_CACHE_STYLE = "#3fb950"
_SPARK = "▁▂▃▄▅▆▇█"


def _cost_line(days: list[DayTokens]) -> str:
    """Una celda por día: altura proporcional al costo de ese día."""
    peak = max(d.cost for d in days)
    if peak <= 0:
        return "·" * len(days)
    levels = len(_SPARK) - 1
    return "".join(
        _SPARK[round(d.cost / peak * levels)] if d.cost > 0 else "·"
        for d in days
    )


def _cache_line(days: list[DayTokens]) -> str:
    """Una celda por día: altura proporcional al % de caché de ese día."""
    levels = len(_SPARK) - 1
    return "".join(
        _SPARK[round(d.cache_hit_ratio * levels)]
        if (d.input + d.cache_read) > 0 else "·"
        for d in days
    )


def _cache_ratio(days: list[DayTokens]) -> float:
    """% de caché ponderado del rango mostrado."""
    read = sum(d.cache_read for d in days)
    denom = sum(d.input + d.cache_read for d in days)
    return read / denom if denom else 0.0


class TokensByDay(Static):
    """Barras verticales por día: output abajo (azul), input arriba (gris)."""

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self._days: list[DayTokens] = []
        self.can_focus = False

    def set_days(self, days: list[DayTokens]) -> None:
        self._days = days
        self.refresh()

    def render(self) -> Text:
        text = Text(no_wrap=True)
        if not self._days:
            text.append(t("no_data"), style="dim")
            return text

        # una columna por día; si no cabe, muestra los últimos que quepan
        width = max(self.size.width or 60, 10)
        days = self._days[-width:]
        peak = max((d.input + d.output) for d in days) or 1

        # eje: valores de referencia arriba
        text.append(f"{format_tokens(peak):>8} ", style="dim")
        text.append("\n")

        for row in range(HEIGHT, 0, -1):
            line = Text()
            for d in days:
                total = d.input + d.output
                # altura total de la barra en celdas (escala lineal)
                filled = round(total / peak * HEIGHT)
                out_filled = round(d.output / peak * HEIGHT)
                if filled >= row:
                    if out_filled >= row:
                        line.append("█", style=_OUTPUT_STYLE)
                    else:
                        line.append("█", style=_INPUT_STYLE)
                elif filled == row - 1 and (total / peak * HEIGHT) % 1 > 0.35:
                    # media celda: medio bloque
                    if out_filled >= row - 1:
                        line.append("▄", style=_OUTPUT_STYLE)
                    else:
                        line.append("▄", style=_INPUT_STYLE)
                else:
                    line.append(" ")
            text.append_text(line)
            text.append("\n")

        text.append(" " * 8, style="dim")
        text.append("▔" * len(days), style="#30363d")
        text.append("\n")
        text.append(f"{days[0].day.strftime('%m-%d'):>8} ", style="dim")
        text.append(f"{days[-1].day.strftime('%m-%d')}", style="dim")
        text.append("\n")
        text.append(" " * 8, style="dim")
        text.append(_cost_line(days), style=_COST_STYLE)
        text.append("\n")
        text.append(" " * 8, style="dim")
        text.append(_cache_line(days), style=_CACHE_STYLE)
        text.append("\n")
        text.append("  ", style="dim")
        text.append(t("legend_output"), style=_OUTPUT_STYLE)
        text.append(t("legend_input"), style=_INPUT_STYLE)
        text.append(t("legend_cost"), style=_COST_STYLE)
        text.append(
            t("legend_cache", pct=format_percent(_cache_ratio(days))),
            style=_CACHE_STYLE,
        )
        return text
