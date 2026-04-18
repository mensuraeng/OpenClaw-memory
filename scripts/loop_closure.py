#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from collections import defaultdict
from datetime import datetime, UTC
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
MEMORY = ROOT / "memory"
INBOX = MEMORY / "inbox"
INSTITUTIONAL = MEMORY / "institutional"
LOOPS_PATH = INSTITUTIONAL / "loop-status.json"
REPORT_PATH = INSTITUTIONAL / "loop-status.md"
AGENTS = ["main", "mensura", "mia", "pcs", "finance"]

STATUS_BY_TYPE = {
    "critical_alert": "blocked",
    "task_failed": "blocked",
    "delegation_failed": "blocked",
    "pending": "open",
    "project_update": "in_progress",
    "task_completed": "closed",
    "delegation_completed": "closed",
    "publication_done": "closed",
    "decision_made": "noted",
}

INFORMATIVE_STATUSES = {"noted", "unknown"}
OPERATIONAL_STATUSES = {"blocked", "open", "in_progress", "closed"}

FAMILY_PATTERNS = [
    (r"^openclaw memory \| ", "program:openclaw-memory"),
    (r"^mission control \| ", "program:mission-control"),
]

STATUS_PRIORITY = {
    "blocked": 5,
    "open": 4,
    "in_progress": 3,
    "closed": 2,
    "noted": 1,
    "unknown": 0,
}

REOPEN_TRIGGERS = {"blocked", "open"}
CLOSE_TRIGGERS = {"closed"}
PROGRESS_TRIGGERS = {"in_progress"}


def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower()).strip()


def read_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    rows = []
    for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            payload = json.loads(line)
            if isinstance(payload, dict):
                rows.append(payload)
        except json.JSONDecodeError:
            continue
    return rows


def infer_status(payload: dict) -> str:
    meta = payload.get("meta") or {}
    meta_status = str(meta.get("status") or "").strip().lower()
    if meta_status in {"blocked", "open", "in_progress", "closed", "noted", "waiting_input", "attention", "failed", "running", "completed_validated", "completed_unvalidated"}:
        if meta_status in {"waiting_input", "attention", "failed"}:
            return "blocked"
        if meta_status in {"running"}:
            return "in_progress"
        if meta_status in {"completed_validated", "completed_unvalidated"}:
            return "closed"
        return meta_status
    return STATUS_BY_TYPE.get(str(payload.get("type") or ""), "unknown")


def infer_family(payload: dict) -> str | None:
    meta = payload.get("meta") or {}
    for key in ["family", "program", "project"]:
        value = meta.get(key)
        if value:
            return str(value)
    title_norm = normalize(str(payload.get("title") or ""))
    for pattern, family in FAMILY_PATTERNS:
        if re.search(pattern, title_norm):
            return family
    return None


def infer_loop_key(payload: dict) -> str:
    meta = payload.get("meta") or {}
    for key in ["taskId", "threadId", "entityId", "projectId"]:
        value = meta.get(key)
        if value:
            return f"{key}:{value}"

    family = infer_family(payload)
    title = str(payload.get("title") or "")
    title_norm = normalize(title)
    patterns = [
        r"mission control \| [^|]+ \| ([a-z0-9\-]{8,})",
        r"mission control \| status [^|]+ \| (.+)$",
    ]
    for pattern in patterns:
        match = re.search(pattern, title_norm)
        if match:
            base = match.group(1).strip()
            return f"{family}:{base}" if family else f"title:{base}"

    compact = re.sub(r"[^a-z0-9à-ÿ ]", " ", title_norm)
    compact = re.sub(r"\s+", " ", compact).strip()
    if family:
        return family
    return f"title:{compact[:120]}"


def summarize(payload: dict) -> dict:
    meta = payload.get("meta") or {}
    return {
        "timestamp": payload.get("timestamp"),
        "day": payload.get("day"),
        "agent": payload.get("agent"),
        "type": payload.get("type"),
        "title": payload.get("title"),
        "source": payload.get("source"),
        "status": infer_status(payload),
        "owner": meta.get("owner") or meta.get("agentId") or payload.get("agent"),
        "nextStep": meta.get("nextStep"),
        "family": infer_family(payload),
    }


def collect_events(day: str | None = None) -> list[dict]:
    rows = []
    if day:
        days = [day]
    else:
        days = sorted([path.name for path in INBOX.iterdir() if path.is_dir()]) if INBOX.exists() else []
    for day_name in days:
        day_dir = INBOX / day_name
        for agent in AGENTS:
            rows.extend(read_jsonl(day_dir / agent / "events.jsonl"))
    return rows


def choose_current(existing: dict | None, candidate: dict) -> dict:
    if not existing:
        return candidate

    existing_status = existing.get("status") or "unknown"
    candidate_status = candidate.get("status") or "unknown"
    existing_ts = str(existing.get("timestamp") or "")
    candidate_ts = str(candidate.get("timestamp") or "")

    if existing_status in OPERATIONAL_STATUSES and candidate_status in INFORMATIVE_STATUSES:
        return existing if existing_ts >= candidate_ts or True else candidate
    if existing_status in INFORMATIVE_STATUSES and candidate_status in OPERATIONAL_STATUSES:
        return candidate

    if candidate_status in CLOSE_TRIGGERS and existing_status in {"blocked", "open", "in_progress"}:
        return candidate
    if existing_status == "closed" and candidate_status in REOPEN_TRIGGERS:
        return candidate
    if existing_status == "closed" and candidate_status in PROGRESS_TRIGGERS:
        return candidate
    if existing_status in REOPEN_TRIGGERS and candidate_status in PROGRESS_TRIGGERS:
        return candidate

    if candidate_ts >= existing_ts:
        if existing_status == "unknown" and candidate_status != "unknown":
            return candidate
        if existing_status == candidate_status:
            return candidate

    if STATUS_PRIORITY.get(candidate_status, 0) > STATUS_PRIORITY.get(existing_status, 0):
        return candidate
    if STATUS_PRIORITY.get(candidate_status, 0) == STATUS_PRIORITY.get(existing_status, 0):
        if candidate_ts >= existing_ts:
            return candidate
    return existing


def run(day: str | None = None) -> int:
    events = collect_events(day)
    grouped: dict[str, dict] = {}
    histories: dict[str, list[dict]] = defaultdict(list)

    for payload in events:
        loop_key = infer_loop_key(payload)
        item = summarize(payload)
        histories[loop_key].append(item)
        grouped[loop_key] = choose_current(grouped.get(loop_key), item)

    output = {
        "generatedAt": datetime.now(UTC).strftime("%Y-%m-%d %H:%M UTC"),
        "dayScope": day or "all",
        "totalLoops": len(grouped),
        "statusCounts": defaultdict(int),
        "loops": {},
    }

    for loop_key, current in grouped.items():
        output["statusCounts"][current.get("status") or "unknown"] += 1
        history = sorted(histories[loop_key], key=lambda item: str(item.get("timestamp") or ""))
        transitions = []
        last_status = None
        last_operational_status = None
        for item in history:
            status = item.get("status") or "unknown"
            if status in OPERATIONAL_STATUSES:
                if status != last_operational_status:
                    transitions.append({
                        "timestamp": item.get("timestamp"),
                        "from": last_operational_status,
                        "to": status,
                        "title": item.get("title"),
                        "kind": "operational",
                    })
                    last_operational_status = status
            elif status != last_status and last_operational_status is None:
                transitions.append({
                    "timestamp": item.get("timestamp"),
                    "from": last_status,
                    "to": status,
                    "title": item.get("title"),
                    "kind": "informative",
                })
            last_status = status
        output["loops"][loop_key] = {
            "current": current,
            "history": history,
            "transitions": transitions,
        }

    output["statusCounts"] = dict(output["statusCounts"])
    LOOPS_PATH.parent.mkdir(parents=True, exist_ok=True)
    LOOPS_PATH.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        "# Loop status institucional",
        "",
        f"_Gerado em {output['generatedAt']}_",
        "",
        f"- escopo: {output['dayScope']}",
        f"- total de loops: {output['totalLoops']}",
        f"- contagem por status: {json.dumps(output['statusCounts'], ensure_ascii=False)}",
        "",
        "## Loops ativos",
        "",
    ]
    active = []
    closed = []
    for loop_key, payload in output["loops"].items():
        current = payload["current"]
        transitions = payload.get("transitions") or []
        last_transition = transitions[-1] if transitions else None
        suffix = f" | última transição={last_transition.get('from') or '∅'}→{last_transition.get('to')}" if last_transition else ""
        line = f"- {loop_key} | status={current.get('status')} | título={current.get('title')} | owner={current.get('owner') or '?'}{suffix}"
        if current.get("status") in {"blocked", "open", "in_progress"}:
            active.append(line)
        else:
            closed.append(line)
    lines.extend(active or ["- sem loops ativos identificados"])
    lines.append("")
    lines.append("## Loops fechados / anotados")
    lines.append("")
    lines.extend(closed[:20] or ["- nenhum loop fechado identificado"])
    REPORT_PATH.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")

    print(json.dumps({
        "ok": True,
        "loops": len(grouped),
        "statusCounts": output["statusCounts"],
        "report": str(REPORT_PATH),
    }, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    day = sys.argv[1] if len(sys.argv) > 1 else None
    raise SystemExit(run(day))
