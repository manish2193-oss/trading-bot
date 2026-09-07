# IBKR delayed futures data setup

This integration is market-data only and contains no order-placement code.

1. Open the IBKR paper account and log in through Trader Workstation (TWS) or IB Gateway.
2. Enable socket clients in API settings and keep read-only API mode enabled.
3. Install IBKR's official TWS Python API into this project's `.venv`.
4. Copy `.env.example` to `backend/.env` and set `MARKET_DATA_PROVIDER=ibkr`.
5. Use port `7497` for paper TWS or `4002` for paper Gateway unless configured differently.
6. Set `IBKR_FUTURES_EXPIRY` explicitly to the MES contract under research. Expiry is never guessed.

The adapter requests IBKR market-data type 3. IBKR supplies delayed data without a subscription and automatically returns live data where the account is entitled. The dashboard labels the returned type.
