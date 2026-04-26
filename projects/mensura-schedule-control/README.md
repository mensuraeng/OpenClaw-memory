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

## Documento de arquitetura

`/root/.openclaw/workspace/docs/cronogramas/SUPABASE-CRONOGRAMA-PREDITIVO-v0.1.md`
