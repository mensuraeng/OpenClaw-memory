#!/usr/bin/env python3
"""Retencao segura dos backups locais e Backblaze B2.

Politica operacional:
  - B2: manter 2 conjuntos mais recentes em flavia/vps-full e flavia/2nd-brain.
  - VPS: manter 2 backups full locais validos e 2 conjuntos locais do 2nd-brain.
  - Nunca limpar backup full local se nao existir ao menos 1 conjunto full valido no B2.

Por padrao roda em dry-run. Use --run para apagar candidatos.
"""
from __future__ import annotations

import argparse
import base64
import json
import os
import re
import urllib.error
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

WORKSPACE = Path('/root/.openclaw/workspace')
ENV_FILE = WORKSPACE / 'memory/context/backblaze_b2_backup.env'
OPENCLAW_BACKUPS = Path('/root/openclaw-backups')
SECOND_BRAIN_LOCAL = WORKSPACE / 'runtime/backups/2nd-brain'

VPS_PREFIX = 'flavia/vps-full/'
SECOND_BRAIN_PREFIX = 'flavia/2nd-brain/'
REMOTE_KEEP = 2
LOCAL_KEEP = 2
MIN_FULL_BACKUP_BYTES = 1024 * 1024 * 1024


@dataclass
class BackupSet:
    key: str
    created: str
    files: list[dict[str, Any]]
    complete: bool = True

    @property
    def size(self) -> int:
        return sum(int(f.get('contentLength') or f.get('size') or 0) for f in self.files)


def load_env(path: Path = ENV_FILE) -> dict[str, str]:
    env: dict[str, str] = {}
    if path.exists():
        for raw in path.read_text(encoding='utf-8').splitlines():
            line = raw.strip()
            if not line or line.startswith('#') or '=' not in line:
                continue
            key, value = line.split('=', 1)
            env[key.strip()] = value.strip().strip('"').strip("'")
    for key in ['B2_KEY_ID', 'B2_APPLICATION_KEY', 'B2_BUCKET_NAME']:
        if os.getenv(key):
            env[key] = os.getenv(key, '')
    return env


def require_env(env: dict[str, str]) -> None:
    missing = [k for k in ['B2_KEY_ID', 'B2_APPLICATION_KEY', 'B2_BUCKET_NAME'] if not env.get(k)]
    if missing:
        raise SystemExit(f'Configuração B2 incompleta. Faltando: {", ".join(missing)} em {ENV_FILE}')


def b2_json(url: str, method: str = 'GET', headers: dict[str, str] | None = None, body: bytes | None = None) -> dict[str, Any]:
    req = urllib.request.Request(url, data=body, headers=headers or {}, method=method)
    try:
        with urllib.request.urlopen(req, timeout=180) as response:
            text = response.read().decode('utf-8', 'replace')
            return json.loads(text) if text else {}
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode('utf-8', 'replace')[:1000]
        raise RuntimeError(f'B2 HTTP {exc.code}: {detail}') from exc


def authorize(env: dict[str, str]) -> dict[str, Any]:
    token = base64.b64encode(f"{env['B2_KEY_ID']}:{env['B2_APPLICATION_KEY']}".encode()).decode()
    return b2_json('https://api.backblazeb2.com/b2api/v3/b2_authorize_account', headers={'Authorization': 'Basic ' + token})


def find_bucket(auth: dict[str, Any], bucket_name: str) -> dict[str, Any]:
    api = auth['apiInfo']['storageApi']['apiUrl']
    body = json.dumps({'accountId': auth['accountId'], 'bucketName': bucket_name}).encode()
    data = b2_json(api + '/b2api/v3/b2_list_buckets', method='POST', headers={'Authorization': auth['authorizationToken'], 'Content-Type': 'application/json'}, body=body)
    buckets = data.get('buckets', [])
    if not buckets:
        raise RuntimeError(f'Bucket não encontrado ou sem permissão: {bucket_name}')
    return buckets[0]


def list_files(auth: dict[str, Any], bucket_id: str, prefix: str) -> list[dict[str, Any]]:
    api = auth['apiInfo']['storageApi']['apiUrl']
    start_file_name: str | None = None
    files: list[dict[str, Any]] = []
    while True:
        payload: dict[str, Any] = {'bucketId': bucket_id, 'prefix': prefix, 'maxFileCount': 1000}
        if start_file_name:
            payload['startFileName'] = start_file_name
        data = b2_json(api + '/b2api/v3/b2_list_file_names', method='POST', headers={'Authorization': auth['authorizationToken'], 'Content-Type': 'application/json'}, body=json.dumps(payload).encode())
        files.extend(data.get('files', []))
        start_file_name = data.get('nextFileName')
        if not start_file_name:
            return files


def delete_file(auth: dict[str, Any], file_info: dict[str, Any]) -> None:
    api = auth['apiInfo']['storageApi']['apiUrl']
    body = json.dumps({'fileName': file_info['fileName'], 'fileId': file_info['fileId']}).encode()
    b2_json(api + '/b2api/v3/b2_delete_file_version', method='POST', headers={'Authorization': auth['authorizationToken'], 'Content-Type': 'application/json'}, body=body)


def vps_sets(files: list[dict[str, Any]]) -> list[BackupSet]:
    grouped: dict[str, list[dict[str, Any]]] = {}
    for item in files:
        name = item.get('fileName', '')
        rest = name[len(VPS_PREFIX):] if name.startswith(VPS_PREFIX) else ''
        if '/' not in rest:
            continue
        key = rest.split('/', 1)[0]
        grouped.setdefault(key, []).append(item)
    sets: list[BackupSet] = []
    for key, items in grouped.items():
        names = [i.get('fileName', '') for i in items]
        complete = any(n.endswith('.manifest.json') for n in names) and any('.part-' in n for n in names)
        sets.append(BackupSet(key=key, created=key, files=items, complete=complete))
    return sorted(sets, key=lambda s: s.created, reverse=True)


def second_brain_sets(files: list[dict[str, Any]]) -> list[BackupSet]:
    sets: list[BackupSet] = []
    for item in files:
        name = item.get('fileName', '')
        match = re.search(r'2nd-brain-(\d{8}T\d{6}Z)\.tar\.gz\.enc$', name)
        if match:
            sets.append(BackupSet(key=match.group(1), created=match.group(1), files=[item], complete=True))
    return sorted(sets, key=lambda s: s.created, reverse=True)


def local_full_backups() -> list[Path]:
    if not OPENCLAW_BACKUPS.exists():
        return []
    candidates = []
    for path in OPENCLAW_BACKUPS.glob('*-openclaw-backup.tar.gz'):
        if path.is_file() and path.stat().st_size >= MIN_FULL_BACKUP_BYTES:
            candidates.append(path)
    return sorted(candidates, key=lambda p: p.stat().st_mtime, reverse=True)


def local_second_brain_sets() -> list[list[Path]]:
    grouped: dict[str, list[Path]] = {}
    if not SECOND_BRAIN_LOCAL.exists():
        return []
    for path in SECOND_BRAIN_LOCAL.glob('2nd-brain-*.tar.gz*'):
        match = re.match(r'2nd-brain-(\d{8}T\d{6}Z)\.tar\.gz(?:\.enc)?$', path.name)
        if match:
            grouped.setdefault(match.group(1), []).append(path)
    return [grouped[k] for k in sorted(grouped.keys(), reverse=True)]


def summarize_set(item: BackupSet) -> dict[str, Any]:
    return {
        'key': item.key,
        'complete': item.complete,
        'files': len(item.files),
        'size_bytes': item.size,
    }


def retention_plan(auth: dict[str, Any], bucket_id: str) -> dict[str, Any]:
    vps = vps_sets(list_files(auth, bucket_id, VPS_PREFIX))
    vps_complete = [s for s in vps if s.complete]
    brain = second_brain_sets(list_files(auth, bucket_id, SECOND_BRAIN_PREFIX))
    local_full = local_full_backups()
    local_brain = local_second_brain_sets()

    return {
        'remote_vps_sets': [summarize_set(s) for s in vps],
        'remote_vps_delete': [summarize_set(s) for s in vps_complete[REMOTE_KEEP:]],
        'remote_vps_incomplete': [summarize_set(s) for s in vps if not s.complete],
        'remote_2nd_brain_sets': [summarize_set(s) for s in brain],
        'remote_2nd_brain_delete': [summarize_set(s) for s in brain[REMOTE_KEEP:]],
        'local_full_sets': [{'path': str(p), 'size_bytes': p.stat().st_size, 'mtime_utc': datetime.fromtimestamp(p.stat().st_mtime, timezone.utc).isoformat()} for p in local_full],
        'local_full_delete': [] if not vps_complete else [{'path': str(p), 'size_bytes': p.stat().st_size} for p in local_full[LOCAL_KEEP:]],
        'local_full_cleanup_blocked': len(vps_complete) == 0 and len(local_full) > LOCAL_KEEP,
        'local_2nd_brain_sets': [[str(p) for p in group] for group in local_brain],
        'local_2nd_brain_delete': [[str(p) for p in group] for group in local_brain[LOCAL_KEEP:]],
        '_objects': {
            'remote_vps_delete': vps_complete[REMOTE_KEEP:],
            'remote_2nd_brain_delete': brain[REMOTE_KEEP:],
            'local_full_delete': [] if not vps_complete else local_full[LOCAL_KEEP:],
            'local_2nd_brain_delete': local_brain[LOCAL_KEEP:],
        },
    }


def run_deletes(auth: dict[str, Any], plan: dict[str, Any]) -> dict[str, int]:
    counts = {'remote_files_deleted': 0, 'local_files_deleted': 0}
    objects = plan['_objects']
    for backup_set in objects['remote_vps_delete'] + objects['remote_2nd_brain_delete']:
        for file_info in backup_set.files:
            delete_file(auth, file_info)
            counts['remote_files_deleted'] += 1
    for path in objects['local_full_delete']:
        path.unlink()
        counts['local_files_deleted'] += 1
    for group in objects['local_2nd_brain_delete']:
        for path in group:
            path.unlink()
            counts['local_files_deleted'] += 1
    return counts


def strip_objects(plan: dict[str, Any]) -> dict[str, Any]:
    clean = dict(plan)
    clean.pop('_objects', None)
    return clean


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--run', action='store_true', help='Executa as exclusoes planejadas')
    parser.add_argument('--dry-run', action='store_true', help='Mostra o plano sem apagar nada')
    args = parser.parse_args()

    env = load_env()
    require_env(env)
    auth = authorize(env)
    bucket = find_bucket(auth, env['B2_BUCKET_NAME'])
    plan = retention_plan(auth, bucket['bucketId'])
    result = {
        'mode': 'run' if args.run else 'dry-run',
        'bucket': bucket.get('bucketName'),
        'policy': {
            'remote_keep_sets': REMOTE_KEEP,
            'local_keep_sets': LOCAL_KEEP,
            'local_full_cleanup_requires_remote_vps_complete': True,
        },
        'plan': strip_objects(plan),
    }
    if args.run:
        result['deleted'] = run_deletes(auth, plan)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
