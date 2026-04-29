#!/usr/bin/env python3
"""Pack operational context for LLM input without changing canonical data.

Principle: JSON/Markdown remain source of truth; this script only creates compact,
read-only context packs for prompts, subagents, and Mission Control analysis.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
from collections.abc import Iterable
from pathlib import Path
from typing import Any

DEFAULT_KEYS = [
    "id",
    "name",
    "title",
    "status",
    "enabled",
    "isActive",
    "isPaused",
    "risk",
    "priority",
    "owner",
    "next_step",
    "nextRun",
    "lastRun",
    "lastEdit",
    "evidence",
    "detail",
    "path",
]

MODE_KEYS: dict[str, list[str]] = {
    "summary": ["id", "name", "title", "status", "priority", "risk", "next_step", "owner", "evidence"],
    "agent": ["id", "name", "title", "status", "priority", "risk", "next_step", "evidence", "detail"],
    "audit": ["id", "name", "title", "status", "risk", "detail", "evidence", "path"],
    "table": DEFAULT_KEYS,
}


def read_text(path: str | None) -> str:
    if not path or path == "-":
        return sys.stdin.read()
    return Path(path).read_text(encoding="utf-8", errors="replace")


def load_input(path: str | None, input_format: str) -> Any:
    text = read_text(path)
    if input_format == "auto":
        suffix = Path(path).suffix.lower() if path and path != "-" else ""
        if suffix == ".csv":
            input_format = "csv"
        elif suffix in {".json", ".jsonl"}:
            input_format = suffix[1:]
        else:
            stripped = text.lstrip()
            input_format = "json" if stripped.startswith(("{", "[")) else "text"
    if input_format == "json":
        return json.loads(text)
    if input_format == "jsonl":
        return [json.loads(line) for line in text.splitlines() if line.strip()]
    if input_format == "csv":
        return list(csv.DictReader(text.splitlines()))
    return text


def flatten_records(data: Any) -> list[dict[str, Any]]:
    if isinstance(data, list):
        return [x if isinstance(x, dict) else {"value": x} for x in data]
    if isinstance(data, dict):
        for key in ("items", "jobs", "tasks", "projects", "checks", "scenarios", "data", "results"):
            value = data.get(key)
            if isinstance(value, list):
                return [x if isinstance(x, dict) else {"value": x} for x in value]
        return [data]
    return [{"text": str(data)}]


def get_nested(record: dict[str, Any], key: str) -> Any:
    cur: Any = record
    for part in key.split("."):
        if not isinstance(cur, dict) or part not in cur:
            return None
        cur = cur[part]
    return cur


def compact_value(value: Any, max_len: int = 220) -> Any:
    if value is None:
        return None
    if isinstance(value, (bool, int, float)):
        return value
    if isinstance(value, str):
        clean = " ".join(value.split())
        return clean if len(clean) <= max_len else clean[: max_len - 1] + "…"
    if isinstance(value, list):
        if len(value) <= 3 and all(not isinstance(x, (dict, list)) for x in value):
            return value
        return f"[{len(value)} items]"
    if isinstance(value, dict):
        return "{" + ",".join(list(value.keys())[:8]) + "}"
    return str(value)


def project_record(record: dict[str, Any], keys: list[str]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for key in keys:
        value = get_nested(record, key)
        compacted = compact_value(value)
        if compacted not in (None, ""):
            out[key.replace(".", "_")] = compacted
    if not out:
        for key, value in list(record.items())[:8]:
            compacted = compact_value(value)
            if compacted not in (None, ""):
                out[key] = compacted
    return out


def estimate_tokens(text: str) -> int:
    # Conservative operational estimate: enough for before/after comparisons without tokenizer deps.
    return max(1, round(len(text) / 4))


def sha12(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()[:12]


def to_csv(records: list[dict[str, Any]]) -> str:
    if not records:
        return ""
    fields: list[str] = []
    for record in records:
        for key in record.keys():
            if key not in fields:
                fields.append(key)
    lines = []
    from io import StringIO

    buf = StringIO()
    writer = csv.DictWriter(buf, fieldnames=fields, lineterminator="\n")
    writer.writeheader()
    writer.writerows(records)
    return buf.getvalue().rstrip("\n")


def build_pack(args: argparse.Namespace) -> tuple[str, dict[str, Any]]:
    raw_text = read_text(args.input)
    data = load_input(args.input, args.input_format)
    records = flatten_records(data)
    keys = args.keys.split(",") if args.keys else MODE_KEYS.get(args.mode, DEFAULT_KEYS)
    projected = [project_record(r, keys) for r in records]
    if args.limit:
        projected = projected[: args.limit]

    if args.output == "json":
        body = json.dumps(projected, ensure_ascii=False, separators=(",", ":"))
    elif args.output == "jsonl":
        body = "\n".join(json.dumps(r, ensure_ascii=False, separators=(",", ":")) for r in projected)
    elif args.output == "csv":
        body = to_csv(projected)
    elif args.output == "markdown":
        lines = [f"# Context pack — {args.mode}", ""]
        for idx, record in enumerate(projected, start=1):
            fields = "; ".join(f"{k}: {v}" for k, v in record.items())
            lines.append(f"{idx}. {fields}")
        body = "\n".join(lines)
    else:
        body = str(projected)

    meta = {
        "mode": args.mode,
        "input": args.input or "stdin",
        "records_in": len(records),
        "records_out": len(projected),
        "format": args.output,
        "source_sha12": sha12(raw_text),
        "input_chars": len(raw_text),
        "output_chars": len(body),
        "estimated_tokens_in": estimate_tokens(raw_text),
        "estimated_tokens_out": estimate_tokens(body),
    }
    if meta["estimated_tokens_in"]:
        meta["estimated_token_reduction_pct"] = round(
            (1 - meta["estimated_tokens_out"] / meta["estimated_tokens_in"]) * 100, 1
        )
    return body, meta


def main() -> None:
    parser = argparse.ArgumentParser(description="Create compact read-only context packs for LLM prompts")
    parser.add_argument("input", nargs="?", help="Input file; defaults to stdin")
    parser.add_argument("--input-format", choices=["auto", "json", "jsonl", "csv", "text"], default="auto")
    parser.add_argument("--mode", choices=["summary", "agent", "audit", "table"], default="summary")
    parser.add_argument("--output", choices=["json", "jsonl", "csv", "markdown"], default="json")
    parser.add_argument("--keys", help="Comma-separated keys to keep; supports dotted paths")
    parser.add_argument("--limit", type=int, default=0, help="Max records to include")
    parser.add_argument("--meta", action="store_true", help="Write metadata to stderr")
    args = parser.parse_args()
    body, meta = build_pack(args)
    if args.meta:
        print(json.dumps(meta, ensure_ascii=False, separators=(",", ":")), file=sys.stderr)
    print(body)


if __name__ == "__main__":
    main()
