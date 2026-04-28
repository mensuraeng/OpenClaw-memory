#!/usr/bin/env python3
"""Monitor read-only for LinkedIn Community Management API approval emails.

Checks configured Microsoft Graph mailboxes without modifying messages.
Outputs JSON with matches and a recommended action.
"""
from __future__ import annotations

import json
import sys
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

WORK = Path('/root/.openclaw/workspace')
OUTDIR = WORK / 'runtime/linkedin-institutional'
OUTDIR.mkdir(parents=True, exist_ok=True)

ACCOUNTS = [
    {'name': 'mensura-alexandre', 'config': 'config/ms-graph.json', 'user': 'alexandre@mensuraengenharia.com.br'},
    {'name': 'flavia', 'config': 'config/ms-graph.json', 'user': 'flavia@mensuraengenharia.com.br'},
    {'name': 'mia-alexandre', 'config': 'config/ms-graph-mia.json', 'user': 'alexandre@miaengenharia.com.br'},
    {'name': 'pcs-alexandre', 'config': 'config/ms-graph-pcs.json', 'user': 'alexandre@pcsengenharia.com.br'},
]

FOLDERS = ['inbox', 'junkemail']
APP_CLIENT_ID = '77ke3c00urrpdv'
APP_NAME = 'OpenClaw - Community API'

POSITIVE_TERMS = [
    'community management api',
    'w_organization_social',
    'r_organization_social',
    'organization social',
    'developer application review',
    'linkedin developer',
    'linkedin developers',
    APP_CLIENT_ID.lower(),
    APP_NAME.lower(),
]
APPROVAL_TERMS = ['approved', 'aproved', 'aprovado', 'granted', 'access has been granted', 'request approved']
PENDING_TERMS = ['review in progress', 'under review', 'in review', 'pending review', 'em análise', 'em analise']
REJECTION_TERMS = ['rejected', 'denied', 'not approved', 'recusado', 'negado']


def load_cfg(path: str) -> dict:
    return json.loads((WORK / path).read_text(encoding='utf-8'))


def get_token(cfg: dict) -> str:
    data = urllib.parse.urlencode({
        'client_id': cfg['clientId'],
        'client_secret': cfg['clientSecret'],
        'scope': 'https://graph.microsoft.com/.default',
        'grant_type': 'client_credentials',
    }).encode()
    req = urllib.request.Request(
        f"https://login.microsoftonline.com/{cfg['tenantId']}/oauth2/v2.0/token",
        data=data,
        method='POST',
    )
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.load(r)['access_token']


def graph_get(token: str, path: str) -> dict:
    req = urllib.request.Request('https://graph.microsoft.com/v1.0' + path, headers={'Authorization': 'Bearer ' + token})
    with urllib.request.urlopen(req, timeout=90) as r:
        return json.load(r)


def classify(text: str) -> str:
    low = text.lower()
    if any(t in low for t in REJECTION_TERMS):
        return 'rejeitado/negado'
    if any(t in low for t in APPROVAL_TERMS):
        return 'aprovado'
    if any(t in low for t in PENDING_TERMS):
        return 'em análise'
    return 'possivelmente relacionado'


def main() -> int:
    lookback_hours = int(sys.argv[1]) if len(sys.argv) > 1 else 240
    since = (datetime.now(timezone.utc) - timedelta(hours=lookback_hours)).strftime('%Y-%m-%dT%H:%M:%SZ')
    matches = []
    errors = []

    for account in ACCOUNTS:
        try:
            cfg = load_cfg(account['config'])
            token = get_token(cfg)
            for folder in FOLDERS:
                filt = urllib.parse.quote(f"receivedDateTime ge {since}")
                select = 'id,subject,from,receivedDateTime,bodyPreview,webLink'
                path = f"/users/{urllib.parse.quote(account['user'])}/mailFolders/{folder}/messages?$top=50&$orderby=receivedDateTime%20desc&$filter={filt}&$select={select}"
                for m in graph_get(token, path).get('value', []):
                    sender = (m.get('from') or {}).get('emailAddress', {}).get('address', '')
                    subject = m.get('subject', '') or ''
                    preview = m.get('bodyPreview', '') or ''
                    text = '\n'.join([sender, subject, preview]).lower()
                    if 'linkedin' not in text and APP_CLIENT_ID.lower() not in text and APP_NAME.lower() not in text:
                        continue
                    if any(term in text for term in POSITIVE_TERMS):
                        matches.append({
                            'account': account['name'],
                            'user': account['user'],
                            'folder': folder,
                            'receivedDateTime': m.get('receivedDateTime'),
                            'from': sender,
                            'subject': subject,
                            'classification': classify(text),
                            'preview': preview[:600],
                            'webLink': m.get('webLink'),
                            'id': m.get('id'),
                        })
        except Exception as exc:
            errors.append({'account': account['name'], 'user': account['user'], 'error': str(exc)[:800]})

    approved = [m for m in matches if m['classification'] == 'aprovado']
    rejected = [m for m in matches if m['classification'] == 'rejeitado/negado']
    status = 'approval_found' if approved else 'rejection_found' if rejected else 'no_approval_found'
    recommended_action = (
        'Gerar OAuth institucional com escopos w_organization_social r_organization_social e validar páginas.'
        if approved else
        'Revisar motivo da negativa no LinkedIn Developers.' if rejected else
        'Continuar monitorando; Community Management API ainda não apareceu como aprovada.'
    )
    result = {
        'checked_at_utc': datetime.now(timezone.utc).isoformat(),
        'lookback_hours': lookback_hours,
        'app': APP_NAME,
        'client_id': APP_CLIENT_ID,
        'status': status,
        'matches': matches,
        'errors': errors,
        'recommended_action': recommended_action,
    }
    (OUTDIR / 'community-api-email-check-latest.json').write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    (OUTDIR / f'community-api-email-check-{stamp}.json').write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
