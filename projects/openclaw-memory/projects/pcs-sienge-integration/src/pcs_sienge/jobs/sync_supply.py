from __future__ import annotations

from ..client import SiengeClient
from ..config import SiengeConfig
from ..endpoints.purchase_orders import list_purchase_orders
from ..endpoints.purchase_quotations import list_purchase_quotations_bulk


def run(start_date: str, end_date: str, config_path: str | None = None):
    config = SiengeConfig.from_file(config_path)
    client = SiengeClient(config)
    return {
        "purchase_orders": list_purchase_orders(client).items,
        "purchase_quotations": list_purchase_quotations_bulk(client, start_date, end_date).items,
    }
