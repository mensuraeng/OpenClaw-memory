#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INSTITUTIONAL = ROOT / "memory" / "institutional"
FILES = {
    "decisions": INSTITUTIONAL / "decisions.md",
    "pending": INSTITUTIONAL / "pending.md",
    "lessons": INSTITUTIONAL / "lessons.md",
    "projects": INSTITUTIONAL / "projects.md",
}


def extract_matches(text: str, query: str, limit: int) -> list[str]:
    lines = text.splitlines()
    out = []
    q = query.lower().strip()
    for idx, line in enumerate(lines):
        if q in line.lower():
            start = max(0, idx - 1)
            end = min(len(lines), idx + 2)
            block = "\n".join(lines[start:end]).strip()
            if block:
                out.append(block)
        if len(out) >= limit:
            break
    return out


def run_query(query: str, limit: int) -> dict:
    result = {"query": query, "hits": {}}
    for name, path in FILES.items():
        if not path.exists():
            continue
        matches = extract_matches(path.read_text(encoding="utf-8", errors="ignore"), query, limit)
        if matches:
            result["hits"][name] = matches
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Simple executive query over institutional memory")
    parser.add_argument("query")
    parser.add_argument("--limit", type=int, default=5)
    args = parser.parse_args()
    print(json.dumps(run_query(args.query, args.limit), ensure_ascii=False, indent=2))
