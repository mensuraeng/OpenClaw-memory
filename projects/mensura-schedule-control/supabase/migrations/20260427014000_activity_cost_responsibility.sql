-- migration: activity_cost_responsibility
-- purpose: add structured cost and responsibility fields for executive cost-weighted progress and delay ownership
-- created_at: 2026-04-27

alter table schedule.activity_versions
  add column if not exists planned_cost numeric,
  add column if not exists actual_cost numeric,
  add column if not exists remaining_cost numeric,
  add column if not exists cost_weight_percent numeric,
  add column if not exists responsible_name text;

create index if not exists idx_activity_versions_responsible_name on schedule.activity_versions(responsible_name);
create index if not exists idx_activity_versions_planned_cost on schedule.activity_versions(planned_cost) where planned_cost is not null;

update schedule.activity_versions av
set
  planned_cost = coalesce(
    case when (av.raw_payload->>'Custo') ~ '^-?[0-9]+([.,][0-9]+)?$' then replace(av.raw_payload->>'Custo', ',', '.')::numeric end,
    case when (av.raw_payload->>'cost') ~ '^-?[0-9]+([.,][0-9]+)?$' then replace(av.raw_payload->>'cost', ',', '.')::numeric end
  ),
  actual_cost = coalesce(
    case when (av.raw_payload->>'Custo real') ~ '^-?[0-9]+([.,][0-9]+)?$' then replace(av.raw_payload->>'Custo real', ',', '.')::numeric end,
    case when (av.raw_payload->>'actual_cost') ~ '^-?[0-9]+([.,][0-9]+)?$' then replace(av.raw_payload->>'actual_cost', ',', '.')::numeric end
  ),
  remaining_cost = case when (av.raw_payload->>'remaining_cost') ~ '^-?[0-9]+([.,][0-9]+)?$' then replace(av.raw_payload->>'remaining_cost', ',', '.')::numeric end,
  cost_weight_percent = case when (av.raw_payload->>'Peso da Atividade') ~ '^-?[0-9]+([.,][0-9]+)?$' then replace(av.raw_payload->>'Peso da Atividade', ',', '.')::numeric end,
  responsible_name = nullif(coalesce(
    av.raw_payload->>'Responsáveis',
    av.raw_payload->>'responsible',
    av.raw_payload->>'resource_names',
    av.raw_payload->>'primary_resource'
  ), '')
where av.raw_payload ?| array['Custo','cost','Custo real','actual_cost','remaining_cost','Peso da Atividade','Responsáveis','responsible','resource_names','primary_resource'];
