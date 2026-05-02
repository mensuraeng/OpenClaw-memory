#!/usr/bin/env python3
"""Backup criptografado do 2nd-brain para Backblaze B2.

Segredos esperados em arquivo local não versionado:
  /root/.openclaw/workspace/memory/context/backblaze_b2_backup.env

Variáveis:
  B2_KEY_ID=...
  B2_APPLICATION_KEY=...
  B2_BUCKET_NAME=flavia-backups
  BACKUP_PASSPHRASE=frase-longa-aleatoria

Uso:
  python3 scripts/backup_2nd_brain_b2.py --dry-run
  python3 scripts/backup_2nd_brain_b2.py --run
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import json
import os
import shutil
import subprocess
import tarfile
import tempfile
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

WORKSPACE = Path('/root/.openclaw/workspace')
ENV_FILE = WORKSPACE / 'memory/context/backblaze_b2_backup.env'
SOURCE_DIRS = [Path('/root/2nd-brain')]
OUT_DIR = WORKSPACE / 'runtime/backups/2nd-brain'
PREFIX = 'flavia/2nd-brain'


def load_env(path: Path = ENV_FILE) -> dict[str, str]:
    data: dict[str, str] = {}
    if path.exists():
        for raw in path.read_text(encoding='utf-8').splitlines():
            line = raw.strip()
            if not line or line.startswith('#') or '=' not in line:
                continue
            k, v = line.split('=', 1)
            data[k.strip()] = v.strip().strip('"').strip("'")
    for k in ['B2_KEY_ID', 'B2_APPLICATION_KEY', 'B2_BUCKET_NAME', 'BACKUP_PASSPHRASE']:
        if os.getenv(k):
            data[k] = os.getenv(k, '')
    return data


def require_env(env: dict[str, str]) -> None:
    missing = [k for k in ['B2_KEY_ID', 'B2_APPLICATION_KEY', 'B2_BUCKET_NAME', 'BACKUP_PASSPHRASE'] if not env.get(k)]
    if missing:
        raise SystemExit(f'Configuração incompleta. Faltando: {", ".join(missing)} em {ENV_FILE}')


def make_tarball(ts: str) -> Path:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    tar_path = OUT_DIR / f'2nd-brain-{ts}.tar.gz'
    manifest = {
        'created_at_utc': datetime.now(timezone.utc).isoformat(),
        'sources': [str(p) for p in SOURCE_DIRS],
        'host': os.uname().nodename,
        'kind': 'flavia-2nd-brain-backup',
    }
    with tarfile.open(tar_path, 'w:gz') as tar:
        for src in SOURCE_DIRS:
            if src.exists():
                tar.add(src, arcname=src.name)
        info = tarfile.TarInfo('BACKUP-MANIFEST.json')
        payload = json.dumps(manifest, ensure_ascii=False, indent=2).encode('utf-8')
        info.size = len(payload)
        info.mtime = int(time.time())
        tar.addfile(info, fileobj=__import__('io').BytesIO(payload))
    return tar_path


def encrypt_file(src: Path, passphrase: str) -> Path:
    dst = src.with_suffix(src.suffix + '.enc')
    cmd = [
        'openssl', 'enc', '-aes-256-cbc', '-pbkdf2', '-salt',
        '-in', str(src), '-out', str(dst), '-pass', f'pass:{passphrase}'
    ]
    subprocess.run(cmd, check=True)
    return dst


def sha1_file(path: Path) -> str:
    h = hashlib.sha1()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def b2_request(url: str, method='GET', headers=None, body: bytes | None = None) -> dict:
    req = urllib.request.Request(url, data=body, headers=headers or {}, method=method)
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            text = r.read().decode('utf-8', 'replace')
            return json.loads(text) if text else {}
    except urllib.error.HTTPError as e:
        raise RuntimeError(f'B2 HTTP {e.code}: {e.read().decode("utf-8", "replace")[:1000]}')


def authorize(env: dict[str, str]) -> dict:
    token = base64.b64encode(f"{env['B2_KEY_ID']}:{env['B2_APPLICATION_KEY']}".encode()).decode()
    return b2_request('https://api.backblazeb2.com/b2api/v3/b2_authorize_account', headers={'Authorization': 'Basic ' + token})


def find_bucket(auth: dict, bucket_name: str) -> dict:
    body = json.dumps({'accountId': auth['accountId'], 'bucketName': bucket_name}).encode()
    data = b2_request(auth['apiInfo']['storageApi']['apiUrl'] + '/b2api/v3/b2_list_buckets', method='POST', headers={'Authorization': auth['authorizationToken'], 'Content-Type': 'application/json'}, body=body)
    buckets = data.get('buckets', [])
    if not buckets:
        raise RuntimeError(f'Bucket não encontrado ou sem permissão: {bucket_name}')
    return buckets[0]


def upload(auth: dict, bucket_id: str, file_path: Path, remote_name: str) -> dict:
    api = auth['apiInfo']['storageApi']['apiUrl']
    body = json.dumps({'bucketId': bucket_id}).encode()
    up = b2_request(api + '/b2api/v3/b2_get_upload_url', method='POST', headers={'Authorization': auth['authorizationToken'], 'Content-Type': 'application/json'}, body=body)
    data = file_path.read_bytes()
    headers = {
        'Authorization': up['authorizationToken'],
        'X-Bz-File-Name': urllib.request.pathname2url(remote_name),
        'Content-Type': 'application/octet-stream',
        'Content-Length': str(len(data)),
        'X-Bz-Content-Sha1': sha1_file(file_path),
    }
    return b2_request(up['uploadUrl'], method='POST', headers=headers, body=data)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--run', action='store_true', help='Cria, criptografa e envia para B2')
    ap.add_argument('--dry-run', action='store_true', help='Valida configuração sem enviar')
    args = ap.parse_args()

    env = load_env()
    if args.dry_run or not args.run:
        present = {k: bool(env.get(k)) for k in ['B2_KEY_ID', 'B2_APPLICATION_KEY', 'B2_BUCKET_NAME', 'BACKUP_PASSPHRASE']}
        print(json.dumps({'env_file': str(ENV_FILE), 'present': present, 'sources': [str(p) for p in SOURCE_DIRS]}, ensure_ascii=False, indent=2))
        if all(present.values()):
            auth = authorize(env)
            bucket = find_bucket(auth, env['B2_BUCKET_NAME'])
            print(json.dumps({'b2_auth': 'ok', 'bucket': bucket.get('bucketName'), 'bucketId': bucket.get('bucketId')}, ensure_ascii=False, indent=2))
        return 0

    require_env(env)
    ts = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    tar_path = make_tarball(ts)
    enc_path = encrypt_file(tar_path, env['BACKUP_PASSPHRASE'])
    # Segurança operacional: o artefato descriptografado só existe como staging
    # mínimo para criptografia. Depois do .enc gerado, não manter .tar.gz aberto
    # em disco.
    try:
        tar_path.unlink()
    except FileNotFoundError:
        pass
    auth = authorize(env)
    bucket = find_bucket(auth, env['B2_BUCKET_NAME'])
    remote = f'{PREFIX}/{enc_path.name}'
    result = upload(auth, bucket['bucketId'], enc_path, remote)
    print(json.dumps({
        'status': 'uploaded',
        'bucket': env['B2_BUCKET_NAME'],
        'remote': remote,
        'local_encrypted': str(enc_path),
        'size': enc_path.stat().st_size,
        'fileId': result.get('fileId'),
        'sha1': result.get('contentSha1'),
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
