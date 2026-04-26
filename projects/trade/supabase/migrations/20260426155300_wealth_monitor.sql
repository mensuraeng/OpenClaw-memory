-- Trade Wealth Monitor v0.1
-- Purpose: investment products, fixed income/funds monitoring, opportunities and portfolio analytics.
-- Explicitly NOT for automatic investment execution.

create table if not exists trade.investment_products (
  id uuid primary key default gen_random_uuid(),
  product_type text not null check (product_type in (
    'cdb','lci','lca','cri','cra','debenture','tesouro_direto','structured_note',
    'open_fund','listed_fund','fii','etf','fi_infra','stock','commodity','fx','index','other'
  )),
  symbol text,
  name text not null,
  issuer text,
  manager text,
  administrator text,
  market text not null default 'BR' check (market in ('BR','US','GLOBAL','OTHER')),
  currency text not null default 'BRL',
  indexer text,
  rate numeric,
  rate_unit text,
  benchmark text,
  maturity_date date,
  liquidity_terms text,
  tax_treatment text,
  fgc_eligible boolean,
  rating text,
  risk_class text not null default 'unknown' check (risk_class in ('low','medium','high','critical','unknown')),
  status text not null default 'monitored' check (status in ('monitored','eligible','blocked','expired','owned','watchlist')),
  source_id uuid references trade.data_sources(id) on delete set null,
  metadata jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create unique index if not exists uq_investment_products_identity
  on trade.investment_products(product_type, coalesce(symbol,''), name, coalesce(maturity_date, '1900-01-01'::date));
create index if not exists idx_investment_products_type_status on trade.investment_products(product_type, status);
create index if not exists idx_investment_products_maturity on trade.investment_products(maturity_date);

create table if not exists trade.product_quotes (
  id bigserial primary key,
  product_id uuid not null references trade.investment_products(id) on delete cascade,
  source_id uuid references trade.data_sources(id) on delete set null,
  as_of_ts timestamptz not null,
  price numeric,
  nav numeric,
  quota numeric,
  yield_rate numeric,
  spread_bps numeric,
  duration numeric,
  liquidity_score numeric,
  raw jsonb not null default '{}'::jsonb,
  inserted_at timestamptz not null default now(),
  unique(product_id, source_id, as_of_ts)
);

create index if not exists idx_product_quotes_product_ts on trade.product_quotes(product_id, as_of_ts desc);

create table if not exists trade.portfolio_positions (
  id uuid primary key default gen_random_uuid(),
  product_id uuid references trade.investment_products(id) on delete set null,
  asset_id uuid references trade.assets(id) on delete set null,
  account_label text,
  position_type text not null default 'investment' check (position_type in ('investment','cash','paper','watchlist')),
  quantity numeric,
  invested_amount numeric,
  current_value numeric,
  currency text not null default 'BRL',
  acquisition_date date,
  maturity_date date,
  contracted_rate numeric,
  contracted_indexer text,
  liquidity_terms text,
  notes text,
  metadata jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create index if not exists idx_portfolio_positions_product on trade.portfolio_positions(product_id);
create index if not exists idx_portfolio_positions_asset on trade.portfolio_positions(asset_id);

create table if not exists trade.portfolio_snapshots (
  id uuid primary key default gen_random_uuid(),
  as_of_date date not null,
  currency text not null default 'BRL',
  total_value numeric,
  allocation jsonb not null default '{}'::jsonb,
  risk_summary jsonb not null default '{}'::jsonb,
  notes text,
  created_at timestamptz not null default now(),
  unique(as_of_date, currency)
);

create table if not exists trade.investment_opportunities (
  id uuid primary key default gen_random_uuid(),
  product_id uuid not null references trade.investment_products(id) on delete cascade,
  as_of_ts timestamptz not null default now(),
  source_id uuid references trade.data_sources(id) on delete set null,
  opportunity_type text not null default 'monitor' check (opportunity_type in ('monitor','new_offer','rebalance','rollover','risk_alert','maturity_alert')),
  expected_return_net numeric,
  benchmark_return_net numeric,
  spread_bps numeric,
  liquidity_score numeric,
  credit_score numeric,
  concentration_after_pct numeric,
  confidence text not null default 'low' check (confidence in ('low','medium','high')),
  decision_status text not null default 'research' check (decision_status in ('research','monitor','eligible','blocked','needs_human_review')),
  thesis text,
  risk_notes text,
  metadata jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now()
);

create index if not exists idx_investment_opportunities_status on trade.investment_opportunities(decision_status, as_of_ts desc);

insert into trade.data_sources(name, source_type, url, cost_tier, realtime, reliability_score, metadata)
values
  ('bcb_sgs_macro', 'api', 'https://www.bcb.gov.br/estabilidadefinanceira/selic', 'free', false, 0.95, '{"scope":"selic_ipca_macro"}'::jsonb),
  ('tesouro_direto_public', 'api', 'https://www.tesourodireto.com.br', 'free', false, 0.90, '{"scope":"tesouro_rates_prices"}'::jsonb),
  ('cvm_open_data', 'api', 'https://dados.cvm.gov.br', 'free', false, 0.90, '{"scope":"funds_quotes_reports"}'::jsonb),
  ('manual_broker_export', 'file', null, 'free', false, 0.60, '{"scope":"private_fixed_income_offers_positions"}'::jsonb)
on conflict (name) do nothing;

insert into trade.investment_products(product_type, symbol, name, market, currency, indexer, benchmark, risk_class, status, metadata)
values
  ('tesouro_direto', 'TESOURO_SELIC', 'Tesouro Selic', 'BR', 'BRL', 'SELIC', 'CDI', 'low', 'monitored', '{"baseline":true}'::jsonb),
  ('tesouro_direto', 'TESOURO_IPCA', 'Tesouro IPCA+', 'BR', 'BRL', 'IPCA+', 'IPCA', 'medium', 'monitored', '{"baseline":true}'::jsonb),
  ('index', 'CDI', 'CDI', 'BR', 'BRL', 'CDI', 'CDI', 'low', 'monitored', '{"baseline":true}'::jsonb),
  ('commodity', 'GOLD', 'Ouro', 'GLOBAL', 'USD', null, 'DXY', 'medium', 'monitored', '{"commodity":"gold"}'::jsonb),
  ('commodity', 'SILVER', 'Prata', 'GLOBAL', 'USD', null, 'DXY', 'high', 'monitored', '{"commodity":"silver"}'::jsonb)
on conflict do nothing;

alter table trade.investment_products enable row level security;
alter table trade.product_quotes enable row level security;
alter table trade.portfolio_positions enable row level security;
alter table trade.portfolio_snapshots enable row level security;
alter table trade.investment_opportunities enable row level security;
