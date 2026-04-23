#!/usr/bin/env python3
import argparse
import datetime as dt
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path('/root/.openclaw/workspace')
NOTEBOOKLM = Path('/root/.openclaw/venvs/notebooklm/bin/notebooklm')
STATE_DIR = ROOT / 'tools' / 'notebooklm-sync' / 'state'
OUTBOX = ROOT / 'tools' / 'notebooklm-sync' / 'outbox'
MEMORY_DAY = ROOT / 'memory' / '2026-04-20.md'
SNAPSHOT = STATE_DIR / 'last_notebooks.json'
REPORT = OUTBOX / 'last_sync_report.md'


def run_cmd(args):
    return subprocess.run(args, capture_output=True, text=True)


def now_local():
    return dt.datetime.now().astimezone()


def ensure_dirs():
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    OUTBOX.mkdir(parents=True, exist_ok=True)


def notebooklm_json_list():
    result = run_cmd([str(NOTEBOOKLM), 'list', '--help'])
    if result.returncode != 0:
        return None
    return True


def list_notebooks():
    result = run_cmd([str(NOTEBOOKLM), 'list'])
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or result.stdout.strip() or 'NotebookLM list failed')
    lines = [line.rstrip() for line in result.stdout.splitlines() if line.strip()]
    return lines


def load_previous():
    if not SNAPSHOT.exists():
        return []
    try:
        return json.loads(SNAPSHOT.read_text())
    except Exception:
        return []


def save_snapshot(lines):
    SNAPSHOT.write_text(json.dumps(lines, ensure_ascii=False, indent=2))


def summarize_changes(previous, current):
    prev = set(previous)
    cur = set(current)
    added = sorted(cur - prev)
    removed = sorted(prev - cur)
    unchanged = sorted(cur & prev)
    return added, removed, unchanged


def build_report(previous, current, added, removed, unchanged):
    ts = now_local().strftime('%Y-%m-%d %H:%M:%S %Z')
    parts = []
    parts.append(f'# NotebookLM sync report\n\n- generated_at: {ts}\n- notebook_count: {len(current)}\n')
    if added:
        parts.append('## New notebooks\n')
        parts.extend([f'- {x}\n' for x in added])
    if removed:
        parts.append('\n## Removed or unavailable notebooks\n')
        parts.extend([f'- {x}\n' for x in removed])
    parts.append('\n## Current notebooks\n')
    parts.extend([f'- {x}\n' for x in current])
    if not current:
        parts.append('- none\n')
    return ''.join(parts)


def append_memory_stub(report_text, dry_run):
    stamp = now_local().strftime('%H:%M')
    entry = f"\n- {stamp} NotebookLM sync preparado: relatório salvo em `tools/notebooklm-sync/outbox/last_sync_report.md`; sincronização depende de login válido e futura curadoria das mudanças relevantes.\n"
    if dry_run:
        return
    if MEMORY_DAY.exists():
        with MEMORY_DAY.open('a', encoding='utf-8') as f:
            f.write(entry)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args()

    ensure_dirs()

    try:
        current = list_notebooks()
    except Exception as e:
        msg = str(e)
        REPORT.write_text(f'# NotebookLM sync failed\n\n- error: {msg}\n', encoding='utf-8')
        print(msg, file=sys.stderr)
        return 2

    previous = load_previous()
    added, removed, unchanged = summarize_changes(previous, current)
    report = build_report(previous, current, added, removed, unchanged)
    if not args.dry_run:
        REPORT.write_text(report, encoding='utf-8')
        save_snapshot(current)
        append_memory_stub(report, dry_run=False)
    else:
        print(report)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
