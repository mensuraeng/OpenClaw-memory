-- Trade Supabase Foundation v0.1
-- Purpose: analytics, predictive research, strategy lab, journal and risk governance.
-- Explicitly NOT for real-money order execution.

create extension if not exists pgcrypto;

create schema if not exists trade;

-- -----------------------------
-- Reference data
-- -----------------------------
create table if not exists trade.assets (
  id uuid primary key default gen_random_uuid(),
  symbol text not null,
  yahoo_symbol text,
  name text,
  asset_type text not null check (asset_type in ('stock','etf','index','future','fx','rate','commodity','crypto','other')),
  market text not null check (market in ('US','BR','GLOBAL','OTHER')),
  currency text not null default 'USD',
  exchange text,
  is_benchmark boolean not null default false,
  is_active boolean not null default true,
  metadata jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  unique(symbol, market)
);

create table if not exists trade.data_sources (
  id uuid primary key default gen_random_uuid(),
  name text not null unique,
  source_type text not null check (source_type in ('api','scrape','manual','file','computed')),
  url text,
  cost_tier text not null default 'free' check (cost_tier in ('free','cheap','paid','unknown')),
  realtime boolean not null default false,
  reliability_score numeric(4,2),
  metadata jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now()
);

-- -----------------------------
-- Market and macro data
-- -----------------------------
create table if not exists trade.market_bars (
  id bigserial primary key,
  asset_id uuid not null references trade.assets(id) on delete cascade,
  source_id uuid references trade.data_sources(id),
  timeframe text not null check (timeframe in ('1m','5m','15m','30m','1h','1d','1w','1mo')),
  ts timestamptz not null,
  open numeric,
  high numeric,
  low numeric,
  close numeric not null,
  adjusted_close numeric,
  volume numeric,
  vwap numeric,
  raw jsonb not null default '{}'::jsonb,
  inserted_at timestamptz not null default now(),
  unique(asset_id, source_id, timeframe, ts)
);

create index if not exists idx_market_bars_asset_tf_ts on trade.market_bars(asset_id, timeframe, ts desc);

create table if not exists trade.macro_observations (
  id bigserial primary key,
  source_id uuid references trade.data_sources(id),
  series_code text not null,
  name text not null,
  country text not null default 'US',
  ts date not null,
  value numeric not null,
  unit text,
  metadata jsonb not null default '{}'::jsonb,
  inserted_at timestamptz not null default now(),
  unique(series_code, country, ts)
);

create index if not exists idx_macro_series_ts on trade.macro_observations(series_code, country, ts desc);

create table if not exists trade.events_calendar (
  id uuid primary key default gen_random_uuid(),
  event_type text not null check (event_type in ('macro','earnings','fed','copom','holiday','company','other')),
  country text,
  asset_id uuid references trade.assets(id) on delete set null,
  title text not null,
  ts timestamptz not null,
  importance text not null default 'medium' check (importance in ('low','medium','high','critical')),
  actual numeric,
  forecast numeric,
  previous numeric,
  metadata jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now()
);

-- -----------------------------
-- Feature store
-- -----------------------------
create table if not exists trade.feature_sets (
  id uuid primary key default gen_random_uuid(),
  name text not null,
  version text not null,
  description text,
  feature_definitions jsonb not null default '{}'::jsonb,
  status text not null default 'research' check (status in ('research','candidate','active','deprecated')),
  created_at timestamptz not null default now(),
  unique(name, version)
);

create table if not exists trade.asset_features (
  id bigserial primary key,
  asset_id uuid not null references trade.assets(id) on delete cascade,
  feature_set_id uuid not null references trade.feature_sets(id) on delete cascade,
  timeframe text not null,
  ts timestamptz not null,
  features jsonb not null,
  inserted_at timestamptz not null default now(),
  unique(asset_id, feature_set_id, timeframe, ts)
);

create index if not exists idx_asset_features_asset_ts on trade.asset_features(asset_id, timeframe, ts desc);
create index if not exists idx_asset_features_gin on trade.asset_features using gin(features);

-- -----------------------------
-- Strategy Lab
-- -----------------------------
create table if not exists trade.strategies (
  id uuid primary key default gen_random_uuid(),
  name text not null,
  strategy_type text not null check (strategy_type in ('radar','factor','technical','macro','ml','pine','scalp_research','other')),
  description text,
  hypothesis text not null,
  allowed_stage text not null default 'research_only' check (allowed_stage in ('research_only','backtest','forward_test','paper','shadow','blocked')),
  risk_class text not null default 'medium' check (risk_class in ('low','medium','high','critical')),
  config jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  unique(name)
);

create table if not exists trade.strategy_runs (
  id uuid primary key default gen_random_uuid(),
  strategy_id uuid not null references trade.strategies(id) on delete cascade,
  run_type text not null check (run_type in ('backtest','walk_forward','out_of_sample','forward_test','paper','shadow')),
  universe jsonb not null default '[]'::jsonb,
  start_ts timestamptz,
  end_ts timestamptz,
  parameters jsonb not null default '{}'::jsonb,
  assumptions jsonb not null default '{}'::jsonb,
  metrics jsonb not null default '{}'::jsonb,
  status text not null default 'completed' check (status in ('planned','running','completed','failed','invalidated')),
  notes text,
  created_at timestamptz not null default now()
);

create table if not exists trade.simulated_trades (
  id uuid primary key default gen_random_uuid(),
  strategy_run_id uuid not null references trade.strategy_runs(id) on delete cascade,
  asset_id uuid not null references trade.assets(id),
  side text not null check (side in ('buy','sell','long','short','flat')),
  signal_ts timestamptz not null,
  entry_ts timestamptz,
  exit_ts timestamptz,
  expected_entry numeric,
  simulated_entry numeric,
  simulated_exit numeric,
  quantity numeric,
  gross_pnl numeric,
  estimated_cost numeric not null default 0,
  estimated_slippage numeric not null default 0,
  net_pnl numeric,
  return_pct numeric,
  thesis text,
  invalidation text,
  metadata jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now()
);

-- -----------------------------
-- Predictive Lab
-- -----------------------------
create table if not exists trade.models (
  id uuid primary key default gen_random_uuid(),
  name text not null,
  version text not null,
  model_type text not null check (model_type in ('baseline','bayesian','monte_carlo','regression','tree','classification','nlp','ensemble','other')),
  target text not null,
  horizon text not null,
  feature_set_id uuid references trade.feature_sets(id) on delete set null,
  training_window jsonb not null default '{}'::jsonb,
  parameters jsonb not null default '{}'::jsonb,
  status text not null default 'research' check (status in ('research','candidate','forward_test','active','blocked','deprecated')),
  created_at timestamptz not null default now(),
  unique(name, version)
);

create table if not exists trade.forecasts (
  id uuid primary key default gen_random_uuid(),
  model_id uuid not null references trade.models(id) on delete cascade,
  asset_id uuid not null references trade.assets(id) on delete cascade,
  as_of_ts timestamptz not null,
  horizon text not null,
  target text not null,
  probability_up numeric check (probability_up >= 0 and probability_up <= 1),
  expected_return numeric,
  expected_drawdown numeric,
  confidence text not null default 'low' check (confidence in ('low','medium','high')),
  regime text,
  base_rate jsonb not null default '{}'::jsonb,
  explanation jsonb not null default '{}'::jsonb,
  risk_gate_status text not null default 'not_evaluated' check (risk_gate_status in ('not_evaluated','pass','warn','block')),
  created_at timestamptz not null default now(),
  unique(model_id, asset_id, as_of_ts, horizon, target)
);

create index if not exists idx_forecasts_asset_asof on trade.forecasts(asset_id, as_of_ts desc);

create table if not exists trade.model_metrics (
  id uuid primary key default gen_random_uuid(),
  model_id uuid not null references trade.models(id) on delete cascade,
  evaluation_window jsonb not null,
  metrics jsonb not null,
  calibration jsonb not null default '{}'::jsonb,
  benchmark jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now()
);

-- -----------------------------
-- Risk & Journal
-- -----------------------------
create table if not exists trade.risk_events (
  id uuid primary key default gen_random_uuid(),
  severity text not null check (severity in ('info','warning','block','critical')),
  event_type text not null,
  asset_id uuid references trade.assets(id) on delete set null,
  strategy_id uuid references trade.strategies(id) on delete set null,
  model_id uuid references trade.models(id) on delete set null,
  message text not null,
  decision text,
  metadata jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now()
);

create table if not exists trade.journal_entries (
  id uuid primary key default gen_random_uuid(),
  entry_type text not null check (entry_type in ('thesis','decision','lesson','daily_report','weekly_report','model_review','risk_review','other')),
  title text not null,
  body text not null,
  related_asset_id uuid references trade.assets(id) on delete set null,
  related_strategy_id uuid references trade.strategies(id) on delete set null,
  related_model_id uuid references trade.models(id) on delete set null,
  tags text[] not null default '{}',
  metadata jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now()
);

-- -----------------------------
-- Initial seed data
-- -----------------------------
insert into trade.data_sources(name, source_type, url, cost_tier, realtime, reliability_score)
values
  ('yahoo_chart_api', 'api', 'https://query1.finance.yahoo.com', 'free', false, 0.70),
  ('brapi', 'api', 'https://brapi.dev', 'cheap', false, 0.75),
  ('bcb_sgs', 'api', 'https://www.bcb.gov.br', 'free', false, 0.90)
on conflict (name) do nothing;

insert into trade.assets(symbol, yahoo_symbol, name, asset_type, market, currency, exchange, is_benchmark)
values
  ('SPY', 'SPY', 'SPDR S&P 500 ETF Trust', 'etf', 'US', 'USD', 'NYSEARCA', true),
  ('QQQ', 'QQQ', 'Invesco QQQ Trust', 'etf', 'US', 'USD', 'NASDAQ', true),
  ('BOVA11', 'BOVA11.SA', 'iShares Ibovespa Fundo de Índice', 'etf', 'BR', 'BRL', 'B3', true),
  ('DXY', 'DX-Y.NYB', 'US Dollar Index', 'index', 'US', 'USD', 'ICE', true)
on conflict (symbol, market) do nothing;

insert into trade.strategies(name, strategy_type, description, hypothesis, allowed_stage, risk_class, config)
values
  (
    'market_radar_baseline',
    'radar',
    'Baseline read-only market radar for US/BR watchlists.',
    'Market context and benchmark-relative movement improve decision quality before any strategy is considered.',
    'research_only',
    'low',
    '{"execution_allowed": false}'::jsonb
  ),
  (
    'scalp_research_only',
    'scalp_research',
    'Restricted research bucket for scalp/futures intraday ideas.',
    'Scalp hypotheses may teach microstructure but are not approved for paper, shadow or real execution in MVP.',
    'blocked',
    'critical',
    '{"execution_allowed": false, "broker_connection_allowed": false, "reason": "day_trade_leverage_guardrail"}'::jsonb
  )
on conflict (name) do nothing;

-- Enable RLS for future API safety. Service role/backend can still operate.
alter table trade.assets enable row level security;
alter table trade.data_sources enable row level security;
alter table trade.market_bars enable row level security;
alter table trade.macro_observations enable row level security;
alter table trade.events_calendar enable row level security;
alter table trade.feature_sets enable row level security;
alter table trade.asset_features enable row level security;
alter table trade.strategies enable row level security;
alter table trade.strategy_runs enable row level security;
alter table trade.simulated_trades enable row level security;
alter table trade.models enable row level security;
alter table trade.forecasts enable row level security;
alter table trade.model_metrics enable row level security;
alter table trade.risk_events enable row level security;
alter table trade.journal_entries enable row level security;
