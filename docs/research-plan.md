# Research plan and promotion gate

## Objective

Find out whether a simple, explainable strategy has a persistent edge **after** costs. The objective is not to target a monthly income figure. A backtest is evidence, not a promise.

## Data rules

- Store immutable raw files outside Git; record source, download date, timezone and adjustment method.
- Test at least distinct regimes: calm bull market, sharp sell-off, high-inflation/rate-change period, and sideways market.
- Do not choose parameters after looking at the test period. Keep a final untouched holdout period.
- Futures series need a documented roll method. Back-adjustment can distort absolute price levels; the chosen method must be consistent for all comparisons.

## Minimum evaluation sequence

1. **In-sample:** develop a small number of hypotheses only.
2. **Walk-forward:** optimise only on each past window, test on the next window.
3. **Holdout:** run once after the rules are frozen.
4. **Stress tests:** double costs/slippage, delay fills one bar, remove the best 5 trades, and test neighbouring parameters.
5. **Paper trading:** trade the exact frozen rules for at least 3 months and at least 50 eligible signals. Compare planned versus actual fills and costs.

## Promotion gate (all required)

- Positive out-of-sample expectancy after conservative costs.
- No single month or trade supplies most of the total profit.
- Results remain viable when costs are doubled and parameters change slightly.
- Maximum drawdown is affordable and within the pre-written limit.
- Paper execution matches the model closely enough to explain differences.
- A human reviews every strategy/risk configuration change.
- Broker, legal/tax, market-data and operational requirements have been independently checked.

Until all gates pass, the project stays paper-only.

## Initial risk policy

For a hypothetical £5,000 account: one micro contract maximum, no averaging down, no overnight positions at first, and a daily loss limit selected before the session. The backtester reports USD because CME contracts are USD-denominated; GBP conversion and tax records must be handled separately.

