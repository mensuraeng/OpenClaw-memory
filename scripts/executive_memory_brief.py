#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from datetime import datetime, timedelta, UTC
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INSTITUTIONAL = ROOT / "memory" / "institutional"
INBOX = ROOT / "memory" / "inbox"


def tail_blocks(path: Path, limit: int = 5) -> list[str]:
    if not path.exists():
        return []
    text = path.read_text(encoding="utf-8", errors="ignore").strip()
    if not text:
        return []
    blocks = [block.strip() for block in re.split(r"\n\s*\n", text) if block.strip() and not block.startswith("#") and not block.startswith("_")]
    return blocks[-limit:]


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


def week_events(limit: int = 8) -> list[str]:
    today = datetime.now(UTC).date()
    rows = []
    for delta in range(7):
        day = (today - timedelta(days=delta)).strftime("%Y-%m-%d")
        day_dir = INBOX / day
        if not day_dir.exists():
            continue
        for events_path in day_dir.glob("*/events.jsonl"):
            for row in read_jsonl(events_path):
                title = str(row.get("title") or "Sem título").strip()
                rows.append(f"- [{row.get('day','?')}] {title} ({row.get('type','?')} / {row.get('agent','?')})")
    return rows[-limit:]


def main() -> int:
    decisions = tail_blocks(INSTITUTIONAL / "decisions.md", 3)
    pending = tail_blocks(INSTITUTIONAL / "pending.md", 5)
    lessons = tail_blocks(INSTITUTIONAL / "lessons.md", 3)
    projects = tail_blocks(INSTITUTIONAL / "projects.md", 5)
    recent = week_events(8)

    lines = ["MEMÓRIA EXECUTIVA", ""]
    lines.append("O QUE MUDOU NA SEMANA")
    lines.extend(recent or ["- sem mudanças capturadas"]) 
    lines.append("")
    lines.append("DECISÕES RECENTES")
    lines.extend(decisions or ["- sem decisões registradas"]) 
    lines.append("")
    lines.append("PENDÊNCIAS RELEVANTES")
    lines.extend(pending or ["- sem pendências registradas"]) 
    lines.append("")
    lines.append("LIÇÕES")
    lines.extend(lessons or ["- sem lições registradas"]) 
    lines.append("")
    lines.append("MOVIMENTOS / PROJETOS")
    lines.extend(projects or ["- sem movimentos registrados"]) 

    print("\n".join(lines).strip())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
