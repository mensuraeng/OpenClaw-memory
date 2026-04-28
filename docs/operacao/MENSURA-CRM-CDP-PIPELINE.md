# MENSURA — CRM/CDP Pipeline v1

_Atualizado: 2026-04-28_

## Objetivo

Transformar a base comercial versionada da MENSURA em pipeline operacional rastreável, com fonte, janela, método, confiança e risco de erro explícitos.

## Fonte de verdade v1

- SQLite comercial: `projects/mensura-commercial-intelligence/data/commercial-intelligence.sqlite`
- Exports históricos: `projects/mensura-commercial-intelligence/exports/`
- Runtime pipeline: `runtime/data-pipeline/`

## Camadas

| Camada | Path | Função |
|---|---|---|
| staging | `runtime/data-pipeline/staging/` | entradas brutas ainda não verificadas |
| enriched | `runtime/data-pipeline/enriched/` | dados enriquecidos, ainda não necessariamente aprovados |
| verified | `runtime/data-pipeline/verified/` | contatos/empresas aptos a decisão operacional |
| rejected | `runtime/data-pipeline/rejected/` | descartados, bounces, descadastro, baixa confiança |
| crm | `runtime/data-pipeline/crm/` | candidatos prontos para CRM/importação/dry-run |
| outreach | `runtime/data-pipeline/outreach/` | listas aprovadas para campanha, nunca disparo automático sem regra explícita |
| archive | `runtime/data-pipeline/archive/` | snapshots antigos |

## Script v1

```bash
python3 scripts/mensura_crm_pipeline.py --json
python3 scripts/mensura_crm_pipeline.py --write --json
```

O script é read-only em sistemas externos. Ele não escreve em HubSpot, Phantombuster, LinkedIn ou e-mail.

## Artefatos gerados

- `runtime/data-pipeline/verified/mensura-verified-contacts-latest.jsonl`
- `runtime/data-pipeline/crm/mensura-crm-import-candidates-latest.jsonl`
- `runtime/data-pipeline/crm/mensura-crm-import-candidates-latest.csv`
- `runtime/data-pipeline/crm/mensura-crm-pipeline-latest.json`

## Critério de verificação v1

Um contato entra em `verified/crm` quando:

1. tem e-mail;
2. é corporativo;
3. não está em suppression list;
4. tem status de validade positivo ou grade A/B;
5. mantém rastreabilidade com base local.

## Saída executiva obrigatória

Todo relatório derivado deve declarar:

- fonte;
- método;
- janela/data de geração;
- confiança;
- risco de erro;
- contagem de rejeitados/suppressions quando relevante.

## HubSpot

HubSpot é destino operacional, não verdade única. Escrita no HubSpot exige comando explícito/dry-run aprovado. A pipeline v1 só prepara candidatos.

## Reconciliação HubSpot read-only

```bash
python3 scripts/mensura_hubspot_reconcile.py --write --json
```

Artefato:

- `runtime/data-pipeline/crm/mensura-hubspot-reconciliation-latest.json`

Primeira leitura validada em 2026-04-28:

- Local: 1242 contatos com e-mail; 795 e-mails válidos/não suprimidos; 477 domínios de empresas.
- HubSpot: 967 contatos com e-mail; 366 empresas com domínio; 2 deals.
- Gaps: 25 e-mails locais válidos ausentes no HubSpot; 111 domínios locais ausentes no HubSpot; 0 e-mails/domínios no HubSpot ausentes da base local.

## Próximos upgrades

1. Ledger por lead: origem → validação → campanha → resposta → deal.
2. Score ICP normalizado por segmento/obra/cargo.
3. Geração automática de lote `outreach/` com aprovação humana antes de disparo.
4. Rotina de diff recorrente local ↔ HubSpot com alerta somente para divergência material.
