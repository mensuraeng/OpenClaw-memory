# Mensura CRM/CDP + Lead Intelligence — alerta interno

_Gerado em UTC: 2026-04-30T07:56:02.877084+00:00_

## Status

- Modo: `read_only`
- Writes externos: `False`
- Confiança: medium-high for local artifacts; HubSpot diff depends on freshness of reconciliation snapshot

## Resumo

- ledger_rows: 767
- crm_candidate_rows: 767
- campaign_sent: 30
- campaign_classified_recipients: 30
- campaign_counts: {'sem resposta': 12, 'bounce': 18}
- campaign_noise_filtered: 3
- crm_diff_rows: 767
- crm_diff_status_counts: {'candidate_or_present': 767}
- hubspot_gap_counts: {'valid_local_emails_missing_in_hubspot': 25, 'hubspot_emails_missing_in_local': 0, 'local_domains_missing_in_hubspot': 111, 'hubspot_domains_missing_in_local': 0}
- pipeline_counts: {'companies': 477, 'contacts': 1242, 'suppression_list': 474, 'campaigns': 0, 'campaign_recipients': 0, 'interactions': 0}
- alert_count: 4

## Alertas/Recomendações internas

### attention — crm_diff
- Evidência: 25 emails locais válidos não aparecem no HubSpot no snapshot atual.
- Recomendação: revisar amostra e decidir import controlado; este relatório não executa write.

### attention — crm_domain_diff
- Evidência: 111 domínios locais não aparecem como empresas no HubSpot.
- Recomendação: priorizar domínios ICP alto antes de qualquer importação de empresa.

### high — campaign_bounce_rate
- Evidência: Taxa de bounce do lote: 18/30 (60.0%).
- Recomendação: pausar escala de novos lotes até higienizar base; preservar apenas follow-up manual de contatos válidos.

### info — campaign_noise_filtered
- Evidência: 3 item(ns) de inbox foram ignorados por não terem vínculo com lote/campanha.
- Recomendação: manter filtro por assunto/destinatário para reduzir falso positivo.

## Guardrails

- Não importar no HubSpot automaticamente.
- Não enviar email/follow-up automaticamente.
- Não enviar Telegram automaticamente.
- Não chamar Make/scenario run.
- Qualquer ação externa exige aprovação explícita do Alê.
