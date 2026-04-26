# Mensura Schedule Control — Supabase

Banco operacional para cronograma, controle semanal e análise preditiva de obras.

## Objetivo

Transformar cronogramas MS Project/Excel/Primavera em base histórica versionada para:

- comparar baseline x atual;
- medir avanço real e consumo de folga;
- registrar restrições, riscos e causas de atraso;
- gerar métricas EVM/Lean;
- criar feature store para análise preditiva;
- auditar forecasts e resultados observados.

## Princípio central

Nunca sobrescrever cronograma. Cada importação cria uma `schedule.schedule_versions` nova.

A identidade permanente da atividade fica em `schedule.activity_identities`; o estado da atividade em cada cronograma fica em `schedule.activity_versions`.

## Schemas

- `raw` — importação bruta e auditoria;
- `schedule` — obra, versões, atividades, rede lógica e baseline;
- `control` — progresso, restrições, riscos, lookahead e decisões;
- `analytics` — métricas, features, labels e forecasts.

## Migration inicial

`supabase/migrations/20260426144000_schedule_predictive_foundation.sql`

## Supabase cloud

Projeto cloud separado criado para não misturar cronogramas/obras com o projeto pessoal Trade:

- Nome: `mensura-schedule-control`
- Ref: `ckmuyvbacgdidmiccvif`
- Região: `sa-east-1`
- Dashboard: `https://supabase.com/dashboard/project/ckmuyvbacgdidmiccvif`

Credenciais ficam somente em arquivo local ignorado pelo Git:

`/root/.openclaw/workspace/memory/context/mensura_schedule_supabase.env`

## CLI interna

Entry point:

```bash
./bin/mensura-schedule --help
```

Comandos principais:

```bash
./bin/mensura-schedule validate
./bin/mensura-schedule lint
./bin/mensura-schedule migration-list
./bin/mensura-schedule db-counts
./bin/mensura-schedule critical-summary --limit 20
./bin/mensura-schedule quality-report
./bin/mensura-schedule data-readiness
./bin/mensura-schedule project-classify
./bin/mensura-schedule risk-report
./bin/mensura-schedule baseline-discovery --only-candidates
./bin/mensura-schedule baseline-compare
./bin/mensura-schedule weekly-metrics-preview
./bin/mensura-schedule populate-weekly-metrics --execute
./bin/mensura-schedule audit-orphans
./bin/mensura-schedule search-sharepoint --contains "Arquivos Auxiliares"
./bin/mensura-schedule download-sharepoint
./bin/mensura-schedule inspect-workbooks --print-schedule
./bin/mensura-schedule ingest-sharepoint --dry-run
./bin/mensura-schedule ingest-sharepoint
```

Regra: CLI deve retornar texto estruturado ou JSON (`--json` onde disponível) para uso por agentes/cron.

## Documento de arquitetura

`/root/.openclaw/workspace/docs/cronogramas/SUPABASE-CRONOGRAMA-PREDITIVO-v0.1.md`
