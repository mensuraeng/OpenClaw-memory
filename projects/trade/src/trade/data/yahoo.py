"""Yahoo Finance lightweight market data adapter.

No credentials. Intended for radar/snapshot only, not execution.
"""
from __future__ import annotations

import json
import time
import urllib.parse
import urllib.request
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from typing import Any


@dataclass
class QuoteSnapshot:
    symbol: str
    source_symbol: str
    currency: str | None
    regular_market_price: float | None
    previous_close: float | None
    open: float | None
    day_high: float | None
    day_low: float | None
    volume: int | None
    market_time: int | None
    change_pct: float | None
    source: str = "yahoo_chart"
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class HistoricalBar:
    symbol: str
    source_symbol: str
    ts: str
    open: float | None
    high: float | None
    low: float | None
    close: float | None
    adjusted_close: float | None
    volume: int | None
    currency: str | None
    source: str = "yahoo_chart"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _urlopen_json(url: str, timeout: int = 15) -> dict[str, Any]:
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 TradeRadar/0.1",
            "Accept": "application/json",
        },
    )
    with urllib.request.urlopen(req, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


def normalize_symbol(symbol: str, market: str) -> str:
    # Yahoo uses hyphen for Berkshire class B while most watchlists use BRK.B.
    if symbol == "BRK.B":
        return "BRK-B"
    if market == "br" and not symbol.endswith(".SA"):
        return f"{symbol}.SA"
    return symbol


def fetch_quote(symbol: str, market: str) -> QuoteSnapshot:
    source_symbol = normalize_symbol(symbol, market)
    encoded = urllib.parse.quote(source_symbol)
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{encoded}?range=5d&interval=1d"

    try:
        payload = _urlopen_json(url)
        result = payload.get("chart", {}).get("result") or []
        if not result:
            err = payload.get("chart", {}).get("error")
            return QuoteSnapshot(symbol, source_symbol, None, None, None, None, None, None, None, None, None, error=str(err))

        item = result[0]
        meta = item.get("meta", {})
        quote = (item.get("indicators", {}).get("quote") or [{}])[0]
        timestamps = item.get("timestamp") or []

        closes = [x for x in quote.get("close", []) if x is not None]
        previous_close = meta.get("chartPreviousClose")
        price = meta.get("regularMarketPrice")
        if price is None and closes:
            price = closes[-1]
        if previous_close is None and len(closes) >= 2:
            previous_close = closes[-2]

        change_pct = None
        if price is not None and previous_close not in (None, 0):
            change_pct = (float(price) / float(previous_close) - 1.0) * 100.0

        return QuoteSnapshot(
            symbol=symbol,
            source_symbol=source_symbol,
            currency=meta.get("currency"),
            regular_market_price=float(price) if price is not None else None,
            previous_close=float(previous_close) if previous_close is not None else None,
            open=float(meta.get("regularMarketOpen")) if meta.get("regularMarketOpen") is not None else None,
            day_high=float(meta.get("regularMarketDayHigh")) if meta.get("regularMarketDayHigh") is not None else None,
            day_low=float(meta.get("regularMarketDayLow")) if meta.get("regularMarketDayLow") is not None else None,
            volume=int(meta.get("regularMarketVolume")) if meta.get("regularMarketVolume") is not None else None,
            market_time=int(meta.get("regularMarketTime")) if meta.get("regularMarketTime") is not None else (timestamps[-1] if timestamps else int(time.time())),
            change_pct=change_pct,
        )
    except Exception as exc:  # noqa: BLE001 - adapter must degrade gracefully
        return QuoteSnapshot(symbol, source_symbol, None, None, None, None, None, None, None, None, None, error=repr(exc))


def fetch_history(symbol: str, market: str, range_: str = "5y", interval: str = "1d") -> list[HistoricalBar]:
    """Fetch historical OHLCV bars from Yahoo Chart API.

    This is read-only, credentialless data collection for research/predictive
    base building. It deliberately returns plain dataclasses so callers can
    decide how to validate, persist and audit records.
    """
    source_symbol = normalize_symbol(symbol, market)
    encoded = urllib.parse.quote(source_symbol)
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{encoded}?range={urllib.parse.quote(range_)}&interval={urllib.parse.quote(interval)}&events=history"
    payload = _urlopen_json(url, timeout=30)
    result = payload.get("chart", {}).get("result") or []
    if not result:
        err = payload.get("chart", {}).get("error")
        raise RuntimeError(f"Yahoo returned no history for {symbol}: {err}")

    item = result[0]
    meta = item.get("meta", {})
    timestamps = item.get("timestamp") or []
    quote = (item.get("indicators", {}).get("quote") or [{}])[0]
    adjclose = (item.get("indicators", {}).get("adjclose") or [{}])[0].get("adjclose") or []

    bars: list[HistoricalBar] = []
    for idx, ts in enumerate(timestamps):
        close = _list_get(quote.get("close"), idx)
        if close is None:
            continue
        bars.append(
            HistoricalBar(
                symbol=symbol,
                source_symbol=source_symbol,
                ts=datetime.fromtimestamp(int(ts), tz=timezone.utc).isoformat(),
                open=_to_float(_list_get(quote.get("open"), idx)),
                high=_to_float(_list_get(quote.get("high"), idx)),
                low=_to_float(_list_get(quote.get("low"), idx)),
                close=_to_float(close),
                adjusted_close=_to_float(_list_get(adjclose, idx)) or _to_float(close),
                volume=_to_int(_list_get(quote.get("volume"), idx)),
                currency=meta.get("currency"),
            )
        )
    return bars


def _list_get(values: Any, idx: int) -> Any:
    if not isinstance(values, list) or idx >= len(values):
        return None
    return values[idx]


def _to_float(value: Any) -> float | None:
    return float(value) if value is not None else None


def _to_int(value: Any) -> int | None:
    return int(value) if value is not None else None
