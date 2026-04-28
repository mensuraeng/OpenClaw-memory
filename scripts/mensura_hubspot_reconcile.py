#!/usr/bin/env python3
"""Mensura HubSpot reconciliation — read-only.

Compares local Commercial Intelligence SQLite with live HubSpot contacts/companies/deals.
No writes. Explicit pagination.
"""
from __future__ import annotations

import argparse
import json
import sqlite3
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
from secret_config import load_json_config

WORKSPACE = Path('/root/.openclaw/workspace')
DB = WORKSPACE / 'projects/mensura-commercial-intelligence/data/commercial-intelligence.sqlite'
OUT = WORKSPACE / 'runtime/data-pipeline/crm'


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def hubspot_search(base: str, token: str, obj: str, properties: list[str], limit: int = 100) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    after: str | None = None
    while True:
        body: dict[str, Any] = {'limit': limit, 'properties': properties}
        if after:
            body['after'] = after
        req = urllib.request.Request(
            f'{base}/crm/v3/objects/{obj}/search',
            data=json.dumps(body).encode(),
            headers={'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'},
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read())
        results.extend(data.get('results', []))
        after = data.get('paging', {}).get('next', {}).get('after')
        if not after:
            break
    return results


def local_sets() -> dict[str, set[str]]:
    con = sqlite3.connect(DB)
    emails = {r[0].strip().lower() for r in con.execute("select email from contacts where email is not null and trim(email)<>''").fetchall()}
    valid_emails = {r[0].strip().lower() for r in con.execute("""
        select c.email from contacts c
        where c.email is not null and trim(c.email)<>''
          and coalesce(c.is_corporate,0)=1
          and not exists (select 1 from suppression_list s where lower(s.email)=lower(c.email))
          and (lower(coalesce(c.validity_status,'')) in ('valid','válido','valido','ok') or upper(coalesce(c.grade,'')) in ('A','B'))
    """).fetchall()}
    domains = {r[0].strip().lower() for r in con.execute("select domain from companies where domain is not null and trim(domain)<>''").fetchall()}
    return {'emails': emails, 'valid_emails': valid_emails, 'domains': domains}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('--write', action='store_true')
    ap.add_argument('--json', action='store_true')
    args = ap.parse_args()
    cfg = load_json_config(WORKSPACE / 'config/hubspot-mensura.json')
    token = cfg['accessToken']
    base = cfg.get('apiBaseUrl', 'https://api.hubapi.com')
    hs_contacts = hubspot_search(base, token, 'contacts', ['email', 'firstname', 'lastname', 'company'])
    hs_companies = hubspot_search(base, token, 'companies', ['domain', 'name'])
    hs_deals = hubspot_search(base, token, 'deals', ['dealname', 'dealstage', 'amount'])
    local = local_sets()
    hs_emails = {c.get('properties', {}).get('email', '').strip().lower() for c in hs_contacts if c.get('properties', {}).get('email')}
    hs_domains = {c.get('properties', {}).get('domain', '').strip().lower() for c in hs_companies if c.get('properties', {}).get('domain')}
    payload = {
        'generated_at_utc': now_iso(),
        'mode': 'read_only',
        'source': {
            'local_sqlite': str(DB),
            'hubspot_portal_id': cfg.get('portalId'),
            'hubspot_objects': ['contacts', 'companies', 'deals'],
        },
        'method': 'HubSpot CRM v3 search API with explicit pagination; local SQLite set comparison; no writes',
        'confidence': 'high for counts returned by HubSpot API and local SQLite at generation time',
        'risk_of_error': 'email/domain matching does not prove company identity; HubSpot duplicate/merge rules may differ from local SQLite',
        'counts': {
            'local_contacts_with_email': len(local['emails']),
            'local_valid_emails_not_suppressed': len(local['valid_emails']),
            'local_company_domains': len(local['domains']),
            'hubspot_contacts_with_email': len(hs_emails),
            'hubspot_companies_with_domain': len(hs_domains),
            'hubspot_deals': len(hs_deals),
        },
        'gaps': {
            'valid_local_emails_missing_in_hubspot': len(local['valid_emails'] - hs_emails),
            'hubspot_emails_missing_in_local': len(hs_emails - local['emails']),
            'local_domains_missing_in_hubspot': len(local['domains'] - hs_domains),
            'hubspot_domains_missing_in_local': len(hs_domains - local['domains']),
        },
        'samples': {
            'valid_local_missing_in_hubspot': sorted(list(local['valid_emails'] - hs_emails))[:25],
            'hubspot_missing_in_local': sorted(list(hs_emails - local['emails']))[:25],
        },
    }
    if args.write:
        OUT.mkdir(parents=True, exist_ok=True)
        ts = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
        path = OUT / f'mensura-hubspot-reconciliation-{ts}.json'
        latest = OUT / 'mensura-hubspot-reconciliation-latest.json'
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        latest.write_text(path.read_text(encoding='utf-8'), encoding='utf-8')
        payload['artifact'] = str(path)
        payload['latest_artifact'] = str(latest)
    print(json.dumps(payload, ensure_ascii=False, indent=2) if args.json else json.dumps(payload, ensure_ascii=False))


if __name__ == '__main__':
    main()
