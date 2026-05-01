#!/usr/bin/env python3
"""Health unificado read-only do ecossistema Flávia/OpenClaw.

Não envia mensagem, não move e-mail, não altera sistemas externos.
Gera runtime/operational-health/latest.json com semáforo operacional.
"""
from __future__ import annotations

import base64
import json
import os
import subprocess
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

WORK = Path('/root/.openclaw/workspace')
OUT = WORK / 'runtime/operational-health'
OUT.mkdir(parents=True, exist_ok=True)


def status(name, state, detail=None, evidence=None):
    return {"name": name, "status": state, "detail": detail, "evidence": evidence}


def run(cmd, timeout=30):
    try:
        p = subprocess.run(cmd, cwd=WORK, capture_output=True, text=True, timeout=timeout)
        return p.returncode, (p.stdout or '')[-4000:], (p.stderr or '')[-2000:]
    except subprocess.TimeoutExpired as e:
        return 124, (e.stdout or '')[-1000:] if e.stdout else '', 'timeout'
    except Exception as e:
        return 1, '', str(e)


def graph_check(account, config_path, user):
    rc, out, err = run(['python3', 'scripts/msgraph_email.py', 'list', '--account', account, '--user', user, '--limit', '1'], timeout=45)
    return status(f'graph_email_{account}', 'ok' if rc == 0 and ('📧' in out or '📩' in out) else 'fail', detail=(err or out[:300]), evidence=user)


def b2_check():
    env_path = WORK / 'memory/context/backblaze_b2_backup.env'
    if not env_path.exists():
        return status('backblaze_b2', 'blocked', 'env ausente')
    env = {}
    for line in env_path.read_text(encoding='utf-8').splitlines():
        if '=' in line and not line.strip().startswith('#'):
            k, v = line.split('=', 1)
            env[k.strip()] = v.strip().strip('"').strip("'")
    missing = [k for k in ['B2_KEY_ID', 'B2_APPLICATION_KEY', 'B2_BUCKET_NAME'] if not env.get(k)]
    if missing:
        return status('backblaze_b2', 'blocked', 'missing ' + ','.join(missing))
    try:
        cred = base64.b64encode(f"{env['B2_KEY_ID']}:{env['B2_APPLICATION_KEY']}".encode()).decode()
        req = urllib.request.Request('https://api.backblazeb2.com/b2api/v3/b2_authorize_account', headers={'Authorization': 'Basic ' + cred})
        with urllib.request.urlopen(req, timeout=30) as r:
            auth = json.load(r)
        return status('backblaze_b2', 'ok', f"bucket alvo {env['B2_BUCKET_NAME']}", evidence=auth.get('accountId'))
    except Exception as e:
        return status('backblaze_b2', 'fail', str(e)[:500])


def linkedin_community_check():
    latest = WORK / 'runtime/linkedin-institutional/community-api-email-check-latest.json'
    if latest.exists():
        try:
            data = json.loads(latest.read_text(encoding='utf-8'))
            state = data.get('status', 'unknown')
            mapped = 'ok' if state == 'approval_found' else 'pending' if state == 'no_approval_found' else 'attention'
            return status('linkedin_institutional_community_api', mapped, state, evidence=data.get('checked_at_utc'))
        except Exception as e:
            return status('linkedin_institutional_community_api', 'fail', str(e))
    return status('linkedin_institutional_community_api', 'pending', 'sem latest; monitor ainda não gerou estado')


def file_exists_check(name, path, ok_status='ok', missing_status='attention'):
    p = WORK / path if not str(path).startswith('/') else Path(path)
    return status(name, ok_status if p.exists() else missing_status, str(p))


def backup_processes():
    matches = []
    proc = Path('/proc')
    for child in proc.iterdir():
        if not child.name.isdigit():
            continue
        try:
            raw = (child / 'cmdline').read_bytes()
        except Exception:
            continue
        if not raw:
            continue
        args = [part.decode('utf-8', 'replace') for part in raw.split(b'\0') if part]
        joined = ' '.join(args)
        if 'backup_vps_full_b2_stream.py' in joined and '--run' in args:
            matches.append(f"{child.name} {joined}")
    return matches


def backup_runtime_check():
    tmp = WORK / 'runtime/backups/vps-full-stream-tmp'
    manifests = WORK / 'runtime/backups/vps-full-manifests'
    parts = list(tmp.glob('*')) if tmp.exists() else []
    recent_manifests = sorted(manifests.glob('*.manifest.json'), key=lambda p: p.stat().st_mtime, reverse=True) if manifests.exists() else []
    running = backup_processes()
    if running:
        return status('vps_full_backup', 'running', f'{len(parts)} parte(s) temporária(s)', evidence='\n'.join(running)[:500])
    if parts:
        return status('vps_full_backup', 'attention', f'{len(parts)} parte(s) temporária(s) sem processo ativo')
    if recent_manifests:
        return status('vps_full_backup', 'ok', 'manifesto local encontrado', evidence=str(recent_manifests[0]))
    return status('vps_full_backup', 'pending', 'sem manifesto full local ainda')


def cron_health_hint():
    rc, out, err = run(['bash', '-lc', 'openclaw status 2>/dev/null | head -80'], timeout=90)
    if rc == 0:
        return status('openclaw_status', 'ok', 'status executado', evidence=out[:1000])
    return status('openclaw_status', 'attention', err or out[:500])


def main():
    checks = []
    checks.append(cron_health_hint())
    checks.append(graph_check('mensura', 'config/ms-graph.json', 'alexandre@mensuraengenharia.com.br'))
    checks.append(graph_check('mia', 'config/ms-graph-mia.json', 'alexandre@miaengenharia.com.br'))
    checks.append(graph_check('pcs', 'config/ms-graph-pcs.json', 'alexandre@pcsengenharia.com.br'))
    checks.append(graph_check('mensura', 'config/ms-graph.json', 'flavia@mensuraengenharia.com.br'))
    checks.append(b2_check())
    checks.append(backup_runtime_check())
    checks.append(linkedin_community_check())
    checks.append(file_exists_check('working_queue_flavia', '/root/2nd-brain/06-agents/flavia/WORKING.md'))
    checks.append(file_exists_check('authority_matrix', 'docs/operacao/MATRIZ-DE-AUTORIDADE-INTEGRACOES.md'))
    checks.append(file_exists_check('data_trust_rules', 'docs/operacao/REGRAS-DE-DADOS-E-CONFIANCA.md'))
    checks.append(file_exists_check('operating_loops', 'docs/operacao/OPERATING-LOOPS.md'))

    counts = {}
    for c in checks:
        counts[c['status']] = counts.get(c['status'], 0) + 1
    overall = 'ok'
    if counts.get('fail'):
        overall = 'fail'
    elif counts.get('attention'):
        overall = 'attention'
    elif counts.get('blocked'):
        overall = 'blocked'
    elif counts.get('running') or counts.get('pending'):
        overall = 'active'

    result = {
        'checked_at_utc': datetime.now(timezone.utc).isoformat(),
        'overall': overall,
        'counts': counts,
        'checks': checks,
    }
    (OUT / 'latest.json').write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    (OUT / f'health-{stamp}.json').write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
