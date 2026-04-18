#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT.parents[1]
MISSION_CONTROL = WORKSPACE / "projects" / "mission-control"
TASK_EVENTS = MISSION_CONTROL / "runtime" / "tasks" / "task-events.jsonl"
TASK_EXECUTIONS = MISSION_CONTROL / "runtime" / "tasks" / "task-executions.jsonl"
RECONCILE_SUMMARY = MISSION_CONTROL / "scripts" / "reconcile-summary-example.json"
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
    "sla_breached": "critical_alert",
    "stale_detected": "critical_alert",
    "orphan_detected": "critical_alert",
    "auto_closed": "task_completed",
}
STATUS_MAP = {
    "blocked": "critical_alert",
    "waiting_input": "critical_alert",
    "failed": "task_failed",
    "completed_unvalidated": "task_completed",
    "completed_validated": "task_completed",
    "running": "project_update",
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


def read_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    rows = []
    for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        if not line.strip():
            continue
        try:
            payload = json.loads(line)
            if isinstance(payload, dict):
                rows.append(payload)
        except json.JSONDecodeError:
            continue
    return rows


def read_events() -> list[dict]:
    return read_jsonl(TASK_EVENTS)


def read_task_executions() -> list[dict]:
    return read_jsonl(TASK_EXECUTIONS)


def read_reconcile_summary() -> dict:
    if not RECONCILE_SUMMARY.exists():
        return {}
    try:
        payload = json.loads(RECONCILE_SUMMARY.read_text(encoding="utf-8"))
        return payload if isinstance(payload, dict) else {}
    except json.JSONDecodeError:
        return {}


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
    executions = read_task_executions()
    reconcile = read_reconcile_summary()
    started = last_id is None
    imported = 0
    newest = last_id
    imported_statuses = 0
    imported_summary = 0

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
            "status": row.get("payload", {}).get("status") if isinstance(row.get("payload"), dict) else None,
        }
        rc = capture(mapped, title, body, meta, day)
        if rc == 0:
            imported += 1
        newest = event_id or newest

    for task in executions:
        status = str(task.get("status") or "")
        mapped = STATUS_MAP.get(status)
        if not mapped:
            continue
        timestamp = str(task.get("updatedAt") or task.get("createdAt") or "")
        day = timestamp[:10] if len(timestamp) >= 10 else "1970-01-01"
        task_id = str(task.get("taskId") or "unknown")
        signature = f"status::{task_id}::{status}::{timestamp}"
        if state.get("seenTaskStatuses") and signature in state.get("seenTaskStatuses", []):
            continue
        title = f"Mission Control | status {status} | {task.get('title') or task_id}"
        body = str(task.get("objective") or task.get("failureReason") or task.get("blockingReason") or "").strip()
        meta = {
            "taskId": task.get("taskId"),
            "agentId": task.get("targetAgent") or task.get("sourceAgent"),
            "status": status,
            "owner": task.get("targetAgent"),
            "nextStep": task.get("expectedOutput"),
            "sourceType": "task_execution",
        }
        rc = capture(mapped, title, body, meta, day)
        if rc == 0:
            imported_statuses += 1
            state.setdefault("seenTaskStatuses", []).append(signature)

    if reconcile:
        summary_sig = json.dumps(reconcile.get("summary", {}), ensure_ascii=False, sort_keys=True)
        if summary_sig and summary_sig != state.get("lastReconcileSummary"):
            title = "Mission Control | resumo executivo de reconciliação"
            body = json.dumps(reconcile.get("summary", {}), ensure_ascii=False)
            meta = {"sourceType": "reconcile_summary", "status": "attention"}
            rc = capture("critical_alert", title, body, meta, "2026-04-18")
            if rc == 0:
                imported_summary += 1
                state["lastReconcileSummary"] = summary_sig

    if newest:
        state["lastEventId"] = newest
        state["importedAt"] = rows[-1].get("timestamp") if rows else None
    save_state(state)

    print(json.dumps({
        "ok": True,
        "imported_events": imported,
        "imported_statuses": imported_statuses,
        "imported_summary": imported_summary,
        "lastEventId": newest,
    }, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
