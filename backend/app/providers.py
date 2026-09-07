"""Server-side provider boundaries. Trading/order execution is intentionally absent."""
from dataclasses import dataclass
from datetime import datetime
from typing import Protocol
@dataclass(frozen=True)
class Quote: symbol:str; price:float; as_of:datetime; source:str; delayed:bool
class FuturesMarketDataProvider(Protocol):
    def latest_quote(self,symbol:str)->Quote: ...
class Trading212PortfolioProvider(Protocol):
    """Read-only portfolio synchronisation; not a CME futures adapter."""
    def portfolio_snapshot(self)->dict: ...
