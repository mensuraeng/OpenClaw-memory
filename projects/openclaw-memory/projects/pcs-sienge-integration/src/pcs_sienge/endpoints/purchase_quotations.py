from __future__ import annotations

from ..client import SiengeClient


def list_purchase_quotations_bulk(client: SiengeClient, start_date: str, end_date: str):
    return client.get(
        "bulk-data/v1/purchase-quotations",
        params={"startDate": start_date, "endDate": end_date},
    )


def authorize_supplier_negotiation(
    client: SiengeClient,
    purchase_quotation_id: int,
    supplier_id: int,
):
    return client.patch(
        f"purchase-quotations/{purchase_quotation_id}/suppliers/{supplier_id}/authorization"
    )
