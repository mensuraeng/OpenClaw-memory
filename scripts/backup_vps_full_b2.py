#!/usr/bin/env python3
"""Backup criptografado da VPS persistente para Backblaze B2, em partes.

Usa as mesmas credenciais locais do backup do 2nd-brain:
  /root/.openclaw/workspace/memory/context/backblaze_b2_backup.env

Escopo: backup de sistema persistente, não snapshot de kernel/runtime.
Inclui: /root, /etc, /home, /var, /opt, /usr/local, /srv
Exclui diretórios virtuais/cache temporário para evitar recursão e lixo não restaurável.

Uso:
  python3 scripts/backup_vps_full_b2.py --dry-run
  python3 scripts/backup_vps_full_b2.py --run
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import json
import os
import subprocess
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

WORKSPACE = Path('/root/.openclaw/workspace')
ENV_FILE = WORKSPACE / 'memory/context/backblaze_b2_backup.env'
OUT_DIR = WORKSPACE / 'runtime/backups/vps-full'
MANIFEST_DIR = WORKSPACE / 'runtime/backups/vps-full-manifests'
PREFIX = 'flavia/vps-full'
PART_BYTES = 1024 * 1024 * 1024  # 1 GiB chunks; safe for simple B2 uploads
KEEP_LOCAL_SETS = 0  # backup full fica na nuvem; local mantém só manifesto pequeno
SOURCES = ['/root', '/etc', '/home', '/var', '/opt', '/usr/local', '/srv']
EXCLUDES = [
    '/proc', '/sys', '/dev', '/run', '/tmp', '/mnt', '/media', '/lost+found',
    '/root/.cache', '/root/.npm', '/root/.local/share/Trash',
    '/root/.openclaw/workspace/runtime/backups',
    '/root/.openclaw/workspace/tmp',
    '/var/cache', '/var/tmp', '/var/log/journal',
]


def load_env(path: Path = ENV_FILE) -> dict[str, str]:
    data: dict[str, str] = {}
    for raw in path.read_text(encoding='utf-8').splitlines():
        line = raw.strip()
        if not line or line.startswith('#') or '=' not in line:
            continue
        k, v = line.split('=', 1)
        data[k.strip()] = v.strip().strip('"').strip("'")
    return data


def require_env(env: dict[str, str]) -> None:
    missing = [k for k in ['B2_KEY_ID', 'B2_APPLICATION_KEY', 'B2_BUCKET_NAME', 'BACKUP_PASSPHRASE'] if not env.get(k)]
    if missing:
        raise SystemExit(f'Configuração incompleta. Faltando: {", ".join(missing)} em {ENV_FILE}')


def run(cmd: list[str], **kw):
    return subprocess.run(cmd, check=True, text=True, **kw)


def existing_sources() -> list[str]:
    return [s for s in SOURCES if Path(s).exists()]


def du_summary() -> str:
    # Bounded estimate. Full du over /root can take several minutes because of venvs/repos.
    cmd = ['timeout', '45', 'du', '-sh'] + existing_sources()
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode == 124:
        return 'estimativa interrompida após 45s; backup ainda pode rodar normalmente'
    return r.stdout.strip()


def create_encrypted_parts(ts: str) -> list[Path]:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    base = OUT_DIR / f'vps-full-{ts}.tar.gz.enc.part-'
    tar_cmd = ['tar', '--warning=no-file-changed', '--ignore-failed-read', '-czf', '-']
    for ex in EXCLUDES:
        tar_cmd += ['--exclude', ex]
    tar_cmd += existing_sources()
    openssl_cmd = ['openssl', 'enc', '-aes-256-cbc', '-pbkdf2', '-salt', '-pass', f"file:{ENV_FILE}"]
    # openssl cannot read only BACKUP_PASSPHRASE from env file, so pass via env var instead.
    # Use shell-free pipeline to avoid echoing the secret.
    env = os.environ.copy()
    env['BACKUP_PASSPHRASE'] = load_env()['BACKUP_PASSPHRASE']
    openssl_cmd = ['openssl', 'enc', '-aes-256-cbc', '-pbkdf2', '-salt', '-pass', 'env:BACKUP_PASSPHRASE']
    split_cmd = ['split', '-b', str(PART_BYTES), '-', str(base)]
    p1 = subprocess.Popen(tar_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    p2 = subprocess.Popen(openssl_cmd, stdin=p1.stdout, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env)
    assert p1.stdout is not None
    p1.stdout.close()
    p3 = subprocess.Popen(split_cmd, stdin=p2.stdout, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    assert p2.stdout is not None
    p2.stdout.close()
    _, e3 = p3.communicate()
    e1 = p1.stderr.read().decode('utf-8', 'replace') if p1.stderr else ''
    e2 = p2.stderr.read().decode('utf-8', 'replace') if p2.stderr else ''
    rc1 = p1.wait(); rc2 = p2.wait(); rc3 = p3.returncode
    # tar may return 1 if files changed during read; acceptable for live backup, but not 2+.
    if rc1 not in (0, 1) or rc2 != 0 or rc3 != 0:
        raise RuntimeError(f'pipeline failed tar={rc1} openssl={rc2} split={rc3}\nTAR:{e1[-2000:]}\nOPENSSL:{e2[-1000:]}\nSPLIT:{e3.decode("utf-8", "replace")[-1000:]}')
    parts = sorted(OUT_DIR.glob(f'vps-full-{ts}.tar.gz.enc.part-*'))
    if not parts:
        raise RuntimeError('Nenhuma parte gerada')
    manifest = {
        'created_at_utc': datetime.now(timezone.utc).isoformat(),
        'kind': 'flavia-vps-full-backup',
        'host': os.uname().nodename,
        'sources': existing_sources(),
        'excludes': EXCLUDES,
        'part_bytes': PART_BYTES,
        'parts': [{'name': p.name, 'size': p.stat().st_size, 'sha1': sha1_file(p)} for p in parts],
        'restore_hint': 'Baixar manifest + partes em ordem, concatenar: cat part-* > backup.tar.gz.enc; descriptografar com openssl enc -d -aes-256-cbc -pbkdf2 -in backup.tar.gz.enc -out backup.tar.gz; extrair com tar -xzf backup.tar.gz -C /restore/path',
    }
    manifest_path = OUT_DIR / f'vps-full-{ts}.manifest.json'
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')
    return [manifest_path] + parts


def sha1_file(path: Path) -> str:
    h = hashlib.sha1()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def b2_request(url: str, method='GET', headers=None, body=None) -> dict:
    req = urllib.request.Request(url, data=body, headers=headers or {}, method=method)
    try:
        with urllib.request.urlopen(req, timeout=180) as r:
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


def upload_one(auth: dict, bucket_id: str, file_path: Path, remote_name: str) -> dict:
    api = auth['apiInfo']['storageApi']['apiUrl']
    body = json.dumps({'bucketId': bucket_id}).encode()
    up = b2_request(api + '/b2api/v3/b2_get_upload_url', method='POST', headers={'Authorization': auth['authorizationToken'], 'Content-Type': 'application/json'}, body=body)
    size = file_path.stat().st_size
    headers = {
        'Authorization': up['authorizationToken'],
        'X-Bz-File-Name': urllib.parse.quote(remote_name, safe='/'),
        'Content-Type': 'application/octet-stream',
        'Content-Length': str(size),
        'X-Bz-Content-Sha1': sha1_file(file_path),
    }
    with file_path.open('rb') as f:
        req = urllib.request.Request(up['uploadUrl'], data=f, headers=headers, method='POST')
        with urllib.request.urlopen(req, timeout=3600) as r:
            text = r.read().decode('utf-8', 'replace')
            return json.loads(text) if text else {}


def part_name(index: int) -> str:
    return f'part-{index:04d}'


def create_upload_encrypted_parts(ts: str, auth: dict, bucket_id: str) -> tuple[Path, list[dict]]:
    """Cria o backup criptografado e envia parte por parte ao B2.

    A versão anterior gerava todas as partes localmente antes do upload. Em VPS
    pequena isso lota o disco. Aqui só uma parte de até PART_BYTES existe em
    disco por vez; depois do upload, ela é removida.
    """
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    MANIFEST_DIR.mkdir(parents=True, exist_ok=True)
    tar_cmd = ['tar', '--warning=no-file-changed', '--ignore-failed-read', '-czf', '-']
    for ex in EXCLUDES:
        tar_cmd += ['--exclude', ex]
    tar_cmd += existing_sources()

    env = os.environ.copy()
    env['BACKUP_PASSPHRASE'] = load_env()['BACKUP_PASSPHRASE']
    openssl_cmd = ['openssl', 'enc', '-aes-256-cbc', '-pbkdf2', '-salt', '-pass', 'env:BACKUP_PASSPHRASE']

    p1 = subprocess.Popen(tar_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    p2 = subprocess.Popen(openssl_cmd, stdin=p1.stdout, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env)
    assert p1.stdout is not None
    p1.stdout.close()
    assert p2.stdout is not None

    uploaded: list[dict] = []
    index = 0
    try:
        while True:
            suffix = part_name(index)
            local_part = OUT_DIR / f'vps-full-{ts}.tar.gz.enc.{suffix}'
            h = hashlib.sha1()
            size = 0
            with local_part.open('wb') as f:
                while size < PART_BYTES:
                    chunk = p2.stdout.read(min(8 * 1024 * 1024, PART_BYTES - size))
                    if not chunk:
                        break
                    f.write(chunk)
                    h.update(chunk)
                    size += len(chunk)
            if size == 0:
                local_part.unlink(missing_ok=True)
                break
            remote = f'{PREFIX}/{ts}/{local_part.name}'
            res = upload_one(auth, bucket_id, local_part, remote)
            uploaded.append({
                'name': local_part.name,
                'remote': remote,
                'size': size,
                'sha1': h.hexdigest(),
                'fileId': res.get('fileId'),
                'contentSha1': res.get('contentSha1'),
            })
            print(json.dumps({'uploaded': remote, 'size': size}, ensure_ascii=False), flush=True)
            local_part.unlink(missing_ok=True)
            index += 1
    finally:
        p2.stdout.close()

    e1 = p1.stderr.read().decode('utf-8', 'replace') if p1.stderr else ''
    e2 = p2.stderr.read().decode('utf-8', 'replace') if p2.stderr else ''
    rc2 = p2.wait()
    rc1 = p1.wait()
    # tar may return 1 if files changed during read; acceptable for live backup, but not 2+.
    if rc1 not in (0, 1) or rc2 != 0:
        raise RuntimeError(f'pipeline failed tar={rc1} openssl={rc2}\nTAR:{e1[-2000:]}\nOPENSSL:{e2[-1000:]}')
    if not uploaded:
        raise RuntimeError('Nenhuma parte enviada')

    manifest = {
        'created_at_utc': datetime.now(timezone.utc).isoformat(),
        'kind': 'flavia-vps-full-backup',
        'storage': 'backblaze-b2-cloud-first',
        'host': os.uname().nodename,
        'sources': existing_sources(),
        'excludes': EXCLUDES,
        'part_bytes': PART_BYTES,
        'parts': uploaded,
        'restore_hint': 'Baixar manifest + partes em ordem, concatenar: cat part-* > backup.tar.gz.enc; descriptografar com openssl enc -d -aes-256-cbc -pbkdf2 -in backup.tar.gz.enc -out backup.tar.gz; extrair com tar -xzf backup.tar.gz -C /restore/path',
    }
    manifest_path = MANIFEST_DIR / f'vps-full-{ts}.manifest.json'
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')
    manifest_remote = f'{PREFIX}/{ts}/{manifest_path.name}'
    manifest_res = upload_one(auth, bucket_id, manifest_path, manifest_remote)
    uploaded.insert(0, {'name': manifest_path.name, 'remote': manifest_remote, 'size': manifest_path.stat().st_size, 'fileId': manifest_res.get('fileId'), 'contentSha1': manifest_res.get('contentSha1')})
    print(json.dumps({'uploaded': manifest_remote, 'size': manifest_path.stat().st_size}, ensure_ascii=False), flush=True)
    return manifest_path, uploaded


def cleanup_local_sets(keep: int = KEEP_LOCAL_SETS) -> list[str]:
    """Remove conjuntos locais antigos depois de upload bem-sucedido."""
    if not OUT_DIR.exists():
        return []
    groups: dict[str, list[Path]] = {}
    for p in OUT_DIR.glob('vps-full-*'):
        name = p.name
        if name.endswith('.manifest.json'):
            ts = name.removeprefix('vps-full-').removesuffix('.manifest.json')
        elif '.tar.gz.enc.part-' in name:
            ts = name.removeprefix('vps-full-').split('.tar.gz.enc.part-', 1)[0]
        else:
            continue
        groups.setdefault(ts, []).append(p)
    timestamps = sorted(groups.keys(), reverse=True)
    removed: list[str] = []
    for ts in timestamps[keep:]:
        for p in groups[ts]:
            try:
                p.unlink()
                removed.append(str(p))
            except FileNotFoundError:
                pass
    return removed


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--run', action='store_true')
    ap.add_argument('--dry-run', action='store_true')
    args = ap.parse_args()
    env = load_env()
    require_env(env)
    if args.dry_run or not args.run:
        auth = authorize(env)
        bucket = find_bucket(auth, env['B2_BUCKET_NAME'])
        print(json.dumps({
            'mode': 'dry-run',
            'bucket': bucket.get('bucketName'),
            'sources': existing_sources(),
            'excludes': EXCLUDES,
            'du': du_summary(),
            'local_retention_sets': KEEP_LOCAL_SETS,
            'note': 'Backup full será criptografado, dividido em partes de 1GiB, enviado ao B2 em modo cloud-first e a VPS manterá localmente apenas manifestos pequenos.'
        }, ensure_ascii=False, indent=2))
        return 0
    ts = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    auth = authorize(env)
    bucket = find_bucket(auth, env['B2_BUCKET_NAME'])
    manifest_path, uploaded = create_upload_encrypted_parts(ts, auth, bucket['bucketId'])
    removed_local = cleanup_local_sets(KEEP_LOCAL_SETS)
    print(json.dumps({'status': 'uploaded', 'bucket': env['B2_BUCKET_NAME'], 'set': f'{PREFIX}/{ts}/', 'local_manifest': str(manifest_path), 'local_retention_sets': KEEP_LOCAL_SETS, 'removed_local_old_files': len(removed_local), 'files': uploaded}, ensure_ascii=False, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
