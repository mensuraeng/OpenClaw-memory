#!/usr/bin/env python3
"""Mensura CRM/CDP pipeline v1 — read-only/source-of-truth exporter.

Purpose:
- Turn Mensura Commercial Intelligence SQLite into verified runtime artifacts.
- Keep source, window, method, confidence and risk explicit.
- Do not write to HubSpot/Phantombuster/LinkedIn. This script is internal/read-only.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

WORKSPACE = Path('/root/.openclaw/workspace')
DB = WORKSPACE / 'projects/mensura-commercial-intelligence/data/commercial-intelligence.sqlite'
OUT_ROOT = WORKSPACE / 'runtime/data-pipeline'


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode('utf-8')).hexdigest()


def rows(con: sqlite3.Connection, sql: str, params: tuple[Any, ...] = ()) -> list[dict[str, Any]]:
    con.row_factory = sqlite3.Row
    return [dict(r) for r in con.execute(sql, params).fetchall()]


def one(con: sqlite3.Connection, sql: str, params: tuple[Any, ...] = ()) -> Any:
    return con.execute(sql, params).fetchone()[0]


def ensure_dirs() -> None:
    for p in ['staging', 'enriched', 'verified', 'rejected', 'crm', 'outreach', 'archive']:
        (OUT_ROOT / p).mkdir(parents=True, exist_ok=True)


def load_snapshot() -> dict[str, Any]:
    if not DB.exists():
        raise SystemExit(f'Database não encontrado: {DB}')
    con = sqlite3.connect(DB)
    counts = {
        'companies': one(con, 'select count(*) from companies'),
        'contacts': one(con, 'select count(*) from contacts'),
        'suppression_list': one(con, 'select count(*) from suppression_list'),
        'campaigns': one(con, 'select count(*) from campaigns'),
        'campaign_recipients': one(con, 'select count(*) from campaign_recipients'),
        'interactions': one(con, 'select count(*) from interactions'),
    }
    validity = rows(con, "select coalesce(validity_status,'unknown') as status, count(*) as count from contacts group by 1 order by count desc")
    grades = rows(con, "select coalesce(grade,'unknown') as grade, count(*) as count from contacts group by 1 order by count desc")
    campaign_status = rows(con, "select coalesce(status,'unknown') as status, count(*) as count from campaign_recipients group by 1 order by count desc")
    bad = {
        'contacts_without_email': one(con, "select count(*) from contacts where email is null or trim(email)=''"),
        'contacts_without_name': one(con, "select count(*) from contacts where name is null or trim(name)=''"),
        'contacts_without_company': one(con, "select count(*) from contacts where company_id is null"),
        'non_corporate_contacts': one(con, "select count(*) from contacts where coalesce(is_corporate,0)=0"),
    }
    verified = rows(con, """
        select
          c.id as contact_id,
          c.email,
          c.name,
          c.role,
          c.phone,
          c.mobile,
          c.segment as contact_segment,
          c.source as contact_source,
          c.validity_status,
          c.grade,
          c.score,
          coalesce(c.is_corporate,0) as is_corporate,
          co.company_name,
          co.trading_name,
          co.legal_name,
          co.domain,
          co.segment as company_segment,
          co.city,
          co.state,
          co.icp_score
        from contacts c
        left join companies co on co.id = c.company_id
        where lower(coalesce(c.validity_status,'')) in ('valid','válido','valido','ok')
          and coalesce(c.is_corporate,0)=1
          and c.email is not null and trim(c.email) <> ''
          and not exists (select 1 from suppression_list s where lower(s.email)=lower(c.email))
        order by coalesce(c.score,0) desc, c.email
    """)
    # Some historical validators used grades more than validity_status; include fallback if strict query is empty.
    if not verified:
        verified = rows(con, """
            select
              c.id as contact_id, c.email, c.name, c.role, c.phone, c.mobile,
              c.segment as contact_segment, c.source as contact_source,
              c.validity_status, c.grade, c.score, coalesce(c.is_corporate,0) as is_corporate,
              co.company_name, co.trading_name, co.legal_name, co.domain,
              co.segment as company_segment, co.city, co.state, co.icp_score
            from contacts c
            left join companies co on co.id = c.company_id
            where upper(coalesce(c.grade,'')) in ('A','B')
              and coalesce(c.is_corporate,0)=1
              and c.email is not null and trim(c.email) <> ''
              and not exists (select 1 from suppression_list s where lower(s.email)=lower(c.email))
            order by coalesce(c.score,0) desc, c.email
        """)
    return {
        'generated_at_utc': now_iso(),
        'source': str(DB),
        'method': 'sqlite read-only snapshot; no external writes; suppression list applied to verified export',
        'confidence': 'medium-high: source is local commercial intelligence DB; depends on freshness of ingestion/validation jobs',
        'risk_of_error': 'contacts may be stale if source enrichment or bounce suppression is outdated; HubSpot live state is not mutated here',
        'counts': counts,
        'validity_status': validity,
        'grades': grades,
        'campaign_recipient_status': campaign_status,
        'quality_flags': bad,
        'verified_contacts_count': len(verified),
        'verified_contacts': verified,
    }


def write_outputs(snapshot: dict[str, Any]) -> dict[str, str]:
    ensure_dirs()
    ts = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    manifest = {k: v for k, v in snapshot.items() if k != 'verified_contacts'}
    manifest['artifact_version'] = 'mensura-crm-pipeline-v1'
    manifest['entities'] = ['companies', 'contacts', 'suppression_list', 'campaigns', 'campaign_recipients', 'interactions']
    verified_path = OUT_ROOT / 'verified' / f'mensura-verified-contacts-{ts}.jsonl'
    latest_verified = OUT_ROOT / 'verified' / 'mensura-verified-contacts-latest.jsonl'
    crm_path = OUT_ROOT / 'crm' / f'mensura-crm-import-candidates-{ts}.jsonl'
    latest_crm = OUT_ROOT / 'crm' / 'mensura-crm-import-candidates-latest.jsonl'
    manifest_path = OUT_ROOT / 'crm' / f'mensura-crm-pipeline-manifest-{ts}.json'
    latest_manifest = OUT_ROOT / 'crm' / 'mensura-crm-pipeline-latest.json'
    csv_path = OUT_ROOT / 'crm' / f'mensura-crm-import-candidates-{ts}.csv'
    latest_csv = OUT_ROOT / 'crm' / 'mensura-crm-import-candidates-latest.csv'

    contacts = snapshot['verified_contacts']
    with verified_path.open('w', encoding='utf-8') as f1, crm_path.open('w', encoding='utf-8') as f2:
        for c in contacts:
            company = c.get('company_name') or c.get('trading_name') or c.get('legal_name')
            rec = {
                'external_id': sha256_text((c.get('email') or '').lower()),
                'email': c.get('email'),
                'name': c.get('name'),
                'role': c.get('role'),
                'company': company,
                'domain': c.get('domain'),
                'city': c.get('city'),
                'state': c.get('state'),
                'segment': c.get('company_segment') or c.get('contact_segment'),
                'lead_score': c.get('score'),
                'icp_score': c.get('icp_score'),
                'source': c.get('contact_source') or 'mensura-commercial-intelligence',
                'pipeline_stage': 'lead_identificado',
                'next_action': 'revisar para campanha/outreach; não enviar automaticamente',
                'confidence': 'medium' if c.get('grade') else 'medium-low',
            }
            f1.write(json.dumps(c, ensure_ascii=False) + '\n')
            f2.write(json.dumps(rec, ensure_ascii=False) + '\n')
    latest_verified.write_text(verified_path.read_text(encoding='utf-8'), encoding='utf-8')
    latest_crm.write_text(crm_path.read_text(encoding='utf-8'), encoding='utf-8')

    fieldnames = ['external_id','email','name','role','company','domain','city','state','segment','lead_score','icp_score','source','pipeline_stage','next_action','confidence']
    with csv_path.open('w', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for line in crm_path.read_text(encoding='utf-8').splitlines():
            w.writerow(json.loads(line))
    latest_csv.write_text(csv_path.read_text(encoding='utf-8'), encoding='utf-8')

    manifest['artifacts'] = {
        'verified_jsonl': str(verified_path),
        'crm_jsonl': str(crm_path),
        'crm_csv': str(csv_path),
    }
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    latest_manifest.write_text(manifest_path.read_text(encoding='utf-8'), encoding='utf-8')
    return {
        'manifest': str(manifest_path),
        'latest_manifest': str(latest_manifest),
        'verified_jsonl': str(verified_path),
        'latest_verified_jsonl': str(latest_verified),
        'crm_jsonl': str(crm_path),
        'latest_crm_jsonl': str(latest_crm),
        'crm_csv': str(csv_path),
        'latest_crm_csv': str(latest_csv),
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('--json', action='store_true')
    ap.add_argument('--write', action='store_true', help='write runtime artifacts')
    args = ap.parse_args()
    snapshot = load_snapshot()
    artifacts = write_outputs(snapshot) if args.write else {}
    payload = {k: v for k, v in snapshot.items() if k != 'verified_contacts'}
    payload['artifacts'] = artifacts
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print('Mensura CRM/CDP pipeline v1')
        print(f"- source: {snapshot['source']}")
        print(f"- contacts: {snapshot['counts']['contacts']}")
        print(f"- companies: {snapshot['counts']['companies']}")
        print(f"- suppression: {snapshot['counts']['suppression_list']}")
        print(f"- verified export candidates: {snapshot['verified_contacts_count']}")
        print(f"- quality flags: {snapshot['quality_flags']}")
        if artifacts:
            print(f"- latest manifest: {artifacts['latest_manifest']}")
            print(f"- latest CRM CSV: {artifacts['latest_crm_csv']}")


if __name__ == '__main__':
    main()
