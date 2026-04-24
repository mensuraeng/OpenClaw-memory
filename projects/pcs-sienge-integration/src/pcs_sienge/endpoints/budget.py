from __future__ import annotations

from ..client import SiengeClient


def get_sheets(client: SiengeClient, building_id: int):
    """Lista planilhas de orçamento da obra."""
    return client.get(f"building-cost-estimations/{building_id}/sheets")


def get_resources(client: SiengeClient, building_id: int, sheet_id: int | None = None):
    """Lista insumos/recursos do orçamento da obra."""
    params = {}
    if sheet_id is not None:
        params["sheetId"] = sheet_id
    return client.get(
        f"building-cost-estimations/{building_id}/resources",
        params=params or None,
    )


def create_resource(client: SiengeClient, building_id: int, payload: dict) -> dict:
    """Cria um item de insumo no orçamento da obra."""
    return client.post(f"building-cost-estimations/{building_id}/resources", body=payload)


def update_resource(client: SiengeClient, building_id: int, resource_id: int, payload: dict) -> dict:
    """Atualiza quantidade/custo de um insumo no orçamento."""
    return client.patch(
        f"building-cost-estimations/{building_id}/resources/{resource_id}",
        body=payload,
    )
