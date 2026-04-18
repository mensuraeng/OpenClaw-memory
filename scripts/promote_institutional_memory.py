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
CONSOLIDATION = MEMORY / "consolidation"
INSTITUTIONAL = MEMORY / "institutional"
INDEX = MEMORY / "institutional" / "index.json"
AGENTS = ["main", "mensura", "mia", "pcs", "finance"]
MAX_BODY = 500

CATEGORY_HINTS = {
    "decision": ["decisão", "decid", "aprovado", "definido", "fica definido", "regra", "diretriz"],
    "pending": ["pendência", "pendente", "falta", "aguard", "precisa", "bloque", "prazo"],
    "lesson": ["lição", "aprend", "erro", "não repetir", "falha", "correção", "insight"],
    "project": ["obra", "projeto", "cliente", "cronograma", "ccsp", "pcs", "mia", "mensura"],
}
CATEGORY_FILES = {
    "decision": "decisions.md",
    "pending": "pending.md",
    "lesson": "lessons.md",
    "project": "projects.md",
}


def read_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    items = []
    for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            payload = json.loads(line)
            if isinstance(payload, dict):
                items.append(payload)
        except json.JSONDecodeError:
            continue
    return items


def normalize(text: str) -> str:
    text = text.lower()
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def classify(payload: dict) -> str:
    hay = " ".join(
        str(payload.get(k, "")) for k in ("type", "title", "body")
    ).lower()
    for category, hints in CATEGORY_HINTS.items():
        if any(hint in hay for hint in hints):
            return category
    return "project"


def summarize(payload: dict) -> str:
    title = str(payload.get("title") or "Sem título").strip()
    body = str(payload.get("body") or "").strip()
    body = re.sub(r"\s+", " ", body)
    if len(body) > MAX_BODY:
        body = body[: MAX_BODY - 3].rstrip() + "..."
    bits = [f"- [{payload.get('day', '?')}] {title}"]
    if body:
        bits.append(f"  {body}")
    bits.append(
        f"  Fonte: agente={payload.get('agent','?')} | tipo={payload.get('type','?')} | origem={payload.get('source','?')}"
    )
    return "\n".join(bits)


def append_unique(path: Path, entries: list[str]) -> int:
    path.parent.mkdir(parents=True, exist_ok=True)
    existing = path.read_text(encoding="utf-8", errors="ignore") if path.exists() else ""
    existing_norm = normalize(existing)
    new_items = []
    for entry in entries:
        head = normalize(entry.splitlines()[0])
        if head and head in existing_norm:
            continue
        new_items.append(entry)
    if not new_items:
        return 0
    with path.open("a", encoding="utf-8") as f:
        if path.stat().st_size if path.exists() else 0:
            f.write("\n")
        f.write("\n\n".join(new_items).rstrip() + "\n")
    return len(new_items)


def promote_day(day: str) -> int:
    day_dir = INBOX / day
    if not day_dir.exists():
        print(json.dumps({"day": day, "status": "no_inbox"}, ensure_ascii=False))
        return 0

    grouped: dict[str, list[str]] = defaultdict(list)
    counts: dict[str, int] = defaultdict(int)

    for agent in AGENTS:
        events_path = day_dir / agent / "events.jsonl"
        for payload in read_jsonl(events_path):
            payload.setdefault("agent", agent)
            payload.setdefault("day", day)
            category = classify(payload)
            grouped[category].append(summarize(payload))
            counts[category] += 1

    generated_at = datetime.now(UTC).strftime("%Y-%m-%d %H:%M UTC")
    promoted = {}
    for category, entries in grouped.items():
        file_name = CATEGORY_FILES[category]
        dest = INSTITUTIONAL / file_name
        header = ""
        if not dest.exists():
            dest.parent.mkdir(parents=True, exist_ok=True)
            header = f"# {category.title()} institucional\n\n_Gerado inicialmente em {generated_at}_\n\n"
            dest.write_text(header, encoding="utf-8")
        promoted[category] = append_unique(dest, entries)

    index_payload = {
        "lastRunAt": generated_at,
        "lastDay": day,
        "sourceInbox": str(day_dir),
        "counts": counts,
        "promoted": promoted,
    }
    INDEX.parent.mkdir(parents=True, exist_ok=True)
    INDEX.write_text(json.dumps(index_payload, ensure_ascii=False, indent=2), encoding="utf-8")

    summary_path = CONSOLIDATION / day / "promotion-summary.json"
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.write_text(json.dumps(index_payload, ensure_ascii=False, indent=2), encoding="utf-8")

    print(json.dumps({"day": day, "status": "ok", "promoted": promoted, "counts": counts}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    day = sys.argv[1] if len(sys.argv) > 1 else datetime.now().strftime("%Y-%m-%d")
    raise SystemExit(promote_day(day))
