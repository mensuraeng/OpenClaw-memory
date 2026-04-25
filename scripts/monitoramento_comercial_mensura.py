#!/usr/bin/env python3
"""
Monitoramento Diário — Máquina Comercial MENSURA
Roda seg-sex às 08:00 BRT via cron (exceto feriados nacionais).
Puxa HubSpot + Phantombuster, gera relatório CFO em HTML, envia no Telegram.
"""

import json
import urllib.request
import urllib.parse
from datetime import datetime, timedelta, timezone
from pathlib import Path
import re

# ── Feriados nacionais brasileiros ───────────────────────────────────────────
# Fixos: (mês, dia) | Variáveis: listados por ano
_FERIADOS_FIXOS = {(1,1),(4,21),(5,1),(9,7),(10,12),(11,2),(11,15),(12,25)}
_FERIADOS_VARIAVEIS = {
    # Carnaval (seg/ter), Sexta da Paixão, Corpus Christi
    2026: {(2,16),(2,17),(4,3),(6,4)},
    2027: {(2,8),(2,9),(3,26),(6,17)},
}

def _is_feriado(dt: datetime) -> bool:
    if (dt.month, dt.day) in _FERIADOS_FIXOS:
        return True
    ano_vars = _FERIADOS_VARIAVEIS.get(dt.year, set())
    return (dt.month, dt.day) in ano_vars

# ── Credenciais (carregadas de config — nunca hardcoded) ─────────────────────
_BASE = Path(__file__).parent.parent

def _load_config():
    hs   = json.loads((_BASE / "config/hubspot-mensura.json").read_text())
    pb   = json.loads((_BASE / "config/phantombuster-mensura.json").read_text())
    oc   = json.loads((_BASE.parent / "openclaw.json").read_text())
    return hs, pb, oc

_hs_cfg, _pb_cfg, _oc_cfg = _load_config()

HUBSPOT_TOKEN    = _hs_cfg["accessToken"]
PHANTOM_KEY      = _pb_cfg["apiKey"]
TELEGRAM_TOKEN   = _oc_cfg["channels"]["telegram"]["botToken"]
TELEGRAM_CHAT    = "-1003366344184"  # Grupo Mensura
TELEGRAM_TOPIC   = 1                 # Tópico principal Mensura

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

def telegram_send(html: str):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = json.dumps({
        "chat_id": TELEGRAM_CHAT,
        "text": html,
        "parse_mode": "HTML",
        "disable_web_page_preview": True,
    }).encode()
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
    sete_dias_atras = hoje - timedelta(days=7)
    for d in deals:
        stage = d["properties"].get("dealstage", "unknown")
        por_estagio[stage] = por_estagio.get(stage, 0) + 1
        modified_str = d["properties"].get("hs_lastmodifieddate")
        if modified_str and stage not in ("closedwon", "closedlost"):
            try:
                modified_dt = datetime.fromisoformat(modified_str.replace("Z", "+00:00"))
                if modified_dt < sete_dias_atras:
                    parados += 1
            except (ValueError, TypeError):
                pass

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

        convites_enviados = len(re.findall(r'[Ss]ent.*?invitation|invitation.*?sent', output))
        convites_aceitos  = len(re.findall(r'accepted|conectou', output, re.I))

        # Taxa de aceite acumulada via contagem no HubSpot
        taxa_aceite = None
        if nome == "linkedin_outreach":
            total_abordagens = hs_search("deals", filters=[
                {"propertyName": "dealstage", "operator": "IN",
                 "value": ["qualifiedtobuy", "1347867818", "presentationscheduled",
                           "decisionmakerboughtin", "contractsent", "1347046829",
                           "1347046830", "closedwon"]}
            ]).get("total", 0)
            conexoes = hs_search("deals", filters=[
                {"propertyName": "dealstage", "operator": "IN",
                 "value": ["1347867818", "presentationscheduled", "decisionmakerboughtin",
                           "contractsent", "1347046829", "1347046830", "closedwon"]}
            ]).get("total", 0)
            if total_abordagens > 0:
                taxa_aceite = round(conexoes / total_abordagens * 100, 1)

        resultado[nome] = {
            "status": status,
            "nb_launches": pb_get("/agents/fetch", {"id": agent_id}).get("nbLaunches", 0),
            "convites_enviados_sessao": convites_enviados,
            "convites_aceitos_sessao": convites_aceitos,
            "taxa_aceite_pct": taxa_aceite,
            "ultima_execucao": r.get("mostRecentEndedAt", "—"),
        }
    return resultado


# ── Leads quentes e follow-ups urgentes ──────────────────────────────────────
def coleta_leads_quentes():
    brt = timezone(timedelta(hours=-3))
    dois_dias_atras = int((datetime.now(brt) - timedelta(days=2)).timestamp() * 1000)

    # Top 3 contatos mais recentemente ativos
    r = hs_search("contacts", limit=3,
                  properties=["firstname", "lastname", "company", "hs_lastcontactdate",
                               "jobtitle"])
    leads = []
    for c in r.get("results", []):
        p = c["properties"]
        nome = f"{p.get('firstname', '')} {p.get('lastname', '')}".strip()
        if nome:
            leads.append(f"{nome} ({p.get('company', '?')}) — {p.get('jobtitle', '')}".strip(" —"))

    # Deals em "Resposta recebida" parados há 2+ dias
    r2 = hs_search("deals", filters=[
        {"propertyName": "dealstage", "operator": "EQ", "value": "presentationscheduled"},
        {"propertyName": "hs_lastmodifieddate", "operator": "LTE", "value": str(dois_dias_atras)},
    ], limit=10, properties=["dealname", "hs_lastmodifieddate"])
    urgentes = [d["properties"].get("dealname", "?") for d in r2.get("results", [])]

    return leads, urgentes

# ── Gerar relatório HTML ──────────────────────────────────────────────────────
def gerar_relatorio(hs, pb, leads_quentes, urgentes):
    brt = timezone(timedelta(hours=-3))
    agora = datetime.now(brt)
    hoje = agora.strftime("%d/%m/%Y")
    hora = agora.strftime("%H:%M")

    outreach = pb.get("linkedin_outreach", {})
    sender   = pb.get("hubspot_contact_sender", {})

    # Pipeline
    pipeline_lines = []
    for stage_id, label in STAGE_LABELS.items():
        count = hs["por_estagio"].get(stage_id, 0)
        if count > 0:
            pipeline_lines.append(f"  • {label}: <b>{count}</b>")
    pipeline_str = "\n".join(pipeline_lines) if pipeline_lines else "  ⚪ Pipeline vazio — aguardando primeiros aceites"

    # Taxa de aceite
    taxa = outreach.get("taxa_aceite_pct")
    taxa_str = f"{taxa}%" if taxa is not None else "—"

    # Leads quentes
    quentes_str = "\n".join(f"  • {l}" for l in leads_quentes) if leads_quentes else "  (sem atividade recente)"

    # Alertas
    alertas = []
    if urgentes:
        for d in urgentes:
            alertas.append(f"🔥 <b>URGENTE:</b> {d} — resposta recebida há 2d+ sem follow-up")
    if hs["leads_parados_7d"] > 0:
        alertas.append(f"⚠️ <b>{hs['leads_parados_7d']} deals</b> sem atividade há 7+ dias")
    if hs["deals_total"] == 0:
        alertas.append("ℹ️ Pipeline vazio — aguardando primeiros aceites do Outreach")
    if outreach.get("nb_launches", 0) < 1:
        alertas.append("⚠️ LinkedIn Outreach sem execuções — verificar se está ativo")
    alertas_str = "\n".join(alertas) if alertas else "✅ Nenhum alerta crítico"

    relatorio = (
        f"📊 <b>RELATÓRIO DIÁRIO — MÁQUINA COMERCIAL MENSURA</b>\n"
        f"<i>Data: {hoje} | {hora} BRT</i>\n"
        f"\n"
        f"<b>1. RESUMO EXECUTIVO</b>\n"
        f"Contatos no CRM: <b>{hs['contatos_total']}</b> (+{hs['contatos_novos_24h']} nas últimas 24h)\n"
        f"Empresas cadastradas: <b>{hs['empresas_total']}</b>\n"
        f"Deals ativos: <b>{hs['deals_total']}</b>\n"
        f"Leads parados 7d+: <b>{hs['leads_parados_7d']}</b>\n"
        f"\n"
        f"<b>2. PIPELINE MENSURA</b>\n"
        f"{pipeline_str}\n"
        f"\n"
        f"<b>3. PHANTOMBUSTER / LINKEDIN</b>\n"
        f"  • Outreach: <code>{outreach.get('status', '—')}</code> | {outreach.get('nb_launches', 0)} execuções | taxa aceite: <b>{taxa_str}</b>\n"
        f"  • HubSpot Sender: <code>{sender.get('status', '—')}</code> | {sender.get('nb_launches', 0)} execuções\n"
        f"\n"
        f"<b>4. LEADS QUENTES</b>\n"
        f"{quentes_str}\n"
        f"\n"
        f"<b>5. ALERTAS</b>\n"
        f"{alertas_str}\n"
        f"\n"
        f"<b>6. AÇÃO PRIORITÁRIA HOJE</b>\n"
        f"  • Verificar LinkedIn: quem aceitou → responder (Cenário A/B)\n"
        f"  • Deals em <i>Resposta recebida</i> → ligar hoje (roteiro 20 min)\n"
        f"  • Atualizar estágio no HubSpot após cada interação\n"
        f"\n"
        f"<i>Gerado pelo OpenClaw — {hora} BRT</i>"
    )

    return relatorio

# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    brt = timezone(timedelta(hours=-3))
    hoje = datetime.now(brt)

    if _is_feriado(hoje):
        print(f"📅 Hoje ({hoje.strftime('%d/%m/%Y')}) é feriado nacional — relatório não enviado.")
        return

    print("Coletando HubSpot...")
    hs = coleta_hubspot()
    print("Coletando Phantombuster...")
    pb = coleta_phantombuster()
    print("Coletando leads quentes e follow-ups urgentes...")
    leads_quentes, urgentes = coleta_leads_quentes()
    print("Gerando relatório HTML...")
    relatorio = gerar_relatorio(hs, pb, leads_quentes, urgentes)
    print(relatorio)
    print("\nEnviando no Telegram...")
    telegram_send(relatorio)
    print("✅ Relatório enviado.")

if __name__ == "__main__":
    main()
