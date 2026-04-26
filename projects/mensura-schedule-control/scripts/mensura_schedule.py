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
