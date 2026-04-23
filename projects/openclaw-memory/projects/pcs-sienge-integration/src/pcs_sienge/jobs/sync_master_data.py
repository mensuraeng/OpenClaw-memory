from __future__ import annotations

from ..client import SiengeClient
from ..config import SiengeConfig
from ..endpoints.cost_centers import list_cost_centers
from ..endpoints.creditors import list_creditors


def run(config_path: str | None = None):
    config = SiengeConfig.from_file(config_path)
    client = SiengeClient(config)
    return {
        "creditors": list_creditors(client).items,
        "cost_centers": list_cost_centers(client).items,
    }
