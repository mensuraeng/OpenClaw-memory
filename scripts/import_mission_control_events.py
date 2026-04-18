#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT.parents[1]
TASK_EVENTS = WORKSPACE / "projects" / "mission-control" / "runtime" / "tasks" / "task-events.jsonl"
CAPTURE = ROOT / "scripts" / "capture_openclaw_event.py"
STATE = ROOT / "runtime" / "mission-control-import-state.json"
EVENT_MAP = {
    "validated": "task_completed",
    "completed_unvalidated": "task_completed",
    "failed": "task_failed",
    "escalated": "critical_alert",
    "blocked": "critical_alert",
    "waiting_input": "critical_alert",
    "retry_started": "task_failed",
}


def load_state() -> dict:
    if not STATE.exists():
        return {}
    try:
        return json.loads(STATE.read_text(encoding="utf-8"))
    except Exception:
        return {}


def save_state(data: dict) -> None:
    STATE.parent.mkdir(parents=True, exist_ok=True)
    STATE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def read_events() -> list[dict]:
    if not TASK_EVENTS.exists():
        return []
    rows = []
    for line in TASK_EVENTS.read_text(encoding="utf-8", errors="ignore").splitlines():
        if not line.strip():
            continue
        try:
            payload = json.loads(line)
            if isinstance(payload, dict):
                rows.append(payload)
        except json.JSONDecodeError:
            continue
    return rows


def capture(event_type: str, title: str, body: str, meta: dict, day: str) -> int:
    cmd = [
        sys.executable,
        str(CAPTURE),
        "--agent",
        "main",
        "--event-type",
        event_type,
        "--title",
        title,
        "--body",
        body,
        "--source",
        "mission-control",
        "--day",
        day,
        "--meta",
        json.dumps(meta, ensure_ascii=False),
    ]
    return subprocess.run(cmd, capture_output=True, text=True, timeout=60).returncode


def main() -> int:
    state = load_state()
    last_id = state.get("lastEventId")
    rows = read_events()
    started = last_id is None
    imported = 0
    newest = last_id

    for row in rows:
        event_id = row.get("eventId")
        if not started:
            if event_id == last_id:
                started = True
            continue
        if event_id == last_id:
            continue
        mapped = EVENT_MAP.get(str(row.get("type") or ""))
        if not mapped:
            newest = event_id or newest
            continue
        timestamp = str(row.get("timestamp") or "")
        day = timestamp[:10] if len(timestamp) >= 10 else "1970-01-01"
        title = f"Mission Control | {row.get('type')} | {row.get('taskId')}"
        body = str(row.get("message") or "").strip()
        meta = {
            "taskId": row.get("taskId"),
            "agentId": row.get("agentId"),
            "sourceType": row.get("type"),
        }
        rc = capture(mapped, title, body, meta, day)
        if rc == 0:
            imported += 1
        newest = event_id or newest

    if newest:
        save_state({"lastEventId": newest, "importedAt": rows[-1].get("timestamp") if rows else None})

    print(json.dumps({"ok": True, "imported": imported, "lastEventId": newest}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
