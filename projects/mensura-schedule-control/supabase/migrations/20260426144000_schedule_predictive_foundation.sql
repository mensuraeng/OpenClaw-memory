-- migration: schedule_predictive_foundation
-- purpose: foundation schema for construction schedule control and predictive analytics
-- created_at: 2026-04-26
-- owner: Mensura Engenharia / Flávia
-- notes:
--   This migration creates a versioned schedule model. Do not overwrite historical schedules.
--   Every import creates a schedule.schedule_versions row and a new set of schedule.activity_versions.

create extension if not exists pgcrypto;

create schema if not exists raw;
create schema if not exists schedule;
create schema if not exists control;
create schema if not exists analytics;

-- -----------------------------------------------------------------------------
-- Shared helpers
-- -----------------------------------------------------------------------------

create or replace function public.set_updated_at()
returns trigger
language plpgsql
as $$
begin
  new.updated_at = now();
  return new;
end;
$$;

-- -----------------------------------------------------------------------------
-- Schedule structural layer
-- -----------------------------------------------------------------------------

create table schedule.projects (
  id uuid primary key default gen_random_uuid(),
  code text not null unique,
  name text not null,
  company text,
  client_name text,
  contract_name text,
  contract_reference text,
  contract_start_date date,
  contract_finish_date date,
  contract_duration_days integer generated always as (
    case
      when contract_start_date is not null and contract_finish_date is not null
      then (contract_finish_date - contract_start_date + 1)
      else null
    end
  ) stored,
  status text not null default 'active' check (status in ('planned', 'active', 'paused', 'completed', 'cancelled', 'archived')),
  timezone text not null default 'America/Sao_Paulo',
  metadata jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create trigger trg_projects_updated_at
before update on schedule.projects
for each row execute function public.set_updated_at();

create table schedule.project_calendars (
  id uuid primary key default gen_random_uuid(),
  project_id uuid not null references schedule.projects(id) on delete cascade,
  name text not null,
  calendar_type text not null default 'standard',
  workweek jsonb not null default '{}'::jsonb,
  holidays jsonb not null default '[]'::jsonb,
  is_default boolean not null default false,
  created_at timestamptz not null default now(),
  unique(project_id, name)
);

create table schedule.wbs_nodes (
  id uuid primary key default gen_random_uuid(),
  project_id uuid not null references schedule.projects(id) on delete cascade,
  parent_id uuid references schedule.wbs_nodes(id) on delete cascade,
  wbs_code text not null,
  name text not null,
  level integer,
  sort_order integer,
  created_at timestamptz not null default now(),
  unique(project_id, wbs_code)
);

create table schedule.responsible_parties (
  id uuid primary key default gen_random_uuid(),
  project_id uuid references schedule.projects(id) on delete cascade,
  party_type text not null default 'obra' check (party_type in ('obra', 'cliente', 'projetista', 'fornecedor', 'terceiro', 'orgao_publico', 'diretoria', 'outro')),
  name text not null,
  organization text,
  email text,
  phone text,
  metadata jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now(),
  unique(project_id, party_type, name)
);

-- -----------------------------------------------------------------------------
-- Raw import/audit layer
-- -----------------------------------------------------------------------------

create table raw.import_jobs (
  id uuid primary key default gen_random_uuid(),
  project_id uuid not null references schedule.projects(id) on delete cascade,
  source_tool text not null check (source_tool in ('ms_project', 'ms_project_excel', 'primavera', 'excel', 'csv', 'manual', 'other')),
  source_filename text,
  source_uri text,
  file_hash text,
  imported_by text,
  imported_at timestamptz not null default now(),
  status text not null default 'received' check (status in ('received', 'parsed', 'validated', 'failed', 'archived')),
  data_date date,
  validation_errors jsonb not null default '[]'::jsonb,
  raw_metadata jsonb not null default '{}'::jsonb
);

create table raw.source_rows (
  id bigserial primary key,
  import_job_id uuid not null references raw.import_jobs(id) on delete cascade,
  source_row_number integer,
  source_activity_uid text,
  activity_code text,
  raw_payload jsonb not null,
  parse_errors jsonb not null default '[]'::jsonb,
  created_at timestamptz not null default now(),
  unique(import_job_id, source_row_number)
);

-- -----------------------------------------------------------------------------
-- Versioned schedule layer
-- -----------------------------------------------------------------------------

create table schedule.schedule_versions (
  id uuid primary key default gen_random_uuid(),
  project_id uuid not null references schedule.projects(id) on delete cascade,
  import_job_id uuid references raw.import_jobs(id) on delete set null,
  version_label text not null,
  data_date date not null,
  source_tool text not null,
  is_baseline_candidate boolean not null default false,
  schedule_quality_score numeric check (schedule_quality_score is null or (schedule_quality_score >= 0 and schedule_quality_score <= 100)),
  notes text,
  metadata jsonb not null default '{}'::jsonb,
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
  identity_confidence text not null default 'medium' check (identity_confidence in ('high', 'medium', 'low', 'manual_review')),
  first_seen_version_id uuid references schedule.schedule_versions(id) on delete set null,
  is_active boolean not null default true,
  created_at timestamptz not null default now(),
  unique(project_id, source_activity_uid),
  unique(project_id, activity_code, normalized_name)
);

create table schedule.activity_versions (
  id uuid primary key default gen_random_uuid(),
  schedule_version_id uuid not null references schedule.schedule_versions(id) on delete cascade,
  activity_identity_id uuid not null references schedule.activity_identities(id) on delete cascade,
  wbs_node_id uuid references schedule.wbs_nodes(id) on delete set null,
  calendar_id uuid references schedule.project_calendars(id) on delete set null,
  responsible_party_id uuid references schedule.responsible_parties(id) on delete set null,
  activity_code text,
  activity_name text not null,
  activity_type text,
  wbs_code text,
  discipline text,
  location text,
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
  constraint_type text,
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
  relationship_type text not null default 'FS' check (relationship_type in ('FS', 'SS', 'FF', 'SF')),
  lag_days numeric not null default 0,
  created_at timestamptz not null default now(),
  check (predecessor_activity_version_id <> successor_activity_version_id),
  unique(schedule_version_id, predecessor_activity_version_id, successor_activity_version_id, relationship_type, lag_days)
);

create table schedule.baselines (
  id uuid primary key default gen_random_uuid(),
  project_id uuid not null references schedule.projects(id) on delete cascade,
  schedule_version_id uuid not null references schedule.schedule_versions(id) on delete restrict,
  baseline_type text not null default 'original' check (baseline_type in ('original', 'revised', 'recovery', 'contractual', 'internal')),
  approved_at timestamptz,
  approved_by text,
  approval_reference text,
  is_active boolean not null default true,
  notes text,
  created_at timestamptz not null default now()
);

create unique index uq_active_baseline_per_type
on schedule.baselines(project_id, baseline_type)
where is_active;

-- -----------------------------------------------------------------------------
-- Control / weekly execution layer
-- -----------------------------------------------------------------------------

create table control.progress_updates (
  id uuid primary key default gen_random_uuid(),
  project_id uuid not null references schedule.projects(id) on delete cascade,
  schedule_version_id uuid references schedule.schedule_versions(id) on delete set null,
  data_date date not null,
  reported_by text,
  overall_physical_percent numeric check (overall_physical_percent is null or (overall_physical_percent >= 0 and overall_physical_percent <= 100)),
  confidence_level text not null default 'medium' check (confidence_level in ('high', 'medium', 'low')),
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
  created_at timestamptz not null default now(),
  unique(progress_update_id, activity_identity_id)
);

create table control.weekly_plans (
  id uuid primary key default gen_random_uuid(),
  project_id uuid not null references schedule.projects(id) on delete cascade,
  week_start date not null,
  week_end date not null,
  iso_year integer,
  iso_week integer,
  planned_by text,
  approved_by text,
  status text not null default 'draft' check (status in ('draft', 'committed', 'closed', 'cancelled')),
  notes text,
  created_at timestamptz not null default now(),
  unique(project_id, week_start)
);

create table control.weekly_plan_items (
  id uuid primary key default gen_random_uuid(),
  weekly_plan_id uuid not null references control.weekly_plans(id) on delete cascade,
  activity_identity_id uuid not null references schedule.activity_identities(id) on delete cascade,
  commitment_type text not null default 'finish' check (commitment_type in ('start', 'finish', 'progress', 'milestone')),
  committed_percent numeric check (committed_percent is null or (committed_percent >= 0 and committed_percent <= 100)),
  completed boolean,
  completed_at date,
  non_completion_reason text,
  notes text,
  created_at timestamptz not null default now(),
  unique(weekly_plan_id, activity_identity_id, commitment_type)
);

create table control.constraints (
  id uuid primary key default gen_random_uuid(),
  project_id uuid not null references schedule.projects(id) on delete cascade,
  activity_identity_id uuid references schedule.activity_identities(id) on delete set null,
  constraint_type text not null check (constraint_type in ('projeto', 'cliente', 'suprimentos', 'mao_de_obra', 'frente', 'clima', 'seguranca', 'contrato', 'orgao_publico', 'fornecedor', 'outro')),
  description text not null,
  owner_type text check (owner_type is null or owner_type in ('obra', 'cliente', 'projetista', 'fornecedor', 'terceiro', 'orgao_publico', 'diretoria', 'outro')),
  owner_name text,
  opened_at date not null default current_date,
  due_date date,
  removed_at date,
  status text not null default 'open' check (status in ('open', 'removed', 'cancelled', 'transferred')),
  impact_days_estimate numeric,
  confidence_level text not null default 'medium' check (confidence_level in ('high', 'medium', 'low')),
  metadata jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now()
);

create table control.risks (
  id uuid primary key default gen_random_uuid(),
  project_id uuid not null references schedule.projects(id) on delete cascade,
  activity_identity_id uuid references schedule.activity_identities(id) on delete set null,
  risk_category text not null,
  description text not null,
  probability_score integer check (probability_score between 1 and 5),
  impact_score integer check (impact_score between 1 and 5),
  severity_score integer generated always as (probability_score * impact_score) stored,
  owner_type text,
  owner_name text,
  status text not null default 'open' check (status in ('open', 'mitigated', 'accepted', 'closed', 'cancelled')),
  mitigation_plan text,
  due_date date,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create trigger trg_risks_updated_at
before update on control.risks
for each row execute function public.set_updated_at();

create table control.decisions (
  id uuid primary key default gen_random_uuid(),
  project_id uuid not null references schedule.projects(id) on delete cascade,
  activity_identity_id uuid references schedule.activity_identities(id) on delete set null,
  decision_type text not null,
  description text not null,
  owner_name text,
  due_date date,
  decided_at timestamptz,
  status text not null default 'pending' check (status in ('pending', 'decided', 'cancelled', 'escalated')),
  escalated_to_director boolean not null default false,
  created_at timestamptz not null default now()
);

-- -----------------------------------------------------------------------------
-- Analytics / predictive layer
-- -----------------------------------------------------------------------------

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
  metrics jsonb not null default '{}'::jsonb,
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

create table analytics.model_registry (
  id uuid primary key default gen_random_uuid(),
  model_name text not null,
  model_version text not null,
  prediction_target text not null,
  feature_set_version text not null,
  algorithm text,
  training_window jsonb not null default '{}'::jsonb,
  metrics jsonb not null default '{}'::jsonb,
  status text not null default 'experimental' check (status in ('experimental', 'validated', 'deprecated', 'archived')),
  created_at timestamptz not null default now(),
  unique(model_name, model_version)
);

create table analytics.forecasts (
  id uuid primary key default gen_random_uuid(),
  project_id uuid not null references schedule.projects(id) on delete cascade,
  model_id uuid references analytics.model_registry(id) on delete set null,
  forecast_date date not null,
  forecast_type text not null check (forecast_type in ('project_finish', 'milestone_delay', 'activity_delay', 'criticality_risk')),
  model_name text not null,
  model_version text not null,
  horizon_days integer,
  predicted_finish_date date,
  p_finish_after_contract numeric check (p_finish_after_contract is null or (p_finish_after_contract >= 0 and p_finish_after_contract <= 1)),
  expected_delay_days numeric,
  p50_delay_days numeric,
  p80_delay_days numeric,
  p95_delay_days numeric,
  drivers jsonb not null default '[]'::jsonb,
  input_feature_snapshot jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now()
);

create table analytics.forecast_outcomes (
  id uuid primary key default gen_random_uuid(),
  forecast_id uuid not null references analytics.forecasts(id) on delete cascade,
  observed_at date not null,
  observed_value jsonb not null,
  error_metrics jsonb not null default '{}'::jsonb,
  notes text,
  created_at timestamptz not null default now(),
  unique(forecast_id, observed_at)
);

-- -----------------------------------------------------------------------------
-- Views
-- -----------------------------------------------------------------------------

create view schedule.v_latest_schedule_versions as
select distinct on (project_id)
  *
from schedule.schedule_versions
order by project_id, data_date desc, created_at desc;

create view schedule.v_latest_activity_status as
select
  p.id as project_id,
  p.code as project_code,
  sv.id as schedule_version_id,
  sv.data_date,
  ai.id as activity_identity_id,
  ai.source_activity_uid,
  ai.activity_code as identity_activity_code,
  av.activity_code,
  av.activity_name,
  av.wbs_code,
  av.discipline,
  av.location,
  av.baseline_start,
  av.baseline_finish,
  av.current_start,
  av.current_finish,
  av.actual_start,
  av.actual_finish,
  av.percent_complete,
  av.is_critical,
  av.total_float_days,
  av.status
from schedule.projects p
join schedule.v_latest_schedule_versions sv on sv.project_id = p.id
join schedule.activity_versions av on av.schedule_version_id = sv.id
join schedule.activity_identities ai on ai.id = av.activity_identity_id;

create view schedule.v_baseline_vs_current as
select
  cur.project_id,
  cur.project_code,
  cur.activity_identity_id,
  cur.activity_code,
  cur.activity_name,
  cur.wbs_code,
  cur.discipline,
  cur.location,
  cur.baseline_start,
  cur.baseline_finish,
  cur.current_start,
  cur.current_finish,
  (cur.current_start - cur.baseline_start) as start_variance_days,
  (cur.current_finish - cur.baseline_finish) as finish_variance_days,
  cur.percent_complete,
  cur.is_critical,
  cur.total_float_days,
  cur.status
from schedule.v_latest_activity_status cur;

create view control.v_open_constraints as
select
  c.*,
  (current_date - c.opened_at) as days_open,
  case when c.due_date is not null and c.status = 'open' and c.due_date < current_date then true else false end as is_overdue
from control.constraints c
where c.status = 'open';

create view analytics.v_project_health_current as
select distinct on (p.id)
  p.id as project_id,
  p.code as project_code,
  p.name as project_name,
  m.week_start,
  m.data_date,
  m.spi,
  m.bei,
  m.ppc,
  m.irr,
  m.iao,
  m.delay_days_vs_contract,
  m.critical_activities_delayed_count,
  m.negative_float_activities_count,
  m.overdue_constraints_count,
  case
    when coalesce(m.delay_days_vs_contract, 0) > 20 or coalesce(m.spi, 1) < 0.70 or coalesce(m.bei, 1) < 0.70 then 'critical'
    when coalesce(m.delay_days_vs_contract, 0) > 10 or coalesce(m.spi, 1) < 0.85 or coalesce(m.bei, 1) < 0.85 then 'red'
    when coalesce(m.delay_days_vs_contract, 0) > 5 or coalesce(m.spi, 1) < 0.95 or coalesce(m.bei, 1) < 0.95 then 'yellow'
    else 'green'
  end as health_status
from schedule.projects p
left join analytics.project_weekly_metrics m on m.project_id = p.id
order by p.id, m.week_start desc nulls last, m.created_at desc nulls last;

-- -----------------------------------------------------------------------------
-- Indexes
-- -----------------------------------------------------------------------------

create index idx_schedule_versions_project_data_date on schedule.schedule_versions (project_id, data_date desc);
create index idx_activity_identities_project_uid on schedule.activity_identities (project_id, source_activity_uid);
create index idx_activity_versions_version_identity on schedule.activity_versions (schedule_version_id, activity_identity_id);
create index idx_activity_versions_current_finish on schedule.activity_versions (current_finish);
create index idx_activity_versions_critical on schedule.activity_versions (schedule_version_id, is_critical) where is_critical;
create index idx_activity_dependencies_pred on schedule.activity_dependencies (schedule_version_id, predecessor_activity_version_id);
create index idx_activity_dependencies_succ on schedule.activity_dependencies (schedule_version_id, successor_activity_version_id);

create index idx_import_jobs_project_imported_at on raw.import_jobs (project_id, imported_at desc);
create index idx_source_rows_import_job on raw.source_rows (import_job_id);

create index idx_progress_updates_project_data_date on control.progress_updates (project_id, data_date desc);
create index idx_activity_progress_update_identity on control.activity_progress_snapshots (progress_update_id, activity_identity_id);
create index idx_constraints_project_status_due on control.constraints (project_id, status, due_date);
create index idx_risks_project_status_severity on control.risks (project_id, status, severity_score desc);
create index idx_weekly_plans_project_week on control.weekly_plans (project_id, week_start desc);

create index idx_project_weekly_metrics_project_week on analytics.project_weekly_metrics (project_id, week_start desc);
create index idx_activity_weekly_features_lookup on analytics.activity_weekly_features (project_id, week_start, activity_identity_id);
create index idx_project_weekly_features_lookup on analytics.project_weekly_features (project_id, week_start);
create index idx_forecasts_project_date_type on analytics.forecasts (project_id, forecast_date desc, forecast_type);

-- -----------------------------------------------------------------------------
-- RLS placeholder
-- -----------------------------------------------------------------------------
-- MVP is service-role/internal scripts. Enable RLS before exposing via app/client.
-- Example later:
-- alter table schedule.projects enable row level security;
-- create policy "service role full access" on schedule.projects for all using (auth.role() = 'service_role');
