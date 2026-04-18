from __future__ import annotations

from ..client import SiengeClient


def get_stock_building_appropriation(
    client: SiengeClient,
    cost_center_id: int,
    resource_id: int,
    detail_id: int | None = None,
    trademark_id: int | None = None,
):
    params = {}
    if detail_id is not None:
        params["detailId"] = detail_id
    if trademark_id is not None:
        params["trademarkId"] = trademark_id
    return client.get(
        f"stock-inventories/{cost_center_id}/items/{resource_id}/building-appropriation",
        params=params or None,
    )
