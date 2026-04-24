#!/usr/bin/env python3
"""
Rotina 2x/semana — Revisão Técnico-Comercial MENSURA
Roda toda segunda e quinta às 08:30 BRT.
Envia prompt de revisão de posicionamento para o canal Telegram do agente MENSURA.
"""

import json
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

_BASE = Path(__file__).parent.parent

def _load_config():
    hs = json.loads((_BASE / "config/hubspot-mensura.json").read_text())
    pb = json.loads((_BASE / "config/phantombuster-mensura.json").read_text())
    oc = json.loads((_BASE.parent / "openclaw.json").read_text())
    return hs, pb, oc

_hs_cfg, _pb_cfg, _oc_cfg = _load_config()
HUBSPOT_TOKEN  = _hs_cfg["accessToken"]
TELEGRAM_TOKEN = _oc_cfg["channels"]["telegram"]["botToken"]

# Canal MENSURA — grupo dedicado, topic 1
MENSURA_GROUP  = "-1003366344184"
MENSURA_TOPIC  = 1

def hs_search(obj, filters=None, limit=1, props=None):
    url = f"https://api.hubapi.com/crm/v3/objects/{obj}/search"
    body = {"limit": limit}
    if filters:
        body["filterGroups"] = [{"filters": filters}]
    if props:
        body["properties"] = props
    data = json.dumps(body).encode()
    req = urllib.request.Request(url, data=data,
          headers={"Authorization": f"Bearer {HUBSPOT_TOKEN}", "Content-Type": "application/json"})
    try:
        return json.loads(urllib.request.urlopen(req, timeout=15).read())
    except:
        return {"total": 0, "results": []}

def telegram_send(chat_id, msg, thread_id=None):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": msg, "parse_mode": "Markdown"}
    if thread_id:
        payload["message_thread_id"] = thread_id
    data = json.dumps(payload).encode()
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    try:
        urllib.request.urlopen(req, timeout=10)
    except Exception as e:
        print(f"Telegram error: {e}")

def main():
    brt = timezone(timedelta(hours=-3))
    hoje = datetime.now(brt).strftime("%d/%m/%Y")
    dia_semana = datetime.now(brt).strftime("%A")

    # Snapshot do pipeline para contextualizar a revisão
    deals = hs_search("deals", limit=50, props=["dealstage", "dealname"])
    por_estagio = {}
    for d in deals.get("results", []):
        s = d["properties"].get("dealstage", "?")
        por_estagio[s] = por_estagio.get(s, 0) + 1

    abordagens   = por_estagio.get("qualifiedtobuy", 0)
    respostas    = por_estagio.get("presentationscheduled", 0)
    reunioes     = por_estagio.get("decisionmakerboughtin", 0)
    propostas    = por_estagio.get("1347046829", 0)

    prompt = f"""⚙️ *[MENSURA] — Revisão Técnico-Comercial*
Data: {hoje} ({dia_semana})

*Pipeline atual:*
• Abordagens enviadas: {abordagens}
• Respostas recebidas: {respostas}
• Reuniões agendadas: {reunioes}
• Propostas enviadas: {propostas}

---

MENSURA, revise a Máquina Comercial sob o ponto de vista técnico-comercial.

Avalie se as ações de Marketing estão alinhadas ao posicionamento:
_"A MENSURA vende previsibilidade executiva, controle técnico e governança de decisão para obras complexas."_

Analise:
• se os leads são aderentes ao ICP
• se as mensagens estão técnicas e executivas
• se as ofertas estão claras
• se o conteúdo evita tom genérico ou promocional
• se os argumentos valorizam prazo, custo, risco, qualidade, governança e decisão
• se as propostas estão posicionadas como valor, não como commodity
• se há oportunidades perdidas

Entregue:
1. avaliação geral (nota 1–10 + justificativa)
2. pontos desalinhados
3. correções recomendadas (antes → depois)
4. argumentos comerciais melhores
5. riscos de posicionamento
6. próximos comandos para Marketing"""

    telegram_send(MENSURA_GROUP, prompt)
    print(f"✅ Prompt MENSURA enviado — {datetime.now(brt).strftime('%H:%M')} BRT")

if __name__ == "__main__":
    main()

