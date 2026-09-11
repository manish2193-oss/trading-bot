# Trading Bot — SignalDesk

SignalDesk is an equity research and portfolio-monitoring application. It ranks eligible companies by industry using sourced prices, filings, quality, growth, valuation and trend metrics. It **does not place trades**, promise returns, or substitute for regulated financial advice.

## Workflow

1. A scheduled Python job retrieves daily prices and indicators from Alpha Vantage and fundamentals from SEC EDGAR.
2. The deterministic engine scores only records with at least 85% metric coverage. Every result retains a source and timestamp.
3. Entry zones use price, the 50-day trend and 14-day ATR. Targets use a 2:1 reward/risk reference; these are review levels, not forecasts.
4. You buy through your broker only after your own review, then record the actual quantity and fill price.
5. Monitoring raises review alerts for targets, invalidation levels, trend deterioration, changed fundamentals and negative sourced news. It never sells automatically.

The free-data version uses a small universe because Alpha Vantage's free tier is limited to 25 requests per day. Full-market or intraday screening requires a licensed feed.

## Run locally

```bash
cp .env.example .env
python3 -m venv .venv
. .venv/bin/activate
pip install -r backend/requirements.txt
uvicorn backend.app.main:app --reload --port 8000
```

In a second terminal:

```bash
cd web
npm install
npm run dev
```

The dashboard starts empty by design. Add a real Alpha Vantage key to `.env`; never add secrets to GitHub. The Supabase migration stays inside the existing `trading_bot` schema and does not modify public tables.

## AI boundary

OpenAI is optional. Use it after deterministic pre-screening to summarize cited evidence, extract risks from news, and produce structured explanations. Never ask a language model to invent prices, EPS or margins; those must come from market/filing providers. API billing is separate from a ChatGPT subscription.

## Tests

```bash
python3 -m unittest discover -s tests -v
cd web && npm run build
```
