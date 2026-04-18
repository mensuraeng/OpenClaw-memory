from __future__ import annotations

from ..client import SiengeClient


def list_purchase_orders(client: SiengeClient, limit: int = 200, offset: int = 0):
    return client.get("purchase-orders", params={"limit": limit, "offset": offset})


def get_purchase_order(client: SiengeClient, purchase_order_id: int):
    return client.get(f"purchase-orders/{purchase_order_id}")
