from __future__ import annotations
import os
from datetime import UTC, datetime
from pathlib import Path
from typing import Literal
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from .providers import IbkrDelayedFuturesProvider

STATE_PATH = Path(os.environ.get("VECTOR_STATE_PATH", "paper-runtime-state.json"))
app = FastAPI(title="VectorLab Research API", version="0.1.0")
app.add_middleware(CORSMiddleware, allow_origins=os.environ.get("CORS_ORIGINS", "http://localhost:5173").split(","), allow_methods=["*"], allow_headers=["*"])
class Automation(BaseModel):
    state: Literal["stopped", "running", "paused"] = "stopped"
    mode: Literal["paper"] = "paper"
    updated_at: datetime
def read_state() -> Automation:
    return Automation.model_validate_json(STATE_PATH.read_text()) if STATE_PATH.exists() else Automation(updated_at=datetime.now(UTC))
def write_state(state: Literal["stopped", "running", "paused"]) -> Automation:
    result=Automation(state=state,updated_at=datetime.now(UTC)); STATE_PATH.write_text(result.model_dump_json()); return result
@app.get("/health")
def health(): return {"status":"ok","mode":"paper-only"}
@app.get("/api/dashboard")
def dashboard():
    market={"symbol":"MES","price":None,"as_of":None,"source":"unconfigured","delayed":False}; alerts=[]
    if os.environ.get("MARKET_DATA_PROVIDER") == "ibkr":
        expiry=os.environ.get("IBKR_FUTURES_EXPIRY", "")
        if not expiry: alerts.append("IBKR_FUTURES_EXPIRY is required; contract expiry is never guessed.")
        else:
            try:
                quote=IbkrDelayedFuturesProvider(os.environ.get("IBKR_HOST","127.0.0.1"),int(os.environ.get("IBKR_PORT","7947")),int(os.environ.get("IBKR_CLIENT_ID","71")),expiry).latest_quote("MES")
                market={"symbol":quote.symbol,"price":quote.price,"as_of":quote.as_of,"source":quote.source,"delayed":quote.delayed}
            except Exception as error: alerts.append(str(error))
    else: alerts.append("No entitled exchange-data provider has been configured. Automation cannot start.")
    return {"automation":read_state().model_dump(mode="json"),"market":market,"portfolio":{"equity":5000,"cash":5000,"open_positions":0,"realised_pnl":0},"equity_curve":[],"alerts":alerts}
@app.post("/api/automation/{action}")
def control(action: Literal["start","pause","resume","stop"]):
    current=read_state()
    if action=="start" and os.environ.get("MARKET_DATA_PROVIDER") != "ibkr": raise HTTPException(409,"Market-data provider is not configured; paper automation remains locked.")
    if action=="pause" and current.state!="running": raise HTTPException(409,"Only a running automation can be paused.")
    if action=="resume" and current.state!="paused": raise HTTPException(409,"Only a paused automation can be resumed.")
    return write_state("stopped" if action=="stop" else "paused" if action=="pause" else "running").model_dump(mode="json")
