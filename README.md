# Trading Bot — futures research lab

This is a **research and paper-trading** project for liquid, exchange-traded futures. It cannot send live orders and contains no broker credentials or live API code.

## Application

- `web/`: React/TypeScript dashboard with research status, controls, charts and PDF export (via browser print).
- `backend/`: FastAPI paper-only service; it contains no broker order-routing code.
- `supabase/migrations/`: isolated `trading_bot` schema for paper fills, quotes and runs, protected by RLS. It does not modify existing application tables.
- `futures_research/`: deterministic Python research/backtesting engine.

The dashboard never invents prices. It locks automation until an entitled futures-market data provider is configured. Trading 212 can later be a **read-only** Invest/ISA portfolio synchronisation, not a CME futures connection.

```bash
python3 -m venv .venv && . .venv/bin/activate
pip install -r backend/requirements.txt
uvicorn backend.app.main:app --reload --port 8000
cd web && npm run dev
```

The workflow is intentionally gated:

1. Import trustworthy, adjusted OHLCV data.
2. Run a cost-aware backtest without look-ahead bias.
3. Validate with walk-forward, out-of-sample periods.
4. Paper trade the unchanged strategy and reconcile every fill.
5. Review the live-trading checklist before adding any broker integration.

## First instrument

Begin with one liquid micro contract, not many markets. The default sample configuration is MES (Micro E-mini S&P 500), where each index point is $5 and each tick is $1.25. Margin is not a risk budget: set the loss limits below independently.

## Install and run

This first version uses only Python's standard library.

```bash
python3 -m unittest discover -s tests -v
python3 -m futures_research.cli backtest --csv examples/mes_sample.csv --fast 2 --slow 4
```

CSV columns must be `timestamp,open,high,low,close,volume`, ordered oldest first. Use a data source whose exchange, session, roll/adjustment policy, timezone, and licensing you understand. Do not mix unadjusted contracts across rolls.

## Safety defaults

- One contract maximum
- Long/flat only (no shorting in v1)
- Next-bar-open execution, never same-bar fills
- Commission and adverse slippage included in every fill
- Daily loss circuit breaker and maximum drawdown reporting
- No live broker module

Read [docs/research-plan.md](docs/research-plan.md) before interpreting a backtest result.
