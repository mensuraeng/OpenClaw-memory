-- migration: schedule_intake_packages
-- purpose: Supabase structure for receiving schedule files by company/status/package under 500MB
-- created_at: 2026-04-27

create schema if not exists intake;

create table if not exists intake.schedule_packages (
  id uuid primary key default gen_random_uuid(),
  package_code text not null unique,
  company text not null check (company in ('Mensura', 'MIA', 'PCS', 'Pessoal', 'Outro')),
  package_status text not null check (package_status in ('em_andamento', 'concluidas', 'misto', 'historico', 'outro')),
  lot_number integer not null default 1 check (lot_number > 0),
  expected_filename text,
  max_size_mb integer not null default 500 check (max_size_mb > 0),
  received_filename text,
  received_uri text,
  received_size_bytes bigint check (received_size_bytes is null or received_size_bytes >= 0),
  file_hash text,
  intake_status text not null default 'planned' check (intake_status in ('planned', 'received', 'expanded', 'validated', 'imported', 'partial', 'failed', 'archived')),
  received_at timestamptz,
  expanded_at timestamptz,
  notes text,
  metadata jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create trigger trg_schedule_packages_updated_at
before update on intake.schedule_packages
for each row execute function public.set_updated_at();

create table if not exists intake.schedule_package_items (
  id uuid primary key default gen_random_uuid(),
  package_id uuid not null references intake.schedule_packages(id) on delete cascade,
  company text not null check (company in ('Mensura', 'MIA', 'PCS', 'Pessoal', 'Outro')),
  project_registry_id uuid references portfolio.project_registry(id) on delete set null,
  project_code text not null,
  project_name text,
  project_operational_status text not null default 'candidate' check (project_operational_status in ('ongoing', 'completed', 'candidate', 'administrative', 'excluded', 'duplicate', 'unknown')),
  relative_path text,
  source_filename text,
  file_type text not null default 'mpp' check (file_type in ('mpp', 'xml', 'xlsx', 'zip', 'csv', 'other')),
  version_label text,
  data_date date,
  file_hash text,
  schedule_version_id uuid references schedule.schedule_versions(id) on delete set null,
  import_job_id uuid references raw.import_jobs(id) on delete set null,
  item_status text not null default 'planned' check (item_status in ('planned', 'received', 'validated', 'imported', 'skipped', 'failed', 'partial')),
  is_partial boolean not null default false,
  validation_errors jsonb not null default '[]'::jsonb,
  notes text,
  metadata jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  unique(package_id, relative_path),
  unique(package_id, project_code, version_label)
);

create trigger trg_schedule_package_items_updated_at
before update on intake.schedule_package_items
for each row execute function public.set_updated_at();

create index if not exists idx_schedule_packages_company_status on intake.schedule_packages(company, package_status, intake_status);
create index if not exists idx_schedule_package_items_package on intake.schedule_package_items(package_id);
create index if not exists idx_schedule_package_items_project on intake.schedule_package_items(project_code, item_status);
create index if not exists idx_schedule_package_items_registry on intake.schedule_package_items(project_registry_id);

create or replace view intake.v_schedule_intake_dashboard as
select
  p.id as package_id,
  p.package_code,
  p.company,
  p.package_status,
  p.lot_number,
  p.expected_filename,
  p.received_filename,
  p.intake_status,
  p.max_size_mb,
  round((p.received_size_bytes::numeric / 1024 / 1024), 2) as received_size_mb,
  count(i.id)::int as item_count,
  count(i.id) filter (where i.item_status='imported')::int as imported_count,
  count(i.id) filter (where i.item_status='failed')::int as failed_count,
  count(i.id) filter (where i.is_partial)::int as partial_count,
  coalesce(jsonb_agg(jsonb_build_object(
    'project_code', i.project_code,
    'project_name', i.project_name,
    'status', i.item_status,
    'version_label', i.version_label,
    'data_date', i.data_date,
    'schedule_version_id', i.schedule_version_id,
    'is_partial', i.is_partial
  ) order by i.project_code) filter (where i.id is not null), '[]'::jsonb) as items,
  p.notes,
  p.updated_at
from intake.schedule_packages p
left join intake.schedule_package_items i on i.package_id=p.id
group by p.id;

insert into intake.schedule_packages(package_code, company, package_status, lot_number, expected_filename, notes, metadata)
values
  ('MENSURA_em_andamento_lote01', 'Mensura', 'em_andamento', 1, 'MENSURA_em_andamento_lote01.zip', 'Prioridade 1: obras Mensura em andamento.', jsonb_build_object('priority', 1)),
  ('MIA_em_andamento_lote01', 'MIA', 'em_andamento', 1, 'MIA_em_andamento_lote01.zip', 'Prioridade 2: obras MIA em andamento.', jsonb_build_object('priority', 2)),
  ('PCS_em_andamento_lote01', 'PCS', 'em_andamento', 1, 'PCS_em_andamento_lote01.zip', 'Prioridade 3: obras PCS em andamento; Teatro Suzano quando cronograma estiver pronto.', jsonb_build_object('priority', 3)),
  ('MENSURA_concluidas_lote01', 'Mensura', 'concluidas', 1, 'MENSURA_concluidas_lote01.zip', 'Histórico Mensura para benchmark e calibração futura.', jsonb_build_object('priority', 4)),
  ('MIA_concluidas_lote01', 'MIA', 'concluidas', 1, 'MIA_concluidas_lote01.zip', 'Histórico MIA para benchmark e calibração futura.', jsonb_build_object('priority', 5)),
  ('PCS_concluidas_lote01', 'PCS', 'concluidas', 1, 'PCS_concluidas_lote01.zip', 'Histórico PCS para benchmark e calibração futura.', jsonb_build_object('priority', 6))
on conflict (package_code) do update set
  expected_filename=excluded.expected_filename,
  notes=excluded.notes,
  metadata=intake.schedule_packages.metadata || excluded.metadata;
