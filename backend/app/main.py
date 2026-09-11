from __future__ import annotations
import json, os
from datetime import UTC, datetime
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from stock_research.models import StockSnapshot
from stock_research.scoring import assess_stock

STATE_PATH = Path(os.environ.get("RESEARCH_STATE_PATH", "research-runtime-state.json"))
app = FastAPI(title="SignalDesk Research API", version="0.2.0")
app.add_middleware(CORSMiddleware, allow_origins=os.environ.get("CORS_ORIGINS", "http://localhost:5173").split(","), allow_methods=["*"], allow_headers=["*"])

class PositionIn(BaseModel):
    symbol: str = Field(min_length=1, max_length=12)
    company: str = Field(min_length=1, max_length=100)
    industry: str = Field(min_length=1, max_length=100)
    quantity: float = Field(gt=0)
    purchase_price: float = Field(gt=0)
    target_price: float | None = Field(default=None, gt=0)
    invalidation_price: float | None = Field(default=None, gt=0)

def empty_state(): return {"positions": [], "candidates": [], "alerts": [], "last_scan": None}
def read_state():
    if not STATE_PATH.exists(): return empty_state()
    try: return {**empty_state(), **json.loads(STATE_PATH.read_text())}
    except (json.JSONDecodeError, OSError): return empty_state()
def write_state(state: dict): STATE_PATH.write_text(json.dumps(state, indent=2))

@app.get("/health")
def health(): return {"status": "ok", "mode": "research-only", "order_routing": False}

@app.get("/api/dashboard")
def dashboard():
    state, configured = read_state(), bool(os.environ.get("ALPHA_VANTAGE_API_KEY"))
    return {**state, "scanner": {"state": "scheduled" if configured else "needs_configuration", "cadence": os.environ.get("SCREENING_CADENCE", "daily"), "provider": "Alpha Vantage + SEC EDGAR" if configured else "unconfigured"}, "notices": [] if configured else ["Add ALPHA_VANTAGE_API_KEY to enable evidence-backed daily screening. No sample prices are displayed."]}

@app.post("/api/portfolio", status_code=201)
def add_position(position: PositionIn):
    state = read_state()
    if any(p["symbol"] == position.symbol.upper() and p.get("status", "open") == "open" for p in state["positions"]): raise HTTPException(409, "An open position already exists for this symbol.")
    record = {**position.model_dump(), "symbol": position.symbol.upper(), "status": "open", "opened_at": datetime.now(UTC).isoformat(), "current_price": None, "unrealised_pnl": None}
    state["positions"].append(record); write_state(state); return record

@app.post("/api/portfolio/{symbol}/close")
def close_position(symbol: str):
    state = read_state(); match = next((p for p in state["positions"] if p["symbol"] == symbol.upper() and p.get("status") == "open"), None)
    if not match: raise HTTPException(404, "Open position not found.")
    match["status"], match["closed_at"] = "closed", datetime.now(UTC).isoformat(); write_state(state); return match

@app.post("/api/research/evaluate")
def evaluate(snapshot: StockSnapshot): return assess_stock(snapshot).model_dump(mode="json")
