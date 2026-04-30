#!/usr/bin/env python3
"""Validação segura de conexão Apify.

Não imprime token. Resolve credencial via env/fallback/KeeSpace usando secret_config.
"""
from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))

from secret_config import load_json_config, assert_no_plaintext_secret_refs  # noqa: E402


def call_apify(base_url: str, token: str) -> dict:
    req = urllib.request.Request(
        f'{base_url.rstrip("/")}/users/me',
        headers={'Authorization': f'Bearer {token}', 'Accept': 'application/json'},
        method='GET',
    )
    with urllib.request.urlopen(req, timeout=20) as resp:
        return json.loads(resp.read().decode('utf-8'))


def main() -> int:
    ap = argparse.ArgumentParser(description='Checa conexão Apify sem imprimir token.')
    ap.add_argument('--config', default='config/apify.json')
    ap.add_argument('--json', action='store_true')
    args = ap.parse_args()

    plaintext = assert_no_plaintext_secret_refs(args.config)
    if plaintext:
        out = {'ok': False, 'reason': 'plaintext_secret_paths', 'plaintext_secret_paths': plaintext}
        print(json.dumps(out, ensure_ascii=False, indent=2))
        return 2

    try:
        cfg = load_json_config(args.config, resolve=True)
        data = call_apify(cfg['base_url'], cfg['apify_api_token'])
        user = data.get('data') or data
        out = {
            'ok': True,
            'account': {
                'id': user.get('id'),
                'username': user.get('username'),
                'email_present': bool(user.get('email')),
            },
            'token_printed': False,
        }
        print(json.dumps(out, ensure_ascii=False, indent=2))
        return 0
    except RuntimeError as e:
        out = {'ok': False, 'reason': 'secret_not_resolved', 'message': str(e)}
    except urllib.error.HTTPError as e:
        out = {'ok': False, 'reason': 'apify_http_error', 'status': e.code}
    except Exception as e:
        out = {'ok': False, 'reason': type(e).__name__, 'message': str(e)[:300]}
    print(json.dumps(out, ensure_ascii=False, indent=2))
    return 1


if __name__ == '__main__':
    raise SystemExit(main())
