#!/usr/bin/env python3
"""Gold monitor for Trade Wealth Monitor.

Read-only. No broker, no orders. Tracks gold plus macro context:
DXY, US 10Y, USD/BRL, silver and S&P 500.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import psycopg2

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
sys.path.insert(0, str(SRC))
from trade.data.yahoo import fetch_quote  # noqa: E402

DEFAULT_DB_URL = "postgresql://postgres:postgres@127.0.0.1:54322/postgres"


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def collect(entries: list[dict[str, str]]) -> list[dict[str, Any]]:
    out = []
    for item in entries:
        q = fetch_quote(item["symbol"], "us").to_dict()
        q["label"] = item.get("label", item["symbol"])
        out.append(q)
    return out


def build_notes(snapshot: dict[str, Any]) -> list[str]:
    thresholds = snapshot["thresholds"]
    notes: list[str] = []
    quotes = {q["symbol"]: q for q in snapshot["primary"] + snapshot["context"] if q.get("change_pct") is not None}
    gold = quotes.get("GC=F") or quotes.get("GLD")
    silver = quotes.get("SI=F") or quotes.get("SLV")
    dxy = quotes.get("DX-Y.NYB")
    us10y = quotes.get("^TNX")
    usdbrl = quotes.get("USDBRL=X")

    if gold:
        g = gold["change_pct"]
        notes.append(f"Ouro referência `{gold['symbol']}`: {g:+.2f}% no dia.")
        if abs(g) >= thresholds["gold_daily_abs_change_pct"]:
            notes.append(f"ALERTA: movimento diário do ouro acima do gatilho ({g:+.2f}%).")
    if silver and abs(silver["change_pct"]) >= thresholds["silver_daily_abs_change_pct"]:
        notes.append(f"Prata com movimento relevante: `{silver['symbol']}` {silver['change_pct']:+.2f}%.")
    if dxy and abs(dxy["change_pct"]) >= thresholds["usd_daily_abs_change_pct"]:
        notes.append(f"DXY moveu {dxy['change_pct']:+.2f}%; checar impacto sobre ouro.")
    if us10y and abs(us10y["change_pct"]) >= thresholds["us10y_daily_abs_change_pct"]:
        notes.append(f"US10Y moveu {us10y['change_pct']:+.2f}%; juros reais podem afetar ouro.")
    if usdbrl and abs(usdbrl["change_pct"]) >= thresholds["usd_daily_abs_change_pct"]:
        notes.append(f"USD/BRL moveu {usdbrl['change_pct']:+.2f}%; impacto em exposição local a ouro.")
    if gold and dxy and gold["change_pct"] > thresholds["gold_context_divergence_pct"] and dxy["change_pct"] > 0:
        notes.append("Divergência: ouro subindo junto com dólar forte; possível busca por proteção/risco geopolítico.")
    return notes or ["Sem gatilho material no monitor de ouro."]


def render(snapshot: dict[str, Any]) -> str:
    lines = ["# Gold Monitor — Trade", "", f"Gerado em: `{snapshot['generated_at']}`", "", "## Ouro", ""]
    for q in snapshot["primary"]:
        if q.get("error"):
            lines.append(f"- `{q['symbol']}` — erro: {q['error']}")
        else:
            lines.append(f"- `{q['symbol']}` {q.get('label','')}: {q.get('regular_market_price')} {q.get('currency') or ''} ({q.get('change_pct'):+.2f}%)")
    lines += ["", "## Contexto", ""]
    for q in snapshot["context"]:
        if q.get("error"):
            lines.append(f"- `{q['symbol']}` — erro: {q['error']}")
        else:
            ch = q.get('change_pct')
            lines.append(f"- `{q['symbol']}` {q.get('label','')}: {q.get('regular_market_price')} {q.get('currency') or ''} ({ch:+.2f}%)")
    lines += ["", "## Notas", ""] + [f"- {n}" for n in snapshot["notes"]]
    lines += ["", "_Monitor read-only. Sem recomendação automática de compra/venda._", ""]
    return "\n".join(lines)


def upsert_asset(cur, symbol: str, name: str, asset_type: str, market: str, currency: str | None):
    cur.execute(
        """
        insert into trade.assets(symbol, yahoo_symbol, name, asset_type, market, currency, is_benchmark, metadata)
        values (%s,%s,%s,%s,%s,%s,false,%s::jsonb)
        on conflict (symbol, market) do update set
          yahoo_symbol=excluded.yahoo_symbol, name=excluded.name, currency=excluded.currency, updated_at=now(), metadata=trade.assets.metadata || excluded.metadata
        returning id
        """,
        (symbol, symbol, name, asset_type, market, currency or "USD", json.dumps({"gold_monitor": True})),
    )
    return cur.fetchone()[0]


def source_id(cur):
    cur.execute("select id from trade.data_sources where name='yahoo_chart_api'")
    row = cur.fetchone()
    return row[0]


def save_db(snapshot: dict[str, Any], db_url: str):
    with psycopg2.connect(db_url) as conn, conn.cursor() as cur:
        sid = source_id(cur)
        for section, asset_type in (("primary", "commodity"), ("context", "other")):
            for q in snapshot[section]:
                if q.get("error") or q.get("regular_market_price") is None:
                    continue
                market = "GLOBAL" if q["symbol"] in {"GC=F", "SI=F", "DX-Y.NYB", "USDBRL=X"} else "US"
                aid = upsert_asset(cur, q["symbol"], q.get("label") or q["symbol"], asset_type, market, q.get("currency"))
                ts = datetime.fromtimestamp(int(q.get("market_time") or datetime.now(timezone.utc).timestamp()), tz=timezone.utc)
                cur.execute(
                    """
                    insert into trade.market_bars(asset_id, source_id, timeframe, ts, open, high, low, close, adjusted_close, volume, raw)
                    values (%s,%s,'1d',%s,%s,%s,%s,%s,%s,%s,%s::jsonb)
                    on conflict (asset_id, source_id, timeframe, ts) do update set
                      open=excluded.open, high=excluded.high, low=excluded.low, close=excluded.close,
                      adjusted_close=excluded.adjusted_close, volume=excluded.volume, raw=excluded.raw
                    """,
                    (aid, sid, ts, q.get("open"), q.get("day_high"), q.get("day_low"), q.get("regular_market_price"), q.get("regular_market_price"), q.get("volume"), json.dumps(q)),
                )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default=str(ROOT / "config" / "gold_monitor.example.json"))
    parser.add_argument("--db", action="store_true", help="write snapshot to Supabase/Postgres")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    cfg = load_json(Path(args.config))
    now = datetime.now(timezone.utc)
    snapshot = {
        "generated_at": now.isoformat(),
        "safety": cfg["safety"],
        "thresholds": cfg["alert_thresholds"],
        "primary": collect(cfg["primary"]),
        "context": collect(cfg["context"]),
    }
    snapshot["notes"] = build_notes(snapshot)

    cache_dir = ROOT / "runtime" / "cache"
    report_dir = ROOT / "runtime" / "reports"
    cache_dir.mkdir(parents=True, exist_ok=True)
    report_dir.mkdir(parents=True, exist_ok=True)
    (cache_dir / "gold-monitor-latest.json").write_text(json.dumps(snapshot, ensure_ascii=False, indent=2), encoding="utf-8")
    md = render(snapshot)
    (report_dir / "gold-monitor-latest.md").write_text(md, encoding="utf-8")
    (report_dir / f"gold-monitor-{now.strftime('%Y%m%d-%H%M%S')}.md").write_text(md, encoding="utf-8")

    if args.db:
        save_db(snapshot, os.getenv("TRADE_DATABASE_URL", DEFAULT_DB_URL))
    if args.json:
        print(json.dumps(snapshot, ensure_ascii=False, indent=2))
    else:
        print("snapshot_json=runtime/cache/gold-monitor-latest.json")
        print("report_md=runtime/reports/gold-monitor-latest.md")
        for n in snapshot["notes"]:
            print(f"note={n}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
