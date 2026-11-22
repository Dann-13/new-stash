"""Línea con la sesión más reciente de OpenCode."""

from __future__ import annotations

from datetime import datetime

from rich.text import Text
from textual.widgets import Static

from ..data.models import SessionStat
from ..format import format_cost, format_tokens
from ..i18n import t


def _ago(ts_ms: int, now: datetime) -> str:
    seconds = max(0, int(now.timestamp() - ts_ms / 1000))
    if seconds < 60:
        return t("ago_s", n=seconds)
    if seconds < 3600:
        return t("ago_min", n=seconds // 60)
    return t("ago_h", n=seconds // 3600)


class SessionLive(Static):
    """Resumen de la sesión que tuvo actividad por última vez."""

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.can_focus = False

    def set_session(self, stat: SessionStat | None) -> None:
        if stat is None:
            self.update(Text(t("session_none"), style="dim"))
            return
        text = Text(no_wrap=True)
        text.append(t("session_label"), style="dim")
        text.append(stat.session_id[:14], style="#58a6ff")
        text.append(
            t(
                "session_detail",
                input=format_tokens(stat.input),
                output=format_tokens(stat.output),
                cost=format_cost(stat.cost),
                turns=stat.turns,
                ago=_ago(stat.last_ts_ms, datetime.now()),
            ),
            style="#c9d1d9",
        )
        self.update(text)
