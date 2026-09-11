from datetime import UTC, datetime
import unittest
from stock_research.models import StockSnapshot
from stock_research.scoring import assess_stock

class Tests(unittest.TestCase):
    def test_incomplete_is_withheld(self):
        r=assess_stock(StockSnapshot(symbol="ABC",company="ABC",industry="Test",price=10,as_of=datetime.now(UTC),source="test")); self.assertFalse(r.eligible); self.assertIsNone(r.score)
    def test_entry_has_reward(self):
        r=assess_stock(StockSnapshot(symbol="ABC",company="ABC",industry="Tech",price=100,as_of=datetime.now(UTC),source="test",pe_ratio=18,peg_ratio=1.1,eps_growth_pct=20,revenue_growth_pct=12,gross_margin_pct=65,operating_margin_pct=28,debt_to_equity=.4,sma_50=98,sma_200=90,atr_14=3,sentiment=.2)); self.assertTrue(r.eligible); self.assertLess(r.invalidation_price,r.entry_low); self.assertGreater(r.target_price,r.entry_high)
