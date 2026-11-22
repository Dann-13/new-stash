"""Línea con la sesión más reciente de OpenCode."""

from __future__ import annotations

from datetime import datetime

from rich.text import Text
from textual.widgets import Static

from ..data.models import SessionStat
from ..format import format_cost, format_tokens


def _ago(ts_ms: int, now: datetime) -> str:
    seconds = max(0, int(now.timestamp() - ts_ms / 1000))
    if seconds < 60:
        return f"hace {seconds} s"
    if seconds < 3600:
        return f"hace {seconds // 60} min"
    return f"hace {seconds // 3600} h"


class SessionLive(Static):
    """Resumen de la sesión que tuvo actividad por última vez."""

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.can_focus = False

    def set_session(self, stat: SessionStat | None) -> None:
        if stat is None:
            self.update(Text("sesión actual: sin actividad", style="dim"))
            return
        text = Text(no_wrap=True)
        text.append("sesión actual ", style="dim")
        text.append(stat.session_id[:14], style="#58a6ff")
        text.append(
            f"  in {format_tokens(stat.input)} · out {format_tokens(stat.output)}"
            f" · {format_cost(stat.cost)} · {stat.turns} turnos"
            f" · {_ago(stat.last_ts_ms, datetime.now())}",
            style="#c9d1d9",
        )
        self.update(text)
