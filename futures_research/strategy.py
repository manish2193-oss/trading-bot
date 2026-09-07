from __future__ import annotations

from dataclasses import dataclass

from .models import Bar


def simple_moving_average(values: list[float], period: int) -> float | None:
    if len(values) < period:
        return None
    return sum(values[-period:]) / period


@dataclass(frozen=True)
class MovingAverageTrend:
    """Long/flat trend rule. Signal at close; execution occurs next bar open."""
    fast_period: int = 20
    slow_period: int = 80

    def __post_init__(self) -> None:
        if not 1 < self.fast_period < self.slow_period:
            raise ValueError("Require 1 < fast_period < slow_period")

    def target_position(self, history: list[Bar]) -> int:
        closes = [bar.close for bar in history]
        fast = simple_moving_average(closes, self.fast_period)
        slow = simple_moving_average(closes, self.slow_period)
        if fast is None or slow is None:
            return 0
        return 1 if fast > slow else 0

