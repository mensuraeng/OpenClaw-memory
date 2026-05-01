#!/usr/bin/env python3
"""KeeSpace readiness/secret hygiene check.

No secret values are printed. Exit codes:
0 = ok for selected mode
1 = hygiene/resolution failure
2 = runtime not configured for KeeSpace pure mode
"""
from __future__ import annotations

import argparse
import json
import os
import time
from pathlib import Path

from secret_config import assert_no_plaintext_secret_refs, load_json_config, secret_mode

WORKSPACE = Path('/root/.openclaw/workspace')
CONFIGS = [
    WORKSPACE / 'config/hubspot-mensura.json',
    WORKSPACE / 'config/phantombuster-mensura.json',
    WORKSPACE / 'config/linkedin-mensura.json',
]
WORKSPACE_SECRET_FILES = [
    WORKSPACE / 'config/linkedin-mensura.env',
    WORKSPACE / 'credentials/ga4-service-account.json',
    WORKSPACE / 'credentials/ga_service_account.json',
]
ROOT_FALLBACKS = [
    Path('/root/.secrets/openclaw-commercial.env'),
    Path('/root/.secrets/openclaw-linkedin.env'),
    Path('/root/.secrets/make.env'),
    Path('/root/.secrets/notion.env'),
    Path('/root/.secrets/sienge-pcs.env'),
    Path('/root/.secrets/ga4-service-account.json'),
]


def _safe_file_state(path: Path) -> dict:
    if not path.exists():
        return {'path': str(path), 'exists': False}
    st = path.stat()
    return {'path': str(path), 'exists': True, 'mode': oct(st.st_mode & 0o777), 'bytes': st.st_size}


def run_check(require_keespace: bool = False) -> tuple[int, dict]:
    plaintext = {str(p): assert_no_plaintext_secret_refs(p) for p in CONFIGS if p.exists()}
    workspace_secret_state = [_safe_file_state(p) for p in WORKSPACE_SECRET_FILES]
    root_fallback_state = [_safe_file_state(p) for p in ROOT_FALLBACKS]
    resolution = {}
    for p in CONFIGS:
        try:
            cfg = load_json_config(p)
            resolution[str(p)] = {'ok': True, 'top_level_keys': sorted(cfg.keys())}
        except Exception as exc:
            resolution[str(p)] = {'ok': False, 'error': str(exc).split('\n')[0]}

    db = os.environ.get('KEESPACE_DATABASE') or os.environ.get('KEEPASSXC_DATABASE')
    password_file = os.environ.get('KEESPACE_PASSWORD_FILE') or os.environ.get('KEEPASSXC_PASSWORD_FILE')
    key_file = os.environ.get('KEESPACE_KEY_FILE') or os.environ.get('KEEPASSXC_KEY_FILE')
    keespace_runtime = {
        'mode': secret_mode(),
        'database_set': bool(db),
        'database_exists': bool(db and Path(db).exists()),
        'password_file_set': bool(password_file),
        'password_file_exists': bool(password_file and Path(password_file).exists()),
        'key_file_set': bool(key_file),
        'key_file_exists': bool(key_file and Path(key_file).exists()),
    }

    ok_plaintext = all(not v for v in plaintext.values())
    ok_workspace = all((not s['exists']) or (s.get('bytes') or 0) < 200 for s in workspace_secret_state)
    ok_resolution = all(v['ok'] for v in resolution.values())
    ok_fallback_perms = all((not s['exists']) or s.get('mode') == '0o600' for s in root_fallback_state)
    ok_keespace_runtime = keespace_runtime['database_exists'] and (keespace_runtime['password_file_exists'] or keespace_runtime['key_file_exists'])

    payload = {
        'ok': ok_plaintext and ok_workspace and ok_resolution and ok_fallback_perms and (ok_keespace_runtime if require_keespace else True),
        'require_keespace': require_keespace,
        'plaintext_secret_paths': plaintext,
        'workspace_secret_files': workspace_secret_state,
        'root_fallback_files': root_fallback_state,
        'resolution': resolution,
        'keespace_runtime': keespace_runtime,
    }
    if payload['ok']:
        return 0, payload
    if require_keespace and not ok_keespace_runtime:
        return 2, payload
    return 1, payload


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--require-keespace', action='store_true')
    ap.add_argument('--loop', action='store_true', help='repeat until ok')
    ap.add_argument('--interval', type=int, default=60)
    ap.add_argument('--max-minutes', type=int, default=0, help='0 = no limit')
    args = ap.parse_args()

    started = time.time()
    while True:
        code, payload = run_check(require_keespace=args.require_keespace)
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        if code == 0 or not args.loop:
            return code
        if args.max_minutes and time.time() - started > args.max_minutes * 60:
            return code
        time.sleep(max(args.interval, 5))


if __name__ == '__main__':
    raise SystemExit(main())
