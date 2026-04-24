from __future__ import annotations

import base64
import json
import urllib.parse
import urllib.request
from dataclasses import dataclass

from .config import SiengeConfig
from .errors import SiengeAuthError


@dataclass
class AccessToken:
    token: str
    token_type: str = "Bearer"
    expires_in: int | None = None

    @property
    def authorization_header(self) -> str:
        return f"{self.token_type} {self.token}".strip()


def build_client_basic_auth_header(config: SiengeConfig) -> str:
    raw = f"{config.username}:{config.password}".encode("utf-8")
    token = base64.b64encode(raw).decode("utf-8")
    return f"Basic {token}"


def fetch_basic_access_token(config: SiengeConfig) -> AccessToken:
    """Returns a Basic auth token directly — no OAuth token exchange needed."""
    raw = f"{config.username}:{config.password}".encode("utf-8")
    encoded = base64.b64encode(raw).decode("utf-8")
    return AccessToken(token=encoded, token_type="Basic")


def fetch_access_token(config: SiengeConfig) -> AccessToken:
    payload = urllib.parse.urlencode(
        {
            "grant_type": "client_credentials",
        }
    ).encode("utf-8")
    headers = {
        "Authorization": build_client_basic_auth_header(config),
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "application/json",
    }
    req = urllib.request.Request(config.token_url, data=payload, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=config.timeout_seconds) as response:
            content = response.read()
            data = json.loads(content.decode("utf-8") or "{}")
    except urllib.error.HTTPError as exc:
        payload = exc.read().decode("utf-8", errors="ignore")
        raise SiengeAuthError(f"Falha ao obter token OAuth2: [{exc.code}] {payload}") from exc
    except urllib.error.URLError as exc:
        raise SiengeAuthError(f"Falha de conexão ao obter token OAuth2: {exc.reason}") from exc

    access_token = data.get("access_token")
    token_type = data.get("token_type") or "Bearer"
    expires_in = data.get("expires_in")
    if not access_token:
        raise SiengeAuthError(f"Resposta de auth sem access_token: {data}")
    return AccessToken(token=access_token, token_type=token_type, expires_in=expires_in)
