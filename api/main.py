from __future__ import annotations

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from .scanner import LiveDataError, scan_symbol, scan_universe

app = FastAPI(
    title="Zorathvael Futures Scanner API",
    version="1.0.0",
    description="Live Binance USDT-M Futures scanner. No mock market data.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

DEFAULT_UNIVERSE = [
    "BTCUSDT", "ETHUSDT", "SOLUSDT", "XRPUSDT", "DOGEUSDT",
    "SUIUSDT", "ADAUSDT", "AVAXUSDT", "LINKUSDT", "1000PEPEUSDT",
    "WIFUSDT", "APTUSDT", "NEARUSDT", "INJUSDT", "SEIUSDT",
]


@app.get("/")
def root():
    return {
        "service": "Zorathvael Futures Scanner API",
        "version": app.version,
        "data_source": "Binance USDT-M Futures public API",
        "mock_data": False,
        "endpoints": ["/health", "/scan", "/scan/universe"],
    }


@app.get("/health")
def health():
    return {"status": "ok", "live_data_source": "binance-futures-public"}


@app.get("/scan")
def scan(
    symbol: str = Query(..., description="Example: SUIUSDT"),
    interval: str = Query("15m"),
):
    try:
        return scan_symbol(symbol, interval)
    except LiveDataError as exc:
        return {
            "symbol": symbol.upper(),
            "interval": interval,
            "status": "NO TRADE — LIVE DATA UNAVAILABLE",
            "live_data": False,
            "error": str(exc),
        }
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.get("/scan/universe")
def scan_market(
    symbols: str | None = Query(
        None,
        description="Comma-separated symbols. Defaults to a liquid altcoin universe.",
    )
):
    selected = (
        [x.strip().upper() for x in symbols.split(",") if x.strip()]
        if symbols
        else DEFAULT_UNIVERSE
    )
    return {
        "interval": "15m",
        "data_source": "Binance USDT-M Futures public API",
        "mock_data": False,
        "results": scan_universe(selected),
    }
