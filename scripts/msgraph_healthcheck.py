#!/usr/bin/env python3
"""
Healthcheck operacional das integrações Microsoft Graph.
Verifica token, inbox e calendário das contas configuradas.
"""

import json
import os
import subprocess
import sys
from datetime import datetime

WORKSPACE = os.path.expanduser("~/.openclaw/workspace")
EMAIL_SCRIPT = os.path.join(WORKSPACE, "scripts", "msgraph_email.py")
CALENDAR_SCRIPT = os.path.join(WORKSPACE, "scripts", "msgraph_calendar.py")
FLAVIA_IDENTITY = os.path.join(WORKSPACE, "config", "flavia-identity.json")

CHECKS = [
    {
        "name": "Mensura email",
        "command": ["python3", EMAIL_SCRIPT, "list", "--account", "mensura", "--limit", "1"],
    },
    {
        "name": "Mensura calendário",
        "command": ["python3", CALENDAR_SCRIPT, "list", "--account", "mensura", "--days", "1"],
    },
    {
        "name": "MIA email",
        "command": ["python3", EMAIL_SCRIPT, "list", "--account", "mia", "--limit", "1"],
    },
    {
        "name": "MIA calendário",
        "command": ["python3", CALENDAR_SCRIPT, "list", "--account", "mia", "--days", "1"],
    },
]


def load_flavia_email():
    with open(FLAVIA_IDENTITY, encoding="utf-8") as f:
        data = json.load(f)
    return data["email"]


def run_check(name, command):
    result = subprocess.run(command, capture_output=True, text=True)
    ok = result.returncode == 0
    output = (result.stdout or result.stderr).strip()
    first_line = output.splitlines()[0] if output else "sem saída"
    return {
        "name": name,
        "ok": ok,
        "returncode": result.returncode,
        "summary": first_line,
        "output": output,
    }


flavia_email = load_flavia_email()
CHECKS.append(
    {
        "name": "Flávia email",
        "command": [
            "python3",
            EMAIL_SCRIPT,
            "list",
            "--config",
            os.path.join(WORKSPACE, "config", "ms-graph.json"),
            "--user",
            flavia_email,
            "--limit",
            "1",
        ],
    }
)


results = [run_check(item["name"], item["command"]) for item in CHECKS]
failed = [r for r in results if not r["ok"]]

print(f"Microsoft Graph healthcheck | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print()
for r in results:
    status = "OK" if r["ok"] else "FAIL"
    print(f"[{status}] {r['name']} -> {r['summary']}")

if failed:
    print()
    print("Falhas detalhadas:")
    for r in failed:
        print()
        print(f"--- {r['name']} (exit {r['returncode']}) ---")
        print(r["output"])
    sys.exit(1)

sys.exit(0)
