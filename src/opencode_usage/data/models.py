"""Dataclasses de datos (pure data, sin UI)."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class TokenTotals:
    input: int = 0
    output: int = 0
    reasoning: int = 0
    cache_read: int = 0
    cache_write: int = 0
    cost: float = 0.0
    turns: int = 0
    sessions: int = 0

    @property
    def total(self) -> int:
        return self.input + self.output

    @property
    def cache_hit_ratio(self) -> float:
        denom = self.input + self.cache_read
        return self.cache_read / denom if denom else 0.0


@dataclass(frozen=True)
class DayTokens:
    day: date
    input: int
    output: int
    cost: float = 0.0
    cache_read: int = 0

    @property
    def cache_hit_ratio(self) -> float:
        """Fracción de input servida desde caché ese día (0..1)."""
        denom = self.input + self.cache_read
        return self.cache_read / denom if denom else 0.0


@dataclass(frozen=True)
class ModelStat:
    model_id: str
    provider_id: str
    input: int
    output: int
    reasoning: int
    cache_read: int
    cost: float
    turns: int

    @property
    def cost_per_1k_output(self) -> float | None:
        """Costo por cada 1000 tokens de output. None si no produjo output."""
        if self.output <= 0:
            return None
        return self.cost / (self.output / 1000)


@dataclass(frozen=True)
class AgentStat:
    agent: str
    input: int
    output: int
    cost: float
    turns: int


@dataclass(frozen=True)
class SessionStat:
    session_id: str
    input: int
    output: int
    cost: float
    turns: int
    last_ts_ms: int


@dataclass(frozen=True)
class HeatCell:
    weekday: int  # 0 = lunes ... 6 = domingo
    hour: int  # 0..23
    tokens: int
