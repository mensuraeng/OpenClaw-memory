#!/usr/bin/env python3
"""Validate Trade ingestion envelopes before DB writes.

The validator is intentionally dependency-light. It enforces the MVP safety
contract and the minimum fields needed to build an auditable predictive base.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ALLOWED_PAYLOAD_TYPES = {
    "market_snapshot",
    "macro_event",
    "news_item",
    "thesis",
    "signal",
    "forecast",
    "risk_event",
    "journal_entry",
    "strategy_run",
    "simulated_trade",
}

QUALITATIVE_TYPES = {"news_item", "thesis", "signal", "forecast", "journal_entry"}
RISK_REQUIRED_TYPES = {"thesis", "signal", "simulated_trade"}


class ValidationError(Exception):
    pass


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ValidationError(message)


def _path_get(obj: dict[str, Any], path: str) -> Any:
    cur: Any = obj
    for part in path.split("."):
        if not isinstance(cur, dict) or part not in cur:
            return None
        cur = cur[part]
    return cur


def validate_envelope(envelope: dict[str, Any]) -> None:
    _require(isinstance(envelope, dict), "envelope must be a JSON object")
    _require(envelope.get("schema_version") == "trade.ingestion.v0.1", "schema_version must be trade.ingestion.v0.1")
    _require(bool(envelope.get("event_id")), "event_id is required")
    _require(bool(envelope.get("generated_at")), "generated_at is required")

    source = envelope.get("source")
    _require(isinstance(source, dict), "source object is required")
    _require(bool(source.get("name")), "source.name is required")
    _require(source.get("type") in {"api", "scrape", "manual", "file", "computed"}, "source.type is invalid")

    safety = envelope.get("safety")
    _require(isinstance(safety, dict), "safety object is required")
    _require(safety.get("read_only") is True, "safety.read_only must be true")
    _require(safety.get("execution_allowed") is False, "safety.execution_allowed must be false in MVP")
    _require(safety.get("real_money") is False, "safety.real_money must be false in MVP")
    _require(safety.get("broker_connected") is False, "safety.broker_connected must be false in MVP")

    payload_type = envelope.get("payload_type")
    _require(payload_type in ALLOWED_PAYLOAD_TYPES, f"payload_type is invalid: {payload_type!r}")
    payload = envelope.get("payload")
    _require(isinstance(payload, dict), "payload object is required")

    if payload_type == "market_snapshot":
        _require(payload.get("market") in {"US", "BR", "GLOBAL", "OTHER"}, "market_snapshot.payload.market is invalid")
        _require(bool(payload.get("timeframe")), "market_snapshot.payload.timeframe is required")
        assets = payload.get("assets")
        _require(isinstance(assets, list) and len(assets) > 0, "market_snapshot.payload.assets must be a non-empty list")
        for idx, asset in enumerate(assets):
            _require(bool(asset.get("symbol")), f"market_snapshot.assets[{idx}].symbol is required")
            _require(asset.get("close") is not None, f"market_snapshot.assets[{idx}].close is required")
            _require(bool(asset.get("ts")), f"market_snapshot.assets[{idx}].ts is required")

    if payload_type == "forecast":
        for field in ["model.name", "model.version", "asset", "as_of_ts", "horizon", "target"]:
            _require(_path_get(payload, field) is not None, f"forecast.payload.{field} is required")
        has_probability = payload.get("probability_up") is not None or payload.get("expected_return") is not None
        _require(has_probability, "forecast requires probability_up or expected_return")

    if payload_type in QUALITATIVE_TYPES:
        has_sources = bool(_path_get(payload, "thesis.data_sources")) or bool(_path_get(payload, "explanation.sources")) or bool(source.get("url")) or source.get("type") in {"manual", "file", "computed"}
        _require(has_sources, f"{payload_type} requires source attribution")

    if payload_type in RISK_REQUIRED_TYPES:
        has_risk = bool(payload.get("risk")) or bool(_path_get(payload, "thesis.risk"))
        has_invalidation = bool(payload.get("invalidation")) or bool(_path_get(payload, "thesis.invalidation"))
        _require(has_risk, f"{payload_type} requires risk")
        _require(has_invalidation, f"{payload_type} requires invalidation")


def iter_json_inputs(path: Path):
    text = path.read_text(encoding="utf-8")
    if path.suffix == ".jsonl":
        for line_no, line in enumerate(text.splitlines(), start=1):
            if line.strip():
                yield line_no, json.loads(line)
    else:
        data = json.loads(text)
        if isinstance(data, list):
            for idx, item in enumerate(data, start=1):
                yield idx, item
        else:
            yield 1, data


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate Trade ingestion payload/envelope JSON or JSONL")
    parser.add_argument("path")
    parser.add_argument("--quiet", action="store_true")
    args = parser.parse_args()

    path = Path(args.path)
    count = 0
    try:
        for line_no, envelope in iter_json_inputs(path):
            validate_envelope(envelope)
            count += 1
    except Exception as exc:  # noqa: BLE001 - CLI returns readable validation error
        print(f"INVALID {path}:{line_no if 'line_no' in locals() else '?'}: {exc}", file=sys.stderr)
        return 1

    if not args.quiet:
        print(f"VALID {path}: {count} envelope(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
