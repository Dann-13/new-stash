"""Precios de modelos en USD por 1M tokens.

Solo se usa como respaldo cuando la base de datos no trae `cost`.
La tabla es aproximada y fácil de editar.
"""

from __future__ import annotations

# model_id -> (precio input por 1M, precio output por 1M)
PRICES_USD_PER_MTOK: dict[str, tuple[float, float]] = {
    "deepseek-chat": (0.27, 1.10),
    "deepseek-reasoner": (0.55, 2.19),
    "claude-opus-4-1": (15.0, 75.0),
    "claude-sonnet-4": (3.0, 15.0),
    "claude-haiku-4": (0.80, 4.00),
    "gpt-5": (1.25, 10.0),
    "gpt-5-mini": (0.25, 2.00),
    "gemini-2.5-pro": (1.25, 10.0),
    "gemini-2.5-flash": (0.30, 2.50),
}


def estimate(model_id: str, input_tokens: int, output_tokens: int) -> float | None:
    """Costo estimado en USD, o None si el modelo no está en la tabla."""
    price = PRICES_USD_PER_MTOK.get(model_id)
    if price is None:
        return None
    return (input_tokens * price[0] + output_tokens * price[1]) / 1_000_000
