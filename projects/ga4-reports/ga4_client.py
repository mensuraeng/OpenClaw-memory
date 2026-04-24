"""
GA4 Data API client para MENSURA e MIA.
Credenciais: /root/.openclaw/workspace/credentials/ga4-service-account.json
"""
import os
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import (
    DateRange,
    Dimension,
    Metric,
    RunReportRequest,
)
from google.oauth2 import service_account

SERVICE_ACCOUNT_FILE = os.path.expanduser(
    "/root/.openclaw/workspace/credentials/ga4-service-account.json"
)

PROPERTIES = {
    "mensura": "366003407",
    "mia": "516543098",
}


def get_client() -> BetaAnalyticsDataClient:
    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE,
        scopes=["https://www.googleapis.com/auth/analytics.readonly"],
    )
    return BetaAnalyticsDataClient(credentials=credentials)


def run_report(
    company: str,
    start_date: str,
    end_date: str,
    dimensions: list[str],
    metrics: list[str],
) -> list[dict]:
    """
    Executa um relatório GA4.

    company: 'mensura' ou 'mia'
    start_date / end_date: '2026-04-01', '7daysAgo', 'today', etc.
    dimensions: ex. ['date', 'sessionSourceMedium']
    metrics: ex. ['sessions', 'activeUsers', 'screenPageViews']
    """
    property_id = PROPERTIES[company]
    client = get_client()

    request = RunReportRequest(
        property=f"properties/{property_id}",
        dimensions=[Dimension(name=d) for d in dimensions],
        metrics=[Metric(name=m) for m in metrics],
        date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
    )

    response = client.run_report(request)

    rows = []
    for row in response.rows:
        record = {}
        for i, dim in enumerate(dimensions):
            record[dim] = row.dimension_values[i].value
        for i, met in enumerate(metrics):
            record[met] = row.metric_values[i].value
        rows.append(record)

    return rows


def sessions_last_7_days(company: str) -> list[dict]:
    return run_report(
        company=company,
        start_date="7daysAgo",
        end_date="today",
        dimensions=["date"],
        metrics=["sessions", "activeUsers", "screenPageViews"],
    )


def top_sources(company: str, days: int = 30) -> list[dict]:
    return run_report(
        company=company,
        start_date=f"{days}daysAgo",
        end_date="today",
        dimensions=["sessionSourceMedium"],
        metrics=["sessions", "activeUsers"],
    )


if __name__ == "__main__":
    import json

    for company in ("mensura", "mia"):
        print(f"\n=== {company.upper()} — sessões últimos 7 dias ===")
        rows = sessions_last_7_days(company)
        print(json.dumps(rows, indent=2, ensure_ascii=False))

        print(f"\n=== {company.upper()} — top fontes (30 dias) ===")
        rows = top_sources(company)
        for r in sorted(rows, key=lambda x: int(x["sessions"]), reverse=True)[:5]:
            print(f"  {r['sessionSourceMedium']:40s} {r['sessions']} sessões")
