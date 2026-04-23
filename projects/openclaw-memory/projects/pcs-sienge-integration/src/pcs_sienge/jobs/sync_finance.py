from __future__ import annotations

from ..client import SiengeClient
from ..config import SiengeConfig
from ..endpoints.payables import list_payables_bulk
from ..endpoints.receivables import list_receivables_bulk


def run(start_date: str, end_date: str, config_path: str | None = None):
    config = SiengeConfig.from_file(config_path)
    client = SiengeClient(config)
    return {
        "payables": list_payables_bulk(client, start_date, end_date).items,
        "receivables": list_receivables_bulk(client, start_date, end_date).items,
    }
