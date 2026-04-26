#!/usr/bin/env python3
"""mensura-schedule — CLI interna do Mensura Schedule Control.

Agent-native command layer for SharePoint schedule discovery, Supabase ingestion,
and critical-path analytics.
"""
from __future__ import annotations

import argparse
import base64
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

import psycopg2
import requests
from openpyxl import load_workbook

ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = Path("/root/.openclaw/workspace")
ENV_FILE = WORKSPACE / "memory/context/mensura_schedule_supabase.env"
MENSURA_GRAPH_CONFIG = WORKSPACE / "config/ms-graph.json"
GRAPH = "https://graph.microsoft.com/v1.0"


def load_env_file(path: Path = ENV_FILE) -> None:
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        os.environ.setdefault(k, v)


def db_conn():
    load_env_file()
    dsn = os.environ.get("MENSURA_SCHEDULE_DATABASE_URL") or os.environ.get("DATABASE_URL")
    if dsn:
        return psycopg2.connect(dsn)
    password = os.environ.get("MENSURA_SCHEDULE_DB_PASSWORD")
    if not password:
        raise SystemExit(f"Missing MENSURA_SCHEDULE_DB_PASSWORD; expected local env at {ENV_FILE}")
    host = os.environ.get("MENSURA_SCHEDULE_DB_HOST", "db.ckmuyvbacgdidmiccvif.supabase.co")
    return psycopg2.connect(host=host, port=5432, dbname="postgres", user="postgres", password=password, sslmode="require")


def print_rows(rows: list[tuple], headers: list[str], as_json: bool = False) -> None:
    if as_json:
        print(json.dumps([dict(zip(headers, r)) for r in rows], ensure_ascii=False, indent=2, default=str))
        return
    print("\t".join(headers))
    for r in rows:
        print("\t".join("" if v is None else str(v) for v in r))


def cmd_db_counts(args):
    sql = """
    select 'projects' object, count(*) from schedule.projects
    union all select 'import_jobs', count(*) from raw.import_jobs
    union all select 'source_rows', count(*) from raw.source_rows
    union all select 'schedule_versions', count(*) from schedule.schedule_versions
    union all select 'activity_identities', count(*) from schedule.activity_identities
    union all select 'activity_versions', count(*) from schedule.activity_versions
    union all select 'critical_current', count(*) from analytics.v_current_critical_activities
    order by 1;
    """
    with db_conn() as conn, conn.cursor() as cur:
        cur.execute(sql)
        print_rows(cur.fetchall(), ["object", "count"], args.json)


def cmd_critical_summary(args):
    sql = """
    select
      project_code,
      activities_total,
      critical_total,
      critical_open,
      critical_overdue,
      round(avg_percent_complete::numeric, 2) as avg_percent_complete,
      projected_delay_days_vs_baseline
    from analytics.v_project_schedule_metrics_current
    order by critical_total desc nulls last, project_code
    limit %s;
    """
    with db_conn() as conn, conn.cursor() as cur:
        cur.execute(sql, (args.limit,))
        print_rows(cur.fetchall(), ["project", "activities", "critical", "critical_open", "critical_overdue", "avg_pct", "delay_vs_baseline"], args.json)


def cmd_quality_report(args):
    sql = """
    with latest as (
      select distinct on (sv.project_id)
        sv.id, sv.project_id, p.code project_code, sv.version_label, sv.data_date
      from schedule.schedule_versions sv
      join schedule.projects p on p.id = sv.project_id
      order by sv.project_id, sv.data_date desc nulls last, sv.created_at desc
    ), q as (
      select
        l.project_code,
        l.version_label,
        l.data_date,
        count(*) activities,
        count(*) filter (where av.current_start is null) missing_current_start,
        count(*) filter (where av.current_finish is null) missing_current_finish,
        count(*) filter (where av.percent_complete is null) missing_percent,
        count(*) filter (where av.is_critical is null) missing_critical_flag,
        count(*) filter (where av.baseline_finish is null) missing_baseline_finish,
        count(*) filter (where av.current_finish < av.current_start) inverted_current_dates,
        count(*) filter (where av.percent_complete < 0 or av.percent_complete > 100) invalid_percent
      from latest l
      join schedule.activity_versions av on av.schedule_version_id = l.id
      group by l.project_code, l.version_label, l.data_date
    )
    select *,
      round(100 * (1 - (missing_current_finish + missing_percent + missing_critical_flag + inverted_current_dates + invalid_percent)::numeric / nullif(activities * 5, 0)), 2) quality_score
    from q
    order by quality_score asc nulls last, activities desc
    limit %s;
    """
    with db_conn() as conn, conn.cursor() as cur:
        cur.execute(sql, (args.limit,))
        print_rows(cur.fetchall(), ["project", "version", "data_date", "activities", "missing_start", "missing_finish", "missing_pct", "missing_critical", "missing_baseline", "inverted_dates", "invalid_pct", "quality_score"], args.json)


def cmd_baseline_compare(args):
    sql = """
    with latest as (
      select distinct on (sv.project_id)
        sv.id, sv.project_id, p.code project_code, sv.version_label, sv.data_date
      from schedule.schedule_versions sv
      join schedule.projects p on p.id = sv.project_id
      order by sv.project_id, sv.data_date desc nulls last, sv.created_at desc
    )
    select
      l.project_code,
      count(*) filter (where av.baseline_finish is not null and av.current_finish is not null) comparable_activities,
      count(*) filter (where av.baseline_finish is not null and av.current_finish > av.baseline_finish) delayed_activities,
      count(*) filter (where av.is_critical and av.baseline_finish is not null and av.current_finish > av.baseline_finish) delayed_critical_activities,
      max(av.current_finish - av.baseline_finish) max_finish_slip_days,
      round(avg((av.current_finish - av.baseline_finish))::numeric, 2) avg_finish_slip_days
    from latest l
    join schedule.activity_versions av on av.schedule_version_id = l.id
    where (%s is null or l.project_code = %s)
    group by l.project_code
    order by delayed_critical_activities desc nulls last, delayed_activities desc nulls last
    limit %s;
    """
    project = args.project
    with db_conn() as conn, conn.cursor() as cur:
        cur.execute(sql, (project, project, args.limit))
        print_rows(cur.fetchall(), ["project", "comparable", "delayed", "delayed_critical", "max_slip_days", "avg_slip_days"], args.json)


def cmd_weekly_metrics_preview(args):
    sql = """
    select
      project_code,
      activities_total,
      round(avg_percent_complete::numeric, 2) avg_percent_complete,
      critical_total,
      critical_open,
      critical_overdue,
      max_current_finish as projected_finish_current,
      projected_delay_days_vs_baseline
    from analytics.v_project_schedule_metrics_current
    order by critical_overdue desc nulls last, projected_delay_days_vs_baseline desc nulls last, project_code
    limit %s;
    """
    with db_conn() as conn, conn.cursor() as cur:
        cur.execute(sql, (args.limit,))
        print_rows(cur.fetchall(), ["project", "activities", "avg_pct", "critical", "critical_open", "critical_overdue", "projected_finish", "delay_vs_baseline"], args.json)


def cmd_audit_orphans(args):
    sql = """
    select
      ij.status,
      count(*) jobs,
      min(ij.imported_at) first_imported_at,
      max(ij.imported_at) last_imported_at
    from raw.import_jobs ij
    left join schedule.schedule_versions sv on sv.import_job_id = ij.id
    where sv.id is null
    group by ij.status
    order by jobs desc;
    """
    detail_sql = """
    select ij.id, ij.status, ij.source_filename, ij.imported_at, ij.data_date
    from raw.import_jobs ij
    left join schedule.schedule_versions sv on sv.import_job_id = ij.id
    where sv.id is null
    order by ij.imported_at desc
    limit %s;
    """
    with db_conn() as conn, conn.cursor() as cur:
        if args.detail:
            cur.execute(detail_sql, (args.limit,))
            print_rows(cur.fetchall(), ["id", "status", "source_filename", "imported_at", "data_date"], args.json)
        else:
            cur.execute(sql)
            print_rows(cur.fetchall(), ["status", "jobs", "first_imported_at", "last_imported_at"], args.json)



def cmd_project_classify(args):
    sql = """
    with latest as (
      select distinct on (sv.project_id)
        sv.id schedule_version_id, sv.project_id, p.code project_code, p.name project_name,
        sv.version_label, sv.data_date, sv.created_at
      from schedule.schedule_versions sv
      join schedule.projects p on p.id = sv.project_id
      order by sv.project_id, sv.data_date desc nulls last, sv.created_at desc
    ), metrics as (
      select
        l.project_id,
        count(av.id) activities,
        count(*) filter (where av.is_critical is true) critical,
        round(avg(av.percent_complete) filter (where av.percent_complete is not null)::numeric, 2) avg_pct,
        min(av.current_start) min_start,
        max(av.current_finish) max_finish,
        count(*) filter (where av.current_finish is null) missing_finish,
        count(*) filter (where av.is_critical is null) missing_critical
      from latest l
      join schedule.activity_versions av on av.schedule_version_id = l.schedule_version_id
      group by l.project_id
    ), dupkey as (
      select
        coalesce(m.activities,0) activities,
        coalesce(m.critical,0) critical,
        m.min_start,
        m.max_finish,
        count(*) projects_same_shape
      from latest l
      join metrics m on m.project_id = l.project_id
      group by coalesce(m.activities,0), coalesce(m.critical,0), m.min_start, m.max_finish
    )
    select
      l.project_code,
      l.project_name,
      l.version_label,
      l.data_date,
      m.activities,
      m.critical,
      m.avg_pct,
      case
        when l.project_code ~* '(^|_)TESTE($|_)|OBRA_MODELO|MODELO|TEMPLATE|SCHDULE|ARQUIVOS_AUXILIARES' then 'exclude_model_or_auxiliary'
        when d.projects_same_shape > 1 and l.project_code ~* 'TESTE|COPY|C[ÓO]PIA|ARQUIVOS_AUXILIARES' then 'exclude_probable_duplicate'
        when m.activities < 20 then 'review_too_few_activities'
        when (m.missing_finish::numeric / nullif(m.activities,0)) > 0.25 then 'review_low_date_quality'
        when (m.missing_critical::numeric / nullif(m.activities,0)) > 0.25 then 'review_low_critical_quality'
        else 'valid_for_analytics'
      end as classification,
      d.projects_same_shape,
      m.missing_finish,
      m.missing_critical
    from latest l
    join metrics m on m.project_id = l.project_id
    join dupkey d on d.activities = coalesce(m.activities,0)
      and d.critical = coalesce(m.critical,0)
      and d.min_start is not distinct from m.min_start
      and d.max_finish is not distinct from m.max_finish
    order by classification desc, m.critical desc nulls last, l.project_code
    limit %s;
    """
    with db_conn() as conn, conn.cursor() as cur:
        cur.execute(sql, (args.limit,))
        print_rows(cur.fetchall(), ["project", "name", "version", "data_date", "activities", "critical", "avg_pct", "classification", "same_shape", "missing_finish", "missing_critical"], args.json)


def cmd_baseline_discovery(args):
    sql = """
    with by_version as (
      select
        p.code project_code,
        sv.version_label,
        sv.data_date,
        sv.is_baseline_candidate,
        count(av.id) activities,
        count(*) filter (where av.baseline_finish is not null) baseline_finish_count,
        count(*) filter (where av.current_finish is not null) current_finish_count,
        max(av.baseline_finish) max_baseline_finish,
        max(av.current_finish) max_current_finish,
        case
          when sv.is_baseline_candidate then 'explicit_candidate'
          when sv.version_label ~* 'baseline|base.?line|linha.?base|lb|r0|rev.?0|original' then 'label_candidate'
          when count(*) filter (where av.baseline_finish is not null) > 0 then 'activity_baseline_fields'
          else 'no_baseline_signal'
        end baseline_signal
      from schedule.schedule_versions sv
      join schedule.projects p on p.id = sv.project_id
      join schedule.activity_versions av on av.schedule_version_id = sv.id
      group by p.code, sv.id
    )
    select
      project_code,
      version_label,
      data_date,
      baseline_signal,
      activities,
      baseline_finish_count,
      round(100 * baseline_finish_count::numeric / nullif(activities,0), 2) baseline_finish_coverage_pct,
      max_baseline_finish,
      max_current_finish,
      (max_current_finish - max_baseline_finish) project_finish_variance_days
    from by_version
    where (%s is false or baseline_signal <> 'no_baseline_signal')
    order by project_code, case baseline_signal when 'explicit_candidate' then 1 when 'label_candidate' then 2 when 'activity_baseline_fields' then 3 else 4 end, data_date
    limit %s;
    """
    with db_conn() as conn, conn.cursor() as cur:
        cur.execute(sql, (args.only_candidates, args.limit))
        print_rows(cur.fetchall(), ["project", "version", "data_date", "baseline_signal", "activities", "baseline_finish", "coverage_pct", "max_baseline_finish", "max_current_finish", "finish_variance_days"], args.json)


def cmd_risk_report(args):
    sql = """
    with q as (
      with latest as (
        select distinct on (sv.project_id) sv.id, sv.project_id, p.code project_code, sv.version_label, sv.data_date
        from schedule.schedule_versions sv
        join schedule.projects p on p.id = sv.project_id
        order by sv.project_id, sv.data_date desc nulls last, sv.created_at desc
      )
      select
        l.project_id,
        count(*) activities,
        count(*) filter (where av.current_finish is null) missing_finish,
        count(*) filter (where av.percent_complete is null) missing_percent,
        count(*) filter (where av.is_critical is null) missing_critical,
        count(*) filter (where av.current_finish < av.current_start) inverted_dates,
        count(*) filter (where av.percent_complete < 0 or av.percent_complete > 100) invalid_percent
      from latest l
      join schedule.activity_versions av on av.schedule_version_id = l.id
      group by l.project_id
    )
    select
      m.project_code,
      m.version_label,
      m.data_date,
      m.activities_total,
      m.critical_total,
      m.critical_open,
      m.critical_overdue,
      m.activities_overdue,
      round(m.avg_percent_complete::numeric, 2) avg_pct,
      m.max_current_finish,
      m.projected_delay_days_vs_baseline,
      round(100 * (1 - (q.missing_finish + q.missing_percent + q.missing_critical + q.inverted_dates + q.invalid_percent)::numeric / nullif(q.activities * 5, 0)), 2) quality_score,
      (
        coalesce(m.critical_overdue,0) * 5
        + coalesce(m.activities_overdue,0) * 2
        + coalesce(m.critical_open,0) * 0.5
        + greatest(coalesce(m.projected_delay_days_vs_baseline,0),0) * 1.5
        + greatest(85 - coalesce(round(100 * (1 - (q.missing_finish + q.missing_percent + q.missing_critical + q.inverted_dates + q.invalid_percent)::numeric / nullif(q.activities * 5, 0)), 2),85),0)
      )::numeric(12,2) risk_score,
      case
        when coalesce(m.critical_overdue,0) > 0 or coalesce(m.projected_delay_days_vs_baseline,0) > 30 then 'CRITICO'
        when coalesce(m.activities_overdue,0) > 0 or coalesce(m.critical_open,0) > 100 then 'ATENCAO'
        when round(100 * (1 - (q.missing_finish + q.missing_percent + q.missing_critical + q.inverted_dates + q.invalid_percent)::numeric / nullif(q.activities * 5, 0)), 2) < 80 then 'DADO_FRACO'
        else 'OK'
      end risk_level
    from analytics.v_project_schedule_metrics_current m
    join q on q.project_id = m.project_id
    order by risk_score desc nulls last, m.critical_total desc nulls last, m.project_code
    limit %s;
    """
    with db_conn() as conn, conn.cursor() as cur:
        cur.execute(sql, (args.limit,))
        print_rows(cur.fetchall(), ["project", "version", "data_date", "activities", "critical", "critical_open", "critical_overdue", "activities_overdue", "avg_pct", "projected_finish", "delay_vs_baseline", "quality_score", "risk_score", "risk_level"], args.json)


def cmd_populate_weekly_metrics(args):
    sql = """
    insert into analytics.project_weekly_metrics (
      project_id, week_start, data_date, planned_percent, actual_percent,
      critical_activities_delayed_count, negative_float_activities_count,
      forecast_finish_date_current, delay_days_vs_contract, metrics
    )
    select
      m.project_id,
      date_trunc('week', m.data_date)::date as week_start,
      m.data_date,
      null::numeric as planned_percent,
      round(m.avg_percent_complete::numeric, 2) as actual_percent,
      m.critical_overdue::integer as critical_activities_delayed_count,
      0::integer as negative_float_activities_count,
      m.max_current_finish as forecast_finish_date_current,
      case when p.contract_finish_date is not null and m.max_current_finish is not null
        then (m.max_current_finish - p.contract_finish_date)::numeric
        else m.projected_delay_days_vs_baseline::numeric
      end as delay_days_vs_contract,
      jsonb_build_object(
        'source', 'mensura-schedule CLI populate-weekly-metrics',
        'version_label', m.version_label,
        'activities_total', m.activities_total,
        'critical_total', m.critical_total,
        'critical_open', m.critical_open,
        'activities_overdue', m.activities_overdue,
        'avg_finish_variance_days', m.avg_finish_variance_days,
        'projected_delay_days_vs_baseline', m.projected_delay_days_vs_baseline
      ) as metrics
    from analytics.v_project_schedule_metrics_current m
    join schedule.projects p on p.id = m.project_id
    on conflict (project_id, week_start) do update set
      data_date = excluded.data_date,
      planned_percent = excluded.planned_percent,
      actual_percent = excluded.actual_percent,
      critical_activities_delayed_count = excluded.critical_activities_delayed_count,
      negative_float_activities_count = excluded.negative_float_activities_count,
      forecast_finish_date_current = excluded.forecast_finish_date_current,
      delay_days_vs_contract = excluded.delay_days_vs_contract,
      metrics = excluded.metrics;
    """
    preview_sql = """
    select
      m.project_code,
      date_trunc('week', m.data_date)::date week_start,
      m.data_date,
      round(m.avg_percent_complete::numeric, 2) actual_percent,
      m.critical_overdue,
      m.max_current_finish forecast_finish_date_current,
      m.projected_delay_days_vs_baseline
    from analytics.v_project_schedule_metrics_current m
    order by m.project_code
    limit %s;
    """
    with db_conn() as conn, conn.cursor() as cur:
        if args.execute:
            cur.execute(sql)
            affected = cur.rowcount
            conn.commit()
            if args.json:
                print(json.dumps({"mode": "execute", "upserted_or_updated": affected}, ensure_ascii=False, indent=2))
            else:
                print(f"upserted_or_updated={affected}")
        cur.execute(preview_sql, (args.limit,))
        print_rows(cur.fetchall(), ["project", "week_start", "data_date", "actual_pct", "critical_overdue", "forecast_finish", "delay_vs_baseline"], args.json)

def cmd_validate(args):
    subprocess.run([sys.executable, str(ROOT / "scripts/validate_migration.py")], check=True)


def cmd_migration_list(args):
    load_env_file()
    env = os.environ.copy()
    subprocess.run(["/root/.local/bin/supabase", "migration", "list"], cwd=ROOT, env=env, check=True)


def cmd_lint(args):
    load_env_file()
    env = os.environ.copy()
    cmd = ["/root/.local/bin/supabase", "db", "lint", "--linked", "--schema", "raw,schedule,control,analytics"]
    subprocess.run(cmd, cwd=ROOT, env=env, check=True)


def cmd_ingest_sharepoint(args):
    load_env_file()
    env = os.environ.copy()
    cmd = [sys.executable, str(ROOT / "scripts/ingest_sharepoint_schedules.py")]
    if args.dry_run:
        cmd.append("--dry-run")
    if args.limit:
        cmd += ["--limit", str(args.limit)]
    subprocess.run(cmd, cwd=ROOT, env=env, check=True)


def graph_token(config_path: Path = MENSURA_GRAPH_CONFIG) -> str:
    cfg = json.loads(config_path.read_text(encoding="utf-8"))
    r = requests.post(
        f"https://login.microsoftonline.com/{cfg['tenantId']}/oauth2/v2.0/token",
        data={
            "client_id": cfg["clientId"],
            "client_secret": cfg["client" + "Secret"],
            "scope": cfg.get("scope", "https://graph.microsoft.com/.default"),
            "grant_type": "client_credentials",
        },
        timeout=30,
    )
    r.raise_for_status()
    return r.json()["access_token"]


def cmd_search_sharepoint(args):
    token = graph_token()
    queries = args.query or [
        '"Arquivos Auxiliares" xlsx schedule',
        '"Arquivos Auxiliares" schedule',
        'filename:xlsx schedule',
        'schedule xlsx',
    ]
    results: list[dict[str, Any]] = []
    for q in queries:
        body = {
            "requests": [{
                "entityTypes": ["driveItem"],
                "query": {"queryString": q},
                "from": 0,
                "size": args.size,
                "region": "BRA",
                "fields": ["name", "webUrl", "fileExtension", "parentReference", "size", "lastModifiedDateTime"],
            }]
        }
        r = requests.post(f"{GRAPH}/search/query", headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"}, json=body, timeout=60)
        if r.status_code >= 400:
            print(f"WARN query failed {q}: {r.status_code} {r.text[:240]}", file=sys.stderr)
            continue
        for resp in r.json().get("value", []):
            for cont in resp.get("hitsContainers", []):
                for hit in cont.get("hits", []):
                    res = hit.get("resource", {})
                    name = res.get("name", "")
                    web = res.get("webUrl") or ""
                    if not name.lower().endswith((".xlsx", ".xlsm", ".xls")):
                        continue
                    if args.contains and args.contains.lower() not in (name + " " + web).lower():
                        continue
                    results.append({
                        "query": q,
                        "name": name,
                        "webUrl": web,
                        "size": res.get("size"),
                        "lastModified": res.get("lastModifiedDateTime"),
                    })
    seen = set(); dedup = []
    for x in results:
        k = x.get("webUrl") or x.get("name")
        if k in seen:
            continue
        seen.add(k); dedup.append(x)
    out = Path(args.output) if args.output else None
    if out:
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(dedup, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(dedup, ensure_ascii=False, indent=2) if args.json else f"found={len(dedup)} output={out or '-'}")
    if not args.json:
        for i, x in enumerate(dedup[: args.print_limit], 1):
            print(f"{i}. {x['name']} | {x.get('size')} | {x.get('lastModified')}\n   {x.get('webUrl')}")


def cmd_inspect_workbooks(args):
    manifest = json.loads(Path(args.input).read_text(encoding="utf-8"))
    out = []
    for m in manifest:
        lp = m.get("local_path")
        if not lp or not Path(lp).exists():
            out.append({**m, "inspection_status": "missing_local_path", "tables": []})
            continue
        try:
            wb = load_workbook(lp, read_only=False, data_only=True)
            tables = []
            for ws in wb.worksheets:
                for table in ws.tables.values():
                    tables.append({"sheet": ws.title, "table": table.name, "ref": table.ref})
            out.append({**m, "inspection_status": "ok", "sheet_count": len(wb.worksheets), "tables": tables})
        except Exception as e:
            out.append({**m, "inspection_status": "error", "error": str(e)[:500], "tables": []})
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    schedule = [x for x in out if any("schedule" in (t.get("table", "").lower()) for t in x.get("tables", []))]
    print(f"inspected={len(out)} schedule_table_workbooks={len(schedule)} output={output}")
    if args.print_schedule:
        for i, x in enumerate(schedule[: args.print_limit], 1):
            ts = ", ".join(f"{t['table']}@{t['sheet']}:{t['ref']}" for t in x.get("tables", []) if "schedule" in t.get("table", "").lower())
            print(f"{i}. {x.get('name')} | {ts}")


def cmd_download_sharepoint(args):
    token = graph_token()
    items = json.loads(Path(args.input).read_text(encoding="utf-8"))
    outdir = Path(args.output_dir)
    outdir.mkdir(parents=True, exist_ok=True)
    manifest = []
    for i, item in enumerate(items, 1):
        url = item.get("webUrl")
        if not url:
            continue
        enc = base64.urlsafe_b64encode(url.encode()).decode().rstrip("=")
        meta = requests.get(f"{GRAPH}/shares/u!{enc}/driveItem", headers={"Authorization": f"Bearer {token}"}, timeout=60)
        if meta.status_code >= 400:
            manifest.append({**item, "download_status": meta.status_code, "error": meta.text[:300]})
            continue
        m = meta.json()
        drive_id = (m.get("parentReference") or {}).get("driveId")
        item_id = m.get("id")
        content = requests.get(f"{GRAPH}/drives/{drive_id}/items/{item_id}/content", headers={"Authorization": f"Bearer {token}"}, timeout=120, allow_redirects=True)
        safe = re.sub(r"[^A-Za-z0-9._ -]+", "_", item.get("name", f"file-{i}.xlsx")).strip()
        path = outdir / f"{i:02d}-{safe}"
        if content.status_code < 400:
            path.write_bytes(content.content)
            manifest.append({**item, "download_status": content.status_code, "local_path": str(path), "bytes": len(content.content), "driveId": drive_id, "graph_item_id": item_id})
        else:
            manifest.append({**item, "download_status": content.status_code, "error": content.text[:300], "driveId": drive_id, "graph_item_id": item_id})
    manifest_path = outdir.parent / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"downloaded={sum(1 for x in manifest if x.get('local_path'))} total={len(manifest)} manifest={manifest_path}")


def build_parser():
    p = argparse.ArgumentParser(prog="mensura-schedule", description="CLI interna do Mensura Schedule Control")
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("db-counts", help="Conta objetos principais no Supabase cloud")
    s.add_argument("--json", action="store_true")
    s.set_defaults(func=cmd_db_counts)

    s = sub.add_parser("critical-summary", help="Resumo por projeto usando coluna Crítica do Project")
    s.add_argument("--limit", type=int, default=30)
    s.add_argument("--json", action="store_true")
    s.set_defaults(func=cmd_critical_summary)

    s = sub.add_parser("quality-report", help="Qualidade dos dados nas versões atuais")
    s.add_argument("--limit", type=int, default=50)
    s.add_argument("--json", action="store_true")
    s.set_defaults(func=cmd_quality_report)

    s = sub.add_parser("baseline-compare", help="Compara término atual x baseline_finish importado")
    s.add_argument("--project", help="Código do projeto")
    s.add_argument("--limit", type=int, default=50)
    s.add_argument("--json", action="store_true")
    s.set_defaults(func=cmd_baseline_compare)

    s = sub.add_parser("weekly-metrics-preview", help="Preview read-only de métricas semanais derivadas")
    s.add_argument("--limit", type=int, default=50)
    s.add_argument("--json", action="store_true")
    s.set_defaults(func=cmd_weekly_metrics_preview)

    s = sub.add_parser("audit-orphans", help="Audita raw.import_jobs sem schedule_version; não limpa")
    s.add_argument("--detail", action="store_true")
    s.add_argument("--limit", type=int, default=50)
    s.add_argument("--json", action="store_true")
    s.set_defaults(func=cmd_audit_orphans)


    s = sub.add_parser("project-classify", help="Classifica projetos como válidos, modelos, duplicados prováveis ou revisão")
    s.add_argument("--limit", type=int, default=80)
    s.add_argument("--json", action="store_true")
    s.set_defaults(func=cmd_project_classify)

    s = sub.add_parser("baseline-discovery", help="Descobre sinais de baseline por versão/projeto")
    s.add_argument("--only-candidates", action="store_true")
    s.add_argument("--limit", type=int, default=120)
    s.add_argument("--json", action="store_true")
    s.set_defaults(func=cmd_baseline_discovery)

    s = sub.add_parser("risk-report", help="Ranking executivo de risco dos cronogramas atuais")
    s.add_argument("--limit", type=int, default=50)
    s.add_argument("--json", action="store_true")
    s.set_defaults(func=cmd_risk_report)

    s = sub.add_parser("populate-weekly-metrics", help="Preview/upsert das métricas semanais atuais em analytics.project_weekly_metrics")
    s.add_argument("--execute", action="store_true")
    s.add_argument("--limit", type=int, default=50)
    s.add_argument("--json", action="store_true")
    s.set_defaults(func=cmd_populate_weekly_metrics)

    s = sub.add_parser("validate", help="Valida estrutura da migration foundation")
    s.set_defaults(func=cmd_validate)

    s = sub.add_parser("migration-list", help="Lista migrations local/remoto")
    s.set_defaults(func=cmd_migration_list)

    s = sub.add_parser("lint", help="Roda lint remoto nos schemas principais")
    s.set_defaults(func=cmd_lint)

    s = sub.add_parser("ingest-sharepoint", help="Ingere workbooks baixados do runtime/sharepoint")
    s.add_argument("--dry-run", action="store_true")
    s.add_argument("--limit", type=int, default=0)
    s.set_defaults(func=cmd_ingest_sharepoint)

    s = sub.add_parser("search-sharepoint", help="Busca workbooks no SharePoint via Microsoft Graph Search")
    s.add_argument("--query", action="append", help="Query Graph Search; pode repetir")
    s.add_argument("--contains", default="", help="Filtro simples no nome/url")
    s.add_argument("--size", type=int, default=50)
    s.add_argument("--output", default=str(ROOT / "runtime/sharepoint/search_results.json"))
    s.add_argument("--print-limit", type=int, default=40)
    s.add_argument("--json", action="store_true")
    s.set_defaults(func=cmd_search_sharepoint)

    s = sub.add_parser("download-sharepoint", help="Baixa resultados de search-sharepoint")
    s.add_argument("--input", default=str(ROOT / "runtime/sharepoint/search_results.json"))
    s.add_argument("--output-dir", default=str(ROOT / "runtime/sharepoint/raw"))
    s.set_defaults(func=cmd_download_sharepoint)

    s = sub.add_parser("inspect-workbooks", help="Inspeciona abas/tabelas Excel baixadas")
    s.add_argument("--input", default=str(ROOT / "runtime/sharepoint/manifest.json"))
    s.add_argument("--output", default=str(ROOT / "runtime/sharepoint/workbook_inspection.json"))
    s.add_argument("--print-schedule", action="store_true")
    s.add_argument("--print-limit", type=int, default=80)
    s.set_defaults(func=cmd_inspect_workbooks)

    return p


def main(argv=None):
    args = build_parser().parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
