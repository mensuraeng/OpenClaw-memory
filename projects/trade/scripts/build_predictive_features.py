#!/usr/bin/env python3
"""Build deterministic predictive features from trade.market_bars.

Features are research inputs only. They do not produce orders.
"""
from __future__ import annotations

import argparse
import json
import math
import os
from collections import defaultdict, deque
from pathlib import Path
from statistics import mean, pstdev
from typing import Any

try:
    import psycopg2  # type: ignore
    import psycopg2.extras  # type: ignore
except Exception:  # noqa: BLE001
    psycopg2 = None

WORKSPACE = Path("/root/.openclaw/workspace")
ENV_FILE = WORKSPACE / "memory/context/trade_supabase.env"
DEFAULT_DB_URL = "postgresql://postgres:postgres@127.0.0.1:54322/postgres"


def load_env_file(path: Path = ENV_FILE) -> None:
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        os.environ.setdefault(k, v)


def get_feature_set_id(cur) -> str:
    cur.execute("select id from trade.feature_sets where name = 'predictive_technical_daily' and version = '0.1'")
    row = cur.fetchone()
    if row:
        return row["id"] if isinstance(row, dict) else row[0]
    cur.execute(
        """
        insert into trade.feature_sets(name, version, description, feature_definitions, status)
        values ('predictive_technical_daily', '0.1', 'Daily deterministic technical features for predictive research.', %s::jsonb, 'research')
        returning id
        """,
        (json.dumps({
            "ret_1d": "1-day close return",
            "ret_5d": "5-day close return",
            "ret_20d": "20-day close return",
            "vol_20d_ann": "20-day annualized realized volatility",
            "ma_20_ratio": "close / 20-day moving average - 1",
            "ma_50_ratio": "close / 50-day moving average - 1",
            "drawdown_252d": "close / trailing 252-day high - 1",
            "volume_z_20d": "volume z-score vs trailing 20 days",
            "range_pct": "(high - low) / close",
        }),),
    )
    row = cur.fetchone()
    return row["id"] if isinstance(row, dict) else row[0]


def fetch_bars(cur, symbols: list[str] | None, limit_assets: int | None) -> dict[str, list[dict[str, Any]]]:
    params: list[Any] = []
    where = ""
    if symbols:
        where = "where a.symbol = any(%s)"
        params.append(symbols)
    elif limit_assets:
        where = "where a.id in (select id from trade.assets where is_active order by symbol limit %s)"
        params.append(limit_assets)
    cur.execute(
        f"""
        select a.id as asset_id, a.symbol, mb.ts, mb.open, mb.high, mb.low, mb.close, mb.adjusted_close, mb.volume
        from trade.market_bars mb
        join trade.assets a on a.id = mb.asset_id
        {where}
        order by a.symbol, mb.ts
        """,
        params,
    )
    rows = cur.fetchall()
    by_symbol: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        by_symbol[row["symbol"]].append(dict(row))
    return by_symbol


def safe_return(now: float | None, prev: float | None) -> float | None:
    if now is None or prev in (None, 0):
        return None
    return float(now) / float(prev) - 1.0


def zscore(value: float | None, values: list[float]) -> float | None:
    if value is None or len(values) < 5:
        return None
    sigma = pstdev(values)
    if sigma == 0:
        return None
    return (value - mean(values)) / sigma


def build_symbol_features(rows: list[dict[str, Any]]) -> list[tuple[str, str, dict[str, Any]]]:
    closes: list[float] = []
    volumes: list[float] = []
    out: list[tuple[str, str, dict[str, Any]]] = []
    returns_1d_window: deque[float] = deque(maxlen=20)

    for row in rows:
        close = float(row["adjusted_close"] or row["close"])
        high = float(row["high"]) if row.get("high") is not None else None
        low = float(row["low"]) if row.get("low") is not None else None
        volume = float(row["volume"]) if row.get("volume") is not None else None

        ret_1d = safe_return(close, closes[-1] if closes else None)
        if ret_1d is not None:
            returns_1d_window.append(ret_1d)

        def ret_n(n: int) -> float | None:
            return safe_return(close, closes[-n]) if len(closes) >= n else None

        def ma_ratio(n: int) -> float | None:
            if len(closes) < n:
                return None
            avg = mean(closes[-n:])
            return close / avg - 1.0 if avg else None

        trailing_high = max(closes[-252:] or [close])
        vol_window = list(returns_1d_window)
        features = {
            "ret_1d": ret_1d,
            "ret_5d": ret_n(5),
            "ret_20d": ret_n(20),
            "vol_20d_ann": (pstdev(vol_window) * math.sqrt(252)) if len(vol_window) >= 10 else None,
            "ma_20_ratio": ma_ratio(20),
            "ma_50_ratio": ma_ratio(50),
            "drawdown_252d": close / trailing_high - 1.0 if trailing_high else None,
            "volume_z_20d": zscore(volume, volumes[-20:]) if volume is not None else None,
            "range_pct": ((high - low) / close) if high is not None and low is not None and close else None,
        }
        out.append((row["asset_id"], row["ts"].isoformat() if hasattr(row["ts"], "isoformat") else str(row["ts"]), features))
        closes.append(close)
        if volume is not None:
            volumes.append(volume)
    return out


def ingest_features(db_url: str, symbols: list[str] | None, limit_assets: int | None) -> dict[str, int]:
    if psycopg2 is None:
        raise RuntimeError("psycopg2 is required")
    counts = {"assets": 0, "features": 0}
    with psycopg2.connect(db_url) as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            feature_set_id = get_feature_set_id(cur)
            by_symbol = fetch_bars(cur, symbols, limit_assets)
            counts["assets"] = len(by_symbol)
            for symbol, rows in by_symbol.items():
                for asset_id, ts, features in build_symbol_features(rows):
                    cur.execute(
                        """
                        insert into trade.asset_features(asset_id, feature_set_id, timeframe, ts, features)
                        values (%s,%s,'1d',%s,%s::jsonb)
                        on conflict (asset_id, feature_set_id, timeframe, ts) do update set
                          features = excluded.features
                        """,
                        (asset_id, feature_set_id, ts, json.dumps(features)),
                    )
                    counts["features"] += 1
    return counts


def main() -> int:
    parser = argparse.ArgumentParser(description="Build predictive technical features from Trade OHLCV")
    parser.add_argument("--symbols", nargs="*")
    parser.add_argument("--limit-assets", type=int)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    load_env_file()
    counts = ingest_features(os.getenv("TRADE_DATABASE_URL", DEFAULT_DB_URL), args.symbols, args.limit_assets)
    summary = {"counts": counts, "safety": {"read_only": True, "execution_allowed": False, "real_money": False}}
    print(json.dumps(summary, ensure_ascii=False, indent=2) if args.json else summary)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
