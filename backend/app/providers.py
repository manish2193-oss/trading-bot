"""Server-side provider boundaries. Trading/order execution is intentionally absent."""
from dataclasses import dataclass
from datetime import UTC, datetime
from threading import Event, Thread
from typing import Protocol
import time
@dataclass(frozen=True)
class Quote: symbol:str; price:float; as_of:datetime; source:str; delayed:bool
class FuturesMarketDataProvider(Protocol):
    def latest_quote(self,symbol:str)->Quote: ...
class Trading212PortfolioProvider(Protocol):
    """Read-only portfolio synchronisation; not a CME futures adapter."""
    def portfolio_snapshot(self)->dict: ...


class IbkrDelayedFuturesProvider:
    """Read one delayed/live quote from TWS or IB Gateway; no order methods."""
    def __init__(self, host: str, port: int, client_id: int, expiry: str, timeout: float = 8.0):
        self.host, self.port, self.client_id, self.expiry, self.timeout = host, port, client_id, expiry, timeout

    def latest_quote(self, symbol: str) -> Quote:
        try:
            from ibapi.client import EClient
            from ibapi.contract import Contract
            from ibapi.wrapper import EWrapper
        except ImportError as error:
            raise RuntimeError("Install IBKR's official TWS Python API in the backend environment") from error
        ready, quote_ready = Event(), Event()
        result: dict[str, object] = {"price": None, "data_type": 3, "error": None}

        class App(EWrapper, EClient):
            def __init__(self): EClient.__init__(self, self)
            def nextValidId(self, orderId): ready.set()
            def marketDataType(self, reqId, marketDataType): result["data_type"] = marketDataType
            def tickPrice(self, reqId, tickType, price, attrib):
                if tickType in (4, 68) and price and price > 0: result["price"] = float(price); quote_ready.set()
            def error(self, reqId, errorTime, errorCode, errorString, advancedOrderReject=""):
                if errorCode not in (2104, 2106, 2158): result["error"] = f"IBKR {errorCode}: {errorString}"

        app = App(); app.connect(self.host, self.port, self.client_id); Thread(target=app.run, daemon=True).start()
        try:
            if not ready.wait(self.timeout): raise RuntimeError("IBKR Gateway/TWS connection timed out")
            contract = Contract(); contract.symbol = symbol; contract.secType = "FUT"; contract.exchange = "CME"; contract.currency = "USD"; contract.lastTradeDateOrContractMonth = self.expiry
            app.reqMarketDataType(3); app.reqMktData(9101, contract, "", False, False, [])
            if not quote_ready.wait(self.timeout): raise RuntimeError(str(result["error"] or "IBKR returned no usable last price"))
            return Quote(symbol, float(result["price"]), datetime.now(UTC), "IBKR TWS API", int(result["data_type"]) != 1)
        finally:
            if app.isConnected(): app.cancelMktData(9101); time.sleep(.05); app.disconnect()
