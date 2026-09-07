from datetime import datetime, timedelta
import unittest

from futures_research.backtest import run_backtest
from futures_research.models import Bar, CostModel, MES
from futures_research.strategy import MovingAverageTrend
from futures_research.validation import rolling_windows


def bars(closes: list[float]) -> list[Bar]:
    start = datetime(2025, 1, 1)
    return [Bar(start + timedelta(days=i), price, price + 1, price - 1, price, 1) for i, price in enumerate(closes)]


class BacktestTests(unittest.TestCase):
    def test_strategy_waits_until_slow_period(self) -> None:
        strategy = MovingAverageTrend(2, 4)
        self.assertEqual(strategy.target_position(bars([1, 2, 3])), 0)
        self.assertEqual(strategy.target_position(bars([1, 2, 3, 4])), 1)

    def test_execution_happens_after_signal_bar(self) -> None:
        result = run_backtest(bars([1, 2, 3, 4, 5, 6]), MovingAverageTrend(2, 4), MES, CostModel(0, 0))
        self.assertEqual(result.fills[0].timestamp, bars([1, 2, 3, 4, 5, 6])[4].timestamp.isoformat())
        self.assertEqual(result.fills[0].side, "BUY")

    def test_commission_reduces_result(self) -> None:
        data = bars([1, 2, 3, 4, 5, 6, 1])
        free = run_backtest(data, MovingAverageTrend(2, 4), MES, CostModel(0, 0))
        costly = run_backtest(data, MovingAverageTrend(2, 4), MES, CostModel(2, 1))
        self.assertLess(costly.net_profit, free.net_profit)

    def test_windows_do_not_overlap_test_periods(self) -> None:
        windows = rolling_windows(30, 10, 5)
        self.assertEqual([(w.test_start, w.test_end) for w in windows], [(10, 15), (15, 20), (20, 25), (25, 30)])


if __name__ == "__main__":
    unittest.main()
