#!/usr/bin/env python3
"""Create a manual Hostinger VPS snapshot with explicit confirmation.

Required configuration, via environment or /root/.openclaw/.env:
- HOSTINGER_API_TOKEN
- HOSTINGER_VM_ID

Safety:
- Requires --yes to create a snapshot.
- Never restores or deletes snapshots.
- Logs result to runtime/hostinger/.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

ENV_PATHS = [Path('/root/.openclaw/.env'), Path('/root/.openclaw/workspace/.env')]
STATE_DIR = Path('/root/.openclaw/workspace/runtime/hostinger')
API_BASE = 'https://developers.hostinger.com/api/vps/v1'


def load_dotenv() -> None:
    for path in ENV_PATHS:
        if not path.exists():
            continue
        for raw in path.read_text(errors='ignore').splitlines():
            line = raw.strip()
            if not line or line.startswith('#') or '=' not in line:
                continue
            key, value = line.split('=', 1)
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            if key and key not in os.environ:
                os.environ[key] = value


def write_result(result: dict) -> Path:
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    path = STATE_DIR / f'snapshot-create-{ts}.json'
    path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    (STATE_DIR / 'snapshot-create-latest.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    return path


def main() -> int:
    parser = argparse.ArgumentParser(description='Create Hostinger VPS snapshot')
    parser.add_argument('--yes', action='store_true', help='Actually create the snapshot')
    parser.add_argument('--json', action='store_true', help='Print JSON output')
    args = parser.parse_args()

    now = datetime.now(timezone.utc)
    load_dotenv()
    token = os.environ.get('HOSTINGER_API_TOKEN') or os.environ.get('HAPI_API_TOKEN')
    vm_id = os.environ.get('HOSTINGER_VM_ID') or os.environ.get('HOSTINGER_VIRTUAL_MACHINE_ID')

    result = {
        'checked_at': now.isoformat(),
        'provider': 'hostinger',
        'operation': 'create_snapshot',
        'vm_id_configured': bool(vm_id),
        'token_configured': bool(token),
        'status': 'unknown',
        'message': '',
        'safety': 'create only; never restore/delete',
    }

    if not args.yes:
        result.update({'status': 'dry_run', 'message': 'Dry-run: use --yes to create snapshot. Creating a snapshot overwrites the existing Hostinger snapshot.'})
        path = write_result(result)
        result['evidence_path'] = str(path)
        print(json.dumps(result, ensure_ascii=False, indent=2) if args.json else result['message'])
        return 0

    if not token or not vm_id:
        missing = []
        if not token:
            missing.append('HOSTINGER_API_TOKEN')
        if not vm_id:
            missing.append('HOSTINGER_VM_ID')
        result.update({'status': 'blocked', 'message': 'Configuração ausente: ' + ', '.join(missing)})
        path = write_result(result)
        result['evidence_path'] = str(path)
        print(json.dumps(result, ensure_ascii=False, indent=2) if args.json else result['message'])
        return 2

    url = f'{API_BASE}/virtual-machines/{vm_id}/snapshot'
    req = Request(url, method='POST', headers={'Authorization': f'Bearer {token}', 'Accept': 'application/json'})
    try:
        with urlopen(req, timeout=60) as response:
            body = response.read().decode('utf-8', errors='replace')
            payload = json.loads(body) if body else {}
            result.update({'status': 'submitted', 'http_status': response.status, 'response': payload, 'message': 'Snapshot Hostinger solicitado com sucesso.'})
            path = write_result(result)
            result['evidence_path'] = str(path)
            print(json.dumps(result, ensure_ascii=False, indent=2) if args.json else result['message'])
            return 0
    except HTTPError as exc:
        body = exc.read().decode('utf-8', errors='replace')[:2000]
        result.update({'status': 'error', 'http_status': exc.code, 'message': f'Hostinger API HTTP {exc.code}', 'error_body': body})
    except (URLError, TimeoutError, json.JSONDecodeError) as exc:
        result.update({'status': 'error', 'message': f'Falha ao criar snapshot Hostinger: {type(exc).__name__}: {exc}'})

    path = write_result(result)
    result['evidence_path'] = str(path)
    print(json.dumps(result, ensure_ascii=False, indent=2) if args.json else result['message'])
    return 1


if __name__ == '__main__':
    sys.exit(main())
