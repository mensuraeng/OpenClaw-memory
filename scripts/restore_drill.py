#!/usr/bin/env python3
"""Restore drill seguro/read-only para infraestrutura Flávia/OpenClaw.

Guardrails:
- nunca restaura sobre produção;
- nunca apaga backup ou arquivo real;
- usa tempfile para qualquer cópia/validação;
- não chama B2/serviço externo;
- não imprime segredos.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import sqlite3
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from typing import Any

WORK = Path('/root/.openclaw/workspace')
OUT = WORK / 'runtime/restore-drill'
SQLITE_CRITICAL = WORK / 'projects/mensura-commercial-intelligence/data/commercial-intelligence.sqlite'
SECOND_BRAIN = Path('/root/2nd-brain')
BACKUPS_ROOT = WORK / 'runtime/backups'

SKIP_DIRS = {
    '.git', '__pycache__', '.pytest_cache', 'node_modules', '.venv', 'venv',
    'vps-full-stream-tmp', 'tmp', 'temp', 'cache', '.cache',
}
MAX_MANIFESTS = 80
MAX_MANIFEST_BYTES = 20 * 1024 * 1024


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode('utf-8')).hexdigest()


def safe_rel(path: Path, base: Path = WORK) -> str:
    """Canonical path key: absolute resolved path mapped to stable POSIX relative key when possible."""
    resolved = path.expanduser().resolve(strict=False)
    base_resolved = base.expanduser().resolve(strict=False)
    try:
        return resolved.relative_to(base_resolved).as_posix()
    except ValueError:
        return resolved.as_posix()


def canonical_path_key(raw: str | Path, base: Path = WORK) -> str:
    raw_str = str(raw).strip()
    if not raw_str:
        raise ValueError('empty path')
    p = Path(raw_str).expanduser()
    if not p.is_absolute():
        p = base / p
    return safe_rel(p, base=base)


def canonical_backup_id(raw: str) -> str:
    text = str(raw).strip().replace('\\', '/')
    while '//' in text:
        text = text.replace('//', '/')
    text = text.rstrip('/')
    if not text:
        raise ValueError('empty backup id')
    # Backup IDs are identifiers, not paths. Keep case to avoid merging genuinely distinct IDs.
    return text


def canonical_manifest_key(raw: str) -> str:
    text = str(raw).strip().replace('\\', '/')
    # Treat manifest file keys as path-like POSIX keys; remove query/fragment-like noise if present.
    text = text.split('?', 1)[0].split('#', 1)[0]
    norm = PurePosixPath('/' + text.lstrip('/')).as_posix().lstrip('/')
    if norm == '.':
        norm = ''
    norm = norm.rstrip('/')
    if not norm:
        raise ValueError('empty manifest key')
    return norm


def normalize_hash(raw: str) -> str:
    text = str(raw).strip().lower()
    if not text:
        raise ValueError('empty hash')
    return text


def run(cmd: list[str], cwd: Path, timeout: int = 60) -> dict[str, Any]:
    try:
        p = subprocess.run(cmd, cwd=str(cwd), capture_output=True, text=True, timeout=timeout)
        return {
            'cmd': cmd[:2] + ['…'] if len(cmd) > 2 else cmd,
            'returncode': p.returncode,
            'stdout_tail': (p.stdout or '')[-4000:],
            'stderr_tail': (p.stderr or '')[-2000:],
        }
    except subprocess.TimeoutExpired:
        return {'cmd': cmd[:2] + ['…'], 'returncode': 124, 'stdout_tail': '', 'stderr_tail': 'timeout'}
    except Exception as e:
        return {'cmd': cmd[:2] + ['…'], 'returncode': 1, 'stdout_tail': '', 'stderr_tail': str(e)[:500]}


def check_key_normalization() -> dict[str, Any]:
    path_variants = [
        'projects/mensura-commercial-intelligence/data/../data/commercial-intelligence.sqlite',
        str(SQLITE_CRITICAL),
        str(SQLITE_CRITICAL) + '/',
    ]
    # File path and same textual path with trailing slash should converge for keying purposes.
    path_keys = [canonical_path_key(v).rstrip('/') for v in path_variants]

    manifest_variants = [
        'runtime/backups/example/manifest.json',
        '/runtime/backups/example/manifest.json/',
        'runtime/backups/example/manifest.json?download=1',
    ]
    manifest_keys = [canonical_manifest_key(v) for v in manifest_variants]

    backup_variants = ['backup-20260430/', 'backup-20260430']
    backup_keys = [canonical_backup_id(v) for v in backup_variants]

    checks = {
        'path_relative_absolute_trailing_slash': len(set(path_keys)) == 1,
        'manifest_query_trailing_slash': len(set(manifest_keys)) == 1,
        'backup_id_trailing_slash': len(set(backup_keys)) == 1,
        'different_paths_remain_different': canonical_path_key('a') != canonical_path_key('b'),
    }
    return {
        'status': 'ok' if all(checks.values()) else 'fail',
        'checks': checks,
        'evidence': {
            'path_key_hashes': [sha256_text(k)[:12] for k in path_keys],
            'manifest_key_hashes': [sha256_text(k)[:12] for k in manifest_keys],
            'backup_id_hashes': [sha256_text(k)[:12] for k in backup_keys],
        },
    }


def check_sqlite(temp_root: Path) -> dict[str, Any]:
    check: dict[str, Any] = {'name': 'critical_sqlite_copy_integrity', 'path': safe_rel(SQLITE_CRITICAL)}
    if not SQLITE_CRITICAL.exists():
        check.update({'status': 'skipped', 'detail': 'arquivo crítico não existe'})
        return check
    if not SQLITE_CRITICAL.is_file():
        check.update({'status': 'fail', 'detail': 'path crítico existe mas não é arquivo'})
        return check

    copy_path = temp_root / 'commercial-intelligence.sqlite'
    shutil.copy2(SQLITE_CRITICAL, copy_path)
    conn = sqlite3.connect(f'file:{copy_path}?mode=ro', uri=True)
    try:
        integrity = conn.execute('PRAGMA integrity_check').fetchone()[0]
        tables = [row[0] for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name")]
        counts: dict[str, int | str] = {}
        for table in tables:
            # Table names came from sqlite_master; quote defensively.
            quoted = '"' + table.replace('"', '""') + '"'
            try:
                counts[table] = int(conn.execute(f'SELECT COUNT(*) FROM {quoted}').fetchone()[0])
            except Exception as e:
                counts[table] = f'count_error:{type(e).__name__}'
        check.update({
            'status': 'ok' if integrity == 'ok' else 'fail',
            'detail': f'integrity_check={integrity}',
            'size_bytes': SQLITE_CRITICAL.stat().st_size,
            'table_count': len(tables),
            'row_counts': counts,
            'temp_copy': 'tempfile sandbox, removed automatically',
        })
        return check
    finally:
        conn.close()


def check_second_brain_git() -> dict[str, Any]:
    check: dict[str, Any] = {'name': 'second_brain_git_readonly', 'path': str(SECOND_BRAIN)}
    if not SECOND_BRAIN.exists():
        check.update({'status': 'skipped', 'detail': 'path não existe'})
        return check
    if not (SECOND_BRAIN / '.git').exists():
        check.update({'status': 'skipped', 'detail': 'não é repositório git'})
        return check
    status = run(['git', 'status', '--porcelain=v1'], cwd=SECOND_BRAIN, timeout=30)
    fsck = run(['git', 'fsck', '--no-progress'], cwd=SECOND_BRAIN, timeout=120)
    dirty_lines = [line for line in status.get('stdout_tail', '').splitlines() if line.strip()]
    ok = status['returncode'] == 0 and fsck['returncode'] == 0
    state = 'ok' if ok and not dirty_lines else 'attention' if ok else 'fail'
    check.update({
        'status': state,
        'detail': 'git status/fsck somente leitura executados',
        'dirty_count': len(dirty_lines),
        'fsck_returncode': fsck['returncode'],
        'status_returncode': status['returncode'],
        'fsck_stderr_tail': fsck.get('stderr_tail', '')[-1000:],
    })
    return check


def iter_manifest_paths(root: Path):
    if not root.exists():
        return
    yielded = 0
    for current, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS and not d.startswith('.')]
        for filename in filenames:
            lower = filename.lower()
            if lower.startswith('manifest') and lower.endswith('.json') or lower.endswith('.manifest.json'):
                path = Path(current) / filename
                yielded += 1
                yield path
                if yielded >= MAX_MANIFESTS:
                    return


def extract_manifest_entries(data: Any) -> list[dict[str, Any]]:
    if isinstance(data, list):
        return [item for item in data if isinstance(item, dict)]
    if not isinstance(data, dict):
        return []
    for key in ('files', 'entries', 'objects', 'items', 'parts'):
        value = data.get(key)
        if isinstance(value, list):
            return [item for item in value if isinstance(item, dict)]
    return []


def entry_key_and_hash(entry: dict[str, Any]) -> tuple[str | None, str | None]:
    key_fields = ('path', 'file', 'name', 'key', 'relative_path', 'relpath')
    hash_fields = ('sha256', 'hash', 'checksum', 'digest')
    raw_key = next((entry.get(k) for k in key_fields if entry.get(k)), None)
    raw_hash = next((entry.get(k) for k in hash_fields if entry.get(k)), None)
    key = canonical_manifest_key(str(raw_key)) if raw_key else None
    digest = normalize_hash(str(raw_hash)) if raw_hash else None
    return key, digest


def check_manifests() -> dict[str, Any]:
    check: dict[str, Any] = {'name': 'local_backup_manifests', 'root': safe_rel(BACKUPS_ROOT)}
    if not BACKUPS_ROOT.exists():
        check.update({'status': 'skipped', 'detail': 'runtime/backups não existe'})
        return check
    summaries = []
    problems = []
    for path in iter_manifest_paths(BACKUPS_ROOT) or []:
        rel = safe_rel(path)
        try:
            size = path.stat().st_size
            if size > MAX_MANIFEST_BYTES:
                summaries.append({'path': rel, 'status': 'skipped', 'detail': f'manifest muito grande: {size} bytes'})
                continue
            data = json.loads(path.read_text(encoding='utf-8'))
            entries = extract_manifest_entries(data)
            canonical_pairs = []
            missing_key = 0
            for entry in entries:
                try:
                    key, digest = entry_key_and_hash(entry)
                    if key:
                        canonical_pairs.append({'key': key, 'hash': digest})
                    else:
                        missing_key += 1
                except Exception as e:
                    problems.append({'path': rel, 'problem': f'entry_normalization_error:{type(e).__name__}'})
            duplicate_keys = len(canonical_pairs) - len({p['key'] for p in canonical_pairs})
            duplicate_key_hash_pairs = len(canonical_pairs) - len({(p['key'], p.get('hash')) for p in canonical_pairs})
            if duplicate_keys:
                problems.append({'path': rel, 'problem': f'{duplicate_keys} duplicate canonical manifest key(s)'})
            summaries.append({
                'path': rel,
                'status': 'ok' if not duplicate_keys else 'attention',
                'top_level_type': type(data).__name__,
                'entries': len(entries),
                'missing_key_entries': missing_key,
                'duplicate_canonical_keys': duplicate_keys,
                'duplicate_canonical_key_hash_pairs': duplicate_key_hash_pairs,
                'manifest_key': canonical_manifest_key(rel),
            })
        except Exception as e:
            problems.append({'path': rel, 'problem': f'manifest_read_error:{type(e).__name__}'})
            summaries.append({'path': rel, 'status': 'fail', 'detail': str(e)[:300]})
    if not summaries:
        check.update({'status': 'skipped', 'detail': 'nenhum manifest*.json local encontrado no escopo limitado'})
    else:
        check.update({
            'status': 'fail' if any(s.get('status') == 'fail' for s in summaries) else 'attention' if problems else 'ok',
            'manifest_count': len(summaries),
            'manifests': summaries,
            'problems': problems,
        })
    return check


def markdown_report(result: dict[str, Any]) -> str:
    lines = [
        '# Restore Drill — latest',
        '',
        f"- Checked at UTC: `{result['checked_at_utc']}`",
        f"- Overall: **{result['overall']}**",
        f"- Workspace: `{WORK}`",
        f"- Safety: read-only, tempfile sandbox, no external calls, no production restore.",
        '',
        '## Checks',
    ]
    for check in result['checks']:
        detail = check.get('detail') or check.get('path') or ''
        suffix = f" — {detail}" if detail else ''
        lines.append(f"- **{check['name']}**: `{check['status']}`{suffix}")
        if check['name'] == 'critical_sqlite_copy_integrity' and check.get('row_counts'):
            counts = ', '.join(f"{k}={v}" for k, v in sorted(check['row_counts'].items()))
            lines.append(f"  - SQLite row counts: {counts}")
        if check['name'] == 'local_backup_manifests':
            lines.append(f"  - Manifest count: {check.get('manifest_count', 0)}")
        if check['name'] == 'key_normalization_and_idempotency':
            lines.append(f"  - Stability checks: {json.dumps(check.get('checks', {}), ensure_ascii=False, sort_keys=True)}")
    lines.append('')
    lines.append('## Guardrails')
    lines.extend([
        '- Não restaura sobre caminhos reais.',
        '- Não apaga backups.',
        '- Não executa `rm`.',
        '- Não chama B2/serviços externos.',
        '- Não imprime segredos.',
    ])
    return '\n'.join(lines) + '\n'


def build_result() -> dict[str, Any]:
    OUT.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='restore-drill-') as tmp:
        temp_root = Path(tmp)
        checks = [
            {'name': 'key_normalization_and_idempotency', **check_key_normalization()},
            check_sqlite(temp_root),
            check_second_brain_git(),
            check_manifests(),
        ]
    counts: dict[str, int] = {}
    for check in checks:
        counts[check['status']] = counts.get(check['status'], 0) + 1
    if counts.get('fail'):
        overall = 'fail'
    elif counts.get('attention'):
        overall = 'attention'
    elif counts.get('ok'):
        overall = 'ok'
    else:
        overall = 'skipped'
    return {
        'checked_at_utc': now_iso(),
        'overall': overall,
        'counts': counts,
        'guardrails': {
            'production_restore': False,
            'destructive_actions': False,
            'external_calls': False,
            'tempfile_sandbox': True,
        },
        'checks': checks,
    }


def write_outputs(result: dict[str, Any]) -> None:
    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    json_text = json.dumps(result, ensure_ascii=False, indent=2) + '\n'
    md_text = markdown_report(result)
    (OUT / 'latest.json').write_text(json_text, encoding='utf-8')
    (OUT / 'latest.md').write_text(md_text, encoding='utf-8')
    (OUT / f'restore-drill-{stamp}.json').write_text(json_text, encoding='utf-8')
    (OUT / f'restore-drill-{stamp}.md').write_text(md_text, encoding='utf-8')


def main() -> int:
    parser = argparse.ArgumentParser(description='Restore drill seguro/read-only')
    parser.add_argument('--json', action='store_true', help='imprime JSON resumido no stdout')
    args = parser.parse_args()
    result = build_result()
    write_outputs(result)
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result['overall'] in {'ok', 'attention', 'skipped'} else 1


if __name__ == '__main__':
    raise SystemExit(main())
