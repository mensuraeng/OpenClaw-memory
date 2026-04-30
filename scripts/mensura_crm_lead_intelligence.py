#!/usr/bin/env python3
"""Mensura CRM/CDP + Lead Intelligence — read-only report.

Combines existing local CRM/CDP artifacts, HubSpot reconciliation snapshots and
MENSURA cold-campaign return logs into auditable JSON/CSV/Markdown outputs.

Guardrails:
- no HubSpot imports/writes;
- no email sends;
- no Telegram sends;
- no Make/scenario calls;
- no mutation of CRM or mailbox state.
"""
from __future__ import annotations

import argparse
import csv
import json
import re
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

WORKSPACE = Path('/root/.openclaw/workspace')
CRM_DIR = WORKSPACE / 'runtime/data-pipeline/crm'
LEDGER_CSV = CRM_DIR / 'lead-ledger/mensura-lead-ledger-latest.csv'
CANDIDATES_CSV = CRM_DIR / 'mensura-crm-import-candidates-latest.csv'
RECON_JSON = CRM_DIR / 'mensura-hubspot-reconciliation-latest.json'
PIPELINE_JSON = CRM_DIR / 'mensura-crm-pipeline-latest.json'
CAMPAIGN_DIR = WORKSPACE / 'runtime/mensura-marketing/campanha-20260427'
OUT_DIR = CRM_DIR / 'lead-intelligence'

CAMPAIGN_SUBJECT = 'Quando o cronograma vira instrumento de decisão'
CAMPAIGN_CLASSES = [
    'interesse positivo',
    'neutro',
    'sem timing',
    'descadastro/não interesse',
    'bounce',
    'sem resposta',
]

EMAIL_RE = re.compile(r'[A-Z0-9._%+\-]+@[A-Z0-9.\-]+\.[A-Z]{2,}', re.I)


@dataclass(frozen=True)
class CampaignRecipient:
    email: str
    empresa: str = ''
    nome: str = ''
    cargo: str = ''
    segmento: str = ''
    status_envio: str = ''


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def ts_label() -> str:
    return datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(newline='', encoding='utf-8') as f:
        return [dict(r) for r in csv.DictReader(f)]


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding='utf-8'))


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    with path.open('w', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
        w.writeheader()
        for row in rows:
            w.writerow({k: row.get(k, '') for k in fieldnames})


def norm_email(value: str | None) -> str:
    return (value or '').strip().lower()


def load_campaign_recipients() -> dict[str, CampaignRecipient]:
    rows = read_csv(CAMPAIGN_DIR / 'lote-01-envio-log.csv')
    recipients: dict[str, CampaignRecipient] = {}
    for r in rows:
        email = norm_email(r.get('email'))
        if not email:
            continue
        recipients[email] = CampaignRecipient(
            email=email,
            empresa=r.get('empresa', ''),
            nome=r.get('nome', ''),
            cargo=r.get('cargo', ''),
            segmento=r.get('segmento', ''),
            status_envio=r.get('status', ''),
        )
    return recipients


def item_text(item: dict[str, Any]) -> str:
    return '\n'.join(str(item.get(k) or '') for k in ['subject', 'preview', 'bodyPreview', 'from']).lower()


def extract_recipient(item: dict[str, Any], recipients: dict[str, CampaignRecipient]) -> str | None:
    explicit = norm_email(item.get('matched_recipient'))
    if explicit in recipients:
        return explicit
    sender = norm_email(item.get('from'))
    if sender in recipients:
        return sender
    text = item_text(item)
    for email in EMAIL_RE.findall(text):
        e = norm_email(email)
        if e in recipients:
            return e
    for email in recipients:
        if email in text:
            return email
    return None


def is_campaign_related(item: dict[str, Any], recipients: dict[str, CampaignRecipient]) -> bool:
    subject = str(item.get('subject') or '').lower()
    if CAMPAIGN_SUBJECT.lower() in subject:
        return True
    return extract_recipient(item, recipients) is not None


def normalize_campaign_class(item: dict[str, Any]) -> str:
    cls = str(item.get('classification') or '').strip().lower()
    if cls in CAMPAIGN_CLASSES:
        return cls
    text = item_text(item)
    subj = str(item.get('subject') or '').lower()
    if 'undeliverable:' in subj or 'delivery has failed' in text or "couldn't be delivered" in text or 'não foi entregue' in text:
        return 'bounce'
    if any(x in text for x in ['descadastrar', 'remover', 'não tenho interesse', 'nao tenho interesse', 'não me envie', 'nao me envie', 'unsubscribe']):
        return 'descadastro/não interesse'
    if any(x in text for x in ['sem timing', 'agora não', 'agora nao', 'no momento', 'futuro', 'mais pra frente', 'mais para frente']):
        return 'sem timing'
    if any(x in text for x in ['interesse', 'podemos conversar', 'vamos conversar', 'reunião', 'reuniao', 'agenda', 'proposta', 'conhecer melhor']):
        return 'interesse positivo'
    return 'neutro'


def class_priority(cls: str) -> int:
    # Recipient state priority. Bounce wins over no response; positive wins over neutral if a real recipient reply exists.
    order = {
        'interesse positivo': 6,
        'sem timing': 5,
        'descadastro/não interesse': 5,
        'neutro': 4,
        'bounce': 3,
        'sem resposta': 1,
    }
    return order.get(cls, 0)


def next_action_for_class(cls: str) -> str:
    return {
        'interesse positivo': 'preparar resposta personalizada e pedir aprovação antes de qualquer envio externo',
        'neutro': 'revisar contexto; não responder automaticamente; manter em nutrição se fizer sentido',
        'sem timing': 'registrar timing futuro; não insistir agora; revisar cadência em 30-60 dias',
        'descadastro/não interesse': 'suprimir de novos disparos; não contatar novamente sem base legal/validação',
        'bounce': 'higienizar email/domínio antes de novo lote; não importar/escalar sem revisão',
        'sem resposta': 'elegível a follow-up interno se ICP continuar válido; não enviar automaticamente',
    }.get(cls, 'revisar manualmente')


def load_campaign_items(recipients: dict[str, CampaignRecipient]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    unique: dict[str, dict[str, Any]] = {}
    ignored: list[dict[str, Any]] = []
    for path in sorted(CAMPAIGN_DIR.glob('retornos-check-*.json')):
        if 'new-since-last' in path.name:
            continue
        doc = read_json(path)
        items = doc.get('items') or doc.get('campaign_related') or []
        for idx, item in enumerate(items):
            if not isinstance(item, dict):
                continue
            recipient = extract_recipient(item, recipients)
            related = is_campaign_related(item, recipients)
            if not related:
                ignored.append({
                    'source_file': str(path),
                    'reason': 'sem vínculo com campanha/lote; provável ruído de inbox',
                    'from': item.get('from'),
                    'subject': item.get('subject'),
                    'classification_original': item.get('classification'),
                })
                continue
            rec = dict(item)
            rec['source_file'] = str(path)
            rec['matched_recipient_normalized'] = recipient or ''
            rec['classification_normalized'] = normalize_campaign_class(item)
            # Older check files did not persist Graph message ids. Dedupe by stable campaign evidence first
            # so the same bounce copied across multiple snapshots does not inflate event_count.
            stable_key = f"{recipient}|{rec['classification_normalized']}|{item.get('receivedDateTime')}|{item.get('subject')}"
            key = stable_key if recipient else (item.get('id') or f"{item.get('receivedDateTime')}|{item.get('from')}|{item.get('subject')}|{idx}")
            unique[str(key)] = rec
    return list(unique.values()), ignored


def build_recipient_status(recipients: dict[str, CampaignRecipient], items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_recipient: dict[str, list[dict[str, Any]]] = defaultdict(list)
    unmatched: list[dict[str, Any]] = []
    for item in items:
        rec = norm_email(item.get('matched_recipient_normalized'))
        if rec and rec in recipients:
            by_recipient[rec].append(item)
        else:
            unmatched.append(item)

    rows: list[dict[str, Any]] = []
    for email, recipient in sorted(recipients.items()):
        events = by_recipient.get(email, [])
        cls = 'sem resposta'
        latest_dt = ''
        evidence_subjects: list[str] = []
        for ev in events:
            ev_cls = ev.get('classification_normalized') or 'neutro'
            if class_priority(ev_cls) > class_priority(cls):
                cls = ev_cls
            dt = str(ev.get('receivedDateTime') or '')
            if dt > latest_dt:
                latest_dt = dt
            subj = str(ev.get('subject') or '')
            if subj and subj not in evidence_subjects:
                evidence_subjects.append(subj)
        rows.append({
            'email': email,
            'empresa': recipient.empresa,
            'nome': recipient.nome,
            'cargo': recipient.cargo,
            'segmento': recipient.segmento,
            'status_envio': recipient.status_envio,
            'classification': cls,
            'event_count': len(events),
            'latest_event_at': latest_dt,
            'next_action': next_action_for_class(cls),
            'evidence_subjects': ' | '.join(evidence_subjects[:3]),
        })
    # Preserve unmatched campaign-related events as review rows; usually this should be zero after extraction.
    for ev in unmatched:
        rows.append({
            'email': '',
            'empresa': '',
            'nome': '',
            'cargo': '',
            'segmento': '',
            'status_envio': '',
            'classification': ev.get('classification_normalized') or 'neutro',
            'event_count': 1,
            'latest_event_at': ev.get('receivedDateTime') or '',
            'next_action': 'revisar evento sem destinatário correspondente no lote; não agir automaticamente',
            'evidence_subjects': ev.get('subject') or '',
        })
    return rows


def lead_score_bucket(score: str | int | None) -> str:
    try:
        s = int(float(score or 0))
    except Exception:
        s = 0
    if s >= 90:
        return 'A'
    if s >= 70:
        return 'B'
    if s > 0:
        return 'C'
    return 'unknown'


def build_crm_diff_rows(ledger: list[dict[str, str]], candidates: list[dict[str, str]], recon: dict[str, Any]) -> list[dict[str, Any]]:
    candidates_by_email = {norm_email(r.get('email')): r for r in candidates if norm_email(r.get('email'))}
    missing_samples = set(norm_email(e) for e in (recon.get('samples', {}).get('valid_local_missing_in_hubspot') or []))
    rows: list[dict[str, Any]] = []
    seen: set[str] = set()
    for r in ledger:
        email = norm_email(r.get('email'))
        if not email or email in seen:
            continue
        seen.add(email)
        cand = candidates_by_email.get(email, {})
        status = r.get('hubspot_reconcile_status') or 'unknown'
        if email in missing_samples:
            status = 'missing_in_hubspot_sample'
        rows.append({
            'email': email,
            'company': r.get('company') or cand.get('company') or '',
            'domain': r.get('domain') or cand.get('domain') or '',
            'name': r.get('name') or cand.get('name') or '',
            'role': r.get('role') or cand.get('role') or '',
            'segment': r.get('segment') or cand.get('segment') or '',
            'lead_score': r.get('lead_score') or cand.get('lead_score') or '',
            'lead_grade': lead_score_bucket(r.get('lead_score') or cand.get('lead_score')),
            'pipeline_stage': r.get('pipeline_stage') or cand.get('pipeline_stage') or '',
            'hubspot_reconcile_status': status,
            'diff_action': 'validar antes de qualquer import/write; relatório é read-only',
            'source': r.get('source') or cand.get('source') or '',
            'confidence': r.get('confidence') or cand.get('confidence') or '',
        })
    return rows


def compute_alerts(recon: dict[str, Any], recipient_rows: list[dict[str, Any]], ignored_items: list[dict[str, Any]]) -> list[dict[str, str]]:
    alerts: list[dict[str, str]] = []
    gaps = recon.get('gaps') or {}
    missing_emails = int(gaps.get('valid_local_emails_missing_in_hubspot') or 0)
    missing_domains = int(gaps.get('local_domains_missing_in_hubspot') or 0)
    if missing_emails:
        alerts.append({
            'severity': 'attention',
            'topic': 'crm_diff',
            'message': f'{missing_emails} emails locais válidos não aparecem no HubSpot no snapshot atual.',
            'recommendation': 'revisar amostra e decidir import controlado; este relatório não executa write.',
        })
    if missing_domains:
        alerts.append({
            'severity': 'attention',
            'topic': 'crm_domain_diff',
            'message': f'{missing_domains} domínios locais não aparecem como empresas no HubSpot.',
            'recommendation': 'priorizar domínios ICP alto antes de qualquer importação de empresa.',
        })
    counts = Counter(r['classification'] for r in recipient_rows if r.get('email'))
    sent = sum(counts.values())
    bounces = counts.get('bounce', 0)
    if sent and bounces / sent >= 0.25:
        alerts.append({
            'severity': 'high',
            'topic': 'campaign_bounce_rate',
            'message': f'Taxa de bounce do lote: {bounces}/{sent} ({bounces/sent:.1%}).',
            'recommendation': 'pausar escala de novos lotes até higienizar base; preservar apenas follow-up manual de contatos válidos.',
        })
    if counts.get('interesse positivo', 0):
        alerts.append({
            'severity': 'opportunity',
            'topic': 'campaign_positive_response',
            'message': f'{counts["interesse positivo"]} resposta(s) positiva(s) vinculada(s à campanha).',
            'recommendation': 'preparar resposta individual e solicitar aprovação antes do envio.',
        })
    if ignored_items:
        alerts.append({
            'severity': 'info',
            'topic': 'campaign_noise_filtered',
            'message': f'{len(ignored_items)} item(ns) de inbox foram ignorados por não terem vínculo com lote/campanha.',
            'recommendation': 'manter filtro por assunto/destinatário para reduzir falso positivo.',
        })
    return alerts


def markdown_alerts(payload: dict[str, Any]) -> str:
    lines = [
        '# Mensura CRM/CDP + Lead Intelligence — alerta interno',
        '',
        f"_Gerado em UTC: {payload['generated_at_utc']}_",
        '',
        '## Status',
        '',
        f"- Modo: `{payload['mode']}`",
        f"- Writes externos: `{payload['external_writes']}`",
        f"- Confiança: {payload['confidence']}",
        '',
        '## Resumo',
        '',
    ]
    summary = payload['summary']
    for k, v in summary.items():
        lines.append(f'- {k}: {v}')
    lines.extend(['', '## Alertas/Recomendações internas', ''])
    if not payload['alerts']:
        lines.append('- Nenhum alerta material.')
    for a in payload['alerts']:
        lines.extend([
            f"### {a['severity']} — {a['topic']}",
            f"- Evidência: {a['message']}",
            f"- Recomendação: {a['recommendation']}",
            '',
        ])
    lines.extend([
        '## Guardrails',
        '',
        '- Não importar no HubSpot automaticamente.',
        '- Não enviar email/follow-up automaticamente.',
        '- Não enviar Telegram automaticamente.',
        '- Não chamar Make/scenario run.',
        '- Qualquer ação externa exige aprovação explícita do Alê.',
        '',
    ])
    return '\n'.join(lines)


def run(write: bool = True) -> dict[str, Any]:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    ledger = read_csv(LEDGER_CSV)
    candidates = read_csv(CANDIDATES_CSV)
    recon = read_json(RECON_JSON)
    pipeline = read_json(PIPELINE_JSON)
    recipients = load_campaign_recipients()
    campaign_items, ignored_items = load_campaign_items(recipients)
    recipient_rows = build_recipient_status(recipients, campaign_items)
    diff_rows = build_crm_diff_rows(ledger, candidates, recon)
    campaign_counts = Counter(r['classification'] for r in recipient_rows if r.get('email'))
    diff_counts = Counter(r['hubspot_reconcile_status'] for r in diff_rows)
    alerts = compute_alerts(recon, recipient_rows, ignored_items)

    label = ts_label()
    json_path = OUT_DIR / f'mensura-lead-intelligence-{label}.json'
    csv_diff_path = OUT_DIR / f'mensura-lead-intelligence-diff-{label}.csv'
    csv_campaign_path = OUT_DIR / f'mensura-campaign-classification-{label}.csv'
    alert_path = OUT_DIR / f'mensura-lead-intelligence-alert-{label}.md'
    latest_json = OUT_DIR / 'mensura-lead-intelligence-latest.json'
    latest_diff = OUT_DIR / 'mensura-lead-intelligence-diff-latest.csv'
    latest_campaign = OUT_DIR / 'mensura-campaign-classification-latest.csv'
    latest_alert = OUT_DIR / 'mensura-lead-intelligence-alert-latest.md'

    payload = {
        'generated_at_utc': now_iso(),
        'mode': 'read_only',
        'external_writes': False,
        'source_files': {
            'lead_ledger_csv': str(LEDGER_CSV),
            'crm_candidates_csv': str(CANDIDATES_CSV),
            'hubspot_reconciliation_json': str(RECON_JSON),
            'crm_pipeline_json': str(PIPELINE_JSON),
            'campaign_dir': str(CAMPAIGN_DIR),
        },
        'method': 'local CSV/JSON set comparison + campaign return consolidation; no CRM/email/Telegram/Make writes',
        'confidence': 'medium-high for local artifacts; HubSpot diff depends on freshness of reconciliation snapshot',
        'risk_of_error': 'HubSpot reconciliation latest may be stale; campaign classification is rule-based and requires review before external action',
        'summary': {
            'ledger_rows': len(ledger),
            'crm_candidate_rows': len(candidates),
            'campaign_sent': len(recipients),
            'campaign_classified_recipients': len(recipient_rows),
            'campaign_counts': dict(campaign_counts),
            'campaign_noise_filtered': len(ignored_items),
            'crm_diff_rows': len(diff_rows),
            'crm_diff_status_counts': dict(diff_counts),
            'hubspot_gap_counts': recon.get('gaps', {}),
            'pipeline_counts': pipeline.get('counts', {}),
            'alert_count': len(alerts),
        },
        'alerts': alerts,
        'artifacts': {
            'json': str(json_path),
            'latest_json': str(latest_json),
            'diff_csv': str(csv_diff_path),
            'latest_diff_csv': str(latest_diff),
            'campaign_csv': str(csv_campaign_path),
            'latest_campaign_csv': str(latest_campaign),
            'alert_markdown': str(alert_path),
            'latest_alert_markdown': str(latest_alert),
        },
        'samples': {
            'hubspot_missing_email_samples': (recon.get('samples', {}) or {}).get('valid_local_missing_in_hubspot', [])[:25],
            'alerts': alerts[:10],
            'ignored_campaign_noise': ignored_items[:10],
        },
    }

    if write:
        json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        latest_json.write_text(json_path.read_text(encoding='utf-8'), encoding='utf-8')
        diff_fields = ['email','company','domain','name','role','segment','lead_score','lead_grade','pipeline_stage','hubspot_reconcile_status','diff_action','source','confidence']
        campaign_fields = ['email','empresa','nome','cargo','segmento','status_envio','classification','event_count','latest_event_at','next_action','evidence_subjects']
        write_csv(csv_diff_path, diff_rows, diff_fields)
        latest_diff.write_text(csv_diff_path.read_text(encoding='utf-8'), encoding='utf-8')
        write_csv(csv_campaign_path, recipient_rows, campaign_fields)
        latest_campaign.write_text(csv_campaign_path.read_text(encoding='utf-8'), encoding='utf-8')
        alert_path.write_text(markdown_alerts(payload), encoding='utf-8')
        latest_alert.write_text(alert_path.read_text(encoding='utf-8'), encoding='utf-8')
    return payload


def main() -> None:
    ap = argparse.ArgumentParser(description='Mensura CRM/CDP + Lead Intelligence read-only report')
    ap.add_argument('--no-write', action='store_true', help='do not write runtime artifacts')
    ap.add_argument('--json', action='store_true', help='print full JSON payload')
    args = ap.parse_args()
    payload = run(write=not args.no_write)
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        s = payload['summary']
        print('Mensura CRM/CDP + Lead Intelligence')
        print(f"- mode: {payload['mode']} / external_writes={payload['external_writes']}")
        print(f"- ledger rows: {s['ledger_rows']}")
        print(f"- CRM diff rows: {s['crm_diff_rows']}")
        print(f"- campaign sent: {s['campaign_sent']}")
        print(f"- campaign counts: {s['campaign_counts']}")
        print(f"- alerts: {s['alert_count']}")
        for k, v in payload['artifacts'].items():
            if k.startswith('latest'):
                print(f"- {k}: {v}")


if __name__ == '__main__':
    main()
