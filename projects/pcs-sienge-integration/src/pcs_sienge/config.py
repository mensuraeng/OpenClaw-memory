from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path

from .errors import SiengeConfigError


DEFAULT_CONFIG_PATH = Path("/root/.openclaw/workspace/config/sienge-pcs.json")


@dataclass
class SiengeConfig:
    subdomain: str
    username: str
    password: str
    base_url: str
    timeout_seconds: int = 30

    @classmethod
    def from_file(cls, path: str | os.PathLike[str] | None = None) -> "SiengeConfig":
        config_path = Path(path) if path else DEFAULT_CONFIG_PATH
        if not config_path.exists():
            raise SiengeConfigError(
                f"Arquivo de configuração não encontrado: {config_path}"
            )

        data = json.loads(config_path.read_text(encoding="utf-8"))
        subdomain = data.get("subdomain")
        username = data.get("username")
        password = data.get("password")
        timeout_seconds = int(data.get("timeoutSeconds", 30))

        if not subdomain or not username or not password:
            raise SiengeConfigError(
                "Config inválida. Esperado: subdomain, username, password"
            )

        base_url = data.get("baseUrl") or f"https://api.sienge.com.br/{subdomain}/public/api"
        return cls(
            subdomain=subdomain,
            username=username,
            password=password,
            base_url=base_url.rstrip("/"),
            timeout_seconds=timeout_seconds,
        )
