from __future__ import annotations

import base64

from .config import SiengeConfig


def build_basic_auth_header(config: SiengeConfig) -> str:
    raw = f"{config.username}:{config.password}".encode("utf-8")
    token = base64.b64encode(raw).decode("utf-8")
    return f"Basic {token}"
