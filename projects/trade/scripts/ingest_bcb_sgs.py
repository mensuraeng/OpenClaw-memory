#!/usr/bin/env python3
"""Ingest Brazilian macro series from Banco Central SGS into Trade DB.

Read-only public source. Writes only trade.macro_observations.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.request
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any

try:
    import psycopg2  # type: ignore
except Exception:  # noqa: BLE001
    psycopg2 = None

ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = Path("/root/.openclaw/workspace")
ENV_FILE = WORKSPACE / "memory/context/trade_supabase.env"
DEFAULT_DB_URL = "postgresql://postgres:postgres@127.0.0.1:54322/postgres"

SERIES = {
    # Codes from Banco Central do Brasil SGS public API.
    "selic_meta": {"code": 432, "name": "Meta Selic", "unit": "% a.a."},
    "selic_over": {"code": 11, "name": "Taxa Selic over", "unit": "% a.d."},
    "cdi": {"code": 12, "name": "CDI", "unit": "% a.d."},
    "ipca": {"code": 433, "name": "IPCA", "unit": "% m/m"},
    "usd_brl_ptax_buy": {"code": 1, "name": "USD/BRL PTAX compra", "unit": "BRL"},
    "usd_brl_ptax_sell": {"code": 10813, "name": "USD/BRL PTAX venda", "unit": "BRL"},
}


def load_env_file(path: Path = ENV_FILE) -> None:
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        os.environ.setdefault(k, v)


def fetch_series_window(code: int, start: date, end: date) -> list[dict[str, Any]]:
    url = (
        f"https://api.bcb.gov.br/dados/serie/bcdata.sgs.{code}/dados?"
        f"formato=json&dataInicial={start.strftime('%d/%m/%Y')}&dataFinal={end.strftime('%d/%m/%Y')}"
    )
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 OpenClaw-Trade/0.1"})
    with urllib.request.urlopen(req, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))


def fetch_series(code: int, start: date, end: date) -> list[dict[str, Any]]:
    # SGS may reject very large daily ranges with HTTP 406. Chunk by year.
    rows: list[dict[str, Any]] = []
    cursor = start
    while cursor <= end:
        window_end = min(date(cursor.year, 12, 31), end)
        rows.extend(fetch_series_window(code, cursor, window_end))
        cursor = window_end + timedelta(days=1)
    return rows


def parse_ptbr_date(value: str) -> date:
    return datetime.strptime(value, "%d/%m/%Y").date()


def get_source_id(cur) -> str:
    cur.execute("select id from trade.data_sources where name = 'bcb_sgs'")
    row = cur.fetchone()
    if row:
        return row[0]
    cur.execute(
        """
        insert into trade.data_sources(name, source_type, url, cost_tier, realtime, reliability_score)
        values ('bcb_sgs', 'api', 'https://api.bcb.gov.br/dados/serie/bcdata.sgs', 'free', false, 0.90)
        returning id
        """
    )
    return cur.fetchone()[0]


def ingest(rows_by_series: dict[str, list[dict[str, Any]]], db_url: str) -> int:
    if psycopg2 is None:
        raise RuntimeError("psycopg2 is required")
    inserted = 0
    with psycopg2.connect(db_url) as conn:
        with conn.cursor() as cur:
            source_id = get_source_id(cur)
            for slug, rows in rows_by_series.items():
                meta = SERIES[slug]
                for row in rows:
                    value = str(row.get("valor", "")).replace(",", ".")
                    if value == "":
                        continue
                    cur.execute(
                        """
                        insert into trade.macro_observations(source_id, series_code, name, country, ts, value, unit, metadata)
                        values (%s,%s,%s,'BR',%s,%s,%s,%s::jsonb)
                        on conflict (series_code, country, ts) do update set
                          value = excluded.value,
                          unit = excluded.unit,
                          metadata = excluded.metadata
                        """,
                        (
                            source_id,
                            slug,
                            meta["name"],
                            parse_ptbr_date(row["data"]),
                            float(value),
                            meta["unit"],
                            json.dumps({"sgs_code": meta["code"], "source": "Banco Central do Brasil SGS"}),
                        ),
                    )
                    inserted += 1
    return inserted


def main() -> int:
    parser = argparse.ArgumentParser(description="Ingest BCB SGS macro series into Trade DB")
    parser.add_argument("--years", type=int, default=10)
    parser.add_argument("--series", nargs="*", choices=sorted(SERIES), default=sorted(SERIES))
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    end = date.today()
    start = end - timedelta(days=365 * args.years + 10)
    rows_by_series: dict[str, list[dict[str, Any]]] = {}
    errors: list[dict[str, str]] = []
    for slug in args.series:
        try:
            rows_by_series[slug] = fetch_series(int(SERIES[slug]["code"]), start, end)
        except Exception as exc:  # noqa: BLE001
            errors.append({"series": slug, "error": repr(exc)})
            rows_by_series[slug] = []

    load_env_file()
    inserted = ingest(rows_by_series, os.getenv("TRADE_DATABASE_URL", DEFAULT_DB_URL))
    summary = {
        "series": {slug: len(rows) for slug, rows in rows_by_series.items()},
        "inserted_or_updated": inserted,
        "errors": errors,
        "safety": {"read_only": True, "execution_allowed": False, "real_money": False},
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2) if args.json else summary)
    return 0 if inserted else 1


if __name__ == "__main__":
    raise SystemExit(main())
