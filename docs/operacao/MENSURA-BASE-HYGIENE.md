# MENSURA — Higienização de base comercial

Atualizado em 2026-04-30.

## Objetivo

Transformar a base comercial local em uma fila segura para campanha fria, preservando reputação de domínio e mantendo rastreabilidade CRM.

## Guardrails

- Não importa contatos no HubSpot.
- Não dispara email.
- Não chama Make.
- Não envia Telegram.
- Não altera CRM externo.
- Todo resultado é arquivo interno para revisão.

## Scripts

Gerar artefatos CSV/JSON:

```bash
python3 scripts/mensura_base_hygiene.py --write --json
```

Persistir a camada derivada no SQLite local:

```bash
python3 scripts/mensura_persist_hygiene_db.py --write --json
```

Entrada principal:

- `runtime/data-pipeline/crm/mensura-crm-import-candidates-latest.csv`
- `runtime/data-pipeline/crm/lead-intelligence/mensura-campaign-classification-latest.csv`
- `projects/mensura-commercial-intelligence/data/commercial-intelligence.sqlite` — suppression list local
- `runtime/data-pipeline/crm/mensura-hubspot-reconciliation-latest.json`

Saída principal:

- `runtime/mensura-marketing/higienizacao-current/summary-latest.json`
- `runtime/mensura-marketing/higienizacao-current/base-higienizada-latest.csv`
- `runtime/mensura-marketing/higienizacao-current/tier-a-pronto-revisao-latest.csv`
- `runtime/mensura-marketing/higienizacao-current/tier-a-1por-dominio-latest.csv`
- `runtime/mensura-marketing/higienizacao-current/proximo-lote-sugerido-30-latest.csv`
- `runtime/mensura-marketing/higienizacao-current/tier-b-enriquecer-latest.csv`
- `runtime/mensura-marketing/higienizacao-current/rejeitados-suppression-hold-latest.csv`
- `runtime/mensura-marketing/higienizacao-current/alerta-higienizacao-latest.md`

## Critérios de higiene

Bloqueia ou segura:

- email inválido;
- suppression por email ou domínio;
- contatos já usados no lote 01;
- bounce do lote 01;
- domínio sem DNS/MX/A;
- domínio pessoal ou institucional não empresarial;
- segmento fora do ICP;
- email genérico/role-based;
- ausência de empresa, nome ou cargo, conforme severidade.

Prioriza:

- segmento ICP: construtora, incorporadora, real estate, engenharia, empreendimento, urbanismo;
- cargo decisor ou influenciador: diretoria, gerência, engenharia, obras, planejamento, sócio, head, C-level;
- contato nomeado com cargo;
- domínio resolvendo;
- score local alto.

## Resultado da rodada 2026-04-30

- Entrada: 767 candidatos locais.
- Tier A pronto para revisão: 76.
- Tier A 1 por domínio: 47.
- Próximo lote sugerido: 30.
- Tier B para enriquecimento: 12.
- Rejeitar/hold: 168.
- Baixa prioridade: 511.
- Validação: 30 contatos no próximo lote, 30 domínios únicos, zero overlap com lote 01, zero motivos de rejeição nos 30 sugeridos.

## Persistência no banco local

Banco:

- `projects/mensura-commercial-intelligence/data/commercial-intelligence.sqlite`

Backup antes da escrita:

- `runtime/backups/mensura-commercial-intelligence-db/20260430T080306Z/commercial-intelligence.sqlite`
- `runtime/backups/mensura-commercial-intelligence-db/20260430T080306Z/manifest.json`

Tabelas/views criadas:

- `lead_hygiene_runs`
- `lead_hygiene_results`
- `lead_hygiene_current`
- `lead_hygiene_next_lot_current`

Validação no banco:

- `lead_hygiene_runs`: 1
- `lead_hygiene_results` na rodada atual: 767
- `lead_hygiene_next_lot_current`: 30
- domínios únicos no próximo lote: 30
- `pragma integrity_check`: ok

## Recomendação operacional

Não escalar volume ainda. Usar no máximo 30 contatos Tier A, um por domínio, com revisão humana antes de qualquer disparo. Em paralelo, enriquecer Tier B e revisar copy/cadência para reduzir risco de bounce e preservar reputação do remetente.
