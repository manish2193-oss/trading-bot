from __future__ import annotations

from dataclasses import dataclass

from .backtest import BacktestResult, run_backtest
from .models import Bar, Contract, CostModel
from .strategy import MovingAverageTrend


@dataclass(frozen=True)
class WalkForwardWindow:
    train_start: int
    train_end: int
    test_start: int
    test_end: int


def rolling_windows(total_bars: int, train_bars: int, test_bars: int) -> list[WalkForwardWindow]:
    if train_bars < 3 or test_bars < 1:
        raise ValueError("Invalid window sizes")
    windows = []
    start = 0
    while start + train_bars + test_bars <= total_bars:
        windows.append(WalkForwardWindow(start, start + train_bars, start + train_bars, start + train_bars + test_bars))
        start += test_bars
    return windows


def walk_forward_test(
    bars: list[Bar], strategy: MovingAverageTrend, contract: Contract, costs: CostModel,
    train_bars: int, test_bars: int,
) -> list[BacktestResult]:
    """Tests frozen parameters on sequential unseen windows; no optimisation performed here."""
    return [
        run_backtest(bars[w.test_start:w.test_end], strategy, contract, costs)
        for w in rolling_windows(len(bars), train_bars, test_bars)
    ]

