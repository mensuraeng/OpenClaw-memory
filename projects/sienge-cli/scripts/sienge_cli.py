#!/usr/bin/env python3
"""sienge — CLI controlada para integração Sienge.

v0.2 libera upload real somente sob ordem explícita do Alê/Alexandre,
com flags de autorização e confirmação. Dry-run continua sendo o padrão.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

WORKSPACE = Path('/root/.openclaw/workspace')
SCRIPTS = {
    'upload_teatro_legacy': WORKSPACE / 'scripts/sienge_upload_orcamento_teatro_suzano.py',
    'monitor_lock': WORKSPACE / 'scripts/sienge_monitor_lock_teatro.py',
    'pcs_upload': WORKSPACE / 'projects/pcs-sienge-integration/scripts/upload_budget.py',
    'pcs_upload_teatro': WORKSPACE / 'projects/pcs-sienge-integration/scripts/upload_budget_teatro.py',
}
BLOCKED_TOP_LEVEL = {'send', 'delete', 'post', 'commit'}
CONFIRM_PHRASE = 'AUTORIZO SIENGE'


def emit(payload, args):
    print(json.dumps(payload, ensure_ascii=False, indent=2, default=str) if getattr(args, 'json', False) else json.dumps(payload, ensure_ascii=False, indent=2, default=str))


def status(args):
    emit({
        'mode': 'controlled_v0.2',
        'time': datetime.now().isoformat(timespec='seconds'),
        'scripts': {k: {'path': str(v), 'exists': v.exists()} for k, v in SCRIPTS.items()},
        'guardrails': 'dry-run by default; real upload only with explicit Alexandre authorization flags',
        'confirm_phrase': CONFIRM_PHRASE,
    }, args)


def budget_validate(args):
    path = Path(args.file).expanduser().resolve()
    emit({
        'mode': 'read_only',
        'file': str(path),
        'exists': path.exists(),
        'suffix': path.suffix.lower(),
        'size': path.stat().st_size if path.exists() else None,
        'upload_ready_format': path.exists() and path.suffix.lower() in {'.xlsx', '.xlsm', '.xls'},
        'note': 'Validação estrutural profunda ainda depende do script alvo; use upload-authorized sem --execute para dry-run.',
    }, args)


def _target_script(target: str) -> Path:
    if target == 'teatro':
        return SCRIPTS['pcs_upload_teatro']
    if target == 'generic':
        return SCRIPTS['pcs_upload']
    raise SystemExit(f'Target inválido: {target}')


def _build_upload_cmd(args, execute: bool) -> list[str]:
    script = _target_script(args.target)
    if not script.exists():
        raise SystemExit(f'Script alvo não existe: {script}')
    cmd = ['python3', str(script), '--file', str(Path(args.file).expanduser().resolve()), '--building-id', str(args.building_id)]
    if args.config:
        cmd += ['--config', args.config]
    if args.target == 'teatro':
        cmd += ['--batch-limit', str(args.batch_limit)]
        if args.reset_checkpoint:
            cmd.append('--reset-checkpoint')
    elif args.sheet_id is not None:
        cmd += ['--sheet-id', str(args.sheet_id)]
    if not execute:
        cmd.append('--dry-run')
    return cmd


def upload_authorized(args):
    path = Path(args.file).expanduser().resolve()
    if not path.exists():
        raise SystemExit(f'Arquivo não existe: {path}')
    if path.suffix.lower() not in {'.xlsx', '.xlsm', '.xls'}:
        raise SystemExit('Arquivo precisa ser Excel: .xlsx/.xlsm/.xls')

    execute = bool(args.execute)
    if execute:
        missing = []
        if (args.approved_by or '').strip().lower() not in {'alexandre', 'alê', 'ale', 'alexandre aguiar'}:
            missing.append('--approved-by Alexandre')
        if (args.confirm or '').strip() != CONFIRM_PHRASE:
            missing.append(f'--confirm "{CONFIRM_PHRASE}"')
        if not args.approval_note or len(args.approval_note.strip()) < 12:
            missing.append('--approval-note com justificativa objetiva')
        if missing:
            emit({
                'mode': 'blocked_missing_authorization',
                'execute_requested': True,
                'missing': missing,
                'rule': 'Upload real no Sienge só com ordem explícita do Alexandre/Alê.',
            }, args)
            raise SystemExit(2)

    cmd = _build_upload_cmd(args, execute=execute)
    if args.print_command or not execute:
        payload = {
            'mode': 'dry_run' if not execute else 'authorized_execute_preview',
            'execute': execute,
            'target': args.target,
            'file': str(path),
            'building_id': args.building_id,
            'approved_by': args.approved_by if execute else None,
            'approval_note': args.approval_note if execute else None,
            'cmd': cmd,
            'note': 'Sem --execute, roda o script alvo em --dry-run. Com --execute e autorização completa, executa upload real.',
        }
        if not execute or args.print_command:
            emit(payload, args)
        if not execute:
            result = subprocess.run(cmd, text=True, capture_output=True, timeout=args.timeout)
            emit({'mode': 'dry_run_result', 'ok': result.returncode == 0, 'code': result.returncode, 'stdout': result.stdout[-6000:], 'stderr': result.stderr[-4000:]}, args)
            if result.returncode != 0:
                raise SystemExit(result.returncode)
            return

    result = subprocess.run(cmd, text=True, capture_output=True, timeout=args.timeout)
    emit({
        'mode': 'authorized_execute_result',
        'ok': result.returncode == 0,
        'code': result.returncode,
        'target': args.target,
        'file': str(path),
        'approved_by': args.approved_by,
        'approval_note': args.approval_note,
        'stdout': result.stdout[-8000:],
        'stderr': result.stderr[-8000:],
    }, args)
    if result.returncode != 0:
        raise SystemExit(result.returncode)


def upload_dry(args):
    # Backwards-compatible alias.
    args.execute = False
    args.approved_by = None
    args.confirm = None
    args.approval_note = None
    args.target = getattr(args, 'target', 'teatro')
    args.building_id = getattr(args, 'building_id', 1354)
    args.batch_limit = getattr(args, 'batch_limit', 90)
    args.config = getattr(args, 'config', None)
    args.sheet_id = getattr(args, 'sheet_id', None)
    args.reset_checkpoint = False
    args.print_command = True
    args.timeout = getattr(args, 'timeout', 180)
    upload_authorized(args)


def guardrails(args):
    emit({
        'mode': 'controlled_v0.2',
        'rules': [
            'Dry-run é o padrão.',
            'Upload real só com --execute + --approved-by Alexandre + --confirm "AUTORIZO SIENGE" + --approval-note.',
            'Arquivo precisa existir localmente e ser Excel.',
            'Sem envio externo automático pela CLI.',
            'Sem delete/rollback automático.',
        ],
        'confirm_phrase': CONFIRM_PHRASE,
        'real_upload_command': 'sienge budget upload-authorized <arquivo.xlsx> --execute --approved-by Alexandre --confirm "AUTORIZO SIENGE" --approval-note "ordem do Alê ..."',
    }, args)


def parser():
    p = argparse.ArgumentParser(prog='sienge')
    sub = p.add_subparsers(dest='cmd', required=True)

    s = sub.add_parser('status')
    s.add_argument('--json', action='store_true')
    s.set_defaults(func=status)

    s = sub.add_parser('budget')
    ss = s.add_subparsers(dest='subcmd', required=True)

    v = ss.add_parser('validate')
    v.add_argument('file')
    v.add_argument('--json', action='store_true')
    v.set_defaults(func=budget_validate)

    d = ss.add_parser('upload-dry-run')
    d.add_argument('file')
    d.add_argument('--target', choices=['teatro', 'generic'], default='teatro')
    d.add_argument('--building-id', type=int, default=1354)
    d.add_argument('--batch-limit', type=int, default=90)
    d.add_argument('--config')
    d.add_argument('--sheet-id', type=int)
    d.add_argument('--timeout', type=int, default=180)
    d.add_argument('--json', action='store_true')
    d.set_defaults(func=upload_dry)

    u = ss.add_parser('upload-authorized')
    u.add_argument('file')
    u.add_argument('--target', choices=['teatro', 'generic'], default='teatro')
    u.add_argument('--building-id', type=int, default=1354)
    u.add_argument('--batch-limit', type=int, default=90)
    u.add_argument('--config')
    u.add_argument('--sheet-id', type=int)
    u.add_argument('--reset-checkpoint', action='store_true')
    u.add_argument('--execute', action='store_true')
    u.add_argument('--approved-by')
    u.add_argument('--confirm')
    u.add_argument('--approval-note')
    u.add_argument('--print-command', action='store_true')
    u.add_argument('--timeout', type=int, default=900)
    u.add_argument('--json', action='store_true')
    u.set_defaults(func=upload_authorized)

    s = sub.add_parser('guardrails')
    s.add_argument('--json', action='store_true')
    s.set_defaults(func=guardrails)
    return p


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    if argv and argv[0].lower() in BLOCKED_TOP_LEVEL:
        raise SystemExit('Blocked: sienge v0.2 only allows controlled budget upload subcommands.')
    args = parser().parse_args(argv)
    args.func(args)


if __name__ == '__main__':
    main()
