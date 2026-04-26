# Supabase — Arquitetura de Cronograma Preditivo v0.1

_Atualizado em 2026-04-26_

## 1. Tese

Para chegar em análise preditiva de prazo, o banco não pode ser só uma tabela de atividades.

A arquitetura correta precisa preservar:

1. **versões do cronograma** — cada importação é um snapshot imutável;
2. **baseline aprovada** — separada do cronograma atualizado;
3. **realizado por data-base** — avanço, datas reais e status semana a semana;
4. **lógica de rede** — predecessoras, sucessoras, folga, caminho crítico;
5. **restrições e causas** — o que travou, por quem, por quanto tempo;
6. **métricas de controle** — SPI, BEI, PPC, IRR, IAO, consumo de folga;
7. **features históricas** — base para modelos probabilísticos;
8. **previsões auditáveis** — modelo, versão, features, previsão, resultado observado.

Sem isso, qualquer IA vira opinião em cima de planilha. Com isso, o sistema aprende padrões reais de atraso.

---

## 2. Princípio de arquitetura

### Regra principal

**Nunca sobrescrever histórico.**

Cada novo cronograma importado do MS Project / Excel / Primavera deve criar uma nova `schedule_version`.
As atividades dessa versão entram como linhas novas em `activity_versions`.
O vínculo entre versões é feito por um identificador estável (`activity_identity`).

Isso permite responder:

- o que mudou desde a semana passada?
- qual atividade escorregou?
- quem consome mais folga?
- que tipo de frente atrasa mais?
- qual padrão antecede atraso crítico?
- qual a probabilidade de terminar fora do prazo?

---

## 3. Schemas recomendados

No Supabase/Postgres, usar schemas separados:

| Schema | Função |
|---|---|
| `schedule` | cronogramas, versões, atividades, baseline, dependências |
| `control` | progresso real, restrições, riscos, lookahead, reuniões, decisões |
| `analytics` | métricas, feature store, labels, modelos, previsões |
| `raw` | metadados de importação, arquivos brutos, payloads JSON |

Se quiser simplificar no MVP, começar com `schedule` e `analytics`, mas já deixar nomes compatíveis com a expansão.

---

## 4. Camadas do banco

### Camada 0 — Raw / auditoria de importação

Objetivo: guardar origem e rastreabilidade.

Tabelas:

- `raw.import_jobs`
- `raw.import_files`
- `raw.source_rows`

Campos-chave:

- obra;
- origem: MS Project, Excel, Primavera, CSV, manual;
- hash do arquivo;
- data de importação;
- usuário/agente que importou;
- status: `received`, `parsed`, `validated`, `failed`;
- erros de validação;
- payload bruto por linha em `jsonb`.

Regra: arquivo original fica no Supabase Storage ou filesystem; Postgres guarda metadado, hash e parsed rows.

---

### Camada 1 — Cadastro estrutural

Tabelas:

- `schedule.projects`
- `schedule.contracts`
- `schedule.project_calendars`
- `schedule.wbs_nodes`
- `schedule.locations`
- `schedule.disciplines`
- `schedule.responsible_parties`

Objetivo: dar contexto estável para cada obra.

Campos mínimos de `projects`:

- `id`
- `code`
- `name`
- `company` — Mensura/MIA/PCS/cliente quando aplicável
- `client_name`
- `contract_start_date`
- `contract_finish_date`
- `contract_duration_days`
- `status`
- `created_at`

---

### Camada 2 — Versões do cronograma

Tabelas:

- `schedule.schedule_versions`
- `schedule.activity_identities`
- `schedule.activity_versions`
- `schedule.activity_dependencies`
- `schedule.baselines`
- `schedule.baseline_activity_values`

#### `schedule_versions`

Uma linha por cronograma importado.

Campos essenciais:

- `id`
- `project_id`
- `import_job_id`
- `version_label` — ex: `2026-W18`, `R03`, `baseline original`
- `data_date` — data-base/status date do cronograma
- `source_tool` — ms_project/excel/primavera/manual
- `is_baseline_candidate`
- `created_at`

#### `activity_identities`

Identidade estável da atividade ao longo do tempo.

Campos essenciais:

- `id`
- `project_id`
- `source_activity_uid` — ID original quando existir
- `activity_code`
- `normalized_name`
- `wbs_code`
- `identity_confidence` — alto/médio/baixo

Regra: se o ID muda entre versões, criar mecanismo de reconciliação manual. Para predição, identidade ruim destrói histórico.

#### `activity_versions`

Estado da atividade em cada versão do cronograma.

Campos essenciais:

- `id`
- `schedule_version_id`
- `activity_identity_id`
- `wbs_node_id`
- `activity_name`
- `activity_type`
- `discipline`
- `location`
- `responsible_party_id`
- `planned_duration_days`
- `remaining_duration_days`
- `baseline_start`
- `baseline_finish`
- `current_start`
- `current_finish`
- `actual_start`
- `actual_finish`
- `percent_complete`
- `physical_percent_complete`
- `is_critical`
- `total_float_days`
- `free_float_days`
- `constraint_type`
- `calendar_id`
- `status`
- `raw_payload jsonb`

#### `activity_dependencies`

Rede lógica.

Campos essenciais:

- `schedule_version_id`
- `predecessor_activity_version_id`
- `successor_activity_version_id`
- `relationship_type` — FS/SS/FF/SF
- `lag_days`

#### `baselines`

Baseline aprovada, não apenas versão qualquer.

Campos essenciais:

- `id`
- `project_id`
- `schedule_version_id`
- `baseline_type` — original/revised/recovery
- `approved_at`
- `approved_by`
- `approval_reference`
- `is_active`

---

### Camada 3 — Controle real semanal

Tabelas:

- `control.progress_updates`
- `control.activity_progress_snapshots`
- `control.weekly_plans`
- `control.weekly_plan_items`
- `control.constraints`
- `control.risks`
- `control.issues`
- `control.meetings`
- `control.decisions`
- `control.weather_daily`
- `control.procurement_items`
- `control.rfis`

Essa camada é onde nasce a predição real, porque cronograma sozinho mostra consequência; restrição/risco/reunião mostra causa.

#### `progress_updates`

Uma atualização por obra/data-base.

Campos:

- `project_id`
- `schedule_version_id`
- `data_date`
- `reported_by`
- `overall_physical_percent`
- `notes`
- `confidence_level`

#### `activity_progress_snapshots`

Estado real de cada atividade na data-base.

Campos:

- `progress_update_id`
- `activity_identity_id`
- `activity_version_id`
- `status`
- `percent_complete`
- `actual_start`
- `actual_finish`
- `remaining_duration_days`
- `blocker_count`
- `root_cause_category`
- `field_notes`

#### `weekly_plans` e `weekly_plan_items`

Compromisso Lean. Não deve ser gerado automaticamente pelo baseline.

Campos de plano:

- `project_id`
- `week_start`
- `week_end`
- `iso_week`
- `planned_by`
- `approved_by`

Campos dos itens:

- `weekly_plan_id`
- `activity_identity_id`
- `commitment_type` — start/finish/progress/milestone
- `committed_quantity` / `committed_percent`
- `completed`
- `completed_at`
- `non_completion_reason`

#### `constraints`

Banco crítico para predição.

Campos:

- `project_id`
- `activity_identity_id`
- `constraint_type` — projeto, cliente, suprimentos, mão de obra, frente, clima, segurança, contrato, órgão público
- `description`
- `owner_type`
- `owner_name`
- `opened_at`
- `due_date`
- `removed_at`
- `status`
- `days_open` — calculado por view
- `impact_days_estimate`
- `confidence_level`

---

### Camada 4 — Métricas e Feature Store

Tabelas:

- `analytics.project_weekly_metrics`
- `analytics.activity_weekly_features`
- `analytics.project_weekly_features`
- `analytics.prediction_labels`
- `analytics.model_registry`
- `analytics.model_runs`
- `analytics.forecasts`
- `analytics.forecast_items`
- `analytics.forecast_outcomes`

#### `project_weekly_metrics`

KPIs humanos e executivos.

Campos:

- `project_id`
- `week_start`
- `data_date`
- `spi`
- `bei`
- `ppc`
- `irr`
- `iao`
- `planned_percent`
- `actual_percent`
- `critical_activities_delayed_count`
- `negative_float_activities_count`
- `overdue_constraints_count`
- `open_risks_score_sum`
- `forecast_finish_date_current`
- `delay_days_vs_contract`

#### `activity_weekly_features`

Uma linha por atividade por semana. Essa é a base de ML.

Exemplos de features:

- `planned_duration_days`
- `remaining_duration_days`
- `percent_complete`
- `percent_complete_delta_7d`
- `start_variance_days`
- `finish_variance_days`
- `float_days`
- `float_consumed_7d`
- `is_critical`
- `predecessor_count`
- `unfinished_predecessor_count`
- `successor_count`
- `constraint_open_count`
- `constraint_overdue_count`
- `risk_score_open`
- `rfi_open_count`
- `procurement_delay_flag`
- `weather_rain_days_7d`
- `responsible_party_id`
- `discipline`
- `location`

#### `project_weekly_features`

Uma linha por obra por semana.

Exemplos:

- `elapsed_contract_percent`
- `actual_physical_percent`
- `planned_physical_percent`
- `progress_velocity_4w`
- `spi_trend_4w`
- `bei_trend_4w`
- `ppc_trend_4w`
- `irr_trend_4w`
- `critical_path_delay_days`
- `float_buffer_total_days`
- `float_buffer_consumed_percent`
- `compression_ratio_future`
- `overdue_constraints_count`
- `client_decision_pending_count`
- `project_rfi_aging_avg_days`
- `weather_lost_days_30d`

#### `prediction_labels`

Labels observados para treinar/avaliar.

Exemplos:

- `activity_finished_late` boolean
- `activity_finish_delay_days`
- `project_finished_late` boolean
- `project_finish_delay_days`
- `milestone_missed` boolean
- `milestone_delay_days`

Regra: label só pode ser preenchido quando o resultado real aconteceu. Sem isso, não há treino honesto.

---

## 5. Previsões que o sistema deve suportar

### Nível atividade

- Probabilidade de a atividade terminar atrasada.
- Dias esperados de atraso.
- Probabilidade de virar crítica nos próximos 15/30 dias.
- Impacto provável em sucessoras.

### Nível frente/WBS

- Frente com maior risco de escorregamento.
- Disciplina com maior consumo de folga.
- Responsável com restrições vencendo/atrasadas.

### Nível obra

- Probabilidade de terminar depois do prazo contratual.
- Data de término provável / otimista / pessimista.
- Dias de atraso esperados.
- Top 5 causas prováveis de atraso.
- Ações com maior potencial de recuperação.

### Nível portfólio

- Obras com maior risco de intervenção do diretor.
- Engenheiro/gestor com maior carga de restrições críticas.
- Padrões recorrentes por cliente, tipologia, disciplina, fornecedor.

---

## 6. Views/materialized views recomendadas

| View | Função |
|---|---|
| `schedule.v_latest_activity_status` | última versão de cada atividade por obra |
| `schedule.v_baseline_vs_current` | comparação baseline x cronograma atual |
| `control.v_open_constraints` | restrições abertas e vencidas |
| `analytics.v_project_health_current` | semáforo atual por obra |
| `analytics.v_activity_delay_training_set` | dataset tabular para previsão de atraso por atividade |
| `analytics.v_project_delay_training_set` | dataset tabular para previsão de atraso da obra |
| `analytics.mv_weekly_project_features` | feature store semanal materializada |

Materialized views devem ser usadas para datasets pesados. Atualizar após importação semanal.

---

## 7. Índices mínimos

```sql
create index on schedule.schedule_versions (project_id, data_date desc);
create index on schedule.activity_versions (schedule_version_id, activity_identity_id);
create index on schedule.activity_identities (project_id, source_activity_uid);
create index on schedule.activity_dependencies (schedule_version_id, predecessor_activity_version_id);
create index on schedule.activity_dependencies (schedule_version_id, successor_activity_version_id);

create index on control.progress_updates (project_id, data_date desc);
create index on control.activity_progress_snapshots (progress_update_id, activity_identity_id);
create index on control.constraints (project_id, status, due_date);
create index on control.risks (project_id, status);

create index on analytics.activity_weekly_features (project_id, week_start, activity_identity_id);
create index on analytics.project_weekly_features (project_id, week_start);
create index on analytics.forecasts (project_id, forecast_date desc, forecast_type);
```

---

## 8. Segurança / Supabase

- Ativar RLS em tabelas expostas para app/web.
- Serviço interno pode usar service role, mas segredo nunca deve ir para Git ou 2nd-brain.
- Criar policies por empresa/projeto se houver acesso externo de cliente.
- Para MVP interno, preferir schema privado + acesso via scripts/service role.
- Arquivos brutos de cronograma devem ficar em bucket privado.

---

## 9. MVP recomendado

### Fase 1 — Banco mínimo preditivo

Criar:

1. `schedule.projects`
2. `raw.import_jobs`
3. `schedule.schedule_versions`
4. `schedule.activity_identities`
5. `schedule.activity_versions`
6. `schedule.activity_dependencies`
7. `schedule.baselines`
8. `control.progress_updates`
9. `control.activity_progress_snapshots`
10. `control.constraints`
11. `analytics.project_weekly_metrics`
12. `analytics.activity_weekly_features`
13. `analytics.project_weekly_features`
14. `analytics.forecasts`

### Fase 2 — Lean/torre de controle

Adicionar:

- weekly plans;
- PPC;
- IRR;
- IAO;
- reuniões;
- decisões;
- riscos;
- RFIs;
- procurement.

### Fase 3 — modelos preditivos

Começar simples:

1. regras estatísticas e base rates;
2. regressão/logística calibrada;
3. modelos de árvore/gradient boosting quando houver volume;
4. Monte Carlo por duração e risco;
5. NLP de atas/restrições só depois de dado estruturado consistente.

---

## 10. SQL skeleton inicial

```sql
create schema if not exists raw;
create schema if not exists schedule;
create schema if not exists control;
create schema if not exists analytics;

create table schedule.projects (
  id uuid primary key default gen_random_uuid(),
  code text not null unique,
  name text not null,
  company text,
  client_name text,
  contract_start_date date,
  contract_finish_date date,
  contract_duration_days integer,
  status text not null default 'active',
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table raw.import_jobs (
  id uuid primary key default gen_random_uuid(),
  project_id uuid not null references schedule.projects(id) on delete cascade,
  source_tool text not null,
  source_filename text,
  file_hash text,
  imported_by text,
  imported_at timestamptz not null default now(),
  status text not null default 'received',
  validation_errors jsonb not null default '[]'::jsonb,
  raw_metadata jsonb not null default '{}'::jsonb
);

create table schedule.schedule_versions (
  id uuid primary key default gen_random_uuid(),
  project_id uuid not null references schedule.projects(id) on delete cascade,
  import_job_id uuid references raw.import_jobs(id) on delete set null,
  version_label text not null,
  data_date date not null,
  source_tool text not null,
  is_baseline_candidate boolean not null default false,
  created_at timestamptz not null default now(),
  unique(project_id, version_label),
  unique(project_id, data_date, source_tool, version_label)
);

create table schedule.activity_identities (
  id uuid primary key default gen_random_uuid(),
  project_id uuid not null references schedule.projects(id) on delete cascade,
  source_activity_uid text,
  activity_code text,
  normalized_name text not null,
  wbs_code text,
  identity_confidence text not null default 'medium',
  created_at timestamptz not null default now(),
  unique(project_id, source_activity_uid)
);

create table schedule.activity_versions (
  id uuid primary key default gen_random_uuid(),
  schedule_version_id uuid not null references schedule.schedule_versions(id) on delete cascade,
  activity_identity_id uuid not null references schedule.activity_identities(id) on delete cascade,
  activity_name text not null,
  wbs_code text,
  discipline text,
  location text,
  responsible_party text,
  planned_duration_days numeric,
  remaining_duration_days numeric,
  baseline_start date,
  baseline_finish date,
  current_start date,
  current_finish date,
  actual_start date,
  actual_finish date,
  percent_complete numeric check (percent_complete is null or (percent_complete >= 0 and percent_complete <= 100)),
  physical_percent_complete numeric check (physical_percent_complete is null or (physical_percent_complete >= 0 and physical_percent_complete <= 100)),
  is_critical boolean,
  total_float_days numeric,
  free_float_days numeric,
  status text,
  raw_payload jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now(),
  unique(schedule_version_id, activity_identity_id)
);

create table schedule.activity_dependencies (
  id uuid primary key default gen_random_uuid(),
  schedule_version_id uuid not null references schedule.schedule_versions(id) on delete cascade,
  predecessor_activity_version_id uuid not null references schedule.activity_versions(id) on delete cascade,
  successor_activity_version_id uuid not null references schedule.activity_versions(id) on delete cascade,
  relationship_type text not null default 'FS',
  lag_days numeric not null default 0,
  check (predecessor_activity_version_id <> successor_activity_version_id)
);

create table schedule.baselines (
  id uuid primary key default gen_random_uuid(),
  project_id uuid not null references schedule.projects(id) on delete cascade,
  schedule_version_id uuid not null references schedule.schedule_versions(id) on delete restrict,
  baseline_type text not null default 'original',
  approved_at timestamptz,
  approved_by text,
  approval_reference text,
  is_active boolean not null default true,
  created_at timestamptz not null default now()
);

create table control.progress_updates (
  id uuid primary key default gen_random_uuid(),
  project_id uuid not null references schedule.projects(id) on delete cascade,
  schedule_version_id uuid references schedule.schedule_versions(id) on delete set null,
  data_date date not null,
  reported_by text,
  overall_physical_percent numeric check (overall_physical_percent is null or (overall_physical_percent >= 0 and overall_physical_percent <= 100)),
  confidence_level text not null default 'medium',
  notes text,
  created_at timestamptz not null default now(),
  unique(project_id, data_date)
);

create table control.activity_progress_snapshots (
  id uuid primary key default gen_random_uuid(),
  progress_update_id uuid not null references control.progress_updates(id) on delete cascade,
  activity_identity_id uuid not null references schedule.activity_identities(id) on delete cascade,
  activity_version_id uuid references schedule.activity_versions(id) on delete set null,
  status text,
  percent_complete numeric check (percent_complete is null or (percent_complete >= 0 and percent_complete <= 100)),
  actual_start date,
  actual_finish date,
  remaining_duration_days numeric,
  blocker_count integer not null default 0,
  root_cause_category text,
  field_notes text,
  unique(progress_update_id, activity_identity_id)
);

create table control.constraints (
  id uuid primary key default gen_random_uuid(),
  project_id uuid not null references schedule.projects(id) on delete cascade,
  activity_identity_id uuid references schedule.activity_identities(id) on delete set null,
  constraint_type text not null,
  description text not null,
  owner_type text,
  owner_name text,
  opened_at date not null default current_date,
  due_date date,
  removed_at date,
  status text not null default 'open',
  impact_days_estimate numeric,
  confidence_level text not null default 'medium',
  created_at timestamptz not null default now()
);

create table analytics.project_weekly_metrics (
  id uuid primary key default gen_random_uuid(),
  project_id uuid not null references schedule.projects(id) on delete cascade,
  week_start date not null,
  data_date date not null,
  spi numeric,
  bei numeric,
  ppc numeric,
  irr numeric,
  iao numeric,
  planned_percent numeric,
  actual_percent numeric,
  critical_activities_delayed_count integer,
  negative_float_activities_count integer,
  overdue_constraints_count integer,
  open_risks_score_sum numeric,
  forecast_finish_date_current date,
  delay_days_vs_contract numeric,
  created_at timestamptz not null default now(),
  unique(project_id, week_start)
);

create table analytics.activity_weekly_features (
  id uuid primary key default gen_random_uuid(),
  project_id uuid not null references schedule.projects(id) on delete cascade,
  activity_identity_id uuid not null references schedule.activity_identities(id) on delete cascade,
  week_start date not null,
  feature_set_version text not null default 'v0.1',
  features jsonb not null,
  label jsonb,
  created_at timestamptz not null default now(),
  unique(project_id, activity_identity_id, week_start, feature_set_version)
);

create table analytics.project_weekly_features (
  id uuid primary key default gen_random_uuid(),
  project_id uuid not null references schedule.projects(id) on delete cascade,
  week_start date not null,
  feature_set_version text not null default 'v0.1',
  features jsonb not null,
  label jsonb,
  created_at timestamptz not null default now(),
  unique(project_id, week_start, feature_set_version)
);

create table analytics.forecasts (
  id uuid primary key default gen_random_uuid(),
  project_id uuid not null references schedule.projects(id) on delete cascade,
  forecast_date date not null,
  forecast_type text not null,
  model_name text not null,
  model_version text not null,
  horizon_days integer,
  predicted_finish_date date,
  p_finish_after_contract numeric,
  expected_delay_days numeric,
  p50_delay_days numeric,
  p80_delay_days numeric,
  p95_delay_days numeric,
  drivers jsonb not null default '[]'::jsonb,
  input_feature_snapshot jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now()
);
```

---

## 11. Decisão recomendada

Implementar primeiro o **MVP de banco preditivo**, não o MENSURA OS completo.

Motivo: para predição, o gargalo é histórico versionado e feature store. PPC/IRR/IAO são importantes, mas entram melhor na Fase 2 depois que a ingestão de cronograma estiver limpa.

Ordem certa:

1. importar cronograma versionado;
2. reconciliar identidade das atividades;
3. comparar baseline x atual;
4. registrar progresso semanal;
5. registrar restrições/causas;
6. gerar métricas e features;
7. só então rodar previsão.

