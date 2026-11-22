"""Diálogo modal para elegir la carpeta destino del export."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Vertical
from textual.screen import ModalScreen
from textual.widgets import Input, Label

from ..i18n import t


class ExportScreen(ModalScreen[str | None]):
    """Pide una carpeta. Devuelve la ruta elegida, o None si se cancela."""

    BINDINGS = [Binding("escape", "cancel", show=False)]

    def __init__(self, current: str) -> None:
        super().__init__()
        self._current = current

    def compose(self) -> ComposeResult:
        with Vertical(id="export-dialog"):
            yield Label(t("export_title"), id="export-title")
            yield Input(value=self._current, id="export-input")
            yield Label(t("export_hint"), id="export-hint")

    def on_mount(self) -> None:
        self.query_one("#export-input", Input).focus()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        self.dismiss(event.value.strip())

    def action_cancel(self) -> None:
        self.dismiss(None)
