#!/usr/bin/env python3
"""Generate a low-cost BR+US market radar snapshot.

Safety: read-only data collection. No trading credentials. No order placement.
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
sys.path.insert(0, str(SRC))

from trade.data.yahoo import fetch_quote  # noqa: E402
from trade.journal.reports import render_market_snapshot, write_report  # noqa: E402


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def collect_market(market_key: str, config: dict) -> dict:
    return {
        "benchmarks": [fetch_quote(symbol, market_key).to_dict() for symbol in config.get("benchmarks", [])],
        "watchlist": [fetch_quote(symbol, market_key).to_dict() for symbol in config.get("watchlist", [])],
    }


def build_notes(snapshot: dict) -> list[str]:
    notes: list[str] = []
    for market_key, label in [("us", "EUA"), ("br", "Brasil")]:
        quotes = snapshot["markets"][market_key].get("benchmarks", []) + snapshot["markets"][market_key].get("watchlist", [])
        ok = [q for q in quotes if q.get("change_pct") is not None]
        errors = [q for q in quotes if q.get("error")]
        if ok:
            top = max(ok, key=lambda q: q["change_pct"])
            bottom = min(ok, key=lambda q: q["change_pct"])
            notes.append(f"- **{label}:** maior alta no universo: `{top['symbol']}` ({top['change_pct']:+.2f}%); maior queda: `{bottom['symbol']}` ({bottom['change_pct']:+.2f}%).")
        if errors:
            notes.append(f"- **{label}:** {len(errors)} ativos retornaram erro de coleta; revisar símbolos/fonte se persistir.")
    return notes or ["- Sem dados suficientes para leitura automática."]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--universe", default=str(ROOT / "config" / "universe.example.json"))
    parser.add_argument("--json", action="store_true", help="print JSON snapshot")
    args = parser.parse_args()

    now = datetime.now(timezone.utc)
    universe = load_json(Path(args.universe))
    snapshot = {
        "generated_at": now.isoformat(),
        "safety": {
            "read_only": True,
            "real_trading_enabled": False,
            "orders_enabled": False,
        },
        "markets": {
            "us": collect_market("us", universe["us"]),
            "br": collect_market("br", universe["br"]),
        },
    }
    snapshot["notes"] = build_notes(snapshot)

    cache_dir = ROOT / "runtime" / "cache"
    cache_dir.mkdir(parents=True, exist_ok=True)
    cache_path = cache_dir / "market-radar-latest.json"
    cache_path.write_text(json.dumps(snapshot, ensure_ascii=False, indent=2), encoding="utf-8")

    markdown = render_market_snapshot(snapshot)
    report_path = write_report(markdown, ROOT / "runtime" / "reports", now)

    if args.json:
        print(json.dumps(snapshot, ensure_ascii=False, indent=2))
    else:
        print(f"snapshot_json={cache_path}")
        print(f"report_md={report_path}")
        print(f"latest_md={ROOT / 'runtime' / 'reports' / 'market-radar-latest.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
