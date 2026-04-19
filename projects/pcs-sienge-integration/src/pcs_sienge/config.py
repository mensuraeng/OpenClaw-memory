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
    token_url: str
    api_base_url: str
    company_name: str | None = None
    api_user_name: str | None = None
    api_user_id: str | None = None
    company_id: str | None = None
    timezone: str | None = None
    auth_type: str = "oauth2_basic_oauth_client_credentials"
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

        token_url = data.get("tokenUrl") or f"https://{subdomain}.sienge.com.br/sienge/oauth/token"
        api_base_url = data.get("apiBaseUrl") or f"https://{subdomain}.sienge.com.br/sienge/api/v1"
        return cls(
            subdomain=subdomain,
            username=username,
            password=password,
            token_url=token_url.rstrip("/"),
            api_base_url=api_base_url.rstrip("/"),
            company_name=data.get("companyName"),
            api_user_name=data.get("apiUserName"),
            api_user_id=data.get("apiUserId"),
            company_id=data.get("companyId"),
            timezone=data.get("timezone"),
            auth_type=data.get("authType") or "oauth2_basic_oauth_client_credentials",
            timeout_seconds=timeout_seconds,
        )
