#!/usr/bin/env python3
"""
Guard-rail para rotinas CCSP Casa 7.

Objetivo:
- distinguir claramente alinhamento operacional diário de status executivo;
- impedir reaproveitamento de artefatos legados em tmp/ como fonte de status validado;
- servir como ponto único de validação futura antes de qualquer envio externo.
"""

from __future__ import annotations

from pathlib import Path
from typing import Iterable

FORBIDDEN_HINTS = [
    "Avanço físico global atual: 7%",
    "Croncheap | Execução",
    "CCSP Casa 7 — Status da Obra (manhã)",
]


def assert_not_legacy_status_text(text: str) -> None:
    for hint in FORBIDDEN_HINTS:
        if hint in text:
            raise ValueError(
                "Texto bloqueado pelo guard-rail: parece status executivo legado/não validado."
            )


def assert_no_tmp_sources(paths: Iterable[str]) -> None:
    for raw in paths:
        p = Path(raw)
        if "tmp" in p.parts:
            raise ValueError(
                f"Fonte bloqueada pelo guard-rail: artefato temporário não pode alimentar envio externo ({raw})."
            )


def classify_ccsp_message(text: str) -> str:
    lowered = text.lower()
    if "status da obra" in lowered or "avanço físico global" in lowered:
        return "status_executivo"
    return "alinhamento_operacional"
