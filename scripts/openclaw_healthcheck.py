#!/usr/bin/env python3
"""Healthcheck operacional padronizado do OpenClaw na VPS.

Gera JSON e Markdown em runtime/health. Exit code:
  0 = OK
  1 = warnings
  2 = critical
"""
from __future__ import annotations

import json
import shutil
import subprocess
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

WORKSPACE = Path('/root/.openclaw/workspace')
OUT_DIR = WORKSPACE / 'runtime/health'
MISSION_HEALTH_URL = 'http://127.0.0.1:3001/api/health'


def run(cmd: list[str], timeout: int = 20) -> tuple[int, str]:
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return proc.returncode, (proc.stdout + proc.stderr).strip()
    except Exception as exc:
        return 99, str(exc)


def check_pm2() -> dict[str, Any]:
    code, out = run(['pm2', 'jlist'])
    if code != 0:
        return {'status': 'critical', 'detail': out[:500]}
    try:
        processes = json.loads(out)
    except Exception as exc:
        return {'status': 'critical', 'detail': f'pm2 json parse failed: {exc}'}
    mission = next((p for p in processes if p.get('name') == 'mission-control'), None)
    if not mission:
        return {'status': 'critical', 'detail': 'mission-control not found in pm2'}
    env = mission.get('pm2_env', {})
    status = env.get('status')
    unstable = env.get('unstable_restarts', 0)
    restarts = env.get('restart_time', 0)
    if status != 'online':
        level = 'critical'
    elif unstable:
        level = 'warning'
    else:
        level = 'ok'
    return {
        'status': level,
        'detail': f'mission-control {status}, restarts={restarts}, unstable={unstable}',
        'restart_time': restarts,
        'unstable_restarts': unstable,
    }


def check_mission_http() -> dict[str, Any]:
    try:
        with urllib.request.urlopen(MISSION_HEALTH_URL, timeout=10) as response:
            body = response.read(4096).decode('utf-8', 'replace')
            level = 'ok' if response.status == 200 else 'critical'
            return {'status': level, 'detail': f'HTTP {response.status}', 'body_sample': body[:500]}
    except Exception as exc:
        return {'status': 'critical', 'detail': str(exc)}


def check_systemd() -> dict[str, Any]:
    code, out = run(['systemctl', '--failed', '--no-pager'])
    if code != 0:
        return {'status': 'warning', 'detail': out[:500]}
    failed_lines = [line for line in out.splitlines() if line.startswith('●')]
    return {
        'status': 'critical' if failed_lines else 'ok',
        'detail': f'{len(failed_lines)} failed units',
        'failed_units': failed_lines,
    }


def check_docker() -> dict[str, Any]:
    code, out = run(['docker', 'ps', '-a', '--format', '{{.Names}}|{{.Status}}'])
    if code != 0:
        return {'status': 'warning', 'detail': out[:500]}
    bad = []
    for line in out.splitlines():
        name, _, status = line.partition('|')
        low = status.lower()
        if 'exited' in low or 'restarting' in low or 'dead' in low or 'unhealthy' in low:
            bad.append({'name': name, 'status': status})
    return {'status': 'critical' if bad else 'ok', 'detail': f'{len(bad)} unhealthy containers', 'bad': bad}


def check_disk() -> dict[str, Any]:
    usage = shutil.disk_usage('/')
    used_pct = round((usage.used / usage.total) * 100, 1)
    if used_pct >= 90:
        level = 'critical'
    elif used_pct >= 80:
        level = 'warning'
    else:
        level = 'ok'
    return {
        'status': level,
        'detail': f'root disk {used_pct}% used',
        'used_pct': used_pct,
        'free_gb': round(usage.free / (1024 ** 3), 1),
    }


def check_logs() -> dict[str, Any]:
    roots = [Path('/root/.pm2/logs'), Path('/root/.openclaw/logs'), WORKSPACE / 'logs/cron', Path('/var/log')]
    large = []
    for root in roots:
        if not root.exists():
            continue
        for path in root.rglob('*'):
            try:
                if path.is_file() and path.stat().st_size > 50 * 1024 * 1024:
                    large.append({'path': str(path), 'size_mb': round(path.stat().st_size / (1024 ** 2), 1)})
            except OSError:
                continue
    return {'status': 'warning' if large else 'ok', 'detail': f'{len(large)} log files >50MB', 'large': large[:20]}


def check_backups() -> dict[str, Any]:
    script = WORKSPACE / 'scripts/backup_retention_b2.py'
    if not script.exists():
        return {'status': 'critical', 'detail': 'backup_retention_b2.py missing'}
    code, out = run(['python3', str(script), '--dry-run'], timeout=90)
    if code != 0:
        return {'status': 'critical', 'detail': out[-1000:]}
    try:
        data = json.loads(out)
    except Exception as exc:
        return {'status': 'critical', 'detail': f'backup dry-run parse failed: {exc}'}
    plan = data.get('plan', {})
    vps_sets = plan.get('remote_vps_sets', [])
    brain_sets = plan.get('remote_2nd_brain_sets', [])
    warnings = []
    if not vps_sets:
        warnings.append('remote vps-full has no complete set yet')
    if len(brain_sets) < 2:
        warnings.append('remote 2nd-brain has fewer than 2 sets')
    return {
        'status': 'warning' if warnings else 'ok',
        'detail': '; '.join(warnings) if warnings else 'backup retention policy satisfied',
        'remote_vps_sets': len(vps_sets),
        'remote_2nd_brain_sets': len(brain_sets),
    }


def worst(checks: dict[str, dict[str, Any]]) -> str:
    statuses = [c['status'] for c in checks.values()]
    if 'critical' in statuses:
        return 'critical'
    if 'warning' in statuses:
        return 'warning'
    return 'ok'


def write_outputs(report: dict[str, Any]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    latest_json = OUT_DIR / 'openclaw-health-latest.json'
    latest_md = OUT_DIR / 'openclaw-health-latest.md'
    latest_json.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    lines = [
        '# OpenClaw Health',
        '',
        f"- Status: `{report['status']}`",
        f"- Timestamp UTC: `{report['timestamp_utc']}`",
        '',
        '## Checks',
        '',
    ]
    for name, check in report['checks'].items():
        lines.append(f"- `{name}`: `{check['status']}` - {check['detail']}")
    latest_md.write_text('\n'.join(lines) + '\n', encoding='utf-8')


def main() -> int:
    checks = {
        'pm2': check_pm2(),
        'mission_http': check_mission_http(),
        'systemd': check_systemd(),
        'docker': check_docker(),
        'disk': check_disk(),
        'logs': check_logs(),
        'backups': check_backups(),
    }
    status = worst(checks)
    report = {
        'status': status,
        'timestamp_utc': datetime.now(timezone.utc).isoformat(),
        'checks': checks,
    }
    write_outputs(report)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 2 if status == 'critical' else 1 if status == 'warning' else 0


if __name__ == '__main__':
    raise SystemExit(main())
