#!/usr/bin/env python3
"""Read-only Hostinger VPS snapshot check.

Required configuration, via environment or /root/.openclaw/.env:
- HOSTINGER_API_TOKEN
- HOSTINGER_VM_ID

This script only checks the current snapshot. It never creates, restores, or deletes snapshots.
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
STATE_FILE = STATE_DIR / 'snapshot-status-latest.json'
API_BASE = 'https://developers.hostinger.com/api/vps/v1'
USER_AGENT = 'OpenClaw-Flavia/1.0 (+https://docs.openclaw.ai)'


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


def parse_dt(value):
    if not value or not isinstance(value, str):
        return None
    candidates = [value]
    if value.endswith('Z'):
        candidates.append(value[:-1] + '+00:00')
    for item in candidates:
        try:
            dt = datetime.fromisoformat(item)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt.astimezone(timezone.utc)
        except ValueError:
            pass
    return None


def find_timestamp(payload):
    keys = ('created_at', 'createdAt', 'created', 'date', 'updated_at', 'updatedAt')
    if isinstance(payload, dict):
        for key in keys:
            dt = parse_dt(payload.get(key))
            if dt:
                return dt, key
        for value in payload.values():
            found = find_timestamp(value)
            if found:
                return found
    elif isinstance(payload, list):
        for item in payload:
            found = find_timestamp(item)
            if found:
                return found
    return None


def main() -> int:
    parser = argparse.ArgumentParser(description='Check Hostinger VPS snapshot status')
    parser.add_argument('--max-age-hours', type=float, default=30 * 24, help='Warn if snapshot is older than this threshold')
    parser.add_argument('--json', action='store_true', help='Print JSON output')
    args = parser.parse_args()

    load_dotenv()
    token = os.environ.get('HOSTINGER_API_TOKEN') or os.environ.get('HAPI_API_TOKEN')
    vm_id = os.environ.get('HOSTINGER_VM_ID') or os.environ.get('HOSTINGER_VIRTUAL_MACHINE_ID')
    now = datetime.now(timezone.utc)

    result = {
        'checked_at': now.isoformat(),
        'provider': 'hostinger',
        'vm_id_configured': bool(vm_id),
        'token_configured': bool(token),
        'status': 'unknown',
        'severity': 'unknown',
        'message': '',
    }

    if not token or not vm_id:
        missing = []
        if not token:
            missing.append('HOSTINGER_API_TOKEN')
        if not vm_id:
            missing.append('HOSTINGER_VM_ID')
        result.update({
            'status': 'blocked',
            'severity': 'attention',
            'message': 'Configuração ausente: ' + ', '.join(missing),
        })
        STATE_DIR.mkdir(parents=True, exist_ok=True)
        STATE_FILE.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
        print(json.dumps(result, ensure_ascii=False, indent=2) if args.json else result['message'])
        return 2

    url = f'{API_BASE}/virtual-machines/{vm_id}/snapshot'
    req = Request(url, headers={'Authorization': f'Bearer {token}', 'Accept': 'application/json', 'User-Agent': USER_AGENT})
    try:
        with urlopen(req, timeout=30) as response:
            body = response.read().decode('utf-8', errors='replace')
            payload = json.loads(body) if body else {}
            result['http_status'] = response.status
            result['snapshot'] = payload
    except HTTPError as exc:
        body = exc.read().decode('utf-8', errors='replace')[:2000]
        result.update({'status': 'error', 'severity': 'fail', 'http_status': exc.code, 'message': f'Hostinger API HTTP {exc.code}', 'error_body': body})
        STATE_DIR.mkdir(parents=True, exist_ok=True)
        STATE_FILE.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
        print(json.dumps(result, ensure_ascii=False, indent=2) if args.json else result['message'])
        return 1
    except (URLError, TimeoutError, json.JSONDecodeError) as exc:
        result.update({'status': 'error', 'severity': 'fail', 'message': f'Falha ao consultar Hostinger snapshot: {type(exc).__name__}: {exc}'})
        STATE_DIR.mkdir(parents=True, exist_ok=True)
        STATE_FILE.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
        print(json.dumps(result, ensure_ascii=False, indent=2) if args.json else result['message'])
        return 1

    found = find_timestamp(result.get('snapshot'))
    if found:
        snapshot_dt, key = found
        age_hours = (now - snapshot_dt).total_seconds() / 3600
        result['snapshot_timestamp'] = snapshot_dt.isoformat()
        result['snapshot_timestamp_field'] = key
        result['snapshot_age_hours'] = round(age_hours, 2)
        if age_hours > args.max_age_hours:
            result.update({'status': 'stale', 'severity': 'attention', 'message': f'Snapshot Hostinger antigo: {age_hours:.1f}h'})
            rc = 3
        else:
            result.update({'status': 'ok', 'severity': 'ok', 'message': f'Snapshot Hostinger verificado: {age_hours:.1f}h'})
            rc = 0
    else:
        result.update({'status': 'ok_unparsed', 'severity': 'attention', 'message': 'Snapshot consultado, mas data não identificada automaticamente'})
        rc = 4

    STATE_DIR.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(result, ensure_ascii=False, indent=2) if args.json else result['message'])
    return rc


if __name__ == '__main__':
    sys.exit(main())
