from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class FetchResult:
    endpoint: str
    status_code: int
    items: list[dict[str, Any]] = field(default_factory=list)
    raw: dict[str, Any] | list[Any] | None = None
