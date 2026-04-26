#!/usr/bin/env python3
"""trade — CLI interna agent-native do Programa Trade.

Read-only command layer for market radar, gold monitor, news radar checklist,
reports and Supabase readiness. This CLI intentionally has no real-money order
commands.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = Path("/root/.openclaw/workspace")
ENV_FILE = WORKSPACE / "memory/context/trade_supabase.env"

FORBIDDEN_WORDS = {"order", "orders", "buy", "sell", "trade-real", "execute", "broker", "corretora", "ordem", "comprar", "vender"}


def load_env_file(path: Path = ENV_FILE) -> None:
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        os.environ.setdefault(k, v)


def run_python(script: str, *args: str, env: dict[str, str] | None = None) -> int:
    cmd = [sys.executable, str(ROOT / "scripts" / script), *args]
    return subprocess.run(cmd, cwd=ROOT, env=env or os.environ.copy(), check=False).returncode


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def cmd_status(args):
    latest_market = ROOT / "runtime/cache/market-radar-latest.json"
    latest_gold = ROOT / "runtime/cache/gold-monitor-latest.json"
    latest_news = sorted((ROOT / "runtime/cache").glob("news-radar-*-latest.json")) if (ROOT / "runtime/cache").exists() else []
    payload = {
        "project": "Trade",
        "mode": "read_only_mvp",
        "real_money_execution": "blocked",
        "broker_orders": "not_implemented",
        "market_radar_cache": str(latest_market) if latest_market.exists() else None,
        "gold_monitor_cache": str(latest_gold) if latest_gold.exists() else None,
        "news_radar_caches": [str(p) for p in latest_news],
        "supabase_env_file_exists": ENV_FILE.exists(),
    }
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print("Trade status")
        print("- modo: MVP read-only")
        print("- execução real: BLOQUEADA")
        print(f"- Market Radar cache: {'OK' if latest_market.exists() else 'ausente'}")
        print(f"- Gold Monitor cache: {'OK' if latest_gold.exists() else 'ausente'}")
        print(f"- News Radar caches: {len(latest_news)}")
        print(f"- env Supabase local: {'OK' if ENV_FILE.exists() else 'ausente'}")


def cmd_market_radar(args):
    cmd_args = []
    if args.universe:
        cmd_args += ["--universe", args.universe]
    if args.json:
        cmd_args.append("--json")
    return run_python("market_radar.py", *cmd_args)


def cmd_gold_monitor(args):
    cmd_args = []
    if args.config:
        cmd_args += ["--config", args.config]
    if args.db:
        load_env_file()
        cmd_args.append("--db")
    if args.json:
        cmd_args.append("--json")
    return run_python("gold_monitor.py", *cmd_args)


def cmd_news_radar(args):
    cmd_args = [args.mode]
    if args.config:
        cmd_args += ["--config", args.config]
    return run_python("news_radar.py", *cmd_args)


def cmd_supabase_status(args):
    load_env_file()
    return run_python("supabase_status.py")


def cmd_reports(args):
    reports_dir = ROOT / "runtime/reports"
    reports = sorted(reports_dir.glob("*.md"), reverse=True) if reports_dir.exists() else []
    if args.kind:
        reports = [p for p in reports if args.kind in p.name]
    reports = reports[: args.limit]
    if args.json:
        print(json.dumps([{"path": str(p), "name": p.name, "size": p.stat().st_size} for p in reports], ensure_ascii=False, indent=2))
    else:
        for p in reports:
            print(p)


def cmd_show_report(args):
    path = Path(args.path)
    if not path.is_absolute():
        path = ROOT / path
    resolved = path.resolve()
    if ROOT not in resolved.parents and resolved != ROOT:
        raise SystemExit("Refusing to read outside Trade project")
    text = resolved.read_text(encoding="utf-8")
    lines = text.splitlines()
    print("\n".join(lines[: args.lines]))


def cmd_guardrails(args):
    risk = load_json(ROOT / "config/risk.example.json")
    charter = ROOT / "docs/TRADE-CHARTER-v0.1.md"
    payload = {
        "real_money_execution": "blocked",
        "automatic_orders": "blocked",
        "crypto_increase": "blocked_without_explicit_review",
        "leverage_options_short_margin_day_trade": "blocked_in_mvp",
        "risk_config": risk,
        "charter": str(charter),
    }
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print("Guardrails Trade")
        print("- dinheiro real: bloqueado no MVP")
        print("- ordens automáticas: bloqueadas")
        print("- aumento de cripto: bloqueado sem revisão explícita")
        print("- alavancagem/opções/short/margem/day trade real: bloqueados")
        print(f"- risk config: {ROOT / 'config/risk.example.json'}")
        print(f"- charter: {charter}")


def build_parser():
    p = argparse.ArgumentParser(prog="trade", description="CLI interna do Programa Trade — read-only/risk-governed")
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("status", help="Status read-only do Programa Trade")
    s.add_argument("--json", action="store_true")
    s.set_defaults(func=cmd_status)

    s = sub.add_parser("market-radar", help="Executa Market Radar informativo")
    s.add_argument("--universe")
    s.add_argument("--json", action="store_true")
    s.set_defaults(func=cmd_market_radar)

    s = sub.add_parser("gold-monitor", help="Executa Gold Monitor informativo")
    s.add_argument("--config")
    s.add_argument("--db", action="store_true", help="grava snapshot no Supabase; não executa ordens")
    s.add_argument("--json", action="store_true")
    s.set_defaults(func=cmd_gold_monitor)

    s = sub.add_parser("news-radar", help="Gera payload/checklist de News Radar")
    s.add_argument("mode", choices=["pre_market", "lunch", "close", "weekend"])
    s.add_argument("--config")
    s.set_defaults(func=cmd_news_radar)

    s = sub.add_parser("supabase-status", help="Checa env Supabase sem exibir segredos")
    s.set_defaults(func=cmd_supabase_status)

    s = sub.add_parser("reports", help="Lista relatórios runtime")
    s.add_argument("--kind", choices=["market-radar", "gold-monitor"], default=None)
    s.add_argument("--limit", type=int, default=20)
    s.add_argument("--json", action="store_true")
    s.set_defaults(func=cmd_reports)

    s = sub.add_parser("show-report", help="Mostra início de relatório dentro do projeto Trade")
    s.add_argument("path")
    s.add_argument("--lines", type=int, default=80)
    s.set_defaults(func=cmd_show_report)

    s = sub.add_parser("guardrails", help="Exibe travas operacionais do Trade")
    s.add_argument("--json", action="store_true")
    s.set_defaults(func=cmd_guardrails)

    return p


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    if argv and argv[0].lower() in FORBIDDEN_WORDS:
        raise SystemExit("Blocked: Trade CLI has no real-money execution/order command in MVP.")
    args = build_parser().parse_args(argv)
    result = args.func(args)
    if isinstance(result, int):
        raise SystemExit(result)


if __name__ == "__main__":
    main()
