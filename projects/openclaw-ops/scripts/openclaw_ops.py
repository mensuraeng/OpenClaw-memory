#!/usr/bin/env python3
"""openclaw-ops — CLI operacional read-only para saúde da operação OpenClaw.

v0.1: diagnóstico seguro. Não reinicia serviços, não altera config, não remove arquivos,
não envia mensagens e não executa update.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

WORKSPACE = Path('/root/.openclaw/workspace')
PROJECT = Path(__file__).resolve().parents[1]
BACKUPS = Path('/root/openclaw-backups')
LOGS = Path('/root/.openclaw/logs')

BLOCKED = {
    'restart', 'stop', 'start', 'update', 'upgrade', 'delete', 'remove', 'rm', 'prune',
    'cleanup-run', 'clean-run', 'send', 'message', 'config-apply', 'config-patch',
    'gateway-restart', 'restore', 'rollback', 'kill'
}


def run(cmd: list[str], timeout: int = 20) -> dict[str, Any]:
    if not shutil.which(cmd[0]):
        return {'ok': False, 'cmd': cmd, 'error': f'command not found: {cmd[0]}'}
    try:
        cp = subprocess.run(cmd, text=True, capture_output=True, timeout=timeout)
        return {'ok': cp.returncode == 0, 'cmd': cmd, 'code': cp.returncode, 'stdout': cp.stdout[-12000:], 'stderr': cp.stderr[-4000:]}
    except subprocess.TimeoutExpired as e:
        return {'ok': False, 'cmd': cmd, 'error': f'timeout after {timeout}s', 'stdout': (e.stdout or '')[-4000:] if isinstance(e.stdout, str) else '', 'stderr': (e.stderr or '')[-4000:] if isinstance(e.stderr, str) else ''}
    except Exception as e:
        return {'ok': False, 'cmd': cmd, 'error': str(e)}


def disk_summary() -> dict[str, Any]:
    usage = shutil.disk_usage('/')
    return {
        'total_gb': round(usage.total / 1024**3, 2),
        'used_gb': round(usage.used / 1024**3, 2),
        'free_gb': round(usage.free / 1024**3, 2),
        'used_pct': round(usage.used / usage.total * 100, 1),
    }


def backup_summary() -> dict[str, Any]:
    files = []
    if BACKUPS.exists():
        for p in BACKUPS.glob('*.tar.gz'):
            try:
                st = p.stat()
                files.append({'path': str(p), 'size_gb': round(st.st_size / 1024**3, 2), 'mtime': datetime.fromtimestamp(st.st_mtime).isoformat(timespec='seconds')})
            except FileNotFoundError:
                pass
    files.sort(key=lambda x: x['mtime'], reverse=True)
    tmp_count = len(list(BACKUPS.glob('*.tmp'))) if BACKUPS.exists() else 0
    return {'dir': str(BACKUPS), 'count': len(files), 'tmp_count': tmp_count, 'latest': files[:5], 'total_gb': round(sum(f['size_gb'] for f in files), 2)}


def git_summary() -> list[dict[str, Any]]:
    repos = [WORKSPACE, Path('/root/2nd-brain'), WORKSPACE / 'finance', WORKSPACE / 'projects/trade', WORKSPACE / 'projects/mensura-schedule-control']
    out = []
    for r in repos:
        if not (r / '.git').exists():
            continue
        st = run(['git', '-C', str(r), 'status', '--short'], timeout=10)
        head = run(['git', '-C', str(r), 'log', '-1', '--oneline'], timeout=10)
        out.append({'repo': str(r), 'dirty_lines': len([l for l in st.get('stdout','').splitlines() if l.strip()]), 'head': head.get('stdout','').strip(), 'status_ok': st['ok']})
    return out


def parse_doctor(text: str) -> dict[str, Any]:
    lower = text.lower()
    return {
        'has_error': any(k in lower for k in [' error', 'failed', '❌']),
        'has_warning': any(k in lower for k in [' warning', 'warn', '⚠️']),
        'summary': text[-4000:],
    }


def cmd_status(args):
    payload = {
        'mode': 'read_only_v0.1',
        'time': datetime.now().isoformat(timespec='seconds'),
        'workspace': str(WORKSPACE),
        'disk': disk_summary(),
        'backups': backup_summary(),
        'git': git_summary(),
        'guardrails': 'no restart/update/delete/send/cleanup execution',
    }
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print('openclaw-ops status')
        print('- modo: read-only')
        print(f"- disco: {payload['disk']['free_gb']} GB livres ({payload['disk']['used_pct']}% usado)")
        print(f"- backups: {payload['backups']['count']} tar.gz, {payload['backups']['tmp_count']} tmp, {payload['backups']['total_gb']} GB")
        for r in payload['git']:
            dirty = 'limpo' if r['dirty_lines'] == 0 else f"{r['dirty_lines']} alterações"
            print(f"- git {r['repo']}: {dirty} · {r['head']}")


def cmd_health(args):
    checks = {
        'openclaw_status': run(['openclaw', 'status'], timeout=args.timeout),
        'openclaw_doctor': run(['openclaw', 'doctor', '--non-interactive'], timeout=args.timeout),
        'disk': {'ok': disk_summary()['free_gb'] >= args.min_free_gb, 'data': disk_summary()},
        'backups': {'ok': True, 'data': backup_summary()},
    }
    if checks['openclaw_doctor'].get('stdout'):
        checks['openclaw_doctor']['parsed'] = parse_doctor(checks['openclaw_doctor']['stdout'])
    ok = all(v.get('ok', False) if isinstance(v, dict) and 'ok' in v else True for v in checks.values())
    payload = {'ok': ok, 'checks': checks}
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(f"health_ok={ok}")
        for name, chk in checks.items():
            print(f"{name}\t{chk.get('ok')}")
            if not chk.get('ok') and chk.get('error'):
                print(f"  error: {chk['error']}")
            if name == 'disk':
                d = chk['data']; print(f"  disk: {d['free_gb']} GB livres, {d['used_pct']}% usado")


def cmd_crons(args):
    # The tool API is canonical for cron mutation/listing. CLI v0.1 provides a local diagnostic wrapper
    # around OpenClaw status/known logs, without editing jobs.
    logs = []
    for root in [WORKSPACE / 'logs/cron', LOGS]:
        if root.exists():
            for p in sorted(root.glob('*'), key=lambda x: x.stat().st_mtime if x.exists() else 0, reverse=True)[:args.limit]:
                if p.is_file():
                    logs.append({'path': str(p), 'size_kb': round(p.stat().st_size/1024,1), 'mtime': datetime.fromtimestamp(p.stat().st_mtime).isoformat(timespec='seconds')})
    payload = {
        'mode': 'read_only',
        'note': 'Use OpenClaw cron tool for authoritative job list; this command inventories local cron logs only in v0.1.',
        'logs': logs,
    }
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(payload['note'])
        for l in logs:
            print(f"{l['mtime']}\t{l['size_kb']} KB\t{l['path']}")


def cmd_cost(args):
    candidates = [WORKSPACE / 'reports', WORKSPACE / 'projects/mission-control/data', LOGS]
    found = []
    for root in candidates:
        if not root.exists(): continue
        for p in root.rglob('*'):
            if p.is_file() and any(k in p.name.lower() for k in ['cost','usage','token']):
                try:
                    found.append({'path': str(p), 'size_kb': round(p.stat().st_size/1024,1), 'mtime': datetime.fromtimestamp(p.stat().st_mtime).isoformat(timespec='seconds')})
                except FileNotFoundError: pass
    found.sort(key=lambda x:x['mtime'], reverse=True)
    payload={'mode':'read_only','files':found[:args.limit],'note':'Inventário de arquivos de custo/usage; não recalcula nem altera orçamento.'}
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(payload['note'])
        for f in payload['files']:
            print(f"{f['mtime']}\t{f['size_kb']} KB\t{f['path']}")


def cmd_backup(args):
    payload = backup_summary()
    payload['mode'] = 'read_only'
    payload['note'] = 'Não executa backup/restauração. Use comando aprovado separado para mutação.'
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(payload['note'])
        print(f"backups={payload['count']} tmp={payload['tmp_count']} total_gb={payload['total_gb']}")
        for f in payload['latest']:
            print(f"{f['mtime']}\t{f['size_gb']} GB\t{f['path']}")


def cmd_cleanup(args):
    targets = [
        Path('/root/.cache/pip'), Path('/root/.cache/whisper'), Path('/root/.cache/ms-playwright'),
        Path('/root/.cache/huggingface'), Path('/root/.cache/node-gyp')
    ]
    rows=[]
    for t in targets:
        if not t.exists():
            rows.append({'path': str(t), 'exists': False, 'size_mb': 0}); continue
        total=0
        for p in t.rglob('*'):
            try:
                if p.is_file(): total += p.stat().st_size
            except Exception: pass
        rows.append({'path': str(t), 'exists': True, 'size_mb': round(total/1024**2,1)})
    pycache_count=sum(1 for _ in WORKSPACE.rglob('__pycache__')) if WORKSPACE.exists() else 0
    payload={'mode':'dry_run_only','cache_targets':rows,'pycache_dirs_under_workspace':pycache_count,'note':'Diagnóstico apenas; não remove nada.'}
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(payload['note'])
        for r in rows: print(f"{r['size_mb']} MB\t{r['path']}")
        print(f"pycache_dirs_under_workspace={pycache_count}")


def cmd_guardrails(args):
    payload = {
        'mode':'read_only_v0.1',
        'blocked': sorted(BLOCKED),
        'allowed': ['status','health','crons logs','cost files','backup status','cleanup dry-run','guardrails'],
        'rules': [
            'No restart/update/config mutation.',
            'No delete/prune/cleanup execution.',
            'No message/email/Telegram/WhatsApp sends.',
            'No restore/rollback without explicit human authorization.',
            'Use OpenClaw first-class tools for authoritative cron/job operations.'
        ]
    }
    if args.json: print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print('openclaw-ops guardrails')
        for r in payload['rules']: print(f'- {r}')


def build_parser():
    p=argparse.ArgumentParser(prog='openclaw-ops', description='CLI operacional OpenClaw — read-only v0.1')
    sub=p.add_subparsers(dest='cmd', required=True)
    s=sub.add_parser('status'); s.add_argument('--json', action='store_true'); s.set_defaults(func=cmd_status)
    s=sub.add_parser('health'); s.add_argument('--json', action='store_true'); s.add_argument('--timeout', type=int, default=25); s.add_argument('--min-free-gb', type=float, default=5.0); s.set_defaults(func=cmd_health)
    s=sub.add_parser('crons'); ss=s.add_subparsers(dest='subcmd', required=True); l=ss.add_parser('logs'); l.add_argument('--json', action='store_true'); l.add_argument('--limit', type=int, default=30); l.set_defaults(func=cmd_crons)
    s=sub.add_parser('cost'); ss=s.add_subparsers(dest='subcmd', required=True); d=ss.add_parser('daily'); d.add_argument('--json', action='store_true'); d.add_argument('--limit', type=int, default=50); d.set_defaults(func=cmd_cost)
    s=sub.add_parser('backup'); ss=s.add_subparsers(dest='subcmd', required=True); b=ss.add_parser('status'); b.add_argument('--json', action='store_true'); b.set_defaults(func=cmd_backup)
    s=sub.add_parser('cleanup'); ss=s.add_subparsers(dest='subcmd', required=True); c=ss.add_parser('dry-run'); c.add_argument('--json', action='store_true'); c.set_defaults(func=cmd_cleanup)
    s=sub.add_parser('guardrails'); s.add_argument('--json', action='store_true'); s.set_defaults(func=cmd_guardrails)
    return p


def main(argv=None):
    argv=list(sys.argv[1:] if argv is None else argv)
    if argv and argv[0].lower() in BLOCKED:
        raise SystemExit('Blocked: openclaw-ops v0.1 is read-only. No restart/update/delete/send/cleanup execution.')
    args=build_parser().parse_args(argv)
    args.func(args)

if __name__ == '__main__':
    main()
