#!/usr/bin/env python3
"""Persist MENSURA lead hygiene artifacts into local SQLite.

Internal-only derived layer. Does not call HubSpot, email, Telegram or Make.
"""
from __future__ import annotations

import argparse
import csv
import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

WORKSPACE = Path('/root/.openclaw/workspace')
DB = WORKSPACE / 'projects/mensura-commercial-intelligence/data/commercial-intelligence.sqlite'
HYGIENE_DIR = WORKSPACE / 'runtime/mensura-marketing/higienizacao-current'
SUMMARY = HYGIENE_DIR / 'summary-latest.json'
BASE = HYGIENE_DIR / 'base-higienizada-latest.csv'
NEXT_LOT = HYGIENE_DIR / 'proximo-lote-sugerido-30-latest.csv'


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline='', encoding='utf-8') as f:
        return list(csv.DictReader(f))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('--write', action='store_true')
    ap.add_argument('--json', action='store_true')
    args = ap.parse_args()

    if not DB.exists():
        raise SystemExit(f'DB não encontrado: {DB}')
    if not SUMMARY.exists() or not BASE.exists() or not NEXT_LOT.exists():
        raise SystemExit('Artefatos de higienização não encontrados; rode scripts/mensura_base_hygiene.py --write --json antes.')

    summary = json.loads(SUMMARY.read_text(encoding='utf-8'))
    rows = read_csv(BASE)
    next_emails = {r['email'].strip().lower() for r in read_csv(NEXT_LOT)}
    generated = summary.get('generated_at_utc') or now_iso()
    run_id = generated.replace(':', '').replace('-', '').replace('+0000', 'Z').replace('+00:00', 'Z')

    payload = {
        'mode': 'read_only_source_to_local_db',
        'external_writes': False,
        'run_id': run_id,
        'db': str(DB),
        'summary': {
            'input_total': summary.get('input_total'),
            'tier_counts': summary.get('tier_counts'),
            'tier_a_unique_domains': summary.get('tier_a_unique_domains'),
            'recommended_next_lot_size': summary.get('recommended_next_lot_size'),
        },
        'rows_to_persist': len(rows),
        'next_lot_emails': len(next_emails),
    }

    if args.write:
        con = sqlite3.connect(DB)
        try:
            con.execute('pragma foreign_keys=on')
            con.executescript('''
            create table if not exists lead_hygiene_runs (
              run_id text primary key,
              generated_at_utc text not null,
              source_summary_path text not null,
              input_total integer not null,
              tier_a_ready integer not null,
              tier_a_unique_domains integer not null,
              next_lot_suggested integer not null,
              tier_b_enrich integer not null,
              rejected_hold integer not null,
              low_priority integer not null,
              recommendation text,
              external_writes integer not null default 0,
              created_at text not null default current_timestamp
            );
            create table if not exists lead_hygiene_results (
              run_id text not null,
              email text not null,
              company text,
              domain text,
              name text,
              role text,
              segment text,
              lead_score integer,
              hygiene_score integer,
              tier text not null,
              dns_status text,
              hubspot_reconcile_status text,
              source text,
              reasons text,
              positives text,
              next_action text,
              selected_next_lot integer not null default 0,
              created_at text not null default current_timestamp,
              primary key (run_id, email),
              foreign key (run_id) references lead_hygiene_runs(run_id) on delete cascade
            );
            create index if not exists idx_lead_hygiene_results_email on lead_hygiene_results(email);
            create index if not exists idx_lead_hygiene_results_tier on lead_hygiene_results(tier);
            create index if not exists idx_lead_hygiene_results_domain on lead_hygiene_results(domain);
            create view if not exists lead_hygiene_current as
              select r.*
              from lead_hygiene_results r
              join (select run_id from lead_hygiene_runs order by generated_at_utc desc limit 1) latest
                on latest.run_id = r.run_id;
            create view if not exists lead_hygiene_next_lot_current as
              select * from lead_hygiene_current where selected_next_lot = 1 order by hygiene_score desc, domain, email;
            ''')
            tiers = summary.get('tier_counts') or {}
            con.execute('''
              insert or replace into lead_hygiene_runs (
                run_id, generated_at_utc, source_summary_path, input_total, tier_a_ready,
                tier_a_unique_domains, next_lot_suggested, tier_b_enrich, rejected_hold,
                low_priority, recommendation, external_writes
              ) values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0)
            ''', (
                run_id,
                generated,
                str(SUMMARY),
                int(summary.get('input_total') or 0),
                int(tiers.get('A_pronto_revisao') or 0),
                int(summary.get('tier_a_unique_domains') or 0),
                int(summary.get('recommended_next_lot_size') or 0),
                int(tiers.get('B_enriquecer') or 0),
                int(tiers.get('rejeitar') or 0),
                int(tiers.get('C_baixa_prioridade') or 0),
                summary.get('recommendation') or '',
            ))
            con.execute('delete from lead_hygiene_results where run_id=?', (run_id,))
            for row in rows:
                email = (row.get('email') or '').strip().lower()
                con.execute('''
                  insert into lead_hygiene_results (
                    run_id, email, company, domain, name, role, segment, lead_score, hygiene_score,
                    tier, dns_status, hubspot_reconcile_status, source, reasons, positives,
                    next_action, selected_next_lot
                  ) values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    run_id, email, row.get('company'), row.get('domain'), row.get('name'), row.get('role'),
                    row.get('segment'), int(row.get('lead_score') or 0), int(row.get('hygiene_score') or 0),
                    row.get('tier'), row.get('dns_status'), row.get('hubspot_reconcile_status'), row.get('source'),
                    row.get('reasons'), row.get('positives'), row.get('next_action'), 1 if email in next_emails else 0,
                ))
            con.commit()
            payload['persisted'] = True
            payload['db_counts'] = {
                'lead_hygiene_runs': con.execute('select count(*) from lead_hygiene_runs').fetchone()[0],
                'lead_hygiene_results_for_run': con.execute('select count(*) from lead_hygiene_results where run_id=?', (run_id,)).fetchone()[0],
                'lead_hygiene_next_lot_current': con.execute('select count(*) from lead_hygiene_next_lot_current').fetchone()[0],
                'unique_next_lot_domains': con.execute('select count(distinct domain) from lead_hygiene_next_lot_current').fetchone()[0],
            }
            payload['integrity_check'] = con.execute('pragma integrity_check').fetchone()[0]
        finally:
            con.close()
    else:
        payload['persisted'] = False

    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(f"run_id={run_id}")
        print(f"rows_to_persist={len(rows)} next_lot={len(next_emails)}")
        if payload.get('persisted'):
            print(payload['db_counts'])


if __name__ == '__main__':
    main()
