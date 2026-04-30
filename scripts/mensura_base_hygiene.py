#!/usr/bin/env python3
"""MENSURA base hygiene — read-only campaign readiness filter.

Purpose:
- Take current local CRM/CDP candidates and campaign feedback.
- Suppress bounces, already-sent contacts, non-ICP/personal/role-based emails and weak records.
- Generate internal artifacts for review before any import/outreach.

Guardrails: no HubSpot writes, no email sends, no Telegram/Make calls.
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import sqlite3
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import dns.resolver

WORKSPACE = Path('/root/.openclaw/workspace')
DB = WORKSPACE / 'projects/mensura-commercial-intelligence/data/commercial-intelligence.sqlite'
CRM_CANDIDATES = WORKSPACE / 'runtime/data-pipeline/crm/mensura-crm-import-candidates-latest.csv'
CAMPAIGN_CLASSIFICATION = WORKSPACE / 'runtime/data-pipeline/crm/lead-intelligence/mensura-campaign-classification-latest.csv'
HUBSPOT_RECON = WORKSPACE / 'runtime/data-pipeline/crm/mensura-hubspot-reconciliation-latest.json'
OUT_ROOT = WORKSPACE / 'runtime/mensura-marketing/higienizacao-current'

ROLE_BASED_PREFIXES = {
    'adm','admin','administrativo','atendimento','cadastro','cobranca','cobrança','compras','comercial','contabilidade',
    'contato','contratos','diretoria','email','engenharia','financeiro','fiscal','geral','info','marketing','nfe','nf-e',
    'obras','orcamento','orçamento','ouvidoria','recepcao','recepção','rh','sac','secretaria','suporte','vendas'
}
PERSONAL_DOMAINS = {
    'gmail.com','hotmail.com','hotmail.com.br','outlook.com','outlook.com.br','live.com','live.com.br','yahoo.com',
    'yahoo.com.br','icloud.com','me.com','uol.com.br','bol.com.br','terra.com.br','ig.com.br','aol.com','proton.me'
}
NON_COMPANY_DOMAIN_SUFFIXES = ('.edu.br', '.edu', '.gov.br', '.org.br')
NON_COMPANY_DOMAIN_KEYWORDS = ('unicamp.br', 'insper.edu.br')
ICP_TERMS = ('construtora','incorporadora','real estate','engenharia','empreendimento','urbanismo')
DECISION_TERMS = (
    'diretor','diretora','ceo','cfo','coo','cto','sócio','socio','presidente','vp','gerente','head','superintendente',
    'coordenador','coordenadora','obra','obras','engenharia','planejamento','construção','construcao','incorporação','incorporacao'
)
LOW_RELEVANCE_ROLE_TERMS = ('comprador','compras','assistente','analista','estagi', 'auxiliar')
EMAIL_RE = re.compile(r'^[^@\s]+@[^@\s]+\.[^@\s]+$')


def now_ts() -> str:
    return datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline='', encoding='utf-8') as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
        w.writeheader()
        for row in rows:
            w.writerow(row)


def email_parts(email: str) -> tuple[str, str]:
    email = (email or '').strip().lower()
    if '@' not in email:
        return email, ''
    local, domain = email.rsplit('@', 1)
    return local, domain


def load_suppression() -> tuple[set[str], set[str]]:
    if not DB.exists():
        return set(), set()
    con = sqlite3.connect(DB)
    emails: set[str] = set()
    domains: set[str] = set()
    for email, domain in con.execute('select email, domain from suppression_list'):
        if email:
            emails.add(str(email).strip().lower())
        if domain:
            domains.add(str(domain).strip().lower())
    return emails, domains


def load_campaign_feedback() -> dict[str, dict[str, str]]:
    if not CAMPAIGN_CLASSIFICATION.exists():
        return {}
    return {r['email'].strip().lower(): r for r in read_csv(CAMPAIGN_CLASSIFICATION) if r.get('email')}


def dns_status(domain: str, cache: dict[str, str]) -> str:
    domain = (domain or '').strip().lower()
    if not domain:
        return 'missing_domain'
    if domain in cache:
        return cache[domain]
    try:
        answers = dns.resolver.resolve(domain, 'MX', lifetime=2.5)
        cache[domain] = 'mx_ok' if answers else 'no_mx'
    except Exception:
        try:
            answers = dns.resolver.resolve(domain, 'A', lifetime=2.5)
            cache[domain] = 'a_ok_no_mx' if answers else 'no_dns'
        except Exception:
            cache[domain] = 'no_dns'
    return cache[domain]


def classify(row: dict[str, str], suppression_emails: set[str], suppression_domains: set[str], sent: dict[str, dict[str, str]], dns_cache: dict[str, str]) -> dict[str, Any]:
    email = (row.get('email') or '').strip().lower()
    local, domain = email_parts(email)
    name = (row.get('name') or '').strip()
    role = (row.get('role') or '').strip()
    company = (row.get('company') or '').strip()
    segment = (row.get('segment') or '').strip().lower()
    source = row.get('source') or ''
    lead_score = int(float(row.get('lead_score') or 0))
    reasons: list[str] = []
    positives: list[str] = []

    if not EMAIL_RE.match(email):
        reasons.append('email_invalido')
    if email in suppression_emails:
        reasons.append('suppression_email')
    if domain in suppression_domains:
        reasons.append('suppression_domain')
    if email in sent:
        classification = sent[email].get('classification') or 'sent'
        reasons.append(f'lote01_{classification.replace(" ", "_")}')
    if domain in PERSONAL_DOMAINS:
        reasons.append('email_pessoal_ou_provedor_generico')
    if domain.endswith(NON_COMPANY_DOMAIN_SUFFIXES) or any(k in domain for k in NON_COMPANY_DOMAIN_KEYWORDS):
        reasons.append('dominio_institucional_nao_empresa')
    if local in ROLE_BASED_PREFIXES or any(local.startswith(p + '.') or local.startswith(p + '-') for p in ROLE_BASED_PREFIXES):
        reasons.append('email_generico_role_based')
    if not any(term in segment for term in ICP_TERMS):
        reasons.append('segmento_fora_icp_ou_ambíguo')
    if not company:
        reasons.append('sem_empresa')
    if not name:
        reasons.append('sem_nome_contato')
    if not role:
        reasons.append('sem_cargo')

    ds = dns_status(domain or (row.get('domain') or '').strip().lower(), dns_cache)
    if ds in ('no_dns','missing_domain','no_mx'):
        reasons.append(f'dns_{ds}')

    if any(term in role.lower() for term in DECISION_TERMS):
        positives.append('cargo_decisor_ou_influenciador')
    if any(term in segment for term in ICP_TERMS):
        positives.append('segmento_icp')
    if lead_score >= 85:
        positives.append('score_alto')
    if name and role:
        positives.append('contato_nomeado_com_cargo')
    if ds in ('mx_ok','a_ok_no_mx'):
        positives.append('dominio_resolve')

    hard_reject = any(r.startswith('suppression') or r.startswith('lote01_') or r in {'email_invalido','email_pessoal_ou_provedor_generico','dominio_institucional_nao_empresa','segmento_fora_icp_ou_ambíguo','dns_no_dns','dns_missing_domain','dns_no_mx'} for r in reasons)
    enrichment_needed = any(r in {'sem_nome_contato','sem_cargo','email_generico_role_based','sem_empresa'} for r in reasons)
    low_relevance_role = any(t in role.lower() for t in LOW_RELEVANCE_ROLE_TERMS)

    # scoring: conservative because cold-email reputation matters more than volume.
    hygiene_score = 0
    hygiene_score += 35 if 'segmento_icp' in positives else 0
    hygiene_score += 25 if 'cargo_decisor_ou_influenciador' in positives else 0
    hygiene_score += 15 if 'contato_nomeado_com_cargo' in positives else 0
    hygiene_score += 15 if 'dominio_resolve' in positives else 0
    hygiene_score += min(10, max(0, lead_score - 80))
    hygiene_score -= 30 if 'email_generico_role_based' in reasons else 0
    hygiene_score -= 20 if low_relevance_role else 0
    hygiene_score -= 15 if 'sem_nome_contato' in reasons else 0
    hygiene_score -= 15 if 'sem_cargo' in reasons else 0
    hygiene_score -= 100 if hard_reject else 0
    hygiene_score = max(0, min(100, hygiene_score))

    if hard_reject:
        tier = 'rejeitar'
        next_action = 'manter fora de campanha e CRM write; preservar como evidência/suppression'
    elif hygiene_score >= 75 and not enrichment_needed and not low_relevance_role:
        tier = 'A_pronto_revisao'
        next_action = 'apto para revisão humana de próximo lote; não enviar automaticamente'
    elif hygiene_score >= 55 and not hard_reject:
        tier = 'B_enriquecer'
        next_action = 'enriquecer cargo/nome/empresa antes de campanha'
    else:
        tier = 'C_baixa_prioridade'
        next_action = 'não usar em lote frio agora; manter para enriquecimento futuro'

    return {
        'email': email,
        'company': company,
        'domain': domain or row.get('domain',''),
        'name': name,
        'role': role,
        'segment': row.get('segment') or '',
        'lead_score': lead_score,
        'hygiene_score': hygiene_score,
        'tier': tier,
        'dns_status': ds,
        'hubspot_reconcile_status': row.get('hubspot_reconcile_status') or '',
        'source': source,
        'reasons': ';'.join(reasons),
        'positives': ';'.join(positives),
        'next_action': next_action,
    }


def one_per_domain(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    best: dict[str, dict[str, Any]] = {}
    for r in rows:
        d = (r.get('domain') or '').lower()
        if not d:
            continue
        old = best.get(d)
        if old is None or (int(r['hygiene_score']), int(r['lead_score']), r['email']) > (int(old['hygiene_score']), int(old['lead_score']), old['email']):
            best[d] = r
    return sorted(best.values(), key=lambda r: (-int(r['hygiene_score']), -int(r['lead_score']), r['domain'], r['email']))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('--write', action='store_true')
    ap.add_argument('--json', action='store_true')
    ap.add_argument('--limit-dns', type=int, default=0, help='for test only; 0 = all domains')
    args = ap.parse_args()

    candidates = read_csv(CRM_CANDIDATES)
    suppression_emails, suppression_domains = load_suppression()
    feedback = load_campaign_feedback()
    dns_cache: dict[str, str] = {}

    if args.limit_dns:
        # prefill after limit with unknown to keep fast tests deterministic.
        seen = []
        for r in candidates:
            d = email_parts(r.get('email',''))[1] or r.get('domain','')
            if d and d not in seen:
                seen.append(d)
        for d in seen[args.limit_dns:]:
            dns_cache[d] = 'not_checked_test_limit'

    scored = [classify(r, suppression_emails, suppression_domains, feedback, dns_cache) for r in candidates]
    tier_counts = Counter(r['tier'] for r in scored)
    dns_counts = Counter(r['dns_status'] for r in scored)
    reason_counts: Counter[str] = Counter()
    for r in scored:
        for reason in filter(None, str(r['reasons']).split(';')):
            reason_counts[reason] += 1

    tier_a = [r for r in scored if r['tier'] == 'A_pronto_revisao']
    tier_a_1domain = one_per_domain(tier_a)
    next_lot_30 = tier_a_1domain[:30]
    enrich = sorted([r for r in scored if r['tier'] == 'B_enriquecer'], key=lambda r: (-int(r['hygiene_score']), r['domain'], r['email']))
    rejected = [r for r in scored if r['tier'] == 'rejeitar']

    summary = {
        'generated_at_utc': now_iso(),
        'mode': 'read_only',
        'external_writes': False,
        'source_files': {
            'crm_candidates': str(CRM_CANDIDATES),
            'campaign_classification': str(CAMPAIGN_CLASSIFICATION),
            'hubspot_reconciliation': str(HUBSPOT_RECON),
            'sqlite_suppression': str(DB),
        },
        'method': 'rule-based conservative hygiene + suppression + campaign feedback + DNS MX/A check; no external writes',
        'input_total': len(candidates),
        'suppression_emails': len(suppression_emails),
        'suppression_domains': len(suppression_domains),
        'campaign_feedback_contacts': len(feedback),
        'dns_domains_checked': len([d for d, s in dns_cache.items() if s != 'not_checked_test_limit']),
        'tier_counts': dict(tier_counts),
        'dns_counts': dict(dns_counts),
        'top_rejection_or_hold_reasons': dict(reason_counts.most_common(20)),
        'recommended_next_lot_size': len(next_lot_30),
        'tier_a_unique_domains': len(tier_a_1domain),
        'recommendation': 'Não escalar volume ainda. Usar no máximo 30 contatos Tier A com revisão humana, 1 por domínio, após confirmar copy e cadência. Prioridade paralela: enriquecer Tier B antes de novo lote.',
        'guardrails': ['sem HubSpot import', 'sem email', 'sem Telegram', 'sem Make run', 'sem alteração CRM'],
    }

    ts = now_ts()
    artifacts = {}
    if args.write:
        OUT_ROOT.mkdir(parents=True, exist_ok=True)
        fields = ['email','company','domain','name','role','segment','lead_score','hygiene_score','tier','dns_status','hubspot_reconcile_status','source','reasons','positives','next_action']
        outputs = {
            f'base-higienizada-{ts}.csv': scored,
            f'tier-a-pronto-revisao-{ts}.csv': tier_a,
            f'tier-a-1por-dominio-{ts}.csv': tier_a_1domain,
            f'proximo-lote-sugerido-30-{ts}.csv': next_lot_30,
            f'tier-b-enriquecer-{ts}.csv': enrich,
            f'rejeitados-suppression-hold-{ts}.csv': rejected,
        }
        for filename, rows in outputs.items():
            p = OUT_ROOT / filename
            write_csv(p, rows, fields)
            latest = OUT_ROOT / filename.replace(f'-{ts}', '-latest')
            latest.write_text(p.read_text(encoding='utf-8'), encoding='utf-8')
            artifacts[filename.rsplit('-', 1)[0]] = str(p)
        summary_path = OUT_ROOT / f'summary-{ts}.json'
        summary['artifacts'] = artifacts
        summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        (OUT_ROOT / 'summary-latest.json').write_text(summary_path.read_text(encoding='utf-8'), encoding='utf-8')
        alert = OUT_ROOT / f'alerta-higienizacao-{ts}.md'
        alert.write_text(
            '# MENSURA — Higienização de base\n\n'
            f"- Gerado em UTC: {summary['generated_at_utc']}\n"
            f"- Base de entrada: {summary['input_total']} contatos\n"
            f"- Tier A pronto para revisão: {tier_counts.get('A_pronto_revisao',0)}\n"
            f"- Tier A 1 por domínio: {summary['tier_a_unique_domains']}\n"
            f"- Próximo lote sugerido: {summary['recommended_next_lot_size']} contatos\n"
            f"- Tier B para enriquecer: {tier_counts.get('B_enriquecer',0)}\n"
            f"- Rejeitar/hold: {tier_counts.get('rejeitar',0)}\n\n"
            '## Recomendação\n\n'
            f"{summary['recommendation']}\n\n"
            '## Guardrails\n\n'
            '- Sem import HubSpot.\n- Sem disparo de email.\n- Sem Make run.\n- Sem envio externo.\n',
            encoding='utf-8'
        )
        (OUT_ROOT / 'alerta-higienizacao-latest.md').write_text(alert.read_text(encoding='utf-8'), encoding='utf-8')
        summary['artifacts']['summary'] = str(summary_path)
        summary['artifacts']['alert'] = str(alert)

    if args.json:
        print(json.dumps(summary, ensure_ascii=False, indent=2))
    else:
        print('MENSURA base hygiene read-only')
        print(f"- input_total: {summary['input_total']}")
        print(f"- tier_counts: {summary['tier_counts']}")
        print(f"- tier_a_unique_domains: {summary['tier_a_unique_domains']}")
        print(f"- recommended_next_lot_size: {summary['recommended_next_lot_size']}")
        print(f"- dns_counts: {summary['dns_counts']}")
        if artifacts:
            print(f"- output_dir: {OUT_ROOT}")


if __name__ == '__main__':
    main()
