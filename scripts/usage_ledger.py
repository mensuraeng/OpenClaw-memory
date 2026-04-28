#!/usr/bin/env python3
"""Registra uso/custo operacional em JSONL.

Exemplo:
python3 scripts/usage_ledger.py --agent main --domain infra --operation health_check --tool operational_health --status ok --evidence runtime/operational-health/latest.json
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

OUT = Path('/root/.openclaw/workspace/runtime/usage-ledger/usage-ledger.jsonl')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--agent', required=True)
    ap.add_argument('--domain', required=True)
    ap.add_argument('--operation', required=True)
    ap.add_argument('--tool', required=True)
    ap.add_argument('--entity', default='')
    ap.add_argument('--input-units', type=float, default=None)
    ap.add_argument('--output-units', type=float, default=None)
    ap.add_argument('--credits', type=float, default=None)
    ap.add_argument('--estimated-cost-usd', type=float, default=None)
    ap.add_argument('--status', choices=['ok', 'fail', 'skipped'], required=True)
    ap.add_argument('--evidence', default='')
    ap.add_argument('--notes', default='')
    args = ap.parse_args()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    row = {
        'ts': datetime.now(timezone.utc).isoformat(),
        'agent': args.agent,
        'domain': args.domain,
        'operation': args.operation,
        'tool': args.tool,
        'entity': args.entity,
        'input_units': args.input_units,
        'output_units': args.output_units,
        'credits': args.credits,
        'estimated_cost_usd': args.estimated_cost_usd,
        'status': args.status,
        'evidence': args.evidence,
        'notes': args.notes,
    }
    with OUT.open('a', encoding='utf-8') as f:
        f.write(json.dumps(row, ensure_ascii=False) + '\n')
    print(json.dumps(row, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
