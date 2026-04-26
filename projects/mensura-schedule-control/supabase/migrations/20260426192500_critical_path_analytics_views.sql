-- migration: critical_path_analytics_views
-- purpose: expose Project-informed critical activity analytics from imported schedule data
-- created_at: 2026-04-26

create or replace view analytics.v_current_critical_activities as
select
  p.id as project_id,
  p.code as project_code,
  p.name as project_name,
  sv.id as schedule_version_id,
  sv.version_label,
  sv.data_date,
  ai.id as activity_identity_id,
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
  av.physical_percent_complete,
  av.total_float_days,
  av.status,
  (av.current_finish - av.baseline_finish) as finish_variance_days,
  case
    when av.actual_finish is not null then 'finished'
    when av.current_finish is not null and av.current_finish < sv.data_date and coalesce(av.percent_complete, 0) < 100 then 'overdue'
    when av.current_finish is not null and av.current_finish <= sv.data_date + 14 and coalesce(av.percent_complete, 0) < 100 then 'due_14d'
    else 'open'
  end as critical_status
from schedule.projects p
join schedule.v_latest_schedule_versions lsv on lsv.project_id = p.id
join schedule.schedule_versions sv on sv.id = lsv.id
join schedule.activity_versions av on av.schedule_version_id = sv.id
join schedule.activity_identities ai on ai.id = av.activity_identity_id
where av.is_critical is true;

create or replace view analytics.v_project_schedule_metrics_current as
select
  p.id as project_id,
  p.code as project_code,
  p.name as project_name,
  sv.id as schedule_version_id,
  sv.version_label,
  sv.data_date,
  count(av.id) as activities_total,
  count(*) filter (where av.is_critical is true) as critical_total,
  count(*) filter (where av.is_critical is true and av.actual_finish is null and coalesce(av.percent_complete,0) < 100) as critical_open,
  count(*) filter (where av.is_critical is true and av.current_finish < sv.data_date and av.actual_finish is null and coalesce(av.percent_complete,0) < 100) as critical_overdue,
  count(*) filter (where av.current_finish < sv.data_date and av.actual_finish is null and coalesce(av.percent_complete,0) < 100) as activities_overdue,
  count(*) filter (where coalesce(av.percent_complete,0) >= 100 or av.actual_finish is not null) as activities_finished,
  avg(av.percent_complete) filter (where av.percent_complete is not null) as avg_percent_complete,
  avg((av.current_finish - av.baseline_finish)) filter (where av.current_finish is not null and av.baseline_finish is not null) as avg_finish_variance_days,
  max((av.current_finish - av.baseline_finish)) filter (where av.current_finish is not null and av.baseline_finish is not null) as max_finish_variance_days,
  min(av.current_start) as min_current_start,
  max(av.current_finish) as max_current_finish,
  max(av.baseline_finish) as max_baseline_finish,
  (max(av.current_finish) - max(av.baseline_finish)) as projected_delay_days_vs_baseline
from schedule.projects p
join schedule.v_latest_schedule_versions lsv on lsv.project_id = p.id
join schedule.schedule_versions sv on sv.id = lsv.id
join schedule.activity_versions av on av.schedule_version_id = sv.id
group by p.id, p.code, p.name, sv.id, sv.version_label, sv.data_date;
