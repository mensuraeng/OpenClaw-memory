#!/usr/bin/env python3
"""Backup full da VPS para Backblaze B2 sem acumular staging local.

Fluxo: tar -> openssl -> partes temporárias -> upload B2 -> apagar parte local.
Mantém localmente apenas manifest/log pequeno. O restore baixa as partes do B2 e concatena.
"""
from __future__ import annotations

import argparse, base64, hashlib, json, os, subprocess, time, urllib.error, urllib.parse, urllib.request
from datetime import datetime, timezone
from pathlib import Path

WORKSPACE = Path('/root/.openclaw/workspace')
ENV_FILE = WORKSPACE / 'memory/context/backblaze_b2_backup.env'
TMP_DIR = WORKSPACE / 'runtime/backups/vps-full-stream-tmp'
MANIFEST_DIR = WORKSPACE / 'runtime/backups/vps-full-manifests'
PREFIX = 'flavia/vps-full'
PART_BYTES = 256 * 1024 * 1024  # 256 MiB; reduz risco de queda TLS em upload longo
UPLOAD_RETRIES = 5
SOURCES = ['/root', '/etc', '/home', '/var', '/opt', '/usr/local', '/srv']
EXCLUDES = [
    '/proc', '/sys', '/dev', '/run', '/tmp', '/mnt', '/media', '/lost+found',
    '/root/.cache', '/root/.npm', '/root/.local/share/Trash',
    '/root/openclaw-backups',
    '/root/.openclaw/workspace/runtime/backups',
    '/root/.openclaw/workspace/tmp',
    '/var/cache', '/var/tmp', '/var/log/journal',
]


def load_env():
    env={}
    for line in ENV_FILE.read_text(encoding='utf-8').splitlines():
        if '=' in line and not line.strip().startswith('#'):
            k,v=line.split('=',1); env[k.strip()]=v.strip().strip('"').strip("'")
    return env

def require_env(env):
    missing=[k for k in ['B2_KEY_ID','B2_APPLICATION_KEY','B2_BUCKET_NAME','BACKUP_PASSPHRASE'] if not env.get(k)]
    if missing: raise SystemExit('Faltando: '+', '.join(missing))

def req_json(url, method='GET', headers=None, body=None, timeout=180):
    req=urllib.request.Request(url, data=body, headers=headers or {}, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            text=r.read().decode('utf-8','replace')
            return json.loads(text) if text else {}
    except urllib.error.HTTPError as e:
        raise RuntimeError(f'B2 HTTP {e.code}: {e.read().decode("utf-8","replace")[:1000]}')

def authorize(env):
    token=base64.b64encode(f"{env['B2_KEY_ID']}:{env['B2_APPLICATION_KEY']}".encode()).decode()
    return req_json('https://api.backblazeb2.com/b2api/v3/b2_authorize_account', headers={'Authorization':'Basic '+token})

def bucket(auth, name):
    body=json.dumps({'accountId':auth['accountId'],'bucketName':name}).encode()
    data=req_json(auth['apiInfo']['storageApi']['apiUrl']+'/b2api/v3/b2_list_buckets', method='POST', headers={'Authorization':auth['authorizationToken'],'Content-Type':'application/json'}, body=body)
    if not data.get('buckets'): raise RuntimeError('Bucket não encontrado: '+name)
    return data['buckets'][0]

def sha1_file(p: Path):
    h=hashlib.sha1()
    with p.open('rb') as f:
        for chunk in iter(lambda:f.read(1024*1024), b''): h.update(chunk)
    return h.hexdigest()

def upload_one(auth, bucket_id, path: Path, remote: str):
    api=auth['apiInfo']['storageApi']['apiUrl']
    last_err=None
    file_sha1=sha1_file(path)
    for attempt in range(1, UPLOAD_RETRIES + 1):
        try:
            up=req_json(api+'/b2api/v3/b2_get_upload_url', method='POST', headers={'Authorization':auth['authorizationToken'],'Content-Type':'application/json'}, body=json.dumps({'bucketId':bucket_id}).encode())
            headers={
                'Authorization':up['authorizationToken'],
                'X-Bz-File-Name':urllib.parse.quote(remote, safe='/'),
                'Content-Type':'application/octet-stream',
                'Content-Length':str(path.stat().st_size),
                'X-Bz-Content-Sha1':file_sha1,
            }
            with path.open('rb') as f:
                request=urllib.request.Request(up['uploadUrl'], data=f, headers=headers, method='POST')
                with urllib.request.urlopen(request, timeout=3600) as r:
                    text=r.read().decode('utf-8','replace')
                    return json.loads(text) if text else {}
        except Exception as e:
            last_err=e
            wait=min(60, 5 * attempt)
            print(json.dumps({'upload_retry':attempt,'remote':remote,'error':str(e),'wait_seconds':wait}, ensure_ascii=False), flush=True)
            time.sleep(wait)
    raise RuntimeError(f'Falha ao subir {remote} após {UPLOAD_RETRIES} tentativas: {last_err}')

def existing_sources(): return [s for s in SOURCES if Path(s).exists()]

def du_quick():
    r=subprocess.run(['timeout','30','du','-sh']+existing_sources(), capture_output=True, text=True)
    return r.stdout.strip() if r.returncode != 124 else 'estimativa interrompida após 30s'

def cleanup_tmp():
    TMP_DIR.mkdir(parents=True, exist_ok=True)
    for p in TMP_DIR.glob('*'):
        if p.is_file(): p.unlink()

def stream_backup(env):
    cleanup_tmp(); MANIFEST_DIR.mkdir(parents=True, exist_ok=True)
    ts=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    auth=authorize(env); b=bucket(auth, env['B2_BUCKET_NAME'])
    tar_cmd=['tar','--warning=no-file-changed','--ignore-failed-read','-czf','-']
    for ex in EXCLUDES: tar_cmd += ['--exclude', ex]
    tar_cmd += existing_sources()
    proc_env=os.environ.copy(); proc_env['BACKUP_PASSPHRASE']=env['BACKUP_PASSPHRASE']
    p1=subprocess.Popen(tar_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    p2=subprocess.Popen(['openssl','enc','-aes-256-cbc','-pbkdf2','-salt','-pass','env:BACKUP_PASSPHRASE'], stdin=p1.stdout, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=proc_env)
    assert p1.stdout and p2.stdout
    p1.stdout.close()
    parts=[]; idx=0
    try:
        while True:
            chunk=p2.stdout.read(PART_BYTES)
            if not chunk: break
            idx += 1
            part=TMP_DIR / f'vps-full-{ts}.tar.gz.enc.part-{idx:05d}'
            part.write_bytes(chunk)
            remote=f'{PREFIX}/{ts}/{part.name}'
            res=upload_one(auth, b['bucketId'], part, remote)
            item={'name':part.name,'remote':remote,'size':part.stat().st_size,'sha1':sha1_file(part),'fileId':res.get('fileId')}
            parts.append(item)
            print(json.dumps({'uploaded_part':idx,'remote':remote,'size':item['size']}, ensure_ascii=False), flush=True)
            part.unlink()
    finally:
        if p2.stdout: p2.stdout.close()
    e2=p2.stderr.read().decode('utf-8','replace') if p2.stderr else ''
    rc2=p2.wait()
    e1=p1.stderr.read().decode('utf-8','replace') if p1.stderr else ''
    rc1=p1.wait()
    if rc1 not in (0,1) or rc2 != 0:
        raise RuntimeError(f'pipeline failed tar={rc1} openssl={rc2}\nTAR:{e1[-2000:]}\nOPENSSL:{e2[-1000:]}')
    manifest={'created_at_utc':datetime.now(timezone.utc).isoformat(),'kind':'flavia-vps-full-stream-backup','host':os.uname().nodename,'sources':existing_sources(),'excludes':EXCLUDES,'part_bytes':PART_BYTES,'bucket':env['B2_BUCKET_NAME'],'prefix':f'{PREFIX}/{ts}/','parts':parts,'restore_hint':'Baixar as partes em ordem; cat part-* > backup.tar.gz.enc; openssl enc -d -aes-256-cbc -pbkdf2 -in backup.tar.gz.enc -out backup.tar.gz; tar -xzf backup.tar.gz -C /restore/path'}
    manifest_path=MANIFEST_DIR / f'vps-full-{ts}.manifest.json'
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')
    remote_manifest=f'{PREFIX}/{ts}/{manifest_path.name}'
    res=upload_one(auth, b['bucketId'], manifest_path, remote_manifest)
    print(json.dumps({'status':'uploaded','bucket':env['B2_BUCKET_NAME'],'set':f'{PREFIX}/{ts}/','parts':len(parts),'manifest_remote':remote_manifest,'local_kept':'manifest only','local_manifest':str(manifest_path)}, ensure_ascii=False, indent=2))

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--run', action='store_true'); ap.add_argument('--dry-run', action='store_true')
    args=ap.parse_args(); env=load_env(); require_env(env)
    if args.dry_run or not args.run:
        auth=authorize(env); b=bucket(auth, env['B2_BUCKET_NAME'])
        print(json.dumps({'mode':'dry-run','bucket':b['bucketName'],'sources':existing_sources(),'excludes':EXCLUDES,'part_bytes':PART_BYTES,'local_policy':'sem backup full acumulado na VPS; só parte temporária + manifest pequeno','du':du_quick()}, ensure_ascii=False, indent=2)); return
    stream_backup(env)
if __name__=='__main__': main()
