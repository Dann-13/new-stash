"""Panel de proveedor externo: saldo de DeepSeek (solo si hay clave)."""

from __future__ import annotations

from rich.text import Text
from textual.widgets import Static

from ..providers.deepseek import DeepSeekBalance

_OK = "#3fb950"
_BAD = "#f85149"


class ProviderPanel(Static):
    """Una línea con el saldo. Oculto cuando no hay DEEPSEEK_API_KEY."""

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.can_focus = False

    def set_balance(self, balance: DeepSeekBalance) -> None:
        text = Text(no_wrap=True)
        text.append("deepseek ", style="dim")
        text.append(
            f"saldo {balance.total:.2f} {balance.currency}",
            style=_OK if balance.is_available else _BAD,
        )
        text.append(
            "  · disponible" if balance.is_available else "  · sin saldo para llamadas",
            style=_OK if balance.is_available else _BAD,
        )
        self.update(text)

    def set_error(self, message: str) -> None:
        text = Text(no_wrap=True)
        text.append("deepseek ", style="dim")
        text.append(message, style=_BAD)
        self.update(text)

    def set_loading(self) -> None:
        self.update(Text("deepseek  consultando saldo…", style="dim"))
