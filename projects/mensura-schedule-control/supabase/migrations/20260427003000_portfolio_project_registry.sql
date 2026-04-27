-- migration: portfolio_project_registry
-- purpose: master portfolio registry for Mensura/MIA/PCS projects across schedule, Sienge and 2nd-brain
-- created_at: 2026-04-27

create schema if not exists portfolio;

create table if not exists portfolio.project_registry (
  id uuid primary key default gen_random_uuid(),
  company text not null check (company in ('Mensura', 'MIA', 'PCS', 'Pessoal', 'Outro')),
  canonical_code text not null,
  canonical_name text not null,
  operational_status text not null default 'candidate' check (operational_status in ('ongoing', 'completed', 'excluded', 'duplicate', 'candidate', 'administrative', 'paused', 'cancelled')),
  include_in_executive_report boolean not null default false,
  include_in_forecast boolean not null default false,
  source_system text not null default 'manual' check (source_system in ('schedule_control', 'sienge', '2nd_brain', 'sharepoint', 'manual', 'mixed')),
  schedule_project_id uuid references schedule.projects(id) on delete set null,
  canonical_project_id uuid references portfolio.project_registry(id) on delete set null,
  exclusion_reason text,
  notes text,
  metadata jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  unique(company, canonical_code)
);

create trigger trg_project_registry_updated_at
before update on portfolio.project_registry
for each row execute function public.set_updated_at();

create table if not exists portfolio.project_aliases (
  id uuid primary key default gen_random_uuid(),
  project_registry_id uuid not null references portfolio.project_registry(id) on delete cascade,
  alias text not null,
  alias_type text not null default 'code' check (alias_type in ('code', 'name', 'sharepoint', 'sienge', 'manual')),
  source_system text not null default 'manual',
  created_at timestamptz not null default now(),
  unique(project_registry_id, alias, alias_type)
);

create index if not exists idx_project_registry_company_status on portfolio.project_registry(company, operational_status);
create index if not exists idx_project_registry_schedule_project on portfolio.project_registry(schedule_project_id);
create index if not exists idx_project_registry_executive on portfolio.project_registry(include_in_executive_report) where include_in_executive_report;
create index if not exists idx_project_aliases_alias on portfolio.project_aliases(alias);

create or replace view portfolio.v_project_registry_current as
select
  pr.id,
  pr.company,
  pr.canonical_code,
  pr.canonical_name,
  pr.operational_status,
  pr.include_in_executive_report,
  pr.include_in_forecast,
  pr.source_system,
  pr.schedule_project_id,
  sp.code as schedule_project_code,
  sp.name as schedule_project_name,
  cp.canonical_code as canonical_parent_code,
  pr.exclusion_reason,
  pr.notes,
  coalesce(jsonb_agg(pa.alias order by pa.alias) filter (where pa.id is not null), '[]'::jsonb) as aliases,
  pr.metadata,
  pr.updated_at
from portfolio.project_registry pr
left join schedule.projects sp on sp.id = pr.schedule_project_id
left join portfolio.project_registry cp on cp.id = pr.canonical_project_id
left join portfolio.project_aliases pa on pa.project_registry_id = pr.id
group by pr.id, sp.code, sp.name, cp.canonical_code;
