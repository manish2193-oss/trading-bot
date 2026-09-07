from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class Bar:
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float = 0.0


@dataclass(frozen=True)
class Contract:
    symbol: str
    point_value: float
    tick_size: float
    tick_value: float


@dataclass(frozen=True)
class CostModel:
    commission_per_side: float
    slippage_ticks_per_side: float

    def fill_price(self, raw_price: float, is_buy: bool, contract: Contract) -> float:
        adverse_move = self.slippage_ticks_per_side * contract.tick_size
        return raw_price + adverse_move if is_buy else raw_price - adverse_move

    def side_cost(self) -> float:
        return self.commission_per_side


MES = Contract(symbol="MES", point_value=5.0, tick_size=0.25, tick_value=1.25)
MNQ = Contract(symbol="MNQ", point_value=2.0, tick_size=0.25, tick_value=0.50)
MGC = Contract(symbol="MGC", point_value=10.0, tick_size=0.10, tick_value=1.00)

