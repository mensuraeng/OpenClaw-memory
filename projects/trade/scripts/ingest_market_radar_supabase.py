#!/usr/bin/env python3
"""Ingest latest Trade Market Radar JSON into Supabase/Postgres.

Safe by design:
- writes only analytics/reference tables in schema trade;
- does not create orders;
- does not connect to brokers;
- accepts local Postgres/Supabase DB URL via TRADE_DATABASE_URL.
"""
from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

import psycopg2
import psycopg2.extras

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CACHE = PROJECT_ROOT / "runtime" / "cache" / "market-radar-latest.json"
DEFAULT_DB_URL = "postgresql://postgres:postgres@127.0.0.1:54322/postgres"


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def iter_quotes(payload: dict[str, Any]) -> Iterable[tuple[str, str, dict[str, Any], bool]]:
    markets = payload.get("markets", {})
    for market_key, market_payload in markets.items():
        market = "US" if market_key.lower() == "us" else "BR" if market_key.lower() == "br" else market_key.upper()
        for section in ("benchmarks", "watchlist"):
            is_benchmark = section == "benchmarks"
            for quote in market_payload.get(section, []) or []:
                if quote.get("error"):
                    continue
                if not quote.get("symbol") or quote.get("regular_market_price") is None:
                    continue
                yield market, section, quote, is_benchmark


def ts_from_quote(quote: dict[str, Any], generated_at: str | None) -> datetime:
    if quote.get("market_time"):
        return datetime.fromtimestamp(int(quote["market_time"]), tz=timezone.utc)
    if generated_at:
        return datetime.fromisoformat(generated_at.replace("Z", "+00:00"))
    return datetime.now(timezone.utc)


def upsert_asset(cur, quote: dict[str, Any], market: str, is_benchmark: bool) -> str:
    symbol = quote["symbol"]
    yahoo_symbol = quote.get("source_symbol") or symbol
    currency = quote.get("currency") or ("BRL" if market == "BR" else "USD")
    asset_type = "etf" if is_benchmark and symbol.endswith("11") else "stock"
    if symbol in {"SPY", "VOO", "QQQ", "BOVA11"}:
        asset_type = "etf"
    if symbol.startswith("^"):
        asset_type = "index"

    cur.execute(
        """
        insert into trade.assets(symbol, yahoo_symbol, name, asset_type, market, currency, is_benchmark, metadata)
        values (%s, %s, %s, %s, %s, %s, %s, %s::jsonb)
        on conflict (symbol, market) do update set
          yahoo_symbol = excluded.yahoo_symbol,
          currency = excluded.currency,
          is_benchmark = trade.assets.is_benchmark or excluded.is_benchmark,
          updated_at = now(),
          metadata = trade.assets.metadata || excluded.metadata
        returning id
        """,
        (
            symbol,
            yahoo_symbol,
            symbol,
            asset_type,
            market,
            currency,
            is_benchmark,
            json.dumps({"latest_source": quote.get("source"), "section": "benchmark" if is_benchmark else "watchlist"}),
        ),
    )
    return cur.fetchone()[0]


def get_source_id(cur) -> str:
    cur.execute("select id from trade.data_sources where name = 'yahoo_chart_api'")
    row = cur.fetchone()
    if row:
        return row[0]
    cur.execute(
        """
        insert into trade.data_sources(name, source_type, url, cost_tier, realtime, reliability_score)
        values ('yahoo_chart_api', 'api', 'https://query1.finance.yahoo.com', 'free', false, 0.70)
        returning id
        """
    )
    return cur.fetchone()[0]


def get_feature_set_id(cur) -> str:
    cur.execute("select id from trade.feature_sets where name = 'market_radar_snapshot' and version = '0.1'")
    row = cur.fetchone()
    if row:
        return row[0]
    cur.execute(
        """
        insert into trade.feature_sets(name, version, description, feature_definitions, status)
        values (
          'market_radar_snapshot',
          '0.1',
          'Features generated from the read-only Market Radar quote snapshot.',
          %s::jsonb,
          'research'
        )
        returning id
        """,
        (json.dumps({
            "change_pct": "daily percent change vs previous close",
            "day_range_pct": "(day_high - day_low) / previous_close",
            "volume": "latest reported volume",
        }),),
    )
    return cur.fetchone()[0]


def ingest(payload: dict[str, Any], db_url: str) -> dict[str, int]:
    generated_at = payload.get("generated_at")
    counts = {"assets": 0, "bars": 0, "features": 0}
    with psycopg2.connect(db_url) as conn:
        with conn.cursor() as cur:
            source_id = get_source_id(cur)
            feature_set_id = get_feature_set_id(cur)
            for market, _section, quote, is_benchmark in iter_quotes(payload):
                asset_id = upsert_asset(cur, quote, market, is_benchmark)
                counts["assets"] += 1
                ts = ts_from_quote(quote, generated_at)
                raw = json.dumps(quote)
                cur.execute(
                    """
                    insert into trade.market_bars(
                      asset_id, source_id, timeframe, ts, open, high, low, close,
                      adjusted_close, volume, raw
                    ) values (%s,%s,'1d',%s,%s,%s,%s,%s,%s,%s,%s::jsonb)
                    on conflict (asset_id, source_id, timeframe, ts) do update set
                      open = excluded.open,
                      high = excluded.high,
                      low = excluded.low,
                      close = excluded.close,
                      adjusted_close = excluded.adjusted_close,
                      volume = excluded.volume,
                      raw = excluded.raw
                    """,
                    (
                        asset_id,
                        source_id,
                        ts,
                        quote.get("open"),
                        quote.get("day_high"),
                        quote.get("day_low"),
                        quote.get("regular_market_price"),
                        quote.get("regular_market_price"),
                        quote.get("volume"),
                        raw,
                    ),
                )
                counts["bars"] += 1

                prev = quote.get("previous_close")
                high = quote.get("day_high")
                low = quote.get("day_low")
                day_range_pct = None
                if prev and high is not None and low is not None:
                    day_range_pct = ((float(high) - float(low)) / float(prev)) * 100
                features = {
                    "change_pct": quote.get("change_pct"),
                    "day_range_pct": day_range_pct,
                    "volume": quote.get("volume"),
                    "currency": quote.get("currency"),
                    "source_symbol": quote.get("source_symbol"),
                    "market": market,
                    "is_benchmark": is_benchmark,
                }
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
    cache_path = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_CACHE
    db_url = os.getenv("TRADE_DATABASE_URL", DEFAULT_DB_URL)
    payload = load_json(cache_path)
    if not payload.get("safety", {}).get("read_only"):
        raise SystemExit("Refusing to ingest payload without read_only safety flag.")
    counts = ingest(payload, db_url)
    print("Ingested Market Radar snapshot into Supabase/Postgres:", counts)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
