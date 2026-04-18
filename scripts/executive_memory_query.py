#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timedelta, UTC
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INSTITUTIONAL = ROOT / "memory" / "institutional"
INBOX = ROOT / "memory" / "inbox"
LOOPS_PATH = INSTITUTIONAL / "loop-status.json"
FILES = {
    "decisions": INSTITUTIONAL / "decisions.md",
    "pending": INSTITUTIONAL / "pending.md",
    "lessons": INSTITUTIONAL / "lessons.md",
    "projects": INSTITUTIONAL / "projects.md",
}
SPECIAL_QUERIES = {
    "o que mudou hoje": "changed_today",
    "o que mudou na semana": "changed_week",
    "quais decisões continuam abertas": "open_decisions",
    "quais riscos cresceram": "growing_risks",
    "o que continua aberto": "open_loops",
    "o que fechou hoje": "closed_today",
}


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


def extract_matches(text: str, query: str, limit: int) -> list[str]:
    lines = text.splitlines()
    out = []
    q = normalize(query)
    for idx, line in enumerate(lines):
        if q in normalize(line):
            start = max(0, idx - 1)
            end = min(len(lines), idx + 3)
            block = "\n".join(lines[start:end]).strip()
            if block:
                out.append(block)
        if len(out) >= limit:
            break
    return out


def collect_events(days: list[str]) -> list[dict]:
    rows = []
    for day in days:
        day_dir = INBOX / day
        if not day_dir.exists():
            continue
        for events_path in day_dir.glob("*/events.jsonl"):
            rows.extend(read_jsonl(events_path))
    return rows


def summarize_event(row: dict) -> dict:
    return {
        "day": row.get("day"),
        "agent": row.get("agent"),
        "type": row.get("type"),
        "title": row.get("title"),
        "source": row.get("source"),
    }


def query_changed(days_back: int) -> dict:
    today = datetime.now(UTC).date()
    days = [(today - timedelta(days=delta)).strftime("%Y-%m-%d") for delta in range(days_back)]
    rows = collect_events(days)
    by_type: dict[str, list[dict]] = {}
    for row in rows:
        by_type.setdefault(str(row.get("type") or "unknown"), []).append(summarize_event(row))
    return {
        "window": days,
        "total": len(rows),
        "by_type": {k: v[:10] for k, v in sorted(by_type.items(), key=lambda item: len(item[1]), reverse=True)}
    }


def tail_blocks(path: Path) -> list[str]:
    if not path.exists():
        return []
    text = path.read_text(encoding="utf-8", errors="ignore").strip()
    if not text:
        return []
    return [block.strip() for block in re.split(r"\n\s*\n", text) if block.strip() and not block.startswith("#") and not block.startswith("_")]


def query_open_decisions(limit: int) -> dict:
    decisions = tail_blocks(FILES["decisions"])
    pending = tail_blocks(FILES["pending"])
    decision_blocks = decisions[-limit:]
    pending_signals = [block for block in pending if any(token in normalize(block) for token in ["aguard", "pend", "bloque", "precisa", "falta"])]
    return {
        "recent_decisions": decision_blocks,
        "pending_signals": pending_signals[:limit],
    }


def query_growing_risks(limit: int) -> dict:
    risks = []
    pending_blocks = tail_blocks(FILES["pending"])
    if pending_blocks:
        risks.extend(pending_blocks)
    for path in [FILES["projects"], FILES["lessons"]]:
        for block in tail_blocks(path):
            hay = normalize(block)
            if any(token in hay for token in ["risco", "bloque", "falha", "pend", "atras", "sem resposta", "aguard", "critical_alert", "attention"]):
                risks.append(block)
    unique = []
    seen = set()
    for block in risks:
        head = normalize(block.splitlines()[0])
        if head in seen:
            continue
        seen.add(head)
        unique.append(block)
    return {"risks": unique[:limit]}


def read_loops() -> dict:
    if not LOOPS_PATH.exists():
        return {}
    try:
        payload = json.loads(LOOPS_PATH.read_text(encoding="utf-8"))
        return payload if isinstance(payload, dict) else {}
    except json.JSONDecodeError:
        return {}


def query_open_loops(limit: int) -> dict:
    loops = read_loops().get("loops", {})
    items = []
    for loop_key, payload in loops.items():
        current = payload.get("current", {})
        if current.get("status") in {"blocked", "open", "in_progress"}:
            items.append({"loop": loop_key, **current})
    items.sort(key=lambda item: {"blocked": 0, "open": 1, "in_progress": 2}.get(item.get("status"), 9))
    return {"open_loops": items[:limit]}


def query_closed_today(limit: int) -> dict:
    loops = read_loops().get("loops", {})
    today = datetime.now(UTC).strftime("%Y-%m-%d")
    items = []
    for loop_key, payload in loops.items():
        current = payload.get("current", {})
        if current.get("status") == "closed" and str(current.get("day") or "") == today:
            items.append({"loop": loop_key, **current})
    return {"closed_today": items[:limit]}


def run_query(query: str, limit: int) -> dict:
    normalized = normalize(query)
    special = SPECIAL_QUERIES.get(normalized)
    if special == "changed_today":
        return {"query": query, "mode": special, "result": query_changed(1)}
    if special == "changed_week":
        return {"query": query, "mode": special, "result": query_changed(7)}
    if special == "open_decisions":
        return {"query": query, "mode": special, "result": query_open_decisions(limit)}
    if special == "growing_risks":
        return {"query": query, "mode": special, "result": query_growing_risks(limit)}
    if special == "open_loops":
        return {"query": query, "mode": special, "result": query_open_loops(limit)}
    if special == "closed_today":
        return {"query": query, "mode": special, "result": query_closed_today(limit)}

    result = {"query": query, "mode": "search", "hits": {}}
    for name, path in FILES.items():
        if not path.exists():
            continue
        matches = extract_matches(path.read_text(encoding="utf-8", errors="ignore"), query, limit)
        if matches:
            result["hits"][name] = matches
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Executive query over institutional memory")
    parser.add_argument("query")
    parser.add_argument("--limit", type=int, default=5)
    args = parser.parse_args()
    print(json.dumps(run_query(args.query, args.limit), ensure_ascii=False, indent=2))
