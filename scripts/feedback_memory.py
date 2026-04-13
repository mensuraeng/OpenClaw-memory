#!/usr/bin/env python3
import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

BASE = Path('/root/.openclaw/workspace/memory/feedback')
FILES = {
    'content': BASE / 'content.json',
    'recommendations': BASE / 'recommendations.json',
    'tasks': BASE / 'tasks.json',
}


def load(domain: str):
    path = FILES[domain]
    if not path.exists():
        return {'entries': []}
    return json.loads(path.read_text())


def save(domain: str, data):
    FILES[domain].write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n')


def cmd_add(args):
    data = load(args.domain)
    entry = {
        'date': args.date or datetime.now(timezone.utc).date().isoformat(),
        'context': args.context,
        'decision': args.decision,
        'reason': args.reason,
        'tags': [t.strip() for t in (args.tags or '').split(',') if t.strip()],
    }
    if args.replaces:
        entry['replaces'] = args.replaces
    data.setdefault('entries', []).append(entry)
    save(args.domain, data)
    print(json.dumps(entry, ensure_ascii=False, indent=2))
    return 0


def score(entry, terms):
    hay = ' '.join([
        entry.get('context', ''),
        entry.get('reason', ''),
        ' '.join(entry.get('tags', [])),
        entry.get('decision', ''),
    ]).lower()
    return sum(1 for term in terms if term in hay)


def cmd_query(args):
    terms = [t.lower() for t in args.query.split() if t.strip()]
    out = []
    domains = [args.domain] if args.domain else list(FILES.keys())
    for domain in domains:
        data = load(domain)
        for entry in data.get('entries', []):
            s = score(entry, terms)
            if terms and s == 0:
                continue
            out.append({'domain': domain, 'score': s, **entry})
    out.sort(key=lambda x: (x['score'], x.get('date', '')), reverse=True)
    print(json.dumps({'results': out[: args.limit]}, ensure_ascii=False, indent=2))
    return 0


def build_parser():
    p = argparse.ArgumentParser(description='Registra e consulta feedback approve/reject do workspace.')
    sub = p.add_subparsers(dest='cmd', required=True)

    add = sub.add_parser('add')
    add.add_argument('--domain', choices=sorted(FILES.keys()), required=True)
    add.add_argument('--decision', choices=['approve', 'reject'], required=True)
    add.add_argument('--context', required=True)
    add.add_argument('--reason', required=True)
    add.add_argument('--tags', default='')
    add.add_argument('--date')
    add.add_argument('--replaces')
    add.set_defaults(func=cmd_add)

    query = sub.add_parser('query')
    query.add_argument('query')
    query.add_argument('--domain', choices=sorted(FILES.keys()))
    query.add_argument('--limit', type=int, default=5)
    query.set_defaults(func=cmd_query)

    return p


if __name__ == '__main__':
    parser = build_parser()
    args = parser.parse_args()
    raise SystemExit(args.func(args))
