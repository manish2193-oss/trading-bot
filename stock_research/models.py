from datetime import datetime
from pydantic import BaseModel, Field

class StockSnapshot(BaseModel):
    symbol: str; company: str; industry: str
    price: float = Field(gt=0)
    as_of: datetime; source: str
    pe_ratio: float | None = None; peg_ratio: float | None = None
    eps_growth_pct: float | None = None; revenue_growth_pct: float | None = None
    gross_margin_pct: float | None = None; operating_margin_pct: float | None = None
    debt_to_equity: float | None = None; sma_50: float | None = None
    sma_200: float | None = None; atr_14: float | None = None
    sentiment: float | None = Field(default=None, ge=-1, le=1)

class Assessment(BaseModel):
    symbol: str; eligible: bool; score: float | None; coverage_pct: float
    quality_score: float | None; growth_score: float | None; valuation_score: float | None; momentum_score: float | None
    entry_low: float | None; entry_high: float | None; target_price: float | None; invalidation_price: float | None
    evidence: list[str]; risks: list[str]; as_of: datetime; source: str
