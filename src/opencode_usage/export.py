"""Exporta el uso mostrado a CSV (por día) y Markdown (resumen).

Funciones puras de escritura: reciben datos ya calculados, no tocan la UI.
"""

from __future__ import annotations

import csv
from pathlib import Path

from .data.models import AgentStat, DayTokens, ModelStat, TokenTotals
from .format import format_cost, format_percent
from .i18n import t


def export_csv(path: Path, days: list[DayTokens]) -> None:
    """Una fila por día: fecha, input, output, costo en USD."""
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["date", "input_tokens", "output_tokens", "cost_usd"])
        for d in days:
            writer.writerow([d.day.isoformat(), d.input, d.output, f"{d.cost:.6f}"])


def _cell(text: str) -> str:
    return text.replace("|", "\\|")


def export_markdown(
    path: Path,
    label: str,
    totals: TokenTotals,
    models: list[ModelStat],
    agents: list[AgentStat],
) -> None:
    """Resumen legible: totales, modelos y agentes del rango."""
    lines = [
        "# opencode usage",
        "",
        t("md_range", label=label),
        "",
        t("md_totals"),
        "",
        t("md_input", n=totals.input),
        t("md_output", n=totals.output),
        t("md_cache", pct=format_percent(totals.cache_hit_ratio)),
        t("md_turns", n=totals.turns),
        t("md_sessions", n=totals.sessions),
        t("md_cost", c=format_cost(totals.cost)),
        "",
        t("md_models"),
        "",
        t("md_models_header"),
        "|---|---|---:|---:|---:|---:|",
    ]
    for m in models:
        lines.append(
            f"| {_cell(m.model_id)} | {_cell(m.provider_id)} | {m.input} | "
            f"{m.output} | {m.turns} | {format_cost(m.cost)} |"
        )
    lines += [
        "",
        t("md_agents"),
        "",
        t("md_agents_header"),
        "|---|---:|---:|---:|---:|",
    ]
    for a in agents:
        lines.append(
            f"| {_cell(a.agent)} | {a.input} | {a.output} | {a.turns} | "
            f"{format_cost(a.cost)} |"
        )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
