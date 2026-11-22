"""Saldo de DeepSeek: GET /user/balance (API oficial, solo lectura).

Seguridad:
- La clave llega como argumento desde la variable de entorno DEEPSEEK_API_KEY.
  Este módulo nunca la guarda, nunca la escribe y nunca la incluye en errores.
- Solo se habla con ``https://api.deepseek.com``. Sin otros destinos.
- Errores de red o HTTP producen mensajes genéricos, sin datos de la petición.
"""

from __future__ import annotations

import json
import urllib.error
import urllib.request
from dataclasses import dataclass

from ..i18n import t

BALANCE_URL = "https://api.deepseek.com/user/balance"
TIMEOUT_SECONDS = 10


class DeepSeekError(Exception):
    """Fallo al consultar el saldo. El mensaje nunca contiene la clave."""


@dataclass(frozen=True)
class DeepSeekBalance:
    is_available: bool
    currency: str
    total: float
    granted: float
    topped_up: float


def fetch_balance(api_key: str) -> DeepSeekBalance:
    """Consulta el saldo. Lanza DeepSeekError con mensaje seguro si falla."""
    if not api_key:
        raise DeepSeekError(t("ds_no_key"))
    if not BALANCE_URL.startswith("https://"):
        raise DeepSeekError(t("ds_https"))
    req = urllib.request.Request(
        BALANCE_URL,
        headers={"Authorization": f"Bearer {api_key}", "Accept": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT_SECONDS) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        if exc.code in (401, 403):
            raise DeepSeekError(t("ds_rejected")) from None
        raise DeepSeekError(t("ds_http", code=exc.code)) from None
    except (urllib.error.URLError, TimeoutError, OSError):
        raise DeepSeekError(t("ds_network")) from None
    except (json.JSONDecodeError, UnicodeDecodeError):
        raise DeepSeekError(t("ds_json")) from None
    return _parse_balance(payload)


def _parse_balance(payload: dict) -> DeepSeekBalance:
    infos = payload.get("balance_infos") or []
    if not isinstance(infos, list) or not infos:
        raise DeepSeekError(t("ds_no_balance"))
    info = infos[0]
    try:
        return DeepSeekBalance(
            is_available=bool(payload.get("is_available")),
            currency=str(info.get("currency") or "?"),
            total=float(info.get("total_balance") or 0),
            granted=float(info.get("granted_balance") or 0),
            topped_up=float(info.get("topped_up_balance") or 0),
        )
    except (TypeError, ValueError):
        raise DeepSeekError(t("ds_bad_format")) from None
