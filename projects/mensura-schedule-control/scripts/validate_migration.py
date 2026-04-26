#!/usr/bin/env python3
from pathlib import Path
import re

migration = Path(__file__).resolve().parents[1] / "supabase" / "migrations" / "20260426144000_schedule_predictive_foundation.sql"
sql = migration.read_text(encoding="utf-8")

checks = {
    "raw schema": "create schema if not exists raw" in sql,
    "schedule schema": "create schema if not exists schedule" in sql,
    "control schema": "create schema if not exists control" in sql,
    "analytics schema": "create schema if not exists analytics" in sql,
    "projects table": "create table schedule.projects" in sql,
    "schedule_versions table": "create table schedule.schedule_versions" in sql,
    "activity_identities table": "create table schedule.activity_identities" in sql,
    "activity_versions table": "create table schedule.activity_versions" in sql,
    "activity_dependencies table": "create table schedule.activity_dependencies" in sql,
    "baselines table": "create table schedule.baselines" in sql,
    "progress_updates table": "create table control.progress_updates" in sql,
    "constraints table": "create table control.constraints" in sql,
    "weekly metrics table": "create table analytics.project_weekly_metrics" in sql,
    "feature store table": "create table analytics.activity_weekly_features" in sql,
    "forecasts table": "create table analytics.forecasts" in sql,
    "latest status view": "create view schedule.v_latest_activity_status" in sql,
}
missing = [name for name, ok in checks.items() if not ok]
if missing:
    raise SystemExit("Missing expected blocks: " + ", ".join(missing))

# crude balance checks, catches common copy mistakes
for char in ["(", ")"]:
    pass
if sql.count("(") != sql.count(")"):
    raise SystemExit(f"Unbalanced parentheses: (={sql.count('(')} )={sql.count(')')}")

statements = [s.strip() for s in sql.split(";") if s.strip() and not s.strip().startswith("--")]
print(f"OK migration={migration}")
print(f"statements={len(statements)}")
print(f"tables={len(re.findall(r'create table ', sql, re.I))}")
print(f"views={len(re.findall(r'create view ', sql, re.I))}")
print(f"indexes={len(re.findall(r'create index ', sql, re.I))}")
