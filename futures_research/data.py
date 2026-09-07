from __future__ import annotations

import csv
from datetime import datetime
from pathlib import Path

from .models import Bar


REQUIRED_COLUMNS = {"timestamp", "open", "high", "low", "close", "volume"}


def load_ohlcv_csv(path: str | Path) -> list[Bar]:
    """Load oldest-first OHLCV data and reject malformed or non-monotonic rows."""
    with Path(path).open(newline="") as file:
        reader = csv.DictReader(file)
        if not reader.fieldnames or not REQUIRED_COLUMNS.issubset(reader.fieldnames):
            raise ValueError(f"CSV must include: {sorted(REQUIRED_COLUMNS)}")
        bars = [
            Bar(
                timestamp=datetime.fromisoformat(row["timestamp"].replace("Z", "+00:00")),
                open=float(row["open"]), high=float(row["high"]), low=float(row["low"]),
                close=float(row["close"]), volume=float(row["volume"]),
            )
            for row in reader
        ]
    if len(bars) < 3:
        raise ValueError("At least three bars are required")
    if any(b.open <= 0 or b.high < b.low or not b.low <= b.close <= b.high for b in bars):
        raise ValueError("Invalid OHLC values")
    if any(a.timestamp >= b.timestamp for a, b in zip(bars, bars[1:])):
        raise ValueError("Timestamps must be strictly oldest-first")
    return bars

