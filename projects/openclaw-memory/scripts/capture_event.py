#!/usr/bin/env python3
from __future__ import annotations
import json
from datetime import datetime, UTC
from pathlib import Path
import argparse

ROOT = Path(__file__).resolve().parents[1]
INBOX = ROOT / "memory" / "inbox"
VALID_AGENTS = {"main", "mensura", "mia", "pcs", "finance"}


def ensure_day(day: str, agent: str) -> Path:
    base = INBOX / day / agent
    base.mkdir(parents=True, exist_ok=True)
    notes = base / "notes.md"
    events = base / "events.jsonl"
    if not notes.exists():
        notes.write_text("# Inbox Notes\n\n", encoding="utf-8")
    if not events.exists():
        events.write_text("", encoding="utf-8")
    return base


def append_note(notes_path: Path, title: str, body: str, timestamp: str) -> None:
    with notes_path.open("a", encoding="utf-8") as f:
        f.write(f"\n## {timestamp} — {title}\n\n{body.strip()}\n")


def append_event(events_path: Path, payload: dict) -> None:
    with events_path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(payload, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Capture an OpenClaw Memory event")
    parser.add_argument("--agent", required=True)
    parser.add_argument("--type", required=True)
    parser.add_argument("--title", required=True)
    parser.add_argument("--body", default="")
    parser.add_argument("--day", default=datetime.now().strftime("%Y-%m-%d"))
    parser.add_argument("--source", default="manual")
    parser.add_argument("--meta", default="{}", help="JSON object string")
    args = parser.parse_args()

    if args.agent not in VALID_AGENTS:
        raise SystemExit(f"invalid agent: {args.agent}")

    try:
        meta = json.loads(args.meta)
        if not isinstance(meta, dict):
            raise ValueError("meta must be a JSON object")
    except Exception as exc:
        raise SystemExit(f"invalid --meta: {exc}")

    base = ensure_day(args.day, args.agent)
    ts = datetime.now(UTC).strftime("%Y-%m-%d %H:%M UTC")
    event = {
        "timestamp": ts,
        "day": args.day,
        "agent": args.agent,
        "type": args.type,
        "title": args.title,
        "body": args.body,
        "source": args.source,
        "meta": meta,
    }
    append_event(base / "events.jsonl", event)
    if args.body.strip():
        append_note(base / "notes.md", args.title, args.body, ts)
    print(json.dumps({"ok": True, "path": str(base), "event_type": args.type, "agent": args.agent}, ensure_ascii=False))
