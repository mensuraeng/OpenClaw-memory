from __future__ import annotations

import json
import time
import urllib.error
import urllib.parse
import urllib.request
from typing import Any

from .auth import build_basic_auth_header
from .config import SiengeConfig
from .errors import SiengeApiError
from .models import FetchResult


class SiengeClient:
    def __init__(self, config: SiengeConfig):
        self.config = config
        self.auth_header = build_basic_auth_header(config)

    def _request(
        self,
        method: str,
        path: str,
        params: dict[str, Any] | None = None,
        body: dict[str, Any] | None = None,
        retries: int = 3,
    ) -> FetchResult:
        query = f"?{urllib.parse.urlencode(params, doseq=True)}" if params else ""
        url = f"{self.config.base_url}/{path.lstrip('/')}" + query
        data = json.dumps(body).encode("utf-8") if body else None
        headers = {
            "Authorization": self.auth_header,
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

        for attempt in range(1, retries + 1):
            req = urllib.request.Request(url, data=data, headers=headers, method=method)
            try:
                with urllib.request.urlopen(req, timeout=self.config.timeout_seconds) as response:
                    content = response.read()
                    payload = json.loads(content) if content else {}
                    items = []
                    if isinstance(payload, dict):
                        items = payload.get("results") or payload.get("data") or payload.get("value") or []
                    elif isinstance(payload, list):
                        items = payload
                    return FetchResult(endpoint=path, status_code=response.status, items=items, raw=payload)
            except urllib.error.HTTPError as exc:
                payload = exc.read().decode("utf-8", errors="ignore")
                if attempt >= retries or exc.code < 500:
                    raise SiengeApiError(exc.code, f"Erro na API {path}", payload)
            except urllib.error.URLError as exc:
                payload = str(exc.reason)
                if attempt >= retries:
                    raise SiengeApiError(0, f"Falha de conexão em {path}", payload)

            time.sleep(min(attempt * 2, 10))

        raise SiengeApiError(0, f"Falha inesperada em {path}")

    def get(self, path: str, params: dict[str, Any] | None = None) -> FetchResult:
        return self._request("GET", path, params=params)

    def post(self, path: str, body: dict[str, Any]) -> FetchResult:
        return self._request("POST", path, body=body)

    def patch(self, path: str, body: dict[str, Any] | None = None) -> FetchResult:
        return self._request("PATCH", path, body=body)
