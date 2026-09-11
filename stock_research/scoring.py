from .models import Assessment, StockSnapshot

def clamp(v: float): return max(0, min(100, v))
def assess_stock(s: StockSnapshot) -> Assessment:
    required = [s.pe_ratio, s.eps_growth_pct, s.gross_margin_pct, s.operating_margin_pct, s.sma_50, s.sma_200, s.atr_14]
    coverage = sum(v is not None for v in required) / len(required) * 100
    risks, evidence = [], []
    if coverage < 85:
        return Assessment(symbol=s.symbol, eligible=False, score=None, coverage_pct=round(coverage,1), quality_score=None, growth_score=None, valuation_score=None, momentum_score=None, entry_low=None, entry_high=None, target_price=None, invalidation_price=None, evidence=evidence, risks=["Insufficient metric coverage; ranking withheld."], as_of=s.as_of, source=s.source)
    quality = clamp((s.gross_margin_pct or 0)*.9 + (s.operating_margin_pct or 0)*1.8)
    growth = clamp(50+(s.eps_growth_pct or 0)*1.5+(s.revenue_growth_pct or 0)*.5)
    valuation = clamp(100-max(0,(s.pe_ratio or 100)-10)*2.2-max(0,(s.peg_ratio or 1)-1)*12)
    momentum = clamp(50+(s.price/(s.sma_200 or s.price)-1)*180+((s.sma_50 or s.price)/(s.sma_200 or s.price)-1)*120)
    score = quality*.30+growth*.25+valuation*.25+momentum*.20
    atr, anchor = s.atr_14 or s.price*.03, min(s.price, s.sma_50 or s.price)
    low, high = max(.01,anchor-.5*atr), anchor+.25*atr
    invalidation, target = max(.01,low-1.5*atr), high+2*(high-max(.01,low-1.5*atr))
    evidence = [f"Gross margin {s.gross_margin_pct:.1f}% and operating margin {s.operating_margin_pct:.1f}%.", f"EPS growth {s.eps_growth_pct:.1f}%; P/E {s.pe_ratio:.1f}."]
    if s.sentiment is not None and s.sentiment < -.35: risks.append("Recent sourced-news sentiment is materially negative."); score -= 8
    if s.debt_to_equity is not None and s.debt_to_equity > 2: risks.append("Debt-to-equity is elevated."); score -= 6
    if s.price < (s.sma_200 or 0): risks.append("Price is below its 200-day trend.")
    return Assessment(symbol=s.symbol,eligible=score>=60,score=round(clamp(score),1),coverage_pct=round(coverage,1),quality_score=round(quality,1),growth_score=round(growth,1),valuation_score=round(valuation,1),momentum_score=round(momentum,1),entry_low=round(low,2),entry_high=round(high,2),target_price=round(target,2),invalidation_price=round(invalidation,2),evidence=evidence,risks=risks,as_of=s.as_of,source=s.source)
