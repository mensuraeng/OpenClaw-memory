#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CAPTURE = ROOT / "scripts" / "capture_event.py"
VALID_AGENTS = {"main", "mensura", "mia", "pcs", "finance"}
IMPORTANT_TYPES = {
    "decision_made",
    "task_completed",
    "task_failed",
    "publication_done",
    "critical_alert",
    "delegation_completed",
    "delegation_failed",
    "email_sent",
}


def capture(agent: str, event_type: str, title: str, body: str, source: str, meta: dict, day: str | None) -> int:
    cmd = [
        sys.executable,
        str(CAPTURE),
        "--agent",
        agent,
        "--type",
        event_type,
        "--title",
        title,
        "--body",
        body,
        "--source",
        source,
        "--meta",
        json.dumps(meta, ensure_ascii=False),
    ]
    if day:
        cmd += ["--day", day]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    if result.stdout:
        print(result.stdout.strip())
    if result.stderr:
        print(result.stderr.strip(), file=sys.stderr)
    return result.returncode


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Capture important OpenClaw events into memory inbox")
    parser.add_argument("--agent", required=True)
    parser.add_argument("--event-type", required=True)
    parser.add_argument("--title", required=True)
    parser.add_argument("--body", default="")
    parser.add_argument("--source", default="openclaw")
    parser.add_argument("--day", default=datetime.now().strftime("%Y-%m-%d"))
    parser.add_argument("--meta", default="{}")
    parser.add_argument("--allow-low-signal", action="store_true")
    args = parser.parse_args()

    if args.agent not in VALID_AGENTS:
        raise SystemExit(f"invalid agent: {args.agent}")

    if not args.allow_low_signal and args.event_type not in IMPORTANT_TYPES:
        print(json.dumps({
            "ok": False,
            "skipped": True,
            "reason": "low_signal",
            "event_type": args.event_type,
        }, ensure_ascii=False))
        raise SystemExit(0)

    try:
        meta = json.loads(args.meta)
        if not isinstance(meta, dict):
            raise ValueError("meta must be object")
    except Exception as exc:
        raise SystemExit(f"invalid --meta: {exc}")

    raise SystemExit(
        capture(
            agent=args.agent,
            event_type=args.event_type,
            title=args.title,
            body=args.body,
            source=args.source,
            meta=meta,
            day=args.day,
        )
    )
