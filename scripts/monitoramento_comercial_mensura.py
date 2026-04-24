#!/usr/bin/env python3
"""
Monitoramento Diário — Máquina Comercial MENSURA
Roda todo dia às 08:00 BRT via cron.
Puxa HubSpot + Phantombuster, gera relatório CFO, envia no Telegram.
"""

import json
import urllib.request
import urllib.parse
from datetime import datetime, timedelta, timezone
from pathlib import Path
import re

# ── Credenciais (carregadas de config — nunca hardcoded) ─────────────────────
_BASE = Path(__file__).parent.parent

def _load_config():
    hs   = json.loads((_BASE / "config/hubspot-mensura.json").read_text())
    pb   = json.loads((_BASE / "config/phantombuster-mensura.json").read_text())
    oc   = json.loads((_BASE.parent / "openclaw.json").read_text())
    return hs, pb, oc

_hs_cfg, _pb_cfg, _oc_cfg = _load_config()

HUBSPOT_TOKEN  = _hs_cfg["accessToken"]
PHANTOM_KEY    = _pb_cfg["apiKey"]
TELEGRAM_TOKEN = _oc_cfg["channels"]["telegram"]["botToken"]
TELEGRAM_CHAT  = _oc_cfg["channels"]["telegram"]["allowFrom"][0]

PHANTOM_AGENTS = _pb_cfg["agents"]

STAGE_LABELS = {
    "appointmentscheduled": "Lead identificado",
    "qualifiedtobuy":       "Abordagem enviada",
    "1347867818":           "Conexão aceita",
    "presentationscheduled":"Resposta recebida",
    "decisionmakerboughtin":"Reunião agendada",
    "contractsent":         "Diagnóstico em andamento",
    "1347046829":           "Proposta enviada",
    "1347046830":           "Negociação",
    "closedwon":            "Fechado — Ganho",
    "closedlost":           "Fechado — Perdido",
}

# ── Helpers ──────────────────────────────────────────────────────────────────
def hs_get(path, params=None):
    url = f"https://api.hubapi.com{path}"
    if params:
        url += "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {HUBSPOT_TOKEN}"})
    try:
        return json.loads(urllib.request.urlopen(req, timeout=15).read())
    except Exception as e:
        return {"error": str(e)}

def hs_search(object_type, filters=None, limit=1, properties=None):
    url = f"https://api.hubapi.com/crm/v3/objects/{object_type}/search"
    body = {"limit": limit}
    if filters:
        body["filterGroups"] = [{"filters": filters}]
    if properties:
        body["properties"] = properties
    data = json.dumps(body).encode()
    req = urllib.request.Request(url, data=data,
          headers={"Authorization": f"Bearer {HUBSPOT_TOKEN}", "Content-Type": "application/json"})
    try:
        return json.loads(urllib.request.urlopen(req, timeout=15).read())
    except Exception as e:
        return {"error": str(e), "total": 0, "results": []}

def pb_get(path, params=None):
    url = f"https://api.phantombuster.com/api/v2{path}"
    if params:
        url += "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"X-Phantombuster-Key": PHANTOM_KEY})
    try:
        return json.loads(urllib.request.urlopen(req, timeout=15).read())
    except Exception as e:
        return {"error": str(e)}

def telegram_send(msg):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = json.dumps({"chat_id": TELEGRAM_CHAT, "text": msg, "parse_mode": "Markdown"}).encode()
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    try:
        urllib.request.urlopen(req, timeout=10)
    except Exception as e:
        print(f"Telegram error: {e}")

# ── Coleta HubSpot ────────────────────────────────────────────────────────────
def coleta_hubspot():
    brt = timezone(timedelta(hours=-3))
    hoje = datetime.now(brt)
    ontem = hoje - timedelta(days=1)
    ts_ontem = int(ontem.replace(hour=0,minute=0,second=0).timestamp() * 1000)

    # Contatos totais e novos
    contatos_total = hs_search("contacts").get("total", 0)
    contatos_novos = hs_search("contacts", filters=[
        {"propertyName": "createdate", "operator": "GTE", "value": str(ts_ontem)}
    ]).get("total", 0)

    # Deals por estágio
    deals_r = hs_search("deals", limit=100, properties=["dealstage", "hs_lastmodifieddate", "closedate"])
    deals = deals_r.get("results", [])
    por_estagio = {}
    parados = 0
    sete_dias_atras = int((hoje - timedelta(days=7)).timestamp() * 1000)
    for d in deals:
        stage = d["properties"].get("dealstage", "unknown")
        por_estagio[stage] = por_estagio.get(stage, 0) + 1
        modified = d["properties"].get("hs_lastmodifieddate")
        if modified and int(modified) < sete_dias_atras:
            if stage not in ("closedwon", "closedlost"):
                parados += 1

    # Empresas
    empresas_total = hs_search("companies").get("total", 0)

    return {
        "contatos_total": contatos_total,
        "contatos_novos_24h": contatos_novos,
        "empresas_total": empresas_total,
        "deals_total": len(deals),
        "por_estagio": por_estagio,
        "leads_parados_7d": parados,
    }

# ── Coleta Phantombuster ──────────────────────────────────────────────────────
def coleta_phantombuster():
    resultado = {}
    for nome, agent_id in PHANTOM_AGENTS.items():
        r = pb_get("/agents/fetch-output", {"id": agent_id})
        output = r.get("output", "")
        status = r.get("status", "unknown")

        # Extrair métricas do output de texto
        convites_enviados = len(re.findall(r'[Ss]ent.*?invitation|invitation.*?sent', output))
        convites_aceitos  = len(re.findall(r'accepted|conectou', output, re.I))

        resultado[nome] = {
            "status": status,
            "nb_launches": pb_get("/agents/fetch", {"id": agent_id}).get("nbLaunches", 0),
            "convites_enviados_sessao": convites_enviados,
            "convites_aceitos_sessao": convites_aceitos,
            "ultima_execucao": r.get("mostRecentEndedAt", "—"),
        }
    return resultado

# ── Gerar relatório ───────────────────────────────────────────────────────────
def gerar_relatorio(hs, pb):
    brt = timezone(timedelta(hours=-3))
    hoje = datetime.now(brt).strftime("%d/%m/%Y")

    outreach = pb.get("linkedin_outreach", {})
    sender   = pb.get("hubspot_contact_sender", {})

    # Pipeline summary
    pipeline_lines = []
    for stage_id, label in STAGE_LABELS.items():
        count = hs["por_estagio"].get(stage_id, 0)
        if count > 0:
            pipeline_lines.append(f"  {label}: *{count}*")
    pipeline_str = "\n".join(pipeline_lines) if pipeline_lines else "  (pipeline vazio — deals serão criados conforme Phantombuster avança)"

    # Diagnóstico automático
    alertas = []
    if hs["leads_parados_7d"] > 0:
        alertas.append(f"⚠️ {hs['leads_parados_7d']} deals sem atividade há 7+ dias — cobrar próxima ação")
    if hs["deals_total"] == 0:
        alertas.append("ℹ️ Pipeline vazio — aguardando primeiros aceites do Outreach")
    if outreach.get("nb_launches", 0) < 1:
        alertas.append("⚠️ LinkedIn Outreach sem execuções — verificar se está ativo")

    alertas_str = "\n".join(alertas) if alertas else "✅ Nenhum alerta crítico"

    relatorio = f"""📊 *RELATÓRIO DIÁRIO — MÁQUINA COMERCIAL MENSURA*
Data: {hoje}

*1. RESUMO EXECUTIVO*
Contatos no CRM: *{hs['contatos_total']}* ({hs['contatos_novos_24h']} novos nas últimas 24h)
Empresas cadastradas: *{hs['empresas_total']}*
Deals ativos: *{hs['deals_total']}*
Leads parados (7d+): *{hs['leads_parados_7d']}*

*2. PIPELINE MENSURA*
{pipeline_str}

*3. PHANTOMBUSTER*
LinkedIn Outreach: `{outreach.get('status', '—')}` | {outreach.get('nb_launches', 0)} execuções
HubSpot Sender: `{sender.get('status', '—')}` | {sender.get('nb_launches', 0)} execuções

*4. ALERTAS*
{alertas_str}

*5. AÇÃO PRIORITÁRIA HOJE*
• Verificar no LinkedIn quem aceitou o convite → responder usando protocolo Cenário A/B
• Deals em "Resposta recebida" → ligar hoje (usar roteiro de qualificação 20 min)
• Atualizar estágio no HubSpot após cada interação

_Gerado automaticamente pelo OpenClaw — {datetime.now(brt).strftime('%H:%M')} BRT_"""

    return relatorio

# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    print("Coletando HubSpot...")
    hs = coleta_hubspot()
    print("Coletando Phantombuster...")
    pb = coleta_phantombuster()
    print("Gerando relatório...")
    relatorio = gerar_relatorio(hs, pb)
    print(relatorio)
    print("\nEnviando no Telegram...")
    telegram_send(relatorio)
    print("✅ Relatório enviado.")

if __name__ == "__main__":
    main()
