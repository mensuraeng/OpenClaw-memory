#!/usr/bin/env python3
"""Envia cobrança diária CCSP Casa 7 para Victor com base no relatório semanal vigente.

Uso seguro:
  --execute envia email de fato.
  sem --execute faz preview.

A configuração semanal deve ser regenerada após cada relatório de fechamento semanal.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = Path("/root/.openclaw/workspace")
DEFAULT_CONFIG = ROOT / "config" / "cobrancas-victor-current.json"
BRT = timezone(timedelta(hours=-3))


def load_config(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def build_body(cfg: dict, date_key: str, entry: dict) -> str:
    items = "\n".join(f"{i}. {item}" for i, item in enumerate(entry["items"], start=1))
    return f"""Victor, bom dia.

Segue cobrança objetiva da Casa 7 — CCSP para {entry['label']} ({date_key}), conforme {cfg['report_rev']} de {cfg['report_date']}.

{entry['headline']}

Pontos do dia:
{items}

Por favor, responder ainda hoje com:
- status de cada item;
- responsável;
- prazo atualizado;
- fotos/evidências quando aplicável;
- bloqueios externos que precisam ser formalizados.

Observação: esta cobrança é parte da rotina semanal de controle da MIA para proteger prazo, escopo e rastreabilidade da obra.

Abs,
Flávia
Acompanhamento operacional MIA/Mensura
"""


def send_email(cfg: dict, subject: str, body: str) -> subprocess.CompletedProcess:
    email = cfg["email"]
    cmd = [
        "python3",
        str(WORKSPACE / "scripts" / "msgraph_email.py"),
        "send",
        "--account",
        email.get("account", "mia"),
        "--user",
        email["user"],
        "--to",
        email["to"],
        "--subject",
        subject,
        "--body",
        body,
    ]
    for cc in email.get("cc", []):
        cmd.extend(["--cc", cc])
    return subprocess.run(cmd, text=True, capture_output=True, timeout=120)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default=str(DEFAULT_CONFIG))
    parser.add_argument("--date", help="YYYY-MM-DD; default hoje BRT")
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    cfg_path = Path(args.config)
    cfg = load_config(cfg_path)
    date_key = args.date or datetime.now(BRT).strftime("%Y-%m-%d")
    entry = cfg.get("daily", {}).get(date_key)
    if not entry:
        result = {
            "ok": True,
            "sent": False,
            "reason": "no_daily_entry",
            "date": date_key,
            "config": str(cfg_path),
        }
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0

    subject = entry["subject"]
    body = build_body(cfg, date_key, entry)
    out_dir = ROOT / "runtime" / "email-previews"
    out_dir.mkdir(parents=True, exist_ok=True)
    preview_path = out_dir / f"cobranca-victor-{date_key}.txt"
    preview_path.write_text(f"Subject: {subject}\n\n{body}", encoding="utf-8")

    if not args.execute:
        result = {
            "ok": True,
            "sent": False,
            "mode": "preview",
            "date": date_key,
            "subject": subject,
            "preview": str(preview_path),
        }
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0

    cp = send_email(cfg, subject, body)
    log_dir = ROOT / "runtime" / "email-logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    log_path = log_dir / f"cobranca-victor-{date_key}.json"
    result = {
        "ok": cp.returncode == 0,
        "sent": cp.returncode == 0,
        "date": date_key,
        "subject": subject,
        "preview": str(preview_path),
        "stdout": cp.stdout[-2000:],
        "stderr": cp.stderr[-2000:],
        "code": cp.returncode,
    }
    log_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if cp.returncode == 0 else cp.returncode


if __name__ == "__main__":
    raise SystemExit(main())
