from __future__ import annotations

from ..client import SiengeClient


def list_cost_centers(client: SiengeClient, limit: int = 200, offset: int = 0):
    return client.get("v1/cost-centers", params={"limit": limit, "offset": offset})
