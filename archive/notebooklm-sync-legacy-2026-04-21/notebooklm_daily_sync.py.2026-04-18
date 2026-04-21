#!/usr/bin/env python3
"""Consulta todos os notebooks do NotebookLM e gera um rascunho de atualização de memória.

Requer login prévio do notebooklm-py no storage padrão ou via NOTEBOOKLM_STORAGE.
Não promove automaticamente para memória institucional. Gera material auditável para promoção.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

WORKSPACE = Path('/root/.openclaw/workspace')
VENV_BIN = WORKSPACE / '.venvs' / 'notebooklm' / 'bin' / 'python'
STORAGE = os.environ.get('NOTEBOOKLM_STORAGE', '/root/.notebooklm/storage_state.json')
OUT_BASE = WORKSPACE / 'memory' / 'notebooklm-sync'
TIMEZONE = 'America/Sao_Paulo'

PROMPT = (
    'Faça uma atualização executiva de memória deste notebook. '
    'Responda em português do Brasil, com os blocos exatos: '\
    'NOVAS INFORMAÇÕES, DECISÕES, PENDÊNCIAS, RISCOS, PRÓXIMOS PASSOS. '
    'Se não houver evidência suficiente em algum bloco, escreva "nenhum item confiável".'
)


def run_cli(*args: str) -> str:
    cmd = [str(VENV_BIN), '-m', 'notebooklm', '--storage', STORAGE, *args]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or result.stdout.strip() or f'falha em {cmd}')
    return result.stdout.strip()


def list_notebooks() -> list[dict]:
    raw = run_cli('list')
    lines = [line.strip() for line in raw.splitlines() if line.strip()]
    notebooks = []
    for line in lines:
        if line.lower().startswith('available notebooks'):
            continue
        parts = [p.strip() for p in line.split('|')]
        if len(parts) >= 2:
            notebooks.append({'id': parts[0], 'title': parts[1], 'raw': line})
        else:
            notebooks.append({'id': line.split()[0], 'title': line, 'raw': line})
    return notebooks


def sanitize(name: str) -> str:
    keep = []
    for ch in name.lower():
        keep.append(ch if ch.isalnum() else '-')
    slug = ''.join(keep)
    while '--' in slug:
        slug = slug.replace('--', '-')
    return slug.strip('-')[:80] or 'notebook'


def main() -> int:
    now = datetime.now().strftime('%Y-%m-%d')
    out_dir = OUT_BASE / now
    out_dir.mkdir(parents=True, exist_ok=True)

    try:
        notebooks = list_notebooks()
    except Exception as exc:
        print(json.dumps({'status': 'error', 'stage': 'list', 'error': str(exc)}, ensure_ascii=False))
        return 1

    summary = {
        'date': now,
        'timezone': TIMEZONE,
        'storage': STORAGE,
        'status': 'ok',
        'count': len(notebooks),
        'items': [],
    }

    for nb in notebooks:
        item = {'id': nb['id'], 'title': nb['title'], 'status': 'ok'}
        try:
            run_cli('use', nb['id'])
            answer = run_cli('ask', PROMPT)
            summary_text = run_cli('summary')
            slug = sanitize(nb['title'])
            md_path = out_dir / f'{slug}.md'
            md_path.write_text(
                f"# {nb['title']}\n\n"
                f"- id: {nb['id']}\n"
                f"- data: {now}\n\n"
                f"## Summary do NotebookLM\n\n{summary_text}\n\n"
                f"## Atualização executiva de memória\n\n{answer}\n",
                encoding='utf-8'
            )
            item['file'] = str(md_path)
        except Exception as exc:
            item['status'] = 'error'
            item['error'] = str(exc)
        summary['items'].append(item)

    summary_path = out_dir / 'index.json'
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({'status': summary['status'], 'count': summary['count'], 'path': str(summary_path)}, ensure_ascii=False))
    return 0


if __name__ == '__main__':
    sys.exit(main())
