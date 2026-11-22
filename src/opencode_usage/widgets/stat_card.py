"""Tarjeta de estadística grande (INPUT, OUTPUT, TURNS, COST)."""

from __future__ import annotations

from textual.widgets import Static


class StatCard(Static):
    """Muestra label + valor grande + subtexto."""

    def set_stat(self, label: str, value: str, sub: str = "") -> None:
        sub_line = f"\n[dim]{sub}[/dim]" if sub else ""
        self.update(f"[dim]{label}[/dim]\n[b]{value}[/b]{sub_line}")
