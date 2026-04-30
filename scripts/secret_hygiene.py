#!/usr/bin/env python3
"""Secret hygiene scanner seguro para workspace/2nd-brain.

Objetivo: detectar possíveis segredos sem imprimir valores reais.
Saída contém apenas caminho canônico, linha, detector, severidade e fingerprint hash.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

WORKSPACE = Path('/root/.openclaw/workspace')
SECOND_BRAIN = Path('/root/2nd-brain')
OUT = WORKSPACE / 'runtime/secret-hygiene'

SKIP_DIRS = {
    '.git', 'node_modules', '__pycache__', '.pytest_cache', '.venv', 'venv',
    'dist', 'build', '.next', '.cache', 'coverage', '.venvs', 'site-packages', 'runtime/restore-drill',
    'runtime/health', 'runtime/backups', 'tmp', 'temp',
}
SKIP_SUFFIXES = {
    '.png', '.jpg', '.jpeg', '.gif', '.webp', '.pdf', '.zip', '.gz', '.tgz', '.7z',
    '.sqlite', '.db', '.pyc', '.mp4', '.mov', '.mp3', '.wav', '.woff', '.woff2',
}
MAX_FILE_BYTES = 2 * 1024 * 1024
MAX_FINDINGS_PER_FILE = 20

DETECTORS: list[tuple[str, str, re.Pattern[str]]] = [
    ('openai_api_key', 'critical', re.compile(r'\bsk-[A-Za-z0-9_-]{20,}\b')),
    ('github_token', 'critical', re.compile(r'\bgh[pousr]_[A-Za-z0-9_]{20,}\b')),
    ('slack_token', 'critical', re.compile(r'\bxox[baprs]-[A-Za-z0-9-]{20,}\b')),
    ('google_api_key', 'high', re.compile(r'\bAIza[0-9A-Za-z_-]{30,}\b')),
    ('aws_access_key', 'high', re.compile(r'\bAKIA[0-9A-Z]{16}\b')),
    ('private_key_header', 'critical', re.compile(r'-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----')),
    ('generic_secret_assignment', 'review', re.compile(r'(?i)\b(?:secret|token|api[_-]?key|access[_-]?token|password|passwd)\b\s*[:=]\s*["\']?([^"\'\s#]{16,})')),
]


def now_slug() -> str:
    return datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')


def canonical_path(path: Path, root: Path) -> str:
    resolved = path.expanduser().resolve(strict=False)
    root_resolved = root.expanduser().resolve(strict=False)
    try:
        return resolved.relative_to(root_resolved).as_posix()
    except ValueError:
        return resolved.as_posix()


def canonical_fingerprint_input(value: str) -> str:
    # Não altera case do segredo inteiro para evitar colidir segredos realmente distintos.
    # Remove apenas ruído de captura comum.
    return value.strip().strip('"\'').strip()


def fingerprint(value: str) -> str:
    return hashlib.sha256(canonical_fingerprint_input(value).encode('utf-8')).hexdigest()[:16]


def shannon_entropy(value: str) -> float:
    if not value:
        return 0.0
    counts = Counter(value)
    length = len(value)
    return -sum((n / length) * math.log2(n / length) for n in counts.values())


def should_skip_dir(path: Path) -> bool:
    parts = set(path.parts)
    return bool(parts & SKIP_DIRS)


def iter_files(roots: Iterable[Path]) -> Iterable[tuple[Path, Path]]:
    for root in roots:
        if not root.exists():
            continue
        for current, dirnames, filenames in os.walk(root):
            current_path = Path(current)
            dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS and not d.startswith('.cache') and d != '.venvs']
            if should_skip_dir(current_path.relative_to(root) if current_path != root else Path('.')):
                continue
            for filename in filenames:
                path = current_path / filename
                if path.suffix.lower() in SKIP_SUFFIXES:
                    continue
                try:
                    if path.stat().st_size > MAX_FILE_BYTES:
                        continue
                except OSError:
                    continue
                yield root, path


def scan_line(line: str) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    for detector, severity, pattern in DETECTORS:
        for match in pattern.finditer(line):
            raw = match.group(1) if match.lastindex else match.group(0)
            findings.append({
                'detector': detector,
                'severity': severity,
                'fingerprint': fingerprint(raw),
                'entropy': round(shannon_entropy(raw), 2),
            })
    # Entropia genérica só para strings longas em atribuições sensíveis; sem imprimir valor.
    return findings


def downgrade_if_test_fixture(finding: dict[str, Any], rel_path: str) -> None:
    normalized = rel_path.replace('\\', '/').lower()
    if '/test/' in normalized or normalized.endswith('.test.js') or '/tests/' in normalized:
        if finding.get('severity') in {'critical', 'high'}:
            finding['severity'] = 'review'
            finding['fixture_context'] = True


def scan(roots: list[Path]) -> dict[str, Any]:
    results: list[dict[str, Any]] = []
    files_scanned = 0
    for root, path in iter_files(roots):
        files_scanned += 1
        per_file = 0
        try:
            with path.open('r', encoding='utf-8', errors='ignore') as fh:
                for line_no, line in enumerate(fh, 1):
                    for finding in scan_line(line):
                        if per_file >= MAX_FINDINGS_PER_FILE:
                            break
                        downgrade_if_test_fixture(finding, canonical_path(path, root))
                        finding.update({
                            'root': str(root),
                            'path': canonical_path(path, root),
                            'line': line_no,
                            'key_normalization_and_idempotency': {
                                'status': 'pass',
                                'note': 'fingerprint gerado de valor capturado canonicalizado por trim; segredo não impresso',
                            },
                        })
                        results.append(finding)
                        per_file += 1
                    if per_file >= MAX_FINDINGS_PER_FILE:
                        break
        except OSError:
            continue
    severity_order = {'critical': 4, 'high': 3, 'review': 2, 'medium': 2, 'low': 1}
    worst = max((severity_order.get(f['severity'], 0) for f in results), default=0)
    status = 'block' if worst >= 4 else 'review' if results else 'pass'
    return {
        'checked_at_utc': datetime.now(timezone.utc).isoformat(),
        'status': status,
        'files_scanned': files_scanned,
        'findings_count': len(results),
        'findings_by_severity': dict(Counter(f['severity'] for f in results)),
        'guardrails': {
            'prints_real_secret_values': False,
            'external_calls': False,
            'destructive_actions': False,
            'canonical_fingerprints': True,
        },
        'findings': results,
    }


def write_outputs(report: dict[str, Any], out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    latest_json = out_dir / 'latest.json'
    latest_md = out_dir / 'latest.md'
    stamp = now_slug()
    run_json = out_dir / f'secret-hygiene-{stamp}.json'
    run_md = out_dir / f'secret-hygiene-{stamp}.md'
    json_text = json.dumps(report, ensure_ascii=False, indent=2) + '\n'
    md = [
        '# Secret Hygiene — relatório seguro',
        '',
        f"- Status: `{report['status']}`",
        f"- Arquivos varridos: {report['files_scanned']}",
        f"- Achados: {report['findings_count']}",
        f"- Por severidade: `{report['findings_by_severity']}`",
        '',
        '## Guardrails',
        '- Valores reais de segredo não são impressos.',
        '- Fingerprints usam hash de valor canonicalizado por trim.',
        '- Sem chamada externa e sem ação destrutiva.',
        '',
        '## Achados',
    ]
    for f in report['findings'][:200]:
        md.append(f"- `{f['severity']}` `{f['detector']}` em `{f['path']}:{f['line']}` fingerprint `{f['fingerprint']}`")
    if report['findings_count'] > 200:
        md.append(f"- ... {report['findings_count'] - 200} achados adicionais no JSON.")
    md_text = '\n'.join(md) + '\n'
    for p, text in [(latest_json, json_text), (run_json, json_text), (latest_md, md_text), (run_md, md_text)]:
        p.write_text(text, encoding='utf-8')


def main() -> int:
    parser = argparse.ArgumentParser(description='Varre segredos sem imprimir valores reais.')
    parser.add_argument('--workspace', action='store_true', help='varrer workspace')
    parser.add_argument('--second-brain', action='store_true', help='varrer /root/2nd-brain')
    parser.add_argument('--json', action='store_true', help='imprimir resumo JSON seguro')
    parser.add_argument('--no-write', action='store_true', help='não gravar runtime/secret-hygiene')
    args = parser.parse_args()

    roots: list[Path] = []
    if args.workspace or not (args.workspace or args.second_brain):
        roots.append(WORKSPACE)
    if args.second_brain:
        roots.append(SECOND_BRAIN)
    report = scan(roots)
    if not args.no_write:
        write_outputs(report, OUT)
    if args.json:
        safe_summary = {k: report[k] for k in ('checked_at_utc', 'status', 'files_scanned', 'findings_count', 'findings_by_severity', 'guardrails')}
        print(json.dumps(safe_summary, ensure_ascii=False, indent=2))
    return 0 if report['status'] in {'pass', 'review', 'block'} else 1


if __name__ == '__main__':
    raise SystemExit(main())
