from __future__ import annotations

from dataclasses import dataclass

from .models import Bar, Contract, CostModel
from .strategy import MovingAverageTrend


@dataclass(frozen=True)
class Fill:
    timestamp: str
    side: str
    price: float
    reason: str


@dataclass(frozen=True)
class BacktestResult:
    starting_cash: float
    ending_equity: float
    net_profit: float
    max_drawdown: float
    trades: int
    fills: tuple[Fill, ...]


def run_backtest(
    bars: list[Bar], strategy: MovingAverageTrend, contract: Contract,
    costs: CostModel, starting_cash: float = 5_000.0,
) -> BacktestResult:
    """One-contract long/flat backtest. Signals execute on the following open."""
    cash = starting_cash
    position = 0
    entry_price: float | None = None
    equity_high = starting_cash
    max_drawdown = 0.0
    fills: list[Fill] = []
    pending_target: int | None = None

    for index, bar in enumerate(bars):
        if pending_target is not None and pending_target != position:
            is_buy = pending_target > position
            price = costs.fill_price(bar.open, is_buy=is_buy, contract=contract)
            if is_buy:
                entry_price = price
                cash -= costs.side_cost()
                fills.append(Fill(bar.timestamp.isoformat(), "BUY", price, "signal"))
            else:
                assert entry_price is not None
                cash += (price - entry_price) * contract.point_value - costs.side_cost()
                entry_price = None
                fills.append(Fill(bar.timestamp.isoformat(), "SELL", price, "signal"))
            position = pending_target

        mark_to_market = cash
        if position and entry_price is not None:
            mark_to_market += (bar.close - entry_price) * contract.point_value
        equity_high = max(equity_high, mark_to_market)
        max_drawdown = max(max_drawdown, equity_high - mark_to_market)

        # A close-generated decision cannot be used until the next bar.
        pending_target = strategy.target_position(bars[: index + 1])

    if position and entry_price is not None:
        final_bar = bars[-1]
        price = costs.fill_price(final_bar.close, is_buy=False, contract=contract)
        cash += (price - entry_price) * contract.point_value - costs.side_cost()
        fills.append(Fill(final_bar.timestamp.isoformat(), "SELL", price, "end_of_test"))

    return BacktestResult(
        starting_cash=starting_cash,
        ending_equity=cash,
        net_profit=cash - starting_cash,
        max_drawdown=max_drawdown,
        trades=sum(fill.side == "SELL" for fill in fills),
        fills=tuple(fills),
    )

