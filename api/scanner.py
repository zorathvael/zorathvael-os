from __future__ import annotations

import math
import time
from dataclasses import dataclass
from typing import Any

import requests

BINANCE_FAPI = "https://fapi.binance.com"
SESSION = requests.Session()
SESSION.headers.update({"User-Agent": "Zorathvael-Scanner/1.0"})


class LiveDataError(RuntimeError):
    pass


def _get(path: str, params: dict[str, Any] | None = None) -> Any:
    try:
        response = SESSION.get(f"{BINANCE_FAPI}{path}", params=params, timeout=8)
        response.raise_for_status()
        return response.json()
    except Exception as exc:
        raise LiveDataError(f"Binance Futures API unavailable: {exc}") from exc


def _ema(values: list[float], period: int) -> float:
    if len(values) < period:
        return sum(values) / max(len(values), 1)
    k = 2.0 / (period + 1)
    value = sum(values[:period]) / period
    for price in values[period:]:
        value = price * k + value * (1 - k)
    return value


def _rsi(values: list[float], period: int = 14) -> float:
    if len(values) <= period:
        return 50.0
    gains = []
    losses = []
    for a, b in zip(values[-period - 1:-1], values[-period:]):
        delta = b - a
        gains.append(max(delta, 0.0))
        losses.append(max(-delta, 0.0))
    avg_gain = sum(gains) / period
    avg_loss = sum(losses) / period
    if avg_loss == 0:
        return 100.0 if avg_gain else 50.0
    rs = avg_gain / avg_loss
    return 100.0 - (100.0 / (1.0 + rs))


def _atr(rows: list[list[Any]], period: int = 14) -> float:
    if len(rows) < period + 1:
        return 0.0
    trs = []
    previous_close = float(rows[-period - 1][4])
    for row in rows[-period:]:
        high = float(row[2])
        low = float(row[3])
        close = float(row[4])
        trs.append(max(high - low, abs(high - previous_close), abs(low - previous_close)))
        previous_close = close
    return sum(trs) / len(trs)


def _safe_float(value: Any) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


@dataclass
class ScanResult:
    symbol: str
    interval: str
    status: str
    side: str | None
    score: int
    price: float
    entry: float | None
    stop_loss: float | None
    take_profit: list[float]
    leverage: int | None
    metrics: dict[str, Any]
    reasons: list[str]
    live_data: bool = True

    def as_dict(self) -> dict[str, Any]:
        return self.__dict__


def scan_symbol(symbol: str, interval: str = "15m") -> dict[str, Any]:
    symbol = symbol.upper().strip()
    if not symbol.endswith("USDT"):
        symbol += "USDT"
    if interval not in {"5m", "15m", "30m", "1h"}:
        raise ValueError("interval must be one of: 5m, 15m, 30m, 1h")

    # No mocks: every signal is derived from current public Binance Futures data.
    klines = _get("/fapi/v1/klines", {"symbol": symbol, "interval": interval, "limit": 120})
    if len(klines) < 60:
        raise LiveDataError("Insufficient live kline history")

    depth = _get("/fapi/v1/depth", {"symbol": symbol, "limit": 20})
    ticker = _get("/fapi/v1/ticker/24hr", {"symbol": symbol})
    oi = _get("/fapi/v1/openInterest", {"symbol": symbol})
    funding = _get("/fapi/v1/premiumIndex", {"symbol": symbol})

    closes = [float(x[4]) for x in klines]
    volumes = [float(x[5]) for x in klines]
    price = _safe_float(ticker.get("lastPrice")) or closes[-1]
    ema20 = _ema(closes, 20)
    ema50 = _ema(closes, 50)
    rsi = _rsi(closes)
    atr = _atr(klines)

    recent_volume = sum(volumes[-5:]) / 5
    baseline_volume = sum(volumes[-25:-5]) / 20
    volume_ratio = recent_volume / baseline_volume if baseline_volume else 0.0

    bids = sum(_safe_float(x[1]) for x in depth.get("bids", []))
    asks = sum(_safe_float(x[1]) for x in depth.get("asks", []))
    total_book = bids + asks
    imbalance = (bids - asks) / total_book if total_book else 0.0

    oi_value = _safe_float(oi.get("openInterest"))
    funding_rate = _safe_float(funding.get("lastFundingRate"))

    long_points = 0
    short_points = 0
    reasons: list[str] = []

    if price > ema20:
        long_points += 18
    else:
        short_points += 18
    if ema20 > ema50:
        long_points += 18
        reasons.append("EMA20 > EMA50")
    elif ema20 < ema50:
        short_points += 18
        reasons.append("EMA20 < EMA50")

    if 52 <= rsi <= 68:
        long_points += 12
    elif 32 <= rsi <= 48:
        short_points += 12

    if imbalance >= 0.08:
        long_points += 16
        reasons.append("order-book bid imbalance")
    elif imbalance <= -0.08:
        short_points += 16
        reasons.append("order-book ask imbalance")

    if volume_ratio >= 1.25:
        if closes[-1] > closes[-2]:
            long_points += 16
        elif closes[-1] < closes[-2]:
            short_points += 16
        reasons.append("volume expansion")

    # OI is included as a live metric and confirmation input, not fabricated as a
    # directional predictor. Directional OI change requires a second sample.
    if oi_value > 0:
        reasons.append("live open interest available")

    side = "LONG" if long_points > short_points else "SHORT"
    raw_score = max(long_points, short_points)
    score = min(100, int(raw_score))

    # ENTRY NOW requires meaningful confluence and a liquid/active market.
    entry = stop = None
    tps: list[float] = []
    leverage = None
    status = "WAIT"

    if score >= 68 and volume_ratio >= 1.10 and atr > 0:
        risk = max(atr * 1.15, price * 0.0025)
        if side == "LONG":
            entry = price
            stop = price - risk
            tps = [price + risk * 1.2, price + risk * 2.0, price + risk * 3.0]
        else:
            entry = price
            stop = price + risk
            tps = [price - risk * 1.2, price - risk * 2.0, price - risk * 3.0]
        leverage = 3 if score < 80 else 4
        status = "ENTRY NOW"

    return ScanResult(
        symbol=symbol,
        interval=interval,
        status=status,
        side=side if status == "ENTRY NOW" else None,
        score=score,
        price=price,
        entry=entry,
        stop_loss=stop,
        take_profit=tps,
        leverage=leverage,
        metrics={
            "ema20": ema20,
            "ema50": ema50,
            "rsi14": rsi,
            "atr14": atr,
            "volume_ratio": volume_ratio,
            "order_book_imbalance": imbalance,
            "open_interest": oi_value,
            "funding_rate": funding_rate,
            "change_24h_pct": _safe_float(ticker.get("priceChangePercent")),
            "quote_volume_24h": _safe_float(ticker.get("quoteVolume")),
            "server_time_ms": int(time.time() * 1000),
        },
        reasons=reasons,
    ).as_dict()


def scan_universe(symbols: list[str]) -> list[dict[str, Any]]:
    results = []
    for symbol in symbols:
        try:
            results.append(scan_symbol(symbol, "15m"))
        except Exception as exc:
            results.append({
                "symbol": symbol.upper(),
                "interval": "15m",
                "status": "NO TRADE — LIVE DATA UNAVAILABLE",
                "live_data": False,
                "error": str(exc),
            })
    return results
