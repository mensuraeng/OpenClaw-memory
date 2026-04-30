#!/usr/bin/env python3
"""Send MENSURA campaign D+3 follow-up after explicit Alexandre approval.

Inputs:
- runtime/mensura-marketing/campanha-20260427/followup-d3-final-latest.csv
- runtime/mensura-marketing/campanha-20260427/followup-d3-summary-20260430-0932.json

Safety:
- Requires --send to actually send.
- Writes stamped JSON/CSV logs.
- Uses one Microsoft Graph token and serial sendMail calls.
"""
from __future__ import annotations

import argparse
import csv
import json
import time
import urllib.parse
import urllib.request
import urllib.error
from datetime import datetime, timezone, timedelta
from pathlib import Path

WORKSPACE = Path('/root/.openclaw/workspace')
CAMPAIGN_DIR = WORKSPACE / 'runtime/mensura-marketing/campanha-20260427'
CSV_PATH = CAMPAIGN_DIR / 'followup-d3-final-latest.csv'
SUMMARY_PATH = CAMPAIGN_DIR / 'followup-d3-summary-20260430-0932.json'
CONFIG_PATH = WORKSPACE / 'config/ms-graph.json'
USER = 'flavia@mensuraengenharia.com.br'
BRT = timezone(timedelta(hours=-3))


def now_label() -> str:
    return datetime.now(BRT).strftime('%Y%m%d-%H%M')


def load_config() -> dict:
    return json.loads(CONFIG_PATH.read_text(encoding='utf-8'))


def get_token(cfg: dict) -> str:
    url = f"https://login.microsoftonline.com/{cfg['tenantId']}/oauth2/v2.0/token"
    data = urllib.parse.urlencode({
        'client_id': cfg['clientId'],
        'client_secret': cfg['clientSecret'],
        'scope': 'https://graph.microsoft.com/.default',
        'grant_type': 'client_credentials',
    }).encode()
    req = urllib.request.Request(url, data=data, method='POST')
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.load(r)['access_token']


def graph_send(token: str, to: str, subject: str, body: str) -> tuple[int, str]:
    url = f'https://graph.microsoft.com/v1.0/users/{USER}/sendMail'
    payload = {
        'message': {
            'subject': subject,
            'body': {'contentType': 'Text', 'content': body},
            'toRecipients': [{'emailAddress': {'address': to}}],
        },
        'saveToSentItems': True,
    }
    req = urllib.request.Request(
        url,
        data=json.dumps(payload, ensure_ascii=False).encode('utf-8'),
        headers={'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'},
        method='POST',
    )
    try:
        with urllib.request.urlopen(req, timeout=90) as r:
            return r.status, ''
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode('utf-8', errors='replace')


def first_name(nome: str) -> str:
    parts = (nome or '').replace('|', ' ').strip().split()
    if not parts:
        return ''
    # Keep accented/original casing; normalize ALLCAPS first token lightly.
    p = parts[0]
    return p[:1].upper() + p[1:].lower() if p.isupper() else p


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('--send', action='store_true')
    ap.add_argument('--dry-run', action='store_true')
    args = ap.parse_args()
    if not args.send and not args.dry_run:
        raise SystemExit('Use --dry-run ou --send')

    summary = json.loads(SUMMARY_PATH.read_text(encoding='utf-8'))
    subject = summary['subject']
    template = summary['body_template']
    rows = list(csv.DictReader(CSV_PATH.open(newline='', encoding='utf-8')))
    if len(rows) != int(summary['eligible_followup_d3']):
        raise SystemExit(f"Divergência de contagem: csv={len(rows)} summary={summary['eligible_followup_d3']}")

    run_label = now_label()
    results = []
    token = None if args.dry_run else get_token(load_config())
    for idx, row in enumerate(rows, start=1):
        email = row['email'].strip().lower()
        nome_primeiro = first_name(row.get('nome', '')) or 'tudo bem'
        body = template.format(nome_primeiro=nome_primeiro)
        result = {
            'ordem': idx,
            'email': email,
            'empresa': row.get('empresa', ''),
            'nome': row.get('nome', ''),
            'subject': subject,
            'body_preview': body[:220],
            'mode': 'send' if args.send else 'dry-run',
            'status': None,
            'error': '',
        }
        if args.send:
            status, error = graph_send(token, email, subject, body)
            result['status'] = status
            result['error'] = error
            # Light serialization to avoid burst behavior.
            time.sleep(0.4)
        results.append(result)
        print(f"{idx:02d} {'SEND' if args.send else 'DRY'} {email} {result['status'] or ''} {result['error'][:120]}")

    json_log = CAMPAIGN_DIR / f"followup-d3-send-log-{run_label}.json"
    csv_log = CAMPAIGN_DIR / f"followup-d3-send-log-{run_label}.csv"
    payload = {
        'sent_at': datetime.now(BRT).strftime('%Y-%m-%d %H:%M BRT'),
        'approved_by': 'Alexandre via Telegram: "1 - sim!" em 2026-04-30 09:33 BRT',
        'mode': 'send' if args.send else 'dry-run',
        'subject': subject,
        'source_csv': str(CSV_PATH.relative_to(WORKSPACE)),
        'count': len(results),
        'success_count': sum(1 for r in results if r['status'] in (202, None) and not r['error']),
        'error_count': sum(1 for r in results if r['error']),
        'results': results,
    }
    json_log.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding='utf-8')
    with csv_log.open('w', encoding='utf-8', newline='') as f:
        fieldnames = ['ordem','email','empresa','nome','subject','mode','status','error']
        w = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
        w.writeheader()
        w.writerows(results)
    (CAMPAIGN_DIR / 'followup-d3-send-log-latest.json').write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f"json_log={json_log}")
    print(f"csv_log={csv_log}")


if __name__ == '__main__':
    main()
