-- XP data access tracking for Trade Wealth Monitor.
-- No secrets. No order execution.

create table if not exists trade.broker_connections (
  id uuid primary key default gen_random_uuid(),
  broker text not null,
  connection_method text not null check (connection_method in ('manual_export','open_finance','developer_portal','browser_assisted','other')),
  status text not null default 'planned' check (status in ('planned','active','blocked','revoked','failed')),
  read_only boolean not null default true,
  execution_enabled boolean not null default false,
  consent_scope jsonb not null default '{}'::jsonb,
  notes text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  unique(broker, connection_method)
);

create table if not exists trade.broker_import_jobs (
  id uuid primary key default gen_random_uuid(),
  broker_connection_id uuid references trade.broker_connections(id) on delete set null,
  broker text not null,
  import_type text not null check (import_type in ('portfolio_snapshot','positions','transactions','funds','fixed_income','statement','other')),
  source_format text not null check (source_format in ('csv','xlsx','pdf','image','api','manual','other')),
  source_label text,
  status text not null default 'received' check (status in ('received','parsed','validated','imported','failed','discarded')),
  rows_detected integer,
  rows_imported integer,
  error_message text,
  metadata jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now()
);

insert into trade.broker_connections(broker, connection_method, status, read_only, execution_enabled, consent_scope, notes)
values
  ('XP', 'manual_export', 'active', true, false, '{"data":"positions/statements exported by user"}'::jsonb, 'Immediate path: user-provided XP CSV/PDF/images.'),
  ('XP', 'open_finance', 'planned', true, false, '{"data":"investments read-only after explicit consent"}'::jsonb, 'Future regulated path. Requires consent and compatible receiver/TPP.'),
  ('XP', 'developer_portal', 'planned', true, false, '{"data":"positions/movements/products if partner access is approved"}'::jsonb, 'XP Developer Portal appears partner-oriented. Validate eligibility before use.')
on conflict (broker, connection_method) do update set
  notes = excluded.notes,
  updated_at = now();

insert into trade.data_sources(name, source_type, url, cost_tier, realtime, reliability_score, metadata)
values
  ('xp_manual_export', 'file', null, 'free', false, 0.75, '{"broker":"XP","method":"manual_export","scope":"positions_statements"}'::jsonb),
  ('xp_developer_portal', 'api', 'https://developer.xpinc.com/', 'unknown', false, 0.70, '{"broker":"XP","method":"developer_portal","status":"requires_access_validation"}'::jsonb),
  ('open_finance_investments', 'api', 'https://openfinancebrasil.org.br/', 'unknown', false, 0.85, '{"method":"open_finance","scope":"investments_read_only_after_consent"}'::jsonb)
on conflict (name) do update set
  metadata = trade.data_sources.metadata || excluded.metadata;

alter table trade.broker_connections enable row level security;
alter table trade.broker_import_jobs enable row level security;
