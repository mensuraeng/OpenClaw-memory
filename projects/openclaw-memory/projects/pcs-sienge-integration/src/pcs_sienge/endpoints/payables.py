from __future__ import annotations

from ..client import SiengeClient


def list_payables_bulk(
    client: SiengeClient,
    start_date: str,
    end_date: str,
    selection_type: str = "D",
):
    return client.get(
        "bulk-data/v1/outcome",
        params={
            "startDate": start_date,
            "endDate": end_date,
            "selectionType": selection_type,
        },
    )
