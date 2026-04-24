#!/usr/bin/env python3
"""
Rotina diária — Operação Comercial Marketing MENSURA
Roda todo dia útil às 09:00 BRT.
Coleta dados do HubSpot + Phantombuster e envia prompt operacional para o agente Marketing.
"""

import json
import urllib.request
import urllib.parse
from datetime import datetime, timedelta, timezone
from pathlib import Path

_BASE = Path(__file__).parent.parent

def _load_config():
    hs  = json.loads((_BASE / "config/hubspot-mensura.json").read_text())
    pb  = json.loads((_BASE / "config/phantombuster-mensura.json").read_text())
    oc  = json.loads((_BASE.parent / "openclaw.json").read_text())
    return hs, pb, oc

_hs_cfg, _pb_cfg, _oc_cfg = _load_config()
HUBSPOT_TOKEN  = _hs_cfg["accessToken"]
PHANTOM_KEY    = _pb_cfg["apiKey"]
TELEGRAM_TOKEN = _oc_cfg["channels"]["telegram"]["botToken"]
TELEGRAM_CHAT  = _oc_cfg["channels"]["telegram"]["allowFrom"][0]

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
    except Exception as e:
        return {"total": 0, "results": [], "error": str(e)}

def pb_get(path, params=None):
    url = f"https://api.phantombuster.com/api/v2{path}"
    if params:
        url += "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"X-Phantombuster-Key": PHANTOM_KEY})
    try:
        return json.loads(urllib.request.urlopen(req, timeout=15).read())
    except:
        return {}

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
    ts_ontem = int((datetime.now(brt) - timedelta(days=1)).replace(
        hour=0, minute=0, second=0).timestamp() * 1000)

    # Dados HubSpot
    contatos_total   = hs_search("contacts").get("total", 0)
    contatos_novos   = hs_search("contacts", filters=[
        {"propertyName": "createdate", "operator": "GTE", "value": str(ts_ontem)}
    ]).get("total", 0)
    empresas_total   = hs_search("companies").get("total", 0)
    deals            = hs_search("deals", limit=100, props=["dealstage","hs_lastmodifieddate"])
    por_estagio      = {}
    for d in deals.get("results", []):
        s = d["properties"].get("dealstage", "?")
        por_estagio[s] = por_estagio.get(s, 0) + 1

    abordagens   = por_estagio.get("qualifiedtobuy", 0)
    respostas    = por_estagio.get("presentationscheduled", 0)
    reunioes     = por_estagio.get("decisionmakerboughtin", 0)
    diagnosticos = por_estagio.get("contractsent", 0)
    propostas    = por_estagio.get("1347046829", 0)

    # Phantombuster
    outreach = pb_get("/agents/fetch", {"id": _pb_cfg["agents"]["linkedin_outreach"]})
    nb_exec  = outreach.get("nbLaunches", 0)

    prompt = f"""📢 *[Marketing] — Operação Comercial MENSURA*
Data: {hoje}

*Dados do dia (HubSpot + Phantombuster):*
• Contatos no CRM: {contatos_total} ({contatos_novos} novos)
• Empresas cadastradas: {empresas_total}
• Abordagens enviadas: {abordagens}
• Respostas recebidas: {respostas}
• Reuniões agendadas: {reunioes}
• Diagnósticos em andamento: {diagnosticos}
• Propostas enviadas: {propostas}
• Execuções LinkedIn Outreach: {nb_exec}

---

Marketing, gere o relatório operacional da Máquina Comercial da MENSURA.

Analise: conteúdos produzidos, leads mapeados, abordagens enviadas, respostas recebidas, follow-ups pendentes, empresas sem próxima ação, campanhas em andamento, oportunidades de melhoria.

Entregue:
1. resumo do dia
2. ações executadas
3. ações pendentes
4. gargalos
5. plano de ação das próximas 24h
6. comandos que precisa da MENSURA
7. decisões para Flávia/Alexandre

Não entregue relatório narrativo vazio. Entregue dados, desvios, decisões e próximas ações."""

    telegram_send(TELEGRAM_CHAT, prompt)
    print(f"✅ Prompt Marketing enviado — {datetime.now(brt).strftime('%H:%M')} BRT")

if __name__ == "__main__":
    main()
