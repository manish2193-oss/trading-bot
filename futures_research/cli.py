from __future__ import annotations

import argparse
from dataclasses import asdict
import json

from .backtest import run_backtest
from .data import load_ohlcv_csv
from .models import CostModel, MES
from .strategy import MovingAverageTrend


def main() -> None:
    parser = argparse.ArgumentParser(description="Research-only futures backtester")
    subcommands = parser.add_subparsers(dest="command", required=True)
    backtest = subcommands.add_parser("backtest")
    backtest.add_argument("--csv", required=True)
    backtest.add_argument("--fast", type=int, default=20)
    backtest.add_argument("--slow", type=int, default=80)
    backtest.add_argument("--commission", type=float, default=1.50)
    backtest.add_argument("--slippage-ticks", type=float, default=1.0)
    arguments = parser.parse_args()

    if arguments.command == "backtest":
        result = run_backtest(
            load_ohlcv_csv(arguments.csv),
            MovingAverageTrend(arguments.fast, arguments.slow),
            MES,
            CostModel(arguments.commission, arguments.slippage_ticks),
        )
        payload = asdict(result)
        payload["fills"] = list(payload["fills"])
        print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()

