#!/usr/bin/env python3
"""Build the initial historical base for Trade Predictive Lab.

Sources currently supported:
- Yahoo Chart API historical OHLCV for configured BR/US universe.
- Local runtime reports as journal entries (optional).

Safety:
- read-only public/file data only;
- writes analytics/journal tables only when --db is passed;
- no broker credentials, no orders, no execution.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
sys.path.insert(0, str(SRC))
sys.path.insert(0, str(ROOT / "scripts"))

from trade.data.yahoo import fetch_history  # noqa: E402
from validate_ingestion_payload import validate_envelope  # noqa: E402

try:  # Optional: only needed with --db
    import psycopg2  # type: ignore
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


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def stable_id(*parts: Any) -> str:
    material = "|".join(str(p) for p in parts)
    return hashlib.sha256(material.encode("utf-8")).hexdigest()[:32]


def iter_universe(universe: dict[str, Any]) -> Iterable[tuple[str, str, bool]]:
    for market_key, market in [("us", "US"), ("br", "BR")]:
        cfg = universe.get(market_key, {})
        for symbol in cfg.get("benchmarks", []) or []:
            yield market, symbol, True
        for symbol in cfg.get("watchlist", []) or []:
            yield market, symbol, False


def asset_type_for(symbol: str, is_benchmark: bool) -> str:
    if symbol.startswith("^") or symbol in {"DXY"}:
        return "index"
    if is_benchmark or symbol.endswith("11") or symbol in {"SPY", "VOO", "QQQ", "IVV"}:
        return "etf"
    return "stock"


def market_snapshot_envelope(market: str, symbol: str, is_benchmark: bool, bars: list[dict[str, Any]], range_: str, interval: str) -> dict[str, Any]:
    generated_at = datetime.now(timezone.utc).isoformat()
    assets: list[dict[str, Any]] = []
    previous_close: float | None = None
    for bar in bars:
        close = bar.get("close")
        change_pct = None
        day_range_pct = None
        if previous_close not in (None, 0) and close is not None:
            change_pct = (float(close) / float(previous_close) - 1.0) * 100.0
        high = bar.get("high")
        low = bar.get("low")
        if previous_close not in (None, 0) and high is not None and low is not None:
            day_range_pct = ((float(high) - float(low)) / float(previous_close)) * 100.0
        previous_close = float(close) if close is not None else previous_close
        assets.append(
            {
                "symbol": symbol,
                "source_symbol": bar.get("source_symbol") or symbol,
                "name": symbol,
                "asset_type": asset_type_for(symbol, is_benchmark),
                "currency": bar.get("currency") or ("BRL" if market == "BR" else "USD"),
                "exchange": None,
                "is_benchmark": is_benchmark,
                "ts": bar["ts"],
                "open": bar.get("open"),
                "high": high,
                "low": low,
                "close": close,
                "adjusted_close": bar.get("adjusted_close"),
                "volume": bar.get("volume"),
                "features": {
                    "change_pct": change_pct,
                    "day_range_pct": day_range_pct,
                    "source_symbol": bar.get("source_symbol") or symbol,
                    "market": market,
                    "is_benchmark": is_benchmark,
                    "history_range": range_,
                },
                "raw": bar,
            }
        )
    return {
        "schema_version": "trade.ingestion.v0.1",
        "event_id": stable_id("market_history", market, symbol, range_, interval, len(assets), assets[-1]["ts"] if assets else "empty"),
        "generated_at": generated_at,
        "source": {
            "name": "yahoo_chart_api",
            "type": "api",
            "url": "https://query1.finance.yahoo.com/v8/finance/chart",
            "reliability_score": 0.70,
        },
        "safety": {
            "read_only": True,
            "execution_allowed": False,
            "real_money": False,
            "broker_connected": False,
        },
        "payload_type": "market_snapshot",
        "payload": {
            "market": market,
            "timeframe": interval,
            "assets": assets,
        },
    }


def journal_envelope(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    stat = path.stat()
    created_at = datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc).isoformat()
    return {
        "schema_version": "trade.ingestion.v0.1",
        "event_id": stable_id("runtime_report", path.name, stat.st_size, int(stat.st_mtime)),
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source": {"name": "local_runtime_report", "type": "file", "url": str(path.relative_to(ROOT)), "reliability_score": 0.80},
        "safety": {"read_only": True, "execution_allowed": False, "real_money": False, "broker_connected": False},
        "payload_type": "journal_entry",
        "payload": {
            "entry_type": "daily_report" if "weekly" not in path.name else "weekly_report",
            "title": path.stem,
            "body": text,
            "tags": ["runtime_report", path.name.split("-")[0]],
            "created_at": created_at,
            "metadata": {"path": str(path.relative_to(ROOT)), "size": stat.st_size},
        },
    }


def get_source_id(cur, source: dict[str, Any]) -> str:
    cur.execute("select id from trade.data_sources where name = %s", (source["name"],))
    row = cur.fetchone()
    if row:
        return row[0]
    cur.execute(
        """
        insert into trade.data_sources(name, source_type, url, cost_tier, realtime, reliability_score, metadata)
        values (%s, %s, %s, 'free', false, %s, '{}'::jsonb)
        returning id
        """,
        (source["name"], source["type"], source.get("url"), source.get("reliability_score")),
    )
    return cur.fetchone()[0]


def get_feature_set_id(cur) -> str:
    cur.execute("select id from trade.feature_sets where name = 'predictive_base_ohlcv' and version = '0.1'")
    row = cur.fetchone()
    if row:
        return row[0]
    cur.execute(
        """
        insert into trade.feature_sets(name, version, description, feature_definitions, status)
        values ('predictive_base_ohlcv', '0.1', 'Initial OHLCV-derived predictive base features.', %s::jsonb, 'research')
        returning id
        """,
        (json.dumps({"change_pct": "daily return pct", "day_range_pct": "intraday range vs previous close", "history_range": "Yahoo historical range used"}),),
    )
    return cur.fetchone()[0]


def upsert_asset(cur, item: dict[str, Any], market: str) -> str:
    cur.execute(
        """
        insert into trade.assets(symbol, yahoo_symbol, name, asset_type, market, currency, exchange, is_benchmark, metadata)
        values (%s,%s,%s,%s,%s,%s,%s,%s,%s::jsonb)
        on conflict (symbol, market) do update set
          yahoo_symbol = excluded.yahoo_symbol,
          name = coalesce(trade.assets.name, excluded.name),
          currency = excluded.currency,
          exchange = coalesce(trade.assets.exchange, excluded.exchange),
          is_benchmark = trade.assets.is_benchmark or excluded.is_benchmark,
          updated_at = now(),
          metadata = trade.assets.metadata || excluded.metadata
        returning id
        """,
        (
            item["symbol"],
            item.get("source_symbol") or item["symbol"],
            item.get("name") or item["symbol"],
            item.get("asset_type") or "stock",
            market,
            item.get("currency") or ("BRL" if market == "BR" else "USD"),
            item.get("exchange"),
            bool(item.get("is_benchmark")),
            json.dumps({"predictive_base": True}),
        ),
    )
    return cur.fetchone()[0]


def ingest_market_snapshot(cur, envelope: dict[str, Any]) -> dict[str, int]:
    source_id = get_source_id(cur, envelope["source"])
    feature_set_id = get_feature_set_id(cur)
    payload = envelope["payload"]
    market = payload["market"]
    timeframe = payload["timeframe"]
    counts = {"assets": 0, "bars": 0, "features": 0}
    for item in payload["assets"]:
        asset_id = upsert_asset(cur, item, market)
        counts["assets"] += 1
        cur.execute(
            """
            insert into trade.market_bars(asset_id, source_id, timeframe, ts, open, high, low, close, adjusted_close, volume, raw)
            values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s::jsonb)
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
                timeframe,
                item["ts"],
                item.get("open"),
                item.get("high"),
                item.get("low"),
                item["close"],
                item.get("adjusted_close"),
                item.get("volume"),
                json.dumps(item.get("raw") or item),
            ),
        )
        counts["bars"] += 1
        cur.execute(
            """
            insert into trade.asset_features(asset_id, feature_set_id, timeframe, ts, features)
            values (%s,%s,%s,%s,%s::jsonb)
            on conflict (asset_id, feature_set_id, timeframe, ts) do update set
              features = excluded.features
            """,
            (asset_id, feature_set_id, timeframe, item["ts"], json.dumps(item.get("features") or {})),
        )
        counts["features"] += 1
    return counts


def ingest_journal(cur, envelope: dict[str, Any]) -> dict[str, int]:
    payload = envelope["payload"]
    cur.execute(
        """
        insert into trade.journal_entries(entry_type, title, body, tags, metadata, created_at)
        values (%s,%s,%s,%s,%s::jsonb,%s)
        on conflict do nothing
        """,
        (
            payload.get("entry_type", "daily_report"),
            payload["title"],
            payload["body"],
            payload.get("tags") or [],
            json.dumps(payload.get("metadata") or {}),
            payload.get("created_at") or envelope["generated_at"],
        ),
    )
    return {"journal_entries": 1}


def ingest_envelopes_db(envelopes: list[dict[str, Any]], db_url: str) -> dict[str, int]:
    if psycopg2 is None:
        raise RuntimeError("psycopg2 is required for --db")
    totals: dict[str, int] = {}
    with psycopg2.connect(db_url) as conn:
        with conn.cursor() as cur:
            for envelope in envelopes:
                if envelope["payload_type"] == "market_snapshot":
                    counts = ingest_market_snapshot(cur, envelope)
                elif envelope["payload_type"] == "journal_entry":
                    counts = ingest_journal(cur, envelope)
                else:
                    counts = {}
                for key, value in counts.items():
                    totals[key] = totals.get(key, 0) + value
    return totals


def write_jsonl(path: Path, envelopes: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(json.dumps(e, ensure_ascii=False, sort_keys=True) for e in envelopes) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Build Trade predictive base from historical/public/local sources")
    parser.add_argument("--universe", default=str(ROOT / "config" / "universe.example.json"))
    parser.add_argument("--range", default="5y", dest="range_", help="Yahoo range, e.g. 1y, 2y, 5y, 10y, max")
    parser.add_argument("--interval", default="1d", help="Yahoo interval, e.g. 1d, 1wk, 1mo")
    parser.add_argument("--symbols", nargs="*", help="Optional subset of symbols from universe")
    parser.add_argument("--include-runtime-reports", action="store_true")
    parser.add_argument("--db", action="store_true", help="Write validated envelopes into Supabase/Postgres")
    parser.add_argument("--output", default=str(ROOT / "runtime" / "datasets" / "predictive-base-latest.jsonl"))
    args = parser.parse_args()

    universe = load_json(Path(args.universe))
    selected = set(args.symbols or [])
    envelopes: list[dict[str, Any]] = []
    errors: list[dict[str, str]] = []

    for market, symbol, is_benchmark in iter_universe(universe):
        if selected and symbol not in selected:
            continue
        try:
            bars = [bar.to_dict() for bar in fetch_history(symbol, market.lower(), args.range_, args.interval)]
            if not bars:
                errors.append({"symbol": symbol, "error": "no bars returned"})
                continue
            envelope = market_snapshot_envelope(market, symbol, is_benchmark, bars, args.range_, args.interval)
            validate_envelope(envelope)
            envelopes.append(envelope)
        except Exception as exc:  # noqa: BLE001 - continue building rest of base
            errors.append({"symbol": symbol, "error": repr(exc)})

    if args.include_runtime_reports:
        for path in sorted((ROOT / "runtime" / "reports").glob("*.md")):
            envelope = journal_envelope(path)
            validate_envelope(envelope)
            envelopes.append(envelope)

    output = Path(args.output)
    write_jsonl(output, envelopes)

    db_counts: dict[str, int] = {}
    if args.db:
        load_env_file()
        db_counts = ingest_envelopes_db(envelopes, os.getenv("TRADE_DATABASE_URL", DEFAULT_DB_URL))

    summary = {
        "output": str(output),
        "envelopes": len(envelopes),
        "errors": errors,
        "db_counts": db_counts,
        "safety": {"read_only": True, "execution_allowed": False, "real_money": False},
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0 if envelopes else 1


if __name__ == "__main__":
    raise SystemExit(main())
