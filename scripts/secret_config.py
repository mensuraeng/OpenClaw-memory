#!/usr/bin/env python3
"""Secret/config resolver for OpenClaw local automations.

Policy:
- Repository/workspace configs should store references, not secret values.
- Runtime may resolve from process env or a root-owned env file during migration.
- KeeSpace/KeePassXC is supported when the vault is unlocked/provided through env.

This module never prints secret values.
"""
from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path
from typing import Any

WORKSPACE = Path(__file__).resolve().parents[1]
DEFAULT_ENV_FILES = [
    Path('/root/.secrets/openclaw-commercial.env'),
    Path('/root/.secrets/openclaw.env'),
    Path('/root/.secrets/notion.env'),
]

_ENV_LOADED = False


def load_env_files(paths: list[Path] | None = None) -> None:
    global _ENV_LOADED
    if _ENV_LOADED:
        return
    for path in paths or DEFAULT_ENV_FILES:
        if not path.exists():
            continue
        for raw in path.read_text(encoding='utf-8').splitlines():
            line = raw.strip()
            if not line or line.startswith('#') or '=' not in line:
                continue
            key, value = line.split('=', 1)
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            os.environ.setdefault(key, value)
    _ENV_LOADED = True


def _resolve_keepassxc(ref: dict[str, Any]) -> str | None:
    """Resolve a KeePassXC/KeeSpace entry when env grants access.

    Expected env:
    - KEEPASSXC_DATABASE=/path/to/vault.kdbx or KEESPACE_DATABASE=...
    - optional KEEPASSXC_KEY_FILE=/path/to/keyfile
    - optional KEEPASSXC_PASSWORD_FILE=/path/to/password-file

    The entry path is passed by ref['keespace'] or ref['keepassxc'].
    Attribute defaults to password.
    """
    entry = ref.get('keespace') or ref.get('keepassxc')
    if not entry:
        return None
    db = os.environ.get('KEEPASSXC_DATABASE') or os.environ.get('KEESPACE_DATABASE')
    if not db:
        return None
    cmd = ['keepassxc-cli', 'show', '--quiet']
    key_file = os.environ.get('KEEPASSXC_KEY_FILE') or os.environ.get('KEESPACE_KEY_FILE')
    if key_file:
        cmd += ['--key-file', key_file]
    attr = ref.get('attribute') or 'password'
    cmd += ['--attributes', attr, db, entry]
    try:
        password_file = os.environ.get('KEEPASSXC_PASSWORD_FILE') or os.environ.get('KEESPACE_PASSWORD_FILE')
        stdin = Path(password_file).read_text(encoding='utf-8') if password_file else ''
        cp = subprocess.run(cmd, input=stdin, text=True, capture_output=True, timeout=15)
        if cp.returncode == 0:
            value = cp.stdout.strip().splitlines()[-1].strip() if cp.stdout.strip() else ''
            return value or None
    except Exception:
        return None
    return None


def resolve_secret_ref(value: Any, *, name: str = 'secret', required: bool = True) -> Any:
    load_env_files()
    if isinstance(value, dict):
        if 'env' in value:
            env_name = str(value['env'])
            resolved = os.environ.get(env_name)
            if resolved:
                return resolved
        if 'file' in value:
            p = Path(str(value['file'])).expanduser()
            if p.exists():
                return p.read_text(encoding='utf-8').strip()
        resolved = _resolve_keepassxc(value)
        if resolved:
            return resolved
        if required:
            refs = ', '.join(f'{k}={v}' for k, v in value.items() if k in {'env', 'file', 'keespace', 'keepassxc'})
            raise RuntimeError(f'Segredo não resolvido: {name} ({refs})')
        return None
    if isinstance(value, str) and value.startswith('env:'):
        env_name = value.split(':', 1)[1]
        resolved = os.environ.get(env_name)
        if resolved:
            return resolved
        if required:
            raise RuntimeError(f'Segredo não resolvido: {name} (env={env_name})')
        return None
    return value


def _walk_resolve(obj: Any, path: str = '') -> Any:
    if isinstance(obj, dict):
        keys = set(obj)
        if keys & {'env', 'file', 'keespace', 'keepassxc'}:
            return resolve_secret_ref(obj, name=path or 'secret')
        return {k: _walk_resolve(v, f'{path}.{k}' if path else k) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_walk_resolve(v, f'{path}[{i}]') for i, v in enumerate(obj)]
    if isinstance(obj, str) and obj.startswith('env:'):
        return resolve_secret_ref(obj, name=path or 'secret')
    return obj


def load_json_config(path: str | Path, *, resolve: bool = True) -> dict[str, Any]:
    p = Path(path)
    data = json.loads(p.read_text(encoding='utf-8'))
    return _walk_resolve(data) if resolve else data


def assert_no_plaintext_secret_refs(path: str | Path) -> list[str]:
    """Return suspicious plaintext secret paths in a JSON config."""
    data = load_json_config(path, resolve=False)
    suspicious: list[str] = []
    secret_keys = {'token', 'accesstoken', 'apikey', 'api_key', 'webhook', 'secret', 'password'}

    def walk(x: Any, prefix: str = '') -> None:
        if isinstance(x, dict):
            for k, v in x.items():
                p = f'{prefix}.{k}' if prefix else k
                lk = k.lower()
                if any(s in lk for s in secret_keys) and isinstance(v, str) and v and not v.startswith('env:'):
                    suspicious.append(p)
                walk(v, p)
        elif isinstance(x, list):
            for i, v in enumerate(x):
                walk(v, f'{prefix}[{i}]')

    walk(data)
    return suspicious


if __name__ == '__main__':
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument('config')
    ap.add_argument('--check', action='store_true')
    args = ap.parse_args()
    if args.check:
        bad = assert_no_plaintext_secret_refs(args.config)
        print(json.dumps({'config': args.config, 'plaintext_secret_paths': bad, 'ok': not bad}, ensure_ascii=False, indent=2))
    else:
        cfg = load_json_config(args.config)
        print(json.dumps({'config': args.config, 'resolved': True, 'top_level_keys': sorted(cfg)}, ensure_ascii=False, indent=2))
