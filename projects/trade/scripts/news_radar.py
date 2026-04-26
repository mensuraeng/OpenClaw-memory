#!/usr/bin/env python3
"""Trade News Radar skeleton.

The full curated search is performed by the OpenClaw agent at cron time because
it can use web search and judgment. This script stores config and renders the
expected checklist/prompt for each run.
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=["pre_market", "lunch", "close", "weekend"])
    parser.add_argument("--config", default=str(ROOT / "config" / "news_radar.example.json"))
    args = parser.parse_args()
    cfg = json.loads(Path(args.config).read_text(encoding="utf-8"))
    payload = {
        "generated_at": datetime.now().isoformat(),
        "mode": args.mode,
        "destination": cfg["destination"],
        "queries": cfg["queries"],
        "guardrails": cfg["guardrails"],
        "instruction": "Use OpenClaw web_search/firecrawl as needed; summarize only market-relevant facts for Trade; no orders; send to Investimento/Notícias only if target/thread configured."
    }
    out = ROOT / "runtime" / "cache" / f"news-radar-{args.mode}-latest.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(out)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
