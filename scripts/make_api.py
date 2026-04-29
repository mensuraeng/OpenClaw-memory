#!/usr/bin/env python3
"""Small guarded Make.com API helper for OpenClaw.

Loads credentials from /root/.secrets/make.env by default.
Read operations are allowed directly. Running a scenario is an external side effect
and therefore requires --yes plus normal human approval in OpenClaw workflows.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ENV_PATH = Path(os.environ.get("MAKE_ENV", "/root/.secrets/make.env"))


def load_env(path: Path = ENV_PATH) -> dict[str, str]:
    if not path.exists():
        raise SystemExit(f"missing env file: {path}")
    values: dict[str, str] = {}
    for raw in path.read_text().splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip().strip('"').strip("'")
    for key in ("MAKE_API_KEY", "MAKE_ZONE", "MAKE_TEAM_ID"):
        if not values.get(key):
            raise SystemExit(f"missing {key} in {path}")
    return values


def request(method: str, path: str, *, query: dict | None = None, body: dict | None = None) -> dict:
    env = load_env()
    base = f"https://{env['MAKE_ZONE']}/api/v2"
    url = base + path
    if query:
        url += "?" + urllib.parse.urlencode(query, doseq=True)
    data = None
    headers = {
        "Authorization": "Token " + env["MAKE_API_KEY"],
        "Accept": "application/json",
        "User-Agent": "OpenClaw/1.0 (+https://docs.openclaw.ai)",
    }
    if body is not None:
        data = json.dumps(body).encode()
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            text = response.read().decode()
            return json.loads(text) if text else {"ok": True}
    except urllib.error.HTTPError as error:
        detail = error.read().decode(errors="ignore")[:1000]
        raise SystemExit(f"Make API error HTTP {error.code}: {detail}") from error


def cmd_list(args: argparse.Namespace) -> None:
    env = load_env()
    data = request(
        "GET",
        "/scenarios",
        query={
            "teamId": env["MAKE_TEAM_ID"],
            "pg[limit]": str(args.limit),
            "cols[]": ["id", "name", "isActive", "isPaused", "lastEdit", "nextExec"],
        },
    )
    rows = data.get("scenarios") or data.get("data") or []
    print(json.dumps(rows, ensure_ascii=False, indent=2))


def cmd_run(args: argparse.Namespace) -> None:
    if not args.yes:
        raise SystemExit("refusing to run scenario without --yes; this is an external side effect")
    body = json.loads(args.data) if args.data else None
    data = request("POST", f"/scenarios/{args.scenario_id}/run", body=body)
    print(json.dumps(data, ensure_ascii=False, indent=2))


def main() -> None:
    parser = argparse.ArgumentParser(description="Guarded Make.com API helper")
    sub = parser.add_subparsers(dest="cmd", required=True)
    p_list = sub.add_parser("list", help="List scenarios for configured team")
    p_list.add_argument("--limit", type=int, default=20)
    p_list.set_defaults(func=cmd_list)
    p_run = sub.add_parser("run", help="Run a scenario by ID; external side effect")
    p_run.add_argument("scenario_id")
    p_run.add_argument("--data", help="JSON body with scenario input data")
    p_run.add_argument("--yes", action="store_true", help="Confirm external side effect")
    p_run.set_defaults(func=cmd_run)
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
