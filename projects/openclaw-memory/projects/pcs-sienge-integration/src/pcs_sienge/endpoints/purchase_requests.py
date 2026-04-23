from __future__ import annotations

from ..client import SiengeClient


def get_purchase_request(client: SiengeClient, purchase_request_id: int):
    return client.get(f"purchase-requests/{purchase_request_id}")
