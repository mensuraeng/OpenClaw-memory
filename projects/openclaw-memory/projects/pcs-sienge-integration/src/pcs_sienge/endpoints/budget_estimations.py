from __future__ import annotations

import base64
import json
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass, field
from typing import Any

from ..config import SiengeConfig


PUBLIC_API_BASE = "https://api.sienge.com.br/{subdomain}/public/api/v1"


@dataclass
class BudgetSheet:
    id: int
    description: str
    building_unit_id: int
    raw: dict = field(default_factory=dict)


@dataclass
class BudgetResource:
    id: int
    description: str
    unit_of_measure: str
    category: str
    resource_code: str
    raw: dict = field(default_factory=dict)


def _basic_auth_header(config: SiengeConfig) -> str:
    raw = f"{config.username}:{config.password}".encode()
    return f"Basic {base64.b64encode(raw).decode()}"


def _public_get(config: SiengeConfig, path: str, params: dict[str, Any] | None = None) -> dict:
    base = PUBLIC_API_BASE.format(subdomain=config.subdomain)
    query = f"?{urllib.parse.urlencode(params)}" if params else ""
    url = f"{base}/{path.lstrip('/')}{query}"
    headers = {
        "Authorization": _basic_auth_header(config),
        "Accept": "application/json",
    }
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=config.timeout_seconds) as r:
            return json.loads(r.read().decode())
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="ignore")
        raise RuntimeError(f"[{exc.code}] {path}: {body[:200]}") from exc


def get_budget_sheets(config: SiengeConfig, building_id: int, limit: int = 200, offset: int = 0) -> list[dict]:
    """Retorna planilhas do orçamento da obra (uma por unidade construtiva).
    Requer recurso building-cost-estimations-v1 habilitado no usuário de API.
    """
    data = _public_get(
        config,
        f"building-cost-estimations/{building_id}/sheets",
        params={"limit": limit, "offset": offset},
    )
    return data.get("results", [])


def get_budget_sheet_items(
    config: SiengeConfig, building_id: int, building_unit_id: int, limit: int = 200, offset: int = 0
) -> list[dict]:
    """Retorna itens de uma planilha do orçamento (serviços/composições com quantidades e valores)."""
    data = _public_get(
        config,
        f"building-cost-estimations/{building_id}/sheets/{building_unit_id}/items",
        params={"limit": limit, "offset": offset},
    )
    return data.get("results", [])


def get_budget_resources(config: SiengeConfig, building_id: int, limit: int = 200, offset: int = 0) -> list[dict]:
    """Retorna insumos cadastrados no orçamento da obra (materiais, mão de obra, equipamentos).
    Este endpoint NÃO requer permissão especial — já funciona com o usuário atual.
    """
    data = _public_get(
        config,
        f"building-cost-estimations/{building_id}/resources",
        params={"limit": limit, "offset": offset},
    )
    return data.get("results", [])


def get_budget_resources_all(config: SiengeConfig, building_id: int) -> list[dict]:
    """Busca todos os insumos do orçamento paginando automaticamente."""
    all_items: list[dict] = []
    offset = 0
    limit = 200
    while True:
        page = get_budget_resources(config, building_id, limit=limit, offset=offset)
        if not page:
            break
        all_items.extend(page)
        if len(page) < limit:
            break
        offset += limit
    return all_items


def get_cost_estimate_resources(
    config: SiengeConfig, building_id: int, limit: int = 200, offset: int = 0
) -> list[dict]:
    """Retorna insumos orçados (com valores unitários e totais por composição).
    Requer recurso building-cost-estimation-cost-estimate-resources-v1.
    """
    data = _public_get(
        config,
        f"building-cost-estimations/{building_id}/cost-estimate-resources",
        params={"limit": limit, "offset": offset},
    )
    return data.get("results", [])
