#!/usr/bin/env python3
"""
CCSP Casa 7 — Relatório Semanal (toda segunda, 8h BRT / 11h UTC).

Gera o payload de alerta semanal pedindo 3 inputs ao Alê e entrega
à Flávia, que decide a saída final (consolidar e responder direto,
delegar para `mia`, ou agendar a comunicação).

Não fala diretamente com Telegram nem email. A regra é:
    script → gera payload → Flávia consolida → saída final
"""

import os
import sys
from datetime import datetime, timezone, timedelta

# Permite importar send_to_flavia.py do mesmo diretório, mesmo
# quando este script roda via `cd workspace && python3 scripts/...`
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from send_to_flavia import send_to_flavia  # noqa: E402

BRT = timezone(timedelta(hours=-3))


def gerar_corpo(semana_str: str) -> str:
    return f"""📊 *CCSP Casa 7 — Atualização Semanal | {semana_str}*

Alê, preciso de 3 inputs para fechar o relatório desta semana:

*1. Cronograma atualizado do Victor*
  → Arquivo .mpp ou % de avanço por atividade

*2. Decisões e deliberações da semana*
  → O que o cliente (TOOLS/Rafael) aprovou, pediu ou questionou?
  → Alguma diretriz nova da gerenciadora?
  → Aprovações pendentes que foram resolvidas?

*3. Ocorrências novas*
  → Algum imprevisto, não conformidade ou desvio não registrado?

Com isso gero: relatório interno, relatório TOOLS, look ahead, alertas e histórico atualizado."""


def main() -> int:
    hoje = datetime.now(BRT)
    semana_str = hoje.strftime("%d/%m/%Y")
    payload = {
        "source": "ccsp_relatorio_semanal.py",
        "kind": "alerta_semanal_inputs_pendentes",
        "project": "CCSP Casa 7",
        "company": "MIA",
        "urgency": "normal",
        "scheduled_at": hoje.isoformat(),
        "body": gerar_corpo(semana_str),
    }
    return send_to_flavia(payload)


if __name__ == "__main__":
    sys.exit(main())
