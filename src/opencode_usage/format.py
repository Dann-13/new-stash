"""Formato de números para la UI."""

from __future__ import annotations


def format_tokens(n: int) -> str:
    """1234567 -> '1.2M'."""
    if n >= 1_000_000_000:
        return f"{n / 1_000_000_000:.1f}B"
    if n >= 1_000_000:
        return f"{n / 1_000_000:.1f}M"
    if n >= 1_000:
        return f"{n / 1_000:.1f}K"
    return str(n)


def format_cost(v: float) -> str:
    """0.00054 -> '$0.0005'."""
    if v <= 0:
        return "$0"
    if v < 0.01:
        return f"${v:.4f}"
    return f"${v:.2f}"


def format_percent(ratio: float) -> str:
    """0.983 -> '98.3%'."""
    return f"{ratio * 100:.1f}%"
