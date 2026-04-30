#!/usr/bin/env python3
"""Auditoria estática de intake para skills candidatas.

Não executa a skill candidata. Lê arquivos, classifica risco e gera relatório local.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from typing import Any, Iterable

WORKSPACE = Path('/root/.openclaw/workspace')
OUT = WORKSPACE / 'runtime/skills-intake'
SKIP_DIRS = {'.git', 'node_modules', '__pycache__', '.pytest_cache', '.venv', 'venv', 'dist', 'build'}
SKIP_SUFFIXES = {'.png', '.jpg', '.jpeg', '.gif', '.webp', '.pdf', '.zip', '.gz', '.sqlite', '.db', '.pyc'}
MAX_FILE_BYTES = 1_500_000

RISK_PATTERNS: list[tuple[str, str, int, re.Pattern[str]]] = [
    ('destructive_command', 'block', 35, re.compile(r'\b(rm\s+-rf|shred\b|mkfs\b|dd\s+if=|:(){:|:&};:)')),
    ('secret_file_access', 'block', 30, re.compile(r'(\.env\b|\.ssh/|id_rsa|credentials|access[_-]?token|api[_-]?key)', re.I)),
    ('network_execution', 'suspect', 25, re.compile(r'(curl|wget).*(\|\s*(bash|sh)|python\s+-)', re.I)),
    ('shell_execution', 'review', 15, re.compile(r'\b(subprocess\.|os\.system\(|child_process\.|execSync\(|spawn\()', re.I)),
    ('external_network', 'review', 10, re.compile(r'\b(fetch\(|requests\.|axios\.|httpx\.|urllib\.request|WebClient\()', re.I)),
    ('encoded_payload', 'suspect', 25, re.compile(r'(base64\s+-d|atob\(|fromCharCode|eval\(|exec\()', re.I)),
    ('permission_creep_hint', 'review', 15, re.compile(r'(gmail|drive|slack|telegram|whatsapp|github|aws|gcp|azure|ssh|sudo|docker)', re.I)),
    ('raw_key_idempotency_risk', 'review', 20, re.compile(r'(req\.url|request\.url|location\.href|pathname\s*\+|hash\([^)]*(url|path|email|domain)|idempotency|rate.?limit|dedup|fingerprint)', re.I)),
]


def now_slug() -> str:
    return datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')


def canonical_path(path: Path, root: Path) -> str:
    resolved = path.resolve(strict=False)
    root_resolved = root.resolve(strict=False)
    try:
        return resolved.relative_to(root_resolved).as_posix()
    except ValueError:
        return resolved.as_posix()


def canonical_url_path(raw: str) -> str:
    text = str(raw).strip().split('?', 1)[0].split('#', 1)[0].replace('\\', '/')
    norm = PurePosixPath('/' + text.lstrip('/')).as_posix().rstrip('/')
    return norm or '/'


def sha(text: str) -> str:
    return hashlib.sha256(text.encode('utf-8')).hexdigest()[:16]


def iter_files(root: Path) -> Iterable[Path]:
    for current, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for filename in filenames:
            path = Path(current) / filename
            if path.suffix.lower() in SKIP_SUFFIXES:
                continue
            try:
                if path.stat().st_size > MAX_FILE_BYTES:
                    continue
            except OSError:
                continue
            yield path


def classify(score: int, severities: Counter[str]) -> str:
    if severities.get('block', 0) or score >= 70:
        return 'BLOCK'
    if severities.get('suspect', 0) or score >= 45:
        return 'SUSPECT'
    if severities.get('review', 0) or score >= 15:
        return 'REVIEW'
    return 'CLEAN'


def check_key_normalization() -> dict[str, Any]:
    variants = ['/googlechat', '/googlechat/', '/googlechat?foo=bar']
    keys = [canonical_url_path(v) for v in variants]
    return {
        'status': 'pass' if len(set(keys)) == 1 else 'block',
        'achado': 'skill intake normaliza path/query/trailing slash antes de gerar chave de auditoria',
        'risco': 'rate-limit bypass | dedup fragmentation',
        'correcao': 'gerar key a partir do path canônico validado',
        'teste_minimo': variants,
        'key_hashes': [sha(k) for k in keys],
    }


def audit(root: Path) -> dict[str, Any]:
    root = root.expanduser().resolve(strict=False)
    if not root.exists() or not root.is_dir():
        raise SystemExit(f'candidate path inválido: {root}')
    files = list(iter_files(root))
    findings: list[dict[str, Any]] = []
    inventory = Counter()
    for path in files:
        rel = canonical_path(path, root)
        inventory[path.suffix.lower() or '<none>'] += 1
        try:
            lines = path.read_text(encoding='utf-8', errors='ignore').splitlines()
        except OSError:
            continue
        for line_no, line in enumerate(lines, 1):
            for detector, severity, weight, pattern in RISK_PATTERNS:
                if pattern.search(line):
                    findings.append({
                        'path': rel,
                        'line': line_no,
                        'detector': detector,
                        'severity': severity,
                        'weight': weight,
                    })
    score = min(100, sum(f['weight'] for f in findings))
    severities = Counter(f['severity'] for f in findings)
    status = classify(score, severities)
    skill_md = root / 'SKILL.md'
    declared = skill_md.read_text(encoding='utf-8', errors='ignore')[:2000] if skill_md.exists() else ''
    return {
        'checked_at_utc': datetime.now(timezone.utc).isoformat(),
        'candidate': str(root),
        'status': status,
        'risk_score': score,
        'files_scanned': len(files),
        'inventory_by_suffix': dict(sorted(inventory.items())),
        'has_skill_md': skill_md.exists(),
        'declared_description_excerpt_hash': sha(declared) if declared else None,
        'findings_by_severity': dict(severities),
        'findings': findings[:500],
        'findings_truncated': len(findings) > 500,
        'trust_verifier': {
            'status': 'not_run',
            'reason': 'script executa apenas auditoria estática local; trust-verifier deve ser etapa separada quando houver pacote candidato real',
        },
        'guardrails': {
            'candidate_code_executed': False,
            'external_calls': False,
            'destructive_actions': False,
        },
        'key_normalization_and_idempotency': check_key_normalization(),
    }


def safe_name(path: Path) -> str:
    return re.sub(r'[^A-Za-z0-9_.-]+', '-', path.name.strip() or 'candidate')[:80]


def write_outputs(report: dict[str, Any], base_out: Path) -> None:
    stamp = now_slug()
    out_dir = base_out / safe_name(Path(report['candidate'])) / stamp
    out_dir.mkdir(parents=True, exist_ok=True)
    json_text = json.dumps(report, ensure_ascii=False, indent=2) + '\n'
    (out_dir / 'report.json').write_text(json_text, encoding='utf-8')
    latest_dir = base_out / safe_name(Path(report['candidate']))
    (latest_dir / 'latest.json').write_text(json_text, encoding='utf-8')
    md = [
        '# Skill Intake Audit', '',
        f"- Candidata: `{report['candidate']}`",
        f"- Status: `{report['status']}`",
        f"- Score: {report['risk_score']}/100",
        f"- Arquivos varridos: {report['files_scanned']}",
        f"- Achados por severidade: `{report['findings_by_severity']}`",
        '',
        '## Guardrails',
        '- Código candidato não executado.',
        '- Sem chamada externa.',
        '- Sem ação destrutiva.',
        '',
        '## [key_normalization_and_idempotency]',
        f"- Status: `{report['key_normalization_and_idempotency']['status']}`",
        f"- Achado: {report['key_normalization_and_idempotency']['achado']}",
        f"- Risco: {report['key_normalization_and_idempotency']['risco']}",
        '',
        '## Achados principais',
    ]
    for f in report['findings'][:80]:
        md.append(f"- `{f['severity']}` `{f['detector']}` em `{f['path']}:{f['line']}`")
    md_text = '\n'.join(md) + '\n'
    (out_dir / 'report.md').write_text(md_text, encoding='utf-8')
    (latest_dir / 'latest.md').write_text(md_text, encoding='utf-8')


def main() -> int:
    parser = argparse.ArgumentParser(description='Audita skill candidata sem executá-la.')
    parser.add_argument('path', help='diretório local da skill candidata')
    parser.add_argument('--json', action='store_true', help='imprimir resumo JSON')
    parser.add_argument('--no-write', action='store_true', help='não gravar runtime/skills-intake')
    args = parser.parse_args()
    report = audit(Path(args.path))
    if not args.no_write:
        write_outputs(report, OUT)
    if args.json:
        summary_keys = ['checked_at_utc', 'candidate', 'status', 'risk_score', 'files_scanned', 'findings_by_severity', 'guardrails', 'key_normalization_and_idempotency']
        print(json.dumps({k: report[k] for k in summary_keys}, ensure_ascii=False, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
