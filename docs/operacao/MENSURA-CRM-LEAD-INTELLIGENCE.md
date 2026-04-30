# MENSURA CRM/CDP + Lead Intelligence

_Atualizado em 2026-04-29_

## Objetivo

Implantar capacidade interna/read-only para comparar ledger local de leads com HubSpot/CRM, classificar respostas da campanha fria MENSURA e gerar recomendações comerciais internas sem executar nenhuma ação externa.

## Script principal

```bash
python3 scripts/mensura_crm_lead_intelligence.py
```

Saídas principais:

```text
runtime/data-pipeline/crm/lead-intelligence/mensura-lead-intelligence-latest.json
runtime/data-pipeline/crm/lead-intelligence/mensura-lead-intelligence-diff-latest.csv
runtime/data-pipeline/crm/lead-intelligence/mensura-campaign-classification-latest.csv
runtime/data-pipeline/crm/lead-intelligence/mensura-lead-intelligence-alert-latest.md
```

## Fontes usadas

- `runtime/data-pipeline/crm/lead-ledger/mensura-lead-ledger-latest.csv`
- `runtime/data-pipeline/crm/mensura-crm-import-candidates-latest.csv`
- `runtime/data-pipeline/crm/mensura-hubspot-reconciliation-latest.json`
- `runtime/data-pipeline/crm/mensura-crm-pipeline-latest.json`
- `runtime/mensura-marketing/campanha-20260427/`

## Guardrails

O fluxo é estritamente read-only:

- não importa no HubSpot;
- não cria/edita contato, empresa ou negócio;
- não envia email;
- não envia Telegram;
- não chama Make/scenario run;
- não altera CRM;
- qualquer ação externa exige aprovação explícita do Alê.

## Classificação de campanha

Categorias operacionais usadas:

- `interesse positivo`
- `neutro`
- `sem timing`
- `descadastro/não interesse`
- `bounce`
- `sem resposta`

O script filtra ruído de inbox: uma mensagem só entra na campanha se houver vínculo com o assunto da campanha ou destinatário do lote.

## Validação 2026-04-30T01:46Z

Com dados atuais, o fluxo gerou evidência validada:

- ledger local: 767 linhas;
- candidatos CRM: 767 linhas;
- contatos locais com email: 1242;
- contatos locais válidos não suprimidos: 795;
- contatos HubSpot com email: 967;
- empresas HubSpot com domínio: 366;
- negócios HubSpot: 2;
- gaps HubSpot:
  - 25 emails locais válidos ausentes no HubSpot;
  - 111 domínios locais ausentes no HubSpot;
  - 0 emails HubSpot ausentes no local;
  - 0 domínios HubSpot ausentes no local;
- campanha lote 01:
  - enviados: 30;
  - bounces: 18;
  - sem resposta: 12;
  - ruídos filtrados: 3.

Alertas internos gerados:

1. `attention/crm_diff` — 25 emails locais válidos ausentes no HubSpot.
2. `attention/crm_domain_diff` — 111 domínios locais ausentes no HubSpot.
3. `high/campaign_bounce_rate` — taxa de bounce 18/30 = 60%.
4. `info/campaign_noise_filtered` — 3 itens ignorados por falta de vínculo com a campanha.

## Recomendação operacional

Não escalar novos lotes da campanha fria antes de higienizar a base. A taxa de bounce de 60% é alta e aumenta risco reputacional/entregabilidade.

Próximo passo seguro: usar `mensura-campaign-classification-latest.csv` para separar:

- contatos com bounce → supressão/revisão;
- contatos sem resposta → possível follow-up manual aprovado;
- gaps HubSpot → fila de revisão para import controlado, se aprovado.
